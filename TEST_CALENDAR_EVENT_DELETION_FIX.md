# Test Plan: Calendar Event Deletion Fix

## Overview

This document provides testing procedures to verify the FullCalendar event deletion fix.

**Fix Applied**: Replaced `calendar.getEventById()` with `Array.find()` for reliable event matching.

**File Modified**: `/src/templates/common/oobc_calendar.html` (lines 584-630)

---

## Pre-Test Setup

### 1. Start Development Server

```bash
cd src
python manage.py runserver
```

### 2. Open Browser Console

- Navigate to: `http://localhost:8000/oobc-management/calendar/`
- Open Developer Tools (F12 or Cmd+Option+I)
- Switch to **Console** tab

### 3. Create Test Work Items

Create at least 3 work items with different types:

```python
# Run in Django shell: python manage.py shell
from common.models import WorkItem
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Create test work items
project = WorkItem.objects.create(
    work_type='project',
    title='Test Project for Calendar Deletion',
    description='Testing event deletion functionality',
    start_date='2025-10-10',
    due_date='2025-12-31',
    created_by=user,
    is_calendar_visible=True
)

activity = WorkItem.objects.create(
    work_type='activity',
    title='Test Activity for Calendar Deletion',
    description='Testing activity deletion',
    parent=project,
    start_date='2025-10-15',
    due_date='2025-11-15',
    created_by=user,
    is_calendar_visible=True
)

task = WorkItem.objects.create(
    work_type='task',
    title='Test Task for Calendar Deletion',
    description='Testing task deletion',
    parent=activity,
    start_date='2025-10-20',
    due_date='2025-10-25',
    created_by=user,
    is_calendar_visible=True
)

print(f"Created Project: {project.id}")
print(f"Created Activity: {activity.id}")
print(f"Created Task: {task.id}")
```

---

## Test Cases

### Test Case 1: Single Work Item Deletion (No Children)

**Objective**: Verify instant removal of work item without children.

**Steps**:

1. Navigate to calendar: `http://localhost:8000/oobc-management/calendar/`
2. Find the "Test Task for Calendar Deletion" event
3. Click on the event to open the modal
4. Click the **Delete** button
5. Observe the browser console

**Expected Console Output**:

```
🗑️  Work item deleted: {id: "...", title: "Test Task for Calendar Deletion", type: "Task"}
🔍 Searching for work item ID: <uuid>
📊 Total events in calendar: 3
🔎 Searching for IDs: [<uuid>, "work-item-<uuid>", "coordination-event-<uuid>", "staff-task-<uuid>"]
✅ Found match: work-item-<uuid>
✅ Removed event from calendar with ID: work-item-<uuid>
✅ Task "Test Task for Calendar Deletion" deleted successfully
```

**Expected UI Behavior**:

- [ ] Event disappears from calendar **instantly** (no page reload)
- [ ] Modal closes automatically
- [ ] No error messages in console
- [ ] Calendar still shows other events

**Pass Criteria**: Event removed instantly without full calendar refresh.

---

### Test Case 2: Work Item with Children Deletion

**Objective**: Verify cascade deletion removes all events.

**Steps**:

1. Navigate to calendar
2. Click on "Test Activity for Calendar Deletion" event
3. Click **Delete** button
4. Observe console output

**Expected Console Output**:

```
🗑️  Work item deleted: {id: "...", title: "Test Activity for Calendar Deletion", type: "Activity"}
🔍 Searching for work item ID: <uuid>
📊 Total events in calendar: 2  (task already deleted, activity + project remain)
🔎 Searching for IDs: [...]
✅ Found match: work-item-<uuid>
✅ Removed event from calendar with ID: work-item-<uuid>
```

**Expected UI Behavior**:

- [ ] Activity event disappears instantly
- [ ] If task was still visible, it also disappears (cascade delete)
- [ ] Project event remains visible
- [ ] No console errors

**Pass Criteria**: Cascade deletion works, only parent activity removed from calendar.

---

### Test Case 3: Root-Level Work Item Deletion

**Objective**: Verify deletion of top-level work item.

**Steps**:

1. Navigate to calendar
2. Click on "Test Project for Calendar Deletion" event
3. Click **Delete** button
4. Observe console

**Expected Console Output**:

```
🗑️  Work item deleted: {id: "...", title: "Test Project for Calendar Deletion", type: "Project"}
🔍 Searching for work item ID: <uuid>
📊 Total events in calendar: 1
🔎 Searching for IDs: [...]
✅ Found match: work-item-<uuid>
✅ Removed event from calendar with ID: work-item-<uuid>
```

**Expected UI Behavior**:

- [ ] Project event disappears
- [ ] Calendar shows no test events
- [ ] No errors in console

---

### Test Case 4: Verify Legacy ID Format Compatibility

**Objective**: Ensure legacy event formats still work.

**Setup**: Manually create an event with legacy ID format in browser console:

```javascript
// In browser console on calendar page
calendar.addEvent({
    id: 'staff-task-12345678-1234-1234-1234-123456789abc',
    title: 'Legacy Staff Task',
    start: '2025-10-15',
    end: '2025-10-16',
    backgroundColor: '#3B82F6'
});
```

**Steps**:

1. Manually trigger deletion event:

```javascript
// In browser console
document.body.dispatchEvent(new CustomEvent('workItemDeleted', {
    detail: {
        id: '12345678-1234-1234-1234-123456789abc',
        title: 'Legacy Staff Task',
        type: 'Task'
    }
}));
```

2. Observe console output

**Expected Console Output**:

```
🗑️  Work item deleted: {id: "12345678-1234-1234-1234-123456789abc", title: "Legacy Staff Task", type: "Task"}
🔍 Searching for work item ID: 12345678-1234-1234-1234-123456789abc
📊 Total events in calendar: <count>
🔎 Searching for IDs: ["12345678-1234-1234-1234-123456789abc", "work-item-12345678-...", "coordination-event-12345678-...", "staff-task-12345678-..."]
✅ Found match: staff-task-12345678-1234-1234-1234-123456789abc
✅ Removed event from calendar with ID: staff-task-12345678-1234-1234-1234-123456789abc
```

**Pass Criteria**: Legacy format events are found and removed correctly.

---

### Test Case 5: Event Not Found Fallback

**Objective**: Verify graceful fallback when event doesn't exist.

**Steps**:

1. In browser console, trigger deletion for non-existent ID:

```javascript
document.body.dispatchEvent(new CustomEvent('workItemDeleted', {
    detail: {
        id: 'ffffffff-ffff-ffff-ffff-ffffffffffff',
        title: 'Non-Existent Work Item',
        type: 'Task'
    }
}));
```

2. Observe console output

**Expected Console Output**:

```
🗑️  Work item deleted: {id: "ffffffff-ffff-ffff-ffff-ffffffffffff", ...}
🔍 Searching for work item ID: ffffffff-ffff-ffff-ffff-ffffffffffff
📊 Total events in calendar: <count>
🔎 Searching for IDs: ["ffffffff-ffff-ffff-ffff-ffffffffffff", "work-item-ffffffff-...", ...]
⚠️  Could not find calendar event, triggering full refresh
⚠️  Searched for IDs: ffffffff-ffff-ffff-ffff-ffffffffffff,work-item-ffffffff-...
⚠️  Available event IDs: work-item-<uuid1>, work-item-<uuid2>, ...
```

**Expected UI Behavior**:

- [ ] Console shows warning (not error)
- [ ] Calendar automatically refreshes (refetchEvents)
- [ ] All valid events still display correctly
- [ ] No JavaScript errors

**Pass Criteria**: Fallback refresh works without errors.

---

### Test Case 6: Multiple Rapid Deletions

**Objective**: Verify system handles multiple quick deletions.

**Steps**:

1. Create 5 test work items
2. Delete them one by one rapidly (click delete as soon as previous modal closes)
3. Observe console for each deletion

**Expected Behavior**:

- [ ] Each deletion logs correctly
- [ ] Each event disappears instantly
- [ ] No "event not found" warnings
- [ ] Final calendar state is correct

**Pass Criteria**: All deletions succeed without race conditions.

---

### Test Case 7: Different Calendar Views

**Objective**: Test deletion works in all views.

**Steps**:

1. Switch to **Month** view → Delete an event → Verify instant removal
2. Switch to **Week** view → Delete an event → Verify instant removal
3. Switch to **List** view → Delete an event → Verify instant removal

**Expected Behavior**:

- [ ] Month view: Event disappears from month grid
- [ ] Week view: Event disappears from week timeline
- [ ] List view: Event disappears from list
- [ ] No view-specific errors

**Pass Criteria**: Deletion works identically in all calendar views.

---

## Performance Verification

### Benchmark: Deletion Speed

**Test**: Measure time from delete click to event removal.

**Expected**: < 100ms (instant to human perception)

**Measure in Console**:

```javascript
// Add timing to event listener (temporary test)
var startTime = performance.now();
// ... deletion code ...
var endTime = performance.now();
console.log(`⏱️  Deletion took ${(endTime - startTime).toFixed(2)}ms`);
```

**Pass Criteria**: Deletion completes in under 100ms.

---

## Browser Compatibility

Test in the following browsers:

- [ ] Chrome/Edge (Chromium) - Latest
- [ ] Firefox - Latest
- [ ] Safari - Latest (if on macOS)

**Expected**: Identical behavior in all browsers.

---

## Regression Testing

### Verify Related Features Still Work

After deletion fix:

- [ ] Creating new work items adds them to calendar
- [ ] Editing work items updates calendar display
- [ ] Moving events (drag & drop) still works
- [ ] Filtering calendar by type/status works
- [ ] Calendar date navigation works

---

## Known Issues to Monitor

1. **Cache invalidation**: Ensure deleted events don't reappear on calendar refresh
2. **Timezone handling**: Verify events deleted in correct timezone
3. **Permission checks**: Ensure unauthorized users can't delete

---

## Cleanup After Testing

```python
# Run in Django shell
from common.models import WorkItem

# Delete test work items
WorkItem.objects.filter(title__icontains='Test').delete()

print("Test work items cleaned up")
```

---

## Success Criteria Summary

Fix is considered successful if:

1. ✅ All 7 test cases pass
2. ✅ No JavaScript errors in console
3. ✅ Event removal is instant (< 100ms)
4. ✅ Fallback refresh works when event not found
5. ✅ Works in all calendar views (month/week/list)
6. ✅ Compatible with all major browsers
7. ✅ No regression in related features

---

## Troubleshooting

### Issue: Event still not found

**Debug**:

```javascript
// In browser console
console.log('All events:', calendar.getEvents().map(e => ({
    id: e.id,
    title: e.title,
    type: typeof e.id
})));
```

Compare the IDs to ensure format matches.

### Issue: Calendar not refreshing

**Check**:

1. Browser console for errors
2. Network tab for failed API calls
3. Cache settings in Django

### Issue: Permission errors

**Verify**:

1. User has delete permissions
2. `get_work_item_permissions()` returns correct values
3. HTMX DELETE request succeeds (check Network tab)

---

## Related Documentation

- [FULLCALENDAR_GETEVENTBYID_ROOT_CAUSE_ANALYSIS.md](FULLCALENDAR_GETEVENTBYID_ROOT_CAUSE_ANALYSIS.md) - Root cause analysis
- `/src/templates/common/oobc_calendar.html` - Calendar template with fix
- `/src/common/views/work_items.py` - Deletion view logic
- `/src/common/views/calendar.py` - Calendar feed logic

---

## Test Report Template

```markdown
## Test Execution Report

**Date**: YYYY-MM-DD
**Tester**: [Name]
**Environment**: Development/Staging/Production

### Test Results

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC1: Single deletion | PASS/FAIL | |
| TC2: Cascade deletion | PASS/FAIL | |
| TC3: Root deletion | PASS/FAIL | |
| TC4: Legacy format | PASS/FAIL | |
| TC5: Not found fallback | PASS/FAIL | |
| TC6: Rapid deletions | PASS/FAIL | |
| TC7: Different views | PASS/FAIL | |

### Issues Found

1. [Issue description]
   - Severity: High/Medium/Low
   - Reproducible: Yes/No
   - Fix required: Yes/No

### Performance

- Average deletion time: ___ ms
- Browser compatibility: Chrome ✓, Firefox ✓, Safari ✓

### Conclusion

Fix is: **APPROVED / NEEDS REVISION**
```
