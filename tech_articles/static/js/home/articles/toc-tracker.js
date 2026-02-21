/**
 * TOC Scroll Tracker - Highlights current section in TOC
 * Improved: respects fixed header by using CSS var --scroll-offset and intercepts anchor clicks
 */

class TOCTracker {
    constructor() {
        this.nav = document.getElementById('toc-nav');
        if (!this.nav) return;

        this.links = Array.from(this.nav.querySelectorAll('.toc-link'));
        this.headings = this.getHeadings();
        this.currentId = null;

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

        // Intercept in-page anchor clicks to apply offset scrolling
        document.addEventListener('click', (e) => {
            const anchor = e.target.closest('a[href^="#"]');
            if (!anchor) return;
            const href = anchor.getAttribute('href');
            if (!href || href === '#') return;
            const hash = href.split('#')[1];
            if (!hash) return;
            const target = document.getElementById(hash);
            if (!target) return; // allow default navigation if element missing

            e.preventDefault();
            this.scrollToWithOffset(target);
            history.pushState(null, '', '#' + hash);
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
        const ids = this.links.map(link => link.dataset.tocId);
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
