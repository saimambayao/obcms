# BMMS Embedded Architecture - Visual Diagrams

**Reference:** Understanding OBCMS/BMMS dual-mode architecture
**Status:** ⚠️ CONFLICTS DETECTED - Phase -1 reconciliation required
**Revised:** 2025-10-14 (Post-Audit)

---

## 🔴 CRITICAL: Current State vs Target State

**⚠️ The following conflicts must be resolved BEFORE implementing Phase 0:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CURRENT STATE (WITH CONFLICTS) ⚠️                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Settings (base.py:638)                Middleware Stack (base.py:133)   │
│  ┌─────────────────────────┐          ┌──────────────────────────────┐ │
│  │ ENABLE_MULTI_TENANT:    │          │ OrganizationContextMiddleware│ │
│  │   default=True ⚠️       │          │  (common.middleware)         │ │
│  │ (should be mode-based)  │          │                              │ │
│  └─────────────────────────┘          │ Line 44: ⚠️ WRONG IMPORT    │ │
│                                       │   from coordination.models   │ │
│  ┌─────────────────────────┐          │   import Organization        │ │
│  │ BMMS_MODE: ❌ MISSING   │          │                              │ │
│  │ (mode detection broken) │          │ ⚠️ NOT MODE-AWARE           │ │
│  └─────────────────────────┘          │   (no OBCMS/BMMS logic)     │ │
│                                       └──────────────────────────────┘ │
│  ┌───────────────────────────────┐                                     │
│  │ DEFAULT_ORGANIZATION_CODE:    │    Organizations App (✅ READY)     │
│  │   ❌ MISSING                  │    ┌──────────────────────────────┐ │
│  │ (default org detection broken)│    │ Organization model ✅        │ │
│  └───────────────────────────────┘    │ OrganizationScopedModel ✅  │ │
│                                       │ OrganizationMiddleware ⚠️    │ │
│  Existing Models                       │  (conflicts with existing)  │ │
│  ┌───────────────────────────┐        └──────────────────────────────┘ │
│  │ ❌ No organization field  │                                         │
│  │   - MANA models           │        Thread-Local Context (✅ READY)  │
│  │   - Coordination models   │        ┌──────────────────────────────┐ │
│  │   - Other modules         │        │ get_current_organization() ✅│ │
│  └───────────────────────────┘        │ set_current_organization() ✅│ │
│                                       │ clear_current_org() ✅       │ │
│                                       └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    ⬇️
                  🔴 PHASE -1: RECONCILIATION REQUIRED (2 hours)
                  - Fix Organization import (5 min)
                  - Add BMMS_MODE config (15 min)
                  - Audit ENABLE_MULTI_TENANT (30 min)
                  - Resolve middleware strategy (1 hour)
                                    ⬇️
┌─────────────────────────────────────────────────────────────────────────┐
│                    TARGET STATE (AFTER PHASE -1) ✅                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Settings (base.py + bmms_config.py)   Middleware Stack                │
│  ┌─────────────────────────┐          ┌──────────────────────────────┐ │
│  │ BMMS_MODE: obcms ✅     │          │ Refactored Middleware ✅     │ │
│  │   (from .env)           │          │  (mode-aware)                │ │
│  └─────────────────────────┘          │                              │ │
│                                       │ Correct import: ✅           │ │
│  ┌─────────────────────────┐          │   from organizations.models  │ │
│  │ DEFAULT_ORGANIZATION_   │          │   import Organization        │ │
│  │ CODE: OOBC ✅           │          │                              │ │
│  │   (from .env)           │          │ Mode-aware logic: ✅         │ │
│  └─────────────────────────┘          │   if is_obcms_mode():        │ │
│                                       │     auto_inject_oobc()       │ │
│  ┌─────────────────────────┐          │   elif is_bmms_mode():       │ │
│  │ ENABLE_MULTI_TENANT:    │          │     extract_from_url()       │ │
│  │   default=False ✅      │          └──────────────────────────────┘ │
│  │   (mode-dependent)      │                                           │
│  └─────────────────────────┘          Organizations App (✅ READY)     │
│                                       ┌──────────────────────────────┐ │
│  Existing Models (Phase 2+)            │ Organization model ✅        │ │
│  ┌───────────────────────────┐        │ OrganizationScopedModel ✅  │ │
│  │ ✅ organization field     │        │ No middleware conflicts ✅   │ │
│  │   - MANA (converted)      │        └──────────────────────────────┘ │
│  │   - Coordination          │                                         │
│  │   - Other modules         │        Thread-Local Context (✅ READY)  │
│  └───────────────────────────┘        ┌──────────────────────────────┐ │
│                                       │ get_current_organization() ✅│ │
│                                       │ set_current_organization() ✅│ │
│                                       │ clear_current_org() ✅       │ │
│                                       └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

**🔴 ACTION REQUIRED:**

Complete all Phase -1 fixes before proceeding with Phase 0 implementation.

**See:** [RECONCILIATION_PLAN.md](./RECONCILIATION_PLAN.md) for detailed fix instructions.

**Phase -1 Checklist:**
- [ ] Fix 1: Correct Organization import path (common/middleware/organization_context.py:44)
- [ ] Fix 2: Add BMMS_MODE configuration (.env and bmms_config.py)
- [ ] Fix 3: Audit and fix ENABLE_MULTI_TENANT default (base.py:638)
- [ ] Fix 4: Resolve middleware conflict (choose refactor vs replace strategy)
- [ ] Validation: All tests pass, `python manage.py check` succeeds

---

## 1. System Overview

```
┌───────────────────────────────────────────────────────────────────────┐
│                         OBCMS/BMMS System                             │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Configuration Layer (.env)                      │   │
│  │                                                              │   │
│  │  BMMS_MODE = 'obcms' | 'bmms'                               │   │
│  │  DEFAULT_ORGANIZATION_CODE = 'OOBC'                         │   │
│  │  ENABLE_MULTI_TENANT = True | False                          │   │
│  └────────────────────────┬─────────────────────────────────────┘   │
│                           │                                          │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Request Processing Pipeline                     │   │
│  │                                                              │   │
│  │  1. Django Request → AuthenticationMiddleware               │   │
│  │  2. OBCMSOrganizationMiddleware (OBCMS auto-inject)        │   │
│  │  3. OrganizationMiddleware (BMMS URL extraction)            │   │
│  │  4. View Processing                                          │   │
│  │  5. Template Rendering                                       │   │
│  └────────────────────────┬─────────────────────────────────────┘   │
│                           │                                          │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Data Layer (PostgreSQL)                         │   │
│  │                                                              │   │
│  │  All models have organization field                          │   │
│  │  Queries auto-filtered by OrganizationScopedManager         │   │
│  │  Data isolation enforced at database level                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mode Comparison

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        OBCMS vs BMMS Modes                               │
└──────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════╗
║                           OBCMS MODE                                  ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Configuration:                                                       ║
║    BMMS_MODE = 'obcms'                                               ║
║    DEFAULT_ORGANIZATION_CODE = 'OOBC'                                ║
║    ENABLE_MULTI_TENANT = False                                       ║
║                                                                       ║
║  Organization Handling:                                               ║
║    ✓ Auto-inject OOBC organization (OBCMSOrganizationMiddleware)    ║
║    ✓ No URL organization prefix required                             ║
║    ✓ Single-tenant operation                                         ║
║    ✓ No organization switching                                       ║
║                                                                       ║
║  URL Patterns:                                                        ║
║    /communities/              → OBCCommunity list                    ║
║    /mana/assessments/         → Assessment list                      ║
║    /coordination/activities/  → Activity list                        ║
║                                                                       ║
║  User Experience:                                                     ║
║    ✓ Seamless single-org experience                                  ║
║    ✓ No org selection required                                       ║
║    ✓ All OOBC staff see same data                                    ║
║    ✓ Clean, simple URLs                                              ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

                                  │
                                  │ Configuration Change Only
                                  │ (Restart application)
                                  ▼

╔═══════════════════════════════════════════════════════════════════════╗
║                           BMMS MODE                                   ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Configuration:                                                       ║
║    BMMS_MODE = 'bmms'                                                ║
║    DEFAULT_ORGANIZATION_CODE = 'OOBC'                                ║
║    ENABLE_MULTI_TENANT = True                                        ║
║                                                                       ║
║  Organization Handling:                                               ║
║    ✓ Extract org from URL: /moa/<CODE>/ (OrganizationMiddleware)   ║
║    ✓ Multi-tenant operation (44 MOAs)                                ║
║    ✓ Organization switching enabled                                  ║
║    ✓ Data isolation per organization                                 ║
║                                                                       ║
║  URL Patterns:                                                        ║
║    /moa/OOBC/communities/     → OOBC communities                     ║
║    /moa/MOH/mana/assessments/ → MOH assessments                      ║
║    /moa/MENR/coordination/    → MENR activities                      ║
║                                                                       ║
║  User Experience:                                                     ║
║    ✓ Multi-org dashboard                                             ║
║    ✓ Organization selector                                           ║
║    ✓ Each MOA sees only their data                                   ║
║    ✓ OCM sees aggregated view (read-only)                            ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## 3. Request Flow

### OBCMS Mode Request Flow

```
User Request: /communities/
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│ 1. Django Request Handler                                     │
│    - URL: /communities/                                       │
│    - User: authenticated (john@oobc.gov.ph)                  │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 2. AuthenticationMiddleware                                   │
│    - Loads user from session                                  │
│    - Attaches user to request                                 │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 3. OBCMSOrganizationMiddleware                               │
│    - Detects OBCMS mode                                       │
│    - Gets default org: Organization.objects.get(code='OOBC') │
│    - Sets request.organization = OOBC                         │
│    - Sets thread-local: set_current_organization(OOBC)       │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 4. OrganizationMiddleware                                     │
│    - Detects OBCMS mode                                       │
│    - Skips (org already set by OBCMSOrganizationMiddleware) │
│    - Returns early                                            │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 5. View: community_list()                                     │
│    - @login_required decorator validates user                 │
│    - @require_organization decorator validates org context    │
│    - QuerySet: OBCCommunity.objects.all()                    │
│      → Auto-filtered to OOBC (OrganizationScopedManager)     │
│    - Returns only OOBC communities                            │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 6. Template Rendering                                         │
│    - Context includes: request.organization = OOBC            │
│    - Community list filtered to OOBC                          │
│    - Renders communities/list.html                            │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 7. Response                                                    │
│    - HTML page with OOBC communities                          │
│    - Clean URL: /communities/                                 │
└───────────────────────────────────────────────────────────────┘
```

---

### BMMS Mode Request Flow

```
User Request: /moa/MOH/mana/assessments/
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│ 1. Django Request Handler                                     │
│    - URL: /moa/MOH/mana/assessments/                         │
│    - User: authenticated (dr.ahmad@moh.barmm.gov.ph)         │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 2. AuthenticationMiddleware                                   │
│    - Loads user from session                                  │
│    - Attaches user to request                                 │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 3. OBCMSOrganizationMiddleware                               │
│    - Detects BMMS mode                                        │
│    - Skips (OrganizationMiddleware will handle)             │
│    - Returns early                                            │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 4. OrganizationMiddleware                                     │
│    - Detects BMMS mode                                        │
│    - Extracts org code from URL: "MOH"                        │
│    - Loads org: Organization.objects.get(code='MOH')         │
│    - Validates user access:                                   │
│      → OrganizationMembership.objects.filter(               │
│           user=dr.ahmad, organization=MOH, is_active=True)   │
│    - Sets request.organization = MOH                          │
│    - Sets thread-local: set_current_organization(MOH)        │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 5. View: assessment_list()                                    │
│    - @login_required decorator validates user                 │
│    - @require_organization decorator:                         │
│      → Validates org context exists                           │
│      → Validates user has access to MOH                       │
│    - QuerySet: Assessment.objects.all()                      │
│      → Auto-filtered to MOH (OrganizationScopedManager)      │
│    - Returns only MOH assessments                             │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 6. Template Rendering                                         │
│    - Context includes: request.organization = MOH             │
│    - Assessment list filtered to MOH                          │
│    - Renders mana/assessment_list.html                        │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│ 7. Response                                                    │
│    - HTML page with MOH assessments                           │
│    - URL includes org: /moa/MOH/mana/assessments/            │
└───────────────────────────────────────────────────────────────┘
```

---

## 4. Database Architecture

### Model Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                     OrganizationScopedModel                     │
│                        (Abstract Base)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Fields:                                                        │
│    organization → ForeignKey(Organization, PROTECT)            │
│                                                                 │
│  Managers:                                                      │
│    objects = OrganizationScopedManager()                       │
│      → Auto-filters by get_current_organization()              │
│      → Returns only current org's data                         │
│                                                                 │
│    all_objects = models.Manager()                              │
│      → No filtering                                            │
│      → Returns all organizations' data                         │
│      → Used by admin/OCM                                       │
│                                                                 │
│  Methods:                                                       │
│    save() → Auto-sets organization if not provided             │
│                                                                 │
│  Meta:                                                          │
│    abstract = True                                             │
│    indexes = [Index(fields=['organization'])]                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Inheritance
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  OBCCommunity   │    │   Assessment    │    │   Partnership   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│                 │    │                 │    │                 │
│ organization ✓  │    │ organization ✓  │    │ organization ✓  │
│ (inherited)     │    │ (inherited)     │    │ (inherited)     │
│                 │    │                 │    │                 │
│ objects ✓       │    │ objects ✓       │    │ objects ✓       │
│ (auto-filter)   │    │ (auto-filter)   │    │ (auto-filter)   │
│                 │    │                 │    │                 │
│ all_objects ✓   │    │ all_objects ✓   │    │ all_objects ✓   │
│ (unfiltered)    │    │ (unfiltered)    │    │ (unfiltered)    │
│                 │    │                 │    │                 │
│ barangay        │    │ title           │    │ partner_org     │
│ name            │    │ status          │    │ partnership_type│
│ population      │    │ start_date      │    │ start_date      │
│ ...             │    │ ...             │    │ ...             │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

### Query Behavior

```
┌─────────────────────────────────────────────────────────────────────┐
│                       QuerySet Behavior                             │
└─────────────────────────────────────────────────────────────────────┘

Scenario 1: OBCMS Mode with OOBC Organization
══════════════════════════════════════════════════════════════════════

Thread-Local: organization = OOBC

OBCCommunity.objects.all()
    ↓
OrganizationScopedManager.get_queryset()
    ↓
queryset.filter(organization=OOBC)
    ↓
SELECT * FROM communities_obc_community WHERE organization_id = 1

Result: Only OOBC communities returned ✓


Scenario 2: BMMS Mode with MOH Organization
══════════════════════════════════════════════════════════════════════

Thread-Local: organization = MOH

Assessment.objects.all()
    ↓
OrganizationScopedManager.get_queryset()
    ↓
queryset.filter(organization=MOH)
    ↓
SELECT * FROM mana_assessment WHERE organization_id = 3

Result: Only MOH assessments returned ✓


Scenario 3: Admin/OCM Cross-Organization Access
══════════════════════════════════════════════════════════════════════

Thread-Local: organization = OCM (or None)

OBCCommunity.all_objects.all()
    ↓
models.Manager.get_queryset()
    ↓
No filtering applied
    ↓
SELECT * FROM communities_obc_community

Result: All organizations' communities returned ✓


Scenario 4: No Organization Context (Error Case)
══════════════════════════════════════════════════════════════════════

Thread-Local: organization = None

OBCCommunity.objects.all()
    ↓
OrganizationScopedManager.get_queryset()
    ↓
No current organization → Return unfiltered
    ↓
SELECT * FROM communities_obc_community

Result: All communities returned (for migrations/management commands)
```

---

## 5. Three-Step Migration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   STEP 1: Add Nullable Field                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Migration File: 000X_add_organization_field.py                    │
│                                                                     │
│  operations = [                                                     │
│      migrations.AddField(                                           │
│          model_name='obccommunity',                                │
│          name='organization',                                       │
│          field=models.ForeignKey(                                   │
│              blank=True,                                            │
│              null=True,  ← NULLABLE                                │
│              ...                                                    │
│          ),                                                         │
│      ),                                                             │
│  ]                                                                  │
│                                                                     │
│  Database State After Step 1:                                       │
│  ┌────────────────────────────────────────────┐                   │
│  │ communities_obc_community                  │                   │
│  ├─────┬──────────┬───────────────────────────┤                   │
│  │ id  │ name     │ organization_id           │                   │
│  ├─────┼──────────┼───────────────────────────┤                   │
│  │ 1   │ Comm A   │ NULL ← Existing records   │                   │
│  │ 2   │ Comm B   │ NULL ← Existing records   │                   │
│  │ 3   │ Comm C   │ NULL ← Existing records   │                   │
│  └─────┴──────────┴───────────────────────────┘                   │
│                                                                     │
│  ✓ Field added                                                      │
│  ✓ Existing records unaffected                                     │
│  ✓ No data loss                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STEP 2: Populate Field                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Management Command: populate_organization_field                    │
│                                                                     │
│  Command: python manage.py populate_organization_field             │
│                                                                     │
│  Logic:                                                             │
│    1. Get default org: Organization.objects.get(code='OOBC')      │
│    2. Find records: Model.all_objects.filter(organization=None)    │
│    3. Update: .update(organization=default_org)                    │
│                                                                     │
│  Database State After Step 2:                                       │
│  ┌────────────────────────────────────────────┐                   │
│  │ communities_obc_community                  │                   │
│  ├─────┬──────────┬───────────────────────────┤                   │
│  │ id  │ name     │ organization_id           │                   │
│  ├─────┼──────────┼───────────────────────────┤                   │
│  │ 1   │ Comm A   │ 1 (OOBC) ← Populated      │                   │
│  │ 2   │ Comm B   │ 1 (OOBC) ← Populated      │                   │
│  │ 3   │ Comm C   │ 1 (OOBC) ← Populated      │                   │
│  └─────┴──────────┴───────────────────────────┘                   │
│                                                                     │
│  ✓ All records have organization                                    │
│  ✓ Data integrity maintained                                        │
│  ✓ Ready for Step 3                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STEP 3: Make Field Required                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Migration File: 000Y_make_organization_required.py                │
│                                                                     │
│  operations = [                                                     │
│      migrations.AlterField(                                         │
│          model_name='obccommunity',                                │
│          name='organization',                                       │
│          field=models.ForeignKey(                                   │
│              # NO blank=True, null=True ← REQUIRED                 │
│              ...                                                    │
│          ),                                                         │
│      ),                                                             │
│  ]                                                                  │
│                                                                     │
│  Database State After Step 3:                                       │
│  ┌────────────────────────────────────────────┐                   │
│  │ communities_obc_community                  │                   │
│  ├─────┬──────────┬───────────────────────────┤                   │
│  │ id  │ name     │ organization_id NOT NULL  │ ← Constraint      │
│  ├─────┼──────────┼───────────────────────────┤                   │
│  │ 1   │ Comm A   │ 1 (OOBC)                  │                   │
│  │ 2   │ Comm B   │ 1 (OOBC)                  │                   │
│  │ 3   │ Comm C   │ 1 (OOBC)                  │                   │
│  └─────┴──────────┴───────────────────────────┘                   │
│                                                                     │
│  ✓ NOT NULL constraint enforced                                    │
│  ✓ Future records must have organization                           │
│  ✓ Migration complete                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. URL Routing Patterns

```
┌─────────────────────────────────────────────────────────────────────┐
│                     OBCMS Mode URL Patterns                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Pattern: /app_name/view_name/                                     │
│                                                                     │
│  Examples:                                                          │
│    /                           → Dashboard                         │
│    /communities/               → Community list                    │
│    /communities/create/        → Create community                  │
│    /communities/123/           → Community detail                  │
│    /communities/123/edit/      → Edit community                    │
│    /mana/                      → MANA dashboard                    │
│    /mana/assessments/          → Assessment list                   │
│    /mana/assessments/456/      → Assessment detail                 │
│    /coordination/              → Coordination dashboard            │
│    /coordination/activities/   → Activity list                     │
│                                                                     │
│  Characteristics:                                                   │
│    ✓ Clean, simple URLs                                            │
│    ✓ No organization prefix                                        │
│    ✓ Organization implicit (OOBC)                                  │
│    ✓ Traditional Django URL structure                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

                                │
                                │ Mode Switch
                                ▼

┌─────────────────────────────────────────────────────────────────────┐
│                     BMMS Mode URL Patterns                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Pattern: /moa/<org_code>/app_name/view_name/                     │
│                                                                     │
│  Examples:                                                          │
│    /moa/OOBC/                  → OOBC Dashboard                    │
│    /moa/OOBC/communities/      → OOBC Community list              │
│    /moa/MOH/                   → MOH Dashboard                     │
│    /moa/MOH/mana/assessments/  → MOH Assessment list              │
│    /moa/MENR/planning/         → MENR Planning                     │
│    /moa/OCM/                   → OCM Aggregation Dashboard         │
│                                                                     │
│  Multi-Organization Navigation:                                     │
│    User switches from MOH to MENR:                                  │
│      /moa/MOH/mana/assessments/                                    │
│         ↓ (Click org switcher)                                     │
│      /moa/MENR/mana/assessments/                                   │
│                                                                     │
│  Characteristics:                                                   │
│    ✓ Organization explicit in URL                                  │
│    ✓ Multi-org support                                             │
│    ✓ Organization-based routing                                    │
│    ✓ Bookmarkable per-org URLs                                     │
│                                                                     │
│  Backward Compatibility:                                            │
│    /communities/ → redirects to /moa/OOBC/communities/             │
│                   (or user's primary org)                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7. Data Isolation Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                   BMMS Multi-Tenant Data Isolation                  │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   PostgreSQL DB     │
                    │   (Single Database) │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
    │ Organization  │  │ Organization  │  │ Organization  │
    │   ID: 1       │  │   ID: 3       │  │   ID: 5       │
    │   Code: OOBC  │  │   Code: MOH   │  │   Code: MENR  │
    └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
            │                  │                  │
    ┌───────┴───────┐  ┌───────┴───────┐  ┌───────┴───────┐
    │               │  │               │  │               │
    ▼               ▼  ▼               ▼  ▼               ▼

OBCCommunity       Assessment      Partnership
org_id=1           org_id=3        org_id=5
- Comm A           - Assess X      - Partner A
- Comm B           - Assess Y      - Partner B
- Comm C

MunicipalityCoverage  OBCCommunity    Planning
org_id=1              org_id=3        org_id=5
- Muni X              - Comm D        - Plan X
- Muni Y              - Comm E

╔═══════════════════════════════════════════════════════════════════╗
║                      Data Access Rules                            ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  OOBC User (org_id=1):                                           ║
║    ✓ Can see: OOBC communities, OOBC municipal coverage         ║
║    ✗ Cannot see: MOH assessments, MENR partnerships             ║
║                                                                   ║
║  MOH User (org_id=3):                                            ║
║    ✓ Can see: MOH assessments, MOH communities                  ║
║    ✗ Cannot see: OOBC data, MENR data                           ║
║                                                                   ║
║  MENR User (org_id=5):                                           ║
║    ✓ Can see: MENR partnerships, MENR planning                  ║
║    ✗ Cannot see: OOBC data, MOH data                            ║
║                                                                   ║
║  OCM User (special):                                              ║
║    ✓ Can see: All organizations' data (read-only)               ║
║    ✓ Aggregated dashboards across all MOAs                       ║
║    ✗ Cannot edit: Any organization's data                        ║
║                                                                   ║
║  Superuser:                                                       ║
║    ✓ Can see: All data (Model.all_objects.all())                ║
║    ✓ Can edit: Any organization's data                           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

Query Examples:
───────────────

OOBC Context (org_id=1):
    OBCCommunity.objects.all()
    → SELECT * FROM communities_obc_community WHERE organization_id = 1
    → Returns: Comm A, Comm B, Comm C

MOH Context (org_id=3):
    Assessment.objects.all()
    → SELECT * FROM mana_assessment WHERE organization_id = 3
    → Returns: Assess X, Assess Y

OCM Context (read-only):
    OBCCommunity.all_objects.all()
    → SELECT * FROM communities_obc_community
    → Returns: All communities (OOBC, MOH, MENR)
```

---

## 8. Configuration Files

```
Project Root
├── .env.obcms                 ← OBCMS Mode Configuration
├── .env.bmms                  ← BMMS Mode Configuration
└── .env → .env.obcms          ← Symlink to active config

─────────────────────────────────────────────────────────────────

File: .env.obcms
════════════════════════════════════════════════════════════════

# OBCMS Mode - Single-tenant for OOBC only
BMMS_MODE=obcms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=False
ALLOW_ORGANIZATION_SWITCHING=False

DATABASE_URL=sqlite:///db.sqlite3
DEBUG=True
SECRET_KEY=dev-secret-key

─────────────────────────────────────────────────────────────────

File: .env.bmms
════════════════════════════════════════════════════════════════

# BMMS Mode - Multi-tenant for 44 MOAs
BMMS_MODE=bmms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=True
ALLOW_ORGANIZATION_SWITCHING=True

DATABASE_URL=postgresql://user:pass@localhost:5432/bmms
DEBUG=False
SECRET_KEY=prod-secret-key-generate-new

─────────────────────────────────────────────────────────────────

Mode Switching:
═══════════════

OBCMS → BMMS:
    1. cp .env.bmms .env
    2. sudo systemctl restart obcms
    3. Verify: python manage.py shell
       >>> from obc_management.settings.bmms_config import is_bmms_mode
       >>> is_bmms_mode()
       True

BMMS → OBCMS:
    1. cp .env.obcms .env
    2. sudo systemctl restart obcms
    3. Verify: python manage.py shell
       >>> from obc_management.settings.bmms_config import is_obcms_mode
       >>> is_obcms_mode()
       True
```

---

**End of Diagrams**

**Version:** 1.0
**Last Updated:** 2025-10-14
**For:** BMMS Embedded Architecture Implementation
