# Planning Module Visual Reference Guide

**Date:** 2025-10-13
**Purpose:** Visual component guide for Planning Module templates
**Compliance:** OBCMS UI Standards Master Guide v3.1

---

## Component Visual Reference

### 1. Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Planning Dashboard                                          │
│  Strategic and annual planning for OOBC operations              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ 🎯 Total │  │ ✅ Active│  │ 🚩 Goals │  │ 📅 Annual│      │
│  │    12    │  │     8    │  │    45    │  │     3    │      │
│  │  Plans   │  │  Plans   │  │ ┌────┐   │  │  Plans   │      │
│  │          │  │          │  │ │25│20│   │  │          │      │
│  │          │  │          │  │ └────┘   │  │          │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────┐     │
│  │ ➕ Create Strategic     │  │ 📋 View Annual Work     │     │
│  │    Plan                 │  │    Plans                │     │
│  │ Start new multi-year... │  │ Manage yearly plans...  │     │
│  └─────────────────────────┘  └─────────────────────────┘     │
│                                                                 │
│  🕐 Recent Activity                                             │
│  ├─ Strategic Plan 2024-2028 created • 2 hours ago            │
│  ├─ Goal "Improve Education" updated • 5 hours ago            │
│  └─ Annual Plan 2025 approved • 1 day ago                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Strategic Plans List Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 Strategic Plans                                             │
│  Multi-year strategic plans for OOBC operations                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Stat Cards Grid - Same as Dashboard]                         │
│                                                                 │
│  [All Plans] [Active] [Draft] [Archived]  ← Filter Buttons     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 📋 Strategic Plans                    [+ Create Plan]    │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────┐  [✅]  │  │
│  │  │ OOBC Strategic Plan 2024-2028               │ Active │  │
│  │  │ 2024-2028                                   │        │  │
│  │  │ ┌──────┬──────┬──────┐                     │        │  │
│  │  │ │ 5yrs │ 12   │ 67%  │                     │        │  │
│  │  │ └──────┴──────┴──────┘                     │        │  │
│  │  │ ████████████████▒▒▒▒▒▒▒ 67%               │        │  │
│  │  └─────────────────────────────────────────────┘        │  │
│  │                                                           │  │
│  │  [More plan cards...]                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Strategic Plan Detail Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 OOBC Strategic Plan 2024-2028                    [✅Active] │
│  2024-2028 (5 years)                                  [Edit]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐             │
│  │ 👁️ VISION          │  │ 🧭 MISSION          │             │
│  │ A prosperous...     │  │ To empower...       │             │
│  └─────────────────────┘  └─────────────────────┘             │
│                                                                 │
│  Overall Progress                                        67%    │
│  ████████████████▒▒▒▒▒▒▒▒                                      │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  🚩 Strategic Goals                          [+ Add Goal]       │
│                                                                 │
│  🔴 Critical Priority                                           │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │ Improve Education    │  │ Healthcare Access    │           │
│  │ Target: 20 schools   │  │ Target: 15 clinics   │           │
│  │ Progress: 75%        │  │ Progress: 60%        │           │
│  │ ████████▒▒           │  │ ██████▒▒▒▒           │           │
│  │ [✓Complete] [Edit]   │  │ [⏳Progress] [Edit]  │           │
│  └──────────────────────┘  └──────────────────────┘           │
│                                                                 │
│  🟠 High Priority                                               │
│  [Goal cards...]                                                │
│                                                                 │
│  📅 Annual Work Plans                    [+ Add Annual Plan]   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ OOBC Annual Work Plan 2024                      [✅]   │    │
│  │ 12 objectives • 67% complete                           │    │
│  │ ████████████▒▒▒▒▒▒                                     │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Strategic Plan Form Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  ➕ Create Strategic Plan                                       │
│  Create a new multi-year strategic plan for OOBC               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │  ℹ️ Basic Information                                     │  │
│  │                                                           │  │
│  │  Plan Title *                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ e.g., OOBC Strategic Plan 2024-2028              ▼ │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  Start Year *              End Year *                    │  │
│  │  ┌────────────┐            ┌────────────┐               │  │
│  │  │ 2024     ▼ │            │ 2028     ▼ │               │  │
│  │  └────────────┘            └────────────┘               │  │
│  │                                                           │  │
│  │  🧭 Vision and Mission                                    │  │
│  │                                                           │  │
│  │  Vision Statement *                                      │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ Describe the long-term vision...                    │ │  │
│  │  │                                                      │ │  │
│  │  │                                                      │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  Mission Statement *                                     │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ Describe the mission statement...                   │ │  │
│  │  │                                                      │ │  │
│  │  │                                                      │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  🔛 Plan Status                                           │  │
│  │                                                           │  │
│  │  Status *                                                │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ Select...                                         ▼ │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  ─────────────────────────────────────────────────────   │  │
│  │                                                           │  │
│  │                              [Cancel]  [Create Plan]     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Annual Plans List Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  📅 Annual Work Plans                                           │
│  Yearly operational plans and objectives                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [All Years] [2025] [2024] [2023]  ← Year Filter Buttons       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 📋 Annual Work Plans                  [+ Create Plan]    │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────┐  [✅]  │  │
│  │  │ OOBC Annual Work Plan 2025                  │ Active │  │
│  │  │ Year: 2025                                  │        │  │
│  │  │ Strategic Plan: OOBC Strategic Plan 24-28   │        │  │
│  │  │ ┌───────┬───────┬────────┐                 │        │  │
│  │  │ │ 12    │ 8     │ 67%    │                 │        │  │
│  │  │ │ Total │ Done  │ Prog   │                 │        │  │
│  │  │ └───────┴───────┴────────┘                 │        │  │
│  │  │ ████████████████▒▒▒▒▒▒▒ 67%               │        │  │
│  │  └─────────────────────────────────────────────┘        │  │
│  │                                                           │  │
│  │  [More plan cards...]                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 6. Annual Plan Detail Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  📅 OOBC Annual Work Plan 2025                       [✅Active] │
│  Year: 2025                                            [Edit]   │
│  Strategic Plan: OOBC Strategic Plan 2024-2028                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 📝 Description                                           │  │
│  │ This annual plan focuses on...                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Overall Progress                                        67%    │
│  ████████████████▒▒▒▒▒▒▒▒                                      │
│  8 of 12 objectives completed                                  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ✅ Work Plan Objectives                     [+ Add Objective] │
│                                                                 │
│  🔵 In Progress (3)                                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Build 5 new classrooms in Lanao del Sur OBCs          │    │
│  │ Target: Dec 31, 2025                                  │    │
│  │ Progress: 60%                                         │    │
│  │ ██████▒▒▒▒                                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ⚪ Not Started (1)                                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Conduct community consultation                        │    │
│  │ Target: Jun 30, 2025                                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ✅ Completed (8)                                               │
│  [Completed objective cards...]                                │
│                                                                 │
│  🔗 Linked M&E Programs                                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Education Infrastructure Program                       │    │
│  │ Build schools and classrooms in OBCs...               │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Color Reference

### Status Badge Colors

```
Active:      ┌─────────────┐
            │ ✅ Active   │ ← bg-emerald-100 text-emerald-800
            └─────────────┘

Draft:       ┌─────────────┐
            │ ✏️ Draft    │ ← bg-gray-100 text-gray-800
            └─────────────┘

Approved:    ┌─────────────┐
            │ 👍 Approved │ ← bg-blue-100 text-blue-800
            └─────────────┘

Archived:    ┌─────────────┐
            │ 📦 Archived │ ← bg-amber-100 text-amber-800
            └─────────────┘

Completed:   ┌─────────────┐
            │ ✓✓ Complete │ ← bg-blue-100 text-blue-800
            └─────────────┘
```

### Priority Badge Colors

```
Critical:    ┌─────────────┐
            │ ❗ Critical │ ← bg-red-100 text-red-800
            └─────────────┘

High:        ┌─────────────┐
            │ ⬆️ High     │ ← bg-orange-100 text-orange-800
            └─────────────┘

Medium:      ┌─────────────┐
            │ ➖ Medium   │ ← bg-blue-100 text-blue-800
            └─────────────┘

Low:         ┌─────────────┐
            │ ⬇️ Low      │ ← bg-gray-100 text-gray-800
            └─────────────┘
```

### Progress Bar Colors

```
Emerald (Success):
████████████████▒▒▒▒▒▒▒▒  ← bg-emerald-600

Blue (Info):
████████████████▒▒▒▒▒▒▒▒  ← bg-blue-600

Purple (Annual):
████████████████▒▒▒▒▒▒▒▒  ← bg-purple-600

Amber (Warning):
████████████████▒▒▒▒▒▒▒▒  ← bg-amber-600
```

### Icon Colors (Stat Cards)

```
🎯 Total/General    → text-amber-600
✅ Success/Complete → text-emerald-600
🚩 Info/Process     → text-blue-600
📅 Draft/Proposed   → text-purple-600
⚠️ Warning          → text-orange-600
🔴 Critical         → text-red-600
```

---

## Responsive Breakpoints

### Mobile (< 768px)

```
┌─────────────┐
│ Stat Card 1 │
└─────────────┘

┌─────────────┐
│ Stat Card 2 │
└─────────────┘

┌─────────────┐
│ Stat Card 3 │
└─────────────┘

┌─────────────┐
│ Stat Card 4 │
└─────────────┘

grid-cols-1
```

### Tablet (768px - 1023px)

```
┌─────────────┐  ┌─────────────┐
│ Stat Card 1 │  │ Stat Card 2 │
└─────────────┘  └─────────────┘

┌─────────────┐  ┌─────────────┐
│ Stat Card 3 │  │ Stat Card 4 │
└─────────────┘  └─────────────┘

md:grid-cols-2
```

### Desktop (≥ 1024px)

```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│  Card 1 │  │  Card 2 │  │  Card 3 │  │  Card 4 │
└─────────┘  └─────────┘  └─────────┘  └─────────┘

lg:grid-cols-4
```

---

## Touch Target Specifications

### Minimum Sizes (WCAG 2.1 AA)

```
Button:
┌──────────────────────────┐
│   [Edit Plan]            │ ← min-h-[48px]
└──────────────────────────┘
         48px × 48px minimum

Input Field:
┌──────────────────────────┐
│ Plan Title...            │ ← min-h-[48px]
└──────────────────────────┘
         Full width × 48px height

Filter Button:
┌─────────────┐
│ [All Plans] │ ← px-4 py-2 (48px touch area)
└─────────────┘
```

---

## Animation Timing

### Hover Effects

```
Transform Duration:    300ms
Opacity Duration:      200ms
Color Duration:        200ms
Shadow Duration:       300ms

Example:
.stat-card:hover {
    transform: translateY(-8px);      /* 300ms */
    box-shadow: 0 20px 40px ...;      /* 300ms */
    transition: all 0.3s ease;
}

.filter-button:hover {
    background-color: gray-200;        /* 200ms */
    transition: colors 0.2s ease;
}
```

### Progress Bars

```
Width Transition:      300ms ease

████████▒▒▒▒  →  ████████████▒▒
   50%              75%

<div style="width: {{ percentage }}%; transition: width 0.3s ease"></div>
```

---

## Empty States

### Strategic Plans Empty State

```
┌─────────────────────────────────────────┐
│                                         │
│            🎯                           │
│           (huge)                        │
│                                         │
│      No Strategic Plans Yet             │
│                                         │
│  Create your first strategic plan       │
│         to get started                  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ + Create Strategic Plan         │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Goals Empty State

```
┌─────────────────────────────────────────┐
│                                         │
│            🚩                           │
│          (medium)                       │
│                                         │
│    No strategic goals defined yet       │
│                                         │
│        + Add first goal                 │
│                                         │
└─────────────────────────────────────────┘
```

---

## Button Styles

### Primary Button (Gradient)

```
┌────────────────────────────────────┐
│  ➕ Create Strategic Plan         │  ← Blue-to-Emerald Gradient
└────────────────────────────────────┘
bg-gradient-to-r from-blue-600 to-emerald-600
hover:shadow-lg hover:-translate-y-1
```

### Secondary Button (Outline)

```
┌────────────────────────────────────┐
│  ❌ Cancel                         │  ← Gray Border
└────────────────────────────────────┘
border-2 border-gray-300 text-gray-700
hover:bg-gray-50
```

### Filter Button (Active)

```
┌─────────────┐
│ All Plans   │  ← Blue-to-Emerald Gradient
└─────────────┘
bg-gradient-to-r from-blue-600 to-emerald-600 text-white
```

### Filter Button (Inactive)

```
┌─────────────┐
│ All Plans   │  ← Light Gray
└─────────────┘
bg-gray-100 text-gray-700 hover:bg-gray-200
```

---

## Form Field Visual Guide

### Text Input

```
Plan Title *
┌─────────────────────────────────────────────┐
│ e.g., OOBC Strategic Plan 2024-2028         │
└─────────────────────────────────────────────┘
rounded-xl, border-gray-200, min-h-[48px]
```

### Dropdown with Chevron

```
Status *
┌─────────────────────────────────────────────┐
│ Select...                                 ▼ │
└─────────────────────────────────────────────┘
rounded-xl, border-gray-200, appearance-none
Chevron: pointer-events-none, absolute right-0
```

### Textarea

```
Description
┌─────────────────────────────────────────────┐
│ Overview of annual priorities and approach  │
│                                             │
│                                             │
│                                             │
└─────────────────────────────────────────────┘
rounded-xl, border-gray-200, rows="4"
```

### Error State

```
Plan Title *
┌─────────────────────────────────────────────┐
│                                             │ ← Red border
└─────────────────────────────────────────────┘
❌ This field is required
    ↑ Red text (text-red-600)
```

---

## Spacing Standards

```
Between Sections:        mb-6  (24px)
Between Cards:           gap-6 (24px)
Card Padding:            p-6   (24px)
Stat Card Padding:       p-6   (24px)
Form Field Margin:       mb-4  (16px)
Input Padding:           px-4 py-3 (16px/12px)
Button Padding:          px-6 py-3 (24px/12px)
Icon Margin:             mr-2 or mr-3 (8px/12px)
```

---

## Icon Reference

### Planning Module Icons

```
Dashboard:           fa-bullseye
Strategic Plans:     fa-bullseye
Goals:               fa-flag
Annual Plans:        fa-calendar-alt
Objectives:          fa-tasks
Progress:            fa-chart-line
Create/Add:          fa-plus
Edit:                fa-edit
View:                fa-eye
Delete:              fa-trash
Active:              fa-check-circle
Draft:               fa-pencil-alt
Approved:            fa-thumbs-up
Archived:            fa-archive
Completed:           fa-check-double
In Progress:         fa-spinner
Not Started:         fa-circle
Deferred:            fa-pause
Critical Priority:   fa-exclamation-circle
High Priority:       fa-arrow-up
Medium Priority:     fa-minus
Low Priority:        fa-arrow-down
Link:                fa-link
Info:                fa-info-circle
Calendar:            fa-calendar
Clock:               fa-clock
```

---

## Quick Reference Checklist

### When Creating New Templates

- [ ] Extends `base.html`
- [ ] Includes breadcrumb navigation
- [ ] Uses 3D milk white stat cards (if applicable)
- [ ] Applies semantic icon colors
- [ ] Implements responsive grid (1/2/4 columns)
- [ ] Sets touch targets min-h-[48px]
- [ ] Uses rounded-xl for inputs/buttons
- [ ] Applies emerald-500 focus rings
- [ ] Includes empty states with CTAs
- [ ] Shows loading/error states
- [ ] Has ARIA labels on interactive elements
- [ ] Follows WCAG 2.1 AA color contrast
- [ ] Uses Font Awesome icons consistently

---

**Document Owner:** UI/UX Team
**Last Updated:** 2025-10-13
**Status:** ✅ Visual Reference Complete
