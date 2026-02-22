/**
 * Article Detail Interactions Manager
 * Handles claps, likes, comments and code copy buttons on article detail pages
 */

class ArticleInteractions {
    constructor() {
        this.articleId = null;
        this.authModal = null;
        this.init();
    }

    init() {
        // Get article ID from page
        const articleElement = document.querySelector('[data-article-id]');
        if (!articleElement) return;

        this.articleId = articleElement.dataset.articleId;

        // Initialise the auth-required modal
        this.initAuthModal();

        // Bind event listeners
        this.bindClapButton();
        this.bindLikeButton();
        this.bindCommentSubmit();
        this.bindCommentLikes();
        this.addCodeCopyButtons();
    }

    // ── Auth modal ────────────────────────────────────────────────────────────

    initAuthModal() {
        const modalEl = document.getElementById('authRequiredModal');
        if (!modalEl || typeof Modal === 'undefined') return;

        this.authModal = new Modal(modalEl, {
            placement: 'center',
            backdrop: 'dynamic',
            backdropClasses: 'bg-black/60 fixed inset-0 z-99998 backdrop-blur-[2px]',
            closable: true,
        });

        // Close buttons
        ['authRequiredModalClose', 'authRequiredModalClose2'].forEach((id) => {
            const btn = document.getElementById(id);
            if (btn) btn.addEventListener('click', () => this.authModal.hide());
        });
    }

    /**
     * Show the auth-required modal with an optional custom message.
     * Falls back to an alert if Flowbite is not available.
     * @param {string} message - Localised message to display in the modal body.
     */
    showAuthModal(message) {
        const msgEl = document.getElementById('authRequiredModalMessage');
        if (msgEl && message) {
            msgEl.textContent = message;
        }
        if (this.authModal) {
            this.authModal.show();
        } else {
            console.warn(message || gettext('Please log in to continue.'));
        }
    }

    // ── Clap ──────────────────────────────────────────────────────────────────

    bindClapButton() {
        const clapBtn = document.querySelector('[data-action="clap"]');
        if (!clapBtn) return;

        clapBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            try {
                const response = await this.apiCall('POST', window.urls.articleClap(this.articleId));

                if (response.success) {
                    const countEl = document.querySelector('[data-clap-count]');
                    if (countEl) {
                        countEl.textContent = response.total;
                    }

                    clapBtn.classList.add('animate-bounce');
                    setTimeout(() => clapBtn.classList.remove('animate-bounce'), 500);
                }
            } catch (error) {
                console.error('Clap error:', error);
                if (error.error) {
                    window.toastManager.buildToast()
                        .setMessage(error.error)
                        .setType('danger')
                        .show();
                }
            }
        });
    }

    // ── Article like ─────────────────────────────────────────────────────────

    bindLikeButton() {
        const likeBtn = document.querySelector('[data-action="like"]');
        if (!likeBtn) return;

        likeBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            if (likeBtn.dataset.requireAuth === 'true') {
                this.showAuthModal(gettext('Please log in to like this article.'));
                return;
            }

            try {
                const response = await this.apiCall('POST', window.urls.articleLike(this.articleId));

                if (response.success) {
                    const countEl = document.querySelector('[data-like-count]');
                    if (countEl) {
                        countEl.textContent = response.total;
                    }

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

    // ── Comment submit ────────────────────────────────────────────────────────

    bindCommentSubmit() {
        const submitBtn = document.querySelector('[data-comment-submit]');
        const textarea = document.querySelector('[data-comment-textarea]');
        const cancelBtn = document.querySelector('[data-comment-cancel]');

        if (!submitBtn || !textarea) return;

        submitBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            const content = textarea.value.trim();
            if (!content) {
                window.toastManager.buildToast()
                    .setMessage(gettext('Please enter a comment.'))
                    .setType('warning')
                    .show();
                return;
            }

            try {
                submitBtn.disabled = true;
                submitBtn.textContent = gettext('Posting...');

                const response = await this.apiCall('POST', window.urls.articleComments(this.articleId), {
                    content: content
                });

                if (response.success) {
                    textarea.value = '';
                    this.addCommentToList(response.comment);
                    this.incrementCommentCount();
                }
            } catch (error) {
                console.error('Comment error:', error);
                window.toastManager.buildToast()
                    .setMessage(error.error || gettext('Failed to post comment.'))
                    .setType('danger')
                    .show();
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

    /**
     * Increment comment counts in both the header stat button and the
     * comments-section heading (kept in sync).
     */
    incrementCommentCount() {
        // Header stat button
        const headerCountEl = document.querySelector('[data-comment-count]');
        if (headerCountEl) {
            const current = parseInt(headerCountEl.textContent) || 0;
            headerCountEl.textContent = current + 1;
        }

        // Comments-section heading "(N)"
        const sectionCountEl = document.querySelector('[data-comments-section-count]');
        if (sectionCountEl) {
            const current = parseInt(sectionCountEl.textContent.replace(/[()]/g, '')) || 0;
            sectionCountEl.textContent = `(${current + 1})`;
        }
    }

    // ── Comment likes ─────────────────────────────────────────────────────────

    bindCommentLikes() {
        document.addEventListener('click', async (e) => {
            const likeBtn = e.target.closest('[data-comment-like]');
            if (!likeBtn) return;

            e.preventDefault();

            if (likeBtn.dataset.requireAuth === 'true') {
                this.showAuthModal(gettext('Please log in to like comments.'));
                return;
            }

            const commentId = likeBtn.dataset.commentLike;

            try {
                const response = await this.apiCall('POST', window.urls.articleCommentLike(commentId));

                if (response.success) {
                    const countEl = document.querySelector(`[data-comment-like-count="${commentId}"]`);
                    if (countEl) {
                        countEl.textContent = response.total;
                    }

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

    // ── Code copy buttons ─────────────────────────────────────────────────────

    /**
     * Inject a "Copy" button into every fenced code block inside .article-prose.
     */
    addCodeCopyButtons() {
        const prose = document.querySelector('.article-prose');
        if (!prose) return;

        prose.querySelectorAll('pre').forEach((pre) => {
            // Avoid adding duplicate buttons
            if (pre.querySelector('.code-copy-btn')) return;

            // Make <pre> position:relative so the button can be positioned inside
            pre.style.position = 'relative';

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'code-copy-btn';
            btn.setAttribute('aria-label', gettext('Copy code'));
            btn.innerHTML = `
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                   fill="none" stroke="currentColor" stroke-width="2"
                   stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              <span class="code-copy-label">${gettext('Copy')}</span>`;

            btn.addEventListener('click', () => {
                const code = pre.querySelector('code');
                const text = code ? code.innerText : pre.innerText;
                navigator.clipboard.writeText(text).then(() => {
                    const label = btn.querySelector('.code-copy-label');
                    if (label) {
                        label.textContent = gettext('Copied!');
                        btn.classList.add('copied');
                        setTimeout(() => {
                            label.textContent = gettext('Copy');
                            btn.classList.remove('copied');
                        }, 2000);
                    }
                }).catch(() => {
                    // clipboard API unavailable – try legacy execCommand fallback
                    try {
                        const textarea = document.createElement('textarea');
                        textarea.value = text;
                        textarea.style.position = 'fixed';
                        textarea.style.opacity = '0';
                        document.body.appendChild(textarea);
                        textarea.focus();
                        textarea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textarea);
                        const label = btn.querySelector('.code-copy-label');
                        if (label) {
                            label.textContent = gettext('Copied!');
                            btn.classList.add('copied');
                            setTimeout(() => {
                                label.textContent = gettext('Copy');
                                btn.classList.remove('copied');
                            }, 2000);
                        }
                    } catch (fallbackErr) {
                        console.error('Copy failed:', fallbackErr);
                    }
                });
            });

            pre.appendChild(btn);
        });
    }

    // ── DOM helpers ───────────────────────────────────────────────────────────

    addCommentToList(comment) {
        const commentsList = document.querySelector('[data-comments-list]');
        if (!commentsList) return;

        // Remove "no comments" placeholder if present
        const placeholder = commentsList.querySelector('.text-center.py-8');
        if (placeholder) placeholder.remove();

        const commentHTML = `
      <div class="article-comment-item" data-comment-id="${comment.id}">
        <div class="article-comment-avatar-col">
          <div class="article-avatar-placeholder" style="background-color: #4B5563;">
            <span>${(comment.user.name || comment.user.email).charAt(0).toUpperCase()}</span>
          </div>
        </div>
        <div class="article-comment-body">
          <div class="article-comment-header">
            <span class="article-comment-author">${this.escapeHtml(comment.user.name || comment.user.email)}</span>
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

    // ── API helper ────────────────────────────────────────────────────────────

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
