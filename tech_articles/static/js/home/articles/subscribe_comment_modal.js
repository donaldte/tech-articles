/**
 * subscribe_comment_modal.js
 * ---------------------------------------------------
 * Handles the "Subscribe / Comment" modal for the
 * article preview page.
 *
 * Requires:
 *   - Flowbite v3 (already included globally)
 *   - The modal markup: #subscribeCommentModal
 *
 * Triggered by:
 *   - [data-trigger="subscribe-modal"] — comment & heart buttons
 * ---------------------------------------------------
 */

(function () {
  'use strict';

  /**
   * Initialise Flowbite Modal instance and bind all triggers / close actions.
   */
  function initSubscribeCommentModal() {
    const modalEl = document.getElementById('subscribeCommentModal');

    if (!modalEl) {
      return; // Modal markup not present on this page — bail out.
    }

    // ── Flowbite v3 Modal instance ──────────────────────────────────────────
    const modal = new Modal(modalEl, {
      placement: 'center',
      backdrop: 'dynamic',             // click outside closes the modal
      backdropClasses:
        'bg-black/60 fixed inset-0 z-99998 backdrop-blur-[2px]',
      closable: true,                  // Escape key closes the modal
    });

    // ── Open triggers (comment button, heart/like button) ───────────────────
    const triggers = document.querySelectorAll(
      '[data-trigger="subscribe-modal"]'
    );

    triggers.forEach(function (trigger) {
      trigger.addEventListener('click', function (e) {
        e.preventDefault();
        modal.show();
      });
    });

    // ── Internal close button ───────────────────────────────────────────────
    const closeBtn = document.getElementById('subscribeCommentModalClose');

    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        modal.hide();
      });
    }

    // ── Expose instance on window for external usage if needed ──────────────
    window.subscribeCommentModal = modal;
  }

  // ── Bootstrap after DOM is ready ──────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSubscribeCommentModal);
  } else {
    initSubscribeCommentModal();
  }
})();
