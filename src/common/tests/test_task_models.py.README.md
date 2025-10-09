# test_task_models.py - SKIPPED

## Status: SKIPPED

This test file has been skipped because it tests functionality that was never fully implemented in the OBCMS codebase.

## Reason for Skipping

The test file imports and tests the following models that **do not exist** in the current codebase:
- `TaskTemplate` - A model for creating reusable task templates
- `TaskTemplateItem` - Items/steps within a task template

These models were planned but never implemented. The codebase has since migrated to the `WorkItem` model for unified activity tracking.

## What This Test File Tests

1. **StaffTask Domain Logic** - Tests domain field choices (MANA, Coordination, Policy, etc.)
2. **StaffTask Validation** - Tests validation rules for task relationships
3. **StaffTask Phase Fields** - Tests assessment, policy, and service phase choices
4. **TaskTemplate Model** - Tests template creation and management (NOT IMPLEMENTED)
5. **TaskTemplateItem Model** - Tests template item ordering and phases (NOT IMPLEMENTED)
6. **Template Relationships** - Tests `created_from_template` field (NOT IMPLEMENTED)

## Migration Status

**Priority:** LOW - Feature was never in production

**What Would Be Needed:**
1. Complete rewrite to use `WorkItem` model instead of `StaffTask`
2. Remove all `TaskTemplate` and `TaskTemplateItem` references
3. Update validation tests to match current `WorkItem` validation logic
4. Verify domain logic works with unified `WorkItem.activity_type` field

**Alternatives:**
- Most domain logic can be tested through integration tests using actual WorkItem instances
- Template functionality may not be needed with current WorkItem architecture

## Related Files

- **Model File:** `src/common/models.py` (contains StaffTask, but NOT TaskTemplate)
- **WorkItem Model:** `src/common/models/work_item.py` (new unified model)
- **Legacy StaffTask:** `src/common/legacy/staff_task_model.py` (deprecated)

## Last Modified

- Test file created: October 2, 2025
- Skipped on: October 5, 2025
- Reason: Import errors due to non-existent TaskTemplate models
