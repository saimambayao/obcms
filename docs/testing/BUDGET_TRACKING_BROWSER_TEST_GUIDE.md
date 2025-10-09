# Budget Tracking Browser Test Guide

**Date**: 2025-10-08
**Purpose**: Quick visual verification of budget tracking functionality in the browser
**Prerequisites**: Test data created via `create_budget_test_data.py`

---

## Quick Start

### 1. Start Development Server

```bash
cd src
./manage.py runserver
```

Server will be available at: **http://localhost:8000**

---

## Test URLs

### Test PPA #1: School-Based Management and Operation

**PPA Details**:
- Budget: ₱24,904,909,955.00
- Work Items: 3 (1 GREEN, 1 AMBER, 1 RED)
- MOA: Ministry of Basic, Higher, and Technical Education

**URLs**:
```
PPA Detail: http://localhost:8000/monitoring/6d3b4870-b882-4648-b6fb-2592de446a5c/
Work Items Tab: http://localhost:8000/monitoring/6d3b4870-b882-4648-b6fb-2592de446a5c/#work-items
```

### Test PPA #2: Road and Bridge Development Program

**PPA Details**:
- Budget: ₱6,028,570,000.00
- Work Items: 3 (1 GREEN, 1 AMBER, 1 RED)
- MOA: Ministry of Public Works

**URLs**:
```
PPA Detail: http://localhost:8000/monitoring/[PPA_ID]/
Work Items Tab: http://localhost:8000/monitoring/[PPA_ID]/#work-items
```

### Test PPA #3: Madaris Education Services

**PPA Details**:
- Budget: ₱1,845,513,695.00
- Work Items: 3 (1 GREEN, 1 AMBER, 1 RED)
- MOA: Ministry of Basic, Higher, and Technical Education

**URLs**:
```
PPA Detail: http://localhost:8000/monitoring/[PPA_ID]/
Work Items Tab: http://localhost:8000/monitoring/[PPA_ID]/#work-items
```

---

## What to Verify

### ✅ Visual Checklist

#### 1. Work Items Tab Display

- [ ] Tab is visible and clickable
- [ ] Shows count of work items (should show "3")
- [ ] Table/list displays correctly

#### 2. Work Item Cards/Rows

For each work item, verify:

**🟢 UNDER BUDGET (Infrastructure Component)**
- [ ] Green background/border color
- [ ] Allocated: ₱8,301,636,651.67
- [ ] Spent: ₱4,980,981,991.00
- [ ] Variance: -40.00% (negative, in green)
- [ ] Status indicator shows "Under Budget" or similar
- [ ] Progress bar shows 60%

**🟡 NEAR LIMIT (Capacity Building Component)**
- [ ] Amber/yellow background/border color
- [ ] Allocated: ₱8,301,636,651.67
- [ ] Spent: ₱8,052,587,552.12
- [ ] Variance: -3.00% (slightly negative, in amber)
- [ ] Status indicator shows "Near Limit" or similar
- [ ] Progress bar shows 97%

**🔴 OVER BUDGET (Equipment Component)**
- [ ] Red background/border color
- [ ] Allocated: ₱8,301,636,651.67
- [ ] Spent: ₱8,716,718,484.25
- [ ] Variance: +5.00% (positive, in red)
- [ ] Status indicator shows "Over Budget" or similar
- [ ] Progress bar shows 100%

#### 3. Budget Totals Section

- [ ] Total Allocated: ₱24,904,909,955.00
- [ ] Total Spent: ₱21,750,288,027.37
- [ ] Overall Variance: -12.67% (should match)
- [ ] Variance amount in currency: ₱-3,154,621,927.63

#### 4. Budget Status Indicators

- [ ] Icons/badges for each status (🟢 🟡 🔴)
- [ ] Color coding is consistent
- [ ] Status text is readable
- [ ] Hover effects work (if applicable)

---

## Expected Visual Appearance

### Work Item Card Example (GREEN)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🟢 UNDER BUDGET                                                 │
│                                                                 │
│ School-Based Management and Operation - Infrastructure Component│
│                                                                 │
│ ┌──────────────────┬──────────────────┬──────────────────────┐  │
│ │ Allocated        │ Spent            │ Variance             │  │
│ │ ₱8.30B           │ ₱4.98B           │ -40.00% (₱-3.32B)    │  │
│ └──────────────────┴──────────────────┴──────────────────────┘  │
│                                                                 │
│ Progress: [████████████████████░░░░░░░░░░░░] 60%               │
│                                                                 │
│ Status: In Progress | Type: Activity                           │
│ Notes: Under budget - efficient procurement. Savings available.│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Work Item Card Example (AMBER)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🟡 NEAR LIMIT                                                   │
│                                                                 │
│ School-Based Management and Operation - Capacity Building Comp. │
│                                                                 │
│ ┌──────────────────┬──────────────────┬──────────────────────┐  │
│ │ Allocated        │ Spent            │ Variance             │  │
│ │ ₱8.30B           │ ₱8.05B           │ -3.00% (₱-249.05M)   │  │
│ └──────────────────┴──────────────────┴──────────────────────┘  │
│                                                                 │
│ Progress: [███████████████████████████████████░░] 97%           │
│                                                                 │
│ Status: In Progress | Type: Activity                           │
│ Notes: Near budget limit - requires monitoring.                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Work Item Card Example (RED)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔴 OVER BUDGET                                                  │
│                                                                 │
│ School-Based Management and Operation - Equipment Component    │
│                                                                 │
│ ┌──────────────────┬──────────────────┬──────────────────────┐  │
│ │ Allocated        │ Spent            │ Variance             │  │
│ │ ₱8.30B           │ ₱8.72B           │ +5.00% (₱+415.08M)   │  │
│ └──────────────────┴──────────────────┴──────────────────────┘  │
│                                                                 │
│ Progress: [████████████████████████████████████████] 100%       │
│                                                                 │
│ Status: In Progress | Type: Task                               │
│ Notes: Over budget - cost overrun due to price increases.      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Interactions to Test

### 1. Sorting

- [ ] Sort by allocated budget (ascending/descending)
- [ ] Sort by actual expenditure
- [ ] Sort by variance percentage
- [ ] Sort by variance amount

### 2. Filtering

- [ ] Filter to show only "Over Budget" items (RED)
- [ ] Filter to show only "Near Limit" items (AMBER)
- [ ] Filter to show only "Under Budget" items (GREEN)
- [ ] Filter by work type (Activity, Task)
- [ ] Filter by status (In Progress, Completed, etc.)

### 3. Search

- [ ] Search by work item title
- [ ] Search results filter correctly
- [ ] Clear search resets view

### 4. Pagination (if applicable)

- [ ] Page size selector works
- [ ] Next/previous buttons function
- [ ] Jump to page works

---

## Color Coding Verification

### CSS Classes to Check

**Inspect Element → Check Applied Classes**

```css
/* Under Budget - GREEN */
.under-budget {
    background-color: #ecfdf5; /* bg-emerald-50 */
    border-color: #10b981;     /* border-emerald-500 */
}

/* Near Limit - AMBER */
.near-limit {
    background-color: #fffbeb; /* bg-amber-50 */
    border-color: #f59e0b;     /* border-amber-500 */
}

/* Over Budget - RED */
.over-budget {
    background-color: #fef2f2; /* bg-red-50 */
    border-color: #ef4444;     /* border-red-500 */
}
```

### Variance Display Colors

```css
/* Negative variance (under budget) */
.variance-negative {
    color: #047857; /* text-emerald-700 */
}

/* Positive variance (over budget) */
.variance-positive {
    color: #b91c1c; /* text-red-700 */
}
```

---

## Responsive Testing

### Desktop (1920x1080)
- [ ] All 3 work items visible
- [ ] Budget numbers readable
- [ ] Color indicators clear
- [ ] No horizontal scroll

### Tablet (768x1024)
- [ ] Layout adapts (single column if needed)
- [ ] Touch targets large enough
- [ ] Numbers still readable

### Mobile (375x667)
- [ ] Cards stack vertically
- [ ] Budget numbers abbreviated (e.g., "₱8.30B")
- [ ] Status indicators visible
- [ ] Scroll works smoothly

---

## Performance Check

### Page Load
- [ ] Work items tab loads in < 2 seconds
- [ ] No JavaScript errors in console
- [ ] No layout shifts (CLS)

### Interactions
- [ ] Sorting is instant (< 100ms)
- [ ] Filtering is instant (< 100ms)
- [ ] Search results update smoothly

---

## Accessibility Check

### Keyboard Navigation
- [ ] Tab through work items
- [ ] Enter/Space to expand details
- [ ] Arrow keys to navigate list

### Screen Reader
- [ ] Budget status announced correctly
- [ ] Variance values read properly
- [ ] Color indicators have text labels

### Color Contrast
- [ ] Green text readable on green background
- [ ] Amber text readable on amber background
- [ ] Red text readable on red background
- [ ] All meet WCAG 2.1 AA (4.5:1 ratio)

---

## Common Issues & Solutions

### Issue: Work items not showing

**Check**:
1. Navigate to correct PPA detail page
2. Click "Work Items" tab
3. Open browser console for errors

**Solution**:
```javascript
// Console should NOT show:
- "related_ppa is null"
- "Cannot read property 'allocated_budget'"
- 404 errors for API endpoints
```

### Issue: Colors not displaying

**Check**:
1. Right-click work item → Inspect
2. Check applied CSS classes
3. Verify Tailwind CSS is loaded

**Solution**:
```html
<!-- Should see classes like: -->
<div class="bg-emerald-50 border-emerald-500 ...">
```

### Issue: Variance calculation wrong

**Check**:
1. Open browser DevTools
2. Check Network tab for API response
3. Verify JSON data

**Expected JSON**:
```json
{
  "allocated_budget": "8301636651.67",
  "actual_expenditure": "4980981991.00",
  "variance": "-3320654660.67",
  "variance_pct": "-40.00"
}
```

---

## Screenshot Checklist

Take screenshots for documentation:

- [ ] Full page view of PPA with work items tab
- [ ] Close-up of GREEN work item
- [ ] Close-up of AMBER work item
- [ ] Close-up of RED work item
- [ ] Budget totals section
- [ ] Mobile view (responsive)

Save screenshots to:
```
docs/testing/screenshots/budget_tracking/
```

---

## Test Report Template

After testing, document results:

```markdown
# Budget Tracking Browser Test Report

**Date**: [Date]
**Tester**: [Name]
**Browser**: [Chrome/Firefox/Safari] [Version]
**Device**: [Desktop/Mobile]

## Test Results

### Visual Display: ✅ Pass / ❌ Fail
- Work items tab: [Pass/Fail]
- Color indicators: [Pass/Fail]
- Budget numbers: [Pass/Fail]

### Functionality: ✅ Pass / ❌ Fail
- Sorting: [Pass/Fail]
- Filtering: [Pass/Fail]
- Search: [Pass/Fail]

### Performance: ✅ Pass / ❌ Fail
- Page load: [X]s
- Interaction speed: [Pass/Fail]

### Issues Found
1. [Description]
2. [Description]

### Screenshots
- [Attach screenshots]
```

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Mark feature as production-ready
2. Document in release notes
3. Create user guide
4. Update changelog

### If Tests Fail ❌
1. Document failures in GitHub issue
2. Include screenshots
3. Provide browser/device info
4. Assign to developer

---

## Quick Reference: Test Data

| PPA | Budget | Work Items | Status Distribution |
|-----|--------|------------|---------------------|
| School-Based Management | ₱24.90B | 3 | 1 GREEN, 1 AMBER, 1 RED |
| Road and Bridge | ₱6.03B | 3 | 1 GREEN, 1 AMBER, 1 RED |
| Madaris Education | ₱1.85B | 3 | 1 GREEN, 1 AMBER, 1 RED |

**Total**: 9 work items across 3 PPAs

---

## Support

### Need Help?
- Check [Budget Tracking Test Data Summary](BUDGET_TRACKING_TEST_DATA_SUMMARY.md)
- Review [Budget Tracking Implementation](../improvements/BUDGET_TRACKING_ENHANCEMENTS_IMPLEMENTATION.md)
- Run verification script: `python scripts/verify_budget_test_data.py`

---

**Status**: Ready for browser testing
**Last Updated**: 2025-10-08
