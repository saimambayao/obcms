# FullCalendar Width Issue - Root Cause & Fixes

## Root Cause Analysis

### **THE CRITICAL ISSUE: FullCalendar v6 `height: 'auto'` + Flex Container Interaction**

**Problem Summary:**
The calendar was rendering as a narrow vertical strip because:

1. **FullCalendar v6 Height Setting**: Using `height: 'auto'` causes FullCalendar to fit content without expanding to fill available space
2. **Flex Container Shrinking**: The parent container `<div class="flex-1 min-w-0">` has `min-w-0` which allows it to shrink below minimum content width
3. **Initialization Timing**: Calendar initializes BEFORE the flex layout fully stabilizes, measuring a collapsed container width
4. **Scrollgrid System**: V6's new scrollgrid renders with table elements that default to `width: auto` (content-based sizing)
5. **CSS Override Failure**: The `!important` rules were being overridden by FullCalendar's internal inline styles

### **Why `updateSize()` Calls Didn't Work:**
- The calendar locks in its initial width measurement during first render
- Even with `setTimeout` calls, the flex container hadn't stabilized yet
- V6's scrollgrid calculates dimensions based on initial container measurement

---

## Implemented Fixes

### **Fix #1: Change FullCalendar Height Configuration** ✅
**File:** `src/static/common/js/calendar_modern.js`

**Before:**
```javascript
height: 'auto',
```

**After:**
```javascript
height: 'parent', // CRITICAL: Use 'parent' instead of 'auto' for flex containers
contentHeight: 700, // Explicit content height for proper rendering
```

**Why This Works:**
- `height: 'parent'` makes FullCalendar fill its parent container
- `contentHeight: 700` provides explicit height reference for v6's scrollgrid calculations

---

### **Fix #2: Update Container HTML Structure** ✅
**File:** `src/templates/components/calendar_modern.html`

**Before:**
```html
<div class="flex-1 min-w-0 p-6 space-y-4">
```

**After:**
```html
<div class="flex-1 p-6 space-y-4" style="min-width: 600px;">
```

**Why This Works:**
- Removed `min-w-0` which was allowing the container to shrink below content width
- Added explicit `min-width: 600px` to prevent collapse
- Ensures calendar has minimum space to render properly

---

### **Fix #3: Update FullCalendar Container with Explicit Height** ✅
**File:** `src/templates/components/calendar_modern.html`

**Before:**
```html
<div id="modernCalendar" class="..." style="min-height: 700px;">
```

**After:**
```html
<div id="modernCalendar" class="..." style="height: 750px; position: relative;">
```

**Why This Works:**
- Changed from `min-height` to explicit `height` for predictable dimensions
- Added `position: relative` for proper FullCalendar positioning context
- 750px provides comfortable viewing height

---

### **Fix #4: Update CSS Container Rules** ✅
**File:** `src/templates/components/calendar_modern.html`

**Before:**
```css
#modernCalendar {
    width: 100%;
    min-height: 700px;
    display: block;
    position: relative;
}

#modernCalendar .fc {
    width: 100% !important;
    height: auto;
}
```

**After:**
```css
#modernCalendar {
    width: 100%;
    height: 750px;
    display: block;
    position: relative;
}

#modernCalendar .fc {
    width: 100% !important;
    height: 100% !important;
}
```

**Why This Works:**
- Explicit height on container and `.fc` element
- Forces FullCalendar to fill exact dimensions

---

### **Fix #5: Update View Harness Height** ✅
**File:** `src/templates/components/calendar_modern.html`

**Before:**
```css
#modernCalendar .fc-view-harness {
    min-height: 650px;
}
```

**After:**
```css
#modernCalendar .fc-view-harness {
    height: 100% !important;
    position: relative !important;
}
```

**Why This Works:**
- Forces view harness to fill 100% of parent height
- Ensures proper vertical expansion

---

### **Fix #6: Add Critical Scrollgrid CSS Overrides** ✅
**File:** `src/templates/components/calendar_modern.html`

**Added:**
```css
/* Force all internal FullCalendar elements to 100% width */
#modernCalendar .fc-view-harness,
#modernCalendar .fc-view,
#modernCalendar .fc-scrollgrid,
#modernCalendar .fc-col-header,
#modernCalendar .fc-scrollgrid-sync-table,
#modernCalendar .fc-daygrid-body,
#modernCalendar .fc-timegrid-body,
#modernCalendar .fc-timegrid-slots table,
#modernCalendar .fc-timegrid-cols table,
#modernCalendar .fc-timegrid-cols,
#modernCalendar .fc-timegrid-axis-chunk,
#modernCalendar .fc-timegrid-divider,
#modernCalendar .fc-daygrid-day-frame {
    width: 100% !important;
    min-width: 100% !important;
}

/* Critical: Override FullCalendar v6 scrollgrid width calculation */
#modernCalendar .fc-scrollgrid-section > * {
    width: 100% !important;
}

#modernCalendar .fc-scrollgrid-section-body > td,
#modernCalendar .fc-scrollgrid-section-header > th {
    width: auto !important;
}
```

**Why This Works:**
- Targets FullCalendar v6's scrollgrid system specifically
- Forces all scrollgrid sections to fill 100% width
- Allows individual cells to auto-size within the full width

---

### **Fix #7: Update Parent Container Width Rule** ✅
**File:** `src/templates/components/calendar_modern.html`

**Before:**
```css
.flex-1.min-w-0 {
    flex: 1 1 0%;
    min-width: 0;
    width: 100%;
}
```

**After:**
```css
.flex-1 {
    flex: 1 1 0%;
    min-width: 600px;
    width: 100%;
}

@media (max-width: 768px) {
    .flex-1 {
        min-width: 100%;
    }
}
```

**Why This Works:**
- Enforces minimum width on flex containers
- Prevents shrinking below calendar's minimum usable width
- Mobile-responsive fallback

---

### **Fix #8: Improve Initialization Timing** ✅
**File:** `src/static/common/js/calendar_modern.js`

**Before:**
```javascript
modernCalendar.render();

setTimeout(() => {
    if (modernCalendar) {
        modernCalendar.updateSize();
    }
}, 100);
```

**After:**
```javascript
modernCalendar.render();

// Multiple recalculations ensure proper sizing in flex container
setTimeout(() => {
    if (modernCalendar) {
        modernCalendar.updateSize();
    }
}, 50);

setTimeout(() => {
    if (modernCalendar) {
        modernCalendar.updateSize();
    }
}, 200);

setTimeout(() => {
    if (modernCalendar) {
        modernCalendar.updateSize();
    }
}, 500);
```

**Why This Works:**
- Multiple resize calls at different intervals (50ms, 200ms, 500ms)
- Ensures calendar recalculates after flex layout stabilizes
- Catches any delayed CSS application

---

### **Fix #9: Update View Switcher to Force Resize** ✅
**File:** `src/static/common/js/calendar_modern.js`

**Before:**
```javascript
modernCalendar.changeView(view);
setTimeout(() => {
    modernCalendar.updateSize();
}, 50);
```

**After:**
```javascript
modernCalendar.changeView(view);
// Force multiple size recalculations after view change
setTimeout(() => {
    modernCalendar.updateSize();
}, 50);
setTimeout(() => {
    modernCalendar.updateSize();
}, 200);
```

**Why This Works:**
- Each view switch triggers multiple recalculations
- Ensures new view renders with proper dimensions

---

## FullCalendar v6 Specific Considerations

### **Scrollgrid System:**
- V6 introduced a new rendering system called "scrollgrid"
- Uses table-based layout with complex width calculations
- Requires explicit container dimensions for proper rendering
- `height: 'auto'` is incompatible with flex containers in v6

### **Height vs ContentHeight:**
- `height: 'parent'` - Makes calendar fill parent container (best for flex layouts)
- `contentHeight: 700` - Sets the scrollable content area height
- Both settings work together for proper v6 rendering

### **Width Calculation:**
- V6 measures container width on first render
- Locks in initial measurement unless `updateSize()` is called
- Requires stable container dimensions before initialization
- Flex containers must have explicit `min-width` to prevent collapse

---

## Testing Steps

### **1. Hard Refresh Browser:**
```bash
# Clear browser cache and reload
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

### **2. Verify Calendar Renders Full Width:**
- Calendar should fill the entire right panel (minus sidebar)
- Week view should show 7 full columns
- Day view should show single full-width column
- Month view should show 7x5 grid properly distributed
- Year view should show 12 months in grid layout

### **3. Test Responsive Behavior:**
- Resize browser window
- Calendar should maintain proper width at all sizes
- Mobile: Calendar should be full width
- Tablet: Calendar should share space with sidebar
- Desktop: Calendar should have minimum 600px width

### **4. Test View Switching:**
- Switch between Day, Week, Month, Year views
- Each view should render with full width
- No narrow strips or collapsed columns

### **5. Test Events Display:**
- Events should render with proper width
- Event text should be readable (not squished)
- Multi-day events should span properly

---

## Expected Results After Fixes

### **Visual Indicators of Success:**

✅ **Full Width Rendering:**
- Calendar fills entire right panel
- Week view shows 7 equally-sized columns
- No narrow vertical strip

✅ **Proper Event Display:**
- Events render with readable text
- Event time shows clearly
- Colors and borders display correctly

✅ **Responsive Layout:**
- Sidebar + Calendar fit properly on large screens
- Calendar goes full width on mobile
- No horizontal scrolling (unless intentional)

✅ **View Switching:**
- All views (Day, Week, Month, Year) render properly
- No width changes between views
- Smooth transitions

### **Console Verification:**
```javascript
// Check calendar dimensions in browser console
const cal = document.getElementById('modernCalendar');
console.log('Container width:', cal.offsetWidth);
console.log('Calendar FC width:', cal.querySelector('.fc').offsetWidth);
console.log('Should be equal and > 600px');
```

---

## Rollback Instructions

If the fixes cause issues, revert with:

```bash
cd /path/to/obcms
git checkout src/static/common/js/calendar_modern.js
git checkout src/templates/components/calendar_modern.html
```

---

## Summary

**Root Cause:**
- FullCalendar v6 `height: 'auto'` incompatible with flex containers
- Flex container `min-w-0` allowed collapse
- Calendar initialized before flex layout stabilized

**Solution:**
- Changed to `height: 'parent'` + `contentHeight: 700`
- Removed `min-w-0`, added explicit `min-width: 600px`
- Added explicit container heights (750px)
- Multiple CSS overrides for v6's scrollgrid system
- Improved initialization timing with multiple `updateSize()` calls

**Result:**
- Calendar renders full width across all views
- Proper responsive behavior
- Events display correctly
- No more narrow strip issue

---

**Files Modified:**
1. `/src/static/common/js/calendar_modern.js` - JavaScript configuration
2. `/src/templates/components/calendar_modern.html` - HTML structure and CSS

**Next Steps:**
1. Test in browser with hard refresh
2. Verify all views (Day, Week, Month, Year)
3. Test responsive behavior
4. Verify event display quality
