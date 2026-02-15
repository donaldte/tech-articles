/**
 * Admin Dashboard Manager
 *
 * Manages the admin dashboard page, displaying system statistics,
 * revenue charts, and recent activity.
 *
 * Features:
 * - OOP-based architecture
 * - Dynamic data rendering
 * - Revenue chart visualization
 * - Subscription distribution chart
 * - Internationalization support
 *
 * @author Tech Articles Team
 * @version 1.0.0
 */

class AdminDashboard {
    /**
     * Initialize the admin dashboard
     */
    constructor() {
        this.currentDateElement = document.getElementById('current-date');
        this.revenueChartElement = document.getElementById('revenue-chart');
        this.subscriptionDistributionElement = document.getElementById('subscription-distribution');
        this.recentActivityElement = document.getElementById('recent-activity');
        this.periodButtons = document.querySelectorAll('.period-btn');
        
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
        this.renderRecentActivity();
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
     * Render revenue chart
     */
    renderRevenueChart() {
        if (!this.revenueChartElement) return;

        const data = this.generateMockRevenueData();
        
        // Create simple area chart with CSS
        this.revenueChartElement.innerHTML = '';
        
        const maxValue = Math.max(...data.values);
        const chartContainer = document.createElement('div');
        chartContainer.className = 'flex items-end justify-between gap-2 h-full px-4';

        data.labels.forEach((label, index) => {
            const value = data.values[index];
            const percentage = (value / maxValue) * 100;

            const barContainer = document.createElement('div');
            barContainer.className = 'flex flex-col items-center flex-1 h-full';

            const barWrapper = document.createElement('div');
            barWrapper.className = 'flex items-end justify-center flex-1 w-full';

            const bar = document.createElement('div');
            bar.className = 'w-full bg-gradient-to-t from-primary to-primary/50 rounded-t-lg transition-all hover:from-primary-hover hover:to-primary/70 cursor-pointer relative group';
            bar.style.height = `${percentage}%`;
            
            // Tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 bg-surface-light border border-border-dark rounded-lg text-xs text-white opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none';
            tooltip.textContent = `$${value.toLocaleString()}`;
            bar.appendChild(tooltip);

            barWrapper.appendChild(bar);
            barContainer.appendChild(barWrapper);

            const labelElement = document.createElement('div');
            labelElement.className = 'text-xs text-text-muted mt-2 text-center';
            labelElement.textContent = label;
            barContainer.appendChild(labelElement);

            chartContainer.appendChild(barContainer);
        });

        this.revenueChartElement.appendChild(chartContainer);
    }

    /**
     * Generate mock revenue data
     * @returns {Object} - Chart data with labels and values
     */
    generateMockRevenueData() {
        if (this.currentPeriod === 'week') {
            return {
                labels: [
                    gettext('Monday'),
                    gettext('Tuesday'),
                    gettext('Wednesday'),
                    gettext('Thursday'),
                    gettext('Friday'),
                    gettext('Saturday'),
                    gettext('Sunday'),
                ],
                values: [5200, 6800, 5500, 7200, 6400, 3800, 2500]
            };
        } else if (this.currentPeriod === 'month') {
            return {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                values: [28500, 32400, 29800, 35200]
            };
        } else {
            return {
                labels: [
                    gettext('January'),
                    gettext('February'),
                    gettext('March'),
                    gettext('April'),
                    gettext('May'),
                    gettext('June'),
                    gettext('July'),
                    gettext('August'),
                    gettext('September'),
                    gettext('October'),
                    gettext('November'),
                    gettext('December'),
                ],
                values: [35000, 38000, 42000, 45000, 48000, 52000, 55000, 58000, 60000, 63000, 65000, 68000]
            };
        }
    }

    /**
     * Render subscription distribution chart (donut chart)
     */
    renderSubscriptionDistribution() {
        if (!this.subscriptionDistributionElement) return;

        const mockData = [
            { plan: gettext('Basic'), count: 450, color: '#60A5FA' },
            { plan: gettext('Premium'), count: 585, color: '#00E5FF' },
            { plan: gettext('Enterprise'), count: 200, color: '#A78BFA' }
        ];

        const total = mockData.reduce((sum, item) => sum + item.count, 0);

        // Create legend and stats
        const container = document.createElement('div');
        container.className = 'flex flex-col h-full';

        // Donut chart (simplified visualization)
        const chartArea = document.createElement('div');
        chartArea.className = 'flex-1 flex items-center justify-center mb-6';
        
        const donutContainer = document.createElement('div');
        donutContainer.className = 'relative w-48 h-48';
        
        // Create simplified donut visualization
        const donutSvg = `
            <svg viewBox="0 0 100 100" class="w-full h-full transform -rotate-90">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#2A2A35" stroke-width="20"/>
                ${mockData.map((item, index) => {
                    const percentage = (item.count / total) * 100;
                    const startAngle = mockData.slice(0, index).reduce((sum, d) => sum + (d.count / total) * 360, 0);
                    const endAngle = startAngle + (percentage * 3.6);
                    const largeArcFlag = percentage > 50 ? 1 : 0;
                    
                    const startX = 50 + 40 * Math.cos((startAngle - 90) * Math.PI / 180);
                    const startY = 50 + 40 * Math.sin((startAngle - 90) * Math.PI / 180);
                    const endX = 50 + 40 * Math.cos((endAngle - 90) * Math.PI / 180);
                    const endY = 50 + 40 * Math.sin((endAngle - 90) * Math.PI / 180);
                    
                    return `<path d="M 50 50 L ${startX} ${startY} A 40 40 0 ${largeArcFlag} 1 ${endX} ${endY} Z" fill="${item.color}" opacity="0.8"/>`;
                }).join('')}
            </svg>
        `;
        donutContainer.innerHTML = donutSvg;
        
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
        
        mockData.forEach(item => {
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

    /**
     * Render recent activity
     */
    renderRecentActivity() {
        if (!this.recentActivityElement) return;

        const mockActivities = [
            {
                user: 'John Doe',
                action: gettext('subscribed to Premium plan'),
                time: new Date(Date.now() - 15 * 60000), // 15 minutes ago
                icon: 'check',
                color: 'green'
            },
            {
                user: 'Jane Smith',
                action: gettext('booked an appointment'),
                time: new Date(Date.now() - 45 * 60000), // 45 minutes ago
                icon: 'calendar',
                color: 'blue'
            },
            {
                user: 'Bob Johnson',
                action: gettext('downloaded a resource'),
                time: new Date(Date.now() - 90 * 60000), // 1.5 hours ago
                icon: 'download',
                color: 'purple'
            },
            {
                user: 'Alice Williams',
                action: gettext('read an article'),
                time: new Date(Date.now() - 120 * 60000), // 2 hours ago
                icon: 'book',
                color: 'yellow'
            }
        ];

        if (mockActivities.length === 0) {
            this.recentActivityElement.innerHTML = `
                <p class="text-center py-8 text-text-muted">${gettext('No recent activity')}</p>
            `;
            return;
        }

        this.recentActivityElement.innerHTML = mockActivities.map(activity => this.createActivityItem(activity)).join('');
    }

    /**
     * Create activity item HTML
     * @param {Object} activity - Activity data
     * @returns {string} - Activity item HTML
     */
    createActivityItem(activity) {
        const timeAgo = this.formatTimeAgo(activity.time);
        
        const icons = {
            check: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>',
            calendar: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>',
            download: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"/>',
            book: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>'
        };

        const colorClasses = {
            green: 'bg-green-500/20 text-green-400',
            blue: 'bg-blue-500/20 text-blue-400',
            purple: 'bg-purple-500/20 text-purple-400',
            yellow: 'bg-yellow-500/20 text-yellow-400'
        };

        return `
            <div class="flex items-start gap-4 p-4 bg-surface-darker rounded-lg border border-border-dark">
                <div class="w-10 h-10 rounded-lg ${colorClasses[activity.color]} flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        ${icons[activity.icon]}
                    </svg>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm text-white">
                        <span class="font-semibold">${activity.user}</span>
                        <span class="text-text-muted"> ${activity.action}</span>
                    </p>
                    <p class="text-xs text-text-muted mt-1">${timeAgo}</p>
                </div>
            </div>
        `;
    }

    /**
     * Format time ago
     * @param {Date} date - Date to format
     * @returns {string} - Formatted time ago string
     */
    formatTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) {
            return gettext('Just now');
        } else if (diffMins < 60) {
            return ngettext('%s minute ago', '%s minutes ago', diffMins).replace('%s', diffMins);
        } else if (diffHours < 24) {
            return ngettext('%s hour ago', '%s hours ago', diffHours).replace('%s', diffHours);
        } else {
            return ngettext('%s day ago', '%s days ago', diffDays).replace('%s', diffDays);
        }
    }
}
