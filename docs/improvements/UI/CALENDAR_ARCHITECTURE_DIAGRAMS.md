# Calendar Architecture Visual Diagrams

**Companion Document to:** `CALENDAR_ARCHITECTURE_CLEAN.md`
**Version:** 1.0
**Date:** 2025-10-06

---

## Diagram 1: Current vs Recommended Layout Structure

```
CURRENT APPROACH (PROBLEMATIC)
================================

┌──────────────────────────────────────────────────────────────┐
│ Page Wrapper (max-w-full mx-auto px-4)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Header Card (fixed height ~140px)                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Grid Container (grid lg:grid-cols-12)                  │  │
│  │  ┌──────────┐  ┌─────────────────────────────────────┐ │  │
│  │  │ Sidebar  │  │ Main (lg:col-span-9)               │ │  │
│  │  │ (col-3)  │  │  ┌───────────────────────────────┐ │ │  │
│  │  │          │  │  │ Card (bg-white p-6)           │ │ │  │
│  │  │ Mini Cal │  │  │  ┌─────────────────────────┐ │ │ │  │
│  │  │ Filters  │  │  │  │ #calendar              │ │ │ │  │
│  │  │ Legend   │  │  │  │ (NO explicit size!)    │ │ │ │  │
│  │  │          │  │  │  │                         │ │ │ │  │
│  │  │          │  │  │  │ FullCalendar defaults  │ │ │ │  │
│  │  │          │  │  │  │ to narrow width        │ │ │ │  │
│  │  │          │  │  │  └─────────────────────────┘ │ │ │  │
│  │  │          │  │  └───────────────────────────────┘ │ │  │
│  │  └──────────┘  └─────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘

ISSUES:
❌ Grid spans (col-3, col-9) have no explicit pixel widths
❌ Calendar element has no height constraint
❌ FullCalendar initializes before grid calculates dimensions
❌ height: 'auto' relies on aspectRatio (unpredictable)


RECOMMENDED APPROACH (CLEAN)
================================

┌──────────────────────────────────────────────────────────────┐
│ Page Wrapper (.calendar-page-wrapper)                       │
│ width: 100%, padding: 24px                                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Header Card (.calendar-header-card)                    │  │
│  │ width: 100%, height: auto (~140px)                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Main Layout (.calendar-main-layout)                    │  │
│  │ display: grid                                           │  │
│  │ grid-template-columns: 320px 1fr  ← EXPLICIT!          │  │
│  │ height: calc(100vh - 180px)       ← EXPLICIT!          │  │
│  │                                                          │  │
│  │  ┌─────────┐  ┌──────────────────────────────────────┐ │  │
│  │  │ Sidebar │  │ Main Container                       │ │  │
│  │  │ (320px) │  │ (.calendar-main-container)           │ │  │
│  │  │ height: │  │ width: 100%, height: 100%            │ │  │
│  │  │ 100%    │  │  ┌────────────────────────────────┐  │ │  │
│  │  │         │  │  │ Card Wrapper                   │  │ │  │
│  │  │ Mini    │  │  │ (.calendar-card-wrapper)       │  │ │  │
│  │  │ Cal     │  │  │ width: 100%, height: 100%      │  │ │  │
│  │  │         │  │  │ display: flex, flex-col        │  │ │  │
│  │  │ Filters │  │  │  ┌──────────────────────────┐  │  │ │  │
│  │  │         │  │  │  │ Calendar Element         │  │  │ │  │
│  │  │ Legend  │  │  │  │ (.calendar-element)      │  │  │ │  │
│  │  │         │  │  │  │ width: 100%, height: 100%│  │  │ │  │
│  │  │ (scroll)│  │  │  │ flex: 1                  │  │  │ │  │
│  │  │         │  │  │  │                          │  │  │ │  │
│  │  │         │  │  │  │ FullCalendar fills this! │  │  │ │  │
│  │  │         │  │  │  │ height: 'parent'         │  │  │ │  │
│  │  └─────────┘  │  │  └──────────────────────────┘  │  │ │  │
│  │               │  └────────────────────────────────┘  │ │  │
│  │               └──────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘

BENEFITS:
✅ Explicit grid columns: 320px sidebar + 1fr calendar (fills remaining)
✅ Explicit height: calc(100vh - 180px) for main layout
✅ Dimension chain: viewport → grid → container → calendar
✅ FullCalendar sees real dimensions at initialization
✅ height: 'parent' fills container exactly
```

---

## Diagram 2: Dimension Cascade Flow

```
DIMENSION CASCADE (Top to Bottom)
==================================

Viewport
  │
  │ width: 1920px (example desktop)
  │ height: 1080px
  │
  ▼
┌─────────────────────────────────────────────┐
│ .calendar-page-wrapper                      │
│ width: 100% (1920px)                        │
│ padding: 24px each side                     │
│ → Available: 1872px width                   │
└─────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────┐
│ .calendar-header-card                       │
│ width: 100% (1872px)                        │
│ height: auto (~140px, content-driven)       │
│ margin-bottom: 24px                         │
└─────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────┐
│ .calendar-main-layout (GRID)                │
│ width: 100% (1872px)                        │
│ height: calc(100vh - 180px) = 900px         │
│ grid-template-columns: 320px 1fr            │
│ gap: 24px                                   │
│                                             │
│ ┌──────────┐       ┌────────────────────┐  │
│ │ Sidebar  │  24px │ Main Container     │  │
│ │ 320px    │ gap   │ 1fr = 1528px      │  │
│ │ × 900px  │       │ × 900px            │  │
│ └──────────┘       └────────────────────┘  │
│                         │                   │
└─────────────────────────│───────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │ .calendar-card-wrapper            │
          │ width: 100% (1528px)              │
          │ height: 100% (900px)              │
          │ padding: 24px                     │
          │ → Content area: 1480px × 852px    │
          └───────────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │ .calendar-element (#calendar)     │
          │ width: 100% (1480px)              │
          │ height: 100% (852px)              │
          │ flex: 1                           │
          └───────────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │ FullCalendar                      │
          │ Measures parent: 1480px × 852px   │
          │ Renders with full width!          │
          │ height: 'parent' → fills exactly  │
          └───────────────────────────────────┘

CALCULATION EXAMPLE:
====================
Viewport: 1920px width
- Page padding: -48px (24px × 2)
- Available: 1872px

Grid allocation:
- Sidebar: 320px (fixed)
- Gap: 24px
- Calendar: 1fr = 1872 - 320 - 24 = 1528px

Card wrapper:
- Width: 1528px (100% of grid column)
- Padding: -48px (24px × 2)
- Content: 1480px

Result: Calendar sees 1480px × 852px container
        Renders full width!
```

---

## Diagram 3: Initialization Timing Sequence

```
INITIALIZATION SEQUENCE (Time Flow)
====================================

1. Page Load
   │
   ├─ HTML parsed
   ├─ CSS loaded
   ├─ JavaScript loaded
   │
   ▼
2. DOMContentLoaded Event
   │
   ├─ DOM tree complete
   ├─ Layout NOT guaranteed
   │
   ▼
3. requestAnimationFrame #1
   │
   ├─ Browser prepares next paint
   ├─ CSS calculations started
   │
   ▼
4. requestAnimationFrame #2
   │
   ├─ Layout calculations complete
   ├─ Container dimensions computed
   │
   ▼
5. Initialize ModernCalendar
   │
   ├─ Check container dimensions
   ├─ Verify width > 0, height > 0
   │
   ▼
6. Create FullCalendar Instance
   │
   ├─ FullCalendar reads parent dimensions
   ├─ Parent has concrete size: 1480px × 852px
   ├─ height: 'parent' → uses parent height
   │
   ▼
7. Render Calendar
   │
   ├─ Calendar fills container exactly
   ├─ No re-layout needed
   │
   ▼
8. Calendar Ready ✅


TIMING CODE:
============

document.addEventListener('DOMContentLoaded', function() {
    // Step 2: DOM ready, but layout may not be complete

    requestAnimationFrame(() => {
        // Step 3: Next paint cycle, CSS started

        requestAnimationFrame(() => {
            // Step 4: Layout complete, dimensions computed

            window.modernCalendar = new ModernCalendar({
                // Step 5-8: Initialize with real dimensions
                calendarEl: document.getElementById('calendar'),
                // ...
            });
        });
    });
});


WHY DOUBLE RAF?
===============

┌─────────────────────────────────────────────────────┐
│ Frame N (Current)                                   │
│ ├─ JavaScript executes                              │
│ ├─ DOM mutations applied                            │
│ └─ requestAnimationFrame callbacks queued           │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│ Frame N+1 (First RAF)                               │
│ ├─ Browser recalculates styles                      │
│ ├─ Layout engine computes positions/sizes           │
│ └─ Paint prepares (dimensions may not be final)     │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│ Frame N+2 (Second RAF) ✅ SAFE TO READ DIMENSIONS   │
│ ├─ Layout calculations complete                     │
│ ├─ getBoundingClientRect() returns final values     │
│ └─ FullCalendar can initialize with real dimensions │
└─────────────────────────────────────────────────────┘
```

---

## Diagram 4: Responsive Breakpoints

```
RESPONSIVE LAYOUT BEHAVIOR
===========================

DESKTOP (≥ 1024px)
┌────────────────────────────────────────────────┐
│ ┌──────────┐  ┌──────────────────────────────┐ │
│ │ Sidebar  │  │ Calendar                     │ │
│ │ 320px    │  │ 1fr (remaining space)        │ │
│ │ Visible  │  │ Full width                   │ │
│ └──────────┘  └──────────────────────────────┘ │
└────────────────────────────────────────────────┘
Grid: 320px 1fr
Sidebar: Static, visible
Calendar: Fills remaining space


TABLET (768px - 1023px)
┌────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────┐   │
│ │ Calendar                                 │   │
│ │ Full width (sidebar hidden/fixed)        │   │
│ │                                          │   │
│ └──────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘

┌──────────┐  ← Sidebar slides in from left
│ Sidebar  │     when toggle button clicked
│ 320px    │     (position: fixed)
│ Fixed    │     (z-index: 60)
│ Overlay  │
└──────────┘

Grid: 1fr (single column)
Sidebar: Fixed overlay, toggle button
Calendar: Full width


MOBILE (< 768px)
┌──────────────────────┐
│ Calendar             │
│ Full width           │
│ Min height: 500px    │
│                      │
│ (Optimized for       │
│  portrait viewing)   │
└──────────────────────┘

┌──────────┐  ← Sidebar full-width overlay
│ Sidebar  │     (width: 100vw or 320px)
│ Fixed    │
│ Overlay  │
└──────────┘

Grid: 1fr (single column)
Sidebar: Full-width overlay
Calendar: Full width, shorter min-height
```

---

## Diagram 5: CSS Grid vs Flex Comparison

```
GRID LAYOUT (RECOMMENDED)
==========================

.calendar-main-layout {
    display: grid;
    grid-template-columns: 320px 1fr;  ← Explicit widths
    gap: 24px;
}

┌─────────────────────────────────────────┐
│ Grid Container (1872px total)           │
│                                         │
│  [Column 1]     [Gap]    [Column 2]    │
│  320px          24px     1fr = 1528px  │
│  │                        │             │
│  ▼                        ▼             │
│  Sidebar                  Calendar      │
│  (320px)                  (1528px)      │
│                                         │
│  Fixed width              Calculated    │
│  immediately              immediately   │
└─────────────────────────────────────────┘

FullCalendar initializes:
- Measures parent: 1528px ✅
- Renders full width ✅


FLEX LAYOUT (PROBLEMATIC)
==========================

.calendar-main-layout {
    display: flex;
    gap: 24px;
}

.sidebar { flex: 0 0 320px; }
.calendar { flex: 1; }

┌─────────────────────────────────────────┐
│ Flex Container (1872px total)           │
│                                         │
│  [Sidebar]      [Gap]    [Calendar]    │
│  flex: 0 0      24px     flex: 1       │
│  320px                   ???px          │
│  │                       │              │
│  ▼                       ▼              │
│  Sidebar                 Calendar       │
│  (320px)                 (Calculating…) │
│                                         │
│  Sized first             Sized AFTER    │
│                          sidebar        │
└─────────────────────────────────────────┘

FullCalendar initializes:
- Parent width calculating… ⏳
- May measure too early ❌
- Defaults to narrow width ❌


WHY GRID WINS:
==============

GRID:
✅ Explicit column widths (320px, 1fr)
✅ Both columns sized simultaneously
✅ Predictable dimensions before paint
✅ FullCalendar sees real width immediately

FLEX:
❌ flex: 1 requires calculation
❌ Calculated after fixed-width items
❌ May not be ready at initialization
❌ FullCalendar may measure too early
```

---

## Diagram 6: Height Configuration Options

```
HEIGHT CONFIGURATION COMPARISON
================================

OPTION 1: height: 'auto' (Current - Problematic)
┌────────────────────────────────────────┐
│ Calendar Container                     │
│ (No explicit height)                   │
│  ┌──────────────────────────────────┐  │
│  │ FullCalendar                     │  │
│  │ height: 'auto'                   │  │
│  │                                  │  │
│  │ Uses aspectRatio (default 1.35)  │  │
│  │ Height = Width ÷ 1.35            │  │
│  │                                  │  │
│  │ Problem: Unpredictable height    │  │
│  │ based on container width         │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

Example: Container width = 1200px
         Calendar height = 1200 ÷ 1.35 = 888px
         (May not fit viewport)


OPTION 2: height: 'parent' (Recommended)
┌────────────────────────────────────────┐
│ Calendar Container                     │
│ height: calc(100vh - 180px) = 900px    │
│  ┌──────────────────────────────────┐  │
│  │ FullCalendar                     │  │
│  │ height: 'parent'                 │  │
│  │                                  │  │
│  │ Fills parent exactly: 900px      │  │
│  │                                  │  │
│  │ Predictable, viewport-based      │  │
│  │ Always fits screen               │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

Result: Calendar height = 900px
        (Exact match to container)


OPTION 3: height: 800 (Explicit Pixels - Alternative)
┌────────────────────────────────────────┐
│ Calendar Container                     │
│ (Height can be anything)               │
│  ┌──────────────────────────────────┐  │
│  │ FullCalendar                     │  │
│  │ height: 800                      │  │
│  │                                  │  │
│  │ Fixed 800px regardless           │  │
│  │ of container                     │  │
│  │                                  │  │
│  │ Simple, but not responsive       │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

Result: Calendar height = 800px always
        (May overflow or leave space)


OPTION 4: contentHeight: 'auto' (View Area Only)
┌────────────────────────────────────────┐
│ Calendar Container                     │
│  ┌──────────────────────────────────┐  │
│  │ ┌────────────────────────────┐   │  │
│  │ │ Header Toolbar             │   │  │
│  │ │ (Fixed height ~60px)       │   │  │
│  │ └────────────────────────────┘   │  │
│  │ ┌────────────────────────────┐   │  │
│  │ │ View Area                  │   │  │
│  │ │ contentHeight: 'auto'      │   │  │
│  │ │                            │   │  │
│  │ │ Uses aspectRatio for view  │   │  │
│  │ │ Total = view + header      │   │  │
│  │ └────────────────────────────┘   │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

Example: Container width = 1200px
         View height = 1200 ÷ 1.35 = 888px
         Total height = 888 + 60 = 948px


RECOMMENDATION:
===============
Use height: 'parent' with explicit container height
- Most predictable
- Viewport-responsive
- Fills available space exactly
```

---

## Diagram 7: Troubleshooting Decision Tree

```
TROUBLESHOOTING NARROW CALENDAR
================================

Is calendar too narrow?
  │
  ├─ YES → Check container dimensions
  │         │
  │         ├─ Console: document.getElementById('calendar')
  │         │           .getBoundingClientRect()
  │         │
  │         ├─ Width < expected?
  │         │   │
  │         │   ├─ YES → Check parent container
  │         │   │         │
  │         │   │         ├─ Has explicit width?
  │         │   │         │   │
  │         │   │         │   ├─ NO → Add width: 100%
  │         │   │         │   │      Add flex: 1 or grid 1fr
  │         │   │         │   │
  │         │   │         │   └─ YES → Check grid/flex calculation
  │         │   │         │            Is grid column sized correctly?
  │         │   │         │
  │         │   │         └─ Check initialization timing
  │         │   │                Did FullCalendar init too early?
  │         │   │                Add double requestAnimationFrame
  │         │   │
  │         │   └─ NO → Container is correct size
  │         │            Check FullCalendar config
  │         │            Is height: 'parent' set?
  │         │
  │         └─ Height < expected?
  │               │
  │               ├─ YES → Check parent height
  │               │         Use calc(100vh - offset)
  │               │         Add height: 100% on parents
  │               │
  │               └─ NO → Height is correct
  │
  └─ NO → Calendar looks good! ✅


COMMON FIXES:
=============

1. Container has no width
   → Add: width: 100%; flex: 1; or grid 1fr

2. FullCalendar initialized too early
   → Add: requestAnimationFrame × 2

3. Parent container has no height
   → Add: height: calc(100vh - 180px)

4. Using height: 'auto'
   → Change to: height: 'parent'

5. Nested flex/grid conflicts
   → Simplify: Use single grid level

6. Missing handleWindowResize
   → Add: handleWindowResize: true
```

---

## Diagram 8: Event Flow - Window Resize

```
WINDOW RESIZE HANDLING
=======================

User resizes browser window
  │
  ▼
Browser fires 'resize' event
  │
  ▼
FullCalendar detects resize
(if handleWindowResize: true)
  │
  ▼
Debounce delay (100ms default)
(windowResizeDelay: 100)
  │
  ▼
FullCalendar calls updateSize()
  │
  ├─ Re-measure parent container
  ├─ Calculate new dimensions
  ├─ Re-render calendar grid
  └─ Update event positions
  │
  ▼
Calendar smoothly adjusts
to new dimensions ✅


CONFIGURATION:
==============

this.calendar = new FullCalendar.Calendar(el, {
    handleWindowResize: true,     // Enable auto-resize
    windowResizeDelay: 100,        // 100ms debounce
    // ...
});


TIMELINE:
=========

 0ms: Window resize starts
100ms: User still resizing...
200ms: User still resizing...
300ms: User stops resizing
      └─ Last resize event fires
400ms: FullCalendar debounce complete (300ms + 100ms)
      └─ updateSize() called
      └─ Calendar re-renders
410ms: Smooth transition complete ✅


WITHOUT handleWindowResize:
============================

 0ms: Window resize starts
300ms: User stops resizing
      └─ Calendar DOES NOT adjust ❌
      └─ Calendar stays narrow ❌
      └─ User sees broken layout ❌
```

---

## Summary Comparison Table

| Aspect | Current Approach | Recommended Approach |
|--------|------------------|---------------------|
| **Container Structure** | Grid spans (col-3, col-9) | Grid with explicit widths (320px 1fr) |
| **Height Control** | No explicit height | calc(100vh - 180px) |
| **Layout System** | Tailwind Grid only | Grid + Flexbox hybrid |
| **FullCalendar height** | 'auto' (aspectRatio) | 'parent' (fills container) |
| **Initialization** | Immediate render | Double RAF (wait for layout) |
| **Resize Handling** | None | handleWindowResize: true |
| **Dimension Chain** | Implicit (spans) | Explicit (viewport → container → calendar) |
| **Result** | ❌ Narrow calendar | ✅ Full-width calendar |

---

**Next:** Implement recommended architecture from `CALENDAR_ARCHITECTURE_CLEAN.md`

**Reference Documents:**
- `CALENDAR_ARCHITECTURE_CLEAN.md` - Full implementation guide
- `OBCMS_UI_COMPONENTS_STANDARDS.md` - UI component standards
- FullCalendar Sizing Docs - https://fullcalendar.io/docs/sizing
