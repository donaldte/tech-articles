/**
 * OTP Resend Handler
 * Manages OTP resend functionality with fetch API
 *
 * Features:
 * - Sends OTP resend request via fetch
 * - Shows "Sending..." state after 2 seconds
 * - Displays error notifications
 * - Restarts countdown timer on success
 * - Internationalization support
 *
 * @author Runbookly
 * @version 1.0.0
 */

(function () {
  'use strict';

  /**
   * Initialize OTP resend handler
   */
  function init() {
    const resendButton = document.getElementById('resend-otp-btn');
    if (!resendButton) return;

    resendButton.addEventListener('click', handleResendClick);
  }

  /**
   * Handle resend button click
   * @param {Event} event - Click event
   */
  function handleResendClick(event) {
    event.preventDefault();

    const button = this;
    const purpose = button.dataset.purpose;
    const originalText = button.textContent;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (!purpose) {
      console.warn('Resend button missing data-purpose attribute');
      return;
    }

    // Get URL from config
    const resendUrl = window.appConfig?.getUrl('otpResend');
    if (!resendUrl) {
      console.error('OTP resend URL not configured');
      showErrorNotification(gettext('Configuration error. Please try again.'));
      return;
    }

    // Disable button and show initial state
    button.disabled = true;
    button.classList.add('opacity-50', 'cursor-not-allowed');

    // Show "Sending..." after 2 seconds
    const sendingTimeout = setTimeout(function () {
      button.textContent = gettext('Sending...');
    }, 2000);

    // Send request
    fetch(resendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken || ''
      },
      body: 'purpose=' + encodeURIComponent(purpose)
    })
      .then(response => response.json())
      .then(data => {
        clearTimeout(sendingTimeout);

        if (data.success) {
          handleResendSuccess(button);
        } else {
          handleResendError(button, originalText, data.error);
        }
      })
      .catch(error => {
        clearTimeout(sendingTimeout);
        console.error('Resend OTP error:', error);
        handleResendError(button, originalText, gettext('Error sending code. Please try again.'));
      });
  }

  /**
   * Handle successful resend
   * Restarts the countdown timer and reloads the page
   */
  function handleResendSuccess() {
    // Restart countdown timer (60 seconds)
    const timerKey = 'otp_resend_timer';
    const expiryTime = Date.now() + 60000;
    sessionStorage.setItem(timerKey, expiryTime.toString());

    // Reload page to restart timer and reinitialize
    // This ensures the timer displays correctly
    window.location.reload();
  }

  /**
   * Handle resend error
   * Displays error notification and restores button state
   * @param {HTMLButtonElement} button - Resend button
   * @param {string} originalText - Original button text
   * @param {string} errorMessage - Error message to display
   */
  function handleResendError(button, originalText, errorMessage) {
    button.disabled = false;
    button.classList.remove('opacity-50', 'cursor-not-allowed');
    button.textContent = originalText;

    showErrorNotification(errorMessage);
  }

  /**
   * Show error notification
   * Creates and displays a temporary error notification
   * @param {string} message - Error message to display
   */
  function showErrorNotification(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm max-w-md z-50';
    errorDiv.role = 'alert';
    errorDiv.setAttribute('aria-live', 'assertive');
    errorDiv.textContent = message;

    document.body.appendChild(errorDiv);

    // Auto-remove after 5 seconds
    setTimeout(function () {
      if (errorDiv.parentElement) {
        errorDiv.remove();
      }
    }, 5000);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for dynamic content
  window.initOTPResend = init;
})();
