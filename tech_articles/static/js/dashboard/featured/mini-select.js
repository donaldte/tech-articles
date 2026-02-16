/**
 * MiniSelect - A lightweight, customizable select component
 *
 * A vanilla JavaScript select library with support for single/multi-select,
 * search/filtering, keyboard navigation, and full accessibility.
 *
 * Features:
 * - No dependencies (pure vanilla JavaScript)
 * - Single and multi-select modes
 * - Search/filtering with highlighting
 * - Remove selected items with button
 * - Keyboard navigation (Arrow keys, Enter, Escape, Tab, Backspace)
 * - Full ARIA support for accessibility
 * - Internationalization with Django's gettext
 * - Responsive design with Tailwind CSS
 *
 * @author Tech Articles Team
 * @version 1.0.0
 */

class MiniSelect {
    /**
     * Initialize MiniSelect
     * @param {HTMLSelectElement|string} element - The select element or selector
     * @param {Object} options - Configuration options
     * @param {boolean} options.multiple - Enable multiple selection
     * @param {string} options.placeholder - Placeholder text
     * @param {boolean} options.search - Enable search/filtering
     * @param {number} options.maxItems - Maximum items to select (for multiple mode)
     * @param {boolean} options.closeAfterSelect - Close dropdown after selection
     * @param {Function} options.onChange - Callback when selection changes
     * @param {Function} options.onOpen - Callback when dropdown opens
     * @param {Function} options.onClose - Callback when dropdown closes
     */
    constructor(element, options = {}) {
        // Get the select element
        this.selectElement = typeof element === 'string' 
            ? document.querySelector(element) 
            : element;

        if (!this.selectElement || this.selectElement.tagName !== 'SELECT') {
            throw new Error('MiniSelect requires a valid select element');
        }

        // Configuration
        this.options = {
            multiple: this.selectElement.multiple || false,
            placeholder: options.placeholder || this.selectElement.getAttribute('placeholder') || gettext('Select an option...'),
            search: options.search !== false, // Default true
            maxItems: options.maxItems || null,
            closeAfterSelect: options.closeAfterSelect !== false, // Default true
            onChange: options.onChange || null,
            onOpen: options.onOpen || null,
            onClose: options.onClose || null,
        };

        // State
        this.isOpen = false;
        this.searchTerm = '';
        this.selectedValues = [];
        this.focusedIndex = -1;
        this.filteredOptions = [];

        // DOM elements (to be created)
        this.wrapper = null;
        this.control = null;
        this.valueContainer = null;
        this.searchInput = null;
        this.dropdown = null;
        this.optionsList = null;

        // Bind methods
        this.handleDocumentClick = this.handleDocumentClick.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleSearchInput = this.handleSearchInput.bind(this);

        // Initialize
        this.init();
    }

    /**
     * Initialize the component
     */
    init() {
        // Hide the original select
        this.selectElement.style.display = 'none';

        // Build the custom select UI
        this.buildUI();

        // Load initial values
        this.syncFromSelect();

        // Bind events
        this.bindEvents();

        // Mark as initialized
        this.selectElement.classList.add('mini-select-initialized');
    }

    /**
     * Build the custom select UI
     */
    buildUI() {
        // Create wrapper
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'mini-select-wrapper';
        this.selectElement.parentNode.insertBefore(this.wrapper, this.selectElement);
        this.wrapper.appendChild(this.selectElement);

        // Create control (the visible part)
        this.control = document.createElement('div');
        this.control.className = 'mini-select-control';
        this.control.setAttribute('role', 'combobox');
        this.control.setAttribute('aria-expanded', 'false');
        this.control.setAttribute('aria-haspopup', 'listbox');
        this.control.setAttribute('tabindex', '0');
        this.wrapper.appendChild(this.control);

        // Create value container
        this.valueContainer = document.createElement('div');
        this.valueContainer.className = 'mini-select-value-container';
        this.control.appendChild(this.valueContainer);

        // Create search input
        this.searchInput = document.createElement('input');
        this.searchInput.type = 'text';
        this.searchInput.className = 'mini-select-search';
        this.searchInput.setAttribute('aria-label', gettext('Search options'));
        this.searchInput.setAttribute('aria-autocomplete', 'list');
        this.searchInput.setAttribute('autocomplete', 'off');
        this.searchInput.setAttribute('tabindex', '-1');
        this.valueContainer.appendChild(this.searchInput);

        // Create dropdown arrow
        const arrow = document.createElement('div');
        arrow.className = 'mini-select-arrow';
        arrow.innerHTML = '<svg width="12" height="8" viewBox="0 0 12 8" fill="none"><path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        arrow.setAttribute('aria-hidden', 'true');
        this.control.appendChild(arrow);

        // Create dropdown
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'mini-select-dropdown';
        this.dropdown.style.display = 'none';
        this.wrapper.appendChild(this.dropdown);

        // Create options list
        this.optionsList = document.createElement('ul');
        this.optionsList.className = 'mini-select-options';
        this.optionsList.setAttribute('role', 'listbox');
        if (this.options.multiple) {
            this.optionsList.setAttribute('aria-multiselectable', 'true');
        }
        this.dropdown.appendChild(this.optionsList);

        // Create no results message
        this.noResults = document.createElement('div');
        this.noResults.className = 'mini-select-no-results';
        this.noResults.textContent = gettext('No results found');
        this.noResults.style.display = 'none';
        this.dropdown.appendChild(this.noResults);
    }

    /**
     * Synchronize from the original select element
     */
    syncFromSelect() {
        // Clear current selections
        this.selectedValues = [];

        // Get selected options from select element
        const selectedOptions = Array.from(this.selectElement.selectedOptions);
        this.selectedValues = selectedOptions.map(opt => opt.value);

        // Render the current state
        this.render();
    }

    /**
     * Synchronize to the original select element
     */
    syncToSelect() {
        // Update select element's selected options
        Array.from(this.selectElement.options).forEach(option => {
            option.selected = this.selectedValues.includes(option.value);
        });

        // Trigger change event on select element
        const event = new Event('change', { bubbles: true });
        this.selectElement.dispatchEvent(event);

        // Call onChange callback if provided
        if (this.options.onChange) {
            this.options.onChange(this.selectedValues);
        }
    }

    /**
     * Render the component
     */
    render() {
        this.renderValue();
        this.renderOptions();
    }

    /**
     * Render the selected value(s)
     */
    renderValue() {
        // Clear value container except search input
        while (this.valueContainer.firstChild && this.valueContainer.firstChild !== this.searchInput) {
            this.valueContainer.removeChild(this.valueContainer.firstChild);
        }

        if (this.selectedValues.length === 0) {
            // Show placeholder
            const placeholder = document.createElement('div');
            placeholder.className = 'mini-select-placeholder';
            placeholder.textContent = this.options.placeholder;
            this.valueContainer.insertBefore(placeholder, this.searchInput);
            this.searchInput.style.display = 'none';
        } else if (this.options.multiple) {
            // Show selected items as tags
            this.searchInput.style.display = '';
            this.selectedValues.forEach(value => {
                const option = Array.from(this.selectElement.options).find(opt => opt.value === value);
                if (option) {
                    const tag = this.createTag(value, option.text);
                    this.valueContainer.insertBefore(tag, this.searchInput);
                }
            });
        } else {
            // Show single selected value
            const option = Array.from(this.selectElement.options).find(opt => opt.value === this.selectedValues[0]);
            if (option) {
                const singleValue = document.createElement('div');
                singleValue.className = 'mini-select-single-value';
                singleValue.textContent = option.text;
                this.valueContainer.insertBefore(singleValue, this.searchInput);
            }
            this.searchInput.style.display = 'none';
        }

        // Show/hide search input based on state
        if (this.isOpen && this.options.search) {
            this.searchInput.style.display = '';
            this.searchInput.focus();
        }
    }

    /**
     * Create a tag element for multi-select
     * @param {string} value - Option value
     * @param {string} text - Option text
     * @returns {HTMLElement} Tag element
     */
    createTag(value, text) {
        const tag = document.createElement('div');
        tag.className = 'mini-select-tag';
        tag.setAttribute('data-value', value);

        const tagText = document.createElement('span');
        tagText.className = 'mini-select-tag-text';
        tagText.textContent = text;
        tag.appendChild(tagText);

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'mini-select-tag-remove';
        removeBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M9 3L3 9M3 3L9 9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
        removeBtn.setAttribute('aria-label', interpolate(gettext('Remove %s'), [text]));
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeValue(value);
            // Open dropdown after removal for multi-select as per requirements
            if (this.options.multiple && !this.isOpen) {
                this.open();
            }
        });
        tag.appendChild(removeBtn);

        return tag;
    }

    /**
     * Render options in dropdown
     */
    renderOptions() {
        // Clear options list
        this.optionsList.innerHTML = '';

        // Get options from select element
        const options = Array.from(this.selectElement.options);

        // Filter options based on search term
        this.filteredOptions = options.filter(option => {
            if (!option.value) return false; // Skip empty options
            if (!this.searchTerm) return true;
            return option.text.toLowerCase().includes(this.searchTerm.toLowerCase());
        });

        // Show no results message if needed
        if (this.filteredOptions.length === 0) {
            this.noResults.style.display = 'block';
            this.optionsList.style.display = 'none';
            return;
        } else {
            this.noResults.style.display = 'none';
            this.optionsList.style.display = '';
        }

        // Render filtered options
        this.filteredOptions.forEach((option, index) => {
            const li = document.createElement('li');
            li.className = 'mini-select-option';
            li.setAttribute('role', 'option');
            li.setAttribute('data-value', option.value);
            li.setAttribute('tabindex', '-1');

            // Highlight search term (safely)
            if (this.searchTerm) {
                // Escape special regex characters in search term
                const escapedTerm = this.searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const regex = new RegExp(`(${escapedTerm})`, 'gi');
                const parts = option.text.split(regex);
                
                // Build the highlighted content safely
                parts.forEach((part, idx) => {
                    if (idx % 2 === 1) {
                        // This is a match
                        const mark = document.createElement('mark');
                        mark.textContent = part;
                        li.appendChild(mark);
                    } else {
                        // Regular text
                        li.appendChild(document.createTextNode(part));
                    }
                });
            } else {
                li.textContent = option.text;
            }

            // Mark selected
            if (this.selectedValues.includes(option.value)) {
                li.classList.add('mini-select-option-selected');
                li.setAttribute('aria-selected', 'true');
            } else {
                li.setAttribute('aria-selected', 'false');
            }

            // Mark focused
            if (index === this.focusedIndex) {
                li.classList.add('mini-select-option-focused');
            }

            // Click handler
            li.addEventListener('click', () => {
                this.selectOption(option.value);
            });

            this.optionsList.appendChild(li);
        });
    }

    /**
     * Select an option
     * @param {string} value - Option value to select
     */
    selectOption(value) {
        if (this.options.multiple) {
            // Toggle selection in multiple mode
            if (this.selectedValues.includes(value)) {
                this.removeValue(value);
            } else {
                // Check max items limit
                if (this.options.maxItems && this.selectedValues.length >= this.options.maxItems) {
                    return;
                }
                this.selectedValues.push(value);
            }
        } else {
            // Single selection
            this.selectedValues = [value];
            if (this.options.closeAfterSelect) {
                this.close();
            }
        }

        // Sync and render
        this.syncToSelect();
        this.render();
    }

    /**
     * Remove a selected value
     * @param {string} value - Value to remove
     */
    removeValue(value) {
        this.selectedValues = this.selectedValues.filter(v => v !== value);
        this.syncToSelect();
        this.render();
    }

    /**
     * Clear all selections
     */
    clear() {
        this.selectedValues = [];
        this.syncToSelect();
        this.render();
    }

    /**
     * Open the dropdown
     */
    open() {
        if (this.isOpen) return;

        this.isOpen = true;
        this.dropdown.style.display = 'block';
        this.control.classList.add('mini-select-control-open');
        this.control.setAttribute('aria-expanded', 'true');

        // Reset search
        this.searchTerm = '';
        this.searchInput.value = '';
        this.focusedIndex = -1;

        // Render
        this.render();

        // Focus search input if enabled
        if (this.options.search) {
            this.searchInput.focus();
        }

        // Call onOpen callback
        if (this.options.onOpen) {
            this.options.onOpen();
        }

        // Add document click listener
        setTimeout(() => {
            document.addEventListener('click', this.handleDocumentClick);
        }, 0);
    }

    /**
     * Close the dropdown
     */
    close() {
        if (!this.isOpen) return;

        this.isOpen = false;
        this.dropdown.style.display = 'none';
        this.control.classList.remove('mini-select-control-open');
        this.control.setAttribute('aria-expanded', 'false');

        // Reset search
        this.searchTerm = '';
        this.searchInput.value = '';
        this.focusedIndex = -1;

        // Render
        this.render();

        // Remove document click listener
        document.removeEventListener('click', this.handleDocumentClick);

        // Call onClose callback
        if (this.options.onClose) {
            this.options.onClose();
        }
    }

    /**
     * Toggle dropdown open/close
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Control click to toggle dropdown
        this.control.addEventListener('click', (e) => {
            // Don't toggle if clicking remove button
            if (e.target.closest('.mini-select-tag-remove')) {
                return;
            }
            this.toggle();
        });

        // Control keyboard navigation
        this.control.addEventListener('keydown', this.handleKeyDown);

        // Search input
        if (this.options.search) {
            this.searchInput.addEventListener('input', this.handleSearchInput);
            this.searchInput.addEventListener('keydown', this.handleKeyDown);
        }
    }

    /**
     * Handle document click (close dropdown when clicking outside)
     * @param {Event} e - Click event
     */
    handleDocumentClick(e) {
        if (!this.wrapper.contains(e.target)) {
            this.close();
        }
    }

    /**
     * Handle keyboard navigation
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeyDown(e) {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (!this.isOpen) {
                    this.open();
                } else {
                    this.focusedIndex = Math.min(this.focusedIndex + 1, this.filteredOptions.length - 1);
                    this.renderOptions();
                    this.scrollToFocused();
                }
                break;

            case 'ArrowUp':
                e.preventDefault();
                if (this.isOpen) {
                    this.focusedIndex = Math.max(this.focusedIndex - 1, 0);
                    this.renderOptions();
                    this.scrollToFocused();
                }
                break;

            case 'Enter':
                e.preventDefault();
                if (this.isOpen && this.focusedIndex >= 0 && this.filteredOptions[this.focusedIndex]) {
                    this.selectOption(this.filteredOptions[this.focusedIndex].value);
                } else if (!this.isOpen) {
                    this.open();
                }
                break;

            case 'Escape':
                e.preventDefault();
                if (this.isOpen) {
                    this.close();
                }
                break;

            case 'Tab':
                if (this.isOpen) {
                    this.close();
                }
                break;

            case 'Backspace':
                // Remove last selected item when backspace on empty search
                if (this.options.multiple && this.searchInput.value === '' && this.selectedValues.length > 0) {
                    e.preventDefault();
                    const lastValue = this.selectedValues[this.selectedValues.length - 1];
                    this.removeValue(lastValue);
                }
                break;
        }
    }

    /**
     * Handle search input
     * @param {Event} e - Input event
     */
    handleSearchInput(e) {
        this.searchTerm = e.target.value;
        this.focusedIndex = -1;
        this.renderOptions();
    }

    /**
     * Scroll focused option into view
     */
    scrollToFocused() {
        const focusedElement = this.optionsList.querySelector('.mini-select-option-focused');
        if (focusedElement) {
            focusedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    /**
     * Destroy the component and restore original select
     */
    destroy() {
        // Remove event listeners
        document.removeEventListener('click', this.handleDocumentClick);

        // Remove custom UI
        if (this.wrapper && this.wrapper.parentNode) {
            this.wrapper.parentNode.insertBefore(this.selectElement, this.wrapper);
            this.wrapper.remove();
        }

        // Show original select
        this.selectElement.style.display = '';
        this.selectElement.classList.remove('mini-select-initialized');
    }

    /**
     * Get selected value(s)
     * @returns {string|string[]} Selected value(s)
     */
    getValue() {
        return this.options.multiple ? this.selectedValues : this.selectedValues[0] || null;
    }

    /**
     * Set value(s)
     * @param {string|string[]} value - Value(s) to set
     */
    setValue(value) {
        if (this.options.multiple) {
            this.selectedValues = Array.isArray(value) ? value : [value];
        } else {
            this.selectedValues = value ? [value] : [];
        }
        this.syncToSelect();
        this.render();
    }

    /**
     * Refresh options from select element
     */
    refresh() {
        this.syncFromSelect();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MiniSelect;
}
