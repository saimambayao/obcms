#!/bin/bash
# Django 5.2 Compatibility Audit Script
# Checks OBCMS codebase for potential compatibility issues

set -e

echo "========================================"
echo "Django 5.2 Compatibility Audit"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$BASE_DIR/src"

# Check counter
ISSUES_FOUND=0

echo "Scanning directory: $SRC_DIR"
echo ""

# 1. Check for pytz usage (deprecated in Django 5.0)
echo "1. Checking for pytz usage (deprecated)..."
PYTZ_COUNT=$(grep -r "import pytz\|from pytz" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYTZ_COUNT" -gt 0 ]; then
    echo -e "${RED}   ✗ Found $PYTZ_COUNT file(s) using pytz${NC}"
    grep -rn "import pytz\|from pytz" "$SRC_DIR" --include="*.py" 2>/dev/null | head -5
    ISSUES_FOUND=$((ISSUES_FOUND + PYTZ_COUNT))
else
    echo -e "${GREEN}   ✓ No pytz usage found${NC}"
fi
echo ""

# 2. Check for USE_L10N setting (removed in Django 5.0)
echo "2. Checking for USE_L10N setting (removed)..."
USE_L10N_COUNT=$(grep -r "USE_L10N" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$USE_L10N_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $USE_L10N_COUNT reference(s) to USE_L10N${NC}"
    grep -rn "USE_L10N" "$SRC_DIR" --include="*.py" 2>/dev/null
    echo -e "${YELLOW}   → Action: Remove these lines (always enabled in Django 5.0+)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + USE_L10N_COUNT))
else
    echo -e "${GREEN}   ✓ No USE_L10N references found${NC}"
fi
echo ""

# 3. Check for Model.save() positional arguments (deprecated)
echo "3. Checking for Model.save() positional arguments..."
SAVE_POSITIONAL=$(grep -r "\.save([^)]*force_insert[^=]" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$SAVE_POSITIONAL" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $SAVE_POSITIONAL potential positional argument(s) in save()${NC}"
    grep -rn "\.save([^)]*force_insert[^=]" "$SRC_DIR" --include="*.py" 2>/dev/null | head -5
    echo -e "${YELLOW}   → Action: Convert to keyword arguments${NC}"
else
    echo -e "${GREEN}   ✓ No positional arguments in save() found${NC}"
fi
echo ""

# 4. Check for old form rendering methods (as_table, as_p, as_ul)
echo "4. Checking for deprecated form rendering methods..."
FORM_RENDER_COUNT=$(grep -r "\.as_table\|\.as_p\|\.as_ul" "$SRC_DIR/templates" 2>/dev/null | wc -l | tr -d ' ')
if [ "$FORM_RENDER_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $FORM_RENDER_COUNT usage(s) of deprecated form rendering${NC}"
    grep -rn "\.as_table\|\.as_p\|\.as_ul" "$SRC_DIR/templates" 2>/dev/null | head -5
    echo -e "${YELLOW}   → Action: Consider using div-based rendering or custom templates${NC}"
else
    echo -e "${GREEN}   ✓ No deprecated form rendering found${NC}"
fi
echo ""

# 5. Check for email alternatives direct assignment
echo "5. Checking for email alternatives direct assignment..."
EMAIL_ALT_COUNT=$(grep -r "\.alternatives\s*=" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$EMAIL_ALT_COUNT" -gt 0 ]; then
    echo -e "${RED}   ✗ Found $EMAIL_ALT_COUNT direct assignment(s) to .alternatives${NC}"
    grep -rn "\.alternatives\s*=" "$SRC_DIR" --include="*.py" 2>/dev/null
    echo -e "${RED}   → Action: Use attach_alternative() method instead${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + EMAIL_ALT_COUNT))
else
    echo -e "${GREEN}   ✓ No direct alternatives assignments found${NC}"
fi
echo ""

# 6. Check for log_deletion usage (deprecated)
echo "6. Checking for log_deletion usage..."
LOG_DELETION_COUNT=$(grep -r "log_deletion" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$LOG_DELETION_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $LOG_DELETION_COUNT reference(s) to log_deletion${NC}"
    grep -rn "log_deletion" "$SRC_DIR" --include="*.py" 2>/dev/null
    echo -e "${YELLOW}   → Action: Use signals instead${NC}"
else
    echo -e "${GREEN}   ✓ No log_deletion usage found${NC}"
fi
echo ""

# 7. Check for index_together in models (deprecated)
echo "7. Checking for index_together usage..."
INDEX_TOGETHER_COUNT=$(grep -r "index_together" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$INDEX_TOGETHER_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $INDEX_TOGETHER_COUNT reference(s) to index_together${NC}"
    grep -rn "index_together" "$SRC_DIR" --include="*.py" 2>/dev/null
    echo -e "${YELLOW}   → Action: Use indexes = [models.Index(...)] instead${NC}"
else
    echo -e "${GREEN}   ✓ No index_together usage found${NC}"
fi
echo ""

# 8. Check for is_dst parameter usage (removed)
echo "8. Checking for is_dst parameter usage..."
IS_DST_COUNT=$(grep -r "is_dst\s*=" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$IS_DST_COUNT" -gt 0 ]; then
    echo -e "${RED}   ✗ Found $IS_DST_COUNT usage(s) of is_dst parameter${NC}"
    grep -rn "is_dst\s*=" "$SRC_DIR" --include="*.py" 2>/dev/null
    echo -e "${RED}   → Action: Remove is_dst parameter${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + IS_DST_COUNT))
else
    echo -e "${GREEN}   ✓ No is_dst parameter found${NC}"
fi
echo ""

# 9. Check USE_TZ setting
echo "9. Checking USE_TZ setting..."
USE_TZ_FALSE=$(grep -r "USE_TZ\s*=\s*False" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$USE_TZ_FALSE" -gt 0 ]; then
    echo -e "${RED}   ✗ Found USE_TZ = False (Django 5.0+ default is True)${NC}"
    grep -rn "USE_TZ\s*=\s*False" "$SRC_DIR" --include="*.py" 2>/dev/null
    echo -e "${RED}   → Action: Change to USE_TZ = True${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + USE_TZ_FALSE))
else
    echo -e "${GREEN}   ✓ USE_TZ correctly configured${NC}"
fi
echo ""

# 10. Check for BaseUserManager.make_random_password() (removed)
echo "10. Checking for make_random_password usage..."
RANDOM_PWD_COUNT=$(grep -r "make_random_password" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$RANDOM_PWD_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $RANDOM_PWD_COUNT reference(s) to make_random_password${NC}"
    grep -rn "make_random_password" "$SRC_DIR" --include="*.py" 2>/dev/null
    echo -e "${YELLOW}   → Action: Use get_random_string() instead${NC}"
else
    echo -e "${GREEN}   ✓ No make_random_password usage found${NC}"
fi
echo ""

# Summary
echo "========================================"
echo "Audit Summary"
echo "========================================"
echo ""

if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo -e "${GREEN}✓ No critical compatibility issues found!${NC}"
    echo ""
    echo "Your codebase appears ready for Django 5.2 migration."
    echo "Proceed with dependency updates and testing."
else
    echo -e "${YELLOW}⚠ Found $ISSUES_FOUND potential issue(s)${NC}"
    echo ""
    echo "Review the findings above and make necessary adjustments."
    echo "Most issues are deprecation warnings and can be addressed gradually."
fi

echo ""
echo "Next Steps:"
echo "1. Review findings above"
echo "2. Address any critical issues (marked with ✗)"
echo "3. Update dependencies: pip install Django==5.2.7"
echo "4. Run test suite: pytest -v"
echo "5. Consult: docs/deployment/DJANGO_5_2_MIGRATION_ANALYSIS.md"
echo ""

exit 0
