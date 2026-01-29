/**
 * OTP Input Handler
 * Manages 6-digit OTP input fields with auto-focus and validation
 */

(function () {
  'use strict';

  /**
   * Initialize OTP input functionality
   */
  function init() {
    const otpForm = document.getElementById('otp-form');
    if (!otpForm) return;

    const hiddenCodeInput = otpForm.querySelector('[data-otp-hidden]');
    const submitButton = document.getElementById('submit-otp-button');
    const otpInputs = otpForm.querySelectorAll('[data-otp-input]');

    if (!hiddenCodeInput || !submitButton || otpInputs.length === 0) return;

    // Store initial value
    hiddenCodeInput.setAttribute('data-initial-value', hiddenCodeInput.value);

    // Show submit button if hidden code input has a value
    if (hiddenCodeInput.value) {
      submitButton.classList.remove('hidden');
    }

    // Prefill inputs on page load
    prefillInputs(otpInputs, hiddenCodeInput);

    // Add event listeners
    setupEventListeners(otpInputs, hiddenCodeInput, submitButton, otpForm);
  }

  /**
   * Prefill input fields from hidden code value
   * @param {NodeList} inputs - OTP input elements
   * @param {HTMLInputElement} hiddenInput - Hidden code input
   */
  function prefillInputs(inputs, hiddenInput) {
    const codeValue = hiddenInput.value || '';

    codeValue.split('').forEach((char, index) => {
      if (inputs[index]) {
        inputs[index].value = char;
      }
    });

    updateCodeAndButton(inputs, hiddenInput, document.getElementById('submit-otp-button'));
  }

  /**
   * Setup event listeners for OTP inputs
   * @param {NodeList} inputs - OTP input elements
   * @param {HTMLInputElement} hiddenInput - Hidden code input
   * @param {HTMLButtonElement} submitButton - Submit button element
   * @param {HTMLFormElement} form - Form element
   */
  function setupEventListeners(inputs, hiddenInput, submitButton, form) {
    inputs.forEach(function (input, index) {
      // Keydown event for backspace navigation
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !this.value && index > 0) {
          inputs[index - 1].focus();
        }
      });

      // Input event for value changes
      input.addEventListener('input', function () {
        // Ensure only digits are allowed
        this.value = this.value.replace(/\D/g, '').slice(0, 1);

        // Move to next input if value is entered
        if (this.value && index < inputs.length - 1) {
          inputs[index + 1].focus();
        }

        updateCodeAndButton(inputs, hiddenInput, submitButton, form);
      });

      // Paste event handler
      input.addEventListener('paste', function (event) {
        event.preventDefault();
        const pasteData = (event.clipboardData || window.clipboardData).getData('text');
        const digits = pasteData.replace(/\D/g, '').slice(0, 6);

        inputs.forEach((inp, idx) => {
          if (digits[idx]) {
            inp.value = digits[idx];
          }
        });

        // Focus on the last filled input or the last input
        const lastFilledIndex = Math.min(digits.length - 1, inputs.length - 1);
        inputs[lastFilledIndex].focus();

        updateCodeAndButton(inputs, hiddenInput, submitButton, form);
      });

      // Focus event to select content
      input.addEventListener('focus', function () {
        this.select();
      });
    });

    // Submit button click event
    submitButton.addEventListener('click', function () {
      if (!submitButton.disabled) {
        submitForm(inputs, form);
      }
    });
  }

  /**
   * Update hidden code input and submit button state
   * @param {NodeList} inputs - OTP input elements
   * @param {HTMLInputElement} hiddenInput - Hidden code input
   * @param {HTMLButtonElement} submitButton - Submit button element
   * @param {HTMLFormElement} form - Form element (optional)
   */
  function updateCodeAndButton(inputs, hiddenInput, submitButton, form) {
    // Combine all input values
    const code = Array.from(inputs).map(input => input.value).join('');

    // Update hidden input
    hiddenInput.value = code;

    // Enable/disable submit button based on all inputs being filled
    const isCodeValid = code.length === 6 && /^\d{6}$/.test(code);
    submitButton.disabled = !isCodeValid;

    // Auto-submit if code wasn't initially present and all fields are now filled
    const initialCodeEmpty = !hiddenInput.getAttribute('data-initial-value');
    if (form && initialCodeEmpty && isCodeValid) {
      submitForm(inputs, form);
    }
  }

  /**
   * Disable all OTP input fields
   * @param {NodeList} inputs - OTP input elements
   */
  function disableInputs(inputs) {
    inputs.forEach(input => {
      input.classList.add('opacity-50', 'cursor-not-allowed');
      input.disabled = true;
    });
  }

  /**
   * Submit the form
   * @param {NodeList} inputs - OTP input elements
   * @param {HTMLFormElement} form - Form element
   */
  function submitForm(inputs, form) {
    disableInputs(inputs);
    form.submit();
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose init function for dynamic content
  window.initOTPInput = init;
})();
