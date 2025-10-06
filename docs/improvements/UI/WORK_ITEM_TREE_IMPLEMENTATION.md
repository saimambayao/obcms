# Work Item Tree Implementation Guide

## Overview

This document provides implementation guidance for the recursive Work Item Tree component with HTMX lazy loading, localStorage state persistence, and full accessibility support.

## Component Features

### Core Features
- **Recursive Tree Structure**: Hierarchical display of Projects → Sub-Projects → Activities → Tasks → Subtasks
- **HTMX Lazy Loading**: Children loaded on-demand to optimize initial page load
- **localStorage Persistence**: Expanded/collapsed state persists across page reloads
- **Visual Tree Connectors**: CSS-based lines showing parent-child relationships
- **Budget Tracking**: Real-time budget allocation, expenditure, and variance display
- **Progress Tracking**: Visual progress bars with color-coded status indicators
- **Accessibility**: Full ARIA support, keyboard navigation (Arrow keys, Space, Enter, Home, End)
- **Responsive Design**: Mobile, tablet, and desktop layouts with print-friendly styles

### Accessibility Features
- **ARIA Tree Roles**: `role="tree"`, `role="treeitem"`, `role="group"`
- **ARIA Expanded State**: `aria-expanded` tracked per node
- **Keyboard Navigation**:
  - `ArrowRight`: Expand node or move to first child
  - `ArrowLeft`: Collapse node or move to parent
  - `ArrowDown`: Move to next visible node
  - `ArrowUp`: Move to previous visible node
  - `Space/Enter`: Toggle expand/collapse
  - `Home`: Jump to first root node
  - `End`: Jump to last visible node
- **Screen Reader Announcements**: Dynamic state changes announced
- **Focus Management**: Proper focus indicators and visual feedback

## File Structure

```
src/
├── templates/
│   └── monitoring/
│       └── partials/
│           └── work_item_tree.html          # Recursive tree node template
├── static/
│   └── monitoring/
│       ├── css/
│       │   └── work_item_tree.css           # Tree connector styles, animations
│       └── js/
│           └── work_item_tree.js            # State management, keyboard navigation
└── monitoring/
    ├── urls.py                              # URL configuration for HTMX endpoints
    └── views.py                             # Django views for tree data
```

## Backend Implementation

### 1. URL Configuration

Add to `src/monitoring/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # ... existing patterns ...

    # Work Item Tree HTMX Endpoints
    path(
        'work-items/<uuid:work_item_id>/children/',
        views.work_item_children_fragment,
        name='work_item_children'
    ),

    # Optional: Full tree view
    path(
        'work-items/tree/<uuid:root_id>/',
        views.work_item_tree_view,
        name='work_item_tree'
    ),
]
```

### 2. View Implementation

Add to `src/monitoring/views.py`:

```python
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from common.work_item_model import WorkItem

def work_item_children_fragment(request, work_item_id):
    """
    HTMX endpoint: Return children of a work item as HTML fragment.

    This view is called when a user expands a tree node. It returns
    only the immediate children as HTML, which HTMX swaps into the
    children container.
    """
    parent = get_object_or_404(WorkItem, id=work_item_id)
    children = parent.get_children()  # MPTT method for immediate children

    # Calculate depth for proper indentation
    parent_depth = parent.level  # MPTT provides level attribute
    child_depth = parent_depth + 1

    # Render children recursively
    html_fragments = []
    for child in children:
        fragment_html = render_to_string(
            'monitoring/partials/work_item_tree.html',
            {
                'work_item': child,
                'depth': child_depth,
            },
            request=request
        )
        html_fragments.append(fragment_html)

    return HttpResponse(''.join(html_fragments))


def work_item_tree_view(request, root_id):
    """
    Full page view: Display entire work item tree starting from root.

    This view renders the complete tree page with the root work item
    and placeholder children containers (lazy loaded via HTMX).
    """
    root_item = get_object_or_404(
        WorkItem.objects.select_related(
            'related_ppa',
            'related_assessment',
            'related_policy',
            'created_by'
        ).prefetch_related(
            'assignees',
            'teams'
        ),
        id=root_id
    )

    context = {
        'root_item': root_item,
        'page_title': f'Work Item Tree: {root_item.title}',
    }

    return render(request, 'monitoring/work_item_tree_page.html', context)
```

### 3. Full Page Template

Create `src/templates/monitoring/work_item_tree_page.html`:

```django
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'monitoring/css/work_item_tree.css' %}">
{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-6">
    <!-- Page Header -->
    <div class="mb-6">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-gray-900">{{ page_title }}</h1>
                <p class="text-gray-600 mt-1">Hierarchical view of all work items</p>
            </div>
            <div class="flex items-center gap-2">
                <button type="button"
                        onclick="WorkItemTree.expandAll()"
                        class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors">
                    <i class="fas fa-expand-arrows-alt mr-2"></i>Expand All
                </button>
                <button type="button"
                        onclick="WorkItemTree.collapseAll()"
                        class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                    <i class="fas fa-compress-arrows-alt mr-2"></i>Collapse All
                </button>
                <button type="button"
                        onclick="WorkItemTree.clearState()"
                        class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                    <i class="fas fa-eraser mr-2"></i>Reset State
                </button>
            </div>
        </div>
    </div>

    <!-- Work Item Tree -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div class="tree-container" role="tree" aria-label="Work item hierarchy">
            {% include "monitoring/partials/work_item_tree.html" with work_item=root_item depth=0 %}
        </div>
    </div>
</div>

<!-- Work Item Modal (for viewing/editing) -->
<div id="workItemModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <!-- Modal content loaded via HTMX -->
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'monitoring/js/work_item_tree.js' %}"></script>
{% endblock %}
```

## View Context Structure

### Expected Context Variables

When including the tree template, provide these context variables:

```python
context = {
    'work_item': WorkItem instance,  # REQUIRED: Current node
    'depth': int,                     # REQUIRED: Current depth level (0-indexed)
}
```

### WorkItem Model Properties Used

The template expects these properties on the `WorkItem` model:

```python
work_item.id                    # UUID
work_item.title                 # str
work_item.description           # str (optional)
work_item.work_type             # str (project, sub_project, activity, etc.)
work_item.status                # str (not_started, in_progress, completed, etc.)
work_item.priority              # str (low, medium, high, urgent, critical)
work_item.progress              # int (0-100)
work_item.allocated_budget      # Decimal (optional)
work_item.actual_expenditure    # Decimal (optional)
work_item.start_date            # date (optional)
work_item.due_date              # date (optional)
work_item.is_overdue            # bool property
work_item.get_children()        # MPTT method: Returns immediate children
work_item.get_work_type_display()    # Django choice field display
work_item.get_status_display()       # Django choice field display
work_item.get_priority_display()     # Django choice field display
```

## Budget Variance Calculation

The template uses Django template tags for budget variance calculation:

```django
{# Example budget variance logic #}
{% if work_item.allocated_budget and work_item.actual_expenditure %}
    {% widthratio work_item.actual_expenditure 1 100 as actual_cents %}
    {% widthratio work_item.allocated_budget 1 100 as allocated_cents %}
    {% widthratio actual_cents allocated_cents 100 as variance_pct %}

    {% if actual_cents > allocated_cents %}
        <!-- Over Budget (Red) -->
    {% elif variance_pct >= 95 %}
        <!-- Near Limit (Amber) -->
    {% else %}
        <!-- Within Budget (Emerald) -->
    {% endif %}
{% endif %}
```

## Custom Template Tags (Optional Enhancement)

For cleaner variance calculations, consider creating custom template tags:

Create `src/monitoring/templatetags/work_item_tags.py`:

```python
from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def budget_variance(work_item):
    """Calculate budget variance percentage."""
    if not work_item.allocated_budget or not work_item.actual_expenditure:
        return None

    variance = work_item.actual_expenditure - work_item.allocated_budget
    return (variance / work_item.allocated_budget) * 100

@register.filter
def budget_variance_class(work_item):
    """Return CSS class based on budget variance."""
    variance_pct = budget_variance(work_item)
    if variance_pct is None:
        return 'text-gray-400'

    if variance_pct > 0:
        return 'text-red-600'  # Over budget
    elif variance_pct >= -5:
        return 'text-amber-600'  # Near limit (within 5%)
    else:
        return 'text-emerald-600'  # Within budget
```

Usage in template:

```django
{% load work_item_tags %}

<p class="{{ work_item|budget_variance_class }}">
    Variance: {{ work_item|budget_variance|floatformat:1 }}%
</p>
```

## Testing the Component

### Manual Testing Checklist

- [ ] **Initial Load**: Tree renders with root node visible
- [ ] **Expand Node**: Click chevron icon, children load via HTMX
- [ ] **Collapse Node**: Click chevron icon again, children collapse smoothly
- [ ] **State Persistence**: Refresh page, expanded nodes remain expanded
- [ ] **Keyboard Navigation**: Arrow keys navigate tree, Space/Enter toggle nodes
- [ ] **ARIA Attributes**: Screen reader announces expanded/collapsed states
- [ ] **Budget Variance**: Colors change based on over/under budget
- [ ] **Progress Bar**: Visual indicator updates based on progress percentage
- [ ] **Mobile Responsive**: Tree displays correctly on mobile (no indent)
- [ ] **Hover Actions**: Edit/View/Delete buttons appear on hover
- [ ] **Loading Indicator**: Spinner shows during HTMX request
- [ ] **Error Handling**: Failed HTMX requests show error message

### JavaScript Console Testing

```javascript
// Check expanded state
WorkItemTree.getExpandedState()

// Expand all nodes
WorkItemTree.expandAll()

// Collapse all nodes
WorkItemTree.collapseAll()

// Clear persisted state
WorkItemTree.clearState()
```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Only load children when expanded (implemented via HTMX)
2. **Query Optimization**: Use `select_related()` and `prefetch_related()` in views
3. **Pagination**: For very large trees, consider paginating children (100+ items)
4. **Caching**: Cache expensive budget calculations at model level
5. **Database Indexing**: Ensure MPTT fields (`lft`, `rght`, `tree_id`, `level`) are indexed

### Expected Performance

- **Initial Load**: <200ms for single root node
- **HTMX Child Load**: <100ms for 10-20 children
- **Expand Animation**: 300ms smooth transition
- **State Save**: <5ms localStorage write

## Accessibility Testing

### Screen Reader Testing (NVDA/JAWS)

1. Navigate to tree with keyboard
2. Verify "tree" role announced
3. Expand node with Enter key
4. Verify "expanded" state announced
5. Navigate children with Arrow Down
6. Verify child count announced
7. Collapse with Enter key
8. Verify "collapsed" state announced

### Keyboard-Only Testing

1. Tab to tree
2. Arrow Right to expand
3. Arrow Down to next node
4. Arrow Left to collapse
5. Home key to jump to first node
6. End key to jump to last node
7. Verify focus indicators visible

## Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Full support (localStorage, HTMX, CSS Grid)
- **Mobile Safari/Chrome**: Full support (responsive layout)
- **IE11**: Not supported (uses modern CSS features)

## Troubleshooting

### Children Not Loading

**Symptom**: Clicking expand button doesn't load children

**Solutions**:
1. Check browser console for HTMX errors
2. Verify URL pattern `monitoring:work_item_children` exists
3. Check Django view returns valid HTML
4. Ensure work item has `get_children()` method (MPTT)

### State Not Persisting

**Symptom**: Expanded nodes collapse after page reload

**Solutions**:
1. Check localStorage is enabled in browser
2. Verify `work_item.id` is unique UUID
3. Check browser console for JS errors in `work_item_tree.js`
4. Clear localStorage and test: `WorkItemTree.clearState()`

### Tree Connectors Not Showing

**Symptom**: No visual lines connecting nodes

**Solutions**:
1. Verify `work_item_tree.css` is loaded
2. Check `depth` variable is passed correctly
3. Inspect element to verify `.tree-connectors` div exists
4. Check CSS for `.tree-line` and `.tree-branch` classes

### Budget Variance Incorrect

**Symptom**: Wrong colors or percentages displayed

**Solutions**:
1. Verify `allocated_budget` and `actual_expenditure` are Decimal types
2. Check Django template math with `{% widthratio %}` tag
3. Ensure currency values are positive
4. Test variance calculation in Django shell

## Future Enhancements

### Planned Features

1. **Drag and Drop**: Reorder nodes via drag and drop (requires SortableJS)
2. **Bulk Operations**: Select multiple nodes for bulk actions
3. **Filtering**: Filter tree by work type, status, priority
4. **Search**: Live search within tree hierarchy
5. **Export**: Export tree structure to PDF/Excel
6. **Real-time Updates**: WebSocket integration for live collaboration
7. **Virtualization**: Render only visible nodes for very large trees (>1000 nodes)
8. **Gantt View**: Alternate timeline view of work items

### Optional Integrations

- **Chart.js**: Budget distribution pie chart
- **FullCalendar**: Timeline view of work items
- **Leaflet**: Geographic distribution of work items (for location-based projects)

## Related Documentation

- [WorkItem Model Documentation](/docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md)
- [HTMX Integration Guide](/docs/development/htmx_patterns.md)
- [Accessibility Standards](/docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md)
- [MonitoringEntry Integration](/docs/improvements/WORKITEM_MIGRATION_COMPLETE.md)

## Support

For questions or issues:
- Check Django logs: `src/logs/debug.log`
- Review HTMX requests in browser Network tab
- Test with `DEBUG=True` for detailed error messages
- Consult HTMX documentation: https://htmx.org/docs/

---

**Last Updated**: 2025-10-06
**Component Version**: 1.0.0
**Status**: Production-Ready
