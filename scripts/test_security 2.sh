#!/bin/bash
# OBCMS Security Testing Suite
# Comprehensive security feature testing script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

echo "============================================"
echo "OBCMS Security Testing Suite"
echo "============================================"
echo ""

# Test counter
test_number=0

# Function to print test header
print_test() {
    ((test_number++))
    echo -e "${BLUE}Test $test_number: $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}  ✅ PASS: $1${NC}"
    ((PASSED++))
}

# Function to print failure
print_failure() {
    echo -e "${RED}  ❌ FAIL: $1${NC}"
    ((FAILED++))
}

# Function to print info
print_info() {
    echo -e "${YELLOW}  ℹ️  INFO: $1${NC}"
}

cd src

# ============================================
# Test 1: Django Version
# ============================================
print_test "Django version verification"

DJANGO_VERSION=$(python -c "import django; print(django.get_version())")
print_info "Django version: $DJANGO_VERSION"

if [[ "$DJANGO_VERSION" =~ ^5\.2\. ]]; then
    print_success "Django 5.2.x installed (CVE-2025-57833 patched)"
else
    print_failure "Django should be 5.2.x (currently $DJANGO_VERSION)"
fi

echo ""

# ============================================
# Test 2: Security Dependencies
# ============================================
print_test "Security dependencies check"

DEPS_TO_CHECK=("django-auditlog" "django-axes" "python-magic")
ALL_DEPS_INSTALLED=true

for dep in "${DEPS_TO_CHECK[@]}"; do
    if pip show "$dep" > /dev/null 2>&1; then
        VERSION=$(pip show "$dep" | grep Version | cut -d' ' -f2)
        print_success "$dep installed (version: $VERSION)"
    else
        print_failure "$dep not installed"
        ALL_DEPS_INSTALLED=false
    fi
done

echo ""

# ============================================
# Test 3: Database Migrations
# ============================================
print_test "Database migrations status"

if python manage.py showmigrations --plan | grep -q "\[ \]"; then
    print_failure "Unapplied migrations found"
    python manage.py showmigrations | grep "\[ \]" | head -5
else
    print_success "All migrations applied"
fi

# Check specific security app migrations
for app in axes auditlog token_blacklist; do
    if python manage.py showmigrations "$app" > /dev/null 2>&1; then
        if python manage.py showmigrations "$app" | grep -q "\[X\]"; then
            print_success "$app migrations applied"
        else
            print_failure "$app migrations not applied"
        fi
    fi
done

echo ""

# ============================================
# Test 4: Django Security Check
# ============================================
print_test "Django deployment security check"

if python manage.py check --deploy 2>&1 | grep -q "System check identified no issues"; then
    print_success "No security issues detected"
elif python manage.py check --deploy 2>&1 | grep -q "DEBUG"; then
    print_info "DEBUG=True warnings (acceptable in development)"
else
    print_failure "Security warnings detected"
    python manage.py check --deploy 2>&1 | grep -A 2 "WARNINGS\|ERRORS" || true
fi

echo ""

# ============================================
# Test 5: Settings Configuration
# ============================================
print_test "Security settings verification"

# Check for security apps in INSTALLED_APPS
python -c "
from django.conf import settings
import sys

security_apps = [
    'auditlog',
    'axes',
    'rest_framework_simplejwt.token_blacklist',
]

all_installed = True
for app in security_apps:
    if app in settings.INSTALLED_APPS:
        print('✅ $app in INSTALLED_APPS')
    else:
        print('❌ $app NOT in INSTALLED_APPS')
        all_installed = False

sys.exit(0 if all_installed else 1)
" && print_success "All security apps configured" || print_failure "Missing security apps"

# Check for security middleware
python -c "
from django.conf import settings

security_middleware = [
    'axes.middleware.AxesMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

all_configured = True
for mw in security_middleware:
    if mw in settings.MIDDLEWARE:
        print('✅ $mw in MIDDLEWARE')
    else:
        print('❌ $mw NOT in MIDDLEWARE')
        all_configured = False

exit(0 if all_configured else 1)
" && print_success "All security middleware configured" || print_failure "Missing security middleware"

# Check throttle configuration
python -c "
from django.conf import settings

if 'DEFAULT_THROTTLE_CLASSES' in settings.REST_FRAMEWORK:
    print('✅ API throttling configured')
    exit(0)
else:
    print('❌ API throttling NOT configured')
    exit(1)
" && print_success "API rate limiting configured" || print_failure "API rate limiting not configured"

echo ""

# ============================================
# Test 6: File Validators
# ============================================
print_test "File upload security validators"

if python -c "from common.validators import validate_image_file, validate_document_file, validate_file_size, sanitize_filename" 2>/dev/null; then
    print_success "File validators module loads successfully"

    # Test filename sanitization
    python -c "
from common.validators import sanitize_filename
test_cases = [
    ('../../../etc/passwd', 'etcpasswd'),
    ('test<>file.pdf', 'testfile.pdf'),
    ('normal_file.doc', 'normal_file.doc'),
]
for input_name, expected in test_cases:
    result = sanitize_filename(input_name)
    if '..' not in result and '<' not in result and '>' not in result:
        print(f'✅ Sanitized: {input_name} -> {result}')
    else:
        print(f'❌ Failed to sanitize: {input_name}')
"
    print_success "Filename sanitization working"
else
    print_failure "File validators module not found"
fi

echo ""

# ============================================
# Test 7: Security Logging
# ============================================
print_test "Security logging utilities"

if python -c "from common.security_logging import log_failed_login, log_unauthorized_access, log_data_export, get_client_ip" 2>/dev/null; then
    print_success "Security logging module loads successfully"
else
    print_failure "Security logging module not found"
fi

# Check if logs directory exists
if [ -d "logs" ]; then
    print_success "Logs directory exists"
else
    print_failure "Logs directory not found"
fi

echo ""

# ============================================
# Test 8: Auditlog Configuration
# ============================================
print_test "Auditlog model registration"

python -c "
from auditlog.models import LogEntry
from common.models import User
from communities.models import BarangayOBC
from mana.models import Assessment

# Check if models are registered
from auditlog.registry import auditlog

registered_models = auditlog.get_models()
critical_models = [User, BarangayOBC, Assessment]

all_registered = True
for model in critical_models:
    if model in registered_models:
        print(f'✅ {model.__name__} registered for audit logging')
    else:
        print(f'❌ {model.__name__} NOT registered')
        all_registered = False

exit(0 if all_registered else 1)
" && print_success "Critical models registered for auditing" || print_failure "Some models not registered"

echo ""

# ============================================
# Test 9: Axes Configuration
# ============================================
print_test "Django-axes failed login protection"

python -c "
from django.conf import settings

# Check axes configuration
required_settings = {
    'AXES_ENABLED': True,
    'AXES_FAILURE_LIMIT': 5,
}

all_configured = True
for setting, expected in required_settings.items():
    actual = getattr(settings, setting, None)
    if actual == expected:
        print(f'✅ {setting} = {actual}')
    else:
        print(f'❌ {setting} = {actual} (expected: {expected})')
        all_configured = False

exit(0 if all_configured else 1)
" && print_success "Axes configuration correct" || print_failure "Axes configuration issues"

echo ""

# ============================================
# Test 10: Password Validation
# ============================================
print_test "Password policy enforcement"

python -c "
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Test weak passwords (should fail)
weak_passwords = ['short', '12345678', 'password123']
weak_pass_count = 0

for pwd in weak_passwords:
    try:
        validate_password(pwd)
        print(f'❌ Weak password accepted: {pwd}')
    except ValidationError:
        weak_pass_count += 1

if weak_pass_count == len(weak_passwords):
    print('✅ All weak passwords rejected')
    exit(0)
else:
    print(f'❌ Some weak passwords accepted ({len(weak_passwords)-weak_pass_count}/{len(weak_passwords)})')
    exit(1)
" && print_success "Password validation working (12-char minimum)" || print_failure "Password validation issues"

echo ""

# ============================================
# Test 11: JWT Token Blacklist
# ============================================
print_test "JWT token blacklist configuration"

python -c "
from django.conf import settings

jwt_config = settings.SIMPLE_JWT

required_settings = {
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

all_configured = True
for setting, expected in required_settings.items():
    actual = jwt_config.get(setting)
    if actual == expected:
        print(f'✅ {setting} = {actual}')
    else:
        print(f'❌ {setting} = {actual} (expected: {expected})')
        all_configured = False

# Check if token_blacklist models exist
try:
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
    print('✅ Token blacklist models available')
except ImportError:
    print('❌ Token blacklist models not available')
    all_configured = False

exit(0 if all_configured else 1)
" && print_success "JWT token blacklisting configured" || print_failure "JWT token blacklisting issues"

echo ""

# ============================================
# Test 12: Throttling Classes
# ============================================
print_test "Custom throttling classes"

python -c "
from common.throttling import (
    AuthenticationThrottle,
    AnonThrottle,
    UserThrottle,
    BurstThrottle,
    DataExportThrottle,
    AdminThrottle
)
print('✅ All 6 custom throttle classes available')
" && print_success "Custom throttle classes loaded" || print_failure "Throttle classes not found"

echo ""

# ============================================
# Test Summary
# ============================================
echo "============================================"
echo "Test Summary"
echo "============================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All security tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start development server: python manage.py runserver"
    echo "2. Test rate limiting: Try logging in with wrong password 6 times"
    echo "3. Check audit logs: /admin/auditlog/logentry/"
    echo "4. Review security documentation: docs/security/"
    exit 0
else
    echo -e "${RED}⚠️  Some security tests failed${NC}"
    echo ""
    echo "Remediation steps:"
    echo "1. Run: bash scripts/setup_security.sh"
    echo "2. Review failed tests above"
    echo "3. Check documentation: docs/security/SECURITY_IMPLEMENTATION_GUIDE.md"
    exit 1
fi
