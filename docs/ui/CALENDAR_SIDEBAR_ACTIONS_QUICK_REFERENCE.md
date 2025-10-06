# Calendar Sidebar Actions - Quick Reference

**Last Updated:** 2025-10-06

## Overview

Quick reference for the calendar sidebar action buttons (Duplicate & Delete) implementation.

---

## Button Layout

```
┌─────────────────────────────────────────────┐
│  Calendar Event Edit Form                   │
│                                             │
│  [Title Input]                              │
│  [Status] [Priority]                        │
│  [Start Date] [Due Date]                    │
│  [Progress]                                 │
│  [Description]                              │
│  [Assignees]                                │
│                                             │
│  ───────────────────────────────────────    │
│  [Save Changes]         [Cancel]            │  ← Primary actions
│  ───────────────────────────────────────    │
│  [Duplicate]           [Delete]             │  ← Secondary actions
└─────────────────────────────────────────────┘
```

---

## Duplicate Button

### Usage

```html
<button type="button"
        hx-post="{% url 'common:work_item_duplicate' pk=work_item.pk %}"
        hx-target="#detailPanelBody"
        hx-swap="innerHTML"
        hx-indicator="#duplicateIndicator"
        class="...">
    <i class="fas fa-copy text-sm"></i>
    Duplicate
</button>
```

### Behavior

1. **Click** → Shows loading indicator
2. **Backend** → Creates copy with " (Copy)" suffix
3. **Response** → Returns edit form for duplicate
4. **Calendar** → Refreshes and shows new event
5. **Toast** → "Duplicated as '[Title] (Copy)'"

### Styling

```css
/* Duplicate button classes */
.flex-1                    /* Takes equal space */
.inline-flex items-center justify-center gap-2
.px-3 py-2                 /* Padding */
.text-sm font-medium       /* Typography */
.text-gray-700             /* Text color */
.bg-white                  /* Background */
.border border-gray-300    /* Border */
.rounded-lg                /* Border radius */
.hover:bg-gray-50 hover:border-gray-400  /* Hover state */
.transition-all shadow-sm  /* Animation */
```

### Permissions

- Requires: `common.add_workitem` OR `is_staff=True`
- Error: 403 with "You do not have permission to duplicate work items."

---

## Delete Button

### Usage

```html
<button type="button"
        hx-delete="{% url 'common:work_item_delete' pk=work_item.pk %}"
        hx-confirm="⚠️ Delete '{{ work_item.title }}'?

This action cannot be undone. The work item and all its data will be permanently deleted.

Click OK to confirm deletion."
        hx-swap="none"
        hx-on::after-request="
            if(event.detail.successful) {
                // Close sidebar
                document.getElementById('detailPanel').classList.remove('open');
                document.getElementById('detailBackdrop').classList.remove('open');
                document.getElementById('calendarContainer').classList.remove('detail-open');
                // Refresh calendar
                if(window.calendar) { window.calendar.refetchEvents(); }
                // Show success toast
                document.body.dispatchEvent(new CustomEvent('showToast', {
                    detail: { message: 'Work item deleted successfully', level: 'success' }
                }));
            }
        "
        class="...">
    <i class="fas fa-trash text-sm"></i>
    Delete
</button>
```

### Behavior

1. **Click** → Shows native browser confirmation dialog
2. **User confirms** → Sends DELETE request
3. **Backend** → Deletes work item (cascade to children)
4. **Response** → Returns 200 OK
5. **Sidebar** → Closes automatically
6. **Calendar** → Refreshes and removes event
7. **Toast** → "Work item deleted successfully"

### Styling

```css
/* Delete button classes */
.flex-1                    /* Takes equal space */
.inline-flex items-center justify-center gap-2
.px-3 py-2                 /* Padding */
.text-sm font-medium       /* Typography */
.text-white                /* Text color */
.bg-red-600                /* Background (destructive) */
.border border-red-600     /* Border */
.rounded-lg                /* Border radius */
.hover:bg-red-700 hover:border-red-700  /* Hover state */
.transition-all shadow-sm  /* Animation */
```

### Permissions

- Requires: Owner OR Superuser OR `common.delete_workitem`
- Error: 403 with "You do not have permission to delete this work item."

---

## Backend Endpoints

### Duplicate Endpoint

**URL:** `/oobc-management/work-items/<uuid:pk>/duplicate/`
**Method:** POST
**View:** `common.views.work_items.work_item_duplicate`

**Request:**
```http
POST /oobc-management/work-items/abc-123/duplicate/
X-CSRF-Token: ...
HX-Request: true
```

**Response (Success):**
```html
<!-- Edit form HTML for duplicated item -->
<form hx-post="..." ...>
    <input name="title" value="Original Title (Copy)" />
    ...
</form>
```

**Response Headers:**
```http
HX-Trigger: {
    "calendarRefresh": {"eventId": "new-uuid"},
    "showToast": {
        "message": "Duplicated as 'Title (Copy)'",
        "level": "success"
    }
}
```

**Response (Error):**
```http
HTTP 403 Forbidden
HX-Trigger: {
    "showToast": {
        "message": "You do not have permission to duplicate work items.",
        "level": "error"
    }
}
```

---

### Delete Endpoint

**URL:** `/oobc-management/work-items/<uuid:pk>/delete/`
**Method:** DELETE
**View:** `common.views.work_items.work_item_delete`

**Request:**
```http
DELETE /oobc-management/work-items/abc-123/delete/
X-CSRF-Token: ...
HX-Request: true
```

**Response (Success):**
```http
HTTP 200 OK
HX-Trigger: {
    "workItemDeleted": {
        "id": "abc-123",
        "title": "Original Title",
        "type": "Task"
    },
    "showToast": {
        "message": "Task 'Original Title' deleted successfully",
        "level": "success"
    },
    "refreshCalendar": true
}
```

**Response (Error):**
```http
HTTP 403 Forbidden
HX-Trigger: {
    "showToast": {
        "message": "You do not have permission to delete this work item.",
        "level": "error"
    }
}
```

---

## Toast Notifications

### Success Toast (Duplicate)

```javascript
{
    message: "Duplicated as 'Title (Copy)'",
    level: "success"
}
```

**Appearance:** Emerald gradient, auto-dismiss after 3s

---

### Success Toast (Delete)

```javascript
{
    message: "Work item deleted successfully",
    level: "success"
}
```

**Appearance:** Emerald gradient, auto-dismiss after 3s

---

### Error Toast (Permission Denied)

```javascript
{
    message: "You do not have permission to [action] work items.",
    level: "error"
}
```

**Appearance:** Rose gradient, auto-dismiss after 3s

---

## JavaScript Hooks

### Close Sidebar After Delete

```javascript
hx-on::after-request="
    if(event.detail.successful) {
        // Close sidebar
        document.getElementById('detailPanel').classList.remove('open');
        document.getElementById('detailBackdrop').classList.remove('open');
        document.getElementById('calendarContainer').classList.remove('detail-open');

        // Refresh calendar
        if(window.calendar) {
            window.calendar.refetchEvents();
        }

        // Show success toast
        document.body.dispatchEvent(new CustomEvent('showToast', {
            detail: {
                message: 'Work item deleted successfully',
                level: 'success'
            }
        }));
    }
"
```

**Why in template?**
- Need to close sidebar (client-side state)
- Need to refresh calendar (FullCalendar API)
- Cannot be done purely from backend HX-Trigger

---

## Testing Commands

### Manual Testing

1. **Open calendar sidebar:**
   ```
   Navigate to: /oobc-management/calendar/advanced-modern/
   Click any event
   Click "Edit" button
   ```

2. **Test Duplicate:**
   - Click "Duplicate"
   - Verify loading indicator shows
   - Verify edit form appears with " (Copy)" suffix
   - Verify calendar shows new event
   - Verify toast notification

3. **Test Delete:**
   - Click "Delete"
   - Verify confirmation dialog
   - Click "OK"
   - Verify sidebar closes
   - Verify calendar removes event
   - Verify toast notification

### Permission Testing

```python
# Test as regular user (no permissions)
user = User.objects.get(username='regular_user')
client.force_login(user)

# Should get 403 for duplicate
response = client.post(f'/oobc-management/work-items/{uuid}/duplicate/')
assert response.status_code == 403

# Should get 403 for delete
response = client.delete(f'/oobc-management/work-items/{uuid}/delete/')
assert response.status_code == 403
```

---

## Troubleshooting

### Duplicate button does nothing

**Check:**
1. CSRF token in form: `{% csrf_token %}`
2. HTMX loaded: `<script src="https://unpkg.com/htmx.org@1.9.10"></script>`
3. URL exists: `python manage.py show_urls | grep duplicate`
4. View imported: Check `common/views/__init__.py`

**Fix:**
```bash
cd src
python manage.py check
# Should show no errors
```

---

### Delete confirmation doesn't appear

**Check:**
1. Browser blocks native dialogs (rare)
2. HTMX version supports `hx-confirm` (1.9.10+)
3. Attribute syntax is correct (multiline string)

**Fix:**
```html
<!-- Ensure multiline string is properly formatted -->
hx-confirm="⚠️ Delete '{{ work_item.title }}'?

This action cannot be undone. The work item and all its data will be permanently deleted.

Click OK to confirm deletion."
```

---

### Sidebar doesn't close after delete

**Check:**
1. Element IDs match: `#detailPanel`, `#detailBackdrop`, `#calendarContainer`
2. `hx-on::after-request` syntax is correct
3. Event is successful: `event.detail.successful`

**Debug:**
```javascript
// Add console.log to debug
hx-on::after-request="
    console.log('After request:', event.detail);
    if(event.detail.successful) {
        console.log('Success - closing sidebar');
        // ... rest of code
    }
"
```

---

### Calendar doesn't refresh

**Check:**
1. `window.calendar` exists (FullCalendar initialized)
2. `refetchEvents()` method is available
3. Cache is invalidated: `invalidate_calendar_cache(user_id)`

**Debug:**
```javascript
// Check if calendar exists
if(window.calendar) {
    console.log('Calendar found:', window.calendar);
    window.calendar.refetchEvents();
} else {
    console.error('Calendar not initialized');
}
```

---

## Common Patterns

### Add Similar Button

```html
<!-- Archive button (example) -->
<button type="button"
        hx-post="{% url 'common:work_item_archive' pk=work_item.pk %}"
        hx-target="#detailPanelBody"
        hx-swap="innerHTML"
        hx-indicator="#archiveIndicator"
        class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all shadow-sm">
    <i class="fas fa-archive text-sm"></i>
    Archive
</button>

<div id="archiveIndicator" class="htmx-indicator text-center py-2">
    <i class="fas fa-spinner fa-spin text-blue-500 text-sm"></i>
    <span class="ml-2 text-sm text-gray-600">Archiving...</span>
</div>
```

---

### Custom Confirmation Modal

Replace `hx-confirm` with custom modal:

```html
<!-- Trigger modal instead of native confirm -->
<button type="button"
        onclick="openDeleteModal('{{ work_item.pk }}', '{{ work_item.title }}')"
        class="...">
    <i class="fas fa-trash text-sm"></i>
    Delete
</button>

<!-- Custom modal (in template) -->
<div id="deleteModal" class="hidden fixed inset-0 z-50 ...">
    <div class="bg-white rounded-xl p-6 ...">
        <h3>Confirm Deletion</h3>
        <p id="deleteMessage"></p>
        <button hx-delete="..." hx-target="#detailPanelBody">
            Confirm
        </button>
    </div>
</div>

<script>
function openDeleteModal(pk, title) {
    document.getElementById('deleteMessage').textContent =
        `Delete "${title}"? This action cannot be undone.`;
    document.getElementById('deleteModal').classList.remove('hidden');
}
</script>
```

---

## Related Files

**Templates:**
- `/src/templates/common/partials/calendar_event_edit_form.html`
- `/src/templates/common/partials/calendar_event_detail.html`
- `/src/templates/common/calendar_advanced_modern.html`

**Backend:**
- `/src/common/views/work_items.py`
- `/src/common/urls.py`
- `/src/common/views/__init__.py`

**Documentation:**
- [Full Implementation Guide](../../docs/improvements/UI/CALENDAR_SIDEBAR_DUPLICATE_DELETE_IMPLEMENTATION.md)
- [Calendar Inline Editing](CALENDAR_INLINE_EDITING_QUICK_REFERENCE.md)

---

## Quick Copy-Paste

### Basic Duplicate Button
```html
<button type="button"
        hx-post="{% url 'common:work_item_duplicate' pk=work_item.pk %}"
        hx-target="#detailPanelBody"
        hx-swap="innerHTML"
        hx-indicator="#duplicateIndicator"
        class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all shadow-sm">
    <i class="fas fa-copy text-sm"></i>
    Duplicate
</button>
<div id="duplicateIndicator" class="htmx-indicator text-center py-2">
    <i class="fas fa-spinner fa-spin text-blue-500 text-sm"></i>
    <span class="ml-2 text-sm text-gray-600">Duplicating...</span>
</div>
```

### Basic Delete Button
```html
<button type="button"
        hx-delete="{% url 'common:work_item_delete' pk=work_item.pk %}"
        hx-confirm="⚠️ Delete '{{ work_item.title }}'?

This action cannot be undone. The work item and all its data will be permanently deleted.

Click OK to confirm deletion."
        hx-swap="none"
        hx-on::after-request="
            if(event.detail.successful) {
                document.getElementById('detailPanel').classList.remove('open');
                document.getElementById('detailBackdrop').classList.remove('open');
                document.getElementById('calendarContainer').classList.remove('detail-open');
                if(window.calendar) { window.calendar.refetchEvents(); }
                document.body.dispatchEvent(new CustomEvent('showToast', {
                    detail: { message: 'Work item deleted successfully', level: 'success' }
                }));
            }
        "
        class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-white bg-red-600 border border-red-600 rounded-lg hover:bg-red-700 hover:border-red-700 transition-all shadow-sm">
    <i class="fas fa-trash text-sm"></i>
    Delete
</button>
```

---

**End of Quick Reference**
