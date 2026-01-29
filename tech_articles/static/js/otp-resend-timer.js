/**
 * OTP Resend Timer
 * Manages countdown timer for OTP resend functionality
 */

(function () {
  'use strict';

  const CONFIG = {
    countdownDuration: 60, // seconds
    storageKey: 'otp_resend_timer',
  };

  /**
   * Initialize resend timer functionality
   */
  function init() {
    const resendButton = document.getElementById('resend-otp-btn');
    if (!resendButton) return;

    // Check if OTP was just sent from the view
    const otpJustSent = window.otpJustSent === true;

    // Check if there's an active timer in session storage
    let savedTimer = getTimerFromStorage();

    // Only start timer if:
    // 1. OTP was just sent from the view (fresh OTP), OR
    // 2. Timer exists from a previous request
    if (otpJustSent && !savedTimer) {
      // OTP just sent, start fresh timer
      savedTimer = CONFIG.countdownDuration;
      saveTimerToStorage(savedTimer);
      startCountdown(resendButton, savedTimer);
    } else if (savedTimer && savedTimer > 0) {
      // Timer exists from before, continue countdown
      startCountdown(resendButton, savedTimer);
    }
    // Otherwise, button remains enabled (no timer needed)
  }


  /**
   * Start countdown timer
   * @param {HTMLButtonElement} button - Resend button element
   * @param {number} duration - Countdown duration in seconds
   */
  function startCountdown(button, duration) {
    let timeLeft = duration;
    const originalText = button.getAttribute('data-original-text') || button.textContent;

    if (!button.hasAttribute('data-original-text')) {
      button.setAttribute('data-original-text', originalText);
    }

    // Disable button
    button.disabled = true;
    button.classList.add('opacity-80', '!cursor-not-allowed');

    // Update button text immediately
    updateButtonText(button, timeLeft, originalText);

    const interval = setInterval(function () {
      timeLeft--;
      saveTimerToStorage(timeLeft);

      if (timeLeft <= 0) {
        clearInterval(interval);
        resetButton(button, originalText);
        clearTimerFromStorage();
      } else {
        updateButtonText(button, timeLeft, originalText);
      }
    }, 1000);
  }

  /**
   * Update button text with countdown
   * @param {HTMLButtonElement} button - Button element
   * @param {number} seconds - Seconds remaining
   * @param {string} originalText - Original button text
   */
  function updateButtonText(button, seconds, originalText) {
    // Show countdown with format: Resend(Xs)
    button.textContent = `${originalText}(${seconds}s)`;
  }

  /**
   * Reset button to original state
   * @param {HTMLButtonElement} button - Button element
   * @param {string} originalText - Original button text
   */
  function resetButton(button, originalText) {
    button.disabled = false;
    button.classList.remove('opacity-80', '!cursor-not-allowed');
    button.textContent = originalText;
  }

  /**
   * Save timer to session storage
   * @param {number} seconds - Seconds to save
   */
  function saveTimerToStorage(seconds) {
    const expiryTime = Date.now() + (seconds * 1000);
    sessionStorage.setItem(CONFIG.storageKey, expiryTime.toString());
  }

  /**
   * Get timer from session storage
   * @returns {number|null} - Remaining seconds or null
   */
  function getTimerFromStorage() {
    const expiryTime = sessionStorage.getItem(CONFIG.storageKey);
    if (!expiryTime) return null;

    const timeLeft = Math.max(0, Math.floor((parseInt(expiryTime) - Date.now()) / 1000));
    return timeLeft > 0 ? timeLeft : null;
  }

  /**
   * Clear timer from session storage
   */
  function clearTimerFromStorage() {
    sessionStorage.removeItem(CONFIG.storageKey);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose init function for dynamic content
  window.initOTPResendTimer = init;
})();
