# Work Items Profile Page Issue Report

**Date**: 2025-10-08
**Status**: ROOT CAUSE IDENTIFIED
**Severity**: MEDIUM
**Component**: Staff Profile - Tasks Tab
**URL**: `http://localhost:8000/profile/?tab=tasks`

---

## Executive Summary

Work items assigned to users appear in the **calendar view** but do NOT appear in the **"Assigned tasks" section** on the same page. The status distribution also shows all zeros despite work items being assigned to the user.

**Root Cause**: **Query filter mismatch** - The "Assigned tasks" section only queries for `work_type="task"`, but the calendar displays ALL work types (projects, activities, tasks, etc.).

---

## Issue Details

### Current Behavior

1. **Calendar View**: Shows work items correctly (e.g., "Draeganess" project on October 8th)
2. **Assigned Tasks Section**: Shows "No tasks assigned to this staff member yet."
3. **Status Distribution**: Shows all zeros (Not Started: 0, In Progress: 0, etc.)

### Expected Behavior

1. **Calendar View**: Should show all assigned work items (CORRECT - already working)
2. **Assigned Tasks Section**: Should show recent work items assigned to the user (BROKEN)
3. **Status Distribution**: Should show accurate counts for each status (BROKEN)

---

## Root Cause Analysis

### Location 1: `build_staff_profile_detail_context` Function
**File**: `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/views/management.py`
**Lines**: 267-281

```python
# LINE 267-270: Recent tasks query (RESTRICTIVE - only tasks)
recent_tasks = (
    WorkItem.objects.filter(work_type="task", assignees=profile.user)
    .prefetch_related("teams", "assignees")
    .order_by("-updated_at")[:10]
)

# LINE 276-281: Status distribution query (RESTRICTIVE - only tasks)
tasks_by_status = {
    label: profile.user.assigned_work_items.filter(
        work_type="task", status=status
    ).count()
    for status, label in WorkItem.STATUS_CHOICES
}
```

**Problem**: Both queries filter by `work_type="task"`, which excludes:
- Projects (`work_type="project"`)
- Sub-projects (`work_type="sub_project"`)
- Activities (`work_type="activity"`)
- Sub-activities (`work_type="sub_activity"`)

### Location 2: Calendar Feed (CORRECT BEHAVIOR)
**File**: `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/templates/common/staff_profile/tabs/_tasks.html`
**Lines**: 159-194

```javascript
// LINE 163: Calendar fetches ALL work items for the user
const url = `/oobc-management/work-items/calendar/feed/?assignee=${userId}&_=${cacheBuster}`;
```

The calendar endpoint returns ALL work items assigned to the user (no `work_type` filter), which is why "Draeganess" (a project) appears in the calendar.

---

## Database Evidence

### Work Items in System

```
Total work items: 17
Work items with work_type="task": 2
```

### "Draeganess" Work Item Details

```
Title: Draeganess
Work type: project  ← NOT "task", so excluded from "Assigned tasks" section
Assignees: [Noron Andan (OOBC Executive), Quraish Langcap (OOBC Executive)]
Start date: 2025-10-08
Due date: 2025-10-09
```

### User Assignment Status

For the first user (admin):
```
Work items assigned: 0
Tasks assigned: 0  ← Zero tasks, but may have other work types
```

This confirms that:
1. The "Draeganess" project is assigned to other users (Noron Andan, Quraish Langcap)
2. The current user viewing the profile has no work items assigned
3. If viewing Noron or Quraish's profile, the calendar would show "Draeganess" but the "Assigned tasks" section would still be empty (because it's a project, not a task)

---

## Recommended Fix

### Option 1: Include All Work Types (Recommended)

**Change the queries to include all work types, not just tasks:**

```python
# Fix in src/common/views/management.py (line 267-270)

# BEFORE (restrictive):
recent_tasks = (
    WorkItem.objects.filter(work_type="task", assignees=profile.user)
    .prefetch_related("teams", "assignees")
    .order_by("-updated_at")[:10]
)

# AFTER (inclusive):
recent_tasks = (
    WorkItem.objects.filter(assignees=profile.user)  # Remove work_type filter
    .prefetch_related("teams", "assignees")
    .order_by("-updated_at")[:10]
)

# Fix status distribution (line 276-281)

# BEFORE (restrictive):
tasks_by_status = {
    label: profile.user.assigned_work_items.filter(
        work_type="task", status=status
    ).count()
    for status, label in WorkItem.STATUS_CHOICES
}

# AFTER (inclusive):
tasks_by_status = {
    label: profile.user.assigned_work_items.filter(
        status=status
    ).count()
    for status, label in WorkItem.STATUS_CHOICES
}
```

**Benefits:**
- Matches calendar behavior (consistency across UI)
- Shows all assigned work (projects, activities, tasks)
- Accurate status distribution
- Simpler query logic

### Option 2: Rename Section to "Assigned Tasks Only"

Keep the restrictive filter but update the UI to clarify that only tasks are shown:

```html
<!-- In src/templates/common/staff_profile/tabs/_tasks.html -->
<h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
    <i class="fas fa-tasks text-emerald-600"></i>
    Assigned Tasks Only  <!-- Change from "Assigned tasks" -->
</h2>
<p class="text-xs text-gray-500 mt-1">
    Projects and activities are shown in the calendar below
</p>
```

**Drawbacks:**
- Confusing UX (why differentiate?)
- Inconsistent with calendar
- Less useful overview

---

## Testing Steps

### 1. Reproduce the Issue

1. Navigate to `http://localhost:8000/profile/?tab=tasks`
2. Observe calendar shows "Draeganess" on October 8th
3. Observe "Assigned tasks" section shows empty state
4. Observe status distribution shows all zeros

### 2. Test the Fix (Option 1)

1. Apply the code changes to `src/common/views/management.py`
2. Restart Django server (no database migration needed)
3. Refresh `http://localhost:8000/profile/?tab=tasks`
4. Verify "Assigned tasks" section now shows "Draeganess"
5. Verify status distribution shows correct counts
6. Verify calendar still works correctly

### 3. Test Work Item Creation

1. Click "+ Create work item" button
2. Verify sidebar opens correctly
3. Fill in form:
   - Work Type: **Task** (to test original behavior)
   - Title: "Test Task from Profile"
   - Status: Not Started
   - Priority: Medium
   - Assign to current user
4. Submit the form
5. Verify new task appears in:
   - "Assigned tasks" section
   - Status distribution (increment "Not Started" count)
   - Calendar (if dates are set)

### 4. Test with Different Work Types

Create work items with different `work_type` values:
- Project
- Activity
- Task

Verify all appear in:
- Calendar view (already working)
- "Assigned tasks" section (after fix)
- Status distribution (after fix)

---

## Code Locations Reference

### Backend Context Builder
- **File**: `src/common/views/management.py`
- **Function**: `build_staff_profile_detail_context` (lines 204-305)
- **Lines to fix**: 267-270 (recent_tasks), 276-281 (tasks_by_status)

### Template Rendering
- **File**: `src/templates/common/staff_profile/tabs/_tasks.html`
- **Lines**: 44-80 (Assigned tasks section)
- **Lines**: 12-19 (Status distribution)
- **Lines**: 84-100 (Calendar view)

### Calendar Script
- **File**: `src/templates/common/staff_profile/tabs/_tasks.html`
- **Lines**: 103-255 (JavaScript calendar initialization)
- **Line 163**: Calendar feed URL (no work_type filter)

### Work Item Model
- **File**: `src/common/work_item_model.py`
- **Lines**: 27-250 (WorkItem model definition)
- **Lines**: 56-70 (WORK_TYPE_CHOICES)
- **Lines**: 173-178 (assignees field)

---

## Impact Assessment

### Current Impact
- **UX Confusion**: Users see work items in calendar but not in task list
- **Incomplete Information**: Status distribution inaccurate
- **Misleading Empty State**: "No tasks assigned" when work items exist

### After Fix (Option 1)
- **Consistency**: Calendar and task list show same data
- **Accuracy**: Status distribution reflects all assigned work
- **Better UX**: Complete overview of user's workload

### Performance
- **Minimal**: Removing `work_type="task"` filter may slightly increase query results
- **No N+1 Queries**: Already using `prefetch_related("teams", "assignees")`
- **No Database Changes**: Pure query modification

---

## Accessibility & UI Standards Compliance

### Current Template Compliance
The tasks tab template follows OBCMS UI standards:
- ✅ Rounded corners (`rounded-2xl`)
- ✅ Emerald accent colors (`text-emerald-600`)
- ✅ Proper spacing and padding
- ✅ Status badges with semantic colors
- ✅ Icon usage consistent with OBCMS guidelines

### After Fix
No UI changes required - only backend query modification.

---

## Recommendation

**Implement Option 1: Include All Work Types**

This fix:
1. Aligns backend queries with calendar behavior
2. Provides accurate, complete information
3. Requires minimal code changes (2 query modifications)
4. Improves UX consistency
5. No database migration needed
6. No breaking changes to API or templates

**Priority**: MEDIUM (affects UX but not blocking)
**Complexity**: Simple (query filter adjustment)
**Estimated Implementation**: 5 minutes
**Testing**: 10 minutes

---

## Next Steps

1. **Apply Fix**: Modify queries in `src/common/views/management.py`
2. **Test Locally**: Verify "Assigned tasks" section shows all work types
3. **Verify Calendar**: Ensure calendar still works correctly
4. **Test Creation**: Create work items of different types
5. **Update Documentation**: Document the change in changelog
6. **Deploy**: Push to staging for validation

---

## Additional Notes

### Why This Issue Occurred

The original implementation likely intended to separate "tasks" (tactical work) from "projects/activities" (strategic work). However, this creates UX confusion when:
1. Users are assigned to projects (e.g., "Draeganess")
2. Calendar shows the project
3. Task list shows empty (because project ≠ task)

### WorkItem Model Design

The unified `WorkItem` model supports all work types:
```python
WORK_TYPE_CHOICES = [
    ("project", "Project"),
    ("sub_project", "Sub-Project"),
    ("activity", "Activity"),
    ("sub_activity", "Sub-Activity"),
    ("task", "Task"),
    ("subtask", "Subtask"),
]
```

All share the same fields (assignees, status, dates, etc.), so filtering by work_type is optional, not required.

---

**Report Generated**: 2025-10-08
**Reporter**: Chrome DevTools MCP Debug Agent
**Status**: Awaiting fix implementation
