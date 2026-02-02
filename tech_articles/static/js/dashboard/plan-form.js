/**
 * Plan Form Manager
 * Handles plan features data parsing for create and edit forms
 */

document.addEventListener('DOMContentLoaded', () => {
    // Parse plan features from server-side JSON using json_script to prevent XSS
    // json_script handles serialization automatically, converting Python types properly
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
});
