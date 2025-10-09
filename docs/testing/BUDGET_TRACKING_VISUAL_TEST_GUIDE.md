# Budget Tracking - Visual Test Guide

**Purpose:** Step-by-step visual testing guide with expected screenshots
**URL:** `http://localhost:8000/oobc-management/work-items/afcadb19-8b75-4ee9-b4c5-7ccd5150f4a2/edit/`

---

## 🎯 Quick Test Execution (5 Minutes)

### Step 1: Navigate to Edit Page
```
URL: http://localhost:8000/oobc-management/work-items/afcadb19-8b75-4ee9-b4c5-7ccd5150f4a2/edit/
```

**Expected View:**
```
┌─────────────────────────────────────────────────────────────┐
│  Edit Work Item                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Basic Information Section]                                │
│  [Status & Priority Section]                                │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 💰 Budget Tracking                                    │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │                                                       │ │
│  │  Allocated Budget        Actual Expenditure         │ │
│  │  ┌─────────────────┐    ┌─────────────────┐         │ │
│  │  │ ₱ [input field] │    │ ₱ [input field] │         │ │
│  │  └─────────────────┘    └─────────────────┘         │ │
│  │                                                       │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │ Budget Variance:             ₱0.00              │ │ │
│  │  │ [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] (0%)        │ │ │
│  │  │ No budget allocated                             │ │ │
│  │  └─────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  [Schedule & Timeline Section]                              │
└─────────────────────────────────────────────────────────────┘
```

**✅ Checklist:**
- [ ] Section appears between "Status & Priority" and "Schedule & Timeline"
- [ ] Wallet icon (💰) is emerald color
- [ ] Two input fields with ₱ prefix
- [ ] Variance display shows ₱0.00 in gray
- [ ] Progress bar is gray (0% width)

---

## 📸 Test Scenario 1: Under Budget (50% Utilization)

### Actions:
1. Click "Allocated Budget" field
2. Type: `100000`
3. Click "Actual Expenditure" field
4. Type: `50000`
5. Click outside fields

### Expected Visual Result:

```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Budget Tracking                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Allocated Budget              Actual Expenditure          │
│  ┌───────────────────┐         ┌───────────────────┐       │
│  │ ₱ 100000.00       │         │ ₱ 50000.00        │       │
│  └───────────────────┘         └───────────────────┘       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Budget Variance:                 ₱50,000.00 🟢      │   │
│  │ [████████████████░░░░░░░░░░░░░░░░░░░░░░] (50%)      │   │
│  │ 50.0% utilized - Within budget 🟢                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Color Verification:**
- **Variance Display:** ₱50,000.00 in **emerald-600** (#059669)
- **Progress Bar:** **emerald-500** (#10b981) background, 50% width
- **Status Text:** "50.0% utilized - Within budget" in **emerald-600**

**✅ Checklist:**
- [ ] Variance updates **instantly** (no page reload)
- [ ] All green (emerald) colors applied
- [ ] Progress bar width exactly 50%
- [ ] Status text shows "50.0% utilized - Within budget"
- [ ] Smooth animation (300ms transition)
- [ ] No JavaScript errors in console

---

## 📸 Test Scenario 2: Near Limit (96% Utilization)

### Actions:
1. Keep Allocated Budget: `100000`
2. Change Actual Expenditure to: `96000`
3. Tab out

### Expected Visual Result:

```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Budget Tracking                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Allocated Budget              Actual Expenditure          │
│  ┌───────────────────┐         ┌───────────────────┐       │
│  │ ₱ 100000.00       │         │ ₱ 96000.00        │       │
│  └───────────────────┘         └───────────────────┘       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Budget Variance:                  ₱4,000.00 🟡      │   │
│  │ [████████████████████████████████████░░░░░] (96%)   │   │
│  │ 96.0% utilized - Near budget limit ⚠️              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Color Verification:**
- **Variance Display:** ₱4,000.00 in **amber-600** (#d97706)
- **Progress Bar:** **amber-500** (#f59e0b) background, 96% width
- **Status Text:** "96.0% utilized - Near budget limit" in **amber-600**

**✅ Checklist:**
- [ ] Color changes from green to amber **instantly**
- [ ] Progress bar width exactly 96%
- [ ] Warning message appears
- [ ] Smooth color transition
- [ ] No console errors

**🧪 Edge Case Tests:**
- [ ] 95.0% → Amber (boundary)
- [ ] 94.9% → Green (below threshold)
- [ ] 99.9% → Amber (near 100%)
- [ ] 100.0% → Amber (exact match)

---

## 📸 Test Scenario 3: Over Budget (120% Utilization)

### Actions:
1. Keep Allocated Budget: `100000`
2. Change Actual Expenditure to: `120000`
3. Tab out

### Expected Visual Result:

```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Budget Tracking                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Allocated Budget              Actual Expenditure          │
│  ┌───────────────────┐         ┌───────────────────┐       │
│  │ ₱ 100000.00       │         │ ₱ 120000.00       │       │
│  └───────────────────┘         └───────────────────┘       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Budget Variance:                 ₱20,000.00 🔴      │   │
│  │ [████████████████████████████████████████████] (100%)│   │
│  │ Over budget by ₱20,000.00 ❌                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Color Verification:**
- **Variance Display:** ₱20,000.00 in **red-600** (#dc2626)
- **Progress Bar:** **red-500** (#ef4444) background, **100% width** (capped)
- **Status Text:** "Over budget by ₱20,000.00" in **red-600**

**✅ Checklist:**
- [ ] Color changes to red
- [ ] Progress bar width **capped at 100%** (not 120%)
- [ ] Shows overage amount: "Over budget by ₱20,000.00"
- [ ] Variance shows absolute value (₱20,000.00, not -₱20,000.00)
- [ ] No console errors

**🧪 Edge Case Tests:**
- [ ] 110% → Red, bar at 100%
- [ ] 150% → Red, bar at 100%
- [ ] 200% → Red, bar at 100% (no overflow)

---

## 📸 Test Scenario 4: Zero Budget Edge Case

### Actions:
1. Clear Allocated Budget (leave empty or `0`)
2. Clear Actual Expenditure (leave empty or `0`)

### Expected Visual Result:

```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Budget Tracking                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Allocated Budget              Actual Expenditure          │
│  ┌───────────────────┐         ┌───────────────────┐       │
│  │ ₱ 0.00            │         │ ₱ 0.00            │       │
│  └───────────────────┘         └───────────────────┘       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Budget Variance:                     ₱0.00 🟢      │   │
│  │ [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] (0%)    │   │
│  │ No budget allocated                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**✅ Checklist:**
- [ ] No JavaScript errors (division by zero handled)
- [ ] Status text: "No budget allocated"
- [ ] Progress bar at 0%
- [ ] Green color (default state)

**🧪 Zero Budget with Expenditure:**
```
Allocated: 0
Expenditure: 1000
Expected: Red, "Over budget by ₱1,000.00"
```

---

## 📸 Test Scenario 5: Form Submission & Persistence

### Actions:
1. Set Allocated Budget: `100000`
2. Set Actual Expenditure: `50000`
3. Verify variance shows: ₱50,000.00 (green), 50%
4. Click "Save Work Item" button
5. Wait for "Saved at [time]" message
6. Navigate to work item detail page
7. Click "Edit" to return to edit page

### Expected After Save & Reload:

```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Budget Tracking                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Allocated Budget              Actual Expenditure          │
│  ┌───────────────────┐         ┌───────────────────┐       │
│  │ ₱ 100000.00       │ ✅      │ ₱ 50000.00        │ ✅    │
│  └───────────────────┘         └───────────────────┘       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Budget Variance:                 ₱50,000.00 🟢      │   │
│  │ [████████████████░░░░░░░░░░░░░░░░░░░░░░] (50%)      │   │
│  │ 50.0% utilized - Within budget 🟢                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**✅ Checklist:**
- [ ] Values persisted in database
- [ ] Variance recalculates on page load
- [ ] Color coding applied correctly
- [ ] Progress bar width restored
- [ ] `calculateBudgetVariance()` called on `DOMContentLoaded`

**Database Verification (Django Shell):**
```python
from common.work_item_model import WorkItem
item = WorkItem.objects.get(pk='afcadb19-8b75-4ee9-b4c5-7ccd5150f4a2')
assert item.allocated_budget == 100000.00
assert item.actual_expenditure == 50000.00
```

---

## 📸 Test Scenario 6: Responsive Design

### Mobile View (375px width)

```
┌─────────────────────────┐
│ 💰 Budget Tracking      │
├─────────────────────────┤
│                         │
│ Allocated Budget        │
│ ┌─────────────────────┐ │
│ │ ₱ 100000.00         │ │
│ └─────────────────────┘ │
│                         │
│ Actual Expenditure      │
│ ┌─────────────────────┐ │
│ │ ₱ 50000.00          │ │
│ └─────────────────────┘ │
│                         │
│ ┌─────────────────────┐ │
│ │ Budget Variance:    │ │
│ │ ₱50,000.00 🟢       │ │
│ │ [████████░░░░░] 50% │ │
│ │ 50.0% utilized -    │ │
│ │ Within budget 🟢    │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

**✅ Mobile Checklist:**
- [ ] Single column layout (`grid-cols-1`)
- [ ] Allocated Budget: Full width
- [ ] Actual Expenditure: Full width (stacked below)
- [ ] Touch targets: Minimum 48px height
- [ ] No horizontal scrolling
- [ ] Text remains readable

### Desktop View (1920px width)

```
┌───────────────────────────────────────────────────────────────┐
│ 💰 Budget Tracking                                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  Allocated Budget                    Actual Expenditure      │
│  ┌──────────────────────────┐       ┌──────────────────────┐ │
│  │ ₱ 100000.00              │       │ ₱ 50000.00           │ │
│  └──────────────────────────┘       └──────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Budget Variance:                         ₱50,000.00 🟢  │ │
│  │ [████████████████████████░░░░░░░░░░░░░░░░░░░░░] (50%)   │ │
│  │ 50.0% utilized - Within budget 🟢                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

**✅ Desktop Checklist:**
- [ ] Two-column layout (`md:grid-cols-2`)
- [ ] Side-by-side inputs
- [ ] Variance display: Full width
- [ ] Proper spacing (`gap-6`)

---

## 🧪 JavaScript Console Testing

### Open Console (F12 or Cmd+Option+I)

**Expected Console Output (No Errors):**
```
[Page Load]
✅ No errors
✅ calculateBudgetVariance() executes

[Typing in Allocated Budget]
✅ oninput event fired
✅ calculateBudgetVariance() called
✅ No undefined errors

[Typing in Actual Expenditure]
✅ oninput event fired
✅ calculateBudgetVariance() called
✅ Variance updates in real-time
```

**❌ Errors to Watch For:**
```javascript
// Bad: Element not found
❌ TypeError: Cannot read property 'value' of null
   → Check: id_allocated_budget exists

// Bad: Function not defined
❌ ReferenceError: calculateBudgetVariance is not defined
   → Check: Script loaded properly

// Bad: Cannot update display
❌ TypeError: Cannot set property 'textContent' of null
   → Check: budget-variance-display exists

// Bad: NaN in calculation
❌ Variance: NaN
   → Check: parseFloat() handling
```

---

## 📋 Quick Test Summary Table

| Scenario | Allocated | Expenditure | Variance | Color | Bar % | Status |
|----------|-----------|-------------|----------|-------|-------|--------|
| Initial Load | 0 | 0 | ₱0.00 | Gray | 0% | No budget allocated |
| Under Budget | 100000 | 50000 | ₱50,000.00 | 🟢 Green | 50% | 50.0% utilized - Within budget |
| Near Limit | 100000 | 96000 | ₱4,000.00 | 🟡 Amber | 96% | 96.0% utilized - Near budget limit |
| Over Budget | 100000 | 120000 | ₱20,000.00 | 🔴 Red | 100% | Over budget by ₱20,000.00 |
| Edge: 100% | 100000 | 100000 | ₱0.00 | 🟡 Amber | 100% | 100.0% utilized - Near budget limit |
| Edge: Zero Budget | 0 | 1000 | ₱1,000.00 | 🔴 Red | 100% | Over budget by ₱1,000.00 |

---

## 🎬 Testing Workflow (Step-by-Step)

### Complete Test Run (15 minutes)

```bash
# 1. Start Server
cd src
./manage.py runserver

# 2. Open Browser
http://localhost:8000/oobc-management/work-items/afcadb19-8b75-4ee9-b4c5-7ccd5150f4a2/edit/

# 3. Open DevTools
F12 (or Cmd+Option+I)
Go to Console tab

# 4. Test Scenario 1: Under Budget (50%)
Allocated: 100000
Expenditure: 50000
Expected: Green, ₱50,000.00, 50%, "50.0% utilized - Within budget"
✅ Screenshot

# 5. Test Scenario 2: Near Limit (96%)
Expenditure: 96000
Expected: Amber, ₱4,000.00, 96%, "96.0% utilized - Near budget limit"
✅ Screenshot

# 6. Test Scenario 3: Over Budget (120%)
Expenditure: 120000
Expected: Red, ₱20,000.00, 100% (capped), "Over budget by ₱20,000.00"
✅ Screenshot

# 7. Test Edge Cases
- Zero budget: 0 / 0 → Gray, "No budget allocated"
- Zero with expenditure: 0 / 1000 → Red, "Over budget"
- Exact match: 100000 / 100000 → Amber, 100%
✅ Screenshots

# 8. Test Form Submission
Click "Save Work Item"
Wait for confirmation
Navigate away
Return to edit page
Verify: Values persisted, variance recalculated
✅ Screenshot

# 9. Test Responsive (Optional)
Resize browser: 375px, 768px, 1920px
Verify: Layout adapts properly
✅ Screenshots

# 10. Review Console
Check for errors
Expected: No errors
✅ Console screenshot
```

---

## ✅ Final Checklist

### Visual Elements
- [ ] ₱ peso sign displays correctly
- [ ] Two-column grid on desktop
- [ ] Single-column on mobile
- [ ] Progress bar animates smoothly
- [ ] Colors match design system

### Functionality
- [ ] Real-time variance calculation
- [ ] Correct color coding (green/amber/red)
- [ ] Progress bar width accurate
- [ ] Form values persist after save
- [ ] No JavaScript errors

### Edge Cases
- [ ] Zero budget handled
- [ ] Over budget (>100%) handled
- [ ] Exact 100% triggers amber
- [ ] Division by zero protected
- [ ] Decimal values supported

### Accessibility
- [ ] Keyboard navigable
- [ ] Focus rings visible
- [ ] Screen reader compatible
- [ ] Color contrast sufficient

### Browser Compatibility
- [ ] Chrome ✅
- [ ] Firefox ✅
- [ ] Safari ✅
- [ ] Edge ✅

---

## 📸 Screenshot Naming Convention

Save screenshots with descriptive names:
```
budget_tracking_1_initial_load.png
budget_tracking_2_under_budget_50.png
budget_tracking_3_near_limit_96.png
budget_tracking_4_over_budget_120.png
budget_tracking_5_edge_zero_budget.png
budget_tracking_6_form_saved.png
budget_tracking_7_responsive_mobile.png
budget_tracking_8_console_no_errors.png
```

---

## 🎯 Expected Test Outcome

**✅ All Tests Should Pass**

The Budget Tracking section is fully functional with:
- Real-time variance calculation
- Accurate color coding
- Smooth transitions
- Proper form persistence
- Responsive layout
- No JavaScript errors
- Accessible to all users

**Status:** 📋 **READY FOR MANUAL TESTING**
