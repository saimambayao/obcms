#!/bin/bash

echo "================================================"
echo "CALENDAR DELETE - FINAL FIX VERIFICATION"
echo "================================================"
echo ""

PASS=0
FAIL=0

# Test 1: Check @never_cache decorator
echo "Test 1: Checking for @never_cache decorator..."
if grep -q "@never_cache" src/common/views/calendar.py; then
    echo "   ✅ PASS: @never_cache decorator found"
    ((PASS++))
else
    echo "   ❌ FAIL: @never_cache decorator NOT found"
    ((FAIL++))
fi
echo ""

# Test 2: Check never_cache import
echo "Test 2: Checking for never_cache import..."
if grep -q "from django.views.decorators.cache import never_cache" src/common/views/calendar.py; then
    echo "   ✅ PASS: never_cache import found"
    ((PASS++))
else
    echo "   ❌ FAIL: never_cache import NOT found"
    ((FAIL++))
fi
echo ""

# Test 3: Check cache versioning
echo "Test 3: Checking for cache versioning..."
if grep -q "cache_version = cache.get" src/common/views/calendar.py; then
    echo "   ✅ PASS: Cache versioning found"
    ((PASS++))
else
    echo "   ❌ FAIL: Cache versioning NOT found"
    ((FAIL++))
fi
echo ""

# Test 4: Check invalidate_calendar_cache function
echo "Test 4: Checking for invalidate_calendar_cache function..."
if grep -q "def invalidate_calendar_cache" src/common/views/work_items.py; then
    echo "   ✅ PASS: Cache invalidation function found"
    ((PASS++))
else
    echo "   ❌ FAIL: Cache invalidation function NOT found"
    ((FAIL++))
fi
echo ""

# Test 5: Check cache invalidation calls
echo "Test 5: Checking cache invalidation is called..."
CALLS=$(grep -c "invalidate_calendar_cache(request.user.id)" src/common/views/work_items.py)
if [ "$CALLS" -ge 3 ]; then
    echo "   ✅ PASS: Cache invalidation called $CALLS times (create/edit/delete)"
    ((PASS++))
else
    echo "   ⚠️  WARNING: Cache invalidation called only $CALLS times (expected 3)"
fi
echo ""

# Test 6: Check improved event removal
echo "Test 6: Checking for improved event removal..."
if grep -q "allEvents.find(function(evt)" src/templates/common/oobc_calendar.html; then
    echo "   ✅ PASS: Improved event removal found"
    ((PASS++))
else
    echo "   ⚠️  WARNING: Using getEventById (may have issues)"
fi
echo ""

# Test 7: Check CSRF configuration
echo "Test 7: Checking CSRF configuration..."
if grep -q "htmx:configRequest" src/templates/base.html; then
    echo "   ✅ PASS: HTMX CSRF configuration found"
    ((PASS++))
else
    echo "   ❌ FAIL: HTMX CSRF configuration NOT found"
    ((FAIL++))
fi
echo ""

echo "================================================"
echo "RESULTS: $PASS passed, $FAIL failed"
echo "================================================"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 ALL FIXES ARE IN PLACE!"
    echo ""
    echo "Next steps:"
    echo "1. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)"
    echo "2. Open calendar: http://localhost:8000/oobc-management/calendar/"
    echo "3. Open DevTools → Network tab"
    echo "4. Delete a work item"
    echo "5. Check Network tab for calendar feed request"
    echo "6. Verify Response Headers include:"
    echo "   Cache-Control: no-cache, no-store, must-revalidate"
    echo "7. Verify event count decreases (e.g., 30 → 29)"
    echo "8. Hard refresh page again"
    echo "9. Verify deleted item is GONE"
    echo ""
    echo "Expected console output:"
    echo "  ✅ CSRF token added to DELETE request"
    echo "  🗑️  Work item deleted: {...}"
    echo "  ✅ Removed event from calendar with ID: work-item-[uuid]"
    echo "  🔄 Refreshing calendar..."
    echo "  📊 Calendar events loaded - 29 items  ← ONE LESS"
    echo ""
    exit 0
else
    echo "❌ $FAIL CRITICAL TESTS FAILED"
    echo ""
    echo "Review the failures above and apply the necessary fixes."
    echo ""
    exit 1
fi
