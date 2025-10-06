# Tree Table Bug: Quick Fix Guide

**Issue:** Children appearing ABOVE parent in Work Items tree expansion
**Severity:** High (breaks visual hierarchy)
**Affected Component:** `/src/templates/monitoring/partials/work_item_tree.html`

---

## Root Cause

The children container is positioned **before** the node card in the DOM, causing children to render above the parent visually.

---

## Quick Fix

### Current Problem (Lines 44-363 in work_item_tree.html)

The template structure might have the children container positioned incorrectly relative to the node card.

### Solution: Verify DOM Order

Ensure this exact structure:

```html
<div class="tree-node" id="node-{{ work_item.id }}">

  <!-- 1. Node card FIRST -->
  <div class="node-card">
    <button hx-target="#children-{{ work_item.id }}"
            hx-swap="innerHTML">
      Expand
    </button>
    Parent content here
  </div>

  <!-- 2. Children container AFTER card -->
  <div class="children-container hidden"
       id="children-{{ work_item.id }}">
    <!-- Children loaded here -->
  </div>

</div>
```

**Critical:** Children container MUST be a **sibling** of node-card, positioned **after** it.

---

## Verification Steps

### 1. Inspect DOM in Browser

```javascript
// Open browser console
const parent = document.getElementById('node-{WORK_ITEM_ID}');
console.log('Structure:', parent.children);

// Expected output:
// 0: div.node-card
// 1: div.children-container
```

### 2. Expand a Node and Check Order

1. Expand "Activity A1"
2. Right-click → Inspect Element
3. Verify DOM order:
   ```
   <div id="node-parent">
     <div class="node-card">Activity A1</div>
     <div class="children-container">
       <div id="node-child1">Task 1</div>
       <div id="node-child2">Task 2</div>
     </div>
   </div>
   ```

### 3. Check Visual Order

After expansion:
```
✅ CORRECT:
  Activity A1 (Parent)
    ↓
    Task 1 (Child)
    ↓
    Task 2 (Child)

❌ INCORRECT:
    Task 1 (Child)
    ↓
    Task 2 (Child)
    ↓
  Activity A1 (Parent) ← Parent below children!
```

---

## Implementation Checklist

- [ ] Open `/src/templates/monitoring/partials/work_item_tree.html`
- [ ] Locate `<div class="tree-node">` wrapper (line ~20)
- [ ] Verify `<div class="node-card">` comes FIRST (line ~44)
- [ ] Verify `<div class="children-container">` comes AFTER (line ~356)
- [ ] Ensure container is NOT nested inside card
- [ ] Test expansion on Work Items tree
- [ ] Verify children appear below parent
- [ ] Test collapse functionality
- [ ] Check multiple tree levels (depth 0, 1, 2, 3)

---

## HTMX Configuration

### Correct Setup

```html
<button hx-get="{% url 'monitoring:work_item_children' work_item.id %}"
        hx-target="#children-{{ work_item.id }}"
        hx-swap="innerHTML"
        hx-trigger="click once">
  <i class="fas fa-chevron-right"></i>
</button>
```

**Key Points:**
- `hx-target`: Points to children container ID
- `hx-swap`: Use `innerHTML` for container pattern
- `hx-trigger`: `click once` prevents duplicate loads

---

## Django View (Already Correct)

The view at `/src/common/views/work_items.py` already has correct MPTT ordering:

```python
children = (
    work_item.get_children()
    .order_by('lft')  # MPTT pre-order traversal
)
```

**No changes needed** in Python code. Issue is template-only.

---

## Testing

### Test Cases

1. **Expand root-level item** → Children should appear below
2. **Expand child item** → Grandchildren should appear below child
3. **Collapse expanded item** → Children should hide
4. **Expand multiple siblings** → Each shows own children
5. **Deep nesting (5 levels)** → All levels render correctly

### Test Script

```javascript
// Paste in browser console to test all nodes
document.querySelectorAll('.expand-toggle').forEach(button => {
  const nodeId = button.dataset.workItemId;
  console.log('Testing node:', nodeId);
  
  // Trigger expansion
  button.click();
  
  // Wait for HTMX
  setTimeout(() => {
    const container = document.getElementById(`children-${nodeId}`);
    const parent = document.getElementById(`node-${nodeId}`);
    
    console.log('Parent position:', parent.offsetTop);
    console.log('Container position:', container.offsetTop);
    
    if (container.offsetTop > parent.offsetTop) {
      console.log('✅ Children below parent');
    } else {
      console.error('❌ Children above parent!');
    }
  }, 500);
});
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Container Nested in Card

```html
<!-- WRONG -->
<div class="node-card">
  <button>Expand</button>
  <div class="children-container">...</div>
</div>
```

### ❌ Mistake 2: Container Before Card

```html
<!-- WRONG -->
<div class="tree-node">
  <div class="children-container">...</div>
  <div class="node-card">...</div>
</div>
```

### ❌ Mistake 3: Wrong HTMX Swap

```html
<!-- WRONG -->
<button hx-swap="beforebegin">Expand</button>
```

---

## Reference Documents

- **Complete Guide:** `/docs/research/TREE_DOM_ORDERING.md`
- **Visual Guide:** `/docs/research/TREE_DOM_ORDERING_VISUAL.md`
- **MPTT Documentation:** https://django-mptt.readthedocs.io/
- **HTMX Swap Docs:** https://htmx.org/attributes/hx-swap/

---

## Need Help?

If children still appear above parent after fix:

1. Check browser console for errors
2. Verify HTMX is loading correctly
3. Inspect DOM structure (use browser DevTools)
4. Confirm CSS isn't using absolute positioning
5. Test in different browsers
6. Clear browser cache and reload

---

**Status:** Ready to implement
**Priority:** High
**Estimated Fix Time:** 5-10 minutes
**Testing Time:** 10-15 minutes
