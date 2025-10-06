# Calendar Event Icons - Visual Reference Guide

**Date**: 2025-10-06
**Purpose**: Quick visual reference for verifying event icons are displaying correctly

---

## Icon Specifications

### Projects
- **Icon**: `<i class="fas fa-folder"></i>` 📁
- **Color**: Blue (`#3b82f6`)
- **HTML**: `<i class="fas fa-folder" style="margin-right: 4px;"></i>`
- **Expected Appearance**: Blue folder icon before project name

**Example Event**:
```
📁 Infrastructure Development Project
```

---

### Activities
- **Icon**: `<i class="fas fa-calendar-check"></i>` ✓
- **Color**: Green (`#10b981`)
- **HTML**: `<i class="fas fa-calendar-check" style="margin-right: 4px;"></i>`
- **Expected Appearance**: Green calendar-check icon before activity name

**Example Event**:
```
✓ Community Workshop Series
```

---

### Tasks
- **Icon**: `<i class="fas fa-tasks"></i>` ☐
- **Color**: Purple (`#8b5cf6`)
- **HTML**: `<i class="fas fa-tasks" style="margin-right: 4px;"></i>`
- **Expected Appearance**: Purple tasks icon before task name

**Example Event**:
```
☐ Survey Data Collection
```

---

### Coordination
- **Icon**: `<i class="fas fa-handshake"></i>` 🤝
- **Color**: Teal (`#14b8a6`)
- **HTML**: `<i class="fas fa-handshake" style="margin-right: 4px;"></i>`
- **Expected Appearance**: Teal handshake icon before coordination event name

**Example Event**:
```
🤝 Stakeholder Meeting
```

---

## Visual Verification Checklist

### In Month View
```
┌─────────────────────────────────────────────────────────┐
│  Sun   Mon   Tue   Wed   Thu   Fri   Sat                │
│                                                          │
│   1     2     3     4     5     6     7                  │
│         📁Project  ✓Activity                             │
│                    ☐Task                                 │
│                                                          │
│   8     9    10    11    12    13    14                  │
│  🤝Meeting  📁Project              ✓Workshop             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Verify**:
- [ ] Each event has an icon
- [ ] Icon color matches event background
- [ ] Icon appears before event title
- [ ] 4px spacing between icon and text
- [ ] Icons don't overlap or get cut off

---

### In Week View
```
┌──────┬───────────────────────────────────────────────────┐
│ Time │ Monday                                            │
├──────┼───────────────────────────────────────────────────┤
│ 9am  │ 📁 Infrastructure Development Project             │
│      │ (Blue background)                                 │
├──────┼───────────────────────────────────────────────────┤
│ 11am │ ✓ Community Workshop                              │
│      │ (Green background)                                │
├──────┼───────────────────────────────────────────────────┤
│ 2pm  │ 🤝 Stakeholder Meeting                            │
│      │ (Teal background)                                 │
└──────┴───────────────────────────────────────────────────┘
```

**Verify**:
- [ ] Icons visible at start of each event
- [ ] Icons scale with event height
- [ ] No truncation in narrow time slots
- [ ] Icons maintain color consistency

---

### In Day View
```
┌──────────────────────────────────────────────────────────┐
│ 9:00 AM - 10:00 AM                                       │
│ 📁 Infrastructure Development Project                    │
│ Blue background, folder icon                             │
├──────────────────────────────────────────────────────────┤
│ 11:00 AM - 12:00 PM                                      │
│ ✓ Community Workshop Series                              │
│ Green background, calendar-check icon                    │
├──────────────────────────────────────────────────────────┤
│ 2:00 PM - 3:00 PM                                        │
│ 🤝 Stakeholder Coordination Meeting                      │
│ Teal background, handshake icon                          │
└──────────────────────────────────────────────────────────┘
```

**Verify**:
- [ ] Icons prominent and clear
- [ ] Full event titles visible
- [ ] Icons aligned to left edge
- [ ] Consistent sizing across all events

---

### In Year View (Multi-Month)
```
┌─────────────────────┐  ┌─────────────────────┐
│   January 2025      │  │   February 2025     │
├─────────────────────┤  ├─────────────────────┤
│  📁  ✓  ☐  🤝       │  │  📁  ✓  ☐           │
│  (Small icons)      │  │  (Small icons)      │
└─────────────────────┘  └─────────────────────┘
```

**Verify**:
- [ ] Icons visible (may be small)
- [ ] No layout breaking
- [ ] Events remain clickable
- [ ] Icons don't overflow cell boundaries

---

## Icon Rendering Locations

### Primary Location (Most Common)
```html
<div class="fc-event">
    <div class="fc-event-main">
        <div class="fc-event-title">
            <i class="fas fa-folder" style="margin-right: 4px;"></i>
            Project Name
        </div>
    </div>
</div>
```

**Where to Check**: `.fc-event-title` (first child is icon)

---

### Alternative Location (Some Views)
```html
<div class="fc-event">
    <div class="fc-event-main">
        <i class="fas fa-folder" style="margin-right: 4px;"></i>
        Project Name
    </div>
</div>
```

**Where to Check**: `.fc-event-main` (first child is icon)

---

### Fallback Location (Edge Cases)
```html
<div class="fc-event">
    <i class="fas fa-folder" style="margin-right: 4px;"></i>
    <div class="fc-event-main">
        Project Name
    </div>
</div>
```

**Where to Check**: `.fc-event` (first child is icon)

---

## Browser DevTools Inspection

### How to Verify Icons in DevTools

1. **Open DevTools** (F12 or Cmd+Option+I)
2. **Select an event element**
3. **Look for icon HTML**:
   ```html
   <i class="fas fa-folder" style="margin-right: 4px;"></i>
   ```
4. **Verify CSS classes**:
   - `fas` (FontAwesome Solid)
   - `fa-folder` / `fa-calendar-check` / `fa-tasks` / `fa-handshake`
5. **Check inline style**: `margin-right: 4px;`

---

### Console Verification

**Check if FontAwesome is loaded**:
```javascript
// In browser console
document.querySelector('.fas').computedStyleMap().get('font-family')
// Expected: "Font Awesome 5 Free" or similar
```

**Check icon count**:
```javascript
// Count all event icons
document.querySelectorAll('.fc-event .fas').length
// Should match total visible events
```

---

## Common Issues & Solutions

### Issue 1: No Icons Visible
**Symptoms**: Events show only text, no icons
**Check**:
- FontAwesome CSS loaded? (`<link>` tag in `<head>`)
- JavaScript executed without errors? (check console)
- `eventDidMount` hook called? (add `console.log('eventDidMount called')`)

**Solution**:
```javascript
// Verify in console
document.querySelector('.fas')  // Should return an element
```

---

### Issue 2: Wrong Icon Type
**Symptoms**: All events show same icon (e.g., all folders)
**Check**:
- `work_type` property in event data
- `workTypeIcons` mapping correct
- Icon class assignment logic

**Debug**:
```javascript
// In eventDidMount hook
console.log('Work type:', info.event.extendedProps.work_type);
console.log('Icon class:', workTypeIcons[workType]);
```

---

### Issue 3: Icons Cut Off or Hidden
**Symptoms**: Icons partially visible or truncated
**Check**:
- Event container `overflow: hidden`
- Icon `margin-right` applied
- Parent element width sufficient

**CSS Fix**:
```css
.fc-event-title {
    overflow: visible !important;  /* If icons cut off */
}
```

---

### Issue 4: Icons Not Aligned
**Symptoms**: Icons appear below or to the right of text
**Check**:
- Icon inserted as first child (`insertBefore(icon, element.firstChild)`)
- No conflicting CSS `float` or `position`
- `margin-right: 4px` applied

**Verify**:
```javascript
// Icon should be first child
document.querySelector('.fc-event-title').firstChild.tagName
// Expected: "I" (icon element)
```

---

## Expected DOM Structure

### Correct Structure ✅
```html
<div class="fc-event" style="background-color: #3b82f6;">
    <div class="fc-event-main">
        <div class="fc-event-title">
            <i class="fas fa-folder" style="margin-right: 4px;"></i>
            <!-- Icon is FIRST child -->
            Infrastructure Development Project
        </div>
    </div>
</div>
```

---

### Incorrect Structure ❌
```html
<div class="fc-event" style="background-color: #3b82f6;">
    <div class="fc-event-main">
        <div class="fc-event-title">
            Infrastructure Development Project
            <i class="fas fa-folder"></i>
            <!-- Icon is LAST child (wrong!) -->
        </div>
    </div>
</div>
```

---

## Quick Visual Test

**5-Second Check**:
1. Open calendar in Month view
2. Look for icons at the start of each event
3. Verify 4 different icon types visible:
   - 📁 Folder (blue projects)
   - ✓ Calendar-check (green activities)
   - ☐ Tasks (purple tasks)
   - 🤝 Handshake (teal coordination)

**If all 4 icon types visible → Icons working correctly! ✅**

---

## Screenshot Checklist

When reporting issues, include screenshots showing:
- [ ] Full calendar view
- [ ] Individual event with missing/incorrect icon
- [ ] Browser DevTools Elements tab (showing HTML)
- [ ] Browser console (showing any errors)
- [ ] Network tab (verify FontAwesome loaded)

---

## Color Verification

**Icon Background Colors** (should match sidebar legend):
```javascript
// Projects
background-color: #3b82f6  // Blue

// Activities
background-color: #10b981  // Green

// Tasks
background-color: #8b5cf6  // Purple

// Coordination
background-color: #14b8a6  // Teal
```

**Quick Check**:
- Blue events = Folder icon
- Green events = Calendar-check icon
- Purple events = Tasks icon
- Teal events = Handshake icon

---

## Accessibility Notes

**Screen Reader Announcements**:
- Icons should be decorative (not announced separately)
- Event title announces normally
- ARIA labels on checkboxes work correctly

**Keyboard Navigation**:
- Icons don't interfere with Tab navigation
- Events remain clickable with Enter key

---

## Performance Metrics

**Icon Rendering Performance**:
- **Expected**: < 2ms per icon insertion
- **Acceptable**: < 5ms per icon
- **Problematic**: > 10ms per icon

**Measure in DevTools**:
```javascript
// In console
performance.mark('icon-start');
// Trigger icon render (e.g., change view)
performance.mark('icon-end');
performance.measure('icon-render', 'icon-start', 'icon-end');
```

---

## Related Files

**Calendar Template**:
- `/src/templates/common/calendar_advanced_modern.html`

**Icon Mapping** (lines 796-802):
```javascript
const workTypeIcons = {
    'project': 'fa-folder',
    'activity': 'fa-calendar-check',
    'task': 'fa-tasks',
    'coordination': 'fa-handshake'
};
```

**Icon Insertion Logic** (lines 834-861):
- Checks for `.fc-event-title` (primary)
- Falls back to `.fc-event-main` (alternative)
- Final fallback to `.fc-event` (edge cases)

---

## Summary

**Icons Working Correctly When**:
- ✅ Icons visible on all events
- ✅ Correct icon type for each work type
- ✅ Icons appear before event title
- ✅ 4px spacing between icon and text
- ✅ Icons visible in all calendar views
- ✅ No console errors related to icons
- ✅ Events remain clickable
- ✅ Icons don't break layout

**Icons NOT Working If**:
- ❌ No icons visible on any events
- ❌ All events show same icon type
- ❌ Icons appear after text (not before)
- ❌ Icons cut off or truncated
- ❌ Console errors about FontAwesome
- ❌ Events not clickable due to icon overlap

---

**Quick Reference**: Icons should match sidebar legend exactly - same icon, same color, same order.

**Testing Time**: 2-3 minutes for visual verification across all views.
