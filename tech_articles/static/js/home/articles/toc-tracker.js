/**
 * TOC Scroll Tracker - Highlights current section in TOC
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

    init() {
        if (!this.headings.length) return;
        this.updateActiveLink();
        window.addEventListener('scroll', () => this.updateActiveLink(), { passive: true });
    }

    getHeadings() {
        const ids = this.links.map(link => link.dataset.tocId);
        return ids.map(id => document.getElementById(id)).filter(Boolean);
    }

    updateActiveLink() {
        const scrollPos = window.scrollY + 100;
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
