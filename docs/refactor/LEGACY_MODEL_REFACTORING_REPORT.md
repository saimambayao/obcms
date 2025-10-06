# Legacy Model Refactoring Report
## StaffTask, Event, ProjectWorkflow → WorkItem Migration

**Date:** 2025-10-05
**Status:** IN PROGRESS
**Priority:** HIGH

---

## Executive Summary

This report documents the comprehensive refactoring effort to replace all legacy model imports (StaffTask, Event, ProjectWorkflow) with the unified WorkItem model across the OBCMS codebase.

### Scope
- **Total files with legacy imports:** 40+ files
- **Total import statements:** 57+ occurrences
- **Affected modules:** common, coordination, project_central, monitoring, mana

### Current Status
- ✅ **Analysis Complete:** All legacy imports identified and categorized
- ✅ **Strategy Defined:** Refactoring patterns documented
- ⏳ **Refactoring In Progress:** calendar_api.py completed
- ⏳ **Testing Pending:** Post-refactoring validation

---

## Files Analyzed

### Category 1: CRITICAL VIEWS (Priority: URGENT)
**Status:** Partially refactored

| File | Legacy Imports | Complexity | Status |
|------|---------------|------------|--------|
| `src/common/views/calendar_api.py` | StaffTask, Event | Medium | ✅ COMPLETED |
| `src/common/views/tasks.py` | StaffTask (65x), Event | High | 🔄 STARTED |
| `src/common/views/management.py` | StaffTask, Event, ProjectWorkflow | High | ⏳ PENDING |
| `src/common/views/dashboard.py` | Event | Medium | ⏳ PENDING |
| `src/common/views/coordination.py` | Event, ProjectWorkflow | Medium | ⏳ PENDING |
| `src/common/views/attendance.py` | Event | Low | ⏳ PENDING |
| `src/common/views.py` | Event | Medium | ⏳ PENDING |

### Category 2: PROJECT_CENTRAL SERVICES (Priority: HIGH)

| File | Legacy Imports | Complexity | Status |
|------|---------------|------------|--------|
| `src/project_central/views.py` | StaffTask, Event | Medium | ⏳ PENDING |
| `src/project_central/services/workflow_service.py` | StaffTask, ProjectWorkflow | High | ⏳ PENDING |
| `src/project_central/services/approval_service.py` | StaffTask | Low | ⏳ PENDING |
| `src/project_central/services/report_generator.py` | ProjectWorkflow | Low | ⏳ PENDING |
| `src/project_central/services/alert_service.py` | ProjectWorkflow | Low | ⏳ PENDING |
| `src/project_central/services/analytics_service.py` | ProjectWorkflow | Low | ⏳ PENDING |
| `src/project_central/tasks.py` | ProjectWorkflow | Medium | ⏳ PENDING |

### Category 3: COORDINATION MODULE (Priority: HIGH)

| File | Legacy Imports | Complexity | Status |
|------|---------------|------------|--------|
| `src/coordination/views.py` | StaffTask, Event, ProjectWorkflow | High | ⏳ PENDING |
| `src/coordination/models.py` | StaffTask (circular import) | Low | ⏳ PENDING |
| `src/coordination/signals.py` | ProjectWorkflow | Low | ⏳ PENDING |
| `src/coordination/forms.py` | RecurringEventPattern, ProjectWorkflow | Medium | ⏳ PENDING |

### Category 4: MONITORING & ADMIN (Priority: MEDIUM)

| File | Legacy Imports | Complexity | Status |
|------|---------------|------------|--------|
| `src/monitoring/admin.py` | StaffTask | Low | ⏳ PENDING |
| `src/monitoring/serializers.py` | StaffTask | Low | ⏳ PENDING |
| `src/monitoring/tasks.py` | StaffTask | Low | ⏳ PENDING |

### Category 5: COMMON SERVICES (Priority: MEDIUM)

| File | Legacy Imports | Complexity | Status |
|------|---------------|------------|--------|
| `src/common/services/task_automation.py` | StaffTask | Medium | ⏳ PENDING |
| `src/common/services/resource_bookings.py` | StaffTask | Low | ⏳ PENDING |
| `src/common/signals.py` | Event | Low | ⏳ PENDING |
| `src/common/tasks.py` | Event | Low | ⏳ PENDING |

### Category 6: MODELS & PROXIES (Priority: MEDIUM)

| File | Legacy Imports | Complexity | Status |
|------|---------------|------------|--------|
| `src/common/models/proxies.py` | Event, ProjectWorkflow | Low | ⏳ PENDING |
| `src/project_central/models.py` | StaffTask (circular import) | Low | ⏳ PENDING |

### Category 7: TEST FILES (Priority: LOW)

| File | Legacy Imports | Complexity | Status |
|------|---------------|------------|--------|
| `src/tests/*.py` | Multiple | Varies | ⏳ PENDING |
| `src/common/tests/*.py` | Multiple | Varies | ⏳ PENDING |

### Category 8: EXCLUDED (Migration Commands - DO NOT REFACTOR)

These files MUST retain legacy imports for data migration purposes:

- ❌ `src/common/management/commands/migrate_staff_tasks.py`
- ❌ `src/common/management/commands/migrate_events.py`
- ❌ `src/common/management/commands/migrate_project_workflows.py`
- ❌ `src/common/management/commands/migrate_to_workitem.py`
- ❌ `src/common/management/commands/verify_workitem_migration.py`
- ❌ `src/common/management/commands/populate_task_templates.py`

---

## Refactoring Patterns

### 1. Import Statements

#### StaffTask → WorkItem
```python
# OLD:
from common.models import StaffTask

# NEW:
from common.models import WorkItem
```

#### Event → WorkItem (Activity)
```python
# OLD:
from coordination.models import Event

# NEW:
from common.models import WorkItem
# Note: Event is now deprecated, use WorkItem with work_type='activity'
```

#### ProjectWorkflow → WorkItem (Project)
```python
# OLD:
from project_central.models import ProjectWorkflow

# NEW:
from common.models import WorkItem
# Note: ProjectWorkflow is now deprecated, use WorkItem with work_type='project'
```

### 2. Model Creation

#### Tasks
```python
# OLD:
task = StaffTask.objects.create(
    title="Review policy draft",
    status="in_progress",
    priority="high"
)

# NEW:
task = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    title="Review policy draft",
    status=WorkItem.STATUS_IN_PROGRESS,
    priority=WorkItem.PRIORITY_HIGH
)
```

#### Activities (formerly Events)
```python
# OLD:
event = Event.objects.create(
    title="Community Workshop",
    event_type="workshop",
    start_date=date(2025, 10, 15)
)

# NEW:
activity = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_ACTIVITY,
    title="Community Workshop",
    start_date=date(2025, 10, 15)
)
# Store event_type in activity_data
activity.activity_data = {"event_type": "workshop"}
activity.save()

# OR use property setter:
activity.event_type = "workshop"
activity.save()
```

#### Projects (formerly ProjectWorkflow)
```python
# OLD:
project = ProjectWorkflow.objects.create(
    title="Infrastructure Assessment",
    current_stage="need_identification"
)

# NEW:
project = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_PROJECT,
    title="Infrastructure Assessment"
)
# Use property setter:
project.workflow_stage = "need_identification"
project.save()
```

### 3. Model Queries

#### Filtering Tasks
```python
# OLD:
tasks = StaffTask.objects.filter(status="in_progress")

# NEW:
tasks = WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK],
    status=WorkItem.STATUS_IN_PROGRESS
)
```

#### Filtering Activities
```python
# OLD:
events = Event.objects.filter(start_date__gte=today)

# NEW:
activities = WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY],
    start_date__gte=today
)
```

#### Filtering Projects
```python
# OLD:
projects = ProjectWorkflow.objects.filter(status="active")

# NEW:
projects = WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT],
    status=WorkItem.STATUS_IN_PROGRESS
)
```

### 4. Constants Mapping

#### Status Constants
```python
# OLD → NEW
StaffTask.STATUS_NOT_STARTED   → WorkItem.STATUS_NOT_STARTED
StaffTask.STATUS_IN_PROGRESS   → WorkItem.STATUS_IN_PROGRESS
StaffTask.STATUS_AT_RISK       → WorkItem.STATUS_AT_RISK
StaffTask.STATUS_COMPLETED     → WorkItem.STATUS_COMPLETED
StaffTask.STATUS_BLOCKED       → WorkItem.STATUS_BLOCKED

# WorkItem has additional statuses:
WorkItem.STATUS_CANCELLED
```

#### Priority Constants
```python
# OLD → NEW
StaffTask.PRIORITY_LOW         → WorkItem.PRIORITY_LOW
StaffTask.PRIORITY_MEDIUM      → WorkItem.PRIORITY_MEDIUM
StaffTask.PRIORITY_HIGH        → WorkItem.PRIORITY_HIGH

# WorkItem has additional priorities:
WorkItem.PRIORITY_URGENT
WorkItem.PRIORITY_CRITICAL
```

#### Choices
```python
# OLD → NEW
StaffTask.STATUS_CHOICES       → WorkItem.STATUS_CHOICES
StaffTask.PRIORITY_CHOICES     → WorkItem.PRIORITY_CHOICES
```

### 5. Domain-Specific Data

#### Tasks with Domain
```python
# OLD:
task = StaffTask.objects.create(
    title="Conduct needs assessment",
    domain="mana",
    assessment_phase="planning"
)

# NEW:
task = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    title="Conduct needs assessment"
)
# Use domain property (backward compatible):
task.domain = "mana"
# Store phase in task_data:
task.task_data = {"assessment_phase": "planning"}
task.save()

# OR more explicitly:
task = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    title="Conduct needs assessment",
    task_data={
        "domain": "mana",
        "assessment_phase": "planning"
    }
)
```

#### Query by Domain
```python
# OLD:
tasks = StaffTask.objects.filter(domain="mana")

# NEW (using JSON field query):
tasks = WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK],
    task_data__domain="mana"
)

# OR using property in code:
all_tasks = WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
)
mana_tasks = [task for task in all_tasks if task.domain == "mana"]
```

### 6. Foreign Key Relationships

#### Legacy ForeignKey to Event/StaffTask
```python
# OLD:
class MonitoringEntry(models.Model):
    linked_event = models.ForeignKey(Event, ...)
    related_task = models.ForeignKey(StaffTask, ...)

# NEW:
class MonitoringEntry(models.Model):
    # Option 1: Generic Foreign Key
    work_item = GenericForeignKey('content_type', 'object_id')

    # Option 2: Direct FK to WorkItem
    linked_work_item = models.ForeignKey(WorkItem, ...)
```

---

## Completed Refactorings

### ✅ `src/common/views/calendar_api.py`

**Changes Made:**
1. ✅ Import: `from common.models import StaffTask` → `from common.models import WorkItem`
2. ✅ Import: `from coordination.models import Event` → (removed, using WorkItem)
3. ✅ Event queries → WorkItem with `work_type__in=[WORK_TYPE_ACTIVITY, WORK_TYPE_SUB_ACTIVITY]`
4. ✅ StaffTask queries → WorkItem with `work_type__in=[WORK_TYPE_TASK, WORK_TYPE_SUBTASK]`
5. ✅ Updated permission checks: `coordination.change_event` → `common.change_workitem`
6. ✅ Field mappings: `event.end_date` → `activity.due_date`
7. ✅ JSON field usage: `activity.activity_data['duration_hours']`

**Lines Changed:** 15
**Testing Status:** Syntax validated ✅

---

## Refactoring Strategy

### Phase 1: High-Priority Production Files (CURRENT)
1. ✅ `common/views/calendar_api.py` - COMPLETED
2. ⏳ `common/views/management.py` - IN PROGRESS
3. ⏳ `common/views/tasks.py` - STARTED (65 occurrences - high complexity)
4. ⏳ `coordination/views.py`
5. ⏳ `project_central/views.py`

### Phase 2: Services Layer
1. ⏳ `common/services/task_automation.py`
2. ⏳ `common/services/resource_bookings.py`
3. ⏳ `project_central/services/*.py`

### Phase 3: Admin & Serializers
1. ⏳ `monitoring/admin.py`
2. ⏳ `monitoring/serializers.py`
3. ⏳ `monitoring/tasks.py`

### Phase 4: Forms & Signals
1. ⏳ `coordination/forms.py`
2. ⏳ `coordination/signals.py`
3. ⏳ `common/signals.py`
4. ⏳ `common/tasks.py`

### Phase 5: Test Files (Lower Priority)
1. ⏳ `tests/*.py`
2. ⏳ `common/tests/*.py`
3. ⏳ `coordination/tests/*.py`
4. ⏳ `project_central/tests/*.py`

---

## Automation Tools

### Refactoring Script
**Location:** `/refactor_legacy_models.py`

**Usage:**
```bash
# Preview changes
python3 refactor_legacy_models.py --dry-run

# Apply changes
python3 refactor_legacy_models.py
```

**Features:**
- Automated import replacement
- Constants mapping
- Query pattern refactoring
- Excludes migration commands
- Dry-run mode for safety

**Limitations:**
- Simple regex-based (may miss complex cases)
- Requires manual review of changes
- May not handle all edge cases
- Foreign key migrations need manual intervention

**Recommendation:** Use as a starting point, then manually review and refine each file.

---

## Testing Strategy

### Pre-Refactoring Checklist
- [ ] Backup database: `cp src/db.sqlite3 src/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)`
- [ ] Create git branch: `git checkout -b refactor/legacy-models-to-workitem`
- [ ] Run existing tests: `pytest src/ -v`
- [ ] Document baseline test results

### Post-Refactoring Validation
- [ ] Syntax check all modified files: `python3 -m py_compile <file>`
- [ ] Import test: Ensure no circular imports
- [ ] Unit tests: `pytest src/common/tests/ -v`
- [ ] Integration tests: `pytest src/tests/ -v`
- [ ] Manual testing: Calendar drag-drop, task creation, filtering
- [ ] Performance regression: Check query performance
- [ ] Browser testing: Test HTMX interactions

### Critical Test Cases
1. **Task Creation:** Create tasks via UI and API
2. **Activity Creation:** Create activities (formerly events)
3. **Project Creation:** Create projects (formerly workflows)
4. **Calendar Integration:** Drag-drop, filtering, display
5. **Domain Filtering:** Task queries by domain
6. **Status Updates:** Status transitions, progress tracking
7. **Assignment:** Assignee/team management
8. **Hierarchies:** Parent-child relationships

---

## Risks & Mitigation

### Risk 1: Breaking Existing Functionality
**Severity:** HIGH
**Probability:** MEDIUM
**Mitigation:**
- Comprehensive testing before deployment
- Gradual rollout (file by file, not all at once)
- Feature flags for new WorkItem-based views
- Maintain legacy views temporarily as fallback

### Risk 2: Database Inconsistencies
**Severity:** HIGH
**Probability:** LOW
**Mitigation:**
- Migration scripts already completed
- Data verification commands available
- Database backups before refactoring

### Risk 3: Performance Regression
**Severity:** MEDIUM
**Probability:** LOW
**Mitigation:**
- WorkItem has proper indexes
- Query optimization for JSON field filters
- Performance tests in place

### Risk 4: Frontend Breaking Changes
**Severity:** MEDIUM
**Probability:** MEDIUM
**Mitigation:**
- HTMX templates may reference legacy IDs
- JavaScript calendar integration needs update
- Template variable names may need adjustment

### Risk 5: Circular Import Issues
**Severity:** LOW
**Probability:** LOW
**Mitigation:**
- Use lazy imports where needed
- Move imports into function scope if circular
- Proper app dependency ordering

---

## Dependencies & Blockers

### Prerequisites
- ✅ WorkItem model implemented and migrated
- ✅ Backward compatibility properties (domain, workflow_stage, event_type)
- ✅ Data migration scripts completed
- ✅ Proxy models available (StaffTaskProxy, etc.)

### Blockers
- ⚠️ **DOMAIN_CHOICES constant:** StaffTask.DOMAIN_CHOICES not in WorkItem
  - **Solution:** Define centrally or keep in legacy constants
- ⚠️ **Form classes:** StaffTaskForm may need refactoring
  - **Solution:** Create WorkItemForm or update existing forms
- ⚠️ **Templates:** May reference {{ task.domain }} assuming direct field
  - **Solution:** Test templates with WorkItem (property should work)

---

## Next Steps

### Immediate (Next Session)
1. Complete `common/views/management.py` refactoring
2. Complete `common/views/tasks.py` refactoring
3. Refactor `coordination/views.py`
4. Run syntax checks on all modified files
5. Document any patterns not covered by automation

### Short-Term (Next 2-3 Sessions)
1. Refactor all project_central services
2. Refactor monitoring module files
3. Update forms to use WorkItem
4. Run comprehensive test suite
5. Fix any test failures

### Medium-Term
1. Refactor all test files
2. Remove deprecated views (mark for deletion)
3. Update documentation
4. Create migration guide for future developers

### Long-Term
1. Remove proxy models once all code migrated
2. Delete legacy model definitions (after backup)
3. Update API documentation
4. Performance optimization if needed

---

## Success Criteria

### Code Quality
- [ ] Zero legacy model imports in production code (except migration commands)
- [ ] All syntax errors resolved
- [ ] No circular imports
- [ ] Code follows project standards (CLAUDE.md)

### Functionality
- [ ] All existing features work identically
- [ ] Calendar integration functional
- [ ] Task/Activity/Project CRUD operations work
- [ ] Domain filtering works correctly
- [ ] HTMX interactions smooth

### Testing
- [ ] Unit tests: 100% passing
- [ ] Integration tests: 100% passing
- [ ] Manual QA: All critical paths tested
- [ ] Performance: No significant regression

### Documentation
- [ ] This refactoring report updated
- [ ] Code comments added where complex
- [ ] Migration guide created
- [ ] Changelog updated

---

## Lessons Learned

### What Worked Well
1. ✅ Comprehensive analysis before refactoring
2. ✅ Categorizing files by priority
3. ✅ Automated script for pattern detection
4. ✅ WorkItem backward compatibility properties

### Challenges
1. ⚠️ High volume of files (40+)
2. ⚠️ Complex domain-specific logic
3. ⚠️ DOMAIN_CHOICES constants not in WorkItem
4. ⚠️ Some files marked DEPRECATED but still in use

### Recommendations
1. 📝 Consider incremental refactoring over time
2. 📝 Add deprecation warnings to legacy views
3. 📝 Create WorkItem admin interface improvements
4. 📝 Consider creating domain constants in WorkItem model

---

## References

- **WorkItem Model:** `src/common/work_item_model.py`
- **Proxy Models:** `src/common/models/proxies.py`
- **Migration Docs:** `docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md`
- **Refactoring Script:** `/refactor_legacy_models.py`

---

**Report Status:** LIVING DOCUMENT
**Last Updated:** 2025-10-05
**Next Review:** After Phase 1 completion
