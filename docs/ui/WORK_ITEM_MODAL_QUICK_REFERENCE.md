# WorkItem Modal - Quick Reference

**Last Updated:** 2025-10-06

---

## Usage

### 1. Include Modal Container in Template

```django
{% extends "base.html" %}

{% block content %}
    <!-- Your page content -->

    <!-- Include modal container -->
    {% include 'common/components/task_modal.html' %}
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script src="{% static 'common/js/htmx-focus-management.js' %}"></script>
{% endblock %}
```

---

## 2. Trigger Modal from Calendar Event

```javascript
// FullCalendar event click handler
eventClick: function(info) {
    const workItemId = info.event.id;

    // Load modal content via HTMX
    htmx.ajax('GET', `/work-items/${workItemId}/modal/`, {
        target: '#taskModalContent',
        swap: 'innerHTML'
    });

    // Show modal
    document.getElementById('taskModal').classList.remove('hidden');
}
```

---

## 3. Backend View Context

```python
def work_item_modal(request, work_item_id):
    work_item = get_object_or_404(WorkItem, pk=work_item_id)

    context = {
        'work_item': work_item,
        'children': work_item.get_children(),
        'ancestors': work_item.get_ancestors(),
        'breadcrumb': _build_breadcrumb(work_item),
        'delete_url': reverse('common:work_item_delete', kwargs={'pk': work_item.pk}),
        'edit_url': reverse('common:work_item_edit', kwargs={'pk': work_item.pk}),
    }

    return render(request, 'common/partials/work_item_modal.html', context)
```

---

## Required Template Variables

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `work_item` | WorkItem | Yes | Work item instance |
| `children` | QuerySet | No | Child work items |
| `breadcrumb` | String | No | Hierarchy breadcrumb |
| `delete_url` | URL | Yes | Delete endpoint |
| `edit_url` | URL | Yes | Edit page URL |

---

## Modal Features

### Automatic Features
- ✅ Close on backdrop click
- ✅ Close on Escape key
- ✅ Focus trap
- ✅ Calendar refresh after delete
- ✅ HTMX integration
- ✅ Accessibility (WCAG 2.1 AA)

### Badges Displayed
- Type badge (Project/Activity/Task)
- Status badge (Completed/At Risk/Blocked/Not Started/In Progress)
- Priority badge (Critical/Urgent/High/Normal/Low)

### Information Sections
- Description
- Progress bar
- Timeline (start/due dates)
- Assignees
- Teams
- Type-specific data
- Child items (if applicable)

---

## HTMX Delete Flow

```
User clicks Delete
    ↓
Confirmation dialog
    ↓
HTMX DELETE request
    ↓
Backend returns 204 No Content
    ↓
hx-on::after-request fires
    ↓
Modal closes instantly
    ↓
Calendar refreshes
    ↓
No page reload
```

---

## Color Reference

### Status Colors
- Completed: `bg-emerald-100 text-emerald-700`
- At Risk: `bg-rose-100 text-rose-700`
- Blocked: `bg-red-100 text-red-700`
- Not Started: `bg-amber-100 text-amber-700`
- In Progress: `bg-blue-100 text-blue-700`

### Type Colors
- Project: `bg-blue-100 text-blue-700`
- Activity: `bg-emerald-100 text-emerald-700`
- Task: `bg-purple-100 text-purple-700`

### Priority Colors
- Critical: `bg-rose-100 text-rose-700`
- Urgent: `bg-orange-100 text-orange-700`
- High: `bg-amber-100 text-amber-700`
- Normal: `bg-blue-100 text-blue-700`
- Low: `bg-gray-100 text-gray-600`

---

## Testing Checklist

### Visual
- [ ] Modal opens centered
- [ ] Badges display correctly
- [ ] Progress bar shows percentage
- [ ] Timeline shows dates or "No dates set"
- [ ] Footer buttons styled correctly

### Functional
- [ ] Close button (X) works
- [ ] Edit button navigates to edit page
- [ ] Delete button shows confirmation
- [ ] Delete closes modal instantly
- [ ] Calendar refreshes after delete

### Accessibility
- [ ] Tab key navigates elements
- [ ] Escape key closes modal
- [ ] Screen reader announces title
- [ ] ARIA attributes present

---

## Troubleshooting

### Modal doesn't close after delete
**Check:** `hx-on::after-request` handler
```html
hx-on::after-request="if(event.detail.successful) {
    document.getElementById('taskModal').classList.add('hidden');
    if(window.calendar) { window.calendar.refetchEvents(); }
}"
```

### Calendar doesn't refresh
**Check:** FullCalendar instance exists
```javascript
if(window.calendar) {
    window.calendar.refetchEvents();
}
```

### Focus trap not working
**Check:** JavaScript file included
```django
<script src="{% static 'common/js/htmx-focus-management.js' %}"></script>
```

---

## Related Documentation

- [Full Documentation](/docs/improvements/UI/WORK_ITEM_MODAL_STANDARDIZATION.md)
- [UI Components Guide](/docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md)
- [Modal & Dialogs Section](/docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md#modal--dialogs)

---

**Quick Start:**
1. Include modal container in template
2. Add HTMX focus management script
3. Trigger modal with event click
4. Backend returns modal content
5. Done!
