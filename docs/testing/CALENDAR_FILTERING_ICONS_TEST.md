# Calendar Event Filtering & Icons Testing Guide

**Date**: 2025-10-06
**Target**: Advanced Modern Calendar (`/oobc-management/calendar/advanced/`)
**Estimated Testing Time**: 10-15 minutes

---

## Quick Start

1. **Navigate to Advanced Modern Calendar**:
   ```
   http://localhost:8000/oobc-management/calendar/advanced/
   ```

2. **Open Browser Console** (F12 or Cmd+Option+I):
   - Required to verify debug logging
   - Look for filter-related console output

3. **Verify Initial State**:
   - All event types should be checked (Projects, Activities, Tasks, Coordination)
   - All events should be visible on calendar
   - Each event should display a type icon

---

## Test 1: Event Type Filtering ✅

### Test 1.1: Uncheck Single Type

**Steps**:
1. Open browser console (F12)
2. Uncheck "Projects" in sidebar
3. Observe console output and calendar

**Expected Console Output**:
```javascript
Filter updated: project = false
Active filters: {"project":false,"activity":true,"task":true,"coordination":true,"completed":false}
Refetching events...
Applying filters. Total events: 25
  Filtering OUT: Example Project #1 (type: project)
  Filtering OUT: Example Project #2 (type: project)
Filtered events: 20
```

**Expected Behavior**:
- [ ] All project events disappear instantly from calendar
- [ ] Other event types remain visible
- [ ] No page reload occurs
- [ ] Smooth transition (no flicker)
- [ ] Console shows correct filter state

**Actual Result**: _____________________________

---

### Test 1.2: Re-check Single Type

**Steps**:
1. Check "Projects" checkbox again
2. Observe console and calendar

**Expected Console Output**:
```javascript
Filter updated: project = true
Active filters: {"project":true,"activity":true,"task":true,"coordination":true,"completed":false}
Refetching events...
Applying filters. Total events: 25
Filtered events: 25
```

**Expected Behavior**:
- [ ] All project events reappear instantly
- [ ] Project icons visible on events
- [ ] No page reload
- [ ] Smooth transition

**Actual Result**: _____________________________

---

### Test 1.3: Uncheck Multiple Types

**Steps**:
1. Uncheck "Projects" and "Activities"
2. Only "Tasks" and "Coordination" should be checked

**Expected Console Output**:
```javascript
Filter updated: project = false
Active filters: {"project":false,"activity":false,"task":true,"coordination":true,"completed":false}
Refetching events...
Applying filters. Total events: 25
  Filtering OUT: Example Project (type: project)
  Filtering OUT: Example Activity (type: activity)
Filtered events: 10
```

**Expected Behavior**:
- [ ] Only Tasks and Coordination events visible
- [ ] Projects and Activities completely hidden
- [ ] Correct icon types shown (tasks, handshake)
- [ ] No console errors

**Actual Result**: _____________________________

---

### Test 1.4: Uncheck All Types

**Steps**:
1. Uncheck all 4 event types
2. Calendar should be empty

**Expected Behavior**:
- [ ] Calendar shows no events
- [ ] No JavaScript errors in console
- [ ] Console shows 0 filtered events
- [ ] UI remains responsive

**Expected Console Output**:
```javascript
Applying filters. Total events: 25
  Filtering OUT: [all events]
Filtered events: 0
```

**Actual Result**: _____________________________

---

### Test 1.5: Show Completed Items Toggle

**Steps**:
1. Check all event types
2. Check "Show Completed Items" checkbox
3. Uncheck it

**Expected Behavior**:
- [ ] Checking shows completed events (if any exist)
- [ ] Unchecking hides completed events
- [ ] Filter state updates correctly
- [ ] Console shows completed filter change

**Actual Result**: _____________________________

---

## Test 2: Event Icons ✅

### Test 2.1: Month View Icons

**Steps**:
1. Ensure calendar is in Month view
2. Check all event types
3. Examine each visible event

**Expected Behavior**:
- [ ] **Projects** show folder icon (📁 `fa-folder`) in blue
- [ ] **Activities** show calendar-check icon (✓ `fa-calendar-check`) in green
- [ ] **Tasks** show tasks icon (☐ `fa-tasks`) in purple
- [ ] **Coordination** show handshake icon (🤝 `fa-handshake`) in teal
- [ ] Icons appear before event title
- [ ] 4px spacing between icon and title
- [ ] Icons scale properly with text

**Actual Result**: _____________________________

**Screenshot**: _____________________________

---

### Test 2.2: Week View Icons

**Steps**:
1. Switch to Week view
2. Examine event icons

**Expected Behavior**:
- [ ] All icons visible in Week view
- [ ] Icons maintain correct colors
- [ ] No layout issues or icon overlap
- [ ] Icons visible in all-day events
- [ ] Icons visible in timed events

**Actual Result**: _____________________________

---

### Test 2.3: Day View Icons

**Steps**:
1. Switch to Day view
2. Examine event icons

**Expected Behavior**:
- [ ] All icons visible in Day view
- [ ] Icons properly aligned
- [ ] No truncation or hiding of icons

**Actual Result**: _____________________________

---

### Test 2.4: Year View Icons

**Steps**:
1. Switch to Year view (multi-month)
2. Zoom in on events if needed

**Expected Behavior**:
- [ ] Icons visible (may be small)
- [ ] No layout breaking in year view
- [ ] Events remain clickable

**Actual Result**: _____________________________

---

## Test 3: Integration Testing ✅

### Test 3.1: Filter + Icon Combination

**Steps**:
1. Uncheck "Projects" and "Activities"
2. Verify only Tasks and Coordination visible
3. Examine icons on remaining events

**Expected Behavior**:
- [ ] Only task icons (☐) and handshake icons (🤝) visible
- [ ] No folder or calendar-check icons shown
- [ ] Icons correctly match filtered event types
- [ ] Console shows correct filtering

**Actual Result**: _____________________________

---

### Test 3.2: Event Click with Icons

**Steps**:
1. Click on an event with an icon
2. Verify detail panel opens

**Expected Behavior**:
- [ ] Event click still works (icons don't block clicks)
- [ ] Detail panel opens on right side
- [ ] Event details display correctly
- [ ] "View Full Details" button functional

**Actual Result**: _____________________________

---

### Test 3.3: Calendar Navigation with Filters

**Steps**:
1. Uncheck "Projects"
2. Click "Next" button to navigate to next month
3. Click "Previous" button
4. Click "Today" button

**Expected Behavior**:
- [ ] Filters persist during navigation
- [ ] Project events remain hidden after navigation
- [ ] Icons remain visible on all pages
- [ ] No console errors during navigation

**Actual Result**: _____________________________

---

## Test 4: Responsive Testing ✅

### Test 4.1: Mobile View (< 1024px)

**Steps**:
1. Resize browser to 768px width (tablet)
2. Open sidebar (hamburger menu)
3. Toggle filters
4. Examine icons

**Expected Behavior**:
- [ ] Sidebar opens as overlay
- [ ] Filters work correctly on mobile
- [ ] Icons visible and properly sized
- [ ] No horizontal scrolling
- [ ] Touch-friendly checkbox targets

**Actual Result**: _____________________________

---

### Test 4.2: Desktop View (> 1024px)

**Steps**:
1. Resize to full desktop width
2. Toggle sidebar collapse
3. Verify filters and icons

**Expected Behavior**:
- [ ] Sidebar collapse/expand smooth
- [ ] Calendar resizes correctly
- [ ] Icons remain visible after resize
- [ ] Filters work in collapsed sidebar

**Actual Result**: _____________________________

---

## Test 5: Performance Testing ✅

### Test 5.1: Large Dataset

**Steps**:
1. Load calendar with 50+ events
2. Toggle filters rapidly (on/off 5 times)
3. Observe console and performance

**Expected Behavior**:
- [ ] Filtering completes in < 100ms
- [ ] No lag or stutter
- [ ] Icons render quickly (< 50ms)
- [ ] Console logs not overwhelming
- [ ] No memory leaks (check DevTools Memory tab)

**Actual Result**: _____________________________

---

### Test 5.2: View Switching

**Steps**:
1. Switch between Month → Week → Day → Year → Month
2. With filters active (some unchecked)
3. Monitor console performance

**Expected Behavior**:
- [ ] View switches smooth (< 300ms)
- [ ] Icons re-render correctly
- [ ] Filters persist across views
- [ ] No duplicate event rendering
- [ ] Console shows correct event counts

**Actual Result**: _____________________________

---

## Test 6: Edge Cases ✅

### Test 6.1: No Events Scenario

**Steps**:
1. Navigate to a month with 0 events
2. Toggle filters

**Expected Behavior**:
- [ ] No JavaScript errors
- [ ] Console shows "Total events: 0"
- [ ] Calendar displays empty state
- [ ] Filters still toggleable

**Actual Result**: _____________________________

---

### Test 6.2: Events Without Work Type

**Steps**:
1. If events exist without `work_type` property
2. Verify they display correctly

**Expected Behavior**:
- [ ] Events without icons still render
- [ ] No console errors about missing icons
- [ ] Fallback background color applies
- [ ] Event clickable and functional

**Actual Result**: _____________________________

---

### Test 6.3: Browser Refresh

**Steps**:
1. Uncheck some filters
2. Refresh page (F5 or Cmd+R)
3. Check filter state

**Expected Behavior**:
- [ ] Filters reset to default (all checked)
- [ ] All events visible after refresh
- [ ] Icons render correctly
- [ ] No errors in fresh console

**Actual Result**: _____________________________

---

## Test 7: Accessibility ✅

### Test 7.1: Keyboard Navigation

**Steps**:
1. Use Tab key to navigate sidebar
2. Use Space/Enter to toggle checkboxes
3. Navigate calendar with arrow keys

**Expected Behavior**:
- [ ] Checkboxes focusable with Tab
- [ ] Space/Enter toggles checkboxes
- [ ] Focus indicators visible
- [ ] Filters work via keyboard
- [ ] No keyboard traps

**Actual Result**: _____________________________

---

### Test 7.2: Screen Reader (Optional)

**Steps**:
1. Enable VoiceOver (Mac) or NVDA (Windows)
2. Navigate filter checkboxes
3. Listen for announcements

**Expected Behavior**:
- [ ] Checkboxes announced correctly
- [ ] Filter state changes announced
- [ ] Event count changes announced (via ARIA live region)
- [ ] Icons have appropriate alt text or ARIA labels

**Actual Result**: _____________________________

---

## Test 8: Console Verification ✅

### Test 8.1: Debug Logging Check

**Steps**:
1. Open console before any interaction
2. Uncheck "Projects"
3. Verify exact console output

**Expected Messages**:
```javascript
Filter updated: project = false
Active filters: {"project":false,"activity":true,"task":true,"coordination":true,"completed":false}
Refetching events...
Applying filters. Total events: [number]
  Filtering OUT: [event title] (type: project)
Filtered events: [reduced number]
```

**Checklist**:
- [ ] All expected log messages appear
- [ ] Filter state JSON correct
- [ ] Event titles logged correctly
- [ ] Event counts accurate
- [ ] No unexpected errors
- [ ] No warnings about deprecated APIs

**Actual Result**: _____________________________

---

## Test Summary

**Total Tests**: 23 test scenarios
**Tests Passed**: ___ / 23
**Tests Failed**: ___ / 23
**Tests Skipped**: ___ / 23

---

## Issues Found

**Issue #1**:
- **Description**: _____________________________
- **Severity**: Critical / High / Medium / Low
- **Steps to Reproduce**: _____________________________
- **Expected**: _____________________________
- **Actual**: _____________________________
- **Screenshot/Console Log**: _____________________________

**Issue #2**:
- **Description**: _____________________________
- **Severity**: Critical / High / Medium / Low
- **Steps to Reproduce**: _____________________________
- **Expected**: _____________________________
- **Actual**: _____________________________
- **Screenshot/Console Log**: _____________________________

---

## Browser Compatibility

| Browser | Version | Filtering Works | Icons Display | Notes |
|---------|---------|----------------|---------------|-------|
| Chrome | _____ | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | _____ |
| Firefox | _____ | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | _____ |
| Safari | _____ | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | _____ |
| Edge | _____ | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | _____ |
| Mobile Safari | _____ | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | _____ |
| Chrome Android | _____ | ☐ Pass ☐ Fail | ☐ Pass ☐ Fail | _____ |

---

## Final Verification

**Deployment Readiness**:
- [ ] All critical tests pass
- [ ] No console errors (except debug logs)
- [ ] Icons visible in all views
- [ ] Filters work instantly
- [ ] Smooth transitions (no flicker)
- [ ] Mobile responsive
- [ ] Keyboard accessible
- [ ] Performance acceptable (< 100ms filter time)

**Recommendation**: ☐ Ready for Production | ☐ Needs Fixes | ☐ More Testing Required

---

## Notes

_Add any additional observations, concerns, or recommendations here:_

---

**Tested By**: _____________________________
**Date**: _____________________________
**Environment**: ☐ Development | ☐ Staging | ☐ Production
**Database**: ☐ SQLite | ☐ PostgreSQL
**Event Count**: _____ events in test dataset
