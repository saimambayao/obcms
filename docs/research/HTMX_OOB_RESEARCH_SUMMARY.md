# HTMX Out-of-Band Swap Research Summary

**Date:** 2025-10-06
**Research Focus:** Implementing HTMX OOB swaps for updating multiple elements (sidebar + tree row) in Django views
**Status:** Research Complete - Implementation Ready

---

## Executive Summary

Research has identified the root cause of why out-of-band (OOB) table row swaps are not working in the OBCMS work items tree view. The implementation in `src/common/views/work_items.py` follows most best practices but is missing a critical wrapper element required by HTML parsing rules.

### The Problem

When Django returns a `<tr>` element in an HTTP response for HTMX OOB swapping, the browser's HTML parser strips the `<tr>` tag because table rows cannot exist as standalone elements per HTML specification. This causes the OOB swap to silently fail.

### The Solution

Wrap the `<tr>` element in a `<template>` tag, which preserves the HTML structure until HTMX processes it. Additionally, enable `htmx.config.useTemplateFragments = true` in HTMX 1.9.12 (this is the default in HTMX 2.0+).

**Effort:** 5 minutes implementation, 15 minutes testing
**Risk:** Very low
**Impact:** Fixes instant UI updates for work item tree editing

---

## Key Research Findings

### 1. OOB Elements Must Be Siblings

**Rule:** Elements with `hx-swap-oob` must be top-level (siblings) in the response, never nested.

```python
# ✅ CORRECT: Siblings
main_html = render_to_string('main.html', ctx, request=request)
oob_html = render_to_string('oob.html', ctx, request=request)
combined = main_html + '\n' + oob_html

# ❌ WRONG: Nested
# OOB element inside main content will not be processed
```

**OBCMS Status:** ✅ Current implementation is correct (line 828 in work_items.py)

### 2. Table Elements Require Special Handling

**Problem:** HTML elements that can only exist inside specific parents (`<tr>`, `<td>`, `<th>`, `<thead>`, `<tbody>`, `<tfoot>`, `<colgroup>`, `<caption>`, `<col>`, `<li>`) get stripped by the browser's HTML parser when returned as standalone elements.

**Symptom:**
```html
<!-- Server sends: -->
<tr id="work-item-row-123" hx-swap-oob="true">
    <td>Cell content</td>
</tr>

<!-- Browser receives: -->
<td>Cell content</td>
<!-- <tr> tag was stripped! -->
```

**Solution:** Wrap in `<template>` tag

```html
<template>
    <tr id="work-item-row-123" hx-swap-oob="true">
        <td>Cell content</td>
    </tr>
</template>
```

**OBCMS Status:** ❌ Missing in current implementation

### 3. HTMX Version Compatibility

**Current Version:** HTMX 1.9.12

**Critical Config:**
- `htmx.config.useTemplateFragments` = **false** (default in 1.9.x)
- Must be manually enabled for `<template>` wrapper to work
- Default is **true** in HTMX 2.0+

**OBCMS Status:** ❌ Not currently enabled

### 4. How HTMX Processes OOB Swaps

1. HTMX receives HTTP response from server
2. Scans response for **top-level** elements with `hx-swap-oob`
3. If `useTemplateFragments = true`, extracts content from `<template>` tags
4. Extracts OOB elements from response
5. Swaps OOB elements into their target locations
6. Inserts remaining content into the main target

**Key Insight:** HTMX only scans top-level elements, which is why sibling structure is required.

---

## Implementation Guide

### Step 1: Enable Template Fragment Support

**File:** `src/templates/base.html`

**Add after HTMX script (around line 660):**

```html
<!-- HTMX Core -->
<script src="{% static 'vendor/htmx/htmx.min.js' %}" defer></script>

<!-- HTMX Configuration for OOB Table Row Swaps -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Enable template fragment support (required for <tr> OOB swaps)
        htmx.config.useTemplateFragments = true;
        console.log('HTMX useTemplateFragments enabled');
    });
</script>
```

### Step 2: Wrap Table Row in Template Tag

**File:** `src/common/views/work_items.py`

**Current code (line 824-828):**
```python
# Combine both: edit form stays in sidebar + row updates instantly
from django.http import HttpResponse
combined_html = edit_form_html + '\n' + row_html_with_oob

response = HttpResponse(combined_html)
```

**Updated code:**
```python
# Wrap table row in <template> to prevent HTML parser from stripping <tr>
row_html_wrapped = f'<template>{row_html_with_oob}</template>'

# Combine both: edit form stays in sidebar + row updates instantly
from django.http import HttpResponse
combined_html = edit_form_html + '\n' + row_html_wrapped

response = HttpResponse(combined_html)
```

### Step 3: Test

1. Start development server: `cd src && ./manage.py runserver`
2. Navigate to work items tree: `/work-items/`
3. Click "Edit" on any work item (sidebar opens)
4. Make a change (e.g., update progress)
5. Save changes
6. **Expected:** Tree row updates instantly without page reload
7. **Check console:** Look for `htmx:oobBeforeSwap` and `htmx:oobAfterSwap` events

---

## Common Issues and Solutions

### Issue: OOB Swap Doesn't Fire

**Symptoms:**
- No `htmx:oobBeforeSwap` event in console
- Tree row doesn't update after saving
- Need to refresh page to see changes

**Causes:**
1. `useTemplateFragments` not enabled
2. `<tr>` not wrapped in `<template>`
3. Mismatched IDs between OOB element and DOM element
4. OOB element nested instead of sibling

**Debug:**
```javascript
// Enable HTMX logging
htmx.logAll();

// Check config
console.log(htmx.config.useTemplateFragments);  // Should be true

// Listen for events
document.body.addEventListener('htmx:oobBeforeSwap', (e) => {
    console.log('OOB swap starting:', e.detail);
});
```

### Issue: Wrong Element Updates

**Cause:** ID mismatch

**Solution:** Ensure OOB element ID matches existing DOM element ID exactly:

```html
<!-- Existing in DOM: -->
<tr id="work-item-row-123">...</tr>

<!-- OOB response must have: -->
<template>
    <tr id="work-item-row-123" hx-swap-oob="true">...</tr>
</template>
```

---

## Why Current Implementation Fails

### Current Flow (Broken)

1. User edits work item in sidebar
2. Django view renders updated row HTML (includes `<tr>`)
3. View adds `hx-swap-oob="true"` to `<tr>`
4. View concatenates edit form + row HTML
5. HttpResponse sends HTML to browser
6. **Browser's HTML parser strips `<tr>` tag** (can't exist standalone)
7. HTMX looks for element with `id="work-item-row-123"`
8. **Can't find it** (was stripped to just `<td>` elements)
9. OOB swap silently fails

### Fixed Flow

1. User edits work item in sidebar
2. Django view renders updated row HTML (includes `<tr>`)
3. View adds `hx-swap-oob="true"` to `<tr>`
4. **View wraps in `<template>` tag**
5. View concatenates edit form + wrapped row HTML
6. HttpResponse sends HTML to browser
7. **`<template>` tag preserves `<tr>` structure**
8. **HTMX (with `useTemplateFragments=true`) extracts from `<template>`**
9. HTMX finds element with `id="work-item-row-123"`
10. OOB swap succeeds - row updates instantly

---

## Supporting Evidence

### From Web Research

**Stack Overflow:** "HTMX hx-swap-oob adding a new table row only adds the `<td>`'s and not the wrapping `<tr>`"
- **Answer:** "Wrap your row in the response in `<tbody>` with `hx-swap-oob` on the `<tbody>` element instead"
- **Alternative:** "Use a `<template>` tag to encapsulate table row elements"

**GitHub Issue #1198:** "htmx-oob-swap not replacing `<tr>` (table row) fragments"
- **Solution:** "You can use a template tag to encapsulate types of elements that, by the HTML spec, can't stand on their own in the DOM"
- **Requires:** `htmx.config.useTemplateFragments` enabled

**HTMX Official Docs:** "Out-of-Band Swaps"
- "When HTMX receives a response from the server, it scans the response for **top-level content** that includes the hx-swap-oob attribute"
- "You can use a `<template>` tag to encapsulate... `<tr>`, `<td>`, `<th>`, `<thead>`, `<tbody>`, `<tfoot>`, `<colgroup>`, `<caption>`, `<col>` & `<li>`"

### From OBCMS Codebase Analysis

**Current Implementation (`src/common/views/work_items.py` lines 786-837):**

✅ **Correct:**
- Sibling structure (concatenates edit form + row)
- Unique ID targeting (`work-item-row-{work_item.id}`)
- Regex extraction of main `<tr>` (excludes placeholders)
- Uses `hx-swap-oob="true"` (outerHTML swap)

❌ **Missing:**
- `<template>` wrapper around `<tr>`
- `htmx.config.useTemplateFragments = true` in base.html

**Template (`src/templates/work_items/_work_item_tree_row.html`):**
- Line 4: `<tr id="work-item-row-{{ work_item.id }}">`
- Lines 228-244: Placeholder and skeleton rows (correctly excluded by regex)

---

## Testing Plan

### Unit Test Checklist

- [ ] Config check: `htmx.config.useTemplateFragments === true`
- [ ] Console logging: No errors when editing work item
- [ ] HTMX events: `htmx:oobBeforeSwap` fires
- [ ] HTMX events: `htmx:oobAfterSwap` fires
- [ ] DOM update: Tree row updates without page reload
- [ ] Progress bar: Updates correctly
- [ ] Status badge: Updates correctly
- [ ] Priority badge: Updates correctly
- [ ] Type badge: Updates correctly
- [ ] Dates: Update correctly
- [ ] Title: Updates correctly

### Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

### Edge Cases

- [ ] Edit root-level work item
- [ ] Edit deeply nested work item (level 5+)
- [ ] Edit work item with children
- [ ] Edit work item with auto-calculated progress
- [ ] Rapid successive edits
- [ ] Edit while tree is expanded
- [ ] Edit while tree is collapsed

---

## Documentation Created

This research has produced three comprehensive documentation files:

1. **[HTMX_OOB_SWAP_IMPLEMENTATION_GUIDE.md](docs/research/HTMX_OOB_SWAP_IMPLEMENTATION_GUIDE.md)**
   - Comprehensive technical guide
   - Answers 4 critical questions
   - Common pitfalls and solutions
   - OBCMS-specific analysis
   - Best practices for Django + HTMX
   - 10+ examples with code

2. **[HTMX_OOB_QUICK_REFERENCE.md](docs/research/HTMX_OOB_QUICK_REFERENCE.md)**
   - Quick implementation patterns
   - Copy-paste ready code examples
   - Troubleshooting table
   - Golden rules
   - Testing checklist

3. **[HTMX_VERSION_COMPATIBILITY.md](docs/research/HTMX_VERSION_COMPATIBILITY.md)**
   - HTMX 1.9.12 specific guidance
   - Config requirements
   - Upgrade path to HTMX 2.0
   - Version comparison
   - Breaking changes to watch

---

## Next Steps

### Immediate (Fix the Bug)

1. **Enable config** (5 min)
   - Edit `src/templates/base.html`
   - Add `htmx.config.useTemplateFragments = true`

2. **Wrap row in template** (5 min)
   - Edit `src/common/views/work_items.py` line 824
   - Change: `combined_html = edit_form_html + '\n' + row_html_with_oob`
   - To: `combined_html = edit_form_html + '\n' + f'<template>{row_html_with_oob}</template>'`

3. **Test** (15 min)
   - Manual testing in browser
   - Check console for events
   - Verify row updates instantly

### Future Enhancements

1. **Consider HTMX 2.0 upgrade**
   - `useTemplateFragments` enabled by default
   - Better error messages
   - Improved OOB swap handling
   - See migration guide: https://htmx.org/migration-guide-htmx-1/

2. **Add automated tests**
   - Selenium tests for OOB swap behavior
   - Assert HTMX events fire
   - Verify DOM updates

3. **Apply pattern to other views**
   - Calendar event updates
   - Task board updates
   - Any other OOB table row swaps

---

## Conclusion

The OBCMS work items tree OOB swap issue is **well-understood** and **easily fixable**. The root cause is a missing `<template>` wrapper and disabled `useTemplateFragments` config in HTMX 1.9.12.

**Implementation effort:** Low (10 minutes)
**Testing effort:** Low (15 minutes)
**Risk:** Very low (config is backward compatible)
**Impact:** High (enables instant UI updates for work item tree)

The research has produced comprehensive documentation that will serve as a reference for all future HTMX OOB implementations in OBCMS.

---

## References

### Official Documentation
- [HTMX Out-of-Band Swaps](https://htmx.org/attributes/hx-swap-oob/)
- [HTMX Examples - Updating Other Content](https://htmx.org/examples/update-other-content/)

### GitHub Issues (Evidence)
- [#1198 - OOB swap not replacing `<tr>` fragments](https://github.com/bigskysoftware/htmx/issues/1198)
- [#1538 - OOB strips `<tr>` wrapping](https://github.com/bigskysoftware/htmx/issues/1538)
- [#1900 - OOB breaks with `<tbody>`](https://github.com/bigskysoftware/htmx/issues/1900)

### Community Resources
- [Django HTMX Patterns (spookylukey)](https://github.com/spookylukey/django-htmx-patterns)
- [Stack Overflow: How to swap table row with hx-swap-oob](https://stackoverflow.com/questions/66655028/)

### OBCMS Files
- View: `src/common/views/work_items.py` (lines 786-837)
- Template: `src/templates/work_items/_work_item_tree_row.html`
- Base: `src/templates/base.html` (HTMX config)

---

**Research completed by:** Claude Code (Anthropic)
**Documentation status:** Complete and production-ready
**Implementation status:** Pending (awaiting deployment)
