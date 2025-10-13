# RBAC Frontend Visual Guide

**Quick Reference for RBAC UI Components**

---

## Page Structure

```
User Management Page
├── Header ("User Management")
├── Tab Navigation
│   ├── [User Approvals] (default active)
│   └── [Permissions & Roles]
└── Tab Content
    ├── User Approvals Content (existing)
    └── Permissions & Roles Content (new RBAC dashboard)
```

---

## Component Hierarchy

```
RBAC Dashboard
│
├── Stat Cards (4-column grid)
│   ├── Total Users (amber icon)
│   ├── Active Roles (blue icon)
│   ├── Pending Assignments (purple icon)
│   └── Feature Toggles (emerald icon)
│
├── Search & Filter Controls
│   ├── Search input (live search, 500ms delay)
│   ├── User Type dropdown
│   └── Organization dropdown
│
├── Bulk Actions Bar
│   ├── Select All checkbox
│   ├── Selected count
│   ├── Bulk Assign Role button
│   └── Bulk Remove Roles button
│
└── Users Grid Table
    ├── Checkbox column
    ├── User column (avatar + name + email)
    ├── User Type column (badge)
    ├── Organization column
    ├── Roles column (purple badges)
    └── Actions column (Permissions + Assign Role buttons)
```

---

## Modal Components

### 1. User Permissions Modal

```
┌─────────────────────────────────────────────────────┐
│ [🔒] User Permissions                          [×]  │
│     John Doe (john@example.com)                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ℹ️ User Type: Staff | Organization: OOBC           │
│                                                     │
│ 🛡️ Assigned Roles                      [+ Add Role] │
│ ┌─────────────────────────────────┐                │
│ │ [👑] Admin Role                │ [🗑️ Remove]     │
│ │     Full system access          │                │
│ └─────────────────────────────────┘                │
│                                                     │
│ 🔀 Feature Access Matrix                           │
│ ┌─────────────────────────────────────────┐        │
│ │ 📊 Dashboard Access                [ON]  │        │
│ │ 👥 User Management                 [OFF] │        │
│ │ 🏛️ Community Management            [ON]  │        │
│ └─────────────────────────────────────────┘        │
│                                                     │
│ 🔑 Direct Permissions                              │
│ ┌──────────────┐ ┌──────────────┐                 │
│ │ View Reports │ │ Edit Settings│                 │
│ └──────────────┘ └──────────────┘                 │
│                                                     │
│                               [Grant Permission]    │
└─────────────────────────────────────────────────────┘
```

### 2. Role Assignment Form

```
┌─────────────────────────────────────────────────────┐
│ [🛡️] Assign Role                              [×]  │
│     John Doe                                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Role *                                              │
│ ┌─────────────────────────────────────────┐        │
│ │ Admin (15 permissions)              [▼] │        │
│ └─────────────────────────────────────────┘        │
│ Full system access with all permissions             │
│                                                     │
│ Organization Context (Optional)                     │
│ ┌─────────────────────────────────────────┐        │
│ │ All Organizations                   [▼] │        │
│ └─────────────────────────────────────────┘        │
│                                                     │
│ 📅 Validity Period (Optional)                      │
│ ┌──────────────────┐ ┌──────────────────┐         │
│ │ Valid From       │ │ Valid Until      │         │
│ └──────────────────┘ └──────────────────┘         │
│                                                     │
│ Notes                                               │
│ ┌─────────────────────────────────────────┐        │
│ │ [text area]                             │        │
│ └─────────────────────────────────────────┘        │
│                                                     │
│                     [Cancel] [Assign Role]          │
└─────────────────────────────────────────────────────┘
```

### 3. Feature Toggle Matrix

```
┌─────────────────────────────────────────────────────────┐
│ Feature Access Matrix: John Doe                         │
├────────────┬──────────┬──────────────────────────────┐  │
│ Feature    │ Access   │ Source                       │  │
├────────────┼──────────┼──────────────────────────────┤  │
│ 📊 Dashboard│  [ON]   │ [🛡️ Role]                    │  │
│ Overview    │         │                              │  │
├────────────┼──────────┼──────────────────────────────┤  │
│ 👥 User     │  [OFF]  │ [🚫 Disabled]                │  │
│ Management  │         │                              │  │
├────────────┼──────────┼──────────────────────────────┤  │
│ 🏛️ Communities│ [ON]  │ [👤 Direct]                  │  │
│ Module      │         │                              │  │
└────────────┴──────────┴──────────────────────────────┘  │
│                                                         │
│ Legend: [ON] = Enabled | [OFF] = Disabled              │
│         [🛡️ Role] = From role | [👤 Direct] = Direct   │
└─────────────────────────────────────────────────────────┘
```

### 4. Permission Details Panel (Accordion)

```
┌─────────────────────────────────────────────────────┐
│ Permission Details: Admin Role                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ▼ [📊] Dashboard (5 permissions)                   │
│   ┌──────────────┐ ┌──────────────┐               │
│   │ View Stats   │ │ Export Data  │               │
│   └──────────────┘ └──────────────┘               │
│                                                     │
│ ▶ [👥] User Management (8 permissions)             │
│                                                     │
│ ▶ [🏛️] Communities (12 permissions)                │
│                                                     │
├─────────────────────────────────────────────────────┤
│      15          5           8           2          │
│     Total       View       Create       Edit       │
└─────────────────────────────────────────────────────┘
```

### 5. Bulk Assign Modal

```
┌─────────────────────────────────────────────────────┐
│ [👥] Bulk Role Assignment                      [×] │
│     Assign role to 3 selected users                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ℹ️ Selected Users (3)                              │
│ [John Doe] [Jane Smith] [Bob Johnson]              │
│                                                     │
│ Role to Assign *                                    │
│ ┌─────────────────────────────────────────┐        │
│ │ Staff Member (8 permissions)        [▼] │        │
│ └─────────────────────────────────────────┘        │
│                                                     │
│ ⚙️ Assignment Options                              │
│ ☑️ Replace existing roles                          │
│ ☑️ Send email notification                         │
│                                                     │
│ ⚠️ Important                                        │
│ This will affect 3 users. Review carefully.        │
│                                                     │
│                     [Cancel] [Assign to 3 Users]    │
└─────────────────────────────────────────────────────┘
```

---

## Color Reference

### Stat Card Icons
```
Total Users       → text-amber-600    (🟠)
Active Roles      → text-blue-600     (🔵)
Pending           → text-purple-600   (🟣)
Feature Toggles   → text-emerald-600  (🟢)
```

### Role/Permission Badges
```
Role Badge        → bg-purple-100 text-purple-800  (🟣)
User Type Badge   → bg-blue-100 text-blue-800      (🔵)
```

### Permission Type Badges
```
View              → bg-blue-100 text-blue-800      (eye icon)
Create            → bg-emerald-100 text-emerald-800 (plus icon)
Edit              → bg-amber-100 text-amber-800    (edit icon)
Delete            → bg-red-100 text-red-800        (trash icon)
Other             → bg-purple-100 text-purple-800  (cog icon)
```

### Toggle States
```
Enabled           → bg-emerald-600  (green)
Disabled          → bg-gray-300     (gray)
```

### Alert Banners
```
Info              → bg-blue-50 border-l-4 border-blue-500
Warning           → bg-amber-50 border-l-4 border-amber-500
Error             → bg-red-50 border-l-4 border-red-500
Success           → bg-emerald-50 border-l-4 border-emerald-500
```

---

## HTMX Interaction Flows

### 1. Tab Switching (JavaScript)
```
User clicks "Permissions & Roles" tab
    ↓
JavaScript: showTab('permissions')
    ↓
Hide #approvals-content
    ↓
Show #permissions-content
    ↓
HTMX triggers: hx-trigger="load once"
    ↓
GET /rbac/ → dashboard.html
    ↓
Swap into #permissions-content
```

### 2. Live Search
```
User types in search input
    ↓
HTMX waits 500ms (delay)
    ↓
GET /rbac/users/list/?search=john&user_type=staff
    ↓
Include #user-type-filter, #organization-filter
    ↓
Swap #users-grid with results
```

### 3. Feature Toggle
```
User clicks toggle switch
    ↓
POST /rbac/user/{id}/features/{feature_id}/toggle/
    ↓
Show loading spinner (#indicator)
    ↓
Backend toggles feature
    ↓
Return 204 No Content OR updated row HTML
    ↓
Hide spinner, update toggle visual
```

### 4. Role Assignment
```
User clicks "Assign Role" button
    ↓
GET /rbac/user/{id}/roles/assign-form/
    ↓
Swap into #rbac-modal-content
    ↓
openRbacModal() (JavaScript)
    ↓
User fills form, clicks "Assign Role"
    ↓
POST /rbac/user/{id}/roles/assign/
    ↓
Return updated permissions modal HTML
    ↓
Swap #rbac-modal-content
```

### 5. Bulk Assignment
```
User selects multiple checkboxes
    ↓
JavaScript: updateSelectedCount()
    ↓
Show #bulk-actions bar
    ↓
User clicks "Assign Role"
    ↓
GET /rbac/bulk-assign-form/?user_ids=1,2,3
    ↓
Swap into #rbac-modal-content
    ↓
openRbacModal()
    ↓
User submits form
    ↓
POST /rbac/bulk-assign/
    ↓
Return updated #users-grid HTML
    ↓
Close modal, clear checkboxes
```

---

## Responsive Breakpoints

### Mobile (< 768px)
```
- Stat cards: 1 column
- Search/filters: Stack vertically
- Table: Horizontal scroll
- Buttons: Full width, stacked
- Modal: Full screen
```

### Tablet (768px - 1024px)
```
- Stat cards: 2 columns
- Search/filters: 2 columns
- Table: Condensed columns
- Buttons: Inline with space-x-2
- Modal: 90% width
```

### Desktop (>= 1024px)
```
- Stat cards: 4 columns
- Search/filters: 3 columns inline
- Table: Full columns visible
- Buttons: Inline with space-x-3
- Modal: Max-w-4xl centered
```

---

## Keyboard Navigation

```
Tab         → Move to next interactive element
Shift+Tab   → Move to previous element
Enter       → Activate button/toggle
Space       → Check/uncheck checkbox
Escape      → Close modal
Arrow Keys  → Navigate accordions (native)
```

---

## Loading States

### HTMX Indicators
```html
<!-- Spinner -->
<i class="fas fa-spinner fa-spin htmx-indicator"></i>

<!-- Button loading -->
<button hx-indicator="#loading">
    <span id="loading" class="htmx-indicator">
        <i class="fas fa-spinner fa-spin"></i>
    </span>
    Save
</button>

<!-- Dashboard loading -->
<div class="text-center py-12">
    <i class="fas fa-spinner fa-spin text-4xl text-blue-600"></i>
    <p>Loading RBAC dashboard...</p>
</div>
```

---

## Empty States

### No Users
```
┌─────────────────────────┐
│     [👥 icon]           │
│  No users found         │
│  matching your criteria │
└─────────────────────────┘
```

### No Roles
```
┌─────────────────────────┐
│     [👑 icon]           │
│  No roles assigned      │
│  to this user           │
└─────────────────────────┘
```

### No Features
```
┌─────────────────────────┐
│     [🔀 icon]           │
│  No features available  │
│  for toggle             │
└─────────────────────────┘
```

---

## Animation Timing

```
Hover effects     → duration-200  (200ms)
Tab transitions   → duration-300  (300ms)
Modal open/close  → duration-300  (300ms)
Toggle switches   → duration-300  (300ms)
HTMX swaps        → swap:300ms
Delete swaps      → delete swap:200ms
```

---

## Quick Copy-Paste Snippets

### Toggle Switch
```html
<label class="relative inline-flex items-center cursor-pointer">
    <input type="checkbox" class="sr-only peer">
    <div class="w-11 h-6 bg-gray-200 rounded-full peer-checked:bg-emerald-600">
        <div class="bg-white rounded-full h-5 w-5 peer-checked:translate-x-5"></div>
    </div>
</label>
```

### Permission Badge
```html
<span class="px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
    <i class="fas fa-eye mr-1"></i>View
</span>
```

### User Avatar
```html
<div class="h-10 w-10 bg-gradient-to-br from-blue-500 to-emerald-500 rounded-full flex items-center justify-center text-white font-bold">
    {{ user.first_name.0|upper }}
</div>
```

### HTMX Button
```html
<button hx-get="/rbac/user/{{ user.id }}/permissions/"
        hx-target="#rbac-modal-content"
        hx-swap="innerHTML"
        onclick="openRbacModal()">
    Permissions
</button>
```

---

**Last Updated:** 2025-10-13
**Status:** ✅ Visual Reference Complete
