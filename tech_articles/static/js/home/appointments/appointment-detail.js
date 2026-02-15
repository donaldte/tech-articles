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

class AppointmentDetail {
    /**
     * Initialize the appointment detail manager
     * @param {Object} config - Configuration object
     * @param {number} config.slotId - Selected slot ID
     * @param {string} config.paymentUrl - URL for payment page
     * @param {Object} config.i18n - Internationalization strings
     */
    constructor(config) {
        this.config = config;
        this.confirmBtn = document.getElementById('confirm-appointment-btn');
        
        // DOM elements for displaying appointment data
        this.appointmentType = document.getElementById('appointment-type');
        this.appointmentDatetime = document.getElementById('appointment-datetime');
        this.appointmentDuration = document.getElementById('appointment-duration');
        this.appointmentPrice = document.getElementById('appointment-price');

        this.init();
    }

    /**
     * Initialize the manager
     */
    init() {
        this.loadAppointmentData();
        this.bindEvents();
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
     * Load appointment data (mock data for template)
     */
    loadAppointmentData() {
        // Mock appointment data
        const mockData = {
            type: gettext('Expert Consultation'),
            description: gettext('One-on-one expert consultation'),
            date: new Date(2026, 2, 15, 10, 0), // March 15, 2026, 10:00 AM
            duration: 60, // minutes
            price: 99.00,
            currency: 'USD'
        };

        this.displayAppointmentData(mockData);
    }

    /**
     * Display appointment data in the UI
     * @param {Object} data - Appointment data
     */
    displayAppointmentData(data) {
        // Format date and time
        const dateOptions = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        const timeOptions = { 
            hour: '2-digit', 
            minute: '2-digit' 
        };
        
        const lang = document.documentElement.lang || 'en';
        const formattedDate = data.date.toLocaleDateString(lang, dateOptions);
        const formattedTime = data.date.toLocaleTimeString(lang, timeOptions);
        const datetime = `${formattedDate} ${gettext('at')} ${formattedTime}`;

        // Update appointment type
        if (this.appointmentType) {
            this.appointmentType.textContent = data.type;
        }

        // Update datetime
        if (this.appointmentDatetime) {
            this.appointmentDatetime.textContent = datetime;
        }

        // Update duration
        if (this.appointmentDuration) {
            const durationText = ngettext(
                '%s minute',
                '%s minutes',
                data.duration
            );
            this.appointmentDuration.textContent = interpolate(durationText, [data.duration]);
        }

        // Update price
        if (this.appointmentPrice) {
            this.appointmentPrice.textContent = `$${data.price.toFixed(2)}`;
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
