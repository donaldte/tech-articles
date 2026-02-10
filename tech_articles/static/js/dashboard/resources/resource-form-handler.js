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
                fileInput: document.getElementById('file-input'),
                fileName: document.getElementById('file-name'),
                fileSize: document.getElementById('file-size'),
                fileIcon: document.getElementById('file-icon'),
                removeFileBtn: document.getElementById('remove-file-btn'),
                dropZone: document.getElementById('drop-zone'),
                fileInfo: document.getElementById('file-info'),
                dropZoneContent: document.getElementById('drop-zone-content'),
                categorySelect: document.getElementById('id_category'),
                articleSelect: document.getElementById('id_article'),
                cancelBtn: document.getElementById('cancel-btn'),
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
            if (!this.elements.fileInput) return;

            this.elements.fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.handleFileSelected(file);
                }
            });

            if (this.elements.removeFileBtn) {
                this.elements.removeFileBtn.addEventListener('click', () => {
                    this.clearFileSelection();
                });
            }
        }

        setupDragAndDrop() {
            if (!this.elements.dropZone) return;

            // Prevent defaults
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                this.elements.dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            });

            // Highlight drop zone
            ['dragenter', 'dragover'].forEach(eventName => {
                this.elements.dropZone.addEventListener(eventName, () => {
                    this.elements.dropZone.classList.add('border-primary', 'bg-primary/5');
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                this.elements.dropZone.addEventListener(eventName, () => {
                    this.elements.dropZone.classList.remove('border-primary', 'bg-primary/5');
                });
            });

            // Handle drop
            this.elements.dropZone.addEventListener('drop', (e) => {
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
            this.elements.fileInfo?.classList.remove('hidden');
            this.elements.dropZoneContent?.classList.add('hidden');
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

            if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|xls|xlsx|csv|ppt|pptx|png|jpg|jpeg|gif|svg|webp|mp3|wav|ogg|flac|mp4|mov|avi|mkv|zip|rar|7z|tar|gz|txt|odt)$/i)) {
                return {
                    valid: false,
                    error: gettext('Invalid file type. Only documents, spreadsheets, presentations, images, media, and archives are allowed.')
                };
            }

            return {valid: true};
        }

        updateFileDisplay(file) {
            if (this.elements.fileName) {
                this.elements.fileName.textContent = file.name;
            }

            if (this.elements.fileSize) {
                this.elements.fileSize.textContent = this.formatFileSize(file.size);
            }

            if (this.elements.fileIcon) {
                // Update icon based on file type
                this.elements.fileIcon.innerHTML = this.getFileIcon(file.name);
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
                pdf: '<svg class="w-8 h-8 text-red-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2 2 2 0 0 0 2 2h12a2 2 0 0 0 2-2 2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2V4a2 2 0 0 0-2-2h-7Zm-6 9a1 1 0 0 0-1 1v5a1 1 0 1 0 2 0v-1h.5a2.5 2.5 0 0 0 0-5H5Zm1.5 3H6v-1h.5a.5.5 0 0 1 0 1Zm4.5-3a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h1.376A2.626 2.626 0 0 0 15 15.375v-1.75A2.626 2.626 0 0 0 12.375 11H11Zm1 5v-3h.375a.626.626 0 0 1 .625.626v1.748a.625.625 0 0 1-.626.626H12Zm5-5a1 1 0 0 0-1 1v5a1 1 0 1 0 2 0v-1h1a1 1 0 1 0 0-2h-1v-1h1a1 1 0 1 0 0-2h-2Z" clip-rule="evenodd"></path></svg>',
                doc: '<svg class="w-8 h-8 text-blue-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm-1.02 4.804a1 1 0 1 0-1.96.392l1 5a1 1 0 0 0 1.838.319L12 15.61l1.143 1.905a1 1 0 0 0 1.838-.319l1-5a1 1 0 0 0-1.962-.392l-.492 2.463-.67-1.115a1 1 0 0 0-1.714 0l-.67 1.116-.492-2.464Z" clip-rule="evenodd"></path></svg>',
                docx: '<svg class="w-8 h-8 text-blue-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm-1.02 4.804a1 1 0 1 0-1.96.392l1 5a1 1 0 0 0 1.838.319L12 15.61l1.143 1.905a1 1 0 0 0 1.838-.319l1-5a1 1 0 0 0-1.962-.392l-.492 2.463-.67-1.115a1 1 0 0 0-1.714 0l-.67 1.116-.492-2.464Z" clip-rule="evenodd"></path></svg>',
                xls: '<svg class="w-8 h-8 text-green-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm2-2a1 1 0 1 0 0 2h3a1 1 0 1 0 0-2h-3Zm0 3a1 1 0 1 0 0 2h3a1 1 0 1 0 0-2h-3Zm-6 4a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1v-6Zm8 1v1h-2v-1h2Zm0 3h-2v1h2v-1Zm-4-3v1H9v-1h2Zm0 3H9v1h2v-1Z" clip-rule="evenodd"></path></svg>',
                xlsx: '<svg class="w-8 h-8 text-green-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm2-2a1 1 0 1 0 0 2h3a1 1 0 1 0 0-2h-3Zm0 3a1 1 0 1 0 0 2h3a1 1 0 1 0 0-2h-3Zm-6 4a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1v-6Zm8 1v1h-2v-1h2Zm0 3h-2v1h2v-1Zm-4-3v1H9v-1h2Zm0 3H9v1h2v-1Z" clip-rule="evenodd"></path></svg>',
                csv: '<svg class="w-8 h-8 text-green-600" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2 2 2 0 0 0 2 2h12a2 2 0 0 0 2-2 2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2V4a2 2 0 0 0-2-2h-7Zm1.018 8.828a2.34 2.34 0 0 0-2.373 2.13v.008a2.32 2.32 0 0 0 2.06 2.497l.535.059a.993.993 0 0 0 .136.006.272.272 0 0 1 .263.367l-.008.02a.377.377 0 0 1-.018.044.49.49 0 0 1-.078.02 1.689 1.689 0 0 1-.297.021h-1.13a1 1 0 1 0 0 2h1.13c.417 0 .892-.05 1.324-.279.47-.248.78-.648.953-1.134a2.272 2.272 0 0 0-2.115-3.06l-.478-.052a.32.32 0 0 1-.285-.341.34.34 0 0 1 .344-.306l.94.02a1 1 0 1 0 .043-2l-.943-.02h-.003Zm7.933 1.482a1 1 0 1 0-1.902-.62l-.57 1.747-.522-1.726a1 1 0 0 0-1.914.578l1.443 4.773a1 1 0 0 0 1.908.021l1.557-4.773Zm-13.762.88a.647.647 0 0 1 .458-.19h1.018a1 1 0 1 0 0-2H6.647A2.647 2.647 0 0 0 4 13.647v1.706A2.647 2.647 0 0 0 6.647 18h1.018a1 1 0 1 0 0-2H6.647A.647.647 0 0 1 6 15.353v-1.706c0-.172.068-.336.19-.457Z" clip-rule="evenodd"></path></svg>',
                ppt: '<svg class="w-8 h-8 text-orange-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2 2 2 0 0 0 2 2h12a2 2 0 0 0 2-2 2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2V4a2 2 0 0 0-2-2h-7Zm-6 9a1 1 0 0 0-1 1v5a1 1 0 1 0 2 0v-1h.5a2.5 2.5 0 0 0 0-5H5Zm1.5 3H6v-1h.5a.5.5 0 0 1 0 1Zm4.5-3a1 1 0 0 0-1 1v5a1 1 0 1 0 2 0v-1h.5a2.5 2.5 0 0 0 0-5H11Zm1.5 3H12v-1h.5a.5.5 0 0 1 0 1Zm4.5-3a1 1 0 1 0 0 2v4a1 1 0 1 0 2 0v-4a1 1 0 1 0 0-2h-2Z" clip-rule="evenodd"></path></svg>',
                pptx: '<svg class="w-8 h-8 text-orange-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2 2 2 0 0 0 2 2h12a2 2 0 0 0 2-2 2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2V4a2 2 0 0 0-2-2h-7Zm-6 9a1 1 0 0 0-1 1v5a1 1 0 1 0 2 0v-1h.5a2.5 2.5 0 0 0 0-5H5Zm1.5 3H6v-1h.5a.5.5 0 0 1 0 1Zm4.5-3a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h1.376A2.626 2.626 0 0 0 15 15.375v-1.75A2.626 2.626 0 0 0 12.375 11H11Zm1 5v-3h.375a.626.626 0 0 1 .625.626v1.748a.625.625 0 0 1-.626.626H12Zm5-5a1 1 0 0 0-1 1v5a1 1 0 1 0 2 0v-1h1a1 1 0 1 0 0-2h-1v-1h1a1 1 0 1 0 0-2h-2Z" clip-rule="evenodd"></path></svg>',
                png: '<svg class="w-8 h-8 text-purple-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm.394 9.553a1 1 0 0 0-1.817.062l-2.5 6A1 1 0 0 0 8 19h8a1 1 0 0 0 .894-1.447l-2-4A1 1 0 0 0 13.2 13.4l-.53.706-1.276-2.553ZM13 9.5a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Z" clip-rule="evenodd"></path></svg>',
                jpg: '<svg class="w-8 h-8 text-purple-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm.394 9.553a1 1 0 0 0-1.817.062l-2.5 6A1 1 0 0 0 8 19h8a1 1 0 0 0 .894-1.447l-2-4A1 1 0 0 0 13.2 13.4l-.53.706-1.276-2.553ZM13 9.5a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Z" clip-rule="evenodd"></path></svg>',
                jpeg: '<svg class="w-8 h-8 text-purple-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm.394 9.553a1 1 0 0 0-1.817.062l-2.5 6A1 1 0 0 0 8 19h8a1 1 0 0 0 .894-1.447l-2-4A1 1 0 0 0 13.2 13.4l-.53.706-1.276-2.553ZM13 9.5a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Z" clip-rule="evenodd"></path></svg>',
                gif: '<svg class="w-8 h-8 text-purple-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm.394 9.553a1 1 0 0 0-1.817.062l-2.5 6A1 1 0 0 0 8 19h8a1 1 0 0 0 .894-1.447l-2-4A1 1 0 0 0 13.2 13.4l-.53.706-1.276-2.553ZM13 9.5a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Z" clip-rule="evenodd"></path></svg>',
                svg: '<svg class="w-8 h-8 text-purple-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm.394 9.553a1 1 0 0 0-1.817.062l-2.5 6A1 1 0 0 0 8 19h8a1 1 0 0 0 .894-1.447l-2-4A1 1 0 0 0 13.2 13.4l-.53.706-1.276-2.553ZM13 9.5a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Z" clip-rule="evenodd"></path></svg>',
                webp: '<svg class="w-8 h-8 text-purple-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm.394 9.553a1 1 0 0 0-1.817.062l-2.5 6A1 1 0 0 0 8 19h8a1 1 0 0 0 .894-1.447l-2-4A1 1 0 0 0 13.2 13.4l-.53.706-1.276-2.553ZM13 9.5a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Z" clip-rule="evenodd"></path></svg>',
                mp3: '<svg class="w-8 h-8 text-pink-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm2.318.052h-.002A1 1 0 0 0 12 8v5.293A4.033 4.033 0 0 0 10.5 13C8.787 13 7 14.146 7 16s1.787 3 3.5 3 3.5-1.146 3.5-3c0-.107-.006-.211-.017-.313A1.04 1.04 0 0 0 14 15.5V9.766c.538.493 1 1.204 1 2.234a1 1 0 1 0 2 0c0-1.881-.956-3.14-1.86-3.893a6.4 6.4 0 0 0-1.636-.985 4.009 4.009 0 0 0-.165-.063l-.014-.005-.005-.001-.002-.001ZM9 16c0-.356.452-1 1.5-1s1.5.644 1.5 1-.452 1-1.5 1S9 16.356 9 16Z" clip-rule="evenodd"></path></svg>',
                wav: '<svg class="w-8 h-8 text-pink-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm2.318.052h-.002A1 1 0 0 0 12 8v5.293A4.033 4.033 0 0 0 10.5 13C8.787 13 7 14.146 7 16s1.787 3 3.5 3 3.5-1.146 3.5-3c0-.107-.006-.211-.017-.313A1.04 1.04 0 0 0 14 15.5V9.766c.538.493 1 1.204 1 2.234a1 1 0 1 0 2 0c0-1.881-.956-3.14-1.86-3.893a6.4 6.4 0 0 0-1.636-.985 4.009 4.009 0 0 0-.165-.063l-.014-.005-.005-.001-.002-.001ZM9 16c0-.356.452-1 1.5-1s1.5.644 1.5 1-.452 1-1.5 1S9 16.356 9 16Z" clip-rule="evenodd"></path></svg>',
                ogg: '<svg class="w-8 h-8 text-pink-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm2.318.052h-.002A1 1 0 0 0 12 8v5.293A4.033 4.033 0 0 0 10.5 13C8.787 13 7 14.146 7 16s1.787 3 3.5 3 3.5-1.146 3.5-3c0-.107-.006-.211-.017-.313A1.04 1.04 0 0 0 14 15.5V9.766c.538.493 1 1.204 1 2.234a1 1 0 1 0 2 0c0-1.881-.956-3.14-1.86-3.893a6.4 6.4 0 0 0-1.636-.985 4.009 4.009 0 0 0-.165-.063l-.014-.005-.005-.001-.002-.001ZM9 16c0-.356.452-1 1.5-1s1.5.644 1.5 1-.452 1-1.5 1S9 16.356 9 16Z" clip-rule="evenodd"></path></svg>',
                flac: '<svg class="w-8 h-8 text-pink-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm2.318.052h-.002A1 1 0 0 0 12 8v5.293A4.033 4.033 0 0 0 10.5 13C8.787 13 7 14.146 7 16s1.787 3 3.5 3 3.5-1.146 3.5-3c0-.107-.006-.211-.017-.313A1.04 1.04 0 0 0 14 15.5V9.766c.538.493 1 1.204 1 2.234a1 1 0 1 0 2 0c0-1.881-.956-3.14-1.86-3.893a6.4 6.4 0 0 0-1.636-.985 4.009 4.009 0 0 0-.165-.063l-.014-.005-.005-.001-.002-.001ZM9 16c0-.356.452-1 1.5-1s1.5.644 1.5 1-.452 1-1.5 1S9 16.356 9 16Z" clip-rule="evenodd"></path></svg>',
                mp4: '<svg class="w-8 h-8 text-indigo-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm-2 4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2H9Zm0 2h2v2H9v-2Zm7.965-.557a1 1 0 0 0-1.692-.72l-1.268 1.218a1 1 0 0 0-.308.721v.733a1 1 0 0 0 .37.776l1.267 1.032a1 1 0 0 0 1.631-.776v-2.984Z" clip-rule="evenodd"></path></svg>',
                mov: '<svg class="w-8 h-8 text-indigo-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm-2 4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2H9Zm0 2h2v2H9v-2Zm7.965-.557a1 1 0 0 0-1.692-.72l-1.268 1.218a1 1 0 0 0-.308.721v.733a1 1 0 0 0 .37.776l1.267 1.032a1 1 0 0 0 1.631-.776v-2.984Z" clip-rule="evenodd"></path></svg>',
                avi: '<svg class="w-8 h-8 text-indigo-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm-2 4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2H9Zm0 2h2v2H9v-2Zm7.965-.557a1 1 0 0 0-1.692-.72l-1.268 1.218a1 1 0 0 0-.308.721v.733a1 1 0 0 0 .37.776l1.267 1.032a1 1 0 0 0 1.631-.776v-2.984Z" clip-rule="evenodd"></path></svg>',
                mkv: '<svg class="w-8 h-8 text-indigo-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Zm2 0V2h7a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9h5a2 2 0 0 0 2-2Zm-2 4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2H9Zm0 2h2v2H9v-2Zm7.965-.557a1 1 0 0 0-1.692-.72l-1.268 1.218a1 1 0 0 0-.308.721v.733a1 1 0 0 0 .37.776l1.267 1.032a1 1 0 0 0 1.631-.776v-2.984Z" clip-rule="evenodd"></path></svg>',
                zip: '<svg class="w-8 h-8 text-yellow-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm3 2h2.01v2.01h-2V8h2v2.01h-2V12h2v2.01h-2V16h2v2.01h-2v2H12V18h2v-1.99h-2V14h2v-1.99h-2V10h2V8.01h-2V6h2V4Z" clip-rule="evenodd"></path></svg>',
                rar: '<svg class="w-8 h-8 text-yellow-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm3 2h2.01v2.01h-2V8h2v2.01h-2V12h2v2.01h-2V16h2v2.01h-2v2H12V18h2v-1.99h-2V14h2v-1.99h-2V10h2V8.01h-2V6h2V4Z" clip-rule="evenodd"></path></svg>',
                "7z": '<svg class="w-8 h-8 text-yellow-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm3 2h2.01v2.01h-2V8h2v2.01h-2V12h2v2.01h-2V16h2v2.01h-2v2H12V18h2v-1.99h-2V14h2v-1.99h-2V10h2V8.01h-2V6h2V4Z" clip-rule="evenodd"></path></svg>',
                tar: '<svg class="w-8 h-8 text-yellow-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm3 2h2.01v2.01h-2V8h2v2.01h-2V12h2v2.01h-2V16h2v2.01h-2v2H12V18h2v-1.99h-2V14h2v-1.99h-2V10h2V8.01h-2V6h2V4Z" clip-rule="evenodd"></path></svg>',
                gz: '<svg class="w-8 h-8 text-yellow-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Zm3 2h2.01v2.01h-2V8h2v2.01h-2V12h2v2.01h-2V16h2v2.01h-2v2H12V18h2v-1.99h-2V14h2v-1.99h-2V10h2V8.01h-2V6h2V4Z" clip-rule="evenodd"></path></svg>',
                txt: '<svg class="w-8 h-8 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7ZM8 16a1 1 0 0 1 1-1h6a1 1 0 1 1 0 2H9a1 1 0 0 1-1-1Zm1-5a1 1 0 1 0 0 2h6a1 1 0 1 0 0-2H9Z" clip-rule="evenodd"></path></svg>',
                odt: '<svg class="w-8 h-8 text-blue-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M6 16v-3h.375a.626.626 0 0 1 .625.626v1.749a.626.626 0 0 1-.626.625H6Zm6-2.5a.5.5 0 1 1 1 0v2a.5.5 0 0 1-1 0v-2Z"></path><path fill-rule="evenodd" d="M11 7V2h7a2 2 0 0 1 2 2v5h1a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-1a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2H3a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1h6a2 2 0 0 0 2-2Zm7.683 6.006 1.335-.024-.037-2-1.327.024a2.647 2.647 0 0 0-2.636 2.647v1.706a2.647 2.647 0 0 0 2.647 2.647H20v-2h-1.335a.647.647 0 0 1-.647-.647v-1.706a.647.647 0 0 1 .647-.647h.018ZM5 11a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h1.376A2.626 2.626 0 0 0 9 15.375v-1.75A2.626 2.626 0 0 0 6.375 11H5Zm7.5 0a2.5 2.5 0 0 0-2.5 2.5v2a2.5 2.5 0 0 0 5 0v-2a2.5 2.5 0 0 0-2.5-2.5Z" clip-rule="evenodd"></path><path d="M9 7V2.221a2 2 0 0 0-.5.365L4.586 6.5a2 2 0 0 0-.365.5H9Z"></path></svg>',
            };
            return icons[ext] || '<svg class="w-8 h-8 text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M9 2.221V7H4.221a2 2 0 0 1 .365-.5L8.5 2.586A2 2 0 0 1 9 2.22ZM11 2v5a2 2 0 0 1-2 2H4v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2h-7Z" clip-rule="evenodd"></path></svg>';
        }

        clearFileSelection() {
            this.currentFile = null;

            if (this.elements.fileInput) {
                this.elements.fileInput.value = '';
            }

            this.elements.fileInfo?.classList.add('hidden');
            this.elements.dropZoneContent?.classList.remove('hidden');

            // Clear progress
            const progressContainer = document.getElementById(`progress-container-${this.uploadInputId}`);
            if (progressContainer) {
                progressContainer.classList.add('hidden');
            }
        }

        setupCategoryFilter() {
            if (!this.elements.categorySelect || !this.elements.articleSelect) return;

            this.elements.categorySelect.addEventListener('change', async (e) => {
                const categoryId = e.target.value;

                if (!categoryId) {
                    // Reset articles
                    this.elements.articleSelect.innerHTML = '<option value="">---------</option>';
                    return;
                }

                // Fetch articles for this category
                try {
                    global.loader?.show();
                    const response = await fetch(`${this.options.articlesByCategory}?category_id=${categoryId}`);
                    if (!response.ok) throw new Error('Failed to fetch articles');

                    const data = await response.json();

                    // Update article select
                    this.elements.articleSelect.innerHTML = '<option value="">---------</option>';
                    data.articles.forEach(article => {
                        const option = document.createElement('option');
                        option.value = article.id;
                        option.textContent = article.title;
                        this.elements.articleSelect.appendChild(option);
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
            if (!this.elements.cancelBtn) return;

            this.elements.cancelBtn.addEventListener('click', (e) => {
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

