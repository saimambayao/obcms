# Calendar Inline Editing: Quick Test Guide

**5-Minute Verification Checklist**

## Setup
1. Start Django development server: `cd src && python manage.py runserver`
2. Login as a user with work items
3. Navigate to calendar view: `/oobc-management/calendar/`

## Test 1: Basic Inline Editing (Most Important)
**Expected: Edit form loads immediately on event click**

1. Click any calendar event
2. ✅ **PASS:** Edit form appears immediately (no detail view first)
3. ✅ **PASS:** Header says "Edit Event" with edit icon
4. ✅ **PASS:** "View Details" button visible in top-right
5. ✅ **PASS:** All form fields populated with current values

**Result:** PASS / FAIL

---

## Test 2: Save Changes
**Expected: Changes save and calendar refreshes**

1. Click calendar event → Edit form opens
2. Change title field (e.g., add "UPDATED" suffix)
3. Click "Save Changes" button
4. ✅ **PASS:** Loading spinner appears briefly
5. ✅ **PASS:** Detail view appears after save
6. ✅ **PASS:** Success toast notification appears
7. ✅ **PASS:** Calendar event updates with new title

**Result:** PASS / FAIL

---

## Test 3: View Details Toggle
**Expected: Toggle between edit form and detail view**

1. Click calendar event → Edit form opens
2. Click "View Details" button in top-right
3. ✅ **PASS:** Detail view (read-only) appears
4. ✅ **PASS:** "Edit" button visible (if user has permission)
5. Click "Edit" button
6. ✅ **PASS:** Edit form appears again

**Result:** PASS / FAIL

---

## Test 4: Cancel Button
**Expected: Cancel returns to detail view without saving**

1. Click calendar event → Edit form opens
2. Change title field (don't save)
3. Click "Cancel" button
4. ✅ **PASS:** Detail view appears
5. ✅ **PASS:** Changes NOT saved (original title shown)
6. ✅ **PASS:** Calendar event unchanged

**Result:** PASS / FAIL

---

## Test 5: Permission Handling
**Expected: Read-only users see detail view, not edit form**

### Setup: Test with different user types

#### A. Owner/Assigned User (Should Edit)
1. Login as work item owner or assigned user
2. Click their calendar event
3. ✅ **PASS:** Edit form appears immediately

#### B. Read-Only User (Should View)
1. Login as user without edit permission
2. Click someone else's calendar event
3. ✅ **PASS:** Detail view appears (NOT edit form)
4. ✅ **PASS:** No "Edit" button shown

**Result:** PASS / FAIL

---

## Test 6: Form Validation
**Expected: Validation errors display correctly**

1. Click calendar event → Edit form opens
2. Clear required "Title" field (make it empty)
3. Click "Save Changes"
4. ✅ **PASS:** Error message appears below title field
5. ✅ **PASS:** Form NOT submitted
6. ✅ **PASS:** Edit form remains visible (not switched to detail view)

**Result:** PASS / FAIL

---

## Test 7: Loading States
**Expected: Loading indicators during HTMX requests**

1. Click calendar event
2. ✅ **PASS:** Loading spinner appears with "Loading..." text
3. ✅ **PASS:** Edit form replaces spinner
4. Change a field and click "Save Changes"
5. ✅ **PASS:** "Save Changes" button disables during save
6. ✅ **PASS:** "Saving..." indicator appears

**Result:** PASS / FAIL

---

## Test 8: Mobile Responsiveness
**Expected: Works on mobile screens**

1. Resize browser to mobile width (375px)
2. Click calendar event
3. ✅ **PASS:** Edit form fits mobile screen
4. ✅ **PASS:** "View Details" button doesn't wrap/overflow
5. ✅ **PASS:** Form fields are touch-friendly (min 44px height)
6. ✅ **PASS:** Save/Cancel buttons stacked on mobile

**Result:** PASS / FAIL

---

## Test 9: Keyboard Navigation
**Expected: Full keyboard accessibility**

1. Click calendar event → Edit form opens
2. ✅ **PASS:** Focus automatically on first input field
3. Press Tab key repeatedly
4. ✅ **PASS:** Tab order: Title → Status → Priority → Dates → Progress → Description → Assignees → Save → Cancel → View Details
5. Press Escape key
6. ✅ **PASS:** Detail panel closes (optional - may not be implemented)

**Result:** PASS / FAIL

---

## Test 10: Edge Cases
**Expected: Graceful error handling**

#### A. Network Error Simulation
1. Open browser DevTools → Network tab
2. Set throttling to "Offline"
3. Click calendar event
4. ✅ **PASS:** Error message appears (not blank screen)

#### B. Invalid Work Item
1. Manually navigate to: `/oobc-management/work-items/99999/sidebar/edit/`
2. ✅ **PASS:** 404 error page or error message (not crash)

**Result:** PASS / FAIL

---

## Summary

**Total Tests:** 10
**Tests Passed:** _____ / 10
**Overall Status:** PASS / FAIL

### Critical Failures (Must Fix)
- [ ] Test 1: Basic inline editing
- [ ] Test 2: Save changes
- [ ] Test 5: Permission handling

### Important Failures (Should Fix)
- [ ] Test 3: View details toggle
- [ ] Test 4: Cancel button
- [ ] Test 6: Form validation

### Nice-to-Have Failures (Can Fix Later)
- [ ] Test 7: Loading states
- [ ] Test 8: Mobile responsiveness
- [ ] Test 9: Keyboard navigation
- [ ] Test 10: Edge cases

---

## Quick Rollback (If Tests Fail)

If critical tests fail, revert these files:

```bash
cd /Users/saidamenmambayao/Library/Mobile\ Documents/com~apple~CloudDocs/BTA/OOBC/obcms

# Restore from git
git checkout src/templates/common/calendar_advanced_modern.html
git checkout src/templates/common/partials/calendar_event_edit_form.html
git checkout src/common/views/work_items.py

# Restart server
cd src && python manage.py runserver
```

---

## Browser Console Debugging

**If tests fail, check browser console for errors:**

```javascript
// Expected console logs (no errors)
htmx.ajax GET /oobc-management/work-items/123/sidebar/edit/  ✅
htmx.ajax POST /oobc-management/work-items/123/sidebar/edit/ ✅

// Common errors to watch for:
404 Not Found → URL pattern incorrect
403 Forbidden → Permission issue
500 Server Error → Backend crash (check Django logs)
```

**Django logs location:** `src/logs/django.log`

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Mark todos as complete
2. Document in release notes
3. Deploy to staging environment
4. User acceptance testing (UAT)

### If Tests Fail ❌
1. Review failed test details
2. Check browser console for errors
3. Check Django logs for backend errors
4. Debug specific issue
5. Re-run failed tests after fix

---

**Testing Completed By:** _______________
**Date:** _______________
**Environment:** Development / Staging / Production
