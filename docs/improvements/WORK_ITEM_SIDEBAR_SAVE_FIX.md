# Work Item Sidebar Save Button Fix

**Date:** 2025-10-08
**Status:** ✅ FIXED
**Priority:** HIGH

## Problem

The "Save Changes" button on work item edit forms in the monitoring PPA detail page (`/monitoring/entry/{id}/`) was not saving changes. The same form worked correctly on the main work items page (`/oobc-management/work-items/`).

**URLs Affected:**
- ❌ BROKEN: `http://localhost:8000/monitoring/entry/{uuid}/` (monitoring PPA detail page)
- ✅ WORKING: `http://localhost:8000/oobc-management/work-items/` (work items tree page)

## Root Cause

The `work_item_sidebar_edit` view in `src/common/views/work_items.py` was using incorrect template selection logic:

```python
# OLD CODE (BROKEN)
edit_template = 'work_items/partials/sidebar_edit_form.html' if is_work_items_tree else 'common/partials/calendar_event_edit_form.html'
```

**The Problem:**
- `is_work_items_tree` checks for `'work-items' in referer`
- Monitoring page URL is `/monitoring/entry/{uuid}/`, which does NOT contain `work-items`
- Result: Monitoring page used the **calendar edit form** instead of the **work items sidebar edit form**
- Calendar edit form doesn't respect the `sidebar_target_id` parameter correctly
- Form submissions targeted wrong element ID (`sidebar-content` instead of `ppa-sidebar-content`)

## Technical Analysis

### Sidebar ID Mismatch

**Work Items Page:**
- Sidebar container: `#work-item-sidebar`
- Sidebar content: `#sidebar-content`
- Form correctly targets: `#sidebar-content`

**Monitoring PPA Page:**
- Sidebar container: `#ppa-work-item-sidebar`
- Sidebar content: `#ppa-sidebar-content`
- Form was targeting: `#sidebar-content` (WRONG!)

### Template Selection Logic

The view had logic to detect monitoring pages:

```python
is_monitoring_detail = '/monitoring/entry/' in referer
sidebar_target_id = 'ppa-sidebar-content' if is_monitoring_detail else 'sidebar-content'
```

But the template selection only checked `is_work_items_tree`:

```python
# WRONG: Doesn't check is_monitoring_detail
edit_template = 'work_items/partials/sidebar_edit_form.html' if is_work_items_tree else 'common/partials/calendar_event_edit_form.html'
```

### Why Calendar Template Failed

The calendar edit form (`common/partials/calendar_event_edit_form.html`) has hardcoded target IDs and doesn't use the `sidebar_target_id` parameter properly. The work items sidebar edit form (`work_items/partials/sidebar_edit_form.html`) correctly uses:

```django
<form hx-post="{% url 'common:work_item_sidebar_edit' pk=work_item.pk %}"
      hx-target="#{{ sidebar_target_id|default:'sidebar-content' }}"
      ...>
```

## Solution

Updated template selection logic to also check `is_monitoring_detail`:

```python
# NEW CODE (FIXED)
detail_template = 'work_items/partials/sidebar_detail.html' if (is_work_items_tree or is_monitoring_detail) else 'common/partials/calendar_event_detail.html'
edit_template = 'work_items/partials/sidebar_edit_form.html' if (is_work_items_tree or is_monitoring_detail) else 'common/partials/calendar_event_edit_form.html'
```

**Changes Made:**
- `src/common/views/work_items.py` (lines 854-855)

## Verification

**Test Steps:**
1. Navigate to monitoring PPA detail page: `/monitoring/entry/{uuid}/`
2. Switch to "Work Items" tab
3. Click "Edit" button on any work item
4. Modify dates or other fields
5. Click "Save Changes"
6. ✅ Verify: Changes save successfully
7. ✅ Verify: Success toast appears
8. ✅ Verify: Table row updates instantly (OOB swap)
9. ✅ Verify: Form stays open in sidebar

**Expected Behavior:**
- Form submission targets correct sidebar (`#ppa-sidebar-content`)
- Changes persist to database
- Table row updates via HTMX out-of-band swap
- Success toast notification displays
- Sidebar remains open with updated form

## Files Modified

```
src/common/views/work_items.py
```

## Related Files

**Templates:**
- `src/templates/work_items/partials/sidebar_edit_form.html` (correct template)
- `src/templates/common/partials/calendar_event_edit_form.html` (incorrect template for monitoring)
- `src/templates/monitoring/partials/work_items_tab.html` (monitoring page sidebar container)
- `src/templates/work_items/work_item_list.html` (work items page sidebar container)

**Views:**
- `src/common/views/work_items.py` (work_item_sidebar_edit function)

## Impact

**Before Fix:**
- Monitoring page work item edits did NOT save
- Calendar page work item edits worked (but used different template)
- Work items page edits worked perfectly

**After Fix:**
- ✅ Monitoring page work item edits save correctly
- ✅ Calendar page work item edits continue to work
- ✅ Work items page edits continue to work

## Lessons Learned

1. **Template Selection Consistency**: When adding new page contexts (like monitoring), ensure ALL template selection logic includes the new context check
2. **Sidebar Target ID Pattern**: Different pages can have different sidebar IDs - always use the `sidebar_target_id` parameter pattern
3. **HTMX Target Verification**: Verify HTMX `hx-target` attributes match actual DOM element IDs
4. **Referrer Detection**: URL-based context detection (`in referer`) works but requires maintenance when adding new pages

## Testing Recommendations

**Regression Tests Needed:**
- Work item editing on work items page (`/oobc-management/work-items/`)
- Work item editing on monitoring PPA page (`/monitoring/entry/{uuid}/`)
- Work item editing on calendar page (if applicable)
- Verify each page uses correct sidebar container ID
- Verify form submissions target correct element
- Verify OOB swap updates table rows
- Verify success/error toasts display correctly

---

**Status:** ✅ COMPLETE
**Resolution:** Template selection logic updated to include monitoring page detection
