/**
 * TOC Scroll Tracker - Highlights current section in TOC
 * Improved: respects fixed header by using CSS var --scroll-offset and intercepts anchor clicks
 */

class TOCTracker {
    constructor() {
        this.nav = document.getElementById('toc-nav');
        if (!this.nav) return;

        this.links = Array.from(this.nav.querySelectorAll('.toc-link'));
        this.currentId = null;

        // Determine current page number from query params (default 1)
        const urlParams = new URLSearchParams(window.location.search);
        this.currentPage = parseInt(urlParams.get('page') || '1', 10);

        this.headings = this.getHeadings();

        this.init();
    }

    // Compute header height and set CSS variable
    setCssOffset() {
        const header = document.querySelector('.navbar');
        const defaultOffset = 72; // px fallback
        const offset = header ? Math.ceil(header.getBoundingClientRect().height + 8) : defaultOffset;
        document.documentElement.style.setProperty('--scroll-offset', offset + 'px');
    }

    init() {
        if (!this.headings.length) return;
        this.setCssOffset();
        window.addEventListener('resize', () => this.setCssOffset(), {passive: true});

        // Intercept TOC anchor clicks
        document.addEventListener('click', (e) => {
            const anchor = e.target.closest('a[href]');
            if (!anchor) return;
            const href = anchor.getAttribute('href');
            if (!href || href === '#') return;

            // TOC links with ?page=X#hash
            if (anchor.classList.contains('toc-link') && href.includes('?page=')) {
                const linkPage = parseInt(anchor.dataset.tocPage || '1', 10);
                const hash = href.split('#')[1] || '';

                if (linkPage !== this.currentPage) {
                    // Navigate to a different page, let the browser handle it fully
                    e.preventDefault();
                    window.location.href = href;
                    return;
                }

                // Same page: smooth scroll to the heading
                if (hash) {
                    const target = document.getElementById(hash);
                    if (target) {
                        e.preventDefault();
                        this.scrollToWithOffset(target);
                        history.replaceState(null, '', href);
                        return;
                    }
                }
                return;
            }

            // Legacy plain anchor links (#hash only)
            if (href.startsWith('#')) {
                const hash = href.slice(1);
                if (!hash) return;
                const target = document.getElementById(hash);
                if (!target) return;
                e.preventDefault();
                this.scrollToWithOffset(target);
                history.replaceState(null, '', '#' + hash);
            }
        });

        this.updateActiveLink();
        window.addEventListener('scroll', () => this.updateActiveLink(), {passive: true});

        // If page loaded with a hash, scroll to it respecting offset
        if (window.location.hash) {
            const id = window.location.hash.replace('#', '');
            const el = document.getElementById(id);
            if (el) setTimeout(() => this.scrollToWithOffset(el), 50);
        }
    }

    getHeadings() {
        const ids = this.links
            .filter(link => parseInt(link.dataset.tocPage || '1', 10) === this.currentPage)
            .map(link => link.dataset.tocId);
        return ids.map(id => document.getElementById(id)).filter(Boolean);
    }

    scrollToWithOffset(el) {
        if (!el) return;
        // read CSS var --scroll-offset (expects px)
        const raw = getComputedStyle(document.documentElement).getPropertyValue('--scroll-offset') || '72px';
        const offset = parseInt(raw, 10) || 72;
        const rect = el.getBoundingClientRect();
        const top = window.scrollY + rect.top - offset;
        window.scrollTo({top: Math.max(0, top), behavior: 'smooth'});
    }

    updateActiveLink() {
        // Use the CSS offset so active calculation matches visual position
        const raw = getComputedStyle(document.documentElement).getPropertyValue('--scroll-offset') || '72px';
        const offset = parseInt(raw, 10) || 72;
        const scrollPos = window.scrollY + offset + 5; // small tolerance
        let currentHeading = null;

        for (const heading of this.headings) {
            if (heading.offsetTop <= scrollPos) {
                currentHeading = heading;
            }
        }

        if (!currentHeading) return;

        const newId = currentHeading.id;
        if (newId === this.currentId) return;

        this.currentId = newId;

        this.links.forEach(link => {
            if (link.dataset.tocId === newId) {
                link.classList.add('active', 'text-primary', 'font-medium');
                link.classList.remove('text-text-secondary');
            } else {
                link.classList.remove('active', 'text-primary', 'font-medium');
                link.classList.add('text-text-secondary');
            }
        });
    }
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new TOCTracker());
} else {
    new TOCTracker();
}

/**
 * Navigate back, skipping history entries that only differ by hash
 * (e.g. TOC anchor clicks on the same article page).
 * Falls back to fallbackUrl when no different URL is found.
 */
window.articleBack = function (fallbackUrl) {
    const MAX_HISTORY_STEPS = 20;
    const HISTORY_NAVIGATION_DELAY_MS = 150;
    let steps = 0;
    const targetKey = window.location.pathname + window.location.search;

    const tryBack = () => {
        if (steps >= MAX_HISTORY_STEPS) {
            if (fallbackUrl) window.location.href = fallbackUrl;
            return;
        }

        if (window.history.length <= 1) {
            if (fallbackUrl) window.location.href = fallbackUrl;
            return;
        }

        window.history.back();
        steps++;

        setTimeout(() => {
            const current = window.location.pathname + window.location.search;
            if (current === targetKey) {
                // Still on the same page (only hash changed), keep going
                tryBack();
            }
            // Otherwise we've arrived at a genuinely different URL — done.
        }, HISTORY_NAVIGATION_DELAY_MS);
    };

    tryBack();
};
