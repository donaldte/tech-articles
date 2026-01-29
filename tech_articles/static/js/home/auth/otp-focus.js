/**
 * OTP Focus Manager
 * Manages focus behavior for OTP input fields
 *
 * Features:
 * - Auto-focus on last filled input if form has validation errors
 * - Cursor always at end of input
 * - Click handler to place cursor at end
 * - Accessibility support
 *
 * @author Runbookly
 * @version 1.0.0
 */

(function () {
  'use strict';

  /**
   * Initialize OTP focus management
   * Sets up click handlers for cursor positioning
   */
  function init() {
    const otpForm = document.getElementById('otp-form');
    if (!otpForm) return;

    // Handle click on OTP inputs to place cursor at end
    const otpInputs = otpForm.querySelectorAll('input[data-otp-input]');
    otpInputs.forEach(input => {
      input.addEventListener('click', function () {
        const length = this.value.length;
        this.setSelectionRange(length, length);
      });
    });
  }

  /**
   * Focus on the appropriate OTP input field
   * Focuses on the last filled input, or first empty input if none are filled
   * Called after inputs are prefilled
   */
  function focusLastOTPInput() {
    const otpForm = document.getElementById('otp-form');
    if (!otpForm) return;

    // Get all inputs in order
    const allInputs = otpForm.querySelectorAll('input[data-otp-input]');
    if (allInputs.length === 0) return;

    // Convert to array for reliable indexing
    const otpInputs = Array.from(allInputs).slice(0, 6);

    // Find last filled input
    let lastFilledIndex = -1;
    for (let i = 0; i < otpInputs.length; i++) {
      if (otpInputs[i].value.trim() !== '') {
        lastFilledIndex = i;
      }
    }

    // Determine which input to focus
    let targetInput;
    if (lastFilledIndex >= 0 && lastFilledIndex < otpInputs.length - 1) {
      // Focus on input after last filled
      targetInput = otpInputs[lastFilledIndex + 1];
    } else if (lastFilledIndex === otpInputs.length - 1) {
      // All filled, focus on last
      targetInput = otpInputs[lastFilledIndex];
    } else {
      // None filled, focus on first
      targetInput = otpInputs[0];
    }

    // Focus and place cursor at end
    setTimeout(function () {
      targetInput.focus();
      const length = targetInput.value.length;
      targetInput.setSelectionRange(length, length);
    }, 50);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose functions for dynamic content and otp-input.js
  window.initOTPFocus = init;
  window.focusLastOTPInput = focusLastOTPInput;
})();
