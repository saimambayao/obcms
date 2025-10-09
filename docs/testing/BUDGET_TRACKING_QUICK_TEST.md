# Budget Tracking - Quick Test Reference

**URL:** `http://localhost:8000/oobc-management/work-items/afcadb19-8b75-4ee9-b4c5-7ccd5150f4a2/edit/`

---

## 🚀 5-Minute Quick Test

### Prerequisites
1. Server running: `cd src && ./manage.py runserver`
2. Browser: Open DevTools Console (F12)
3. Navigate to edit page (URL above)

---

## Test Matrix

| # | Allocated | Expenditure | Expected Variance | Color | Bar % | Status Text |
|---|-----------|-------------|-------------------|-------|-------|-------------|
| 1 | 100000 | 50000 | ₱50,000.00 | 🟢 Green | 50% | 50.0% utilized - Within budget |
| 2 | 100000 | 96000 | ₱4,000.00 | 🟡 Amber | 96% | 96.0% utilized - Near budget limit |
| 3 | 100000 | 120000 | ₱20,000.00 | 🔴 Red | 100% | Over budget by ₱20,000.00 |
| 4 | 0 | 0 | ₱0.00 | ⚪ Gray | 0% | No budget allocated |
| 5 | 100000 | 100000 | ₱0.00 | 🟡 Amber | 100% | 100.0% utilized - Near budget limit |

---

## Quick Validation Checklist

### ✅ Visual Elements
- [ ] Section appears between "Status & Priority" and "Schedule & Timeline"
- [ ] Wallet icon (💰) is emerald color
- [ ] ₱ peso sign appears before both input fields
- [ ] Variance display card shows with progress bar

### ✅ Real-Time Calculation
- [ ] Typing in allocated budget updates variance **instantly**
- [ ] Typing in expenditure updates variance **instantly**
- [ ] No page reload required

### ✅ Color Coding
- [ ] Green (0-94% utilization)
- [ ] Amber (95-100% utilization)
- [ ] Red (>100% utilization)

### ✅ Progress Bar
- [ ] Width matches percentage
- [ ] Capped at 100% (never exceeds)
- [ ] Smooth transition (300ms)

### ✅ Form Persistence
- [ ] Click "Save Work Item"
- [ ] Navigate away and return
- [ ] Values restored correctly
- [ ] Variance recalculates on load

### ✅ Console Check
- [ ] No JavaScript errors
- [ ] `calculateBudgetVariance()` executes

---

## Color Reference

| State | Display Color | Bar Color | Text Color |
|-------|---------------|-----------|------------|
| Under Budget | `text-emerald-600` | `bg-emerald-500` | `text-emerald-600` |
| Near Limit | `text-amber-600` | `bg-amber-500` | `text-amber-600` |
| Over Budget | `text-red-600` | `bg-red-500` | `text-red-600` |
| No Budget | `text-gray-900` | `bg-gray-200` | `text-gray-500` |

---

## Pass/Fail Criteria

### ✅ PASS
- All 5 test scenarios work correctly
- Real-time updates function
- Colors match expected values
- No JavaScript errors in console
- Form values persist after save

### ❌ FAIL
- Any JavaScript errors
- Variance not updating in real-time
- Incorrect color coding
- Progress bar exceeds 100%
- Values lost after form submission

---

## Quick Test Commands

```bash
# Start Server
cd src && ./manage.py runserver

# Open Browser
open http://localhost:8000/oobc-management/work-items/afcadb19-8b75-4ee9-b4c5-7ccd5150f4a2/edit/

# Django Shell - Verify Database
cd src
./manage.py shell
>>> from common.work_item_model import WorkItem
>>> item = WorkItem.objects.get(pk='afcadb19-8b75-4ee9-b4c5-7ccd5150f4a2')
>>> print(f"Allocated: {item.allocated_budget}, Expenditure: {item.actual_expenditure}")
```

---

## Expected Function Behavior

```javascript
// Function: calculateBudgetVariance()
// Location: work_item_form.html, lines 1070-1118

// Input: allocated_budget, actual_expenditure
// Output: Updates DOM elements with variance display

// Example:
// allocated = 100000
// expenditure = 50000
// variance = 100000 - 50000 = 50000
// percentage = (50000 / 100000) * 100 = 50.0%
// Result: Green, ₱50,000.00, 50% bar, "50.0% utilized - Within budget"
```

---

## Responsive Breakpoints

| Viewport | Expected Layout |
|----------|-----------------|
| < 768px (Mobile) | Single column, stacked inputs |
| ≥ 768px (Desktop) | Two columns, side-by-side inputs |

---

## Known Good State

After testing, the page should look like this when loaded:

```
Budget Tracking Section:
✅ Positioned correctly (between Status/Priority and Schedule)
✅ Wallet icon emerald color
✅ ₱ prefix on both inputs
✅ Variance display with progress bar
✅ Initial state: ₱0.00, gray color, 0% bar
✅ Real-time updates on input
✅ Color coding: green → amber → red
✅ Form persistence works
✅ No console errors
```

---

**Test Duration:** ~5 minutes
**Expected Result:** ✅ ALL TESTS PASS
**Status:** 📋 READY FOR TESTING
