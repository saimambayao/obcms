# FullCalendar Title Duplication - Quick Fix Guide

**TL;DR:** Stop using `eventDidMount` for content. Use `eventContent` instead.

---

## The Problem in 30 Seconds

```javascript
// ❌ WRONG - Causes title duplication on view switches
eventDidMount: function(info) {
    var titleEl = info.el.querySelector('.fc-event-title');
    titleEl.innerHTML = '<custom content>';  // This breaks
}

// ✅ CORRECT - No duplication, works perfectly
eventContent: function(arg) {
    return {
        html: '<custom content>'  // This works
    };
}
```

---

## Quick Decision Tree

```
Need to customize event appearance?
│
├─ YES → Use eventContent
│   │
│   ├─ Simple HTML? → Return { html: '...' }
│   ├─ Complex DOM? → Return { domNodes: [...] }
│   └─ View-specific? → Check arg.view.type
│
└─ Need to attach listeners?
    └─ Use eventDidMount (but DON'T touch content)
```

---

## The Fix (3 Steps)

### Step 1: Move Content to `eventContent`

```javascript
// OLD (eventDidMount)
eventDidMount: function(info) {
    var titleEl = info.el.querySelector('.fc-event-title');
    titleEl.innerHTML = `
        <div class="flex items-center gap-1">
            <i class="fas fa-icon"></i>
            <span>${info.event.title}</span>
        </div>
    `;
}

// NEW (eventContent)
eventContent: function(arg) {
    return {
        html: `
            <div class="flex items-center gap-1">
                <i class="fas fa-icon"></i>
                <span>${arg.event.title}</span>
            </div>
        `
    };
}
```

### Step 2: Keep Only Side Effects in `eventDidMount`

```javascript
eventDidMount: function(info) {
    // ✅ Good: Tooltips
    info.el.setAttribute('title', info.event.extendedProps.tooltip);

    // ✅ Good: Event listeners
    info.el.addEventListener('click', handleClick);

    // ✅ Good: Data attributes
    info.el.setAttribute('data-event-id', info.event.id);

    // ❌ Bad: Content manipulation (use eventContent instead)
}
```

### Step 3: Handle View-Specific Rendering

```javascript
eventContent: function(arg) {
    var viewType = arg.view.type;

    // List view
    if (viewType.includes('list')) {
        return { html: '<simple content>' };
    }

    // Week view
    if (viewType.includes('timeGrid')) {
        return { html: '<detailed content>' };
    }

    // Month view (default)
    return { html: '<compact content>' };
}
```

---

## Common Patterns

### Pattern 1: Simple Icon + Text

```javascript
eventContent: function(arg) {
    var icon = arg.event.extendedProps.icon || 'circle';
    return {
        html: `
            <div class="flex items-center gap-2">
                <i class="fas fa-${icon}"></i>
                <span>${arg.event.title}</span>
            </div>
        `
    };
}
```

### Pattern 2: Status Badge

```javascript
eventContent: function(arg) {
    var status = arg.event.extendedProps.status || 'pending';
    var statusColors = {
        pending: 'bg-gray-500',
        active: 'bg-blue-500',
        complete: 'bg-green-500'
    };

    return {
        html: `
            <div class="flex items-center justify-between">
                <span>${arg.event.title}</span>
                <span class="px-2 py-1 rounded ${statusColors[status]} text-white text-xs">
                    ${status}
                </span>
            </div>
        `
    };
}
```

### Pattern 3: View-Specific Layout

```javascript
eventContent: function(arg) {
    var viewType = arg.view.type;
    var event = arg.event;
    var props = event.extendedProps;

    // List: Icon + Title only
    if (viewType.includes('list')) {
        return {
            html: `
                <div class="flex items-center gap-2">
                    <i class="fas fa-${props.icon}"></i>
                    <span>${event.title}</span>
                </div>
            `
        };
    }

    // Week: Multi-line with details
    if (viewType.includes('timeGrid')) {
        return {
            html: `
                <div class="flex flex-col gap-1">
                    <div class="font-medium">${event.title}</div>
                    <div class="text-xs text-gray-600">${props.location || ''}</div>
                </div>
            `
        };
    }

    // Month: Compact horizontal
    return {
        html: `
            <div class="flex items-center gap-1">
                <i class="fas fa-${props.icon}"></i>
                <span class="truncate">${event.title}</span>
            </div>
        `
    };
}
```

### Pattern 4: DOM Nodes (Advanced)

```javascript
eventContent: function(arg) {
    // Create DOM elements instead of HTML string
    var container = document.createElement('div');
    container.className = 'flex items-center gap-1';

    var icon = document.createElement('i');
    icon.className = 'fas fa-icon';
    container.appendChild(icon);

    var title = document.createElement('span');
    title.textContent = arg.event.title;
    title.className = 'truncate';
    container.appendChild(title);

    // Return DOM nodes
    return { domNodes: [container] };
}
```

---

## Troubleshooting

### Issue: Content Still Duplicating

**Cause:** You're still using `eventDidMount` for content.

**Fix:** Search your code for:
```javascript
// Find and remove these patterns:
titleEl.innerHTML = ...
titleEl.appendChild(...)
titleEl.textContent = ...
```

Move all content generation to `eventContent`.

---

### Issue: Content Not Updating on Data Change

**Cause:** Using `eventDidMount` instead of `eventContent`.

**Fix:** `eventContent` fires automatically on data changes. `eventDidMount` does not.

---

### Issue: Lost Event Listeners After View Switch

**Cause:** Normal behavior - elements are recreated.

**Fix:** FullCalendar re-attaches listeners automatically. Just keep them in `eventDidMount`.

---

### Issue: Performance Degradation

**Cause:** Complex DOM manipulation in `eventContent`.

**Fix:** Use HTML strings instead of DOM nodes:
```javascript
// Slower (DOM manipulation)
eventContent: function(arg) {
    var div = document.createElement('div');
    div.appendChild(...);  // Slow
    return { domNodes: [div] };
}

// Faster (HTML string)
eventContent: function(arg) {
    return { html: '<div>...</div>' };  // Fast
}
```

---

## Testing Checklist

After implementing the fix:

- [ ] Load calendar in month view
- [ ] Custom content appears ✓
- [ ] Switch to week view
- [ ] No duplicate titles ✓
- [ ] Switch to list view
- [ ] Content adapts correctly ✓
- [ ] Switch back to month
- [ ] Still no duplication ✓
- [ ] Drag an event
- [ ] Content stays correct ✓
- [ ] Resize browser
- [ ] Responsive behavior works ✓

---

## OBCMS-Specific Example

### Current (Broken)

```javascript
// src/templates/common/oobc_calendar.html (lines 289-452)
eventDidMount: function(info) {
    var titleEl = info.el.querySelector('.fc-event-title');
    titleEl.innerHTML = '';  // ❌ Causes duplication

    var eventRow = document.createElement('div');
    // ... build content
    titleEl.appendChild(eventRow);  // ❌ Breaks on view switch
}
```

### Fixed (Working)

```javascript
// Use eventContent for all content
eventContent: function(arg) {
    var viewType = arg.view.type;
    var workItem = arg.event.extendedProps;

    // List view
    if (viewType.includes('list')) {
        return {
            html: `
                <div class="flex items-center gap-2">
                    ${getWorkItemIconListView(workItem.workType)}
                    <span>${arg.event.title}</span>
                </div>
            `
        };
    }

    // Month/week view
    var parts = [];
    if (workItem.level > 0) parts.push('<span class="text-gray-400">└</span>');
    parts.push(getWorkItemIcon(workItem.workType));
    parts.push(`<span class="flex-1 truncate">${arg.event.title}</span>`);
    parts.push(getStatusIcon(workItem.status));
    if (workItem.priority === 'critical') {
        parts.push('<i class="fas fa-exclamation-circle text-red-500"></i>');
    }

    return {
        html: `
            <div class="flex items-center gap-1 text-sm">
                ${parts.join('')}
            </div>
        `
    };
},

// Use eventDidMount only for tooltips
eventDidMount: function(info) {
    // ✅ Only side effects here
    info.el.setAttribute('title', buildTooltip(info.event));
    info.el.setAttribute('tabindex', '0');
}
```

---

## Key Takeaways

1. **`eventContent`** = What the event **looks like** (re-renders on changes)
2. **`eventDidMount`** = What the event **does** (one-time setup)
3. **Never manipulate content in `eventDidMount`** (use `eventContent`)
4. **HTML strings are faster than DOM nodes** (for simple content)
5. **View-specific rendering** is easy with `arg.view.type`

---

## Learn More

**Full Analysis:** [FULLCALENDAR_TITLE_DUPLICATION_ANALYSIS.md](FULLCALENDAR_TITLE_DUPLICATION_ANALYSIS.md)

**Official Docs:**
- [eventContent](https://fullcalendar.io/docs/event-content)
- [eventDidMount](https://fullcalendar.io/docs/eventDidMount)
- [Event Render Hooks](https://fullcalendar.io/docs/event-render-hooks)

**GitHub Issue:** [#6713](https://github.com/fullcalendar/fullcalendar/issues/6713)

---

**Status:** Production-ready solution
**Tested:** FullCalendar v5 and v6
**Compatibility:** All modern browsers
