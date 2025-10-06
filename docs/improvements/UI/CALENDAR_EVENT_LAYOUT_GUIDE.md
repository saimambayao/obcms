# Calendar Event Layout Guide

**Quick Reference for Developers**

---

## Event Layout Pattern

### Current Implementation: Google Calendar Style

```
[hierarchy-indicator] [icon] Title text... [status] [priority] [time] [expand-btn]
```

---

## Element Breakdown

### 1. Hierarchy Indicator (Optional)
```javascript
if (level > 0) {
    indicator.textContent = '└';
    indicator.className = 'text-gray-400 text-xs leading-none';
}
```
- Only shown for child items (level > 0)
- Single character: `└`
- Gray color, extra small text

### 2. Work Type Icon (Always)
```javascript
iconEl.innerHTML = getWorkItemIcon(workType).replace('mr-1', '');
iconEl.className = 'leading-none';
```
- Icons:
  - Project: `fa-project-diagram` (blue)
  - Sub-project: `fa-folder-tree` (cyan)
  - Activity: `fa-clipboard-list` (green)
  - Sub-activity: `fa-list-check` (light green)
  - Task: `fa-tasks` (purple)
  - Subtask: `fa-check-square` (light purple)
- Spacing removed (`replace('mr-1', '')`)

### 3. Title Text (Always)
```javascript
titleText.textContent = originalTitle;
titleText.className = 'flex-1 truncate font-medium leading-tight';
```
- `flex-1`: Expand to fill available space
- `truncate`: Ellipsis if too long
- `font-medium`: Medium weight
- `leading-tight`: Compact line height

### 4. Status Icon (Always)
```javascript
statusIconEl.innerHTML = getStatusIcon(status).replace('ml-1', '');
statusIconEl.className = 'leading-none flex-shrink-0';
```
- Icons:
  - Not started: `fa-circle` (gray, outline)
  - In progress: `fa-spinner` (blue)
  - At risk: `fa-exclamation-triangle` (amber)
  - Blocked: `fa-ban` (red)
  - Completed: `fa-check-circle` (green)
  - Cancelled: `fa-times-circle` (gray)
- `flex-shrink-0`: Never squish

### 5. Priority Indicator (Conditional)
```javascript
if (priority === 'critical') {
    priorityEl.innerHTML = '<i class="fas fa-exclamation-circle text-xs" style="color: #EF4444;"></i>';
    priorityEl.className = 'leading-none flex-shrink-0';
}
```
- Only shown for **critical** priority
- Red exclamation circle icon
- Urgent/high/medium priorities: tooltip only

### 6. Time Display (Conditional)
```javascript
var hasTime = workItem.start_time || (info.event.start && !info.event.allDay);
if (hasTime) {
    timeEl.textContent = '2:00 PM'; // Example
    timeEl.className = 'text-xs text-gray-600 flex-shrink-0';
}
```
- Only shown for **timed events** (not all-day)
- Format: `2:00 PM` or `2:00 PM - 4:00 PM`
- Gray text, extra small size

### 7. Expand Button (Conditional)
```javascript
if (workItem.hasChildren) {
    expandBtn.innerHTML = '<i class="fas fa-chevron-right text-xs"></i>';
    expandBtn.className = 'flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors';
}
```
- Only shown for **parent items**
- Chevron-right icon
- Hover effect (gray to darker gray)

---

## Container Structure

### Root Container
```javascript
eventRow.className = 'flex items-center gap-1 text-sm';
```
- `flex`: Horizontal layout
- `items-center`: Vertical centering
- `gap-1`: 0.25rem spacing between elements
- `text-sm`: Base font size (14px)

---

## Tooltip (All Metadata)

### Tooltip Content
```javascript
tooltipParts = [
  'PROJECT: Meeting with stakeholders',      // Work type + title
  'Status: in_progress',                      // Status
  'Priority: critical',                       // Priority (if not medium)
  'Recurring event',                          // If recurring
  'Project: BARMM Infrastructure',            // Parent project (if not project type)
  'Time: 2:00 PM - 4:00 PM'                  // Time (if timed)
];
info.el.setAttribute('title', tooltipParts.join('\n'));
```
- Native browser tooltip
- Multi-line (newline-separated)
- Shows on hover
- Includes ALL metadata (not just visible items)

---

## CSS Classes Reference

### Tailwind Utilities Used
```
flex                   - Flexbox layout
items-center          - Vertical alignment
gap-1                 - 0.25rem spacing
text-sm               - 14px font size
text-xs               - 12px font size
text-gray-400         - Light gray text
text-gray-600         - Medium gray text
flex-1                - Grow to fill space
flex-shrink-0         - Never shrink
truncate              - Ellipsis overflow
font-medium           - Medium font weight
leading-none          - No line height
leading-tight         - Compact line height
hover:text-gray-600   - Hover state
transition-colors     - Smooth color transition
```

---

## Examples

### Basic Task Event
```
[icon-tasks] Update documentation [check-circle]
```

### Critical Priority Project with Time
```
[icon-project] Infrastructure Review [spinner] [exclamation] 2:00 PM
```

### Child Activity (Hierarchy)
```
└ [icon-activity] Stakeholder meeting [circle] 10:00 AM
```

### Parent Item with Children
```
[icon-project] Q4 Planning [check-circle] [chevron-right]
```

### Recurring Event with Time
```
[icon-task] Weekly standup [spinner] 9:00 AM
```
(Tooltip shows: "Recurring event")

---

## Best Practices

### 1. Always Truncate Long Titles
```javascript
titleText.className = 'flex-1 truncate font-medium leading-tight';
```
- Prevents horizontal overflow
- Shows ellipsis (...)
- Hover tooltip shows full text

### 2. Use flex-shrink-0 for Icons
```javascript
iconEl.className = 'leading-none flex-shrink-0';
```
- Prevents icons from squishing
- Maintains icon aspect ratio

### 3. Remove Helper Function Spacing
```javascript
iconEl.innerHTML = getWorkItemIcon(workType).replace('mr-1', '');
```
- Helper functions add margins
- Remove margins for inline layout

### 4. Conditional Rendering
```javascript
if (priority === 'critical') {
    // Only show critical priority inline
}
```
- Don't clutter with low-priority info
- Move non-essential data to tooltip

### 5. Semantic HTML
```javascript
info.el.setAttribute('aria-label', tooltipParts.join(', '));
```
- Accessibility labels
- Screen reader support

---

## Common Pitfalls

### 1. Too Many Inline Elements
**Bad:**
```
[icon] Title [status] [priority] [time] [recurring] [project] [assignee]
```
**Good:**
```
[icon] Title [status] [critical-flag] [time]
```
- Keep inline elements minimal
- Move detailed info to tooltip

### 2. Vertical Stacking
**Bad:**
```javascript
contentContainer.className = 'flex flex-col gap-1';  // Vertical
```
**Good:**
```javascript
eventRow.className = 'flex items-center gap-1';      // Horizontal
```

### 3. Not Handling Long Titles
**Bad:**
```javascript
titleText.className = 'font-medium';  // No truncation
```
**Good:**
```javascript
titleText.className = 'flex-1 truncate font-medium';
```

### 4. Inconsistent Spacing
**Bad:**
```javascript
iconEl.innerHTML = getWorkItemIcon(workType);  // Includes mr-1
```
**Good:**
```javascript
iconEl.innerHTML = getWorkItemIcon(workType).replace('mr-1', '');
```

---

## Testing Checklist

- [ ] Title truncates with ellipsis when too long
- [ ] Icons maintain aspect ratio (no squishing)
- [ ] Spacing is consistent (gap-1)
- [ ] Tooltip shows all metadata on hover
- [ ] Critical priority shows red icon
- [ ] Time only appears for timed events
- [ ] Hierarchy indicator only for child items
- [ ] Expand button only for parents
- [ ] Click to open modal works
- [ ] Hover states work (expand button)

---

## Related Documentation

- [Calendar Event Compact Refactor](CALENDAR_EVENT_COMPACT_REFACTOR.md)
- [OBCMS UI Components & Standards](OBCMS_UI_COMPONENTS_STANDARDS.md)
- [Instant UI Improvements Plan](../instant_ui_improvements_plan.md)

---

## Quick Reference Card

```
EVENT LAYOUT: [opt-hierarchy] [icon] Title... [status] [opt-priority] [opt-time] [opt-expand]

HIERARCHY:  └  (text-gray-400, text-xs, only if level > 0)
ICON:       Work type icon (no margin, leading-none)
TITLE:      flex-1 truncate font-medium leading-tight
STATUS:     Status icon (flex-shrink-0, leading-none)
PRIORITY:   Red exclamation (only if critical)
TIME:       text-xs text-gray-600 (only if timed event)
EXPAND:     Chevron-right (only if hasChildren)

CONTAINER:  flex items-center gap-1 text-sm
TOOLTIP:    title="Work type: Title\nStatus: ...\n..."
```
