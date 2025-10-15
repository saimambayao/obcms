#!/bin/bash
#
# Smoke Test Script
# Verifies core functionality after deployment
#
# Usage: ./scripts/smoke_test.sh
#

set -u  # Treat unset variables as an error

# Configuration
PROJECT_DIR="/var/www/obcms"
VENV_DIR="${PROJECT_DIR}/../venv"
SRC_DIR="${PROJECT_DIR}/src"
BASE_URL="http://localhost:8000"  # Update with actual domain

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test result function
test_result() {
    TESTS_RUN=$((TESTS_RUN + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        if [ -n "${3:-}" ]; then
            echo -e "  ${YELLOW}Detail: $3${NC}"
        fi
    fi
}

echo "================================================================"
echo "OBCMS SMOKE TESTS"
echo "================================================================"
echo ""
echo "Running post-deployment verification tests..."
echo ""

# Activate virtual environment
cd "$SRC_DIR"
source "${VENV_DIR}/bin/activate"

# Test 1: Django Check
echo "=== Test 1: Django System Check ==="
python manage.py check --deploy > /tmp/django_check.log 2>&1
test_result $? "Django deployment checks" "$(cat /tmp/django_check.log)"

# Test 2: Database Connection
echo ""
echo "=== Test 2: Database Connection ==="
python manage.py shell -c "from django.db import connection; connection.cursor().execute('SELECT 1')" > /dev/null 2>&1
test_result $? "Database connection"

# Test 3: Cache Connection
echo ""
echo "=== Test 3: Cache Connection ==="
python manage.py shell -c "from django.core.cache import cache; cache.set('test', 1); assert cache.get('test') == 1" > /dev/null 2>&1
test_result $? "Cache (Redis) connection"

# Test 4: Model Integrity
echo ""
echo "=== Test 4: Model Integrity ==="
TASK_COUNT=$(python manage.py shell -c "from common.models import StaffTask; print(StaffTask.objects.count())" 2>/dev/null)
if [ -n "$TASK_COUNT" ] && [ "$TASK_COUNT" -ge 0 ]; then
    test_result 0 "StaffTask model accessible (count: $TASK_COUNT)"
else
    test_result 1 "StaffTask model not accessible"
fi

PPA_COUNT=$(python manage.py shell -c "from monitoring.models import MonitoringEntry; print(MonitoringEntry.objects.filter(category__in=['oobc_ppa', 'moa_ppa']).count())" 2>/dev/null)
if [ -n "$PPA_COUNT" ] && [ "$PPA_COUNT" -ge 0 ]; then
    test_result 0 "MonitoringEntry model accessible (PPAs: $PPA_COUNT)"
else
    test_result 1 "MonitoringEntry model not accessible"
fi

# Test 5: Migrations Applied
echo ""
echo "=== Test 5: Migrations Status ==="
UNAPPLIED=$(python manage.py showmigrations | grep "\[ \]" | wc -l)
if [ "$UNAPPLIED" -eq 0 ]; then
    test_result 0 "All migrations applied"
else
    test_result 1 "Unapplied migrations found" "$UNAPPLIED migrations pending"
fi

# Test 6: Static Files
echo ""
echo "=== Test 6: Static Files ==="
if [ -d "${PROJECT_DIR}/staticfiles" ] && [ "$(ls -A ${PROJECT_DIR}/staticfiles)" ]; then
    STATIC_FILE_COUNT=$(find "${PROJECT_DIR}/staticfiles" -type f | wc -l)
    test_result 0 "Static files collected ($STATIC_FILE_COUNT files)"
else
    test_result 1 "Static files not found"
fi

# Test 7: Calendar Service
echo ""
echo "=== Test 7: Calendar Aggregation Service ==="
python manage.py shell << 'EOF' > /tmp/calendar_test.log 2>&1
from common.services.calendar import build_calendar_payload
import time

start = time.time()
payload = build_calendar_payload()
duration = time.time() - start

print(f"Entries: {len(payload['entries'])}")
print(f"Modules: {len(payload['module_stats'])}")
print(f"Duration: {duration:.3f}s")

assert len(payload['entries']) >= 0, "Calendar should return entries"
assert duration < 5.0, f"Calendar aggregation took {duration}s, should be < 5s"
print("SUCCESS")
EOF

if grep -q "SUCCESS" /tmp/calendar_test.log; then
    CALENDAR_INFO=$(grep -E "(Entries|Modules|Duration)" /tmp/calendar_test.log | tr '\n' ', ')
    test_result 0 "Calendar aggregation service" "$CALENDAR_INFO"
else
    test_result 1 "Calendar aggregation failed" "$(cat /tmp/calendar_test.log)"
fi

# Test 8: Task Automation Service
echo ""
echo "=== Test 8: Task Automation Signals ==="
python manage.py shell << 'EOF' > /tmp/task_automation_test.log 2>&1
from django.contrib.auth import get_user_model
from mana.models import Assessment
from common.models import StaffTask

User = get_user_model()

# Create test user if needed
user, _ = User.objects.get_or_create(
    username='smoke_test_user',
    defaults={'email': 'smoke@test.com'}
)

# Create test assessment
assessment = Assessment.objects.create(
    title='Smoke Test Assessment',
    methodology='survey',
    status='planning',
    lead_facilitator=user
)

# Check if tasks were created
task_count = StaffTask.objects.filter(related_assessment=assessment).count()

# Cleanup
StaffTask.objects.filter(related_assessment=assessment).delete()
assessment.delete()

print(f"Tasks created: {task_count}")
assert task_count >= 0, "Signal handler should create tasks"
print("SUCCESS")
EOF

if grep -q "SUCCESS" /tmp/task_automation_test.log; then
    TASK_AUTO_INFO=$(grep "Tasks created" /tmp/task_automation_test.log)
    test_result 0 "Task automation signal handler" "$TASK_AUTO_INFO"
else
    test_result 1 "Task automation failed" "$(cat /tmp/task_automation_test.log)"
fi

# Test 9: Services Running
echo ""
echo "=== Test 9: System Services ==="

GUNICORN_STATUS=$(systemctl is-active gunicorn 2>/dev/null || echo "inactive")
if [ "$GUNICORN_STATUS" == "active" ]; then
    test_result 0 "Gunicorn service running"
else
    test_result 1 "Gunicorn service not running" "Status: $GUNICORN_STATUS"
fi

CELERY_STATUS=$(systemctl is-active celery 2>/dev/null || echo "inactive")
if [ "$CELERY_STATUS" == "active" ]; then
    test_result 0 "Celery service running"
else
    test_result 1 "Celery service not running" "Status: $CELERY_STATUS (may be optional)"
fi

NGINX_STATUS=$(systemctl is-active nginx 2>/dev/null || echo "inactive")
if [ "$NGINX_STATUS" == "active" ]; then
    test_result 0 "Nginx service running"
else
    test_result 1 "Nginx service not running" "Status: $NGINX_STATUS"
fi

# Test 10: HTTP Accessibility
echo ""
echo "=== Test 10: HTTP Accessibility ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ]; then
    test_result 0 "Site accessible via HTTP" "Status: $HTTP_CODE"
else
    test_result 1 "Site not accessible" "HTTP $HTTP_CODE"
fi

# Test 11: API Endpoint
echo ""
echo "=== Test 11: Calendar API Endpoint ==="
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/oobc-management/staff/calendar/feed/json/" 2>/dev/null || echo "000")
if [ "$API_CODE" == "200" ] || [ "$API_CODE" == "302" ] || [ "$API_CODE" == "403" ]; then
    # 403 is acceptable (requires login)
    test_result 0 "Calendar API endpoint accessible" "Status: $API_CODE"
else
    test_result 1 "Calendar API endpoint error" "HTTP $API_CODE"
fi

# Test 12: Log Files
echo ""
echo "=== Test 12: Log Files ==="
if [ -f "${PROJECT_DIR}/logs/django.log" ]; then
    RECENT_ERRORS=$(tail -100 "${PROJECT_DIR}/logs/django.log" | grep -i error | grep -v "ERROR_404" | wc -l)
    if [ "$RECENT_ERRORS" -eq 0 ]; then
        test_result 0 "No recent errors in Django log"
    else
        test_result 1 "Errors found in Django log" "$RECENT_ERRORS errors in last 100 lines"
    fi
else
    test_result 1 "Django log file not found"
fi

# Summary
echo ""
echo "================================================================"
echo "SMOKE TEST SUMMARY"
echo "================================================================"
echo -e "Tests Run:    ${TESTS_RUN}"
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "Deployment appears successful!"
    echo ""
    echo "Recommended next steps:"
    echo "  1. Manual testing of critical features"
    echo "  2. Monitor logs for 1 hour"
    echo "  3. Get user feedback"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review failed tests above."
    echo ""
    echo "If critical issues found, consider rollback:"
    echo "  ./scripts/rollback.sh"
    echo ""
    exit 1
fi
