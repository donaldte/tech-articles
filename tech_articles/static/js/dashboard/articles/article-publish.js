/**
 * Article Publish Manager
 * Handles dynamic publishing of articles without page reload.
 */

(function() {
  'use strict';

  class ArticlePublishManager {
    constructor() {
      this.publishButton = document.querySelector('button[data-article-id]');
      this.articleId = null;
      // Selector constant for status badge
      this.statusBadgeSelector = '[data-status-badge]';
      this.init();
    }

    init() {
      if (!this.publishButton) {
        return;
      }

      this.articleId = this.publishButton.dataset.articleId;

      // Check if article is draft and show/hide button accordingly
      this.checkArticleStatus();

      // Bind event listeners
      this.bindEvents();
    }

    bindEvents() {
      if (this.publishButton) {
        this.publishButton.addEventListener('click', (e) => this.handlePublish(e));
      }
    }

    checkArticleStatus() {
      // Check if the status badge indicates draft
      const statusBadge = document.querySelector(this.statusBadgeSelector);
      if (!statusBadge) {
        return;
      }

      const statusText = statusBadge.textContent.trim().toLowerCase();
      
      // Show publish button only for draft articles
      if (statusText === 'draft' || statusText === 'brouillon') {
        this.publishButton.style.display = 'block';
      } else {
        this.publishButton.style.display = 'none';
      }
    }

    async handlePublish(event) {
      event.preventDefault();

      if (!this.articleId) {
        console.error('Article ID not found');
        return;
      }

      // Get CSRF token
      const csrfToken = this.getCsrfToken();
      if (!csrfToken) {
        console.error('CSRF token not found');
        if (window.toastManager) {
          window.toastManager.buildToast()
            .setMessage(gettext('Security token not found. Please refresh the page.'))
            .setType('error')
            .setPosition('bottom-right')
            .setDuration(5000)
            .show();
        }
        return;
      }

      // Disable button during request
      this.publishButton.disabled = true;
      this.publishButton.textContent = gettext('Publishing...');

      try {
        const response = await fetch(`/dashboard/content/articles/${this.articleId}/api/publish/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
        });

        const data = await response.json();

        if (response.ok && data.success) {
          // Update status badge
          this.updateStatusBadge(data.status);

          // Hide publish button
          this.publishButton.style.display = 'none';

          // Update status select if on details page
          this.updateStatusSelect(data.status);

          // Show success message
          if (window.toastManager) {
            window.toastManager.buildToast()
              .setMessage(data.message || gettext('Article published successfully.'))
              .setType('success')
              .setPosition('bottom-right')
              .setDuration(5000)
              .show();
          }
        } else {
          // Show error message
          if (window.toastManager) {
            window.toastManager.buildToast()
              .setMessage(data.message || gettext('Failed to publish article.'))
              .setType('error')
              .setPosition('bottom-right')
              .setDuration(5000)
              .show();
          }

          // Re-enable button
          this.publishButton.disabled = false;
          this.publishButton.textContent = gettext('Publish Article');
        }
      } catch (error) {
        console.error('Error publishing article:', error);
        
        if (window.toastManager) {
          window.toastManager.buildToast()
            .setMessage(gettext('An error occurred while publishing the article.'))
            .setType('error')
            .setPosition('bottom-right')
            .setDuration(5000)
            .show();
        }

        // Re-enable button
        this.publishButton.disabled = false;
        this.publishButton.textContent = gettext('Publish Article');
      }
    }

    updateStatusBadge(status) {
      const statusBadge = document.querySelector(this.statusBadgeSelector);
      if (!statusBadge) {
        return;
      }

      // Remove all existing classes
      statusBadge.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';

      // Add new classes based on status
      if (status === 'published') {
        statusBadge.classList.add('bg-green-500/20', 'text-green-400', 'border', 'border-green-500/30');
        statusBadge.textContent = gettext('Published');
      } else if (status === 'draft') {
        statusBadge.classList.add('bg-yellow-500/20', 'text-yellow-400', 'border', 'border-yellow-500/30');
        statusBadge.textContent = gettext('Draft');
      } else if (status === 'scheduled') {
        statusBadge.classList.add('bg-blue-500/20', 'text-blue-400', 'border', 'border-blue-500/30');
        statusBadge.textContent = gettext('Scheduled');
      } else {
        statusBadge.classList.add('bg-gray-500/20', 'text-gray-400', 'border', 'border-gray-500/30');
        statusBadge.textContent = gettext('Archived');
      }
    }

    updateStatusSelect(status) {
      // Check if we're on the details page with a status select
      const statusSelect = document.querySelector('select[name="status"]');
      if (statusSelect) {
        statusSelect.value = status;
      }
    }

    getCsrfToken() {
      // Try to get from form field first
      const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
      if (tokenInput && tokenInput.value) {
        const token = tokenInput.value.trim();
        if (token.length === 32 || token.length === 64) {
          return token;
        }
      }

      // Fallback to cookie
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        const trimmedCookie = cookie.trim();
        if (trimmedCookie.startsWith(name + '=')) {
          return trimmedCookie.substring(name.length + 1);
        }
      }

      return null;
    }
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      new ArticlePublishManager();
    });
  } else {
    new ArticlePublishManager();
  }
})();
