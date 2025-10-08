/**
 * OBCMS Modern Calendar
 * Version: 1.0
 * Purpose: Modern calendar UI with multi-view support, filters, and detail panel
 * Author: Claude Code (AI-assisted development)
 * Date: 2025-10-06
 */

(function(window) {
    'use strict';

    /**
     * ModernCalendar Class
     * Manages calendar initialization, view switching, filtering, and event display
     */
    class ModernCalendar {
        constructor(options) {
            this.options = Object.assign({
                calendarEl: null,
                miniCalendarEl: null,
                eventsFeedUrl: '',
                createUrl: '',
                detailPanelEl: null,
                detailContentEl: null,
                detailBackdropEl: null,
                modalEl: null,
                modalContentEl: null,
                storageKey: 'calendar_view_mode',
                defaultView: 'dayGridMonth',
                onEventClick: null,
                onViewChange: null
            }, options);

            this.calendar = null;
            this.miniCalendar = null;
            this.currentView = this.loadViewPreference();
            this.activeFilters = {
                project: true,
                activity: true,
                task: true,
                completed: false
            };

            this.init();
        }

        /**
         * Initialize calendar and event listeners
         */
        init() {
            console.log('🚀 Initializing Modern Calendar...');

            this.initMainCalendar();
            this.initMiniCalendar();
            this.initViewSwitcher();
            this.initFilters();
            this.initDetailPanel();
            this.initModal();
            this.initTodayButton();

            console.log('✅ Modern Calendar initialized successfully');
        }

        /**
         * Initialize main FullCalendar instance
         */
        initMainCalendar() {
            if (!this.options.calendarEl) {
                console.error('❌ Calendar element not found');
                return;
            }

            const self = this;

            this.calendar = new FullCalendar.Calendar(this.options.calendarEl, {
                initialView: this.currentView,
                headerToolbar: {
                    left: 'prev,next',
                    center: 'title',
                    right: '' // View buttons in separate UI
                },
                height: 'auto',
                dayMaxEvents: 4,
                moreLinkClick: 'popover',
                eventDisplay: 'block',
                displayEventTime: true,
                displayEventEnd: false,

                // Multi-month year view configuration
                multiMonthMaxColumns: 3,
                multiMonthMinWidth: 300,

                // Events source
                events: function(info, successCallback, failureCallback) {
                    self.fetchEvents(info, successCallback, failureCallback);
                },

                // Event click handler
                eventClick: function(info) {
                    info.jsEvent.preventDefault();
                    self.handleEventClick(info);
                },

                // Event content rendering
                eventContent: function(arg) {
                    return self.buildEventContent(arg);
                },

                // Event mounting (for attributes and tooltips)
                eventDidMount: function(info) {
                    self.setupEventAttributes(info);
                },

                // Date click handler
                dateClick: function(info) {
                    self.handleDateClick(info);
                },

                // View change handler
                datesSet: function(dateInfo) {
                    if (self.options.onViewChange) {
                        self.options.onViewChange(dateInfo);
                    }
                    self.updateMiniCalendarDate(dateInfo.start);
                }
            });

            this.calendar.render();
            console.log('✅ Main calendar rendered');
        }

        /**
         * Initialize mini calendar for quick navigation
         */
        initMiniCalendar() {
            if (!this.options.miniCalendarEl) {
                console.warn('⚠️  Mini calendar element not found');
                return;
            }

            const self = this;

            this.miniCalendar = new FullCalendar.Calendar(this.options.miniCalendarEl, {
                initialView: 'dayGridMonth',
                headerToolbar: {
                    left: 'prev',
                    center: 'title',
                    right: 'next'
                },
                height: 'auto',
                fixedWeekCount: false,
                showNonCurrentDates: false,

                // Date click handler - navigate main calendar
                dateClick: function(info) {
                    self.calendar.gotoDate(info.dateStr);
                    self.highlightMiniCalendarDate(info.date);
                }
            });

            this.miniCalendar.render();
            console.log('✅ Mini calendar rendered');
        }

        /**
         * Initialize view switcher buttons
         */
        initViewSwitcher() {
            const viewButtons = {
                viewMonthBtn: 'dayGridMonth',
                viewWeekBtn: 'timeGridWeek',
                viewDayBtn: 'timeGridDay',
                viewYearBtn: 'multiMonthYear'
            };

            const self = this;

            Object.keys(viewButtons).forEach(btnId => {
                const btn = document.getElementById(btnId);
                if (btn) {
                    btn.addEventListener('click', function() {
                        const view = viewButtons[btnId];
                        self.switchView(view);
                    });
                }
            });

            // Set initial active state
            this.updateViewButtonStates();
        }

        /**
         * Switch calendar view
         */
        switchView(viewName) {
            if (!this.calendar) return;

            this.calendar.changeView(viewName);
            this.currentView = viewName;
            this.saveViewPreference(viewName);
            this.updateViewButtonStates();

            console.log('📅 Switched to view:', viewName);
        }

        /**
         * Update view button active states
         */
        updateViewButtonStates() {
            const viewButtons = document.querySelectorAll('.view-btn');
            viewButtons.forEach(btn => {
                const viewType = btn.getAttribute('data-view');
                if (viewType === this.currentView) {
                    btn.classList.add('active');
                    btn.setAttribute('aria-pressed', 'true');
                } else {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-pressed', 'false');
                }
            });
        }

        /**
         * Initialize filter checkboxes
         */
        initFilters() {
            const filterCheckboxes = document.querySelectorAll('[data-filter]');
            const self = this;

            filterCheckboxes.forEach(checkbox => {
                const filterType = checkbox.getAttribute('data-filter');
                checkbox.checked = this.activeFilters[filterType] || false;

                checkbox.addEventListener('change', function() {
                    self.activeFilters[filterType] = checkbox.checked;
                    self.applyFilters();
                });
            });

            // Clear filters button
            const clearBtn = document.getElementById('clearFiltersBtn');
            if (clearBtn) {
                clearBtn.addEventListener('click', function() {
                    self.clearFilters();
                });
            }
        }

        /**
         * Apply filters to calendar events
         */
        applyFilters() {
            if (!this.calendar) return;

            const allEvents = this.calendar.getEvents();

            allEvents.forEach(event => {
                const workType = event.extendedProps.workType || '';
                const status = event.extendedProps.status || '';
                let show = true;

                // Type filters
                if (workType.includes('project')) {
                    show = show && this.activeFilters.project;
                } else if (workType.includes('activity')) {
                    show = show && this.activeFilters.activity;
                } else if (workType.includes('task')) {
                    show = show && this.activeFilters.task;
                }

                // Completed filter
                if (!this.activeFilters.completed && status === 'completed') {
                    show = false;
                }

                event.setProp('display', show ? 'auto' : 'none');
            });

            console.log('🔍 Filters applied:', this.activeFilters);
        }

        /**
         * Clear all filters
         */
        clearFilters() {
            this.activeFilters = {
                project: true,
                activity: true,
                task: true,
                completed: false
            };

            // Update checkboxes
            const filterCheckboxes = document.querySelectorAll('[data-filter]');
            filterCheckboxes.forEach(checkbox => {
                const filterType = checkbox.getAttribute('data-filter');
                checkbox.checked = this.activeFilters[filterType];
            });

            this.applyFilters();
            console.log('🧹 Filters cleared');
        }

        /**
         * Initialize detail panel
         */
        initDetailPanel() {
            const closeBtn = document.getElementById('closeDetailPanelBtn');
            const backdrop = this.options.detailBackdropEl;
            const panel = this.options.detailPanelEl;

            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.closeDetailPanel());
            }

            if (backdrop) {
                backdrop.addEventListener('click', () => this.closeDetailPanel());
            }

            // Escape key to close
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && panel && panel.classList.contains('open')) {
                    this.closeDetailPanel();
                }
            });
        }

        /**
         * Open detail panel with event data
         */
        openDetailPanel(event) {
            const panel = this.options.detailPanelEl;
            const content = this.options.detailContentEl;
            const backdrop = this.options.detailBackdropEl;

            if (!panel || !content) return;

            // Build detail content
            const html = this.buildDetailPanelContent(event);
            content.innerHTML = html;

            // Show panel
            panel.classList.add('open');
            panel.setAttribute('aria-hidden', 'false');

            if (backdrop) {
                backdrop.classList.remove('hidden');
                backdrop.classList.add('visible');
            }

            // Focus management
            panel.focus();
        }

        /**
         * Close detail panel
         */
        closeDetailPanel() {
            const panel = this.options.detailPanelEl;
            const backdrop = this.options.detailBackdropEl;

            if (panel) {
                panel.classList.remove('open');
                panel.setAttribute('aria-hidden', 'true');
            }

            if (backdrop) {
                backdrop.classList.add('hidden');
                backdrop.classList.remove('visible');
            }
        }

        /**
         * Build detail panel content HTML
         */
        buildDetailPanelContent(event) {
            const props = event.extendedProps || {};
            const workType = props.workType || 'event';
            const status = props.status || 'not_started';
            const priority = props.priority || 'medium';

            let html = `
                <div class="space-y-6">
                    <!-- Event Title -->
                    <div class="detail-section">
                        <h3 class="text-2xl font-bold text-gray-900 mb-2">${this.escapeHtml(event.title)}</h3>
                        <div class="flex items-center gap-2 flex-wrap">
                            ${this.getWorkTypeIcon(workType)}
                            <span class="text-sm font-medium text-gray-600">${this.formatWorkType(workType)}</span>
                        </div>
                    </div>

                    <!-- Date & Time -->
                    <div class="detail-section">
                        <div class="detail-label">Schedule</div>
                        <div class="detail-value">
                            <i class="fas fa-calendar-alt text-blue-600 mr-2"></i>
                            ${this.formatEventDate(event)}
                        </div>
                        ${props.start_time ? `
                            <div class="detail-value mt-2">
                                <i class="fas fa-clock text-emerald-600 mr-2"></i>
                                ${props.start_time}
                            </div>
                        ` : ''}
                    </div>

                    <!-- Status & Priority -->
                    <div class="detail-section">
                        <div class="detail-label mb-3">Status & Priority</div>
                        <div class="flex gap-3">
                            <span class="status-badge-detail ${status}">
                                ${this.getStatusIcon(status)}
                                ${this.formatStatus(status)}
                            </span>
                            <span class="priority-badge-detail ${priority}">
                                ${this.getPriorityIcon(priority)}
                                ${this.formatPriority(priority)}
                            </span>
                        </div>
                    </div>

                    <!-- Description -->
                    ${props.description ? `
                        <div class="detail-section">
                            <div class="detail-label">Description</div>
                            <div class="detail-value text-gray-700 leading-relaxed">
                                ${this.escapeHtml(props.description)}
                            </div>
                        </div>
                    ` : ''}

                    <!-- Project Context -->
                    ${props.project && props.project.name ? `
                        <div class="detail-section">
                            <div class="detail-label">Project</div>
                            <div class="detail-value">
                                <i class="fas fa-project-diagram text-blue-600 mr-2"></i>
                                ${this.escapeHtml(props.project.name)}
                            </div>
                        </div>
                    ` : ''}

                    <!-- Actions -->
                    <div class="space-y-3 pt-4">
                        ${event.url ? `
                            <button onclick="window.modernCalendar.openFullModal('${event.url}')"
                                    class="detail-action-btn primary">
                                <i class="fas fa-eye"></i>
                                View Full Details
                            </button>
                        ` : ''}
                        <button onclick="window.modernCalendar.closeDetailPanel()"
                                class="detail-action-btn secondary">
                            <i class="fas fa-times"></i>
                            Close
                        </button>
                    </div>
                </div>
            `;

            return html;
        }

        /**
         * Initialize modal for full event details
         */
        initModal() {
            const modal = this.options.modalEl;

            if (!modal) return;

            // Close on backdrop click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });

            // Close on Escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    this.closeModal();
                }
            });
        }

        /**
         * Open full modal with event details
         */
        openFullModal(url) {
            const modal = this.options.modalEl;
            const content = this.options.modalContentEl;

            if (!modal || !content) return;

            modal.classList.remove('hidden');
            content.innerHTML = '<div class="text-center py-10"><i class="fas fa-spinner fa-spin text-3xl text-gray-400"></i><p class="mt-4 text-gray-600">Loading...</p></div>';

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Failed to load');
                return response.text();
            })
            .then(html => {
                content.innerHTML = html;

                // Initialize HTMX on modal content
                if (window.htmx) {
                    htmx.process(content);
                }

                // Attach close handlers
                const closeBtn = content.querySelector('[data-close-modal]');
                if (closeBtn) {
                    closeBtn.addEventListener('click', () => this.closeModal());
                }
            })
            .catch(error => {
                console.error('❌ Modal load error:', error);
                content.innerHTML = '<div class="text-center py-10 text-red-600"><i class="fas fa-exclamation-circle text-3xl"></i><p class="mt-4">Failed to load. Please try again.</p></div>';
            });

            // Close detail panel when modal opens
            this.closeDetailPanel();
        }

        /**
         * Close modal
         */
        closeModal() {
            const modal = this.options.modalEl;
            if (modal) {
                modal.classList.add('hidden');
                if (this.options.modalContentEl) {
                    this.options.modalContentEl.innerHTML = '';
                }
            }
        }

        /**
         * Initialize Today button
         */
        initTodayButton() {
            const todayBtn = document.getElementById('todayBtn');
            if (todayBtn) {
                todayBtn.addEventListener('click', () => {
                    if (this.calendar) {
                        this.calendar.today();
                        if (this.miniCalendar) {
                            this.miniCalendar.today();
                        }
                    }
                });
            }
        }

        /**
         * Fetch events from server
         */
        fetchEvents(info, successCallback, failureCallback) {
            const url = `${this.options.eventsFeedUrl}?start=${info.startStr}&end=${info.endStr}`;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP error ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('📊 Fetched events:', data.length);
                    successCallback(data);
                    this.applyFilters(); // Apply filters after events load
                })
                .catch(error => {
                    console.error('❌ Fetch error:', error);
                    failureCallback(error);
                });
        }

        /**
         * Handle event click
         */
        handleEventClick(info) {
            console.log('🖱️  Event clicked:', info.event.title);

            if (this.options.onEventClick) {
                this.options.onEventClick(info);
            }

            // Open detail panel
            this.openDetailPanel(info.event);
        }

        /**
         * Handle date click
         */
        handleDateClick(info) {
            console.log('📅 Date clicked:', info.dateStr);
            // Could open create form with pre-filled date
        }

        /**
         * Build event content HTML
         */
        buildEventContent(arg) {
            const viewType = arg.view.type || '';

            // List view - use default rendering
            if (viewType.indexOf('list') !== -1) {
                return true;
            }

            // Month/Week/Day views - custom compact layout
            const workItem = arg.event.extendedProps || {};
            const workType = workItem.workType || '';
            const status = workItem.status || 'not_started';
            const priority = workItem.priority || 'medium';
            const level = workItem.level || 0;

            let html = '<div class="flex items-center gap-1 text-sm" style="color: inherit;">';

            // Hierarchy indicator
            if (level > 0) {
                html += '<span class="text-gray-400 text-xs leading-none" aria-hidden="true">└</span>';
            }

            // Work type icon
            html += `<span class="leading-none" aria-hidden="true">${this.getWorkTypeIcon(workType, true)}</span>`;

            // Title
            html += `<span class="flex-1 truncate font-medium leading-tight" style="color: inherit;">${this.escapeHtml(arg.event.title)}</span>`;

            // Status icon
            html += `<span class="leading-none flex-shrink-0">${this.getStatusIcon(status, true)}</span>`;

            // Priority (critical only)
            if (priority === 'critical') {
                html += '<span class="leading-none flex-shrink-0"><i class="fas fa-exclamation-circle text-xs" style="color: #EF4444;"></i></span>';
            }

            // Time
            if (workItem.start_time || (arg.event.start && !arg.event.allDay)) {
                const timeText = workItem.start_time || arg.event.start.toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit'
                });
                html += `<span class="text-xs flex-shrink-0" style="color: #374151;">${timeText}</span>`;
            }

            html += '</div>';
            return { html: html };
        }

        /**
         * Setup event attributes and tooltips
         */
        setupEventAttributes(info) {
            const workItem = info.event.extendedProps || {};
            const workType = workItem.workType || '';
            const status = workItem.status || 'not_started';
            const priority = workItem.priority || 'medium';

            // Data attributes
            info.el.setAttribute('data-work-type', workType);
            info.el.setAttribute('data-status', status);
            info.el.setAttribute('data-priority', priority);
            info.el.setAttribute('data-event-id', info.event.id);

            // Tooltip
            const tooltipParts = [
                `${this.formatWorkType(workType)}: ${info.event.title}`,
                `Status: ${this.formatStatus(status)}`,
                `Priority: ${this.formatPriority(priority)}`
            ];

            if (workItem.project && workItem.project.name) {
                tooltipParts.push(`Project: ${workItem.project.name}`);
            }

            info.el.setAttribute('title', tooltipParts.join('\n'));
            info.el.setAttribute('aria-label', tooltipParts.join(', '));
            info.el.setAttribute('tabindex', '0');
            info.el.setAttribute('role', 'button');
        }

        /**
         * Update mini calendar date
         */
        updateMiniCalendarDate(date) {
            if (this.miniCalendar) {
                this.miniCalendar.gotoDate(date);
            }
        }

        /**
         * Highlight date in mini calendar
         */
        highlightMiniCalendarDate(date) {
            // Future enhancement: add visual highlight
        }

        /**
         * Load view preference from localStorage
         */
        loadViewPreference() {
            if (typeof localStorage === 'undefined') return this.options.defaultView;

            const stored = localStorage.getItem(this.options.storageKey);
            return stored || this.options.defaultView;
        }

        /**
         * Save view preference to localStorage
         */
        saveViewPreference(view) {
            if (typeof localStorage !== 'undefined') {
                localStorage.setItem(this.options.storageKey, view);
            }
        }

        /**
         * Helper: Get work type icon
         */
        getWorkTypeIcon(workType, inline = false) {
            const icons = {
                'project': `<i class="fas fa-project-diagram ${inline ? '' : 'mr-1'}" style="color: #3B82F6;"></i>`,
                'sub_project': `<i class="fas fa-folder-tree ${inline ? '' : 'mr-1'}" style="color: #0EA5E9;"></i>`,
                'activity': `<i class="fas fa-clipboard-list ${inline ? '' : 'mr-1'}" style="color: #10B981;"></i>`,
                'sub_activity': `<i class="fas fa-list-check ${inline ? '' : 'mr-1'}" style="color: #22C55E;"></i>`,
                'task': `<i class="fas fa-tasks ${inline ? '' : 'mr-1'}" style="color: #8B5CF6;"></i>`,
                'subtask': `<i class="fas fa-check-square ${inline ? '' : 'mr-1'}" style="color: #A855F7;"></i>`
            };
            return icons[workType] || `<i class="fas fa-circle ${inline ? '' : 'mr-1'}" style="color: #9CA3AF;"></i>`;
        }

        /**
         * Helper: Get status icon
         */
        getStatusIcon(status, inline = false) {
            const icons = {
                'not_started': `<i class="far fa-circle text-xs ${inline ? '' : 'ml-1'}" style="color: #9CA3AF;"></i>`,
                'in_progress': `<i class="fas fa-spinner text-xs ${inline ? '' : 'ml-1'}" style="color: #3B82F6;"></i>`,
                'at_risk': `<i class="fas fa-exclamation-triangle text-xs ${inline ? '' : 'ml-1'}" style="color: #F59E0B;"></i>`,
                'blocked': `<i class="fas fa-ban text-xs ${inline ? '' : 'ml-1'}" style="color: #EF4444;"></i>`,
                'completed': `<i class="fas fa-check-circle text-xs ${inline ? '' : 'ml-1'}" style="color: #10B981;"></i>`,
                'cancelled': `<i class="fas fa-times-circle text-xs ${inline ? '' : 'ml-1'}" style="color: #6B7280;"></i>`
            };
            return icons[status] || '';
        }

        /**
         * Helper: Get priority icon
         */
        getPriorityIcon(priority) {
            const icons = {
                'critical': '<i class="fas fa-exclamation-circle"></i>',
                'high': '<i class="fas fa-arrow-up"></i>',
                'medium': '<i class="fas fa-minus"></i>',
                'low': '<i class="fas fa-arrow-down"></i>'
            };
            return icons[priority] || icons.medium;
        }

        /**
         * Helper: Format work type
         */
        formatWorkType(workType) {
            const labels = {
                'project': 'Project',
                'sub_project': 'Sub-Project',
                'activity': 'Activity',
                'sub_activity': 'Sub-Activity',
                'task': 'Task',
                'subtask': 'Subtask'
            };
            return labels[workType] || 'Event';
        }

        /**
         * Helper: Format status
         */
        formatStatus(status) {
            return status.split('_').map(word =>
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }

        /**
         * Helper: Format priority
         */
        formatPriority(priority) {
            return priority.charAt(0).toUpperCase() + priority.slice(1);
        }

        /**
         * Helper: Format event date
         */
        formatEventDate(event) {
            const start = event.start;
            const end = event.end;

            if (!start) return 'No date';

            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            const startStr = start.toLocaleDateString('en-US', options);

            if (end && !event.allDay) {
                const endStr = end.toLocaleDateString('en-US', options);
                return startStr === endStr ? startStr : `${startStr} - ${endStr}`;
            }

            return startStr;
        }

        /**
         * Helper: Escape HTML
         */
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        /**
         * Public API: Refresh calendar events
         */
        refresh() {
            if (this.calendar) {
                this.calendar.refetchEvents();
            }
        }

        /**
         * Public API: Get current view
         */
        getCurrentView() {
            return this.currentView;
        }

        /**
         * Public API: Go to specific date
         */
        gotoDate(date) {
            if (this.calendar) {
                this.calendar.gotoDate(date);
            }
        }
    }

    // Expose to global scope
    window.ModernCalendar = ModernCalendar;

})(window);
