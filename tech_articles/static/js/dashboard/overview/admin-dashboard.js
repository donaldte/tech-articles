/**
 * Admin Dashboard Manager
 *
 * Manages the admin dashboard page, displaying system statistics,
 * revenue charts, and subscription distribution using real data.
 *
 * @author Tech Articles Team
 * @version 2.0.0
 */

class AdminDashboard {
    /**
     * Initialize the admin dashboard
     * @param {Object} revenueData - Revenue chart data with keys: week, month, year
     * @param {Array} planData - Subscription plan distribution [{plan__name, count}, ...]
     */
    constructor(revenueData, planData) {
        this.currentDateElement = document.getElementById('current-date');
        this.revenueChartElement = document.getElementById('revenue-chart');
        this.subscriptionDistributionElement = document.getElementById('subscription-distribution');
        this.periodButtons = document.querySelectorAll('.period-btn');

        this.revenueData = revenueData || { week: { labels: [], values: [] }, month: { labels: [], values: [] }, year: { labels: [], values: [] } };
        this.planData = planData || [];
        this.currentPeriod = 'month';

        this.init();
    }

    /**
     * Initialize the dashboard
     */
    init() {
        this.displayCurrentDate();
        this.bindEvents();
        this.renderRevenueChart();
        this.renderSubscriptionDistribution();
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
        this.renderRevenueChart();
    }

    /**
     * Format chart labels for display
     * @param {string} label - Raw label from server
     * @param {string} period - Current period
     * @returns {string} - Formatted label
     */
    formatLabel(label, period) {
        const lang = document.documentElement.lang || 'en';

        if (period === 'week') {
            try {
                const date = new Date(label + 'T00:00:00');
                return date.toLocaleDateString(lang, { weekday: 'short' });
            } catch {
                return label;
            }
        } else if (period === 'month') {
            return label;
        } else {
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
     * Render revenue chart using real data
     */
    renderRevenueChart() {
        if (!this.revenueChartElement) return;

        const data = this.revenueData[this.currentPeriod];
        if (!data || !data.labels || !data.values) return;

        this.revenueChartElement.innerHTML = '';

        const maxValue = Math.max(...data.values, 1);
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
            bar.style.height = `${Math.max(percentage, 2)}%`;

            // Tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 bg-surface-light border border-border-dark rounded-lg text-xs text-white opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10';
            tooltip.textContent = `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            bar.appendChild(tooltip);

            barWrapper.appendChild(bar);
            barContainer.appendChild(barWrapper);

            const labelElement = document.createElement('div');
            labelElement.className = 'text-xs text-text-muted mt-2 text-center';
            labelElement.textContent = displayLabel;
            barContainer.appendChild(labelElement);

            chartContainer.appendChild(barContainer);
        });

        this.revenueChartElement.appendChild(chartContainer);
    }

    /**
     * Render subscription distribution chart (donut chart) using real data
     */
    renderSubscriptionDistribution() {
        if (!this.subscriptionDistributionElement) return;

        const colors = ['#60A5FA', '#00E5FF', '#A78BFA', '#34D399', '#FBBF24', '#F87171'];

        const chartData = this.planData.map((item, index) => ({
            plan: item.plan__name || gettext('Unknown'),
            count: item.count || 0,
            color: colors[index % colors.length],
        }));

        const total = chartData.reduce((sum, item) => sum + item.count, 0);

        if (total === 0) {
            this.subscriptionDistributionElement.innerHTML = `
                <div class="flex items-center justify-center h-full">
                    <p class="text-text-muted text-sm">${gettext('No subscription data yet')}</p>
                </div>
            `;
            return;
        }

        // Build container
        const container = document.createElement('div');
        container.className = 'flex flex-col h-full';

        // Donut chart area
        const chartArea = document.createElement('div');
        chartArea.className = 'flex-1 flex items-center justify-center mb-6';

        const donutContainer = document.createElement('div');
        donutContainer.className = 'relative w-48 h-48';

        // Build SVG donut
        let cumulativeAngle = 0;
        const paths = chartData.map((item) => {
            const percentage = (item.count / total) * 100;
            const startAngle = cumulativeAngle;
            cumulativeAngle += (percentage * 3.6);
            const endAngle = cumulativeAngle;
            const largeArcFlag = percentage > 50 ? 1 : 0;

            const startX = 50 + 40 * Math.cos((startAngle - 90) * Math.PI / 180);
            const startY = 50 + 40 * Math.sin((startAngle - 90) * Math.PI / 180);
            const endX = 50 + 40 * Math.cos((endAngle - 90) * Math.PI / 180);
            const endY = 50 + 40 * Math.sin((endAngle - 90) * Math.PI / 180);

            return `<path d="M 50 50 L ${startX} ${startY} A 40 40 0 ${largeArcFlag} 1 ${endX} ${endY} Z" fill="${item.color}" opacity="0.8"/>`;
        }).join('');

        donutContainer.innerHTML = `
            <svg viewBox="0 0 100 100" class="w-full h-full transform -rotate-90">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#2A2A35" stroke-width="20"/>
                ${paths}
            </svg>
        `;

        // Center text
        const centerText = document.createElement('div');
        centerText.className = 'absolute inset-0 flex flex-col items-center justify-center';
        centerText.innerHTML = `
            <span class="text-3xl font-bold text-white">${total}</span>
            <span class="text-xs text-text-muted">${gettext('Total')}</span>
        `;
        donutContainer.appendChild(centerText);

        chartArea.appendChild(donutContainer);
        container.appendChild(chartArea);

        // Legend
        const legend = document.createElement('div');
        legend.className = 'space-y-3';

        chartData.forEach(item => {
            const percentage = ((item.count / total) * 100).toFixed(1);
            const legendItem = document.createElement('div');
            legendItem.className = 'flex items-center justify-between';
            legendItem.innerHTML = `
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full" style="background-color: ${item.color}"></div>
                    <span class="text-sm text-white">${item.plan}</span>
                </div>
                <div class="flex items-center gap-3">
                    <span class="text-sm font-semibold text-white">${item.count}</span>
                    <span class="text-xs text-text-muted">${percentage}%</span>
                </div>
            `;
            legend.appendChild(legendItem);
        });

        container.appendChild(legend);
        this.subscriptionDistributionElement.innerHTML = '';
        this.subscriptionDistributionElement.appendChild(container);
    }
}
