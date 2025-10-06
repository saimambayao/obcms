# OBCMS Advanced Calendar Architecture

**Date:** 2025-10-06
**Status:** Design Phase
**Priority:** MEDIUM
**Complexity:** Moderate

---

## Executive Summary

This document outlines the architecture for a **third, completely standalone modern calendar** for OBCMS, inspired by Google Calendar's UI. This calendar is separate from:

1. **Existing Calendar #1**: `/oobc-management/calendar/` - Main OOBC calendar (`oobc_calendar.html`)
2. **Existing Calendar #2**: `/coordination/calendar/` - Coordination calendar (`coordination/calendar.html`)

**New Calendar #3**: `/oobc-management/calendar/advanced/` - Advanced Google Calendar-style view with:
- Multi-view toggles (Month, Week, Day, Year)
- Light-colored left sidebar with mini calendar and filters
- Right-side detail panel that slides in on event click
- Event type legend with color-coded indicators
- Advanced filtering (Projects, Activities, Tasks, Show Completed)
- Fully responsive design

---

## Current State Analysis

### Existing Calendar Infrastructure

#### Calendar #1: Main OOBC Calendar
- **URL**: `/oobc-management/calendar/`
- **Template**: `src/templates/common/oobc_calendar.html`
- **View**: `oobc_calendar(request)` in `common/views/management.py`
- **Features**:
  - Full-page FullCalendar implementation
  - Hero section with gradient background
  - 3D milk white stat cards
  - Type filters (Projects, Activities, Tasks)
  - Modal for event details
  - Links to "Modern View" (already exists)

#### Calendar #2: Coordination Calendar
- **URL**: `/coordination/calendar/`
- **Template**: `src/templates/coordination/calendar.html`
- **View**: `coordination_calendar(request)` in coordination views
- **Features**:
  - Coordination-focused calendar
  - Event and activity snapshots
  - Right sidebar with upcoming events/activities
  - Links to "Modern Calendar View"

#### Calendar #3 (Existing "Modern View")
- **URL**: `/oobc-management/calendar/modern/`
- **Template**: `src/templates/common/calendar_modern.html`
- **View**: `oobc_calendar_modern(request)` in `common/views/management.py`
- **Features**:
  - View mode switcher (Month/Week/Day/Year)
  - Left sidebar with mini calendar and filters
  - Uses same data feed as Calendar #1

### Data Source

All calendars use the **unified WorkItem feed**:
- **Endpoint**: `/oobc-management/calendar/work-items/feed/`
- **View**: `work_items_calendar_feed(request)` in `common/views/calendar.py`
- **Returns**: JSON array of work items (Projects, Activities, Tasks) in FullCalendar format

---

## Proposed Architecture: Advanced Calendar (Calendar #4)

### Design Justification

**Why create a fourth calendar when Modern View already exists?**

1. **Modern View is functional but not Google Calendar-like**
   - Current Modern View has basic filters and mini calendar
   - Missing: Right-side detail panel (slides in on click)
   - Missing: Advanced UI polish (smooth animations, hover states)
   - Missing: Event type legend with live color indicators

2. **Advanced Calendar provides enterprise-grade UX**
   - **Google Calendar-inspired**: Industry-standard UI patterns
   - **Productivity-focused**: Quick filters, keyboard shortcuts, instant details
   - **Professional**: Suitable for government/enterprise deployment

3. **Standalone design allows experimentation**
   - Test advanced features without disrupting existing calendars
   - A/B testing with users (Classic vs Modern vs Advanced)
   - Future consideration: Replace one of the existing calendars if Advanced is preferred

---

## Component Architecture

### 1. Route & URL Pattern

**New Route**: `/oobc-management/calendar/advanced/`

```python
# src/common/urls.py
path("oobc-management/calendar/advanced/",
     views.oobc_calendar_advanced,
     name="oobc_calendar_advanced"),
```

### 2. Django View Function

**File**: `src/common/views/management.py`

```python
@login_required
def oobc_calendar_advanced(request):
    """
    Advanced Google Calendar-inspired view with:
    - Multi-view toggles (Month, Week, Day, Year)
    - Left sidebar: Mini calendar + filters + legend
    - Right detail panel: Slides in on event click
    - Advanced filtering and search
    """
    context = {
        "USE_UNIFIED_CALENDAR": getattr(settings, "USE_UNIFIED_CALENDAR", True),
        "CALENDAR_VIEW": "advanced",  # Distinguish from other calendars
    }
    return render(request, "common/calendar_advanced.html", context)
```

### 3. Template Structure

**New File**: `src/templates/common/calendar_advanced.html`

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Title + View Toggles + Action Buttons                      │
│ [Month] [Week] [Day] [Year]     [Today] [Create]                  │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────┬────────────────────────────────────┬────────────────┐
│ LEFT SIDEBAR  │      MAIN CALENDAR AREA            │ DETAIL PANEL   │
│ (Light Gray)  │                                    │ (Slides In)    │
│               │                                    │                │
│ ┌───────────┐ │  ┌──────────────────────────────┐ │ ┌────────────┐ │
│ │ Mini Cal  │ │  │                              │ │ │ Event:     │ │
│ │ Oct 2025  │ │  │   FullCalendar Instance      │ │ │ Project X  │ │
│ └───────────┘ │  │                              │ │ │            │ │
│               │  │   (Month/Week/Day/Year view) │ │ │ Date:      │ │
│ ┌───────────┐ │  │                              │ │ │ Oct 15     │ │
│ │ Filters   │ │  │                              │ │ │            │ │
│ │ ☑ Projects│ │  │                              │ │ │ Details... │ │
│ │ ☑ Activity│ │  └──────────────────────────────┘ │ │            │ │
│ │ ☑ Tasks   │ │                                    │ │ [Edit]     │ │
│ │ ☐ Complete│ │                                    │ │ [Delete]   │ │
│ └───────────┘ │                                    │ └────────────┘ │
│               │                                    │                │
│ ┌───────────┐ │                                    │ (Hidden by    │
│ │ Legend    │ │                                    │  default)     │
│ │ ● Project │ │                                    │                │
│ │ ● Activity│ │                                    │                │
│ │ ● Task    │ │                                    │                │
│ └───────────┘ │                                    │                │
└───────────────┴────────────────────────────────────┴────────────────┘
```

### 4. Layout Breakdown

#### A. Header Section
```html
<div class="bg-white rounded-xl shadow-md border border-gray-200 p-6 mb-6">
    <!-- Title -->
    <h1>Advanced Calendar</h1>

    <!-- View Mode Toggles -->
    <div class="view-toggles">
        <button data-view="dayGridMonth">Month</button>
        <button data-view="timeGridWeek">Week</button>
        <button data-view="timeGridDay">Day</button>
        <button data-view="multiMonthYear">Year</button>
    </div>

    <!-- Action Buttons -->
    <a href="{% url 'common:work_item_create' %}">Create</a>
    <button id="todayBtn">Today</button>
</div>
```

#### B. Left Sidebar (Light Gray Background)
```html
<aside class="bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl p-5">
    <!-- Mini Calendar -->
    <div id="miniCalendar" class="mb-6"></div>

    <!-- Filters -->
    <div class="filters mb-6">
        <h3>Show</h3>
        <label><input type="checkbox" checked data-filter="project"> Projects</label>
        <label><input type="checkbox" checked data-filter="activity"> Activities</label>
        <label><input type="checkbox" checked data-filter="task"> Tasks</label>
        <label><input type="checkbox" data-filter="completed"> Show Completed</label>
    </div>

    <!-- Legend -->
    <div class="legend">
        <h3>Event Types</h3>
        <div class="legend-item">
            <span class="color-dot bg-blue-600"></span>
            <span>Project</span>
        </div>
        <div class="legend-item">
            <span class="color-dot bg-emerald-600"></span>
            <span>Activity</span>
        </div>
        <div class="legend-item">
            <span class="color-dot bg-purple-600"></span>
            <span>Task</span>
        </div>
    </div>
</aside>
```

#### C. Main Calendar Area
```html
<div class="calendar-main bg-white rounded-xl shadow-lg border border-gray-200 p-6">
    <div id="calendar"></div>
</div>
```

#### D. Right Detail Panel (Slides In)
```html
<aside id="detailPanel" class="detail-panel hidden">
    <div class="panel-header">
        <h2>Event Details</h2>
        <button id="closePanel">×</button>
    </div>
    <div class="panel-content" id="detailContent">
        <!-- Loaded via AJAX when event clicked -->
    </div>
</aside>
```

### 5. CSS Architecture

**New File**: `src/static/common/css/calendar-advanced.css`

```css
/* ============================================
   ADVANCED CALENDAR STYLES
   Google Calendar-inspired UI
   ============================================ */

/* Three-column grid layout */
.calendar-advanced-layout {
    display: grid;
    grid-template-columns: 280px 1fr 360px;
    gap: 1.5rem;
    transition: grid-template-columns 0.3s ease;
}

/* When detail panel hidden */
.calendar-advanced-layout.panel-hidden {
    grid-template-columns: 280px 1fr 0;
}

/* Left Sidebar - Light colored */
.calendar-sidebar-left {
    background: linear-gradient(135deg, #F9FAFB 0%, #EFF6FF 100%);
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Mini Calendar */
.mini-calendar {
    font-size: 0.875rem;
}

/* Filters */
.calendar-filters label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    cursor: pointer;
    border-radius: 0.5rem;
    transition: background-color 0.2s;
}

.calendar-filters label:hover {
    background-color: rgba(255, 255, 255, 0.6);
}

/* Legend */
.calendar-legend {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding-top: 1rem;
    margin-top: 1rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
}

.color-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
}

/* Right Detail Panel - Slides in from right */
.detail-panel {
    position: fixed;
    right: 0;
    top: 0;
    height: 100vh;
    width: 400px;
    background: white;
    box-shadow: -4px 0 12px rgba(0, 0, 0, 0.15);
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 100;
    overflow-y: auto;
}

.detail-panel.visible {
    transform: translateX(0);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #E5E7EB;
}

.panel-content {
    padding: 1.5rem;
}

/* View Toggle Buttons */
.view-btn {
    background: white;
    border: 1px solid #E5E7EB;
    color: #6B7280;
}

.view-btn.active {
    background: linear-gradient(135deg, #3B82F6 0%, #10B981 100%);
    color: white;
    border-color: transparent;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

/* Responsive Design */
@media (max-width: 1024px) {
    .calendar-advanced-layout {
        grid-template-columns: 1fr;
    }

    .calendar-sidebar-left {
        order: 2; /* Move below calendar on mobile */
    }

    .detail-panel {
        width: 100%;
    }
}
```

### 6. JavaScript Architecture

**Component**: Calendar initialization, filters, detail panel

```javascript
// src/static/common/js/calendar-advanced.js

(function() {
    'use strict';

    // ============================================
    // INITIALIZATION
    // ============================================

    const calendarEl = document.getElementById('calendar');
    const miniCalendarEl = document.getElementById('miniCalendar');
    const detailPanel = document.getElementById('detailPanel');
    const detailContent = document.getElementById('detailContent');

    // Initialize main calendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        height: 'auto',
        headerToolbar: {
            left: 'prev,next',
            center: 'title',
            right: ''  // View controls in separate UI
        },

        // Events from unified feed
        events: function(info, successCallback, failureCallback) {
            fetch('/oobc-management/calendar/work-items/feed/?start=' + info.startStr + '&end=' + info.endStr)
                .then(response => response.json())
                .then(data => successCallback(data))
                .catch(error => failureCallback(error));
        },

        // Event click handler - Show detail panel
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            showDetailPanel(info.event);
        },

        // Styling
        eventClassNames: 'rounded-lg px-2 py-1 cursor-pointer',
    });

    calendar.render();

    // Initialize mini calendar
    const miniCalendar = new FullCalendar.Calendar(miniCalendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: false,
        height: 'auto',

        // Date click - Navigate main calendar
        dateClick: function(info) {
            calendar.gotoDate(info.dateStr);
        },

        // Mark dates with events
        events: calendar.getEvents(),
    });

    miniCalendar.render();

    // ============================================
    // VIEW SWITCHER
    // ============================================

    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const viewType = this.dataset.view;
            calendar.changeView(viewType);

            // Update active state
            document.querySelectorAll('.view-btn').forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            this.classList.add('active');
            this.setAttribute('aria-pressed', 'true');
        });
    });

    // ============================================
    // FILTERS
    // ============================================

    function applyFilters() {
        const projectChecked = document.querySelector('[data-filter="project"]').checked;
        const activityChecked = document.querySelector('[data-filter="activity"]').checked;
        const taskChecked = document.querySelector('[data-filter="task"]').checked;
        const showCompleted = document.querySelector('[data-filter="completed"]').checked;

        calendar.getEvents().forEach(event => {
            const workType = event.extendedProps.workType || '';
            const status = event.extendedProps.status || '';
            let show = true;

            // Type filter
            if (workType.includes('project')) {
                show = show && projectChecked;
            } else if (workType.includes('activity')) {
                show = show && activityChecked;
            } else if (workType.includes('task')) {
                show = show && taskChecked;
            }

            // Completed filter
            if (!showCompleted && status === 'completed') {
                show = false;
            }

            event.setProp('display', show ? 'auto' : 'none');
        });
    }

    document.querySelectorAll('[data-filter]').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });

    // ============================================
    // DETAIL PANEL
    // ============================================

    function showDetailPanel(event) {
        const modalUrl = event.url;
        if (!modalUrl) return;

        // Show panel with loading state
        detailPanel.classList.remove('hidden');
        detailPanel.classList.add('visible');
        detailContent.innerHTML = '<div class="text-center py-10"><i class="fas fa-spinner fa-spin text-3xl text-gray-400"></i></div>';

        // Load content via AJAX
        fetch(modalUrl, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.text())
        .then(html => {
            detailContent.innerHTML = html;

            // Initialize HTMX on loaded content
            if (window.htmx) {
                htmx.process(detailContent);
            }
        })
        .catch(error => {
            console.error(error);
            detailContent.innerHTML = '<div class="text-center py-10 text-red-600"><i class="fas fa-exclamation-circle text-3xl"></i><p class="mt-4">Failed to load</p></div>';
        });
    }

    function closeDetailPanel() {
        detailPanel.classList.remove('visible');
        setTimeout(() => {
            detailPanel.classList.add('hidden');
            detailContent.innerHTML = '';
        }, 300); // Wait for slide animation
    }

    // Close panel button
    document.getElementById('closePanel').addEventListener('click', closeDetailPanel);

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && detailPanel.classList.contains('visible')) {
            closeDetailPanel();
        }
    });

    // ============================================
    // TODAY BUTTON
    // ============================================

    document.getElementById('todayBtn').addEventListener('click', function() {
        calendar.today();
        miniCalendar.today();
    });

    // ============================================
    // HTMX EVENT LISTENERS
    // ============================================

    // Refresh calendar after work item deleted
    document.body.addEventListener('workItemDeleted', function(event) {
        const workItemId = String(event.detail.id);
        const calendarEvent = calendar.getEventById('work-item-' + workItemId);

        if (calendarEvent) {
            calendarEvent.remove();
        } else {
            calendar.refetchEvents();
        }

        closeDetailPanel();
    });

    document.body.addEventListener('refreshCalendar', function() {
        calendar.refetchEvents();
        miniCalendar.refetchEvents();
    });

})();
```

---

## Integration with Existing Calendars

### Quick Action Buttons

**Add to Calendar #1** (`oobc_calendar.html`):
```html
<!-- In hero section, after "List View" button -->
<a href="{% url 'common:oobc_calendar_advanced' %}"
   class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-600 text-white font-semibold shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
    <i class="fas fa-calendar-alt"></i>
    <span>Advanced View</span>
</a>
```

**Add to Calendar #2** (`coordination/calendar.html`):
```html
<!-- In header action buttons -->
<a href="{% url 'common:oobc_calendar_advanced' %}"
   class="inline-flex items-center justify-center px-4 py-2 text-sm font-semibold text-white rounded-lg shadow bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700">
    <i class="fas fa-calendar-alt mr-2"></i>
    Advanced Calendar
</a>
```

**Add to Calendar #3 (Modern View)** (`calendar_modern.html`):
```html
<!-- In header action buttons, after "Today" button -->
<a href="{% url 'common:oobc_calendar_advanced' %}"
   class="border-2 border-purple-500 text-purple-600 px-5 py-2.5 rounded-xl font-semibold hover:bg-purple-50 transition-colors duration-200">
    <i class="fas fa-rocket mr-2"></i>
    <span class="hidden sm:inline">Advanced</span>
</a>
```

---

## Differences from Existing Calendars

### Calendar #1 (Main OOBC Calendar) vs Advanced

| Feature | Main OOBC Calendar | Advanced Calendar |
|---------|-------------------|-------------------|
| **Layout** | Full-page calendar with top filters | 3-column: Sidebar, Calendar, Detail Panel |
| **Detail View** | Modal (overlay) | Right-side panel (slides in) |
| **Mini Calendar** | None | Yes (left sidebar) |
| **Legend** | None | Yes (color-coded) |
| **Sidebar Color** | N/A | Light gray/blue gradient |
| **View Toggles** | FullCalendar toolbar | Separate UI buttons (top) |
| **Filters** | Top bar (horizontal) | Left sidebar (vertical) |

### Calendar #2 (Coordination) vs Advanced

| Feature | Coordination Calendar | Advanced Calendar |
|---------|----------------------|-------------------|
| **Data Source** | Coordination events only | All work items (unified) |
| **Sidebar** | Right sidebar (stats) | Left sidebar (filters) + Right panel (details) |
| **Quick Actions** | New Event, Log Activity | Create Work Item, Today |
| **Focus** | Coordination-specific | Enterprise-wide |

### Calendar #3 (Modern View) vs Advanced

| Feature | Modern View | Advanced Calendar |
|---------|------------|-------------------|
| **Detail View** | Modal | Right-side panel |
| **Legend** | None | Yes (event types) |
| **Mini Calendar** | Basic | Interactive (date navigation) |
| **UI Polish** | Good | Google Calendar-inspired |
| **Animations** | Standard | Smooth slide-ins, transitions |

---

## Implementation Plan

### Phase 1: Core Structure | PRIORITY: CRITICAL
**Prerequisites:** None
**Dependencies:** None

1. Create new template `calendar_advanced.html`
2. Create new view function `oobc_calendar_advanced(request)`
3. Add URL route `/oobc-management/calendar/advanced/`
4. Create CSS file `calendar-advanced.css`
5. Create JavaScript file `calendar-advanced.js`

### Phase 2: Left Sidebar | PRIORITY: HIGH
**Prerequisites:** Phase 1 complete
**Dependencies:** FullCalendar library

1. Implement mini calendar with FullCalendar
2. Add filter checkboxes (Projects, Activities, Tasks, Completed)
3. Create event type legend with color indicators
4. Style with light gray/blue gradient background

### Phase 3: Main Calendar Area | PRIORITY: CRITICAL
**Prerequisites:** Phase 1 complete
**Dependencies:** Work item feed endpoint

1. Initialize FullCalendar with unified work item feed
2. Implement view switcher (Month/Week/Day/Year)
3. Add "Today" button functionality
4. Configure event rendering and styling

### Phase 4: Right Detail Panel | PRIORITY: HIGH
**Prerequisites:** Phase 3 complete
**Dependencies:** Work item modal partial

1. Create sliding panel component (CSS transitions)
2. Implement event click handler to show panel
3. Load work item details via AJAX
4. Add close button and Escape key handler
5. Initialize HTMX on dynamically loaded content

### Phase 5: Integration | PRIORITY: MEDIUM
**Prerequisites:** All phases complete
**Dependencies:** None

1. Add "Advanced View" button to Calendar #1
2. Add "Advanced Calendar" button to Calendar #2
3. Add "Advanced" button to Calendar #3 (Modern View)
4. Test navigation between all calendar views

### Phase 6: Polish & Testing | PRIORITY: MEDIUM
**Prerequisites:** Phase 5 complete
**Dependencies:** None

1. Test responsive design (mobile, tablet, desktop)
2. Verify accessibility (WCAG 2.1 AA)
3. Add keyboard shortcuts (optional)
4. Performance testing (event loading, filtering)
5. Cross-browser testing

---

## Trade-off Analysis

### Pros

1. **Industry-Standard UI**: Google Calendar is familiar to all users
2. **Enhanced Productivity**: Mini calendar, filters, and detail panel improve efficiency
3. **Professional Appearance**: Suitable for government/enterprise deployment
4. **Experimentation-Friendly**: Test advanced features without disrupting existing calendars
5. **Future-Proof**: Can replace older calendars if users prefer Advanced view

### Cons

1. **Maintenance Burden**: Four calendars to maintain (Main, Coordination, Modern, Advanced)
2. **Code Duplication**: Similar FullCalendar setup across multiple templates
3. **User Confusion**: Multiple calendar views may confuse some users
4. **Performance**: Additional JavaScript/CSS for sliding panels

### Alternatives Considered

#### Alternative 1: Enhance Modern View Instead
**Pros:** No new calendar, single maintenance point
**Cons:** Risk breaking existing Modern View users
**Decision:** Create separate Advanced view for experimentation first

#### Alternative 2: Replace Main OOBC Calendar
**Pros:** Reduce calendar count to 3
**Cons:** Disruptive to users, no A/B testing
**Decision:** Keep Main calendar, offer Advanced as option

#### Alternative 3: Single Unified Calendar with Presets
**Pros:** One calendar with multiple "modes"
**Cons:** Complex view switching logic, harder to maintain
**Decision:** Separate calendars are clearer architecturally

---

## Migration Strategy

### Step 1: Deploy Advanced Calendar (Parallel)
- Deploy Advanced calendar alongside existing calendars
- Add "Advanced View" buttons to all calendars
- Monitor user adoption via analytics

### Step 2: Gather User Feedback (4-8 weeks)
- Survey users: Main vs Modern vs Advanced preferences
- Track usage metrics (which calendar is most used?)
- Identify pain points and missing features

### Step 3: Consolidation (Future)
Based on feedback:
- **Option A**: Keep all calendars (users have choice)
- **Option B**: Deprecate least-used calendar
- **Option C**: Merge features into single "Ultimate" calendar

---

## Testing Strategy

### Unit Tests
```python
# tests/test_calendar_advanced.py

def test_oobc_calendar_advanced_view():
    """Test advanced calendar view renders correctly."""
    response = client.get('/oobc-management/calendar/advanced/')
    assert response.status_code == 200
    assert b'Advanced Calendar' in response.content

def test_calendar_advanced_uses_unified_feed():
    """Test advanced calendar uses work items feed."""
    response = client.get('/oobc-management/calendar/advanced/')
    assert b'work-items/feed' in response.content
```

### Integration Tests
1. **View Switching**: Verify Month → Week → Day → Year transitions
2. **Filters**: Verify Projects/Activities/Tasks toggle correctly
3. **Detail Panel**: Verify event click shows panel, Escape closes panel
4. **Mini Calendar**: Verify date click navigates main calendar

### Accessibility Tests
1. **Keyboard Navigation**: Tab through all interactive elements
2. **Screen Reader**: ARIA labels on buttons, panels
3. **Focus Indicators**: Visible focus states on all controls
4. **Color Contrast**: 4.5:1 minimum for all text

### Performance Tests
1. **Event Loading**: < 500ms to load 100 work items
2. **Filter Application**: < 100ms to toggle filters
3. **Panel Animation**: 300ms slide-in transition
4. **Responsive**: Test on mobile (< 768px), tablet (768-1024px), desktop (> 1024px)

---

## Documentation Needs

### Developer Documentation
1. **Architecture Guide**: This document
2. **Template Documentation**: Explain 3-column layout
3. **JavaScript API**: Calendar methods, panel controls

### User Documentation
1. **User Guide**: How to use Advanced Calendar
2. **Comparison Guide**: Main vs Modern vs Advanced calendars
3. **FAQ**: When to use which calendar?

### Admin Documentation
1. **Deployment Guide**: How to enable Advanced Calendar
2. **Monitoring Guide**: Analytics, error tracking
3. **Maintenance Guide**: Update FullCalendar, fix common issues

---

## Success Metrics

### User Engagement
- **Target**: 30% of users try Advanced Calendar within first month
- **Measure**: Page views, unique users

### User Satisfaction
- **Target**: 4.0+ / 5.0 user rating
- **Measure**: In-app feedback survey

### Performance
- **Target**: < 500ms event loading, < 100ms filter application
- **Measure**: Browser performance API, server logs

### Adoption
- **Target**: 20% of users prefer Advanced over Main/Modern
- **Measure**: Usage frequency, session duration

---

## Appendix: File Checklist

### New Files to Create
- [ ] `src/templates/common/calendar_advanced.html` (Template)
- [ ] `src/static/common/css/calendar-advanced.css` (Styles)
- [ ] `src/static/common/js/calendar-advanced.js` (JavaScript)

### Files to Modify
- [ ] `src/common/views/management.py` (Add `oobc_calendar_advanced` view)
- [ ] `src/common/views/__init__.py` (Export `oobc_calendar_advanced`)
- [ ] `src/common/urls.py` (Add URL route)
- [ ] `src/templates/common/oobc_calendar.html` (Add "Advanced View" button)
- [ ] `src/templates/coordination/calendar.html` (Add "Advanced Calendar" button)
- [ ] `src/templates/common/calendar_modern.html` (Add "Advanced" button)

### Testing Files
- [ ] `tests/test_calendar_advanced.py` (Unit + integration tests)

---

**End of Architecture Document**
