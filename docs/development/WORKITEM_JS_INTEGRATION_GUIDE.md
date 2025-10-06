# WorkItem JavaScript Integration Guide

**File:** `src/static/monitoring/js/workitem_integration.js`
**Version:** 1.0.0
**Dependencies:** HTMX (required)

## Overview

This JavaScript module provides comprehensive client-side functionality for WorkItem integration, including:

- **Tree View Management**: Expandable/collapsible hierarchy with localStorage persistence
- **Budget Distribution Validation**: Real-time validation for equal, weighted, and manual distribution methods
- **Modal Management**: Focus trapping, keyboard navigation, and accessibility features
- **HTMX Event Handlers**: Loading states, error handling, and instant UI updates
- **Toast Notifications**: User feedback for actions and errors

---

## Module 1: Tree View Management

### Features

- Expand/collapse work item nodes
- LocalStorage persistence of expanded state
- Keyboard navigation (Enter/Space to toggle)
- Automatic state restoration on page load
- Keyboard shortcuts (Ctrl+E to expand all, Ctrl+C to collapse all)

### HTML Template Example

```html
<!-- Tree node with expand/collapse button -->
<div class="work-item-node">
    <button
        onclick="toggleWorkItemChildren('{{ work_item.id }}')"
        class="flex items-center gap-2 p-2 hover:bg-gray-50 rounded-lg"
        aria-expanded="false"
        aria-label="Toggle {{ work_item.title }} children"
    >
        <i
            id="toggle-icon-{{ work_item.id }}"
            class="fas fa-chevron-right text-gray-400 transition-transform duration-200"
            style="transform: rotate(-90deg);"
        ></i>
        <span class="font-medium">{{ work_item.title }}</span>
    </button>

    <!-- Children container (collapsed by default) -->
    <div
        id="children-{{ work_item.id }}"
        class="work-item-children collapsed ml-6 mt-2"
        aria-expanded="false"
    >
        {% for child in work_item.children.all %}
            <!-- Recursive child nodes -->
            {% include "monitoring/partials/work_item_node.html" with work_item=child %}
        {% endfor %}
    </div>
</div>
```

### CSS Requirements

```css
/* Add to src/static/monitoring/css/workitem_integration.css */
.work-item-children.collapsed {
    display: none;
}

.work-item-children.expanded {
    display: block;
}
```

### API Reference

#### `toggleWorkItemChildren(workItemId)`

Toggles visibility of work item children and saves state to localStorage.

**Parameters:**
- `workItemId` (string): Work item ID

**Example:**
```javascript
// Manual toggle
window.toggleWorkItemChildren('123');
```

---

## Module 2: Budget Distribution Validation

### Features

- **Equal Distribution**: Automatic per-item calculation preview
- **Weighted Distribution**: Real-time validation that weights sum to 100%
- **Manual Distribution**: Validation that allocations sum to total budget
- **Currency Formatting**: Automatic Philippine Peso formatting with commas
- **Visual Feedback**: Real-time validation indicators with color-coded messages

### HTML Template Example

```html
<!-- Budget Distribution Modal -->
<div
    id="budgetDistributionModal"
    class="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 hidden"
    aria-hidden="true"
    role="dialog"
    aria-labelledby="budgetDistributionTitle"
>
    <div class="flex items-center justify-center min-h-screen p-4">
        <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <!-- Modal Header -->
            <div class="border-b border-gray-200 p-6">
                <h2 id="budgetDistributionTitle" class="text-2xl font-bold text-gray-800">
                    Distribute Budget
                </h2>
                <p class="text-gray-600 mt-1">Total Budget: <span data-total-budget="{{ ppa.budget_allocation }}">{{ ppa.budget_allocation|floatformat:2 }}</span></p>
            </div>

            <!-- Modal Content -->
            <div id="budgetDistributionModalContent" class="p-6">
                <!-- Distribution Method Selection -->
                <div class="space-y-4 mb-6">
                    <label class="block text-sm font-medium text-gray-700">Distribution Method</label>

                    <!-- Equal Distribution -->
                    <div class="flex items-start gap-3">
                        <input
                            type="radio"
                            name="distribution_method"
                            value="equal"
                            id="equal-method"
                            checked
                            class="mt-1"
                        >
                        <label for="equal-method" class="flex-1">
                            <span class="font-medium">Equal Distribution</span>
                            <p class="text-sm text-gray-600">Divide budget equally among all work items</p>
                        </label>
                    </div>

                    <!-- Weighted Distribution -->
                    <div class="flex items-start gap-3">
                        <input
                            type="radio"
                            name="distribution_method"
                            value="weighted"
                            id="weighted-method"
                            class="mt-1"
                        >
                        <label for="weighted-method" class="flex-1">
                            <span class="font-medium">Weighted Distribution</span>
                            <p class="text-sm text-gray-600">Assign percentage weights to each work item</p>
                        </label>
                    </div>

                    <!-- Manual Distribution -->
                    <div class="flex items-start gap-3">
                        <input
                            type="radio"
                            name="distribution_method"
                            value="manual"
                            id="manual-method"
                            class="mt-1"
                        >
                        <label for="manual-method" class="flex-1">
                            <span class="font-medium">Manual Distribution</span>
                            <p class="text-sm text-gray-600">Manually specify exact amounts for each work item</p>
                        </label>
                    </div>
                </div>

                <!-- Equal Distribution Section -->
                <div id="equal-distribution-section" class="distribution-method-section">
                    <div id="equal-distribution-preview"></div>
                </div>

                <!-- Weighted Distribution Section -->
                <div id="weighted-distribution-section" class="distribution-method-section hidden">
                    <div class="space-y-3">
                        {% for work_item in work_items %}
                        <div class="flex items-center gap-3">
                            <label class="flex-1 text-sm font-medium text-gray-700">
                                {{ work_item.title }}
                            </label>
                            <div class="relative w-32">
                                <input
                                    type="number"
                                    name="weight_{{ work_item.id }}"
                                    class="weight-input block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500"
                                    placeholder="0.00"
                                    step="0.01"
                                    min="0"
                                    max="100"
                                >
                                <span class="absolute right-3 top-2 text-gray-400">%</span>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    <div id="weighted-validation" class="mt-4"></div>
                </div>

                <!-- Manual Distribution Section -->
                <div id="manual-distribution-section" class="distribution-method-section hidden">
                    <div class="space-y-3">
                        {% for work_item in work_items %}
                        <div class="flex items-center gap-3">
                            <label class="flex-1 text-sm font-medium text-gray-700">
                                {{ work_item.title }}
                            </label>
                            <div class="w-48">
                                <input
                                    type="text"
                                    name="manual_{{ work_item.id }}"
                                    class="manual-budget-input block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500"
                                    placeholder="₱0.00"
                                >
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    <div id="manual-validation" class="mt-4"></div>
                </div>
            </div>

            <!-- Modal Footer -->
            <div class="border-t border-gray-200 p-6 flex justify-end gap-3">
                <button
                    type="button"
                    onclick="closeBudgetDistributionModal()"
                    class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                    Cancel
                </button>
                <button
                    id="distribute-submit"
                    type="submit"
                    class="px-6 py-2 bg-gradient-to-r from-blue-500 to-teal-500 text-white rounded-lg hover:from-blue-600 hover:to-teal-600"
                >
                    Distribute Budget
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Trigger Button -->
<button
    onclick="openBudgetDistributionModal()"
    class="px-4 py-2 bg-gradient-to-r from-blue-500 to-teal-500 text-white rounded-lg hover:from-blue-600 hover:to-teal-600"
>
    <i class="fas fa-calculator mr-2"></i>
    Distribute Budget
</button>
```

### API Reference

#### `BudgetDistribution.init(totalBudget)`

Initialize budget distribution validator with total budget.

**Parameters:**
- `totalBudget` (number): Total budget to distribute

**Example:**
```javascript
// Initialize on modal load
const totalBudget = document.querySelector('[data-total-budget]')?.dataset.totalBudget;
BudgetDistribution.init(parseFloat(totalBudget));
```

---

## Module 3: Modal Management

### Features

- Focus trapping (prevents tabbing outside modal)
- Keyboard navigation (Tab, Shift+Tab, Escape)
- ARIA attributes for accessibility
- Body scroll lock when modal is open
- Auto-focus first interactive element

### HTML Template Example

```html
<!-- Generic Modal Structure -->
<div
    id="workItemModal"
    class="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 hidden"
    aria-hidden="true"
    role="dialog"
    aria-labelledby="workItemModalTitle"
>
    <div class="flex items-center justify-center min-h-screen p-4">
        <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full">
            <div class="border-b border-gray-200 p-6">
                <h2 id="workItemModalTitle" class="text-2xl font-bold text-gray-800">
                    Modal Title
                </h2>
            </div>

            <div class="p-6">
                <!-- Modal content -->
            </div>

            <div class="border-t border-gray-200 p-6 flex justify-end gap-3">
                <button
                    type="button"
                    onclick="ModalManager.closeModal('workItemModal')"
                    class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    class="px-6 py-2 bg-gradient-to-r from-blue-500 to-teal-500 text-white rounded-lg"
                >
                    Save
                </button>
            </div>
        </div>
    </div>
</div>
```

### API Reference

#### `ModalManager.openModal(modalId)`

Open modal with focus trapping.

**Parameters:**
- `modalId` (string): Modal element ID

**Example:**
```javascript
ModalManager.openModal('workItemModal');
```

#### `ModalManager.closeModal(modalId)`

Close modal and restore focus.

**Parameters:**
- `modalId` (string): Modal element ID

**Example:**
```javascript
ModalManager.closeModal('workItemModal');
```

---

## Module 4: HTMX Event Handlers

### Features

- Loading spinners during HTMX requests
- Automatic button disabling during form submissions
- Error handling with user-friendly messages
- Custom event handling via HX-Trigger headers
- Automatic counter and progress bar refreshing

### Backend Integration Example

```python
# views.py
from django.http import HttpResponse
import json

def distribute_budget(request, ppa_id):
    """Distribute budget to work items"""
    if request.method == 'POST':
        # ... perform distribution logic ...

        if request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        'show-toast': {
                            'message': 'Budget distributed successfully',
                            'type': 'success'
                        },
                        'refresh-counters': True,
                        'refresh-progress': True,
                        'close-modal': 'budgetDistributionModal'
                    })
                }
            )
```

### HTMX Template Example

```html
<!-- Form with HTMX -->
<form
    hx-post="{% url 'monitoring:distribute_budget' ppa.id %}"
    hx-target="#work-items-tab-content"
    hx-swap="innerHTML"
    class="space-y-6"
>
    {% csrf_token %}
    <!-- Form fields -->

    <button
        type="submit"
        class="px-6 py-2 bg-gradient-to-r from-blue-500 to-teal-500 text-white rounded-lg loading-trigger"
    >
        Distribute Budget
    </button>
</form>
```

### Supported HX-Trigger Events

| Event | Description | Payload |
|-------|-------------|---------|
| `show-toast` | Display toast notification | `{message: string, type: 'success'\|'error'\|'warning'\|'info'}` |
| `refresh-counters` | Refresh work item counters | `true` |
| `refresh-progress` | Refresh progress bars | `true` |
| `close-modal` | Close modal by ID | `string` (modal ID) |

---

## Module 5: Toast Notifications

### Features

- Automatic 3-second display with slide-in/out animations
- Color-coded by type (success, error, warning, info)
- Icon indicators
- Multiple toast support

### API Reference

#### `showToast(message, type)`

Display toast notification.

**Parameters:**
- `message` (string): Toast message
- `type` (string): Toast type - `'success'`, `'error'`, `'warning'`, or `'info'` (default: `'info'`)

**Example:**
```javascript
// Success toast
showToast('Budget distributed successfully', 'success');

// Error toast
showToast('Failed to save work item', 'error');

// Warning toast
showToast('Total weight must equal 100%', 'warning');

// Info toast
showToast('Loading work items...', 'info');
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Escape` | Close all modals |
| `Ctrl+E` | Expand all work items |
| `Ctrl+C` | Collapse all work items |
| `Enter/Space` | Toggle work item node (when focused) |
| `Tab` | Navigate forward through modal elements |
| `Shift+Tab` | Navigate backward through modal elements |

---

## Accessibility Features

### WCAG 2.1 AA Compliance

- **Focus Management**: Automatic focus on first interactive element when modal opens
- **Focus Trapping**: Tab navigation restricted to modal when open
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **ARIA Labels**: Proper `aria-hidden`, `aria-expanded`, `aria-label` attributes
- **Screen Reader Support**: Live regions for dynamic updates
- **Color Contrast**: Validation messages meet 4.5:1 contrast ratio
- **Touch Targets**: Minimum 48px touch target size

### Testing Checklist

- [ ] Navigate entire tree using keyboard only
- [ ] Open/close modals using Escape key
- [ ] Tab through all modal inputs without escaping
- [ ] Validation messages announced by screen reader
- [ ] Loading states visible and announced
- [ ] Error messages clear and actionable

---

## Performance Considerations

### LocalStorage Usage

Tree expanded state is persisted in localStorage under key `workItemExpandedState`:

```javascript
{
    "123": true,  // Work item 123 is expanded
    "456": false, // Work item 456 is collapsed
    "789": true   // Work item 789 is expanded
}
```

**Clear localStorage:**
```javascript
localStorage.removeItem('workItemExpandedState');
```

### HTMX Request Optimization

- Loading indicators prevent duplicate requests (pointer-events disabled)
- Debounced validation inputs (input event, not keyup)
- Efficient DOM targeting with IDs
- Minimal DOM manipulation

---

## Troubleshooting

### Issue: Tree state not persisting

**Solution:** Check browser localStorage quota and permissions.

```javascript
// Test localStorage
try {
    localStorage.setItem('test', 'test');
    localStorage.removeItem('test');
    console.log('LocalStorage working');
} catch (e) {
    console.error('LocalStorage not available:', e);
}
```

### Issue: Budget validation not working

**Solution:** Ensure inputs have correct classes and IDs.

```html
<!-- Weighted inputs MUST have class "weight-input" -->
<input type="number" class="weight-input" name="weight_123">

<!-- Manual inputs MUST have class "manual-budget-input" -->
<input type="text" class="manual-budget-input" name="manual_123">

<!-- Validation containers MUST have IDs -->
<div id="weighted-validation"></div>
<div id="manual-validation"></div>
```

### Issue: Modal focus trap not working

**Solution:** Ensure modal has focusable elements.

```html
<!-- At least one focusable element required -->
<button>Cancel</button>
<button>Save</button>
```

### Issue: HTMX events not firing

**Solution:** Check HTMX is loaded before workitem_integration.js.

```html
<!-- CORRECT order -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="{% static 'monitoring/js/workitem_integration.js' %}"></script>
```

---

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully supported |
| Firefox | 88+ | ✅ Fully supported |
| Safari | 14+ | ✅ Fully supported |
| Edge | 90+ | ✅ Fully supported |
| Opera | 76+ | ✅ Fully supported |

**Requires:**
- ES6+ support (const, let, arrow functions, template literals)
- LocalStorage API
- Fetch API (for HTMX)

---

## Version History

### v1.0.0 (2025-10-06)
- Initial release
- Tree view with localStorage persistence
- Budget distribution validation (equal, weighted, manual)
- Modal management with focus trapping
- Enhanced HTMX event handlers
- Toast notifications

---

## License

Internal OBCMS project - Not for redistribution
