# OBC Database Tables Presentation

**Status**: Production-Ready with Recommended Improvements
**Last Updated**: 2025-10-12
**Location**: `src/templates/communities/partials/*_manage_results.html`
**Backend**: `src/common/views/communities.py`

---

## Table of Contents

1. [Overview](#overview)
2. [Current Implementation](#current-implementation)
3. [Recent Improvements (2025-10-12)](#recent-improvements-2025-10-12)
4. [Column Width Analysis](#column-width-analysis)
5. [Consistency Across Tables](#consistency-across-tables)
6. [Areas for Improvement](#areas-for-improvement)
7. [Implementation Guide](#implementation-guide)
8. [Technical Reference](#technical-reference)

---

## Overview

OBCMS features three hierarchical OBC database management views:

1. **Barangay OBC Registry** - Community-level OBC records (6,598+ records)
2. **Municipal OBC Directory** - Municipality-level coverage aggregations (282+ records)
3. **Provincial OBC Registry** - Province-level strategic view (20+ records)

These tables follow a consistent design pattern with graduated complexity from barangay → municipal → provincial levels.

### Design Principles

- **Hierarchical Consistency**: Each table reflects its administrative level
- **Information Density**: More granular data at barangay level, aggregated at higher levels
- **Action Accessibility**: View/Edit/Delete actions available to authorized users
- **Responsive Design**: Tables adapt to mobile, tablet, and desktop viewports
- **Semantic Colors**: Consistent use of emerald for success, amber for warnings, blue for info

---

## Current Implementation

### 1. Barangay OBC Registry

**URL**: `/communities/manage/`
**Template**: `src/templates/communities/partials/barangay_manage_results.html`
**Backend**: `src/common/views/communities.py:228-376` (`_build_barangay_table`)

#### Table Structure

| Column | Content | Width Behavior |
|--------|---------|----------------|
| **Community** | Barangay name + OBC ID | Fixed icon (40px) + flex content |
| **Location** | Municipality, Province, Region | Flexible, min-content |
| **Coverage Snapshot** | Population stats, households, stakeholders | Flexible, can expand |

**Column Details**:

```python
headers = [
    {"label": "Community"},      # Barangay name + OBC ID badge
    {"label": "Location"},       # Municipality > Province > Region hierarchy
    {"label": "Coverage Snapshot"},  # 4-line stat block
]
```

**Key Features**:
- Blue gradient icon (fas fa-map-marker-alt) for each barangay
- **Recent Change**: Province and Region text increased to `text-base` (16px) for better readability
- **Recent Change**: Removed unused ethnolinguistic/languages column (dead code cleanup)
- 4-metric snapshot: Est. OBC Population, Barangay Population, Households, Stakeholders tracked

#### Column Content Example

**Community Column**:
```html
<div class='flex items-center gap-3'>
  <span class='inline-flex h-10 w-10 items-center justify-center rounded-xl
    bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-sm'>
    <i class='fas fa-map-marker-alt'></i>
  </span>
  <div>
    <div class='text-sm font-semibold text-gray-900'>50th District</div>
    <div class='text-xs text-gray-500'>ID: X-MO-CO-3580</div>
  </div>
</div>
```

**Location Column**:
```html
<div class='text-sm font-medium text-gray-900'>City of Ozamiz</div>
<div class='text-base font-medium text-gray-700'>Misamis Occidental</div>
<div class='text-base text-gray-600'>Region X · Northern Mindanao</div>
```

**Coverage Snapshot Column**:
```html
<div class='space-y-1 text-sm text-gray-700'>
  <div><span class='font-semibold text-gray-900'>Est. OBC Population:</span> N/A</div>
  <div><span class='font-semibold text-gray-900'>Barangay Population:</span> 581</div>
  <div><span class='font-semibold text-gray-900'>Households:</span> N/A</div>
  <div><span class='font-semibold text-gray-900'>Stakeholders tracked:</span> 0</div>
</div>
```

---

### 2. Municipal OBC Directory

**URL**: `/communities/managemunicipal/`
**Template**: `src/templates/communities/partials/municipal_manage_results.html`
**Backend**: `src/common/views/communities.py:947-1386` (`communities_manage_municipal`)

#### Table Structure

| Column | Content | Width Behavior |
|--------|---------|----------------|
| **Municipality / City** | Name + type (City/Municipality) | Fixed icon (44px) + flex content |
| **Province & Region** | Province name, Region code + name | Flexible |
| **Coverage Snapshot** | Barangays tracked, populations, households | Flexible, can expand |
| **Top 5 Barangays** | Key barangays list | Flexible, text content |
| **Sync Mode** | Auto-sync or Manual badge | Fixed badge width (~120px) |

**Column Details**:

```python
municipality_table_headers = [
    {"label": "Municipality / City"},
    {"label": "Province & Region"},
    {"label": "Coverage Snapshot"},
    {"label": "Top 5 Barangays"},
    {"label": "Sync Mode"},
]
```

**Key Features**:
- Indigo gradient icon (fas fa-city)
- **Recent Change**: Removed unused `history_html` and `_format_municipal_date` (dead code cleanup)
- **Recent Change**: Added `show_actions=table.show_actions` parameter (was missing, causing action buttons to not display)
- Sync Mode badges: Emerald for Auto-sync, Amber for Manual
- Coverage snapshot shows aggregated data from barangay level

#### Column Content Example

**Municipality / City Column**:
```html
<div class='flex items-center gap-3'>
  <span class='inline-flex h-11 w-11 items-center justify-center rounded-xl
    bg-indigo-100 text-indigo-600'>
    <i class='fas fa-city'></i>
  </span>
  <div>
    <div class='text-sm font-semibold text-gray-900'>Davao City</div>
    <div class='text-xs text-gray-500'>City</div>
  </div>
</div>
```

**Province & Region Column**:
```html
<div class='space-y-1'>
  <div class='font-medium text-gray-900'>Davao City (Huc)</div>
  <div class='text-xs text-gray-500'>Region XI · Davao Region</div>
</div>
```

**Coverage Snapshot Column**:
```html
<div class='space-y-1'>
  <div class='text-sm font-semibold text-gray-900'>0 barangay OBCs tracked</div>
  <div class='text-xs text-gray-500'>Est. OBC Population: —</div>
  <div class='text-xs text-gray-500'>Total Population: 1,848,947</div>
  <div class='text-xs text-gray-500'>Households: 0</div>
</div>
```

**Top 5 Barangays Column**:
```html
<div class='text-sm text-gray-700'>Bucana, Buhangin, Talomo, Ma-A, Sasa</div>
<!-- OR if empty -->
<div class='text-sm text-gray-400'>—</div>
```

**Sync Mode Column**:
```html
<!-- Auto-sync -->
<span class='inline-flex items-center gap-1 rounded-full border border-emerald-200
  bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700'>
  <i class='fas fa-sync'></i>
  <span>Auto-sync</span>
</span>

<!-- Manual -->
<span class='inline-flex items-center gap-1 rounded-full border border-amber-200
  bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700'>
  <i class='fas fa-hand-paper'></i>
  <span>Manual</span>
</span>
```

---

### 3. Provincial OBC Registry

**URL**: `/communities/manageprovincial/`
**Template**: `src/templates/communities/partials/provincial_manage_results.html`
**Backend**: `src/common/views/communities.py:1389-1791` (`communities_manage_provincial`)

#### Table Structure

| Column | Content | Width Behavior |
|--------|---------|----------------|
| **Province** | Province name + display name | Fixed icon (44px) + flex content |
| **Region** | Region code + name | Flexible |
| **Coverage Snapshot** | Municipalities, barangays, populations | Flexible, can expand |
| **Top 5 Municipalities/Cities** | Key municipalities list | Flexible, text content |
| **Sync Mode** | Auto-sync or Manual badge | Fixed badge width (~120px) |

**Column Details**:

```python
province_table_headers = [
    {"label": "Province"},
    {"label": "Region"},
    {"label": "Coverage Snapshot"},
    {"label": "Top 5 Municipalities/Cities"},
    {"label": "Sync Mode"},
]
```

**Key Features**:
- Indigo gradient icon (fas fa-flag)
- **Recent Change**: Changed `show_actions=True` to `show_actions=can_manage_communities` (proper permission check)
- Identical Sync Mode implementation to Municipal table (consistency)
- Strategic view: municipalities tracked, barangay OBCs, populations
- Custom header/footer templates for advanced controls

#### Column Content Example

**Province Column**:
```html
<div class='flex items-center gap-3'>
  <span class='inline-flex h-11 w-11 items-center justify-center rounded-xl
    bg-indigo-100 text-indigo-600'>
    <i class='fas fa-flag'></i>
  </span>
  <div>
    <div class='text-sm font-semibold text-gray-900'>Davao del Norte</div>
    <div class='text-xs text-gray-500'>—</div>
  </div>
</div>
```

**Region Column**:
```html
<div class='space-y-1'>
  <div class='text-sm font-medium text-gray-900'>Region XI</div>
  <div class='text-xs text-gray-500'>Davao Region</div>
</div>
```

**Coverage Snapshot Column**:
```html
<div class='space-y-1'>
  <div class='text-sm font-semibold text-gray-900'>5 municipalities tracked</div>
  <div class='text-xs text-gray-500'>Barangay OBCs: 120</div>
  <div class='text-xs text-gray-500'>Est. OBC Population: 45,000</div>
  <div class='text-xs text-gray-500'>Households: 8,500</div>
</div>
```

**Top 5 Municipalities/Cities Column**:
```html
<div class='text-sm text-gray-700'>Tagum City, Panabo City, Island Garden City of Samal, Davao del Norte, Carmen</div>
<!-- OR if empty -->
<div class='text-sm text-gray-400'>—</div>
```

---

## Recent Improvements (2025-10-12)

### Code Cleanup and Dead Code Removal

#### 1. Barangay OBC Table
**Removed**: Unused ethnolinguistic and languages column code (lines 299-350)

```python
# REMOVED: Dead code that built ethno_html variable
# This was never displayed in the table
chips: list = []
if community.primary_ethnolinguistic_group:
    chips.append(...)
# ... 50+ lines of unused code
ethno_html = mark_safe("".join(str(row) for row in ethno_rows))
```

**Impact**:
- Cleaner codebase
- Faster table rendering (no unused HTML generation)
- Reduced memory footprint

#### 2. Municipal OBC Table
**Removed**: Unused history_html variable and helper function

```python
# REMOVED: Dead code
def _format_municipal_date(value):
    if not value:
        return "—"
    try:
        localized = timezone.localtime(value)
    except Exception:
        localized = value
    return localized.strftime("%b %d, %Y")

history_html = format_html(
    "<div class='space-y-1 text-xs text-gray-500'>"
    "<div>Updated {}</div>"
    "<div>Created {}</div>"
    "</div>",
    _format_municipal_date(getattr(coverage, "updated_at", None)),
    _format_municipal_date(getattr(coverage, "created_at", None)),
)
```

**Impact**:
- Removed 20+ lines of dead code
- No "Last Updated" column confusion
- Consistent with other tables

### Typography Improvements

#### Barangay OBC - Location Column Font Increase

**Before**:
```python
format_html("<div class='text-sm text-gray-600'>{}</div>", province.name)
format_html("<div class='text-sm text-gray-500'>Region {} &middot; {}</div>", ...)
```

**After**:
```python
format_html("<div class='text-base font-medium text-gray-700'>{}</div>", province.name)
format_html("<div class='text-base text-gray-600'>Region {} &middot; {}</div>", ...)
```

**Impact**:
- Province name: 14px → 16px (text-sm → text-base)
- Region info: 14px → 16px (text-sm → text-base)
- Improved readability and hierarchy
- Better contrast (gray-600/gray-700 vs gray-500/gray-600)

### Action Buttons Fix

#### Municipal OBC Template
**Before**:
```django
{% include "components/data_table_card.html" with ... rows=table.rows ... %}
```

**After**:
```django
{% include "components/data_table_card.html" with ... rows=table.rows show_actions=table.show_actions ... %}
```

**Impact**: Action buttons (View/Edit/Delete) now display properly

#### Provincial OBC Template
**Before**:
```django
{% include "components/data_table_card.html" with ... show_actions=True ... %}
```

**After**:
```django
{% include "components/data_table_card.html" with ... show_actions=can_manage_communities ... %}
```

**Impact**: Proper permission checking (was hardcoded to True)

---

## Column Width Analysis

### Current Width Distribution Issues

The tables currently use auto-width distribution by the browser's table layout algorithm. This causes several issues:

#### Issue 1: Disproportionate Width Allocation

**Problem**: Columns with longer text content get disproportionately more space

**Example** (Municipal OBC table on 1920px display):
- Municipality / City: ~15% (should be ~20%)
- Province & Region: ~15% (appropriate)
- Coverage Snapshot: ~30% (should be ~25%)
- Top 5 Barangays: ~25% (should be ~30%)
- Sync Mode: ~10% (should be ~10%)
- Actions: ~5% (should be ~5%)

#### Issue 2: Inconsistent Responsive Behavior

**Problem**: No defined breakpoints for column hiding/stacking

**Current Behavior**:
- All columns visible on desktop (1024px+)
- All columns squashed on tablet (768-1023px)
- Horizontal scroll required on mobile (<768px)

**Needed Behavior**:
- Desktop (1024px+): All columns visible with optimal widths
- Tablet (768-1023px): Hide "Top 5" columns, stack key info
- Mobile (<768px): Card layout, hide all except name + key stat

#### Issue 3: Text Truncation vs. Wrapping

**Problem**: No consistent strategy for handling overflow

**Current Behavior**:
- Some columns wrap text (Coverage Snapshot)
- Some columns overflow without ellipsis (Top 5 Barangays)
- No max-width constraints

**Needed Behavior**:
- Name columns: Wrap with word-break
- List columns (Top 5): Truncate with ellipsis at 2 lines
- Stat columns: Always wrap, never truncate

#### Issue 4: Icon + Text Alignment

**Problem**: Icon sizes not contributing to consistent column widths

**Current Behavior**:
```html
<span class='inline-flex h-10 w-10 ...'>  <!-- Barangay: 40px -->
<span class='inline-flex h-11 w-11 ...'>  <!-- Municipal: 44px -->
<span class='inline-flex h-11 w-11 ...'>  <!-- Provincial: 44px -->
```

**Inconsistency**: Barangay uses 40px icons, others use 44px

### Recommended Width Distribution

#### Barangay OBC Table (3 columns + actions)

| Column | Desktop Width | Tablet Width | Mobile Width | Rationale |
|--------|---------------|--------------|--------------|-----------|
| Community | 25% (min: 200px) | 35% | 100% | Name + ID needs space |
| Location | 30% (min: 220px) | 40% | Hidden | 3-line hierarchy |
| Coverage Snapshot | 35% (min: 240px) | Hidden | Hidden | 4-line stats block |
| Actions | 10% (min: 120px) | 25% | Hidden | 3 buttons |

#### Municipal OBC Table (5 columns + actions)

| Column | Desktop Width | Tablet Width | Mobile Width | Rationale |
|--------|---------------|--------------|--------------|-----------|
| Municipality / City | 18% (min: 180px) | 35% | 100% | Name + type |
| Province & Region | 15% (min: 150px) | 30% | Hidden | 2-line hierarchy |
| Coverage Snapshot | 22% (min: 200px) | Hidden | Hidden | 4-line stats |
| Top 5 Barangays | 25% (min: 220px) | Hidden | Hidden | Comma-separated list |
| Sync Mode | 12% (min: 120px) | 20% | Hidden | Badge display |
| Actions | 8% (min: 100px) | 15% | Hidden | 3 buttons |

#### Provincial OBC Table (5 columns + actions)

| Column | Desktop Width | Tablet Width | Mobile Width | Rationale |
|--------|---------------|--------------|--------------|-----------|
| Province | 18% (min: 180px) | 35% | 100% | Name + display name |
| Region | 12% (min: 120px) | 25% | Hidden | 2-line region info |
| Coverage Snapshot | 22% (min: 200px) | Hidden | Hidden | 4-line stats |
| Top 5 Municipalities | 28% (min: 240px) | Hidden | Hidden | Longer municipality names |
| Sync Mode | 12% (min: 120px) | 25% | Hidden | Badge display |
| Actions | 8% (min: 100px) | 15% | Hidden | 3 buttons |

---

## Consistency Across Tables

### Achieved Consistency ✅

#### 1. Sync Mode Badges
- **Municipal and Provincial**: Identical implementation
- Emerald (border-emerald-200, bg-emerald-50, text-emerald-700) for Auto-sync
- Amber (border-amber-200, bg-amber-50, text-amber-700) for Manual
- Icon + text layout with gap-1, rounded-full, px-3 py-1

#### 2. Action Buttons
- **All tables**: View, Edit, Delete buttons
- Consistent permission checking via `can_manage_communities`
- Two-step delete confirmation pattern
- Review before deletion flow

#### 3. Icon Gradients
- **Barangay**: Blue gradient (from-blue-500 to-blue-600)
- **Municipal**: Indigo solid (bg-indigo-100 text-indigo-600)
- **Provincial**: Indigo solid (bg-indigo-100 text-indigo-600)

#### 4. Typography Hierarchy
- Primary text: text-sm font-semibold text-gray-900
- Secondary text: text-xs text-gray-500
- Location text (after improvement): text-base for Province/Region
- Consistent use of semantic colors (gray-900, gray-700, gray-600, gray-500)

### Remaining Inconsistencies ⚠️

#### 1. Icon Sizes
- **Barangay**: 40px × 40px (h-10 w-10)
- **Municipal/Provincial**: 44px × 44px (h-11 w-11)

**Recommendation**: Standardize all to 44px (h-11 w-11) for visual consistency

#### 2. Icon Style
- **Barangay**: Gradient background (bg-gradient-to-br from-blue-500 to-blue-600)
- **Municipal/Provincial**: Solid background (bg-indigo-100 text-indigo-600)

**Recommendation**: Decide on one approach:
- **Option A**: All use gradients (more visual interest)
- **Option B**: All use solid backgrounds (cleaner, more minimal)

#### 3. Top 5 Column Naming
- **Municipal**: "Top 5 Barangays"
- **Provincial**: "Top 5 Municipalities/Cities"

**Status**: ✅ Consistent (reflects hierarchical level appropriately)

#### 4. Empty State Indicators
- **Barangay**: No special empty state (uses generic message)
- **Municipal**: "—" dash for empty fields
- **Provincial**: "—" dash for empty fields + link to add

**Recommendation**: Standardize empty state treatment across all tables

---

## Areas for Improvement

### Priority: HIGH

#### 1. Implement Explicit Column Widths
**Problem**: Browser auto-width causes inconsistent layout
**Solution**: Add Tailwind width classes to column headers

**Implementation**:
```python
# In _build_barangay_table, communities_manage_municipal, communities_manage_provincial
headers = [
    {"label": "Community", "class": "w-1/4 min-w-[200px]"},
    {"label": "Location", "class": "w-[30%] min-w-[220px]"},
    {"label": "Coverage Snapshot", "class": "w-[35%] min-w-[240px]"},
]
```

**Template Update** (components/data_table_card.html):
```django
{% for header in headers %}
  <th class="... {{ header.class|default:'' }}">{{ header.label }}</th>
{% endfor %}
```

#### 2. Add Responsive Column Hiding
**Problem**: Too many columns on tablet/mobile causing squashing
**Solution**: Hide non-critical columns at smaller breakpoints

**Implementation**:
```python
headers = [
    {"label": "Municipality / City", "class": "w-[18%] min-w-[180px]"},
    {"label": "Province & Region", "class": "w-[15%] min-w-[150px] hidden lg:table-cell"},
    {"label": "Coverage Snapshot", "class": "w-[22%] min-w-[200px] hidden xl:table-cell"},
    {"label": "Top 5 Barangays", "class": "w-1/4 min-w-[220px] hidden 2xl:table-cell"},
    {"label": "Sync Mode", "class": "w-[12%] min-w-[120px] hidden lg:table-cell"},
]
```

**Breakpoints**:
- `lg:` (1024px+): Show all except "Top 5"
- `xl:` (1280px+): Show "Top 5" column
- `2xl:` (1536px+): Full table display

#### 3. Text Truncation for List Columns
**Problem**: "Top 5" columns can overflow with long names
**Solution**: Add line-clamp utility

**Implementation**:
```python
key_barangays_html = format_html(
    "<div class='text-sm text-gray-700 line-clamp-2'>{}</div>",
    coverage.key_barangays,
)
```

**CSS** (if line-clamp not available in Tailwind):
```css
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
```

### Priority: MEDIUM

#### 4. Standardize Icon Sizes
**Current**: Barangay (40px), Municipal/Provincial (44px)
**Target**: All 44px (h-11 w-11)

**Change Location**: `src/common/views/communities.py:246`

```python
# Before
"<span class='inline-flex h-10 w-10 items-center justify-center rounded-xl "

# After
"<span class='inline-flex h-11 w-11 items-center justify-center rounded-xl "
```

#### 5. Consistent Icon Style
**Decision Needed**: Gradient vs. Solid backgrounds

**Option A - All Gradients**:
```python
# Municipal/Provincial icons
"<span class='inline-flex h-11 w-11 items-center justify-center rounded-xl "
"bg-gradient-to-br from-indigo-500 to-indigo-600 text-white shadow-sm'>"
```

**Option B - All Solid** (recommended for consistency with stat cards):
```python
# Barangay icon
"<span class='inline-flex h-11 w-11 items-center justify-center rounded-xl "
"bg-blue-100 text-blue-600'>"
```

#### 6. Mobile Card Layout
**Problem**: Tables not optimized for mobile (<768px)
**Solution**: Implement card-based layout for small screens

**Template Addition** (each table partial):
```django
<!-- Desktop table (hidden on mobile) -->
<div class="hidden md:block">
    {% include "components/data_table_card.html" ... %}
</div>

<!-- Mobile cards (shown on mobile only) -->
<div class="md:hidden space-y-4">
    {% for row in rows %}
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
        <!-- Card content with vertical layout -->
    </div>
    {% endfor %}
</div>
```

### Priority: LOW

#### 7. Sortable Columns
**Enhancement**: Allow users to sort by different columns
**Complexity**: Requires backend sorting logic + HTMX updates

**Implementation Strategy**:
1. Add `sortable: true` to header definition
2. Add sort direction indicators (↑ ↓)
3. Backend: Handle `?sort=column&dir=asc|desc` query params
4. HTMX: Update table without full page reload

#### 8. Column Visibility Toggle
**Enhancement**: Let users show/hide columns
**Use Case**: Power users who want customized views

**Implementation Strategy**:
1. Add gear icon dropdown in table header
2. Checkbox list of columns
3. Store preferences in localStorage
4. Apply visibility classes dynamically

#### 9. Export Functionality
**Enhancement**: Export table data to CSV/Excel
**Location**: Add button to table header

**Implementation**:
```python
@login_required
def export_barangay_obc_csv(request):
    """Export filtered barangay OBC data to CSV."""
    # Apply same filters as main view
    # Generate CSV response
    pass
```

---

## Implementation Guide

### Step 1: Add Column Width Classes

**File**: `src/common/views/communities.py`

#### Barangay OBC Table

```python
# Around line 231
headers = [
    {"label": "Community", "class": "w-1/4 min-w-[200px]"},
    {"label": "Location", "class": "w-[30%] min-w-[220px]"},
    {"label": "Coverage Snapshot", "class": "w-[35%] min-w-[240px]"},
]
```

#### Municipal OBC Table

```python
# Around line 1132
municipality_table_headers = [
    {"label": "Municipality / City", "class": "w-[18%] min-w-[180px]"},
    {"label": "Province & Region", "class": "w-[15%] min-w-[150px]"},
    {"label": "Coverage Snapshot", "class": "w-[22%] min-w-[200px]"},
    {"label": "Top 5 Barangays", "class": "w-1/4 min-w-[220px]"},
    {"label": "Sync Mode", "class": "w-[12%] min-w-[120px]"},
]
```

#### Provincial OBC Table

```python
# Around line 1665
province_table_headers = [
    {"label": "Province", "class": "w-[18%] min-w-[180px]"},
    {"label": "Region", "class": "w-[12%] min-w-[120px]"},
    {"label": "Coverage Snapshot", "class": "w-[22%] min-w-[200px]"},
    {"label": "Top 5 Municipalities/Cities", "class": "w-[28%] min-w-[240px]"},
    {"label": "Sync Mode", "class": "w-[12%] min-w-[120px]"},
]
```

### Step 2: Update Data Table Component

**File**: `src/templates/components/data_table_card.html`

**Find** (around the `<th>` definition):
```django
<th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-white">
    {{ header.label }}
</th>
```

**Replace with**:
```django
<th scope="col" class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-white {{ header.class|default:'' }}">
    {{ header.label }}
</th>
```

### Step 3: Add Responsive Hiding (Optional)

Update header definitions to include responsive classes:

```python
municipality_table_headers = [
    {"label": "Municipality / City", "class": "w-[18%] min-w-[180px]"},
    {"label": "Province & Region", "class": "w-[15%] min-w-[150px] hidden lg:table-cell"},
    {"label": "Coverage Snapshot", "class": "w-[22%] min-w-[200px] hidden xl:table-cell"},
    {"label": "Top 5 Barangays", "class": "w-1/4 min-w-[220px] hidden 2xl:table-cell"},
    {"label": "Sync Mode", "class": "w-[12%] min-w-[120px] hidden lg:table-cell"},
]
```

**Also apply to corresponding `<td>` cells** in row generation:

```python
row = {
    "cells": [
        {"content": municipality_html, "class": ""},  # Always visible
        {"content": province_html, "class": "hidden lg:table-cell"},
        {"content": snapshot_html, "class": "hidden xl:table-cell"},
        {"content": key_barangays_html, "class": "hidden 2xl:table-cell"},
        {"content": sync_html, "class": "hidden lg:table-cell"},
    ],
    # ...
}
```

**Update data_table_card.html**:
```django
<td class="px-6 py-4 text-sm text-gray-700 {{ cell.class|default:'' }}">
    {{ cell.content|safe }}
</td>
```

### Step 4: Add Text Truncation

**File**: `src/common/views/communities.py`

**Municipal - Top 5 Barangays** (around line 1271):
```python
if getattr(coverage, "key_barangays", ""):
    key_barangays_html = format_html(
        "<div class='text-sm text-gray-700 line-clamp-2' title='{}'>{}</div>",
        coverage.key_barangays,  # Full text in tooltip
        coverage.key_barangays,
    )
```

**Provincial - Top 5 Municipalities** (around line 1743):
```python
if getattr(coverage, "key_municipalities", ""):
    key_municipalities_html = format_html(
        "<div class='text-sm text-gray-700 line-clamp-2' title='{}'>{}</div>",
        coverage.key_municipalities,
        coverage.key_municipalities,
    )
```

**Add CSS for line-clamp** if not available:
```css
/* src/static/common/css/custom.css */
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
}
```

### Step 5: Testing Checklist

After implementing width improvements:

- [ ] Desktop (1920px): All columns visible with proper proportions
- [ ] Desktop (1440px): All columns visible, no squashing
- [ ] Laptop (1280px): Acceptable layout (may hide "Top 5" if responsive)
- [ ] Tablet (1024px): Key columns visible, others hidden
- [ ] Tablet (768px): Name + critical info only
- [ ] Mobile (414px): Consider card layout or horizontal scroll
- [ ] Text truncation: Long names/lists show ellipsis
- [ ] Tooltips: Hover shows full text when truncated
- [ ] Print view: All columns visible without CSS hiding

---

## Technical Reference

### Backend View Functions

1. **Barangay OBC**: `src/common/views/communities.py:815-948`
   - Function: `communities_manage(request)`
   - Table builder: `_build_barangay_table(communities_page, *, can_manage: bool)` (line 228)
   - Returns: `barangay_table` dict with headers/rows/show_actions

2. **Municipal OBC**: `src/common/views/communities.py:947-1386`
   - Function: `communities_manage_municipal(request)`
   - Inline table building (lines 1132-1349)
   - Returns: `municipality_table` dict with headers/rows/show_actions

3. **Provincial OBC**: `src/common/views/communities.py:1389-1791`
   - Function: `communities_manage_provincial(request)`
   - Inline table building (lines 1665-1816)
   - Returns: `province_table_headers`, `province_table_rows` (separate variables)

### Template Files

1. **Barangay OBC**: `src/templates/communities/partials/barangay_manage_results.html`
   - Line 37: Includes data_table_card.html
   - Uses: `barangay_table.headers`, `barangay_table.rows`, `barangay_table.show_actions`

2. **Municipal OBC**: `src/templates/communities/partials/municipal_manage_results.html`
   - Line 32: Includes data_table_card.html
   - Uses: `table.headers`, `table.rows`, `table.show_actions`

3. **Provincial OBC**: `src/templates/communities/partials/provincial_manage_results.html`
   - Line 3: Includes data_table_card.html
   - Uses: `province_table_headers`, `province_table_rows`, `can_manage_communities`

### Component Template

**File**: `src/templates/components/data_table_card.html`

**Expected Context Variables**:
```python
{
    'title': str,              # Table title
    'icon_class': str,         # Font Awesome icon class
    'accent_class': str,       # Gradient class for header
    'headers': list[dict],     # [{"label": str, "class": str}]
    'rows': list[dict],        # [{"cells": [...], "view_url": str, ...}]
    'show_actions': bool,      # Display action buttons column
    'empty_message': str,      # Message when no rows
}
```

**Row Structure**:
```python
{
    "cells": [
        {"content": str|SafeString, "class": str},  # HTML content + optional CSS
        ...
    ],
    "view_url": str,           # View detail page URL
    "edit_url": str,           # Edit page URL (optional)
    "delete_preview_url": str, # Delete confirmation URL (optional)
    "delete_message": str,     # Delete confirmation message (optional)
    "restore_url": str,        # Restore from archive URL (optional)
}
```

### Database Models

1. **OBCCommunity**: `src/communities/models.py`
   - Represents barangay-level OBC records
   - Fields: estimated_obc_population, total_barangay_population, households, etc.

2. **MunicipalityCoverage**: `src/communities/models.py`
   - Aggregates barangay data to municipality level
   - Fields: total_obc_communities, estimated_obc_population, key_barangays, auto_sync

3. **ProvinceCoverage**: `src/communities/models.py`
   - Aggregates municipality data to province level
   - Fields: total_municipalities, total_obc_communities, key_municipalities, auto_sync

### URL Patterns

```python
# Barangay OBC
path('communities/manage/', views.communities_manage, name='communities_manage')

# Municipal OBC
path('communities/managemunicipal/', views.communities_manage_municipal, name='communities_manage_municipal')

# Provincial OBC
path('communities/manageprovincial/', views.communities_manage_provincial, name='communities_manage_provincial')
```

---

## Change Log

### 2025-10-12 - Code Cleanup and Action Buttons Fix
- **Removed**: Ethnolinguistic/languages dead code from Barangay table
- **Removed**: History/Last Updated dead code from Municipal table
- **Improved**: Province and Region font size in Barangay Location column (14px → 16px)
- **Fixed**: Missing `show_actions` parameter in Municipal table template
- **Fixed**: Hardcoded `show_actions=True` in Provincial table (now uses permission check)

### Future Changes (Planned)
- **TBD**: Implement explicit column width classes
- **TBD**: Add responsive column hiding for tablet/mobile
- **TBD**: Add text truncation for "Top 5" list columns
- **TBD**: Standardize icon sizes across all tables (all 44px)
- **TBD**: Decide on icon style (gradient vs. solid)

---

## Related Documentation

- **UI Components Guide**: `docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`
- **Stat Cards Template**: `docs/improvements/UI/STATCARD_TEMPLATE.md`
- **Data Table Card Component**: `src/templates/components/data_table_card.html`
- **Form Design Standards**: See CLAUDE.md section "Form Design Standards"

---

## Questions or Issues?

If you encounter issues or have suggestions for improving the OBC database table presentation:

1. Check this documentation first
2. Review the UI Components Standards guide
3. Test changes on multiple screen sizes (mobile, tablet, desktop)
4. Ensure consistency across all three tables
5. Update this documentation with your changes

---

**Document Version**: 1.0
**Author**: Claude Code
**Approved By**: OOBC Development Team
