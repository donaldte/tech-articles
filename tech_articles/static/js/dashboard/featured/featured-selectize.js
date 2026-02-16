/**
 * Selectize initialization for featured articles management
 * Configures selectize for the three featured article select fields
 * with search functionality and custom theme matching the dashboard design
 */

(function () {
    'use strict';

    // Store selectize instances
    let firstSelectize, secondSelectize, thirdSelectize;

    /**
     * Initialize selectize on page load
     */
    document.addEventListener('DOMContentLoaded', function () {
        initializeFeaturedSelectize();
    });

    /**
     * Close other selectize instances when one is opened
     * @param {object} currentSelectize - The selectize instance that is opening
     */
    function closeOthers(currentSelectize) {
        [firstSelectize, secondSelectize, thirdSelectize].forEach(s => {
            if (s && s !== currentSelectize) {
                try {
                    s.close();
                } catch (err) {
                    // ignore
                }
                // Also remove focus from the input/control to ensure it loses focus
                try {
                    var $inp = s.$control && s.$control.find('input');
                    if ($inp && $inp.length) {
                        $inp.blur();
                    }
                } catch (err) {
                    // ignore
                }
            }
        });
    }

    /**
     * Handle document click to close selectize when clicking outside
     * @param {Event} e - The click event
     */
    function handleDocumentClick(e) {
        let inside = false;
        [firstSelectize, secondSelectize, thirdSelectize].forEach(s => {
            try {
                if (s && s.$control && s.$control[0].contains(e.target)) inside = true;
                if (s && s.$dropdown && s.$dropdown[0].contains(e.target)) inside = true;
            } catch (err) {
                // ignore DOM access errors
            }
        });
        if (!inside) {
            [firstSelectize, secondSelectize, thirdSelectize].forEach(s => {
                if (!s) return;
                try {
                    var $inp = s.$control && s.$control.find('input');
                    if ($inp && $inp.length) {
                        $inp.blur();
                    }
                } catch (err) {
                    // ignore
                }
                try {
                    s.close();
                } catch (err) { /* ignore */
                }
            });
        }
    }

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
            allowEmptyOption: true,
            maxOptions: 1000,
            maxItems: 1, // Single selection for each field
            placeholder: function () {
                return this.$input.attr('placeholder') || gettext('Select an article...');
            },
            render: {
                option: function (data, escape) {
                    return '<div>' + escape(data.text) + '</div>';
                },
                item: function (data, escape) {
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
            firstSelectize = firstFeatureSelect.selectize({
                ...selectizeConfig,
                placeholder: firstFeatureSelect.attr('placeholder') || gettext('Select first featured article'),
            })[0].selectize;
        }

        // Initialize second featured article selectize
        const secondFeatureSelect = jQuery('#id_second_feature');
        if (secondFeatureSelect.length) {
            secondSelectize = secondFeatureSelect.selectize({
                ...selectizeConfig,
                placeholder: secondFeatureSelect.attr('placeholder') || gettext('Select second featured article'),
            })[0].selectize;
        }

        // Initialize third featured article selectize
        const thirdFeatureSelect = jQuery('#id_third_feature');
        if (thirdFeatureSelect.length) {
            thirdSelectize = thirdFeatureSelect.selectize({
                ...selectizeConfig,
                placeholder: thirdFeatureSelect.attr('placeholder') || gettext('Select third featured article'),
            })[0].selectize;
        }

        // Add event listeners for closing others on open
        if (firstSelectize) firstSelectize.on('open', () => closeOthers(firstSelectize));
        if (secondSelectize) secondSelectize.on('open', () => closeOthers(secondSelectize));
        if (thirdSelectize) thirdSelectize.on('open', () => closeOthers(thirdSelectize));

        // Also bind direct DOM handlers on the control and input for reliability
        function bindControlHandlers(s) {
            if (!s || !s.$control) return;
            // Use mousedown to catch the opening interaction before document click
            s.$control.on('mousedown.featured', function (e) {
                // Close others before this one toggles
                closeOthers(s);
            });
            // Ensure focusing the input also closes others
            const $input = s.$control.find('input');
            if ($input && $input.length) {
                $input.on('focus.featured', function () {
                    closeOthers(s);
                });
            }
        }

        bindControlHandlers(firstSelectize);
        bindControlHandlers(secondSelectize);
        bindControlHandlers(thirdSelectize);

        // Also add data attribute on control for delegated handlers
        function setControlDataAttr(s, selector) {
            try {
                if (s && s.$control && selector) {
                    s.$control.attr('data-featured-for', selector);
                }
            } catch (err) {
                // ignore if setting attribute fails
            }
        }

        setControlDataAttr(firstSelectize, '#id_first_feature');
        setControlDataAttr(secondSelectize, '#id_second_feature');
        setControlDataAttr(thirdSelectize, '#id_third_feature');

        // Delegated handlers - more reliable in complex DOMs
        jQuery(document).on('mousedown.featured', '[data-featured-for]', function (e) {
            var sel = jQuery(this).attr('data-featured-for');
            var inst = window.getFeaturedSelectizeInstance(sel);
            if (inst) {
                closeOthers(inst);
            }
        });

        jQuery(document).on('focusin.featured', '[data-featured-for] input', function (e) {
            var $control = jQuery(this).closest('[data-featured-for]');
            var sel = $control.attr('data-featured-for');
            var inst = window.getFeaturedSelectizeInstance(sel);
            if (inst) {
                closeOthers(inst);
            }
        });

        // Add document click listener for closing on outside click
        document.addEventListener('click', handleDocumentClick);
    }

    /**
     * Utility function to get selectize instance
     * @param {string} selector - CSS selector for the select element
     * @returns {object|null} Selectize instance or null
     */
    window.getFeaturedSelectizeInstance = function (selector) {
        const element = jQuery(selector)[0];
        return element ? element.selectize : null;
    };

    /**
     * Utility function to destroy and reinitialize selectize
     * Useful for dynamic form updates
     * @param {string} selector - CSS selector for the select element
     */
    window.refreshFeaturedSelectize = function (selector) {
        const selectize = window.getFeaturedSelectizeInstance(selector);
        if (selectize) {
            selectize.destroy();
            initializeFeaturedSelectize();
        }
    };

})();
