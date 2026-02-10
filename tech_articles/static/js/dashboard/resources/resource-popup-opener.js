/**
 * Resource Popup Opener - Helper to open resource creation popup and handle communication
 * Used from article creation/editing pages to add resources
 */
(function (global) {
    'use strict';

    class ResourcePopupOpener {
        constructor(options = {}) {
            this.popupWindow = null;
            this.onResourceCreated = options.onResourceCreated || function() {};
            this.articleCategories = options.articleCategories || [];

            // Setup message listener
            this.setupMessageListener();
        }

        /**
         * Open popup window for resource creation
         */
        open() {
            // Build URL with article categories
            let url = '/dashboard/resources/create/popup/';

            if (this.articleCategories.length > 0) {
                const categoriesParam = this.articleCategories.join(',');
                url += `?article_categories=${encodeURIComponent(categoriesParam)}`;
            }

            // Popup dimensions
            const width = 800;
            const height = 700;
            const left = (screen.width - width) / 2;
            const top = (screen.height - height) / 2;

            // Open popup
            this.popupWindow = window.open(
                url,
                'CreateResource',
                `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
            );

            if (!this.popupWindow) {
                if (global.toastManager) {
                    global.toastManager.buildToast()
                        .setMessage(gettext('Please allow popups for this site'))
                        .setType('warning')
                        .show();
                }
                return false;
            }

            // Focus popup
            this.popupWindow.focus();
            return true;
        }

        /**
         * Setup message listener for popup communication
         */
        setupMessageListener() {
            window.addEventListener('message', (event) => {
                // Verify origin for security
                if (event.origin !== window.location.origin) {
                    return;
                }

                // Handle resource created message
                if (event.data && event.data.type === 'resource-created') {
                    this.handleResourceCreated(event.data.resource);
                }
            });
        }

        /**
         * Handle resource created event from popup
         */
        handleResourceCreated(resource) {
            console.log('Resource created:', resource);

            // Show success toast
            if (global.toastManager) {
                global.toastManager.buildToast()
                    .setMessage(
                        interpolate(
                            gettext('Resource "%s" created successfully'),
                            [resource.title]
                        )
                    )
                    .setType('success')
                    .show();
            }

            // Call callback
            if (typeof this.onResourceCreated === 'function') {
                this.onResourceCreated(resource);
            }
        }

        /**
         * Update article categories (for dynamic filtering)
         */
        setArticleCategories(categories) {
            this.articleCategories = categories;
        }

        /**
         * Close popup if open
         */
        close() {
            if (this.popupWindow && !this.popupWindow.closed) {
                this.popupWindow.close();
                this.popupWindow = null;
            }
        }
    }

    // Export to global scope
    global.ResourcePopupOpener = ResourcePopupOpener;

})(window);

