/**
 * Article Pages Manager
 * Handles CRUD operations for article pages in the mini dashboard.
 * Uses Django i18n catalog for translations (gettext, ngettext, interpolate).
 */
class ArticlePagesManager {
    constructor(config) {
        this.articleId = config.articleId;
        this.pagesListUrl = config.pagesListUrl;
        this.pageCreateUrl = config.pageCreateUrl;
        this.pageUpdateUrl = config.pageUpdateUrl;
        this.pageDeleteUrl = config.pageDeleteUrl;
        this.pageGetUrl = config.pageGetUrl;
        this.csrfToken = config.csrfToken;
        
        this.currentPage = 1;
        this.perPage = 6;
        this.editingPageId = null;
        
        this.init();
    }

    init() {
        this.bindAddPageButtons();
        this.loadPages();
    }

    /**
     * Bind add page buttons
     */
    bindAddPageButtons() {
        const addPageBtn = document.getElementById('add-page-btn');
        const addPageEmptyBtn = document.getElementById('add-page-empty-btn');
        
        if (addPageBtn) {
            addPageBtn.addEventListener('click', () => this.showPageModal());
        }
        if (addPageEmptyBtn) {
            addPageEmptyBtn.addEventListener('click', () => this.showPageModal());
        }
    }

    /**
     * Load pages from server
     */
    async loadPages(page = 1) {
        this.currentPage = page;
        const url = `${this.pagesListUrl}?page=${page}&per_page=${this.perPage}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            const result = await response.json();

            if (result.success) {
                this.renderPages(result.pages, result.pagination);
            } else {
                this.showError(result.message);
            }
        } catch (error) {
            console.error('Error loading pages:', error);
            this.showError(gettext('Failed to load pages. Please try again.'));
        }
    }

    /**
     * Render pages as cards
     */
    renderPages(pages, pagination) {
        const container = document.querySelector('.pages-grid-container');
        if (!container) return;

        if (pages.length === 0) {
            container.innerHTML = this.getEmptyStateHTML();
            this.bindAddPageButtons();
            return;
        }

        // Create grid and pagination
        let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">';
        pages.forEach(page => {
            html += this.getPageCardHTML(page);
        });
        html += '</div>';

        // Add pagination
        if (pagination.total_pages > 1) {
            html += this.getPaginationHTML(pagination);
        }

        container.innerHTML = html;
        this.bindPageActions();
    }

    /**
     * Get HTML for a page card
     */
    getPageCardHTML(page) {
        const escapedTitle = this.escapeHtml(page.title);
        const escapedPreview = this.escapeHtml(page.preview);
        
        return `
            <div class="dashboard-card hover:border-primary/50 transition-all duration-300" data-page-id="${page.id}">
                <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center gap-3">
                        <span class="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center text-sm font-bold">
                            ${page.page_number}
                        </span>
                        <div>
                            <h3 class="text-text-primary font-medium">${escapedTitle}</h3>
                            <p class="text-text-muted text-xs">${gettext('Page')} ${page.page_number}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-1">
                        <button type="button" class="page-edit-btn p-2 rounded-lg text-text-secondary hover:text-primary hover:bg-surface-light transition-colors" 
                            data-page-id="${page.id}" title="${gettext('Edit')}">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button type="button" class="page-delete-btn p-2 rounded-lg text-text-secondary hover:text-red-500 hover:bg-red-500/10 transition-colors" 
                            data-page-id="${page.id}" title="${gettext('Delete')}">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                <!-- Content Preview -->
                <div class="bg-surface-light rounded-lg p-3 max-h-32 overflow-hidden">
                    <div class="text-text-secondary text-sm prose prose-sm prose-invert max-w-none line-clamp-4">
                        ${escapedPreview}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get pagination HTML
     */
    getPaginationHTML(pagination) {
        let html = '<div class="flex items-center justify-between mt-6 pt-6 border-t border-border-dark">';
        html += '<div class="text-text-muted text-sm">';
        html += gettext('Showing %(start)s to %(end)s of %(total)s pages').replace('%(start)s', ((pagination.current_page - 1) * this.perPage + 1))
            .replace('%(end)s', Math.min(pagination.current_page * this.perPage, pagination.total_count))
            .replace('%(total)s', pagination.total_count);
        html += '</div>';
        html += '<div class="flex gap-2">';
        
        // Previous button
        if (pagination.has_previous) {
            html += `<button type="button" class="pagination-btn px-4 py-2 rounded-lg bg-surface-light text-text-primary hover:bg-primary hover:text-white transition-colors" 
                data-page="${pagination.current_page - 1}">${gettext('Previous')}</button>`;
        }
        
        // Page numbers
        for (let i = 1; i <= pagination.total_pages; i++) {
            const isActive = i === pagination.current_page;
            const btnClass = isActive 
                ? 'pagination-btn px-4 py-2 rounded-lg bg-primary text-white' 
                : 'pagination-btn px-4 py-2 rounded-lg bg-surface-light text-text-primary hover:bg-primary hover:text-white transition-colors';
            html += `<button type="button" class="${btnClass}" data-page="${i}">${i}</button>`;
        }
        
        // Next button
        if (pagination.has_next) {
            html += `<button type="button" class="pagination-btn px-4 py-2 rounded-lg bg-surface-light text-text-primary hover:bg-primary hover:text-white transition-colors" 
                data-page="${pagination.current_page + 1}">${gettext('Next')}</button>`;
        }
        
        html += '</div></div>';
        return html;
    }

    /**
     * Get empty state HTML
     */
    getEmptyStateHTML() {
        return `
            <div class="dashboard-card text-center py-12">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-surface-light flex items-center justify-center">
                    <svg class="w-8 h-8 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                    </svg>
                </div>
                <h3 class="text-text-primary font-medium mb-1">${gettext('No pages yet')}</h3>
                <p class="text-text-muted text-sm mb-4">${gettext('Start by adding your first page to this article.')}</p>
                <button type="button" class="btn-primary inline-flex items-center gap-2" id="add-page-empty-btn">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    ${gettext('Add Page')}
                </button>
            </div>
        `;
    }

    /**
     * Bind page actions (edit, delete, pagination)
     */
    bindPageActions() {
        // Edit buttons
        document.querySelectorAll('.page-edit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const pageId = btn.dataset.pageId;
                this.editPage(pageId);
            });
        });

        // Delete buttons
        document.querySelectorAll('.page-delete-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const pageId = btn.dataset.pageId;
                this.deletePage(pageId);
            });
        });

        // Pagination buttons
        document.querySelectorAll('.pagination-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const page = parseInt(btn.dataset.page);
                this.loadPages(page);
            });
        });
    }

    /**
     * Show page modal for create/edit
     */
    showPageModal(pageData = null) {
        const isEdit = pageData !== null;
        const title = isEdit ? gettext('Edit Page') : gettext('Add New Page');
        
        const modalHTML = `
            <div id="page-modal" class="fixed inset-0 z-50 overflow-y-auto bg-black/50 flex items-center justify-center p-4" style="backdrop-filter: blur(4px);">
                <div class="bg-surface-dark rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto border border-border-dark">
                    <!-- Modal Header -->
                    <div class="flex items-center justify-between p-6 border-b border-border-dark sticky top-0 bg-surface-dark z-10">
                        <h3 class="text-xl font-bold text-text-primary">${title}</h3>
                        <button type="button" id="close-modal-btn" class="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-light transition-colors">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Modal Body -->
                    <form id="page-form" class="p-6 space-y-6">
                        <!-- Page Number -->
                        <div class="form-group">
                            <label for="page-number" class="form-label">${gettext('Page Number')} <span class="text-red-500">*</span></label>
                            <input type="number" name="page_number" id="page-number" 
                                value="${pageData ? pageData.page_number : ''}" 
                                min="1" class="dashboard-input w-full" required>
                            <p class="text-red-500 text-xs mt-1 hidden" id="page-number-error"></p>
                        </div>

                        <!-- Title -->
                        <div class="form-group">
                            <label for="page-title" class="form-label">${gettext('Title')}</label>
                            <input type="text" name="title" id="page-title" 
                                value="${pageData ? this.escapeHtml(pageData.title || '') : ''}" 
                                class="dashboard-input w-full" 
                                placeholder="${gettext('Optional page title')}">
                            <p class="text-red-500 text-xs mt-1 hidden" id="page-title-error"></p>
                        </div>

                        <!-- Content -->
                        <div class="form-group">
                            <label for="page-content" class="form-label">${gettext('Content')} <span class="text-red-500">*</span></label>
                            <textarea name="content" id="page-content" rows="10" 
                                class="dashboard-textarea w-full" required 
                                placeholder="${gettext('Markdown/MDX content for this page...')}">${pageData ? this.escapeHtml(pageData.content || '') : ''}</textarea>
                            <p class="text-text-muted text-xs mt-1">${gettext('Use Markdown or MDX format')}</p>
                            <p class="text-red-500 text-xs mt-1 hidden" id="page-content-error"></p>
                        </div>

                        <!-- Preview Content -->
                        <div class="form-group">
                            <label for="page-preview" class="form-label">${gettext('Preview Content')}</label>
                            <textarea name="preview_content" id="page-preview" rows="5" 
                                class="dashboard-textarea w-full" 
                                placeholder="${gettext('Optional preview content (visible before paywall)...')}">${pageData ? this.escapeHtml(pageData.preview_content || '') : ''}</textarea>
                            <p class="text-text-muted text-xs mt-1">${gettext('Content visible to users before payment')}</p>
                            <p class="text-red-500 text-xs mt-1 hidden" id="page-preview-error"></p>
                        </div>

                        <!-- Buttons -->
                        <div class="flex justify-end gap-3 pt-4 border-t border-border-dark">
                            <button type="button" id="cancel-modal-btn" class="px-6 py-2 rounded-lg bg-surface-light text-text-primary hover:bg-surface-lighter transition-colors">
                                ${gettext('Cancel')}
                            </button>
                            <button type="submit" id="save-page-btn" class="btn-primary">
                                <span id="save-page-text">${isEdit ? gettext('Update Page') : gettext('Create Page')}</span>
                                <span id="save-page-loader" class="hidden">
                                    <svg class="animate-spin h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    ${gettext('Saving...')}
                                </span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Add modal to DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Bind modal actions
        document.getElementById('close-modal-btn').addEventListener('click', () => this.closeModal());
        document.getElementById('cancel-modal-btn').addEventListener('click', () => this.closeModal());
        document.getElementById('page-form').addEventListener('submit', (e) => {
            e.preventDefault();
            if (isEdit) {
                this.updatePage(pageData.id);
            } else {
                this.createPage();
            }
        });
    }

    /**
     * Close modal
     */
    closeModal() {
        const modal = document.getElementById('page-modal');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * Create new page
     */
    async createPage() {
        const form = document.getElementById('page-form');
        const saveBtn = document.getElementById('save-page-btn');
        const saveText = document.getElementById('save-page-text');
        const saveLoader = document.getElementById('save-page-loader');

        // Clear previous errors
        this.clearFormErrors(form);

        // Show loading state
        saveBtn.disabled = true;
        saveText.classList.add('hidden');
        saveLoader.classList.remove('hidden');

        // Gather form data
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        try {
            const response = await fetch(this.pageCreateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (result.success) {
                this.closeModal();
                this.loadPages(this.currentPage);
                this.showSuccess(result.message);
            } else {
                // Show validation errors
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, message]) => {
                        this.showFieldError('page', field, message);
                    });
                }
                this.showError(result.message);
            }
        } catch (error) {
            console.error('Create page error:', error);
            this.showError(gettext('An unexpected error occurred. Please try again.'));
        } finally {
            saveBtn.disabled = false;
            saveText.classList.remove('hidden');
            saveLoader.classList.add('hidden');
        }
    }

    /**
     * Edit page
     */
    async editPage(pageId) {
        try {
            const url = this.pageGetUrl.replace('PAGE_ID', pageId);
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showPageModal(result.page);
            } else {
                this.showError(result.message);
            }
        } catch (error) {
            console.error('Error loading page:', error);
            this.showError(gettext('Failed to load page. Please try again.'));
        }
    }

    /**
     * Update page
     */
    async updatePage(pageId) {
        const form = document.getElementById('page-form');
        const saveBtn = document.getElementById('save-page-btn');
        const saveText = document.getElementById('save-page-text');
        const saveLoader = document.getElementById('save-page-loader');

        // Clear previous errors
        this.clearFormErrors(form);

        // Show loading state
        saveBtn.disabled = true;
        saveText.classList.add('hidden');
        saveLoader.classList.remove('hidden');

        // Gather form data
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        try {
            const url = this.pageUpdateUrl.replace('PAGE_ID', pageId);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (result.success) {
                this.closeModal();
                this.loadPages(this.currentPage);
                this.showSuccess(result.message);
            } else {
                // Show validation errors
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, message]) => {
                        this.showFieldError('page', field, message);
                    });
                }
                this.showError(result.message);
            }
        } catch (error) {
            console.error('Update page error:', error);
            this.showError(gettext('An unexpected error occurred. Please try again.'));
        } finally {
            saveBtn.disabled = false;
            saveText.classList.remove('hidden');
            saveLoader.classList.add('hidden');
        }
    }

    /**
     * Delete page
     */
    async deletePage(pageId) {
        if (!confirm(gettext('Are you sure you want to delete this page? This action cannot be undone.'))) {
            return;
        }

        try {
            const url = this.pageDeleteUrl.replace('PAGE_ID', pageId);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const result = await response.json();

            if (result.success) {
                this.loadPages(this.currentPage);
                this.showSuccess(result.message);
            } else {
                this.showError(result.message);
            }
        } catch (error) {
            console.error('Delete page error:', error);
            this.showError(gettext('Failed to delete page. Please try again.'));
        }
    }

    /**
     * Clear form errors
     */
    clearFormErrors(form) {
        const errorElements = form.querySelectorAll('[id$="-error"]');
        errorElements.forEach(el => {
            el.classList.add('hidden');
            el.textContent = '';
        });
    }

    /**
     * Show field error
     */
    showFieldError(formType, field, message) {
        const errorEl = document.getElementById(`${formType}-${field.replace('_', '-')}-error`);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove('hidden');
        }
    }

    /**
     * Show success toast
     */
    showSuccess(message) {
        if (window.toastManager) {
            window.toastManager.buildToast()
                .setMessage(message)
                .setType('success')
                .setPosition('top-right')
                .show();
        }
    }

    /**
     * Show error toast
     */
    showError(message) {
        if (window.toastManager) {
            window.toastManager.buildToast()
                .setMessage(message)
                .setType('danger')
                .setPosition('top-right')
                .show();
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
