/**
 * Payment Manager
 *
 * Manages the payment page, handling payment form validation,
 * payment method switching, and payment processing.
 *
 * Features:
 * - OOP-based architecture
 * - Payment method switching (Card/PayPal)
 * - Form validation
 * - Card number formatting
 * - Internationalization support
 * - Security features
 *
 * @author Tech Articles Team
 * @version 1.0.0
 */

class PaymentManager {
    /**
     * Initialize the payment manager
     * @param {Object} config - Configuration object
     * @param {number} config.slotId - Selected slot ID
     * @param {Object} config.i18n - Internationalization strings
     */
    constructor(config) {
        this.config = {
            ...config,
            i18n: {
                processing: gettext('Processing...'),
                paySecurely: gettext('Pay Securely'),
                paymentSuccess: gettext('Payment Successful!'),
                paymentFailed: gettext('Payment Failed'),
                invalidCard: gettext('Please enter a valid card number'),
                invalidExpiry: gettext('Please enter a valid expiry date'),
                invalidCVC: gettext('Please enter a valid CVC'),
                invalidEmail: gettext('Please enter a valid email address'),
                confirmationSent: gettext('Confirmation email has been sent'),
            }
        };
        this.paymentForm = document.getElementById('payment-form');
        this.submitBtn = document.getElementById('submit-payment-btn');
        this.submitBtnText = document.getElementById('submit-btn-text');

        // Payment method elements
        this.paymentMethodTabs = document.querySelectorAll('.payment-method-tab');
        this.cardPaymentForm = document.getElementById('card-payment-form');
        this.paypalPaymentForm = document.getElementById('paypal-payment-form');

        // Form inputs
        this.cardNumberInput = document.getElementById('card-number');
        this.expiryDateInput = document.getElementById('expiry-date');
        this.cvcInput = document.getElementById('cvc');
        this.emailInput = document.getElementById('email');
        this.cardholderNameInput = document.getElementById('cardholder-name');

        // Summary elements
        this.summaryService = document.getElementById('summary-service');
        this.summaryDate = document.getElementById('summary-date');
        this.summaryTime = document.getElementById('summary-time');
        this.summarySubtotal = document.getElementById('summary-subtotal');
        this.summaryTotal = document.getElementById('summary-total');

        this.init();
    }

    /**
     * Initialize the manager
     */
    init() {
        this.bindEvents();
        this.setupFormFormatting();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Payment method tabs
        this.paymentMethodTabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.switchPaymentMethod(e.target.closest('.payment-method-tab')));
        });

        // Form submission
        if (this.paymentForm) {
            this.paymentForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    /**
     * Setup form input formatting
     */
    setupFormFormatting() {
        // Format card number (add spaces every 4 digits)
        if (this.cardNumberInput) {
            this.cardNumberInput.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\s/g, '');
                e.target.value = value.match(/.{1,4}/g)?.join(' ') || value;
            });
        }

        // Format expiry date (MM/YY)
        if (this.expiryDateInput) {
            this.expiryDateInput.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length >= 2) {
                    value = value.slice(0, 2) + '/' + value.slice(2, 4);
                }
                e.target.value = value;
            });
        }

        // Only allow numbers in CVC
        if (this.cvcInput) {
            this.cvcInput.addEventListener('input', (e) => {
                e.target.value = e.target.value.replace(/\D/g, '');
            });
        }
    }

    /**
     * Switch payment method
     * @param {HTMLElement} selectedTab - Selected tab element
     */
    switchPaymentMethod(selectedTab) {
        if (!selectedTab) return;

        const method = selectedTab.dataset.paymentMethod;

        // Update tab states
        this.paymentMethodTabs.forEach(tab => {
            if (tab === selectedTab) {
                tab.classList.add('active', 'bg-primary', 'text-black', 'border-primary');
                tab.classList.remove('bg-transparent', 'text-white', 'border-white/20', 'hover:border-primary/50', 'hover:bg-primary/10');
            } else {
                tab.classList.remove('active', 'bg-primary', 'text-black', 'border-primary');
                tab.classList.add('bg-transparent', 'text-white', 'border-white/20', 'hover:border-primary/50', 'hover:bg-primary/10');
            }
        });

        // Show/hide payment forms
        if (method === 'card') {
            this.cardPaymentForm?.classList.remove('hidden');
            this.paypalPaymentForm?.classList.add('hidden');
        } else if (method === 'paypal') {
            this.cardPaymentForm?.classList.add('hidden');
            this.paypalPaymentForm?.classList.remove('hidden');
        }
    }


    /**
     * Display order summary
     * @param {Object} data - Order data
     */
    displayOrderSummary(data) {
        const lang = document.documentElement.lang || 'en';
        const dateOptions = {weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'};
        const formattedDate = data.date.toLocaleDateString(lang, dateOptions);

        if (this.summaryService) {
            this.summaryService.textContent = data.service;
        }
        if (this.summaryDate) {
            this.summaryDate.textContent = formattedDate;
        }
        if (this.summaryTime) {
            this.summaryTime.textContent = data.time;
        }
        if (this.summarySubtotal) {
            this.summarySubtotal.textContent = `$${data.subtotal.toFixed(2)}`;
        }
        if (this.summaryTotal) {
            this.summaryTotal.textContent = `$${data.total.toFixed(2)}`;
        }
    }

    /**
     * Validate card number using Luhn algorithm
     * @param {string} cardNumber - Card number to validate
     * @returns {boolean} - Validation result
     */
    validateCardNumber(cardNumber) {
        const digits = cardNumber.replace(/\s/g, '');
        if (!/^\d{13,19}$/.test(digits)) return false;

        let sum = 0;
        let isEven = false;

        for (let i = digits.length - 1; i >= 0; i--) {
            let digit = parseInt(digits[i], 10);

            if (isEven) {
                digit *= 2;
                if (digit > 9) digit -= 9;
            }

            sum += digit;
            isEven = !isEven;
        }

        return sum % 10 === 0;
    }

    /**
     * Validate expiry date
     * @param {string} expiry - Expiry date (MM/YY)
     * @returns {boolean} - Validation result
     */
    validateExpiryDate(expiry) {
        if (!/^\d{2}\/\d{2}$/.test(expiry)) return false;

        const [month, year] = expiry.split('/').map(n => parseInt(n, 10));
        if (month < 1 || month > 12) return false;

        const currentDate = new Date();
        const currentYear = currentDate.getFullYear() % 100;
        const currentMonth = currentDate.getMonth() + 1;

        return !(year < currentYear || (year === currentYear && month < currentMonth));
    }

    /**
     * Validate CVC
     * @param {string} cvc - CVC to validate
     * @returns {boolean} - Validation result
     */
    validateCVC(cvc) {
        return /^\d{3,4}$/.test(cvc);
    }

    /**
     * Validate email
     * @param {string} email - Email to validate
     * @returns {boolean} - Validation result
     */
    validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    /**
     * Validate payment form
     * @returns {Object} - Validation result with isValid and errors
     */
    validateForm() {
        const errors = [];

        // Validate cardholder name
        if (!this.cardholderNameInput?.value.trim()) {
            errors.push(gettext('Please enter the cardholder name'));
        }

        // Validate card number
        if (!this.validateCardNumber(this.cardNumberInput?.value || '')) {
            errors.push(this.config.i18n.invalidCard);
        }

        // Validate expiry date
        if (!this.validateExpiryDate(this.expiryDateInput?.value || '')) {
            errors.push(this.config.i18n.invalidExpiry);
        }

        // Validate CVC
        if (!this.validateCVC(this.cvcInput?.value || '')) {
            errors.push(this.config.i18n.invalidCVC);
        }

        // Validate email
        if (!this.validateEmail(this.emailInput?.value || '')) {
            errors.push(this.config.i18n.invalidEmail);
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Handle form submission
     * @param {Event} e - Form submit event
     */
    async handleFormSubmit(e) {
        e.preventDefault();

        const validation = this.validateForm();

        if (!validation.isValid) {
            this.showErrors(validation.errors);
            return;
        }

        // Disable submit button
        this.submitBtn.disabled = true;
        if (this.submitBtnText) {
            this.submitBtnText.textContent = this.config.i18n.processing;
        }

        // Simulate payment processing
        setTimeout(() => {
            this.processPayment();
        }, 2000);
    }

    /**
     * Process payment (real implementation)
     */
    async processPayment() {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await fetch(this.config.paymentUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: new URLSearchParams(new FormData(this.paymentForm)).toString()
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.showSuccess(data.message, data.redirect_url);
            } else {
                this.showPaymentError(data.message || this.config.i18n.paymentFailed);
                
                // Re-enable submit button
                this.submitBtn.disabled = false;
                if (this.submitBtnText) {
                    this.submitBtnText.textContent = this.config.i18n.paySecurely;
                }
            }
        } catch (error) {
            console.error('Payment error:', error);
            this.showPaymentError();
            
            this.submitBtn.disabled = false;
            if (this.submitBtnText) {
                this.submitBtnText.textContent = this.config.i18n.paySecurely;
            }
        }
    }

    /**
     * Show validation errors
     * @param {Array} errors - Array of error messages
     */
    showErrors(errors) {
        if (window.toastManager) {
            errors.forEach(error => {
                window.toastManager
                    .buildToast()
                    .setMessage(error)
                    .setType('error')
                    .setPosition('top-right')
                    .setDuration(4000)
                    .show();
            });
        } else {
            alert(errors.join('\n'));
        }
    }

    /**
     * Show payment error
     */
    showPaymentError() {
        if (window.toastManager) {
            window.toastManager
                .buildToast()
                .setMessage(this.config.i18n.paymentFailed)
                .setType('error')
                .setPosition('top-right')
                .setDuration(5000)
                .show();
        } else {
            alert(this.config.i18n.paymentFailed);
        }
    }

    /**
     * Show success message and redirect
     * @param {string} message - Success message
     * @param {string} redirectUrl - URL to redirect to
     */
    showSuccess(message, redirectUrl) {
        if (window.toastManager) {
            window.toastManager
                .buildToast()
                .setMessage(message || `${this.config.i18n.paymentSuccess} ${this.config.i18n.confirmationSent}`)
                .setType('success')
                .setPosition('top-right')
                .setDuration(3000)
                .show();
        } else {
            alert(message || this.config.i18n.paymentSuccess);
        }

        // Redirect after delay
        setTimeout(() => {
            window.location.href = redirectUrl || '/dashboard/my-appointments/';
        }, 2000);
    }
}
