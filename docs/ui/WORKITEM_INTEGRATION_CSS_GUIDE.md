# WorkItem Integration CSS Usage Guide

**Version:** 1.0.0  
**Last Updated:** 2025-10-06  
**Location:** `src/static/monitoring/css/workitem_integration.css`

## Overview

This stylesheet provides custom CSS components for the WorkItem integration UI, complementing Tailwind CSS with specialized styling following OBCMS UI standards.

**Design Principles:**
- 3D milk white cards with subtle depth
- Gradient buttons (blue-to-teal primary)
- Semantic colors (emerald success, blue info, amber warning, red critical)
- Smooth transitions (300ms movements, 200ms deletions)
- WCAG 2.1 AA compliant (4.5:1 contrast minimum)

**Browser Support:**
- Chrome 90+, Firefox 88+, Safari 14+
- Graceful degradation for IE11+
- Reduced animations for motion-sensitive users

---

## 1. 3D Milk White Stat Cards

### Basic Usage

```html
<div class="stat-card-3d">
    <div class="stat-card-icon stat-icon-blue">
        <i class="fas fa-project-diagram text-2xl"></i>
    </div>
    <div class="text-2xl font-bold text-gray-900">42</div>
    <div class="text-sm text-gray-600">Total Projects</div>
</div>
```

### Icon Color Variants

| Class | Use Case | Color |
|-------|----------|-------|
| `stat-icon-blue` | Informational, totals | Blue (#3b82f6) |
| `stat-icon-emerald` | Success, completed | Emerald (#10b981) |
| `stat-icon-purple` | Activities, drafts | Purple (#a855f7) |
| `stat-icon-amber` | Warnings, pending | Amber (#f59e0b) |
| `stat-icon-red` | Critical, overdue | Red (#ef4444) |

### Features
- Gradient background (white to gray-50)
- Layered shadows for depth
- Top accent border on hover
- Lift animation on hover (-2px translateY)

---

## 2. Tree View Connectors

### Basic Tree Structure

```html
<div class="tree-container">
    <div class="tree-node" style="--depth: 0">
        <div class="tree-node-content">
            <span class="tree-chevron">
                <i class="fas fa-chevron-down"></i>
            </span>
            <span class="work-type-badge work-type-project">PROJECT</span>
            <span class="font-semibold">BARMM Infrastructure Development</span>
        </div>
        <div class="children-container">
            <div class="tree-node" style="--depth: 1">
                <div class="tree-node-content">
                    <span class="tree-chevron">
                        <i class="fas fa-chevron-right"></i>
                    </span>
                    <span class="work-type-badge work-type-activity">ACTIVITY</span>
                    <span class="font-semibold">Road Construction - Phase 1</span>
                </div>
            </div>
        </div>
    </div>
</div>
```

### CSS Custom Properties
- `--depth`: Indentation level (0 = root, 1 = child, 2 = grandchild, etc.)
- Automatic connector lines via `::before` and `::after` pseudo-elements

### Expand/Collapse Behavior
```javascript
// Toggle children visibility
function toggleNode(chevronElement) {
    const container = chevronElement.closest('.tree-node').querySelector('.children-container');
    container.classList.toggle('hidden');
    
    // Rotate chevron
    const icon = chevronElement.querySelector('i');
    icon.classList.toggle('fa-chevron-down');
    icon.classList.toggle('fa-chevron-right');
}
```

---

## 3. Work Type Badges

### Available Types

```html
<!-- Project -->
<span class="work-type-badge work-type-project">PROJECT</span>

<!-- Sub-Project -->
<span class="work-type-badge work-type-sub-project">SUB-PROJECT</span>

<!-- Activity -->
<span class="work-type-badge work-type-activity">ACTIVITY</span>

<!-- Task -->
<span class="work-type-badge work-type-task">TASK</span>

<!-- Subtask -->
<span class="work-type-badge work-type-subtask">SUBTASK</span>
```

### Color Mapping
| Type | Background | Text Color |
|------|------------|------------|
| Project | Blue-50 (#dbeafe) | Blue-900 (#1e40af) |
| Sub-Project | Emerald-50 (#d1fae5) | Emerald-900 (#065f46) |
| Activity | Purple-50 (#e9d5ff) | Purple-900 (#6b21a8) |
| Task | Amber-50 (#fef3c7) | Amber-900 (#92400e) |
| Subtask | Gray-50 (#f3f4f6) | Gray-700 (#374151) |

---

## 4. Status Badges

### Usage Examples

```html
<!-- Pending -->
<span class="status-badge status-pending">
    <i class="fas fa-clock"></i> Pending
</span>

<!-- In Progress -->
<span class="status-badge status-in-progress">
    <i class="fas fa-spinner fa-spin"></i> In Progress
</span>

<!-- Completed -->
<span class="status-badge status-completed">
    <i class="fas fa-check-circle"></i> Completed
</span>

<!-- Blocked -->
<span class="status-badge status-blocked">
    <i class="fas fa-exclamation-triangle"></i> Blocked
</span>

<!-- On Hold -->
<span class="status-badge status-on-hold">
    <i class="fas fa-pause-circle"></i> On Hold
</span>
```

---

## 5. Progress Bars

### Basic Progress Bar

```html
<div class="space-y-1">
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: 65%"></div>
    </div>
    <div class="progress-label">65% Complete</div>
</div>
```

### HTMX Integration

```html
<div class="space-y-1" 
     hx-get="/api/work-items/{{ item.id }}/progress/"
     hx-trigger="every 5s"
     hx-swap="outerHTML">
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: {{ item.progress_percentage }}%"></div>
    </div>
    <div class="progress-label">{{ item.progress_percentage }}% Complete</div>
</div>
```

### Features
- Gradient fill (emerald-500 to emerald-600)
- Shimmer animation overlay
- Smooth width transition (600ms cubic-bezier)

---

## 6. Budget Variance Indicators

### Usage

```html
<!-- Under Budget -->
<span class="variance-indicator variance-under-budget">
    <i class="fas fa-arrow-down"></i> 12% Under Budget
</span>

<!-- Near Budget -->
<span class="variance-indicator variance-near-budget">
    <i class="fas fa-equals"></i> Within Budget
</span>

<!-- Over Budget -->
<span class="variance-indicator variance-over-budget">
    <i class="fas fa-arrow-up"></i> 8% Over Budget
</span>
```

### Django Template Example

```django
{% if item.variance_percentage < -5 %}
    <span class="variance-indicator variance-under-budget">
        <i class="fas fa-arrow-down"></i> {{ item.variance_percentage|abs }}% Under Budget
    </span>
{% elif item.variance_percentage > 5 %}
    <span class="variance-indicator variance-over-budget">
        <i class="fas fa-arrow-up"></i> {{ item.variance_percentage }}% Over Budget
    </span>
{% else %}
    <span class="variance-indicator variance-near-budget">
        <i class="fas fa-equals"></i> Within Budget
    </span>
{% endif %}
```

---

## 7. Modal Styling

### Full Modal Example

```html
<div class="modal-overlay" id="workitem-modal" style="display: none;">
    <div class="modal-container max-w-4xl">
        <!-- Modal Header -->
        <div class="border-b border-gray-200 px-6 py-4">
            <div class="flex items-center justify-between">
                <h2 class="text-2xl font-bold text-gray-900">Add Sub-Project</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
        </div>

        <!-- Modal Body -->
        <div class="px-6 py-4">
            <!-- Form content here -->
        </div>

        <!-- Modal Footer -->
        <div class="border-t border-gray-200 px-6 py-4 bg-gray-50">
            <div class="flex items-center justify-end gap-3">
                <button onclick="closeModal()" class="px-4 py-2 border border-gray-300 rounded-lg">
                    Cancel
                </button>
                <button class="btn-gradient-primary">
                    Create Sub-Project
                </button>
            </div>
        </div>
    </div>
</div>
```

### JavaScript Control

```javascript
function showModal() {
    document.getElementById('workitem-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Prevent background scroll
}

function closeModal() {
    document.getElementById('workitem-modal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close on overlay click
document.querySelector('.modal-overlay').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});
```

---

## 8. Radio Cards

### Method Selection Example

```html
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Option 1 -->
    <label class="radio-card">
        <input type="radio" name="creation_method" value="blank" class="sr-only" required>
        <div class="flex items-start gap-3">
            <div class="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-file text-blue-600 text-xl"></i>
            </div>
            <div>
                <div class="font-semibold text-gray-900">Create from Blank</div>
                <div class="text-sm text-gray-600">Start with an empty sub-project</div>
            </div>
        </div>
    </label>

    <!-- Option 2 -->
    <label class="radio-card">
        <input type="radio" name="creation_method" value="template" class="sr-only">
        <div class="flex items-start gap-3">
            <div class="w-12 h-12 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-copy text-emerald-600 text-xl"></i>
            </div>
            <div>
                <div class="font-semibold text-gray-900">Use Template</div>
                <div class="text-sm text-gray-600">Copy from existing project</div>
            </div>
        </div>
    </label>
</div>
```

### JavaScript Enhancement

```javascript
document.querySelectorAll('.radio-card input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function() {
        // Remove selected class from all cards
        document.querySelectorAll('.radio-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selected class to parent card
        if (this.checked) {
            this.closest('.radio-card').classList.add('selected');
        }
    });
});
```

---

## 9. Gradient Buttons

### Usage

```html
<!-- Primary gradient button (OBCMS standard) -->
<button class="btn-gradient-primary">
    Create Work Item
</button>

<!-- With loading state -->
<button class="btn-gradient-primary htmx-request">
    <span class="loading-spinner mr-2"></span>
    Creating...
</button>

<!-- Disabled state -->
<button class="btn-gradient-primary" disabled>
    Cannot Submit
</button>
```

### HTMX Integration

```html
<button class="btn-gradient-primary"
        hx-post="/api/work-items/create/"
        hx-swap="outerHTML"
        hx-target="#work-item-list"
        hx-indicator=".loading-spinner">
    <span class="loading-spinner mr-2" style="display: none;"></span>
    <span>Create Work Item</span>
</button>
```

---

## 10. Loading Spinners

### Standalone Spinner

```html
<div class="flex items-center justify-center py-8">
    <span class="loading-spinner" style="width: 2rem; height: 2rem;"></span>
</div>
```

### HTMX Loading Indicator

```html
<div hx-get="/api/work-items/" hx-trigger="load">
    <div class="loading-spinner"></div>
    Loading work items...
</div>
```

---

## 11. Responsive Design

### Mobile Breakpoints
- **Mobile**: < 768px
  - Reduced stat card padding (1rem instead of 1.5rem)
  - Reduced tree indentation (1rem instead of 1.5rem per level)
  - Modal width: 95vw with 1rem margin
  - Smaller badge font sizes

### Example: Responsive Grid

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div class="stat-card-3d">
        <!-- Stat card content -->
    </div>
    <div class="stat-card-3d">
        <!-- Stat card content -->
    </div>
    <div class="stat-card-3d">
        <!-- Stat card content -->
    </div>
    <div class="stat-card-3d">
        <!-- Stat card content -->
    </div>
</div>
```

---

## 12. Accessibility

### Keyboard Navigation

```html
<!-- Accessible tree node -->
<div class="tree-node" role="treeitem" tabindex="0" aria-expanded="true">
    <button class="tree-chevron" 
            aria-label="Collapse node"
            onclick="toggleNode(this)">
        <i class="fas fa-chevron-down"></i>
    </button>
    <span>Project Name</span>
</div>
```

### Screen Reader Support

```html
<!-- Progress bar with aria-label -->
<div class="progress-bar-container" 
     role="progressbar" 
     aria-valuenow="65" 
     aria-valuemin="0" 
     aria-valuemax="100"
     aria-label="Project completion">
    <div class="progress-bar-fill" style="width: 65%"></div>
</div>
```

### Focus Management

```javascript
// Focus first input when modal opens
function showModal() {
    const modal = document.getElementById('workitem-modal');
    modal.style.display = 'flex';
    
    // Focus first input
    const firstInput = modal.querySelector('input, textarea, select');
    if (firstInput) firstInput.focus();
}
```

---

## 13. Complete Integration Example

### Full Dashboard Section

```html
<!-- Statistics Cards -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div class="stat-card-3d">
        <div class="stat-card-icon stat-icon-blue">
            <i class="fas fa-project-diagram text-2xl"></i>
        </div>
        <div class="text-2xl font-bold text-gray-900">12</div>
        <div class="text-sm text-gray-600">Total Projects</div>
    </div>
    
    <div class="stat-card-3d">
        <div class="stat-card-icon stat-icon-emerald">
            <i class="fas fa-check-circle text-2xl"></i>
        </div>
        <div class="text-2xl font-bold text-gray-900">8</div>
        <div class="text-sm text-gray-600">Completed</div>
    </div>
    
    <div class="stat-card-3d">
        <div class="stat-card-icon stat-icon-purple">
            <i class="fas fa-tasks text-2xl"></i>
        </div>
        <div class="text-2xl font-bold text-gray-900">28</div>
        <div class="text-sm text-gray-600">Active Tasks</div>
    </div>
    
    <div class="stat-card-3d">
        <div class="stat-card-icon stat-icon-amber">
            <i class="fas fa-clock text-2xl"></i>
        </div>
        <div class="text-2xl font-bold text-gray-900">4</div>
        <div class="text-sm text-gray-600">Pending</div>
    </div>
</div>

<!-- Work Item Tree -->
<div class="bg-white rounded-xl border border-gray-200 shadow-sm">
    <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">Project Hierarchy</h3>
    </div>
    
    <div class="tree-container p-6">
        <div class="tree-node" style="--depth: 0">
            <div class="tree-node-content">
                <span class="tree-chevron" onclick="toggleNode(this)">
                    <i class="fas fa-chevron-down"></i>
                </span>
                <span class="work-type-badge work-type-project">PROJECT</span>
                <span class="font-semibold">BARMM Infrastructure Development</span>
                <span class="status-badge status-in-progress ml-auto">
                    <i class="fas fa-spinner fa-spin"></i> In Progress
                </span>
            </div>
            
            <div class="children-container">
                <div class="tree-node" style="--depth: 1">
                    <div class="tree-node-content">
                        <span class="work-type-badge work-type-activity">ACTIVITY</span>
                        <span>Road Construction - Phase 1</span>
                        
                        <!-- Progress bar -->
                        <div class="ml-auto w-32">
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill" style="width: 65%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## Integration Checklist

When implementing WorkItem integration UI:

- [ ] Include CSS file in base template (`<link rel="stylesheet" href="{% static 'monitoring/css/workitem_integration.css' %}")
- [ ] Use `stat-card-3d` for all statistics displays
- [ ] Apply semantic icon colors (`stat-icon-blue`, `stat-icon-emerald`, etc.)
- [ ] Implement tree connectors with `--depth` CSS custom property
- [ ] Use work type badges for hierarchy visualization
- [ ] Add status badges for workflow states
- [ ] Include progress bars with shimmer animation
- [ ] Apply budget variance indicators where applicable
- [ ] Use modal styling for creation/edit dialogs
- [ ] Implement radio cards for method selection
- [ ] Apply gradient buttons for primary actions
- [ ] Add loading spinners for HTMX requests
- [ ] Test responsive behavior on mobile devices
- [ ] Verify accessibility (keyboard navigation, screen readers)
- [ ] Ensure WCAG 2.1 AA compliance (contrast ratios)

---

## Performance Considerations

### CSS Loading
```html
<!-- Preload critical CSS -->
<link rel="preload" href="{% static 'monitoring/css/workitem_integration.css' %}" as="style">
<link rel="stylesheet" href="{% static 'monitoring/css/workitem_integration.css' %}">
```

### Reduced Motion
The CSS automatically respects `prefers-reduced-motion: reduce` preference:
- Animations are reduced to 0.01ms
- No transformations or transitions

### Print Optimization
Print styles automatically:
- Remove shadows
- Simplify colors (black/white)
- Hide interactive elements (chevrons, spinners)

---

## Browser Compatibility

| Browser | Version | Support Level |
|---------|---------|---------------|
| Chrome | 90+ | Full support |
| Firefox | 88+ | Full support |
| Safari | 14+ | Full support |
| Edge | 90+ | Full support |
| IE | 11+ | Graceful degradation (reduced animations) |

### Fallbacks for Older Browsers
- `backdrop-filter: blur()` → Solid background color
- CSS custom properties → Fixed indentation values
- Gradient borders → Solid border colors
- Animations → Instant state changes

---

## Troubleshooting

### Issue: Stat cards not showing hover effect
**Solution:** Ensure card has `stat-card-3d` class, not just `stat-card`.

### Issue: Tree connectors not aligning
**Solution:** Verify `--depth` CSS custom property is set correctly on each `.tree-node`.

### Issue: Modal not scrolling
**Solution:** Check `max-height: 90vh` is applied to `.modal-container`.

### Issue: Progress bar not animating
**Solution:** Ensure width is set via inline style: `style="width: 65%"`, not class.

### Issue: Radio cards not showing checkmark when selected
**Solution:** Add `.selected` class via JavaScript when radio input changes.

---

## Related Documentation

- [OBCMS UI Components & Standards Guide](./OBCMS_UI_COMPONENTS_STANDARDS.md)
- [WorkItem Integration Implementation Plan](../improvements/WORKITEM_INTEGRATION_IMPLEMENTATION.md)
- [Accessibility Guidelines](./ACCESSIBILITY_GUIDELINES.md)
- [Tailwind CSS Configuration](../../tailwind.config.js)

---

**Questions or Issues?** Contact the OBCMS Development Team.
