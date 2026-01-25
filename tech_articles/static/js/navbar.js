/* eslint-disable max-lines */
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
 * @author djoukevin1469@gmail.com
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
  let mobileMenu = document.getElementById(CONFIG.mobileMenuId);
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
  let mobileMenuOriginalParent = null;
  let lockedScrollY = 0;
  let rafId = null;

  function ensureMobileMenuAttachedToBody() {
    if (!mobileMenu) return;
    if (mobileMenu.parentElement !== document.body) {
      mobileMenuOriginalParent = mobileMenu.parentElement;
      document.body.appendChild(mobileMenu);
    }
    // force computed fixed positioning
    mobileMenu.style.position = 'fixed';
    mobileMenu.style.left = '0';
    mobileMenu.style.right = '0';
    mobileMenu.style.zIndex = '60';
    mobileMenu.style.willChange = 'top';
  }

  function getNavbarHeight() {
    return navbar.getBoundingClientRect().height || navbar.offsetHeight || 80;
  }

  function updateMobileMenuTop() {
    if (!mobileMenu || !navbar) return;
    const navbarHeight = Math.ceil(getNavbarHeight());
    mobileMenu.style.top = `${navbarHeight}px`;
  }

  // Keep top in sync even while opening using RAF
  function setTopRaf() {
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(() => {
      updateMobileMenuTop();
      rafId = null;
    });
  }

  // Robust scroll lock
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
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.left = '';
    document.body.style.right = '';
    document.body.style.width = '';
    document.documentElement.style.overflow = '';
    window.scrollTo(0, lockedScrollY || 0);
  }

  function handleScroll() {
    const scrollPosition = window.scrollY;
    if (scrollPosition > CONFIG.scrollThreshold) {
      navbar.classList.add(CONFIG.scrolledClass);
    } else {
      navbar.classList.remove(CONFIG.scrolledClass);
    }
    // ensure mobile menu top is still correct when navbar changes on scroll
    if (isMobileMenuOpen) updateMobileMenuTop();
  }

  // ===================================
  // Mobile Menu Functions
  // ===================================
  function openMobileMenu() {
    if (!mobileMenu || !mobileToggle) return;
    ensureMobileMenuAttachedToBody();
    isMobileMenuOpen = true;
    mobileMenu.classList.remove(CONFIG.hiddenClass);
    mobileToggle.setAttribute('aria-expanded', 'true');

    // Toggle icons
    if (menuIconOpen) menuIconOpen.classList.add(CONFIG.hiddenClass);
    if (menuIconClose) menuIconClose.classList.remove(CONFIG.hiddenClass);
    // sync top using RAF
    setTopRaf();
    // lock scroll
    lockBodyScroll();
  }

  function closeMobileMenu() {
    if (!mobileMenu || !mobileToggle) return;
    isMobileMenuOpen = false;
    mobileMenu.classList.add(CONFIG.hiddenClass);
    mobileToggle.setAttribute('aria-expanded', 'false');

    // Toggle icons
    if (menuIconOpen) menuIconOpen.classList.remove(CONFIG.hiddenClass);
    if (menuIconClose) menuIconClose.classList.add(CONFIG.hiddenClass);
    unlockBodyScroll();
  }

  function toggleMobileMenu() {
    if (isMobileMenuOpen) closeMobileMenu(); else openMobileMenu();
  }

  // Observe navbar size changes (ResizeObserver) and update mobile menu top
  if (typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(() => {
      updateMobileMenuTop();
    });
    try { ro.observe(navbar); } catch (e) { /* ignore */ }
  } else {
    // fallback to window resize
    window.addEventListener('resize', updateMobileMenuTop, { passive: true });
  }

  // Attach to body at init to avoid fixed containment issues
  ensureMobileMenuAttachedToBody();
  updateMobileMenuTop();

  // Scroll event - update navbar background
  window.addEventListener('scroll', handleScroll, { passive: true });

  if (mobileToggle) mobileToggle.addEventListener('click', (e) => { e.stopPropagation(); toggleMobileMenu(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && isMobileMenuOpen) closeMobileMenu(); });
  document.addEventListener('click', (e) => {
    if (!isMobileMenuOpen) return;
    const target = e.target;
    const isClickInsideMenu = mobileMenu && mobileMenu.contains(target);
    const isClickOnToggle = mobileToggle && mobileToggle.contains(target);
    if (!isClickInsideMenu && !isClickOnToggle) closeMobileMenu();
  });

  // Close mobile menu when clicking on a link (smooth navigation)
  if (mobileMenu) {
    const menuLinks = mobileMenu.querySelectorAll('a');
    menuLinks.forEach((link) => link.addEventListener('click', () => setTimeout(closeMobileMenu, 100)));
  }

  window.addEventListener('resize', () => {
    updateMobileMenuTop();
    if (window.innerWidth >= 768 && isMobileMenuOpen) closeMobileMenu();
  });

  // init scroll handling
  handleScroll();

})();
