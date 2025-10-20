# Hybrid Calendar - Visual Implementation Guide

**Component:** OOBC Calendar
**Template:** `src/templates/common/oobc_calendar.html`
**Status:** COMPLETE

---

## Layout Visualization

### Desktop View (≥1024px)

```
┌───────────────────────────────────────────────────────────────────────┐
│                         HERO SECTION                                  │
│  🗓️  OOBC Calendar                                 [Create] [Advanced]│
│  Organization-wide schedule view                                       │
└───────────────────────────────────────────────────────────────────────┘

┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total       │ Upcoming    │ In Progress │ Completed   │
│ 💼 42       │ 📅 12       │ 🔄 18       │ ✅ 12       │
└─────────────┴─────────────┴─────────────┴─────────────┘

┌──────────────┬──────────────────────────────────────────────┐
│  📆 Calendar │  [Month] [Week] [Day] [Year]  ⏪ [Today] ⏩ │
│              ├──────────────────────────────────────────────┤
│  October 2025│                                              │
│  Su Mo Tu... │          FullCalendar                        │
│   1  2  3... │          📅 Main View                        │
│              │                                              │
│  Event Types │          (Events with icons)                 │
│  ✅ Projects │                                              │
│  ✅ Activity │                                              │
│  ✅ Tasks    │                                              │
│  ✅ Coord    │                                              │
│              │                                              │
│  Options     │                                              │
│  ☐ Completed │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### Desktop with Detail Panel Open

```
┌───────────────────────────────────────────────────────────────────────┐
│                         HERO SECTION                                  │
│  🗓️  OOBC Calendar                                 [Create] [Advanced]│
└───────────────────────────────────────────────────────────────────────┘

┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total       │ Upcoming    │ In Progress │ Completed   │
│ 💼 42       │ 📅 12       │ 🔄 18       │ ✅ 12       │
└─────────────┴─────────────┴─────────────┴─────────────┘

┌──────────┬─────────────────────────────┬────────────────┐
│ Sidebar  │  Header                     │ Event Details  │
│          ├─────────────────────────────┤                │
│ Mini Cal │  FullCalendar               │ Project X      │
│          │                             │ Status: Active │
│ Filters  │  (Resized for detail panel) │                │
│          │                             │ Description... │
│          │                             │                │
│          │                             │ [Edit] [Delete]│
└──────────┴─────────────────────────────┴────────────────┘
   280px              1fr (flexible)           380px
```

### Desktop with Sidebar Collapsed

```
┌───────────────────────────────────────────────────────────────────────┐
│                         HERO SECTION                                  │
│  🗓️  OOBC Calendar                                 [Create] [Advanced]│
└───────────────────────────────────────────────────────────────────────┘

┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total       │ Upcoming    │ In Progress │ Completed   │
│ 💼 42       │ 📅 12       │ 🔄 18       │ ✅ 12       │
└─────────────┴─────────────┴─────────────┴─────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  ➡️ [Month] [Week] [Day] [Year]  ⏪ [Today] ⏩                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                FullCalendar (Full Width)                             │
│                                                                      │
│                (More space for calendar)                             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Mobile View (<1024px)

```
┌─────────────────────────────────┐
│   HERO SECTION                  │
│   🗓️  OOBC Calendar             │
│   [Create] [Advanced]           │
└─────────────────────────────────┘

┌────────────┬────────────┐
│ Total      │ Upcoming   │
│ 💼 42      │ 📅 12      │
├────────────┼────────────┤
│ In Prog    │ Completed  │
│ 🔄 18      │ ✅ 12      │
└────────────┴────────────┘

┌─────────────────────────────────┐
│ ☰ Calendar View                 │
├─────────────────────────────────┤
│ [Month] [Week] [Day] [Year]     │
│ ⏪ [Today] ⏩                    │
├─────────────────────────────────┤
│                                 │
│    FullCalendar                 │
│    (Full Width)                 │
│                                 │
└─────────────────────────────────┘

(Sidebar and Detail Panel overlay when opened)
```

---

## Grid Layout Technical Diagram

```css
.calendar-page-container {
    grid-template-columns: 280px  1fr  0px;
    grid-template-rows:    auto auto auto 1fr;
}

         Col 1          Col 2         Col 3
       (280px)         (1fr)         (0px)
    ┌──────────┬─────────────────┬─────────┐
Row │          │                 │         │
1   │  HERO SECTION (spans 1/4) │         │ auto
    │          │                 │         │
    ├──────────┼─────────────────┼─────────┤
Row │          │                 │         │
2   │  STATS BAR (spans 1/4)    │         │ auto
    │          │                 │         │
    ├──────────┼─────────────────┼─────────┤
Row │ Sidebar  │  Header         │ Detail  │
3   │ (row 3-5)│  (row 3)        │ (row 3-5│ auto
    │          │                 │   0px)  │
    ├──────────┼─────────────────┼─────────┤
Row │ Sidebar  │  Calendar       │ Detail  │
4   │ (cont.)  │  (row 4)        │ (cont.) │ 1fr
    │          │                 │         │
    └──────────┴─────────────────┴─────────┘

When detail panel opens:
    grid-template-columns: 280px 1fr 380px;
```

---

## Color Palette Reference

### Work Type Colors (Events)

```
Projects       Activities     Tasks          Coordination
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ #3b82f6 │   │ #10b981 │   │ #d97706 │   │ #14b8a6 │
│  Blue   │   │  Green  │   │  Gold   │   │  Teal   │
│ 📁      │   │ ✓       │   │ ☑       │   │ 🤝      │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

### Stat Card Colors (Icons)

```
Total          Upcoming       In Progress    Completed
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ #f59e0b │   │ #3b82f6 │   │ #8b5cf6 │   │ #10b981 │
│  Amber  │   │  Blue   │   │ Purple  │   │ Emerald │
│ 💼      │   │ 📅      │   │ 🔄      │   │ ✅      │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

---

## Sidebar Components

### Mini Calendar

```
┌──────────────────────────┐
│ ⏪ October 2025 ⏩       │
├──────────────────────────┤
│ Su Mo Tu We Th Fr Sa     │
│     1  2  3  4  5  6     │
│  7  8  9 [10]11 12 13    │  ← Today (blue)
│ 14 15 16 17 18 19 20     │
│ 21 22 23 24 25 26 27     │
│ 28 29 30 31              │
└──────────────────────────┘
```

### Event Type Filters

```
Event Types
┌──────────────────────────┐
│ 📁 Projects         ☑    │ ← Active (green check)
│ ✓  Activities       ☑    │
│ ☑  Tasks            ☑    │
│ 🤝 Coordination     ☐    │ ← Inactive (no check)
└──────────────────────────┘

Options
┌──────────────────────────┐
│ ✅ Show Completed   ☐    │
└──────────────────────────┘
```

---

## Calendar Header

```
┌────────────────────────────────────────────────────────────┐
│ ⏪ Calendar View                                           │
│                                                            │
│ [Month] [Week] [Day] [Year]  ⏪ [Today] ⏩                │
│  ^^^^^^                       ^^^^^^^^^^^^                 │
│  View Mode Tabs               Navigation                   │
└────────────────────────────────────────────────────────────┘
```

---

## Event Display with Icons

### Month View

```
┌──────────────────────────────────────────┐
│ OCTOBER 2025                             │
├──────────────────────────────────────────┤
│ Sun    Mon    Tue    Wed    Thu    Fri   │
│        1      2      3      4      5      │
│        📁 Project X                       │
│        ✓ Activity Y                       │
│                                           │
│  6      7      8      9      10     11    │
│        ☑ Task Z                           │
│        🤝 Meeting A                        │
└──────────────────────────────────────────┘
```

### Week View

```
┌────────────────────────────────────────────┐
│ 8:00  📁 Project X (9:00-11:00)            │
│ 9:00                                       │
│10:00  ✓ Activity Y (10:30-12:00)          │
│11:00                                       │
│12:00                                       │
│ 1:00  ☑ Task Z (1:00-2:00)                │
│ 2:00  🤝 Meeting A (2:00-3:00)             │
└────────────────────────────────────────────┘
```

### Year View (NEW)

```
┌─────────────────────────────────────────────┐
│ 2025                                        │
├───────┬───────┬───────┬───────┬───────┬────┤
│ Jan   │ Feb   │ Mar   │ Apr   │ May   │ Jun│
├───────┼───────┼───────┼───────┼───────┼────┤
│ Jul   │ Aug   │ Sep   │ Oct   │ Nov   │ Dec│
└───────┴───────┴───────┴───────┴───────┴────┘
```

---

## Detail Panel (HTMX)

```
┌────────────────────────┐
│ Event Details      [X] │ ← Close button
├────────────────────────┤
│                        │
│ 📁 Project X           │
│                        │
│ Status: In Progress    │
│ Due: Oct 15, 2025      │
│                        │
│ Description:           │
│ Lorem ipsum dolor...   │
│                        │
│ Assignee: John Doe     │
│                        │
│ [Edit] [Delete]        │
│                        │
└────────────────────────┘
```

---

## Responsive Breakpoints

| Breakpoint | Width | Sidebar | Detail Panel | Stats Grid |
|------------|-------|---------|--------------|------------|
| Desktop    | ≥1024px | Integrated (280px) | Slide-in (380px) | 4 columns |
| Tablet     | 768-1023px | Overlay | Overlay | 4 columns |
| Mobile     | <768px | Overlay | Overlay (full) | 2 columns |

---

## Toggle States

### Sidebar Toggle Icons

| Context | State | Icon | Action |
|---------|-------|------|--------|
| Desktop | Visible | `fa-chevron-left` | Collapse sidebar |
| Desktop | Collapsed | `fa-chevron-right` | Expand sidebar |
| Mobile | Hidden | `fa-bars` | Show overlay |
| Mobile | Visible | `fa-times` | Hide overlay |

---

## Interaction Flows

### Opening Event Details

```
User clicks event
      ↓
JavaScript intercepts click
      ↓
Prevent default link behavior
      ↓
Extract work item ID
      ↓
Show loading spinner in detail panel
      ↓
HTMX GET request to:
/oobc-management/work-items/{id}/sidebar/detail/
      ↓
Load HTML into detail panel body
      ↓
Slide detail panel in (0px → 380px)
      ↓
Adjust grid: 280px 1fr 0px → 280px 1fr 380px
```

### Filtering Events

```
User clicks filter checkbox
      ↓
Update activeFilters state
      ↓
Update checkbox UI (green check)
      ↓
Update label active state
      ↓
Call calendar.refetchEvents()
      ↓
Fetch events from API
      ↓
Apply filters (applyFilters function)
      ↓
Render filtered events on calendar
```

---

## CSS Transitions

```css
/* Grid column transition */
.calendar-page-container {
    transition: grid-template-columns 300ms ease-in-out;
}

/* Detail panel slide-in */
.calendar-detail-panel {
    transition: all 300ms ease-in-out;
}

/* Sidebar collapse */
.calendar-sidebar {
    transition: transform 300ms ease-in-out;
}

/* Backdrop fade */
.detail-panel-backdrop {
    transition: opacity 300ms ease-in-out;
}
```

---

## Key Features Visual Summary

| Feature | Visual Indicator | Color | Icon |
|---------|------------------|-------|------|
| Projects | Blue event | #3b82f6 | 📁 fa-folder |
| Activities | Green event | #10b981 | ✓ fa-calendar-check |
| Tasks | Gold event | #d97706 | ☑ fa-tasks |
| Coordination | Teal event | #14b8a6 | 🤝 fa-handshake |
| Completed | Gray event (when shown) | - | ✅ |
| Today | Blue highlight | #3b82f6 | - |
| Selected Date | Green highlight | #10b981 | - |

---

## Accessibility Features

✅ ARIA labels on all buttons
✅ Keyboard navigation support
✅ Focus indicators on interactive elements
✅ High contrast colors (WCAG AA)
✅ Touch targets ≥48px on mobile
✅ Screen reader friendly structure

---

## Browser Compatibility

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+
✅ Mobile Safari (iOS 14+)
✅ Chrome Mobile (Android 10+)

---

## Performance Optimizations

✅ CSS Grid (hardware accelerated)
✅ CSS Transitions (GPU compositing)
✅ RequestAnimationFrame for calendar init
✅ Lazy loading of detail panel content
✅ Debounced window resize handler
✅ Minimal DOM manipulation

---

This visual guide provides a comprehensive reference for understanding the hybrid calendar implementation. Use it alongside `HYBRID_CALENDAR_REFACTORING_SUMMARY.md` for complete documentation.
