# Calendar Visual States Reference

**Purpose:** Visual reference for expected calendar states during width expansion testing.

**Component:** Advanced Modern Calendar
**File:** `src/templates/common/calendar_advanced_modern.html`
**Date:** 2025-10-06

---

## Desktop States (Viewport ≥ 1024px)

### State 1: Sidebar Visible (Initial Load)

```
┌────────────────────────────────────────────────────────────────────────┐
│ [≡] Advanced Modern Calendar      [Month][Week][Day][Year] [<][Today][>]│
├──────────────┬─────────────────────────────────────────────────────────┤
│              │                                                         │
│  Calendar    │                   CALENDAR GRID                         │
│  ----------  │                                                         │
│  Jan 2025    │  Sun   Mon   Tue   Wed   Thu   Fri   Sat               │
│              │   29    30    31     1     2     3     4                │
│  Event Types │    5     6     7     8     9    10    11                │
│  ✓ Projects  │   12    13    14    15    16    17    18                │
│  ✓ Activities│   19    20    21    22    23    24    25                │
│  ✓ Tasks     │   26    27    28    29    30    31     1                │
│  ✓ Coord.    │                                                         │
│              │                                                         │
│  Options     │                                                         │
│  ☐ Completed │                                                         │
│              │                                                         │
│  [< Classic] │                                                         │
│              │                                                         │
└──────────────┴─────────────────────────────────────────────────────────┘
    280px                        ~1640px (on 1920px screen)

Grid: 280px | 1fr | 0px
Icon: fa-chevron-left (←)
```

**Visual Characteristics:**
- Toggle button shows **chevron-left (←)**
- Sidebar occupies 280px on the left
- Calendar fills remaining space (~1640px on 1920px screen)
- Grid columns: `280px 1fr 0px`

---

### State 2: Sidebar Collapsed (After First Toggle)

```
┌────────────────────────────────────────────────────────────────────────┐
│ [>] Advanced Modern Calendar      [Month][Week][Day][Year] [<][Today][>]│
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                       CALENDAR GRID (FULL WIDTH)                       │
│                                                                        │
│    Sun      Mon      Tue      Wed      Thu      Fri      Sat          │
│     29       30       31        1        2        3        4           │
│      5        6        7        8        9       10       11           │
│     12       13       14       15       16       17       18           │
│     19       20       21       22       23       24       25           │
│     26       27       28       29       30       31        1           │
│                                                                        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
                           ~1920px (full width)

Grid: 0px | 1fr | 0px
Icon: fa-chevron-right (→)
```

**Visual Characteristics:**
- Toggle button shows **chevron-right (→)**
- Sidebar is hidden (transformed -100%, grid column 0px)
- Calendar expands to full viewport width (~1920px)
- Grid columns: `0px 1fr 0px`
- Transition: **300ms smooth animation**

**Animation Sequence:**
1. Click toggle button
2. Grid columns animate from `280px 1fr 0px` to `0px 1fr 0px` (300ms)
3. Sidebar slides out to left (transform: translateX(-100%))
4. Icon changes from ← to →
5. After 350ms: `calendar.updateSize()` is called
6. Calendar expands to fill new width

---

### State 3: Sidebar Restored (After Second Toggle)

```
[Returns to State 1]

Grid: 280px | 1fr | 0px
Icon: fa-chevron-left (←)
Calendar width: ~1640px
```

**Animation Sequence:**
1. Click toggle button
2. Grid columns animate from `0px 1fr 0px` to `280px 1fr 0px` (300ms)
3. Sidebar slides in from left (transform: translateX(0))
4. Icon changes from → to ←
5. After 350ms: `calendar.updateSize()` is called
6. Calendar contracts to sidebar-visible width

---

## Mobile States (Viewport < 1024px)

### State 1: Sidebar Closed (Initial Load)

```
┌──────────────────────┐
│ [☰] Advanced Modern  │
│ Calendar             │
├──────────────────────┤
│                      │
│   CALENDAR GRID      │
│                      │
│  S  M  T  W  T  F  S │
│ 29 30 31  1  2  3  4 │
│  5  6  7  8  9 10 11 │
│ 12 13 14 15 16 17 18 │
│ 19 20 21 22 23 24 25 │
│ 26 27 28 29 30 31  1 │
│                      │
│                      │
└──────────────────────┘
       375px

Sidebar: translateX(-100%)
Icon: fa-bars (☰)
```

**Visual Characteristics:**
- Toggle button shows **bars (☰)**
- Sidebar is off-screen (position: fixed, transform: translateX(-100%))
- Calendar fills full viewport width
- Grid columns: `0px 1fr 0px` (mobile layout)

---

### State 2: Sidebar Open (After Toggle)

```
┌──────────┐
│ [×]      │
│ Calendar │
│ -------- │
│ Jan 2025 │◄─── Sidebar overlay
│          │
│ Events   │
│ ✓ Proj   │
│ ✓ Act    │    ┌─────────────┐
│ ✓ Task   │    │  CALENDAR   │
│          │    │  (behind)   │
│ Options  │    │             │
│ ☐ Compl  │    │             │
│          │    └─────────────┘
└──────────┘
   280px          [Backdrop]

Sidebar: translateX(0)
Icon: fa-times (×)
Backdrop: visible with opacity
```

**Visual Characteristics:**
- Toggle button shows **times (×)**
- Sidebar slides in from left (position: fixed, transform: translateX(0))
- Backdrop appears behind sidebar (rgba(0,0,0,0.3))
- Calendar remains at full width (unchanged)
- Close button (×) visible in sidebar header

**Animation Sequence:**
1. Click toggle button
2. Sidebar slides in from left (300ms)
3. Backdrop fades in (opacity 0 → 1, 300ms)
4. Icon changes from ☰ to ×
5. Calendar width remains unchanged (no resize needed)

---

### State 3: Sidebar Closed (After Close)

```
[Returns to State 1]

Sidebar: translateX(-100%)
Icon: fa-bars (☰)
Backdrop: hidden
```

**Close Methods:**
1. Click toggle button (×)
2. Click backdrop overlay
3. Click close button in sidebar header

---

## Icon Reference

### Desktop Icons

**Chevron Left (←)**
```html
<i class="fas fa-chevron-left text-gray-600"></i>
```
**Meaning:** Sidebar is visible, click to collapse

**Chevron Right (→)**
```html
<i class="fas fa-chevron-right text-gray-600"></i>
```
**Meaning:** Sidebar is hidden, click to expand

### Mobile Icons

**Bars (☰)**
```html
<i class="fas fa-bars text-gray-600"></i>
```
**Meaning:** Sidebar is closed, click to open

**Times (×)**
```html
<i class="fas fa-times text-gray-600"></i>
```
**Meaning:** Sidebar is open, click to close

---

## Grid Columns Reference

### Desktop

| State             | Grid Columns        | Description                    |
|-------------------|---------------------|--------------------------------|
| Sidebar Visible   | `280px 1fr 0px`     | Sidebar 280px, calendar fills  |
| Sidebar Collapsed | `0px 1fr 0px`       | No sidebar, calendar full width|
| Detail Panel Open | `280px 1fr 380px`   | Sidebar + calendar + detail    |

### Mobile

| State             | Grid Columns        | Description                    |
|-------------------|---------------------|--------------------------------|
| All states        | `0px 1fr 0px`       | Calendar always full width     |

---

## CSS Classes Reference

### Desktop Classes

**Sidebar Collapsed:**
```html
<div class="calendar-container sidebar-collapsed">
```
- Triggers grid columns: `0px 1fr 0px`
- Sidebar transforms: `translateX(-100%)`

### Mobile Classes

**Sidebar Open:**
```html
<aside class="calendar-sidebar open">
```
- Position: fixed
- Transforms: `translateX(0)`

**Backdrop Visible:**
```html
<div class="detail-panel-backdrop open">
```
- Opacity: 1
- Pointer events: auto

---

## Transition Timings

| Component           | Duration | Easing       | Property               |
|---------------------|----------|--------------|------------------------|
| Grid columns        | 300ms    | ease-in-out  | grid-template-columns  |
| Sidebar transform   | 300ms    | ease-in-out  | transform              |
| Backdrop opacity    | 300ms    | ease-in-out  | opacity                |
| Calendar resize     | 350ms    | -            | Delayed `updateSize()` |

---

## Width Calculations

### Desktop (1920px viewport)

**Sidebar Visible:**
- Container width: 1920px
- Sidebar: 280px (grid column 1)
- Calendar: ~1640px (grid column 2, 1fr = 1920px - 280px)
- Detail panel: 0px (grid column 3, hidden)

**Sidebar Collapsed:**
- Container width: 1920px
- Sidebar: 0px (grid column 1, hidden)
- Calendar: ~1920px (grid column 2, 1fr = 1920px)
- Detail panel: 0px (grid column 3, hidden)

**Width Increase:** ~280px (sidebar width)

### Mobile (375px viewport)

**All states:**
- Container width: 375px
- Calendar: 375px (always full width)
- Sidebar: 280px (overlay, does not affect calendar)

**Width Change:** 0px (calendar width unchanged)

---

## Expected Browser Rendering

### Chrome/Edge DevTools

**Computed Styles (Sidebar Visible):**
```
.calendar-container {
  display: grid;
  grid-template-columns: 280px 1fr 0px;
  transition: grid-template-columns 300ms ease-in-out;
}
```

**Computed Styles (Sidebar Collapsed):**
```
.calendar-container.sidebar-collapsed {
  grid-template-columns: 0px 1fr 0px;
}
```

### Firefox DevTools

**Grid Inspector:**
- Shows 3 columns
- Column 1: 280px (or 0px when collapsed)
- Column 2: 1fr (expands to fill)
- Column 3: 0px (detail panel hidden)

---

## Accessibility States

### Toggle Button ARIA

```html
<button class="sidebar-toggle-btn"
        id="toggleSidebarBtn"
        aria-label="Toggle sidebar">
  <i class="fas fa-chevron-left text-gray-600" id="sidebarToggleIcon"></i>
</button>
```

**States:**
- Default: `aria-label="Toggle sidebar"`
- Could enhance with `aria-expanded="true/false"`

---

## Visual Verification Checklist

### Desktop

- [ ] Initial load shows chevron-left (←)
- [ ] Clicking toggle changes icon to chevron-right (→)
- [ ] Sidebar slides out smoothly (300ms)
- [ ] Calendar expands to full width
- [ ] No horizontal scrollbar appears
- [ ] Clicking toggle again restores chevron-left (←)
- [ ] Sidebar slides back in smoothly
- [ ] Calendar contracts to original width

### Mobile

- [ ] Initial load shows bars (☰)
- [ ] Clicking toggle changes icon to times (×)
- [ ] Sidebar slides in from left
- [ ] Backdrop appears behind sidebar
- [ ] Calendar width remains unchanged
- [ ] Clicking backdrop closes sidebar
- [ ] Icon changes back to bars (☰)

---

## Troubleshooting Visual Issues

### Calendar Doesn't Expand Visually

**Check:**
1. Grid columns in DevTools (should change to `0px 1fr 0px`)
2. Calendar element width in Computed panel
3. FullCalendar `.fc` element width
4. Horizontal scrollbar presence (indicates width overflow)

**Expected:**
- Grid columns update immediately
- Calendar width updates after 350ms
- No scrollbar (calendar should fit perfectly)

### Icon Shows Wrong Symbol

**Check:**
1. Icon element className
2. Viewport width (desktop vs mobile threshold at 1024px)
3. Sidebar state (collapsed or open)
4. Console errors blocking icon update

**Expected:**
- Desktop: chevron-left or chevron-right
- Mobile: bars or times
- No console errors

### Sidebar Doesn't Slide

**Check:**
1. CSS transition property
2. Transform value in Computed styles
3. Grid column value
4. JavaScript toggle function execution

**Expected:**
- Smooth 300ms transition
- Transform changes from translateX(0) to translateX(-100%)
- No janky animation

---

## Related Documentation

- **[Calendar Width Expansion Testing Guide](CALENDAR_WIDTH_EXPANSION_TESTING_GUIDE.md)** - Full testing procedures
- **[verify_calendar_expansion.js](verify_calendar_expansion.js)** - Automated test script
- **[Calendar Debug Snippet](CALENDAR_DEBUG_SNIPPET.md)** - Debug logging code

---

**Last Updated:** 2025-10-06
**Status:** Visual Reference Guide
