/**
 * Article List Manager
 * Handles article creation and deletion on the list page.
 * Uses Django i18n catalog for translations (gettext, ngettext, interpolate).
 */
class ArticleListManager {
    constructor(config) {
        this.createUrl = config.createUrl;
        this.deleteUrlTemplate = config.deleteUrlTemplate;
        this.csrfToken = config.csrfToken;
        this.currentDeleteId = null;

        this.init();
    }

    init() {
        this.bindCreateEvents();
        this.bindDeleteEvents();
    }

    /**
     * Bind events for quick article creation
     */
    bindCreateEvents() {
        const toggleBtn = document.getElementById('toggle-create-btn');
        const emptyCreateBtn = document.getElementById('empty-create-btn');
        const closeBtn = document.getElementById('close-create-btn');
        const cancelBtn = document.getElementById('cancel-create-btn');
        const quickCreateSection = document.getElementById('quick-create-section');
        const quickCreateForm = document.getElementById('quick-create-form');

        // Toggle create section
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.showCreateSection());
        }

        if (emptyCreateBtn) {
            emptyCreateBtn.addEventListener('click', () => this.showCreateSection());
        }

        // Close create section
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideCreateSection());
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hideCreateSection());
        }

        // Form submission
        if (quickCreateForm) {
            quickCreateForm.addEventListener('submit', (e) => this.handleCreateSubmit(e));
        }
    }

    /**
     * Show the quick create section
     */
    showCreateSection() {
        const section = document.getElementById('quick-create-section');
        if (section) {
            section.classList.remove('hidden');
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            document.getElementById('article-title')?.focus();
        }
    }

    /**
     * Hide the quick create section
     */
    hideCreateSection() {
        const section = document.getElementById('quick-create-section');
        if (section) {
            section.classList.add('hidden');
            this.resetCreateForm();
        }
    }

    /**
     * Reset the create form
     */
    resetCreateForm() {
        const form = document.getElementById('quick-create-form');
        if (form) {
            form.reset();
        }
        this.clearCreateErrors();
    }

    /**
     * Clear create form errors
     */
    clearCreateErrors() {
        const titleError = document.getElementById('title-error');
        if (titleError) {
            titleError.classList.add('hidden');
            titleError.textContent = '';
        }
    }

    /**
     * Handle create form submission
     */
    async handleCreateSubmit(e) {
        e.preventDefault();
        this.clearCreateErrors();

        const form = e.target;
        const submitBtn = document.getElementById('submit-create-btn');
        const submitText = document.getElementById('submit-text');
        const submitLoader = document.getElementById('submit-loader');

        // Gather form data
        const title = form.querySelector('[name="title"]').value.trim();
        const language = form.querySelector('[name="language"]').value;
        const categoriesSelect = form.querySelector('[name="categories"]');
        const categories = categoriesSelect 
            ? Array.from(categoriesSelect.selectedOptions).map(opt => opt.value)
            : [];

        if (!title) {
            this.showCreateError('title', gettext('Article title is required.'));
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitText.classList.add('hidden');
        submitLoader.classList.remove('hidden');

        try {
            const response = await fetch(this.createUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    title: title,
                    language: language,
                    categories: categories,
                }),
            });

            const data = await response.json();

            if (data.success) {
                // Show success toast
                if (window.toastManager) {
                    window.toastManager.buildToast()
                        .setMessage(data.message)
                        .setType('success')
                        .setPosition('top-right')
                        .show();
                }

                // Redirect to mini dashboard
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                }
            } else {
                // Show validation errors
                if (data.errors) {
                    Object.entries(data.errors).forEach(([field, message]) => {
                        this.showCreateError(field, message);
                    });
                }
                
                // Show error toast
                if (window.toastManager) {
                    window.toastManager.buildToast()
                        .setMessage(data.message || gettext('An error occurred.'))
                        .setType('danger')
                        .setPosition('top-right')
                        .show();
                }
            }
        } catch (error) {
            console.error('Create article error:', error);
            if (window.toastManager) {
                window.toastManager.buildToast()
                    .setMessage(gettext('An unexpected error occurred. Please try again.'))
                    .setType('danger')
                    .setPosition('top-right')
                    .show();
            }
        } finally {
            // Reset loading state
            submitBtn.disabled = false;
            submitText.classList.remove('hidden');
            submitLoader.classList.add('hidden');
        }
    }

    /**
     * Show error for a create form field
     */
    showCreateError(field, message) {
        const errorEl = document.getElementById(`${field}-error`);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove('hidden');
        }
    }

    /**
     * Bind events for article deletion
     */
    bindDeleteEvents() {
        const deleteButtons = document.querySelectorAll('.delete-article-btn');
        const confirmBtn = document.getElementById('confirm-delete-btn');

        deleteButtons.forEach(button => {
            button.addEventListener('click', (e) => this.handleDeleteClick(e));
        });

        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.handleDeleteConfirm());
        }
    }

    /**
     * Handle delete button click
     */
    handleDeleteClick(e) {
        const button = e.currentTarget;
        this.currentDeleteId = button.dataset.articleId;
        const articleTitle = button.dataset.articleTitle;

        const titleEl = document.getElementById('delete-article-title');
        if (titleEl) {
            titleEl.textContent = `"${articleTitle}"`;
        }
    }

    /**
     * Handle delete confirmation
     */
    async handleDeleteConfirm() {
        if (!this.currentDeleteId) return;

        const confirmBtn = document.getElementById('confirm-delete-btn');
        const deleteText = document.getElementById('delete-text');
        const deleteLoader = document.getElementById('delete-loader');

        // Show loading state
        confirmBtn.disabled = true;
        deleteText.classList.add('hidden');
        deleteLoader.classList.remove('hidden');

        const deleteUrl = this.deleteUrlTemplate.replace(
            '00000000-0000-0000-0000-000000000000',
            this.currentDeleteId
        );

        try {
            const response = await fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            const data = await response.json();

            if (data.success) {
                // Show success toast
                if (window.toastManager) {
                    window.toastManager.buildToast()
                        .setMessage(data.message)
                        .setType('success')
                        .setPosition('top-right')
                        .show();
                }

                // Remove the card from DOM
                const card = document.querySelector(`[data-article-id="${this.currentDeleteId}"]`);
                if (card) {
                    card.remove();
                }

                // Close modal
                this.closeDeleteModal();

                // Reload if no articles left
                const remainingCards = document.querySelectorAll('[data-article-id]');
                if (remainingCards.length === 0) {
                    window.location.reload();
                }
            } else {
                if (window.toastManager) {
                    window.toastManager.buildToast()
                        .setMessage(data.message || gettext('An error occurred.'))
                        .setType('danger')
                        .setPosition('top-right')
                        .show();
                }
            }
        } catch (error) {
            console.error('Delete article error:', error);
            if (window.toastManager) {
                window.toastManager.buildToast()
                    .setMessage(gettext('An unexpected error occurred. Please try again.'))
                    .setType('danger')
                    .setPosition('top-right')
                    .show();
            }
        } finally {
            // Reset loading state
            confirmBtn.disabled = false;
            deleteText.classList.remove('hidden');
            deleteLoader.classList.add('hidden');
            this.currentDeleteId = null;
        }
    }

    /**
     * Close the delete modal
     */
    closeDeleteModal() {
        const modal = document.getElementById('delete-modal');
        if (modal) {
            // Use Flowbite modal API if available
            const hideButton = modal.querySelector('[data-modal-hide="delete-modal"]');
            if (hideButton) {
                hideButton.click();
            } else {
                modal.classList.add('hidden');
            }
        }
    }
}

// Export for use
window.ArticleListManager = ArticleListManager;
