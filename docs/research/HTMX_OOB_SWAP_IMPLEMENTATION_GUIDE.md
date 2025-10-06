# HTMX Out-of-Band (OOB) Swap Implementation Guide

**Date:** 2025-10-06
**Status:** Reference Documentation
**Author:** Research based on HTMX documentation, community best practices, and OBCMS codebase analysis

---

## Executive Summary

This document provides a comprehensive technical guide for implementing HTMX out-of-band (OOB) swaps in Django views, with specific focus on updating multiple elements simultaneously (e.g., sidebar content + tree table rows).

**Key Finding:** The OBCMS implementation at `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/views/work_items.py` (lines 786-837) follows correct OOB swap patterns, but there are critical considerations for table row elements.

---

## What are HTMX Out-of-Band Swaps?

The `hx-swap-oob` attribute allows you to specify that some content in a response should be swapped into the DOM somewhere **other than the target**, enabling you to update multiple elements with a single HTMX request.

### Basic Concept

```html
<!-- HTMX request targets #main-content -->
<div hx-get="/api/update" hx-target="#main-content">Click me</div>

<!-- Server response can update BOTH #main-content AND other elements -->
<div id="main-content">
    <!-- This goes to the target -->
    <p>Main content updated</p>
</div>

<div id="sidebar" hx-swap-oob="true">
    <!-- This goes to #sidebar (out-of-band) -->
    <p>Sidebar also updated!</p>
</div>
```

---

## Critical Questions Answered

### 1. Should the OOB element be a sibling or inside the main response?

**Answer: SIBLING (at the same level as the main content)**

```python
# ✅ CORRECT: OOB element as sibling
response_html = """
<div id="main-content">
    <!-- Main content for the target -->
</div>

<div id="sidebar" hx-swap-oob="true">
    <!-- Out-of-band content -->
</div>
"""

# ❌ WRONG: OOB element nested inside main content
response_html = """
<div id="main-content">
    <!-- Main content -->
    <div id="sidebar" hx-swap-oob="true">
        <!-- This won't work properly! -->
    </div>
</div>
"""
```

**Why?** HTMX scans the response for **top-level** elements with `hx-swap-oob`. Nested elements are not processed.

**Source:** HTMX official documentation states: "When HTMX receives a response from the server, it scans the response for **top-level content** that includes the hx-swap-oob attribute."

### 2. How should the response be structured when the target is `innerHTML`?

**Answer: The main content goes to the target, OOB elements are extracted and swapped separately**

```python
# Target: #sidebar-content with hx-swap="innerHTML"

# Response structure:
"""
<!-- Main content (will become innerHTML of #sidebar-content) -->
<div class="sidebar-detail">
    <h2>Work Item Details</h2>
    <p>Content here...</p>
</div>

<!-- OOB content (will replace #work-item-row-123) -->
<tr id="work-item-row-123" hx-swap-oob="true">
    <td>Updated row content</td>
</tr>
"""
```

**Process:**
1. HTMX scans the response
2. Extracts elements with `hx-swap-oob` (the `<tr>`)
3. Inserts remaining content into target using `innerHTML`
4. Separately swaps the OOB elements

### 3. Are there issues with putting `<tr>` elements directly in the response body?

**Answer: YES - Critical HTML parsing issue!**

**The Problem:** By HTML specification, certain elements (`<tr>`, `<td>`, `<th>`, `<thead>`, `<tbody>`, `<tfoot>`, `<colgroup>`, `<caption>`, `<col>`, `<li>`) **cannot stand alone** in the DOM. Browsers will strip or misinterpret them.

**Common Symptom:**
```html
<!-- You send this: -->
<tr id="work-item-row-123" hx-swap-oob="true">
    <td>Cell 1</td>
    <td>Cell 2</td>
</tr>

<!-- Browser receives this (TR stripped!): -->
<td>Cell 1</td>
<td>Cell 2</td>
<!-- Only <td> elements are inserted, not the <tr>! -->
```

### 4. Do we need a wrapper element for OOB table rows?

**Answer: YES - Two proven solutions**

#### Solution 1: `<template>` Tag (Recommended by HTMX)

```html
<!-- Wrap <tr> in <template> tag -->
<div id="sidebar-content">
    <!-- Main content -->
</div>

<template>
    <tr id="work-item-row-123" hx-swap-oob="true">
        <td>Updated cell content</td>
        <td>More content</td>
    </tr>
</template>
```

**Why it works:** The `<template>` tag is designed to hold HTML fragments that are not rendered until used. HTMX extracts the content from `<template>` tags and processes it correctly.

**Requirements:**
- Enable `htmx.config.useTemplateFragments = true` (default in HTMX 2.0+)
- The `<template>` tag will be automatically removed from the final DOM

**Django Implementation:**
```python
from django.template.loader import render_to_string

# Render the row
row_html = render_to_string('work_items/_work_item_tree_row.html', {
    'work_item': work_item
}, request=request)

# Wrap in <template> and add hx-swap-oob
response_html = f"""
{main_content_html}

<template>
    {row_html.replace(f'id="work-item-row-{work_item.id}"',
                      f'id="work-item-row-{work_item.id}" hx-swap-oob="true"', 1)}
</template>
"""
```

#### Solution 2: `<tbody>` Wrapper

```html
<!-- Wrap <tr> in <tbody> with hx-swap-oob -->
<div id="sidebar-content">
    <!-- Main content -->
</div>

<tbody id="work-item-row-123" hx-swap-oob="true">
    <tr>
        <td>Updated cell content</td>
        <td>More content</td>
    </tr>
</tbody>
```

**Why it works:** `<tbody>` is a valid standalone element. When you swap it, the entire tbody (including the tr) is replaced.

**Trade-off:** You must structure your table to use `<tbody id="row-123">` instead of `<tr id="row-123">`.

**Not recommended for OBCMS** because our current templates use `<tr id="work-item-row-{{ work_item.id }}">`.

---

## Common Pitfalls and Troubleshooting

### Pitfall 1: OOB Swap Doesn't Fire

**Symptom:** Console shows no `htmx:oobBeforeSwap` event, element doesn't update

**Causes:**
1. **Missing or mismatched ID:** The element with `hx-swap-oob` must have an `id` that matches an existing element in the DOM
2. **Nested OOB elements:** OOB elements must be top-level in the response, not nested
3. **Invalid selector syntax:** Using complex selectors like `hx-swap-oob="true:#my-element"` (correct: `hx-swap-oob="#my-element"`)

**Debug:**
```javascript
// Enable HTMX debug extension
htmx.logAll();

// Listen for OOB events
document.body.addEventListener('htmx:oobBeforeSwap', function(evt) {
    console.log('OOB swap about to happen:', evt.detail);
});

document.body.addEventListener('htmx:oobAfterSwap', function(evt) {
    console.log('OOB swap completed:', evt.detail);
});
```

### Pitfall 2: `<tr>` Element Gets Stripped

**Symptom:** Only `<td>` elements appear, not the `<tr>`

**Solution:** Use `<template>` wrapper (see Solution 1 above)

### Pitfall 3: Outer Element Stripped with `beforeend`/`afterend`

**Symptom:** When using `hx-swap-oob="beforeend:#list"`, the wrapper element disappears

**Example:**
```html
<!-- You send: -->
<div hx-swap-oob="beforeend:#my-list">
    <li>New item</li>
</div>

<!-- Result: Only <li> is inserted, <div> is stripped -->
```

**Why?** For swap strategies other than `outerHTML` or `true`, HTMX strips the wrapper element and only inserts the inner content.

**Solution:** This is expected behavior! Structure your response accordingly:

```html
<!-- For appending a list item: -->
<div hx-swap-oob="beforeend:#my-list">
    <li>New item</li>  <!-- Only this gets inserted -->
</div>

<!-- For replacing a table row: -->
<tr id="row-123" hx-swap-oob="true">  <!-- Use 'true' or 'outerHTML' -->
    <td>Cell content</td>
</tr>
```

### Pitfall 4: Multiple Elements with Same ID

**Symptom:** Only the first element updates, or wrong element updates

**Solution:** Ensure unique IDs. If you need to update multiple similar elements, use a selector:

```html
<!-- Update all elements with class 'update-me' -->
<div hx-swap-oob="true" class="update-me">Content</div>

<!-- Or use multiple OOB elements with different IDs -->
<div id="element-1" hx-swap-oob="true">Content 1</div>
<div id="element-2" hx-swap-oob="true">Content 2</div>
<div id="element-3" hx-swap-oob="true">Content 3</div>
```

---

## OBCMS Implementation Analysis

### Current Implementation (work_items.py, lines 786-837)

**Location:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/views/work_items.py`

```python
if is_work_items_tree:
    # Return updated edit form for sidebar + updated tree row for instant update
    from django.template.loader import render_to_string
    from common.forms.work_items import WorkItemQuickEditForm

    # Re-render the edit form with updated data (keep sidebar open)
    form = WorkItemQuickEditForm(instance=work_item, user=request.user)
    context = {'form': form, 'work_item': work_item}
    edit_form_html = render_to_string(edit_template, context, request=request)

    # Render the updated tree row for out-of-band swap
    # Template now has id="work-item-row-{{ work_item.id }}" for HTMX targeting
    row_html = render_to_string('work_items/_work_item_tree_row.html', {
        'work_item': work_item
    }, request=request)

    # Extract ONLY the main <tr> (exclude placeholder and skeleton rows)
    import re
    # Match the main row: from opening <tr id="work-item-row-X"> to its closing </tr>
    # Use non-greedy match to get just the first <tr>...</tr>
    pattern = rf'(<tr\s+id="work-item-row-{work_item.id}"[^>]*>.*?</tr>)'
    match = re.search(pattern, row_html, re.DOTALL)

    if match:
        # Successfully extracted just the main row
        main_row_only = match.group(1)
        row_html_with_oob = main_row_only.replace(
            f'id="work-item-row-{work_item.id}"',
            f'id="work-item-row-{work_item.id}" hx-swap-oob="true"',
            1
        )
    else:
        # Fallback: add hx-swap-oob to entire template output
        # This includes placeholder/skeleton rows, but HTMX will only swap the matching ID
        row_html_with_oob = row_html.replace(
            f'id="work-item-row-{work_item.id}"',
            f'id="work-item-row-{work_item.id}" hx-swap-oob="true"',
            1
        )

    # Combine both: edit form stays in sidebar + row updates instantly
    from django.http import HttpResponse
    combined_html = edit_form_html + '\n' + row_html_with_oob

    response = HttpResponse(combined_html)
    response['HX-Trigger'] = json.dumps({
        'showToast': {
            'message': f'{work_item.get_work_type_display()} updated successfully',
            'level': 'success'
        }
    })
    return response
```

### Analysis: What's Correct

1. ✅ **Sibling structure:** OOB element is concatenated as a sibling (`edit_form_html + '\n' + row_html_with_oob`)
2. ✅ **Correct swap value:** Uses `hx-swap-oob="true"` (equivalent to `outerHTML`)
3. ✅ **Unique ID targeting:** Targets `id="work-item-row-{work_item.id}"`
4. ✅ **Regex extraction:** Cleverly extracts only the main `<tr>`, excluding placeholder/skeleton rows

### Analysis: Potential Issue (THE BUG!)

**Problem:** The `<tr>` element is returned directly in the response body **without a `<template>` wrapper**.

**Why this causes issues:**
- According to HTML spec, `<tr>` cannot exist as a top-level element
- When Django's HttpResponse sends `edit_form_html + '\n' + row_html_with_oob`, the browser parses it
- The browser may strip the `<tr>` tags, leaving only `<td>` elements
- HTMX tries to swap `id="work-item-row-123"` but can't find it (because `<tr>` was stripped)
- Result: OOB swap silently fails

**Evidence from web research:**
- GitHub Issue #1198: "htmx-oob-swap not replacing `<tr>` (table row) fragments"
- Stack Overflow: "HTMX hx-swap-oob adding a new table row only adds the `<td>`'s and not the wrapping `<tr>`"
- Solution recommended: "Wrap your row in a `<template>` tag"

---

## Recommended Fix for OBCMS

### Option 1: Wrap `<tr>` in `<template>` (Recommended)

```python
# After extracting the row HTML
if match:
    main_row_only = match.group(1)
    row_html_with_oob = main_row_only.replace(
        f'id="work-item-row-{work_item.id}"',
        f'id="work-item-row-{work_item.id}" hx-swap-oob="true"',
        1
    )
    # Wrap in <template> to prevent HTML parser from stripping <tr>
    row_html_with_oob = f'<template>{row_html_with_oob}</template>'
else:
    row_html_with_oob = row_html.replace(
        f'id="work-item-row-{work_item.id}"',
        f'id="work-item-row-{work_item.id}" hx-swap-oob="true"',
        1
    )
    row_html_with_oob = f'<template>{row_html_with_oob}</template>'

# Combine both: edit form stays in sidebar + row updates instantly
combined_html = edit_form_html + '\n' + row_html_with_oob
```

**Verification required:**
- Ensure `htmx.config.useTemplateFragments = true` is enabled (default in HTMX 2.0+)
- Check HTMX version in base template

### Option 2: Use `<tbody>` wrapper (Not recommended)

Would require restructuring the entire tree table template to use `<tbody id="work-item-row-123">` instead of `<tr id="work-item-row-123">`. This is a larger refactor.

---

## Best Practices for Django + HTMX OOB Swaps

### 1. Always Use Sibling Structure

```python
# ✅ CORRECT
main_html = render_to_string('main.html', context, request=request)
oob_html = render_to_string('oob.html', context, request=request)
combined = main_html + '\n' + oob_html

# ❌ WRONG
main_html = render_to_string('main.html', {'oob_content': oob_html}, request=request)
# This nests OOB content inside main content
```

### 2. Wrap Special Elements in `<template>`

```python
# For <tr>, <td>, <th>, <li>, etc.
row_html = render_to_string('_row.html', context, request=request)
row_html_with_oob = row_html.replace('id="row-123"', 'id="row-123" hx-swap-oob="true"', 1)
wrapped = f'<template>{row_html_with_oob}</template>'
```

### 3. Use Specific Swap Strategies

```python
# Different swap strategies for different use cases:

# Replace entire element (including the element itself)
'hx-swap-oob="true"'  # or 'outerHTML'

# Replace innerHTML only
'hx-swap-oob="innerHTML:#target"'

# Append to end of list
'hx-swap-oob="beforeend:#list"'

# Prepend to beginning
'hx-swap-oob="afterbegin:#list"'

# Insert before element
'hx-swap-oob="beforebegin:#target"'

# Insert after element
'hx-swap-oob="afterend:#target"'
```

### 4. Combine with HX-Trigger Headers

```python
import json
from django.http import HttpResponse

response = HttpResponse(combined_html)
response['HX-Trigger'] = json.dumps({
    'showToast': {
        'message': 'Item updated successfully',
        'level': 'success'
    },
    'refreshCounters': True,
    'itemUpdated': {'id': item.id}
})
return response
```

### 5. Debug with HTMX Events

```javascript
// Add to your base template for debugging
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    console.log('Before swap:', evt.detail);
});

document.body.addEventListener('htmx:afterSwap', function(evt) {
    console.log('After swap:', evt.detail);
});

document.body.addEventListener('htmx:oobBeforeSwap', function(evt) {
    console.log('OOB Before swap:', evt.detail);
});

document.body.addEventListener('htmx:oobAfterSwap', function(evt) {
    console.log('OOB After swap:', evt.detail);
});

// Enable full HTMX logging
htmx.logAll();
```

### 6. Handle Multiple OOB Updates

```python
# Update multiple elements in one response
main_html = render_to_string('main.html', context, request=request)
sidebar_html = render_to_string('sidebar.html', context, request=request)
row_html = render_to_string('row.html', context, request=request)
counter_html = render_to_string('counter.html', context, request=request)

# Add hx-swap-oob to each OOB element
sidebar_with_oob = sidebar_html.replace('id="sidebar"', 'id="sidebar" hx-swap-oob="true"', 1)
row_with_oob = f'<template>{row_html.replace("id=", 'hx-swap-oob="true" id=', 1)}</template>'
counter_with_oob = counter_html.replace('id="counter"', 'id="counter" hx-swap-oob="true"', 1)

# Combine all
combined = main_html + '\n' + sidebar_with_oob + '\n' + row_with_oob + '\n' + counter_with_oob
```

---

## Testing Checklist

When implementing OOB swaps, verify:

- [ ] OOB element has matching `id` in DOM
- [ ] OOB element is a sibling, not nested
- [ ] Special elements (`<tr>`, `<li>`) are wrapped in `<template>`
- [ ] Swap strategy is appropriate (`true`, `innerHTML`, `beforeend`, etc.)
- [ ] Browser console shows no errors
- [ ] HTMX events fire: `htmx:oobBeforeSwap`, `htmx:oobAfterSwap`
- [ ] Multiple OOB elements all update correctly
- [ ] Works across different browsers (Chrome, Firefox, Safari)
- [ ] Mobile/responsive views work correctly
- [ ] No duplicate IDs in the DOM

---

## References

### Official HTMX Documentation
- [hx-swap-oob Attribute](https://htmx.org/attributes/hx-swap-oob/)
- [Out-of-Band Swaps Tutorial](https://htmx.org/examples/update-other-content/)

### GitHub Issues (Critical Reading)
- [#1198 - htmx-oob-swap not replacing `<tr>` fragments](https://github.com/bigskysoftware/htmx/issues/1198)
- [#1538 - hx-swap-oob strips `<tr>` wrapping](https://github.com/bigskysoftware/htmx/issues/1538)
- [#1900 - hx-swap-oob breaks with `<tbody>`](https://github.com/bigskysoftware/htmx/issues/1900)
- [#2790 - hx-swap-oob strips outer element with beforeend](https://github.com/bigskysoftware/htmx/issues/2790)

### Stack Overflow
- [How to swap table row with hx-swap-oob?](https://stackoverflow.com/questions/66655028/htmx-how-to-swap-table-row-with-hx-swap-oob)
- [HTMX adding table row only adds TDs](https://stackoverflow.com/questions/76612680/)

### Community Resources
- [Django HTMX Patterns (spookylukey)](https://github.com/spookylukey/django-htmx-patterns)
- [Using Django messages with OOB swaps](https://blog.benoitblanchon.fr/django-htmx-messages-framework-oob/)

---

## Conclusion

**For OBCMS Work Items Tree:**

The current implementation follows most OOB best practices, but **critically missing the `<template>` wrapper** for the `<tr>` element. This causes the HTML parser to strip the table row, preventing the OOB swap from working.

**Recommended fix:**
```python
# Add this line after extracting row HTML:
row_html_with_oob = f'<template>{row_html_with_oob}</template>'
```

This simple addition will ensure the `<tr>` element is preserved during HTML parsing, allowing HTMX to successfully perform the out-of-band swap.

---

**Implementation Status:** Documentation complete, fix pending
**Testing Required:** Verify HTMX version supports `useTemplateFragments` (HTMX 2.0+)
**File Locations:**
- View: `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/views/work_items.py` (lines 786-837)
- Template: `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/templates/work_items/_work_item_tree_row.html`
