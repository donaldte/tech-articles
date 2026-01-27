/**
 * Language Selector Dropdown - Simple and Reliable
 *
 * Features:
 * - Desktop (pointer): Hover to open/close dropdown
 * - Mobile (touch): Click to toggle dropdown
 * - Keyboard accessible: ESC to close
 * - Auto-closes on outside click
 *
 * @author djoukevin1469@gmail.com
 * @version 2.0.0
 */

(function () {
    'use strict';

    const toggle = document.getElementById('language-toggle');
    const menu = document.getElementById('language-menu');

    if (!toggle || !menu) {
        console.warn('[language-selector] Required elements not found');
        return;
    }

    let isOpen = false;
    let closeTimeout;

    function supportsHover() {
        try { return window.matchMedia('(hover: hover)').matches; } catch { return false; }
    }

    function updateMenuPosition() {
        const rect = toggle.getBoundingClientRect();
        const menuWidth = menu.offsetWidth || 192;
        const menuHeight = menu.offsetHeight || 0;

        // Position below toggle, right-aligned
        let left = rect.right - menuWidth;
        const margin = 8;
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

    function openMenu() {
        if (isOpen) return;

        // Clear any pending close
        if (closeTimeout) clearTimeout(closeTimeout);

        // Dispatch event to close other dropdowns (profile menu)
        try {
            document.dispatchEvent(new CustomEvent('language-selector:toggle', { detail: { opening: true } }));
        } catch (err) {}

        // Show and position
        menu.style.display = 'block';
        menu.style.pointerEvents = 'auto';
        updateMenuPosition();

        // Add visible classes
        menu.classList.remove('opacity-0', 'invisible');
        menu.classList.add('opacity-100', 'visible');

        toggle.setAttribute('aria-expanded', 'true');
        isOpen = true;

        // Notify navbar
        try { document.dispatchEvent(new CustomEvent('close-mobile-menu')); } catch (err) {}
    }

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
        }, 250);

        toggle.setAttribute('aria-expanded', 'false');
        isOpen = false;
    }

    function toggleMenu(e) {
        if (e) e.stopPropagation();
        if (isOpen) closeMenu();
        else openMenu();
    }

    function handleOutsideClick(e) {
        if (!isOpen) return;
        const isClickOnToggle = toggle.contains(e.target);
        const isClickOnMenu = menu.contains(e.target);
        if (!isClickOnToggle && !isClickOnMenu) closeMenu();
    }

    // Event listeners
    toggle.addEventListener('click', toggleMenu);
    document.addEventListener('click', handleOutsideClick);
    document.addEventListener('touchstart', handleOutsideClick);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isOpen) {
            e.preventDefault();
            closeMenu();
        }
    });

    // Language buttons
    try {
        menu.querySelectorAll('.language-form button[type="submit"]').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                setTimeout(closeMenu, 60);
            });
        });
    } catch (err) {}

    // Hover on desktop only - on mobile, dropdown acts as toggle
    if (supportsHover()) {
        // Desktop: hover to open/close
        toggle.addEventListener('pointerenter', openMenu);
        toggle.addEventListener('pointerleave', () => {
            closeTimeout = setTimeout(closeMenu, 150);
        });

        menu.addEventListener('pointerenter', () => {
            if (closeTimeout) clearTimeout(closeTimeout);
        });

        menu.addEventListener('pointerleave', () => {
            closeTimeout = setTimeout(closeMenu, 150);
        });
    } else {
        // Mobile: click outside closes dropdown (toggle is click, outside-click closes)
        // No hover behavior - dropdown stays open until user clicks outside or selects language
    }

    // Reposition on scroll/resize
    window.addEventListener('resize', () => {
        if (isOpen) updateMenuPosition();
    }, { passive: true });

    window.addEventListener('scroll', () => {
        if (isOpen) updateMenuPosition();
    }, { passive: true });

    // Initial state
    toggle.setAttribute('aria-haspopup', 'true');
    menu.style.position = 'absolute';
})();
