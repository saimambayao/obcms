# OBCMS to BMMS Migration Guide

**Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** Ready for Implementation

## Table of Contents

1. [Overview](#overview)
2. [Migration Strategy](#migration-strategy)
3. [Pre-Migration Checklist](#pre-migration-checklist)
4. [Step-by-Step Migration](#step-by-step-migration)
5. [Mode Switching](#mode-switching)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Post-Migration Verification](#post-migration-verification)

---

## Overview

### What is BMMS?

**BMMS (Bangsamoro Ministerial Management System)** is the strategic evolution of OBCMS from a single-organization platform serving only OOBC to a comprehensive multi-tenant management system serving all 44 BARMM Ministries, Offices, and Agencies (MOAs).

### Migration Approach

OBCMS uses an **embedded architecture** approach where BMMS functionality is built directly into the existing codebase with a mode switch:

- **OBCMS Mode** (Single-tenant): System operates as before, serving only OOBC
- **BMMS Mode** (Multi-tenant): System serves 44 MOAs with organization-based data isolation

### Key Benefits

- **Zero disruption** to existing OOBC operations
- **No separate deployment** required
- **Gradual rollout** from single to multi-tenant
- **One codebase** to maintain
- **Seamless transition** with full rollback capability

---

## Migration Strategy

### Three-Phase Migration Pattern

All model migrations follow a consistent **three-step pattern** to ensure zero downtime and data safety:

```
Step 1: Make organization field nullable
  ↓
Step 2: Populate organization for existing data
  ↓
Step 3: Make organization field required (NOT NULL)
```

This ensures:
- Existing data continues working during migration
- No risk of data loss
- Can validate at each step before proceeding
- Full rollback capability at any point

### Zero-Downtime Strategy

1. **Deploy code first** - New code is backward compatible with old data
2. **Run migrations** - Three-step pattern ensures safety
3. **Validate data** - Verify organization assignment before continuing
4. **Switch mode** - Activate BMMS mode only after validation complete

---

## Pre-Migration Checklist

### System Requirements

**CRITICAL:** Complete all items before starting migration:

- [ ] **Backup database** - Full backup with timestamp
  ```bash
  ./scripts/db_backup.sh
  ```

- [ ] **Review current deployment** - Document all environment variables
  ```bash
  cd src
  python manage.py check --deploy
  ```

- [ ] **Test environment ready** - Staging environment mirrors production
- [ ] **Rollback plan documented** - Clear steps to revert if needed
- [ ] **Stakeholders notified** - OOBC and OCM staff informed
- [ ] **Maintenance window scheduled** - 2-4 hour window for migration

### Environment Verification

Verify your current environment settings:

```bash
cd src
python manage.py shell -c "
from django.conf import settings
print(f'BMMS_MODE: {settings.BMMS_MODE}')
print(f'DEFAULT_ORGANIZATION_CODE: {settings.DEFAULT_ORGANIZATION_CODE}')
print(f'Database: {settings.DATABASES[\"default\"][\"NAME\"]}')
"
```

**Expected Output (OBCMS mode):**
```
BMMS_MODE: obcms
DEFAULT_ORGANIZATION_CODE: OOBC
Database: /path/to/db.sqlite3 (or postgres://...)
```

### Code Version Verification

Ensure you have the BMMS-ready codebase:

```bash
# Check if organizations app exists
ls -la src/organizations/

# Verify middleware exists
grep -n "OrganizationMiddleware" src/obc_management/settings/base.py

# Check BMMS config module
cat src/obc_management/settings/bmms_config.py
```

---

## Step-by-Step Migration

### Phase 1: Organizations App Setup

**Duration:** 15-30 minutes
**Downtime:** None

#### 1.1 Verify Organizations App Installation

The `organizations` app should already be in `INSTALLED_APPS`:

```python
# src/obc_management/settings/base.py
INSTALLED_APPS = [
    # ...
    'organizations',  # Should be present
    # ...
]
```

#### 1.2 Create Organizations Tables

Run the initial migration to create the organizations infrastructure:

```bash
cd src
python manage.py migrate organizations
```

**Expected Output:**
```
Running migrations:
  Applying organizations.0001_initial... OK
  Applying organizations.0002_organization_metadata... OK
```

#### 1.3 Create OOBC Organization

The system automatically creates the default OOBC organization on first startup. Verify it exists:

```bash
python manage.py shell -c "
from organizations.models import Organization
org = Organization.objects.get(code='OOBC')
print(f'✅ Organization: {org.name}')
print(f'   Code: {org.code}')
print(f'   Type: {org.org_type}')
print(f'   Active: {org.is_active}')
"
```

**Expected Output:**
```
✅ Organization: Office for Other Bangsamoro Communities
   Code: OOBC
   Type: moa
   Active: True
```

### Phase 2: Model Migration (Core Data)

**Duration:** 1-2 hours
**Downtime:** None (using three-step pattern)

#### 2.1 Identify Models Requiring Migration

The following models need organization fields added:

**Communities App:**
- Community
- CommunityProfile
- Barangay (via relationship)

**MANA App:**
- Assessment
- AssessmentSession
- Participant response models

**Coordination App:**
- Stakeholder
- Partnership
- Meeting/Event

**Project Central (M&E):**
- PPA (Program, Project, Activity)
- Budget tracking
- Performance indicators

**Policies App:**
- Policy
- PolicyEvidence

#### 2.2 Run Step 1 Migrations (Nullable Fields)

Make organization fields nullable first:

```bash
cd src
python manage.py migrate communities 0XXX_add_organization_nullable
python manage.py migrate mana 0XXX_add_organization_nullable
python manage.py migrate coordination 0XXX_add_organization_nullable
python manage.py migrate project_central 0XXX_add_organization_nullable
python manage.py migrate recommendations 0XXX_add_organization_nullable
```

**Verification:**
```bash
python manage.py shell -c "
from communities.models import Community
print(f'Communities: {Community.objects.count()}')
print('✅ Step 1 complete - nullable fields added')
"
```

#### 2.3 Run Step 2 Migrations (Populate Data)

Assign all existing data to OOBC organization:

```bash
cd src
python manage.py populate_organization_data
```

This management command:
1. Gets the OOBC organization
2. Updates all existing records to have `organization = OOBC`
3. Validates 100% of records are updated
4. Reports any issues found

**Expected Output:**
```
Populating organization data for existing records...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Processing Communities... ✅ 234 records updated
Processing MANA Assessments... ✅ 87 records updated
Processing Stakeholders... ✅ 156 records updated
Processing PPAs... ✅ 342 records updated
Processing Policies... ✅ 28 records updated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Organization data population complete
   Total records updated: 847
   No errors encountered
```

**Manual Verification:**
```bash
python manage.py shell -c "
from communities.models import Community
from organizations.models import Organization

oobc = Organization.objects.get(code='OOBC')
total = Community.objects.count()
with_org = Community.objects.filter(organization=oobc).count()

print(f'Total communities: {total}')
print(f'With organization: {with_org}')
print(f'✅ Coverage: {(with_org/total*100):.1f}%')
"
```

**CRITICAL:** Do not proceed to Step 3 until verification shows 100% coverage.

#### 2.4 Run Step 3 Migrations (Required Fields)

Make organization fields NOT NULL:

```bash
cd src
python manage.py migrate communities 0XXX_organization_required
python manage.py migrate mana 0XXX_organization_required
python manage.py migrate coordination 0XXX_organization_required
python manage.py migrate project_central 0XXX_organization_required
python manage.py migrate recommendations 0XXX_organization_required
```

**Warning Signs:**
If any migration fails with "NOT NULL constraint failed", it means:
- Some records were not populated in Step 2
- Run `populate_organization_data` again
- Investigate why some records were missed

### Phase 3: Middleware and Context Setup

**Duration:** 15 minutes
**Downtime:** None

#### 3.1 Verify Middleware Configuration

The organization middleware should already be in settings:

```python
# src/obc_management/settings/base.py
MIDDLEWARE = [
    # ...
    'organizations.middleware.OrganizationMiddleware',  # Should be present
    # ...
]
```

#### 3.2 Test Organization Context

Verify middleware works in OBCMS mode:

```bash
cd src
python manage.py shell -c "
from organizations.utils import get_current_organization

# This should return OOBC in OBCMS mode
org = get_current_organization()
print(f'✅ Current organization: {org.code}')
"
```

### Phase 4: View Layer Verification

**Duration:** 30 minutes
**Downtime:** None

#### 4.1 Test Key Views

Test that views still work with organization context:

```bash
cd src
python manage.py runserver 8000
```

Navigate to key pages and verify:
- [ ] Dashboard loads correctly
- [ ] Community list shows all communities
- [ ] MANA assessments accessible
- [ ] Project list displays
- [ ] No 500 errors in console

#### 4.2 Test Data Isolation (Preparatory)

Even in OBCMS mode, test that data isolation works:

```bash
python manage.py shell -c "
from communities.models import Community
from organizations.models import Organization

oobc = Organization.objects.get(code='OOBC')

# All communities should belong to OOBC
communities = Community.objects.all()
print(f'Total communities: {communities.count()}')

# Filter by organization (should return same count)
oobc_communities = Community.objects.filter(organization=oobc)
print(f'OOBC communities: {oobc_communities.count()}')

assert communities.count() == oobc_communities.count()
print('✅ Data isolation working correctly')
"
```

---

## Mode Switching

### Understanding Modes

**OBCMS Mode (Current State):**
- System serves only OOBC
- All data belongs to OOBC organization
- Single-tenant behavior
- No organization switching UI
- Organization field populated but not enforced in UI

**BMMS Mode (Future State):**
- System serves 44 MOAs
- Each MOA has isolated data
- Multi-tenant behavior
- Organization switching enabled
- Organization field enforced everywhere

### When to Switch Modes

**DO NOT switch to BMMS mode until:**

1. **All migrations complete** - All models have organization fields
2. **Data verified** - 100% of records assigned to organizations
3. **Testing complete** - Staging environment validated
4. **Pilot MOAs ready** - At least 3 MOAs prepared for onboarding
5. **Training complete** - Staff trained on multi-tenant features
6. **Stakeholders ready** - OOBC and OCM coordinated

**Recommended Timeline:**
- **Phase 1-4** (Above): Complete in development/staging
- **Pilot Period**: Run OBCMS mode for 2-4 weeks after migration
- **Phase 5**: Switch to BMMS mode for pilot MOA onboarding
- **Phase 6**: Full rollout to all 44 MOAs

### Switching from OBCMS to BMMS Mode

#### Option A: Environment Variable (Recommended)

1. **Update .env file:**
   ```bash
   # Change from:
   BMMS_MODE=obcms

   # To:
   BMMS_MODE=bmms
   ```

2. **Restart application:**
   ```bash
   # Docker
   docker-compose restart web

   # Systemd
   sudo systemctl restart obcms

   # Gunicorn (manual)
   sudo systemctl restart gunicorn
   ```

3. **Verify mode switch:**
   ```bash
   cd src
   python manage.py shell -c "
   from obc_management.settings.bmms_config import is_bmms_mode
   print(f'BMMS Mode: {is_bmms_mode()}')
   "
   ```

#### Option B: Settings Override

For testing or temporary switches:

```python
# src/obc_management/settings/local.py
from .base import *

BMMS_MODE = 'bmms'  # Override
```

### Post-Switch Verification

After switching to BMMS mode, verify:

```bash
cd src
python manage.py shell -c "
from obc_management.settings.bmms_config import (
    is_bmms_mode,
    multi_tenant_enabled,
    organization_switching_enabled
)

print(f'✅ BMMS Mode: {is_bmms_mode()}')
print(f'✅ Multi-tenant: {multi_tenant_enabled()}')
print(f'✅ Org Switching: {organization_switching_enabled()}')

from organizations.models import Organization
print(f'✅ Organizations: {Organization.objects.filter(is_active=True).count()}')
"
```

**Expected Output (BMMS mode):**
```
✅ BMMS Mode: True
✅ Multi-tenant: True
✅ Org Switching: True
✅ Organizations: 1 (will be 44 after full onboarding)
```

### UI Changes After Mode Switch

**BMMS mode activates:**
- Organization selector in navigation
- Organization context in all views
- Filtered queries by organization
- Organization-specific dashboards
- OCM aggregated view access

---

## Rollback Procedures

### When to Rollback

Rollback if you encounter:
- Data integrity issues (missing organization assignments)
- Performance degradation
- Critical bugs affecting operations
- Stakeholder concerns requiring more preparation

### Rollback Options

#### Option 1: Mode Rollback (Instant)

**Severity:** Low - No data loss
**Downtime:** < 5 minutes

Simply switch back to OBCMS mode:

```bash
# 1. Update .env
BMMS_MODE=obcms

# 2. Restart
docker-compose restart web

# 3. Verify
cd src
python manage.py shell -c "
from obc_management.settings.bmms_config import is_obcms_mode
print(f'OBCMS Mode: {is_obcms_mode()}')
"
```

**Effect:**
- System returns to single-tenant behavior
- All organization fields remain populated
- No data loss
- Can switch back to BMMS later

#### Option 2: Database Rollback (Full)

**Severity:** High - Restores to pre-migration state
**Downtime:** 15-30 minutes

Use if migrations caused data issues:

```bash
# 1. Stop application
docker-compose down

# 2. Restore from backup
cd /path/to/obcms
./scripts/db_restore.sh backups/db.backup.TIMESTAMP

# 3. Roll back migrations
cd src
python manage.py migrate communities 0XXX_before_organization
python manage.py migrate mana 0XXX_before_organization
# ... repeat for all apps

# 4. Restart
docker-compose up -d

# 5. Verify
python manage.py shell -c "
from communities.models import Community
print(f'Communities: {Community.objects.count()}')
"
```

**Warning:** This loses any data created after the backup.

#### Option 3: Partial Rollback

If specific models have issues:

```bash
# Roll back only problematic app
cd src
python manage.py migrate communities 0XXX_before_organization

# Keep other apps migrated
# Can re-attempt migration for that app later
```

### Post-Rollback Actions

After any rollback:

1. **Document what happened** - Write post-mortem
2. **Analyze root cause** - Why did rollback occur?
3. **Test in staging** - Reproduce and fix issue
4. **Plan re-migration** - Schedule when to try again
5. **Notify stakeholders** - Communicate status

---

## Troubleshooting

### Common Issues

#### Issue 1: Migration Fails at Step 3

**Symptom:**
```
django.db.utils.IntegrityError: NOT NULL constraint failed:
communities_community.organization_id
```

**Cause:** Not all records were populated in Step 2

**Solution:**
```bash
# 1. Roll back to Step 2
cd src
python manage.py migrate communities 0XXX_add_organization_nullable

# 2. Re-run population
python manage.py populate_organization_data

# 3. Verify 100% coverage
python manage.py shell -c "
from communities.models import Community
total = Community.objects.count()
with_org = Community.objects.exclude(organization=None).count()
print(f'Coverage: {with_org}/{total} = {(with_org/total*100):.1f}%')
"

# 4. If 100%, retry Step 3
python manage.py migrate communities 0XXX_organization_required
```

#### Issue 2: Views Return Empty Results

**Symptom:** After migration, views show no data (empty lists)

**Cause:** Organization context not set correctly in middleware

**Diagnosis:**
```bash
cd src
python manage.py shell -c "
from organizations.utils import get_current_organization
org = get_current_organization()
print(f'Current org: {org}')

if org is None:
    print('❌ No organization context set!')
else:
    print(f'✅ Organization: {org.code}')
"
```

**Solution:**
- Verify middleware is in MIDDLEWARE list
- Check middleware order (should be after SessionMiddleware)
- Ensure user is authenticated before accessing views
- In OBCMS mode, OOBC should be set automatically

#### Issue 3: Performance Degradation

**Symptom:** Queries much slower after migration

**Cause:** Missing database indexes on organization field

**Solution:**
```bash
cd src
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

# Check indexes
cursor.execute(\"\"\"
    SELECT name FROM sqlite_master
    WHERE type='index' AND tbl_name='communities_community';
\"\"\")

for row in cursor.fetchall():
    print(f'Index: {row[0]}')
"

# Create missing indexes if needed
python manage.py migrate --fake-initial
```

#### Issue 4: OOBC Organization Not Created

**Symptom:**
```
organizations.models.Organization.DoesNotExist: Organization matching
query does not exist.
```

**Solution:**
```bash
cd src
python manage.py shell -c "
from organizations.models import Organization

# Manually create OOBC organization
Organization.objects.create(
    code='OOBC',
    name='Office for Other Bangsamoro Communities',
    org_type='moa',
    is_active=True,
    metadata={
        'description': 'Serves Bangsamoro communities outside BARMM',
        'focus_areas': ['Region IX', 'X', 'XI', 'XII']
    }
)
print('✅ OOBC organization created')
"
```

### Debug Commands

#### Check Migration Status
```bash
cd src
python manage.py showmigrations communities
python manage.py showmigrations mana
python manage.py showmigrations coordination
```

#### Check Organization Data Coverage
```bash
python manage.py shell -c "
from communities.models import Community
from mana.models import Assessment
from coordination.models import Stakeholder
from project_central.models import PPA

models = [
    ('Communities', Community),
    ('Assessments', Assessment),
    ('Stakeholders', Stakeholder),
    ('PPAs', PPA),
]

for name, model in models:
    total = model.objects.count()
    with_org = model.objects.exclude(organization=None).count()
    pct = (with_org/total*100) if total > 0 else 0
    status = '✅' if pct == 100 else '❌'
    print(f'{status} {name}: {with_org}/{total} ({pct:.1f}%)')
"
```

#### Test Organization Context
```bash
cd src
python manage.py shell -c "
from django.test import RequestFactory
from organizations.middleware import OrganizationMiddleware
from django.contrib.auth import get_user_model

User = get_user_model()
factory = RequestFactory()
middleware = OrganizationMiddleware(lambda r: None)

# Create test request
request = factory.get('/')
request.user = User.objects.first()

# Process middleware
middleware.process_request(request)

from organizations.utils import get_current_organization
org = get_current_organization()
print(f'Organization set: {org}')
"
```

---

## Post-Migration Verification

### Verification Checklist

After migration is complete, verify:

#### Database Integrity
- [ ] All models have organization fields
- [ ] 100% of records have organization assigned
- [ ] No NULL organization_id values
- [ ] Foreign keys working correctly

#### Application Functionality
- [ ] Dashboard loads
- [ ] Community list works
- [ ] MANA assessments accessible
- [ ] Projects display correctly
- [ ] Forms save with organization
- [ ] Reports generate

#### Performance
- [ ] Query times acceptable (<500ms for lists)
- [ ] No N+1 query issues
- [ ] Indexes working correctly

#### Data Isolation (Preparatory)
- [ ] All OOBC data accessible
- [ ] Organization filter working
- [ ] No cross-organization leaks

### Verification Script

Run comprehensive verification:

```bash
cd src
python manage.py verify_bmms_migration
```

**Expected Output:**
```
BMMS Migration Verification Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Organizations App
   - OOBC organization exists
   - Organization model working

✅ Model Migrations
   - Communities: 234/234 (100%)
   - Assessments: 87/87 (100%)
   - Stakeholders: 156/156 (100%)
   - PPAs: 342/342 (100%)
   - Policies: 28/28 (100%)

✅ Middleware
   - OrganizationMiddleware active
   - Context setting working

✅ Views
   - All views rendering
   - No 500 errors

✅ Database Performance
   - Indexes created
   - Query times normal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Migration verification complete - All checks passed!
```

---

## Next Steps

After successful migration:

1. **Monitor for 1 week** - Watch for issues in production
2. **Document lessons learned** - Update this guide with findings
3. **Plan pilot MOA onboarding** - Prepare 3 MOAs for BMMS mode
4. **Schedule mode switch** - Set date to activate BMMS mode
5. **Train staff** - Prepare users for multi-tenant features

## Related Documentation

- [BMMS Configuration Guide](BMMS_CONFIGURATION_GUIDE.md) - Environment variables and settings
- [BMMS Deployment Checklist](../deployment/BMMS_DEPLOYMENT_CHECKLIST.md) - Production deployment
- [BMMS Transition Plan](TRANSITION_PLAN.md) - Overall BMMS strategy
- [Development README](../development/README.md) - Development guidelines

## Support

**Questions or issues during migration?**
- Check [Troubleshooting](#troubleshooting) section above
- Review [BMMS Configuration Guide](BMMS_CONFIGURATION_GUIDE.md)
- Contact technical lead or system administrator

---

**Document Version:** 1.0
**Maintained By:** OBCMS Development Team
**Last Reviewed:** 2025-10-14
