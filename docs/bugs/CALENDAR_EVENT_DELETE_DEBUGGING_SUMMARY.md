# Calendar Event Deletion Debugging - Complete Summary

**Created:** 2025-10-06
**Status:** Debugging Tools Ready
**Priority:** HIGH

---

## Executive Summary

**Problem:** Events are not being removed from the calendar after deletion, despite the `workItemDeleted` event firing successfully. The modal closes, the database record is deleted, but the event remains visible on the calendar until page refresh.

**Root Cause (Hypothesis):** ID mismatch between what the delete handler searches for and what the calendar actually has stored. This could be:
- Type mismatch (string vs number)
- Format mismatch (prefixed vs plain ID)
- Property path issue (nested vs flat structure)

**Solution:** Comprehensive debugging strategy with automated tools to identify and fix the exact mismatch.

---

## Debugging Resources Created

### 1. **Comprehensive Debug Guide** (PRIMARY)
**File:** `docs/bugs/CALENDAR_EVENT_DELETE_DEBUG.md`

**Contents:**
- Complete problem analysis
- Step-by-step debugging commands
- Expected vs actual format comparisons
- Manual workaround instructions
- Verification procedures
- Report template

**When to use:** For detailed understanding of the issue and all debugging options.

---

### 2. **Automated Debug Script** (RECOMMENDED)
**File:** `docs/bugs/calendar_debug.js`

**Contents:**
- Ready-to-paste JavaScript debugging tool
- Automatic event monitoring
- ID variant testing
- Helper functions for manual interaction
- Real-time diagnostic output

**When to use:** Quick debugging session - paste into console and delete an event to see diagnostic output.

**Features:**
```javascript
// Automatically logs:
// - Current calendar state
// - All event IDs and their types
// - Delete event payload
// - ID comparison and matching
// - Suggested fixes

// Provides helper functions:
calendarDebug.listEvents()      // List all events
calendarDebug.findByTitle()     // Search by title
calendarDebug.removeById()      // Manual removal
calendarDebug.refresh()         // Force refresh
calendarDebug.stats()           // Show statistics
```

---

### 3. **Quick Start Guide** (START HERE)
**File:** `docs/bugs/CALENDAR_DEBUG_QUICKSTART.md`

**Contents:**
- 2-minute quick start procedure
- What to look for in output
- Common issues with immediate fixes
- Verification commands
- Manual interaction examples

**When to use:** First-time debugging or when you need a quick reference.

**Steps:**
1. Open calendar page
2. Open browser console (F12)
3. Paste debug script
4. Delete an event
5. Read diagnostic output
6. Apply suggested fix

---

### 4. **Visual Examples Reference**
**File:** `docs/bugs/ID_MISMATCH_EXAMPLES.md`

**Contents:**
- Side-by-side comparisons of common mismatches
- Code examples for each scenario
- Before/after code snippets
- Helper functions for ID normalization
- Testing procedures

**When to use:** After identifying the issue type, use this to see the exact fix pattern.

**Scenarios Covered:**
- String vs Number (both directions)
- Missing prefix (e.g., `work-item-123`)
- Wrong property path (nested objects)
- Combined mismatches (type + format)

---

## Quick Start (For Impatient Developers)

### Option A: One-Command Debug (Fastest)

1. Navigate to calendar page
2. Open browser console (F12)
3. Paste this:

```javascript
fetch('/static/docs/bugs/calendar_debug.js').then(r=>r.text()).then(eval);
```

4. Delete an event
5. Read the console output - it will tell you exactly what's wrong

---

### Option B: Manual Step-by-Step (2 minutes)

```javascript
// Step 1: Check calendar state
const allEvents = calendar.getEvents();
console.log('Calendar event IDs:', allEvents.map(e => ({id: e.id, type: typeof e.id})));

// Step 2: Listen for delete
document.body.addEventListener('workItemDeleted', function(event) {
  console.log('Delete event ID:', event.detail.id, '(type:', typeof event.detail.id, ')');

  const found = calendar.getEventById(event.detail.id);
  console.log('Found in calendar?', found !== null);

  if (!found) {
    console.log('❌ MISMATCH DETECTED');
    console.log('Try these variants:');
    console.log('String:', calendar.getEventById(String(event.detail.id)));
    console.log('Number:', calendar.getEventById(Number(event.detail.id)));
    console.log('Prefixed:', calendar.getEventById(`work-item-${event.detail.id}`));
  }
});

// Step 3: Delete an event and watch output
```

---

## Common Fix Patterns (Copy-Paste Ready)

### Fix 1: Convert to Number
```javascript
// Location: src/static/common/js/calendar.js (or similar)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = Number(event.detail.id);  // ← Add this conversion
  const calendarEvent = calendar.getEventById(eventId);
  if (calendarEvent) {
    calendarEvent.remove();
  }
});
```

### Fix 2: Convert to String
```javascript
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = String(event.detail.id);  // ← Add this conversion
  const calendarEvent = calendar.getEventById(eventId);
  if (calendarEvent) {
    calendarEvent.remove();
  }
});
```

### Fix 3: Add Prefix
```javascript
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = `work-item-${event.detail.id}`;  // ← Add prefix
  const calendarEvent = calendar.getEventById(eventId);
  if (calendarEvent) {
    calendarEvent.remove();
  }
});
```

### Fix 4: Correct Property Path
```javascript
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.workItem?.id || event.detail.id;  // ← Try nested first
  const calendarEvent = calendar.getEventById(eventId);
  if (calendarEvent) {
    calendarEvent.remove();
  }
});
```

### Fix 5: Defensive (Handles All Cases)
```javascript
document.body.addEventListener('workItemDeleted', function(event) {
  // Extract ID from various possible paths
  const rawId = event.detail.workItem?.id || event.detail.id;

  // Try different formats until one works
  const variants = [
    rawId,
    String(rawId),
    Number(rawId),
    `work-item-${rawId}`,
    `event-${rawId}`
  ];

  let calendarEvent = null;
  for (const variant of variants) {
    calendarEvent = calendar.getEventById(variant);
    if (calendarEvent) break;
  }

  if (calendarEvent) {
    calendarEvent.remove();
  } else {
    console.warn('Event not found, refreshing calendar');
    calendar.refetchEvents();
  }
});
```

---

## Files to Check/Modify

### Frontend (JavaScript)

**Location:** `src/static/common/js/calendar.js` or embedded in template

**What to look for:**
```javascript
// Event handler for deletion
document.body.addEventListener('workItemDeleted', function(event) {
  // ← This is where the fix goes
});
```

**Possible locations:**
- `src/static/common/js/calendar.js`
- `src/templates/common/oobc_calendar.html` (embedded script)
- `src/templates/common/calendar/*.html`

---

### Backend (Python)

**Location:** `src/common/views/work_items.py` or similar

**What to look for:**
```python
# Delete view response
return HttpResponse(
    status=204,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': ???  # ← Check this
            }
        })
    }
)
```

**Check if ID is:**
- `work_item.id` (number)
- `str(work_item.id)` (string)
- Nested in object structure

**Possible locations:**
- `src/common/views/work_items.py`
- `src/common/views.py`
- `src/coordination/views.py` (if calendar shows coordination events)

---

### Calendar Initialization

**Location:** Template where calendar is initialized

**What to look for:**
```javascript
// FullCalendar initialization
var calendar = new FullCalendar.Calendar(calendarEl, {
  events: [
    {
      id: "{{ item.id }}",    // ← String (template interpolation)
      // vs
      id: {{ item.id }},      // ← Number (no quotes)
      // vs
      id: "work-item-{{ item.id }}",  // ← Prefixed string
      title: "{{ item.title }}",
      // ...
    }
  ]
});
```

**Possible locations:**
- `src/templates/common/oobc_calendar.html`
- `src/templates/common/calendar/calendar_view.html`

---

## Verification Procedure

After applying a fix:

### 1. Clear Console
```javascript
console.clear();
```

### 2. Note Event Count
```javascript
console.log('Before:', calendar.getEvents().length);
```

### 3. Delete Event via UI
(Click delete button on any event)

### 4. Check Event Count Again
```javascript
setTimeout(() => {
  console.log('After:', calendar.getEvents().length);
}, 2000);
```

### 5. Expected Result
```
Before: 15
After: 14  ✅ Success!
```

### 6. Visual Confirmation
- Event should disappear immediately from calendar
- No console errors
- Modal should close
- Page refresh should show event still deleted

---

## Diagnostic Output Examples

### ✅ SUCCESS Output
```
🗑️ DELETION ATTEMPT #1
Timestamp: 2025-10-06T14:30:00.000Z

1️⃣ Event Detail Received:
Full detail object: {id: 123, action: "delete"}

2️⃣ ID to search for: "123" (type: string)

3️⃣ Searching calendar...
✅ SUCCESS: Event found in calendar!
Attempting removal...
✅ VERIFIED: Event successfully removed
```

### ❌ FAILURE Output (Type Mismatch)
```
🗑️ DELETION ATTEMPT #1
Timestamp: 2025-10-06T14:30:00.000Z

1️⃣ Event Detail Received:
Full detail object: {id: 123, action: "delete"}

2️⃣ ID to search for: "123" (type: string)

3️⃣ Searching calendar...
❌ FAILED: Event NOT found in calendar

🔍 DIAGNOSTICS:
What we searched for: {value: "123", type: "string"}

What exists in calendar:
┌─────────┬─────┬──────────┐
│ (index) │  id │   type   │
├─────────┼─────┼──────────┤
│    0    │ 123 │ "number" │  ← TYPE MISMATCH!
└─────────┴─────┴──────────┘

🔬 TRYING VARIANTS:
❌ NOT FOUND "Original": "123" (string)
✅ FOUND "Number": 123 (number)  ← USE THIS FIX!

🎯 POTENTIAL FIX IDENTIFIED!
The correct ID format is: 123
You need to use: calendar.getEventById(Number(eventId))
```

### ❌ FAILURE Output (Prefix Missing)
```
🔬 TRYING VARIANTS:
❌ NOT FOUND "Original": "123" (string)
❌ NOT FOUND "String": "123" (string)
❌ NOT FOUND "Number": 123 (number)
✅ FOUND "work-item- prefix": "work-item-123" (string)  ← USE THIS FIX!

🎯 POTENTIAL FIX IDENTIFIED!
The correct ID format is: "work-item-123"
You need to use: calendar.getEventById(`work-item-${eventId}`)
```

---

## Manual Workarounds

If you need to remove events manually while debugging:

### Remove by Title
```javascript
calendarDebug.removeByTitle("Community Meeting");
```

### Remove by ID (if you know the format)
```javascript
calendarDebug.removeById("work-item-123");
```

### Force Refresh (temporary fix)
```javascript
calendarDebug.refresh();
// or
calendar.refetchEvents();
```

### Remove All Events
```javascript
calendar.getEvents().forEach(e => e.remove());
console.log('All events removed');
```

---

## Troubleshooting

### Issue: Debug script won't load
**Symptom:** Script errors or nothing happens

**Solutions:**
1. Check if calendar instance exists:
   ```javascript
   console.log(window.calendar);
   ```

2. Check if FullCalendar is loaded:
   ```javascript
   console.log(FullCalendar);
   ```

3. Run script after calendar initializes:
   ```javascript
   document.addEventListener('DOMContentLoaded', function() {
     // Paste debug script here
   });
   ```

---

### Issue: Delete event doesn't fire
**Symptom:** No console output when deleting

**Solutions:**
1. Check if HTMX is loaded:
   ```javascript
   console.log(htmx);
   ```

2. Monitor all HTMX events:
   ```javascript
   document.body.addEventListener('htmx:afterSwap', e => console.log('HTMX event:', e));
   ```

3. Check network tab for delete request:
   - Open DevTools → Network
   - Delete event
   - Look for DELETE or POST request
   - Check response headers for `HX-Trigger`

---

### Issue: ID is undefined
**Symptom:** Debug shows `ID to search for: undefined`

**Solutions:**
1. Check event detail structure:
   ```javascript
   document.body.addEventListener('workItemDeleted', e => console.log(e.detail));
   ```

2. Look for nested properties:
   ```javascript
   console.log('Possible paths:', {
     'detail.id': event.detail?.id,
     'detail.workItem.id': event.detail?.workItem?.id,
     'detail.data.id': event.detail?.data?.id
   });
   ```

3. Check backend response (see "Files to Check" section above)

---

## Success Criteria

Fix is successful when:
- ✅ Event disappears from calendar immediately after deletion
- ✅ No console errors during deletion
- ✅ Modal closes smoothly
- ✅ Delete event count decreases by 1
- ✅ Page refresh confirms deletion persisted
- ✅ Multiple consecutive deletions work

---

## Next Steps

1. **Start with Quick Start Guide:** [CALENDAR_DEBUG_QUICKSTART.md](CALENDAR_DEBUG_QUICKSTART.md)

2. **Run debug script:** Copy `calendar_debug.js` into console

3. **Delete an event** and read diagnostic output

4. **Identify mismatch type:** Use [ID_MISMATCH_EXAMPLES.md](ID_MISMATCH_EXAMPLES.md)

5. **Apply fix** from "Common Fix Patterns" above

6. **Verify** using verification procedure

7. **Document** your findings and fix

---

## Documentation Index

| File | Purpose | Use When |
|------|---------|----------|
| [CALENDAR_DEBUG_QUICKSTART.md](CALENDAR_DEBUG_QUICKSTART.md) | 2-minute quick start | First time debugging |
| [calendar_debug.js](calendar_debug.js) | Automated debug script | Need diagnostic output |
| [ID_MISMATCH_EXAMPLES.md](ID_MISMATCH_EXAMPLES.md) | Visual examples | After identifying issue type |
| [CALENDAR_EVENT_DELETE_DEBUG.md](CALENDAR_EVENT_DELETE_DEBUG.md) | Comprehensive guide | Need detailed understanding |
| This file | Summary and overview | Reference and planning |

---

## Report Template

After fixing the issue, document it here:

```markdown
## FIX REPORT: Calendar Event Deletion

**Date:** 2025-10-06
**Fixed By:** [Your Name]

### Issue
Events not removed from calendar after deletion.

### Root Cause
[e.g., "ID type mismatch: calendar stores numbers, delete event sends strings"]

### Evidence
Debug output showed:
- Calendar IDs: `123` (number)
- Delete event ID: `"123"` (string)
- `getEventById("123")` returned `null`

### Fix Applied
**File:** `src/static/common/js/calendar.js`
**Line:** 45

**Before:**
```javascript
const eventId = event.detail.id;
```

**After:**
```javascript
const eventId = Number(event.detail.id);
```

### Testing
- ✅ Ran debug script
- ✅ Deleted test event
- ✅ Console showed "VERIFIED: Event successfully removed"
- ✅ Event disappeared from calendar
- ✅ Page refresh confirmed deletion
- ✅ Tested multiple deletions

### Status
✅ FIXED - Ready for commit
```

---

**Last Updated:** 2025-10-06
**Status:** Debugging tools ready, awaiting test results
