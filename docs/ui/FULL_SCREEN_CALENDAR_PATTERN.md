# Full-Screen Calendar Layout Pattern

**Pattern:** Full-height calendar that fills viewport from navbar to footer
**Use Case:** Calendar views, timeline views, gantt charts, scheduler interfaces
**Template Reference:** `src/templates/common/calendar_advanced_modern.html`

---

## Quick Reference

### Height Calculation Formula

```css
.calendar-container {
    height: calc(100vh - [navbar-height] - [breadcrumb-height]);
}
```

**Standard OBCMS Values:**
- Navbar: `64px` (h-16)
- Breadcrumb: `42px` (measured)
- **Total offset: 106px**

---

## Implementation Pattern

### 1. Container Setup

```css
.calendar-container {
    /* Fill viewport minus fixed headers */
    height: calc(100vh - 106px);

    /* Use grid or flex for layout */
    display: grid;
    grid-template-columns: [sidebar-width] 1fr [detail-width];
    grid-template-rows: auto 1fr;

    /* Prevent overflow */
    overflow: hidden;
}
```

### 2. Main Content Area

```css
.calendar-main {
    /* Position in grid */
    grid-column: 2 / 3;
    grid-row: 2 / 3;

    /* Use flex to fill height */
    display: flex;
    flex-direction: column;

    /* Allow scrolling if needed */
    overflow: auto;

    /* Critical for grid child sizing */
    min-height: 0;
}
```

### 3. Calendar Element

```css
#calendar {
    /* Fill parent */
    flex: 1;
    width: 100%;

    /* Critical for flex child sizing */
    min-height: 0;
}
```

### 4. FullCalendar Configuration

```javascript
calendar = new FullCalendar.Calendar(calendarEl, {
    height: '100%', // Fill parent, NOT fixed pixel value
    // ... other config
});
```

---

## Common Pitfalls

### ❌ DON'T: Use Fixed Heights

```css
/* BAD: Fixed height prevents responsive fill */
#calendar {
    height: 650px;
}

/* BAD: Generic viewport calculation */
.calendar-container {
    height: calc(100vh - 4rem); /* What is 4rem? Unclear! */
}
```

### ✅ DO: Use Flexible Heights

```css
/* GOOD: Explicit calculation with comments */
.calendar-container {
    /* Navbar (64px) + Breadcrumb (42px) = 106px */
    height: calc(100vh - 106px);
}

/* GOOD: Flex fill */
#calendar {
    flex: 1;
    min-height: 0;
}
```

---

## Height Hierarchy

```
body (min-h-screen, flex, flex-col)
├── navbar (64px fixed)
├── breadcrumb (42px fixed)
├── main (flex-1, grows to fill)
│   └── calendar-container (calc(100vh - 106px))
│       ├── header (auto height)
│       └── calendar-main (flex-1)
│           └── #calendar (flex: 1, height: 100%)
└── footer (auto height, below viewport)
```

---

## Responsive Considerations

### Desktop (≥1024px)

```css
.calendar-container {
    height: calc(100vh - 106px);
    grid-template-columns: 280px 1fr 0px;
}
```

### Tablet (768px - 1023px)

```css
.calendar-container {
    height: calc(100vh - 106px);
    grid-template-columns: 0px 1fr 0px; /* Sidebar hidden */
}

.calendar-sidebar {
    position: fixed; /* Overlay mode */
}
```

### Mobile (≤767px)

```css
.calendar-container {
    /* Account for mobile header differences */
    height: calc(100vh - 106px);
    grid-template-columns: 0px 1fr 0px;
}
```

---

## Flexbox Alternative Pattern

If you prefer flexbox over grid:

```css
.calendar-container {
    height: calc(100vh - 106px);
    display: flex;
    flex-direction: row;
}

.calendar-sidebar {
    width: 280px;
    flex-shrink: 0;
}

.calendar-main {
    flex: 1;
    display: flex;
    flex-direction: column;
}

#calendar {
    flex: 1;
    min-height: 0;
}
```

---

## Adding Breadcrumbs

Always add breadcrumb block for navigation context:

```django
{% block breadcrumb %}
<li class="flex items-center">
    <a href="{% url 'common:dashboard' %}" class="text-gray-500 hover:text-gray-700">
        <i class="fas fa-home"></i>
    </a>
</li>
<li class="flex items-center">
    <i class="fas fa-chevron-right text-gray-400 mx-2 text-xs"></i>
    <a href="{% url 'parent_view' %}" class="text-gray-500 hover:text-gray-700">Parent</a>
</li>
<li class="flex items-center">
    <i class="fas fa-chevron-right text-gray-400 mx-2 text-xs"></i>
    <span class="text-gray-900 font-medium">Current Page</span>
</li>
{% endblock %}
```

---

## Footer Considerations

### Footer Below Viewport (Recommended)

```css
/* Calendar fills viewport, footer appears below */
.calendar-container {
    height: calc(100vh - 106px);
}
```

**Pros:**
- Calendar has maximum space
- Footer accessible via scroll
- Clean, modern full-screen feel

**Cons:**
- Footer not immediately visible
- User must scroll to see footer

### Footer Always Visible (Alternative)

```css
/* Calendar shrinks to keep footer visible */
.calendar-container {
    height: calc(100vh - 106px - [footer-height]);
}
```

**Pros:**
- Footer always visible
- No scrolling needed

**Cons:**
- Calendar has less space
- Requires knowing footer height
- Footer height varies by content

---

## Testing Checklist

When implementing this pattern, verify:

- [ ] Calendar fills viewport from breadcrumb to bottom
- [ ] No fixed pixel heights (except navbar/breadcrumb)
- [ ] Breadcrumb navigation appears correctly
- [ ] Footer is visible (scroll down if needed)
- [ ] Responsive on mobile/tablet/desktop
- [ ] No vertical scrollbar on calendar itself
- [ ] Window resize updates calendar height
- [ ] Browser DevTools shows correct computed heights

---

## Browser Compatibility

**Tested:**
- Chrome 120+ ✅
- Firefox 120+ ✅
- Safari 17+ ✅
- Edge 120+ ✅

**CSS Features Used:**
- `calc()` - Supported all browsers
- `flexbox` - Supported all browsers
- `grid` - Supported all browsers
- `min-height: 0` - Critical for flex/grid children

---

## Performance Notes

- **Flexbox/Grid:** Hardware-accelerated, excellent performance
- **calc():** Computed once on load/resize, minimal overhead
- **100% height:** More efficient than fixed pixels (no reflow on resize)

---

## Accessibility

- **Breadcrumb:** Improves navigation context for screen readers
- **Landmark regions:** Use `<main>`, `<aside>`, `<header>` semantic HTML
- **Focus management:** Ensure focus visible after calendar interactions
- **Keyboard navigation:** All calendar controls keyboard-accessible

---

## Examples in OBCMS

### Advanced Modern Calendar (Full Implementation)

**File:** `src/templates/common/calendar_advanced_modern.html`

**Features:**
- Grid layout with sidebar + calendar + detail panel
- Full-height fill
- Responsive sidebar toggle
- FullCalendar integration

### Classic Calendar (Simpler Version)

**File:** `src/templates/common/oobc_calendar.html`

**Features:**
- Simple full-width calendar
- No sidebar
- Full-height fill

### Project Calendar

**File:** `src/templates/project_central/project_calendar.html`

**Features:**
- Project-specific events
- Full-height fill
- Filtered by project context

---

## Related Patterns

1. **[Kanban Board Layout](./KANBAN_LAYOUT_PATTERN.md)** - Similar full-height pattern
2. **[Timeline View](./TIMELINE_VIEW_PATTERN.md)** - Horizontal timeline full-height
3. **[Data Table with Filters](./DATA_TABLE_PATTERN.md)** - Sidebar + table layout

---

## Migration Guide

### From Fixed Height Calendar

**Before:**
```css
#calendar {
    height: 650px;
}
```

**After:**
```css
.calendar-container {
    height: calc(100vh - 106px);
}

.calendar-main {
    display: flex;
    flex-direction: column;
}

#calendar {
    flex: 1;
    min-height: 0;
}
```

**JavaScript:**
```javascript
// Before
height: '650px',

// After
height: '100%',
```

---

## Troubleshooting

### Problem: Calendar has no height (0px)

**Cause:** Parent container has no defined height

**Solution:** Ensure all parent elements have height defined:
```css
.calendar-container { height: calc(100vh - 106px); }
.calendar-main { display: flex; flex-direction: column; }
#calendar { flex: 1; }
```

---

### Problem: Calendar overflows parent

**Cause:** Missing `min-height: 0` on flex/grid children

**Solution:**
```css
.calendar-main {
    min-height: 0; /* Critical! */
}

#calendar {
    min-height: 0; /* Critical! */
}
```

---

### Problem: FullCalendar not rendering

**Cause:** Calendar initialized before element has dimensions

**Solution:**
```javascript
// Wait for paint to complete
requestAnimationFrame(() => {
    initCalendar();
});

// Or check dimensions first
if (calendarEl.offsetHeight === 0) {
    setTimeout(initCalendar, 100);
    return;
}
```

---

### Problem: Footer hidden/inaccessible

**Cause:** Incorrect height calculation

**Solution:**
```css
/* Correct: Footer below viewport (scroll to see) */
.calendar-container {
    height: calc(100vh - 106px);
}

/* OR: Footer always visible */
.calendar-container {
    height: calc(100vh - 106px - 200px); /* 200px = footer height */
}
```

---

## Code Snippet Library

### Basic Full-Height Calendar

```html
<div class="calendar-container" style="height: calc(100vh - 106px);">
    <div class="calendar-main" style="display: flex; flex-direction: column;">
        <div id="calendar" style="flex: 1; min-height: 0;"></div>
    </div>
</div>

<script>
const calendar = new FullCalendar.Calendar(calendarEl, {
    height: '100%',
    // ... config
});
</script>
```

### With Sidebar

```html
<div class="calendar-container" style="height: calc(100vh - 106px); display: grid; grid-template-columns: 280px 1fr;">
    <aside class="calendar-sidebar">
        <!-- Sidebar content -->
    </aside>
    <main class="calendar-main" style="display: flex; flex-direction: column;">
        <div id="calendar" style="flex: 1; min-height: 0;"></div>
    </main>
</div>
```

---

## Further Reading

- [MDN: Flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout)
- [MDN: Grid](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [FullCalendar Height Docs](https://fullcalendar.io/docs/height)
- [OBCMS UI Standards](./OBCMS_UI_COMPONENTS_STANDARDS.md)

---

**Last Updated:** 2025-01-06
**Pattern Version:** 1.0
**Status:** Production-Ready
