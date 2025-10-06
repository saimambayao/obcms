# Calendar Widget Component - Usage Examples

This document provides practical examples for implementing the OBCMS Calendar Widget Component.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Django View Examples](#django-view-examples)
3. [Template Examples](#template-examples)
4. [JavaScript Integration](#javascript-integration)
5. [Customization Examples](#customization-examples)

---

## Basic Examples

### 1. Minimal Calendar

The simplest possible implementation:

```django
{% load static %}

{% block extra_js %}
<script src="{% static 'common/vendor/fullcalendar/index.global.min.js' %}"></script>
{% endblock %}

{% block content %}
<div class="container mx-auto p-6">
    {% include 'components/calendar_widget.html' with
        events_endpoint='/oobc-management/work-items/calendar/feed/'
    %}
</div>
{% endblock %}
```

### 2. Full-Featured Calendar

With all options configured:

```django
{% include 'components/calendar_widget.html' with
    calendar_id='myCalendar'
    events_endpoint='/api/calendar/events/'
    event_types=event_types
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

### 3. Compact Calendar (No Sidebar)

Perfect for embedding in dashboards:

```django
<div class="bg-white rounded-xl shadow-lg p-4">
    <h2 class="text-lg font-bold mb-4">Upcoming Events</h2>
    {% include 'components/calendar_widget.html' with
        calendar_id='dashboardCalendar'
        events_endpoint='/api/events/'
        show_sidebar=False
        calendar_height='400px'
        default_view='timeGridWeek'
    %}
</div>
```

---

## Django View Examples

### Example 1: Basic Calendar View

**views.py**:
```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from common.models import WorkItem

@login_required
def calendar_page(request):
    """Render calendar page with event types"""

    event_types = [
        {'value': 'project', 'label': 'Projects', 'icon': 'fa-folder', 'color': '#3b82f6'},
        {'value': 'activity', 'label': 'Activities', 'icon': 'fa-calendar-check', 'color': '#10b981'},
        {'value': 'task', 'label': 'Tasks', 'icon': 'fa-tasks', 'color': '#d97706'},
    ]

    return render(request, 'calendar_page.html', {
        'event_types': event_types,
    })

@login_required
def calendar_feed(request):
    """Return calendar events in FullCalendar format"""

    events = []
    work_items = WorkItem.objects.filter(created_by=request.user)

    for item in work_items:
        events.append({
            'id': f'work-item-{item.id}',
            'title': item.title,
            'start': item.start_date.isoformat() if item.start_date else None,
            'end': item.due_date.isoformat() if item.due_date else None,
            'allDay': True,
            'backgroundColor': get_color_for_type(item.work_type),
            'borderColor': get_color_for_type(item.work_type),
            'extendedProps': {
                'workType': item.work_type,
                'status': item.status,
                'url': item.get_absolute_url(),
            }
        })

    return JsonResponse(events, safe=False)

def get_color_for_type(work_type):
    colors = {
        'project': '#3b82f6',
        'activity': '#10b981',
        'task': '#d97706',
    }
    return colors.get(work_type, '#6b7280')
```

**urls.py**:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.calendar_page, name='calendar_page'),
    path('calendar/feed/', views.calendar_feed, name='calendar_feed'),
]
```

**template (calendar_page.html)**:
```django
{% extends "base.html" %}
{% load static %}

{% block title %}Calendar{% endblock %}

{% block extra_js %}
<script src="{% static 'common/vendor/fullcalendar/index.global.min.js' %}"></script>
{% endblock %}

{% block content %}
<div class="container mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6">My Calendar</h1>

    {% include 'components/calendar_widget.html' with
        calendar_id='mainCalendar'
        events_endpoint='{% url "calendar_feed" %}'
        event_types=event_types
    %}
</div>
{% endblock %}
```

### Example 2: Department Calendar with Filters

**views.py**:
```python
@login_required
def department_calendar(request):
    """Department-wide calendar with team filtering"""

    department = request.user.profile.department

    # Get team members for filtering
    team_members = User.objects.filter(profile__department=department)

    event_types = [
        {'value': 'meeting', 'label': 'Meetings', 'icon': 'fa-users', 'color': '#8b5cf6'},
        {'value': 'deadline', 'label': 'Deadlines', 'icon': 'fa-flag', 'color': '#ef4444'},
        {'value': 'event', 'label': 'Events', 'icon': 'fa-calendar', 'color': '#3b82f6'},
    ]

    return render(request, 'department_calendar.html', {
        'event_types': event_types,
        'team_members': team_members,
        'department': department,
    })

@login_required
def department_calendar_feed(request):
    """Return department events"""

    department = request.user.profile.department
    assigned_to = request.GET.get('assigned_to')  # Optional filter

    events_qs = Event.objects.filter(department=department)

    if assigned_to:
        events_qs = events_qs.filter(assigned_to_id=assigned_to)

    events = []
    for event in events_qs:
        events.append({
            'id': f'event-{event.id}',
            'title': f'{event.title} ({event.assigned_to.get_full_name()})',
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat() if event.end_datetime else None,
            'allDay': event.is_all_day,
            'backgroundColor': get_event_color(event.event_type),
            'extendedProps': {
                'workType': event.event_type,
                'status': event.status,
                'assigned_to': event.assigned_to.get_full_name(),
            }
        })

    return JsonResponse(events, safe=False)
```

### Example 3: Project Timeline Calendar

**views.py**:
```python
@login_required
def project_timeline(request, project_id):
    """Project-specific timeline calendar"""

    project = get_object_or_404(Project, id=project_id)

    event_types = [
        {'value': 'milestone', 'label': 'Milestones', 'icon': 'fa-flag-checkered', 'color': '#10b981'},
        {'value': 'deliverable', 'label': 'Deliverables', 'icon': 'fa-box', 'color': '#3b82f6'},
        {'value': 'review', 'label': 'Reviews', 'icon': 'fa-check-circle', 'color': '#f59e0b'},
    ]

    return render(request, 'project_timeline.html', {
        'project': project,
        'event_types': event_types,
    })

@login_required
def project_timeline_feed(request, project_id):
    """Return project timeline events"""

    project = get_object_or_404(Project, id=project_id)

    events = []

    # Add milestones
    for milestone in project.milestones.all():
        events.append({
            'id': f'milestone-{milestone.id}',
            'title': milestone.name,
            'start': milestone.due_date.isoformat(),
            'allDay': True,
            'backgroundColor': '#10b981',
            'extendedProps': {
                'workType': 'milestone',
                'status': milestone.status,
            }
        })

    # Add deliverables
    for deliverable in project.deliverables.all():
        events.append({
            'id': f'deliverable-{deliverable.id}',
            'title': deliverable.name,
            'start': deliverable.start_date.isoformat(),
            'end': deliverable.due_date.isoformat(),
            'backgroundColor': '#3b82f6',
            'extendedProps': {
                'workType': 'deliverable',
                'status': deliverable.status,
            }
        })

    return JsonResponse(events, safe=False)
```

---

## Template Examples

### Example 1: Dashboard with Embedded Calendar

```django
{% extends "base.html" %}
{% load static %}

{% block extra_js %}
<script src="{% static 'common/vendor/fullcalendar/index.global.min.js' %}"></script>
{% endblock %}

{% block content %}
<div class="container mx-auto p-6 space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white rounded-xl shadow p-6">
            <h3 class="text-lg font-semibold mb-2">Total Tasks</h3>
            <p class="text-3xl font-bold text-blue-600">{{ total_tasks }}</p>
        </div>
        <!-- More stats... -->
    </div>

    <!-- Embedded Calendar -->
    <div class="bg-white rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-bold mb-4">Upcoming Schedule</h2>
        {% include 'components/calendar_widget.html' with
            calendar_id='dashboardCalendar'
            events_endpoint='{% url "calendar_feed" %}'
            show_sidebar=False
            calendar_height='500px'
            default_view='timeGridWeek'
        %}
    </div>
</div>
{% endblock %}
```

### Example 2: Side-by-Side Calendars

```django
{% extends "base.html" %}
{% load static %}

{% block extra_js %}
<script src="{% static 'common/vendor/fullcalendar/index.global.min.js' %}"></script>
{% endblock %}

{% block content %}
<div class="container mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6">Team Calendars</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- My Calendar -->
        <div class="bg-white rounded-xl shadow-lg p-4">
            <h2 class="text-lg font-bold mb-3">My Calendar</h2>
            {% include 'components/calendar_widget.html' with
                calendar_id='myCalendar'
                events_endpoint='{% url "my_calendar_feed" %}'
                show_sidebar=False
                calendar_height='600px'
            %}
        </div>

        <!-- Team Calendar -->
        <div class="bg-white rounded-xl shadow-lg p-4">
            <h2 class="text-lg font-bold mb-3">Team Calendar</h2>
            {% include 'components/calendar_widget.html' with
                calendar_id='teamCalendar'
                events_endpoint='{% url "team_calendar_feed" %}'
                show_sidebar=False
                calendar_height='600px'
            %}
        </div>
    </div>
</div>
{% endblock %}
```

### Example 3: Full-Page Calendar

```django
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<style>
    /* Remove padding for full-page calendar */
    .main-content {
        padding: 0 !important;
    }
</style>
{% endblock %}

{% block extra_js %}
<script src="{% static 'common/vendor/fullcalendar/index.global.min.js' %}"></script>
{% endblock %}

{% block content %}
{% include 'components/calendar_widget.html' with
    calendar_id='fullPageCalendar'
    events_endpoint='{% url "work_items_calendar_feed" %}'
    calendar_height='calc(100vh - 64px)'
    event_types=event_types
%}
{% endblock %}
```

---

## JavaScript Integration

### Example 1: Refresh Calendar on Action

```javascript
// After creating a new event
function handleEventCreated(eventData) {
    // Refresh the calendar
    document.body.dispatchEvent(new CustomEvent('calendarRefresh'));

    // Show success toast
    window.mainCalendar_showToast('Event created successfully', 'success');
}
```

### Example 2: Listen to Event Clicks

```javascript
// Custom handler for event clicks
document.body.addEventListener('calendarEventClick', (e) => {
    const event = e.detail.event;
    const widgetId = e.detail.widgetId;

    console.log('Event clicked:', event.title);
    console.log('From calendar:', widgetId);

    // Custom action
    if (event.extendedProps.workType === 'meeting') {
        showMeetingDetails(event.id);
    }
});
```

### Example 3: Programmatic Calendar Control

```javascript
// Access calendar instance
const calendar = window.myCalendar_calendar;

// Change view
calendar.changeView('timeGridWeek');

// Navigate to specific date
calendar.gotoDate('2025-12-25');

// Get all events
const events = calendar.getEvents();
console.log('Total events:', events.length);

// Close detail panel
window.myCalendar_closeDetailPanel();
```

### Example 4: HTMX Integration

```html
<!-- Button to refresh calendar after HTMX action -->
<button
    hx-post="/api/events/create/"
    hx-target="#modal-container"
    hx-on::after-request="document.body.dispatchEvent(new CustomEvent('calendarRefresh'))"
    class="btn btn-primary">
    Create Event
</button>
```

---

## Customization Examples

### Example 1: Custom Event Types

```python
# In your view
custom_event_types = [
    {
        'value': 'webinar',
        'label': 'Webinars',
        'icon': 'fa-video',
        'color': '#ec4899'
    },
    {
        'value': 'workshop',
        'label': 'Workshops',
        'icon': 'fa-chalkboard-teacher',
        'color': '#8b5cf6'
    },
    {
        'value': 'consultation',
        'label': 'Consultations',
        'icon': 'fa-comments',
        'color': '#14b8a6'
    },
]

context = {
    'event_types': custom_event_types,
}
```

```django
{% include 'components/calendar_widget.html' with
    events_endpoint='/api/events/'
    event_types=event_types
%}
```

### Example 2: Read-Only Calendar

```django
<!-- Perfect for public-facing event listings -->
{% include 'components/calendar_widget.html' with
    calendar_id='publicCalendar'
    events_endpoint='/api/public/events/'
    enable_drag_drop=False
    enable_event_creation=False
    show_sidebar=True
    show_completed_filter=False
%}
```

### Example 3: Year View by Default

```django
<!-- Great for long-term planning -->
{% include 'components/calendar_widget.html' with
    events_endpoint='/api/events/'
    default_view='multiMonthYear'
    calendar_height='calc(100vh - 150px)'
%}
```

### Example 4: Custom Styling

```django
{% include 'components/calendar_widget.html' with
    calendar_id='customStyledCalendar'
    events_endpoint='/api/events/'
%}

<style>
    /* Override calendar styles */
    #customStyledCalendar-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1rem;
        padding: 1rem;
    }

    #customStyledCalendar-calendar .fc {
        background: rgba(255, 255, 255, 0.95);
    }

    #customStyledCalendar-sidebar {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
</style>
```

### Example 5: Conditional Sidebar

```django
<!-- Show sidebar only on desktop -->
{% include 'components/calendar_widget.html' with
    events_endpoint='/api/events/'
    show_sidebar=request.user_agent.is_pc
%}
```

---

## Advanced Examples

### Multi-User Calendar with Color Coding

**views.py**:
```python
@login_required
def team_calendar_feed(request):
    """Color-code events by assigned user"""

    user_colors = {
        'john': '#3b82f6',
        'jane': '#10b981',
        'bob': '#f59e0b',
    }

    events = []
    tasks = Task.objects.filter(team=request.user.team)

    for task in tasks:
        username = task.assigned_to.username
        color = user_colors.get(username, '#6b7280')

        events.append({
            'id': f'task-{task.id}',
            'title': f'{task.title} ({task.assigned_to.first_name})',
            'start': task.due_date.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'workType': 'task',
                'assigned_to': username,
            }
        })

    return JsonResponse(events, safe=False)
```

### Recurring Events

**views.py**:
```python
from dateutil.rrule import rrule, WEEKLY
from datetime import datetime, timedelta

@login_required
def recurring_events_feed(request):
    """Generate recurring events"""

    events = []
    base_event = Event.objects.get(id=1)

    # Generate weekly recurring events for next 3 months
    start_date = datetime.now()
    end_date = start_date + timedelta(days=90)

    for dt in rrule(WEEKLY, dtstart=start_date, until=end_date):
        events.append({
            'id': f'recurring-{base_event.id}-{dt.strftime("%Y%m%d")}',
            'title': f'{base_event.title} (Recurring)',
            'start': dt.isoformat(),
            'backgroundColor': '#8b5cf6',
            'extendedProps': {
                'workType': 'recurring',
                'original_id': base_event.id,
            }
        })

    return JsonResponse(events, safe=False)
```

---

## Testing Examples

### Unit Test

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import json

class CalendarFeedTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')

    def test_calendar_feed_returns_json(self):
        response = self.client.get('/api/calendar/feed/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_calendar_feed_format(self):
        response = self.client.get('/api/calendar/feed/')
        data = json.loads(response.content)

        self.assertIsInstance(data, list)
        if len(data) > 0:
            event = data[0]
            self.assertIn('id', event)
            self.assertIn('title', event)
            self.assertIn('start', event)
```

---

## Common Patterns

### Pattern 1: Calendar with External Filters

```django
<div class="mb-4">
    <label class="block text-sm font-medium mb-2">Filter by User</label>
    <select id="userFilter" class="form-select">
        <option value="">All Users</option>
        {% for user in team_members %}
        <option value="{{ user.id }}">{{ user.get_full_name }}</option>
        {% endfor %}
    </select>
</div>

{% include 'components/calendar_widget.html' with
    calendar_id='teamCalendar'
    events_endpoint='/api/calendar/feed/'
%}

<script>
document.getElementById('userFilter').addEventListener('change', function() {
    // Update endpoint with filter
    const userId = this.value;
    const calendar = window.teamCalendar_calendar;

    // Refetch with new filter
    calendar.refetchEvents();
});
</script>
```

### Pattern 2: Calendar with Action Buttons

```django
<div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-bold">My Calendar</h2>
    <div class="space-x-2">
        <button onclick="window.myCalendar_calendar.today()" class="btn btn-sm">
            Today
        </button>
        <button onclick="window.myCalendar_refresh()" class="btn btn-sm">
            <i class="fas fa-sync-alt"></i> Refresh
        </button>
        <a href="{% url 'event_create' %}" class="btn btn-sm btn-primary">
            <i class="fas fa-plus"></i> New Event
        </a>
    </div>
</div>

{% include 'components/calendar_widget.html' with
    calendar_id='myCalendar'
    events_endpoint='/api/calendar/feed/'
%}
```

---

## Troubleshooting Tips

### Problem: Calendar not rendering

**Solution**: Ensure FullCalendar is loaded before the widget:

```django
{% block extra_js %}
<!-- MUST be loaded before calendar widget -->
<script src="{% static 'common/vendor/fullcalendar/index.global.min.js' %}"></script>
{% endblock %}
```

### Problem: Events not displaying

**Check endpoint response**:
```bash
curl -H "Cookie: sessionid=..." http://localhost:8000/api/calendar/feed/
```

**Verify format**:
```python
# Each event MUST have at minimum:
{
    'id': 'unique-id',
    'title': 'Event Title',
    'start': '2025-10-01'  # ISO format
}
```

### Problem: Drag & drop not working

**Check CSRF token**:
```django
{% csrf_token %}
<!-- OR -->
<meta name="csrf-token" content="{{ csrf_token }}">
```

---

For more information, see:
- [Calendar Widget Documentation](CALENDAR_WIDGET_COMPONENT.md)
- [FullCalendar Docs](https://fullcalendar.io/docs)
- [HTMX Documentation](https://htmx.org/docs/)
