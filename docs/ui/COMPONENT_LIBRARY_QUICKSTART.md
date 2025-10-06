# OBCMS Component Library - Quick Start Guide

**Last Updated**: 2025-10-02
**Status**: Production-Ready

---

## What's New?

We've built a comprehensive **Reusable Component Library** with 4 new components and extensive documentation:

| Component | Purpose | Location |
|-----------|---------|----------|
| **Kanban Board** | Drag-and-drop task management | `src/templates/components/kanban_board.html` |
| **Calendar Widget** | FullCalendar integration | `src/templates/components/calendar_full.html` |
| **Modal Dialog** | Accessible popups | `src/templates/components/modal.html` |
| **Task Card** | Consistent task display | `src/templates/components/task_card.html` |

---

## 5-Minute Quick Start

### 1. Use the Kanban Board

```django
{# In your template #}
{% include "components/kanban_board.html" with
    board_id="my-tasks"
    columns=task_columns
    item_template="components/task_card.html"
    move_endpoint="/api/tasks/move/"
%}
```

**Django View**:
```python
def kanban_view(request):
    columns = [
        {
            'id': 'pending',
            'title': 'Pending',
            'items': Task.objects.filter(status='pending')
        },
        {
            'id': 'in_progress',
            'title': 'In Progress',
            'items': Task.objects.filter(status='in_progress')
        },
    ]
    return render(request, 'tasks/kanban.html', {'task_columns': columns})
```

### 2. Use the Calendar

```django
{# In your template #}
{% include "components/calendar_full.html" with
    calendar_id="project-calendar"
    events_feed_url="/api/tasks/calendar-feed/"
    editable=True
%}
```

**Django View for Feed**:
```python
def calendar_feed(request):
    tasks = Task.objects.filter(due_date__isnull=False)
    events = [{
        'id': task.id,
        'title': task.title,
        'start': task.due_date.isoformat(),
        'extendedProps': {'type': 'task', 'priority': task.priority}
    } for task in tasks]
    return JsonResponse(events, safe=False)
```

### 3. Use Modals

```django
{# Trigger button #}
<button hx-get="{% url 'task_detail_modal' task.id %}"
        hx-target="#modal-container"
        hx-swap="innerHTML">
    View Details
</button>

{# Modal container in base template #}
<div id="modal-container"></div>

{# Modal fragment (task_detail_modal.html) #}
{% include "components/modal.html" with
    title=task.title
    content_template="tasks/task_detail_content.html"
    size="lg"
%}
```

### 4. Use Task Cards

```django
{# Display a task #}
{% include "components/task_card.html" with task=task %}

{# In a loop #}
{% for task in tasks %}
    <div class="mb-4">
        {% include "components/task_card.html" with
            task=task
            show_actions=True
        %}
    </div>
{% endfor %}
```

---

## Documentation Reference

| Topic | File | Description |
|-------|------|-------------|
| **Component API** | `docs/ui/component_library_guide.md` | Complete parameter reference |
| **HTMX Patterns** | `docs/ui/htmx_patterns.md` | 10 interaction patterns |
| **Accessibility** | `docs/ui/accessibility_patterns.md` | WCAG 2.1 AA compliance |
| **Mobile Design** | `docs/ui/mobile_patterns.md` | Responsive patterns |
| **Overview** | `docs/ui/README.md` | UI documentation hub |

---

## Common Patterns

### Pattern: Load Content with HTMX

```html
<!-- Click to load content -->
<button hx-get="/content/url/"
        hx-target="#target-div"
        hx-swap="innerHTML">
    Load Content
</button>

<div id="target-div"></div>
```

### Pattern: Submit Form Without Reload

```html
<form hx-post="/form/submit/"
      hx-target="#result"
      hx-swap="innerHTML">
    <input type="text" name="title">
    <button type="submit">Submit</button>
</form>

<div id="result"></div>
```

### Pattern: Dependent Dropdowns

```html
<select id="region"
        hx-get="/api/provinces/"
        hx-trigger="change"
        hx-target="#province"
        hx-include="#region">
    <option>Select Region</option>
</select>

<select id="province">
    <option>Select Province</option>
</select>
```

### Pattern: Infinite Scroll

```html
<div id="list">
    {% for item in items %}
    <div>{{ item.title }}</div>
    {% endfor %}
</div>

{% if has_next %}
<div hx-get="?page={{ next_page }}"
     hx-trigger="revealed"
     hx-swap="afterend"
     hx-target="#list">
    Loading...
</div>
{% endif %}
```

---

## Accessibility Checklist

Before deploying, verify:

- [ ] All images have `alt` text
- [ ] All form inputs have labels
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus indicators are visible
- [ ] Color contrast is 4.5:1 for text
- [ ] ARIA labels on icon buttons
- [ ] Heading hierarchy is correct (H1 → H2 → H3)
- [ ] Dynamic content announced to screen readers

---

## Mobile Responsiveness

Use Tailwind responsive classes:

```html
<!-- 1 column mobile, 2 tablet, 3 desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Cards -->
</div>

<!-- Hide on mobile -->
<div class="hidden md:block">Desktop only</div>

<!-- Show on mobile only -->
<div class="block md:hidden">Mobile only</div>
```

**Test at these breakpoints**:
- 320px (small mobile)
- 375px (iPhone SE)
- 768px (tablet)
- 1024px (small desktop)
- 1280px (desktop)

---

## Performance Tips

1. **Lazy Load Heavy Components**:
   ```html
   <div hx-get="/heavy-component/"
        hx-trigger="revealed"
        hx-swap="innerHTML">
       Loading...
   </div>
   ```

2. **Optimize Images**:
   ```html
   <img src="image.jpg" loading="lazy" alt="Description">
   ```

3. **Minimize JavaScript**:
   - Use HTMX for most interactions
   - Alpine.js only for client-side state
   - Avoid jQuery

---

## Troubleshooting

### HTMX Not Working

**Problem**: Button clicks do nothing

**Solution**:
1. Check HTMX library is loaded: `<script src="https://unpkg.com/htmx.org@1.9.10"></script>`
2. Verify target element exists (e.g., `#modal-container`)
3. Check browser console for errors
4. Inspect Network tab for failed requests

### Modal Not Opening

**Problem**: Modal trigger does nothing

**Solution**:
1. Ensure Alpine.js is loaded with `defer` attribute
2. Verify `#modal-container` exists in template
3. Check that modal template path is correct
4. Look for Alpine.js errors in console

### Component Not Rendering

**Problem**: Component appears blank

**Solution**:
1. Verify all required parameters are passed
2. Check component file path is correct
3. Look for Django template syntax errors
4. Verify context data in view

---

## Best Practices

### DO ✅
- Use reusable components from `src/templates/components/`
- Follow mobile-first responsive design
- Test keyboard navigation
- Provide ARIA labels
- Handle loading and error states
- Keep JavaScript minimal

### DON'T ❌
- Duplicate component code
- Rely only on hover states
- Use touch targets < 44px
- Skip accessibility testing
- Ignore mobile breakpoints
- Remove focus indicators

---

## Getting Help

1. **Read Documentation**: Start with `docs/ui/README.md`
2. **Check Examples**: Review existing implementations
3. **Test in Browser**: Use DevTools to inspect elements
4. **Run Accessibility Audit**: Use axe DevTools or Lighthouse

---

## Next Steps

1. **Integrate Components**: Add components to your modules
2. **Review Documentation**: Read detailed guides in `docs/ui/`
3. **Test Thoroughly**: Verify accessibility and responsiveness
4. **Gather Feedback**: Conduct user acceptance testing

---

**Need More Info?**
- Full Documentation: `docs/ui/README.md`
- Component API: `docs/ui/component_library_guide.md`
- HTMX Patterns: `docs/ui/htmx_patterns.md`
- Implementation Report: `docs/ui/COMPONENT_LIBRARY_IMPLEMENTATION_COMPLETE.md`

**Status**: ✅ Production-Ready | All components tested and documented
