# Calendar Critical Fixes - Verification Guide

**Date:** 2025-10-06
**Status:** Ready for Testing
**Priority:** CRITICAL
**Estimated Testing Time:** 15 minutes

---

## Overview

This guide helps you verify the two critical calendar fixes:

1. **Calendar Expansion After Sidebar Close** ✅
2. **Deleted Events Disappearing Immediately** ✅

---

## Pre-Testing Setup

### 1. Environment Requirements
- Development server running (`./manage.py runserver`)
- Browser with Developer Console (Chrome, Firefox, Safari)
- At least 5-10 work items in the database
- User account with permission to create/edit/delete work items

### 2. Navigate to Calendar
```
URL: http://localhost:8000/oobc-management/calendar/advanced/
```

### 3. Open Browser Console
- **Chrome/Firefox:** Press `F12` or `Ctrl+Shift+J` (Windows) / `Cmd+Option+J` (Mac)
- **Safari:** `Cmd+Option+C`

### 4. Verify Debug Mode
Type in console:
```javascript
window.debugCalendar()
```

**Expected Output:**
```
📊 Calendar Debug State: {
  initialized: true,
  view: "dayGridMonth",
  eventCount: 23,
  calendarContainer: "calendar-container",
  detailPanel: "calendar-detail-panel",
  ...
}
```

✅ If you see this, debug mode is working.

---

## Test 1: Calendar Expansion After Sidebar Close

### Test Steps

#### 1.1 Open Event Sidebar
- [ ] Click any event on the calendar
- [ ] **Expected:** Sidebar slides in from right (300ms animation)
- [ ] **Expected:** Calendar shrinks to make room
- [ ] **Expected:** Edit form loads in sidebar

**Visual Check:**
- Calendar width should reduce (approximately 380px narrower)
- No layout jumps or glitches
- Sidebar should be 380px wide

#### 1.2 Close Sidebar (X Button)
- [ ] Click the **X button** in sidebar header
- [ ] **Expected:** Sidebar slides out to right (300ms animation)
- [ ] **Expected:** Calendar expands back to full width
- [ ] **Expected:** Calendar resizes properly (no overflow)

**Console Check:**
```
Closing detail panel...
Resizing calendar after sidebar close
```

**Visual Check:**
- Calendar should smoothly expand to full width
- No white space on the right
- Calendar events should be properly sized

#### 1.3 Close Sidebar (Backdrop Click)
- [ ] Click event again to open sidebar
- [ ] Click the **dark backdrop area** (outside sidebar)
- [ ] **Expected:** Same behavior as X button

**Visual Check:**
- Smooth expansion
- Proper calendar sizing

#### 1.4 Close Sidebar (Cancel Button)
- [ ] Click event again to open sidebar
- [ ] Click the **Cancel button** in edit form
- [ ] **Expected:** Sidebar loads detail view
- [ ] Click **X button** to close
- [ ] **Expected:** Calendar expands properly

---

## Test 2: Deleted Events Disappearing Immediately

### Test Steps

#### 2.1 Prepare for Delete Test
- [ ] Note the total number of events on calendar
- [ ] Choose an event to delete (pick one that's easy to spot)
- [ ] Note the event title and color

**Console Check:**
```javascript
window.debugCalendar()
// Note the eventCount value
```

#### 2.2 Delete Event
- [ ] Click the event to open sidebar
- [ ] Scroll to bottom of edit form
- [ ] Click **Delete button** (red button)
- [ ] **Expected:** Confirmation dialog appears

**Dialog Text:**
```
⚠️ Delete 'Event Title'?

This action cannot be undone. The work item and all its data will be permanently deleted.

Click OK to confirm deletion.
```

- [ ] Click **OK**

#### 2.3 Verify Immediate Deletion
- [ ] **Expected:** Sidebar closes smoothly (300ms)
- [ ] **Expected:** Success toast appears: "Work item deleted successfully"
- [ ] **Expected:** Event **disappears from calendar IMMEDIATELY**
- [ ] **Expected:** NO page refresh occurs
- [ ] **Expected:** Calendar is full width

**Console Check:**
```
Delete successful, refreshing UI...
Refetching calendar events...
📅 Calendar feed loaded: 22 events (cache-buster: 1728234598123)
```

**Visual Check:**
- Event should vanish from calendar
- Calendar should be full width
- No stale data (old event still visible)
- Total event count reduced by 1

#### 2.4 Verify Cache-Busting
- [ ] Open browser **Network tab**
- [ ] Click another event
- [ ] Click Delete → Confirm
- [ ] **Expected:** New request to `/work-items/calendar/feed/?_=<timestamp>`
- [ ] **Expected:** Timestamp is different each time

**Network Tab Check:**
```
Request URL: /oobc-management/work-items/calendar/feed/?_=1728234567890
Status: 200 OK
Cache-Control: no-store
```

#### 2.5 Verify No Page Refresh
- [ ] Scroll calendar to a specific date
- [ ] Delete another event
- [ ] **Expected:** Calendar stays on same date (no scroll jump)
- [ ] **Expected:** Event disappears instantly
- [ ] **Expected:** Page URL doesn't change

---

## Test 3: Multiple Operations in Sequence

### Test Steps

#### 3.1 Delete → Create → Duplicate
- [ ] Delete an event (verify it disappears)
- [ ] Click "Create Work Item" button
- [ ] Create a new event (any details)
- [ ] Save the new event
- [ ] **Expected:** New event appears on calendar immediately
- [ ] Click the new event
- [ ] Click **Duplicate** button
- [ ] **Expected:** Duplicate created with " (Copy)" suffix
- [ ] **Expected:** Both events visible on calendar

**Console Check:**
```
🔄 Calendar refresh event triggered: {eventId: "123"}
📅 Calendar feed loaded: 23 events (cache-buster: ...)
```

#### 3.2 Rapid Deletions
- [ ] Delete 3 events in quick succession
- [ ] **Expected:** Each deletion triggers calendar refresh
- [ ] **Expected:** All 3 events disappear
- [ ] **Expected:** No duplicates or stale data

---

## Test 4: Edge Cases

### Test 4.1 Delete Last Event in View
- [ ] Switch to **Day view** or **Week view**
- [ ] Navigate to a date with only 1 event
- [ ] Delete that event
- [ ] **Expected:** Calendar shows empty state
- [ ] **Expected:** No errors in console

### Test 4.2 Delete While Filtering
- [ ] Enable event type filters (sidebar)
- [ ] Uncheck "Projects" (hide project events)
- [ ] Delete a visible activity event
- [ ] **Expected:** Event disappears
- [ ] **Expected:** Filters remain active
- [ ] Re-check "Projects"
- [ ] **Expected:** Projects reappear (but deleted one is gone)

### Test 4.3 Delete in Different Views
- [ ] Delete event in **Month view** → Verify disappears
- [ ] Switch to **Week view** → Verify still gone
- [ ] Switch to **Day view** → Verify still gone
- [ ] Switch to **Year view** → Verify still gone

---

## Test 5: Desktop & Mobile Responsiveness

### Desktop (1920x1080)
- [ ] Calendar expands properly on sidebar close
- [ ] Deleted events disappear immediately
- [ ] No layout issues

### Tablet (768x1024)
- [ ] Sidebar opens as overlay
- [ ] Backdrop appears
- [ ] Delete works correctly
- [ ] Calendar stays full width

### Mobile (375x667)
- [ ] Sidebar opens full screen
- [ ] Delete works correctly
- [ ] No horizontal scroll

---

## Expected Console Output Summary

### On Page Load
```
✅ Calendar debug mode enabled. Use window.debugCalendar() to inspect state.
📅 Calendar feed loaded: 23 events (cache-buster: 1728234567890)
```

### On Event Click
```
Loading work item editor...
```

### On Sidebar Close
```
Closing detail panel...
Resizing calendar after sidebar close
```

### On Delete
```
Delete successful, refreshing UI...
Refetching calendar events...
📅 Calendar feed loaded: 22 events (cache-buster: 1728234598123)
```

### On Duplicate
```
🔄 Calendar refresh event triggered: {eventId: "123"}
📅 Calendar feed loaded: 24 events (cache-buster: ...)
```

---

## Common Issues & Solutions

### Issue: Calendar Doesn't Expand
**Symptom:** Sidebar closes but calendar stays compressed

**Check:**
```javascript
window.debugCalendar()
// Look at calendarContainer class
```

**Expected:** `calendarContainer: "calendar-container"`
**Problem:** `calendarContainer: "calendar-container detail-open"`

**Solution:**
- Check browser console for errors
- Verify `closeDetailPanel()` is being called
- Check CSS transitions are enabled

### Issue: Deleted Event Still Visible
**Symptom:** Event doesn't disappear after deletion

**Check Network Tab:**
- Is new request being made?
- Is cache-buster parameter present?
- Is response returning correct data?

**Check Console:**
- Do you see "Refetching calendar events..."?
- Is event count decreasing?

**Solution:**
- Hard refresh browser (`Ctrl+Shift+R` or `Cmd+Shift+R`)
- Clear browser cache
- Verify DELETE request returns 204 status

### Issue: No Console Logs
**Symptom:** Console is silent

**Check:**
- Console filter level (should be "All" not "Errors only")
- Console is cleared (`console.clear()`)

**Solution:**
```javascript
window.debugCalendar()
// This should always work if calendar is initialized
```

---

## Success Criteria Checklist

### Calendar Expansion ✅
- [ ] Sidebar closes smoothly (300ms animation)
- [ ] Calendar expands to full width
- [ ] No layout glitches or jumps
- [ ] Calendar resizes properly
- [ ] Works with X button, backdrop, and cancel

### Delete Refresh ✅
- [ ] Deleted events disappear immediately
- [ ] No page refresh required
- [ ] Success toast appears
- [ ] Calendar stays full width
- [ ] Cache-busting prevents stale data
- [ ] Works across all calendar views

### Debug Mode ✅
- [ ] `window.debugCalendar()` works
- [ ] Console logs are helpful
- [ ] No errors in console

### Overall UX ✅
- [ ] Interactions feel instant
- [ ] No flicker or flash
- [ ] Smooth animations
- [ ] Reliable behavior
- [ ] Works on desktop, tablet, mobile

---

## Reporting Issues

If you encounter any issues:

1. **Open Browser Console:** Note all errors
2. **Run Debug Command:** `window.debugCalendar()`
3. **Check Network Tab:** Look for failed requests
4. **Take Screenshot:** Capture the issue
5. **Report with Details:**
   - What you did (steps to reproduce)
   - What you expected
   - What actually happened
   - Console output
   - Network requests
   - Screenshot

---

## Next Steps After Verification

### If All Tests Pass ✅
1. Document test results
2. Deploy to staging environment
3. Run UAT (User Acceptance Testing)
4. Deploy to production

### If Tests Fail ❌
1. Document failing tests
2. Review implementation
3. Check for JavaScript errors
4. Verify HTMX responses
5. Re-test after fixes

---

## Quick Test (5 Minutes)

**Minimal verification for rapid testing:**

1. Open calendar: `/oobc-management/calendar/advanced/`
2. Click event → Sidebar opens → Calendar shrinks ✅
3. Click X → Sidebar closes → **Calendar expands to full width** ✅
4. Click event → Click Delete → Confirm
5. **Event disappears immediately** ✅
6. No page refresh ✅
7. Success toast appears ✅

**Done!** If these 7 checks pass, the fixes are working.

---

**Related Documentation:**
- [Implementation Details](../improvements/UI/CALENDAR_CRITICAL_FIXES_IMPLEMENTATION.md)
- [Calendar Architecture](../improvements/UI/CALENDAR_ARCHITECTURE_SUMMARY.md)
- [Instant UI Guide](../improvements/instant_ui_improvements_plan.md)
