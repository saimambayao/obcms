# Calendar Sidebar Quick Reference

**Component:** Advanced Modern Calendar Sidebar
**File:** `src/templates/common/calendar_advanced_modern.html`
**Last Updated:** 2025-10-06

---

## Quick Implementation Guide

### HTML Structure

```html
<!-- Event Type Filter Item -->
<label class="event-legend-item" for="filterProjects">
    <i class="fas fa-folder event-type-icon" style="color: #3b82f6;"></i>
    <span class="text-sm text-gray-700 flex-1">Projects</span>
    <input type="checkbox" id="filterProjects" class="event-legend-checkbox" checked data-work-type="project">
</label>

<!-- Toggle Button -->
<button class="sidebar-toggle-btn" id="toggleSidebarBtn" aria-label="Toggle sidebar">
    <i class="fas fa-bars text-gray-600" id="sidebarToggleIcon"></i>
</button>
```

---

## CSS Classes Reference

### Event Type Items

| Class                  | Purpose                        | Key Properties                     |
|------------------------|--------------------------------|------------------------------------|
| `.event-legend-item`   | Filter row container           | `display: flex`, `cursor: pointer` |
| `.event-legend-item.active` | Active filter state      | `background: rgba(255,255,255,0.8)` |
| `.event-type-icon`     | Event type icon                | `width: 1.25rem`, `font-size: 0.75rem` |
| `.event-legend-checkbox` | Custom checkbox             | `appearance: none`, `position: relative` |

### Sidebar Toggle

| Class                  | Purpose                        | Key Properties                     |
|------------------------|--------------------------------|------------------------------------|
| `.sidebar-toggle-btn`  | Toggle button                  | `width: 2.5rem`, `border-radius: 0.5rem` |
| `.calendar-sidebar`    | Sidebar container              | `transition: transform 300ms`      |
| `.sidebar-collapsed`   | Desktop collapsed state        | `grid-template-columns: 0px 1fr 0px` |

---

## Event Type Icons & Colors

| Event Type    | Icon                      | Color Code | Font Awesome Class      |
|---------------|---------------------------|------------|-------------------------|
| Projects      | 📁                        | `#3b82f6`  | `fas fa-folder`         |
| Activities    | ✓                         | `#10b981`  | `fas fa-calendar-check` |
| Tasks         | ☑                         | `#8b5cf6`  | `fas fa-tasks`          |
| Coordination  | 🤝                        | `#14b8a6`  | `fas fa-handshake`      |

---

## JavaScript API

### State Variables

```javascript
let sidebarCollapsed = false; // Desktop sidebar state

let activeFilters = {
    project: true,
    activity: true,
    task: true,
    coordination: true,
    completed: false
};
```

### Key Functions

```javascript
// Toggle sidebar (responsive)
function toggleSidebar() {
    const isMobile = window.innerWidth < 1024;
    // ... implementation
}

// Apply filters to events
function applyFilters(events) {
    return events.filter(event => {
        const workType = event.extendedProps?.work_type;
        const isCompleted = event.extendedProps?.is_completed;

        if (workType && !activeFilters[workType]) return false;
        if (isCompleted && !activeFilters.completed) return false;

        return true;
    });
}
```

### Event Listeners

```javascript
// Filter checkbox change
document.querySelectorAll('.event-legend-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const workType = this.dataset.workType;
        activeFilters[workType] = this.checked;

        // Update active state
        const label = this.closest('.event-legend-item');
        label.classList.toggle('active', this.checked);

        // Refresh calendar
        calendar.refetchEvents();
    });
});

// Sidebar toggle
document.getElementById('toggleSidebarBtn').addEventListener('click', toggleSidebar);
```

---

## Responsive Breakpoints

### Desktop (≥1024px)

**Default:** Sidebar visible
**Toggle:** Collapses sidebar (grid layout change)
**Animation:** `transform: translateX(-100%)`

```css
@media (min-width: 1024px) {
    .calendar-container.sidebar-collapsed {
        grid-template-columns: 0px 1fr 0px;
    }

    .calendar-container.sidebar-collapsed .calendar-sidebar {
        transform: translateX(-100%);
    }
}
```

### Mobile (<1024px)

**Default:** Sidebar hidden
**Toggle:** Overlays sidebar
**Animation:** Fixed position + backdrop

```css
@media (max-width: 1024px) {
    .calendar-sidebar {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        width: 280px;
        transform: translateX(-100%);
        z-index: 30;
    }

    .calendar-sidebar.open {
        transform: translateX(0);
    }
}
```

---

## Animation Timings

| Interaction    | Duration | Easing      | Property    |
|----------------|----------|-------------|-------------|
| Sidebar toggle | 300ms    | ease-in-out | `transform` |
| Item hover     | 200ms    | default     | `background`, `transform` |
| Icon scale     | 200ms    | default     | `transform` |
| Checkbox       | 200ms    | default     | `background`, `border` |

---

## Common Customizations

### Adding a New Event Type

**Step 1:** Add HTML
```html
<label class="event-legend-item" for="filterNewType">
    <i class="fas fa-star event-type-icon" style="color: #f59e0b;"></i>
    <span class="text-sm text-gray-700 flex-1">New Type</span>
    <input type="checkbox" id="filterNewType" class="event-legend-checkbox" checked data-work-type="newtype">
</label>
```

**Step 2:** Update JavaScript state
```javascript
let activeFilters = {
    project: true,
    activity: true,
    task: true,
    coordination: true,
    newtype: true, // Add new type
    completed: false
};
```

**Step 3:** Add color mapping
```javascript
const workTypeColors = {
    'project': '#3b82f6',
    'activity': '#10b981',
    'task': '#8b5cf6',
    'coordination': '#14b8a6',
    'newtype': '#f59e0b' // Add new color
};
```

---

### Changing Sidebar Width

**Desktop:**
```css
.calendar-container {
    grid-template-columns: 320px 1fr 0px; /* Change from 280px */
}

.calendar-sidebar {
    /* No change needed - inherits from grid */
}
```

**Mobile:**
```css
@media (max-width: 1024px) {
    .calendar-sidebar {
        width: 320px; /* Change from 280px */
    }
}
```

---

### Customizing Animation Speed

**All Animations:**
```css
.calendar-sidebar {
    transition: transform 500ms ease-in-out; /* Change from 300ms */
}

.event-legend-item {
    transition: all 300ms; /* Change from 200ms */
}
```

---

## Troubleshooting

### Problem: Sidebar doesn't toggle on desktop

**Check:**
1. Is `toggleSidebarBtn` present in DOM?
2. Is event listener attached?
3. Does `calendarContainer` have correct ID?

**Solution:**
```javascript
// Verify elements exist
const toggleBtn = document.getElementById('toggleSidebarBtn');
const calendarContainer = document.getElementById('calendarContainer');

if (!toggleBtn || !calendarContainer) {
    console.error('Missing required elements');
}
```

---

### Problem: Filters don't update calendar

**Check:**
1. Are checkboxes using correct `data-work-type` attributes?
2. Is `calendar.refetchEvents()` being called?
3. Is `applyFilters()` function working?

**Solution:**
```javascript
// Debug filter state
console.log('Active filters:', activeFilters);

// Verify checkbox data attributes
document.querySelectorAll('.event-legend-checkbox').forEach(checkbox => {
    console.log('Checkbox:', checkbox.id, 'Work type:', checkbox.dataset.workType);
});
```

---

### Problem: Icon doesn't change on toggle

**Check:**
1. Is `sidebarToggleIcon` ID present?
2. Is icon class being updated correctly?

**Solution:**
```javascript
const toggleIcon = document.getElementById('sidebarToggleIcon');

if (!toggleIcon) {
    console.error('Toggle icon element not found');
} else {
    console.log('Current icon class:', toggleIcon.className);
}
```

---

### Problem: Sidebar animation is jerky

**Check:**
1. Are there layout-triggering CSS properties in transition?
2. Is browser hardware acceleration enabled?

**Solution:**
```css
/* Use transform (GPU-accelerated) instead of left/right */
.calendar-sidebar {
    transition: transform 300ms ease-in-out;
    will-change: transform; /* Hint for browser optimization */
}

/* Avoid transitioning width, margin, padding */
```

---

## Performance Tips

### Optimize Event Listeners

**Bad:**
```javascript
// Attaching individual listeners
document.getElementById('filterProjects').addEventListener('change', ...);
document.getElementById('filterActivities').addEventListener('change', ...);
document.getElementById('filterTasks').addEventListener('change', ...);
```

**Good:**
```javascript
// Use delegation or loop
document.querySelectorAll('.event-legend-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', handleFilterChange);
});
```

---

### Minimize Calendar Refreshes

**Bad:**
```javascript
// Refresh on every filter change
activeFilters.project = false;
calendar.refetchEvents(); // Refresh 1
activeFilters.activity = false;
calendar.refetchEvents(); // Refresh 2
```

**Good:**
```javascript
// Batch updates
activeFilters.project = false;
activeFilters.activity = false;
calendar.refetchEvents(); // Single refresh
```

---

### Use CSS Transitions (Not JavaScript)

**Bad:**
```javascript
// JavaScript animation
sidebar.style.left = '-280px';
setTimeout(() => {
    sidebar.style.left = '0px';
}, 300);
```

**Good:**
```css
/* CSS transition */
.calendar-sidebar {
    transition: transform 300ms ease-in-out;
}
```

```javascript
// JavaScript just toggles class
sidebar.classList.toggle('open');
```

---

## Accessibility Checklist

- [ ] All interactive elements have ARIA labels
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Focus indicators visible on all elements
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Touch targets ≥44×44px
- [ ] Screen reader announces filter state changes
- [ ] Icons have `aria-hidden="true"` (decorative)
- [ ] Semantic HTML (labels, checkboxes, buttons)

---

## Browser Compatibility

| Browser         | Version | Supported | Notes                          |
|-----------------|---------|-----------|--------------------------------|
| Chrome/Edge     | 90+     | ✅        | Full support                   |
| Firefox         | 88+     | ✅        | Full support                   |
| Safari          | 14+     | ✅        | Full support                   |
| iOS Safari      | 14+     | ✅        | Touch targets optimized        |
| Android Chrome  | 90+     | ✅        | Full support                   |

**Required Features:**
- CSS Grid Layout
- CSS Custom Properties
- `appearance: none` (checkbox styling)
- Font Awesome 5+ (icon fonts)
- `transform` animations

---

## Testing Commands

### Manual Testing

```bash
# Desktop (≥1024px)
1. Open calendar in browser
2. Click toggle button (☰)
3. Verify sidebar collapses with animation
4. Click toggle again (×)
5. Verify sidebar expands

# Mobile (<1024px)
1. Resize browser to mobile width
2. Click toggle button (☰)
3. Verify sidebar overlays content
4. Click backdrop or close button
5. Verify sidebar closes

# Filters
1. Click any event type filter row
2. Verify checkbox toggles
3. Verify calendar refreshes
4. Verify events are hidden/shown correctly
```

### Automated Testing (Future)

```javascript
// Jest/Vitest test example
describe('Sidebar Toggle', () => {
    it('should collapse sidebar on desktop', () => {
        const toggleBtn = document.getElementById('toggleSidebarBtn');
        const container = document.getElementById('calendarContainer');

        toggleBtn.click();

        expect(container.classList.contains('sidebar-collapsed')).toBe(true);
    });

    it('should update filter state on checkbox change', () => {
        const checkbox = document.getElementById('filterProjects');

        checkbox.checked = false;
        checkbox.dispatchEvent(new Event('change'));

        expect(activeFilters.project).toBe(false);
    });
});
```

---

## Related Documentation

- **Full Enhancement Guide:** `CALENDAR_SIDEBAR_ENHANCEMENTS.md`
- **Visual Comparison:** `CALENDAR_SIDEBAR_VISUAL_COMPARISON.md`
- **UI Components Standard:** `docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`
- **Calendar Implementation:** `docs/ui/MODERN_CALENDAR_IMPLEMENTATION.md`

---

## Version History

| Version | Date       | Changes                                      |
|---------|------------|----------------------------------------------|
| 1.0     | 2025-10-06 | Initial implementation with icons, integrated filters, toggle |

---

## Support

For issues or questions:
1. Check this quick reference first
2. Review full enhancement documentation
3. Inspect browser console for errors
4. Verify element IDs and classes match exactly
5. Test in different browsers and viewport sizes

**Common Gotchas:**
- Font Awesome must be loaded for icons to appear
- Toggle icon ID must be `sidebarToggleIcon` (exact match)
- Checkbox `data-work-type` must match filter keys exactly
- Grid layout requires parent container with correct ID
