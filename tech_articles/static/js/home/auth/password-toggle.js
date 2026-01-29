/**
 * Password Toggle Visibility Script
 * Automatically adds toggle visibility icons to password fields
 *
 * @description This script finds all password input fields on the page
 * and adds eye/eye-off icons to toggle password visibility.
 */

(function () {
  'use strict';

  // SVG Icons
  const ICONS = {
    eye: `<svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-width="2" d="M21 12c0 1.2-4.03 6-9 6s-9-4.8-9-6c0-1.2 4.03-6 9-6s9 4.8 9 6Z"/>
      <path stroke="currentColor" stroke-width="2" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
    </svg>`,
    eyeOff: `<svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.933 13.909A4.357 4.357 0 0 1 3 12c0-1 4-6 9-6m7.6 3.8A5.068 5.068 0 0 1 21 12c0 1-3 6-9 6-.314 0-.62-.014-.918-.04M5 19 19 5m-4 7a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
    </svg>`
  };

  /**
   * Initialize password toggle functionality
   */
  function init() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');

    passwordInputs.forEach(function (input) {
      // Skip if already processed
      if (input.dataset.passwordToggleInitialized) {
        return;
      }

      setupPasswordToggle(input);
      input.dataset.passwordToggleInitialized = 'true';
    });
  }

  /**
   * Setup toggle button for a password input
   * @param {HTMLInputElement} input - The password input element
   */
  function setupPasswordToggle(input) {
    // Create wrapper container if the input is not already wrapped
    const parent = input.parentElement;
    let wrapper;

    if (parent.classList.contains('password-input-wrapper')) {
      wrapper = parent;
    } else {
      wrapper = document.createElement('div');
      wrapper.className = 'password-input-wrapper';
      parent.insertBefore(wrapper, input);
      wrapper.appendChild(input);
    }

    // Create toggle button
    const toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = 'password-toggle-btn peer-focus:text-primary';
    toggleButton.setAttribute('aria-label', gettext('Toggle password visibility'));
    toggleButton.innerHTML = ICONS.eye;

    // Insert toggle button after input
    wrapper.appendChild(toggleButton);

    // Add event listeners
    toggleButton.addEventListener('click', function () {
      togglePasswordVisibility(input, toggleButton);
    });

    // Add focus/blur listeners to apply primary border when toggle button is focused
    toggleButton.addEventListener('focus', function () {
      input.classList.add('!border-primary');
    });

    toggleButton.addEventListener('blur', function () {
      input.classList.remove('!border-primary');
    });
  }

  /**
   * Toggle password visibility
   * @param {HTMLInputElement} input - The password input element
   * @param {HTMLButtonElement} button - The toggle button element
   */
  function togglePasswordVisibility(input, button) {
    const isPassword = input.type === 'password';

    input.type = isPassword ? 'text' : 'password';
    button.innerHTML = isPassword ? ICONS.eyeOff : ICONS.eye;
    button.setAttribute(
      'aria-label',
      isPassword ? gettext('Hide password') : gettext('Show password')
    );
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose init function for dynamic content
  window.initPasswordToggle = init;
})();
