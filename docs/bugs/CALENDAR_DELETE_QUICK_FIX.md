# Calendar Delete Bug - Quick Fix Guide

**Problem:** Deleted work items remain visible on calendar until page refresh

**Root Cause:** Race condition - `refreshCalendar` trigger refetches events immediately after removal

**Solution:** Remove the redundant `refreshCalendar` trigger

---

## The Fix

**File:** `/src/common/views/work_items.py`

**Line:** 332-343

**Change:**

```python
# BEFORE (Current - Buggy)
return HttpResponse(
    status=200,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': work_item_id,
                'title': work_title,
                'type': work_type_display
            },
            'showToast': {
                'message': f'{work_type_display} "{work_title}" deleted successfully',
                'level': 'success'
            },
            'refreshCalendar': True  # ❌ REMOVE THIS LINE
        })
    }
)

# AFTER (Fixed)
return HttpResponse(
    status=200,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': work_item_id,
                'title': work_title,
                'type': work_type_display
            },
            'showToast': {
                'message': f'{work_type_display} "{work_title}" deleted successfully',
                'level': 'success'
            }
            # refreshCalendar removed - workItemDeleted handler removes event from UI
        })
    }
)
```

---

## Why This Works

### Current Flow (Buggy)
1. User clicks delete
2. Backend deletes item, sends 3 triggers:
   - `workItemDeleted` → Removes event from calendar ✅
   - `showToast` → Shows success message ✅
   - `refreshCalendar` → **Refetches events from server** ❌
3. Refetch happens before cache is cleared
4. Deleted event comes back!

### Fixed Flow
1. User clicks delete
2. Backend deletes item, sends 2 triggers:
   - `workItemDeleted` → Removes event from calendar ✅
   - `showToast` → Shows success message ✅
3. No refetch = event stays removed ✅

---

## Testing

### Before Fix
```bash
# 1. Open calendar
# 2. Delete a work item
# 3. BUG: Event still visible
# 4. Refresh page
# 5. Event now gone
```

### After Fix
```bash
# 1. Open calendar
# 2. Delete a work item
# 3. FIXED: Event disappears immediately
# 4. No refresh needed
```

---

## Event Structure Reference

### Backend Calendar Feed Format
```javascript
{
    "id": "work-item-{UUID}",  // Important: "work-item-" prefix
    "title": "Task Title",
    "type": "Task",
    "start": "2025-10-15",
    "end": "2025-10-20",
    "color": "#F59E0B",
    // ... other properties
}
```

### Backend Delete Response
```json
{
    "workItemDeleted": {
        "id": "{UUID}",  // No prefix - handler adds it
        "title": "Task Title",
        "type": "Task"
    },
    "showToast": {
        "message": "Task deleted successfully",
        "level": "success"
    }
}
```

### Frontend Event Handler
```javascript
// Receives: {id: "abc-123", title: "Task", type: "Task"}
document.body.addEventListener('workItemDeleted', function(event) {
    var workItemId = event.detail.id;  // "abc-123"

    // Adds prefix to match calendar format
    var deletedId = 'work-item-' + workItemId;  // "work-item-abc-123"

    // Finds and removes event
    var calendarEvent = calendar.getEventById(deletedId);
    if (calendarEvent) {
        calendarEvent.remove();  // ✅ This works!
    }
});
```

---

## Implementation Steps

1. **Edit File**
   ```bash
   # Open the file
   code src/common/views/work_items.py

   # Find line 342: 'refreshCalendar': True
   # Delete that line and the comma on the previous line
   ```

2. **Restart Server**
   ```bash
   # Stop server (Ctrl+C)
   cd src
   python manage.py runserver
   ```

3. **Clear Browser Cache**
   ```bash
   # In browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
   ```

4. **Test**
   ```bash
   # 1. Go to /oobc-management/calendar/
   # 2. Click on any event
   # 3. Click delete button
   # 4. Verify event disappears immediately
   ```

---

## Rollback Plan

If the fix doesn't work, revert by adding the line back:

```python
return HttpResponse(
    status=200,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': work_item_id,
                'title': work_title,
                'type': work_type_display
            },
            'showToast': {
                'message': f'{work_type_display} "{work_title}" deleted successfully',
                'level': 'success'
            },
            'refreshCalendar': True  # Add this back if needed
        })
    }
)
```

---

## Expected Behavior After Fix

- ✅ Event disappears from calendar in < 200ms
- ✅ No page refresh needed
- ✅ Modal closes automatically
- ✅ Success toast appears
- ✅ Event does not reappear
- ✅ Console shows: "✅ Removed event from calendar: work-item-{UUID}"

---

## Full Analysis

For complete technical details, see:
- [CALENDAR_DELETE_BUG_ANALYSIS.md](./CALENDAR_DELETE_BUG_ANALYSIS.md)
