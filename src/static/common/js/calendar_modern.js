/**
 * Modern Calendar Component JavaScript (Refactored)
 * Clean, minimal configuration - let FullCalendar handle its own layout
 */

(function () {
    'use strict';

    let modernCalendar = null;
    let allEvents = [];
    let currentMiniCalDate = new Date();
    let selectedDate = null;

    /**
     * Initialize Modern Calendar
     */
    function initModernCalendar() {
        if (typeof FullCalendar === 'undefined') {
            console.warn('FullCalendar library not loaded');
            return;
        }

        const calendarEl = document.getElementById('modernCalendar');
        if (!calendarEl) {
            console.warn('Modern calendar container not found');
            return;
        }

        // Clean, minimal FullCalendar configuration
        modernCalendar = new FullCalendar.Calendar(calendarEl, {
            // Core settings
            initialView: 'timeGridWeek',
            headerToolbar: false, // Custom header controls
            height: '100%', // Fill container (container has fixed 700px height)

            // Behavior
            nowIndicator: true,
            navLinks: true,
            editable: true,
            selectable: true,
            selectMirror: true,

            // Time settings
            slotMinTime: '06:00:00',
            slotMaxTime: '20:00:00',
            slotDuration: '00:30:00',
            slotLabelInterval: '01:00',

            // Business hours
            businessHours: {
                daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
                startTime: '08:00',
                endTime: '17:00',
            },

            // View configurations
            views: {
                timeGridDay: {
                    titleFormat: { year: 'numeric', month: 'long', day: 'numeric' }
                },
                timeGridWeek: {
                    titleFormat: { year: 'numeric', month: 'long' }
                },
                dayGridMonth: {
                    titleFormat: { year: 'numeric', month: 'long' }
                },
                multiMonthYear: {
                    titleFormat: { year: 'numeric' }
                }
            },

            // Event source
            events: fetchCalendarEvents,

            // Event handlers
            eventClick: handleEventClick,
            eventDrop: handleEventDrop,
            eventResize: handleEventResize,
            datesSet: handleDatesSet,
            dateClick: handleDateClick
        });

        modernCalendar.render();

        // Initialize UI controls
        initViewSwitcher();
        initNavigationControls();
        initMiniCalendar();
        initSearchBar();
        initSidebarToggle();
    }

    /**
     * Fetch calendar events from API
     */
    function fetchCalendarEvents(fetchInfo, successCallback, failureCallback) {
        const params = new URLSearchParams({
            start: fetchInfo.startStr,
            end: fetchInfo.endStr
        });

        fetch('/oobc-management/calendar/work-items/feed/?' + params)
            .then(response => response.json())
            .then(data => {
                const workItems = Array.isArray(data) ? data : (data.workItems || []);
                const events = transformWorkItemsToEvents(workItems);
                allEvents = events;
                successCallback(events);
                updateUpcomingEventsList(events);
                updateMiniCalendar();
            })
            .catch(error => {
                console.error('Error fetching events:', error);
                failureCallback(error);
            });
    }

    /**
     * Transform WorkItems to FullCalendar events
     */
    function transformWorkItemsToEvents(workItems) {
        return workItems.map(item => {
            // Color scheme based on type and status
            let color = getEventColor(item);

            return {
                id: item.id,
                title: item.title,
                start: item.start,
                end: item.end,
                color: color,
                extendedProps: {
                    type: item.type,
                    status: item.status,
                    priority: item.priority,
                    level: item.level,
                    parentId: item.parentId,
                    breadcrumb: item.breadcrumb,
                    modalUrl: item.url,
                    objectId: item.id.replace('work-item-', ''),
                    supportsEditing: true,
                    isRecurring: item.isRecurring || false,
                    project: item.extendedProps?.project || null
                }
            };
        });
    }

    /**
     * Get event color based on type, status, and priority
     */
    function getEventColor(item) {
        // Status-based color (highest priority)
        if (item.status === 'completed') return '#059669'; // Emerald
        if (item.status === 'blocked') return '#dc2626'; // Red

        // Priority-based color
        if (item.priority === 'critical') return '#f97316'; // Orange

        // Type-based color (default)
        const typeColors = {
            'Project': '#8b5cf6', // Purple
            'Activity': '#10b981', // Green
            'Task': '#f59e0b', // Amber
        };

        return typeColors[item.type] || '#3b82f6'; // Default blue
    }

    /**
     * Event click handler
     */
    function handleEventClick(info) {
        info.jsEvent.preventDefault();
        const modalUrl = info.event.extendedProps?.modalUrl;

        if (modalUrl && typeof window.openCalendarModal === 'function') {
            window.openCalendarModal(modalUrl);
        }
    }

    /**
     * Event drop handler (drag and drop)
     */
    function handleEventDrop(info) {
        if (typeof window.updateCalendarEvent === 'function') {
            window.updateCalendarEvent(info, info.revert);
        }
    }

    /**
     * Event resize handler
     */
    function handleEventResize(info) {
        if (typeof window.updateCalendarEvent === 'function') {
            window.updateCalendarEvent(info, info.revert);
        }
    }

    /**
     * Dates set handler (view change, navigation)
     */
    function handleDatesSet(dateInfo) {
        document.getElementById('calendarTitle').textContent = dateInfo.view.title;
        updateMiniCalendar();
    }

    /**
     * Date click handler
     */
    function handleDateClick(info) {
        selectedDate = info.date;
        modernCalendar.gotoDate(info.date);
        updateMiniCalendar();
    }

    /**
     * Initialize View Switcher Buttons
     */
    function initViewSwitcher() {
        const viewButtons = document.querySelectorAll('.calendar-view-btn');

        viewButtons.forEach(button => {
            button.addEventListener('click', function() {
                const view = this.getAttribute('data-view');

                // Update button states
                viewButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                // Change calendar view
                if (modernCalendar) {
                    modernCalendar.changeView(view);
                }
            });
        });
    }

    /**
     * Initialize Navigation Controls
     */
    function initNavigationControls() {
        const prevBtn = document.getElementById('calendarPrev');
        const nextBtn = document.getElementById('calendarNext');
        const todayBtn = document.getElementById('calendarToday');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => modernCalendar.prev());
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => modernCalendar.next());
        }

        if (todayBtn) {
            todayBtn.addEventListener('click', () => {
                modernCalendar.today();
                selectedDate = new Date();
                updateMiniCalendar();
            });
        }
    }

    /**
     * Initialize Mini Calendar
     */
    function initMiniCalendar() {
        renderMiniCalendar();

        const prevBtn = document.getElementById('miniCalPrev');
        const nextBtn = document.getElementById('miniCalNext');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                currentMiniCalDate.setMonth(currentMiniCalDate.getMonth() - 1);
                renderMiniCalendar();
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                currentMiniCalDate.setMonth(currentMiniCalDate.getMonth() + 1);
                renderMiniCalendar();
            });
        }
    }

    /**
     * Render Mini Calendar
     */
    function renderMiniCalendar() {
        const year = currentMiniCalDate.getFullYear();
        const month = currentMiniCalDate.getMonth();

        // Update month header
        const monthEl = document.getElementById('miniCalendarMonth');
        if (monthEl) {
            monthEl.textContent = new Date(year, month, 1).toLocaleDateString('en-US', {
                month: 'long',
                year: 'numeric'
            });
        }

        // Calculate calendar dates
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const prevLastDay = new Date(year, month, 0);
        const firstDayOfWeek = firstDay.getDay();
        const lastDate = lastDay.getDate();
        const prevLastDate = prevLastDay.getDate();

        const datesContainer = document.getElementById('miniCalendarDates');
        if (!datesContainer) return;

        datesContainer.innerHTML = '';

        // Previous month dates
        for (let i = firstDayOfWeek - 1; i >= 0; i--) {
            const date = prevLastDate - i;
            const dateObj = new Date(year, month - 1, date);
            datesContainer.appendChild(createMiniCalDate(dateObj, true));
        }

        // Current month dates
        for (let date = 1; date <= lastDate; date++) {
            const dateObj = new Date(year, month, date);
            datesContainer.appendChild(createMiniCalDate(dateObj, false));
        }

        // Next month dates
        const remainingCells = 42 - (firstDayOfWeek + lastDate);
        for (let date = 1; date <= remainingCells; date++) {
            const dateObj = new Date(year, month + 1, date);
            datesContainer.appendChild(createMiniCalDate(dateObj, true));
        }
    }

    /**
     * Create Mini Calendar Date Element
     */
    function createMiniCalDate(date, isOtherMonth) {
        const div = document.createElement('div');
        div.className = 'mini-cal-date';

        if (isOtherMonth) {
            div.classList.add('other-month');
        }

        // Check if today
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const compareDate = new Date(date);
        compareDate.setHours(0, 0, 0, 0);

        if (compareDate.getTime() === today.getTime()) {
            div.classList.add('today');
        }

        // Check if selected
        if (selectedDate) {
            const selectedCompare = new Date(selectedDate);
            selectedCompare.setHours(0, 0, 0, 0);
            if (compareDate.getTime() === selectedCompare.getTime()) {
                div.classList.add('selected');
            }
        }

        // Check if has events
        if (hasEventsOnDate(date)) {
            div.classList.add('has-events');
        }

        div.textContent = date.getDate();

        div.addEventListener('click', () => {
            selectedDate = new Date(date);
            modernCalendar.gotoDate(date);
            renderMiniCalendar();
        });

        return div;
    }

    /**
     * Check if date has events
     */
    function hasEventsOnDate(date) {
        const checkDate = new Date(date);
        checkDate.setHours(0, 0, 0, 0);

        return allEvents.some(event => {
            const eventStart = new Date(event.start);
            eventStart.setHours(0, 0, 0, 0);
            return eventStart.getTime() === checkDate.getTime();
        });
    }

    /**
     * Update Mini Calendar
     */
    function updateMiniCalendar() {
        renderMiniCalendar();
    }

    /**
     * Update Upcoming Events List
     */
    function updateUpcomingEventsList(events) {
        const listEl = document.getElementById('upcomingEventsList');
        if (!listEl) return;

        // Filter upcoming events (today and future)
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const upcomingEvents = events
            .filter(event => {
                const eventDate = new Date(event.start);
                eventDate.setHours(0, 0, 0, 0);
                return eventDate >= today;
            })
            .sort((a, b) => new Date(a.start) - new Date(b.start))
            .slice(0, 10); // Show max 10 events

        if (upcomingEvents.length === 0) {
            listEl.innerHTML = `
                <div class="text-sm text-gray-500 text-center py-4">
                    <i class="fas fa-calendar-day text-gray-400 text-2xl mb-2"></i>
                    <p>No upcoming events</p>
                </div>
            `;
            return;
        }

        listEl.innerHTML = '';

        // Group by date
        const groupedEvents = {};
        upcomingEvents.forEach(event => {
            const dateKey = new Date(event.start).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });

            if (!groupedEvents[dateKey]) {
                groupedEvents[dateKey] = [];
            }
            groupedEvents[dateKey].push(event);
        });

        // Render grouped events
        Object.keys(groupedEvents).forEach(dateKey => {
            const dateHeader = document.createElement('div');
            dateHeader.className = 'text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2';
            dateHeader.textContent = dateKey;
            listEl.appendChild(dateHeader);

            groupedEvents[dateKey].forEach(event => {
                const eventEl = createEventListItem(event);
                listEl.appendChild(eventEl);
            });
        });
    }

    /**
     * Create Event List Item
     */
    function createEventListItem(event) {
        const div = document.createElement('div');
        div.className = 'flex items-start space-x-3 p-3 rounded-lg border border-gray-200 hover:shadow-md transition-all cursor-pointer mb-2';

        const time = new Date(event.start).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit'
        });

        const typeIcon = getTypeIcon(event.extendedProps?.type);
        const statusIcon = getStatusIcon(event.extendedProps?.status);

        div.innerHTML = `
            <div class="w-2 h-2 rounded-full flex-shrink-0 mt-1.5" style="background-color: ${event.color}"></div>
            <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2 mb-1">
                    <i class="${typeIcon} text-xs text-gray-600"></i>
                    <p class="text-sm font-medium text-gray-900 truncate">${event.title}</p>
                </div>
                <div class="flex items-center space-x-2 text-xs text-gray-500">
                    <i class="far fa-clock"></i>
                    <span>${time}</span>
                    <i class="${statusIcon} ml-2"></i>
                    <span class="capitalize">${event.extendedProps?.status || 'active'}</span>
                </div>
            </div>
        `;

        div.addEventListener('click', () => {
            if (event.extendedProps?.modalUrl && typeof window.openCalendarModal === 'function') {
                window.openCalendarModal(event.extendedProps.modalUrl);
            }
        });

        return div;
    }

    /**
     * Get Type Icon
     */
    function getTypeIcon(type) {
        const icons = {
            'Project': 'fas fa-folder',
            'Activity': 'fas fa-calendar-check',
            'Task': 'fas fa-tasks'
        };
        return icons[type] || 'fas fa-circle';
    }

    /**
     * Get Status Icon
     */
    function getStatusIcon(status) {
        const icons = {
            'completed': 'fas fa-check-circle text-emerald-600',
            'in_progress': 'fas fa-spinner text-blue-600',
            'blocked': 'fas fa-exclamation-circle text-red-600',
            'planned': 'fas fa-clock text-gray-600'
        };
        return icons[status] || 'fas fa-circle';
    }

    /**
     * Initialize Search Bar
     */
    function initSearchBar() {
        const searchInput = document.getElementById('calendarSearch');
        if (!searchInput) return;

        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value.toLowerCase().trim();

                if (!modernCalendar) return;

                // Filter events
                const filteredEvents = allEvents.filter(event => {
                    if (!query) return true;
                    return event.title.toLowerCase().includes(query) ||
                           (event.extendedProps?.breadcrumb || '').toLowerCase().includes(query);
                });

                // Update calendar events
                modernCalendar.removeAllEvents();
                filteredEvents.forEach(event => modernCalendar.addEvent(event));
            }, 300);
        });
    }

    /**
     * Initialize Sidebar Toggle (Mobile)
     */
    function initSidebarToggle() {
        const sidebar = document.getElementById('calendarSidebar');
        const openBtn = document.getElementById('mobileSidebarOpen');
        const closeBtn = document.getElementById('mobileSidebarToggle');

        if (openBtn) {
            openBtn.addEventListener('click', () => {
                sidebar.classList.add('open');
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                sidebar.classList.remove('open');
            });
        }

        // Close sidebar when clicking outside (mobile)
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 1024) {
                if (!sidebar.contains(e.target) && !openBtn.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }

    // Initialize on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModernCalendar);
    } else {
        initModernCalendar();
    }

    // Export for external use
    window.modernCalendarInstance = {
        getCalendar: () => modernCalendar,
        refresh: () => {
            if (modernCalendar) {
                modernCalendar.refetchEvents();
            }
        }
    };
})();
