/**
 * Selectize initialization for article management
 * Configures selectize for categories and tags multi-select fields
 * with custom theme matching the dashboard design
 */

(function() {
  'use strict';

  /**
   * Initialize selectize on page load
   */
  document.addEventListener('DOMContentLoaded', function() {
    initializeSelectize();
  });

  /**
   * Initialize selectize for categories and tags fields
   */
  function initializeSelectize() {
    // Check if jQuery and selectize are loaded
    if (typeof jQuery === 'undefined' || typeof jQuery.fn.selectize === 'undefined') {
      return; // Silently fail if dependencies are not loaded
    }

    // Common selectize configuration matching dashboard theme
    const selectizeConfig = {
      plugins: ['remove_button'],
      delimiter: ',',
      persist: false,
      create: false,
      highlight: true,
      closeAfterSelect: false,
      maxOptions: 1000,
      placeholder: function() {
        return this.$input.attr('placeholder') || 'Select...';
      },
      render: {
        option: function(data, escape) {
          return '<div>' + escape(data.text) + '</div>';
        },
        item: function(data, escape) {
          return '<div>' + escape(data.text) + '</div>';
        }
      },
      // Dropdown settings
      dropdownParent: 'body',
      // Search settings
      searchField: ['text'],
      sortField: 'text',
      // Accessibility
      selectOnTab: true,
      // Loading messages
      loadingClass: 'loading',
      loadThrottle: 300,
    };

    // Initialize categories selectize
    const categoriesSelect = jQuery('#id_categories');
    if (categoriesSelect.length) {
      categoriesSelect.selectize({
        ...selectizeConfig,
        placeholder: categoriesSelect.attr('placeholder') || gettext('Select categories'),
      });
    }

    // Initialize tags selectize
    const tagsSelect = jQuery('#id_tags');
    if (tagsSelect.length) {
      tagsSelect.selectize({
        ...selectizeConfig,
        placeholder: tagsSelect.attr('placeholder') || gettext('Select tags'),
      });
    }
  }

  /**
   * Utility function to get selectize instance
   * @param {string} selector - CSS selector for the select element
   * @returns {object|null} Selectize instance or null
   */
  window.getSelectizeInstance = function(selector) {
    const element = jQuery(selector)[0];
    return element ? element.selectize : null;
  };

  /**
   * Utility function to destroy and reinitialize selectize
   * Useful for dynamic form updates
   * @param {string} selector - CSS selector for the select element
   */
  window.refreshSelectize = function(selector) {
    const selectize = getSelectizeInstance(selector);
    if (selectize) {
      selectize.destroy();
      initializeSelectize();
    }
  };

})();
