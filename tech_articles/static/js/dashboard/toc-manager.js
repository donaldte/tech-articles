/**
 * TOC Manager - Handles TOC generation, editing, and deletion
 */

class TOCManager {
    constructor(config) {
        this.apiUrl = config.apiUrl;
        this.csrfToken = config.csrfToken;
        this.init();
    }

    init() {
        this.bindGenerateButton();
        this.bindRegenerateButton();
        this.bindDeleteButton();
        this.renderTOC();
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

        btn.addEventListener('click', async () => {
            if (!confirm(gettext('Regenerate table of contents? Any manual edits will be lost.'))) {
                return;
            }
            await this.generateTOC();
        });
    }

    bindDeleteButton() {
        const btn = document.querySelector('[data-action="delete-toc"]');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            if (!confirm(gettext('Delete table of contents?'))) {
                return;
            }
            await this.deleteTOC();
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
            alert(gettext('Failed to generate table of contents'));
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
            alert(gettext('Failed to delete table of contents'));
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
