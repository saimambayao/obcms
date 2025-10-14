# BMMS Embedded Architecture - Implementation Summary

**Quick Reference Guide**

---

## Overview

This document provides a quick reference for implementing BMMS multi-tenant architecture embedded within OBCMS. For full details, see [BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md](./BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md).

---

## Core Concept

**Single Codebase, Dual Modes:**

```
OBCMS Mode (Default)          →    BMMS Mode (Configuration Change)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Single-tenant (OOBC only)   →    ✓ Multi-tenant (44 MOAs)
✓ No org prefix in URLs       →    ✓ Org prefix: /moa/<CODE>/
✓ Auto org injection          →    ✓ URL-based org selection
✓ No org switching            →    ✓ Org switching enabled
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRANSITION: Change .env only, NO code changes
```

---

## 🔴 CRITICAL: Pre-Implementation Audit Results

**Status:** REQUIRES PRE-IMPLEMENTATION RECONCILIATION
**Risk Level:** MODERATE-HIGH
**Action Required:** Complete Phase -1 BEFORE starting implementation

### Codebase Audit Summary

A comprehensive audit has revealed **6 critical findings** that impact implementation:

| # | Finding | Severity | Impact | Status |
|---|---------|----------|--------|--------|
| 1 | Middleware Conflict | 🔴 CRITICAL | Duplicate middleware will conflict | Must fix |
| 2 | Wrong Organization Import | 🔴 CRITICAL | Middleware imports from wrong module | Must fix |
| 3 | ENABLE_MULTI_TENANT Already True | 🟡 HIGH | Default behavior differs from plan | Must audit |
| 4 | BMMS_MODE Not Configured | 🟡 HIGH | Mode detection won't work | Must add |
| 5 | Models Not Converted | ✅ GOOD | Matches plan expectations | As expected |
| 6 | Infrastructure Exists | ✅ GOOD | Organizations app ready | Ready to use |

### ⚠️ DO NOT PROCEED UNTIL PHASE -1 IS COMPLETE

**Critical conflicts must be resolved BEFORE Phase 0 implementation.**

**See:** [RECONCILIATION_PLAN.md](./RECONCILIATION_PLAN.md) for complete details

### Phase -1: Mandatory Pre-Implementation Fixes

**Estimated Time:** 2 hours
**Must Complete Before:** Phase 0

#### Fix 1: Correct Organization Import (5 minutes) - 🔴 CRITICAL

```python
# src/common/middleware/organization_context.py line 44
# CURRENT (WRONG):
from coordination.models import Organization

# MUST CHANGE TO:
from organizations.models import Organization
```

**Why Critical:** Middleware will fail to import Organization model, breaking all requests

#### Fix 2: Add BMMS_MODE Configuration (15 minutes) - 🔴 CRITICAL

```bash
# Add to .env
BMMS_MODE=obcms
DEFAULT_ORGANIZATION_CODE=OOBC
```

**Create:** `src/obc_management/settings/bmms_config.py` with mode detection utilities

**Why Critical:** Without this, mode detection functions won't work, middleware won't know which mode to operate in

#### Fix 3: Audit ENABLE_MULTI_TENANT Behavior (30 minutes) - 🟡 HIGH

**Current State:**
```python
# base.py:638
'ENABLE_MULTI_TENANT': env.bool('ENABLE_MULTI_TENANT', default=True),  # Already True!
```

**Plan Expects:**
```python
'ENABLE_MULTI_TENANT': env.bool('ENABLE_MULTI_TENANT', default=(BMMS_MODE == BMMSMode.BMMS)),
```

**Action Required:**
- Test current behavior with ENABLE_MULTI_TENANT=True
- Document what's already using this flag
- Update default to be mode-dependent

**Why High Priority:** System may already be partially in BMMS mode, affecting query behavior

#### Fix 4: Resolve Middleware Strategy (1 hour) - 🔴 CRITICAL

**Issue:** Two middleware approaches will conflict:

**Existing (line 133 in base.py):**
```python
"common.middleware.organization_context.OrganizationContextMiddleware",
```

**Planned:**
```python
"organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware",
"organizations.middleware.OrganizationMiddleware",
```

**Decision Required:** Choose ONE approach:

- **Option A (RECOMMENDED):** Refactor existing middleware to be mode-aware
- **Option B:** Remove existing middleware and implement new stack

**See:** [RECONCILIATION_PLAN.md](./RECONCILIATION_PLAN.md) Section 4 for detailed comparison

**Why Critical:** Duplicate middleware will cause `request.organization` conflicts and data isolation failures

### Validation Checklist Before Phase 0

- [ ] All 4 fixes completed
- [ ] `python manage.py check` passes without errors
- [ ] Organization import path corrected
- [ ] BMMS_MODE configuration added to .env
- [ ] ENABLE_MULTI_TENANT behavior documented
- [ ] Middleware strategy selected and documented
- [ ] Existing tests still pass
- [ ] No middleware conflicts
- [ ] Mode detection works (`is_obcms_mode()` returns True)

### Implementation Readiness

**Current Status:** ⚠️ NOT READY - Phase -1 incomplete

**Once Phase -1 is complete:**
✅ Ready to proceed with Phase 0 (Pre-Implementation)
✅ Ready to proceed with Phase 1 (Configuration Infrastructure)

---

## What Already Exists ✅

**⚠️ Note:** Some existing infrastructure has conflicts that must be resolved in Phase -1

1. **Organizations App** (`src/organizations/`)
   - Organization and OrganizationMembership models
   - OrganizationScopedModel base class
   - OrganizationMiddleware for request context

2. **RBAC Settings** (`src/obc_management/settings/base.py`)
   - `ENABLE_MULTI_TENANT` flag
   - `ALLOW_ORGANIZATION_SWITCHING` flag
   - OCM configuration

3. **Thread-Local Context**
   - `get_current_organization()`
   - `set_current_organization()`
   - `clear_current_organization()`

---

## What Needs Implementation ❌

### 1. New Files to Create

```
src/
├── obc_management/settings/
│   └── bmms_config.py                     # NEW: Mode configuration utilities
├── organizations/
│   ├── utils/__init__.py                   # NEW: Org utility functions
│   ├── middleware/
│   │   └── obcms_middleware.py            # NEW: OBCMS auto-injection
│   ├── models/
│   │   └── mixins.py                      # NEW: Model mixins
│   └── management/commands/
│       ├── ensure_default_organization.py  # NEW: Setup command
│       └── populate_organization_field.py  # NEW: Migration command
├── common/
│   ├── decorators/
│   │   └── organization.py                # NEW: View decorators
│   ├── mixins/
│   │   └── organization.py                # NEW: CBV mixins
│   └── permissions/
│       └── organization.py                # NEW: DRF permissions
└── tests/
    └── conftest.py                        # NEW: Test fixtures
```

### 2. Existing Files to Modify

```
src/
├── obc_management/settings/base.py        # Add BMMS_MODE, update middleware
├── organizations/middleware.py             # Skip in OBCMS mode
├── organizations/models/organization.py    # Add get_default_organization()
├── communities/models.py                   # Inherit OrganizationScopedModel
├── mana/models.py                          # Inherit OrganizationScopedModel
├── coordination/models.py                  # Inherit OrganizationScopedModel
└── [all other app models]                  # Inherit OrganizationScopedModel
```

### 3. Migrations Required

**For each app (communities, mana, coordination, policies, etc.):**

```
Step 1: Add nullable organization field
   → python manage.py makemigrations app_name
   → python manage.py migrate app_name

Step 2: Populate organization field
   → python manage.py populate_organization_field --app app_name

Step 3: Make organization field required
   → python manage.py makemigrations app_name
   → python manage.py migrate app_name
```

---

## Configuration Changes

### OBCMS Mode (.env.obcms)

```bash
BMMS_MODE=obcms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=False
ALLOW_ORGANIZATION_SWITCHING=False
```

### BMMS Mode (.env.bmms)

```bash
BMMS_MODE=bmms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=True
ALLOW_ORGANIZATION_SWITCHING=True
```

### Mode Switching

```bash
# Copy appropriate config
cp .env.bmms .env

# Restart application
sudo systemctl restart obcms

# Verify mode
python manage.py shell
>>> from obc_management.settings.bmms_config import is_bmms_mode
>>> is_bmms_mode()
True
```

---

## Model Migration Pattern

### Before (Current State)

```python
# communities/models.py
class OBCCommunity(models.Model):
    name = models.CharField(max_length=255)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE)
    # NO organization field
```

### After (BMMS-Ready)

```python
# communities/models.py
from organizations.models import OrganizationScopedModel

class OBCCommunity(OrganizationScopedModel):  # Changed base class
    name = models.CharField(max_length=255)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE)
    # organization field inherited automatically
    # objects = OrganizationScopedManager() (auto-filtered)
    # all_objects = models.Manager() (unfiltered)
```

**Result:**
- Queries automatically filtered by organization
- `OBCCommunity.objects.all()` returns only current org's communities
- `OBCCommunity.all_objects.all()` returns all communities (admin/OCM use)

---

## View Conversion Pattern

### Before (Current State)

```python
@login_required
def community_list(request):
    communities = OBCCommunity.objects.all()  # Shows ALL
    return render(request, 'list.html', {'communities': communities})
```

### After (BMMS-Ready)

```python
from common.decorators.organization import require_organization

@login_required
@require_organization  # NEW: Validates org context
def community_list(request):
    # OBCMS mode: Auto-filtered to OOBC communities
    # BMMS mode: Auto-filtered to request.organization communities
    communities = OBCCommunity.objects.all()  # Auto-filtered by manager

    return render(request, 'list.html', {
        'communities': communities,
        'organization': request.organization,  # Available in template
    })
```

**Key Changes:**
1. Add `@require_organization` decorator
2. No queryset changes needed (auto-filtered)
3. Organization available via `request.organization`

---

## URL Pattern Changes

### Before (OBCMS Only)

```python
# urls.py
urlpatterns = [
    path('communities/', include('communities.urls')),
    path('mana/', include('mana.urls')),
]

# Access: /communities/
```

### After (Dual-Mode Support)

```python
# urls.py
from obc_management.settings.bmms_config import is_bmms_mode

obcms_patterns = [
    path('communities/', include('communities.urls')),
    path('mana/', include('mana.urls')),
]

bmms_patterns = [
    path('moa/<str:org_code>/', include([
        path('communities/', include('communities.urls')),
        path('mana/', include('mana.urls')),
    ])),
]

urlpatterns = [path('admin/', admin.site.urls)]

if is_bmms_mode():
    urlpatterns += bmms_patterns
    urlpatterns += obcms_patterns  # Backward compatibility
else:
    urlpatterns += obcms_patterns

# OBCMS mode: /communities/ works
# BMMS mode: /moa/OOBC/communities/ AND /communities/ work
```

---

## Implementation Sequence (High-Level)

```
Phase 0: Pre-Implementation
   ✓ Create feature branch
   ✓ Backup database
   ✓ Verify current state

Phase 1: Configuration Infrastructure (CRITICAL)
   → Create bmms_config.py
   → Update settings/base.py
   → Create .env.obcms and .env.bmms

Phase 2: Organization Utilities (HIGH)
   → Create organizations/utils/__init__.py
   → Enhance Organization model
   → Create management commands

Phase 3: Middleware Enhancement (CRITICAL)
   → Create OBCMSOrganizationMiddleware
   → Update OrganizationMiddleware
   → Update MIDDLEWARE setting

Phase 4: View Decorators (HIGH)
   → Create @require_organization decorator
   → Create OrganizationRequiredMixin
   → Create OrganizationAccessPermission

Phase 5: Model Migration - Communities (CRITICAL)
   → Update models to inherit OrganizationScopedModel
   → Run 3-step migration (nullable → populate → required)
   → Verify all records have organization

Phase 6: Model Migration - MANA (HIGH)
   → Same process as Phase 5

Phase 7: Model Migration - Remaining Apps (MEDIUM)
   → Migrate Coordination, Policies, etc.

Phase 8: View Layer Updates (HIGH)
   → Add decorators to all views
   → Update templates to use organization context

Phase 9: URL Routing Enhancement (MEDIUM)
   → Add dual-mode URL patterns

Phase 10: Testing Infrastructure (HIGH)
   → Create dual-mode test fixtures
   → Write organization-scoping tests
   → Verify all tests pass in both modes

Phase 11: Documentation (MEDIUM)
   → Create migration guides
   → Update development docs

Phase 12: Final Validation (CRITICAL)
   → Run validation checklist
   → Performance testing
   → Merge to main
```

---

## Quick Start Commands

### Setup Default Organization

```bash
cd src/
python manage.py ensure_default_organization
```

### Populate Organization Field (After Step 1 Migration)

```bash
# Dry run first
python manage.py populate_organization_field --dry-run

# Populate all apps
python manage.py populate_organization_field

# Populate specific app
python manage.py populate_organization_field --app communities

# Populate specific model
python manage.py populate_organization_field --app communities --model OBCCommunity
```

### Verify Organization Field

```bash
python manage.py shell

>>> from communities.models import OBCCommunity
>>> from organizations.models import Organization

# Check for null organizations
>>> OBCCommunity.all_objects.filter(organization__isnull=True).count()
0  # Should be 0 after Step 2

# Verify default organization
>>> org = Organization.objects.get(code='OOBC')
>>> OBCCommunity.objects.filter(organization=org).count()
# Should match total count
```

### Test Mode Configuration

```bash
# Test OBCMS mode
python manage.py shell
>>> from obc_management.settings.bmms_config import *
>>> is_obcms_mode()
True
>>> multi_tenant_enabled()
False

# Test BMMS mode (change .env first)
>>> is_bmms_mode()
True
>>> multi_tenant_enabled()
True
```

### Run Tests in Both Modes

```bash
# OBCMS mode
BMMS_MODE=obcms pytest

# BMMS mode
BMMS_MODE=bmms pytest

# Specific test file
pytest src/communities/tests/test_organization_scoping.py

# With coverage
pytest --cov=src --cov-report=html
```

---

## Critical Success Factors

1. **NO Code Changes for Mode Switching**
   - Only `.env` configuration changes
   - Application restart required
   - No migrations needed to switch modes

2. **Zero Data Loss**
   - Three-step migration ensures integrity
   - Backup database before each phase
   - Verify record counts at each step

3. **Backward Compatibility**
   - OBCMS URLs continue to work
   - Existing views function without modification
   - Templates access organization via context

4. **Security Maintained**
   - Organization-level data isolation enforced
   - Users cannot access other orgs' data
   - OCM has read-only aggregation access

5. **Performance Acceptable**
   - Organization filter adds minimal overhead (<5%)
   - Queries remain optimized
   - No N+1 query problems introduced

---

## Validation Checklist (Quick)

Before deployment:

- [ ] Default OOBC organization exists
- [ ] All models have organization field
- [ ] All records have organization assigned
- [ ] No orphaned records (organization=NULL)
- [ ] Auto-filtering works (Model.objects.all())
- [ ] Views have organization context (request.organization)
- [ ] Tests pass in OBCMS mode
- [ ] Tests pass in BMMS mode
- [ ] URLs work in both modes
- [ ] No performance degradation

---

## Troubleshooting

### Issue: "Organization context required but not found"

**Cause:** Middleware not running or incorrectly ordered

**Fix:**
```python
# settings/base.py - Check middleware order
MIDDLEWARE = [
    # ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware",  # BEFORE
    "organizations.middleware.OrganizationMiddleware",  # AFTER
    # ...
]
```

### Issue: "Organization field cannot be null"

**Cause:** Step 3 migration run before Step 2 population

**Fix:**
```bash
# Rollback Step 3 migration
python manage.py migrate app_name 000X  # Previous migration number

# Run Step 2 population
python manage.py populate_organization_field --app app_name

# Re-run Step 3 migration
python manage.py migrate app_name
```

### Issue: Queries show no results

**Cause:** Organization context not set or wrong org selected

**Fix:**
```python
# Check current organization
from organizations.models.scoped import get_current_organization
current_org = get_current_organization()
print(current_org.code if current_org else "No org set")

# Use all_objects to bypass filter
Model.all_objects.all()  # Shows all records regardless of org
```

---

## Next Steps

1. **Read Full Implementation Plan:**
   - See [BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md](./BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md)

2. **Start Implementation:**
   - Create feature branch: `feature/bmms-embedded-architecture`
   - Begin with Phase 1: Configuration Infrastructure

3. **Follow Phase Sequence:**
   - Complete each phase before moving to next
   - Validate after each phase
   - Commit frequently

4. **Test Continuously:**
   - Run tests after each phase
   - Verify in both OBCMS and BMMS modes
   - Check validation checklist

5. **Document Progress:**
   - Update implementation status
   - Note any issues encountered
   - Document solutions

---

## Support Resources

- **Full Documentation:** [BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md](./BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md)
- **BMMS Transition Plan:** [../TRANSITION_PLAN.md](../TRANSITION_PLAN.md)
- **CLAUDE.md Guidelines:** [../../../CLAUDE.md](../../../CLAUDE.md)
- **Development Setup:** [../../development/README.md](../../development/README.md)

---

**Version:** 1.0
**Last Updated:** 2025-10-14
**Implementation Status:** READY FOR EXECUTION
