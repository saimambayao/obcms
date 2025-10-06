# HTMX Version Compatibility for OBCMS

**Date:** 2025-10-06
**Current HTMX Version:** 1.9.12
**Location:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/static/vendor/htmx/htmx.min.js`

---

## Current Configuration

### HTMX Version
- **Installed:** 1.9.12 (local + CDN fallback to unpkg.com)
- **Template location:** `src/templates/base.html` (line 654)

### Config Settings
```javascript
htmx.config = {
    // ... other settings ...
    useTemplateFragments: false,  // DEFAULT in HTMX 1.9.x
    // ... other settings ...
}
```

---

## Template Fragment Support

### What is `useTemplateFragments`?

When enabled, HTMX will look for `<template>` tags in responses and extract their content. This is critical for handling HTML elements that can't exist standalone (like `<tr>`, `<td>`, `<li>`).

### Version History

| HTMX Version | `useTemplateFragments` Default | Notes |
|--------------|-------------------------------|-------|
| 1.9.x | `false` | Must enable manually |
| 2.0+ | `true` | Enabled by default |

### Current Status in OBCMS

**HTMX 1.9.12:** `useTemplateFragments` is **NOT enabled** by default.

To use `<template>` wrapper for OOB swaps, you must either:

1. **Option A: Enable the config setting** (Recommended)
2. **Option B: Upgrade to HTMX 2.0+** (Alternative)

---

## Recommended Solution for OBCMS

### Option 1: Enable `useTemplateFragments` in HTMX 1.9.12

**File:** `src/templates/base.html`

**Add after HTMX script loads:**

```html
<!-- HTMX Core -->
<script src="{% static 'vendor/htmx/htmx.min.js' %}" defer></script>

<!-- HTMX Configuration -->
<script>
    // Enable template fragment support for OOB table row swaps
    document.addEventListener('DOMContentLoaded', function() {
        htmx.config.useTemplateFragments = true;
    });
</script>
```

**Then in view (work_items.py):**

```python
# Wrap table row in <template>
row_html_wrapped = f'<template>{row_html_with_oob}</template>'
combined_html = edit_form_html + '\n' + row_html_wrapped
```

### Option 2: Alternative Approach (No Config Change)

If you don't want to enable `useTemplateFragments`, use a different approach:

**Django View:**
```python
# Instead of wrapping in <template>, wrap in a valid container
# that will be stripped anyway (for non-outerHTML swaps)

# For table rows, temporarily wrap in <tbody>
row_html_wrapped = f'<tbody style="display:contents;">{row_html_with_oob}</tbody>'
combined_html = edit_form_html + '\n' + row_html_wrapped
```

**HTML in row template:**
```html
<!-- Change ID from <tr> to <tbody> -->
<tbody id="work-item-row-{{ work_item.id }}">
    <tr data-work-item-id="{{ work_item.id }}">
        <!-- row content -->
    </tr>
</tbody>
```

**Trade-offs:**
- ❌ Requires template changes (all tree row templates)
- ❌ Changes the DOM structure (additional `<tbody>` wrapper)
- ✅ No HTMX config changes needed
- ✅ Works immediately with current HTMX 1.9.12

### Recommended: Option 1 (Enable useTemplateFragments)

**Why?**
- Cleaner implementation
- No template restructuring needed
- Matches modern HTMX 2.0 behavior
- Easier to upgrade to HTMX 2.0 later
- One-line config change vs multiple template changes

---

## Implementation Plan

### Step 1: Enable `useTemplateFragments`

Edit `src/templates/base.html`:

```html
<!-- Around line 654-660 -->
<script src="{% static 'vendor/htmx/htmx.min.js' %}" defer></script>

<!-- ADD THIS AFTER HTMX LOADS -->
<script>
    // Configure HTMX for OOB table row swaps
    // This enables <template> wrapper support needed for <tr> elements
    document.addEventListener('DOMContentLoaded', function() {
        htmx.config.useTemplateFragments = true;
        console.log('HTMX config.useTemplateFragments enabled');
    });
</script>
```

### Step 2: Update Django View

Edit `src/common/views/work_items.py` (around line 824):

```python
# BEFORE:
combined_html = edit_form_html + '\n' + row_html_with_oob

# AFTER:
row_html_wrapped = f'<template>{row_html_with_oob}</template>'
combined_html = edit_form_html + '\n' + row_html_wrapped
```

### Step 3: Test

1. Edit a work item in the tree view
2. Open browser developer console
3. Check for:
   - Console message: "HTMX config.useTemplateFragments enabled"
   - HTMX events: `htmx:oobBeforeSwap`, `htmx:oobAfterSwap`
   - Tree row updates instantly without page reload

---

## Future Upgrade Path

### HTMX 2.0 Upgrade

When ready to upgrade to HTMX 2.0:

1. **Download HTMX 2.0:**
   ```bash
   cd src/static/vendor/htmx/
   curl -o htmx.min.js https://unpkg.com/htmx.org@2.0.0/dist/htmx.min.js
   ```

2. **Update CDN fallback in base.html:**
   ```html
   fallback.src = 'https://unpkg.com/htmx.org@2.0.0';
   ```

3. **Remove manual config (optional):**
   ```javascript
   // Can remove this line since it's default in 2.0
   htmx.config.useTemplateFragments = true;
   ```

4. **Test thoroughly:**
   - All HTMX interactions
   - OOB swaps
   - Form submissions
   - Calendar interactions
   - Work item tree

### Breaking Changes to Watch

HTMX 2.0 has some breaking changes from 1.9.x:

- Changed default swap timing
- Some event names changed
- `hx-on` attribute syntax changes
- WebSocket extension moved to separate file

**Reference:** https://htmx.org/migration-guide-htmx-1/

---

## Testing Checklist

After enabling `useTemplateFragments`:

- [ ] Console shows config enabled message
- [ ] Edit work item in tree view
- [ ] Sidebar shows edit form
- [ ] Tree row updates instantly (no page reload)
- [ ] Progress bar updates correctly
- [ ] Status badge updates correctly
- [ ] No console errors
- [ ] HTMX events fire: `htmx:oobBeforeSwap`, `htmx:oobAfterSwap`
- [ ] Works in Chrome, Firefox, Safari
- [ ] Mobile view works correctly

---

## Debugging

### Enable HTMX Logging

Add to base.html for debugging:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    htmx.config.useTemplateFragments = true;

    // Enable full HTMX logging (remove in production)
    htmx.logAll();

    // Listen for OOB swap events
    document.body.addEventListener('htmx:oobBeforeSwap', function(e) {
        console.log('OOB Before Swap:', e.detail);
    });

    document.body.addEventListener('htmx:oobAfterSwap', function(e) {
        console.log('OOB After Swap:', e.detail);
    });
});
```

### Check if Template Fragments are Working

```javascript
// In browser console
console.log(htmx.config.useTemplateFragments);  // Should be true

// After an edit operation, check the response
// (in Network tab, look for the HTMX request)
// Response should contain <template><tr>...</tr></template>
```

---

## Conclusion

**Current State:**
- HTMX 1.9.12 installed
- `useTemplateFragments` NOT enabled (default: false)
- OOB table row swaps will fail without proper configuration

**Recommended Fix:**
1. Enable `htmx.config.useTemplateFragments = true` in base.html
2. Wrap OOB `<tr>` elements in `<template>` tags in view
3. Test thoroughly

**Effort:** Low (5 minutes implementation, 15 minutes testing)
**Risk:** Very low (config change is backward compatible)
**Impact:** High (fixes instant UI updates for work item tree)

---

## Related Documentation

- [HTMX OOB Swap Implementation Guide](./HTMX_OOB_SWAP_IMPLEMENTATION_GUIDE.md)
- [HTMX OOB Quick Reference](./HTMX_OOB_QUICK_REFERENCE.md)
- [HTMX Official Documentation](https://htmx.org/attributes/hx-swap-oob/)
- [HTMX 2.0 Migration Guide](https://htmx.org/migration-guide-htmx-1/)
