# HTMX Out-of-Band Swap Quick Reference

**Date:** 2025-10-06
**For:** Quick implementation reference

---

## The Golden Rules

1. **OOB elements MUST be siblings (top-level), never nested**
2. **Table elements (`<tr>`, `<td>`, etc.) MUST be wrapped in `<template>`**
3. **OOB elements need matching IDs in the DOM**
4. **Use `hx-swap-oob="true"` for outerHTML replacement**

---

## Basic Pattern

```python
# Django view returning main content + OOB update
main_html = render_to_string('main.html', context, request=request)
oob_html = render_to_string('oob.html', context, request=request)

# Add hx-swap-oob attribute
oob_with_attr = oob_html.replace('id="target"', 'id="target" hx-swap-oob="true"', 1)

# Combine as SIBLINGS
combined = main_html + '\n' + oob_with_attr

return HttpResponse(combined)
```

---

## Table Row Pattern (CRITICAL!)

```python
# For <tr> elements - MUST wrap in <template>
row_html = render_to_string('_row.html', context, request=request)

# Add hx-swap-oob
row_with_oob = row_html.replace(
    f'id="row-{item.id}"',
    f'id="row-{item.id}" hx-swap-oob="true"',
    1
)

# WRAP IN TEMPLATE (critical!)
row_wrapped = f'<template>{row_with_oob}</template>'

# Combine with main content
combined = main_html + '\n' + row_wrapped
```

**Why?** Browsers strip `<tr>` elements that aren't inside `<table>/<tbody>`. The `<template>` tag preserves them until HTMX processes the swap.

---

## Common Swap Strategies

```python
# Replace entire element (including tag itself)
'hx-swap-oob="true"'          # Same as outerHTML
'hx-swap-oob="outerHTML"'

# Replace innerHTML only
'hx-swap-oob="innerHTML:#target"'

# Append to end
'hx-swap-oob="beforeend:#list"'

# Prepend to beginning
'hx-swap-oob="afterbegin:#list"'

# Insert before/after element
'hx-swap-oob="beforebegin:#target"'
'hx-swap-oob="afterend:#target"'
```

---

## Multiple OOB Updates

```python
# Update 3 different elements in one response
main = render_to_string('main.html', ctx, request=request)
sidebar = render_to_string('sidebar.html', ctx, request=request)
row = render_to_string('row.html', ctx, request=request)
counter = render_to_string('counter.html', ctx, request=request)

# Add oob to each
sidebar = sidebar.replace('id="sidebar"', 'id="sidebar" hx-swap-oob="true"', 1)
row = f'<template>{row.replace("id=", 'hx-swap-oob="true" id=', 1)}</template>'
counter = counter.replace('id="counter"', 'id="counter" hx-swap-oob="true"', 1)

# Combine all
combined = main + '\n' + sidebar + '\n' + row + '\n' + counter
```

---

## With HX-Trigger Headers

```python
import json
from django.http import HttpResponse

response = HttpResponse(combined_html)
response['HX-Trigger'] = json.dumps({
    'showToast': {'message': 'Updated!', 'level': 'success'},
    'refreshCounters': True,
    'itemUpdated': {'id': 123}
})
return response
```

---

## Debugging

```javascript
// Enable HTMX logging (add to base.html)
htmx.logAll();

// Listen for OOB events
document.body.addEventListener('htmx:oobBeforeSwap', (e) => {
    console.log('OOB swap starting:', e.detail);
});

document.body.addEventListener('htmx:oobAfterSwap', (e) => {
    console.log('OOB swap complete:', e.detail);
});
```

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| OOB swap doesn't fire | Element not top-level | Make it a sibling |
| `<tr>` gets stripped | HTML parser removes it | Wrap in `<template>` |
| Wrong element updates | Duplicate IDs | Ensure unique IDs |
| Wrapper gets stripped | Using beforeend/afterend | Expected behavior |

---

## OBCMS-Specific Fix

**File:** `src/common/views/work_items.py` (line ~824)

**Change:**
```python
# BEFORE (broken):
combined_html = edit_form_html + '\n' + row_html_with_oob

# AFTER (fixed):
row_html_wrapped = f'<template>{row_html_with_oob}</template>'
combined_html = edit_form_html + '\n' + row_html_wrapped
```

---

## Elements That Need `<template>` Wrapper

- `<tr>` (table row)
- `<td>` (table cell)
- `<th>` (table header)
- `<thead>` (table head)
- `<tbody>` (table body)
- `<tfoot>` (table footer)
- `<colgroup>` (column group)
- `<caption>` (table caption)
- `<col>` (column)
- `<li>` (list item - sometimes)

**Rule of thumb:** If the element can only exist inside a specific parent element per HTML spec, wrap it in `<template>`.

---

## Testing Checklist

- [ ] OOB element is a sibling to main content
- [ ] Table elements wrapped in `<template>`
- [ ] ID exists in DOM before swap
- [ ] No duplicate IDs
- [ ] Console shows `htmx:oobBeforeSwap` event
- [ ] Element updates correctly
- [ ] Works in Chrome, Firefox, Safari

---

**Full documentation:** See `HTMX_OOB_SWAP_IMPLEMENTATION_GUIDE.md`
