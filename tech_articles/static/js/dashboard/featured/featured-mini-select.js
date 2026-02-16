/**
 * MiniSelect initialization for featured articles management
 * Configures mini-select for the three featured article select fields
 * with search functionality and custom theme matching the dashboard design
 */

(function () {
    'use strict';

    // Store MiniSelect instances
    let firstMiniSelect, secondMiniSelect, thirdMiniSelect;

    /**
     * Initialize mini-select on page load
     */
    document.addEventListener('DOMContentLoaded', function () {
        initializeFeaturedMiniSelect();
    });

    /**
     * Close other mini-select instances when one is opened
     * @param {MiniSelect} currentMiniSelect - The mini-select instance that is opening
     */
    function closeOthers(currentMiniSelect) {
        [firstMiniSelect, secondMiniSelect, thirdMiniSelect].forEach(instance => {
            if (instance && instance !== currentMiniSelect && instance.isOpen) {
                instance.close();
            }
        });
    }

    /**
     * Initialize mini-select for featured article fields
     */
    function initializeFeaturedMiniSelect() {
        // Check if MiniSelect is loaded
        if (typeof MiniSelect === 'undefined') {
            console.error('MiniSelect not loaded');
            return;
        }

        // Common mini-select configuration
        const miniSelectConfig = {
            multiple: false, // Single selection for each field
            search: true,
            closeAfterSelect: true,
        };

        // Helper function to create a MiniSelect instance
        function createInstance(element, placeholder, instanceVar) {
            if (!element) return null;
            
            const instance = new MiniSelect(element, {
                ...miniSelectConfig,
                placeholder: element.getAttribute('placeholder') || placeholder,
                onOpen: () => closeOthers(instance),
            });
            
            return instance;
        }

        // Initialize featured article mini-selects
        const firstFeatureSelect = document.getElementById('id_first_feature');
        firstMiniSelect = createInstance(firstFeatureSelect, gettext('Select first featured article'));

        const secondFeatureSelect = document.getElementById('id_second_feature');
        secondMiniSelect = createInstance(secondFeatureSelect, gettext('Select second featured article'));

        const thirdFeatureSelect = document.getElementById('id_third_feature');
        thirdMiniSelect = createInstance(thirdFeatureSelect, gettext('Select third featured article'));
    }

    /**
     * Utility function to get mini-select instance
     * @param {string} selector - CSS selector for the select element
     * @returns {MiniSelect|null} MiniSelect instance or null
     */
    window.getFeaturedMiniSelectInstance = function (selector) {
        const element = document.querySelector(selector);
        if (!element) return null;

        // Find instance by comparing select elements
        if (firstMiniSelect && firstMiniSelect.selectElement === element) return firstMiniSelect;
        if (secondMiniSelect && secondMiniSelect.selectElement === element) return secondMiniSelect;
        if (thirdMiniSelect && thirdMiniSelect.selectElement === element) return thirdMiniSelect;

        return null;
    };

    /**
     * Utility function to destroy and reinitialize mini-select
     * Useful for dynamic form updates
     * @param {string} selector - CSS selector for the select element
     */
    window.refreshFeaturedMiniSelect = function (selector) {
        const instance = window.getFeaturedMiniSelectInstance(selector);
        if (instance) {
            instance.destroy();
            
            // Reinitialize only the specific instance
            const element = document.querySelector(selector);
            if (!element) return;
            
            // Get placeholder based on selector
            const placeholders = {
                '#id_first_feature': gettext('Select first featured article'),
                '#id_second_feature': gettext('Select second featured article'),
                '#id_third_feature': gettext('Select third featured article'),
            };
            
            const placeholder = element.getAttribute('placeholder') || placeholders[selector];
            
            const newInstance = new MiniSelect(element, {
                multiple: false,
                search: true,
                closeAfterSelect: true,
                placeholder: placeholder,
                onOpen: () => closeOthers(newInstance),
            });
            
            // Update the stored reference
            if (selector === '#id_first_feature') {
                firstMiniSelect = newInstance;
            } else if (selector === '#id_second_feature') {
                secondMiniSelect = newInstance;
            } else if (selector === '#id_third_feature') {
                thirdMiniSelect = newInstance;
            }
            
            return newInstance;
        }
    };

})();
