/**
 * Filter Dropdowns Manager for Articles Listing
 * Handles dropdown toggle, chevron rotation, and filter selection.
 */

(function() {
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
      const dropdownType = button.dataset.dropdown;

      // Handle radio button changes (for sort filter)
      const radioInputs = dropdownContent.querySelectorAll('input[type="radio"]');
      radioInputs.forEach(radio => {
        radio.addEventListener('change', (e) => {
          const selectedOption = e.target.closest('.filter-option').querySelector('span').textContent.trim();
          filterLabel.textContent = selectedOption;
          
          // Close dropdown after selection
          setTimeout(() => {
            this.closeAllDropdowns();
          }, 150);

          // Trigger filtering (could be customized later)
          this.applyFilters();
        });
      });

      // Handle checkbox changes (for category filter)
      const checkboxInputs = dropdownContent.querySelectorAll('input[type="checkbox"]');
      checkboxInputs.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
          this.updateCategoryLabel(container);
          this.applyFilters();
        });
      });
    }

    updateCategoryLabel(container) {
      const button = container.querySelector('[data-dropdown]');
      const filterLabel = button.querySelector('.filter-label');
      const dropdownContent = container.querySelector('.filter-dropdown-content');
      const checkedBoxes = dropdownContent.querySelectorAll('input[type="checkbox"]:checked');

      if (checkedBoxes.length === 0) {
        filterLabel.textContent = gettext('All Categories');
      } else if (checkedBoxes.length === 1) {
        const selectedOption = checkedBoxes[0].closest('.filter-option').querySelector('span').textContent.trim();
        filterLabel.textContent = selectedOption;
      } else {
        filterLabel.textContent = gettext('Multiple Categories');
      }
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
      ).map(checkbox => checkbox.value);

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
        ).map(checkbox => checkbox.dataset.id || checkbox.value)
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
