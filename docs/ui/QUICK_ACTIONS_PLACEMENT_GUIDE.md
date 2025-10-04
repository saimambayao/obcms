# Quick Actions - Placement & Integration Guide

**Quick Reference for Developers**
**Date:** 2025-10-03

---

## 1. Task Board - FAB Quick Actions

### Where to Place
**File:** `/src/templates/common/staff_task_board.html`

### Placement Instructions

**Step 1:** Add Alpine.js to base template (if not present)
```django
{# base.html - in <head> section #}
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

**Step 2:** Include FAB at end of content block
```django
{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-10">
    <!-- Existing header -->
    <!-- Existing metrics cards -->
    <!-- Existing filters -->
    <!-- Existing task board/table -->
</div>

{# Add FAB Quick Actions - BEFORE {% endblock %} #}
{% include "common/partials/task_board_quick_actions.html" %}
{% endblock %}
```

### Visual Result
```
┌─────────────────────────────────────┐
│  Staff Task Board Header            │
├─────────────────────────────────────┤
│  [Metrics Cards Row]                │
├─────────────────────────────────────┤
│  [Filters Panel]                    │
├─────────────────────────────────────┤
│  [Task Board / Table]               │
│                                     │
│                                     │
│                          ┌────┐     │ ← FAB Button
│                          │ ⚡ │     │   (bottom-right)
│                          └────┘     │
└─────────────────────────────────────┘
```

---

## 2. Task Modal - Inline Quick Actions

### Where to Place
**File:** `/src/templates/common/partials/staff_task_modal.html`

### Placement Instructions

**Find this section (around line 62):**
```django
<div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full">
    <div class="flex items-start justify-between px-6 py-5 border-b border-gray-200">
        <!-- Modal header with task title, badges -->
    </div>

    {# INSERT QUICK ACTIONS HERE - AFTER HEADER, BEFORE BODY #}
    {% include "common/partials/task_modal_quick_actions.html" %}

    <div class="px-6 py-5 space-y-6" id="taskModalBody">
        <!-- Existing form content -->
    </div>
</div>
```

### Visual Result
```
┌────────────────────────────────────────┐
│  Task Title                      [×]   │ ← Header
├────────────────────────────────────────┤
│ [✓ Complete] [👤 Assign] [⚡ Priority] │ ← Quick Actions Bar
│ [📅 Due Date] [📋 Clone]               │
├────────────────────────────────────────┤
│  Task Details                          │ ← Modal Body
│  [Form Fields]                         │
│                                        │
│  [Save Changes]                        │
└────────────────────────────────────────┘
```

---

## 3. Barangay Detail - Sidebar Quick Actions

### Where to Place
**File:** `/src/templates/communities/provincial_view.html` (or barangay detail view)

### Placement Instructions

**Modify layout to use grid (around line 34):**
```django
{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Existing header section -->

    {# CHANGE: Wrap content in grid layout #}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main content - 2/3 width -->
        <div class="lg:col-span-2 space-y-6">
            <!-- Existing stats cards -->
            <!-- Existing map -->
            <!-- Existing tables -->
        </div>

        <!-- Sidebar - 1/3 width -->
        <div class="lg:col-span-1">
            {% include "communities/partials/barangay_detail_quick_actions.html" %}
        </div>
    </div>
</div>
{% endblock %}
```

### Visual Result (Desktop)
```
┌────────────────────────────────────────────────────────────┐
│  Barangay OBC Detail Header                                │
├─────────────────────────────────┬──────────────────────────┤
│  Main Content (2/3)             │  Sidebar (1/3)           │
│                                 │  ┌──────────────────┐    │
│  [Stats Cards]                  │  │ QUICK ACTIONS    │    │
│                                 │  ├──────────────────┤    │
│  [Map View]                     │  │ ✏️ Edit Community │    │
│                                 │  │ ✅ Add MANA      │    │
│  [Municipal Coverage Table]     │  │ 📅 Log Activity  │    │
│                                 │  │ 💡 Recommend     │    │
│  [Barangay OBCs Table]          │  │ 📊 Demographics  │    │
│                                 │  │ 📄 Generate PDF  │    │
│                                 │  ├──────────────────┤    │
│                                 │  │ QUICK STATS      │    │
│                                 │  └──────────────────┘    │
└─────────────────────────────────┴──────────────────────────┘
```

### Visual Result (Mobile)
```
┌──────────────────────┐
│  Header              │
├──────────────────────┤
│ QUICK ACTIONS        │ ← Sidebar stacks on top
│ [All 6 actions]      │
├──────────────────────┤
│  Stats Cards         │
│  Map View            │
│  Tables              │
└──────────────────────┘
```

---

## 4. Communities List - Header Quick Actions

### Where to Place
**File:** `/src/templates/communities/communities_manage.html`

### Placement Instructions

**Replace existing header section (around line 19-54):**
```django
{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    {# REPLACE entire header section with: #}
    {% include "communities/partials/communities_list_quick_actions.html" %}

    <!-- Existing statistics cards -->
    <!-- Existing filters -->
    <!-- Existing communities table -->
</div>
{% endblock %}
```

**OR use as reference to enhance existing header:**
```django
{# Keep existing header structure, add enhanced buttons from partial #}
<div class="mb-8 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
    <div>
        <h1>...</h1>
    </div>
    <div class="flex flex-wrap items-center gap-3">
        {# Copy button markup from communities_list_quick_actions.html #}
        <a href="..." class="inline-flex items-center bg-gradient-to-r from-blue-600 to-teal-600 ...">
            <i class="fas fa-plus mr-2"></i>Add Community
        </a>
        <!-- Add other enhanced buttons -->
    </div>
</div>
```

### Visual Result
```
┌─────────────────────────────────────────────────────────────┐
│  Manage Barangay OBC                                        │
│  View, edit, and manage barangay-level OBC communities      │
│                                                             │
│  [➕ Add]  [📥 Import]  [⬇️ Export ▾]  [📊 Reports ▾]       │ ← Enhanced Header
│  [🗺️ Map]  [📁 Archived]                                    │
├─────────────────────────────────────────────────────────────┤
│  [Statistics Cards]                                         │
├─────────────────────────────────────────────────────────────┤
│  [Filters Panel]                                            │
├─────────────────────────────────────────────────────────────┤
│  [Communities Table]                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Files Reference

### Created Component Templates (Reusable)

```
src/templates/components/
├── quick_actions_fab.html          # Generic FAB component
├── quick_actions_sidebar.html      # Generic sidebar component
└── quick_actions_inline.html       # Generic inline component
```

### Created Partial Templates (Page-Specific)

```
src/templates/common/partials/
├── task_board_quick_actions.html   # Task Board FAB implementation
└── task_modal_quick_actions.html   # Task Modal inline implementation

src/templates/communities/partials/
├── barangay_detail_quick_actions.html      # Barangay sidebar implementation
└── communities_list_quick_actions.html     # Communities header implementation
```

---

## Integration Checklist

### Task Board FAB
- [ ] Alpine.js loaded in base.html
- [ ] Include partial before `{% endblock %}`
- [ ] Test FAB opens/closes
- [ ] Test all 4 quick actions work
- [ ] Test ESC key closes menu

### Task Modal Inline
- [ ] Include partial after modal header
- [ ] Test "Mark Complete" updates status
- [ ] Test "Assign to Me" adds user
- [ ] Test "Change Priority" dropdown
- [ ] Test "Set Due Date" focuses input
- [ ] Test "Clone Task" (after backend implemented)
- [ ] Test toast notifications appear

### Barangay Detail Sidebar
- [ ] Wrap content in grid layout (lg:grid-cols-3)
- [ ] Main content in lg:col-span-2
- [ ] Sidebar in lg:col-span-1
- [ ] Include partial in sidebar column
- [ ] Test all 6 action links
- [ ] Test "View Demographics" scroll
- [ ] Test sticky positioning on scroll
- [ ] Test responsive mobile view

### Communities List Header
- [ ] Replace or enhance existing header
- [ ] Include partial or copy button markup
- [ ] Test all action buttons
- [ ] Test Export dropdown (3 formats)
- [ ] Test Reports dropdown (3 types)
- [ ] Test Bulk Import modal opens/closes
- [ ] Test file upload zone (drag-drop)
- [ ] Test archived toggle

---

## Color & Style Reference

### Quick Actions Color Mapping

| Action Type | Color | Tailwind Class | Use Case |
|-------------|-------|----------------|----------|
| Primary | Blue | `from-blue-600 to-teal-600` | Main actions, navigation |
| Success | Emerald | `from-emerald-600 to-teal-600` | Confirmations, completions |
| Create | Indigo | `border-indigo-500 text-indigo-600` | Add, create new |
| Edit | Purple | `border-purple-500 text-purple-600` | Modify, update |
| Warning | Amber | `border-amber-500 text-amber-600` | Review, attention needed |
| Delete | Rose | `border-rose-500 text-rose-600` | Destructive actions |

### Button Variants

**Gradient (Primary):**
```html
<a class="bg-gradient-to-r from-blue-600 to-teal-600 text-white px-4 py-2.5 rounded-xl">
```

**Outline (Secondary):**
```html
<button class="border-2 border-emerald-500 text-emerald-600 hover:bg-emerald-50 px-4 py-2.5 rounded-xl">
```

**Icon Button:**
```html
<div class="w-10 h-10 rounded-lg bg-blue-100 text-blue-600 hover:bg-blue-600 hover:text-white">
    <i class="fas fa-icon"></i>
</div>
```

---

## Testing Instructions

### Manual Testing Steps

1. **FAB Quick Actions (Task Board)**
   ```
   - Navigate to /oobc-management/staff/tasks/
   - Look for floating button (bottom-right)
   - Click to open menu
   - Test each action:
     ✓ Quick Filters scrolls to filter section
     ✓ Bulk Operations shows alert (placeholder)
     ✓ Export Tasks downloads CSV
     ✓ View Analytics navigates to dashboard
   - Press ESC to close menu
   ```

2. **Inline Quick Actions (Task Modal)**
   ```
   - Open any task from task board
   - Look for action bar below header
   - Test each action:
     ✓ Mark Complete sets status to "completed"
     ✓ Assign to Me adds current user
     ✓ Change Priority opens dropdown
     ✓ Set Due Date focuses date input
     ✓ Clone Task creates duplicate (after backend)
   - Check toast notifications appear
   ```

3. **Sidebar Quick Actions (Barangay Detail)**
   ```
   - Navigate to barangay detail view
   - Check sidebar appears on right (desktop)
   - Test each action:
     ✓ Edit Community navigates to edit form
     ✓ Add MANA Assessment opens assessment form
     ✓ Log Activity opens event creation
     ✓ Create Recommendation opens policy form
     ✓ View Demographics scrolls to section
     ✓ Generate Profile downloads PDF
   - Scroll page - verify sidebar is sticky
   - Resize to mobile - verify sidebar stacks on top
   ```

4. **Header Quick Actions (Communities List)**
   ```
   - Navigate to /communities/manage/
   - Check enhanced header buttons
   - Test each action:
     ✓ Add Community navigates to add form
     ✓ Bulk Import opens modal
     ✓ Export Data shows dropdown (CSV, Excel, PDF)
     ✓ Reports shows dropdown (3 report types)
     ✓ Map View toggles map visualization
     ✓ Archived toggles archived view
   - Test bulk import modal:
     ✓ Opens on click
     ✓ Drag-drop zone visible
     ✓ Template download link works
     ✓ File selection works
     ✓ Close on backdrop click
   ```

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| FAB menu not opening | Check Alpine.js is loaded (`console.log(window.Alpine)`) |
| Toast not showing | Verify `task_modal_quick_actions.html` includes `<script>` tag |
| Sidebar not sticky | Ensure parent has `grid` layout with correct columns |
| Export 404 error | Implement backend view for export format handling |
| Clone button fails | Implement `/tasks/<id>/clone/` endpoint |
| Dropdown not closing | Ensure Alpine.js `@click.away` directive is present |

---

## Next Steps

1. **Integrate FAB into Task Board** (5 minutes)
2. **Integrate Inline Actions into Task Modal** (10 minutes)
3. **Integrate Sidebar into Barangay Detail** (15 minutes - includes layout change)
4. **Integrate Header into Communities List** (10 minutes)
5. **Implement Backend Endpoints** (varies - see guide)
6. **Test All Integrations** (30 minutes)

**Total Estimated Time:** 1-2 hours (frontend only, excluding backend)

---

## Support

For detailed implementation instructions, see:
- **[QUICK_ACTIONS_IMPLEMENTATION_GUIDE.md](./QUICK_ACTIONS_IMPLEMENTATION_GUIDE.md)** - Complete guide
- **[OBCMS_UI_COMPONENTS_STANDARDS.md](./OBCMS_UI_COMPONENTS_STANDARDS.md)** - UI standards

---

**Ready to implement? Start with Task Board FAB (easiest integration).**
