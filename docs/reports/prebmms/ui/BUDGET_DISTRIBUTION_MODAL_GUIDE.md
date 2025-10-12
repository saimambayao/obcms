# Budget Distribution Modal - Implementation Guide

**Status:** Complete
**Date:** 2025-10-06
**Component:** `/src/templates/monitoring/partials/budget_distribution_modal.html`

---

## Overview

Interactive modal for distributing PPA (Programs, Projects, Activities) budget across WorkItems using three different methods:

1. **Equal Distribution** - Split budget equally across all work items
2. **Weighted Distribution** - Assign percentage weights (must sum to 100%)
3. **Manual Allocation** - Manually set amounts (must match total budget)

---

## Features

### Core Functionality
- **Three distribution methods** with real-time preview
- **Live validation** with visual feedback (green/red indicators)
- **Currency formatting** (₱ Philippine Peso with comma separators)
- **Smooth animations** (300ms transitions, fade with scale)
- **Keyboard accessibility** (Tab navigation, Escape to close)

### UI/UX Highlights
- **Radio card selection** with emerald border when active
- **Percentage sliders** for weighted distribution
- **Running totals** that update in real-time
- **Visual progress indicators** (emerald for valid, red for invalid)
- **Disabled submit button** until validation passes
- **Loading spinner** during submission

---

## Usage

### 1. Include Modal in Template

```django
{% include 'monitoring/partials/budget_distribution_modal.html' with entry=entry work_items_json=work_items_json %}
```

### 2. Required Context Variables

The Django view must provide:

```python
from django.utils.safestring import mark_safe
import json

def your_view(request, entry_id):
    entry = MonitoringEntry.objects.get(id=entry_id)

    # Get all work items for this PPA
    work_items = WorkItem.objects.filter(
        ppa_entry=entry
    ).values('id', 'title', 'work_type', 'allocated_budget')

    # Prepare JSON data for Alpine.js
    work_items_data = []
    for item in work_items:
        work_items_data.append({
            'id': item['id'],
            'title': item['title'],
            'work_type': item['work_type'],
            'work_type_display': item.get_work_type_display(),
            'current_budget': float(item['allocated_budget'] or 0)
        })

    context = {
        'entry': entry,
        'work_items_json': mark_safe(json.dumps(work_items_data))
    }

    return render(request, 'monitoring/your_template.html', context)
```

### 3. Open Modal Trigger

Add a button to open the modal:

```html
<button
    type="button"
    hx-get="{% url 'monitoring:distribute_budget_modal' entry.id %}"
    hx-target="#modal-container"
    hx-swap="innerHTML"
    class="px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg hover:from-blue-700 hover:to-teal-600 transition-all"
>
    <i class="fas fa-coins mr-2"></i>
    Distribute Budget
</button>

<!-- Modal container -->
<div id="modal-container"></div>
```

---

## Backend Integration

### API Endpoint

**URL:** `POST /monitoring/entries/{id}/distribute-budget/`

**Expected Request Format:**

```json
{
  "method": "equal|weighted|manual",
  "distribution": {
    "123": 50000.00,
    "124": 75000.00,
    "125": 25000.00
  }
}
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "message": "Budget distributed successfully",
  "distribution": {
    "123": 50000.00,
    "124": 75000.00,
    "125": 25000.00
  },
  "total_allocated": 150000.00
}
```

**Error Response (400 Bad Request):**

```json
{
  "success": false,
  "error": "Total allocated amount does not match PPA budget"
}
```

### Django View Implementation

```python
# src/monitoring/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json

@require_POST
def distribute_budget(request, entry_id):
    """
    Distribute PPA budget across work items.

    Supports three methods:
    - equal: Split equally
    - weighted: Percentage-based
    - manual: User-defined amounts
    """
    try:
        entry = MonitoringEntry.objects.get(id=entry_id)

        # Parse request data
        data = json.loads(request.body)
        method = data.get('method')
        distribution = data.get('distribution', {})

        # Validate method
        if method not in ['equal', 'weighted', 'manual']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid distribution method'
            }, status=400)

        # Calculate total allocated
        total_allocated = sum(
            Decimal(str(amount))
            for amount in distribution.values()
        )

        # Validate total matches PPA budget
        budget_variance = abs(entry.allocated_budget - total_allocated)
        if budget_variance > Decimal('0.01'):
            return JsonResponse({
                'success': False,
                'error': f'Total allocated ({total_allocated}) does not match PPA budget ({entry.allocated_budget})'
            }, status=400)

        # Update work items
        with transaction.atomic():
            for work_item_id, amount in distribution.items():
                WorkItem.objects.filter(id=work_item_id).update(
                    allocated_budget=Decimal(str(amount))
                )

        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'Budget distributed successfully',
            'distribution': {
                str(k): float(v) for k, v in distribution.items()
            },
            'total_allocated': float(total_allocated)
        })

    except MonitoringEntry.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'PPA entry not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

### URL Configuration

```python
# src/monitoring/urls.py

urlpatterns = [
    # ...
    path(
        'entries/<int:entry_id>/distribute-budget/',
        views.distribute_budget,
        name='distribute_budget'
    ),
]
```

---

## HTMX Integration

### Modal Loading Pattern

```html
<!-- Trigger button with HTMX -->
<button
    hx-get="{% url 'monitoring:distribute_budget_modal' entry.id %}"
    hx-target="#modal-container"
    hx-swap="innerHTML"
    hx-indicator="#loading-spinner"
>
    Distribute Budget
</button>

<!-- Loading indicator -->
<div id="loading-spinner" class="htmx-indicator">
    <i class="fas fa-spinner fa-spin"></i> Loading...
</div>
```

### Post-Submission Updates

The modal automatically triggers these events after successful submission:

```javascript
// 1. Custom event: budget-distributed
window.addEventListener('budget-distributed', (e) => {
    console.log('Budget distributed:', e.detail);
    // Refresh stats, tables, or other UI elements
});

// 2. HTMX trigger: refresh-stats (if htmx available)
// Use this to reload stats cards or tables:
<div hx-get="/monitoring/stats/" hx-trigger="refresh-stats from:body">
    <!-- Stats content -->
</div>

// 3. Toast notification: show-toast
window.addEventListener('show-toast', (e) => {
    const { message, type } = e.detail;
    // Display toast notification
});
```

---

## Validation Rules

### Equal Distribution
- **Auto-calculated:** Budget divided equally by number of work items
- **Always valid:** No user input required

### Weighted Distribution
- **Rule:** Total weight percentages must sum to exactly 100%
- **Tolerance:** ±0.01% allowed
- **Visual feedback:**
  - Green border when valid (sum = 100%)
  - Red border when invalid (sum ≠ 100%)
- **Submit disabled:** Until weights sum to 100%

### Manual Allocation
- **Rule:** Total allocated amounts must equal PPA budget
- **Tolerance:** ±₱0.01 allowed
- **Visual feedback:**
  - Green border when valid (matches budget)
  - Red border when invalid (doesn't match)
- **Submit disabled:** Until total matches budget

---

## Accessibility Features

### Keyboard Navigation
- **Tab:** Navigate through fields
- **Escape:** Close modal
- **Enter:** Submit form (when valid)
- **Arrow keys:** Adjust sliders

### Screen Reader Support
- **ARIA labels:** All inputs have descriptive labels
- **ARIA live regions:** Validation messages announced
- **Role attributes:** Modal, dialog roles set
- **Focus trap:** Focus stays within modal when open

### Touch Targets
- **Minimum size:** 48x48px (WCAG AA compliant)
- **Sufficient spacing:** 8px minimum between interactive elements

### Color Contrast
- **Text contrast:** 4.5:1 minimum ratio
- **Interactive elements:** High contrast borders
- **Error states:** Red with sufficient contrast

---

## Styling Standards

### Colors
- **Primary gradient:** `from-blue-600 to-teal-500`
- **Success:** `emerald-500` (valid states)
- **Error:** `red-600` (invalid states)
- **Neutral:** `gray-200` (default borders)

### Borders & Radius
- **Modal container:** `rounded-xl`
- **Radio cards:** `rounded-xl`, `border-2`
- **Input fields:** `rounded-lg`
- **Active state:** `border-emerald-500`, `bg-emerald-50`

### Spacing
- **Card padding:** `p-4`
- **Modal padding:** `px-6 py-6`
- **Grid gap:** `gap-4`
- **Input height:** `min-h-[40px]` (accessibility)

### Animations
- **Modal enter:** 300ms ease-out, opacity + scale
- **Modal leave:** 200ms ease-in, opacity + scale
- **Backdrop:** Fade 300ms
- **Input transitions:** 200ms all properties

---

## Testing Checklist

### Functional Tests
- [ ] Equal distribution calculates correctly
- [ ] Weighted sliders sync with number inputs
- [ ] Manual input accepts currency values
- [ ] Validation prevents invalid submissions
- [ ] Success closes modal and shows toast
- [ ] Error displays inline message

### UI/UX Tests
- [ ] Modal opens with smooth animation
- [ ] Method selection updates configuration section
- [ ] Real-time validation indicators work
- [ ] Currency formatting displays correctly
- [ ] Submit button enables/disables properly
- [ ] Loading spinner shows during submission

### Accessibility Tests
- [ ] Keyboard navigation works (Tab, Escape, Enter)
- [ ] Focus trap keeps focus in modal
- [ ] Screen reader announces validation errors
- [ ] All inputs have ARIA labels
- [ ] Color contrast meets WCAG AA standards
- [ ] Touch targets meet 48x48px minimum

### Browser Compatibility
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (macOS/iOS)
- [ ] Mobile browsers (responsive design)

---

## Troubleshooting

### Common Issues

**Issue:** Modal doesn't open
**Solution:** Check HTMX is loaded, verify URL configuration

**Issue:** Validation always fails
**Solution:** Check tolerance values (0.01 for both weight % and amount ₱)

**Issue:** Currency formatting shows NaN
**Solution:** Ensure work_items_json includes numeric values, not strings

**Issue:** Submit button doesn't work
**Solution:** Check CSRF token is present in page, verify API endpoint

**Issue:** No toast notification
**Solution:** Implement `show-toast` event listener in parent page

---

## Example Implementation

Complete example with view, template, and URL configuration:

### 1. View (`src/monitoring/views.py`)

```python
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
import json

def ppa_detail(request, entry_id):
    entry = get_object_or_404(MonitoringEntry, id=entry_id)

    # Get work items
    work_items = WorkItem.objects.filter(ppa_entry=entry)

    # Prepare JSON data
    work_items_data = [{
        'id': item.id,
        'title': item.title,
        'work_type': item.work_type,
        'work_type_display': item.get_work_type_display(),
        'current_budget': float(item.allocated_budget or 0)
    } for item in work_items]

    context = {
        'entry': entry,
        'work_items': work_items,
        'work_items_json': mark_safe(json.dumps(work_items_data))
    }

    return render(request, 'monitoring/ppa_detail.html', context)
```

### 2. Template (`src/templates/monitoring/ppa_detail.html`)

```django
{% extends 'base.html' %}
{% load humanize %}

{% block content %}
<div class="container mx-auto px-4 py-6">
    <!-- PPA Details -->
    <div class="bg-white rounded-xl border shadow-sm p-6 mb-6">
        <h1 class="text-2xl font-bold text-gray-900">{{ entry.title }}</h1>
        <p class="text-gray-600 mt-2">Total Budget: ₱{{ entry.allocated_budget|floatformat:2|intcomma }}</p>

        <!-- Distribute Budget Button -->
        <button
            type="button"
            @click="showModal = true"
            class="mt-4 px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg hover:shadow-lg transition-all"
        >
            <i class="fas fa-coins mr-2"></i>
            Distribute Budget
        </button>
    </div>

    <!-- Work Items Table -->
    <div class="bg-white rounded-xl border shadow-sm overflow-hidden">
        <table class="min-w-full">
            <thead class="bg-gradient-to-r from-blue-600 to-teal-500">
                <tr>
                    <th class="px-4 py-3 text-left text-white">Work Item</th>
                    <th class="px-4 py-3 text-left text-white">Type</th>
                    <th class="px-4 py-3 text-right text-white">Allocated Budget</th>
                </tr>
            </thead>
            <tbody id="work-items-table">
                {% for item in work_items %}
                <tr class="border-t hover:bg-gray-50">
                    <td class="px-4 py-3">{{ item.title }}</td>
                    <td class="px-4 py-3">
                        <span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                            {{ item.get_work_type_display }}
                        </span>
                    </td>
                    <td class="px-4 py-3 text-right">
                        ₱{{ item.allocated_budget|floatformat:2|intcomma }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Modal Container -->
<div x-data="{ showModal: false }" x-show="showModal" @close-modal.window="showModal = false">
    {% include 'monitoring/partials/budget_distribution_modal.html' %}
</div>
{% endblock %}
```

### 3. URL Configuration (`src/monitoring/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('entries/<int:entry_id>/', views.ppa_detail, name='ppa_detail'),
    path('entries/<int:entry_id>/distribute-budget/', views.distribute_budget, name='distribute_budget'),
]
```

---

## File Locations

- **Template:** `/src/templates/monitoring/partials/budget_distribution_modal.html`
- **JavaScript:** `/src/static/monitoring/js/budget-distributor.js` (standalone reference)
- **Documentation:** `/docs/improvements/BUDGET_DISTRIBUTION_MODAL_GUIDE.md`

---

## Dependencies

- **Alpine.js** (v3.x) - Reactive state management
- **Tailwind CSS** (v3.x) - Styling
- **FontAwesome** (v6.x) - Icons
- **HTMX** (v1.9.x) - Optional for modal loading

---

## Performance Considerations

- **Calculation complexity:** O(n) where n = number of work items
- **Real-time updates:** Debouncing not needed (calculations are instant)
- **Memory footprint:** Minimal (Alpine.js reactive data only)
- **Network requests:** Single POST on submit

---

## Future Enhancements

1. **Smart distribution** - AI-suggested weights based on task priority
2. **Bulk templates** - Save and reuse distribution patterns
3. **History tracking** - Audit log of budget changes
4. **Approval workflow** - Multi-step approval for large budgets
5. **Visualization** - Pie chart preview of distribution

---

## Support

For issues or questions, contact the development team or refer to:
- **OBCMS UI Components Guide:** `/docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`
- **Alpine.js Documentation:** https://alpinejs.dev
- **HTMX Documentation:** https://htmx.org

---

**End of Guide**
