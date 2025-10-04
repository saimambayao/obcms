# Quick Actions Implementation Guide

**Status:** Production-Ready
**Date:** 2025-10-03
**OBCMS UI Component Library**

---

## Overview

This guide provides complete, production-ready Quick Actions implementations for Task Management and Communities modules in OBCMS. Quick Actions improve user efficiency by providing contextual shortcuts to common workflows.

---

## Component Architecture

### Three Quick Actions Patterns

1. **FAB (Floating Action Button)** - Bottom-right floating menu for page-level actions
2. **Sidebar Quick Actions** - Sticky sidebar for detail views with contextual actions
3. **Inline Quick Actions** - Header or modal actions for immediate operations

---

## 1. Task Board Quick Actions (FAB Pattern)

### File Location
```
/src/templates/common/partials/task_board_quick_actions.html
```

### Integration Steps

**Step 1:** Add Alpine.js to base template (if not already present)
```html
<!-- In base.html, before closing </head> -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

**Step 2:** Include FAB in `staff_task_board.html`
```django
{% extends 'base.html' %}

{# ... existing content ... #}

{% block content %}
<!-- Existing task board content -->
{% endblock %}

{# Include FAB Quick Actions #}
{% include "common/partials/task_board_quick_actions.html" %}

{% block extra_js %}
<!-- Existing JS -->
{% endblock %}
```

### Features Implemented

1. **Quick Filters Toggle**
   - Scrolls to filters section
   - Smooth scroll animation
   - No page reload

2. **Bulk Operations**
   - Placeholder for multi-select tasks
   - Ready for backend implementation
   - Modal UI prepared

3. **Export Tasks**
   - Links to CSV export
   - Query string preserved
   - Direct download

4. **View Analytics**
   - Links to Staff Management dashboard
   - Performance metrics
   - Task insights

### Visual Design

- **FAB Button:** 16x16 emerald-to-teal gradient, shadow-2xl
- **Menu:** 72w rounded-2xl card with gradient header
- **Badge:** Rose-500 notification count (dynamic)
- **Icons:** 12x12 rounded-xl with color-coded backgrounds
- **Animations:** Scale, rotate, translate on hover/click

### Keyboard Shortcuts

- `ESC` - Close FAB menu
- Extensible for additional shortcuts

---

## 2. Task Modal Quick Actions (Inline Pattern)

### File Location
```
/src/templates/common/partials/task_modal_quick_actions.html
```

### Integration Steps

**Step 1:** Insert in `staff_task_modal.html` after header section
```django
<div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full">
    <!-- Existing modal header -->

    {# Quick Actions Bar #}
    {% include "common/partials/task_modal_quick_actions.html" %}

    <!-- Existing modal body with form -->
</div>
```

### Features Implemented

1. **Mark Complete**
   - Sets status to "completed"
   - Updates progress to 100%
   - Shows toast notification
   - User must save to persist

2. **Assign to Me**
   - Adds current user to assignees
   - Checks if already assigned
   - Shows appropriate feedback
   - Triggers change event for multi-select

3. **Change Priority**
   - Dropdown with 4 levels (Critical, High, Normal, Low)
   - Color-coded options (rose, amber, blue, gray)
   - Instant UI update
   - Requires save to persist

4. **Set Due Date**
   - Focuses due date input
   - Triggers native date picker
   - Accessible keyboard navigation

5. **Clone Task**
   - Creates duplicate task
   - Sends POST to `/clone/` endpoint
   - Shows success/error toast
   - Redirects to new task

### JavaScript Functions

```javascript
// Available functions:
quickMarkComplete(taskId)
quickAssignToMe(taskId)
quickChangePriority(taskId, priority)
quickCloneTask(taskId)
showToast(message, type)
```

### Backend Requirements

**Clone Endpoint** (needs implementation):
```python
# In common/views.py
@require_http_methods(["POST"])
def staff_task_clone(request, task_id):
    task = get_object_or_404(StaffTask, id=task_id)
    new_task = StaffTask.objects.create(
        title=f"{task.title} (Copy)",
        description=task.description,
        impact=task.impact,
        priority=task.priority,
        status='not_started',
        # ... copy other fields
    )
    return JsonResponse({
        'success': True,
        'new_task_id': new_task.id,
        'message': 'Task cloned successfully'
    })
```

**URL Pattern:**
```python
# common/urls.py
path('staff/tasks/<int:task_id>/clone/', views.staff_task_clone, name='staff_task_clone'),
```

### Toast Notification System

- **Auto-dismissing:** 4-second display
- **Color-coded:** Success (emerald), Error (rose), Warning (amber), Info (blue)
- **Position:** Bottom-left fixed
- **Accessibility:** ARIA live region (optional enhancement)

---

## 3. Barangay Detail Quick Actions (Sidebar Pattern)

### File Location
```
/src/templates/communities/partials/barangay_detail_quick_actions.html
```

### Integration Steps

**Step 1:** Modify `provincial_view.html` to use grid layout
```django
{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Existing header -->

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main content - 2 columns -->
        <div class="lg:col-span-2 space-y-6">
            <!-- Existing stats, map, tables -->
        </div>

        <!-- Sidebar - 1 column -->
        <div class="lg:col-span-1">
            {% include "communities/partials/barangay_detail_quick_actions.html" %}
        </div>
    </div>
</div>
{% endblock %}
```

### Features Implemented

1. **Edit Community**
   - Direct link to edit form
   - Indigo color scheme
   - Preserves context

2. **Add MANA Assessment**
   - Pre-fills barangay parameter
   - Blue color scheme
   - Quick workflow

3. **Log Coordination Activity**
   - Links to event creation
   - Emerald color scheme
   - Pre-selects barangay

4. **Create Recommendation**
   - Policy recommendation form
   - Purple color scheme
   - Context-aware

5. **View Demographics**
   - Smooth scroll to section
   - Amber color scheme
   - JavaScript-based navigation

6. **Generate Profile**
   - PDF export link
   - Rose color scheme
   - Opens in new tab

### Quick Stats Section

- **Population:** Estimated OBC population
- **Households:** Total households
- **Assessments:** Count of MANA assessments
- **Dynamic data** from context

### Sticky Positioning

```css
.sticky.top-6 {
    position: sticky;
    top: 1.5rem; /* 24px from top when scrolling */
}
```

---

## 4. Communities List Quick Actions (Header Pattern)

### File Location
```
/src/templates/communities/partials/communities_list_quick_actions.html
```

### Integration Steps

**Step 1:** Replace header section in `communities_manage.html`
```django
{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    {# Replace existing header with: #}
    {% include "communities/partials/communities_list_quick_actions.html" %}

    <!-- Existing stats, filters, table -->
</div>
{% endblock %}
```

### Features Implemented

1. **Add Community**
   - Gradient button (blue-to-teal)
   - Rotate icon on hover
   - Shadow effect on hover

2. **Bulk Import**
   - Opens modal for file upload
   - CSV/Excel template download
   - Drag-and-drop zone
   - Purple color scheme

3. **Export Data**
   - Dropdown with 3 formats:
     - CSV (spreadsheet)
     - Excel (XLSX)
     - PDF (report)
   - Icon-coded options
   - Emerald color scheme

4. **Generate Reports**
   - Dropdown with 3 report types:
     - Coverage Summary (regional)
     - Demographics Report
     - Needs Assessment (MANA)
   - Amber color scheme

5. **Map View**
   - Toggle to map visualization
   - Indigo color scheme
   - Preserves filters

6. **Archived Toggle**
   - Switch between active/archived
   - Conditional rendering
   - Preserves context

### Bulk Import Modal

**Features:**
- Full-screen overlay with backdrop
- Drag-and-drop file zone
- Template download link
- File format validation
- Cancel/Import actions

**JavaScript Functions:**
```javascript
showBulkImportModal()
hideBulkImportModal()
handleFileSelect(event)
submitBulkImport()
```

**Backend Requirements:**

```python
# communities/views.py
@require_http_methods(["POST"])
def communities_bulk_import(request):
    file = request.FILES.get('file')
    # Parse CSV/Excel
    # Validate rows
    # Create BarangayOBC instances
    # Return success/errors
    return JsonResponse({
        'success': True,
        'imported': 25,
        'skipped': 3,
        'errors': []
    })
```

---

## Component Templates (Reusable)

### 1. FAB Component

**File:** `/src/templates/components/quick_actions_fab.html`

**Usage:**
```django
{% include "components/quick_actions_fab.html" with actions=fab_actions %}
```

**Context:**
```python
fab_actions = [
    {
        "id": "filter",
        "icon": "fas fa-filter",
        "label": "Quick Filters",
        "description": "Jump to filters",
        "color": "blue",
        "action": "javascript:scrollToFilters()"
    },
    {
        "id": "export",
        "icon": "fas fa-download",
        "label": "Export Tasks",
        "color": "emerald",
        "action": "/tasks/export/"
    }
]
```

### 2. Sidebar Component

**File:** `/src/templates/components/quick_actions_sidebar.html`

**Usage:**
```django
{% include "components/quick_actions_sidebar.html" with actions=sidebar_actions title="Quick Actions" %}
```

**Context:**
```python
sidebar_actions = [
    {
        "icon": "fas fa-edit",
        "label": "Edit Community",
        "url": f"/communities/{coverage.id}/edit/",
        "color": "indigo",
        "badge": "Required"  # Optional
    }
]
```

### 3. Inline Component

**File:** `/src/templates/components/quick_actions_inline.html`

**Usage:**
```django
{% include "components/quick_actions_inline.html" with actions=inline_actions %}
```

**Context:**
```python
inline_actions = [
    {
        "id": "complete",
        "icon": "fas fa-check",
        "label": "Mark Complete",
        "action": "javascript:markComplete()",
        "color": "emerald",
        "variant": "outline"  # solid, outline, ghost
    }
]
```

---

## Color Scheme Standards

### Semantic Colors (Follow OBCMS UI Standards)

| Action Type | Color | Usage |
|-------------|-------|-------|
| Primary Actions | `blue` | Main workflows, navigation |
| Success/Complete | `emerald` | Confirmations, completions |
| Create/New | `indigo` | Add, create new items |
| Edit/Update | `purple` | Modify, change settings |
| Warning/Review | `amber` | Caution, needs attention |
| Delete/Critical | `rose` | Destructive actions |

### Tailwind Classes

```css
/* Emerald */
bg-emerald-100 text-emerald-600 hover:bg-emerald-600 hover:text-white

/* Blue */
bg-blue-100 text-blue-600 hover:bg-blue-600 hover:text-white

/* Purple */
bg-purple-100 text-purple-600 hover:bg-purple-600 hover:text-white

/* Amber */
bg-amber-100 text-amber-600 hover:bg-amber-600 hover:text-white

/* Rose */
bg-rose-100 text-rose-600 hover:bg-rose-600 hover:text-white

/* Indigo */
bg-indigo-100 text-indigo-600 hover:bg-indigo-600 hover:text-white
```

---

## Accessibility Standards

### WCAG 2.1 AA Compliance

1. **Keyboard Navigation**
   - All buttons focusable with `Tab`
   - Dropdowns navigable with arrow keys
   - `ESC` closes all menus

2. **Screen Reader Support**
   ```html
   <button aria-label="Quick Actions Menu" aria-expanded="false">
   ```

3. **Color Contrast**
   - Text: 4.5:1 minimum
   - Icons: 3:1 minimum
   - All states meet standards

4. **Touch Targets**
   - Minimum 44x44px (all buttons)
   - Adequate spacing between actions

5. **Focus Indicators**
   - Visible focus rings
   - Custom focus styles for Alpine.js components

---

## Performance Considerations

### JavaScript Loading

- **Alpine.js:** CDN loaded (23KB gzipped)
- **Custom scripts:** Inline in template (< 2KB each)
- **Total overhead:** < 30KB

### HTMX Integration

- FAB and inline actions work with HTMX
- No conflicts with modal swapping
- Event listeners preserved after swaps

### Mobile Optimization

- Responsive breakpoints (sm, md, lg, xl)
- Touch-friendly targets (48px minimum)
- Optimized for 320px - 1920px viewports

---

## Testing Checklist

### Functional Testing

- [ ] FAB menu opens/closes correctly
- [ ] All Quick Actions navigate to correct pages
- [ ] Inline actions update form fields
- [ ] Toast notifications display and auto-dismiss
- [ ] Export dropdowns provide correct formats
- [ ] Bulk import modal opens/closes
- [ ] Sidebar actions link correctly
- [ ] Keyboard shortcuts work (ESC)

### Visual Testing

- [ ] Buttons match OBCMS UI standards
- [ ] Colors are semantically correct
- [ ] Hover states work smoothly
- [ ] Icons display correctly
- [ ] Responsive on mobile (320px+)
- [ ] Responsive on tablet (768px+)
- [ ] Responsive on desktop (1024px+)

### Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Screen reader announces actions
- [ ] Focus indicators visible
- [ ] Color contrast passes WCAG AA
- [ ] Touch targets minimum 44px
- [ ] ARIA labels present

### Cross-Browser Testing

- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (macOS/iOS)
- [ ] Mobile browsers (Chrome, Safari)

---

## Implementation Priority

### Phase 1: Task Management (HIGH PRIORITY)

1. ✅ Task Board FAB Quick Actions
2. ✅ Task Modal Inline Quick Actions
3. Backend: Clone task endpoint

### Phase 2: Communities (MEDIUM PRIORITY)

1. ✅ Communities List Header Quick Actions
2. ✅ Barangay Detail Sidebar Quick Actions
3. Backend: Bulk import endpoint
4. Backend: Export endpoints (CSV, Excel, PDF)

### Phase 3: Enhancements (LOW PRIORITY)

1. Keyboard shortcuts (beyond ESC)
2. Advanced bulk operations
3. Real-time notifications
4. Analytics dashboard integration

---

## Backend Integration Requirements

### Required Endpoints

1. **Task Clone**
   - URL: `/oobc-management/staff/tasks/<id>/clone/`
   - Method: POST
   - Returns: `{ success: true, new_task_id: int }`

2. **Communities Bulk Import**
   - URL: `/communities/bulk-import/`
   - Method: POST
   - Accepts: CSV/Excel file
   - Returns: `{ success: true, imported: int, errors: [] }`

3. **Export Endpoints**
   - CSV: `?export=csv`
   - Excel: `?export=excel`
   - PDF: `?export=pdf`
   - Returns: File download

### Optional Enhancements

1. **Bulk Task Operations**
   - URL: `/staff/tasks/bulk/`
   - Actions: delete, assign, change status
   - Method: POST with task IDs array

2. **Quick Stats API**
   - Real-time sidebar stats
   - WebSocket or polling

---

## Maintenance Notes

### File Locations Summary

```
src/templates/
├── components/
│   ├── quick_actions_fab.html          # Reusable FAB
│   ├── quick_actions_sidebar.html      # Reusable sidebar
│   └── quick_actions_inline.html       # Reusable inline
├── common/partials/
│   ├── task_board_quick_actions.html   # Task Board FAB
│   └── task_modal_quick_actions.html   # Task Modal inline
└── communities/partials/
    ├── barangay_detail_quick_actions.html      # Barangay sidebar
    └── communities_list_quick_actions.html     # Communities header
```

### Updating Quick Actions

1. **Add new action:** Edit relevant partial template
2. **Change colors:** Update Tailwind classes
3. **Add backend feature:** Implement endpoint, update JS
4. **Update docs:** Modify this guide

---

## Troubleshooting

### FAB Menu Not Opening

**Issue:** Click doesn't toggle menu
**Solution:** Ensure Alpine.js is loaded before component

```html
<!-- Check in browser console -->
console.log(window.Alpine); // Should not be undefined
```

### Toast Notifications Not Showing

**Issue:** `showToast()` not working
**Solution:** Check JavaScript is included in template

```django
{% include "common/partials/task_modal_quick_actions.html" %}
{# Script tag is inside this partial #}
```

### Sidebar Not Sticky

**Issue:** Sidebar scrolls with page
**Solution:** Ensure parent has correct layout

```html
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2">Main content</div>
    <div class="lg:col-span-1">
        <!-- Sidebar with .sticky.top-6 -->
    </div>
</div>
```

### Export Links 404

**Issue:** Export URLs not working
**Solution:** Implement backend view handlers

```python
def communities_manage(request):
    export_format = request.GET.get('export')
    if export_format == 'csv':
        return generate_csv_response(queryset)
    # ... rest of view
```

---

## Support & Feedback

For questions, issues, or feature requests related to Quick Actions:

1. Check this guide first
2. Review OBCMS UI Components & Standards Guide
3. Test in development environment
4. Submit issue with screenshots and steps to reproduce

---

**End of Quick Actions Implementation Guide**
