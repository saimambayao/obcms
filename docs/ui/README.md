# UI Documentation

Comprehensive documentation for the OBCMS user interface, including reusable components, patterns, and best practices.

---

## 🎯 Official UI Standards

**PRIMARY REFERENCE:** [OBCMS UI Standards Master Guide](OBCMS_UI_STANDARDS_MASTER.md) ⭐ **OFFICIAL**

**Version:** 3.1 | **Status:** ✅ Official Standard | **Last Updated:** 2025-10-12

This master guide consolidates 69+ UI documentation files into a single source of truth for all OBCMS UI/UX development.

**Key Features:**
- ✅ Complete component library with copy-paste examples
- ✅ Blue-to-Teal gradient color system (#1e40af to #059669)
- ✅ HTMX patterns for instant UI updates
- ✅ WCAG 2.1 AA accessibility compliance
- ✅ Mobile-first responsive design patterns
- ✅ Comprehensive documentation index (69+ docs)

**⚡ For AI Agents:** This is your PRIMARY reference - read BEFORE creating any UI component!

**📋 [Color System Correction Summary](COLOR_SYSTEM_CORRECTION_SUMMARY.md)** - **Updated Oct 2025**
- Documents the correction of primary colors from Ocean Blue to confirmed Blue-800
- Verified from navbar screenshot, updated to official Bangsamoro brand colors

**🔧 [Provincial Table Alignment Issues](../improvements/UI/ALIGNMENT_ISSUE_SUMMARY.md)** - **Oct 12, 2025**
- Analysis of vertical alignment issues in provincial OBC table
- Root cause: conflicting flexbox implementations between backend and template
- Solution: Align with working municipal table pattern (separate icon column)
- [Full Technical Analysis](../improvements/UI/PROVINCIAL_TABLE_VERTICAL_ALIGNMENT_ANALYSIS.md) | [Visual Guide](../improvements/UI/PROVINCIAL_TABLE_ALIGNMENT_VISUAL_GUIDE.md)

---

## Overview

The OBCMS UI is built with:
- **Django Templates** for server-side rendering
- **HTMX** for dynamic interactions without full page reloads
- **Alpine.js** for lightweight client-side interactivity
- **Tailwind CSS** for responsive, utility-first styling
- **FullCalendar** for calendar views
- **Leaflet** for interactive maps

## Documentation Structure

### [Component Library Guide](component_library_guide.md)
Complete reference for all reusable UI components.

**Contents**:
- Kanban Board Component
- Calendar Widget Component
- Modal Dialog Component
- Task Card Component
- Data Table Card Component
- Form Field Components

**When to use**: Implementing new features, understanding component APIs, troubleshooting component issues.

---

### [HTMX Patterns](htmx_patterns.md)
Common HTMX interaction patterns with code examples.

**Contents**:
- Inline Editing
- Modal Dialogs
- Infinite Scroll
- Live Counters (Polling)
- Dependent Dropdowns
- Real-time Form Validation
- Out-of-Band Swaps
- Delete Confirmation
- Optimistic Updates
- File Upload Progress

**When to use**: Implementing dynamic interactions, loading content without page reloads, real-time updates.

---

### [Accessibility Patterns](accessibility_patterns.md)
WCAG 2.1 AA compliance patterns and best practices.

**Contents**:
- Semantic HTML Structure
- Keyboard Navigation
- Focus Management
- ARIA Labels and Roles
- Color Contrast
- Screen Reader Support
- Form Accessibility
- Dynamic Content Announcements
- Touch Target Sizes
- Skip Navigation Links

**When to use**: Ensuring accessibility compliance, implementing keyboard navigation, supporting screen readers.

---

### [Mobile Responsiveness](mobile_patterns.md)
Mobile-first responsive design patterns.

**Contents**:
- Responsive Breakpoints
- Mobile-First Approach
- Responsive Grid Layouts
- Mobile Navigation Patterns
- Responsive Tables
- Touch-Friendly Interactions
- Modal Dialogs on Mobile
- Form Layouts
- Typography Scaling
- Testing Across Devices

**When to use**: Implementing responsive layouts, optimizing for mobile devices, testing across screen sizes.

---

## Quick Start

### 1. Using Components

Include components in your Django templates:

```django
{% extends "base.html" %}

{% block content %}
<!-- Use Kanban Board -->
{% include "components/kanban_board.html" with
    board_id="my-kanban"
    columns=columns
    item_template="components/task_card.html"
    move_endpoint="/api/tasks/move/"
%}

<!-- Use Modal -->
{% include "components/modal.html" with
    modal_id="detail-modal"
    title="Task Details"
    content_template="tasks/task_detail_content.html"
    size="lg"
%}
{% endblock %}
```

### 2. HTMX Integration

Add HTMX attributes for dynamic behavior:

```html
<!-- Load content on click -->
<button hx-get="/tasks/1/modal/"
        hx-target="#modal-container"
        hx-swap="innerHTML">
    View Details
</button>

<!-- Submit form without page reload -->
<form hx-post="/tasks/create/"
      hx-target="#task-list"
      hx-swap="afterbegin">
    <!-- Form fields -->
</form>
```

### 3. Mobile-Responsive Layout

Use Tailwind responsive classes:

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Responsive grid: 1 column mobile, 2 tablet, 3 desktop -->
</div>

<div class="hidden md:block">
    <!-- Desktop-only content -->
</div>

<div class="block md:hidden">
    <!-- Mobile-only content -->
</div>
```

---

## Component Library

### Available Components

| Component | File | Purpose |
|-----------|------|---------|
| Kanban Board | `components/kanban_board.html` | Drag-and-drop task boards |
| Calendar (Full) | `components/calendar_full.html` | FullCalendar integration |
| Calendar (Simple) | `components/calendar_widget.html` | Basic calendar wrapper |
| Modal Dialog | `components/modal.html` | Accessible modal popups |
| Task Card | `components/task_card.html` | Consistent task display |
| Data Table Card | `components/data_table_card.html` | Styled data tables |
| Form Field (Input) | `components/form_field_input.html` | Text input fields |
| Form Field (Select) | `components/form_field_select.html` | Dropdown selects |
| Form Field (Generic) | `components/form_field.html` | Any form field type |

### Component Dependencies

**Required in base template**:

```html
<!-- HTMX for dynamic interactions -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>

<!-- Alpine.js for modals and interactive UI -->
<script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>

<!-- Tailwind CSS for styling -->
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.1/dist/tailwind.min.css" rel="stylesheet">

<!-- FullCalendar (if using calendar components) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.css">
<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.js"></script>

<!-- Font Awesome for icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
```

---

## Design Principles

### 1. Progressive Enhancement
Build core functionality that works without JavaScript, then enhance with HTMX/Alpine.js.

### 2. Mobile-First
Design for mobile screens first, then add enhancements for larger screens.

### 3. Accessibility-First
All components meet WCAG 2.1 AA standards out of the box.

### 4. Consistency
Reuse components instead of duplicating code. Maintain visual and interaction consistency.

### 5. Performance
Minimize JavaScript, lazy-load heavy components, optimize for fast interactions.

---

## Common Patterns

### Pattern: Load Modal on Click

```html
<button hx-get="{% url 'task_detail_modal' task.id %}"
        hx-target="#modal-container"
        hx-swap="innerHTML">
    View Task
</button>

<!-- Modal container in base template -->
<div id="modal-container"></div>
```

### Pattern: Infinite Scroll List

```html
<div id="task-list">
    {% for task in tasks %}
    <div class="task-item">{{ task.title }}</div>
    {% endfor %}
</div>

{% if has_next %}
<div hx-get="?page={{ next_page }}"
     hx-trigger="revealed"
     hx-swap="afterend"
     hx-target="#task-list">
    Loading more...
</div>
{% endif %}
```

### Pattern: Dependent Dropdowns

```html
<select id="region"
        hx-get="/api/provinces/"
        hx-trigger="change"
        hx-target="#province-select"
        hx-include="#region">
    <option value="">Select Region</option>
</select>

<select id="province-select">
    <option value="">Select Province</option>
</select>
```

### Pattern: Real-time Validation

```html
<input type="email"
       name="email"
       hx-post="/api/validate-email/"
       hx-trigger="blur changed"
       hx-target="#email-error"
       hx-swap="innerHTML">
<div id="email-error"></div>
```

---

## Accessibility Checklist

Use this checklist for every new UI component:

- [ ] All images have descriptive `alt` text
- [ ] All form inputs have associated labels
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus indicators are visible
- [ ] Color contrast meets 4.5:1 ratio (WCAG AA)
- [ ] ARIA labels on icon-only buttons
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Skip navigation link present
- [ ] Dynamic updates announced to screen readers
- [ ] Touch targets are at least 44x44 pixels
- [ ] Form errors are clearly communicated
- [ ] Modals trap focus and restore on close

---

## Testing Guidelines

### Browser Testing

Test in these browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

### Responsive Testing

Test at these breakpoints:
- 320px (small mobile)
- 375px (iPhone SE)
- 768px (tablet)
- 1024px (small desktop)
- 1280px (desktop)
- 1920px (large desktop)

### Accessibility Testing

Tools:
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE Browser Extension](https://wave.webaim.org/extension/)
- Chrome Lighthouse
- Screen readers (VoiceOver, NVDA, JAWS)

### Performance Testing

Check:
- First Contentful Paint < 1.8s
- Time to Interactive < 3.8s
- Cumulative Layout Shift < 0.1
- No JavaScript errors in console
- HTMX requests complete quickly

---

## Troubleshooting

### HTMX Not Working

**Symptoms**: Clicks do nothing, content doesn't load

**Solutions**:
1. Check HTMX library is loaded: `<script src="https://unpkg.com/htmx.org@1.9.10"></script>`
2. Open browser console and look for JavaScript errors
3. Verify target element exists (e.g., `#modal-container`)
4. Check Django view returns correct HTTP response
5. Inspect Network tab to see if request is being sent

### Alpine.js Not Initializing

**Symptoms**: Dropdowns don't work, modals don't open

**Solutions**:
1. Check Alpine.js library is loaded with `defer` attribute
2. Verify `x-data` directive is on parent element
3. Check browser console for Alpine errors
4. Ensure Alpine syntax is correct (`:class`, `@click`, etc.)

### Component Not Rendering

**Symptoms**: Component appears blank or shows template code

**Solutions**:
1. Verify component file path is correct
2. Check all required parameters are passed
3. Look for Django template syntax errors
4. Verify context data is available in view
5. Check for typos in parameter names

### Mobile Layout Broken

**Symptoms**: Content overflows, buttons too small

**Solutions**:
1. Check viewport meta tag is present
2. Use responsive Tailwind classes (`md:`, `lg:`)
3. Test at actual mobile breakpoints (375px, 768px)
4. Ensure touch targets are 44x44px minimum
5. Remove fixed pixel widths

---

## Best Practices

### DO:
✅ Use reusable components from `components/`
✅ Follow mobile-first responsive design
✅ Implement keyboard navigation
✅ Provide ARIA labels for screen readers
✅ Test on real mobile devices
✅ Keep JavaScript minimal
✅ Use semantic HTML elements
✅ Implement loading states
✅ Handle errors gracefully
✅ Document custom components

### DON'T:
❌ Duplicate component code
❌ Rely solely on hover states
❌ Use tiny touch targets (< 44px)
❌ Skip accessibility testing
❌ Ignore mobile breakpoints
❌ Remove focus indicators
❌ Use non-semantic divs everywhere
❌ Forget loading spinners
❌ Show cryptic error messages
❌ Leave code undocumented

---

## Contributing to UI

When adding new UI components or patterns:

1. **Follow existing conventions**: Match styling and structure of existing components
2. **Document thoroughly**: Add usage examples and parameter descriptions
3. **Test accessibility**: Verify WCAG 2.1 AA compliance
4. **Test responsiveness**: Check all breakpoints (mobile, tablet, desktop)
5. **Update this documentation**: Add your component to the appropriate guide
6. **Provide examples**: Include Django view and template examples

---

## Related Documentation

- [Component Library Guide](component_library_guide.md) - Detailed component API reference
- [HTMX Patterns](htmx_patterns.md) - Common interaction patterns
- [Accessibility Patterns](accessibility_patterns.md) - WCAG compliance guide
- [Mobile Patterns](mobile_patterns.md) - Responsive design guide
- [CLAUDE.md](/CLAUDE.md) - Project coding standards
- [Development Guide](../development/README.md) - Development setup

---

## Questions?

For questions about UI implementation:
1. Check the relevant pattern documentation above
2. Review existing implementations in `src/templates/`
3. Consult CLAUDE.md for project conventions
4. Test with browser DevTools and accessibility audits

---

**Last Updated**: 2025-10-02
**Maintained By**: OBCMS Development Team
