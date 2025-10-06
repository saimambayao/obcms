# Calendar Task Deletion Test Plan

## Bug Fix Summary
**Issue**: Tasks deleted from the OOBC Calendar modal were not being removed from the calendar view.

**Root Cause**: HTMX was not automatically dispatching custom events from the `HX-Trigger` response header. The backend was correctly sending `calendar-event-removed` triggers, but the frontend wasn't listening for them.

**Fix**: Added `htmx:afterRequest` event handler in `/src/templates/common/oobc_calendar.html` (lines 615-641) to manually parse the `HX-Trigger` header and dispatch custom events.

## Changes Made

### File: `/src/templates/common/oobc_calendar.html`

Added event handler that:
1. Intercepts all HTMX responses
2. Parses the `HX-Trigger` header (JSON format)
3. Dispatches each trigger as a custom DOM event
4. Existing `calendar-event-removed` listener then removes the event from FullCalendar

## Manual Testing Steps

### Prerequisites
1. Server is running: `cd src && python manage.py runserver`
2. Navigate to http://localhost:8000/oobc-management/calendar/
3. Login with admin credentials

### Test Case 1: Delete Task from Calendar Modal

**Steps:**
1. Open the OOBC Calendar page
2. Find any task event on the calendar (colored rectangles/blocks)
3. Click on a task to open the modal
4. In the modal, scroll down and click the "Delete" button (red text)
5. Click "Delete task" button in the confirmation dialog (red button)

**Expected Results:**
- ✅ The modal should close immediately
- ✅ The task should **instantly disappear** from the calendar view
- ✅ A success toast notification should appear: "Task [task name] deleted successfully"
- ✅ The calendar should refresh and show updated event count
- ✅ No page reload should occur

**Failure Indicators:**
- ❌ Task remains visible on calendar after deletion
- ❌ Full page reload occurs
- ❌ Modal doesn't close
- ❌ No toast notification appears

### Test Case 2: Verify Database Deletion

**Steps:**
1. Note the task title before deleting (e.g., "Review documentation")
2. Delete the task using Test Case 1 steps
3. Refresh the calendar page manually (F5)
4. Check if the task reappears

**Expected Results:**
- ✅ Task does NOT reappear after page refresh
- ✅ Task is permanently deleted from database

### Test Case 3: Multiple Task Deletion

**Steps:**
1. Delete 3-5 tasks in succession
2. Observe calendar updates after each deletion

**Expected Results:**
- ✅ Each task disappears immediately after deletion
- ✅ No visual glitches or calendar rendering issues
- ✅ Event counts update correctly
- ✅ Toast notifications appear for each deletion

### Test Case 4: Cross-Browser Testing

Test the deletion flow in:
- Chrome/Edge (Chromium-based)
- Firefox
- Safari (if on macOS)

**Expected Results:**
- ✅ Consistent behavior across all browsers
- ✅ No console errors in browser dev tools

## Technical Verification

### Check Browser Console

1. Open Browser Dev Tools (F12)
2. Go to Console tab
3. Delete a task
4. Look for these logs:

```
Task deleted: [task name]
calendar-event-removed event dispatched
Calendar event removed: staff-task-[id]
```

### Check Network Tab

1. Open Browser Dev Tools → Network tab
2. Delete a task
3. Find the DELETE request to `/oobc-management/staff/tasks/[id]/delete/`
4. Check Response Headers

**Expected Response Headers:**
```
HX-Trigger: {
  "task-board-refresh": true,
  "task-modal-close": true,
  "show-toast": "Task \"[name]\" deleted successfully",
  "calendar-event-removed": {"id": "staff-task-[id]"}
}
```

## Debugging

If task deletion fails:

1. **Check browser console for errors:**
   ```javascript
   // Expected: No errors
   // If error: "Cannot read property 'remove' of null"
   // → Calendar instance not initialized properly
   ```

2. **Verify HX-Trigger header is sent:**
   - Network tab → Response Headers
   - Should contain `HX-Trigger` with JSON payload

3. **Verify event listeners are registered:**
   ```javascript
   // In browser console:
   window.__oobcCalendars
   // Should show: {oobc-calendar: [FullCalendar instance]}
   ```

4. **Check server logs:**
   ```
   # Should see in terminal:
   INFO Attempting to delete task [id]
   INFO Deleting task: [name]
   INFO Task [name] deleted successfully
   INFO "POST /oobc-management/staff/tasks/[id]/delete/ HTTP/1.1" 200
   ```

## Rollback Plan

If issues persist, revert changes:

```bash
cd /Users/saidamenmambayao/Library/Mobile\ Documents/com~apple~CloudDocs/BTA/OOBC/obcms
git diff src/templates/common/oobc_calendar.html
# Review changes, then:
git checkout src/templates/common/oobc_calendar.html
```

## Additional Notes

- Fix also improves handling of ALL HX-Trigger events, not just `calendar-event-removed`
- This pattern should work for future HTMX-driven calendar updates
- No backend changes were needed - the backend was already correct
- Fix is compatible with HTMX 1.x and 2.x

## Success Criteria

✅ All Test Cases pass
✅ No console errors
✅ Instant UI updates (no page reload)
✅ Database changes persist
✅ Cross-browser compatibility

---

**Test Date**: 2025-10-04
**Tested By**: _____________
**Result**: ☐ PASS ☐ FAIL ☐ PARTIAL
**Notes**: _____________________________________________
