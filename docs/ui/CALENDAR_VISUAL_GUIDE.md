# OBCMS Calendar Visual Guide

Visual overview of the three calendar implementations in OBCMS.

---

## Layout Comparison

### Calendar #1: Classic Unified
```
┌─────────────────────────────────────────────────────────────┐
│  Header: Unified Calendar                        [Filters]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│               FullCalendar (Month View)                      │
│                                                               │
│   ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐      │
│   │  Su  │  Mo  │  Tu  │  We  │  Th  │  Fr  │  Sa  │      │
│   ├──────┼──────┼──────┼──────┼──────┼──────┼──────┤      │
│   │      │      │   1  │   2  │   3  │   4  │   5  │      │
│   │ [📅] │      │      │ [📅] │      │      │      │      │
│   ├──────┼──────┼──────┼──────┼──────┼──────┼──────┤      │
│   │   6  │   7  │   8  │   9  │  10  │  11  │  12  │      │
│   │      │ [📅] │      │      │      │      │      │      │
│   └──────┴──────┴──────┴──────┴──────┴──────┴──────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```
**Features:**
- Single panel
- Server-side filtering
- Modal for details
- Basic responsiveness

---

### Calendar #2: Coordination
```
┌─────────────────────────────────────────────────────────────┐
│  Header: Coordination Calendar              [Resource List] │
├───────────────────────────────┬─────────────────────────────┤
│                               │                             │
│   FullCalendar (Month View)   │    Resource Booking        │
│                               │                             │
│   ┌──────┬──────┬──────┐     │   📅 Room A                │
│   │  Su  │  Mo  │  Tu  │     │   ├─ Available             │
│   ├──────┼──────┼──────┤     │   └─ Book Now              │
│   │      │      │   1  │     │                             │
│   │ [📅] │      │      │     │   📅 Room B                │
│   ├──────┼──────┼──────┤     │   ├─ Booked (3pm-5pm)      │
│   │   6  │   7  │   8  │     │   └─ View Schedule         │
│   │      │ [📅] │      │     │                             │
│   └──────┴──────┴──────┘     │   📅 Room C                │
│                               │   └─ Available             │
│                               │                             │
└───────────────────────────────┴─────────────────────────────┘
```
**Features:**
- Two-panel layout
- Resource booking
- Partnership focus
- Team collaboration

---

### Calendar #3: Advanced Modern ⭐
```
┌──────────┬─────────────────────────────────────────┬──────────┐
│          │  Header: Advanced Modern Calendar       │          │
│  SIDEBAR │  [Month] [Week] [Day] [Year]  [Create] │          │
│          ├─────────────────────────────────────────┤  DETAIL  │
│  Mini    │                                         │  PANEL   │
│  Cal     │       FullCalendar (Month View)         │          │
│ ┌─────┐  │                                         │ ┌──────┐ │
│ │Oct  │  │   ┌──────┬──────┬──────┬──────┬──────┐ │ │Event │ │
│ │2025 │  │   │  Mo  │  Tu  │  We  │  Th  │  Fr  │ │ │Title │ │
│ └─────┘  │   ├──────┼──────┼──────┼──────┼──────┤ │ └──────┘ │
│          │   │   1  │   2  │   3  │   4  │   5  │ │          │
│ Legend:  │   │ [📘] │      │ [📗] │      │      │ │ 📅 Date  │
│ 📘 Proj  │   ├──────┼──────┼──────┼──────┼──────┤ │          │
│ 📗 Act   │   │   6  │   7  │   8  │   9  │  10  │ │ 📊 Status│
│ 📙 Task  │   │      │ [📙] │      │ [📘] │      │ │          │
│ 📕 Coord │   └──────┴──────┴──────┴──────┴──────┘ │ 🎯 Prior │
│          │                                         │          │
│ Filters: │                                         │ 👥 Team  │
│ ☑ Proj   │                                         │          │
│ ☑ Act    │                                         │ [View]   │
│ ☑ Task   │                                         │ [Full]   │
│ ☐ Done   │                                         │          │
│          │                                         │          │
│ [Clear]  │                                         │ [ X ]    │
│          │                                         │          │
└──────────┴─────────────────────────────────────────┴──────────┘
```
**Features:**
- Three-panel layout
- Mini calendar navigation
- Client-side filtering
- Slide-in detail panel
- Year view support
- localStorage persistence

---

## Color Coding System

### Event Type Colors

```
Projects:      📘 Blue      #3b82f6  ████████
Activities:    📗 Emerald   #10b981  ████████
Tasks:         📙 Purple    #8b5cf6  ████████
Coordination:  📕 Teal      #14b8a6  ████████
```

### Status Colors (Badges)

```
Not Started:   ⚪ Gray      #9ca3af  ████████
In Progress:   🔵 Blue      #3b82f6  ████████
Completed:     🟢 Green     #10b981  ████████
On Hold:       🟡 Yellow    #f59e0b  ████████
Cancelled:     🔴 Red       #ef4444  ████████
```

### Priority Colors (Flags)

```
Low:           🏳️ Gray      #6b7280  ████████
Medium:        🏳️ Blue      #3b82f6  ████████
High:          🏳️ Orange    #f97316  ████████
Critical:      🏴 Red       #dc2626  ████████
```

---

## Responsive Layouts

### Desktop (≥1024px)

**Calendar #3: Advanced Modern**
```
┌──────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ┌────────┬─────────────────────────────────────────┬──────────┐ │
│  │        │                                         │          │ │
│  │  280px │              Flexible Width             │  380px   │ │
│  │        │                                         │          │ │
│  │ Sidebar│           Main Calendar                 │  Detail  │ │
│  │        │                                         │  Panel   │ │
│  │        │                                         │          │ │
│  └────────┴─────────────────────────────────────────┴──────────┘ │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

### Tablet (640px - 1024px)

**Calendar #3: Collapsible Sidebar**
```
┌──────────────────────────────────────────────────────────────┐
│  [☰]  Advanced Modern Calendar                               │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│                                                                │
│                   Main Calendar (Full Width)                  │
│                                                                │
│                                                                │
└──────────────────────────────────────────────────────────────┘

Sidebar (overlay when opened):
┌────────────┐
│            │
│  Sidebar   │───┐
│  280px     │   │
│            │   │← Backdrop (dimmed)
│            │   │
│  [×]       │───┘
└────────────┘

Detail Panel (overlay when opened):
                  ┌────────────┐
        ──────────│            │
        Backdrop →│  Detail    │
         (dimmed) │  380px     │
        ──────────│            │
                  │       [×]  │
                  └────────────┘
```

---

### Mobile (<640px)

**Calendar #3: Full-Screen Overlays**
```
┌─────────────────────┐
│  [☰] Calendar       │
├─────────────────────┤
│                     │
│   Main Calendar     │
│   (Full Screen)     │
│                     │
│                     │
│                     │
│                     │
│                     │
└─────────────────────┘

Sidebar (full overlay):
┌─────────────────────┐
│  Calendar      [×]  │
├─────────────────────┤
│                     │
│  Mini Calendar      │
│                     │
│  Legend             │
│                     │
│  Filters            │
│                     │
│  [Clear]            │
│                     │
└─────────────────────┘

Detail Panel (full overlay):
┌─────────────────────┐
│  Event Details [×]  │
├─────────────────────┤
│                     │
│  📘 Project         │
│                     │
│  Title: ...         │
│  Date: ...          │
│  Status: ...        │
│  Priority: ...      │
│                     │
│  [View Full]        │
│                     │
└─────────────────────┘
```

---

## Interactive Elements

### Mini Calendar (Calendar #3)

```
┌─────────────────────────┐
│  ◀  October 2025  ▶    │
├────┬────┬────┬────┬────┤
│ Su │ Mo │ Tu │ We │ Th │
├────┼────┼────┼────┼────┤
│    │    │  1 │  2 │  3 │
│    │    │ 🟦 │    │    │  ← Clickable date
├────┼────┼────┼────┼────┤
│  6 │  7 │  8 │  9 │ 10 │
│    │ 🟩 │    │    │    │  🟦 = Today (blue)
├────┼────┼────┼────┼────┤  🟩 = Selected (emerald)
│ 13 │ 14 │ 15 │ 16 │ 17 │
│    │    │    │    │    │
└────┴────┴────┴────┴────┘
```

**Interactions:**
- Click date → Jump to that date in main calendar
- Click ◀ ▶ → Navigate months
- Hover → Subtle background change
- Keyboard: Arrow keys navigate

---

### Filter Checkboxes (Calendar #3)

```
┌─────────────────────────┐
│  Filters                │
├─────────────────────────┤
│                         │
│  ☑ Show Projects        │  ← Checked (visible)
│  ☑ Show Activities      │  ← Checked (visible)
│  ☑ Show Tasks           │  ← Checked (visible)
│  ☐ Show Completed       │  ← Unchecked (hidden)
│                         │
│  [Clear Filters]        │  ← Reset button
│                         │
└─────────────────────────┘
```

**Interactions:**
- Click checkbox → Instant filter (no reload)
- Click "Clear Filters" → Reset to defaults
- Visual feedback: Checkmark animation
- Accessible: Keyboard (Space/Enter)

---

### View Mode Buttons (Calendar #3)

```
┌────────────────────────────────────────┐
│  [Month] [Week] [Day] [Year]          │
│    🔵                                  │
│    └─ Active indicator                │
└────────────────────────────────────────┘

Hover state:
┌────────────────────────────────────────┐
│  [Month] [Week] [Day] [Year]          │
│           ^^^^                         │
│           └─ Hover background          │
└────────────────────────────────────────┘
```

**States:**
- **Default:** Gray text, transparent background
- **Hover:** Gray background, darker text
- **Active:** White background, dark text, shadow
- **Transitions:** 150ms ease-in-out

---

### Detail Panel Slide Animation (Calendar #3)

```
State 1: Closed (width: 0, opacity: 0)
┌─────────────────────────────────┐
│                                 │
│   Main Calendar                 │
│                                 │
└─────────────────────────────────┘

State 2: Opening (transition: 300ms)
┌─────────────────────────┬──────┐
│                         │      │
│   Main Calendar         │  Det │ ← Sliding in
│                         │      │
└─────────────────────────┴──────┘

State 3: Open (width: 380px, opacity: 1)
┌─────────────────┬───────────────┐
│                 │               │
│  Main Calendar  │  Detail Panel │
│                 │               │
└─────────────────┴───────────────┘
```

**Animation:**
- **Duration:** 300ms
- **Easing:** ease-in-out
- **Properties:** width, opacity, transform
- **Hardware accelerated:** Yes (GPU)

---

## Event Display Patterns

### Month View

```
┌────────────────────────────────────────────────────┐
│                    October 2025                     │
├──────┬──────┬──────┬──────┬──────┬──────┬──────────┤
│  Mo  │  Tu  │  We  │  Th  │  Fr  │  Sa  │    Su    │
├──────┼──────┼──────┼──────┼──────┼──────┼──────────┤
│      │      │   1  │   2  │   3  │   4  │     5    │
│      │      │ 📘 P │      │ 📗 A │      │          │
│      │      │      │      │      │      │          │
├──────┼──────┼──────┼──────┼──────┼──────┼──────────┤
│   6  │   7  │   8  │   9  │  10  │  11  │    12    │
│ 📙 T │      │ 📘 P │      │      │ 📗 A │          │
│      │      │ 📗 A │      │      │      │          │
├──────┼──────┼──────┼──────┼──────┼──────┼──────────┤
│  13  │  14  │  15  │  16  │  17  │  18  │    19    │
│      │      │      │      │      │      │          │
└──────┴──────┴──────┴──────┴──────┴──────┴──────────┘

Legend: 📘 Project  📗 Activity  📙 Task  📕 Coordination
```

---

### Week View

```
┌────────────────────────────────────────────────────┐
│              Week of October 1, 2025               │
├──────┬──────────────────────────────────────┬─────┤
│ Time │  Mo   Tu   We   Th   Fr   Sa   Su   │     │
├──────┼──────────────────────────────────────┼─────┤
│ 8am  │                                      │     │
├──────┼──────────────────────────────────────┼─────┤
│ 9am  │       ┌──────────────┐              │     │
│      │       │ 📘 Project   │              │     │
├──────┼───────┤   Meeting    │──────────────┼─────┤
│ 10am │       │              │              │     │
│      │       └──────────────┘              │     │
├──────┼──────────────────────────────────────┼─────┤
│ 11am │                            ┌────────┐│     │
│      │                            │📗 Act  ││     │
├──────┼────────────────────────────┤        │┼─────┤
│ 12pm │                            └────────┘│     │
├──────┼──────────────────────────────────────┼─────┤
│ 1pm  │                                      │     │
└──────┴──────────────────────────────────────┴─────┘
```

---

### Day View

```
┌─────────────────────────────┐
│     Wednesday, Oct 3        │
├──────┬──────────────────────┤
│ 8am  │                      │
├──────┼──────────────────────┤
│ 9am  │  ┌────────────────┐  │
│      │  │ 📘 Project     │  │
│      │  │    Meeting     │  │
├──────┼──┤                │  │
│ 10am │  │  Conference    │  │
│      │  │  Room A        │  │
├──────┼──┤                │  │
│ 11am │  │                │  │
│      │  └────────────────┘  │
├──────┼──────────────────────┤
│ 12pm │                      │
├──────┼──────────────────────┤
│ 1pm  │  ┌────────────────┐  │
│      │  │ 📗 Activity    │  │
│      │  │    Workshop    │  │
├──────┼──┴────────────────┘  │
│ 2pm  │                      │
└──────┴──────────────────────┘
```

---

### Year View (Calendar #3)

```
┌────────────────────────────────────────────────────┐
│                       2025                          │
├───────────┬───────────┬───────────┬────────────────┤
│  January  │ February  │   March   │     April      │
│           │           │           │                │
│  1 2 3 4  │  1 2 3 4  │  1 2 3 4  │   1 2 3 4 5   │
│ 📘📗      │     📗    │  📘       │      📗        │
├───────────┼───────────┼───────────┼────────────────┤
│    May    │   June    │   July    │    August      │
│           │           │           │                │
│  1 2 3 4  │  1 2 3 4  │  1 2 3 4  │   1 2 3 4 5   │
│  📙       │  📘📗    │     📙    │   📘           │
├───────────┼───────────┼───────────┼────────────────┤
│ September │  October  │ November  │   December     │
│           │           │           │                │
│  1 2 3 4  │  1 2 3 4  │  1 2 3 4  │   1 2 3 4 5   │
│     📗    │  📘📙    │  📗       │      📘        │
└───────────┴───────────┴───────────┴────────────────┘
```

---

## Accessibility Features

### Keyboard Navigation

```
┌─────────────────────────────────────────┐
│  Keyboard Shortcuts                     │
├─────────────────────────────────────────┤
│                                         │
│  Tab        → Next interactive element  │
│  Shift+Tab  → Previous element          │
│  Enter      → Activate button/link      │
│  Space      → Toggle checkbox           │
│  Esc        → Close detail panel        │
│  Arrow Keys → Navigate mini calendar    │
│                                         │
│  Calendar Navigation:                   │
│  n → Next (week/month)                  │
│  p → Previous (week/month)              │
│  t → Today                              │
│  m → Month view                         │
│  w → Week view                          │
│  d → Day view                           │
│                                         │
└─────────────────────────────────────────┘
```

### Focus Indicators

```
Default state:
┌──────────────┐
│   Button     │
└──────────────┘

Focus state (keyboard):
┌──────────────┐
│   Button     │  ← Blue outline (2px)
└──────────────┘   Emerald inner ring
```

### Screen Reader Announcements

```
Event: Filter changed
Announcement: "Projects filter enabled. Showing 15 project events."

Event: View mode changed
Announcement: "Calendar view changed to Week view."

Event: Detail panel opened
Announcement: "Event details panel opened. Press Escape to close."

Event: Date selected
Announcement: "Date selected: October 15, 2025. 3 events on this day."
```

---

## ARIA Labels

```html
<!-- Navigation buttons -->
<button aria-label="Previous month">◀</button>
<button aria-label="Next month">▶</button>
<button aria-label="Go to today">Today</button>

<!-- View mode buttons -->
<button aria-label="Month view" data-view="dayGridMonth">Month</button>
<button aria-label="Week view" data-view="timeGridWeek">Week</button>
<button aria-label="Day view" data-view="timeGridDay">Day</button>
<button aria-label="Year view" data-view="multiMonthYear">Year</button>

<!-- Filter checkboxes -->
<label>
  <input type="checkbox" aria-label="Show project events">
  Show Projects
</label>

<!-- Close buttons -->
<button aria-label="Close detail panel">×</button>
<button aria-label="Close sidebar">×</button>
```

---

## Performance Indicators

### Loading States

```
Initial Load:
┌─────────────────────────┐
│                         │
│        ⏳               │
│    Loading...           │
│                         │
└─────────────────────────┘

Events Fetching:
┌─────────────────────────┐
│  [Month] [Week] [Day]   │
├─────────────────────────┤
│         ⏳              │
│   Fetching events...    │
│                         │
└─────────────────────────┘

Filtering (instant):
☑ Show Projects  ← No spinner, instant update
```

### Skeleton Screens (Optional Enhancement)

```
┌─────────────────────────────────────────┐
│  ▭▭▭▭  ▭▭▭▭  ▭▭▭▭  ▭▭▭▭               │
│                                         │
│  ┌────┬────┬────┬────┬────┬────┬────┐ │
│  │ ░░ │ ░░ │ ░░ │ ░░ │ ░░ │ ░░ │ ░░ │ │
│  ├────┼────┼────┼────┼────┼────┼────┤ │
│  │ ░░ │ ░░ │ ░░ │ ░░ │ ░░ │ ░░ │ ░░ │ │
│  │ ░░ │    │ ░░ │    │    │ ░░ │    │ │
│  └────┴────┴────┴────┴────┴────┴────┘ │
│                                         │
└─────────────────────────────────────────┘

Legend: ▭ Skeleton text  ░ Skeleton event
```

---

## Conclusion

The **Advanced Modern Calendar (Calendar #3)** provides a rich, modern interface with:

- ✅ **Three-panel layout** for comprehensive workflow
- ✅ **Client-side filtering** for instant updates
- ✅ **Mini calendar** for quick navigation
- ✅ **Slide-in detail panel** for focused event review
- ✅ **Responsive design** across all devices
- ✅ **Full accessibility** (WCAG 2.1 AA)

Access at: `/oobc-management/calendar/advanced-modern/`

---

**Last Updated:** October 6, 2025
**Maintained By:** OBCMS Development Team
