"""Unit tests for MonitoringEntry ↔ WorkItem helpers."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="integration_staff",
        password="testpass123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def organization(staff_user):
    return Organization.objects.create(
        name="Integration Org",
        acronym="INT",
        organization_type="bmoa",
        created_by=staff_user,
    )


def build_execution_project(ppa, *, created_by, completed=1, total=3):
    project = ppa.create_execution_project(created_by=created_by)
    ppa.execution_project = project
    ppa.enable_workitem_tracking = True
    ppa.save(update_fields=["execution_project", "enable_workitem_tracking", "updated_at"])

    for idx in range(total):
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=f"Task {idx + 1}",
            parent=project,
            related_ppa=ppa,
            status=WorkItem.STATUS_COMPLETED if idx < completed else WorkItem.STATUS_IN_PROGRESS,
        )
    return project


@pytest.mark.django_db
def test_create_execution_project_populates_metadata(staff_user, organization):
    ppa = MonitoringEntry.objects.create(
        title="Execution Pipeline",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        budget_allocation=Decimal("500000.00"),
        created_by=staff_user,
        updated_by=staff_user,
    )

    project = ppa.create_execution_project(created_by=staff_user)

    assert project.work_type == WorkItem.WORK_TYPE_PROJECT
    assert project.related_ppa == ppa
    assert project.allocated_budget == Decimal("500000.00")
    assert project.project_data["monitoring_entry_id"] == str(ppa.id)


@pytest.mark.django_db
def test_sync_progress_from_workitem_updates_monitoring_entry(staff_user, organization):
    ppa = MonitoringEntry.objects.create(
        title="Progress Sync PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="ongoing",
        progress=0,
        created_by=staff_user,
        updated_by=staff_user,
    )

    build_execution_project(ppa, created_by=staff_user, completed=2, total=4)

    new_progress = ppa.sync_progress_from_workitem()
    assert new_progress == 50

    ppa.refresh_from_db()
    assert ppa.progress == 50


@pytest.mark.django_db
def test_get_budget_allocation_tree_returns_structure(staff_user, organization):
    ppa = MonitoringEntry.objects.create(
        title="Budget Tree PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        budget_allocation=Decimal("900000.00"),
        created_by=staff_user,
        updated_by=staff_user,
    )

    project = build_execution_project(ppa, created_by=staff_user, completed=0, total=2)
    for child in project.get_children():
        child.allocated_budget = Decimal("450000.00")
        child.save(update_fields=["allocated_budget", "updated_at"])

    tree = ppa.get_budget_allocation_tree()

    assert tree["work_item_id"] == str(project.id)
    assert len(tree["children"]) == 2
    assert tree["children"][0]["allocated_budget"] == Decimal("450000.00")
