# Clean Calendar Architecture for FullCalendar v6

**Version:** 1.0
**Date:** 2025-10-06
**Status:** ARCHITECTURAL DESIGN
**Author:** OBCMS System Architect

---

## Executive Summary

This document provides a clean, simple architecture for the OBCMS Modern Calendar that works **with** FullCalendar v6's natural behavior rather than fighting it. The current implementation uses flex layout with extensive CSS overrides, resulting in a narrow calendar that doesn't utilize available space effectively.

**Key Insight:** FullCalendar v6 calculates its width based on its **immediate parent container**. The solution is to ensure the parent container has explicit dimensions **before** FullCalendar initializes.

---

## Problem Analysis

### Current Implementation Issues

1. **Container Structure:** Sidebar and calendar are in a CSS Grid with `lg:col-span-9`, but FullCalendar initializes before the grid fully calculates dimensions
2. **Layout System:** Mix of Tailwind Grid classes with insufficient explicit sizing
3. **CSS Overrides:** Extensive `!important` rules trying to force FullCalendar to expand
4. **Initialization Timing:** Calendar renders before container is fully sized
5. **Height Configuration:** Uses `height: 'auto'` which doesn't give FullCalendar enough constraints

### Root Cause

**FullCalendar v6 sizing behavior:**
- Measures parent container dimensions **at initialization time**
- If parent has no explicit width/height, defaults to conservative dimensions
- Uses `aspectRatio` (default 1.35) when height is `'auto'`
- Does not automatically resize unless `handleWindowResize: true` is set

**Current container:** Grid column span without explicit pixel/percentage dimensions = FullCalendar measures too early.

---

## Recommended Architecture

### 1. HTML Container Structure

**Use Hybrid Layout: Grid for overall structure, Flexbox for calendar container**

```html
<!-- Outer Container: Full viewport, constrained by padding -->
<div class="calendar-page-wrapper">

  <!-- Header Card: Full width, fixed height -->
  <div class="calendar-header-card">
    <!-- Title, View Switcher, Action Buttons -->
  </div>

  <!-- Main Layout: Fixed-height container with Grid -->
  <div class="calendar-main-layout">

    <!-- Sidebar: Fixed width, scrollable -->
    <aside class="calendar-sidebar">
      <!-- Mini Calendar, Filters, Legend -->
    </aside>

    <!-- Calendar Container: Flex-1, explicit dimensions -->
    <main class="calendar-main-container">
      <!-- White card wrapper -->
      <div class="calendar-card-wrapper">
        <!-- FullCalendar renders here -->
        <div id="calendar" class="calendar-element"></div>
      </div>
    </main>

  </div>

</div>
```

**Key Principles:**
- **Explicit dimensions:** Every container has defined width/height
- **Fixed outer height:** Main layout uses `calc(100vh - header - padding)`
- **Flex-1 on calendar:** Calendar container expands to fill remaining space
- **No nested flex/grid conflicts:** Simple one-level hierarchy

---

### 2. CSS Layout System (Tailwind + Custom CSS)

**Strategy: Explicit sizing cascading from viewport down to calendar element**

```css
/* ============================================
   CALENDAR PAGE WRAPPER
   Full viewport with controlled padding
   ============================================ */
.calendar-page-wrapper {
    width: 100%;
    min-height: 100vh;
    padding: 1.5rem; /* 24px */
}

/* ============================================
   HEADER CARD
   Fixed height, full width, no flex
   ============================================ */
.calendar-header-card {
    width: 100%;
    height: auto; /* Content-driven */
    margin-bottom: 1.5rem;
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* ============================================
   MAIN LAYOUT CONTAINER
   Fixed height: Viewport - Header - Padding
   Grid: Sidebar (320px) + Calendar (1fr)
   ============================================ */
.calendar-main-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 1.5rem;
    height: calc(100vh - 180px); /* Adjust 180px based on header height */
    width: 100%;
}

/* ============================================
   SIDEBAR
   Fixed width, scrollable overflow
   ============================================ */
.calendar-sidebar {
    width: 320px;
    height: 100%; /* Fill grid row height */
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* ============================================
   CALENDAR MAIN CONTAINER
   Fills remaining grid space
   ============================================ */
.calendar-main-container {
    width: 100%; /* Fill remaining grid column */
    height: 100%; /* Fill grid row height */
    min-width: 0; /* Allow grid to shrink if needed */
}

/* ============================================
   CALENDAR CARD WRAPPER
   White background card
   ============================================ */
.calendar-card-wrapper {
    width: 100%;
    height: 100%;
    background: white;
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
}

/* ============================================
   FULLCALENDAR ELEMENT
   CRITICAL: Must have explicit dimensions
   ============================================ */
.calendar-element {
    width: 100%;
    height: 100%;
    flex: 1; /* Fill remaining card space */
    min-height: 600px; /* Fallback minimum */
}

/* ============================================
   RESPONSIVE: Tablet and below
   ============================================ */
@media (max-width: 1024px) {
    .calendar-main-layout {
        grid-template-columns: 1fr; /* Stack sidebar and calendar */
        height: auto; /* Allow natural height */
    }

    .calendar-sidebar {
        position: fixed;
        inset-y: 0;
        left: 0;
        width: 320px;
        transform: translateX(-100%);
        transition: transform 0.3s ease;
        background: white;
        z-index: 60;
        box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
    }

    .calendar-sidebar.open {
        transform: translateX(0);
    }

    .calendar-main-container {
        width: 100%;
        height: calc(100vh - 180px);
    }
}

@media (max-width: 640px) {
    .calendar-page-wrapper {
        padding: 1rem;
    }

    .calendar-main-layout {
        gap: 1rem;
        height: calc(100vh - 150px);
    }

    .calendar-card-wrapper {
        padding: 1rem;
    }

    .calendar-element {
        min-height: 500px;
    }
}
```

**Why This Works:**
1. **Grid guarantees dimensions:** `grid-template-columns: 320px 1fr` explicitly sizes both columns
2. **Height is fixed:** `calc(100vh - 180px)` gives calendar predictable vertical space
3. **No flex conflicts:** Single grid level, no nested flex/grid fighting
4. **Calendar sees real dimensions:** By initialization time, parent has concrete width/height

---

### 3. FullCalendar Configuration

**Strategy: Leverage FullCalendar's native sizing with explicit constraints**

```javascript
this.calendar = new FullCalendar.Calendar(this.options.calendarEl, {
    // ============================================
    // SIZING CONFIGURATION (CRITICAL)
    // ============================================

    // Use 'parent' height to fill container exactly
    height: 'parent',

    // Alternative: Use explicit pixel height
    // height: 800,

    // Disable aspectRatio (we control height via CSS)
    aspectRatio: undefined,

    // Expand rows to fill available height
    expandRows: true,

    // Handle window resize automatically
    handleWindowResize: true,

    // Debounce resize events (performance)
    windowResizeDelay: 100,

    // ============================================
    // VIEW CONFIGURATION
    // ============================================

    initialView: this.currentView,

    headerToolbar: {
        left: 'prev,next',
        center: 'title',
        right: '' // View buttons in separate UI
    },

    // Day max events before "+N more" link
    dayMaxEvents: 4,
    moreLinkClick: 'popover',

    // Event display
    eventDisplay: 'block',
    displayEventTime: true,
    displayEventEnd: false,

    // Multi-month year view
    multiMonthMaxColumns: 3,
    multiMonthMinWidth: 300,

    // ============================================
    // DATA & INTERACTIONS
    // ============================================

    events: function(info, successCallback, failureCallback) {
        self.fetchEvents(info, successCallback, failureCallback);
    },

    eventClick: function(info) {
        info.jsEvent.preventDefault();
        self.handleEventClick(info);
    },

    eventContent: function(arg) {
        return self.buildEventContent(arg);
    },

    eventDidMount: function(info) {
        self.setupEventAttributes(info);
    },

    dateClick: function(info) {
        self.handleDateClick(info);
    },

    datesSet: function(dateInfo) {
        if (self.options.onViewChange) {
            self.options.onViewChange(dateInfo);
        }
        self.updateMiniCalendarDate(dateInfo.start);
    }
});

this.calendar.render();
```

**Key Configuration Choices:**

| Option | Value | Rationale |
|--------|-------|-----------|
| `height` | `'parent'` | Fill parent container exactly (best for grid layouts) |
| `aspectRatio` | `undefined` | Disable aspect ratio constraints (we control height via CSS) |
| `expandRows` | `true` | Rows expand to fill available vertical space |
| `handleWindowResize` | `true` | Auto-adjust on viewport changes |
| `windowResizeDelay` | `100` | Debounce for performance (default: 100ms) |

**Alternative: Explicit Height**
```javascript
// If 'parent' doesn't work, use explicit pixel height
height: 800, // Fixed 800px height
```

---

### 4. Initialization Timing Strategy

**Problem:** If FullCalendar initializes before CSS layout completes, it measures incorrect dimensions.

**Solution:** Initialize after DOM is ready AND layout is painted.

```javascript
// ============================================
// CORRECT INITIALIZATION SEQUENCE
// ============================================

class ModernCalendar {
    constructor(options) {
        this.options = options;
        this.calendar = null;

        // Wait for DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            // DOM already ready, wait for next frame (layout complete)
            requestAnimationFrame(() => this.init());
        }
    }

    init() {
        console.log('🚀 Initializing Modern Calendar...');

        // Verify container exists and has dimensions
        const container = this.options.calendarEl;
        if (!container) {
            console.error('❌ Calendar element not found');
            return;
        }

        // Check if container has computed dimensions
        const rect = container.getBoundingClientRect();
        console.log('📐 Container dimensions:', {
            width: rect.width,
            height: rect.height
        });

        if (rect.width === 0 || rect.height === 0) {
            console.warn('⚠️  Container has zero dimensions, waiting for layout...');

            // Wait for next animation frame (layout complete)
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    this.initMainCalendar();
                    this.initMiniCalendar();
                    this.initViewSwitcher();
                    this.initFilters();
                    this.initDetailPanel();
                    this.initModal();
                    this.initTodayButton();
                });
            });
        } else {
            // Container has dimensions, safe to initialize
            this.initMainCalendar();
            this.initMiniCalendar();
            this.initViewSwitcher();
            this.initFilters();
            this.initDetailPanel();
            this.initModal();
            this.initTodayButton();
        }

        console.log('✅ Modern Calendar initialized successfully');
    }

    initMainCalendar() {
        // ... (same as current implementation with updated config)
    }
}

// ============================================
// USAGE IN TEMPLATE
// ============================================

// Wait for DOMContentLoaded AND fonts/styles loaded
document.addEventListener('DOMContentLoaded', function() {
    // Double-RAF ensures layout is complete
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            window.modernCalendar = new ModernCalendar({
                calendarEl: document.getElementById('calendar'),
                // ... other options
            });
        });
    });
});
```

**Why This Works:**
1. **DOM Ready:** Ensures all elements exist
2. **Layout Complete:** `requestAnimationFrame` waits for browser paint
3. **Double RAF:** Second RAF ensures layout calculations are done
4. **Dimension Check:** Verifies container has non-zero dimensions
5. **Fallback:** If dimensions missing, waits additional frame

---

## Implementation Comparison

### Current Approach (Problematic)

```html
<!-- Grid with implicit dimensions -->
<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
    <aside class="lg:col-span-3">...</aside>
    <main class="lg:col-span-9">
        <div class="bg-white rounded-2xl p-6">
            <div id="calendar"></div> <!-- No explicit dimensions -->
        </div>
    </main>
</div>
```

```javascript
// Initializes immediately
this.calendar = new FullCalendar.Calendar(el, {
    height: 'auto', // Relies on aspectRatio
    // No handleWindowResize
});
this.calendar.render();
```

**Issues:**
- Grid columns have no explicit widths (just spans)
- Calendar element has no height constraint
- Initializes before layout stabilizes
- No resize handling

---

### Recommended Approach (Clean)

```html
<!-- Fixed-height grid with explicit dimensions -->
<div class="calendar-main-layout">
    <aside class="calendar-sidebar">...</aside>
    <main class="calendar-main-container">
        <div class="calendar-card-wrapper">
            <div id="calendar" class="calendar-element"></div>
        </div>
    </main>
</div>
```

```css
.calendar-main-layout {
    display: grid;
    grid-template-columns: 320px 1fr; /* Explicit widths */
    height: calc(100vh - 180px); /* Explicit height */
}

.calendar-element {
    width: 100%;
    height: 100%;
    flex: 1;
}
```

```javascript
// Initializes after layout complete
requestAnimationFrame(() => {
    requestAnimationFrame(() => {
        this.calendar = new FullCalendar.Calendar(el, {
            height: 'parent', // Fill parent exactly
            expandRows: true, // Use available space
            handleWindowResize: true, // Auto-adjust
        });
        this.calendar.render();
    });
});
```

**Benefits:**
- Explicit dimensions cascade from viewport → grid → calendar
- Calendar initializes after layout stabilizes
- Automatic resize handling
- Predictable, maintainable behavior

---

## Why This Architecture Works Better

### 1. Works WITH FullCalendar, Not Against It

**Current:** Fight FullCalendar with `!important` CSS overrides
**Recommended:** Give FullCalendar the container dimensions it needs

### 2. Explicit Dimension Chain

**Current:** Implicit dimensions via grid spans
**Recommended:** Explicit dimensions from viewport → container → calendar

```
Viewport (100vh)
  ↓
Page Wrapper (padding: 24px)
  ↓
Main Layout (height: calc(100vh - 180px))
  ↓
Grid Column (1fr = remaining after 320px sidebar)
  ↓
Card Wrapper (100% of column, flex: 1)
  ↓
Calendar Element (100% of wrapper)
  ↓
FullCalendar (height: 'parent')
```

### 3. Initialization Timing

**Current:** Render immediately, hope layout is ready
**Recommended:** Wait for layout complete, verify dimensions

### 4. Responsive Behavior

**Current:** Media queries fight grid calculations
**Recommended:** Grid recalculates, FullCalendar auto-resizes

### 5. Maintainability

**Current:** Complex CSS overrides, hard to debug
**Recommended:** Simple cascade, easy to understand

---

## Google Calendar Pattern Reference

Google Calendar uses similar architecture:

```
┌─────────────────────────────────────────────┐
│ Header (Fixed Height)                       │
├─────────┬───────────────────────────────────┤
│ Sidebar │ Calendar Area                     │
│ (320px) │ (Flex-1)                          │
│         │                                   │
│ - Mini  │ FullCalendar renders here        │
│   Cal   │ (height: 100% of parent)         │
│ - Cals  │                                   │
│ - Tasks │                                   │
│         │                                   │
│ (Scroll)│ (Scroll if needed)                │
└─────────┴───────────────────────────────────┘
```

**Key Similarities:**
1. **Fixed sidebar width:** 256px (Google) vs 320px (OBCMS)
2. **Flex calendar area:** Remaining space
3. **Fixed viewport height:** `calc(100vh - header)`
4. **No nested flex/grid:** Simple structure

---

## Migration Strategy

### Step 1: Update HTML Structure (Template)

**File:** `src/templates/common/calendar_modern.html`

Replace current grid structure with recommended classes:

```html
<!-- OLD -->
<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
    <aside class="lg:col-span-3">...</aside>
    <main class="lg:col-span-9">...</main>
</div>

<!-- NEW -->
<div class="calendar-main-layout">
    <aside class="calendar-sidebar">...</aside>
    <main class="calendar-main-container">
        <div class="calendar-card-wrapper">
            <div id="calendar" class="calendar-element"></div>
        </div>
    </main>
</div>
```

### Step 2: Add CSS Classes

**File:** `src/static/common/css/calendar-modern.css`

Add recommended CSS classes (see Section 2 above).

### Step 3: Update FullCalendar Config

**File:** `src/static/common/js/calendar-modern.js`

Update `initMainCalendar()`:

```javascript
initMainCalendar() {
    // ... existing code ...

    this.calendar = new FullCalendar.Calendar(this.options.calendarEl, {
        // UPDATE THESE OPTIONS
        height: 'parent', // Changed from 'auto'
        aspectRatio: undefined, // Disable aspect ratio
        expandRows: true, // Add this
        handleWindowResize: true, // Add this
        windowResizeDelay: 100, // Add this

        // ... rest of config unchanged ...
    });

    this.calendar.render();
}
```

### Step 4: Update Initialization Timing

**File:** `src/templates/common/calendar_modern.html` (script block)

Update initialization:

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Wait for layout to stabilize
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            window.modernCalendar = new ModernCalendar({
                calendarEl: document.getElementById('calendar'),
                // ... other options unchanged ...
            });
        });
    });
});
</script>
```

### Step 5: Test Responsive Behavior

1. Desktop (1920px): Sidebar + wide calendar
2. Laptop (1366px): Sidebar + medium calendar
3. Tablet (768px): Stacked layout OR fixed sidebar
4. Mobile (375px): Stacked, full-width calendar

---

## Testing Strategy

### Visual Verification

1. **Desktop:** Calendar should fill width between sidebar and right edge
2. **Resize window:** Calendar should smoothly adjust width
3. **Sidebar toggle:** Calendar should expand when sidebar hidden
4. **View switching:** All views (Month/Week/Day/Year) should fill container

### Dimension Checks

```javascript
// Add to initMainCalendar() for debugging
console.log('📐 Calendar container dimensions:', {
    container: this.options.calendarEl.getBoundingClientRect(),
    parent: this.options.calendarEl.parentElement.getBoundingClientRect()
});

// After render
this.calendar.render();
setTimeout(() => {
    console.log('📐 Calendar after render:', {
        containerWidth: this.options.calendarEl.offsetWidth,
        containerHeight: this.options.calendarEl.offsetHeight,
        fcWidth: this.calendar.el.offsetWidth,
        fcHeight: this.calendar.el.offsetHeight
    });
}, 100);
```

Expected output:
```
📐 Calendar container dimensions: {
    container: { width: 1200, height: 800 },
    parent: { width: 1200, height: 800 }
}
📐 Calendar after render: {
    containerWidth: 1200,
    containerHeight: 800,
    fcWidth: 1200,
    fcHeight: 800
}
```

### Performance Tests

1. **Initialization time:** < 100ms
2. **Window resize:** Smooth, no lag
3. **View switching:** Instant transition
4. **Event rendering:** < 50ms for 100 events

---

## Documentation Needs

### Update Existing Docs

1. **`docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`**
   - Add "Calendar Layout Pattern" section
   - Document `.calendar-main-layout` structure
   - Add responsive breakpoint standards

2. **`docs/development/README.md`**
   - Add "Calendar Architecture" section
   - Reference this document

3. **`CLAUDE.md`**
   - Update "Instant UI & Smooth User Experience" section
   - Add calendar initialization best practices

### Create New Docs

1. **`docs/improvements/UI/CALENDAR_LAYOUT_GUIDE.md`**
   - Developer guide for calendar customization
   - Common layout patterns
   - Troubleshooting narrow calendar issues

---

## Frequently Asked Questions

### Q: Why not use `height: 'auto'`?

**A:** `height: 'auto'` makes FullCalendar calculate height based on `aspectRatio` (default 1.35). This creates unpredictable sizing, especially in grid/flex layouts. Using `height: 'parent'` gives explicit control.

### Q: Why `requestAnimationFrame` twice?

**A:** First RAF waits for next browser paint. Second RAF ensures layout calculations are complete. This guarantees container has computed dimensions before FullCalendar initializes.

### Q: What if `height: 'parent'` doesn't work?

**A:** Fallback to explicit pixel height:
```javascript
height: 800, // Fixed 800px height
```

Or use `contentHeight`:
```javascript
contentHeight: 'auto', // Height of view area only
height: 900, // Total calendar height (including header)
```

### Q: Why Grid instead of Flexbox?

**A:** Grid provides explicit column widths (`320px 1fr`), which FullCalendar can measure accurately. Flexbox with `flex: 1` requires layout calculations that may complete after FullCalendar initializes.

### Q: How to debug narrow calendar issues?

**A:** Check container dimensions:
```javascript
const rect = document.getElementById('calendar').getBoundingClientRect();
console.log('Calendar container:', rect.width, 'x', rect.height);
```

Expected: Width = viewport width - sidebar - padding (e.g., 1200px on 1920px screen)
If width < 600px: Container not sized correctly.

---

## Summary

### Problem
Current flex-based layout with `height: 'auto'` produces narrow calendar because FullCalendar initializes before grid dimensions stabilize.

### Solution
1. **Grid layout** with explicit dimensions (`320px 1fr`)
2. **Fixed height** container (`calc(100vh - 180px)`)
3. **`height: 'parent'`** in FullCalendar config
4. **Delayed initialization** with `requestAnimationFrame`
5. **Auto-resize** with `handleWindowResize: true`

### Result
- Calendar fills available space correctly
- Responsive to window resizing
- No CSS `!important` hacks needed
- Clean, maintainable architecture
- Works WITH FullCalendar v6's natural behavior

---

**Next Steps:**
1. Review this architecture with development team
2. Implement changes in staging environment
3. Test across devices/browsers
4. Deploy to production
5. Update documentation

**References:**
- FullCalendar v6 Sizing Docs: https://fullcalendar.io/docs/sizing
- CSS Grid Layout Guide: https://css-tricks.com/snippets/css/complete-guide-grid/
- `requestAnimationFrame` Timing: https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame
