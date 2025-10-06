"""
WorkItem Model Tests

Tests for the unified work hierarchy model (Phase 5 - Comprehensive Testing).

Test Coverage:
- Model creation (Projects, Activities, Tasks)
- MPTT hierarchy operations (get_ancestors, get_descendants, get_children)
- Validation rules (parent-child type restrictions)
- Auto-progress calculation from children
- Calendar integration
- Type-specific data JSON fields
- Breadcrumb generation
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()


@pytest.mark.django_db
class TestWorkItemCreation:
    """Test WorkItem creation for all types."""

    def test_create_project(self):
        """Test creating a top-level project."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="MANA Assessment Project",
            description="Complete MANA assessment for Region XII",
            start_date=date.today(),
            due_date=date.today() + timedelta(days=90),
            priority=WorkItem.PRIORITY_HIGH,
        )

        assert project.id is not None
        assert project.work_type == WorkItem.WORK_TYPE_PROJECT
        assert project.parent is None
        assert project.is_project is True
        assert project.is_activity is False
        assert project.is_task is False
        assert project.status == WorkItem.STATUS_NOT_STARTED
        assert project.progress == 0

    def test_create_activity(self):
        """Test creating an activity under a project."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Community Engagement Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Stakeholder Consultation Workshop",
            parent=project,
            activity_data={
                "event_type": "workshop",
                "location": "Cotabato City",
                "venue": "OOBC Main Office",
            },
        )

        assert activity.parent == project
        assert activity.is_activity is True
        assert activity.event_type == "workshop"
        assert activity.activity_data["location"] == "Cotabato City"

    def test_create_task(self):
        """Test creating a task under an activity."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Data Collection Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Field Survey",
            parent=project,
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Interview community leaders",
            parent=activity,
            task_data={
                "domain": "mana",
                "deliverable_type": "survey_data",
            },
        )

        assert task.parent == activity
        assert task.is_task is True
        assert task.domain == "mana"
        assert task.task_data["deliverable_type"] == "survey_data"

    def test_create_subtask(self):
        """Test creating a subtask under a task."""
        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Prepare workshop materials",
        )

        subtask = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUBTASK,
            title="Design presentation slides",
            parent=task,
        )

        assert subtask.parent == task
        assert subtask.work_type == WorkItem.WORK_TYPE_SUBTASK
        assert subtask.is_task is True


@pytest.mark.django_db
class TestWorkItemHierarchy:
    """Test MPTT hierarchy operations."""

    def test_get_ancestors(self):
        """Test retrieving ancestors."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Main Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Workshop Activity",
            parent=project,
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Prepare materials",
            parent=activity,
        )

        ancestors = task.get_ancestors()
        assert ancestors.count() == 2
        assert project in ancestors
        assert activity in ancestors

    def test_get_descendants(self):
        """Test retrieving descendants."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Main Project",
        )

        activity1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            parent=project,
        )

        activity2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 2",
            parent=project,
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=activity1,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=activity2,
        )

        descendants = project.get_descendants()
        assert descendants.count() == 4
        assert activity1 in descendants
        assert activity2 in descendants
        assert task1 in descendants
        assert task2 in descendants

    def test_get_children(self):
        """Test retrieving immediate children."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        activity1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            parent=project,
        )

        activity2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 2",
            parent=project,
        )

        # Task under activity1 (should NOT be in project.get_children())
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            parent=activity1,
        )

        children = project.get_children()
        assert children.count() == 2
        assert activity1 in children
        assert activity2 in children

    def test_get_root_project(self):
        """Test getting the root project."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Root Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity",
            parent=project,
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            parent=activity,
        )

        assert task.get_root_project() == project
        assert activity.get_root_project() == project
        assert project.get_root_project() == project

    def test_get_all_tasks(self):
        """Test getting all tasks under a work item."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity",
            parent=project,
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=activity,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=activity,
        )

        subtask = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUBTASK,
            title="Subtask",
            parent=task1,
        )

        all_tasks = project.get_all_tasks()
        assert all_tasks.count() == 3
        assert task1 in all_tasks
        assert task2 in all_tasks
        assert subtask in all_tasks


@pytest.mark.django_db
class TestWorkItemValidation:
    """Test validation rules."""

    def test_validate_parent_child_type_valid(self):
        """Test valid parent-child relationships."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        # Valid: Project can have Activity
        activity = WorkItem(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity",
            parent=project,
        )
        activity.full_clean()  # Should not raise

        # Valid: Activity can have Task
        task = WorkItem(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            parent=activity,
        )
        task.save()
        task.full_clean()  # Should not raise

    def test_validate_parent_child_type_invalid(self):
        """Test invalid parent-child relationships."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        # Invalid: Project cannot have Project as parent
        with pytest.raises(ValidationError) as exc_info:
            invalid_child = WorkItem(
                work_type=WorkItem.WORK_TYPE_PROJECT,
                title="Child Project",
                parent=project,
            )
            invalid_child.full_clean()

        assert "cannot have" in str(exc_info.value)

    def test_validate_subtask_no_children(self):
        """Test that subtasks cannot have children."""
        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
        )

        subtask = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUBTASK,
            title="Subtask",
            parent=task,
        )

        # Subtask cannot have any children
        with pytest.raises(ValidationError):
            invalid_child = WorkItem(
                work_type=WorkItem.WORK_TYPE_SUBTASK,
                title="Invalid child",
                parent=subtask,
            )
            invalid_child.full_clean()

    def test_validate_date_range(self):
        """Test date validation."""
        with pytest.raises(ValidationError) as exc_info:
            item = WorkItem(
                work_type=WorkItem.WORK_TYPE_TASK,
                title="Task",
                start_date=date(2025, 12, 31),
                due_date=date(2025, 1, 1),
            )
            item.full_clean()

        assert "Due date must be after start date" in str(exc_info.value)

    def test_can_have_child_type(self):
        """Test can_have_child_type method."""
        project = WorkItem(work_type=WorkItem.WORK_TYPE_PROJECT, title="Project")
        task = WorkItem(work_type=WorkItem.WORK_TYPE_TASK, title="Task")
        subtask = WorkItem(work_type=WorkItem.WORK_TYPE_SUBTASK, title="Subtask")

        # Project can have Sub-Project, Activity, Task
        assert project.can_have_child_type(WorkItem.WORK_TYPE_SUB_PROJECT)
        assert project.can_have_child_type(WorkItem.WORK_TYPE_ACTIVITY)
        assert project.can_have_child_type(WorkItem.WORK_TYPE_TASK)
        assert not project.can_have_child_type(WorkItem.WORK_TYPE_SUBTASK)

        # Task can have Subtask
        assert task.can_have_child_type(WorkItem.WORK_TYPE_SUBTASK)
        assert not task.can_have_child_type(WorkItem.WORK_TYPE_TASK)

        # Subtask cannot have children
        assert not subtask.can_have_child_type(WorkItem.WORK_TYPE_SUBTASK)


@pytest.mark.django_db
class TestWorkItemProgressCalculation:
    """Test auto-progress calculation."""

    def test_calculate_progress_from_children(self):
        """Test progress calculation based on child completion."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            auto_calculate_progress=True,
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            status=WorkItem.STATUS_COMPLETED,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            status=WorkItem.STATUS_IN_PROGRESS,
        )

        task3 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 3",
            parent=project,
            status=WorkItem.STATUS_NOT_STARTED,
        )

        # 1 out of 3 tasks completed = 33% (integer division)
        calculated = project.calculate_progress_from_children()
        assert calculated == 33

    def test_update_progress(self):
        """Test progress update and propagation."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            auto_calculate_progress=True,
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity",
            parent=project,
            auto_calculate_progress=True,
        )

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=activity,
            status=WorkItem.STATUS_COMPLETED,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=activity,
            status=WorkItem.STATUS_COMPLETED,
        )

        # Update activity progress
        activity.update_progress()
        activity.refresh_from_db()
        assert activity.progress == 100

        # Progress should propagate to project
        project.refresh_from_db()
        # Project has 1 child (activity) at 100% = 100%
        assert project.progress == 100

    def test_manual_progress_no_auto_calculate(self):
        """Test that auto_calculate_progress=False preserves manual progress."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            auto_calculate_progress=False,
            progress=50,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            parent=project,
            status=WorkItem.STATUS_COMPLETED,
        )

        project.update_progress()
        project.refresh_from_db()
        # Should remain 50 (manual)
        assert project.progress == 50


@pytest.mark.django_db
class TestWorkItemCalendarIntegration:
    """Test calendar integration methods."""

    def test_get_calendar_event(self):
        """Test FullCalendar event generation."""
        user = User.objects.create_user(
            username="testuser",
            first_name="John",
            last_name="Doe",
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Important Task",
            start_date=date(2025, 10, 15),
            due_date=date(2025, 10, 20),
            status=WorkItem.STATUS_IN_PROGRESS,
            priority=WorkItem.PRIORITY_HIGH,
            progress=75,
            calendar_color="#F59E0B",
        )
        task.assignees.add(user)

        event = task.get_calendar_event()

        assert event["id"] == str(task.id)
        assert event["title"] == "Important Task"
        assert event["start"] == "2025-10-15"
        assert event["end"] == "2025-10-20"
        assert event["backgroundColor"] == "#F59E0B"
        assert event["extendedProps"]["workType"] == "task"
        assert event["extendedProps"]["status"] == "in_progress"
        assert event["extendedProps"]["priority"] == "high"
        assert event["extendedProps"]["progress"] == 75
        assert "John Doe" in event["extendedProps"]["assignees"]

    def test_calendar_color_property(self):
        """Test calendar color defaults."""
        item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        assert item.calendar_color == "#3B82F6"  # Default blue

    def test_status_border_color(self):
        """Test status-based border colors."""
        task = WorkItem(work_type=WorkItem.WORK_TYPE_TASK, title="Task")

        task.status = WorkItem.STATUS_COMPLETED
        assert task._get_status_border_color() == "#10B981"  # Green

        task.status = WorkItem.STATUS_AT_RISK
        assert task._get_status_border_color() == "#F59E0B"  # Amber

        task.status = WorkItem.STATUS_BLOCKED
        assert task._get_status_border_color() == "#EF4444"  # Red


@pytest.mark.django_db
class TestWorkItemTypeSpecificData:
    """Test type-specific JSON fields."""

    def test_project_data(self):
        """Test project-specific data storage."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            project_data={
                "workflow_stage": "implementation",
                "budget": 500000,
                "funding_source": "BARMM Budget",
            },
        )

        assert project.workflow_stage == "implementation"
        assert project.project_data["budget"] == 500000

    def test_activity_data(self):
        """Test activity-specific data storage."""
        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Workshop",
            activity_data={
                "event_type": "workshop",
                "location": "Cotabato City",
                "venue": "OOBC Office",
                "max_participants": 50,
            },
        )

        assert activity.event_type == "workshop"
        assert activity.activity_data["max_participants"] == 50

    def test_task_data(self):
        """Test task-specific data storage."""
        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Data Collection",
            task_data={
                "domain": "mana",
                "deliverable_type": "survey_data",
                "estimated_hours": 40,
            },
        )

        assert task.domain == "mana"
        assert task.task_data["estimated_hours"] == 40


@pytest.mark.django_db
class TestWorkItemAssignments:
    """Test user and team assignments."""

    def test_assign_users(self):
        """Test assigning users to work items."""
        user1 = User.objects.create_user(username="user1", first_name="John")
        user2 = User.objects.create_user(username="user2", first_name="Jane")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
        )

        task.assignees.add(user1, user2)

        assert task.assignees.count() == 2
        assert user1 in task.assignees.all()
        assert user2 in task.assignees.all()

    def test_assign_teams(self):
        """Test assigning teams to work items."""
        team1 = StaffTeam.objects.create(name="Team Alpha")
        team2 = StaffTeam.objects.create(name="Team Beta")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        project.teams.add(team1, team2)

        assert project.teams.count() == 2
        assert team1 in project.teams.all()


@pytest.mark.django_db
class TestWorkItemLegacyCompatibility:
    """Test backward compatibility with old models."""

    def test_domain_property(self):
        """Test domain property (StaffTask compatibility)."""
        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
        )

        task.domain = "mana"
        task.save()

        assert task.domain == "mana"
        assert task.task_data["domain"] == "mana"

    def test_workflow_stage_property(self):
        """Test workflow_stage property (ProjectWorkflow compatibility)."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        project.workflow_stage = "implementation"
        project.save()

        assert project.workflow_stage == "implementation"
        assert project.project_data["workflow_stage"] == "implementation"

    def test_event_type_property(self):
        """Test event_type property (Event compatibility)."""
        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Workshop",
        )

        activity.event_type = "workshop"
        activity.save()

        assert activity.event_type == "workshop"
        assert activity.activity_data["event_type"] == "workshop"
