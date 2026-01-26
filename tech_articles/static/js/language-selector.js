/**
 * Language Selector Dropdown
 *
 * Features:
 * - Desktop (pointer): Hover to open/close dropdown
 * - Mobile (touch): Click to toggle dropdown
 * - Keyboard accessible: ESC to close, TAB/Arrow keys navigation
 * - Auto-closes on outside click
 * - WCAG 2.1 compliant (ARIA roles and attributes)
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
        toggleId: 'language-toggle',
        menuId: 'language-menu',
        menuDropdownClass: 'language-menu-dropdown',
        formSelector: '.language-form',
        openClass: 'opacity-100',
        visibleClass: 'visible',
        closedClass: 'opacity-0',
        invisibleClass: 'invisible',
        transitionDuration: 200
    };

    // ===================================
    // DOM Elements
    // ===================================
    const toggle = document.getElementById(CONFIG.toggleId);
    const menu = document.getElementById(CONFIG.menuId);

    // Exit early if elements don't exist
    if (!toggle || !menu) {
        console.warn('[language-selector] Required elements not found');
        return;
    }

    // ===================================
    // State & Detection
    // ===================================
    let isOpen = false;
    let isTouchDevice;

    /**
     * Detect if device supports touch/is mobile
     * Multiple detection methods for maximum compatibility
     */
    function detectTouchDevice() {
        return (
            ('ontouchstart' in window) ||
            (window.matchMedia && window.matchMedia('(hover: none) and (pointer: coarse)').matches) ||
            /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
        );
    }

    /**
     * Check if device has hover capability
     */
    function supportsHover() {
        return window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    }

    // ===================================
    // Menu State Functions
    // ===================================

    function openMenu() {
        if (isOpen) return;

        menu.classList.remove(CONFIG.closedClass, CONFIG.invisibleClass);
        menu.classList.add(CONFIG.openClass, CONFIG.visibleClass);
        toggle.setAttribute('aria-expanded', 'true');
        isOpen = true;

        console.debug('[language-selector] Menu opened');
    }

    function closeMenu() {
        if (!isOpen) return;

        menu.classList.remove(CONFIG.openClass, CONFIG.visibleClass);
        menu.classList.add(CONFIG.closedClass, CONFIG.invisibleClass);
        toggle.setAttribute('aria-expanded', 'false');
        isOpen = false;

        // Return focus to toggle button for accessibility
        toggle.focus();

        console.debug('[language-selector] Menu closed');
    }

    function toggleMenu() {
        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    }

    // ===================================
    // Event Handlers
    // ===================================

    /**
     * Toggle button click handler
     */
    function handleToggleClick(e) {
        e.stopPropagation();
        toggleMenu();
    }

    /**
     * Language option click handler
     */
    function handleLanguageSelect(e) {
        // Don't prevent form submission, just close the menu
        e.stopPropagation();

        // Close menu after a brief delay to allow visual feedback
        setTimeout(() => {
            closeMenu();
        }, 50);
    }

    /**
     * Keyboard navigation (ESC to close, etc.)
     */
    function handleKeyDown(e) {
        if (e.key === 'Escape' && isOpen) {
            e.preventDefault();
            closeMenu();
        }

        // Arrow key navigation for accessibility
        if (e.key === 'ArrowDown' && isOpen) {
            e.preventDefault();
            const buttons = menu.querySelectorAll('[role="menuitem"] button, [role="menuitem"][role="menuitem"]');
            const firstButton = buttons[0];
            if (firstButton) firstButton.focus();
        }

        if (e.key === 'ArrowUp' && isOpen) {
            e.preventDefault();
            const buttons = menu.querySelectorAll('[role="menuitem"] button, [role="menuitem"][role="menuitem"]');
            const lastButton = buttons[buttons.length - 1];
            if (lastButton) lastButton.focus();
        }
    }

    /**
     * Click outside handler
     */
    function handleOutsideClick(e) {
        // Check if click is outside both toggle and menu
        const isClickOnToggle = toggle.contains(e.target);
        const isClickOnMenu = menu.contains(e.target);

        if (!isClickOnToggle && !isClickOnMenu && isOpen) {
            closeMenu();
        }
    }

    /**
     * Hover behavior for desktop devices
     */
    function handleMouseEnter() {
        // Only use hover on devices that support it
        if (supportsHover()) {
            openMenu();
        }
    }

    function handleMouseLeave() {
        // Only use hover on devices that support it
        if (supportsHover()) {
            closeMenu();
        }
    }

    // ===================================
    // Initialize
    // ===================================

    // Detect device type
    isTouchDevice = detectTouchDevice();
    console.debug('[language-selector] Device detected:', {
        isTouchDevice,
        supportsHover: supportsHover()
    });

    // Attach toggle button listeners
    toggle.addEventListener('click', handleToggleClick);
    toggle.addEventListener('keydown', handleKeyDown);

    // Attach hover listeners only on desktop/pointer devices
    if (supportsHover()) {
        toggle.parentElement.addEventListener('mouseenter', handleMouseEnter);
        toggle.parentElement.addEventListener('mouseleave', handleMouseLeave);
    }

    // Attach language option click handlers
    const languageForms = menu.querySelectorAll(CONFIG.formSelector);
    languageForms.forEach((form) => {
        const button = form.querySelector('button[type="submit"]');
        if (button) {
            button.addEventListener('click', handleLanguageSelect);
        }
    });

    // Close menu on outside click (works for both touch and hover devices)
    document.addEventListener('click', handleOutsideClick, true);

    // Handle window resize - close menu if resized above mobile breakpoint
    // and hover is now available
    window.addEventListener('resize', () => {
        if (supportsHover() && isOpen) {
            // On resize to desktop, let hover take over
            return;
        }
        if (!supportsHover() && isOpen) {
            // Menu is open on mobile, keep it open
            return;
        }
    }, {passive: true});

    // Close menu on focus outside
    document.addEventListener('focusin', (e) => {
        const isToggleFocused = toggle.contains(e.target);
        const isMenuFocused = menu.contains(e.target);

        if (!isToggleFocused && !isMenuFocused && isOpen) {
            closeMenu();
        }
    });

    // ===================================
    // Initialization Complete
    // ===================================
    console.debug('[language-selector] Initialized successfully');
})();
