/**
 * Manages a loading overlay with spinner animation for the entire document body or specific section
 */
class SimpleLoaderManager {
    /**
     * Initialize the loader manager
     * @param {string|null} sectionId - ID of the section to apply the loader to (null for document.body)
     * @param {number} [contentOpacity=0.5] - Opacity for content elements when loader is shown (default: 0.5)
     * @param {number} [backdropOpacity=0.3] - Opacity for the backdrop (default: 0.3)
     */
    constructor(sectionId = null, contentOpacity = 0.5, backdropOpacity = 0.3) {
        // Target specific section by ID or entire document body if no ID is provided
        this.section = sectionId ? document.getElementById(sectionId) : document.body;
        if (!this.section) {
            throw new Error(interpolate(gettext('Section with ID %s not found'), [sectionId]));
        }

        // Initialize loader components as null (will be created dynamically)
        this.loaderContainer = null;

        // Define loader ID
        this.loaderId = 'dynamic-loader-container';

        // Store configuration values
        this.contentOpacity = contentOpacity;
        this.backdropOpacity = backdropOpacity;

        // Determine positioning type based on section
        this.positionType = this.section === document.body ? 'fixed' : 'absolute';

        // Ensure section has relative positioning if using absolute positioning
        if (this.positionType === 'absolute' && window.getComputedStyle(this.section).position === 'static') {
            this.section.style.position = 'relative';
        }
    }

    /**
     * Create and show the loader with spinner animation
     */
    show() {
        if (this.isLoading()) {
            console.warn(gettext('Loader is already visible'));
            return;
        }

        // Create loader container with backdrop and spinner
        this.loaderContainer = document.createElement('div');
        this.loaderContainer.id = this.loaderId;
        this.loaderContainer.setAttribute('role', 'status');
        this.loaderContainer.setAttribute('aria-live', 'polite');
        this.loaderContainer.setAttribute('aria-label', gettext('Loading content, please wait'));
        this.loaderContainer.className = `${this.positionType} left-0 top-0 z-10000008 flex h-screen w-screen items-center justify-center transition-opacity duration-300`;
        this.loaderContainer.style.backgroundColor = `rgba(0, 0, 0, ${this.backdropOpacity})`;
        this.loaderContainer.style.opacity = '0';

        // Create spinner
        const spinner = document.createElement('div');
        spinner.className = 'size-12 md:size-14 animate-spin rounded-full border-5 border-solid border-primary border-t-primary/10';

        // Add screen reader text
        const srText = document.createElement('span');
        srText.className = 'sr-only';
        srText.textContent = gettext('Loading...');

        // Append spinner and text to loader container
        this.loaderContainer.appendChild(spinner);
        this.loaderContainer.appendChild(srText);

        // Append loader to section
        this.section.appendChild(this.loaderContainer);

        // Fade in loader
        requestAnimationFrame(() => {
            this.loaderContainer.style.opacity = '1';
        });

        // Dim content elements if contentOpacity < 1
        if (this.contentOpacity < 1) {
            this._dimContent();
        }
    }

    /**
     * Dim content elements (all children except loader)
     * @private
     */
    _dimContent() {
        const children = Array.from(this.section.children);
        children.forEach(element => {
            if (element !== this.loaderContainer && element.id !== 'loader') {
                element.style.transition = 'opacity 300ms ease-in-out';
                element.style.opacity = String(this.contentOpacity);
            }
        });
    }

    /**
     * Restore content opacity
     * @private
     */
    _restoreContent() {
        const children = Array.from(this.section.children);
        children.forEach(element => {
            if (element !== this.loaderContainer && element.id !== 'loader') {
                element.style.opacity = '1';
            }
        });
    }

    /**
     * Hide and remove the loader from DOM
     * @param {number} [delay=0] - Delay in ms before starting hide animation
     */
    hide(delay = 0) {
        if (!this.isLoading()) return;

        setTimeout(() => {
            // Fade out loader
            if (this.loaderContainer) {
                this.loaderContainer.style.opacity = '0';
            }

            // Restore content opacity
            this._restoreContent();

            // Wait for transition to complete before removing element
            setTimeout(() => {
                // Remove loader container
                if (this.loaderContainer && this.loaderContainer.parentNode === this.section) {
                    this.section.removeChild(this.loaderContainer);
                    this.loaderContainer = null;
                }
            }, 300); // Match transition duration
        }, delay);
    }

    /**
     * Check if the loader is currently visible
     * @returns {boolean} True if loader is visible
     */
    isLoading() {
        return this.loaderContainer !== null && document.getElementById(this.loaderId) !== null;
    }

    /**
     * Update backdrop opacity
     * @param {number} opacity - New opacity value (0-1)
     */
    updateBackdropOpacity(opacity) {
        this.backdropOpacity = opacity;
        if (this.loaderContainer) {
            this.loaderContainer.style.backgroundColor = `rgba(0, 0, 0, ${opacity})`;
        }
    }

    /**
     * Update content opacity
     * @param {number} opacity - New opacity value (0-1)
     */
    updateContentOpacity(opacity) {
        this.contentOpacity = opacity;
        if (this.isLoading()) {
            this._dimContent();
        }
    }
}
