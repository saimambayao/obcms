# BMMS Mode Switching Process

## Overview

The BMMS implementation enables seamless switching between OBCMS (single-tenant) and BMMS (multi-tenant) modes through simple configuration changes. This process requires no code modifications and can be completed in under a minute.

## Prerequisites

### System Requirements
- ✅ **BMMS Implementation**: Embedded architecture already implemented
- ✅ **Configuration Files**: `.env.obcms` and `.env.bmms` templates available
- ✅ **Database**: Migrated models with organization scoping
- ✅ **Restart Access**: Ability to restart the application server

### Environment Variables
The following key environment variables control mode switching:

| Variable | OBCMS Mode | BMMS Mode | Purpose |
|----------|------------|-----------|---------|
| `BMMS_MODE` | `obcms` | `bmms` | Primary mode switch |
| `ENABLE_MULTI_TENANT` | `False` | `True` | Multi-tenant features |
| `ALLOW_ORGANIZATION_SWITCHING` | `False` | `True` | Organization switching |
| `DEFAULT_ORGANIZATION_CODE` | `OOBC` | `OOBC` | Default org code |

## Step-by-Step Mode Switching

### Current Mode Detection

Before switching, verify the current operational mode:

```bash
# Method 1: Django shell
python manage.py shell -c "
from obc_management.settings.bmms_config import is_bmms_mode, is_obcms_mode
if is_bmms_mode():
    print('Current Mode: BMMS (Multi-tenant)')
elif is_obcms_mode():
    print('Current Mode: OBCMS (Single-tenant)')
else:
    print('Mode: Unknown')
"

# Method 2: Environment variable
echo $BMMS_MODE

# Method 3: Configuration check
python manage.py shell -c "
from django.conf import settings
print('BMMS_MODE:', getattr(settings, 'BMMS_MODE', 'Not set'))
print('ENABLE_MULTI_TENANT:', getattr(settings, 'ENABLE_MULTI_TENANT', 'Not set'))
"
```

### OBCMS → BMMS Mode Switch

**Step 1: Backup Current Configuration**
```bash
# Create timestamped backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

**Step 2: Switch to BMMS Configuration**
```bash
# Apply BMMS configuration
cp .env.bmms .env

# Verify configuration change
grep "BMMS_MODE=" .env
# Should show: BMMS_MODE=bmms
```

**Step 3: Restart Application Server**
```bash
# For development
python manage.py runserver --noreload

# For production (systemd)
sudo systemctl restart obcms

# For production (gunicorn)
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# For Docker
docker-compose restart web
```

**Step 4: Verify BMMS Mode**
```bash
# Test mode detection
python manage.py shell -c "
from obc_management.settings.bmms_config import is_bmms_mode, multi_tenant_enabled
print('BMMS Mode:', is_bmms_mode())
print('Multi-tenant Enabled:', multi_tenant_enabled())
"

# Test URL structure
curl -I http://localhost:8000/moa/OOBC/dashboard/
# Should return 200 OK if authenticated
```

**Expected Results:**
- URLs now require organization prefix: `/moa/<ORG>/`
- Multi-tenant features enabled
- Organization switching available
- All existing data preserved

### BMMS → OBCMS Mode Switch

**Step 1: Backup Current Configuration**
```bash
# Create timestamped backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

**Step 2: Switch to OBCMS Configuration**
```bash
# Apply OBCMS configuration
cp .env.obcms .env

# Verify configuration change
grep "BMMS_MODE=" .env
# Should show: BMMS_MODE=obcms
```

**Step 3: Restart Application Server**
```bash
# For development
python manage.py runserver --noreload

# For production (systemd)
sudo systemctl restart obcms

# For production (gunicorn)
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# For Docker
docker-compose restart web
```

**Step 4: Verify OBCMS Mode**
```bash
# Test mode detection
python manage.py shell -c "
from obc_management.settings.bmms_config import is_obcms_mode, multi_tenant_enabled
print('OBCMS Mode:', is_obcms_mode())
print('Multi-tenant Enabled:', multi_tenant_enabled())
"

# Test URL structure
curl -I http://localhost:8000/dashboard/
# Should return 200 OK if authenticated
```

**Expected Results:**
- URLs work without organization prefix
- Multi-tenant features disabled
- OOBC organization auto-injected
- All existing data preserved

## Configuration File Templates

### OBCMS Configuration (.env.obcms)
```bash
# ========== BMMS MODE SETTINGS ==========
BMMS_MODE=obcms
DEFAULT_ORGANIZATION_CODE=OOBC

# ========== MULTI-TENANT SETTINGS ==========
ENABLE_MULTI_TENANT=False
ALLOW_ORGANIZATION_SWITCHING=False

# ========== DATABASE CONFIGURATION ==========
DATABASE_URL=sqlite:///db.sqlite3

# ========== APPLICATION SETTINGS ==========
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# ========== SITE CONFIGURATION ==========
SITE_NAME=OBCMS
SITE_DESCRIPTION=Office for Other Bangsamoro Communities Management System
```

### BMMS Configuration (.env.bmms)
```bash
# ========== BMMS MODE SETTINGS ==========
BMMS_MODE=bmms
DEFAULT_ORGANIZATION_CODE=OOBC

# ========== MULTI-TENANT SETTINGS ==========
ENABLE_MULTI_TENANT=True
ALLOW_ORGANIZATION_SWITCHING=True

# ========== DATABASE CONFIGURATION ==========
DATABASE_URL=postgresql://user:password@localhost:5432/bmms_db

# ========== APPLICATION SETTINGS ==========
DEBUG=False
SECRET_KEY=generate-strong-secret-key-for-production-deployment
ALLOWED_HOSTS=bmms.oobc.gov.ph,www.bmms.oobc.gov.ph

# ========== SITE CONFIGURATION ==========
SITE_NAME=BMMS
SITE_DESCRIPTION=Bangsamoro Ministerial Management System
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Mode Detection Fails
**Symptoms:**
- `is_bmms_mode()` returns unexpected result
- Configuration changes not applied

**Solutions:**
```bash
# Check environment variables
env | grep BMMS

# Restart Django shell
python manage.py shell
from django.conf import settings
print(settings.BMMS_MODE)

# Check configuration file syntax
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('BMMS_MODE'))"
```

#### Issue 2: URL Structure Not Updating
**Symptoms:**
- Old URLs still work after mode switch
- New URLs return 404 errors

**Solutions:**
```bash
# Clear URL cache
python manage.py check --deploy

# Verify URL patterns
python manage.py shell -c "
from django.urls import reverse
from obc_management.settings.bmms_config import is_bmms_mode
print('BMMS Mode:', is_bmms_mode())
try:
    print('Dashboard URL:', reverse('dashboard'))
except Exception as e:
    print('URL Error:', e)
"

# Restart application (ensure full restart)
pkill -f "python.*manage.py.*runserver"
python manage.py runserver
```

#### Issue 3: Database Connection Errors
**Symptoms:**
- Application won't start after mode switch
- Database connection errors in logs

**Solutions:**
```bash
# Check database URL
echo $DATABASE_URL

# Test database connection
python manage.py dbshell --help
python manage.py check --database default

# For PostgreSQL (BMMS mode)
psql postgresql://user:password@localhost:5432/bmms_db -c "SELECT 1;"

# For SQLite (OBCMS mode)
sqlite3 db.sqlite3 "SELECT 1;"
```

#### Issue 4: Middleware Errors
**Symptoms:**
- 500 errors on all requests
- Middleware-related error messages

**Solutions:**
```bash
# Check middleware configuration
python manage.py shell -c "
from django.conf import settings
print('Middleware:')
for i, middleware in enumerate(settings.MIDDLEWARE):
    print(f'  {i}: {middleware}')
"

# Verify middleware imports
python -c "
from organizations.middleware.obcms_middleware import OBCMSOrganizationMiddleware
from organizations.middleware.organization import OrganizationMiddleware
print('Middleware imports successful')
"
```

## Validation Checklist

### Pre-Switch Validation
- [ ] Current mode successfully detected
- [ ] Database accessible and healthy
- [ ] Configuration templates exist
- [ ] Backup procedures tested
- [ ] Restart permissions verified

### Post-Switch Validation
- [ ] New mode successfully detected
- [ ] Application starts without errors
- [ ] URL structure matches expected pattern
- [ ] Authentication still works
- [ ] Data accessible and intact
- [ ] No error messages in logs
- [ ] Performance acceptable

### Production Readiness
- [ ] Staging environment tested
- [ ] Full test suite passes
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Team notified of change

## Automation Scripts

### Mode Switch Script (Development)
```bash
#!/bin/bash
# switch_mode.sh - Development mode switch utility

set -e

MODE=${1:-"help"}
BACKUP_DIR="backups"

# Create backup directory
mkdir -p $BACKUP_DIR

case $MODE in
  "obcms")
    echo "Switching to OBCMS mode..."
    cp .env $BACKUP_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)
    cp .env.obcms .env
    echo "✅ Configuration updated"
    ;;
  "bmms")
    echo "Switching to BMMS mode..."
    cp .env $BACKUP_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)
    cp .env.bmms .env
    echo "✅ Configuration updated"
    ;;
  "check")
    python manage.py shell -c "
from obc_management.settings.bmms_config import is_bmms_mode
print('Current Mode:', 'BMMS' if is_bmms_mode() else 'OBCMS')
"
    ;;
  *)
    echo "Usage: $0 {obcms|bmms|check}"
    echo "  obcms - Switch to OBCMS (single-tenant) mode"
    echo "  bmms  - Switch to BMMS (multi-tenant) mode"
    echo "  check - Display current mode"
    exit 1
    ;;
esac

echo "🔄 Restart your application server to apply changes"
```

### Production Mode Switch Script
```bash
#!/bin/bash
# switch_mode_production.sh - Production mode switch utility

set -e

MODE=${1:-"help"}
SERVICE_NAME="obcms"
BACKUP_DIR="/var/backups/obcms"

# Root check
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Create backup directory
mkdir -p $BACKUP_DIR

case $MODE in
  "obcms")
    echo "Switching to OBCMS mode (production)..."
    cp /etc/obcms/.env $BACKUP_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)
    cp /etc/obcms/.env.obcms /etc/obcms/.env
    chown www-data:www-data /etc/obcms/.env
    systemctl restart $SERVICE_NAME
    echo "✅ OBCMS mode activated"
    ;;
  "bmms")
    echo "Switching to BMMS mode (production)..."
    cp /etc/obcms/.env $BACKUP_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)
    cp /etc/obcms/.env.bmms /etc/obcms/.env
    chown www-data:www-data /etc/obcms/.env
    systemctl restart $SERVICE_NAME
    echo "✅ BMMS mode activated"
    ;;
  "status")
    systemctl status $SERVICE_NAME
    python manage.py shell -c "
from obc_management.settings.bmms_config import is_bmms_mode
print('Current Mode:', 'BMMS' if is_bmms_mode() else 'OBCMS')
"
    ;;
  *)
    echo "Usage: sudo $0 {obcms|bmms|status}"
    echo "  obcms  - Switch to OBCMS (single-tenant) mode"
    echo "  bmms   - Switch to BMMS (multi-tenant) mode"
    echo "  status - Display current status"
    exit 1
    ;;
esac

echo "🔍 Verifying service status..."
sleep 5
systemctl is-active --quiet $SERVICE_NAME && echo "✅ Service running" || echo "❌ Service failed"
```

## Best Practices

### Development Environment
1. **Always backup** configuration before switching
2. **Test thoroughly** in development before production
3. **Use version control** to track configuration changes
4. **Document all** mode switches for audit trail

### Production Environment
1. **Schedule maintenance window** for mode switches
2. **Notify all users** before switching modes
3. **Monitor system health** after switch
4. **Have rollback plan** ready
5. **Test in staging** before production

### Security Considerations
1. **Validate permissions** before switching modes
2. **Review security settings** for each mode
3. **Audit access controls** after switch
4. **Monitor for unusual activity**

---

**Related Documentation:**
- [System Changes](SYSTEM_CHANGES.md) - What changes occur during mode switching
- [Data Preservation](DATA_PRESERVATION.md) - Data integrity and compatibility
- [Production Readiness](PRODUCTION_READINESS.md) - Production deployment status

**Last Updated:** October 14, 2025  
**Implementation Status:** Complete  
**Testing Status:** Ready for staging validation