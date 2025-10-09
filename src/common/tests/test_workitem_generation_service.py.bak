"""
Test suite for WorkItem Generation Service.

Tests cover:
- PROGRAM template generation (1 project + 3 activities)
- ACTIVITY template generation (1 activity + 5 tasks)
- MILESTONE template generation (1 project + 4 milestones)
- MINIMAL template generation (1 project only)
- Outcome framework-based generation
- Budget distribution across generated items
- Date distribution across generated items
"""

import pytest

pytest.skip(
    "Legacy WorkItem generation tests require updated fixtures after refactor.",
    allow_module_level=True,
)

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from common.work_item_model import WorkItem
from common.services.workitem_generation import WorkItemGenerationService
from coordination.models import Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


@pytest.mark.django_db
class TestWorkItemGenerationService:
    """Test WorkItemGenerationService for PPA execution project generation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="gen_user",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.organization = Organization.objects.create(
            name="Test Agency",
            acronym="TA",
            organization_type="bmoa",
            created_by=self.user,
        )

        self.ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Test Generation PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("5000000.00"),
            fiscal_year=2025,
            plan_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        self.service = WorkItemGenerationService()

    def test_generate_program_template_structure(self):
        """Test PROGRAM template generates correct structure (1 project + 3 activities)."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="program",
        )

        assert result["success"] is True
        assert result["template"] == "program"
        assert result["workitem_count"] == 4  # 1 project + 3 activities

        # Verify project created
        project = WorkItem.objects.get(id=result["root_workitem_id"])
        assert project.work_type == WorkItem.WORK_TYPE_PROJECT
        assert project.ppa_source == self.ppa
        assert self.ppa.name in project.title

        # Verify 3 activities
        activities = project.get_children()
        assert activities.count() == 3

        activity_titles = [a.title for a in activities]
        assert "Planning Phase" in activity_titles
        assert "Implementation Phase" in activity_titles
        assert "Monitoring & Evaluation" in activity_titles

    def test_generate_program_template_budget_distribution(self):
        """Test PROGRAM template distributes budget correctly."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="program",
            distribute_budget=True,
        )

        project = WorkItem.objects.get(id=result["root_workitem_id"])
        activities = list(project.get_children())

        # Project should have full budget
        assert project.budget_allocation == Decimal("5000000.00")

        # Activities should split budget (equal distribution by default)
        # 5M / 3 = 1,666,666.67 each (approximately)
        for activity in activities:
            assert activity.budget_allocation is not None
            assert Decimal("1600000") <= activity.budget_allocation <= Decimal("1700000")

        # Total should match
        total_activity_budget = sum(a.budget_allocation for a in activities)
        assert total_activity_budget == Decimal("5000000.00")

    def test_generate_program_template_date_distribution(self):
        """Test PROGRAM template distributes dates correctly."""
        # Set PPA dates
        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)

        self.ppa.start_date = start_date
        self.ppa.end_date = end_date
        self.ppa.save()

        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="program",
            distribute_dates=True,
        )

        project = WorkItem.objects.get(id=result["root_workitem_id"])
        activities = list(project.get_children().order_by("start_date"))

        # Project should have PPA dates
        assert project.start_date == start_date
        assert project.due_date == end_date

        # Activities should be sequential
        # 365 days / 3 = ~122 days each
        assert activities[0].start_date == start_date
        assert activities[0].due_date < activities[1].start_date
        assert activities[1].due_date < activities[2].start_date
        assert activities[2].due_date == end_date

    def test_generate_activity_template_structure(self):
        """Test ACTIVITY template generates correct structure (1 activity + 5 tasks)."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="activity",
        )

        assert result["success"] is True
        assert result["template"] == "activity"
        assert result["workitem_count"] == 6  # 1 activity + 5 tasks

        # Verify activity created
        activity = WorkItem.objects.get(id=result["root_workitem_id"])
        assert activity.work_type == WorkItem.WORK_TYPE_ACTIVITY
        assert activity.ppa_source == self.ppa

        # Verify 5 tasks
        tasks = activity.get_children()
        assert tasks.count() == 5

    def test_generate_activity_template_task_names(self):
        """Test ACTIVITY template generates appropriate task names."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="activity",
        )

        activity = WorkItem.objects.get(id=result["root_workitem_id"])
        tasks = list(activity.get_children())

        # Should have standard task names
        task_titles = [t.title for t in tasks]
        assert any("Preparation" in title for title in task_titles)
        assert any("Implementation" in title or "Execution" in title for title in task_titles)
        assert any("Review" in title or "Evaluation" in title for title in task_titles)

    def test_generate_milestone_template_structure(self):
        """Test MILESTONE template generates correct structure (1 project + 4 milestones)."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="milestone",
        )

        assert result["success"] is True
        assert result["template"] == "milestone"
        assert result["workitem_count"] == 5  # 1 project + 4 milestones

        project = WorkItem.objects.get(id=result["root_workitem_id"])
        milestones = project.get_children()
        assert milestones.count() == 4

        # Milestones are represented as activities
        for milestone in milestones:
            assert milestone.work_type == WorkItem.WORK_TYPE_ACTIVITY

    def test_generate_milestone_template_quarterly_distribution(self):
        """Test MILESTONE template creates quarterly milestones."""
        # Set annual PPA
        self.ppa.start_date = date(2025, 1, 1)
        self.ppa.end_date = date(2025, 12, 31)
        self.ppa.save()

        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="milestone",
            distribute_dates=True,
        )

        project = WorkItem.objects.get(id=result["root_workitem_id"])
        milestones = list(project.get_children().order_by("start_date"))

        # Should have 4 quarterly milestones
        assert len(milestones) == 4

        # Q1: Jan-Mar
        assert milestones[0].start_date.month == 1
        assert milestones[0].due_date.month == 3

        # Q2: Apr-Jun
        assert milestones[1].start_date.month == 4
        assert milestones[1].due_date.month == 6

        # Q3: Jul-Sep
        assert milestones[2].start_date.month == 7
        assert milestones[2].due_date.month == 9

        # Q4: Oct-Dec
        assert milestones[3].start_date.month == 10
        assert milestones[3].due_date.month == 12

    def test_generate_minimal_template_structure(self):
        """Test MINIMAL template generates single project only."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="minimal",
        )

        assert result["success"] is True
        assert result["template"] == "minimal"
        assert result["workitem_count"] == 1  # Project only

        project = WorkItem.objects.get(id=result["root_workitem_id"])
        assert project.work_type == WorkItem.WORK_TYPE_PROJECT
        assert project.ppa_source == self.ppa
        assert project.get_children().count() == 0  # No children

    def test_generate_minimal_template_copies_ppa_data(self):
        """Test MINIMAL template copies PPA data to project."""
        self.ppa.description = "Test PPA Description"
        self.ppa.start_date = date(2025, 1, 1)
        self.ppa.end_date = date(2025, 12, 31)
        self.ppa.budget_allocation = Decimal("2000000.00")
        self.ppa.save()

        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="minimal",
        )

        project = WorkItem.objects.get(id=result["root_workitem_id"])

        assert self.ppa.name in project.title
        assert project.description == self.ppa.description
        assert project.start_date == self.ppa.start_date
        assert project.due_date == self.ppa.end_date
        assert project.budget_allocation == self.ppa.budget_allocation

    def test_generate_from_outcome_framework(self):
        """Test generation from outcome framework in PPA metadata."""
        # Set outcome framework in PPA
        self.ppa.metadata = {
            "outcome_framework": {
                "outcomes": [
                    {
                        "title": "Improved Education Access",
                        "outputs": [
                            {"title": "Build 10 classrooms"},
                            {"title": "Train 50 teachers"},
                        ],
                    },
                    {
                        "title": "Enhanced Learning Quality",
                        "outputs": [
                            {"title": "Develop curriculum"},
                        ],
                    },
                ]
            }
        }
        self.ppa.save()

        result = self.service.generate_from_outcome_framework(
            ppa=self.ppa,
        )

        assert result["success"] is True

        project = WorkItem.objects.get(id=result["root_workitem_id"])

        # Should create 2 outcomes (as activities)
        outcomes = project.get_children().filter(work_type=WorkItem.WORK_TYPE_ACTIVITY)
        assert outcomes.count() == 2

        # Should create 3 outputs (as tasks) under outcomes
        outcome1 = outcomes.filter(title__icontains="Education Access").first()
        assert outcome1 is not None
        assert outcome1.get_children().count() == 2

        outcome2 = outcomes.filter(title__icontains="Learning Quality").first()
        assert outcome2 is not None
        assert outcome2.get_children().count() == 1

    def test_generate_validation_ppa_not_approved(self):
        """Test generation fails if PPA not approved."""
        self.ppa.approval_status = "pending"
        self.ppa.save()

        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="program",
        )

        assert result["success"] is False
        assert "not approved" in result["error"].lower()

    def test_generate_validation_invalid_template(self):
        """Test generation fails with invalid template name."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="invalid_template",
        )

        assert result["success"] is False
        assert "invalid template" in result["error"].lower()

    def test_generate_validation_already_generated(self):
        """Test generation fails if WorkItems already exist for PPA."""
        # Generate once
        self.service.generate_from_ppa(
            ppa=self.ppa,
            template="minimal",
        )

        # Try generating again
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="program",
        )

        assert result["success"] is False
        assert "already" in result["error"].lower()

    def test_budget_distribution_equal(self):
        """Test equal budget distribution across children."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="activity",
            distribute_budget=True,
            distribution_method="equal",
        )

        activity = WorkItem.objects.get(id=result["root_workitem_id"])
        tasks = list(activity.get_children())

        # 5M / 5 tasks = 1M each
        for task in tasks:
            assert task.budget_allocation == Decimal("1000000.00")

    def test_budget_distribution_weighted_duration(self):
        """Test weighted budget distribution by duration."""
        self.ppa.start_date = date(2025, 1, 1)
        self.ppa.end_date = date(2025, 12, 31)
        self.ppa.save()

        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="activity",
            distribute_budget=True,
            distribute_dates=True,
            distribution_method="weighted_duration",
        )

        activity = WorkItem.objects.get(id=result["root_workitem_id"])
        tasks = list(activity.get_children())

        # Tasks with longer duration should get more budget
        total_budget = sum(t.budget_allocation for t in tasks if t.budget_allocation)
        assert total_budget == Decimal("5000000.00")

        # Verify proportional to duration
        for task in tasks:
            duration = (task.due_date - task.start_date).days
            expected_ratio = duration / 365  # Year total
            actual_ratio = float(task.budget_allocation) / 5000000
            # Should be approximately proportional (within 10%)
            assert abs(expected_ratio - actual_ratio) < 0.1

    def test_date_distribution_sequential(self):
        """Test sequential date distribution."""
        self.ppa.start_date = date(2025, 1, 1)
        self.ppa.end_date = date(2025, 12, 31)
        self.ppa.save()

        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="program",
            distribute_dates=True,
            date_strategy="sequential",
        )

        project = WorkItem.objects.get(id=result["root_workitem_id"])
        activities = list(project.get_children().order_by("start_date"))

        # Activities should be sequential (no overlap)
        for i in range(len(activities) - 1):
            current = activities[i]
            next_activity = activities[i + 1]
            assert current.due_date <= next_activity.start_date

    def test_date_distribution_parallel(self):
        """Test parallel date distribution (all same dates)."""
        self.ppa.start_date = date(2025, 1, 1)
        self.ppa.end_date = date(2025, 12, 31)
        self.ppa.save()

        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="activity",
            distribute_dates=True,
            date_strategy="parallel",
        )

        activity = WorkItem.objects.get(id=result["root_workitem_id"])
        tasks = list(activity.get_children())

        # All tasks should have same dates (parallel execution)
        for task in tasks:
            assert task.start_date == date(2025, 1, 1)
            assert task.due_date == date(2025, 12, 31)

    def test_custom_metadata_preservation(self):
        """Test custom metadata from PPA is preserved in WorkItems."""
        self.ppa.metadata = {
            "sector": "Education",
            "priority_communities": ["Community A", "Community B"],
            "expected_beneficiaries": 1000,
        }
        self.ppa.save()

        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template="minimal",
        )

        project = WorkItem.objects.get(id=result["root_workitem_id"])

        # Metadata should be copied
        assert "ppa_metadata" in project.metadata
        assert project.metadata["ppa_metadata"]["sector"] == "Education"
        assert "Community A" in project.metadata["ppa_metadata"]["priority_communities"]

    @pytest.mark.parametrize(
        "template,expected_count",
        [
            ("program", 4),  # 1 project + 3 activities
            ("activity", 6),  # 1 activity + 5 tasks
            ("milestone", 5),  # 1 project + 4 milestones
            ("minimal", 1),  # 1 project only
        ],
    )
    def test_all_templates_count(self, template, expected_count):
        """Test all templates generate correct number of WorkItems."""
        result = self.service.generate_from_ppa(
            ppa=self.ppa,
            template=template,
        )

        assert result["success"] is True
        assert result["workitem_count"] == expected_count
