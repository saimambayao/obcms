# Quick Action Pattern Decision Guide

**Quick Reference for Choosing the Right Quick Action Pattern**

---

## Decision Flowchart

```
START: What type of page are you designing?
│
├─ Dashboard / Overview Page
│  └─> Use: SIDEBAR QUICK ACTIONS (Right Sidebar)
│      Pattern: Vertical list of action cards
│      Reference: portfolio_dashboard.html lines 182-239
│
├─ Detail Page (Single Record)
│  │
│  ├─ Simple detail with few sections
│  │  └─> Use: FLOATING FAB (Bottom-Right)
│  │      Pattern: FAB with expandable menu
│  │      Actions: Edit, Save, Preview, Help
│  │
│  └─ Rich detail with multiple sections
│     └─> Use: SIDEBAR QUICK ACTIONS (Right Sidebar)
│         Pattern: Related navigation & actions
│         Reference: workflow_detail.html lines 220-250
│
├─ List / Table Page
│  │
│  ├─ Module home page
│  │  └─> Use: HEADER QUICK ACTIONS (Horizontal Grid)
│  │      Pattern: 3-4 column grid of action cards
│  │      Reference: communities_home.html lines 246-393
│  │
│  └─ Table with filters
│     └─> Use: HEADER QUICK ACTIONS (Compact Bar)
│         Pattern: Horizontal button row
│         Reference: coordination_events.html lines 69-90
│
├─ Form Page (Create / Edit)
│  └─> Use: FLOATING FAB (Bottom-Right)
│      Pattern: Save draft, Preview, Help actions
│      Actions: Persistent while scrolling
│
├─ Calendar / Map Page
│  └─> Use: HEADER QUICK ACTIONS + FLOATING FAB
│      Header: View toggles, filters
│      FAB: Quick add, jump to today
│
└─ Long Scrolling Page
   └─> Use: FLOATING FAB (Bottom-Right)
       Pattern: Persistent access to key actions
       Actions: Save, Navigate, Help
```

---

## Pattern Quick Reference

### Pattern A: Sidebar Quick Actions

**Visual:** Right sidebar with vertical action list
**Best For:** Dashboards, rich detail pages
**Layout:** 2-column grid (content + sidebar)
**Action Count:** 3-6 actions
**Mobile Behavior:** Collapses below content

```html
<div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
    <div class="xl:col-span-2"><!-- Main content --></div>
    <aside><!-- Sidebar Quick Actions --></aside>
</div>
```

**When to Use:**
✅ Desktop-focused dashboards
✅ Pages with multiple related sections
✅ Need for contextual navigation
✅ Rich content requiring persistent actions

**When NOT to Use:**
❌ Mobile-first design (sidebar less prominent)
❌ Simple CRUD operations
❌ Limited horizontal space

---

### Pattern B: Header Quick Actions

**Visual:** Horizontal grid below page title
**Best For:** Module home pages, list pages
**Layout:** 3-4 column grid of action cards
**Action Count:** 3-6 actions
**Mobile Behavior:** Stacks vertically

```html
<section>
    <h2>Quick Actions</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Action cards -->
    </div>
</section>
```

**When to Use:**
✅ Module landing pages
✅ List/table pages
✅ Equal-priority actions
✅ Need for visual prominence

**When NOT to Use:**
❌ Form pages (competes with submission)
❌ More than 6 actions (too crowded)
❌ Detail pages with limited width

**Compact Variant:**
```html
<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
    <a class="bg-gradient-to-r from-blue-500 to-blue-600 ...">
        <i class="fas fa-plus mr-2"></i>
        Create New
    </a>
</div>
```

---

### Pattern C: Floating FAB

**Visual:** Fixed bottom-right corner button
**Best For:** Forms, long pages, maps
**Layout:** Floating above content
**Action Count:** 1-3 actions (expandable)
**Mobile Behavior:** Optimized for thumb zone

```html
<div class="fixed bottom-8 right-8 z-50">
    <button class="w-14 h-14 rounded-full ...">
        <i class="fas fa-bolt"></i>
    </button>
</div>
```

**When to Use:**
✅ Long forms requiring scroll
✅ Pages with complex layouts
✅ Persistent action access needed
✅ Mobile-first design

**When NOT to Use:**
❌ Desktop-only applications
❌ Multiple equally important actions
❌ Bottom navigation conflicts

---

## Page Type → Pattern Mapping

| Page Type | Primary Pattern | Secondary | Example Page |
|-----------|----------------|-----------|--------------|
| **Dashboard** | Sidebar | Header | Portfolio Dashboard |
| **Module Home** | Header (Grid) | - | Communities Home |
| **List/Table** | Header (Compact) | - | Events List |
| **Detail (Simple)** | Floating FAB | - | Organization Detail |
| **Detail (Rich)** | Sidebar | FAB | Workflow Detail |
| **Create Form** | Floating FAB | - | Add Community |
| **Edit Form** | Floating FAB | Header | Edit Partnership |
| **Calendar** | Header | FAB | OOBC Calendar |
| **Map** | Header | FAB | Regional Overview |
| **Report** | Header | Sidebar | Budget Dashboard |

---

## Action Type → Color Mapping

### Icon Container Gradients (Header Quick Actions)

| Action Type | Gradient | Example |
|-------------|----------|---------|
| Create/Add | `from-blue-500 to-blue-600` | Add Barangay OBC |
| Manage/Edit | `from-green-500 to-green-600` | Manage Records |
| View/Report | `from-purple-500 to-purple-600` | View Analytics |
| Process | `from-emerald-500 to-teal-600` | Budget Planning |
| Export | `from-amber-500 to-amber-600` | Export Data |
| Calendar | `from-sky-500 to-sky-600` | View Calendar |
| Map | `from-teal-500 to-cyan-600` | View on Map |
| Delete | `from-red-500 to-red-600` | Archive Record |

### Icon Backgrounds (Sidebar Quick Actions)

| Context | Background | Icon Color | Example |
|---------|-----------|------------|---------|
| Alerts/Urgent | `bg-rose-100` | `text-rose-600` | Active Alerts |
| Primary/Active | `bg-emerald-100` | `text-emerald-600` | Tracked Workflows |
| Process/Budget | `bg-blue-100` | `text-blue-600` | Budget Approvals |
| Secondary | `bg-purple-100` | `text-purple-600` | Partnerships |
| Info/Reports | `bg-cyan-100` | `text-cyan-600` | View Reports |

---

## Implementation Checklist

### Before You Start

- [ ] **Page type identified**: Dashboard, list, detail, form, etc.
- [ ] **Pattern selected**: Sidebar, header, or FAB
- [ ] **Actions prioritized**: Most common actions first
- [ ] **User permissions considered**: Show actions based on roles

### During Implementation

- [ ] **Copy template**: Use exact HTML from QUICK_ACTION_COMPONENTS.md
- [ ] **Replace URLs**: Update `{% url '...' %}` tags
- [ ] **Update icons**: Choose semantic FontAwesome icons
- [ ] **Apply colors**: Follow gradient/background guidelines
- [ ] **Add counts/badges**: Show pending items if applicable
- [ ] **Test hover states**: Verify all transitions work
- [ ] **Check responsive**: Test on mobile, tablet, desktop
- [ ] **Verify keyboard nav**: Tab order logical, focus visible
- [ ] **Add ARIA labels**: Screen reader support complete

### After Implementation

- [ ] **Test permissions**: Verify actions respect user roles
- [ ] **Test all links**: Ensure URLs are correct
- [ ] **Check contrast**: WCAG 2.1 AA compliance
- [ ] **Mobile test**: FAB position doesn't conflict with navigation
- [ ] **Document**: Add to module documentation if custom

---

## Common Patterns by Module

### Communities Module
- **Home**: Header (Grid) - Add Barangay, Add Municipal, Manage, View Map
- **Manage**: Header (Compact) - Filter, Export, View Geographic Data
- **Detail**: Sidebar - Edit Profile, View Assessments, Stakeholders

### Coordination Module
- **Home**: Header (Grid) - Organizations, Partnerships, Events, Calendar
- **Events**: Header (Compact) - New Event, Log Activity, Export, Calendar
- **Partnership Detail**: Sidebar - Milestones, Signatories, Documents

### MANA Module
- **Home**: Header (Grid) - New Assessment, Manage, Regional Overview, Reports
- **Assessment Detail**: Sidebar - Edit, View Needs, Generate Report
- **Form**: FAB - Save Draft, Preview, Help

### Project Central Module
- **Portfolio Dashboard**: Sidebar - Active Alerts, Workflows, Budget Approvals
- **Workflow Detail**: Sidebar + FAB - Calendar, Tasks, Activities (Sidebar); Save, Help (FAB)
- **Budget Dashboard**: Header - Create Budget, Manage Approvals, Reports

---

## Troubleshooting

### "Too many actions to fit in sidebar"
**Solution:** Use Header Quick Actions instead, or split into sections

### "FAB conflicts with bottom navigation on mobile"
**Solution:** Adjust position: `bottom-20 sm:bottom-8`

### "Sidebar looks empty on mobile"
**Solution:** That's expected. Sidebar collapses below content. Consider adding header actions for mobile.

### "Actions are cluttered in header"
**Solution:** Limit to 6 actions max. Use compact variant or split into sections.

### "Hover states not working"
**Solution:** Ensure `group` class on parent and `group-hover:` on children

---

## Quick Copy-Paste Examples

### Sidebar Quick Action (Single Item)

```html
<li>
    <a href="{% url 'module:action' %}"
       class="group flex items-center justify-between rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 text-sm font-semibold text-gray-700 hover:border-emerald-200 hover:bg-emerald-50 transition-all duration-200">
        <div class="flex items-center gap-3">
            <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600">
                <i class="fas fa-icon"></i>
            </span>
            <div>
                <p>Action Title</p>
                <p class="text-xs font-normal text-gray-500">Description or count</p>
            </div>
        </div>
        <i class="fas fa-arrow-right text-gray-400 group-hover:text-emerald-600"></i>
    </a>
</li>
```

### Header Quick Action Card

```html
<a href="{% url 'module:action' %}"
   class="group bg-white rounded-lg shadow-lg border border-gray-200 hover-lift transition-all duration-200 flex flex-col">
    <div class="p-6 flex flex-col flex-grow">
        <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <i class="fas fa-plus text-white text-xl"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
            Action Title
        </h3>
        <p class="mt-2 text-sm text-gray-600 flex-grow">
            Action description explaining what this does.
        </p>
        <div class="mt-4 flex items-center text-blue-600 text-sm font-medium">
            <span>Call to Action</span>
            <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
        </div>
    </div>
</a>
```

### Floating FAB (Simple)

```html
<a href="{% url 'module:create' %}"
   class="fixed bottom-8 right-8 z-50 w-14 h-14 rounded-full bg-gradient-to-r from-blue-600 to-teal-600 text-white shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-200 flex items-center justify-center"
   title="Create New"
   aria-label="Create New Record">
    <i class="fas fa-plus text-xl"></i>
</a>
```

---

## Need More Help?

1. **Review Full Documentation**: [QUICK_ACTION_COMPONENTS.md](QUICK_ACTION_COMPONENTS.md)
2. **Check Existing Examples**:
   - Sidebar: `src/templates/project_central/portfolio_dashboard.html` (lines 182-239)
   - Header: `src/templates/communities/communities_home.html` (lines 246-393)
   - FAB: Reference provided in full documentation
3. **Follow UI Standards**: [OBCMS_UI_COMPONENTS_STANDARDS.md](OBCMS_UI_COMPONENTS_STANDARDS.md)

---

**Last Updated:** 2025-10-03
**Version:** 1.0
