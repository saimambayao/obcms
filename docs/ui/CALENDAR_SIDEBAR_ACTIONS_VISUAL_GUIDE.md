# Calendar Sidebar Actions - Visual Guide

**Last Updated:** 2025-10-06

## Before & After Comparison

### BEFORE: Missing Action Buttons

```
┌─────────────────────────────────────────────┐
│  ✏️  Edit Event                    👁️ View   │
├─────────────────────────────────────────────┤
│                                             │
│  Title                                      │
│  ┌───────────────────────────────────────┐ │
│  │ Team Meeting                          │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Status           Priority                 │
│  ┌─────────┐     ┌─────────┐              │
│  │ Active  │     │ High    │              │
│  └─────────┘     └─────────┘              │
│                                             │
│  Start Date       Due Date                 │
│  ┌─────────┐     ┌─────────┐              │
│  │10/01/25 │     │10/15/25 │              │
│  └─────────┘     └─────────┘              │
│                                             │
│  Progress (%)                               │
│  ┌───────────────────────────────────────┐ │
│  │ 50                                    │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Description                                │
│  ┌───────────────────────────────────────┐ │
│  │ Weekly sync meeting...                │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Assign To                                  │
│  ┌───────────────────────────────────────┐ │
│  │ Alice, Bob                            │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ───────────────────────────────────────    │
│                                             │
│  ┌────────────────┐  ┌──────────────────┐  │
│  │ 💾 Save Changes│  │ ❌ Cancel        │  │
│  └────────────────┘  └──────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘

❌ Problem: No way to duplicate or delete from sidebar
```

---

### AFTER: With Action Buttons

```
┌─────────────────────────────────────────────┐
│  ✏️  Edit Event                    👁️ View   │
├─────────────────────────────────────────────┤
│                                             │
│  Title                                      │
│  ┌───────────────────────────────────────┐ │
│  │ Team Meeting                          │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Status           Priority                 │
│  ┌─────────┐     ┌─────────┐              │
│  │ Active  │     │ High    │              │
│  └─────────┘     └─────────┘              │
│                                             │
│  Start Date       Due Date                 │
│  ┌─────────┐     ┌─────────┐              │
│  │10/01/25 │     │10/15/25 │              │
│  └─────────┘     └─────────┘              │
│                                             │
│  Progress (%)                               │
│  ┌───────────────────────────────────────┐ │
│  │ 50                                    │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Description                                │
│  ┌───────────────────────────────────────┐ │
│  │ Weekly sync meeting...                │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Assign To                                  │
│  ┌───────────────────────────────────────┐ │
│  │ Alice, Bob                            │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ───────────────────────────────────────    │
│                                             │
│  ┌────────────────┐  ┌──────────────────┐  │
│  │ 💾 Save Changes│  │ ❌ Cancel        │  │  ← Primary actions
│  └────────────────┘  └──────────────────┘  │
│                                             │
│  ───────────────────────────────────────    │  ← Visual separator
│                                             │
│  ┌──────────────┐    ┌──────────────────┐  │
│  │ 📋 Duplicate │    │ 🗑️  Delete       │  │  ← NEW: Secondary actions
│  └──────────────┘    └──────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘

✅ Solution: Quick access to duplicate and delete
```

---

## User Flow Diagrams

### Duplicate Flow

```
┌─────────────────┐
│ User clicks     │
│ "Duplicate"     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Loading spinner │
│ "Duplicating..."│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend creates │
│ copy with       │
│ "(Copy)" suffix │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sidebar shows   │
│ edit form for   │
│ duplicated item │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calendar adds   │
│ new event       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Success toast:  │
│ "Duplicated as  │
│ 'Title (Copy)'" │
└─────────────────┘
```

**Total Time:** < 500ms

---

### Delete Flow

```
┌─────────────────┐
│ User clicks     │
│ "Delete"        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Browser shows   │
│ confirmation:   │
│ "⚠️ Delete?"     │
└────────┬────────┘
         │
         ├────── User clicks "Cancel" ──────┐
         │                                  │
         │                                  ▼
         │                          ┌─────────────────┐
         │                          │ Dialog closes   │
         │                          │ No action taken │
         │                          └─────────────────┘
         │
         ▼
┌─────────────────┐
│ User clicks "OK"│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DELETE request  │
│ sent to backend │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend deletes │
│ work item       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sidebar closes  │
│ automatically   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calendar        │
│ removes event   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Success toast:  │
│ "Work item      │
│ deleted"        │
└─────────────────┘
```

**Total Time:** < 200ms (after confirmation)

---

## Button States

### Duplicate Button

#### Default State
```
┌────────────────────────┐
│ 📋 Duplicate          │  Gray border, white bg
└────────────────────────┘
```

#### Hover State
```
┌────────────────────────┐
│ 📋 Duplicate          │  Darker gray border, light gray bg
└────────────────────────┘
↑ Cursor changes to pointer
```

#### Loading State
```
┌────────────────────────┐
│ ⏳ Duplicating...      │  Button disabled, spinner shows
└────────────────────────┘
↓ Below button:
🔄 Duplicating...
```

#### Success State
```
Sidebar content replaced with:

┌─────────────────────────────────────────────┐
│  ✏️  Edit Event                              │
├─────────────────────────────────────────────┤
│  Title                                      │
│  ┌───────────────────────────────────────┐ │
│  │ Team Meeting (Copy)  ← NEW TITLE     │ │
│  └───────────────────────────────────────┘ │
│  ...                                        │
└─────────────────────────────────────────────┘

+ Toast notification appears:
┌─────────────────────────────────────────────┐
│ ✅ Duplicated as "Team Meeting (Copy)"      │
└─────────────────────────────────────────────┘
```

---

### Delete Button

#### Default State
```
┌────────────────────────┐
│ 🗑️  Delete             │  Red bg, white text
└────────────────────────┘
```

#### Hover State
```
┌────────────────────────┐
│ 🗑️  Delete             │  Darker red bg
└────────────────────────┘
↑ Cursor changes to pointer
```

#### Confirmation Dialog
```
┌─────────────────────────────────────────────┐
│                                             │
│  ⚠️  Delete 'Team Meeting'?                 │
│                                             │
│  This action cannot be undone. The work    │
│  item and all its data will be             │
│  permanently deleted.                       │
│                                             │
│  Click OK to confirm deletion.              │
│                                             │
│  ┌──────┐                    ┌──────┐      │
│  │  OK  │                    │Cancel│      │
│  └──────┘                    └──────┘      │
│                                             │
└─────────────────────────────────────────────┘
```

#### Success State
```
Sidebar closes (slides out):

┌─────────────────────────────────────────────┐
│                                             │
│        [Sidebar animates closed]            │
│                                             │
└─────────────────────────────────────────────┘

+ Calendar event disappears
+ Toast notification appears:
┌─────────────────────────────────────────────┐
│ ✅ Work item deleted successfully            │
└─────────────────────────────────────────────┘
```

---

## Color Palette

### Duplicate Button (Neutral)
```css
/* Default */
background: #ffffff       /* White */
border: #d1d5db          /* Gray-300 */
text: #374151            /* Gray-700 */

/* Hover */
background: #f9fafb      /* Gray-50 */
border: #9ca3af          /* Gray-400 */

/* Icon */
color: #6b7280           /* Gray-500 */
```

### Delete Button (Destructive)
```css
/* Default */
background: #dc2626      /* Red-600 */
border: #dc2626          /* Red-600 */
text: #ffffff            /* White */

/* Hover */
background: #b91c1c      /* Red-700 */
border: #b91c1c          /* Red-700 */

/* Icon */
color: #ffffff           /* White */
```

### Success Toast
```css
background: linear-gradient(to right, #10b981, #059669)  /* Emerald-500 to Emerald-600 */
text: #ffffff            /* White */
```

### Error Toast
```css
background: linear-gradient(to right, #f43f5e, #e11d48)  /* Rose-500 to Rose-600 */
text: #ffffff            /* White */
```

---

## Responsive Behavior

### Desktop (> 1024px)
```
┌───────────────────────────────┐
│  [Save Changes]    [Cancel]   │  Full width buttons
├───────────────────────────────┤
│  [Duplicate]      [Delete]    │  Equal width (flex-1)
└───────────────────────────────┘
```

### Tablet (768px - 1024px)
```
┌───────────────────────────────┐
│  [Save Changes]    [Cancel]   │  Slightly narrower
├───────────────────────────────┤
│  [Duplicate]      [Delete]    │  Still side-by-side
└───────────────────────────────┘
```

### Mobile (< 768px)
```
┌─────────────────────┐
│  [Save Changes]     │  Full width
│  [Cancel]           │  Full width
├─────────────────────┤
│  [Duplicate]        │  Could stack if needed
│  [Delete]           │  (Currently side-by-side)
└─────────────────────┘
```

**Note:** Currently, buttons remain side-by-side on mobile. If more buttons are added, consider stacking them vertically.

---

## Accessibility Visual Indicators

### Keyboard Focus

```
Default (no focus):
┌────────────────────────┐
│ 📋 Duplicate          │
└────────────────────────┘

Focused (Tab key):
┌────────────────────────┐
│ 📋 Duplicate          │  ← Blue focus ring (3px)
└────────────────────────┘
```

### Screen Reader Announcement

```
When button is focused:
┌─────────────────────────────────────────────┐
│ Screen Reader Says:                         │
│ "Duplicate button"                          │
│ "Press Enter to duplicate this work item"   │
└─────────────────────────────────────────────┘

After clicking:
┌─────────────────────────────────────────────┐
│ Screen Reader Says:                         │
│ "Duplicating work item..."                  │
│ (Loading indicator)                         │
└─────────────────────────────────────────────┘

After success:
┌─────────────────────────────────────────────┐
│ Screen Reader Says:                         │
│ "Duplicated as 'Team Meeting (Copy)'"       │
│ (Success toast)                             │
└─────────────────────────────────────────────┘
```

---

## Error State Examples

### Permission Denied (Duplicate)

```
User clicks "Duplicate"
         ↓
┌─────────────────────────────────────────────┐
│ ❌ You do not have permission to duplicate   │
│    work items.                               │
└─────────────────────────────────────────────┘
         ↓
Red toast appears, auto-dismiss after 3s
```

### Permission Denied (Delete)

```
User clicks "Delete" → Confirms
         ↓
┌─────────────────────────────────────────────┐
│ ❌ You do not have permission to delete      │
│    this work item.                           │
└─────────────────────────────────────────────┘
         ↓
Red toast appears, auto-dismiss after 3s
```

### Network Error

```
User clicks button → Network fails
         ↓
┌─────────────────────────────────────────────┐
│ ❌ An error occurred. Please try again or    │
│    contact support.                          │
└─────────────────────────────────────────────┘
         ↓
Red toast appears, auto-dismiss after 3s
```

---

## Animation Timeline

### Duplicate Success Animation

```
0ms:    User clicks "Duplicate"
        ↓
50ms:   Loading spinner fades in
        ↓
100ms:  Button disabled (grayed out)
        ↓
300ms:  Backend responds
        ↓
350ms:  Sidebar content starts fade-out
        ↓
400ms:  New form content fades in
        ↓
450ms:  Calendar adds new event (slide-in)
        ↓
500ms:  Toast notification appears (slide-down)
        ↓
3500ms: Toast fades out
```

### Delete Success Animation

```
0ms:    User clicks "Delete"
        ↓
50ms:   Confirmation dialog appears
        ↓
[user confirms]
        ↓
100ms:  DELETE request sent
        ↓
150ms:  Backend responds
        ↓
200ms:  Sidebar slides out (300ms transition)
        ↓
250ms:  Calendar event fades out
        ↓
300ms:  Event removed from calendar
        ↓
350ms:  Toast notification appears
        ↓
3350ms: Toast fades out
```

---

## Print Stylesheet Behavior

### When Printing Sidebar

```css
@media print {
    /* Hide action buttons (not useful in print) */
    .sidebar-actions {
        display: none !important;
    }

    /* Show only form content */
    .sidebar-content {
        border: none;
        box-shadow: none;
    }
}
```

**Reasoning:** Print view should show only the data, not interactive elements.

---

## Dark Mode Support (Future)

### Light Mode (Current)
```
Duplicate: White bg, gray border
Delete:    Red-600 bg, white text
```

### Dark Mode (Planned)
```css
/* Duplicate button */
background: #1f2937      /* Gray-800 */
border: #374151          /* Gray-700 */
text: #f9fafb            /* Gray-50 */

/* Delete button */
background: #991b1b      /* Red-800 */
border: #991b1b          /* Red-800 */
text: #fef2f2            /* Red-50 */

/* Hover states */
Duplicate: #111827       /* Gray-900 */
Delete:    #7f1d1d       /* Red-900 */
```

---

## Visual Hierarchy

### Information Density

```
High Priority (Top):
│ Header: "Edit Event" │ View Details
│
Medium Priority (Middle):
│ Form Fields (Title, Status, Priority, etc.)
│
Low Priority (Bottom - separated by border):
│ Primary Actions: Save, Cancel
│ ─────────────────────────────
│ Secondary Actions: Duplicate, Delete
```

### Z-Index Layers

```
Layer 5: Toast notifications     (z-index: 9999)
Layer 4: Confirmation dialogs    (z-index: 9998)
Layer 3: Sidebar panel           (z-index: 1000)
Layer 2: Sidebar backdrop        (z-index: 999)
Layer 1: Calendar main view      (z-index: 1)
```

---

## End of Visual Guide

**See Also:**
- [Implementation Guide](../improvements/UI/CALENDAR_SIDEBAR_DUPLICATE_DELETE_IMPLEMENTATION.md)
- [Quick Reference](CALENDAR_SIDEBAR_ACTIONS_QUICK_REFERENCE.md)
