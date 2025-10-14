# BMMS Deployment Checklist

**Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [OBCMS Mode Deployment](#obcms-mode-deployment)
4. [BMMS Mode Deployment](#bmms-mode-deployment)
5. [Mode Activation Procedure](#mode-activation-procedure)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Rollback Procedures](#rollback-procedures)

---

## Overview

### Deployment Strategy

BMMS uses a **phased deployment approach**:

1. **Phase 1**: Deploy in OBCMS mode (single-tenant) - Current state
2. **Phase 2**: Run migration (add organization fields) - Still OBCMS mode
3. **Phase 3**: Validate migration for 2-4 weeks - OBCMS mode
4. **Phase 4**: Switch to BMMS mode (multi-tenant) - Mode activation
5. **Phase 5**: Onboard pilot MOAs (3 MOAs) - BMMS mode
6. **Phase 6**: Full rollout (44 MOAs) - BMMS mode

This document provides checklists for each phase.

### Critical Rules

**WARNING:** Follow these rules to avoid data loss or downtime:

- ⚠️ **NEVER switch directly to BMMS mode without running migrations first**
- ⚠️ **ALWAYS test in staging before production**
- ⚠️ **ALWAYS backup database before any deployment**
- ⚠️ **ALWAYS validate configuration before restarting services**
- ⚠️ **ALWAYS have rollback plan ready**

---

## Pre-Deployment Checklist

### Required Before ANY Deployment

Complete ALL items before proceeding:

#### Documentation Review

- [ ] Read [PostgreSQL Migration Summary](POSTGRESQL_MIGRATION_SUMMARY.md)
- [ ] Read [OBCMS to BMMS Migration Guide](../plans/bmms/OBCMS_TO_BMMS_MIGRATION_GUIDE.md)
- [ ] Read [BMMS Configuration Guide](../plans/bmms/BMMS_CONFIGURATION_GUIDE.md)
- [ ] Review [Staging Environment Guide](../env/staging-complete.md)

#### Environment Verification

- [ ] Staging environment mirrors production
- [ ] PostgreSQL database ready (no PostGIS needed)
- [ ] Redis server configured and running
- [ ] Celery worker and beat services configured
- [ ] Python 3.12+ installed
- [ ] Virtual environment created

#### Security Checklist

- [ ] New SECRET_KEY generated (50+ characters)
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- [ ] DEBUG=0 in production .env
- [ ] ALLOWED_HOSTS configured correctly
- [ ] CSRF_TRUSTED_ORIGINS set with https:// scheme
- [ ] SSL certificates valid
- [ ] Firewall rules configured

#### Database Preparation

- [ ] PostgreSQL installed and configured
- [ ] Database created with correct encoding
  ```sql
  CREATE DATABASE obcms_prod
  ENCODING 'UTF8'
  LC_COLLATE='en_US.UTF-8'
  LC_CTYPE='en_US.UTF-8';
  ```
- [ ] Database user created with appropriate permissions
- [ ] DATABASE_URL environment variable set
- [ ] Database backup strategy in place

#### Backup Strategy

- [ ] Full database backup script tested
  ```bash
  ./scripts/db_backup.sh
  ```
- [ ] Backup restoration tested
  ```bash
  ./scripts/db_restore.sh backups/db.backup.TIMESTAMP
  ```
- [ ] Backup location secured
- [ ] Backup retention policy defined (30 days recommended)

---

## OBCMS Mode Deployment

### Initial Production Deployment (OBCMS Mode)

Use this checklist for the first production deployment or when running in single-tenant mode.

#### Step 1: Server Preparation (30 minutes)

- [ ] **Server access confirmed**
  ```bash
  ssh user@production-server
  ```

- [ ] **System packages updated**
  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y python3.12 python3.12-venv postgresql redis-server nginx
  ```

- [ ] **Application user created**
  ```bash
  sudo useradd -m -s /bin/bash obcms
  sudo usermod -aG sudo obcms
  ```

- [ ] **Application directory created**
  ```bash
  sudo mkdir -p /opt/obcms
  sudo chown obcms:obcms /opt/obcms
  ```

#### Step 2: Code Deployment (15 minutes)

- [ ] **Code pulled from repository**
  ```bash
  cd /opt/obcms
  git clone https://github.com/your-org/obcms.git .
  git checkout main  # Or specific release tag
  ```

- [ ] **Virtual environment created**
  ```bash
  python3.12 -m venv venv
  source venv/bin/activate
  ```

- [ ] **Dependencies installed**
  ```bash
  pip install --upgrade pip
  pip install -r requirements/production.txt
  ```

- [ ] **Version verified**
  ```bash
  pip list | grep Django
  ```

#### Step 3: Environment Configuration (20 minutes)

- [ ] **.env file created from template**
  ```bash
  cp .env.example .env
  nano .env  # Or use your preferred editor
  ```

- [ ] **OBCMS mode configuration set**
  ```bash
  # Required settings in .env:
  DJANGO_SETTINGS_MODULE=obc_management.settings.production
  DEBUG=0
  SECRET_KEY=<generated-secret-key>
  ALLOWED_HOSTS=obcms.gov.ph,www.obcms.gov.ph
  CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph

  # BMMS Settings (OBCMS mode)
  BMMS_MODE=obcms
  DEFAULT_ORGANIZATION_CODE=OOBC
  ENABLE_MULTI_TENANT=0
  ALLOW_ORGANIZATION_SWITCHING=0

  # Database
  DATABASE_URL=postgres://obcms_prod:secure_password@localhost:5432/obcms_prod

  # Redis
  REDIS_URL=redis://localhost:6379/0
  ```

- [ ] **Configuration validated**
  ```bash
  cd src
  ../venv/bin/python manage.py check --deploy
  ```

  **Expected:** No errors, only informational messages

#### Step 4: Database Setup (30 minutes)

- [ ] **Database connection tested**
  ```bash
  cd src
  ../venv/bin/python manage.py dbshell
  \q  # Exit
  ```

- [ ] **Initial migrations run**
  ```bash
  cd src
  ../venv/bin/python manage.py migrate
  ```

  **Expected Output:**
  ```
  Running migrations:
    Applying contenttypes.0001_initial... OK
    Applying auth.0001_initial... OK
    ...
    Applying organizations.0001_initial... OK
    Applying organizations.0002_organization_metadata... OK
  ```

- [ ] **Superuser created**
  ```bash
  ../venv/bin/python manage.py createsuperuser
  ```

- [ ] **Default OOBC organization verified**
  ```bash
  ../venv/bin/python manage.py shell -c "
  from organizations.models import Organization
  org = Organization.objects.get(code='OOBC')
  print(f'✅ Organization: {org.name}')
  "
  ```

- [ ] **Geographic data loaded** (if not already in DB)
  ```bash
  ../venv/bin/python manage.py load_geographic_data
  ```

#### Step 5: Static Files (15 minutes)

- [ ] **Static files collected**
  ```bash
  cd src
  ../venv/bin/python manage.py collectstatic --noinput
  ```

  **Expected:** All static files copied to STATIC_ROOT

- [ ] **Static directory permissions set**
  ```bash
  sudo chown -R obcms:obcms /opt/obcms/src/staticfiles
  sudo chmod -R 755 /opt/obcms/src/staticfiles
  ```

- [ ] **Media directory created**
  ```bash
  sudo mkdir -p /opt/obcms/media
  sudo chown -R obcms:obcms /opt/obcms/media
  sudo chmod -R 755 /opt/obcms/media
  ```

#### Step 6: Service Configuration (30 minutes)

- [ ] **Gunicorn systemd service created**
  ```bash
  sudo nano /etc/systemd/system/obcms.service
  ```

  ```ini
  [Unit]
  Description=OBCMS Gunicorn Service
  After=network.target postgresql.service redis.service

  [Service]
  Type=notify
  User=obcms
  Group=obcms
  WorkingDirectory=/opt/obcms/src
  Environment="PATH=/opt/obcms/venv/bin"
  ExecStart=/opt/obcms/venv/bin/gunicorn \
      --config /opt/obcms/gunicorn.conf.py \
      obc_management.wsgi:application
  ExecReload=/bin/kill -s HUP $MAINPID
  KillMode=mixed
  TimeoutStopSec=5
  PrivateTmp=true
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```

- [ ] **Celery worker service created**
  ```bash
  sudo nano /etc/systemd/system/obcms-celery.service
  ```

- [ ] **Celery beat service created**
  ```bash
  sudo nano /etc/systemd/system/obcms-celery-beat.service
  ```

- [ ] **Services enabled and started**
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable obcms obcms-celery obcms-celery-beat
  sudo systemctl start obcms obcms-celery obcms-celery-beat
  ```

- [ ] **Service status verified**
  ```bash
  sudo systemctl status obcms
  sudo systemctl status obcms-celery
  sudo systemctl status obcms-celery-beat
  ```

#### Step 7: Nginx Configuration (20 minutes)

- [ ] **Nginx configuration created**
  ```bash
  sudo nano /etc/nginx/sites-available/obcms
  ```

- [ ] **SSL certificates configured**
  ```bash
  sudo certbot --nginx -d obcms.gov.ph -d www.obcms.gov.ph
  ```

- [ ] **Nginx configuration linked**
  ```bash
  sudo ln -s /etc/nginx/sites-available/obcms /etc/nginx/sites-enabled/
  sudo nginx -t  # Test configuration
  sudo systemctl restart nginx
  ```

#### Step 8: Verification (20 minutes)

- [ ] **Admin interface accessible**
  - Visit: https://obcms.gov.ph/admin/
  - Login with superuser credentials
  - Verify dashboard loads

- [ ] **Application functional**
  - Dashboard displays correctly
  - Navigation works
  - No 500 errors in logs

- [ ] **Logs monitored**
  ```bash
  sudo journalctl -u obcms -f
  ```

- [ ] **Performance acceptable**
  - Response times < 500ms
  - No memory leaks
  - CPU usage normal

---

## BMMS Mode Deployment

### Prerequisites

**CRITICAL:** Before switching to BMMS mode, ensure:

- [ ] All OBCMS mode deployment steps complete
- [ ] Migration completed successfully (Phase 1-4 from migration guide)
- [ ] Data validated (100% organization assignment)
- [ ] Tested in staging environment
- [ ] Pilot MOAs prepared (at least 3 MOAs)
- [ ] Staff training complete

### Step 1: Pre-Switch Validation (30 minutes)

- [ ] **Database backup created**
  ```bash
  cd /opt/obcms
  ./scripts/db_backup.sh
  # Verify backup file created with timestamp
  ls -lh backups/
  ```

- [ ] **Current configuration documented**
  ```bash
  cd /opt/obcms/src
  ../venv/bin/python manage.py shell -c "
  from django.conf import settings
  print(f'Current BMMS_MODE: {settings.BMMS_MODE}')
  print(f'Multi-tenant: {settings.ENABLE_MULTI_TENANT}')
  "
  ```

- [ ] **Migration status verified**
  ```bash
  cd /opt/obcms/src
  ../venv/bin/python manage.py showmigrations | grep -E "organizations|communities|mana"
  ```

  **Expected:** All migrations marked with [X]

- [ ] **Organization data coverage verified**
  ```bash
  ../venv/bin/python manage.py shell -c "
  from communities.models import Community
  from mana.models import Assessment
  from project_central.models import PPA

  models = [
      ('Communities', Community),
      ('Assessments', Assessment),
      ('PPAs', PPA),
  ]

  for name, model in models:
      total = model.objects.count()
      with_org = model.objects.exclude(organization=None).count()
      pct = (with_org/total*100) if total > 0 else 0
      status = '✅' if pct == 100 else '❌'
      print(f'{status} {name}: {pct:.1f}%')
  "
  ```

  **Required:** 100% for all models

### Step 2: Configuration Update (15 minutes)

- [ ] **Maintenance mode enabled** (optional)
  ```bash
  # Create maintenance.html in static/
  # Configure Nginx to serve maintenance page
  ```

- [ ] **.env updated for BMMS mode**
  ```bash
  cd /opt/obcms
  nano .env
  ```

  **Change:**
  ```bash
  # From:
  BMMS_MODE=obcms
  ENABLE_MULTI_TENANT=0
  ALLOW_ORGANIZATION_SWITCHING=0

  # To:
  BMMS_MODE=bmms
  ENABLE_MULTI_TENANT=1
  ALLOW_ORGANIZATION_SWITCHING=1
  OCM_ORGANIZATION_CODE=OCM
  ```

- [ ] **Configuration backed up**
  ```bash
  cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
  ```

- [ ] **New configuration validated**
  ```bash
  cd /opt/obcms/src
  ../venv/bin/python manage.py check --deploy
  ```

### Step 3: Service Restart (10 minutes)

- [ ] **Services restarted in order**
  ```bash
  # 1. Stop Celery workers first
  sudo systemctl stop obcms-celery obcms-celery-beat

  # 2. Restart main application
  sudo systemctl restart obcms

  # 3. Start Celery workers
  sudo systemctl start obcms-celery obcms-celery-beat
  ```

- [ ] **Service status verified**
  ```bash
  sudo systemctl status obcms
  sudo systemctl status obcms-celery
  sudo systemctl status obcms-celery-beat
  ```

  **Expected:** All services active (running)

- [ ] **Logs monitored for errors**
  ```bash
  sudo journalctl -u obcms -n 100 --no-pager
  ```

  **Look for:** Startup messages, no errors

### Step 4: BMMS Mode Verification (20 minutes)

- [ ] **Mode switch confirmed**
  ```bash
  cd /opt/obcms/src
  ../venv/bin/python manage.py shell -c "
  from obc_management.settings.bmms_config import (
      is_bmms_mode,
      multi_tenant_enabled,
      organization_switching_enabled
  )

  print(f'BMMS Mode: {is_bmms_mode()}')
  print(f'Multi-tenant: {multi_tenant_enabled()}')
  print(f'Org Switching: {organization_switching_enabled()}')

  from organizations.models import Organization
  orgs = Organization.objects.filter(is_active=True).count()
  print(f'Active Organizations: {orgs}')
  "
  ```

  **Expected Output:**
  ```
  BMMS Mode: True
  Multi-tenant: True
  Org Switching: True
  Active Organizations: 1 (or more if pilot MOAs added)
  ```

- [ ] **UI changes visible**
  - Organization selector visible in navigation
  - Organization context displayed
  - Can switch organizations (if multiple exist)

- [ ] **Data isolation working**
  ```bash
  cd /opt/obcms/src
  ../venv/bin/python manage.py shell -c "
  from communities.models import Community
  from organizations.models import Organization

  oobc = Organization.objects.get(code='OOBC')

  # Test auto-filtering (would need request context in production)
  # This is verification that data structure is correct
  oobc_communities = Community.objects.filter(organization=oobc).count()
  print(f'✅ OOBC communities: {oobc_communities}')
  "
  ```

### Step 5: Pilot MOA Onboarding (30 minutes per MOA)

Repeat for each pilot MOA (recommended: 3 MOAs):

- [ ] **Pilot MOA organization created**
  ```bash
  cd /opt/obcms/src
  ../venv/bin/python manage.py shell -c "
  from organizations.models import Organization

  Organization.objects.create(
      code='TESDA',  # Example: TESDA
      name='Technical Education and Skills Development Authority',
      org_type='moa',
      is_active=True,
      metadata={
          'description': 'Skills development and training',
          'contact_email': 'info@tesda.bmms.gov.ph'
      }
  )
  print('✅ Pilot MOA organization created')
  "
  ```

- [ ] **Pilot MOA users created**
  ```bash
  ../venv/bin/python manage.py createsuperuser --organization=TESDA
  ```

- [ ] **Pilot MOA access verified**
  - Login as pilot MOA user
  - Verify only sees empty dashboard (no OOBC data)
  - Create test community
  - Verify OOBC cannot see pilot MOA data

### Step 6: Monitoring Setup (20 minutes)

- [ ] **Application logs monitored**
  ```bash
  sudo journalctl -u obcms -f
  ```

- [ ] **Database performance monitored**
  ```bash
  # Check query performance
  cd /opt/obcms/src
  ../venv/bin/python manage.py shell -c "
  from django.db import connection
  from django.test.utils import CaptureQueriesContext

  # Monitor query count
  with CaptureQueriesContext(connection) as queries:
      from communities.models import Community
      list(Community.objects.all()[:10])

  print(f'Queries executed: {len(queries)}')
  "
  ```

- [ ] **Error tracking configured**
  - Sentry or similar error tracking
  - Email alerts for 500 errors
  - Slack notifications (optional)

---

## Mode Activation Procedure

### Quick Reference: OBCMS → BMMS Switch

**Estimated Time:** 30 minutes
**Downtime:** 5-10 minutes (during restart)

```bash
# 1. Backup database
cd /opt/obcms
./scripts/db_backup.sh

# 2. Update .env
nano .env
# Change BMMS_MODE=obcms to BMMS_MODE=bmms
# Change ENABLE_MULTI_TENANT=0 to ENABLE_MULTI_TENANT=1
# Change ALLOW_ORGANIZATION_SWITCHING=0 to ALLOW_ORGANIZATION_SWITCHING=1

# 3. Restart services
sudo systemctl stop obcms-celery obcms-celery-beat
sudo systemctl restart obcms
sudo systemctl start obcms-celery obcms-celery-beat

# 4. Verify
cd /opt/obcms/src
../venv/bin/python manage.py shell -c "
from obc_management.settings.bmms_config import is_bmms_mode
print(f'BMMS Mode: {is_bmms_mode()}')
"

# 5. Check logs
sudo journalctl -u obcms -n 50
```

### Mode Switch Decision Matrix

| Current State | Target State | Action Required |
|---------------|--------------|-----------------|
| Fresh install | OBCMS | Deploy in OBCMS mode (use OBCMS checklist) |
| Fresh install | BMMS | Deploy OBCMS → Migrate → Switch to BMMS |
| OBCMS (pre-migration) | BMMS | Run migration first → Then switch mode |
| OBCMS (post-migration) | BMMS | Update .env → Restart services |
| BMMS | OBCMS | Update .env → Restart (rollback) |

---

## Post-Deployment Verification

### Comprehensive Verification Script

Run after any deployment or mode switch:

```bash
cd /opt/obcms/src
../venv/bin/python manage.py verify_deployment
```

### Manual Verification Checklist

#### Application Health

- [ ] **Homepage loads** (< 2 seconds)
- [ ] **Admin interface accessible**
- [ ] **Dashboard displays correctly**
- [ ] **No 500 errors in logs**

#### Database Health

- [ ] **Database connection working**
  ```bash
  cd /opt/obcms/src
  ../venv/bin/python manage.py dbshell
  \q
  ```

- [ ] **Migrations up-to-date**
  ```bash
  ../venv/bin/python manage.py showmigrations
  ```

- [ ] **Query performance acceptable**
  ```bash
  # Average query time < 100ms
  ../venv/bin/python manage.py shell -c "
  import time
  from communities.models import Community

  start = time.time()
  list(Community.objects.all()[:100])
  duration = time.time() - start

  print(f'Query time: {duration*1000:.1f}ms')
  "
  ```

#### Service Health

- [ ] **Gunicorn running**
  ```bash
  sudo systemctl status obcms
  ps aux | grep gunicorn
  ```

- [ ] **Celery worker running**
  ```bash
  sudo systemctl status obcms-celery
  ```

- [ ] **Celery beat running**
  ```bash
  sudo systemctl status obcms-celery-beat
  ```

- [ ] **Redis accessible**
  ```bash
  redis-cli ping
  # Expected: PONG
  ```

#### Security Verification

- [ ] **HTTPS working**
  ```bash
  curl -I https://obcms.gov.ph
  # Check for: Strict-Transport-Security header
  ```

- [ ] **Debug mode off**
  ```bash
  cd /opt/obcms/src
  ../venv/bin/python manage.py shell -c "
  from django.conf import settings
  print(f'DEBUG: {settings.DEBUG}')  # Must be False
  "
  ```

- [ ] **CSRF protection active**
  - Try form submission without CSRF token
  - Should be blocked with 403 error

#### BMMS-Specific Verification (If in BMMS Mode)

- [ ] **Organization selector visible**
- [ ] **Organization context working**
- [ ] **Data isolation verified**
  - Login as OOBC user → See OOBC data only
  - Login as pilot MOA user → See only their data

---

## Rollback Procedures

### Emergency Rollback: BMMS → OBCMS

**When:** Critical issues in BMMS mode requiring immediate rollback

**Duration:** 10 minutes
**Downtime:** 5 minutes

```bash
# 1. Update .env immediately
cd /opt/obcms
nano .env
# Change BMMS_MODE=bmms to BMMS_MODE=obcms
# Change ENABLE_MULTI_TENANT=1 to ENABLE_MULTI_TENANT=0

# 2. Restart services
sudo systemctl restart obcms
sudo systemctl restart obcms-celery obcms-celery-beat

# 3. Verify rollback
cd /opt/obcms/src
../venv/bin/python manage.py shell -c "
from obc_management.settings.bmms_config import is_obcms_mode
print(f'OBCMS Mode: {is_obcms_mode()}')
"

# 4. Test application
curl -I https://obcms.gov.ph

# 5. Notify stakeholders
# Send rollback notification email
```

### Full Database Rollback

**When:** Database corruption or data loss

**Duration:** 30 minutes
**Downtime:** 30 minutes

```bash
# 1. Stop all services
sudo systemctl stop obcms obcms-celery obcms-celery-beat

# 2. Restore database from backup
cd /opt/obcms
./scripts/db_restore.sh backups/db.backup.TIMESTAMP

# 3. Roll back migrations (if needed)
cd /opt/obcms/src
../venv/bin/python manage.py migrate <app> <migration_number>

# 4. Restore .env from backup
cp .env.backup.TIMESTAMP .env

# 5. Restart services
sudo systemctl start obcms obcms-celery obcms-celery-beat

# 6. Verify restoration
../venv/bin/python manage.py shell -c "
from communities.models import Community
print(f'Communities: {Community.objects.count()}')
"
```

---

## Related Documentation

- [OBCMS to BMMS Migration Guide](../plans/bmms/OBCMS_TO_BMMS_MIGRATION_GUIDE.md) - Detailed migration steps
- [BMMS Configuration Guide](../plans/bmms/BMMS_CONFIGURATION_GUIDE.md) - Configuration reference
- [PostgreSQL Migration Summary](POSTGRESQL_MIGRATION_SUMMARY.md) - Database setup
- [Staging Environment Guide](../env/staging-complete.md) - Testing environment

## Support

**Deployment issues or questions?**
- Check relevant guide for your deployment phase
- Review logs: `sudo journalctl -u obcms -n 100`
- Contact technical lead or system administrator

---

**Document Version:** 1.0
**Maintained By:** OBCMS Development Team
**Last Reviewed:** 2025-10-14
