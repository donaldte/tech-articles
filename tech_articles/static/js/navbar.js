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
  // Initialize state based on DOM to prevent drift between variable and actual visibility
  let isMobileMenuOpen = mobileMenu ? !mobileMenu.classList.contains(CONFIG.hiddenClass) : false;
  let mobileMenuOriginalParent = null;
  let lockedScrollY = 0;
  let rafId = null;

  function ensureMobileMenuAttachedToBody() {
    const el = getMobileMenu();
    if (!el) return;
    if (el.parentElement !== document.body) {
      mobileMenuOriginalParent = el.parentElement;
      document.body.appendChild(el);
    }
    // update cached reference
    mobileMenu = el;
    // force computed fixed positioning
    el.style.position = 'fixed';
    el.style.left = '0';
    el.style.right = '0';
    el.style.zIndex = '60';
    el.style.willChange = 'top';
  }

  function getNavbarHeight() {
    return navbar.getBoundingClientRect().height || navbar.offsetHeight || 80;
  }

  function updateMobileMenuTop() {
    const el = getMobileMenu();
    if (!el || !navbar) return;
    const navbarHeight = Math.ceil(getNavbarHeight());
    el.style.top = `${navbarHeight}px`;
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
    // Temporarily disable smooth scroll for instant restoration
    const htmlElement = document.documentElement;
    const originalScrollBehavior = htmlElement.style.scrollBehavior;
    htmlElement.style.scrollBehavior = 'auto';

    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.left = '';
    document.body.style.right = '';
    document.body.style.width = '';
    document.documentElement.style.overflow = '';

    // Restore scroll position instantly
    window.scrollTo(0, lockedScrollY || 0);

    // Restore original scroll behavior after restoration
    setTimeout(() => {
      htmlElement.style.scrollBehavior = originalScrollBehavior;
    }, 0);
  }

  function handleScroll() {
    const scrollPosition = window.scrollY;
    if (scrollPosition > CONFIG.scrollThreshold) {
      navbar.classList.add(CONFIG.scrolledClass);
    } else {
      // Don't remove background if mobile menu is open
      if (!isMobileMenuOpen) {
        navbar.classList.remove(CONFIG.scrolledClass);
      }
    }
    // ensure mobile menu top is still correct when navbar changes on scroll
    if (isMobileMenuOpen) updateMobileMenuTop();
  }

  // ===================================
  // Mobile Menu Functions
  // ===================================

  // Helper to get fresh mobileMenu reference (in case DOM changed)
  function getMobileMenu() {
    if (!mobileMenu) {
      mobileMenu = document.getElementById(CONFIG.mobileMenuId);
    }
    return mobileMenu;
  }

  // Central helper that updates DOM state (class, display, aria)
  function setMenuVisibility(open) {
    const el = getMobileMenu();
    if (!el) {
      console.debug('[navbar] setMenuVisibility: mobile menu not found');
      return;
    }
    console.debug('[navbar] setMenuVisibility ->', open);
    if (open) {
      // attach to body in case it moved
      ensureMobileMenuAttachedToBody();
      el.classList.remove(CONFIG.hiddenClass);
      // Force visibility to avoid conflicts with CSS utilities
      el.style.display = 'block';
      el.style.visibility = 'visible';
      el.style.opacity = '1';
      el.style.pointerEvents = 'auto';
      el.setAttribute('aria-hidden', 'false');
      // ensure correct top now
      updateMobileMenuTop();
    } else {
      el.classList.add(CONFIG.hiddenClass);
      // Force hide
      el.style.display = 'none';
      el.style.visibility = 'hidden';
      el.style.opacity = '0';
      el.style.pointerEvents = 'none';
      el.setAttribute('aria-hidden', 'true');
    }
    isMobileMenuOpen = open;
  }

  function openMobileMenu() {
    const el = getMobileMenu();
    if (!el || !mobileToggle) {
      console.debug('[navbar] openMobileMenu: missing elements', { mobileMenu: !!el, mobileToggle: !!mobileToggle });
      return;
    }
    ensureMobileMenuAttachedToBody();

    console.debug('[navbar] openMobileMenu');
    setMenuVisibility(true);
    mobileToggle.setAttribute('aria-expanded', 'true');

    if (menuIconOpen) menuIconOpen.classList.add(CONFIG.hiddenClass);
    if (menuIconClose) menuIconClose.classList.remove(CONFIG.hiddenClass);

    // Force navbar to have background when menu is open (even if not scrolled)
    navbar.classList.add(CONFIG.scrolledClass);

    setTopRaf();
    lockBodyScroll();
  }

  function closeMobileMenu() {
    const el = getMobileMenu();
    if (!el || !mobileToggle) {
      console.debug('[navbar] closeMobileMenu: missing elements', { mobileMenu: !!el, mobileToggle: !!mobileToggle });
      return;
    }
    console.debug('[navbar] closeMobileMenu');
    setMenuVisibility(false);
    mobileToggle.setAttribute('aria-expanded', 'false');

    if (menuIconOpen) menuIconOpen.classList.remove(CONFIG.hiddenClass);
    if (menuIconClose) menuIconClose.classList.add(CONFIG.hiddenClass);

    // Restore navbar background state based on scroll position
    const scrollPosition = window.scrollY;
    if (scrollPosition <= CONFIG.scrollThreshold) {
      navbar.classList.remove(CONFIG.scrolledClass);
    }

    unlockBodyScroll();
  }

  function toggleMobileMenu() {
    console.debug('[navbar] toggleMobileMenu isMobileMenuOpen=', isMobileMenuOpen);

    if (isMobileMenuOpen) {
      // close
      closeMobileMenu();
    } else {
      // open
      openMobileMenu();
    }
  }

  // initialize menu aria state to match DOM
  if (getMobileMenu()) {
    const initialOpen = !getMobileMenu().classList.contains(CONFIG.hiddenClass);
    getMobileMenu().setAttribute('aria-hidden', initialOpen ? 'false' : 'true');
    isMobileMenuOpen = initialOpen;
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
    const el = getMobileMenu();
    const isClickInsideMenu = el && el.contains(target);
    const isClickOnToggle = mobileToggle && mobileToggle.contains(target);
    if (!isClickInsideMenu && !isClickOnToggle) closeMobileMenu();
  });

  // Close mobile menu when clicking on a link (smooth navigation)
  // always resolve fresh element
  const initMenuLinks = () => {
    const el = getMobileMenu();
    if (!el) return;
    const menuLinks = el.querySelectorAll('a');
    menuLinks.forEach((link) => link.addEventListener('click', () => setTimeout(closeMobileMenu, 100)));
  };

  initMenuLinks();

  window.addEventListener('resize', () => {
    updateMobileMenuTop();
    if (window.innerWidth >= 768 && isMobileMenuOpen) closeMobileMenu();
  });

  // init scroll handling
  handleScroll();

})();
