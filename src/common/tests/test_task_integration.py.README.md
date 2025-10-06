# test_task_integration.py - SKIPPED

## Status: SKIPPED

This test file has been skipped because it tests end-to-end workflows that depend on TaskTemplate functionality which was never implemented.

## Reason for Skipping

The test file relies on:
- `TaskTemplate` model - Does not exist
- `TaskTemplateItem` model - Does not exist
- Template-based workflow automation - Not implemented
- Legacy `StaffTask` model - Replaced by `WorkItem`

## What This Test File Tests

1. **AssessmentTaskWorkflowIntegrationTests**
   - Complete workflow from assessment creation → task auto-creation → task completion
   - Task assignment to teams and staff
   - Domain-specific views
   - Assessment-specific task views with phase grouping
   - Task analytics

2. **EventTaskWorkflowIntegrationTests**
   - Event creation → automatic task generation
   - Event-specific task views
   - Meeting preparation workflow

3. **PolicyTaskWorkflowIntegrationTests**
   - Policy creation → multi-phase task automation
   - Policy development cycle (research → drafting → consultation)
   - Phase-based task grouping

4. **TemplateInstantiationWorkflowTests**
   - Browsing template list
   - Viewing template details
   - Instantiating templates to create tasks
   - Due date calculation from template

5. **TaskBoardKanbanWorkflowTests**
   - Drag-and-drop kanban board functionality
   - Moving tasks between columns (not_started → in_progress → completed)

6. **MultiDomainAnalyticsWorkflowTests**
   - Analytics across MANA, Coordination, Policy, Monitoring, Services domains
   - Domain breakdown, completion rates, priority distribution

## Migration Status

**Priority:** MEDIUM - Integration tests are valuable, but need complete rewrite

**What Would Be Needed:**
1. Rewrite all tests to use `WorkItem` model instead of `StaffTask`
2. Remove template-based automation tests (or implement templates first)
3. Update URL patterns to match current routing (some views may have changed)
4. Verify kanban board still uses same HTMX patterns
5. Test analytics with real WorkItem data

**Value:**
- These integration tests are VERY VALUABLE for verifying end-to-end workflows
- Should be migrated after WorkItem stabilizes, not deleted permanently

## Current State of Tested Features

| Feature | Status | Notes |
|---------|--------|-------|
| Assessment workflows | ✅ Exists | Uses WorkItem, not StaffTask |
| Event workflows | ✅ Exists | Coordination events work differently now |
| Policy workflows | ✅ Exists | Policy tracking exists but different structure |
| Template system | ❌ Never implemented | Not in codebase |
| Kanban board | ✅ Exists | Staff task board at `/oobc-management/staff/tasks/` |
| Analytics | ✅ Exists | Task analytics dashboard exists |
| Domain filtering | ✅ Exists | WorkItem has activity_type field |

## Recommended Next Steps

1. **Short-term:** Keep skipped, focus on WorkItem stability
2. **Medium-term:** Create new integration tests for WorkItem workflows
3. **Long-term:** Decide if template system should be implemented

## Related Files

- **WorkItem Model:** `src/common/models/work_item.py`
- **WorkItem Views:** `src/common/views/work_items.py`
- **Task Board View:** `src/common/views/tasks.py` (staff_task_board)
- **WorkItem Tests:** `src/common/tests/test_work_item_integration.py` (exists!)

## Last Modified

- Test file created: October 2, 2025
- Skipped on: October 5, 2025
- Reason: Depends on non-existent TaskTemplate models and legacy StaffTask
