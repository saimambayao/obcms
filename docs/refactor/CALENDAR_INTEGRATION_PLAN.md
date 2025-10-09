# Calendar Integration Plan for Unified Work Hierarchy

**Date:** 2025-10-05  
**Status:** PLANNING - Calendar-Specific Implementation  
**Priority:** CRITICAL - Core User-Facing Feature  
**Dependencies:** Unified WorkItem Model (see WORK_ITEM_IMPLEMENTATION_EXAMPLES.md)

---

## 1. Executive Summary

**Goal:** Integrate the unified WorkItem hierarchy (Projects → Activities → Tasks) with the OOBC Calendar system to provide a seamless, hierarchical view of all organizational work.

**Current State:** Calendar aggregates data from **2 separate models** (StaffTask + Event)  
**Target State:** Calendar displays **1 unified WorkItem model** with full hierarchy visualization

**Key Benefits:**
- ✅ **Single Data Source:** No more merging StaffTask + Event
- ✅ **Hierarchy Visualization:** See Projects → Activities → Tasks in calendar
- ✅ **Breadcrumb Display:** Show full work path ("Project X > Activity Y > Task Z")
- ✅ **Type-Based Colors:** Automatic color coding by work item type
- ✅ **Expandable Tree View:** Click to expand/collapse hierarchy levels
- ✅ **Unified Modal:** Same form for all work types

---

## 2. Current Calendar Architecture Analysis

### 2.1 Data Flow (Current)

```
┌─────────────────────────────────────────────────────────────┐
│                 CALENDAR VIEW REQUEST                        │
│              /oobc-management/calendar/                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │   oobc_calendar_feed_json()      │
        │   (common/views/management.py)   │
        └──────────────────┬───────────────┘
                           │
                           ▼
          ┌────────────────────────────────────┐
          │  build_calendar_payload()          │
          │  (common/services/calendar.py)     │
          └────────────┬───────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
    ┌─────────────┐         ┌──────────────┐
    │  StaffTask  │         │    Event     │
    │   Model     │         │    Model     │
    └─────────────┘         └──────────────┘
           │                       │
           ▼                       ▼
    [Blue Tasks]            [Green Events]
           │                       │
           └───────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  MERGED JSON ARRAY   │
            │  (FullCalendar)      │
            └──────────────────────┘
```

**Problems:**
- ❌ **2 data sources** → merge complexity
- ❌ **Different schemas** → normalization required
- ❌ **No hierarchy** → flat event list
- ❌ **Manual color coding** → type detection logic
- ❌ **Separate modals** → task modal vs event modal

### 2.2 Calendar JSON Format (Current)

```json
{
  "events": [
    {
      "id": "task-123",
      "title": "Complete Budget Report",
      "start": "2025-10-15",
      "color": "#3b82f6",
      "module": "staff",
      "type": "task",
      "url": "/oobc-management/staff/tasks/123/modal/"
    },
    {
      "id": "event-456",
      "title": "Quarterly Coordination Meeting",
      "start": "2025-10-16T09:00:00",
      "color": "#059669",
      "module": "coordination",
      "type": "event",
      "url": "/coordination/events/456/modal/"
    }
  ]
}
```

### 2.3 Key Files (Current)

| File | Purpose | Lines of Code |
|------|---------|---------------|
| `src/templates/common/oobc_calendar.html` | Calendar UI (FullCalendar) | 193 |
| `src/common/views/management.py:562` | JSON feed endpoint | ~50 |
| `src/common/services/calendar.py:98` | Data aggregation logic | ~200 |
| `src/templates/common/partials/staff_task_modal.html` | Task modal | ~150 |
| `src/templates/coordination/partials/event_modal.html` | Event modal | ~180 |

**Total Current Code:** ~773 lines

---

## 3. Proposed Calendar Architecture (Unified)

### 3.1 New Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 CALENDAR VIEW REQUEST                        │
│              /oobc-management/calendar/                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   work_items_calendar_feed()         │
        │   (common/views/calendar.py - NEW)   │
        └──────────────────┬─────────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  WorkItem   │
                    │  Model      │
                    │  (MPTT)     │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
       [Projects]    [Activities]     [Tasks]
            │              │              │
            └──────────────┼──────────────┘
                           │
                           ▼
            ┌───────────────────────────────┐
            │   UNIFIED JSON WITH           │
            │   HIERARCHY METADATA          │
            └───────────────────────────────┘
```

**Benefits:**
- ✅ **Single query** with `.select_related('parent')`
- ✅ **Polymorphic types** automatically resolved
- ✅ **Hierarchy included** via MPTT tree fields
- ✅ **Type-based colors** from `work_item.calendar_color` property
- ✅ **Unified modal** via polymorphic dispatch

### 3.2 New Calendar JSON Format (With Hierarchy)

```json
{
  "workItems": [
    {
      "id": "work-item-789",
      "title": "Regional Infrastructure Assessment",
      "type": "Project",
      "start": "2025-10-01",
      "end": "2025-12-31",
      "color": "#1e40af",
      "level": 0,
      "parentId": null,
      "breadcrumb": "Regional Infrastructure Assessment",
      "url": "/work-items/789/modal/",
      "hasChildren": true,
      "childCount": 12
    },
    {
      "id": "work-item-790",
      "title": "Field Visit - Cotabato Province",
      "type": "Activity",
      "start": "2025-10-15T09:00:00",
      "end": "2025-10-15T17:00:00",
      "color": "#059669",
      "level": 1,
      "parentId": "work-item-789",
      "breadcrumb": "Regional Infrastructure Assessment > Field Visit - Cotabato Province",
      "url": "/work-items/790/modal/",
      "hasChildren": true,
      "childCount": 5
    },
    {
      "id": "work-item-791",
      "title": "Prepare assessment checklist",
      "type": "Task",
      "start": "2025-10-14",
      "due": "2025-10-14",
      "color": "#dc2626",
      "level": 2,
      "parentId": "work-item-790",
      "breadcrumb": "Regional Infrastructure Assessment > Field Visit > Prepare checklist",
      "url": "/work-items/791/modal/",
      "hasChildren": false,
      "childCount": 0
    }
  ],
  "hierarchy": {
    "maxLevel": 3,
    "totalProjects": 15,
    "totalActivities": 48,
    "totalTasks": 234
  }
}
```

---

## 4. Calendar UI Enhancements

### 4.1 Hierarchical Display Mode

**New Feature:** Toggle between **Flat View** and **Tree View**

```
┌────────────────────────────────────────────────────────────┐
│  Organization Calendar        [Tree View ▼] [Filter]       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  October 2025                                               │
│  ───────────────────────────────────────────────────────   │
│  Mon  Tue  Wed  Thu  Fri  Sat  Sun                         │
│                                                             │
│   1    2    3    4    5    6    7                          │
│        📘 Project A                                         │
│                                                             │
│   8    9   10   11   12   13   14                          │
│            ├─ 📗 Activity 1.1                              │
│                └─ 📕 Task 1.1.1                            │
│                                                             │
│  15   16   17   18   19   20   21                          │
│       └─ 📗 Activity 1.2                                   │
│           ├─ 📕 Task 1.2.1                                 │
│           └─ 📕 Task 1.2.2                                 │
└────────────────────────────────────────────────────────────┘
```

**Implementation:**
```javascript
// FullCalendar with custom event rendering
eventDidMount: function(info) {
    const workItem = info.event.extendedProps;
    const level = workItem.level || 0;

    // Indent based on hierarchy level
    const indent = level * 20;
    info.el.style.marginLeft = `${indent}px`;

    // Add tree indicators
    if (level > 0) {
        const indicator = document.createElement('span');
        indicator.textContent = '└─ ';
        indicator.className = 'hierarchy-indicator';
        info.el.prepend(indicator);
    }

    // Add expand/collapse button if has children
    if (workItem.hasChildren) {
        const expandBtn = document.createElement('button');
        expandBtn.innerHTML = workItem.expanded ? '▼' : '▶';
        expandBtn.onclick = (e) => {
            e.stopPropagation();
            toggleWorkItemChildren(workItem.id);
        };
        info.el.append(expandBtn);
    }
}
```

### 4.2 Breadcrumb Tooltip

**Enhancement:** Hover over any calendar item to see full hierarchy path

```
┌─────────────────────────────────────────────────────┐
│  📕 Prepare assessment checklist                    │
│  ──────────────────────────────────────────────────│
│  📘 Regional Infrastructure Assessment              │
│   └─ 📗 Field Visit - Cotabato Province            │
│      └─ 📕 Prepare assessment checklist            │
│                                                     │
│  Due: Oct 14, 2025                                  │
│  Assigned: John Doe                                 │
└─────────────────────────────────────────────────────┘
```

**Implementation:**
```javascript
eventMouseEnter: function(info) {
    const tooltip = createTooltip(info.event.extendedProps.breadcrumb);
    showTooltip(tooltip, info.jsEvent);
},
eventMouseLeave: function(info) {
    hideTooltip();
}
```

### 4.3 Collapsible Hierarchy

**Feature:** Click parent items to expand/collapse children

```javascript
function toggleWorkItemChildren(parentId) {
    const calendar = window.__calendar;
    const allEvents = calendar.getEvents();

    // Find all child events
    const children = allEvents.filter(e =>
        e.extendedProps.parentId === parentId
    );

    // Toggle visibility
    children.forEach(child => {
        child.setProp('display', child.display === 'none' ? 'auto' : 'none');
    });

    // Update parent expand state
    const parent = allEvents.find(e => e.id === parentId);
    parent.setExtendedProp('expanded', !parent.extendedProps.expanded);
}
```

### 4.4 Type-Based Filtering

**New Filter UI:**
```html
<div class="calendar-filters">
    <label><input type="checkbox" checked data-filter="Project"> Projects</label>
    <label><input type="checkbox" checked data-filter="Activity"> Activities</label>
    <label><input type="checkbox" checked data-filter="Task"> Tasks</label>
    <label><input type="checkbox" data-filter="completed"> Show Completed</label>
</div>
```

**Implementation:**
```javascript
function applyCalendarFilters() {
    const activeTypes = getCheckedTypes();
    const showCompleted = document.querySelector('[data-filter="completed"]').checked;

    calendar.getEvents().forEach(event => {
        const show = activeTypes.includes(event.extendedProps.type) &&
                     (showCompleted || event.extendedProps.status !== 'completed');

        event.setProp('display', show ? 'auto' : 'none');
    });
}
```

---

## 5. Implementation Changes

### 5.1 New Calendar Feed View

**File:** `src/common/views/calendar.py` (NEW)

```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from common.models import WorkItem

@login_required
def work_items_calendar_feed(request):
    """
    Unified calendar feed for all work items (Projects, Activities, Tasks).

    Returns hierarchical work items with parent-child relationships.
    """
    # Optional filters
    work_type = request.GET.get('type')  # Project, Activity, Task
    status = request.GET.get('status')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    # Base query with hierarchy (MPTT optimization)
    queryset = WorkItem.objects.select_related('parent').prefetch_related('assignees')

    # Date range filter
    if start_date and end_date:
        queryset = queryset.filter(
            models.Q(start_date__range=[start_date, end_date]) |
            models.Q(due_date__range=[start_date, end_date])
        )

    # Type filter (polymorphic)
    if work_type:
        queryset = queryset.filter(polymorphic_ctype__model=work_type.lower())

    # Status filter
    if status:
        queryset = queryset.filter(status=status)

    # Serialize to calendar format
    work_items = []
    for item in queryset:
        work_items.append({
            'id': f'work-item-{item.pk}',
            'title': item.title,
            'type': item.work_type,  # "Project", "Activity", "Task"
            'start': item.start_date.isoformat() if item.start_date else None,
            'end': item.due_date.isoformat() if item.due_date else None,
            'color': item.calendar_color,  # Auto by type
            'level': item.level,  # MPTT tree level
            'parentId': f'work-item-{item.parent.pk}' if item.parent else None,
            'breadcrumb': item.breadcrumb,  # "Project > Activity > Task"
            'url': item.get_modal_url(),
            'hasChildren': item.get_children().exists(),
            'childCount': item.get_children().count(),
            'status': item.status,
            'priority': item.priority,
            'extendedProps': {
                'assignees': [u.get_full_name() for u in item.assignees.all()],
                'progress': item.progress,
            }
        })

    return JsonResponse({
        'workItems': work_items,
        'hierarchy': {
            'maxLevel': queryset.aggregate(models.Max('level'))['level__max'] or 0,
            'totalProjects': queryset.instance_of(Project).count(),
            'totalActivities': queryset.instance_of(Activity).count(),
            'totalTasks': queryset.instance_of(Task).count(),
        }
    })
```

### 5.2 Updated Calendar Template

**File:** `src/templates/common/oobc_calendar.html`

**Changes:**

1. **Update events source URL:**
```javascript
// OLD
events: '{% url "common:oobc_calendar_feed_json" %}',

// NEW
events: '{% url "common:work_items_calendar_feed" %}',
```

2. **Add hierarchy rendering:**
```javascript
eventDidMount: function(info) {
    const workItem = info.event.extendedProps;
    const level = workItem.level || 0;

    // Indent based on level
    if (level > 0) {
        info.el.style.paddingLeft = `${level * 20}px`;
        info.el.classList.add(`hierarchy-level-${level}`);
    }

    // Add type icon
    const icon = getWorkItemIcon(workItem.type);
    const iconEl = document.createElement('span');
    iconEl.innerHTML = icon;
    iconEl.className = 'work-item-icon';
    info.el.prepend(iconEl);
},
```

3. **Add breadcrumb tooltips:**
```javascript
eventMouseEnter: function(info) {
    const breadcrumb = info.event.extendedProps.breadcrumb;
    if (breadcrumb) {
        showTooltip(breadcrumb, info.jsEvent.clientX, info.jsEvent.clientY);
    }
},
eventMouseLeave: function() {
    hideTooltip();
}
```

### 5.3 Unified Work Item Modal

**File:** `src/templates/common/partials/work_item_modal.html` (NEW)

```html
{% load static %}

<div class="work-item-modal">
    {# Header with type icon and breadcrumb #}
    <div class="modal-header">
        <div class="flex items-center justify-between">
            <div>
                <span class="work-item-type-badge {{ work_item.work_type|lower }}">
                    {{ work_item.get_work_type_display }}
                </span>
                <h2 class="text-2xl font-bold mt-2">{{ work_item.title }}</h2>
                <p class="text-sm text-gray-500 mt-1">{{ work_item.breadcrumb }}</p>
            </div>
            <button data-close-modal class="text-gray-400 hover:text-gray-600">
                <i class="fas fa-times text-xl"></i>
            </button>
        </div>
    </div>

    {# Type-specific content sections #}
    <div class="modal-body mt-6 space-y-4">
        {% if work_item.work_type == 'Project' %}
            {% include "common/partials/project_details.html" %}
        {% elif work_item.work_type == 'Activity' %}
            {% include "common/partials/activity_details.html" %}
        {% elif work_item.work_type == 'Task' %}
            {% include "common/partials/task_details.html" %}
        {% endif %}

        {# Shared sections for all types #}
        <div class="timeline-section">
            <h3 class="font-semibold">Timeline</h3>
            <p>Start: {{ work_item.start_date|date:"F j, Y" }}</p>
            <p>Due: {{ work_item.due_date|date:"F j, Y" }}</p>
        </div>

        {# Hierarchy tree #}
        {% if work_item.get_children.exists %}
        <div class="children-section">
            <h3 class="font-semibold">Child Items ({{ work_item.get_children.count }})</h3>
            <ul class="hierarchy-tree">
                {% for child in work_item.get_children %}
                <li>
                    <a href="{% url 'common:work_item_modal' child.pk %}">
                        {{ child.work_type }}: {{ child.title }}
                    </a>
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>

    {# Footer with actions #}
    <div class="modal-footer mt-6 pt-4 border-t flex justify-between">
        <div>
            <a href="{% url 'common:work_item_edit' work_item.pk %}" class="btn btn-secondary">
                <i class="fas fa-edit"></i> Edit
            </a>
        </div>
        <form action="{% url 'common:work_item_delete' work_item.pk %}" method="post" class="delete-form">
            {% csrf_token %}
            <button type="submit" class="btn btn-danger">
                <i class="fas fa-trash"></i> Delete
            </button>
        </form>
    </div>
</div>
```

---

## 6. Migration Strategy (Calendar-Specific)

### Phase 1: Parallel Implementation

**Week 1-2: Create New Calendar Views Alongside Old**

1. **Keep existing calendar feed:**
   - `oobc_calendar_feed_json()` continues working
   - Current users unaffected

2. **Add new unified feed:**
   - Create `work_items_calendar_feed()` (parallel)
   - Test with sample WorkItem data

3. **Feature flag:**
   ```python
   # settings.py
   USE_UNIFIED_CALENDAR = False  # Toggle when ready
   ```

   ```html
   <!-- oobc_calendar.html -->
   {% if USE_UNIFIED_CALENDAR %}
       events: '{% url "common:work_items_calendar_feed" %}',
   {% else %}
       events: '{% url "common:oobc_calendar_feed_json" %}',
   {% endif %}
   ```

### Phase 2: Gradual Rollout

**Week 3-4: Enable for Staff Only**

1. **User-based feature flag:**
   ```python
   if request.user.is_staff:
       USE_UNIFIED_CALENDAR = True
   ```

2. **Collect feedback:**
   - Staff test hierarchical features
   - Report bugs/issues
   - Validate UI/UX

### Phase 3: Full Switchover

**Week 5: Enable for All Users**

1. **Set global flag:**
   ```python
   USE_UNIFIED_CALENDAR = True
   ```

2. **Remove old feed:**
   - Delete `oobc_calendar_feed_json()`
   - Delete `build_calendar_payload()` (if unused elsewhere)
   - Clean up legacy code

---

## 7. Testing Plan

### 7.1 Functional Tests

```python
# tests/test_calendar_integration.py

def test_unified_calendar_feed():
    """Test WorkItem calendar feed returns correct hierarchy."""
    # Create hierarchy: Project > Activity > Task
    project = Project.objects.create(title="Test Project", start_date=date.today())
    activity = Activity.objects.create(
        parent=project,
        title="Test Activity",
        start_date=date.today()
    )
    task = Task.objects.create(
        parent=activity,
        title="Test Task",
        start_date=date.today()
    )

    # Request calendar feed
    response = client.get('/api/work-items/calendar/')
    data = response.json()

    # Assert hierarchy in response
    assert len(data['workItems']) == 3
    assert data['hierarchy']['maxLevel'] == 2

    # Assert parent-child relationships
    task_item = next(item for item in data['workItems'] if item['type'] == 'Task')
    assert task_item['parentId'] == f'work-item-{activity.pk}'
    assert task_item['breadcrumb'] == "Test Project > Test Activity > Test Task"
```

### 7.2 UI Tests

```javascript
// cypress/integration/calendar_spec.js

describe('Unified Calendar', () => {
    it('displays hierarchical work items', () => {
        cy.visit('/oobc-management/calendar/');

        // Check Projects appear
        cy.contains('Test Project').should('be.visible');

        // Expand project to see children
        cy.contains('Test Project').click();

        // Check Activities appear indented
        cy.contains('Test Activity').should('have.class', 'hierarchy-level-1');

        // Check Tasks appear further indented
        cy.contains('Test Task').should('have.class', 'hierarchy-level-2');
    });

    it('shows breadcrumb on hover', () => {
        cy.contains('Test Task').trigger('mouseover');
        cy.contains('Test Project > Test Activity > Test Task').should('be.visible');
    });
});
```

---

## 8. Performance Considerations

### 8.1 Query Optimization

**MPTT Efficiency:**
```python
# Get all descendants in 1 query (MPTT magic)
project = Project.objects.get(pk=1)
descendants = project.get_descendants()  # Single query using lft/rght

# With prefetch for calendar
WorkItem.objects.select_related('parent').prefetch_related(
    'assignees',
    'children'  # Prefetch children for expand/collapse
)
```

### 8.2 Caching Strategy

```python
from django.core.cache import cache

def work_items_calendar_feed(request):
    # Cache key based on user + date range
    cache_key = f"calendar:{request.user.id}:{start_date}:{end_date}"
    cached = cache.get(cache_key)

    if cached:
        return JsonResponse(cached)

    # Build payload
    payload = build_work_items_payload()

    # Cache for 5 minutes
    cache.set(cache_key, payload, 300)

    return JsonResponse(payload)
```

### 8.3 Pagination for Large Trees

**For Projects with 100+ children:**
```javascript
// Load children on-demand
function expandProject(projectId) {
    fetch(`/api/work-items/${projectId}/children/`)
        .then(response => response.json())
        .then(children => {
            children.forEach(child => calendar.addEvent(child));
        });
}
```

---

## 9. Success Criteria

### Must Have (Week 6)
- [ ] Calendar displays Projects, Activities, Tasks from WorkItem model
- [ ] Hierarchy levels render correctly (indentation, icons)
- [ ] Breadcrumb tooltips show full path
- [ ] Type-based color coding works automatically
- [ ] Modal opens for all work item types
- [ ] Delete functionality works (page reload)
- [ ] No performance degradation vs current calendar

### Should Have (Week 8)
- [ ] Expandable/collapsible hierarchy
- [ ] Type filtering (show/hide Projects/Activities/Tasks)
- [ ] Drag-and-drop re-parenting
- [ ] Hierarchy export (print-friendly view)

### Nice to Have (Future)
- [ ] Gantt chart view (timeline with dependencies)
- [ ] Critical path highlighting
- [ ] Workload heatmap by assignee
- [ ] Calendar templates (recurring work hierarchies)

---

## 10. Code Reduction Summary

| Component | Before (Lines) | After (Lines) | Reduction |
|-----------|----------------|---------------|-----------|
| **Calendar Template** | 193 | 220 | -27 (new features) |
| **Calendar Feed View** | 50 | 80 | -30 (unified) |
| **Data Aggregation** | 200 | 0 | +200 (deleted) |
| **Task Modal** | 150 | 0 | +150 (unified) |
| **Event Modal** | 180 | 0 | +180 (unified) |
| **Unified Modal** | 0 | 120 | -120 (new) |
| **TOTAL** | **773** | **420** | **+353 (46% reduction)** |

---

## 11. Rollback Plan

### If Issues Arise

**Step 1: Disable feature flag**
```python
USE_UNIFIED_CALENDAR = False
```

**Step 2: Verify old system works**
- Test old calendar feed
- Confirm task/event modals functional

**Step 3: Collect diagnostics**
- User error reports
- Server logs
- Performance metrics

**Step 4: Fix or defer**
- Quick fix → Re-enable in hours
- Complex issue → Defer to next sprint

---

## 12. Implementation Complete

### ✅ Phase 1: Core Implementation (COMPLETED)

**Date:** 2025-10-05

All core components have been implemented:

1. ✅ **New Calendar Feed View** - `src/common/views/calendar.py`
   - `work_items_calendar_feed()` - Unified JSON feed with hierarchy metadata
   - `work_item_modal()` - Modal view for all work item types
   - MPTT optimization with `.select_related('parent')`
   - Caching (5 minutes) for performance

2. ✅ **Unified WorkItem Modal** - `src/templates/common/partials/work_item_modal.html`
   - Type badge and breadcrumb display
   - Type-specific data sections (Project/Activity/Task)
   - Children hierarchy tree
   - Consistent with OBCMS UI standards

3. ✅ **Enhanced Calendar Template** - `src/templates/common/oobc_calendar.html`
   - Feature flag integration (`USE_UNIFIED_CALENDAR`)
   - Hierarchy rendering with indentation
   - Type icons (📘 Projects, 📗 Activities, 📕 Tasks)
   - Tree indicators (└─) for children
   - Breadcrumb tooltips on hover
   - Type filtering checkboxes
   - Expand/collapse functionality (ready for future enhancement)

4. ✅ **URL Routes** - `src/common/urls.py`
   - `/oobc-management/calendar/work-items/feed/` - Calendar feed
   - `/oobc-management/work-items/<uuid>/modal/` - Modal view

5. ✅ **Feature Flag** - `src/obc_management/settings/base.py`
   - `USE_UNIFIED_CALENDAR = False` (default disabled)
   - Context processor for template access
   - Environment variable support

---

## 13. Setup & Activation Instructions

### Enabling Unified Calendar

**Option 1: Environment Variable (Recommended for Production)**

Add to `.env` file:
```env
USE_UNIFIED_CALENDAR=True
```

**Option 2: Settings Override (Development)**

Edit `src/obc_management/settings/base.py`:
```python
USE_UNIFIED_CALENDAR = True  # Change from False to True
```

**Restart Django Server:**
```bash
cd src
python manage.py runserver
```

---

## 14. Testing Guide

### Prerequisites

Ensure you have sample WorkItem data:

```python
# Django shell
python manage.py shell

from common.models import WorkItem
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Create a test hierarchy
project = WorkItem.objects.create(
    work_type='project',
    title='Regional Infrastructure Assessment',
    start_date='2025-10-01',
    due_date='2025-12-31',
    calendar_color='#1e40af',
    created_by=user
)

activity = WorkItem.objects.create(
    parent=project,
    work_type='activity',
    title='Field Visit - Cotabato Province',
    start_date='2025-10-15',
    due_date='2025-10-15',
    calendar_color='#059669',
    created_by=user
)

task = WorkItem.objects.create(
    parent=activity,
    work_type='task',
    title='Prepare assessment checklist',
    start_date='2025-10-14',
    due_date='2025-10-14',
    calendar_color='#dc2626',
    created_by=user
)
```

### Test Checklist

#### 1. **Hierarchy Rendering** ✓
- [ ] Navigate to `/oobc-management/calendar/`
- [ ] Verify Projects appear with 📘 icon
- [ ] Verify Activities appear with 📗 icon, indented 20px
- [ ] Verify Tasks appear with 📕 icon, indented 40px
- [ ] Verify tree indicators (└─) appear for children

#### 2. **Breadcrumb Tooltips** ✓
- [ ] Hover over a Task event
- [ ] Verify tooltip shows: "Project > Activity > Task"
- [ ] Tooltip disappears on mouse leave

#### 3. **Type Filtering** ✓
- [ ] Uncheck "📘 Projects" filter
- [ ] Verify all Projects are hidden
- [ ] Re-check to show Projects
- [ ] Repeat for Activities and Tasks
- [ ] Test "Show Completed" filter

#### 4. **Modal Interaction** ✓
- [ ] Click on a Project event
- [ ] Verify modal opens with Project badge
- [ ] Verify breadcrumb displays correctly
- [ ] Verify children list shows Activities/Tasks
- [ ] Close modal
- [ ] Repeat for Activity and Task

#### 5. **Performance** ✓
- [ ] Check Network tab for calendar feed request
- [ ] Verify response time < 500ms
- [ ] Verify caching works (subsequent requests faster)

#### 6. **Feature Flag Toggle** ✓
- [ ] Set `USE_UNIFIED_CALENDAR=False`
- [ ] Restart server
- [ ] Verify old calendar loads (no hierarchy)
- [ ] Set `USE_UNIFIED_CALENDAR=True`
- [ ] Restart server
- [ ] Verify unified calendar loads

---

## 15. Known Limitations (Future Enhancements)

### Phase 2 Features (Not Yet Implemented)
1. **Expand/Collapse Children** - JavaScript exists but needs refinement
2. **Drag-and-drop Re-parenting** - Future enhancement
3. **Edit Functionality** - Modal has Edit button but needs form integration
4. **Delete Functionality** - Modal has Delete button but needs WorkItem delete view

### Migration Notes
- Old calendar (`oobc_calendar_feed_json`) remains functional
- Parallel implementation allows gradual migration
- No breaking changes to existing functionality

---

## 16. Next Steps

### Immediate Actions
1. ✅ **Implementation Complete** - All core features implemented
2. ⏳ **Testing** - Verify all test checklist items
3. ⏳ **Sample Data** - Create test WorkItems for demo
4. ⏳ **Stakeholder Review** - Demo unified calendar features

### Phase 2: Enhanced Features
1. **Edit/Delete Integration** - Connect modal buttons to WorkItem CRUD views
2. **Expand/Collapse Polish** - Refine expand button behavior
3. **Gantt View** - Timeline visualization with dependencies
4. **Performance Optimization** - Lazy loading for large hierarchies

### Phase 3: Full Switchover
1. **Enable for All Users** - Set `USE_UNIFIED_CALENDAR=True` in production
2. **Monitor Performance** - Track query performance and caching
3. **Remove Old Code** - Delete `oobc_calendar_feed_json()` when confident
4. **User Training** - Document hierarchy features

---

## 17. Rollback Plan

### If Issues Arise

**Step 1: Disable Feature Flag**
```bash
# .env
USE_UNIFIED_CALENDAR=False
```

**Step 2: Restart Server**
```bash
python manage.py runserver
```

**Step 3: Verify Old Calendar Works**
- Test task/event display
- Verify modals functional

**Step 4: Report Issues**
- Collect error logs
- Document unexpected behavior
- Create bug report with reproduction steps

---

## 18. Files Modified

### New Files Created
1. `src/common/views/calendar.py` - Calendar feed views
2. `src/templates/common/partials/work_item_modal.html` - Unified modal

### Modified Files
1. `src/templates/common/oobc_calendar.html` - Hierarchy rendering, filters
2. `src/common/urls.py` - New URL routes
3. `src/common/views/__init__.py` - Import new views
4. `src/obc_management/settings/base.py` - Feature flag
5. `src/common/context_processors.py` - Template context

---

**Status:** ✅ IMPLEMENTATION COMPLETE
**Ready for Testing:** YES
**Production Ready:** PENDING TESTING & STAKEHOLDER APPROVAL
**Implementation Date:** 2025-10-05
**Next Review:** Post-Testing Feedback

