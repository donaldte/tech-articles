/**
 * Navbar behavior for Runbookly
 *
 * Features:
 * - Transparent navbar by default
 * - Adds background color when user scrolls past the navbar height
 * - Mobile menu toggle with smooth animations
 * - Accessibility support (ARIA attributes)
 * - Close mobile menu on outside click or Escape key
 *
 * @author Runbookly Team
 * @version 1.0.0
 */

(function () {
  'use strict';

  // ===================================
  // Configuration
  // ===================================
  const CONFIG = {
    navbarId: 'site-navbar',
    mobileToggleId: 'mobile-menu-toggle',
    mobileMenuId: 'mobile-menu',
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
  let isMobileMenuOpen = false;

  // ===================================
  // Scroll Handler - Toggle background on scroll
  // ===================================
  function handleScroll() {
    const scrollPosition = window.scrollY;

    if (scrollPosition > CONFIG.scrollThreshold) {
      navbar.classList.add(CONFIG.scrolledClass);
    } else {
      navbar.classList.remove(CONFIG.scrolledClass);
    }
  }

  // ===================================
  // Mobile Menu Functions
  // ===================================
  function openMobileMenu() {
    if (!mobileMenu || !mobileToggle) return;

    isMobileMenuOpen = true;
    mobileMenu.classList.remove(CONFIG.hiddenClass);
    mobileToggle.setAttribute('aria-expanded', 'true');

    // Toggle icons
    if (menuIconOpen) menuIconOpen.classList.add(CONFIG.hiddenClass);
    if (menuIconClose) menuIconClose.classList.remove(CONFIG.hiddenClass);

    // Prevent body scroll when menu is open
    document.body.style.overflow = 'hidden';
  }

  function closeMobileMenu() {
    if (!mobileMenu || !mobileToggle) return;

    isMobileMenuOpen = false;
    mobileMenu.classList.add(CONFIG.hiddenClass);
    mobileToggle.setAttribute('aria-expanded', 'false');

    // Toggle icons
    if (menuIconOpen) menuIconOpen.classList.remove(CONFIG.hiddenClass);
    if (menuIconClose) menuIconClose.classList.add(CONFIG.hiddenClass);

    // Restore body scroll
    document.body.style.overflow = '';
  }

  function toggleMobileMenu() {
    if (isMobileMenuOpen) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  }

  // ===================================
  // Event Listeners
  // ===================================

  // Scroll event - update navbar background
  window.addEventListener('scroll', handleScroll, { passive: true });

  // Mobile menu toggle button
  if (mobileToggle) {
    mobileToggle.addEventListener('click', function (event) {
      event.stopPropagation();
      toggleMobileMenu();
    });
  }

  // Close mobile menu on Escape key
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && isMobileMenuOpen) {
      closeMobileMenu();
    }
  });

  // Close mobile menu when clicking outside
  document.addEventListener('click', function (event) {
    if (!isMobileMenuOpen) return;

    const target = event.target;
    const isClickInsideMenu = mobileMenu && mobileMenu.contains(target);
    const isClickOnToggle = mobileToggle && mobileToggle.contains(target);

    if (!isClickInsideMenu && !isClickOnToggle) {
      closeMobileMenu();
    }
  });

  // Close mobile menu when clicking on a link (smooth navigation)
  if (mobileMenu) {
    const menuLinks = mobileMenu.querySelectorAll('a');
    menuLinks.forEach(function (link) {
      link.addEventListener('click', function () {
        // Small delay to allow navigation to start
        setTimeout(closeMobileMenu, 100);
      });
    });
  }

  // Handle window resize - close mobile menu on larger screens
  window.addEventListener('resize', function () {
    if (window.innerWidth >= 768 && isMobileMenuOpen) {
      closeMobileMenu();
    }
  });

  // ===================================
  // Initialize
  // ===================================
  // Check scroll position on page load
  handleScroll();

})();
