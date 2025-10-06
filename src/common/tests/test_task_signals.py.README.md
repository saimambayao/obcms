# test_task_signals.py - SKIPPED

## Status: SKIPPED

This test file has been skipped because it tests automatic task creation from templates, a feature that was never fully implemented.

## Reason for Skipping

The test file imports and relies on:
- `TaskTemplate` - Does not exist in codebase
- `TaskTemplateItem` - Does not exist in codebase
- Signal handlers for auto-creating tasks from templates - Not implemented

## What This Test File Tests

1. **Assessment Signal Tests** - Tests that creating an Assessment auto-creates tasks from templates
2. **Baseline Study Signal Tests** - Tests automatic task generation for baseline studies
3. **Workshop Activity Signal Tests** - Tests workshop-related automated task creation
4. **Event Signal Tests** - Tests meeting/workshop event task automation
5. **Partnership Signal Tests** - Tests partnership negotiation task automation
6. **Policy Signal Tests** - Tests policy development task automation
7. **Policy Milestone Signal Tests** - Tests milestone-specific task creation
8. **Monitoring Entry Signal Tests** - Tests PPA monitoring task automation
9. **Service Application Signal Tests** - Tests application review task creation
10. **Monitoring Progress Sync Tests** - Tests MonitoringEntry progress updates

## Migration Status

**Priority:** LOW - Template-based automation was never in production

**What Would Be Needed:**
1. Decide if template-based task automation is still desired
2. If yes, implement TaskTemplate and TaskTemplateItem models
3. Create signal handlers in `src/common/signals/` directory
4. Update tests to use WorkItem instead of StaffTask
5. Test with real assessment, event, and policy objects

**Current Workaround:**
- Tasks are created manually or through WorkItem direct creation
- No automatic task generation from templates exists in production

## Signal Architecture

The codebase does have a signals directory structure:
```
src/common/signals/
├── __init__.py
├── work_item_signals.py  # WorkItem-related signals
```

But these signals do NOT include template-based task automation.

## Related Files

- **Factories:** `src/common/tests/factories.py` (create_assessment, create_event, etc.)
- **WorkItem Signals:** `src/common/signals/work_item_signals.py`
- **Legacy Tasks:** `src/common/legacy/` (deprecated task implementations)

## Last Modified

- Test file created: October 2, 2025
- Skipped on: October 5, 2025
- Reason: Import errors, feature never implemented
