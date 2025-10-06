"""
Test suite for Budget Distribution Service.

Tests cover:
- Equal distribution algorithm
- Weighted distribution algorithm
- Manual distribution validation
- Distribution application logic
- Error handling and edge cases
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry
from monitoring.services.budget_distribution import BudgetDistributionService

User = get_user_model()


@pytest.mark.django_db
class TestBudgetDistributionService:
    """Test BudgetDistributionService for PPA budget allocation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="budget_user",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.organization = Organization.objects.create(
            name="Test Ministry",
            acronym="TM",
            organization_type="bmoa",
            created_by=self.user,
        )

        self.ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Budget Distribution Test PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("10000000.00"),  # 10M
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        self.service = BudgetDistributionService()

    def test_distribute_equal_simple(self):
        """Test equal distribution among workitems."""
        # Create project with 4 activities
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Equal Distribution Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("10000000.00"),
        )

        activities = []
        for i in range(4):
            activity = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_ACTIVITY,
                title=f"Activity {i+1}",
                parent=project,
                ppa_source=self.ppa,
            )
            activities.append(activity)

        # Distribute equally
        result = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("10000000.00"),
        )

        assert result["success"] is True
        assert result["distribution_method"] == "equal"
        assert len(result["allocations"]) == 4

        # Each activity should get 2.5M
        for allocation in result["allocations"]:
            assert allocation["amount"] == Decimal("2500000.00")

    def test_distribute_equal_with_remainder(self):
        """Test equal distribution handles remainders correctly."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Remainder Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        # Create 3 tasks (can't divide 1M evenly by 3)
        for i in range(3):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i+1}",
                parent=project,
                ppa_source=self.ppa,
            )

        result = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("1000000.00"),
        )

        assert result["success"] is True

        # 1M / 3 = 333,333.33... per task
        allocations = [a["amount"] for a in result["allocations"]]
        total_allocated = sum(allocations)

        # Total should equal original budget
        assert total_allocated == Decimal("1000000.00")

        # Each should be approximately equal
        for amount in allocations:
            assert Decimal("333333.00") <= amount <= Decimal("333334.00")

    def test_distribute_equal_no_children(self):
        """Test equal distribution with no children returns error."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Childless Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        result = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("1000000.00"),
        )

        assert result["success"] is False
        assert "no children" in result["error"].lower()

    def test_distribute_weighted_by_duration(self):
        """Test weighted distribution based on duration."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Weighted Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        from datetime import date

        # Task 1: 30 days
        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            start_date=date(2025, 1, 1),
            due_date=date(2025, 1, 31),
        )

        # Task 2: 60 days (2x task1)
        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            start_date=date(2025, 2, 1),
            due_date=date(2025, 4, 1),
        )

        # Task 3: 10 days
        task3 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            parent=project,
            start_date=date(2025, 4, 2),
            due_date=date(2025, 4, 12),
        )

        result = self.service.distribute_weighted(
            parent=project,
            total_budget=Decimal("1000000.00"),
            weight_by="duration",
        )

        assert result["success"] is True
        assert result["distribution_method"] == "weighted_duration"

        # Total duration: 30 + 60 + 10 = 100 days
        # Task 1: 30/100 = 30% = 300k
        # Task 2: 60/100 = 60% = 600k
        # Task 3: 10/100 = 10% = 100k

        allocations = {a["workitem_id"]: a["amount"] for a in result["allocations"]}
        assert allocations[str(task1.id)] == Decimal("300000.00")
        assert allocations[str(task2.id)] == Decimal("600000.00")
        assert allocations[str(task3.id)] == Decimal("100000.00")

    def test_distribute_weighted_by_complexity(self):
        """Test weighted distribution based on complexity scores."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Complexity Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        # Tasks with different complexity (stored in metadata)
        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Simple Task",
            parent=project,
            metadata={"complexity_score": 1},
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Medium Task",
            parent=project,
            metadata={"complexity_score": 3},
        )

        task3 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Complex Task",
            parent=project,
            metadata={"complexity_score": 6},
        )

        result = self.service.distribute_weighted(
            parent=project,
            total_budget=Decimal("1000000.00"),
            weight_by="complexity",
        )

        assert result["success"] is True

        # Total complexity: 1 + 3 + 6 = 10
        # Task 1: 1/10 = 10% = 100k
        # Task 2: 3/10 = 30% = 300k
        # Task 3: 6/10 = 60% = 600k

        allocations = {a["workitem_id"]: a["amount"] for a in result["allocations"]}
        assert allocations[str(task1.id)] == Decimal("100000.00")
        assert allocations[str(task2.id)] == Decimal("300000.00")
        assert allocations[str(task3.id)] == Decimal("600000.00")

    def test_distribute_weighted_missing_weights(self):
        """Test weighted distribution with some missing weight data."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Missing Weights Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        # Task with duration
        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            start_date=date(2025, 1, 1),
            due_date=date(2025, 1, 31),
        )

        # Task without duration
        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            # No dates
        )

        result = self.service.distribute_weighted(
            parent=project,
            total_budget=Decimal("1000000.00"),
            weight_by="duration",
        )

        # Should fall back to equal distribution or handle gracefully
        assert result["success"] is True

    def test_distribute_manual_valid(self):
        """Test manual distribution with valid allocations."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Manual Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
        )

        task3 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            parent=project,
        )

        manual_allocations = {
            str(task1.id): Decimal("300000.00"),
            str(task2.id): Decimal("450000.00"),
            str(task3.id): Decimal("250000.00"),
        }

        result = self.service.distribute_manual(
            parent=project,
            total_budget=Decimal("1000000.00"),
            allocations=manual_allocations,
        )

        assert result["success"] is True
        assert result["distribution_method"] == "manual"
        assert len(result["allocations"]) == 3

    def test_distribute_manual_exceeds_budget(self):
        """Test manual distribution validation when allocations exceed budget."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Over Budget Manual",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
        )

        manual_allocations = {
            str(task1.id): Decimal("700000.00"),
            str(task2.id): Decimal("600000.00"),  # Total: 1.3M > 1M
        }

        result = self.service.distribute_manual(
            parent=project,
            total_budget=Decimal("1000000.00"),
            allocations=manual_allocations,
        )

        assert result["success"] is False
        assert "exceeds budget" in result["error"].lower()

    def test_distribute_manual_missing_children(self):
        """Test manual distribution validation when some children not allocated."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Incomplete Manual",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
        )

        task3 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            parent=project,
        )

        # Only allocate to 2 of 3 tasks
        manual_allocations = {
            str(task1.id): Decimal("400000.00"),
            str(task2.id): Decimal("600000.00"),
            # task3 missing
        }

        result = self.service.distribute_manual(
            parent=project,
            total_budget=Decimal("1000000.00"),
            allocations=manual_allocations,
        )

        # Should succeed but warn
        assert result["success"] is True
        assert "warnings" in result
        assert len(result["warnings"]) > 0

    def test_apply_distribution_success(self):
        """Test applying distribution actually updates WorkItem budgets."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Apply Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
        )

        # Get distribution
        distribution = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("1000000.00"),
        )

        # Apply it
        result = self.service.apply_distribution(distribution)

        assert result["success"] is True
        assert result["updated_count"] == 2

        # Verify budgets updated
        task1.refresh_from_db()
        task2.refresh_from_db()

        assert task1.budget_allocation == Decimal("500000.00")
        assert task2.budget_allocation == Decimal("500000.00")

    def test_apply_distribution_dry_run(self):
        """Test apply_distribution in dry run mode doesn't save."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Dry Run Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
        )

        distribution = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("1000000.00"),
        )

        result = self.service.apply_distribution(distribution, dry_run=True)

        assert result["success"] is True
        assert result["dry_run"] is True

        # Verify budgets NOT updated
        task1.refresh_from_db()
        assert task1.budget_allocation is None

    def test_validation_errors_negative_budget(self):
        """Test validation catches negative budget amounts."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Negative Budget",
            ppa_source=self.ppa,
        )

        result = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("-100000.00"),  # Negative!
        )

        assert result["success"] is False
        assert "negative" in result["error"].lower()

    def test_validation_errors_zero_budget(self):
        """Test validation handles zero budget appropriately."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Zero Budget",
            ppa_source=self.ppa,
            budget_allocation=Decimal("0.00"),
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
        )

        result = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("0.00"),
        )

        # Should succeed with zero allocations
        assert result["success"] is True
        assert all(a["amount"] == Decimal("0.00") for a in result["allocations"])

    def test_complex_multi_level_distribution(self):
        """Test distribution across complex multi-level hierarchy."""
        # Project
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Complex Multi-Level",
            ppa_source=self.ppa,
            budget_allocation=Decimal("10000000.00"),
        )

        # 2 Activities
        activity1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            parent=project,
            ppa_source=self.ppa,
        )

        activity2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 2",
            parent=project,
            ppa_source=self.ppa,
        )

        # Distribute to activities first (equal)
        activity_distribution = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("10000000.00"),
        )

        self.service.apply_distribution(activity_distribution)

        # Now distribute within each activity
        # Activity 1: 3 tasks
        for i in range(3):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Activity 1 Task {i+1}",
                parent=activity1,
            )

        # Activity 2: 2 tasks
        for i in range(2):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Activity 2 Task {i+1}",
                parent=activity2,
            )

        activity1.refresh_from_db()
        task_distribution1 = self.service.distribute_equal(
            parent=activity1,
            total_budget=activity1.budget_allocation,
        )
        self.service.apply_distribution(task_distribution1)

        activity2.refresh_from_db()
        task_distribution2 = self.service.distribute_equal(
            parent=activity2,
            total_budget=activity2.budget_allocation,
        )
        self.service.apply_distribution(task_distribution2)

        # Verify total budget preserved
        all_tasks = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK,
            parent__parent=project,
        )

        total_task_budget = sum(
            t.budget_allocation for t in all_tasks if t.budget_allocation
        )

        assert total_task_budget == Decimal("10000000.00")

    @pytest.mark.parametrize(
        "method,expected_key",
        [
            ("equal", "equal"),
            ("weighted_duration", "weighted_duration"),
            ("weighted_complexity", "weighted_complexity"),
            ("manual", "manual"),
        ],
    )
    def test_distribution_methods_return_metadata(self, method, expected_key):
        """Test all distribution methods return proper metadata."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Metadata Test",
            ppa_source=self.ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        for i in range(2):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i+1}",
                parent=project,
                start_date=date(2025, 1, 1),
                due_date=date(2025, 1, 31),
                metadata={"complexity_score": 5},
            )

        if method == "manual":
            children = list(project.get_children())
            allocations = {
                str(children[0].id): Decimal("400000.00"),
                str(children[1].id): Decimal("600000.00"),
            }
            result = self.service.distribute_manual(
                parent=project,
                total_budget=Decimal("1000000.00"),
                allocations=allocations,
            )
        elif method.startswith("weighted"):
            weight_type = method.split("_")[1]
            result = self.service.distribute_weighted(
                parent=project,
                total_budget=Decimal("1000000.00"),
                weight_by=weight_type,
            )
        else:
            result = self.service.distribute_equal(
                parent=project,
                total_budget=Decimal("1000000.00"),
            )

        assert "distribution_method" in result
        assert expected_key in result["distribution_method"]
        assert "timestamp" in result
        assert "total_budget" in result
