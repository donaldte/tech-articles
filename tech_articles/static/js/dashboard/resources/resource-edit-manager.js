/**
 * Resource Edit Form Manager
 * Handles file replacement with drag & drop and multipart upload
 */

(function() {
  'use strict';

  class ResourceEditFormManager {
    constructor(formId, options = {}) {
      this.form = document.getElementById(formId);
      if (!this.form) {
        console.warn(`Form with id "${formId}" not found`);
        return;
      }

      // Configuration
      this.config = {
        maxFileSize: 100 * 1024 * 1024, // 100MB
        uploaderId: 'resource-file-upload',
        ...options
      };

      // Initialize upload manager
      this.uploadManager = new ResourceUploadManager(this.config.uploadEndpoints || {});

      // State
      this.currentFile = null;
      this.isUploading = false;

      // DOM elements
      this.elements = {
        fileInput: document.getElementById('file-input'),
        dropZone: document.getElementById('drop-zone'),
        fileInfo: document.getElementById('file-info'),
        dropZoneContent: document.getElementById('drop-zone-content'),
        removeFileBtn: document.getElementById('remove-file-btn'),
        submitBtn: document.getElementById('submit-btn'),
        cancelBtn: document.getElementById('cancel-btn'),
        fileName: document.getElementById('file-name'),
        fileSize: document.getElementById('file-size'),
        fileUploadSection: document.getElementById('file-upload-section'),
        // Hidden fields
        fileKeyInput: document.getElementById('file_key'),
        fileNameInput: document.getElementById('file_name'),
        fileSizeInput: document.getElementById('file_size'),
        contentTypeInput: document.getElementById('content_type')
      };

      this.init();
    }

    init() {
      this.setupFileInput();
      this.setupDragAndDrop();
      this.setupFormSubmission();
      this.setupButtons();
    }

    setupFileInput() {
      if (!this.elements.fileInput) return;

      this.elements.fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          this.handleFileSelected(file);
        }
      });
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
          this.elements.dropZone.classList.add('border-primary', 'bg-primary/5', 'dragging');
        });
      });

      ['dragleave', 'drop'].forEach(eventName => {
        this.elements.dropZone.addEventListener(eventName, () => {
          this.elements.dropZone.classList.remove('border-primary', 'bg-primary/5', 'dragging');
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

    setupButtons() {
      // Remove file button
      if (this.elements.removeFileBtn) {
        this.elements.removeFileBtn.addEventListener('click', () => {
          this.clearFileSelection();
        });
      }

      // Cancel button
      if (this.elements.cancelBtn) {
        this.elements.cancelBtn.addEventListener('click', (e) => {
          e.preventDefault();
            window.location.href = this.form.dataset.listUrl || '/dashboard/resources/';
        });
      }
    }

    setupFormSubmission() {
      this.form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // If no new file selected, submit normally
        if (!this.currentFile) {
          this.submitFormDirectly();
          return;
        }

        // If file selected, upload first then submit
        if (this.isUploading) {
          return; // Already uploading
        }

        await this.handleFileUploadAndSubmit();
      });
    }

    async handleFileUploadAndSubmit() {
      this.isUploading = true;
      this.toggleSubmitButton(false);

      // Scroll to upload section
      if (this.elements.fileUploadSection) {
        this.elements.fileUploadSection.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        });
      }

      try {
        // Upload file
        const uploadResult = await this.uploadManager.startUpload(
          this.config.uploaderId,
          this.currentFile
        );

        if (!uploadResult.success) {
          throw new Error(uploadResult.error || gettext('Upload failed'));
        }

        // Set hidden fields with uploaded file info
        this.updateHiddenFields(uploadResult);

        // Now submit the form
        this.submitFormDirectly();

      } catch (error) {
        console.error('Upload error:', error);
        this.showError(error.message || gettext('Failed to upload file'));
        this.isUploading = false;
        this.toggleSubmitButton(true);
      }
    }

    handleFileSelected(file) {
      // Validate file size
      if (file.size > this.config.maxFileSize) {
        this.showError(
          interpolate(
            gettext('File size must not exceed %s'),
            [this.formatFileSize(this.config.maxFileSize)]
          )
        );
        return;
      }

      this.currentFile = file;

      // Update UI
      if (this.elements.fileName) {
        this.elements.fileName.textContent = file.name;
      }
      if (this.elements.fileSize) {
        this.elements.fileSize.textContent = this.formatFileSize(file.size);
      }

      // Show file info, hide drop zone content
      this.elements.fileInfo?.classList.remove('hidden');
      this.elements.dropZoneContent?.classList.add('hidden');
    }

    clearFileSelection() {
      this.currentFile = null;

      if (this.elements.fileInput) {
        this.elements.fileInput.value = '';
      }

      this.elements.fileInfo?.classList.add('hidden');
      this.elements.dropZoneContent?.classList.remove('hidden');

      // Clear progress
      const progressContainer = document.getElementById(
        `progress-container-${this.config.uploaderId}`
      );
      if (progressContainer) {
        progressContainer.classList.add('hidden');
      }

      // Clear hidden fields
      this.clearHiddenFields();
    }

    updateHiddenFields(uploadResult) {
      if (this.elements.fileKeyInput) {
        this.elements.fileKeyInput.value = uploadResult.key || '';
      }
      if (this.elements.fileNameInput) {
        this.elements.fileNameInput.value = this.currentFile.name;
      }
      if (this.elements.fileSizeInput) {
        this.elements.fileSizeInput.value = this.currentFile.size;
      }
      if (this.elements.contentTypeInput) {
        this.elements.contentTypeInput.value = this.currentFile.type;
      }
    }

    clearHiddenFields() {
      if (this.elements.fileKeyInput) {
        this.elements.fileKeyInput.value = '';
      }
      if (this.elements.fileNameInput) {
        this.elements.fileNameInput.value = '';
      }
      if (this.elements.fileSizeInput) {
        this.elements.fileSizeInput.value = '';
      }
      if (this.elements.contentTypeInput) {
        this.elements.contentTypeInput.value = '';
      }
    }

    submitFormDirectly() {
      // Show loader only when submitting form (not during upload)
      window.loader?.show();
      this.form.submit();
    }

    toggleSubmitButton(enabled) {
      if (this.elements.submitBtn) {
        this.elements.submitBtn.disabled = !enabled;
      }
    }

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    showError(message) {
      if (window.toastManager) {
        window.toastManager.buildToast()
          .setMessage(message)
          .setType('danger')
          .show();
      } else {
        alert(message);
      }
    }

    showSuccess(message) {
      if (window.toastManager) {
        window.toastManager.buildToast()
          .setMessage(message)
          .setType('success')
          .show();
      }
    }
  }

  // Export to global scope
  window.ResourceEditFormManager = ResourceEditFormManager;
})();

