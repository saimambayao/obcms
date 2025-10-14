# BMMS Multi-Tenant Architecture Diagram

**Visual Guide to OBCMS → BMMS Migration**
**Date:** October 14, 2025

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BMMS (Bangsamoro Ministerial Management System)       │
│                         44 BARMM Ministries, Offices, Agencies               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             User Authentication Layer                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ OCM Users    │  │ OOBC Users   │  │ MOA Users    │  │ LGU Users    │  │
│  │ (Read-Only)  │  │ (Full Access)│  │ (Own Org)    │  │ (Limited)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Organization Context Middleware                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Extract organization from URL, query params, session, or user default     │
│  • Set request.organization for all views                                    │
│  • Set request.is_ocm_user flag for special access                          │
│  • Enforce access control rules (OCM, OOBC, MOA)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RBAC (Role-Based Access Control)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │   Features       │  │   Permissions    │  │   Roles          │         │
│  │   (Menu Items)   │  │   (Actions)      │  │   (User Groups)  │         │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤         │
│  │ • Dashboard      │  │ • View           │  │ • Admin          │         │
│  │ • Communities    │  │ • Create         │  │ • Manager        │         │
│  │ • MANA           │  │ • Edit           │  │ • Staff          │         │
│  │ • Coordination   │  │ • Delete         │  │ • Viewer         │         │
│  │ • Planning       │  │ • Approve        │  │                  │         │
│  │ • Budget         │  │ • Export         │  │                  │         │
│  │ • M&E            │  │                  │  │                  │         │
│  │ • Policies       │  │                  │  │                  │         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
│                                                                               │
│  Organization-Scoped: Roles and permissions tied to specific MOAs            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Organization-Scoped Data Layer                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    OrganizationScopedModel (Abstract)                │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  • Automatic organization FK                                         │   │
│  │  • Auto-filtering by current organization (objects manager)         │   │
│  │  • Cross-organization access (all_objects manager)                  │   │
│  │  • Thread-local organization context                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │  Communities│    MANA     │ Coordination│   Planning  │   Budget    │  │
│  ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤  │
│  │OBCCommunity │ Assessment  │ Engagement  │Strategic    │ Proposal    │  │
│  │Coverage     │ Response    │ Partnership │ Plan        │ Disbursement│  │
│  │Data         │ Team        │ Feedback    │ Objective   │ Execution   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘  │
│                                                                               │
│  ┌─────────────┬─────────────┬─────────────────────────────────────────┐  │
│  │    M&E      │   Policies  │         Project Central                 │  │
│  ├─────────────┼─────────────┼─────────────────────────────────────────┤  │
│  │ PPA         │ Recommend-  │ WorkItem (Tasks, Activities, Projects)  │  │
│  │ Indicator   │ ation       │ Timeline                                │  │
│  │ Progress    │ Tracking    │ Dependencies                            │  │
│  └─────────────┴─────────────┴─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Database Layer (PostgreSQL)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Organization Table                 Geographic Reference Data (Shared)       │
│  ├─ OOBC                            ├─ Region                                │
│  ├─ MOH (Ministry of Health)        ├─ Province                              │
│  ├─ MOLE (Labor & Employment)       ├─ Municipality                          │
│  ├─ MAFAR (Agriculture)             ├─ Barangay                              │
│  ├─ ... (41 more MOAs)              └─ GeoJSON Boundaries (JSONField)        │
│  └─ OCM (Chief Minister Office)                                              │
│                                                                               │
│  All scoped data has organization_id FK with index for performance           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Isolation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Multi-Tenant Data Isolation                          │
└─────────────────────────────────────────────────────────────────────────────┘

Organization A (MOH)              Organization B (MOLE)            Organization C (MAFAR)
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│  Communities    │              │  Communities    │              │  Communities    │
│  ├─ MOH Comm 1  │              │  ├─ MOLE Comm 1 │              │  ├─ MAFAR Comm 1│
│  └─ MOH Comm 2  │              │  └─ MOLE Comm 2 │              │  └─ MAFAR Comm 2│
├─────────────────┤              ├─────────────────┤              ├─────────────────┤
│  Assessments    │              │  Assessments    │              │  Assessments    │
│  ├─ MOH Assess 1│              │  ├─ MOLE Assess 1│             │  ├─ MAFAR Assess│
│  └─ MOH Assess 2│              │  └─ MOLE Assess 2│             │  └─ MAFAR Assess│
├─────────────────┤              ├─────────────────┤              ├─────────────────┤
│  PPAs           │              │  PPAs           │              │  PPAs           │
│  ├─ MOH PPA 1   │              │  ├─ MOLE PPA 1  │              │  ├─ MAFAR PPA 1 │
│  └─ MOH PPA 2   │              │  └─ MOLE PPA 2  │              │  └─ MAFAR PPA 2 │
└─────────────────┘              └─────────────────┘              └─────────────────┘
       ▲                                  ▲                                  ▲
       │                                  │                                  │
       └──────────────────────────────────┼──────────────────────────────────┘
                                          │
                    ┌─────────────────────────────────────┐
                    │  Data Isolation Enforcement         │
                    ├─────────────────────────────────────┤
                    │  • OrganizationScopedModel filters │
                    │  • Middleware organization context  │
                    │  • Database-level FK constraints   │
                    │  • Permission checks in views       │
                    └─────────────────────────────────────┘

                    OCM (Office of Chief Minister)
                    ┌─────────────────────────────────────┐
                    │  Aggregated View (Read-Only)        │
                    ├─────────────────────────────────────┤
                    │  Can view all MOA data:             │
                    │  • MOH Communities, Assessments, PPAs│
                    │  • MOLE Communities, Assessments, PPAs│
                    │  • MAFAR Communities, Assessments, PPAs│
                    │  • ... all 44 MOAs                   │
                    │                                      │
                    │  Cannot edit any MOA data            │
                    └─────────────────────────────────────┘
```

---

## Request Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         User Request Flow                                 │
└──────────────────────────────────────────────────────────────────────────┘

1. User Login
   ├─ Authentication (Django Auth + JWT)
   ├─ User.user_type identified (bmoa, oobc_staff, cm_office, etc.)
   └─ User.organization_memberships loaded

2. Request Middleware Stack
   ├─ SessionMiddleware
   ├─ AuthenticationMiddleware
   ├─ OrganizationContextMiddleware  ◄─── Sets request.organization
   │  ├─ Check URL kwargs (org_id, organization_id)
   │  ├─ Check query params (?org=...)
   │  ├─ Check user's primary organization
   │  └─ Check session (current_organization)
   ├─ OCMAccessMiddleware  ◄─── Enforces OCM read-only
   └─ MessageMiddleware

3. View Layer
   ├─ Permission Check (RBAC)
   │  └─ RBACService.has_permission(request, 'communities.view_obc_community')
   │     ├─ Check user roles (for request.organization)
   │     ├─ Check role permissions
   │     └─ Check direct user permissions
   │
   ├─ Query Data (Organization-Scoped)
   │  └─ OBCCommunity.objects.all()  ◄─── Auto-filtered by organization
   │     ├─ OrganizationScopedManager.get_queryset()
   │     ├─ Filter by get_current_organization()
   │     └─ Return only current org's data
   │
   └─ Render Response
      ├─ Context includes organization info
      ├─ Template shows org-specific data
      └─ UI displays organization selector (for OOBC/OCM)

4. Response
   └─ HTTP 200 with organization-scoped data
```

---

## User Access Patterns

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         User Type Access Matrix                           │
└──────────────────────────────────────────────────────────────────────────┘

User Type          │ Access Level          │ Organizations Visible  │ Edit Rights
───────────────────┼───────────────────────┼────────────────────────┼────────────────
Superuser          │ ALL                   │ All 44 MOAs            │ Full (all orgs)
OCM User           │ Aggregated (Read-Only)│ All 44 MOAs            │ None (read-only)
OOBC Executive     │ Full                  │ OOBC + All MOAs        │ OOBC only
OOBC Staff         │ Full                  │ OOBC + All MOAs        │ OOBC only
MOA Admin          │ Organization-Scoped   │ Their MOA only         │ Their MOA only
MOA Manager        │ Organization-Scoped   │ Their MOA only         │ Their MOA only
MOA Staff          │ Organization-Scoped   │ Their MOA only         │ Their MOA only
MOA Viewer         │ Organization-Scoped   │ Their MOA only         │ None (read-only)
LGU User           │ Limited               │ Specific communities   │ Limited
Community Leader   │ Limited               │ Their community only   │ None (read-only)

┌──────────────────────────────────────────────────────────────────────────┐
│                    Organization Switching Rules                           │
└──────────────────────────────────────────────────────────────────────────┘

User Type          │ Can Switch Organizations? │ How?
───────────────────┼───────────────────────────┼────────────────────────────
Superuser          │ ✅ Yes                    │ Organization selector in navbar
OCM User           │ ✅ Yes                    │ Organization selector + All view
OOBC Executive     │ ✅ Yes                    │ Organization selector
OOBC Staff         │ ✅ Yes (limited)          │ Organization selector (readonly)
MOA Admin          │ ❌ No                     │ Locked to their MOA
MOA Staff          │ ❌ No                     │ Locked to their MOA
LGU User           │ ❌ No                     │ N/A
```

---

## Database Schema Relationships

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       Key Model Relationships                             │
└──────────────────────────────────────────────────────────────────────────┘

User ─────────────────┐
                      │
                      ├─── OrganizationMembership ───┬─── Organization (organizations app)
                      │         (M2M through)         │        ├─ OOBC
                      │                               │        ├─ MOH
                      ├─── UserRole ─────────────────┤        ├─ MOLE
                      │         (M2M)                 │        ├─ MAFAR
                      │                               │        └─ ... (44 total)
                      └─── UserPermission ────────────┘
                                │
                                └─── Permission
                                         │
                                         └─── Feature

Organization (organizations) ───┬─── OBCCommunity
                                ├─── Assessment
                                ├─── StakeholderEngagement
                                ├─── Partnership (lead_organization)
                                ├─── PPA (implementing_moa)
                                ├─── StrategicPlan
                                ├─── BudgetProposal
                                ├─── Disbursement
                                ├─── WorkItem
                                └─── ... (40+ models)

Organization (coordination) ────┬─── External Partners (NGOs, INGOs, etc.)
                                ├─── OrganizationContact
                                └─── Communication

Geographic Hierarchy (Shared):
Region ─── Province ─── Municipality ─── Barangay
         │                    │
         └─ GeoJSON           └─ GeoJSON
```

---

## Migration Phases Visualization

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         BMMS Migration Timeline                           │
└──────────────────────────────────────────────────────────────────────────┘

Phase 0: Foundation (PRE-PILOT)
═══════════════════════════════════════════════════════════════════════════
┌─────────────────────────────────────────────────────────────────────────┐
│ • Fix User model organization FK                                         │
│ • Update RBAC models organization FKs                                    │
│ • Create OOBC organization                                               │
│ • Migrate existing users and roles                                       │
│ ✅ OOBC continues to function normally                                   │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
Phase 1: Pilot Launch (PILOT MOAs)
═══════════════════════════════════════════════════════════════════════════
┌─────────────────────────────────────────────────────────────────────────┐
│ • Create pilot MOA organizations (MOH, MOLE, MAFAR)                      │
│ • Add organization FK to critical models:                                │
│   - OBCCommunity, Assessment, PPA                                        │
│ • Update queries with organization filtering                             │
│ ✅ Pilot MOAs can create data                                            │
│ ✅ Data isolation verified                                               │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
Phase 2: Expand Scoping (DURING PILOT)
═══════════════════════════════════════════════════════════════════════════
┌─────────────────────────────────────────────────────────────────────────┐
│ • Add organization FK to remaining models (40+ models)                   │
│ • Update all views, APIs, dashboards                                     │
│ • Performance optimization                                               │
│ ✅ All models organization-scoped                                        │
│ ✅ Query performance <300ms                                              │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
Phase 3: Full Rollout (44 MOAs)
═══════════════════════════════════════════════════════════════════════════
┌─────────────────────────────────────────────────────────────────────────┐
│ • Create remaining 41 MOA organizations                                  │
│ • Onboard in batches (8-10 MOAs per wave)                               │
│ • Scale testing and optimization                                         │
│ ✅ All 44 MOAs operational                                               │
│ ✅ OOBC continues to function                                            │
└─────────────────────────────────────────────────────────────────────────┘

Current Status: ⏸️ Awaiting Phase 0 Implementation
```

---

## Critical Points Visualization

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    Critical Dependencies Map                              │
└──────────────────────────────────────────────────────────────────────────┘

                                User Model
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              moa_organization      │         organization_memberships
              (DEPRECATED)          │         (NEW - M2M)
                    │               │               │
                    ▼               ▼               ▼
         coordination.Organization  │    organizations.Organization
         (External Partners)        │    (BARMM MOAs)
                    │               │               │
                    │               │               ├─── OBCCommunity
                    │               │               ├─── Assessment
                    │               │               ├─── PPA
                    │               │               └─── ... (40+ models)
                    │               │
                    └───────────────┼───────────────┘
                                    │
                        ⚠️ CRITICAL ISSUE:
                        User model points to WRONG Organization!
                        Must be fixed before BMMS pilot.

┌──────────────────────────────────────────────────────────────────────────┐
│                    Data Flow Visualization                                │
└──────────────────────────────────────────────────────────────────────────┘

Request ───► Middleware ───► RBAC Check ───► Query ───► Response
            (Set org)      (Check perms)   (Filter)   (Render)
                │               │              │           │
                │               │              │           │
            request.           has_          WHERE        context[
            organization      permission    organization  'organization'
                                            = current     ]

┌──────────────────────────────────────────────────────────────────────────┐
│                    Performance Bottlenecks                                │
└──────────────────────────────────────────────────────────────────────────┘

Potential Bottleneck         │ Mitigation Strategy
─────────────────────────────┼───────────────────────────────────────────────
Organization FK lookups      │ Database indexes on organization_id
Permission checks per request│ Redis caching (5-minute TTL)
Dashboard aggregations       │ Pre-computed stats, background jobs
Geographic data queries      │ JSONField (no PostGIS), spatial indexes
Cross-organization queries   │ Use all_objects manager (OCM only)
User role lookups            │ Eager loading with select_related()
```

---

## Security Boundaries

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    Data Isolation Security Layers                         │
└──────────────────────────────────────────────────────────────────────────┘

Layer 1: Database Constraints
═════════════════════════════════════════════════════════════════════════════
• organization_id NOT NULL (after migration)
• Foreign key constraints enforce referential integrity
• Indexes on organization_id for performance

Layer 2: ORM Manager Filtering
═════════════════════════════════════════════════════════════════════════════
• OrganizationScopedManager.get_queryset() auto-filters
• Thread-local storage for organization context
• all_objects manager for cross-org access (admin/OCM only)

Layer 3: Middleware Access Control
═════════════════════════════════════════════════════════════════════════════
• OrganizationContextMiddleware sets request.organization
• user_can_access_organization() checks user permissions
• OCMAccessMiddleware enforces read-only for OCM users

Layer 4: View-Level Permission Checks
═════════════════════════════════════════════════════════════════════════════
• @require_permission decorator on views
• RBACService.has_permission() checks organization context
• Manual checks for sensitive operations

Layer 5: Template-Level Filtering
═════════════════════════════════════════════════════════════════════════════
• {% if has_permission %} template tags
• Organization context displayed in UI
• Organization selector for authorized users

┌──────────────────────────────────────────────────────────────────────────┐
│                    Attack Vector Prevention                               │
└──────────────────────────────────────────────────────────────────────────┘

Attack Vector              │ Prevention Method
───────────────────────────┼───────────────────────────────────────────────
URL parameter tampering    │ user_can_access_organization() validation
Direct object reference    │ Organization FK check before serving data
Session hijacking          │ HTTPS only, secure cookies, CSRF protection
SQL injection              │ Django ORM parameterized queries
Cross-org data access      │ OrganizationScopedManager filtering
Privilege escalation       │ RBAC system with organization scoping
```

---

**For implementation details, see:**
- [OBCMS_ARCHITECTURAL_ANALYSIS.md](./OBCMS_ARCHITECTURAL_ANALYSIS.md) - Comprehensive analysis
- [ARCHITECTURAL_ANALYSIS_SUMMARY.md](./ARCHITECTURAL_ANALYSIS_SUMMARY.md) - Quick reference
- [TRANSITION_PLAN.md](./TRANSITION_PLAN.md) - Phase-by-phase implementation
