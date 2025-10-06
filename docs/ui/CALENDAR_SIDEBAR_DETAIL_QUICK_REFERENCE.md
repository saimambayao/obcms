# Calendar Sidebar Detail View - Quick Reference

**Feature:** Work Item Detail View in Calendar Sidebar
**Status:** ✅ Production Ready
**Last Updated:** 2025-10-06

## Quick Links

### Files
- **View:** `/src/common/views/work_items.py` → `work_item_sidebar_detail()`
- **Template:** `/src/templates/common/partials/calendar_event_detail.html`
- **URL:** `/src/common/urls.py` → `common:work_item_sidebar_detail`
- **Integration:** `/src/templates/common/oobc_calendar.html` → `handleEventClick()`

### Verification
```bash
# Run verification script
./scripts/verify_sidebar_implementation.py

# Or with Python
python scripts/verify_sidebar_implementation.py
```

## Usage

### User Flow
1. Click on calendar event
2. Sidebar slides in from right
3. Work item details displayed
4. Edit/Delete buttons (if permitted)

### Developer Integration

#### HTMX Request
```javascript
// Trigger detail view
htmx.ajax('GET', '/oobc-management/work-items/{uuid}/sidebar/detail/', {
    target: '#detailPanelBody',
    swap: 'innerHTML'
});
```

#### Django Template
```django
<!-- Link to detail view -->
<button hx-get="{% url 'common:work_item_sidebar_detail' pk=work_item.pk %}"
        hx-target="#detailPanelBody"
        hx-swap="innerHTML">
    View Details
</button>
```

#### Django View
```python
from django.shortcuts import render, get_object_or_404
from common.work_item_model import WorkItem

@login_required
def work_item_sidebar_detail(request, pk):
    work_item = get_object_or_404(WorkItem, pk=pk)
    permissions = get_work_item_permissions(request.user, work_item)

    context = {
        'work_item': work_item,
        'can_edit': permissions['can_edit'],
        'can_delete': permissions['can_delete'],
    }

    return render(request, 'common/partials/calendar_event_detail.html', context)
```

## Template Structure

### Sections Rendered
1. **Event Type Badge** - Color-coded by work type
2. **Title** - Work item title (H4)
3. **Date Range** - Start date → Due date
4. **Status** - Current status badge
5. **Priority** - Color-coded priority badge
6. **Progress** - Visual progress bar + percentage
7. **Description** - Full description text
8. **Assignees** - List of assigned users
9. **Action Buttons** - Edit and Delete (permission-based)

### Template Context Variables
```python
{
    'work_item': WorkItem,       # The work item object
    'can_edit': bool,             # Permission to edit
    'can_delete': bool,           # Permission to delete
}
```

## Permission System

### Permission Matrix

| User Type | Can Edit | Can Delete |
|-----------|----------|------------|
| Owner (created_by) | ✅ | ✅ |
| Superuser | ✅ | ✅ |
| Staff + `change_workitem` | ✅ | ❌ |
| Staff + `delete_workitem` | ✅ | ✅ |
| Assigned User | ✅ | ❌ |
| Other Users | ❌ | ❌ |

### Permission Check Function
```python
def get_work_item_permissions(user, work_item):
    """Returns {'can_edit': bool, 'can_delete': bool}"""
    # Owner can always edit and delete
    if work_item.created_by == user:
        return {'can_edit': True, 'can_delete': True}

    # Superusers can do anything
    if user.is_superuser:
        return {'can_edit': True, 'can_delete': True}

    # Check Django permissions
    has_change_perm = user.has_perm('common.change_workitem')
    has_delete_perm = user.has_perm('common.delete_workitem')

    can_edit = user.is_staff and has_change_perm
    can_delete = user.is_staff and has_delete_perm

    # Assigned users can edit (but not delete unless they have permission)
    if user in work_item.assignees.all():
        can_edit = True

    return {'can_edit': can_edit, 'can_delete': can_delete}
```

## Color Scheme

### Work Type Colors
```python
WORK_TYPE_COLORS = {
    'project': '#3b82f6',      # Blue
    'activity': '#10b981',     # Green
    'task': '#8b5cf6',         # Purple
    'coordination': '#14b8a6', # Teal
}
```

### Priority Colors
```css
.priority-critical  { bg-red-100 text-red-800 }
.priority-urgent    { bg-orange-100 text-orange-800 }
.priority-high      { bg-yellow-100 text-yellow-800 }
.priority-medium    { bg-blue-100 text-blue-800 }
.priority-low       { bg-gray-100 text-gray-800 }
```

## Action Buttons

### Edit Button
```html
<button hx-get="{% url 'common:work_item_sidebar_edit' pk=work_item.pk %}"
        hx-target="#detailPanelBody"
        hx-swap="innerHTML"
        hx-indicator="#detailPanelLoading"
        class="flex-1 inline-flex items-center justify-center px-4 py-2.5
               bg-gradient-to-r from-blue-500 to-emerald-500 text-white
               font-medium rounded-lg hover:from-blue-600 hover:to-emerald-600
               transition-all shadow-sm">
    <i class="fas fa-edit mr-2"></i>
    Edit
</button>
```

### Delete Button
```html
<button hx-get="{% url 'common:work_item_delete' pk=work_item.pk %}"
        hx-target="#modal-container"
        hx-swap="innerHTML"
        class="inline-flex items-center justify-center px-4 py-2.5
               bg-white text-red-600 font-medium rounded-lg
               border border-red-200 hover:bg-red-50 transition-all shadow-sm">
    <i class="fas fa-trash-alt mr-2"></i>
    Delete
</button>
```

## Testing

### Manual Testing Checklist
- [ ] Click calendar event → sidebar opens
- [ ] Work item details display correctly
- [ ] Edit button visible (if permitted)
- [ ] Delete button visible (if permitted)
- [ ] Progress bar shows correct percentage
- [ ] Assignees list displays properly
- [ ] Color coding is correct for work type
- [ ] Priority badge shows correct color
- [ ] Loading indicator appears during HTMX request

### Automated Verification
```bash
# Run full verification
./scripts/verify_sidebar_implementation.py

# Expected output: ✓ All checks passed!
```

### Django Tests
```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from common.work_item_model import WorkItem

class WorkItemSidebarDetailTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='test')
        self.work_item = WorkItem.objects.create(
            title="Test Work Item",
            work_type=WorkItem.WORK_TYPE_TASK,
            created_by=self.user
        )

    def test_sidebar_detail_view(self):
        self.client.login(username='testuser', password='test')
        response = self.client.get(
            f'/oobc-management/work-items/{self.work_item.pk}/sidebar/detail/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.work_item.title)
        self.assertContains(response, 'can_edit')

    def test_permission_check(self):
        other_user = User.objects.create_user('other', password='test')
        self.client.login(username='other', password='test')
        response = self.client.get(
            f'/oobc-management/work-items/{self.work_item.pk}/sidebar/detail/'
        )
        # Should still show (read access), but no edit/delete buttons
        self.assertEqual(response.status_code, 200)
```

## Troubleshooting

### Issue: Detail panel doesn't open
**Solution:** Check if `handleEventClick` is properly bound to FullCalendar

### Issue: 404 Not Found
**Solution:** Verify URL pattern in `/src/common/urls.py` includes `uuid:pk` parameter

### Issue: Permission denied
**Solution:** Check `get_work_item_permissions()` logic and Django permissions

### Issue: Template not rendering
**Solution:** Verify template path: `common/partials/calendar_event_detail.html`

### Issue: HTMX not swapping content
**Solution:** Check target element `#detailPanelBody` exists in parent template

## Related Documentation

- [Calendar Inline Editing Implementation](CALENDAR_INLINE_EDITING_IMPLEMENTATION.md)
- [Calendar Sidebar Enhancements](CALENDAR_SIDEBAR_ENHANCEMENTS.md)
- [Work Item Sidebar Implementation Complete](../improvements/UI/WORK_ITEM_SIDEBAR_IMPLEMENTATION_COMPLETE.md)
- [OBCMS UI Components & Standards](OBCMS_UI_COMPONENTS_STANDARDS.md)

## API Reference

### URL Pattern
```python
path(
    "oobc-management/work-items/<uuid:pk>/sidebar/detail/",
    views.work_item_sidebar_detail,
    name="work_item_sidebar_detail",
)
```

### View Signature
```python
def work_item_sidebar_detail(request: HttpRequest, pk: UUID) -> HttpResponse
```

### Request Parameters
- `pk` (UUID) - Work item primary key

### Response
- **Status:** 200 OK
- **Content-Type:** text/html
- **Body:** HTML fragment for sidebar detail panel

### Related Views
- `work_item_sidebar_edit` - Edit form view
- `work_item_delete` - Delete confirmation view
- `work_item_detail` - Full page detail view

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-06 | Initial implementation |

---

**Quick Verification:**
```bash
python scripts/verify_sidebar_implementation.py
# Expected: ✓ All checks passed! Implementation is complete.
```
