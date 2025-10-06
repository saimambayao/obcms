# Legacy Model Refactoring: Action Plan
## Quick Reference Guide

**Target:** Replace all StaffTask, Event, ProjectWorkflow imports with WorkItem
**Files Affected:** 40+ files across 7 categories
**Estimated Complexity:** HIGH (due to volume and domain-specific logic)

---

## Quick Start

### 1. Review Current State
```bash
# See full analysis
cat docs/refactor/LEGACY_MODEL_REFACTORING_REPORT.md

# Check which files need refactoring
python3 refactor_legacy_models.py --dry-run
```

### 2. Files Already Completed ✅
- `src/common/views/calendar_api.py` ✅

### 3. Next Priority Files ⏳
1. `src/common/views/management.py` (HIGH - used in dashboard)
2. `src/common/views/tasks.py` (HIGH - 65 occurrences, deprecated but still used)
3. `src/coordination/views.py` (HIGH - multi-model usage)
4. `src/project_central/views.py` (HIGH - workflow integration)

---

## Refactoring Cheat Sheet

### Import Changes
```python
# StaffTask
from common.models import StaffTask  # OLD
from common.models import WorkItem   # NEW

# Event
from coordination.models import Event  # OLD
from common.models import WorkItem     # NEW

# ProjectWorkflow
from project_central.models import ProjectWorkflow  # OLD
from common.models import WorkItem                   # NEW
```

### Query Changes
```python
# Tasks
StaffTask.objects.filter(status="in_progress")  # OLD
WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK],
    status=WorkItem.STATUS_IN_PROGRESS
)  # NEW

# Activities (Events)
Event.objects.filter(start_date__gte=today)  # OLD
WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY],
    start_date__gte=today
)  # NEW

# Projects
ProjectWorkflow.objects.filter(status="active")  # OLD
WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT],
    status=WorkItem.STATUS_IN_PROGRESS
)  # NEW
```

### Constants
```python
# Status
StaffTask.STATUS_NOT_STARTED  → WorkItem.STATUS_NOT_STARTED
StaffTask.STATUS_IN_PROGRESS  → WorkItem.STATUS_IN_PROGRESS
StaffTask.STATUS_COMPLETED    → WorkItem.STATUS_COMPLETED

# Priority
StaffTask.PRIORITY_LOW    → WorkItem.PRIORITY_LOW
StaffTask.PRIORITY_MEDIUM → WorkItem.PRIORITY_MEDIUM
StaffTask.PRIORITY_HIGH   → WorkItem.PRIORITY_HIGH
```

### Domain-Specific Data
```python
# OLD: Direct field
task = StaffTask.objects.create(
    title="Assessment",
    domain="mana"
)

# NEW: Property (backward compatible)
task = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    title="Assessment"
)
task.domain = "mana"  # Uses property setter
task.save()

# OR: Explicit JSON
task = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    title="Assessment",
    task_data={"domain": "mana"}
)
```

---

## File-by-File Guide

### Priority 1: Critical Views

#### `src/common/views/management.py`
**Complexity:** HIGH (uses StaffTask, Event, ProjectWorkflow)
**Occurrences:** ~30
**Key Patterns:**
- Dashboard stats queries
- Team task aggregation
- Status filtering

**Refactoring Steps:**
1. Replace imports
2. Update `_build_team_overview()` queries
3. Update status constant references
4. Test dashboard rendering

#### `src/common/views/tasks.py`
**Complexity:** VERY HIGH (65 StaffTask occurrences)
**Status:** DEPRECATED but still used via URLs
**Recommendation:** Consider whether to refactor or remove entirely

**Options:**
- **Option A:** Full refactoring (time-intensive)
- **Option B:** Add deprecation warnings, redirect to work_items.py
- **Option C:** Mark for removal after work_items.py fully replaces it

#### `src/coordination/views.py`
**Complexity:** HIGH (multi-model usage)
**Occurrences:** ~20
**Key Patterns:**
- Event CRUD operations
- Calendar integration
- Stakeholder engagement

**Refactoring Steps:**
1. Replace Event with WorkItem (activity type)
2. Update event_type handling (use activity_data)
3. Update permissions checks
4. Test calendar display

#### `src/project_central/views.py`
**Complexity:** HIGH
**Occurrences:** ~15
**Key Patterns:**
- Project workflow stages
- Task creation from projects
- Status tracking

**Refactoring Steps:**
1. Replace ProjectWorkflow with WorkItem (project type)
2. Update workflow_stage handling (use project_data)
3. Update hierarchy queries
4. Test project dashboard

### Priority 2: Services

#### `src/project_central/services/workflow_service.py`
**Complexity:** MEDIUM
**Key Changes:**
- Task auto-creation logic
- Workflow progression
- Status updates

#### `src/common/services/task_automation.py`
**Complexity:** MEDIUM
**Key Changes:**
- Template instantiation
- Batch task creation

### Priority 3: Admin & Serializers

#### `src/monitoring/admin.py`
**Complexity:** LOW
**Changes:** Simple import replacement

#### `src/monitoring/serializers.py`
**Complexity:** LOW
**Changes:** Model reference updates

---

## Testing Checklist

### Per-File Testing
After refactoring each file:
- [ ] Syntax check: `python3 -m py_compile <file>`
- [ ] Import test: `python3 -c "import module"`
- [ ] Related tests: `pytest src/tests/test_<module>.py -v`

### Integration Testing
After completing a category:
- [ ] Run full test suite: `pytest src/ -v`
- [ ] Manual UI testing of affected features
- [ ] Check for circular imports
- [ ] Performance regression testing

### Final Validation
Before merging:
- [ ] All tests passing
- [ ] No console errors in browser
- [ ] Calendar functionality verified
- [ ] Task/Activity/Project CRUD verified
- [ ] git diff reviewed for unintended changes

---

## Common Pitfalls

### 1. Forgetting work_type Filter
❌ **Wrong:**
```python
tasks = WorkItem.objects.filter(status=WorkItem.STATUS_IN_PROGRESS)
# This gets ALL work items (tasks, activities, projects)!
```

✅ **Correct:**
```python
tasks = WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK],
    status=WorkItem.STATUS_IN_PROGRESS
)
```

### 2. Assuming Direct Fields Exist
❌ **Wrong:**
```python
task = WorkItem.objects.get(id=task_id)
domain = task.domain  # Assumes field
```

✅ **Correct:**
```python
task = WorkItem.objects.get(
    id=task_id,
    work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
)
domain = task.domain  # Uses property (works!)
# OR
domain = task.task_data.get('domain', 'general')
```

### 3. Not Updating Permissions
❌ **Wrong:**
```python
if request.user.has_perm('coordination.change_event'):
    # Old permission
```

✅ **Correct:**
```python
if request.user.has_perm('common.change_workitem'):
    # New unified permission
```

### 4. Forgetting JSON Field Initialization
❌ **Wrong:**
```python
task = WorkItem.objects.create(work_type=WorkItem.WORK_TYPE_TASK, ...)
task.task_data['domain'] = 'mana'  # KeyError if task_data is None!
```

✅ **Correct:**
```python
task = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    task_data={'domain': 'mana'}
)
# OR
if not task.task_data:
    task.task_data = {}
task.task_data['domain'] = 'mana'
```

---

## Files to NEVER Refactor

These migration commands MUST keep legacy imports:
- `src/common/management/commands/migrate_staff_tasks.py`
- `src/common/management/commands/migrate_events.py`
- `src/common/management/commands/migrate_project_workflows.py`
- `src/common/management/commands/migrate_to_workitem.py`
- `src/common/management/commands/verify_workitem_migration.py`
- `src/common/management/commands/populate_task_templates.py`

**Reason:** They need to import legacy models to perform data migration.

---

## Progress Tracking

### Completed ✅
- [x] Analysis and categorization
- [x] Refactoring patterns documented
- [x] Automated script created
- [x] `calendar_api.py` refactored

### In Progress 🔄
- [ ] `management.py` refactoring
- [ ] `tasks.py` analysis (decide refactor vs remove)

### Pending ⏳
- [ ] All coordination module files
- [ ] All project_central files
- [ ] All monitoring files
- [ ] All test files

### Estimated Completion
- **Phase 1 (Critical Views):** 2-3 sessions
- **Phase 2 (Services):** 1-2 sessions
- **Phase 3 (Admin/Serializers):** 1 session
- **Phase 4 (Forms/Signals):** 1 session
- **Phase 5 (Tests):** 2-3 sessions

**Total Estimated:** 7-12 sessions (assuming focused work)

---

## Quick Commands

```bash
# Find all legacy imports
grep -r "from common.models import.*StaffTask" src --include="*.py" | wc -l
grep -r "from coordination.models import.*Event" src --include="*.py" | wc -l
grep -r "from project_central.models import.*ProjectWorkflow" src --include="*.py" | wc -l

# Dry run refactoring script
python3 refactor_legacy_models.py --dry-run

# Check syntax of a file
python3 -m py_compile src/common/views/calendar_api.py

# Run tests for a module
pytest src/common/tests/ -v

# Create backup before major changes
cp src/db.sqlite3 src/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# View git diff
git diff src/common/views/calendar_api.py
```

---

## Support & Resources

- **Full Report:** `docs/refactor/LEGACY_MODEL_REFACTORING_REPORT.md`
- **WorkItem Model:** `src/common/work_item_model.py`
- **Proxy Models:** `src/common/models/proxies.py`
- **Migration Docs:** `docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md`

---

**Document Status:** ACTIVE
**Last Updated:** 2025-10-05
**Owner:** Development Team
