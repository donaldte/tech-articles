/**
 * Article Pages Manager
 * Handles display and actions for article pages in the mini dashboard.
 * Uses view-based pages for create/edit instead of modals.
 * Uses Django i18n catalog for translations (gettext, ngettext, interpolate).
 */
class ArticlePagesManager {
    constructor(config) {
        this.articleId = config.articleId;
        this.pagesListUrl = config.pagesListUrl;
        this.pageCreateViewUrl = config.pageCreateViewUrl;
        this.pageEditViewUrl = config.pageEditViewUrl;
        this.pageDeleteUrl = config.pageDeleteUrl;
        this.csrfToken = config.csrfToken;

        this.currentPage = 1;
        this.perPage = 6;

        this.init();
    }

    init() {
        this.loadPages();
    }

    /**
     * Navigate to create page view
     */
    navigateToCreatePage() {
        window.location.href = this.pageCreateViewUrl;
    }

    /**
     * Navigate to edit page view
     */
    navigateToEditPage(pageId) {
        const url = this.pageEditViewUrl.replace('00000000-0000-0000-0000-000000000000', pageId);
        window.location.href = url;
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
            this.bindAddPageButton();
            return;
        }

        // Create grid and pagination
        let html = '<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">';
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
        const start = (pagination.current_page - 1) * this.perPage + 1;
        const end = Math.min(pagination.current_page * this.perPage, pagination.total_count);
        const total = pagination.total_count;
        html += interpolate(gettext('Showing %(start)s to %(end)s of %(total)s pages'), {start: start, end: end, total: total}, true);
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
     * Get empty state HTML (only button in the center)
     */
    getEmptyStateHTML() {
        return `
            <div class="text-center py-12">
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
     * Bind add page button (only in empty state)
     */
    bindAddPageButton() {
        const addPageEmptyBtn = document.getElementById('add-page-empty-btn');
        if (addPageEmptyBtn) {
            addPageEmptyBtn.addEventListener('click', () => this.navigateToCreatePage());
        }
    }

    /**
     * Bind page actions (edit, delete, pagination)
     */
    bindPageActions() {
        // Edit buttons - navigate to edit page
        document.querySelectorAll('.page-edit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const pageId = btn.dataset.pageId;
                this.navigateToEditPage(pageId);
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
     * Delete page
     */
    async deletePage(pageId) {
        // User must use the delete modal on the edit page
        // Just navigate to edit page where modal is available
        this.navigateToEditPage(pageId);
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
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
