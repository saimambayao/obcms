"""
Comprehensive test suite for MonitoringEntry and WorkItem integration.

Tests cover:
- Execution project creation from approved PPAs
- Progress synchronization from WorkItem to MonitoringEntry
- Status mapping between systems
- Budget allocation tree generation
- Budget distribution validation
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from common.models import Region, Province, Municipality, Barangay
from common.work_item_model import WorkItem
from communities.models import OBCCommunity
from coordination.models import Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


@pytest.mark.django_db
class TestMonitoringEntryWorkItemIntegration:
    """Test MonitoringEntry integration with WorkItem system."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        # Create user
        self.user = User.objects.create_user(
            username="test_user",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        # Create geographic hierarchy
        self.region = Region.objects.create(
            code="R09",
            name="Zamboanga Peninsula",
            center_coordinates=[123.3, 7.9],
        )
        self.province = Province.objects.create(
            region=self.region,
            code="ZDS",
            name="Zamboanga del Sur",
            center_coordinates=[123.4, 7.8],
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="PAG",
            name="Pagadian City",
            center_coordinates=[123.5, 7.7],
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRG-01",
            name="Kawit",
            center_coordinates=[123.6, 7.6],
        )

        # Create organization
        self.implementing_moa = Organization.objects.create(
            name="Ministry of Social Services",
            acronym="MSS",
            organization_type="bmoa",
            created_by=self.user,
        )

    def test_create_execution_project_program_template(self):
        """Test creating execution project with PROGRAM template (1 project + 3 activities)."""
        # Create MOA PPA
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Community Development Program",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("1000000.00"),
            fiscal_year=2025,
            plan_year=2025,
            status="planning",
            approval_status="approved",
            coverage_region=self.region,
            created_by=self.user,
        )

        # Enable WorkItem tracking with PROGRAM template
        result = ppa.enable_workitem_tracking(
            template="program",
            auto_activate=False,
        )

        assert result["success"] is True
        assert result["workitem_count"] == 4  # 1 project + 3 activities

        # Verify project created
        project = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title__contains="Community Development Program",
        ).first()
        assert project is not None
        assert project.parent is None  # Top-level project

        # Verify 3 activities created
        activities = project.get_children().filter(
            work_type=WorkItem.WORK_TYPE_ACTIVITY
        )
        assert activities.count() == 3

        # Verify activity titles
        activity_titles = [a.title for a in activities]
        assert "Planning Phase" in activity_titles
        assert "Implementation Phase" in activity_titles
        assert "Monitoring & Evaluation" in activity_titles

        # Verify ppa_source set
        for activity in activities:
            assert activity.ppa_source == ppa

    def test_create_execution_project_activity_template(self):
        """Test creating execution project with ACTIVITY template (1 activity + 5 tasks)."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Water System Installation",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("500000.00"),
            fiscal_year=2025,
            plan_year=2025,
            status="planning",
            approval_status="approved",
            coverage_municipality=self.municipality,
            created_by=self.user,
        )

        result = ppa.enable_workitem_tracking(
            template="activity",
            auto_activate=False,
        )

        assert result["success"] is True
        assert result["workitem_count"] == 6  # 1 activity + 5 tasks

        # Verify activity created
        activity = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title__contains="Water System Installation",
        ).first()
        assert activity is not None
        assert activity.ppa_source == ppa

        # Verify 5 tasks created
        tasks = activity.get_children().filter(work_type=WorkItem.WORK_TYPE_TASK)
        assert tasks.count() == 5

    def test_create_execution_project_milestone_template(self):
        """Test creating execution project with MILESTONE template (1 project + 4 milestones)."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Infrastructure Modernization",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("2000000.00"),
            fiscal_year=2025,
            plan_year=2025,
            status="planning",
            approval_status="approved",
            coverage_province=self.province,
            created_by=self.user,
        )

        result = ppa.enable_workitem_tracking(
            template="milestone",
            auto_activate=False,
        )

        assert result["success"] is True
        assert result["workitem_count"] == 5  # 1 project + 4 milestones

        project = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title__contains="Infrastructure Modernization",
        ).first()
        assert project is not None

        milestones = project.get_children().filter(
            work_type=WorkItem.WORK_TYPE_ACTIVITY  # Milestones are activities
        )
        assert milestones.count() == 4

    def test_create_execution_project_minimal_template(self):
        """Test creating execution project with MINIMAL template (1 project only)."""
        ppa = MonitoringEntry.objects.create(
            category="oobc_ppa",
            name="Policy Research Initiative",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("100000.00"),
            fiscal_year=2025,
            plan_year=2025,
            status="planning",
            approval_status="approved",
            created_by=self.user,
        )

        result = ppa.enable_workitem_tracking(
            template="minimal",
            auto_activate=False,
        )

        assert result["success"] is True
        assert result["workitem_count"] == 1  # 1 project only

        project = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title__contains="Policy Research Initiative",
        ).first()
        assert project is not None
        assert project.ppa_source == ppa
        assert project.get_children().count() == 0  # No children

    def test_create_execution_project_validation_not_approved(self):
        """Test that execution project creation fails if PPA not approved."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Pending Approval PPA",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("500000.00"),
            fiscal_year=2025,
            approval_status="pending",  # Not approved
            created_by=self.user,
        )

        result = ppa.enable_workitem_tracking(template="program")

        assert result["success"] is False
        assert "not approved" in result["error"].lower()

    def test_create_execution_project_validation_already_enabled(self):
        """Test that duplicate execution project creation is prevented."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Enabled PPA",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("500000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        # Enable first time
        ppa.enable_workitem_tracking(template="minimal")

        # Try enabling again
        result = ppa.enable_workitem_tracking(template="minimal")

        assert result["success"] is False
        assert "already enabled" in result["error"].lower()

    def test_sync_progress_from_workitem_single_level(self):
        """Test progress sync from single-level WorkItem (1 project with tasks)."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Simple Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("300000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        # Create project manually
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Simple Project",
            ppa_source=ppa,
            progress=0,
        )

        # Create 4 tasks with different progress
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            progress=100,  # Completed
            ppa_source=ppa,
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            progress=50,  # Half done
            ppa_source=ppa,
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            parent=project,
            progress=25,  # Quarter done
            ppa_source=ppa,
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 4",
            parent=project,
            progress=0,  # Not started
            ppa_source=ppa,
        )

        # Sync progress
        ppa.sync_progress_from_workitem()
        ppa.refresh_from_db()

        # Expected: (100 + 50 + 25 + 0) / 4 = 43.75 → 44
        assert ppa.overall_progress == 44

    def test_sync_progress_from_workitem_multi_level(self):
        """Test progress sync from multi-level WorkItem hierarchy."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Complex Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("1000000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        # Create project
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Complex Project",
            ppa_source=ppa,
        )

        # Create 2 activities
        activity1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            parent=project,
            progress=100,  # Completed
            ppa_source=ppa,
        )
        activity2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 2",
            parent=project,
            progress=50,  # Half done
            ppa_source=ppa,
        )

        # Sync progress
        ppa.sync_progress_from_workitem()
        ppa.refresh_from_db()

        # Expected: (100 + 50) / 2 = 75
        assert ppa.overall_progress == 75

    def test_sync_status_from_workitem_completed(self):
        """Test status sync when all WorkItems are completed."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Completed Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("500000.00"),
            fiscal_year=2025,
            approval_status="approved",
            status="ongoing",  # Initial status
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Completed Project",
            ppa_source=ppa,
            status=WorkItem.STATUS_COMPLETED,
            progress=100,
        )

        # Sync status
        ppa.sync_status_from_workitem()
        ppa.refresh_from_db()

        assert ppa.status == "completed"

    def test_sync_status_from_workitem_blocked(self):
        """Test status sync when WorkItems are blocked."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Blocked Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("500000.00"),
            fiscal_year=2025,
            approval_status="approved",
            status="ongoing",
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Blocked Project",
            ppa_source=ppa,
            status=WorkItem.STATUS_BLOCKED,
        )

        ppa.sync_status_from_workitem()
        ppa.refresh_from_db()

        assert ppa.status == "on_hold"  # Blocked maps to on_hold

    def test_get_budget_allocation_tree_simple(self):
        """Test budget allocation tree for simple project structure."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Simple Budget Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("1000000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Simple Budget Project",
            ppa_source=ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            ppa_source=ppa,
            budget_allocation=Decimal("400000.00"),
        )
        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            ppa_source=ppa,
            budget_allocation=Decimal("600000.00"),
        )

        tree = ppa.get_budget_allocation_tree()

        assert tree["total_budget"] == Decimal("1000000.00")
        assert len(tree["items"]) == 1  # 1 project
        assert tree["items"][0]["title"] == "Simple Budget Project"
        assert len(tree["items"][0]["children"]) == 2  # 2 tasks
        assert tree["variance"] == Decimal("0.00")  # No variance

    def test_get_budget_allocation_tree_variance(self):
        """Test budget allocation tree detects variance."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Variance Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("1000000.00"),  # PPA budget
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Variance Project",
            ppa_source=ppa,
            budget_allocation=Decimal("1200000.00"),  # Over budget!
        )

        tree = ppa.get_budget_allocation_tree()

        assert tree["total_budget"] == Decimal("1000000.00")
        assert tree["allocated_to_workitems"] == Decimal("1200000.00")
        assert tree["variance"] == Decimal("200000.00")  # Over by 200k
        assert tree["has_variance"] is True

    def test_validate_budget_distribution_valid(self):
        """Test budget distribution validation with valid allocation."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Valid Budget Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("1000000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Valid Budget Project",
            ppa_source=ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        # Create tasks that sum exactly to project budget
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            ppa_source=ppa,
            budget_allocation=Decimal("300000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            ppa_source=ppa,
            budget_allocation=Decimal("700000.00"),
        )

        result = ppa.validate_budget_distribution()

        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_budget_distribution_over_budget(self):
        """Test budget distribution validation detects over-allocation."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Over Budget Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("1000000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Over Budget Project",
            ppa_source=ppa,
            budget_allocation=Decimal("1000000.00"),
        )

        # Tasks exceed project budget
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            ppa_source=ppa,
            budget_allocation=Decimal("600000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            ppa_source=ppa,
            budget_allocation=Decimal("600000.00"),  # Total: 1.2M > 1M
        )

        result = ppa.validate_budget_distribution()

        assert result["valid"] is False
        assert len(result["issues"]) > 0
        assert any("exceeds" in issue["message"].lower() for issue in result["issues"])

    def test_validate_budget_distribution_missing_allocation(self):
        """Test budget distribution validation detects missing allocations."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Missing Budget Project",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("1000000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Missing Budget Project",
            ppa_source=ppa,
            budget_allocation=None,  # Missing allocation!
        )

        result = ppa.validate_budget_distribution()

        assert result["valid"] is False
        assert any(
            "missing budget" in issue["message"].lower() for issue in result["issues"]
        )


@pytest.mark.django_db
class TestWorkItemPPAMethods:
    """Test WorkItem methods for PPA integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="test_user",
            password="testpass123",
        )

        self.implementing_moa = Organization.objects.create(
            name="Test Organization",
            acronym="TO",
            organization_type="bmoa",
            created_by=self.user,
        )

    def test_get_ppa_source_direct_fk(self):
        """Test get_ppa_source with direct FK."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Direct PPA",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("500000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        workitem = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Direct Project",
            ppa_source=ppa,  # Direct FK
        )

        assert workitem.get_ppa_source() == ppa

    def test_get_ppa_source_parent_traversal(self):
        """Test get_ppa_source via MPTT parent traversal."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Parent PPA",
            implementing_moa=self.implementing_moa,
            budget_allocation=Decimal("500000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        # Create hierarchy
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Parent Project",
            ppa_source=ppa,  # Only project has FK
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Child Activity",
            parent=project,
            # No direct ppa_source
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Grandchild Task",
            parent=activity,
            # No direct ppa_source
        )

        # Task should find PPA via parent traversal
        assert task.get_ppa_source() == ppa
        assert activity.get_ppa_source() == ppa

    def test_calculate_budget_from_children(self):
        """Test automatic budget calculation from children."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Auto Budget Project",
            budget_allocation=None,  # Will be calculated
        )

        # Create child tasks with budgets
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            budget_allocation=Decimal("250000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            budget_allocation=Decimal("350000.00"),
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            parent=project,
            budget_allocation=Decimal("400000.00"),
        )

        calculated = project.calculate_budget_from_children()

        # Expected: 250k + 350k + 400k = 1M
        assert calculated == Decimal("1000000.00")
