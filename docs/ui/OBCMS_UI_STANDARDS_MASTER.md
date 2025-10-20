# OBCMS UI Standards Master Guide

**Version:** 3.1
**Last Updated:** 2025-10-12
**Status:** ✅ Official Standard | Master Reference
**Note:** Consolidated from 69+ UI documentation files - Single source of truth for all OBCMS UI/UX

---

## 📋 Quick Navigation

- [Overview](#overview)
- [Design Principles](#design-principles)
- [Color Palette](#color-palette)
- [Typography](#typography)
- [Component Library](#component-library)
  - [Stat Cards (3D Milk White)](#stat-cards-3d-milk-white)
  - [Quick Action Components](#quick-action-components)
  - [Forms & Input Components](#forms--input-components)
  - [Buttons](#buttons)
  - [Cards & Containers](#cards--containers)
  - [Modal & Dialogs](#modal--dialogs)
  - [Navigation Components](#navigation-components)
  - [Alerts & Messages](#alerts--messages)
  - [Tables & Data Display](#tables--data-display)
  - [Calendar Components](#calendar-components)
  - [Status Indicators](#status-indicators)
- [Patterns & Best Practices](#patterns--best-practices)
- [HTMX & Instant UI](#htmx--instant-ui)
- [Accessibility Guidelines](#accessibility-guidelines)
- [Reference Implementations](#reference-implementations)
- [For AI Coding Agents](#for-ai-coding-agents)

---

## Overview

This document provides the official UI component library and design standards for the **Office for Other Bangsamoro Communities (OOBC) Management System**. All components follow WCAG 2.1 AA accessibility standards and maintain a consistent, government-appropriate aesthetic.

### Purpose

- **Consistency**: Unified visual language across all modules
- **Accessibility**: WCAG 2.1 AA compliant components
- **Efficiency**: Ready-to-use, copy-paste components
- **Maintainability**: Centralized design standards

### Usage

1. Copy the HTML/CSS code for the component you need
2. Customize classes and content as needed
3. Test across different screen sizes
4. Verify accessibility compliance

---

## Design Principles

### 1. Cultural Respect

Colors and design elements honor Bangsamoro heritage while maintaining professional government standards.

- 🌊 **Blue-to-Teal Waters**: Blue-800 to Emerald-600 gradient representing the seas surrounding Mindanao
- 🌾 **Golden Harvests**: Symbolizing agricultural prosperity and hope
- 🌿 **Verdant Landscapes**: The lush forests and natural resources
- 🏛️ **Government Professionalism**: Trust, stability, and transparency

### 2. Professional Aesthetics

Clean, modern interface suitable for government operations with 3D embossed effects where appropriate.

### 3. Accessibility First

- **High contrast ratios**: WCAG 2.1 AA (4.5:1 minimum for normal text)
- **Keyboard navigation**: Logical tab order, clear focus indicators
- **Screen reader compatible**: Semantic HTML, proper ARIA labels
- **Touch-friendly**: Minimum 48x48px targets, adequate spacing

### 4. Mobile-First Responsive

All components adapt gracefully from mobile (320px) to desktop (1920px+).

### 5. Consistent Spacing

**Standard spacing scale:** 4px, 8px, 16px, 24px, 32px, 48px

### 6. Instant UI & Smooth Interactions

- **No full page reloads**: Use HTMX for all CRUD operations
- **Optimistic updates**: Update UI immediately, handle response asynchronously
- **Smooth animations**: 300ms transitions for all state changes
- **Graceful error handling**: Clear feedback with recovery options

---

## Color Palette

### Primary Colors (Bangsamoro Brand) ⭐

**OFFICIAL PRIMARY GRADIENT** - Use for navbars, hero sections, tabs, primary buttons:

```css
/* Blue-to-Teal Gradient (Bangsamoro Brand) */
--primary-blue: #1e40af;         /* Blue-800 (Bangsamoro Brand) */
--primary-teal: #059669;         /* Emerald-600 */
--primary-gradient: linear-gradient(135deg, #1e40af 0%, #059669 100%);
```

**Color Notes:**
- **Blue-800 (`#1e40af`)**: Primary brand color, confirmed from navbar screenshot
- **Emerald-600 (`#059669`)**: Secondary brand color, complements blue perfectly
- **Gradient**: Always use 135-degree diagonal from blue to emerald for brand consistency

**Usage:**

- **Navigation bars**: Top navbar, sidebar headers
- **Hero sections**: Dashboard hero, landing page banners
- **Primary buttons**: Main action buttons (when on white background)
- **Tab active states**: Active tab indicators
- **Progress indicators**: Loading bars, completion status
- **Section headers**: Gradient headers for data tables

**Examples:**

```html
<!-- Navbar (Blue-to-Teal Gradient) -->
<nav class="bg-gradient-to-r from-blue-800 to-emerald-600">
  <!-- Navigation items -->
</nav>

<!-- Hero Section (Blue-to-Teal Gradient) -->
<div class="bg-gradient-to-br from-blue-800 via-teal-600 to-emerald-600">
  <h1 class="text-white">OOBC Management System</h1>
</div>

<!-- Primary Button (Blue-to-Teal Gradient) -->
<button class="bg-gradient-to-r from-blue-800 to-emerald-600 text-white">
  Save Changes
</button>

<!-- Active Tab (Blue-800 border with gradient background) -->
<div class="border-b-4 border-blue-800 bg-gradient-to-r from-blue-50 to-emerald-50">
  Active Tab
</div>
```

**When to Use Gradient vs Solid Colors:**

- ✅ **Use gradient**: Navigation, hero, primary actions, table headers, active states
- ⚠️ **Use solid colors**: Icons, semantic status indicators, secondary elements

### 3D Milk White (Stat Cards)

```css
/* Milk White Palette */
--milk-white-light: #FEFDFB;  /* Gradient start */
--milk-white-dark: #FBF9F5;   /* Gradient end */
--milk-white-icon: #F5F3F0;   /* Icon container */
```

### Semantic Colors

```css
/* Total/General */
--semantic-amber: #d97706;     /* text-amber-600 */

/* Success/Completed */
--semantic-emerald: #059669;   /* text-emerald-600 */

/* Info/Process */
--semantic-blue: #2563eb;      /* text-blue-600 */

/* Draft/Proposed */
--semantic-purple: #7c3aed;    /* text-purple-600 */

/* Warning */
--semantic-orange: #ea580c;    /* text-orange-600 */

/* Critical */
--semantic-red: #dc2626;       /* text-red-600 */
```

### Neutral Colors

```css
/* Gray Scale */
--neutral-50: #f9fafb;
--neutral-100: #f3f4f6;
--neutral-200: #e5e7eb;
--neutral-300: #d1d5db;
--neutral-400: #9ca3af;
--neutral-500: #6b7280;
--neutral-600: #4b5563;
--neutral-700: #374151;
--neutral-800: #1f2937;
--neutral-900: #111827;
```

---

## Typography

### Font Stack

```css
font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
```

### Heading Styles

```html
<!-- H1 - Page Titles -->
<h1 class="text-3xl font-bold text-gray-900 mb-6">Page Title</h1>

<!-- H2 - Section Headers -->
<h2 class="text-2xl font-semibold text-gray-800 mb-4">Section Header</h2>

<!-- H3 - Subsection Headers -->
<h3 class="text-xl font-medium text-gray-700 mb-3">Subsection</h3>

<!-- H4 - Component Titles -->
<h4 class="text-lg font-semibold text-gray-700 mb-2">Component Title</h4>
```

### Text Sizes

| Class | Size | Usage |
|-------|------|-------|
| `text-xs` | 12px | Small labels, captions |
| `text-sm` | 14px | Labels, secondary text |
| `text-base` | 16px | Body text, inputs |
| `text-lg` | 18px | Emphasized text |
| `text-xl` | 20px | Breakdown numbers |
| `text-2xl` | 24px | Large metrics |
| `text-3xl` | 30px | Page titles |
| `text-4xl` | 36px | Stat card numbers |

---

## Component Library

This section contains all official OBCMS UI components with complete code examples.

---

## Stat Cards (3D Milk White)

### Official Design Standard ⭐

The **3D Milk White Stat Card** is the official design for all statistical metrics across OBCMS.

**Reference:** [STATCARD_TEMPLATE.md](../improvements/UI/STATCARD_TEMPLATE.md)

### Simple Stat Card (No Breakdown)

```html
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
     style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
    <!-- Gradient overlay for depth -->
    <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>

    <!-- Content -->
    <div class="relative p-6">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Total Communities</p>
                <p class="text-4xl font-extrabold text-gray-800 mt-1">42</p>
            </div>
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                 style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                <i class="fas fa-home text-2xl text-amber-600"></i>
            </div>
        </div>
    </div>
</div>
```

### Stat Card with 3-Column Breakdown

```html
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
     style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
    <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>

    <!-- Content - CRITICAL: Use flex column for bottom alignment -->
    <div class="relative p-6 flex flex-col h-full">
        <!-- Header -->
        <div class="flex items-center justify-between mb-3">
            <div>
                <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Total Recommendations</p>
                <p class="text-4xl font-extrabold text-gray-800 mt-1">156</p>
            </div>
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                 style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                <i class="fas fa-lightbulb text-2xl text-amber-600"></i>
            </div>
        </div>

        <!-- Spacer to push breakdown to bottom -->
        <div class="flex-grow"></div>

        <!-- Breakdown (Always at bottom) -->
        <div class="grid grid-cols-3 gap-2 pt-3 border-t border-gray-200/60 mt-auto">
            <div class="text-center">
                <p class="text-xl font-bold text-gray-700">42</p>
                <p class="text-xs text-gray-500 font-medium">Policies</p>
            </div>
            <div class="text-center">
                <p class="text-xl font-bold text-gray-700">87</p>
                <p class="text-xs text-gray-500 font-medium">Programs</p>
            </div>
            <div class="text-center">
                <p class="text-xl font-bold text-gray-700">27</p>
                <p class="text-xs text-gray-500 font-medium">Services</p>
            </div>
        </div>
    </div>
</div>
```

### Semantic Icon Colors

| Metric Type | Icon Color | Usage |
|-------------|-----------|--------|
| **Total/Overall** | `text-amber-600` | Total counts, general stats |
| **Success/Complete** | `text-emerald-600` | Completed, implemented, active |
| **Info/Process** | `text-blue-600` | Submitted, in-progress, pending |
| **Draft/Proposed** | `text-purple-600` | Proposed, draft, planned |
| **Warning** | `text-orange-600` | Needs attention, delayed |
| **Critical** | `text-red-600` | Overdue, critical, blocked |

### Grid Layout

```html
<!-- 4-Column Grid (Most Common) -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <!-- 4 stat cards -->
</div>

<!-- 3-Column Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
    <!-- 3 stat cards -->
</div>
```

### Critical: Bottom Alignment

**Why:** When cards have different label lengths, breakdown items can appear misaligned. Bottom alignment ensures professional symmetry.

**Implementation:**

1. Container: `flex flex-col h-full`
2. Spacer: `<div class="flex-grow"></div>`
3. Breakdown: `mt-auto` class

---

## Quick Action Components

### 📚 Comprehensive Documentation Available

**For complete Quick Action implementation guide, see:**

- **[Quick Action Components Guide](QUICK_ACTION_COMPONENTS.md)** - Full component templates and patterns
- **[Quick Action Decision Guide](QUICK_ACTION_DECISION_GUIDE.md)** - Quick reference for choosing patterns

This section provides a brief overview. **Refer to the comprehensive guides above for:**

- 3 Official Quick Action Patterns (Sidebar, Header, Floating FAB)
- Complete HTML/CSS templates
- Context-aware action rules
- Color guidelines by action type
- Decision flowcharts
- Module-specific examples

---

### Quick Action Overview

Quick action components provide instant access to common workflows across OBCMS. There are **three official patterns**:

1. **Sidebar Quick Actions** - Right sidebar for dashboards and detail pages
2. **Header Quick Actions** - Horizontal grid below page title for list pages
3. **Floating Quick Actions (FAB)** - Bottom-right floating button for forms and long pages

### Standard Quick Action Card

Quick action cards provide instant access to common workflows. Used in management dashboards.

```html
<a href="/path/to/action"
   class="block bg-gradient-to-br from-white via-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
    <div class="flex items-start space-x-4">
        <div class="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center">
            <i class="fas fa-plus text-white text-xl"></i>
        </div>
        <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                Create New Assessment
            </h3>
            <p class="text-sm text-gray-600">
                Start a new community needs assessment
            </p>
        </div>
        <div class="flex-shrink-0">
            <i class="fas fa-arrow-right text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all"></i>
        </div>
    </div>
</a>
```

### Quick Action Grid Layout

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Quick action cards -->
</div>
```

### Icon Colors for Quick Actions

| Action Type | Gradient | Icon Color |
|-------------|----------|-----------|
| **Create/Add** | `from-blue-500 to-emerald-500` | `text-white` |
| **Edit/Update** | `from-emerald-500 to-teal-500` | `text-white` |
| **View/Reports** | `from-purple-500 to-pink-500` | `text-white` |
| **Export/Download** | `from-amber-500 to-orange-500` | `text-white` |

---

## Forms & Input Components

### Standard Text Input

```html
<div class="mb-4">
    <label for="field-id" class="block text-sm font-medium text-gray-700 mb-2">
        Field Label <span class="text-red-500">*</span>
    </label>
    <input type="text"
           id="field-id"
           name="field_name"
           class="w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200"
           placeholder="Enter value..."
           required>
    <p class="mt-1 text-sm text-gray-500">Helper text</p>
</div>
```

### Standard Select Dropdown ⭐

**Official Pattern** - Used across all forms

```html
<div class="space-y-1">
    <label for="field-id" class="block text-sm font-medium text-gray-700 mb-2">
        Field Label<span class="text-red-500">*</span>
    </label>
    <div class="relative">
        <select id="field-id"
                name="field_name"
                class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200">
            <option value="">Select...</option>
            <option value="option1">Option 1</option>
            <option value="option2">Option 2</option>
        </select>
        <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
            <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
        </span>
    </div>
</div>
```

### Textarea

```html
<div class="mb-4">
    <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
        Description
    </label>
    <textarea id="description"
              name="description"
              rows="4"
              class="w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200 resize-vertical"
              placeholder="Enter detailed description..."></textarea>
</div>
```

### Checkbox Group

```html
<div class="mb-4">
    <fieldset>
        <legend class="block text-sm font-medium text-gray-700 mb-3">
            Available Services
        </legend>
        <div class="space-y-2">
            <label class="flex items-center">
                <input type="checkbox"
                       name="services[]"
                       value="education"
                       class="h-4 w-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500">
                <span class="ml-2 text-sm text-gray-700">Education</span>
            </label>
            <label class="flex items-center">
                <input type="checkbox"
                       name="services[]"
                       value="healthcare"
                       class="h-4 w-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500">
                <span class="ml-2 text-sm text-gray-700">Healthcare</span>
            </label>
        </div>
    </fieldset>
</div>
```

### Radio Button Card Group

**Enhanced selection with card-based UI**

```html
<div class="space-y-3">
    <!-- Selected Option -->
    <label class="flex items-start p-4 border-2 border-emerald-500 bg-emerald-50 rounded-xl cursor-pointer transition-all hover:shadow-md">
        <input type="radio"
               name="methodology"
               value="comprehensive"
               class="mt-1 mr-3 text-emerald-600 focus:ring-emerald-500"
               checked
               required>
        <div>
            <div class="font-semibold text-emerald-900">Comprehensive Assessment</div>
            <div class="text-sm text-emerald-700 mt-1">Full community-wide assessment covering all sectors</div>
        </div>
    </label>

    <!-- Unselected Option -->
    <label class="flex items-start p-4 border-2 border-gray-200 bg-white rounded-xl cursor-pointer transition-all hover:border-gray-300 hover:shadow-md">
        <input type="radio"
               name="methodology"
               value="targeted"
               class="mt-1 mr-3 text-emerald-600 focus:ring-emerald-500"
               required>
        <div>
            <div class="font-semibold text-gray-900">Targeted Assessment</div>
            <div class="text-sm text-gray-600 mt-1">Focus on specific sectors or priority areas</div>
        </div>
    </label>
</div>
```

### Form Section Container

```html
<div class="bg-white rounded-xl p-6 border border-gray-200 mb-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <i class="fas fa-users text-blue-500 mr-2"></i>
        Basic Information
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Form fields -->
    </div>
</div>
```

### Form Submit Row

```html
<div class="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3 pt-6 border-t border-gray-200">
    <button type="button"
            class="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors duration-200">
        <i class="fas fa-times mr-2"></i>
        Cancel
    </button>
    <button type="submit"
            class="bg-gradient-to-r from-blue-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
        <i class="fas fa-save mr-2"></i>
        Save Changes
    </button>
</div>
```

### Form Input Standards

| Element | Border Radius | Border | Focus State | Min Height |
|---------|--------------|--------|-------------|------------|
| Text Input | `rounded-xl` (12px) | `border-gray-200` | `ring-emerald-500` | `min-h-[48px]` |
| Select | `rounded-xl` (12px) | `border-gray-200` | `ring-emerald-500` | `min-h-[48px]` |
| Textarea | `rounded-xl` (12px) | `border-gray-200` | `ring-emerald-500` | - |
| Checkbox | `rounded` (4px) | `border-gray-300` | `ring-emerald-500` | - |
| Radio | `rounded-full` | `border-gray-300` | `ring-emerald-500` | - |

---

## Buttons

### Primary Button (Gradient)

```html
<button class="bg-gradient-to-r from-blue-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
    <i class="fas fa-save mr-2"></i>
    Primary Action
</button>
```

### Secondary Button (Outline)

```html
<button class="border-2 border-gray-300 text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-200">
    <i class="fas fa-times mr-2"></i>
    Secondary Action
</button>
```

### Tertiary Button (Text Only)

```html
<button class="text-blue-600 hover:text-blue-800 px-4 py-2 font-medium transition-colors duration-200">
    <i class="fas fa-edit mr-1"></i>
    Edit
</button>
```

### Icon Button

```html
<button class="w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors duration-200">
    <i class="fas fa-search text-gray-600"></i>
</button>
```

### Button Sizes

```html
<!-- Small -->
<button class="px-3 py-2 text-sm rounded-lg">Small</button>

<!-- Medium (Default) -->
<button class="px-6 py-3 text-base rounded-xl">Medium</button>

<!-- Large -->
<button class="px-8 py-4 text-lg rounded-xl">Large</button>
```

### Button States

```html
<!-- Loading State -->
<button class="bg-blue-600 text-white px-6 py-3 rounded-xl" disabled>
    <i class="fas fa-spinner fa-spin mr-2"></i>
    Loading...
</button>

<!-- Disabled State -->
<button class="bg-gray-300 text-gray-500 px-6 py-3 rounded-xl cursor-not-allowed" disabled>
    Disabled
</button>
```

---

## Cards & Containers

### Basic Card

```html
<div class="bg-white rounded-xl shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow duration-300">
    <h3 class="text-lg font-semibold text-gray-800 mb-3">
        <i class="fas fa-users text-blue-600 mr-2"></i>
        Card Title
    </h3>
    <p class="text-gray-600 mb-4">
        Card content goes here...
    </p>
    <div class="flex justify-between items-center">
        <span class="text-sm text-gray-500">Last updated: March 2024</span>
        <a href="#" class="text-blue-600 hover:text-blue-800 font-medium">
            View Details →
        </a>
    </div>
</div>
```

### Card with Action Footer

```html
<div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
    <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">Barangay Maluso</h3>
        <p class="text-sm text-gray-600 mb-4">Municipality of Balabagan, Lanao del Sur</p>
        <div class="grid grid-cols-2 gap-4">
            <div>
                <span class="text-sm text-gray-500">Population</span>
                <p class="font-semibold text-gray-900">2,847</p>
            </div>
            <div>
                <span class="text-sm text-gray-500">Households</span>
                <p class="font-semibold text-gray-900">456</p>
            </div>
        </div>
    </div>
    <div class="bg-gray-50 px-6 py-3 border-t border-gray-200">
        <div class="flex space-x-3">
            <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                <i class="fas fa-eye mr-1"></i>View
            </button>
            <button class="text-emerald-600 hover:text-emerald-800 text-sm font-medium">
                <i class="fas fa-edit mr-1"></i>Edit
            </button>
            <button class="text-purple-600 hover:text-purple-800 text-sm font-medium">
                <i class="fas fa-chart-bar mr-1"></i>Report
            </button>
        </div>
    </div>
</div>
```

---

## Modal & Dialogs

### Task/Event Modal (Reusable Component)

**Official reusable modal for tasks, events, and dynamic content.**

#### Template Location

```django
{% include 'common/components/task_modal.html' %}
```

#### Component Structure

```html
<div id="taskModal"
     class="fixed inset-0 hidden z-50 flex items-center justify-center px-4 sm:px-6"
     role="dialog"
     aria-modal="true"
     aria-labelledby="modal-title"
     aria-describedby="modal-description">
    <div class="absolute inset-0 bg-gray-900 bg-opacity-50" data-modal-backdrop aria-hidden="true"></div>
    <div class="relative max-h-[90vh] w-full sm:w-auto overflow-y-auto" id="taskModalContent" hx-target="this" hx-swap="innerHTML"></div>
</div>
```

#### Required JavaScript Dependencies

```html
{% block extra_js %}
{{ block.super }}
<script src="{% static 'common/js/htmx-focus-management.js' %}"></script>
<script src="{% static 'common/js/task_modal_enhancements.js' %}"></script>
{% endblock %}
```

#### Usage Example

**1. Include the component in your template:**

```django
{% extends "common/base_with_sidebar.html" %}

{% block content %}
    <!-- Your page content -->
{% endblock %}

{# Include modal at the end of content block #}
{% include 'common/components/task_modal.html' %}

{% block extra_js %}
{{ block.super }}
<script src="{% static 'common/js/htmx-focus-management.js' %}"></script>
<script src="{% static 'common/js/task_modal_enhancements.js' %}"></script>
{% endblock %}
```

**2. Trigger modal with HTMX or JavaScript:**

```html
<!-- Option A: HTMX (preferred) -->
<button hx-get="{% url 'common:staff_task_modal' task.id %}"
        hx-target="#taskModalContent"
        hx-swap="innerHTML"
        onclick="document.getElementById('taskModal').classList.remove('hidden')"
        class="text-blue-600 hover:text-blue-800">
    View Task
</button>

<!-- Option B: JavaScript -->
<button onclick="openTaskModal('{% url 'common:staff_task_modal' task.id %}')"
        class="text-blue-600 hover:text-blue-800">
    View Task
</button>
```

**3. Define `openTaskModal` function (if using Option B):**

```javascript
function openTaskModal(url) {
    const modal = document.getElementById('taskModal');
    const content = document.getElementById('taskModalContent');

    modal.classList.remove('hidden');
    content.innerHTML = '<div class="bg-white rounded-2xl shadow-xl p-10">Loading...</div>';

    htmx.ajax('GET', url, { target: '#taskModalContent', swap: 'innerHTML' });
}
```

#### Modal Content Requirements

**The modal content (returned by your view) should include:**

1. **Close button with `data-close-modal` attribute:**

```html
<button type="button" class="text-gray-400 hover:text-gray-600" data-close-modal>
    <span class="sr-only">Close</span>
    <i class="fas fa-times text-lg"></i>
</button>
```

2. **Proper heading with `id="modal-title"`:**

```html
<h2 id="modal-title" class="text-2xl font-bold text-gray-900">Task Title</h2>
```

3. **Optional description with `id="modal-description"`:**

```html
<div id="modal-description" class="bg-gray-50 border border-gray-200 rounded-xl p-4">
    Task details and description
</div>
```

#### Automatic Features

✅ **Close on backdrop click** - Click outside modal to close
✅ **Close on Escape key** - Press Esc to close
✅ **Focus trap** - Keyboard navigation stays within modal
✅ **Delete button** - Auto-wired with confirmation dialog
✅ **Loading state** - Shows spinner during HTMX requests
✅ **Accessibility** - ARIA attributes, screen reader support

#### Integration with Task Board

This modal component is used in:

- Staff Task Board (`/oobc-management/staff/tasks/`)
- OOBC Calendar (`/oobc-management/calendar/`)
- All task-related views
- Event management pages

#### Best Practices

1. **Always include required JavaScript:**
   - `htmx-focus-management.js` - Handles modal open/close
   - `task_modal_enhancements.js` - Handles delete buttons, color selects

2. **Use `data-modal-backdrop` for backdrop:**
   - Ensures proper click-outside-to-close behavior

3. **Return only modal content from views:**
   - Don't include the modal container in HTMX responses
   - Only return the card/form content to inject into `#taskModalContent`

4. **Test accessibility:**
   - Keyboard navigation (Tab, Shift+Tab, Escape)
   - Screen reader announcements
   - Focus management

#### Reference Implementation

See working examples:

- [Staff Task Board](src/templates/common/staff_task_board.html)
- [OOBC Calendar](src/templates/common/oobc_calendar.html)
- [Task Modal Partial](src/templates/common/partials/staff_task_modal.html)

---

## Navigation Components

### Breadcrumb

```html
<nav class="flex mb-6" aria-label="Breadcrumb">
    <ol class="flex items-center space-x-2 text-sm">
        <li>
            <a href="/" class="text-blue-600 hover:text-blue-800">
                <i class="fas fa-home"></i>
            </a>
        </li>
        <li class="flex items-center">
            <i class="fas fa-chevron-right text-gray-400 mx-2 text-xs"></i>
            <a href="/communities" class="text-blue-600 hover:text-blue-800">Communities</a>
        </li>
        <li class="flex items-center">
            <i class="fas fa-chevron-right text-gray-400 mx-2 text-xs"></i>
            <span class="text-gray-700">Barangay Profile</span>
        </li>
    </ol>
</nav>
```

### Tab Navigation

```html
<div class="border-b border-gray-200 mb-6">
    <nav class="-mb-px flex space-x-8">
        <a href="#overview"
           class="border-b-2 border-blue-500 text-blue-600 py-3 px-1 text-sm font-medium">
            Overview
        </a>
        <a href="#demographics"
           class="border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 py-3 px-1 text-sm font-medium">
            Demographics
        </a>
        <a href="#infrastructure"
           class="border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 py-3 px-1 text-sm font-medium">
            Infrastructure
        </a>
    </nav>
</div>
```

### Pagination

```html
<div class="flex items-center justify-between bg-white px-4 py-3 border border-gray-200 rounded-lg">
    <div class="flex items-center text-sm text-gray-700">
        <span>Showing</span>
        <span class="font-medium mx-1">1</span>
        <span>to</span>
        <span class="font-medium mx-1">20</span>
        <span>of</span>
        <span class="font-medium mx-1">157</span>
        <span>results</span>
    </div>
    <div class="flex items-center space-x-2">
        <button class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50" disabled>
            Previous
        </button>
        <button class="px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-blue-600 rounded-md">
            1
        </button>
        <button class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            2
        </button>
        <button class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            3
        </button>
        <span class="px-3 py-2 text-sm font-medium text-gray-500">...</span>
        <button class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            Next
        </button>
    </div>
</div>
```

---

## Alerts & Messages

### Success Alert

```html
<div class="bg-emerald-50 border-l-4 border-emerald-500 rounded-r-lg p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-check-circle text-emerald-500 text-xl"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-emerald-800">
                Successfully saved!
            </h3>
            <div class="mt-2 text-sm text-emerald-700">
                <p>Community profile has been updated successfully.</p>
            </div>
        </div>
        <div class="ml-auto pl-3">
            <button class="text-emerald-500 hover:text-emerald-700">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>
</div>
```

### Error Alert

```html
<div class="bg-red-50 border-l-4 border-red-500 rounded-r-lg p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-exclamation-circle text-red-500 text-xl"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
                There were errors with your submission
            </h3>
            <div class="mt-2 text-sm text-red-700">
                <ul class="list-disc pl-5 space-y-1">
                    <li>Community name is required</li>
                    <li>Population must be a positive number</li>
                </ul>
            </div>
        </div>
    </div>
</div>
```

### Warning Alert

```html
<div class="bg-amber-50 border-l-4 border-amber-500 rounded-r-lg p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-exclamation-triangle text-amber-500 text-xl"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-amber-800">
                Attention needed
            </h3>
            <div class="mt-2 text-sm text-amber-700">
                <p>This community data was last updated 6 months ago.</p>
            </div>
        </div>
    </div>
</div>
```

### Info Alert

```html
<div class="bg-blue-50 border-l-4 border-blue-500 rounded-r-lg p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-info-circle text-blue-500 text-xl"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-blue-800">
                New feature available
            </h3>
            <div class="mt-2 text-sm text-blue-700">
                <p>You can now export community data to various formats.</p>
            </div>
        </div>
    </div>
</div>
```

---

## Tables & Data Display

### Basic Data Table

```html
<div class="bg-white shadow-md rounded-xl overflow-hidden border border-gray-200">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gradient-to-r from-blue-600 to-emerald-600">
            <tr>
                <th class="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                    Community
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                    Municipality
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                    Population
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                    Status
                </th>
                <th class="px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider">
                    Actions
                </th>
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            <tr class="hover:bg-gray-50 transition-colors duration-200">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">Barangay Maluso</div>
                    <div class="text-sm text-gray-500">OBC-001</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    Balabagan
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    2,847
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-emerald-100 text-emerald-800">
                        Active
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-3">
                        <a href="#" class="text-blue-600 hover:text-blue-900">
                            <i class="fas fa-eye"></i>
                        </a>
                        <a href="#" class="text-emerald-600 hover:text-emerald-900">
                            <i class="fas fa-edit"></i>
                        </a>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

---

## Status Indicators

### Status Badges

```html
<!-- Success -->
<span class="px-3 py-1 inline-flex items-center text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800">
    <i class="fas fa-check-circle mr-1"></i>
    Active
</span>

<!-- Warning -->
<span class="px-3 py-1 inline-flex items-center text-xs font-semibold rounded-full bg-amber-100 text-amber-800">
    <i class="fas fa-exclamation-triangle mr-1"></i>
    Pending
</span>

<!-- Error -->
<span class="px-3 py-1 inline-flex items-center text-xs font-semibold rounded-full bg-red-100 text-red-800">
    <i class="fas fa-times-circle mr-1"></i>
    Inactive
</span>

<!-- Info -->
<span class="px-3 py-1 inline-flex items-center text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
    <i class="fas fa-info-circle mr-1"></i>
    In Review
</span>
```

### Progress Bar

```html
<div class="mb-4">
    <div class="flex justify-between text-sm text-gray-600 mb-1">
        <span class="font-medium">Assessment Progress</span>
        <span>75%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div class="bg-emerald-600 h-2.5 rounded-full transition-all duration-300" style="width: 75%"></div>
    </div>
</div>
```

---

## Layout System

### Container

```html
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Content -->
</div>
```

### Section Spacing

```html
<div class="space-y-6">
    <!-- Section 1 -->
    <!-- Section 2 -->
    <!-- Section 3 -->
</div>
```

### Responsive Grid

```html
<!-- 2-Column -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Columns -->
</div>

<!-- 3-Column -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Columns -->
</div>

<!-- 4-Column -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- Columns -->
</div>
```

---

## Accessibility Guidelines

### WCAG 2.1 AA Compliance

✅ **Color Contrast**

- Normal text: Minimum 4.5:1
- Large text (18px+): Minimum 3:1
- UI components: Minimum 3:1

✅ **Keyboard Navigation**

- All interactive elements are focusable
- Clear focus indicators
- Logical tab order

✅ **Screen Reader Support**

- Semantic HTML elements
- ARIA labels where needed
- Alt text for images

✅ **Touch Targets**

- Minimum 48x48px for all interactive elements
- Adequate spacing between targets

### Focus States

```css
/* Standard focus ring */
.focus-ring:focus {
    outline: none;
    ring: 2px solid #059669; /* emerald-600 */
    ring-offset: 2px;
}
```

### ARIA Labels

```html
<button aria-label="Delete community profile">
    <i class="fas fa-trash"></i>
</button>

<nav aria-label="Main navigation">
    <!-- Navigation items -->
</nav>

<section aria-labelledby="section-title">
    <h2 id="section-title">Section Title</h2>
    <!-- Section content -->
</section>
```

---

## Implementation Checklist

When implementing UI components:

- [ ] Use appropriate component from this guide
- [ ] Apply semantic HTML elements
- [ ] Include ARIA labels where needed
- [ ] Ensure keyboard navigation works
- [ ] Test color contrast ratios
- [ ] Verify focus states are visible
- [ ] Test on mobile devices
- [ ] Validate responsive behavior
- [ ] Check cross-browser compatibility
- [ ] Test with screen reader

---

## Calendar Components

### Calendar Event Display (Google Calendar Style) ⭐ **NEW**

**Status:** ✅ Implemented (Oct 2025)
**Pattern:** Compact inline layout for calendar events
**Reference:** [Calendar Event Layout Guide](../improvements/UI/CALENDAR_EVENT_LAYOUT_GUIDE.md)

#### Design Pattern

Calendar events use a **single horizontal row** with essential information inline and detailed metadata in tooltips.

```
[hierarchy] [icon] Title text... [status] [priority] [time] [expand]
```

#### Implementation

**File:** `src/templates/common/oobc_calendar.html` (lines 278-407)

**Container:**

```javascript
eventRow.className = 'flex items-center gap-1 text-sm';
```

**Elements:**

1. **Hierarchy Indicator** (optional): `└` for child items
2. **Work Type Icon** (always): Project, Activity, Task icons
3. **Title Text** (always): `flex-1 truncate font-medium leading-tight`
4. **Status Icon** (always): In progress, Completed, etc.
5. **Priority Flag** (conditional): Red exclamation for critical only
6. **Time Display** (conditional): For timed events only
7. **Expand Button** (conditional): For parent items with children

#### Visual Examples

**Basic Event:**

```
[📋] Weekly Team Meeting [🔵]
```

**Critical Priority with Time:**

```
[📊] Q4 Budget Review [🔵] [❗] 2:00 PM
```

**Child Item:**

```
└ [✓] Submit reports [✅] 3:30 PM
```

#### Tooltip (Multi-line)

All detailed metadata appears in native browser tooltip on hover:

```
PROJECT: Infrastructure Development
Status: in_progress
Priority: critical
Recurring event
Project: BARMM Infrastructure
Time: 2:00 PM - 4:00 PM
```

#### CSS Classes Reference

```css
/* Container */
flex items-center gap-1 text-sm

/* Title */
flex-1 truncate font-medium leading-tight

/* Icons */
leading-none flex-shrink-0

/* Time */
text-xs text-gray-600 flex-shrink-0

/* Hierarchy */
text-gray-400 text-xs leading-none
```

#### Benefits

- **Compact**: 3x more events visible in month view
- **Scannable**: Key info at a glance
- **Detailed**: Full metadata in tooltip
- **Accessible**: ARIA labels and keyboard support
- **Performant**: 30% fewer DOM nodes

#### Accessibility

- Comprehensive `aria-label` with all metadata
- Native `title` tooltip for mouse users
- `tabindex="0"` for keyboard navigation
- `role="button"` for semantic meaning
- Screen reader compatible

#### Related Documentation

- [Calendar Event Compact Refactor](../improvements/UI/CALENDAR_EVENT_COMPACT_REFACTOR.md)
- [Calendar Event Layout Guide](../improvements/UI/CALENDAR_EVENT_LAYOUT_GUIDE.md)

---

## Reference Templates

### Forms

- **Provincial Management**: `src/templates/communities/provincial_manage.html`
- **MANA Assessment**: `src/templates/mana/mana_new_assessment.html`
- **Form Components**: `src/templates/components/form_field_*.html`

### Stat Cards

- **Reference Implementation**: `src/templates/recommendations/recommendations_home.html`
- **Template Standard**: [STATCARD_TEMPLATE.md](../improvements/UI/STATCARD_TEMPLATE.md)

### Quick Actions

- **OOBC Management**: `src/templates/common/oobc_management_home.html`
- **MANA Home**: `src/templates/mana/mana_home.html`

### Calendar

- **OOBC Calendar**: `src/templates/common/oobc_calendar.html` (lines 278-407)
- **Layout Guide**: [Calendar Event Layout Guide](../improvements/UI/CALENDAR_EVENT_LAYOUT_GUIDE.md)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **3.1** | **2025-10-12** | **Color system corrected** - Updated to confirmed Blue-to-Teal gradient (#1e40af to #059669), removed Ocean Blue references, verified from navbar screenshot |
| **2.1** | **2025-10-12** | **Enhanced with comprehensive patterns** - Added HTMX & Instant UI section, For AI Coding Agents section, decision trees, quick reference tables, accessibility checklist, mobile patterns |
| 2.1 | 2025-10-06 | Added **Calendar Components** - Google Calendar-style compact event rendering |
| 2.0 | 2025-10-03 | Added 3D Milk White Stat Cards, Quick Action Cards, Form Standards, **Reusable Modal Component** |
| 1.0 | 2024-XX-XX | Initial component library |

---

## Support & Feedback

**Document Owner:** OBCMS UI/UX Team

**Related Documentation:**
- [STATCARD_TEMPLATE.md](../improvements/UI/STATCARD_TEMPLATE.md)
- [Quick Action Components](QUICK_ACTION_COMPONENTS.md)
- [Calendar Event Layout Guide](../improvements/UI/CALENDAR_EVENT_LAYOUT_GUIDE.md)
- [Form Design Standards](../improvements/mana/form_design_standards.md)
- [Instant UI Improvements Plan](../improvements/instant_ui_improvements_plan.md)

**Additional Resources:**
- [DELETE_CONFIRMATION_BEST_PRACTICES.md](DELETE_CONFIRMATION_BEST_PRACTICES.md)
- [OPTIMISTIC_UI_PATTERN_QUICK_REFERENCE.md](OPTIMISTIC_UI_PATTERN_QUICK_REFERENCE.md)
- [WORK_ITEM_MODAL_QUICK_REFERENCE.md](WORK_ITEM_MODAL_QUICK_REFERENCE.md)

---

**Last Updated:** 2025-10-12
**Status:** ✅ Official OBCMS UI Standards - Enhanced with AI Agent Instructions

## Patterns & Best Practices

### Form Design Standards

**IMPORTANT**: When designing or modifying forms, ALWAYS reference existing templates for UI/UX consistency:

- **Review similar forms** in `src/templates/` to understand established patterns
- **Use component templates** (`src/templates/components/`) for standard form elements
- **Follow dropdown styling**: Use `rounded-xl`, `border-gray-200`, emerald focus rings, chevron icons
- **Check reference templates**: `src/templates/communities/provincial_manage.html`, `src/templates/components/form_field_select.html`
- **Maintain consistency** in spacing, colors, borders, and interactive states across all forms

### Data Table Cards

- Directory/list pages should extend `components/data_table_card.html` so Barangay and Municipal OBC lists stay visually aligned.
- Pass a `headers` array and `rows` data with `view_url`, `edit_url`, and `delete_preview_url`.
- The component already handles the action buttons and the two-step delete confirmation (confirm dialog → redirect to detail for "Review before deletion").

### Mobile Patterns

#### Touch Target Sizes

**❌ BAD:**
```html
<button class="w-6 h-6 text-xs">
    <i class="fas fa-trash"></i>
</button>
```

**✅ GOOD:**
```html
<button class="min-w-[48px] min-h-[48px] flex items-center justify-center">
    <i class="fas fa-trash"></i>
</button>
```

#### FAB Mobile Adjustments

```html
<!-- Mobile-Optimized FAB -->
<div class="fixed bottom-20 sm:bottom-8 right-4 sm:right-8 z-50">
    <button class="w-16 h-16 sm:w-14 sm:h-14 rounded-full bg-gradient-to-r from-blue-600 to-teal-600 text-white shadow-2xl">
        <i class="fas fa-bolt text-2xl sm:text-xl"></i>
    </button>
</div>
```

---

## HTMX & Instant UI

**Status:** ✅ Core architectural pattern
**Reference:** [instant_ui_improvements_plan.md](../improvements/instant_ui_improvements_plan.md)

### Priority: Always Implement Instant UI Updates

When working on this codebase, **always prioritize instant UI responses** and smooth interactions. Users expect modern web app behavior - no full page reloads, immediate feedback, and seamless transitions.

### HTMX Implementation Requirements

- **Consistent Targeting**: All interactive elements must use `data-task-id="{{ item.id }}"` for both kanban cards and table rows
- **Optimistic Updates**: Update the UI immediately when user performs an action, then handle server response
- **Smooth Animations**: Use `hx-swap="outerHTML swap:300ms"` or `delete swap:200ms"` for transitions
- **Loading Indicators**: Always show spinners, disabled states, or progress feedback during operations

### Key HTMX Patterns

#### 1. Inline Editing
```html
<div id="task-title-{{ task.id }}"
     hx-get="{% url 'task_edit_field' task.id 'title' %}"
     hx-trigger="click"
     hx-swap="outerHTML"
     tabindex="0">
    <span>{{ task.title }}</span>
    <i class="fas fa-pen text-gray-400 ml-2"></i>
</div>
```

#### 2. Dependent Dropdowns
```html
<select id="region-select"
        hx-get="{% url 'get_provinces' %}"
        hx-trigger="change"
        hx-target="#province-select"
        hx-include="#region-select">
    <option value="">Select Region...</option>
</select>
```

#### 3. Live Counters (Polling)
```html
<div hx-get="{% url 'metrics_pending_tasks' %}"
     hx-trigger="load, every 30s"
     hx-swap="innerHTML"
     aria-live="polite">
    <div class="stat-value">{{ pending_count }}</div>
</div>
```

#### 4. Out-of-Band Swaps
```python
# Django view
return HttpResponse(
    task_html + f'<div id="task-counter" hx-swap-oob="true">{counter_html}</div>'
)
```

#### 5. Optimistic Updates
```html
<button hx-post="{% url 'task_toggle_favorite' task.id %}"
        hx-swap="none"
        onclick="toggleFavoriteOptimistic(this)">
    <i class="fas fa-star"></i>
</button>
```

### Backend Response Standards

All views handling HTMX requests must follow this pattern:

```python
def task_operation_view(request, task_id):
    # ... perform operation ...

    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'task-updated': {'id': task_id, 'action': 'delete'},
                    'show-toast': 'Task updated successfully',
                    'refresh-counters': True
                })
            }
        )
```

### Delete Confirmation Pattern

**Status:** ✅ Production-ready best practices

#### Two-Step Delete with Preview

**Step 1: Confirmation Dialog**
```html
<button hx-get="{% url 'task_delete_confirm' task.id %}"
        hx-target="#modal-container"
        hx-swap="innerHTML"
        class="btn-icon-danger">
    <i class="fas fa-trash"></i>
</button>
```

**Step 2: Modal with Impact Preview**
```html
<div class="modal">
    <p>Delete <strong>{{ task.title }}</strong>?</p>

    <div class="bg-amber-50 border-l-4 border-amber-400 p-4">
        <p>This will also delete:</p>
        <ul>
            <li>{{ subtask_count }} subtasks</li>
            <li>{{ attachment_count }} attachments</li>
        </ul>
    </div>

    <button hx-delete="{% url 'task_delete' task.id %}"
            hx-target="[data-task-id='{{ task.id }}']"
            hx-swap="outerHTML swap:300ms"
            class="btn-danger">
        Delete
    </button>
</div>
```

### UI Animation Standards

- **Task Movements**: 300ms smooth transitions between kanban columns
- **Modal Interactions**: Fade with scale transform for open/close
- **Button Feedback**: Immediate visual response to clicks (color change, disable state)
- **Error Handling**: Clear error states with recovery options, no silent failures

### Critical: Never Use Full Page Reloads

- Implement HTMX for all CRUD operations (Create, Read, Update, Delete)
- Use out-of-band swaps (`hx-swap-oob`) for updating multiple UI regions simultaneously
- Provide graceful fallback mechanisms when HTMX fails
- Maintain accessibility with proper ARIA live regions and state updates

---

## For AI Coding Agents

**CRITICAL:** This document is your PRIMARY reference for all UI/UX work in OBCMS.

### Before Creating ANY UI Component:

1. ✅ **READ this document first** - Check if pattern exists
2. ✅ **COPY existing patterns** - Do NOT create custom components  
3. ✅ **USE component templates** - Found in `src/templates/components/`
4. ✅ **FOLLOW semantic HTML** - Proper accessibility structure
5. ✅ **VERIFY responsive behavior** - Test mobile, tablet, desktop
6. ✅ **TEST accessibility** - WCAG 2.1 AA required
7. ✅ **CHECK color contrast** - Use pre-tested combinations (4.5:1 minimum)

### Implementation Decision Tree

```
Is this a NEW UI component?
├─ YES → Check this guide first
│   ├─ Pattern exists? → Copy from reference template
│   └─ Pattern doesn't exist? → ASK user before creating
└─ NO → Modifying existing? → Follow existing patterns exactly
```

### When Creating Forms:

1. **ALWAYS review similar forms** in `src/templates/` first
2. **USE standard dropdown pattern** (rounded-xl, emerald focus rings)
3. **INCLUDE component templates** instead of duplicating markup
4. **MAINTAIN consistency** in spacing, colors, borders

### When Creating Stat Cards:

1. **USE 3D Milk White template** (mandatory)
2. **COPY from** [STATCARD_TEMPLATE.md](../improvements/UI/STATCARD_TEMPLATE.md)
3. **IMPLEMENT bottom alignment** for breakdowns
4. **FOLLOW semantic icon colors** (amber=total, emerald=success, etc.)

### When Implementing Instant UI:

1. **ALWAYS use HTMX** for CRUD operations
2. **PROVIDE instant feedback** (optimistic updates)
3. **IMPLEMENT smooth animations** (300ms transitions)
4. **HANDLE errors gracefully** (rollback on failure)

### Component Selection Quick Reference

| Need | Component | Reference |
|------|-----------|-----------|
| **Statistics display** | 3D Milk White Stat Card | [STATCARD_TEMPLATE.md](../improvements/UI/STATCARD_TEMPLATE.md) |
| **Action buttons** | Quick Action Cards | [QUICK_ACTION_COMPONENTS.md](QUICK_ACTION_COMPONENTS.md) |
| **Form inputs** | Standard Form Components | This guide § Forms & Input Components |
| **Modal dialogs** | Task/Event Modal | This guide § Modal & Dialogs |
| **Data tables** | Basic Data Table | This guide § Tables & Data Display |
| **Calendar events** | Compact Event Layout | This guide § Calendar Components |
| **Navigation** | Breadcrumb/Tabs | This guide § Navigation Components |
| **Alerts** | Success/Error/Warning/Info | This guide § Alerts & Messages |

### Common Mistakes to Avoid:

❌ **DON'T create custom modal components** - Use `task_modal.html`
❌ **DON'T use full page reloads** - Use HTMX partial updates
❌ **DON'T skip accessibility** - ARIA labels are mandatory
❌ **DON'T forget mobile** - Test responsive behavior
❌ **DON'T create docs in root** - Use `docs/` subdirectories
❌ **DON'T invent new patterns** - Check this guide first

### Accessibility Checklist

- [ ] **Semantic HTML** - Use proper elements (`<nav>`, `<button>`, `<main>`)
- [ ] **ARIA labels** - All interactive elements have descriptive labels
- [ ] **Keyboard navigation** - Tab order is logical, Enter/Space work
- [ ] **Focus indicators** - Visible 2px emerald ring on all focusable elements
- [ ] **Color contrast** - Minimum 4.5:1 for normal text (use WCAG checker)
- [ ] **Touch targets** - Minimum 48x48px, adequate spacing (8px+)
- [ ] **Screen reader** - Test with VoiceOver (Mac) or NVDA (Windows)
- [ ] **Responsive** - Test mobile (375px), tablet (768px), desktop (1440px)

### HTMX Best Practices

- [ ] **Consistent targeting** - Use `data-task-id` for all dynamic elements
- [ ] **Optimistic UI** - Update immediately, handle response asynchronously
- [ ] **Smooth animations** - `hx-swap="outerHTML swap:300ms"`
- [ ] **Loading states** - Show spinner or disable button during requests
- [ ] **Error handling** - Display clear error messages with recovery options
- [ ] **Out-of-band swaps** - Update multiple regions with `hx-swap-oob`
- [ ] **ARIA live regions** - Announce dynamic changes to screen readers

### Quick Decision Guide

**"Which Quick Action pattern should I use?"**
- Dashboard/Detail page → Sidebar Quick Actions
- List/Table page → Header Quick Actions  
- Form/Long page → Floating FAB

**"Which delete confirmation?"**
- Simple delete → Two-step modal (confirm → delete)
- Complex delete → Impact preview (show related items that will be deleted)

**"Which color for this icon?"**
- Total/general → Amber (`text-amber-600`)
- Success/complete → Emerald (`text-emerald-600`)
- In progress → Blue (`text-blue-600`)
- Draft/proposed → Purple (`text-purple-600`)
- Warning → Orange (`text-orange-600`)
- Critical/error → Red (`text-red-600`)

---

**Remember:** When in doubt, choose accessibility and clarity over aesthetics. Every UI choice should serve the user's needs first.

**Last Updated:** 2025-10-12
**Status:** ✅ Official OBCMS UI Standards - Enhanced with AI Agent Instructions
