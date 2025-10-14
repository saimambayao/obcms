# BMMS Implementation Reconciliation Plan

**Status:** CRITICAL - MUST COMPLETE BEFORE IMPLEMENTATION
**Priority:** MANDATORY PRE-REQUISITE
**Risk Level:** HIGH
**Created:** 2025-10-14

---

## Executive Summary

This document provides critical reconciliation steps to resolve conflicts between the existing OBCMS codebase and the planned BMMS implementation. A comprehensive codebase audit has revealed **6 critical conflicts** that must be resolved before proceeding with the implementation plan.

**DO NOT PROCEED WITH IMPLEMENTATION UNTIL ALL RECONCILIATION TASKS ARE COMPLETE.**

---

## Table of Contents

1. [Critical Findings Overview](#critical-findings-overview)
2. [Pre-Implementation Audit Results](#pre-implementation-audit-results)
3. [Risk Assessment](#risk-assessment)
4. [Phase -1: Mandatory Pre-Implementation Fixes](#phase--1-mandatory-pre-implementation-fixes)
5. [Middleware Reconciliation Strategy](#middleware-reconciliation-strategy)
6. [Configuration Reconciliation](#configuration-reconciliation)
7. [Implementation Sequence After Reconciliation](#implementation-sequence-after-reconciliation)
8. [Validation Checklist](#validation-checklist)

---

## Critical Findings Overview

### 🔴 CRITICAL CONFLICTS DETECTED

Six critical conflicts have been identified between the existing codebase and the planned BMMS implementation:

| Finding # | Category | Severity | Impact |
|-----------|----------|----------|--------|
| 1 | Middleware Conflict | CRITICAL | Two middleware classes will conflict |
| 2 | Wrong Import Path | CRITICAL | Middleware uses wrong Organization model |
| 3 | Config Already Set | HIGH | ENABLE_MULTI_TENANT already True |
| 4 | Missing Config | HIGH | BMMS_MODE not configured |
| 5 | Models Not Converted | GOOD | Matches plan expectations |
| 6 | Infrastructure Exists | GOOD | Base models ready |

---

## Pre-Implementation Audit Results

### Finding 1: MIDDLEWARE CONFLICT (CRITICAL)

**Issue:** Duplicate middleware classes attempting to set `request.organization`

**Current State:**
```python
# src/obc_management/settings/base.py (line 133)
MIDDLEWARE = [
    # ...
    "common.middleware.organization_context.OrganizationContextMiddleware",  # ← EXISTING
    # ...
]
```

**Planned Addition:**
```python
# Implementation plan wants to add:
"organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware"  # ← NEW
"organizations.middleware.OrganizationMiddleware"  # ← NEW
```

**Conflict:**
- Both `OrganizationContextMiddleware` and `OBCMSOrganizationMiddleware` will try to set `request.organization`
- This will cause race conditions and unpredictable behavior
- Only ONE organization middleware should exist

**Impact:** Application will crash or produce incorrect organization context

---

### Finding 2: WRONG ORGANIZATION IMPORT (CRITICAL)

**Issue:** Existing middleware imports Organization from wrong location

**File:** `src/common/middleware/organization_context.py` (line 44)

**Current Code:**
```python
from coordination.models import Organization  # ❌ WRONG LOCATION
```

**Should Be:**
```python
from organizations.models import Organization  # ✅ CORRECT LOCATION
```

**Why This Is Critical:**
- The `organizations` app is the correct location for Organization model (Phase 1 foundation)
- `coordination.models.Organization` may not exist or may be outdated
- This will cause `ImportError` or incorrect model usage
- All organization lookups will fail

**Impact:** Middleware will fail to load Organization, breaking all requests

---

### Finding 3: ENABLE_MULTI_TENANT ALREADY TRUE (HIGH)

**Issue:** Multi-tenant flag already enabled in base settings

**File:** `src/obc_management/settings/base.py` (line 638)

**Current Code:**
```python
RBAC_SETTINGS = {
    'ENABLE_MULTI_TENANT': env.bool('ENABLE_MULTI_TENANT', default=True),  # ← Already True!
    # ...
}
```

**Plan Assumption:**
```python
# Plan assumes this should be:
'ENABLE_MULTI_TENANT': env.bool('ENABLE_MULTI_TENANT', default=(BMMS_MODE == BMMSMode.BMMS))
```

**Conflict:**
- System may already be operating in partial BMMS mode
- Need to verify impact on existing functionality
- Must decide: Keep True or make mode-dependent

**Impact:** OBCMS may already have multi-tenant behavior enabled

---

### Finding 4: BMMS_MODE NOT CONFIGURED (HIGH)

**Issue:** No BMMS_MODE setting exists in configuration

**Current State:**
- No `BMMS_MODE` setting in `base.py`
- No `.env.obcms` or `.env.bmms` files exist
- Mode detection functions won't work

**Required:**
```python
# settings/base.py
BMMS_MODE = env.str('BMMS_MODE', default='obcms')
```

```bash
# .env file
BMMS_MODE=obcms
```

**Impact:** Cannot determine operational mode; all mode-based logic will fail

---

### Finding 5: MODELS NOT YET CONVERTED (GOOD)

**Issue:** None - this matches plan expectations

**Current State:**
- Communities models (`OBCCommunity`, etc.) do NOT inherit from `OrganizationScopedModel`
- No `organization` field on existing models
- Models are in expected state for migration

**Status:** ✅ CORRECT - Ready for planned migration in Phases 5-7

---

### Finding 6: INFRASTRUCTURE ALREADY EXISTS (GOOD)

**Issue:** None - foundation is ready

**Current State:**
```
src/organizations/
├── models/
│   ├── organization.py         ✅ Organization, OrganizationMembership
│   └── scoped.py               ✅ OrganizationScopedModel
├── middleware.py               ✅ Middleware infrastructure
└── [thread-local functions]    ✅ get/set/clear_current_organization()
```

**Status:** ✅ CORRECT - Phase 1 foundation complete

---

## Risk Assessment

### CRITICAL RISKS (Must Fix Before Implementation)

#### Risk 1: Middleware Collision
- **Severity:** CRITICAL
- **Probability:** 100% (certain conflict)
- **Impact:** Application failure, incorrect organization context
- **Mitigation:** Choose one middleware strategy (see Reconciliation Strategy)

#### Risk 2: Import Path Error
- **Severity:** CRITICAL
- **Probability:** 100% (import will fail)
- **Impact:** Middleware crashes, all requests fail
- **Mitigation:** Fix import path immediately

### HIGH RISKS (Must Address Before Implementation)

#### Risk 3: Unintended Multi-Tenant Behavior
- **Severity:** HIGH
- **Probability:** 80% (already enabled)
- **Impact:** OBCMS operating in unintended mode
- **Mitigation:** Audit current behavior, adjust settings

#### Risk 4: Mode Detection Failure
- **Severity:** HIGH
- **Probability:** 100% (missing config)
- **Impact:** All mode-based logic fails
- **Mitigation:** Add BMMS_MODE configuration

---

## Phase -1: Mandatory Pre-Implementation Fixes

**THESE FIXES MUST BE COMPLETED BEFORE PHASE 0 OF IMPLEMENTATION PLAN**

### Fix 1: Correct Organization Import Path ⚠️ IMMEDIATE

**Priority:** CRITICAL - FIX FIRST
**Estimated Effort:** 5 minutes
**Risk:** Application breaks without this fix

**Steps:**

1. **Open file:** `src/common/middleware/organization_context.py`

2. **Change line 44:**
   ```python
   # FROM:
   from coordination.models import Organization

   # TO:
   from organizations.models import Organization
   ```

3. **Verify import works:**
   ```bash
   python manage.py shell
   >>> from organizations.models import Organization
   >>> Organization.objects.count()
   # Should return a number without error
   ```

4. **Test middleware loads:**
   ```bash
   python manage.py check
   # Should pass without import errors
   ```

**Success Criteria:**
- ✅ Import error resolved
- ✅ Middleware loads successfully
- ✅ No import warnings in console

---

### Fix 2: Add BMMS_MODE Configuration

**Priority:** CRITICAL
**Estimated Effort:** 15 minutes
**Dependencies:** None

**Steps:**

1. **Create `bmms_config.py`:**

   File: `src/obc_management/settings/bmms_config.py`
   ```python
   """
   BMMS Configuration Module

   Provides configuration constants and utilities for BMMS multi-tenant mode.
   """
   from django.conf import settings


   class BMMSMode:
       """BMMS operational modes."""
       OBCMS = 'obcms'  # Single-tenant mode (OOBC only)
       BMMS = 'bmms'    # Multi-tenant mode (44 MOAs)


   def is_bmms_mode():
       """Check if system is running in BMMS mode."""
       return getattr(settings, 'BMMS_MODE', BMMSMode.OBCMS) == BMMSMode.BMMS


   def is_obcms_mode():
       """Check if system is running in OBCMS mode."""
       return not is_bmms_mode()


   def get_default_organization_code():
       """Get the default organization code for OBCMS mode."""
       return getattr(settings, 'DEFAULT_ORGANIZATION_CODE', 'OOBC')


   def multi_tenant_enabled():
       """Check if multi-tenant features are enabled."""
       if is_obcms_mode():
           return False  # OBCMS always single-tenant
       return getattr(settings, 'ENABLE_MULTI_TENANT', True)


   def organization_switching_enabled():
       """Check if organization switching is allowed."""
       if is_obcms_mode():
           return False  # No switching in OBCMS mode
       return getattr(settings, 'ALLOW_ORGANIZATION_SWITCHING', True)
   ```

2. **Update `settings/base.py`:**

   Add after line 631 (after imports):
   ```python
   from obc_management.settings.bmms_config import BMMSMode

   # ========== BMMS MODE CONFIGURATION ==========
   # Operational mode: 'obcms' (single-tenant) or 'bmms' (multi-tenant)
   BMMS_MODE = env.str('BMMS_MODE', default=BMMSMode.OBCMS)

   # Default organization code for OBCMS mode
   DEFAULT_ORGANIZATION_CODE = env.str('DEFAULT_ORGANIZATION_CODE', default='OOBC')
   ```

3. **Update RBAC_SETTINGS (line 636-652):**
   ```python
   RBAC_SETTINGS = {
       # Enable multi-tenant organization context
       # In OBCMS mode, this is automatically set to False
       'ENABLE_MULTI_TENANT': env.bool(
           'ENABLE_MULTI_TENANT',
           default=(BMMS_MODE == BMMSMode.BMMS)  # ← Changed from default=True
       ),

       # Office of Chief Minister (OCM) organization code
       'OCM_ORGANIZATION_CODE': 'OCM',  # ← Changed from 'ocm' to 'OCM'

       # Permission cache timeout (seconds)
       'CACHE_TIMEOUT': 300,

       # Organization switching
       # In OBCMS mode, this is automatically set to False
       'ALLOW_ORGANIZATION_SWITCHING': env.bool(
           'ALLOW_ORGANIZATION_SWITCHING',
           default=(BMMS_MODE == BMMSMode.BMMS)  # ← Changed from default=True
       ),

       # Session key for current organization
       'SESSION_ORG_KEY': 'current_organization',
   }
   ```

4. **Create `.env.obcms` file:**

   File: `.env.obcms` (in project root)
   ```bash
   # OBCMS Mode - Single-tenant for OOBC only

   # Core Configuration
   BMMS_MODE=obcms
   DEFAULT_ORGANIZATION_CODE=OOBC

   # Multi-tenant Settings (automatically disabled in OBCMS mode)
   ENABLE_MULTI_TENANT=False
   ALLOW_ORGANIZATION_SWITCHING=False

   # Database
   DATABASE_URL=sqlite:///db.sqlite3

   # Debug
   DEBUG=True

   # Security
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Test configuration:**
   ```bash
   python manage.py shell
   >>> from obc_management.settings.bmms_config import *
   >>> is_obcms_mode()
   True
   >>> multi_tenant_enabled()
   False
   >>> organization_switching_enabled()
   False
   ```

**Success Criteria:**
- ✅ `bmms_config.py` created
- ✅ BMMS_MODE setting added
- ✅ Mode detection functions work
- ✅ Settings adjust based on mode

---

### Fix 3: Audit ENABLE_MULTI_TENANT Current Usage

**Priority:** HIGH
**Estimated Effort:** 30 minutes
**Dependencies:** Fix 2 complete

**Steps:**

1. **Check current multi-tenant behavior:**
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> settings.RBAC_SETTINGS['ENABLE_MULTI_TENANT']
   True  # ← Currently enabled
   ```

2. **Search for code that uses this flag:**
   ```bash
   cd src/
   grep -r "ENABLE_MULTI_TENANT" --include="*.py"
   ```

3. **Document findings:**
   - List all files using this flag
   - Identify current behavior
   - Note any breaking changes if set to False

4. **Test OBCMS mode:**
   ```bash
   # Set BMMS_MODE=obcms in .env
   export BMMS_MODE=obcms
   python manage.py runserver
   # Navigate to application, verify functionality
   ```

5. **Verify no regressions:**
   - Dashboard loads
   - Community list works
   - MANA assessments accessible
   - No organization-related errors

**Success Criteria:**
- ✅ Current behavior documented
- ✅ Code dependencies identified
- ✅ OBCMS mode tested
- ✅ No functionality broken

---

### Fix 4: Decide Middleware Strategy

**Priority:** CRITICAL
**Estimated Effort:** 1 hour (decision + implementation)
**Dependencies:** Fix 1, Fix 2 complete

See [Middleware Reconciliation Strategy](#middleware-reconciliation-strategy) section below for detailed options.

**Decision Required:**
- **Option A:** Refactor existing `OrganizationContextMiddleware` ✅ RECOMMENDED
- **Option B:** Remove existing, create new middleware stack

**Success Criteria:**
- ✅ Single middleware handles organization context
- ✅ No conflicts between middleware classes
- ✅ Mode-aware behavior works correctly

---

## Middleware Reconciliation Strategy

### Current State Analysis

**Existing Middleware:**
```python
# Location: src/common/middleware/organization_context.py
# Name: OrganizationContextMiddleware
# Registered: settings/base.py line 133

class OrganizationContextMiddleware:
    """Extracts organization from URL/session/user"""

    def __call__(self, request):
        request.organization = SimpleLazyObject(
            lambda: get_organization_from_request(request)
        )
        response = self.get_response(request)
        return response
```

**Planned Middleware:**
```python
# Location: organizations/middleware/obcms_middleware.py (NEW)
# Name: OBCMSOrganizationMiddleware

class OBCMSOrganizationMiddleware:
    """Auto-inject OOBC in OBCMS mode"""

    def __call__(self, request):
        if is_obcms_mode():
            request.organization = get_default_organization()
        response = self.get_response(request)
        return response
```

### Conflict Analysis

**Problem:** Both middleware classes set `request.organization`:
1. `OBCMSOrganizationMiddleware` runs first (OBCMS auto-inject)
2. `OrganizationContextMiddleware` runs second (URL extraction)
3. Second middleware OVERWRITES first middleware's value
4. Behavior unpredictable

---

### Option A: Refactor Existing Middleware (RECOMMENDED)

**Strategy:** Enhance existing `OrganizationContextMiddleware` to be mode-aware

**Advantages:**
- ✅ Single source of truth
- ✅ No duplicate logic
- ✅ Maintains existing functionality
- ✅ Minimal code changes

**Implementation Steps:**

1. **Update `organization_context.py` imports:**
   ```python
   # Add at top of file (after existing imports)
   from obc_management.settings.bmms_config import is_obcms_mode, is_bmms_mode
   from organizations.utils import get_or_create_default_organization
   ```

2. **Modify `get_organization_from_request()` function:**
   ```python
   def get_organization_from_request(request: HttpRequest):
       """
       Extract organization context from request.

       Mode-aware behavior:
       - OBCMS mode: Always return default OOBC organization
       - BMMS mode: Extract from URL/session/user
       """
       from organizations.models import Organization  # ← Fixed import

       # OBCMS mode: Auto-inject default organization
       if is_obcms_mode():
           # Cache default org to avoid repeated database hits
           if not hasattr(request, '_cached_default_org'):
               request._cached_default_org, _ = get_or_create_default_organization()
           return request._cached_default_org

       # BMMS mode: Extract from request (existing logic)
       if not request.user.is_authenticated:
           return None

       organization = None
       org_id = None

       # [Rest of existing code unchanged]
       # ...
   ```

3. **Add middleware comment:**
   ```python
   class OrganizationContextMiddleware:
       """
       Middleware to set organization context on request object.

       Mode-aware behavior:
       - OBCMS mode: Auto-injects default OOBC organization
       - BMMS mode: Extracts organization from URL/session/user

       This is the ONLY middleware that sets request.organization.
       Do NOT create additional organization middleware classes.
       """
   ```

4. **Test both modes:**
   ```bash
   # OBCMS mode
   export BMMS_MODE=obcms
   python manage.py runserver
   # Access /dashboard/ → should have request.organization = OOBC

   # BMMS mode
   export BMMS_MODE=bmms
   python manage.py runserver
   # Access /moa/MOH/dashboard/ → should have request.organization = MOH
   ```

**Estimated Effort:** 30 minutes

---

### Option B: Remove Existing, Create New Stack (NOT RECOMMENDED)

**Strategy:** Delete existing middleware, implement plan's two-middleware approach

**Disadvantages:**
- ❌ More complex (two middleware classes)
- ❌ Risk of breaking existing functionality
- ❌ Duplicate logic between middleware
- ❌ Higher maintenance burden

**Only Use If:** Existing middleware is fundamentally incompatible

**Implementation Steps:**

1. **Remove from middleware stack:**
   ```python
   # In settings/base.py, REMOVE this line:
   "common.middleware.organization_context.OrganizationContextMiddleware",
   ```

2. **Create new middleware files:**
   - `organizations/middleware/__init__.py`
   - `organizations/middleware/obcms_middleware.py` (OBCMS auto-inject)
   - `organizations/middleware.py` (BMMS URL extraction)

3. **Add to middleware stack:**
   ```python
   MIDDLEWARE = [
       # ...
       "organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware",  # FIRST
       "organizations.middleware.OrganizationMiddleware",  # SECOND
       # ...
   ]
   ```

4. **Comprehensive testing required:**
   - All views
   - All URL patterns
   - Both modes

**Estimated Effort:** 2-3 hours

---

### DECISION: Use Option A

**Rationale:**
- Existing middleware already works
- Single middleware = simpler architecture
- Less risk of breaking existing functionality
- Faster implementation

**Action Items:**
1. ✅ Fix import path (Fix 1)
2. ✅ Add mode detection (Fix 2)
3. ✅ Refactor `get_organization_from_request()` to be mode-aware
4. ✅ Test in both modes
5. ✅ Document middleware behavior

---

## Configuration Reconciliation

### Current vs. Planned Configuration

| Setting | Current | Planned | Resolution |
|---------|---------|---------|------------|
| BMMS_MODE | ❌ Missing | ✅ Required | **ADD** in Fix 2 |
| DEFAULT_ORGANIZATION_CODE | ❌ Missing | ✅ Required | **ADD** in Fix 2 |
| ENABLE_MULTI_TENANT | `default=True` | `default=(mode=='bmms')` | **CHANGE** in Fix 2 |
| ALLOW_ORGANIZATION_SWITCHING | `True` | `(mode=='bmms')` | **CHANGE** in Fix 2 |
| OCM_ORGANIZATION_CODE | `'ocm'` | `'OCM'` | **CHANGE** to uppercase |

### Configuration File Changes

**File: `settings/base.py`**

**Add after line 631:**
```python
from obc_management.settings.bmms_config import BMMSMode

# ========== BMMS MODE CONFIGURATION ==========
BMMS_MODE = env.str('BMMS_MODE', default=BMMSMode.OBCMS)
DEFAULT_ORGANIZATION_CODE = env.str('DEFAULT_ORGANIZATION_CODE', default='OOBC')
```

**Modify RBAC_SETTINGS (lines 636-652):**
```python
RBAC_SETTINGS = {
    'ENABLE_MULTI_TENANT': env.bool(
        'ENABLE_MULTI_TENANT',
        default=(BMMS_MODE == BMMSMode.BMMS)  # ← Changed
    ),
    'OCM_ORGANIZATION_CODE': 'OCM',  # ← Changed to uppercase
    'CACHE_TIMEOUT': 300,
    'ALLOW_ORGANIZATION_SWITCHING': env.bool(
        'ALLOW_ORGANIZATION_SWITCHING',
        default=(BMMS_MODE == BMMSMode.BMMS)  # ← Changed
    ),
    'SESSION_ORG_KEY': 'current_organization',
}
```

---

## Implementation Sequence After Reconciliation

### Phase -1 Complete Checklist

Before proceeding to Phase 0 of main implementation plan:

- [ ] **Fix 1 Complete:** Organization import path corrected
  - [ ] Import changed from `coordination.models` to `organizations.models`
  - [ ] Middleware loads without import errors
  - [ ] `python manage.py check` passes

- [ ] **Fix 2 Complete:** BMMS_MODE configuration added
  - [ ] `bmms_config.py` created
  - [ ] BMMS_MODE setting added to base.py
  - [ ] DEFAULT_ORGANIZATION_CODE setting added
  - [ ] RBAC_SETTINGS updated with mode-based defaults
  - [ ] `.env.obcms` file created
  - [ ] Mode detection functions work

- [ ] **Fix 3 Complete:** ENABLE_MULTI_TENANT audit done
  - [ ] Current behavior documented
  - [ ] Code dependencies identified
  - [ ] OBCMS mode tested
  - [ ] No functionality broken

- [ ] **Fix 4 Complete:** Middleware strategy implemented
  - [ ] Option A (refactor) or Option B (replace) chosen
  - [ ] Middleware updated with mode-aware behavior
  - [ ] Thread-local functions work correctly
  - [ ] Tests pass in both modes

- [ ] **Validation:** All pre-implementation checks pass
  - [ ] No middleware conflicts
  - [ ] Organization context works in OBCMS mode
  - [ ] Mode switching works (change .env, restart)
  - [ ] Existing tests still pass

### Modified Phase 0: Pre-Implementation Setup

**After Phase -1 completion, proceed with:**

1. **Create feature branch** (as planned)
   ```bash
   git checkout -b feature/bmms-embedded-architecture
   ```

2. **Backup database** (as planned)
   ```bash
   cp src/db.sqlite3 src/db.sqlite3.backup
   ```

3. **Verify Phase -1 fixes** (NEW)
   ```bash
   cd src/
   python manage.py check
   python manage.py test --keepdb
   # All should pass
   ```

4. **Proceed to Phase 1** (as planned in main implementation doc)

---

## Validation Checklist

### Pre-Implementation Validation (After Phase -1)

#### Organization Import
- [ ] Import path corrected to `organizations.models.Organization`
- [ ] No ImportError when loading middleware
- [ ] Organization model accessible in shell

#### BMMS Mode Configuration
- [ ] `bmms_config.py` file exists
- [ ] `BMMSMode` class defined
- [ ] Mode detection functions work:
  - [ ] `is_obcms_mode()` returns True when `BMMS_MODE=obcms`
  - [ ] `is_bmms_mode()` returns True when `BMMS_MODE=bmms`
- [ ] Settings adjust based on mode:
  - [ ] `ENABLE_MULTI_TENANT` = False in OBCMS mode
  - [ ] `ALLOW_ORGANIZATION_SWITCHING` = False in OBCMS mode

#### Middleware Configuration
- [ ] Only ONE middleware sets `request.organization`
- [ ] Middleware is mode-aware
- [ ] OBCMS mode: Auto-injects OOBC organization
- [ ] BMMS mode: Extracts from URL/session
- [ ] Thread-local functions work correctly

#### Environment Files
- [ ] `.env.obcms` file exists with correct settings
- [ ] BMMS_MODE variable present
- [ ] DEFAULT_ORGANIZATION_CODE variable present

#### Backward Compatibility
- [ ] Existing views still work
- [ ] Dashboard loads without errors
- [ ] Community list displays correctly
- [ ] MANA assessments accessible
- [ ] No organization-related errors in console

#### Test Suite
- [ ] All existing tests pass
- [ ] No new test failures introduced
- [ ] `python manage.py check` passes
- [ ] No middleware warnings

---

## Troubleshooting

### Issue: "Cannot import name 'Organization'"

**Symptom:** `ImportError: cannot import name 'Organization' from 'coordination.models'`

**Cause:** Wrong import path (Finding #2)

**Solution:**
```bash
# Fix import in organization_context.py line 44
# FROM: from coordination.models import Organization
# TO: from organizations.models import Organization
```

---

### Issue: "BMMS_MODE not defined"

**Symptom:** `AttributeError: 'Settings' object has no attribute 'BMMS_MODE'`

**Cause:** Missing configuration (Finding #4)

**Solution:**
1. Create `bmms_config.py`
2. Add BMMS_MODE to settings/base.py
3. Add BMMS_MODE to .env file

---

### Issue: Middleware conflict errors

**Symptom:** Multiple middleware setting `request.organization`

**Cause:** Both existing and new middleware active (Finding #1)

**Solution:**
- Implement Option A (refactor existing middleware)
- Remove duplicate middleware from MIDDLEWARE list

---

### Issue: Multi-tenant enabled in OBCMS mode

**Symptom:** Organization switching available when it shouldn't be

**Cause:** ENABLE_MULTI_TENANT=True hardcoded (Finding #3)

**Solution:**
- Update RBAC_SETTINGS to use mode-based default
- Set BMMS_MODE=obcms in .env
- Restart application

---

## Success Metrics

### Phase -1 Completion Criteria

✅ **All 4 critical fixes complete:**
1. Organization import path corrected
2. BMMS_MODE configuration added
3. ENABLE_MULTI_TENANT audit complete
4. Middleware strategy implemented

✅ **Validation passing:**
- No middleware conflicts
- Mode detection works
- Organization context correct
- Existing functionality preserved

✅ **Documentation updated:**
- Findings documented
- Decisions recorded
- Changes tracked

✅ **Ready for Phase 0:**
- Feature branch ready
- Database backup ready
- Tests passing
- Validation complete

---

## Next Steps

After completing Phase -1:

1. **Verify all fixes:** Run full validation checklist
2. **Document decisions:** Update main implementation plan
3. **Proceed to Phase 0:** Follow main implementation sequence
4. **Continuous validation:** Test after each phase

---

## References

- **Main Implementation Plan:** [BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md](./BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md)
- **Implementation Summary:** [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **BMMS Transition Plan:** [../TRANSITION_PLAN.md](../TRANSITION_PLAN.md)
- **CLAUDE.md Guidelines:** [../../../CLAUDE.md](../../../CLAUDE.md)

---

**Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** MANDATORY PRE-REQUISITE FOR IMPLEMENTATION
