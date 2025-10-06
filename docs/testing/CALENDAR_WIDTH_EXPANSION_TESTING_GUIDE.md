# Calendar Width Expansion Testing Guide

**Date:** 2025-10-06
**Component:** Advanced Modern Calendar
**File:** `src/templates/common/calendar_advanced_modern.html`
**Status:** Testing & Verification

---

## Overview

This guide provides comprehensive testing procedures for the calendar width expansion functionality. The calendar should smoothly expand to full width when the sidebar is collapsed on desktop, and maintain proper mobile overlay behavior.

---

## Architecture Summary

### Desktop Behavior (viewport ≥ 1024px)

**Grid Layout System:**
```css
/* Default (sidebar visible) */
grid-template-columns: 280px 1fr 0px;

/* Collapsed (sidebar hidden) */
grid-template-columns: 0px 1fr 0px;
```

**Icon States:**
- **Chevron Left (←)**: Sidebar visible, click to collapse
- **Chevron Right (→)**: Sidebar hidden, click to expand

**Animation:**
- 300ms smooth transition on grid column changes
- Calendar resizes after 350ms delay (to allow grid transition to complete)

### Mobile Behavior (viewport < 1024px)

**Overlay System:**
- Sidebar uses `position: fixed` and slides in from left
- Calendar always fills full width
- Backdrop overlay appears behind sidebar

**Icon States:**
- **Bars (☰)**: Sidebar closed, click to open
- **Times (×)**: Sidebar open, click to close

---

## Testing Checklist

### 1. Desktop Width Expansion (≥ 1024px)

#### Initial Load
- [ ] Sidebar is visible (280px width)
- [ ] Calendar fills remaining space
- [ ] Icon shows chevron-left (←)
- [ ] No console errors

**Expected Grid Columns:** `280px 1fr 0px`

#### After Clicking Toggle (First Click)
- [ ] Sidebar slides out smoothly (300ms transition)
- [ ] Calendar expands to full width
- [ ] Icon changes to chevron-right (→)
- [ ] `calendar.updateSize()` is called
- [ ] No layout shift or flicker

**Expected Grid Columns:** `0px 1fr 0px`

#### After Clicking Toggle Again (Second Click)
- [ ] Sidebar slides back in smoothly (300ms transition)
- [ ] Calendar contracts to original width
- [ ] Icon changes back to chevron-left (←)
- [ ] `calendar.updateSize()` is called
- [ ] Calendar events remain properly positioned

**Expected Grid Columns:** `280px 1fr 0px`

### 2. Mobile Overlay Behavior (< 1024px)

#### Initial Load
- [ ] Sidebar is hidden off-screen
- [ ] Calendar fills full viewport width
- [ ] Icon shows bars (☰)
- [ ] No sidebar backdrop visible

#### After Clicking Toggle (Open)
- [ ] Sidebar slides in from left
- [ ] Backdrop appears with opacity transition
- [ ] Icon changes to times (×)
- [ ] Calendar remains full width behind overlay

#### After Clicking Toggle Again (Close)
- [ ] Sidebar slides out to left
- [ ] Backdrop fades out
- [ ] Icon changes back to bars (☰)

#### Backdrop Click (Alternative Close)
- [ ] Clicking backdrop closes sidebar
- [ ] Icon updates to bars (☰)

### 3. Responsive Behavior

#### Resize from Desktop to Mobile
- [ ] Sidebar transitions to overlay mode
- [ ] Icon changes from chevron to bars
- [ ] Calendar maintains full width
- [ ] Desktop collapsed state is reset

#### Resize from Mobile to Desktop
- [ ] Sidebar transitions to inline mode
- [ ] Icon changes from bars/times to chevron
- [ ] Calendar adjusts to grid layout
- [ ] Mobile overlay classes are removed

### 4. FullCalendar Integration

#### After Sidebar Toggle (Desktop)
- [ ] Calendar width updates correctly
- [ ] Events remain properly aligned
- [ ] No horizontal scrollbar appears
- [ ] Month/week/day views render correctly

#### After Sidebar Toggle (Mobile)
- [ ] Calendar width remains unchanged
- [ ] No resize is triggered (unnecessary)

### 5. Performance & Accessibility

#### Performance
- [ ] Transition is smooth (no janky animation)
- [ ] No excessive reflows or repaints
- [ ] `calendar.updateSize()` only called when needed

#### Accessibility
- [ ] Toggle button has `aria-label="Toggle sidebar"`
- [ ] Keyboard navigation works (Enter/Space to toggle)
- [ ] Focus management is correct

---

## Browser Console Testing Commands

### Check Current State

```javascript
// Viewport and state information
console.log('=== CALENDAR STATE ===');
console.log('Viewport width:', window.innerWidth);
console.log('Is mobile:', window.innerWidth < 1024);

const container = document.querySelector('.calendar-container');
console.log('Sidebar collapsed:', container.classList.contains('sidebar-collapsed'));

const icon = document.getElementById('sidebarToggleIcon');
console.log('Icon class:', icon.className);

// Grid layout information
console.log('Grid columns:', getComputedStyle(container).gridTemplateColumns);

// Calendar dimensions
const calendar = document.querySelector('#calendar');
console.log('Calendar width:', calendar.offsetWidth);
console.log('Calendar height:', calendar.offsetHeight);

// Sidebar state (mobile)
const sidebar = document.getElementById('calendarSidebar');
console.log('Sidebar open (mobile):', sidebar.classList.contains('open'));
```

### Verify Icon State

```javascript
// Expected icon states
const isMobile = window.innerWidth < 1024;
const icon = document.getElementById('sidebarToggleIcon');

console.log('=== ICON STATE CHECK ===');
console.log('Viewport:', isMobile ? 'Mobile' : 'Desktop');

if (isMobile) {
    const sidebarOpen = document.getElementById('calendarSidebar').classList.contains('open');
    const expectedIcon = sidebarOpen ? 'fa-times' : 'fa-bars';
    const actualIcon = icon.classList.contains('fa-times') ? 'fa-times' :
                       icon.classList.contains('fa-bars') ? 'fa-bars' : 'unknown';

    console.log('Expected icon:', expectedIcon);
    console.log('Actual icon:', actualIcon);
    console.log('PASS:', expectedIcon === actualIcon);
} else {
    const sidebarCollapsed = document.querySelector('.calendar-container').classList.contains('sidebar-collapsed');
    const expectedIcon = sidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left';
    const actualIcon = icon.classList.contains('fa-chevron-right') ? 'fa-chevron-right' :
                       icon.classList.contains('fa-chevron-left') ? 'fa-chevron-left' : 'unknown';

    console.log('Expected icon:', expectedIcon);
    console.log('Actual icon:', actualIcon);
    console.log('PASS:', expectedIcon === actualIcon);
}
```

### Test Sidebar Toggle

```javascript
// Programmatically toggle sidebar
const toggleBtn = document.getElementById('toggleSidebarBtn');

console.log('=== BEFORE TOGGLE ===');
console.log('Grid columns:', getComputedStyle(document.querySelector('.calendar-container')).gridTemplateColumns);

toggleBtn.click();

console.log('=== AFTER TOGGLE (immediate) ===');
console.log('Grid columns:', getComputedStyle(document.querySelector('.calendar-container')).gridTemplateColumns);

setTimeout(() => {
    console.log('=== AFTER TOGGLE (350ms - after resize) ===');
    console.log('Grid columns:', getComputedStyle(document.querySelector('.calendar-container')).gridTemplateColumns);
    console.log('Calendar width:', document.querySelector('#calendar').offsetWidth);
}, 350);
```

### Monitor Calendar Resize

```javascript
// Watch for calendar resize calls
const originalUpdateSize = window.calendar.updateSize.bind(window.calendar);

window.calendar.updateSize = function() {
    console.log('=== CALENDAR RESIZE TRIGGERED ===');
    console.trace(); // Show call stack
    return originalUpdateSize();
};

console.log('Calendar resize monitoring enabled. Toggle sidebar to see logs.');
```

---

## Visual Verification Checklist

### Desktop (1920px viewport)

**Sidebar Visible:**
```
┌──────────────┬─────────────────────────────────┐
│   Sidebar    │         Calendar                │
│   (280px)    │       (~1640px)                 │
│              │                                 │
│              │                                 │
└──────────────┴─────────────────────────────────┘
```
**Expected:** Chevron-left (←) icon

**Sidebar Collapsed:**
```
┌───────────────────────────────────────────────┐
│              Calendar                         │
│            (~1920px)                          │
│                                               │
│                                               │
└───────────────────────────────────────────────┘
```
**Expected:** Chevron-right (→) icon

### Mobile (375px viewport)

**Sidebar Closed:**
```
┌─────────────────────────┐
│      Calendar           │
│      (375px)            │
│                         │
│                         │
└─────────────────────────┘
```
**Expected:** Bars (☰) icon

**Sidebar Open:**
```
┌──────────┐
│ Sidebar  │◄─── Overlay on top
│ (280px)  │
│          │  ┌─────────────┐
│          │  │  Calendar   │◄─── Behind backdrop
└──────────┘  │  (375px)    │
   [Backdrop] └─────────────┘
```
**Expected:** Times (×) icon

---

## Common Issues & Fixes

### Issue 1: Icon Shows Bars on Desktop Load

**Symptom:** Desktop viewport shows bars (☰) instead of chevron-left (←) on initial page load.

**Root Cause:** `setInitialToggleIcon()` is called at line 1135, but might execute before DOM is fully painted.

**Fix Applied:** Function is called within IIFE, should work correctly.

**Verification:**
```javascript
// Check if called correctly
console.log('Icon on load:', document.getElementById('sidebarToggleIcon').className);
// Expected on desktop: "fas fa-chevron-left text-gray-600"
```

### Issue 2: Calendar Doesn't Resize After Toggle

**Symptom:** Calendar doesn't expand to fill space when sidebar collapses.

**Root Cause:** `calendar.updateSize()` might be called before CSS transition completes.

**Current Implementation:** 350ms delay (good, since transition is 300ms).

**Verification:**
```javascript
// Watch resize calls
console.log('Before toggle - Calendar width:', document.querySelector('#calendar').offsetWidth);
document.getElementById('toggleSidebarBtn').click();
setTimeout(() => {
    console.log('After toggle - Calendar width:', document.querySelector('#calendar').offsetWidth);
}, 400);
```

### Issue 3: Sidebar Stays Visible After Resize to Mobile

**Symptom:** Desktop collapsed state persists when resizing to mobile.

**Current Implementation:** Resize listener resets state correctly (lines 1152-1176).

**Verification:**
```javascript
// Simulate resize to mobile
window.innerWidth = 800; // Mock
window.dispatchEvent(new Event('resize'));

setTimeout(() => {
    console.log('After resize to mobile:');
    console.log('Icon:', document.getElementById('sidebarToggleIcon').className);
    // Expected: "fas fa-bars text-gray-600"
}, 200);
```

---

## DevTools Inspection Guide

### 1. Elements Panel

**Inspect Calendar Container:**
```html
<div class="calendar-container" id="calendarContainer">
```

**Expected Classes:**
- Default: `calendar-container`
- Collapsed: `calendar-container sidebar-collapsed`
- Detail open: `calendar-container detail-open`

**Computed Styles:**
- Check `grid-template-columns`
- Check `transition` property

### 2. Network Panel

**Calendar Events Load:**
- Request to `/work-items/calendar-feed/`
- Should return JSON array
- Check for HTTP errors (401, 403, 500)

### 3. Console Panel

**Expected Logs:**
```
Rendering FullCalendar... {containerHeight: 800, containerWidth: 1640, view: "dayGridMonth"}
Loading spinner hidden
FullCalendar rendered successfully {calendarExists: true, ...}
```

**No Expected Errors:**
- No "Calendar element not found"
- No "Cannot read property 'updateSize' of undefined"

### 4. Performance Panel

**Record Sidebar Toggle:**
1. Start recording
2. Click toggle button
3. Wait 500ms
4. Stop recording

**Expected Timeline:**
- CSS transition (300ms)
- JavaScript execution (<10ms)
- Layout recalculation
- Paint
- Composite

**No Red Flags:**
- No long tasks (>50ms)
- No forced reflows

---

## Automated Testing Script

Copy-paste this into browser console for full automated test:

```javascript
(async function testCalendarWidthExpansion() {
    console.log('=== CALENDAR WIDTH EXPANSION TEST ===\n');

    const container = document.querySelector('.calendar-container');
    const toggleBtn = document.getElementById('toggleSidebarBtn');
    const icon = document.getElementById('sidebarToggleIcon');
    const calendar = document.querySelector('#calendar');

    let passCount = 0;
    let failCount = 0;

    function test(name, condition) {
        if (condition) {
            console.log(`✅ PASS: ${name}`);
            passCount++;
        } else {
            console.error(`❌ FAIL: ${name}`);
            failCount++;
        }
    }

    // Test 1: Initial state
    console.log('--- Test 1: Initial State ---');
    const isMobile = window.innerWidth < 1024;

    if (!isMobile) {
        test('Sidebar visible by default', !container.classList.contains('sidebar-collapsed'));
        test('Icon is chevron-left', icon.classList.contains('fa-chevron-left'));
        test('Grid has sidebar column', getComputedStyle(container).gridTemplateColumns.startsWith('280px'));
    } else {
        test('Sidebar hidden on mobile', !document.getElementById('calendarSidebar').classList.contains('open'));
        test('Icon is bars', icon.classList.contains('fa-bars'));
    }

    // Test 2: Toggle functionality
    console.log('\n--- Test 2: Toggle Functionality ---');
    const widthBefore = calendar.offsetWidth;
    console.log('Calendar width before toggle:', widthBefore);

    toggleBtn.click();

    await new Promise(resolve => setTimeout(resolve, 50));

    if (!isMobile) {
        test('Sidebar collapsed after click', container.classList.contains('sidebar-collapsed'));
        test('Icon changed to chevron-right', icon.classList.contains('fa-chevron-right'));
    } else {
        test('Sidebar opened on mobile', document.getElementById('calendarSidebar').classList.contains('open'));
        test('Icon changed to times', icon.classList.contains('fa-times'));
    }

    // Test 3: Calendar resize (desktop only)
    if (!isMobile) {
        console.log('\n--- Test 3: Calendar Resize ---');

        await new Promise(resolve => setTimeout(resolve, 400));

        const widthAfter = calendar.offsetWidth;
        console.log('Calendar width after toggle:', widthAfter);

        test('Calendar width increased', widthAfter > widthBefore);
        test('Grid columns updated', getComputedStyle(container).gridTemplateColumns.startsWith('0px'));
    }

    // Summary
    console.log('\n=== TEST SUMMARY ===');
    console.log(`Total: ${passCount + failCount} | Pass: ${passCount} | Fail: ${failCount}`);

    if (failCount === 0) {
        console.log('🎉 All tests passed!');
    } else {
        console.warn('⚠️ Some tests failed. Review output above.');
    }
})();
```

---

## Success Criteria

### Desktop
- ✅ Icon shows chevron-left (←) on page load
- ✅ Clicking toggle collapses sidebar smoothly (300ms)
- ✅ Icon changes to chevron-right (→)
- ✅ Calendar expands to full viewport width
- ✅ `calendar.updateSize()` is called after transition
- ✅ Clicking toggle again restores sidebar
- ✅ Icon changes back to chevron-left (←)
- ✅ No console errors

### Mobile
- ✅ Icon shows bars (☰) on page load
- ✅ Clicking toggle opens sidebar overlay
- ✅ Icon changes to times (×)
- ✅ Backdrop appears behind sidebar
- ✅ Clicking backdrop closes sidebar
- ✅ Icon changes back to bars (☰)
- ✅ Calendar width remains unchanged

### Cross-Browser
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (macOS/iOS)

---

## Troubleshooting

### Calendar Not Expanding

**Check:**
1. Grid columns in DevTools (should change from `280px 1fr 0px` to `0px 1fr 0px`)
2. `calendar.updateSize()` is being called (add console.log)
3. Transition duration matches resize delay (300ms transition, 350ms delay)

### Icon Not Updating

**Check:**
1. `setInitialToggleIcon()` is called
2. Viewport width detection is correct
3. No JavaScript errors blocking execution

### Sidebar Stuck Open/Closed

**Check:**
1. Classes are being toggled correctly
2. CSS transitions are not disabled
3. Resize listener is working

---

## Related Documentation

- **[Calendar Architecture Clean](CALENDAR_ARCHITECTURE_CLEAN.md)** - High-level architecture
- **[Calendar Debug Fixes](CALENDAR_DEBUG_FIXES.md)** - Previous bug fixes
- **[Modern Calendar Implementation](../ui/MODERN_CALENDAR_IMPLEMENTATION.md)** - Implementation guide

---

**Last Updated:** 2025-10-06
**Tested Browsers:** Chrome 120+, Firefox 121+, Safari 17+
**Status:** Ready for Testing
