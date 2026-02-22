/**
 * Dashboard Appointments Manager
 * 
 * Manages availability rules and appointment slots in the admin dashboard.
 * Supports weekly navigation and CRUD operations for rules.
 */

class DashboardAppointmentsManager {
    constructor(config) {
        this.apiUrl = config.apiUrl;
        this.saveRuleUrl = config.saveRuleUrl;
        this.updateRuleUrl = config.updateRuleUrl;
        
        this.currentWeekOffset = 0;
        this.grid = document.getElementById('appointments-grid');
        this.prevBtn = document.getElementById('prev-week-btn');
        this.nextBtn = document.getElementById('next-week-btn');
        this.weekDisplay = document.getElementById('current-week-display');
        this.rangeDisplay = document.getElementById('current-week-range');
        
        this.loader = new SimpleLoaderManager('appointments-manager-container');
        this.ruleModal = document.getElementById('rule-modal');
        this.ruleForm = document.getElementById('rule-form');
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.render();
    }

    bindEvents() {
        if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.navigate(-1));
        if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.navigate(1));
        
        // Modal events
        document.querySelectorAll('[data-modal-target]').forEach(btn => {
            btn.addEventListener('click', () => this.openModal(btn.dataset.modalTarget));
        });
        
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => this.closeModal());
        });

        if (this.ruleForm) {
            this.ruleForm.addEventListener('submit', (e) => this.handleRuleSubmit(e));
        }
    }

    navigate(direction) {
        this.currentWeekOffset += direction;
        this.render();
    }

    getWeekRange() {
        const today = new Date();
        const day = today.getDay();
        const diff = today.getDate() - day + (day === 0 ? -6 : 1); // Adjust to Monday
        const monday = new Date(today.setDate(diff + (this.currentWeekOffset * 7)));
        monday.setHours(0, 0, 0, 0);
        
        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        sunday.setHours(23, 59, 59, 999);
        
        return { start: monday, end: sunday };
    }

    formatDate(date) {
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }

    async render() {
        this.loader.show();
        const range = this.getWeekRange();
        
        // Update display
        this.weekDisplay.textContent = `${gettext('Week of')} ${this.formatDate(range.start)}`;
        this.rangeDisplay.textContent = `${this.formatDate(range.start)} - ${this.formatDate(range.end)}`;
        
        try {
            const response = await fetch(`${this.apiUrl}?start=${range.start.toISOString()}&end=${range.end.toISOString()}`);
            const data = await response.json();
            
            this.grid.innerHTML = '';
            
            for (let i = 0; i < 7; i++) {
                const currentDay = new Date(range.start);
                currentDay.setDate(range.start.getDate() + i);
                const dayCode = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'][currentDay.getDay()];
                
                const dayRules = data.rules.filter(r => r.weekday === dayCode);
                const daySlots = data.slots.filter(s => {
                    const slotDate = new Date(s.start_at);
                    return slotDate.toDateString() === currentDay.toDateString();
                });
                
                this.grid.appendChild(this.createDayColumn(currentDay, dayRules, daySlots));
            }
        } catch (error) {
            console.error('Fetch error:', error);
            window.toastManager.buildToast().setMessage(gettext('Error fetching availability')).setType('danger').show();
        } finally {
            this.loader.hide();
        }
    }

    createDayColumn(date, rules, slots) {
        const col = document.createElement('div');
        col.className = 'flex flex-col gap-3';
        
        const isToday = date.toDateString() === new Date().toDateString();
        
        col.innerHTML = `
            <div class="p-3 ${isToday ? 'bg-primary/10 border-primary/30' : 'bg-surface border-border'} border rounded-xl text-center">
                <span class="block text-[10px] font-bold uppercase tracking-wider text-text-secondary">${date.toLocaleDateString(undefined, { weekday: 'short' })}</span>
                <span class="text-base font-bold text-white">${date.getDate()}</span>
            </div>
            <div class="space-y-2">
                ${rules.map(rule => this.createRuleTag(rule)).join('')}
                ${slots.length > 0 ? '<hr class="border-border my-2">' : ''}
                ${slots.map(slot => this.createSlotTag(slot)).join('')}
            </div>
        `;
        
        return col;
    }

    createRuleTag(rule) {
        return `
            <div class="group relative flex items-center justify-between p-2 bg-surface-darker border border-border rounded-lg hover:border-primary/50 transition-colors">
                <div class="flex flex-col">
                    <span class="text-xs font-semibold text-white">${rule.start_time} - ${rule.end_time}</span>
                    <span class="text-[10px] text-text-secondary uppercase">${gettext('Recurring')}</span>
                </div>
                <button type="button" onclick="window.dashboardAppointments.editRule('${rule.id}')" class="opacity-0 group-hover:opacity-100 p-1 text-primary hover:text-white transition-all">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                </button>
            </div>
        `;
    }

    createSlotTag(slot) {
        const startTime = new Date(slot.start_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const isBooked = slot.is_booked;
        
        return `
            <div class="flex items-center justify-between p-2 ${isBooked ? 'bg-primary/20 border-primary/40' : 'bg-surface-light/5 border-border'} border rounded-lg">
                <span class="text-xs ${isBooked ? 'text-primary font-bold' : 'text-text-secondary'}">${startTime}</span>
                ${isBooked ? '<span class="text-[9px] bg-primary text-white px-1 rounded font-bold uppercase">Booked</span>' : ''}
            </div>
        `;
    }

    openModal(targetId, ruleData = null) {
        const modal = document.getElementById(targetId);
        if (!modal) return;
        
        modal.classList.remove('hidden');
        if (ruleData) {
            document.getElementById('rule-id').value = ruleData.id;
            document.getElementById('rule-weekday').value = ruleData.weekday;
            document.getElementById('rule-start-time').value = ruleData.start_time;
            document.getElementById('rule-end-time').value = ruleData.end_time;
            document.getElementById('rule-active').checked = ruleData.is_active;
        } else {
            this.ruleForm.reset();
            document.getElementById('rule-id').value = '';
        }
    }

    closeModal() {
        this.ruleModal.classList.add('hidden');
    }

    async handleRuleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(this.ruleForm);
        const ruleId = formData.get('id');
        const url = ruleId ? this.updateRuleUrl.replace('{id}', ruleId) : this.saveRuleUrl;
        
        this.loader.show();
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            
            if (response.ok) {
                window.toastManager.buildToast().setMessage(gettext('Rule saved successfully')).setType('success').show();
                this.closeModal();
                this.render();
            } else {
                const data = await response.json();
                let errorMsg = gettext('Validation error');
                
                if (data && typeof data === 'object') {
                    // Extract first error message from field errors
                    const firstFieldErrors = Object.values(data)[0];
                    if (Array.isArray(firstFieldErrors) && firstFieldErrors[0]) {
                        errorMsg = firstFieldErrors[0].message || firstFieldErrors[0];
                    } else if (typeof data.message === 'string') {
                        errorMsg = data.message;
                    }
                }
                
                window.toastManager.buildToast().setMessage(errorMsg).setType('danger').show();
            }
        } catch (error) {
            window.toastManager.buildToast().setMessage(gettext('Server error')).setType('danger').show();
        } finally {
            this.loader.hide();
        }
    }

    async editRule(id) {
        this.loader.show();
        try {
            const range = this.getWeekRange();
            const response = await fetch(`${this.apiUrl}?start=${range.start.toISOString()}&end=${range.end.toISOString()}`);
            const data = await response.json();
            
            const rule = data.rules.find(r => r.id === id);
            if (rule) {
                this.openModal('rule-modal', rule);
            } else {
                window.toastManager.buildToast().setMessage(gettext('Rule not found')).setType('danger').show();
            }
        } catch (error) {
            window.toastManager.buildToast().setMessage(gettext('Error fetching rule')).setType('danger').show();
        } finally {
            this.loader.hide();
        }
    }
}

// Global hook
window.dashboardAppointments = null;

document.addEventListener('DOMContentLoaded', () => {
    // This is handled in the template usually, but we ensure instance is accessible
});
