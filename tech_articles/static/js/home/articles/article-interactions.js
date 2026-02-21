/**
 * Article Detail Interactions Manager
 * Handles claps, likes, and comments on article detail pages
 */

class ArticleInteractions {
    constructor() {
        this.articleId = null;
        this.init();
    }

    init() {
        // Get article ID from page
        const articleElement = document.querySelector('[data-article-id]');
        if (!articleElement) return;

        this.articleId = articleElement.dataset.articleId;

        // Bind event listeners
        this.bindClapButton();
        this.bindLikeButton();
        this.bindCommentSubmit();
        this.bindCommentLikes();
    }

    bindClapButton() {
        const clapBtn = document.querySelector('[data-action="clap"]');
        if (!clapBtn) return;

        clapBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            try {
                const response = await this.apiCall('POST', window.urls.articleClap(this.articleId));

                if (response.success) {
                    // Update clap count
                    const countEl = document.querySelector('[data-clap-count]');
                    if (countEl) {
                        countEl.textContent = response.total;
                    }

                    // Add animation
                    clapBtn.classList.add('animate-bounce');
                    setTimeout(() => clapBtn.classList.remove('animate-bounce'), 500);
                }
            } catch (error) {
                console.error('Clap error:', error);
                if (error.error) {
                    alert(error.error);
                }
            }
        });
    }

    bindLikeButton() {
        const likeBtn = document.querySelector('[data-action="like"]');
        if (!likeBtn) return;

        likeBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            // Check if auth required
            if (likeBtn.dataset.requireAuth === 'true') {
                alert(gettext('Please log in to like this article.'));
                return;
            }

            try {
                const response = await this.apiCall('POST', window.urls.articleLike(this.articleId));

                if (response.success) {
                    // Update like count
                    const countEl = document.querySelector('[data-like-count]');
                    if (countEl) {
                        countEl.textContent = response.total;
                    }

                    // Toggle liked state
                    if (response.liked) {
                        likeBtn.classList.add('liked');
                    } else {
                        likeBtn.classList.remove('liked');
                    }
                }
            } catch (error) {
                console.error('Like error:', error);
            }
        });
    }

    bindCommentSubmit() {
        const submitBtn = document.querySelector('[data-comment-submit]');
        const textarea = document.querySelector('[data-comment-textarea]');
        const cancelBtn = document.querySelector('[data-comment-cancel]');

        if (!submitBtn || !textarea) return;

        submitBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            const content = textarea.value.trim();
            if (!content) {
                alert(gettext('Please enter a comment.'));
                return;
            }

            try {
                submitBtn.disabled = true;
                submitBtn.textContent = gettext('Posting...');

                const response = await this.apiCall('POST', window.urls.articleComments(this.articleId), {
                    content: content
                });

                if (response.success) {
                    // Clear textarea
                    textarea.value = '';

                    // Add comment to list
                    this.addCommentToList(response.comment);

                    // Update count
                    const countEl = document.querySelector('[data-comment-count]');
                    if (countEl) {
                        const currentCount = parseInt(countEl.textContent) || 0;
                        countEl.textContent = currentCount + 1;
                    }
                }
            } catch (error) {
                console.error('Comment error:', error);
                alert(error.error || gettext('Failed to post comment.'));
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = gettext('Respond');
            }
        });

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                textarea.value = '';
            });
        }
    }

    bindCommentLikes() {
        document.addEventListener('click', async (e) => {
            const likeBtn = e.target.closest('[data-comment-like]');
            if (!likeBtn) return;

            e.preventDefault();

            // Check if auth required
            if (likeBtn.dataset.requireAuth === 'true') {
                alert(gettext('Please log in to like comments.'));
                return;
            }

            const commentId = likeBtn.dataset.commentLike;

            try {
                const response = await this.apiCall('POST', window.urls.articleCommentLike(commentId));

                if (response.success) {
                    // Update like count
                    const countEl = document.querySelector(`[data-comment-like-count="${commentId}"]`);
                    if (countEl) {
                        countEl.textContent = response.total;
                    }

                    // Toggle liked state
                    if (response.liked) {
                        likeBtn.classList.add('liked');
                    } else {
                        likeBtn.classList.remove('liked');
                    }
                }
            } catch (error) {
                console.error('Comment like error:', error);
            }
        });
    }

    addCommentToList(comment) {
        const commentsList = document.querySelector('[data-comments-list]');
        if (!commentsList) return;

        const commentHTML = `
      <div class="article-comment-item" data-comment-id="${comment.id}">
        <div class="article-comment-avatar-col">
          <div class="article-avatar-placeholder" style="background-color: #4B5563;">
            <span>${(comment.user.name || comment.user.email).charAt(0).toUpperCase()}</span>
          </div>
        </div>
        <div class="article-comment-body">
          <div class="article-comment-header">
            <span class="article-comment-author">${(comment.user.name || comment.user.email)}</span>
            <span class="article-comment-date">${new Date(comment.created_at).toLocaleDateString()}</span>
          </div>
          <p class="article-comment-text">${this.escapeHtml(comment.content)}</p>
          <div class="article-comment-footer">
            <button class="article-comment-like-btn"
                    data-comment-like="${comment.id}"
                    aria-label="${gettext('Like comment')}">
              <svg class="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span data-comment-like-count="${comment.id}">0</span>
            </button>
          </div>
        </div>
      </div>
    `;

        commentsList.insertAdjacentHTML('afterbegin', commentHTML);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async apiCall(method, url, data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            throw result;
        }

        return result;
    }

    getCsrfToken() {
        return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value.trim();
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ArticleInteractions();
    });
} else {
    new ArticleInteractions();
}
