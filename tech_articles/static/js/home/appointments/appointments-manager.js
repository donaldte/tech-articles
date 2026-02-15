/**
 * Appointments Manager
 *
 * Manages the weekly appointment calendar view, allowing users to browse
 * and select available time slots.
 *
 * Features:
 * - OOP-based architecture
 * - Week navigation (previous/next)
 * - Dynamic time slot rendering
 * - Internationalization support
 * - Responsive design
 *
 * @author Tech Articles Team
 * @version 1.0.0
 */

class AppointmentsManager {
    /**
     * Initialize the appointments manager
     * @param {Object} config - Configuration object
     * @param {string} config.detailUrlTemplate - URL template for detail page
     */
    constructor(config) {
        this.detailUrlTemplate = config.detailUrlTemplate;
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
     * Calculate end time given start time and duration
     * @param {string} startTime - Start time in HH:MM format
     * @param {number} duration - Duration in minutes
     * @returns {string} - End time in HH:MM format
     */
    calculateEndTime(startTime, duration) {
        const [hours, minutes] = startTime.split(':').map(Number);
        const endDate = new Date();
        endDate.setHours(hours, minutes + duration, 0, 0);
        return endDate.toTimeString().slice(0, 5);
    }

    /**
     * Generate mock appointment slots for a day
     * @param {Date} date - Date for the slots
     * @returns {Array} - Array of time slots
     */
    generateMockSlots(date) {
        const slots = [];
        const dayOfWeek = date.getDay();

        // Reset time to start of day for comparison
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const compareDate = new Date(date);
        compareDate.setHours(0, 0, 0, 0);

        // Skip Sundays or past dates
        if (dayOfWeek === 0 || compareDate < today) {
            return slots;
        }

        const duration = 60;

        // Generate morning slots (9:00 - 12:00)
        const morningSlots = ['09:00', '10:00', '11:00'];
        morningSlots.forEach((time, index) => {
            slots.push({
                id: Math.random().toString(36).substr(2, 9),
                startTime: time,
                endTime: this.calculateEndTime(time, duration),
                period: gettext('Morning'),
                available: Math.random() > 0.3, // 70% availability
                duration: duration,
                price: 99.00
            });
        });

        // Generate afternoon slots (14:00 - 17:00)
        const afternoonSlots = ['14:00', '15:00', '16:00'];
        afternoonSlots.forEach((time, index) => {
            slots.push({
                id: Math.random().toString(36).substr(2, 9),
                startTime: time,
                endTime: this.calculateEndTime(time, duration),
                period: gettext('Afternoon'),
                available: Math.random() > 0.4, // 60% availability
                duration: duration,
                price: 99.00
            });
        });

        // Generate evening slots (18:00 - 20:00) on weekdays only
        if (dayOfWeek >= 1 && dayOfWeek <= 5) {
            const eveningSlots = ['18:00', '19:00'];
            eveningSlots.forEach((time, index) => {
                slots.push({
                    id: Math.random().toString(36).substr(2, 9),
                    startTime: time,
                    endTime: this.calculateEndTime(time, duration),
                    period: gettext('Evening'),
                    available: Math.random() > 0.5, // 50% availability
                    duration: duration,
                    price: 99.00
                });
            });
        }

        return slots;
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
        const availableSlots = slots.filter(slot => slot.available);
        const hasSlots = availableSlots.length > 0;

        card.innerHTML = `
            <div class="bg-linear-to-r from-primary/10 to-primary/5 px-4 py-3 border-b border-border">
                <h3 class="text-lg font-semibold text-white">${dayName}</h3>
                <p class="text-sm text-gray-300">${formattedDate}</p>
            </div>
            <div class="p-4 space-y-2 max-h-100 overflow-y-auto">
                ${hasSlots
                    ? availableSlots.map(slot => this.createSlotButton(slot, date)).join('')
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
        const detailUrl = this.detailUrlTemplate.replace('{slotId}', slot.id);

        if (slot.available) {
            return `
                <a href="${detailUrl}" class="block w-full px-4 py-3 border border-white/10 bg-surface-darker hover:bg-surface-light hover:border-primary/50 rounded-lg transition-all group">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <p class="text-base font-semibold text-white group-hover:text-primary transition-colors mb-1">${slot.startTime} - ${slot.endTime}</p>
                            <p class="text-xs text-text-secondary">${slot.duration} ${gettext('min')}</p>
                        </div>
                        <div class="text-right">
                            <p class="text-lg font-bold text-primary">$${slot.price.toFixed(2)}</p>
                            <p class="text-xs text-text-secondary">${gettext('USD')}</p>
                        </div>
                    </div>
                </a>
            `;
        } else {
            return `
                <button type="button" disabled class="w-full px-4 py-3 border border-white/5 bg-surface-darker/30 rounded-lg cursor-not-allowed opacity-60">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <p class="text-base font-semibold text-gray-300 line-through mb-1">${slot.startTime} - ${slot.endTime}</p>
                            <p class="text-xs text-gray-300">${gettext('Unavailable')}</p>
                        </div>
                        <div class="text-right">
                            <svg class="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </div>
                    </div>
                </button>
            `;
        }
    }

    /**
     * Render the week view
     */
    renderWeek() {
        if (!this.appointmentsGrid) return;

        const weekStart = this.getWeekStartDate();
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);

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

        // Clear existing content
        this.appointmentsGrid.innerHTML = '';

        // Generate day cards for the week (Monday to Saturday)
        let hasAnySlots = false;
        for (let i = 0; i < 7; i++) {
            const currentDate = new Date(weekStart);
            currentDate.setDate(weekStart.getDate() + i);

            // Skip Sunday (index 0)
            if (currentDate.getDay() === 0) continue;

            const slots = this.generateMockSlots(currentDate);
            const availableSlots = slots.filter(slot => slot.available);

            if (availableSlots.length > 0) {
                hasAnySlots = true;
            }

            const dayCard = this.createDayCard(currentDate, slots);
            this.appointmentsGrid.appendChild(dayCard);
        }
    }
}
