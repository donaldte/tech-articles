/**
 * Resource Upload Manager - Handles multipart uploads to S3 with chunk support
 * Manages file uploads, progress tracking, pause/resume, and drag & drop
 */
(function (global) {
    'use strict';

    class ResourceUploadManager {
        constructor(options = {}) {
            this.chunkSize = options.chunkSize || 5 * 1024 * 1024; // 5MB default
            this.maxConcurrentUploads = options.maxConcurrentUploads || 3;

            // State management
            this.uploadStates = new Map(); // inputId -> state ('idle', 'uploading', 'paused', 'completed', 'failed')
            this.uploadData = new Map(); // inputId -> upload metadata
            this.activeUploads = new Map(); // inputId -> abort controllers

            // API endpoints
            this.endpoints = {
                create: options.createEndpoint || '/dashboard/resources/api/upload/create/',
                presignedUrls: options.presignedUrlsEndpoint || '/dashboard/resources/api/upload/presigned-urls/',
                complete: options.completeEndpoint || '/dashboard/resources/api/upload/complete/',
                abort: options.abortEndpoint || '/dashboard/resources/api/upload/abort/',
            };

            // CSRF token
            this.csrfToken = this.getCSRFToken();
        }

        getCSRFToken() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        }

        /**
         * Initialize upload for a file
         * @param {string} inputId - Unique identifier for the upload
         * @param {File} file - File to upload
         * @returns {Promise<Object>} Upload result
         */
        async startUpload(inputId, file) {
            try {
                // Check if already uploading
                if (this.uploadStates.get(inputId) === 'uploading') {
                    console.warn(`Upload already in progress for ${inputId}`);
                    return { success: false, error: 'Already uploading' };
                }

                // Set state
                this.uploadStates.set(inputId, 'uploading');

                // Update UI
                this.updateProgress(inputId, 0, 'Initializing upload...');

                // Step 1: Create multipart upload
                const createResult = await this.createMultipartUpload(file);
                if (!createResult.success) {
                    throw new Error(createResult.error || 'Failed to initialize upload');
                }

                const { uploadId, key } = createResult.data;

                // Calculate number of parts
                const fileSize = file.size;
                const numParts = Math.ceil(fileSize / this.chunkSize);

                // Step 2: Get presigned URLs
                const urlsResult = await this.getPresignedUrls(key, uploadId, numParts);
                if (!urlsResult.success) {
                    throw new Error(urlsResult.error || 'Failed to get presigned URLs');
                }

                // Store upload metadata
                this.uploadData.set(inputId, {
                    file,
                    uploadId,
                    key,
                    urls: urlsResult.data.urls,
                    parts: [],
                    currentPart: 0,
                    totalParts: numParts,
                });

                // Step 3: Upload parts
                const uploadResult = await this.uploadParts(inputId);
                if (!uploadResult.success) {
                    // Check if it was aborted
                    if (uploadResult.errorType === 'AbortError') {
                        this.uploadStates.set(inputId, 'paused');
                        return { success: false, errorType: 'AbortError' };
                    }
                    throw new Error(uploadResult.error || 'Failed to upload parts');
                }

                // Step 4: Complete upload
                const completeResult = await this.completeUpload(inputId);
                if (!completeResult.success) {
                    throw new Error(completeResult.error || 'Failed to complete upload');
                }

                // Success
                this.uploadStates.set(inputId, 'completed');
                this.updateProgress(inputId, 100, gettext('Upload completed'));

                return {
                    success: true,
                    uploadId,
                    key,
                    location: completeResult.data.location,
                };

            } catch (error) {
                console.error(`Upload failed for ${inputId}:`, error);
                this.uploadStates.set(inputId, 'failed');
                this.updateProgress(inputId, 0, gettext('Upload failed'));

                // Try to abort on S3
                const uploadData = this.uploadData.get(inputId);
                if (uploadData) {
                    await this.abortUpload(uploadData.key, uploadData.uploadId);
                }

                return {
                    success: false,
                    error: error.message || error,
                };
            }
        }

        /**
         * Create multipart upload on S3
         */
        async createMultipartUpload(file) {
            try {
                const response = await fetch(this.endpoints.create, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                    },
                    body: JSON.stringify({
                        file_name: file.name,
                        content_type: file.type || 'application/octet-stream',
                    }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    return { success: false, error: error.error || 'Failed to create upload' };
                }

                const data = await response.json();
                return { success: true, data };

            } catch (error) {
                console.error('Error creating multipart upload:', error);
                return { success: false, error: error.message };
            }
        }

        /**
         * Get presigned URLs for parts
         */
        async getPresignedUrls(key, uploadId, parts) {
            try {
                const response = await fetch(this.endpoints.presignedUrls, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                    },
                    body: JSON.stringify({
                        key,
                        uploadId,
                        parts,
                    }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    return { success: false, error: error.error || 'Failed to get presigned URLs' };
                }

                const data = await response.json();
                return { success: true, data };

            } catch (error) {
                console.error('Error getting presigned URLs:', error);
                return { success: false, error: error.message };
            }
        }

        /**
         * Upload all parts
         */
        async uploadParts(inputId) {
            const uploadData = this.uploadData.get(inputId);
            if (!uploadData) {
                return { success: false, error: 'Upload data not found' };
            }

            const { file, urls } = uploadData;
            const parts = [];

            // Create abort controller for this upload
            const abortController = new AbortController();
            this.activeUploads.set(inputId, abortController);

            try {
                // Upload parts with concurrency control
                for (let i = 0; i < urls.length; i += this.maxConcurrentUploads) {
                    const batch = urls.slice(i, i + this.maxConcurrentUploads);

                    const batchPromises = batch.map(async (urlInfo) => {
                        const partNumber = urlInfo.partNumber;
                        const start = (partNumber - 1) * this.chunkSize;
                        const end = Math.min(start + this.chunkSize, file.size);
                        const chunk = file.slice(start, end);

                        // Upload chunk
                        const response = await fetch(urlInfo.url, {
                            method: 'PUT',
                            body: chunk,
                            signal: abortController.signal,
                        });

                        if (!response.ok) {
                            throw new Error(`Failed to upload part ${partNumber}`);
                        }

                        const etag = response.headers.get('ETag');

                        // Update progress
                        uploadData.currentPart = partNumber;
                        const progress = Math.round((partNumber / urls.length) * 100);
                        this.updateProgress(
                            inputId,
                            progress,
                            interpolate(gettext('Uploading... %s%%'), [progress])
                        );

                        return {
                            ETag: etag,
                            PartNumber: partNumber,
                        };
                    });

                    const batchResults = await Promise.all(batchPromises);
                    parts.push(...batchResults);
                }

                // Sort parts by part number
                parts.sort((a, b) => a.PartNumber - b.PartNumber);
                uploadData.parts = parts;

                return { success: true, parts };

            } catch (error) {
                if (error.name === 'AbortError') {
                    console.log(`Upload paused for ${inputId}`);
                    return { success: false, errorType: 'AbortError' };
                }
                console.error(`Error uploading parts for ${inputId}:`, error);
                return { success: false, error: error.message };
            } finally {
                this.activeUploads.delete(inputId);
            }
        }

        /**
         * Complete multipart upload
         */
        async completeUpload(inputId) {
            const uploadData = this.uploadData.get(inputId);
            if (!uploadData) {
                return { success: false, error: 'Upload data not found' };
            }

            const { key, uploadId, parts } = uploadData;

            try {
                const response = await fetch(this.endpoints.complete, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                    },
                    body: JSON.stringify({
                        key,
                        uploadId,
                        parts,
                    }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    return { success: false, error: error.error || 'Failed to complete upload' };
                }

                const data = await response.json();
                return { success: true, data };

            } catch (error) {
                console.error('Error completing upload:', error);
                return { success: false, error: error.message };
            }
        }

        /**
         * Abort/cancel upload
         */
        async abortUpload(key, uploadId) {
            try {
                const response = await fetch(this.endpoints.abort, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken,
                    },
                    body: JSON.stringify({
                        key,
                        uploadId,
                    }),
                });

                if (!response.ok) {
                    console.warn('Failed to abort upload on server');
                }

                return { success: response.ok };

            } catch (error) {
                console.error('Error aborting upload:', error);
                return { success: false };
            }
        }

        /**
         * Pause upload
         */
        pauseUpload(inputId) {
            const abortController = this.activeUploads.get(inputId);
            if (abortController) {
                abortController.abort();
                this.uploadStates.set(inputId, 'paused');
                this.updateProgress(inputId, null, gettext('Upload paused'));
            }
        }

        /**
         * Resume upload
         */
        async resumeUpload(inputId) {
            const uploadData = this.uploadData.get(inputId);
            if (!uploadData) {
                console.warn(`No upload data found for ${inputId}`);
                return { success: false, error: 'No upload data' };
            }

            // Continue from where we left off
            this.uploadStates.set(inputId, 'uploading');
            return await this.uploadParts(inputId);
        }

        /**
         * Cancel upload completely
         */
        async cancelUpload(inputId) {
            // Pause first
            this.pauseUpload(inputId);

            // Abort on server
            const uploadData = this.uploadData.get(inputId);
            if (uploadData) {
                await this.abortUpload(uploadData.key, uploadData.uploadId);
                this.uploadData.delete(inputId);
            }

            this.uploadStates.set(inputId, 'idle');
            this.updateProgress(inputId, 0, '');
        }

        /**
         * Update progress UI
         */
        updateProgress(inputId, progress, status) {
            const progressBar = document.getElementById(`progress-bar-${inputId}`);
            const statusText = document.getElementById(`status-${inputId}`);
            const progressContainer = document.getElementById(`progress-container-${inputId}`);

            if (progressBar && progress !== null) {
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress);
            }

            if (statusText && status) {
                statusText.textContent = status;
            }

            if (progressContainer && progress !== null) {
                progressContainer.classList.remove('hidden');
            }
        }

        /**
         * Get upload state
         */
        getUploadState(inputId) {
            return this.uploadStates.get(inputId) || 'idle';
        }

        /**
         * Check if any uploads are active
         */
        hasActiveUploads() {
            for (const state of this.uploadStates.values()) {
                if (state === 'uploading' || state === 'paused') {
                    return true;
                }
            }
            return false;
        }
    }

    // Export to global scope
    global.ResourceUploadManager = ResourceUploadManager;

})(window);

