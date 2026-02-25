/**
 * appointment_payment.js
 * Handles the appointment payment summary page UI:
 * - Payment method tab switching (Stripe / PayPal)
 * - Redirects to Stripe Checkout or PayPal approval URL via the create endpoint
 *
 * Uses Django's gettext() / ngettext() / interpolate() for i18n
 * (loaded via {% url 'javascript-catalog' %} in the base template).
 */

class AppointmentPaymentManager {
    /**
     * @param {Object} config
     * @param {string} config.csrfToken  - Django CSRF token
     */
    constructor(config = {}) {
        this.csrfToken = config.csrfToken || this._getCsrfToken();

        this.tabs = document.querySelectorAll('.payment-tab');
        this.panels = document.querySelectorAll('.tab-panel');
        this.stripeBtn = document.getElementById('btn-stripe-pay');
        this.paypalBtn = document.getElementById('btn-paypal-pay');
        this.errorBox = document.getElementById('payment-error');
        this.errorMsg = document.getElementById('payment-error-message');

        this.init();
    }

    init() {
        this._bindTabEvents();
        this._bindPaymentButtons();
    }

    // ------------------------------------------------------------------
    // Tab switching
    // ------------------------------------------------------------------

    _bindTabEvents() {
        this.tabs.forEach((tab) => {
            tab.addEventListener('click', () => this._activateTab(tab.dataset.tab));
        });
    }

    _activateTab(tabName) {
        this.tabs.forEach((t) => {
            const isActive = t.dataset.tab === tabName;
            t.classList.toggle('active', isActive);
            t.classList.toggle('border-primary', isActive);
            t.classList.toggle('text-primary', isActive);
            t.classList.toggle('border-border', !isActive);
            t.classList.toggle('text-text-secondary', !isActive);
        });
        this.panels.forEach((p) => {
            p.classList.toggle('hidden', p.id !== `tab-${tabName}`);
        });
    }

    // ------------------------------------------------------------------
    // Payment buttons
    // ------------------------------------------------------------------

    _bindPaymentButtons() {
        if (this.stripeBtn) {
            this.stripeBtn.addEventListener('click', () => this._initiatePayment('stripe'));
        }
        if (this.paypalBtn) {
            this.paypalBtn.addEventListener('click', () => this._initiatePayment('paypal'));
        }
    }

    async _initiatePayment(gateway) {
        const btn = gateway === 'stripe' ? this.stripeBtn : this.paypalBtn;
        if (!btn) return;

        const appointmentId = btn.dataset.appointmentId;
        const createUrl = btn.dataset.createUrl;

        if (!appointmentId || !createUrl) {
            this._showError(gettext('Configuration error. Please refresh and try again.'));
            return;
        }

        this._setLoading(btn, true);
        this._hideError();

        try {
            const formData = new FormData();
            formData.append('appointment_id', appointmentId);
            formData.append('gateway', gateway);

            const response = await fetch(createUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                },
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                this._showError(data.error || gettext('An error occurred. Please try again.'));
                this._setLoading(btn, false);
                return;
            }

            if (gateway === 'stripe' && data.checkout_url) {
                window.location.href = data.checkout_url;
            } else if (gateway === 'paypal' && data.approval_url) {
                window.location.href = data.approval_url;
            } else {
                this._showError(gettext('Could not initiate payment. Please try again.'));
                this._setLoading(btn, false);
            }
        } catch (err) {
            this._showError(gettext('Network error. Please check your connection and try again.'));
            this._setLoading(btn, false);
        }
    }

    // ------------------------------------------------------------------
    // UI helpers
    // ------------------------------------------------------------------

    _setLoading(btn, loading) {
        if (!btn) return;
        btn.disabled = loading;
        if (loading) {
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = `
                <svg class="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                ${gettext('Processing…')}
            `;
        } else if (btn.dataset.originalText) {
            btn.innerHTML = btn.dataset.originalText;
        }
    }

    _showError(message) {
        if (this.errorBox && this.errorMsg) {
            this.errorMsg.textContent = message;
            this.errorBox.classList.remove('hidden');
        }
    }

    _hideError() {
        if (this.errorBox) {
            this.errorBox.classList.add('hidden');
        }
    }

    _getCsrfToken() {
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        if (el) return el.value;
        const cookie = document.cookie
            .split(';')
            .map((c) => c.trim())
            .find((c) => c.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}

// Auto-initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    new AppointmentPaymentManager();
});
