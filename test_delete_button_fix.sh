#!/bin/bash

# Calendar Delete Button Fix Verification
# Tests that the HTMX processing fix is in place

echo "================================================"
echo "CALENDAR DELETE BUTTON FIX VERIFICATION"
echo "================================================"
echo ""

PASS=0
FAIL=0

# Test 1: Check if htmx.process() call exists
echo "Test 1: Checking for htmx.process() initialization..."
if grep -q "htmx.process(modalContent)" src/templates/common/oobc_calendar.html; then
    echo "   ✅ PASS: htmx.process() call found"
    ((PASS++))
else
    echo "   ❌ FAIL: htmx.process() call NOT found"
    echo "   Fix: Add htmx.process(modalContent) after modalContent.innerHTML = html"
    ((FAIL++))
fi
echo ""

# Test 2: Check if obsolete form handler removed
echo "Test 2: Checking obsolete delete form handler removed..."
if grep -q "querySelector('form\[action\*=\"/delete/\"\]')" src/templates/common/oobc_calendar.html; then
    echo "   ❌ FAIL: Obsolete form handler still present"
    echo "   Fix: Remove the form[action*='/delete/'] querySelector logic"
    ((FAIL++))
else
    echo "   ✅ PASS: Obsolete form handler removed"
    ((PASS++))
fi
echo ""

# Test 3: Check if event dispatcher exists
echo "Test 3: Checking for htmx:afterRequest event dispatcher..."
if grep -q "htmx:afterRequest" src/templates/common/oobc_calendar.html; then
    echo "   ✅ PASS: Event dispatcher found"
    ((PASS++))
else
    echo "   ❌ FAIL: Event dispatcher NOT found"
    echo "   Fix: Add htmx:afterRequest listener to process HX-Trigger headers"
    ((FAIL++))
fi
echo ""

# Test 4: Check if work-item ID format is correct
echo "Test 4: Checking for correct event ID format (work-item)..."
if grep -q "work-item-.*workItemId" src/templates/common/oobc_calendar.html; then
    echo "   ✅ PASS: Correct event ID format found"
    ((PASS++))
else
    echo "   ⚠️  WARNING: work-item ID format not found"
    echo "   May still work with fallback formats"
fi
echo ""

# Test 5: Check if work_item_delete view exists
echo "Test 5: Checking backend delete view..."
if grep -q "def work_item_delete" src/common/views/work_items.py; then
    echo "   ✅ PASS: work_item_delete view exists"
    ((PASS++))
else
    echo "   ❌ FAIL: work_item_delete view NOT found"
    echo "   Fix: Ensure backend delete handler is implemented"
    ((FAIL++))
fi
echo ""

# Test 6: Check if dev server is running
echo "Test 6: Checking if development server is running..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "   ✅ PASS: Server running on port 8000"
    ((PASS++))
else
    echo "   ⚠️  WARNING: Server NOT running"
    echo "   Start with: cd src && python manage.py runserver"
fi
echo ""

# Results
echo "================================================"
echo "RESULTS: $PASS passed, $FAIL failed"
echo "================================================"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ ALL CRITICAL TESTS PASSED!"
    echo ""
    echo "Next steps:"
    echo "1. Clear browser cache (Cmd+Shift+R)"
    echo "2. Open: http://localhost:8000/oobc-management/calendar/"
    echo "3. Open DevTools Console (F12)"
    echo "4. Click any work item"
    echo "5. Look for: '✅ HTMX initialized on modal content'"
    echo "6. Click the red Delete button"
    echo "7. Confirm deletion"
    echo ""
    echo "Expected console output:"
    echo "  ✅ HTMX initialized on modal content"
    echo "  📨 HX-Trigger header received: {...}"
    echo "  🔔 Dispatching event: workItemDeleted"
    echo "  🗑️  Work item deleted: {...}"
    echo "  ✅ Removed event from calendar: work-item-[uuid]"
    echo ""
    echo "Expected UI:"
    echo "  ✅ Modal closes immediately"
    echo "  ✅ Work item disappears from calendar"
    echo "  ✅ Success alert appears"
    echo ""
    exit 0
else
    echo "❌ $FAIL CRITICAL TESTS FAILED"
    echo ""
    echo "Review the failures above and apply the suggested fixes."
    echo "See CALENDAR_DELETE_BUTTON_FINAL_FIX.md for details."
    echo ""
    exit 1
fi
