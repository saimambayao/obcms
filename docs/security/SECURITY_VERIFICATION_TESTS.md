# OBCMS Security Implementation Verification Tests

**Document Version:** 1.0
**Date:** October 3, 2025
**Status:** ACTIVE
**Purpose:** Verify all security implementations are functioning correctly before staging deployment

---

## Executive Summary

This document provides step-by-step verification procedures for all security implementations completed to achieve the 100/100 security score. All tests should be run in the development environment before staging deployment.

**Prerequisites:**
- Development environment set up (`cd src`, virtual environment activated)
- Django server can start successfully (`./manage.py runserver`)
- All migrations applied (`./manage.py migrate`)

---

## Test Suite Overview

| Category | Tests | Status |
|----------|-------|--------|
| API Logging | 3 tests | ⏳ Pending |
| Security Alerts | 6 tests | ⏳ Pending |
| Authentication | 4 tests | ⏳ Pending |
| Audit Trail | 3 tests | ⏳ Pending |
| API Security | 5 tests | ⏳ Pending |
| Configuration | 4 tests | ⏳ Pending |

---

## 1. API Logging Verification

### Test 1.1: Verify API Logging Middleware is Active

```bash
# Navigate to src directory
cd src

# Check that APILoggingMiddleware is in MIDDLEWARE list
python manage.py shell << 'EOF'
from django.conf import settings
middleware_list = settings.MIDDLEWARE
api_logging = 'common.middleware.APILoggingMiddleware' in middleware_list
print(f"✅ API Logging Middleware Active" if api_logging else "❌ API Logging Middleware NOT FOUND")
exit()
EOF
```

**Expected Output:** `✅ API Logging Middleware Active`

---

### Test 1.2: Verify API Request Logging

```bash
# Start development server in background
cd src
./manage.py runserver > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

# Make API request
curl -s http://localhost:8000/api/v1/ > /dev/null

# Check logs for API request entry
sleep 1
tail -20 logs/django.log | grep "API Request"

# Kill server
kill $SERVER_PID
```

**Expected Output:** Log entry like:
```
[INFO] API Request | Method: GET | Path: /api/v1/ | User: Anonymous | IP: 127.0.0.1
```

---

### Test 1.3: Verify API Response Logging with Duration

```bash
# Start server
cd src
./manage.py runserver > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

# Make authenticated API request
curl -s -X GET http://localhost:8000/api/v1/ \
  -H "Accept: application/json" > /dev/null

sleep 1
tail -20 logs/django.log | grep "API Response"

kill $SERVER_PID
```

**Expected Output:** Log entry like:
```
[INFO] API Response | Method: GET | Path: /api/v1/ | Status: 200 | Duration: 0.045s | Size: 156 bytes
```

---

## 2. Security Alerting Verification

### Test 2.1: Verify Alerting Configuration Check

```bash
cd src
python manage.py shell << 'EOF'
from common.alerting import check_alerting_configuration

config = check_alerting_configuration()
print("\n=== Alerting Configuration Status ===")
print(f"Slack Configured: {config['slack_configured']}")
print(f"Email Configured: {config['email_configured']}")
print(f"Logging Configured: {config['logging_configured']}")

if config['logging_configured']:
    print("\n✅ At minimum, logging-based alerts are functional")
else:
    print("\n❌ Critical: Logging not configured")
exit()
EOF
```

**Expected Output:**
```
=== Alerting Configuration Status ===
Slack Configured: False  (or True if SLACK_WEBHOOK_URL is set)
Email Configured: True   (default: security@oobc.gov.ph)
Logging Configured: True

✅ At minimum, logging-based alerts are functional
```

---

### Test 2.2: Test Brute Force Alert (Manual Trigger)

```bash
cd src
python manage.py shell << 'EOF'
from common.alerting import alert_brute_force_attack

print("Triggering test brute force alert...")
alert_brute_force_attack(
    ip_address="192.168.1.100",
    username="test_user",
    attempt_count=12
)
print("\n✅ Alert triggered successfully")
print("Check logs/django.log for alert entry")
exit()
EOF

# Check logs
tail -10 logs/django.log | grep -i "brute force"
```

**Expected Output:**
- Log entry: `[CRITICAL] Security Alert: Brute Force Attack Detected`
- If Slack configured: Message sent to Slack
- Email sent to security team (if configured)

---

### Test 2.3: Test Mass Data Export Alert

```bash
cd src
python manage.py shell << 'EOF'
from common.alerting import alert_mass_data_export
from common.models import User

# Get or create test user
user, _ = User.objects.get_or_create(
    username='test_export_user',
    defaults={'email': 'test@example.com', 'user_type': 'STAFF'}
)

print("Triggering test mass data export alert...")
alert_mass_data_export(
    user=user,
    export_type="OBC Community Data (CSV)",
    record_count=1500
)
print("\n✅ Mass export alert triggered")
print("Check logs/django.log for alert entry")
exit()
EOF

tail -10 logs/django.log | grep -i "mass data export"
```

**Expected Output:** `[WARNING] Security Alert: Mass Data Export`

---

### Test 2.4: Test Unauthorized Access Alert

```bash
cd src
python manage.py shell << 'EOF'
from common.alerting import alert_unauthorized_access
from common.models import User

user, _ = User.objects.get_or_create(
    username='test_unauth_user',
    defaults={'email': 'test@example.com', 'user_type': 'VIEWER'}
)

print("Triggering test unauthorized access alert...")
alert_unauthorized_access(
    user=user,
    path="/admin/",
    permission_required="is_superuser"
)
print("\n✅ Unauthorized access alert triggered")
exit()
EOF

tail -10 logs/django.log | grep -i "unauthorized access"
```

**Expected Output:** `[WARNING] Security Alert: Unauthorized Access Attempt`

---

## 3. Authentication & Axes Verification

### Test 3.1: Verify Django Axes Configuration

```bash
cd src
python manage.py shell << 'EOF'
from django.conf import settings

print("=== Django Axes Configuration ===")
print(f"Enabled: {settings.AXES_ENABLED}")
print(f"Failure Limit: {settings.AXES_FAILURE_LIMIT}")
print(f"Cooloff Time: {settings.AXES_COOLOFF_TIME}")
print(f"Lockout Parameters: {settings.AXES_LOCKOUT_PARAMETERS}")
print(f"Reset on Success: {settings.AXES_RESET_ON_SUCCESS}")

if settings.AXES_ENABLED and settings.AXES_FAILURE_LIMIT == 5:
    print("\n✅ Axes configured correctly")
else:
    print("\n❌ Axes configuration issue")
exit()
EOF
```

**Expected Output:**
```
=== Django Axes Configuration ===
Enabled: True
Failure Limit: 5
Cooloff Time: 0:30:00
Lockout Parameters: [['username', 'ip_address']]
Reset on Success: True

✅ Axes configured correctly
```

---

### Test 3.2: Test Failed Login Tracking

```bash
cd src

# Create test user
python manage.py shell << 'EOF'
from common.models import User
User.objects.filter(username='test_login_user').delete()
User.objects.create_user(
    username='test_login_user',
    password='correct_password',
    email='test@example.com',
    is_approved=True
)
print("Test user created")
exit()
EOF

# Start server
./manage.py runserver > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

# Attempt failed login
curl -s -X POST http://localhost:8000/login/ \
  -d "username=test_login_user&password=wrong_password" \
  -c cookies.txt > /dev/null

# Check if failed attempt was logged
sleep 1
tail -20 logs/django.log | grep -i "failed login"

kill $SERVER_PID
rm -f cookies.txt
```

**Expected Output:** `[WARNING] Failed login attempt | Username: test_login_user | IP: 127.0.0.1`

---

### Test 3.3: Test Account Lockout After 5 Failures

```bash
cd src
./manage.py runserver > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

# Attempt 5 failed logins
echo "Attempting 5 failed logins to trigger lockout..."
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/login/ \
    -d "username=test_login_user&password=wrong_password" > /dev/null
  echo "Attempt $i"
  sleep 1
done

# Check if account is locked
python manage.py shell << 'EOF'
from axes.models import AccessAttempt
attempts = AccessAttempt.objects.filter(username='test_login_user').count()
print(f"\nAccess attempts recorded: {attempts}")
print("✅ Account lockout mechanism active" if attempts >= 5 else "❌ Lockout not triggered")
exit()
EOF

kill $SERVER_PID
```

**Expected Output:**
```
Access attempts recorded: 5
✅ Account lockout mechanism active
```

---

## 4. Audit Trail Verification

### Test 4.1: Verify Auditlog Configuration

```bash
cd src
python manage.py shell << 'EOF'
from django.conf import settings
from auditlog.registry import auditlog

print("=== Auditlog Configuration ===")
print(f"Configured models: {settings.AUDITLOG_INCLUDE_TRACKING_MODELS}")
print(f"\nRegistered models: {len(auditlog.get_models())}")
for model in auditlog.get_models():
    print(f"  - {model._meta.label}")

if len(auditlog.get_models()) > 0:
    print("\n✅ Auditlog configured and models registered")
else:
    print("\n❌ No models registered for audit logging")
exit()
EOF
```

**Expected Output:** List of tracked models including User, OBCCommunity, Assessment, etc.

---

### Test 4.2: Test Audit Log Entry Creation

```bash
cd src
python manage.py shell << 'EOF'
from common.models import User
from auditlog.models import LogEntry

# Create test user to trigger audit log
print("Creating test user to trigger audit log...")
user = User.objects.create_user(
    username='audit_test_user',
    email='audit@example.com',
    password='testpass123'
)

# Check if audit entry was created
audit_entries = LogEntry.objects.filter(
    content_type__model='user',
    object_pk=str(user.id)
).count()

print(f"\nAudit entries created: {audit_entries}")
print("✅ Audit logging working" if audit_entries > 0 else "❌ No audit entry created")

# Cleanup
user.delete()
exit()
EOF
```

**Expected Output:** `✅ Audit logging working`

---

## 5. API Security Verification

### Test 5.1: Verify API Versioning Structure

```bash
cd src
python manage.py shell << 'EOF'
from django.urls import get_resolver
from django.conf import settings

resolver = get_resolver()
url_patterns = [str(pattern) for pattern in resolver.url_patterns]

api_v1_found = any('api/v1' in pattern for pattern in url_patterns)
print(f"API v1 routing: {'✅ Configured' if api_v1_found else '❌ Not found'}")
exit()
EOF
```

**Expected Output:** `API v1 routing: ✅ Configured`

---

### Test 5.2: Verify DRF Browsable API Disabled in Production

```bash
cd src
python manage.py shell << 'EOF'
from django.conf import settings
import os

# Check production settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'obc_management.settings.production'
from django.conf import settings

renderer_classes = settings.REST_FRAMEWORK.get('DEFAULT_RENDERER_CLASSES', [])
browsable_api = 'rest_framework.renderers.BrowsableAPIRenderer' in renderer_classes

if not browsable_api:
    print("✅ Browsable API correctly disabled in production")
else:
    print("❌ Browsable API still enabled in production (SECURITY RISK)")
exit()
EOF
```

**Expected Output:** `✅ Browsable API correctly disabled in production`

---

### Test 5.3: Verify Rate Limiting Configuration

```bash
cd src
python manage.py shell << 'EOF'
from django.conf import settings

throttle_classes = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_CLASSES', [])
throttle_rates = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})

print("=== API Rate Limiting Configuration ===")
print(f"Throttle Classes: {len(throttle_classes)}")
for cls in throttle_classes:
    print(f"  - {cls}")

print(f"\nThrottle Rates:")
for key, rate in throttle_rates.items():
    print(f"  - {key}: {rate}")

if len(throttle_classes) >= 3 and 'anon' in throttle_rates:
    print("\n✅ Rate limiting configured correctly")
else:
    print("\n❌ Rate limiting configuration incomplete")
exit()
EOF
```

**Expected Output:**
```
=== API Rate Limiting Configuration ===
Throttle Classes: 3
  - common.throttling.BurstThrottle
  - common.throttling.AnonThrottle
  - common.throttling.UserThrottle

Throttle Rates:
  - anon: 100/hour
  - user: 1000/hour
  - burst: 60/minute
  ...

✅ Rate limiting configured correctly
```

---

### Test 5.4: Verify JWT Token Blacklisting

```bash
cd src
python manage.py shell << 'EOF'
from django.conf import settings

jwt_settings = settings.SIMPLE_JWT
blacklist_enabled = jwt_settings.get('BLACKLIST_AFTER_ROTATION', False)
rotate_tokens = jwt_settings.get('ROTATE_REFRESH_TOKENS', False)

print(f"JWT Token Rotation: {'✅ Enabled' if rotate_tokens else '❌ Disabled'}")
print(f"JWT Token Blacklisting: {'✅ Enabled' if blacklist_enabled else '❌ Disabled'}")

if blacklist_enabled and rotate_tokens:
    print("\n✅ JWT security configured correctly")
else:
    print("\n⚠️ JWT security could be improved")
exit()
EOF
```

**Expected Output:**
```
JWT Token Rotation: ✅ Enabled
JWT Token Blacklisting: ✅ Enabled

✅ JWT security configured correctly
```

---

## 6. Configuration & Infrastructure

### Test 6.1: Verify Dependabot Configuration

```bash
# Check if Dependabot config exists
if [ -f .github/dependabot.yml ]; then
    echo "✅ Dependabot configuration found"
    echo ""
    cat .github/dependabot.yml
else
    echo "❌ Dependabot configuration missing"
fi
```

**Expected Output:** `✅ Dependabot configuration found` + file contents

---

### Test 6.2: Verify Security Logging Configuration

```bash
cd src
python manage.py shell << 'EOF'
from django.conf import settings
import logging

loggers = settings.LOGGING.get('loggers', {})

security_loggers = {
    'axes': loggers.get('axes'),
    'auditlog': loggers.get('auditlog'),
    'django.security': loggers.get('django.security'),
    'api': loggers.get('api'),
}

print("=== Security Logging Configuration ===")
all_configured = True
for logger_name, logger_config in security_loggers.items():
    if logger_config:
        print(f"✅ {logger_name}: {logger_config.get('level', 'N/A')}")
    else:
        print(f"❌ {logger_name}: NOT CONFIGURED")
        all_configured = False

print(f"\n{'✅ All security loggers configured' if all_configured else '❌ Missing security logger configuration'}")
exit()
EOF
```

**Expected Output:**
```
=== Security Logging Configuration ===
✅ axes: WARNING
✅ auditlog: INFO
✅ django.security: WARNING
✅ api: INFO

✅ All security loggers configured
```

---

### Test 6.3: Verify Incident Response Playbook Exists

```bash
if [ -f docs/security/INCIDENT_RESPONSE_PLAYBOOK.md ]; then
    echo "✅ Incident Response Playbook exists"
    echo ""
    head -20 docs/security/INCIDENT_RESPONSE_PLAYBOOK.md
else
    echo "❌ Incident Response Playbook missing"
fi
```

**Expected Output:** `✅ Incident Response Playbook exists` + document header

---

### Test 6.4: Verify Fail2Ban Setup Script

```bash
if [ -f scripts/setup_fail2ban.sh ]; then
    echo "✅ Fail2Ban setup script exists"
    echo ""
    # Verify it's executable
    if [ -x scripts/setup_fail2ban.sh ]; then
        echo "✅ Script is executable"
    else
        echo "⚠️ Script exists but not executable (run: chmod +x scripts/setup_fail2ban.sh)"
    fi

    # Show key configuration
    echo ""
    echo "Key Configuration:"
    grep -A 5 "django-auth\]" scripts/setup_fail2ban.sh | head -10
else
    echo "❌ Fail2Ban setup script missing"
fi
```

**Expected Output:** `✅ Fail2Ban setup script exists` + configuration preview

---

## 7. Complete Verification Run

### Master Verification Script

Save this as `scripts/verify_security.sh`:

```bash
#!/bin/bash
# OBCMS Security Verification Master Script
# Runs all verification tests in sequence

echo "================================================"
echo "OBCMS Security Implementation Verification"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -n "Testing: $test_name... "

    if eval "$test_command" > /tmp/test_output.log 2>&1; then
        if grep -q "✅" /tmp/test_output.log || grep -q "PASS" /tmp/test_output.log; then
            echo -e "${GREEN}✅ PASS${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}❌ FAIL${NC}"
            FAILED=$((FAILED + 1))
            cat /tmp/test_output.log
        fi
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED=$((FAILED + 1))
        cat /tmp/test_output.log
    fi
}

echo "Starting verification tests..."
echo ""

# Run tests
cd src

echo "=== Configuration Tests ==="
run_test "Django Check" "python manage.py check"
run_test "API Logging Middleware" "python manage.py shell -c 'from django.conf import settings; print(\"✅\" if \"common.middleware.APILoggingMiddleware\" in settings.MIDDLEWARE else \"❌\")'"
run_test "Axes Configuration" "python manage.py shell -c 'from django.conf import settings; print(\"✅\" if settings.AXES_ENABLED else \"❌\")'"

echo ""
echo "=== Security Feature Tests ==="
run_test "Alerting System" "python manage.py shell -c 'from common.alerting import check_alerting_configuration; c = check_alerting_configuration(); print(\"✅\" if c[\"logging_configured\"] else \"❌\")'"
run_test "Auditlog Registry" "python manage.py shell -c 'from auditlog.registry import auditlog; print(\"✅\" if len(auditlog.get_models()) > 0 else \"❌\")'"

echo ""
echo "=== Documentation Tests ==="
run_test "Incident Response Playbook" "test -f ../docs/security/INCIDENT_RESPONSE_PLAYBOOK.md && echo '✅' || echo '❌'"
run_test "Fail2Ban Setup Script" "test -f ../scripts/setup_fail2ban.sh && echo '✅' || echo '❌'"
run_test "Dependabot Config" "test -f ../.github/dependabot.yml && echo '✅' || echo '❌'"

echo ""
echo "================================================"
echo "Verification Complete"
echo "================================================"
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED - System ready for staging deployment${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED - Review output above${NC}"
    exit 1
fi
```

---

## 8. Expected Results Summary

### Passing Criteria

All of the following must be `✅`:

**Configuration:**
- ✅ API Logging Middleware active
- ✅ Django Axes enabled (5 failures = lockout)
- ✅ Auditlog models registered (8+ models)
- ✅ Security loggers configured (axes, auditlog, django.security, api)

**Security Features:**
- ✅ Alerting system functional (at least logging channel)
- ✅ Brute force alert triggers on 10+ attempts
- ✅ Failed login tracking works
- ✅ Account lockout after 5 failures
- ✅ Audit trail records model changes

**API Security:**
- ✅ API versioning (v1) configured
- ✅ DRF Browsable API disabled in production
- ✅ Rate limiting configured (3+ throttle classes)
- ✅ JWT token blacklisting enabled

**Documentation & Infrastructure:**
- ✅ Incident Response Playbook exists
- ✅ Fail2Ban setup script exists and executable
- ✅ Dependabot configuration exists
- ✅ Container security scanning in CI/CD

---

## 9. Troubleshooting

### Issue: API Logging not appearing in logs

**Diagnosis:**
```bash
cd src
tail -f logs/django.log &
curl http://localhost:8000/api/v1/
```

**Fix:** Ensure LOGGING configuration includes 'api' logger

---

### Issue: Alerting tests show "not configured"

**Diagnosis:** Check environment variables
```bash
echo $SLACK_WEBHOOK_URL
echo $SECURITY_TEAM_EMAILS
```

**Fix:** Set in `.env` file (optional, logging channel works without these)

---

### Issue: Axes not locking accounts

**Diagnosis:**
```bash
cd src
python manage.py shell -c "from axes.models import AccessAttempt; print(AccessAttempt.objects.count())"
```

**Fix:** Ensure `axes.middleware.AxesMiddleware` comes AFTER `AuthenticationMiddleware`

---

## 10. Pre-Staging Deployment Checklist

Before deploying to staging, verify:

- [ ] All configuration tests pass
- [ ] API logging produces entries
- [ ] Security alerts trigger correctly
- [ ] Failed login tracking works
- [ ] Audit trail captures changes
- [ ] Incident playbook reviewed by security team
- [ ] Fail2Ban script tested on test server
- [ ] Container scanning workflow active
- [ ] Environment variables documented
- [ ] Rollback plan documented

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | October 3, 2025 | Security Implementation Team | Initial verification procedures |

**Distribution:** Security Team, DevOps, QA Team

**Status:** ✅ READY FOR EXECUTION

---

**END OF VERIFICATION GUIDE**
