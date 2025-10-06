# Calendar Event ID Mismatch - Visual Examples

This document shows common ID mismatch scenarios with side-by-side comparisons.

---

## Scenario 1: String vs Number Type Mismatch

### What's Happening
Calendar stores IDs as **numbers**, but delete event sends **strings**.

### Visual Comparison

| Calendar Events (What Exists) | Delete Event (What We Search For) | Match? |
|------------------------------|-----------------------------------|--------|
| `id: 123` (number)           | `id: "123"` (string)              | ❌ NO  |
| `id: 456` (number)           | `id: "456"` (string)              | ❌ NO  |

### Code Comparison

```javascript
// ❌ CURRENT CODE (FAILS)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.id;  // "123" (string)
  const calendarEvent = calendar.getEventById(eventId);
  // Returns null because calendar has 123 (number)
});

// ✅ FIXED CODE
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = Number(event.detail.id);  // Convert to number
  const calendarEvent = calendar.getEventById(eventId);
  // Now finds 123 (number)
});
```

### How Debug Script Shows It

```
🔍 DIAGNOSTICS:
What we searched for: {value: "123", type: "string"}

What exists in calendar:
┌─────────┬─────┬──────────┐
│ (index) │  id │   type   │
├─────────┼─────┼──────────┤
│    0    │ 123 │ "number" │  ← Different type!
└─────────┴─────┴──────────┘

🔬 TRYING VARIANTS:
❌ NOT FOUND "Original": "123" (string)
✅ FOUND "Number": 123 (number)  ← THIS IS THE FIX!
```

---

## Scenario 2: Number vs String Type Mismatch (Reverse)

### What's Happening
Calendar stores IDs as **strings**, but delete event sends **numbers**.

### Visual Comparison

| Calendar Events (What Exists) | Delete Event (What We Search For) | Match? |
|------------------------------|-----------------------------------|--------|
| `id: "123"` (string)         | `id: 123` (number)                | ❌ NO  |
| `id: "456"` (string)         | `id: 456` (number)                | ❌ NO  |

### Code Comparison

```javascript
// ❌ CURRENT CODE (FAILS)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.id;  // 123 (number)
  const calendarEvent = calendar.getEventById(eventId);
  // Returns null because calendar has "123" (string)
});

// ✅ FIXED CODE
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = String(event.detail.id);  // Convert to string
  const calendarEvent = calendar.getEventById(eventId);
  // Now finds "123" (string)
});
```

### How Debug Script Shows It

```
🔍 DIAGNOSTICS:
What we searched for: {value: 123, type: "number"}

What exists in calendar:
┌─────────┬───────┬──────────┐
│ (index) │  id   │   type   │
├─────────┼───────┼──────────┤
│    0    │ "123" │ "string" │  ← Different type!
└─────────┴───────┴──────────┘

🔬 TRYING VARIANTS:
❌ NOT FOUND "Original": 123 (number)
✅ FOUND "String": "123" (string)  ← THIS IS THE FIX!
```

---

## Scenario 3: Missing Prefix

### What's Happening
Calendar stores IDs with a **prefix** (e.g., `work-item-123`), but delete event sends just the number.

### Visual Comparison

| Calendar Events (What Exists)    | Delete Event (What We Search For) | Match? |
|----------------------------------|-----------------------------------|--------|
| `id: "work-item-123"` (string)   | `id: "123"` (string)              | ❌ NO  |
| `id: "work-item-456"` (string)   | `id: "456"` (string)              | ❌ NO  |

### Code Comparison

```javascript
// ❌ CURRENT CODE (FAILS)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.id;  // "123"
  const calendarEvent = calendar.getEventById(eventId);
  // Returns null because calendar has "work-item-123"
});

// ✅ FIXED CODE
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = `work-item-${event.detail.id}`;  // Add prefix
  const calendarEvent = calendar.getEventById(eventId);
  // Now finds "work-item-123"
});
```

### How Debug Script Shows It

```
🔍 DIAGNOSTICS:
What we searched for: {value: "123", type: "string"}

What exists in calendar:
┌─────────┬──────────────────┬──────────┐
│ (index) │       id         │   type   │
├─────────┼──────────────────┼──────────┤
│    0    │ "work-item-123"  │ "string" │  ← Has prefix!
└─────────┴──────────────────┴──────────┘

🔬 TRYING VARIANTS:
❌ NOT FOUND "Original": "123" (string)
❌ NOT FOUND "String": "123" (string)
✅ FOUND "work-item- prefix": "work-item-123" (string)  ← THIS IS THE FIX!
```

### Where Prefix Comes From

**Backend (Template or View):**
```javascript
// When calendar is initialized
events: [
  {
    id: "work-item-{{ item.id }}",  // ← Prefix added here
    title: "{{ item.title }}",
    // ...
  }
]
```

---

## Scenario 4: Wrong Property Path

### What's Happening
Delete event sends ID nested in an object, but handler looks at wrong property.

### Visual Comparison

| Event Detail Structure       | Current Code                | What We Get        |
|------------------------------|-----------------------------|--------------------|
| `{workItem: {id: 123}}`      | `event.detail.id`           | `undefined` ❌     |
| `{workItem: {id: 123}}`      | `event.detail.workItem.id`  | `123` ✅           |

### Code Comparison

```javascript
// ❌ CURRENT CODE (FAILS)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.id;  // undefined!
  const calendarEvent = calendar.getEventById(eventId);
  // Returns null because eventId is undefined
});

// ✅ FIXED CODE
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.workItem.id;  // Correct path
  const calendarEvent = calendar.getEventById(eventId);
  // Now has correct ID
});

// ✅ DEFENSIVE CODE (handles both)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.workItem?.id || event.detail.id;
  const calendarEvent = calendar.getEventById(eventId);
  // Works regardless of structure
});
```

### How Debug Script Shows It

```
1️⃣ Event Detail Received:
Full detail object: {workItem: {id: 123, title: "Meeting"}, action: "delete"}

Possible ID paths: {
  "detail.id": undefined,              ← ❌ Wrong path
  "detail.workItem.id": 123,           ← ✅ Correct path
  "detail.data.id": undefined,
  "detail.item.id": undefined
}

❌ CRITICAL: No ID found in event detail!
Available properties: ["workItem", "action"]
```

### Backend Fix

If backend is sending wrong structure:

```python
# ❌ CURRENT (nested structure)
return HttpResponse(
    status=204,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'workItem': {
                    'id': work_item.id,
                    'title': work_item.title
                },
                'action': 'delete'
            }
        })
    }
)

# ✅ FIXED (flat structure)
return HttpResponse(
    status=204,
    headers={
        'HX-Trigger': json.dumps({
            'workItemDeleted': {
                'id': work_item.id,
                'title': work_item.title,
                'action': 'delete'
            }
        })
    }
)
```

---

## Scenario 5: Combined Mismatch (Type + Prefix)

### What's Happening
Multiple issues: wrong type **AND** missing prefix.

### Visual Comparison

| Calendar Events (What Exists)    | Delete Event (What We Search For) | Match? |
|----------------------------------|-----------------------------------|--------|
| `id: "event-123"` (string)       | `id: 123` (number)                | ❌ NO  |
| `id: "event-456"` (string)       | `id: 456` (number)                | ❌ NO  |

### Code Comparison

```javascript
// ❌ CURRENT CODE (FAILS)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = event.detail.id;  // 123 (number)
  const calendarEvent = calendar.getEventById(eventId);
  // Returns null - wrong type AND missing prefix
});

// ✅ FIXED CODE (two transforms needed)
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = `event-${String(event.detail.id)}`;  // Convert to string AND add prefix
  const calendarEvent = calendar.getEventById(eventId);
  // Now finds "event-123"
});
```

### How Debug Script Shows It

```
🔍 DIAGNOSTICS:
What we searched for: {value: 123, type: "number"}

What exists in calendar:
┌─────────┬──────────────┬──────────┐
│ (index) │      id      │   type   │
├─────────┼──────────────┼──────────┤
│    0    │ "event-123"  │ "string" │  ← Different type AND has prefix!
└─────────┴──────────────┴──────────┘

🔬 TRYING VARIANTS:
❌ NOT FOUND "Original": 123 (number)
❌ NOT FOUND "String": "123" (string)
❌ NOT FOUND "Number": 123 (number)
❌ NOT FOUND "work-item- prefix": "work-item-123" (string)
✅ FOUND "event- prefix": "event-123" (string)  ← THIS IS THE FIX!
```

---

## Quick Reference: ID Transformation Functions

Use these helper functions to handle different scenarios:

```javascript
// Helper: Normalize ID to match calendar format
function normalizeEventId(rawId) {
  // Example 1: Calendar uses numbers
  return Number(rawId);

  // Example 2: Calendar uses strings
  return String(rawId);

  // Example 3: Calendar uses prefixed strings
  return `work-item-${rawId}`;

  // Example 4: Smart detection (try multiple formats)
  const variants = [
    rawId,
    String(rawId),
    Number(rawId),
    `work-item-${rawId}`,
    `event-${rawId}`
  ];

  for (const variant of variants) {
    const found = calendar.getEventById(variant);
    if (found) return variant;
  }

  console.error('Could not find event with ID:', rawId);
  return null;
}

// Usage in event handler
document.body.addEventListener('workItemDeleted', function(event) {
  const eventId = normalizeEventId(event.detail.id);
  if (!eventId) return;

  const calendarEvent = calendar.getEventById(eventId);
  if (calendarEvent) {
    calendarEvent.remove();
  }
});
```

---

## Debugging Checklist

When encountering ID mismatch:

- [ ] **Step 1:** Check ID type (string vs number)
  ```javascript
  console.log(typeof event.detail.id);
  console.log(typeof calendar.getEvents()[0].id);
  ```

- [ ] **Step 2:** Check ID format (prefix, suffix, transformation)
  ```javascript
  console.log('Delete ID:', event.detail.id);
  console.log('Calendar IDs:', calendar.getEvents().map(e => e.id));
  ```

- [ ] **Step 3:** Check property path
  ```javascript
  console.log('Full event detail:', event.detail);
  console.log('Available properties:', Object.keys(event.detail));
  ```

- [ ] **Step 4:** Try manual match
  ```javascript
  const deleteId = event.detail.id;
  const calendarIds = calendar.getEvents().map(e => e.id);
  console.log('Match found?', calendarIds.includes(deleteId));
  ```

- [ ] **Step 5:** Apply appropriate fix from examples above

---

## Testing Your Fix

After applying a fix, verify it works:

```javascript
// Test script
(function testEventDeletion() {
  console.log('=== EVENT DELETION TEST ===');

  // Get current count
  const before = calendar.getEvents().length;
  console.log('Events before:', before);

  // Simulate deletion (replace with actual ID from your calendar)
  const testId = calendar.getEvents()[0].id;
  console.log('Testing with ID:', testId, '(type:', typeof testId, ')');

  // Trigger the delete handler (simulate HTMX event)
  const deleteEvent = new CustomEvent('workItemDeleted', {
    detail: { id: testId }
  });
  document.body.dispatchEvent(deleteEvent);

  // Check result
  setTimeout(() => {
    const after = calendar.getEvents().length;
    console.log('Events after:', after);

    if (after === before - 1) {
      console.log('%c✅ TEST PASSED: Event removed successfully', 'color: green; font-weight: bold');
    } else {
      console.log('%c❌ TEST FAILED: Event still exists', 'color: red; font-weight: bold');
    }
  }, 500);
})();
```

---

## Summary of Common Fixes

| Scenario | Calendar ID | Delete Event ID | Fix |
|----------|-------------|-----------------|-----|
| Type mismatch (string→number) | `123` | `"123"` | `Number(event.detail.id)` |
| Type mismatch (number→string) | `"123"` | `123` | `String(event.detail.id)` |
| Missing prefix | `"work-item-123"` | `"123"` | `` `work-item-${event.detail.id}` `` |
| Wrong property | N/A | `undefined` | `event.detail.workItem.id` |
| Multiple issues | `"event-123"` | `123` | `` `event-${String(event.detail.id)}` `` |

---

**Next Steps:**
1. Run the debug script: [calendar_debug.js](calendar_debug.js)
2. Identify your scenario from the examples above
3. Apply the corresponding fix
4. Test using the verification script
5. Document your fix for future reference
