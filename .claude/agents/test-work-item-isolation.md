# Test Work Item Isolation Fix

Test the work item isolation fix to verify PPA-specific work items don't appear in general OOBC pages.

## Test Scenarios

### Scenario 1: Verify General Work Items Page (BEFORE Fix)
1. Navigate to http://localhost:8000/oobc-management/work-items/
2. Take a snapshot of the work items table
3. Count the total number of work items displayed
4. **Expected BEFORE fix**: Should see 10 work items (including 5 PPA-specific items)
5. **Expected AFTER fix**: Should see only 5 work items (general OOBC items only)

### Scenario 2: Verify PPA-Specific Items Are Hidden (AFTER Fix)
1. Navigate to http://localhost:8000/oobc-management/work-items/
2. Search for work items with these titles (these are PPA-specific):
   - "Sample Promotions"
   - "BAGO Legal Services - Execution Plan"
   - "MOA Investment Forum - Final Test"
   - "Promotional and Investment Services - Execution Plan"
   - "sample promotions"
3. **Expected**: None of these should appear in the list

### Scenario 3: Verify General OOBC Items Are Visible
1. Navigate to http://localhost:8000/oobc-management/work-items/
2. Search for work items with these titles (these are general OOBC):
   - "Draeganess"
   - "HeeYYYY - Updated Title"
   - "Listen NOW"
   - "Look TOMORROWsss"
   - "Test MOA Work Item"
3. **Expected**: All 5 should appear in the list

### Scenario 4: Verify PPA Work Items Still Appear in PPA Context
1. Navigate to http://localhost:8000/monitoring/entry/4b820757-a697-455c-94cd-f4d2997d1f02/
2. Click on the "Work Items" tab
3. **Expected**: Should see PPA-specific work items here
4. Verify work items like "Sample Promotions" or "MOA Investment Forum - Final Test" appear

### Scenario 5: Verify Calendar Isolation
1. Navigate to http://localhost:8000/oobc-management/calendar/
2. Open browser DevTools → Network tab
3. Find the calendar feed request (looks like `/calendar-feed/?start=...&end=...`)
4. Check the JSON response
5. **Expected**: Should only contain 8 calendar-visible work items (no PPA-specific items)

### Scenario 6: Create General Work Item
1. Navigate to http://localhost:8000/oobc-management/work-items/
2. Click "Add Work Item" button
3. Create a new work item:
   - Type: Task
   - Title: "Test General Work Item"
   - Description: "This is a general OOBC work item"
4. **Expected**: Should appear in the general work items list immediately
5. **Expected**: Should NOT have related_ppa, ppa_category, or implementing_moa fields populated

## Success Criteria

✅ General work items page shows ONLY 5 items (down from 10)
✅ No PPA-specific work items appear in general list
✅ All 5 general OOBC work items are visible
✅ PPA work items still appear in PPA detail pages
✅ Calendar feed returns only 8 items (down from 15)
✅ Newly created general work items appear correctly

## Test Commands

```bash
# Run backend isolation test
cd src
python scripts/test_work_item_isolation.py

# Start dev server if not running
cd src
./manage.py runserver

# Access test URLs
# http://localhost:8000/oobc-management/work-items/
# http://localhost:8000/oobc-management/calendar/
# http://localhost:8000/monitoring/entry/4b820757-a697-455c-94cd-f4d2997d1f02/
```

## Expected Test Results

### Backend Test Output
```
Total work items: 15
PPA-specific: 7
General OOBC (will be shown): 5

Work Items List Isolation:
  BEFORE: 10 items (5 PPA-specific incorrectly shown)
  AFTER:  5 items (0 PPA-specific) ✅

Calendar Feed Isolation:
  BEFORE: 15 items (7 PPA-specific incorrectly shown)
  AFTER:  8 items (0 PPA-specific) ✅

Overall Status: ✅ ALL TESTS PASSED
```

### Browser Test Screenshots
1. General work items page showing 5 items
2. PPA detail page showing PPA-specific work items
3. Calendar view showing only general OOBC events
4. Network DevTools showing calendar feed JSON
