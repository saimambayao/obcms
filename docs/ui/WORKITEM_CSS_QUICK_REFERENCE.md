# WorkItem Integration CSS Quick Reference

**File:** `src/static/monitoring/css/workitem_integration.css`  
**Version:** 1.0.0

---

## 1. Stat Cards

```html
<div class="stat-card-3d">
    <div class="stat-card-icon stat-icon-emerald">
        <i class="fas fa-check-circle text-2xl"></i>
    </div>
    <div class="text-2xl font-bold">42</div>
    <div class="text-sm text-gray-600">Completed</div>
</div>
```

**Icon Colors:** `stat-icon-blue` | `stat-icon-emerald` | `stat-icon-purple` | `stat-icon-amber` | `stat-icon-red`

---

## 2. Tree View

```html
<div class="tree-node" style="--depth: 0">
    <div class="tree-node-content">
        <span class="tree-chevron"><i class="fas fa-chevron-down"></i></span>
        <span class="work-type-badge work-type-project">PROJECT</span>
        <span>Project Name</span>
    </div>
</div>
```

**Set --depth:** 0 (root), 1 (child), 2 (grandchild)

---

## 3. Work Type Badges

```html
<span class="work-type-badge work-type-project">PROJECT</span>
<span class="work-type-badge work-type-sub-project">SUB-PROJECT</span>
<span class="work-type-badge work-type-activity">ACTIVITY</span>
<span class="work-type-badge work-type-task">TASK</span>
<span class="work-type-badge work-type-subtask">SUBTASK</span>
```

---

## 4. Status Badges

```html
<span class="status-badge status-pending">Pending</span>
<span class="status-badge status-in-progress">In Progress</span>
<span class="status-badge status-completed">Completed</span>
<span class="status-badge status-blocked">Blocked</span>
<span class="status-badge status-on-hold">On Hold</span>
```

---

## 5. Progress Bars

```html
<div class="progress-bar-container">
    <div class="progress-bar-fill" style="width: 65%"></div>
</div>
<div class="progress-label">65% Complete</div>
```

**Set width via inline style:** `style="width: {{ percentage }}%"`

---

## 6. Budget Variance

```html
<span class="variance-indicator variance-under-budget">12% Under</span>
<span class="variance-indicator variance-near-budget">Within Budget</span>
<span class="variance-indicator variance-over-budget">8% Over</span>
```

---

## 7. Modals

```html
<div class="modal-overlay">
    <div class="modal-container">
        <!-- Content -->
    </div>
</div>
```

**Show:** `element.style.display = 'flex'`  
**Hide:** `element.style.display = 'none'`

---

## 8. Radio Cards

```html
<label class="radio-card">
    <input type="radio" name="method" class="sr-only">
    <div>Option Content</div>
</label>
```

**Selected:** Add `.selected` class via JavaScript

---

## 9. Gradient Button

```html
<button class="btn-gradient-primary">
    Create Work Item
</button>
```

**With spinner:** `<span class="loading-spinner"></span>`

---

## 10. Loading Spinner

```html
<span class="loading-spinner"></span>
```

**HTMX:** Auto-shown with `.htmx-request` class

---

## Color Reference

| Use Case | Class Suffix | Color |
|----------|-------------|-------|
| Info/Total | `-blue` | Blue (#3b82f6) |
| Success | `-emerald` | Emerald (#10b981) |
| Activity | `-purple` | Purple (#a855f7) |
| Warning | `-amber` | Amber (#f59e0b) |
| Critical | `-red` | Red (#ef4444) |

---

## Responsive Breakpoints

- **Mobile:** < 768px (reduced padding, compact layout)
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

---

## Accessibility

- All interactive elements have focus indicators
- Respects `prefers-reduced-motion`
- WCAG 2.1 AA compliant (4.5:1 contrast)
- Keyboard navigation supported

---

**Full Guide:** [WORKITEM_INTEGRATION_CSS_GUIDE.md](./WORKITEM_INTEGRATION_CSS_GUIDE.md)
