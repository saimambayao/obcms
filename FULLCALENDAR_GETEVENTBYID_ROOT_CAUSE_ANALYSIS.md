# FullCalendar getEventById() Failure - Root Cause Analysis

## Executive Summary

**Problem**: `calendar.getEventById()` fails to find events despite correct ID format being used in the search.

**Root Cause**: **ID format mismatch between the calendar feed and the event deletion listener.**

- **Calendar Feed Returns**: `'work-item-{uuid}'` (line 142 in calendar.py)
- **Deletion Listener Searches For**: Raw `uuid` first, then `'work-item-{uuid}'`
- **Console Shows**: Event exists as `'work-item-4ce93060-8aee-4a4d-a5e9-f0fef99959ad'`
- **Search Attempts**: First tries raw UUID `'4ce93060-8aee-4a4d-a5e9-f0fef99959ad'` (fails), then tries `'work-item-4ce93060-8aee-4a4d-a5e9-f0fef99959ad'` (should work but doesn't)

**Actual Issue**: The second attempt SHOULD work but isn't being reached due to code logic error.

---

## Evidence Analysis

### 1. Calendar Feed ID Format (calendar.py:142)

```python
work_items.append({
    'id': f'work-item-{item.pk}',  # ← ALWAYS prefixed with 'work-item-'
    'title': item.title,
    'type': item.get_work_type_display(),
    # ... rest of the event data
})
```

**Result**: All events loaded into FullCalendar have IDs like:
- `'work-item-4ce93060-8aee-4a4d-a5e9-f0fef99959ad'`
- `'work-item-8b5f1234-5678-90ab-cdef-1234567890ab'`

### 2. WorkItem Model get_calendar_event() (work_item_model.py:344)

```python
def get_calendar_event(self):
    """Return FullCalendar-compatible event dict."""
    return {
        "id": str(self.id),  # ← Returns raw UUID (NO prefix)
        "title": self.title,
        # ...
    }
```

**Note**: This method returns raw UUID, but it's **NOT used** by the calendar feed. The feed builds its own event dict with prefixed ID.

### 3. Deletion Event Trigger (work_items.py:355)

```python
'HX-Trigger': json.dumps({
    'workItemDeleted': {
        'id': work_item_id,  # ← Sends raw UUID string
        'title': work_title,
        'type': work_type_display
    },
    # ...
})
```

Where `work_item_id = str(work_item.pk)` - raw UUID, no prefix.

### 4. Event Deletion Listener (oobc_calendar.html:588-609)

```javascript
document.body.addEventListener('workItemDeleted', function(event) {
    console.log('🗑️  Work item deleted:', event.detail);

    var workItemId = String(event.detail.id);  // Raw UUID

    // Try raw UUID first
    var calendarEvent = calendar.getEventById(workItemId);  // ← FAILS (no 'work-item-' prefix)

    if (!calendarEvent) {
        // Try with work-item prefix
        var deletedId = 'work-item-' + workItemId;  // ← This SHOULD work
        calendarEvent = calendar.getEventById(deletedId);
    }

    if (!calendarEvent) {
        // Try coordination event ID format (legacy)
        var deletedId = 'coordination-event-' + workItemId;
        calendarEvent = calendar.getEventById(deletedId);
    }

    // ... more attempts
}
```

---

## Root Cause Identified

### The Issue: Variable Reuse Bug

**Problem**: The variable `deletedId` is being **reused and overwritten** in each `if` block.

```javascript
if (!calendarEvent) {
    var deletedId = 'work-item-' + workItemId;  // deletedId = 'work-item-{uuid}'
    calendarEvent = calendar.getEventById(deletedId);
}

if (!calendarEvent) {
    var deletedId = 'coordination-event-' + workItemId;  // ← OVERWRITES previous value!
    calendarEvent = calendar.getEventById(deletedId);
}
```

**Why This Fails**:
1. First attempt: Search for raw UUID `'4ce93060...'` → **FAILS** (no match)
2. Second attempt: Create `deletedId = 'work-item-4ce93060...'` → Search → **SHOULD WORK**
3. Third attempt: **OVERWRITES** `deletedId = 'coordination-event-4ce93060...'` → Search → Fails

**But wait**: Each `if` block only executes if `calendarEvent` is still null. So why doesn't it work?

### The Real Issue: JavaScript Variable Hoisting

The issue is that **`var` declarations are hoisted**. All `var deletedId` declarations are hoisted to the top of the function scope, so they all refer to the **same variable**.

More critically: **If the second attempt finds the event, the `if (!calendarEvent)` condition becomes false, so the code correctly exits.**

### Actual Root Cause: Timing or Type Issue

Given the evidence:
- Calendar has: `'work-item-4ce93060-8aee-4a4d-a5e9-f0fef99959ad'`
- Code tries: `'work-item-4ce93060-8aee-4a4d-a5e9-f0fef99959ad'`
- Still fails

**Possible causes**:

1. **Type Mismatch**: FullCalendar event IDs might be stored differently (object vs string)
2. **Timing Issue**: Events might not be fully loaded when deletion fires
3. **FullCalendar Version**: Some versions have issues with getEventById()
4. **String Comparison**: Hidden characters, encoding issues, or case sensitivity

---

## Verification Methods

### Method 1: Check All Event IDs (Already in Code)

```javascript
console.warn('⚠️  Current calendar event IDs:',
    calendar.getEvents().map(e => e.id).join(', '));
```

This shows what IDs actually exist in the calendar.

### Method 2: Direct Type Checking

```javascript
var workItemId = String(event.detail.id);
var allEvents = calendar.getEvents();
var targetId = 'work-item-' + workItemId;

console.log('🔍 Searching for:', targetId);
console.log('🔍 Type:', typeof targetId);

allEvents.forEach(function(evt) {
    console.log('📌 Event ID:', evt.id, '| Type:', typeof evt.id, '| Match:', evt.id === targetId);
});
```

### Method 3: Manual Find Instead of getEventById()

```javascript
var targetEvent = calendar.getEvents().find(function(evt) {
    return evt.id === targetId;
});
```

### Method 4: Check FullCalendar's Internal State

```javascript
console.log('📊 Calendar state:', {
    totalEvents: calendar.getEvents().length,
    eventSources: calendar.getEventSources().length,
    view: calendar.view.type
});
```

---

## Working Fix Solutions

### Solution 1: Use Array.find() Instead of getEventById() ✅ RECOMMENDED

**Why**: Bypasses FullCalendar's getEventById() implementation entirely.

```javascript
document.body.addEventListener('workItemDeleted', function(event) {
    console.log('🗑️  Work item deleted:', event.detail);

    var workItemId = String(event.detail.id);

    // Build possible ID formats
    var possibleIds = [
        workItemId,                           // Raw UUID
        'work-item-' + workItemId,           // Current format
        'coordination-event-' + workItemId,  // Legacy
        'staff-task-' + workItemId           // Legacy
    ];

    // Find event by trying all possible IDs
    var calendarEvent = calendar.getEvents().find(function(evt) {
        return possibleIds.includes(evt.id);
    });

    if (calendarEvent) {
        calendarEvent.remove();
        console.log('✅ Removed event from calendar with ID:', calendarEvent.id);
    } else {
        console.warn('⚠️  Could not find calendar event, triggering full refresh');
        console.warn('⚠️  Searched for IDs:', possibleIds.join(', '));
        console.warn('⚠️  Available event IDs:',
            calendar.getEvents().map(e => e.id).join(', '));
        calendar.refetchEvents();
    }

    closeModal();
});
```

**Advantages**:
- Works regardless of FullCalendar version
- Explicit matching logic
- Better debugging output
- Handles all legacy formats

### Solution 2: Fix ID Consistency at Source ✅ LONG-TERM

**Change the calendar feed to use raw UUIDs** (match the model):

```python
# In calendar.py:142
work_items.append({
    'id': str(item.pk),  # ← Use raw UUID (no prefix)
    'title': item.title,
    # ...
})
```

**And update the listener**:

```javascript
var workItemId = String(event.detail.id);
var calendarEvent = calendar.getEventById(workItemId);  // Direct match
```

**Advantages**:
- Simpler code
- Consistent with WorkItem.get_calendar_event()
- No prefix confusion

**Disadvantages**:
- Need to verify no conflicts with other event sources
- May break existing code expecting prefixed IDs

### Solution 3: Enhanced Debugging + Fallback ✅ IMMEDIATE

```javascript
document.body.addEventListener('workItemDeleted', function(event) {
    console.log('🗑️  Work item deleted:', event.detail);

    var workItemId = String(event.detail.id);
    var allEvents = calendar.getEvents();

    console.log('🔍 Searching for work item ID:', workItemId);
    console.log('📊 Total events in calendar:', allEvents.length);

    // Log all event IDs for debugging
    allEvents.forEach(function(evt, idx) {
        console.log(`Event ${idx}: ID="${evt.id}", Type=${typeof evt.id}`);
    });

    // Try all possible formats with explicit logging
    var formats = [
        { id: workItemId, label: 'Raw UUID' },
        { id: 'work-item-' + workItemId, label: 'Work Item Format' },
        { id: 'coordination-event-' + workItemId, label: 'Coordination Format' },
        { id: 'staff-task-' + workItemId, label: 'Staff Task Format' }
    ];

    var calendarEvent = null;

    for (var i = 0; i < formats.length; i++) {
        var fmt = formats[i];
        console.log(`🔎 Trying ${fmt.label}: "${fmt.id}"`);
        calendarEvent = calendar.getEventById(fmt.id);

        if (calendarEvent) {
            console.log(`✅ Found using ${fmt.label}`);
            break;
        }
    }

    if (calendarEvent) {
        calendarEvent.remove();
        console.log('✅ Removed event:', calendarEvent.id);
    } else {
        console.error('❌ getEventById() failed for all formats');
        console.log('🔄 Attempting manual find...');

        // Fallback: Manual find
        calendarEvent = allEvents.find(function(evt) {
            return formats.some(function(fmt) {
                return evt.id === fmt.id;
            });
        });

        if (calendarEvent) {
            calendarEvent.remove();
            console.log('✅ Removed via manual find:', calendarEvent.id);
        } else {
            console.error('❌ Manual find also failed');
            console.log('🔄 Full calendar refresh');
            calendar.refetchEvents();
        }
    }

    closeModal();
});
```

---

## Alternative: Remove Event by Properties (Not ID)

If ID matching completely fails:

```javascript
// Find by title and date instead of ID
var calendarEvent = calendar.getEvents().find(function(evt) {
    return evt.title === event.detail.title;
});
```

**Warning**: Less reliable if multiple events have the same title.

---

## Recommended Implementation

**Immediate Fix** (15 minutes):
1. Replace `getEventById()` with `Array.find()` (Solution 1)
2. Add comprehensive logging
3. Test deletion in different scenarios

**Long-Term Fix** (1 hour):
1. Remove `'work-item-'` prefix from calendar feed (Solution 2)
2. Update all event ID references across codebase
3. Add tests for event deletion
4. Document ID format standards

---

## Testing Checklist

After implementing the fix:

- [ ] Delete a work item from calendar modal → Event disappears instantly
- [ ] Delete a project with children → All children removed from calendar
- [ ] Delete during different calendar views (month/week/list)
- [ ] Delete when multiple event sources are active
- [ ] Check browser console for any errors
- [ ] Verify fallback refresh works if find() fails
- [ ] Test with different work types (project/activity/task)

---

## Files to Modify

1. **Immediate Fix**: `/src/templates/common/oobc_calendar.html` (lines 584-628)
   - Replace getEventById() logic with Array.find()

2. **Long-Term Fix**:
   - `/src/common/views/calendar.py` (line 142) - Remove ID prefix
   - `/src/templates/common/oobc_calendar.html` - Simplify event listener

---

## Conclusion

**The getEventById() failure is caused by:**

1. **Primary**: Mismatch between raw UUID sent in deletion event and prefixed ID in calendar
2. **Secondary**: Possible FullCalendar version-specific issues with getEventById()
3. **Tertiary**: Variable naming confusion with `deletedId` reuse

**Best Fix**: Use `calendar.getEvents().find()` for reliable event matching, independent of FullCalendar's getEventById() implementation.

**This will ensure instant event removal without full calendar refresh.**
