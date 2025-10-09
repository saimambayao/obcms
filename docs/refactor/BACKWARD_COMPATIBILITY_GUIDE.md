# Backward Compatibility Guide - WorkItem Migration

**Phase 4: Backward Compatibility & Proxy Models**
**Status:** ✅ **IMPLEMENTED**
**Date:** 2025-10-05

## Overview

This guide explains how the WorkItem migration maintains backward compatibility with legacy code while enabling a gradual transition to the new unified work hierarchy model.

## Architecture

### Dual-Write System

```
┌─────────────────────────────────────────────────────────────┐
│                    DUAL-WRITE LAYER                          │
│                                                              │
│  Legacy Model     Signals      WorkItem Model               │
│  ────────────    ────────►    ──────────────                │
│  StaffTask       post_save    work_type='task'              │
│  ────────────    ◄────────    ──────────────                │
│                  post_delete                                 │
│                                                              │
│  ProjectWorkflow  ────────►   work_type='project'           │
│                   ◄────────                                  │
│                                                              │
│  Event           ────────►    work_type='activity'          │
│                  ◄────────                                   │
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **Proxy Models** (`src/common/models/proxies.py`)
   - `StaffTaskProxy` - Filters `WorkItem.objects.filter(work_type='task')`
   - `ProjectWorkflowProxy` - Filters `WorkItem.objects.filter(work_type='project')`
   - `EventProxy` - Filters `WorkItem.objects.filter(work_type='activity')`

2. **Dual-Write Signals** (`src/common/signals/workitem_sync.py`)
   - Automatically syncs changes between legacy models and WorkItem
   - Triggered on `post_save`, `pre_delete` signals
   - Controlled by `DUAL_WRITE_ENABLED` feature flag

3. **Feature Flags** (`src/obc_management/settings/base.py`)
   - `USE_WORKITEM_MODEL` - Enable/disable unified WorkItem model
   - `DUAL_WRITE_ENABLED` - Enable/disable automatic syncing
   - `LEGACY_MODELS_READONLY` - Prevent modifications to legacy models

4. **Verification Tool** (`python manage.py verify_workitem_migration`)
   - Checks data integrity between legacy models and WorkItems
   - Reports missing/orphaned/mismatched records
   - Auto-fix mode to resolve inconsistencies

## Feature Flags

### Configuration (.env or environment variables)

```bash
# Phase 4: Backward Compatibility Feature Flags

# Use new WorkItem model (False = legacy models still active)
USE_WORKITEM_MODEL=false

# Enable dual-write (sync legacy ↔ WorkItem)
DUAL_WRITE_ENABLED=true

# Make legacy models read-only
LEGACY_MODELS_READONLY=false

# Auto-fix migration inconsistencies
WORKITEM_MIGRATION_AUTO_FIX=false

# Strict mode (fail on inconsistencies)
WORKITEM_MIGRATION_STRICT_MODE=false
```

### Migration Phases

#### Phase 1: Dual-Write Mode (Current)
```bash
USE_WORKITEM_MODEL=false
DUAL_WRITE_ENABLED=true
LEGACY_MODELS_READONLY=false
```
- **Status:** Legacy models active, WorkItem synced in background
- **Behavior:** All existing code works normally, WorkItem populated automatically
- **Use Case:** Safe initial rollout, no code changes required

#### Phase 2: Testing & Validation
```bash
USE_WORKITEM_MODEL=false
DUAL_WRITE_ENABLED=true
LEGACY_MODELS_READONLY=false
```
- **Status:** Run verification, fix inconsistencies
- **Action:** `python manage.py verify_workitem_migration --fix`
- **Use Case:** Ensure data integrity before switching

#### Phase 3: Read-Only Legacy Models
```bash
USE_WORKITEM_MODEL=true
DUAL_WRITE_ENABLED=true
LEGACY_MODELS_READONLY=true
```
- **Status:** New code uses WorkItem, legacy code read-only
- **Behavior:** Existing reads work, new writes go to WorkItem only
- **Use Case:** Gradual code migration, prevent legacy writes

#### Phase 4: Full Migration
```bash
USE_WORKITEM_MODEL=true
DUAL_WRITE_ENABLED=false
LEGACY_MODELS_READONLY=true
```
- **Status:** WorkItem fully active, legacy models deprecated
- **Behavior:** All operations use WorkItem model
- **Use Case:** Final state after all code migrated

## Usage Examples

### Example 1: Creating Tasks (Legacy Code Still Works)

```python
from common.models import StaffTask

# Old code continues to work
task = StaffTask.objects.create(
    title="Review policy draft",
    description="Review and provide feedback",
    status="in_progress",
    priority="high",
    domain="policy",
)

# Behind the scenes (when DUAL_WRITE_ENABLED=true):
# - post_save signal triggered
# - WorkItem created automatically with work_type='task'
# - All fields mapped from StaffTask to WorkItem
# - Legacy task_id stored in WorkItem.task_data['legacy_id']
```

### Example 2: Using Proxy Models (Transitional)

```python
from common.models.proxies import StaffTaskProxy

# Proxy model provides same interface as StaffTask
# But uses WorkItem underneath
task = StaffTaskProxy.objects.create(
    title="New task via proxy",
    status="not_started",
    priority="medium",
)

# This creates:
# - WorkItem with work_type='task'
# - StaffTask.board_position → WorkItem.task_data['board_position']
# - All legacy fields accessible via properties
```

### Example 3: Direct WorkItem Usage (Future)

```python
from common.work_item_model import WorkItem

# New code uses WorkItem directly
task = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    title="Fully migrated task",
    description="Using WorkItem model directly",
    status=WorkItem.STATUS_IN_PROGRESS,
    priority=WorkItem.PRIORITY_HIGH,
    task_data={
        'domain': 'policy',
        'assessment_phase': 'analysis',
    }
)

# No legacy model created (when DUAL_WRITE_ENABLED=false)
```

### Example 4: Projects and Activities

```python
from common.work_item_model import WorkItem

# Create a project with hierarchy
project = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_PROJECT,
    title="MANA Assessment - Region XII",
    description="Comprehensive needs assessment",
    status=WorkItem.STATUS_IN_PROGRESS,
    priority=WorkItem.PRIORITY_HIGH,
)

# Add activity under project
activity = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_ACTIVITY,
    title="Community Consultation Workshop",
    parent=project,  # MPTT hierarchy
    start_date="2025-11-01",
    activity_data={
        'event_type': 'workshop',
        'venue': 'LGU Conference Hall',
    }
)

# Add tasks under activity
task1 = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    title="Prepare workshop materials",
    parent=activity,  # Task under Activity under Project
    assignees=[user1, user2],
)

task2 = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_TASK,
    title="Send invitations",
    parent=activity,
)

# Query hierarchy
project.get_children()  # [activity]
activity.get_children()  # [task1, task2]
project.get_descendants()  # [activity, task1, task2] (all levels)
```

## Field Mappings

### StaffTask → WorkItem

| StaffTask Field       | WorkItem Field            | Notes                          |
|-----------------------|---------------------------|--------------------------------|
| `title`               | `title`                   | Direct mapping                 |
| `description`         | `description`             | Direct mapping                 |
| `status`              | `status`                  | Same values                    |
| `priority`            | `priority`                | Same values                    |
| `start_date`          | `start_date`              | Direct mapping                 |
| `due_date`            | `due_date`                | Direct mapping                 |
| `progress`            | `progress`                | 0-100 percentage               |
| `completed_at`        | `completed_at`            | Direct mapping                 |
| `assignees`           | `assignees`               | ManyToMany (same)              |
| `teams`               | `teams`                   | ManyToMany (same)              |
| `created_by`          | `created_by`              | Direct mapping                 |
| `is_recurring`        | `is_recurring`            | Direct mapping                 |
| `recurrence_pattern`  | `recurrence_pattern`      | Direct mapping                 |
| `board_position`      | `task_data['board_position']` | JSON field                 |
| `domain`              | `task_data['domain']`     | JSON field                     |
| `task_category`       | `task_data['task_category']` | JSON field                  |
| `assessment_phase`    | `task_data['assessment_phase']` | JSON field               |
| `linked_event`        | `related_object` (GenericFK) | ContentType relationship    |
| `linked_workflow`     | `related_object` (GenericFK) | ContentType relationship    |

### ProjectWorkflow → WorkItem

| ProjectWorkflow Field       | WorkItem Field                  | Notes                    |
|-----------------------------|---------------------------------|--------------------------|
| `primary_need.title`        | `title`                         | From related Need        |
| `notes`                     | `description`                   | Mapping                  |
| `current_stage`             | `project_data['workflow_stage']` | JSON field              |
| `priority_level`            | `priority`                      | Direct mapping           |
| `initiated_date`            | `start_date`                    | Mapping                  |
| `target_completion_date`    | `due_date`                      | Mapping                  |
| `overall_progress`          | `progress`                      | 0-100 percentage         |
| `actual_completion_date`    | `completed_at`                  | Direct mapping           |
| `is_on_track`               | Calculated from `status`        | Derived property         |
| `is_blocked`                | `status == 'blocked'`           | Status mapping           |
| `estimated_budget`          | `project_data['estimated_budget']` | JSON field           |
| `budget_approved`           | `project_data['budget_approved']` | JSON field            |

### Event → WorkItem

| Event Field      | WorkItem Field                | Notes                      |
|------------------|-------------------------------|----------------------------|
| `title`          | `title`                       | Direct mapping             |
| `description`    | `description`                 | Direct mapping             |
| `event_type`     | `activity_data['event_type']` | JSON field                 |
| `status`         | `status`                      | Status mapping             |
| `priority`       | `priority`                    | Direct mapping             |
| `start_date`     | `start_date`                  | Direct mapping             |
| `start_time`     | `start_time`                  | Direct mapping             |
| `end_date`       | `due_date`                    | Mapping                    |
| `end_time`       | `end_time`                    | Direct mapping             |
| `objectives`     | `activity_data['objectives']` | JSON field                 |
| `venue`          | `activity_data['venue']`      | JSON field                 |
| `organizer`      | `created_by`                  | Mapping                    |

## Migration Verification

### Run Verification Command

```bash
cd src

# Check migration status
python manage.py verify_workitem_migration

# Verbose mode (show all records)
python manage.py verify_workitem_migration --verbose

# Auto-fix missing WorkItems
python manage.py verify_workitem_migration --fix

# Report only (no record checks)
python manage.py verify_workitem_migration --report-only
```

### Sample Output

```
=== WorkItem Migration Verification ===

Feature Flags:
  USE_WORKITEM_MODEL: False
  DUAL_WRITE_ENABLED: True
  LEGACY_MODELS_READONLY: False

1. Checking StaffTask → WorkItem...
  Total: 150, With WorkItem: 148, Missing: 2, Mismatched: 0

2. Checking ProjectWorkflow → WorkItem...
  Total: 25, With WorkItem: 25, Missing: 0, Mismatched: 0

3. Checking Event → WorkItem...
  Total: 200, With WorkItem: 195, Missing: 5, Mismatched: 0

4. Checking for orphaned WorkItems...
  Total WorkItems: 373, Orphaned: 0

=== SUMMARY REPORT ===

┌──────────────────┬───────┬───────────────┬─────────┬────────────┐
│ Legacy Model     │ Total │ With WorkItem │ Missing │ Mismatched │
├──────────────────┼───────┼───────────────┼─────────┼────────────┤
│ StaffTask        │ 150   │ 148           │ 2       │ 0          │
│ ProjectWorkflow  │ 25    │ 25            │ 0       │ 0          │
│ Event            │ 200   │ 195           │ 5       │ 0          │
└──────────────────┴───────┴───────────────┴─────────┴────────────┘

WorkItem Orphans: 0 / 373

✗ Found 7 issue(s). Run with --fix to auto-fix.
```

## Rollback Plan

If issues occur during migration, you can safely rollback:

### Option 1: Disable WorkItem Model
```bash
# .env
USE_WORKITEM_MODEL=false
DUAL_WRITE_ENABLED=false
LEGACY_MODELS_READONLY=false
```
**Effect:** System reverts to using only legacy models (StaffTask, ProjectWorkflow, Event)

### Option 2: Keep Dual-Write Active
```bash
# .env
USE_WORKITEM_MODEL=false
DUAL_WRITE_ENABLED=true
LEGACY_MODELS_READONLY=false
```
**Effect:** Legacy models active, WorkItem continues syncing in background

### Option 3: Database Rollback
```bash
# Disable dual-write first
USE_WORKITEM_MODEL=false
DUAL_WRITE_ENABLED=false

# Delete all WorkItems (if needed)
cd src
python manage.py shell

>>> from common.work_item_model import WorkItem
>>> WorkItem.objects.all().delete()
```
**Effect:** Removes all WorkItem data, keeps legacy models intact

## Testing Recommendations

### 1. Unit Tests

```python
from django.test import TestCase
from common.models import StaffTask
from common.work_item_model import WorkItem

class DualWriteTestCase(TestCase):
    def test_stafftask_creates_workitem(self):
        """Test that creating a StaffTask creates a WorkItem."""
        task = StaffTask.objects.create(
            title="Test Task",
            status="in_progress",
            priority="high",
        )

        # Check WorkItem was created
        work_item = WorkItem.objects.filter(
            task_data__legacy_id=str(task.id),
            work_type=WorkItem.WORK_TYPE_TASK
        ).first()

        self.assertIsNotNone(work_item)
        self.assertEqual(work_item.title, task.title)
        self.assertEqual(work_item.status, task.status)

    def test_stafftask_update_syncs_workitem(self):
        """Test that updating a StaffTask updates WorkItem."""
        task = StaffTask.objects.create(title="Original Title")

        task.title = "Updated Title"
        task.save()

        work_item = WorkItem.objects.filter(
            task_data__legacy_id=str(task.id)
        ).first()

        self.assertEqual(work_item.title, "Updated Title")
```

### 2. Integration Tests

```python
def test_end_to_end_project_workflow():
    """Test complete project workflow with WorkItem."""
    # Create project
    project = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title="Test Project",
    )

    # Add activity
    activity = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_ACTIVITY,
        title="Workshop",
        parent=project,
    )

    # Add tasks
    task1 = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="Task 1",
        parent=activity,
    )

    # Verify hierarchy
    assert project.get_children().count() == 1
    assert activity.get_children().count() == 1
    assert project.get_descendants().count() == 2
```

### 3. Performance Tests

```python
def test_dual_write_performance():
    """Ensure dual-write doesn't significantly slow down operations."""
    import time

    start = time.time()
    for i in range(100):
        StaffTask.objects.create(
            title=f"Task {i}",
            status="not_started",
        )
    end = time.time()

    # Should complete in reasonable time (< 5 seconds for 100 records)
    assert (end - start) < 5.0
```

## Troubleshooting

### Issue: WorkItems not created when saving legacy models

**Solution:**
```bash
# 1. Check feature flag
echo $DUAL_WRITE_ENABLED  # Should be "true"

# 2. Check signals are registered
cd src
python manage.py shell

>>> from django.db.models.signals import post_save
>>> from common.models import StaffTask
>>> post_save.receivers_for(StaffTask)  # Should show signal handlers

# 3. Manually trigger sync
>>> task = StaffTask.objects.first()
>>> task.save()  # Force signal trigger
```

### Issue: Data mismatch between legacy and WorkItem

**Solution:**
```bash
# Run verification with verbose output
python manage.py verify_workitem_migration --verbose

# Auto-fix mismatches
python manage.py verify_workitem_migration --fix
```

### Issue: Orphaned WorkItems

**Solution:**
```python
# Option 1: Delete orphaned WorkItems
from common.work_item_model import WorkItem

orphaned = WorkItem.objects.filter(
    task_data__legacy_id=None,
    project_data__legacy_id=None,
    activity_data__legacy_id=None,
)
orphaned.delete()

# Option 2: Create legacy records for orphaned WorkItems
# (Manual intervention required)
```

## Best Practices

1. **Always run verification before switching phases**
   ```bash
   python manage.py verify_workitem_migration --fix
   ```

2. **Enable dual-write in development first**
   - Test thoroughly before production deployment
   - Run for at least 1 week with dual-write enabled

3. **Monitor logs during migration**
   ```python
   import logging
   logger = logging.getLogger('common.signals.workitem_sync')
   logger.setLevel(logging.DEBUG)
   ```

4. **Backup database before phase changes**
   ```bash
   # SQLite
   cp db.sqlite3 db.sqlite3.backup

   # PostgreSQL
   pg_dump obcms_prod > backup_before_workitem_migration.sql
   ```

5. **Update code incrementally**
   - Start with new features using WorkItem directly
   - Gradually refactor existing code to use WorkItem
   - Keep legacy code working during transition

## Migration Checklist

### Pre-Migration
- [ ] Review this documentation thoroughly
- [ ] Backup database
- [ ] Set `DUAL_WRITE_ENABLED=true` in `.env`
- [ ] Deploy and run for 1 week
- [ ] Run `verify_workitem_migration` daily
- [ ] Monitor logs for errors

### Phase 1: Dual-Write Active
- [ ] All legacy models syncing to WorkItem
- [ ] No errors in logs
- [ ] Verification shows 100% sync
- [ ] Performance acceptable

### Phase 2: Testing
- [ ] Write tests for new WorkItem code
- [ ] Refactor critical paths to use WorkItem
- [ ] Run comprehensive test suite
- [ ] Performance benchmarks pass

### Phase 3: Read-Only Legacy
- [ ] Set `LEGACY_MODELS_READONLY=true`
- [ ] Set `USE_WORKITEM_MODEL=true`
- [ ] Deploy to staging
- [ ] Test all workflows
- [ ] Fix any issues

### Phase 4: Full Migration
- [ ] Set `DUAL_WRITE_ENABLED=false`
- [ ] All code using WorkItem
- [ ] Legacy models deprecated
- [ ] Documentation updated

## Support

For questions or issues:
- **Documentation:** `docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md`
- **Code:** `src/common/models/proxies.py`, `src/common/signals/workitem_sync.py`
- **Management Command:** `python manage.py verify_workitem_migration --help`

---

**Last Updated:** 2025-10-05
**Status:** ✅ Phase 4 Complete - Backward Compatibility Implemented
