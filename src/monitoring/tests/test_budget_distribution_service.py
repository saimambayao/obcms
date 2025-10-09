"""Tests for the refactored BudgetDistributionService."""

from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry
from monitoring.services.budget_distribution import BudgetDistributionService

User = get_user_model()


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="budget_user",
        password="testpass123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def organization(staff_user):
    return Organization.objects.create(
        name="Budget Ministry",
        acronym="BM",
        organization_type="bmoa",
        created_by=staff_user,
    )


def create_ppa(user, organization, *, budget=Decimal("1200000.00")):
    return MonitoringEntry.objects.create(
        title="Budget Test PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        budget_allocation=budget,
        fiscal_year=2025,
        approval_status=MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW,
        enable_workitem_tracking=True,
        created_by=user,
        updated_by=user,
    )


def create_project_with_tasks(ppa, *, created_by, task_count=3):
    """Create an execution project and attach a set number of child tasks."""
    project = ppa.create_execution_project(created_by=created_by)
    ppa.execution_project = project
    ppa.enable_workitem_tracking = True
    ppa.save(update_fields=["execution_project", "enable_workitem_tracking", "updated_at"])

    tasks = []
    for idx in range(task_count):
        tasks.append(
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {idx + 1}",
                parent=project,
                related_ppa=ppa,
            )
        )
    return project, tasks


@pytest.fixture
def ppa_with_tasks(staff_user, organization):
    ppa = create_ppa(staff_user, organization)
    project, tasks = create_project_with_tasks(ppa, created_by=staff_user, task_count=3)
    return ppa, project, tasks


@pytest.mark.django_db
class TestBudgetDistributionService:
    def test_distribute_equal_splits_budget_evenly(self, ppa_with_tasks):
        ppa, project, tasks = ppa_with_tasks

        distribution = BudgetDistributionService.distribute_equal(ppa)

        assert len(distribution) == len(tasks) + 1  # Root project + tasks
        total = sum(distribution.values())
        assert total == ppa.budget_allocation

        task_amounts = [distribution[task.id] for task in tasks]
        assert all(amount == Decimal("300000.00") for amount in task_amounts)
        assert distribution[project.id] == Decimal("300000.00")

    def test_distribute_equal_requires_work_items(self, staff_user, organization):
        ppa = create_ppa(staff_user, organization)
        # No execution project yet → ppa.work_items is empty
        with pytest.raises(ValidationError):
            BudgetDistributionService.distribute_equal(ppa)

    def test_distribute_weighted_applies_weights(self, ppa_with_tasks):
        ppa, project, tasks = ppa_with_tasks

        weights = {
            tasks[0].id: 0.5,
            tasks[1].id: 0.3,
            tasks[2].id: 0.2,
            project.id: 0.0,  # Explicitly include root project
        }

        distribution = BudgetDistributionService.distribute_weighted(ppa, weights=weights)

        assert len(distribution) == len(weights)
        assert distribution[tasks[0].id] == Decimal("600000.00")
        assert distribution[tasks[1].id] == Decimal("360000.00")
        assert distribution[tasks[2].id] == Decimal("240000.00")
        assert distribution[project.id] == Decimal("0.00")

    def test_distribute_weighted_missing_weights_raises(self, ppa_with_tasks):
        ppa, project, tasks = ppa_with_tasks

        weights = {tasks[0].id: 0.7, tasks[1].id: 0.3}  # Missing task[2] and project

        with pytest.raises(ValidationError):
            BudgetDistributionService.distribute_weighted(ppa, weights=weights)

    def test_distribute_manual_valid(self, ppa_with_tasks):
        ppa, project, tasks = ppa_with_tasks
        allocations = {
            project.id: Decimal("0.00"),
            tasks[0].id: Decimal("500000.00"),
            tasks[1].id: Decimal("400000.00"),
            tasks[2].id: Decimal("300000.00"),
        }

        distribution = BudgetDistributionService.distribute_manual(ppa, allocations)

        assert distribution == allocations

    def test_distribute_manual_total_mismatch(self, ppa_with_tasks):
        ppa, project, tasks = ppa_with_tasks
        allocations = {
            project.id: Decimal("0.00"),
            tasks[0].id: Decimal("500000.00"),
            tasks[1].id: Decimal("500000.00"),
            tasks[2].id: Decimal("500000.00"),  # Sum 1.5M vs budget 1.2M
        }

        with pytest.raises(ValidationError):
            BudgetDistributionService.distribute_manual(ppa, allocations)

    def test_apply_distribution_updates_workitems(self, ppa_with_tasks):
        ppa, project, tasks = ppa_with_tasks
        distribution = BudgetDistributionService.distribute_equal(ppa)

        updated_count = BudgetDistributionService.apply_distribution(ppa, distribution)

        assert updated_count == len(distribution)
        for task in tasks:
            task.refresh_from_db()
            assert task.allocated_budget == Decimal("300000.00")

        project.refresh_from_db()
        assert project.allocated_budget == Decimal("300000.00")

        total_allocated = (
            ppa.work_items.aggregate(total=Sum("allocated_budget"))["total"] or Decimal("0.00")
        )
        assert Decimal(str(total_allocated)) == ppa.budget_allocation

    def test_apply_distribution_rejects_missing_work_item(self, ppa_with_tasks):
        ppa, project, tasks = ppa_with_tasks
        distribution = {uuid4(): Decimal("100.00")}

        with pytest.raises(ValidationError):
            BudgetDistributionService.apply_distribution(ppa, distribution)
