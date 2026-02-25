/**
 * Purchase checkout page — payment tab switcher and double-submit protection.
 * Depends on Tailwind CSS classes and Django i18n (gettext loaded via javascript-catalog).
 */
(function () {
  'use strict';

  // ── Tab switcher ──────────────────────────────────────────────────────────
  const tabs = document.querySelectorAll('.payment-tab');
  const panels = document.querySelectorAll('.tab-panel');

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      const target = tab.dataset.tab;

      tabs.forEach(function (t) {
        t.classList.remove('active');
      });
      tab.classList.add('active');

      panels.forEach(function (p) {
        p.classList.add('hidden');
      });

      const panel = document.getElementById('tab-' + target);
      if (panel) {
        panel.classList.remove('hidden');
      }
    });
  });

  // ── Double-submit / double-click protection ───────────────────────────────
  const forms = document.querySelectorAll('#purchase-form-card, #purchase-form-paypal');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (!submitBtn) return;

      if (submitBtn.dataset.submitting === 'true') {
        e.preventDefault();
        return;
      }

      submitBtn.dataset.submitting = 'true';
      submitBtn.disabled = true;

      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML =
        '<svg class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">' +
        '<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>' +
        '<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>' +
        '</svg>' +
        (typeof gettext !== 'undefined' ? gettext('Processing...') : 'Processing...');

      // Re-enable after 15 seconds as fallback (e.g. if redirect fails)
      setTimeout(function () {
        submitBtn.disabled = false;
        submitBtn.dataset.submitting = 'false';
        submitBtn.innerHTML = originalText;
      }, 15000);
    });
  });
})();
