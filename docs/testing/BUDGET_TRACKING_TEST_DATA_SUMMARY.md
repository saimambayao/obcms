# Budget Tracking Test Data Summary

**Date**: 2025-10-08
**Status**: ✅ Complete
**Purpose**: Create comprehensive sample work items to test budget tracking functionality

---

## Overview

Successfully created **9 work items** across **3 PPAs** demonstrating all three budget status scenarios:
- 🟢 **GREEN**: Under budget (60% utilization)
- 🟡 **AMBER**: Near budget limit (97% utilization)
- 🔴 **RED**: Over budget (105% utilization)

This test data enables verification of:
- Budget variance calculations
- Status color indicators (green/amber/red)
- Budget aggregation per PPA
- Work item budget tracking displays

---

## Test Data Created

### 1. School-Based Management and Operation
**PPA Budget**: ₱24,904,909,955.00
**Implementing MOA**: Ministry of Basic, Higher, and Technical Education

| Component | Type | Allocated | Spent | Variance | Status |
|-----------|------|-----------|-------|----------|--------|
| Infrastructure Component | Activity | ₱8,301,636,651.67 | ₱4,980,981,991.00 | -40.00% | 🟢 GREEN |
| Capacity Building Component | Activity | ₱8,301,636,651.67 | ₱8,052,587,552.12 | -3.00% | 🟡 AMBER |
| Equipment Component | Task | ₱8,301,636,651.67 | ₱8,716,718,484.25 | +5.00% | 🔴 RED |

**PPA Totals**:
- Total Allocated: ₱24,904,909,955.00
- Total Spent: ₱21,750,288,027.37
- Overall Variance: ₱-3,154,621,927.63 (-12.67%)
- ✅ Work item budgets match PPA budget exactly

---

### 2. Road and Bridge Development Program
**PPA Budget**: ₱6,028,570,000.00
**Implementing MOA**: Ministry of Public Works

| Component | Type | Allocated | Spent | Variance | Status |
|-----------|------|-----------|-------|----------|--------|
| Infrastructure Component | Activity | ₱2,009,523,333.33 | ₱1,205,714,000.00 | -40.00% | 🟢 GREEN |
| Capacity Building Component | Activity | ₱2,009,523,333.33 | ₱1,949,237,633.33 | -3.00% | 🟡 AMBER |
| Equipment Component | Task | ₱2,009,523,333.33 | ₱2,109,999,500.00 | +5.00% | 🔴 RED |

**PPA Totals**:
- Total Allocated: ₱6,028,570,000.00
- Total Spent: ₱5,264,951,133.33
- Overall Variance: ₱-763,618,866.67 (-12.67%)
- ✅ Work item budgets match PPA budget exactly

---

### 3. Madaris Education Services
**PPA Budget**: ₱1,845,513,695.00
**Implementing MOA**: Ministry of Basic, Higher, and Technical Education

| Component | Type | Allocated | Spent | Variance | Status |
|-----------|------|-----------|-------|----------|--------|
| Infrastructure Component | Activity | ₱615,171,231.67 | ₱369,102,739.00 | -40.00% | 🟢 GREEN |
| Capacity Building Component | Activity | ₱615,171,231.67 | ₱596,716,094.72 | -3.00% | 🟡 AMBER |
| Equipment Component | Task | ₱615,171,231.67 | ₱645,929,793.25 | +5.00% | 🔴 RED |

**PPA Totals**:
- Total Allocated: ₱1,845,513,695.00
- Total Spent: ₱1,611,748,626.97
- Overall Variance: ₱-233,765,068.03 (-12.67%)
- ✅ Work item budgets match PPA budget exactly

---

## Overall Statistics

### Budget Status Distribution
```
Total Work Items with Budgets: 13

🟢 Under Budget (GREEN): 7 items (53.8%)
   - Variance < -5%
   - Efficient, under budget
   - Example: 60% utilization

🟡 Near Limit (AMBER):   3 items (23.1%)
   - Variance: -5% to +2%
   - Close to budget, requires monitoring
   - Example: 97% utilization

🔴 Over Budget (RED):    3 items (23.1%)
   - Variance >= +2%
   - Over budget, action needed
   - Example: 105% utilization
```

### Budget Status Thresholds
```python
if variance_pct > 2:
    status = "🔴 OVER BUDGET"
    css_class = "over-budget"
elif variance_pct > -5:
    status = "🟡 NEAR LIMIT"
    css_class = "near-limit"
else:
    status = "🟢 UNDER BUDGET"
    css_class = "under-budget"
```

---

## Data Validation

### ✅ Verified Aspects

1. **Budget Allocation Accuracy**
   - Each PPA's work items sum exactly to the PPA budget (±₱0.01 tolerance)
   - Budget distribution is mathematically correct (1/3 per component)

2. **Variance Calculation**
   - Formula: `variance = actual_expenditure - allocated_budget`
   - Percentage: `variance_pct = (variance / allocated_budget) * 100`

3. **Status Color Logic**
   - GREEN: variance < -5% (efficient spending)
   - AMBER: -5% ≤ variance < +2% (near budget limit)
   - RED: variance ≥ +2% (over budget)

4. **Work Item Properties**
   - All items have `related_ppa` linking to parent PPA
   - All items have realistic `budget_notes` explaining scenario
   - Progress and status fields set appropriately
   - Work types varied (activity, task)

---

## Test Scenarios Covered

### Scenario 1: Under Budget (GREEN) - 60% Utilization
```
Component: Infrastructure Development
Allocated:  ₱8,301,636,651.67
Spent:      ₱4,980,981,991.00
Variance:   ₱-3,320,654,660.67 (-40.00%)
Status:     🟢 UNDER BUDGET
Reason:     Efficient procurement process, savings available
```

### Scenario 2: Near Limit (AMBER) - 97% Utilization
```
Component: Capacity Building
Allocated:  ₱8,301,636,651.67
Spent:      ₱8,052,587,552.12
Variance:   ₱-249,049,099.55 (-3.00%)
Status:     🟡 NEAR LIMIT
Reason:     Close to budget, requires monitoring
```

### Scenario 3: Over Budget (RED) - 105% Utilization
```
Component: Equipment Acquisition
Allocated:  ₱8,301,636,651.67
Spent:      ₱8,716,718,484.25
Variance:   ₱415,081,832.58 (+5.00%)
Status:     🔴 OVER BUDGET
Reason:     Cost overrun due to price increases
```

---

## Scripts Created

### 1. Data Creation Script
**Location**: `/src/scripts/create_budget_test_data.py`

**Usage**:
```bash
cd src
python scripts/create_budget_test_data.py
```

**Features**:
- Creates 3 work items per PPA (9 total)
- Demonstrates all three budget status colors
- Ensures budgets sum to PPA total
- Adds realistic budget notes
- Provides detailed console output

### 2. Verification Script
**Location**: `/src/scripts/verify_budget_test_data.py`

**Usage**:
```bash
cd src
python scripts/verify_budget_test_data.py
```

**Features**:
- Displays all work items with budget details
- Shows variance calculations
- Verifies PPA budget aggregation
- Counts items by status color
- Provides CSS class suggestions

---

## Next Steps: Testing in UI

### 1. Access Monitoring Dashboard
```
URL: http://localhost:8000/monitoring/
```

### 2. View PPA Details
1. Navigate to a test PPA:
   - School-Based Management and Operation
   - Road and Bridge Development Program
   - Madaris Education Services

2. Click "Work Items" tab

3. Verify display shows:
   - Work item titles
   - Allocated budget
   - Actual expenditure
   - Variance with percentage
   - Color indicator (green/amber/red)

### 3. Test Budget Aggregation
1. Check PPA totals section
2. Verify sum of work item budgets
3. Confirm overall variance calculation
4. Validate color coding logic

### 4. Test Filtering/Sorting
- Filter by budget status (over/under/near limit)
- Sort by variance percentage
- Sort by allocated budget
- Search work items by title

---

## Expected UI Display

### Work Items Table (Example)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Work Items (3)                                                      Total:  │
│                                                           ₱24,904,909,955.00 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 🟢 Infrastructure Component                             UNDER BUDGET       │
│    Allocated: ₱8,301,636,651.67 | Spent: ₱4,980,981,991.00                 │
│    Variance: ₱-3,320,654,660.67 (-40.00%) | Progress: 60%                  │
│    Status: In Progress                                                      │
│                                                                             │
│ 🟡 Capacity Building Component                          NEAR LIMIT         │
│    Allocated: ₱8,301,636,651.67 | Spent: ₱8,052,587,552.12                 │
│    Variance: ₱-249,049,099.55 (-3.00%) | Progress: 97%                     │
│    Status: In Progress                                                      │
│                                                                             │
│ 🔴 Equipment Component                                   OVER BUDGET        │
│    Allocated: ₱8,301,636,651.67 | Spent: ₱8,716,718,484.25                 │
│    Variance: ₱415,081,832.58 (+5.00%) | Progress: 100%                     │
│    Status: In Progress                                                      │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ TOTALS:                                                                     │
│   Allocated: ₱24,904,909,955.00                                             │
│   Spent:     ₱21,750,288,027.37                                             │
│   Variance:  ₱-3,154,621,927.63 (-12.67%)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CSS Classes for Styling

### Budget Status Indicators

```css
/* Under Budget - GREEN */
.under-budget {
    background-color: #ecfdf5; /* bg-emerald-50 */
    border-color: #10b981;     /* border-emerald-500 */
    color: #047857;            /* text-emerald-700 */
}

/* Near Limit - AMBER */
.near-limit {
    background-color: #fffbeb; /* bg-amber-50 */
    border-color: #f59e0b;     /* border-amber-500 */
    color: #b45309;            /* text-amber-700 */
}

/* Over Budget - RED */
.over-budget {
    background-color: #fef2f2; /* bg-red-50 */
    border-color: #ef4444;     /* border-red-500 */
    color: #b91c1c;            /* text-red-700 */
}
```

---

## Troubleshooting

### Issue: Work items not showing
**Solution**: Ensure `related_ppa` field is set correctly:
```python
wi = WorkItem.objects.get(id='...')
wi.related_ppa  # Should return a MonitoringEntry object
```

### Issue: Budget totals don't match
**Solution**: Verify sum of allocated budgets:
```python
from django.db.models import Sum
WorkItem.objects.filter(related_ppa=ppa).aggregate(
    Sum('allocated_budget')
)
```

### Issue: Variance calculation incorrect
**Solution**: Check decimal precision:
```python
variance = wi.actual_expenditure - wi.allocated_budget
variance_pct = (variance / wi.allocated_budget) * 100
# Should use Decimal types, not float
```

---

## Cleanup (Optional)

To remove test data:

```python
from common.work_item_model import WorkItem

# Delete test work items (created by system user)
WorkItem.objects.filter(
    created_by__username='system',
    related_ppa__isnull=False
).delete()
```

**Warning**: This will delete all work items created by the system user. Be careful in production!

---

## Related Documentation

- [Budget Tracking Enhancements Implementation](../improvements/BUDGET_TRACKING_ENHANCEMENTS_IMPLEMENTATION.md)
- [Budget Tracking Test Report](BUDGET_TRACKING_TEST_REPORT.md)
- [Budget Tracking Quick Test Guide](BUDGET_TRACKING_QUICK_TEST.md)
- [Work Item Model](../../src/common/work_item_model.py)
- [Monitoring Entry Model](../../src/monitoring/models.py)

---

## Success Criteria

✅ **All criteria met**:

1. ✅ Created 9 work items across 3 PPAs
2. ✅ Each PPA has 3 work items demonstrating:
   - 1 under budget (GREEN) - 60% utilization
   - 1 near budget limit (AMBER) - 97% utilization
   - 1 over budget (RED) - 105% utilization
3. ✅ Realistic budget values (sum to PPA budget ±₱0.01)
4. ✅ Descriptive titles and budget notes
5. ✅ Variance calculations verified
6. ✅ Status color logic tested
7. ✅ Scripts created for data generation and verification
8. ✅ Documentation complete

---

**Status**: ✅ Ready for UI testing
**Last Updated**: 2025-10-08
