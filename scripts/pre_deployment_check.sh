#!/usr/bin/env bash
#
# Pre-Deployment Automated Checklist for OBCMS
#
# This script automates critical pre-deployment checks before deploying
# to staging or production environments.
#
# Usage:
#   ./scripts/pre_deployment_check.sh [--env-file .env.staging]
#
# Exit codes:
#   0 - All checks passed
#   1 - Critical checks failed
#

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Parse arguments
ENV_FILE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--env-file .env.staging]"
            exit 1
            ;;
    esac
done

# Load environment file if provided
if [ -n "$ENV_FILE" ]; then
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}Error: Environment file not found: $ENV_FILE${NC}"
        exit 1
    fi
    echo -e "${BLUE}Loading environment from: $ENV_FILE${NC}"
    set -a
    source "$ENV_FILE"
    set +a
    echo ""
fi

echo -e "${BOLD}================================================${NC}"
echo -e "${BOLD}OBCMS Pre-Deployment Automated Checklist${NC}"
echo -e "${BOLD}================================================${NC}"
echo ""

# Function to print check result
check_result() {
    local status=$1
    local message=$2
    local severity=${3:-"error"}  # error, warning, info

    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $message"
        ((PASSED++))
    elif [ "$status" = "fail" ]; then
        if [ "$severity" = "warning" ]; then
            echo -e "${YELLOW}⚠${NC} $message"
            ((WARNINGS++))
        else
            echo -e "${RED}✗${NC} $message"
            ((FAILED++))
        fi
    fi
}

# ============================================================================
# 1. ENVIRONMENT VALIDATION
# ============================================================================

echo -e "${BOLD}1. Environment Variable Validation${NC}"
echo "---------------------------------------------------"

# Check if Python validation script exists and run it
if [ -f "scripts/validate_env.py" ]; then
    if [ -n "$ENV_FILE" ]; then
        python scripts/validate_env.py --env-file "$ENV_FILE" --quiet
        ENV_CHECK_EXIT=$?
    else
        python scripts/validate_env.py --quiet
        ENV_CHECK_EXIT=$?
    fi

    if [ $ENV_CHECK_EXIT -eq 0 ]; then
        check_result "pass" "Environment variables validated"
    elif [ $ENV_CHECK_EXIT -eq 2 ]; then
        check_result "fail" "Environment validation passed with warnings" "warning"
    else
        check_result "fail" "Environment validation failed"
    fi
else
    check_result "fail" "Environment validation script not found" "warning"
fi

echo ""

# ============================================================================
# 2. DJANGO DEPLOYMENT CHECKS
# ============================================================================

echo -e "${BOLD}2. Django Deployment Security Checks${NC}"
echo "---------------------------------------------------"

if [ -f "scripts/run_deployment_check.py" ]; then
    if python scripts/run_deployment_check.py > /dev/null 2>&1; then
        check_result "pass" "Django deployment checks passed (--deploy)"
    else
        check_result "fail" "Django deployment checks failed"
    fi
else
    check_result "fail" "Deployment check script not found" "warning"
fi

echo ""

# ============================================================================
# 3. STATIC FILES
# ============================================================================

echo -e "${BOLD}3. Static Files Collection${NC}"
echo "---------------------------------------------------"

cd src 2>/dev/null || { check_result "fail" "src/ directory not found"; exit 1; }

if python manage.py collectstatic --noinput --dry-run > /dev/null 2>&1; then
    check_result "pass" "Static files collection test passed"
else
    check_result "fail" "Static files collection failed"
fi

cd ..

echo ""

# ============================================================================
# 4. DATABASE MIGRATIONS
# ============================================================================

echo -e "${BOLD}4. Database Migrations${NC}"
echo "---------------------------------------------------"

cd src

# Check for unapplied migrations
UNAPPLIED=$(python manage.py showmigrations --plan | grep "\[ \]" | wc -l | tr -d ' ')

if [ "$UNAPPLIED" -eq 0 ]; then
    check_result "pass" "All migrations applied"
else
    check_result "fail" "$UNAPPLIED unapplied migrations found" "warning"
fi

# Check for migration conflicts
if python manage.py makemigrations --check --dry-run > /dev/null 2>&1; then
    check_result "pass" "No migration conflicts detected"
else
    check_result "fail" "Migration conflicts detected"
fi

cd ..

echo ""

# ============================================================================
# 5. TESTING
# ============================================================================

echo -e "${BOLD}5. Test Suite Status${NC}"
echo "---------------------------------------------------"

# Run critical smoke tests only (fast)
cd src

if pytest -m smoke --tb=no -q > /dev/null 2>&1; then
    check_result "pass" "Smoke tests passed"
else
    check_result "fail" "Smoke tests failed" "warning"
fi

cd ..

echo ""

# ============================================================================
# 6. SECURITY
# ============================================================================

echo -e "${BOLD}6. Security Checks${NC}"
echo "---------------------------------------------------"

# Check for common security issues
if grep -r "SECRET_KEY.*=.*'django-insecure" src/ 2>/dev/null; then
    check_result "fail" "Insecure SECRET_KEY found in code"
else
    check_result "pass" "No hardcoded insecure SECRET_KEY"
fi

if grep -r "DEBUG.*=.*True" src/obc_management/settings/production.py 2>/dev/null; then
    check_result "fail" "DEBUG=True in production settings"
else
    check_result "pass" "DEBUG properly set in production"
fi

if [ -f ".env" ]; then
    if git check-ignore .env > /dev/null 2>&1; then
        check_result "pass" ".env file is gitignored"
    else
        check_result "fail" ".env file is NOT gitignored - security risk!"
    fi
fi

echo ""

# ============================================================================
# 7. DEPENDENCIES
# ============================================================================

echo -e "${BOLD}7. Dependency Checks${NC}"
echo "---------------------------------------------------"

# Check for known vulnerabilities
if command -v safety &> /dev/null; then
    if safety check --json > /dev/null 2>&1; then
        check_result "pass" "No known vulnerabilities in dependencies"
    else
        check_result "fail" "Vulnerabilities found in dependencies" "warning"
    fi
else
    check_result "fail" "safety command not found (install: pip install safety)" "warning"
fi

echo ""

# ============================================================================
# 8. DOCKER
# ============================================================================

echo -e "${BOLD}8. Docker Configuration${NC}"
echo "---------------------------------------------------"

if [ -f "Dockerfile" ]; then
    check_result "pass" "Dockerfile exists"

    # Check for production target
    if grep -q "FROM.*production" Dockerfile; then
        check_result "pass" "Production Docker target defined"
    else
        check_result "fail" "Production Docker target not found" "warning"
    fi
else
    check_result "fail" "Dockerfile not found"
fi

if [ -f "docker-compose.prod.yml" ]; then
    check_result "pass" "Production Docker Compose file exists"
else
    check_result "fail" "docker-compose.prod.yml not found" "warning"
fi

echo ""

# ============================================================================
# 9. DOCUMENTATION
# ============================================================================

echo -e "${BOLD}9. Documentation${NC}"
echo "---------------------------------------------------"

REQUIRED_DOCS=(
    "docs/deployment/production-deployment-issues-resolution.md"
    "docs/env/staging-complete.md"
    "docs/testing/staging_rehearsal_checklist.md"
    ".env.example"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        check_result "pass" "$(basename $doc) exists"
    else
        check_result "fail" "$doc not found" "warning"
    fi
done

echo ""

# ============================================================================
# 10. GIT STATUS
# ============================================================================

echo -e "${BOLD}10. Git Repository Status${NC}"
echo "---------------------------------------------------"

if git rev-parse --git-dir > /dev/null 2>&1; then
    # Check for uncommitted changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        check_result "pass" "No uncommitted changes"
    else
        check_result "fail" "Uncommitted changes detected" "warning"
    fi

    # Check current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
        check_result "pass" "On main branch ($BRANCH)"
    else
        check_result "fail" "Not on main branch (current: $BRANCH)" "warning"
    fi
else
    check_result "fail" "Not a git repository" "warning"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${BOLD}================================================${NC}"
echo -e "${BOLD}Pre-Deployment Check Summary${NC}"
echo -e "${BOLD}================================================${NC}"
echo ""

echo -e "${GREEN}✓ Passed:${NC} $PASSED checks"
echo -e "${YELLOW}⚠ Warnings:${NC} $WARNINGS checks"
echo -e "${RED}✗ Failed:${NC} $FAILED checks"
echo ""

if [ $FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ ALL CHECKS PASSED${NC}"
    echo -e "${GREEN}System is ready for deployment!${NC}"
    exit 0
elif [ $FAILED -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}⚠ PASSED WITH WARNINGS${NC}"
    echo -e "${YELLOW}Review warnings before deployment${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}✗ CHECKS FAILED${NC}"
    echo -e "${RED}Fix critical issues before deployment!${NC}"
    exit 1
fi
