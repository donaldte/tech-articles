/* eslint-disable max-lines */
/**
 * Navbar behavior with mobile offcanvas sidebar
 *
 * Features:
 * - Transparent navbar by default
 * - Adds background color when user scrolls past the navbar height
 * - Mobile offcanvas sidebar with smooth slide-in/slide-out animations
 * - Accessibility support (ARIA attributes)
 * - Close offcanvas on outside click, backdrop click, or Escape key
 * - Body scroll lock when offcanvas is open
 *
 * @author djoukevin1469@gmail.com
 * @version 2.0.0
 */

(function () {
  'use strict';

  // ===================================
  // i18n Messages
  // ===================================
  const i18n = {
    openMenu: document.documentElement.lang === 'fr' ? 'Ouvrir le menu' : 'Open menu',
    closeMenu: document.documentElement.lang === 'fr' ? 'Fermer le menu' : 'Close menu'
  };

  // ===================================
  // Configuration
  // ===================================
  const CONFIG = {
    navbarId: 'site-navbar',
    mobileToggleId: 'mobile-menu-toggle',
    mobileMenuId: 'mobile-menu',
    mobileMenuPanelId: 'mobile-menu-panel',
    mobileMenuBackdropId: 'mobile-menu-backdrop',
    mobileMenuCloseId: 'mobile-menu-close',
    menuIconOpenId: 'menu-icon-open',
    menuIconCloseId: 'menu-icon-close',
    scrolledClass: 'navbar-scrolled',
    hiddenClass: 'hidden',
    // Threshold in pixels - navbar becomes opaque when scrolled past this point
    scrollThreshold: 50
  };

  // ===================================
  // DOM Elements
  // ===================================
  const navbar = document.getElementById(CONFIG.navbarId);
  const mobileToggle = document.getElementById(CONFIG.mobileToggleId);
  const mobileMenu = document.getElementById(CONFIG.mobileMenuId);
  const mobileMenuPanel = document.getElementById(CONFIG.mobileMenuPanelId);
  const mobileMenuBackdrop = document.getElementById(CONFIG.mobileMenuBackdropId);
  const mobileMenuClose = document.getElementById(CONFIG.mobileMenuCloseId);
  const menuIconOpen = document.getElementById(CONFIG.menuIconOpenId);
  const menuIconClose = document.getElementById(CONFIG.menuIconCloseId);

  // Exit early if navbar doesn't exist
  if (!navbar) {
    console.warn('Navbar element not found');
    return;
  }

  // ===================================
  // State
  // ===================================
  let isOffcanvasOpen = false;
  let lockedScrollY = 0;

  // ===================================
  // Scroll Lock Functions
  // ===================================
  function lockBodyScroll() {
    lockedScrollY = window.scrollY || window.pageYOffset || 0;
    document.body.style.position = 'fixed';
    document.body.style.top = `-${lockedScrollY}px`;
    document.body.style.left = '0';
    document.body.style.right = '0';
    document.body.style.width = '100%';
    document.documentElement.style.overflow = 'hidden';
  }

  function unlockBodyScroll() {
    const htmlElement = document.documentElement;
    const originalScrollBehavior = htmlElement.style.scrollBehavior;
    htmlElement.style.scrollBehavior = 'auto';

    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.left = '';
    document.body.style.right = '';
    document.body.style.width = '';
    document.documentElement.style.overflow = '';

    window.scrollTo(0, lockedScrollY || 0);

    setTimeout(() => {
      htmlElement.style.scrollBehavior = originalScrollBehavior;
    }, 0);
  }

  // ===================================
  // Navbar Scroll Handler
  // ===================================
  function handleScroll() {
    const scrollPosition = window.scrollY;
    if (scrollPosition > CONFIG.scrollThreshold) {
      navbar.classList.add(CONFIG.scrolledClass);
    } else {
      if (!isOffcanvasOpen) {
        navbar.classList.remove(CONFIG.scrolledClass);
      }
    }
  }

  // ===================================
  // Offcanvas Functions
  // ===================================
  function openOffcanvas() {
    if (!mobileMenu || !mobileMenuPanel || !mobileMenuBackdrop) {
      console.debug('[navbar] openOffcanvas: missing elements');
      return;
    }

    // Close all dropdowns (language, profile) before opening offcanvas
    document.dispatchEvent(new CustomEvent('dropdown:open', { detail: { id: 'mobile-offcanvas' } }));

    console.debug('[navbar] openOffcanvas');
    isOffcanvasOpen = true;

    // Enable pointer events on container
    mobileMenu.classList.remove('opacity-0');
    mobileMenu.classList.add('pointer-events-auto');
    mobileMenu.setAttribute('aria-hidden', 'false');

    // Show backdrop with fade-in
    mobileMenuBackdrop.classList.remove('opacity-0');
    mobileMenuBackdrop.classList.add('opacity-100');

    // Slide in panel
    mobileMenuPanel.classList.remove('translate-x-full');
    mobileMenuPanel.classList.add('translate-x-0');

    // Update toggle button
    if (mobileToggle) {
      mobileToggle.setAttribute('aria-expanded', 'true');
      mobileToggle.setAttribute('aria-label', i18n.closeMenu);
    }

    // Toggle icons
    if (menuIconOpen) menuIconOpen.classList.add(CONFIG.hiddenClass);
    if (menuIconClose) menuIconClose.classList.remove(CONFIG.hiddenClass);

    // Force navbar background
    navbar.classList.add(CONFIG.scrolledClass);

    // Lock body scroll
    lockBodyScroll();
  }

  function closeOffcanvas() {
    if (!mobileMenu || !mobileMenuPanel || !mobileMenuBackdrop) {
      console.debug('[navbar] closeOffcanvas: missing elements');
      return;
    }

    console.debug('[navbar] closeOffcanvas');
    isOffcanvasOpen = false;

    // Slide out panel
    mobileMenuPanel.classList.remove('translate-x-0');
    mobileMenuPanel.classList.add('translate-x-full');

    // Fade out backdrop
    mobileMenuBackdrop.classList.remove('opacity-100');
    mobileMenuBackdrop.classList.add('opacity-0');

    // Disable pointer events on container after animation
    setTimeout(() => {
      mobileMenu.classList.add('opacity-0');
      mobileMenu.classList.remove('pointer-events-auto');
      mobileMenu.setAttribute('aria-hidden', 'true');
    }, 300);

    // Update toggle button
    if (mobileToggle) {
      mobileToggle.setAttribute('aria-expanded', 'false');
      mobileToggle.setAttribute('aria-label', i18n.openMenu);
    }

    // Toggle icons
    if (menuIconOpen) menuIconOpen.classList.remove(CONFIG.hiddenClass);
    if (menuIconClose) menuIconClose.classList.add(CONFIG.hiddenClass);

    // Restore navbar background based on scroll position
    const scrollPosition = window.scrollY;
    if (scrollPosition <= CONFIG.scrollThreshold) {
      navbar.classList.remove(CONFIG.scrolledClass);
    }

    // Unlock body scroll
    unlockBodyScroll();
  }

  function toggleOffcanvas() {
    console.debug('[navbar] toggleOffcanvas isOffcanvasOpen=', isOffcanvasOpen);
    if (isOffcanvasOpen) {
      closeOffcanvas();
    } else {
      openOffcanvas();
    }
  }

  // ===================================
  // Event Listeners
  // ===================================

  // Scroll event
  window.addEventListener('scroll', handleScroll, { passive: true });

  // Toggle button
  if (mobileToggle) {
    mobileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleOffcanvas();
    });
  }

  // Close button in offcanvas
  if (mobileMenuClose) {
    mobileMenuClose.addEventListener('click', (e) => {
      e.stopPropagation();
      closeOffcanvas();
    });
  }

  // Backdrop click
  if (mobileMenuBackdrop) {
    mobileMenuBackdrop.addEventListener('click', closeOffcanvas);
  }

  // Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOffcanvasOpen) {
      closeOffcanvas();
    }
  });

  // Close on link click
  if (mobileMenuPanel) {
    const menuLinks = mobileMenuPanel.querySelectorAll('a');
    menuLinks.forEach((link) => {
      link.addEventListener('click', () => {
        setTimeout(closeOffcanvas, 100);
      });
    });
  }

  // Listen for dropdown:open events to close offcanvas
  document.addEventListener('dropdown:open', (e) => {
    if (e.detail && e.detail.id !== 'mobile-offcanvas' && isOffcanvasOpen) {
      try {
        closeOffcanvas();
      } catch (err) {
        console.debug('[navbar] dropdown:open handler error', err);
      }
    }
  }, true);

  // Close offcanvas when language selector is used
  document.addEventListener('language-selector:toggle', (ev) => {
    try {
      const opening = ev && ev.detail && ev.detail.opening;
      if (opening && isOffcanvasOpen) {
        closeOffcanvas();
      }
    } catch (err) {
      console.debug('[navbar] language-selector:toggle handler error', err);
    }
  }, true);

  document.addEventListener('language-selector:select', () => {
    if (isOffcanvasOpen) closeOffcanvas();
  }, true);

  // Close on window resize to desktop
  window.addEventListener('resize', () => {
    if (window.innerWidth >= 1030 && isOffcanvasOpen) {
      closeOffcanvas();
    }
  });

  // Initialize scroll handling
  handleScroll();

})();
