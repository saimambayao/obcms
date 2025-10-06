# Tree Ordering Quick Reference Card

## The Problem

```
❌ Children appearing ABOVE parent in tree expansion
```

## The Root Cause

```
Container positioned BEFORE card in DOM
```

## The Solution

```html
<div class="tree-node">
  <!-- 1. Card FIRST -->
  <div class="node-card">Parent</div>
  
  <!-- 2. Container AFTER -->
  <div class="children-container">
    Children here
  </div>
</div>
```

## Visual Guide

```
╔══════════════════════════════════════╗
║  CORRECT DOM ORDER                   ║
╠══════════════════════════════════════╣
║                                      ║
║  [Position 0] Parent Node Card       ║
║       ↓                              ║
║  [Position 1] Children Container     ║
║       ↓                              ║
║       [1.0] Child 1                  ║
║       [1.1] Child 2                  ║
║       [1.2] Child 3                  ║
║                                      ║
╚══════════════════════════════════════╝
```

## HTMX Configuration

```html
<button hx-get="/children/123"
        hx-target="#children-123"
        hx-swap="innerHTML"
        hx-trigger="click once">
  Expand
</button>
```

## MPTT Ordering

```python
children = work_item.get_children().order_by('lft')
```

## Checklist

- [ ] Card before container
- [ ] Container is sibling (not nested)
- [ ] HTMX target is container ID
- [ ] HTMX swap is "innerHTML"
- [ ] MPTT ordered by 'lft'

## Documentation

- **Full Guide:** `/docs/research/TREE_DOM_ORDERING.md`
- **Visual:** `/docs/research/TREE_DOM_ORDERING_VISUAL.md`
- **Fix Guide:** `/docs/research/TREE_BUG_FIX_GUIDE.md`

## The Golden Rule

```
DOM ORDER = VISUAL ORDER

Parent → Children (ALWAYS)
```
