# OBCMS Quick Action Components Guide

**Version:** 1.0
**Last Updated:** 2025-10-03
**Status:** Official Standard
**Operating Mode:** Architect Mode

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Action Patterns](#quick-action-patterns)
3. [A. Sidebar Quick Actions (Right Sidebar)](#a-sidebar-quick-actions-right-sidebar)
4. [B. Header Quick Actions (Horizontal Bar)](#b-header-quick-actions-horizontal-bar)
5. [C. Floating Quick Actions (Bottom-Right FAB)](#c-floating-quick-actions-bottom-right-fab)
6. [Quick Action Card Anatomy](#quick-action-card-anatomy)
7. [Context-Aware Action Rules](#context-aware-action-rules)
8. [Decision Matrix: When to Use Each Pattern](#decision-matrix-when-to-use-each-pattern)
9. [Color Guidelines by Action Type](#color-guidelines-by-action-type)
10. [Accessibility & Best Practices](#accessibility--best-practices)

---

## Overview

Quick Actions provide users with immediate access to common workflows and operations. This guide defines **three official patterns** for Quick Actions in OBCMS:

1. **Sidebar Quick Actions** - Right sidebar for detail pages and dashboards
2. **Header Quick Actions** - Horizontal action bar below page title for list/table pages
3. **Floating Quick Actions** - Bottom-right FAB for forms and long pages

### Design Principles

- **Context-Aware**: Actions change based on page type and user permissions
- **Prioritized**: Most common actions appear first
- **Accessible**: Keyboard navigation, ARIA labels, touch-friendly
- **Consistent**: Same visual language across all modules
- **Permission-Aware**: Actions respect user roles and permissions

---

## Quick Action Patterns

### Pattern Selection Guide

| Page Type | Primary Pattern | Secondary Pattern | Use Case |
|-----------|----------------|-------------------|----------|
| **Dashboard** | Sidebar | Header | System overview with metrics |
| **Detail Page** | Sidebar | Floating FAB | Single record view (workflow, organization, etc.) |
| **List/Table Page** | Header | - | Directory of multiple records |
| **Form Page** | Floating FAB | Header | Create/edit operations |
| **Calendar/Map** | Header | Floating FAB | Interactive visualization |
| **Home/Landing** | Header (Grid) | - | Module entry point |

---

## A. Sidebar Quick Actions (Right Sidebar)

### Use Cases
- Dashboard pages (Portfolio Dashboard, Management Dashboard)
- Detail pages with rich content (Workflow Detail, Partnership Detail)
- Pages with multiple content sections requiring persistent actions

### Design Characteristics
- **Position**: Right sidebar, sticky on scroll
- **Width**: `md:w-80` (320px) on medium+ screens, full-width on mobile
- **Layout**: Vertical stack of action cards
- **Header**: Icon + Title + Description

### Complete Component Template

```html
<!-- ============================================= -->
<!-- SIDEBAR QUICK ACTIONS (RIGHT SIDEBAR)       -->
<!-- Use for: Dashboards, Detail Pages           -->
<!-- ============================================= -->
<aside class="rounded-2xl bg-white border border-gray-200 shadow-xl p-6 space-y-5 sticky top-6">
    <!-- Header -->
    <header class="flex items-center gap-3">
        <div class="shrink-0 rounded-xl bg-emerald-100 text-emerald-600 p-3">
            <i class="fas fa-bolt text-xl"></i>
        </div>
        <div>
            <h3 class="text-lg font-semibold text-gray-900">Action Center</h3>
            <p class="text-sm text-gray-500">Quick jumps into the most active modules</p>
        </div>
    </header>

    <!-- Action List -->
    <ul class="space-y-3">
        <!-- Action Item: View/Navigate -->
        <li>
            <a href="{% url 'module:action_view' %}"
               class="group flex items-center justify-between rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 text-sm font-semibold text-gray-700 hover:border-emerald-200 hover:bg-emerald-50 transition-all duration-200">
                <div class="flex items-center gap-3">
                    <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-rose-100 text-rose-600">
                        <i class="fas fa-bell-exclamation"></i>
                    </span>
                    <div>
                        <p>Active alerts</p>
                        <p class="text-xs font-normal text-gray-500">{{ count }} awaiting review</p>
                    </div>
                </div>
                <i class="fas fa-arrow-right text-gray-400 group-hover:text-emerald-600"></i>
            </a>
        </li>

        <!-- Action Item: Manage/List -->
        <li>
            <a href="{% url 'module:manage' %}"
               class="group flex items-center justify-between rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 text-sm font-semibold text-gray-700 hover:border-emerald-200 hover:bg-emerald-50 transition-all duration-200">
                <div class="flex items-center gap-3">
                    <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600">
                        <i class="fas fa-diagram-project"></i>
                    </span>
                    <div>
                        <p>Tracked workflows</p>
                        <p class="text-xs font-normal text-gray-500">{{ count }} recent updates</p>
                    </div>
                </div>
                <i class="fas fa-arrow-right text-gray-400 group-hover:text-emerald-600"></i>
            </a>
        </li>

        <!-- Action Item: Process/Dashboard -->
        <li>
            <a href="{% url 'module:dashboard' %}"
               class="group flex items-center justify-between rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 text-sm font-semibold text-gray-700 hover:border-emerald-200 hover:bg-emerald-50 transition-all duration-200">
                <div class="flex items-center gap-3">
                    <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-100 text-blue-600">
                        <i class="fas fa-calculator"></i>
                    </span>
                    <div>
                        <p>Budget approvals</p>
                        <p class="text-xs font-normal text-gray-500">Check ceiling allocations and routes</p>
                    </div>
                </div>
                <i class="fas fa-arrow-right text-gray-400 group-hover:text-emerald-600"></i>
            </a>
        </li>
    </ul>
</aside>
```

### Layout Integration (Two-Column)

```html
<div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
    <!-- Main Content (2/3 width) -->
    <div class="xl:col-span-2">
        <!-- Main content here -->
    </div>

    <!-- Sidebar Quick Actions (1/3 width) -->
    <aside class="rounded-2xl bg-white border border-gray-200 shadow-xl p-6 space-y-5">
        <!-- Sidebar Quick Actions Component -->
    </aside>
</div>
```

### Icon Background Colors

| Action Type | Background Class | Icon Color | Use Case |
|-------------|-----------------|------------|----------|
| **Alert/Critical** | `bg-rose-100` | `text-rose-600` | Alerts, warnings, urgent actions |
| **Primary/Main** | `bg-emerald-100` | `text-emerald-600` | Main workflows, projects, core actions |
| **Process/Calculate** | `bg-blue-100` | `text-blue-600` | Budget, calculations, processing |
| **Info/View** | `bg-cyan-100` | `text-cyan-600` | Reports, analytics, viewing |
| **Secondary** | `bg-purple-100` | `text-purple-600` | Alternative actions, coordination |

---

## B. Header Quick Actions (Horizontal Bar)

### Use Cases
- List pages with tables (Communities List, Events List, Organizations)
- Home/landing pages for modules
- Pages with filters and search
- After hero sections on module home pages

### Design Characteristics
- **Position**: Below page title/description, above main content
- **Layout**: Horizontal grid (`md:grid-cols-3` or `md:grid-cols-4`)
- **Card Style**: Vertical cards with gradient icon containers
- **Hover Effect**: Lift transform (`hover:-translate-y-1`)

### Complete Component Template

```html
<!-- ============================================= -->
<!-- HEADER QUICK ACTIONS (HORIZONTAL BAR)       -->
<!-- Use for: List Pages, Home Pages, Tables     -->
<!-- ============================================= -->
<section>
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        <!-- Quick Action Card: Create/Add -->
        <a href="{% url 'module:create' %}"
           class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
            <div class="p-6 flex flex-col flex-grow">
                <!-- Icon Container (Gradient) -->
                <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <i class="fas fa-plus text-white text-xl"></i>
                </div>

                <!-- Title -->
                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    Add New Record
                </h3>

                <!-- Description -->
                <p class="mt-2 text-sm text-gray-600 flex-grow">
                    Create a new entry in the system database.
                </p>

                <!-- Call-to-Action Arrow -->
                <div class="mt-4 flex items-center text-blue-600 text-sm font-medium">
                    <span>Open Form</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </div>
            </div>
        </a>

        <!-- Quick Action Card: Manage/View -->
        <a href="{% url 'module:manage' %}"
           class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
            <div class="p-6 flex flex-col flex-grow">
                <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <i class="fas fa-edit text-white text-xl"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-green-600 transition-colors">
                    Manage Records
                </h3>
                <p class="mt-2 text-sm text-gray-600 flex-grow">
                    View and update existing records in the database.
                </p>
                <div class="mt-4 flex items-center text-green-600 text-sm font-medium">
                    <span>Open Management</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </div>
            </div>
        </a>

        <!-- Quick Action Card: Report/Export -->
        <a href="{% url 'module:report' %}"
           class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
            <div class="p-6 flex flex-col flex-grow">
                <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <i class="fas fa-chart-bar text-white text-xl"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">
                    View Reports
                </h3>
                <p class="mt-2 text-sm text-gray-600 flex-grow">
                    Generate analytics and export data summaries.
                </p>
                <div class="mt-4 flex items-center text-purple-600 text-sm font-medium">
                    <span>Open Reports</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </div>
            </div>
        </a>

    </div>
</section>
```

### Compact Horizontal Variant (Below Table Header)

For pages with limited vertical space:

```html
<!-- Compact Horizontal Quick Actions -->
<div class="bg-white rounded-lg shadow-lg p-6 mb-8">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

        <a href="{% url 'module:create' %}"
           class="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-3 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 font-medium flex items-center justify-center">
            <i class="fas fa-plus mr-2"></i>
            Create New
        </a>

        <a href="{% url 'module:manage' %}"
           class="bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-4 py-3 rounded-lg hover:from-emerald-600 hover:to-teal-700 transition-all duration-200 transform hover:scale-105 font-medium flex items-center justify-center">
            <i class="fas fa-edit mr-2"></i>
            Manage Records
        </a>

        <button class="bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-3 rounded-lg hover:from-green-600 hover:to-green-700 transition-all duration-200 transform hover:scale-105 font-medium">
            <i class="fas fa-file-export mr-2"></i>
            Export Data
        </button>

        <a href="{% url 'module:calendar' %}"
           class="bg-gradient-to-r from-purple-500 to-purple-600 text-white px-4 py-3 rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 font-medium flex items-center justify-center">
            <i class="fas fa-calendar-week mr-2"></i>
            View Calendar
        </a>

    </div>
</div>
```

---

## C. Floating Quick Actions (Bottom-Right FAB)

### Use Cases
- Form pages (Create/Edit forms with many fields)
- Long scrolling pages (detail pages with multiple sections)
- Map/calendar interfaces where header space is limited
- Pages where users need persistent access to actions while scrolling

### Design Characteristics
- **Position**: Fixed bottom-right corner (`fixed bottom-8 right-8`)
- **Z-Index**: High (`z-50`) to float above all content
- **Size**: Large touch target (56x56px minimum)
- **Menu**: Expandable menu on click/hover
- **Mobile**: Adjusted position (`bottom-20` on small screens for navigation clearance)

### Complete Component Template

```html
<!-- ============================================= -->
<!-- FLOATING QUICK ACTIONS (BOTTOM-RIGHT FAB)   -->
<!-- Use for: Forms, Long Pages, Maps/Calendars  -->
<!-- ============================================= -->

<!-- FAB Button with Expandable Menu -->
<div class="fixed bottom-8 right-8 z-50 flex flex-col items-end gap-3" id="fabMenu">

    <!-- Secondary Actions (Hidden by default, shown on hover/click) -->
    <div class="hidden group-hover:flex flex-col gap-3 transition-all duration-300" id="fabActions">

        <!-- Action: Save Draft -->
        <a href="#"
           onclick="saveDraft(); return false;"
           class="flex items-center gap-3 bg-white rounded-full shadow-lg border border-gray-200 px-4 py-3 hover:shadow-xl transition-all duration-200 group/action"
           title="Save as Draft">
            <span class="text-sm font-medium text-gray-700 group-hover/action:text-emerald-600 transition-colors">
                Save Draft
            </span>
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-md">
                <i class="fas fa-save text-white"></i>
            </div>
        </a>

        <!-- Action: Preview -->
        <a href="#"
           onclick="previewForm(); return false;"
           class="flex items-center gap-3 bg-white rounded-full shadow-lg border border-gray-200 px-4 py-3 hover:shadow-xl transition-all duration-200 group/action"
           title="Preview">
            <span class="text-sm font-medium text-gray-700 group-hover/action:text-blue-600 transition-colors">
                Preview
            </span>
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md">
                <i class="fas fa-eye text-white"></i>
            </div>
        </a>

        <!-- Action: Help -->
        <a href="#"
           onclick="showHelp(); return false;"
           class="flex items-center gap-3 bg-white rounded-full shadow-lg border border-gray-200 px-4 py-3 hover:shadow-xl transition-all duration-200 group/action"
           title="Help & Documentation">
            <span class="text-sm font-medium text-gray-700 group-hover/action:text-purple-600 transition-colors">
                Help
            </span>
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-md">
                <i class="fas fa-question-circle text-white"></i>
            </div>
        </a>

    </div>

    <!-- Primary FAB Button (Always Visible) -->
    <button type="button"
            class="w-14 h-14 rounded-full bg-gradient-to-r from-blue-600 to-teal-600 text-white shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-200 flex items-center justify-center group"
            onclick="toggleFABMenu()"
            aria-label="Quick Actions Menu"
            aria-expanded="false"
            id="fabButton">
        <i class="fas fa-bolt text-xl group-hover:rotate-12 transition-transform"></i>
    </button>

</div>

<!-- JavaScript for FAB Menu Toggle -->
<script>
function toggleFABMenu() {
    const fabActions = document.getElementById('fabActions');
    const fabButton = document.getElementById('fabButton');
    const isExpanded = fabButton.getAttribute('aria-expanded') === 'true';

    if (isExpanded) {
        fabActions.classList.add('hidden');
        fabButton.setAttribute('aria-expanded', 'false');
    } else {
        fabActions.classList.remove('hidden');
        fabButton.setAttribute('aria-expanded', 'true');
    }
}

// Close FAB menu when clicking outside
document.addEventListener('click', function(event) {
    const fabMenu = document.getElementById('fabMenu');
    const fabActions = document.getElementById('fabActions');
    const fabButton = document.getElementById('fabButton');

    if (!fabMenu.contains(event.target)) {
        fabActions.classList.add('hidden');
        fabButton.setAttribute('aria-expanded', 'false');
    }
});
</script>
```

### Simplified FAB (Single Primary Action)

For pages with one primary action:

```html
<!-- Simple FAB: Add/Create -->
<a href="{% url 'module:create' %}"
   class="fixed bottom-8 right-8 z-50 w-14 h-14 rounded-full bg-gradient-to-r from-blue-600 to-teal-600 text-white shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-200 flex items-center justify-center"
   title="Create New Record"
   aria-label="Create New Record">
    <i class="fas fa-plus text-xl"></i>
</a>
```

### Mobile Adjustments

```html
<!-- Mobile-Optimized FAB (Larger, Higher Position) -->
<div class="fixed bottom-20 sm:bottom-8 right-4 sm:right-8 z-50">
    <button type="button"
            class="w-16 h-16 sm:w-14 sm:h-14 rounded-full bg-gradient-to-r from-blue-600 to-teal-600 text-white shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-200 flex items-center justify-center"
            aria-label="Quick Actions">
        <i class="fas fa-bolt text-2xl sm:text-xl"></i>
    </button>
</div>
```

---

## Quick Action Card Anatomy

### Required Elements

1. **Icon Container**
   - Size: `w-12 h-12` (48x48px) or `w-9 h-9` (36x36px) for compact
   - Background: Gradient (`bg-gradient-to-br from-{color}-500 to-{color}-600`)
   - Icon: FontAwesome, `text-white text-xl`
   - Hover: `group-hover:scale-110 transition-transform`

2. **Title**
   - Font: `text-lg font-semibold text-gray-900`
   - Hover: `group-hover:text-{color}-600 transition-colors`
   - Contrast: Minimum 4.5:1 ratio

3. **Description (Optional)**
   - Font: `text-sm text-gray-600`
   - Purpose: Explain action clearly
   - Length: Keep under 15 words

4. **Count/Badge (Optional)**
   - Position: Next to title or in icon container
   - Style: `text-xs font-normal text-gray-500`
   - Use case: Show pending items, recent updates

5. **Link/Action**
   - Element: `<a>` or `<button>`
   - States: Default, hover, focus, active
   - Arrow: `<i class="fas fa-arrow-right">` for navigation

### Spacing Guidelines

```css
/* Card Padding */
padding: 1.5rem; /* p-6 */

/* Icon Margin Bottom */
margin-bottom: 1rem; /* mb-4 */

/* Title Margin Top (if description) */
margin-top: 0.5rem; /* mt-2 */

/* CTA Margin Top */
margin-top: 1rem; /* mt-4 */

/* Gap Between Cards */
gap: 1.5rem; /* gap-6 */
```

---

## Context-Aware Action Rules

### What actions appear on different page types?

#### Detail Pages (Workflow, Partnership, Organization, etc.)

**Sidebar Quick Actions:**
- View related records (calendar, tasks, activities)
- Navigate to management dashboards
- Access reports/analytics specific to this record
- Edit/update current record
- Create related records (add task, schedule activity)

**Example (Workflow Detail):**
```html
<ul class="space-y-3">
    <li><a href="project-calendar">View Project Calendar</a></li>
    <li><a href="create-task">Create Project Task</a></li>
    <li><a href="add-activity">Schedule Activity</a></li>
    <li><a href="budget-dashboard">Budget Dashboard</a></li>
</ul>
```

#### List/Table Pages (Communities, Events, Assessments)

**Header Quick Actions:**
- Create new record (primary action)
- Manage/edit existing records
- Export/download data
- View calendar/map visualization
- Access filters/advanced search

**Example (Communities List):**
```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <a href="add-barangay">Add Barangay OBC</a>
    <a href="manage-barangay">Manage Barangay OBC</a>
    <a href="view-on-map">View on Map</a>
</div>
```

#### Dashboard Pages (Portfolio, Management, Module Home)

**Sidebar Quick Actions:**
- Navigate to key modules
- Access pending approvals/alerts
- View recent activities
- Quick links to workflows

**Header Quick Actions (Hero Section):**
- Primary CTA (create new workflow, start assessment)
- Return to main dashboard
- View calendar/schedule
- Export system reports

#### Form Pages (Create/Edit)

**Floating FAB:**
- Save as draft
- Preview before submit
- Help/documentation
- Clear form/reset
- Auto-save indicator

#### Calendar/Map Pages

**Header Quick Actions:**
- Create event/add location
- Toggle view modes (calendar/list/map)
- Export calendar
- Filter by date range

**Floating FAB:**
- Quick add event
- Jump to today
- View legend/help

---

## Decision Matrix: When to Use Each Pattern

### Use Sidebar Quick Actions When:

✅ Page has rich content requiring persistent navigation (dashboards)
✅ Multiple related modules need quick access
✅ Actions relate to specific context of current page
✅ Desktop layout with 2-column or 3-column grid
✅ User needs to jump between related sections frequently

❌ Mobile-first design (sidebar collapses, loses prominence)
❌ Page is form-heavy with limited width
❌ Actions are simple CRUD operations (use header instead)

### Use Header Quick Actions When:

✅ Module home page or landing page
✅ List/table pages with multiple records
✅ Actions are primary workflows (create, manage, export)
✅ Need grid layout to showcase multiple equal-priority actions
✅ After hero sections to guide users to next steps

❌ Form pages (actions compete with form submission)
❌ Detail pages with limited horizontal space
❌ More than 6 actions (too crowded)

### Use Floating FAB When:

✅ Long forms requiring scroll to complete
✅ Pages with complex layouts (map, calendar, multi-section detail)
✅ Need persistent action access while scrolling
✅ Primary action is clear (save, create, submit)
✅ Mobile-first design requiring bottom-right thumb zone access

❌ Desktop-only applications (header actions better)
❌ Multiple equally important actions (FAB is for 1-3 actions max)
❌ Pages with bottom navigation that would conflict

---

## Color Guidelines by Action Type

### Icon Container Gradients

| Action Type | Gradient Class | Icon Color | Use Case |
|-------------|---------------|------------|----------|
| **Create/Add** | `from-blue-500 to-blue-600` | `text-white` | Add records, create new |
| **Manage/Edit** | `from-green-500 to-green-600` | `text-white` | Edit, update, manage |
| **View/Report** | `from-purple-500 to-purple-600` | `text-white` | Analytics, reports |
| **Process/Calculate** | `from-emerald-500 to-teal-600` | `text-white` | Budget, workflows |
| **Export/Download** | `from-amber-500 to-amber-600` | `text-white` | Export data, download |
| **Delete/Archive** | `from-red-500 to-red-600` | `text-white` | Destructive actions |
| **Calendar/Schedule** | `from-sky-500 to-sky-600` | `text-white` | Time-based actions |
| **Map/Location** | `from-teal-500 to-cyan-600` | `text-white` | Geographic actions |

### Semantic Icon Colors (for Sidebar Actions)

| Context | Background | Icon Color | Use Case |
|---------|-----------|------------|----------|
| **Alerts/Urgent** | `bg-rose-100` | `text-rose-600` | Pending approvals, alerts |
| **Primary/Active** | `bg-emerald-100` | `text-emerald-600` | Main workflows, active items |
| **Info/Process** | `bg-blue-100` | `text-blue-600` | Budget, calculations |
| **Secondary** | `bg-purple-100` | `text-purple-600` | Coordination, partnerships |
| **Warning** | `bg-amber-100` | `text-amber-600` | Needs attention |

### Hover State Colors

```html
<!-- Header Quick Action Card Hover -->
<h3 class="group-hover:text-blue-600">   <!-- Title color on hover -->
<div class="text-blue-600">             <!-- CTA arrow color -->

<!-- Sidebar Quick Action Hover -->
<a class="hover:border-emerald-200 hover:bg-emerald-50">  <!-- Card background -->
<i class="group-hover:text-emerald-600">                  <!-- Arrow color -->
```

---

## Accessibility & Best Practices

### WCAG 2.1 AA Compliance

#### Color Contrast
- **Text on White**: Minimum 4.5:1 ratio
- **Icon on Gradient**: White icons ensure maximum contrast
- **Hover States**: Maintain contrast ratios during interactions

#### Keyboard Navigation
```html
<!-- Focusable elements with visible focus ring -->
<a href="..." class="focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2">
    Quick Action
</a>
```

#### ARIA Labels
```html
<!-- FAB with proper labeling -->
<button type="button"
        aria-label="Quick Actions Menu"
        aria-expanded="false"
        aria-haspopup="true">
    <i class="fas fa-bolt"></i>
</button>

<!-- Action with description -->
<a href="..."
   aria-label="Add new barangay OBC to the database">
    Add Barangay OBC
</a>
```

#### Touch Targets
- **Minimum Size**: 48x48px (WCAG 2.1 Level AAA: 44x44px)
- **FAB Button**: 56x56px (14/14 Tailwind units)
- **Spacing**: Minimum 8px gap between adjacent targets

### Best Practices

#### 1. Prioritize Actions
- **Most Common First**: Place frequently used actions at top/left
- **Primary vs Secondary**: Use visual hierarchy (size, color, position)
- **Limit Count**: Maximum 6 actions per section to avoid overwhelming users

#### 2. Clear Labels
- **Action Verbs**: "Create", "Manage", "Export", not "Click Here"
- **Context**: "Add Barangay OBC", not just "Add"
- **Consistent Language**: Same terms across similar actions

#### 3. Visual Feedback
```html
<!-- Hover lift effect -->
class="hover:-translate-y-1 transition-all duration-200"

<!-- Icon scale on hover -->
class="group-hover:scale-110 transition-transform"

<!-- Arrow slide on hover -->
class="group-hover:translate-x-1 transition-transform"
```

#### 4. Loading States
```html
<!-- Disabled state for processing actions -->
<button disabled class="opacity-50 cursor-not-allowed">
    <i class="fas fa-spinner fa-spin mr-2"></i>
    Processing...
</button>
```

#### 5. Responsive Behavior
```html
<!-- Mobile: Stack vertically -->
<div class="grid grid-cols-1 md:grid-cols-3">

<!-- Tablet: 2 columns -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">

<!-- FAB: Adjust position for mobile navigation -->
<div class="fixed bottom-20 sm:bottom-8 right-4 sm:right-8">
```

---

## Implementation Checklist

When implementing Quick Actions:

- [ ] **Pattern Selected**: Choose appropriate pattern for page type
- [ ] **Actions Prioritized**: Most common actions appear first
- [ ] **Icons Chosen**: Semantic, recognizable FontAwesome icons
- [ ] **Colors Applied**: Follow gradient guidelines for action types
- [ ] **Hover States**: All interactive states implemented
- [ ] **Keyboard Navigation**: Tab order logical, focus visible
- [ ] **ARIA Labels**: Screen reader support complete
- [ ] **Touch Targets**: Minimum 48x48px, adequate spacing
- [ ] **Responsive**: Mobile, tablet, desktop layouts tested
- [ ] **Permission Checks**: Actions respect user roles (`{% if user.is_staff %}`)
- [ ] **Context-Aware**: Actions relevant to current page/record
- [ ] **Loading States**: Disabled states for async actions

---

## Examples by Module

### Communities Module

**Home Page (Header Quick Actions):**
- Add Barangay OBC
- Add Municipal OBC
- Manage Barangay OBC
- View on Map

**Detail Page (Sidebar Quick Actions):**
- Edit Community Profile
- View MANA Assessments
- View Stakeholders
- Export Community Data

### Coordination Module

**Events List (Header Quick Actions):**
- Create Coordination Event
- Log Activity
- Export Coordination Data
- Calendar Management

**Partnership Detail (Sidebar Quick Actions):**
- View Milestones
- Manage Signatories
- Upload Documents
- View Organizations

### Project Management Portal Module

**Portfolio Dashboard (Sidebar Quick Actions):**
- Active Alerts
- Tracked Workflows
- Budget Approvals

**Workflow Detail (Floating FAB + Header):**
- Header: Add Activity, Create Task, View Calendar
- FAB: Save Progress, Preview, Help

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-03 | Initial release with 3 official patterns |

---

## References

- [OBCMS UI Components & Standards Guide](OBCMS_UI_COMPONENTS_STANDARDS.md)
- [Stat Card Template](../improvements/UI/STATCARD_TEMPLATE.md)
- [WCAG 2.1 AA Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [FontAwesome Icons](https://fontawesome.com/icons)

---

**Questions or need clarification?** Refer to existing implementations:
- Portfolio Dashboard (Sidebar): `src/templates/project_central/portfolio_dashboard.html`
- Communities Home (Header): `src/templates/communities/communities_home.html`
- Coordination Events (Compact Header): `src/templates/coordination/coordination_events.html`
