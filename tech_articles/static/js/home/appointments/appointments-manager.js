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
     * @param {Object} config.i18n - Internationalization strings
     */
    constructor(config) {
        this.config = config;
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
        this.bindEvents();
        this.renderWeek();
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
            this.config.i18n.sunday,
            this.config.i18n.monday,
            this.config.i18n.tuesday,
            this.config.i18n.wednesday,
            this.config.i18n.thursday,
            this.config.i18n.friday,
            this.config.i18n.saturday,
        ];
        return days[dayIndex];
    }

    /**
     * Generate mock appointment slots for a day
     * @param {Date} date - Date for the slots
     * @returns {Array} - Array of time slots
     */
    generateMockSlots(date) {
        const slots = [];
        const dayOfWeek = date.getDay();
        
        // Skip Sundays or past dates
        if (dayOfWeek === 0 || date < new Date()) {
            return slots;
        }

        // Generate morning slots (9:00 - 12:00)
        const morningSlots = ['09:00', '10:00', '11:00'];
        morningSlots.forEach((time, index) => {
            slots.push({
                id: Math.random().toString(36).substr(2, 9),
                time: time,
                period: this.config.i18n.morning,
                available: Math.random() > 0.3, // 70% availability
                duration: 60,
                price: 99.00
            });
        });

        // Generate afternoon slots (14:00 - 17:00)
        const afternoonSlots = ['14:00', '15:00', '16:00'];
        afternoonSlots.forEach((time, index) => {
            slots.push({
                id: Math.random().toString(36).substr(2, 9),
                time: time,
                period: this.config.i18n.afternoon,
                available: Math.random() > 0.4, // 60% availability
                duration: 60,
                price: 99.00
            });
        });

        // Generate evening slots (18:00 - 20:00) on weekdays only
        if (dayOfWeek >= 1 && dayOfWeek <= 5) {
            const eveningSlots = ['18:00', '19:00'];
            eveningSlots.forEach((time, index) => {
                slots.push({
                    id: Math.random().toString(36).substr(2, 9),
                    time: time,
                    period: this.config.i18n.evening,
                    available: Math.random() > 0.5, // 50% availability
                    duration: 60,
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
            <div class="bg-gradient-to-r from-primary/10 to-primary/5 px-4 py-3 border-b border-border">
                <h3 class="text-lg font-semibold text-white">${dayName}</h3>
                <p class="text-sm text-text-muted">${formattedDate}</p>
            </div>
            <div class="p-4 space-y-2 max-h-[400px] overflow-y-auto">
                ${hasSlots 
                    ? availableSlots.map(slot => this.createSlotButton(slot, date)).join('') 
                    : `<p class="text-center py-8 text-text-muted text-sm">${this.config.i18n.noSlots}</p>`
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
        const detailUrl = this.config.detailUrlTemplate.replace('{slotId}', slot.id);
        const statusClass = slot.available ? 'bg-surface-darker hover:bg-primary/10 border-primary/30' : 'bg-surface-darker/50 border-border/50 opacity-50 cursor-not-allowed';
        const statusIcon = slot.available 
            ? '<svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
            : '<svg class="w-4 h-4 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>';

        if (slot.available) {
            return `
                <a href="${detailUrl}" class="block w-full px-4 py-3 border ${statusClass} rounded-lg transition-all group">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm font-semibold text-white group-hover:text-primary transition-colors">${slot.time}</p>
                            <p class="text-xs text-text-muted">${slot.duration} ${gettext('min')} • $${slot.price.toFixed(2)}</p>
                        </div>
                        ${statusIcon}
                    </div>
                </a>
            `;
        } else {
            return `
                <button type="button" disabled class="w-full px-4 py-3 border ${statusClass} rounded-lg cursor-not-allowed">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm font-semibold text-text-muted">${slot.time}</p>
                            <p class="text-xs text-text-muted">${this.config.i18n.unavailable}</p>
                        </div>
                        ${statusIcon}
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
            this.currentWeekDisplay.textContent = `${this.config.i18n.weekOf} ${this.formatDate(weekStart)}`;
        }
        if (this.currentWeekRange) {
            this.currentWeekRange.textContent = this.formatDateRange(weekStart, weekEnd);
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

        // Show/hide no slots message
        if (this.noSlotsMessage) {
            if (hasAnySlots) {
                this.noSlotsMessage.classList.add('hidden');
            } else {
                this.noSlotsMessage.classList.remove('hidden');
            }
        }
    }
}
