# Phase 0: Communities Views URL Reference Fix

**Status**: ✅ COMPLETE  
**Date**: 2025-10-13  
**File**: `src/common/views/communities.py`

## Problem

13 remaining `reverse("common:communities_*")` references were found in the communities views file after the initial migration. These needed to be updated to use the correct `communities:` namespace.

## Solution

Used sed to efficiently replace all occurrences:

```bash
sed -i '' 's/reverse("common:communities_/reverse("communities:communities_/g' src/common/views/communities.py
```

## Changes Made

### Total Replacements: 13

All instances changed from `reverse("common:communities_*")` to `reverse("communities:communities_*")`

**Updated Lines:**
- Line 819: `reverse("communities:communities_add")`
- Line 827: `reverse("communities:communities_manage_municipal")`
- Line 1077: `reverse("communities:communities_manage_municipal")`
- Line 1091: `reverse("communities:communities_add_municipality")`
- Line 1099: `reverse("communities:communities_manage_provincial")`
- Line 1238: `reverse("communities:communities_view_municipal", args=[coverage.pk])`
- Line 1515: `reverse("communities:communities_manage_provincial")`
- Line 1529: `reverse("communities:communities_add_province")`
- Line 1537: `reverse("communities:communities_manage_municipal")`
- Line 1766: `reverse("communities:communities_add_province")`
- Line 1828: `reverse("communities:communities_manage")`
- Line 1932: `reverse("communities:communities_manage_municipal")`
- Line 2049: `reverse("communities:communities_manage_provincial")`

## Verification

### 1. No Legacy References Remaining
```bash
grep -n 'reverse("common:communities' src/common/views/communities.py
# Result: No matches (0 results)
```

### 2. All References Updated
```bash
grep -n 'reverse("communities:communities' src/common/views/communities.py | wc -l
# Result: 15 total references (13 fixed + 2 previously correct)
```

### 3. Django Check Passed
```bash
python manage.py check
# Result: System check identified no issues (0 silenced)
```

## Current State

**File**: `src/common/views/communities.py`
- ✅ 0 legacy `common:communities_*` references
- ✅ 15 correct `communities:communities_*` references
- ✅ Django check passes with no errors
- ✅ Ready for testing

## Related Files

This fix completes the communities URL migration started in:
- `docs/improvements/PHASE_0_4_COMMUNITIES_URL_MIGRATION_COMPLETE.md`

## Next Steps

1. Test all communities views to ensure URLs resolve correctly
2. Verify redirect functionality in forms and HTMX responses
3. Check accessibility of all communities pages
4. Update any remaining documentation references

---

**Pattern Used**: `reverse("common:communities_*")` → `reverse("communities:communities_*")`  
**Method**: sed bulk replacement with verification  
**Impact**: All communities views now use correct namespace
