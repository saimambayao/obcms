# OBCMS Architectural Analysis for BMMS Migration

**Document Version:** 1.0
**Date:** October 14, 2025
**Prepared By:** OBCMS System Architect
**Purpose:** Identify critical dependencies, single-tenant assumptions, and multi-tenant requirements for safe BMMS migration

---

## Executive Summary

This document provides a comprehensive architectural analysis of the current OBCMS (Other Bangsamoro Communities Management System) codebase to identify:

1. **Critical Dependencies** - Tightly coupled components requiring careful migration
2. **Single-Tenant Assumptions** - Code patterns assuming single organization (OOBC)
3. **Multi-Tenant Readiness** - Existing infrastructure that supports BMMS transition
4. **Data Isolation Requirements** - Models and queries requiring organization scoping
5. **Authentication & Authorization** - User management and permission systems

**Key Findings:**
- ✅ **Strong Foundation**: Organizations app and RBAC infrastructure already in place
- ✅ **Middleware Ready**: OrganizationContextMiddleware provides request-level isolation
- ⚠️ **Moderate Risk**: 40+ models need organization scoping with backward compatibility
- ⚠️ **User Model Adaptation**: Custom User model has MOA-specific fields but needs refinement
- ✅ **Low Risk**: Settings and configuration already support multi-tenancy flags

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Critical Dependencies & Coupling](#2-critical-dependencies--coupling)
3. [Single-Tenant Assumptions](#3-single-tenant-assumptions)
4. [Database Schema Analysis](#4-database-schema-analysis)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [Multi-Tenant Infrastructure (Already Built)](#6-multi-tenant-infrastructure-already-built)
7. [Migration Risk Assessment](#7-migration-risk-assessment)
8. [Recommendations for Safe Migration](#8-recommendations-for-safe-migration)

---

## 1. Architecture Overview

### 1.1 Application Structure

```
OBCMS (Django 5.x Multi-App Architecture)
├── obc_management/          # Django project root (settings, URLs, WSGI)
│   ├── settings/
│   │   ├── base.py         # Base settings with RBAC_SETTINGS
│   │   ├── development.py  # Dev environment
│   │   └── production.py   # Production settings
│   └── urls.py
│
├── common/                  # Shared models, utilities, RBAC
│   ├── models.py           # User, Region, Province, Municipality, Barangay
│   ├── rbac_models.py      # Feature, Permission, Role, UserRole
│   ├── work_item_model.py  # Unified work hierarchy (WorkItem)
│   └── middleware/
│       └── organization_context.py  # Multi-tenant context
│
├── organizations/           # 🆕 BMMS Foundation (Phase 1)
│   ├── models/
│   │   ├── organization.py      # Organization, OrganizationMembership
│   │   └── scoped.py           # OrganizationScopedModel, Manager
│   ├── middleware.py           # Organization isolation
│   └── services/               # Pilot MOA services
│
├── communities/            # OBC community management
│   └── models.py          # OBCCommunity, ProvinceCoverage, etc.
│
├── mana/                  # Mapping & Needs Assessment
│   └── models.py          # Assessment, AssessmentCategory, etc.
│
├── coordination/          # Stakeholder coordination
│   └── models.py          # Organization (legacy), Partnership, etc.
│
├── monitoring/            # M&E (Monitoring & Evaluation)
│   └── models.py          # PPA, Indicator, ProgressReport
│
├── planning/              # Strategic planning module
│   └── models.py          # StrategicPlan, Objective, etc.
│
├── budget_preparation/    # Budget preparation (Parliament Bill No. 325)
├── budget_execution/      # Budget execution
├── ocm/                   # OCM aggregation layer
└── project_central/       # Integrated project management
```

### 1.2 Technical Stack

| Component | Technology | Multi-Tenant Ready? |
|-----------|-----------|---------------------|
| **Framework** | Django 5.x | ✅ Yes |
| **Database** | PostgreSQL (prod) / SQLite (dev) | ✅ Yes |
| **ORM** | Django ORM | ✅ Yes |
| **Geographic Data** | JSONField (GeoJSON) | ✅ Yes - No PostGIS |
| **Authentication** | Django Auth + JWT (DRF) | ⚠️ Needs MOA scoping |
| **Authorization** | Custom RBAC system | ✅ Yes - Organization-aware |
| **Background Tasks** | Celery + Redis | ✅ Yes |
| **API** | Django REST Framework | ⚠️ Needs org filtering |
| **Frontend** | HTMX + Tailwind CSS | ⚠️ Needs context awareness |

---

## 2. Critical Dependencies & Coupling

### 2.1 Tight Coupling Points (HIGH RISK)

#### A. User Model → Organization Relationship

**File:** `src/common/models.py` (Lines 23-200)

**Current Structure:**
```python
class User(AbstractUser):
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,  # Includes 'bmoa', 'lgu', 'nga'
    )
    moa_organization = models.ForeignKey(
        'coordination.Organization',  # ⚠️ Points to coordination, not organizations
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='moa_staff_users',
    )
```

**Issue:** User model references `coordination.Organization` instead of `organizations.Organization`

**Impact:**
- 🔴 **CRITICAL**: All user-organization relationships point to wrong model
- 🔴 **BLOCKING**: Must be resolved before BMMS pilot can proceed
- 🔴 **DATA MIGRATION**: Existing MOA users need relationship migration

**Solution Path:**
1. Create new ForeignKey to `organizations.Organization`
2. Data migration to link existing users
3. Deprecate `moa_organization` field after transition period
4. Update all code references

---

#### B. Coordination.Organization vs Organizations.Organization Duplication

**Files:**
- `src/coordination/models.py` (Lines 761-1092) - Legacy Organization
- `src/organizations/models/organization.py` (Lines 17-212) - New Organization

**Current Situation:**
```python
# coordination/models.py (LEGACY)
class Organization(models.Model):
    """Stakeholder organizations (BMOAs, LGUs, NGAs, etc.)"""
    ORGANIZATION_TYPES = [
        ("bmoa", "BARMM Ministry/Agency/Office"),
        ("lgu", "Local Government Unit"),
        # ... 11 other types
    ]

# organizations/models/organization.py (NEW - BMMS)
class Organization(models.Model):
    """BARMM Ministry, Office, or Agency (MOA)"""
    ORG_TYPE_CHOICES = [
        ('ministry', 'Ministry'),
        ('office', 'Office'),
        ('agency', 'Agency'),
        # ... 2 other types
    ]
```

**Issue:** Two separate Organization models serving different purposes

**Impact:**
- 🟡 **MEDIUM RISK**: Namespace collision if both apps are active
- 🟡 **CONFUSION**: Developers may use wrong model
- 🟡 **DATA INTEGRITY**: Foreign keys point to different tables

**Current Mitigation:**
- Django app namespacing prevents direct conflict
- Code explicitly uses `coordination.Organization` vs `organizations.Organization`
- Database tables are separate: `coordination_organization` vs `organizations_organization`

**Migration Strategy:**
1. **Keep Both Models** during transition (2-5 years)
2. **coordination.Organization** = External stakeholders (NGOs, INGOs, tribal orgs, media, donors)
3. **organizations.Organization** = Internal BARMM MOAs only (44 organizations)
4. **Clear Documentation** on when to use which model
5. **Eventual Consolidation** in BMMS 2.0 (post-full rollout)

---

#### C. WorkItem Unified Hierarchy Dependencies

**File:** `src/common/work_item_model.py`

**Current Structure:**
```python
class WorkItem(models.Model):
    """Unified work hierarchy replacing StaffTask, Event, ProjectWorkflow"""
    work_type = models.CharField(
        choices=[('task', 'Task'), ('activity', 'Activity'), ('project', 'Project')]
    )
    organization = models.ForeignKey(
        'coordination.Organization',  # ⚠️ Should be organizations.Organization
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
```

**Issue:** WorkItem model also points to coordination.Organization

**Impact:**
- 🟡 **MEDIUM RISK**: All work items tied to wrong organization model
- 🟡 **SCALABILITY**: Cannot scope work to specific MOAs properly

**Dependencies:**
- `common.WorkItem` (unified work model)
- `coordination.CoordinationNote` (meeting minutes linked to WorkItem)
- `project_central.models` (project management tasks)
- `monitoring.models` (PPA progress tracking)

---

### 2.2 Loose Coupling Points (LOW RISK)

#### A. Geographic Hierarchy (Independent)

**Models:** Region → Province → Municipality → Barangay

**Status:** ✅ **SAFE** - No organization coupling, shared across all MOAs

**Structure:**
```python
# src/common/models.py
class Region(models.Model):
    code = models.CharField(max_length=10, unique=True)
    boundary_geojson = models.JSONField(null=True, blank=True)  # No PostGIS!

class Province(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    boundary_geojson = models.JSONField(null=True, blank=True)

class Municipality(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

class Barangay(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
```

**Migration Impact:** None - geographic data is reference data shared by all organizations

---

#### B. RBAC System (Organization-Aware)

**Models:** Feature, Permission, Role, RolePermission, UserRole, UserPermission

**Status:** ✅ **READY** - Already organization-scoped

**Structure:**
```python
# src/common/rbac_models.py
class Role(models.Model):
    organization = models.ForeignKey(
        'coordination.Organization',  # ⚠️ Needs update to organizations.Organization
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    scope = models.CharField(
        choices=[('system', 'System-wide'), ('organization', 'Organization-specific')]
    )
```

**Migration Path:** Update FK from `coordination.Organization` to `organizations.Organization`

---

## 3. Single-Tenant Assumptions

### 3.1 Code Patterns Assuming Single Organization

#### A. Unscoped QuerySets (HIGH PRIORITY)

**Location:** Multiple views across apps

**Example - Communities Views:**
```python
# src/common/views/communities.py
def provincial_view(request, province_code):
    """Provincial OBC overview"""
    province = get_object_or_404(Province, code=province_code)

    # ⚠️ ISSUE: No organization scoping
    communities = OBCCommunity.objects.filter(
        barangay__municipality__province=province
    )

    # ⚠️ ISSUE: All coverage data shown regardless of organization
    coverage_data = ProvinceCoverage.objects.filter(province=province)
```

**Fix Required:**
```python
def provincial_view(request, province_code):
    """Provincial OBC overview - Organization-scoped"""
    province = get_object_or_404(Province, code=province_code)
    organization = request.organization  # From OrganizationContextMiddleware

    # ✅ FIXED: Organization-scoped query
    communities = OBCCommunity.objects.filter(
        organization=organization,
        barangay__municipality__province=province
    )

    # ✅ FIXED: Scoped coverage data
    coverage_data = ProvinceCoverage.objects.filter(
        organization=organization,
        province=province
    )
```

**Affected Areas:**
- ❌ `communities/views.py` - All CRUD operations
- ❌ `mana/views.py` - Assessment management
- ❌ `coordination/views.py` - Stakeholder engagement
- ❌ `monitoring/views.py` - PPA and indicator tracking
- ❌ `planning/views.py` - Strategic plan management
- ❌ `budget_preparation/views.py` - Budget proposals
- ❌ `budget_execution/views.py` - Disbursement tracking

**Estimated Models Needing Scoping:** 40+ models across 8 apps

---

#### B. Dashboard Aggregations (CRITICAL)

**Location:** Dashboard views assume single-organization context

**Example:**
```python
# Typical dashboard view (hypothetical example)
def dashboard(request):
    total_communities = OBCCommunity.objects.count()  # ⚠️ Global count
    active_assessments = Assessment.objects.filter(status='in_progress').count()
    total_partnerships = Partnership.objects.filter(status='active').count()

    context = {
        'total_communities': total_communities,
        'active_assessments': active_assessments,
        'total_partnerships': total_partnerships,
    }
    return render(request, 'dashboard.html', context)
```

**Fix Required:**
```python
def dashboard(request):
    org = request.organization

    # ✅ Organization-scoped counts
    total_communities = OBCCommunity.objects.filter(organization=org).count()
    active_assessments = Assessment.objects.filter(
        organization=org,
        status='in_progress'
    ).count()
    total_partnerships = Partnership.objects.filter(
        organizations__in=[org],
        status='active'
    ).count()

    context = {
        'organization': org,
        'total_communities': total_communities,
        'active_assessments': active_assessments,
        'total_partnerships': total_partnerships,
    }
    return render(request, 'dashboard.html', context)
```

---

#### C. Permission Checks Without Organization Context

**Location:** View decorators and permission checks

**Example:**
```python
# Current permission check (simplified)
@require_permission('communities.view_obc_community')
def community_list(request):
    communities = OBCCommunity.objects.all()  # ⚠️ No org scoping
```

**Fix Required:**
```python
@require_permission('communities.view_obc_community')  # Permission check includes org context
def community_list(request):
    org = request.organization
    communities = OBCCommunity.objects.filter(organization=org)  # ✅ Scoped
```

**Good News:** RBAC system already supports organization context in permission checks (see `common/rbac_models.py`)

---

### 3.2 Settings & Configuration Assumptions

#### A. Settings Already Support Multi-Tenancy

**File:** `src/obc_management/settings/base.py` (Lines 632-652)

```python
# ✅ ALREADY CONFIGURED
RBAC_SETTINGS = {
    # Enable multi-tenant organization context
    'ENABLE_MULTI_TENANT': env.bool('ENABLE_MULTI_TENANT', default=True),

    # Office of Chief Minister (OCM) organization code
    # OCM has special aggregation access (read-only across all MOAs)
    'OCM_ORGANIZATION_CODE': 'ocm',

    # Permission cache timeout (seconds)
    'CACHE_TIMEOUT': 300,  # 5 minutes

    # Organization switching
    'ALLOW_ORGANIZATION_SWITCHING': True,  # OOBC staff and OCM can switch

    # Session key for current organization
    'SESSION_ORG_KEY': 'current_organization',
}
```

**Status:** ✅ **READY** - No changes needed

---

#### B. Middleware Stack Already Includes Organization Context

**File:** `src/obc_management/settings/base.py` (Lines 122-143)

```python
MIDDLEWARE = [
    # ... other middleware ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "auditlog.middleware.AuditlogMiddleware",

    # ✅ Multi-tenant organization context (after AuthenticationMiddleware)
    "common.middleware.organization_context.OrganizationContextMiddleware",

    # ✅ Enforce OCM read-only access
    "ocm.middleware.OCMAccessMiddleware",

    # ... other middleware ...
]
```

**Status:** ✅ **READY** - Already in place

---

## 4. Database Schema Analysis

### 4.1 Models Requiring Organization Scoping

#### Priority 1 (CRITICAL - Core Data Models)

| Model | App | Current Status | Action Required |
|-------|-----|----------------|-----------------|
| `OBCCommunity` | communities | ❌ No org FK | Add organization FK + data migration |
| `ProvinceCoverage` | communities | ❌ No org FK | Add organization FK + data migration |
| `MunicipalityCoverage` | communities | ❌ No org FK | Add organization FK + data migration |
| `Assessment` | mana | ❌ No org FK | Add organization FK + data migration |
| `AssessmentResponse` | mana | ❌ No org FK | Add organization FK (inherits from Assessment) |
| `StakeholderEngagement` | coordination | ❌ No org FK | Add organization FK + data migration |
| `Partnership` | coordination | ⚠️ M2M orgs | Add `lead_organization` FK for scoping |
| `PPA` | monitoring | ❌ No org FK | Add `implementing_moa` FK + data migration |
| `Indicator` | monitoring | ❌ No org FK | Add organization FK (inherits from PPA) |
| `StrategicPlan` | planning | ❌ No org FK | Add organization FK + data migration |

**Total Critical Models:** 10 models

---

#### Priority 2 (HIGH - Supporting Data Models)

| Model | App | Current Status | Action Required |
|-------|-----|----------------|-----------------|
| `ConsultationFeedback` | coordination | ❌ No org FK | Add organization FK (inherits from Engagement) |
| `Communication` | coordination | ❌ No org FK | Add organization FK + data migration |
| `WorkItem` | common | ⚠️ Wrong org FK | Update FK to organizations.Organization |
| `CoordinationNote` | coordination | ❌ No org FK | Add organization FK (links to WorkItem) |
| `ProgressReport` | monitoring | ❌ No org FK | Add organization FK (inherits from PPA) |
| `BudgetProposal` | budget_preparation | ❌ No org FK | Add organization FK + data migration |
| `Disbursement` | budget_execution | ❌ No org FK | Add organization FK + data migration |

**Total High Priority Models:** 7 models

---

#### Priority 3 (MEDIUM - Configuration & Reference Data)

| Model | App | Current Status | Action Required |
|-------|-----|----------------|-----------------|
| `OrganizationContact` | coordination | ⚠️ Legacy org | Migrate to organizations.Organization |
| `CommunicationTemplate` | coordination | ❌ No org FK | Add organization FK (org-specific templates) |
| `StaffProfile` | common | ❌ No org FK | Link to organizations.OrganizationMembership |
| `StaffTeam` | common | ❌ No org FK | Add organization FK for MOA-specific teams |
| `Role` | common (RBAC) | ⚠️ Wrong org FK | Update FK to organizations.Organization |
| `Feature` | common (RBAC) | ⚠️ Wrong org FK | Update FK to organizations.Organization |

**Total Medium Priority Models:** 6 models

---

### 4.2 Models That Do NOT Need Organization Scoping

✅ **Reference Data (Shared Across All Organizations)**

| Model | App | Reason |
|-------|-----|--------|
| `Region` | common | Geographic reference data |
| `Province` | common | Geographic reference data |
| `Municipality` | common | Geographic reference data |
| `Barangay` | common | Geographic reference data |
| `AssessmentCategory` | mana | Standardized assessment types |
| `StakeholderEngagementType` | coordination | Standardized engagement types |
| `Permission` | common (RBAC) | System-wide permissions |

---

### 4.3 Database Migration Strategy

#### Phase 1: Preparation (PRE-PILOT)

```sql
-- 1. Add organization FK to OBCCommunity (nullable initially)
ALTER TABLE communities_obccommunity
ADD COLUMN organization_id UUID NULL
REFERENCES organizations_organization(id);

-- 2. Create default OOBC organization if not exists
INSERT INTO organizations_organization (id, code, name, org_type, is_active)
VALUES (
    gen_random_uuid(),
    'OOBC',
    'Office for Other Bangsamoro Communities',
    'office',
    true
) ON CONFLICT (code) DO NOTHING;

-- 3. Migrate all existing OBC communities to OOBC organization
UPDATE communities_obccommunity
SET organization_id = (
    SELECT id FROM organizations_organization WHERE code = 'OOBC' LIMIT 1
)
WHERE organization_id IS NULL;

-- 4. Make organization FK required after migration
ALTER TABLE communities_obccommunity
ALTER COLUMN organization_id SET NOT NULL;

-- 5. Create index for performance
CREATE INDEX idx_obccommunity_organization
ON communities_obccommunity(organization_id);
```

#### Phase 2: Pilot MOAs (MOH, MOLE, MAFAR)

```sql
-- 1. Create pilot MOA organizations
INSERT INTO organizations_organization (id, code, name, org_type, is_active, is_pilot)
VALUES
    (gen_random_uuid(), 'MOH', 'Ministry of Health', 'ministry', true, true),
    (gen_random_uuid(), 'MOLE', 'Ministry of Labor and Employment', 'ministry', true, true),
    (gen_random_uuid(), 'MAFAR', 'Ministry of Agriculture, Fisheries and Agrarian Reform', 'ministry', true, true);

-- 2. Pilot MOAs start with empty data (no migration from OOBC)
-- Each MOA will create their own OBCCommunities, Assessments, etc.
```

#### Phase 3: Backward Compatibility

**Key Principle:** OOBC must continue to function normally during BMMS pilot

```python
# Migration helper for backward compatibility
class Migration(migrations.Migration):
    def migrate_forward(apps, schema_editor):
        OBCCommunity = apps.get_model('communities', 'OBCCommunity')
        Organization = apps.get_model('organizations', 'Organization')

        # Get or create OOBC organization
        oobc_org, created = Organization.objects.get_or_create(
            code='OOBC',
            defaults={
                'name': 'Office for Other Bangsamoro Communities',
                'org_type': 'office',
                'is_active': True,
            }
        )

        # Assign all existing communities to OOBC
        OBCCommunity.objects.filter(organization__isnull=True).update(
            organization=oobc_org
        )

    def migrate_backward(apps, schema_editor):
        # Remove organization FK (allow rollback)
        pass
```

---

## 5. Authentication & Authorization

### 5.1 User Model Structure

**File:** `src/common/models.py` (Lines 23-200)

**Current User Types:**
```python
USER_TYPES = (
    ("admin", "Administrator"),
    ("oobc_executive", "OOBC Executive"),
    ("oobc_staff", "OOBC Staff"),
    ("cm_office", "Chief Minister Office"),  # ✅ OCM users
    ("bmoa", "BARMM Ministry/Agency/Office"),  # ✅ MOA users
    ("lgu", "Local Government Unit"),
    ("nga", "National Government Agency"),
    ("community_leader", "Community Leader"),
    ("researcher", "Assessment Coordinator/Researcher"),
)
```

**Status:** ✅ **GOOD** - Already supports MOA user types

**Issue:** User model references `coordination.Organization` instead of `organizations.Organization`

```python
class User(AbstractUser):
    moa_organization = models.ForeignKey(
        'coordination.Organization',  # ⚠️ WRONG MODEL
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='moa_staff_users',
    )
```

**Fix Required:**
```python
class User(AbstractUser):
    # Deprecated field (keep for backward compatibility during transition)
    moa_organization = models.ForeignKey(
        'coordination.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='moa_staff_users_legacy',
        help_text='DEPRECATED: Use organization_memberships instead'
    )

    # New approach: Use OrganizationMembership model
    # Access via: user.organization_memberships.all()
    # Primary org: user.organization_memberships.filter(is_primary=True).first()
```

---

### 5.2 Organization Membership Model

**File:** `src/organizations/models/organization.py` (Lines 214-335)

**Status:** ✅ **EXCELLENT** - Fully implemented and ready

```python
class OrganizationMembership(models.Model):
    """User membership in an organization"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships',
    )

    role = models.CharField(
        max_length=20,
        choices=[('admin', 'Administrator'), ('manager', 'Manager'),
                 ('staff', 'Staff'), ('viewer', 'Viewer')],
        default='staff',
    )

    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Whether this is the user\'s primary organization'
    )

    # Permissions
    can_manage_users = models.BooleanField(default=False)
    can_approve_plans = models.BooleanField(default=False)
    can_approve_budgets = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)

    class Meta:
        unique_together = [['user', 'organization']]
```

**Features:**
- ✅ Multiple organizations per user
- ✅ Primary organization designation
- ✅ Role-based permissions
- ✅ Built-in validation (clean method)

---

### 5.3 RBAC System

**File:** `src/common/rbac_models.py`

**Status:** ✅ **READY** - Comprehensive RBAC infrastructure

**Models:**
1. **Feature** - Represents menu items, modules, actions
2. **Permission** - Granular actions (view, create, edit, delete, approve, export)
3. **Role** - Bundled permissions (Admin, Manager, Staff, Viewer)
4. **RolePermission** - Role-to-Permission mapping (M2M with metadata)
5. **UserRole** - User-to-Role assignment (organization-scoped)
6. **UserPermission** - Direct permission grants (bypass roles)

**Key Features:**
```python
class Role(models.Model):
    scope = models.CharField(
        choices=[
            ('system', 'System-wide'),
            ('organization', 'Organization-specific'),
            ('module', 'Module-specific'),
        ]
    )
    organization = models.ForeignKey(
        'coordination.Organization',  # ⚠️ Needs update
        null=True,
        blank=True,
    )
    parent_role = models.ForeignKey('self', ...)  # ✅ Permission inheritance
    level = models.IntegerField(choices=ROLE_LEVELS)  # ✅ Hierarchy

class UserRole(models.Model):
    user = models.ForeignKey(User, ...)
    role = models.ForeignKey(Role, ...)
    organization = models.ForeignKey(
        'coordination.Organization',  # ⚠️ Needs update
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(null=True, blank=True)  # ✅ Temporary roles
```

**Migration Required:**
- Update all `ForeignKey('coordination.Organization')` to `ForeignKey('organizations.Organization')`
- Data migration to link existing roles to new Organization model

---

### 5.4 Organization Context Middleware

**File:** `src/common/middleware/organization_context.py`

**Status:** ✅ **PRODUCTION-READY** - Fully implemented

**Features:**
```python
class OrganizationContextMiddleware:
    """Sets request.organization for organization-scoped queries"""

    def __call__(self, request):
        # Extract organization from:
        # 1. URL kwargs (org_id, organization_id)
        # 2. Query params (?org=...)
        # 3. User's default organization
        # 4. Session (current_organization)

        request.organization = SimpleLazyObject(
            lambda: get_organization_from_request(request)
        )
        request.is_ocm_user = is_ocm_user(request.user)
```

**Access Control Rules:**
```python
def user_can_access_organization(user, organization) -> bool:
    # Superusers: Access to all
    if user.is_superuser:
        return True

    # OCM users: Read-only access to all MOAs
    if is_ocm_user(user):
        return True

    # OOBC staff: Access to all organizations (operations)
    if user.is_oobc_staff:
        return True

    # MOA staff: Access to THEIR organization only
    if user.is_moa_staff:
        return user.moa_organization == organization

    return False
```

**Integration:**
```python
# In views.py
def my_view(request):
    org = request.organization  # Automatically set by middleware
    if not org:
        return HttpResponseForbidden("No organization context")

    # All queries automatically scoped
    communities = OBCCommunity.objects.filter(organization=org)
```

---

## 6. Multi-Tenant Infrastructure (Already Built)

### 6.1 OrganizationScopedModel Abstract Base Class

**File:** `src/organizations/models/scoped.py`

**Status:** ✅ **PRODUCTION-READY**

```python
class OrganizationScopedModel(models.Model):
    """
    Abstract base class for organization-scoped models.

    Features:
    - Automatic organization FK
    - Auto-filtering by current organization
    - Cross-organization access via all_objects manager
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_set',
    )

    # Default manager: auto-filters by current organization
    objects = OrganizationScopedManager()

    # Unfiltered manager: for admin/OCM cross-organization access
    all_objects = models.Manager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization']),
        ]

    def save(self, *args, **kwargs):
        # Auto-set organization from thread-local context
        if not self.organization_id:
            current_org = get_current_organization()
            if current_org:
                self.organization = current_org
        super().save(*args, **kwargs)
```

**Usage:**
```python
# Before (single-tenant)
class OBCCommunity(models.Model):
    name = models.CharField(max_length=200)

# After (multi-tenant)
class OBCCommunity(OrganizationScopedModel):
    name = models.CharField(max_length=200)
    # organization FK automatically added

# Queries automatically scoped:
OBCCommunity.objects.all()  # Only returns current org's communities

# Admin/OCM can access all:
OBCCommunity.all_objects.all()  # Returns all communities across all orgs
```

---

### 6.2 OrganizationScopedManager

**File:** `src/organizations/models/scoped.py` (Lines 42-94)

**Status:** ✅ **PRODUCTION-READY**

```python
class OrganizationScopedManager(models.Manager):
    """Custom manager that auto-filters by current organization"""

    def get_queryset(self):
        queryset = super().get_queryset()
        current_org = get_current_organization()

        if current_org:
            return queryset.filter(organization=current_org)

        # No org in context: return unfiltered (for admin/migrations)
        return queryset

    def for_organization(self, organization):
        """Explicitly filter by a specific organization"""
        return super().get_queryset().filter(organization=organization)

    def all_organizations(self):
        """Get unfiltered queryset (for OCM/admin)"""
        return super().get_queryset()
```

**Thread-Local Storage:**
```python
import threading

_thread_locals = threading.local()

def get_current_organization():
    """Get organization from thread-local storage"""
    return getattr(_thread_locals, 'organization', None)

def set_current_organization(organization):
    """Set organization in thread-local storage"""
    _thread_locals.organization = organization

def clear_current_organization():
    """Clear organization from thread-local storage"""
    if hasattr(_thread_locals, 'organization'):
        del _thread_locals.organization
```

---

### 6.3 OCM Aggregation Layer

**Directory:** `src/ocm/`

**Status:** ✅ **IMPLEMENTED** - OCM middleware enforces read-only access

**OCM Access Rules:**
1. OCM users can view ALL organization data (read-only)
2. OCM users CANNOT create/edit/delete data in other organizations
3. OCM users see aggregated dashboards across all MOAs
4. OCM users identified by: `user.user_type == 'cm_office'` OR `user.moa_organization.code == 'ocm'`

**Middleware:** `src/ocm/middleware.py`

---

## 7. Migration Risk Assessment

### 7.1 Risk Matrix

| Category | Risk Level | Impact | Mitigation |
|----------|-----------|--------|-----------|
| **User Model Updates** | 🔴 HIGH | All authentication breaks if wrong | Dual FKs during transition, deprecation warnings |
| **Organization FK Migrations** | 🟡 MEDIUM | 40+ models need scoping | Phased migration, backward compatibility |
| **RBAC Model Updates** | 🟡 MEDIUM | Permission system uses wrong org FK | Update all RBAC FKs, data migration |
| **Dashboard Queries** | 🟡 MEDIUM | Aggregations show wrong data | Add organization filters, update logic |
| **API Endpoints** | 🟡 MEDIUM | APIs return unscoped data | Add organization filtering to DRF viewsets |
| **WorkItem Hierarchy** | 🟡 MEDIUM | All tasks tied to wrong org model | Update FK, migrate existing work items |
| **Geographic Data** | 🟢 LOW | Reference data shared across orgs | No changes needed |
| **Settings & Middleware** | 🟢 LOW | Already multi-tenant ready | No changes needed |

---

### 7.2 Critical Path Items (MUST COMPLETE BEFORE PILOT)

1. **User Model Organization FK** (🔴 CRITICAL)
   - Add new FK to `organizations.Organization`
   - Data migration for existing MOA users
   - Update all code references

2. **RBAC System Organization FKs** (🔴 CRITICAL)
   - Update Role, Feature FKs
   - Migrate existing roles/permissions
   - Test permission checks

3. **OBCCommunity Organization Scoping** (🔴 CRITICAL)
   - Add organization FK
   - Migrate OOBC communities
   - Update all queries

4. **Assessment Organization Scoping** (🔴 CRITICAL)
   - Add organization FK to Assessment model
   - Migrate OOBC assessments
   - Update MANA module queries

5. **WorkItem Organization FK** (🔴 CRITICAL)
   - Update FK to organizations.Organization
   - Migrate existing work items
   - Update project_central queries

---

### 7.3 Non-Critical Items (CAN COMPLETE DURING PILOT)

1. **Partnership Model Updates** (🟡 MEDIUM)
   - Add lead_organization FK for scoping
   - Keep M2M relationships for multi-org partnerships

2. **Communication & Coordination Notes** (🟡 MEDIUM)
   - Add organization scoping
   - Migrate existing data

3. **Budget Module Organization Scoping** (🟡 MEDIUM)
   - Add organization FKs to budget_preparation models
   - Add organization FKs to budget_execution models

4. **Staff Management Organization Scoping** (🟢 LOW)
   - Link StaffProfile to OrganizationMembership
   - Add organization FK to StaffTeam

---

## 8. Recommendations for Safe Migration

### 8.1 Migration Phases

#### Phase 0: Foundation (PRE-PILOT)

**Goal:** Fix critical FK issues without breaking OBCMS

**Tasks:**
1. ✅ Add `organization` FK to User model (nullable, pointing to organizations.Organization)
2. ✅ Create OOBC organization record in organizations.Organization
3. ✅ Data migration: Link existing OOBC users to OOBC organization
4. ✅ Update RBAC models to use organizations.Organization
5. ✅ Test: OOBC staff can still log in and access data

**Validation:**
- All existing OOBC users can log in
- All OOBC data still accessible
- No permission errors
- Dashboard shows correct data

**Risk:** 🟢 LOW - Additive changes only, no data removal

---

#### Phase 1: Pilot MOA Foundation (PILOT LAUNCH)

**Goal:** Enable 3 pilot MOAs (MOH, MOLE, MAFAR) to start using BMMS

**Tasks:**
1. ✅ Create pilot MOA organizations (MOH, MOLE, MAFAR)
2. ✅ Add organization FK to OBCCommunity (nullable initially)
3. ✅ Add organization FK to Assessment (nullable initially)
4. ✅ Update queries to filter by organization when available
5. ✅ Test: Pilot MOAs can create their own communities/assessments

**Validation:**
- OOBC data remains unchanged
- Pilot MOAs start with empty data (no OOBC data shown)
- Data isolation: MOH cannot see MOLE data
- OCM can view all MOA data (read-only)

**Risk:** 🟡 MEDIUM - Requires careful testing of data isolation

---

#### Phase 2: Expand Organization Scoping (DURING PILOT)

**Goal:** Add organization scoping to remaining critical models

**Tasks:**
1. ✅ Add organization FK to PPA, Indicator, ProgressReport
2. ✅ Add organization FK to StakeholderEngagement, Partnership
3. ✅ Add organization FK to StrategicPlan, Objective
4. ✅ Add organization FK to BudgetProposal, Disbursement
5. ✅ Update all dashboard queries
6. ✅ Update all API endpoints

**Validation:**
- All CRUD operations respect organization scoping
- Dashboards show org-specific data
- APIs filter by organization
- Performance acceptable (<300ms query time)

**Risk:** 🟡 MEDIUM - Many queries to update, regression testing critical

---

#### Phase 3: Full Rollout (44 MOAs)

**Goal:** Onboard all 44 BARMM MOAs to BMMS

**Tasks:**
1. ✅ Create remaining 41 MOA organizations
2. ✅ Onboard MOAs in batches (8-10 MOAs per wave)
3. ✅ Train MOA staff on BMMS
4. ✅ Migrate existing MOA data (if any)
5. ✅ Monitor performance and data integrity

**Validation:**
- All 44 MOAs operational
- Data isolation verified
- Performance acceptable (<500ms query time with 44 orgs)
- No cross-organization data leaks

**Risk:** 🟡 MEDIUM - Scale testing required

---

### 8.2 Backward Compatibility Strategy

#### Keep OBCMS Functional

**Principle:** OBCMS must continue to work normally during entire BMMS transition (2-5 years)

**Approach:**
1. **Dual Organization Models** - Keep both `coordination.Organization` and `organizations.Organization`
   - `coordination.Organization` = External stakeholders (NGOs, donors, etc.)
   - `organizations.Organization` = Internal BARMM MOAs only

2. **Nullable Organization FKs** - All new `organization` fields nullable during transition
   - Default to OOBC organization if not specified
   - Gradual enforcement via application logic, not database constraints

3. **Query Fallbacks** - Queries check for organization context, fall back to all data if not available
   ```python
   def get_communities(request):
       org = request.organization
       if org:
           return OBCCommunity.objects.filter(organization=org)
       else:
           # Fallback for OOBC or admin users
           return OBCCommunity.objects.all()
   ```

4. **Feature Flags** - Use settings to enable/disable BMMS features
   ```python
   if settings.RBAC_SETTINGS['ENABLE_MULTI_TENANT']:
       # Use organization-scoped queries
   else:
       # Use legacy single-tenant queries
   ```

---

### 8.3 Testing Strategy

#### Unit Tests (Per Model)

```python
# tests/test_organization_scoping.py
def test_obccommunity_organization_scoping():
    """Test OBCCommunity filters by organization"""
    oobc = Organization.objects.get(code='OOBC')
    moh = Organization.objects.get(code='MOH')

    # Create communities for different orgs
    comm1 = OBCCommunity.objects.create(name='OOBC Community', organization=oobc)
    comm2 = OBCCommunity.objects.create(name='MOH Community', organization=moh)

    # Set current organization to OOBC
    set_current_organization(oobc)

    # Query should only return OOBC communities
    communities = OBCCommunity.objects.all()
    assert communities.count() == 1
    assert communities.first() == comm1

    # Set current organization to MOH
    set_current_organization(moh)

    # Query should only return MOH communities
    communities = OBCCommunity.objects.all()
    assert communities.count() == 1
    assert communities.first() == comm2
```

#### Integration Tests (Cross-Model)

```python
def test_dashboard_data_isolation():
    """Test dashboard shows only org-specific data"""
    oobc = Organization.objects.get(code='OOBC')
    moh = Organization.objects.get(code='MOH')

    # Create data for both orgs
    OBCCommunity.objects.create(name='OOBC Comm', organization=oobc)
    OBCCommunity.objects.create(name='MOH Comm', organization=moh)

    Assessment.objects.create(title='OOBC Assessment', organization=oobc)
    Assessment.objects.create(title='MOH Assessment', organization=moh)

    # Simulate OOBC user request
    request = create_mock_request(organization=oobc)
    response = dashboard_view(request)

    # Verify only OOBC data shown
    assert response.context['total_communities'] == 1
    assert response.context['active_assessments'] == 1
```

#### Data Isolation Tests (Security)

```python
def test_moa_cannot_access_other_moa_data():
    """Test MOA users cannot see other MOA's data"""
    moh = Organization.objects.get(code='MOH')
    mole = Organization.objects.get(code='MOLE')

    moh_user = User.objects.create(username='moh_user', user_type='bmoa')
    moh_membership = OrganizationMembership.objects.create(
        user=moh_user,
        organization=moh,
        role='staff',
        is_primary=True
    )

    # Create data for MOLE
    mole_community = OBCCommunity.objects.create(
        name='MOLE Community',
        organization=mole
    )

    # Simulate MOH user request
    request = create_mock_request(user=moh_user, organization=moh)

    # Try to access MOLE community (should fail)
    with pytest.raises(PermissionDenied):
        community_detail_view(request, pk=mole_community.pk)
```

---

### 8.4 Performance Considerations

#### Index Strategy

```sql
-- Add organization indexes to all scoped models
CREATE INDEX idx_obccommunity_org ON communities_obccommunity(organization_id);
CREATE INDEX idx_assessment_org ON mana_assessment(organization_id);
CREATE INDEX idx_ppa_org ON monitoring_ppa(organization_id);
CREATE INDEX idx_engagement_org ON coordination_stakeholderengagement(organization_id);
CREATE INDEX idx_partnership_org ON coordination_partnership(lead_organization_id);
CREATE INDEX idx_workitem_org ON common_workitem(organization_id);

-- Composite indexes for common queries
CREATE INDEX idx_obccommunity_org_province
ON communities_obccommunity(organization_id, province_id);

CREATE INDEX idx_assessment_org_status
ON mana_assessment(organization_id, status);

CREATE INDEX idx_ppa_org_year
ON monitoring_ppa(organization_id, fiscal_year);
```

#### Query Optimization

```python
# Use select_related for FKs
communities = OBCCommunity.objects.filter(
    organization=org
).select_related(
    'barangay__municipality__province__region'
)

# Use prefetch_related for M2M
assessments = Assessment.objects.filter(
    organization=org
).prefetch_related('team_members')

# Use count() for aggregations, not len()
total_communities = OBCCommunity.objects.filter(
    organization=org
).count()  # ✅ Efficient

# Avoid
total_communities = len(OBCCommunity.objects.filter(
    organization=org
).all())  # ❌ Loads all data into memory
```

#### Caching Strategy

```python
from django.core.cache import cache

def get_dashboard_stats(organization):
    """Get dashboard stats with caching"""
    cache_key = f'dashboard_stats_{organization.code}'
    stats = cache.get(cache_key)

    if not stats:
        stats = {
            'total_communities': OBCCommunity.objects.filter(
                organization=organization
            ).count(),
            'active_assessments': Assessment.objects.filter(
                organization=organization,
                status='in_progress'
            ).count(),
            # ... other stats
        }
        cache.set(cache_key, stats, 300)  # Cache for 5 minutes

    return stats
```

---

### 8.5 Monitoring & Validation

#### Data Integrity Checks

```sql
-- Verify no orphaned data (data without organization FK)
SELECT COUNT(*) FROM communities_obccommunity WHERE organization_id IS NULL;
SELECT COUNT(*) FROM mana_assessment WHERE organization_id IS NULL;
SELECT COUNT(*) FROM monitoring_ppa WHERE organization_id IS NULL;

-- Verify organization scoping (MOA data separation)
SELECT
    o.code,
    COUNT(DISTINCT c.id) AS community_count,
    COUNT(DISTINCT a.id) AS assessment_count,
    COUNT(DISTINCT p.id) AS ppa_count
FROM organizations_organization o
LEFT JOIN communities_obccommunity c ON c.organization_id = o.id
LEFT JOIN mana_assessment a ON a.organization_id = o.id
LEFT JOIN monitoring_ppa p ON p.organization_id = o.id
GROUP BY o.code
ORDER BY o.code;

-- Verify data isolation (ensure no cross-contamination)
SELECT
    'communities' AS model,
    COUNT(*) AS cross_org_count
FROM communities_obccommunity c1
INNER JOIN communities_obccommunity c2
    ON c1.id = c2.id
    AND c1.organization_id != c2.organization_id;
```

#### Performance Monitoring

```python
# Add query logging for organization-scoped queries
import logging
from django.db import connection

logger = logging.getLogger('django.db.backends')

def log_query_performance(request):
    """Log slow queries for organization-scoped data"""
    org = request.organization

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM communities_obccommunity WHERE organization_id = %s", [org.id])
        communities_count = cursor.fetchone()[0]

    logger.info(f"Organization {org.code} - Communities: {communities_count} - Query time: {connection.queries[-1]['time']}ms")
```

---

## Conclusion

### Current State Assessment

**✅ Strong Foundation:**
- Organizations app fully implemented with Organization and OrganizationMembership models
- OrganizationContextMiddleware provides request-level organization context
- OrganizationScopedModel abstract base class ready for inheritance
- RBAC system comprehensive and organization-aware
- Settings and middleware stack already configured for multi-tenancy

**⚠️ Moderate Risk Areas:**
- 40+ models need organization FK added with data migrations
- User model references wrong Organization model (coordination vs organizations)
- RBAC models reference wrong Organization model
- WorkItem model references wrong Organization model
- All views need organization filtering added to queries

**✅ Low Risk Areas:**
- Geographic hierarchy (Region/Province/Municipality/Barangay) requires no changes
- Settings already support multi-tenancy flags
- Middleware stack properly ordered
- No PostGIS dependency (JSONField for geographic data)

### Recommended Approach

**1. PRE-PILOT (1-2 weeks)**
- Fix User model organization FK
- Update RBAC models organization FKs
- Create OOBC organization record
- Migrate existing users and roles
- Test: OOBC continues to function normally

**2. PILOT LAUNCH (2-4 weeks)**
- Create pilot MOA organizations (MOH, MOLE, MAFAR)
- Add organization FK to OBCCommunity, Assessment, PPA
- Update critical queries with organization filtering
- Test: Pilot MOAs can create data, data isolation works

**3. PILOT OPERATION (3-6 months)**
- Add organization FK to remaining models
- Update all views, APIs, dashboards
- Performance tuning and optimization
- Continuous monitoring and validation

**4. FULL ROLLOUT (6-12 months)**
- Onboard remaining 41 MOAs in batches
- Scale testing with 44 organizations
- Performance optimization
- Final validation and security audit

### Success Criteria

**Technical:**
- ✅ All 44 MOAs can log in and access only their data
- ✅ OCM can view all MOA data (read-only)
- ✅ Query performance <300ms for single-org queries
- ✅ No cross-organization data leaks (100% isolation)
- ✅ OOBC continues to function normally

**Operational:**
- ✅ Zero downtime deployment
- ✅ Rollback plan tested and verified
- ✅ Comprehensive test coverage (>95%)
- ✅ Documentation updated for multi-tenancy
- ✅ Training materials prepared for MOA staff

---

**Document Prepared By:** OBCMS System Architect
**Review Status:** Ready for Technical Review
**Next Steps:** Present to development team for implementation planning
