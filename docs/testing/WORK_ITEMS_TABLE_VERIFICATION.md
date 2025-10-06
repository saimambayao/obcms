# Work Items Table - Fixed Columns Verification Guide

**Quick Reference for Testing the Fixed Column Layout**

---

## Quick Test (5 Minutes)

### 1. Visual Verification

```bash
# Start development server
cd src
python manage.py runserver
```

**Navigate to:** http://localhost:8000/oobc-management/work-items/

**What to Check:**
- ✅ Table has fixed column widths
- ✅ Columns don't shift when expanding/collapsing
- ✅ Smooth 300ms transition when children load
- ✅ Hierarchy indentation works correctly
- ✅ Long titles truncate with ellipsis

### 2. Expand/Collapse Test

**Steps:**
1. Click expand button (chevron right) on a work item with children
2. **Expected:** Chevron rotates to down, children appear smoothly
3. **Verify:** Columns stay exactly the same width
4. Click collapse button (chevron down)
5. **Expected:** Chevron rotates to right, children disappear
6. **Verify:** Columns still fixed

### 3. Re-Expand Test (JavaScript Cache)

**Steps:**
1. Expand an item (children load via HTMX)
2. Collapse the item
3. Expand the item again
4. **Expected:** Instant expansion (no HTMX call, pure JavaScript)
5. **Verify:** Check Network tab - no new requests

### 4. Expand All / Collapse All

**Steps:**
1. Click "Expand All" button
2. **Expected:** All items expand sequentially
3. **Verify:** Columns stay fixed throughout
4. Click "Collapse All" button
5. **Expected:** All items collapse instantly
6. **Verify:** Tree returns to initial state

---

## Browser Console Verification

### Check for Errors

```javascript
// Open browser console (F12)
// You should see:
✅ Work Items tree navigation initialized (fixed column layout)

// No errors should appear
```

### Inspect State (Advanced)

```javascript
// In console, check itemStates (if exposed for debugging)
// Each item should have:
{
  loaded: true/false,
  expanded: true/false
}
```

---

## Visual Regression Checklist

| Test Case | Before Fix | After Fix | Status |
|-----------|-----------|-----------|--------|
| Expand children | Columns shift | Columns fixed | ✅ |
| Collapse children | Columns shift back | Columns fixed | ✅ |
| Multiple levels | Columns jump | Columns fixed | ✅ |
| Long titles | Overflow | Truncate | ✅ |
| Expand All | Progressive shift | Fixed throughout | ✅ |

---

## Performance Verification

### Measure Expand Time

```javascript
// In browser console
console.time('expand');
// Click expand button
// After children appear:
console.timeEnd('expand');

// Expected:
// First expand: 100-300ms (HTMX request)
// Re-expand: < 20ms (JavaScript only)
```

### Measure Layout Shift (CLS)

```javascript
// Use Chrome DevTools > Lighthouse
// Run audit on Work Items page
// Check "Cumulative Layout Shift" score

// Expected: 0.0 (no layout shift)
```

---

## Keyboard Accessibility Test

**Steps:**
1. Navigate to page
2. Press Tab repeatedly
3. **Expected:** Focus moves to expand buttons
4. Press Enter or Space on focused button
5. **Expected:** Item expands/collapses
6. **Verify:** Focus remains on button

---

## Screen Reader Test (Optional)

**macOS VoiceOver:**
1. Enable VoiceOver (Cmd+F5)
2. Navigate to Work Items table
3. **Expected Announcements:**
   - "Table, 7 columns, X rows"
   - "Title & Hierarchy, column header"
   - "Expand/Collapse, button"
   - Work item titles read correctly

---

## Mobile Responsive Test

**Steps:**
1. Open DevTools (F12)
2. Toggle device toolbar (Cmd+Shift+M)
3. Select iPhone or Android device
4. **Expected:** Horizontal scroll appears (min-width: 1200px)
5. **Verify:** Table maintains fixed columns even on small screens

---

## Edge Cases

### 1. Deep Nesting (5+ Levels)

**Test:**
- Create work item hierarchy 5 levels deep
- Expand all levels
- **Verify:** Indentation increases correctly, columns stay fixed

### 2. Large Dataset (100+ Items)

**Test:**
- Import/create 100+ work items
- Expand multiple items
- **Verify:** Performance remains acceptable (< 500ms)

### 3. Empty Children

**Test:**
- Expand item with `children_count = 0` (should not have expand button)
- **Verify:** No expand button shown

### 4. Filter Then Expand

**Test:**
- Apply filter (e.g., Status: In Progress)
- Expand filtered items
- **Verify:** Columns stay fixed

---

## Known Good States

### Correct Table HTML Structure

```html
<table style="table-layout: fixed; min-width: 1200px;">
  <colgroup>
    <col style="width: 40%;"> <!-- Title -->
    <col style="width: 10%;"> <!-- Type -->
    <col style="width: 10%;"> <!-- Status -->
    <col style="width: 8%;">  <!-- Priority -->
    <col style="width: 12%;"> <!-- Progress -->
    <col style="width: 12%;"> <!-- Dates -->
    <col style="width: 8%;">  <!-- Actions -->
  </colgroup>
  <thead>...</thead>
  <tbody>
    <tr data-work-item-id="1" data-level="0">...</tr>
    <!-- Children appear as siblings, not nested -->
    <tr data-work-item-id="2" data-level="1">...</tr>
    <tr data-work-item-id="3" data-level="1">...</tr>
  </tbody>
</table>
```

### Correct HTMX Attributes

```html
<button
  hx-get="/oobc-management/work-items/1/tree-partial/"
  hx-target="#children-placeholder-1"
  hx-swap="outerHTML swap:300ms"
  data-item-id="1"
  data-toggle="children-1">
  <i class="fas fa-chevron-right toggle-icon"></i>
</button>
```

---

## Troubleshooting

### Issue: Columns Still Shifting

**Check:**
- Verify `table-layout: fixed` in browser inspector
- Confirm `<colgroup>` is present with percentage widths
- Check for conflicting CSS rules

### Issue: Children Not Loading

**Check:**
- Network tab for 500 errors
- Browser console for JavaScript errors
- HTMX debug mode: `htmx.logAll()`

### Issue: Expand Button Does Nothing

**Check:**
- Verify HTMX attributes are correct
- Check `data-item-id` matches work item ID
- Verify HTMX library is loaded

### Issue: Slow Expansion

**Check:**
- Network tab for slow HTMX requests
- Number of children being loaded
- Server response time

---

## Success Criteria

✅ **All tests pass when:**

1. Columns remain fixed width during all operations
2. Expand/collapse is smooth and instant (after first load)
3. No JavaScript errors in console
4. No layout shift (CLS = 0.0)
5. Keyboard navigation works perfectly
6. Responsive layout works on mobile (with horizontal scroll)
7. Expand All / Collapse All functions correctly
8. State is maintained correctly (re-expand doesn't reload)

---

## Sign-Off

**Tester Name:** _________________
**Date:** _________________
**Browser/Device:** _________________

**Result:** ✅ PASS / ❌ FAIL

**Notes:**
___________________________________________
___________________________________________
___________________________________________
