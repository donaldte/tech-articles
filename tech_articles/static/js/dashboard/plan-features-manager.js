/**
 * PlanFeaturesManager - Manages dynamic plan features on plan create/edit forms
 *
 * This module provides a clean interface for managing plan features:
 * - Add new features dynamically
 * - Remove features
 * - Toggle feature inclusion
 * - Serialize features to JSON for form submission
 */

class PlanFeaturesManager {
    constructor(options = {}) {
        this.containerId = options.containerId || 'plan-features-container';
        this.inputId = options.inputId || 'features_json';
        this.features = options.initialFeatures || [];

        this.container = document.getElementById(this.containerId);
        this.input = document.getElementById(this.inputId);

        if (!this.container) {
            console.error(`Container with ID "${this.containerId}" not found`);
            return;
        }

        this.init();
    }

    /**
     * Initialize the manager
     */
    init() {
        this.render();
        this.attachEventListeners();

        // Update hidden input on form submit
        const form = this.container.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                this.updateHiddenInput();
            });
        }
    }

    /**
     * Add a new feature
     */
    addFeature() {
        const feature = {
            id: null,
            name: '',
            display_order: this.features.length,
            is_included: true,
        };

        this.features.push(feature);
        this.render();
    }

    /**
     * Remove a feature by index
     */
    removeFeature(index) {
        this.features.splice(index, 1);
        this.render();
    }

    /**
     * Update a feature field
     */
    updateFeature(index, field, value) {
        if (this.features[index]) {
            this.features[index][field] = value;
            this.updateHiddenInput();
        }
    }

    /**
     * Toggle feature inclusion
     */
    toggleFeatureInclusion(index) {
        if (this.features[index]) {
            this.features[index].is_included = !this.features[index].is_included;
            this.render();
        }
    }

    /**
     * Render all features
     */
    render() {
        // Clear container
        this.container.innerHTML = '';

        if (this.features.length === 0) {
            this.renderEmptyState();
            return;
        }

        // Render each feature
        this.features.forEach((feature, index) => {
            const featureElement = this.createFeatureElement(feature, index);
            this.container.appendChild(featureElement);
        });

        this.updateHiddenInput();
    }

    /**
     * Render empty state
     */
    renderEmptyState() {
        const emptyState = document.createElement('div');
        emptyState.className = 'text-center py-8 text-text-muted';
        emptyState.innerHTML = `
            <svg class="w-12 h-12 mx-auto mb-3 text-text-muted/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <p class="text-sm">${gettext('No features added yet. Click the button below to add one.')}</p>
        `;
        this.container.appendChild(emptyState);
    }

    /**
     * Create a feature element
     */
    createFeatureElement(feature, index) {
        const div = document.createElement('div');
        div.className = 'feature-item border border-border-dark rounded-lg p-4 mb-3 bg-background-secondary';
        div.setAttribute('data-index', index);

        div.innerHTML = `
            <div class="flex items-start gap-3">
                <!-- Inclusion Toggle -->
                <div class="flex-shrink-0 pt-2">
                    <button type="button"
                            class="inclusion-toggle w-6 h-6 rounded flex items-center justify-center transition-colors ${feature.is_included ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}"
                            data-index="${index}"
                            title="${feature.is_included ? gettext('Included') : gettext('Excluded')}">
                        ${feature.is_included
                            ? '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>'
                            : '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>'
                        }
                    </button>
                </div>

                <!-- Feature Fields -->
                <div class="flex-grow space-y-3">
                    <div>
                        <label class="block text-text-muted text-xs font-medium mb-1">
                            ${gettext('Feature name')}
                        </label>
                        <input type="text"
                               class="feature-name dashboard-input w-full"
                               placeholder="${gettext('Enter feature name')}"
                               value="${this.escapeHtml(feature.name)}"
                               data-index="${index}"
                               required>
                    </div>
                    <div>
                        <label class="block text-text-muted text-xs font-medium mb-1">
                            ${gettext('Display order')}
                        </label>
                        <input type="number"
                               class="feature-order dashboard-input w-full"
                               placeholder="${gettext('Order in which features are displayed')}"
                               value="${feature.display_order || 0}"
                               data-index="${index}"
                               min="0"
                               inputmode="numeric">
                    </div>
                </div>

                <!-- Remove Button -->
                <div class="flex-shrink-0 pt-2">
                    <button type="button"
                            class="remove-feature text-red-400 hover:text-red-300 transition-colors p-1"
                            data-index="${index}"
                            title="${gettext('Remove')}">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        return div;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Use event delegation for dynamic elements
        this.container.addEventListener('click', (e) => {
            const target = e.target.closest('button');
            if (!target) return;

            const index = parseInt(target.getAttribute('data-index'));

            if (target.classList.contains('remove-feature')) {
                e.preventDefault();
                this.removeFeature(index);
            } else if (target.classList.contains('inclusion-toggle')) {
                e.preventDefault();
                this.toggleFeatureInclusion(index);
            }
        });

        this.container.addEventListener('input', (e) => {
            const target = e.target;
            const index = parseInt(target.getAttribute('data-index'));

            if (target.classList.contains('feature-name')) {
                this.updateFeature(index, 'name', target.value);
            } else if (target.classList.contains('feature-order')) {
                this.updateFeature(index, 'display_order', parseInt(target.value) || 0);
            }
        });
    }

    /**
     * Update hidden input with JSON data
     */
    updateHiddenInput() {
        if (this.input) {
            this.input.value = JSON.stringify(this.features);
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
}
