# WorkItem Detail View - Visual Guide

**Date:** 2025-10-06
**Component:** Work Item Detail Page
**Template:** `src/templates/work_items/work_item_detail.html`

---

## Visual Layout Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🏠 Home > Work Items > Parent Item > Current Item                  │ ← Breadcrumb
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 📋 Work Item Title          [Active Badge]          [Edit] [Delete]│ ← Header
│ Project Task                                                        │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ LEFT COLUMN (2/3)                    │  RIGHT COLUMN (1/3)         │
│ ┌───────────────────────────────┐    │  ┌──────────────────────┐  │
│ │ ℹ️ Basic Information          │    │  │ 📅 Schedule & Timeline │  │
│ │                               │    │  │                      │  │
│ │ Description text...           │    │  │ Start: Mar 1, 2025  │  │
│ │                               │    │  │ Due: Apr 30, 2025   │  │
│ └───────────────────────────────┘    │  └──────────────────────┘  │
│                                      │                             │
│ ┌───────────────────────────────┐    │  ┌──────────────────────┐  │
│ │ ⚙️ Type-specific Data         │    │  │ 📊 Status & Progress  │  │
│ │                               │    │  │                      │  │
│ │ Key: Value                    │    │  │ Status: [Active]    │  │
│ │ Key: Value                    │    │  │ Priority: [High]    │  │
│ └───────────────────────────────┘    │  │ Progress: ▓▓▓▓░░ 75%│  │
│                                      │  └──────────────────────┘  │
│ ┌───────────────────────────────┐    │                             │
│ │ 🗂️ Sub-Items (3)              │    │  ┌──────────────────────┐  │
│ │                               │    │  │ 👥 Assignment         │  │
│ │ ╔═══════════════════════════╗ │    │  │                      │  │
│ │ ║ Title │ Type │ Status ║    │    │  │ • John Doe          │  │
│ │ ╠═══════════════════════════╣ │    │  │ • Jane Smith        │  │
│ │ ║ Sub 1 │ Task │ Active ║    │    │  └──────────────────────┘  │
│ │ ║ Sub 2 │ Task │ Pending║    │    │                             │
│ │ ╚═══════════════════════════╝ │    │  ┌──────────────────────┐  │
│ └───────────────────────────────┘    │  │ 💾 Metadata           │  │
│                                      │  │                      │  │
│                                      │  │ Created: Mar 1      │  │
│                                      │  │ Updated: Mar 15     │  │
│                                      │  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Breadcrumb Navigation

**Visual:**
```
🏠 > Work Items > Parent Task > Current Task
```

**Styling:**
- Blue links with hover effect
- Chevron-right separators (gray-400)
- Current page in bold (gray-700)
- Small text (text-sm)

**Code:**
```html
<nav aria-label="Breadcrumb">
    <ol class="flex items-center space-x-2 text-sm">
        <li><a href="..." class="text-blue-600 hover:text-blue-800"><i class="fas fa-home"></i></a></li>
        <li><i class="fas fa-chevron-right text-gray-400 mx-2 text-xs"></i></li>
        <li><a href="..." class="text-blue-600 hover:text-blue-800">Work Items</a></li>
        <!-- More items -->
    </ol>
</nav>
```

---

### 2. Page Header

**Visual:**
```
📋 Implement User Dashboard          [✓ Active]          [✏️ Edit] [🗑️ Delete]
Project Task
```

**Styling:**
- H1: 3xl, bold, gray-900
- Icon: Blue-600 (fa-tasks)
- Status badge: Rounded-full, emerald/amber/blue background
- Buttons: Gradient primary, outline secondary

**Badge Colors:**
- Active: Emerald (bg-emerald-100, text-emerald-800)
- Pending: Amber (bg-amber-100, text-amber-800)
- Completed: Blue (bg-blue-100, text-blue-800)

---

### 3. Section Cards

#### Basic Structure
```
┌────────────────────────────────────┐
│ ℹ️ Section Title                   │ ← Icon + Title
├────────────────────────────────────┤
│                                    │
│ Content goes here...               │
│                                    │
└────────────────────────────────────┘
```

**Styling:**
- Background: White (bg-white)
- Border: Light gray (border-gray-200)
- Rounded: xl (rounded-xl)
- Padding: 6 (p-6)
- Shadow: None (flat design)

**Icon Colors by Section:**
```
ℹ️ Basic Information    → Blue (text-blue-500)
⚙️ Type-specific Data   → Purple (text-purple-500)
🗂️ Sub-Items           → Emerald (text-emerald-500)
📅 Schedule & Timeline  → Purple (text-purple-500)
📊 Status & Progress    → Blue (text-blue-500)
👥 Assignment           → Amber (text-amber-500)
💾 Metadata             → Gray (text-gray-500)
```

---

### 4. Status Badges

**Visual Examples:**
```
[✓ Active]     ← Emerald green
[🕐 Pending]   ← Amber yellow
[✓✓ Completed] ← Blue
```

**Code Pattern:**
```html
<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-emerald-100 text-emerald-800">
    <i class="fas fa-check-circle mr-1"></i>
    Active
</span>
```

**Color Mapping:**
| Status | Background | Text | Icon |
|--------|-----------|------|------|
| Active | emerald-100 | emerald-800 | fa-check-circle |
| Pending | amber-100 | amber-800 | fa-clock |
| Completed | blue-100 | blue-800 | fa-check-double |

---

### 5. Priority Badges

**Visual Examples:**
```
[❗ Critical]  ← Red
[⬆️ High]      ← Orange
[➖ Medium]    ← Amber
[⬇️ Low]       ← Gray
```

**Color Mapping:**
| Priority | Background | Text | Icon |
|----------|-----------|------|------|
| Critical | red-100 | red-800 | fa-exclamation-circle |
| High | orange-100 | orange-800 | fa-arrow-up |
| Medium | amber-100 | amber-800 | fa-minus |
| Low | gray-100 | gray-800 | fa-arrow-down |

---

### 6. Progress Bar

**Visual:**
```
Completion                          75%
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░
```

**Styling:**
- Container: Gray-200 background, rounded-full, h-2.5
- Bar: Emerald-600, smooth transition
- Label: Small text above bar

**Code:**
```html
<div class="flex justify-between text-sm text-gray-600 mb-1">
    <span class="font-medium">Completion</span>
    <span>75%</span>
</div>
<div class="w-full bg-gray-200 rounded-full h-2.5">
    <div class="bg-emerald-600 h-2.5 rounded-full transition-all duration-300"
         style="width: 75%"></div>
</div>
```

---

### 7. Children Table

**Visual:**
```
╔══════════════════════════════════════════════════════════╗
║ Title              │ Type  │ Status    │ Progress       ║ ← Gradient header
╠══════════════════════════════════════════════════════════╣
║ Setup Database     │ Task  │ [Active]  │ 100% ▓▓▓▓▓    ║
║ API Integration    │ Task  │ [Pending] │  50% ▓▓▓░░    ║
║ UI Implementation  │ Task  │ [Active]  │  25% ▓░░░░    ║
╚══════════════════════════════════════════════════════════╝
```

**Styling:**
- Header: Gradient (from-blue-600 to-emerald-600)
- Header text: White, uppercase, semibold, xs
- Rows: Hover effect (hover:bg-gray-50)
- Borders: Gray-200 dividers

---

### 8. Action Buttons

**Primary Button (Edit):**
```
┌──────────────┐
│ ✏️ Edit      │ ← Gradient blue-to-emerald
└──────────────┘
```

**Secondary Button (Delete):**
```
┌──────────────┐
│ 🗑️ Delete    │ ← Red outline
└──────────────┘
```

**Code:**
```html
<!-- Primary -->
<a class="bg-gradient-to-r from-blue-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:-translate-y-1">
    <i class="fas fa-edit mr-2"></i>
    Edit
</a>

<!-- Secondary -->
<a class="border-2 border-red-300 text-red-700 px-6 py-3 rounded-xl font-semibold hover:bg-red-50">
    <i class="fas fa-trash mr-2"></i>
    Delete
</a>
```

---

## Responsive Breakpoints

### Mobile (< 1024px)
```
┌─────────────────────┐
│ Breadcrumb          │
├─────────────────────┤
│ Header + Badges     │
│ [Edit] [Delete]     │
├─────────────────────┤
│ Basic Information   │ ← Full width
├─────────────────────┤
│ Type-specific Data  │
├─────────────────────┤
│ Sub-Items           │
├─────────────────────┤
│ Schedule & Timeline │
├─────────────────────┤
│ Status & Progress   │
├─────────────────────┤
│ Assignment          │
├─────────────────────┤
│ Metadata            │
└─────────────────────┘
```

### Desktop (>= 1024px)
```
┌─────────────────────────────────────────────┐
│ Breadcrumb                                  │
├─────────────────────────────────────────────┤
│ Header + Badges              [Edit] [Delete]│
├───────────────────────────┬─────────────────┤
│ Basic Information (2/3)   │ Schedule (1/3)  │
├───────────────────────────┼─────────────────┤
│ Type-specific Data        │ Status          │
├───────────────────────────┼─────────────────┤
│ Sub-Items                 │ Assignment      │
│                           ├─────────────────┤
│                           │ Metadata        │
└───────────────────────────┴─────────────────┘
```

---

## Color Palette Reference

### Primary Colors
- **Blue-600:** `#2563eb` - Primary actions, icons
- **Emerald-600:** `#059669` - Success, progress
- **Amber-600:** `#d97706` - Warnings, pending

### Semantic Status Colors
```
Active:    bg-emerald-100 (#d1fae5) + text-emerald-800 (#065f46)
Pending:   bg-amber-100 (#fef3c7)   + text-amber-800 (#92400e)
Completed: bg-blue-100 (#dbeafe)    + text-blue-800 (#1e40af)
```

### Semantic Priority Colors
```
Critical:  bg-red-100 (#fee2e2)     + text-red-800 (#991b1b)
High:      bg-orange-100 (#ffedd5)  + text-orange-800 (#9a3412)
Medium:    bg-amber-100 (#fef3c7)   + text-amber-800 (#92400e)
Low:       bg-gray-100 (#f3f4f6)    + text-gray-800 (#1f2937)
```

### Background Colors
```
Card Background:  bg-white (#ffffff)
Card Border:      border-gray-200 (#e5e7eb)
Page Background:  Default (inherited from base)
```

---

## Accessibility Features

### Visual Indicators
- **Focus rings:** Emerald-500 with 2px offset
- **Hover states:** Consistent across all interactive elements
- **Loading states:** Spinner with descriptive text

### Screen Reader Support
- **Breadcrumb:** `aria-label="Breadcrumb"`
- **Sections:** Semantic `<section>` elements
- **Icons:** Conveyed through adjacent text
- **Status:** Clearly labeled with text, not just color

### Keyboard Navigation
```
Tab       → Next interactive element
Shift+Tab → Previous interactive element
Enter     → Activate link/button
```

---

## Empty State Patterns

### No Assignees
```
┌─────────────────────────────────┐
│ 👥 Assignment                   │
├─────────────────────────────────┤
│ [🚫 Not assigned]               │ ← Gray badge
└─────────────────────────────────┘
```

### No Dates
```
┌─────────────────────────────────┐
│ 📅 Schedule & Timeline          │
├─────────────────────────────────┤
│ No dates specified              │ ← Italic gray text
└─────────────────────────────────┘
```

---

## Implementation Checklist

### Visual Elements
- [x] Breadcrumb navigation with chevrons
- [x] Page header with status badge
- [x] Section cards with icon headers
- [x] Status badges with semantic colors
- [x] Priority badges with semantic colors
- [x] Progress bar with percentage
- [x] Children table with gradient header
- [x] Action buttons (Edit/Delete)

### Responsive Design
- [x] Mobile: Single column layout
- [x] Desktop: 2/3 + 1/3 grid
- [x] Flexible header with wrap
- [x] Scrollable table on small screens

### Accessibility
- [x] Semantic HTML (nav, section, table)
- [x] ARIA labels where needed
- [x] Keyboard navigation support
- [x] Color contrast WCAG AA
- [x] Touch targets 48px+

---

## Reference Screenshots

**Note:** Actual screenshots would be added here during implementation testing.

### Desktop View
- Full-width layout with sidebar
- All sections visible without scrolling
- Hover effects on interactive elements

### Mobile View
- Stacked single-column layout
- Collapsed sections for easy scanning
- Touch-friendly button sizes

---

## Related Components

- **[WorkItem List View](work_item_list.html)** - Overview table
- **[WorkItem Form](work_item_form.html)** - Create/Edit form
- **[WorkItem Delete Confirm](work_item_delete_confirm.html)** - Deletion confirmation

---

**Last Updated:** 2025-10-06
**Status:** ✅ Visual Guide Complete
