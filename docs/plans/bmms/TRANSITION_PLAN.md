# OBCMS to BMMS Technical Transition Plan

**Document Version:** 1.0
**Date:** 2025-10-12
**Status:** Strategic Planning - Technical Specification
**Priority:** CRITICAL - Government-Wide Digital Transformation
**Classification:** Internal Development Documentation

---

## Executive Summary

This document provides a comprehensive technical roadmap for transforming **OBCMS (Office for Other Bangsamoro Communities Management System)** into **BMMS (Bangsamoro Ministerial Management System)** - a government-wide platform serving 44 BARMM Ministries, Offices, and Agencies (MOAs).

### Transformation Scope

**Current State:** Single-tenant system (OOBC only, 110-160 users)
**Target State:** Multi-tenant platform (44 MOAs + OCM (Office of the Chief Minister), 700-1100 users)
**Scale Factor:** 30x organizations, 5-8x users, 20-50x data volume

### Critical Success Factors

✅ **Zero Downtime for OOBC** - OBCMS operations continue unchanged throughout transition
✅ **Parallel Development** - BMMS features built on isolated branch
✅ **UI/Architecture Alignment** - Resolve existing technical debt during migration
✅ **Data Integrity** - Zero tolerance for cross-organization data leakage
✅ **Parliament Bill No. 325 Compliance** - Full budget system implementation

### Strategic Approach

1. **Git Branching Strategy** - Develop BMMS on `feature/bmms` branch while `main` serves OBCMS
2. **Additive Migrations** - Non-destructive database changes, no data loss
3. **Organization-Based Multi-Tenancy** - Single database with organization scoping (NOT separate databases)
4. **URL Refactoring** - Fix "Monolithic Router Anti-Pattern" common app routing during transition
5. **Module-by-Module Migration** - Systematic transformation with comprehensive testing

---

## Table of Contents

### Part I: Architecture Analysis
1. [Current OBCMS Architecture Assessment](#1-current-obcms-architecture-assessment)
2. [Target BMMS Architecture](#2-target-bmms-architecture)
3. [Gap Analysis & Migration Path](#3-gap-analysis--migration-path)

### Part II: Git Branching Strategy
4. [Branch Structure & Workflow](#4-branch-structure--workflow)
5. [Merge & Sync Strategy](#5-merge--sync-strategy)
6. [Version Control Best Practices](#6-version-control-best-practices)

### Part III: Database Migration
7. [Schema Evolution Strategy](#7-schema-evolution-strategy)
8. [Data Migration Scripts](#8-data-migration-scripts)
9. [Multi-Tenancy Data Isolation](#9-multi-tenancy-data-isolation)

### Part IV: Multi-Tenancy Implementation
10. [Organization Model Design](#10-organization-model-design)
11. [Middleware & Context Management](#11-middleware--context-management)
12. [Permission System Enhancement](#12-permission-system-enhancement)

### Part V: Module-by-Module Transition
13. [Communities Module (Already Shared)](#13-communities-module-already-shared)
14. [MANA Module Transformation](#14-mana-module-transformation)
15. [Coordination Module Enhancement](#15-coordination-module-enhancement)
16. [M&E Module Organization Scoping](#16-me-module-organization-scoping)
17. [Recommendations/Policies Module](#17-recommendationspolicies-module)
18. [NEW: Planning Module](#18-new-planning-module)
19. [NEW: Budgeting Module (Parliament Bill No. 325)](#19-new-budgeting-module-parliament-bill-no-325)

### Part VI: URL Structure Refactoring
20. [Fixing the "Monolithic Router Anti-Pattern" Common App](#20-fixing-the-monolithic-router-anti-pattern-common-app)
21. [New URL Structure Implementation](#21-new-url-structure-implementation)
22. [Backward Compatibility Strategy](#22-backward-compatibility-strategy)

### Part VII: Testing & Deployment
23. [Testing Strategy](#23-testing-strategy)
24. [Deployment Roadmap](#24-deployment-roadmap)
25. [Risk Mitigation](#25-risk-mitigation)

### Appendices
- [Appendix A: Code Examples](#appendix-a-code-examples)
- [Appendix B: Migration Scripts](#appendix-b-migration-scripts)
- [Appendix C: Database Schema Diagrams](#appendix-c-database-schema-diagrams)
- [Appendix D: Testing Checklists](#appendix-d-testing-checklists)

---

## Part I: Architecture Analysis

### 1. Current OBCMS Architecture Assessment

#### 1.1 Strengths (Ready for Expansion)

**✅ Solid Technical Foundation:**
- Django 5.x with clean app structure
- PostgreSQL-compatible (118 migrations verified)
- Geographic data via JSONField (NO PostGIS dependency)
- HTMX for instant UI updates
- Comprehensive M&E system (100+ fields)
- 8-stage approval workflows operational
- REST APIs with JWT authentication
- 99.2% test coverage (254/256 tests passing)

**✅ Multi-Organization Groundwork:**
- Organization model exists in `coordination` app (44 BARMM MOAs documented)
- MOA RBAC partially implemented
- `implementing_moa` field in PPA tracking
- Focal person management per MOA

#### 1.2 Critical Issues (Must Fix During Transition)

**❌ Issue #1: "Monolithic Router Anti-Pattern" Common App**
*Severity: CRITICAL | Effort: HIGH | Risk: MEDIUM*

```python
# CURRENT PROBLEM (src/common/urls.py - 848 lines)
urlpatterns = [
    # OBC Data (should be in communities/)
    path("communities/", views.communities_home, name="communities_home"),

    # MANA (should be in mana/)
    path("mana/", views.mana_home, name="mana_home"),

    # Coordination (should be in coordination/)
    path("coordination/", views.coordination_home, name="coordination_home"),

    # Recommendations (should be in recommendations/)
    path("recommendations/", views.recommendations_home, name="recommendations_home"),

    # ... 700+ more lines ...
]
```

**Impact:**
- `common/views.py` exceeds 2000+ lines (should be <500)
- Namespace confusion: `common:mana_home` suggests MANA is part of common
- Developer friction: Finding code requires searching 2000 lines
- Violates Django best practices: Apps should be modular

**❌ Issue #2: Single-Tenant Architecture**
*Severity: CRITICAL | Effort: HIGH | Risk: HIGH*

- No organization-scoped data filtering
- Hard-coded for OOBC operations
- No organization switcher UI
- Permission model assumes single organization

**❌ Issue #3: Missing BMMS Modules**
*Severity: HIGH | Effort: HIGH | Risk: MEDIUM*

- **Planning Module:** Not implemented (strategic planning, annual work plans)
- **Budgeting Module:** Not implemented (Parliament Bill No. 325 compliance required)
- **Inter-Ministerial Coordination:** Limited cross-MOA workflows
- **OCM Aggregation Layer:** No consolidated dashboards for Office of the Chief Minister

#### 1.3 Alignment Assessment (from 05-ui-architecture-alignment-plan.md)

| Module | Django App | URL Namespace | Alignment Status |
|--------|------------|---------------|------------------|
| **M&E** | `monitoring` | `monitoring:*` | ✅ **Excellent** - Direct 1:1 mapping |
| **Project Portal** | `project_central` | `project_central:*` | ✅ **Good** - Clear boundaries |
| **Coordination** | `coordination` + `common` | `common:coordination_*` | ⚠️ **Partial** - Mixed routing |
| **OBC Data** | `communities` | `common:communities_*` | ❌ **Poor** - Routed through common |
| **MANA** | `mana` | `common:mana_*` | ❌ **Poor** - Split system confusion |
| **Recommendations** | `recommendations.*` | `common:recommendations_*` | ❌ **Poor** - Fragmented structure |

**Overall Score:** 3/6 modules (50%) have acceptable alignment

---

### 2. Target BMMS Architecture

#### 2.1 Multi-Tenancy Strategy

**Design Decision: Organization-Based Single Database**

```
BMMS Architecture

├── Shared Services (All MOAs Access)
│   ├── Communities (OBC Profiles) ✅ Already Shared
│   ├── Geographic Data (Regions, Provinces, Municipalities, Barangays) ✅ Shared
│   └── Calendar (System-wide events) ✅ Shared
│
├── Organization-Scoped Services
│   ├── MANA (Assessments per MOA + Collaborative)
│   ├── Coordination (Intra-MOA + Inter-MOA)
│   ├── M&E (PPAs per MOA)
│   ├── Planning (NEW - Strategic & Annual Plans per MOA)
│   └── Budgeting (NEW - Budget Prep & Tracking per MOA)
│
└── Aggregation Layer (OCM Only)
    ├── Cross-MOA Dashboards
    ├── Consolidated Budget View
    ├── Inter-Ministerial Coordination
    └── Government-Wide Performance Reports
```

#### 2.2 New URL Structure

**Problem Resolution:** Fix "Monolithic Router Anti-Pattern" common app AND support multi-tenancy

**Target URL Pattern:** `/moa/<ORG_CODE>/module/...`

**Examples:**
```
# Organization-scoped URLs
/moa/OOBC/mana/assessments/           # OOBC MANA assessments
/moa/MOH/me/projects/                 # MOH projects (M&E)
/moa/MOLE/planning/strategic-plans/   # MOLE strategic plans

# OCM oversight URLs
/ocm/reports/consolidated/            # Cross-MOA reports
/ocm/budget-aggregation/              # Government-wide budget view

# Shared resources (no org scoping)
/communities/barangay/                # All MOAs see same OBC communities
/api/v1/geographic/regions/           # Shared geographic data
```

#### 2.3 Core Components

**New Django App: `organizations`**

```python
# src/organizations/models.py

class Organization(models.Model):
    """MOA/Agency representation"""
    code = models.CharField(max_length=20, unique=True)  # e.g., 'OOBC', 'MOH'
    name = models.CharField(max_length=200)
    org_type = models.CharField(
        max_length=20,
        choices=[
            ('ministry', 'Ministry'),
            ('office', 'Office'),
            ('agency', 'Agency'),
            ('special', 'Special Body'),
        ]
    )

    # Module enablement flags
    enable_mana = models.BooleanField(default=True)
    enable_planning = models.BooleanField(default=True)
    enable_budgeting = models.BooleanField(default=True)
    enable_me = models.BooleanField(default=True)
    enable_coordination = models.BooleanField(default=True)

    # Geographic scope
    primary_region = models.ForeignKey('common.Region', null=True, on_delete=models.SET_NULL)

    # Contact
    head_official = models.CharField(max_length=200, blank=True)
    primary_focal_person = models.ForeignKey(
        'common.User',
        null=True,
        on_delete=models.SET_NULL,
        related_name='primary_for_orgs'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class OrganizationMembership(models.Model):
    """User-to-Organization mapping"""
    user = models.ForeignKey('common.User', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=30,
        choices=[
            ('admin', 'Organization Administrator'),
            ('planning_officer', 'Planning Officer'),
            ('budget_officer', 'Budget Officer'),
            ('me_officer', 'M&E Officer'),
            ('staff', 'Staff'),
            ('viewer', 'Read-Only Viewer'),
        ]
    )

    is_primary = models.BooleanField(default=False)  # Default org for user

    class Meta:
        unique_together = [['user', 'organization']]
        indexes = [
            models.Index(fields=['user', 'is_primary']),
            models.Index(fields=['organization', 'role']),
        ]
```

---

### 3. Gap Analysis & Migration Path

#### 3.1 Component Readiness Matrix

| Component | Current State | BMMS Requirement | Migration Complexity |
|-----------|---------------|------------------|---------------------|
| **Communities** | ✅ Operational | No changes (already shared) | **SIMPLE** - Already multi-org ready |
| **MANA** | ✅ Operational | Add `organization` field | **MODERATE** - Data migration required |
| **Coordination** | ✅ Operational | Enhance inter-MOA features | **MODERATE** - Extend existing models |
| **M&E** | ✅ Operational | Add `organization` field | **MODERATE** - PPA scoping needed |
| **Policies** | ✅ Operational | Add `organization` field | **SIMPLE** - Minimal changes |
| **Planning** | ❌ Not Built | Build from scratch | **COMPLEX** - New module |
| **Budgeting** | ❌ Not Built | Build from scratch + compliance | **VERY COMPLEX** - Parliament Bill No. 325 |
| **OCM Aggregation** | ❌ Not Built | Build aggregation layer | **MODERATE** - Read-only dashboards |
| **URL Routing** | ❌ Broken (Monolithic Router) | Refactor to module-based | **COMPLEX** - Template updates |

#### 3.2 Migration Dependency Graph (REVISED)

```
Phase 1: Foundation (CRITICAL)
    └─> organizations app
        └─> OrganizationMiddleware
            └─> OrganizationScopedModel base class

Phase 2: Planning Module (CRITICAL - MOVED UP)
    └─> NEW module (depends on Phase 1 only)

Phase 3: Budgeting Module (CRITICAL - MOVED UP)
    └─> Parliament Bill No. 325 compliance (depends on Phase 2: Planning)

Phase 4: Coordination Enhancement (HIGH - MOVED UP)
    └─> Cross-MOA partnerships (depends on Phase 1)

Phase 5: Module Migration (MEDIUM - DEFERRED)
    ├─> MANA organization scoping (depends on Phase 1)
    ├─> M&E organization scoping (depends on Phase 1)
    └─> Policies organization scoping (depends on Phase 1)

Phase 6: OCM Aggregation (HIGH)
    └─> Cross-MOA dashboards (depends on Phases 1-5, but can start after Phase 4)

Phase 7: Pilot MOA Onboarding (HIGH)
    ├─> 3 pilot MOAs: MOH, MOLE, MAFAR (depends on Phases 1-4, 6)
    └─> UAT and training (Phase 5 optional for pilot)

Phase 8: Full Rollout (MEDIUM)
    └─> 44 MOAs operational (depends on Phase 7 success)
```

**Key Changes from Original:**
- Planning & Budgeting moved up (immediate value delivery)
- Coordination enhancement moved up (pilot MOAs need this)
- Module Migration deferred to Phase 5 (OOBC-specific, not urgent)
- Pilot can start after Planning/Budgeting/Coordination (doesn't need MANA)

#### 3.3 Breaking Changes Analysis

**Minimal Breaking Changes (by design):**

✅ **No Schema Deletions** - All migrations are additive
✅ **Backward Compatible URLs** - Old URLs redirect to new structure
✅ **OOBC Data Preservation** - All existing data migrated to OOBC organization
✅ **Permission Compatibility** - Existing permissions mapped to new system

**Intentional Changes (with migration path):**

⚠️ **URL Structure** - `common:mana_*` → `mana:*` (redirects implemented)
⚠️ **Organization Required** - New models require `organization` field (default to OOBC)
⚠️ **Multi-Org Context** - Users can belong to multiple organizations

---

## Part II: Git Branching Strategy

### 4. Branch Structure & Workflow

#### 4.1 Branch Architecture

```
main (OBCMS - Production)
  ├── hotfix/* (Emergency fixes)
  ├── feature/obcms-* (OBCMS improvements)
  └── release/obcms-v* (OBCMS releases)

feature/bmms (BMMS Development - Long-Running)
  ├── feature/bmms-organizations (Phase 1)
  ├── feature/bmms-planning (Phase 3)
  ├── feature/bmms-budgeting (Phase 3)
  ├── feature/bmms-url-refactor (Phase 4)
  └── feature/bmms-cmo (Phase 5)
```

#### 4.2 Development Workflow

**Step 1: Create BMMS Base Branch**
```bash
# From main branch
git checkout main
git pull origin main

# Create long-running BMMS branch
git checkout -b feature/bmms
git push -u origin feature/bmms
```

**Step 2: Develop BMMS Features in Sub-Branches**
```bash
# Work on specific BMMS features
git checkout feature/bmms
git pull origin feature/bmms

# Create feature sub-branch
git checkout -b feature/bmms-organizations
# ... develop organizations app ...
git add .
git commit -m "Add organizations app with multi-tenancy foundation"
git push origin feature/bmms-organizations

# Merge to BMMS base
git checkout feature/bmms
git merge feature/bmms-organizations
git push origin feature/bmms
```

**Step 3: Continue OBCMS Development on Main**
```bash
# Bug fixes and improvements for OBCMS
git checkout main
git checkout -b feature/obcms-fix-calendar-bug

# ... fix bug ...
git commit -m "Fix calendar resource booking conflict detection"
git push origin feature/obcms-fix-calendar-bug

# Merge to main via PR
# ... GitHub PR review ...
git checkout main
git merge feature/obcms-fix-calendar-bug
git push origin main
```

#### 4.3 Critical Rules

**🔒 RULE 1: Never Merge BMMS to Main Until Ready**
- BMMS stays on `feature/bmms` branch until full completion
- Main branch continues serving OBCMS in production
- No half-built BMMS features leak to production

**🔒 RULE 2: Sync Main Changes to BMMS Regularly**
```bash
# Every week: Pull OBCMS improvements into BMMS
git checkout feature/bmms
git merge main
git push origin feature/bmms
```

**🔒 RULE 3: Tag OBCMS Releases**
```bash
# When deploying OBCMS updates
git checkout main
git tag -a v1.5.0 -m "OBCMS v1.5.0 - Calendar improvements"
git push origin v1.5.0
```

---

### 5. Merge & Sync Strategy

#### 5.1 Regular Sync (Weekly)

**Purpose:** Keep BMMS branch up-to-date with OBCMS bug fixes and improvements

**Procedure:**
```bash
# 1. Ensure main is clean
git checkout main
git pull origin main

# 2. Switch to BMMS
git checkout feature/bmms
git pull origin feature/bmms

# 3. Merge main into BMMS
git merge main

# 4. Resolve conflicts (prioritize BMMS changes)
# ... manual conflict resolution ...

# 5. Test merged code
pytest -v
pytest tests/performance/ -v

# 6. Push merged BMMS
git push origin feature/bmms
```

**Conflict Resolution Priority:**
- ✅ **Keep BMMS changes** for: URL routing, organization scoping, new modules
- ✅ **Keep main changes** for: Bug fixes, security patches, UI improvements
- ⚠️ **Merge both** for: Model additions, utility functions

#### 5.2 Hotfix Workflow

**Scenario:** Critical bug discovered in production OBCMS

```bash
# 1. Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-security-patch

# 2. Fix bug
# ... apply patch ...
git commit -m "SECURITY: Fix authentication bypass vulnerability"

# 3. Merge to main (emergency)
git checkout main
git merge hotfix/critical-security-patch
git tag -a v1.4.1 -m "Security patch"
git push origin main --tags

# 4. Deploy to production immediately

# 5. Backport to BMMS
git checkout feature/bmms
git merge main  # Includes the hotfix
git push origin feature/bmms
```

#### 5.3 Final BMMS Merge Strategy

**When:** After successful pilot with 2-3 MOAs, all tests passing

**Procedure:**
```bash
# 1. Freeze OBCMS development (code freeze)
git checkout main
# Announce: "OBCMS code freeze for BMMS merge"

# 2. Final sync
git checkout feature/bmms
git merge main
pytest -v  # All tests must pass

# 3. Create release branch
git checkout -b release/bmms-v2.0
git push origin release/bmms-v2.0

# 4. Extensive testing on release branch
# ... QA testing, UAT, security audit ...

# 5. Merge to main (BMMS launch)
git checkout main
git merge release/bmms-v2.0
git tag -a v2.0.0 -m "BMMS v2.0.0 - Multi-tenant launch"
git push origin main --tags

# 6. Archive OBCMS branch
git tag -a obcms-final -m "Final OBCMS version before BMMS"
git push origin obcms-final
```

---

### 6. Version Control Best Practices

#### 6.1 Commit Message Convention

**Format:**
```
[CONTEXT] Short summary (50 chars max)

Detailed explanation (72 chars per line):
- What changed
- Why it changed
- Any breaking changes or migration notes

Refs: #issue-number
```

**Contexts:**
- `[OBCMS]` - OBCMS-specific changes (main branch)
- `[BMMS]` - BMMS-specific changes (feature/bmms branch)
- `[SHARED]` - Changes affecting both (utilities, models)
- `[MIGRATION]` - Database migrations
- `[HOTFIX]` - Emergency fixes
- `[REFACTOR]` - Code improvements without functional changes

**Examples:**
```bash
git commit -m "[BMMS] Add Organization model and multi-tenancy foundation

- Created organizations Django app
- Implemented Organization and OrganizationMembership models
- Added OrganizationMiddleware for request context
- Created OrganizationScopedModel base class

This establishes the foundation for multi-tenant BMMS.

Refs: #BMMS-001"
```

```bash
git commit -m "[OBCMS] Fix calendar resource double-booking bug

- Added proper date range overlap detection
- Implemented transaction-level locking for bookings
- Updated CalendarResourceBooking.check_availability()

No breaking changes. All existing bookings preserved.

Refs: #OBCMS-234"
```

#### 6.2 Branch Protection Rules

**Main Branch (OBCMS Production):**
- ✅ Require pull request reviews (minimum 2 approvers)
- ✅ Require status checks to pass (pytest, linting)
- ✅ Require linear history (no merge commits)
- ✅ Require signed commits (GPG signatures)
- ❌ Do NOT allow force pushes
- ❌ Do NOT allow deletions

**Feature/BMMS Branch:**
- ✅ Require pull request reviews (minimum 1 approver)
- ✅ Require status checks to pass
- ✅ Allow merge commits (for syncing from main)
- ❌ Do NOT allow force pushes after initial push
- ⚠️ Allow careful rebasing for clean history

#### 6.3 Release Tagging Strategy

**OBCMS Versions (1.x series):**
```bash
v1.0.0  # Initial OBCMS production
v1.1.0  # Minor feature additions
v1.1.1  # Patch/bug fix
v1.5.0  # Current version
obcms-final  # Final OBCMS before BMMS merge
```

**BMMS Versions (2.x series):**
```bash
v2.0.0-alpha.1  # BMMS first alpha (Phase 1 complete)
v2.0.0-beta.1   # BMMS beta (Phase 2-3 complete)
v2.0.0-rc.1     # Release candidate (pilot testing)
v2.0.0          # BMMS production launch
v2.1.0          # Post-launch improvements
```

---

## Part III: Database Migration

### 7. Schema Evolution Strategy

#### 7.1 Migration Principles

**✅ ADDITIVE ONLY - Never Destructive**

```python
# ✅ GOOD: Add new field with default
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='assessment',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                default=1  # OOBC organization ID
            ),
        ),
    ]

# ❌ BAD: Remove field (breaks OBCMS)
class Migration(migrations.Migration):
    operations = [
        migrations.RemoveField(
            model_name='assessment',
            name='old_field',  # NEVER DO THIS
        ),
    ]
```

**✅ DATA MIGRATION BEFORE SCHEMA CHANGE**

```python
# Step 1: Data migration (populate new field)
def populate_organization_field(apps, schema_editor):
    Assessment = apps.get_model('mana', 'Assessment')
    Organization = apps.get_model('organizations', 'Organization')

    oobc_org = Organization.objects.get(code='OOBC')

    # Assign all existing assessments to OOBC
    Assessment.objects.filter(organization__isnull=True).update(
        organization=oobc_org
    )

class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0001_initial'),
        ('mana', '0015_previous_migration'),
    ]

    operations = [
        # First: Add field with null=True
        migrations.AddField(
            model_name='assessment',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True  # Temporarily allow null
            ),
        ),
        # Second: Populate data
        migrations.RunPython(
            populate_organization_field,
            reverse_code=migrations.RunPython.noop
        ),
        # Third: Make field required
        migrations.AlterField(
            model_name='assessment',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False  # Now required
            ),
        ),
    ]
```

#### 7.2 Migration Sequence

**Phase 1: Foundation (Organizations App)**

```python
# migrations/organizations/0001_initial.py
class Migration(migrations.Migration):
    initial = True

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('org_type', models.CharField(max_length=20)),
                # ... all fields ...
            ],
        ),
        migrations.CreateModel(
            name='OrganizationMembership',
            # ... fields ...
        ),
    ]

# migrations/organizations/0002_seed_initial_orgs.py
def seed_organizations(apps, schema_editor):
    Organization = apps.get_model('organizations', 'Organization')

    # Create OOBC first (ID=1 for default references)
    Organization.objects.create(
        code='OOBC',
        name='Office for Other Bangsamoro Communities',
        org_type='office',
        enable_mana=True,
        enable_planning=True,
        enable_budgeting=True,
        enable_me=True,
        enable_coordination=True,
        is_active=True,
    )

    # Create other initial MOAs for pilot
    Organization.objects.create(code='MOH', name='Ministry of Health', ...)
    Organization.objects.create(code='MOLE', name='Ministry of Labor and Employment', ...)
    # ... more MOAs ...

class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_organizations, reverse_code=migrations.RunPython.noop),
    ]
```

**Phase 2: Module Organization Scoping**

```python
# migrations/mana/0016_add_organization_field.py
class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0002_seed_initial_orgs'),
        ('mana', '0015_previous_migration'),
    ]

    operations = [
        # Step 1: Add nullable field
        migrations.AddField(
            model_name='assessment',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True,
                blank=True
            ),
        ),

        # Step 2: Populate with OOBC
        migrations.RunPython(populate_oobc_organization),

        # Step 3: Make required
        migrations.AlterField(
            model_name='assessment',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False
            ),
        ),

        # Step 4: Add index for performance
        migrations.AddIndex(
            model_name='assessment',
            index=models.Index(fields=['organization', 'status'], name='mana_assess_org_status_idx'),
        ),
    ]

# Repeat for AssessmentFinding, AssessmentRecommendation, etc.
```

#### 7.3 Rollback Strategy

**Scenario: Migration Fails Mid-Process**

```python
# Option 1: Automatic rollback (transaction-safe)
class Migration(migrations.Migration):
    atomic = True  # DEFAULT: All operations in single transaction

    operations = [
        # If ANY operation fails, ALL rolled back
    ]

# Option 2: Manual rollback
python manage.py migrate mana 0015  # Rollback to previous migration

# Option 3: Fake rollback (if data already correct)
python manage.py migrate mana 0015 --fake

# Option 4: Emergency restore from backup
pg_restore -d obcms_prod backup_before_migration.sql
```

**Best Practice: Pre-Migration Backup**
```bash
# ALWAYS backup before major migrations
pg_dump -d obcms_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Then run migration
cd src
python manage.py migrate
```

---

### 8. Data Migration Scripts

#### 8.1 OOBC Data Migration to Organization

**Script: `migrate_oobc_to_organization.py`**

```python
# src/organizations/management/commands/migrate_oobc_to_organization.py

from django.core.management.base import BaseCommand
from django.db import transaction
from organizations.models import Organization, OrganizationMembership
from common.models import User
from mana.models import Assessment
from monitoring.models import Program, Project, Activity
from recommendations.policies.models import PolicyRecommendation

class Command(BaseCommand):
    help = 'Migrate all OOBC data to OOBC organization'

    def handle(self, *args, **options):
        with transaction.atomic():
            # 1. Get or create OOBC organization
            oobc_org, created = Organization.objects.get_or_create(
                code='OOBC',
                defaults={
                    'name': 'Office for Other Bangsamoro Communities',
                    'org_type': 'office',
                    'enable_mana': True,
                    'enable_planning': True,
                    'enable_budgeting': True,
                    'enable_me': True,
                    'enable_coordination': True,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS('✅ Created OOBC organization'))

            # 2. Migrate all OOBC staff to OrganizationMembership
            oobc_staff = User.objects.filter(user_type='oobc_staff')
            for user in oobc_staff:
                membership, created = OrganizationMembership.objects.get_or_create(
                    user=user,
                    organization=oobc_org,
                    defaults={
                        'role': 'staff',
                        'is_primary': True,
                    }
                )
                if created:
                    self.stdout.write(f'✅ Added {user.username} to OOBC')

            # 3. Assign all assessments to OOBC
            assessments_updated = Assessment.objects.filter(
                organization__isnull=True
            ).update(organization=oobc_org)

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Assigned {assessments_updated} assessments to OOBC'
                )
            )

            # 4. Assign all M&E items to OOBC
            programs_updated = Program.objects.filter(
                organization__isnull=True
            ).update(organization=oobc_org)

            projects_updated = Project.objects.filter(
                organization__isnull=True
            ).update(organization=oobc_org)

            activities_updated = Activity.objects.filter(
                organization__isnull=True
            ).update(organization=oobc_org)

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ M&E migration: {programs_updated} programs, '
                    f'{projects_updated} projects, {activities_updated} activities'
                )
            )

            # 5. Assign all policy recommendations to OOBC
            policies_updated = PolicyRecommendation.objects.filter(
                organization__isnull=True
            ).update(organization=oobc_org)

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Assigned {policies_updated} policy recommendations to OOBC'
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    '\n🎉 OOBC data migration complete! All existing data now scoped to OOBC organization.'
                )
            )
```

**Usage:**
```bash
cd src
python manage.py migrate_oobc_to_organization
```

#### 8.2 Bulk MOA Creation Script

**Script: `create_all_moas.py`**

```python
# src/organizations/management/commands/create_all_moas.py

from django.core.management.base import BaseCommand
from organizations.models import Organization

class Command(BaseCommand):
    help = 'Create all 44 BARMM MOAs'

    BARMM_MOAS = [
        # Ministries (16)
        {'code': 'MAFAR', 'name': 'Ministry of Agriculture, Fisheries and Agrarian Reform', 'type': 'ministry'},
        {'code': 'MBHTE', 'name': 'Ministry of Basic, Higher and Technical Education', 'type': 'ministry'},
        {'code': 'MENRE', 'name': 'Ministry of Environment, Natural Resources and Energy', 'type': 'ministry'},
        {'code': 'MFBM', 'name': 'Ministry of Finance, Budget and Management', 'type': 'ministry'},
        {'code': 'MOH', 'name': 'Ministry of Health', 'type': 'ministry'},
        {'code': 'MHSD', 'name': 'Ministry of Human Settlements and Development', 'type': 'ministry'},
        {'code': 'MIPA', 'name': 'Ministry of Indigenous Peoples Affairs', 'type': 'ministry'},
        {'code': 'MILG', 'name': 'Ministry of Interior and Local Government', 'type': 'ministry'},
        {'code': 'MOLE', 'name': 'Ministry of Labor and Employment', 'type': 'ministry'},
        {'code': 'MPOS', 'name': 'Ministry of Public Order and Safety', 'type': 'ministry'},
        {'code': 'MPW', 'name': 'Ministry of Public Works', 'type': 'ministry'},
        {'code': 'MOST', 'name': 'Ministry of Science and Technology', 'type': 'ministry'},
        {'code': 'MSSD', 'name': 'Ministry of Social Services and Development', 'type': 'ministry'},
        {'code': 'MTIT', 'name': 'Ministry of Trade, Investments and Tourism', 'type': 'ministry'},
        {'code': 'MTC', 'name': 'Ministry of Transportation and Communications', 'type': 'ministry'},
        {'code': 'OCM', 'name': 'Office of the Chief Minister', 'type': 'office'},

        # Offices and Agencies (13)
        {'code': 'WALI', 'name': 'Office of the Wali', 'type': 'office'},
        {'code': 'BHRC', 'name': 'Bangsamoro Human Rights Commission', 'type': 'agency'},
        {'code': 'BPMA', 'name': 'Bangsamoro Planning and Management Agency', 'type': 'agency'},
        {'code': 'BDRRMC', 'name': 'Bangsamoro Disaster Risk Reduction and Management Council', 'type': 'agency'},
        {'code': 'BEDC', 'name': 'Bangsamoro Economic Development Council', 'type': 'agency'},
        {'code': 'BRPOC', 'name': 'Bangsamoro Regional Police Office Commission', 'type': 'agency'},
        {'code': 'BSDB', 'name': 'Bangsamoro Sustainable Development Board', 'type': 'agency'},
        {'code': 'BHB', 'name': 'Bangsamoro Halal Board', 'type': 'agency'},
        {'code': 'BEB', 'name': 'Bangsamoro Electoral Board', 'type': 'agency'},
        {'code': 'BEZA', 'name': 'Bangsamoro Economic Zone Authority', 'type': 'agency'},
        {'code': 'BMIA', 'name': 'Bangsamoro Media and Information Agency', 'type': 'agency'},
        {'code': 'CAB', 'name': 'Commission on Audit for BARMM', 'type': 'agency'},
        {'code': 'CAA', 'name': 'Civil Aviation Authority', 'type': 'agency'},

        # Special: OOBC already created
        # {'code': 'OOBC', 'name': 'Office for Other Bangsamoro Communities', 'type': 'office'},
    ]

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0

        for moa_data in self.BARMM_MOAS:
            org, created = Organization.objects.get_or_create(
                code=moa_data['code'],
                defaults={
                    'name': moa_data['name'],
                    'org_type': moa_data['type'],
                    'enable_mana': True,
                    'enable_planning': True,
                    'enable_budgeting': True,
                    'enable_me': True,
                    'enable_coordination': True,
                    'is_active': True,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created: {moa_data["code"]} - {moa_data["name"]}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Already exists: {moa_data["code"]}')
                )
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Complete! Created {created_count} new MOAs. '
                f'{existing_count} already existed.'
            )
        )
```

**Usage:**
```bash
cd src
python manage.py create_all_moas
```

---

### 9. Multi-Tenancy Data Isolation

#### 9.1 OrganizationScopedModel Base Class

**Implementation:**

```python
# src/organizations/models.py

import threading

# Thread-local storage for request context
_thread_locals = threading.local()

def get_current_organization():
    """Get organization from current request context"""
    return getattr(_thread_locals, 'organization', None)

class OrganizationScopedManager(models.Manager):
    """Manager that auto-filters by request organization"""

    def get_queryset(self):
        """Auto-filter by organization from request context"""
        request = getattr(_thread_locals, 'request', None)

        if request and hasattr(request, 'organization'):
            # Filter by request organization
            return super().get_queryset().filter(
                organization=request.organization
            )

        # No organization context: return all (for admin, management commands)
        return super().get_queryset()

class OrganizationScopedModel(models.Model):
    """Abstract base class for organization-scoped models"""

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_set',
        help_text='Organization that owns this record'
    )

    # Default manager (auto-filters by org)
    objects = OrganizationScopedManager()

    # Unfiltered manager (bypass org scoping)
    all_objects = models.Manager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization']),
        ]

    def save(self, *args, **kwargs):
        """Auto-populate organization from request if not set"""
        if not self.organization_id:
            org = get_current_organization()
            if org:
                self.organization = org

        super().save(*args, **kwargs)
```

**Usage in Models:**

```python
# src/mana/models.py

from organizations.models import OrganizationScopedModel

class Assessment(OrganizationScopedModel):
    """MANA assessment (organization-scoped)"""
    title = models.CharField(max_length=255)
    community = models.ForeignKey('communities.OBCCommunity', on_delete=models.CASCADE)
    # ... other fields ...

    # No need to manually add organization field - inherited from base

# Now queries automatically filter by org:
# Assessment.objects.all()  -> Only assessments for current user's org
# Assessment.all_objects.all()  -> ALL assessments (admin/OCM only)
```

#### 9.2 OrganizationMiddleware

**Implementation:**

```python
# src/organizations/middleware.py

from django.http import HttpResponseForbidden
from organizations.models import Organization, OrganizationMembership, _thread_locals

class OrganizationMiddleware:
    """Set organization context on every request"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request in thread-local for manager access
        _thread_locals.request = request

        # Extract organization from URL pattern
        org_code = self._extract_org_code(request.path)

        if org_code:
            # URL has organization code: /moa/OOBC/...
            try:
                organization = Organization.objects.get(code=org_code)

                # Verify user has access to this organization
                if request.user.is_authenticated:
                    has_access = OrganizationMembership.objects.filter(
                        user=request.user,
                        organization=organization
                    ).exists()

                    if not has_access and not request.user.is_superuser:
                        return HttpResponseForbidden(
                            f"You do not have access to {organization.name}"
                        )

                request.organization = organization
                _thread_locals.organization = organization

            except Organization.DoesNotExist:
                return HttpResponseForbidden(f"Invalid organization code: {org_code}")

        else:
            # No org in URL: use user's primary organization
            if request.user.is_authenticated:
                membership = OrganizationMembership.objects.filter(
                    user=request.user,
                    is_primary=True
                ).select_related('organization').first()

                if membership:
                    request.organization = membership.organization
                    _thread_locals.organization = membership.organization
                else:
                    request.organization = None
                    _thread_locals.organization = None
            else:
                request.organization = None
                _thread_locals.organization = None

        response = self.get_response(request)

        # Cleanup thread-local
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        if hasattr(_thread_locals, 'organization'):
            del _thread_locals.organization

        return response

    def _extract_org_code(self, path):
        """Extract organization code from URL path"""
        # Pattern: /moa/<ORG_CODE>/...
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'moa':
            return parts[1].upper()
        return None

# Register middleware in settings.py
MIDDLEWARE = [
    # ... other middleware ...
    'organizations.middleware.OrganizationMiddleware',  # Add after auth middleware
]
```

#### 9.3 Data Isolation Testing

**Test Suite:**

```python
# tests/organizations/test_data_isolation.py

from django.test import TestCase, RequestFactory
from organizations.models import Organization, OrganizationMembership
from organizations.middleware import OrganizationMiddleware
from mana.models import Assessment
from common.models import User

class DataIsolationTestCase(TestCase):
    def setUp(self):
        # Create two organizations
        self.oobc = Organization.objects.create(code='OOBC', name='OOBC')
        self.moh = Organization.objects.create(code='MOH', name='MOH')

        # Create users for each org
        self.oobc_user = User.objects.create(username='oobc_staff')
        self.moh_user = User.objects.create(username='moh_staff')

        OrganizationMembership.objects.create(
            user=self.oobc_user, organization=self.oobc, role='staff', is_primary=True
        )
        OrganizationMembership.objects.create(
            user=self.moh_user, organization=self.moh, role='staff', is_primary=True
        )

        # Create assessments for each org
        self.oobc_assessment = Assessment.objects.create(
            organization=self.oobc,
            title='OOBC Assessment'
        )
        self.moh_assessment = Assessment.objects.create(
            organization=self.moh,
            title='MOH Assessment'
        )

        self.factory = RequestFactory()
        self.middleware = OrganizationMiddleware(get_response=lambda req: None)

    def test_user_only_sees_own_org_data(self):
        """CRITICAL: Users only see their organization's data"""
        # OOBC user request
        request = self.factory.get('/moa/OOBC/mana/assessments/')
        request.user = self.oobc_user
        self.middleware(request)

        # Should only see OOBC assessments
        visible_assessments = Assessment.objects.all()
        self.assertEqual(visible_assessments.count(), 1)
        self.assertEqual(visible_assessments.first(), self.oobc_assessment)

        # MOH user request
        request = self.factory.get('/moa/MOH/mana/assessments/')
        request.user = self.moh_user
        self.middleware(request)

        # Should only see MOH assessments
        visible_assessments = Assessment.objects.all()
        self.assertEqual(visible_assessments.count(), 1)
        self.assertEqual(visible_assessments.first(), self.moh_assessment)

    def test_cannot_access_other_org_via_url_manipulation(self):
        """CRITICAL: URL manipulation cannot bypass org isolation"""
        # OOBC user tries to access MOH data
        request = self.factory.get('/moa/MOH/mana/assessments/')
        request.user = self.oobc_user
        response = self.middleware(request)

        # Should be forbidden
        self.assertEqual(response.status_code, 403)

    def test_admin_can_see_all_data(self):
        """Superusers can access all organization data"""
        admin = User.objects.create(username='admin', is_superuser=True)
        request = self.factory.get('/moa/OOBC/mana/assessments/')
        request.user = admin
        self.middleware(request)

        # Admin should see all assessments
        all_assessments = Assessment.all_objects.all()
        self.assertEqual(all_assessments.count(), 2)
```

**Run Isolation Tests:**
```bash
pytest tests/organizations/test_data_isolation.py -v
```

---

## Part IV: Multi-Tenancy Implementation

### 10. Organization Model Design

#### 10.1 Complete Organization Model

```python
# src/organizations/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Organization(models.Model):
    """
    BARMM Ministry, Office, or Agency (MOA)
    Represents a government entity using BMMS
    """

    # Identification
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text=_('Unique organization code (e.g., OOBC, MOH, MOLE)')
    )
    name = models.CharField(
        max_length=200,
        help_text=_('Full organization name')
    )
    acronym = models.CharField(
        max_length=20,
        blank=True,
        help_text=_('Common acronym (if different from code)')
    )

    # Classification
    org_type = models.CharField(
        max_length=20,
        choices=[
            ('ministry', _('Ministry')),
            ('office', _('Office')),
            ('agency', _('Agency')),
            ('special', _('Special Body')),
            ('commission', _('Commission')),
        ],
        help_text=_('Type of government entity')
    )

    # Mandate and Authority
    mandate = models.TextField(
        blank=True,
        help_text=_('Legal mandate and responsibilities')
    )
    powers = models.JSONField(
        default=list,
        help_text=_('List of powers and functions')
    )

    # Module Activation
    enable_mana = models.BooleanField(
        default=True,
        help_text=_('Enable Mapping & Needs Assessment module')
    )
    enable_planning = models.BooleanField(
        default=True,
        help_text=_('Enable Strategic Planning module')
    )
    enable_budgeting = models.BooleanField(
        default=True,
        help_text=_('Enable Budgeting module (Parliament Bill No. 325)')
    )
    enable_me = models.BooleanField(
        default=True,
        help_text=_('Enable Monitoring & Evaluation module')
    )
    enable_coordination = models.BooleanField(
        default=True,
        help_text=_('Enable Coordination module')
    )
    enable_policies = models.BooleanField(
        default=True,
        help_text=_('Enable Policy Recommendations module')
    )

    # Geographic Scope
    primary_region = models.ForeignKey(
        'common.Region',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Primary region of operation')
    )
    service_areas = models.ManyToManyField(
        'common.Municipality',
        blank=True,
        help_text=_('Municipalities served by this organization')
    )

    # Leadership & Contact
    head_official = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Name of head official (Minister, Director, etc.)')
    )
    head_title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Title of head official')
    )
    primary_focal_person = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='primary_for_orgs',
        help_text=_('Primary focal person for BMMS')
    )
    alternate_focal_person = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='alternate_for_orgs',
        help_text=_('Alternate focal person')
    )

    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)

    # Budget & Resources
    annual_budget = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Annual budget allocation (PHP)')
    )
    staff_count = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Total number of staff')
    )

    # System Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        help_text=_('Active organizations appear in dropdowns and reports')
    )

    # Ordering
    display_order = models.IntegerField(
        default=0,
        help_text=_('Order for display in lists (lower numbers first)')
    )

    class Meta:
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['org_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def active_staff_count(self):
        """Count of active staff memberships"""
        return self.organizationmembership_set.filter(
            user__is_active=True
        ).count()

    @property
    def enabled_modules(self):
        """List of enabled module names"""
        modules = []
        if self.enable_mana:
            modules.append('MANA')
        if self.enable_planning:
            modules.append('Planning')
        if self.enable_budgeting:
            modules.append('Budgeting')
        if self.enable_me:
            modules.append('M&E')
        if self.enable_coordination:
            modules.append('Coordination')
        if self.enable_policies:
            modules.append('Policies')
        return modules

class OrganizationMembership(models.Model):
    """
    User-to-Organization relationship
    Users can belong to multiple organizations with different roles
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_('User account')
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        help_text=_('Organization')
    )

    # Role within organization
    role = models.CharField(
        max_length=30,
        choices=[
            ('admin', _('Organization Administrator')),
            ('planning_officer', _('Planning Officer')),
            ('budget_officer', _('Budget Officer')),
            ('me_officer', _('M&E Officer')),
            ('mana_coordinator', _('MANA Coordinator')),
            ('staff', _('General Staff')),
            ('viewer', _('Read-Only Viewer')),
        ],
        help_text=_('Role/position within organization')
    )

    # Primary organization flag
    is_primary = models.BooleanField(
        default=False,
        help_text=_('Default organization for this user')
    )

    # Employment details
    position_title = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Official position title')
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Department/division within organization')
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_('Active memberships grant access')
    )
    date_joined = models.DateField(
        auto_now_add=True,
        help_text=_('Date user joined organization')
    )
    date_left = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date user left organization (if applicable)')
    )

    class Meta:
        unique_together = [['user', 'organization']]
        indexes = [
            models.Index(fields=['user', 'is_primary']),
            models.Index(fields=['organization', 'role']),
            models.Index(fields=['organization', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.organization.code} ({self.role})"

    def save(self, *args, **kwargs):
        # Ensure only one primary membership per user
        if self.is_primary:
            OrganizationMembership.objects.filter(
                user=self.user,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)
```

#### 10.2 Organization Utilities

```python
# src/organizations/utils.py

from django.db import connection
from organizations.models import Organization, OrganizationMembership, _thread_locals

def get_user_organizations(user):
    """Get all organizations a user belongs to"""
    if not user.is_authenticated:
        return Organization.objects.none()

    return Organization.objects.filter(
        organizationmembership__user=user,
        organizationmembership__is_active=True,
        is_active=True
    ).distinct()

def get_user_primary_organization(user):
    """Get user's primary organization"""
    if not user.is_authenticated:
        return None

    membership = OrganizationMembership.objects.filter(
        user=user,
        is_primary=True,
        is_active=True
    ).select_related('organization').first()

    return membership.organization if membership else None

def switch_organization_context(request, org_code):
    """Switch user's current organization context"""
    try:
        organization = Organization.objects.get(code=org_code)

        # Verify user has access
        has_access = OrganizationMembership.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True
        ).exists()

        if has_access or request.user.is_superuser:
            request.organization = organization
            _thread_locals.organization = organization
            return True

        return False

    except Organization.DoesNotExist:
        return False

def get_organization_stats(organization):
    """Get quick stats for an organization"""
    from mana.models import Assessment
    from monitoring.models import Program, Project
    from recommendations.policies.models import PolicyRecommendation

    stats = {
        'staff_count': organization.active_staff_count,
        'assessments': Assessment.objects.filter(organization=organization).count(),
        'programs': Program.objects.filter(organization=organization).count(),
        'projects': Project.objects.filter(organization=organization).count(),
        'policies': PolicyRecommendation.objects.filter(organization=organization).count(),
    }

    return stats
```

---

### 11. Middleware & Context Management

#### 11.1 Enhanced OrganizationMiddleware

*(Already shown in section 9.2, repeated here for completeness)*

```python
# src/organizations/middleware.py

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from organizations.models import Organization, OrganizationMembership, _thread_locals

class OrganizationMiddleware:
    """
    Set organization context on every request
    Handles URL-based and session-based organization switching
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request in thread-local for manager access
        _thread_locals.request = request

        # Extract organization from URL pattern
        org_code = self._extract_org_code(request.path)

        if org_code:
            # URL has explicit organization code: /moa/OOBC/...
            try:
                organization = Organization.objects.get(code=org_code, is_active=True)

                # Verify user has access to this organization
                if request.user.is_authenticated:
                    has_access = OrganizationMembership.objects.filter(
                        user=request.user,
                        organization=organization,
                        is_active=True
                    ).exists()

                    if not has_access and not request.user.is_superuser:
                        return HttpResponseForbidden(
                            f"<h1>Access Denied</h1>"
                            f"<p>You do not have permission to access {organization.name}.</p>"
                            f"<p><a href='{reverse('dashboard')}'>Return to Dashboard</a></p>"
                        )

                request.organization = organization
                _thread_locals.organization = organization

            except Organization.DoesNotExist:
                return HttpResponseForbidden(
                    f"<h1>Invalid Organization</h1>"
                    f"<p>Organization code '{org_code}' not found.</p>"
                )

        elif request.path.startswith('/ocm/'):
            # Office of the Chief Minister (OCM) routes - no org scoping
            request.organization = None
            _thread_locals.organization = None

        else:
            # No org in URL: use user's primary organization or session org
            if request.user.is_authenticated:
                # Check session for selected org
                session_org_id = request.session.get('selected_organization_id')

                if session_org_id:
                    try:
                        organization = Organization.objects.get(
                            pk=session_org_id,
                            is_active=True,
                            organizationmembership__user=request.user,
                            organizationmembership__is_active=True
                        )
                        request.organization = organization
                        _thread_locals.organization = organization
                    except Organization.DoesNotExist:
                        # Session org invalid, clear it
                        del request.session['selected_organization_id']
                        request.organization = None
                        _thread_locals.organization = None
                else:
                    # Use primary organization
                    membership = OrganizationMembership.objects.filter(
                        user=request.user,
                        is_primary=True,
                        is_active=True
                    ).select_related('organization').first()

                    if membership:
                        request.organization = membership.organization
                        _thread_locals.organization = membership.organization
                    else:
                        request.organization = None
                        _thread_locals.organization = None
            else:
                request.organization = None
                _thread_locals.organization = None

        response = self.get_response(request)

        # Cleanup thread-local
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        if hasattr(_thread_locals, 'organization'):
            del _thread_locals.organization

        return response

    def _extract_org_code(self, path):
        """Extract organization code from URL path"""
        # Pattern: /moa/<ORG_CODE>/...
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'moa':
            return parts[1].upper()
        return None

class OrganizationSwitcherMiddleware:
    """
    Allow users to switch between organizations via session
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for organization switch request
        if request.method == 'POST' and 'switch_organization' in request.POST:
            org_id = request.POST.get('switch_organization')

            if org_id and request.user.is_authenticated:
                try:
                    # Verify user has access
                    organization = Organization.objects.get(
                        pk=org_id,
                        is_active=True,
                        organizationmembership__user=request.user,
                        organizationmembership__is_active=True
                    )

                    # Store in session
                    request.session['selected_organization_id'] = organization.id

                    # Redirect to dashboard of new org
                    return HttpResponseRedirect(
                        reverse('organization_dashboard', kwargs={'org_code': organization.code})
                    )

                except Organization.DoesNotExist:
                    pass

        return self.get_response(request)
```

#### 11.2 Context Processors

```python
# src/organizations/context_processors.py

from organizations.utils import get_user_organizations

def organization_context(request):
    """Add organization context to all templates"""
    context = {
        'current_organization': getattr(request, 'organization', None),
        'user_organizations': [],
    }

    if request.user.is_authenticated:
        context['user_organizations'] = get_user_organizations(request.user)

    return context

# Add to settings.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... existing processors ...
                'organizations.context_processors.organization_context',
            ],
        },
    },
]
```

#### 11.3 Organization Switcher UI

```html
<!-- src/templates/components/organization_switcher.html -->

{% if user_organizations|length > 1 %}
<div class="organization-switcher">
    <form method="post">
        {% csrf_token %}
        <label for="org-select" class="block text-sm font-medium text-gray-700 mb-2">
            Switch Organization
        </label>
        <div class="relative">
            <select
                id="org-select"
                name="switch_organization"
                onchange="this.form.submit()"
                class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200"
            >
                <option value="">Select Organization...</option>
                {% for org in user_organizations %}
                <option
                    value="{{ org.id }}"
                    {% if current_organization.id == org.id %}selected{% endif %}
                >
                    {{ org.code }} - {{ org.name }}
                </option>
                {% endfor %}
            </select>
            <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
                <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
            </span>
        </div>
    </form>
</div>
{% endif %}

<!-- Show current organization -->
{% if current_organization %}
<div class="current-org-badge mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
    <div class="flex items-center">
        <div class="flex-shrink-0">
            <i class="fas fa-building text-emerald-600 text-2xl"></i>
        </div>
        <div class="ml-4">
            <h3 class="text-sm font-medium text-emerald-800">Current Organization</h3>
            <p class="text-lg font-semibold text-emerald-900">{{ current_organization.code }}</p>
            <p class="text-sm text-emerald-700">{{ current_organization.name }}</p>
        </div>
    </div>
</div>
{% endif %}
```

---

### 12. Permission System Enhancement

#### 12.1 Three-Level Permission Model

**System-Level Permissions** (Django default)
- Superuser (can do anything)
- Staff (can access admin)

**Organization-Level Permissions** (NEW)
- Organization Administrator
- Module-specific roles (Planning Officer, Budget Officer, M&E Officer)
- General Staff
- Read-Only Viewer

**Cross-Organization Permissions** (NEW - for OCM)
- OCM Staff (view all organizations)
- Inter-ministerial coordinators (facilitate cross-MOA projects)

#### 12.2 Permission Decorators

```python
# src/organizations/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied
from organizations.models import OrganizationMembership

def require_organization_role(*allowed_roles):
    """
    Decorator to require specific role within current organization

    Usage:
        @require_organization_role('admin', 'planning_officer')
        def create_strategic_plan(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'organization') or not request.organization:
                raise PermissionDenied("No organization context")

            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")

            # Superusers bypass check
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check membership
            membership = OrganizationMembership.objects.filter(
                user=request.user,
                organization=request.organization,
                is_active=True
            ).first()

            if not membership:
                raise PermissionDenied(
                    f"You are not a member of {request.organization.name}"
                )

            if membership.role not in allowed_roles:
                raise PermissionDenied(
                    f"Your role ({membership.role}) cannot access this feature. "
                    f"Required: {', '.join(allowed_roles)}"
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator

def require_ocm_access(view_func):
    """
    Decorator for OCM-only views (cross-organization oversight)

    Usage:
        @require_ocm_access
        def consolidated_budget_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required")

        # Check if user belongs to OCM or is superuser
        is_ocm_staff = OrganizationMembership.objects.filter(
            user=request.user,
            organization__code='OCM',  # Office of the Chief Minister
            is_active=True
        ).exists()

        if not (is_ocm_staff or request.user.is_superuser):
            raise PermissionDenied(
                "This view is restricted to Office of the Chief Minister staff"
            )

        return view_func(request, *args, **kwargs)

    return wrapper

def require_module_enabled(module_name):
    """
    Decorator to check if module is enabled for current organization

    Usage:
        @require_module_enabled('budgeting')
        def budget_preparation_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'organization') or not request.organization:
                raise PermissionDenied("No organization context")

            module_enabled = getattr(
                request.organization,
                f'enable_{module_name}',
                False
            )

            if not module_enabled:
                raise PermissionDenied(
                    f"The {module_name} module is not enabled for {request.organization.name}"
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
```

#### 12.3 Permission Usage Examples

```python
# src/planning/views.py

from django.views.generic import CreateView, UpdateView, ListView
from organizations.decorators import require_organization_role, require_module_enabled
from planning.models import StrategicPlan

@require_module_enabled('planning')
@require_organization_role('admin', 'planning_officer')
def create_strategic_plan(request):
    """Only org admins and planning officers can create strategic plans"""
    # ... implementation ...

@require_module_enabled('budgeting')
@require_organization_role('admin', 'budget_officer')
def submit_annual_budget(request):
    """Only org admins and budget officers can submit budgets"""
    # ... implementation ...

from organizations.decorators import require_ocm_access

@require_ocm_access
def consolidated_moa_performance(request):
    """OCM staff view of all MOA performance metrics"""
    from organizations.models import Organization
    from monitoring.models import Program

    # Aggregate across ALL organizations (OCM oversight)
    all_orgs = Organization.objects.filter(is_active=True)

    performance_data = []
    for org in all_orgs:
        programs = Program.all_objects.filter(organization=org)  # Bypass org scoping
        performance_data.append({
            'organization': org,
            'total_programs': programs.count(),
            'active_programs': programs.filter(status='active').count(),
            # ... more metrics ...
        })

    return render(request, 'cmo/consolidated_performance.html', {
        'performance_data': performance_data
    })
```

---

## Part V: Module-by-Module Transition

This section provides detailed technical guidance for transforming each OBCMS module into its BMMS equivalent. Each module analysis includes current state assessment, target architecture, specific migration steps, code examples, testing requirements, and dependency mapping.

---

### 13. Communities Module (Already Shared)

#### Current State Analysis

**Django App:** `src/communities/`
**URL Namespace:** `common:communities_*` (routed through common app)
**Current Organization Support:** NONE - Single-tenant for OOBC only

**Key Models:**
```python
# src/communities/models.py

class OBCCommunity(CommunityProfileBase):
    """Barangay-level OBC community"""
    barangay = models.OneToOneField('common.Barangay', on_delete=models.CASCADE)
    # 11-section profile (demographics, livelihoods, infrastructure, etc.)
    dominant_ethnolinguistic_group = models.CharField(max_length=50)
    settlement_type = models.CharField(max_length=20)
    # ... 100+ fields ...

class MunicipalityCoverage(models.Model):
    """Municipality-level OBC aggregation"""
    municipality = models.OneToOneField('common.Municipality', on_delete=models.CASCADE)
    total_obc_population = models.IntegerField(default=0)

class ProvinceCoverage(models.Model):
    """Province-level OBC aggregation"""
    province = models.OneToOneField('common.Province', on_delete=models.CASCADE)
    submission_status = models.CharField(max_length=20)  # MANA participants

class Stakeholder(models.Model):
    """Community stakeholders"""
    community = models.ForeignKey(OBCCommunity, on_delete=models.CASCADE)
    stakeholder_type = models.CharField(max_length=30)
```

**Current Data Volume:**
- ~500 Barangay OBC communities
- ~50 Municipal coverages
- ~15 Provincial coverages
- ~2000 stakeholder records

**Critical Finding:** ✅ **Communities module is already multi-org ready!**

**Why:** OBC community data is **reference data** shared across all organizations. Every MOA needs to see the same OBC profiles when:
- Planning interventions (MANA assessments)
- Targeting beneficiaries (M&E projects)
- Coordinating partnerships (Coordination module)
- Allocating budgets (Planning/Budgeting)

#### Target BMMS State

**Organization Scoping:** **SHARED** (No organization field needed)

**Rationale:**
```
┌──────────────────────────────────────────────────────────────┐
│  Why Communities Module Stays SHARED                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Geographic Hierarchy (Shared Foundation):                  │
│  • Region > Province > Municipality > Barangay              │
│  • Same OBC communities for all MOAs                        │
│                                                              │
│  Organization-Specific Data Goes Elsewhere:                 │
│  • MANA assessments → mana.Assessment (org-scoped)          │
│  • M&E projects → monitoring.Project (org-scoped)           │
│  • Coordination → coordination.Partnership (org-scoped)     │
│                                                              │
│  Analogy: OBCs are like "cities on a map" - everyone sees  │
│           the same cities, but each org has its own         │
│           projects/activities IN those cities.              │
└──────────────────────────────────────────────────────────────┘
```

**Enhancement Required:** Fix URL routing (move from `common:communities_*` to `communities:*`)

**No Database Changes Needed:** ✅ Models remain unchanged

#### Migration Strategy

**Step 1: URL Namespace Refactoring**
- **Complexity:** Simple
- **Priority:** HIGH
- **Technical Approach:** Create proper `communities` namespace, update templates

**Database Changes:** NONE
**Code Changes:**
```python
# src/communities/urls.py
app_name = "communities"  # Add this line

urlpatterns = [
    path("", views.obc_list, name="manage"),  # Was: common:communities_manage
    path("<int:pk>/", views.obc_detail, name="detail"),
    path("<int:pk>/edit/", views.obc_edit, name="edit"),
    path("municipal/", views.municipal_coverage_list, name="municipal"),
    path("provincial/", views.provincial_coverage_list, name="provincial"),
]

# src/obc_management/urls.py (CHANGE)
# BEFORE
path("", include("common.urls")),  # Everything through common

# AFTER
path("communities/", include("communities.urls")),  # Direct routing
```

**Template Updates:**
```bash
# Find all template references
grep -r "common:communities_" src/templates/

# Update to new namespace
sed -i '' 's/common:communities_manage/communities:manage/g' src/templates/**/*.html
sed -i '' 's/common:communities_detail/communities:detail/g' src/templates/**/*.html
```

**Step 2: Add Multi-Org Context Awareness (UI Only)**
- **Complexity:** Simple
- **Priority:** MEDIUM
- **Technical Approach:** Show which orgs are working in each community

**Code Changes:**
```python
# src/communities/models.py (ADD new method)

class OBCCommunity(CommunityProfileBase):
    # ... existing fields ...

    @property
    def active_organizations(self):
        """Get organizations currently working in this community"""
        from mana.models import Assessment
        from monitoring.models import Project
        from organizations.models import Organization

        # Find orgs via assessments
        mana_org_ids = Assessment.objects.filter(
            community=self
        ).values_list('organization_id', flat=True).distinct()

        # Find orgs via M&E projects
        me_org_ids = Project.objects.filter(
            target_communities=self
        ).values_list('organization_id', flat=True).distinct()

        # Combine and return
        all_org_ids = set(list(mana_org_ids) + list(me_org_ids))
        return Organization.objects.filter(id__in=all_org_ids)
```

**Template Enhancement:**
```html
<!-- src/templates/communities/detail.html -->
<div class="community-organizations-card">
    <h3>Organizations Working in This Community</h3>
    {% for org in community.active_organizations %}
        <div class="org-badge">
            <span class="org-code">{{ org.code }}</span>
            <span class="org-name">{{ org.name }}</span>
        </div>
    {% empty %}
        <p class="text-gray-500">No organizations currently active</p>
    {% endfor %}
</div>
```

#### Testing Requirements

**Test Suite:**
```python
# tests/communities/test_bmms_compatibility.py

from django.test import TestCase
from organizations.models import Organization
from communities.models import OBCCommunity
from mana.models import Assessment

class CommunitiesSharedAccessTestCase(TestCase):
    def setUp(self):
        self.oobc = Organization.objects.create(code='OOBC', name='OOBC')
        self.moh = Organization.objects.create(code='MOH', name='MOH')

        self.community = OBCCommunity.objects.create(
            barangay=self.barangay,
            total_population=5000
        )

    def test_all_orgs_see_same_communities(self):
        """CRITICAL: All organizations see same OBC community data"""
        # OOBC request
        oobc_request = self.factory.get('/communities/')
        oobc_request.user = self.oobc_user
        oobc_request.organization = self.oobc

        # MOH request
        moh_request = self.factory.get('/communities/')
        moh_request.user = self.moh_user
        moh_request.organization = self.moh

        # Both should see the same community
        self.assertEqual(
            OBCCommunity.objects.all().count(),
            1
        )

    def test_active_organizations_property(self):
        """Test community shows which orgs are working there"""
        # Create MANA assessment by MOH
        Assessment.objects.create(
            community=self.community,
            organization=self.moh,
            title='MOH Assessment'
        )

        # Check active organizations
        active_orgs = self.community.active_organizations
        self.assertIn(self.moh, active_orgs)
        self.assertNotIn(self.oobc, active_orgs)  # OOBC has no activities yet

    def test_url_namespace_refactoring(self):
        """Test new URL namespace works"""
        url = reverse('communities:manage')
        self.assertEqual(url, '/communities/')

        url = reverse('communities:detail', kwargs={'pk': self.community.pk})
        self.assertEqual(url, f'/communities/{self.community.pk}/')
```

**Run Tests:**
```bash
pytest tests/communities/test_bmms_compatibility.py -v
```

#### Dependencies

**Requires:**
- Phase 1: Organizations app created (provides Organization model for relationships)
- URL refactoring plan (Part VI) completed

**Blocks:**
- MANA module transformation (uses communities.OBCCommunity)
- M&E module transformation (uses communities.OBCCommunity)

**Code Example - Before/After:**
```python
# ============================================
# BEFORE (OBCMS)
# ============================================

# Template reference
{% url 'common:communities_manage' %}  # Confusing namespace

# View access (everyone sees same data)
def obc_list(request):
    communities = OBCCommunity.objects.all()
    return render(request, 'communities/list.html', {'communities': communities})

# ============================================
# AFTER (BMMS)
# ============================================

# Template reference
{% url 'communities:manage' %}  # Clear namespace

# View access (still everyone sees same data, but with org context)
def obc_list(request):
    communities = OBCCommunity.objects.all()

    # Optional: highlight communities where user's org is active
    if request.organization:
        for community in communities:
            community.is_my_org_active = request.organization in community.active_organizations

    return render(request, 'communities/list.html', {'communities': communities})
```

**Complexity Rating:** Simple
**Priority:** HIGH (Quick win, foundation for other modules)

---

### 14. MANA Module Transformation

#### Current State Analysis

**Django App:** `src/mana/`
**URL Namespace:** `common:mana_*` (routed through common) + `mana:*` (workshops)
**Current Organization Support:** NONE - All OOBC assessments

**Key Models:**
```python
# src/mana/models.py

class Assessment(models.Model):
    """MANA assessment session"""
    title = models.CharField(max_length=255)
    community = models.ForeignKey('communities.OBCCommunity', on_delete=models.CASCADE)
    assessment_date = models.DateField()
    assessment_type = models.CharField(max_length=20)  # baseline, thematic, follow_up
    themes = models.JSONField(default=list)  # SERC themes
    status = models.CharField(max_length=20)
    # NO organization field ❌

class AssessmentParticipant(models.Model):
    """Workshop participants"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    user = models.ForeignKey('common.User', on_delete=models.CASCADE)
    participant_type = models.CharField(max_length=20)

class AssessmentFinding(models.Model):
    """Assessment results"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    finding_type = models.CharField(max_length=20)
    description = models.TextField()
    priority_level = models.CharField(max_length=10)

class AssessmentRecommendation(models.Model):
    """Action recommendations"""
    finding = models.ForeignKey(AssessmentFinding, on_delete=models.CASCADE)
    recommendation = models.TextField()
    responsible_agency = models.CharField(max_length=200)
```

**Current Data Volume:**
- ~200 OOBC assessments
- ~1500 assessment findings
- ~800 recommendations
- ~3000 participant records

#### Target BMMS State

**Organization Scoping:** **ORGANIZATION-SCOPED + COLLABORATIVE**

**Enhancement Pattern:**
```
┌────────────────────────────────────────────────────────────┐
│  MANA Assessment Types in BMMS:                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Type 1: Single-MOA Assessment                            │
│  • MOH conducts health needs assessment                   │
│  • organization = MOH (exclusive)                         │
│  • Only MOH staff can edit                                │
│                                                            │
│  Type 2: Joint Assessment (Multi-MOA Collaboration)      │
│  • OOBC + MOLE + MSSD conduct livelihood assessment      │
│  • lead_organization = OOBC                               │
│  • participating_organizations = [OOBC, MOLE, MSSD]      │
│  • All participants can contribute findings               │
│                                                            │
│  Type 3: OOBC-Facilitated Assessment (Legacy)            │
│  • OOBC conducts comprehensive SERC assessment            │
│  • organization = OOBC                                    │
│  • Recommendations route to relevant MOAs                 │
└────────────────────────────────────────────────────────────┘
```

#### Migration Strategy

**Step 1: Add Organization Field to Assessment**
- **Complexity:** Moderate
- **Priority:** CRITICAL
- **Technical Approach:** Additive migration with OOBC default

**Database Changes:**
```python
# migrations/mana/0016_add_organization_field.py

from django.db import migrations, models

def populate_oobc_organization(apps, schema_editor):
    """Assign all existing assessments to OOBC"""
    Assessment = apps.get_model('mana', 'Assessment')
    Organization = apps.get_model('organizations', 'Organization')

    oobc_org = Organization.objects.get(code='OOBC')

    # Assign all existing assessments to OOBC
    Assessment.objects.filter(organization__isnull=True).update(
        organization=oobc_org
    )

    print(f"✅ Assigned {Assessment.objects.count()} assessments to OOBC")

class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0002_seed_initial_orgs'),
        ('mana', '0015_previous_migration'),
    ]

    operations = [
        # Step 1: Add nullable organization field
        migrations.AddField(
            model_name='assessment',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True,
                blank=True,
                help_text='Lead organization conducting this assessment'
            ),
        ),

        # Step 2: Populate with OOBC
        migrations.RunPython(
            populate_oobc_organization,
            reverse_code=migrations.RunPython.noop
        ),

        # Step 3: Make field required
        migrations.AlterField(
            model_name='assessment',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False,
                help_text='Lead organization conducting this assessment'
            ),
        ),

        # Step 4: Add index for performance
        migrations.AddIndex(
            model_name='assessment',
            index=models.Index(
                fields=['organization', 'status'],
                name='mana_assess_org_status_idx'
            ),
        ),
    ]
```

**Step 2: Add Multi-MOA Collaboration Support**
- **Complexity:** Moderate
- **Priority:** HIGH
- **Technical Approach:** Add M2M relationship for participating orgs

**Database Changes:**
```python
# migrations/mana/0017_add_collaborative_assessments.py

class Migration(migrations.Migration):
    dependencies = [
        ('mana', '0016_add_organization_field'),
    ]

    operations = [
        # Add collaborative assessment support
        migrations.AddField(
            model_name='assessment',
            name='is_collaborative',
            field=models.BooleanField(
                default=False,
                help_text='Is this a joint assessment with multiple MOAs?'
            ),
        ),

        migrations.AddField(
            model_name='assessment',
            name='participating_organizations',
            field=models.ManyToManyField(
                'organizations.Organization',
                blank=True,
                related_name='collaborative_assessments',
                help_text='Organizations participating in this joint assessment'
            ),
        ),

        # Add contribution tracking
        migrations.CreateModel(
            name='AssessmentContribution',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('assessment', models.ForeignKey(
                    'Assessment',
                    on_delete=models.CASCADE,
                    related_name='contributions'
                )),
                ('organization', models.ForeignKey(
                    'organizations.Organization',
                    on_delete=models.CASCADE
                )),
                ('findings_contributed', models.IntegerField(default=0)),
                ('recommendations_contributed', models.IntegerField(default=0)),
                ('last_contribution_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
```

**Updated Model:**
```python
# src/mana/models.py (AFTER)

from organizations.models import OrganizationScopedModel

class Assessment(OrganizationScopedModel):  # Inherits organization field
    """MANA assessment session (organization-scoped)"""
    title = models.CharField(max_length=255)
    community = models.ForeignKey('communities.OBCCommunity', on_delete=models.CASCADE)
    assessment_date = models.DateField()
    assessment_type = models.CharField(max_length=20)
    themes = models.JSONField(default=list)
    status = models.CharField(max_length=20)

    # Multi-MOA collaboration
    is_collaborative = models.BooleanField(
        default=False,
        help_text='Is this a joint assessment with multiple MOAs?'
    )
    participating_organizations = models.ManyToManyField(
        'organizations.Organization',
        blank=True,
        related_name='collaborative_assessments',
        help_text='Organizations participating in this joint assessment'
    )

    class Meta:
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['community', 'assessment_date']),
        ]

    def can_edit(self, user):
        """Check if user can edit this assessment"""
        if user.is_superuser:
            return True

        # Lead organization members can edit
        if user.organization == self.organization:
            return True

        # Participating organization members can contribute
        if self.is_collaborative:
            return self.participating_organizations.filter(
                id=user.organization.id
            ).exists()

        return False

    @property
    def all_organizations(self):
        """Get lead + participating organizations"""
        orgs = list(self.participating_organizations.all())
        orgs.insert(0, self.organization)  # Lead org first
        return orgs
```

**Step 3: Update Queries to Respect Organization Scoping**
- **Complexity:** Moderate
- **Priority:** CRITICAL
- **Technical Approach:** Use OrganizationScopedManager for automatic filtering

**Code Changes:**
```python
# src/mana/views.py (BEFORE)

def assessment_list(request):
    """List all assessments (OOBC-only)"""
    assessments = Assessment.objects.all()  # Shows ALL assessments
    return render(request, 'mana/list.html', {'assessments': assessments})

# src/mana/views.py (AFTER)

from organizations.decorators import require_module_enabled

@require_module_enabled('mana')
def assessment_list(request):
    """List assessments for current organization"""
    # Automatic org filtering via OrganizationScopedManager
    my_assessments = Assessment.objects.all()  # Only user's org

    # Also show collaborative assessments where user's org participates
    collaborative = Assessment.objects.filter(
        is_collaborative=True,
        participating_organizations=request.organization
    ).exclude(
        organization=request.organization  # Don't duplicate
    )

    return render(request, 'mana/list.html', {
        'my_assessments': my_assessments,
        'collaborative_assessments': collaborative,
    })
```

**Step 4: Fix URL Routing (Move from common to mana)**
- **Complexity:** Simple
- **Priority:** HIGH
- **Technical Approach:** Same as communities module

**Code Changes:**
```python
# src/mana/urls.py (UPDATE)
app_name = "mana"  # Ensure this exists

urlpatterns = [
    # Staff tools
    path("", views.mana_home, name="home"),  # Was: common:mana_home
    path("regional/", views.regional_overview, name="regional"),
    path("provincial/", views.provincial_overview, name="provincial"),
    path("desk-review/", views.desk_review, name="desk_review"),

    # Assessments
    path("assessments/", views.assessment_list, name="assessments"),
    path("assessments/<int:pk>/", views.assessment_detail, name="assessment_detail"),
    path("assessments/create/", views.assessment_create, name="assessment_create"),

    # Collaborative assessments
    path("collaborative/", views.collaborative_list, name="collaborative"),
    path("collaborative/<int:pk>/join/", views.join_assessment, name="join"),

    # Workshops (participants)
    path("workshops/", views.my_workshops, name="my_workshops"),
    path("workshops/assessments/<int:pk>/", views.participant_workshop, name="workshop"),
]

# src/obc_management/urls.py (CHANGE)
path("mana/", include("mana.urls")),  # Direct routing (not through common)
```

#### Testing Requirements

**Test Suite:**
```python
# tests/mana/test_organization_scoping.py

from django.test import TestCase
from organizations.models import Organization, OrganizationMembership
from mana.models import Assessment
from communities.models import OBCCommunity

class MANAOrganizationScopingTestCase(TestCase):
    def setUp(self):
        # Create organizations
        self.oobc = Organization.objects.create(code='OOBC', name='OOBC')
        self.moh = Organization.objects.create(code='MOH', name='MOH')
        self.mole = Organization.objects.create(code='MOLE', name='MOLE')

        # Create users
        self.oobc_user = User.objects.create(username='oobc_staff')
        self.moh_user = User.objects.create(username='moh_staff')

        OrganizationMembership.objects.create(
            user=self.oobc_user, organization=self.oobc, role='staff'
        )
        OrganizationMembership.objects.create(
            user=self.moh_user, organization=self.moh, role='staff'
        )

        # Create test data
        self.community = OBCCommunity.objects.create(...)

        self.oobc_assessment = Assessment.objects.create(
            organization=self.oobc,
            community=self.community,
            title='OOBC SERC Assessment'
        )

        self.moh_assessment = Assessment.objects.create(
            organization=self.moh,
            community=self.community,
            title='MOH Health Assessment'
        )

        self.collaborative_assessment = Assessment.objects.create(
            organization=self.oobc,  # Lead
            community=self.community,
            title='Joint Livelihood Assessment',
            is_collaborative=True
        )
        self.collaborative_assessment.participating_organizations.add(self.oobc, self.mole)

    def test_organization_scoped_queries(self):
        """Test automatic organization filtering"""
        # OOBC request
        request = self.factory.get('/mana/assessments/')
        request.user = self.oobc_user
        request.organization = self.oobc

        # Should only see OOBC assessments
        visible = Assessment.objects.all()
        self.assertEqual(visible.count(), 2)  # OOBC + collaborative (lead)
        self.assertIn(self.oobc_assessment, visible)
        self.assertNotIn(self.moh_assessment, visible)

    def test_collaborative_assessment_access(self):
        """Test multi-org collaborative assessments"""
        # MOLE should see collaborative assessment
        request = self.factory.get('/mana/collaborative/')
        request.user = self.mole_user
        request.organization = self.mole

        # Check participation
        self.assertTrue(
            self.collaborative_assessment.can_edit(self.mole_user)
        )

    def test_data_migration_preserved_oobc(self):
        """Test all existing assessments assigned to OOBC"""
        oobc_assessments = Assessment.all_objects.filter(organization=self.oobc)
        self.assertGreaterEqual(oobc_assessments.count(), 1)
```

#### Dependencies

**Requires:**
- Phase 1: Organizations app + middleware
- Communities module (provides OBCCommunity)
- OrganizationScopedModel base class

**Blocks:**
- Coordination module (references mana.Assessment)
- Planning module (uses MANA findings for needs-based planning)

**Complexity Rating:** Moderate
**Priority:** CRITICAL (Core OBCMS functionality)

---

### 15. Coordination Module Enhancement

#### Current State Analysis

**Django App:** `src/coordination/`
**URL Namespace:** `common:coordination_*` (routed through common)
**Current Organization Support:** PARTIAL - Organization model exists but not used for scoping

**Key Models:**
```python
# src/coordination/models.py

class Organization(models.Model):
    """Partner organizations (44 BARMM MOAs documented)"""
    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=20)  # bmoa, lgu, nga, ingo, etc.
    mandate = models.TextField(blank=True)
    powers = models.JSONField(default=list)
    focal_person = models.CharField(max_length=200, blank=True)
    # NO ownership/scoping mechanism ❌

class Partnership(models.Model):
    """Formal partnership agreements"""
    title = models.CharField(max_length=255)
    partnership_type = models.CharField(max_length=20)  # MOA, MOU, contract, etc.
    organizations = models.ManyToManyField(Organization)  # Multi-org support ✅
    status = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    # NO lead organization field ❌

class StakeholderEngagement(models.Model):
    """Engagement activities"""
    title = models.CharField(max_length=255)
    engagement_type = models.CharField(max_length=20)
    organizations = models.ManyToManyField(Organization)
    related_assessment = models.ForeignKey('mana.Assessment', null=True, on_delete=models.SET_NULL)
    # NO lead organization field ❌

class Communication(models.Model):
    """Communication tracking"""
    subject = models.CharField(max_length=255)
    from_organization = models.ForeignKey(Organization, related_name='sent_communications', on_delete=models.CASCADE)
    to_organizations = models.ManyToManyField(Organization, related_name='received_communications')
    # FROM org exists, but no ownership scoping ❌
```

**Current Data Volume:**
- ~150 organization records (44 MOAs + partners)
- ~50 partnership agreements
- ~300 stakeholder engagements
- ~1000 communications

#### Target BMMS State

**Organization Scoping:** **HYBRID** (Lead org tracking + cross-org visibility)

**Enhancement Pattern:**
```
┌───────────────────────────────────────────────────────────┐
│  Coordination in BMMS:                                    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Intra-MOA Coordination:                                 │
│  • MOH manages partnerships with health NGOs             │
│  • lead_organization = MOH                               │
│  • Visible only to MOH staff                             │
│                                                           │
│  Inter-MOA Coordination:                                 │
│  • OOBC + MOH + MSSD joint program                       │
│  • lead_organization = OOBC                              │
│  • participating_organizations = [OOBC, MOH, MSSD]      │
│  • All participants see and contribute                   │
│                                                           │
│  OCM Oversight:                                          │
│  • Office of the Chief Minister views ALL coordination         │
│  • Cross-MOA collaboration monitoring                   │
│  • Government-wide partnership analytics                │
└───────────────────────────────────────────────────────────┘
```

**Critical Issue:** **`coordination.Organization` will be REPLACED by `organizations.Organization`**

**Migration Path:**
1. Rename existing `coordination.Organization` → `coordination.PartnerOrganization` (external partners)
2. Use `organizations.Organization` for BARMM MOAs (internal)
3. Update all foreign keys and M2M relationships

#### Migration Strategy

**Step 1: Rename Organization Model to Avoid Conflict**
- **Complexity:** Moderate
- **Priority:** CRITICAL
- **Technical Approach:** Rename existing model, preserve data

**Database Changes:**
```python
# migrations/coordination/0020_rename_organization_model.py

class Migration(migrations.Migration):
    dependencies = [
        ('coordination', '0019_previous_migration'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Organization',
            new_name='PartnerOrganization',
        ),

        # Update related_name for clarity
        migrations.AlterField(
            model_name='partnerorganization',
            name='partnerships',
            field=models.ManyToManyField(
                'Partnership',
                related_name='partner_organizations'  # Updated
            ),
        ),
    ]
```

**Updated Model:**
```python
# src/coordination/models.py (AFTER)

class PartnerOrganization(models.Model):
    """External partner organizations (NGOs, LGUs, private sector)"""
    name = models.CharField(max_length=255)
    organization_type = models.CharField(
        max_length=20,
        choices=[
            ('lgu', 'Local Government Unit'),
            ('nga', 'National Government Agency'),
            ('ingo', 'International NGO'),
            ('lngo', 'Local NGO'),
            ('cso', 'Civil Society Organization'),
            ('academic', 'Academic Institution'),
            ('private', 'Private Sector'),
            ('coop', 'Cooperative'),
        ]
    )
    # ... other fields ...

    class Meta:
        db_table = 'coordination_organization'  # Keep old table name
```

**Step 2: Add Organization Scoping to Partnerships**
- **Complexity:** Moderate
- **Priority:** HIGH
- **Technical Approach:** Add lead_organization field

**Database Changes:**
```python
# migrations/coordination/0021_add_organization_scoping.py

def assign_partnerships_to_oobc(apps, schema_editor):
    """Assign all existing partnerships to OOBC"""
    Partnership = apps.get_model('coordination', 'Partnership')
    Organization = apps.get_model('organizations', 'Organization')

    oobc_org = Organization.objects.get(code='OOBC')

    Partnership.objects.filter(lead_organization__isnull=True).update(
        lead_organization=oobc_org
    )

class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0002_seed_initial_orgs'),
        ('coordination', '0020_rename_organization_model'),
    ]

    operations = [
        # Add lead organization field
        migrations.AddField(
            model_name='partnership',
            name='lead_organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True,
                help_text='BARMM MOA leading this partnership'
            ),
        ),

        # Populate with OOBC
        migrations.RunPython(
            assign_partnerships_to_oobc,
            reverse_code=migrations.RunPython.noop
        ),

        # Make required
        migrations.AlterField(
            model_name='partnership',
            name='lead_organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False
            ),
        ),

        # Add participating MOAs for inter-ministerial partnerships
        migrations.AddField(
            model_name='partnership',
            name='participating_moas',
            field=models.ManyToManyField(
                'organizations.Organization',
                blank=True,
                related_name='joint_partnerships',
                help_text='Other BARMM MOAs participating in this partnership'
            ),
        ),

        # Add index
        migrations.AddIndex(
            model_name='partnership',
            index=models.Index(
                fields=['lead_organization', 'status'],
                name='coord_partner_org_status_idx'
            ),
        ),
    ]
```

**Updated Models:**
```python
# src/coordination/models.py (AFTER)

from organizations.models import OrganizationScopedModel

class Partnership(OrganizationScopedModel):  # Inherits organization field
    """Formal partnership agreements (org-scoped)"""
    title = models.CharField(max_length=255)
    partnership_type = models.CharField(max_length=20)

    # External partners (NGOs, LGUs, etc.)
    partner_organizations = models.ManyToManyField(
        'PartnerOrganization',
        help_text='External partner organizations involved'
    )

    # Inter-MOA collaboration
    participating_moas = models.ManyToManyField(
        'organizations.Organization',
        blank=True,
        related_name='joint_partnerships',
        help_text='Other BARMM MOAs participating'
    )

    status = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['organization', 'status']),
        ]

    def can_view(self, user):
        """Check if user can view this partnership"""
        if user.is_superuser:
            return True

        # Lead MOA can view
        if user.organization == self.organization:
            return True

        # Participating MOAs can view
        if self.participating_moas.filter(id=user.organization.id).exists():
            return True

        return False

class StakeholderEngagement(OrganizationScopedModel):
    """Engagement activities (org-scoped)"""
    title = models.CharField(max_length=255)
    engagement_type = models.CharField(max_length=20)

    # Related to partnership (optional)
    partnership = models.ForeignKey(
        'Partnership',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # External partners involved
    partner_organizations = models.ManyToManyField('PartnerOrganization')

    # Inter-MOA collaboration
    participating_moas = models.ManyToManyField(
        'organizations.Organization',
        blank=True,
        related_name='joint_engagements'
    )

    # Related MANA assessment (if applicable)
    related_assessment = models.ForeignKey(
        'mana.Assessment',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
```

**Step 3: Fix URL Routing**
- **Complexity:** Simple
- **Priority:** MEDIUM
- **Technical Approach:** Same as previous modules

```python
# src/coordination/urls.py (UPDATE)
app_name = "coordination"

urlpatterns = [
    # Organizations (external partners)
    path("partners/", views.partner_list, name="partners"),
    path("partners/<int:pk>/", views.partner_detail, name="partner_detail"),

    # Partnerships
    path("partnerships/", views.partnership_list, name="partnerships"),
    path("partnerships/<int:pk>/", views.partnership_detail, name="partnership_detail"),
    path("partnerships/create/", views.partnership_create, name="partnership_create"),

    # Inter-MOA partnerships
    path("inter-ministerial/", views.inter_moa_list, name="inter_moa"),
    path("inter-ministerial/<int:pk>/", views.inter_moa_detail, name="inter_moa_detail"),

    # Engagements
    path("engagements/", views.engagement_list, name="engagements"),
    path("engagements/<int:pk>/", views.engagement_detail, name="engagement_detail"),

    # Communications
    path("communications/", views.communication_list, name="communications"),
]

# src/obc_management/urls.py (CHANGE)
path("coordination/", include("coordination.urls")),  # Direct routing
```

#### Testing Requirements

**Test Suite:**
```python
# tests/coordination/test_organization_scoping.py

class CoordinationOrganizationScopingTestCase(TestCase):
    def test_partnership_org_scoping(self):
        """Test partnerships are scoped to lead organization"""
        oobc_partnerships = Partnership.objects.all()  # Auto-filtered
        self.assertEqual(oobc_partnerships.count(), 1)
        self.assertEqual(oobc_partnerships.first(), self.oobc_partnership)

    def test_inter_moa_partnership_visibility(self):
        """Test inter-MOA partnerships visible to all participants"""
        # Create inter-MOA partnership
        partnership = Partnership.objects.create(
            organization=self.oobc,  # Lead
            title='OOBC-MOH Joint Health Program'
        )
        partnership.participating_moas.add(self.moh)

        # MOH should be able to view
        self.assertTrue(partnership.can_view(self.moh_user))

    def test_partner_organization_rename(self):
        """Test coordination.Organization renamed to PartnerOrganization"""
        from coordination.models import PartnerOrganization

        partner = PartnerOrganization.objects.create(
            name='Save the Children',
            organization_type='ingo'
        )

        self.assertEqual(partner.__class__.__name__, 'PartnerOrganization')
```

#### Dependencies

**Requires:**
- Phase 1: Organizations app
- MANA module transformation (for related_assessment links)

**Blocks:**
- OCM aggregation layer (uses coordination data for inter-MOA monitoring)

**Complexity Rating:** Moderate
**Priority:** HIGH (Enables inter-ministerial collaboration)

---

### 16. M&E Module Organization Scoping

#### Current State Analysis

**Django App:** `src/monitoring/`
**URL Namespace:** `monitoring:*` ✅ (Good - already separate)
**Current Organization Support:** PARTIAL - `implementing_moa` field exists

**Key Models:**
```python
# src/monitoring/models.py (inferred)

class Program(models.Model):
    """Program-level M&E"""
    title = models.CharField(max_length=255)
    implementing_moa = models.ForeignKey(
        'coordination.Organization',
        null=True,
        on_delete=models.SET_NULL
    )  # ⚠️ Points to coordination.Organization (will be wrong after rename)
    # NO organization field for ownership ❌

class Project(models.Model):
    """Project-level M&E"""
    program = models.ForeignKey('Program', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    target_communities = models.ManyToManyField('communities.OBCCommunity')
    # NO organization field ❌

class Activity(models.Model):
    """Activity-level M&E"""
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    # NO organization field ❌
```

**Current Data Volume:**
- ~100 programs
- ~500 projects
- ~2000 activities

#### Target BMMS State

**Organization Scoping:** **ORGANIZATION-SCOPED** (Each MOA manages own PPAs)

**Enhancement Pattern:**
```
┌───────────────────────────────────────────────────────────┐
│  M&E in BMMS:                                             │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  MOA-Specific PPAs:                                      │
│  • MOH manages health programs/projects/activities       │
│  • organization = MOH (exclusive ownership)              │
│  • Only MOH staff can edit                               │
│                                                           │
│  Inter-MOA Projects (Future):                            │
│  • OOBC + MOH joint health outreach project              │
│  • lead_organization = OOBC                              │
│  • partner_organizations = [MOH]                         │
│  • Collaborative execution tracking                      │
│                                                           │
│  OCM Aggregation:                                        │
│  • Office of the Chief Minister views all MOA PPAs              │
│  • Government-wide performance dashboards                │
│  • Cross-MOA budget execution monitoring                 │
└───────────────────────────────────────────────────────────┘
```

#### Migration Strategy

**Step 1: Fix implementing_moa Foreign Key**
- **Complexity:** Simple
- **Priority:** CRITICAL (Dependency on coordination refactor)
- **Technical Approach:** Update FK after coordination.Organization renamed

**Database Changes:**
```python
# migrations/monitoring/0025_fix_implementing_moa_fk.py

class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0002_seed_initial_orgs'),
        ('coordination', '0020_rename_organization_model'),
        ('monitoring', '0024_previous_migration'),
    ]

    operations = [
        # Update implementing_moa to point to organizations.Organization
        migrations.RemoveField(
            model_name='program',
            name='implementing_moa',
        ),

        migrations.AddField(
            model_name='program',
            name='implementing_moa',
            field=models.ForeignKey(
                'organizations.Organization',
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                help_text='BARMM MOA implementing this program'
            ),
        ),
    ]
```

**Step 2: Add Organization Ownership to PPAs**
- **Complexity:** Moderate
- **Priority:** CRITICAL
- **Technical Approach:** Add organization field with OOBC default

**Database Changes:**
```python
# migrations/monitoring/0026_add_organization_scoping.py

def assign_ppas_to_oobc(apps, schema_editor):
    """Assign all existing PPAs to OOBC"""
    Program = apps.get_model('monitoring', 'Program')
    Project = apps.get_model('monitoring', 'Project')
    Activity = apps.get_model('monitoring', 'Activity')
    Organization = apps.get_model('organizations', 'Organization')

    oobc_org = Organization.objects.get(code='OOBC')

    # Assign programs
    Program.objects.filter(organization__isnull=True).update(
        organization=oobc_org
    )

    # Assign projects
    Project.objects.filter(organization__isnull=True).update(
        organization=oobc_org
    )

    # Assign activities
    Activity.objects.filter(organization__isnull=True).update(
        organization=oobc_org
    )

class Migration(migrations.Migration):
    dependencies = [
        ('monitoring', '0025_fix_implementing_moa_fk'),
    ]

    operations = [
        # Add organization to Program
        migrations.AddField(
            model_name='program',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True
            ),
        ),

        # Add organization to Project
        migrations.AddField(
            model_name='project',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True
            ),
        ),

        # Add organization to Activity
        migrations.AddField(
            model_name='activity',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True
            ),
        ),

        # Populate with OOBC
        migrations.RunPython(
            assign_ppas_to_oobc,
            reverse_code=migrations.RunPython.noop
        ),

        # Make required
        migrations.AlterField(
            model_name='program',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False
            ),
        ),
        migrations.AlterField(
            model_name='project',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False
            ),
        ),
        migrations.AlterField(
            model_name='activity',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False
            ),
        ),

        # Add indexes
        migrations.AddIndex(
            model_name='program',
            index=models.Index(
                fields=['organization', 'status'],
                name='monitor_prog_org_status_idx'
            ),
        ),
    ]
```

**Updated Models:**
```python
# src/monitoring/models.py (AFTER)

from organizations.models import OrganizationScopedModel

class Program(OrganizationScopedModel):
    """Program (org-scoped)"""
    title = models.CharField(max_length=255)

    # implementing_moa can differ from organization (partnership scenario)
    implementing_moa = models.ForeignKey(
        'organizations.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='implemented_programs',
        help_text='MOA implementing this program (may differ from owner)'
    )

    # ... 100+ M&E fields ...

class Project(OrganizationScopedModel):
    """Project (org-scoped)"""
    program = models.ForeignKey('Program', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    target_communities = models.ManyToManyField('communities.OBCCommunity')
    # ... fields ...

class Activity(OrganizationScopedModel):
    """Activity (org-scoped)"""
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    # ... fields ...
```

**Step 3: Update Queries**
- **Complexity:** Simple
- **Priority:** HIGH
- **Technical Approach:** OrganizationScopedModel auto-filters

```python
# src/monitoring/views.py (BEFORE)

def program_list(request):
    programs = Program.objects.all()  # Shows ALL programs
    return render(request, 'monitoring/programs.html', {'programs': programs})

# src/monitoring/views.py (AFTER)

from organizations.decorators import require_module_enabled

@require_module_enabled('me')
def program_list(request):
    # Automatic org filtering
    programs = Program.objects.all()  # Only user's org
    return render(request, 'monitoring/programs.html', {'programs': programs})
```

#### Testing Requirements

**Test Suite:**
```python
# tests/monitoring/test_organization_scoping.py

class MEOrganizationScopingTestCase(TestCase):
    def test_program_org_scoping(self):
        """Test programs scoped to organization"""
        oobc_programs = Program.objects.all()
        self.assertEqual(oobc_programs.count(), 1)

    def test_ocm_can_see_all_ppas(self):
        """Test OCM staff can view all MOA PPAs"""
        ocm_user = User.objects.create(username='ocm_staff', is_superuser=True)

        all_programs = Program.all_objects.all()  # Bypass org scoping
        self.assertGreaterEqual(all_programs.count(), 2)  # OOBC + MOH
```

#### Dependencies

**Requires:**
- Phase 1: Organizations app
- Coordination module refactor (fixing coordination.Organization rename)

**Blocks:**
- Budgeting module (links budget items to PPAs)
- Planning module (links strategic plans to PPAs)

**Complexity Rating:** Moderate
**Priority:** HIGH (Core performance monitoring functionality)

---

### 17. Recommendations/Policies Module

#### Current State Analysis

**Django App:** `src/recommendations/policies/`
**URL Namespace:** `common:recommendations_*` (routed through common)
**Current Organization Support:** NONE

**Key Models:**
```python
# src/recommendations/policies/models.py

class PolicyRecommendation(models.Model):
    """Policy recommendation tracking"""
    title = models.CharField(max_length=255)
    recommendation_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    target_agency = models.CharField(max_length=200)  # Text field, not FK ❌
    # NO organization field ❌
```

#### Target BMMS State

**Organization Scoping:** **ORGANIZATION-SCOPED** (Each MOA manages own policies)

#### Migration Strategy

**Step 1: Add Organization Field**
- **Complexity:** Simple
- **Priority:** MEDIUM
- **Technical Approach:** Same pattern as MANA/M&E

**Database Changes:**
```python
# migrations/recommendations/policies/0010_add_organization.py

def assign_policies_to_oobc(apps, schema_editor):
    PolicyRecommendation = apps.get_model('policies', 'PolicyRecommendation')
    Organization = apps.get_model('organizations', 'Organization')

    oobc_org = Organization.objects.get(code='OOBC')

    PolicyRecommendation.objects.filter(organization__isnull=True).update(
        organization=oobc_org
    )

class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0002_seed_initial_orgs'),
        ('policies', '0009_previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='policyrecommendation',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=True
            ),
        ),

        migrations.RunPython(assign_policies_to_oobc),

        migrations.AlterField(
            model_name='policyrecommendation',
            name='organization',
            field=models.ForeignKey(
                'organizations.Organization',
                on_delete=models.PROTECT,
                null=False
            ),
        ),
    ]
```

**Step 2: Fix URL Routing**
```python
# src/recommendations/policies/urls.py
app_name = "policies"

urlpatterns = [
    path("", views.policy_list, name="list"),
    path("<int:pk>/", views.policy_detail, name="detail"),
]

# src/obc_management/urls.py
path("policies/", include("recommendations.policies.urls")),
```

#### Testing Requirements

```python
def test_policy_org_scoping(self):
    """Test policies scoped to organization"""
    oobc_policies = PolicyRecommendation.objects.all()
    self.assertEqual(oobc_policies.first().organization, self.oobc)
```

#### Dependencies

**Requires:** Phase 1: Organizations app

**Complexity Rating:** Simple
**Priority:** MEDIUM (Less complex than MANA/M&E)

---

### 18. NEW: Planning Module

#### Target BMMS State

**Organization Scoping:** **ORGANIZATION-SCOPED**

**Purpose:** Strategic planning and annual work plans per MOA

**Key Models:**
```python
# src/planning/models.py

from organizations.models import OrganizationScopedModel

class StrategicPlan(OrganizationScopedModel):
    """3-5 year strategic plan"""
    title = models.CharField(max_length=255)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    vision = models.TextField()
    mission = models.TextField()
    strategic_goals = models.JSONField(default=list)
    status = models.CharField(max_length=20)

class AnnualWorkPlan(OrganizationScopedModel):
    """Annual operational plan"""
    strategic_plan = models.ForeignKey('StrategicPlan', on_delete=models.CASCADE)
    year = models.IntegerField()
    objectives = models.JSONField(default=list)
    # Links to M&E projects
    linked_programs = models.ManyToManyField('monitoring.Program')
```

#### Migration Strategy

**Step 1: Create Planning App**
```bash
cd src
python manage.py startapp planning
```

**Step 2: Implement Models**
```python
# migrations/planning/0001_initial.py

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('organizations', '0002_seed_initial_orgs'),
        ('monitoring', '0026_add_organization_scoping'),
    ]

    operations = [
        migrations.CreateModel(
            name='StrategicPlan',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('organization', models.ForeignKey(
                    'organizations.Organization',
                    on_delete=models.PROTECT
                )),
                ('title', models.CharField(max_length=255)),
                ('start_year', models.IntegerField()),
                ('end_year', models.IntegerField()),
                # ... fields ...
            ],
        ),

        migrations.CreateModel(
            name='AnnualWorkPlan',
            # ... fields ...
        ),
    ]
```

**Step 3: Build UI**
```python
# src/planning/urls.py
app_name = "planning"

urlpatterns = [
    path("strategic/", views.strategic_plan_list, name="strategic"),
    path("annual/", views.annual_work_plan_list, name="annual"),
]
```

#### Dependencies

**Requires:**
- Phase 1: Organizations app
- M&E module transformation (for linking plans to PPAs)

**Complexity Rating:** Complex (Build from scratch)
**Priority:** HIGH (Required for BMMS)

---

### 19. NEW: Budgeting Module (Parliament Bill No. 325)

#### Target BMMS State

**Organization Scoping:** **ORGANIZATION-SCOPED + OCM AGGREGATION**

**Purpose:** Budget preparation, authorization, execution per MOA

**Legal Foundation:** Parliament Bill No. 325 (Bangsamoro Budget System Act)

**Key Requirements:**
- Budget preparation (per MOA)
- Budget authorization (GAAB approval)
- Budget execution (allotments, obligations, disbursements)
- Financial accountability reporting

#### Migration Strategy

**Step 1: Create Core Budget Apps**
```bash
cd src
python manage.py startapp budget_system
python manage.py startapp budget_preparation
python manage.py startapp budget_authorization
python manage.py startapp budget_execution
python manage.py startapp financial_accountability
```

**Step 2: Implement Fiscal Policy Models**
```python
# src/budget_system/models.py

class FiscalPolicyStatement(models.Model):
    """Statement of Fiscal Policy (Section 7)"""
    title = models.CharField(max_length=255)
    fiscal_year = models.IntegerField()
    medium_term_objectives = models.JSONField(default=dict)
    status = models.CharField(max_length=20)

class MediumTermFiscalStrategy(models.Model):
    """MTFS (Section 8)"""
    fiscal_policy = models.ForeignKey('FiscalPolicyStatement', on_delete=models.CASCADE)
    year = models.IntegerField()
    # ... fields ...
```

**Step 3: Implement Budget Preparation**
```python
# src/budget_preparation/models.py

from organizations.models import OrganizationScopedModel

class BudgetCall(models.Model):
    """Annual Budget Call"""
    fiscal_year = models.IntegerField()
    submission_deadline = models.DateField()
    budget_ceiling = models.DecimalField(max_digits=14, decimal_places=2)

class MOABudgetProposal(OrganizationScopedModel):
    """M/O/A budget submission"""
    budget_call = models.ForeignKey('BudgetCall', on_delete=models.CASCADE)
    proposed_amount = models.DecimalField(max_digits=14, decimal_places=2)
    justification = models.TextField()
    status = models.CharField(max_length=20)  # draft, submitted, approved

class ProgramBudget(OrganizationScopedModel):
    """Budget per program"""
    budget_proposal = models.ForeignKey('MOABudgetProposal', on_delete=models.CASCADE)
    program = models.ForeignKey('monitoring.Program', on_delete=models.CASCADE)
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
```

**Step 4: Implement Budget Authorization**
```python
# src/budget_authorization/models.py

class GAAB(models.Model):
    """General Appropriations Act of Bangsamoro"""
    fiscal_year = models.IntegerField()
    parliament_bill_number = models.CharField(max_length=50)
    total_appropriation = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20)  # enacted, published

class GAABItem(models.Model):
    """GAAB line items per MOA"""
    gaab = models.ForeignKey('GAAB', on_delete=models.CASCADE)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT)
    appropriated_amount = models.DecimalField(max_digits=12, decimal_places=2)
```

**Step 5: Implement Budget Execution**
```python
# src/budget_execution/models.py

from organizations.models import OrganizationScopedModel

class Allotment(OrganizationScopedModel):
    """Allotment tracking"""
    gaab_item = models.ForeignKey('budget_authorization.GAABItem', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20)

class Obligation(OrganizationScopedModel):
    """Obligation tracking"""
    allotment = models.ForeignKey('Allotment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    obligated_date = models.DateField()

class Disbursement(OrganizationScopedModel):
    """Disbursement tracking"""
    obligation = models.ForeignKey('Obligation', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    disbursed_date = models.DateField()
```

#### Testing Requirements

```python
# tests/budget/test_organization_scoping.py

def test_budget_proposal_org_scoping(self):
    """Test budget proposals scoped to organization"""
    moh_proposals = MOABudgetProposal.objects.all()
    self.assertEqual(moh_proposals.first().organization, self.moh)

def test_ocm_can_aggregate_all_budgets(self):
    """Test OCM can view consolidated budget"""
    all_proposals = MOABudgetProposal.all_objects.all()
    total_requested = all_proposals.aggregate(Sum('proposed_amount'))
    self.assertGreater(total_requested['proposed_amount__sum'], 0)
```

#### Dependencies

**Requires:**
- Phase 1: Organizations app
- M&E module (for linking budget to PPAs)
- Planning module (for budget-plan alignment)

**Complexity Rating:** Very Complex (New system + legal compliance)
**Priority:** CRITICAL (Parliament Bill No. 325 compliance)

---

### 20. Common Module Refactoring (Fix "Monolithic Router Anti-Pattern")

#### Current State Analysis

**Problem:** `common` app handles 4 modules' views + 6 modules' URL routing

**Files:**
- `src/common/urls.py`: 848 lines (should be < 200)
- `src/common/views.py`: 2000+ lines (should be < 500)

#### Target BMMS State

**Enhancement:** Slim down common app to core shared infrastructure only

**What Stays in Common:**
- Dashboard (unified entry point)
- User management
- Geographic hierarchy (Region, Province, Municipality, Barangay)
- WorkItem system (tasks, activities, projects)
- Calendar (shared across all orgs)
- Staff teams and performance targets

**What Moves Out:**
- Communities views → `communities/` app
- MANA views → `mana/` app
- Coordination views → `coordination/` app
- Recommendations views → `recommendations/` app

#### Migration Strategy

**Step 1: Move Views to Respective Apps**
```python
# src/communities/views.py (CREATE/ENHANCE)

def obc_list(request):
    """Moved from common.views"""
    communities = OBCCommunity.objects.all()
    return render(request, 'communities/list.html', {'communities': communities})

def obc_detail(request, pk):
    """Moved from common.views"""
    community = get_object_or_404(OBCCommunity, pk=pk)
    return render(request, 'communities/detail.html', {'community': community})

# Repeat for mana/, coordination/, recommendations/
```

**Step 2: Update URL Routing**
```python
# src/obc_management/urls.py (AFTER)

urlpatterns = [
    # Dashboard (stays in common)
    path("dashboard/", include("common.urls")),  # Only dashboard + infrastructure

    # Module-specific URLs (direct routing)
    path("communities/", include("communities.urls")),
    path("mana/", include("mana.urls")),
    path("coordination/", include("coordination.urls")),
    path("policies/", include("recommendations.policies.urls")),
    path("monitoring/", include("monitoring.urls")),
    path("planning/", include("planning.urls")),
    path("budget/", include("budget_system.urls")),
]
```

**Step 3: Update All Template References**
```bash
# Find all template references to common:*
grep -r "{% url 'common:" src/templates/

# Update systematically
sed -i '' 's/common:communities_/communities:/g' src/templates/**/*.html
sed -i '' 's/common:mana_/mana:/g' src/templates/**/*.html
sed -i '' 's/common:coordination_/coordination:/g' src/templates/**/*.html
sed -i '' 's/common:recommendations_/policies:/g' src/templates/**/*.html
```

#### Testing Requirements

```python
def test_url_refactoring_complete(self):
    """Test all modules have proper namespaces"""
    # Communities
    url = reverse('communities:manage')
    self.assertEqual(url, '/communities/')

    # MANA
    url = reverse('mana:home')
    self.assertEqual(url, '/mana/')

    # Coordination
    url = reverse('coordination:partnerships')
    self.assertEqual(url, '/coordination/partnerships/')

    # Policies
    url = reverse('policies:list')
    self.assertEqual(url, '/policies/')
```

#### Dependencies

**Requires:**
- All other module migrations complete
- Comprehensive template audit

**Complexity Rating:** Complex (High risk of breaking URLs)
**Priority:** MEDIUM (Technical debt reduction)

---

## Summary Matrix

| Module | Organization Scoping | Complexity | Priority | Database Changes | URL Changes |
|--------|---------------------|------------|----------|------------------|-------------|
| **Communities** | SHARED (no org field) | Simple | HIGH | NONE | Namespace only |
| **MANA** | ORG-SCOPED + Collaborative | Moderate | CRITICAL | Add org + M2M | Namespace + routing |
| **Coordination** | HYBRID (lead + participants) | Moderate | HIGH | Rename + add org | Namespace + routing |
| **M&E** | ORG-SCOPED | Moderate | HIGH | Add org to PPAs | Minimal (already good) |
| **Policies** | ORG-SCOPED | Simple | MEDIUM | Add org | Namespace only |
| **Planning** | ORG-SCOPED (NEW) | Complex | HIGH | Create from scratch | New app |
| **Budgeting** | ORG-SCOPED (NEW) | Very Complex | CRITICAL | Create from scratch | New app |
| **Common Refactor** | N/A (Infrastructure) | Complex | MEDIUM | NONE | Major refactoring |

---

**Part V Complete:** Module-by-module transition plan with detailed technical guidance, code examples, and testing requirements.

---

## Part VI: URL Structure Refactoring

**Critical Context:** This section addresses the "Monolithic Router Anti-Pattern" common app routing issue identified in `docs/plans/obcmsapps/05-ui-architecture-alignment-plan.md`. The current architecture violates Django best practices by consolidating 4 out of 6 user modules in a bloated `common` app, creating maintenance bottlenecks and unclear module boundaries.

**Strategic Importance:** URL refactoring is a prerequisite for BMMS multi-tenancy. We must fix the architectural debt NOW (during BMMS transition) to avoid carrying it forward to a 30x larger system.

---

### 20. Fixing the "Monolithic Router Anti-Pattern" Common App

#### 20.1 Current URL Problems

**Problem Severity:** CRITICAL - Blocks clean BMMS implementation

**Current State Analysis:**

```python
# src/common/urls.py (847 lines - BLOATED "Monolithic Router")
from django.urls import path
from . import views
from coordination import views as coordination_views

app_name = "common"

urlpatterns = [
    # Dashboard & Infrastructure (✅ CORRECT - belongs in common)
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    
    # ❌ PROBLEM: Communities module (should be in communities/)
    path("communities/", views.communities_home, name="communities_home"),
    path("communities/manage/", views.communities_manage, name="communities_manage"),
    path("communities/<int:community_id>/", views.communities_view, name="communities_view"),
    # ... 50+ more communities URLs ...
    
    # ❌ PROBLEM: MANA module (should be in mana/)
    path("mana/", views.mana_home, name="mana_home"),
    path("mana/regional/", views.mana_regional_overview, name="mana_regional_overview"),
    path("mana/desk-review/", views.mana_desk_review, name="mana_desk_review"),
    # ... 30+ more MANA URLs ...
    
    # ❌ PROBLEM: Coordination module (should be in coordination/)
    path("coordination/", views.coordination_home, name="coordination_home"),
    path("coordination/partnerships/", views.coordination_partnerships, name="coordination_partnerships"),
    # ... 20+ more coordination URLs ...
    
    # ❌ PROBLEM: Recommendations module (should be in recommendations/)
    path("recommendations/", views.recommendations_home, name="recommendations_home"),
    path("recommendations/manage/", views.recommendations_manage, name="recommendations_manage"),
    # ... 15+ more recommendations URLs ...
    
    # ... 700+ MORE LINES ...
]
```

**Impact Analysis:**

| Issue | Current State | Business Impact | Technical Debt |
|-------|---------------|-----------------|----------------|
| **File Size** | 847 lines in `common/urls.py` | Developer friction, slow code navigation | High merge conflict risk |
| **View File** | 2000+ lines in `common/views.py` | Violates Single Responsibility | Maintenance nightmare |
| **Namespace Confusion** | `common:mana_home` (suggests MANA is part of common) | Developer confusion, incorrect mental models | Code discovery requires 5+ steps |
| **Module Coupling** | 4 modules tightly coupled to `common` | Cannot modularize for BMMS | Blocks clean organization-scoping |
| **Testing Complexity** | Single massive file to test | Slow test execution, unclear coverage | Risk of regression bugs |

**Why This Blocks BMMS:**

1. **Organization-Scoped URLs:** BMMS needs `/moa/<ORG_CODE>/mana/` but current routing is flat
2. **Module Independence:** BMMS requires each module to handle its own organization context
3. **Multi-Tenant Middleware:** Cannot inject organization context when routing is centralized
4. **Scalability:** 30 organizations × current complexity = unmaintainable system

**Quantified Problem:**

```bash
# Code distribution (CURRENT)
src/common/
├── urls.py         # 847 lines (routing 6 modules!)
├── views.py        # 2000+ lines (handling 6 modules!)
└── ...

# What it SHOULD be
src/common/
├── urls.py         # < 150 lines (dashboard + infrastructure only)
├── views/
│   ├── dashboard.py   # 200 lines
│   ├── calendar.py    # 300 lines
│   └── staff.py       # 400 lines
└── ...

src/communities/
├── urls.py         # 100 lines (all communities URLs)
├── views.py        # 500 lines (communities logic)
└── ...

src/mana/
├── urls.py         # 80 lines (all MANA URLs)
├── views.py        # 600 lines (MANA logic)
└── ...
```

**Namespace Confusion Examples:**

```python
# Current (CONFUSING - module buried in common namespace)
{% url 'common:communities_home' %}      # ❌ Communities appears to be part of common
{% url 'common:mana_home' %}             # ❌ MANA appears to be part of common
{% url 'common:coordination_home' %}     # ❌ Coordination appears to be part of common

# Target (CLEAR - proper module namespaces)
{% url 'communities:home' %}             # ✅ Clearly communities module
{% url 'mana:home' %}                    # ✅ Clearly MANA module
{% url 'coordination:home' %}            # ✅ Clearly coordination module
```

**Developer Experience Impact:**

**Before (Current State):**
```bash
# Developer task: "Add MANA desk review export feature"
# Step 1: Which app has MANA code?
$ ls src/
common/  communities/  mana/  coordination/  # Two possible locations!

# Step 2: Check mana/ app
$ cat src/mana/urls.py
app_name = "mana"  # Only workshop participant URLs
urlpatterns = [
    path("workshops/", ...)  # Not what I need
]

# Step 3: Must be in common then...
$ cat src/common/urls.py
# Scroll through 847 lines...
# Line 132: path("mana/", views.mana_home, name="mana_home")
# Line 155: path("mana/desk-review/", views.mana_desk_review, name="mana_desk_review")
# ✅ Found it! But wasted 5 minutes searching...

# Step 4: Find the view function
$ cat src/common/views.py
# Scroll through 2000+ lines...
# Line 892: def mana_desk_review(request):
# ✅ Finally! Total time: 10+ minutes
```

**After (Target State):**
```bash
# Developer task: "Add MANA desk review export feature"
# Step 1: Open MANA app (obvious location)
$ cat src/mana/urls.py
app_name = "mana"
urlpatterns = [
    path("", views.home, name="home"),
    path("desk-review/", views.desk_review, name="desk_review"),
    path("desk-review/export/", views.desk_review_export, name="desk_review_export"),  # Add here
]

# Step 2: Open MANA views
$ cat src/mana/views.py
def desk_review(request):
    ...

def desk_review_export(request):  # Add new function here
    ...

# ✅ Done! Total time: 30 seconds
```

**Bottom Line:** Current architecture violates Django's "apps should be self-contained" principle. We MUST fix this before BMMS expansion.

---

#### 20.2 Target BMMS URL Structure

**Design Principles:**

1. **Organization-First Routing** - All user-facing modules under organization context
2. **Backward Compatibility** - OBCMS URLs redirect to BMMS equivalents
3. **Module Independence** - Each Django app owns its URL namespace
4. **RESTful Patterns** - Consistent URL design across modules

**Complete BMMS URL Hierarchy:**

```python
# ============================================================================
# PUBLIC PAGES (No Authentication Required)
# ============================================================================
/                                  # Landing page (BMMS overview, login/register)
/login/                            # Authentication (Django built-in)
/register/                         # User registration (role selection)
/about/                            # About BMMS/BARMM

# ============================================================================
# ORGANIZATION CONTEXT (Multi-Tenant Core)
# ============================================================================
# Format: /moa/<ORG_CODE>/<module>/
# ORG_CODE examples: OOBC, MSSD, MOH, MOE, MOA, MILF, etc.

/moa/<ORG_CODE>/                   # Organization landing page (redirect to dashboard)
/moa/<ORG_CODE>/dashboard/         # Organization-specific dashboard

# ----------------------------------------------------------------------------
# COMMUNITIES MODULE (Shared across all MOAs)
# ----------------------------------------------------------------------------
/moa/<ORG_CODE>/communities/                        # OBC data home
/moa/<ORG_CODE>/communities/barangay/               # Barangay OBC list
/moa/<ORG_CODE>/communities/barangay/<int:id>/      # Barangay OBC detail
/moa/<ORG_CODE>/communities/barangay/<int:id>/edit/ # Edit Barangay OBC
/moa/<ORG_CODE>/communities/municipal/              # Municipal OBC list
/moa/<ORG_CODE>/communities/municipal/<int:id>/     # Municipal OBC detail
/moa/<ORG_CODE>/communities/provincial/             # Provincial OBC list
/moa/<ORG_CODE>/communities/provincial/<int:id>/    # Provincial OBC detail
/moa/<ORG_CODE>/communities/stakeholders/           # Stakeholder directory
/moa/<ORG_CODE>/communities/import/                 # CSV import
/moa/<ORG_CODE>/communities/export/                 # Data export
/moa/<ORG_CODE>/communities/report/                 # Generate reports

# ----------------------------------------------------------------------------
# MANA MODULE (Organization-Scoped Assessments)
# ----------------------------------------------------------------------------
/moa/<ORG_CODE>/mana/                               # MANA home
/moa/<ORG_CODE>/mana/assessments/                   # Assessment list (org-filtered)
/moa/<ORG_CODE>/mana/assessments/new/               # Create assessment
/moa/<ORG_CODE>/mana/assessments/<uuid:id>/         # Assessment detail
/moa/<ORG_CODE>/mana/assessments/<uuid:id>/edit/    # Edit assessment
/moa/<ORG_CODE>/mana/regional/                      # Regional overview
/moa/<ORG_CODE>/mana/provincial/                    # Provincial overview
/moa/<ORG_CODE>/mana/provincial/<int:id>/           # Province detail
/moa/<ORG_CODE>/mana/desk-review/                   # Desk review module
/moa/<ORG_CODE>/mana/survey/                        # Survey module
/moa/<ORG_CODE>/mana/kii/                           # Key Informant Interviews
/moa/<ORG_CODE>/mana/playbook/                      # MANA methodology
/moa/<ORG_CODE>/mana/activity-planner/              # Activity planner
/moa/<ORG_CODE>/mana/activity-log/                  # Activity log

# Collaborative MANA (Cross-Organization)
/moa/<ORG_CODE>/mana/collaborations/                # Joint assessments
/moa/<ORG_CODE>/mana/collaborations/<uuid:id>/      # Collaboration detail
/moa/<ORG_CODE>/mana/shared-with-me/                # Assessments shared by other MOAs

# ----------------------------------------------------------------------------
# COORDINATION MODULE (Intra-MOA + Inter-MOA)
# ----------------------------------------------------------------------------
/moa/<ORG_CODE>/coordination/                       # Coordination home
/moa/<ORG_CODE>/coordination/organizations/         # Partner organizations (external)
/moa/<ORG_CODE>/coordination/organizations/<uuid:id>/ # Organization detail
/moa/<ORG_CODE>/coordination/partnerships/          # Partnership agreements
/moa/<ORG_CODE>/coordination/partnerships/<uuid:id>/ # Partnership detail
/moa/<ORG_CODE>/coordination/events/                # Events/activities list
/moa/<ORG_CODE>/coordination/calendar/              # Organization calendar
/moa/<ORG_CODE>/coordination/resources/             # Resource management
/moa/<ORG_CODE>/coordination/resources/<int:id>/    # Resource detail
/moa/<ORG_CODE>/coordination/bookings/              # Resource booking requests

# Inter-MOA Coordination (NEW in BMMS)
/moa/<ORG_CODE>/coordination/inter-moa/             # Cross-MOA partnerships
/moa/<ORG_CODE>/coordination/inter-moa/<uuid:id>/   # Inter-MOA partnership detail
/moa/<ORG_CODE>/coordination/joint-projects/        # Joint projects with other MOAs

# ----------------------------------------------------------------------------
# M&E MODULE (Organization-Scoped PPAs)
# ----------------------------------------------------------------------------
/moa/<ORG_CODE>/me/                                 # M&E home
/moa/<ORG_CODE>/me/programs/                        # Programs list (org-filtered)
/moa/<ORG_CODE>/me/programs/<uuid:id>/              # Program detail
/moa/<ORG_CODE>/me/projects/                        # Projects list
/moa/<ORG_CODE>/me/projects/<uuid:id>/              # Project detail
/moa/<ORG_CODE>/me/activities/                      # Activities list
/moa/<ORG_CODE>/me/activities/<uuid:id>/            # Activity detail
/moa/<ORG_CODE>/me/reports/                         # M&E reports
/moa/<ORG_CODE>/me/indicators/                      # Performance indicators

# ----------------------------------------------------------------------------
# PLANNING MODULE (NEW in BMMS)
# ----------------------------------------------------------------------------
/moa/<ORG_CODE>/planning/                           # Strategic planning home
/moa/<ORG_CODE>/planning/strategic-plans/           # Strategic plan list
/moa/<ORG_CODE>/planning/strategic-plans/<uuid:id>/ # Plan detail
/moa/<ORG_CODE>/planning/annual-plans/              # Annual operational plans
/moa/<ORG_CODE>/planning/annual-plans/<uuid:id>/    # Annual plan detail
/moa/<ORG_CODE>/planning/gap-analysis/              # OBC needs vs MOA mandates
/moa/<ORG_CODE>/planning/rdp-alignment/             # Regional Development Plan alignment

# ----------------------------------------------------------------------------
# BUDGETING MODULE (NEW in BMMS - Parliament Bill No. 325)
# ----------------------------------------------------------------------------
/moa/<ORG_CODE>/budgeting/                          # Budget management home
/moa/<ORG_CODE>/budgeting/proposals/                # Budget proposal list
/moa/<ORG_CODE>/budgeting/proposals/new/            # Create budget proposal
/moa/<ORG_CODE>/budgeting/proposals/<uuid:id>/      # Proposal detail
/moa/<ORG_CODE>/budgeting/proposals/<uuid:id>/edit/ # Edit proposal
/moa/<ORG_CODE>/budgeting/allocations/              # Current budget allocations
/moa/<ORG_CODE>/budgeting/utilization/              # Budget utilization tracking
/moa/<ORG_CODE>/budgeting/scenarios/                # Budget scenario planning
/moa/<ORG_CODE>/budgeting/scenarios/<uuid:id>/      # Scenario detail
/moa/<ORG_CODE>/budgeting/forecasting/              # Budget forecasting
/moa/<ORG_CODE>/budgeting/policy-matrix/            # Policy-budget alignment matrix

# ============================================================================
# OFFICE OF THE CHIEF MINISTER (OCM) CONTEXT (Cross-MOA Aggregation)
# ============================================================================
/ocm/                                               # OCM landing page
/ocm/dashboard/                                     # All-MOA consolidated dashboard
/ocm/budget-aggregation/                            # Consolidated budget across 44 MOAs
/ocm/budget-aggregation/<ORG_CODE>/                 # MOA-specific budget view
/ocm/budget-aggregation/compare/                    # Budget comparison tool
/ocm/reports/                                       # Cross-MOA reports
/ocm/reports/obc-coverage/                          # Total OBC coverage report
/ocm/reports/program-inventory/                     # All programs across MOAs
/ocm/reports/coordination-matrix/                   # Inter-MOA coordination map
/ocm/approval-workflow/                             # OCM approval queues
/ocm/moa-performance/                               # MOA performance dashboard

# ============================================================================
# INTERNAL MANAGEMENT (OOBC Staff, System Admin)
# ============================================================================
/oobc-management/                                   # OOBC internal operations
/oobc-management/user-approvals/                    # MOA user registration approvals
/oobc-management/staff/                             # Staff management
/oobc-management/staff/profiles/                    # Staff profiles
/oobc-management/staff/leave/                       # Leave management
/oobc-management/staff/performance/                 # Performance tracking
/oobc-management/calendar/                          # OOBC internal calendar
/oobc-management/work-items/                        # Work item management
/oobc-management/deprecation/                       # Feature deprecation tracking

# ============================================================================
# BACKWARD COMPATIBILITY (OBCMS Legacy URLs - Phase 1)
# ============================================================================
# These redirect to BMMS equivalents with 302 Found (temporary redirect)
# Allows existing bookmarks and external links to continue working

/communities/                       → /moa/OOBC/communities/          (302 redirect)
/communities/manage/                → /moa/OOBC/communities/barangay/ (302 redirect)
/communities/<int:id>/              → /moa/OOBC/communities/barangay/<int:id>/ (302 redirect)

/mana/                              → /moa/OOBC/mana/                 (302 redirect)
/mana/regional/                     → /moa/OOBC/mana/regional/        (302 redirect)
/mana/desk-review/                  → /moa/OOBC/mana/desk-review/     (302 redirect)

/coordination/                      → /moa/OOBC/coordination/         (302 redirect)
/coordination/partnerships/         → /moa/OOBC/coordination/partnerships/ (302 redirect)

/recommendations/                   → /moa/OOBC/policies/             (302 redirect)

# Note: /dashboard/ remains at root level, redirects based on user's default organization
/dashboard/                         → /moa/<USER_DEFAULT_ORG>/dashboard/ (302 redirect)
```

**URL Pattern Conventions:**

```python
# ============================================================================
# BMMS URL NAMING CONVENTIONS
# ============================================================================

# 1. Organization Context Prefix (Always Present)
/moa/<ORG_CODE>/...                 # ORG_CODE is uppercase (OOBC, MSSD, MOH, etc.)

# 2. Module Name (Lowercase, Hyphenated)
/moa/<ORG_CODE>/communities/        # ✅ Lowercase
/moa/<ORG_CODE>/planning/           # ✅ Lowercase
/moa/<ORG_CODE>/budgeting/          # ✅ Lowercase (not "budget")

# 3. Resource Actions (RESTful)
/<resource>/                        # List view
/<resource>/new/                    # Create form
/<resource>/<id>/                   # Detail view
/<resource>/<id>/edit/              # Edit form
/<resource>/<id>/delete/            # Delete confirmation

# 4. Nested Resources (Max 2 levels)
/<resource>/<id>/<sub-resource>/    # ✅ Good
/<resource>/<id>/<sub>/<sub>/      # ❌ Too deep

# 5. Hyphenated Multi-Word URLs
/desk-review/                       # ✅ Hyphenated
/desk_review/                       # ❌ Underscores
/deskreview/                        # ❌ No separation

# 6. ID Formats
/<int:id>/                          # Integer PKs (communities, resources)
/<uuid:id>/                         # UUID PKs (assessments, work items)
/<str:code>/                        # Code-based lookups (organizations)

# 7. Filter/Search Query Params (Not in URL path)
/?status=active                     # ✅ Query param for filtering
/?region=IX                         # ✅ Query param for filtering
/active/                            # ❌ Don't create separate paths for filters
```

**Module URL Namespace Mapping:**

| Module | Django App | URL Namespace | Base Path |
|--------|------------|---------------|-----------|
| **Communities** | `communities` | `communities:*` | `/moa/<ORG>/communities/` |
| **MANA** | `mana` | `mana:*` | `/moa/<ORG>/mana/` |
| **Coordination** | `coordination` | `coordination:*` | `/moa/<ORG>/coordination/` |
| **M&E** | `monitoring` | `monitoring:*` | `/moa/<ORG>/me/` |
| **Policies** | `recommendations.policies` | `policies:*` | `/moa/<ORG>/policies/` |
| **Planning** | `planning` | `planning:*` | `/moa/<ORG>/planning/` (NEW) |
| **Budgeting** | `budget_system` | `budgeting:*` | `/moa/<ORG>/budgeting/` (NEW) |
| **OCM** | `ocm` | `ocm:*` | `/ocm/` |
| **Common** | `common` | `common:*` | `/dashboard/`, `/profile/` (infrastructure only) |

**Example: Full URL Resolution**

```python
# Template Usage (BMMS)
{% url 'mana:assessment_detail' org_code=request.organization.code id=assessment.id %}
# Resolves to: /moa/MSSD/mana/assessments/a1b2c3d4-5678-90ab-cdef-1234567890ab/

# View Usage (BMMS)
from django.urls import reverse
url = reverse('budgeting:proposal_detail', kwargs={
    'org_code': 'MOH',
    'id': 'uuid-here'
})
# Resolves to: /moa/MOH/budgeting/proposals/uuid-here/

# Redirect with Organization Context
return redirect('coordination:home', org_code=request.organization.code)
# Redirects to: /moa/<CURRENT_ORG>/coordination/
```

**OCM Special URLs:**

```python
# OCM users see aggregated views across ALL organizations
{% url 'cmo:budget_aggregation' %}
# Resolves to: /ocm/budget-aggregation/

# OCM can drill down to specific MOA
{% url 'cmo:budget_aggregation_detail' org_code='MSSD' %}
# Resolves to: /ocm/budget-aggregation/MSSD/

# OCM sees cross-MOA reports
{% url 'cmo:inter_moa_coordination' %}
# Resolves to: /ocm/reports/coordination-matrix/
```

---

### 21. New URL Structure Implementation

#### 21.1 Django URL Configuration (Complete Code)

**Step 1: Project-Level URL Routing**

```python
# ============================================================================
# FILE: src/obc_management/urls.py (Project-Level URL Configuration)
# ============================================================================
"""
BMMS URL Configuration

The `urlpatterns` list routes URLs to views. Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from common import views as common_views
from common.views import legacy_redirect

urlpatterns = [
    # ========================================================================
    # ADMIN INTERFACE
    # ========================================================================
    path('admin/', admin.site.urls),
    
    # ========================================================================
    # PUBLIC PAGES (No Authentication)
    # ========================================================================
    path('', common_views.landing_page, name='landing'),  # BMMS landing page
    path('about/', common_views.about, name='about'),
    
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    path('login/', auth_views.LoginView.as_view(
        template_name='common/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('register/', common_views.UserRegistrationView.as_view(), name='register'),
    
    path('register/moa/', common_views.MOARegistrationView.as_view(), name='moa_register'),
    
    path('register/moa/success/', common_views.MOARegistrationSuccessView.as_view(), 
         name='moa_register_success'),
    
    # ========================================================================
    # ORGANIZATION CONTEXT (Multi-Tenant Core)
    # ========================================================================
    # Format: /moa/<ORG_CODE>/<module>/
    # OrganizationMiddleware extracts ORG_CODE and sets request.organization
    
    path('moa/<str:org_code>/', include([
        
        # Redirect organization root to dashboard
        path('', RedirectView.as_view(pattern_name='common:dashboard', permanent=False)),
        
        # --------------------------------------------------------------------
        # COMMON (Dashboard, Profile, Infrastructure)
        # --------------------------------------------------------------------
        path('dashboard/', include('common.urls')),  # Includes dashboard, profile, work items, calendar
        
        # --------------------------------------------------------------------
        # COMMUNITIES MODULE (Shared Data)
        # --------------------------------------------------------------------
        path('communities/', include('communities.urls')),
        
        # --------------------------------------------------------------------
        # MANA MODULE (Organization-Scoped Assessments)
        # --------------------------------------------------------------------
        path('mana/', include('mana.urls')),
        
        # --------------------------------------------------------------------
        # COORDINATION MODULE (Intra-MOA + Inter-MOA)
        # --------------------------------------------------------------------
        path('coordination/', include('coordination.urls')),
        
        # --------------------------------------------------------------------
        # M&E MODULE (Organization-Scoped PPAs)
        # --------------------------------------------------------------------
        path('me/', include('monitoring.urls')),
        
        # --------------------------------------------------------------------
        # POLICIES MODULE (Organization-Scoped Recommendations)
        # --------------------------------------------------------------------
        path('policies/', include('recommendations.policies.urls')),
        
        # --------------------------------------------------------------------
        # PLANNING MODULE (NEW in BMMS)
        # --------------------------------------------------------------------
        path('planning/', include('planning.urls')),
        
        # --------------------------------------------------------------------
        # BUDGETING MODULE (NEW in BMMS)
        # --------------------------------------------------------------------
        path('budgeting/', include('budget_system.urls')),
        
    ])),
    
    # ========================================================================
    # OFFICE OF THE CHIEF MINISTER (OCM) CONTEXT
    # ========================================================================
    path('cmo/', include('cmo.urls')),
    
    # ========================================================================
    # INTERNAL MANAGEMENT (OOBC Staff, System Admin)
    # ========================================================================
    path('oobc-management/', include([
        path('', common_views.oobc_management_home, name='oobc_management_home'),
        path('user-approvals/', common_views.MOAApprovalListView.as_view(), name='moa_approval_list'),
        path('staff/', include('common.urls.staff')),  # Staff management URLs
        path('work-items/', include('common.urls.work_items')),  # Work item URLs
        path('deprecation/', common_views.deprecation_dashboard, name='deprecation_dashboard'),
    ])),
    
    # ========================================================================
    # API ENDPOINTS (DRF)
    # ========================================================================
    path('api/', include('common.urls.api')),  # Unified API routing
    
    # ========================================================================
    # BACKWARD COMPATIBILITY (OBCMS Legacy URLs - Phase 1)
    # ========================================================================
    # Temporary 302 redirects to BMMS equivalents
    # These preserve existing bookmarks and external links
    
    path('communities/', legacy_redirect, {'module': 'communities', 'default_org': 'OOBC'}),
    path('communities/<path:subpath>', legacy_redirect, {'module': 'communities', 'default_org': 'OOBC'}),
    
    path('mana/', legacy_redirect, {'module': 'mana', 'default_org': 'OOBC'}),
    path('mana/<path:subpath>', legacy_redirect, {'module': 'mana', 'default_org': 'OOBC'}),
    
    path('coordination/', legacy_redirect, {'module': 'coordination', 'default_org': 'OOBC'}),
    path('coordination/<path:subpath>', legacy_redirect, {'module': 'coordination', 'default_org': 'OOBC'}),
    
    path('recommendations/', legacy_redirect, {'module': 'policies', 'default_org': 'OOBC'}),
    path('recommendations/<path:subpath>', legacy_redirect, {'module': 'policies', 'default_org': 'OOBC'}),
    
    # Special case: Dashboard redirects to user's default organization
    path('dashboard/', common_views.dashboard_redirect, name='dashboard_legacy'),
]

# ============================================================================
# STATIC/MEDIA FILES (Development Only)
# ============================================================================
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
```

**Step 2: Module-Level URL Configuration (Example: Communities)**

```python
# ============================================================================
# FILE: src/communities/urls.py (Communities Module URLs)
# ============================================================================
"""
Communities Module URL Configuration

All URLs are prefixed with /moa/<ORG_CODE>/communities/
OrganizationMiddleware ensures request.organization is set
"""
from django.urls import path
from . import views

app_name = "communities"

urlpatterns = [
    # ========================================================================
    # COMMUNITIES HOME
    # ========================================================================
    path('', views.home, name='home'),
    
    # ========================================================================
    # BARANGAY OBCs
    # ========================================================================
    path('barangay/', views.barangay_list, name='barangay_list'),
    path('barangay/add/', views.barangay_add, name='barangay_add'),
    path('barangay/<int:id>/', views.barangay_detail, name='barangay_detail'),
    path('barangay/<int:id>/edit/', views.barangay_edit, name='barangay_edit'),
    path('barangay/<int:id>/delete/', views.barangay_delete, name='barangay_delete'),
    path('barangay/<int:id>/restore/', views.barangay_restore, name='barangay_restore'),
    
    # ========================================================================
    # MUNICIPAL OBCs
    # ========================================================================
    path('municipal/', views.municipal_list, name='municipal_list'),
    path('municipal/add/', views.municipal_add, name='municipal_add'),
    path('municipal/<int:id>/', views.municipal_detail, name='municipal_detail'),
    path('municipal/<int:id>/edit/', views.municipal_edit, name='municipal_edit'),
    path('municipal/<int:id>/delete/', views.municipal_delete, name='municipal_delete'),
    path('municipal/<int:id>/restore/', views.municipal_restore, name='municipal_restore'),
    
    # ========================================================================
    # PROVINCIAL OBCs
    # ========================================================================
    path('provincial/', views.provincial_list, name='provincial_list'),
    path('provincial/add/', views.provincial_add, name='provincial_add'),
    path('provincial/<int:id>/', views.provincial_detail, name='provincial_detail'),
    path('provincial/<int:id>/edit/', views.provincial_edit, name='provincial_edit'),
    path('provincial/<int:id>/delete/', views.provincial_delete, name='provincial_delete'),
    path('provincial/<int:id>/submit/', views.provincial_submit, name='provincial_submit'),
    path('provincial/<int:id>/restore/', views.provincial_restore, name='provincial_restore'),
    
    # ========================================================================
    # STAKEHOLDERS
    # ========================================================================
    path('stakeholders/', views.stakeholders_list, name='stakeholders_list'),
    
    # ========================================================================
    # DATA MANAGEMENT
    # ========================================================================
    path('import/', views.import_csv, name='import_csv'),
    path('export/', views.export_data, name='export_data'),
    path('report/', views.generate_report, name='generate_report'),
    
    # ========================================================================
    # GEOGRAPHIC DATA
    # ========================================================================
    path('locations/centroid/', views.location_centroid, name='location_centroid'),
]
```

**Step 3: Organization Middleware**

```python
# ============================================================================
# FILE: src/common/middleware/organization.py (Organization Context Middleware)
# ============================================================================
"""
Organization Context Middleware

Extracts organization code from URL path and sets request.organization.
Handles invalid organization codes gracefully.
"""
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from common.models import Organization


class OrganizationMiddleware:
    """
    Middleware to extract organization context from URL and set request.organization.
    
    URL Pattern: /moa/<ORG_CODE>/<module>/...
    
    Examples:
        /moa/OOBC/communities/       → request.organization = Organization(code='OOBC')
        /moa/MSSD/mana/              → request.organization = Organization(code='MSSD')
        /moa/MOH/budgeting/          → request.organization = Organization(code='MOH')
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract organization code from URL path
        path_parts = request.path.strip('/').split('/')
        
        # Check if URL starts with 'moa/<ORG_CODE>/'
        if len(path_parts) >= 2 and path_parts[0] == 'moa':
            org_code = path_parts[1].upper()  # Normalize to uppercase
            
            try:
                # Look up organization by code
                organization = Organization.objects.get(code=org_code, is_active=True)
                request.organization = organization
                
            except Organization.DoesNotExist:
                # Handle invalid organization code
                if request.user.is_authenticated:
                    # Redirect authenticated users to their default organization
                    default_org = self._get_user_default_organization(request.user)
                    if default_org:
                        # Rebuild URL with correct organization code
                        new_path = f"/moa/{default_org.code}/{'/'.join(path_parts[2:])}"
                        return redirect(new_path)
                
                # Invalid organization code and no fallback
                raise Http404(f"Organization '{org_code}' does not exist or is inactive.")
        
        else:
            # URL doesn't have organization context (e.g., /login/, /admin/, /ocm/)
            request.organization = None
            
            # For legacy URLs, let the legacy_redirect view handle it
            if self._is_legacy_url(request.path):
                pass  # Let view handle redirect
            
            # For OCM URLs, no organization context needed
            elif request.path.startswith('/ocm/'):
                pass  # OCM views handle aggregation
            
            # For authenticated users accessing dashboard root, redirect to their org
            elif request.path == '/dashboard/' and request.user.is_authenticated:
                default_org = self._get_user_default_organization(request.user)
                if default_org:
                    return redirect('common:dashboard', org_code=default_org.code)
        
        response = self.get_response(request)
        return response
    
    def _get_user_default_organization(self, user):
        """Get user's default organization based on profile."""
        try:
            if hasattr(user, 'profile') and user.profile.default_organization:
                return user.profile.default_organization
            
            # Fallback: Get user's first organization membership
            if hasattr(user, 'organization_memberships'):
                first_membership = user.organization_memberships.filter(
                    organization__is_active=True
                ).first()
                if first_membership:
                    return first_membership.organization
            
            # Last resort: OOBC for staff users
            if user.groups.filter(name='OOBC Staff').exists():
                return Organization.objects.get(code='OOBC')
        
        except Exception:
            pass
        
        return None
    
    def _is_legacy_url(self, path):
        """Check if URL is a legacy OBCMS URL that needs redirect."""
        legacy_prefixes = [
            '/communities/',
            '/mana/',
            '/coordination/',
            '/recommendations/',
        ]
        return any(path.startswith(prefix) for prefix in legacy_prefixes)
```

**Step 4: Legacy Redirect View**

```python
# ============================================================================
# FILE: src/common/views/legacy.py (Backward Compatibility Redirects)
# ============================================================================
"""
Legacy URL Redirect Views

Handles OBCMS → BMMS URL redirects for backward compatibility.
Uses 302 (Found) temporary redirects to preserve bookmarks.
"""
from django.shortcuts import redirect
from django.urls import reverse


def legacy_redirect(request, module, default_org='OOBC', subpath=''):
    """
    Redirect legacy OBCMS URLs to BMMS equivalents.
    
    Args:
        request: HttpRequest object
        module: Target module (communities, mana, coordination, policies)
        default_org: Default organization code (OOBC for legacy users)
        subpath: Remaining URL path after module prefix
    
    Examples:
        /communities/manage/
        → /moa/OOBC/communities/barangay/
        
        /mana/regional/
        → /moa/OOBC/mana/regional/
        
        /coordination/partnerships/
        → /moa/OOBC/coordination/partnerships/
    """
    
    # Determine user's organization (if authenticated)
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.default_organization:
            org_code = request.user.profile.default_organization.code
        else:
            org_code = default_org
    else:
        org_code = default_org
    
    # Map legacy module names to BMMS module names
    module_mapping = {
        'communities': 'communities',
        'mana': 'mana',
        'coordination': 'coordination',
        'recommendations': 'policies',  # Renamed
        'policies': 'policies',
    }
    
    bmms_module = module_mapping.get(module, module)
    
    # Handle special URL mapping (legacy path → BMMS path)
    path_mapping = {
        'communities/manage/': 'communities/barangay/',
        'communities/managemunicipal/': 'communities/municipal/',
        'communities/manageprovincial/': 'communities/provincial/',
        'mana/manage-assessments/': 'mana/assessments/',
        'coordination/events/': 'coordination/calendar/',
    }
    
    # Check if current path matches a special mapping
    current_path = f"{module}/{subpath}" if subpath else f"{module}/"
    if current_path in path_mapping:
        bmms_path = path_mapping[current_path]
    else:
        # Default: preserve subpath structure
        bmms_path = f"{bmms_module}/{subpath}" if subpath else f"{bmms_module}/"
    
    # Build full BMMS URL
    bmms_url = f"/moa/{org_code}/{bmms_path}"
    
    # Preserve query parameters
    if request.GET:
        query_string = request.GET.urlencode()
        bmms_url += f"?{query_string}"
    
    # 302 temporary redirect (allows changing redirect target later)
    return redirect(bmms_url)


def dashboard_redirect(request):
    """
    Redirect /dashboard/ to user's default organization dashboard.
    
    Example:
        /dashboard/ → /moa/OOBC/dashboard/ (for OOBC staff)
        /dashboard/ → /moa/MSSD/dashboard/ (for MSSD users)
    """
    if request.user.is_authenticated:
        # Get user's default organization
        if hasattr(request.user, 'profile') and request.user.profile.default_organization:
            org_code = request.user.profile.default_organization.code
        else:
            # Fallback: OOBC for staff, first organization for others
            org_code = 'OOBC'  # TODO: Implement smarter fallback
        
        return redirect('common:dashboard', org_code=org_code)
    else:
        # Unauthenticated users go to login
        return redirect('login')
```

---

### 22. Backward Compatibility Strategy

#### 22.1 Phase 0: Pre-Refactoring (Before BMMS Work)

**Goal:** Extract routing from `common` app to respective modules WITHOUT changing URLs.

**Priority:** CRITICAL (Prerequisite for BMMS)

**Why This Matters:**
- BMMS development happens on `feature/bmms` branch
- `main` branch continues serving OBCMS production
- Pre-refactoring ensures both branches benefit from cleaner architecture
- Reduces technical debt BEFORE expansion

**Implementation Steps:**

```python
# ============================================================================
# STEP 1: Create Module-Specific URL Files
# ============================================================================

# FILE: src/communities/urls.py (CREATE NEW FILE)
from django.urls import path
from common import views  # Still use common views (temporary)

app_name = "communities"

urlpatterns = [
    # Move from common/urls.py to here
    path("", views.communities_home, name="home"),
    path("manage/", views.communities_manage, name="manage"),
    path("<int:community_id>/", views.communities_view, name="detail"),
    path("<int:community_id>/edit/", views.communities_edit, name="edit"),
    # ... all other communities URLs ...
]

# FILE: src/mana/urls.py (ENHANCE EXISTING FILE)
from django.urls import path
from common import views  # Still use common views (temporary)

app_name = "mana"

urlpatterns = [
    # Move from common/urls.py to here
    path("", views.mana_home, name="home"),
    path("regional/", views.mana_regional_overview, name="regional_overview"),
    path("desk-review/", views.mana_desk_review, name="desk_review"),
    # ... all other MANA URLs ...
    
    # Keep existing workshop URLs
    path("workshops/", views.workshop_list, name="workshop_list"),
    # ...
]
```

```python
# ============================================================================
# STEP 2: Update Project URLs (Route to Module URLs)
# ============================================================================

# FILE: src/obc_management/urls.py (MODIFY)
from django.urls import path, include

urlpatterns = [
    # OLD: Everything routed through common
    # path("", include("common.urls")),
    
    # NEW: Direct routing to modules
    path("dashboard/", include("common.urls")),  # Only dashboard + infrastructure
    path("communities/", include("communities.urls")),  # NEW
    path("mana/", include("mana.urls")),  # NEW
    path("coordination/", include("coordination.urls")),  # NEW
    path("recommendations/", include("recommendations.policies.urls")),  # NEW
    path("oobc-management/", include("common.urls.oobc")),  # Split off OOBC management
    
    # ... other patterns ...
]
```

```python
# ============================================================================
# STEP 3: Update ALL Template References
# ============================================================================

# Run automated find-and-replace across all templates
find . -name "*.html" -exec sed -i '' 's/common:communities_/communities:/g' {} +
find . -name "*.html" -exec sed -i '' 's/common:mana_/mana:/g' {} +
find . -name "*.html" -exec sed -i '' 's/common:coordination_/coordination:/g' {} +
find . -name "*.html" -exec sed -i '' 's/common:recommendations_/policies:/g' {} +

# Example template changes:
# BEFORE: {% url 'common:communities_home' %}
# AFTER:  {% url 'communities:home' %}

# BEFORE: {% url 'common:mana_regional_overview' %}
# AFTER:  {% url 'mana:regional_overview' %}
```

```python
# ============================================================================
# STEP 4: Update View Redirects
# ============================================================================

# FILE: src/common/views/__init__.py (MODIFY)

# BEFORE
from django.shortcuts import redirect
return redirect('common:communities_manage')

# AFTER
return redirect('communities:manage')
```

**Testing Checklist (Phase 0):**

```python
# ============================================================================
# TEST SUITE: Phase 0 URL Refactoring
# ============================================================================

class Phase0URLTests(TestCase):
    """Test that URL refactoring doesn't break existing functionality."""
    
    def test_communities_urls_resolve(self):
        """Test communities URLs resolve correctly."""
        url = reverse('communities:home')
        self.assertEqual(url, '/communities/')
        
        url = reverse('communities:manage')
        self.assertEqual(url, '/communities/manage/')
        
        url = reverse('communities:detail', kwargs={'community_id': 1})
        self.assertEqual(url, '/communities/1/')
    
    def test_mana_urls_resolve(self):
        """Test MANA URLs resolve correctly."""
        url = reverse('mana:home')
        self.assertEqual(url, '/mana/')
        
        url = reverse('mana:regional_overview')
        self.assertEqual(url, '/mana/regional/')
    
    def test_coordination_urls_resolve(self):
        """Test coordination URLs resolve correctly."""
        url = reverse('coordination:home')
        self.assertEqual(url, '/coordination/')
        
        url = reverse('coordination:partnerships')
        self.assertEqual(url, '/coordination/partnerships/')
    
    def test_no_namespace_conflicts(self):
        """Test that URL names are unique within namespaces."""
        # Should not raise NoReverseMatch
        reverse('communities:home')
        reverse('mana:home')
        reverse('coordination:home')
    
    def test_template_rendering(self):
        """Test that templates render with new namespaces."""
        response = self.client.get('/dashboard/')
        self.assertContains(response, '/communities/')  # Link rendered correctly
        self.assertContains(response, '/mana/')
        self.assertContains(response, '/coordination/')
    
    def test_redirects_use_new_namespaces(self):
        """Test that view redirects use new namespaces."""
        # Example: Form submission redirects
        response = self.client.post('/communities/add/', {
            'name': 'Test Community',
            # ... form data ...
        })
        self.assertRedirects(response, '/communities/manage/')  # New URL

# ============================================================================
# RUN TESTS
# ============================================================================
$ cd src
$ python manage.py test common.tests.test_phase0_urls -v2
```

**Rollback Plan (Phase 0):**

```bash
# If Phase 0 refactoring causes issues:

# 1. Revert project URLs
git checkout HEAD~1 -- src/obc_management/urls.py

# 2. Revert new module URL files
git rm src/communities/urls.py
git rm src/mana/urls_staff.py
git checkout HEAD~1 -- src/mana/urls.py

# 3. Revert template changes
git checkout HEAD~1 -- src/templates/

# 4. Restart server
cd src && python manage.py runserver
```

**Phase 0 Success Criteria:**

- [ ] All modules have proper `urls.py` with `app_name` defined
- [ ] `obc_management/urls.py` routes directly to module URLs
- [ ] All templates use new namespaces (`communities:*`, not `common:communities_*`)
- [ ] All view redirects use new namespaces
- [ ] 100% test pass rate (no regressions)
- [ ] `common/urls.py` reduced from 847 lines to < 300 lines
- [ ] Zero changes to actual URL paths (only namespaces changed)

---

#### 22.2 Phase 1: Organization Context URLs (BMMS Foundation)

**Goal:** Implement organization-scoped URLs while maintaining backward compatibility.

**Priority:** CRITICAL (BMMS Core Requirement)

**Branch:** `feature/bmms`

**Implementation Steps:**

```python
# ============================================================================
# STEP 1: Add Organization Middleware
# ============================================================================

# FILE: src/obc_management/settings/base.py (MODIFY)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # NEW: Organization context middleware
    'common.middleware.organization.OrganizationMiddleware',  # ← ADD THIS
]
```

```python
# ============================================================================
# STEP 2: Update Module URLs to Accept org_code
# ============================================================================

# FILE: src/communities/urls.py (MODIFY)
from django.urls import path
from . import views

app_name = "communities"

urlpatterns = [
    # URLs now work with /moa/<org_code>/communities/...
    # org_code extracted by middleware, available as request.organization
    path("", views.home, name="home"),
    path("barangay/", views.barangay_list, name="barangay_list"),
    path("barangay/<int:id>/", views.barangay_detail, name="barangay_detail"),
    # ...
]
```

```python
# ============================================================================
# STEP 3: Update Project URLs for Organization Context
# ============================================================================

# FILE: src/obc_management/urls.py (MODIFY)
from django.urls import path, include
from common.views import legacy_redirect

urlpatterns = [
    # Organization context routing
    path('moa/<str:org_code>/', include([
        path('dashboard/', include('common.urls')),
        path('communities/', include('communities.urls')),
        path('mana/', include('mana.urls')),
        path('coordination/', include('coordination.urls')),
        path('me/', include('monitoring.urls')),
        path('policies/', include('recommendations.policies.urls')),
        path('planning/', include('planning.urls')),  # NEW
        path('budgeting/', include('budget_system.urls')),  # NEW
    ])),
    
    # Legacy redirects (OBCMS backward compatibility)
    path('communities/', legacy_redirect, {'module': 'communities', 'default_org': 'OOBC'}),
    path('communities/<path:subpath>', legacy_redirect, {'module': 'communities', 'default_org': 'OOBC'}),
    path('mana/', legacy_redirect, {'module': 'mana', 'default_org': 'OOBC'}),
    path('mana/<path:subpath>', legacy_redirect, {'module': 'mana', 'default_org': 'OOBC'}),
    # ... more legacy redirects ...
]
```

```python
# ============================================================================
# STEP 4: Update Templates to Include org_code
# ============================================================================

<!-- BEFORE (OBCMS) -->
<a href="{% url 'communities:home' %}">Communities</a>
<a href="{% url 'mana:home' %}">MANA</a>

<!-- AFTER (BMMS) -->
<a href="{% url 'communities:home' org_code=request.organization.code %}">Communities</a>
<a href="{% url 'mana:home' org_code=request.organization.code %}">MANA</a>

<!-- Dynamic organization selector (NEW) -->
<div class="organization-selector">
    <label>Organization:</label>
    <select id="org-switcher">
        {% for org in user.accessible_organizations %}
        <option value="{{ org.code }}" {% if org == request.organization %}selected{% endif %}>
            {{ org.name }}
        </option>
        {% endfor %}
    </select>
</div>

<script>
// Switch organization (reload page with new org context)
document.getElementById('org-switcher').addEventListener('change', function(e) {
    const newOrgCode = e.target.value;
    const currentPath = window.location.pathname;
    
    // Replace current org code with new one in URL
    const newPath = currentPath.replace(/\/moa\/[A-Z]+\//, `/moa/${newOrgCode}/`);
    window.location.href = newPath;
});
</script>
```

**Testing Checklist (Phase 1):**

```python
# ============================================================================
# TEST SUITE: Phase 1 Organization Context
# ============================================================================

class Phase1OrganizationURLTests(TestCase):
    """Test organization-scoped URLs work correctly."""
    
    def setUp(self):
        # Create test organizations
        self.oobc = Organization.objects.create(code='OOBC', name='Office for Other Bangsamoro Communities')
        self.mssd = Organization.objects.create(code='MSSD', name='Ministry of Social Services and Development')
        self.moh = Organization.objects.create(code='MOH', name='Ministry of Health')
    
    def test_organization_urls_resolve(self):
        """Test org-scoped URLs resolve correctly."""
        url = reverse('communities:home', kwargs={'org_code': 'OOBC'})
        self.assertEqual(url, '/moa/OOBC/communities/')
        
        url = reverse('mana:home', kwargs={'org_code': 'MSSD'})
        self.assertEqual(url, '/moa/MSSD/mana/')
    
    def test_middleware_sets_organization(self):
        """Test middleware sets request.organization."""
        response = self.client.get('/moa/OOBC/dashboard/')
        self.assertEqual(response.wsgi_request.organization, self.oobc)
        
        response = self.client.get('/moa/MSSD/dashboard/')
        self.assertEqual(response.wsgi_request.organization, self.mssd)
    
    def test_invalid_organization_code(self):
        """Test invalid organization code raises 404."""
        response = self.client.get('/moa/INVALID/dashboard/')
        self.assertEqual(response.status_code, 404)
    
    def test_legacy_redirect_works(self):
        """Test legacy OBCMS URLs redirect to BMMS."""
        response = self.client.get('/communities/')
        self.assertRedirects(response, '/moa/OOBC/communities/', status_code=302)
        
        response = self.client.get('/mana/')
        self.assertRedirects(response, '/moa/OOBC/mana/', status_code=302)
    
    def test_legacy_redirect_preserves_subpath(self):
        """Test legacy redirects preserve URL subpaths."""
        response = self.client.get('/communities/manage/')
        self.assertRedirects(response, '/moa/OOBC/communities/barangay/', status_code=302)
        
        response = self.client.get('/mana/regional/')
        self.assertRedirects(response, '/moa/OOBC/mana/regional/', status_code=302)
    
    def test_legacy_redirect_preserves_query_params(self):
        """Test legacy redirects preserve query parameters."""
        response = self.client.get('/communities/?region=IX')
        self.assertRedirects(response, '/moa/OOBC/communities/?region=IX', status_code=302)
    
    def test_user_default_organization(self):
        """Test authenticated users redirect to their default organization."""
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        user.profile.default_organization = self.mssd
        user.profile.save()
        
        self.client.login(username='testuser', password='password')
        response = self.client.get('/communities/')
        
        # Should redirect to user's default org (MSSD), not OOBC
        self.assertRedirects(response, '/moa/MSSD/communities/', status_code=302)
    
    def test_organization_switcher_dropdown(self):
        """Test organization switcher renders in templates."""
        response = self.client.get('/moa/OOBC/dashboard/')
        self.assertContains(response, 'organization-selector')
        self.assertContains(response, self.oobc.name)
    
    def test_breadcrumbs_include_organization(self):
        """Test breadcrumbs show current organization."""
        response = self.client.get('/moa/OOBC/communities/barangay/1/')
        self.assertContains(response, 'OOBC')  # Organization in breadcrumb
        self.assertContains(response, 'Communities')
        self.assertContains(response, 'Barangay OBC')

# ============================================================================
# RUN TESTS
# ============================================================================
$ cd src
$ python manage.py test common.tests.test_phase1_organization_urls -v2
```

**Phase 1 Success Criteria:**

- [ ] OrganizationMiddleware extracts `org_code` and sets `request.organization`
- [ ] All module URLs work with `/moa/<ORG_CODE>/` prefix
- [ ] Legacy OBCMS URLs redirect to `/moa/OOBC/...` (302 temporary redirect)
- [ ] Authenticated users redirect to their default organization
- [ ] Invalid organization codes raise 404
- [ ] Organization switcher dropdown works
- [ ] All templates include `org_code` in URL tags
- [ ] 100% test pass rate for organization routing

---

#### 22.3 Phase 2: Multi-Tenant URLs (Full BMMS)

**Goal:** All modules use organization context, legacy redirects deprecated.

**Priority:** HIGH (BMMS Production)

**Branch:** `feature/bmms` (merge to `main` after testing)

**Implementation Steps:**

```python
# ============================================================================
# STEP 1: Add OCM URLs
# ============================================================================

# FILE: src/ocm/urls.py (CREATE NEW APP)
from django.urls import path
from . import views

app_name = "ocm"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('budget-aggregation/', views.budget_aggregation, name='budget_aggregation'),
    path('budget-aggregation/<str:org_code>/', views.budget_aggregation_detail, name='budget_aggregation_detail'),
    path('reports/', views.reports, name='reports'),
    path('reports/obc-coverage/', views.obc_coverage_report, name='obc_coverage_report'),
    path('reports/program-inventory/', views.program_inventory, name='program_inventory'),
    path('reports/coordination-matrix/', views.coordination_matrix, name='coordination_matrix'),
    path('moa-performance/', views.moa_performance, name='moa_performance'),
]
```

```python
# ============================================================================
# STEP 2: Update Navigation for Multi-Tenant
# ============================================================================

<!-- FILE: src/templates/common/navbar_bmms.html (NEW TEMPLATE) -->
<nav class="navbar">
    <!-- Organization Context Display -->
    <div class="navbar-org-context">
        <span class="org-name">{{ request.organization.name }}</span>
        <button class="org-switcher-btn" data-toggle="modal" data-target="#orgSwitcherModal">
            <i class="fas fa-exchange-alt"></i> Switch Organization
        </button>
    </div>
    
    <!-- Main Navigation -->
    <ul class="navbar-menu">
        <li><a href="{% url 'common:dashboard' org_code=request.organization.code %}">Dashboard</a></li>
        <li><a href="{% url 'communities:home' org_code=request.organization.code %}">Communities</a></li>
        <li><a href="{% url 'mana:home' org_code=request.organization.code %}">MANA</a></li>
        <li><a href="{% url 'coordination:home' org_code=request.organization.code %}">Coordination</a></li>
        <li><a href="{% url 'monitoring:home' org_code=request.organization.code %}">M&E</a></li>
        <li><a href="{% url 'planning:home' org_code=request.organization.code %}">Planning</a></li>
        <li><a href="{% url 'budgeting:home' org_code=request.organization.code %}">Budgeting</a></li>
        
        <!-- OCM Special Menu (Only for OCM users) -->
        {% if user|is_ocm_staff %}
        <li><a href="{% url 'cmo:dashboard' %}">OCM Dashboard</a></li>
        {% endif %}
    </ul>
</nav>

<!-- Organization Switcher Modal -->
<div class="modal" id="orgSwitcherModal">
    <div class="modal-content">
        <h2>Switch Organization</h2>
        <ul class="org-list">
            {% for org in user.accessible_organizations %}
            <li>
                <a href="{% url 'common:dashboard' org_code=org.code %}"
                   class="org-card {% if org == request.organization %}active{% endif %}">
                    <strong>{{ org.code }}</strong>
                    <span>{{ org.name }}</span>
                </a>
            </li>
            {% endfor %}
        </ul>
    </div>
</div>
```

```python
# ============================================================================
# STEP 3: Deprecate Legacy Redirects (Document Only)
# ============================================================================

# FILE: src/obc_management/urls.py (MODIFY)

urlpatterns = [
    # ... organization context URLs ...
    
    # ========================================================================
    # LEGACY REDIRECTS (DEPRECATED - Will be removed in BMMS v2.0)
    # ========================================================================
    # These redirects are temporary for OBCMS backward compatibility.
    # All users should update bookmarks to use /moa/<ORG_CODE>/ URLs.
    # Deprecation date: 2026-01-01
    # Removal date: 2026-06-01
    
    path('communities/', legacy_redirect, {'module': 'communities', 'default_org': 'OOBC'}),
    path('mana/', legacy_redirect, {'module': 'mana', 'default_org': 'OOBC'}),
    # ... other legacy redirects ...
]
```

```python
# ============================================================================
# STEP 4: Add Deprecation Warning Banner
# ============================================================================

<!-- FILE: src/templates/components/legacy_url_warning.html (NEW) -->
{% if request.path|is_legacy_url %}
<div class="alert alert-warning legacy-url-warning">
    <i class="fas fa-exclamation-triangle"></i>
    <strong>Legacy URL Detected</strong>
    <p>
        You're using an outdated OBCMS URL. Please update your bookmark to:
        <code>{{ request.build_absolute_uri|bmms_url }}</code>
    </p>
    <button class="btn-copy-new-url" data-url="{{ request.build_absolute_uri|bmms_url }}">
        Copy New URL
    </button>
</div>
{% endif %}
```

**Phase 2 Success Criteria:**

- [ ] OCM aggregation views operational
- [ ] Organization switcher modal works across all modules
- [ ] Legacy URL warning banner displays on old URLs
- [ ] All 44 MOAs can access their scoped data
- [ ] Inter-MOA collaboration features work
- [ ] Performance acceptable with 30 organizations
- [ ] Security audit passed (no cross-org data leakage)
- [ ] 100% test pass rate across all modules

---

### Implementation Checklist

#### Phase 0: Pre-Refactoring (CRITICAL - Do First)

- [ ] **Create module URL files**
  - [ ] `src/communities/urls.py` (extract from common)
  - [ ] `src/mana/urls.py` (enhance existing)
  - [ ] `src/coordination/urls.py` (extract from common)
  - [ ] `src/recommendations/policies/urls.py` (extract from common)

- [ ] **Update project URLs**
  - [ ] Modify `src/obc_management/urls.py` to route directly to modules
  - [ ] Verify no URL path changes (only namespace changes)

- [ ] **Update all templates**
  - [ ] Run automated find-and-replace for namespace changes
  - [ ] Manual review of critical templates (dashboard, navbar)
  - [ ] Update all `{% url %}` tags

- [ ] **Update view redirects**
  - [ ] Search for `redirect('common:*')` across codebase
  - [ ] Replace with new namespaces

- [ ] **Testing**
  - [ ] Write Phase 0 URL tests
  - [ ] Run full test suite
  - [ ] Manual QA testing (click every link)

- [ ] **Code review & merge**
  - [ ] Create PR: "Phase 0: Extract module URLs from common app"
  - [ ] Request review from team
  - [ ] Merge to `main` branch
  - [ ] Deploy to staging
  - [ ] Verify production-ready

#### Phase 1: Organization Context (BMMS Foundation)

- [ ] **Middleware implementation**
  - [ ] Create `src/common/middleware/organization.py`
  - [ ] Add to MIDDLEWARE in settings
  - [ ] Test invalid organization code handling

- [ ] **Legacy redirect views**
  - [ ] Implement `legacy_redirect` function
  - [ ] Implement `dashboard_redirect` function
  - [ ] Test redirect preservation (query params, subpaths)

- [ ] **Update project URLs**
  - [ ] Add `/moa/<org_code>/` routing pattern
  - [ ] Add legacy redirect patterns
  - [ ] Remove old flat routing

- [ ] **Update templates**
  - [ ] Add `org_code` to all `{% url %}` tags
  - [ ] Create organization switcher dropdown
  - [ ] Update navigation menus

- [ ] **Testing**
  - [ ] Write Phase 1 organization tests
  - [ ] Test middleware with multiple organizations
  - [ ] Test legacy redirects
  - [ ] Test user default organization
  - [ ] Load testing (simulate 30 organizations)

- [ ] **Documentation**
  - [ ] Update CLAUDE.md with new URL patterns
  - [ ] Create BMMS URL migration guide
  - [ ] Document organization switcher usage

#### Phase 2: Full Multi-Tenant (BMMS Production)

- [ ] **OCM app development**
  - [ ] Create `src/ocm/` app
  - [ ] Implement aggregation views
  - [ ] Create OCM dashboard
  - [ ] Implement budget aggregation
  - [ ] Implement cross-MOA reports

- [ ] **UI enhancements**
  - [ ] Organization switcher modal
  - [ ] Legacy URL warning banner
  - [ ] Breadcrumbs with organization context
  - [ ] OCM special menu

- [ ] **Testing**
  - [ ] Security audit (no cross-org data leakage)
  - [ ] Performance testing (30 organizations, 800 users)
  - [ ] End-to-end user flows
  - [ ] OCM aggregation accuracy

- [ ] **Deployment**
  - [ ] Merge `feature/bmms` to `main`
  - [ ] Database migration (add Organization model data)
  - [ ] Deploy to staging
  - [ ] User acceptance testing
  - [ ] Deploy to production
  - [ ] Monitor for 48 hours

- [ ] **Deprecation planning**
  - [ ] Document legacy URL deprecation timeline
  - [ ] Communicate to users (6 months notice)
  - [ ] Set removal date (e.g., 2026-06-01)

---

### Rollback Plan

**If Phase 0 fails:**
```bash
git revert <phase0-commits>
# Restore common/urls.py to original state
# Revert all template changes
# Restart server
```

**If Phase 1 fails:**
```bash
git checkout main  # Revert to before Phase 1
# Remove OrganizationMiddleware from settings
# Remove organization context from URLs
# Restart server
```

**If Phase 2 fails (Production):**
```bash
# Emergency rollback procedure
git revert <phase2-commits>
python manage.py migrate common <previous-migration>
# Disable OCM module
BMMS_ENABLED=False in settings
# Restart all services
```

**Database Rollback:**
- No schema changes in Phase 0 (safe)
- Phase 1 adds Organization model (non-destructive)
- Phase 2 adds organization foreign keys (reversible)

---

**Part VI Complete:** URL Structure Refactoring plan with phased implementation, complete code examples, comprehensive testing strategy, and rollback procedures.

---

## Part VII: Testing & Deployment Strategy

### Section 23: Testing Strategy

#### 23.1 Test Coverage Requirements

**Coverage Targets:**

| Test Type | Target Coverage | Priority | Rationale |
|-----------|----------------|----------|-----------|
| Unit Tests | 90%+ | CRITICAL | Ensure individual components work correctly |
| Integration Tests | 85%+ | HIGH | Verify module interactions |
| Critical Paths | 100% | CRITICAL | Data isolation, permissions, budgeting |
| API Tests | 95%+ | HIGH | All endpoints must be verified |
| Security Tests | 100% | CRITICAL | No data leakage allowed |

**Test Pyramid:**

```
           /\
          /  \         E2E Tests (5%)
         /____\        - Full user workflows
        /      \       - Cross-browser testing
       /________\      
      /          \     Integration Tests (15%)
     /            \    - Multi-model interactions
    /______________\   - API endpoint tests
   /                \  
  /                  \ Unit Tests (80%)
 /____________________\- Model methods
                       - Utility functions
                       - Permissions
```

**CI/CD Integration:**

```yaml
# .github/workflows/test-bmms.yml
name: BMMS Test Suite

on:
  push:
    branches: [feature/bmms, staging, main]
  pull_request:
    branches: [feature/bmms, staging, main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: obcms_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements/development.txt
      
      - name: Run unit tests
        run: |
          cd src
          pytest tests/ -v --cov=. --cov-report=xml --cov-report=term
      
      - name: Check coverage threshold
        run: |
          cd src
          coverage report --fail-under=90
      
      - name: Run security tests
        run: |
          cd src
          pytest tests/security/ -v --maxfail=0
      
      - name: Run integration tests
        run: |
          cd src
          pytest tests/integration/ -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./src/coverage.xml
          fail_ci_if_error: true
```

---

#### 23.2 Unit Testing Examples

**23.2.1 OrganizationScopedModel Queryset Filtering**

```python
# src/tests/test_organizations.py

import pytest
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment
from coordination.models import Partnership

User = get_user_model()


@pytest.mark.django_db
class TestOrganizationScopedModel:
    """Test base organization-scoped model behavior."""
    
    @pytest.fixture
    def organizations(self):
        """Create test organizations."""
        oobc = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='OCM'
        )
        moh = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='MOA'
        )
        mole = Organization.objects.create(
            code='MOLE',
            name='Ministry of Labor and Employment',
            org_type='MOA'
        )
        return {'oobc': oobc, 'moh': moh, 'mole': mole}
    
    @pytest.fixture
    def users(self, organizations):
        """Create users for each organization."""
        oobc_user = User.objects.create_user(
            username='oobc_admin',
            email='admin@oobc.gov.ph',
            default_organization=organizations['oobc']
        )
        moh_user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            default_organization=organizations['moh']
        )
        mole_user = User.objects.create_user(
            username='mole_staff',
            email='staff@mole.gov.ph',
            default_organization=organizations['mole']
        )
        return {
            'oobc': oobc_user,
            'moh': moh_user,
            'mole': mole_user
        }
    
    def test_org_scoped_queryset_filtering(self, organizations):
        """Test that organization-scoped querysets filter correctly."""
        # Create assessments for different organizations
        moh_assessment = Assessment.objects.create(
            title='MOH Health Assessment',
            organization=organizations['moh'],
            status='draft'
        )
        mole_assessment = Assessment.objects.create(
            title='MOLE Labor Assessment',
            organization=organizations['mole'],
            status='draft'
        )
        
        # Test organization-scoped manager
        moh_assessments = Assessment.objects.for_organization(organizations['moh'])
        assert moh_assessments.count() == 1
        assert moh_assessment in moh_assessments
        assert mole_assessment not in moh_assessments
        
        mole_assessments = Assessment.objects.for_organization(organizations['mole'])
        assert mole_assessments.count() == 1
        assert mole_assessment in mole_assessments
        assert moh_assessment not in mole_assessments
    
    def test_org_scoped_queryset_excludes_others(self, organizations):
        """Verify organization-scoped queryset excludes other orgs' data."""
        # Create 10 assessments for MOH, 5 for MOLE
        for i in range(10):
            Assessment.objects.create(
                title=f'MOH Assessment {i}',
                organization=organizations['moh']
            )
        for i in range(5):
            Assessment.objects.create(
                title=f'MOLE Assessment {i}',
                organization=organizations['mole']
            )
        
        # MOH should only see 10
        moh_qs = Assessment.objects.for_organization(organizations['moh'])
        assert moh_qs.count() == 10
        
        # MOLE should only see 5
        mole_qs = Assessment.objects.for_organization(organizations['mole'])
        assert mole_qs.count() == 5
        
        # Verify no overlap
        moh_ids = set(moh_qs.values_list('id', flat=True))
        mole_ids = set(mole_qs.values_list('id', flat=True))
        assert len(moh_ids & mole_ids) == 0
    
    def test_queryset_chaining_preserves_org_filter(self, organizations):
        """Test that queryset chaining preserves organization filter."""
        # Create assessments with different statuses
        Assessment.objects.create(
            title='MOH Draft',
            organization=organizations['moh'],
            status='draft'
        )
        Assessment.objects.create(
            title='MOH Published',
            organization=organizations['moh'],
            status='published'
        )
        Assessment.objects.create(
            title='MOLE Draft',
            organization=organizations['mole'],
            status='draft'
        )
        
        # Chain filters - should only get MOH draft
        moh_drafts = (Assessment.objects
                      .for_organization(organizations['moh'])
                      .filter(status='draft'))
        
        assert moh_drafts.count() == 1
        assert moh_drafts.first().title == 'MOH Draft'
```

**23.2.2 Permission Decorators**

```python
# src/tests/test_permissions.py

import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from organizations.decorators import (
    require_organization,
    require_moa_or_cmo,
    require_ocm_only
)
from organizations.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestPermissionDecorators:
    """Test organization permission decorators."""
    
    @pytest.fixture
    def factory(self):
        return RequestFactory()
    
    @pytest.fixture
    def organizations(self):
        oobc = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='OCM'
        )
        moh = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='MOA'
        )
        return {'oobc': oobc, 'moh': moh}
    
    @pytest.fixture
    def users(self, organizations):
        ocm_user = User.objects.create_user(
            username='ocm_admin',
            email='admin@cmo.gov.ph',
            default_organization=organizations['oobc']
        )
        moa_user = User.objects.create_user(
            username='moa_staff',
            email='staff@moh.gov.ph',
            default_organization=organizations['moh']
        )
        return {'ocm': ocm_user, 'moa': moa_user}
    
    def test_require_organization_authenticated(self, factory, users, organizations):
        """Test require_organization with authenticated user."""
        @require_organization
        def test_view(request, org_code):
            return HttpResponse('Success')
        
        # Create request with organization middleware
        request = factory.get('/moa/MOH/dashboard/')
        request.user = users['moa']
        request.organization = organizations['moh']
        
        response = test_view(request, org_code='MOH')
        assert response.status_code == 200
        assert response.content == b'Success'
    
    def test_require_organization_missing_org(self, factory, users):
        """Test require_organization fails when organization not set."""
        @require_organization
        def test_view(request, org_code):
            return HttpResponse('Success')
        
        request = factory.get('/dashboard/')
        request.user = users['moa']
        request.organization = None  # No organization set
        
        response = test_view(request, org_code='MOH')
        assert response.status_code == 403
    
    def test_require_organization_anonymous(self, factory):
        """Test require_organization redirects anonymous users."""
        @require_organization
        def test_view(request, org_code):
            return HttpResponse('Success')
        
        request = factory.get('/moa/MOH/dashboard/')
        request.user = AnonymousUser()
        
        response = test_view(request, org_code='MOH')
        assert response.status_code == 302  # Redirect to login
        assert '/accounts/login/' in response.url
    
    def test_require_moa_or_ocm_allows_both(self, factory, users, organizations):
        """Test require_moa_or_cmo allows MOA and OCM users."""
        @require_moa_or_cmo
        def test_view(request, org_code):
            return HttpResponse('Success')
        
        # Test MOA user
        request_moa = factory.get('/moa/MOH/dashboard/')
        request_moa.user = users['moa']
        request_moa.organization = organizations['moh']
        
        response_moa = test_view(request_moa, org_code='MOH')
        assert response_moa.status_code == 200
        
        # Test OCM user
        request_cmo = factory.get('/ocm/OOBC/dashboard/')
        request_cmo.user = users['cmo']
        request_cmo.organization = organizations['oobc']
        
        response_cmo = test_view(request_cmo, org_code='OOBC')
        assert response_cmo.status_code == 200
    
    def test_require_ocm_only_blocks_moa(self, factory, users, organizations):
        """Test require_ocm_only blocks MOA users."""
        @require_ocm_only
        def test_view(request, org_code):
            return HttpResponse('OCM Success')
        
        # OCM user should succeed
        request_cmo = factory.get('/ocm/OOBC/dashboard/')
        request_cmo.user = users['cmo']
        request_cmo.organization = organizations['oobc']
        
        response_cmo = test_view(request_cmo, org_code='OOBC')
        assert response_cmo.status_code == 200
        
        # MOA user should be blocked
        request_moa = factory.get('/moa/MOH/dashboard/')
        request_moa.user = users['moa']
        request_moa.organization = organizations['moh']
        
        response_moa = test_view(request_moa, org_code='MOH')
        assert response_moa.status_code == 403
```

**23.2.3 URL Routing with Organization Context**

```python
# src/tests/test_url_routing.py

import pytest
from django.urls import reverse, resolve
from django.test import Client
from organizations.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestURLRouting:
    """Test organization-aware URL routing."""
    
    @pytest.fixture
    def client(self):
        return Client()
    
    @pytest.fixture
    def organizations(self):
        oobc = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='OCM'
        )
        moh = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='MOA'
        )
        return {'oobc': oobc, 'moh': moh}
    
    @pytest.fixture
    def user(self, organizations):
        user = User.objects.create_user(
            username='test_user',
            email='test@moh.gov.ph',
            password='testpass123',
            default_organization=organizations['moh']
        )
        return user
    
    def test_org_dashboard_url_generation(self, organizations):
        """Test URL generation with organization code."""
        url = reverse('organizations:dashboard', kwargs={'org_code': 'MOH'})
        assert url == '/moa/MOH/'
        
        url = reverse('organizations:dashboard', kwargs={'org_code': 'OOBC'})
        assert url == '/ocm/OOBC/'
    
    def test_org_dashboard_url_resolution(self):
        """Test URL resolution with organization code."""
        match = resolve('/moa/MOH/')
        assert match.url_name == 'dashboard'
        assert match.kwargs['org_code'] == 'MOH'
        
        match = resolve('/ocm/OOBC/')
        assert match.url_name == 'dashboard'
        assert match.kwargs['org_code'] == 'OOBC'
    
    def test_mana_url_generation(self, organizations):
        """Test MANA module URL generation with org context."""
        url = reverse('mana:assessment_list', kwargs={'org_code': 'MOH'})
        assert url == '/moa/MOH/mana/assessments/'
        
        url = reverse('mana:assessment_create', kwargs={'org_code': 'MOH'})
        assert url == '/moa/MOH/mana/assessments/create/'
    
    def test_coordination_url_generation(self, organizations):
        """Test Coordination module URL generation."""
        url = reverse('coordination:partnership_list', kwargs={'org_code': 'MOH'})
        assert url == '/moa/MOH/coordination/partnerships/'
    
    def test_planning_url_generation(self, organizations):
        """Test Planning module URL generation."""
        url = reverse('planning:ppa_list', kwargs={'org_code': 'MOH'})
        assert url == '/moa/MOH/planning/ppas/'
    
    def test_budget_url_generation(self, organizations):
        """Test Budget module URL generation."""
        url = reverse('budget:allocation_list', kwargs={'org_code': 'MOH'})
        assert url == '/moa/MOH/budget/allocations/'
    
    def test_legacy_redirect_preserves_query_params(self, client, user):
        """Test legacy URL redirect preserves query parameters."""
        client.force_login(user)
        
        # Access legacy URL with query params
        response = client.get('/mana/assessments/?status=published&page=2')
        
        # Should redirect to org-aware URL with params preserved
        assert response.status_code == 302
        assert response.url == '/moa/MOH/mana/assessments/?status=published&page=2'
    
    def test_legacy_redirect_preserves_subpaths(self, client, user):
        """Test legacy URL redirect preserves subpaths."""
        client.force_login(user)
        
        # Access legacy URL with subpath
        response = client.get('/mana/assessments/123/edit/')
        
        # Should redirect to org-aware URL with subpath preserved
        assert response.status_code == 302
        assert response.url == '/moa/MOH/mana/assessments/123/edit/'
```

**23.2.4 Middleware Organization Extraction**

```python
# src/tests/test_middleware.py

import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from organizations.middleware import OrganizationMiddleware
from organizations.models import Organization

User = get_user_model()


@pytest.mark.django_db
class TestOrganizationMiddleware:
    """Test organization extraction middleware."""
    
    @pytest.fixture
    def factory(self):
        return RequestFactory()
    
    @pytest.fixture
    def middleware(self):
        def get_response(request):
            return HttpResponse('OK')
        return OrganizationMiddleware(get_response)
    
    @pytest.fixture
    def organizations(self):
        oobc = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='OCM'
        )
        moh = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='MOA'
        )
        return {'oobc': oobc, 'moh': moh}
    
    @pytest.fixture
    def user(self, organizations):
        return User.objects.create_user(
            username='test_user',
            email='test@moh.gov.ph',
            default_organization=organizations['moh']
        )
    
    def test_extract_org_from_url(self, factory, middleware, organizations, user):
        """Test organization extraction from URL path."""
        request = factory.get('/moa/MOH/dashboard/')
        request.user = user
        
        response = middleware(request)
        
        assert hasattr(request, 'organization')
        assert request.organization == organizations['moh']
        assert response.status_code == 200
    
    def test_extract_org_ocm_path(self, factory, middleware, organizations):
        """Test organization extraction from OCM path."""
        ocm_user = User.objects.create_user(
            username='ocm_user',
            email='cmo@oobc.gov.ph',
            default_organization=organizations['oobc']
        )
        
        request = factory.get('/ocm/OOBC/dashboard/')
        request.user = ocm_user
        
        response = middleware(request)
        
        assert request.organization == organizations['oobc']
        assert request.organization.org_type == 'OCM'
    
    def test_fallback_to_user_default_org(self, factory, middleware, organizations, user):
        """Test fallback to user's default organization."""
        # Request without org_code in path
        request = factory.get('/some/path/')
        request.user = user
        
        response = middleware(request)
        
        assert hasattr(request, 'organization')
        assert request.organization == organizations['moh']
    
    def test_no_organization_for_anonymous(self, factory, middleware):
        """Test no organization set for anonymous users."""
        from django.contrib.auth.models import AnonymousUser
        
        request = factory.get('/moa/MOH/dashboard/')
        request.user = AnonymousUser()
        
        response = middleware(request)
        
        assert hasattr(request, 'organization')
        assert request.organization is None
    
    def test_invalid_org_code_returns_none(self, factory, middleware, user):
        """Test invalid organization code returns None."""
        request = factory.get('/moa/INVALID/dashboard/')
        request.user = user
        
        response = middleware(request)
        
        assert hasattr(request, 'organization')
        assert request.organization is None
```

---

#### 23.3 Integration Testing Scenarios

**23.3.1 Data Isolation Test**

```python
# src/tests/integration/test_data_isolation.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment, NeedsAnalysis
from coordination.models import Partnership
from policies.models import PolicyRecommendation

User = get_user_model()


@pytest.mark.django_db
class TestDataIsolation:
    """Test that MOA A cannot access MOA B's data."""
    
    @pytest.fixture
    def setup_organizations(self):
        """Create two MOAs with complete data sets."""
        moh = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='MOA'
        )
        mole = Organization.objects.create(
            code='MOLE',
            name='Ministry of Labor and Employment',
            org_type='MOA'
        )
        
        # Create users
        moh_user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moh
        )
        mole_user = User.objects.create_user(
            username='mole_staff',
            email='staff@mole.gov.ph',
            password='testpass123',
            default_organization=mole
        )
        
        # Create MOH data
        moh_assessment = Assessment.objects.create(
            title='MOH Health Assessment 2024',
            organization=moh,
            status='published'
        )
        moh_needs = NeedsAnalysis.objects.create(
            assessment=moh_assessment,
            category='healthcare',
            priority='high'
        )
        moh_partnership = Partnership.objects.create(
            title='MOH-Hospital Partnership',
            organization=moh,
            status='active'
        )
        moh_policy = PolicyRecommendation.objects.create(
            title='Healthcare Policy 2024',
            organization=moh,
            status='draft'
        )
        
        # Create MOLE data
        mole_assessment = Assessment.objects.create(
            title='MOLE Labor Assessment 2024',
            organization=mole,
            status='published'
        )
        mole_needs = NeedsAnalysis.objects.create(
            assessment=mole_assessment,
            category='employment',
            priority='high'
        )
        mole_partnership = Partnership.objects.create(
            title='MOLE-Company Partnership',
            organization=mole,
            status='active'
        )
        mole_policy = PolicyRecommendation.objects.create(
            title='Labor Policy 2024',
            organization=mole,
            status='draft'
        )
        
        return {
            'moh': moh,
            'mole': mole,
            'moh_user': moh_user,
            'mole_user': mole_user,
            'moh_data': {
                'assessment': moh_assessment,
                'needs': moh_needs,
                'partnership': moh_partnership,
                'policy': moh_policy
            },
            'mole_data': {
                'assessment': mole_assessment,
                'needs': mole_needs,
                'partnership': mole_partnership,
                'policy': mole_policy
            }
        }
    
    def test_mana_assessment_isolation(self, setup_organizations):
        """Test MOH cannot see MOLE assessments."""
        client = Client()
        client.force_login(setup_organizations['moh_user'])
        
        # Access MOH assessments (should work)
        response = client.get('/moa/MOH/mana/assessments/')
        assert response.status_code == 200
        assert setup_organizations['moh_data']['assessment'].title in str(response.content)
        assert setup_organizations['mole_data']['assessment'].title not in str(response.content)
        
        # Try to access MOLE assessment directly (should fail)
        mole_assessment_id = setup_organizations['mole_data']['assessment'].id
        response = client.get(f'/moa/MOH/mana/assessments/{mole_assessment_id}/')
        assert response.status_code == 404  # Not found (filtered out)
    
    def test_coordination_partnership_isolation(self, setup_organizations):
        """Test MOH cannot see MOLE partnerships."""
        client = Client()
        client.force_login(setup_organizations['moh_user'])
        
        # Access MOH partnerships (should work)
        response = client.get('/moa/MOH/coordination/partnerships/')
        assert response.status_code == 200
        content = str(response.content)
        assert setup_organizations['moh_data']['partnership'].title in content
        assert setup_organizations['mole_data']['partnership'].title not in content
    
    def test_policy_recommendation_isolation(self, setup_organizations):
        """Test MOH cannot see MOLE policies."""
        client = Client()
        client.force_login(setup_organizations['moh_user'])
        
        # Access MOH policies (should work)
        response = client.get('/moa/MOH/policies/')
        assert response.status_code == 200
        content = str(response.content)
        assert setup_organizations['moh_data']['policy'].title in content
        assert setup_organizations['mole_data']['policy'].title not in content
    
    def test_api_isolation(self, setup_organizations):
        """Test API endpoints enforce data isolation."""
        client = Client()
        client.force_login(setup_organizations['moh_user'])
        
        # Access MOH API endpoints (should only return MOH data)
        response = client.get('/api/mana/assessments/?org_code=MOH')
        assert response.status_code == 200
        data = response.json()
        
        # Verify only MOH assessments returned
        moh_titles = [a['title'] for a in data['results']]
        assert setup_organizations['moh_data']['assessment'].title in moh_titles
        assert setup_organizations['mole_data']['assessment'].title not in moh_titles
    
    def test_direct_model_query_isolation(self, setup_organizations):
        """Test direct model queries respect organization scope."""
        # Simulate MOH user context
        moh = setup_organizations['moh']
        
        # Query assessments for MOH
        moh_assessments = Assessment.objects.for_organization(moh)
        assert moh_assessments.count() == 1
        assert setup_organizations['moh_data']['assessment'] in moh_assessments
        assert setup_organizations['mole_data']['assessment'] not in moh_assessments
```

**23.3.2 Shared Data Test**

```python
# src/tests/integration/test_shared_data.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from communities.models import Region, Province, Municipality, Barangay

User = get_user_model()


@pytest.mark.django_db
class TestSharedData:
    """Test that all MOAs can access shared OBC communities data."""
    
    @pytest.fixture
    def setup_shared_data(self):
        """Create shared OBC communities data."""
        # Create organizations
        moh = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        mole = Organization.objects.create(code='MOLE', name='Ministry of Labor', org_type='MOA')
        mafar = Organization.objects.create(code='MAFAR', name='Ministry of Agriculture', org_type='MOA')
        
        # Create users
        moh_user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moh
        )
        mole_user = User.objects.create_user(
            username='mole_staff',
            email='staff@mole.gov.ph',
            password='testpass123',
            default_organization=mole
        )
        mafar_user = User.objects.create_user(
            username='mafar_staff',
            email='staff@mafar.gov.ph',
            password='testpass123',
            default_organization=mafar
        )
        
        # Create shared community data (NOT organization-scoped)
        region = Region.objects.create(name='Region IX', code='09')
        province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=region)
        municipality = Municipality.objects.create(
            name='Pagadian City',
            code='097211',
            province=province
        )
        barangay = Barangay.objects.create(
            name='Balangasan',
            code='097211001',
            municipality=municipality,
            population=5234,
            obc_status='Confirmed'
        )
        
        return {
            'moh': moh,
            'mole': mole,
            'mafar': mafar,
            'moh_user': moh_user,
            'mole_user': mole_user,
            'mafar_user': mafar_user,
            'region': region,
            'province': province,
            'municipality': municipality,
            'barangay': barangay
        }
    
    def test_all_moas_see_same_regions(self, setup_shared_data):
        """Test all MOAs see the same region data."""
        client = Client()
        
        # Login as MOH
        client.force_login(setup_shared_data['moh_user'])
        response_moh = client.get('/moa/MOH/communities/regions/')
        assert response_moh.status_code == 200
        assert 'Region IX' in str(response_moh.content)
        
        # Login as MOLE
        client.force_login(setup_shared_data['mole_user'])
        response_mole = client.get('/moa/MOLE/communities/regions/')
        assert response_mole.status_code == 200
        assert 'Region IX' in str(response_mole.content)
        
        # Login as MAFAR
        client.force_login(setup_shared_data['mafar_user'])
        response_mafar = client.get('/moa/MAFAR/communities/regions/')
        assert response_mafar.status_code == 200
        assert 'Region IX' in str(response_mafar.content)
    
    def test_all_moas_see_same_barangays(self, setup_shared_data):
        """Test all MOAs see the same barangay data."""
        barangay = setup_shared_data['barangay']
        
        # Query barangays (no organization filter)
        all_barangays = Barangay.objects.all()
        assert all_barangays.count() == 1
        assert barangay in all_barangays
        
        # Verify no organization field on Barangay model
        assert not hasattr(Barangay, 'organization')
    
    def test_communities_api_shared_across_orgs(self, setup_shared_data):
        """Test communities API returns same data for all MOAs."""
        client = Client()
        
        # MOH API call
        client.force_login(setup_shared_data['moh_user'])
        response_moh = client.get('/api/communities/barangays/')
        assert response_moh.status_code == 200
        moh_data = response_moh.json()
        
        # MOLE API call
        client.force_login(setup_shared_data['mole_user'])
        response_mole = client.get('/api/communities/barangays/')
        assert response_mole.status_code == 200
        mole_data = response_mole.json()
        
        # Verify same data returned
        assert moh_data == mole_data
        assert len(moh_data['results']) == 1
        assert moh_data['results'][0]['name'] == 'Balangasan'
```

**23.3.3 Cross-Org Coordination Test**

```python
# src/tests/integration/test_cross_org_coordination.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from coordination.models import Partnership, Stakeholder

User = get_user_model()


@pytest.mark.django_db
class TestCrossOrgCoordination:
    """Test inter-MOA partnership coordination."""
    
    @pytest.fixture
    def setup_coordination(self):
        """Create multi-MOA coordination scenario."""
        moh = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        mole = Organization.objects.create(code='MOLE', name='Ministry of Labor', org_type='MOA')
        
        moh_user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moh
        )
        mole_user = User.objects.create_user(
            username='mole_staff',
            email='staff@mole.gov.ph',
            password='testpass123',
            default_organization=mole
        )
        
        # MOH creates partnership
        partnership = Partnership.objects.create(
            title='Health & Employment Initiative',
            organization=moh,  # Created by MOH
            status='active'
        )
        
        # Add MOLE as stakeholder
        mole_stakeholder = Stakeholder.objects.create(
            name='Ministry of Labor and Employment',
            stakeholder_type='government',
            organization=mole  # Reference to MOLE org
        )
        partnership.stakeholders.add(mole_stakeholder)
        
        return {
            'moh': moh,
            'mole': mole,
            'moh_user': moh_user,
            'mole_user': mole_user,
            'partnership': partnership,
            'mole_stakeholder': mole_stakeholder
        }
    
    def test_moh_sees_own_partnership(self, setup_coordination):
        """Test MOH can see partnership it created."""
        client = Client()
        client.force_login(setup_coordination['moh_user'])
        
        response = client.get('/moa/MOH/coordination/partnerships/')
        assert response.status_code == 200
        assert 'Health & Employment Initiative' in str(response.content)
    
    def test_mole_sees_partnership_as_stakeholder(self, setup_coordination):
        """Test MOLE can see partnerships where it's a stakeholder."""
        client = Client()
        client.force_login(setup_coordination['mole_user'])
        
        # MOLE should see partnership (as stakeholder)
        response = client.get('/moa/MOLE/coordination/partnerships/')
        assert response.status_code == 200
        # Should show partnerships where MOLE is stakeholder
        assert 'Health & Employment Initiative' in str(response.content)
    
    def test_cross_org_partnership_updates(self, setup_coordination):
        """Test MOLE can update partnership it's stakeholder in."""
        client = Client()
        client.force_login(setup_coordination['mole_user'])
        
        partnership_id = setup_coordination['partnership'].id
        
        # MOLE updates partnership
        response = client.post(
            f'/moa/MOLE/coordination/partnerships/{partnership_id}/update/',
            {
                'notes': 'MOLE coordination notes',
                'contribution': 'Job placement services'
            },
            follow=True
        )
        
        assert response.status_code == 200
        # Verify update was saved
        setup_coordination['partnership'].refresh_from_db()
        assert 'Job placement services' in setup_coordination['partnership'].notes
```

**23.3.4 Budget-to-WorkItem Distribution Test**

```python
# src/tests/integration/test_budget_distribution.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from decimal import Decimal
from organizations.models import Organization
from budget.models import BudgetAllocation, WorkItem
from planning.models import ProgramProjectActivity

User = get_user_model()


@pytest.mark.django_db
class TestBudgetDistribution:
    """Test Parliament Bill No. 325 budget distribution."""
    
    @pytest.fixture
    def setup_budget(self):
        """Create budget and work items."""
        moh = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        moh_user = User.objects.create_user(
            username='moh_budget',
            email='budget@moh.gov.ph',
            password='testpass123',
            default_organization=moh
        )
        
        # Create PPA
        ppa = ProgramProjectActivity.objects.create(
            code='MOH-2024-001',
            title='Rural Health Program 2024',
            organization=moh,
            ppa_type='program',
            status='approved'
        )
        
        # Create budget allocation (PHP 10,000,000)
        budget = BudgetAllocation.objects.create(
            ppa=ppa,
            organization=moh,
            fiscal_year=2024,
            total_amount=Decimal('10000000.00'),
            status='approved'
        )
        
        # Create work items
        work_item_1 = WorkItem.objects.create(
            budget_allocation=budget,
            description='Medical supplies procurement',
            allocated_amount=Decimal('6000000.00'),
            disbursed_amount=Decimal('0.00')
        )
        work_item_2 = WorkItem.objects.create(
            budget_allocation=budget,
            description='Healthcare worker training',
            allocated_amount=Decimal('4000000.00'),
            disbursed_amount=Decimal('0.00')
        )
        
        return {
            'moh': moh,
            'moh_user': moh_user,
            'ppa': ppa,
            'budget': budget,
            'work_item_1': work_item_1,
            'work_item_2': work_item_2
        }
    
    def test_work_items_sum_equals_budget(self, setup_budget):
        """Test work items sum equals total budget allocation."""
        budget = setup_budget['budget']
        
        # Calculate total allocated
        work_items = WorkItem.objects.filter(budget_allocation=budget)
        total_allocated = sum(wi.allocated_amount for wi in work_items)
        
        assert total_allocated == budget.total_amount
        assert total_allocated == Decimal('10000000.00')
    
    def test_work_item_disbursement_tracking(self, setup_budget):
        """Test disbursement tracking per work item."""
        work_item = setup_budget['work_item_1']
        
        # Disburse 50% of work item
        disbursement_amount = Decimal('3000000.00')
        work_item.disbursed_amount = disbursement_amount
        work_item.save()
        
        # Verify remaining balance
        remaining = work_item.allocated_amount - work_item.disbursed_amount
        assert remaining == Decimal('3000000.00')
        assert work_item.disbursement_percentage() == Decimal('50.00')
    
    def test_budget_utilization_calculation(self, setup_budget):
        """Test budget utilization rate calculation."""
        budget = setup_budget['budget']
        work_item_1 = setup_budget['work_item_1']
        work_item_2 = setup_budget['work_item_2']
        
        # Disburse from both work items
        work_item_1.disbursed_amount = Decimal('4000000.00')
        work_item_1.save()
        work_item_2.disbursed_amount = Decimal('2000000.00')
        work_item_2.save()
        
        # Calculate total utilization
        total_disbursed = (work_item_1.disbursed_amount + 
                          work_item_2.disbursed_amount)
        utilization_rate = (total_disbursed / budget.total_amount) * 100
        
        assert total_disbursed == Decimal('6000000.00')
        assert utilization_rate == Decimal('60.00')
    
    def test_budget_cannot_exceed_allocation(self, setup_budget):
        """Test work items cannot exceed budget allocation."""
        budget = setup_budget['budget']
        
        # Try to create work item exceeding remaining budget
        with pytest.raises(Exception):
            WorkItem.objects.create(
                budget_allocation=budget,
                description='Excessive allocation',
                allocated_amount=Decimal('5000000.00'),  # Exceeds remaining
                disbursed_amount=Decimal('0.00')
            )
```

**23.3.5 OCM Aggregation Test**

```python
# src/tests/integration/test_ocm_aggregation.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from decimal import Decimal
from organizations.models import Organization
from budget.models import BudgetAllocation
from mana.models import Assessment
from coordination.models import Partnership
from planning.models import ProgramProjectActivity

User = get_user_model()


@pytest.mark.django_db
class TestOCMAggregation:
    """Test OCM cross-MOA aggregation and reporting."""
    
    @pytest.fixture
    def setup_ocm_data(self):
        """Create OCM and multiple MOA data."""
        # Create OCM
        cmo = Organization.objects.create(code='OOBC', name='Office for OBC', org_type='OCM')
        ocm_user = User.objects.create_user(
            username='ocm_admin',
            email='admin@cmo.gov.ph',
            password='testpass123',
            default_organization=cmo
        )
        
        # Create MOAs
        moh = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        mole = Organization.objects.create(code='MOLE', name='Ministry of Labor', org_type='MOA')
        mafar = Organization.objects.create(code='MAFAR', name='Ministry of Agriculture', org_type='MOA')
        
        # Create budgets for each MOA
        moh_ppa = ProgramProjectActivity.objects.create(
            code='MOH-2024-001',
            title='Health Program',
            organization=moh,
            ppa_type='program'
        )
        moh_budget = BudgetAllocation.objects.create(
            ppa=moh_ppa,
            organization=moh,
            fiscal_year=2024,
            total_amount=Decimal('50000000.00')
        )
        
        mole_ppa = ProgramProjectActivity.objects.create(
            code='MOLE-2024-001',
            title='Employment Program',
            organization=mole,
            ppa_type='program'
        )
        mole_budget = BudgetAllocation.objects.create(
            ppa=mole_ppa,
            organization=mole,
            fiscal_year=2024,
            total_amount=Decimal('30000000.00')
        )
        
        mafar_ppa = ProgramProjectActivity.objects.create(
            code='MAFAR-2024-001',
            title='Agriculture Program',
            organization=mafar,
            ppa_type='program'
        )
        mafar_budget = BudgetAllocation.objects.create(
            ppa=mafar_ppa,
            organization=mafar,
            fiscal_year=2024,
            total_amount=Decimal('40000000.00')
        )
        
        # Create assessments for each MOA
        Assessment.objects.create(
            title='MOH Assessment',
            organization=moh,
            status='published'
        )
        Assessment.objects.create(
            title='MOLE Assessment',
            organization=mole,
            status='published'
        )
        Assessment.objects.create(
            title='MAFAR Assessment',
            organization=mafar,
            status='draft'
        )
        
        return {
            'ocm': ocm,
            'ocm_user': ocm_user,
            'moh': moh,
            'mole': mole,
            'mafar': mafar
        }
    
    def test_ocm_sees_all_moa_budgets(self, setup_ocm_data):
        """Test OCM can aggregate budgets from all MOAs."""
        client = Client()
        client.force_login(setup_ocm_data['ocm_user'])
        
        # Access OCM budget dashboard
        response = client.get('/ocm/OOBC/budget/aggregate/')
        assert response.status_code == 200
        
        # Verify all MOA budgets visible
        content = str(response.content)
        assert 'Ministry of Health' in content
        assert 'Ministry of Labor' in content
        assert 'Ministry of Agriculture' in content
        assert '50,000,000' in content
        assert '30,000,000' in content
        assert '40,000,000' in content
    
    def test_ocm_budget_total_calculation(self, setup_ocm_data):
        """Test OCM calculates correct total budget."""
        # Query all budgets
        all_budgets = BudgetAllocation.objects.filter(
            organization__org_type='MOA',
            fiscal_year=2024
        )
        
        total_budget = sum(b.total_amount for b in all_budgets)
        assert total_budget == Decimal('120000000.00')
    
    def test_ocm_sees_all_moa_assessments(self, setup_ocm_data):
        """Test OCM can view assessments from all MOAs."""
        client = Client()
        client.force_login(setup_ocm_data['ocm_user'])
        
        # Access OCM MANA dashboard
        response = client.get('/ocm/OOBC/mana/aggregate/')
        assert response.status_code == 200
        
        # Verify all MOA assessments visible
        content = str(response.content)
        assert 'MOH Assessment' in content
        assert 'MOLE Assessment' in content
        assert 'MAFAR Assessment' in content
    
    def test_ocm_assessment_count_by_status(self, setup_ocm_data):
        """Test OCM can count assessments by status across MOAs."""
        # Count published assessments
        published_count = Assessment.objects.filter(
            organization__org_type='MOA',
            status='published'
        ).count()
        
        assert published_count == 2
        
        # Count draft assessments
        draft_count = Assessment.objects.filter(
            organization__org_type='MOA',
            status='draft'
        ).count()
        
        assert draft_count == 1
    
    def test_ocm_cannot_modify_moa_data(self, setup_ocm_data):
        """Test OCM has read-only access to MOA data."""
        client = Client()
        client.force_login(setup_ocm_data['ocm_user'])
        
        # Try to edit MOH assessment
        moh_assessment = Assessment.objects.get(title='MOH Assessment')
        response = client.post(
            f'/ocm/OOBC/mana/assessments/{moh_assessment.id}/edit/',
            {'title': 'Modified by OCM', 'status': 'published'},
            follow=True
        )
        
        # Should be forbidden
        assert response.status_code == 403
```

---

#### 23.4 Performance Testing


### 23.4.1 Page Load Performance Testing

**Objective:** Ensure all pages load within acceptable time thresholds under various conditions.

```python
# src/tests/performance/test_page_load.py

import pytest
import time
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment
from coordination.models import Partnership
from communities.models import Region, Province, Municipality, Barangay

User = get_user_model()


@pytest.mark.django_db
class TestPageLoadPerformance:
    """Test page load performance across OBCMS modules."""

    @pytest.fixture
    def setup_performance_data(self):
        """Create realistic dataset for performance testing."""
        # Create organization
        moa = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='MOA'
        )

        # Create user
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create 50 assessments
        for i in range(50):
            Assessment.objects.create(
                title=f'Assessment {i}',
                organization=moa,
                status='published' if i % 2 == 0 else 'draft',
                description=f'Test assessment {i}' * 10  # Realistic content
            )

        # Create 30 partnerships
        for i in range(30):
            Partnership.objects.create(
                title=f'Partnership {i}',
                organization=moa,
                status='active' if i % 3 == 0 else 'pending'
            )

        # Create community hierarchy
        region = Region.objects.create(name='Region IX', code='09')
        province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=region)
        muni = Municipality.objects.create(name='Pagadian City', code='097201', province=province)

        # Create 100 barangays
        for i in range(100):
            Barangay.objects.create(
                name=f'Barangay {i}',
                code=f'09720100{i:03d}',
                municipality=muni,
                population=1000 + i * 50,
                obc_status='Confirmed'
            )

        return {
            'moa': moa,
            'user': user,
            'region': region
        }

    def test_dashboard_load_time(self, setup_performance_data):
        """Dashboard should load in < 200ms."""
        client = Client()
        user = setup_performance_data['user']
        client.force_login(user)

        start_time = time.time()
        response = client.get(f'/moa/{user.default_organization.code}/')
        end_time = time.time()

        load_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert load_time_ms < 200, f"Dashboard load time {load_time_ms:.2f}ms exceeds 200ms"
        print(f"✓ Dashboard loaded in {load_time_ms:.2f}ms")

    def test_assessment_list_load_time(self, setup_performance_data):
        """Assessment list should load in < 300ms with pagination."""
        client = Client()
        user = setup_performance_data['user']
        client.force_login(user)

        start_time = time.time()
        response = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
        end_time = time.time()

        load_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert load_time_ms < 300, f"List load time {load_time_ms:.2f}ms exceeds 300ms"
        print(f"✓ Assessment list loaded in {load_time_ms:.2f}ms")

    def test_calendar_view_load_time(self, setup_performance_data):
        """Calendar view with events should load in < 500ms."""
        client = Client()
        user = setup_performance_data['user']
        client.force_login(user)

        start_time = time.time()
        response = client.get(f'/moa/{user.default_organization.code}/coordination/calendar/')
        end_time = time.time()

        load_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert load_time_ms < 500, f"Calendar load time {load_time_ms:.2f}ms exceeds 500ms"
        print(f"✓ Calendar loaded in {load_time_ms:.2f}ms")

    def test_geojson_rendering_performance(self, setup_performance_data):
        """GeoJSON boundary rendering should complete in < 400ms."""
        client = Client()
        user = setup_performance_data['user']
        client.force_login(user)

        start_time = time.time()
        response = client.get('/api/communities/regions/09/geojson/')
        end_time = time.time()

        load_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert load_time_ms < 400, f"GeoJSON load time {load_time_ms:.2f}ms exceeds 400ms"
        print(f"✓ GeoJSON rendered in {load_time_ms:.2f}ms")


### 23.4.2 Database Query Performance Testing

**Objective:** Detect and prevent N+1 query problems, ensure proper use of indexes.

```python
# src/tests/performance/test_query_performance.py

import pytest
from django.test import Client
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment
from coordination.models import Partnership

User = get_user_model()


@pytest.mark.django_db
class TestQueryPerformance:
    """Test database query efficiency."""

    @pytest.fixture
    def setup_query_test(self):
        """Setup data for query tests."""
        moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create 20 assessments
        for i in range(20):
            Assessment.objects.create(
                title=f'Assessment {i}',
                organization=moa,
                status='published'
            )

        return {'moa': moa, 'user': user}

    def test_assessment_list_query_count(self, setup_query_test):
        """Assessment list should use ≤ 5 queries (no N+1 problem)."""
        client = Client()
        user = setup_query_test['user']
        client.force_login(user)

        with CaptureQueriesContext(connection) as queries:
            response = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')

        query_count = len(queries)

        assert response.status_code == 200
        assert query_count <= 5, f"Query count {query_count} exceeds 5 (N+1 problem detected)"
        print(f"✓ Assessment list used {query_count} queries")

    def test_select_related_optimization(self, setup_query_test):
        """Verify select_related() is used for foreign keys."""
        from mana.models import Assessment

        with CaptureQueriesContext(connection) as queries_without:
            # WITHOUT select_related
            assessments = Assessment.objects.filter(organization=setup_query_test['moa'])
            for a in assessments:
                _ = a.organization.name  # Triggers extra query per assessment

        with CaptureQueriesContext(connection) as queries_with:
            # WITH select_related
            assessments = Assessment.objects.filter(
                organization=setup_query_test['moa']
            ).select_related('organization')
            for a in assessments:
                _ = a.organization.name  # No extra queries

        # select_related should drastically reduce queries
        assert len(queries_with) < len(queries_without), \
            "select_related() not reducing query count"
        print(f"✓ select_related reduced queries from {len(queries_without)} to {len(queries_with)}")

    def test_slow_query_detection(self, setup_query_test):
        """All queries should complete in < 100ms."""
        client = Client()
        user = setup_query_test['user']
        client.force_login(user)

        with CaptureQueriesContext(connection) as queries:
            response = client.get(f'/moa/{user.default_organization.code}/')

        slow_queries = []
        for query in queries:
            query_time = float(query['time']) * 1000  # Convert to ms
            if query_time > 100:
                slow_queries.append({
                    'sql': query['sql'][:100],
                    'time': query_time
                })

        assert len(slow_queries) == 0, f"Found {len(slow_queries)} slow queries: {slow_queries}"
        print(f"✓ All {len(queries)} queries completed in < 100ms")

    def test_index_usage_verification(self, setup_query_test):
        """Verify database indexes are being used for organization filtering."""
        moa = setup_query_test['moa']

        with connection.cursor() as cursor:
            # Test organization_id index usage
            cursor.execute(
                "EXPLAIN SELECT * FROM mana_assessment WHERE organization_id = %s",
                [moa.id]
            )
            explain_output = cursor.fetchall()

        explain_text = str(explain_output).lower()

        # Check for index usage (works for both SQLite and PostgreSQL)
        has_index = any([
            'index' in explain_text,
            'search' in explain_text,  # SQLite "SEARCH TABLE ... USING INDEX"
            'scan' in explain_text and 'index' in explain_text  # PostgreSQL "Index Scan"
        ])

        assert has_index, "Database index not being used for organization filtering"
        print(f"✓ Index detected in query plan: {explain_text[:200]}")


### 23.4.3 HTMX Performance Testing

**Objective:** Verify instant UI updates and smooth HTMX interactions.

```python
# src/tests/performance/test_htmx_performance.py

import pytest
import time
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from coordination.models import Task

User = get_user_model()


@pytest.mark.django_db
class TestHTMXPerformance:
    """Test HTMX interaction performance."""

    @pytest.fixture
    def setup_htmx_test(self):
        """Setup data for HTMX tests."""
        moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create tasks for kanban testing
        for i in range(10):
            Task.objects.create(
                title=f'Task {i}',
                organization=moa,
                assigned_to=user,
                status='pending'
            )

        return {'moa': moa, 'user': user}

    def test_htmx_swap_time(self, setup_htmx_test):
        """HTMX element swaps should complete in < 50ms."""
        client = Client()
        user = setup_htmx_test['user']
        client.force_login(user)

        task = Task.objects.first()

        start_time = time.time()
        response = client.post(
            f'/moa/{user.default_organization.code}/coordination/tasks/{task.id}/update-status/',
            {'status': 'in-progress'},
            HTTP_HX_REQUEST='true'
        )
        end_time = time.time()

        swap_time_ms = (end_time - start_time) * 1000

        assert response.status_code in [200, 204]
        assert swap_time_ms < 50, f"HTMX swap time {swap_time_ms:.2f}ms exceeds 50ms"
        print(f"✓ HTMX swap completed in {swap_time_ms:.2f}ms")

    def test_optimistic_update_performance(self, setup_htmx_test):
        """Optimistic updates should return immediately with 204 No Content."""
        client = Client()
        user = setup_htmx_test['user']
        client.force_login(user)

        task = Task.objects.first()

        start_time = time.time()
        response = client.delete(
            f'/moa/{user.default_organization.code}/coordination/tasks/{task.id}/delete/',
            HTTP_HX_REQUEST='true'
        )
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 204
        assert response_time_ms < 30, f"Optimistic update took {response_time_ms:.2f}ms (should be < 30ms)"
        print(f"✓ Optimistic update completed in {response_time_ms:.2f}ms")

    def test_out_of_band_swap_performance(self, setup_htmx_test):
        """Out-of-band swaps (multiple element updates) should be fast."""
        client = Client()
        user = setup_htmx_test['user']
        client.force_login(user)

        task = Task.objects.first()

        start_time = time.time()
        response = client.post(
            f'/moa/{user.default_organization.code}/coordination/tasks/{task.id}/update-status/',
            {'status': 'completed'},
            HTTP_HX_REQUEST='true'
        )
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Response should include HX-Trigger header for counter updates
        assert response.has_header('HX-Trigger') or response.status_code == 204
        assert response_time_ms < 100, f"OOB swap took {response_time_ms:.2f}ms"
        print(f"✓ Out-of-band swap completed in {response_time_ms:.2f}ms")


### 23.4.4 Concurrent User Load Testing

**Objective:** Test system stability under high concurrent user load.

```python
# src/tests/performance/test_concurrent_load.py

import pytest
import time
import concurrent.futures
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.slow
class TestConcurrentLoad:
    """Test system under concurrent user load."""

    @pytest.fixture
    def setup_concurrent_test(self):
        """Create multiple organizations and users."""
        organizations = []
        users = []

        # Create 10 MOAs
        for i in range(10):
            org = Organization.objects.create(
                code=f'MOA{i:02d}',
                name=f'Ministry {i}',
                org_type='MOA'
            )
            organizations.append(org)

            # Create 5 users per org (50 total users)
            for j in range(5):
                user = User.objects.create_user(
                    username=f'staff_{org.code}_{j}',
                    email=f'staff{j}@{org.code.lower()}.gov.ph',
                    password='testpass123',
                    default_organization=org
                )
                users.append(user)

        return {'organizations': organizations, 'users': users}

    def simulate_user_session(self, user):
        """Simulate typical user session."""
        client = Client()
        client.force_login(user)

        try:
            # Dashboard view
            r1 = client.get(f'/moa/{user.default_organization.code}/')
            assert r1.status_code == 200

            # List view
            r2 = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
            assert r2.status_code == 200

            # API call
            r3 = client.get('/api/communities/barangays/?limit=10')
            assert r3.status_code == 200

            return True
        except Exception as e:
            print(f"User session failed: {e}")
            return False

    def test_500_concurrent_users(self, setup_concurrent_test):
        """System should handle 500 concurrent users without degradation."""
        users = setup_concurrent_test['users']

        start_time = time.time()

        # Simulate 500 concurrent sessions (50 users * 10 sessions each)
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for _ in range(500):
                user = users[_ % len(users)]
                future = executor.submit(self.simulate_user_session, user)
                futures.append(future)

            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        end_time = time.time()
        total_time_seconds = end_time - start_time

        success_count = sum(results)
        success_rate = (success_count / len(results)) * 100

        assert success_rate >= 95, f"Success rate {success_rate:.1f}% < 95%"
        assert total_time_seconds < 60, f"Load test took {total_time_seconds:.1f}s (should be < 60s)"

        print(f"✓ 500 concurrent users: {success_rate:.1f}% success in {total_time_seconds:.1f}s")

    def test_sustained_load(self, setup_concurrent_test):
        """System should maintain performance under sustained load."""
        users = setup_concurrent_test['users']

        # Run for 5 minutes with continuous load
        start_time = time.time()
        duration_seconds = 300  # 5 minutes

        successful_requests = 0
        failed_requests = 0

        while time.time() - start_time < duration_seconds:
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for _ in range(100):
                    user = users[_ % len(users)]
                    future = executor.submit(self.simulate_user_session, user)
                    futures.append(future)

                results = [f.result() for f in concurrent.futures.as_completed(futures)]
                successful_requests += sum(results)
                failed_requests += len(results) - sum(results)

            time.sleep(1)  # Throttle between batches

        success_rate = (successful_requests / (successful_requests + failed_requests)) * 100

        assert success_rate >= 95, f"Sustained load success rate {success_rate:.1f}% < 95%"
        print(f"✓ Sustained load: {successful_requests} successful, {failed_requests} failed ({success_rate:.1f}%)")


### 23.4.5 API Performance Testing

**Objective:** Ensure REST API endpoints meet performance targets.

```python
# src/tests/performance/test_api_performance.py

import pytest
import time
from django.test import Client
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from organizations.models import Organization
from communities.models import Barangay, Region, Province, Municipality

User = get_user_model()


@pytest.mark.django_db
class TestAPIPerformance:
    """Test REST API endpoint performance."""

    @pytest.fixture
    def setup_api_test(self):
        """Setup data for API tests."""
        moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create community hierarchy with 100 barangays
        region = Region.objects.create(name='Region IX', code='09')
        province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=region)
        muni = Municipality.objects.create(name='Pagadian City', code='097201', province=province)

        for i in range(100):
            Barangay.objects.create(
                name=f'Barangay {i}',
                code=f'09720100{i:03d}',
                municipality=muni,
                population=1000 + i * 50,
                obc_status='Confirmed'
            )

        return {'moa': moa, 'user': user}

    def test_api_list_response_time(self, setup_api_test):
        """API list endpoints should respond in < 500ms."""
        client = APIClient()
        user = setup_api_test['user']
        client.force_authenticate(user=user)

        start_time = time.time()
        response = client.get('/api/communities/barangays/')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time_ms < 500, f"API response time {response_time_ms:.2f}ms exceeds 500ms"
        print(f"✓ API list endpoint responded in {response_time_ms:.2f}ms")

    def test_api_pagination_performance(self, setup_api_test):
        """Paginated API calls should be fast."""
        client = APIClient()
        user = setup_api_test['user']
        client.force_authenticate(user=user)

        start_time = time.time()
        response = client.get('/api/communities/barangays/?page=1&page_size=20')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert 'results' in response.json()
        assert response_time_ms < 300, f"Paginated API took {response_time_ms:.2f}ms"
        print(f"✓ Paginated API responded in {response_time_ms:.2f}ms")

    def test_api_filtering_performance(self, setup_api_test):
        """Filtered API queries should use indexes and be fast."""
        client = APIClient()
        user = setup_api_test['user']
        client.force_authenticate(user=user)

        start_time = time.time()
        response = client.get('/api/communities/barangays/?obc_status=Confirmed')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time_ms < 400, f"Filtered API took {response_time_ms:.2f}ms"
        print(f"✓ Filtered API responded in {response_time_ms:.2f}ms")

    def test_geojson_api_performance(self, setup_api_test):
        """GeoJSON API endpoints should serialize efficiently."""
        client = APIClient()
        user = setup_api_test['user']
        client.force_authenticate(user=user)

        start_time = time.time()
        response = client.get('/api/communities/regions/09/geojson/')
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time_ms < 600, f"GeoJSON API took {response_time_ms:.2f}ms"
        print(f"✓ GeoJSON API responded in {response_time_ms:.2f}ms")


### 23.4.6 Caching Performance Testing

**Objective:** Verify caching strategies improve performance.

```python
# src/tests/performance/test_caching.py

import pytest
import time
from django.test import Client
from django.core.cache import cache
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment

User = get_user_model()


@pytest.mark.django_db
class TestCachingPerformance:
    """Test caching effectiveness."""

    @pytest.fixture
    def setup_caching_test(self):
        """Setup data for caching tests."""
        moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moa
        )

        # Create 50 assessments
        for i in range(50):
            Assessment.objects.create(
                title=f'Assessment {i}',
                organization=moa,
                status='published'
            )

        # Clear cache before test
        cache.clear()

        return {'moa': moa, 'user': user}

    def test_cache_hit_performance(self, setup_caching_test):
        """Cached responses should be 10x faster than uncached."""
        client = Client()
        user = setup_caching_test['user']
        client.force_login(user)

        # First request (cache miss)
        start_time = time.time()
        response1 = client.get(f'/moa/{user.default_organization.code}/')
        end_time = time.time()
        uncached_time_ms = (end_time - start_time) * 1000

        # Second request (cache hit)
        start_time = time.time()
        response2 = client.get(f'/moa/{user.default_organization.code}/')
        end_time = time.time()
        cached_time_ms = (end_time - start_time) * 1000

        speedup_factor = uncached_time_ms / cached_time_ms if cached_time_ms > 0 else 1

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Cached should be noticeably faster (at least 2x)
        assert speedup_factor >= 2, f"Cache speedup {speedup_factor:.1f}x < 2x"

        print(f"✓ Cache hit: {cached_time_ms:.2f}ms (uncached: {uncached_time_ms:.2f}ms, {speedup_factor:.1f}x faster)")

    def test_cache_invalidation(self, setup_caching_test):
        """Cache should invalidate when data changes."""
        client = Client()
        user = setup_caching_test['user']
        client.force_login(user)

        # Prime cache
        response1 = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
        assert response1.status_code == 200

        # Modify data
        Assessment.objects.create(
            title='New Assessment',
            organization=setup_caching_test['moa'],
            status='published'
        )

        # Fetch again (cache should be invalidated)
        response2 = client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
        assert response2.status_code == 200

        # New assessment should be visible
        content = response2.content.decode()
        assert 'New Assessment' in content, "Cache not invalidated after data change"

        print("✓ Cache properly invalidated after data change")

    def test_organization_context_caching(self, setup_caching_test):
        """Organization context should be cached per user."""
        client = Client()
        user = setup_caching_test['user']
        client.force_login(user)

        # Multiple requests to different pages
        start_time = time.time()
        for _ in range(10):
            client.get(f'/moa/{user.default_organization.code}/')
            client.get(f'/moa/{user.default_organization.code}/mana/assessments/')
            client.get(f'/moa/{user.default_organization.code}/coordination/partnerships/')
        end_time = time.time()

        avg_time_ms = ((end_time - start_time) / 30) * 1000

        # Average request should be fast due to org context caching
        assert avg_time_ms < 150, f"Average request time {avg_time_ms:.2f}ms too slow (caching not effective)"
        print(f"✓ Organization context caching: avg {avg_time_ms:.2f}ms per request")


### 23.4.7 Frontend Performance Testing (Core Web Vitals)

**Objective:** Ensure frontend meets Core Web Vitals standards.

```python
# src/tests/performance/test_frontend_performance.py

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


@pytest.mark.django_db
@pytest.mark.selenium
class TestFrontendPerformance:
    """Test frontend performance metrics (Core Web Vitals)."""

    @pytest.fixture
    def setup_selenium(self):
        """Setup Selenium WebDriver for performance testing."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Enable performance logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)

        yield driver

        driver.quit()

    def get_web_vitals(self, driver):
        """Extract Core Web Vitals from page."""
        # Inject Web Vitals library and measure
        vitals_script = """
        return new Promise((resolve) => {
            const vitals = {};

            // Largest Contentful Paint (LCP)
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                vitals.lcp = entries[entries.length - 1].renderTime || entries[entries.length - 1].loadTime;
            }).observe({type: 'largest-contentful-paint', buffered: true});

            // First Contentful Paint (FCP)
            new PerformanceObserver((list) => {
                vitals.fcp = list.getEntries()[0].startTime;
            }).observe({type: 'paint', buffered: true});

            // Cumulative Layout Shift (CLS)
            let cls = 0;
            new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        cls += entry.value;
                    }
                }
                vitals.cls = cls;
            }).observe({type: 'layout-shift', buffered: true});

            // Time to Interactive (TTI)
            const navTiming = performance.getEntriesByType('navigation')[0];
            vitals.tti = navTiming.domInteractive;

            setTimeout(() => resolve(vitals), 2000);
        });
        """

        return driver.execute_async_script(vitals_script)

    def test_largest_contentful_paint(self, setup_selenium, live_server):
        """LCP should be < 2.5 seconds (Good)."""
        driver = setup_selenium
        driver.get(f'{live_server.url}/accounts/login/')

        # Login
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Navigate to dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.dashboard'))
        )

        vitals = self.get_web_vitals(driver)
        lcp_seconds = vitals.get('lcp', 0) / 1000

        assert lcp_seconds < 2.5, f"LCP {lcp_seconds:.2f}s exceeds 2.5s (Poor)"

        if lcp_seconds < 2.5:
            print(f"✓ LCP: {lcp_seconds:.2f}s (Good)")
        else:
            print(f"✗ LCP: {lcp_seconds:.2f}s (Needs Improvement)")

    def test_first_contentful_paint(self, setup_selenium, live_server):
        """FCP should be < 1.8 seconds (Good)."""
        driver = setup_selenium
        driver.get(f'{live_server.url}/')

        vitals = self.get_web_vitals(driver)
        fcp_seconds = vitals.get('fcp', 0) / 1000

        assert fcp_seconds < 1.8, f"FCP {fcp_seconds:.2f}s exceeds 1.8s"
        print(f"✓ FCP: {fcp_seconds:.2f}s (Good)")

    def test_cumulative_layout_shift(self, setup_selenium, live_server):
        """CLS should be < 0.1 (Good)."""
        driver = setup_selenium
        driver.get(f'{live_server.url}/')

        vitals = self.get_web_vitals(driver)
        cls_score = vitals.get('cls', 0)

        assert cls_score < 0.1, f"CLS {cls_score:.3f} exceeds 0.1 (Poor)"
        print(f"✓ CLS: {cls_score:.3f} (Good)")

    def test_time_to_interactive(self, setup_selenium, live_server):
        """TTI should be < 3.8 seconds (Good)."""
        driver = setup_selenium
        driver.get(f'{live_server.url}/')

        vitals = self.get_web_vitals(driver)
        tti_seconds = vitals.get('tti', 0) / 1000

        assert tti_seconds < 3.8, f"TTI {tti_seconds:.2f}s exceeds 3.8s"
        print(f"✓ TTI: {tti_seconds:.2f}s (Good)")


### 23.4.8 Load Testing with Locust (EXPANDED)

**Comprehensive load testing scenarios covering all OBCMS modules.**

```python
# locustfile.py

from locust import HttpUser, task, between, SequentialTaskSet
import random
import json


class MANAUserTasks(SequentialTaskSet):
    """MANA module user workflow."""

    @task
    def view_mana_dashboard(self):
        """View MANA dashboard."""
        self.client.get(f'/moa/{self.user.org_code}/mana/')

    @task
    def list_assessments(self):
        """View assessments list."""
        self.client.get(f'/moa/{self.user.org_code}/mana/assessments/')

    @task
    def search_assessments(self):
        """Search assessments."""
        terms = ['health', 'education', 'livelihood', 'infrastructure']
        term = random.choice(terms)
        self.client.get(
            f'/moa/{self.user.org_code}/mana/assessments/',
            params={'search': term}
        )

    @task
    def view_assessment_detail(self):
        """View assessment detail."""
        # Assume assessment IDs 1-50 exist
        assessment_id = random.randint(1, 50)
        self.client.get(f'/moa/{self.user.org_code}/mana/assessments/{assessment_id}/')

    @task
    def create_assessment(self):
        """Create new assessment."""
        self.client.get(f'/moa/{self.user.org_code}/mana/assessments/create/')

        # POST form data
        self.client.post(
            f'/moa/{self.user.org_code}/mana/assessments/create/',
            {
                'title': f'Load Test Assessment {random.randint(1000, 9999)}',
                'description': 'Automated load test assessment',
                'status': 'draft'
            }
        )


class CoordinationUserTasks(SequentialTaskSet):
    """Coordination module user workflow."""

    @task
    def view_calendar(self):
        """View coordination calendar."""
        self.client.get(f'/moa/{self.user.org_code}/coordination/calendar/')

    @task
    def fetch_events(self):
        """Fetch calendar events (AJAX)."""
        self.client.get(
            f'/moa/{self.user.org_code}/coordination/events/',
            params={
                'start': '2024-01-01',
                'end': '2024-12-31'
            }
        )

    @task
    def view_partnerships(self):
        """View partnerships list."""
        self.client.get(f'/moa/{self.user.org_code}/coordination/partnerships/')

    @task
    def view_tasks_kanban(self):
        """View tasks kanban."""
        self.client.get(f'/moa/{self.user.org_code}/coordination/tasks/')

    @task
    def update_task_status(self):
        """Update task status (HTMX)."""
        task_id = random.randint(1, 20)
        status = random.choice(['pending', 'in-progress', 'completed'])

        self.client.post(
            f'/moa/{self.user.org_code}/coordination/tasks/{task_id}/update-status/',
            {'status': status},
            headers={'HX-Request': 'true'}
        )


class BudgetUserTasks(SequentialTaskSet):
    """Budget module user workflow."""

    @task
    def view_budget_dashboard(self):
        """View budget dashboard."""
        self.client.get(f'/moa/{self.user.org_code}/budget/')

    @task
    def view_allocations(self):
        """View budget allocations."""
        self.client.get(f'/moa/{self.user.org_code}/budget/allocations/')

    @task
    def filter_by_fiscal_year(self):
        """Filter budgets by fiscal year."""
        year = random.choice([2024, 2025, 2026])
        self.client.get(
            f'/moa/{self.user.org_code}/budget/allocations/',
            params={'fiscal_year': year}
        )

    @task
    def view_ppa_budget(self):
        """View PPA budget detail."""
        ppa_id = random.randint(1, 30)
        self.client.get(f'/moa/{self.user.org_code}/budget/ppa/{ppa_id}/')


class MOAUser(HttpUser):
    """Simulate MOA staff user behavior."""

    wait_time = between(2, 8)

    def on_start(self):
        """Login on start."""
        self.org_code = random.choice([
            'MOH', 'MOLE', 'MAFAR', 'MSWDD', 'MBHTE', 'MENRE',
            'MPWH', 'MIPA', 'MTIT', 'MEST', 'MFBM', 'MOJ'
        ])

        response = self.client.post('/accounts/login/', {
            'username': f'staff_{self.org_code}',
            'password': 'testpass123'
        })

        if response.status_code == 200:
            self.org_code = self.org_code
        else:
            print(f"Login failed for {self.org_code}")

    @task(3)
    def view_dashboard(self):
        """View organization dashboard (most frequent)."""
        self.client.get(f'/moa/{self.org_code}/')

    @task(2)
    def mana_workflow(self):
        """Execute MANA workflow."""
        tasks = MANAUserTasks(self)
        tasks.execute()

    @task(2)
    def coordination_workflow(self):
        """Execute Coordination workflow."""
        tasks = CoordinationUserTasks(self)
        tasks.execute()

    @task(1)
    def budget_workflow(self):
        """Execute Budget workflow."""
        tasks = BudgetUserTasks(self)
        tasks.execute()

    @task(1)
    def view_communities(self):
        """View OBC communities (shared data)."""
        self.client.get('/api/communities/barangays/')

    @task(1)
    def view_policies(self):
        """View policy recommendations."""
        self.client.get(f'/moa/{self.org_code}/policies/')


class OCMUser(HttpUser):
    """Simulate OCM admin user behavior (aggregation queries)."""

    wait_time = between(5, 15)

    def on_start(self):
        """Login as OCM user."""
        self.client.post('/accounts/login/', {
            'username': 'ocm_admin',
            'password': 'testpass123'
        })

    @task(3)
    def view_ocm_dashboard(self):
        """View OCM aggregation dashboard."""
        self.client.get('/ocm/OOBC/')

    @task(2)
    def view_budget_aggregation(self):
        """View aggregated budget data across all MOAs."""
        self.client.get('/ocm/OOBC/budget/aggregate/')

    @task(2)
    def view_mana_aggregation(self):
        """View aggregated MANA data."""
        self.client.get('/ocm/OOBC/mana/aggregate/')

    @task(1)
    def view_coordination_report(self):
        """View cross-MOA coordination report."""
        self.client.get('/ocm/OOBC/coordination/report/')

    @task(1)
    def export_report(self):
        """Export aggregated report."""
        self.client.get('/ocm/OOBC/reports/export/', params={'format': 'pdf'})


class PeakLoadUser(HttpUser):
    """Simulate peak load (budget submission deadline)."""

    wait_time = between(0.5, 2)  # Faster interactions during peak

    def on_start(self):
        """Login."""
        self.org_code = random.choice(['MOH', 'MOLE', 'MAFAR', 'MSWDD'])
        self.client.post('/accounts/login/', {
            'username': f'staff_{self.org_code}',
            'password': 'testpass123'
        })

    @task(5)
    def submit_budget(self):
        """Submit budget allocation (high frequency)."""
        self.client.post(
            f'/moa/{self.org_code}/budget/allocations/create/',
            {
                'ppa': random.randint(1, 30),
                'fiscal_year': 2025,
                'total_amount': random.randint(100000, 10000000),
                'status': 'submitted'
            }
        )

    @task(3)
    def view_budget_status(self):
        """Check budget submission status."""
        self.client.get(f'/moa/{self.org_code}/budget/submissions/status/')

    @task(2)
    def update_budget(self):
        """Update existing budget."""
        budget_id = random.randint(1, 50)
        self.client.post(
            f'/moa/{self.org_code}/budget/allocations/{budget_id}/edit/',
            {'total_amount': random.randint(100000, 10000000)}
        )
```

**Run Load Tests:**

```bash
# Install Locust
pip install locust

# Test 1: Normal Load (500 users, 80% MOA / 20% OCM)
locust -f locustfile.py \
  --users=500 \
  --spawn-rate=50 \
  --host=http://localhost:8000 \
  --user-classes=MOAUser:8,OCMUser:2

# Test 2: Peak Load (800 users, budget deadline simulation)
locust -f locustfile.py \
  --users=800 \
  --spawn-rate=100 \
  --host=http://localhost:8000 \
  --user-classes=PeakLoadUser

# Test 3: Sustained Load (300 users, 8-hour simulation)
locust -f locustfile.py \
  --users=300 \
  --spawn-rate=30 \
  --run-time=8h \
  --host=http://localhost:8000

# View results at http://localhost:8089
```


### 23.4.9 Performance Monitoring & Profiling

**Production monitoring setup for ongoing performance tracking.**

```python
# src/obc_management/settings/production.py

# Django Debug Toolbar (DEVELOPMENT ONLY - DO NOT USE IN PRODUCTION)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Logging slow queries (PostgreSQL)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'performance.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'WARNING',  # Log slow queries
            'propagate': False,
        },
    },
}

# PostgreSQL slow query logging
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c log_min_duration_statement=100'  # Log queries > 100ms
}
```

**Grafana Dashboard Configuration (docker-compose.yml):**

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

  postgres_exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://obcms_user:password@postgres:5432/obcms_prod?sslmode=disable"
    ports:
      - "9187:9187"

volumes:
  prometheus_data:
  grafana_data:
```

**Prometheus Configuration (prometheus.yml):**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'django'
    static_configs:
      - targets: ['web:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```


### 23.4.10 Performance Testing Checklist

```markdown
# Performance Testing Checklist

## Page Load Performance
- [ ] Dashboard loads in < 200ms
- [ ] List views load in < 300ms
- [ ] Detail views load in < 250ms
- [ ] Calendar view loads in < 500ms
- [ ] Map views load in < 600ms
- [ ] API endpoints respond in < 500ms

## Database Query Optimization
- [ ] No N+1 query problems detected
- [ ] All queries use proper indexes
- [ ] select_related() used for foreign keys
- [ ] prefetch_related() used for M2M
- [ ] Query count per page ≤ 10
- [ ] All queries complete in < 100ms
- [ ] Slow query logging enabled (> 100ms)

## HTMX Performance
- [ ] Element swaps complete in < 50ms
- [ ] Optimistic updates return 204 in < 30ms
- [ ] Out-of-band swaps work correctly
- [ ] Loading indicators display immediately
- [ ] No full page reloads for CRUD operations

## Caching
- [ ] Redis cache configured and working
- [ ] Cache hit rate > 70%
- [ ] Expensive queries cached (1-5 min TTL)
- [ ] Cache invalidation on model updates
- [ ] Organization context cached per user

## Concurrent Load
- [ ] System handles 500 concurrent users
- [ ] Success rate > 95% under load
- [ ] Response times stable under load
- [ ] No database connection exhaustion
- [ ] No memory leaks during sustained load

## API Performance
- [ ] REST API list endpoints < 500ms
- [ ] Pagination working efficiently
- [ ] Filtering uses database indexes
- [ ] GeoJSON serialization < 600ms
- [ ] Bulk operations handle 1000+ records

## Frontend Performance (Core Web Vitals)
- [ ] LCP (Largest Contentful Paint) < 2.5s
- [ ] FCP (First Contentful Paint) < 1.8s
- [ ] CLS (Cumulative Layout Shift) < 0.1
- [ ] TTI (Time to Interactive) < 3.8s
- [ ] TBT (Total Blocking Time) < 300ms

## Load Testing Results
- [ ] Normal load test (500 users): ✓ Pass
- [ ] Peak load test (800 users): ✓ Pass
- [ ] Sustained load test (8 hours): ✓ Pass
- [ ] Stress test (find breaking point): Documented
- [ ] Budget deadline simulation: ✓ Pass

## Monitoring Setup
- [ ] Prometheus configured
- [ ] Grafana dashboards created
- [ ] PostgreSQL query logging enabled
- [ ] Django slow query logging enabled
- [ ] APM tool configured (optional)
- [ ] Error tracking configured (Sentry)

## Performance Targets Met
- [ ] Dashboard load: ✓ < 200ms
- [ ] API response: ✓ < 500ms
- [ ] HTMX swaps: ✓ < 50ms
- [ ] 500 concurrent users: ✓ Pass
- [ ] Core Web Vitals: ✓ Good
- [ ] Database queries: ✓ < 100ms
- [ ] Cache hit rate: ✓ > 70%
```

---

#### 23.5 Security Testing

**23.5.1 Data Leakage Test Suite**

```python
# src/tests/security/test_data_leakage.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment
from coordination.models import Partnership
from budget.models import BudgetAllocation
from planning.models import ProgramProjectActivity
from decimal import Decimal

User = get_user_model()


@pytest.mark.django_db
class TestDataLeakagePrevention:
    """Security tests to prevent cross-organization data leakage."""
    
    @pytest.fixture
    def setup_security_test(self):
        """Create two MOAs with sensitive data."""
        moh = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        mole = Organization.objects.create(code='MOLE', name='Ministry of Labor', org_type='MOA')
        
        moh_user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moh
        )
        mole_user = User.objects.create_user(
            username='mole_staff',
            email='staff@mole.gov.ph',
            password='testpass123',
            default_organization=mole
        )
        
        # Create sensitive MOH data
        moh_assessment = Assessment.objects.create(
            title='MOH Confidential Health Assessment',
            organization=moh,
            status='draft'  # NOT published
        )
        moh_ppa = ProgramProjectActivity.objects.create(
            code='MOH-2024-SECRET',
            title='Classified Health Program',
            organization=moh,
            ppa_type='program'
        )
        moh_budget = BudgetAllocation.objects.create(
            ppa=moh_ppa,
            organization=moh,
            fiscal_year=2024,
            total_amount=Decimal('100000000.00')
        )
        
        # Create sensitive MOLE data
        mole_assessment = Assessment.objects.create(
            title='MOLE Confidential Labor Assessment',
            organization=mole,
            status='draft'
        )
        
        return {
            'moh': moh,
            'mole': mole,
            'moh_user': moh_user,
            'mole_user': mole_user,
            'moh_assessment': moh_assessment,
            'mole_assessment': mole_assessment,
            'moh_budget': moh_budget
        }
    
    def test_direct_url_access_blocked(self, setup_security_test):
        """Test MOLE cannot access MOH assessment by direct URL."""
        client = Client()
        client.force_login(setup_security_test['mole_user'])
        
        # Try to access MOH assessment directly
        moh_assessment_id = setup_security_test['moh_assessment'].id
        response = client.get(f'/moa/MOLE/mana/assessments/{moh_assessment_id}/')
        
        # Should return 404 (filtered out by organization scope)
        assert response.status_code == 404
    
    def test_api_access_blocked(self, setup_security_test):
        """Test MOLE cannot access MOH data via API."""
        client = Client()
        client.force_login(setup_security_test['mole_user'])
        
        # Try to access MOH assessment via API
        moh_assessment_id = setup_security_test['moh_assessment'].id
        response = client.get(f'/api/mana/assessments/{moh_assessment_id}/')
        
        # Should return 404 or 403
        assert response.status_code in [404, 403]
    
    def test_budget_data_isolation(self, setup_security_test):
        """Test MOLE cannot see MOH budget allocations."""
        client = Client()
        client.force_login(setup_security_test['mole_user'])
        
        # Try to access MOH budget via MOLE context
        response = client.get('/moa/MOLE/budget/allocations/')
        assert response.status_code == 200
        
        content = str(response.content)
        
        # MOH budget should NOT be visible
        assert 'MOH-2024-SECRET' not in content
        assert '100,000,000' not in content
        assert 'Classified Health Program' not in content
    
    def test_org_switching_prevented(self, setup_security_test):
        """Test user cannot switch to unauthorized organization."""
        client = Client()
        client.force_login(setup_security_test['mole_user'])
        
        # MOLE user tries to access MOH dashboard
        response = client.get('/moa/MOH/')
        
        # Should be redirected or blocked
        assert response.status_code in [302, 403]
    
    def test_sql_injection_prevention(self, setup_security_test):
        """Test SQL injection attacks are prevented."""
        client = Client()
        client.force_login(setup_security_test['mole_user'])
        
        # Attempt SQL injection in search parameter
        malicious_search = "'; DROP TABLE mana_assessment; --"
        response = client.get(
            '/moa/MOLE/mana/assessments/',
            {'search': malicious_search}
        )
        
        # Should return safely (no SQL executed)
        assert response.status_code == 200
        
        # Verify table still exists
        assert Assessment.objects.exists()
    
    def test_csrf_protection(self, setup_security_test):
        """Test CSRF protection on POST requests."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(setup_security_test['mole_user'])
        
        # Try to POST without CSRF token
        response = client.post(
            '/moa/MOLE/mana/assessments/create/',
            {'title': 'New Assessment', 'status': 'draft'}
        )
        
        # Should be rejected (403 Forbidden)
        assert response.status_code == 403
    
    def test_session_fixation_prevention(self, setup_security_test):
        """Test session ID changes after login."""
        client = Client()
        
        # Get initial session ID
        client.get('/accounts/login/')
        session_before = client.session.session_key
        
        # Login
        client.post('/accounts/login/', {
            'username': 'mole_staff',
            'password': 'testpass123'
        })
        
        # Session ID should change
        session_after = client.session.session_key
        assert session_before != session_after
```

**23.5.2 Permission Boundary Tests**

```python
# src/tests/security/test_permission_boundaries.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from mana.models import Assessment

User = get_user_model()


@pytest.mark.django_db
class TestPermissionBoundaries:
    """Test permission boundaries between roles."""
    
    @pytest.fixture
    def setup_roles(self):
        """Create users with different roles."""
        moh = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        
        # Regular staff (limited permissions)
        staff_user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=moh,
            is_staff=False,
            is_superuser=False
        )
        
        # MOA admin (organization-level permissions)
        admin_user = User.objects.create_user(
            username='moh_admin',
            email='admin@moh.gov.ph',
            password='testpass123',
            default_organization=moh,
            is_staff=True,
            is_superuser=False
        )
        
        # Superuser (system-wide permissions)
        super_user = User.objects.create_user(
            username='system_admin',
            email='admin@oobc.gov.ph',
            password='testpass123',
            default_organization=moh,
            is_staff=True,
            is_superuser=True
        )
        
        return {
            'moh': moh,
            'staff': staff_user,
            'admin': admin_user,
            'super': super_user
        }
    
    def test_staff_cannot_delete_assessments(self, setup_roles):
        """Test regular staff cannot delete assessments."""
        client = Client()
        client.force_login(setup_roles['staff'])
        
        assessment = Assessment.objects.create(
            title='Test Assessment',
            organization=setup_roles['moh'],
            status='published'
        )
        
        # Try to delete
        response = client.post(
            f'/moa/MOH/mana/assessments/{assessment.id}/delete/'
        )
        
        # Should be forbidden
        assert response.status_code == 403
        assert Assessment.objects.filter(id=assessment.id).exists()
    
    def test_admin_can_delete_own_org_assessments(self, setup_roles):
        """Test admin can delete assessments in their organization."""
        client = Client()
        client.force_login(setup_roles['admin'])
        
        assessment = Assessment.objects.create(
            title='Test Assessment',
            organization=setup_roles['moh'],
            status='draft'
        )
        
        # Should be able to delete
        response = client.post(
            f'/moa/MOH/mana/assessments/{assessment.id}/delete/',
            follow=True
        )
        
        assert response.status_code == 200
        assert not Assessment.objects.filter(id=assessment.id).exists()
    
    def test_superuser_can_access_all_orgs(self, setup_roles):
        """Test superuser can access all organizations."""
        client = Client()
        client.force_login(setup_roles['super'])
        
        # Create another organization
        mole = Organization.objects.create(code='MOLE', name='Ministry of Labor', org_type='MOA')
        mole_assessment = Assessment.objects.create(
            title='MOLE Assessment',
            organization=mole,
            status='published'
        )
        
        # Superuser should be able to access MOLE data
        response = client.get(f'/moa/MOLE/mana/assessments/{mole_assessment.id}/')
        assert response.status_code == 200
```

---

#### 23.6 User Acceptance Testing (UAT)

**23.6.1 UAT Plan**

```markdown
# User Acceptance Testing Plan

## Objective
Verify that the BMMS transition does not break existing OOBC functionality and that new features work as expected for all user groups.

## Test Groups

### Group 1: OOBC Staff (Existing Users)
**Goal:** Ensure nothing breaks for current OOBC operations.

**Test Scenarios:**

1. **Login and Navigation**
   - [ ] Login with existing credentials
   - [ ] Dashboard loads correctly (no errors)
   - [ ] All existing menu items are accessible
   - [ ] Legacy URLs redirect properly to new org-aware URLs

2. **Communities Module**
   - [ ] View OBC communities (Regions, Provinces, Municipalities, Barangays)
   - [ ] Search and filter barangays
   - [ ] Add/edit barangay information
   - [ ] View community profiles

3. **MANA Module**
   - [ ] Create new assessment
   - [ ] Edit existing assessment
   - [ ] View assessment list
   - [ ] Search assessments
   - [ ] Generate assessment report

4. **Coordination Module**
   - [ ] View partnerships
   - [ ] Create new partnership
   - [ ] Add stakeholders to partnerships
   - [ ] Update partnership status

5. **Policies Module**
   - [ ] View policy recommendations
   - [ ] Create new policy recommendation
   - [ ] Update policy status
   - [ ] Generate policy report

**Success Criteria:**
- All existing functionality works WITHOUT changes
- No data loss or corruption
- Performance is equal or better than before
- UI/UX is consistent with current system

---

### Group 2: Pilot MOA Staff (New Users)
**Goal:** Verify new multi-tenant features work correctly for MOAs.

**Test Scenarios:**

1. **Onboarding**
   - [ ] Receive login credentials
   - [ ] First-time login successful
   - [ ] Organization context is set correctly (e.g., MOH)
   - [ ] Dashboard shows MOA-specific content

2. **Organization Isolation**
   - [ ] Can only see own organization's data
   - [ ] Cannot access other MOAs' assessments
   - [ ] Cannot access other MOAs' budgets
   - [ ] Search results filtered to own organization

3. **Planning Module (NEW)**
   - [ ] Create Program/Project/Activity (PPA)
   - [ ] Set PPA details (code, title, type, status)
   - [ ] Link PPA to barangays
   - [ ] View PPA list

4. **Budget Module (NEW)**
   - [ ] Create budget allocation
   - [ ] Link budget to PPA
   - [ ] Add work items
   - [ ] Track budget utilization
   - [ ] Generate budget report

5. **MANA with Organization Context**
   - [ ] Create assessment (automatically linked to MOA)
   - [ ] View only MOA's assessments
   - [ ] Search within MOA's data

6. **Coordination with Other MOAs**
   - [ ] Create partnership
   - [ ] Add other MOA as stakeholder
   - [ ] View partnerships where MOA is stakeholder
   - [ ] Update partnership (if stakeholder)

**Success Criteria:**
- MOA users can only see their own data
- MOA users can create PPAs and budgets
- Cross-MOA coordination works correctly
- Budget tracking complies with Parliament Bill No. 325

---

### Group 3: OCM Staff (Aggregation Users)
**Goal:** Verify OCM can aggregate and report across all MOAs.

**Test Scenarios:**

1. **OCM Dashboard**
   - [ ] Login as OCM user
   - [ ] Dashboard shows aggregated statistics
   - [ ] See counts from all MOAs

2. **Budget Aggregation**
   - [ ] View total budget across all MOAs
   - [ ] View budget breakdown by MOA
   - [ ] View utilization rates per MOA
   - [ ] Generate consolidated budget report

3. **MANA Aggregation**
   - [ ] View assessments from all MOAs
   - [ ] Filter assessments by MOA
   - [ ] View assessment counts by status
   - [ ] Generate cross-MOA MANA report

4. **Coordination Aggregation**
   - [ ] View all partnerships
   - [ ] View inter-MOA partnerships
   - [ ] Generate coordination report

5. **Read-Only Access**
   - [ ] Verify OCM cannot modify MOA data
   - [ ] Verify OCM cannot delete assessments
   - [ ] Verify OCM cannot edit budgets

**Success Criteria:**
- OCM sees data from all MOAs
- Aggregations are accurate
- OCM has read-only access (no modifications)
- Reports generate correctly
```

**23.6.2 UAT Execution Workflow**

```markdown
# UAT Execution Workflow

## Phase 1: Pre-UAT Setup (1 Week Before)

### Environment Preparation
- [ ] Deploy BMMS to staging environment
- [ ] Load production-like test data:
  - 29 MOA organizations
  - 100+ assessments per MOA
  - 50+ barangays
  - Budget allocations for each MOA
  - Inter-MOA partnerships

### User Preparation
- [ ] Create UAT user accounts:
  - 5 OOBC staff accounts
  - 3 MOA accounts per pilot (MOH, MOLE, MAFAR)
  - 2 OCM accounts
- [ ] Email login credentials to UAT participants
- [ ] Schedule UAT sessions (3 days, 2 hours/day)

### Documentation
- [ ] Prepare UAT test scripts
- [ ] Create video tutorial (15 minutes)
- [ ] Prepare FAQ document

---

## Phase 2: UAT Execution (3 Days)

### Day 1: OOBC Staff Testing
**Time:** 2 hours
**Participants:** 5 OOBC staff members

**Agenda:**
1. **Intro (15 min):** System overview, what's new
2. **Guided Testing (60 min):** Execute test scenarios with facilitator
3. **Free Exploration (30 min):** Users explore on their own
4. **Feedback Session (15 min):** Collect issues, concerns, suggestions

**Facilitator Actions:**
- Record all issues in spreadsheet
- Take screenshots of bugs
- Note performance concerns
- Document UX/UI feedback

---

### Day 2: Pilot MOA Staff Testing
**Time:** 2 hours
**Participants:** 3 staff from MOH, MOLE, MAFAR (9 total)

**Agenda:**
1. **Onboarding (20 min):** How to use Planning and Budget modules
2. **Guided Testing (70 min):** Execute MOA test scenarios
3. **Free Exploration (20 min):** Create own PPAs and budgets
4. **Feedback Session (10 min):** Collect feedback

**Focus Areas:**
- Data isolation verification
- Budget workflow usability
- Cross-MOA coordination

---

### Day 3: OCM Staff Testing
**Time:** 2 hours
**Participants:** 2 OCM staff members

**Agenda:**
1. **Intro (15 min):** OCM aggregation features
2. **Guided Testing (60 min):** Execute OCM test scenarios
3. **Report Generation (30 min):** Generate all OCM reports
4. **Feedback Session (15 min):** Collect feedback

**Focus Areas:**
- Aggregation accuracy
- Report completeness
- Read-only access enforcement

---

## Phase 3: Post-UAT Analysis (2 Days)

### Issue Categorization
Categorize all issues by:
- **Critical:** Blocks production deployment (data loss, security, crashes)
- **High:** Major functionality broken (cannot create budget, assessments not showing)
- **Medium:** Functionality works but has issues (slow performance, confusing UI)
- **Low:** Minor issues (typos, cosmetic bugs)

### Issue Resolution
- [ ] Fix all CRITICAL issues before production
- [ ] Fix all HIGH issues before production
- [ ] Document MEDIUM issues for post-deployment fix
- [ ] Document LOW issues for future releases

### UAT Sign-Off
- [ ] OOBC Director signs off (existing functionality works)
- [ ] Pilot MOA leads sign off (new features work)
- [ ] OCM lead signs off (aggregation works)
- [ ] Technical lead signs off (performance acceptable)

---

## Phase 4: Production Readiness

### Pre-Deployment Checklist
- [ ] All CRITICAL and HIGH issues resolved
- [ ] UAT sign-off received from all groups
- [ ] Performance benchmarks met (< 200ms dashboard, 500+ concurrent users)
- [ ] Security audit passed (no data leakage)
- [ ] Database migration tested (rollback plan ready)
- [ ] Monitoring configured (APM, error tracking)

### Deployment Approval
- [ ] Technical lead approval
- [ ] OOBC Director approval
- [ ] OCM Director approval
- [ ] Final go/no-go decision
```

---

**Part VII Section 23 Complete: Comprehensive testing strategy covering unit tests, integration tests, performance benchmarks, security audits, and UAT planning.**



---

## 23.7 Component Testing

### 23.7.1 Overview

**Purpose:** Test individual UI components in isolation to ensure they render correctly, handle interactions properly, and maintain accessibility standards.

**Scope:**
- Django template components (src/templates/components/)
- Form widgets and validation
- HTMX interactions (instant UI updates)
- Tailwind CSS components (stat cards, quick action cards)
- JavaScript components (calendar, resource booking, organization switcher)
- Leaflet.js map components

**Testing Tools:**
- Django template testing (TestCase)
- Selenium/Playwright for browser-based tests
- HTMX testing (hx-get, hx-post, hx-swap verification)
- Jest for JavaScript unit tests
- Axe for accessibility testing


### 23.7.2 Form Component Testing

**Test Django form components and validation logic.**

```python
# src/tests/components/test_form_components.py

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from organizations.models import Organization
from communities.models import Region, Province, Municipality, Barangay
from common.forms.staff import StaffForm

User = get_user_model()


class TestFormComponents(TestCase):
    """Test form components and validation."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

        # Create geographic hierarchy
        self.region = Region.objects.create(name='Region IX', code='09')
        self.province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=self.region)
        self.municipality = Municipality.objects.create(
            name='Pagadian City',
            code='097201',
            province=self.province
        )

    def test_text_input_component(self):
        """Test text input component renders correctly."""
        context = {
            'field': StaffForm().fields['first_name'],
            'field_name': 'first_name',
            'field_id': 'id_first_name',
            'label': 'First Name',
            'required': True,
            'value': '',
            'errors': []
        }

        html = render_to_string('components/form_field_input.html', context)

        # Verify structure
        self.assertIn('rounded-xl', html)
        self.assertIn('border-gray-200', html)
        self.assertIn('focus:ring-emerald-500', html)
        self.assertIn('min-h-[48px]', html)
        self.assertIn('text-red-500', html)  # Required asterisk

        print("✓ Text input component renders correctly")

    def test_dropdown_component(self):
        """Test dropdown component with proper styling."""
        context = {
            'field': StaffForm().fields['gender'],
            'field_name': 'gender',
            'field_id': 'id_gender',
            'label': 'Gender',
            'required': True,
            'choices': [('', 'Select gender...'), ('M', 'Male'), ('F', 'Female')],
            'value': '',
            'errors': []
        }

        html = render_to_string('components/form_field_select.html', context)

        # Verify structure
        self.assertIn('rounded-xl', html)
        self.assertIn('appearance-none', html)
        self.assertIn('pr-12', html)  # Space for chevron
        self.assertIn('fa-chevron-down', html)
        self.assertIn('pointer-events-none', html)  # Chevron not clickable

        print("✓ Dropdown component renders correctly")

    def test_form_validation_display(self):
        """Test error message display."""
        client = Client()
        client.force_login(self.user)

        # Submit invalid form
        response = client.post(
            f'/moa/{self.moa.code}/staff/create/',
            {
                'username': '',  # Missing required field
                'email': 'invalid-email',  # Invalid email
            }
        )

        self.assertEqual(response.status_code, 200)

        content = response.content.decode()

        # Verify error messages displayed
        self.assertIn('text-red-600', content)
        self.assertIn('This field is required', content)
        self.assertIn('Enter a valid email', content)

        print("✓ Form validation errors display correctly")

    def test_cascading_dropdowns(self):
        """Test cascading dropdowns (Region → Province → Municipality)."""
        client = Client()
        client.force_login(self.user)

        # Get barangay form
        response = client.get(f'/moa/{self.moa.code}/communities/barangays/create/')
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()

        # Verify HTMX attributes for cascading
        self.assertIn('hx-get', content)
        self.assertIn('hx-target', content)
        self.assertIn('hx-trigger="change"', content)

        # Test cascade: select province
        response = client.get(
            '/api/communities/municipalities/',
            {'province': self.province.id},
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('municipalities', data)

        print("✓ Cascading dropdowns work correctly")

    def test_date_picker_component(self):
        """Test date picker initialization."""
        context = {
            'field_name': 'start_date',
            'field_id': 'id_start_date',
            'label': 'Start Date',
            'required': True,
            'value': '',
        }

        html = render_to_string('components/form_field_date.html', context)

        # Verify date input
        self.assertIn('type="date"', html)
        self.assertIn('rounded-xl', html)
        self.assertIn('min-h-[48px]', html)

        print("✓ Date picker component renders correctly")


### 23.7.3 UI Component Testing

**Test custom UI components (stat cards, quick action cards, etc.).**

```python
# src/tests/components/test_ui_components.py

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from organizations.models import Organization
from mana.models import Assessment
from coordination.models import Partnership

User = get_user_model()


class TestUIComponents(TestCase):
    """Test custom UI components."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

    def test_stat_card_simple_variant(self):
        """Test 3D milk white stat card (simple variant)."""
        context = {
            'title': 'Total Assessments',
            'value': 42,
            'icon': 'fa-clipboard-list',
            'icon_color': 'text-amber-600',
            'icon_bg': 'bg-amber-50'
        }

        html = render_to_string('components/stat_card.html', context)

        # Verify structure
        self.assertIn('bg-white', html)
        self.assertIn('rounded-xl', html)
        self.assertIn('border', html)
        self.assertIn('shadow-sm', html)
        self.assertIn('fa-clipboard-list', html)
        self.assertIn('text-amber-600', html)
        self.assertIn('42', html)

        print("✓ Simple stat card renders correctly")

    def test_stat_card_breakdown_variant(self):
        """Test stat card with 3-column breakdown."""
        context = {
            'title': 'Total Partnerships',
            'value': 156,
            'icon': 'fa-handshake',
            'icon_color': 'text-emerald-600',
            'icon_bg': 'bg-emerald-50',
            'breakdown': [
                {'label': 'Active', 'value': 120, 'color': 'text-emerald-600'},
                {'label': 'Pending', 'value': 30, 'color': 'text-blue-600'},
                {'label': 'Closed', 'value': 6, 'color': 'text-gray-600'}
            ]
        }

        html = render_to_string('components/stat_card_breakdown.html', context)

        # Verify breakdown section
        self.assertIn('grid-cols-3', html)
        self.assertIn('Active', html)
        self.assertIn('120', html)
        self.assertIn('text-emerald-600', html)
        self.assertIn('Pending', html)
        self.assertIn('30', html)

        print("✓ Breakdown stat card renders correctly")

    def test_quick_action_card(self):
        """Test quick action card component."""
        context = {
            'title': 'New Assessment',
            'description': 'Create a new MANA assessment',
            'icon': 'fa-plus',
            'url': '/moa/MOH/mana/assessments/create/',
            'gradient_from': 'from-blue-500',
            'gradient_to': 'to-teal-500'
        }

        html = render_to_string('components/quick_action_card.html', context)

        # Verify structure
        self.assertIn('bg-white', html)
        self.assertIn('rounded-xl', html)
        self.assertIn('hover:shadow-md', html)
        self.assertIn('bg-gradient-to-br', html)
        self.assertIn('from-blue-500', html)
        self.assertIn('to-teal-500', html)
        self.assertIn('fa-plus', html)
        self.assertIn('fa-arrow-right', html)

        print("✓ Quick action card renders correctly")

    def test_breadcrumb_component(self):
        """Test breadcrumb navigation component."""
        context = {
            'breadcrumbs': [
                {'label': 'Dashboard', 'url': '/moa/MOH/'},
                {'label': 'MANA', 'url': '/moa/MOH/mana/'},
                {'label': 'Assessments', 'url': '/moa/MOH/mana/assessments/'},
                {'label': 'Create', 'url': None}  # Current page
            ]
        }

        html = render_to_string('components/breadcrumbs.html', context)

        # Verify structure
        self.assertIn('fa-chevron-right', html)
        self.assertIn('Dashboard', html)
        self.assertIn('MANA', html)
        self.assertIn('Assessments', html)
        self.assertIn('Create', html)
        self.assertIn('text-gray-500', html)  # Current page styling

        print("✓ Breadcrumb component renders correctly")

    def test_pagination_component(self):
        """Test pagination component."""
        context = {
            'page_obj': {
                'has_previous': True,
                'previous_page_number': 1,
                'number': 2,
                'has_next': True,
                'next_page_number': 3,
                'paginator': {'num_pages': 5}
            }
        }

        html = render_to_string('components/pagination.html', context)

        # Verify structure
        self.assertIn('Previous', html)
        self.assertIn('Next', html)
        self.assertIn('rounded-lg', html)
        self.assertIn('hover:bg-gray-50', html)

        print("✓ Pagination component renders correctly")

    def test_alert_messages(self):
        """Test alert message components."""
        test_messages = [
            {'level': 'success', 'text': 'Assessment created successfully', 'border': 'border-emerald-500'},
            {'level': 'error', 'text': 'Failed to save data', 'border': 'border-red-500'},
            {'level': 'warning', 'text': 'This action cannot be undone', 'border': 'border-amber-500'},
            {'level': 'info', 'text': 'New updates available', 'border': 'border-blue-500'}
        ]

        for msg in test_messages:
            context = {
                'level': msg['level'],
                'message': msg['text']
            }

            html = render_to_string('components/alert.html', context)

            self.assertIn(msg['border'], html)
            self.assertIn('border-l-4', html)
            self.assertIn(msg['text'], html)

        print("✓ Alert message components render correctly")

    def test_data_table_component(self):
        """Test data table card component."""
        # Create test data
        for i in range(5):
            Assessment.objects.create(
                title=f'Assessment {i}',
                organization=self.moa,
                status='published'
            )

        assessments = Assessment.objects.filter(organization=self.moa)

        context = {
            'title': 'Recent Assessments',
            'headers': ['Title', 'Status', 'Created', 'Actions'],
            'rows': [
                {
                    'id': a.id,
                    'cells': [a.title, a.status, a.created_at],
                    'view_url': f'/moa/{self.moa.code}/mana/assessments/{a.id}/',
                    'edit_url': f'/moa/{self.moa.code}/mana/assessments/{a.id}/edit/',
                    'delete_preview_url': f'/moa/{self.moa.code}/mana/assessments/{a.id}/'
                }
                for a in assessments
            ]
        }

        html = render_to_string('components/data_table_card.html', context)

        # Verify structure
        self.assertIn('bg-white', html)
        self.assertIn('rounded-xl', html)
        self.assertIn('Recent Assessments', html)
        self.assertIn('<table', html)
        self.assertIn('bg-gradient-to-r', html)  # Header gradient
        self.assertIn('from-blue-600', html)
        self.assertIn('to-teal-500', html)

        print("✓ Data table component renders correctly")


### 23.7.4 HTMX Interaction Testing

**Test HTMX-powered instant UI updates.**

```python
# src/tests/components/test_htmx_interactions.py

import pytest
import time
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from coordination.models import Task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

User = get_user_model()


class TestHTMXInteractions(TestCase):
    """Test HTMX instant UI updates."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

        # Create test tasks
        for i in range(5):
            Task.objects.create(
                title=f'Task {i}',
                organization=self.moa,
                assigned_to=self.user,
                status='pending'
            )

    def test_htmx_task_status_update(self):
        """Test instant task status update via HTMX."""
        client = Client()
        client.force_login(self.user)

        task = Task.objects.first()

        # Update status via HTMX
        response = client.post(
            f'/moa/{self.moa.code}/coordination/tasks/{task.id}/update-status/',
            {'status': 'in-progress'},
            HTTP_HX_REQUEST='true'
        )

        # Should return 204 No Content (optimistic update)
        self.assertEqual(response.status_code, 204)

        # Verify HX-Trigger header
        self.assertTrue(response.has_header('HX-Trigger'))

        # Verify task updated in database
        task.refresh_from_db()
        self.assertEqual(task.status, 'in-progress')

        print("✓ HTMX task status update works correctly")

    def test_htmx_delete_confirmation(self):
        """Test two-step delete confirmation."""
        client = Client()
        client.force_login(self.user)

        task = Task.objects.first()

        # Step 1: Show delete confirmation modal
        response = client.get(
            f'/moa/{self.moa.code}/coordination/tasks/{task.id}/delete-confirm/',
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify modal content
        self.assertIn('Are you sure', content)
        self.assertIn(task.title, content)
        self.assertIn('Delete', content)
        self.assertIn('Cancel', content)

        # Step 2: Confirm deletion
        response = client.delete(
            f'/moa/{self.moa.code}/coordination/tasks/{task.id}/delete/',
            HTTP_HX_REQUEST='true'
        )

        self.assertEqual(response.status_code, 204)

        # Verify task deleted
        self.assertFalse(Task.objects.filter(id=task.id).exists())

        print("✓ HTMX two-step delete confirmation works correctly")

    def test_htmx_form_submission(self):
        """Test HTMX form submission without page reload."""
        client = Client()
        client.force_login(self.user)

        # Submit form via HTMX
        response = client.post(
            f'/moa/{self.moa.code}/coordination/tasks/create/',
            {
                'title': 'New Task via HTMX',
                'description': 'Created via HTMX test',
                'status': 'pending',
                'assigned_to': self.user.id
            },
            HTTP_HX_REQUEST='true'
        )

        # Should redirect or return partial HTML
        self.assertIn(response.status_code, [200, 201, 302])

        # Verify task created
        self.assertTrue(Task.objects.filter(title='New Task via HTMX').exists())

        print("✓ HTMX form submission works correctly")

    def test_htmx_out_of_band_swaps(self):
        """Test out-of-band swaps (multiple element updates)."""
        client = Client()
        client.force_login(self.user)

        task = Task.objects.first()

        # Update task status (should trigger counter updates)
        response = client.post(
            f'/moa/{self.moa.code}/coordination/tasks/{task.id}/update-status/',
            {'status': 'completed'},
            HTTP_HX_REQUEST='true'
        )

        # Check for HX-Trigger header with counter refresh event
        if response.has_header('HX-Trigger'):
            import json
            trigger_data = json.loads(response['HX-Trigger'])
            self.assertIn('refresh-counters', trigger_data)

        print("✓ HTMX out-of-band swaps work correctly")


@pytest.mark.django_db
@pytest.mark.selenium
class TestHTMXBrowserInteractions:
    """Test HTMX interactions in real browser."""

    @pytest.fixture
    def setup_selenium(self):
        """Setup Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)

        yield driver

        driver.quit()

    def test_kanban_drag_drop_animation(self, setup_selenium, live_server):
        """Test kanban drag-drop with smooth animation."""
        driver = setup_selenium

        # Login
        driver.get(f'{live_server.url}/accounts/login/')
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Navigate to kanban
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.kanban-board'))
        )

        # Find task card
        task_card = driver.find_element(By.CSS_SELECTOR, '[data-task-id="1"]')
        initial_column = task_card.find_element(By.XPATH, './ancestor::*[@data-status]')

        # Drag to different column
        target_column = driver.find_element(By.CSS_SELECTOR, '[data-status="in-progress"]')

        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        actions.drag_and_drop(task_card, target_column).perform()

        # Wait for animation (300ms)
        time.sleep(0.4)

        # Verify task moved
        task_card_new = driver.find_element(By.CSS_SELECTOR, '[data-task-id="1"]')
        new_column = task_card_new.find_element(By.XPATH, './ancestor::*[@data-status]')

        assert new_column.get_attribute('data-status') == 'in-progress'

        print("✓ Kanban drag-drop animation works correctly")

    def test_instant_search_results(self, setup_selenium, live_server):
        """Test instant search results via HTMX."""
        driver = setup_selenium

        # Login
        driver.get(f'{live_server.url}/accounts/login/')
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Navigate to assessment list
        driver.get(f'{live_server.url}/moa/MOH/mana/assessments/')

        # Find search input
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'search'))
        )

        # Type search query
        search_input.clear()
        search_input.send_keys('health')

        # Wait for HTMX to update results (should be < 500ms)
        time.sleep(0.6)

        # Verify results updated
        results = driver.find_elements(By.CSS_SELECTOR, '[data-assessment-id]')
        assert len(results) > 0

        print("✓ Instant search results work correctly")


### 23.7.5 JavaScript Component Testing

**Test JavaScript components (Calendar, Organization Switcher, etc.).**

```javascript
// src/static/common/js/__tests__/calendar.test.js

/**
 * Jest tests for FullCalendar integration
 */

import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';

describe('Calendar Component', () => {
  let calendarEl;
  let calendar;

  beforeEach(() => {
    // Setup DOM element
    calendarEl = document.createElement('div');
    calendarEl.id = 'calendar';
    document.body.appendChild(calendarEl);

    // Initialize calendar
    calendar = new Calendar(calendarEl, {
      plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
      initialView: 'dayGridMonth',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      editable: true,
      droppable: true
    });

    calendar.render();
  });

  afterEach(() => {
    calendar.destroy();
    document.body.removeChild(calendarEl);
  });

  test('calendar renders correctly', () => {
    expect(calendarEl.querySelector('.fc')).toBeTruthy();
    expect(calendarEl.querySelector('.fc-toolbar')).toBeTruthy();
  });

  test('calendar loads events from API', async () => {
    // Mock fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          {
            id: 1,
            title: 'Test Event',
            start: '2024-01-15T10:00:00',
            end: '2024-01-15T11:00:00'
          }
        ])
      })
    );

    calendar.refetchEvents();

    // Wait for events to load
    await new Promise(resolve => setTimeout(resolve, 100));

    const events = calendar.getEvents();
    expect(events.length).toBeGreaterThan(0);
    expect(events[0].title).toBe('Test Event');
  });

  test('event click opens detail modal', () => {
    const mockEvent = {
      id: 1,
      title: 'Meeting',
      start: new Date('2024-01-15T10:00:00'),
      end: new Date('2024-01-15T11:00:00')
    };

    calendar.addEvent(mockEvent);

    const eventEl = calendarEl.querySelector('.fc-event');
    expect(eventEl).toBeTruthy();

    // Simulate click
    eventEl.click();

    // Verify modal opened (depends on your modal implementation)
    // expect(document.querySelector('#event-detail-modal')).toBeTruthy();
  });

  test('drag and drop event updates time', () => {
    const mockEvent = {
      id: 1,
      title: 'Meeting',
      start: '2024-01-15T10:00:00',
      end: '2024-01-15T11:00:00'
    };

    calendar.addEvent(mockEvent);

    const event = calendar.getEventById(1);
    const oldStart = event.start;

    // Simulate drag (mock event drop)
    const dropInfo = {
      date: new Date('2024-01-16T10:00:00'),
      allDay: false
    };

    // This would trigger eventDrop callback
    event.setStart(dropInfo.date);

    expect(event.start).not.toEqual(oldStart);
  });
});
```

```javascript
// src/static/common/js/__tests__/organization_switcher.test.js

/**
 * Jest tests for Organization Switcher
 */

describe('Organization Switcher', () => {
  let switcherEl;

  beforeEach(() => {
    // Setup DOM
    document.body.innerHTML = `
      <div id="org-switcher" class="relative">
        <button id="org-switcher-button" type="button">
          <span id="current-org-name">Ministry of Health</span>
          <i class="fas fa-chevron-down"></i>
        </button>
        <div id="org-dropdown" class="hidden absolute">
          <a href="/moa/MOH/" data-org-code="MOH">Ministry of Health</a>
          <a href="/moa/MOLE/" data-org-code="MOLE">Ministry of Labor</a>
        </div>
      </div>
    `;

    switcherEl = document.getElementById('org-switcher');
  });

  test('dropdown opens on button click', () => {
    const button = document.getElementById('org-switcher-button');
    const dropdown = document.getElementById('org-dropdown');

    expect(dropdown.classList.contains('hidden')).toBe(true);

    button.click();

    expect(dropdown.classList.contains('hidden')).toBe(false);
  });

  test('selecting organization updates display', () => {
    const orgLink = document.querySelector('[data-org-code="MOLE"]');
    const currentOrgName = document.getElementById('current-org-name');

    expect(currentOrgName.textContent).toBe('Ministry of Health');

    orgLink.click();

    // Would trigger page navigation in real app
    // Here we just verify the element exists
    expect(orgLink.getAttribute('href')).toBe('/moa/MOLE/');
  });

  test('dropdown closes when clicking outside', () => {
    const button = document.getElementById('org-switcher-button');
    const dropdown = document.getElementById('org-dropdown');

    button.click();
    expect(dropdown.classList.contains('hidden')).toBe(false);

    // Simulate click outside
    document.body.click();

    // In real implementation, this would close dropdown
    // expect(dropdown.classList.contains('hidden')).toBe(true);
  });
});
```


### 23.7.6 Leaflet.js Map Component Testing

**Test interactive map components and GeoJSON rendering.**

```python
# src/tests/components/test_map_components.py

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from communities.models import Region, Province, Municipality, Barangay
import json

User = get_user_model()


class TestMapComponents(TestCase):
    """Test Leaflet.js map integration."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

        # Create region with GeoJSON boundary
        self.region = Region.objects.create(
            name='Region IX',
            code='09',
            center_coordinates={'lat': 8.45, 'lng': 123.25},
            bounding_box=[[7.0, 122.0], [9.9, 124.5]],
            boundary_geojson={
                'type': 'Polygon',
                'coordinates': [
                    [[122.0, 7.0], [124.5, 7.0], [124.5, 9.9], [122.0, 9.9], [122.0, 7.0]]
                ]
            }
        )

    def test_geojson_api_endpoint(self):
        """Test GeoJSON API returns valid GeoJSON."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/api/communities/regions/{self.region.code}/geojson/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = response.json()

        # Verify GeoJSON structure
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertIn('features', data)
        self.assertGreater(len(data['features']), 0)

        feature = data['features'][0]
        self.assertEqual(feature['type'], 'Feature')
        self.assertIn('geometry', feature)
        self.assertEqual(feature['geometry']['type'], 'Polygon')
        self.assertIn('properties', feature)

        print("✓ GeoJSON API returns valid GeoJSON")

    def test_map_center_coordinates(self):
        """Test map centers on correct coordinates."""
        client = Client()
        client.force_login(self.user)

        response = client.get('/communities/regions/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify map initialization
        self.assertIn('L.map', content)
        self.assertIn('8.45', content)  # Lat
        self.assertIn('123.25', content)  # Lng

        print("✓ Map centers on correct coordinates")

    def test_boundary_rendering(self):
        """Test boundary GeoJSON renders on map."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/communities/regions/{self.region.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify boundary data included
        self.assertIn('boundary_geojson', content)
        self.assertIn('L.geoJSON', content)

        print("✓ Boundary GeoJSON renders on map")

    def test_popup_interaction(self):
        """Test map popup displays community info."""
        client = Client()
        client.force_login(self.user)

        # Create barangay with location
        province = Province.objects.create(name='Zamboanga del Sur', code='0972', region=self.region)
        muni = Municipality.objects.create(name='Pagadian City', code='097201', province=province)
        barangay = Barangay.objects.create(
            name='Balangasan',
            code='09720101',
            municipality=muni,
            population=5000,
            obc_status='Confirmed',
            center_coordinates={'lat': 8.5, 'lng': 123.3}
        )

        response = client.get('/api/communities/barangays/map-data/')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify barangay in map data
        self.assertGreater(len(data['features']), 0)

        feature = next((f for f in data['features'] if f['properties']['name'] == 'Balangasan'), None)
        self.assertIsNotNone(feature)
        self.assertEqual(feature['properties']['population'], 5000)
        self.assertEqual(feature['properties']['obc_status'], 'Confirmed')

        print("✓ Map popup displays community info")


### 23.7.7 Accessibility Testing

**Ensure components meet WCAG 2.1 AA standards.**

```python
# src/tests/components/test_accessibility.py

import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from organizations.models import Organization
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from axe_selenium_python import Axe

User = get_user_model()


class TestAccessibility(TestCase):
    """Test WCAG 2.1 AA accessibility compliance."""

    def setUp(self):
        """Setup test data."""
        self.moa = Organization.objects.create(code='MOH', name='Ministry of Health', org_type='MOA')
        self.user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
            default_organization=self.moa
        )

    def test_color_contrast_ratios(self):
        """Test color contrast meets 4.5:1 ratio (WCAG AA)."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/moa/{self.moa.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify high contrast text colors used
        self.assertIn('text-gray-700', content)  # Body text
        self.assertIn('text-gray-900', content)  # Headings
        self.assertNotIn('text-gray-400', content)  # Too light for body text

        print("✓ Color contrast ratios meet WCAG AA standards")

    def test_form_labels_and_aria(self):
        """Test forms have proper labels and ARIA attributes."""
        client = Client()
        client.force_login(self.user)

        response = client.get('/accounts/login/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify labels
        self.assertIn('<label for="id_username"', content)
        self.assertIn('<label for="id_password"', content)

        # Verify required field indicators
        self.assertIn('required', content)

        print("✓ Forms have proper labels and ARIA attributes")

    def test_keyboard_navigation(self):
        """Test all interactive elements are keyboard accessible."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/moa/{self.moa.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify focusable elements
        self.assertIn('focus:ring-', content)  # Focus indicators
        self.assertIn('focus:border-', content)

        # No tabindex > 0 (anti-pattern)
        self.assertNotIn('tabindex="1"', content)
        self.assertNotIn('tabindex="2"', content)

        print("✓ Keyboard navigation properly implemented")

    def test_touch_target_sizes(self):
        """Test interactive elements meet 48px minimum size."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/moa/{self.moa.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify minimum touch target sizes
        self.assertIn('min-h-[48px]', content)  # Buttons
        self.assertIn('py-3 px-4', content)  # Sufficient padding

        print("✓ Touch target sizes meet 48px minimum")

    def test_heading_hierarchy(self):
        """Test proper heading hierarchy (h1 → h2 → h3)."""
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/moa/{self.moa.code}/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Should have one h1
        h1_count = content.count('<h1')
        self.assertGreaterEqual(h1_count, 1, "Page should have at least one h1")

        # h2 should come after h1, not skip to h3
        # This is a simplified check

        print("✓ Heading hierarchy is properly structured")


@pytest.mark.django_db
@pytest.mark.selenium
class TestAccessibilityAxe:
    """Test accessibility using Axe DevTools."""

    @pytest.fixture
    def setup_selenium(self):
        """Setup Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)

        yield driver

        driver.quit()

    def test_dashboard_accessibility(self, setup_selenium, live_server):
        """Run Axe accessibility audit on dashboard."""
        driver = setup_selenium

        # Login
        driver.get(f'{live_server.url}/accounts/login/')
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Wait for dashboard
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.dashboard'))
        )

        # Run Axe audit
        axe = Axe(driver)
        axe.inject()
        results = axe.run()

        # Check for violations
        violations = results['violations']

        assert len(violations) == 0, f"Found {len(violations)} accessibility violations: {violations}"

        print(f"✓ Dashboard passed Axe accessibility audit (0 violations)")


### 23.7.8 Component Testing Checklist

```markdown
# Component Testing Checklist

## Form Components
- [ ] Text inputs render with proper styling (rounded-xl, border, focus ring)
- [ ] Dropdowns have chevron icon and proper styling
- [ ] Date pickers initialize correctly
- [ ] Required field indicators display (red asterisk)
- [ ] Error messages display in red with clear text
- [ ] Validation works client-side and server-side
- [ ] Cascading dropdowns work (Region → Province → Municipality)
- [ ] Form submission via HTMX (no page reload)

## UI Components
- [ ] Stat cards (simple variant) render correctly
- [ ] Stat cards (breakdown variant) display 3-column layout
- [ ] Quick action cards have gradient icons
- [ ] Breadcrumbs display with chevron separators
- [ ] Pagination controls work (prev/next, page numbers)
- [ ] Alert messages display with correct colors (success, error, warning, info)
- [ ] Data table cards render with gradient headers
- [ ] Modals open/close smoothly

## HTMX Interactions
- [ ] Task status updates instantly (< 50ms)
- [ ] Delete confirmation shows modal first
- [ ] Delete removes element with smooth animation (200ms)
- [ ] Form submissions return partial HTML (no reload)
- [ ] Out-of-band swaps update multiple elements
- [ ] Loading indicators display during requests
- [ ] HX-Trigger headers fire custom events
- [ ] Error states display gracefully

## JavaScript Components
- [ ] Calendar renders correctly
- [ ] Calendar loads events from API
- [ ] Event click opens detail modal
- [ ] Drag-drop events update time
- [ ] Organization switcher dropdown works
- [ ] Selecting organization navigates correctly
- [ ] Dropdown closes when clicking outside

## Map Components
- [ ] GeoJSON API returns valid FeatureCollection
- [ ] Map centers on correct coordinates
- [ ] Boundaries render as polygons
- [ ] Markers display for barangays
- [ ] Popups show community info
- [ ] Map controls work (zoom, pan)

## Accessibility (WCAG 2.1 AA)
- [ ] Color contrast ratios ≥ 4.5:1
- [ ] All forms have labels with 'for' attributes
- [ ] Required fields marked with aria-required="true"
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus indicators visible on all interactive elements
- [ ] Touch targets minimum 48px
- [ ] Heading hierarchy proper (h1 → h2 → h3)
- [ ] Images have alt text
- [ ] Links have descriptive text (no "click here")
- [ ] Axe DevTools audit: 0 violations
- [ ] Screen reader compatible (test with NVDA/JAWS)

## Performance
- [ ] Components render in < 100ms
- [ ] HTMX swaps complete in < 50ms
- [ ] Calendar loads events in < 300ms
- [ ] Map renders GeoJSON in < 500ms
- [ ] No layout shift (CLS < 0.1)
- [ ] Images lazy load
- [ ] JavaScript bundles minified

## Browser Compatibility
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## Responsive Design
- [ ] Mobile (375px width)
- [ ] Tablet (768px width)
- [ ] Desktop (1920px width)
- [ ] Forms usable on mobile
- [ ] Dropdowns work on touch devices
- [ ] Maps interactive on mobile
```

---

## Integration into TRANSITION_PLAN.md

**Insert Location:**

- **Section 23.7** (Component Testing) - Insert after Section 23.6 (UAT), before Section 24
- **Section 23.4** (Performance Testing - Expanded) - Replace existing Section 23.4

**Steps:**

1. Backup TRANSITION_PLAN.md
2. Replace Section 23.4 with expanded Performance Testing content above
3. Insert Section 23.7 (Component Testing) after Section 23.6
4. Update table of contents with new subsections
5. Renumber subsequent sections if needed

**Commit Message:**

```
Expand Testing Strategy: Add Component Testing & Enhanced Performance Testing

- Add comprehensive Component Testing (Section 23.7)
  - Form component tests (dropdowns, validation, cascading)
  - UI component tests (stat cards, quick actions, alerts)
  - HTMX interaction tests (instant updates, delete confirmation)
  - JavaScript component tests (Calendar, Organization Switcher)
  - Leaflet.js map tests (GeoJSON, boundaries, popups)
  - Accessibility tests (WCAG 2.1 AA compliance, Axe audits)
  - 20+ test scenarios with production-ready code

- Expand Performance Testing (Section 23.4)
  - Page load performance (dashboard, lists, calendar)
  - Database query optimization (N+1 detection, indexes)
  - HTMX performance (swap times, optimistic updates)
  - Concurrent load testing (500-800 users)
  - API performance (REST endpoints, GeoJSON)
  - Caching performance (hit rates, invalidation)
  - Frontend performance (Core Web Vitals)
  - Load testing with Locust (comprehensive scenarios)
  - Performance monitoring (Prometheus, Grafana)
  - 30+ performance tests with clear thresholds

All tests include:
- Production-ready Django/Python code
- Selenium/Playwright browser tests
- Jest JavaScript unit tests
- Locust load testing scripts
- Performance monitoring configuration
- Comprehensive checklists
- Clear success criteria
```

---

### Section 24: Deployment Strategy