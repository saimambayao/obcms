# test_task_views_extended.py - SKIPPED

## Status: SKIPPED

This test file has been skipped because it tests views that depend on TaskTemplate models which do not exist in the codebase.

## Reason for Skipping

The test file imports and tests:
- `TaskTemplate` model - Does not exist
- `TaskTemplateItem` model - Does not exist
- Template-related views (list, detail, instantiate) - May not exist or work differently
- Legacy `StaffTask` model - Being replaced by `WorkItem`

## What This Test File Tests

1. **DomainTasksViewTests**
   - Domain-filtered task views (tasks_by_domain)
   - Filtering by status and priority
   - Domain-specific analytics

2. **AssessmentTasksViewTests**
   - Assessment-specific task views
   - Grouping tasks by assessment phase (planning, data_collection, analysis)

3. **EventTasksViewTests**
   - Event-specific task views
   - Tasks linked to coordination events

4. **PolicyTasksViewTests**
   - Policy-specific task views
   - Grouping tasks by policy phase (evidence, drafting, consultation)

5. **TaskAnalyticsViewTests**
   - Task analytics dashboard
   - Domain breakdown calculations
   - Completion rate calculations
   - Priority distribution
   - Recent completed task counts

6. **EnhancedDashboardViewTests**
   - Personal task dashboard
   - User-specific task filtering
   - Domain filtering
   - Personal statistics

7. **TaskTemplateListViewTests**
   - Template list view (DEPENDS ON TaskTemplate)
   - Active/inactive template filtering
   - Domain filtering

8. **TaskTemplateDetailViewTests**
   - Template detail view (DEPENDS ON TaskTemplate)
   - Template item display
   - Sequence ordering

9. **TaskTemplateInstantiateViewTests**
   - Template instantiation endpoint (DEPENDS ON TaskTemplate)
   - Task creation from templates

## Migration Status

**Priority:** MEDIUM - Some views are valuable, others depend on missing features

**What Would Be Needed:**

### For Non-Template Views (Worth Migrating)
1. Update domain task views to use WorkItem
2. Update assessment task views to use WorkItem
3. Update event task views to use WorkItem
4. Update policy task views to use WorkItem
5. Update analytics views to use WorkItem
6. Update enhanced dashboard to use WorkItem

### For Template Views (Low Priority)
1. Decide if template system should be implemented
2. If yes, implement TaskTemplate and TaskTemplateItem models
3. Create template views and URLs
4. Update tests to use new implementation

## Current State of Tested Views

| View Category | Exists? | Uses WorkItem? | Notes |
|--------------|---------|----------------|-------|
| Domain tasks | ✅ Yes | ❓ Needs verification | Check `common:tasks_by_domain` URL |
| Assessment tasks | ✅ Yes | ❓ Needs verification | Check `common:assessment_tasks` URL |
| Event tasks | ✅ Yes | ❓ Needs verification | Check `common:event_tasks` URL |
| Policy tasks | ✅ Yes | ❓ Needs verification | Check `common:policy_tasks` URL |
| Task analytics | ✅ Yes | ❓ Needs verification | Check `common:task_analytics` URL |
| Enhanced dashboard | ✅ Yes | ❓ Needs verification | Check `common:enhanced_task_dashboard` URL |
| Template list | ❌ No | N/A | TaskTemplate not implemented |
| Template detail | ❌ No | N/A | TaskTemplate not implemented |
| Template instantiate | ❌ No | N/A | TaskTemplate not implemented |

## Recommended Migration Strategy

1. **Phase 1:** Verify which URLs/views still exist in current codebase
2. **Phase 2:** Update tests for existing views to use WorkItem
3. **Phase 3:** Remove template-related tests entirely (or mark as future work)

## URL Pattern Verification Needed

Check `src/common/urls.py` for these URL patterns:
```python
path('tasks/domain/<str:domain>/', ..., name='tasks_by_domain')
path('tasks/assessment/<uuid:assessment_id>/', ..., name='assessment_tasks')
path('tasks/event/<uuid:event_id>/', ..., name='event_tasks')
path('tasks/policy/<uuid:policy_id>/', ..., name='policy_tasks')
path('tasks/analytics/', ..., name='task_analytics')
path('tasks/dashboard/', ..., name='enhanced_task_dashboard')
path('templates/', ..., name='task_template_list')
path('templates/<int:template_id>/', ..., name='task_template_detail')
path('templates/<int:template_id>/instantiate/', ..., name='instantiate_template')
```

## Related Files

- **Common URLs:** `src/common/urls.py` (check which views exist)
- **Task Views:** `src/common/views/tasks.py`
- **WorkItem Views:** `src/common/views/work_items.py`
- **WorkItem Tests:** `src/common/tests/test_work_item_views.py` (may have equivalent tests)

## Last Modified

- Test file created: October 2, 2025
- Skipped on: October 5, 2025
- Reason: Depends on TaskTemplate models and legacy StaffTask architecture
