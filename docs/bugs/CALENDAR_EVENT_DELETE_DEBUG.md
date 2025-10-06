# Calendar Event Deletion Debugging Strategy

**Issue:** Events are not being removed from the calendar after deletion, despite `workItemDeleted` event firing successfully.

**Status:** Debugging in progress
**Priority:** HIGH
**Date:** 2025-10-06

---

## Problem Summary

**Symptom:**
- User deletes a work item/event
- `workItemDeleted` event fires (confirmed in logs)
- Event handler executes `calendar.getEventById(id).remove()`
- **BUT** Event remains visible on calendar
- Manual page refresh shows event is actually deleted from database

**Hypothesis:**
Event ID mismatch between:
1. What the delete handler is searching for
2. What the calendar actually has stored

---

## Debugging Commands

### Step 1: Inspect Calendar State After Load

Open browser console after calendar loads and run:

```javascript
// Get the calendar instance
const calendar = window.calendar || FullCalendar.Calendar.getInstance(document.getElementById('calendar'));

// List ALL events currently in calendar
const allEvents = calendar.getEvents();
console.log('=== CALENDAR EVENTS ===');
console.log('Total events:', allEvents.length);

allEvents.forEach((event, index) => {
  console.log(`Event ${index + 1}:`, {
    id: event.id,
    idType: typeof event.id,
    title: event.title,
    start: event.start,
    extendedProps: event.extendedProps
  });
});

// Show sample event structure
if (allEvents.length > 0) {
  console.log('=== SAMPLE EVENT FULL STRUCTURE ===');
  console.log(allEvents[0]);
}
```

**Expected Output:**
```
=== CALENDAR EVENTS ===
Total events: 15
Event 1: {
  id: "123",          // ← Note: String or Number?
  idType: "string",   // ← CRITICAL: Check this
  title: "Community Meeting",
  start: Date Mon Oct 07 2025...,
  extendedProps: {...}
}
```

---

### Step 2: Monitor Delete Event Payload

Before deleting an event, set up a listener:

```javascript
// Listen for workItemDeleted events
document.body.addEventListener('workItemDeleted', function(event) {
  console.log('=== WORK ITEM DELETED EVENT ===');
  console.log('Event detail:', event.detail);
  console.log('ID received:', event.detail.id);
  console.log('ID type:', typeof event.detail.id);

  // Try to find the event in calendar
  const calendarEvent = calendar.getEventById(event.detail.id);
  console.log('Found in calendar?', calendarEvent !== null);

  if (!calendarEvent) {
    console.error('❌ EVENT NOT FOUND IN CALENDAR');
    console.log('Searching for:', event.detail.id, '(type:', typeof event.detail.id, ')');

    // Show all available IDs for comparison
    const availableIds = calendar.getEvents().map(e => ({
      id: e.id,
      type: typeof e.id,
      title: e.title
    }));
    console.log('Available event IDs:', availableIds);
  } else {
    console.log('✅ EVENT FOUND IN CALENDAR');
    console.log('Event object:', calendarEvent);
  }
});

console.log('✅ Delete listener installed. Now delete an event.');
```

**Expected Issues:**
- ID type mismatch: `"123"` (string) vs `123` (number)
- ID format mismatch: `"work-item-123"` vs `"123"`
- ID property missing or undefined

---

### Step 3: Compare ID Formats

Run this after Step 2 captures a delete event:

```javascript
// Compare what we're searching for vs what exists
const searchingFor = event.detail.id; // From delete event
const calendarIds = calendar.getEvents().map(e => e.id);

console.log('=== ID COMPARISON ===');
console.log('Searching for:', searchingFor, '(type:', typeof searchingFor, ')');
console.log('Calendar has:', calendarIds);

// Try different ID formats
const variants = [
  searchingFor,
  String(searchingFor),
  Number(searchingFor),
  `work-item-${searchingFor}`,
  `workitem-${searchingFor}`,
  `event-${searchingFor}`
];

console.log('=== TRYING VARIANTS ===');
variants.forEach(variant => {
  const found = calendar.getEventById(variant);
  console.log(`"${variant}" (${typeof variant}):`, found ? '✅ FOUND' : '❌ NOT FOUND');
});
```

---

### Step 4: Inspect Event Source Data

Check how events are loaded into the calendar:

```javascript
// Find the script tag or AJAX call that loads events
console.log('=== EVENT SOURCES ===');
calendar.getEventSources().forEach((source, index) => {
  console.log(`Source ${index + 1}:`, source);
});

// If events are embedded in HTML, find them
const calendarElement = document.getElementById('calendar');
const eventData = calendarElement?.dataset?.events;
if (eventData) {
  console.log('=== EMBEDDED EVENT DATA ===');
  const parsed = JSON.parse(eventData);
  console.log('Sample events:', parsed.slice(0, 3));
}
```

---

## Manual Removal Workaround

If you need to manually remove an event while debugging:

```javascript
// Option 1: Remove by exact match
const eventToRemove = calendar.getEvents().find(e => e.title === 'Community Meeting');
if (eventToRemove) {
  eventToRemove.remove();
  console.log('✅ Manually removed event');
}

// Option 2: Remove by index
const allEvents = calendar.getEvents();
allEvents[0].remove(); // Remove first event
console.log('✅ Removed first event');

// Option 3: Force refresh calendar
calendar.refetchEvents();
console.log('✅ Calendar refreshed');
```

---

## Expected vs Actual Formats

### Scenario A: Type Mismatch
```javascript
// ACTUAL in calendar:
{ id: "123", title: "Meeting" }  // String

// SEARCHING for:
123  // Number

// FIX: Convert to string before searching
calendar.getEventById(String(event.detail.id))
```

### Scenario B: Prefix Mismatch
```javascript
// ACTUAL in calendar:
{ id: "work-item-123", title: "Meeting" }

// SEARCHING for:
"123"

// FIX: Add prefix
calendar.getEventById(`work-item-${event.detail.id}`)
```

### Scenario C: Property Path Issue
```javascript
// ACTUAL event detail:
{ workItem: { id: 123 }, action: "delete" }

// SEARCHING for:
event.detail.id  // undefined!

// FIX: Use correct path
event.detail.workItem.id
```

---

## Verification Commands

After applying a fix, verify it works:

```javascript
// 1. Clear console
console.clear();

// 2. Count events before deletion
const beforeCount = calendar.getEvents().length;
console.log('Events before deletion:', beforeCount);

// 3. Delete an event via UI
// (manually click delete)

// 4. Wait 2 seconds, then check
setTimeout(() => {
  const afterCount = calendar.getEvents().length;
  console.log('Events after deletion:', afterCount);
  console.log('Difference:', beforeCount - afterCount);

  if (afterCount === beforeCount - 1) {
    console.log('✅ SUCCESS: Event removed from calendar');
  } else {
    console.log('❌ FAILED: Event still in calendar');
  }
}, 2000);
```

---

## Files to Inspect

Based on the issue, check these files:

### 1. Event Handler (JavaScript)
**File:** `src/static/common/js/calendar.js` or similar

Look for:
```javascript
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.id; // ← Check this line
  const calendarEvent = calendar.getEventById(eventId); // ← Check this
  if (calendarEvent) {
    calendarEvent.remove();
  }
});
```

### 2. Event Source (Template or View)
**File:** `src/templates/common/oobc_calendar.html`

Look for event initialization:
```javascript
events: [
  {
    id: "{{ item.id }}",  // ← String template
    // vs
    id: {{ item.id }},    // ← Number literal
  }
]
```

### 3. Delete View (Backend)
**File:** `src/common/views/work_items.py` or similar

Look for HX-Trigger response:
```python
'HX-Trigger': json.dumps({
  'workItemDeleted': {
    'id': work_item.id,  # ← Number
    # vs
    'id': str(work_item.id)  # ← String
  }
})
```

---

## Quick Diagnosis Checklist

Run through these in order:

- [ ] **Step 1:** List all calendar events - Do they have IDs?
- [ ] **Step 2:** Install delete listener - Does event fire?
- [ ] **Step 3:** Check ID in event detail - What type is it?
- [ ] **Step 4:** Compare with calendar IDs - Do they match?
- [ ] **Step 5:** Identify mismatch type (string/number/prefix)
- [ ] **Step 6:** Apply fix based on mismatch type
- [ ] **Step 7:** Verify with deletion test

---

## Common Fixes

### Fix 1: Type Conversion
```javascript
// Before
const calendarEvent = calendar.getEventById(event.detail.id);

// After
const calendarEvent = calendar.getEventById(String(event.detail.id));
```

### Fix 2: ID Prefix
```javascript
// Before
const calendarEvent = calendar.getEventById(event.detail.id);

// After
const calendarEvent = calendar.getEventById(`work-item-${event.detail.id}`);
```

### Fix 3: Property Path
```javascript
// Before
const eventId = event.detail.id;

// After
const eventId = event.detail.workItem?.id || event.detail.id;
```

### Fix 4: Fallback to Refresh
```javascript
// If getEventById fails, force refresh
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.id;
  const calendarEvent = calendar.getEventById(eventId);

  if (calendarEvent) {
    calendarEvent.remove();
  } else {
    // Fallback: refresh all events
    console.warn('Event not found, refreshing calendar');
    calendar.refetchEvents();
  }
});
```

---

## Next Steps

1. **Run Step 1** to understand current calendar state
2. **Run Step 2** to capture delete event details
3. **Compare** the IDs from both steps
4. **Identify** the exact mismatch pattern
5. **Apply** the appropriate fix from "Common Fixes"
6. **Verify** with the verification commands
7. **Document** the root cause and fix

---

## Report Template

After debugging, fill this out:

```
CALENDAR EVENT DELETE DEBUG REPORT
==================================

Date: 2025-10-06
Debugger: [Your Name]

FINDINGS:
- Calendar event IDs: [type and format]
- Delete event IDs: [type and format]
- Mismatch type: [string/number/prefix/path]

ROOT CAUSE:
[Describe the exact issue]

FIX APPLIED:
[Code change made]

VERIFICATION:
- Before: [event count or behavior]
- After: [event count or behavior]
- Status: [✅ FIXED / ❌ NOT FIXED]

FILES MODIFIED:
- [file path and what changed]
```

---

## References

- FullCalendar API: https://fullcallendar.io/docs/Calendar-getEventById
- HTMX Events: https://htmx.org/reference/#events
- Django JSON Responses: https://docs.djangoproject.com/en/4.2/ref/request-response/#jsonresponse-objects
