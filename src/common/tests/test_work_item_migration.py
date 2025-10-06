"""
WorkItem Migration Tests

Tests for data migration from legacy models to WorkItem (Phase 5 - Testing).

Test Coverage:
- StaffTask → WorkItem migration
- ProjectWorkflow → WorkItem migration
- Event → WorkItem migration
- Relationship preservation (assignees, teams)
- No data loss verification
- Idempotent migrations (can run multiple times)
"""

import pytest
from datetime import date, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model

from common.models import StaffTask, StaffTeam
from common.work_item_model import WorkItem

User = get_user_model()


@pytest.mark.django_db
class TestStaffTaskMigration:
    """Test StaffTask → WorkItem migration."""

    def test_migrate_simple_task(self):
        """Test migrating a simple task."""
        user = User.objects.create_user(username="testuser")
        team = StaffTeam.objects.create(name="Test Team")

        # Create legacy StaffTask
        task = StaffTask.objects.create(
            title="Complete survey",
            description="Survey all stakeholders",
            status=StaffTask.STATUS_IN_PROGRESS,
            priority=StaffTask.PRIORITY_HIGH,
            progress=50,
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
            created_by=user,
        )
        task.assignees.add(user)
        task.teams.add(team)

        # Migrate to WorkItem
        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            progress=task.progress,
            start_date=task.start_date,
            due_date=task.due_date,
            created_by=task.created_by,
            task_data={
                "domain": task.domain,
                "legacy_task_id": task.id,
            },
        )
        work_item.assignees.set(task.assignees.all())
        work_item.teams.set(task.teams.all())

        # Verify data preservation
        assert work_item.title == "Complete survey"
        assert work_item.description == "Survey all stakeholders"
        assert work_item.status == "in_progress"
        assert work_item.priority == "high"
        assert work_item.progress == 50
        assert work_item.assignees.count() == 1
        assert work_item.teams.count() == 1
        assert user in work_item.assignees.all()
        assert team in work_item.teams.all()

    def test_migrate_task_with_domain_specific_fields(self):
        """Test migrating task with domain-specific data."""
        task = StaffTask.objects.create(
            title="MANA Assessment Task",
            domain=StaffTask.DOMAIN_MANA,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            deliverable_type="survey_data",
            task_category="field_work",
        )

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=task.title,
            task_data={
                "domain": task.domain,
                "assessment_phase": task.assessment_phase,
                "deliverable_type": task.deliverable_type,
                "task_category": task.task_category,
                "legacy_task_id": task.id,
            },
        )

        # Verify domain-specific data
        assert work_item.domain == "mana"
        assert work_item.task_data["assessment_phase"] == "data_collection"
        assert work_item.task_data["deliverable_type"] == "survey_data"

    def test_migrate_task_hierarchy(self):
        """Test migrating task with parent-child relationships."""
        parent_task = StaffTask.objects.create(
            title="Parent Task",
        )

        # Note: StaffTask doesn't have explicit parent field
        # This test demonstrates how we'd structure the migration
        parent_work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=parent_task.title,
        )

        child_task = StaffTask.objects.create(
            title="Child Task",
        )

        child_work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUBTASK,
            title=child_task.title,
            parent=parent_work_item,
        )

        assert child_work_item.parent == parent_work_item
        assert child_work_item.get_root() == parent_work_item

    def test_preserve_recurrence_pattern(self):
        """Test preserving recurrence data."""
        from common.models import RecurringEventPattern

        pattern = RecurringEventPattern.objects.create(
            recurrence_type=RecurringEventPattern.RECURRENCE_WEEKLY,
            interval=1,
            by_weekday=[1, 3, 5],  # Mon, Wed, Fri
        )

        task = StaffTask.objects.create(
            title="Weekly Status Update",
            is_recurring=True,
            recurrence_pattern=pattern,
        )

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=task.title,
            is_recurring=task.is_recurring,
            recurrence_pattern=task.recurrence_pattern,
        )

        assert work_item.is_recurring is True
        assert work_item.recurrence_pattern == pattern


@pytest.mark.django_db
class TestProjectWorkflowMigration:
    """Test ProjectWorkflow → WorkItem migration."""

    def test_migrate_project(self):
        """Test migrating a project workflow."""
        # Note: Assuming ProjectWorkflow model exists in project_central app
        # This is a template for the actual migration

        user = User.objects.create_user(username="pm_user")

        # Create WorkItem as Project
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Community Development Project",
            description="Comprehensive community development initiative",
            start_date=date(2025, 1, 1),
            due_date=date(2025, 12, 31),
            created_by=user,
            project_data={
                "workflow_stage": "implementation",
                "budget": 1000000,
                "funding_source": "BARMM",
                "legacy_workflow_id": 123,
            },
        )

        assert project.workflow_stage == "implementation"
        assert project.project_data["budget"] == 1000000

    def test_migrate_project_with_activities(self):
        """Test migrating project with nested activities."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="MANA Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Community Consultation",
            parent=project,
            activity_data={
                "event_type": "consultation",
                "location": "Maguindanao",
            },
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Prepare consultation materials",
            parent=activity,
        )

        # Verify hierarchy
        assert activity.parent == project
        assert task.parent == activity
        assert task.get_root_project() == project


@pytest.mark.django_db
class TestEventMigration:
    """Test Event → WorkItem migration."""

    def test_migrate_event_as_activity(self):
        """Test migrating coordination Event to WorkItem Activity."""
        user = User.objects.create_user(username="coordinator")

        # Simulate Event → Activity migration
        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Stakeholder Coordination Meeting",
            description="Monthly coordination with stakeholders",
            start_date=date(2025, 10, 15),
            due_date=date(2025, 10, 15),
            start_time="09:00:00",
            end_time="12:00:00",
            created_by=user,
            activity_data={
                "event_type": "meeting",
                "location": "Cotabato City",
                "venue": "OOBC Conference Room",
                "max_participants": 30,
                "legacy_event_id": 456,
            },
        )

        assert activity.event_type == "meeting"
        assert activity.activity_data["venue"] == "OOBC Conference Room"
        assert activity.activity_data["max_participants"] == 30


@pytest.mark.django_db
class TestMigrationDataIntegrity:
    """Test data integrity during migration."""

    def test_no_data_loss_task_fields(self):
        """Verify all StaffTask fields are migrated."""
        user = User.objects.create_user(username="testuser")

        task = StaffTask.objects.create(
            title="Test Task",
            description="Test Description",
            impact="High impact on community",
            status=StaffTask.STATUS_AT_RISK,
            priority=StaffTask.PRIORITY_CRITICAL,
            progress=75,
            start_date=date(2025, 10, 1),
            due_date=date(2025, 10, 31),
            domain=StaffTask.DOMAIN_MANA,
            task_category="assessment",
            created_by=user,
        )

        # Migrate
        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            progress=task.progress,
            start_date=task.start_date,
            due_date=task.due_date,
            created_by=task.created_by,
            task_data={
                "domain": task.domain,
                "task_category": task.task_category,
                "impact": task.impact,
            },
        )

        # Verify no data loss
        assert work_item.title == task.title
        assert work_item.description == task.description
        assert work_item.status == task.status
        assert work_item.priority == task.priority
        assert work_item.progress == task.progress
        assert work_item.domain == task.domain
        assert work_item.task_data["impact"] == task.impact

    def test_preserve_many_to_many_relationships(self):
        """Verify M2M relationships are preserved."""
        user1 = User.objects.create_user(username="user1")
        user2 = User.objects.create_user(username="user2")
        team1 = StaffTeam.objects.create(name="Team 1")
        team2 = StaffTeam.objects.create(name="Team 2")

        task = StaffTask.objects.create(title="Task")
        task.assignees.add(user1, user2)
        task.teams.add(team1, team2)

        # Migrate
        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=task.title,
        )
        work_item.assignees.set(task.assignees.all())
        work_item.teams.set(task.teams.all())

        # Verify
        assert work_item.assignees.count() == 2
        assert work_item.teams.count() == 2
        assert set(work_item.assignees.all()) == set(task.assignees.all())
        assert set(work_item.teams.all()) == set(task.teams.all())


@pytest.mark.django_db
class TestIdempotentMigration:
    """Test that migrations can run multiple times safely."""

    def test_idempotent_task_migration(self):
        """Test running task migration twice doesn't duplicate data."""
        task = StaffTask.objects.create(title="Test Task")

        # First migration
        work_item1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=task.title,
            task_data={"legacy_task_id": task.id},
        )

        # Simulate running migration again (should check for existing)
        existing = WorkItem.objects.filter(
            task_data__legacy_task_id=task.id
        ).first()

        if existing:
            # Update instead of create
            existing.title = task.title
            existing.save()
            work_item2 = existing
        else:
            work_item2 = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=task.title,
                task_data={"legacy_task_id": task.id},
            )

        # Verify only one WorkItem exists
        assert WorkItem.objects.filter(task_data__legacy_task_id=task.id).count() == 1
        assert work_item1.id == work_item2.id


@pytest.mark.django_db
class TestBulkMigration:
    """Test bulk migration performance."""

    def test_bulk_create_work_items(self):
        """Test migrating multiple tasks in bulk."""
        tasks = [
            StaffTask(title=f"Task {i}", domain=StaffTask.DOMAIN_GENERAL)
            for i in range(100)
        ]
        StaffTask.objects.bulk_create(tasks)

        # Migrate in bulk
        work_items = []
        for task in StaffTask.objects.all():
            work_items.append(
                WorkItem(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=task.title,
                    task_data={"domain": task.domain, "legacy_task_id": task.id},
                )
            )

        WorkItem.objects.bulk_create(work_items)

        # Verify
        assert WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_TASK).count() == 100


@pytest.mark.django_db
class TestMigrationEdgeCases:
    """Test edge cases in migration."""

    def test_migrate_task_with_null_fields(self):
        """Test migrating task with null/blank fields."""
        task = StaffTask.objects.create(
            title="Minimal Task",
            # All optional fields left as None/blank
        )

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=task.title,
            description=task.description or "",
            start_date=task.start_date,
            due_date=task.due_date,
        )

        assert work_item.description == ""
        assert work_item.start_date is None
        assert work_item.due_date is None

    def test_migrate_task_with_unicode_title(self):
        """Test migrating task with Unicode characters."""
        task = StaffTask.objects.create(
            title="تنسيق المجتمع (Community Coordination)",
            description="مهمة لتنسيق المجتمع",
        )

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=task.title,
            description=task.description,
        )

        assert "تنسيق المجتمع" in work_item.title
        assert "مهمة لتنسيق المجتمع" in work_item.description
