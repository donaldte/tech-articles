/**
 * Manages a loading overlay with Lottie animation and backdrop for a specific section or the entire document body
 */
class LottieLoaderManager {
    /**
     * Initialize the Lottie loader manager
     * @param {string|null} sectionId - ID of the section to apply the loader to (null for document.body)
     * @param {string} animationPath - Path to the Lottie JSON animation file
     * @param {number} [contentOpacity=0.5] - Opacity for content elements when loader is shown (default: 0.5)
     * @param {number} [backdropOpacity=0.5] - Opacity for the backdrop (default: 0.5)
     * @param {number} [animationSize=120] - Size of the animation in pixels (default: 120)
     */
    constructor(sectionId = null, animationPath = '', contentOpacity = 0.5, backdropOpacity = 0.5, animationSize = 120) {
        // Target specific section by ID or entire document body if no ID is provided
        this.section = sectionId ? document.getElementById(sectionId) : document.body;
        if (!this.section) {
            throw new Error(interpolate(gettext('Section with ID %s not found'), [sectionId]));
        }

        // Store content elements (all children of the section)
        this.contentElements = Array.from(this.section.children);

        // Initialize loader components as null (will be created dynamically)
        this.loaderContainer = null;
        this.backdrop = null;
        this.animationContainer = null;
        this.lottieInstance = null;

        // Define loader and backdrop IDs
        this.loaderId = 'lottie-loader-container';
        this.backdropId = 'lottie-loader-backdrop';
        this.canvasId = 'lottie-loader-animation';

        // Store configuration values
        this.animationPath = animationPath;
        this.contentOpacity = contentOpacity;
        this.backdropOpacity = backdropOpacity;
        this.animationSize = animationSize;

        // Determine positioning type based on section
        this.positionType = this.section === document.body ? 'fixed' : 'absolute';

        // Ensure section has relative positioning if using absolute positioning
        if (this.positionType === 'absolute' && window.getComputedStyle(this.section).position === 'static') {
            this.section.style.position = 'relative';
        }
    }

    /**
     * Create and show the loader with Lottie animation and backdrop
     */
    showLoader() {
        if (this.isLoading()) {
            console.warn(gettext('Loader is already visible'));
            return;
        }

        // Create backdrop element
        this.backdrop = document.createElement('div');
        this.backdrop.id = this.backdropId;
        this.backdrop.className = `${this.positionType} inset-0 bg-[#19191B] transition-opacity duration-300 z-[9999]`;
        this.backdrop.style.opacity = '0';

        // Create loader container
        this.loaderContainer = document.createElement('div');
        this.loaderContainer.id = this.loaderId;
        this.loaderContainer.setAttribute('role', 'status');
        this.loaderContainer.setAttribute('aria-live', 'polite');
        this.loaderContainer.setAttribute('aria-label', gettext('Loading content, please wait'));
        this.loaderContainer.className = `${this.positionType} -translate-x-1/2 -translate-y-1/2 top-1/2 left-1/2 z-[10000] flex flex-col items-center justify-center`;

        // Create container for Lottie animation
        this.animationContainer = document.createElement('div');
        this.animationContainer.id = this.canvasId;
        this.animationContainer.className = 'block';
        this.animationContainer.style.width = `${this.animationSize}px`;
        this.animationContainer.style.height = `${this.animationSize}px`;

        // Add screen reader text
        const srText = document.createElement('span');
        srText.className = 'sr-only';
        srText.textContent = gettext('Loading...');

        // Append animation container and text to loader container
        this.loaderContainer.appendChild(this.animationContainer);
        this.loaderContainer.appendChild(srText);

        // Append backdrop and loader to section
        this.section.appendChild(this.backdrop);
        this.section.appendChild(this.loaderContainer);

        // Fade in backdrop
        requestAnimationFrame(() => {
            this.backdrop.style.opacity = this.backdropOpacity;
        });

        // Dim content elements using provided opacity
        this.contentElements.forEach(element => {
            if (element !== this.backdrop && element !== this.loaderContainer) {
                element.style.transition = 'opacity 300ms ease-in-out';
                element.style.opacity = this.contentOpacity;
            }
        });

        // Initialize Lottie animation
        this._initLottieAnimation();
    }

    /**
     * Initialize the Lottie animation on the container
     * @private
     */
    _initLottieAnimation() {
        try {
            // Check if lottie is available
            if (typeof lottie === 'undefined') {
                console.error(gettext('Lottie library is not loaded. Please include lottie-web.'));
                return;
            }

            // Initialize Lottie animation
            this.lottieInstance = lottie.loadAnimation({
                container: this.animationContainer,
                renderer: 'svg',
                loop: true,
                autoplay: true,
                path: this.animationPath
            });
        } catch (error) {
            console.error(interpolate(gettext('Failed to initialize Lottie animation: %s'), [error.message]));
        }
    }

    /**
     * Hide and remove the loader and backdrop from DOM
     */
    hideLoader() {
        // Fade out backdrop
        if (this.backdrop) {
            this.backdrop.style.opacity = '0';
        }

        // Restore content opacity
        this.contentElements.forEach(element => {
            if (element !== this.backdrop && element !== this.loaderContainer) {
                element.style.opacity = '1';
            }
        });

        // Wait for transition to complete before removing elements
        setTimeout(() => {
            // Destroy Lottie instance
            if (this.lottieInstance && typeof this.lottieInstance.destroy === 'function') {
                this.lottieInstance.destroy();
                this.lottieInstance = null;
            }

            // Remove backdrop
            if (this.backdrop && this.backdrop.parentNode === this.section) {
                this.section.removeChild(this.backdrop);
                this.backdrop = null;
            }

            // Remove loader container
            if (this.loaderContainer && this.loaderContainer.parentNode === this.section) {
                this.section.removeChild(this.loaderContainer);
                this.loaderContainer = null;
            }

            this.animationContainer = null;
        }, 300); // Match transition duration
    }

    /**
     * Check if the loader is currently visible
     * @returns {boolean} True if loader is visible
     */
    isLoading() {
        return this.loaderContainer !== null && document.getElementById(this.loaderId) !== null;
    }

    /**
     * Update the animation path and reload the Lottie animation
     * @param {string} newAnimationPath - New path to the Lottie JSON animation file
     */
    updateAnimation(newAnimationPath) {
        this.animationPath = newAnimationPath;
        if (this.isLoading()) {
            // Destroy current instance and reinitialize with new animation
            if (this.lottieInstance && typeof this.lottieInstance.destroy === 'function') {
                this.lottieInstance.destroy();
            }
            this._initLottieAnimation();
        }
    }

    /**
     * Update backdrop opacity
     * @param {number} opacity - New opacity value (0-1)
     */
    updateBackdropOpacity(opacity) {
        this.backdropOpacity = opacity;
        if (this.backdrop) {
            this.backdrop.style.opacity = opacity;
        }
    }

    /**
     * Update content opacity
     * @param {number} opacity - New opacity value (0-1)
     */
    updateContentOpacity(opacity) {
        this.contentOpacity = opacity;
        this.contentElements.forEach(element => {
            if (element !== this.backdrop && element !== this.loaderContainer) {
                element.style.opacity = opacity;
            }
        });
    }
}
