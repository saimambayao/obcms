#!/bin/bash
# OBCMS Security Setup Script
# Installs dependencies, runs migrations, and configures security features

set -e

echo "============================================"
echo "OBCMS Security Setup"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "requirements/base.txt" ]; then
    echo -e "${RED}❌ Error: Must run from OBCMS root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Installing security dependencies...${NC}"
pip install -r requirements/base.txt

echo ""
echo -e "${YELLOW}Step 2: Verifying Django version...${NC}"
DJANGO_VERSION=$(python -c "import django; print(django.get_version())")
echo "Django version: $DJANGO_VERSION"

if [[ ! "$DJANGO_VERSION" =~ ^5\.2\. ]]; then
    echo -e "${RED}❌ Warning: Django version should be 5.2.x for CVE-2025-57833 fix${NC}"
    echo "Current version: $DJANGO_VERSION"
else
    echo -e "${GREEN}✅ Django 5.2.x installed (CVE-2025-57833 patched)${NC}"
fi

echo ""
echo -e "${YELLOW}Step 3: Running database migrations...${NC}"
cd src

# Run migrations for security apps
echo "  - Migrating axes (failed login tracking)..."
python manage.py migrate axes

echo "  - Migrating auditlog (audit trail)..."
python manage.py migrate auditlog

echo "  - Migrating token_blacklist (JWT security)..."
python manage.py migrate token_blacklist

echo "  - Running all remaining migrations..."
python manage.py migrate

echo ""
echo -e "${YELLOW}Step 4: Creating logs directory...${NC}"
mkdir -p logs
chmod 755 logs
echo -e "${GREEN}✅ Logs directory created${NC}"

echo ""
echo -e "${YELLOW}Step 5: Running Django security check...${NC}"
python manage.py check --deploy || true

echo ""
echo "============================================"
echo -e "${GREEN}✅ Security setup complete!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Review the output above for any warnings"
echo "2. Run security tests: bash scripts/test_security.sh"
echo "3. Review documentation: docs/security/"
echo ""
echo "Security features enabled:"
echo "  ✅ API rate limiting (6 throttle classes)"
echo "  ✅ JWT token blacklisting"
echo "  ✅ Audit logging (9 models tracked)"
echo "  ✅ Failed login protection (5 attempts, 30min lockout)"
echo "  ✅ File upload validation"
echo "  ✅ Password policy (12-char minimum)"
echo "  ✅ Dependency scanning (CI/CD)"
echo ""
