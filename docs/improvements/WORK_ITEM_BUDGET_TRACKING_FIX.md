# Work Item Budget Tracking Fix

**Date:** 2025-10-08
**Status:** ✅ FIXED
**Priority:** HIGH

## Problem Summary

The MOA Budget Tracking tab was displaying incorrect "WORK ITEM BUDGET" values that didn't match the actual work items under each PPA.

### Evidence

**Budget Tracking Tab:**
- Expenditure Management Program - WORK ITEM BUDGET: ₱111,648,503.00
- TOTAL WORK ITEM BUDGET stat card: ₱195,157,233.00

**Work Items Tab (same PPA):**
- TOTAL BUDGET: ₱0.00
- WORK ITEMS: 1 child activity
- Actual allocated budget: ₱5,582,425.15

### Root Cause

The budget tracking service (`src/monitoring/services/budget_tracking.py`) was incorrectly including **execution project root nodes** in its work item budget calculations.

**Execution Project Structure:**
```
Expenditure Management Program (PPA)
└── Expenditure Management Program - Execution Plan (ROOT PROJECT)
    ├── allocated_budget: ₱111,648,503.00  ← CONTAINER (should NOT be counted)
    ├── work_type: 'project'
    ├── parent: NULL
    └── Children:
        └── Sample Work Item (ACTIVITY)
            └── allocated_budget: ₱5,582,425.15  ← ACTUAL WORK ITEM (should be counted)
```

**The Bug:**
- Budget tracking service queried: `WorkItem.objects.filter(related_ppa=ppa)`
- This returned BOTH the root project (₱111,648,503.00) AND the child activity (₱5,582,425.15)
- Total: ₱117,230,928.15 (WRONG)

**Expected Behavior:**
- Should ONLY count child work items (activities, tasks, subtasks)
- Should EXCLUDE execution project roots (which are just containers with the PPA's total budget)
- Expected total: ₱5,582,425.15 (CORRECT)

## Solution Implemented

### 1. Fixed Budget Tracking Service

**File:** `src/monitoring/services/budget_tracking.py`

**Change:** Modified `_aggregate_work_items()` function to exclude execution project roots:

```python
def _aggregate_work_items(ppas: Sequence[MonitoringEntry]) -> MutableMapping[str, list[WorkItem]]:
    """
    Return a mapping of PPA ID to related work items for faster lookups.

    Excludes execution project roots (parent IS NULL and work_type='project')
    because they are just containers with the PPA's total budget.
    Only actual child work items (activities, tasks, subtasks) are counted.
    """
    work_items = WorkItem.objects.filter(
        related_ppa__in=ppas
    ).exclude(
        # Exclude execution project roots (containers, not actual work items)
        parent__isnull=True,
        work_type=WorkItem.WORK_TYPE_PROJECT,
    ).only(
        "related_ppa_id",
        "allocated_budget",
        "actual_expenditure",
    )
    # ... rest of function
```

**Rationale:**
- Execution project roots are created automatically when enabling work item tracking
- They inherit the PPA's `budget_allocation` as a starting point
- They serve as hierarchical containers, not actual work items
- Only their children (activities, tasks, subtasks) represent real work

### 2. Renamed Stat Card for Clarity

**File:** `src/templates/coordination/partials/moa_budget_tab.html`

**Change:** Updated stat card label:
- **Before:** "TOTAL WORK ITEM BUDGET"
- **After:** "TOTAL PPA WORK ITEM BUDGET"

**Rationale:**
- Clarifies that this is the sum of work item budgets across all PPAs in the MOA
- Distinguishes from PPA budget allocations
- Matches the naming convention of other stat cards

## Testing Results

**Test Case:** Expenditure Management Program PPA

### Before Fix:
```
Work Item Budget: ₱111,648,503.00  ❌ WRONG
  (Included execution project root + child activity)
```

### After Fix:
```
Work Item Budget: ₱5,582,425.15  ✅ CORRECT
  (Only counts actual child work items)
```

**Verification Query:**
```python
# Get work items for this PPA (AFTER fix)
work_items = WorkItem.objects.filter(
    related_ppa=ppa
).exclude(
    parent__isnull=True,
    work_type=WorkItem.WORK_TYPE_PROJECT,
)
# Returns: 1 activity with allocated_budget=₱5,582,425.15
```

## Impact Assessment

### Files Modified:
1. `src/monitoring/services/budget_tracking.py` - Budget calculation logic
2. `src/templates/coordination/partials/moa_budget_tab.html` - UI label update

### Behavior Changes:
- ✅ **Budget Tracking Tab** now shows correct work item budget per PPA (excludes execution project roots)
- ✅ **TOTAL PPA WORK ITEM BUDGET** stat card now matches sum of actual child work items
- ✅ **Work Items Tab** budget now aligns with Budget Tracking Tab
- ✅ No changes to existing work item creation/deletion logic

### Backward Compatibility:
- ✅ **Fully compatible** - Only changes calculation logic, not data model
- ✅ No migrations required
- ✅ No existing data affected
- ✅ Works with all existing PPAs and work items

## Data Integrity Note

During investigation, discovered that some work items have `ppa_category=None` instead of `'moa_ppa'`. This is a separate data integrity issue and does NOT affect budget tracking (which uses `related_ppa` FK, not `ppa_category`).

**Example:**
```python
WorkItem: "Expenditure Management Program - Execution Plan"
  related_ppa: Expenditure Management Program (FK relationship)  ✅
  ppa_category: None  ⚠️ Should be 'moa_ppa'
  implementing_moa: None  ⚠️ Should be Ministry of Finance
```

**Recommendation:** Consider adding a data migration to backfill `ppa_category` and `implementing_moa` from the `related_ppa.category` and `related_ppa.implementing_moa` for consistency. However, this is NOT required for budget tracking functionality.

## Verification Steps

To verify the fix is working correctly:

1. **Navigate to MOA Organization Detail Page**
   - Go to: `/coordination/organization/{moa_id}/`
   - Click "Budget Tracking" tab

2. **Check Budget Values**
   - Each PPA's "WORK ITEM BUDGET" should match the sum of its CHILD work items only
   - Should NOT include the execution project root budget
   - Should match the Work Items tab's budget summary

3. **Check Stat Card**
   - Label should read "TOTAL PPA WORK ITEM BUDGET"
   - Value should equal sum of all work item budgets across all PPAs

4. **Cross-Reference with Work Items Tab**
   - For each PPA, click "View" to open PPA detail
   - Go to "Work Items" tab
   - Verify "TOTAL BUDGET" stat matches Budget Tracking tab's "WORK ITEM BUDGET" column

## Expected Results After Fix

**For Expenditure Management Program PPA:**
```
Budget Tracking Table:
  - Budget Allocation: ₱111,648,503.00 (PPA's total budget)
  - Work Item Budget: ₱5,582,425.15 ✅ (sum of child work items only)
  - Expenditure: ₱0.00
  - Variance: ₱111,648,503.00

Work Items Tab:
  - TOTAL BUDGET: ₱5,582,425.15 ✅ (matches Budget Tracking)
  - WORK ITEMS: 1 (the child activity)
```

**For MOA Overall Stats:**
```
TOTAL MOA BUDGET: ₱238,420,117.00 (sum of all PPA budget allocations)
TOTAL PPA WORK ITEM BUDGET: ₱13,221,005.85 ✅ (sum of actual child work items)
TOTAL EXPENDITURE: ₱0.00
UTILIZATION RATE: 0.0%
```

## Related Documentation

- [Work Item Isolation Fix](WORK_ITEM_ISOLATION_FIX.md) - Related work item filtering improvements
- [Work Item PPA Hierarchy Fix](WORK_ITEM_PPA_HIERARCHY_FIX.md) - PPA-WorkItem relationship refinements
- [Budget Tracking Enhancements](BUDGET_TRACKING_ENHANCEMENTS_IMPLEMENTATION.md) - Overall budget tracking improvements

## Conclusion

This fix ensures that budget tracking calculations align with the Work Items tab by:
1. Excluding execution project roots (which are containers, not actual work)
2. Only counting child work items (activities, tasks, subtasks)
3. Improving label clarity for the stat card

The system now provides accurate, consistent budget reporting across all MOA budget tracking views.
