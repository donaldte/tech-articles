/**
 * Articles Listing Manager
 *
 * OOP-based manager for the articles listing page.
 * Handles lazy-loaded featured articles, search, category filtering,
 * sorting, paginated article grid, related articles, and pagination controls.
 *
 * All sections are loaded dynamically via JSON API endpoints.
 * Internationalization uses Django's gettext / ngettext / interpolate.
 *
 * @version 1.0.0
 */

class ArticlesListingManager {
    /**
     * @param {Object} config
     * @param {string} config.articlesApiUrl    - API URL for articles listing
     * @param {string} config.featuredApiUrl    - API URL for featured articles
     * @param {string} config.relatedApiUrl     - API URL for related articles
     * @param {string} config.categoriesApiUrl  - API URL for categories
     * @param {string} config.articleDetailUrl   - Base URL for article detail
     * @param {string} config.staticUrl         - Base URL for static files
     * @param {string} [config.defaultCoverImage] - Fallback cover image path (relative to staticUrl)
     */
    constructor(config) {
        this.config = config;
        this.currentPage = 1;
        this.totalPages = 1;
        this.searchTimeout = null;
        this.defaultSort = 'recent';
        this.selectedSort = this.defaultSort;
        this.selectedCategories = [];

        // DOM element references
        this.searchInput = document.querySelector('[data-articles-search]');
        this.sortContainer = document.querySelector('[data-dropdown="sort"]');
        this.categoryContainer = document.querySelector('[data-dropdown="category"]');
        this.featuredGrid = document.querySelector('[data-featured-grid]');
        this.articlesGrid = document.querySelector('[data-articles-grid]');
        this.paginationNav = document.querySelector('[data-articles-pagination]');
        this.relatedList = document.querySelector('[data-related-list]');
        this.categoryDropdownContent = document.querySelector('[data-dropdown-content="category"]');
        this.filtersForm = document.querySelector('[data-filters-form]');

        this.init();
    }

    // ──────────────────────────────────────────────
    //  Initialization
    // ──────────────────────────────────────────────

    init() {
        this._resetFilters();
        this.bindEvents();
        this.loadAllSections();
    }

    /**
     * Reset all filters and search input to their default state.
     * Called on page load to avoid unpredictable browser-cached values.
     */
    _resetFilters() {
        if (this.searchInput) {
            this.searchInput.value = '';
        }
        this.selectedSort = this.defaultSort;
        this.selectedCategories = [];
        this.currentPage = 1;

        // Reset sort radio to default
        const defaultSort = document.querySelector(`input[name="sort"][value="${this.defaultSort}"]`);
        if (defaultSort) {
            defaultSort.checked = true;
        }

        // Reset sort label
        const sortLabel = this.sortContainer
            ? this.sortContainer.querySelector('.filter-label')
            : null;
        if (sortLabel) {
            sortLabel.textContent = gettext('Most Recent');
        }

        // Reset category label
        const categoryLabel = this.categoryContainer
            ? this.categoryContainer.querySelector('.filter-label')
            : null;
        if (categoryLabel) {
            categoryLabel.textContent = gettext('All Categories');
        }
    }

    loadAllSections() {
        this._showFeaturedSection();
        this.showSkeleton(this.featuredGrid, this._featuredSkeleton());
        this.showSkeleton(this.articlesGrid, this._articlesSkeleton());
        this.showSkeleton(this.relatedList, this._relatedSkeleton());

        this.loadCategories();
        this.loadFeatured();
        this.loadArticles();
        this.loadRelated();
    }

    // ──────────────────────────────────────────────
    //  Events
    // ──────────────────────────────────────────────

    bindEvents() {
        // Debounced search
        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.currentPage = 1;
                    const val = this.searchInput ? this.searchInput.value.trim() : '';
                    // Only perform search when empty (cleared) or when length >= 3
                    if (val === '' || val.length >= 3) {
                        this._updateFeaturedVisibility();
                        this.loadArticles();
                    } else {
                        // For 1-2 characters, do not call loadArticles
                        this._updateFeaturedVisibility();
                    }
                }, 400);
            });
        }

        // Sort radio buttons
        if (this.sortContainer) {
            const sortDropdown = this.sortContainer.closest('.filter-dropdown-container');
            if (sortDropdown) {
                sortDropdown.addEventListener('change', (e) => {
                    if (e.target.name === 'sort') {
                        this.selectedSort = e.target.value;
                        this.currentPage = 1;
                        this._updateFeaturedVisibility();
                        this.loadArticles();
                    }
                });
            }
        }

        // Category checkboxes (delegated)
        if (this.categoryDropdownContent) {
            this.categoryDropdownContent.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox') {
                    this._syncSelectedCategories();
                    this.currentPage = 1;
                    this._updateFeaturedVisibility();
                    this.loadArticles();
                }
            });
        }
    }

    _syncSelectedCategories() {
        if (!this.categoryDropdownContent) return;
        const allOption = this.categoryDropdownContent.querySelector('input[data-all="true"]');
        if (allOption && allOption.checked) {
            this.selectedCategories = [];
            return;
        }
        this.selectedCategories = Array.from(
            this.categoryDropdownContent.querySelectorAll('input[type="checkbox"]:checked')
        ).filter(cb => cb.dataset.all !== 'true')
            .map(cb => cb.dataset.id);
    }

    /**
     * Check if the page is in its initial state (no search, no category filter).
     */
    _isInitialState() {
        // Treat search as active only when the query has at least 3 characters
        const val = this.searchInput ? this.searchInput.value.trim() : '';
        const hasSearch = val.length >= 3;
        const hasCategories = this.selectedCategories.length > 0;
        const hasSort = this.selectedSort !== this.defaultSort;
        return !hasSearch && !hasCategories && !hasSort;
    }

    /**
     * Show or hide the featured section based on the current filter state.
     * Featured articles are only visible in the initial state.
     */
    _updateFeaturedVisibility() {
        if (this._isInitialState()) {
            this._showFeaturedSection();
        } else {
            this._hideFeaturedSection();
        }
        this._updateFiltersOverflow();
    }

    _updateFiltersOverflow() {
        if (!this.filtersForm) return;
        const shouldOverflowVisible = !this._isInitialState();
        const targets = [this.filtersForm, this.filtersForm.parentElement].filter(Boolean);
        targets.forEach(el => {
            el.style.overflow = shouldOverflowVisible ? 'visible' : '';
        });
    }

    _showFeaturedSection() {
        if (this.featuredGrid) {
            this.featuredGrid.style.display = '';
        }
    }

    _hideFeaturedSection() {
        if (this.featuredGrid) {
            this.featuredGrid.style.display = 'none';
        }
    }

    /**
     * Enable the search input and filter buttons.
     * Called once articles have been rendered so the user cannot interact
     * with filters while the page is still loading.
     */
    _enableFilters() {
        if (this.searchInput) {
            this.searchInput.disabled = false;
        }
        if (this.sortContainer) {
            this.sortContainer.disabled = false;
        }
        if (this.categoryContainer) {
            this.categoryContainer.disabled = false;
        }
    }

    // ──────────────────────────────────────────────
    //  Data fetching helpers
    // ──────────────────────────────────────────────

    async _fetchJson(url) {
        try {
            const response = await fetch(url, {
                headers: {'X-Requested-With': 'XMLHttpRequest'},
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Fetch error for ${url}:`, error);
            return null;
        }
    }

    // ──────────────────────────────────────────────
    //  Categories (populates the filter dropdown)
    // ──────────────────────────────────────────────

    async loadCategories() {
        const data = await this._fetchJson(this.config.categoriesApiUrl);
        if (!data || !data.categories) return;

        if (!this.categoryDropdownContent) return;

        const allOption = `
            <label class="filter-option">
                <input type="checkbox" name="category" value="all" data-id="all" data-all="true" checked>
                <span>${this._escapeHtml(gettext('All Categories'))}</span>
            </label>
        `;

        this.categoryDropdownContent.innerHTML = allOption + data.categories.map(cat => `
            <label class="filter-option">
                <input type="checkbox" name="category" value="${this._escapeHtml(cat.slug)}" data-id="${this._escapeHtml(cat.id)}">
                <span>${this._escapeHtml(cat.name)}</span>
            </label>
        `).join('');
    }

    // ──────────────────────────────────────────────
    //  Featured articles
    // ──────────────────────────────────────────────

    async loadFeatured() {
        const data = await this._fetchJson(this.config.featuredApiUrl);

        if (!this.featuredGrid) return;

        if (!data || !data.featured || data.featured.length === 0) {
            this.featuredGrid.innerHTML = this._emptyState(gettext('No featured articles available.'));
            return;
        }

        const featured = data.featured;
        const primary = featured[0] || null;
        const secondary = featured.slice(1, 3);

        let html = '';

        if (primary) {
            html += this._renderFeaturedPrimary(primary);
        }

        if (secondary.length > 0) {
            html += `<div class="featured-article-secondary">`;
            secondary.forEach((article, idx) => {
                html += this._renderFeaturedSecondary(article, idx);
            });
            html += `</div>`;
        }

        this.featuredGrid.innerHTML = html;
    }

    _renderFeaturedPrimary(article) {
        const category = article.categories.length > 0 ? article.categories[0] : '';
        const imgSrc = this._coverUrl(article.cover_image_url);
        const altText = this._escapeHtml(article.cover_alt_text || article.title);
        return `
            <article class="featured-article featured-article-primary">
                <img src="${imgSrc}" alt="${altText}" class="featured-article-image">
                <div class="featured-article-overlay"></div>
                <div class="featured-article-content">
                    <div class="featured-article-meta">
                        <span class="first-featured-article-category">${this._escapeHtml(category)}</span>
                    </div>
                    <h2 class="featured-article-title">${this._escapeHtml(article.title)}</h2>
                    <p class="featured-article-description">${this._escapeHtml(article.summary)}</p>
                    <a href="${this.config.articleDetailUrl}" class="text-primary flex items-center gap-2 text-sm hover:underline">
                        ${gettext('Read featured article')}
                        ${this._arrowSvg()}
                    </a>
                </div>
            </article>
        `;
    }

    _renderFeaturedSecondary(article, idx) {
        const category = article.categories.length > 0 ? article.categories[0] : '';
        const imgSrc = this._coverUrl(article.cover_image_url);
        const altText = this._escapeHtml(article.cover_alt_text || article.title);
        const categoryClass = idx === 0 ? 'second-featured-article-category' : 'third-featured-article-category';
        return `
            <article class="featured-article featured-article-secondary-card">
                <img src="${imgSrc}" alt="${altText}" class="featured-article-image">
                <div class="featured-article-overlay"></div>
                <div class="featured-article-content">
                    <div class="featured-article-meta">
                        <span class="${categoryClass}">${this._escapeHtml(category)}</span>
                    </div>
                    <h2 class="featured-article-title">${this._escapeHtml(article.title)}</h2>
                    <a href="${this.config.articleDetailUrl}" class="text-primary flex items-center gap-2 text-sm hover:underline">
                        ${gettext('Read featured article')}
                        ${this._arrowSvg()}
                    </a>
                </div>
            </article>
        `;
    }

    // ──────────────────────────────────────────────
    //  Articles list (paginated)
    // ──────────────────────────────────────────────

    async loadArticles() {
        if (this.articlesGrid) {
            this.showSkeleton(this.articlesGrid, this._articlesSkeleton());
        }

        const params = new URLSearchParams();
        params.set('page', this.currentPage);
        params.set('sort', this.selectedSort);

        const searchVal = this.searchInput ? this.searchInput.value.trim() : '';
        // Only include the search parameter when the query has at least 3 characters
        if (searchVal && searchVal.length >= 3) {
            params.set('search', searchVal);
        }

        if (this.selectedCategories.length > 0) {
            params.set('categories', this.selectedCategories.join(','));
        }

        const url = `${this.config.articlesApiUrl}?${params.toString()}`;
        const data = await this._fetchJson(url);

        if (!data) {
            if (this.articlesGrid) {
                this.articlesGrid.innerHTML = this._emptyState(gettext('Failed to load articles.'));
            }
            this._renderPagination(null);
            this._enableFilters();
            return;
        }

        this.totalPages = data.pagination.total_pages;
        this.currentPage = data.pagination.current_page;

        if (!this.articlesGrid) return;

        if (data.articles.length === 0) {
            this.articlesGrid.innerHTML = this._emptyState(gettext('No articles found.'));
            this._renderPagination(null);
            this._enableFilters();
            return;
        }

        this.articlesGrid.innerHTML = data.articles.map(
            article => this._renderArticleCard(article)
        ).join('');

        this._renderPagination(data.pagination);
        this._enableFilters();
    }

    _renderArticleCard(article) {
        const category = article.categories.length > 0 ? article.categories[0] : '';
        const imgSrc = this._coverUrl(article.cover_image_url);
        const altText = this._escapeHtml(article.cover_alt_text || article.title);
        const langClass = this._escapeHtml(article.language);
        const langLabel = this._formatLanguageLabel(article.language);

        const readTimeFmt = interpolate(
            ngettext('%s min read', '%s min read', article.reading_time_minutes),
            [article.reading_time_minutes]
        );

        return `
            <article class="article-card group flex flex-col h-full p-4 sm:p-5 lg:p-6">
                <div class="article-card-image-wrapper mb-6">
                    <img src="${imgSrc}" alt="${altText}" class="article-card-image rounded-lg">
                </div>
                <div class="article-card-content flex flex-col flex-1">
                    <div class="article-card-meta flex-wrap">
                        <span class="article-card-category-badge">${this._escapeHtml(category)}</span>
                        <svg class="article-card-separator" viewBox="0 0 4 4" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="2" cy="2" r="2" fill="currentColor"></circle>
                        </svg>
                        <span class="article-card-read-time">${readTimeFmt}</span>
                    </div>
                    <h3 class="article-card-title">${this._escapeHtml(article.title)}</h3>
                    <p class="article-card-description">${this._escapeHtml(article.summary)}</p>
                    <div class="article-card-footer mt-auto flex flex-row items-center gap-3">
                        <div class="article-card-language ${langClass}">
                            <svg class="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"
                                 width="24" height="24" fill="none" viewBox="0 0 24 24">
                                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="m13 19 3.5-9 3.5 9m-6.125-2h5.25M3 7h7m0 0h2m-2 0c0 1.63-.793 3.926-2.239 5.655M7.5 6.818V5m.261 7.655C6.79 13.82 5.521 14.725 4 15m3.761-2.345L5 10m2.761 2.655L10.2 15"></path>
                            </svg>
                            <span class="text-sm font-medium">${this._escapeHtml(langLabel)}</span>
                        </div>
                        <div class="sm:ml-auto">
                            <a href="${this.config.articleDetailUrl}" class="btn-primary">${gettext('Read more')}</a>
                        </div>
                    </div>
                </div>
            </article>
        `;
    }

    // ──────────────────────────────────────────────
    //  Pagination
    // ──────────────────────────────────────────────

    _renderPagination(pagination) {
        if (!this.paginationNav) return;

        if (!pagination || pagination.total_pages <= 1) {
            this.paginationNav.innerHTML = '';
            return;
        }

        const pages = this._getPageNumbers(pagination.current_page, pagination.total_pages);

        let html = '';

        // Previous button
        html += `
            <button class="pagination-button" data-page="${pagination.current_page - 1}"
                    aria-label="${gettext('Previous page')}"
                    ${!pagination.has_previous ? 'disabled' : ''}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10.5 3.5L6 8L10.5 12.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
            </button>
        `;

        // Page numbers
        html += `<div class="pagination-pages">`;
        pages.forEach(p => {
            if (p === '...') {
                html += `
                    <span class="pagination-ellipsis">
                        <svg width="2" height="2" viewBox="0 0 4 4" fill="none"><circle cx="2" cy="2" r="2" fill="#D9D9D9"></circle></svg>
                        <svg width="2" height="2" viewBox="0 0 4 4" fill="none"><circle cx="2" cy="2" r="2" fill="#D9D9D9"></circle></svg>
                        <svg width="2" height="2" viewBox="0 0 4 4" fill="none"><circle cx="2" cy="2" r="2" fill="#D9D9D9"></circle></svg>
                    </span>
                `;
            } else {
                const activeClass = p === pagination.current_page ? 'pagination-page-active' : '';
                const ariaCurrent = p === pagination.current_page ? 'aria-current="page"' : '';
                html += `<button class="pagination-page ${activeClass}" data-page="${p}" ${ariaCurrent}>${p}</button>`;
            }
        });
        html += `</div>`;

        // Next button
        html += `
            <button class="pagination-button" data-page="${pagination.current_page + 1}"
                    aria-label="${gettext('Next page')}"
                    ${!pagination.has_next ? 'disabled' : ''}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M5.5 3.5L10 8L5.5 12.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
            </button>
        `;

        this.paginationNav.innerHTML = html;

        // Bind pagination click events
        this.paginationNav.querySelectorAll('[data-page]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = parseInt(e.currentTarget.dataset.page, 10);
                if (!isNaN(page) && page >= 1 && page <= this.totalPages) {
                    this.currentPage = page;
                    this.loadArticles();
                    this.articlesGrid.scrollIntoView({behavior: 'smooth', block: 'start'});
                }
            });
        });
    }

    _getPageNumbers(current, total) {
        if (total <= 7) {
            return Array.from({length: total}, (_, i) => i + 1);
        }
        const pages = [];
        pages.push(1);
        if (current > 3) pages.push('...');
        for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
            pages.push(i);
        }
        if (current < total - 2) pages.push('...');
        pages.push(total);
        return pages;
    }

    // ──────────────────────────────────────────────
    //  Related articles (sidebar)
    // ──────────────────────────────────────────────

    async loadRelated() {
        const data = await this._fetchJson(this.config.relatedApiUrl);

        if (!this.relatedList) return;

        if (!data || !data.related || data.related.length === 0) {
            this.relatedList.innerHTML = this._emptyState(gettext('No related articles.'));
            return;
        }

        this.relatedList.innerHTML = data.related.map(
            article => this._renderRelatedCard(article)
        ).join('');
    }

    _renderRelatedCard(article) {
        const category = article.categories.length > 0 ? article.categories[0] : '';

        const readTimeFmt = interpolate(
            ngettext('%s min read', '%s min read', article.reading_time_minutes),
            [article.reading_time_minutes]
        );

        return `
            <a href="${this.config.articleDetailUrl}" class="related-article-card">
                <div class="related-article-meta">
                    <span class="related-article-category">${this._escapeHtml(category)}</span>
                    <span class="related-article-dot"></span>
                    <span class="related-article-read-time">${readTimeFmt}</span>
                </div>
                <h3 class="related-article-title">${this._escapeHtml(article.title)}</h3>
                <p class="related-article-description">${this._escapeHtml(article.summary)}</p>
                <div class="related-article-footer">
                    <span class="related-article-cta">
                        ${gettext('Read article')}
                        <svg class="related-article-cta-icon" width="16" height="13" viewBox="0 0 16 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M0.5 6.33331H15.0833" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"></path>
                            <path d="M9.66602 12.1667L15.4993 6.33333L9.66602 0.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"></path>
                        </svg>
                    </span>
                </div>
            </a>
        `;
    }

    // ──────────────────────────────────────────────
    //  Skeleton loaders
    // ──────────────────────────────────────────────

    showSkeleton(container, html) {
        if (container) {
            container.innerHTML = html;
        }
    }

    _featuredSkeleton() {
        return `
            <div class="featured-article featured-article-primary animate-pulse bg-[#1E1E28] min-h-85 sm:min-h-95 rounded-2xl"></div>
            <div class="featured-article-secondary">
                <div class="featured-article featured-article-secondary-card animate-pulse bg-[#1E1E28] min-h-60 sm:min-h-65 rounded-2xl"></div>
                <div class="featured-article featured-article-secondary-card animate-pulse bg-[#1E1E28] min-h-60 sm:min-h-65 rounded-2xl"></div>
            </div>
        `;
    }

    _articlesSkeleton() {
        const card = `
            <div class="article-card animate-pulse p-4 sm:p-5 lg:p-6">
                <div class="bg-[#1E1E28] rounded-lg aspect-video mb-6"></div>
                <div class="space-y-3">
                    <div class="h-4 bg-[#1E1E28] rounded w-1/3"></div>
                    <div class="h-5 bg-[#1E1E28] rounded w-3/4"></div>
                    <div class="h-4 bg-[#1E1E28] rounded w-full"></div>
                    <div class="h-4 bg-[#1E1E28] rounded w-2/3"></div>
                </div>
            </div>
        `;
        return card.repeat(6);
    }

    _relatedSkeleton() {
        const card = `
            <div class="related-article-card animate-pulse p-4">
                <div class="h-3 bg-[#1E1E28] rounded w-1/4 mb-3"></div>
                <div class="h-4 bg-[#1E1E28] rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-[#1E1E28] rounded w-full"></div>
            </div>
        `;
        return card.repeat(4);
    }

    // ──────────────────────────────────────────────
    //  Helpers
    // ──────────────────────────────────────────────

    _emptyState(message) {
        return `<div class="text-center py-12 text-gray-400 col-span-full">${this._escapeHtml(message)}</div>`;
    }

    _coverUrl(key) {
        if (!key) {
            const fallback = this.config.defaultCoverImage || 'images/articles/1.jpg';
            return this.config.staticUrl + fallback;
        }
        if (key.startsWith('http://') || key.startsWith('https://')) {
            return key;
        }
        return '/media/' + key;
    }

    _formatLanguageLabel(language) {
        if (!language) return '';
        return language.charAt(0).toUpperCase() + language.slice(1);
    }

    _arrowSvg() {
        return `<svg width="16" height="13" viewBox="0 0 16 13" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0.5 6.33331H15.0833" stroke="#00E5FF" stroke-linecap="round" stroke-linejoin="round"></path>
            <path d="M9.66602 12.1667L15.4993 6.33333L9.66602 0.5" stroke="#00E5FF" stroke-linecap="round" stroke-linejoin="round"></path>
        </svg>`;
    }

    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

