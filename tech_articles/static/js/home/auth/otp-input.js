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
    prefillInputs(otpInputs, hiddenCodeInput, submitButton, otpForm);

    // Add event listeners
    setupEventListeners(otpInputs, hiddenCodeInput, submitButton, otpForm);
  }

  /**
   * Prefill input fields from hidden code value
   * @param {NodeList} inputs - OTP input elements
   * @param {HTMLInputElement} hiddenInput - Hidden code input
   * @param {HTMLInputElement} submitButton - Submit button element
   * @param {HTMLInputElement} form - OTP form element
   */
  function prefillInputs(inputs, hiddenInput, submitButton, form) {
    const codeValue = hiddenInput.value || '';

    codeValue.split('').forEach((char, index) => {
      if (inputs[index]) {
        inputs[index].value = char;
      }
    });

    updateCodeAndButton(inputs, hiddenInput, submitButton, form);
  }

  /**
   * Setup event listeners for OTP inputs
   */
  function setupEventListeners(inputs, hiddenInput, submitButton, form) {
    inputs.forEach((input, index) => {
      // Keyup event for navigation
      input.addEventListener('keyup', function (e) {
        handleKeyUp(this, inputs, index, e, hiddenInput, submitButton, form);
      });

      // Input event for all changes
      input.addEventListener('input', function () {
        // Only allow digits
        this.value = this.value.replace(/\D/g, '');
        updateCodeAndButton(inputs, hiddenInput, submitButton, form);
      });

      // Paste event
      input.addEventListener('paste', function (e) {
        handlePaste(e, inputs, hiddenInput, submitButton, form);
      });
    });

    // Submit button click
    submitButton.addEventListener('click', function () {
      if (!submitButton.disabled) {
        disableInputs(inputs);
        form.submit();
      }
    });
  }

  /**
   * Handle keyup events
   */
  function handleKeyUp(element, inputs, index, e, hiddenInput, submitButton, form) {
    const prevInput = index > 0 ? inputs[index - 1] : null;
    const nextInput = index < inputs.length - 1 ? inputs[index + 1] : null;

    if (e.key === 'Backspace') {
      if (element.value === '' && prevInput) {
        prevInput.focus();
      }
    } else if (element.value.length === 1 && nextInput) {
      nextInput.focus();
    }

    updateCodeAndButton(inputs, hiddenInput, submitButton, form);
  }

  /**
   * Handle paste events
   */
  function handlePaste(e, inputs, hiddenInput, submitButton, form) {
    e.preventDefault();
    const pasteData = (e.clipboardData || window.clipboardData).getData('text');
    const digits = pasteData.replace(/\D/g, '');

    inputs.forEach((input, index) => {
      if (digits[index]) {
        input.value = digits[index];
      }
    });

    // Focus on next empty or last input
    const lastFilledIndex = Math.min(digits.length - 1, inputs.length - 1);
    if (inputs[lastFilledIndex + 1]) {
      inputs[lastFilledIndex + 1].focus();
    }

    updateCodeAndButton(inputs, hiddenInput, submitButton, form);
  }

  /**
   * Update hidden code input and button state
   */
  function updateCodeAndButton(inputs, hiddenInput, submitButton, form) {
    const code = Array.from(inputs).map(input => input.value).join('');
    hiddenInput.value = code;

    // Enable/disable submit button
    const isValid = code.length === 6 && /^\d{6}$/.test(code);
    submitButton.disabled = !isValid;

    // Auto-submit if initially empty and all filled
    const wasInitiallyEmpty = !hiddenInput.getAttribute('data-initial-value');
    if (wasInitiallyEmpty && isValid) {
      disableInputs(inputs);
      form.submit();
    }
  }

  /**
   * Disable all OTP inputs
   */
  function disableInputs(inputs) {
    inputs.forEach(input => {
      input.disabled = true;
      input.classList.add('opacity-50', 'cursor-not-allowed');
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for dynamic content
  window.initOTPInput = init;
})();
