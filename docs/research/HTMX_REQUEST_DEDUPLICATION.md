# HTMX Request Deduplication: Best Practices for Dynamic UIs

**Research Summary: Preventing Duplicate Requests and Target Errors in HTMX Applications**

*Priority: HIGH | Complexity: Moderate | Prerequisites: HTMX fundamentals*

---

## Executive Summary

This document provides actionable patterns for preventing duplicate HTMX requests and target errors in dynamic user interfaces, with specific focus on Work Items tree use cases. Based on HTMX documentation and community best practices, this guide covers:

1. **Request Deduplication** - Preventing duplicate requests using trigger modifiers
2. **Target Error Prevention** - Strategies to avoid `htmx:targetError` events
3. **State Synchronization** - Keeping UI state consistent across interactions
4. **Error Recovery** - Graceful handling of failures with rollback patterns

**Key Finding:** Most duplicate request and target error issues can be prevented with proper use of HTMX's built-in trigger modifiers (`once`, `throttle`, `debounce`) and synchronization strategies (`hx-sync`).

---

## 1. HTMX Trigger Modifiers Reference

### 1.1 Core Trigger Modifiers

HTMX provides several modifiers to control when and how requests are triggered:

| Modifier | Behavior | Use Case | Example |
|----------|----------|----------|---------|
| `once` | Trigger only once, then stop listening | Initial load, one-time expansion | `hx-trigger="click once"` |
| `throttle` | Delay after event, ignore events during delay | Rate limiting sustained activity | `hx-trigger="input throttle:500ms"` |
| `delay` (debounce) | Wait for pause in events before triggering | Search-as-you-type | `hx-trigger="keyup delay:300ms"` |
| `from:<selector>` | Listen to events from another element | Global events, custom triggers | `hx-trigger="custom-event from:body"` |
| `changed` | Only trigger if value changed | Form inputs | `hx-trigger="keyup changed"` |
| `queue` | Queue events for sequential processing | Ordered operations | `hx-trigger="click queue:last"` |

---

### 1.2 Detailed Modifier Explanations

#### `once` - Prevent Repeat Requests

**When to Use:**
- Tree node expansion (load children once)
- Initial data loading
- One-time user actions

**Example:**
```html
<!-- Load children only once, never again -->
<button
    hx-get="/api/work-items/{{ item.id }}/children/"
    hx-trigger="click once"
    hx-target="#children-{{ item.id }}"
    hx-swap="innerHTML">
    Expand
</button>
```

**Why It Works:**
- HTMX stops listening to the event after first trigger
- Perfect for lazy-loading content that doesn't change
- Prevents duplicate API calls on repeated clicks

**Limitation:**
- Cannot re-trigger even if needed (e.g., refresh)
- Use `hx-sync` if you need re-triggering with protection

---

#### `throttle` - Rate Limiting During Sustained Activity

**When to Use:**
- Scroll events
- Resize events
- Real-time updates with high frequency

**Example:**
```html
<!-- Throttle infinite scroll requests -->
<div
    hx-get="/api/work-items/?page=2"
    hx-trigger="scroll throttle:500ms"
    hx-target="#work-items-list"
    hx-swap="beforeend">
</div>
```

**Behavior:**
```
User scrolls continuously:
Event → [500ms delay] → Request
Event → Ignored (still in delay)
Event → Ignored (still in delay)
[500ms passes] → Request (if event occurred during delay)
```

**Why It Works:**
- Ensures minimum time between requests
- Prevents request spam during sustained activity
- Still responds to activity, just at controlled rate

---

#### `delay` (Debouncing) - Wait for User to Finish

**When to Use:**
- Search-as-you-type
- Form validation
- Any input where you want to wait for pause

**Example:**
```html
<!-- Search with debounce -->
<input
    type="text"
    name="search"
    hx-get="/api/work-items/search/"
    hx-trigger="keyup changed delay:300ms"
    hx-target="#search-results"
    placeholder="Search work items...">
```

**Behavior:**
```
User types "project":
'p' → [300ms timer starts]
'r' → [timer resets]
'o' → [timer resets]
'j' → [timer resets]
'e' → [timer resets]
'c' → [timer resets]
't' → [timer resets]
[300ms passes with no typing] → Request sent
```

**Why It Works:**
- Only triggers after user stops typing
- Reduces API calls from 7 to 1 in example above
- Improves performance and reduces server load

**Best Practice:**
```html
<!-- Combine 'changed' with 'delay' -->
<input
    hx-trigger="keyup changed delay:300ms"
    ...>
```
This prevents requests when value hasn't actually changed (e.g., arrow keys, ctrl).

---

### 1.3 Combining Modifiers

You can combine multiple modifiers for precise control:

```html
<!-- Search: Only on change, debounced, with throttle fallback -->
<input
    hx-get="/search/"
    hx-trigger="keyup changed delay:300ms, scroll throttle:500ms"
    hx-target="#results">
```

---

## 2. Request Synchronization with `hx-sync`

### 2.1 Overview

The `hx-sync` attribute coordinates AJAX requests to prevent race conditions and duplicate requests.

**Syntax:**
```html
<div hx-sync="SELECTOR:STRATEGY">
```

### 2.2 Synchronization Strategies

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `drop` | Ignore new request if one in flight (default) | Prevent double-clicks |
| `abort` | Cancel in-flight request, start new one | Search (latest query wins) |
| `replace` | Queue new request, cancel pending | Form submission |
| `queue` | Execute all requests sequentially | Ordered operations |

---

#### Strategy: `drop` (Default)

**Behavior:** Ignore new requests while one is in flight.

**Example:**
```html
<!-- Prevent double-click on expand button -->
<button
    hx-get="/api/work-items/{{ item.id }}/children/"
    hx-sync="this:drop"
    hx-target="#children-{{ item.id }}">
    Expand
</button>
```

**Use When:**
- Button clicks that shouldn't be repeated
- Expanding/collapsing UI elements
- Any action where first request is what matters

---

#### Strategy: `abort`

**Behavior:** Cancel current request, start new one immediately.

**Example:**
```html
<!-- Search: Latest query wins, abort old searches -->
<input
    hx-get="/api/work-items/search/"
    hx-trigger="keyup delay:300ms"
    hx-sync="this:abort"
    hx-target="#results">
```

**Use When:**
- Search interfaces (latest query most relevant)
- Filters that change frequently
- Real-time updates where latest data matters

**Why It Works:**
```
User types "project":
"pro" → Request A starts
[User continues typing]
"proj" → Request A aborted, Request B starts
"proje" → Request B aborted, Request C starts
"project" → Request C aborted, Request D starts
[300ms delay]
Request D completes → Shows "project" results
```

---

#### Strategy: `replace`

**Behavior:** Abort current request if another occurs while it's in flight.

**Example:**
```html
<!-- Form submission -->
<form
    hx-post="/api/work-items/"
    hx-sync="this:replace"
    hx-target="#work-items-list">
    ...
</form>
```

**Difference from `abort`:**
- `abort`: New request cancels old and starts immediately
- `replace`: New request waits until old completes, then replaces it

---

#### Strategy: `queue`

**Behavior:** Queue requests for sequential execution.

**Sub-strategies:**
- `queue:first` - Queue first request seen while one in flight
- `queue:last` - Queue last request seen while one in flight
- `queue:all` - Queue all requests

**Example:**
```html
<!-- Queue all delete operations (order matters) -->
<button
    hx-delete="/api/work-items/{{ item.id }}/"
    hx-sync="this:queue:all"
    hx-target="closest .work-item-row">
    Delete
</button>
```

**Use When:**
- Operations that must execute in order
- Sequential updates (e.g., reordering items)
- Batch operations

---

### 2.3 Synchronization Scope

You can synchronize across multiple elements:

```html
<!-- Synchronize all buttons in this form -->
<form id="work-item-form">
    <button
        hx-post="/api/work-items/"
        hx-sync="#work-item-form:drop">
        Submit
    </button>

    <button
        hx-delete="/api/work-items/{{ item.id }}/"
        hx-sync="#work-item-form:drop">
        Delete
    </button>
</form>
```

All buttons with `hx-sync="#work-item-form:drop"` share the same request queue.

---

## 3. Target Error Prevention

### 3.1 What Causes `htmx:targetError`?

The `htmx:targetError` event fires when HTMX cannot find the target element specified in `hx-target`.

**Common Causes:**
1. Target element doesn't exist in DOM
2. Target element removed by previous swap
3. Typo in target selector
4. Target not yet rendered (timing issue)

---

### 3.2 Prevention Strategies

#### Strategy 1: Use Static Containers

**Problem:**
```html
<!-- BAD: Target might not exist -->
<button hx-get="/api/children/" hx-target="#dynamic-{{ item.id }}">
    Expand
</button>
<!-- Target created dynamically later -->
```

**Solution:**
```html
<!-- GOOD: Create static container upfront -->
<button hx-get="/api/children/" hx-target="#children-{{ item.id }}">
    Expand
</button>

<!-- Static container always exists -->
<div id="children-{{ item.id }}" style="display: none;"></div>
```

---

#### Strategy 2: Use Relative Selectors

Instead of specific IDs, use relative selectors that always work:

```html
<!-- GOOD: Relative selectors -->
<div class="work-item-row">
    <button
        hx-get="/api/children/"
        hx-target="next .children-container"
        hx-swap="innerHTML">
        Expand
    </button>

    <div class="children-container"></div>
</div>
```

**Available Relative Selectors:**
- `this` - The element itself
- `closest <selector>` - Closest ancestor matching selector
- `next <selector>` - Next sibling matching selector
- `previous <selector>` - Previous sibling matching selector
- `find <selector>` - First child matching selector

---

#### Strategy 3: Validate Targets Before Swap

Use `htmx:beforeSwap` to validate target exists:

```javascript
document.body.addEventListener('htmx:beforeSwap', function(event) {
    const target = event.detail.target;

    if (!target) {
        console.error('Target not found:', event.detail.requestConfig.target);
        event.preventDefault(); // Cancel swap
        return;
    }

    // Target exists, proceed
});
```

---

#### Strategy 4: Handle `htmx:targetError` Gracefully

Always provide fallback for target errors:

```javascript
document.body.addEventListener('htmx:targetError', function(event) {
    console.error('Target error:', {
        element: event.detail.element,
        selector: event.detail.target
    });

    // Fallback: Find alternative container
    const fallbackTarget = document.getElementById('main-content');
    if (fallbackTarget && event.detail.xhr) {
        fallbackTarget.innerHTML = event.detail.xhr.response;
    }

    // Or show error message
    showToast('Could not find target element. Please refresh the page.', 'error');
});
```

---

### 3.3 Work Items Tree Pattern

**Best Practice for Tree Expansion:**

```html
<!-- work_item_tree_row.html -->
<div class="work-item-row" data-work-item-id="{{ item.id }}">
    {% if item.has_children %}
        <button
            class="expand-btn"
            hx-get="{% url 'work_items:children' item.id %}"
            hx-trigger="click once"
            hx-target="#children-{{ item.id }}"
            hx-swap="innerHTML swap:200ms"
            hx-sync="this:drop"
            hx-indicator="#loading-{{ item.id }}">

            <i class="fas fa-chevron-right chevron-icon"></i>
            {{ item.title }}
        </button>

        <!-- Loading indicator -->
        <div id="loading-{{ item.id }}" class="htmx-indicator">
            <div class="skeleton-row"></div>
        </div>

        <!-- Static children container (ALWAYS exists) -->
        <div id="children-{{ item.id }}" class="children-container" style="display: none;"></div>
    {% else %}
        <div class="work-item-leaf">
            <i class="fas fa-file"></i>
            {{ item.title }}
        </div>
    {% endif %}
</div>
```

**Key Points:**
1. `hx-trigger="click once"` - Prevents duplicate requests
2. `hx-sync="this:drop"` - Ignore rapid clicks during request
3. Static `#children-{{ item.id }}` container always exists
4. Indicator with unique ID for loading feedback

---

## 4. State Synchronization Patterns

### 4.1 Out-of-Band (OOB) Swaps

Update multiple UI regions from a single response.

#### Basic OOB Pattern

**Server Response:**
```html
<!-- Primary target: Work item details -->
<div id="work-item-{{ item.id }}" class="work-item-row">
    {{ item.title }} - {{ item.status }}
</div>

<!-- OOB: Update parent counter -->
<div id="parent-count-{{ parent.id }}" hx-swap-oob="true">
    {{ parent.children_count }} children
</div>

<!-- OOB: Update breadcrumb -->
<div id="breadcrumb" hx-swap-oob="true">
    {% for ancestor in item.get_ancestors %}
        {{ ancestor.title }} /
    {% endfor %}
    {{ item.title }}
</div>
```

**Why It Works:**
- Single request updates multiple regions
- Maintains UI consistency
- No need for multiple follow-up requests

---

#### OOB Swap Strategies

```html
<!-- Replace entire element (default) -->
<div id="target" hx-swap-oob="true">New content</div>

<!-- Use specific swap strategy -->
<div id="target" hx-swap-oob="innerHTML">New content</div>
<div id="target" hx-swap-oob="beforeend">Append content</div>
<div id="target" hx-swap-oob="afterbegin">Prepend content</div>
<div id="target" hx-swap-oob="delete"><!-- Deletes #target --></div>
```

---

### 4.2 Custom Events for State Sync

#### Server-Triggered Events

Use `HX-Trigger` response header to trigger events:

**Django View:**
```python
from django.http import HttpResponse
import json

def update_work_item(request, item_id):
    item = WorkItem.objects.get(id=item_id)
    item.status = request.POST.get('status')
    item.save()

    response = render(request, 'work_item_row.html', {'item': item})

    # Trigger custom events
    response['HX-Trigger'] = json.dumps({
        'work-item-updated': {'id': item_id, 'status': item.status},
        'refresh-counters': True,
        'show-toast': 'Work item updated successfully'
    })

    return response
```

**Client-Side Event Listeners:**
```javascript
// Listen for work item updates
document.body.addEventListener('work-item-updated', function(event) {
    const detail = event.detail;
    console.log(`Work item ${detail.id} updated to ${detail.status}`);

    // Update UI elements
    updateStatusBadges(detail.id, detail.status);
    refreshParentNode(detail.id);
});

// Listen for counter refresh
document.body.addEventListener('refresh-counters', function(event) {
    // Refresh all stat cards
    htmx.trigger('#stats-container', 'refresh');
});

// Listen for toast notifications
document.body.addEventListener('show-toast', function(event) {
    showToast(event.detail.value, 'success');
});
```

---

#### Event Timing

Use different trigger headers for precise timing:

| Header | When It Fires | Use Case |
|--------|---------------|----------|
| `HX-Trigger` | As soon as response received | Immediate feedback |
| `HX-Trigger-After-Swap` | After content swapped into DOM | Update related elements |
| `HX-Trigger-After-Settle` | After animations complete | Final state updates |

**Example:**
```python
response['HX-Trigger'] = 'show-loading'  # Immediate
response['HX-Trigger-After-Swap'] = 'content-loaded'  # After swap
response['HX-Trigger-After-Settle'] = 'animation-complete'  # After settle
```

---

### 4.3 Client-Side State Management

#### LocalStorage for Persistent State

```javascript
// Save expanded work items
function saveExpandedState() {
    const expanded = Array.from(
        document.querySelectorAll('.work-item-row.expanded')
    ).map(row => row.dataset.workItemId);

    localStorage.setItem('work_items_expanded', JSON.stringify(expanded));
}

// Restore on page load
function restoreExpandedState() {
    const expanded = JSON.parse(
        localStorage.getItem('work_items_expanded') || '[]'
    );

    expanded.forEach(itemId => {
        const row = document.querySelector(`[data-work-item-id="${itemId}"]`);
        if (row) {
            const expandBtn = row.querySelector('.expand-btn');
            if (expandBtn) expandBtn.click();
        }
    });
}

// Auto-save on changes
document.body.addEventListener('htmx:afterSwap', saveExpandedState);

// Restore on load
document.addEventListener('DOMContentLoaded', restoreExpandedState);
```

---

## 5. Error Recovery Patterns

### 5.1 Optimistic UI with Rollback

**Pattern: Update UI immediately, revert on error**

```javascript
// Optimistic expand
function optimisticExpand(button) {
    const row = button.closest('.work-item-row');
    const chevron = button.querySelector('.chevron-icon');
    const childrenContainer = row.querySelector('.children-container');

    // Save current state for rollback
    const previousState = {
        chevronClass: chevron.className,
        containerDisplay: childrenContainer.style.display,
        rowClass: row.className
    };

    // Optimistic update (instant)
    chevron.classList.remove('fa-chevron-right');
    chevron.classList.add('fa-chevron-down');
    childrenContainer.style.display = 'block';
    row.classList.add('expanded');

    // Rollback on error
    button.addEventListener('htmx:responseError', function() {
        chevron.className = previousState.chevronClass;
        childrenContainer.style.display = previousState.containerDisplay;
        row.className = previousState.rowClass;

        showToast('Failed to load children. Please try again.', 'error');
    }, { once: true });

    // Also handle network errors
    button.addEventListener('htmx:sendError', function() {
        chevron.className = previousState.chevronClass;
        childrenContainer.style.display = previousState.containerDisplay;
        row.className = previousState.rowClass;

        showToast('Network error. Please check your connection.', 'error');
    }, { once: true });
}
```

---

### 5.2 Error Event Handling

#### HTMX Error Events

| Event | When It Fires | Detail Properties |
|-------|---------------|-------------------|
| `htmx:sendError` | Request failed to send (network error) | `xhr`, `error` |
| `htmx:responseError` | Server returned error (4xx, 5xx) | `xhr`, `response` |
| `htmx:targetError` | Target element not found | `target`, `element` |
| `htmx:beforeSwap` | Before swap (can prevent) | `shouldSwap`, `target` |

---

#### Global Error Handler

```javascript
// Global error handler
class HTMXErrorHandler {
    constructor() {
        this.setupListeners();
    }

    setupListeners() {
        // Network errors
        document.body.addEventListener('htmx:sendError', (e) => {
            this.handleNetworkError(e);
        });

        // Server errors
        document.body.addEventListener('htmx:responseError', (e) => {
            this.handleServerError(e);
        });

        // Target errors
        document.body.addEventListener('htmx:targetError', (e) => {
            this.handleTargetError(e);
        });

        // Validation before swap
        document.body.addEventListener('htmx:beforeSwap', (e) => {
            this.validateBeforeSwap(e);
        });
    }

    handleNetworkError(event) {
        console.error('Network error:', event.detail);

        showToast(
            'Network error. Please check your connection and try again.',
            'error'
        );

        // Optionally retry
        if (confirm('Network error. Retry request?')) {
            htmx.trigger(event.detail.elt, event.detail.triggerSpec.trigger);
        }
    }

    handleServerError(event) {
        const status = event.detail.xhr.status;
        const response = event.detail.xhr.response;

        console.error('Server error:', status, response);

        let message = 'Server error. Please try again.';

        if (status === 404) {
            message = 'Resource not found.';
        } else if (status === 403) {
            message = 'You do not have permission to perform this action.';
        } else if (status === 500) {
            message = 'Internal server error. Please contact support.';
        }

        showToast(message, 'error');
    }

    handleTargetError(event) {
        console.error('Target error:', {
            element: event.detail.element,
            selector: event.detail.target
        });

        // Try to find fallback target
        const fallback = document.querySelector('#main-content');
        if (fallback && event.detail.xhr) {
            fallback.innerHTML = `
                <div class="alert alert-error">
                    <p>Could not find target element. Content loaded here instead:</p>
                    ${event.detail.xhr.response}
                </div>
            `;
        } else {
            showToast('Could not find target element. Please refresh the page.', 'error');
        }
    }

    validateBeforeSwap(event) {
        // Validate response before swapping
        const response = event.detail.xhr.response;

        // Check if response is empty
        if (!response || response.trim() === '') {
            console.warn('Empty response, preventing swap');
            event.detail.shouldSwap = false;
            showToast('No content to display.', 'warning');
            return;
        }

        // Check if target exists
        if (!event.detail.target) {
            console.error('Target missing in beforeSwap');
            event.detail.shouldSwap = false;
            return;
        }

        // Custom validation logic
        if (response.includes('ERROR:')) {
            console.error('Error in response:', response);
            event.detail.shouldSwap = false;
            showToast('Server returned an error.', 'error');
            return;
        }
    }
}

// Initialize global error handler
const errorHandler = new HTMXErrorHandler();
```

---

### 5.3 Response Targets Extension

Use different targets for success vs error responses:

**Include Extension:**
```html
<script src="https://unpkg.com/htmx.org/dist/ext/response-targets.js"></script>
```

**Usage:**
```html
<div hx-ext="response-targets">
    <button
        hx-post="/api/work-items/"
        hx-target="#success-message"
        hx-target-4xx="#client-error"
        hx-target-5xx="#server-error">
        Submit
    </button>

    <div id="success-message"></div>
    <div id="client-error"></div>
    <div id="server-error"></div>
</div>
```

**Important:** Place `hx-ext="response-targets"` on parent element, not the button itself.

---

## 6. Work Items Tree Use Case: Complete Pattern

### 6.1 Requirements

For the Work Items tree, we need:

1. Prevent duplicate expand requests
2. Avoid target errors when toggling
3. Maintain expanded state consistency
4. Handle errors gracefully with rollback
5. Provide instant feedback (<50ms)

---

### 6.2 Implementation

**HTML Template:**
```html
<!-- work_item_tree_row.html -->
<div class="work-item-row" data-work-item-id="{{ item.id }}">
    {% if item.has_children %}
        <button
            class="expand-btn"
            hx-get="{% url 'work_items:children' item.id %}"
            hx-trigger="click once"
            hx-target="#children-{{ item.id }}"
            hx-swap="innerHTML swap:200ms"
            hx-sync="this:drop"
            hx-indicator="#loading-{{ item.id }}"
            onclick="optimisticExpand(this)"
            data-item-id="{{ item.id }}">

            <i class="fas fa-chevron-right chevron-icon transition-transform duration-150"></i>
            <span class="item-title">{{ item.title }}</span>
            <span class="item-count text-gray-500">({{ item.children_count }})</span>
        </button>

        <!-- Loading indicator (skeleton) -->
        <div id="loading-{{ item.id }}" class="htmx-indicator ml-8">
            <div class="skeleton-row animate-pulse">
                <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            </div>
        </div>

        <!-- Static children container (ALWAYS exists) -->
        <div id="children-{{ item.id }}" class="children-container ml-8" style="display: none;"></div>
    {% else %}
        <div class="work-item-leaf">
            <i class="fas fa-file text-gray-400"></i>
            <span class="item-title">{{ item.title }}</span>
        </div>
    {% endif %}
</div>
```

**JavaScript:**
```javascript
// Optimistic expand with error recovery
function optimisticExpand(button) {
    const itemId = button.dataset.itemId;
    const row = button.closest('.work-item-row');
    const chevron = button.querySelector('.chevron-icon');
    const childrenContainer = document.getElementById(`children-${itemId}`);

    // Check if already expanded
    if (row.classList.contains('expanded')) {
        // Collapse (instant)
        chevron.classList.remove('fa-chevron-down');
        chevron.classList.add('fa-chevron-right');
        childrenContainer.style.display = 'none';
        row.classList.remove('expanded');
        return;
    }

    // Save state for rollback
    const previousState = {
        chevronClasses: chevron.className,
        containerDisplay: childrenContainer.style.display,
        rowClasses: row.className
    };

    // Optimistic UI update (instant - <50ms)
    chevron.classList.remove('fa-chevron-right');
    chevron.classList.add('fa-chevron-down');
    childrenContainer.style.display = 'block';
    row.classList.add('expanded', 'loading');

    // Rollback function
    const rollback = () => {
        chevron.className = previousState.chevronClasses;
        childrenContainer.style.display = previousState.containerDisplay;
        row.className = previousState.rowClasses;
    };

    // Error handling
    button.addEventListener('htmx:responseError', function(event) {
        rollback();
        showToast('Failed to load children. Please try again.', 'error');
    }, { once: true });

    button.addEventListener('htmx:sendError', function(event) {
        rollback();
        showToast('Network error. Please check your connection.', 'error');
    }, { once: true });

    button.addEventListener('htmx:targetError', function(event) {
        rollback();
        console.error('Target error:', event.detail);
        showToast('Could not find target element. Please refresh.', 'error');
    }, { once: true });

    // Success handling
    button.addEventListener('htmx:afterSwap', function(event) {
        row.classList.remove('loading');
        saveExpandedState();
    }, { once: true });
}

// State persistence
function saveExpandedState() {
    const expanded = Array.from(
        document.querySelectorAll('.work-item-row.expanded')
    ).map(row => row.dataset.workItemId);

    localStorage.setItem('work_items_expanded', JSON.stringify(expanded));
}

function restoreExpandedState() {
    const expanded = JSON.parse(
        localStorage.getItem('work_items_expanded') || '[]'
    );

    expanded.forEach(itemId => {
        const row = document.querySelector(`[data-work-item-id="${itemId}"]`);
        if (row && !row.classList.contains('expanded')) {
            const expandBtn = row.querySelector('.expand-btn');
            if (expandBtn) {
                // Trigger expansion
                expandBtn.click();
            }
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Restore expanded state
    restoreExpandedState();

    // Auto-save on any change
    document.body.addEventListener('htmx:afterSwap', saveExpandedState);
});
```

**CSS:**
```css
/* Smooth animations */
.chevron-icon {
    transition: transform 0.15s ease;
}

.work-item-row.expanded .chevron-icon {
    transform: rotate(90deg);
}

.children-container {
    transition: opacity 0.2s ease;
}

.work-item-row.loading .children-container {
    opacity: 0.5;
}

/* HTMX indicator */
.htmx-indicator {
    display: none;
}

.htmx-request .htmx-indicator {
    display: block;
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
    padding: 0.5rem 0;
}
```

---

## 7. Decision Matrix

### 7.1 Choosing the Right Modifier

| Scenario | Recommended Modifier | Reason |
|----------|---------------------|--------|
| Tree expansion (one-time load) | `click once` | Children loaded once, never again |
| Tree expansion (may refresh) | `click` + `hx-sync="this:drop"` | Can re-expand, but prevent doubles |
| Search input | `keyup changed delay:300ms` | Wait for typing pause, only on change |
| Filter dropdown | `change` | Trigger immediately on selection |
| Infinite scroll | `intersect once` | Load next page once when visible |
| Real-time updates | `every 5s` + `hx-sync="this:replace"` | Poll, but cancel old requests |
| Form submission | `submit` + `hx-sync="this:drop"` | Prevent double-submit |
| Delete button | `click` + `hx-sync="this:drop"` | Prevent accidental double-delete |

---

### 7.2 Choosing Synchronization Strategy

| Scenario | hx-sync Strategy | Reason |
|----------|-----------------|--------|
| Button click (expansion) | `this:drop` | Ignore rapid clicks |
| Search (typing) | `this:abort` | Latest query most relevant |
| Form submission | `this:drop` | First submission is what matters |
| Sequential operations | `this:queue:all` | Order matters |
| Real-time polling | `this:replace` | Latest data wins |

---

### 7.3 Target Selection Strategy

| Scenario | Target Strategy | Example |
|----------|----------------|---------|
| Known static element | ID selector | `hx-target="#children-123"` |
| Dynamic sibling | Relative selector | `hx-target="next .children-container"` |
| Parent container | Relative selector | `hx-target="closest .work-item-row"` |
| Self-replacement | `this` | `hx-target="this"` |
| Multiple targets | OOB swaps | `hx-swap-oob="true"` |

---

## 8. Testing Checklist

### 8.1 Duplicate Request Prevention

- [ ] Single click → One request
- [ ] Rapid clicks → One request (not multiple)
- [ ] Click during loading → Request ignored
- [ ] Search typing → Only final query triggers request
- [ ] Scroll events → Throttled to reasonable rate

### 8.2 Target Error Prevention

- [ ] All target containers exist in DOM
- [ ] Target selectors correct (no typos)
- [ ] Relative selectors work correctly
- [ ] OOB swap targets all exist
- [ ] `htmx:targetError` handled gracefully

### 8.3 State Synchronization

- [ ] UI updates immediately (optimistic)
- [ ] Server response updates UI correctly
- [ ] Error reverts optimistic changes
- [ ] Multiple UI regions update together (OOB)
- [ ] State persists across page reloads (LocalStorage)

### 8.4 Error Recovery

- [ ] Network error shows message and reverts
- [ ] Server error (4xx, 5xx) shows message and reverts
- [ ] Target error shows message and provides fallback
- [ ] User can retry failed operation
- [ ] No orphaned loading states

---

## 9. Common Pitfalls and Solutions

### Pitfall 1: Using `once` When You Need Re-triggering

**Problem:**
```html
<!-- Can't re-expand after collapse -->
<button hx-trigger="click once">Expand</button>
```

**Solution:**
```html
<!-- Can re-expand, but prevent doubles -->
<button hx-trigger="click" hx-sync="this:drop">Expand</button>
```

---

### Pitfall 2: Missing Static Containers

**Problem:**
```html
<!-- Target created dynamically - may not exist -->
<button hx-target="#dynamic-target">Load</button>
```

**Solution:**
```html
<!-- Always create static container -->
<button hx-target="#static-target">Load</button>
<div id="static-target" style="display: none;"></div>
```

---

### Pitfall 3: Not Combining `changed` with `delay`

**Problem:**
```html
<!-- Triggers on arrow keys, ctrl, etc. -->
<input hx-trigger="keyup delay:300ms">
```

**Solution:**
```html
<!-- Only triggers when value actually changes -->
<input hx-trigger="keyup changed delay:300ms">
```

---

### Pitfall 4: Forgetting Error Handlers

**Problem:**
```javascript
// Optimistic update, but no rollback on error
chevron.classList.add('fa-chevron-down');
```

**Solution:**
```javascript
// Always implement rollback
button.addEventListener('htmx:responseError', rollback, { once: true });
button.addEventListener('htmx:sendError', rollback, { once: true });
```

---

### Pitfall 5: OOB Extension Not on Parent

**Problem:**
```html
<!-- Extension on button doesn't work -->
<button hx-ext="response-targets" hx-target-error="#error">Submit</button>
```

**Solution:**
```html
<!-- Extension must be on parent -->
<div hx-ext="response-targets">
    <button hx-target-error="#error">Submit</button>
</div>
```

---

## 10. Resources

### Official Documentation
- [HTMX Trigger Attribute](https://htmx.org/attributes/hx-trigger/)
- [HTMX Sync Attribute](https://htmx.org/attributes/hx-sync/)
- [HTMX Events Reference](https://htmx.org/events/)
- [HTMX Response Targets Extension](https://htmx.org/extensions/response-targets/)

### OBCMS Documentation
- [Optimistic UI Pattern Quick Reference](../ui/OPTIMISTIC_UI_PATTERN_QUICK_REFERENCE.md)
- [Fast Tree UI Patterns](FAST_TREE_UI_PATTERNS.md)
- [Work Item Tree Implementation](../improvements/UI/WORK_ITEM_TREE_OPTIMISTIC_UI_IMPLEMENTATION.md)

### External Resources
- [HTMX GitHub Discussions](https://github.com/bigskysoftware/htmx/discussions)
- [Hypermedia Systems Book](https://hypermedia.systems/)
- [HTMX Examples](https://htmx.org/examples/)

---

## Conclusion

Preventing duplicate HTMX requests and target errors comes down to:

1. **Use the right trigger modifier:**
   - `once` for one-time operations
   - `delay` for debouncing user input
   - `throttle` for rate-limiting sustained events

2. **Use `hx-sync` to prevent race conditions:**
   - `drop` for ignoring duplicates
   - `abort` for latest-wins scenarios
   - `queue` when order matters

3. **Prevent target errors:**
   - Create static containers upfront
   - Use relative selectors
   - Handle `htmx:targetError` gracefully

4. **Implement proper error recovery:**
   - Optimistic UI with rollback
   - Listen to all error events
   - Provide clear user feedback

5. **Test thoroughly:**
   - Rapid clicks, slow networks, missing targets
   - Verify optimistic updates and rollback
   - Ensure state synchronization works

For Work Items tree specifically, use:
- `hx-trigger="click once"` for initial expansion
- Static `#children-{{ item.id }}` containers
- Optimistic UI with full error handling
- State persistence via LocalStorage

**Key Principle:** HTMX provides all the tools needed to prevent duplicate requests and target errors. Use them properly from the start, and your UI will be fast, consistent, and error-free.

---

*Research compiled: 2025-10-06*
*Based on: HTMX official documentation, community best practices, and OBCMS implementation patterns*
