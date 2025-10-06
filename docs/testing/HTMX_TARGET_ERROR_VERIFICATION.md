# HTMX Target Error Verification Guide

**Date:** 2025-10-06
**Component:** Work Items Hierarchical Tree View
**Fix Reference:** [HTMX_TARGET_ERROR_FIX.md](../improvements/UI/HTMX_TARGET_ERROR_FIX.md)

---

## Quick Verification Checklist

Use this checklist to verify the HTMX target error fix is working correctly.

---

## Prerequisites

1. **Start Development Server:**
   ```bash
   cd src
   python manage.py runserver
   ```

2. **Open Work Items List:**
   - Navigate to: `http://localhost:8000/oobc-management/work-items/`
   - Ensure you have work items with children (sub-items)

3. **Open Browser Console:**
   - Chrome/Edge: `F12` → Console tab
   - Firefox: `F12` → Console tab
   - Safari: `Cmd+Option+C`

---

## Test Cases

### Test 1: Single Expand (Baseline)

**Steps:**
1. Find a work item with children (shows children count badge)
2. Click the expand button (chevron icon) **once**
3. Observe the behavior

**Expected Results:**
- ✅ Chevron rotates to down position immediately (< 50ms)
- ✅ Skeleton loading row appears briefly
- ✅ Children rows load and display
- ✅ Placeholder row is removed
- ✅ Console shows initialization message
- ✅ NO errors in console

**Console Output:**
```
✅ Work Items tree navigation initialized with optimistic UI updates (< 50ms instant feedback)
🔒 HTMX "click once" trigger enabled - prevents duplicate requests for already-loaded children
```

---

### Test 2: Rapid Double Click (HTMX Protection)

**Steps:**
1. Find an unexpanded work item with children
2. Click the expand button **twice rapidly** (within 100ms)
3. Check browser Network tab and Console

**Expected Results:**
- ✅ Only **ONE** HTMX request fires (check Network tab)
- ✅ Second click is ignored by HTMX ("click once" trigger)
- ✅ Children load normally
- ✅ NO console errors
- ✅ NO `htmx:targetError` events

**How to Verify:**
- Open Network tab (F12 → Network)
- Filter by XHR/Fetch
- Look for `work_item_tree_partial` requests
- Should see **only 1 request**, not 2

---

### Test 3: Expand → Collapse → Expand (JavaScript Toggle)

**Steps:**
1. Expand a work item (children load via HTMX)
2. Click the same button again to **collapse** children
3. Click the same button again to **expand** children
4. Check Network tab

**Expected Results:**
- ✅ First expand: HTMX request fires
- ✅ Collapse: Instant (JavaScript only, NO HTMX request)
- ✅ Second expand: Instant (JavaScript only, NO HTMX request)
- ✅ Smooth transitions (300ms)
- ✅ NO console errors
- ✅ Console may show: "Preventing duplicate request - children already loaded"

**Network Tab:**
- Should show **only 1 request** (the initial load)
- Collapse and subsequent expands use NO network requests

---

### Test 4: Multiple Rapid Clicks Before Load (State Protection)

**Steps:**
1. Find an unexpanded work item with children
2. Click expand button **5 times rapidly** before children finish loading
3. Observe behavior

**Expected Results:**
- ✅ Only **ONE** HTMX request fires
- ✅ Console shows: "Preventing duplicate request - children already loaded"
- ✅ Children load normally once
- ✅ NO target errors
- ✅ UI remains stable

**Console Output:**
```
Preventing duplicate request - children already loaded for item: <item-id>
```

---

### Test 5: Expand All Button

**Steps:**
1. Ensure you have multiple work items with children
2. Click the "Expand All" button in the tree controls
3. Observe all items expanding

**Expected Results:**
- ✅ All items expand sequentially (100ms delay between each)
- ✅ Expand All icon spins briefly (500ms)
- ✅ All children load successfully
- ✅ NO console errors
- ✅ NO target errors

**Network Tab:**
- One request per top-level item with children
- No duplicate requests

---

### Test 6: Collapse All Button

**Steps:**
1. After expanding all items (Test 5)
2. Click "Collapse All" button
3. Click "Expand All" again

**Expected Results:**
- ✅ All items collapse instantly (JavaScript only)
- ✅ Second "Expand All" uses NO HTMX requests (children already loaded)
- ✅ Instant expansion (< 50ms per item)
- ✅ NO console errors

**Network Tab:**
- Zero requests on collapse
- Zero requests on second expand all

---

### Test 7: Console Error Check (Critical)

**Steps:**
1. Perform all above tests
2. Review browser console for any errors

**Expected Results:**
- ✅ NO `❌ HTMX Target Error:` messages
- ✅ NO red error messages
- ✅ Only green success messages and info logs

**FAIL Criteria:**
- ❌ ANY `htmx:targetError` in console
- ❌ ANY red error messages related to HTMX
- ❌ ANY missing element errors

---

## Advanced Verification

### Network Request Analysis

**Open Network Tab → XHR/Fetch Filter**

For each expanded work item, verify:
- **Request URL:** Contains `work_item_tree_partial/<id>/`
- **Request Count:** Exactly **1 request per item** (never more)
- **Response Status:** 200 OK
- **Response Time:** Typically < 200ms

### State Tracking Verification

**Open Browser Console → Type:**
```javascript
// This won't work as itemStates is inside IIFE, but you can check logs
// The logs will confirm state management is working
```

**Look for logs like:**
```
Preventing duplicate request - children already loaded for item: <uuid>
```

This confirms state tracking is working correctly.

---

## Troubleshooting

### Issue: Still seeing target errors

**Possible Causes:**
1. Browser cache not cleared
2. Old JavaScript loaded
3. Template changes not reflected

**Fix:**
```bash
# Hard refresh browser
Ctrl+Shift+R (Chrome/Firefox)
Cmd+Shift+R (Mac)

# Clear Django static cache
cd src
python manage.py collectstatic --noinput --clear
```

---

### Issue: Children load multiple times

**Check:**
1. Network tab shows multiple requests?
2. Console shows "Preventing duplicate request" message?

**Fix:**
- Verify `hx-trigger="click once"` is in the button template
- Check browser console for JavaScript errors
- Ensure latest code is deployed

---

### Issue: Console shows "Target element does not exist"

**This is EXPECTED and HANDLED:**
- The error is caught by `htmx:beforeRequest` safety check
- Request is prevented with `event.preventDefault()`
- Console shows warning but no red error
- UI remains stable

**This is working correctly!**

---

## Performance Metrics

**Measure these during testing:**

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Chevron rotation time | < 50ms | Visual observation |
| Skeleton appearance | < 50ms | Visual observation |
| Children load time | < 300ms | Network tab (Time column) |
| Collapse speed | < 50ms | Visual observation (instant) |
| Duplicate requests | 0 | Network tab (Count) |
| Console errors | 0 | Console tab (Red messages) |

---

## Sign-Off Checklist

Before marking as verified, confirm:

- [ ] Test 1: Single expand works smoothly
- [ ] Test 2: Rapid double click shows only 1 request
- [ ] Test 3: Expand → Collapse → Expand is instant after first load
- [ ] Test 4: Multiple rapid clicks show "Preventing duplicate" log
- [ ] Test 5: Expand All works without errors
- [ ] Test 6: Collapse All and re-expand is instant
- [ ] Test 7: Console shows ZERO red errors
- [ ] Network tab confirms 1 request per item maximum
- [ ] Performance metrics meet targets
- [ ] UI feels smooth and responsive

---

## Expected Console Output (Full Session)

**On Page Load:**
```
✅ Work Items tree navigation initialized with optimistic UI updates (< 50ms instant feedback)
🔒 HTMX "click once" trigger enabled - prevents duplicate requests for already-loaded children
```

**On First Expand:**
```
(No console output - silent success)
```

**On Second Click (if user tries to expand again):**
```
Preventing duplicate request - children already loaded for item: f44df647-fd42-455a-ab36-537253f8d769
```

**On Error Recovery (rare, handled gracefully):**
```
❌ HTMX Target Error: {error: "htmx:targetError", ...}
Reverted optimistic UI for item: f44df647-fd42-455a-ab36-537253f8d769
```

---

## Status

**Test Date:** _____________
**Tester Name:** _____________
**Result:** ☐ PASS  ☐ FAIL
**Notes:**

---

## Related Documents

- [HTMX Target Error Fix](../improvements/UI/HTMX_TARGET_ERROR_FIX.md) - Technical implementation details
- [Instant UI Improvements](../improvements/instant_ui_improvements_plan.md) - Overall UI strategy
- [Work Items User Guide](../USER_GUIDE_PROJECT_MANAGEMENT.md) - End user documentation

---

**Verification Status:** ⏳ PENDING VERIFICATION

**Next Steps:**
1. Run all 7 test cases
2. Verify zero console errors
3. Confirm network request counts
4. Mark as verified in this document
