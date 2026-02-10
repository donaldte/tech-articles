/**
 * Resource Form Handler - Manages resource creation/editing with file upload
 * Supports drag & drop, file validation, and dynamic article filtering by category
 */
(function (global) {
    'use strict';

    class ResourceFormHandler {
        constructor(formId, options = {}) {
            this.form = document.getElementById(formId);
            if (!this.form) {
                console.error(`Form with id "${formId}" not found`);
                return;
            }

            this.options = options;
            this.isPopupMode = options.isPopupMode || false;
            this.uploadManager = null;
            this.currentFile = null;
            this.uploadInputId = 'resource-file-upload';

            // DOM elements
            this.elements = {
                fileUploadSection: document.getElementById('file-upload-section'),
            };

            this.init();
        }

        init() {
            // Initialize upload manager
            this.uploadManager = new global.ResourceUploadManager(this.options.uploadEndpoints || {});

            // Setup file input
            this.setupFileInput();

            // Setup drag & drop
            this.setupDragAndDrop();

            // Setup dynamic article filtering by category
            this.setupCategoryFilter();

            // Setup form submission
            this.setupFormSubmission();

            // Setup cancel button
            this.setupCancelButton();
        }

        setupFileInput() {
            const fileInput = document.getElementById('file-input');
            const fileInputLabel = document.getElementById('file-input-label');
            const fileName = document.getElementById('file-name');
            const fileSize = document.getElementById('file-size');
            const removeFileBtn = document.getElementById('remove-file-btn');

            if (!fileInput) return;

            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.handleFileSelected(file);
                }
            });

            if (removeFileBtn) {
                removeFileBtn.addEventListener('click', () => {
                    this.clearFileSelection();
                });
            }
        }

        setupDragAndDrop() {
            const dropZone = document.getElementById('drop-zone');
            if (!dropZone) return;

            // Prevent defaults
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            });

            // Highlight drop zone
            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => {
                    dropZone.classList.add('border-primary', 'bg-primary/5');
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => {
                    dropZone.classList.remove('border-primary', 'bg-primary/5');
                });
            });

            // Handle drop
            dropZone.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileSelected(files[0]);
                }
            });
        }

        handleFileSelected(file) {
            // Validate file
            const validation = this.validateFile(file);
            if (!validation.valid) {
                if (global.toastManager) {
                    global.toastManager.buildToast()
                        .setMessage(validation.error)
                        .setType('danger')
                        .setPosition('top-right')
                        .setDuration(5000)
                        .show();
                }
                return;
            }

            // Store file
            this.currentFile = file;

            // Update UI
            this.updateFileDisplay(file);

            // Show file info
            document.getElementById('file-info')?.classList.remove('hidden');
            document.getElementById('drop-zone-content')?.classList.add('hidden');
        }

        validateFile(file) {
            // Max file size: 100MB
            const maxSize = 100 * 1024 * 1024;
            if (file.size > maxSize) {
                return {
                    valid: false,
                    error: gettext('File size must not exceed 100MB')
                };
            }

            // Allowed types
            const allowedTypes = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'text/plain',
                'application/zip',
                'application/x-rar-compressed',
            ];

            if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|xls|xlsx|ppt|pptx|txt|zip|rar)$/i)) {
                return {
                    valid: false,
                    error: gettext('Invalid file type. Only documents, spreadsheets, presentations, and archives are allowed.')
                };
            }

            return {valid: true};
        }

        updateFileDisplay(file) {
            const fileName = document.getElementById('file-name');
            const fileSize = document.getElementById('file-size');
            const fileIcon = document.getElementById('file-icon');

            if (fileName) {
                fileName.textContent = file.name;
            }

            if (fileSize) {
                fileSize.textContent = this.formatFileSize(file.size);
            }

            if (fileIcon) {
                // Update icon based on file type
                fileIcon.innerHTML = this.getFileIcon(file.name);
            }
        }

        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }

        getFileIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            const icons = {
                pdf: '<svg class="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z"/></svg>',
                doc: '<svg class="w-8 h-8 text-blue-500" fill="currentColor" viewBox="0 0 20 20"><path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z"/></svg>',
                docx: '<svg class="w-8 h-8 text-blue-500" fill="currentColor" viewBox="0 0 20 20"><path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z"/></svg>',
                xls: '<svg class="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z"/></svg>',
                xlsx: '<svg class="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z"/></svg>',
                zip: '<svg class="w-8 h-8 text-gray-500" fill="currentColor" viewBox="0 0 20 20"><path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z"/></svg>',
                rar: '<svg class="w-8 h-8 text-gray-500" fill="currentColor" viewBox="0 0 20 20"><path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z"/></svg>',
            };
            return icons[ext] || '<svg class="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20"><path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z"/></svg>';
        }

        clearFileSelection() {
            this.currentFile = null;

            const fileInput = document.getElementById('file-input');
            if (fileInput) {
                fileInput.value = '';
            }

            document.getElementById('file-info')?.classList.add('hidden');
            document.getElementById('drop-zone-content')?.classList.remove('hidden');

            // Clear progress
            const progressContainer = document.getElementById(`progress-container-${this.uploadInputId}`);
            if (progressContainer) {
                progressContainer.classList.add('hidden');
            }
        }

        setupCategoryFilter() {
            const categorySelect = document.getElementById('id_category');
            const articleSelect = document.getElementById('id_article');

            if (!categorySelect || !articleSelect) return;

            categorySelect.addEventListener('change', async (e) => {
                const categoryId = e.target.value;

                if (!categoryId) {
                    // Reset articles
                    articleSelect.innerHTML = '<option value="">---------</option>';
                    return;
                }

                // Fetch articles for this category
                try {
                    global.loader?.show();
                    const response = await fetch(`${this.options.articlesByCategory}?category_id=${categoryId}`);
                    if (!response.ok) throw new Error('Failed to fetch articles');

                    const data = await response.json();

                    // Update article select
                    articleSelect.innerHTML = '<option value="">---------</option>';
                    data.articles.forEach(article => {
                        const option = document.createElement('option');
                        option.value = article.id;
                        option.textContent = article.title;
                        articleSelect.appendChild(option);
                    });

                } catch (error) {
                    console.error('Error fetching articles:', error);
                    if (global.toastManager) {
                        global.toastManager.buildToast()
                            .setMessage(gettext('Failed to load articles'))
                            .setType('danger')
                            .show();
                    }
                } finally {
                    global.loader?.hide();
                }
            });
        }

        setupFormSubmission() {
            this.form.addEventListener('submit', async (e) => {
                e.preventDefault();

                // Scroll to upload section
                if (this.elements.fileUploadSection) {
                    this.elements.fileUploadSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }

                // Check if file is selected
                if (!this.currentFile) {
                    if (global.toastManager) {
                        global.toastManager.buildToast()
                            .setMessage(gettext('Please select a file to upload'))
                            .setType('warning')
                            .show();
                    }
                    return;
                }

                try {
                    // Step 1: Upload file
                    const uploadResult = await this.uploadManager.startUpload(this.uploadInputId, this.currentFile);

                    if (!uploadResult.success) {
                        throw new Error(uploadResult.error || 'Upload failed');
                    }

                    // Step 2: Submit form with file data
                    await this.submitFormData(uploadResult);

                } catch (error) {
                    console.error('Form submission error:', error);
                    if (global.toastManager) {
                        global.toastManager.buildToast()
                            .setMessage(error.message || gettext('An error occurred'))
                            .setType('danger')
                            .show();
                    }
                }
            });
        }

        async submitFormData(uploadResult) {
            const formData = new FormData(this.form);

            // Add file metadata
            formData.append('file_key', uploadResult.key);
            formData.append('file_name', this.currentFile.name);
            formData.append('file_size', this.currentFile.size);
            formData.append('content_type', this.currentFile.type);

            // Show loader
            window.loader?.show();

            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.uploadManager.csrfToken,
                },
            });

            // Hide loader
            window.loader?.hide();

            if (!response.ok) {
                const error = await response.text();
                throw new Error(error || 'Form submission failed');
            }

            // Handle popup mode
            if (this.isPopupMode) {
                const result = await response.json();

                // Send data to parent window
                if (window.opener && result.success) {
                    window.opener.postMessage({
                        type: 'resource-created',
                        resource: result.resource
                    }, window.location.origin);

                    // Close popup
                    window.close();
                }
            } else {
                // Normal mode - redirect
                window.location.href = this.options.successUrl || '/dashboard/resources/';
            }
        }

        setupCancelButton() {
            const cancelBtn = document.getElementById('cancel-btn');
            if (!cancelBtn) return;

            cancelBtn.addEventListener('click', (e) => {
                e.preventDefault();

                if (this.isPopupMode) {
                    window.close();
                } else {
                    window.location.href = this.options.cancelUrl || '/dashboard/resources/';
                }
            });
        }
    }

    // Export to global scope
    global.ResourceFormHandler = ResourceFormHandler;

})(window);

