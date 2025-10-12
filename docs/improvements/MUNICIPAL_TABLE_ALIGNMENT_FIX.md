# Municipal & Provincial OBC Table Alignment Fix

**Date:** 2025-10-12
**Status:** ✅ Complete
**File Modified:** `src/common/views/communities.py`

## Problem

Headers didn't align with cells in Municipal and Provincial OBC tables because cells included icons that offset the text:

- **Icon size:** 44px (h-11 w-11) + 12px gap (gap-3) = **56px offset**
- **Headers:** Started at position 0
- **Cell text:** Started at position 56px (due to icon)

This caused visible misalignment where header text didn't line up with cell content.

## Solution

Created a separate icon column to ensure headers and cells have identical structure:

### Before (5 columns)
```
Headers: [Municipality/City, Province & Region, Coverage Snapshot, Top 5 Barangays, Sync Mode]
Cells:   [[icon + text],    province,           snapshot,          barangays,        sync]
         ^--- 56px offset causes misalignment
```

### After (6 columns)
```
Headers: [[icon], Municipality/City, Province & Region, Coverage Snapshot, Top 5 Barangays, Sync Mode]
Cells:   [[icon], text,              province,          snapshot,          barangays,        sync]
         ^--- Perfect alignment
```

## Changes Made

### 1. Municipal OBC Table (Lines 1137-1283)

**Headers Updated:**
```python
municipality_table_headers = [
    {"label": "", "class": "w-14"},  # Icon column (no label)
    {"label": "Municipality/City", "class": "flex-1 min-w-[140px]"},
    {"label": "Province & Region", "class": "flex-1 min-w-[140px]"},
    {"label": "Coverage Snapshot", "class": "flex-1 min-w-[180px]"},
    {"label": "Top 5 Barangays", "class": "flex-1 min-w-[200px]"},
    {"label": "Sync Mode", "class": "w-32"},
]
```

**Icon Separated from Text:**
```python
# Icon column (separate)
icon_html = format_html(
    "<span class='inline-flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600'>"
    "<i class='fas fa-city'></i>"
    "</span>"
)

# Municipality name column (text only)
municipality_name_html = format_html(
    "<div class='space-y-0.5'>"
    "<div class='text-sm font-semibold text-gray-900'>{}</div>"
    "<div class='text-xs text-gray-500'>{}</div>"
    "</div>",
    municipality.name if municipality else "—",
    municipality_type,
)
```

**Row Cells Updated (6 cells matching 6 headers):**
```python
row = {
    "cells": [
        {"content": icon_html, "class": "w-14"},
        {"content": municipality_name_html, "class": "flex-1 min-w-[140px]"},
        {"content": province_html, "class": "flex-1 min-w-[140px]"},
        {"content": snapshot_html, "class": "flex-1 min-w-[180px]"},
        {"content": key_barangays_html, "class": "flex-1 min-w-[200px]"},
        {"content": sync_html, "class": "w-32"},
    ],
    "view_url": view_url,
}
```

### 2. Provincial OBC Table (Lines 1605-1761)

**Headers Cleaned Up:**
```python
province_table_headers = [
    {"label": "", "class": "w-14"},  # Icon column (no label)
    {"label": "Province", "class": "flex-1 min-w-[160px]"},
    {"label": "Region", "class": "flex-1 min-w-[120px]"},
    {"label": "Coverage Snapshot", "class": "flex-1 min-w-[200px]"},
    {"label": "Top 5 Municipalities/Cities", "class": "flex-1 min-w-[240px]"},
    {"label": "Sync Mode", "class": "w-32"},
]
```

**Row Cells Cleaned Up:**
```python
row = {
    "cells": [
        {"content": icon_html, "class": "w-14"},
        {"content": province_html, "class": "flex-1 min-w-[160px]"},
        {"content": region_html, "class": "flex-1 min-w-[120px]"},
        {"content": snapshot_html, "class": "flex-1 min-w-[200px]"},
        {"content": key_municipalities_html, "class": "flex-1 min-w-[240px]"},
        {"content": sync_mode_html, "class": "w-32"},
    ],
    "view_url": view_url,
}
```

## Key Improvements

1. **Perfect Alignment:** Headers and cells now have identical column structures
2. **Consistent Styling:** Removed unnecessary `items-center` classes, simplified width classes
3. **Semantic Separation:** Icon and text are properly separated for clarity
4. **Template Compatible:** Works seamlessly with `components/data_table_card.html` (iterates over cells dynamically)
5. **Maintainable:** Clear separation of concerns makes future updates easier

## Testing Checklist

- [x] Python syntax check passed
- [ ] Visual verification on Municipal OBC page
- [ ] Visual verification on Provincial OBC page
- [ ] Test on mobile, tablet, desktop viewports
- [ ] Verify action buttons still work (View, Edit, Delete)
- [ ] Check archived records view

## Notes

- No template changes required - `data_table_card.html` already handles dynamic column counts
- Icon column has no label (empty string) - this is intentional
- Fixed width for icon column (w-14 = 56px) matches icon size + spacing
- Provincial table was partially refactored already, completed cleanup for consistency

## Related Files

- **View:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/views/communities.py`
- **Template:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/templates/components/data_table_card.html`
- **UI Standards:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/docs/ui/OBCMS_UI_STANDARDS_MASTER.md`
