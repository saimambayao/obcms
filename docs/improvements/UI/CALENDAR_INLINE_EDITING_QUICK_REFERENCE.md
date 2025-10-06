# Calendar Inline Editing - Quick Reference

**For**: Developers extending or maintaining the feature
**Last Updated**: 2025-10-06

---

## File Locations

| Component | File Path |
|-----------|-----------|
| **Quick Edit Form** | `/src/common/forms/work_items.py` → `WorkItemQuickEditForm` |
| **Detail View** | `/src/common/views/work_items.py` → `work_item_sidebar_detail` |
| **Edit View** | `/src/common/views/work_items.py` → `work_item_sidebar_edit` |
| **Detail Template** | `/src/templates/common/partials/calendar_event_detail.html` |
| **Edit Template** | `/src/templates/common/partials/calendar_event_edit_form.html` |
| **URLs** | `/src/common/urls.py` → sidebar detail/edit patterns |
| **JavaScript** | `/src/templates/common/calendar_advanced_modern.html` → event handlers |

---

## URL Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/oobc-management/work-items/{id}/sidebar/detail/` | GET | Load detail view HTML |
| `/oobc-management/work-items/{id}/sidebar/edit/` | GET | Load edit form HTML |
| `/oobc-management/work-items/{id}/sidebar/edit/` | POST | Submit form, return detail view |

---

## HTMX Flow Diagram

```
┌──────────────────────────────────────────────────────┐
│                  User Interaction                     │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  Event Click → htmx.ajax('GET', detailUrl)           │
│  Target: #detailPanelBody                            │
│  Swap: innerHTML                                     │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  Backend: work_item_sidebar_detail(request, pk)      │
│  Returns: calendar_event_detail.html                 │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  Detail View Rendered in #detailPanelBody            │
│  Contains: Edit button with hx-get attribute         │
└──────────────────────────────────────────────────────┘
                      │
                      ▼ (User clicks Edit)
┌──────────────────────────────────────────────────────┐
│  HTMX GET: /sidebar/edit/                            │
│  Target: #detailPanelBody                            │
│  Swap: innerHTML                                     │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  Backend: work_item_sidebar_edit(request, pk) [GET]  │
│  Returns: calendar_event_edit_form.html              │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  Edit Form Rendered in #detailPanelBody              │
│  Contains: Form with hx-post attribute               │
└──────────────────────────────────────────────────────┘
                      │
                      ▼ (User submits form)
┌──────────────────────────────────────────────────────┐
│  HTMX POST: /sidebar/edit/                           │
│  Target: #detailPanelBody                            │
│  Swap: innerHTML                                     │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  Backend: work_item_sidebar_edit(request, pk) [POST] │
│  Valid: Save → Return detail view + HX-Trigger       │
│  Invalid: Return form with errors                    │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  HTMX Swaps Response into #detailPanelBody           │
│  Triggers HX-Trigger events                          │
└──────────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│  Event Listeners:                                    │
│  - calendarRefresh → calendar.refetchEvents()        │
│  - showToast → showToast(message, level)             │
└──────────────────────────────────────────────────────┘
```

---

## Code Snippets

### Add New Field to Quick Edit Form

**File**: `/src/common/forms/work_items.py`

```python
class WorkItemQuickEditForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = [
            'title',
            'status',
            'priority',
            'start_date',
            'due_date',
            'description',
            'assignees',
            'progress',
            'new_field_here',  # Add new field
        ]
        widgets = {
            # ... existing widgets ...
            'new_field_here': forms.TextInput(attrs={
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500',
            }),
        }
```

**Then update template**: `/src/templates/common/partials/calendar_event_edit_form.html`

```html
<!-- Add field in form -->
<div>
    <label for="{{ form.new_field_here.id_for_label }}" class="block text-sm font-medium text-gray-700 mb-1">
        New Field Label
    </label>
    {{ form.new_field_here }}
    {% if form.new_field_here.errors %}
    <p class="mt-1 text-xs text-red-600">{{ form.new_field_here.errors.0 }}</p>
    {% endif %}
</div>
```

---

### Add Custom Validation

**File**: `/src/common/forms/work_items.py`

```python
class WorkItemQuickEditForm(forms.ModelForm):
    # ... existing code ...

    def clean(self):
        cleaned_data = super().clean()

        # Existing validation
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        if start_date and due_date and start_date > due_date:
            raise ValidationError({
                'due_date': 'Due date must be after start date'
            })

        # Add custom validation
        progress = cleaned_data.get('progress')
        status = cleaned_data.get('status')
        if status == WorkItem.STATUS_COMPLETED and progress < 100:
            raise ValidationError({
                'progress': 'Completed work items must have 100% progress'
            })

        return cleaned_data
```

---

### Trigger Additional Events After Save

**File**: `/src/common/views/work_items.py`

```python
@login_required
@require_http_methods(["GET", "POST"])
def work_item_sidebar_edit(request, pk):
    # ... existing code ...

    if request.method == 'POST':
        form = WorkItemQuickEditForm(request.POST, instance=work_item)
        if form.is_valid():
            work_item = form.save()

            # ... existing save logic ...

            # Trigger multiple events
            response['HX-Trigger'] = json.dumps({
                'calendarRefresh': {'eventId': str(work_item.pk)},
                'showToast': {
                    'message': f'{work_item.get_work_type_display()} updated successfully',
                    'level': 'success'
                },
                'customEvent': {'data': 'your-custom-data'},  # Add custom event
                'anotherEvent': True,  # Boolean event trigger
            })
            return response
```

**Then add listener in JavaScript**:

```javascript
document.body.addEventListener('customEvent', function(event) {
    console.log('Custom event received:', event.detail);
    // Your custom logic here
});
```

---

### Modify Toast Notification Style

**File**: `/src/templates/common/calendar_advanced_modern.html`

```javascript
function showToast(message, level = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `
        flex items-start gap-3 p-4 rounded-lg shadow-lg mb-3 transform transition-all duration-300
        ${level === 'success' ? 'bg-emerald-50 border border-emerald-200' : ''}
        ${level === 'error' ? 'bg-red-50 border border-red-200' : ''}
        ${level === 'warning' ? 'bg-amber-50 border border-amber-200' : ''}
        ${level === 'info' ? 'bg-blue-50 border border-blue-200' : ''}
        ${level === 'custom' ? 'bg-purple-50 border border-purple-200' : ''}  // Add custom level
    `;

    const icon = {
        success: 'fa-check-circle text-emerald-600',
        error: 'fa-exclamation-circle text-red-600',
        warning: 'fa-exclamation-triangle text-amber-600',
        info: 'fa-info-circle text-blue-600',
        custom: 'fa-star text-purple-600',  // Add custom icon
    }[level] || 'fa-info-circle text-blue-600';

    // ... rest of toast creation ...
}
```

---

### Add Loading State to Edit Button

**File**: `/src/templates/common/partials/calendar_event_detail.html`

```html
<button hx-get="{% url 'common:work_item_sidebar_edit' pk=work_item.pk %}"
        hx-target="#detailPanelBody"
        hx-swap="innerHTML"
        hx-indicator="#detailPanelLoading"
        class="flex-1 inline-flex items-center justify-center px-4 py-2.5 bg-gradient-to-r from-blue-500 to-emerald-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-emerald-600 transition-all shadow-sm">
    <i class="fas fa-edit mr-2"></i>
    Edit
</button>

<!-- Loading Indicator -->
<div id="detailPanelLoading" class="htmx-indicator text-center py-2">
    <i class="fas fa-spinner fa-spin text-blue-500"></i>
    <span class="ml-2 text-sm text-gray-600">Loading...</span>
</div>
```

---

## Common Tasks

### Add Permission Check for Specific Action

```python
@login_required
@require_http_methods(["GET", "POST"])
def work_item_sidebar_edit(request, pk):
    work_item = get_object_or_404(WorkItem, pk=pk)
    permissions = get_work_item_permissions(request.user, work_item)

    # Custom permission check
    if not permissions['can_edit'] or not request.user.is_staff:
        return HttpResponse(status=403, headers={
            'HX-Trigger': json.dumps({
                'showToast': {
                    'message': 'Only staff members can edit work items.',
                    'level': 'error'
                }
            })
        })

    # ... rest of view logic ...
```

---

### Debug HTMX Request/Response

**Add to JavaScript**:

```javascript
// Log all HTMX requests
document.body.addEventListener('htmx:beforeRequest', function(event) {
    console.log('HTMX Request:', event.detail);
});

// Log all HTMX responses
document.body.addEventListener('htmx:afterRequest', function(event) {
    console.log('HTMX Response:', event.detail);
});

// Log HX-Trigger events
document.body.addEventListener('htmx:trigger', function(event) {
    console.log('HX-Trigger:', event.detail);
});
```

---

### Customize Form Widget Styling

**File**: `/src/common/forms/work_items.py`

```python
# Standard widget classes
BASE_INPUT_CLASS = 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500'
SELECT_CLASS = BASE_INPUT_CLASS + ' appearance-none'
TEXTAREA_CLASS = BASE_INPUT_CLASS

# Apply to widgets
class WorkItemQuickEditForm(forms.ModelForm):
    class Meta:
        widgets = {
            'title': forms.TextInput(attrs={'class': BASE_INPUT_CLASS}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3}),
        }
```

---

## Testing Helpers

### Test Permission Scenarios

```python
# tests/test_work_item_sidebar.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from common.work_item_model import WorkItem

User = get_user_model()

class WorkItemSidebarTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.work_item = WorkItem.objects.create(
            title='Test Work Item',
            created_by=self.owner,
            work_type='task'
        )

    def test_owner_can_edit(self):
        self.client.login(username='owner', password='pass')
        response = self.client.get(f'/oobc-management/work-items/{self.work_item.pk}/sidebar/edit/')
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_edit(self):
        self.client.login(username='other', password='pass')
        response = self.client.get(f'/oobc-management/work-items/{self.work_item.pk}/sidebar/edit/')
        self.assertEqual(response.status_code, 403)
```

---

### Test Form Validation

```python
def test_due_date_validation(self):
    self.client.login(username='owner', password='pass')
    response = self.client.post(
        f'/oobc-management/work-items/{self.work_item.pk}/sidebar/edit/',
        {
            'title': 'Updated Title',
            'start_date': '2025-10-15',
            'due_date': '2025-10-10',  # Before start date
        }
    )
    self.assertContains(response, 'Due date must be after start date')
```

---

## Troubleshooting

### Issue: Form Doesn't Submit

**Check**:
1. CSRF token is present: `{% csrf_token %}`
2. Form has `hx-post` attribute
3. Form has `hx-target` and `hx-swap` attributes
4. JavaScript console for errors

---

### Issue: Calendar Doesn't Refresh

**Check**:
1. Backend sends `HX-Trigger` header: `response['HX-Trigger'] = json.dumps({...})`
2. `calendarRefresh` event listener is attached
3. `calendar` variable is defined and initialized
4. Browser console shows "Calendar refresh triggered:" log

---

### Issue: Toast Doesn't Appear

**Check**:
1. Backend sends `HX-Trigger` header with `showToast`
2. `showToast` event listener is attached
3. `showToast()` function is defined
4. Toast container is created: `document.getElementById('toast-container')`
5. Browser console for JavaScript errors

---

## Performance Tips

### Reduce HTMX Payload Size

**Use minimal templates**:
- Only include necessary fields in detail/edit templates
- Avoid loading related objects unless needed
- Use `select_related()` and `prefetch_related()` in views

```python
@login_required
def work_item_sidebar_detail(request, pk):
    work_item = get_object_or_404(
        WorkItem.objects.select_related('created_by', 'parent')
                        .prefetch_related('assignees'),
        pk=pk
    )
    # ... rest of view ...
```

---

### Cache Template Fragments

```django
{% load cache %}

{% cache 600 work_item_detail work_item.id work_item.updated_at %}
    <!-- Detail view content -->
{% endcache %}
```

---

### Debounce Rapid Edits

If users are submitting forms too quickly:

```javascript
// Prevent double-submission
let isSubmitting = false;

document.body.addEventListener('htmx:beforeRequest', function(event) {
    if (event.detail.elt.tagName === 'FORM' && isSubmitting) {
        event.preventDefault();
        return;
    }
    isSubmitting = true;
});

document.body.addEventListener('htmx:afterRequest', function(event) {
    isSubmitting = false;
});
```

---

## Related Files

| File | Purpose |
|------|---------|
| `/src/common/work_item_model.py` | WorkItem model definition |
| `/src/common/views/work_items.py` | All work item views (list, detail, create, edit, delete) |
| `/src/common/forms/work_items.py` | WorkItemForm (full form) + WorkItemQuickEditForm |
| `/src/common/urls.py` | URL patterns for work items |
| `/src/templates/work_items/` | Full-page templates for work items |
| `/src/templates/common/partials/` | Sidebar partial templates |

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-10-06
