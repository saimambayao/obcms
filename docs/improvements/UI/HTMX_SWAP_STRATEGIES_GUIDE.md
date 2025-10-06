# HTMX Swap Strategies Guide for OBCMS

**Purpose:** Help developers choose the right HTMX swap strategy for different UI scenarios

**Date:** 2025-10-06

---

## Common HTMX Swap Strategies

### 1. `innerHTML` - Replace Inner Content

**Use Case:** Update content inside an element

```html
<!-- Before -->
<div id="target">
  <p>Old content</p>
</div>

<!-- HTMX Button -->
<button hx-get="/api/content"
        hx-target="#target"
        hx-swap="innerHTML">
  Update
</button>

<!-- After -->
<div id="target">
  <p>New content from server</p>
</div>
```

**Best For:**
- Updating card content
- Refreshing dashboard sections
- Replacing list contents

---

### 2. `outerHTML` - Replace Entire Element ⚠️ **1-to-1 ONLY**

**Use Case:** Replace entire element including the wrapper

```html
<!-- Before -->
<div id="target" class="card">
  <p>Old content</p>
</div>

<!-- HTMX Button -->
<button hx-get="/api/card"
        hx-target="#target"
        hx-swap="outerHTML">
  Replace Card
</button>

<!-- After -->
<div id="new-card" class="card-updated">
  <p>Completely new card</p>
</div>
```

**CRITICAL LIMITATION:**
- ❌ **Cannot replace 1 element with multiple elements**
- ✅ **Only works for 1-to-1 replacement**

**Example Failure:**
```html
<!-- This FAILS ❌ -->
<tr id="placeholder"></tr>  <!-- Target: 1 element -->

<!-- Server returns multiple <tr> elements -->
<tr>Child 1</tr>
<tr>Child 2</tr>
<tr>Child 3</tr>

<!-- HTMX Error: Cannot replace 1 with 3 -->
<!-- Error: TypeError: null is not an object (evaluating 'e.insertBefore') -->
```

**Best For:**
- Swapping single components
- Updating form fields
- Replacing single table rows
- Modal content replacement

---

### 3. `afterend` - Insert After Target ✅ **Multi-Element Support**

**Use Case:** Insert new elements as siblings after the target

```html
<!-- Before -->
<tr id="parent-row">Parent Item</tr>
<tr id="placeholder" style="display: none;"></tr>

<!-- HTMX Button -->
<button hx-get="/api/children"
        hx-target="#placeholder"
        hx-swap="afterend">
  Load Children
</button>

<!-- After HTMX (placeholder still exists) -->
<tr id="parent-row">Parent Item</tr>
<tr id="placeholder" style="display: none;"></tr>
<tr>Child 1</tr>  <!-- Inserted after placeholder -->
<tr>Child 2</tr>  <!-- Inserted after placeholder -->
<tr>Child 3</tr>  <!-- Inserted after placeholder -->

<!-- After JavaScript cleanup (placeholder.remove()) -->
<tr id="parent-row">Parent Item</tr>
<tr>Child 1</tr>
<tr>Child 2</tr>
<tr>Child 3</tr>
```

**Best For:**
- **Loading multiple table rows** ✅ (Work Items use case)
- Adding list items
- Progressive loading (load more)
- Inserting multiple siblings

**Workflow:**
1. HTMX inserts elements **after** target
2. JavaScript removes placeholder via `htmx:afterSwap` event
3. Clean DOM structure remains

---

### 4. `beforebegin` - Insert Before Target

**Use Case:** Insert new elements as siblings before the target

```html
<!-- Before -->
<ul id="list">
  <li id="marker">--- New items above ---</li>
  <li>Existing Item 1</li>
</ul>

<!-- HTMX Button -->
<button hx-get="/api/items"
        hx-target="#marker"
        hx-swap="beforebegin">
  Load More
</button>

<!-- After -->
<ul id="list">
  <li>New Item 1</li>
  <li>New Item 2</li>
  <li id="marker">--- New items above ---</li>
  <li>Existing Item 1</li>
</ul>
```

**Best For:**
- Prepending list items
- Loading older messages (chat)
- Infinite scroll (top)

---

### 5. `beforeend` - Insert Inside Target (at end)

**Use Case:** Append new content inside an element

```html
<!-- Before -->
<ul id="list">
  <li>Item 1</li>
</ul>

<!-- HTMX Button -->
<button hx-get="/api/more-items"
        hx-target="#list"
        hx-swap="beforeend">
  Load More
</button>

<!-- After -->
<ul id="list">
  <li>Item 1</li>
  <li>Item 2</li>  <!-- Appended inside -->
  <li>Item 3</li>  <!-- Appended inside -->
</ul>
```

**Best For:**
- Infinite scroll (bottom)
- Appending list items
- Loading more content

---

### 6. `afterbegin` - Insert Inside Target (at start)

**Use Case:** Prepend new content inside an element

```html
<!-- Before -->
<ul id="list">
  <li>Item 2</li>
</ul>

<!-- HTMX Button -->
<button hx-get="/api/new-items"
        hx-target="#list"
        hx-swap="afterbegin">
  Add New
</button>

<!-- After -->
<ul id="list">
  <li>Item 1</li>  <!-- Prepended inside -->
  <li>Item 2</li>
</ul>
```

**Best For:**
- Adding newest items first (reverse chronological)
- Notification lists
- Activity feeds

---

### 7. `delete` - Remove Element

**Use Case:** Remove target element from DOM

```html
<!-- Before -->
<div id="notification" class="alert">
  <p>You have a new message</p>
  <button hx-delete="/api/notification/123"
          hx-target="#notification"
          hx-swap="delete">
    Dismiss
  </button>
</div>

<!-- After -->
<!-- Element removed from DOM -->
```

**Best For:**
- Dismissing notifications
- Deleting list items
- Removing temporary elements

---

### 8. `none` - No Swap (Request Only)

**Use Case:** Make request but don't update DOM

```html
<button hx-post="/api/track-click"
        hx-swap="none">
  Track Event
</button>
```

**Best For:**
- Analytics tracking
- Background operations
- Fire-and-forget requests

---

## Decision Tree: Choosing the Right Swap Strategy

```
START
  |
  ├─ Need to replace target element itself?
  │   └─ YES → outerHTML (1-to-1 only) ⚠️
  │
  ├─ Need to replace target's content?
  │   └─ YES → innerHTML
  │
  ├─ Need to insert MULTIPLE siblings?
  │   ├─ Insert AFTER target → afterend ✅
  │   └─ Insert BEFORE target → beforebegin
  │
  ├─ Need to append/prepend INSIDE target?
  │   ├─ Append (at end) → beforeend
  │   └─ Prepend (at start) → afterbegin
  │
  ├─ Need to remove element?
  │   └─ YES → delete
  │
  └─ No DOM update needed?
      └─ YES → none
```

---

## Work Items Hierarchical Table Example

### Problem (Before Fix)

```html
<!-- Template: _work_item_tree_row.html -->
<button hx-get="/work-items/1/tree/"
        hx-target="#children-placeholder-1"
        hx-swap="outerHTML">  <!-- ❌ WRONG: Can't replace 1 with N -->
  Expand
</button>

<tr id="children-placeholder-1" style="display: none;"></tr>

<!-- Server returns: -->
<tr>Child 1</tr>
<tr>Child 2</tr>
<tr>Child 3</tr>

<!-- Result: ❌ HTMX Error (swapError, targetError) -->
```

### Solution (After Fix)

```html
<!-- Template: _work_item_tree_row.html -->
<button hx-get="/work-items/1/tree/"
        hx-target="#children-placeholder-1"
        hx-swap="afterend swap:300ms">  <!-- ✅ CORRECT: Insert after -->
  Expand
</button>

<tr id="children-placeholder-1" style="display: none;"></tr>

<!-- JavaScript: work_item_list.html -->
<script>
document.body.addEventListener('htmx:afterSwap', function(event) {
    const targetId = event.detail.target?.id;

    if (targetId?.startsWith('children-placeholder-')) {
        const placeholder = document.getElementById(targetId);

        // Remove placeholder after children inserted
        if (placeholder) {
            placeholder.remove();  // ✅ Cleanup
        }
    }
});
</script>

<!-- Result: ✅ Clean DOM, no errors -->
```

**DOM Evolution:**

```html
<!-- Step 1: Initial state -->
<tr data-work-item-id="1">Parent</tr>
<tr id="children-placeholder-1" style="display: none;"></tr>
<tr data-work-item-id="2">Next Parent</tr>

<!-- Step 2: After HTMX afterend swap -->
<tr data-work-item-id="1">Parent</tr>
<tr id="children-placeholder-1" style="display: none;"></tr>  ← Still here
<tr data-work-item-id="1-1">Child 1</tr>                      ← Inserted after
<tr data-work-item-id="1-2">Child 2</tr>                      ← Inserted after
<tr data-work-item-id="2">Next Parent</tr>

<!-- Step 3: After JavaScript placeholder.remove() -->
<tr data-work-item-id="1">Parent</tr>
<tr data-work-item-id="1-1">Child 1</tr>
<tr data-work-item-id="1-2">Child 2</tr>
<tr data-work-item-id="2">Next Parent</tr>  ← Clean structure ✅
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Using `outerHTML` for Multiple Elements

**Problem:**
```html
<button hx-get="/items"
        hx-target="#placeholder"
        hx-swap="outerHTML">  <!-- ❌ Fails if server returns multiple elements -->
```

**Solution:**
```html
<button hx-get="/items"
        hx-target="#placeholder"
        hx-swap="afterend">  <!-- ✅ Supports multiple elements -->
```

### Pitfall 2: Forgetting to Clean Up Placeholders

**Problem:**
```html
<!-- Placeholder remains in DOM after afterend swap -->
<div id="placeholder"></div>
<div>New Content</div>
<div>New Content</div>
```

**Solution:**
```javascript
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target?.id === 'placeholder') {
        event.detail.target.remove();  // ✅ Cleanup
    }
});
```

### Pitfall 3: Wrong Swap for Table Rows

**Problem:**
```html
<tbody hx-get="/rows" hx-swap="outerHTML">  <!-- ❌ Replaces <tbody> -->
```

**Solution:**
```html
<tbody hx-get="/rows" hx-swap="innerHTML">  <!-- ✅ Replaces rows inside -->
```

---

## Performance Best Practices

### 1. Use Appropriate Swap Transitions

```html
<!-- Fast transitions for small updates -->
<button hx-swap="innerHTML swap:100ms">Quick Update</button>

<!-- Smooth transitions for larger changes -->
<button hx-swap="afterend swap:300ms">Load Children</button>

<!-- No transition for instant updates -->
<button hx-swap="innerHTML swap:0ms">Instant</button>
```

### 2. Avoid Unnecessary Swaps

```html
<!-- ❌ Bad: Full re-render on every change -->
<div hx-get="/dashboard" hx-swap="outerHTML" hx-trigger="every 5s">

<!-- ✅ Good: Only update changed parts -->
<div id="stats" hx-get="/stats" hx-swap="innerHTML" hx-trigger="every 30s">
```

### 3. Use `hx-select` for Targeted Swaps

```html
<!-- Server returns full page, but only swap specific part -->
<button hx-get="/page"
        hx-target="#content"
        hx-swap="innerHTML"
        hx-select="#updated-section">  <!-- Only extract this part -->
```

---

## Accessibility Considerations

### 1. Maintain Focus Management

```html
<button hx-post="/action"
        hx-swap="outerHTML"
        hx-on="htmx:afterSwap: this.focus()">  <!-- Keep focus on button -->
```

### 2. Announce Changes to Screen Readers

```html
<!-- Add aria-live region for dynamic content -->
<div id="notifications"
     aria-live="polite"
     aria-atomic="true"
     hx-get="/notifications"
     hx-swap="innerHTML"
     hx-trigger="every 60s">
</div>
```

### 3. Preserve Keyboard Navigation

```javascript
document.body.addEventListener('htmx:afterSwap', function(event) {
    // Re-initialize keyboard handlers if needed
    initKeyboardNavigation(event.detail.target);
});
```

---

## Summary Table

| Swap Strategy | Target | Result | Multi-Element | Use Case |
|---------------|--------|--------|---------------|----------|
| `innerHTML` | Element content | Replace inner HTML | ✅ Yes | Update content |
| `outerHTML` | Element itself | Replace entire element | ❌ **No** | 1-to-1 replacement |
| `afterend` | After element | Insert siblings after | ✅ **Yes** | Table rows, lists |
| `beforebegin` | Before element | Insert siblings before | ✅ Yes | Prepend siblings |
| `beforeend` | Inside (end) | Append inside | ✅ Yes | Append children |
| `afterbegin` | Inside (start) | Prepend inside | ✅ Yes | Prepend children |
| `delete` | Element itself | Remove from DOM | N/A | Dismiss/delete |
| `none` | N/A | No swap | N/A | Track events |

---

## Related Resources

- **HTMX Official Docs:** https://htmx.org/attributes/hx-swap/
- **OBCMS Instant UI Guide:** `/docs/improvements/instant_ui_improvements_plan.md`
- **Work Items Fix:** `/docs/improvements/UI/WORK_ITEMS_HTMX_SWAP_FIX.md`
- **CLAUDE.md Guidelines:** `/CLAUDE.md` (Instant UI section)

---

## Quick Reference Card

**Need to replace 1 element?** → `outerHTML`
**Need to update content inside?** → `innerHTML`
**Need to insert multiple siblings?** → `afterend` or `beforebegin`
**Need to append/prepend inside?** → `beforeend` or `afterbegin`
**Need to remove element?** → `delete`
**Need to track without updating?** → `none`

**Remember:** `outerHTML` = **1-to-1 ONLY** ⚠️

For multiple elements, always use:
- `afterend` (insert after)
- `beforebegin` (insert before)
- `beforeend` (append inside)
- `afterbegin` (prepend inside)
