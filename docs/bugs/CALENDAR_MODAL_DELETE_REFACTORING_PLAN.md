# Calendar Modal Delete Functionality - Comprehensive Refactoring Plan

**Status:** ANALYSIS COMPLETE - READY FOR IMPLEMENTATION
**Created:** 2025-10-03
**Priority:** HIGH
**Complexity:** Moderate

---

## Executive Summary

The calendar modal delete functionality has a persistent bug where deleting tasks or events from calendar modal popups **does not work reliably**. Despite implementing the recommended fix (manual event dispatch with `hx-on::after-request`), the issue persists. This document provides a **deep root cause analysis** and **multiple solution approaches** with clear recommendations.

---

## Table of Contents

1. [Root Cause Analysis](#root-cause-analysis)
2. [Architectural Issues Identified](#architectural-issues-identified)
3. [Solution Approaches](#solution-approaches)
4. [Recommended Approach](#recommended-approach)
5. [Implementation Steps](#implementation-steps)
6. [Edge Cases & Risks](#edge-cases--risks)
7. [Testing Strategy](#testing-strategy)
8. [Success Criteria](#success-criteria)

---

## Root Cause Analysis

### The Core Problem: Event Listener Scope Mismatch

After analyzing the codebase thoroughly, the root cause is **NOT** HTMX event handling failure. The issue is **architectural**:

#### 1. **Modal Content Swap Destroys Event Context**

**Current Flow (BROKEN):**
```javascript
// Step 1: User clicks delete in modal
<form hx-post="/delete/123/"
      hx-target="#taskModalContent"     // ← Targets modal INNER content
      hx-swap="innerHTML"                // ← REPLACES entire modal content
      hx-on::after-request="...">        // ← This handler is ATTACHED to the <form>
```

**The Fatal Flaw:**
- The `hx-on::after-request` handler is attached to the `<form>` element
- The form is **inside** `#taskModalContent`
- When HTMX swaps `innerHTML` of `#taskModalContent`, it **DESTROYS the form element**
- Destroyed form = destroyed event handler = **handler never fires**

**Proof:**
```javascript
// Line 215 in staff_task_modal.html
<form hx-post="{% url 'common:staff_task_delete' task.id %}"
      hx-target="#taskModalContent"      // ← Targets PARENT of this form
      hx-swap="innerHTML"                 // ← Destroys THIS FORM
      hx-on::after-request="if(event.detail.successful) { ... }">  // ← DESTROYED before firing
```

**Timeline of Destruction:**
1. User clicks "Delete task" button → Form submits
2. Server responds with HTTP 200 (empty content)
3. HTMX receives response → Begins swap
4. HTMX swaps `#taskModalContent.innerHTML = ""`
5. **Form element is DESTROYED** (it's inside taskModalContent)
6. `hx-on::after-request` handler was attached to the form → **Handler is GONE**
7. Event never fires → Modal stays open → Calendar doesn't refresh

#### 2. **Target/Swap Configuration Anti-Pattern**

The configuration creates a **circular dependency**:
- Form is inside `#taskModalContent`
- Form targets `#taskModalContent` for swapping
- Swapping destroys the form
- Form destruction destroys event handlers

This is an **architectural anti-pattern** in HTMX applications.

#### 3. **Why It Works Elsewhere But Not Here**

**Task Board (WORKING):**
```javascript
// Task board uses different targets
document.body.addEventListener('task-board-refresh', function() {
    refreshBoardContainer();  // Refetches board data
});
```

**Key Difference:**
- Task board delete forms target `[data-task-id]` selectors (the individual card)
- Cards are **outside** the modal
- Destroying a card doesn't destroy event listeners on `document.body`

**Calendar Modal (BROKEN):**
- Calendar modal delete forms target `#taskModalContent` (the modal itself)
- Form is **inside** the target being swapped
- Self-destruction prevents event handlers from executing

---

## Architectural Issues Identified

### Issue 1: Self-Destructive HTMX Target Pattern

**Problem:** Form targets its own parent container for swapping.

**Impact:** Event handlers attached to the form never execute because the form is destroyed during swap.

**Prevalence:** This affects **both** task delete and event delete in calendar modals:
- `src/templates/common/partials/staff_task_modal.html:215`
- `src/templates/coordination/partials/event_modal.html:282`

### Issue 2: Inconsistent Event Handling Patterns

**Calendar Page Event Listeners:**
```javascript
// Line 568-570: oobc_calendar.html
['calendar-close-modal', 'task-modal-close'].forEach(function (eventName) {
    document.body.addEventListener(eventName, closeTaskModal);
});

// Line 601-607: task-board-refresh listener
document.body.addEventListener('task-board-refresh', function (event) {
    var calendar = window.__oobcCalendars['oobc-calendar'];
    if (calendar) {
        calendar.refetchEvents();
    }
});
```

**Backend Response:**
```python
# Line 3264: common/views/management.py
response["HX-Trigger"] = json.dumps({
    "task-board-refresh": True,
    "task-modal-close": True,
    "show-toast": f'Task "{task_title}" deleted successfully',
})
```

**The Mismatch:**
- Backend sends `HX-Trigger` headers correctly
- Frontend has event listeners set up correctly
- **BUT:** The form that triggers the request is destroyed before HTMX can process the headers

### Issue 3: Modal Architecture Fragility

**Current Modal System:**
```javascript
// openTaskModal loads content via HTMX
function openTaskModal(url) {
    htmx.ajax('GET', url, { target: '#taskModalContent', swap: 'innerHTML' });
}

// closeTaskModal clears content
function closeTaskModal() {
    taskModalContent.innerHTML = '';
}
```

**Problems:**
1. No state management - each modal load is isolated
2. Event handlers are ephemeral (destroyed with content)
3. No lifecycle hooks for cleanup/transition
4. Calendar refresh depends on events that may never fire

### Issue 4: No Debugging/Logging for Event Flow

**Missing Instrumentation:**
- No console logs for event dispatch
- No confirmation that `hx-on::after-request` fires
- No tracking of HX-Trigger header processing
- No validation that custom events reach listeners

**This makes debugging extremely difficult.**

---

## Solution Approaches

### Approach A: Event Handler on Modal Container (RECOMMENDED)

**Strategy:** Move event handler **outside** the swap target to prevent destruction.

**Implementation:**
```html
<!-- BEFORE (BROKEN): Handler inside swap target -->
<form hx-post="{% url 'common:staff_task_delete' task.id %}"
      hx-target="#taskModalContent"
      hx-swap="innerHTML"
      hx-on::after-request="...">  <!-- DESTROYED during swap -->
```

```html
<!-- AFTER (WORKING): Handler on modal wrapper -->
<div id="taskModal"
     hx-on::htmx:after-request="handleModalDelete(event)">  <!-- PERSISTS -->
    <div id="taskModalContent">
        <form hx-post="{% url 'common:staff_task_delete' task.id %}"
              hx-target="#taskModalContent"
              hx-swap="innerHTML">
            <!-- Form content -->
        </form>
    </div>
</div>

<script>
function handleModalDelete(event) {
    // Check if this was a delete request
    if (event.detail.successful &&
        event.detail.pathInfo.requestPath.includes('/delete/')) {
        console.log('Delete successful, closing modal and refreshing calendar');
        document.body.dispatchEvent(new CustomEvent('task-modal-close'));
        document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
    }
}
</script>
```

**Pros:**
- ✅ Handler persists through content swaps
- ✅ Minimal code changes required
- ✅ Follows HTMX best practices
- ✅ Works for both tasks and events
- ✅ Doesn't break existing functionality

**Cons:**
- ⚠️ Need to identify delete requests (check URL pattern)
- ⚠️ Requires updating modal wrapper template

**Complexity:** Low
**Risk:** Low

---

### Approach B: Use `hx-swap-oob` for Side Effects

**Strategy:** Return out-of-band swap that triggers side effects without destroying the form.

**Implementation:**
```python
# Backend: common/views/management.py
def staff_task_delete(request, task_id):
    task = get_object_or_404(StaffTask, pk=task_id)

    if request.POST.get("confirm") == "yes":
        task_title = task.title
        task.delete()

        if request.headers.get("HX-Request"):
            # Return empty content + out-of-band trigger element
            response = HttpResponse("""
                <div id="taskModalContent"></div>
                <div id="delete-trigger" hx-swap-oob="true" style="display:none;"
                     data-task-deleted="true" data-task-title="{title}">
                </div>
            """.format(title=task_title))
            return response
```

```javascript
// Frontend: Add MutationObserver to detect trigger
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
            if (node.id === 'delete-trigger' && node.dataset.taskDeleted) {
                console.log('Delete trigger detected');
                document.body.dispatchEvent(new CustomEvent('task-modal-close'));
                document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
                node.remove();
            }
        });
    });
});
observer.observe(document.body, { childList: true });
```

**Pros:**
- ✅ HTMX native feature (out-of-band swaps)
- ✅ No dependency on event timing
- ✅ Backend controls the trigger

**Cons:**
- ⚠️ Requires MutationObserver (more complex)
- ⚠️ Backend returns HTML instead of clean HTTP response
- ⚠️ Not as semantic/clean as event-based approach

**Complexity:** Moderate
**Risk:** Low-Moderate

---

### Approach C: Global HTMX Event Listener with Request Tracking

**Strategy:** Use global HTMX events and track delete requests.

**Implementation:**
```javascript
// Add to oobc_calendar.html
(function() {
    let pendingDeleteRequest = null;

    // Track delete form submissions
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        const url = event.detail.pathInfo.requestPath;
        if (url.includes('/delete/') && url.includes('/staff-task/')) {
            console.log('Delete request starting:', url);
            pendingDeleteRequest = {
                type: 'task',
                url: url,
                timestamp: Date.now()
            };
        }
    });

    // Handle successful delete responses
    document.body.addEventListener('htmx:afterRequest', function(event) {
        if (pendingDeleteRequest && event.detail.successful) {
            const timeSinceRequest = Date.now() - pendingDeleteRequest.timestamp;

            // Only process if request was recent (< 2 seconds)
            if (timeSinceRequest < 2000) {
                console.log('Delete completed successfully');
                document.body.dispatchEvent(new CustomEvent('task-modal-close'));
                document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
                pendingDeleteRequest = null;
            }
        }
    });
})();
```

**Pros:**
- ✅ Uses global HTMX events (always fire)
- ✅ No template changes needed
- ✅ Works for all delete operations
- ✅ Easy to add logging/debugging

**Cons:**
- ⚠️ Relies on URL pattern matching (fragile)
- ⚠️ State management can be tricky
- ⚠️ Timing-dependent (2-second window)

**Complexity:** Moderate
**Risk:** Moderate

---

### Approach D: Dedicated Delete Endpoint with JavaScript Response

**Strategy:** Separate delete endpoint that returns JavaScript to execute.

**Implementation:**
```python
# Backend: New endpoint
def staff_task_delete_modal(request, task_id):
    """Delete task from calendar modal - returns JavaScript."""
    task = get_object_or_404(StaffTask, pk=task_id)

    if request.POST.get("confirm") == "yes":
        task_title = task.title
        task.delete()

        # Return JavaScript that executes in browser
        return HttpResponse(f"""
            <script>
                console.log('Task deleted: {task_title}');
                document.getElementById('taskModalContent').innerHTML = '';
                document.body.dispatchEvent(new CustomEvent('task-modal-close'));
                document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
                if (window.showToast) {{
                    window.showToast({{
                        message: 'Task "{task_title}" deleted successfully',
                        level: 'success'
                    }});
                }}
            </script>
        """, content_type="text/html")
```

```html
<!-- Frontend: Use new endpoint -->
<form hx-post="{% url 'common:staff_task_delete_modal' task.id %}"
      hx-target="#taskModalContent"
      hx-swap="innerHTML">
```

**Pros:**
- ✅ Guaranteed execution (JavaScript always runs)
- ✅ Simple to understand
- ✅ Easy to debug (console.log inline)
- ✅ No event timing issues

**Cons:**
- ❌ Security concerns (XSS if task_title not escaped)
- ❌ Not RESTful/semantic
- ❌ Mixes backend logic with frontend behavior
- ❌ Doesn't scale well (anti-pattern)

**Complexity:** Low
**Risk:** High (security)

---

### Approach E: Alpine.js Modal State Management

**Strategy:** Replace vanilla JS modal with Alpine.js for reactive state management.

**Implementation:**
```html
<!-- Modal with Alpine.js -->
<div x-data="calendarModal()"
     x-show="open"
     @task-deleted.window="handleDelete($event)">
    <div id="taskModalContent" x-html="content"></div>
</div>

<script>
function calendarModal() {
    return {
        open: false,
        content: '',

        openModal(url) {
            fetch(url)
                .then(r => r.text())
                .then(html => {
                    this.content = html;
                    this.open = true;
                });
        },

        handleDelete(event) {
            console.log('Task deleted:', event.detail);
            this.content = '';
            this.open = false;

            // Refresh calendar
            const calendar = window.__oobcCalendars['oobc-calendar'];
            if (calendar) calendar.refetchEvents();
        }
    }
}
</script>
```

**Pros:**
- ✅ Proper state management
- ✅ Reactive by design
- ✅ Clean separation of concerns
- ✅ Modern approach

**Cons:**
- ❌ Requires adding Alpine.js dependency
- ❌ Significant refactoring required
- ❌ Learning curve for team
- ❌ Overkill for this specific issue

**Complexity:** High
**Risk:** Moderate (major refactor)

---

## Recommended Approach

### **PRIMARY: Approach A - Event Handler on Modal Container**

**Rationale:**
1. **Lowest complexity** - Minimal code changes required
2. **Lowest risk** - Doesn't break existing functionality
3. **Best practices** - Follows HTMX documentation recommendations
4. **Maintainable** - Easy to understand for future developers
5. **Scalable** - Works for both tasks and events with same pattern

**Confidence:** HIGH (95%)

### **FALLBACK: Approach C - Global HTMX Event Listener**

If Approach A proves insufficient (edge cases), use Approach C as fallback.

**Rationale:**
1. No template changes needed
2. Works globally for all delete operations
3. Easy to add comprehensive logging

**Confidence:** MODERATE (75%)

---

## Implementation Steps

### Phase 1: Update Modal Wrapper Template

**File:** `src/templates/common/components/task_modal.html`

**Current Structure:**
```html
<div id="taskModal" class="...">
    <div id="taskModalContent"></div>
</div>
```

**Updated Structure:**
```html
<div id="taskModal"
     class="..."
     hx-on::htmx:after-request="if(event.detail.successful && event.detail.pathInfo.requestPath.includes('/delete/')) { console.log('Delete detected in modal'); document.body.dispatchEvent(new CustomEvent('task-modal-close')); document.body.dispatchEvent(new CustomEvent('task-board-refresh')); }">
    <div id="taskModalContent"></div>
</div>
```

**Changes:**
- Add `hx-on::htmx:after-request` to the modal wrapper (outside swap target)
- Check if request was successful AND URL contains `/delete/`
- Dispatch both `task-modal-close` and `task-board-refresh` events
- Add console.log for debugging

### Phase 2: Remove Redundant Event Handlers from Forms

**Files to Update:**
1. `src/templates/common/partials/staff_task_modal.html:215`
2. `src/templates/coordination/partials/event_modal.html:282`

**Current (BROKEN):**
```html
<form hx-post="{% url 'common:staff_task_delete' task.id %}"
      hx-target="#taskModalContent"
      hx-swap="innerHTML"
      hx-on::after-request="if(event.detail.successful) { document.body.dispatchEvent(new CustomEvent('task-modal-close')); document.body.dispatchEvent(new CustomEvent('task-board-refresh')); }">
```

**Updated (CLEAN):**
```html
<form hx-post="{% url 'common:staff_task_delete' task.id %}"
      hx-target="#taskModalContent"
      hx-swap="innerHTML">
```

**Rationale:** Handler is now on modal wrapper, so form-level handler is redundant and broken.

### Phase 3: Add Comprehensive Logging

**File:** `src/templates/common/oobc_calendar.html`

**Add Debug Logging:**
```javascript
// Add after line 607 (existing task-board-refresh listener)
document.body.addEventListener('task-modal-close', function(event) {
    console.log('task-modal-close event received', event);
});

document.body.addEventListener('task-board-refresh', function(event) {
    console.log('task-board-refresh event received', event);
});

// Add global HTMX event logging for delete operations
document.body.addEventListener('htmx:beforeRequest', function(event) {
    if (event.detail.pathInfo.requestPath.includes('/delete/')) {
        console.log('DELETE request started:', event.detail.pathInfo.requestPath);
    }
});

document.body.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.pathInfo.requestPath.includes('/delete/')) {
        console.log('DELETE request completed:', {
            successful: event.detail.successful,
            url: event.detail.pathInfo.requestPath,
            status: event.detail.xhr.status
        });
    }
});
```

### Phase 4: Update Backend Logging

**File:** `src/common/views/management.py`

**Add Detailed Logging:**
```python
def staff_task_delete(request, task_id):
    """Delete a staff task."""
    logger.info(f"DELETE request received for task {task_id}")
    logger.info(f"Request headers: {dict(request.headers)}")

    task = get_object_or_404(StaffTask, pk=task_id)

    if request.POST.get("confirm") == "yes":
        task_title = task.title
        logger.info(f"Deleting task: {task_title} (ID: {task_id})")
        task.delete()
        logger.info(f"Task {task_title} deleted successfully")

        if request.headers.get("HX-Request"):
            response = HttpResponse("")
            response["HX-Trigger"] = json.dumps({
                "task-board-refresh": True,
                "task-modal-close": True,
                "show-toast": f'Task "{task_title}" deleted successfully',
            })
            logger.info(f"Returning HTMX response with triggers: {response['HX-Trigger']}")
            return response

    logger.warning(f"Task deletion not confirmed for task {task_id}")
    # ... rest of function
```

### Phase 5: Testing & Validation

**Test Cases:**
1. Delete task from calendar modal
2. Delete event from calendar modal
3. Verify modal closes automatically
4. Verify calendar refreshes (item disappears)
5. Verify toast notification appears
6. Check browser console for logs
7. Test with slow network (throttling)
8. Test with browser DevTools Network tab open

---

## Edge Cases & Risks

### Edge Case 1: Multiple Rapid Deletes

**Scenario:** User clicks delete multiple times rapidly.

**Risk:** Events may fire multiple times, causing multiple refreshes.

**Mitigation:**
```javascript
// Add debouncing to refresh handler
let refreshTimeout = null;
document.body.addEventListener('task-board-refresh', function(event) {
    clearTimeout(refreshTimeout);
    refreshTimeout = setTimeout(function() {
        var calendar = window.__oobcCalendars['oobc-calendar'];
        if (calendar) {
            calendar.refetchEvents();
        }
    }, 200);
});
```

### Edge Case 2: Network Failure During Delete

**Scenario:** Delete request fails due to network error.

**Risk:** Modal stays open, user confused about state.

**Mitigation:** Already handled by global error handlers in `base.html:706-728`

### Edge Case 3: Permission Denied

**Scenario:** User lacks permission to delete.

**Risk:** Backend returns 403, modal shows error but doesn't close.

**Mitigation:**
```javascript
// Update modal wrapper handler
hx-on::htmx:after-request="
    if (event.detail.pathInfo.requestPath.includes('/delete/')) {
        if (event.detail.successful) {
            console.log('Delete successful');
            document.body.dispatchEvent(new CustomEvent('task-modal-close'));
            document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
        } else {
            console.error('Delete failed:', event.detail.xhr.status);
            // Modal stays open to show error message
        }
    }
"
```

### Edge Case 4: Browser Back Button

**Scenario:** User deletes item, then hits back button.

**Risk:** Calendar may show stale data.

**Mitigation:** Calendar already uses `events` function that fetches fresh data on every render.

### Edge Case 5: Concurrent Edits

**Scenario:** Two users delete the same task simultaneously.

**Risk:** 404 error for second delete.

**Mitigation:** Django's `get_object_or_404` already handles this - returns 404 response.

---

## Testing Strategy

### Unit Tests (Backend)

**File:** `src/common/tests/test_views.py`

```python
class StaffTaskDeleteTestCase(TestCase):
    def test_delete_task_with_htmx_request(self):
        """Test task deletion via HTMX returns correct headers."""
        task = StaffTask.objects.create(title="Test Task")

        response = self.client.post(
            reverse('common:staff_task_delete', args=[task.id]),
            data={'confirm': 'yes'},
            headers={'HX-Request': 'true'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('HX-Trigger', response.headers)

        triggers = json.loads(response['HX-Trigger'])
        self.assertIn('task-board-refresh', triggers)
        self.assertIn('task-modal-close', triggers)
        self.assertIn('show-toast', triggers)

        # Verify task was deleted
        self.assertFalse(StaffTask.objects.filter(pk=task.id).exists())
```

### Integration Tests (Selenium)

**File:** `src/tests/selenium/test_calendar_modal_delete.py`

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CalendarModalDeleteTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)

    def test_delete_task_from_calendar_modal(self):
        """Test deleting task from calendar modal closes modal and refreshes."""
        # Navigate to calendar
        self.browser.get(f'{self.live_server_url}/oobc-management/calendar/')

        # Click on a task in calendar
        task_event = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'fc-event'))
        )
        task_event.click()

        # Wait for modal to open
        modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, 'taskModal'))
        )

        # Click delete button
        delete_btn = self.browser.find_element(By.CSS_SELECTOR, '[data-delete-trigger]')
        delete_btn.click()

        # Confirm deletion
        confirm_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-delete-confirm] button[type="submit"]'))
        )
        confirm_btn.click()

        # Wait for modal to close
        self.wait.until(
            EC.invisibility_of_element_located((By.ID, 'taskModal'))
        )

        # Verify modal is hidden
        modal_classes = self.browser.find_element(By.ID, 'taskModal').get_attribute('class')
        self.assertIn('hidden', modal_classes)

        # Verify calendar refreshed (task should be gone)
        # This requires checking FullCalendar's internal state or DOM
        events = self.browser.execute_script("""
            var calendar = window.__oobcCalendars['oobc-calendar'];
            return calendar ? calendar.getEvents().length : -1;
        """)
        self.assertGreaterEqual(events, 0)  # Calendar has events array
```

### Manual Testing Checklist

**Before Release:**
- [ ] Delete task from calendar modal (Chrome)
- [ ] Delete task from calendar modal (Firefox)
- [ ] Delete task from calendar modal (Safari)
- [ ] Delete event from calendar modal (Chrome)
- [ ] Delete event from calendar modal (Firefox)
- [ ] Delete event from calendar modal (Safari)
- [ ] Verify modal closes within 500ms
- [ ] Verify calendar refreshes within 1 second
- [ ] Verify toast notification appears
- [ ] Check browser console for errors
- [ ] Test with slow network (Throttling: Slow 3G)
- [ ] Test with fast network (No throttling)
- [ ] Test with Network tab open (DevTools)
- [ ] Test rapid delete clicks (spam prevention)
- [ ] Test delete without permission (403 handling)
- [ ] Test delete non-existent task (404 handling)

---

## Success Criteria

### Functional Requirements (MUST PASS)

1. ✅ **Modal closes automatically** after successful delete (< 500ms)
2. ✅ **Calendar refreshes** to remove deleted item (< 1 second)
3. ✅ **Toast notification** appears confirming deletion
4. ✅ **No JavaScript errors** in browser console
5. ✅ **Database record deleted** (verified in admin)
6. ✅ **Works for both tasks and events** (same pattern)
7. ✅ **Works across browsers** (Chrome, Firefox, Safari)

### Non-Functional Requirements (SHOULD PASS)

8. ✅ **Response time < 200ms** (server-side delete)
9. ✅ **UI update < 1 second** (client-side refresh)
10. ✅ **No full page reload** (HTMX instant UI)
11. ✅ **Accessible** (keyboard navigation, screen readers)
12. ✅ **Mobile-friendly** (touch events work)

### Code Quality Requirements

13. ✅ **No code duplication** (DRY principle)
14. ✅ **Comprehensive logging** (debug-friendly)
15. ✅ **Error handling** (graceful degradation)
16. ✅ **Unit tests pass** (backend delete logic)
17. ✅ **Integration tests pass** (Selenium E2E)

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review this plan with team
- [ ] Create feature branch: `fix/calendar-modal-delete-refactor`
- [ ] Back up current implementation (git stash or commit)

### Implementation
- [ ] Update modal wrapper template (`task_modal.html`)
- [ ] Remove redundant handlers from task modal (`staff_task_modal.html`)
- [ ] Remove redundant handlers from event modal (`event_modal.html`)
- [ ] Add comprehensive logging to calendar page (`oobc_calendar.html`)
- [ ] Update backend logging (`management.py` and `coordination/views.py`)

### Testing
- [ ] Write unit tests for delete endpoints
- [ ] Write Selenium integration tests
- [ ] Run manual testing checklist (all browsers)
- [ ] Fix any issues found during testing

### Documentation
- [ ] Update `CALENDAR_MODAL_DELETE_BUG.md` with resolution
- [ ] Add code comments explaining the fix
- [ ] Update `CLAUDE.md` if needed (HTMX patterns)

### Deployment
- [ ] Create pull request with detailed description
- [ ] Code review by team member
- [ ] Merge to main branch
- [ ] Deploy to staging environment
- [ ] Verify fix in staging
- [ ] Deploy to production
- [ ] Monitor error logs for 24 hours

---

## Appendix: Alternative Patterns Considered

### Pattern 1: Return HX-Redirect Header

**Concept:** After delete, redirect to calendar page.

**Rejected Because:**
- Full page reload (not instant UI)
- Loses scroll position
- Worse UX than current approach

### Pattern 2: WebSocket Push Notification

**Concept:** Server pushes delete event via WebSocket.

**Rejected Because:**
- Overkill for single-user action
- Requires WebSocket infrastructure
- More complex than necessary

### Pattern 3: Polling Calendar Endpoint

**Concept:** Poll calendar data every N seconds.

**Rejected Because:**
- Inefficient (unnecessary requests)
- Delayed feedback (user waits for poll)
- Not instant UI

---

## References

### HTMX Documentation
- [Events & Callbacks](https://htmx.org/docs/#events)
- [Request Headers](https://htmx.org/docs/#request-headers)
- [Response Headers](https://htmx.org/docs/#response-headers)
- [Out of Band Swaps](https://htmx.org/docs/#oob_swaps)

### FullCalendar Documentation
- [refetchEvents()](https://fullcalendar.io/docs/Calendar-refetchEvents)
- [Event Object](https://fullcalendar.io/docs/event-object)

### Related Issues
- `docs/bugs/CALENDAR_MODAL_DELETE_BUG.md` - Original bug report
- `docs/improvements/instant_ui_improvements_plan.md` - Instant UI standards

---

**Last Updated:** 2025-10-03
**Next Review:** After implementation
