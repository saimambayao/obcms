# Calendar Event Filtering & Icons Debug Fix

**Date:** 2025-10-06
**Status:** Debug logging added, awaiting user testing
**Operating Mode:** Debugger Mode

## Problem Summary

The user reported two issues with the advanced modern calendar:

1. **❌ Event filtering not working**: Unchecking event types (Projects, Activities, Tasks) doesn't remove events from the calendar (all 13 events still show)
2. **❌ Icons not appearing**: Event type icons are not displaying on calendar events

Console showed:
```
Applying filters. Total events: 13
Active filters: {"project":true,"activity":true,"task":true,"coordination":true,"completed":false}
Filtered events: 13  <-- Should be less if filtering worked!
```

## Root Cause Analysis

### Data Structure Mismatch

**The Issue:**
The JavaScript code was looking for `work_type` in the wrong location:

```javascript
// ❌ WRONG (original code):
const workType = event.extendedProps.work_type;  // undefined!
```

**Why it was wrong:**

1. **API Response Structure** (`/common/views/calendar.py` line 150):
   ```python
   work_items.append({
       'id': f'work-item-{item.pk}',
       'title': item.title,
       'workType': item.work_type,  # <-- At TOP LEVEL, not in extendedProps
       'status': item.status,        # <-- Also at top level
       'extendedProps': {
           'assignees': [...],
           'teams': [...]
       }
   })
   ```

2. **How FullCalendar Handles Data:**
   - FullCalendar moves non-standard fields to `extendedProps` automatically
   - Standard fields: `id`, `title`, `start`, `end`, `color`, `url`
   - Custom fields: `workType`, `status`, `priority` → moved to `extendedProps.workType`, etc.

3. **Two Different Contexts:**
   - **In `fetchEvents` / `applyFilters`**: Working with raw API data → `event.workType` (top level)
   - **In `eventDidMount`**: Working with FullCalendar-processed data → `info.event.extendedProps.workType`

### Completion Status Check

**The Issue:**
There is no `is_completed` field. Completion is determined by:

```python
# status field has values: "planned", "in_progress", "completed", "cancelled"
const isCompleted = event.status === 'completed';
```

## Fixes Applied

### 1. Enhanced Debug Logging

**File:** `/src/templates/common/calendar_advanced_modern.html`

**Added to `fetchEvents` function (line ~906):**
```javascript
// 🔍 DEBUG: Log first event to see structure
if (data.length > 0) {
    console.log('📊 FIRST EVENT STRUCTURE:', JSON.stringify(data[0], null, 2));
    console.log('📊 Event keys:', Object.keys(data[0]));
    if (data[0].extendedProps) {
        console.log('📊 ExtendedProps keys:', Object.keys(data[0].extendedProps));
    }
}
```

**Enhanced `applyFilters` function (line ~946):**
```javascript
// Track statistics
let filterStats = {
    total: events.length,
    filteredByType: 0,
    filteredByCompletion: 0,
    kept: 0
};

const filtered = events.filter((event, index) => {
    // FIX: workType is at TOP LEVEL in raw API data
    const workType = event.workType || event.extendedProps?.work_type;

    // FIX: Check status field for completion
    const isCompleted = event.status === 'completed';

    // DEBUG: Log first 5 events
    if (index < 5) {
        console.log(`🔍 Event #${index + 1}:`, event.title);
        console.log('  - workType (from event.workType):', event.workType);
        console.log('  - workType (from extendedProps):', event.extendedProps?.work_type);
        console.log('  - status:', event.status);
        console.log('  - isCompleted:', isCompleted);
        console.log('  - activeFilters[workType]:', activeFilters[workType]);
    }

    // Check work type filter
    if (workType && !activeFilters[workType]) {
        filterStats.filteredByType++;
        return false;
    }

    // Check completed filter
    if (isCompleted && !activeFilters.completed) {
        filterStats.filteredByCompletion++;
        return false;
    }

    filterStats.kept++;
    return true;
});

console.log('📊 Filter Statistics:', filterStats);
```

**Fixed `eventDidMount` function (line ~826):**
```javascript
// FullCalendar moves non-standard fields to extendedProps
// Our API returns 'workType' at top level, but FullCalendar moves it to extendedProps
const workType = info.event.extendedProps.workType;
```

### 2. Expected Work Type Values

Based on the filter checkboxes and API code:

- `project` - Projects and Sub-Projects (WORK_TYPE_PROJECT, WORK_TYPE_SUB_PROJECT)
- `activity` - Activities and Sub-Activities (WORK_TYPE_ACTIVITY, WORK_TYPE_SUB_ACTIVITY)
- `task` - Tasks and Subtasks (WORK_TYPE_TASK, WORK_TYPE_SUBTASK)
- `coordination` - Coordination events (if they exist - needs verification)

### 3. Status Values

From `common/models.py`:
- `planned` - Planned status
- `ongoing` or `in_progress` - In progress status
- `completed` - Completed status
- `cancelled` - Cancelled status

## Testing Instructions

### Step 1: Reload the Calendar Page

1. Navigate to: `/oobc-management/calendar/advanced/`
2. Open browser DevTools Console (F12 → Console tab)
3. Reload the page (F5 or Cmd+R)

### Step 2: Check Debug Output

**Expected console output:**

```
📊 FIRST EVENT STRUCTURE: {
  "id": "work-item-123",
  "title": "Regional Infrastructure Assessment",
  "workType": "project",  // <-- Should be here at top level
  "status": "in_progress",
  "start": "2025-10-01",
  "end": "2025-10-02",
  "color": "#3b82f6",
  "extendedProps": {
    "assignees": ["John Doe"],
    "teams": ["Regional Team"]
  }
}
📊 Event keys: ["id", "title", "workType", "status", "start", "end", "color", "extendedProps"]
📊 ExtendedProps keys: ["assignees", "teams"]

Applying filters. Total events: 13
Active filters: {"project":true,"activity":true,"task":true,"coordination":true,"completed":false}

🔍 Event #1: Regional Infrastructure Assessment
  - workType (from event.workType): project
  - workType (from extendedProps): undefined
  - status: in_progress
  - isCompleted: false
  - activeFilters[workType]: true
  ✅ Keeping: Regional Infrastructure Assessment

🔍 Event #2: Community Needs Assessment
  - workType (from event.workType): activity
  - workType (from extendedProps): undefined
  - status: planned
  - isCompleted: false
  - activeFilters[workType]: true
  ✅ Keeping: Community Needs Assessment

📊 Filter Statistics: {
  total: 13,
  filteredByType: 0,
  filteredByCompletion: 0,
  kept: 13
}
Filtered events: 13
```

### Step 3: Test Event Type Filtering

1. **Uncheck "Projects"** checkbox in sidebar
2. Check console output:
   ```
   📊 Filter Statistics: {
     total: 13,
     filteredByType: 5,  // <-- Should be > 0
     filteredByCompletion: 0,
     kept: 8  // <-- Should be less than total
   }
   Filtered events: 8  // <-- Should match 'kept'
   ```

3. **Expected result:** Project events should disappear from calendar

4. **Re-check "Projects"** → All events should return

5. **Uncheck "Activities"** → Activity events should disappear

6. **Uncheck "Tasks"** → Task events should disappear

### Step 4: Test Icons

1. Check if icons appear on calendar events:
   - Projects: 📁 (fa-folder) in blue
   - Activities: ✅ (fa-calendar-check) in green
   - Tasks: ☑️ (fa-tasks) in purple
   - Coordination: 🤝 (fa-handshake) in teal

2. Icons should appear:
   - **Month view:** Before event title in each event box
   - **Week/Day view:** Before event title in time slots

### Step 5: Share Findings

**Copy and paste the console output** including:

1. First event structure (📊 FIRST EVENT STRUCTURE)
2. First 5 event debug logs (🔍 Event #1, #2, etc.)
3. Filter statistics when unchecking "Projects"
4. Any errors or unexpected behavior

## Potential Issues & Solutions

### Issue 1: workType is undefined in both locations

**Symptom:**
```
- workType (from event.workType): undefined
- workType (from extendedProps): undefined
```

**Cause:** API might not be returning `workType` field

**Solution:** Check the calendar feed view response:
```bash
cd src
python manage.py shell
>>> from common.models import WorkItem
>>> item = WorkItem.objects.first()
>>> print(item.work_type)  # See what this returns
```

### Issue 2: activeFilters[workType] is undefined

**Symptom:**
```
- activeFilters[workType]: undefined
```

**Cause:** workType value doesn't match filter keys

**Solution:** workType might be using different values (e.g., "PROJECT" instead of "project"). Need to add normalization:

```javascript
const workType = (event.workType || event.extendedProps?.work_type).toLowerCase();
```

### Issue 3: Coordination filter always shows 0 events

**Symptom:** No coordination events exist

**Cause:** The API (`work_items_calendar_feed`) only returns WorkItems (projects, activities, tasks), not coordination events

**Solution:** Either:
1. Remove the coordination filter from the UI
2. Add a separate API call for coordination events
3. Create WorkItems with `work_type='coordination'`

### Issue 4: Icons still not appearing

**Symptom:** Icons don't render in calendar

**Possible causes:**
1. workType is undefined in `eventDidMount`
2. Font Awesome not loaded
3. workTypeIcons mapping doesn't match workType values

**Debug:**
```javascript
// Add to eventDidMount:
console.log('🎨 eventDidMount - workType:', workType, 'icon:', workTypeIcons[workType]);
```

## Next Steps

1. **User tests the page** and shares console output
2. **Analyze the actual data structure** from console logs
3. **Adjust code based on findings** (if workType values are different than expected)
4. **Test filtering works** (events disappear when unchecking types)
5. **Test icons appear** on calendar events
6. **Clean up debug logs** (or make conditional with localStorage flag)

## Files Modified

- `/src/templates/common/calendar_advanced_modern.html`
  - Line ~906: Added first event structure debug logging
  - Line ~946: Enhanced applyFilters with comprehensive debugging
  - Line ~826: Fixed eventDidMount to use correct extendedProps path
  - Line ~960: Fixed workType access in applyFilters (top level vs extendedProps)
  - Line ~964: Fixed completion check (status === 'completed')

## Related Files

- `/src/common/views/calendar.py` - Calendar feed view (work_items_calendar_feed)
- `/src/common/models.py` - WorkItem model definition

## Success Criteria

- [ ] Console shows actual event data structure
- [ ] workType field is accessible and has expected values
- [ ] Unchecking "Projects" removes project events from calendar
- [ ] Unchecking "Activities" removes activity events from calendar
- [ ] Unchecking "Tasks" removes task events from calendar
- [ ] Icons appear on calendar events with correct colors
- [ ] Filter statistics show correct counts
- [ ] No JavaScript errors in console

## Documentation

**See also:**
- [Calendar Architecture](CALENDAR_ARCHITECTURE_CLEAN.md) - Overall calendar architecture
- [Calendar Debug Fixes](CALENDAR_DEBUG_FIXES.md) - Previous debugging sessions
- [Modern Calendar Implementation](MODERN_CALENDAR_IMPLEMENTATION.md) - Feature overview
