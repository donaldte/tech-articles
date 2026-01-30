/**
 * SidebarManager module to handle sidebar interactions, responsive behavior, and menu management.
 * Uses Module Pattern for encapsulation and State Pattern for sidebar states.
 */
const SidebarManager = (function () {
    // Private variables
    let isMobile = window.innerWidth < 1024; // Tracks mobile (<1024px) or desktop
    let isSidebarExpanded = getInitialSidebarState(); // Tracks sidebar state (expanded or collapsed, desktop perspective)
    const selectors = {
        sidebar: '#sidebar',
        sidebarHeader: '.sidebar-header',
        header: '#header',
        mainContent: '#main-content',
        barsIcon: 'header button.action',
        barsIcon1: '#header-icon-1',
        barsIcon2: '#header-icon-2', // Hamburger icon (open)
        barsIcon3: '#header-icon-3', // Close icon
        sidebarIcon1: '#sidebar-icon-1', // Expanded sidebar icon
        sidebarIcon2: '#sidebar-icon-2', // Collapsed sidebar icon
        closeNotifBtn: '#close-notif-btn',
        mobileMenuBtn: '#mobile-menu-btn',
        mobileActions: '#mobile-actions',
        notifBtn: '#notif-btn',
        profileBtn: '#profile-btn',
        notifDropdown: '#notification-dropdown',
        profileDropdown: '#profile-dropdown',
        overlay: '#content-overlay',
        sidebarMenu: '#sidebar-menu',
    };

    // Cache DOM elements
    const elements = {};
    for (const [key, selector] of Object.entries(selectors)) {
        elements[key] = document.querySelector(selector);
    }

    // Ensure sidebarMenu is properly cached
    if (!elements.sidebarMenu) {
        elements.sidebarMenu = document.querySelector(selectors.sidebarMenu);
    }

    // Sidebar state configurations
    const states = {
        expanded: {
            sidebarClasses: ['translate-x-0', 'w-[290px]'],
            removeSidebarClasses: ['-translate-x-full', 'lg:w-[90px]', 'hidden'],
            headerClasses: ['justify-start',],
            barsClasses: ['lg:bg-transparent', 'bg-gray-100'],
            barsIcon2Classes: ['hidden'], // Hide hamburger icon
            barsIcon3Classes: ['block', 'lg:hidden'], // Show close icon
            removeBarsIcon2Classes: ['block', 'lg:hidden'],
            removeBarsIcon3Classes: ['hidden'],
            menuGroupTitleClasses: [],
            menuGroupIconClasses: ['hidden'],
            menuItemTextClasses: [],
            menuItemArrowClasses: [],
        },
        collapsed: {
            sidebarClasses: ['translate-x-0', 'lg:w-[90px]'],
            removeSidebarClasses: ['-translate-x-full', 'w-[290px]'],
            headerClasses: ['justify-center'],
            barsClasses: [],
            barsIcon2Classes: ['block', 'lg:hidden'], // Show hamburger icon
            barsIcon3Classes: ['hidden'], // Hide close icon
            removeBarsIcon2Classes: ['hidden'],
            removeBarsIcon3Classes: ['block', 'lg:hidden'],
            menuGroupTitleClasses: ['lg:hidden'],
            menuGroupIconClasses: ['lg:block', 'hidden'],
            menuItemTextClasses: ['lg:hidden'],
            menuItemArrowClasses: ['lg:hidden'],
        },
    };

    /**
     * Get initial sidebar state based on screen size (no localStorage).
     * @returns {boolean} - Initial state (true for expanded on desktop, false for collapsed)
     */
    function getInitialSidebarState() {
        // Default: expanded on mobile (implies collapsed on desktop), collapsed on desktop (implies expanded on mobile)
        return !isMobile;
    }

    /**
     * Initialize the module by setting up DOM elements, event listeners, and initial state.
     */
    function init() {
        // Clear localStorage for sidebar state
        localStorage.removeItem('sidebarExpanded');

        // Create overlay if not exists
        if (!elements.overlay) {
            const overlay = document.createElement('div');
            overlay.id = 'content-overlay';
            overlay.className = 'fixed inset-0 bg-black/50 z-30 hidden';
            document.body.appendChild(overlay);
            elements.overlay = overlay;
        }

        // Set initial state based on screen size
        updateResponsiveState();
        if (isMobile) {
            isSidebarExpanded = true; // Force collapsed state on mobile
            applyState('collapsed');
        } else {
            applyState(getEffectiveState());
        }

        // Initialize MenuManager
        MenuManager.init();

        // Setup event listeners
        setupEventListeners();

        // Update content width to 100%
        updateContentWidth();
    }

    /**
     * Get effective sidebar state based on screen size and isSidebarExpanded.
     * @returns {string} - 'expanded' or 'collapsed'
     */
    function getEffectiveState() {
        if (isMobile) {
            // On mobile, inverse of desktop state
            return isSidebarExpanded ? 'collapsed' : 'expanded';
        }
        // On desktop, use the stored state
        return isSidebarExpanded ? 'expanded' : 'collapsed';
    }

    /**
     * Update responsive state based on screen width.
     */
    function updateResponsiveState() {
        isMobile = window.innerWidth < 1024;
        if (isMobile) {
            // In mobile, sidebar visibility depends on effective state
            elements.sidebar?.classList.add('w-[290px]');
            elements.sidebar?.classList.remove('lg:w-[90px]');
            toggleMenuElements(false);
        } else {
            // In desktop, apply current state
            elements.sidebar?.classList.remove('hidden');
            toggleMenuElements(isSidebarExpanded);
        }
        // Apply the effective state
        applyState(getEffectiveState());
    }

    /**
     * Apply sidebar state (expanded or collapsed).
     * @param {string} state - 'expanded' or 'collapsed'
     */
    function applyState(state) {
        const config = states[state];
        if (!elements.sidebar) return;

        // Update sidebar classes
        elements.sidebar.classList.add(...(Array.isArray(config.sidebarClasses) ? config.sidebarClasses : [config.sidebarClasses]));
        elements.sidebar.classList.remove(...(Array.isArray(config.removeSidebarClasses) ? config.removeSidebarClasses : [config.removeSidebarClasses]));

        // In mobile, control sidebar visibility
        if (isMobile) {
            if (state === 'collapsed') {
                elements.sidebar.classList.add('hidden');
                elements.overlay.classList.add('hidden');
                MenuManager.closeAllDropdowns();
                elements.sidebarMenu?.classList.remove('mt-4');
            } else {
                elements.sidebar.classList.remove('hidden');
                elements.overlay.classList.remove('hidden');
                MenuManager.restoreDropdowns();
                elements.sidebarMenu?.classList.add('mt-4');
            }
        } else {
            // In desktop, sidebar is always visible
            elements.sidebar.classList.remove('hidden');
            elements.overlay.classList.add('hidden');
            if (state === 'collapsed') {
                MenuManager.closeAllDropdowns();
                elements.sidebarMenu?.classList.remove('mt-4');
            } else {
                MenuManager.restoreDropdowns();
            }
        }

        // Update header classes
        elements.sidebarHeader?.classList.add(...config.headerClasses);
        elements.sidebarHeader?.classList.remove(state === 'expanded' ? 'justify-center' : 'justify-start');

        // Update bars icon classes
        elements.barsIcon?.classList.add(...config.barsClasses);
        elements.barsIcon?.classList.remove(...(state === 'expanded' ? [] : ['lg:bg-transparent', 'bg-gray-100']));
        elements.barsIcon2?.classList.add(...config.barsIcon2Classes);
        elements.barsIcon2?.classList.remove(...config.removeBarsIcon2Classes);
        elements.barsIcon3?.classList.add(...config.barsIcon3Classes);
        elements.barsIcon3?.classList.remove(...config.removeBarsIcon3Classes);

        // Update menu elements visibility
        toggleMenuElements(state === 'expanded');
    }

    /**
     * Toggle visibility of menu group titles, icons, and text.
     * @param {boolean} isVisible - Whether to show text or icons
     */
    function toggleMenuElements(isVisible) {
        if (!elements.sidebar) return;
        elements.sidebar.querySelectorAll('.menu-group-title').forEach(el => {
            el.classList.toggle('lg:hidden', !isVisible && !isMobile);
        });
        elements.sidebar.querySelectorAll('.menu-group-icon').forEach(el => {
            el.classList.toggle('hidden', isVisible || isMobile);
            el.classList.toggle('lg:block', !isVisible && !isMobile);
        });
        elements.sidebar.querySelectorAll('.menu-item-text').forEach(el => {
            el.classList.toggle('lg:hidden', !isVisible && !isMobile);
        });
        elements.sidebar.querySelectorAll('.menu-item-arrow').forEach(el => {
            el.classList.toggle('lg:hidden', !isVisible && !isMobile);
        });
        elements.sidebarIcon1?.classList.toggle('hidden', !isVisible && !isMobile);
        elements.sidebarIcon2?.classList.toggle('hidden', isVisible || isMobile);
        elements.sidebarIcon2?.classList.toggle('lg:block', !isVisible && !isMobile);
    }

    /**
     * Toggle sidebar state and apply responsive behavior.
     */
    function toggleSidebar() {
        isSidebarExpanded = !isSidebarExpanded;
        applyState(getEffectiveState());
    }

    /**
     * Close sidebar explicitly (used for overlay and outside clicks).
     */
    function closeSidebar() {
        if (isMobile && getEffectiveState() === 'expanded') {
            isSidebarExpanded = true; // On mobile, closing sidebar means desktop should be collapsed
            applyState('collapsed');
        }
    }

    /**
     * Toggle dropdown visibility.
     * @param {HTMLElement} dropdown - The dropdown element to toggle
     * @param {boolean} closeOthers - Whether to close other dropdowns
     */
    function toggleDropdown(dropdown, closeOthers = true) {
        if (closeOthers) {
            elements.notifDropdown?.classList.add('hidden');
            elements.profileDropdown?.classList.add('hidden');
        }
        dropdown?.classList.toggle('hidden');
    }

    /**
     * Update header and main content width to 100%.
     */
    function updateContentWidth() {
        if (elements.header) elements.header.style.width = '100%';
        if (elements.mainContent) elements.mainContent.style.width = '100%';
    }

    /**
     * Setup all event listeners for sidebar interactions.
     */
    function setupEventListeners() {
        // Toggle sidebar on bars icon click
        elements.barsIcon?.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleSidebar();
        });

        // Close sidebar on overlay click (mobile)
        elements.overlay?.addEventListener('click', () => {
            if (isMobile) {
                closeSidebar();
            }
        });

        // Close sidebar and dropdowns on outside click
        document.addEventListener('click', (e) => {
            // Close sidebar on outside click (mobile)
            if (isMobile && !e.target.closest('#sidebar, header button') && !elements.sidebar?.classList.contains('hidden')) {
                closeSidebar();
            }
            // Close notification dropdown on outside click
            if (!e.target.closest('#notif-btn, #notification-dropdown')) {
                elements.notifDropdown?.classList.add('hidden');
            }
            // Close profile dropdown on outside click
            if (!e.target.closest('#profile-btn, #profile-dropdown')) {
                elements.profileDropdown?.classList.add('hidden');
            }
            // Close mobile actions on outside click
            if (!e.target.closest('#mobile-menu-btn, #mobile-actions')) {
                elements.mobileActions?.classList.add('hidden');
            }
        });

        // Toggle notification dropdown
        elements.closeNotifBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleDropdown(elements.notifDropdown);
        });
        elements.notifBtn?.addEventListener('click', () => toggleDropdown(elements.notifDropdown));

        // Toggle profile dropdown
        elements.profileBtn?.addEventListener('click', () => toggleDropdown(elements.profileDropdown));

        // Toggle mobile actions
        elements.mobileMenuBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            elements.mobileActions?.classList.toggle('hidden');
            elements.mobileActions?.classList.toggle('flex', isMobile);
        });

        // Expand sidebar on hover (desktop only)
        elements.sidebar?.addEventListener('mouseenter', () => {
            if (!isSidebarExpanded && !isMobile) {
                applyState('expanded');
            }
        });

        // Collapse sidebar on mouse leave (desktop only)
        elements.sidebar?.addEventListener('mouseleave', () => {
            if (!isSidebarExpanded && !isMobile) {
                applyState('collapsed');
            }
        });

        // Update state on window resize with debouncing
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                const wasMobile = isMobile;
                updateResponsiveState();
                if (wasMobile !== isMobile) {
                    applyState(getEffectiveState());
                }
            }, 100);
        });
    }

    // Public API
    return {
        init,
    };
})();

/**
 * MenuManager module to handle menu options, sub-options, and active states without relying on IDs.
 * Uses Module Pattern for encapsulation and State Pattern for menu states.
 */
const MenuManager = (function () {
    // Private variables
    let activeOptionElement = null; // Reference to the initially active option (remains active)
    let openDropdownIndices = []; // Array of indices of currently open dropdowns
    const selectors = {
        menuItems: '.menu-item',
        menuDropdownContainers: '.menu-dropdown-container',
        menuDropdownItems: '.menu-dropdown-item',
    };

    // Cache DOM elements
    const elements = {
        menuItems: document.querySelectorAll(selectors.menuItems),
        menuDropdownContainers: document.querySelectorAll(selectors.menuDropdownContainers),
        menuDropdownItems: document.querySelectorAll(selectors.menuDropdownItems),
    };

    /**
     * Scroll to the active menu item or sub-item on initialization.
     */
    function scrollToActiveOption() {
        const sidebar = document.querySelector('#sidebar');
        if (!sidebar) return;

        let activeElement = sidebar.querySelector('.menu-item-active');
        if (!activeElement) {
            activeElement = sidebar.querySelector('.menu-dropdown-item-active');
        }

        if (activeElement) {
            setTimeout(() => {
                activeElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'nearest'
                });
            }, 100);
        }
    }

    /**
     * Initialize the module by setting up initial state and event listeners.
     */
    function init() {
        // Clear localStorage for toggled option
        localStorage.removeItem('toggledOptionIndex');

        // Set initial active option
        setInitialActiveOption();

        // Scroll to the active option
        scrollToActiveOption();

        // Setup event listeners
        setupEventListeners();
    }

    /**
     * Set the initial active option based on the menu-item-active class.
     */
    function setInitialActiveOption() {
        elements.menuItems.forEach((item, index) => {
            if (item.classList.contains('menu-item-active')) {
                activeOptionElement = item;
                // Check if the active option has an active sub-option
                const dropdown = item.parentElement.querySelector('.menu-dropdown-container');
                if (dropdown) {
                    const hasActiveSubOption = Array.from(dropdown.querySelectorAll('.menu-dropdown-item')).some(subItem =>
                        subItem.classList.contains('menu-dropdown-item-active')
                    );
                    if (hasActiveSubOption) {
                        openDropdown(item);
                        openDropdownIndices.push(index);
                    }
                }
            }
        });
    }

    /**
     * Open the dropdown for the specified option.
     * @param {HTMLElement} item - The menu item element
     */
    function openDropdown(item) {
        const dropdown = item.parentElement.querySelector('.menu-dropdown-container');
        if (dropdown) {
            dropdown.classList.remove('hidden');
            const arrow = item.querySelector('.menu-item-arrow');
            if (arrow) {
                arrow.classList.remove('menu-item-arrow-inactive');
                arrow.classList.add('menu-item-arrow-active');
            }
        }
    }

    /**
     * Close the dropdown for the specified option.
     * @param {HTMLElement} item - The menu item element
     */
    function closeDropdown(item) {
        const dropdown = item.parentElement.querySelector('.menu-dropdown-container');
        if (dropdown) {
            dropdown.classList.add('hidden');
            const arrow = item.querySelector('.menu-item-arrow');
            if (arrow) {
                arrow.classList.add('menu-item-arrow-inactive');
                arrow.classList.remove('menu-item-arrow-active');
            }
        }
    }

    /**
     * Set the specified option as active.
     * @param {HTMLElement} item - The menu item element
     */
    function setOptionActive(item) {
        item.classList.add('menu-item-active');
        item.classList.remove('menu-item-inactive');
        const icon = item.querySelector('svg:not(.menu-item-arrow)');
        if (icon) {
            icon.classList.add('menu-item-icon-active');
            icon.classList.remove('menu-item-icon-inactive');
        }
    }

    /**
     * Set the specified option as inactive.
     * @param {HTMLElement} item - The menu item element
     */
    function setOptionInactive(item) {
        if (item !== activeOptionElement) {
            item.classList.remove('menu-item-active');
            item.classList.add('menu-item-inactive');
            const icon = item.querySelector('svg:not(.menu-item-arrow)');
            if (icon) {
                icon.classList.remove('menu-item-icon-active');
                icon.classList.add('menu-item-icon-inactive');
            }
        }
    }

    /**
     * Toggle the dropdown state for the specified option.
     * @param {HTMLElement} item - The menu item element
     */
    function toggleOptionDropdown(item) {
        const itemIndex = Array.from(elements.menuItems).indexOf(item);
        const dropdown = item.parentElement.querySelector('.menu-dropdown-container');
        const isDropdownOpen = dropdown && !dropdown.classList.contains('hidden');
        const isActiveOption = activeOptionElement === item;

        // Close all other dropdowns
        elements.menuItems.forEach((otherItem, otherIndex) => {
            if (otherItem !== item) {
                closeDropdown(otherItem);
                setOptionInactive(otherItem);
                openDropdownIndices = openDropdownIndices.filter(index => index !== otherIndex);
            }
        });

        // Toggle the current dropdown
        if (isDropdownOpen) {
            closeDropdown(item);
            if (!isActiveOption) {
                setOptionInactive(item); // Deactivate option when closing dropdown
            }
            openDropdownIndices = openDropdownIndices.filter(index => index !== itemIndex);
        } else {
            openDropdown(item);
            if (!isActiveOption) {
                setOptionActive(item);
            }
            if (!openDropdownIndices.includes(itemIndex)) {
                openDropdownIndices.push(itemIndex);
            }
        }
    }

    /**
     * Close all dropdowns and deactivate their options (except active option).
     */
    function closeAllDropdowns() {
        elements.menuItems.forEach(item => {
            closeDropdown(item);
            setOptionInactive(item);
        });
        // Do not clear openDropdownIndices to preserve state for restoreDropdowns
    }

    /**
     * Restore previously open dropdowns based on openDropdownIndices.
     */
    function restoreDropdowns() {
        openDropdownIndices.forEach(index => {
            if (index >= 0 && index < elements.menuItems.length) {
                const item = elements.menuItems[index];
                openDropdown(item);
                if (item !== activeOptionElement) {
                    setOptionActive(item);
                }
            }
        });
    }

    /**
     * Handle click on a menu item.
     * @param {HTMLElement} item - The menu item element
     */
    function handleMenuItemClick(item) {
        const hasDropdown = item.parentElement.querySelector('.menu-dropdown-container');
        if (hasDropdown) {
            toggleOptionDropdown(item);
        }
        // Do not activate options without dropdowns unless they are the active option
    }

    /**
     * Setup event listeners for menu interactions.
     */
    function setupEventListeners() {
        elements.menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                handleMenuItemClick(item);
            });
        });
    }

    // Public API
    return {
        init,
        closeAllDropdowns,
        restoreDropdowns,
    };
})();

// Initialize the sidebar manager on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    SidebarManager.init();
});
