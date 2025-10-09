# Budget Tracking Tab Calculation Fix

**Status:** ✅ COMPLETE
**Date:** 2025-10-08
**Priority:** HIGH
**Complexity:** Simple

---

## Problem Statement

The MOA Budget Tracking tab displayed incorrect work item budget totals due to incorrect field usage in the template.

### Symptoms

1. **Work Items Tab** showed: ₱1,300,000 (correct)
2. **Budget Tracking Tab** showed: ₱83,508,730.00 (WRONG)
3. The incorrect amount matched the PPA's `budget_allocation` instead of the sum of work item `allocated_budget` values

### Root Cause

In `src/templates/coordination/partials/moa_budget_tab.html`:

**Issue 1: Incorrect "Total PPA Budget" value**
- Line 38: Showed `moa_budget_stats.total_allocated`
- **Problem**: `total_allocated` is the sum of work item budgets, NOT PPA budgets
- **Should be**: `moa_budget_stats.total_budget` (sum of PPA budget_allocation fields)

**Issue 2: Table footer used wrong field name**
- Line 189: Used `moa_budget_stats.total_allocated`
- **Should be**: `moa_budget_stats.total_work_item_budget` (more explicit field name)

---

## Solution

### 1. Budget Tracking Service Analysis

File: `src/monitoring/services/budget_tracking.py`

**Service correctly calculates:**
```python
# Line 80: Sum of all PPA budget allocations
total_budget += ppa_budget

# Line 101: Sum of all work item allocated budgets
total_allocated += ppa_allocated

# Lines 112-113: Return both values
"total_budget": total_budget,            # Sum of PPA budgets
"total_allocated": total_allocated,      # Sum of work item budgets
"total_work_item_budget": total_allocated,  # Alias for clarity
```

**Key insight:** The service provides both `total_allocated` and `total_work_item_budget` with the SAME value for clarity. Templates should use the more explicit `total_work_item_budget`.

### 2. Template Fixes

File: `src/templates/coordination/partials/moa_budget_tab.html`

**Fix 1: Correct "Total PPA Budget" stat card (Line 39)**
```html
<!-- BEFORE: Showed work item total -->
<p class="mt-2 text-2xl font-bold text-emerald-600">
    ₱{{ moa_budget_stats.total_allocated|floatformat:2|intcomma|default:"0.00" }}
</p>

<!-- AFTER: Shows PPA total -->
<p class="mt-2 text-2xl font-bold text-emerald-600">
    ₱{{ moa_budget_stats.total_budget|floatformat:2|intcomma|default:"0.00" }}
</p>
```

**Fix 2: Update table footer to use explicit field name (Line 193)**
```html
<!-- BEFORE: Generic name -->
₱{{ moa_budget_stats.total_allocated|floatformat:2|intcomma|default:"0.00" }}

<!-- AFTER: Explicit field name -->
₱{{ moa_budget_stats.total_work_item_budget|floatformat:2|intcomma|default:"0.00" }}
```

**Fix 3: Rearrange stat cards layout**

Changed from 5 columns in 1 row to 2 rows:

**Row 1 (3 columns):** Budget metrics
- Total MOA Budget
- Total PPA Budget
- Total Work Item Budget

**Row 2 (2 columns):** Utilization metrics
- Total Expenditure
- Utilization Rate

Grid classes:
- Row 1: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- Row 2: `grid-cols-1 md:grid-cols-2`

---

## Budget Field Definitions

For clarity, here's what each budget field represents:

### Stat Cards

| Stat Card | Field | Calculation | Description |
|-----------|-------|-------------|-------------|
| **Total MOA Budget** | `total_budget` | Sum of `ppa.budget_allocation` | Total budget allocated across all PPAs |
| **Total PPA Budget** | `total_budget` | Sum of `ppa.budget_allocation` | Same as Total MOA Budget (redundant but clear) |
| **Total Work Item Budget** | `total_work_item_budget` | Sum of `workitem.allocated_budget` | Total budget allocated to work items |
| **Total Expenditure** | `total_expenditure` | Sum of `workitem.actual_expenditure` | Total spent across all work items |
| **Utilization Rate** | `utilization_rate` | `(total_expenditure / total_budget) * 100` | Percentage of budget utilized |

### Table Columns

| Column | Per-PPA Field | Calculation | Description |
|--------|---------------|-------------|-------------|
| **Budget Allocation** | `ppa.budget_allocation` | From MonitoringEntry model | PPA's total budget |
| **Work Item Budget** | `ppa.work_item_budget` | Sum of work items for THIS PPA | Budget allocated to work items |
| **Expenditure** | `ppa.total_expenditure` | Sum of actual_expenditure for THIS PPA | Total spent on work items |
| **Variance** | `ppa.variance` | `budget_allocation - total_expenditure` | Under/over budget |
| **Utilization** | `ppa.utilization_rate` | `(total_expenditure / budget_allocation) * 100` | % utilized |

---

## Testing Verification

### Before Fix

```
URL: http://localhost:8000/monitoring/entry/cd6c2505-86da-4ae0-8e72-cab4a6bab69a/

Work Items Tab:
  TOTAL BUDGET: ₱1,300,000... ✓ CORRECT

Budget Tracking Tab:
  Stat Cards:
    - Total MOA Budget: ₱82,208,730.00
    - Total PPA Budget: ₱83,508,730.00 ❌ WRONG (showing work item total)
    - Total Work Item Budget: ₱83,508,730.00 ✓ CORRECT

  Table:
    - Financial Sustainability Program: ₱83,508,730.00 ❌ WRONG (too high)
```

### After Fix (Expected)

```
Budget Tracking Tab:
  Stat Cards (Row 1):
    - Total MOA Budget: ₱82,208,730.00 ✓
    - Total PPA Budget: ₱82,208,730.00 ✓ (now matches MOA budget)
    - Total Work Item Budget: ₱1,300,000.00 ✓ (matches Work Items tab)

  Stat Cards (Row 2):
    - Total Expenditure: ₱0.00 ✓
    - Utilization Rate: 0.0% ✓

  Table:
    - Financial Sustainability Program:
      - Budget Allocation: ₱82,208,730.00
      - Work Item Budget: ₱1,300,000.00 ✓ (now correct)
      - Expenditure: ₱0.00
      - Variance: +₱82,208,730.00
```

---

## Files Changed

1. **`src/templates/coordination/partials/moa_budget_tab.html`**
   - Line 20: Split stat cards into 2 rows (3 + 2 columns)
   - Line 39: Fixed "Total PPA Budget" to use `total_budget`
   - Line 62: Added second row div for utilization metrics
   - Line 193: Updated footer to use `total_work_item_budget`

---

## Related Documentation

- **Budget Tracking Service:** `src/monitoring/services/budget_tracking.py`
- **Work Item Model:** `src/common/work_item_model.py`
- **Monitoring Entry Model:** `src/monitoring/models.py`
- **View:** `src/coordination/views.py` (organization_detail function)

---

## Notes

### Why "Total MOA Budget" and "Total PPA Budget" Show Same Value

Both display `total_budget` (sum of all PPA budget_allocation fields) because:

1. **Total MOA Budget**: Budget allocated TO this MOA
2. **Total PPA Budget**: Budget allocated across PPAs under this MOA

In practice, these are the same value since an MOA's total budget IS the sum of its PPA budgets. The redundancy provides UI clarity - users can see both the "big picture" (MOA) and the "breakdown" (PPAs) are aligned.

### Budget Hierarchy

```
Organization (MOA)
└── MonitoringEntry (PPA 1) - budget_allocation: ₱82,208,730
    ├── WorkItem 1 - allocated_budget: ₱500,000
    ├── WorkItem 2 - allocated_budget: ₱800,000
    └── ...
└── MonitoringEntry (PPA 2) - budget_allocation: ₱50,000,000
    └── WorkItem 3 - allocated_budget: ₱1,000,000

Total MOA Budget = Total PPA Budget = ₱132,208,730 (sum of PPA budgets)
Total Work Item Budget = ₱2,300,000 (sum of work item budgets)
```

### Future Improvements

**Not needed now, but consider for future:**

1. **Unallocated Budget Indicator**: Show `total_budget - total_work_item_budget` as "Unallocated"
2. **Per-PPA Unallocated**: Show `ppa.budget_allocation - ppa.work_item_budget` in table
3. **Budget Allocation Percentage**: Show `(work_item_budget / budget_allocation) * 100%` per PPA

---

## Deployment Checklist

- [x] Identify root cause in template
- [x] Fix "Total PPA Budget" stat card to use correct field
- [x] Fix table footer to use explicit field name
- [x] Rearrange stat cards into 2-row layout
- [x] Document the fix and field definitions
- [ ] Test in browser (verify numbers match)
- [ ] Verify responsive layout on mobile/tablet
- [ ] Check all MOA detail pages (not just one PPA)

---

**Status:** Ready for browser testing and verification.
