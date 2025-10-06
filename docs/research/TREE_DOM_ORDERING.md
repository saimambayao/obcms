# Tree DOM Ordering: Best Practices for HTML Tables

**Status:** Complete
**Created:** 2025-10-06
**Author:** Research Report
**Related Issue:** Children appearing ABOVE parent in tree table expansion

---

## Executive Summary

When implementing hierarchical tree structures in HTML tables (especially with MPTT models), **DOM insertion order is critical**. Children must be inserted **immediately after their parent row** (using `afterend`) to maintain proper visual hierarchy. The current bug occurs because children are being inserted in the wrong position, causing them to appear above the parent instead of below.

---

## Problem Statement

In the OBCMS Work Items tree view (`/monitoring/partials/work_item_tree.html`), when a user clicks the expand button:

- **Expected:** Children appear BELOW the parent in the DOM
- **Actual:** Children appear ABOVE the parent (wrong insertion order)

**Root Cause:** HTMX swap strategy and target element positioning

---

## Understanding MPTT Tree Traversal

### What is MPTT?

**Modified Preorder Tree Traversal (MPTT)** is a technique for storing hierarchical data in a database.

```
Example Tree Structure:
┌─────────────────────────────────────────┐
│ Project A (lft:1, rght:14)              │
├────────────────────────────────────────┐│
│ ├─ Activity A1 (lft:2, rght:7)        ││
│ │  ├─ Task A1.1 (lft:3, rght:4)       ││
│ │  └─ Task A1.2 (lft:5, rght:6)       ││
│ └─ Activity A2 (lft:8, rght:13)       ││
│    ├─ Task A2.1 (lft:9, rght:10)      ││
│    └─ Task A2.2 (lft:11, rght:12)     ││
└────────────────────────────────────────┘│
                                          │
```

### MPTT Display Order

MPTT uses **pre-order traversal** for display:

```python
# Django QuerySet ordering for MPTT tree display
WorkItem.objects.order_by('tree_id', 'lft')
```

This produces:

```
1. Project A (lft:1)
2.   Activity A1 (lft:2)
3.     Task A1.1 (lft:3)
4.     Task A1.2 (lft:5)
5.   Activity A2 (lft:8)
6.     Task A2.1 (lft:9)
7.     Task A2.2 (lft:11)
```

**Key Insight:** In MPTT pre-order traversal, **children always appear AFTER their parent** in the ordered sequence.

---

## DOM Ordering for Tree Tables

### Correct DOM Structure

For a tree table to display correctly, the **DOM order MUST match the visual tree order**:

```html
<div class="tree">
  <!-- Parent Row (Position N) -->
  <div class="tree-node" id="node-parent">
    <div class="node-card">Parent Item</div>
  </div>

  <!-- Children Container (Position N+1) -->
  <div class="children-container" id="children-parent">
    <!-- Child 1 (Position N+2) -->
    <div class="tree-node" id="node-child1">
      <div class="node-card">Child 1</div>
    </div>

    <!-- Child 2 (Position N+3) -->
    <div class="tree-node" id="node-child2">
      <div class="node-card">Child 2</div>
    </div>
  </div>
</div>
```

### Visual Diagram: Correct vs. Incorrect

```
✅ CORRECT ORDER (Children after parent):
┌────────────────────────────────┐
│ [0] Root Node                  │ ← Parent at position 0
├────────────────────────────────┤
│   [1] Child 1                  │ ← First child at position 1
├────────────────────────────────┤
│   [2] Child 2                  │ ← Second child at position 2
├────────────────────────────────┤
│ [3] Another Root               │ ← Next sibling at position 3
└────────────────────────────────┘

❌ INCORRECT ORDER (Children before parent):
┌────────────────────────────────┐
│   [0] Child 1                  │ ← Child at position 0 (WRONG!)
├────────────────────────────────┤
│   [1] Child 2                  │ ← Child at position 1 (WRONG!)
├────────────────────────────────┤
│ [2] Root Node                  │ ← Parent at position 2 (WRONG!)
├────────────────────────────────┤
│ [3] Another Root               │
└────────────────────────────────┘
```

---

## HTMX Swap Strategies

### Available HTMX Swap Options

HTMX provides 4 main swap options based on `Element.insertAdjacentHTML`:

```javascript
// Standard DOM insertion positions
element.insertAdjacentHTML(position, html)

// Positions:
'beforebegin' → hx-swap="beforebegin"  // Before the target element
'afterbegin'  → hx-swap="afterbegin"   // First child of target
'beforeend'   → hx-swap="beforeend"    // Last child of target (default)
'afterend'    → hx-swap="afterend"     // After the target element
```

### Visual Representation

```html
<!-- beforebegin -->
<div id="target">
  <!-- afterbegin -->
  Existing content
  <!-- beforeend -->
</div>
<!-- afterend -->
```

### For Tree Expansion: Use `afterend`

**Correct Strategy for Tree Nodes:**

```html
<!-- Parent Node -->
<div class="tree-node" id="node-123">
  <div class="node-card">Parent Item</div>

  <!-- Expand Button with HTMX -->
  <button hx-get="/api/work_item_children/123"
          hx-target="#node-123"
          hx-swap="afterend">
    Expand
  </button>
</div>

<!-- Children will be inserted AFTER #node-123 -->
```

**Result After Expansion:**

```html
<!-- Parent Node (Position N) -->
<div class="tree-node" id="node-123">...</div>

<!-- Children (Position N+1, N+2, ...) -->
<div class="tree-node" id="node-456">Child 1</div>
<div class="tree-node" id="node-789">Child 2</div>
```

---

## Common Tree Table Patterns

### Pattern 1: Container-Based (Current OBCMS Approach)

**Structure:**

```html
<!-- Parent Node -->
<div class="tree-node">
  <div class="node-card">Parent</div>
</div>

<!-- Separate Children Container -->
<div class="children-container hidden" id="children-parent">
  <!-- Children loaded here -->
</div>
```

**HTMX Configuration:**

```html
<button hx-get="/children/parent"
        hx-target="#children-parent"
        hx-swap="innerHTML">  <!-- Load INTO container -->
  Expand
</button>
```

**Pros:**
- Clean separation of parent and children
- Easy to show/hide children with CSS (`hidden` class)
- Container provides grouping for ARIA roles

**Cons:**
- Requires placeholder container in initial render
- Container adds extra DOM element

### Pattern 2: Inline Insertion (No Container)

**Structure:**

```html
<!-- Parent Node -->
<div class="tree-node" id="node-parent">
  <div class="node-card">Parent</div>
</div>

<!-- No placeholder - children inserted directly after parent -->
```

**HTMX Configuration:**

```html
<button hx-get="/children/parent"
        hx-target="#node-parent"
        hx-swap="afterend">  <!-- Insert AFTER parent -->
  Expand
</button>
```

**Pros:**
- No extra container element
- Simpler DOM structure
- Direct sibling insertion

**Cons:**
- Harder to track which nodes are children
- Collapsing requires removing multiple siblings
- Need data attributes to identify children

---

## Solution for OBCMS Work Items Tree

### Current Bug Analysis

**File:** `/src/templates/monitoring/partials/work_item_tree.html`

**Current Implementation (Lines 63-72):**

```html
<button type="button"
        class="expand-toggle"
        data-work-item-id="{{ work_item.id }}"
        hx-get="{% url 'monitoring:work_item_children' work_item.id %}"
        hx-target="#children-{{ work_item.id }}"
        hx-swap="innerHTML"
        hx-trigger="click once"
        onclick="toggleWorkItemNode(this, '{{ work_item.id }}')">
```

**Children Container (Lines 356-363):**

```html
<div class="children-container hidden"
     id="children-{{ work_item.id }}"
     role="group">
  <!-- Children will be loaded via HTMX when expanded -->
</div>
```

**Problem:** The children container is placed AFTER the parent node card, but the template structure might be causing incorrect DOM ordering.

### Recommended Fix

**Option A: Verify Container Position** (Preferred - Less Disruptive)

Ensure the children container is positioned correctly in the DOM:

```html
<!-- Parent Node Container -->
<div class="tree-node relative" id="node-{{ work_item.id }}">

  <!-- Node Card -->
  <div class="node-card">
    <!-- Parent content here -->
  </div>

  <!-- Children Container (MUST be sibling, not nested) -->
  <div class="children-container hidden"
       id="children-{{ work_item.id }}"
       role="group"
       aria-label="Sub-items of {{ work_item.title }}">
    <!-- Children loaded here via HTMX -->
  </div>

</div>
```

**Key Points:**
1. Children container is a **sibling** of node-card (not nested inside)
2. Container is part of the same `tree-node` wrapper
3. HTMX swaps `innerHTML` of the container
4. JavaScript toggles `hidden` class on the container

**Option B: Switch to Direct Insertion** (Alternative)

Change to inline insertion without container:

```html
<!-- HTMX Button -->
<button hx-get="{% url 'monitoring:work_item_children' work_item.id %}"
        hx-target="#node-{{ work_item.id }}"
        hx-swap="afterend"
        onclick="toggleExpansion(this, '{{ work_item.id }}')">
```

**JavaScript for Collapse:**

```javascript
function toggleExpansion(button, nodeId) {
  const nodeElement = document.getElementById(`node-${nodeId}`);
  const isExpanded = button.getAttribute('aria-expanded') === 'true';

  if (isExpanded) {
    // Collapse: Remove all following sibling nodes with data-parent-id
    let nextSibling = nodeElement.nextElementSibling;
    while (nextSibling && nextSibling.dataset.parentId === nodeId) {
      const toRemove = nextSibling;
      nextSibling = nextSibling.nextElementSibling;
      toRemove.remove();
    }
    button.setAttribute('aria-expanded', 'false');
  } else {
    // Expand: HTMX will insert children after this node
    button.setAttribute('aria-expanded', 'true');
  }
}
```

---

## Best Practices Summary

### ✅ DO

1. **Order children immediately after parent** in DOM
2. **Use MPTT pre-order traversal** for tree display
3. **Match DOM order to visual tree order**
4. **Use `hx-swap="afterend"` for inline insertion**
5. **Use `hx-swap="innerHTML"` with container pattern**
6. **Include ARIA attributes** (`role="treeitem"`, `aria-expanded`)
7. **Persist expansion state** in localStorage
8. **Implement keyboard navigation** (Arrow keys)

### ❌ DON'T

1. **Don't insert children before parent** (causes visual bug)
2. **Don't use `beforebegin` for tree expansion**
3. **Don't nest children inside parent card** (breaks structure)
4. **Don't forget to toggle expand/collapse icons**
5. **Don't load entire tree at once** (performance issue)
6. **Don't skip accessibility attributes**

---

## Implementation Checklist for OBCMS

- [ ] Verify children container is sibling of node-card (not nested)
- [ ] Confirm HTMX target is correct (`#children-{{ work_item.id }}`)
- [ ] Check HTMX swap is `innerHTML` (for container pattern)
- [ ] Test expansion on different tree levels
- [ ] Verify collapse removes correct children
- [ ] Ensure visual connectors align properly
- [ ] Test keyboard navigation
- [ ] Verify ARIA attributes update correctly
- [ ] Check localStorage persistence works
- [ ] Test with deep nesting (5+ levels)

---

## Code Examples

### Example 1: Correct Container Pattern

```html
<!-- Parent Node Wrapper -->
<div class="tree-node" id="node-{{ item.id }}" data-depth="{{ depth }}">

  <!-- Parent Card -->
  <div class="node-card bg-white border rounded-xl p-4">
    <button hx-get="/children/{{ item.id }}"
            hx-target="#children-{{ item.id }}"
            hx-swap="innerHTML"
            onclick="toggleNode('{{ item.id }}')">
      <i class="fas fa-chevron-right" id="icon-{{ item.id }}"></i>
    </button>
    <span>{{ item.title }}</span>
  </div>

  <!-- Children Container (Sibling of card) -->
  <div class="children-container hidden" id="children-{{ item.id }}">
    <!-- HTMX loads children here -->
  </div>

</div>
```

### Example 2: Server Response (Django Template)

```django
{# File: _work_item_tree_nodes.html #}
{% for child in children %}
  {% include "monitoring/partials/work_item_tree.html" with work_item=child depth=parent_level %}
{% endfor %}
```

**Key:** Recursive template renders children with incremented depth.

### Example 3: JavaScript Toggle Function

```javascript
function toggleWorkItemNode(button, workItemId) {
  const icon = document.getElementById(`toggle-icon-${workItemId}`);
  const container = document.getElementById(`children-${workItemId}`);
  const isExpanded = button.getAttribute('aria-expanded') === 'true';

  if (isExpanded) {
    // Collapse
    container.classList.add('hidden');
    icon.style.transform = 'rotate(0deg)';
    button.setAttribute('aria-expanded', 'false');
    localStorage.setItem(`work-item-${workItemId}`, 'collapsed');
  } else {
    // Expand
    container.classList.remove('hidden');
    icon.style.transform = 'rotate(90deg)';
    button.setAttribute('aria-expanded', 'true');
    localStorage.setItem(`work-item-${workItemId}`, 'expanded');
  }
}
```

---

## Performance Considerations

### Lazy Loading with HTMX

**Advantages:**
- Only load visible children (reduces initial page size)
- Cache children responses (5-minute TTL in OBCMS)
- Use `hx-trigger="click once"` to prevent duplicate requests

**Example:**

```python
# views.py
@login_required
def work_item_tree_partial(request, pk):
    from django.core.cache import cache

    cache_key = f"work_item_children:{pk}:{request.user.id}"
    cached_html = cache.get(cache_key)

    if cached_html:
        return HttpResponse(cached_html)

    work_item = get_object_or_404(WorkItem, pk=pk)
    children = work_item.get_children().order_by('lft')  # MPTT ordering

    html = render_to_string('_work_item_tree_nodes.html', {
        'work_items': children,
        'parent_level': work_item.level + 1
    })

    cache.set(cache_key, html, 300)  # 5 minutes
    return HttpResponse(html)
```

### Database Query Optimization

```python
# Optimized query for tree display
children = (
    work_item.get_children()
    .select_related('parent', 'created_by')  # Avoid N+1
    .prefetch_related('assignees', 'teams')
    .only(
        'id', 'work_type', 'title', 'status', 'priority',
        'level', 'tree_id', 'lft', 'rght'  # MPTT fields
    )
    .annotate(children_count=Count('children'))
    .order_by('lft')  # Pre-order traversal
)
```

---

## Accessibility Best Practices

### ARIA Roles for Tree Structure

```html
<div role="tree" aria-label="Work Items Hierarchy">

  <!-- Root Node -->
  <div role="treeitem"
       aria-level="1"
       aria-expanded="false"
       aria-owns="children-123"
       id="node-123"
       tabindex="0">
    <div>Root Item</div>
  </div>

  <!-- Children Group -->
  <div role="group"
       id="children-123"
       aria-label="Sub-items of Root Item"
       class="hidden">

    <!-- Child Node -->
    <div role="treeitem"
         aria-level="2"
         id="node-456"
         tabindex="-1">
      <div>Child Item</div>
    </div>

  </div>

</div>
```

### Keyboard Navigation

```javascript
document.addEventListener('keydown', (e) => {
  const activeNode = document.activeElement.closest('[role="treeitem"]');
  if (!activeNode) return;

  switch (e.key) {
    case 'ArrowRight':
      // Expand node or move to first child
      expandNode(activeNode);
      break;

    case 'ArrowLeft':
      // Collapse node or move to parent
      collapseNode(activeNode);
      break;

    case 'ArrowDown':
      // Move to next visible node
      focusNextNode(activeNode);
      break;

    case 'ArrowUp':
      // Move to previous visible node
      focusPreviousNode(activeNode);
      break;
  }
});
```

---

## References

### Web Search Findings

1. **MDN: DOM Traversal**
   https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Traversing_an_HTML_table_with_JavaScript_and_DOM_Interfaces

2. **HTMX Swap Attribute Documentation**
   https://htmx.org/attributes/hx-swap/

3. **MPTT: Modified Preorder Tree Traversal**
   https://django-mptt.readthedocs.io/en/latest/overview.html

4. **Tabulator Tree Tables**
   https://tabulator.info/docs/6.3/tree

5. **Stack Overflow: Tree Table Implementations**
   https://stackoverflow.com/questions/5636375/how-to-create-a-collapsing-tree-table-in-html-css-js

### OBCMS Internal Documentation

- `/docs/research/MOA_PPA_WORKITEM_INTEGRATION_ARCHITECTURE.md`
- `/docs/improvements/PROJECT_ACTIVITY_TASK_INTEGRATION_COMPLETE.md`
- `/src/common/work_item_model.py` (MPTT implementation)
- `/src/common/views/work_items.py` (Tree view logic)

---

## Conclusion

**Answer to Original Question:**

> When a parent row at position N has children, should the children be inserted:
> - A) Immediately after parent (position N+1)? ✅ **YES**
> - B) After all parent's siblings? ❌ NO
> - C) After parent's placeholder row? ❌ NO (if placeholder is separate)

**Correct Approach:**

- **Container Pattern:** Children load INTO the container (which is at position N+1)
- **Inline Pattern:** Children insert AFTER the parent node (positions N+1, N+2, ...)
- **MPTT Ordering:** Always use `order_by('tree_id', 'lft')` for pre-order traversal

**Fix for OBCMS:**

1. Verify children container is positioned correctly after parent card
2. Ensure container is a sibling of the card (not nested inside)
3. Confirm HTMX swap is `innerHTML` for container pattern
4. Test expansion behavior across all tree levels

---

**Document Version:** 1.0
**Last Updated:** 2025-10-06
**Next Review:** After bug fix implementation
