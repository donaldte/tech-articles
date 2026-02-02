/**
 * CRUD Operations Manager for Dashboard
 * Handles delete confirmations and AJAX operations
 */

class CrudManager {
    constructor() {
        this.deleteModal = null;
        this.deleteForm = null;
        this.init();
    }

    init() {
        this.bindDeleteButtons();
    }

    /**
     * Bind click events to delete buttons
     */
    bindDeleteButtons() {
        document.querySelectorAll('[data-delete-action]').forEach(button => {
            button.addEventListener('click', (e) => this.handleDeleteClick(e));
        });
    }

    /**
     * Handle delete button click
     * @param {Event} e - Click event
     */
    handleDeleteClick(e) {
        const button = e.currentTarget;
        const itemId = button.dataset.itemId;
        const itemName = button.dataset.itemName;
        const deleteUrl = button.dataset.deleteUrl;
        const modalId = button.dataset.modalTarget || 'delete-modal';

        this.showDeleteModal(modalId, itemId, itemName, deleteUrl);
    }

    /**
     * Show delete confirmation modal
     * @param {string} modalId - Modal element ID
     * @param {string} itemId - Item ID to delete
     * @param {string} itemName - Item name for display
     * @param {string} deleteUrl - URL for delete action
     */
    showDeleteModal(modalId, itemId, itemName, deleteUrl) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        const nameElement = modal.querySelector('[data-delete-item-name]');
        const form = modal.querySelector('form');

        if (nameElement) {
            nameElement.textContent = `"${itemName}"`;
        }

        if (form && deleteUrl) {
            form.action = deleteUrl;
        }
    }

    /**
     * Perform AJAX delete operation
     * @param {string} url - Delete URL
     * @param {string} csrfToken - CSRF token
     * @returns {Promise} - Fetch promise
     */
    async deleteItem(url, csrfToken) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                },
            });

            return await response.json();
        } catch (error) {
            console.error('Delete operation failed:', error);
            throw error;
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.crudManager = new CrudManager();
});
