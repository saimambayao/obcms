# Stat Card Auto-Refresh Implementation Guide

**Date:** 2025-10-02
**Status:** 🚀 Ready for Implementation
**Reference:** [STATCARD_TEMPLATE.md](STATCARD_TEMPLATE.md#-auto-refresh-with-htmx-live-updates)

---

## Overview

This guide shows how to add **real-time auto-refresh** functionality to stat cards across OBCMS. Stats will update every 60 seconds without page reload using HTMX.

**Benefits:**
- ⚡ Real-time dashboard updates
- 🎯 Better user experience
- 📊 Live metric visibility
- 🔄 No manual refresh needed
- ⚙️ Efficient (only fetches stats, not full page)

---

## Quick Start Example: Dashboard

### Step 1: Create Partial Template

Create `src/templates/partials/dashboard_stats_cards.html`:

```html
<!-- Dashboard Stat Cards (Partial for HTMX) -->
<!-- Total OBC Communities -->
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
     style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
    <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>
    <div class="relative p-6">
        <div class="flex items-center justify-between mb-3">
            <div>
                <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">Total OBC Communities</p>
                <p class="text-4xl font-extrabold text-gray-800 mt-1">{{ stats.communities.total|default:0 }}</p>
            </div>
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                 style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                <i class="fas fa-mosque text-2xl text-blue-600"></i>
            </div>
        </div>
        <div class="grid grid-cols-2 gap-2 pt-3 border-t border-gray-200/60">
            <div class="text-center">
                <p class="text-xl font-bold text-gray-700">{{ stats.communities.barangay_total|default:0 }}</p>
                <p class="text-xs text-gray-500 font-medium">Barangay OBCs</p>
            </div>
            <div class="text-center">
                <p class="text-xl font-bold text-gray-700">{{ stats.communities.municipal_total|default:0 }}</p>
                <p class="text-xs text-gray-500 font-medium">Municipal OBCs</p>
            </div>
        </div>
    </div>
</div>

<!-- MANA Assessments -->
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl transform hover:-translate-y-2 transition-all duration-300"
     style="box-shadow: 0 8px 20px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.06), inset 0 -2px 4px rgba(0,0,0,0.02), inset 0 2px 4px rgba(255,255,255,0.9);">
    <div class="absolute inset-0 bg-gradient-to-br from-white/60 via-transparent to-gray-100/20"></div>
    <div class="relative p-6">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-gray-600 text-sm font-semibold uppercase tracking-wide">MANA Assessments</p>
                <p class="text-4xl font-extrabold text-gray-800 mt-1">{{ stats.mana.total_assessments|default:0 }}</p>
            </div>
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
                 style="background: linear-gradient(135deg, #FFFFFF 0%, #F5F3F0 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.05), inset 0 2px 4px rgba(255,255,255,0.8);">
                <i class="fas fa-chart-bar text-2xl text-emerald-600"></i>
            </div>
        </div>
    </div>
</div>

<!-- Add remaining cards... -->
```

**IMPORTANT:** Partial template contains **ONLY the stat cards** (div elements), NO wrapper grid!

### Step 2: Create Django View

Add to `src/common/views.py`:

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from communities.models import BarangayOBC, MunicipalOBC
from mana.models import Assessment
from coordination.models import Partnership
from policies.models import PolicyRecommendation

@login_required
def dashboard_stats_cards(request):
    """Return just the dashboard stat cards for HTMX refresh"""

    # Calculate stats
    barangay_total = BarangayOBC.objects.count()
    municipal_total = MunicipalOBC.objects.count()

    context = {
        'stats': {
            'communities': {
                'total': barangay_total + municipal_total,
                'barangay_total': barangay_total,
                'municipal_total': municipal_total,
            },
            'mana': {
                'total_assessments': Assessment.objects.count(),
            },
            'coordination': {
                'active_partnerships': Partnership.objects.filter(status='active').count(),
                'bmoas': Partnership.objects.filter(partner_type='bmoa').count(),
                'ngas': Partnership.objects.filter(partner_type='nga').count(),
                'lgus': Partnership.objects.filter(partner_type='lgu').count(),
            },
            'policy_tracking': {
                'total_recommendations': PolicyRecommendation.objects.count(),
                'policies': PolicyRecommendation.objects.filter(category='policy').count(),
                'programs': PolicyRecommendation.objects.filter(category='program').count(),
                'services': PolicyRecommendation.objects.filter(category='service').count(),
            },
            'monitoring': {
                'total': 0,  # Add actual monitoring model query
                'pending_requests': 0,
                'avg_progress': 0,
            },
        }
    }

    return render(request, 'partials/dashboard_stats_cards.html', context)
```

### Step 3: Add URL Pattern

Add to `src/common/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    # ... existing URLs ...
    path('dashboard/stats-cards/', views.dashboard_stats_cards, name='dashboard_stats_cards'),
]
```

### Step 4: Update Main Template

Update `src/templates/common/dashboard.html`:

**Before:**
```html
<!-- System Overview Statistics - 3D Milk White Design -->
<div class="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- Stat cards here... -->
</div>
```

**After:**
```html
<!-- System Overview Statistics - Auto-refresh every 60s -->
<div class="mb-8">
    <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-bold text-gray-900">System Overview</h2>
        <span class="text-xs text-gray-500">
            <i class="fas fa-sync-alt"></i> Updates every 60s
        </span>
    </div>

    <div hx-get="{% url 'common:dashboard_stats_cards' %}"
         hx-trigger="load, every 60s"
         hx-swap="innerHTML swap:300ms"
         class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Loading state -->
        <div class="col-span-full flex items-center justify-center py-12">
            <i class="fas fa-spinner fa-spin text-gray-400 text-2xl"></i>
        </div>
    </div>
</div>
```

---

## Implementation for Other Modules

### Recommendations Module

**1. Create** `src/templates/partials/recommendations_stats_cards.html`
**2. Create view:** `src/policies/views.py` → `recommendations_stats_cards()`
**3. Add URL:** `src/policies/urls.py` → `path('recommendations/stats-cards/', ...)`
**4. Update:** `src/templates/recommendations/recommendations_home.html`

```python
# src/policies/views.py
@login_required
def recommendations_stats_cards(request):
    from policies.models import PolicyRecommendation

    context = {
        'stats': {
            'recommendations': {
                'total': PolicyRecommendation.objects.count(),
                'implemented': PolicyRecommendation.objects.filter(status='implemented').count(),
                'submitted': PolicyRecommendation.objects.filter(status='submitted').count(),
                'proposed': PolicyRecommendation.objects.filter(status='proposed').count(),
                # Breakdown
                'policies': PolicyRecommendation.objects.filter(category='policy').count(),
                'programs': PolicyRecommendation.objects.filter(category='program').count(),
                'services': PolicyRecommendation.objects.filter(category='service').count(),
                'implemented_policies': PolicyRecommendation.objects.filter(
                    status='implemented', category='policy'
                ).count(),
                # ... etc
            }
        }
    }
    return render(request, 'partials/recommendations_stats_cards.html', context)
```

### MANA Module

**1. Create** `src/templates/partials/mana_stats_cards.html`
**2. Create view:** `src/mana/views.py` → `mana_stats_cards()`
**3. Add URL:** `src/mana/urls.py` → `path('mana/stats-cards/', ...)`
**4. Update:** `src/templates/mana/mana_home.html`

```python
# src/mana/views.py
@login_required
def mana_stats_cards(request):
    from mana.models import Assessment

    context = {
        'stats': {
            'mana': {
                'total_assessments': Assessment.objects.count(),
                'completed': Assessment.objects.filter(status='completed').count(),
                'in_progress': Assessment.objects.filter(status='in_progress').count(),
                'planned': Assessment.objects.filter(status='planned').count(),
            }
        }
    }
    return render(request, 'partials/mana_stats_cards.html', context)
```

---

## Template Pattern

**For each module, follow this structure:**

### Main Template Pattern
```html
{% extends 'base.html' %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

    <!-- Hero Section -->
    <section class="...">
        <!-- Module hero content -->
    </section>

    <!-- Statistics Cards - Auto-refresh -->
    <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-gray-900">Statistics</h2>
            <span class="text-xs text-gray-500">
                <i class="fas fa-sync-alt"></i> Updates every 60s
            </span>
        </div>

        <div hx-get="{% url 'app:module_stats_cards' %}"
             hx-trigger="load, every 60s"
             hx-swap="innerHTML swap:300ms"
             class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Loading spinner -->
            <div class="col-span-full flex items-center justify-center py-12">
                <i class="fas fa-spinner fa-spin text-gray-400 text-2xl"></i>
            </div>
        </div>
    </div>

    <!-- Rest of content -->
</div>
{% endblock %}
```

### Partial Template Pattern
```html
<!-- partials/module_stats_cards.html -->
<!-- Card 1 -->
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl ...">
    <!-- 3D milk white stat card content -->
</div>

<!-- Card 2 -->
<div class="relative overflow-hidden bg-gradient-to-br from-[#FEFDFB] to-[#FBF9F5] rounded-2xl ...">
    <!-- 3D milk white stat card content -->
</div>

<!-- Card 3... -->
```

---

## Testing Checklist

After implementing auto-refresh:

- [ ] **Visual Test:** Open page, confirm stat cards load
- [ ] **Refresh Test:** Wait 60 seconds, verify cards update
- [ ] **Network Test:** Open browser DevTools > Network, confirm AJAX request every 60s
- [ ] **Loading State:** Refresh page, confirm spinner shows briefly
- [ ] **Smooth Transition:** Verify no layout shift during update
- [ ] **Data Accuracy:** Confirm numbers match database
- [ ] **Error Handling:** Test with network disconnected (should show old data)
- [ ] **Performance:** Check query execution time (should be < 100ms)

---

## Rollout Priority

Implement auto-refresh in this order:

### Phase 1: Core Dashboards (HIGH)
1. ✅ **Main Dashboard** (`common/dashboard.html`) - 5 cards
2. **MANA Home** (`mana/mana_home.html`) - 4 cards
3. **Communities Home** (`communities/communities_home.html`) - 3 cards
4. **Coordination Home** (`coordination/coordination_home.html`) - 4 cards
5. **Recommendations Home** (`recommendations/recommendations_home.html`) - 4 cards

### Phase 2: Management Dashboards (MEDIUM)
6. **OOBC Management** (`common/oobc_management_home.html`) - 4 cards
7. **Monitoring Dashboard** (`monitoring/dashboard.html`) - Dynamic cards

### Phase 3: Specialized Dashboards (LOW)
8. **Project Central** dashboards
9. **Calendar** views with stats
10. **Staff Management** views

---

## Performance Optimization

### Caching (Recommended)

Add caching to reduce database load:

```python
from django.core.cache import cache

@login_required
def dashboard_stats_cards(request):
    cache_key = f'dashboard_stats_{request.user.id}'
    stats = cache.get(cache_key)

    if not stats:
        # Calculate stats
        stats = {
            'communities': {
                'total': BarangayOBC.objects.count() + MunicipalOBC.objects.count(),
                # ...
            }
        }
        # Cache for 30 seconds (half the refresh interval)
        cache.set(cache_key, stats, timeout=30)

    context = {'stats': stats}
    return render(request, 'partials/dashboard_stats_cards.html', context)
```

### Database Indexing

Ensure these fields are indexed:
- `status` fields (for filtering)
- `category` fields (for grouping)
- Foreign key fields (automatic)

### Query Optimization

Use `.count()` instead of `len()`:
```python
# ❌ Slow
total = len(Assessment.objects.all())

# ✅ Fast
total = Assessment.objects.count()
```

---

## Troubleshooting

### Issue: Stats don't refresh

**Solution:** Check HTMX is loaded in base template:
```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

### Issue: Loading spinner shows forever

**Solution:** Verify:
1. URL pattern is correct
2. View returns template (not redirect)
3. Template path is correct
4. No Python errors (check logs)

### Issue: Layout shifts during refresh

**Solution:** Ensure:
1. Grid classes match in main template and partial
2. Card heights are consistent
3. Use `swap:300ms` for smooth transition

---

## Next Steps

1. **Implement Phase 1** (core dashboards)
2. **Test thoroughly** (visual + functional)
3. **Add caching** (if needed for performance)
4. **Monitor** browser console for errors
5. **Document** any module-specific variations

---

**Documentation:**
- [Stat Card Template](STATCARD_TEMPLATE.md)
- [Implementation Tracker](STATCARD_IMPLEMENTATION_TRACKER.md)
- [Implementation Progress](STATCARD_IMPLEMENTATION_PROGRESS.md)

**Support:** For questions, refer to HTMX documentation at https://htmx.org
