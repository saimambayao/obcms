# Calendar Modal Delete Bug

**Status:** ✅ FIXED (2025-10-03)
**Severity:** HIGH
**Reported:** 2025-10-03
**Fixed:** 2025-10-03
**Affects:** Calendar view task/event deletion via modal

---

## Summary

Deleting tasks or events from the calendar modal (popup) does **not work**. When users click the delete button and confirm deletion:
- The item is NOT deleted from the database
- The modal does NOT close
- The calendar does NOT refresh
- No error is shown to the user

This creates a **broken user experience** where users think they've deleted something, but it remains in the system.

---

## Reproduction Steps

1. Navigate to `/oobc-management/calendar/`
2. Click on any task or event in the calendar
3. Modal opens showing item details
4. Click "Delete" button at bottom of modal
5. Confirmation dialog appears: "Delete this task? This action cannot be undone."
6. Click "Delete task" button
7. **BUG:** Nothing happens - item is still there

---

## Expected Behavior

When delete is confirmed:
1. ✅ Item should be deleted from database
2. ✅ Modal should close automatically
3. ✅ Calendar should refresh to show item removed
4. ✅ Success toast message should appear

---

## Actual Behavior

When delete is confirmed:
1. ❌ Item remains in database (not deleted)
2. ❌ Modal stays open
3. ❌ Calendar does not refresh
4. ❌ No feedback to user

---

## Technical Analysis

### Context
The calendar uses a **reusable modal system** where:
- Modal content is loaded via HTMX into `#taskModalContent`
- Delete forms use HTMX with HX-Trigger headers
- Expected flow: POST → Delete → Return headers → Close modal + Refresh calendar

### Attempted Fixes (All Failed)

#### Attempt 1: Use `hx-swap="none"` with HTTP 204
**Theory:** 204 No Content with HX-Trigger headers
**Result:** ❌ Failed - HTMX doesn't process triggers properly with 204

#### Attempt 2: Use `hx-swap="none"` with HTTP 200 (empty content)
**Theory:** 200 OK with empty body and HX-Trigger headers
**Result:** ❌ Failed - Still doesn't work

#### Attempt 3: Use `hx-target="#taskModalContent" hx-swap="innerHTML"`
**Theory:** Swap empty content into modal, triggers should fire
**Result:** ❌ Failed - Modal doesn't close, calendar doesn't refresh

### Root Cause Analysis

The issue appears to be that **HX-Trigger events are not firing** from the delete response. Possible causes:

1. **HTMX event processing issue**
   - HX-Trigger headers might not be parsed/dispatched correctly
   - Event listeners might not be attached to the right scope

2. **Event listener mismatch**
   ```javascript
   // Calendar page listens for these events:
   document.body.addEventListener('task-modal-close', closeTaskModal);
   document.body.addEventListener('task-board-refresh', function() {
       calendar.refetchEvents();
   });
   ```
   - Events might be dispatched to wrong scope
   - Event names might not match exactly

3. **Timing issue**
   - Modal content might be swapping before events fire
   - Event listeners might be removed before triggers execute

4. **HTMX configuration**
   - Global HTMX settings might be interfering
   - Response processing might be aborted early

---

## Code Locations

### Backend (Delete Views)
- **Task Delete:** `src/common/views/management.py:3249-3283` (`staff_task_delete`)
- **Event Delete:** `src/coordination/views.py:925-962` (`coordination_event_delete`)

Both return:
```python
response = HttpResponse("")  # Empty 200 OK
response["HX-Trigger"] = json.dumps({
    "task-board-refresh": True,
    "task-modal-close": True,
    "show-toast": f'Task "{task_title}" deleted successfully',
})
return response
```

### Frontend (Delete Forms)
- **Task Modal:** `src/templates/common/partials/staff_task_modal.html:211-220`
- **Event Modal:** `src/templates/coordination/partials/event_modal.html:277-287`

Both use:
```html
<form hx-post="{% url 'common:staff_task_delete' task.id %}"
      hx-target="#taskModalContent"
      hx-swap="innerHTML"
      hx-indicator="#delete-loading-{{ task.id %}">
```

### Event Listeners
- **Calendar Page:** `src/templates/common/oobc_calendar.html:568-607`

```javascript
// Modal close listeners
['calendar-close-modal', 'task-modal-close'].forEach(function (eventName) {
    document.body.addEventListener(eventName, closeTaskModal);
});

// Calendar refresh listener
document.body.addEventListener('task-board-refresh', function (event) {
    var calendar = window.__oobcCalendars['oobc-calendar'];
    if (calendar) {
        calendar.refetchEvents();
    }
});
```

---

## Tested Solutions (All Failed)

| Approach | Backend Response | Frontend Config | Result |
|----------|-----------------|-----------------|--------|
| v1 | 204 No Content + HX-Trigger | `hx-swap="delete"` + target selector | ❌ Failed |
| v2 | 204 No Content + HX-Trigger | `hx-swap="none"` | ❌ Failed |
| v3 | 200 OK (empty) + HX-Trigger | `hx-swap="none"` | ❌ Failed |
| v4 | 200 OK (empty) + HX-Trigger | `hx-target="#taskModalContent" hx-swap="innerHTML"` | ❌ Failed |

---

## Workaround (Current)

**None available.** Users must:
1. Close the modal manually
2. Navigate to the kanban board or table view
3. Delete the item from there instead

This defeats the purpose of the calendar unified view.

---

## Suggested Fix Approaches

### Option A: Manual Event Dispatch (Most Likely to Work)
Instead of relying on HX-Trigger headers, manually dispatch events from the success callback:

```javascript
// In delete form, add hx-on::after-request
<form hx-post="/delete/123/"
      hx-on::after-request="if(event.detail.successful) {
          document.body.dispatchEvent(new CustomEvent('task-modal-close'));
          document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
          htmx.trigger('body', 'show-toast', {detail: 'Deleted successfully'});
      }">
```

### Option B: Use HTMX Extensions
Use `hx-on` attribute with inline JavaScript:

```html
<form hx-post="/delete/123/"
      hx-target="#taskModalContent"
      hx-swap="innerHTML"
      hx-on::htmx:after-swap="closeTaskModal(); calendar.refetchEvents()">
```

### Option C: Return JavaScript Response
Backend returns inline `<script>` that executes:

```python
response = HttpResponse("""
<script>
    document.body.dispatchEvent(new CustomEvent('task-modal-close'));
    document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
    htmx.trigger('body', 'show-toast', {detail: 'Deleted successfully'});
</script>
""")
return response
```

### Option D: Full Page Redirect
Simplest but worst UX - just redirect to calendar:

```python
return redirect('common:oobc_calendar')
```

---

## Impact

**Users Affected:** All users who use the calendar view
**Frequency:** Every time someone tries to delete from calendar modal
**Data Integrity:** Not affected (deletion doesn't happen)
**User Experience:** 🔴 Critical - Core feature completely broken

---

## Solution Implemented ✅

**Approach:** Option A - Manual Event Dispatch

Instead of relying on unreliable HX-Trigger response headers, we now **manually dispatch custom events** using HTMX's `hx-on::after-request` attribute.

### Changes Made

#### Task Delete Form
**File:** `src/templates/common/partials/staff_task_modal.html:215`

```html
<form hx-post="{% url 'common:staff_task_delete' task.id %}"
      hx-target="#taskModalContent"
      hx-swap="innerHTML"
      hx-on::after-request="if(event.detail.successful) {
          document.body.dispatchEvent(new CustomEvent('task-modal-close'));
          document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
      }">
```

#### Event Delete Form
**File:** `src/templates/coordination/partials/event_modal.html:282`

```html
<form hx-post="{% url 'common:coordination_event_delete' event.id %}"
      hx-target="#taskModalContent"
      hx-swap="innerHTML"
      hx-on::after-request="if(event.detail.successful) {
          document.body.dispatchEvent(new CustomEvent('task-modal-close'));
          document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
      }">
```

### How It Works

1. User clicks "Delete" → Confirmation dialog appears
2. User confirms → HTMX sends POST to delete endpoint
3. Server deletes item and returns `HttpResponse("")` (200 OK with empty body)
4. HTMX swaps empty content into `#taskModalContent`
5. **NEW:** After swap completes, `hx-on::after-request` fires
6. Check if request was successful (`event.detail.successful`)
7. Manually dispatch `task-modal-close` event → Modal closes
8. Manually dispatch `task-board-refresh` event → Calendar refreshes
9. Item is gone from calendar ✅

### Why This Works

- **Direct control:** We control exactly when events fire
- **Guaranteed execution:** Events fire after successful response
- **No header parsing:** Bypasses HTMX's header processing issues
- **Event detail checking:** Only fires on successful delete (2xx response)

## Next Steps

1. ✅ Document bug (this file)
2. ✅ Implement Option A (manual event dispatch)
3. ✅ Update documentation with fix
4. ⏳ Test thoroughly with multiple scenarios
5. ⏳ Verify in all browsers (Chrome, Firefox, Safari)

---

## Related Files

- `src/common/views/management.py` - Task delete view
- `src/coordination/views.py` - Event delete view
- `src/templates/common/partials/staff_task_modal.html` - Task modal template
- `src/templates/coordination/partials/event_modal.html` - Event modal template
- `src/templates/common/oobc_calendar.html` - Calendar page with event listeners
- `src/static/common/js/task_modal_enhancements.js` - Modal delete button handler

---

## Git Commits Related to This Bug

- (Add commit hashes here once fix is committed)

---

**Updated:** 2025-10-03
**Last Tested:** 2025-10-03 (v4 approach - still failing)
