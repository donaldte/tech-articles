class AppointmentsManager {
    /**
     * Initialize the appointments manager
     * @param {Object} config - Configuration object
     * @param {string} config.detailUrlTemplate - URL template for detail page
     * @param {string} config.slotsApiUrl - URL for slots API
     */
    constructor(config) {
        this.serviceSelectionUrl = config.serviceSelectionUrl;
        this.slotsApiUrl = config.slotsApiUrl;
        this.currentWeekOffset = 0;
        this.appointmentsGrid = document.getElementById('appointments-grid');
        this.noSlotsMessage = document.getElementById('no-slots-message');
        this.prevWeekBtn = document.getElementById('prev-week-btn');
        this.nextWeekBtn = document.getElementById('next-week-btn');
        this.currentWeekDisplay = document.getElementById('current-week-display');
        this.currentWeekRange = document.getElementById('current-week-range');

        this.init();
    }

    /**
     * Initialize the manager
     */
    init() {
        this.displayTimezone();
        this.bindEvents();
        this.renderWeek();
    }

    /**
     * Display the user's timezone
     */
    displayTimezone() {
        const timezoneDisplay = document.getElementById('timezone-display');
        if (timezoneDisplay) {
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            const offset = new Date().getTimezoneOffset();
            const offsetHours = Math.abs(Math.floor(offset / 60));
            const offsetMinutes = Math.abs(offset % 60);
            const offsetSign = offset <= 0 ? '+' : '-';
            const offsetString = `UTC${offsetSign}${offsetHours.toString().padStart(2, '0')}:${offsetMinutes.toString().padStart(2, '0')}`;
            timezoneDisplay.textContent = `${timezone} (${offsetString})`;
        }
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        if (this.prevWeekBtn) {
            this.prevWeekBtn.addEventListener('click', () => this.navigateWeek(-1));
        }

        if (this.nextWeekBtn) {
            this.nextWeekBtn.addEventListener('click', () => this.navigateWeek(1));
        }
    }

    /**
     * Navigate to a different week
     * @param {number} direction - Direction to navigate (-1 for previous, 1 for next)
     */
    navigateWeek(direction) {
        // Prevent navigating to past weeks
        if (direction === -1 && this.currentWeekOffset <= 0) {
            return;
        }
        this.currentWeekOffset += direction;
        this.renderWeek();
    }

    /**
     * Get the start date of the current week
     * @returns {Date} - Start date of the week (Monday)
     */
    getWeekStartDate() {
        const today = new Date();
        const currentDay = today.getDay();
        const daysFromMonday = currentDay === 0 ? 6 : currentDay - 1;

        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - daysFromMonday + (this.currentWeekOffset * 7));
        weekStart.setHours(0, 0, 0, 0);

        return weekStart;
    }

    /**
     * Format date for display
     * @param {Date} date - Date to format
     * @returns {string} - Formatted date string
     */
    formatDate(date) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString(document.documentElement.lang || 'en', options);
    }

    /**
     * Format date range for display
     * @param {Date} startDate - Start date
     * @param {Date} endDate - End date
     * @returns {string} - Formatted date range
     */
    formatDateRange(startDate, endDate) {
        const options = { month: 'short', day: 'numeric' };
        const start = startDate.toLocaleDateString(document.documentElement.lang || 'en', options);
        const end = endDate.toLocaleDateString(document.documentElement.lang || 'en', options);
        return `${start} - ${end}`;
    }

    /**
     * Get day name
     * @param {number} dayIndex - Day index (0-6)
     * @returns {string} - Day name
     */
    getDayName(dayIndex) {
        const days = [
            gettext('Sunday'),
            gettext('Monday'),
            gettext('Tuesday'),
            gettext('Wednesday'),
            gettext('Thursday'),
            gettext('Friday'),
            gettext('Saturday'),
        ];
        return days[dayIndex];
    }

    /**
     * Create a day card element
     * @param {Date} date - Date for the card
     * @param {Array} slots - Time slots for the day
     * @returns {HTMLElement} - Day card element
     */
    createDayCard(date, slots) {
        const card = document.createElement('div');
        card.className = 'bg-surface border border-border rounded-xl overflow-hidden hover:border-primary/30 transition-colors';

        const dayName = this.getDayName(date.getDay());
        const formattedDate = this.formatDate(date);
        const hasSlots = slots.length > 0;

        card.innerHTML = `
            <div class="bg-linear-to-r from-primary/10 to-primary/5 px-4 py-3 border-b border-border">
                <h3 class="text-lg font-semibold text-white">${dayName}</h3>
                <p class="text-sm text-gray-300">${formattedDate}</p>
            </div>
            <div class="p-4 space-y-2 max-h-100 overflow-y-auto">
                ${hasSlots
                    ? slots.map(slot => this.createSlotButton(slot, date)).join('')
                    : `<p class="text-center py-8 text-gray-300 text-sm">${gettext('No slots available')}</p>`
                }
            </div>
        `;

        return card;
    }

    /**
     * Create a slot button element
     * @param {Object} slot - Slot data
     * @param {Date} date - Date for the slot
     * @returns {string} - Slot button HTML
     */
    createSlotButton(slot, date) {
        const url = new URL(this.serviceSelectionUrl, window.location.origin);
        url.searchParams.append('start', slot.start_at);
        url.searchParams.append('end', slot.end_at);

        return `
            <a href="${url.toString()}" class="block w-full px-4 py-3 border border-white/10 bg-surface-darker hover:bg-surface-light hover:border-primary/50 rounded-lg transition-all group text-center">
                <p class="text-base font-semibold text-white group-hover:text-primary transition-colors">${slot.startTime} - ${slot.endTime}</p>
                <p class="text-[10px] text-text-secondary uppercase tracking-widest mt-1">${gettext('Available')}</p>
            </a>
        `;
    }

    /**
     * Render the week view
     */
    async renderWeek() {
        if (!this.appointmentsGrid) return;

        const weekStart = this.getWeekStartDate();
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        weekEnd.setHours(23, 59, 59, 999);

        // Update week display
        if (this.currentWeekDisplay) {
            this.currentWeekDisplay.textContent = `${gettext('Week of')} ${this.formatDate(weekStart)}`;
        }
        if (this.currentWeekRange) {
            this.currentWeekRange.textContent = this.formatDateRange(weekStart, weekEnd);
        }

        // Disable/enable previous week button
        if (this.prevWeekBtn) {
            if (this.currentWeekOffset <= 0) {
                this.prevWeekBtn.disabled = true;
                this.prevWeekBtn.classList.add('opacity-50', 'cursor-not-allowed');
                this.prevWeekBtn.classList.remove('hover:bg-surface-dark');
            } else {
                this.prevWeekBtn.disabled = false;
                this.prevWeekBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                this.prevWeekBtn.classList.add('hover:bg-surface-dark');
            }
        }

        // Clear existing content and show loading if possible
        this.appointmentsGrid.innerHTML = `
            <div class="col-span-full py-12 flex flex-col items-center justify-center space-y-4">
                <div class="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                <p class="text-text-secondary italic">${gettext('Fetching available slots...')}</p>
            </div>
        `;

        try {
            const response = await fetch(`${this.slotsApiUrl}?start=${weekStart.toISOString()}&end=${weekEnd.toISOString()}`);
            const data = await response.json();
            
            this.appointmentsGrid.innerHTML = '';
            
            if (data.slots && data.slots.length > 0) {
                for (let i = 0; i < 7; i++) {
                    const currentDate = new Date(weekStart);
                    currentDate.setDate(weekStart.getDate() + i);

                    const daySlots = data.slots.filter(slot => slot.date === currentDate.toISOString().split('T')[0]);
                    const dayCard = this.createDayCard(currentDate, daySlots);
                    this.appointmentsGrid.appendChild(dayCard);
                }
            } else {
                this.appointmentsGrid.innerHTML = `
                    <div class="col-span-full py-24 text-center">
                        <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2-2v12a2 2 0 002 2z"/>
                        </svg>
                        <p class="text-lg font-medium text-white mb-2">${gettext('No availability found for this week')}</p>
                        <p class="text-text-secondary">${gettext('Please try selecting a different week or check back later.')}</p>
                    </div>
                `;
            }
        } catch (error) {
            this.appointmentsGrid.innerHTML = `
                <div class="col-span-full py-24 text-center">
                    <p class="text-danger">${gettext('An error occurred while fetching availability. Please try again.')}</p>
                </div>
            `;
        }
    }
}
