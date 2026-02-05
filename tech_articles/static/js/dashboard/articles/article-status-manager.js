/**
 * Article Status Manager
 * Manages article status transitions (publish, archive, restore) with dynamic UI updates.
 */
class ArticleStatusManager {
    constructor(articleId, initialStatus) {
        this.articleId = articleId;
        this.currentStatus = initialStatus;
        this.button = document.getElementById('article-status-action-btn');
        this.statusBadge = document.querySelector('.status-badge');
        this.statusSelect = document.getElementById('id_status');
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        this.init();
    }

    init() {
        if (!this.button) {
            console.error('Article status action button not found');
            return;
        }

        // Set initial button state
        this.updateButton();

        // Add click event listener
        this.button.addEventListener('click', () => this.handleStatusChange());
    }

    /**
     * Update button appearance based on current status
     */
    updateButton() {
        // Remove all status-specific classes
        this.button.className = 'px-4 py-2 text-xs md:text-sm font-medium rounded-lg transition-colors';

        switch (this.currentStatus) {
            case 'draft':
                this.button.classList.add('btn-primary');
                this.button.textContent = gettext('Publish Article');
                this.button.setAttribute('aria-label', gettext('Publish article'));
                this.button.dataset.action = 'publish';
                break;

            case 'published':
                this.button.classList.add('bg-orange-500', 'hover:bg-orange-600', 'text-white');
                this.button.textContent = gettext('Archive Article');
                this.button.setAttribute('aria-label', gettext('Archive article'));
                this.button.dataset.action = 'archive';
                break;

            case 'archived':
                this.button.classList.add('bg-green-500', 'hover:bg-green-600', 'text-white');
                this.button.textContent = gettext('Restore Article');
                this.button.setAttribute('aria-label', gettext('Restore article'));
                this.button.dataset.action = 'restore';
                break;

            default:
                // For scheduled or other statuses, hide the button
                this.button.style.display = 'none';
        }
    }

    /**
     * Update status badge in header
     */
    updateStatusBadge(status, statusDisplay) {
        if (!this.statusBadge) return;

        // Remove all status-specific classes
        this.statusBadge.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium status-badge';

        // Update badge text
        this.statusBadge.textContent = statusDisplay;

        // Add appropriate color classes based on status
        switch (status) {
            case 'published':
                this.statusBadge.classList.add('bg-green-500/20', 'text-green-400', 'border', 'border-green-500/30');
                break;
            case 'draft':
                this.statusBadge.classList.add('bg-yellow-500/20', 'text-yellow-400', 'border', 'border-yellow-500/30');
                break;
            case 'archived':
                this.statusBadge.classList.add('bg-gray-500/20', 'text-gray-400', 'border', 'border-gray-500/30');
                break;
            case 'scheduled':
                this.statusBadge.classList.add('bg-blue-500/20', 'text-blue-400', 'border', 'border-blue-500/30');
                break;
        }
    }

    /**
     * Update status dropdown if it exists on the page
     */
    updateStatusSelect(status) {
        if (!this.statusSelect) return;

        // Update the selected option
        this.statusSelect.value = status;
        
        // Trigger change event if needed
        const event = new Event('change', { bubbles: true });
        this.statusSelect.dispatchEvent(event);
    }

    /**
     * Get API endpoint based on action
     */
    getApiEndpoint(action) {
        const baseUrl = `/dashboard/content/articles/${this.articleId}/api/${action}/`;
        return baseUrl;
    }

    /**
     * Handle status change button click
     */
    async handleStatusChange() {
        const action = this.button.dataset.action;
        
        if (!action) {
            console.error('No action defined for button');
            return;
        }

        // Disable button during request
        this.button.disabled = true;
        const originalText = this.button.textContent;
        this.button.textContent = gettext('Processing...');

        try {
            const response = await fetch(this.getApiEndpoint(action), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
            });

            const data = await response.json();

            if (data.success) {
                // Update current status
                this.currentStatus = data.article.status;

                // Update all UI elements
                this.updateButton();
                this.updateStatusBadge(data.article.status, data.article.status_display);
                this.updateStatusSelect(data.article.status);

                // Show success toast
                window.toastManager.buildToast()
                    .setMessage(data.message)
                    .setType('success')
                    .setPosition('top-right')
                    .setDuration(4000)
                    .show();
            } else {
                // Show error toast
                window.toastManager.buildToast()
                    .setMessage(data.message)
                    .setType('danger')
                    .setPosition('top-right')
                    .setDuration(5000)
                    .show();

                // Reset button
                this.button.textContent = originalText;
            }
        } catch (error) {
            console.error('Error updating article status:', error);
            
            // Show error toast
            window.toastManager.buildToast()
                .setMessage(gettext('An error occurred while updating the article status. Please try again.'))
                .setType('danger')
                .setPosition('top-right')
                .setDuration(5000)
                .show();

            // Reset button
            this.button.textContent = originalText;
        } finally {
            // Re-enable button
            this.button.disabled = false;
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('article-status-action-btn');
    if (button) {
        const articleId = button.dataset.articleId;
        const articleStatus = button.dataset.articleStatus;
        
        if (articleId && articleStatus) {
            window.articleStatusManager = new ArticleStatusManager(articleId, articleStatus);
        }
    }
});
