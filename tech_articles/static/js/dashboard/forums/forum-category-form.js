/**
 * ForumCategoryForm — handles interactive behaviour on the
 * forum category create / edit form.
 *
 * Depends on Django's JavaScriptCatalog (gettext) for i18n.
 *
 * @class
 */
class ForumCategoryForm {
  constructor() {
    this._init();
  }

  /** Bind all event listeners. */
  _init() {
    this._setupPurchasableToggle();
  }

  /**
   * Toggle visibility of purchase price / currency fields
   * based on the "Is Purchasable" checkbox.
   */
  _setupPurchasableToggle() {
    const checkbox = document.querySelector('[data-toggle-target="purchase-fields"]');
    const target = document.getElementById('purchase-fields');
    if (!checkbox || !target) return;

    const toggle = () => {
      if (checkbox.checked) {
        target.classList.remove('hidden');
      } else {
        target.classList.add('hidden');
      }
    };

    // Set initial state
    toggle();
    checkbox.addEventListener('change', toggle);
  }
}

// Initialise on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.forumCategoryForm = new ForumCategoryForm();
});
