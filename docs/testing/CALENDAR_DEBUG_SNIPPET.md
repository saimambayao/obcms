# Calendar Debug Snippet

**Purpose:** Add enhanced logging to the Advanced Modern Calendar for debugging width expansion issues.

**File:** `src/templates/common/calendar_advanced_modern.html`

---

## Debug Code to Add

Add this code **after line 1135** (after `setInitialToggleIcon();`):

```javascript
// ==========================================================================
// DEBUG: Calendar Width Expansion Logging
// ==========================================================================
(function enableDebugLogging() {
    console.log('%c=== CALENDAR DEBUG MODE ENABLED ===', 'background: #3b82f6; color: white; padding: 4px 8px; font-weight: bold;');

    // Log initial state
    function logState(context) {
        const isMobile = window.innerWidth < 1024;
        const container = document.querySelector('.calendar-container');
        const icon = document.getElementById('sidebarToggleIcon');
        const calendar = document.querySelector('#calendar');

        console.group(`%c[${context}] State Check`, 'color: #3b82f6; font-weight: bold;');
        console.log('Viewport:', window.innerWidth, 'x', window.innerHeight, '(' + (isMobile ? 'MOBILE' : 'DESKTOP') + ')');
        console.log('Sidebar collapsed:', container?.classList.contains('sidebar-collapsed'));
        console.log('Grid columns:', getComputedStyle(container)?.gridTemplateColumns);
        console.log('Icon class:', icon?.className);
        console.log('Calendar width:', calendar?.offsetWidth + 'px');
        console.groupEnd();
    }

    // Log on page load
    logState('Page Load');

    // Override toggleSidebar to add logging
    const originalToggle = window.toggleSidebar || toggleSidebar;

    window.toggleSidebar = function() {
        console.log('%c[TOGGLE] Button clicked', 'background: #10b981; color: white; padding: 2px 8px; font-weight: bold;');
        logState('Before Toggle');

        // Call original function
        const result = originalToggle ? originalToggle.apply(this, arguments) : toggleSidebar();

        // Log after immediate changes
        setTimeout(() => {
            logState('After Toggle (immediate)');
        }, 50);

        // Log after resize
        setTimeout(() => {
            logState('After Toggle (350ms - post resize)');
        }, 400);

        return result;
    };

    // Log on window resize
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            logState('After Window Resize');
        }, 250);
    });

    console.log('%cDebug logging enabled. Toggle sidebar to see detailed logs.', 'color: #10b981; font-weight: bold;');
})();
// ==========================================================================
// END DEBUG
// ==========================================================================
```

---

## Where to Add

### Option 1: Inline in Template (Temporary)

1. Open `src/templates/common/calendar_advanced_modern.html`
2. Find line 1135: `setInitialToggleIcon();`
3. Paste the debug code **immediately after** this line
4. Save and reload the page
5. Open browser console to see debug logs

### Option 2: Browser Console (No File Edit)

1. Open the Advanced Modern Calendar page
2. Open browser DevTools (F12)
3. Paste the entire debug code into the Console tab
4. Press Enter
5. Toggle sidebar to see logs

---

## What the Debug Code Does

### 1. **Logs Initial State on Page Load**

```
=== CALENDAR DEBUG MODE ENABLED ===
[Page Load] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Sidebar collapsed: false
  Grid columns: 280px 1fr 0px
  Icon class: fas fa-chevron-left text-gray-600
  Calendar width: 1640px
```

### 2. **Logs State Changes on Toggle**

```
[TOGGLE] Button clicked
[Before Toggle] State Check
  ...
[After Toggle (immediate)] State Check
  Sidebar collapsed: true
  Grid columns: 0px 1fr 0px
  Icon class: fas fa-chevron-right text-gray-600
  Calendar width: 1640px
[After Toggle (350ms - post resize)] State Check
  Calendar width: 1920px
```

### 3. **Logs Window Resize Events**

```
[After Window Resize] State Check
  Viewport: 800 x 600 (MOBILE)
  Icon class: fas fa-bars text-gray-600
  ...
```

---

## Expected Output (Desktop)

### Initial Page Load

```javascript
=== CALENDAR DEBUG MODE ENABLED ===
[Page Load] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Sidebar collapsed: false
  Grid columns: 280px 1fr 0px
  Icon class: fas fa-chevron-left text-gray-600
  Calendar width: 1640px
Debug logging enabled. Toggle sidebar to see detailed logs.
```

### First Toggle (Collapse Sidebar)

```javascript
[TOGGLE] Button clicked
[Before Toggle] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Sidebar collapsed: false
  Grid columns: 280px 1fr 0px
  Icon class: fas fa-chevron-left text-gray-600
  Calendar width: 1640px

[After Toggle (immediate)] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Sidebar collapsed: true
  Grid columns: 0px 1fr 0px
  Icon class: fas fa-chevron-right text-gray-600
  Calendar width: 1640px  ← Still old width (transition in progress)

[After Toggle (350ms - post resize)] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Sidebar collapsed: true
  Grid columns: 0px 1fr 0px
  Icon class: fas fa-chevron-right text-gray-600
  Calendar width: 1920px  ← ✅ Expanded to full width!
```

### Second Toggle (Expand Sidebar)

```javascript
[TOGGLE] Button clicked
[Before Toggle] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Sidebar collapsed: true
  Grid columns: 0px 1fr 0px
  Icon class: fas fa-chevron-right text-gray-600
  Calendar width: 1920px

[After Toggle (immediate)] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Sidebar collapsed: false
  Grid columns: 280px 1fr 0px
  Icon class: fas fa-chevron-left text-gray-600
  Calendar width: 1920px  ← Still old width (transition in progress)

[After Toggle (350ms - post resize)] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Sidebar collapsed: false
  Grid columns: 280px 1fr 0px
  Icon class: fas fa-chevron-left text-gray-600
  Calendar width: 1640px  ← ✅ Contracted to sidebar-visible width!
```

---

## Expected Output (Mobile)

### Initial Page Load

```javascript
[Page Load] State Check
  Viewport: 375 x 667 (MOBILE)
  Sidebar collapsed: false
  Grid columns: 0px 1fr 0px
  Icon class: fas fa-bars text-gray-600
  Calendar width: 375px
```

### Toggle Open

```javascript
[TOGGLE] Button clicked
[Before Toggle] State Check
  Viewport: 375 x 667 (MOBILE)
  Icon class: fas fa-bars text-gray-600
  Calendar width: 375px

[After Toggle (immediate)] State Check
  Icon class: fas fa-times text-gray-600
  Calendar width: 375px  ← No change (overlay on top)

[After Toggle (350ms - post resize)] State Check
  Icon class: fas fa-times text-gray-600
  Calendar width: 375px  ← ✅ Still full width (correct)
```

---

## Troubleshooting Guide

### Issue 1: Icon Shows Bars on Desktop

**Debug Output:**
```javascript
[Page Load] State Check
  Viewport: 1920 x 1080 (DESKTOP)
  Icon class: fas fa-bars text-gray-600  ← ❌ Wrong!
```

**Fix:**
- Check if `setInitialToggleIcon()` is being called
- Verify function logic at line 1125-1135

### Issue 2: Calendar Doesn't Expand

**Debug Output:**
```javascript
[After Toggle (350ms - post resize)] State Check
  Sidebar collapsed: true
  Grid columns: 0px 1fr 0px
  Calendar width: 1640px  ← ❌ Didn't expand!
```

**Possible Causes:**
- `calendar.updateSize()` not being called
- FullCalendar instance not initialized
- CSS transition blocking resize

**Fix:**
- Check if `calendar` variable is defined
- Verify `setTimeout` delay matches transition duration
- Inspect CSS grid in DevTools

### Issue 3: Icon Doesn't Update After Toggle

**Debug Output:**
```javascript
[After Toggle (immediate)] State Check
  Sidebar collapsed: true
  Icon class: fas fa-chevron-left text-gray-600  ← ❌ Should be fa-chevron-right!
```

**Fix:**
- Check `toggleSidebar()` function at line 1080-1120
- Verify icon className assignment at lines 1103 and 1112

---

## Clean Up After Debugging

Once you've identified and fixed the issue:

1. **Remove the debug code** from the template
2. **Or comment it out** for future reference:

```javascript
// DEBUG: Uncomment to enable debug logging
/*
(function enableDebugLogging() {
    // ... debug code ...
})();
*/
```

---

## Advanced Debugging

### Monitor calendar.updateSize() Calls

Add this after the calendar is initialized:

```javascript
// Monitor calendar resize calls
if (calendar && calendar.updateSize) {
    const originalUpdateSize = calendar.updateSize.bind(calendar);

    calendar.updateSize = function() {
        console.log('%c[CALENDAR] updateSize() called', 'background: #8b5cf6; color: white; padding: 2px 8px;');
        console.trace(); // Show call stack
        return originalUpdateSize();
    };

    console.log('%c[DEBUG] calendar.updateSize() monitoring enabled', 'color: #8b5cf6; font-weight: bold;');
}
```

### Watch for CSS Transition Events

```javascript
// Watch grid transitions
const container = document.querySelector('.calendar-container');

container.addEventListener('transitionstart', function(e) {
    if (e.propertyName === 'grid-template-columns') {
        console.log('%c[TRANSITION] Grid transition started', 'background: #14b8a6; color: white; padding: 2px 8px;');
    }
});

container.addEventListener('transitionend', function(e) {
    if (e.propertyName === 'grid-template-columns') {
        console.log('%c[TRANSITION] Grid transition ended', 'background: #10b981; color: white; padding: 2px 8px;');
        console.log('Grid columns:', getComputedStyle(container).gridTemplateColumns);
    }
});

console.log('%c[DEBUG] Transition monitoring enabled', 'color: #14b8a6; font-weight: bold;');
```

---

## Related Documentation

- **[Calendar Width Expansion Testing Guide](CALENDAR_WIDTH_EXPANSION_TESTING_GUIDE.md)** - Full testing procedures
- **[verify_calendar_expansion.js](verify_calendar_expansion.js)** - Automated verification script

---

**Last Updated:** 2025-10-06
**Status:** Debug Tool (Temporary Use)
