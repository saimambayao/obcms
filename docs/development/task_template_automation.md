# Task Template Automation Service Guide

**Status:** Active
**Last Updated:** 2025-10-02
**Owner:** OOBC Development Team

## Overview

`common.services.task_automation.create_tasks_from_template` orchestrates the
creation of `StaffTask` records from declarative templates. The service powers
Project Management Portal workflow generation, MANA automation, coordination events, and
monitoring migrations. This guide documents the function contract, idempotency
model, resource booking support, and testing expectations so new automation
flows remain consistent.

## Function Signature

```python
create_tasks_from_template(template_name: str, **kwargs) -> list[StaffTask]
```

### Core Parameters

| Argument | Type | Description |
| --- | --- | --- |
| `template_name` | `str` | Name of the `TaskTemplate` to instantiate. Must be active. |
| `start_date` | `date \\| str` | Base date used to compute `days_from_start` offsets. Defaults to `timezone.now().date()`. ISO strings are accepted. |
| `created_by` | `User \\| None` | Creator assigned to generated tasks (and resource bookings). |
| `resource_bookings` | `Sequence[Mapping] \\| Mapping \\| None` | Optional booking specifications (see below). |
| `idempotency_filter` | `Mapping[str, object]` | Optional filter applied with `created_from_template` to detect pre-existing task batches. When matches are found, the call returns the existing tasks without creating new records. |
| `auto_generated` | `bool` | Flags generated tasks as system-created (`StaffTask.auto_generated`). |
| Additional keyword arguments | Depends on domain | Any field present on `StaffTask` can be supplied (e.g., `linked_workflow`, `related_ppa`). Values also participate in template string formatting. |

### Template Item Mapping

Each `TaskTemplateItem` contributes a single `StaffTask`. Item attributes map
as follows:

| Template Item Field | StaffTask Field |
| --- | --- |
| `title` | `StaffTask.title` (with `.format(**context)` substitution) |
| `description` | `StaffTask.description` |
| `priority` | `StaffTask.priority` |
| `estimated_hours` | `StaffTask.estimated_hours` |
| `task_category` | `StaffTask.task_category` |
| `assessment_phase`/`policy_phase`/`service_phase` | Domain-specific fields |
| `task_role` | `StaffTask.task_role` |
| `days_from_start` | Offset applied to `start_date` for `StaffTask.due_date` |

## Idempotency Model

Pass `idempotency_filter` when automation may be triggered multiple times for
the same entity (e.g., Project Workflow stages). The service checks for existing
`StaffTask` rows matching:

```python
StaffTask.objects.filter(created_from_template=template, **idempotency_filter)
```

If records exist, the call returns the matching queryset (ordered by
`created_at`) and **does not** create new tasks. This mechanism protects against
duplicate task batches when re-running signals or user actions.

### Example

```python
create_tasks_from_template(
    "project_budget_planning",
    linked_workflow=workflow,
    related_ppa=workflow.ppa,
    start_date=workflow.initiated_date,
    created_by=request.user,
    idempotency_filter={"linked_workflow": workflow},
    auto_generated=True,
)
```

## Resource Booking Specifications

`resource_bookings` accepts either a list or a mapping. Common patterns:

```python
# Apply same booking to every generated task
resource_bookings=[{
    "resource_id": resource.id,
    "start_offset_hours": 2,
    "duration_hours": 3,
    "notes": "Stage review",
}]

# Map bookings to template sequence / title
resource_bookings={
    1: [{"resource_name": "Strategy Room", "duration_hours": 2}],
    "default": [{"resource_name": "Projector", "start_offset_hours": 1}],
}
```

Supported keys for each spec:

| Key | Type | Notes |
| --- | --- | --- |
| `resource_id` / `resource_name` | lookup | Required. Resolves `CalendarResource`. |
| `start` / `end` | ISO string or `datetime` | Explicit schedule. |
| `start_offset_days` / `start_offset_hours` | `int` | Offset from task `start_date` (default 08:00). |
| `duration_hours` | `float \\| int` | Alternative to `end`. |
| `notes` | `str` | Defaults to `"Auto-booked for task: {title}"`. |
| `status` | CalendarResourceBooking status | Defaults to `pending`. |
| `approved_by` | `user_id` | Optional approver. |

The helper validates bookings (`full_clean()`) before saving, so domain
integrations immediately surface conflicts.

## Error Handling

- `TaskTemplate.DoesNotExist` → returns empty list.
- `ResourceBookingSpecError` / `ValidationError` → raised with contextual
  message (captured in tests like `test_create_tasks_with_bad_resource_booking_spec_raises`).
- Idempotency filters must use concrete `StaffTask` fields; invalid keys raise a
  `FieldError` upstream.

## Testing Expectations

| Scenario | Location |
| --- | --- |
| Standard instantiation, date offsets, template substitutions | `common/tests/test_task_automation.py::test_create_tasks_from_template_with_context` |
| Idempotency guard | `project_central/tests/test_views.py::GenerateWorkflowTasksViewTests.test_generate_workflow_tasks_is_idempotent` |
| Resource booking creation & conflict detection | `common/tests/test_task_automation.py::test_create_tasks_with_resource_bookings` |
| Celery notification batching for automation outputs | `common/tests/test_tasks_notifications.py` |

When adding new automation flows:

1. Reference this contract (idempotency, resource specs, context variables).
2. Extend pytest coverage to include both success and failure paths.
3. Update this document if new kwargs or behaviours are introduced.

## Related Resources

- `common/services/resource_bookings.py` – booking helper API
- `docs/testing/TESTING_STRATEGY.md` – integration testing references
- `docs/testing/staging_rehearsal_checklist.md` – deployment rehearsal guidance
