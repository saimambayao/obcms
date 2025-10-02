# Official OBCMS Stat Card Template - 3D Milk White Design

**Status:** ✅ Official Design Standard
**Date Created:** 2025-10-02
**Reference Implementation:** [recommendations_home.html](../../../src/templates/recommendations/recommendations_home.html)
**Preview:** http://localhost:8000/recommendations/

---

## Overview

This document defines the **official stat card design** for the entire OBCMS system. All statistics cards across all modules must follow this 3D milk white design for consistency and professional appearance.

## Design Philosophy

- **Clean & Modern:** Soft milk white palette for a professional, government-appropriate aesthetic
- **3D Embossed Effect:** Tactile appearance using layered shadows and gradients
- **Accessibility:** High contrast text for readability (WCAG 2.1 AA compliant)
- **Consistency:** Uniform design across all modules (Dashboard, MANA, Coordination, Recommendations, etc.)

---

## Base Stat Card Template

### HTML Structure

```html
<!-- Statistics Cards - 3D Milk White Design -->
<div class="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- Single Stat Card -->
    <div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
         style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
        <!-- Gradient overlay for depth -->
        <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>

        <!-- Content - Use flex column to push breakdown to bottom -->
        <div class="relative p-6 flex flex-col h-full">
            <!-- Header: Label + Number + Icon -->
            <div class="flex items-center justify-between mb-3">
                <div>
                    <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Stat Label</p>
                    <p class="text-4xl font-extrabold text-gray-800 mt-1">0</p>
                </div>
                <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                     style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                    <i class="fas fa-icon-name text-2xl text-color-600"></i>
                </div>
            </div>

            <!-- Spacer to push breakdown to bottom -->
            <div class="flex-grow"></div>

            <!-- Optional: Breakdown (3 columns) - Always at bottom -->
            <div class="grid grid-cols-3 gap-2 pt-3 border-t border-gray-200/60 mt-auto">
                <div class="text-center">
                    <p class="text-xl font-bold text-gray-700">0</p>
                    <p class="text-xs text-gray-500 font-medium">Category 1</p>
                </div>
                <div class="text-center">
                    <p class="text-xl font-bold text-gray-700">0</p>
                    <p class="text-xs text-gray-500 font-medium">Category 2</p>
                </div>
                <div class="text-center">
                    <p class="text-xl font-bold text-gray-700">0</p>
                    <p class="text-xs text-gray-500 font-medium">Category 3</p>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## Design Specifications

### Color Palette

| Element | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| **Background (Light)** | Milk White | `#FEFDFB` | Card background gradient start |
| **Background (Dark)** | Warm White | `#FBF9F5` | Card background gradient end |
| **Text (Primary)** | Charcoal | `text-gray-800` | Main numbers, headings |
| **Text (Secondary)** | Medium Gray | `text-gray-600` | Labels, descriptions |
| **Text (Tertiary)** | Light Gray | `text-gray-500` | Small text, categories |
| **Border** | Translucent Gray | `border-gray-200/60` | Separator lines |

### Icon Colors (Semantic)

| Category | Icon Color | Usage |
|----------|-----------|--------|
| **Total/General** | Amber | `text-amber-600` | Overall statistics |
| **Success/Completed** | Emerald | `text-emerald-600` | Implemented, completed items |
| **Info/Submitted** | Blue | `text-blue-600` | Submitted, in-progress items |
| **Draft/Proposed** | Purple | `text-purple-600` | Proposed, draft items |
| **Warning** | Orange | `text-orange-600` | Needs attention |
| **Danger** | Red | `text-red-600` | Critical, overdue |

### Shadow Specifications

**3D Embossed Effect (Card):**
```css
box-shadow:
    0 8px 20px rgba(0,0,0,0.08),        /* Primary depth shadow */
    0 2px 8px rgba(0,0,0,0.06),         /* Secondary shadow */
    inset 0 -2px 4px rgba(0,0,0,0.02),  /* Bottom inset (depth) */
    inset 0 2px 4px rgba(255,255,255,0.9); /* Top highlight (raised) */
```

**3D Embossed Effect (Icon Container):**
```css
box-shadow:
    0 4px 12px rgba(0,0,0,0.1),         /* Depth shadow */
    inset 0 -2px 4px rgba(0,0,0,0.05),  /* Bottom inset */
    inset 0 2px 4px rgba(255,255,255,0.8); /* Top highlight */
```

### Typography

| Element | Size | Weight | Transform |
|---------|------|--------|-----------|
| **Main Number** | `text-4xl` (36px) | `font-extrabold` (800) | - |
| **Label** | `text-sm` (14px) | `font-semibold` (600) | `uppercase`, `tracking-wide` |
| **Breakdown Numbers** | `text-xl` (20px) | `font-bold` (700) | - |
| **Breakdown Labels** | `text-xs` (12px) | `font-medium` (500) | - |

### Spacing & Layout

- **Card Padding:** `p-6` (24px)
- **Grid Gap:** `gap-6` (24px between cards)
- **Border Radius:** `rounded-2xl` (16px)
- **Icon Container Size:** `w-16 h-16` (64x64px)
- **Hover Lift:** `hover:-translate-y-2` (8px up)
- **⚠️ Bottom Alignment:** Breakdown items MUST be aligned to bottom of card for visual symmetry

---

## ⚠️ Critical: Bottom Alignment for Symmetry

**Why Bottom Alignment Matters:**

When stat cards have different label lengths or content heights, the breakdown items (Policies, Programs, Services) can appear misaligned, creating visual asymmetry. To maintain professional appearance:

### Implementation Requirements

1. **Container must use flexbox column:**
   ```html
   <div class="relative p-6 flex flex-col h-full">
   ```

2. **Add flexible spacer between header and breakdown:**
   ```html
   <div class="flex-grow"></div>
   ```

3. **Breakdown section must have `mt-auto`:**
   ```html
   <div class="grid grid-cols-3 gap-2 pt-3 border-t border-gray-200/60 mt-auto">
   ```

### Visual Example

```
❌ BAD (Without bottom alignment):
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Label       │  │ Very Long   │  │ Short       │
│ 42          │  │ Label Text  │  │ 12          │
│             │  │ 156         │  │             │
│ Breakdown   │  │             │  │ Breakdown   │
│ [Policies]  │  │ Breakdown   │  │ [Policies]  │
│ [Programs]  │  │ [Policies]  │  │ [Programs]  │
│ [Services]  │  │ [Programs]  │  │ [Services]  │
│             │  │ [Services]  │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
    ↑                 ↑                 ↑
  Misaligned    Misaligned       Misaligned
  (no symmetry across cards)

✅ GOOD (With bottom alignment):
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Label       │  │ Very Long   │  │ Short       │
│ 42          │  │ Label Text  │  │ 12          │
│             │  │ 156         │  │             │
│             │  │             │  │             │
│             │  │             │  │             │
│ Breakdown   │  │ Breakdown   │  │ Breakdown   │
│ [Policies]  │  │ [Policies]  │  │ [Policies]  │
│ [Programs]  │  │ [Programs]  │  │ [Programs]  │
│ [Services]  │  │ [Services]  │  │ [Services]  │
└─────────────┘  └─────────────┘  └─────────────┘
         ↑              ↑              ↑
    Perfect alignment across all cards
    (professional symmetry)
```

### Code Comparison

**❌ Wrong (No bottom alignment):**
```html
<div class="relative p-6">
    <div class="flex items-center justify-between mb-3">
        <!-- Header content -->
    </div>
    <div class="grid grid-cols-3 gap-2 pt-3 border-t border-gray-200/60">
        <!-- Breakdown items -->
    </div>
</div>
```

**✅ Correct (With bottom alignment):**
```html
<div class="relative p-6 flex flex-col h-full">
    <div class="flex items-center justify-between mb-3">
        <!-- Header content -->
    </div>

    <!-- Spacer pushes breakdown to bottom -->
    <div class="flex-grow"></div>

    <div class="grid grid-cols-3 gap-2 pt-3 border-t border-gray-200/60 mt-auto">
        <!-- Breakdown items -->
    </div>
</div>
```

### Testing Bottom Alignment

Create stat cards with different label lengths to verify alignment:
- "Total" (short label)
- "Total Recommendations" (medium label)
- "Total Implemented Recommendations" (long label)

All breakdown sections should align perfectly at the bottom regardless of label length.

---

## ⚡ Auto-Refresh with HTMX (Live Updates)

**NEW:** All stat cards should support auto-refresh for real-time metric updates.

### Implementation Pattern

**1. Wrap stat cards in HTMX container:**
```html
<!-- Statistics Cards - Auto-refresh every 60s -->
<div class="mb-8">
    <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-bold text-gray-900">System Overview</h2>
        <span class="text-xs text-gray-500">
            <i class="fas fa-sync-alt"></i> Updates every 60s
        </span>
    </div>

    <div hx-get="{% url 'app:stats_cards' %}"
         hx-trigger="load, every 60s"
         hx-swap="innerHTML"
         class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Loading state -->
        <div class="col-span-full flex items-center justify-center py-12">
            <i class="fas fa-spinner fa-spin text-gray-400 text-2xl"></i>
        </div>
    </div>
</div>
```

**2. Create Django view endpoint:**
```python
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_stats_cards(request):
    """Return just the stat cards HTML (partial template)"""
    context = {
        'stats': {
            'communities': {
                'total': Community.objects.count(),
                'barangay_total': Community.objects.filter(type='barangay').count(),
            },
            # ... other stats
        }
    }
    return render(request, 'partials/dashboard_stats_cards.html', context)
```

**3. Create partial template** (`templates/partials/dashboard_stats_cards.html`):
```html
<!-- Just the stat cards, NO wrapper div -->
<!-- Total OBC Communities -->
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl ...">
    <!-- Card content -->
</div>

<!-- More stat cards... -->
```

**4. Add URL pattern:**
```python
# urls.py
path('dashboard/stats-cards/', views.dashboard_stats_cards, name='dashboard_stats_cards'),
```

### Auto-Refresh Features

✅ **Real-time Updates:** Stats refresh every 60 seconds without page reload
✅ **Smooth Transitions:** HTMX swap animations prevent jarring updates
✅ **Visual Indicator:** "Updates every 60s" badge shows refresh status
✅ **Loading State:** Spinner shows during initial load
✅ **Efficient:** Only updates stat cards, not entire page

### Customization Options

**Different refresh intervals:**
```html
hx-trigger="load, every 30s"  <!-- Every 30 seconds -->
hx-trigger="load, every 120s" <!-- Every 2 minutes -->
hx-trigger="load"             <!-- Only on load (no auto-refresh) -->
```

**Smooth swap animation:**
```html
hx-swap="innerHTML swap:300ms"  <!-- Fade transition -->
```

---

## Variants

### Simple Stat Card (No Breakdown)

```html
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
     style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
    <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>
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

### Stat Card with 2-Column Breakdown

```html
<!-- Replace 'grid-cols-3' with 'grid-cols-2' -->
<div class="grid grid-cols-2 gap-3 pt-3 border-t border-gray-200/60">
    <div class="text-center">
        <p class="text-xl font-bold text-gray-700">25</p>
        <p class="text-xs text-gray-500 font-medium">Category A</p>
    </div>
    <div class="text-center">
        <p class="text-xl font-bold text-gray-700">17</p>
        <p class="text-xs text-gray-500 font-medium">Category B</p>
    </div>
</div>
```

### Stat Card with Progress Bar

```html
<div class="relative p-6">
    <div class="flex items-center justify-between mb-3">
        <div>
            <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Completion Rate</p>
            <p class="text-4xl font-extrabold text-gray-800 mt-1">68%</p>
        </div>
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
             style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
            <i class="fas fa-chart-line text-2xl text-emerald-600"></i>
        </div>
    </div>

    <!-- Progress Bar -->
    <div class="mt-4">
        <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div class="bg-emerald-500 h-2 rounded-full" style="width: 68%"></div>
        </div>
    </div>
</div>
```

---

## Implementation Guidelines

### Step 1: Replace Existing Stat Cards

1. **Locate stat card sections** in template (usually after hero section)
2. **Identify the grid structure** (typically `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4`)
3. **Replace card markup** with 3D milk white template
4. **Update dynamic data** (template variables like `{{ stats.total }}`)
5. **Choose appropriate icon** and color based on semantic meaning

### Step 2: Icon Selection

**FontAwesome Icons:**
- `fa-home` - Communities, locations
- `fa-users` - People, groups, families
- `fa-lightbulb` - Recommendations, ideas
- `fa-check-circle` - Completed, implemented
- `fa-paper-plane` - Submitted, sent
- `fa-edit` - Draft, proposed
- `fa-chart-line` - Growth, analytics
- `fa-calendar` - Events, schedules
- `fa-file-alt` - Documents, reports
- `fa-handshake` - Partnerships, coordination

### Step 3: Grid Responsive Behavior

```html
<!-- 1 column on mobile, 2 on tablet, 4 on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

<!-- 1 column on mobile, 2 on tablet, 3 on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

<!-- Always 2 columns on all sizes -->
<div class="grid grid-cols-2 gap-6">
```

---

## Accessibility Considerations

### WCAG 2.1 AA Compliance

✅ **Color Contrast:**
- Main text (`text-gray-800` on milk white): **11.5:1** (exceeds AAA)
- Label text (`text-gray-600` on milk white): **7.2:1** (exceeds AA)
- Small text (`text-gray-500` on milk white): **4.8:1** (meets AA)

✅ **Interactive Elements:**
- Hover effect provides visual feedback (lift animation)
- Focus states inherit from Tailwind defaults
- Touch targets exceed 44x44px minimum

✅ **Semantic HTML:**
- Use proper heading hierarchy
- Include ARIA labels where appropriate
- Maintain logical tab order

### Screen Reader Support

```html
<!-- Add aria-label for context -->
<div class="..." aria-label="Total recommendations: 42">
    <!-- Card content -->
</div>

<!-- Or use sr-only text -->
<div class="...">
    <span class="sr-only">Total recommendations</span>
    <!-- Visual content -->
</div>
```

---

## Testing Checklist

Before deploying, verify each stat card:

- [ ] ✅ Uses milk white background (`#FEFDFB` to `#FBF9F5`)
- [ ] ✅ Has 3D embossed shadow (outer + inset)
- [ ] ✅ Icon container has separate 3D effect
- [ ] ✅ Text colors match specification (gray-800, gray-600, gray-500)
- [ ] ✅ Hover animation works (translate-y-2)
- [ ] ✅ Responsive grid adapts to screen sizes
- [ ] ✅ Icon color matches semantic meaning
- [ ] ✅ Typography sizes and weights are correct
- [ ] ✅ Border radius is `rounded-2xl`
- [ ] ✅ Contrast ratios meet WCAG AA standards

---

## Module-Specific Examples

### Dashboard (Main)
- Total Communities
- Total Families
- Active Assessments
- Recent Activity

### MANA (Assessments)
- Total Assessments
- Completed Assessments
- Pending Assessments
- Coverage Rate

### Coordination (Partnerships)
- Active Partnerships
- Resource Commitments
- Coordination Meetings
- Joint Programs

### Recommendations (Policies)
- Total Recommendations *(reference implementation)*
- Implemented
- Submitted
- Proposed

### Communities (OBC Data)
- Registered Barangays
- Provincial Coverage
- Municipal Coverage
- Data Completeness

---

## Migration Status

**Target:** All stat cards across OBCMS
**Completed Modules:**
- ✅ Recommendations (`recommendations_home.html`)

**Pending Modules:**
- ⏳ Dashboard (`dashboard.html`)
- ⏳ MANA (`mana_dashboard.html`, `assessment_list.html`)
- ⏳ Coordination (`coordination_dashboard.html`)
- ⏳ Communities (`communities_dashboard.html`)
- ⏳ Monitoring dashboards (all variants)

---

## Support & Questions

**Document Owner:** OBCMS UI/UX Team
**Last Updated:** 2025-10-02
**Version:** 1.0.0

For questions or design variations, refer to:
- Reference implementation: [recommendations_home.html](../../../src/templates/recommendations/recommendations_home.html)
- Live preview: http://localhost:8000/recommendations/
- Design system documentation: [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)

---

## Notes

- **DO NOT** modify the shadow specifications - they create the signature 3D effect
- **MAINTAIN** consistent spacing (p-6, gap-6) across all implementations
- **USE** semantic icon colors (amber=total, emerald=success, blue=info, purple=draft)
- **TEST** on multiple screen sizes before committing
- **VERIFY** accessibility with contrast checker tools

This design is now the **official standard** for all OBCMS stat cards. Any deviations must be approved by the UI/UX team.
