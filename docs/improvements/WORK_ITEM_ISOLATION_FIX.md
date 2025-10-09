# Work Item Isolation Fix

**Status:** ✅ Completed
**Date:** 2025-10-08
**Priority:** CRITICAL
**Category:** Bug Fix - Data Isolation

## Problem Statement

PPA-specific work items were appearing in the general OOBC work items page and calendar, violating the MOA/OOBC data isolation principle.

### Affected URLs
- `/oobc-management/work-items/` - General OOBC work items list
- `/oobc-management/calendar/` - General OOBC calendar

### Root Cause

The `work_item_list` view and `work_item_calendar_feed` view in `src/common/views/work_items.py` were not filtering out PPA-specific work items.

Work items are considered PPA-specific when ANY of these fields are populated:
- `related_ppa` - ForeignKey to MonitoringEntry (PPA)
- `ppa_category` - CharField ('moa_ppa', 'oobc_ppa', 'obc_request')
- `implementing_moa` - ForeignKey to Organization (for MOA-specific PPAs)

## Solution

### Files Modified

1. **`src/common/views/work_items.py`**
   - `work_item_list()` - Added isolation filter (lines 194-198)
   - `work_item_calendar_feed()` - Added isolation filter (lines 775-781)

### Code Changes

#### work_item_list View

**Before Fix:**
```python
# CRITICAL: Filter to show ONLY root items initially
# Children are loaded on-demand via HTMX when user expands
queryset = queryset.filter(level=0)
```

**After Fix:**
```python
# CRITICAL: Filter to show ONLY root items initially
# Children are loaded on-demand via HTMX when user expands
queryset = queryset.filter(level=0)

# CRITICAL: Exclude PPA-specific work items from general OOBC list
# PPA work items should only appear in PPA/MOA contexts
# Work items are PPA-specific if ANY of these fields are populated:
# - related_ppa: Linked to a specific PPA
# - ppa_category: Has a PPA category (moa_ppa, oobc_ppa, obc_request)
# - implementing_moa: Linked to a specific MOA organization
queryset = queryset.filter(
    related_ppa__isnull=True,      # Exclude items linked to a PPA
    ppa_category__isnull=True,     # Exclude items with PPA category
    implementing_moa__isnull=True  # Exclude items with MOA
)
```

#### work_item_calendar_feed View

**Before Fix:**
```python
# Filter work items
queryset = WorkItem.objects.filter(is_calendar_visible=True)
```

**After Fix:**
```python
# Filter work items - ONLY general OOBC work items (no PPA-specific items)
queryset = WorkItem.objects.filter(
    is_calendar_visible=True,
    # Exclude PPA-specific work items from general OOBC calendar
    related_ppa__isnull=True,
    ppa_category__isnull=True,
    implementing_moa__isnull=True
)
```

## Impact Analysis

### Before Fix (Bug State)

**Work Items List:**
- Total items shown: **10** (5 general + 5 PPA-specific)
- PPA items incorrectly visible: **5**
- Example problematic items:
  - "Sample Promotions" (linked to Promotional and Investment Services PPA)
  - "BAGO Legal Services - Execution Plan" (linked to BAGO Legal Services PPA)
  - "MOA Investment Forum - Final Test" (linked to Promotional and Investment Services PPA)

**Calendar Feed:**
- Total items shown: **15** (8 general + 7 PPA-specific)
- PPA items incorrectly visible: **7**

### After Fix (Correct State)

**Work Items List:**
- Total items shown: **5** (general OOBC only)
- PPA items visible: **0** ✅
- Only shows items where `related_ppa`, `ppa_category`, and `implementing_moa` are ALL NULL

**Calendar Feed:**
- Total items shown: **8** (general OOBC only)
- PPA items visible: **0** ✅
- Filtered out 7 PPA-specific items correctly

## Testing

### Backend Test

Created `src/scripts/test_work_item_isolation.py` to verify the fix.

**Run Test:**
```bash
cd src
python scripts/test_work_item_isolation.py
```

**Expected Output:**
```
✅ ISOLATION FIXED: No PPA-specific items appear in general list!
   Filtered out 5 PPA-specific items correctly

✅ CALENDAR ISOLATION FIXED: No PPA-specific items in general calendar!
   Filtered out 7 PPA-specific items correctly

Overall Status: ✅ ALL TESTS PASSED
```

### Browser Testing

See `.claude/agents/test-work-item-isolation.md` for comprehensive browser test scenarios.

**Key Test Cases:**
1. ✅ General work items page shows only 5 items (down from 10)
2. ✅ PPA-specific items like "Sample Promotions" don't appear in general list
3. ✅ General items like "Draeganess" still appear correctly
4. ✅ PPA work items still appear in PPA detail pages (e.g., `/monitoring/entry/...`)
5. ✅ Calendar feed returns only 8 items (down from 15)

## Data Isolation Principle

### General OOBC Work Items
**Criteria:** ALL isolation fields must be NULL
- `related_ppa IS NULL`
- `ppa_category IS NULL`
- `implementing_moa IS NULL`

**Visible In:**
- `/oobc-management/work-items/` ✅
- `/oobc-management/calendar/` ✅
- Staff profiles and dashboards ✅

**NOT Visible In:**
- PPA detail pages (`/monitoring/entry/.../`)
- MOA profile pages (`/coordination/organization/.../`)

### PPA-Specific Work Items
**Criteria:** ANY isolation field is populated
- `related_ppa IS NOT NULL` OR
- `ppa_category IS NOT NULL` OR
- `implementing_moa IS NOT NULL`

**Visible In:**
- PPA detail pages (`/monitoring/entry/.../`) ✅
- MOA profile pages (if `implementing_moa` set) ✅
- PPA-specific calendars ✅

**NOT Visible In:**
- `/oobc-management/work-items/` ✅ (FIX APPLIED)
- `/oobc-management/calendar/` ✅ (FIX APPLIED)

## Related Work

### Isolation Fields Implementation
- Migration: `0029_add_work_item_isolation_fields.py`
- Data Migration: `0030_backfill_work_item_isolation_data.py`
- Model: `src/common/work_item_model.py` (lines 258-279)

### Automatic Population Logic
When work items are created or updated, the `populate_isolation_fields()` method automatically sets:
- `ppa_category` from related PPA's category
- `implementing_moa` from related PPA's implementing MOA

**See:** `src/common/work_item_model.py` lines 626-654

### Other Views Using Isolation
Already correctly implemented in:
- `work_item_edit()` - Filters related items by same category (lines 458-468)
- `work_item_search_related()` - Enforces MOA/OOBC isolation (lines 1189-1198)

## Performance Considerations

### Database Indexes
Isolation fields have database indexes for efficient filtering:
```python
indexes = [
    models.Index(fields=["related_ppa"], name="wi_rel_ppa_idx"),
    models.Index(fields=["ppa_category"], name="wi_ppa_category_idx"),
    models.Index(fields=["implementing_moa"], name="wi_implementing_moa_idx"),
    models.Index(fields=["ppa_category", "implementing_moa"], name="wi_moa_filter_idx"),
]
```

### Query Performance
- **Before Fix:** Full table scan of all work items
- **After Fix:** Index-optimized query using NULL checks
- **Performance Impact:** Minimal (indexes make NULL checks fast)

## Edge Cases Handled

### Work Items Created Before Migration
- If created before isolation fields existed, all three fields will be NULL
- These are treated as general OOBC work items ✅

### Work Items Created in Admin Panel
- If manually created without setting isolation fields, all three will be NULL
- These are treated as general OOBC work items ✅

### Work Items with Parent but No Isolation
- Child work items inherit isolation from parent
- General OOBC hierarchy: All have NULL isolation fields ✅

### Work Items Manually Linked to PPA
- If `related_ppa` is set, `populate_isolation_fields()` auto-fills category and MOA
- These are correctly excluded from general views ✅

## Future Enhancements

### Considered but Not Implemented
1. **Soft Delete for PPA Items** - Not needed; database constraints handle this
2. **Separate Models** - Current unified model works well with isolation fields
3. **Permission-Based Filtering** - Current approach is simpler and more performant

### Monitoring
- Monitor query performance in production
- Track isolation field population success rate
- Alert if general views show unexpected PPA items

## Deployment Notes

### Production Checklist
- [x] Code changes applied
- [x] Backend tests passing
- [x] Browser tests completed
- [ ] Deploy to staging
- [ ] Verify in staging environment
- [ ] Deploy to production

### Rollback Plan
If issues arise, revert commits:
```bash
git revert <commit-hash>
```

No database changes required - isolation fields already exist and populated.

## References

- **Issue:** PPA work items appearing in general OOBC pages
- **Design Doc:** `docs/improvements/MOA_OOBC_SEPARATION_ANALYSIS.md`
- **Test Script:** `src/scripts/test_work_item_isolation.py`
- **Test Guide:** `.claude/agents/test-work-item-isolation.md`
- **Model Documentation:** `src/common/work_item_model.py` (MOA/OOBC Isolation section)

## Conclusion

✅ **Fix Applied:** PPA-specific work items are now properly isolated from general OOBC views.

**Impact:**
- Improved data isolation between MOA and OOBC contexts
- Cleaner general OOBC work items list (5 items instead of 10)
- Cleaner general OOBC calendar (8 items instead of 15)
- No impact on PPA-specific views (work items still visible in correct contexts)

**Test Results:** ✅ ALL TESTS PASSED
