# Quick Actions UI Template

**Status**: Active
**Last Updated**: 2025-10-02
**Category**: UI Component Standards

---

## Overview

This document defines the standard UI template for "Quick Actions" sections across the OOBC Management System. All Quick Actions must follow this template to ensure visual consistency, proper alignment, and optimal user experience.

---

## Design Principles

1. **Vertical Alignment**: Action links must always appear at the bottom of cards, regardless of description length
2. **Consistent Spacing**: Use standardized padding and margins
3. **Visual Hierarchy**: Icon → Title → Description → Action Link (top to bottom)
4. **Responsive Grid**: Adapt to screen sizes (1 col mobile → 2 cols tablet → 3-4 cols desktop)
5. **Accessibility**: Proper semantic HTML, hover states, and color contrast

---

## Standard Template

### HTML Structure

```html
<!-- Quick Actions Section -->
<section>
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        <!-- Single Quick Action Card -->
        <a href="{% url 'your:url' %}"
           class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">

            <div class="p-6 flex flex-col flex-grow">

                <!-- Icon Container (Fixed at top) -->
                <div class="w-12 h-12 bg-gradient-to-br from-{color}-500 to-{color}-600 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-{icon} text-white text-xl"></i>
                </div>

                <!-- Title (Fixed below icon) -->
                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-{color}-600 transition-colors">
                    Action Title
                </h3>

                <!-- Description (Flexible content area) -->
                <p class="mt-2 text-sm text-gray-600 flex-grow">
                    Description of what this action does. Can be 1-2 sentences.
                </p>

                <!-- Action Link (Always at bottom) -->
                <div class="mt-4 flex items-center text-{color}-600 text-sm font-medium">
                    <span>Action Text</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </div>

            </div>
        </a>

    </div>
</section>
```

---

## Key CSS Classes Breakdown

### Container Card
```html
class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col"
```

**Critical Changes:**
- ✅ **`flex flex-col`** - Makes card a flex container with vertical layout
- This allows inner content to use flex properties for bottom alignment

### Inner Wrapper
```html
class="p-6 flex flex-col flex-grow"
```

**Critical Changes:**
- ✅ **`flex flex-col`** - Makes inner wrapper flex container
- ✅ **`flex-grow`** - Allows wrapper to fill card height
- This is the key to making description + link alignment work

### Description
```html
class="mt-2 text-sm text-gray-600 flex-grow"
```

**Critical Changes:**
- ✅ **`flex-grow`** - Allows description to expand and push link to bottom
- This ensures link stays at bottom regardless of description length

### Action Link
```html
class="mt-4 flex items-center text-{color}-600 text-sm font-medium"
```

- Standard margin-top maintains consistent spacing
- Flex display for icon + text alignment
- Animated arrow on hover

---

## Grid Layout Options

### 3 Columns (Most Common)
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

Use for: Most Quick Actions sections with 3-6 items

### 4 Columns
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
```

Use for: Sections with exactly 4 items that need equal width

### 2 Columns
```html
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
```

Use for: Sections with only 2 items

---

## Color Schemes by Module

| Module | Primary Color | Icon Gradient | Hover Color |
|--------|---------------|---------------|-------------|
| **Dashboard** | Gray | `from-gray-500 to-gray-600` | `text-gray-600` |
| **Communities (OBC Data)** | Blue | `from-blue-500 to-blue-600` | `text-blue-600` |
| **MANA** | Green | `from-green-500 to-green-600` | `text-green-600` |
| **Coordination** | Purple | `from-purple-500 to-purple-600` | `text-purple-600` |
| **Recommendations** | Orange | `from-orange-500 to-orange-600` | `text-orange-600` |
| **M&E** | Violet | `from-violet-500 to-violet-600` | `text-violet-600` |
| **OOBC Management** | Emerald/Teal | `from-emerald-500 to-emerald-600` | `text-emerald-600` |

**Note:** Individual cards within a module can use different colors for visual distinction.

---

## Complete Example (4 Cards)

```html
<section>
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

        <!-- Card 1: New Item -->
        <a href="{% url 'module:new' %}"
           class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
            <div class="p-6 flex flex-col flex-grow">
                <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-plus text-white text-xl"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-orange-600 transition-colors">
                    New Item
                </h3>
                <p class="mt-2 text-sm text-gray-600 flex-grow">
                    Create a new item with a potentially longer description that spans multiple lines.
                </p>
                <div class="mt-4 flex items-center text-orange-600 text-sm font-medium">
                    <span>Create Item</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </div>
            </div>
        </a>

        <!-- Card 2: Add Evidence -->
        <a href="{% url 'module:evidence' %}"
           class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
            <div class="p-6 flex flex-col flex-grow">
                <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-chart-line text-white text-xl"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    Add Evidence
                </h3>
                <p class="mt-2 text-sm text-gray-600 flex-grow">
                    Submit supporting evidence.
                </p>
                <div class="mt-4 flex items-center text-blue-600 text-sm font-medium">
                    <span>Add Evidence</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </div>
            </div>
        </a>

        <!-- Card 3: Track Activity -->
        <a href="{% url 'module:track' %}"
           class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
            <div class="p-6 flex flex-col flex-grow">
                <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-bullhorn text-white text-xl"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-green-600 transition-colors">
                    Track Activity
                </h3>
                <p class="mt-2 text-sm text-gray-600 flex-grow">
                    Record activity.
                </p>
                <div class="mt-4 flex items-center text-green-600 text-sm font-medium">
                    <span>Track Activity</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </div>
            </div>
        </a>

        <!-- Card 4: Manage All -->
        <a href="{% url 'module:manage' %}"
           class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
            <div class="p-6 flex flex-col flex-grow">
                <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-list-alt text-white text-xl"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">
                    Manage All
                </h3>
                <p class="mt-2 text-sm text-gray-600 flex-grow">
                    View and manage all data with comprehensive filtering and sorting options.
                </p>
                <div class="mt-4 flex items-center text-purple-600 text-sm font-medium">
                    <span>Manage All</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </div>
            </div>
        </a>

    </div>
</section>
```

**Visual Result:** All four action links ("Create Item", "Add Evidence", "Track Activity", "Manage All") will align at the same vertical position at the bottom of their respective cards, regardless of description length.

---

## Common Mistakes to Avoid

### ❌ Missing `flex flex-col` on Card
```html
<!-- WRONG: Link will not align properly -->
<a href="#" class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200">
    <div class="p-6">
        <!-- Content -->
    </div>
</a>
```

### ✅ Correct with Flex
```html
<!-- CORRECT: Enables flex alignment -->
<a href="#" class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
    <div class="p-6 flex flex-col flex-grow">
        <!-- Content -->
    </div>
</a>
```

### ❌ Missing `flex-grow` on Description
```html
<!-- WRONG: Description won't push link down -->
<p class="mt-2 text-sm text-gray-600">
    Description text.
</p>
```

### ✅ Correct with flex-grow
```html
<!-- CORRECT: Description expands to fill space -->
<p class="mt-2 text-sm text-gray-600 flex-grow">
    Description text.
</p>
```

---

## Accessibility Requirements

1. **Semantic HTML**: Use `<a>` for clickable cards, not `<div>` with onclick
2. **Keyboard Navigation**: Cards must be focusable and keyboard-accessible
3. **Screen Readers**: Ensure title and description provide context
4. **Color Contrast**: Maintain WCAG 2.1 AA standards (4.5:1 for text)
5. **Focus States**: Visible focus indicators for keyboard users

---

## Responsive Behavior

### Mobile (< 768px)
- **Grid**: `grid-cols-1` - Single column, stacked cards
- **Spacing**: Full `gap-6` maintained
- **Touch Targets**: Minimum 48px height for touch

### Tablet (768px - 1023px)
- **Grid**: `md:grid-cols-2` - Two columns
- **Layout**: Side-by-side cards
- **Spacing**: Consistent `gap-6`

### Desktop (≥ 1024px)
- **Grid**: `lg:grid-cols-3` or `lg:grid-cols-4`
- **Layout**: 3-4 columns depending on content
- **Hover**: Full hover effects active

---

## Testing Checklist

Before deploying Quick Actions:

- [ ] All cards in a section have equal height
- [ ] Action links align at the same vertical position
- [ ] Cards with short descriptions look good (no excessive whitespace)
- [ ] Cards with long descriptions look good (text wraps properly)
- [ ] Hover effects work correctly (color change, arrow animation)
- [ ] Responsive breakpoints work (1 → 2 → 3/4 columns)
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Screen reader announces card purpose
- [ ] Touch targets are adequate on mobile
- [ ] Colors match module theme

---

## Implementation Guide

### Step 1: Add Flex Classes to Card
```diff
- <a href="#" class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200">
+ <a href="#" class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
```

### Step 2: Add Flex Classes to Inner Wrapper
```diff
- <div class="p-6">
+ <div class="p-6 flex flex-col flex-grow">
```

### Step 3: Add flex-grow to Description
```diff
- <p class="mt-2 text-sm text-gray-600">
+ <p class="mt-2 text-sm text-gray-600 flex-grow">
```

### Step 4: Keep Action Link Standard
```html
<!-- No changes needed to action link structure -->
<div class="mt-4 flex items-center text-{color}-600 text-sm font-medium">
    <span>Action Text</span>
    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
</div>
```

---

## Files to Update

When implementing this template, update Quick Actions in:

1. **Dashboard**: `src/templates/common/dashboard.html`
2. **Communities**: `src/templates/communities/communities_home.html`
3. **MANA**: `src/templates/mana/mana_home.html`
4. **Coordination**: `src/templates/coordination/coordination_home.html`
5. **Recommendations**: `src/templates/recommendations/recommendations_home.html`
6. **M&E**: `src/templates/monitoring/dashboard.html`
7. **M&E MOA/PPAs**: `src/templates/monitoring/moa_ppas_dashboard.html`
8. **M&E Initiatives**: `src/templates/monitoring/oobc_initiatives_dashboard.html`
9. **M&E Requests**: `src/templates/monitoring/obc_requests_dashboard.html`
10. **OOBC Management**: `src/templates/common/oobc_staff_management.html`

---

## Maintenance

- Review Quick Actions quarterly for consistency
- Update this template when design patterns evolve
- Document any new variations or edge cases
- Ensure new modules follow this template from start

---

## Related Documentation

- [System Modules Template](../ui/SYSTEM_MODULES_TEMPLATE.md) (if exists)
- [UI Component Standards](../../development/README.md#ui-standards)
- [Tailwind CSS Guidelines](../../development/README.md#tailwind-css)
- [Accessibility Guidelines](../../development/ACCESSIBILITY.md) (if exists)

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-02 | 1.0 | Initial template creation with flex-based bottom alignment |
