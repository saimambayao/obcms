# WorkItem Tree Component - Quick Reference

## At a Glance

**Component**: Recursive Tree View for Hierarchical WorkItems
**Tech Stack**: Django Templates + HTMX + Tailwind CSS + Vanilla JS
**Accessibility**: WCAG 2.1 AA Compliant
**Performance**: Lazy loading, localStorage state persistence

---

## File Locations

```
Templates:  src/templates/monitoring/partials/work_item_tree.html
CSS:        src/static/monitoring/css/work_item_tree.css
JavaScript: src/static/monitoring/js/work_item_tree.js
Docs:       docs/improvements/UI/WORK_ITEM_TREE_IMPLEMENTATION.md
```

---

## Usage

### Basic Template Include

```django
{% include "monitoring/partials/work_item_tree.html" with work_item=root_item depth=0 %}
```

### Required Context

```python
context = {
    'work_item': WorkItem.objects.get(id=root_id),  # Root node
    'depth': 0,                                      # Starting depth
}
```

### Full Page Template

```django
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'monitoring/css/work_item_tree.css' %}">
{% endblock %}

{% block content %}
<div class="tree-container" role="tree">
    {% include "monitoring/partials/work_item_tree.html" with work_item=root_item depth=0 %}
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'monitoring/js/work_item_tree.js' %}"></script>
{% endblock %}
```

---

## HTMX Endpoint

### URL Pattern

```python
# src/monitoring/urls.py
path('work-items/<uuid:work_item_id>/children/', views.work_item_children_fragment, name='work_item_children'),
```

### View Function

```python
# src/monitoring/views.py
def work_item_children_fragment(request, work_item_id):
    parent = get_object_or_404(WorkItem, id=work_item_id)
    children = parent.get_children()
    child_depth = parent.level + 1

    html_fragments = []
    for child in children:
        fragment_html = render_to_string(
            'monitoring/partials/work_item_tree.html',
            {'work_item': child, 'depth': child_depth},
            request=request
        )
        html_fragments.append(fragment_html)

    return HttpResponse(''.join(html_fragments))
```

---

## Features Summary

### Visual Elements

| Feature | Description |
|---------|-------------|
| **Tree Connectors** | CSS-based lines showing parent-child relationships |
| **Work Type Badges** | Color-coded: Blue (project), Emerald (activity), Purple (task), Amber (subtask) |
| **Status Badges** | Emerald (completed), Blue (in progress), Orange (at risk), Red (blocked) |
| **Priority Badges** | Only shown for High/Urgent/Critical priorities |
| **Budget Cards** | 3-column grid: Allocated, Expenditure, Variance |
| **Progress Bar** | Animated, color-coded by status |
| **Timeline** | Start date and due date with overdue indicator |

### Interactive Features

| Feature | Trigger | Behavior |
|---------|---------|----------|
| **Expand Node** | Click chevron | HTMX loads children, animates open (300ms) |
| **Collapse Node** | Click chevron | Animates closed (300ms), hides children |
| **View Details** | Click eye icon | Opens modal via HTMX |
| **Edit Item** | Click edit icon | Opens edit form via HTMX |
| **Delete Item** | Click trash icon | Confirms, then deletes via HTMX |
| **State Persistence** | Auto | Saves expanded/collapsed state to localStorage |

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `Tab` | Focus next interactive element |
| `Shift+Tab` | Focus previous interactive element |
| `ArrowRight` | Expand node OR move to first child |
| `ArrowLeft` | Collapse node OR move to parent |
| `ArrowDown` | Move to next visible node |
| `ArrowUp` | Move to previous visible node |
| `Space` / `Enter` | Toggle expand/collapse |
| `Home` | Jump to first root node |
| `End` | Jump to last visible node |

---

## Budget Variance Indicators

### Color Coding

- **Red (Over Budget)**: `actual > allocated`
  - Shows: `+₱X,XXX (XX% over)`
  - Icon: ↑ arrow

- **Amber (Near Limit)**: `95% ≤ variance < 100%`
  - Shows: `₱X,XXX remaining (XX%)`
  - Icon: ⚠ warning

- **Emerald (Within Budget)**: `variance < 95%`
  - Shows: `₱X,XXX remaining (XX%)`
  - Icon: ✓ checkmark

- **Gray (No Data)**: `allocated OR expenditure is null`
  - Shows: `—`

---

## JavaScript API

### Public Methods

```javascript
// Get current expanded state
WorkItemTree.getExpandedState()
// Returns: { "uuid-1": true, "uuid-2": true, ... }

// Save expanded state for a node
WorkItemTree.saveExpandedState("uuid", true)

// Clear all persisted state
WorkItemTree.clearState()

// Expand all nodes in tree
WorkItemTree.expandAll()

// Collapse all nodes in tree
WorkItemTree.collapseAll()
```

### Example Usage

```javascript
// Expand all nodes on page load
document.addEventListener('DOMContentLoaded', function() {
    WorkItemTree.expandAll();
});

// Reset state on button click
document.getElementById('resetBtn').addEventListener('click', function() {
    WorkItemTree.clearState();
    location.reload();
});
```

---

## Accessibility Features

### ARIA Attributes

```html
<!-- Tree Container -->
<div role="tree" aria-label="Work item hierarchy">
    <!-- Tree Node -->
    <div role="treeitem" aria-level="1" aria-expanded="false" tabindex="0">
        <!-- Expand Button -->
        <button aria-label="Expand to show 3 sub-items" aria-controls="children-uuid">
            <i class="fas fa-chevron-right"></i>
        </button>

        <!-- Children Container -->
        <div id="children-uuid" role="group" aria-label="Sub-items of Project A">
            <!-- Child nodes... -->
        </div>
    </div>
</div>
```

### Screen Reader Announcements

```javascript
// On expand
"Expanded: Loaded 3 sub-items"

// On collapse
"Collapsed sub-items"

// On keyboard navigation
"Project A, expanded, level 1"
```

---

## Responsive Breakpoints

| Breakpoint | Width | Changes |
|------------|-------|---------|
| **Mobile** | <640px | No tree connectors, budget cards stack, smaller icons |
| **Tablet** | 641px-1024px | Reduced indentation (12px vs 24px) |
| **Desktop** | >1024px | Full indentation, 3-column budget grid |

---

## Common Customizations

### Change Indent Spacing

```css
/* src/static/monitoring/css/work_item_tree.css */
.node-card {
    margin-left: calc(var(--depth, 0) * 32px); /* Default: 24px */
}
```

### Change Animation Duration

```css
.children-container {
    transition: max-height 0.5s ease-out; /* Default: 0.3s */
}
```

### Change Budget Threshold

```django
<!-- src/templates/monitoring/partials/work_item_tree.html -->
{% elif variance_pct >= 90 %}  <!-- Default: 95 -->
    <!-- Near Limit (Amber) -->
{% endif %}
```

### Disable State Persistence

```javascript
// src/static/monitoring/js/work_item_tree.js
function saveExpandedState(workItemId, isExpanded) {
    // Comment out localStorage.setItem() to disable
    // localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}
```

---

## Troubleshooting

### Issue: Children not loading

**Check**:
1. Browser console for errors
2. URL pattern `monitoring:work_item_children` exists
3. View returns valid HTML
4. HTMX loaded before `work_item_tree.js`

**Fix**:
```python
# Verify URL in Django shell
from django.urls import reverse
reverse('monitoring:work_item_children', args=['uuid-here'])
```

### Issue: State not persisting

**Check**:
1. localStorage enabled in browser
2. No JavaScript errors in console
3. `work_item.id` is valid UUID

**Fix**:
```javascript
// Test in browser console
WorkItemTree.getExpandedState()
// Should return object, not error
```

### Issue: Tree connectors misaligned

**Check**:
1. CSS file loaded
2. `depth` variable passed correctly
3. Template `{% for i in "x"|rjust:depth %}` works

**Fix**:
```html
<!-- Debug depth in template -->
<div data-depth="{{ depth }}">Depth: {{ depth }}</div>
```

---

## Performance Tips

### Optimize Large Trees

```python
# Use select_related/prefetch_related
WorkItem.objects.select_related(
    'related_ppa',
    'created_by'
).prefetch_related(
    'assignees',
    'teams'
)
```

### Limit Children Per Request

```python
# Paginate children if >20
children = parent.get_children()[:20]
```

### Cache Budget Calculations

```python
# Add cached property to WorkItem model
@cached_property
def budget_variance_pct(self):
    if not self.allocated_budget or not self.actual_expenditure:
        return None
    return ((self.actual_expenditure - self.allocated_budget) / self.allocated_budget) * 100
```

---

## Testing Checklist

Quick verification before deployment:

- [ ] Tree renders with root node
- [ ] Expand loads children via HTMX
- [ ] Collapse hides children
- [ ] State persists after refresh
- [ ] Keyboard navigation works (Arrow keys)
- [ ] Screen reader announces states
- [ ] Budget variance colors correct
- [ ] Mobile responsive (no horizontal scroll)
- [ ] Hover shows action buttons
- [ ] No JavaScript errors in console

---

## Related Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Work Item Modal** | `common/partials/work_item_modal.html` | View/Edit details |
| **Work Item Form** | `work_items/work_item_form.html` | Create/Edit form |
| **Budget Distribution** | Service layer | Auto-distribute budgets |
| **Progress Calculation** | WorkItem model | Auto-calculate from children |

---

## Support Resources

- **Full Documentation**: [WORK_ITEM_TREE_IMPLEMENTATION.md](WORK_ITEM_TREE_IMPLEMENTATION.md)
- **DoD Checklist**: [WORK_ITEM_TREE_DOD_CHECKLIST.md](WORK_ITEM_TREE_DOD_CHECKLIST.md)
- **WorkItem Model**: [UNIFIED_WORK_HIERARCHY_EVALUATION.md](/docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md)
- **HTMX Docs**: https://htmx.org/docs/
- **ARIA Tree Pattern**: https://www.w3.org/WAI/ARIA/apg/patterns/treeview/

---

**Last Updated**: 2025-10-06
**Version**: 1.0.0
**Status**: Production-Ready
