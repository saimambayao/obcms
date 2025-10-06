# WorkItem JavaScript - Quick Reference

**File:** `src/static/monitoring/js/workitem_integration.js`
**Size:** 856 lines
**Dependencies:** HTMX

---

## Quick Start

### 1. Include JavaScript File

```html
<!-- In your template (after HTMX) -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="{% static 'monitoring/js/workitem_integration.js' %}"></script>
```

### 2. Initialize Budget Distribution

```html
<!-- Add data attribute to modal -->
<div id="budgetDistributionModal" data-total-budget="{{ ppa.budget_allocation }}">
    <!-- Modal content will auto-initialize BudgetDistribution -->
</div>
```

### 3. Use Tree View

```html
<!-- Tree node button -->
<button onclick="toggleWorkItemChildren('{{ work_item.id }}')">
    <i id="toggle-icon-{{ work_item.id }}" class="fas fa-chevron-right"></i>
    {{ work_item.title }}
</button>

<!-- Children container -->
<div id="children-{{ work_item.id }}" class="work-item-children collapsed">
    <!-- Child nodes -->
</div>
```

---

## API Quick Reference

### Public Functions

```javascript
// Tree Management
window.toggleWorkItemChildren(workItemId)

// Modal Management
window.openBudgetDistributionModal()
window.closeBudgetDistributionModal()

// Progress Updates
window.updateWorkItemProgress(workItemId, progress)
```

### Internal Modules

```javascript
// Budget Distribution
BudgetDistribution.init(totalBudget)
BudgetDistribution.validateWeighted()  // Returns: boolean
BudgetDistribution.validateManual()    // Returns: boolean
BudgetDistribution.formatCurrency(amt) // Returns: string (₱1,234.56)

// Modal Manager
ModalManager.openModal(modalId)
ModalManager.closeModal(modalId)

// Toast Notifications
showToast(message, type)  // type: 'success' | 'error' | 'warning' | 'info'
```

---

## Required HTML Classes & IDs

### Budget Distribution

```html
<!-- Distribution method radios (name MUST be "distribution_method") -->
<input type="radio" name="distribution_method" value="equal">
<input type="radio" name="distribution_method" value="weighted">
<input type="radio" name="distribution_method" value="manual">

<!-- Weighted inputs (class MUST be "weight-input") -->
<input type="number" class="weight-input" name="weight_{{ work_item.id }}">

<!-- Manual inputs (class MUST be "manual-budget-input") -->
<input type="text" class="manual-budget-input" name="manual_{{ work_item.id }}">

<!-- Validation containers (IDs MUST match method name) -->
<div id="weighted-validation"></div>
<div id="manual-validation"></div>
<div id="equal-distribution-preview"></div>

<!-- Method sections (class MUST be "distribution-method-section") -->
<div id="equal-distribution-section" class="distribution-method-section"></div>
<div id="weighted-distribution-section" class="distribution-method-section hidden"></div>
<div id="manual-distribution-section" class="distribution-method-section hidden"></div>

<!-- Submit button (ID MUST be "distribute-submit") -->
<button id="distribute-submit" type="submit">Distribute</button>
```

### Tree View

```html
<!-- Toggle icon (ID pattern: toggle-icon-{workItemId}) -->
<i id="toggle-icon-{{ work_item.id }}" class="fas fa-chevron-right"></i>

<!-- Children container (ID pattern: children-{workItemId}, class MUST be "work-item-children") -->
<div id="children-{{ work_item.id }}" class="work-item-children collapsed"></div>
```

### Modals

```html
<!-- Modal container (must have unique ID) -->
<div id="budgetDistributionModal" class="hidden" aria-hidden="true" role="dialog">
    <!-- Must contain focusable elements (button, input, etc.) -->
</div>
```

---

## HTMX Integration

### Backend Response Headers

```python
# Django view example
return HttpResponse(
    status=204,
    headers={
        'HX-Trigger': json.dumps({
            'show-toast': {
                'message': 'Success!',
                'type': 'success'
            },
            'refresh-counters': True,
            'refresh-progress': True,
            'close-modal': 'budgetDistributionModal'
        })
    }
)
```

### Supported HX-Trigger Events

| Event | Payload | Action |
|-------|---------|--------|
| `show-toast` | `{message: string, type: string}` or `string` | Display toast |
| `refresh-counters` | `true` | Refresh stat counters |
| `refresh-progress` | `true` | Refresh progress bars |
| `close-modal` | `string` (modal ID) | Close modal |

### HTMX Template Pattern

```html
<!-- Add loading-trigger class for loading spinner -->
<form hx-post="..." hx-target="..." class="loading-trigger">
    <button type="submit">Submit</button>
</form>
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Escape` | Close all modals |
| `Ctrl+E` | Expand all work items |
| `Ctrl+C` | Collapse all work items |
| `Enter` or `Space` | Toggle tree node (when focused) |
| `Tab` | Next element in modal |
| `Shift+Tab` | Previous element in modal |

---

## Validation Rules

### Weighted Distribution
- Each input: 0 ≤ weight ≤ 100
- Total: Must equal 100% (±0.01% tolerance)
- Format: Two decimal places (e.g., 33.33)

### Manual Distribution
- Each input: ≥ 0
- Total: Must equal PPA budget allocation (±0.01 tolerance)
- Format: Philippine Peso with commas (e.g., ₱1,234,567.89)

### Equal Distribution
- No validation required
- Automatically calculates: `totalBudget / workItemCount`

---

## CSS Requirements

```css
/* Add to src/static/monitoring/css/workitem_integration.css */

/* Tree view collapsed/expanded states */
.work-item-children.collapsed {
    display: none;
}

.work-item-children.expanded {
    display: block;
}

/* Distribution method sections (hidden by default except equal) */
.distribution-method-section.hidden {
    display: none;
}

/* Optional: Smooth transitions for tree toggle */
#toggle-icon-* {
    transition: transform 200ms ease;
}
```

---

## Common Patterns

### Pattern 1: Tree Node (Recursive)

```html
<!-- partials/work_item_node.html -->
<div class="work-item-node ml-{{ depth|default:0 }}">
    <button
        onclick="toggleWorkItemChildren('{{ work_item.id }}')"
        class="flex items-center gap-2 p-2 hover:bg-gray-50 rounded-lg"
        aria-expanded="false"
    >
        <i
            id="toggle-icon-{{ work_item.id }}"
            class="fas fa-chevron-right text-gray-400 transition-transform"
            style="transform: rotate(-90deg);"
        ></i>
        <span>{{ work_item.title }}</span>
    </button>

    <div id="children-{{ work_item.id }}" class="work-item-children collapsed">
        {% for child in work_item.children.all %}
            {% include "monitoring/partials/work_item_node.html" with work_item=child depth=depth|add:1 %}
        {% endfor %}
    </div>
</div>
```

### Pattern 2: Budget Distribution Form

```html
<form
    hx-post="{% url 'monitoring:distribute_budget' ppa.id %}"
    hx-target="#work-items-tab-content"
    hx-swap="innerHTML"
>
    {% csrf_token %}

    <!-- Method selection -->
    <div class="space-y-3">
        <label>
            <input type="radio" name="distribution_method" value="equal" checked>
            Equal Distribution
        </label>
        <label>
            <input type="radio" name="distribution_method" value="weighted">
            Weighted Distribution
        </label>
        <label>
            <input type="radio" name="distribution_method" value="manual">
            Manual Distribution
        </label>
    </div>

    <!-- Equal section -->
    <div id="equal-distribution-section" class="distribution-method-section">
        <div id="equal-distribution-preview"></div>
    </div>

    <!-- Weighted section -->
    <div id="weighted-distribution-section" class="distribution-method-section hidden">
        {% for work_item in work_items %}
        <div class="flex items-center gap-3">
            <label>{{ work_item.title }}</label>
            <input type="number" class="weight-input" name="weight_{{ work_item.id }}" step="0.01">
        </div>
        {% endfor %}
        <div id="weighted-validation"></div>
    </div>

    <!-- Manual section -->
    <div id="manual-distribution-section" class="distribution-method-section hidden">
        {% for work_item in work_items %}
        <div class="flex items-center gap-3">
            <label>{{ work_item.title }}</label>
            <input type="text" class="manual-budget-input" name="manual_{{ work_item.id }}">
        </div>
        {% endfor %}
        <div id="manual-validation"></div>
    </div>

    <button id="distribute-submit" type="submit">Distribute Budget</button>
</form>
```

### Pattern 3: Modal with HTMX Content

```html
<!-- Modal container -->
<div
    id="budgetDistributionModal"
    class="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 hidden"
    aria-hidden="true"
    role="dialog"
>
    <div class="flex items-center justify-center min-h-screen p-4">
        <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full">
            <div class="p-6">
                <h2 class="text-2xl font-bold">Modal Title</h2>
                <p data-total-budget="{{ ppa.budget_allocation }}">
                    Total: {{ ppa.budget_allocation|floatformat:2 }}
                </p>
            </div>

            <!-- HTMX loads content here -->
            <div
                id="budgetDistributionModalContent"
                hx-get="{% url 'monitoring:budget_distribution_form' ppa.id %}"
                hx-trigger="revealed"
            >
                <div class="p-6">Loading...</div>
            </div>

            <div class="border-t p-6 flex justify-end gap-3">
                <button onclick="closeBudgetDistributionModal()">Cancel</button>
                <button type="submit">Save</button>
            </div>
        </div>
    </div>
</div>

<!-- Trigger button -->
<button onclick="openBudgetDistributionModal()">Open Modal</button>
```

---

## Troubleshooting

### Issue: Validation not working

**Check:**
1. Inputs have correct classes (`weight-input`, `manual-budget-input`)
2. Validation containers exist with correct IDs (`weighted-validation`, `manual-validation`)
3. Radio buttons have `name="distribution_method"`
4. Modal has `data-total-budget` attribute

### Issue: Modal won't close with Escape

**Check:**
1. Modal has `id` attribute
2. Modal contains focusable elements (button, input, etc.)
3. No JavaScript errors in console

### Issue: Tree state not persisting

**Check:**
1. Browser localStorage is enabled
2. Children containers have correct ID pattern: `children-{workItemId}`
3. Toggle icons have correct ID pattern: `toggle-icon-{workItemId}`
4. Children containers have `work-item-children` class

### Issue: HTMX events not firing

**Check:**
1. HTMX is loaded before workitem_integration.js
2. HTMX version is 1.9.10 or higher
3. Elements have correct `hx-*` attributes
4. Backend returns proper `HX-Trigger` headers

---

## Performance Tips

1. **Limit localStorage writes**: Tree state is saved on toggle, not on every page load
2. **Debounce validation**: Validation runs on `input` event, not `keyup`
3. **Disable pointer events during loading**: Prevents duplicate HTMX requests
4. **Use event delegation**: Single listener for all tree nodes via `onclick` attribute

---

## Testing Checklist

- [ ] All distribution methods validate correctly
- [ ] Tree state persists across page reloads
- [ ] Modals close with Escape key
- [ ] Tab navigation stays within modal
- [ ] Loading spinners appear during HTMX requests
- [ ] Error messages display for network failures
- [ ] Toast notifications appear for all actions
- [ ] Keyboard shortcuts work (Ctrl+E, Ctrl+C)
- [ ] Currency formatting works (Philippine Peso)
- [ ] Validation indicators update in real-time

---

## Documentation Links

- **Full Guide:** [WORKITEM_JS_INTEGRATION_GUIDE.md](./WORKITEM_JS_INTEGRATION_GUIDE.md)
- **Implementation Summary:** [docs/improvements/WORKITEM_JS_COMPLETE.md](../improvements/WORKITEM_JS_COMPLETE.md)
- **HTMX Documentation:** https://htmx.org/docs/

---

**Last Updated:** 2025-10-06
**Maintained By:** OBCMS Development Team
