# Phase 0.5 - Coordination URL Migration Status

**Date:** 2025-10-13
**Status:** IN PROGRESS - PAUSED DUE TO FILE CORRUPTION

## Issue Encountered

During Phase 0.5c migration, the linter automatically reverted changes to `common/urls.py`, causing:
- Previously commented URLs to become active again
- Migration comments to be removed
- File integrity issues

## Completed Sub-phases

### ✅ Phase 0.5a - Partnerships (5 URLs)
- **Status:** COMPLETE
- **Location:** `coordination/urls.py` lines 29-56
- **URLs Migrated:**
  1. `partnerships/` → `coordination:partnerships`
  2. `partnerships/add/` → `coordination:partnership_add`
  3. `partnerships/<id>/` → `coordination:partnership_view`
  4. `partnerships/<id>/edit/` → `coordination:partnership_edit`
  5. `partnerships/<id>/delete/` → `coordination:partnership_delete`

### ✅ Phase 0.5b - Organizations (6 URLs)
- **Status:** COMPLETE
- **Location:** `coordination/urls.py` lines 58-90
- **URLs Migrated:**
  1. `organizations/` → `coordination:organizations`
  2. `organizations/add/` → `coordination:organization_add`
  3. `organizations/<id>/edit/` → `coordination:organization_edit`
  4. `organizations/<id>/delete/` → `coordination:organization_delete`
  5. `organizations/<id>/work-items/partial/` → `coordination:organization_work_items_partial`
  6. `organizations/<id>/` → `coordination:organization_detail`

### ✅ Phase 0.5c - Core Coordination (7 URLs)
- **Status:** COMPLETE (in coordination/urls.py)
- **Status:** NEEDS CLEANUP (common/urls.py auto-reverted)
- **Location:** `coordination/urls.py` lines 92-105
- **URLs Migrated:**
  1. `` (root) → `coordination:home`
  2. `events/` → `coordination:events`
  3. `calendar/` → `coordination:calendar`
  4. `view-all/` → `coordination:view_all`
  5. `activities/add/` → `coordination:activity_add`
  6. `notes/add/` → `coordination:note_add`
  7. `notes/activity-options/` → `coordination:note_activity_options`

## Pending Sub-phases

### ⏳ Phase 0.5d - Calendar Resources (14 URLs)
**HIGH RISK - Drag-and-drop functionality**

URLs to migrate from `common/urls.py`:
1. `oobc-management/calendar/resources/` → `coordination:calendar_resource_list`
2. `oobc-management/calendar/resources/add/` → `coordination:calendar_resource_create`
3. `oobc-management/calendar/resources/<id>/` → `coordination:calendar_resource_detail`
4. `oobc-management/calendar/resources/<id>/edit/` → `coordination:calendar_resource_edit`
5. `oobc-management/calendar/resources/<id>/delete/` → `coordination:calendar_resource_delete`
6. `oobc-management/calendar/resources/<id>/calendar/` → `coordination:calendar_resource_calendar`
7. `oobc-management/calendar/resources/<id>/book/` → `coordination:calendar_booking_request`
8. `oobc-management/calendar/bookings/` → `coordination:calendar_booking_list`
9. `oobc-management/calendar/bookings/request/` → `coordination:calendar_booking_request_general`
10. `oobc-management/calendar/bookings/<id>/approve/` → `coordination:calendar_booking_approve`
11. `coordination/resources/<id>/bookings/feed/` → `coordination:resource_bookings_feed`
12. `coordination/resources/check-conflicts/` → `coordination:check_conflicts`
13. `coordination/resources/<id>/book-enhanced/` → `coordination:resource_booking_form`
14. `api/calendar/event/update/` → `coordination:calendar_event_update` (drag-and-drop API)

### ⏳ Phase 0.5e - Staff Leave (3 URLs)
1. `oobc-management/staff/leave/` → `coordination:staff_leave_list`
2. `oobc-management/staff/leave/request/` → `coordination:staff_leave_request`
3. `oobc-management/staff/leave/<id>/approve/` → `coordination:staff_leave_approve`

### ⏳ Phase 0.5f - Calendar Sharing (5 URLs)
1. `oobc-management/calendar/share/` → `coordination:calendar_share_create`
2. `oobc-management/calendar/share/manage/` → `coordination:calendar_share_manage`
3. `calendar/shared/<token>/` → `coordination:calendar_share_view`
4. `oobc-management/calendar/share/<id>/toggle/` → `coordination:calendar_share_toggle`
5. `oobc-management/calendar/share/<id>/delete/` → `coordination:calendar_share_delete`

## Action Required

1. **Fix `common/urls.py` manually:**
   - Comment out lines 194-304 (coordination URLs)
   - Add migration header with date
   - Ensure MANA and Communities migrations are commented

2. **Complete remaining phases:**
   - Phase 0.5d (HIGH RISK - test drag-and-drop carefully)
   - Phase 0.5e
   - Phase 0.5f

3. **Testing checklist:**
   - [ ] Calendar drag-and-drop works
   - [ ] Resource booking workflows functional
   - [ ] Staff leave management works
   - [ ] Calendar sharing functional
   - [ ] All HTMX interactions work

4. **Update coordination URLs in main `urls.py`:**
   ```python
   # Add to src/obc_management/urls.py
   path('coordination/', include('coordination.urls')),
   ```

## Files Modified

- ✅ `/Users/saidamenmambayao/.../obcms/src/coordination/urls.py` (migrated URLs added)
- ⚠️ `/Users/saidamenmambayao/.../obcms/src/common/urls.py` (needs manual cleanup)
- ⏳ `/Users/saidamenmambayao/.../obcms/src/obc_management/urls.py` (needs coordination path)

## Total URL Count

- **Completed:** 18 URLs (5 + 6 + 7)
- **Pending:** 22 URLs (14 + 3 + 5)
- **Total:** 40 URLs (not 97 as initially estimated)

The 97 estimate likely included:
- Duplicate path/re_path patterns
- Legacy commented URLs
- Related non-coordination URLs

## Next Steps

1. ✅ Document current status (this file)
2. ⏳ Manually fix `common/urls.py`
3. ⏳ Complete Phase 0.5d (Calendar Resources)
4. ⏳ Complete Phase 0.5e (Staff Leave)
5. ⏳ Complete Phase 0.5f (Calendar Sharing)
6. ⏳ Test all functionality
7. ⏳ Update Phase 0 execution checklist
