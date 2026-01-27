/**
 * Language Selector Dropdown - Click Only
 *
 * Features:
 * - Click to toggle dropdown (no hover)
 * - Fixed position relative to viewport
 * - No slide animation
 * - Active state on toggle button (text-primary when open)
 * - Closes mobile menu and other dropdowns when opened
 *
 * @author Runbookly
 * @version 3.1.0
 */

(function () {
  'use strict';

  const toggle = document.getElementById('language-toggle');
  const menu = document.getElementById('language-menu');

  if (!toggle || !menu) {
    return;
  }

  let isOpen = false;

  /**
   * Update menu position (calculate before showing)
   */
  function updateMenuPosition() {
    const rect = toggle.getBoundingClientRect();
    const menuWidth = 192;
    const margin = 8;

    let left = rect.right - menuWidth;
    if (left < margin) left = margin;
    if (left + menuWidth > window.innerWidth - margin) {
      left = Math.max(margin, window.innerWidth - menuWidth - margin);
    }

    let top = rect.bottom + 8;

    menu.style.left = left + 'px';
    menu.style.top = top + 'px';
  }

  /**
   * Open the menu
   */
  function openMenu() {
    if (isOpen) return;

    // Close mobile menu
    document.dispatchEvent(new CustomEvent('dropdown:open', { detail: { id: 'language-menu' } }));

    // Position BEFORE making visible (prevents slide animation)
    updateMenuPosition();

    // Show menu
    menu.style.display = 'block';
    requestAnimationFrame(() => {
      menu.style.opacity = '1';
      menu.classList.remove('opacity-0', 'invisible');
      menu.classList.add('opacity-100', 'visible');
    });

    // Active state on toggle - add text-primary class
    toggle.classList.add('text-primary');
    toggle.classList.remove('text-white');
    toggle.setAttribute('aria-expanded', 'true');
    isOpen = true;
  }

  /**
   * Close the menu
   */
  function closeMenu() {
    if (!isOpen) return;

    menu.style.opacity = '0';
    menu.classList.remove('opacity-100', 'visible');
    menu.classList.add('opacity-0', 'invisible');

    setTimeout(() => {
      if (!isOpen) {
        menu.style.display = 'none';
      }
    }, 150);

    // Remove active state - restore text-white
    toggle.classList.remove('text-primary');
    toggle.classList.add('text-white');
    toggle.setAttribute('aria-expanded', 'false');
    isOpen = false;
  }

  /**
   * Toggle the menu
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
   * Handle outside clicks
   */
  function handleOutsideClick(e) {
    if (!isOpen) return;
    if (!toggle.contains(e.target) && !menu.contains(e.target)) {
      closeMenu();
    }
  }

  // Click only (no hover)
  toggle.addEventListener('click', toggleMenu);

  // Outside click
  document.addEventListener('click', handleOutsideClick);
  document.addEventListener('touchstart', handleOutsideClick, { passive: true });

  // ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      e.preventDefault();
      closeMenu();
      toggle.focus();
    }
  });

  // Close when other dropdowns or mobile menu open
  document.addEventListener('dropdown:open', (e) => {
    if (e.detail && e.detail.id !== 'language-menu' && isOpen) {
      closeMenu();
    }
  });

  // Initial setup
  toggle.setAttribute('aria-haspopup', 'true');
  toggle.setAttribute('aria-expanded', 'false');
  menu.style.position = 'fixed';
  menu.style.display = 'none';
  menu.style.transition = 'opacity 150ms ease';

})();
