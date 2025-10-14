# BMMS Configuration Guide

**Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** Complete

## Table of Contents

1. [Overview](#overview)
2. [Core Settings](#core-settings)
3. [Environment Variables](#environment-variables)
4. [Mode-Dependent Behavior](#mode-dependent-behavior)
5. [Configuration Examples](#configuration-examples)
6. [Validation Commands](#validation-commands)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What is BMMS Configuration?

BMMS configuration controls how the system operates in single-tenant (OBCMS) versus multi-tenant (BMMS) mode. The configuration is managed through:

1. **Environment variables** (`.env` file) - Primary configuration method
2. **Django settings** (`settings/base.py`) - Read environment variables
3. **BMMS config module** (`settings/bmms_config.py`) - Mode detection utilities

### Configuration Philosophy

- **Environment-based** - All configuration via environment variables
- **Safe defaults** - OBCMS mode is default (backward compatible)
- **Explicit activation** - BMMS mode must be explicitly enabled
- **No code changes** - Mode switching without code deployment

---

## Core Settings

### BMMS_MODE

**Purpose:** Controls whether system operates in single-tenant (OBCMS) or multi-tenant (BMMS) mode.

**Type:** String enum
**Default:** `'obcms'`
**Required:** No (defaults to OBCMS mode if not set)

**Valid Values:**
- `'obcms'` - Single-tenant mode (OOBC only)
- `'bmms'` - Multi-tenant mode (44 MOAs)

**Environment Variable:**
```bash
# .env
BMMS_MODE=obcms  # Default
# or
BMMS_MODE=bmms   # Multi-tenant mode
```

**Django Setting:**
```python
# src/obc_management/settings/base.py
from obc_management.settings.bmms_config import BMMSMode

BMMS_MODE = env.str('BMMS_MODE', default=BMMSMode.OBCMS)
```

**Usage in Code:**
```python
from obc_management.settings.bmms_config import is_bmms_mode, is_obcms_mode

if is_bmms_mode():
    # Multi-tenant behavior
    show_organization_selector()
else:
    # Single-tenant behavior
    hide_organization_selector()
```

**Effect on System:**
- **OBCMS mode**: All data belongs to OOBC, no organization switching
- **BMMS mode**: Data isolated by organization, org switching enabled

---

### DEFAULT_ORGANIZATION_CODE

**Purpose:** Specifies which organization is the default (used in OBCMS mode and as fallback).

**Type:** String
**Default:** `'OOBC'`
**Required:** No (defaults to OOBC)

**Environment Variable:**
```bash
# .env
DEFAULT_ORGANIZATION_CODE=OOBC  # Default
```

**Django Setting:**
```python
# src/obc_management/settings/base.py
DEFAULT_ORGANIZATION_CODE = env.str('DEFAULT_ORGANIZATION_CODE', default='OOBC')
```

**Usage in Code:**
```python
from obc_management.settings.bmms_config import get_default_organization_code

# Get default organization
default_code = get_default_organization_code()  # Returns 'OOBC'

# Use in queries
from organizations.models import Organization
default_org = Organization.objects.get(code=default_code)
```

**When It's Used:**
- OBCMS mode: All operations use this organization
- BMMS mode: Fallback when no organization context set
- Initial data population during migration
- Default for new data creation

---

### ENABLE_MULTI_TENANT

**Purpose:** Enables multi-tenant features (data isolation, organization filtering).

**Type:** Boolean
**Default:** Depends on BMMS_MODE
- `True` if `BMMS_MODE='bmms'`
- `False` if `BMMS_MODE='obcms'`

**Environment Variable:**
```bash
# .env
ENABLE_MULTI_TENANT=0  # Disabled (OBCMS mode)
# or
ENABLE_MULTI_TENANT=1  # Enabled (BMMS mode)
```

**Django Setting:**
```python
# src/obc_management/settings/base.py
ENABLE_MULTI_TENANT = env.bool(
    'ENABLE_MULTI_TENANT',
    default=(BMMS_MODE == BMMSMode.BMMS)
)
```

**Usage in Code:**
```python
from obc_management.settings.bmms_config import multi_tenant_enabled

if multi_tenant_enabled():
    # Apply organization filters to queries
    queryset = queryset.filter(organization=current_org)
else:
    # No filtering needed (single-tenant)
    pass
```

**Effect on System:**
- **Enabled**: Queries automatically filtered by organization
- **Disabled**: Queries return all data regardless of organization

---

### ALLOW_ORGANIZATION_SWITCHING

**Purpose:** Controls whether users can switch between organizations.

**Type:** Boolean
**Default:** Depends on BMMS_MODE
- `True` if `BMMS_MODE='bmms'`
- `False` if `BMMS_MODE='obcms'`

**Environment Variable:**
```bash
# .env
ALLOW_ORGANIZATION_SWITCHING=0  # Disabled (OBCMS mode)
# or
ALLOW_ORGANIZATION_SWITCHING=1  # Enabled (BMMS mode)
```

**Django Setting:**
```python
# src/obc_management/settings/base.py
ALLOW_ORGANIZATION_SWITCHING = env.bool(
    'ALLOW_ORGANIZATION_SWITCHING',
    default=(BMMS_MODE == BMMSMode.BMMS)
)
```

**Usage in Templates:**
```django
{% load bmms_tags %}

{% if organization_switching_enabled %}
    <div class="organization-selector">
        {% include "organizations/organization_selector.html" %}
    </div>
{% endif %}
```

**Effect on System:**
- **Enabled**: Shows organization selector in UI, allows switching
- **Disabled**: Hides organization selector, locked to default org

---

### OCM_ORGANIZATION_CODE

**Purpose:** Identifies the Office of the Chief Minister (OCM) organization for aggregated reporting.

**Type:** String
**Default:** `'OCM'`
**Required:** No (only needed in BMMS mode with OCM features)

**Environment Variable:**
```bash
# .env
OCM_ORGANIZATION_CODE=OCM  # Default
```

**Django Setting:**
```python
# src/obc_management/settings/base.py
OCM_ORGANIZATION_CODE = env.str('OCM_ORGANIZATION_CODE', default='OCM')
```

**Usage in Code:**
```python
from django.conf import settings
from organizations.models import Organization

# Check if current user is from OCM
current_org = get_current_organization()
if current_org.code == settings.OCM_ORGANIZATION_CODE:
    # Show aggregated data from all MOAs
    all_data = get_aggregated_data()
else:
    # Show only this organization's data
    org_data = get_organization_data(current_org)
```

**Effect on System:**
- OCM users see read-only aggregated data from all 44 MOAs
- Other MOA users see only their organization's data

---

## Environment Variables

### Complete .env Template for BMMS

#### OBCMS Mode Configuration
```bash
# =================================================================
# BMMS CONFIGURATION - OBCMS MODE (Single-tenant)
# =================================================================

# System runs in single-tenant mode (OOBC only)
BMMS_MODE=obcms

# Default organization is OOBC
DEFAULT_ORGANIZATION_CODE=OOBC

# Multi-tenant features disabled
ENABLE_MULTI_TENANT=0

# Organization switching disabled
ALLOW_ORGANIZATION_SWITCHING=0

# OCM organization (not used in OBCMS mode, but can be defined)
OCM_ORGANIZATION_CODE=OCM
```

#### BMMS Mode Configuration
```bash
# =================================================================
# BMMS CONFIGURATION - BMMS MODE (Multi-tenant)
# =================================================================

# System runs in multi-tenant mode (44 MOAs)
BMMS_MODE=bmms

# Default organization is still OOBC (fallback)
DEFAULT_ORGANIZATION_CODE=OOBC

# Multi-tenant features enabled
ENABLE_MULTI_TENANT=1

# Organization switching enabled
ALLOW_ORGANIZATION_SWITCHING=1

# OCM organization for aggregated reporting
OCM_ORGANIZATION_CODE=OCM
```

### Environment Variable Precedence

Configuration loading order:

1. **Environment variables** (`.env` file) - Highest priority
2. **Django settings defaults** (`settings/base.py`) - If env var not set
3. **BMMS config defaults** (`settings/bmms_config.py`) - Fallback

Example:
```bash
# If .env has:
BMMS_MODE=bmms

# It overrides the default in settings/base.py:
BMMS_MODE = env.str('BMMS_MODE', default=BMMSMode.OBCMS)
# Result: BMMS_MODE = 'bmms'
```

### Required vs Optional Variables

**Required for Production:**
- None! All BMMS settings have safe defaults

**Recommended for BMMS Mode:**
- `BMMS_MODE=bmms` (activate multi-tenant)
- `ENABLE_MULTI_TENANT=1` (enable data isolation)
- `ALLOW_ORGANIZATION_SWITCHING=1` (enable org switching)

**Optional:**
- `DEFAULT_ORGANIZATION_CODE` (defaults to OOBC)
- `OCM_ORGANIZATION_CODE` (defaults to OCM)

---

## Mode-Dependent Behavior

### Feature Matrix

| Feature | OBCMS Mode | BMMS Mode |
|---------|-----------|-----------|
| **Data Isolation** | No (all OOBC) | Yes (per MOA) |
| **Organization Selector** | Hidden | Visible |
| **Organization Switching** | Disabled | Enabled |
| **Multi-tenant Queries** | Disabled | Enabled |
| **OCM Aggregation** | Not applicable | Enabled |
| **Organization Field** | Populated | Required |
| **Dashboard** | OOBC-specific | Org-specific |

### Query Behavior

#### OBCMS Mode
```python
# In OBCMS mode, queries return all data (all belongs to OOBC)
from communities.models import Community

communities = Community.objects.all()
# Returns: All 234 communities (all OOBC's)
```

#### BMMS Mode
```python
# In BMMS mode, queries auto-filter by current organization
from communities.models import Community

communities = Community.objects.all()
# With organization context set to OOBC: Returns OOBC's 234 communities
# With organization context set to TESDA: Returns TESDA's communities only
```

### UI Behavior

#### OBCMS Mode UI
- No organization selector in navigation
- Dashboard shows OOBC data only
- No organization switching options
- Single-tenant user experience

#### BMMS Mode UI
- Organization selector in navigation
- Dashboard shows current organization's data
- Dropdown to switch organizations
- Multi-tenant user experience with clear org context

### Permission Behavior

#### OBCMS Mode Permissions
```python
# Users have access to OOBC data
user.has_perm('communities.view_community')  # Can view OOBC communities
```

#### BMMS Mode Permissions
```python
# Users have access only to their organization's data
user.has_perm('communities.view_community')  # Can view only
# Permission + Organization membership determines access
```

### Middleware Behavior

#### OBCMS Mode Middleware
```python
# OrganizationMiddleware sets context to OOBC
def process_request(request):
    if is_obcms_mode():
        # Always set to default organization (OOBC)
        set_current_organization(default_org)
```

#### BMMS Mode Middleware
```python
# OrganizationMiddleware sets context based on user
def process_request(request):
    if is_bmms_mode():
        # Set to user's organization or selected organization
        set_current_organization(user.current_organization)
```

---

## Configuration Examples

### Example 1: Development (OBCMS Mode)

```bash
# .env
DJANGO_SETTINGS_MODULE=obc_management.settings.development
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1

# BMMS: OBCMS mode for development
BMMS_MODE=obcms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=0
ALLOW_ORGANIZATION_SWITCHING=0

# Database: SQLite for development
# (No DATABASE_URL needed, uses default)

# Redis: Local Redis
REDIS_URL=redis://localhost:6379/0
```

### Example 2: Staging (OBCMS Mode)

```bash
# .env
DJANGO_SETTINGS_MODULE=obc_management.settings.staging
DEBUG=0
SECRET_KEY=staging-secret-key-50-characters-minimum-abc123xyz789
ALLOWED_HOSTS=staging.obcms.gov.ph
CSRF_TRUSTED_ORIGINS=https://staging.obcms.gov.ph

# BMMS: OBCMS mode for staging (pre-migration)
BMMS_MODE=obcms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=0
ALLOW_ORGANIZATION_SWITCHING=0

# Database: PostgreSQL
DATABASE_URL=postgres://obcms_staging:staging_password@db:5432/obcms_staging

# Redis: Staging Redis
REDIS_URL=redis://redis:6379/0
```

### Example 3: Production (OBCMS Mode - Initial Deployment)

```bash
# .env
DJANGO_SETTINGS_MODULE=obc_management.settings.production
DEBUG=0
SECRET_KEY=production-secret-key-cryptographically-secure-50-chars
ALLOWED_HOSTS=obcms.gov.ph,www.obcms.gov.ph
CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph

# BMMS: OBCMS mode for production (initial state)
BMMS_MODE=obcms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=0
ALLOW_ORGANIZATION_SWITCHING=0

# Database: PostgreSQL Production
DATABASE_URL=postgres://obcms_prod:secure_password@db:5432/obcms_prod

# Redis: Production Redis
REDIS_URL=redis://redis:6379/0

# Email: Production SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gov.ph
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@obcms.gov.ph
EMAIL_HOST_PASSWORD=email_secure_password

# Security
SECURE_SSL_REDIRECT=1
SECURE_HSTS_SECONDS=31536000
```

### Example 4: Production (BMMS Mode - After Migration)

```bash
# .env
DJANGO_SETTINGS_MODULE=obc_management.settings.production
DEBUG=0
SECRET_KEY=production-secret-key-cryptographically-secure-50-chars
ALLOWED_HOSTS=bmms.gov.ph,www.bmms.gov.ph
CSRF_TRUSTED_ORIGINS=https://bmms.gov.ph,https://www.bmms.gov.ph

# BMMS: BMMS mode activated (multi-tenant)
BMMS_MODE=bmms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=1
ALLOW_ORGANIZATION_SWITCHING=1
OCM_ORGANIZATION_CODE=OCM

# Database: PostgreSQL Production (same as before)
DATABASE_URL=postgres://obcms_prod:secure_password@db:5432/obcms_prod

# Redis: Production Redis
REDIS_URL=redis://redis:6379/0

# Email: Production SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gov.ph
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@bmms.gov.ph
EMAIL_HOST_PASSWORD=email_secure_password

# Security
SECURE_SSL_REDIRECT=1
SECURE_HSTS_SECONDS=31536000
```

### Example 5: Pilot MOA Testing (BMMS Mode)

```bash
# .env
DJANGO_SETTINGS_MODULE=obc_management.settings.staging
DEBUG=0
SECRET_KEY=pilot-secret-key-for-testing-bmms-50-chars-minimum
ALLOWED_HOSTS=pilot.bmms.gov.ph
CSRF_TRUSTED_ORIGINS=https://pilot.bmms.gov.ph

# BMMS: BMMS mode for pilot testing
BMMS_MODE=bmms
DEFAULT_ORGANIZATION_CODE=OOBC
ENABLE_MULTI_TENANT=1
ALLOW_ORGANIZATION_SWITCHING=1
OCM_ORGANIZATION_CODE=OCM

# Database: Separate pilot database
DATABASE_URL=postgres://bmms_pilot:pilot_password@db:5432/bmms_pilot

# Redis: Pilot Redis
REDIS_URL=redis://redis:6379/0
```

---

## Validation Commands

### Check Current Configuration

```bash
cd src
python manage.py shell -c "
from django.conf import settings
from obc_management.settings.bmms_config import (
    is_bmms_mode,
    is_obcms_mode,
    get_default_organization_code,
    multi_tenant_enabled,
    organization_switching_enabled
)

print('BMMS Configuration Status')
print('=' * 50)
print(f'BMMS_MODE: {settings.BMMS_MODE}')
print(f'DEFAULT_ORGANIZATION_CODE: {settings.DEFAULT_ORGANIZATION_CODE}')
print(f'ENABLE_MULTI_TENANT: {settings.ENABLE_MULTI_TENANT}')
print(f'ALLOW_ORGANIZATION_SWITCHING: {settings.ALLOW_ORGANIZATION_SWITCHING}')
print(f'OCM_ORGANIZATION_CODE: {settings.OCM_ORGANIZATION_CODE}')
print()
print('Helper Functions:')
print(f'is_bmms_mode(): {is_bmms_mode()}')
print(f'is_obcms_mode(): {is_obcms_mode()}')
print(f'get_default_organization_code(): {get_default_organization_code()}')
print(f'multi_tenant_enabled(): {multi_tenant_enabled()}')
print(f'organization_switching_enabled(): {organization_switching_enabled()}')
"
```

**Expected Output (OBCMS Mode):**
```
BMMS Configuration Status
==================================================
BMMS_MODE: obcms
DEFAULT_ORGANIZATION_CODE: OOBC
ENABLE_MULTI_TENANT: False
ALLOW_ORGANIZATION_SWITCHING: False
OCM_ORGANIZATION_CODE: OCM

Helper Functions:
is_bmms_mode(): False
is_obcms_mode(): True
get_default_organization_code(): OOBC
multi_tenant_enabled(): False
organization_switching_enabled(): False
```

**Expected Output (BMMS Mode):**
```
BMMS Configuration Status
==================================================
BMMS_MODE: bmms
DEFAULT_ORGANIZATION_CODE: OOBC
ENABLE_MULTI_TENANT: True
ALLOW_ORGANIZATION_SWITCHING: True
OCM_ORGANIZATION_CODE: OCM

Helper Functions:
is_bmms_mode(): True
is_obcms_mode(): False
get_default_organization_code(): OOBC
multi_tenant_enabled(): True
organization_switching_enabled(): True
```

### Verify Organization Context

```bash
cd src
python manage.py shell -c "
from organizations.utils import get_current_organization
from organizations.models import Organization

print('Organization Context Test')
print('=' * 50)

# Check if default org exists
try:
    default_org = Organization.objects.get(code='OOBC')
    print(f'✅ Default org exists: {default_org.name}')
except Organization.DoesNotExist:
    print('❌ Default org does not exist!')

# Test context setting
org = get_current_organization()
if org:
    print(f'✅ Current organization: {org.code} - {org.name}')
else:
    print('⚠️ No organization context set (expected in shell)')
"
```

### Test Mode-Dependent Query Behavior

```bash
cd src
python manage.py shell -c "
from communities.models import Community
from organizations.models import Organization
from obc_management.settings.bmms_config import is_bmms_mode

print('Query Behavior Test')
print('=' * 50)

# Get total communities
total = Community.objects.count()
print(f'Total communities: {total}')

# Test organization filter
oobc = Organization.objects.get(code='OOBC')
oobc_communities = Community.objects.filter(organization=oobc).count()
print(f'OOBC communities: {oobc_communities}')

# Check if mode affects queries
if is_bmms_mode():
    print('✅ BMMS mode: Queries will auto-filter by organization')
else:
    print('✅ OBCMS mode: Queries return all data (all OOBC)')

# Verify coverage
if total == oobc_communities:
    print('✅ All data assigned to OOBC (migration complete)')
else:
    print(f'⚠️ Some data not assigned: {total - oobc_communities} orphaned')
"
```

### Validate Settings Against Deployment Checklist

```bash
cd src
python manage.py check --deploy
```

This checks:
- DEBUG is False in production
- SECRET_KEY is set and secure
- ALLOWED_HOSTS configured
- Security middleware enabled
- CSRF settings correct
- And more...

---

## Troubleshooting

### Issue 1: Mode Not Changing

**Symptom:** Changed `BMMS_MODE` in `.env` but system still in old mode

**Cause:** Application not restarted after env change

**Solution:**
```bash
# Docker
docker-compose restart web

# Systemd
sudo systemctl restart obcms

# Development server
# Ctrl+C and restart python manage.py runserver
```

### Issue 2: Environment Variable Not Read

**Symptom:** Setting shows default value instead of `.env` value

**Diagnosis:**
```bash
# Check if .env file is in correct location
ls -la .env

# Check if django-environ is reading .env
cd src
python manage.py shell -c "
import os
print(f'.env loaded: {\"BMMS_MODE\" in os.environ}')
print(f'BMMS_MODE value: {os.environ.get(\"BMMS_MODE\", \"NOT SET\")}')
"
```

**Solution:**
1. Ensure `.env` is in project root (same directory as `manage.py`)
2. Verify no typos in variable names
3. Restart application after changes

### Issue 3: Multi-tenant Features Not Working

**Symptom:** `BMMS_MODE=bmms` but data not isolated

**Diagnosis:**
```bash
cd src
python manage.py shell -c "
from obc_management.settings.bmms_config import multi_tenant_enabled
print(f'Multi-tenant enabled: {multi_tenant_enabled()}')
"
```

**Solution:**
If False when should be True:
```bash
# Explicitly set in .env
ENABLE_MULTI_TENANT=1

# Restart application
docker-compose restart web
```

### Issue 4: Organization Selector Not Showing

**Symptom:** In BMMS mode but no org selector in UI

**Diagnosis:**
```bash
cd src
python manage.py shell -c "
from obc_management.settings.bmms_config import organization_switching_enabled
print(f'Org switching enabled: {organization_switching_enabled()}')
"
```

**Solution:**
```bash
# Ensure both settings are enabled
BMMS_MODE=bmms
ALLOW_ORGANIZATION_SWITCHING=1

# Clear template cache
python manage.py shell -c "
from django.core.cache import cache
cache.clear()
"

# Restart
docker-compose restart web
```

### Issue 5: Default Organization Not Found

**Symptom:**
```
organizations.models.Organization.DoesNotExist:
Organization matching query does not exist.
```

**Diagnosis:**
```bash
cd src
python manage.py shell -c "
from organizations.models import Organization
print(f'Organizations: {Organization.objects.count()}')
print(f'Codes: {list(Organization.objects.values_list(\"code\", flat=True))}')
"
```

**Solution:**
```bash
# Create default organization
cd src
python manage.py shell -c "
from organizations.models import Organization

Organization.objects.get_or_create(
    code='OOBC',
    defaults={
        'name': 'Office for Other Bangsamoro Communities',
        'org_type': 'moa',
        'is_active': True,
    }
)
print('✅ Default organization created')
"
```

### Issue 6: Configuration Mismatch

**Symptom:** `BMMS_MODE=obcms` but `ENABLE_MULTI_TENANT=1` (contradictory)

**Diagnosis:**
```bash
cd src
python manage.py shell -c "
from django.conf import settings
from obc_management.settings.bmms_config import is_bmms_mode, multi_tenant_enabled

print(f'BMMS_MODE: {settings.BMMS_MODE}')
print(f'is_bmms_mode(): {is_bmms_mode()}')
print(f'ENABLE_MULTI_TENANT: {settings.ENABLE_MULTI_TENANT}')
print(f'multi_tenant_enabled(): {multi_tenant_enabled()}')

# Check for mismatch
if not is_bmms_mode() and multi_tenant_enabled():
    print('⚠️ CONFIGURATION MISMATCH!')
    print('OBCMS mode should not have multi-tenant enabled')
"
```

**Solution:**
Use consistent configuration:
```bash
# OBCMS Mode (Consistent)
BMMS_MODE=obcms
ENABLE_MULTI_TENANT=0
ALLOW_ORGANIZATION_SWITCHING=0

# BMMS Mode (Consistent)
BMMS_MODE=bmms
ENABLE_MULTI_TENANT=1
ALLOW_ORGANIZATION_SWITCHING=1
```

---

## Related Documentation

- [OBCMS to BMMS Migration Guide](OBCMS_TO_BMMS_MIGRATION_GUIDE.md) - Step-by-step migration
- [BMMS Deployment Checklist](../deployment/BMMS_DEPLOYMENT_CHECKLIST.md) - Production deployment
- [Development README](../development/README.md) - Development setup
- [BMMS Transition Plan](TRANSITION_PLAN.md) - Overall strategy

## Support

**Configuration questions or issues?**
- Check [Troubleshooting](#troubleshooting) section above
- Review [Validation Commands](#validation-commands)
- Contact technical lead or system administrator

---

**Document Version:** 1.0
**Maintained By:** OBCMS Development Team
**Last Reviewed:** 2025-10-14
