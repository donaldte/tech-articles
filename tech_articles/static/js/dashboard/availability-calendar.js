/**
 * Weekly Calendar for Availability Settings
 * Manages time slot configuration with interactive calendar interface
 */

(function() {
    'use strict';

    const WEEKDAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
    const WEEKDAY_NAMES = {
        'mon': 'Monday',
        'tue': 'Tuesday',
        'wed': 'Wednesday',
        'thu': 'Thursday',
        'fri': 'Friday',
        'sat': 'Saturday',
        'sun': 'Sunday'
    };
    const START_HOUR = 0;
    const END_HOUR = 24;

    let availabilityRules = [];

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initCalendar();
        loadAvailabilityRules();
        setupEventListeners();
    });

    /**
     * Initialize the calendar grid
     */
    function initCalendar() {
        const calendarBody = document.getElementById('calendar-body');
        if (!calendarBody) return;

        let html = '';
        
        // Create hourly grid
        for (let hour = START_HOUR; hour < END_HOUR; hour++) {
            html += `<div class="grid grid-cols-8 gap-2 border-b border-gray-100">`;
            
            // Time label
            html += `<div class="text-xs text-gray-500 py-2 text-center">${formatHour(hour)}</div>`;
            
            // Day cells
            WEEKDAYS.forEach(day => {
                html += `<div class="calendar-cell relative min-h-[40px] border border-gray-200 rounded hover:bg-blue-50 cursor-pointer transition-colors" 
                              data-day="${day}" 
                              data-hour="${hour}">
                         </div>`;
            });
            
            html += `</div>`;
        }
        
        calendarBody.innerHTML = html;
    }

    /**
     * Load availability rules from server
     */
    function loadAvailabilityRules() {
        fetch('/dashboard/appointments/api/rules/')
            .then(response => response.json())
            .then(data => {
                availabilityRules = data.rules || [];
                renderCalendarRules();
            })
            .catch(error => {
                console.error('Error loading availability rules:', error);
                showNotification('Error loading availability rules', 'error');
            });
    }

    /**
     * Render availability rules on the calendar
     */
    function renderCalendarRules() {
        // Clear existing highlights
        document.querySelectorAll('.calendar-cell').forEach(cell => {
            cell.classList.remove('bg-green-100', 'border-green-400');
            cell.innerHTML = '';
        });

        // Highlight cells based on rules
        availabilityRules.forEach(rule => {
            const startHour = parseInt(rule.start_time.split(':')[0]);
            const endHour = parseInt(rule.end_time.split(':')[0]);
            
            for (let hour = startHour; hour < endHour; hour++) {
                const cell = document.querySelector(`.calendar-cell[data-day="${rule.weekday}"][data-hour="${hour}"]`);
                if (cell) {
                    cell.classList.add('bg-green-100', 'border-green-400');
                    if (hour === startHour) {
                        cell.innerHTML = `<span class="text-xs text-green-700 font-medium">${rule.start_time} - ${rule.end_time}</span>`;
                    }
                }
            }
        });
    }

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // Configuration form
        const configForm = document.getElementById('config-form');
        if (configForm) {
            configForm.addEventListener('submit', handleConfigSubmit);
        }

        // Add availability button
        const addAvailabilityBtn = document.getElementById('add-availability-btn');
        if (addAvailabilityBtn) {
            addAvailabilityBtn.addEventListener('click', openAvailabilityModal);
        }

        // Availability form
        const availabilityForm = document.getElementById('availability-form');
        if (availabilityForm) {
            availabilityForm.addEventListener('submit', handleAvailabilitySubmit);
        }

        // Add exception button
        const addExceptionBtn = document.getElementById('add-exception-btn');
        if (addExceptionBtn) {
            addExceptionBtn.addEventListener('click', openExceptionModal);
        }

        // Exception form
        const exceptionForm = document.getElementById('exception-form');
        if (exceptionForm) {
            exceptionForm.addEventListener('submit', handleExceptionSubmit);
        }
    }

    /**
     * Handle configuration form submission
     */
    function handleConfigSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        
        fetch('/dashboard/appointments/api/config/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
            } else {
                showNotification('Error saving configuration', 'error');
            }
        })
        .catch(error => {
            console.error('Error saving configuration:', error);
            showNotification('Error saving configuration', 'error');
        });
    }

    /**
     * Handle availability rule form submission
     */
    function handleAvailabilitySubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            weekday: formData.get('weekday'),
            start_time: formData.get('start_time'),
            end_time: formData.get('end_time'),
            is_recurring: formData.get('is_recurring') ? true : false,
            is_active: true
        };
        
        fetch('/dashboard/appointments/api/rules/', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                closeAvailabilityModal();
                e.target.reset();
                loadAvailabilityRules();
                addRuleToList(data.rule);
            } else {
                showNotification('Error adding availability rule', 'error');
            }
        })
        .catch(error => {
            console.error('Error adding availability rule:', error);
            showNotification('Error adding availability rule', 'error');
        });
    }

    /**
     * Handle exception date form submission
     */
    function handleExceptionSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            date: formData.get('date'),
            reason: formData.get('reason'),
            is_active: true
        };
        
        fetch('/dashboard/appointments/api/exceptions/', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                closeExceptionModal();
                e.target.reset();
                addExceptionToList(data.exception);
            } else {
                showNotification('Error adding exception date', 'error');
            }
        })
        .catch(error => {
            console.error('Error adding exception date:', error);
            showNotification('Error adding exception date', 'error');
        });
    }

    /**
     * Delete availability rule
     */
    window.deleteRule = function(ruleId) {
        const confirmMsg = window.i18nMessages?.confirmDeleteRule || 'Are you sure you want to delete this availability rule?';
        if (!confirm(confirmMsg)) {
            return;
        }

        fetch(`/dashboard/appointments/api/rules/?id=${ruleId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                document.querySelector(`[data-rule-id="${ruleId}"]`)?.remove();
                loadAvailabilityRules();
            } else {
                showNotification('Error deleting rule', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting rule:', error);
            showNotification('Error deleting rule', 'error');
        });
    };

    /**
     * Delete exception date
     */
    window.deleteException = function(exceptionId) {
        const confirmMsg = window.i18nMessages?.confirmDeleteException || 'Are you sure you want to delete this exception date?';
        if (!confirm(confirmMsg)) {
            return;
        }

        fetch(`/dashboard/appointments/api/exceptions/?id=${exceptionId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                document.querySelector(`[data-exception-id="${exceptionId}"]`)?.remove();
            } else {
                showNotification('Error deleting exception', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting exception:', error);
            showNotification('Error deleting exception', 'error');
        });
    };

    /**
     * Add rule to the list UI
     */
    function addRuleToList(rule) {
        const rulesList = document.getElementById('rules-list');
        if (!rulesList) return;

        const recurringText = window.i18nMessages?.recurring || 'Recurring';
        const deleteText = window.i18nMessages?.delete || 'Delete';

        const ruleHtml = `
            <div class="flex items-center justify-between bg-gray-50 p-3 rounded-md" data-rule-id="${rule.id}">
                <div class="flex items-center space-x-3">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ${WEEKDAY_NAMES[rule.weekday]}
                    </span>
                    <span class="text-sm text-gray-700">
                        ${rule.start_time} - ${rule.end_time}
                    </span>
                    ${rule.is_recurring ? `<span class="text-xs text-gray-500">(${recurringText})</span>` : ''}
                </div>
                <button onclick="deleteRule('${rule.id}')" class="text-red-600 hover:text-red-800 text-sm">
                    ${deleteText}
                </button>
            </div>
        `;

        // Remove "no rules" message if present
        const noRulesMsg = rulesList.querySelector('p.text-gray-500');
        if (noRulesMsg) {
            noRulesMsg.remove();
        }

        rulesList.insertAdjacentHTML('beforeend', ruleHtml);
    }

    /**
     * Add exception to the list UI
     */
    function addExceptionToList(exception) {
        const exceptionsList = document.getElementById('exceptions-list');
        if (!exceptionsList) return;

        const deleteText = window.i18nMessages?.delete || 'Delete';

        const exceptionHtml = `
            <div class="flex items-center justify-between bg-gray-50 p-3 rounded-md" data-exception-id="${exception.id}">
                <div class="flex items-center space-x-3">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        ${exception.date}
                    </span>
                    <span class="text-sm text-gray-700">${exception.reason}</span>
                </div>
                <button onclick="deleteException('${exception.id}')" class="text-red-600 hover:text-red-800 text-sm">
                    ${deleteText}
                </button>
            </div>
        `;

        // Remove "no exceptions" message if present
        const noExceptionsMsg = exceptionsList.querySelector('p.text-gray-500');
        if (noExceptionsMsg) {
            noExceptionsMsg.remove();
        }

        exceptionsList.insertAdjacentHTML('beforeend', exceptionHtml);
    }

    /**
     * Modal management functions
     */
    function openAvailabilityModal() {
        document.getElementById('availability-modal')?.classList.remove('hidden');
    }

    window.closeAvailabilityModal = function() {
        document.getElementById('availability-modal')?.classList.add('hidden');
    };

    function openExceptionModal() {
        document.getElementById('exception-modal')?.classList.remove('hidden');
    }

    window.closeExceptionModal = function() {
        document.getElementById('exception-modal')?.classList.add('hidden');
    };

    /**
     * Utility functions
     */
    function formatHour(hour) {
        return `${hour.toString().padStart(2, '0')}:00`;
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            'bg-blue-500'
        } text-white`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
})();
