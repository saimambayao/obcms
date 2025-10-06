# Work Items Tree Navigation - Quick Reference

**Last Updated:** 2025-10-06

## State Machine

```
UNLOADED → LOADING → EXPANDED ⇄ COLLAPSED
              ↓
          UNLOADED (on error)
```

## State Definitions

| State | Description | User Action | Next State |
|-------|-------------|-------------|------------|
| **UNLOADED** | Children never loaded | Click button | LOADING (HTMX) |
| **LOADING** | HTMX request in flight | Click ignored | EXPANDED (success) or UNLOADED (error) |
| **EXPANDED** | Children visible | Click button | COLLAPSED (instant) |
| **COLLAPSED** | Children hidden | Click button | EXPANDED (instant) |

## Key Functions

### State Management
```javascript
getNodeState(itemId)           // Get current state
setNodeState(itemId, newState) // Set state (logs transition)
isChildrenLoaded(itemId)       // Check if EXPANDED or COLLAPSED
isNodeExpanded(itemId)         // Check if EXPANDED
```

### UI Updates
```javascript
updateChevron(itemId, expanded)  // Rotate chevron icon
showSkeleton(itemId)             // Show loading skeleton
hideSkeleton(itemId)             // Hide loading skeleton
```

### Children Visibility
```javascript
showChildren(itemId)    // EXPANDED state (show rows)
hideChildren(itemId)    // COLLAPSED state (hide rows)
```

### HTMX Management
```javascript
removePlaceholder(itemId)      // Remove placeholder row
removeHtmxAttributes(itemId)   // Prevent duplicate requests
```

## Event Flow

### First Expansion (HTMX Load)

```
User Click
   ↓
htmx:beforeRequest
   → Check state (prevent duplicate)
   → Set state: LOADING
   → updateChevron(itemId, true)
   → showSkeleton(itemId)
   ↓
HTMX loads from server
   ↓
htmx:afterSwap
   → hideSkeleton(itemId)
   → setNodeState(itemId, EXPANDED)
   → removePlaceholder(itemId)
   → removeHtmxAttributes(itemId)  ← Prevents future HTMX requests
```

### Subsequent Toggles (JavaScript Only)

```
User Click (EXPANDED)
   ↓
hideChildren(itemId)
   → Hide all descendant rows
   → updateChevron(itemId, false)
   → setNodeState(itemId, COLLAPSED)

User Click (COLLAPSED)
   ↓
showChildren(itemId)
   → Show direct children
   → updateChevron(itemId, true)
   → setNodeState(itemId, EXPANDED)
```

## Console Logging

All operations logged with `[Tree]` prefix:

```javascript
[Tree] Node 123: unloaded → loading
[Tree] Loading children for 123
[Tree] Children loaded for 123
[Tree] Node 123: loading → expanded
[Tree] Click on 123 (state: expanded)
[Tree] Collapsing 123
[Tree] Node 123: expanded → collapsed
```

## Error Handling

### Network Error
```javascript
htmx:sendError
   → updateChevron(itemId, false)
   → hideSkeleton(itemId)
   → setNodeState(itemId, UNLOADED)
   → console.error('[Tree] Network error loading {itemId}')
```

### Server Error
```javascript
htmx:responseError
   → updateChevron(itemId, false)
   → hideSkeleton(itemId)
   → setNodeState(itemId, UNLOADED)
   → console.error('[Tree] Server error loading {itemId}')
```

## Bulk Operations

### Expand All
```javascript
1. Iterate all buttons
2. UNLOADED nodes → collect for sequential loading
3. COLLAPSED nodes → showChildren() immediately
4. Load unloaded nodes sequentially (100ms delay)
```

### Collapse All
```javascript
1. Iterate all buttons
2. EXPANDED nodes → hideChildren() immediately
```

## HTML Requirements

### Tree Row
```html
<tr data-work-item-id="{{ work_item.id }}" data-level="{{ work_item.level }}">
    <!-- Content -->
</tr>
```

### Expand Button
```html
<button data-item-id="{{ work_item.id }}"
        hx-get="{% url 'common:work_item_tree_partial' pk=work_item.pk %}"
        hx-target="#children-placeholder-{{ work_item.id }}"
        hx-swap="afterend swap:300ms"
        hx-trigger="click once">
    <i class="fas fa-chevron-right toggle-icon"></i>
    <i class="fas fa-spinner fa-spin htmx-indicator"></i>
</button>
```

**Note:** HTMX attributes removed after first load by `removeHtmxAttributes()`

### Placeholder Row
```html
<tr id="children-placeholder-{{ work_item.id }}" style="display: none;">
    <!-- Removed after children loaded -->
</tr>
```

### Skeleton Row
```html
<tr id="skeleton-row-{{ work_item.id }}" style="display: none;">
    <td colspan="7">
        <div class="animate-pulse">Loading...</div>
    </td>
</tr>
```

## Performance

- **Optimistic UI:** < 50ms feedback on all interactions
- **No Redundant Requests:** HTMX attributes removed after first load
- **Instant Toggle:** JavaScript handles subsequent clicks (no server)
- **Sequential Loading:** Expand All prevents server overload (100ms delay)

## Debugging Tips

1. **Check Console Logs:**
   ```
   [Tree] Node {id}: {oldState} → {newState}
   ```

2. **Inspect State Map:**
   ```javascript
   console.log(nodeStates);  // View all node states
   ```

3. **Check HTMX Attributes:**
   ```javascript
   const button = document.querySelector('[data-item-id="123"]');
   console.log(button.hasAttribute('hx-get'));  // Should be false after load
   ```

4. **Verify State Transitions:**
   - UNLOADED → LOADING → EXPANDED (first click)
   - EXPANDED ⇄ COLLAPSED (subsequent clicks)
   - LOADING → UNLOADED (on error)

## Common Issues

### Issue: Button doesn't toggle after first load
**Solution:** Check if HTMX attributes were removed (`removeHtmxAttributes()`)

### Issue: Duplicate HTMX requests
**Solution:** Verify `hx-trigger="click once"` and attribute removal

### Issue: Children not showing/hiding
**Solution:** Check state transitions and `showChildren()`/`hideChildren()` logic

### Issue: State stuck in LOADING
**Solution:** Check for HTMX errors in console, verify server response

## Testing Checklist

- [ ] First expand (HTMX load)
- [ ] Collapse (hide children)
- [ ] Expand again (show, no HTMX)
- [ ] Collapse again
- [ ] Network error handling
- [ ] Server error handling
- [ ] Expand All functionality
- [ ] Collapse All functionality
- [ ] Prevent clicks during LOADING
- [ ] Console logs for all transitions

## Related Files

- **Template:** `src/templates/work_items/work_item_list.html`
- **Partial:** `src/templates/work_items/_work_item_tree_row.html`
- **View:** `src/common/views/work_items.py`
- **Documentation:** `docs/improvements/WORK_ITEMS_TREE_REFACTORING.md`

## Quick Start

To understand the code:

1. Read the state machine diagram (lines 380-396)
2. Review the NodeState enum (lines 416-425)
3. Check the click handler (lines 794-835)
4. Follow a complete flow from UNLOADED → EXPANDED → COLLAPSED

The code is organized into clear sections with headers:
- `STATE MACHINE`
- `STATE MANAGEMENT`
- `UI UPDATES`
- `CHILDREN VISIBILITY`
- `HTMX EVENT HANDLERS`
- `USER INTERACTIONS`
- `BULK OPERATIONS`

Each section is self-contained and easy to navigate.
