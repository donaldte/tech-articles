/**
 * ForumCategoryManager — handles category list interactions (delete with
 * cascade confirmation, modal management, AJAX operations).
 *
 * Depends on Django's JavaScriptCatalog (gettext / ngettext) for i18n
 * and the global ToastManager instance (window.toastManager).
 *
 * @class
 */
class ForumCategoryManager {
  /**
   * @param {Object} options
   * @param {string} [options.modalId='delete-category-modal'] - Delete modal element ID.
   * @param {string} [options.deleteBtnSelector='.js-delete-category-btn'] - Selector for delete buttons.
   */
  constructor(options = {}) {
    this.modalId = options.modalId || 'delete-category-modal';
    this.deleteBtnSelector = options.deleteBtnSelector || '.js-delete-category-btn';

    /** @type {HTMLElement|null} */
    this.modal = document.getElementById(this.modalId);
    /** @type {string|null} Current delete URL */
    this._deleteUrl = null;
    /** @type {boolean} Prevents double-submit */
    this._isDeleting = false;

    this._init();
  }

  /* ------------------------------------------------------------------
   * Initialisation
   * ----------------------------------------------------------------*/

  /** Bind all event listeners. */
  _init() {
    if (!this.modal) return;

    // Delete trigger buttons
    document.querySelectorAll(this.deleteBtnSelector).forEach((btn) => {
      btn.addEventListener('click', (e) => this._onDeleteClick(e));
    });

    // Modal close buttons
    this.modal.querySelectorAll('.js-modal-close').forEach((btn) => {
      btn.addEventListener('click', () => this._closeModal());
    });

    // Overlay click → close
    const overlay = this.modal.querySelector('.js-modal-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => this._closeModal());
    }

    // Escape key → close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
        this._closeModal();
      }
    });

    // Confirm delete
    const confirmBtn = this.modal.querySelector('.js-confirm-delete');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', () => this._performDelete());
    }
  }

  /* ------------------------------------------------------------------
   * Modal helpers
   * ----------------------------------------------------------------*/

  /** Open the delete modal with animation. */
  _openModal() {
    this.modal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
  }

  /** Close the delete modal. */
  _closeModal() {
    this.modal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    this._deleteUrl = null;
    this._resetDeleteButton();
  }

  /* ------------------------------------------------------------------
   * Delete flow
   * ----------------------------------------------------------------*/

  /**
   * Handle click on a delete button: fetch category info (thread count)
   * then show the appropriate confirmation modal.
   *
   * @param {Event} e
   */
  async _onDeleteClick(e) {
    const btn = e.currentTarget;
    const deleteUrl = btn.dataset.deleteUrl;
    const categoryName = btn.dataset.categoryName;

    this._deleteUrl = deleteUrl;

    // Pre-populate the modal immediately with the name
    const nameEl = this.modal.querySelector('#delete-modal-category-name');
    const messageEl = this.modal.querySelector('#delete-modal-message');
    const cascadeWarning = this.modal.querySelector('#delete-modal-cascade-warning');
    const cascadeText = this.modal.querySelector('#delete-modal-cascade-text');

    if (nameEl) nameEl.textContent = `"${categoryName}"`;
    if (messageEl) messageEl.textContent = gettext('Are you sure you want to delete');
    if (cascadeWarning) cascadeWarning.classList.add('hidden');

    // Fetch thread count via AJAX GET
    try {
      const response = await fetch(deleteUrl, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });

      if (response.ok) {
        const data = await response.json();

        if (data.thread_count > 0) {
          const warningMsg = ngettext(
            'This category contains %s thread that will also be permanently deleted.',
            'This category contains %s threads that will also be permanently deleted.',
            data.thread_count
          );
          if (cascadeText) cascadeText.textContent = interpolate(warningMsg, [data.thread_count]);
          if (cascadeWarning) cascadeWarning.classList.remove('hidden');
        }
      }
    } catch {
      // If the pre-check fails we still show the modal without cascade info
    }

    this._openModal();
  }

  /**
   * Execute the delete via POST (AJAX).
   */
  async _performDelete() {
    if (this._isDeleting || !this._deleteUrl) return;

    this._isDeleting = true;
    this._setDeleteLoading(true);

    const csrfToken = this._getCsrfToken();

    try {
      const response = await fetch(this._deleteUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        this._closeModal();
        this._showToast(data.message || gettext('Category deleted successfully.'), 'success');
        // Remove the table row and reload after a short delay
        setTimeout(() => { window.location.reload(); }, 800);
      } else {
        this._showToast(data.message || gettext('An error occurred while deleting.'), 'danger');
        this._setDeleteLoading(false);
        this._isDeleting = false;
      }
    } catch {
      this._showToast(gettext('Network error. Please try again.'), 'danger');
      this._setDeleteLoading(false);
      this._isDeleting = false;
    }
  }

  /* ------------------------------------------------------------------
   * UI helpers
   * ----------------------------------------------------------------*/

  /**
   * Toggle loading state on the delete confirmation button.
   *
   * @param {boolean} loading
   */
  _setDeleteLoading(loading) {
    const btn = this.modal.querySelector('.js-confirm-delete');
    if (!btn) return;

    const textEl = btn.querySelector('.js-delete-text');
    const loadingEl = btn.querySelector('.js-delete-loading');

    if (loading) {
      if (textEl) textEl.classList.add('hidden');
      if (loadingEl) loadingEl.classList.remove('hidden');
      btn.disabled = true;
    } else {
      if (textEl) textEl.classList.remove('hidden');
      if (loadingEl) loadingEl.classList.add('hidden');
      btn.disabled = false;
    }
  }

  /** Reset the delete button state when the modal is closed. */
  _resetDeleteButton() {
    this._isDeleting = false;
    this._setDeleteLoading(false);
  }

  /**
   * Show a toast notification using the global ToastManager.
   *
   * @param {string} message
   * @param {string} type - 'success' | 'danger' | 'warning' | 'info'
   */
  _showToast(message, type) {
    if (window.toastManager) {
      window.toastManager.buildToast()
        .setMessage(message)
        .setType(type)
        .setPosition('top-right')
        .setDuration(4000)
        .show();
    }
  }

  /**
   * Retrieve the CSRF token from the cookie.
   *
   * @returns {string}
   */
  _getCsrfToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + '=')) {
        return decodeURIComponent(trimmed.substring(name.length + 1));
      }
    }
    return '';
  }
}

// Initialise on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.forumCategoryManager = new ForumCategoryManager();
});
