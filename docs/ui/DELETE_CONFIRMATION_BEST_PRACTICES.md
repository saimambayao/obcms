# Delete Confirmation Modal Best Practices Guide

**Stack:** Django + HTMX + Tailwind CSS
**Date:** 2025-10-06
**Status:** Production-Ready Reference

This comprehensive guide documents best practices for implementing delete confirmation modals in modern web applications, specifically optimized for the OBCMS Django + HTMX + Tailwind CSS stack.

---

## Table of Contents

1. [Modal UI/UX Patterns](#1-modal-uiux-patterns)
2. [HTMX Modal Implementation](#2-htmx-modal-implementation)
3. [Delete Button Anti-Patterns](#3-delete-button-anti-patterns)
4. [Instant UI Updates](#4-instant-ui-updates)
5. [Complete Implementation Examples](#5-complete-implementation-examples)
6. [Accessibility Considerations](#6-accessibility-considerations)
7. [Testing Checklist](#7-testing-checklist)

---

## 1. Modal UI/UX Patterns

### 1.1 When to Use Delete Confirmation Modals

**Use confirmation modals for:**
- High-stakes actions (deleting accounts, projects, permanent data)
- Actions with significant cascading effects (deleting parent items with children)
- Irreversible operations where undo is not feasible
- Actions affecting multiple records or users

**Skip confirmation modals for:**
- Low-stakes deletions where undo is available
- Actions that move items to trash/archive (recoverable)
- Rapidly repeated actions (bulk operations with single confirmation)

### 1.2 Modal Structure Best Practices

#### Visual Hierarchy

```
┌─────────────────────────────────────┐
│  [!] Delete Confirmation            │ ← Warning icon + Clear title
├─────────────────────────────────────┤
│                                     │
│  Are you sure you want to delete:   │ ← Descriptive message
│                                     │
│  "Project Alpha (15 tasks)"         │ ← Show what will be deleted
│                                     │
│  This action cannot be undone.      │ ← Consequence warning
│  All related tasks will be deleted. │
│                                     │
├─────────────────────────────────────┤
│           [Cancel]  [Delete]        │ ← Secondary, Primary
└─────────────────────────────────────┘
```

#### Key Design Principles

**Clarity:**
- Use a clear, descriptive title: "Delete Project?" or "Confirm Deletion"
- Show exactly what will be deleted (name, count, preview)
- Explain consequences in plain language
- Use conversational, direct messaging

**Visual Design:**
- Center modals for critical actions
- Use warning colors (red/amber) to signal destructive action
- Include warning icon (exclamation triangle, alert circle)
- Ensure sufficient contrast (WCAG 2.1 AA: 4.5:1 minimum)

**Button Hierarchy:**
```html
<!-- GOOD: Cancel is secondary, Delete is primary destructive -->
<button class="btn-secondary">Cancel</button>
<button class="btn-danger">Delete</button>

<!-- BAD: Reversed hierarchy -->
<button class="btn-danger">Delete</button>
<button class="btn-secondary">Cancel</button>
```

### 1.3 Advanced Confirmation Techniques

#### Type-to-Confirm Pattern

For **critical, absolutely unrecoverable** actions (like GitHub repository deletion):

```html
<div class="modal-body">
  <p class="text-gray-700 mb-4">
    To confirm deletion, type <strong class="text-red-600">{{ object.name }}</strong>
  </p>

  <input
    type="text"
    id="confirm-input"
    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-red-500 focus:border-red-500"
    placeholder="Type the name to confirm"
    autocomplete="off"
  >

  <button
    id="delete-btn"
    disabled
    class="btn-danger disabled:opacity-50 disabled:cursor-not-allowed mt-4"
  >
    Delete
  </button>
</div>

<script>
  const input = document.getElementById('confirm-input');
  const deleteBtn = document.getElementById('delete-btn');
  const requiredText = '{{ object.name }}';

  input.addEventListener('input', (e) => {
    deleteBtn.disabled = e.target.value !== requiredText;
  });
</script>
```

**When to use:**
- Deleting entire accounts or workspaces
- Permanently removing projects with hundreds of records
- Actions that affect multiple users or teams

#### Checkbox Confirmation Pattern

For **medium-severity** actions with important consequences:

```html
<div class="modal-body">
  <div class="bg-amber-50 border-l-4 border-amber-400 p-4 mb-4">
    <div class="flex">
      <i class="fas fa-exclamation-triangle text-amber-400 mr-3"></i>
      <div>
        <p class="text-sm text-amber-700">
          This will delete 15 tasks and 42 attachments associated with this project.
        </p>
      </div>
    </div>
  </div>

  <label class="flex items-start cursor-pointer">
    <input
      type="checkbox"
      id="confirm-checkbox"
      class="mt-1 mr-3 h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
    >
    <span class="text-sm text-gray-700">
      I understand this action cannot be undone
    </span>
  </label>

  <button
    id="delete-btn"
    disabled
    class="btn-danger disabled:opacity-50 mt-4"
  >
    Delete Project
  </button>
</div>

<script>
  document.getElementById('confirm-checkbox').addEventListener('change', (e) => {
    document.getElementById('delete-btn').disabled = !e.target.checked;
  });
</script>
```

### 1.4 Alternative Patterns to Consider

#### Undo Pattern (Preferred for Low/Medium Stakes)

Instead of confirmation, provide immediate action with undo option:

```html
<!-- Toast notification after delete -->
<div class="toast-success">
  <i class="fas fa-check-circle"></i>
  <span>Task deleted</span>
  <button hx-post="/tasks/{{ task.id }}/undo" class="btn-link">Undo</button>
</div>
```

**Advantages:**
- Faster user workflow
- Reduces decision fatigue
- Maintains user momentum

**Considerations:**
- Requires backend undo logic
- May not be suitable for permanent deletions
- Needs temporary data retention (soft delete)

#### Trash/Archive Pattern

Move to recoverable location instead of immediate deletion:

```html
<button hx-post="/projects/{{ project.id }}/archive" class="btn-secondary">
  <i class="fas fa-archive"></i>
  Archive Project
</button>
```

**Advantages:**
- No confirmation needed
- User can recover mistakes
- Reduces anxiety about accidental deletion

**Considerations:**
- Requires trash management UI
- Permanent deletion still needs confirmation
- Database cleanup processes needed

---

## 2. HTMX Modal Implementation

### 2.1 Implementation Patterns

HTMX provides multiple approaches for delete confirmation modals:

#### Pattern A: Server-Rendered Modal (Recommended)

**Advantages:**
- Full server-side validation
- Consistent with Django template patterns
- Easy to implement progressive enhancement
- SEO-friendly fallback

**Flow:**
```
User Click → GET modal HTML → Display modal → User confirms → POST/DELETE → Update UI
```

**HTML Template (List View):**
```html
<!-- Task list with delete buttons -->
<tr data-task-id="{{ task.id }}">
  <td>{{ task.title }}</td>
  <td>
    <button
      hx-get="{% url 'task_delete_confirm' task.id %}"
      hx-target="#modal-container"
      hx-swap="innerHTML"
      class="btn-icon-danger"
      aria-label="Delete task"
    >
      <i class="fas fa-trash"></i>
    </button>
  </td>
</tr>

<!-- Modal container (empty initially) -->
<div id="modal-container"></div>
```

**Django View (Modal Content):**
```python
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task

@login_required
def task_delete_confirm(request, task_id):
    """Return delete confirmation modal HTML."""
    task = get_object_or_404(Task, id=task_id, created_by=request.user)

    context = {
        'task': task,
        'related_count': task.subtasks.count()  # Show impact
    }

    return render(request, 'common/modals/task_delete_confirm.html', context)
```

**Modal Template (task_delete_confirm.html):**
```html
<!-- Modal backdrop -->
<div class="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center"
     id="delete-modal"
     _="on closeModal remove #delete-modal">

  <!-- Modal dialog -->
  <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 transform transition-all"
       @click.away="htmx.trigger('#delete-modal', 'closeModal')">

    <!-- Modal header -->
    <div class="flex items-start justify-between p-6 border-b border-gray-200">
      <div class="flex items-center">
        <div class="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
          <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
        </div>
        <div>
          <h3 class="text-xl font-semibold text-gray-900">
            Delete Task?
          </h3>
        </div>
      </div>
      <button
        @click="htmx.trigger('#delete-modal', 'closeModal')"
        class="text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Close modal"
      >
        <i class="fas fa-times text-xl"></i>
      </button>
    </div>

    <!-- Modal body -->
    <div class="p-6">
      <p class="text-gray-700 mb-4">
        Are you sure you want to delete <strong class="text-gray-900">{{ task.title }}</strong>?
      </p>

      {% if related_count > 0 %}
      <div class="bg-amber-50 border-l-4 border-amber-400 p-4 mb-4">
        <div class="flex">
          <i class="fas fa-info-circle text-amber-400 mr-3 mt-0.5"></i>
          <div>
            <p class="text-sm text-amber-700">
              This task has <strong>{{ related_count }} subtask{{ related_count|pluralize }}</strong>
              that will also be deleted.
            </p>
          </div>
        </div>
      </div>
      {% endif %}

      <p class="text-sm text-gray-500">
        This action cannot be undone.
      </p>
    </div>

    <!-- Modal footer -->
    <div class="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 rounded-b-xl">
      <button
        @click="htmx.trigger('#delete-modal', 'closeModal')"
        class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
      >
        Cancel
      </button>

      <button
        hx-delete="{% url 'task_delete' task.id %}"
        hx-target="[data-task-id='{{ task.id }}']"
        hx-swap="outerHTML swap:300ms"
        hx-on::after-request="htmx.trigger('#delete-modal', 'closeModal')"
        class="px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-red-600 to-red-700 rounded-xl hover:from-red-700 hover:to-red-800 transition-all shadow-sm"
      >
        <i class="fas fa-trash mr-2"></i>
        Delete Task
      </button>
    </div>

  </div>
</div>
```

**Django Delete View:**
```python
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import json

@login_required
@require_http_methods(["DELETE"])
def task_delete(request, task_id):
    """Handle task deletion."""
    task = get_object_or_404(Task, id=task_id, created_by=request.user)

    # Store info for response
    task_title = task.title

    # Delete the task
    task.delete()

    # Return empty response with custom headers for HTMX
    return HttpResponse(
        status=200,
        content='',  # Empty content triggers removal
        headers={
            'HX-Trigger': json.dumps({
                'task-deleted': {'id': task_id},
                'show-toast': f'Task "{task_title}" deleted successfully',
                'refresh-counters': True
            })
        }
    )
```

#### Pattern B: HTML Dialog Element (Modern Browsers)

**Advantages:**
- Native browser modal (accessibility built-in)
- No backdrop JavaScript needed
- Semantic HTML

**HTML:**
```html
<button
  onclick="document.getElementById('delete-dialog-{{ task.id }}').showModal()"
  class="btn-icon-danger"
>
  <i class="fas fa-trash"></i>
</button>

<dialog id="delete-dialog-{{ task.id }}" class="rounded-xl shadow-2xl max-w-md backdrop:bg-gray-900 backdrop:bg-opacity-50">
  <div class="bg-white p-6">
    <h3 class="text-xl font-semibold mb-4">Delete Task?</h3>
    <p class="text-gray-700 mb-6">
      Are you sure you want to delete <strong>{{ task.title }}</strong>?
    </p>

    <div class="flex justify-end gap-3">
      <button
        onclick="this.closest('dialog').close()"
        class="btn-secondary"
      >
        Cancel
      </button>

      <form
        hx-delete="{% url 'task_delete' task.id %}"
        hx-target="[data-task-id='{{ task.id }}']"
        hx-swap="outerHTML swap:300ms"
        hx-on::after-request="this.closest('dialog').close()"
      >
        {% csrf_token %}
        <button type="submit" class="btn-danger">
          Delete
        </button>
      </form>
    </div>
  </div>
</dialog>
```

**Browser Support:** Chrome 37+, Firefox 98+, Safari 15.4+ (March 2022+)

#### Pattern C: Simple hx-confirm (Quick Prototyping)

**Advantages:**
- Fastest to implement
- No modal HTML needed
- Good for admin/internal tools

**HTML:**
```html
<button
  hx-delete="{% url 'task_delete' task.id %}"
  hx-target="[data-task-id='{{ task.id }}']"
  hx-swap="outerHTML swap:300ms"
  hx-confirm="Are you sure you want to delete '{{ task.title }}'? This cannot be undone."
  class="btn-icon-danger"
>
  <i class="fas fa-trash"></i>
</button>
```

**Limitations:**
- Uses browser's native `confirm()` dialog (not customizable)
- No ability to show related data impact
- Less accessible
- Cannot add type-to-confirm or checkboxes

### 2.2 HTMX Event Handling

#### Close Modal After Successful Delete

```html
<!-- Option 1: Use HTMX events -->
<button
  hx-delete="/tasks/123/"
  hx-on::after-request="if(event.detail.successful) htmx.trigger('#modal', 'closeModal')"
>
  Delete
</button>

<!-- Option 2: Use Alpine.js -->
<button
  hx-delete="/tasks/123/"
  @htmx:after-request="if($event.detail.successful) $dispatch('close-modal')"
>
  Delete
</button>

<!-- Option 3: Custom event from server -->
<!-- Django view sets HX-Trigger: close-modal -->
<div id="modal" hx-on:close-modal="this.remove()">
  <!-- Modal content -->
</div>
```

#### Error Handling in Modals

```python
from django.http import HttpResponse

@login_required
@require_http_methods(["DELETE"])
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Check permissions
    if task.created_by != request.user:
        return HttpResponse(
            status=403,
            content='<div class="alert-error">You do not have permission to delete this task.</div>',
            headers={'HX-Retarget': '#modal-errors', 'HX-Reswap': 'innerHTML'}
        )

    # Check constraints
    if task.subtasks.filter(status='in_progress').exists():
        return HttpResponse(
            status=400,
            content='<div class="alert-warning">Cannot delete task with in-progress subtasks.</div>',
            headers={'HX-Retarget': '#modal-errors', 'HX-Reswap': 'innerHTML'}
        )

    task.delete()
    return HttpResponse(status=200, content='')
```

**Modal Template with Error Container:**
```html
<div class="modal">
  <!-- Error display area -->
  <div id="modal-errors"></div>

  <!-- Modal content -->
  <div class="modal-body">
    <!-- ... -->
  </div>
</div>
```

### 2.3 Loading States and Spinners

Always show loading feedback during async operations:

```html
<button
  hx-delete="{% url 'task_delete' task.id %}"
  hx-indicator="#delete-spinner"
  class="btn-danger"
>
  <span class="htmx-indicator" id="delete-spinner">
    <i class="fas fa-spinner fa-spin mr-2"></i>
  </span>
  <span>Delete</span>
</button>
```

**HTMX automatically:**
- Adds `htmx-request` class during request
- Shows elements with `htmx-indicator` class
- Can disable buttons during request

**Enhanced with CSS:**
```css
.htmx-request button {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.htmx-indicator {
  display: none;
}

.htmx-request .htmx-indicator {
  display: inline-block;
}
```

---

## 3. Delete Button Anti-Patterns

### 3.1 Common Problems and Solutions

#### Anti-Pattern 1: Accidental Double-Click Deletion

**Problem:**
```html
<!-- BAD: No protection against double-click -->
<button onclick="deleteTask()" class="btn-danger">Delete</button>
<button onclick="confirmDelete()" class="btn-primary">Confirm</button>
```

User rapidly clicks "Delete" then "Confirm" → Item deleted without reading message.

**Solution:**
```html
<!-- GOOD: Button disabled during processing -->
<button
  hx-delete="/tasks/123/"
  hx-disabled-elt="this"
  class="btn-danger"
>
  Delete
</button>
```

**Alternative: Add delay to enable confirm button:**
```html
<script>
  const confirmBtn = document.getElementById('confirm-delete');
  confirmBtn.disabled = true;

  setTimeout(() => {
    confirmBtn.disabled = false;
  }, 1000); // 1 second delay forces user to pause
</script>
```

#### Anti-Pattern 2: Unclear Button Hierarchy

**Problem:**
```html
<!-- BAD: Primary action is destructive -->
<button class="btn-primary bg-red-600">Delete</button>
<button class="btn-secondary">Cancel</button>
```

Visual hierarchy suggests "Delete" is the recommended action.

**Solution:**
```html
<!-- GOOD: Secondary cancel, danger delete -->
<button class="btn-secondary">Cancel</button>
<button class="btn-danger">Delete</button>
```

#### Anti-Pattern 3: No Visual Feedback

**Problem:**
```html
<!-- BAD: No indication of what's being deleted -->
<button hx-delete="/tasks/123/">Delete</button>
```

User can't verify they're deleting the right item.

**Solution:**
```html
<!-- GOOD: Show what will be deleted -->
<div class="modal-body">
  <p>Delete <strong class="text-red-600">{{ task.title }}</strong>?</p>
  <div class="bg-gray-50 p-4 rounded-lg mt-3">
    <p class="text-sm text-gray-600">Created: {{ task.created_at }}</p>
    <p class="text-sm text-gray-600">Last modified: {{ task.updated_at }}</p>
    <p class="text-sm text-gray-600">Subtasks: {{ task.subtasks.count }}</p>
  </div>
</div>
```

#### Anti-Pattern 4: Hidden or Hard-to-Find Delete Button

**Problem:**
```html
<!-- BAD: Delete buried in dropdown menu -->
<div class="dropdown">
  <button>Actions ▾</button>
  <ul>
    <li>Edit</li>
    <li>Duplicate</li>
    <li>Archive</li>
    <li>Share</li>
    <li>Delete</li> <!-- User has to hunt for it -->
  </ul>
</div>
```

**Solution:**
```html
<!-- GOOD: Clear, accessible delete action -->
<div class="flex gap-2">
  <button class="btn-secondary">Edit</button>
  <button class="btn-icon-danger" aria-label="Delete task">
    <i class="fas fa-trash"></i>
  </button>
</div>
```

#### Anti-Pattern 5: No Consequence Warning

**Problem:**
```html
<!-- BAD: No indication this is permanent -->
<p>Delete this task?</p>
<button>Yes</button>
```

**Solution:**
```html
<!-- GOOD: Clear consequence messaging -->
<div class="modal-body">
  <p class="text-gray-700 mb-3">
    Are you sure you want to delete <strong>{{ task.title }}</strong>?
  </p>

  <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
    <div class="flex">
      <i class="fas fa-exclamation-circle text-red-400 mr-3"></i>
      <div>
        <p class="text-sm font-medium text-red-800 mb-1">
          This action cannot be undone
        </p>
        <p class="text-sm text-red-700">
          The following will be permanently deleted:
        </p>
        <ul class="list-disc list-inside text-sm text-red-700 mt-2">
          <li>Task and all metadata</li>
          <li>{{ task.subtasks.count }} subtask{{ task.subtasks.count|pluralize }}</li>
          <li>{{ task.attachments.count }} attachment{{ task.attachments.count|pluralize }}</li>
          <li>All comments and activity history</li>
        </ul>
      </div>
    </div>
  </div>
</div>
```

### 3.2 Mobile Considerations

#### Touch Target Size

**Problem:**
```html
<!-- BAD: Too small for touch -->
<button class="w-6 h-6 text-xs">
  <i class="fas fa-trash"></i>
</button>
```

**Solution:**
```html
<!-- GOOD: Minimum 48x48px touch target -->
<button class="min-w-[48px] min-h-[48px] flex items-center justify-center">
  <i class="fas fa-trash"></i>
</button>
```

#### Spacing for Accidental Taps

**Problem:**
```html
<!-- BAD: Edit and delete too close together -->
<button class="btn-edit">Edit</button>
<button class="btn-delete">Delete</button>
```

**Solution:**
```html
<!-- GOOD: Adequate spacing between actions -->
<div class="flex gap-4">
  <button class="btn-edit">Edit</button>
  <button class="btn-delete">Delete</button>
</div>
```

---

## 4. Instant UI Updates

### 4.1 Optimistic Deletion Pattern

For the best user experience, remove the item from the UI **immediately** while the delete request processes in the background.

#### Basic Optimistic Delete with Rollback

**HTML:**
```html
<tr
  data-task-id="{{ task.id }}"
  class="transition-opacity duration-300"
>
  <td>{{ task.title }}</td>
  <td>
    <button
      hx-delete="{% url 'task_delete' task.id %}"
      hx-target="closest tr"
      hx-swap="outerHTML swap:300ms"
      class="btn-icon-danger"
    >
      <i class="fas fa-trash"></i>
    </button>
  </td>
</tr>
```

**CSS for Smooth Removal:**
```css
/* Fade out animation during swap */
tr.htmx-swapping {
  opacity: 0;
  transform: translateX(-20px);
  transition: all 300ms ease-out;
}
```

#### Advanced: Optimistic with Rollback on Error

**Using hx-optimistic Extension:**

```html
<!-- Include the hx-optimistic extension -->
<script src="https://unpkg.com/hx-optimistic@1.0.0/dist/hx-optimistic.js"></script>

<tr
  data-task-id="{{ task.id }}"
  hx-ext="optimistic"
  hx-optimistic="remove"
>
  <td>{{ task.title }}</td>
  <td>
    <button
      hx-delete="{% url 'task_delete' task.id %}"
      hx-target="closest tr"
      hx-swap="delete"
    >
      Delete
    </button>
  </td>
</tr>
```

**How it works:**
1. User clicks delete
2. Row fades out immediately (optimistic update)
3. DELETE request sent to server
4. **If success:** Row stays removed
5. **If error:** Row fades back in with error message

### 4.2 Tree View Updates

For hierarchical structures (nested tasks, folders, org charts), use targeted updates:

#### HTML Structure

```html
<div class="tree-view">
  <!-- Parent node -->
  <div data-node-id="{{ parent.id }}" class="tree-node">
    <div class="node-content">
      <button class="toggle-children">
        <i class="fas fa-chevron-right"></i>
      </button>
      <span>{{ parent.title }}</span>
      <button
        hx-delete="{% url 'node_delete' parent.id %}"
        hx-target="closest [data-node-id]"
        hx-swap="outerHTML swap:300ms"
        class="btn-icon-danger"
      >
        <i class="fas fa-trash"></i>
      </button>
    </div>

    <!-- Children (nested) -->
    <div class="children ml-6">
      {% for child in parent.children.all %}
      <div data-node-id="{{ child.id }}" class="tree-node">
        <div class="node-content">
          <span>{{ child.title }}</span>
          <button
            hx-delete="{% url 'node_delete' child.id %}"
            hx-target="closest [data-node-id]"
            hx-swap="outerHTML swap:300ms"
            class="btn-icon-danger"
          >
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>
```

**Key Attributes:**
- `data-node-id="{{ node.id }}"` - Unique identifier for targeting
- `hx-target="closest [data-node-id]"` - Targets the entire node container
- `hx-swap="outerHTML swap:300ms"` - Replaces entire node with transition

#### CSS for Tree Animations

```css
/* Collapse animation when deleting */
.tree-node {
  transition: all 300ms ease-out;
  max-height: 200px; /* Adjust based on content */
  overflow: hidden;
}

.tree-node.htmx-swapping {
  max-height: 0;
  opacity: 0;
  margin: 0;
  padding: 0;
  transform: translateX(-20px);
}

/* Nested children also collapse */
.tree-node.htmx-swapping .children {
  display: none;
}
```

### 4.3 Out-of-Band Updates

Update multiple UI regions simultaneously when deleting items:

**Django View:**
```python
from django.template.loader import render_to_string

@login_required
@require_http_methods(["DELETE"])
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    task.delete()

    # Render updated counter
    counter_html = render_to_string('partials/task_counter.html', {
        'total_tasks': project.tasks.count(),
        'completed_tasks': project.tasks.filter(status='completed').count()
    })

    # Return empty content for main target + OOB update for counter
    response = HttpResponse('')
    response['HX-Trigger'] = json.dumps({
        'task-deleted': {'id': task_id, 'project_id': project.id}
    })

    # Add out-of-band swap for counter
    oob_html = f'<div id="task-counter" hx-swap-oob="true">{counter_html}</div>'
    response.content = oob_html

    return response
```

**HTML:**
```html
<!-- Main content area -->
<div id="task-list">
  <div data-task-id="123">
    <!-- Task row gets removed -->
  </div>
</div>

<!-- Counter updates out-of-band -->
<div id="task-counter">
  <span>Total: 15</span>
  <span>Completed: 8</span>
</div>
```

### 4.4 Toast Notifications After Delete

Show user feedback after successful deletion:

**Django View:**
```python
return HttpResponse(
    status=200,
    content='',
    headers={
        'HX-Trigger': json.dumps({
            'show-toast': {
                'message': f'Task "{task.title}" deleted successfully',
                'type': 'success'
            }
        })
    }
)
```

**JavaScript Toast Handler:**
```javascript
// Listen for custom events from server
document.body.addEventListener('show-toast', (event) => {
  const { message, type } = event.detail;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type} fixed bottom-4 right-4 px-6 py-4 rounded-xl shadow-lg transform transition-all duration-300 translate-y-20 opacity-0`;
  toast.innerHTML = `
    <div class="flex items-center gap-3">
      <i class="fas fa-check-circle text-emerald-500"></i>
      <span class="text-gray-900">${message}</span>
    </div>
  `;

  document.body.appendChild(toast);

  // Animate in
  setTimeout(() => {
    toast.classList.remove('translate-y-20', 'opacity-0');
  }, 10);

  // Auto-remove after 3 seconds
  setTimeout(() => {
    toast.classList.add('translate-y-20', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
});
```

---

## 5. Complete Implementation Examples

### 5.1 Example 1: Simple Task Deletion

**List View Template:**
```html
{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
  <h1 class="text-2xl font-bold mb-6">My Tasks</h1>

  <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
    <table class="w-full">
      <thead class="bg-gradient-to-r from-blue-600 to-teal-600 text-white">
        <tr>
          <th class="px-6 py-4 text-left">Task</th>
          <th class="px-6 py-4 text-left">Status</th>
          <th class="px-6 py-4 text-left">Due Date</th>
          <th class="px-6 py-4 text-right">Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for task in tasks %}
        <tr data-task-id="{{ task.id }}" class="border-b border-gray-200 hover:bg-gray-50 transition-colors">
          <td class="px-6 py-4">
            <div class="font-medium text-gray-900">{{ task.title }}</div>
            <div class="text-sm text-gray-500">{{ task.description|truncatewords:10 }}</div>
          </td>
          <td class="px-6 py-4">
            <span class="px-3 py-1 rounded-full text-xs font-medium
              {% if task.status == 'completed' %}bg-emerald-100 text-emerald-800
              {% elif task.status == 'in_progress' %}bg-blue-100 text-blue-800
              {% else %}bg-gray-100 text-gray-800{% endif %}">
              {{ task.get_status_display }}
            </span>
          </td>
          <td class="px-6 py-4 text-gray-600">
            {{ task.due_date|date:"M d, Y" }}
          </td>
          <td class="px-6 py-4">
            <div class="flex items-center justify-end gap-2">
              <a href="{% url 'task_detail' task.id %}" class="btn-icon-secondary">
                <i class="fas fa-eye"></i>
              </a>
              <button
                hx-get="{% url 'task_delete_confirm' task.id %}"
                hx-target="#modal-container"
                hx-swap="innerHTML"
                class="btn-icon-danger"
                aria-label="Delete task"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="4" class="px-6 py-12 text-center text-gray-500">
            No tasks found. <a href="{% url 'task_create' %}" class="text-blue-600 hover:underline">Create one?</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <!-- Pagination -->
  {% if is_paginated %}
  <div class="mt-6 flex justify-center">
    <!-- Pagination controls here -->
  </div>
  {% endif %}
</div>

<!-- Modal container -->
<div id="modal-container"></div>
{% endblock %}
```

**Django Views:**
```python
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from .models import Task
import json

@login_required
def task_list(request):
    """Display user's tasks."""
    tasks = Task.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def task_delete_confirm(request, task_id):
    """Return delete confirmation modal HTML."""
    task = get_object_or_404(Task, id=task_id, created_by=request.user)

    context = {
        'task': task,
        'subtask_count': task.subtasks.count(),
        'attachment_count': task.attachments.count()
    }

    return render(request, 'tasks/modals/delete_confirm.html', context)

@login_required
@require_http_methods(["DELETE"])
def task_delete(request, task_id):
    """Handle task deletion."""
    task = get_object_or_404(Task, id=task_id, created_by=request.user)

    # Store for response
    task_title = task.title

    # Perform deletion
    task.delete()

    # Return success response
    return HttpResponse(
        status=200,
        content='',
        headers={
            'HX-Trigger': json.dumps({
                'task-deleted': {'id': task_id},
                'show-toast': f'Task "{task_title}" deleted successfully'
            })
        }
    )
```

**Modal Template (tasks/modals/delete_confirm.html):**
```html
<div class="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center"
     id="delete-modal"
     _="on closeModal remove #delete-modal">

  <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 transform transition-all"
       @click.away="htmx.trigger('#delete-modal', 'closeModal')">

    <div class="flex items-start justify-between p-6 border-b border-gray-200">
      <div class="flex items-center">
        <div class="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
          <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
        </div>
        <h3 class="text-xl font-semibold text-gray-900">Delete Task?</h3>
      </div>
      <button
        @click="htmx.trigger('#delete-modal', 'closeModal')"
        class="text-gray-400 hover:text-gray-600 transition-colors"
      >
        <i class="fas fa-times text-xl"></i>
      </button>
    </div>

    <div class="p-6">
      <p class="text-gray-700 mb-4">
        Are you sure you want to delete <strong class="text-gray-900">{{ task.title }}</strong>?
      </p>

      {% if subtask_count > 0 or attachment_count > 0 %}
      <div class="bg-amber-50 border-l-4 border-amber-400 p-4 mb-4">
        <div class="flex">
          <i class="fas fa-info-circle text-amber-400 mr-3 mt-0.5"></i>
          <div>
            <p class="text-sm font-medium text-amber-800 mb-2">
              This will also delete:
            </p>
            <ul class="text-sm text-amber-700 space-y-1">
              {% if subtask_count > 0 %}
              <li>{{ subtask_count }} subtask{{ subtask_count|pluralize }}</li>
              {% endif %}
              {% if attachment_count > 0 %}
              <li>{{ attachment_count }} attachment{{ attachment_count|pluralize }}</li>
              {% endif %}
            </ul>
          </div>
        </div>
      </div>
      {% endif %}

      <p class="text-sm text-gray-500">
        This action cannot be undone.
      </p>
    </div>

    <div class="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 rounded-b-xl">
      <button
        @click="htmx.trigger('#delete-modal', 'closeModal')"
        class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
      >
        Cancel
      </button>

      <button
        hx-delete="{% url 'task_delete' task.id %}"
        hx-target="[data-task-id='{{ task.id }}']"
        hx-swap="outerHTML swap:300ms"
        hx-on::after-request="htmx.trigger('#delete-modal', 'closeModal')"
        class="px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-red-600 to-red-700 rounded-xl hover:from-red-700 hover:to-red-800 transition-all shadow-sm"
      >
        <i class="fas fa-trash mr-2"></i>
        Delete Task
      </button>
    </div>

  </div>
</div>
```

**URLs:**
```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:task_id>/delete/confirm/', views.task_delete_confirm, name='task_delete_confirm'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
]
```

### 5.2 Example 2: Tree View with Nested Deletions

**Tree Template:**
```html
{% load static %}

<div class="tree-view p-6">
  {% for node in root_nodes %}
    {% include "partials/tree_node.html" with node=node depth=0 %}
  {% endfor %}
</div>

<!-- Modal container -->
<div id="modal-container"></div>

<style>
  .tree-node {
    transition: all 300ms ease-out;
  }

  .tree-node.htmx-swapping {
    opacity: 0;
    max-height: 0;
    margin: 0;
    overflow: hidden;
    transform: translateX(-20px);
  }
</style>
```

**Recursive Node Partial (partials/tree_node.html):**
```html
<div data-node-id="{{ node.id }}" class="tree-node mb-2">
  <div class="node-content flex items-center gap-2 p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
       style="margin-left: {{ depth }}rem;">

    {% if node.children.exists %}
    <button
      class="toggle-children w-6 h-6 flex items-center justify-center text-gray-400 hover:text-gray-600"
      onclick="this.querySelector('i').classList.toggle('fa-chevron-right'); this.querySelector('i').classList.toggle('fa-chevron-down'); this.closest('.tree-node').querySelector('.children').classList.toggle('hidden');"
    >
      <i class="fas fa-chevron-right text-xs"></i>
    </button>
    {% else %}
    <span class="w-6"></span>
    {% endif %}

    <i class="fas fa-folder text-blue-500"></i>

    <span class="flex-1 text-gray-900">{{ node.title }}</span>

    <span class="text-xs text-gray-500">{{ node.children.count }} items</span>

    <div class="flex gap-1">
      <button
        class="btn-icon-secondary text-xs"
        onclick="alert('Edit: {{ node.title }}')"
      >
        <i class="fas fa-edit"></i>
      </button>

      <button
        hx-get="{% url 'node_delete_confirm' node.id %}"
        hx-target="#modal-container"
        hx-swap="innerHTML"
        class="btn-icon-danger text-xs"
      >
        <i class="fas fa-trash"></i>
      </button>
    </div>
  </div>

  {% if node.children.exists %}
  <div class="children ml-6">
    {% for child in node.children.all %}
      {% include "partials/tree_node.html" with node=child depth=depth|add:1 %}
    {% endfor %}
  </div>
  {% endif %}
</div>
```

**Django Views:**
```python
@login_required
def node_delete_confirm(request, node_id):
    """Return delete confirmation for tree node."""
    node = get_object_or_404(TreeNode, id=node_id)

    # Count all descendants
    descendant_count = node.get_descendant_count()

    context = {
        'node': node,
        'descendant_count': descendant_count,
        'has_children': descendant_count > 0
    }

    return render(request, 'tree/modals/node_delete_confirm.html', context)

@login_required
@require_http_methods(["DELETE"])
def node_delete(request, node_id):
    """Delete tree node and all descendants."""
    node = get_object_or_404(TreeNode, id=node_id)

    node_title = node.title
    descendant_count = node.get_descendant_count()

    # Delete node (cascades to children)
    node.delete()

    return HttpResponse(
        status=200,
        content='',
        headers={
            'HX-Trigger': json.dumps({
                'node-deleted': {'id': node_id},
                'show-toast': f'Deleted "{node_title}" and {descendant_count} nested items'
            })
        }
    )
```

**Modal for Tree Node:**
```html
<div class="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center"
     id="delete-modal"
     _="on closeModal remove #delete-modal">

  <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4">

    <div class="flex items-start justify-between p-6 border-b border-gray-200">
      <div class="flex items-center">
        <div class="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
          <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
        </div>
        <h3 class="text-xl font-semibold text-gray-900">Delete Folder?</h3>
      </div>
      <button
        @click="htmx.trigger('#delete-modal', 'closeModal')"
        class="text-gray-400 hover:text-gray-600"
      >
        <i class="fas fa-times text-xl"></i>
      </button>
    </div>

    <div class="p-6">
      <p class="text-gray-700 mb-4">
        Are you sure you want to delete <strong class="text-gray-900">{{ node.title }}</strong>?
      </p>

      {% if has_children %}
      <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
        <div class="flex">
          <i class="fas fa-exclamation-circle text-red-400 mr-3 mt-0.5"></i>
          <div>
            <p class="text-sm font-medium text-red-800 mb-2">
              Warning: This folder contains nested items
            </p>
            <p class="text-sm text-red-700">
              Deleting this folder will <strong>permanently delete {{ descendant_count }} nested item{{ descendant_count|pluralize }}</strong>,
              including all subfolders and their contents.
            </p>
          </div>
        </div>
      </div>
      {% endif %}

      <p class="text-sm text-gray-500">
        This action cannot be undone.
      </p>
    </div>

    <div class="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 rounded-b-xl">
      <button
        @click="htmx.trigger('#delete-modal', 'closeModal')"
        class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50"
      >
        Cancel
      </button>

      <button
        hx-delete="{% url 'node_delete' node.id %}"
        hx-target="[data-node-id='{{ node.id }}']"
        hx-swap="outerHTML swap:300ms"
        hx-on::after-request="htmx.trigger('#delete-modal', 'closeModal')"
        class="px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-red-600 to-red-700 rounded-xl hover:from-red-700 hover:to-red-800"
      >
        <i class="fas fa-trash mr-2"></i>
        Delete{% if has_children %} All ({{ descendant_count|add:1 }}){% endif %}
      </button>
    </div>

  </div>
</div>
```

---

## 6. Accessibility Considerations

### 6.1 ARIA Attributes

Always include proper ARIA labels and roles:

```html
<button
  hx-get="{% url 'task_delete_confirm' task.id %}"
  hx-target="#modal-container"
  class="btn-icon-danger"
  aria-label="Delete task: {{ task.title }}"
>
  <i class="fas fa-trash" aria-hidden="true"></i>
</button>

<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
  class="modal"
>
  <h3 id="modal-title">Delete Task?</h3>
  <p id="modal-description">This action cannot be undone.</p>
</div>
```

### 6.2 Keyboard Navigation

Ensure modals can be operated with keyboard only:

```html
<div class="modal" id="delete-modal">
  <!-- Auto-focus the cancel button (safe action) -->
  <button autofocus @click="closeModal()">Cancel</button>

  <!-- Delete button requires explicit tab/enter -->
  <button>Delete</button>
</div>

<script>
  // Trap focus within modal
  const modal = document.getElementById('delete-modal');
  const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal();
    }

    if (e.key === 'Tab') {
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    }
  });
</script>
```

### 6.3 Screen Reader Announcements

```html
<!-- Live region for delete feedback -->
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
  class="sr-only"
  id="delete-status"
>
  <!-- JavaScript updates this with messages -->
</div>

<script>
  document.body.addEventListener('task-deleted', (event) => {
    const statusEl = document.getElementById('delete-status');
    statusEl.textContent = `Task deleted successfully`;
  });
</script>
```

### 6.4 Focus Management

Return focus to appropriate element after modal closes:

```javascript
let previousFocus = null;

function openDeleteModal(taskId) {
  // Store current focus
  previousFocus = document.activeElement;

  // Open modal (HTMX handles this)
  // ...
}

function closeModal() {
  const modal = document.getElementById('delete-modal');
  modal.remove();

  // Restore focus
  if (previousFocus) {
    previousFocus.focus();
  }
}
```

---

## 7. Testing Checklist

### 7.1 Functional Testing

- [ ] Modal opens when delete button clicked
- [ ] Modal displays correct item details
- [ ] Cancel button closes modal without deleting
- [ ] Delete button removes item from UI
- [ ] Delete request sent to correct endpoint
- [ ] Success toast appears after deletion
- [ ] Error message shown if deletion fails
- [ ] Counters/stats update after deletion
- [ ] Related items cascaded correctly

### 7.2 UX Testing

- [ ] Modal centered on screen
- [ ] Backdrop prevents interaction with background
- [ ] Click outside modal closes it
- [ ] Escape key closes modal
- [ ] Delete button clearly indicates danger
- [ ] Cancel button is safe default action
- [ ] Loading spinner shows during request
- [ ] Button disabled during request
- [ ] Item fades out smoothly before removal
- [ ] No layout shift when item removed

### 7.3 Accessibility Testing

- [ ] Can navigate modal with keyboard only
- [ ] Focus trapped within modal
- [ ] Tab order is logical
- [ ] Escape key closes modal
- [ ] Focus returns to trigger button after close
- [ ] All interactive elements have ARIA labels
- [ ] Screen reader announces modal opened
- [ ] Screen reader announces deletion success
- [ ] Color contrast meets WCAG 2.1 AA (4.5:1)
- [ ] Touch targets minimum 48x48px on mobile

### 7.4 Edge Cases

- [ ] Rapid clicking delete button doesn't duplicate requests
- [ ] Double-clicking confirm doesn't cause errors
- [ ] Network errors handled gracefully
- [ ] Permission denied shows clear error
- [ ] Deleting last item in list handled correctly
- [ ] Deleting parent cascades to children
- [ ] Concurrent deletions don't cause conflicts
- [ ] Works correctly in all supported browsers
- [ ] Works on mobile devices (touch)
- [ ] Works with slow network connections

### 7.5 Performance Testing

- [ ] Modal loads in under 100ms
- [ ] Delete request completes in under 500ms
- [ ] UI update happens immediately (optimistic)
- [ ] No memory leaks from unclosed modals
- [ ] No console errors or warnings
- [ ] Animations smooth (60fps)

---

## Summary

### Key Takeaways

1. **Use server-rendered modals** with HTMX for best maintainability and accessibility
2. **Always show what will be deleted** - names, counts, previews
3. **Explain consequences clearly** - "cannot be undone", cascading effects
4. **Provide instant UI feedback** - optimistic updates, smooth animations
5. **Follow button hierarchy** - Cancel (secondary), Delete (danger primary)
6. **Add friction for critical actions** - type-to-confirm, checkboxes, delays
7. **Test accessibility** - keyboard navigation, screen readers, focus management
8. **Handle errors gracefully** - show clear messages, allow retry

### Implementation Priority

**Phase 1: Basic Delete Confirmation**
- Simple modal with confirm/cancel
- HTMX delete request
- Basic instant UI removal

**Phase 2: Enhanced UX**
- Show related item counts
- Add consequence warnings
- Smooth fade-out animations
- Toast notifications

**Phase 3: Advanced Features**
- Type-to-confirm for critical actions
- Out-of-band counter updates
- Optimistic updates with rollback
- Tree view cascading deletes

**Phase 4: Polish**
- Accessibility audit
- Mobile touch optimization
- Loading states and error handling
- Performance optimization

---

## References

- [HTMX Delete Row Example](https://htmx.org/examples/delete-row/)
- [HTMX Modal Dialog Examples](https://htmx.org/examples/modal-bootstrap/)
- [Nielsen Norman Group: Confirmation Dialogs](https://www.nngroup.com/articles/confirmation-dialog/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Tailwind CSS Modal Components](https://tailwindcss.com/plus/ui-blocks/application-ui/overlays/modal-dialogs)
- [Django HTMX Patterns](https://github.com/spookylukey/django-htmx-patterns)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-06
**Maintained By:** OBCMS Development Team
