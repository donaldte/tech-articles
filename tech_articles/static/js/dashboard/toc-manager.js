/**
 * TOC Manager - Handles TOC generation, editing, and deletion
 */

class TOCManager {
    constructor(config) {
        this.apiUrl = config.apiUrl;
        this.csrfToken = config.csrfToken;
        this.confirmModal = null;
        this.init();
    }

    init() {
        this.initConfirmModal();
        this.bindGenerateButton();
        this.bindRegenerateButton();
        this.bindDeleteButton();
        this.renderTOC();
    }

    initConfirmModal() {
        const modalElement = document.getElementById('toc-confirm-modal');
        if (!modalElement) return;

        if (typeof Modal !== 'undefined') {
            this.confirmModal = new Modal(modalElement, {
                backdrop: 'static',
                backdropClasses: 'bg-gray-900/50 fixed inset-0 z-[9999]',
                closable: true
            });
        } else {
            this.confirmModal = {
                element: modalElement,
                show: () => {
                    modalElement.classList.remove('hidden');
                    modalElement.style.display = 'flex';
                    document.body.style.overflow = 'hidden';
                },
                hide: () => {
                    modalElement.classList.add('hidden');
                    modalElement.style.display = 'none';
                    document.body.style.overflow = '';
                }
            };
        }

        const closeBtn = document.getElementById('toc-modal-close');
        const cancelBtn = document.getElementById('toc-modal-cancel');
        if (closeBtn) closeBtn.addEventListener('click', () => this.confirmModal.hide());
        if (cancelBtn) cancelBtn.addEventListener('click', () => this.confirmModal.hide());
    }

    showConfirmModal(message, onConfirm) {
        if (!this.confirmModal) {
            console.warn('Confirmation modal not available, skipping action.');
            return;
        }
        const messageEl = document.getElementById('toc-confirm-message');
        if (messageEl) messageEl.textContent = message;

        const confirmBtn = document.getElementById('toc-modal-confirm');
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        newConfirmBtn.addEventListener('click', () => {
            this.confirmModal.hide();
            if (onConfirm) onConfirm();
        });

        this.confirmModal.show();
    }

    showError(message) {
        if (window.toastManager) {
            window.toastManager.buildToast()
                .setMessage(message)
                .setType('danger')
                .show();
        } else {
            console.error(message);
        }
    }

    bindGenerateButton() {
        const btn = document.querySelector('[data-action="generate-toc"]');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            await this.generateTOC();
        });
    }

    bindRegenerateButton() {
        const btn = document.querySelector('[data-action="regenerate-toc"]');
        if (!btn) return;

        btn.addEventListener('click', () => {
            this.showConfirmModal(
                gettext('Regenerate table of contents? Any manual edits will be lost.'),
                () => this.generateTOC()
            );
        });
    }

    bindDeleteButton() {
        const btn = document.querySelector('[data-action="delete-toc"]');
        if (!btn) return;

        btn.addEventListener('click', () => {
            this.showConfirmModal(
                gettext('Delete table of contents?'),
                () => this.deleteTOC()
            );
        });
    }

    async generateTOC() {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('Failed to generate TOC');

            const data = await response.json();
            if (data.success) {
                window.location.reload();
            }
        } catch (error) {
            console.error('TOC generation error:', error);
            this.showError(gettext('Failed to generate table of contents'));
        }
    }

    async deleteTOC() {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('Failed to delete TOC');

            const data = await response.json();
            if (data.success) {
                window.location.reload();
            }
        } catch (error) {
            console.error('TOC deletion error:', error);
            this.showError(gettext('Failed to delete table of contents'));
        }
    }

    renderTOC() {
        const container = document.getElementById('toc-preview');
        if (!container || !window.tocData || !window.tocData.length) return;

        container.innerHTML = this.renderTOCItems(window.tocData);
    }

    renderTOCItems(items, level = 0) {
        let html = '<ul class="space-y-1">';

        for (const item of items) {
            const indent = level * 12;
            const itemLevel = item.level || (level + 1);

            let linkClass;
            if (itemLevel === 1) {
                linkClass = 'font-semibold text-mid text-text-primary hover:text-primary';
            } else if (itemLevel === 2) {
                linkClass = 'font-medium text-sm text-text-secondary hover:text-primary';
            } else if (itemLevel === 3) {
                linkClass = 'text-xs text-text-secondary hover:text-primary';
            } else {
                linkClass = 'text-xxs text-gray-500 hover:text-primary';
            }

            html += `
                <li style="margin-left: ${indent}px" class="py-0.5">
                    <a href="${window.articleDetailUrl}?page=${item.page_number}#${item.id}"
                       class="${linkClass} block transition-colors">
                        ${item.text}
                    </a>
                    ${item.children && item.children.length > 0 ? this.renderTOCChildren(item.children) : ''}
                </li>
            `;
        }

        html += '</ul>';
        return html;
    }

    renderTOCChildren(items) {
        return `<ul class="ml-3 mt-1 space-y-1 pl-3 border-l border-white/10">${this._buildChildItems(items)}</ul>`;
    }

    _buildChildItems(items) {
        let html = '';
        for (const item of items) {
            const itemLevel = item.level || 3;
            let linkClass;
            if (itemLevel === 1) {
                linkClass = 'font-semibold text-mid text-text-primary hover:text-primary';
            } else if (itemLevel === 2) {
                linkClass = 'font-medium text-sm text-text-secondary hover:text-primary';
            } else if (itemLevel === 3) {
                linkClass = 'text-xs text-text-secondary hover:text-primary';
            } else {
                linkClass = 'text-xxs text-gray-500 hover:text-primary';
            }
            const childrenHtml = item.children && item.children.length > 0
                ? this.renderTOCChildren(item.children)
                : '';
            html += `
                <li class="py-0.5">
                    <a href="${window.articleDetailUrl}?page=${item.page_number}#${item.id}" class="${linkClass} block transition-colors">${item.text}</a>
                    ${childrenHtml}
                </li>
            `;
        }
        return html;
    }
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new TOCManager({
        apiUrl: window.tocApiUrl,
        csrfToken: window.csrfToken,
    }));
} else {
    new TOCManager({
        apiUrl: window.tocApiUrl,
        csrfToken: window.csrfToken,
    });
}
