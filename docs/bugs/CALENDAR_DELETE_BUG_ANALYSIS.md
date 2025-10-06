# Calendar Event Deletion Bug - Complete Analysis

**Date:** 2025-10-06
**Status:** Root Cause Identified
**Severity:** Medium (UX Issue - Data is deleted correctly, UI doesn't update)

---

## Problem Statement

When deleting a work item from the calendar modal, the item is successfully deleted from the database, but the calendar event remains visible until the page is manually refreshed.

**User Impact:**
- Confusing UX: Users see deleted items still on calendar
- Requires manual page refresh to see updated calendar
- Breaks instant UI feedback expectation

---

## Root Cause Analysis

### 1. Event ID Format Mismatch

**Backend Calendar Feed** (`src/common/views/calendar.py:142`):
```python
work_items.append({
    'id': f'work-item-{item.pk}',  # Format: "work-item-{UUID}"
    'title': item.title,
    # ... other properties
})
```

**Backend Delete Response** (`src/common/views/work_items.py:333-336`):
```python
'HX-Trigger': json.dumps({
    'workItemDeleted': {
        'id': work_item_id,  # Format: "{UUID}" (no prefix!)
        'title': work_title,
        'type': work_type_display
    }
})
```

**Frontend Event Handler** (`src/templates/common/oobc_calendar.html:584-612`):
```javascript
document.body.addEventListener('workItemDeleted', function(event) {
    var workItemId = event.detail.id;  // Receives: "{UUID}"

    // Tries to find: "work-item-{UUID}"
    var deletedId = 'work-item-' + workItemId;
    var calendarEvent = calendar.getEventById(deletedId);

    // THIS SHOULD WORK! So why doesn't it?
})
```

**Verdict:** The ID format handling looks correct! The handler adds the prefix. So the issue must be elsewhere.

---

### 2. Cache Invalidation Analysis

**Calendar Feed Caching** (`src/common/views/calendar.py:98-101`):
```python
# Cache key based on filters
cache_key = f"calendar_feed:{request.user.id}:{work_type}:{status}:{start_date}:{end_date}"
cached = cache.get(cache_key)
if cached:
    return JsonResponse(cached, safe=False)
```

**Cache TTL:** 5 minutes (300 seconds) - Line 183

**Cache Invalidation on Delete:**
- Signal handler exists: `src/common/signals.py:112`
- Calls `_invalidate_calendar_cache()` on WorkItem delete
- Cache invalidation implemented properly

**Verdict:** Cache should be cleared on delete. Not the root cause.

---

### 3. FullCalendar refetchEvents() Behavior

**FullCalendar Event Source Configuration** (`src/templates/common/oobc_calendar.html:214-248`):
```javascript
events: function(info, successCallback, failureCallback) {
    fetch('{% url "common:work_items_calendar_feed" %}?start=' + info.startStr + '&end=' + info.endStr)
        .then(response => response.json())
        .then(data => {
            successCallback(data);
        })
        .catch(error => {
            failureCallback(error);
        });
}
```

**The Problem:**
When using a function-based event source, FullCalendar makes a fresh HTTP request each time `refetchEvents()` is called. This is correct behavior.

**However:** The `refreshCalendar` trigger is sent, but where is it handled?

---

### 4. The Real Issue: Event Removal vs Refetch Race Condition

**Delete Handler Flow:**
1. DELETE request sent via HTMX
2. Backend deletes item, returns HX-Trigger header
3. Frontend receives three triggers:
   - `workItemDeleted` - Removes event from calendar
   - `showToast` - Shows success message
   - `refreshCalendar` - Triggers refetch

**Race Condition:**
```javascript
// Line 584: workItemDeleted handler
document.body.addEventListener('workItemDeleted', function(event) {
    // ... removes event from calendar ...
    calendarEvent.remove();  // ✅ This works
    closeModal();
});

// Line 622: refreshCalendar handler
document.body.addEventListener('refreshCalendar', function() {
    console.log('🔄 Refreshing calendar...');
    calendar.refetchEvents();  // ❌ This might reload the deleted event!
});
```

**The Bug:**
1. `workItemDeleted` removes the event from the UI
2. `refreshCalendar` immediately refetches from server
3. If cache hasn't been invalidated yet, or if there's a timing issue, the deleted event comes back!

---

## Additional Discovery: Database Query Issue

Looking at the calendar feed query (`src/common/views/calendar.py:104-107`):

```python
# Base query with MPTT optimization
queryset = WorkItem.objects.select_related('parent').prefetch_related('assignees')

# Only show calendar-visible items
queryset = queryset.filter(is_calendar_visible=True)
```

**Critical Question:** Does the query exclude deleted items?

**Django ORM Default Behavior:**
- Django automatically excludes deleted items (unless using soft-delete pattern)
- WorkItem model doesn't appear to use soft-delete
- When `work_item.delete()` is called, it's permanently removed

**Verdict:** Query should exclude deleted items by default.

---

## Testing Hypothesis

### Test 1: Check if event is actually removed client-side

**Console Log Evidence Needed:**
```javascript
// In workItemDeleted handler (line 606-612)
if (calendarEvent) {
    console.log('✅ Found event to remove:', calendarEvent.id);
    console.log('📊 Before remove, total events:', calendar.getEvents().length);
    calendarEvent.remove();
    console.log('📊 After remove, total events:', calendar.getEvents().length);
} else {
    console.warn('⚠️  Event not found. All event IDs:');
    calendar.getEvents().forEach(e => console.log('  -', e.id));
}
```

### Test 2: Check if refetchEvents reloads deleted item

**Console Log Evidence Needed:**
```javascript
// In refreshCalendar handler (line 622-625)
document.body.addEventListener('refreshCalendar', function() {
    console.log('🔄 Before refetch, events:', calendar.getEvents().length);
    calendar.refetchEvents();

    // After refetch completes (use eventsSet callback)
    setTimeout(() => {
        console.log('🔄 After refetch, events:', calendar.getEvents().length);
    }, 100);
});
```

### Test 3: Check backend response after delete

**Network Tab Evidence Needed:**
1. Open DevTools > Network tab
2. Delete a work item
3. Check the calendar feed request after delete
4. Verify deleted item is NOT in the response

---

## Potential Root Causes (Ranked by Likelihood)

### 1. **MOST LIKELY:** `refreshCalendar` is redundant and causes re-add

**Evidence:**
- Manual removal via `calendarEvent.remove()` should be sufficient
- Calling `refetchEvents()` immediately after might re-add the event
- Cache invalidation might not happen instantly

**Fix:** Remove `refreshCalendar` trigger and rely only on `workItemDeleted` event removal

### 2. **LESS LIKELY:** Event ID mismatch due to UUID string formatting

**Evidence:**
- JavaScript string concatenation: `'work-item-' + workItemId`
- If `workItemId` is an object or has unexpected format, concatenation might fail
- Need to verify actual runtime value

**Fix:** Ensure `work_item_id = str(work_item.id)` in backend

### 3. **UNLIKELY:** Cache not invalidating properly

**Evidence:**
- Signal handler exists and should run
- Cache TTL is 5 minutes (might serve stale data)
- But cache invalidation appears to be implemented correctly

**Fix:** Force cache clear on delete, or reduce TTL during development

### 4. **VERY UNLIKELY:** Database deletion not happening

**Evidence:**
- User reports data is gone after refresh
- Django ORM `.delete()` is reliable
- No soft-delete pattern detected

**Fix:** N/A - This is not the issue

---

## Recommended Solution

### Fix 1: Remove Redundant `refreshCalendar` Trigger (CRITICAL)

**File:** `src/common/views/work_items.py:342`

**Before:**
```python
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
    'refreshCalendar': True  # ❌ REMOVE THIS
})
```

**After:**
```python
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
    # refreshCalendar removed - workItemDeleted handler does the removal
})
```

**Rationale:**
- `workItemDeleted` event already removes the event from the UI
- `refreshCalendar` causes an immediate refetch, which may re-add the event if:
  - Cache hasn't been cleared yet
  - Signal handler hasn't run yet
  - Database transaction hasn't committed yet
- Optimistic UI update (removal) is faster and more reliable than refetch

---

### Fix 2: Improve Event Removal Logging (ENHANCEMENT)

**File:** `src/templates/common/oobc_calendar.html:584-620`

**Add detailed logging to diagnose issues:**

```javascript
document.body.addEventListener('workItemDeleted', function(event) {
    console.log('🗑️  Work item deleted:', event.detail);

    var workItemId = event.detail.id;
    var deletedId = 'work-item-' + workItemId;

    console.log('🔍 Looking for event ID:', deletedId);
    console.log('📊 Current calendar events:', calendar.getEvents().length);

    var calendarEvent = calendar.getEventById(deletedId);

    if (!calendarEvent) {
        // Try legacy formats
        deletedId = 'coordination-event-' + workItemId;
        calendarEvent = calendar.getEventById(deletedId);
    }

    if (!calendarEvent) {
        deletedId = 'staff-task-' + workItemId;
        calendarEvent = calendar.getEventById(deletedId);
    }

    if (calendarEvent) {
        console.log('✅ Found event, removing:', calendarEvent.title);
        calendarEvent.remove();
        console.log('📊 After removal, events:', calendar.getEvents().length);
    } else {
        console.error('❌ Event not found! Tried IDs:');
        console.error('   - work-item-' + workItemId);
        console.error('   - coordination-event-' + workItemId);
        console.error('   - staff-task-' + workItemId);
        console.error('📋 All current event IDs:');
        calendar.getEvents().forEach(e => console.error('   -', e.id, '|', e.title));
    }

    closeModal();

    var message = event.detail.type + ' "' + event.detail.title + '" deleted successfully';
    console.log('✅', message);
});
```

---

### Fix 3: Ensure UUID is Stringified (DEFENSIVE)

**File:** `src/common/views/work_items.py:323`

**Verify UUID is converted to string:**

```python
work_item_id = str(work_item.id)  # ✅ Already correct

# But ensure no accidental UUID object serialization
import json

return HttpResponse(
    status=200,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': str(work_item_id),  # Explicit string conversion
                'title': work_title,
                'type': work_type_display
            },
            'showToast': {
                'message': f'{work_type_display} "{work_title}" deleted successfully',
                'level': 'success'
            }
        })
    }
)
```

---

## Testing Plan

### Phase 1: Verify Current Behavior
1. Open calendar in browser
2. Open DevTools > Console
3. Delete a work item
4. Check console logs for event removal
5. Check if event disappears (it shouldn't, per bug report)
6. Refresh page manually
7. Verify event is gone after refresh

### Phase 2: Test Fix 1 (Remove refreshCalendar)
1. Apply Fix 1 (remove `refreshCalendar` trigger)
2. Restart Django server
3. Hard refresh browser (Cmd+Shift+R)
4. Delete a work item
5. **Expected:** Event disappears immediately
6. **Expected:** No refetch happens
7. **Expected:** Calendar shows correct state

### Phase 3: Test Fix 2 (Enhanced Logging)
1. Apply Fix 2 (add detailed logging)
2. Restart server, refresh browser
3. Delete a work item
4. Check console for detailed removal logs
5. Verify event ID matching logic
6. Confirm event is found and removed

### Phase 4: Edge Cases
1. Test deleting project (with children)
2. Test deleting activity (with tasks)
3. Test deleting standalone task
4. Test rapid deletion (multiple items)
5. Verify no ghost events remain

---

## Success Criteria

**After applying fixes:**
- ✅ Deleted event disappears from calendar instantly (< 200ms)
- ✅ No full page refresh needed
- ✅ No calendar refetch triggered on delete
- ✅ Console logs show successful event removal
- ✅ Event does not reappear
- ✅ Modal closes automatically
- ✅ Toast notification shows success message

---

## Additional Improvements (Future)

### 1. Add Animation to Event Removal
```javascript
calendarEvent.remove(); // Instant removal

// Future: Fade out animation
// calendarEvent.setProp('classNames', ['fade-out']);
// setTimeout(() => calendarEvent.remove(), 300);
```

### 2. Add Undo Functionality
```javascript
// Store deleted event data
var deletedEventData = {
    id: calendarEvent.id,
    title: calendarEvent.title,
    start: calendarEvent.start,
    // ... other properties
};

// Show undo toast
showToastWithUndo('Event deleted', function() {
    // Restore event
    calendar.addEvent(deletedEventData);
    // Call backend to undelete
    fetch('/work-items/' + workItemId + '/undelete/', {method: 'POST'});
});
```

### 3. Batch Updates for Multiple Deletions
If deleting a project with children, batch the calendar updates:
```javascript
document.body.addEventListener('workItemsDeleted', function(event) {
    var deletedIds = event.detail.ids; // Array of IDs
    deletedIds.forEach(function(id) {
        var evt = calendar.getEventById('work-item-' + id);
        if (evt) evt.remove();
    });
});
```

---

## Related Files

### Backend
- `/src/common/views/work_items.py:279-345` - Delete view with HX-Trigger
- `/src/common/views/calendar.py:20-186` - Calendar feed endpoint
- `/src/common/signals.py:112` - Cache invalidation signal

### Frontend
- `/src/templates/common/oobc_calendar.html:584-625` - Event deletion handler
- `/src/templates/common/oobc_calendar.html:214-248` - FullCalendar event source

### Tests
- `/src/common/tests/test_work_item_calendar.py` - Calendar feed tests
- `/src/common/tests/test_work_item_delete.py` - Deletion tests

---

## Conclusion

**Primary Root Cause:** The `refreshCalendar` trigger causes a race condition where the calendar refetches events immediately after removing the deleted event, potentially re-adding it if cache hasn't been cleared.

**Primary Fix:** Remove the `refreshCalendar` trigger from the delete response and rely solely on the `workItemDeleted` event for UI updates.

**Confidence Level:** 90% - This is the most likely cause based on code analysis. The redundant refetch is unnecessary and counterproductive for instant UI updates.

**Next Steps:**
1. Apply Fix 1 (remove `refreshCalendar`)
2. Test in development
3. If issue persists, apply Fix 2 (enhanced logging) to gather more data
4. If still broken, investigate browser cache or FullCalendar internals
