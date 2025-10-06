# Calendar Event Deletion - Quick Debug Guide

**Problem:** Events not removed from calendar after deletion
**Goal:** Find the ID mismatch causing the issue

---

## 🚀 Quick Start (2 minutes)

### Step 1: Open Calendar Page
Navigate to: `http://localhost:8000/oobc-management/calendar/` (or your calendar page)

### Step 2: Open Browser Console
- **Chrome/Edge:** Press `F12` or `Ctrl+Shift+J` (Windows) / `Cmd+Option+J` (Mac)
- **Firefox:** Press `F12` or `Ctrl+Shift+K` (Windows) / `Cmd+Option+K` (Mac)
- **Safari:** `Cmd+Option+C`

### Step 3: Paste Debug Script

Copy the entire contents of `docs/bugs/calendar_debug.js` and paste into the console, then press Enter.

**OR** run this one-liner:

```javascript
fetch('/static/docs/bugs/calendar_debug.js').then(r=>r.text()).then(eval);
```

### Step 4: Delete an Event
Click delete on any calendar event and watch the console output.

---

## 📊 What to Look For

The debug script will output sections like this:

### ✅ SUCCESS Case (Event Found)
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

### ❌ FAILURE Case (Event NOT Found)
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
┌─────────┬──────────────┬──────────┬─────────┐
│ (index) │      id      │   type   │  title  │
├─────────┼──────────────┼──────────┼─────────┤
│    0    │ "event-123"  │ "string" │ "..." │  ← NOTE THE PREFIX!
└─────────┴──────────────┴──────────┴─────────┘

🔬 TRYING VARIANTS:
✅ FOUND "event- prefix": event-123 (string)  ← THIS IS THE FIX!
```

---

## 🎯 Common Issues & Fixes

### Issue 1: ID Type Mismatch

**Symptom:**
```
Searching for: "123" (string)
Calendar has: 123 (number)
```

**Fix:**
```javascript
// In your event handler
const calendarEvent = calendar.getEventById(Number(event.detail.id));
// or
const calendarEvent = calendar.getEventById(String(event.detail.id));
```

---

### Issue 2: ID Prefix Mismatch

**Symptom:**
```
Searching for: "123"
Calendar has: "event-123"
```

**Fix:**
```javascript
// In your event handler
const calendarEvent = calendar.getEventById(`event-${event.detail.id}`);
```

**File to modify:** `src/static/common/js/calendar.js` or wherever the delete handler is

---

### Issue 3: Wrong Property Path

**Symptom:**
```
❌ CRITICAL: No ID found in event detail!
Available properties: ["workItem", "action"]
```

**Fix:**
```javascript
// Before
const eventId = event.detail.id;

// After
const eventId = event.detail.workItem.id;
```

**File to modify:** Backend view that triggers `workItemDeleted` event

---

## 🛠️ Manual Commands

If you need to manually interact with the calendar:

```javascript
// List all events
calendarDebug.listEvents();

// Find specific event
calendarDebug.findByTitle("Community Meeting");

// Remove event manually (if you found the ID)
calendarDebug.removeById("event-123");

// Force refresh (temporary workaround)
calendarDebug.refresh();

// Show statistics
calendarDebug.stats();
```

---

## 📝 Common Fix Patterns

### Pattern A: String/Number Conversion
```javascript
// Location: src/static/common/js/calendar.js (or similar)

// BEFORE
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.id;
  const calendarEvent = calendar.getEventById(eventId);
  // ...
});

// AFTER (if calendar stores numbers but receives strings)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = Number(event.detail.id); // Convert to number
  const calendarEvent = calendar.getEventById(eventId);
  // ...
});
```

### Pattern B: Add Prefix
```javascript
// BEFORE
const calendarEvent = calendar.getEventById(event.detail.id);

// AFTER (if debug showed "event-" prefix needed)
const calendarEvent = calendar.getEventById(`event-${event.detail.id}`);
```

### Pattern C: Fix Backend
```python
# Location: src/common/views/work_items.py (or similar)

# BEFORE
return HttpResponse(
    status=204,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': work_item.id  # Sends as number
            }
        })
    }
)

# AFTER (if calendar expects strings)
return HttpResponse(
    status=204,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': str(work_item.id)  # Convert to string
            }
        })
    }
)
```

---

## ✅ Verification

After applying a fix:

```javascript
console.clear();

// Count before
const before = calendar.getEvents().length;
console.log('Events before:', before);

// Delete an event via UI

// Check after (wait 2 seconds)
setTimeout(() => {
  const after = calendar.getEvents().length;
  console.log('Events after:', after);
  console.log('Removed:', before - after);

  if (after === before - 1) {
    console.log('✅ FIX VERIFIED: Event removed successfully!');
  } else {
    console.log('❌ FIX FAILED: Event still present');
  }
}, 2000);
```

---

## 📋 Report Template

After finding the issue, document it:

```markdown
## Calendar Event Deletion Fix

**Date:** 2025-10-06
**Issue:** Events not removed from calendar after deletion

**Root Cause:**
[e.g., "ID type mismatch: calendar stores numbers, delete event sends strings"]

**Evidence:**
- Calendar event IDs: `123` (number)
- Delete event sends: `"123"` (string)
- `getEventById("123")` returns `null`

**Fix Applied:**
File: `src/static/common/js/calendar.js`
Line: ~45
Change: Convert string to number before lookup

```javascript
const eventId = Number(event.detail.id);
const calendarEvent = calendar.getEventById(eventId);
```

**Testing:**
- ✅ Deleted event in dev environment
- ✅ Console shows "VERIFIED: Event successfully removed"
- ✅ Event disappears from calendar instantly
- ✅ Page refresh confirms deletion persisted

**Status:** FIXED
```

---

## 🔗 Full Documentation

For complete debugging strategy: [CALENDAR_EVENT_DELETE_DEBUG.md](CALENDAR_EVENT_DELETE_DEBUG.md)

---

## 💡 Quick Tips

1. **Always check the console first** - The debug script will tell you exactly what's wrong
2. **Look for the variant that succeeds** - The script tries multiple ID formats
3. **Type matters** - `"123"` ≠ `123` in JavaScript strict equality
4. **Prefixes matter** - `"123"` ≠ `"event-123"`
5. **When in doubt, refresh** - `calendar.refetchEvents()` is a safe workaround

---

## 🆘 Still Not Working?

If the debug script doesn't help:

1. Check if calendar instance exists:
   ```javascript
   console.log(window.calendar);
   console.log(FullCalendar);
   ```

2. Check if delete event fires:
   ```javascript
   document.body.addEventListener('workItemDeleted', e => console.log('DELETE EVENT:', e));
   ```

3. Check network tab:
   - Is delete request sent?
   - Does it return 200/204?
   - Is HX-Trigger header present?

4. Check for JavaScript errors:
   - Open console before deleting
   - Look for red error messages

5. Share console output:
   - Copy entire console log
   - Share with team for analysis
