/**
 * Plan Form Manager
 * Handles plan features data parsing for create and edit forms
 */

(function() {
    'use strict';
    
    /**
     * Parse plan features data from JSON script element
     */
    function parsePlanFeatures() {
        const planFeaturesElement = document.getElementById('plan-features-data');
        
        if (planFeaturesElement) {
            try {
                window.planFeatures = JSON.parse(planFeaturesElement.textContent);
            } catch (error) {
                console.error('Failed to parse plan features data:', error);
                window.planFeatures = [];  // Fallback to empty array
            }
        } else {
            // No features data available (e.g., on create form)
            window.planFeatures = [];
        }
    }
    
    // Execute when DOM is ready, or immediately if already loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', parsePlanFeatures);
    } else {
        parsePlanFeatures();
    }
})();
