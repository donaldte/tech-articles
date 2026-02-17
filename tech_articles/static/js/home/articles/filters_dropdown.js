/**
 * Filter Dropdowns Manager for Articles Listing
 * Handles dropdown toggle, chevron rotation, and filter selection.
 */

(function () {
    'use strict';

    class FiltersDropdownManager {
        constructor() {
            this.dropdownContainers = document.querySelectorAll('.filter-dropdown-container');
            this.activeDropdown = null;
            this.overlay = null;
            this.init();
        }

        init() {
            if (this.dropdownContainers.length === 0) {
                return;
            }

            this.createOverlay();
            this.bindEvents();
        }

        createOverlay() {
            // Create overlay element for click-outside detection
            this.overlay = document.createElement('div');
            this.overlay.className = 'filter-dropdown-overlay';
            document.body.appendChild(this.overlay);

            this.overlay.addEventListener('click', () => this.closeAllDropdowns());
        }

        bindEvents() {
            this.dropdownContainers.forEach(container => {
                const button = container.querySelector('[data-dropdown]');
                if (!button) return;

                // Toggle dropdown on button click
                button.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleDropdown(container);
                });

                // Handle filter option changes
                const dropdownContent = container.querySelector('.filter-dropdown-content');
                if (dropdownContent) {
                    this.bindFilterOptions(container, dropdownContent);
                }
            });

            // Close dropdowns on Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeAllDropdowns();
                }
            });
        }

        bindFilterOptions(container, dropdownContent) {
            const button = container.querySelector('[data-dropdown]');
            const filterLabel = button.querySelector('.filter-label');

            dropdownContent.addEventListener('change', (e) => {
                const target = e.target;
                if (!target || target.tagName !== 'INPUT') return;

                if (target.type === 'radio') {
                    const selectedOption = target.closest('.filter-option').querySelector('span').textContent.trim();
                    filterLabel.textContent = selectedOption;

                    setTimeout(() => {
                        this.closeAllDropdowns();
                    }, 150);

                    this.applyFilters();
                    return;
                }

                if (target.type === 'checkbox') {
                    this.handleCategoryChange(container, target);
                    this.updateCategoryLabel(container);
                    this.applyFilters();
                }
            });
        }

        isAllCategoryOption(checkbox) {
            return checkbox && (checkbox.dataset.all === 'true' || checkbox.value === 'all');
        }

        handleCategoryChange(container, changedCheckbox) {
            const dropdownContent = container.querySelector('.filter-dropdown-content');
            const allOption = dropdownContent.querySelector('input[type="checkbox"][data-all="true"]');
            const otherOptions = Array.from(dropdownContent.querySelectorAll('input[type="checkbox"]'))
                .filter(cb => !this.isAllCategoryOption(cb));

            if (this.isAllCategoryOption(changedCheckbox) && changedCheckbox.checked) {
                otherOptions.forEach(cb => {
                    cb.checked = false;
                });
                return;
            }

            if (!this.isAllCategoryOption(changedCheckbox) && changedCheckbox.checked && allOption) {
                allOption.checked = false;
            }

            const anyOtherChecked = otherOptions.some(cb => cb.checked);
            if (!anyOtherChecked && allOption) {
                allOption.checked = true;
            }
        }

        updateCategoryLabel(container) {
            const button = container.querySelector('[data-dropdown]');
            const filterLabel = button.querySelector('.filter-label');
            const dropdownContent = container.querySelector('.filter-dropdown-content');
            const allOption = dropdownContent.querySelector('input[type="checkbox"][data-all="true"]');
            const checkedBoxes = Array.from(
                dropdownContent.querySelectorAll('input[type="checkbox"]:checked')
            ).filter(cb => !this.isAllCategoryOption(cb));

            if ((allOption && allOption.checked) || checkedBoxes.length === 0) {
                filterLabel.textContent = gettext('All Categories');
                return;
            }

            if (checkedBoxes.length === 1) {
                const selectedOption = checkedBoxes[0].closest('.filter-option').querySelector('span').textContent.trim();
                filterLabel.textContent = selectedOption;
                return;
            }

            const label = interpolate(
                ngettext('%s category selected', '%s categories selected', checkedBoxes.length),
                [checkedBoxes.length]
            );
            filterLabel.textContent = label;
        }

        toggleDropdown(container) {
            const isActive = container.classList.contains('active');

            // Close all dropdowns first
            this.closeAllDropdowns();

            if (!isActive) {
                // Open the clicked dropdown
                container.classList.add('active');
                this.overlay.classList.add('active');
                this.activeDropdown = container;
            }
        }

        closeAllDropdowns() {
            this.dropdownContainers.forEach(container => {
                container.classList.remove('active');
            });

            if (this.overlay) {
                this.overlay.classList.remove('active');
            }

            this.activeDropdown = null;
        }

        applyFilters() {
            // Collect selected filters
            const selectedSort = document.querySelector('input[name="sort"]:checked')?.value || 'recent';
            const selectedCategories = Array.from(
                document.querySelectorAll('input[name="category"]:checked')
            ).filter(checkbox => !this.isAllCategoryOption(checkbox))
                .map(checkbox => checkbox.dataset.id || checkbox.value);

            // Log filters for debugging (can be replaced with actual filtering logic)
            console.log('Applied filters:', {
                sort: selectedSort,
                categories: selectedCategories
            });

            // Here you can implement the actual filtering logic
            // For example: fetch articles with these filters via AJAX
            // or filter the displayed articles on the client side
        }

        getSelectedFilters() {
            return {
                sort: document.querySelector('input[name="sort"]:checked')?.value || 'recent',
                categories: Array.from(
                    document.querySelectorAll('input[name="category"]:checked')
                ).filter(checkbox => !this.isAllCategoryOption(checkbox))
                    .map(checkbox => checkbox.dataset.id || checkbox.value)
            };
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new FiltersDropdownManager();
        });
    } else {
        new FiltersDropdownManager();
    }
})();
