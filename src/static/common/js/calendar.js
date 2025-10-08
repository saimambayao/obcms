(function () {
    /**
     * Get CSRF token for Django AJAX requests
     */
    function getCsrfToken() {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Show toast notification
     */
    function showToast(message, type) {
        type = type || 'info';
        var toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 px-6 py-4 rounded-lg shadow-lg z-50 transition-opacity duration-300';

        var colors = {
            'success': 'bg-green-500 text-white',
            'error': 'bg-red-500 text-white',
            'info': 'bg-blue-500 text-white',
            'warning': 'bg-yellow-500 text-white'
        };

        toast.className += ' ' + (colors[type] || colors.info);
        toast.innerHTML = '<i class="fas fa-' + (type === 'success' ? 'check' : type === 'error' ? 'exclamation' : 'info') + '-circle mr-2"></i>' + message;

        document.body.appendChild(toast);

        setTimeout(function() {
            toast.style.opacity = '0';
            setTimeout(function() {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    /**
     * Update event via AJAX (drag-and-drop or resize)
     */
    function updateCalendarEvent(eventInfo, revertFunc) {
        var extendedProps = eventInfo.event.extendedProps || {};

        if (extendedProps.supportsEditing !== true) {
            showToast('Drag-and-drop is disabled for this item.', 'info');
            if (typeof revertFunc === 'function') {
                revertFunc();
            }
            return;
        }

        var objectId = extendedProps.objectId || eventInfo.event.id;
        if (!objectId) {
            showToast('Unable to determine the record to update.', 'error');
            if (typeof revertFunc === 'function') {
                revertFunc();
            }
            return;
        }

        var serializedStart = eventInfo.event.start
            ? eventInfo.event.start.toISOString()
            : null;
        var serializedEnd = eventInfo.event.end
            ? eventInfo.event.end.toISOString()
            : null;

        var deltas = {};
        if (eventInfo.delta && typeof eventInfo.delta.milliseconds === 'number') {
            deltas.deltaMs = eventInfo.delta.milliseconds;
            if (typeof eventInfo.delta.days === 'number') {
                deltas.deltaDays = eventInfo.delta.days;
            }
        }
        if (eventInfo.startDelta && typeof eventInfo.startDelta.milliseconds === 'number') {
            deltas.startDeltaMs = eventInfo.startDelta.milliseconds;
        }
        if (eventInfo.endDelta && typeof eventInfo.endDelta.milliseconds === 'number') {
            deltas.endDeltaMs = eventInfo.endDelta.milliseconds;
        }

        var eventData = {
            id: objectId,
            originalId: eventInfo.event.id,
            type:
                extendedProps.type ||
                extendedProps.category ||
                'event',
            module: extendedProps.module || null,
            start: serializedStart,
            end: serializedEnd,
            allDay: eventInfo.event.allDay,
            metadata: {
                hasStartDate: Boolean(extendedProps.hasStartDate),
                hasDueDate: Boolean(extendedProps.hasDueDate),
            },
            deltas: deltas,
        };

        // Show loading indicator on event
        eventInfo.el.style.opacity = '0.6';

        fetch('/api/calendar/event/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(eventData)
        })
        .then(function(response) {
            if (!response.ok) {
                return response.json().then(function(data) {
                    throw new Error(data.error || 'Failed to update event');
                });
            }
            return response.json();
        })
        .then(function(data) {
            eventInfo.el.style.opacity = '1';
            showToast(data.message || 'Event updated successfully', 'success');
        })
        .catch(function(error) {
            eventInfo.el.style.opacity = '1';
            console.error('Error updating event:', error);
            showToast(error.message || 'Failed to update event', 'error');

            // Revert the event to its original position/time
            if (typeof revertFunc === 'function') {
                revertFunc();
            }
        });
    }

    /**
     * Render calendar with drag-and-drop support
     */
    function renderCalendar(widgetId, events, options) {
        if (typeof FullCalendar === "undefined") {
            console.warn("FullCalendar library is not loaded; calendar widget skipped.");
            return null;
        }

        var container = document.getElementById(widgetId);
        if (!container) {
            console.warn("Calendar container not found for id", widgetId);
            return null;
        }

        var config = Object.assign(
            {
                initialView: "dayGridMonth",
                headerToolbar: {
                    left: "prev,next today",
                    center: "title",
                    right: "dayGridMonth,timeGridWeek,listWeek",
                },
                height: "auto",
                events: events || [],
                displayEventTime: true,
                eventDisplay: "block",

                // Drag-and-drop features
                editable: true,
                droppable: false,
                eventStartEditable: true,
                eventDurationEditable: true,
                eventResizableFromStart: true,

                // Event handlers for drag-and-drop
                eventDrop: function(info) {
                    updateCalendarEvent(info, info.revert);
                },

                eventResize: function(info) {
                    updateCalendarEvent(info, info.revert);
                },

                // Event styling with recurring indicators
                eventDidMount: function(info) {
                    var event = info.event;
                    var props = event.extendedProps;

                    // Add recurring indicator icon
                    if (props.isRecurring || props.is_recurring) {
                        var icon = document.createElement('i');
                        icon.className = 'fas fa-repeat ml-1 text-xs opacity-75';
                        icon.title = 'Recurring event';

                        var titleEl = info.el.querySelector('.fc-event-title');
                        if (titleEl) {
                            titleEl.appendChild(icon);
                        }
                    }

                    // Add project/activity badge if task has project context
                    if (props.project && props.project.id) {
                        var badge = document.createElement('div');
                        badge.className = 'calendar-project-badge';
                        badge.innerHTML = '<i class="fas fa-project-diagram"></i><span>' + props.project.name + '</span>';

                        var titleContainer = info.el.querySelector('.fc-event-title-container');
                        if (titleContainer) {
                            titleContainer.appendChild(badge);
                        }
                    }

                    // Add context icon for tasks based on task_context
                    if (props.type === 'staff_task' && props.task_context) {
                        var icon = document.createElement('i');
                        icon.className = 'mr-1 text-xs';

                        if (props.task_context === 'project_activity') {
                            icon.className += ' fas fa-project-diagram';
                            icon.title = 'Project Activity Task';
                        } else if (props.task_context === 'project') {
                            icon.className += ' fas fa-folder';
                            icon.title = 'Project Task';
                        } else if (props.task_context === 'activity') {
                            icon.className += ' fas fa-calendar-check';
                            icon.title = 'Activity Task';
                        } else {
                            icon.className += ' fas fa-tasks';
                            icon.title = 'Standalone Task';
                        }

                        var titleEl = info.el.querySelector('.fc-event-title');
                        if (titleEl) {
                            titleEl.insertBefore(icon, titleEl.firstChild);
                        }
                    }

                    // Add cursor pointer for all events
                    info.el.style.cursor = 'move';

                    // Enhanced tooltip with project/event details
                    var tooltipContent = event.title;

                    if (props.project) {
                        tooltipContent += '\nProject: ' + props.project.name;
                    }

                    if (props.event) {
                        tooltipContent += '\nEvent: ' + props.event.name;
                    }

                    if (props.description) {
                        tooltipContent += '\n' + props.description;
                    }

                    info.el.title = tooltipContent;
                },
            },
            options || {}
        );

        function defaultEventClickHandler(info) {
            if (info.jsEvent) {
                info.jsEvent.preventDefault();
            }

            var props = info.event.extendedProps || {};
            var modalUrl = props.modalUrl || null;
            var type = props.type || props.category || "event";
            var objectId = props.objectId || info.event.id;

            if (!modalUrl && objectId) {
                if (type === "staff_task" || type === "task") {
                    modalUrl = "/oobc-management/staff/tasks/" + objectId + "/modal/";
                } else if (type === "event") {
                    modalUrl = "/coordination/events/" + objectId + "/modal/";
                }
            }

            if (modalUrl && typeof window.openCalendarModal === "function") {
                window.openCalendarModal(modalUrl);
                return false;
            }

            if (modalUrl) {
                window.location.href = modalUrl;
                return false;
            }

            return false;
        }

        if (typeof config.eventClick === "function") {
            var userEventClick = config.eventClick;
            config.eventClick = function(info) {
                var result = userEventClick(info);
                if (result !== false) {
                    return defaultEventClickHandler(info);
                }
                return result;
            };
        } else {
            config.eventClick = defaultEventClickHandler;
        }

        var userDayCellDidMount = config.dayCellDidMount;

        config.dayCellDidMount = function (info) {
            var day = info.date.getDay();
            var numberEl = info.el.querySelector(".fc-daygrid-day-number");

            if (numberEl) {
                // Jumu'ah (Friday) in red
                if (day === 5) {
                    numberEl.style.color = "#dc2626";
                }
                // Weekend (Saturday/Sunday) in blue
                else if (day === 6 || day === 0) {
                    numberEl.style.color = "#2563eb";
                }
                else {
                    numberEl.style.removeProperty("color");
                }
            }

            if (typeof userDayCellDidMount === "function") {
                userDayCellDidMount(info);
            }
        };

        var calendar = new FullCalendar.Calendar(container, config);
        calendar.render();

        if (!window.__oobcCalendars) {
            window.__oobcCalendars = {};
        }
        window.__oobcCalendars[widgetId] = calendar;

        return calendar;
    }

    window.renderCalendar = renderCalendar;
})();
