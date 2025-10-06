# Consistent Dashboard Implementation Plan

**Date**: October 2, 2025
**Status**: Implementation Specifications
**Purpose**: Standardize all module entry dashboards with consistent patterns
**Related**: [OBCMS UI Structure Analysis](OBCMS_UI_STRUCTURE_ANALYSIS.md)

---

## 🎯 **DESIGN PRINCIPLES**

### **Core Requirements** (User-Specified)

Every module dashboard/home page MUST have:

1. **📊 Dashboard Stat Cards** - Key metrics at a glance
2. **🎯 Hero Section** - Module mission control with gradient banner, inline stats, and primary actions
3. **🔔 Recent Updates/Activities & Upcoming Events** - Temporal awareness
4. **⚡ Context-Aware Quick Actions Section** - Submodules and related links
5. **🔗 Related Modules/Workflows** - Cross-module contextual integration

### **Success Criteria**

✅ **Visual Consistency** - All dashboards use same layout structure
✅ **Predictable Navigation** - Users know where to find what
✅ **Contextual Discovery** - Related features surfaced intelligently
✅ **Actionable** - Primary actions always accessible

---

## 📐 **STANDARDIZED TEMPLATE STRUCTURE**

### **Universal Dashboard Pattern**

```html
<!-- Every module dashboard follows this structure -->

┌────────────────────────────────────────────────────────────────┐
│ 1. HEADER SECTION (Simple breadcrumb area)                     │
│    - Breadcrumb navigation                                     │
│    - Page title (h1)                                           │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 2. STAT CARDS GRID (4 columns responsive)                      │
│    [Card 1] [Card 2] [Card 3] [Card 4]                        │
│    - Gradient backgrounds                                       │
│    - Icon, label, value                                        │
│    - Sub-metrics if applicable                                 │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 3. HERO SECTION (Module Mission Control) ⭐ NEW               │
│                                                                 │
│    Gradient Banner (green-to-blue or module-specific colors)   │
│    ┌──────────────────────────────────────────────────────┐   │
│    │ 🏷 [CONTEXT BADGE]                                    │   │
│    │                                                        │   │
│    │ MODULE NAME HEADLINE                                  │   │
│    │ Value proposition description explaining the module's │   │
│    │ purpose and key capabilities                          │   │
│    │                                                        │   │
│    │ ┌─────────┐ ┌─────────┐ ┌─────────┐   [Action 1]    │   │
│    │ │Inline   │ │Inline   │ │Inline   │   [Action 2]    │   │
│    │ │Stat 1   │ │Stat 2   │ │Stat 3   │   [Action 3]    │   │
│    │ │  Value  │ │  Value  │ │  Value  │   [Action 4]    │   │
│    │ └─────────┘ └─────────┘ └─────────┘   [Action 5]    │   │
│    └──────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 4. RECENT ACTIVITIES & UPCOMING EVENTS (2-column grid)         │
│                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────┐     │
│  │ 📋 Recent Activities     │  │ 📅 Upcoming Events      │     │
│  │ - Timeline feed          │  │ - Event list (next 7)   │     │
│  │ - Last 10 updates        │  │ - With dates            │     │
│  │ - "View All" link        │  │ - "View Calendar" link  │     │
│  └─────────────────────────┘  └─────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 5. QUICK ACTIONS / SUBMODULES SECTION (Feature Cards Grid)     │
│                                                                 │
│    [Feature 1]    [Feature 2]    [Feature 3]    [Feature 4]   │
│    Icon           Icon           Icon           Icon           │
│    Title          Title          Title          Title          │
│    Description    Description    Description    Description    │
│    [Launch →]     [Launch →]     [Launch →]     [Launch →]    │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ 6. RELATED MODULES INTEGRATION CTA (Like MOA PPAs ✅)          │
│                                                                 │
│    Gradient banner with:                                       │
│    - Related module description                                │
│    - Quick access buttons (4-6 links)                          │
│    - "Learn More" or "View Dashboard" primary CTA             │
└────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ **TEMPLATE CODE BLUEPRINT**

### **Base Template Structure**

```html
{% extends 'base.html' %}

{% block title %}[Module Name] - OBC Management System{% endblock %}

{% block breadcrumb %}
<li>
    <a href="{% url 'common:dashboard' %}" class="text-neutral-500 hover:text-neutral-700">Dashboard</a>
</li>
<li><span class="text-neutral-400 mx-1">/</span></li>
<li class="text-neutral-800 font-semibold">[Module Name]</li>
{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8">

    <!-- ========================================= -->
    <!-- 1. HEADER SECTION -->
    <!-- ========================================= -->
    <header class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">[Module Name]</h1>
            <p class="mt-2 text-lg text-gray-600 max-w-3xl">
                [Module description and purpose]
            </p>
        </div>
        <div class="flex items-center gap-3">
            <a href="[primary-action-url]" class="btn-primary inline-flex items-center px-4 py-2 rounded-lg text-white font-medium hover-lift">
                <i class="fas fa-[icon] mr-2"></i>
                [Primary Action]
            </a>
            <!-- Optional: Secondary action button -->
        </div>
    </header>

    <!-- ========================================= -->
    <!-- 2. STAT CARDS GRID -->
    <!-- ========================================= -->
    <section class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

        <!-- Stat Card Template -->
        <div class="relative overflow-hidden bg-gradient-to-br from-[color]-500 via-[color]-600 to-[color]-700 rounded-xl shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent"></div>
            <div class="relative p-6 text-white">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <p class="text-[color]-100 text-sm font-medium">[Metric Label]</p>
                        <p class="text-3xl font-bold">{{ stats.[metric]|default:0 }}</p>
                    </div>
                    <div class="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                        <i class="fas fa-[icon] text-2xl"></i>
                    </div>
                </div>

                <!-- Optional: Sub-metrics grid (if card has breakdown) -->
                <div class="grid grid-cols-3 gap-2 pt-3 border-t border-[color]-400/30">
                    <div class="text-center">
                        <p class="text-xl font-bold">{{ stats.[sub1]|default:0 }}</p>
                        <p class="text-xs text-[color]-100">[Label 1]</p>
                    </div>
                    <div class="text-center">
                        <p class="text-xl font-bold">{{ stats.[sub2]|default:0 }}</p>
                        <p class="text-xs text-[color]-100">[Label 2]</p>
                    </div>
                    <div class="text-center">
                        <p class="text-xl font-bold">{{ stats.[sub3]|default:0 }}</p>
                        <p class="text-xs text-[color]-100">[Label 3]</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Repeat stat cards (4 total recommended) -->

    </section>

    <!-- ========================================= -->
    <!-- 3. HERO SECTION (Module Mission Control) ⭐ -->
    <!-- ========================================= -->
    <section class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[color1]-500 via-[color2]-500 to-[color3]-600 shadow-2xl">
        <!-- Background decoration -->
        <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>
        <div class="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -mr-48 -mt-48"></div>
        <div class="absolute bottom-0 left-0 w-72 h-72 bg-white/5 rounded-full -ml-36 -mb-36"></div>

        <!-- Content -->
        <div class="relative px-6 sm:px-10 py-8 sm:py-10">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

                <!-- Left: Module branding and stats -->
                <div class="flex-1 space-y-6">
                    <!-- Context Badge -->
                    <div class="inline-flex items-center rounded-lg bg-white/20 backdrop-blur-sm px-3 py-1.5 text-sm font-semibold text-white border border-white/30">
                        <i class="fas fa-[badge-icon] mr-2"></i>
                        [CONTEXT BADGE TEXT]
                    </div>

                    <!-- Headline -->
                    <h2 class="text-3xl sm:text-4xl font-bold text-white leading-tight">
                        [Module Headline]
                    </h2>

                    <!-- Description -->
                    <p class="text-white/90 text-base sm:text-lg max-w-2xl leading-relaxed">
                        [Module description explaining purpose, value proposition, and key capabilities]
                    </p>

                    <!-- Inline Stats -->
                    <div class="flex flex-wrap gap-4">
                        <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                            <p class="text-sm text-white/70 uppercase tracking-wide">[Stat 1 Label]</p>
                            <p class="text-2xl font-bold text-white">{{ hero_stats.stat1|default:0 }}</p>
                        </div>
                        <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                            <p class="text-sm text-white/70 uppercase tracking-wide">[Stat 2 Label]</p>
                            <p class="text-2xl font-bold text-white">{{ hero_stats.stat2|default:0 }}</p>
                        </div>
                        <div class="bg-white/15 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/20">
                            <p class="text-sm text-white/70 uppercase tracking-wide">[Stat 3 Label]</p>
                            <p class="text-2xl font-bold text-white">{{ hero_stats.stat3|default:0 }}</p>
                        </div>
                    </div>
                </div>

                <!-- Right: Primary Action Buttons -->
                <div class="flex-shrink-0">
                    <div class="flex flex-col gap-3 min-w-[220px]">
                        <!-- Primary Action -->
                        <a href="[action1-url]" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white text-[color]-600 font-semibold shadow-lg hover:bg-[color]-50 hover:shadow-xl transition-all duration-200">
                            <i class="fas fa-[icon1]"></i>
                            <span>[Action 1 Label]</span>
                        </a>

                        <!-- Secondary Actions -->
                        <a href="[action2-url]" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all duration-200">
                            <i class="fas fa-[icon2]"></i>
                            <span>[Action 2 Label]</span>
                        </a>

                        <a href="[action3-url]" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/20 backdrop-blur-sm text-white font-semibold border border-white/30 hover:bg-white/30 transition-all duration-200">
                            <i class="fas fa-[icon3]"></i>
                            <span>[Action 3 Label]</span>
                        </a>

                        <!-- Optional: More actions (4-6 total recommended) -->
                        <a href="[action4-url]" class="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-white/10 backdrop-blur-sm text-white font-medium border border-white/20 hover:bg-white/20 transition-all duration-200">
                            <i class="fas fa-[icon4]"></i>
                            <span>[Action 4 Label]</span>
                        </a>
                    </div>
                </div>

            </div>
        </div>
    </section>

    <!-- ========================================= -->
    <!-- 4. RECENT ACTIVITIES & UPCOMING EVENTS -->
    <!-- ========================================= -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Recent Activities Panel -->
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <i class="fas fa-clock-rotate-left text-blue-500 mr-2"></i>
                    Recent Activities
                </h2>
            </div>
            <div class="p-6">
                {% if recent_activities %}
                <div class="space-y-4">
                    {% for activity in recent_activities|slice:":10" %}
                    <div class="flex items-start gap-4 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                        <div class="flex-shrink-0">
                            <div class="w-10 h-10 rounded-full bg-[color]-100 flex items-center justify-center">
                                <i class="fas fa-[icon] text-[color]-600"></i>
                            </div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium text-gray-900 truncate">
                                {{ activity.title }}
                            </p>
                            <p class="text-xs text-gray-500 mt-1">
                                {{ activity.description|truncatewords:15 }}
                            </p>
                            <p class="text-xs text-gray-400 mt-1">
                                <i class="far fa-clock mr-1"></i>
                                {{ activity.created_at|timesince }} ago
                            </p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                <div class="mt-4 text-center">
                    <a href="[view-all-url]" class="text-sm text-blue-600 hover:text-blue-800 font-medium">
                        View All Activities →
                    </a>
                </div>
                {% else %}
                <div class="text-center py-8">
                    <i class="fas fa-inbox text-gray-300 text-4xl mb-3"></i>
                    <p class="text-gray-500">No recent activities</p>
                </div>
                {% endif %}
            </div>
        </div>

        <!-- Upcoming Events Panel -->
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                    <i class="fas fa-calendar-days text-emerald-500 mr-2"></i>
                    Upcoming Events
                </h2>
            </div>
            <div class="p-6">
                {% if upcoming_events %}
                <div class="space-y-3">
                    {% for event in upcoming_events|slice:":7" %}
                    <a href="[event-detail-url]" class="block p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200">
                        <div class="flex items-start gap-3">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500 flex flex-col items-center justify-center text-white text-xs font-bold">
                                    <span class="text-lg">{{ event.start_date|date:"d" }}</span>
                                    <span class="text-[10px] uppercase">{{ event.start_date|date:"M" }}</span>
                                </div>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-semibold text-gray-900 truncate">
                                    {{ event.title }}
                                </p>
                                <p class="text-xs text-gray-600 mt-1">
                                    <i class="far fa-clock mr-1"></i>
                                    {{ event.start_date|date:"M d, Y • g:i A" }}
                                </p>
                                {% if event.location %}
                                <p class="text-xs text-gray-500 mt-1">
                                    <i class="fas fa-map-marker-alt mr-1"></i>
                                    {{ event.location|truncatewords:5 }}
                                </p>
                                {% endif %}
                            </div>
                        </div>
                    </a>
                    {% endfor %}
                </div>
                <div class="mt-4 text-center">
                    <a href="[calendar-url]" class="text-sm text-emerald-600 hover:text-emerald-800 font-medium">
                        View Full Calendar →
                    </a>
                </div>
                {% else %}
                <div class="text-center py-8">
                    <i class="fas fa-calendar-xmark text-gray-300 text-4xl mb-3"></i>
                    <p class="text-gray-500">No upcoming events</p>
                    <a href="[add-event-url]" class="text-sm text-blue-600 hover:text-blue-800 font-medium mt-2 inline-block">
                        Schedule an Event →
                    </a>
                </div>
                {% endif %}
            </div>
        </div>

    </section>

    <!-- ========================================= -->
    <!-- 4. QUICK ACTIONS / SUBMODULES SECTION -->
    <!-- ========================================= -->
    <section>
        <div class="mb-6">
            <h2 class="text-2xl font-bold text-gray-900 flex items-center">
                <i class="fas fa-bolt text-yellow-500 mr-3"></i>
                Quick Actions
            </h2>
            <p class="text-gray-600 mt-1">Access key [module] features and tools</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

            <!-- Feature Card Template -->
            <a href="[feature-url]" class="group block bg-white rounded-xl border-2 border-gray-200 hover:border-blue-400 shadow-sm hover:shadow-lg transition-all duration-200">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-4">
                        <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-[color]-400 to-[color]-600 flex items-center justify-center text-white shadow-lg">
                            <i class="fas fa-[icon] text-2xl"></i>
                        </div>
                        <i class="fas fa-arrow-right text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all"></i>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">
                        [Feature Title]
                    </h3>
                    <p class="text-sm text-gray-600 mb-4">
                        [Feature description in 1-2 sentences]
                    </p>
                    <div class="flex items-center text-sm text-blue-600 font-medium">
                        <span>Launch Tool</span>
                        <i class="fas fa-chevron-right ml-1 text-xs"></i>
                    </div>
                </div>
            </a>

            <!-- Repeat feature cards (4-8 cards recommended) -->

        </div>
    </section>

    <!-- ========================================= -->
    <!-- 5. RELATED MODULES INTEGRATION CTA -->
    <!-- ========================================= -->
    <section class="relative overflow-hidden rounded-3xl border border-[color]-200/60 bg-gradient-to-r from-[color1]-600 via-[color2]-500 to-[color3]-500 text-white shadow-xl">
        <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>

        <div class="relative px-6 sm:px-10 py-8 sm:py-10">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">

                <!-- Left: Description -->
                <div class="space-y-4 max-w-2xl">
                    <div class="inline-flex items-center rounded-full bg-white/15 px-3 py-1 text-sm font-semibold backdrop-blur">
                        <i class="fa-solid fa-[icon] mr-2"></i>
                        [Related Module Category]
                    </div>
                    <h2 class="text-3xl sm:text-4xl font-semibold leading-tight">
                        [Integration Headline]
                    </h2>
                    <p class="text-white/80 text-base sm:text-lg">
                        [Integration description explaining the relationship and value]
                    </p>
                </div>

                <!-- Right: Quick Access Panel -->
                <div class="w-full max-w-sm">
                    <div class="rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20 p-6 shadow-lg space-y-3">
                        <h3 class="text-sm font-semibold uppercase tracking-wide text-white/70">Quick Access</h3>

                        <!-- Quick Link 1 -->
                        <a href="[link1-url]" class="flex items-center justify-between rounded-xl bg-white text-[color]-600 font-semibold px-4 py-3 shadow hover:bg-[color]-50 transition-all duration-200">
                            <span class="flex items-center gap-2">
                                <i class="fa-solid fa-[icon]"></i> [Link 1 Title]
                            </span>
                            <i class="fa-solid fa-arrow-right"></i>
                        </a>

                        <!-- Quick Link 2 -->
                        <a href="[link2-url]" class="flex items-center justify-between rounded-xl bg-[color]-500/70 hover:bg-[color]-500 text-white font-semibold px-4 py-3 transition-all duration-200">
                            <span class="flex items-center gap-2">
                                <i class="fa-solid fa-[icon]"></i> [Link 2 Title]
                            </span>
                            <i class="fa-solid fa-arrow-right"></i>
                        </a>

                        <!-- Quick Link 3 -->
                        <a href="[link3-url]" class="flex items-center justify-between rounded-xl bg-white/15 hover:bg-white/25 text-white font-semibold px-4 py-3 border border-white/20 transition-all duration-200">
                            <span class="flex items-center gap-2">
                                <i class="fa-solid fa-[icon]"></i> [Link 3 Title]
                            </span>
                            <i class="fa-solid fa-arrow-right"></i>
                        </a>

                        <!-- Quick Link 4 -->
                        <a href="[link4-url]" class="flex items-center justify-between rounded-xl bg-white/15 hover:bg-white/25 text-white font-semibold px-4 py-3 border border-white/20 transition-all duration-200">
                            <span class="flex items-center gap-2">
                                <i class="fa-solid fa-[icon]"></i> [Link 4 Title]
                            </span>
                            <i class="fa-solid fa-arrow-right"></i>
                        </a>
                    </div>
                </div>

            </div>
        </div>
    </section>

</div>
{% endblock %}
```

---

## 🎯 **HERO SECTION SPECIFICATIONS**

**Complete hero section designs for all 7 modules**: See [HERO_SECTION_SPECIFICATIONS.md](HERO_SECTION_SPECIFICATIONS.md)

Each module has a custom-designed hero section with:
- Module-specific gradient colors
- Contextual badge (mission statement)
- Value proposition headline and description
- 3 inline stats in glassmorphism cards
- 4-6 primary action buttons

**Quick Reference**:
- **Main Dashboard**: Blue-Indigo-Purple gradient, "COMMAND CENTER"
- **Communities**: Blue-Cyan-Teal gradient, "COMMUNITY DATA HUB"
- **MANA**: Emerald-Teal-Cyan gradient, "ASSESSMENT OPERATIONS CENTER"
- **Coordination**: Orange-Amber-Yellow gradient, "PARTNERSHIP COORDINATION HUB"
- **Recommendations**: Purple-Violet-Indigo gradient, "POLICY DEVELOPMENT CENTER"
- **M&E**: Rose-Pink-Fuchsia gradient, "MONITORING & EVALUATION CENTER"
- **OOBC Mgt**: Sky-Blue-Indigo gradient, "OFFICE OPERATIONS HUB"

---

## 📋 **MODULE-SPECIFIC IMPLEMENTATION SPECS**

### **1. Main Dashboard** (`common/dashboard.html`)

**Current State**: ✅ Has stat cards, ⚠️ Missing activities/events sections

**Specifications**:

#### **Stat Cards** (✅ Exists - Keep)
```python
# context data needed
stats = {
    'communities': {
        'barangay_total': 1234,
        'municipal_total': 156
    },
    'mana': {
        'total_assessments': 45
    },
    'coordination': {
        'active_partnerships': 78,
        'bmoas': 12,
        'ngas': 25,
        'lgus': 41
    },
    'staff': {
        'total': 34,
        'active': 28
    }
}
```

#### **Recent Activities** (❌ Add)
```python
# Pull from multiple sources
recent_activities = [
    # From communities
    {
        'type': 'community_added',
        'title': 'New Barangay OBC: Brgy. Poblacion, Cotabato City',
        'description': 'Added by Juan Dela Cruz',
        'icon': 'fa-mosque',
        'color': 'blue',
        'created_at': datetime.now(),
        'url': '/communities/1234/'
    },
    # From MANA
    {
        'type': 'assessment_completed',
        'title': 'MANA Assessment Completed: Maguindanao del Norte',
        'description': 'Education sector assessment finalized',
        'icon': 'fa-check-circle',
        'color': 'green',
        'created_at': datetime.now(),
        'url': '/mana/manage-assessments/uuid/'
    },
    # From Coordination
    {
        'type': 'partnership_signed',
        'title': 'MOA Signed: DepEd Partnership',
        'description': 'Education partnership agreement formalized',
        'icon': 'fa-handshake',
        'color': 'purple',
        'created_at': datetime.now(),
        'url': '/coordination/partnerships/uuid/'
    },
    # From Tasks
    {
        'type': 'task_completed',
        'title': 'Task Completed: Budget Report Q4',
        'description': 'Completed by Maria Santos',
        'icon': 'fa-check-square',
        'color': 'emerald',
        'created_at': datetime.now(),
        'url': '/oobc-management/staff/tasks/123/'
    }
]
# Show last 10, ordered by created_at desc
```

#### **Upcoming Events** (❌ Add)
```python
# Pull from coordination and calendar
upcoming_events = Event.objects.filter(
    start_date__gte=timezone.now()
).order_by('start_date')[:7]

# Include:
# - Coordination events
# - MANA fieldwork activities
# - Calendar events
```

#### **Quick Actions** (❌ Add)
```html
<!-- Feature Cards Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

    <!-- Add Barangay OBC -->
    <a href="{% url 'common:communities_add' %}" class="feature-card">
        <i class="fas fa-mosque"></i>
        <h3>Add Barangay OBC</h3>
        <p>Register new Bangsamoro community profile</p>
    </a>

    <!-- New MANA Assessment -->
    <a href="{% url 'common:mana_new_assessment' %}" class="feature-card">
        <i class="fas fa-map-marked-alt"></i>
        <h3>New Assessment</h3>
        <p>Launch mapping and needs assessment project</p>
    </a>

    <!-- Schedule Event -->
    <a href="{% url 'common:coordination_event_add' %}" class="feature-card">
        <i class="fas fa-calendar-plus"></i>
        <h3>Schedule Event</h3>
        <p>Add coordination meeting or activity</p>
    </a>

    <!-- View Calendar -->
    <a href="{% url 'common:oobc_calendar' %}" class="feature-card">
        <i class="fas fa-calendar-week"></i>
        <h3>View Calendar</h3>
        <p>Organization-wide schedule and events</p>
    </a>

    <!-- Task Board -->
    <a href="{% url 'common:staff_task_board' %}" class="feature-card">
        <i class="fas fa-tasks"></i>
        <h3>Task Board</h3>
        <p>Manage team assignments and workflows</p>
    </a>

    <!-- MOA PPAs -->
    <a href="{% url 'monitoring:moa_ppas' %}" class="feature-card">
        <i class="fas fa-project-diagram"></i>
        <h3>MOA PPAs</h3>
        <p>Monitor ministry programs and initiatives</p>
    </a>

    <!-- Planning & Budgeting -->
    <a href="{% url 'common:planning_budgeting' %}" class="feature-card">
        <i class="fas fa-calculator"></i>
        <h3>Planning & Budgeting</h3>
        <p>Budget planning and strategic tools</p>
    </a>

    <!-- Reports -->
    <a href="{% url 'project_central:report_list' %}" class="feature-card">
        <i class="fas fa-file-chart-line"></i>
        <h3>Reports</h3>
        <p>Generate analytics and compliance reports</p>
    </a>
</div>
```

#### **Related Modules** (❌ Add)
```html
<!-- No specific integration CTA needed for main dashboard -->
<!-- Main dashboard is the hub, not a spoke -->
```

---

### **2. Communities Home** (`communities/communities_home.html`)

**Current State**: ✅ Exists, ⚠️ Needs enrichment

**Specifications**:

#### **Stat Cards** (✅ Exists - Keep & Enhance)
```python
stats = {
    'barangay_total': 1234,
    'municipal_total': 156,
    'provincial_total': 15,
    'total_population': 456789,
    'region_ix_count': 678,
    'region_xii_count': 556
}
```

#### **Recent Activities** (❌ Add)
```python
recent_activities = [
    # Recent OBC additions
    {
        'type': 'community_added',
        'title': f'New Barangay OBC: {community.barangay_name}, {community.municipality}',
        'description': f'Added by {community.created_by.get_full_name()}',
        'icon': 'fa-mosque',
        'color': 'blue',
        'created_at': community.created_at,
        'url': f'/communities/{community.id}/'
    },
    # Recent updates
    {
        'type': 'community_updated',
        'title': f'Updated: {community.barangay_name}',
        'description': 'Population data revised',
        'icon': 'fa-edit',
        'color': 'emerald',
        'created_at': community.updated_at,
        'url': f'/communities/{community.id}/'
    }
]
```

#### **Upcoming Events** (❌ Add)
```python
# Events related to communities
upcoming_events = Event.objects.filter(
    start_date__gte=timezone.now(),
    # Filter community-related events
    Q(tags__contains='community') |
    Q(tags__contains='field_visit') |
    Q(tags__contains='consultation')
).order_by('start_date')[:7]
```

#### **Quick Actions** (❌ Add)
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

    <a href="{% url 'common:communities_add' %}">
        <i class="fas fa-mosque"></i>
        <h3>Add Barangay OBC</h3>
        <p>Register new community profile</p>
    </a>

    <a href="{% url 'common:communities_add_municipality' %}">
        <i class="fas fa-city"></i>
        <h3>Add Municipal Coverage</h3>
        <p>Create municipal-level snapshot</p>
    </a>

    <a href="{% url 'common:communities_add_province' %}">
        <i class="fas fa-flag"></i>
        <h3>Add Provincial Coverage</h3>
        <p>Register provincial OBC data</p>
    </a>

    <a href="{% url 'common:mana_geographic_data' %}">
        <i class="fas fa-map"></i>
        <h3>Geographic Data</h3>
        <p>Manage spatial layers and GIS</p>
    </a>

    <a href="{% url 'common:communities_manage' %}">
        <i class="fas fa-list"></i>
        <h3>View All Barangays</h3>
        <p>Browse and manage profiles</p>
    </a>

    <a href="{% url 'common:communities_manage_municipal' %}">
        <i class="fas fa-building"></i>
        <h3>Municipal Dashboard</h3>
        <p>View coverage by municipality</p>
    </a>

    <a href="{% url 'common:communities_manage_provincial' %}">
        <i class="fas fa-chart-bar"></i>
        <h3>Provincial Overview</h3>
        <p>Regional coverage statistics</p>
    </a>

    <a href="#">
        <i class="fas fa-file-export"></i>
        <h3>Export Data</h3>
        <p>Download OBC database (CSV/Excel)</p>
    </a>
</div>
```

#### **Related Modules** (❌ Add)
```html
<!-- Integration with MANA -->
<section class="bg-gradient-to-r from-emerald-600 via-teal-500 to-sky-500">
    <h2>View OBCs on MANA Map</h2>
    <p>Visualize community distribution and density with interactive geospatial mapping</p>

    <div class="quick-links">
        <a href="{% url 'common:mana_regional_overview' %}">Regional Map View</a>
        <a href="{% url 'common:mana_provincial_overview' %}">Provincial Dashboard</a>
        <a href="{% url 'common:mana_new_assessment' %}">Launch Assessment</a>
        <a href="{% url 'common:mana_geographic_data' %}">Geographic Data</a>
    </div>
</section>
```

---

### **3. MANA Home** (`mana/mana_home.html`)

**Current State**: ✅ Has stat cards & assessment areas, ⚠️ Needs activities/events

**Specifications**:

#### **Stat Cards** (✅ Exists - Keep)
```python
stats = {
    'mana': {
        'total_assessments': 45,
        'completed': 12,
        'in_progress': 18,
        'planned': 15,
        'by_area': {
            'education': 12,
            'economic': 10,
            'social': 8,
            'cultural': 7,
            'infrastructure': 8
        }
    }
}
```

#### **Recent Activities** (❌ Add)
```python
recent_activities = [
    {
        'type': 'assessment_started',
        'title': f'Assessment Started: {assessment.title}',
        'description': f'Facilitator: {assessment.facilitator.get_full_name()}',
        'icon': 'fa-play-circle',
        'color': 'blue',
        'created_at': assessment.created_at,
        'url': f'/mana/manage-assessments/{assessment.id}/'
    },
    {
        'type': 'fieldwork_completed',
        'title': f'Fieldwork Done: {activity.title}',
        'description': f'{activity.municipality}, {activity.province}',
        'icon': 'fa-check-circle',
        'color': 'green',
        'created_at': activity.completed_at,
        'url': f'/mana/activity-log/?id={activity.id}'
    },
    {
        'type': 'desk_review_submitted',
        'title': 'Desk Review: Education Sector',
        'description': '45 documents analyzed',
        'icon': 'fa-book-open',
        'color': 'purple',
        'created_at': review.submitted_at,
        'url': '/mana/desk-review/'
    }
]
```

#### **Upcoming Events** (❌ Add)
```python
# MANA-specific events (fieldwork, workshops, consultations)
upcoming_events = Event.objects.filter(
    start_date__gte=timezone.now(),
    Q(tags__contains='mana') |
    Q(tags__contains='assessment') |
    Q(tags__contains='fieldwork')
).order_by('start_date')[:7]

# Or from MANA Activity Planner
upcoming_activities = MANAActivity.objects.filter(
    scheduled_date__gte=timezone.now(),
    status='planned'
).order_by('scheduled_date')[:7]
```

#### **Quick Actions** (⚠️ Enhance - Move assessment areas here as cards)
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

    <!-- Methodology Cards (currently in assessment areas) -->
    <a href="{% url 'common:mana_desk_review' %}">
        <i class="fas fa-book-open"></i>
        <h3>Desk Review</h3>
        <p>Document analysis and literature review</p>
    </a>

    <a href="{% url 'common:mana_survey_module' %}">
        <i class="fas fa-clipboard-list"></i>
        <h3>Survey Module</h3>
        <p>Structured field data collection</p>
    </a>

    <a href="{% url 'common:mana_kii' %}">
        <i class="fas fa-comments"></i>
        <h3>Key Informant Interviews</h3>
        <p>Qualitative interview transcripts</p>
    </a>

    <a href="{% url 'common:mana_activity_planner' %}">
        <i class="fas fa-calendar-day"></i>
        <h3>Activity Planner</h3>
        <p>Schedule fieldwork and activities</p>
    </a>

    <a href="{% url 'common:mana_playbook' %}">
        <i class="fas fa-book"></i>
        <h3>MANA Playbook</h3>
        <p>Assessment methodology guide</p>
    </a>

    <a href="{% url 'common:mana_regional_overview' %}">
        <i class="fas fa-map"></i>
        <h3>Regional Map</h3>
        <p>Interactive geospatial view</p>
    </a>

    <a href="{% url 'common:mana_provincial_overview' %}">
        <i class="fas fa-chart-bar"></i>
        <h3>Provincial Dashboard</h3>
        <p>Province-level summaries</p>
    </a>

    <a href="{% url 'common:mana_new_assessment' %}">
        <i class="fas fa-plus-circle"></i>
        <h3>New Assessment</h3>
        <p>Launch new assessment project</p>
    </a>
</div>
```

#### **Related Modules** (❌ Add)
```html
<!-- Integration with Task Management -->
<section class="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-500">
    <h2>Assessment Tasks & Workflows</h2>
    <p>Track assessment activities, assign tasks, and monitor progress across your MANA projects</p>

    <div class="quick-links">
        <a href="{% url 'common:enhanced_task_dashboard' %}?domain=mana">View MANA Tasks</a>
        <a href="{% url 'common:staff_task_create' %}?domain=mana">Create Task</a>
        <a href="{% url 'common:task_analytics' %}?domain=mana">Task Analytics</a>
        <a href="{% url 'common:mana_activity_log' %}">Activity Log</a>
    </div>
</section>
```

---

### **4. Coordination Home** (`coordination/coordination_home.html`)

**Current State**: ✅ Has stat cards, ⚠️ Needs activities/events enhancement

**Specifications**:

#### **Stat Cards** (✅ Exists - Keep)
```python
stats = {
    'mapped_partners': {
        'total': 78,
        'bmoa': 12,
        'nga': 25,
        'lgu': 41
    },
    'active_partnerships': {
        'total': 45,
        'bmoa': 8,
        'nga': 15,
        'lgu': 22
    },
    'coordination_activities_done': {
        'total': 156,
        'bmoa': 45,
        'nga': 56,
        'lgu': 55
    },
    'planned_coordination_activities': {
        'total': 23,
        'bmoa': 5,
        'nga': 8,
        'lgu': 10
    }
}
```

#### **Recent Activities** (❌ Add)
```python
recent_activities = [
    {
        'type': 'partnership_created',
        'title': f'New Partnership: {partnership.partnership_name}',
        'description': f'{partnership.organization.name} • {partnership.partnership_type}',
        'icon': 'fa-handshake',
        'color': 'green',
        'created_at': partnership.created_at,
        'url': f'/coordination/partnerships/{partnership.id}/'
    },
    {
        'type': 'event_completed',
        'title': f'Event Completed: {event.title}',
        'description': f'{event.attendees_count} participants',
        'icon': 'fa-check-circle',
        'color': 'blue',
        'created_at': event.end_date,
        'url': f'/coordination/events/{event.id}/'
    },
    {
        'type': 'organization_added',
        'title': f'New Partner: {org.name}',
        'description': f'{org.organization_type} • {org.location}',
        'icon': 'fa-building',
        'color': 'purple',
        'created_at': org.created_at,
        'url': f'/coordination/organizations/{org.id}/'
    }
]
```

#### **Upcoming Events** (✅ Already exists conceptually - Formalize)
```python
# Already pulls coordination events
upcoming_events = Event.objects.filter(
    start_date__gte=timezone.now(),
    event_type__in=['coordination', 'meeting', 'workshop']
).order_by('start_date')[:7]
```

#### **Quick Actions** (❌ Add)
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

    <a href="{% url 'common:coordination_organization_add' %}">
        <i class="fas fa-building"></i>
        <h3>Add Partner Organization</h3>
        <p>Register new partner in directory</p>
    </a>

    <a href="{% url 'common:coordination_partnership_add' %}">
        <i class="fas fa-file-contract"></i>
        <h3>New Partnership</h3>
        <p>Create MOA/MOU agreement</p>
    </a>

    <a href="{% url 'common:coordination_event_add' %}">
        <i class="fas fa-calendar-plus"></i>
        <h3>Schedule Event</h3>
        <p>Plan coordination meeting or activity</p>
    </a>

    <a href="{% url 'common:coordination_calendar' %}">
        <i class="fas fa-calendar-alt"></i>
        <h3>Event Calendar</h3>
        <p>View all coordination activities</p>
    </a>

    <a href="{% url 'common:coordination_resource_booking_form' %}">
        <i class="fas fa-door-open"></i>
        <h3>Book Resource</h3>
        <p>Reserve conference room or equipment</p>
    </a>

    <a href="{% url 'common:coordination_organizations' %}">
        <i class="fas fa-users"></i>
        <h3>Partner Directory</h3>
        <p>Browse mapped organizations</p>
    </a>

    <a href="{% url 'common:coordination_partnerships' %}">
        <i class="fas fa-handshake"></i>
        <h3>View Partnerships</h3>
        <p>Active MOAs and agreements</p>
    </a>

    <a href="{% url 'common:coordination_view_all' %}">
        <i class="fas fa-list"></i>
        <h3>All Activities</h3>
        <p>Complete coordination log</p>
    </a>
</div>
```

#### **Related Modules** (❌ Add)
```html
<!-- Integration with Task Management -->
<section class="bg-gradient-to-r from-purple-600 via-pink-500 to-rose-500">
    <h2>Event Tasks & QR Check-in</h2>
    <p>Manage event logistics, track attendance with QR codes, and coordinate follow-up tasks</p>

    <div class="quick-links">
        <a href="{% url 'common:enhanced_task_dashboard' %}?domain=coordination">View Event Tasks</a>
        <a href="{% url 'common:event_check_in' event_id='latest' %}">QR Check-in</a>
        <a href="{% url 'common:event_attendance_report' event_id='latest' %}">Attendance Reports</a>
        <a href="{% url 'common:oobc_calendar' %}?filter=coordination">Calendar Integration</a>
    </div>
</section>
```

---

### **5. Recommendations Home** (`recommendations/recommendations_home.html`)

**Current State**: ⚠️ Underdeveloped, only policies functional

**Specifications**:

#### **Stat Cards** (❌ Add - Currently Missing)
```python
stats = {
    'total_recommendations': 34,
    'proposed': 12,
    'under_review': 8,
    'approved': 10,
    'implemented': 4,
    'by_area': {
        'education': 8,
        'economic': 7,
        'social': 6,
        'governance': 5,
        'infrastructure': 4,
        'cultural': 4
    }
}
```

#### **Recent Activities** (❌ Add)
```python
recent_activities = [
    {
        'type': 'recommendation_submitted',
        'title': f'New Recommendation: {rec.title}',
        'description': f'{rec.area} • Priority: {rec.priority}',
        'icon': 'fa-lightbulb',
        'color': 'yellow',
        'created_at': rec.created_at,
        'url': f'/recommendations/{rec.id}/'
    },
    {
        'type': 'recommendation_approved',
        'title': f'Approved: {rec.title}',
        'description': f'Approved by {rec.approved_by.get_full_name()}',
        'icon': 'fa-check-circle',
        'color': 'green',
        'created_at': rec.approved_at,
        'url': f'/recommendations/{rec.id}/'
    }
]
```

#### **Upcoming Events** (❌ Add)
```python
# Policy-related events (hearings, consultations, reviews)
upcoming_events = Event.objects.filter(
    start_date__gte=timezone.now(),
    Q(tags__contains='policy') |
    Q(tags__contains='recommendation') |
    Q(tags__contains='consultation')
).order_by('start_date')[:7]
```

#### **Quick Actions** (❌ Add)
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

    <a href="{% url 'common:recommendations_new' %}">
        <i class="fas fa-lightbulb"></i>
        <h3>Submit Recommendation</h3>
        <p>Propose new policy or program</p>
    </a>

    <a href="{% url 'common:recommendations_manage' %}">
        <i class="fas fa-balance-scale"></i>
        <h3>View All Policies</h3>
        <p>Browse policy recommendations</p>
    </a>

    <a href="{% url 'common:recommendations_by_area' area='education' %}">
        <i class="fas fa-graduation-cap"></i>
        <h3>Education Policies</h3>
        <p>Education sector recommendations</p>
    </a>

    <a href="{% url 'common:recommendations_by_area' area='economic' %}">
        <i class="fas fa-chart-line"></i>
        <h3>Economic Development</h3>
        <p>Economic policy initiatives</p>
    </a>

    <a href="{% url 'common:recommendations_by_area' area='social' %}">
        <i class="fas fa-heart"></i>
        <h3>Social Services</h3>
        <p>Social development policies</p>
    </a>

    <a href="{% url 'common:recommendations_by_area' area='governance' %}">
        <i class="fas fa-landmark"></i>
        <h3>Governance</h3>
        <p>Administrative and governance reforms</p>
    </a>

    <a href="{% url 'common:recommendations_by_area' area='cultural' %}">
        <i class="fas fa-mosque"></i>
        <h3>Cultural Preservation</h3>
        <p>Cultural development initiatives</p>
    </a>

    <a href="#">
        <i class="fas fa-file-export"></i>
        <h3>Export Report</h3>
        <p>Download recommendations database</p>
    </a>
</div>
```

#### **Related Modules** (❌ Add)
```html
<!-- Integration with Budget & Task Management -->
<section class="bg-gradient-to-r from-amber-600 via-orange-500 to-red-500">
    <h2>Policy-Budget Linkage</h2>
    <p>Connect policy recommendations to budget allocations and track implementation tasks</p>

    <div class="quick-links">
        <a href="{% url 'common:policy_budget_matrix' %}">Policy-Budget Matrix</a>
        <a href="{% url 'project_central:policy_analytics' policy_id='all' %}">Policy Analytics</a>
        <a href="{% url 'common:enhanced_task_dashboard' %}?domain=policy">Policy Tasks</a>
        <a href="{% url 'common:planning_budgeting' %}#policies">Budget Planning</a>
    </div>
</section>
```

---

### **6. M&E Dashboard** (`monitoring/monitoring_dashboard.html`)

**Current State**: ❌ **Needs Creation** - No unified M&E home exists

**Specifications**:

#### **Stat Cards** (❌ Create)
```python
stats = {
    'moa_ppas': {
        'total': 234,
        'ongoing': 156,
        'completed': 67,
        'planning': 11
    },
    'oobc_initiatives': {
        'total': 56,
        'active': 34,
        'completed': 22
    },
    'obc_requests': {
        'total': 89,
        'approved': 45,
        'pending': 32,
        'completed': 12
    },
    'total_budget': 456000000,  # Total across all sources
    'budget_utilized': 234567890
}
```

#### **Recent Activities** (❌ Create)
```python
recent_activities = [
    {
        'type': 'moa_ppa_added',
        'title': f'New MOA PPA: {entry.title}',
        'description': f'{entry.implementing_moa.name} • ₱{entry.budget_allocation:,.0f}',
        'icon': 'fa-file-contract',
        'color': 'blue',
        'created_at': entry.created_at,
        'url': f'/monitoring/entry/{entry.id}/'
    },
    {
        'type': 'initiative_completed',
        'title': f'Completed: {entry.title}',
        'description': f'{entry.beneficiaries_count} beneficiaries',
        'icon': 'fa-check-circle',
        'color': 'green',
        'created_at': entry.completed_date,
        'url': f'/monitoring/entry/{entry.id}/'
    }
]
```

#### **Upcoming Events** (❌ Create)
```python
# M&E related events (reviews, evaluations, reporting)
upcoming_events = Event.objects.filter(
    start_date__gte=timezone.now(),
    Q(tags__contains='monitoring') |
    Q(tags__contains='evaluation') |
    Q(tags__contains='review')
).order_by('start_date')[:7]
```

#### **Quick Actions** (❌ Create)
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

    <a href="{% url 'monitoring:create_moa' %}">
        <i class="fas fa-file-alt"></i>
        <h3>Add MOA PPA</h3>
        <p>Register ministry/agency program</p>
    </a>

    <a href="{% url 'monitoring:create_oobc' %}">
        <i class="fas fa-hand-holding-heart"></i>
        <h3>Add OOBC Initiative</h3>
        <p>Create office-led program</p>
    </a>

    <a href="{% url 'monitoring:create_request' %}">
        <i class="fas fa-file-signature"></i>
        <h3>Add OBC Request</h3>
        <p>Log community assistance request</p>
    </a>

    <a href="{% url 'project_central:me_analytics_dashboard' %}">
        <i class="fas fa-chart-bar"></i>
        <h3>M&E Analytics</h3>
        <p>Performance metrics and analysis</p>
    </a>

    <a href="{% url 'monitoring:prioritization_matrix' %}">
        <i class="fas fa-sort-amount-down"></i>
        <h3>Prioritization Tool</h3>
        <p>Rank and prioritize initiatives</p>
    </a>

    <a href="{% url 'monitoring:scenario_rebalance' %}">
        <i class="fas fa-balance-scale"></i>
        <h3>Budget Scenarios</h3>
        <p>What-if budget planning</p>
    </a>

    <a href="{% url 'project_central:report_list' %}">
        <i class="fas fa-file-chart-line"></i>
        <h3>Generate Reports</h3>
        <p>Compliance and performance reports</p>
    </a>

    <a href="{% url 'monitoring:export_aip_summary' %}">
        <i class="fas fa-file-excel"></i>
        <h3>Export Data</h3>
        <p>Download M&E database</p>
    </a>
</div>
```

#### **Related Modules** (❌ Create)
```html
<!-- Integration with Project Management Portal (Already done via MOA PPAs page ✅) -->
<!-- But add unified M&E dashboard integration -->
<section class="bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-500">
    <h2>Integrated Project Management</h2>
    <p>Advanced budget approvals, alerts, and portfolio-wide analytics for all M&E initiatives</p>

    <div class="quick-links">
        <a href="{% url 'project_central:portfolio_dashboard' %}">Portfolio Dashboard</a>
        <a href="{% url 'project_central:budget_approval_dashboard' %}">Budget Approvals</a>
        <a href="{% url 'project_central:alert_list' %}">System Alerts</a>
        <a href="{% url 'project_central:report_list' %}">Reports Library</a>
    </div>
</section>
```

---

### **7. OOBC Management Home** (`common/oobc_management_home.html`)

**Current State**: ✅ Has stat cards & Planning CTA, ⚠️ Needs activities/events

**Specifications**:

#### **Stat Cards** (✅ Exists - Keep)
```python
metrics = {
    'staff_total': 34,
    'active_staff': 28,
    'pending_approvals': 12,
    'pending_staff': 3
}
```

#### **Recent Activities** (❌ Add)
```python
recent_activities = [
    {
        'type': 'task_completed',
        'title': f'Task Completed: {task.title}',
        'description': f'By {task.assignee.get_full_name()} • {task.domain}',
        'icon': 'fa-check-square',
        'color': 'green',
        'created_at': task.completed_at,
        'url': f'/oobc-management/staff/tasks/{task.id}/'
    },
    {
        'type': 'staff_joined',
        'title': f'New Staff: {user.get_full_name()}',
        'description': f'{user.position} • {user.department}',
        'icon': 'fa-user-plus',
        'color': 'blue',
        'created_at': user.date_joined,
        'url': f'/oobc-management/staff/profiles/{user.id}/'
    },
    {
        'type': 'leave_approved',
        'title': f'Leave Approved: {leave.staff.get_full_name()}',
        'description': f'{leave.leave_type} • {leave.duration} days',
        'icon': 'fa-calendar-check',
        'color': 'emerald',
        'created_at': leave.approved_at,
        'url': f'/oobc-management/staff/leave/{leave.id}/'
    }
]
```

#### **Upcoming Events** (❌ Add)
```python
# Office-wide events from calendar
upcoming_events = Event.objects.filter(
    start_date__gte=timezone.now(),
    is_organization_wide=True
).order_by('start_date')[:7]

# Also include staff leave/absences as "events"
upcoming_absences = StaffLeave.objects.filter(
    start_date__gte=timezone.now(),
    status='approved'
).order_by('start_date')[:5]
```

#### **Quick Actions** (❌ Add - Beyond Planning CTA)
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

    <a href="{% url 'common:staff_task_board' %}">
        <i class="fas fa-tasks"></i>
        <h3>Task Board</h3>
        <p>View and manage team tasks</p>
    </a>

    <a href="{% url 'common:staff_task_create' %}">
        <i class="fas fa-plus-square"></i>
        <h3>Create Task</h3>
        <p>Assign new task to team member</p>
    </a>

    <a href="{% url 'common:oobc_calendar' %}">
        <i class="fas fa-calendar-alt"></i>
        <h3>Calendar</h3>
        <p>Organization-wide schedule</p>
    </a>

    <a href="{% url 'common:staff_leave_request' %}">
        <i class="fas fa-umbrella-beach"></i>
        <h3>Request Leave</h3>
        <p>Submit leave application</p>
    </a>

    <a href="{% url 'common:staff_profiles_list' %}">
        <i class="fas fa-users-cog"></i>
        <h3>Staff Directory</h3>
        <p>Team profiles and contacts</p>
    </a>

    <a href="{% url 'common:staff_performance_dashboard' %}">
        <i class="fas fa-chart-line"></i>
        <h3>Performance</h3>
        <p>Team KPIs and analytics</p>
    </a>

    <a href="{% url 'common:gap_analysis_dashboard' %}">
        <i class="fas fa-chart-area"></i>
        <h3>Gap Analysis</h3>
        <p>Budget vs needs comparison</p>
    </a>

    <a href="{% url 'common:strategic_goals_dashboard' %}">
        <i class="fas fa-bullseye"></i>
        <h3>Strategic Goals</h3>
        <p>Track organizational objectives</p>
    </a>
</div>
```

#### **Related Modules** (✅ Planning CTA Exists - Add Another)
```html
<!-- Current: Planning & Budgeting CTA ✅ (Keep) -->

<!-- Add: Cross-Module Task Integration -->
<section class="bg-gradient-to-r from-rose-600 via-pink-500 to-purple-500">
    <h2>Cross-Module Task Management</h2>
    <p>Track tasks across all modules with domain-specific views and advanced analytics</p>

    <div class="quick-links">
        <a href="{% url 'common:tasks_by_domain' domain='mana' %}">MANA Tasks</a>
        <a href="{% url 'common:tasks_by_domain' domain='coordination' %}">Coordination Tasks</a>
        <a href="{% url 'common:tasks_by_domain' domain='monitoring' %}">M&E Tasks</a>
        <a href="{% url 'common:task_analytics' %}">Task Analytics</a>
    </div>
</section>
```

---

## 📊 **IMPLEMENTATION PRIORITY MATRIX**

| Dashboard | Priority | Complexity | Impact | Status |
|-----------|----------|------------|--------|--------|
| **Main Dashboard** | 🔴 Critical | Medium | 🔥🔥🔥 | ⚠️ Partial |
| **Communities Home** | 🔴 High | Low | 🔥🔥 | ⚠️ Needs CTAs |
| **MANA Home** | 🔴 High | Medium | 🔥🔥 | ⚠️ Needs activities |
| **Coordination Home** | 🟡 Medium | Low | 🔥🔥 | ✅ Mostly done |
| **OOBC Mgt Home** | 🟡 Medium | Low | 🔥🔥 | ⚠️ Needs activities |
| **M&E Dashboard** | 🔴 High | High | 🔥🔥🔥 | ❌ **Create from scratch** |
| **Recommendations Home** | 🟢 Low | Medium | 🔥 | ⚠️ Underdeveloped |

---

## 🚀 **PHASED ROLLOUT PLAN**

### **Phase 1: Hero Sections** | **PRIORITY: CRITICAL** ⭐

**Goal**: Add hero sections to all module dashboards for visual impact and primary action surfacing

**Tasks**:
1. ❌ Main Dashboard - Add "COMMAND CENTER" hero with blue-indigo-purple gradient
2. ❌ Communities Home - Add "COMMUNITY DATA HUB" hero with blue-cyan-teal gradient
3. ❌ MANA Home - Add "ASSESSMENT OPERATIONS" hero with emerald-teal-cyan gradient
4. ❌ Coordination Home - Add "PARTNERSHIP HUB" hero with orange-amber-yellow gradient
5. ❌ OOBC Mgt Home - Add "OFFICE OPERATIONS" hero with sky-blue-indigo gradient
6. ❌ M&E Dashboard - Add "MONITORING CENTER" hero with rose-pink-fuchsia gradient (if dashboard exists)
7. ❌ Recommendations Home - Add "POLICY DEVELOPMENT" hero with purple-violet-indigo gradient

**Complexity**: Moderate (copy-paste pattern, customize content)
**Dependencies**: None (independent implementation)
**Impact**: 🔥🔥🔥 **VERY HIGH** (immediate visual transformation, primary actions surfaced)
**Files to Modify**: 7 templates

**Reference**: See [HERO_SECTION_SPECIFICATIONS.md](HERO_SECTION_SPECIFICATIONS.md) for complete code

---

### **Phase 2: Recent Activities & Events** | **PRIORITY: HIGH**

**Goal**: Add temporal awareness to existing dashboards

**Tasks**:
1. ❌ Main Dashboard - Add activities/events sections
2. ❌ Coordination Home - Formalize activities/events
3. ❌ OOBC Management - Add activities/events
4. ❌ MANA Home - Add activities/events
5. ❌ Communities Home - Add activities/events

**Complexity**: Simple (template-only changes)
**Dependencies**: Backend views must provide `recent_activities` and `upcoming_events` context
**Prerequisites**: Activity aggregation logic in views
**Impact**: High (engagement and context)
**Files to Modify**: 5 templates

---

### **Phase 3: Quick Actions Enhancement** | **PRIORITY: HIGH**

**Goal**: Add consistent Quick Actions sections

**Tasks**:
1. ✅ Main Dashboard - Add 8 feature cards
2. ✅ Communities Home - Add 8 feature cards
3. ✅ MANA Home - Move assessment areas to Quick Actions
4. ✅ Coordination Home - Add 8 feature cards
5. ✅ OOBC Mgt Home - Add 8 feature cards (beyond Planning CTA)

**Complexity**: Simple (template-only changes)
**Dependencies**: None (independent implementation)
**Impact**: High (discoverability)
**Files to Modify**: 5 templates

---

### **Phase 4: Cross-Module Integration** | **PRIORITY: HIGH**

**Goal**: Add Related Modules Integration CTAs

**Tasks**:
1. ✅ Communities Home → MANA Map integration
2. ✅ MANA Home → Task Management integration
3. ✅ Coordination Home → Task & QR integration
4. ✅ Recommendations Home → Budget integration
5. ✅ OOBC Mgt Home → Cross-module task integration

**Complexity**: Moderate (requires understanding of module relationships)
**Dependencies**: Related module URLs must exist and be accessible
**Prerequisites**: All target modules have functional dashboards
**Impact**: Very High (workflow efficiency)
**Files to Modify**: 5 templates

---

### **Phase 5: New M&E Dashboard** | **PRIORITY: HIGH**

**Goal**: Create unified M&E Dashboard from scratch

**Tasks**:
1. ❌ Create `monitoring_dashboard.html` template
2. ❌ Create `monitoring_dashboard()` view
3. ❌ Aggregate stats from MOA PPAs, OOBC Initiatives, OBC Requests
4. ❌ Add to URL routing
5. ❌ Update navbar to link to unified dashboard

**Complexity**: Complex (new view + template + data aggregation)
**Dependencies**: MOA PPAs, OOBC Initiatives, OBC Requests models must exist
**Prerequisites**: Monitoring app fully functional
**Impact**: Very High (consistency)
**Files to Create**: 1 template, 1 view
**Files to Modify**: 2 (urls.py, navbar.html)

---

### **Phase 6: Recommendations Enhancement** | **PRIORITY: MEDIUM**

**Goal**: Fully develop Recommendations Home dashboard

**Tasks**:
1. ❌ Add stat cards
2. ❌ Add activities/events
3. ❌ Add Quick Actions
4. ❌ Add Budget integration CTA

**Complexity**: Moderate (view + template modifications)
**Dependencies**: Recommendations models must have sufficient data
**Prerequisites**: Policy-Budget Matrix functionality exists
**Impact**: Medium (low usage currently)
**Files to Modify**: 1 template, 1 view

---

## ✅ **SUCCESS METRICS**

### **Quantitative**

- **Navigation Efficiency**: 50% reduction in clicks to common actions
- **Feature Discovery**: 80% of users discover Quick Actions within first visit
- **User Retention**: 30% increase in return visits to module dashboards
- **Task Completion**: 40% faster workflow completion (measured via task timestamps)

### **Qualitative**

- **Consistency**: 100% of dashboards follow same 6-section structure
- **Predictability**: Users know where to find activities, events, and actions
- **Integration**: Related modules surfaced contextually in every dashboard
- **Actionability**: Primary actions always ≤2 clicks away

---

## 📝 **IMPLEMENTATION CHECKLIST**

### **Template Standards**

- [ ] All 7 dashboards have Header with breadcrumb and page title
- [ ] All 7 dashboards have 4 Stat Cards in responsive grid
- [ ] All 7 dashboards have Hero Section with gradient, badge, headline, 3 inline stats, 4-6 actions
- [ ] All 7 dashboards have Recent Activities panel (last 10 items)
- [ ] All 7 dashboards have Upcoming Events panel (next 7 days)
- [ ] All 7 dashboards have Quick Actions section (4-8 feature cards)
- [ ] All 7 dashboards have Related Modules Integration CTA

### **Backend Requirements**

- [ ] Views provide `stats` context variable (for stat cards)
- [ ] Views provide `hero_stats` context variable (for hero section inline stats)
- [ ] Views provide `recent_activities` context variable (list of dicts)
- [ ] Views provide `upcoming_events` context variable (queryset)
- [ ] Views provide module-specific data for Quick Actions
- [ ] All activities have: type, title, description, icon, color, created_at, url
- [ ] Hero stats are calculated efficiently (avoid N+1 queries)

### **Documentation**

- [ ] Component library updated with dashboard patterns
- [ ] Developer guide for adding new dashboards
- [ ] User guide for navigating dashboards
- [ ] Accessibility compliance verified (WCAG 2.1 AA)

---

## 🎓 **DESIGN PATTERNS REFERENCE**

### **Stat Card Pattern**

```html
<div class="relative overflow-hidden bg-gradient-to-br from-{color}-500 via-{color}-600 to-{color}-700 rounded-xl shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300">
    <div class="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent"></div>
    <div class="relative p-6 text-white">
        <!-- Main metric -->
        <div class="flex items-center justify-between mb-4">
            <div>
                <p class="text-{color}-100 text-sm font-medium">{label}</p>
                <p class="text-3xl font-bold">{value}</p>
            </div>
            <div class="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <i class="fas fa-{icon} text-2xl"></i>
            </div>
        </div>
        <!-- Optional: Sub-metrics -->
        <div class="grid grid-cols-3 gap-2 pt-3 border-t border-{color}-400/30">
            <div class="text-center">
                <p class="text-xl font-bold">{sub_value}</p>
                <p class="text-xs text-{color}-100">{sub_label}</p>
            </div>
        </div>
    </div>
</div>
```

### **Recent Activities Pattern**

```html
<div class="bg-white rounded-xl shadow-lg border border-gray-200">
    <div class="px-6 py-4 border-b bg-gray-50">
        <h2 class="text-lg font-semibold text-gray-800 flex items-center">
            <i class="fas fa-clock-rotate-left text-blue-500 mr-2"></i>
            Recent Activities
        </h2>
    </div>
    <div class="p-6 space-y-4">
        {% for activity in recent_activities|slice:":10" %}
        <div class="flex items-start gap-4 pb-4 border-b last:border-0">
            <div class="w-10 h-10 rounded-full bg-{color}-100 flex items-center justify-center">
                <i class="fas fa-{icon} text-{color}-600"></i>
            </div>
            <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ activity.title }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ activity.description|truncatewords:15 }}</p>
                <p class="text-xs text-gray-400 mt-1">
                    <i class="far fa-clock mr-1"></i>{{ activity.created_at|timesince }} ago
                </p>
            </div>
        </div>
        {% endfor %}
        <div class="text-center">
            <a href="{url}" class="text-sm text-blue-600 font-medium">View All →</a>
        </div>
    </div>
</div>
```

### **Feature Card Pattern**

```html
<a href="{url}" class="group block bg-white rounded-xl border-2 border-gray-200 hover:border-blue-400 shadow-sm hover:shadow-lg transition-all">
    <div class="p-6">
        <div class="flex items-center justify-between mb-4">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-{color}-400 to-{color}-600 flex items-center justify-center text-white shadow-lg">
                <i class="fas fa-{icon} text-2xl"></i>
            </div>
            <i class="fas fa-arrow-right text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <p class="text-sm text-gray-600 mb-4">{description}</p>
        <div class="flex items-center text-sm text-blue-600 font-medium">
            <span>Launch Tool</span>
            <i class="fas fa-chevron-right ml-1 text-xs"></i>
        </div>
    </div>
</a>
```

### **Integration CTA Pattern** (MOA PPAs ✅ Gold Standard)

```html
<section class="relative overflow-hidden rounded-3xl border border-{color}-200/60 bg-gradient-to-r from-{color1}-600 via-{color2}-500 to-{color3}-500 text-white shadow-xl">
    <div class="absolute inset-0 bg-white/10 opacity-20 mix-blend-overlay"></div>
    <div class="relative px-6 sm:px-10 py-8 sm:py-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
        <div class="space-y-4 max-w-2xl">
            <div class="inline-flex items-center rounded-full bg-white/15 px-3 py-1 text-sm font-semibold backdrop-blur">
                <i class="fa-solid fa-{icon} mr-2"></i>{category}
            </div>
            <h2 class="text-3xl sm:text-4xl font-semibold">{headline}</h2>
            <p class="text-white/80 text-lg">{description}</p>
        </div>
        <div class="w-full max-w-sm">
            <div class="rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20 p-6 shadow-lg space-y-3">
                <h3 class="text-sm font-semibold uppercase">Quick Access</h3>
                <!-- 4 quick link buttons -->
            </div>
        </div>
    </div>
</section>
```

---

**End of Implementation Plan**

**Next Steps**:
1. Review specifications with team
2. Prioritize Phase 1 (Quick Wins)
3. Begin template modifications
4. Iterate with user feedback

**Prepared By**: Claude Code AI Agent
**Date**: October 2, 2025
**Version**: 1.0
