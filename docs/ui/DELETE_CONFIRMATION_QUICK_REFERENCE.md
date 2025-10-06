# Delete Confirmation Quick Reference

**One-Page Cheat Sheet for Django + HTMX + Tailwind**

---

## Quick Decision Tree

```
Need delete confirmation?
│
├─ LOW STAKES (tags, comments)
│  └─> Use: Undo pattern (no modal)
│
├─ MEDIUM STAKES (tasks, files)
│  └─> Use: Simple confirmation modal
│
└─ HIGH STAKES (projects, accounts)
   └─> Use: Type-to-confirm modal
```

---

## Pattern 1: Server-Rendered Modal (Recommended)

**Use when:** You need full validation, show related data, maintain consistency

### Template (List View)
```html
<tr data-task-id="{{ task.id }}">
  <td>{{ task.title }}</td>
  <td>
    <button
      hx-get="{% url 'task_delete_confirm' task.id %}"
      hx-target="#modal-container"
      hx-swap="innerHTML"
      class="btn-icon-danger"
    >
      <i class="fas fa-trash"></i>
    </button>
  </td>
</tr>

<div id="modal-container"></div>
```

### Django View
```python
@login_required
def task_delete_confirm(request, task_id):
    task = get_object_or_404(Task, id=task_id, created_by=request.user)
    return render(request, 'modals/delete_confirm.html', {'task': task})

@login_required
@require_http_methods(["DELETE"])
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, created_by=request.user)
    task.delete()

    return HttpResponse(
        status=200,
        content='',
        headers={'HX-Trigger': json.dumps({'show-toast': 'Deleted!'})}
    )
```

### Modal Template
```html
<div class="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center"
     id="delete-modal"
     _="on closeModal remove #delete-modal">

  <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4">
    <!-- Header -->
    <div class="flex items-start p-6 border-b">
      <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
        <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
      </div>
      <h3 class="text-xl font-semibold">Delete Task?</h3>
      <button @click="htmx.trigger('#delete-modal', 'closeModal')" class="ml-auto">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Body -->
    <div class="p-6">
      <p class="text-gray-700 mb-4">
        Delete <strong>{{ task.title }}</strong>?
      </p>
      <p class="text-sm text-gray-500">This cannot be undone.</p>
    </div>

    <!-- Footer -->
    <div class="flex justify-end gap-3 px-6 py-4 bg-gray-50 rounded-b-xl">
      <button
        @click="htmx.trigger('#delete-modal', 'closeModal')"
        class="btn-secondary"
      >
        Cancel
      </button>
      <button
        hx-delete="{% url 'task_delete' task.id %}"
        hx-target="[data-task-id='{{ task.id }}']"
        hx-swap="outerHTML swap:300ms"
        hx-on::after-request="htmx.trigger('#delete-modal', 'closeModal')"
        class="btn-danger"
      >
        Delete
      </button>
    </div>
  </div>
</div>
```

---

## Pattern 2: HTML Dialog (Modern Browsers Only)

**Use when:** You need native accessibility, simpler implementation

```html
<button onclick="document.getElementById('dialog-{{ task.id }}').showModal()">
  Delete
</button>

<dialog id="dialog-{{ task.id }}" class="rounded-xl backdrop:bg-gray-900 backdrop:bg-opacity-50">
  <div class="p-6">
    <h3>Delete Task?</h3>
    <p>Delete <strong>{{ task.title }}</strong>?</p>

    <div class="flex gap-3 mt-4">
      <button onclick="this.closest('dialog').close()">Cancel</button>
      <form
        hx-delete="{% url 'task_delete' task.id %}"
        hx-target="[data-task-id='{{ task.id }}']"
        hx-on::after-request="this.closest('dialog').close()"
      >
        <button type="submit">Delete</button>
      </form>
    </div>
  </div>
</dialog>
```

---

## Pattern 3: Simple hx-confirm

**Use when:** Prototyping, admin tools, internal systems

```html
<button
  hx-delete="{% url 'task_delete' task.id %}"
  hx-target="[data-task-id='{{ task.id }}']"
  hx-swap="outerHTML swap:300ms"
  hx-confirm="Delete '{{ task.title }}'? This cannot be undone."
>
  Delete
</button>
```

---

## Instant UI Updates

### Fade Out Animation
```css
.htmx-swapping {
  opacity: 0;
  transform: translateX(-20px);
  transition: all 300ms ease-out;
}
```

### Tree View Deletion
```html
<div data-node-id="{{ node.id }}" class="tree-node">
  <span>{{ node.title }}</span>
  <button
    hx-delete="{% url 'node_delete' node.id %}"
    hx-target="closest [data-node-id]"
    hx-swap="outerHTML swap:300ms"
  >
    Delete
  </button>

  <div class="children">
    <!-- Nested children -->
  </div>
</div>
```

### Toast Notification
```javascript
document.body.addEventListener('show-toast', (event) => {
  const message = event.detail.message || event.detail;

  const toast = document.createElement('div');
  toast.className = 'fixed bottom-4 right-4 px-6 py-4 bg-white rounded-xl shadow-lg';
  toast.innerHTML = `
    <i class="fas fa-check-circle text-emerald-500 mr-2"></i>
    ${message}
  `;

  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 3000);
});
```

---

## Type-to-Confirm (High Stakes)

```html
<input
  type="text"
  id="confirm-input"
  placeholder="Type '{{ object.name }}' to confirm"
>

<button id="delete-btn" disabled class="btn-danger disabled:opacity-50">
  Delete
</button>

<script>
  document.getElementById('confirm-input').addEventListener('input', (e) => {
    const required = '{{ object.name }}';
    document.getElementById('delete-btn').disabled = e.target.value !== required;
  });
</script>
```

---

## Common Anti-Patterns (Avoid These)

### ❌ Bad: No visual feedback
```html
<button hx-delete="/tasks/123/">Delete</button>
```

### ✅ Good: Show what will be deleted
```html
<button>Delete "{{ task.title }}"?</button>
```

---

### ❌ Bad: Primary delete button
```html
<button class="btn-primary bg-red-600">Delete</button>
<button class="btn-secondary">Cancel</button>
```

### ✅ Good: Secondary cancel, danger delete
```html
<button class="btn-secondary">Cancel</button>
<button class="btn-danger">Delete</button>
```

---

### ❌ Bad: No consequence warning
```html
<p>Delete this task?</p>
```

### ✅ Good: Clear consequences
```html
<p>Delete <strong>{{ task.title }}</strong>?</p>
<div class="alert-warning">
  This will delete {{ task.subtasks.count }} subtasks.
  This cannot be undone.
</div>
```

---

## Accessibility Checklist

- [ ] `aria-label` on icon-only buttons
- [ ] `role="dialog"` on modals
- [ ] `aria-modal="true"` on modals
- [ ] Focus trapped in modal
- [ ] Escape key closes modal
- [ ] Focus returns after close
- [ ] 48x48px minimum touch targets
- [ ] 4.5:1 color contrast ratio

---

## Testing Checklist

- [ ] Modal opens on click
- [ ] Cancel closes without deleting
- [ ] Delete removes item from UI
- [ ] Success toast appears
- [ ] Error handling works
- [ ] Keyboard navigation works
- [ ] Click outside closes modal
- [ ] No double-click issues
- [ ] Works on mobile
- [ ] Animations smooth

---

## CSS Classes Reference

### OBCMS Button Classes
```css
.btn-secondary          /* Cancel, back */
.btn-danger            /* Delete, destructive */
.btn-icon-danger       /* Icon-only delete */
```

### Modal Classes
```css
.fixed.inset-0                    /* Full screen overlay */
.bg-gray-900.bg-opacity-50       /* Backdrop */
.z-50                            /* Above content */
.rounded-xl                      /* Rounded corners */
.shadow-2xl                      /* Deep shadow */
```

### Alert Classes
```css
.bg-red-50.border-l-4.border-red-400     /* Error alert */
.bg-amber-50.border-l-4.border-amber-400 /* Warning alert */
```

---

## URLs Pattern

```python
# urls.py
urlpatterns = [
    path('tasks/<int:pk>/delete/confirm/', views.task_delete_confirm, name='task_delete_confirm'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
]
```

---

## Complete Example (Copy-Paste Ready)

**See full guide:** [DELETE_CONFIRMATION_BEST_PRACTICES.md](DELETE_CONFIRMATION_BEST_PRACTICES.md)

- Example 1: Simple task deletion (tables)
- Example 2: Tree view with nested deletions
- Full Django views with error handling
- Complete modal templates
- CSS animations
- Accessibility features

---

**Last Updated:** 2025-10-06
**Full Guide:** [docs/ui/DELETE_CONFIRMATION_BEST_PRACTICES.md](DELETE_CONFIRMATION_BEST_PRACTICES.md)
