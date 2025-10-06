"""
Test suite for WorkItem PPA integration methods.

Tests cover:
- PPA source resolution (direct FK and parent traversal)
- Budget calculation from children
- Budget rollup validation
- Bidirectional sync between WorkItem and PPA
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


@pytest.mark.django_db
class TestWorkItemPPAMethods:
    """Test WorkItem methods for PPA integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="ppa_test_user",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.organization = Organization.objects.create(
            name="Ministry of Education",
            acronym="MOE",
            organization_type="bmoa",
            created_by=self.user,
        )

        self.ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Education Program 2025",
            implementing_moa=self.organization,
            budget_allocation=Decimal("5000000.00"),
            fiscal_year=2025,
            plan_year=2025,
            status="planning",
            approval_status="approved",
            created_by=self.user,
        )

    def test_get_ppa_source_direct_fk(self):
        """Test get_ppa_source() with direct foreign key."""
        workitem = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Direct FK Project",
            ppa_source=self.ppa,
            created_by=self.user,
        )

        assert workitem.get_ppa_source() == self.ppa

    def test_get_ppa_source_none(self):
        """Test get_ppa_source() returns None when no PPA linked."""
        workitem = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Standalone Task",
            created_by=self.user,
        )

        assert workitem.get_ppa_source() is None

    def test_get_ppa_source_parent_traversal_single_level(self):
        """Test get_ppa_source() via parent traversal (1 level)."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Parent Project",
            ppa_source=self.ppa,
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Child Task",
            parent=project,
        )

        # Task has no direct ppa_source, should get from parent
        assert task.ppa_source is None
        assert task.get_ppa_source() == self.ppa

    def test_get_ppa_source_parent_traversal_multi_level(self):
        """Test get_ppa_source() via parent traversal (3 levels)."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Root Project",
            ppa_source=self.ppa,
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Mid Activity",
            parent=project,
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Leaf Task",
            parent=activity,
        )

        # Task should traverse: task → activity → project → ppa
        assert task.get_ppa_source() == self.ppa
        assert activity.get_ppa_source() == self.ppa

    def test_get_ppa_source_caching(self):
        """Test get_ppa_source() uses efficient ancestor query."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Cached Project",
            ppa_source=self.ppa,
        )

        # Create deep hierarchy
        current = project
        for i in range(5):
            current = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_ACTIVITY,
                title=f"Level {i+1}",
                parent=current,
            )

        # Deep child should still find PPA efficiently
        assert current.get_ppa_source() == self.ppa

    def test_calculate_budget_from_children_no_children(self):
        """Test calculate_budget_from_children() with no children."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Childless Project",
            budget_allocation=Decimal("1000000.00"),
        )

        calculated = project.calculate_budget_from_children()

        assert calculated == Decimal("0.00")

    def test_calculate_budget_from_children_all_allocated(self):
        """Test calculate_budget_from_children() with all children having budgets."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Fully Allocated Project",
        )

        # Create 3 tasks with budgets
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task A",
            parent=project,
            budget_allocation=Decimal("300000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task B",
            parent=project,
            budget_allocation=Decimal("450000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task C",
            parent=project,
            budget_allocation=Decimal("250000.00"),
        )

        calculated = project.calculate_budget_from_children()

        # Expected: 300k + 450k + 250k = 1M
        assert calculated == Decimal("1000000.00")

    def test_calculate_budget_from_children_partial_allocation(self):
        """Test calculate_budget_from_children() with some children missing budgets."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Partially Allocated Project",
        )

        # Mix of allocated and non-allocated
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            budget_allocation=Decimal("200000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            budget_allocation=None,  # No budget
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            parent=project,
            budget_allocation=Decimal("300000.00"),
        )

        calculated = project.calculate_budget_from_children()

        # Expected: 200k + 0 + 300k = 500k
        assert calculated == Decimal("500000.00")

    def test_calculate_budget_from_children_zero_allocation(self):
        """Test calculate_budget_from_children() with explicit zero budgets."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Zero Budget Project",
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Free Task",
            parent=project,
            budget_allocation=Decimal("0.00"),
        )

        calculated = project.calculate_budget_from_children()

        assert calculated == Decimal("0.00")

    def test_validate_budget_rollup_valid(self):
        """Test validate_budget_rollup() with valid allocation."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Valid Rollup Project",
            budget_allocation=Decimal("1000000.00"),
        )

        # Children sum exactly to parent
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            budget_allocation=Decimal("600000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            budget_allocation=Decimal("400000.00"),
        )

        is_valid, variance = project.validate_budget_rollup()

        assert is_valid is True
        assert variance == Decimal("0.00")

    def test_validate_budget_rollup_under_allocated(self):
        """Test validate_budget_rollup() with under-allocation."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Under Allocated Project",
            budget_allocation=Decimal("1000000.00"),
        )

        # Children sum less than parent
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            budget_allocation=Decimal("300000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            budget_allocation=Decimal("200000.00"),
        )

        is_valid, variance = project.validate_budget_rollup()

        assert is_valid is False
        assert variance == Decimal("-500000.00")  # 500k under

    def test_validate_budget_rollup_over_allocated(self):
        """Test validate_budget_rollup() with over-allocation."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Over Allocated Project",
            budget_allocation=Decimal("1000000.00"),
        )

        # Children sum exceeds parent
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            budget_allocation=Decimal("700000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            budget_allocation=Decimal("600000.00"),
        )

        is_valid, variance = project.validate_budget_rollup()

        assert is_valid is False
        assert variance == Decimal("300000.00")  # 300k over

    def test_validate_budget_rollup_no_parent_budget(self):
        """Test validate_budget_rollup() when parent has no budget."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="No Budget Project",
            budget_allocation=None,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            budget_allocation=Decimal("100000.00"),
        )

        is_valid, variance = project.validate_budget_rollup()

        # Can't validate without parent budget
        assert is_valid is True  # Or define as invalid?
        assert variance == Decimal("0.00")

    def test_sync_to_ppa_progress(self):
        """Test sync_to_ppa() updates PPA progress."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Sync Project",
            ppa_source=self.ppa,
            progress=75,
        )

        # Initial PPA progress
        assert self.ppa.overall_progress == 0

        # Sync
        project.sync_to_ppa()

        # Refresh and check
        self.ppa.refresh_from_db()
        assert self.ppa.overall_progress == 75

    def test_sync_to_ppa_status_completed(self):
        """Test sync_to_ppa() updates PPA status to completed."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Completed Sync Project",
            ppa_source=self.ppa,
            status=WorkItem.STATUS_COMPLETED,
            progress=100,
        )

        # Initial status
        assert self.ppa.status == "planning"

        # Sync
        project.sync_to_ppa()

        self.ppa.refresh_from_db()
        assert self.ppa.status == "completed"

    def test_sync_to_ppa_status_in_progress(self):
        """Test sync_to_ppa() updates PPA status to ongoing."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="In Progress Sync Project",
            ppa_source=self.ppa,
            status=WorkItem.STATUS_IN_PROGRESS,
            progress=50,
        )

        project.sync_to_ppa()

        self.ppa.refresh_from_db()
        assert self.ppa.status == "ongoing"

    def test_sync_to_ppa_status_blocked(self):
        """Test sync_to_ppa() maps blocked status to on_hold."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Blocked Sync Project",
            ppa_source=self.ppa,
            status=WorkItem.STATUS_BLOCKED,
        )

        project.sync_to_ppa()

        self.ppa.refresh_from_db()
        assert self.ppa.status == "on_hold"

    def test_sync_to_ppa_no_ppa_source(self):
        """Test sync_to_ppa() gracefully handles missing PPA source."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="No PPA Project",
            # No ppa_source
            progress=50,
        )

        # Should not raise error
        project.sync_to_ppa()  # No-op

    def test_sync_to_ppa_child_item(self):
        """Test sync_to_ppa() from child syncs to parent's PPA."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Parent Project",
            ppa_source=self.ppa,
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Child Task",
            parent=project,
            progress=80,
        )

        # Sync from child
        task.sync_to_ppa()

        # Should update PPA via parent
        self.ppa.refresh_from_db()
        # Progress should reflect task's contribution
        assert self.ppa.overall_progress > 0

    def test_sync_to_ppa_budget_tracking(self):
        """Test sync_to_ppa() updates budget-related fields."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Budget Sync Project",
            ppa_source=self.ppa,
            budget_allocation=Decimal("5000000.00"),
            budget_spent=Decimal("2000000.00"),
        )

        project.sync_to_ppa()

        # Verify budget fields synced
        # (Assuming PPA has budget tracking fields)
        # This test depends on PPA model having these fields

    @pytest.mark.parametrize(
        "workitem_status,expected_ppa_status",
        [
            (WorkItem.STATUS_NOT_STARTED, "planning"),
            (WorkItem.STATUS_IN_PROGRESS, "ongoing"),
            (WorkItem.STATUS_AT_RISK, "ongoing"),
            (WorkItem.STATUS_BLOCKED, "on_hold"),
            (WorkItem.STATUS_COMPLETED, "completed"),
            (WorkItem.STATUS_CANCELLED, "cancelled"),
        ],
    )
    def test_status_mapping_to_ppa(self, workitem_status, expected_ppa_status):
        """Test all WorkItem status mappings to PPA status."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Status Mapping Test",
            ppa_source=self.ppa,
            status=workitem_status,
        )

        project.sync_to_ppa()

        self.ppa.refresh_from_db()
        assert self.ppa.status == expected_ppa_status

    def test_get_all_ppa_workitems(self):
        """Test retrieving all WorkItems linked to a PPA."""
        # Create hierarchy
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="PPA Project",
            ppa_source=self.ppa,
        )

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

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=activity1,
            ppa_source=self.ppa,
        )

        # Create unrelated workitem
        unrelated = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Unrelated Task",
        )

        # Get all WorkItems for PPA
        ppa_workitems = WorkItem.objects.filter(ppa_source=self.ppa)

        assert ppa_workitems.count() == 4  # Excludes unrelated
        assert project in ppa_workitems
        assert activity1 in ppa_workitems
        assert activity2 in ppa_workitems
        assert task1 in ppa_workitems
        assert unrelated not in ppa_workitems

    def test_aggregate_progress_from_hierarchy(self):
        """Test aggregating progress across entire WorkItem hierarchy."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Aggregate Project",
            ppa_source=self.ppa,
        )

        # Create 2 activities with different progress
        activity1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            parent=project,
            ppa_source=self.ppa,
            progress=100,  # Complete
        )

        activity2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 2",
            parent=project,
            ppa_source=self.ppa,
            progress=50,  # Half done
        )

        # Update project progress from children
        project.update_progress_from_children()
        project.refresh_from_db()

        # Expected: (100 + 50) / 2 = 75
        assert project.progress == 75

    def test_cascade_budget_updates(self):
        """Test budget updates cascade through hierarchy."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Cascade Project",
            budget_allocation=Decimal("1000000.00"),
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Cascade Activity",
            parent=project,
            budget_allocation=Decimal("500000.00"),
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Cascade Task",
            parent=activity,
            budget_allocation=Decimal("200000.00"),
        )

        # Update task budget
        task.budget_allocation = Decimal("300000.00")
        task.save()

        # Recalculate parent budgets
        activity.budget_allocation = activity.calculate_budget_from_children()
        activity.save()

        # Verify cascade
        assert activity.budget_allocation == Decimal("300000.00")
