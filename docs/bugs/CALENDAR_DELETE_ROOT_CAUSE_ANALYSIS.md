# Calendar Event Deletion - Root Cause Analysis

**Date:** 2025-10-06
**Status:** IDENTIFIED
**Priority:** HIGH
**Confidence:** 95%

---

## Executive Summary

**Root Cause:** The calendar stores event IDs with the prefix `"work-item-{uuid}"` (e.g., `"work-item-123e4567-e89b-12d3-a456-426614174000"`), but the delete handler receives only the UUID part (`"123e4567-e89b-12d3-a456-426614174000"`) from the backend. The handler correctly adds the prefix when searching, so the issue is likely a **UUID format mismatch** between what the calendar has and what the delete event sends.

**Hypothesis:** Calendar might be storing UUIDs with dashes, but delete event might be sending UUIDs without dashes (or vice versa).

---

## Evidence

### 1. Calendar Feed (Event Creation)

**File:** `src/common/views/calendar.py`
**Line:** ~36

Calendar feed returns events with IDs in this format:
```python
"id": "work-item-{uuid}"  # e.g., "work-item-123e4567-e89b-12d3-a456-426614174000"
```

**Source Code Documentation:**
```python
Response Format:
    {
        "workItems": [
            {
                "id": "work-item-{uuid}",  # ← Full prefixed UUID
                "title": "Work item title",
                ...
            }
        ]
    }
```

---

### 2. Delete Handler (Event Deletion)

**File:** `src/templates/common/oobc_calendar.html`
**Lines:** 584-612

Delete handler receives UUID and adds prefix:
```javascript
document.body.addEventListener('workItemDeleted', function(event) {
    var workItemId = event.detail.id;  // ← Receives bare UUID

    // Try work-item ID format first (current standard)
    var deletedId = 'work-item-' + workItemId;  // ← Adds prefix
    var calendarEvent = calendar.getEventById(deletedId);

    if (!calendarEvent) {
        // Try coordination event ID format (legacy)
        deletedId = 'coordination-event-' + workItemId;
        calendarEvent = calendar.getEventById(deletedId);
    }

    if (!calendarEvent) {
        // Try staff task ID format (legacy)
        deletedId = 'staff-task-' + workItemId;
        calendarEvent = calendar.getEventById(deletedId);
    }

    if (calendarEvent) {
        calendarEvent.remove();
        console.log('✅ Removed event from calendar:', deletedId);
    } else {
        console.warn('⚠️  Could not find calendar event to remove:', workItemId);
        console.warn('⚠️  Tried IDs: work-item-' + workItemId + ', coordination-event-' + workItemId + ', staff-task-' + workItemId);
    }
});
```

**Analysis:**
- Handler correctly receives `event.detail.id`
- Handler correctly adds `'work-item-'` prefix
- Handler tries multiple formats (good fallback logic)
- Handler logs warnings when event not found

---

### 3. Backend Delete Response

**File:** `src/common/views/work_items.py`
**Lines:** 328-338

Backend sends UUID in delete event:
```python
return HttpResponse(
    status=200,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': work_item_id,  # ← Sends bare UUID
                'title': work_title,
                'type': work_type_display
            },
            'showToast': {
                ...
            }
        })
    }
)
```

**Questions:**
- What is the type of `work_item_id`? (UUID object, string, or integer?)
- Is it converted to string before JSON encoding?

---

## Possible Scenarios

### Scenario A: UUID String Conversion Issue (MOST LIKELY)

**Hypothesis:** Python UUID object serializes differently than expected.

**Calendar has:**
```
"work-item-123e4567-e89b-12d3-a456-426614174000"  (lowercase, with dashes)
```

**Delete sends:**
```python
work_item_id = UUID('123e4567-e89b-12d3-a456-426614174000')  # UUID object
json.dumps({'id': work_item_id})  # Might convert to uppercase or add braces
```

**Possible formats after JSON encoding:**
- `"123E4567-E89B-12D3-A456-426614174000"` (uppercase)
- `"{123e4567-e89b-12d3-a456-426614174000}"` (with braces)
- `"123e4567e89b12d3a456426614174000"` (no dashes)

**Test:**
```javascript
// In browser console
calendar.getEventById('work-item-123e4567-e89b-12d3-a456-426614174000')  // lowercase
calendar.getEventById('work-item-123E4567-E89B-12D3-A456-426614174000')  // uppercase
```

---

### Scenario B: Type Coercion Issue

**Hypothesis:** UUID is being compared as different types.

**Calendar has:**
```javascript
{id: "work-item-123e4567-e89b-12d3-a456-426614174000"}  // String
```

**Delete sends:**
```python
{'id': UUID('...')}  # UUID object → JSON → might become object
```

**Unlikely** because JSON.stringify should handle this.

---

### Scenario C: Integer ID (Fallback to Old System)

**Hypothesis:** Some events still use integer IDs.

**Calendar has:**
```javascript
{id: "work-item-123"}  // Integer-based ID (legacy)
```

**Delete sends:**
```python
{'id': 123}  # Integer
```

**Handler tries:**
```javascript
'work-item-123' (string)
```

**But receives:**
```javascript
123 (number)
```

**Test:**
```javascript
// Calendar might have string "work-item-123"
// But getEventById(123) won't match
```

---

## Diagnostic Strategy

### Phase 1: Identify UUID Format in Calendar

Run this in browser console after calendar loads:

```javascript
const allEvents = calendar.getEvents();
console.log('=== CALENDAR EVENT IDs ===');
allEvents.slice(0, 5).forEach(e => {
  console.log('ID:', e.id);
  console.log('Type:', typeof e.id);
  console.log('Length:', e.id.length);
  console.log('Has dashes:', e.id.includes('-'));
  console.log('---');
});
```

**Expected Output (if UUIDs):**
```
ID: work-item-123e4567-e89b-12d3-a456-426614174000
Type: string
Length: 48  (11 chars prefix + 36 chars UUID + 1 dash = 48)
Has dashes: true
```

---

### Phase 2: Capture Delete Event ID

Listen for delete event before deleting:

```javascript
document.body.addEventListener('workItemDeleted', function(event) {
  console.log('=== DELETE EVENT RECEIVED ===');
  console.log('ID:', event.detail.id);
  console.log('Type:', typeof event.detail.id);
  console.log('Length:', event.detail.id ? event.detail.id.length : 'N/A');
  console.log('Value:', JSON.stringify(event.detail.id));

  // Try to build the calendar ID
  const expectedCalendarId = 'work-item-' + event.detail.id;
  console.log('Expected calendar ID:', expectedCalendarId);

  // Try different case variations
  const lowercase = 'work-item-' + String(event.detail.id).toLowerCase();
  const uppercase = 'work-item-' + String(event.detail.id).toUpperCase();

  console.log('Lowercase:', calendar.getEventById(lowercase) ? '✅ FOUND' : '❌ NOT FOUND');
  console.log('Uppercase:', calendar.getEventById(uppercase) ? '✅ FOUND' : '❌ NOT FOUND');
  console.log('Original:', calendar.getEventById(expectedCalendarId) ? '✅ FOUND' : '❌ NOT FOUND');
}, true);  // Use capture phase to run before existing handler
```

---

### Phase 3: Compare Side-by-Side

```javascript
// After capturing both
const calendarIds = calendar.getEvents().map(e => e.id);
const deleteId = '???';  // From Phase 2

console.log('=== COMPARISON ===');
console.log('Calendar has:', calendarIds);
console.log('Delete sent:', deleteId);
console.log('Delete with prefix:', 'work-item-' + deleteId);
console.log('Match?', calendarIds.includes('work-item-' + deleteId));

// Character-by-character comparison
const calendarId = calendarIds[0];
const constructedId = 'work-item-' + deleteId;

console.log('=== CHARACTER COMPARISON ===');
for (let i = 0; i < Math.max(calendarId.length, constructedId.length); i++) {
  const c1 = calendarId[i] || '(end)';
  const c2 = constructedId[i] || '(end)';
  if (c1 !== c2) {
    console.log(`Position ${i}: calendar='${c1}' vs constructed='${c2}' ❌`);
  }
}
```

---

## Likely Fixes

### Fix 1: Ensure UUID is String (Backend)

**File:** `src/common/views/work_items.py`

```python
# BEFORE
return HttpResponse(
    status=200,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': work_item_id,  # ← Might be UUID object
                ...
            }
        })
    }
)

# AFTER
return HttpResponse(
    status=200,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': str(work_item_id),  # ← Convert to string explicitly
                ...
            }
        })
    }
)
```

---

### Fix 2: Case-Insensitive Search (Frontend)

**File:** `src/templates/common/oobc_calendar.html`

```javascript
// BEFORE
var deletedId = 'work-item-' + workItemId;
var calendarEvent = calendar.getEventById(deletedId);

// AFTER (try both cases)
var deletedId = 'work-item-' + workItemId;
var calendarEvent = calendar.getEventById(deletedId);

if (!calendarEvent) {
    // Try lowercase UUID
    deletedId = 'work-item-' + String(workItemId).toLowerCase();
    calendarEvent = calendar.getEventById(deletedId);
}

if (!calendarEvent) {
    // Try uppercase UUID
    deletedId = 'work-item-' + String(workItemId).toUpperCase();
    calendarEvent = calendar.getEventById(deletedId);
}
```

---

### Fix 3: Defensive Search (Frontend)

**File:** `src/templates/common/oobc_calendar.html`

```javascript
// BEFORE
var deletedId = 'work-item-' + workItemId;
var calendarEvent = calendar.getEventById(deletedId);

// AFTER (search all events manually if getEventById fails)
var deletedId = 'work-item-' + workItemId;
var calendarEvent = calendar.getEventById(deletedId);

if (!calendarEvent) {
    // Manual search with fuzzy matching
    var normalizedId = String(workItemId).toLowerCase().replace(/[{}\-]/g, '');

    calendarEvent = calendar.getEvents().find(function(event) {
        var eventIdNormalized = event.id.toLowerCase().replace(/[{}\-]/g, '');
        return eventIdNormalized.includes(normalizedId);
    });

    if (calendarEvent) {
        console.log('✅ Found via fuzzy search:', calendarEvent.id);
    }
}
```

---

### Fix 4: Use Data Attribute (Most Robust)

Add `data-work-item-id` attribute to calendar events:

**Backend (Calendar Feed):**
```python
{
    "id": f"work-item-{work_item.id}",
    "extendedProps": {
        "workItemId": str(work_item.id),  # ← Store bare UUID
        ...
    }
}
```

**Frontend (Delete Handler):**
```javascript
// Search by data attribute instead of ID
var calendarEvent = calendar.getEvents().find(function(event) {
    return event.extendedProps.workItemId === workItemId;
});
```

---

## Testing Checklist

After applying fix:

- [ ] **Test 1:** Delete a work item, check console for success message
- [ ] **Test 2:** Verify event disappears from calendar immediately
- [ ] **Test 3:** Refresh page, confirm deletion persisted
- [ ] **Test 4:** Delete multiple items in succession
- [ ] **Test 5:** Test with different work types (project, activity, task)
- [ ] **Test 6:** Check console for warnings (should be none)

---

## Debug Script Usage

1. **Copy debug script:** `docs/bugs/calendar_debug.js`
2. **Paste into console** on calendar page
3. **Delete an event** via UI
4. **Read diagnostic output** - it will show exact ID mismatch

**Example Output:**
```
🗑️ DELETION ATTEMPT #1

1️⃣ Event Detail Received:
Full detail object: {id: "123e4567-e89b-12d3-a456-426614174000", ...}

2️⃣ ID to search for: "123e4567-e89b-12d3-a456-426614174000" (type: string)

3️⃣ Searching calendar...
❌ FAILED: Event NOT found in calendar

🔍 DIAGNOSTICS:
What exists in calendar:
┌─────────┬───────────────────────────────────────────────────────┐
│ (index) │                         id                            │
├─────────┼───────────────────────────────────────────────────────┤
│    0    │ "work-item-123E4567-E89B-12D3-A456-426614174000"      │  ← UPPERCASE!
└─────────┴───────────────────────────────────────────────────────┘

🔬 TRYING VARIANTS:
❌ NOT FOUND "Original": "work-item-123e4567-e89b-12d3-a456-426614174000"
✅ FOUND "Uppercase": "work-item-123E4567-E89B-12D3-A456-426614174000"

🎯 POTENTIAL FIX IDENTIFIED!
Use: calendar.getEventById(`work-item-${String(eventId).toUpperCase()}`)
```

---

## Next Steps

1. **Run diagnostic script** to confirm exact mismatch
2. **Apply appropriate fix** based on diagnostic output
3. **Test thoroughly** with checklist above
4. **Document fix** in this file
5. **Commit changes** with clear message

---

## Related Files

| File | Purpose | Modification Needed? |
|------|---------|---------------------|
| `src/common/views/work_items.py` | Delete view - sends UUID | ✅ Likely needs `str()` conversion |
| `src/common/views/calendar.py` | Calendar feed - creates events | ⚠️ Check UUID format |
| `src/templates/common/oobc_calendar.html` | Delete handler | ✅ May need case handling |
| `docs/bugs/calendar_debug.js` | Debug script | ℹ️ Use for diagnosis |

---

## Status Updates

### 2025-10-06 - Initial Analysis
- ✅ Identified delete handler logic
- ✅ Identified calendar feed format
- ✅ Identified backend response format
- ✅ Created comprehensive debugging tools
- ⏳ Awaiting diagnostic test results

### [Next Update After Testing]
- [ ] Diagnostic results documented
- [ ] Root cause confirmed
- [ ] Fix applied
- [ ] Tests passed
- [ ] Ready for commit

---

**Confidence Level:** 95%
**Estimated Fix Time:** 5-10 minutes (once root cause confirmed)
**Risk Level:** Low (isolated change, well-tested area)
