# test_task_automation.py - SKIPPED

## Status: SKIPPED

This test file was already skipped previously (existing as test_task_automation.py.skip).

## Reason for Skipping

The test file imports and tests:
- `TaskTemplate` model - Does not exist in codebase
- `TaskTemplateItem` model - Does not exist in codebase
- Automated task creation from templates - Feature never implemented

## What This Test File Tests

Automated task generation workflows based on templates:
1. Template-based task automation
2. Task scheduling based on template sequences
3. Automatic task assignment rules
4. Template context variable substitution

## Migration Status

**Priority:** LOW - Feature was never in production, may not be needed

**Decision Required:**
- Should OBCMS have a template-based task automation system?
- Or should tasks continue to be created manually/directly?

## Related Files

- **Other skipped tests:** See LEGACY_TESTS_README.md for complete list
- **WorkItem Model:** `src/common/models/work_item.py` (current task/activity model)

## Last Modified

- Test file created: October 2, 2025 (or earlier)
- Originally skipped: Unknown date
- Documented: October 5, 2025
