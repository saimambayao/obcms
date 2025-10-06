# Legacy Task Tests - SKIPPED

## Overview

This document explains why several task-related test files have been skipped and what would be needed to migrate them to the current OBCMS architecture.

## Summary

**Date Skipped:** October 5, 2025

**Reason:** All skipped tests depend on TaskTemplate and TaskTemplateItem models which were never implemented in the OBCMS codebase. Additionally, these tests use the legacy StaffTask model which is being replaced by the WorkItem unified activity model.

## Skipped Test Files

| File | Lines | Tests | Reason | Priority |
|------|-------|-------|--------|----------|
| `test_task_automation.py.skip` | ~400 | Template automation | TaskTemplate not implemented | LOW |
| `test_task_models.py.skip` | 574 | StaffTask & Template models | TaskTemplate not implemented | LOW |
| `test_task_signals.py.skip` | 656 | Auto-task creation signals | TaskTemplate not implemented | LOW |
| `test_task_integration.py.skip` | 600 | End-to-end workflows | TaskTemplate not implemented | MEDIUM |
| `test_task_views_extended.py.skip` | 704 | Domain/analytics/template views | Mixed - some views exist, templates don't | MEDIUM |

**Total:** 5 test files, ~2,934 lines of test code

## Missing Models

### TaskTemplate
**Status:** Never implemented
**Purpose:** Reusable task templates for automated task generation
**Expected Location:** `src/common/models/task_template.py` or `src/common/models.py`

**Expected Structure:**
```python
class TaskTemplate(models.Model):
    name = models.CharField(max_length=200, unique=True)
    domain = models.CharField(max_length=50, choices=StaffTask.DOMAIN_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### TaskTemplateItem
**Status:** Never implemented
**Purpose:** Individual task items within a template
**Expected Location:** `src/common/models/task_template.py` or `src/common/models.py`

**Expected Structure:**
```python
class TaskTemplateItem(models.Model):
    template = models.ForeignKey(TaskTemplate, related_name='items', on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    sequence = models.PositiveIntegerField()
    days_from_start = models.IntegerField(default=0)
    priority = models.CharField(max_length=20, choices=StaffTask.PRIORITY_CHOICES)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    assessment_phase = models.CharField(max_length=50, blank=True)
    policy_phase = models.CharField(max_length=50, blank=True)
    service_phase = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['sequence']
```

## Migration Status by Test File

### 1. test_task_automation.py.skip
**What it tests:**
- Automatic task generation from templates
- Task scheduling based on template sequences
- Template context variable substitution

**Migration complexity:** HIGH - Entire feature doesn't exist
**Value:** LOW - Manual task creation works fine
**Decision needed:** Should template automation be implemented at all?

---

### 2. test_task_models.py.skip
**What it tests:**
- StaffTask domain logic (MANA, Coordination, Policy, etc.)
- StaffTask validation rules
- StaffTask phase fields (assessment_phase, policy_phase, service_phase)
- TaskTemplate CRUD operations
- TaskTemplateItem ordering and relationships

**Migration complexity:** MEDIUM
**Value:** MEDIUM - Domain validation tests are useful
**Recommendation:**
- Migrate StaffTask domain tests to WorkItem
- Skip TaskTemplate tests unless feature is implemented

---

### 3. test_task_signals.py.skip
**What it tests:**
- Auto-task creation when Assessment is created
- Auto-task creation when Event is created
- Auto-task creation when Policy is created
- Auto-task creation when Partnership is created
- Auto-task creation for service applications
- Monitoring entry progress synchronization

**Migration complexity:** HIGH
**Value:** MEDIUM - IF template automation is implemented
**Current workaround:** Tasks are created manually
**Recommendation:**
- Keep skipped until template system is decided
- Progress sync tests might be valuable - consider extracting

---

### 4. test_task_integration.py.skip
**What it tests:**
- Complete assessment workflow (create → auto-generate tasks → assign → complete)
- Event task workflow
- Policy development workflow
- Template browsing and instantiation
- Kanban board drag-and-drop
- Multi-domain analytics

**Migration complexity:** MEDIUM-HIGH
**Value:** HIGH - Integration tests are very valuable
**Recommendation:**
- **HIGH PRIORITY** - These tests should be migrated!
- Rewrite to use WorkItem instead of StaffTask
- Remove template-specific tests
- Keep kanban and analytics tests (these features exist)

**Note:** WorkItem integration tests may already exist at `src/common/tests/test_work_item_integration.py`

---

### 5. test_task_views_extended.py.skip
**What it tests:**
- Domain-filtered task views (e.g., `/tasks/domain/mana/`)
- Assessment-specific task views with phase grouping
- Event-specific task views
- Policy-specific task views
- Task analytics dashboard
- Enhanced personal dashboard
- Template list/detail/instantiate views

**Migration complexity:** MEDIUM
**Value:** HIGH for non-template views, LOW for template views
**Recommendation:**
- Verify which views still exist in `src/common/urls.py`
- Migrate tests for existing views to use WorkItem
- Delete template view tests

## Current Test Coverage

### Existing WorkItem Tests
The codebase already has WorkItem-specific tests that may cover similar functionality:

```
src/common/tests/
├── test_work_item_model.py          # WorkItem model tests
├── test_work_item_views.py          # WorkItem view tests
├── test_work_item_integration.py    # WorkItem integration tests
├── test_work_item_calendar.py       # Calendar integration
├── test_work_item_factories.py      # Test factories
├── test_work_item_migration.py      # Migration tests
└── test_work_item_performance.py    # Performance tests
```

**Recommendation:** Review these files to see if they already cover what the legacy tests attempted to test.

## What Functionality Actually Exists?

| Feature | Exists? | Model | Notes |
|---------|---------|-------|-------|
| Task management | ✅ Yes | WorkItem | Unified model for all activities |
| Domain categorization | ✅ Yes | WorkItem.activity_type | Replaces StaffTask.domain |
| Assessment tasks | ✅ Yes | WorkItem | Links to assessments |
| Event tasks | ✅ Yes | WorkItem | Links to events |
| Policy tasks | ✅ Yes | WorkItem | Links to policies |
| Task templates | ❌ No | N/A | Never implemented |
| Auto-task creation | ❌ No | N/A | Never implemented |
| Kanban board | ✅ Yes | WorkItem | Staff task board exists |
| Analytics | ✅ Yes | WorkItem | Task analytics dashboard exists |
| Phase tracking | ❓ Unknown | WorkItem | Needs verification |

## Recommendations

### Immediate Actions (Completed ✅)
1. ✅ Rename all 5 test files to `.skip` extension
2. ✅ Create README for each file explaining why it's skipped
3. ✅ Create this summary document

### Short-term (Next Sprint)
1. **Verify URL patterns** - Check which views in these tests actually exist
2. **Review WorkItem tests** - Determine if existing tests cover the same ground
3. **Extract valuable tests** - If monitoring sync tests are useful, extract them

### Medium-term (Next Quarter)
1. **Migrate integration tests** - Rewrite `test_task_integration.py` for WorkItem
2. **Migrate view tests** - Rewrite `test_task_views_extended.py` for existing views
3. **Delete template tests** - Unless template feature is approved

### Long-term (Future Consideration)
1. **Decide on templates** - Should TaskTemplate system be implemented?
2. **If yes:** Implement models, views, signals, then restore template tests
3. **If no:** Delete all template-related test files permanently

## Decision Needed: Task Templates

**Question:** Should OBCMS implement a TaskTemplate system for automated task generation?

**Pros:**
- Standardized workflows for common activities (assessments, events, policies)
- Consistent task creation across teams
- Reduced manual task setup time
- Enforced best practices through templates

**Cons:**
- Significant development effort (models, views, signals, admin)
- Added complexity to the system
- Current manual approach works fine
- WorkItem model may already provide sufficient flexibility

**Current Status:** Feature was planned but never implemented. All 5 test files were written assuming this feature would exist, but it never did.

**Recommendation:** Discuss with product owner whether template automation provides enough value to justify implementation effort.

## Test File Details

For detailed information about each skipped test file, see:
- `test_task_automation.py.README.md`
- `test_task_models.py.README.md`
- `test_task_signals.py.README.md`
- `test_task_integration.py.README.md`
- `test_task_views_extended.py.README.md`

## Running Tests

To verify pytest runs without import errors:
```bash
cd src
pytest common/tests/ -v --tb=short
```

The skipped files will not be discovered by pytest (they end in `.skip` instead of `.py`).

## Related Documentation

- **WorkItem Model:** `src/common/models/work_item.py`
- **WorkItem Migration:** `WORKITEM_MIGRATION_COMPLETE.md` (project root)
- **Legacy Tasks:** `src/common/legacy/` (deprecated implementations)

## Contact

For questions about these skipped tests or the decision on TaskTemplate implementation, contact the development team.

---

**Last Updated:** October 5, 2025
**Status:** All legacy task tests documented and skipped
**Next Review:** Q1 2026 (decide on template system)
