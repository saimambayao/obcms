"""Integration tests for MonitoringEntry ↔ WorkItem helpers."""

import json
from decimal import Decimal

import pytest

try:
    from django.core.exceptions import ValidationError
    from django.urls import reverse
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for monitoring WorkItem integration tests",
        allow_module_level=True,
    )

from common.work_item_model import WorkItem

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_create_execution_project_populates_metadata(staff_user, monitoring_entry_factory):
    ppa = monitoring_entry_factory(
        title="Execution Pipeline",
        status="planning",
        budget_allocation=Decimal("500000.00"),
    )

    project = ppa.create_execution_project(created_by=staff_user)

    assert project.work_type == WorkItem.WORK_TYPE_PROJECT
    assert project.related_ppa == ppa
    assert project.allocated_budget == Decimal("500000.00")
    assert project.project_data["monitoring_entry_id"] == str(ppa.id)


@pytest.mark.django_db
def test_sync_progress_from_workitem_updates_monitoring_entry(
    staff_user, monitoring_entry_factory, execution_project_builder
):
    ppa = monitoring_entry_factory(
        title="Progress Sync PPA",
        status="ongoing",
    )

    execution_project_builder(ppa, created_by=staff_user, completed=2, total=4)

    new_progress = ppa.sync_progress_from_workitem()
    assert new_progress == 50

    ppa.refresh_from_db()
    assert ppa.progress == 50


@pytest.mark.django_db
def test_get_budget_allocation_tree_returns_structure(
    staff_user, monitoring_entry_factory, execution_project_builder
):
    ppa = monitoring_entry_factory(
        title="Budget Tree PPA",
        status="planning",
        budget_allocation=Decimal("900000.00"),
    )

    project = execution_project_builder(
        ppa, created_by=staff_user, completed=0, total=2
    )
    for child in project.get_children():
        child.allocated_budget = Decimal("450000.00")
        child.save(update_fields=["allocated_budget", "updated_at"])

    tree = ppa.get_budget_allocation_tree()

    assert tree["work_item_id"] == str(project.id)
    assert len(tree["children"]) == 2
    assert tree["children"][0]["allocated_budget"] == Decimal("450000.00")


@pytest.mark.django_db
def test_monitoring_detail_renders_without_execution_project(
    client, staff_user, monitoring_entry_factory
):
    ppa = monitoring_entry_factory(
        title="Tracking Without Project",
        enable_workitem_tracking=True,
    )

    client.force_login(staff_user)
    response = client.get(reverse("monitoring:detail", args=[ppa.id]))

    assert response.status_code == 200
    content = response.content
    assert b"cursor-not-allowed" in content
    assert b'aria-disabled="true"' in content


@pytest.mark.django_db
def test_create_execution_project_requires_implementing_moa(
    staff_user, monitoring_entry_factory
):
    ppa = monitoring_entry_factory(
        title="MOA Validation",
        category="moa_ppa",
        implementing_moa=None,
    )

    with pytest.raises(ValidationError):
        ppa.create_execution_project(created_by=staff_user)


@pytest.mark.django_db
def test_sync_status_from_workitem_updates_monitoring_entry(
    staff_user, monitoring_entry_factory, execution_project_builder
):
    ppa = monitoring_entry_factory(status="planning")

    project = execution_project_builder(
        ppa,
        created_by=staff_user,
        statuses=[WorkItem.STATUS_IN_PROGRESS],
        total=1,
    )
    project.status = WorkItem.STATUS_COMPLETED
    project.save(update_fields=["status", "updated_at"])

    updated_status = ppa.sync_status_from_workitem()

    assert updated_status == "completed"
    ppa.refresh_from_db()
    assert ppa.status == "completed"


@pytest.mark.django_db
def test_work_items_summary_partial_returns_stats_for_execution_project(
    hx_client,
    staff_user,
    monitoring_entry_factory,
    execution_project_builder,
):
    ppa = monitoring_entry_factory(
        enable_workitem_tracking=True,
        budget_allocation=Decimal("200000.00"),
    )

    project = execution_project_builder(
        ppa,
        created_by=staff_user,
        completed=1,
        total=2,
    )
    project.progress = 60
    project.allocated_budget = Decimal("0.00")
    project.save(update_fields=["progress", "allocated_budget", "updated_at"])

    child_items = list(project.get_children())
    for index, child in enumerate(child_items):
        child.progress = 40 + (index * 20)
        child.allocated_budget = Decimal("100000.00")
        child.save(update_fields=["progress", "allocated_budget", "updated_at"])

    progress_values = [project.progress] + [child.progress for child in child_items]
    expected_average = int(round(sum(progress_values) / len(progress_values)))

    response = hx_client.get(reverse("monitoring:work_items_summary", args=[ppa.id]))

    assert response.status_code == 200
    stats = response.context["workitem_stats"]
    budget_summary = response.context["budget_summary"]

    assert stats["total_work_items"] == 3  # project + 2 child tasks
    assert stats["avg_progress"] == expected_average
    assert stats["total_budget_allocated"] == Decimal("200000.00")
    assert stats["unallocated_budget"] == Decimal("0.00")
    assert budget_summary["remaining"] == Decimal("0.00")
    assert "HX-Trigger" not in response.headers


@pytest.mark.django_db
def test_work_items_summary_partial_sets_toast_when_regeneration_fails(
    hx_client,
    monitoring_entry_factory,
    monkeypatch,
):
    ppa = monitoring_entry_factory(
        enable_workitem_tracking=True,
        implementing_moa=None,
    )

    WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="Orphan integration item",
        related_ppa=ppa,
    )

    def failing_regeneration(self, *, created_by=None, updated_by=None):
        raise ValidationError("Execution project requires implementing MOA.")

    monkeypatch.setattr(
        ppa.__class__,
        "ensure_execution_project",
        failing_regeneration,
    )

    response = hx_client.get(reverse("monitoring:work_items_summary", args=[ppa.id]))

    assert response.status_code == 204
    trigger_header = response.headers.get("HX-Trigger")
    assert trigger_header is not None

    payload = json.loads(trigger_header)
    assert payload["show-toast"] == "Execution project requires implementing MOA."
