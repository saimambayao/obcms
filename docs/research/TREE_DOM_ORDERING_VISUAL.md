# Tree DOM Ordering: Visual Reference Guide

**Quick Reference:** Visual diagrams showing correct vs incorrect DOM ordering for tree tables

---

## Problem Visualization

### ❌ INCORRECT: Children Appear ABOVE Parent

```
┌─────────────────────────────────────────────────┐
│ Work Items Tree                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌────────────────────┐                          │
│ │   Task A1.1        │ ← Child 1 (WRONG!)      │
│ └────────────────────┘                          │
│                                                 │
│ ┌────────────────────┐                          │
│ │   Task A1.2        │ ← Child 2 (WRONG!)      │
│ └────────────────────┘                          │
│                                                 │
│ ┌────────────────────┐                          │
│ │ ▶ Activity A1      │ ← Parent (WRONG!)       │
│ └────────────────────┘                          │
│                                                 │
└─────────────────────────────────────────────────┘

DOM Order:
1. <div id="node-child1">Task A1.1</div>
2. <div id="node-child2">Task A1.2</div>
3. <div id="node-parent">Activity A1</div>  ← Parent AFTER children!
```

**Why This Happens:**
- Children container positioned BEFORE parent card in DOM
- HTMX inserts children, but container is above parent
- Visual result: Tree appears inverted

---

### ✅ CORRECT: Children Appear BELOW Parent

```
┌─────────────────────────────────────────────────┐
│ Work Items Tree                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌────────────────────┐                          │
│ │ ▼ Activity A1      │ ← Parent (CORRECT!)     │
│ └────────────────────┘                          │
│   ┌────────────────┐                            │
│   │ Task A1.1      │   ← Child 1 (CORRECT!)    │
│   └────────────────┘                            │
│   ┌────────────────┐                            │
│   │ Task A1.2      │   ← Child 2 (CORRECT!)    │
│   └────────────────┘                            │
│                                                 │
└─────────────────────────────────────────────────┘

DOM Order:
1. <div id="node-parent">Activity A1</div>
2. <div id="children-parent">
     <div id="node-child1">Task A1.1</div>
     <div id="node-child2">Task A1.2</div>
   </div>
```

**Why This Works:**
- Parent node at position 0
- Children container at position 1 (after parent)
- Children load INTO container
- Visual result: Proper tree hierarchy

---

## DOM Structure Comparison

### ❌ Incorrect Structure

```html
<div class="tree-node">
  <!-- WRONG: Children container BEFORE node card -->
  <div class="children-container" id="children-123">
    <!-- Children loaded here -->
  </div>

  <div class="node-card">
    <button hx-target="#children-123">Expand</button>
    <span>Parent Item</span>
  </div>
</div>
```

**Problem:** Container renders above the card, so children appear above parent.

---

### ✅ Correct Structure (Container Pattern)

```html
<div class="tree-node">
  <!-- Node card FIRST -->
  <div class="node-card">
    <button hx-target="#children-123"
            hx-swap="innerHTML">Expand</button>
    <span>Parent Item</span>
  </div>

  <!-- Children container AFTER card -->
  <div class="children-container hidden" id="children-123">
    <!-- Children loaded here -->
  </div>
</div>
```

**Solution:** Card renders first, then container below it.

---

### ✅ Alternative: Inline Insertion (No Container)

```html
<!-- Parent Node -->
<div class="tree-node" id="node-123">
  <div class="node-card">
    <button hx-target="#node-123"
            hx-swap="afterend">Expand</button>
    <span>Parent Item</span>
  </div>
</div>

<!-- Children inserted AFTER this node by HTMX -->
```

**Solution:** No container needed. HTMX inserts children as siblings.

---

## HTMX Swap Strategy Visual Guide

### Understanding `hx-swap` Positions

```html
<!-- beforebegin (Position A) -->
<div id="target">
  <!-- afterbegin (Position B) -->
  Target Content
  <!-- beforeend (Position C) -->
</div>
<!-- afterend (Position D) -->
```

### For Tree Expansion: Which Position?

```
Scenario: Expand "Activity A1" to show child tasks

Initial DOM:
┌─────────────────────┐
│ Activity A1         │ ← Target element
└─────────────────────┘

Goal: Insert children AFTER parent
```

#### Option 1: `hx-swap="innerHTML"` (Container Pattern)

```html
<div class="tree-node">
  <div class="node-card">Activity A1</div>
  <div id="children-123">
    <!-- hx-swap="innerHTML" replaces THIS content -->
  </div>
</div>
```

**Result:**
```
┌─────────────────────┐
│ Activity A1         │
├─────────────────────┤
│  ┌──────────────┐   │
│  │ Task A1.1    │   │ ← Inserted INTO container
│  └──────────────┘   │
│  ┌──────────────┐   │
│  │ Task A1.2    │   │ ← Inserted INTO container
│  └──────────────┘   │
└─────────────────────┘
```

**Best for:** Structured layouts, easy collapse, ARIA grouping

---

#### Option 2: `hx-swap="afterend"` (Inline Pattern)

```html
<div class="tree-node" id="node-123">
  <div class="node-card">
    <button hx-target="#node-123"
            hx-swap="afterend">Expand</button>
    Activity A1
  </div>
</div>
<!-- hx-swap="afterend" inserts AFTER node-123 -->
```

**Result:**
```
┌─────────────────────┐
│ Activity A1         │ ← Original node
└─────────────────────┘
┌─────────────────────┐
│  Task A1.1          │ ← Inserted sibling 1
└─────────────────────┘
┌─────────────────────┐
│  Task A1.2          │ ← Inserted sibling 2
└─────────────────────┘
```

**Best for:** Simple structures, minimal DOM, direct insertion

---

## MPTT Tree Order Visualization

### Database Tree Structure (MPTT)

```
Project A
├── Activity A1
│   ├── Task A1.1
│   └── Task A1.2
└── Activity A2
    └── Task A2.1
```

### MPTT Left/Right Values

```
Node            lft  rght  level
─────────────────────────────────
Project A       1    12    0
  Activity A1   2    7     1
    Task A1.1   3    4     2
    Task A1.2   5    6     2
  Activity A2   8    11    1
    Task A2.1   9    10    2
```

### Pre-Order Traversal (Display Order)

```python
# Django query
WorkItem.objects.order_by('tree_id', 'lft')

# Result (in this order):
1. Project A      (lft=1)  ← Parent first
2.   Activity A1  (lft=2)  ← Then children
3.     Task A1.1  (lft=3)
4.     Task A1.2  (lft=5)
5.   Activity A2  (lft=8)
6.     Task A2.1  (lft=9)
```

**Key Insight:** In MPTT, `lft` values determine display order. Lower `lft` = appears first.

---

## Complete Working Example

### HTML Template

```html
<!-- Parent Node Container -->
<div class="tree-node relative"
     id="node-{{ work_item.id }}"
     data-depth="{{ depth }}">

  <!-- Node Card -->
  <div class="node-card bg-white border rounded-xl p-4">
    <!-- Expand/Collapse Button -->
    {% if work_item.get_children %}
    <button type="button"
            class="expand-toggle"
            hx-get="{% url 'work_item_children' work_item.id %}"
            hx-target="#children-{{ work_item.id }}"
            hx-swap="innerHTML"
            hx-trigger="click once"
            onclick="toggleNode('{{ work_item.id }}')">
      <i class="fas fa-chevron-right" id="icon-{{ work_item.id }}"></i>
    </button>
    {% endif %}

    <span>{{ work_item.title }}</span>
  </div>

  <!-- Children Container (AFTER card) -->
  {% if work_item.get_children %}
  <div class="children-container hidden"
       id="children-{{ work_item.id }}"
       role="group">
    <!-- HTMX loads children here -->
  </div>
  {% endif %}

</div>
```

### Server Response (Children Loaded via HTMX)

```django
{# Template: _work_item_tree_nodes.html #}
{% for child in children %}
  {% include "work_item_tree.html" with work_item=child depth=parent_level %}
{% endfor %}
```

### JavaScript Toggle Function

```javascript
function toggleNode(nodeId) {
  const icon = document.getElementById(`icon-${nodeId}`);
  const container = document.getElementById(`children-${nodeId}`);
  const button = icon.closest('button');
  const isExpanded = button.getAttribute('aria-expanded') === 'true';

  if (isExpanded) {
    // Collapse
    container.classList.add('hidden');
    icon.classList.remove('fa-chevron-down');
    icon.classList.add('fa-chevron-right');
    button.setAttribute('aria-expanded', 'false');
  } else {
    // Expand
    container.classList.remove('hidden');
    icon.classList.remove('fa-chevron-right');
    icon.classList.add('fa-chevron-down');
    button.setAttribute('aria-expanded', 'true');
  }
}
```

### Resulting DOM After Expansion

```html
<!-- Parent -->
<div class="tree-node" id="node-parent">
  <div class="node-card">
    <button aria-expanded="true">
      <i class="fas fa-chevron-down"></i>
    </button>
    <span>Activity A1</span>
  </div>

  <!-- Children Container (visible) -->
  <div class="children-container" id="children-parent">
    
    <!-- Child 1 -->
    <div class="tree-node" id="node-child1">
      <div class="node-card">
        <span>Task A1.1</span>
      </div>
    </div>

    <!-- Child 2 -->
    <div class="tree-node" id="node-child2">
      <div class="node-card">
        <span>Task A1.2</span>
      </div>
    </div>

  </div>
</div>
```

---

## Debugging Checklist

When children appear in the wrong order:

### Step 1: Inspect DOM Structure

```javascript
// In browser console
const parent = document.getElementById('node-123');
console.log('Parent:', parent);
console.log('Next sibling:', parent.nextElementSibling);

// Should show children container, not another parent node
```

### Step 2: Check Element Positions

```javascript
// Get positions of elements
const nodes = document.querySelectorAll('.tree-node');
nodes.forEach((node, index) => {
  console.log(`Position ${index}:`, node.id, node.querySelector('.node-card').textContent);
});

// Output should show parents before children
```

### Step 3: Verify HTMX Configuration

```html
<!-- Check these attributes -->
hx-target="#children-123"  ← Target is correct ID?
hx-swap="innerHTML"        ← Swap strategy is innerHTML?
hx-get="/api/children/123" ← URL returns correct children?
```

### Step 4: Test Expansion Manually

```javascript
// Manually trigger HTMX request
const button = document.querySelector('[hx-get="/api/children/123"]');
htmx.trigger(button, 'click');

// Check if children appear in correct position
```

---

## Common Pitfalls

### Pitfall 1: Nesting Container Inside Card

```html
<!-- ❌ WRONG -->
<div class="node-card">
  <button>Expand</button>
  <span>Parent</span>
  
  <div class="children-container">
    <!-- Children nested inside card -->
  </div>
</div>
```

**Problem:** Children render inside parent card, breaking layout.

**Fix:** Move container outside card, make it a sibling.

---

### Pitfall 2: Wrong HTMX Swap Strategy

```html
<!-- ❌ WRONG -->
<button hx-target="#node-123"
        hx-swap="beforebegin">
  Expand
</button>
```

**Problem:** `beforebegin` inserts children BEFORE parent node.

**Fix:** Use `afterend` (inline) or target container with `innerHTML`.

---

### Pitfall 3: CSS Positioning Issues

```css
/* ❌ WRONG */
.children-container {
  position: absolute;
  top: 0; /* Container floats to top */
}
```

**Problem:** Absolute positioning removes container from flow.

**Fix:** Use `position: relative` or static (default).

---

### Pitfall 4: Forgetting MPPT Ordering

```python
# ❌ WRONG
children = work_item.get_children()  # No ordering

# ✅ CORRECT
children = work_item.get_children().order_by('lft')
```

**Problem:** Children appear in random order without MPTT sorting.

**Fix:** Always use `.order_by('lft')` for tree traversal.

---

## Quick Reference Card

```
╔════════════════════════════════════════════════════╗
║ TREE DOM ORDERING QUICK REFERENCE                 ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║ Container Pattern:                                 ║
║   hx-target="#children-123"                        ║
║   hx-swap="innerHTML"                              ║
║   → Children load INTO container                   ║
║                                                    ║
║ Inline Pattern:                                    ║
║   hx-target="#node-123"                            ║
║   hx-swap="afterend"                               ║
║   → Children insert AFTER node                     ║
║                                                    ║
║ MPTT Ordering:                                     ║
║   .order_by('tree_id', 'lft')                      ║
║   → Pre-order traversal (parent → children)        ║
║                                                    ║
║ DOM Structure:                                     ║
║   1. Parent card                                   ║
║   2. Children container (sibling, not nested)      ║
║                                                    ║
║ Critical Rules:                                    ║
║   ✓ Children after parent in DOM                   ║
║   ✓ Container is sibling of card                   ║
║   ✓ MPTT ordering for display                      ║
║   ✗ No absolute positioning                        ║
║   ✗ No nesting container in card                   ║
║                                                    ║
╚════════════════════════════════════════════════════╝
```

---

**Related:** See `TREE_DOM_ORDERING.md` for complete documentation
**Version:** 1.0
**Last Updated:** 2025-10-06
