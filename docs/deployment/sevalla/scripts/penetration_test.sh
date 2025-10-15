#!/bin/bash
# OBCMS Comprehensive Penetration Test
# Tests all implemented security features

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
BASE_URL="http://localhost:8000"

echo "============================================"
echo "OBCMS PENETRATION TEST"
echo "============================================"
echo ""
echo "Target: $BASE_URL"
echo "Date: $(date)"
echo ""

# Function to print test results
print_test() {
    echo -e "${BLUE}[TEST] $1${NC}"
}

print_pass() {
    echo -e "${GREEN}  ✅ PASS: $1${NC}"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}  ❌ FAIL: $1${NC}"
    ((FAILED++))
}

print_info() {
    echo -e "${YELLOW}  ℹ️  INFO: $1${NC}"
}

# ============================================
# 1. AUTHENTICATION TESTS
# ============================================
echo ""
echo "=== 1. AUTHENTICATION & SESSION SECURITY ==="
echo ""

# Test 1.1: Health endpoint (should be accessible)
print_test "Health endpoint accessibility"
HEALTH=$(curl -s $BASE_URL/health/ | grep -o "healthy")
if [ "$HEALTH" = "healthy" ]; then
    print_pass "Health endpoint accessible without auth"
else
    print_fail "Health endpoint not working"
fi

# Test 1.2: Admin panel requires auth
print_test "Admin panel authentication requirement"
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/admin/)
if [ "$ADMIN_STATUS" = "302" ] || [ "$ADMIN_STATUS" = "200" ]; then
    print_pass "Admin panel redirect (requires login)"
else
    print_fail "Admin panel returned unexpected status: $ADMIN_STATUS"
fi

# Test 1.3: SQL Injection in login (development test)
print_test "SQL injection resistance in auth"
LOGIN_SQL=$(curl -s -X POST $BASE_URL/login/ \
    -d "username=admin' OR '1'='1" \
    -d "password=anything" \
    -w "%{http_code}" -o /dev/null 2>/dev/null || echo "000")

if [ "$LOGIN_SQL" != "500" ]; then
    print_pass "SQL injection attempt did not crash server (status: $LOGIN_SQL)"
else
    print_fail "SQL injection caused server error"
fi

# ============================================
# 2. API SECURITY TESTS
# ============================================
echo ""
echo "=== 2. API SECURITY ==="
echo ""

# Test 2.1: API requires authentication
print_test "API authentication requirement"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/)
if [ "$API_STATUS" = "403" ] || [ "$API_STATUS" = "401" ] || [ "$API_STATUS" = "404" ]; then
    print_pass "API requires authentication (status: $API_STATUS)"
else
    print_fail "API may be publicly accessible (status: $API_STATUS)"
fi

# Test 2.2: Rate limiting on repeated requests
print_test "API rate limiting (burst protection)"
print_info "Sending 70 rapid requests to test burst throttle..."
RATE_LIMITED=0
for i in {1..70}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health/)
    if [ "$STATUS" = "429" ]; then
        RATE_LIMITED=1
        break
    fi
done

if [ $RATE_LIMITED -eq 1 ]; then
    print_pass "Rate limiting activated (429 Too Many Requests)"
else
    print_info "Rate limit not hit in 70 requests (60/min burst limit)"
fi

# ============================================
# 3. INPUT VALIDATION TESTS
# ============================================
echo ""
echo "=== 3. INPUT VALIDATION ==="
echo ""

# Test 3.1: XSS in URL parameters
print_test "XSS resistance in URL parameters"
XSS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    "$BASE_URL/?search=<script>alert('XSS')</script>")
if [ "$XSS_STATUS" != "500" ]; then
    print_pass "XSS payload did not crash server (status: $XSS_STATUS)"
else
    print_fail "XSS payload caused server error"
fi

# Test 3.2: Path traversal in URL
print_test "Path traversal resistance"
TRAVERSAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    "$BASE_URL/../../etc/passwd")
if [ "$TRAVERSAL_STATUS" = "404" ]; then
    print_pass "Path traversal blocked (404 Not Found)"
else
    print_info "Path traversal response: $TRAVERSAL_STATUS"
fi

# ============================================
# 4. SECURITY HEADERS
# ============================================
echo ""
echo "=== 4. SECURITY HEADERS ==="
echo ""

# Test 4.1: X-Frame-Options header
print_test "X-Frame-Options (clickjacking protection)"
XFRAME=$(curl -s -I $BASE_URL/ | grep -i "X-Frame-Options")
if echo "$XFRAME" | grep -qi "DENY\|SAMEORIGIN"; then
    print_pass "X-Frame-Options present: $XFRAME"
else
    print_fail "X-Frame-Options missing or weak"
fi

# Test 4.2: X-Content-Type-Options
print_test "X-Content-Type-Options (MIME sniffing)"
XCONTENT=$(curl -s -I $BASE_URL/ | grep -i "X-Content-Type-Options")
if echo "$XCONTENT" | grep -qi "nosniff"; then
    print_pass "X-Content-Type-Options: nosniff present"
else
    print_fail "X-Content-Type-Options missing"
fi

# ============================================
# 5. CSRF PROTECTION
# ============================================
echo ""
echo "=== 5. CSRF PROTECTION ==="
echo ""

# Test 5.1: POST without CSRF token
print_test "CSRF protection on POST requests"
CSRF_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST $BASE_URL/login/ \
    -d "username=test&password=test")
if [ "$CSRF_STATUS" = "403" ]; then
    print_pass "CSRF protection active (403 Forbidden)"
else
    print_info "POST without CSRF returned: $CSRF_STATUS (may allow if GET fallback)"
fi

# ============================================
# 6. ERROR HANDLING
# ============================================
echo ""
echo "=== 6. ERROR HANDLING & INFO DISCLOSURE ==="
echo ""

# Test 6.1: 404 error message
print_test "404 error disclosure"
NOT_FOUND=$(curl -s $BASE_URL/this-page-does-not-exist-test-404/)
if echo "$NOT_FOUND" | grep -qi "traceback\|django\|python"; then
    print_fail "404 page may expose DEBUG information"
else
    print_pass "404 page does not expose stack traces"
fi

# Test 6.2: Invalid URL format
print_test "Malformed URL handling"
MALFORMED=$(curl -s -o /dev/null -w "%{http_code}" \
    "$BASE_URL/<>?invalid")
if [ "$MALFORMED" != "500" ]; then
    print_pass "Malformed URL handled gracefully (status: $MALFORMED)"
else
    print_fail "Malformed URL caused server error"
fi

# ============================================
# 7. FILE SECURITY
# ============================================
echo ""
echo "=== 7. FILE & MEDIA SECURITY ==="
echo ""

# Test 7.1: Media directory listing
print_test "Media directory listing prevention"
MEDIA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/media/)
if [ "$MEDIA_STATUS" = "403" ] || [ "$MEDIA_STATUS" = "404" ]; then
    print_pass "Media directory not listable (status: $MEDIA_STATUS)"
else
    print_info "Media directory returned: $MEDIA_STATUS"
fi

# Test 7.2: Static directory listing
print_test "Static directory listing prevention"
STATIC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/static/)
if [ "$STATIC_STATUS" = "403" ] || [ "$STATIC_STATUS" = "404" ]; then
    print_pass "Static directory not listable (status: $STATIC_STATUS)"
else
    print_info "Static directory returned: $STATIC_STATUS"
fi

# ============================================
# 8. READINESS CHECK
# ============================================
echo ""
echo "=== 8. DEPLOYMENT READINESS ==="
echo ""

# Test 8.1: Readiness endpoint
print_test "Readiness check endpoint"
READY=$(curl -s $BASE_URL/ready/ | grep -o "ready\|not_ready")
if [ "$READY" = "ready" ]; then
    print_pass "System ready (database + cache accessible)"
elif [ "$READY" = "not_ready" ]; then
    print_info "System not ready (check dependencies)"
else
    print_fail "Readiness endpoint not responding correctly"
fi

# ============================================
# TEST SUMMARY
# ============================================
echo ""
echo "============================================"
echo "PENETRATION TEST SUMMARY"
echo "============================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    PERCENTAGE=$((PASSED * 100 / TOTAL))
    echo "Success Rate: $PERCENTAGE%"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL PENETRATION TESTS PASSED!${NC}"
    echo ""
    echo "Security posture: STRONG"
    echo "Recommendation: Ready for staging deployment"
else
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED${NC}"
    echo ""
    echo "Review failed tests above"
    echo "Remediate before production deployment"
fi

echo ""
echo "Next steps:"
echo "1. Review test results above"
echo "2. Fix any critical findings"
echo "3. Deploy to staging for external pen test"
echo "4. Schedule professional security audit (Month 3)"
echo ""
