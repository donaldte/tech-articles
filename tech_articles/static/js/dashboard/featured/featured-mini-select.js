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

        // Initialize first featured article mini-select
        const firstFeatureSelect = document.getElementById('id_first_feature');
        if (firstFeatureSelect) {
            firstMiniSelect = new MiniSelect(firstFeatureSelect, {
                ...miniSelectConfig,
                placeholder: firstFeatureSelect.getAttribute('placeholder') || gettext('Select first featured article'),
                onOpen: () => closeOthers(firstMiniSelect),
            });
        }

        // Initialize second featured article mini-select
        const secondFeatureSelect = document.getElementById('id_second_feature');
        if (secondFeatureSelect) {
            secondMiniSelect = new MiniSelect(secondFeatureSelect, {
                ...miniSelectConfig,
                placeholder: secondFeatureSelect.getAttribute('placeholder') || gettext('Select second featured article'),
                onOpen: () => closeOthers(secondMiniSelect),
            });
        }

        // Initialize third featured article mini-select
        const thirdFeatureSelect = document.getElementById('id_third_feature');
        if (thirdFeatureSelect) {
            thirdMiniSelect = new MiniSelect(thirdFeatureSelect, {
                ...miniSelectConfig,
                placeholder: thirdFeatureSelect.getAttribute('placeholder') || gettext('Select third featured article'),
                onOpen: () => closeOthers(thirdMiniSelect),
            });
        }
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
            
            const miniSelectConfig = {
                multiple: false,
                search: true,
                closeAfterSelect: true,
            };
            
            let newInstance;
            if (selector === '#id_first_feature') {
                firstMiniSelect = new MiniSelect(element, {
                    ...miniSelectConfig,
                    placeholder: element.getAttribute('placeholder') || gettext('Select first featured article'),
                    onOpen: () => closeOthers(firstMiniSelect),
                });
                newInstance = firstMiniSelect;
            } else if (selector === '#id_second_feature') {
                secondMiniSelect = new MiniSelect(element, {
                    ...miniSelectConfig,
                    placeholder: element.getAttribute('placeholder') || gettext('Select second featured article'),
                    onOpen: () => closeOthers(secondMiniSelect),
                });
                newInstance = secondMiniSelect;
            } else if (selector === '#id_third_feature') {
                thirdMiniSelect = new MiniSelect(element, {
                    ...miniSelectConfig,
                    placeholder: element.getAttribute('placeholder') || gettext('Select third featured article'),
                    onOpen: () => closeOthers(thirdMiniSelect),
                });
                newInstance = thirdMiniSelect;
            }
            
            return newInstance;
        }
    };

})();
