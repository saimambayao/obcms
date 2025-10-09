# Budget Tracking End-to-End Test Plan

**Date**: 2025-10-08
**Status**: Ready for Manual Testing
**Priority**: CRITICAL
**Component**: Budget Tracking Workflow

---

## Overview

This document provides a comprehensive end-to-end testing procedure for the budget tracking feature across all work item forms (sidebar create, main edit, sidebar edit, and detail view).

**Prerequisites:**
- Development server running on http://localhost:8000
- Chrome DevTools (F12) open with Console tab visible
- Test user logged in with appropriate permissions
- Test PPA ID: `76db959e-1b99-472d-9b1d-924d4d22fd6f`
- Test Work Item ID: `6c25915a-8a99-496e-9c8b-8bb34a42979e`

---

## Test Scenario 1: Sidebar Create Form Budget (from PPA page)

### Setup
1. Navigate to: http://localhost:8000/monitoring/entry/76db959e-1b99-472d-9b1d-924d4d22fd6f/
2. Open Chrome DevTools (F12) → Console tab
3. Click the "Create Work Item" button

### Expected UI Elements

**Budget Tracking Section should appear with:**

1. **Total PPA Budget Display**
   - Large blue info box at the top
   - Icon: `fa-wallet`
   - Label: "Total PPA Budget"
   - Value: Should match the PPA's total budget (formatted with ₱ and commas)
   - Read-only (not editable)

2. **Allocated Budget Input**
   - Label: "Allocated Budget" with red asterisk (required)
   - Input field with `₱` prefix
   - Placeholder: "0.00"
   - Type: number with step="0.01"

3. **Actual Expenditure Input**
   - Label: "Actual Expenditure"
   - Input field with `₱` prefix
   - Placeholder: "0.00"
   - Type: number with step="0.01"
   - Optional field (no asterisk)

4. **Budget Variance Display**
   - Label: "Budget Variance"
   - Shows "₱0.00" when no values entered
   - Color-coded based on variance:
     - **Green**: > 10% remaining (healthy)
     - **Amber/Yellow**: 5-10% remaining (warning)
     - **Red**: < 5% remaining or over budget (critical)
   - Progress bar showing utilization percentage

### Test Cases

#### Test 1.1: PPA Total Budget Validation (Over Allocation)
**Steps:**
1. In "Allocated Budget", enter: `999999999` (extremely high value)
2. Tab out or click elsewhere

**Expected Results:**
- ❌ Red error message appears below allocated budget input:
  - "Allocated budget cannot exceed PPA total budget of ₱[PPA_AMOUNT]"
- ❌ Submit button is disabled (gray, not clickable)
- ❌ Console shows validation message (not an error)

**Screenshot Checklist:**
- [ ] Error message visible
- [ ] Submit button disabled
- [ ] No console errors (validation warnings OK)

#### Test 1.2: PPA Total Budget Validation (Valid Allocation)
**Steps:**
1. In "Allocated Budget", enter a value less than PPA total (e.g., `50000`)
2. Tab out

**Expected Results:**
- ✅ Error message disappears
- ✅ Submit button is enabled (blue gradient)
- ✅ Budget variance recalculates

**Screenshot Checklist:**
- [ ] No error message
- [ ] Submit button enabled
- [ ] Variance shows correctly

#### Test 1.3: Budget Variance Calculation - Healthy (Green)
**Steps:**
1. Set Allocated Budget: `50000`
2. Set Actual Expenditure: `30000`
3. Observe variance display

**Expected Results:**
- ✅ Variance shows: **₱20,000** (or ₱20,000.00)
- ✅ Background color: **Green** (emerald-50 or similar)
- ✅ Progress bar: **60%** filled (30,000 / 50,000 = 60%)
- ✅ Text indicator: "40% Remaining" or similar

**Screenshot Checklist:**
- [ ] Variance value correct
- [ ] Green background
- [ ] Progress bar at 60%
- [ ] Console clear of errors

#### Test 1.4: Budget Variance Calculation - Warning (Amber)
**Steps:**
1. Set Allocated Budget: `100000`
2. Set Actual Expenditure: `94000`
3. Observe variance display

**Expected Results:**
- ✅ Variance shows: **₱6,000**
- ✅ Background color: **Amber/Yellow** (amber-50 or yellow-50)
- ✅ Progress bar: **94%** filled
- ✅ Warning indicator: "6% Remaining" (in warning zone: 5-10%)

**Screenshot Checklist:**
- [ ] Variance value correct
- [ ] Amber/yellow background
- [ ] Progress bar at 94%
- [ ] Console clear of errors

#### Test 1.5: Budget Variance Calculation - Over Budget (Red)
**Steps:**
1. Set Allocated Budget: `50000`
2. Set Actual Expenditure: `60000`
3. Observe variance display

**Expected Results:**
- ✅ Variance shows: **-₱10,000** (negative, over budget)
- ✅ Background color: **Red** (red-50 or rose-50)
- ✅ Progress bar: **120%** (or 100% filled, over budget indicator)
- ✅ Critical indicator: "Over Budget by ₱10,000" or similar

**Screenshot Checklist:**
- [ ] Negative variance displayed
- [ ] Red background
- [ ] Over budget indicator
- [ ] Console clear of errors

#### Test 1.6: Real-time Calculation
**Steps:**
1. Set Allocated Budget: `100000`
2. Slowly increment Actual Expenditure: `90000`, `95000`, `96000`, `98000`
3. Observe variance updates

**Expected Results:**
- ✅ Variance updates **instantly** as you type (no delay)
- ✅ Color changes automatically at thresholds:
  - Green → Amber at ~90,000 (10% threshold)
  - Amber → Red at ~95,000 (5% threshold)
- ✅ Progress bar animates smoothly
- ✅ No JavaScript errors in console

**Screenshot Checklist:**
- [ ] Real-time updates work
- [ ] Smooth color transitions
- [ ] No console errors

### Console Verification
**Open Console (F12 → Console) and verify:**
- ✅ NO red errors
- ✅ Function `calculateSidebarCreateBudgetVariance()` exists (type in console to check)
- ✅ Event listeners attached properly (no "listener not found" warnings)

---

## Test Scenario 2: Main Edit Form Budget

### Setup
1. Navigate to: http://localhost:8000/oobc-management/work-items/6c25915a-8a99-496e-9c8b-8bb34a42979e/edit/
2. Open Chrome DevTools (F12) → Console tab
3. Scroll to Budget Tracking section

### Expected UI Elements

**Same as Sidebar Create, but:**
- Values should be **pre-filled** if work item already has budget data
- PPA total budget should display if work item is linked to a PPA
- Layout may be slightly different (full-width form vs sidebar)

### Test Cases

#### Test 2.1: Pre-filled Values Verification
**Steps:**
1. Check if allocated budget and expenditure are pre-filled
2. Verify variance is calculated on page load

**Expected Results:**
- ✅ Allocated budget shows existing value (if any)
- ✅ Actual expenditure shows existing value (if any)
- ✅ Variance calculates automatically on page load
- ✅ Color coding is correct for current values

**Screenshot Checklist:**
- [ ] Pre-filled values correct
- [ ] Variance calculated on load
- [ ] No console errors

#### Test 2.2: PPA Validation in Edit Form
**Steps:**
1. If work item is linked to PPA, try to allocate > PPA total
2. Verify validation works

**Expected Results:**
- ✅ Same validation as sidebar create
- ✅ Error message appears
- ✅ Submit button disables

**Screenshot Checklist:**
- [ ] Validation works
- [ ] Error message displayed
- [ ] Submit disabled

#### Test 2.3: Form Submission with Budget
**Steps:**
1. Set valid budget values:
   - Allocated: `75000`
   - Expenditure: `50000`
2. Click "Update Work Item" or "Save" button
3. Wait for success message
4. Navigate back to work item detail page

**Expected Results:**
- ✅ Form submits successfully
- ✅ Success message appears (HTMX or Django messages)
- ✅ Values persist after save
- ✅ Detail page shows updated budget

**Screenshot Checklist:**
- [ ] Form submitted
- [ ] Success message
- [ ] Values persisted

### Console Verification
- ✅ Function `calculateBudgetVariance()` exists (main form version)
- ✅ No errors during form submission
- ✅ HTMX events fire correctly (if using HTMX)

---

## Test Scenario 3: Detail View Budget Display

### Setup
1. Navigate to: http://localhost:8000/oobc-management/work-items/6c25915a-8a99-496e-9c8b-8bb34a42979e/
2. Scroll to **Status & Priority** section
3. Look for **Budget Tracking** section AFTER Status & Priority

### Expected UI Elements

**Budget Tracking Section (Read-only):**
1. Section appears AFTER "Status & Priority"
2. All fields are **read-only** (plain text, not inputs)
3. Displays:
   - Total PPA Budget (if linked)
   - Allocated Budget (formatted with ₱)
   - Actual Expenditure (formatted with ₱)
   - Budget Variance (color-coded, with icon)
   - Utilization percentage with progress bar

### Test Cases

#### Test 3.1: Read-only Display Verification
**Steps:**
1. Verify all budget fields are displayed
2. Confirm they are NOT editable

**Expected Results:**
- ✅ Budget section appears after Status & Priority
- ✅ All values are plain text (not input fields)
- ✅ Color coding matches variance status
- ✅ Progress bar shows utilization visually

**Screenshot Checklist:**
- [ ] Section positioned correctly
- [ ] Read-only display
- [ ] Color coding correct
- [ ] Progress bar accurate

#### Test 3.2: Budget Variance Color Coding
**Steps:**
1. Check the variance value and color
2. Verify it matches expected thresholds

**Expected Results:**
- ✅ **Green**: Healthy budget (> 10% remaining)
- ✅ **Amber**: Warning (5-10% remaining)
- ✅ **Red**: Critical (< 5% or over budget)
- ✅ Icon matches status (check, warning, or alert icon)

**Screenshot Checklist:**
- [ ] Correct color for variance
- [ ] Icon matches status
- [ ] Visual clarity

#### Test 3.3: PPA Total Budget Display
**Steps:**
1. If work item is linked to PPA, verify PPA total shows
2. If not linked, verify it says "Not linked to PPA" or similar

**Expected Results:**
- ✅ PPA total budget displays correctly (if linked)
- ✅ Graceful message if not linked
- ✅ No broken or missing data

**Screenshot Checklist:**
- [ ] PPA total displays
- [ ] Graceful handling of missing data

---

## Test Scenario 4: Sidebar Edit Form Budget

### Setup
1. Navigate to work item detail: http://localhost:8000/oobc-management/work-items/6c25915a-8a99-496e-9c8b-8bb34a42979e/
2. Click the "Edit" button (opens sidebar)
3. Scroll to Budget Tracking section in sidebar

### Expected UI Elements
**Same as sidebar create, but:**
- Values are pre-filled from existing work item
- Form is in edit mode (not create mode)

### Test Cases

#### Test 4.1: Pre-filled Values in Sidebar Edit
**Steps:**
1. Open sidebar edit form
2. Verify budget values are pre-filled

**Expected Results:**
- ✅ Allocated budget pre-filled
- ✅ Actual expenditure pre-filled
- ✅ Variance calculated on load
- ✅ Color coding correct

**Screenshot Checklist:**
- [ ] Values pre-filled
- [ ] Variance calculated
- [ ] No console errors

#### Test 4.2: Real-time Calculation in Sidebar Edit
**Steps:**
1. Modify allocated budget or expenditure
2. Observe variance updates

**Expected Results:**
- ✅ Variance updates instantly
- ✅ Color changes at thresholds
- ✅ Progress bar updates smoothly
- ✅ No console errors

**Screenshot Checklist:**
- [ ] Real-time updates
- [ ] Smooth transitions
- [ ] No errors

#### Test 4.3: PPA Validation in Sidebar Edit
**Steps:**
1. Try to allocate > PPA total (if linked)
2. Verify validation

**Expected Results:**
- ✅ Error message appears
- ✅ Submit button disables
- ✅ Validation clears when corrected

**Screenshot Checklist:**
- [ ] Validation works
- [ ] Submit behavior correct

### Console Verification
- ✅ Function `calculateSidebarEditBudgetVariance()` exists
- ✅ No errors during editing
- ✅ Form submission works

---

## Test Scenario 5: JavaScript Console Check

### Setup
1. Open any page with budget tracking
2. Open Chrome DevTools (F12) → Console tab
3. Perform all budget operations

### Verification Steps

#### Step 5.1: Check Function Existence
**In Console, type:**
```javascript
typeof calculateBudgetVariance
typeof calculateSidebarCreateBudgetVariance
typeof calculateSidebarEditBudgetVariance
```

**Expected Results:**
- ✅ All should return `"function"` (not `"undefined"`)
- ✅ Functions are globally accessible

#### Step 5.2: Monitor Console During Operations
**Perform these actions while watching console:**
1. Change allocated budget
2. Change actual expenditure
3. Submit form
4. Navigate between pages

**Expected Results:**
- ✅ **NO red errors** at any point
- ✅ Warnings are OK (e.g., "Validation triggered")
- ✅ Info messages are OK (e.g., "Form submitted")
- ✅ NO "Uncaught TypeError" or "Uncaught ReferenceError"

#### Step 5.3: Test Error Handling
**In Console, try to trigger edge cases:**
```javascript
// Test division by zero (allocated = 0)
// In form, set allocated budget to 0, expenditure to 100

// Test negative values
// Set allocated to -100

// Test empty values
// Clear both fields completely
```

**Expected Results:**
- ✅ No crashes or unhandled exceptions
- ✅ Graceful handling of edge cases
- ✅ Variance shows "N/A" or "0" for invalid inputs

---

## Test Scenario 6: Form Submission Test (End-to-End)

### Objective
Verify that budget values persist across create → save → reload → edit cycle.

### Steps

#### Step 6.1: Create New Work Item with Budget
1. Navigate to PPA detail page
2. Click "Create Work Item"
3. Fill in required fields:
   - Title: "Test Budget Work Item"
   - Description: "Testing budget tracking"
   - Allocated Budget: `80000`
   - Actual Expenditure: `45000`
4. Submit form
5. Note the work item ID from success message or URL

**Expected:**
- ✅ Form submits successfully
- ✅ Redirects to work item detail page
- ✅ No console errors

#### Step 6.2: Verify Budget on Detail Page
1. On the detail page, scroll to Budget Tracking section
2. Verify values match what was entered

**Expected:**
- ✅ Allocated Budget: **₱80,000.00**
- ✅ Actual Expenditure: **₱45,000.00**
- ✅ Variance: **₱35,000.00** (green, healthy)
- ✅ Progress bar: **56.25%** (45,000 / 80,000)

#### Step 6.3: Edit Budget Values
1. Click "Edit" button (sidebar or main form)
2. Change values:
   - Allocated Budget: `90000`
   - Actual Expenditure: `85000`
3. Submit form

**Expected:**
- ✅ Form submits successfully
- ✅ Success message appears

#### Step 6.4: Verify Updated Budget
1. Refresh the page
2. Check budget values again

**Expected:**
- ✅ Allocated Budget: **₱90,000.00**
- ✅ Actual Expenditure: **₱85,000.00**
- ✅ Variance: **₱5,000.00** (amber, warning - only 5.5% remaining)
- ✅ Progress bar: **94.44%**

#### Step 6.5: Navigate Away and Return
1. Go to another page (e.g., work items list)
2. Return to work item detail
3. Verify budget values still correct

**Expected:**
- ✅ Values persist across navigation
- ✅ No data loss
- ✅ Variance recalculates correctly

---

## Expected Results Summary

### Overall Success Criteria

**✅ ALL of the following must be TRUE:**

1. **UI Elements Display Correctly**
   - [ ] Budget section appears in all 4 contexts (sidebar create, main edit, sidebar edit, detail)
   - [ ] Total PPA Budget displays when work item is linked to PPA
   - [ ] All input fields have proper labels and formatting
   - [ ] Progress bars render correctly
   - [ ] Color coding is accurate

2. **PPA Validation Works**
   - [ ] Cannot allocate > PPA total budget
   - [ ] Error message appears for over-allocation
   - [ ] Submit button disables when validation fails
   - [ ] Error clears when allocation is corrected

3. **Real-time Variance Calculation**
   - [ ] Variance updates instantly as values change
   - [ ] Color changes at correct thresholds (10%, 5%, 0%)
   - [ ] Progress bar animates smoothly
   - [ ] No lag or delay in calculations

4. **Form Submission**
   - [ ] Budget values persist after save
   - [ ] Values reload correctly on page refresh
   - [ ] Edit form pre-fills with existing values
   - [ ] No data loss during CRUD operations

5. **JavaScript Quality**
   - [ ] NO console errors (red text)
   - [ ] All functions defined and accessible
   - [ ] Event listeners attach properly
   - [ ] HTMX integration works (if used)

6. **Accessibility & UX**
   - [ ] Submit button disables during validation errors
   - [ ] Clear error messages for users
   - [ ] Visual feedback is immediate
   - [ ] Color coding is intuitive (green=good, red=bad)

7. **Edge Cases Handled**
   - [ ] Zero values don't cause errors
   - [ ] Negative values handled gracefully
   - [ ] Empty fields don't crash form
   - [ ] Very large numbers format correctly

---

## Error Reporting Template

### If Issues Found

**For each issue, document:**

1. **Test Scenario & Step**: (e.g., "Test 1.3, Step 2")
2. **Expected Behavior**: (e.g., "Variance should show ₱20,000 in green")
3. **Actual Behavior**: (e.g., "Variance shows 'NaN' with no color")
4. **Console Errors**: (copy full error message)
5. **Screenshot**: (attach screenshot showing the issue)
6. **Browser Info**: (e.g., Chrome 141.0.7390.55)
7. **Reproducible**: (Yes/No, steps to reproduce)

### Example Issue Report

```markdown
**Issue #1: Variance Calculation Broken**

- **Test**: Scenario 1, Test 1.3
- **Expected**: Variance should show "₱20,000" in green
- **Actual**: Variance shows "NaN" with no background color
- **Console Error**:
  ```
  Uncaught TypeError: Cannot read property 'toFixed' of undefined
      at calculateSidebarCreateBudgetVariance (work_item_form.js:123)
  ```
- **Screenshot**: [Attached]
- **Browser**: Chrome 141.0.7390.55 on macOS
- **Reproducible**: Yes, every time allocated budget is entered
```

---

## Testing Checklist

**Before Reporting Results, Verify:**

- [ ] All 6 test scenarios completed
- [ ] All test cases executed (at least 15+ test cases)
- [ ] Screenshots captured for each scenario
- [ ] Console checked for errors in each context
- [ ] Form submission tested end-to-end
- [ ] Both create and edit workflows tested
- [ ] PPA validation verified
- [ ] Real-time calculations verified
- [ ] Edge cases explored (zeros, negatives, empty)
- [ ] All issues documented with error messages and screenshots

---

## Final Report Format

### Budget Tracking E2E Test Results

**Date Tested**: [Date]
**Tester**: [Name]
**Browser**: Chrome [Version]
**Server**: http://localhost:8000

#### Summary
- **Total Tests**: [Number]
- **Passed**: [Number] ✅
- **Failed**: [Number] ❌
- **Pass Rate**: [Percentage]%

#### Test Results by Scenario

**Scenario 1: Sidebar Create Form**
- Test 1.1 (PPA Validation - Over): ✅ / ❌
- Test 1.2 (PPA Validation - Valid): ✅ / ❌
- Test 1.3 (Variance - Green): ✅ / ❌
- Test 1.4 (Variance - Amber): ✅ / ❌
- Test 1.5 (Variance - Red): ✅ / ❌
- Test 1.6 (Real-time): ✅ / ❌

**Scenario 2: Main Edit Form**
- [Results...]

**Scenario 3: Detail View**
- [Results...]

**Scenario 4: Sidebar Edit Form**
- [Results...]

**Scenario 5: Console Check**
- [Results...]

**Scenario 6: Form Submission**
- [Results...]

#### Issues Found
1. [Issue #1 with details]
2. [Issue #2 with details]
3. [...]

#### Screenshots
- [Attach all screenshots with labels]

#### Overall Assessment
- ✅ **PASS**: All features work as expected
- ❌ **FAIL**: Critical issues found, fixes required
- ⚠️ **PARTIAL**: Minor issues, acceptable for staging

#### Recommendations
- [Any suggestions for improvements]

---

## Notes

- **Test Duration**: Plan for ~30-45 minutes to complete all tests thoroughly
- **Prerequisites**: Ensure test data exists (PPA with budget, work items)
- **Console**: Keep DevTools open for ALL tests to catch JavaScript errors
- **Screenshots**: Use Chrome's built-in screenshot tool (Cmd+Shift+5 on Mac, or DevTools screenshot)
- **Patience**: Wait for animations and transitions to complete before verifying results

---

**Document prepared for manual testing due to Chrome DevTools MCP connection issues.**
**All tests can be performed manually following this comprehensive guide.**
