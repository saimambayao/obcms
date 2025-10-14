# BMMS Embedded Architecture Implementation Plan

**Status:** ⚠️ REQUIRES PRE-IMPLEMENTATION RECONCILIATION
**Priority:** CRITICAL
**Created:** 2025-10-14
**Author:** System Architect
**Revised:** 2025-10-14 (Post-Audit)

---

## 🔴 CRITICAL: Pre-Implementation Reconciliation Required

**⚠️ STOP: Do NOT proceed with implementation until Phase -1 is complete.**

A comprehensive codebase audit has revealed critical conflicts between this implementation plan and the actual codebase state. These conflicts **MUST** be resolved before implementing any phases.

### Audit Findings Summary

| # | Finding | Severity | Impact | Resolution Required |
|---|---------|----------|--------|---------------------|
| 1 | Middleware Conflict | 🔴 CRITICAL | Duplicate middleware will conflict | Fix in Phase -1 |
| 2 | Wrong Organization Import | 🔴 CRITICAL | Middleware will fail | Fix in Phase -1 |
| 3 | ENABLE_MULTI_TENANT Already True | 🟡 HIGH | Behavior differs from plan | Audit in Phase -1 |
| 4 | BMMS_MODE Not Configured | 🟡 HIGH | Mode detection won't work | Add in Phase -1 |
| 5 | Models Not Converted | ✅ GOOD | Matches plan expectations | Proceed as planned |
| 6 | Infrastructure Exists | ✅ GOOD | Ready to use | Proceed as planned |

**Full Details:** See [RECONCILIATION_PLAN.md](./RECONCILIATION_PLAN.md)

### Immediate Action Required

**Before implementing Phase 0, complete Phase -1:**

1. **Fix Organization Import** (5 min) - Line 44 in `common/middleware/organization_context.py`
2. **Add BMMS_MODE Configuration** (15 min) - Create `bmms_config.py`, update `.env`
3. **Audit ENABLE_MULTI_TENANT** (30 min) - Document current True default behavior
4. **Resolve Middleware Strategy** (1 hour) - Choose refactor existing vs create new

**Estimated Time:** 2 hours
**Validation Required:** All tests must pass before Phase 0

---

## Executive Summary

This document provides a comprehensive implementation plan for deploying OBCMS with BMMS multi-tenant code architecture already embedded. The implementation ensures that transitioning from OBCMS (single-tenant for OOBC) to BMMS (multi-tenant for 44 MOAs) requires ONLY configuration changes—no code changes.

**Key Strategy:** Build BMMS multi-tenant infrastructure NOW, but hide it behind feature flags so OBCMS operates in single-tenant mode by default.

**⚠️ Important:** This plan has been revised post-audit to account for existing infrastructure conflicts. Phase -1 (Pre-Implementation Reconciliation) must be completed first.

---

## Table of Contents

0. **[Pre-Implementation Reconciliation](#pre-implementation-reconciliation)** ← **START HERE**

1. [Current State Analysis](#current-state-analysis)
2. [Architecture Overview](#architecture-overview)
3. [File Generation Plan](#file-generation-plan)
4. [File Modification Plan](#file-modification-plan)
5. [Configuration Strategy](#configuration-strategy)
6. [Model Migration Strategy](#model-migration-strategy)
7. [View Layer Strategy](#view-layer-strategy)
8. [URL Routing Strategy](#url-routing-strategy)
9. [Testing Strategy](#testing-strategy)
10. [Implementation Sequence](#implementation-sequence)
11. [Validation Checklist](#validation-checklist)

---

## Pre-Implementation Reconciliation

### Phase -1: Critical Fixes (MANDATORY - 2 hours)

**Complete BEFORE Phase 0 implementation.**

See [RECONCILIATION_PLAN.md](./RECONCILIATION_PLAN.md) for complete details.

#### Fix 1: Correct Organization Import (5 minutes) 🔴 CRITICAL

```python
# File: src/common/middleware/organization_context.py line 44
# CHANGE FROM:
from coordination.models import Organization

# CHANGE TO:
from organizations.models import Organization
```

#### Fix 2: Add BMMS_MODE Configuration (15 minutes) 🔴 CRITICAL

1. Create `src/obc_management/settings/bmms_config.py` (see File Generation Plan)
2. Add to `.env`: `BMMS_MODE=obcms`
3. Add to `.env`: `DEFAULT_ORGANIZATION_CODE=OOBC`

#### Fix 3: Audit ENABLE_MULTI_TENANT (30 minutes) 🟡 HIGH

Document current behavior where `ENABLE_MULTI_TENANT` defaults to True (line 638 in base.py).
Update to mode-dependent default: `default=(BMMS_MODE == BMMSMode.BMMS)`

#### Fix 4: Middleware Strategy Decision (1 hour) 🔴 CRITICAL

**Choose ONE approach:**

- **Option A (RECOMMENDED):** Refactor existing `OrganizationContextMiddleware` to be mode-aware
- **Option B:** Remove existing middleware and implement new stack from this plan

See RECONCILIATION_PLAN.md Section 4 for detailed comparison.

### Validation Before Phase 0

- [ ] All 4 fixes complete
- [ ] Organization import corrected
- [ ] BMMS_MODE configuration added
- [ ] Middleware strategy documented
- [ ] `python manage.py check` passes
- [ ] Existing tests pass

---

## Current State Analysis

### ⚠️ CONFLICTS DETECTED

**The following conflicts must be resolved in Phase -1 before proceeding:**

1. **Middleware Conflict:** Existing `OrganizationContextMiddleware` (line 133 in base.py) conflicts with planned new middleware
2. **Wrong Import:** Line 44 imports Organization from `coordination.models` instead of `organizations.models`
3. **Config Mismatch:** `ENABLE_MULTI_TENANT` defaults to True (should be mode-dependent)
4. **Missing Config:** No `BMMS_MODE` setting exists yet

**See Phase -1 above for resolution steps.**

### ✅ Already Implemented (Phase 1 Foundation)

**⚠️ Note:** Some components exist but have conflicts requiring fixes.

The following BMMS components already exist in the codebase:

1. **Organizations App** (`src/organizations/`)
   - `models/organization.py` - Organization and OrganizationMembership models ✅
   - `models/scoped.py` - OrganizationScopedModel base class with auto-filtering ✅
   - `middleware.py` - OrganizationMiddleware for request context ✅ (but conflicts with existing middleware)

2. **Existing Middleware** (`src/common/middleware/organization_context.py`) ⚠️
   - `OrganizationContextMiddleware` already exists (line 133 in base.py)
   - **ISSUE:** Imports Organization from wrong location (line 44)
   - **ISSUE:** Not mode-aware (doesn't distinguish OBCMS vs BMMS)
   - **ACTION REQUIRED:** Choose reconciliation strategy in Phase -1

3. **RBAC Settings** (`src/obc_management/settings/base.py`)
   - `ENABLE_MULTI_TENANT` flag ⚠️ (currently defaults to True, line 638)
   - `OCM_ORGANIZATION_CODE` configuration ✅
   - `ALLOW_ORGANIZATION_SWITCHING` flag ✅

4. **Thread-Local Organization Context**
   - `get_current_organization()` - retrieves org from thread storage ✅
   - `set_current_organization()` - sets org in thread storage ✅
   - `clear_current_organization()` - cleanup function ✅

### ❌ NOT Yet Implemented

1. **Organization Field on Existing Models**
   - Communities, MANA, Coordination, Policies models lack `organization` field
   - Models currently operate without organization scoping

2. **Organization-Aware Views**
   - Views don't inject organization into querysets
   - No organization validation in view decorators

3. **Default Organization Injection for OBCMS Mode**
   - No automatic assignment of OOBC organization
   - No middleware to enforce single-tenant behavior

4. **OBCMS vs BMMS Mode Configuration**
   - Missing distinct configuration profiles
   - No clear distinction between modes

5. **Migration Path from Single-Tenant to Multi-Tenant**
   - No three-step migration pattern (nullable → populate → required)
   - No data seeding for default organization

---

## Architecture Overview

### Dual-Mode Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     OBCMS/BMMS Codebase                     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Configuration Layer (settings.py)             │  │
│  │                                                        │  │
│  │  BMMS_MODE = 'obcms'  OR  BMMS_MODE = 'bmms'        │  │
│  │  ENABLE_MULTI_TENANT = False  OR  True               │  │
│  │  DEFAULT_ORGANIZATION_CODE = 'OOBC'                  │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Middleware Layer                              │  │
│  │                                                        │  │
│  │  OrganizationMiddleware (enhanced)                   │  │
│  │   - OBCMS mode: Auto-inject OOBC org                 │  │
│  │   - BMMS mode: Extract org from URL /moa/<CODE>/    │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Model Layer                                   │  │
│  │                                                        │  │
│  │  All models inherit OrganizationScopedModel          │  │
│  │   - organization field (ForeignKey)                   │  │
│  │   - Auto-filtering by current org                     │  │
│  │   - all_objects manager for cross-org access         │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         View Layer                                    │  │
│  │                                                        │  │
│  │  @require_organization decorator                      │  │
│  │   - OBCMS mode: Transparent (OOBC auto-injected)     │  │
│  │   - BMMS mode: Validate org access                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘

             OBCMS Mode              │     BMMS Mode
                                     │
  URLs: /communities/               │   URLs: /moa/OOBC/communities/
        /mana/assessments/          │          /moa/MOH/mana/assessments/
                                     │          /moa/MENR/planning/
  Organization: OOBC (auto)         │   Organization: From URL path
  Multi-tenant: Disabled             │   Multi-tenant: Enabled
  Org switching: Disabled            │   Org switching: Enabled
```

### Key Design Principles

1. **Configuration-Driven Behavior**
   - Single codebase, dual modes
   - Mode determined by environment variables
   - No code changes required to switch modes

2. **Backward Compatibility**
   - OBCMS URLs work without `/moa/<CODE>` prefix
   - Legacy views continue to function
   - Existing tests pass without modification

3. **Zero-Downtime Migration**
   - Three-step migration: nullable → populate → required
   - Data integrity maintained throughout
   - Rollback capability at each step

4. **Security First**
   - Organization isolation enforced at database level
   - No cross-organization data leakage
   - OCM read-only access clearly defined

---

## File Generation Plan

### 1. Configuration Management Files

#### 1.1 `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/obc_management/settings/bmms_config.py`

**Purpose:** Centralized BMMS configuration module

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

---

#### 1.2 `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/organizations/utils/__init__.py`

**Purpose:** Organization-related utility functions

```python
"""
Organization utilities for BMMS multi-tenant support.
"""
from django.conf import settings
from organizations.models import Organization
from obc_management.settings.bmms_config import (
    is_obcms_mode,
    get_default_organization_code,
)


def get_default_organization():
    """
    Get the default organization for OBCMS mode.

    Returns:
        Organization: OOBC organization instance

    Raises:
        Organization.DoesNotExist: If default org not found
    """
    code = get_default_organization_code()
    return Organization.objects.get(code=code, is_active=True)


def get_or_create_default_organization():
    """
    Get or create the default organization for OBCMS mode.

    Returns:
        tuple: (Organization, created)
    """
    code = get_default_organization_code()
    return Organization.objects.get_or_create(
        code=code,
        defaults={
            'name': 'Office for Other Bangsamoro Communities',
            'short_name': 'OOBC',
            'organization_type': 'ministry',
            'is_active': True,
            'enabled_modules': [
                'communities',
                'mana',
                'coordination',
                'policies',
                'monitoring',
            ],
        }
    )


def ensure_default_organization_exists():
    """
    Ensure default organization exists in OBCMS mode.

    Called during system initialization to guarantee OOBC org exists.
    """
    if is_obcms_mode():
        get_or_create_default_organization()
```

---

### 2. Middleware Enhancements

#### 2.1 `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/organizations/middleware/obcms_middleware.py`

**Purpose:** OBCMS-specific middleware for auto-injecting default organization

```python
"""
OBCMS Middleware for automatic organization injection.

In OBCMS mode, automatically injects the default OOBC organization
into every request without requiring URL-based organization selection.
"""
import logging
from django.http import HttpRequest, HttpResponse
from organizations.models.scoped import set_current_organization, clear_current_organization
from organizations.utils import get_or_create_default_organization
from obc_management.settings.bmms_config import is_obcms_mode

logger = logging.getLogger(__name__)


class OBCMSOrganizationMiddleware:
    """
    Auto-inject OOBC organization in OBCMS mode.

    This middleware runs BEFORE OrganizationMiddleware and sets
    the default organization for all requests in OBCMS mode.

    In BMMS mode, this middleware does nothing (OrganizationMiddleware handles it).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Cache the default organization
        self._default_org = None

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and inject default organization in OBCMS mode."""

        if is_obcms_mode():
            # Ensure default organization exists
            if not self._default_org:
                self._default_org, _ = get_or_create_default_organization()

            # Inject default organization into request
            request.organization = self._default_org
            set_current_organization(self._default_org)

            logger.debug(
                f'OBCMS mode: Auto-injected organization {self._default_org.code} '
                f'for user: {request.user.username if request.user.is_authenticated else "anonymous"}'
            )

        # Process request
        response = self.get_response(request)

        # Cleanup (if not already cleaned by OrganizationMiddleware)
        if is_obcms_mode():
            clear_current_organization()

        return response
```

---

### 3. View Decorators

#### 3.1 `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/decorators/organization.py`

**Purpose:** Organization-aware view decorators

```python
"""
Organization-aware view decorators for BMMS multi-tenant support.
"""
import logging
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from organizations.models import Organization, OrganizationMembership
from obc_management.settings.bmms_config import is_bmms_mode, is_obcms_mode

logger = logging.getLogger(__name__)


def require_organization(view_func):
    """
    Decorator to ensure request has valid organization context.

    In OBCMS mode: Transparent (organization auto-injected by middleware)
    In BMMS mode: Validates user has access to requested organization

    Usage:
        @require_organization
        def my_view(request):
            # request.organization is guaranteed to exist
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if organization exists on request
        if not hasattr(request, 'organization') or request.organization is None:
            logger.error(
                f'No organization context in request for view: {view_func.__name__}'
            )
            return HttpResponseForbidden(
                'Organization context required but not found. '
                'Please ensure middleware is properly configured.'
            )

        # In BMMS mode, validate user access
        if is_bmms_mode() and request.user.is_authenticated:
            # Superusers can access any organization
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check for active membership
            has_access = OrganizationMembership.objects.filter(
                user=request.user,
                organization=request.organization,
                is_active=True
            ).exists()

            if not has_access:
                logger.warning(
                    f'User {request.user.username} denied access to '
                    f'organization {request.organization.code}'
                )
                return HttpResponseForbidden(
                    f'You do not have access to {request.organization.name}. '
                    f'Please contact your system administrator.'
                )

        # In OBCMS mode, access is automatically granted (single org)
        return view_func(request, *args, **kwargs)

    return wrapper


def organization_param(param_name='org_code'):
    """
    Decorator to extract organization from URL parameters.

    This decorator loads the organization from a URL parameter
    and validates user access before calling the view.

    Usage:
        @organization_param('org_code')
        def my_view(request, org_code):
            # request.organization is set and validated
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Extract org code from kwargs
            org_code = kwargs.get(param_name)

            if not org_code:
                return HttpResponseForbidden(
                    f'Organization parameter "{param_name}" is required.'
                )

            # Load organization
            organization = get_object_or_404(
                Organization,
                code=org_code.upper(),
                is_active=True
            )

            # Validate access in BMMS mode
            if is_bmms_mode() and request.user.is_authenticated:
                if not request.user.is_superuser:
                    has_access = OrganizationMembership.objects.filter(
                        user=request.user,
                        organization=organization,
                        is_active=True
                    ).exists()

                    if not has_access:
                        logger.warning(
                            f'User {request.user.username} denied access to '
                            f'organization {organization.code} via URL parameter'
                        )
                        return HttpResponseForbidden(
                            f'You do not have access to {organization.name}.'
                        )

            # Set organization on request
            request.organization = organization

            # Call view
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
```

---

### 4. Management Commands

#### 4.1 `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/organizations/management/commands/ensure_default_organization.py`

**Purpose:** Management command to ensure default organization exists

```python
"""
Management command to ensure default organization exists for OBCMS mode.
"""
from django.core.management.base import BaseCommand
from organizations.utils import get_or_create_default_organization


class Command(BaseCommand):
    help = 'Ensure default OOBC organization exists for OBCMS mode'

    def handle(self, *args, **options):
        organization, created = get_or_create_default_organization()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created default organization: {organization.code} - {organization.name}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Default organization already exists: {organization.code} - {organization.name}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Organization ID: {organization.id}'
            )
        )
```

---

#### 4.2 `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/organizations/management/commands/populate_organization_field.py`

**Purpose:** Populate organization field for existing records (migration step 2)

```python
"""
Management command to populate organization field for existing records.

This is STEP 2 of the three-step migration:
1. Add nullable organization field (migration)
2. Populate organization field (this command) ✓
3. Make organization field required (migration)
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from organizations.utils import get_default_organization
from organizations.models.scoped import OrganizationScopedModel


class Command(BaseCommand):
    help = 'Populate organization field for existing records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Only populate models in this app (e.g., communities)',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Only populate this specific model (e.g., OBCCommunity)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        app_label = options.get('app')
        model_name = options.get('model')
        dry_run = options.get('dry_run', False)

        # Get default organization
        try:
            default_org = get_default_organization()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error getting default organization: {e}\n'
                    f'Run: python manage.py ensure_default_organization'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Using default organization: {default_org.code} (ID: {default_org.id})'
            )
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Get all models that inherit from OrganizationScopedModel
        scoped_models = []

        for app_config in apps.get_app_configs():
            if app_label and app_config.label != app_label:
                continue

            for model in app_config.get_models():
                if issubclass(model, OrganizationScopedModel) and not model._meta.abstract:
                    if model_name and model.__name__ != model_name:
                        continue
                    scoped_models.append(model)

        if not scoped_models:
            self.stdout.write(self.style.WARNING('No organization-scoped models found'))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Found {len(scoped_models)} organization-scoped models\n'
            )
        )

        total_updated = 0

        for model in scoped_models:
            self.stdout.write(f'Processing {model._meta.app_label}.{model.__name__}...')

            # Count records without organization
            records_without_org = model.all_objects.filter(organization__isnull=True).count()

            if records_without_org == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  All records already have organization - skipping\n'
                    )
                )
                continue

            self.stdout.write(
                self.style.WARNING(
                    f'  Found {records_without_org} records without organization'
                )
            )

            if not dry_run:
                with transaction.atomic():
                    updated = model.all_objects.filter(
                        organization__isnull=True
                    ).update(organization=default_org)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Updated {updated} records\n'
                        )
                    )
                    total_updated += updated
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Would update {records_without_org} records (DRY RUN)\n'
                    )
                )
                total_updated += records_without_org

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDRY RUN COMPLETE: Would have updated {total_updated} records total'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSUCCESS: Updated {total_updated} records total'
                )
            )
```

---

### 5. Model Base Classes

#### 5.1 `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/organizations/models/mixins.py`

**Purpose:** Model mixins for organization scoping

```python
"""
Model mixins for organization-scoped functionality.
"""
from django.db import models
from django.core.exceptions import ValidationError
from organizations.models.scoped import get_current_organization


class OrganizationValidationMixin:
    """
    Mixin to add organization-aware validation to models.

    Use this with OrganizationScopedModel to add validation
    that ensures foreign key relationships stay within the same organization.
    """

    def clean(self):
        """Validate that all foreign key relationships are within the same organization."""
        super().clean()

        # Skip validation if no organization set yet
        if not hasattr(self, 'organization') or not self.organization:
            return

        # Get all foreign key fields
        for field in self._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                # Skip self-referential and non-organization-scoped FKs
                if field.related_model == self.__class__:
                    continue

                # Check if related model has organization field
                if not hasattr(field.related_model, 'organization'):
                    continue

                # Get the related object
                related_obj = getattr(self, field.name, None)
                if related_obj and hasattr(related_obj, 'organization'):
                    if related_obj.organization != self.organization:
                        raise ValidationError({
                            field.name: f'Must belong to the same organization ({self.organization.code})'
                        })


class OrganizationAuditMixin(models.Model):
    """
    Mixin to add organization-aware audit fields to models.

    Adds created_by_org and updated_by_org fields that track
    which organization's user created/updated the record.
    """

    created_by_organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_created',
        null=True,
        blank=True,
        editable=False,
        help_text='Organization of user who created this record'
    )

    updated_by_organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_updated',
        null=True,
        blank=True,
        editable=False,
        help_text='Organization of user who last updated this record'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Auto-populate organization audit fields."""
        current_org = get_current_organization()

        if current_org:
            if not self.pk:  # New record
                self.created_by_organization = current_org
            self.updated_by_organization = current_org

        super().save(*args, **kwargs)
```

---

## File Modification Plan

### Existing Files to Modify

#### 1. Settings Configuration

##### File: `src/obc_management/settings/base.py`

**Changes Required:**

```python
# Add after existing imports
from obc_management.settings.bmms_config import BMMSMode

# ADD NEW SETTINGS (after RBAC_SETTINGS):
# ========== BMMS MODE CONFIGURATION ==========
# Operational mode: 'obcms' (single-tenant) or 'bmms' (multi-tenant)
BMMS_MODE = env.str('BMMS_MODE', default=BMMSMode.OBCMS)

# Default organization code for OBCMS mode
DEFAULT_ORGANIZATION_CODE = env.str('DEFAULT_ORGANIZATION_CODE', default='OOBC')

# MODIFY EXISTING RBAC_SETTINGS:
RBAC_SETTINGS = {
    # Enable multi-tenant organization context
    # In OBCMS mode, this is automatically set to False
    'ENABLE_MULTI_TENANT': env.bool('ENABLE_MULTI_TENANT', default=(BMMS_MODE == BMMSMode.BMMS)),

    # Office of Chief Minister (OCM) organization code
    'OCM_ORGANIZATION_CODE': 'OCM',  # Changed from 'ocm' to 'OCM'

    # Permission cache timeout (seconds)
    'CACHE_TIMEOUT': 300,  # 5 minutes

    # Organization switching
    # In OBCMS mode, this is automatically set to False
    'ALLOW_ORGANIZATION_SWITCHING': env.bool(
        'ALLOW_ORGANIZATION_SWITCHING',
        default=(BMMS_MODE == BMMSMode.BMMS)
    ),

    # Session key for current organization
    'SESSION_ORG_KEY': 'current_organization',
}

# MODIFY MIDDLEWARE (insert OBCMSOrganizationMiddleware BEFORE OrganizationMiddleware):
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "common.middleware.DeprecatedURLRedirectMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "axes.middleware.AxesMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware",  # NEW: OBCMS auto-injection
    "organizations.middleware.OrganizationMiddleware",  # EXISTING: BMMS org extraction
    "common.middleware.AuditMiddleware",
    # ... rest unchanged
]
```

**Reasoning:**
- `BMMS_MODE` distinguishes between OBCMS (single-tenant) and BMMS (multi-tenant) modes
- `DEFAULT_ORGANIZATION_CODE` specifies which organization to use in OBCMS mode
- `ENABLE_MULTI_TENANT` automatically adjusts based on mode
- Middleware ordering ensures OBCMS auto-injection happens first

---

#### 2. Organization Middleware Enhancement

##### File: `src/organizations/middleware.py`

**Changes Required:**

Add at the top after imports:

```python
from obc_management.settings.bmms_config import is_bmms_mode, is_obcms_mode
```

Modify the `__call__` method to skip in OBCMS mode:

```python
def __call__(self, request: HttpRequest) -> HttpResponse:
    """
    Process request and set organization context.

    In OBCMS mode: This middleware does nothing (OBCMSOrganizationMiddleware handles it)
    In BMMS mode: Extract organization from URL and validate access
    """

    # In OBCMS mode, organization is already set by OBCMSOrganizationMiddleware
    if is_obcms_mode():
        # Just pass through - organization already set
        response = self.get_response(request)
        return response

    # BMMS mode: Extract organization from URL path
    org_code = self._extract_org_code_from_url(request.path)

    # ... rest of existing code unchanged
```

**Reasoning:**
- In OBCMS mode, skip URL extraction (no `/moa/<CODE>` prefix)
- Organization already set by OBCMSOrganizationMiddleware
- In BMMS mode, use existing URL-based extraction logic

---

#### 3. Organization Model Enhancement

##### File: `src/organizations/models/organization.py`

**Changes Required:**

Add class method to get default organization:

```python
@classmethod
def get_default_organization(cls):
    """
    Get the default organization for OBCMS mode.

    Returns:
        Organization: Default organization instance

    Raises:
        Organization.DoesNotExist: If default org not found
    """
    from obc_management.settings.bmms_config import get_default_organization_code
    code = get_default_organization_code()
    return cls.objects.get(code=code, is_active=True)
```

**Reasoning:**
- Provides centralized access to default organization
- Used by middleware, decorators, and management commands

---

## Configuration Strategy

### Environment Variable Configurations

#### OBCMS Mode Configuration (`.env.obcms`)

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

# Site Configuration
SITE_NAME=OBCMS
SITE_DESCRIPTION=Office for Other Bangsamoro Communities Management System
```

---

#### BMMS Mode Configuration (`.env.bmms`)

```bash
# BMMS Mode - Multi-tenant for 44 MOAs

# Core Configuration
BMMS_MODE=bmms
DEFAULT_ORGANIZATION_CODE=OOBC

# Multi-tenant Settings (enabled in BMMS mode)
ENABLE_MULTI_TENANT=True
ALLOW_ORGANIZATION_SWITCHING=True

# Database (PostgreSQL required for production)
DATABASE_URL=postgresql://user:pass@localhost:5432/bmms_db

# Debug
DEBUG=False

# Security
SECRET_KEY=generate-new-secret-key-for-production
ALLOWED_HOSTS=bmms.oobc.gov.ph,www.bmms.oobc.gov.ph

# Site Configuration
SITE_NAME=BMMS
SITE_DESCRIPTION=Bangsamoro Ministerial Management System
```

---

### Mode Switching Process

**From OBCMS to BMMS:**

1. **Update .env file**
   ```bash
   # Change from:
   BMMS_MODE=obcms
   ENABLE_MULTI_TENANT=False

   # To:
   BMMS_MODE=bmms
   ENABLE_MULTI_TENANT=True
   ```

2. **Restart application**
   ```bash
   # Development
   python manage.py runserver

   # Production
   sudo systemctl restart obcms
   ```

3. **Verify mode change**
   ```bash
   python manage.py shell
   >>> from obc_management.settings.bmms_config import is_bmms_mode
   >>> is_bmms_mode()
   True
   ```

**NO CODE CHANGES REQUIRED** ✅

---

## Model Migration Strategy

### Three-Step Migration Pattern

All existing models must be migrated to include the `organization` field. This is done in three steps to ensure zero-downtime and data integrity.

#### Step 1: Add Nullable Organization Field

**For each app (communities, mana, coordination, etc.):**

**Migration File:** `src/communities/migrations/000X_add_organization_field.py`

```python
"""
Add nullable organization field to all Community models.

This is STEP 1 of 3 for BMMS multi-tenant migration.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0001_initial'),
        ('communities', 'previous_migration'),
    ]

    operations = [
        # OBCCommunity
        migrations.AddField(
            model_name='obccommunity',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,  # NULLABLE in step 1
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_obccommunity_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AddIndex(
            model_name='obccommunity',
            index=models.Index(fields=['organization'], name='communities_org_idx'),
        ),

        # MunicipalityCoverage
        migrations.AddField(
            model_name='municipalitycoverage',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_municipalitycoverage_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AddIndex(
            model_name='municipalitycoverage',
            index=models.Index(fields=['organization'], name='muni_cov_org_idx'),
        ),

        # ProvinceCoverage
        migrations.AddField(
            model_name='provincecoverage',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_provincecoverage_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),
        migrations.AddIndex(
            model_name='provincecoverage',
            index=models.Index(fields=['organization'], name='prov_cov_org_idx'),
        ),

        # CommunityLivelihood
        migrations.AddField(
            model_name='communitylivelihood',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_communitylivelihood_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),

        # Add for all other models: CommunityInfrastructure, Stakeholder, etc.
        # ... (similar pattern for each model)
    ]
```

**Apply Migration:**
```bash
cd src/
python manage.py makemigrations communities
python manage.py migrate communities
```

**Result:** All models now have nullable `organization` field. Existing records have `organization=NULL`.

---

#### Step 2: Populate Organization Field

**Run Management Command:**

```bash
# Ensure default organization exists
python manage.py ensure_default_organization

# Populate organization field for all existing records
python manage.py populate_organization_field

# Verify (dry run first)
python manage.py populate_organization_field --dry-run

# Populate specific app
python manage.py populate_organization_field --app communities

# Populate specific model
python manage.py populate_organization_field --app communities --model OBCCommunity
```

**Result:** All existing records now have `organization=OOBC`.

**Verification:**

```bash
python manage.py shell

>>> from communities.models import OBCCommunity
>>> OBCCommunity.all_objects.filter(organization__isnull=True).count()
0  # Should be 0

>>> from organizations.models import Organization
>>> oobc = Organization.objects.get(code='OOBC')
>>> OBCCommunity.all_objects.filter(organization=oobc).count()
X  # Should match total count
```

---

#### Step 3: Make Organization Field Required

**Migration File:** `src/communities/migrations/000Y_make_organization_required.py`

```python
"""
Make organization field required (NOT NULL).

This is STEP 3 of 3 for BMMS multi-tenant migration.

CRITICAL: Do NOT run this migration until Step 2 is complete
and all records have been populated with organization values.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('communities', '000X_add_organization_field'),
    ]

    operations = [
        # OBCCommunity
        migrations.AlterField(
            model_name='obccommunity',
            name='organization',
            field=models.ForeignKey(
                # NO LONGER NULLABLE
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_obccommunity_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),

        # MunicipalityCoverage
        migrations.AlterField(
            model_name='municipalitycoverage',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_municipalitycoverage_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),

        # ProvinceCoverage
        migrations.AlterField(
            model_name='provincecoverage',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='communities_provincecoverage_set',
                to='organizations.organization',
                help_text='Organization that owns this record'
            ),
        ),

        # Apply to all other models
        # ... (similar pattern)
    ]
```

**Apply Migration:**
```bash
python manage.py migrate communities
```

**Result:** `organization` field is now required. Database enforces NOT NULL constraint.

---

### Migration Sequence by App

**Order of Migration (by dependency):**

1. **Organizations** (already complete)
2. **Common** (base models - Region, Province, Municipality, Barangay, User)
   - NO organization field needed (shared across all orgs)
3. **Communities** (OBCCommunity, MunicipalityCoverage, ProvinceCoverage)
4. **MANA** (Assessment, AssessmentResponse, ManaWorkshop)
5. **Coordination** (Partnership, Activity, Stakeholder)
6. **Policies** (PolicyRecommendation, PolicyDocument, PolicyTracking)
7. **Monitoring** (if models exist)
8. **Planning** (StrategicPlan, AnnualPlan)
9. **Budget Preparation** (BudgetProposal, BudgetAllocation)
10. **Budget Execution** (Obligation, Disbursement)

**Command Sequence:**

```bash
# For each app (replace X with app name):
cd src/

# Step 1: Generate migration
python manage.py makemigrations X

# Apply Step 1 migration
python manage.py migrate X

# Step 2: Populate data
python manage.py populate_organization_field --app X

# Verify Step 2
python manage.py populate_organization_field --app X --dry-run

# Step 3: Generate "make required" migration
python manage.py makemigrations X

# Apply Step 3 migration
python manage.py migrate X
```

---

## Model Conversion Examples

### Example 1: Convert Communities App Models

#### Current Model (WITHOUT Organization):

```python
# src/communities/models.py - BEFORE
class OBCCommunity(CommunityProfileBase):
    """OBC Community model."""

    name = models.CharField(max_length=255)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE)
    # ... other fields

    class Meta:
        db_table = "communities_obc_community"
        ordering = ["name"]
```

#### Updated Model (WITH Organization):

```python
# src/communities/models.py - AFTER
from organizations.models import OrganizationScopedModel

class OBCCommunity(OrganizationScopedModel, CommunityProfileBase):
    """OBC Community model with organization scoping."""

    name = models.CharField(max_length=255)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE)
    # ... other fields

    # organization field inherited from OrganizationScopedModel
    # objects = OrganizationScopedManager() (auto-filters by current org)
    # all_objects = models.Manager() (unfiltered access)

    class Meta:
        db_table = "communities_obc_community"
        ordering = ["organization", "name"]  # Add organization to ordering
        indexes = [
            # organization index inherited from OrganizationScopedModel
        ]
```

**Changes:**
1. Inherit from `OrganizationScopedModel` (FIRST in inheritance chain)
2. Remove manual `organization` field (inherited automatically)
3. Add `organization` to `ordering` in Meta
4. No need to add index (inherited automatically)

---

### Example 2: Convert MANA App Models

#### Current Model:

```python
# src/mana/models.py - BEFORE
class Assessment(models.Model):
    """MANA Assessment model."""

    title = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    # ... other fields

    class Meta:
        db_table = "mana_assessment"
        ordering = ["-created_at"]
```

#### Updated Model:

```python
# src/mana/models.py - AFTER
from organizations.models import OrganizationScopedModel

class Assessment(OrganizationScopedModel):
    """MANA Assessment model with organization scoping."""

    title = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    # ... other fields

    # organization field inherited from OrganizationScopedModel

    class Meta:
        db_table = "mana_assessment"
        ordering = ["organization", "-created_at"]
```

---

## View Layer Strategy

### View Conversion Patterns

#### Pattern 1: Function-Based Views (CURRENT)

**Before:**
```python
# src/communities/views.py - BEFORE
from django.contrib.auth.decorators import login_required

@login_required
def community_list(request):
    """List all OBC communities."""
    communities = OBCCommunity.objects.all()  # Shows ALL communities
    return render(request, 'communities/list.html', {'communities': communities})
```

**After (OBCMS-compatible):**
```python
# src/communities/views.py - AFTER
from django.contrib.auth.decorators import login_required
from common.decorators.organization import require_organization

@login_required
@require_organization  # NEW: Ensures organization context exists
def community_list(request):
    """List all OBC communities (organization-scoped)."""
    # In OBCMS mode: Shows only OOBC communities (auto-filtered)
    # In BMMS mode: Shows only communities for request.organization
    communities = OBCCommunity.objects.all()  # Auto-filtered by OrganizationScopedManager

    return render(request, 'communities/list.html', {
        'communities': communities,
        'organization': request.organization,  # Available in template
    })
```

**Key Points:**
- Add `@require_organization` decorator (validates org context)
- No change to queryset logic (auto-filtered by manager)
- Organization available via `request.organization`

---

#### Pattern 2: Class-Based Views

**Before:**
```python
# src/mana/views.py - BEFORE
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'mana/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20
```

**After (OBCMS-compatible):**
```python
# src/mana/views.py - AFTER
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from common.mixins.organization import OrganizationRequiredMixin

class AssessmentListView(OrganizationRequiredMixin, LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'mana/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20

    def get_queryset(self):
        """Get assessments for current organization (auto-filtered)."""
        # In OBCMS mode: Returns only OOBC assessments
        # In BMMS mode: Returns only assessments for request.organization
        return super().get_queryset()  # Already filtered by OrganizationScopedManager

    def get_context_data(self, **kwargs):
        """Add organization to context."""
        context = super().get_context_data(**kwargs)
        context['organization'] = self.request.organization
        return context
```

**Key Points:**
- Add `OrganizationRequiredMixin` (FIRST in mixin chain)
- No change to queryset (auto-filtered)
- Add organization to context for template access

---

#### Pattern 3: API Views (DRF)

**Before:**
```python
# src/communities/api/views.py - BEFORE
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class OBCCommunityViewSet(viewsets.ModelViewSet):
    queryset = OBCCommunity.objects.all()
    serializer_class = OBCCommunitySerializer
    permission_classes = [IsAuthenticated]
```

**After (OBCMS-compatible):**
```python
# src/communities/api/views.py - AFTER
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from common.permissions.organization import OrganizationAccessPermission

class OBCCommunityViewSet(viewsets.ModelViewSet):
    serializer_class = OBCCommunitySerializer
    permission_classes = [IsAuthenticated, OrganizationAccessPermission]

    def get_queryset(self):
        """Get communities for current organization (auto-filtered)."""
        # In OBCMS mode: Returns only OOBC communities
        # In BMMS mode: Returns only communities for request.organization
        return OBCCommunity.objects.all()  # Auto-filtered by OrganizationScopedManager
```

**Key Points:**
- Add `OrganizationAccessPermission` to validate org access
- Use `get_queryset()` method instead of class attribute
- Queryset auto-filtered by manager

---

## URL Routing Strategy

### Dual URL Pattern Support

The system must support both OBCMS-style URLs (no org prefix) and BMMS-style URLs (with org prefix).

#### URL Configuration Changes

##### File: `src/obc_management/urls.py`

**Before:**
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('common.urls')),
    path('communities/', include('communities.urls')),
    path('mana/', include('mana.urls')),
    path('coordination/', include('coordination.urls')),
    # ...
]
```

**After (Dual-mode support):**
```python
from obc_management.settings.bmms_config import is_bmms_mode

# OBCMS-style URLs (no org prefix)
obcms_patterns = [
    path('', include('common.urls')),
    path('communities/', include('communities.urls')),
    path('mana/', include('mana.urls')),
    path('coordination/', include('coordination.urls')),
    path('policies/', include('recommendations.urls')),
    # ...
]

# BMMS-style URLs (with org prefix)
bmms_patterns = [
    path('moa/<str:org_code>/', include([
        path('', include('common.urls')),
        path('communities/', include('communities.urls')),
        path('mana/', include('mana.urls')),
        path('coordination/', include('coordination.urls')),
        path('policies/', include('recommendations.urls')),
        # ...
    ])),
]

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Add appropriate patterns based on mode
if is_bmms_mode():
    urlpatterns += bmms_patterns
    # Also support OBCMS-style for backward compatibility
    urlpatterns += obcms_patterns
else:
    # OBCMS mode: Only OBCMS-style URLs
    urlpatterns += obcms_patterns
```

**Result:**
- **OBCMS Mode:** `/communities/` works
- **BMMS Mode:** Both `/moa/OOBC/communities/` and `/communities/` work

---

## Testing Strategy

### Dual-Mode Test Suite

All tests must pass in BOTH OBCMS mode and BMMS mode.

#### Test Configuration

##### File: `src/tests/conftest.py` (NEW)

```python
"""
Pytest configuration for OBCMS/BMMS dual-mode testing.
"""
import pytest
from django.conf import settings
from obc_management.settings.bmms_config import BMMSMode
from organizations.utils import get_or_create_default_organization


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup database for tests."""
    with django_db_blocker.unblock():
        # Ensure default organization exists
        get_or_create_default_organization()


@pytest.fixture
def obcms_mode(settings):
    """Force OBCMS mode for this test."""
    settings.BMMS_MODE = BMMSMode.OBCMS
    settings.ENABLE_MULTI_TENANT = False
    settings.ALLOW_ORGANIZATION_SWITCHING = False
    return settings


@pytest.fixture
def bmms_mode(settings):
    """Force BMMS mode for this test."""
    settings.BMMS_MODE = BMMSMode.BMMS
    settings.ENABLE_MULTI_TENANT = True
    settings.ALLOW_ORGANIZATION_SWITCHING = True
    return settings


@pytest.fixture
def default_organization(db):
    """Get default OOBC organization."""
    from organizations.models import Organization
    org, _ = Organization.objects.get_or_create(
        code='OOBC',
        defaults={
            'name': 'Office for Other Bangsamoro Communities',
            'short_name': 'OOBC',
            'organization_type': 'ministry',
            'is_active': True,
        }
    )
    return org


@pytest.fixture
def sample_moa_organization(db):
    """Get sample MOA organization for BMMS testing."""
    from organizations.models import Organization
    org, _ = Organization.objects.get_or_create(
        code='MOH',
        defaults={
            'name': 'Ministry of Health',
            'short_name': 'MOH',
            'organization_type': 'ministry',
            'is_active': True,
        }
    )
    return org
```

---

#### Test Examples

##### Test 1: Model Auto-Filtering

```python
# src/communities/tests/test_organization_scoping.py
import pytest
from communities.models import OBCCommunity
from organizations.models.scoped import set_current_organization


@pytest.mark.django_db
def test_obcms_mode_auto_filters_to_oobc(obcms_mode, default_organization):
    """Test that OBCMS mode auto-filters to OOBC organization."""
    # Set current org to OOBC (simulates OBCMS middleware)
    set_current_organization(default_organization)

    # Create community (organization auto-set by OrganizationScopedModel)
    community = OBCCommunity.objects.create(
        name='Test Community',
        barangay_id=1,
    )

    # Verify organization was auto-set
    assert community.organization == default_organization

    # Verify queryset is auto-filtered
    communities = OBCCommunity.objects.all()
    assert communities.count() == 1
    assert communities.first().organization == default_organization


@pytest.mark.django_db
def test_bmms_mode_isolates_organizations(bmms_mode, default_organization, sample_moa_organization):
    """Test that BMMS mode isolates data by organization."""
    # Create communities for different organizations
    set_current_organization(default_organization)
    oobc_community = OBCCommunity.objects.create(
        name='OOBC Community',
        barangay_id=1,
    )

    set_current_organization(sample_moa_organization)
    moh_community = OBCCommunity.objects.create(
        name='MOH Community',
        barangay_id=2,
    )

    # Switch to OOBC context
    set_current_organization(default_organization)

    # Verify only OOBC community visible
    communities = OBCCommunity.objects.all()
    assert communities.count() == 1
    assert communities.first().name == 'OOBC Community'

    # Switch to MOH context
    set_current_organization(sample_moa_organization)

    # Verify only MOH community visible
    communities = OBCCommunity.objects.all()
    assert communities.count() == 1
    assert communities.first().name == 'MOH Community'

    # Verify all_objects manager sees both
    all_communities = OBCCommunity.all_objects.all()
    assert all_communities.count() == 2
```

---

##### Test 2: View Organization Context

```python
# src/communities/tests/test_views.py
import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_obcms_mode_community_list_view(client, obcms_mode, default_organization, admin_user):
    """Test community list view in OBCMS mode."""
    client.force_login(admin_user)

    # Create community
    from communities.models import OBCCommunity
    from organizations.models.scoped import set_current_organization

    set_current_organization(default_organization)
    community = OBCCommunity.objects.create(
        name='Test Community',
        barangay_id=1,
    )

    # Access community list
    url = reverse('communities:list')  # /communities/
    response = client.get(url)

    assert response.status_code == 200
    assert 'Test Community' in response.content.decode()


@pytest.mark.django_db
def test_bmms_mode_community_list_view_with_org_prefix(client, bmms_mode, default_organization, admin_user):
    """Test community list view in BMMS mode with org prefix."""
    client.force_login(admin_user)

    # Create membership for user
    from organizations.models import OrganizationMembership
    OrganizationMembership.objects.create(
        user=admin_user,
        organization=default_organization,
        role='admin',
        is_active=True,
        is_primary=True,
    )

    # Create community
    from communities.models import OBCCommunity
    from organizations.models.scoped import set_current_organization

    set_current_organization(default_organization)
    community = OBCCommunity.objects.create(
        name='Test Community',
        barangay_id=1,
    )

    # Access community list with org prefix
    url = f'/moa/OOBC/communities/'
    response = client.get(url)

    assert response.status_code == 200
    assert 'Test Community' in response.content.decode()
```

---

### Test Execution Commands

```bash
# Run all tests in OBCMS mode
BMMS_MODE=obcms pytest

# Run all tests in BMMS mode
BMMS_MODE=bmms pytest

# Run specific test file
pytest src/communities/tests/test_organization_scoping.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run only organization-related tests
pytest -k "organization"
```

---

## Implementation Sequence

### Phase-by-Phase Execution

#### Phase 0: Pre-Implementation Setup (CRITICAL)

**Duration:** 1 implementation session
**Priority:** CRITICAL

1. **Create feature branch**
   ```bash
   git checkout -b feature/bmms-embedded-architecture
   ```

2. **Backup database**
   ```bash
   cp src/db.sqlite3 src/db.sqlite3.backup
   ```

3. **Verify current state**
   ```bash
   cd src/
   python manage.py check
   python manage.py test --keepdb
   ```

**Deliverables:**
- ✅ Feature branch created
- ✅ Database backup created
- ✅ All existing tests passing

---

#### Phase 1: Configuration Infrastructure

**Duration:** 1 implementation session
**Priority:** CRITICAL

**Tasks:**

1. **Create bmms_config.py**
   - Location: `src/obc_management/settings/bmms_config.py`
   - Content: See [File Generation Plan](#file-generation-plan)

2. **Update settings/base.py**
   - Add BMMS_MODE configuration
   - Update RBAC_SETTINGS
   - Add middleware ordering

3. **Create .env.obcms and .env.bmms**
   - OBCMS configuration
   - BMMS configuration

4. **Test configuration**
   ```bash
   python manage.py shell
   >>> from obc_management.settings.bmms_config import *
   >>> is_obcms_mode()
   True
   ```

**Deliverables:**
- ✅ Configuration module created
- ✅ Settings updated
- ✅ Environment files created
- ✅ Configuration validated

---

#### Phase 2: Organization Utilities

**Duration:** 1 implementation session
**Priority:** HIGH

**Tasks:**

1. **Create organizations/utils/__init__.py**
   - Utility functions for org management
   - See [File Generation Plan](#file-generation-plan)

2. **Enhance Organization model**
   - Add `get_default_organization()` class method
   - See [File Modification Plan](#file-modification-plan)

3. **Create management commands**
   - `ensure_default_organization`
   - `populate_organization_field`

4. **Test utilities**
   ```bash
   python manage.py ensure_default_organization
   python manage.py shell
   >>> from organizations.utils import get_default_organization
   >>> org = get_default_organization()
   >>> org.code
   'OOBC'
   ```

**Deliverables:**
- ✅ Utility module created
- ✅ Organization model enhanced
- ✅ Management commands created
- ✅ Default organization exists

---

#### Phase 3: Middleware Enhancement

**Duration:** 1 implementation session
**Priority:** CRITICAL

**Tasks:**

1. **Create OBCMSOrganizationMiddleware**
   - Location: `src/organizations/middleware/obcms_middleware.py`
   - Auto-injects OOBC in OBCMS mode

2. **Update OrganizationMiddleware**
   - Skip in OBCMS mode
   - See [File Modification Plan](#file-modification-plan)

3. **Update MIDDLEWARE in settings**
   - Add OBCMSOrganizationMiddleware BEFORE OrganizationMiddleware

4. **Test middleware**
   ```bash
   python manage.py runserver
   # Access http://localhost:8000/dashboard/
   # Verify request.organization exists in templates
   ```

**Deliverables:**
- ✅ OBCMS middleware created
- ✅ Organization middleware updated
- ✅ Middleware ordering correct
- ✅ Organization auto-injection working

---

#### Phase 4: View Decorators

**Duration:** 1 implementation session
**Priority:** HIGH

**Tasks:**

1. **Create common/decorators/organization.py**
   - `@require_organization` decorator
   - `@organization_param()` decorator

2. **Create common/mixins/organization.py**
   - `OrganizationRequiredMixin` for CBVs

3. **Create common/permissions/organization.py**
   - `OrganizationAccessPermission` for DRF

4. **Test decorators**
   ```python
   # src/test_decorators.py
   from django.http import HttpRequest
   from common.decorators.organization import require_organization

   @require_organization
   def test_view(request):
       return HttpResponse(f'Org: {request.organization.code}')

   # Create test request with org
   request = HttpRequest()
   request.organization = get_default_organization()
   response = test_view(request)
   assert response.status_code == 200
   ```

**Deliverables:**
- ✅ Decorators created
- ✅ Mixins created
- ✅ Permissions created
- ✅ Decorator tests passing

---

#### Phase 5: Model Migration - Communities App

**Duration:** 2 implementation sessions
**Priority:** CRITICAL

**Tasks:**

1. **Update OBCCommunity model**
   - Inherit from OrganizationScopedModel
   - Remove manual organization field definition

2. **Generate Step 1 migration (nullable)**
   ```bash
   python manage.py makemigrations communities
   python manage.py migrate communities
   ```

3. **Populate organization field (Step 2)**
   ```bash
   python manage.py populate_organization_field --app communities
   ```

4. **Generate Step 3 migration (required)**
   ```bash
   python manage.py makemigrations communities
   python manage.py migrate communities
   ```

5. **Verify migration**
   ```bash
   python manage.py shell
   >>> from communities.models import OBCCommunity
   >>> OBCCommunity.all_objects.filter(organization__isnull=True).count()
   0
   ```

**Deliverables:**
- ✅ Models updated to inherit OrganizationScopedModel
- ✅ Step 1 migration applied (nullable)
- ✅ Step 2 population complete
- ✅ Step 3 migration applied (required)
- ✅ All communities have organization

---

#### Phase 6: Model Migration - MANA App

**Duration:** 2 implementation sessions
**Priority:** HIGH

**Tasks:**

1. **Update MANA models**
   - Assessment, AssessmentResponse, etc.

2. **Three-step migration**
   - Same process as Communities

3. **Test auto-filtering**
   ```python
   from organizations.models.scoped import set_current_organization
   set_current_organization(get_default_organization())
   assessments = Assessment.objects.all()
   # Should only show OOBC assessments
   ```

**Deliverables:**
- ✅ MANA models migrated
- ✅ Three-step migration complete
- ✅ Auto-filtering verified

---

#### Phase 7: Model Migration - Remaining Apps

**Duration:** 3-4 implementation sessions
**Priority:** MEDIUM

**Apps to migrate:**
- Coordination
- Policies
- Monitoring
- Planning
- Budget Preparation
- Budget Execution

**Process for each app:**
1. Update models
2. Generate Step 1 migration
3. Populate data (Step 2)
4. Generate Step 3 migration
5. Verify

**Deliverables:**
- ✅ All apps migrated
- ✅ All records have organization
- ✅ Auto-filtering works across all apps

---

#### Phase 8: View Layer Updates

**Duration:** 2-3 implementation sessions
**Priority:** HIGH

**Tasks:**

1. **Update function-based views**
   - Add `@require_organization` decorator

2. **Update class-based views**
   - Add `OrganizationRequiredMixin`

3. **Update API views**
   - Add `OrganizationAccessPermission`

4. **Test views**
   - Verify organization context exists
   - Verify auto-filtering works

**Deliverables:**
- ✅ All views updated with organization awareness
- ✅ View tests passing
- ✅ Organization context available in templates

---

#### Phase 9: URL Routing Enhancement

**Duration:** 1 implementation session
**Priority:** MEDIUM

**Tasks:**

1. **Update urls.py**
   - Add dual-mode URL patterns
   - Support both OBCMS and BMMS URLs

2. **Test URL routing**
   ```bash
   # OBCMS mode
   curl http://localhost:8000/communities/

   # BMMS mode (when enabled)
   curl http://localhost:8000/moa/OOBC/communities/
   ```

**Deliverables:**
- ✅ Dual URL patterns working
- ✅ Both URL styles supported

---

#### Phase 10: Testing Infrastructure

**Duration:** 2 implementation sessions
**Priority:** HIGH

**Tasks:**

1. **Create test fixtures**
   - conftest.py with OBCMS/BMMS mode fixtures

2. **Write dual-mode tests**
   - Test model auto-filtering
   - Test view organization context
   - Test data isolation

3. **Run full test suite**
   ```bash
   # OBCMS mode
   BMMS_MODE=obcms pytest

   # BMMS mode
   BMMS_MODE=bmms pytest
   ```

**Deliverables:**
- ✅ Test infrastructure created
- ✅ Dual-mode tests written
- ✅ All tests passing in both modes

---

#### Phase 11: Documentation

**Duration:** 1 implementation session
**Priority:** MEDIUM

**Tasks:**

1. **Create migration guides**
   - OBCMS → BMMS migration guide
   - Configuration guide

2. **Update development docs**
   - Add BMMS architecture overview
   - Document mode switching

3. **Create deployment checklist**
   - OBCMS deployment steps
   - BMMS deployment steps

**Deliverables:**
- ✅ Migration guides complete
- ✅ Development docs updated
- ✅ Deployment checklists created

---

#### Phase 12: Final Validation

**Duration:** 1 implementation session
**Priority:** CRITICAL

**Tasks:**

1. **Run validation checklist**
   - See [Validation Checklist](#validation-checklist)

2. **Performance testing**
   - Verify no performance degradation

3. **Merge to main**
   ```bash
   git add .
   git commit -m "Implement BMMS embedded architecture"
   git push origin feature/bmms-embedded-architecture
   # Create PR and merge
   ```

**Deliverables:**
- ✅ All validation checks passing
- ✅ Performance acceptable
- ✅ Feature merged to main

---

## Validation Checklist

### Pre-Deployment Validation

#### 1. Configuration Validation

- [ ] `BMMS_MODE` setting works correctly
- [ ] Default organization code configurable via `DEFAULT_ORGANIZATION_CODE`
- [ ] Multi-tenant flags respond to mode changes
- [ ] Environment files (`.env.obcms`, `.env.bmms`) contain correct values

**Commands:**
```bash
# Test OBCMS mode
export BMMS_MODE=obcms
python manage.py shell
>>> from obc_management.settings.bmms_config import *
>>> is_obcms_mode()
True
>>> multi_tenant_enabled()
False

# Test BMMS mode
export BMMS_MODE=bmms
python manage.py shell
>>> is_bmms_mode()
True
>>> multi_tenant_enabled()
True
```

---

#### 2. Organization Setup Validation

- [ ] Default OOBC organization exists
- [ ] OOBC has correct code, name, and configuration
- [ ] Management command `ensure_default_organization` works

**Commands:**
```bash
python manage.py ensure_default_organization
python manage.py shell
>>> from organizations.models import Organization
>>> org = Organization.objects.get(code='OOBC')
>>> org.name
'Office for Other Bangsamoro Communities'
>>> org.is_active
True
```

---

#### 3. Middleware Validation

- [ ] OBCMSOrganizationMiddleware auto-injects OOBC in OBCMS mode
- [ ] OrganizationMiddleware skips in OBCMS mode
- [ ] OrganizationMiddleware extracts org from URL in BMMS mode
- [ ] Thread-local organization context properly cleaned up

**Commands:**
```bash
# Start development server
python manage.py runserver

# Test OBCMS mode (no org prefix)
curl http://localhost:8000/dashboard/
# Should see organization context in response

# Test BMMS mode (with org prefix)
export BMMS_MODE=bmms
python manage.py runserver
curl http://localhost:8000/moa/OOBC/dashboard/
# Should see organization context
```

---

#### 4. Model Migration Validation

- [ ] All models have `organization` field
- [ ] Organization field is NOT NULL
- [ ] All existing records have organization assigned
- [ ] No orphaned records (organization=NULL)

**Commands:**
```bash
python manage.py shell

# Check each app
>>> from communities.models import OBCCommunity
>>> OBCCommunity.all_objects.filter(organization__isnull=True).count()
0

>>> from mana.models import Assessment
>>> Assessment.all_objects.filter(organization__isnull=True).count()
0

# Verify organization field exists
>>> OBCCommunity._meta.get_field('organization')
<django.db.models.fields.related.ForeignKey: organization>
```

---

#### 5. Auto-Filtering Validation

- [ ] OrganizationScopedManager auto-filters by current organization
- [ ] `Model.objects.all()` only shows current org's data
- [ ] `Model.all_objects.all()` shows all orgs' data
- [ ] Thread-local organization properly set by middleware

**Commands:**
```bash
python manage.py shell

>>> from organizations.models.scoped import set_current_organization
>>> from organizations.utils import get_default_organization
>>> from communities.models import OBCCommunity

# Set organization context
>>> org = get_default_organization()
>>> set_current_organization(org)

# Test auto-filtering
>>> OBCCommunity.objects.all().count()
X  # Should match OOBC communities

>>> OBCCommunity.objects.all()[0].organization.code
'OOBC'

# Test all_objects (no filter)
>>> OBCCommunity.all_objects.all().count()
X  # Should match total communities (same as objects if only OOBC exists)
```

---

#### 6. View Validation

- [ ] `@require_organization` decorator works
- [ ] `OrganizationRequiredMixin` works for CBVs
- [ ] Views have access to `request.organization`
- [ ] Templates can access `{{ organization }}`

**Test Views:**
```bash
# Create test view
cat > src/test_views.py << 'EOF'
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from common.decorators.organization import require_organization

@login_required
@require_organization
def test_org_view(request):
    return HttpResponse(f'Organization: {request.organization.code}')
EOF

# Add to urls.py temporarily
# path('test-org/', test_org_view)

# Test
curl -u admin:password http://localhost:8000/test-org/
# Should return: Organization: OOBC
```

---

#### 7. URL Routing Validation

- [ ] OBCMS-style URLs work: `/communities/`
- [ ] BMMS-style URLs work: `/moa/OOBC/communities/`
- [ ] Organization extracted correctly from BMMS URLs
- [ ] 404 for invalid organization codes

**Commands:**
```bash
# Test OBCMS URLs
curl http://localhost:8000/communities/

# Test BMMS URLs (after switching to BMMS mode)
export BMMS_MODE=bmms
python manage.py runserver
curl http://localhost:8000/moa/OOBC/communities/

# Test invalid org
curl http://localhost:8000/moa/INVALID/communities/
# Should return 404 or 403
```

---

#### 8. Test Suite Validation

- [ ] All existing tests pass in OBCMS mode
- [ ] All existing tests pass in BMMS mode
- [ ] New organization-specific tests pass
- [ ] Test coverage above 90%

**Commands:**
```bash
# Run tests in OBCMS mode
export BMMS_MODE=obcms
pytest --cov=src --cov-report=term-missing

# Run tests in BMMS mode
export BMMS_MODE=bmms
pytest --cov=src --cov-report=term-missing

# Run specific test files
pytest src/communities/tests/test_organization_scoping.py
pytest src/mana/tests/test_organization_scoping.py
```

---

#### 9. Data Integrity Validation

- [ ] No data loss during migration
- [ ] Record counts match before/after migration
- [ ] Foreign key relationships intact
- [ ] Existing functionality preserved

**Commands:**
```bash
python manage.py shell

# Verify record counts
>>> from communities.models import OBCCommunity
>>> OBCCommunity.all_objects.count()
# Compare with count before migration

# Check foreign keys
>>> community = OBCCommunity.objects.first()
>>> community.barangay
<Barangay object>
>>> community.barangay.municipality
<Municipality object>
```

---

#### 10. Performance Validation

- [ ] No significant performance degradation
- [ ] Database queries optimized (no N+1 problems)
- [ ] Organization filter adds negligible overhead
- [ ] Page load times acceptable

**Commands:**
```bash
# Enable query logging
export DJANGO_DEBUG=True

# Run performance tests
python manage.py test --keepdb --debug-mode

# Check query counts
python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import override_settings
>>> with override_settings(DEBUG=True):
...     communities = OBCCommunity.objects.all()[:10]
...     list(communities)
...     print(len(connection.queries))
# Should be reasonable number (not thousands)
```

---

### Post-Deployment Validation (OBCMS Mode)

#### 11. OBCMS Functional Validation

- [ ] Dashboard loads correctly
- [ ] Community list shows all OOBC communities
- [ ] MANA assessments accessible
- [ ] Coordination activities functional
- [ ] Policy recommendations work
- [ ] All CRUD operations function

**Manual Testing:**
1. Log in as OOBC admin
2. Navigate to dashboard
3. Create new community
4. Edit existing community
5. Create MANA assessment
6. Create coordination activity
7. Verify all operations successful

---

#### 12. OBCMS Data Isolation Validation

- [ ] All records belong to OOBC organization
- [ ] No cross-organization data visible
- [ ] Queries properly filtered
- [ ] Admin sees only OOBC data

**Commands:**
```bash
python manage.py shell

>>> from organizations.utils import get_default_organization
>>> org = get_default_organization()

# Verify all communities belong to OOBC
>>> from communities.models import OBCCommunity
>>> OBCCommunity.objects.exclude(organization=org).count()
0

# Verify all assessments belong to OOBC
>>> from mana.models import Assessment
>>> Assessment.objects.exclude(organization=org).count()
0
```

---

### Post-Deployment Validation (BMMS Mode)

#### 13. BMMS Multi-Org Validation

- [ ] Multiple organizations can be created
- [ ] Each organization has isolated data
- [ ] Users can switch organizations (if permitted)
- [ ] OCM can view all organizations (read-only)

**Setup Test Organizations:**
```bash
python manage.py shell

>>> from organizations.models import Organization

# Create test MOA organizations
>>> moh = Organization.objects.create(
...     code='MOH',
...     name='Ministry of Health',
...     short_name='MOH',
...     organization_type='ministry',
...     is_active=True
... )

>>> menr = Organization.objects.create(
...     code='MENR',
...     name='Ministry of Environment and Natural Resources',
...     short_name='MENR',
...     organization_type='ministry',
...     is_active=True
... )

# Verify isolation
>>> from communities.models import OBCCommunity
>>> from organizations.models.scoped import set_current_organization

>>> set_current_organization(moh)
>>> OBCCommunity.objects.count()
0  # MOH has no communities yet

>>> set_current_organization(get_default_organization())
>>> OBCCommunity.objects.count()
X  # OOBC communities visible
```

---

#### 14. BMMS URL Validation

- [ ] URLs with org prefix work: `/moa/OOBC/`
- [ ] Multiple org URLs work: `/moa/MOH/`, `/moa/MENR/`
- [ ] Invalid org codes return 404
- [ ] Unauthorized access returns 403

**Commands:**
```bash
# Test multiple org URLs
curl http://localhost:8000/moa/OOBC/dashboard/
curl http://localhost:8000/moa/MOH/dashboard/
curl http://localhost:8000/moa/MENR/dashboard/

# Test invalid org
curl http://localhost:8000/moa/INVALID/dashboard/
# Should return 404
```

---

## Final Checklist

### Completion Criteria

Before considering implementation complete, verify:

- ✅ All Phase 0-12 tasks completed
- ✅ All validation checks passing
- ✅ Zero data loss during migration
- ✅ OBCMS mode fully functional
- ✅ BMMS mode ready for activation
- ✅ Mode switching works via configuration only
- ✅ Tests pass in both modes
- ✅ Documentation complete
- ✅ Deployment guide available
- ✅ No production issues detected

---

## Rollback Plan

### If Issues Occur

**Step 1: Stop Application**
```bash
# Development
Ctrl+C (stop runserver)

# Production
sudo systemctl stop obcms
```

**Step 2: Restore Database**
```bash
# Restore from backup
cp src/db.sqlite3.backup src/db.sqlite3
```

**Step 3: Revert Code**
```bash
git checkout main
git branch -D feature/bmms-embedded-architecture
```

**Step 4: Restart Application**
```bash
# Development
python manage.py runserver

# Production
sudo systemctl start obcms
```

---

## Success Metrics

### Implementation Success Criteria

1. **Code Quality**
   - All tests pass in both OBCMS and BMMS modes
   - Code coverage above 90%
   - No linting errors
   - No security vulnerabilities

2. **Functional Requirements**
   - OBCMS operates in single-tenant mode without code changes
   - BMMS can be enabled via configuration only
   - Organization switching works in BMMS mode
   - Data isolation enforced across all modules

3. **Performance Requirements**
   - No significant performance degradation (<5% overhead)
   - Page load times under 2 seconds
   - Database queries optimized
   - No N+1 query problems

4. **Data Integrity**
   - Zero data loss during migration
   - All foreign key relationships intact
   - Record counts match before/after
   - No orphaned records

5. **Documentation**
   - Implementation guide complete
   - Migration guide complete
   - Configuration guide complete
   - Deployment checklist complete

---

## Conclusion

This implementation plan provides a comprehensive, step-by-step approach to embedding BMMS multi-tenant architecture into OBCMS. By following this plan:

1. **OBCMS continues to work exactly as it does now** (single-tenant mode)
2. **BMMS multi-tenant infrastructure is built underneath**
3. **Switching from OBCMS to BMMS requires ONLY configuration changes**
4. **No code modifications needed to transition between modes**
5. **Data integrity maintained throughout the migration**
6. **Zero-downtime deployment achievable**

The implementation ensures backward compatibility while providing a clear path forward to full multi-tenant BMMS deployment for all 44 BARMM Ministries, Offices, and Agencies.

---

**Document Version:** 1.0
**Last Updated:** 2025-10-14
**Next Review:** After Phase 6 completion
