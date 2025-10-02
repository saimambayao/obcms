# OBCMS Security Implementation Guide

**Version:** 1.0
**Date:** January 2025
**Status:** ✅ Implemented

---

## Overview

This guide documents the security enhancements implemented in OBCMS following the comprehensive security assessment. All critical and high-priority vulnerabilities have been addressed.

---

## ✅ Implemented Security Features

### 1. **API Rate Limiting** ✅ IMPLEMENTED

**Status:** Production-ready
**Files:**
- [src/common/throttling.py](../../src/common/throttling.py)
- [src/obc_management/settings/base.py:219-231](../../src/obc_management/settings/base.py#L219)

**Configuration:**

```python
# Anonymous users: 100 requests/hour
# Authenticated users: 1000 requests/hour
# Authentication endpoints: 5 attempts/minute
# Burst protection: 60 requests/minute
# Data exports: 10/hour
# Admin users: 5000 requests/hour
```

**Custom Throttle Classes:**
- `AuthenticationThrottle` - Protects login endpoints (5/minute)
- `AnonThrottle` - Anonymous users (100/hour)
- `UserThrottle` - Authenticated users (1000/hour)
- `BurstThrottle` - Short-term burst protection (60/minute)
- `DataExportThrottle` - Export operations (10/hour)
- `AdminThrottle` - Admin users (5000/hour)

**Usage in Views:**
```python
from rest_framework.decorators import throttle_classes
from common.throttling import AuthenticationThrottle

@throttle_classes([AuthenticationThrottle])
def login_view(request):
    # This view is protected by 5 attempts/minute throttle
    pass
```

---

### 2. **JWT Token Blacklisting** ✅ IMPLEMENTED

**Status:** Production-ready
**Files:**
- [src/obc_management/settings/base.py:248-254](../../src/obc_management/settings/base.py#L248)

**Features:**
- Token blacklisting on rotation
- Automatic invalidation on logout
- Compromised token revocation
- Last login tracking

**Configuration:**
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,  # ✅ New
    "UPDATE_LAST_LOGIN": True,  # ✅ New
}
```

**Logout Implementation:**
```python
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

def logout_view(request):
    # Blacklist all user tokens on logout
    tokens = OutstandingToken.objects.filter(user=request.user)
    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)
```

---

### 3. **Audit Logging (django-auditlog)** ✅ IMPLEMENTED

**Status:** Production-ready
**Files:**
- [src/common/auditlog_config.py](../../src/common/auditlog_config.py)
- [src/common/apps.py:12-18](../../src/common/apps.py#L12)
- [src/obc_management/settings/base.py:418-430](../../src/obc_management/settings/base.py#L418)

**Tracked Models:**
- User (authentication, profile changes)
- BarangayOBC, MunicipalOBC, ProvincialOBC (community data)
- Assessment, AssessmentResponse, Workshop (MANA data)
- Partnership, Stakeholder (coordination data)
- Task, Workflow, Project (project management)

**Features:**
- Automatic change tracking (who, what, when)
- Full object serialization before/after changes
- IP address tracking
- Tamper-proof audit trail

**Viewing Audit Logs:**
```python
from auditlog.models import LogEntry

# Get all changes to a specific object
logs = LogEntry.objects.get_for_object(barangay_obc_instance)

# Recent changes by user
logs = LogEntry.objects.filter(actor=user).order_by('-timestamp')[:10]
```

---

### 4. **Failed Login Tracking (django-axes)** ✅ IMPLEMENTED

**Status:** Production-ready
**Files:**
- [src/obc_management/settings/base.py:397-416](../../src/obc_management/settings/base.py#L397)

**Features:**
- Account lockout after 5 failed attempts
- 30-minute cooldown period
- IP + username combination tracking
- Auto-reset on successful login
- Proxy-aware (respects X-Forwarded-For)

**Configuration:**
```python
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5  # Lock after 5 failures
AXES_COOLOFF_TIME = timedelta(minutes=30)  # 30-minute lockout
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True
```

**Admin Interface:**
- View failed attempts: `/admin/axes/accessattempt/`
- Manually unlock accounts: Delete AccessAttempt records

---

### 5. **Security Event Logging** ✅ IMPLEMENTED

**Status:** Production-ready
**Files:**
- [src/common/security_logging.py](../../src/common/security_logging.py)

**Logged Events:**
- Failed login attempts (IP, username, reason)
- Successful logins (user, IP)
- Logout events
- Unauthorized access attempts
- Permission denials
- Sensitive data access
- Data exports (type, count, user)
- Administrative actions

**Usage:**
```python
from common.security_logging import (
    log_failed_login,
    log_successful_login,
    log_unauthorized_access,
    log_data_export,
)

# In login view
if authentication_failed:
    log_failed_login(request, username, reason="Invalid password")
else:
    log_successful_login(request, user)

# In data export view
log_data_export(request, user, "OBC Community Data", record_count=150)
```

**Decorator for Automatic Logging:**
```python
from common.security_logging import log_sensitive_access

@log_sensitive_access("MANA Assessment Data")
def view_assessment(request, assessment_id):
    # Automatically logs access to this sensitive view
    pass
```

---

### 6. **File Upload Security** ✅ IMPLEMENTED

**Status:** Production-ready
**Files:**
- [src/common/validators.py](../../src/common/validators.py)

**Validators:**
- `validate_file_size()` - Prevent disk exhaustion (default: 10MB)
- `validate_file_extension()` - Whitelist allowed extensions
- `validate_file_content_type()` - Prevent content-type spoofing (uses python-magic)
- `sanitize_filename()` - Prevent path traversal attacks
- `validate_image_file()` - Comprehensive image validation (max 5MB)
- `validate_document_file()` - Comprehensive document validation (max 10MB)

**Usage in Models:**
```python
from django.db import models
from common.validators import validate_image_file, validate_document_file

class Document(models.Model):
    photo = models.ImageField(
        upload_to='photos/%Y/%m/',
        validators=[validate_image_file]
    )
    attachment = models.FileField(
        upload_to='documents/%Y/%m/',
        validators=[validate_document_file]
    )
```

**Allowed File Types:**
- **Images:** .jpg, .jpeg, .png, .gif, .webp (max 5MB)
- **Documents:** .pdf, .doc, .docx, .xls, .xlsx (max 10MB)

---

### 7. **Stronger Password Policy** ✅ IMPLEMENTED

**Status:** Production-ready
**Files:**
- [src/obc_management/settings/base.py:150-166](../../src/obc_management/settings/base.py#L150)

**Requirements:**
- ✅ Minimum 12 characters (upgraded from 8)
- ✅ Cannot be similar to user attributes
- ✅ Cannot be common password
- ✅ Cannot be entirely numeric

**Future Enhancements:**
- Password expiration (90 days)
- Password history (prevent reuse)
- Complexity requirements (uppercase, lowercase, numbers, special chars)

---

### 8. **Dependency Vulnerability Scanning** ✅ IMPLEMENTED

**Status:** Production-ready
**Files:**
- [scripts/security_scan.sh](../../scripts/security_scan.sh)
- [.github/workflows/security.yml](../../.github/workflows/security.yml)

**Tools:**
- `pip-audit` - Python dependency CVE scanner
- `bandit` - Python code security linter
- `gitleaks` - Secret detection in git history

**Manual Scan:**
```bash
# Run dependency scan
bash scripts/security_scan.sh

# Or directly with pip-audit
pip-audit --requirement requirements/base.txt
```

**Automated CI/CD:**
- Runs on every push/PR to main/develop branches
- Weekly scheduled scan (Mondays 9:00 AM UTC)
- Scans Python dependencies, Django config, and code for security issues

---

## 🔐 Security Best Practices

### For Developers

#### 1. Always Use Security Validators

```python
# ❌ BAD: No file validation
class Document(models.Model):
    file = models.FileField(upload_to='documents/')

# ✅ GOOD: With security validation
from common.validators import validate_document_file

class Document(models.Model):
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        validators=[validate_document_file]
    )
```

#### 2. Log Security-Relevant Events

```python
# ❌ BAD: No logging
if not user.has_perm('view_community'):
    raise PermissionDenied

# ✅ GOOD: Log permission denial
from common.security_logging import log_permission_denied

if not user.has_perm('view_community'):
    log_permission_denied(request, user, 'view_community', resource=community)
    raise PermissionDenied
```

#### 3. Use Throttling for Sensitive Endpoints

```python
# ❌ BAD: No rate limiting
@api_view(['POST'])
def data_export(request):
    # Unlimited exports

# ✅ GOOD: Rate limited
from common.throttling import DataExportThrottle
from rest_framework.decorators import throttle_classes

@api_view(['POST'])
@throttle_classes([DataExportThrottle])
def data_export(request):
    # Limited to 10 exports/hour per user
```

#### 4. Never Store Secrets in Code

```python
# ❌ BAD: Hardcoded credentials
API_KEY = "sk_live_abc123def456"

# ✅ GOOD: Use environment variables
from django.conf import settings
API_KEY = settings.GOOGLE_API_KEY  # From .env
```

---

## 📊 Security Monitoring

### Monitoring Dashboards

**Failed Login Attempts:**
```bash
# View recent failed logins (requires Axes installed)
python manage.py axes_list_attempts

# Reset specific user lockout
python manage.py axes_reset_username <username>

# Reset IP-based lockout
python manage.py axes_reset_ip <ip_address>
```

**Audit Logs:**
```python
# In Django admin
http://localhost:8000/admin/auditlog/logentry/

# Programmatically
from auditlog.models import LogEntry
from datetime import timedelta
from django.utils import timezone

# Recent changes (last 24 hours)
recent = LogEntry.objects.filter(
    timestamp__gte=timezone.now() - timedelta(days=1)
).order_by('-timestamp')

# Changes by specific user
user_changes = LogEntry.objects.filter(actor=user)

# Changes to specific model
from communities.models import BarangayOBC
obc_changes = LogEntry.objects.get_for_model(BarangayOBC)
```

**Security Logs:**
```bash
# View security event logs
tail -f src/logs/django.log | grep "django.security"

# Failed login attempts
grep "Failed login" src/logs/django.log

# Unauthorized access attempts
grep "Unauthorized access" src/logs/django.log

# Data exports
grep "Data export" src/logs/django.log
```

---

## 🚀 Production Deployment Checklist

### Pre-Deployment

- [ ] Run Django security check: `python manage.py check --deploy`
- [ ] Run dependency scan: `bash scripts/security_scan.sh`
- [ ] Verify Django version ≥ 5.2.0
- [ ] Verify all security packages installed:
  - [ ] django-auditlog ≥ 3.0.0
  - [ ] django-axes ≥ 6.1.0
  - [ ] djangorestframework-simplejwt (with token_blacklist)
  - [ ] python-magic ≥ 0.4.27

### Database Migrations

```bash
# Apply security-related migrations
cd src
python manage.py migrate axes
python manage.py migrate auditlog
python manage.py migrate token_blacklist
```

### Environment Variables

Ensure these are set in production `.env`:

```bash
# Security settings already in production.py
DEBUG=0
SECRET_KEY=<50+ character random key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Rate limiting cache (Redis recommended)
REDIS_URL=redis://redis:6379/0
```

### Post-Deployment Verification

```bash
# 1. Test rate limiting
for i in {1..10}; do
  curl -X POST https://yourdomain.com/api/token/ \
       -d "username=test&password=wrong"
done
# Should return 429 Too Many Requests after 5 attempts

# 2. Verify audit logging
# Login to admin and make a change, check LogEntry table

# 3. Check security logs
curl https://yourdomain.com/health/
# Review logs for any errors
```

---

## 🔧 Troubleshooting

### Rate Limiting Issues

**Problem:** Users getting 429 errors unexpectedly

**Solution:**
```python
# Check cache connectivity
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
'value'

# Clear throttle cache (reset all rate limits)
>>> from django.core.cache import cache
>>> cache.clear()
```

### Axes Lockout Issues

**Problem:** Legitimate user locked out

**Solution:**
```bash
# Unlock specific user
python manage.py axes_reset_username <username>

# Unlock specific IP
python manage.py axes_reset_ip <ip_address>

# Unlock all
python manage.py axes_reset
```

### Auditlog Not Working

**Problem:** No audit logs appearing

**Solution:**
```python
# Verify registration in Django shell
python manage.py shell
>>> from auditlog.registry import auditlog
>>> auditlog.get_models()
# Should show registered models

# Check middleware is enabled
# src/obc_management/settings/base.py
MIDDLEWARE = [
    # ...
    'auditlog.middleware.AuditlogMiddleware',  # Must be after AuthenticationMiddleware
]
```

---

## 📚 Additional Resources

### Documentation
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [DRF Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [django-auditlog](https://django-auditlog.readthedocs.io/)
- [django-axes](https://django-axes.readthedocs.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### Security Tools
- `pip-audit` - Dependency vulnerability scanning
- `bandit` - Python code security linter
- `safety` - Alternative dependency scanner
- `gitleaks` - Secret detection

---

## 🎯 Next Steps

### Short-Term (Month 1)
- [ ] Deploy centralized logging (Graylog/ELK)
- [ ] Configure real-time security alerts
- [ ] Implement data retention policies
- [ ] Create incident response runbooks

### Medium-Term (Month 2-3)
- [ ] Deploy WAF (Cloudflare or AWS WAF)
- [ ] Add malware scanning for file uploads (ClamAV)
- [ ] Enable database encryption at rest
- [ ] Conduct penetration testing

### Long-Term (Month 4-6)
- [ ] Implement password expiration policy
- [ ] Add multi-factor authentication (MFA)
- [ ] Deploy intrusion detection system (IDS)
- [ ] Achieve ISO 27001 compliance

---

## 📞 Security Contact

For security issues or questions:
- **Security Team:** security@oobc.gov.ph
- **Emergency:** [On-call phone number]
- **Bug Bounty:** [If applicable]

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Next Review:** July 2025

---

*This document is maintained by the OBCMS Security Team*
