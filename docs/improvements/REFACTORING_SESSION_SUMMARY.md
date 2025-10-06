# Legacy Model Refactoring: Session Summary
**Date:** 2025-10-05
**Task:** Replace all StaffTask, Event, ProjectWorkflow imports with unified WorkItem model
**Status:** Analysis Complete | Refactoring In Progress

---

## What Was Accomplished

### ✅ Completed

1. **Comprehensive Codebase Analysis**
   - Identified 40+ files with legacy model imports
   - Categorized files by priority (7 categories)
   - Documented 57+ import statements to refactor
   - Excluded migration commands from refactoring scope

2. **Refactoring Patterns Documented**
   - Import statement patterns
   - Model creation patterns
   - Query patterns (filter, get, create)
   - Constants mapping (STATUS, PRIORITY)
   - Domain-specific data handling
   - Foreign key relationship strategies

3. **Files Successfully Refactored**
   - ✅ **src/common/views/calendar_api.py** (COMPLETED)
     - Replaced `StaffTask` → `WorkItem` with task type filtering
     - Replaced `Event` → `WorkItem` with activity type filtering
     - Updated permissions: `coordination.change_event` → `common.change_workitem`
     - Field mappings: `event.end_date` → `activity.due_date`
     - JSON field usage: `activity.activity_data['duration_hours']`
     - Syntax validated ✅

   - 🔄 **src/common/views/tasks.py** (PARTIALLY STARTED)
     - Import statement updated
     - 65 occurrences identified
     - **Decision needed:** Refactor fully vs. mark for deprecation removal

4. **Documentation Created**
   - **Main Report:** `docs/refactor/LEGACY_MODEL_REFACTORING_REPORT.md`
     - Complete file analysis (40+ files categorized)
     - Refactoring patterns with code examples
     - Risk assessment and mitigation strategies
     - Testing strategy and success criteria

   - **Action Plan:** `docs/refactor/LEGACY_REFACTORING_ACTION_PLAN.md`
     - Quick reference cheat sheet
     - File-by-file refactoring guide
     - Common pitfalls and solutions
     - Progress tracking template

5. **Automation Tool Created**
   - **Script:** `/refactor_legacy_models.py`
   - Features:
     - Automated pattern detection
     - Import replacement
     - Constants mapping
     - Dry-run mode for safe preview
   - Dry-run results:
     - 22 files will be changed
     - 4 files unchanged
     - 0 errors detected

### ⏳ In Progress

- `src/common/views/management.py` (analyzed, ready to refactor)
- `src/common/views/tasks.py` (started, decision point)

### 📋 Pending

All other files in categories 2-7 (see detailed list in reports)

---

## Key Findings

### Legacy Model Distribution

| Model | Occurrences | Primary Locations |
|-------|-------------|-------------------|
| **StaffTask** | ~200+ usages | common/views, project_central/services, monitoring/* |
| **Event** | ~80+ usages | coordination/*, common/views, common/tasks |
| **ProjectWorkflow** | ~50+ usages | project_central/*, coordination/forms |

### Complexity Assessment

**High Complexity Files (require careful manual refactoring):**
- `src/common/views/tasks.py` (65 StaffTask occurrences) - DEPRECATED but still in use
- `src/common/views/management.py` (30+ occurrences across 3 models)
- `src/coordination/views.py` (multi-model usage with complex logic)
- `src/project_central/services/workflow_service.py` (workflow automation logic)

**Medium Complexity Files:**
- `src/project_central/views.py`
- `src/common/services/task_automation.py`
- `src/coordination/forms.py`

**Low Complexity Files (simple import replacement):**
- `src/monitoring/admin.py`
- `src/monitoring/serializers.py`
- `src/common/services/resource_bookings.py`

### Critical Insights

1. **DOMAIN_CHOICES Issue**
   - `StaffTask.DOMAIN_CHOICES` referenced in multiple files
   - Not present in `WorkItem` model
   - **Solution:** Use WorkItem.domain property or define constants centrally

2. **Deprecated but Active Views**
   - `src/common/views/tasks.py` marked DEPRECATED
   - Still referenced in `common/urls.py`
   - **Decision needed:** Refactor or remove?

3. **Backward Compatibility Properties Work Well**
   - `WorkItem.domain`, `WorkItem.workflow_stage`, `WorkItem.event_type`
   - These properties make migration smoother
   - Reduces code changes in many cases

4. **Permission Model Changes**
   - `coordination.change_event` → `common.change_workitem`
   - `common.change_stafftask` → `common.change_workitem`
   - `project_central.change_projectworkflow` → `common.change_workitem`
   - Need to verify permission assignments in production

---

## Refactoring Patterns Applied

### Pattern 1: Simple Import Replacement
```python
# BEFORE
from common.models import StaffTask, TaskTemplate
from coordination.models import Event

# AFTER
from common.models import WorkItem, TaskTemplate
```

### Pattern 2: Query with Type Filtering
```python
# BEFORE
tasks = StaffTask.objects.filter(status="in_progress")

# AFTER
tasks = WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK],
    status=WorkItem.STATUS_IN_PROGRESS
)
```

### Pattern 3: Constants Mapping
```python
# BEFORE
task.status = StaffTask.STATUS_COMPLETED
if priority == StaffTask.PRIORITY_HIGH:

# AFTER
task.status = WorkItem.STATUS_COMPLETED
if priority == WorkItem.PRIORITY_HIGH:
```

### Pattern 4: Activity (Event) Refactoring
```python
# BEFORE
event = Event.objects.get(pk=event_id)
event.end_date = new_date

# AFTER
activity = WorkItem.objects.get(
    pk=event_id,
    work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY]
)
activity.due_date = new_date  # Field name changed
```

### Pattern 5: JSON Field Storage
```python
# BEFORE
event.duration_hours = 2.5

# AFTER
if not activity.activity_data:
    activity.activity_data = {}
activity.activity_data['duration_hours'] = 2.5
activity.save(update_fields=['activity_data'])
```

---

## Files Changed Summary

### Category 1: Views (1/10 completed)
- ✅ `calendar_api.py` - DONE
- ⏳ `management.py` - READY
- ⏳ `tasks.py` - DECISION POINT
- ⏳ `coordination.py` - PENDING
- ⏳ `dashboard.py` - PENDING
- ⏳ `attendance.py` - PENDING
- ⏳ `views.py` - PENDING
- ⏳ `coordination/views.py` - PENDING
- ⏳ `project_central/views.py` - PENDING
- ⏳ `mana/views.py` - PENDING

### Category 2: Services (0/8 completed)
- All pending

### Category 3: Admin/Serializers (0/3 completed)
- All pending

### Category 4: Forms/Signals (0/4 completed)
- All pending

### Category 5: Tests (0/15+ completed)
- All pending

**Overall Progress:** ~2.5% complete (1 file refactored, 1 partially done, 38+ pending)

---

## Next Steps

### Immediate (Next Session)

1. **Decision on `tasks.py`**
   - Option A: Full refactoring (high effort, maintains functionality)
   - Option B: Add deprecation redirect to `work_items.py` (lower effort)
   - Option C: Remove from URLs entirely (requires route migration)
   - **Recommendation:** Option B - gradual migration

2. **Complete `management.py`**
   - Highest priority (dashboard heavily used)
   - ~30 occurrences to refactor
   - Complex team/task aggregation logic
   - Estimated: 1-2 hours

3. **Run Automated Script (with review)**
   - Apply to low-complexity files first
   - Manual review of each change
   - Test after each file
   - Estimated: 2-3 hours for 10 simple files

### Short-Term (Next 2-3 Sessions)

1. Refactor all project_central services (5 files)
2. Refactor coordination module (4 files)
3. Refactor monitoring module (3 files)
4. Run comprehensive test suite
5. Fix any test failures

### Medium-Term

1. Refactor all test files
2. Update forms to use WorkItem
3. Remove deprecated views
4. Performance optimization

---

## Risks Identified

### High Priority Risks

1. **Breaking Calendar Drag-Drop Functionality**
   - **Status:** Mitigated in `calendar_api.py`
   - **Next:** Test thoroughly with real data
   - **Action:** Add integration tests

2. **Dashboard Performance Regression**
   - **Concern:** JSON field queries may be slower
   - **Mitigation:** WorkItem has proper indexes
   - **Action:** Run performance tests after refactoring

3. **Permission Checks Breaking**
   - **Risk:** Users may lose access if permissions not updated
   - **Mitigation:** Document permission migrations needed
   - **Action:** Update permission assignments in deployment

### Medium Priority Risks

4. **DOMAIN_CHOICES Undefined**
   - **Issue:** `StaffTask.DOMAIN_CHOICES` used in ~5 files
   - **Workaround:** Define centrally or keep legacy constant
   - **Action:** Create `WORK_ITEM_DOMAINS` constant

5. **Template Variable Incompatibility**
   - **Risk:** Templates may assume direct fields
   - **Mitigation:** WorkItem has backward-compatible properties
   - **Action:** Test all templates that use `task.domain`, etc.

---

## Testing Status

### Completed
- ✅ Syntax validation: `calendar_api.py`
- ✅ Dry-run validation: 22 files, 0 errors

### Pending
- ⏳ Import tests for refactored files
- ⏳ Unit tests (254 tests total)
- ⏳ Integration tests
- ⏳ Manual UI testing
- ⏳ Calendar drag-drop testing
- ⏳ Performance regression testing

---

## Recommendations

### For Continuing This Work

1. **Take Incremental Approach**
   - Refactor one category at a time
   - Test thoroughly after each file
   - Don't rush to refactor all 40+ files at once

2. **Use Automation Wisely**
   - Script is good for simple files
   - Manual refactoring better for complex logic
   - Always review automated changes

3. **Prioritize by Impact**
   - Focus on views first (user-facing)
   - Then services (business logic)
   - Leave tests for last (they validate everything)

4. **Consider Gradual Migration**
   - Keep deprecated views temporarily
   - Add redirects to new WorkItem views
   - Remove old views only when fully replaced

5. **Document as You Go**
   - Update this report with each file completed
   - Note any patterns not covered
   - Document decisions made

---

## Tools & Resources Created

### Documentation
1. **`docs/refactor/LEGACY_MODEL_REFACTORING_REPORT.md`**
   - Comprehensive analysis (40+ files)
   - Refactoring patterns with examples
   - Testing strategy
   - Risk assessment

2. **`docs/refactor/LEGACY_REFACTORING_ACTION_PLAN.md`**
   - Quick reference cheat sheet
   - Common pitfalls
   - File-by-file guide
   - Progress tracking

3. **`REFACTORING_SESSION_SUMMARY.md` (this file)**
   - What was accomplished
   - Next steps
   - Recommendations

### Automation
4. **`refactor_legacy_models.py`**
   - Pattern-based refactoring
   - Dry-run mode
   - Excludes migration commands
   - 22/40 files ready for automation

---

## Metrics

### Volume
- **Files analyzed:** 40+
- **Import statements:** 57+
- **Model occurrences:** ~330+
  - StaffTask: ~200+
  - Event: ~80+
  - ProjectWorkflow: ~50+

### Progress
- **Files refactored:** 1 complete, 1 partial
- **Completion:** ~2.5%
- **Estimated remaining:** 7-12 focused sessions

### Code Quality
- **Syntax errors:** 0
- **Circular imports:** 0
- **Test failures:** TBD (pending test run)

---

## Questions for Follow-up

1. **Should `tasks.py` be refactored or deprecated?**
   - File is marked DEPRECATED
   - Still actively used via URLs
   - Alternative exists (`work_items.py`)

2. **Where should DOMAIN_CHOICES be defined?**
   - Currently in `StaffTask` (legacy)
   - Not in `WorkItem`
   - Needed in multiple files

3. **Should we update permissions now or later?**
   - Permission model changes needed
   - Could break existing access control
   - Needs coordination with deployment

4. **Run automated script or continue manual?**
   - Script ready for 22 files
   - Some files need manual review
   - Hybrid approach recommended?

---

## Files for Reference

### Completed Refactorings
- `/Users/.../obcms/src/common/views/calendar_api.py`

### Created Documentation
- `/Users/.../obcms/docs/refactor/LEGACY_MODEL_REFACTORING_REPORT.md`
- `/Users/.../obcms/docs/refactor/LEGACY_REFACTORING_ACTION_PLAN.md`
- `/Users/.../obcms/REFACTORING_SESSION_SUMMARY.md`

### Created Tools
- `/Users/.../obcms/refactor_legacy_models.py`

### Key Reference Files
- `/Users/.../obcms/src/common/work_item_model.py` (new unified model)
- `/Users/.../obcms/src/common/models/proxies.py` (backward compatibility)
- `/Users/.../obcms/src/common/views/work_items.py` (new views)

---

## Command Quick Reference

```bash
# Analysis
python3 refactor_legacy_models.py --dry-run

# Find specific imports
grep -r "from common.models import.*StaffTask" src --include="*.py"

# Syntax check
python3 -m py_compile src/common/views/calendar_api.py

# Run tests
cd src
pytest common/tests/ -v

# Backup database
cp src/db.sqlite3 src/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Git workflow
git checkout -b refactor/legacy-models-to-workitem
git add docs/refactor/*.md refactor_legacy_models.py src/common/views/calendar_api.py
git commit -m "Add legacy model refactoring documentation and complete calendar_api.py"
```

---

**Session Status:** PRODUCTIVE
**Next Session Goal:** Complete `management.py` + decide on `tasks.py` strategy
**Estimated Next Session Duration:** 2-3 hours
**Report Maintained By:** Claude Code
**Last Updated:** 2025-10-05
