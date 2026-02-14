/**
 * Newsletter Subscription Manager
 * 
 * Handles newsletter subscription with language dropdown selection,
 * form validation, loading states, and AJAX submission.
 * 
 * Features:
 * - OOP-based architecture
 * - Custom language dropdown with Flowbite v3
 * - Form validation
 * - Loading spinner with text
 * - Input disabling during submission
 * - Success/error notifications via toast manager
 * - CSRF token handling
 * 
 * @author Tech Articles Team
 * @version 2.0.0
 */

class NewsletterSubscriptionManager {
    /**
     * Initialize the newsletter subscription manager
     * @param {string} formId - ID of the newsletter form
     * @param {string} subscribeUrl - URL endpoint for subscription
     */
    constructor(formId, subscribeUrl) {
        this.form = document.getElementById(formId);
        this.subscribeUrl = subscribeUrl;
        
        if (!this.form) {
            console.warn(`Newsletter form with ID "${formId}" not found`);
            return;
        }
        
        this.emailInput = this.form.querySelector('input[name="email"]');
        this.languageInput = this.form.querySelector('input[name="language"]');
        this.submitButton = this.form.querySelector('button[type="submit"]');
        this.csrfInput = this.form.querySelector('input[name="csrfmiddlewaretoken"]');
        
        // Create language dropdown elements
        this.languageDropdown = null;
        this.languageButton = null;
        this.languageMenu = null;
        this.selectedLanguage = {code: 'fr', name: 'Français'};
        
        // Loading state
        this.isLoading = false;
        this.originalButtonText = '';
        
        this.init();
    }
    
    /**
     * Initialize the subscription manager
     */
    init() {
        this.createLanguageDropdown();
        this.bindEvents();
    }
    
    /**
     * Create custom language dropdown
     */
    createLanguageDropdown() {
        // Find the email input container
        const emailContainer = this.emailInput.closest('.flex');
        if (!emailContainer) return;
        
        // Create language dropdown button
        this.languageButton = document.createElement('button');
        this.languageButton.type = 'button';
        this.languageButton.className = 'form-input inline-flex items-center justify-between gap-2 min-w-[160px] whitespace-nowrap';
        this.languageButton.innerHTML = `
            <span class="flex items-center gap-2">
                <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"></path>
                </svg>
                <span id="selected-language-text">${this.selectedLanguage.name}</span>
            </span>
            <svg class="w-4 h-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
        `;
        
        // Create dropdown menu
        this.languageMenu = document.createElement('div');
        this.languageMenu.className = 'absolute hidden bg-surface-dark border border-border-dark rounded-lg shadow-xl py-2 mt-2 z-50 min-w-[160px]';
        this.languageMenu.innerHTML = `
            <button type="button" data-lang="fr" class="language-option w-full text-left px-4 py-2 hover:bg-surface-light transition-colors flex items-center gap-2">
                <svg class="w-5 h-5 text-primary opacity-0 language-check" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
                <span class="text-text-primary">Français</span>
            </button>
            <button type="button" data-lang="en" class="language-option w-full text-left px-4 py-2 hover:bg-surface-light transition-colors flex items-center gap-2">
                <svg class="w-5 h-5 text-primary opacity-0 language-check" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
                <span class="text-text-primary">English</span>
            </button>
            <button type="button" data-lang="es" class="language-option w-full text-left px-4 py-2 hover:bg-surface-light transition-colors flex items-center gap-2">
                <svg class="w-5 h-5 text-primary opacity-0 language-check" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
                <span class="text-text-primary">Español</span>
            </button>
        `;
        
        // Create wrapper for dropdown
        this.languageDropdown = document.createElement('div');
        this.languageDropdown.className = 'relative';
        this.languageDropdown.appendChild(this.languageButton);
        this.languageDropdown.appendChild(this.languageMenu);
        
        // Insert immediately after email input (before submit button)
        // Find the submit button and insert the dropdown before it
        const submitButton = emailContainer.querySelector('button[type="submit"]');
        if (submitButton) {
            emailContainer.insertBefore(this.languageDropdown, submitButton);
        } else {
            emailContainer.appendChild(this.languageDropdown);
        }
        
        // Create hidden input for language
        if (!this.languageInput) {
            this.languageInput = document.createElement('input');
            this.languageInput.type = 'hidden';
            this.languageInput.name = 'language';
            this.form.appendChild(this.languageInput);
        }
        
        // Update the selected language display
        this.updateSelectedLanguage('fr');
    }
    
    /**
     * Update selected language display
     */
    updateSelectedLanguage(langCode) {
        const languageNames = {
            'fr': 'Français',
            'en': 'English',
            'es': 'Español'
        };
        
        this.selectedLanguage = {
            code: langCode,
            name: languageNames[langCode] || 'Français'
        };
        
        // Update button text
        const textElement = this.languageButton.querySelector('#selected-language-text');
        if (textElement) {
            textElement.textContent = this.selectedLanguage.name;
        }
        
        // Update hidden input
        if (this.languageInput) {
            this.languageInput.value = langCode;
        }
        
        // Update checkmarks
        const options = this.languageMenu.querySelectorAll('.language-option');
        options.forEach(option => {
            const check = option.querySelector('.language-check');
            if (option.dataset.lang === langCode) {
                check.classList.remove('opacity-0');
                check.classList.add('opacity-100');
            } else {
                check.classList.remove('opacity-100');
                check.classList.add('opacity-0');
            }
        });
    }
    
    /**
     * Toggle dropdown menu
     */
    toggleDropdown() {
        if (this.isLoading) return;
        
        const isHidden = this.languageMenu.classList.contains('hidden');
        
        if (isHidden) {
            // Position the menu
            this.languageMenu.style.top = `${this.languageButton.offsetHeight + 8}px`;
            this.languageMenu.style.left = '0';
            
            this.languageMenu.classList.remove('hidden');
            
            // Rotate arrow
            const arrow = this.languageButton.querySelector('svg:last-child');
            arrow.style.transform = 'rotate(180deg)';
        } else {
            this.closeDropdown();
        }
    }
    
    /**
     * Close dropdown menu
     */
    closeDropdown() {
        this.languageMenu.classList.add('hidden');
        const arrow = this.languageButton.querySelector('svg:last-child');
        arrow.style.transform = 'rotate(0deg)';
    }
    
    /**
     * Bind events
     */
    bindEvents() {
        // Language dropdown toggle
        this.languageButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleDropdown();
        });
        
        // Language selection
        const options = this.languageMenu.querySelectorAll('.language-option');
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const langCode = option.dataset.lang;
                this.updateSelectedLanguage(langCode);
                this.closeDropdown();
            });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.languageDropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
    }
    
    /**
     * Get CSRF token from form field
     */
    getCsrfToken() {
        // Try to get token from form field first
        if (this.csrfInput && this.csrfInput.value) {
            const token = this.csrfInput.value;
            // Django CSRF tokens are typically 64 characters (32 bytes in hex)
            // or 64 characters for cookie-based tokens
            if (token.length === 64 || token.length === 32) {
                return token;
            }
        }
        
        // Fallback to cookie method
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    /**
     * Set loading state
     */
    setLoading(loading) {
        this.isLoading = loading;
        
        if (loading) {
            // Save original button text
            this.originalButtonText = this.submitButton.innerHTML;
            
            // Update button with spinner and text
            this.submitButton.innerHTML = `
                <span class="flex items-center gap-2">
                    <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>${gettext('Subscribing...')}</span>
                </span>
            `;
            this.submitButton.disabled = true;
            
            // Disable inputs
            this.emailInput.disabled = true;
            this.languageButton.disabled = true;
            this.languageButton.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            // Restore button
            this.submitButton.innerHTML = this.originalButtonText;
            this.submitButton.disabled = false;
            
            // Enable inputs
            this.emailInput.disabled = false;
            this.languageButton.disabled = false;
            this.languageButton.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }
    
    /**
     * Show toast notification
     * @private
     */
    showToast(message, type = 'danger', duration = 4000) {
        if (window.toastManager) {
            window.toastManager.buildToast()
                .setMessage(message)
                .setType(type)
                .setPosition('top-right')
                .setDuration(duration)
                .show();
        } else {
            // Fallback to console if toast manager is not available
            console.warn('ToastManager not available. Message:', message);
            alert(message); // Simple fallback for user notification
        }
    }
    
    /**
     * Handle form submission
     */
    async handleSubmit() {
        if (this.isLoading) return;
        
        // Basic validation
        const email = this.emailInput.value.trim();
        if (!email) {
            this.showToast(gettext('Please enter your email address'));
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showToast(gettext('Please enter a valid email address'));
            return;
        }
        
        this.setLoading(true);
        
        // Prepare form data
        const formData = new FormData();
        formData.append('email', email);
        formData.append('language', this.selectedLanguage.code);
        
        try {
            const response = await fetch(this.subscribeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData,
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(data.message, 'success', 5000);
                this.form.reset();
                this.updateSelectedLanguage('fr');
            } else {
                this.showToast(data.message || gettext('Please correct the errors below.'), 'danger', 5000);
            }
        } catch (error) {
            console.error('Subscription error:', error);
            this.showToast(gettext('An error occurred. Please try again later.'));
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Validate email format
     */
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NewsletterSubscriptionManager;
}
