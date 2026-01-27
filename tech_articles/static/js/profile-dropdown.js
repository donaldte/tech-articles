/**
 * Profile Dropdown Menu - Runbookly
 *
 * Features:
 * - Click to toggle dropdown
 * - Closes other dropdowns when opened (language selector)
 * - Keyboard accessible: ESC to close
 * - Auto-closes on outside click
 *
 * @author djoukevin1469@gmail.com
 * @version 1.0.0
 */

(function () {
  'use strict';

  const toggle = document.getElementById('profile-toggle');
  const menu = document.getElementById('profile-menu');

  // Exit if user is not authenticated (elements won't exist)
  if (!toggle || !menu) {
    return;
  }

  let isOpen = false;
  let closeTimeout;

  /**
   * Update menu position relative to toggle button
   */
  function updateMenuPosition() {
    const rect = toggle.getBoundingClientRect();
    const menuWidth = menu.offsetWidth || 288;
    const menuHeight = menu.offsetHeight || 0;
    const margin = 8;

    // Position below toggle, right-aligned
    let left = rect.right - menuWidth;
    if (left < margin) left = margin;
    if (left + menuWidth > window.innerWidth - margin) {
      left = Math.max(margin, window.innerWidth - menuWidth - margin);
    }

    let top = rect.bottom + 8;
    // If menu would overflow bottom, position above toggle
    if (top + menuHeight > window.innerHeight - margin) {
      top = Math.max(margin, rect.top - menuHeight - 8);
    }

    menu.style.left = left + 'px';
    menu.style.top = top + 'px';
  }

  /**
   * Close other dropdowns (language selector)
   */
  function closeOtherDropdowns() {
    // Close language dropdown if open
    const langMenu = document.getElementById('language-menu');
    const langToggle = document.getElementById('language-toggle');

    if (langMenu && !langMenu.classList.contains('invisible')) {
      langMenu.classList.remove('opacity-100', 'visible');
      langMenu.classList.add('opacity-0', 'invisible');
      langMenu.style.pointerEvents = 'none';
      setTimeout(() => {
        langMenu.style.display = 'none';
      }, 200);
      if (langToggle) {
        langToggle.setAttribute('aria-expanded', 'false');
      }
    }

    // Close mobile menu if open
    try {
      document.dispatchEvent(new CustomEvent('close-mobile-menu'));
    } catch (err) {
      // Ignore errors
    }
  }

  /**
   * Open the profile menu
   */
  function openMenu() {
    if (isOpen) return;

    // Clear any pending close
    if (closeTimeout) clearTimeout(closeTimeout);

    // Close other dropdowns first
    closeOtherDropdowns();

    // Show and position
    menu.style.display = 'block';
    menu.style.pointerEvents = 'auto';
    updateMenuPosition();

    // Add visible classes with slight delay for animation
    requestAnimationFrame(() => {
      menu.classList.remove('opacity-0', 'invisible');
      menu.classList.add('opacity-100', 'visible');
    });

    toggle.setAttribute('aria-expanded', 'true');
    isOpen = true;

    // Dispatch event for other components
    try {
      document.dispatchEvent(new CustomEvent('profile-menu:open'));
    } catch (err) {
      // Ignore errors
    }
  }

  /**
   * Close the profile menu
   */
  function closeMenu() {
    if (!isOpen) return;

    // Clear pending close
    if (closeTimeout) clearTimeout(closeTimeout);

    menu.classList.remove('opacity-100', 'visible');
    menu.classList.add('opacity-0', 'invisible');
    menu.style.pointerEvents = 'none';

    // Hide element after transition
    closeTimeout = setTimeout(() => {
      if (!isOpen) menu.style.display = 'none';
    }, 200);

    toggle.setAttribute('aria-expanded', 'false');
    isOpen = false;

    // Dispatch event for other components
    try {
      document.dispatchEvent(new CustomEvent('profile-menu:close'));
    } catch (err) {
      // Ignore errors
    }
  }

  /**
   * Toggle the profile menu
   */
  function toggleMenu(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (isOpen) {
      closeMenu();
    } else {
      openMenu();
    }
  }

  /**
   * Handle clicks outside the menu
   */
  function handleOutsideClick(e) {
    if (!isOpen) return;
    const isClickOnToggle = toggle.contains(e.target);
    const isClickOnMenu = menu.contains(e.target);
    if (!isClickOnToggle && !isClickOnMenu) {
      closeMenu();
    }
  }

  // Event listeners
  toggle.addEventListener('click', toggleMenu);
  document.addEventListener('click', handleOutsideClick);
  document.addEventListener('touchstart', handleOutsideClick, { passive: true });

  // Keyboard support
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      e.preventDefault();
      closeMenu();
      toggle.focus();
    }
  });

  // Close profile menu when language selector opens
  document.addEventListener('language-selector:toggle', (ev) => {
    try {
      const opening = ev && ev.detail && ev.detail.opening;
      if (opening && isOpen) {
        closeMenu();
      }
    } catch (err) {
      // Ignore errors
    }
  }, true);

  // Reposition on scroll/resize
  window.addEventListener('resize', () => {
    if (isOpen) updateMenuPosition();
  }, { passive: true });

  window.addEventListener('scroll', () => {
    if (isOpen) updateMenuPosition();
  }, { passive: true });

  // Initial ARIA state
  toggle.setAttribute('aria-haspopup', 'true');
  toggle.setAttribute('aria-expanded', 'false');
  menu.setAttribute('aria-hidden', 'true');
  menu.style.position = 'absolute';

})();
