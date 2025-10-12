# OBCMS Navbar RBAC Analysis

**Status:** Analysis Complete
**Date:** 2025-10-13
**Purpose:** Comprehensive analysis of navbar menu structure and required RBAC controls for BMMS implementation

---

## Executive Summary

This document provides a complete inventory of all navbar menu items, their URLs, associated views, current permission checks, and module affiliations. This analysis will inform the Role-Based Access Control (RBAC) design for the BMMS multi-tenant system.

---

## Current User Model Structure

### User Types (from `common.models.User`)

```python
USER_TYPES = (
    ("admin", "Administrator"),
    ("oobc_executive", "OOBC Executive"),
    ("oobc_staff", "OOBC Staff"),
    ("cm_office", "Chief Minister Office"),
    ("bmoa", "BARMM Ministry/Agency/Office"),
    ("lgu", "Local Government Unit"),
    ("nga", "National Government Agency"),
    ("community_leader", "Community Leader"),
    ("researcher", "Assessment Coordinator/Researcher"),
)
```

### Key User Properties

- `is_oobc_staff` - Returns True for `oobc_staff` and `oobc_executive`
- `is_oobc_executive` - Returns True for `oobc_executive` only
- `is_moa_staff` - Returns True for `bmoa`, `lgu`, `nga`
- `is_community_leader` - Returns True for `community_leader`
- `moa_organization` - ForeignKey to `coordination.Organization` (for MOA staff only)
- `is_approved` - Boolean for account approval status

---

## Navbar Menu Structure Analysis

### 1. **Dashboard (Logo/Home)**

**Location:** Line 10
**URL:** `{% url 'common:dashboard' %}`
**Icon:** `fa-mosque`
**Label:** "OBC Management System"

**Current Permission Check:**
- Requires authentication (`{% if user.is_authenticated %}`)

**Module:** Core/Common
**View Type:** Dashboard aggregation

---

### 2. **Restricted Menu (MANA Participants/Facilitators)**

**Location:** Lines 21-40
**Visibility Condition:** `not user.is_staff and not user.is_superuser and perms.mana.can_access_regional_mana`

#### 2.1 Provincial OBC
- **URL:** `{% url 'communities:communities_manage_provincial' %}`
- **Icon:** `fa-flag`
- **Label:** "Provincial OBC"
- **Module:** Communities
- **Permission:** `perms.mana.can_access_regional_mana`

#### 2.2 Regional MANA
- **URL:** `{% url 'mana:mana_regional_overview' %}`
- **Icon:** `fa-map-marked-alt`
- **Label:** "Regional MANA"
- **Module:** MANA
- **Permission:** `perms.mana.can_access_regional_mana`

#### 2.3 Facilitator Dashboard
- **URL:** `{% url 'mana:mana_manage_assessments' %}`
- **Icon:** `fa-chalkboard-teacher`
- **Label:** "Facilitator Dashboard"
- **Module:** MANA
- **Permission:** `perms.mana.can_facilitate_workshop`

---

### 3. **Main Navigation (Standard Users)**

**Location:** Lines 42-315
**Visibility Condition:** `else` (not restricted MANA users)

#### 3.1 MOA Profile (MOA Focal Users Only)

**Location:** Lines 44-50
**Visibility Condition:** `{% if user|is_moa_focal_user_filter %}`

- **URL:** `{% get_coordination_url user %}` → `/coordination/organizations/{moa_id}/`
- **Icon:** `fa-building`
- **Label:** `{{ user|get_coordination_label }}` → "MOA Profile"
- **Module:** Coordination
- **Permission Check:** Custom filter `is_moa_focal_user_filter`
  - Checks: `is_moa_staff` AND `is_approved` AND `moa_organization` exists

---

#### 3.2 OBC Data (Dropdown)

**Location:** Lines 52-90
**Visibility:** All authenticated users

**Main Link:**
- **URL:** `{% url 'communities:communities_home' %}`
- **Icon:** `fa-users`
- **Label:** "OBC Data"

**Submenu Items:**

##### 3.2.1 Barangay OBCs
- **URL:** `{% url 'communities:communities_manage' %}`
- **Icon:** `fa-map-marker-alt` (blue-500)
- **Description:** "Manage barangay-level profiles and data"
- **Module:** Communities
- **View:** Barangay management

##### 3.2.2 Municipal OBCs
- **URL:** `{% url 'communities:communities_manage_municipal' %}`
- **Icon:** `fa-city` (indigo-500)
- **Description:** "View municipal coverage snapshots and trends"
- **Module:** Communities
- **View:** Municipal overview

##### 3.2.3 Provincial OBCs
- **URL:** `{% url 'communities:communities_manage_provincial' %}`
- **Icon:** `fa-flag` (emerald-500)
- **Description:** "View provincial coverage and OBC statistics"
- **Module:** Communities
- **View:** Provincial overview

##### 3.2.4 Geographic Data (Conditional)
- **URL:** `{% url 'mana:mana_geographic_data' %}`
- **Icon:** `fa-map` (purple-500)
- **Description:** "Manage geographic layers and spatial datasets"
- **Module:** MANA
- **Permission:** `{% if user|can_access_geographic_data %}`
- **Permission Logic:** Requires `is_oobc_staff` OR `is_superuser`

---

#### 3.3 MANA (Dropdown)

**Location:** Lines 92-137
**Visibility:** `{% if user|can_access_mana_filter %}`
**Permission Logic:** Requires `is_oobc_staff` OR `is_superuser`

**Main Link:**
- **URL:** `{% url 'mana:mana_home' %}`
- **Icon:** `fa-map-marked-alt`
- **Label:** "MANA"

**Submenu Items:**

##### 3.3.1 Regional MANA
- **URL:** `{% url 'mana:mana_regional_overview' %}`
- **Icon:** `fa-globe-asia` (sky-500)
- **Description:** "Access regional mapping layers and insights"

##### 3.3.2 Provincial MANA
- **URL:** `{% url 'mana:mana_provincial_overview' %}`
- **Icon:** `fa-map` (amber-500)
- **Description:** "Review provincial dashboards and summaries"

##### 3.3.3 Desk Review
- **URL:** `{% url 'mana:mana_desk_review' %}`
- **Icon:** `fa-book-open` (purple-500)
- **Description:** "Launch document-based assessments"

##### 3.3.4 Survey
- **URL:** `{% url 'mana:mana_survey_module' %}`
- **Icon:** `fa-clipboard-list` (green-500)
- **Description:** "Capture structured field survey data"

##### 3.3.5 Key Informant Interview
- **URL:** `{% url 'mana:mana_kii' %}`
- **Icon:** `fa-comments` (rose-500)
- **Description:** "Document KII findings and transcripts"

---

#### 3.4 Coordination (Conditional Dropdown)

**Location:** Lines 139-182
**Visibility:** `{% if not user|is_moa_focal_user_filter %}`
**Logic:** Only shown to OOBC staff (MOA focal users see direct link instead)

**Main Link:**
- **URL:** `{% url 'coordination:home' %}`
- **Icon:** `fa-handshake`
- **Label:** "Coordination"

**Submenu Items:**

##### 3.4.1 Mapped Partners
- **URL:** `{% url 'coordination:organizations' %}`
- **Icon:** `fa-users-cog` (cyan-500)
- **Description:** "Directory of partner organizations and contacts"

##### 3.4.2 Partnership Agreements
- **URL:** `{% url 'coordination:partnerships' %}`
- **Icon:** `fa-file-contract` (amber-500)
- **Description:** "Track MOAs, MOUs, and collaboration terms"

##### 3.4.3 Coordination Activities
- **URL:** `{% url 'coordination:events' %}`
- **Icon:** `fa-calendar-check` (lime-500)
- **Description:** "Manage meetings, events, and follow-ups"

---

#### 3.5 Recommendations (Dropdown)

**Location:** Lines 184-215
**Visibility:** `{% if user|can_access_policies %}`
**Permission Logic:** `is_oobc_staff` OR `is_superuser` OR `is_moa_staff`

**Main Link:**
- **URL:** `{% url 'policies:home' %}`
- **Icon:** `fa-gavel`
- **Label:** "Recommendations"

**Submenu Items:**

##### 3.5.1 Policies
- **URL:** `{% url 'policies:manage' %}`
- **Icon:** `fa-balance-scale` (orange-500)
- **Description:** "Monitor policy recommendations and status"

##### 3.5.2 Systematic Programs
- **URL:** `{% url 'policies:programs' %}`
- **Icon:** `fa-project-diagram` (indigo-500)
- **Description:** "Review programmatic interventions and pipelines"

##### 3.5.3 Services
- **URL:** `{% url 'policies:services' %}`
- **Icon:** `fa-concierge-bell` (teal-500)
- **Description:** "Track service delivery priorities and progress"

---

#### 3.6 M&E (Monitoring & Evaluation) (Dropdown)

**Location:** Lines 217-257
**Visibility:** Always visible (no conditional)

**Main Link:**
- **URL:** `{% url 'monitoring:home' %}`
- **Icon:** `fa-chart-pie`
- **Label:** "M&E"

**Submenu Items:**

##### 3.6.1 MOA PPAs
- **URL:** `{% url 'monitoring:moa_ppas' %}`
- **Icon:** `fa-file-contract` (blue-500)
- **Description:** "Monitor Ministries, Offices, and Agencies programs"

##### 3.6.2 OOBC Initiatives (Conditional)
- **URL:** `{% url 'monitoring:oobc_initiatives' %}`
- **Icon:** `fa-hand-holding-heart` (emerald-500)
- **Description:** "Office-led programs supporting OBC communities"
- **Permission:** `{% if user|can_access_oobc_initiatives %}`
- **Permission Logic:** `is_oobc_staff` OR `is_superuser`

##### 3.6.3 OBC Requests
- **URL:** `{% url 'monitoring:obc_requests' %}`
- **Icon:** `fa-file-signature` (indigo-500)
- **Description:** "Community proposals and assistance requests"

##### 3.6.4 M&E Analytics (Conditional)
- **URL:** `{% url 'project_central:me_analytics_dashboard' %}`
- **Icon:** `fa-chart-bar` (emerald-500)
- **Description:** "Performance metrics and impact analysis"
- **Permission:** `{% if user|can_access_me_analytics %}`
- **Permission Logic:** `is_oobc_staff` OR `is_superuser`

---

#### 3.7 OOBC Management (Dropdown)

**Location:** Lines 259-313
**Visibility:** `{% if user|can_access_oobc_management %}`
**Permission Logic:** `is_oobc_staff` OR `is_superuser`

**Main Link:**
- **URL:** `{% url 'common:oobc_management_home' %}`
- **Icon:** `fa-toolbox`
- **Label:** "OOBC Mgt"

**Submenu Items:**

##### 3.7.1 Staff Management
- **URL:** `{% url 'common:staff_management' %}`
- **Icon:** `fa-user-cog` (green-500)
- **Description:** "Coordinate workloads, tasks, and staffing needs"

##### 3.7.2 Work Items
- **URL:** `{% url 'common:work_item_list' %}`
- **Icon:** `fa-tasks` (emerald-500)
- **Description:** "Unified task, activity, and project management system"

##### 3.7.3 Planning & Budgeting
- **URL:** `{% url 'common:planning_budgeting' %}`
- **Icon:** `fa-file-signature` (blue-500)
- **Description:** "Manage OOBC Office PPAs and OBC MOA PPAs"

##### 3.7.4 Calendar Management
- **URL:** `{% url 'common:oobc_calendar' %}`
- **Icon:** `fa-calendar-week` (blue-500)
- **Description:** "Organization-wide schedule for coordination, MANA, and staff actions"

##### 3.7.5 Project Management Portal
- **URL:** `{% url 'project_central:portfolio_dashboard' %}`
- **Icon:** `fa-project-diagram` (purple-500)
- **Description:** "Project-activity-task integration dashboard and workflow management"

##### 3.7.6 User Approvals (Highly Restricted)
- **URL:** `{% url 'common:user_approvals' %}`
- **Icon:** `fa-user-check` (amber-500)
- **Description:** "Review and approve pending user account registrations"
- **Permission:** Complex inline check (Line 302):
  ```django
  {% if user.is_superuser or
        user.user_type == 'admin' or
        user.user_type == 'oobc_staff' and user.position in [
          'Executive Director',
          'Deputy Executive Director',
          'DMO IV',
          'DMO III',
          'Information System Analyst',
          'Information System Analyst II',
          'Planning Officer I',
          'Planning Officer II',
          'Community Development Officer I'
        ] %}
  ```

---

### 4. **User Menu (Profile & Logout)**

**Location:** Lines 318-355
**Visibility:** All authenticated users

#### 4.1 Profile Link
- **URL:** `{% url 'common:profile' %}`
- **Icon:** `fa-user-circle`
- **Label:** "Profile"

#### 4.2 Admin Panel (Staff Only)
- **URL:** `/admin/`
- **Icon:** `fa-tools`
- **Label:** "Admin Panel"
- **Permission:** `{% if user.is_staff %}`

#### 4.3 Logout
- **URL:** `{% url 'common:logout' %}`
- **Icon:** `fa-sign-out-alt`
- **Label:** "Logout"

---

## Custom Permission Filters Analysis

### Template Tags Location
**File:** `/src/common/templatetags/moa_rbac.py`

### 1. User Type Checks

#### `is_moa_focal_user_filter(user)`
**Returns:** Boolean
**Logic:**
```python
return (
    user.is_moa_staff and
    user.is_approved and
    user.moa_organization is not None
)
```

#### `can_access_mana_filter(user)`
**Returns:** Boolean
**Logic:**
```python
return user.is_superuser or user.is_oobc_staff
```

#### `can_access_geographic_data(user)`
**Returns:** Boolean
**Logic:**
```python
return user.is_superuser or user.is_oobc_staff
```

### 2. Module Access Checks

#### `can_access_oobc_initiatives(user)`
**Returns:** Boolean
**Logic:**
```python
return user.is_superuser or user.is_oobc_staff
```

#### `can_access_me_analytics(user)`
**Returns:** Boolean
**Logic:**
```python
return user.is_superuser or user.is_oobc_staff
```

#### `can_access_oobc_management(user)`
**Returns:** Boolean
**Logic:**
```python
return user.is_superuser or user.is_oobc_staff
```

#### `can_access_policies(user)`
**Returns:** Boolean
**Logic:**
```python
return (
    user.is_superuser or
    user.is_oobc_staff or
    user.is_moa_staff
)
```

### 3. Dynamic URL/Label Generation

#### `get_coordination_label(user)`
**Returns:** String
**Logic:**
```python
if user.is_moa_staff and user.moa_organization:
    return "MOA Profile"
return "Coordination"
```

#### `get_coordination_url(user)`
**Returns:** String
**Logic:**
```python
if user.is_moa_staff and user.moa_organization:
    return f"/coordination/organizations/{user.moa_organization.id}/"
return "/coordination/organizations/"
```

---

## Django Model Permissions

### MANA Module Permissions
**Location:** `/src/mana/models.py` - WorkshopParticipantAccount model

```python
permissions = [
    ("can_access_regional_mana", "Can access regional MANA workshops"),
    ("can_view_provincial_obc", "Can view provincial OBC data"),
    ("can_facilitate_workshop", "Can facilitate and manage MANA workshops"),
]
```

**Usage in navbar:**
- `perms.mana.can_access_regional_mana` - Line 21 (restricted menu visibility)
- `perms.mana.can_facilitate_workshop` - Line 32 (facilitator dashboard)

---

## RBAC Requirements for BMMS

### 1. Organization-Level Data Isolation

**Current State:**
- MOA users linked to single organization via `moa_organization` FK
- Basic filtering in template tags and view methods

**BMMS Requirement:**
- Comprehensive row-level security
- Query filtering at ORM level
- Multi-tenant data isolation
- OCM read-only aggregated access

### 2. Module-Level Access Control

**Current Modules with Restrictions:**

| Module | Current Access Rules |
|--------|---------------------|
| MANA | OOBC Staff + Superuser + Workshop Participants (via perms) |
| Geographic Data | OOBC Staff + Superuser |
| OOBC Initiatives | OOBC Staff + Superuser |
| M&E Analytics | OOBC Staff + Superuser |
| OOBC Management | OOBC Staff + Superuser |
| Policies/Recommendations | OOBC Staff + Superuser + MOA Staff |
| Coordination (Full) | OOBC Staff + Superuser |
| Coordination (Profile View) | MOA Focal Users (approved only) |

**BMMS Enhancement Needed:**
- Granular module permissions per organization
- Feature-level toggles (enable/disable modules per MOA)
- Role-based module access within organizations

### 3. Feature-Level Permissions

**Current Feature Restrictions:**

| Feature | Current Logic | Location |
|---------|---------------|----------|
| User Approvals | Complex inline position check | Line 302 (navbar) |
| PPA Creation | `can_create_ppa_filter` | Template tag |
| PPA Editing | `user.can_edit_ppa(ppa)` | User model method |
| PPA Viewing | `user.can_view_ppa(ppa)` | User model method |
| Work Item Editing | `user.can_edit_work_item(item)` | User model method |
| MOA Management | `can_manage_moa(user, org)` | Template tag |

**BMMS Enhancement Needed:**
- Role-based permissions (Admin, Manager, Staff, Viewer)
- Action-based permissions (Create, Read, Update, Delete)
- Resource-specific permissions

### 4. Position-Based Access (Legacy Pattern)

**Current Usage:**
- User Approvals menu item (Line 302)
- Hardcoded position names
- Brittle string comparison

**BMMS Recommendation:**
- Replace with role-based permissions
- Use Django groups/permissions
- Avoid hardcoded position checks

---

## Permission Architecture Summary

### Current Permission Layers

1. **Authentication Layer** - `user.is_authenticated`
2. **User Type Layer** - `is_oobc_staff`, `is_moa_staff`, etc.
3. **Approval Layer** - `is_approved` (for MOA users)
4. **Django Permissions Layer** - `perms.mana.*`
5. **Custom Filter Layer** - Template tag filters
6. **Model Method Layer** - `user.can_edit_ppa()`, etc.
7. **Position Layer** - Hardcoded position checks (legacy)

### Recommended BMMS Permission Layers

1. **Authentication** - Login required
2. **Organization** - Multi-tenant isolation
3. **Role** - Django groups (Admin, Manager, Staff, Viewer)
4. **Module** - Feature toggles per organization
5. **Action** - CRUD permissions (Django permissions)
6. **Data** - Row-level security (ORM filters)

---

## Menu Items Requiring RBAC Updates

### Critical (Security-Sensitive)

1. **User Approvals** - Replace position check with role-based permission
2. **OOBC Management** - Add organization-scoped admin role
3. **Planning & Budgeting** - Add budget permission checks
4. **M&E Analytics** - Add analytics viewer role

### Medium (Data Isolation)

5. **MOA PPAs** - Enforce organization filtering
6. **OOBC Initiatives** - Add initiative management permission
7. **Work Items** - Organization-scoped task management
8. **Coordination** - Organization-based partnership access

### Low (Module Access)

9. **MANA** - Already has Django permissions (enhance for BMMS)
10. **Communities** - Public data (read-only for most)
11. **Policies** - Already accessible to MOA staff

---

## Next Steps for RBAC Implementation

### Phase 1: Foundation (CRITICAL)
1. Create Django permission groups:
   - `OOBC_Admin`
   - `OOBC_Manager`
   - `OOBC_Staff`
   - `OOBC_Viewer`
   - `MOA_Admin`
   - `MOA_Manager`
   - `MOA_Staff`
   - `MOA_Viewer`
   - `OCM_Viewer` (read-only aggregated)

2. Migrate position-based checks to role-based permissions
3. Add organization context to all permission checks

### Phase 2: Data Isolation (HIGH)
1. Implement organization-scoped querysets
2. Add manager methods to all models
3. Create middleware for automatic organization filtering

### Phase 3: Module Toggles (MEDIUM)
1. Create `OrganizationModuleConfig` model
2. Add module enable/disable flags
3. Update navbar to respect module toggles

### Phase 4: UI Enhancement (LOW)
1. Hide/show menu items based on permissions
2. Add loading states for permission checks
3. Implement graceful degradation for insufficient permissions

---

## Files Requiring Updates

### Models
- `/src/common/models.py` - User model enhancements
- `/src/coordination/models.py` - Organization module config
- All app models - Add organization-scoped managers

### Template Tags
- `/src/common/templatetags/moa_rbac.py` - Update permission logic
- Create new `/src/common/templatetags/bmms_rbac.py`

### Templates
- `/src/templates/common/navbar.html` - Update permission checks
- All module templates - Add permission guards

### Views
- All view files - Add permission decorators/mixins
- Add organization context to all queries

### Middleware
- Create `/src/common/middleware/organization_middleware.py`

---

## Conclusion

The current OBCMS navbar has a **hybrid permission system** combining:
- User type checks (7 types)
- Django permissions (3 custom MANA permissions)
- Custom template filters (11 filters)
- Model methods (5 permission methods)
- Hardcoded position checks (legacy pattern)

**For BMMS, we need:**
1. **Unified role-based permissions** (Django groups)
2. **Organization-scoped data isolation** (middleware + managers)
3. **Module configuration per organization** (feature toggles)
4. **Graceful UI updates** (show/hide based on permissions)

This analysis provides the foundation for designing a robust, scalable RBAC system for the multi-tenant BMMS platform.
