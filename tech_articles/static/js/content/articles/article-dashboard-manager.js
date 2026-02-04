/**
 * Article Dashboard Manager
 * Handles article updates in the mini dashboard (Details, SEO, Pricing tabs).
 * Uses Django i18n catalog for translations (gettext, ngettext, interpolate).
 */
class ArticleDashboardManager {
    constructor(config) {
        this.articleId = config.articleId;
        this.detailsUrl = config.detailsUrl;
        this.seoUrl = config.seoUrl;
        this.pricingUrl = config.pricingUrl;
        this.csrfToken = config.csrfToken;

        this.init();
    }

    init() {
        this.bindProfileDropdown();
        this.bindDetailsForm();
        this.bindSEOForm();
        this.bindPricingForm();
        this.bindCharacterCounters();
        this.bindPricingToggle();
    }

    /**
     * Bind profile dropdown toggle
     */
    bindProfileDropdown() {
        const profileBtn = document.getElementById('profile-btn');
        const profileDropdown = document.getElementById('profile-dropdown');

        if (profileBtn && profileDropdown) {
            profileBtn.addEventListener('click', (e) => {
                e.preventDefault();
                profileDropdown.classList.toggle('hidden');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
                    profileDropdown.classList.add('hidden');
                }
            });
        }
    }

    /**
     * Bind details form submission
     */
    bindDetailsForm() {
        const form = document.getElementById('details-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleFormSubmit(form, this.detailsUrl, 'details');
        });
    }

    /**
     * Bind SEO form submission
     */
    bindSEOForm() {
        const form = document.getElementById('seo-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleFormSubmit(form, this.seoUrl, 'seo');
        });
    }

    /**
     * Bind pricing form submission
     */
    bindPricingForm() {
        const form = document.getElementById('pricing-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleFormSubmit(form, this.pricingUrl, 'pricing');
        });
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(form, url, formType) {
        const saveBtn = document.getElementById(`save-${formType}-btn`);
        const saveText = document.getElementById(`save-${formType}-text`);
        const saveLoader = document.getElementById(`save-${formType}-loader`);

        // Clear previous errors
        this.clearFormErrors(form);

        // Show loading state
        if (saveBtn) saveBtn.disabled = true;
        if (saveText) saveText.classList.add('hidden');
        if (saveLoader) saveLoader.classList.remove('hidden');

        // Gather form data
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (result.success) {
                if (window.toastManager) {
                    window.toastManager.buildToast()
                        .setMessage(result.message)
                        .setType('success')
                        .setPosition('top-right')
                        .show();
                }
            } else {
                // Show validation errors
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, message]) => {
                        this.showFieldError(formType, field, message);
                    });
                }

                if (window.toastManager) {
                    window.toastManager.buildToast()
                        .setMessage(result.message || gettext('An error occurred.'))
                        .setType('danger')
                        .setPosition('top-right')
                        .show();
                }
            }
        } catch (error) {
            console.error('Form submission error:', error);
            if (window.toastManager) {
                window.toastManager.buildToast()
                    .setMessage(gettext('An unexpected error occurred. Please try again.'))
                    .setType('danger')
                    .setPosition('top-right')
                    .show();
            }
        } finally {
            // Reset loading state
            if (saveBtn) saveBtn.disabled = false;
            if (saveText) saveText.classList.remove('hidden');
            if (saveLoader) saveLoader.classList.add('hidden');
        }
    }

    /**
     * Clear form errors
     */
    clearFormErrors(form) {
        const errorElements = form.querySelectorAll('[id$="-error"]');
        errorElements.forEach(el => {
            el.classList.add('hidden');
            el.textContent = '';
        });
    }

    /**
     * Show field error
     */
    showFieldError(formType, field, message) {
        const errorEl = document.getElementById(`${formType}-${field}-error`);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove('hidden');
        }
    }

    /**
     * Bind character counters for SEO fields
     */
    bindCharacterCounters() {
        const seoTitle = document.getElementById('seo-title');
        const seoDescription = document.getElementById('seo-description');
        const seoTitleCount = document.getElementById('seo-title-count');
        const seoDescCount = document.getElementById('seo-desc-count');

        if (seoTitle && seoTitleCount) {
            seoTitle.addEventListener('input', () => {
                seoTitleCount.textContent = seoTitle.value.length;
            });
        }

        if (seoDescription && seoDescCount) {
            seoDescription.addEventListener('input', () => {
                seoDescCount.textContent = seoDescription.value.length;
            });
        }
    }

    /**
     * Bind pricing toggle (show/hide price field based on access type)
     */
    bindPricingToggle() {
        const accessSelect = document.getElementById('pricing-access');
        const priceGroup = document.getElementById('price-group');

        if (!accessSelect || !priceGroup) return;

        const togglePriceGroup = () => {
            if (accessSelect.value === 'paid') {
                priceGroup.classList.remove('hidden');
            } else {
                priceGroup.classList.add('hidden');
            }
        };

        // Initial state
        togglePriceGroup();

        // On change
        accessSelect.addEventListener('change', togglePriceGroup);
    }
}

// Export for use
window.ArticleDashboardManager = ArticleDashboardManager;
