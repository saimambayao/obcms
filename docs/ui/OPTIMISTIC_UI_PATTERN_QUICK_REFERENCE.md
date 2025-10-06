# Optimistic UI Pattern - Quick Reference Card

**For OBCMS Developers**
**Last Updated:** 2025-10-06

---

## What Is Optimistic UI?

**Definition:** Update the UI immediately when user performs an action, before waiting for server response.

**Goal:** Make interactions feel instant (< 50ms feedback) instead of slow (200-500ms delay).

**User Perception:** "This app is fast!" vs. "This app is slow..."

---

## When to Use Optimistic UI

### ✅ USE for:

- Expand/collapse operations (tree views, accordions)
- Form submissions (show success state immediately)
- Toggle switches (on/off states)
- Like/favorite buttons
- Quick edits (inline editing)
- Adding items to lists
- Deleting items from lists

### ❌ DON'T USE for:

- Critical operations (payments, legal confirmations)
- Operations that frequently fail
- Complex server-side validation
- Security-sensitive actions
- Operations with unpredictable outcomes

---

## The 3-Phase Pattern

### Phase 1: Instant Feedback (< 50ms)

**What to do:**
1. Update UI optimistically (assume success)
2. Show loading indicator
3. Disable interactive elements

**Example:**
```javascript
// BEFORE server request
function showOptimisticState() {
    button.disabled = true;
    icon.classList.add('fa-chevron-down');
    showSkeletonRow();
    showSpinner();
}
```

---

### Phase 2: Server Request (50-500ms)

**What to do:**
1. Send HTMX/AJAX request
2. Keep loading indicators visible
3. Keep elements disabled

**Example:**
```html
<button
    hx-post="/api/endpoint/"
    hx-indicator="#spinner"
    hx-disabled-elt="this">
    Action
</button>
```

---

### Phase 3: Server Response

**Success Path:**
```javascript
// AFTER successful response
function handleSuccess() {
    hideSpinner();
    hideSkeletonRow();
    showRealContent();
    button.disabled = false;
}
```

**Error Path:**
```javascript
// AFTER error response
function handleError() {
    revertOptimisticChanges();
    hideSpinner();
    hideSkeletonRow();
    showErrorMessage();
    button.disabled = false;
}
```

---

## HTMX Implementation Template

### HTML Template

```html
<!-- Button with optimistic UI -->
<button
    hx-get="/api/endpoint/{{ item.id }}/"
    hx-target="#target-{{ item.id }}"
    hx-swap="afterend swap:300ms"
    hx-indicator="#loading-indicator-{{ item.id }}"
    hx-disabled-elt="this"
    class="action-btn"
    data-item-id="{{ item.id }}">

    <!-- Icon (toggled optimistically) -->
    <i class="fas fa-chevron-right toggle-icon"></i>

    <!-- Loading indicator (hidden by default) -->
    <i id="loading-indicator-{{ item.id }}"
       class="fas fa-spinner fa-spin htmx-indicator"></i>
</button>

<!-- Target placeholder -->
<div id="target-{{ item.id }}" style="display: none;"></div>

<!-- Skeleton row (shown during loading) -->
<div id="skeleton-{{ item.id }}" class="skeleton-row" style="display: none;">
    <div class="animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-1/3"></div>
    </div>
</div>
```

---

### CSS

```css
/* Hide loading indicator by default */
.htmx-indicator {
    display: none;
}

/* Show during HTMX request */
.htmx-request .htmx-indicator {
    display: inline-block;
}

/* Hide main icon during loading */
.htmx-request .toggle-icon {
    display: none;
}

/* Skeleton animation */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-row {
    transition: opacity 200ms ease-in-out;
}
```

---

### JavaScript Event Handlers

```javascript
// Phase 1: BEFORE request (instant feedback)
document.body.addEventListener('htmx:beforeRequest', function(event) {
    const target = event.detail.target;
    const itemId = target.dataset.itemId;

    // INSTANT FEEDBACK (< 20ms)
    rotateIconDown(itemId);
    showSkeletonRow(itemId);
});

// Phase 2: AFTER successful response
document.body.addEventListener('htmx:afterSwap', function(event) {
    const target = event.detail.target;
    const itemId = extractItemId(target);

    // Clean up
    hideSkeletonRow(itemId);
    // Icon already rotated optimistically
});

// Phase 3: ERROR handling
document.body.addEventListener('htmx:sendError', function(event) {
    const target = event.detail.target;
    const itemId = extractItemId(target);

    // Revert optimistic changes
    rotateIconRight(itemId);
    hideSkeletonRow(itemId);
    showErrorToast('Request failed. Please try again.');
});

document.body.addEventListener('htmx:responseError', function(event) {
    const target = event.detail.target;
    const itemId = extractItemId(target);

    // Revert optimistic changes
    rotateIconRight(itemId);
    hideSkeletonRow(itemId);
    showErrorToast('Server error. Please try again.');
});
```

---

### Helper Functions

```javascript
// Show skeleton loading row
function showSkeletonRow(itemId) {
    const skeleton = document.getElementById(`skeleton-${itemId}`);
    if (skeleton) skeleton.style.display = '';
}

// Hide skeleton loading row
function hideSkeletonRow(itemId) {
    const skeleton = document.getElementById(`skeleton-${itemId}`);
    if (skeleton) skeleton.style.display = 'none';
}

// Rotate icon down (expanded state)
function rotateIconDown(itemId) {
    const button = document.querySelector(`[data-item-id="${itemId}"]`);
    const icon = button?.querySelector('.toggle-icon');
    if (icon) {
        icon.classList.remove('fa-chevron-right');
        icon.classList.add('fa-chevron-down');
    }
}

// Rotate icon right (collapsed state)
function rotateIconRight(itemId) {
    const button = document.querySelector(`[data-item-id="${itemId}"]`);
    const icon = button?.querySelector('.toggle-icon');
    if (icon) {
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-right');
    }
}

// Extract item ID from target element
function extractItemId(target) {
    if (target.id && target.id.startsWith('target-')) {
        return target.id.replace('target-', '');
    }
    return null;
}
```

---

## Skeleton Row Patterns

### Simple Skeleton (Single Line)

```html
<div class="skeleton-row animate-pulse">
    <div class="h-4 bg-gray-200 rounded w-1/3"></div>
</div>
```

### Card Skeleton (Multiple Lines)

```html
<div class="skeleton-row animate-pulse space-y-2">
    <div class="h-4 bg-gray-200 rounded w-3/4"></div>
    <div class="h-4 bg-gray-100 rounded w-1/2"></div>
    <div class="h-4 bg-gray-100 rounded w-1/4"></div>
</div>
```

### Table Row Skeleton

```html
<tr class="skeleton-row">
    <td colspan="7" class="px-4 py-3">
        <div class="flex items-center gap-2 animate-pulse">
            <div class="h-4 bg-gray-200 rounded w-1/3"></div>
            <div class="h-4 bg-gray-100 rounded w-20"></div>
        </div>
    </td>
</tr>
```

### List Item Skeleton

```html
<li class="skeleton-row animate-pulse">
    <div class="flex items-center gap-3 p-3">
        <div class="w-10 h-10 bg-gray-200 rounded-full"></div>
        <div class="flex-1 space-y-2">
            <div class="h-3 bg-gray-200 rounded w-2/3"></div>
            <div class="h-3 bg-gray-100 rounded w-1/3"></div>
        </div>
    </div>
</li>
```

---

## Loading Indicator Patterns

### Spinner Icon

```html
<i class="fas fa-spinner fa-spin htmx-indicator"></i>
```

### Pulse Dot

```html
<span class="htmx-indicator inline-block w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
```

### Progress Bar

```html
<div class="htmx-indicator w-full bg-gray-200 rounded-full h-1">
    <div class="bg-blue-600 h-1 rounded-full animate-pulse" style="width: 100%"></div>
</div>
```

### Text Indicator

```html
<span class="htmx-indicator text-sm text-gray-500">Loading...</span>
```

---

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Initial Visual Feedback | < 50ms | DevTools Performance tab |
| Perceived Load Time | < 500ms | User perception |
| Animation Duration | 200-300ms | CSS transition timing |
| Total Request Time | < 2s | Network tab |

**Golden Rule:** User should see feedback in < 50ms (feels instant)

---

## Accessibility Checklist

### Required ARIA Attributes

```html
<button aria-label="Expand/Collapse" hx-disabled-elt="this">
    <!-- HTMX automatically adds aria-busy="true" during requests -->
</button>
```

### Screen Reader Announcements

- ✅ Button label clear ("Expand/Collapse")
- ✅ Loading state announced (aria-busy)
- ✅ Disabled state announced (disabled attribute)
- ✅ Success/error announced (ARIA live regions)

### Keyboard Navigation

- ✅ Tab to button
- ✅ Space/Enter to activate
- ✅ Focus retained during loading
- ✅ Focus moved appropriately after success

---

## Common Pitfalls & Solutions

### Pitfall 1: Double-Click Issues

❌ **Problem:** User clicks multiple times during loading

✅ **Solution:** Use `hx-disabled-elt="this"` attribute

```html
<button hx-disabled-elt="this">Action</button>
```

---

### Pitfall 2: Icon Not Rotating

❌ **Problem:** Icon changes AFTER content loads (backward)

✅ **Solution:** Rotate icon in `htmx:beforeRequest` event

```javascript
document.body.addEventListener('htmx:beforeRequest', function(event) {
    rotateIconDown(itemId); // BEFORE request
});
```

---

### Pitfall 3: Skeleton Not Hiding

❌ **Problem:** Skeleton stays visible after content loads

✅ **Solution:** Hide skeleton in `htmx:afterSwap` event

```javascript
document.body.addEventListener('htmx:afterSwap', function(event) {
    hideSkeletonRow(itemId); // AFTER swap
});
```

---

### Pitfall 4: Error State Not Reverting

❌ **Problem:** Optimistic UI stays even after error

✅ **Solution:** Listen to both error events

```javascript
// Network error
document.body.addEventListener('htmx:sendError', revertOptimisticUI);

// Server error (4xx, 5xx)
document.body.addEventListener('htmx:responseError', revertOptimisticUI);
```

---

### Pitfall 5: No Loading Indicator

❌ **Problem:** No visual feedback during request

✅ **Solution:** Add spinner and use `hx-indicator` attribute

```html
<button hx-indicator="#spinner-123">
    <i class="toggle-icon"></i>
    <i id="spinner-123" class="fas fa-spinner fa-spin htmx-indicator"></i>
</button>
```

---

## Testing Checklist

### Manual Testing

- [ ] Click action → instant visual feedback (< 50ms)
- [ ] Loading indicator visible during request
- [ ] Button disabled during request (no double-click)
- [ ] Smooth transition after response (200-300ms)
- [ ] Error handling reverts optimistic changes
- [ ] Keyboard navigation works (Tab, Space, Enter)
- [ ] Screen reader announces states correctly

### Network Testing

- [ ] Fast network (< 100ms) → smooth
- [ ] Slow network (300ms) → loading indicator visible
- [ ] Offline (timeout) → error handled gracefully

### Browser Testing

- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## Code Review Checklist

**Before approving optimistic UI implementation:**

- [ ] HTMX attributes correct (`hx-indicator`, `hx-disabled-elt`)
- [ ] Loading indicators present (spinner, skeleton)
- [ ] CSS animations smooth (200-300ms)
- [ ] JavaScript event handlers complete (beforeRequest, afterSwap, errors)
- [ ] Error handling reverts optimistic changes
- [ ] Accessibility attributes present (aria-label, etc.)
- [ ] Skeleton rows match content structure
- [ ] Performance targets met (< 50ms feedback)
- [ ] Documentation updated
- [ ] Tests written/updated

---

## Examples in OBCMS

### Work Item Tree Expansion

**File:** `/src/templates/work_items/_work_item_tree_row.html`

**Features:**
- Instant chevron rotation
- Skeleton rows for children
- Spinning loading indicator
- Auto-disabled button
- Error recovery

**Reference:** See `docs/improvements/UI/WORK_ITEM_TREE_OPTIMISTIC_UI_IMPLEMENTATION.md`

---

### Future Examples (Planned)

**Project Central Portfolio Tree:**
- Apply same pattern to project hierarchy
- Reuse skeleton row templates

**MOA Organizational Hierarchy:**
- Apply same pattern to org chart
- Customize skeleton for org units

**Policy Recommendation Tree:**
- Apply same pattern to policy structure
- Customize skeleton for policy items

---

## Quick Start Template

**Copy-paste this to get started:**

```html
<!-- HTML -->
<button
    hx-get="/api/endpoint/{{ id }}/"
    hx-target="#target-{{ id }}"
    hx-swap="afterend swap:300ms"
    hx-indicator="#spinner-{{ id }}"
    hx-disabled-elt="this"
    data-item-id="{{ id }}">
    <i class="fas fa-chevron-right toggle-icon"></i>
    <i id="spinner-{{ id }}" class="fas fa-spinner fa-spin htmx-indicator"></i>
</button>

<div id="target-{{ id }}" style="display: none;"></div>
<div id="skeleton-{{ id }}" class="skeleton-row" style="display: none;">
    <div class="animate-pulse h-4 bg-gray-200 rounded w-1/3"></div>
</div>
```

```css
/* CSS */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: inline-block; }
.htmx-request .toggle-icon { display: none; }
.skeleton-row { transition: opacity 200ms; }
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.animate-pulse { animation: pulse 2s infinite; }
```

```javascript
// JavaScript
document.body.addEventListener('htmx:beforeRequest', function(e) {
    const id = e.detail.target.id.replace('target-', '');
    document.getElementById(`skeleton-${id}`).style.display = '';
});

document.body.addEventListener('htmx:afterSwap', function(e) {
    const id = e.detail.target.id.replace('target-', '');
    document.getElementById(`skeleton-${id}`).style.display = 'none';
});

document.body.addEventListener('htmx:sendError', function(e) {
    const id = e.detail.target.id.replace('target-', '');
    document.getElementById(`skeleton-${id}`).style.display = 'none';
    console.error('Request failed');
});
```

---

## Resources

**OBCMS Documentation:**
- [UI Components & Standards](OBCMS_UI_COMPONENTS_STANDARDS.md)
- [Work Item Tree Implementation](../improvements/UI/WORK_ITEM_TREE_OPTIMISTIC_UI_IMPLEMENTATION.md)
- [Before/After Comparison](../improvements/UI/WORK_ITEM_TREE_BEFORE_AFTER.md)

**External Resources:**
- [HTMX Documentation](https://htmx.org/docs/)
- [HTMX Loading Indicators](https://htmx.org/docs/#indicators)
- [HTMX Events Reference](https://htmx.org/events/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated:** 2025-10-06
**Maintainer:** OBCMS Development Team
**Version:** 1.0
