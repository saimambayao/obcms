# Budget System UI Components - Quick Reference

**Status:** ✅ Complete
**Date:** October 13, 2025

---

## 📁 File Locations

```
src/templates/
├── budget_execution/
│   ├── budget_dashboard.html           # Main dashboard with charts
│   ├── allotment_release.html          # Quarterly allotment form
│   ├── obligation_form.html            # Obligation recording (PO, Contract)
│   └── disbursement_form.html          # Payment recording
├── budget_preparation/
│   ├── budget_proposal_form.html       # Annual budget proposal
│   └── partials/
│       └── program_budget_item.html    # Dynamic program budget row
└── static/budget/js/
    └── budget_charts.js                # Chart.js integration
```

---

## 🎨 Stat Card Template (3D Milk White)

```html
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
     style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
    <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>

    <div class="relative p-6 flex flex-col h-full">
        <div class="flex items-center justify-between mb-3">
            <div>
                <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">METRIC NAME</p>
                <p class="text-4xl font-extrabold text-gray-800 mt-1">VALUE</p>
            </div>
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                 style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                <i class="fas fa-ICON text-2xl text-COLOR"></i>
            </div>
        </div>

        <!-- SPACER for bottom alignment -->
        <div class="flex-grow"></div>

        <!-- Breakdown (always at bottom) -->
        <div class="pt-3 border-t border-gray-200/60 mt-auto">
            <div class="text-center">
                <p class="text-xl font-bold text-gray-700">PERCENTAGE%</p>
                <p class="text-xs text-gray-500 font-medium">Label</p>
            </div>
        </div>
    </div>
</div>
```

**Icon Colors:**
- Amber (`text-amber-600`): Total/General
- Blue (`text-blue-600`): Process/Info
- Purple (`text-purple-600`): Draft/Proposed
- Emerald (`text-emerald-600`): Success/Complete

---

## 📊 Chart.js Integration

### Initialize Quarterly Chart
```javascript
const quarterlyData = {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
        {
            label: 'Allotted',
            data: [20, 25, 20, 15],
            backgroundColor: 'rgba(37, 99, 235, 0.8)', // blue-600
        },
        {
            label: 'Obligated',
            data: [15, 20, 15, 10],
            backgroundColor: 'rgba(249, 115, 22, 0.8)', // orange-500
        },
        {
            label: 'Disbursed',
            data: [10, 15, 12, 8],
            backgroundColor: 'rgba(5, 150, 105, 0.8)', // emerald-600
        }
    ]
};

initQuarterlyChart('quarterlyExecutionChart', quarterlyData);
```

---

## 📝 Standard Dropdown (OBCMS Style)

```html
<div class="space-y-1">
    <label for="field-id" class="block text-sm font-medium text-gray-700 mb-2">
        Field Label<span class="text-red-500">*</span>
    </label>
    <div class="relative">
        <select id="field-id"
                name="field_name"
                class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200"
                required>
            <option value="">Select...</option>
            <option value="1">Option 1</option>
        </select>
        <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
            <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
        </span>
    </div>
</div>
```

---

## 💰 Currency Input (Philippine Peso)

```html
<div class="space-y-1">
    <label for="amount" class="block text-sm font-medium text-gray-700 mb-2">
        Amount<span class="text-red-500">*</span>
    </label>
    <div class="relative">
        <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₱</span>
        <input type="number"
               id="amount"
               name="amount"
               step="0.01"
               min="0.01"
               class="w-full pl-8 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]"
               placeholder="0.00"
               required>
    </div>
</div>
```

---

## ⚡ HTMX Patterns

### 1. Add Program Budget (Instant UI)
```html
<button type="button"
        hx-get="{% url 'budget_preparation:add_program_budget' %}"
        hx-target="#program-budgets"
        hx-swap="beforeend"
        class="bg-gradient-to-r from-blue-600 to-emerald-600 text-white px-4 py-2 rounded-xl">
    <i class="fas fa-plus mr-2"></i>Add Program
</button>
```

### 2. Load Budget Details
```html
<select hx-get="{% url 'budget_execution:get_budget_details' %}"
        hx-target="#budget-details"
        hx-trigger="change">
    <option value="">Select program budget...</option>
</select>

<div id="budget-details">
    <!-- HTMX loads content here -->
</div>
```

### 3. Real-Time Calculation
```javascript
document.addEventListener('input', function(e) {
    if (e.target.name && e.target.name.includes('requested_amount')) {
        calculateTotal();
    }
});

function calculateTotal() {
    let total = 0;
    const inputs = document.querySelectorAll('input[name*="requested_amount"]');
    inputs.forEach(input => {
        total += parseFloat(input.value) || 0;
    });

    document.getElementById('total-proposed').textContent =
        '₱' + total.toLocaleString('en-PH', { minimumFractionDigits: 2 });
}
```

---

## 📋 Table Template (Blue-to-Teal Header)

```html
<div class="bg-white shadow-md rounded-xl overflow-hidden border border-gray-200">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-blue-600 to-emerald-600">
            <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                    Column 1
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                    Column 2
                </th>
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            <tr class="hover:bg-gray-50 transition-colors duration-200">
                <td class="px-6 py-4 whitespace-nowrap">Content</td>
                <td class="px-6 py-4 whitespace-nowrap">Content</td>
            </tr>
        </tbody>
    </table>
</div>
```

---

## 🎯 Progress Bar (Emerald)

```html
<div class="flex items-center">
    <span class="text-sm font-medium text-gray-700 mr-3">75%</span>
    <div class="flex-1 bg-gray-200 rounded-full h-2.5 max-w-xs">
        <div class="bg-emerald-600 h-2.5 rounded-full transition-all duration-300"
             style="width: 75%"></div>
    </div>
</div>
```

---

## ✅ Validation Alert

```html
<div class="bg-amber-50 border-l-4 border-amber-400 rounded-r-lg p-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-exclamation-triangle text-amber-400 text-xl"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-amber-800">Validation Warning</h3>
            <div class="mt-2 text-sm text-amber-700">
                <p>Amount exceeds available balance.</p>
            </div>
        </div>
    </div>
</div>
```

---

## 🔘 Button Styles

### Primary (Gradient)
```html
<button class="bg-gradient-to-r from-blue-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
    <i class="fas fa-save mr-2"></i>
    Save Changes
</button>
```

### Secondary (Outline)
```html
<button class="border-2 border-gray-300 text-gray-700 px-6 py-3 rounded-xl hover:bg-gray-50 transition-colors duration-200">
    <i class="fas fa-times mr-2"></i>
    Cancel
</button>
```

---

## 🎨 Color Reference

| Color | Tailwind Class | Hex | Usage |
|-------|---------------|-----|-------|
| **Blue** | `blue-600` | `#2563eb` | Info, Process |
| **Emerald** | `emerald-600` | `#059669` | Success, Complete |
| **Amber** | `amber-600` | `#d97706` | Total, General |
| **Purple** | `purple-600` | `#7c3aed` | Draft, Proposed |
| **Orange** | `orange-500` | `#f97316` | Warning |
| **Red** | `red-600` | `#dc2626` | Critical, Error |

---

## 📱 Responsive Grid

```html
<!-- 4-Column Grid (Most Common) -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- 4 stat cards -->
</div>

<!-- 2-Column Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Form fields -->
</div>
```

---

## ♿ Accessibility Checklist

- [x] Touch targets minimum 48x48px
- [x] Color contrast > 4.5:1 (normal text)
- [x] Keyboard navigation (Tab, Enter, Space)
- [x] Focus indicators (emerald ring)
- [x] ARIA labels for icons
- [x] Required field indicators (`*`)
- [x] Error messages associated with inputs
- [x] Screen reader compatible

---

## 🔗 URL Routes (Backend Required)

```python
# Budget Preparation
/budget/proposals/                      # List proposals
/budget/proposals/create/               # Create proposal form
/budget/proposals/<id>/edit/            # Edit proposal form

# Budget Execution
/budget/execution/dashboard/            # Main dashboard
/budget/execution/allotment/release/    # Allotment release form
/budget/execution/obligation/record/    # Obligation form
/budget/execution/disbursement/record/  # Disbursement form

# HTMX Partials
/budget/preparation/add-program-budget/ # Program budget partial
/budget/execution/budget-details/<id>/  # Budget details partial
/budget/execution/allotment-balance/<id>/ # Balance partial
```

---

## 📦 Dependencies

```html
<!-- Chart.js (via CDN) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<!-- HTMX (via CDN) -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>

<!-- Budget Charts (Local) -->
<script src="{% static 'budget/js/budget_charts.js' %}"></script>
```

---

## 🚀 Quick Start

1. **Copy template structure**
2. **Add to Django views**
3. **Configure URL routes**
4. **Test with sample data**
5. **Implement backend API**
6. **Deploy to staging**

---

**Last Updated:** October 13, 2025
**Status:** ✅ Ready for Integration
