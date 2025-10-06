# OBCMS Calendar Widget Component

## Overview

A fully reusable, self-contained calendar widget component extracted from the advanced-modern calendar implementation. This component can be embedded anywhere in OBCMS to provide full calendar functionality with FullCalendar integration, HTMX dynamic loading, and complete customization options.

## File Location

```
/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/templates/components/calendar_widget.html
```

## Features

- **FullCalendar Integration**: Full-featured calendar with month, week, day, and year views
- **HTMX Integration**: Dynamic event loading and form interactions
- **Drag & Drop**: Optional drag-and-drop event rescheduling
- **Event Creation**: Double-click on dates to create new events
- **Mini Calendar**: Optional sidebar mini calendar for date navigation
- **Event Filtering**: Filter events by type and completion status
- **Responsive Design**: Mobile-friendly with collapsible sidebars
- **Multiple Instances**: Fully scoped CSS and JavaScript for multiple calendars on same page
- **Detail Panel**: Slide-out panel for event editing/viewing
- **Toast Notifications**: Built-in toast system for user feedback

## Basic Usage

### Minimal Implementation

```django
{% load static %}

{% include 'components/calendar_widget.html' with
    events_endpoint='/oobc-management/work-items/calendar/feed/'
%}
```

### Full Configuration

```django
{% load static %}

{% include 'components/calendar_widget.html' with
    calendar_id='projectCalendar'
    events_endpoint='/api/calendar/events/'
    event_types=custom_event_types
    show_sidebar=True
    calendar_height='calc(100vh - 200px)'
    enable_event_creation=True
    enable_drag_drop=True
    default_view='dayGridMonth'
    show_mini_calendar=True
    show_completed_filter=True
    update_endpoint='/api/calendar/update/'
%}
```

## Context Variables

### Required

| Variable | Type | Description |
|----------|------|-------------|
| `events_endpoint` | String | URL endpoint that returns calendar events in FullCalendar format |

### Optional

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `calendar_id` | String | `'calendarWidget'` | Unique ID for this calendar instance |
| `event_types` | List | Standard work types | Event type configurations (see format below) |
| `show_sidebar` | Boolean | `True` | Show/hide left sidebar |
| `calendar_height` | String | `'calc(100vh - 200px)'` | CSS height value for calendar container |
| `enable_event_creation` | Boolean | `True` | Enable double-click event creation |
| `enable_drag_drop` | Boolean | `True` | Enable drag-and-drop rescheduling |
| `default_view` | String | `'dayGridMonth'` | Initial calendar view mode |
| `show_mini_calendar` | Boolean | `True` | Show mini calendar in sidebar |
| `show_completed_filter` | Boolean | `True` | Show completed items filter |
| `update_endpoint` | String | `/oobc-management/calendar/event/update/` | URL for event updates |

### Event Types Format

```python
event_types = [
    {
        'value': 'project',
        'label': 'Projects',
        'icon': 'fa-folder',
        'color': '#3b82f6'
    },
    {
        'value': 'activity',
        'label': 'Activities',
        'icon': 'fa-calendar-check',
        'color': '#10b981'
    },
    {
        'value': 'task',
        'label': 'Tasks',
        'icon': 'fa-tasks',
        'color': '#d97706'
    },
    {
        'value': 'coordination',
        'label': 'Coordination',
        'icon': 'fa-handshake',
        'color': '#14b8a6'
    }
]
```

## Events Endpoint Response Format

The `events_endpoint` must return JSON in FullCalendar event format:

```json
[
    {
        "id": "work-item-123",
        "title": "Project Title",
        "start": "2025-10-01",
        "end": "2025-12-31",
        "allDay": true,
        "backgroundColor": "#3b82f6",
        "borderColor": "#3b82f6",
        "extendedProps": {
            "workType": "project",
            "status": "in_progress",
            "url": "/work-items/123/",
            "assignees": ["John Doe"],
            "progress": 65
        }
    }
]
```

### Required Fields

- `id`: Unique event identifier
- `title`: Event title
- `start`: Start date/time (ISO format)

### Optional Fields

- `end`: End date/time (ISO format)
- `allDay`: Boolean for all-day events
- `backgroundColor`: Event background color
- `borderColor`: Event border color
- `extendedProps`: Custom data object
  - `workType`: Event type (matches event_types value)
  - `status`: Event status (e.g., 'completed', 'in_progress')
  - Any other custom fields

## JavaScript Events

### Dispatched Events

#### calendarRefresh

Trigger this event to refresh calendar data:

```javascript
document.body.dispatchEvent(new CustomEvent('calendarRefresh'));
```

#### calendarEventClick

Fired when an event is clicked:

```javascript
document.body.addEventListener('calendarEventClick', (e) => {
    console.log('Event clicked:', e.detail.event);
    console.log('Widget ID:', e.detail.widgetId);
});
```

### Global Functions

Each calendar instance exposes utility functions:

```javascript
// Refresh calendar (replace 'calendarWidget' with your calendar_id)
window.calendarWidget_refresh();

// Close detail panel
window.calendarWidget_closeDetailPanel();

// Show toast notification
window.calendarWidget_showToast('Message', 'success'); // levels: success, error, warning, info
```

## Django View Integration

### Example View

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

@login_required
def calendar_page(request):
    """Render page with embedded calendar widget"""

    event_types = [
        {
            'value': 'project',
            'label': 'Projects',
            'icon': 'fa-folder',
            'color': '#3b82f6'
        },
        {
            'value': 'activity',
            'label': 'Activities',
            'icon': 'fa-calendar-check',
            'color': '#10b981'
        },
    ]

    context = {
        'event_types': event_types,
        'events_endpoint': '/api/calendar/feed/',
    }

    return render(request, 'my_calendar_page.html', context)

@login_required
def calendar_feed(request):
    """Return calendar events in FullCalendar format"""

    events = []
    # Fetch your events from database
    work_items = WorkItem.objects.filter(user=request.user)

    for item in work_items:
        events.append({
            'id': f'work-item-{item.id}',
            'title': item.title,
            'start': item.start_date.isoformat() if item.start_date else None,
            'end': item.due_date.isoformat() if item.due_date else None,
            'allDay': True,
            'backgroundColor': '#3b82f6',
            'borderColor': '#3b82f6',
            'extendedProps': {
                'workType': item.work_type,
                'status': item.status,
                'url': item.get_absolute_url(),
            }
        })

    return JsonResponse(events, safe=False)
```

### Example Template

```django
{% extends "base.html" %}
{% load static %}

{% block title %}My Calendar{% endblock %}

{% block content %}
<div class="container mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6">Project Calendar</h1>

    {% include 'components/calendar_widget.html' with
        calendar_id='projectCalendar'
        events_endpoint='/api/calendar/feed/'
        event_types=event_types
        calendar_height='calc(100vh - 250px)'
    %}
</div>
{% endblock %}

{% block extra_js %}
<!-- FullCalendar is required -->
<script src="{% static 'common/vendor/fullcalendar/index.global.min.js' %}"></script>
{% endblock %}
```

## Multiple Calendars on Same Page

The component is fully scoped and supports multiple instances:

```django
<!-- Projects Calendar -->
<div class="mb-8">
    <h2 class="text-xl font-bold mb-4">Projects</h2>
    {% include 'components/calendar_widget.html' with
        calendar_id='projectsCalendar'
        events_endpoint='/api/projects/calendar/'
        calendar_height='500px'
    %}
</div>

<!-- Tasks Calendar -->
<div class="mb-8">
    <h2 class="text-xl font-bold mb-4">Tasks</h2>
    {% include 'components/calendar_widget.html' with
        calendar_id='tasksCalendar'
        events_endpoint='/api/tasks/calendar/'
        calendar_height='500px'
        show_sidebar=False
    %}
</div>
```

## Customization Examples

### Minimal Calendar (No Sidebar)

```django
{% include 'components/calendar_widget.html' with
    events_endpoint='/api/events/'
    show_sidebar=False
    calendar_height='600px'
%}
```

### Read-Only Calendar

```django
{% include 'components/calendar_widget.html' with
    events_endpoint='/api/events/'
    enable_drag_drop=False
    enable_event_creation=False
%}
```

### Year View by Default

```django
{% include 'components/calendar_widget.html' with
    events_endpoint='/api/events/'
    default_view='multiMonthYear'
%}
```

### Custom Event Types

```django
{% with custom_types='[{"value": "meeting", "label": "Meetings", "icon": "fa-users", "color": "#8b5cf6"}, {"value": "deadline", "label": "Deadlines", "icon": "fa-flag", "color": "#ef4444"}]'|safe %}
    {% include 'components/calendar_widget.html' with
        events_endpoint='/api/events/'
        event_types=custom_types
    %}
{% endwith %}
```

## Styling & Theming

All styles are scoped using the `calendar_id` to prevent conflicts:

```css
/* Override specific calendar styles */
#myCustomCalendar-container {
    background: #f9fafb;
}

#myCustomCalendar-calendar .fc {
    border-radius: 0.5rem;
}
```

## Dependencies

### Required

- **FullCalendar 6.x**: Calendar library
  ```django
  <script src="{% static 'common/vendor/fullcalendar/index.global.min.js' %}"></script>
  ```

- **HTMX**: For dynamic content loading (if using detail panel)
  ```django
  <script src="{% static 'js/htmx.min.js' %}"></script>
  ```

- **Tailwind CSS**: For styling
  ```django
  <link href="{% static 'css/tailwind.css' %}" rel="stylesheet">
  ```

- **Font Awesome**: For icons
  ```django
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  ```

### Optional

- Django authentication (for user-specific events)
- CSRF middleware (for event updates)

## Accessibility

The component follows WCAG 2.1 AA standards:

- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **ARIA Labels**: Proper labels on buttons and controls
- **Screen Readers**: Meaningful text for assistive technology
- **Focus Management**: Clear focus indicators
- **Touch Targets**: Minimum 44x44px touch targets on mobile

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari 14+, Chrome Mobile 90+)

## Performance Considerations

- **Lazy Loading**: Calendar initializes only when container has dimensions
- **Cache Busting**: Automatic timestamp-based cache invalidation
- **Debouncing**: Event fetching optimized to prevent excessive requests
- **Memory Management**: Proper cleanup of event listeners and components

## Troubleshooting

### Calendar Not Rendering

1. **Check FullCalendar is loaded**:
   ```javascript
   console.log(typeof FullCalendar); // Should be 'function'
   ```

2. **Verify container height**:
   ```javascript
   const container = document.getElementById('calendarWidget-container');
   console.log(container.offsetHeight); // Should be > 0
   ```

3. **Check events endpoint**:
   ```bash
   curl http://localhost:8000/api/calendar/feed/
   ```

### Events Not Displaying

1. **Verify response format**: Ensure events match FullCalendar format
2. **Check filters**: Ensure event types are not filtered out
3. **Console errors**: Check browser console for errors

### Drag & Drop Not Working

1. **Verify `enable_drag_drop=True`**
2. **Check CSRF token**: Ensure CSRF token is available
3. **Verify update endpoint**: Ensure update_endpoint is correct

## Migration from Legacy Calendar

If migrating from the old calendar implementation:

```python
# Old implementation
{% include 'components/calendar_widget.html' with
    widget_id='old_calendar'
    events_json=events|json_script:"events-data"
    options_json=options|json_script:"options-data"
%}

# New implementation
{% include 'components/calendar_widget.html' with
    calendar_id='old_calendar'
    events_endpoint='/api/calendar/feed/'
    event_types=event_types
%}
```

## Examples in OBCMS

### Work Items Calendar

```django
{% include 'components/calendar_widget.html' with
    calendar_id='workItemsCalendar'
    events_endpoint='{% url "common:work_items_calendar_feed" %}'
    update_endpoint='{% url "common:calendar_event_update" %}'
%}
```

### Advanced Modern Calendar (Reference Implementation)

See: `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/templates/common/calendar_advanced_modern.html`

This is the original implementation from which this component was extracted.

## Future Enhancements

Potential future improvements:

- [ ] Multiple event selection
- [ ] Bulk event operations
- [ ] Custom event rendering templates
- [ ] Event conflict detection
- [ ] Recurring events support
- [ ] Export to iCal/Google Calendar
- [ ] Print view
- [ ] Offline support with service workers

## Related Documentation

- [FullCalendar Documentation](https://fullcalendar.io/docs)
- [HTMX Documentation](https://htmx.org/docs/)
- [OBCMS UI Components Guide](docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md)
- [Calendar API Views](src/common/views/calendar_api.py)
- [Work Items Calendar Feed](src/common/views/calendar.py)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the reference implementation in `calendar_advanced_modern.html`
3. Consult the FullCalendar documentation
4. Contact the development team

---

**Component Version**: 1.0.0
**Last Updated**: 2025-10-06
**Extracted From**: `calendar_advanced_modern.html`
