#!/bin/bash

# Calendar Delete Button Test Script
# This script helps verify the calendar delete fix is working

echo "=================================="
echo "CALENDAR DELETE BUTTON TEST"
echo "=================================="
echo ""

# Check if server is running
echo "1. Checking if development server is running..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "   ✅ Server is running on port 8000"
else
    echo "   ❌ Server is NOT running"
    echo "   Start server with: cd src && python manage.py runserver"
    exit 1
fi
echo ""

# Check if HTMX fix is present
echo "2. Checking if HTMX fix is present in calendar template..."
if grep -q "htmx:afterRequest" src/templates/common/oobc_calendar.html; then
    echo "   ✅ htmx:afterRequest handler found"
else
    echo "   ❌ htmx:afterRequest handler NOT found"
    echo "   Fix may not be applied correctly"
    exit 1
fi
echo ""

# Check if event ID fix is present
echo "3. Checking if event ID format fix is present..."
if grep -q "work-item-.*workItemId" src/templates/common/oobc_calendar.html; then
    echo "   ✅ work-item ID format found"
else
    echo "   ❌ work-item ID format NOT found"
    echo "   Fix may not be applied correctly"
    exit 1
fi
echo ""

# Check if work item delete view exists
echo "4. Checking if work item delete view exists..."
if grep -q "def work_item_delete" src/common/views/work_items.py; then
    echo "   ✅ work_item_delete view found"
else
    echo "   ❌ work_item_delete view NOT found"
    exit 1
fi
echo ""

# Check if URL pattern exists
echo "5. Checking if work item delete URL pattern exists..."
if grep -q "work-items.*delete" src/common/urls.py; then
    echo "   ✅ work-item delete URL pattern found"
else
    echo "   ❌ work-item delete URL pattern NOT found"
    exit 1
fi
echo ""

echo "=================================="
echo "✅ ALL CHECKS PASSED"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Open browser to: http://localhost:8000/oobc-management/calendar/"
echo "2. Open DevTools Console (F12)"
echo "3. Click any work item on the calendar"
echo "4. Click the red 'Delete' button"
echo "5. Confirm the deletion"
echo ""
echo "Expected console output:"
echo "  📨 HX-Trigger header received: {...}"
echo "  🔔 Dispatching event: workItemDeleted {...}"
echo "  🗑️  Work item deleted: {...}"
echo "  ✅ Removed event from calendar: work-item-[uuid]"
echo ""
echo "Expected UI behavior:"
echo "  ✅ Modal closes immediately"
echo "  ✅ Work item disappears from calendar"
echo "  ✅ Success alert appears"
echo "  ✅ No page reload"
echo ""
echo "See CALENDAR_DELETE_FIX_COMPLETE.md for detailed testing procedure"
echo ""
