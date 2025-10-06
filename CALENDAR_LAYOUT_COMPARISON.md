# Calendar Layout Architecture Comparison

**Advanced Modern vs. OOBC Calendar**

---

## Overview

This document compares the two calendar implementations in OBCMS, showing how the **same technical foundation** produces **completely different UI designs**.

---

## Layout Diagrams

### Advanced Modern Calendar (3-Column Grid)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Navbar (64px)                                                        │
├─────────────────────────────────────────────────────────────────────┤
│ Breadcrumb (42px)                                                    │
├──────────────┬───────────────────────────────────┬──────────────────┤
│              │                                   │                  │
│  SIDEBAR     │  HEADER                           │                  │
│  (280px)     │  Title + View Tabs + Navigation   │                  │
│              ├───────────────────────────────────┤                  │
│  Mini Cal    │                                   │   DETAIL PANEL   │
│              │                                   │   (0→380px)      │
│  Filters     │         CALENDAR                  │                  │
│              │                                   │   Slides in      │
│  Options     │                                   │   on event       │
│              │                                   │   click          │
│              │                                   │                  │
│              │                                   │                  │
└──────────────┴───────────────────────────────────┴──────────────────┘
    ↓                       ↓                             ↓
 Collapsible          Full calendar               Overlay panel
 (0px on mobile)      (fills space)               (fixed position)
```

---

### OOBC Calendar (Horizontal Top Bar)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Navbar (64px)                                                        │
├─────────────────────────────────────────────────────────────────────┤
│ Breadcrumb (42px)                                                    │
├─────────────────────────────────────────────────────────────────────┤
│ HERO: OOBC Calendar | Create | Advanced                             │
├────────────┬───────────┬───────────┬──────────────┬─────────────────┤
│  Total     │ Upcoming  │ Progress  │  Completed   │                 │
│  [icon] 0  │ [icon] 0  │ [icon] 0  │  [icon] 0    │                 │
└────────────┴───────────┴───────────┴──────────────┴─────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ TOOLBAR: [Month|Week|Day] [◄ Today ►] [📁 Projects][📊 Activities] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                                                                      │
│                        CALENDAR                                      │
│                  (Full width, no sidebars)                           │
│                                                                      │
│                                                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                                              ┌───────┐
                                                              │  📅   │ Toggle
                                                              └───────┘
                                                         ┌──────────────┐
                                                         │  Mini Cal    │ Slides
                                                         │  [Jan 2025]  │ from
                                                         │  Su Mo Tu... │ right
                                                         └──────────────┘
```

---

## Technical Foundation (Shared)

Both implementations use **identical technical patterns**:

### CSS Grid Container

```css
/* Page container with viewport-based height */
height: calc(100vh - 106px); /* Navbar + Breadcrumb */
display: grid;
overflow: hidden;
```

### Flexbox Calendar Wrapper

```css
.calendar-wrapper {
    display: flex;
    flex-direction: column;
    min-height: 0; /* CRITICAL */
}
```

### Calendar Div

```css
#calendar {
    flex: 1;
    min-height: 0; /* CRITICAL */
    width: 100%;
}
```

### FullCalendar Config

```javascript
calendar = new FullCalendar.Calendar(calendarEl, {
    height: '100%', // CRITICAL: Fill parent
    // ...
});
```

**Why it works:**
- `min-height: 0` allows flex/grid children to shrink
- `height: '100%'` makes FullCalendar fill available space
- Grid/flexbox architecture provides proper constraints

---

## UI Differences

| Aspect | Advanced Modern | OOBC Calendar |
|--------|----------------|---------------|
| **Layout** | 3-column grid | Vertical stack |
| **Stats** | Sidebar (optional) | Horizontal bar (top) |
| **Filters** | Sidebar checkboxes | Toolbar pill chips |
| **Mini Calendar** | Left sidebar | Floating bottom-right |
| **Navigation** | Top header | Embedded toolbar |
| **Hero** | None | Compact banner |
| **Event Details** | Right slide-in panel | Page navigation |
| **Screen Space** | Sidebars reduce width | Full-width calendar |

---

## When to Use Each

### Advanced Modern ✅

- Desktop-first users
- Power users needing quick access
- Enterprise/corporate context
- High information density
- In-place event previews

### OOBC Calendar ✅

- Mobile-first audience
- Casual/occasional users
- Public-facing schedules
- Clean, simple aesthetic
- Single-task focus

---

## Conclusion

Same engine, different bodies:
- **Advanced Modern:** Sports car (performance)
- **OOBC Calendar:** Family sedan (comfort)

Both production-ready. Choose based on audience needs.
