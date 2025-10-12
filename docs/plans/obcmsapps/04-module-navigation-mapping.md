# OBCMS Module Navigation Mapping - Quick Reference

**Document:** 04-module-navigation-mapping.md
**Last Updated:** 2025-10-12
**Purpose:** Quick reference for mapping navigation menu items to Django apps and code locations

---

## How to Use This Document

This is a **quick reference** for:
- **Users:** Finding where features are located
- **Developers:** Locating code for specific features
- **Support:** Troubleshooting user questions about navigation

**Format:** Navigation Label → Django App → Views → URLs → Models

---

## Navigation to Code Mapping

### 1. OBC Data Module

| Navigation Item | Django App | View Location | URL Pattern | Key Models |
|----------------|------------|---------------|-------------|------------|
| **Barangay OBCs** | `communities` | `communities/views.py` | `/communities/` | `OBCCommunity`, `CommunityLivelihood`, `Stakeholder` |
| **Municipal OBCs** | `communities` | `communities/views.py` | `/communities/municipal/` | `MunicipalityCoverage` |
| **Provincial OBCs** | `communities` | `communities/views.py` | `/communities/provincial/` | `ProvinceCoverage` |
| **Geographic Data** 🔒 | `communities` | `communities/views.py` | `/communities/geographic-data/` | `GeographicDataLayer`, `MapVisualization`, `SpatialDataPoint` |

**Code Locations:**
```python
# Models
src/communities/models.py
  - OBCCommunity (extends CommunityProfileBase)
  - MunicipalityCoverage
  - ProvinceCoverage
  - GeographicDataLayer

# Views
src/communities/views.py
  - obc_list, obc_detail, obc_edit
  - municipal_coverage_list
  - provincial_coverage_list
  - geographic_layers

# Templates
src/templates/communities/
  - barangay_manage.html
  - municipal_manage.html
  - provincial_manage.html
  - geographic_data.html
```

---

### 2. MANA Module

| Navigation Item | Django App | View Location | URL Pattern | Key Models |
|----------------|------------|---------------|-------------|------------|
| **Regional MANA** 🔒 | `mana` | `mana/views.py` | `/mana/regional/` | `Assessment`, `AssessmentFinding` |
| **Provincial MANA** 🔒 | `mana` | `mana/views.py` | `/mana/provincial/` | `Assessment`, `AssessmentParticipant` |
| **Desk Review** 🔒 | `mana` | `mana/views.py` | `/mana/desk-review/` | `Assessment` |
| **Survey** 🔒 | `mana` | `mana/views.py` | `/mana/survey/` | `Assessment` |
| **Key Informant Interview** 🔒 | `mana` | `mana/views.py` | `/mana/kii/` | `Assessment` |

**Participant Workshops (Separate System):**
- **URL:** `/mana/workshops/assessments/{id}/participant/`
- **Middleware:** `ManaParticipantAccessMiddleware`
- **Access:** Gated sequential progression (Workshop 1 → 2 → 3 → 4 → 5)

**Code Locations:**
```python
# Models
src/mana/models.py
  - Assessment
  - AssessmentParticipant
  - AssessmentFinding
  - AssessmentRecommendation

# Views (Staff)
src/mana/views.py
  - regional_overview
  - provincial_overview
  - desk_review
  - survey_module
  - kii_module

# Views (Participants)
src/mana/views_participant.py
  - participant_workshop (sequential progression)

# Templates
src/templates/mana/
  - regional_overview.html
  - provincial_overview.html
  - workshops/participant/ (5 workshop templates)
```

**🔒 Visibility:** Staff/Superuser only (`can_access_mana_filter`)

---

### 3. Coordination Module

| Navigation Item | Django App | View Location | URL Pattern | Key Models |
|----------------|------------|---------------|-------------|------------|
| **Mapped Partners** | `coordination` | `coordination/views.py` | `/coordination/organizations/` | `Organization`, `OrganizationContact`, `MAOFocalPerson` |
| **Partnership Agreements** | `coordination` | `coordination/views.py` | `/coordination/partnerships/` | `Partnership`, `PartnershipMilestone`, `PartnershipDocument` |
| **Coordination Activities** | `coordination` | `coordination/views.py` | `/coordination/events/` | `StakeholderEngagement`, `EngagementFacilitator`, `ConsultationFeedback` |

**Additional Features:**
- **Communication Tracking:** `/coordination/communications/` → `Communication`, `CommunicationTemplate`
- **Coordination Notes:** `/coordination/notes/` → `CoordinationNote`

**Code Locations:**
```python
# Models
src/coordination/models.py
  - Organization (13 types)
  - Partnership (9 types, 12 status states)
  - StakeholderEngagement (10 engagement types)
  - Communication (15 types)

# Views
src/coordination/views.py
  - organization_list, organization_detail
  - partnership_list, partnership_detail
  - engagement_list, engagement_detail
  - communication_list

# Templates
src/templates/coordination/
  - organizations/
  - partnerships/
  - engagements/
```

**Dynamic Navigation:**
- **OOBC Staff:** "Coordination" → Organization list
- **MOA Users:** "MOA Profile" → Own organization detail

---

### 4. Recommendations Module

| Navigation Item | Django App | View Location | URL Pattern | Key Models |
|----------------|------------|---------------|-------------|------------|
| **Policies** | `recommendations.policies` | `policies/views.py` | `/policies/` | (Policy models - inferred) |
| **Systematic Programs** | `recommendations.policies` | `policies/views.py` | `/policies/programs/` | (Program models - inferred) |
| **Services** | `recommendations.policies` | `policies/views.py` | `/policies/services/` | (Service models - inferred) |

**Document Management:**
- **URL:** `/documents/`
- **App:** `recommendations.documents`
- **Models:** (Document repository models)

**Code Locations:**
```python
# Models
src/recommendations/policies/models.py
  - (Policy recommendation models)
  - (Program tracking models)

src/recommendations/documents/models.py
  - (Document management models)

# Views
src/recommendations/policies/views.py
  - policy_list, policy_detail
  - programs_list
  - services_list

# Templates
src/templates/recommendations/
  - policies/
  - programs/
  - services/
```

**🔒 Visibility:** Staff/Superuser/MOA Staff (`can_access_policies`)

---

### 5. M&E Module (Monitoring & Evaluation)

| Navigation Item | Django App | View Location | URL Pattern | Key Models |
|----------------|------------|---------------|-------------|------------|
| **MOA PPAs** | `monitoring` | `monitoring/views.py` | `/monitoring/moa-ppas/` | (PPA, MOA models - inferred) |
| **OOBC Initiatives** 🔒 | `monitoring` | `monitoring/views.py` | `/monitoring/oobc-initiatives/` | (OOBC initiative models) |
| **OBC Requests** | `monitoring` | `monitoring/views.py` | `/monitoring/obc-requests/` | (Request models) |
| **M&E Analytics** 🔒 | `project_central` | `project_central/views.py` | `/project-management/analytics/` | (Analytics models) |

**Code Locations:**
```python
# Models
src/monitoring/models.py
  - (MOA, PPA, Initiative models)

# Views
src/monitoring/views.py
  - me_home
  - moa_ppa_list
  - oobc_initiatives
  - obc_requests

src/project_central/views.py
  - me_analytics_dashboard

# Templates
src/templates/monitoring/
  - home.html
  - moa_ppas/
  - oobc_initiatives/
```

**🔒 Visibility:**
- **OOBC Initiatives:** Staff/Superuser only
- **M&E Analytics:** Staff/Superuser only

---

### 6. OOBC Management Module

| Navigation Item | Django App | View Location | URL Pattern | Key Models |
|----------------|------------|---------------|-------------|------------|
| **Staff Management** | `common` | `common/views.py` | `/staff/` | `User`, `StaffProfile`, `StaffTeam`, `StaffTeamMembership` |
| **Work Items** | `common` | `common/views.py` | `/work-items/` | `WorkItem` (unified model) |
| **Planning & Budgeting** | `common` | `common/views.py` | `/oobc-management/planning/` | (Planning models - inferred) |
| **Calendar Management** | `common` | `common/views.py` | `/calendar/` | `WorkItem`, `RecurringEventPattern`, `CalendarResource`, `CalendarResourceBooking` |
| **Project Management Portal** | `project_central` | `project_central/views.py` | `/project-management/` | `WorkItem` (work_type='project') |
| **User Approvals** 🔒 | `common` | `common/views.py` | `/approvals/` | `User` (approval_tier, is_approved) |

**Code Locations:**
```python
# Models
src/common/models.py
  - User (custom user model)
  - StaffProfile
  - StaffTeam, StaffTeamMembership
  - WorkItem (MPTT hierarchical)
  - RecurringEventPattern (RFC 5545)
  - CalendarResource, CalendarResourceBooking
  - TrainingProgram, TrainingEnrollment
  - PerformanceTarget

# Views
src/common/views.py
  - staff_list, staff_detail
  - work_item_list, work_item_detail
  - calendar_view
  - resource_list
  - user_approvals

# Templates
src/templates/common/
  - staff/
  - work_items/
  - calendar/
```

**🔒 Visibility:** Staff/Superuser only (`can_access_oobc_management`)

**Legacy URLs (Redirected):**
- `/project-central/*` → `/project-management/*` (permanent redirect)

---

## Geographic Hierarchy (Shared Across Modules)

| Model | Django App | Used By | Purpose |
|-------|------------|---------|---------|
| **Region** | `common` | communities, mana, coordination | Top-level geographic unit (IX, X, XI, XII) |
| **Province** | `common` | communities, mana, coordination | Province within region |
| **Municipality** | `common` | communities, mana, coordination | Municipality/city within province |
| **Barangay** | `common` | communities, mana, coordination | Barangay within municipality |

**Code Location:**
```python
src/common/models.py
  - Region (with boundary_geojson, center_coordinates)
  - Province
  - Municipality
  - Barangay

# All include JSONField for GeoJSON boundaries (NO PostGIS)
```

**API Endpoints:**
```python
/api/v1/regions/
/api/v1/provinces/
/api/v1/municipalities/
/api/v1/barangays/
/api/v1/communities/geojson/  # GeoJSON for Leaflet.js
```

---

## User Menu Items

| Menu Item | URL Pattern | View/Redirect | Purpose |
|-----------|-------------|---------------|---------|
| **Profile** | `/profile/` | `common/views.py:user_profile` | Edit personal info, change password |
| **Admin Panel** 🔒 | `/admin/` | Django admin | Full system administration |
| **Logout** | `/logout/` | `common/views.py:logout_view` | Clear session, redirect to login |

**Code Location:**
```python
src/common/views.py
  - user_profile
  - logout_view

src/templates/common/
  - profile.html
```

**🔒 Admin Panel Visibility:** Only if `user.is_staff = True`

---

## API Endpoints (Quick Reference)

### Current Stable API (v1)

| Endpoint | Django App | Purpose | Authentication |
|----------|------------|---------|----------------|
| `/api/v1/communities/` | `communities` | OBC community data | JWT required |
| `/api/v1/communities/geojson/` | `communities` | GeoJSON for maps | JWT required |
| `/api/v1/coordination/organizations/` | `coordination` | Partner directory | JWT required |
| `/api/v1/coordination/partnerships/` | `coordination` | Partnership agreements | JWT required |
| `/api/v1/mana/assessments/` | `mana` | Assessment data | JWT required |

**Code Location:**
```python
src/api/v1/urls.py
  - includes from api.v1.communities_urls
  - includes from api.v1.coordination_urls
  - includes from api.v1.mana_urls
```

### Legacy API (Being Migrated)

| Endpoint | Django App | Status |
|----------|------------|--------|
| `/api/administrative/` | `common` | ⚠️ Migrating to v1 |
| `/api/communities/` | `communities` | ⚠️ Migrating to v1 |
| `/api/mana/` | `mana` | ⚠️ Migrating to v1 |
| `/api/coordination/` | `coordination` | ⚠️ Migrating to v1 |

---

## Permission Filters (Role-Based Access)

**Location:** `src/common/templatetags/moa_rbac.py`

| Filter | Purpose | Returns True If |
|--------|---------|-----------------|
| `is_moa_focal_user_filter` | MOA user check | is_moa_staff + is_approved + has moa_organization |
| `can_access_mana_filter` | MANA module access | is_superuser OR is_oobc_staff |
| `can_access_geographic_data` | Geographic data | is_superuser OR is_oobc_staff |
| `can_access_policies` | Policy module | is_superuser OR is_oobc_staff OR is_moa_staff |
| `can_access_oobc_initiatives` | OOBC initiatives | is_superuser OR is_oobc_staff |
| `can_access_me_analytics` | M&E analytics | is_superuser OR is_oobc_staff |
| `can_access_oobc_management` | OOBC Mgt module | is_superuser OR is_oobc_staff |

**Usage in Templates:**
```django
{% load moa_rbac %}

{% if user|can_access_mana_filter %}
  <!-- MANA navigation item visible -->
{% endif %}
```

---

## Common Troubleshooting

### User Can't See Navigation Item

**Check:**
1. User role (`user.user_type`)
2. Approval status (`user.is_approved`, `user.approval_tier`)
3. Permission filter in `moa_rbac.py`
4. Organization linkage (`user.moa_organization` for MOA users)

**Code Location:**
```python
src/templates/common/navbar.html
  - Check {% if user|can_access_* %} conditions

src/common/templatetags/moa_rbac.py
  - Check filter logic
```

---

### Feature Not Working After Clicking Nav Item

**Check:**
1. URL pattern in `urls.py`
2. View exists in `views.py`
3. Template exists in `templates/`
4. Permissions in view decorator (`@login_required`, `@permission_required`)

**Example:**
```python
# src/communities/urls.py
path('communities/', views.obc_list, name='communities_manage'),

# src/communities/views.py
@login_required
def obc_list(request):
    # View logic
```

---

### Finding Code for Specific Feature

**Steps:**
1. **Find URL:** Check navbar.html for `{% url 'namespace:name' %}`
2. **Find URL Pattern:** Search `urls.py` for `name='...'`
3. **Find View:** Look at view function/class in URL pattern
4. **Find Models:** Import statements in view file
5. **Find Template:** Return statement in view (e.g., `return render(request, 'template.html')`)

**Example:**
```
Navigation: "Barangay OBCs"
↓
URL: {% url 'common:communities_manage' %}
↓
URL Pattern: path('communities/', views.obc_list, name='communities_manage')
↓
View: src/communities/views.py:obc_list
↓
Models: from .models import OBCCommunity
↓
Template: src/templates/communities/barangay_manage.html
```

---

## Quick Reference: Module to App Mapping

| User-Facing Module | Primary Django App | Supporting Apps |
|--------------------|-------------------|-----------------|
| **OBC Data** | `communities` | `common` (Region, Province, Municipality, Barangay) |
| **MANA** | `mana` | `common` (WorkItem), `communities` (OBCCommunity) |
| **Coordination** | `coordination` | `common` (User, WorkItem) |
| **Recommendations** | `recommendations.policies` | `recommendations.documents` |
| **M&E** | `monitoring` | `project_central` (analytics) |
| **OOBC Management** | `common` | `project_central` (project portal) |

---

## Related Documentation

- [User-Facing Organization](01-user-facing-organization.md) - Full navigation guide
- [Technical Organization](02-technical-organization.md) - Django app structure
- [Domain Architecture](03-domain-architecture.md) - Module relationships
- [Main README](README.md) - Documentation index

---

**Last Updated:** 2025-10-12
**Purpose:** Quick reference for developers and support staff
**Tip:** Use Ctrl+F / Cmd+F to search for specific navigation items or URLs
