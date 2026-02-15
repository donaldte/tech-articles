/**
 * User Dashboard Manager
 *
 * Manages the user dashboard page, displaying statistics, recent activity,
 * and activity charts.
 *
 * Features:
 * - OOP-based architecture
 * - Dynamic data rendering
 * - Activity chart visualization
 * - Internationalization support
 *
 * @author Tech Articles Team
 * @version 1.0.0
 */

class UserDashboard {
    /**
     * Initialize the user dashboard
     */
    constructor() {
        this.currentDateElement = document.getElementById('current-date');
        this.activityChartElement = document.getElementById('activity-chart');
        this.recentArticlesElement = document.getElementById('recent-articles');
        this.upcomingAppointmentsElement = document.getElementById('upcoming-appointments');
        this.periodButtons = document.querySelectorAll('.period-btn');
        
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
        this.renderRecentArticles();
        this.renderUpcomingAppointments();
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
     * Render activity chart
     */
    renderActivityChart() {
        if (!this.activityChartElement) return;

        const data = this.generateMockChartData();
        
        // Create simple bar chart with CSS
        this.activityChartElement.innerHTML = '';
        
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
            tooltip.textContent = `${value} ${gettext('Articles Read')}`;
            bar.appendChild(tooltip);

            barWrapper.appendChild(bar);
            barContainer.appendChild(barWrapper);

            const labelElement = document.createElement('div');
            labelElement.className = 'text-xs text-text-muted mt-2 text-center';
            labelElement.textContent = label;
            barContainer.appendChild(labelElement);

            chartContainer.appendChild(barContainer);
        });

        this.activityChartElement.appendChild(chartContainer);
    }

    /**
     * Generate mock chart data
     * @returns {Object} - Chart data with labels and values
     */
    generateMockChartData() {
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
                values: [12, 19, 15, 22, 18, 8, 5]
            };
        } else if (this.currentPeriod === 'month') {
            return {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                values: [45, 52, 48, 55]
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
                values: [45, 52, 48, 55, 62, 58, 65, 70, 68, 75, 72, 80]
            };
        }
    }

    /**
     * Render recent articles
     */
    renderRecentArticles() {
        if (!this.recentArticlesElement) return;

        const mockArticles = [
            {
                title: gettext('Getting Started with Django 5.0'),
                category: gettext('Backend'),
                date: new Date(2026, 2, 10),
                readTime: 8
            },
            {
                title: gettext('Advanced React Patterns'),
                category: gettext('Frontend'),
                date: new Date(2026, 2, 8),
                readTime: 12
            },
            {
                title: gettext('Docker Best Practices'),
                category: gettext('DevOps'),
                date: new Date(2026, 2, 5),
                readTime: 10
            }
        ];

        if (mockArticles.length === 0) {
            this.recentArticlesElement.innerHTML = `
                <p class="text-center py-8 text-text-muted">${gettext('No recently read articles')}</p>
            `;
            return;
        }

        this.recentArticlesElement.innerHTML = mockArticles.map(article => this.createArticleItem(article)).join('');
    }

    /**
     * Create article item HTML
     * @param {Object} article - Article data
     * @returns {string} - Article item HTML
     */
    createArticleItem(article) {
        const lang = document.documentElement.lang || 'en';
        const formattedDate = article.date.toLocaleDateString(lang, { month: 'short', day: 'numeric' });

        return `
            <div class="flex items-start gap-4 p-4 bg-surface-darker rounded-lg border border-border-dark hover:border-primary/30 transition-all">
                <div class="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                    </svg>
                </div>
                <div class="flex-1 min-w-0">
                    <h3 class="text-sm font-semibold text-white truncate">${article.title}</h3>
                    <div class="flex items-center gap-3 mt-1">
                        <span class="text-xs text-primary">${article.category}</span>
                        <span class="text-xs text-text-muted">•</span>
                        <span class="text-xs text-text-muted">${formattedDate}</span>
                        <span class="text-xs text-text-muted">•</span>
                        <span class="text-xs text-text-muted">${article.readTime} ${gettext('min read')}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render upcoming appointments
     */
    renderUpcomingAppointments() {
        if (!this.upcomingAppointmentsElement) return;

        const mockAppointments = [
            {
                title: gettext('Expert Consultation'),
                date: new Date(2026, 2, 18, 10, 0),
                duration: 60,
                status: 'confirmed'
            },
            {
                title: gettext('Technical Review'),
                date: new Date(2026, 2, 22, 14, 30),
                duration: 90,
                status: 'pending'
            }
        ];

        if (mockAppointments.length === 0) {
            this.upcomingAppointmentsElement.innerHTML = `
                <p class="text-center py-8 text-text-muted">${gettext('No upcoming appointments')}</p>
            `;
            return;
        }

        this.upcomingAppointmentsElement.innerHTML = mockAppointments.map(appt => this.createAppointmentItem(appt)).join('');
    }

    /**
     * Create appointment item HTML
     * @param {Object} appointment - Appointment data
     * @returns {string} - Appointment item HTML
     */
    createAppointmentItem(appointment) {
        const lang = document.documentElement.lang || 'en';
        const formattedDate = appointment.date.toLocaleDateString(lang, { 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        const statusColors = {
            confirmed: 'bg-green-500/10 text-green-400',
            pending: 'bg-yellow-500/10 text-yellow-400',
            cancelled: 'bg-red-500/10 text-red-400'
        };

        return `
            <div class="flex items-start gap-4 p-4 bg-surface-darker rounded-lg border border-border-dark hover:border-primary/30 transition-all">
                <div class="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
                    <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between gap-2">
                        <h3 class="text-sm font-semibold text-white">${appointment.title}</h3>
                        <span class="text-xs font-medium px-2 py-1 rounded-full ${statusColors[appointment.status]}">${gettext(appointment.status)}</span>
                    </div>
                    <div class="flex items-center gap-3 mt-1">
                        <span class="text-xs text-text-muted">${formattedDate}</span>
                        <span class="text-xs text-text-muted">•</span>
                        <span class="text-xs text-text-muted">${appointment.duration} ${gettext('min')}</span>
                    </div>
                </div>
            </div>
        `;
    }
}
