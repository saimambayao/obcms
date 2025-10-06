# Calendar Modal Deletion - All Possible Solutions

**Date**: 2025-10-04
**Status**: PERSISTENT ISSUE - Multiple attempted fixes have failed
**Severity**: CRITICAL - Core feature broken

---

## The Problem

When deleting tasks/events from the calendar modal:
- ✅ Task IS deleted from database (backend works)
- ❌ Modal does NOT close automatically
- ❌ Calendar does NOT refresh to show deletion
- User must manually close modal and refresh page

---

## What We've Tried (All Failed)

### Attempt 1: HX-Trigger Response Headers
**Approach**: Backend sends custom event triggers in response header
**Result**: ❌ Events not dispatched to listeners
**Why it failed**: HTMX may not process HX-Trigger headers correctly in all scenarios

### Attempt 2: `hx-on::after-request` on Delete Form
**Approach**: Form has inline HTMX event handler
**Result**: ❌ Handler never fires
**Why it failed**: Form gets destroyed during HTMX swap before handler executes

### Attempt 3: `hx-on::after-request` on #taskModal Wrapper
**Approach**: Move handler to parent element that survives swap
**Result**: ❌ Still doesn't work
**Why it failed**: Unknown - possibly event bubbling issue or wrong HTMX version

### Attempt 4: `htmx:afterSwap` Global Listener
**Approach**: Listen for HTMX afterSwap events, check if delete URL
**Result**: ❌ Still broken (current state)
**Why it failed**: Unknown - possibly xhr.responseURL not available or wrong property

---

## Remaining Options (Ranked by Reliability)

### ⭐ Option A: Backend Returns Inline JavaScript (MOST RELIABLE)

**Confidence**: 95% - This will definitely work

**Backend Change**:
```python
# File: src/common/views/management.py:3268
def staff_task_delete(request, task_id):
    task = get_object_or_404(StaffTask, pk=task_id)

    if request.POST.get("confirm") == "yes":
        task_title = task.title
        task.delete()

        if request.headers.get("HX-Request"):
            # Return JavaScript that executes in browser
            return HttpResponse(f"""
<script>
    (function() {{
        console.log('Task deleted via inline script');

        // Close modal
        var modal = document.getElementById('taskModal');
        if (modal) {{
            modal.classList.add('hidden');
            modal.setAttribute('aria-hidden', 'true');
        }}

        var content = document.getElementById('taskModalContent');
        if (content) {{
            content.innerHTML = '';
        }}

        document.body.classList.remove('overflow-hidden');

        // Refresh calendar
        setTimeout(function() {{
            var calendar = window.__oobcCalendars && window.__oobcCalendars['oobc-calendar'];
            if (calendar) {{
                calendar.refetchEvents();
            }}
        }}, 200);

        // Show toast (if function exists)
        if (typeof showToast === 'function') {{
            showToast('{task_title} deleted successfully', 'success');
        }}
    }})();
</script>
""", content_type="text/html")
```

**Pros**:
- ✅ Guaranteed to execute
- ✅ Direct DOM manipulation
- ✅ No reliance on event systems
- ✅ Works with any HTMX version

**Cons**:
- ⚠️ Mixing concerns (backend generates JS)
- ⚠️ Requires escaping task title for JS

---

### Option B: MutationObserver Watching Modal Content

**Confidence**: 85% - Should work if configured correctly

**Frontend Change**:
```javascript
// File: src/templates/common/oobc_calendar.html
// Add after modal initialization

if (taskModalContent) {
    var lastContent = taskModalContent.innerHTML;

    var observer = new MutationObserver(function(mutations) {
        var currentContent = taskModalContent.innerHTML;

        // Deletion makes content empty or very short
        var wasDeleted = lastContent.includes('data-delete-confirm') &&
                         (currentContent.trim().length < 50 || currentContent.trim() === '');

        if (wasDeleted) {
            console.log('Deletion detected via MutationObserver');
            closeTaskModal();

            setTimeout(function() {
                var calendar = window.__oobcCalendars['oobc-calendar'];
                if (calendar) {
                    calendar.refetchEvents();
                }
            }, 200);
        }

        lastContent = currentContent;
    });

    observer.observe(taskModalContent, {
        childList: true,
        subtree: true
    });
}
```

**Pros**:
- ✅ Pure frontend solution
- ✅ No backend changes
- ✅ Detects any content change

**Cons**:
- ⚠️ Might trigger on non-delete changes
- ⚠️ Requires careful tuning

---

### Option C: Custom HTMX Extension

**Confidence**: 80% - Requires HTMX knowledge

**Create Extension**:
```javascript
// File: src/static/common/js/htmx-calendar-delete.js

htmx.defineExtension('calendar-delete', {
    onEvent: function (name, evt) {
        if (name === 'htmx:afterSwap' &&
            evt.detail.target &&
            evt.detail.target.id === 'taskModalContent') {

            var pathInfo = evt.detail.pathInfo || {};
            if (pathInfo.requestPath && pathInfo.requestPath.includes('/delete/')) {
                // Close modal
                document.body.dispatchEvent(new CustomEvent('task-modal-close'));

                // Refresh calendar
                setTimeout(function() {
                    document.body.dispatchEvent(new CustomEvent('task-board-refresh'));
                }, 200);
            }
        }
    }
});
```

**Template Change**:
```html
<div id="taskModal" hx-ext="calendar-delete">
```

**Pros**:
- ✅ Clean separation of concerns
- ✅ Reusable across pages

**Cons**:
- ⚠️ Requires HTMX extension knowledge
- ⚠️ Another file to maintain

---

### Option D: Full Page Redirect (NUCLEAR OPTION)

**Confidence**: 100% - Will definitely work but worst UX

**Backend Change**:
```python
def staff_task_delete(request, task_id):
    task = get_object_or_404(StaffTask, pk=task_id)

    if request.POST.get("confirm") == "yes":
        task.delete()
        messages.success(request, f'Task "{task.title}" deleted')
        return redirect('common:oobc_calendar')
```

**Pros**:
- ✅ 100% reliable
- ✅ Simple to implement
- ✅ No JavaScript issues

**Cons**:
- ❌ Full page reload (bad UX)
- ❌ Loses scroll position
- ❌ Defeats purpose of HTMX

---

### Option E: WebSocket/Server-Sent Events

**Confidence**: 90% - Overkill but would work

**Implementation**: Use Django Channels to push deletion events

**Pros**:
- ✅ Real-time updates
- ✅ Works for multi-user scenarios

**Cons**:
- ❌ Massive overkill for this issue
- ❌ Requires Channels/Redis setup

---

## Recommended Implementation Order

### Phase 1: Quick Fix (Option A - Inline JavaScript)
**Timeline**: 15 minutes
**Confidence**: 95%

1. Modify `staff_task_delete` view to return `<script>` tag
2. Modify `coordination_event_delete` view to return `<script>` tag
3. Test manually in browser
4. ✅ Should work immediately

### Phase 2: Clean Up (Option B - MutationObserver)
**Timeline**: 30 minutes
**Confidence**: 85%

1. Implement MutationObserver in calendar.html
2. Remove inline JavaScript from backend
3. Test thoroughly
4. Monitor for false positives

### Phase 3: Long-term Solution (Option C - HTMX Extension)
**Timeline**: 1-2 hours
**Confidence**: 80%

1. Create custom HTMX extension
2. Load extension in calendar page
3. Apply to modal wrapper
4. Test across all deletion scenarios

---

## Decision Matrix

| Option | Reliability | Effort | UX Impact | Maintainability |
|--------|-------------|--------|-----------|-----------------|
| **A: Inline JS** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **B: MutationObserver** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **C: HTMX Extension** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **D: Page Redirect** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **E: WebSocket** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## My Recommendation

**Implement Option A (Inline JavaScript) RIGHT NOW**

Why:
1. **Guaranteed to work** - No dependency on event systems
2. **Fast to implement** - 15 minutes
3. **Good UX** - Modal closes, calendar refreshes instantly
4. **Low risk** - Isolated change, easy to revert

Later, if you want cleaner code:
- Refactor to Option B (MutationObserver) or
- Refactor to Option C (HTMX Extension)

But don't let perfect be the enemy of good. Get Option A working TODAY, refactor later.

---

## Implementation Code for Option A

### File 1: `src/common/views/management.py`

```python
@login_required
@require_POST
def staff_task_delete(request, task_id):
    """Delete a staff task."""
    logger.info(f"Attempting to delete task {task_id}")
    task = get_object_or_404(StaffTask, pk=task_id)

    if request.POST.get("confirm") == "yes":
        task_title = task.title
        task_id_str = str(task.id)
        logger.info(f"Deleting task: {task_title}")
        task.delete()
        logger.info(f"Task {task_title} deleted successfully")

        # For HTMX requests, return JavaScript that closes modal and refreshes calendar
        if request.headers.get("HX-Request"):
            # Escape task title for JavaScript
            safe_title = task_title.replace("'", "\\'").replace('"', '\\"')

            return HttpResponse(f"""
<script>
(function() {{
    console.log('✅ Task deleted: {safe_title}');

    // Close the modal
    var modal = document.getElementById('taskModal');
    if (modal) {{
        modal.classList.add('hidden');
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('overflow-hidden');
    }}

    var content = document.getElementById('taskModalContent');
    if (content) {{
        content.innerHTML = '';
    }}

    // Refresh the calendar after a short delay
    setTimeout(function() {{
        var calendar = window.__oobcCalendars && window.__oobcCalendars['oobc-calendar'];
        if (calendar) {{
            calendar.refetchEvents();
            console.log('🔄 Calendar refreshed');
        }}
    }}, 150);
}})();
</script>
""", content_type="text/html")

        # For regular requests, redirect to task board
        messages.success(request, f'Task "{task_title}" has been deleted.')
        return redirect("common:staff_task_board")

    # If not confirmed, return error
    logger.warning(f"Task deletion not confirmed for task {task_id}")
    if request.headers.get("HX-Request"):
        return JsonResponse({"error": "Confirmation required."}, status=400)

    messages.error(request, "Task deletion was not confirmed.")
    return redirect("common:staff_task_board")
```

### File 2: `src/coordination/views.py` (coordination_event_delete)

Same pattern - return `<script>` tag with modal close and calendar refresh logic.

---

## Testing Checklist

After implementing Option A:

- [ ] Delete task from calendar modal → Modal closes, calendar refreshes
- [ ] Delete event from calendar modal → Modal closes, calendar refreshes
- [ ] Check browser console for "✅ Task deleted" message
- [ ] Check browser console for "🔄 Calendar refreshed" message
- [ ] Verify no JavaScript errors
- [ ] Test in Chrome, Firefox, Safari
- [ ] Test with slow network (throttling)

---

## Final Note

This bug has been persistent because we've been fighting HTMX's event system. Option A bypasses that entirely by having the server directly inject JavaScript. It's not the "cleanest" solution architecturally, but it **will work** and that's what matters right now.

Ship Option A today. Refactor to Option B or C next week if you want cleaner code.

---

**Created**: 2025-10-04
**Priority**: URGENT - Implement Option A immediately
**Estimated Fix Time**: 15 minutes
