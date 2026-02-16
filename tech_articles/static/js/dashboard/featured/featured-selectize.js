/**
 * Selectize initialization for featured articles management
 * Configures selectize for the three featured article select fields
 * with search functionality and custom theme matching the dashboard design
 */

(function() {
  'use strict';

  /**
   * Initialize selectize on page load
   */
  document.addEventListener('DOMContentLoaded', function() {
    initializeFeaturedSelectize();
  });

  /**
   * Initialize selectize for featured article fields
   */
  function initializeFeaturedSelectize() {
    // Check if jQuery and selectize are loaded
    if (typeof jQuery === 'undefined' || typeof jQuery.fn.selectize === 'undefined') {
      console.warn('jQuery or Selectize not loaded');
      return;
    }

    // Common selectize configuration matching dashboard theme
    const selectizeConfig = {
      plugins: ['remove_button'],
      delimiter: ',',
      persist: false,
      create: false,
      highlight: true,
      closeAfterSelect: true,
      maxOptions: 1000,
      maxItems: 1, // Single selection for each field
      placeholder: function() {
        return this.$input.attr('placeholder') || gettext('Select an article...');
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

    // Initialize first featured article selectize
    const firstFeatureSelect = jQuery('#id_first_feature');
    if (firstFeatureSelect.length) {
      firstFeatureSelect.selectize({
        ...selectizeConfig,
        placeholder: firstFeatureSelect.attr('placeholder') || gettext('Select first featured article'),
      });
    }

    // Initialize second featured article selectize
    const secondFeatureSelect = jQuery('#id_second_feature');
    if (secondFeatureSelect.length) {
      secondFeatureSelect.selectize({
        ...selectizeConfig,
        placeholder: secondFeatureSelect.attr('placeholder') || gettext('Select second featured article'),
      });
    }

    // Initialize third featured article selectize
    const thirdFeatureSelect = jQuery('#id_third_feature');
    if (thirdFeatureSelect.length) {
      thirdFeatureSelect.selectize({
        ...selectizeConfig,
        placeholder: thirdFeatureSelect.attr('placeholder') || gettext('Select third featured article'),
      });
    }
  }

  /**
   * Utility function to get selectize instance
   * @param {string} selector - CSS selector for the select element
   * @returns {object|null} Selectize instance or null
   */
  window.getFeaturedSelectizeInstance = function(selector) {
    const element = jQuery(selector)[0];
    return element ? element.selectize : null;
  };

  /**
   * Utility function to destroy and reinitialize selectize
   * Useful for dynamic form updates
   * @param {string} selector - CSS selector for the select element
   */
  window.refreshFeaturedSelectize = function(selector) {
    const selectize = getFeaturedSelectizeInstance(selector);
    if (selectize) {
      selectize.destroy();
      initializeFeaturedSelectize();
    }
  };

})();
