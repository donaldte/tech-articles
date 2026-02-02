/**
 * Elegant Toast Manager for Runbookly
 * Manages toasts with customizable messages, types, positions, and animation durations.
 * Respects dark theme with primary accent color (#00E5FF).
 * Uses a builder pattern for flexible configuration.
 * @class
 */
class ToastManager {
    constructor() {
        this.toastContainer = document.createElement('div');
        this.toastContainer.id = 'toast-container';
        this.toastContainer.className = 'fixed z-[10000004] flex flex-col gap-3 pointer-events-none';
        document.body.appendChild(this.toastContainer);

        this.injectStyles();
    }

    /**
     * Injects CSS styles for toast animations and layout.
     * @private
     */
    injectStyles() {
        const styles = `
            #toast-container {
                max-width: 24rem;
                width: auto;
                pointer-events: none;
            }
            #toast-container > * {
                pointer-events: auto;
            }

            /* Animations for different positions */
            @keyframes slide-in-top {
                from { transform: translateY(-100%); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes slide-out-top {
                from { transform: translateY(0); opacity: 1; }
                to { transform: translateY(-100%); opacity: 0; }
            }
            @keyframes slide-in-bottom {
                from { transform: translateY(100%); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes slide-out-bottom {
                from { transform: translateY(0); opacity: 1; }
                to { transform: translateY(100%); opacity: 0; }
            }
            @keyframes slide-in-left {
                from { transform: translateX(-100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slide-out-left {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(-100%); opacity: 0; }
            }
            @keyframes slide-in-right {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slide-out-right {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
            @keyframes progress {
                from { width: 100%; }
                to { width: 0%; }
            }

            .animate-slide-in-top {
                animation: slide-in-top var(--animation-duration, 0.3s) ease-out forwards;
            }
            .animate-slide-out-top {
                animation: slide-out-top var(--animation-duration, 0.3s) ease-in forwards;
            }
            .animate-slide-in-bottom {
                animation: slide-in-bottom var(--animation-duration, 0.3s) ease-out forwards;
            }
            .animate-slide-out-bottom {
                animation: slide-out-bottom var(--animation-duration, 0.3s) ease-in forwards;
            }
            .animate-slide-in-left {
                animation: slide-in-left var(--animation-duration, 0.3s) ease-out forwards;
            }
            .animate-slide-out-left {
                animation: slide-out-left var(--animation-duration, 0.3s) ease-in forwards;
            }
            .animate-slide-in-right {
                animation: slide-in-right var(--animation-duration, 0.3s) ease-out forwards;
            }
            .animate-slide-out-right {
                animation: slide-out-right var(--animation-duration, 0.3s) ease-in forwards;
            }
            .progress-bar {
                animation: progress var(--progress-duration, 4s) linear forwards;
            }

            /* Toast styles */
            .toast-base {
                display: flex;
                align-items: center;
                width: 100%;
                max-width: 24rem;
                padding: 1rem;
                margin-bottom: 0.75rem;
                border-radius: 0.5rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(0, 229, 255, 0.2);
                backdrop-filter: blur(10px);
            }

            .toast-success {
                background: linear-gradient(135deg, #065f46 0%, #047857 100%);
                border-color: #10b981;
            }

            .toast-danger {
                background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
                border-color: #ef4444;
            }

            .toast-warning {
                background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
                border-color: #f59e0b;
            }

            .toast-info {
                background: linear-gradient(135deg, #164e63 0%, #155e75 100%);
                border-color: #00e5ff;
            }

            .toast-content {
                display: flex;
                align-items: center;
                width: 100%;
                gap: 0.75rem;
            }

            .toast-icon-wrapper {
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                width: 2rem;
                height: 2rem;
                border-radius: 0.5rem;
            }

            .toast-icon-success {
                background: #064e3b;
                color: #34d399;
            }

            .toast-icon-danger {
                background: #7f1d1d;
                color: #f87171;
            }

            .toast-icon-warning {
                background: #78350f;
                color: #fbbf24;
            }

            .toast-icon-info {
                background: #164e63;
                color: #22d3ee;
            }

            .toast-message {
                flex: 1;
                font-size: 0.875rem;
                color: #e5e7eb;
                line-height: 1.5;
                word-break: break-word;
            }

            .toast-close-btn {
                flex-shrink: 0;
                background: transparent;
                border: none;
                color: #9ca3af;
                cursor: pointer;
                padding: 0.375rem;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 2rem;
                height: 2rem;
                border-radius: 0.375rem;
                transition: all 0.2s ease;
                margin-left: 0.75rem;
            }

            .toast-close-btn:hover {
                color: #f3f4f6;
                background: rgba(255, 255, 255, 0.1);
            }

            .toast-close-btn:focus {
                outline: none;
                ring: 2px rgba(0, 229, 255, 0.5);
                background: rgba(0, 229, 255, 0.1);
            }

            .progress-bar-success {
                background: linear-gradient(90deg, #10b981, #06b6d4);
            }

            .progress-bar-danger {
                background: linear-gradient(90deg, #ef4444, #f87171);
            }

            .progress-bar-warning {
                background: linear-gradient(90deg, #f59e0b, #fbbf24);
            }

            .progress-bar-info {
                background: linear-gradient(90deg, #00e5ff, #06b6d4);
            }
        `;
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    /**
     * Sets the position of the toast container.
     * @param {string} position - The position ('top-left', 'top-right', 'bottom-left', 'bottom-right').
     * @private
     */
    setPosition(position) {
        this.toastContainer.style.top = '';
        this.toastContainer.style.right = '';
        this.toastContainer.style.bottom = '';
        this.toastContainer.style.left = '';

        switch (position) {
            case 'top-left':
                this.toastContainer.style.top = '1rem';
                this.toastContainer.style.left = '1rem';
                break;
            case 'top-right':
                this.toastContainer.style.top = '1rem';
                this.toastContainer.style.right = '1rem';
                break;
            case 'bottom-left':
                this.toastContainer.style.bottom = '1rem';
                this.toastContainer.style.left = '1rem';
                break;
            case 'bottom-right':
                this.toastContainer.style.bottom = '1rem';
                this.toastContainer.style.right = '1rem';
                break;
            default:
                this.toastContainer.style.top = '1rem';
                this.toastContainer.style.right = '1rem';
        }
    }

    /**
     * Creates a new ToastBuilder instance to configure a toast.
     * @returns {ToastBuilder} A new ToastBuilder instance.
     */
    buildToast() {
        return new ToastBuilder(this);
    }

    /**
     * Shows a toast with the specified configuration.
     * @private
     * @param {Object} config - The toast configuration.
     */
    showToast({ message, type = 'info', position = 'top-right', duration = 4000 }) {
        const toastStyles = {
            success: {
                id: `toast-success-${Date.now()}`,
                type: 'success',
                className: 'toast-success',
                iconClass: 'toast-icon-success',
                progressClass: 'progress-bar-success',
                icon: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>`
            },
            danger: {
                id: `toast-danger-${Date.now()}`,
                type: 'danger',
                className: 'toast-danger',
                iconClass: 'toast-icon-danger',
                progressClass: 'progress-bar-danger',
                icon: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                </svg>`
            },
            warning: {
                id: `toast-warning-${Date.now()}`,
                type: 'warning',
                className: 'toast-warning',
                iconClass: 'toast-icon-warning',
                progressClass: 'progress-bar-warning',
                icon: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>`
            },
            info: {
                id: `toast-info-${Date.now()}`,
                type: 'info',
                className: 'toast-info',
                iconClass: 'toast-icon-info',
                progressClass: 'progress-bar-info',
                icon: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                </svg>`
            }
        };

        const style = toastStyles[type] || toastStyles.info;

        // Determine animation based on position
        let slideInAnimation, slideOutAnimation;
        if (position.includes('top')) {
            slideInAnimation = position.includes('left') ? 'animate-slide-in-left' : 'animate-slide-in-right';
            slideOutAnimation = position.includes('left') ? 'animate-slide-out-left' : 'animate-slide-out-right';
        } else {
            slideInAnimation = position.includes('left') ? 'animate-slide-in-left' : 'animate-slide-in-right';
            slideOutAnimation = position.includes('left') ? 'animate-slide-out-left' : 'animate-slide-out-right';
        }

        // Create toast element
        const toast = document.createElement('div');
        toast.id = style.id;
        toast.className = `toast-base ${style.className} ${slideInAnimation}`;
        toast.setAttribute('role', 'alert');

        const animationDuration = Math.min(duration / 10, 500);
        toast.style.setProperty('--animation-duration', `${animationDuration}ms`);
        toast.style.setProperty('--progress-duration', `${duration}ms`);

        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon-wrapper ${style.iconClass}">
                    ${style.icon}
                </div>
                <div class="toast-message">${this.escapeHtml(message)}</div>
                <button type="button" class="toast-close-btn" aria-label="Close notification">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </button>
            </div>
            <div class="absolute bottom-0 left-0 h-1 ${style.progressClass} progress-bar w-full"></div>
        `;

        this.toastContainer.appendChild(toast);
        this.setPosition(position);

        // Close button handler
        const closeBtn = toast.querySelector('.toast-close-btn');
        closeBtn.addEventListener('click', () => {
            this.removeToast(toast, slideOutAnimation, animationDuration);
        });

        // Auto-close after specified duration
        setTimeout(() => {
            if (toast.parentElement) {
                this.removeToast(toast, slideOutAnimation, animationDuration);
            }
        }, duration);
    }

    /**
     * Remove a toast with animation.
     * @private
     */
    removeToast(toast, slideOutAnimation, animationDuration) {
        const slideInClass = Array.from(toast.classList).find(cls => cls.startsWith('animate-slide-in'));
        if (slideInClass) {
            toast.classList.remove(slideInClass);
        }
        toast.classList.add(slideOutAnimation);
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, animationDuration);
    }

    /**
     * Escape HTML special characters to prevent XSS.
     * @private
     */
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, char => map[char]);
    }

    /**
     * Closes all currently displayed toasts.
     */
    closeAllToasts() {
        const toasts = this.toastContainer.querySelectorAll('[role="alert"]');
        toasts.forEach(toast => {
            const slideInAnimation = Array.from(toast.classList).find(cls => cls.startsWith('animate-slide-in'));
            const direction = slideInAnimation ? slideInAnimation.replace('animate-slide-in-', '') : 'right';
            const slideOutAnimation = `animate-slide-out-${direction}`;
            const animationDuration = parseFloat(toast.style.getPropertyValue('--animation-duration')) || 300;

            this.removeToast(toast, slideOutAnimation, animationDuration);
        });
    }
}

/**
 * Builder class for configuring and displaying toasts fluently.
 * @class
 */
class ToastBuilder {
    /**
     * @param {ToastManager} manager - The ToastManager instance.
     */
    constructor(manager) {
        this.manager = manager;
        this.config = {
            message: '',
            type: 'info',
            position: 'top-right',
            duration: 4000
        };
    }

    /**
     * Sets the toast message.
     * @param {string} message - The message to display.
     * @returns {ToastBuilder} This builder instance.
     */
    setMessage(message) {
        this.config.message = message;
        return this;
    }

    /**
     * Sets the toast type.
     * @param {string} type - The type of toast ('success', 'danger', 'warning', 'info').
     * @returns {ToastBuilder} This builder instance.
     */
    setType(type) {
        this.config.type = type;
        return this;
    }

    /**
     * Sets the toast position.
     * @param {string} position - The position ('top-left', 'top-right', 'bottom-left', 'bottom-right').
     * @returns {ToastBuilder} This builder instance.
     */
    setPosition(position) {
        this.config.position = position;
        return this;
    }

    /**
     * Sets the duration of the toast progress bar and auto-close.
     * @param {number} duration - The duration in milliseconds.
     * @returns {ToastBuilder} This builder instance.
     */
    setDuration(duration) {
        this.config.duration = duration;
        return this;
    }

    /**
     * Shows the configured toast.
     */
    show() {
        if (!this.config.message) {
            console.error('Toast message is required');
            return;
        }
        this.manager.showToast(this.config);
    }
}

// Initialize and export singleton instance
const toastManager = new ToastManager();
window.toastManager = toastManager;
