/**
 * User Dashboard Manager
 *
 * Manages the user dashboard page, displaying statistics
 * and activity charts using real data from the server.
 *
 * @author Tech Articles Team
 * @version 2.0.0
 */

class UserDashboard {
    /**
     * Initialize the user dashboard
     * @param {Object} chartData - Real chart data from server with keys: week, month, year
     */
    constructor(chartData) {
        this.currentDateElement = document.getElementById('current-date');
        this.activityChartElement = document.getElementById('activity-chart');
        this.periodButtons = document.querySelectorAll('.period-btn');

        this.chartData = chartData || { week: { labels: [], values: [] }, month: { labels: [], values: [] }, year: { labels: [], values: [] } };
        this.currentPeriod = 'week';

        this.init();
    }

    /**
     * Initialize the dashboard
     */
    init() {
        this.displayCurrentDate();
        this.bindEvents();
        this.renderActivityChart();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        this.periodButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handlePeriodChange(e.target));
        });
    }

    /**
     * Display current date
     */
    displayCurrentDate() {
        if (!this.currentDateElement) return;

        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        const lang = document.documentElement.lang || 'en';
        this.currentDateElement.textContent = now.toLocaleDateString(lang, options);
    }

    /**
     * Handle period change
     * @param {HTMLElement} button - Clicked button
     */
    handlePeriodChange(button) {
        const period = button.dataset.period;
        if (period === this.currentPeriod) return;

        this.currentPeriod = period;

        // Update button states
        this.periodButtons.forEach(btn => {
            if (btn.dataset.period === period) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Re-render chart
        this.renderActivityChart();
    }

    /**
     * Format chart labels for display
     * @param {string} label - Raw label from server
     * @param {string} period - Current period (week, month, year)
     * @returns {string} - Formatted label
     */
    formatLabel(label, period) {
        const lang = document.documentElement.lang || 'en';

        if (period === 'week') {
            // Labels are ISO date strings (YYYY-MM-DD)
            try {
                const date = new Date(label + 'T00:00:00');
                return date.toLocaleDateString(lang, { weekday: 'short' });
            } catch {
                return label;
            }
        } else if (period === 'month') {
            // Labels are W1, W2, etc.
            return label;
        } else {
            // Labels are month numbers (1-12)
            try {
                const monthIndex = parseInt(label) - 1;
                const date = new Date(2026, monthIndex, 1);
                return date.toLocaleDateString(lang, { month: 'short' });
            } catch {
                return label;
            }
        }
    }

    /**
     * Render activity chart using real data
     */
    renderActivityChart() {
        if (!this.activityChartElement) return;

        const data = this.chartData[this.currentPeriod];
        if (!data || !data.labels || !data.values) return;

        this.activityChartElement.innerHTML = '';

        const maxValue = Math.max(...data.values, 1); // Avoid division by zero
        const chartContainer = document.createElement('div');
        chartContainer.className = 'flex items-end justify-between gap-2 h-full px-4';

        data.labels.forEach((label, index) => {
            const value = data.values[index] || 0;
            const percentage = (value / maxValue) * 100;
            const displayLabel = this.formatLabel(label, this.currentPeriod);

            const barContainer = document.createElement('div');
            barContainer.className = 'flex flex-col items-center flex-1 h-full';

            const barWrapper = document.createElement('div');
            barWrapper.className = 'flex items-end justify-center flex-1 w-full';

            const bar = document.createElement('div');
            bar.className = 'w-full bg-gradient-to-t from-primary to-primary/50 rounded-t-lg transition-all hover:from-primary-hover hover:to-primary/70 cursor-pointer relative group';
            bar.style.height = `${Math.max(percentage, 2)}%`; // Minimum 2% for visibility

            // Tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 bg-surface-light border border-border-dark rounded-lg text-xs text-white opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10';
            tooltip.textContent = `${value} ${gettext('articles')}`;
            bar.appendChild(tooltip);

            barWrapper.appendChild(bar);
            barContainer.appendChild(barWrapper);

            const labelElement = document.createElement('div');
            labelElement.className = 'text-xs text-text-muted mt-2 text-center';
            labelElement.textContent = displayLabel;
            barContainer.appendChild(labelElement);

            chartContainer.appendChild(barContainer);
        });

        this.activityChartElement.appendChild(chartContainer);
    }
}
