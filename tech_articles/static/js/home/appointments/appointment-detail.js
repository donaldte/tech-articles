/**
 * Appointment Detail Manager
 *
 * Manages the appointment detail page, displaying appointment information
 * and handling the confirmation/payment flow.
 *
 * Features:
 * - OOP-based architecture
 * - Dynamic appointment data display
 * - Confirmation button handling
 * - Internationalization support
 *
 * @author Tech Articles Team
 * @version 1.0.0
 */

class AppointmentDetail {k
    constructor(config) {
        this.config = {
            ...config,
            i18n: {
                confirmPayment: gettext('Confirm & Pay'),
                processing: gettext('Processing...'),
                errorTitle: gettext('Error'),
                errorMessage: gettext('An error occurred. Please try again.'),
            }
        };
        this.confirmBtn = document.getElementById('confirm-appointment-btn');

        this.init();
    }

    /**
     * Initialize the manager
     */
    init() {
        this.displayTimezone();
        this.bindEvents();
    }

    /**
     * Display the user's timezone
     */
    displayTimezone() {
        const timezoneDisplay = document.getElementById('appointment-timezone');
        if (timezoneDisplay) {
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const offset = new Date().getTimezoneOffset();
            const offsetHours = Math.abs(Math.floor(offset / 60));
            const offsetMinutes = Math.abs(offset % 60);
            const offsetSign = offset <= 0 ? '+' : '-';
            const offsetString = `UTC${offsetSign}${offsetHours.toString().padStart(2, '0')}:${offsetMinutes.toString().padStart(2, '0')}`;
            timezoneDisplay.textContent = `${timezone} (${offsetString})`;
        }
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        if (this.confirmBtn) {
            this.confirmBtn.addEventListener('click', () => this.handleConfirmation());
        }
    }


    /**
     * Handle confirmation button click
     */
    handleConfirmation() {
        if (!this.confirmBtn) return;

        // Disable button to prevent double-clicks
        this.confirmBtn.disabled = true;

        // Update button text to show processing
        const originalText = this.confirmBtn.innerHTML;
        this.confirmBtn.innerHTML = `
            <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>${this.config.i18n.processing}</span>
        `;

        // Simulate processing delay, then redirect to payment page
        setTimeout(() => {
            window.location.href = this.config.paymentUrl;
        }, 500);
    }

    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    showError(message) {
        if (window.toastManager) {
            window.toastManager
                .buildToast()
                .setMessage(message)
                .setType('error')
                .setPosition('top-right')
                .setDuration(5000)
                .show();
        } else {
            alert(message);
        }

        // Re-enable button
        if (this.confirmBtn) {
            this.confirmBtn.disabled = false;
            this.confirmBtn.innerHTML = `
                <span>${this.config.i18n.confirmPayment}</span>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            `;
        }
    }
}
