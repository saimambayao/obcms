# Template and URL Updates for WorkItem System

**Status:** ✅ COMPLETE
**Date:** 2025-10-05
**Author:** Claude Code
**Purpose:** Document all template and URL updates to transition from legacy models (StaffTask, ProjectWorkflow, Event) to the unified WorkItem system.

---

## Executive Summary

This document tracks the systematic migration from legacy task management models to the unified WorkItem hierarchy system. The migration maintains backward compatibility through URL redirects while updating all frontend references to use the new WorkItem endpoints.

### Migration Scope

- **Legacy Models:** StaffTask, ProjectWorkflow, CoordinationEvent
- **New Model:** WorkItem (unified hierarchy)
- **Impact:** 26 templates referencing StaffTask, 9 referencing ProjectWorkflow, 27 referencing Events
- **Approach:** Gradual migration with backward compatibility

---

## Part 1: URL Pattern Updates

### 1.1 WorkItem URL Patterns (ENABLED)

**File:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/urls.py`

**Status:** ✅ Uncommented and activated

#### Activated URL Patterns:

```python
# WorkItem CRUD URLs (Phase 3: Unified Work Hierarchy)
path(
    "oobc-management/work-items/",
    views.work_item_list,
    name="work_item_list",
),
path(
    "oobc-management/work-items/create/",
    views.work_item_create,
    name="work_item_create",
),
path(
    "oobc-management/work-items/<uuid:pk>/",
    views.work_item_detail,
    name="work_item_detail",
),
path(
    "oobc-management/work-items/<uuid:pk>/edit/",
    views.work_item_edit,
    name="work_item_edit",
),
path(
    "oobc-management/work-items/<uuid:pk>/delete/",
    views.work_item_delete,
    name="work_item_delete",
),
path(
    "oobc-management/work-items/<uuid:pk>/tree/",
    views.work_item_tree_partial,
    name="work_item_tree_partial",
),
path(
    "oobc-management/work-items/<uuid:pk>/update-progress/",
    views.work_item_update_progress,
    name="work_item_update_progress",
),
path(
    "oobc-management/work-items/calendar/feed/",
    views.work_item_calendar_feed,
    name="work_item_calendar_feed",
),
```

**View Verification:** ✅ All views confirmed to exist in `src/common/views/work_items.py`

---

### 1.2 Legacy URL Redirects (Backward Compatibility)

**File:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/urls.py`

**Purpose:** Ensure old bookmarks and links don't break during transition

#### Added Redirects:

```python
# Legacy URL Redirects (Backward Compatibility)
# Redirect old StaffTask URLs to WorkItem endpoints
path(
    "oobc-management/staff/tasks/<int:task_id>/",
    RedirectView.as_view(pattern_name="common:work_item_list", permanent=False),
    name="stafftask_detail_redirect",
),
path(
    "oobc-management/staff/tasks/<int:task_id>/edit/",
    RedirectView.as_view(pattern_name="common:work_item_list", permanent=False),
    name="stafftask_edit_redirect",
),
# Note: Individual task redirects require WorkItem UUID lookup
# Users will be redirected to the work items list instead
```

**Redirect Strategy:**

- **Permanent:** `permanent=False` (302 redirect) allows future changes
- **Target:** All legacy task URLs redirect to `work_item_list` (users can find their items there)
- **Limitation:** Integer task IDs can't be directly mapped to UUID WorkItem IDs without database lookup

**Future Enhancement:**
Create a redirect view that:
1. Accepts old StaffTask integer ID
2. Looks up corresponding WorkItem UUID
3. Redirects to specific WorkItem detail page

```python
# Example future implementation
def legacy_task_redirect(request, task_id):
    """Redirect old StaffTask ID to WorkItem UUID"""
    try:
        # Look up StaffTask and find corresponding WorkItem
        staff_task = StaffTask.objects.get(id=task_id)
        work_item = WorkItem.objects.get(
            legacy_task_id=staff_task.id,
            item_type='task'
        )
        return redirect('common:work_item_detail', pk=work_item.id)
    except (StaffTask.DoesNotExist, WorkItem.DoesNotExist):
        messages.warning(request, f"Task #{task_id} not found. Showing all work items.")
        return redirect('common:work_item_list')
```

---

## Part 2: Template Updates

### 2.1 OOBC Management Home Template

**File:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/templates/common/oobc_management_home.html`

**Status:** ✅ Updated

#### Changes Made:

**1. Hero Section Quick Actions (Lines 70-73)**

**Before:**
```html
<a href="{% url 'common:staff_task_create' %}" class="...">
    <i class="fas fa-plus-square"></i>
    <span>Create Task</span>
</a>
```

**After:**
```html
<a href="{% url 'common:work_item_create' %}" class="...">
    <i class="fas fa-plus-square"></i>
    <span>Create Work Item</span>
</a>
```

**2. Recent Updates Section (Lines 101-104)**

**Before:**
```html
<a href="{% url 'common:staff_task_board' %}" class="inline-flex items-center gap-2 text-sky-600 hover:text-sky-700">
    <i class="fas fa-tasks"></i>
    Manage Staff Tasks
</a>
```

**After:**
```html
<a href="{% url 'common:work_item_list' %}" class="inline-flex items-center gap-2 text-sky-600 hover:text-sky-700">
    <i class="fas fa-tasks"></i>
    Manage Work Items
</a>
```

**Impact:**
- Users clicking "Create Work Item" now go to unified WorkItem form
- "Manage Work Items" shows unified list view (tasks, activities, projects)
- Recent feed still shows legacy models (future: update to show WorkItems)

**Note:** Recent feeds currently still display legacy StaffTask, Event, and PPA data. Future update will switch to WorkItem queryset.

---

### 2.2 Navigation Template (Navbar)

**File:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/templates/common/navbar.html`

**Status:** ✅ Updated

#### Changes Made:

**Added "Work Items" Menu Entry (Lines 240-246)**

**New Menu Item:**
```html
<a href="{% url 'common:work_item_list' %}" class="flex items-start space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors duration-150" role="menuitem">
    <i class="fas fa-tasks text-emerald-500 mt-1"></i>
    <span>
        <span class="block font-semibold text-gray-900">Work Items</span>
        <span class="block text-xs text-gray-500">Unified task, activity, and project management system.</span>
    </span>
</a>
```

**Menu Structure:**
```
OOBC Management
├── Staff Management
├── Work Items ← NEW
├── Planning & Budgeting
├── Calendar Management
├── Project Central
└── User Approvals (admin only)
```

**Design Rationale:**
- Positioned after "Staff Management" (related functionality)
- Before "Planning & Budgeting" (workflow sequence)
- Uses emerald-500 icon color (matches task semantics)
- Clear description emphasizes unified nature

---

### 2.3 Calendar Templates

**Status:** ⚠️ PENDING REVIEW

**Files Requiring Update:**

1. `/src/templates/common/oobc_calendar.html` - Main calendar view
2. `/src/templates/coordination/calendar.html` - Coordination calendar
3. `/src/templates/project_central/project_calendar.html` - Project calendar
4. `/src/templates/components/calendar_full.html` - Reusable calendar component

**Current State:**
- Calendar feed already uses `work_items_calendar_feed` (✅ Updated)
- Modal still uses legacy `staff_task_modal` for task clicks
- Event modals use `coordination_event_modal`

**Required Changes:**

```javascript
// OLD: src/templates/common/oobc_calendar.html
eventClick: function(info) {
    var eventType = info.event.extendedProps.eventType;
    if (eventType === 'task') {
        // OLD: Load StaffTask modal
        fetch(`/oobc-management/staff/tasks/${taskId}/modal/`)
    }
}

// NEW: Use unified WorkItem modal
eventClick: function(info) {
    var workItemId = info.event.extendedProps.workItemId;
    if (workItemId) {
        // NEW: Load WorkItem modal
        fetch(`/oobc-management/work-items/${workItemId}/modal/`)
    }
}
```

**Migration Strategy:**
1. Update calendar feed to include `work_item_id` in event data
2. Update `eventClick` handler to use WorkItem modal endpoint
3. Maintain legacy event modal for CoordinationEvent (for now)
4. Test all calendar interactions (click, drag, edit)

---

### 2.4 Dashboard Templates

**Status:** ⚠️ PENDING REVIEW

**Files Containing Legacy References:**

**Staff Task Board Templates:**
- `/src/templates/common/staff_task_board.html` - Main kanban board
- `/src/templates/common/partials/staff_task_board_board.html` - Board view
- `/src/templates/common/partials/staff_task_table_wrapper.html` - Table view
- `/src/templates/common/partials/staff_task_modal.html` - Task detail modal
- `/src/templates/common/partials/staff_task_create_modal.html` - Create modal

**Task Analytics Templates:**
- `/src/templates/common/tasks/enhanced_dashboard.html`
- `/src/templates/common/tasks/analytics.html`
- `/src/templates/common/tasks/domain_tasks.html`
- `/src/templates/common/tasks/assessment_tasks.html`
- `/src/templates/common/tasks/event_tasks.html`
- `/src/templates/common/tasks/policy_tasks.html`

**Project Central Templates:**
- `/src/templates/project_central/workflow_detail.html`
- `/src/templates/project_central/workflow_form.html`
- `/src/templates/project_central/project_list.html`

**Coordination Templates:**
- `/src/templates/coordination/partials/event_modal.html`
- `/src/templates/coordination/event_form.html`
- `/src/templates/coordination/coordination_events.html`

**Migration Priority:**

1. **HIGH PRIORITY:**
   - Staff task board (main UI for task management)
   - Task modals (used throughout system)
   - Calendar modals (clicked frequently)

2. **MEDIUM PRIORITY:**
   - Task analytics dashboards (used by managers)
   - Project workflow forms (active development)

3. **LOW PRIORITY:**
   - Backup templates (OOBC_calendar_BACKUP_20251005.html)
   - Deprecated views

---

## Part 3: URL Mapping Reference

### 3.1 Old URL → New URL Mappings

| Old URL | New URL | Redirect | Notes |
|---------|---------|----------|-------|
| `/oobc-management/staff/tasks/` | `/oobc-management/work-items/` | ❌ Manual | List view - no redirect yet |
| `/oobc-management/staff/tasks/new/` | `/oobc-management/work-items/create/` | ❌ Manual | Create form |
| `/oobc-management/staff/tasks/<id>/` | `/oobc-management/work-items/<uuid>/` | ✅ Redirect to list | Detail view |
| `/oobc-management/staff/tasks/<id>/edit/` | `/oobc-management/work-items/<uuid>/edit/` | ✅ Redirect to list | Edit form |
| `/oobc-management/staff/tasks/<id>/delete/` | `/oobc-management/work-items/<uuid>/delete/` | ❌ No redirect | Delete action |
| `/oobc-management/staff/tasks/<id>/modal/` | `/oobc-management/work-items/<uuid>/modal/` | ❌ HTMX only | Modal content |

**ProjectWorkflow URLs:** (Future implementation)
```
/project-central/workflows/<id>/        → /oobc-management/work-items/<uuid>/
/project-central/workflows/<id>/edit/   → /oobc-management/work-items/<uuid>/edit/
```

**CoordinationEvent URLs:** (Keep separate for now)
```
/coordination/events/<uuid>/            → Keep as-is (different domain)
/coordination/events/<uuid>/modal/      → Keep as-is (specialized UI)
```

---

### 3.2 Named URL Patterns

**Legacy Names (Deprecated):**
```python
# StaffTask
'common:staff_task_board'           # Kanban board
'common:staff_task_create'          # Create form
'common:staff_task_modal'           # Detail modal
'common:staff_task_delete'          # Delete endpoint
'common:staff_task_update'          # Update endpoint

# ProjectWorkflow
'project_central:workflow_detail'   # Detail view
'project_central:workflow_form'     # Create/edit form

# Event (keep for now)
'common:coordination_event_modal'   # Event modal
'common:coordination_event_add'     # Create event
```

**New Names (Active):**
```python
# WorkItem
'common:work_item_list'             # List view (replaces task_board)
'common:work_item_create'           # Create form
'common:work_item_detail'           # Detail view
'common:work_item_edit'             # Edit form
'common:work_item_delete'           # Delete endpoint
'common:work_item_modal'            # Detail modal (HTMX)
'common:work_item_tree_partial'     # Hierarchy tree
'common:work_item_update_progress'  # Progress update
'common:work_item_calendar_feed'    # Calendar JSON feed
```

---

## Part 4: Testing Checklist

### 4.1 URL Tests

**Manual Testing:**

- [ ] Visit `/oobc-management/work-items/` → Should load WorkItem list
- [ ] Visit `/oobc-management/work-items/create/` → Should load create form
- [ ] Visit `/oobc-management/staff/tasks/123/` → Should redirect to work item list
- [ ] Visit `/oobc-management/staff/tasks/123/edit/` → Should redirect to work item list

**Automated Tests:** (Future implementation)

```python
# tests/test_workitem_urls.py

def test_work_item_list_url_resolves():
    """Test that work item list URL resolves correctly"""
    url = reverse('common:work_item_list')
    assert url == '/oobc-management/work-items/'

def test_legacy_task_url_redirects():
    """Test that legacy StaffTask URLs redirect"""
    response = client.get('/oobc-management/staff/tasks/123/')
    assert response.status_code == 302
    assert response.url == reverse('common:work_item_list')
```

---

### 4.2 Template Tests

**Visual Regression Tests:**

- [ ] OOBC Management Home: "Create Work Item" button visible and functional
- [ ] OOBC Management Home: "Manage Work Items" link visible and functional
- [ ] Navbar: "Work Items" menu entry visible under OOBC Management
- [ ] Navbar: "Work Items" menu entry has correct description

**Functional Tests:**

- [ ] Click "Create Work Item" → Load WorkItem create form
- [ ] Click "Manage Work Items" → Load WorkItem list view
- [ ] Click navbar "Work Items" → Load WorkItem list view
- [ ] Calendar event click → Load WorkItem modal (after update)

---

### 4.3 User Workflow Tests

**Scenario 1: Create New Work Item**
1. Navigate to OOBC Management Home
2. Click "Create Work Item" button
3. Fill out WorkItem form (title, type, assignees, etc.)
4. Submit form
5. Verify redirect to WorkItem detail page
6. Verify item appears in WorkItem list

**Scenario 2: View Work Items**
1. Navigate to OOBC Management Home
2. Click "Manage Work Items" link
3. Verify WorkItem list loads with correct columns
4. Click on a work item
5. Verify detail view loads correctly

**Scenario 3: Access via Navbar**
1. Click "OOBC Mgt" in navbar
2. Hover to reveal dropdown
3. Click "Work Items" menu entry
4. Verify WorkItem list loads

**Scenario 4: Legacy URL Redirect**
1. Visit old URL: `/oobc-management/staff/tasks/123/`
2. Verify redirect to `/oobc-management/work-items/`
3. Verify no 404 error

---

## Part 5: Migration Timeline

### Phase 1: Foundation (✅ COMPLETE)
- [x] Uncomment WorkItem URL patterns
- [x] Add legacy URL redirects
- [x] Update OOBC Management Home template
- [x] Update navbar template
- [x] Document all changes

### Phase 2: Calendar Integration (⚠️ IN PROGRESS)
- [ ] Update calendar templates to use WorkItem modal
- [ ] Update calendar feed to include work_item_id
- [ ] Update eventClick handlers
- [ ] Test all calendar interactions
- [ ] Remove legacy modal references

### Phase 3: Dashboard Migration (📋 PLANNED)
- [ ] Update staff task board to use WorkItem views
- [ ] Update task modals to WorkItem modal
- [ ] Migrate task analytics to WorkItem queries
- [ ] Update project workflow templates
- [ ] Test all dashboard views

### Phase 4: Data Migration (📋 PLANNED)
- [ ] Create data migration script (StaffTask → WorkItem)
- [ ] Create data migration script (ProjectWorkflow → WorkItem)
- [ ] Optionally migrate CoordinationEvent → WorkItem (Activity type)
- [ ] Test data integrity
- [ ] Run migration in staging

### Phase 5: Cleanup (📋 PLANNED)
- [ ] Remove legacy StaffTask model
- [ ] Remove legacy ProjectWorkflow model
- [ ] Remove legacy templates
- [ ] Remove legacy views
- [ ] Remove legacy URL patterns
- [ ] Update all documentation

---

## Part 6: Backward Compatibility Notes

### 6.1 Session/Cookie Handling

**Current Behavior:**
- No session data tied to StaffTask model
- Calendar preferences stored separately
- No cookies specific to task views

**Impact:** ✅ No session/cookie migration needed

---

### 6.2 Bookmarked URLs

**User Impact:**
- Users with bookmarked `/oobc-management/staff/tasks/123/` will be redirected to work item list
- They can search/filter to find their specific work item
- Future enhancement: direct UUID redirect after data migration

**Mitigation:**
1. Add migration notice banner to redirected pages
2. Provide search/filter instructions
3. Consider browser extension to update bookmarks

---

### 6.3 External Links

**Sources:**
- Email notifications (task assignments, due date reminders)
- Slack/Teams integrations
- Calendar invites
- Reports/exports

**Action Required:**
- [ ] Update email templates to use WorkItem URLs
- [ ] Update notification service to use WorkItem endpoints
- [ ] Update calendar invite URLs
- [ ] Re-export reports with new URLs

---

## Part 7: Known Issues & Limitations

### 7.1 Current Limitations

1. **ID Mapping:** Integer StaffTask IDs cannot be directly mapped to UUID WorkItem IDs
   - **Workaround:** Redirect to list view, user searches manually
   - **Future Fix:** Add legacy_task_id field to WorkItem, implement smart redirect

2. **Calendar Modal:** Still uses legacy `staff_task_modal` endpoint
   - **Impact:** Task clicks in calendar load old modal
   - **Fix Required:** Update calendar template eventClick handler

3. **Recent Feeds:** OOBC Management Home still queries legacy models
   - **Impact:** "Recent Updates" shows old data structure
   - **Fix Required:** Update view to query WorkItem model

4. **Task Board:** Legacy `/oobc-management/staff/tasks/` URL still active
   - **Impact:** Old board view still accessible
   - **Decision:** Keep until Phase 3 migration complete

---

### 7.2 Breaking Changes

**None at this time.** All changes maintain backward compatibility via redirects.

**Future Breaking Changes (After Data Migration):**
- Legacy URL redirects will become permanent (301)
- Legacy views will be removed
- Legacy models will be deprecated

---

## Part 8: Rollback Plan

### 8.1 Quick Rollback (If Issues Arise)

**Step 1: Comment Out WorkItem URLs**
```python
# In src/common/urls.py, comment out lines 799-839:
# path("oobc-management/work-items/", ...) → # path("oobc-management/work-items/", ...)
```

**Step 2: Revert Template Changes**
```bash
git checkout src/templates/common/oobc_management_home.html
git checkout src/templates/common/navbar.html
```

**Step 3: Restart Server**
```bash
cd src
./manage.py runserver
```

**Time Required:** < 5 minutes

---

### 8.2 Full Rollback (Revert All Changes)

```bash
# Revert URLs
git checkout src/common/urls.py

# Revert templates
git checkout src/templates/common/oobc_management_home.html
git checkout src/templates/common/navbar.html

# Restart server
cd src
./manage.py runserver
```

---

## Part 9: Next Steps

### Immediate Actions (Week 1)

1. **Test Current Changes:**
   - [ ] Manual testing of all updated URLs
   - [ ] Visual inspection of updated templates
   - [ ] User acceptance testing with sample workflows

2. **Calendar Integration:**
   - [ ] Update calendar templates (oobc_calendar.html)
   - [ ] Update eventClick handler to use WorkItem modal
   - [ ] Test calendar interactions

3. **Documentation:**
   - [ ] Share this report with team
   - [ ] Create user migration guide
   - [ ] Update admin documentation

### Short-term Actions (Month 1)

1. **Dashboard Migration:**
   - [ ] Migrate staff task board to WorkItem views
   - [ ] Update task modals
   - [ ] Migrate analytics dashboards

2. **Data Migration Planning:**
   - [ ] Design migration script
   - [ ] Create staging environment test
   - [ ] Plan rollback strategy

### Long-term Actions (Quarter 1)

1. **Full Migration:**
   - [ ] Execute data migration
   - [ ] Remove legacy models
   - [ ] Update all integrations
   - [ ] Archive old code

---

## Part 10: Contact & Support

**Questions?** Contact:
- **Technical Lead:** [Your Name]
- **Project Manager:** [PM Name]
- **Slack Channel:** #obcms-workitem-migration

**Documentation:**
- **WorkItem Model Spec:** `docs/improvements/WORKITEM_HIERARCHY_SYSTEM.md`
- **API Reference:** `docs/api/workitem_endpoints.md`
- **User Guide:** `docs/user/workitem_user_guide.md`

---

## Appendix A: File Change Summary

### Modified Files (2025-10-05)

1. **`src/common/urls.py`**
   - Uncommented WorkItem URL patterns (lines 799-839)
   - Added legacy URL redirects (lines 841-854)
   - Added `from django.views.generic import RedirectView` import

2. **`src/templates/common/oobc_management_home.html`**
   - Updated "Create Task" → "Create Work Item" (line 70-73)
   - Updated "Manage Staff Tasks" → "Manage Work Items" (line 101-104)

3. **`src/templates/common/navbar.html`**
   - Added "Work Items" menu entry under OOBC Management (lines 240-246)

### Created Files (2025-10-05)

1. **`docs/refactor/TEMPLATE_URL_UPDATES.md`** (this document)
   - Comprehensive migration documentation
   - Testing checklist
   - Rollback procedures

---

## Appendix B: Code Samples

### B.1 WorkItem List View Usage

**In templates:**
```html
<!-- Link to work item list -->
<a href="{% url 'common:work_item_list' %}">View All Work Items</a>

<!-- Link to create work item -->
<a href="{% url 'common:work_item_create' %}">Create New Work Item</a>

<!-- Link to specific work item (requires UUID) -->
<a href="{% url 'common:work_item_detail' pk=work_item.id %}">View Details</a>
```

**In views:**
```python
from django.urls import reverse
from django.shortcuts import redirect

# Redirect to work item list
return redirect('common:work_item_list')

# Redirect to specific work item
return redirect('common:work_item_detail', pk=work_item_id)

# Build URL manually
url = reverse('common:work_item_detail', kwargs={'pk': work_item_id})
```

---

### B.2 WorkItem Modal Usage (HTMX)

**In calendar template:**
```html
<div id="work-item-modal-container"></div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        eventClick: function(info) {
            var workItemId = info.event.extendedProps.workItemId;
            if (workItemId) {
                // Load WorkItem modal via HTMX
                htmx.ajax('GET', `/oobc-management/work-items/${workItemId}/modal/`, {
                    target: '#work-item-modal-container',
                    swap: 'innerHTML'
                });
            }
        }
    });
    calendar.render();
});
</script>
```

---

### B.3 WorkItem Create Form Usage

**Button/Link:**
```html
<a href="{% url 'common:work_item_create' %}"
   class="btn btn-primary">
    <i class="fas fa-plus"></i>
    Create Work Item
</a>
```

**With query parameters (pre-fill form):**
```html
<a href="{% url 'common:work_item_create' %}?type=task&assignee={{ user.id }}"
   class="btn btn-primary">
    Create Task for Me
</a>
```

---

## Appendix C: Testing Commands

### C.1 URL Resolution Tests

```bash
# Test WorkItem URLs resolve
cd src
./manage.py shell

from django.urls import reverse
print(reverse('common:work_item_list'))          # /oobc-management/work-items/
print(reverse('common:work_item_create'))        # /oobc-management/work-items/create/
print(reverse('common:work_item_detail', kwargs={'pk': 'some-uuid'}))  # /oobc-management/work-items/some-uuid/
```

### C.2 Template Rendering Tests

```bash
# Test template syntax
cd src
./manage.py check --tag templates

# Test specific template
./manage.py shell
from django.template.loader import render_to_string
context = {'user': user, 'metrics': {}, 'recent_feeds': {}}
html = render_to_string('common/oobc_management_home.html', context)
print('work_item_create' in html)  # Should be True
print('staff_task_create' in html) # Should be False
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-05 | Claude Code | Initial document creation |
| 1.0 | 2025-10-05 | Claude Code | Added all implementation details |

---

**END OF DOCUMENT**
