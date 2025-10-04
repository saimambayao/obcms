"""
Unit tests for Project-Activity-Task Integration (Phase 2).

Tests model methods and properties for ProjectWorkflow, Event, and StaffTask.
"""

from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from project_central.models import ProjectWorkflow
from coordination.models import Event
from common.models import StaffTask, Region, Province, Municipality, Barangay
from communities.models import OBCCommunity
from mana.models import Need

User = get_user_model()


class ProjectActivityIntegrationTest(TestCase):
    """Test project-activity-task integration model logic."""

    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            user_type="oobc_staff",
        )

        # Create geographic hierarchy
        self.region = Region.objects.create(
            code="IX", name="Zamboanga Peninsula", is_active=True
        )
        self.province = Province.objects.create(
            region=self.region, code="ZAN", name="Zamboanga del Norte", is_active=True
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="DIPOLOG",
            name="Dipolog City",
            municipality_type="city",
            is_active=True,
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY001",
            name="Central",
            is_active=True,
        )

        # Create OBC community
        self.community = OBCCommunity.objects.create(
            name="Test Community",
            barangay=self.barangay,
            community_type="indigenous",
            population_total=500,
            created_by=self.user,
        )

        # Create need
        self.need = Need.objects.create(
            title="Education Infrastructure Need",
            description="Need for school building",
            assessment_area="education",
            priority_level="high",
            is_validated=True,
            community=self.community,
            created_by=self.user,
        )

        # Create project workflow
        self.workflow = ProjectWorkflow.objects.create(
            primary_need=self.need,
            current_stage="need_identification",
            priority_level="high",
            project_lead=self.user,
            created_by=self.user,
        )

    def test_create_project_activity(self):
        """Verify event can be linked to project."""
        event = Event.objects.create(
            title="Project Kickoff Meeting",
            event_type="meeting",
            description="Kickoff for education project",
            objectives="Launch project",
            status="planned",
            start_date=date.today() + timedelta(days=7),
            venue="Municipal Hall",
            address="Dipolog City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            project_activity_type="project_kickoff",
        )

        self.assertEqual(event.related_project, self.workflow)
        self.assertTrue(event.is_project_activity)
        self.assertEqual(event.project_activity_type, "project_kickoff")

    def test_all_project_tasks_aggregation(self):
        """Verify tasks aggregate from multiple sources."""
        # Create workflow task
        workflow_task = StaffTask.objects.create(
            title="Workflow Task 1",
            linked_workflow=self.workflow,
            task_context="project",
            created_by=self.user,
        )

        # Create activity
        activity = Event.objects.create(
            title="Project Review",
            event_type="review",
            description="Review meeting",
            objectives="Review progress",
            status="planned",
            start_date=date.today() + timedelta(days=14),
            venue="Office",
            address="City Hall",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
        )

        # Create activity task
        activity_task = StaffTask.objects.create(
            title="Activity Task 1",
            linked_event=activity,
            task_context="project_activity",
            created_by=self.user,
        )

        # Test aggregation
        all_tasks = self.workflow.all_project_tasks
        self.assertEqual(all_tasks.count(), 2)
        self.assertIn(workflow_task, all_tasks)
        self.assertIn(activity_task, all_tasks)

    def test_get_upcoming_activities(self):
        """Test filtering upcoming activities."""
        # Create past activity
        past_activity = Event.objects.create(
            title="Past Activity",
            event_type="meeting",
            description="Past meeting",
            objectives="Review",
            status="completed",
            start_date=date.today() - timedelta(days=7),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
        )

        # Create upcoming activity (within 30 days)
        upcoming_activity = Event.objects.create(
            title="Upcoming Activity",
            event_type="meeting",
            description="Future meeting",
            objectives="Plan",
            status="planned",
            start_date=date.today() + timedelta(days=14),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
        )

        # Create far future activity (beyond 30 days)
        far_future = Event.objects.create(
            title="Far Future Activity",
            event_type="meeting",
            description="Far meeting",
            objectives="Review",
            status="planned",
            start_date=date.today() + timedelta(days=45),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
        )

        # Test default (30 days)
        upcoming = self.workflow.get_upcoming_activities()
        self.assertEqual(upcoming.count(), 1)
        self.assertIn(upcoming_activity, upcoming)
        self.assertNotIn(past_activity, upcoming)
        self.assertNotIn(far_future, upcoming)

        # Test custom range (60 days)
        upcoming_60 = self.workflow.get_upcoming_activities(days=60)
        self.assertEqual(upcoming_60.count(), 2)
        self.assertIn(upcoming_activity, upcoming_60)
        self.assertIn(far_future, upcoming_60)

    def test_task_context_validation_warnings(self):
        """Test task_context validation logs warnings without blocking."""
        import logging

        # Capture warnings
        with self.assertLogs("common.models", level="WARNING") as cm:
            # Create task with 'project' context but no linked_workflow
            task = StaffTask(
                title="Test Task",
                task_context="project",
                created_by=self.user,
            )
            task.clean()

        # Verify warning was logged
        self.assertTrue(
            any("context 'project' but no linked_workflow" in msg for msg in cm.output)
        )

    def test_auto_task_generation_disabled_by_default(self):
        """Test that auto-task generation does NOT run by default."""
        # Create event without _auto_generate_tasks flag
        event = Event.objects.create(
            title="Test Event",
            event_type="meeting",
            description="Test description",
            objectives="Test objectives",
            status="planned",
            start_date=date.today() + timedelta(days=7),
            venue="Test Venue",
            address="Test Address",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
        )

        # Verify no tasks were auto-generated
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 0)

    def test_auto_task_generation_when_enabled(self):
        """Test auto-task generation when explicitly enabled."""
        # Create event with _auto_generate_tasks flag
        event = Event(
            title="Test Event with Tasks",
            event_type="meeting",
            description="Test description",
            objectives="Test objectives",
            status="planned",
            start_date=date.today() + timedelta(days=7),
            venue="Test Venue",
            address="Test Address",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
        )
        event._auto_generate_tasks = True
        event.save()

        # Verify tasks were auto-generated
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 2)

        # Verify task details
        task_titles = [task.title for task in tasks]
        self.assertIn(f"Prepare agenda for {event.title}", task_titles)
        self.assertIn(f"Send invitations for {event.title}", task_titles)

        # Verify task contexts
        for task in tasks:
            self.assertEqual(task.task_context, "project_activity")
            self.assertEqual(task.linked_workflow, self.workflow)


class ProjectWorkflowPropertyTest(TestCase):
    """Test ProjectWorkflow properties in isolation."""

    def setUp(self):
        """Set up minimal test data."""
        self.user = User.objects.create_user(
            username="proptest", email="prop@test.com", user_type="oobc_staff"
        )

        # Create geographic hierarchy
        region = Region.objects.create(code="XII", name="SOCCSKSARGEN", is_active=True)
        province = Province.objects.create(
            region=region, code="CTB", name="Cotabato", is_active=True
        )
        municipality = Municipality.objects.create(
            province=province, code="KIDAPAWAN", name="Kidapawan", is_active=True
        )
        barangay = Barangay.objects.create(
            municipality=municipality, code="BRGY002", name="Poblacion", is_active=True
        )

        community = OBCCommunity.objects.create(
            name="Test Community 2",
            barangay=barangay,
            community_type="settler",
            population_total=300,
            created_by=self.user,
        )

        need = Need.objects.create(
            title="Health Infrastructure",
            description="Need for clinic",
            assessment_area="health",
            priority_level="medium",
            is_validated=True,
            community=community,
            created_by=self.user,
        )

        self.workflow = ProjectWorkflow.objects.create(
            primary_need=need,
            current_stage="need_identification",
            priority_level="medium",
            created_by=self.user,
        )

    def test_all_project_tasks_empty(self):
        """Test all_project_tasks returns empty QuerySet when no tasks exist."""
        tasks = self.workflow.all_project_tasks
        self.assertEqual(tasks.count(), 0)

    def test_get_upcoming_activities_empty(self):
        """Test get_upcoming_activities returns empty when no activities."""
        activities = self.workflow.get_upcoming_activities()
        self.assertEqual(activities.count(), 0)


class EnhancedTaskGenerationTest(TestCase):
    """Test Phase 6: Enhanced task generation with activity type-specific templates."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="tasktest",
            email="tasktest@example.com",
            password="testpass123",
            user_type="oobc_staff",
        )

        # Create geographic hierarchy
        region = Region.objects.create(
            code="IX", name="Zamboanga Peninsula", is_active=True
        )
        province = Province.objects.create(
            region=region, code="ZAN", name="Zamboanga del Norte", is_active=True
        )
        municipality = Municipality.objects.create(
            province=province,
            code="DIPOLOG",
            name="Dipolog City",
            municipality_type="city",
            is_active=True,
        )
        barangay = Barangay.objects.create(
            municipality=municipality,
            code="BRGY001",
            name="Central",
            is_active=True,
        )

        community = OBCCommunity.objects.create(
            name="Test Community",
            barangay=barangay,
            community_type="indigenous",
            population_total=500,
            created_by=self.user,
        )

        need = Need.objects.create(
            title="Education Infrastructure Need",
            description="Need for school building",
            assessment_area="education",
            priority_level="high",
            is_validated=True,
            community=community,
            created_by=self.user,
        )

        self.workflow = ProjectWorkflow.objects.create(
            primary_need=need,
            current_stage="need_identification",
            priority_level="high",
            project_lead=self.user,
            created_by=self.user,
        )

    def test_project_kickoff_task_generation(self):
        """Test task generation for project_kickoff activity type."""
        event = Event(
            title="Project Kickoff Meeting",
            event_type="meeting",
            description="Kickoff meeting",
            objectives="Launch project",
            status="planned",
            start_date=date.today() + timedelta(days=10),
            venue="Municipal Hall",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            project_activity_type="project_kickoff",
        )
        event._auto_generate_tasks = True
        event.save()

        # Verify correct number of tasks created (4 prep + 2 followup = 6)
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 6)

        # Verify specific prep tasks
        prep_task_titles = [
            f"Prepare project charter for {event.title}",
            f"Prepare presentation materials for {event.title}",
            f"Send calendar invitations for {event.title}",
            f"Book venue and arrange logistics for {event.title}",
        ]
        for title in prep_task_titles:
            self.assertTrue(tasks.filter(title=title).exists())

        # Verify specific followup tasks
        followup_task_titles = [
            f"Document kickoff meeting minutes for {event.title}",
            f"Distribute project charter to stakeholders",
        ]
        for title in followup_task_titles:
            self.assertTrue(tasks.filter(title=title).exists())

        # Verify all tasks have correct context
        for task in tasks:
            self.assertEqual(task.task_context, "project_activity")
            self.assertEqual(task.linked_workflow, self.workflow)
            self.assertEqual(task.priority, "medium")

    def test_milestone_review_task_generation(self):
        """Test task generation for milestone_review activity type."""
        event = Event(
            title="Q1 Milestone Review",
            event_type="review",
            description="Review meeting",
            objectives="Review milestones",
            status="planned",
            start_date=date.today() + timedelta(days=10),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            project_activity_type="milestone_review",
        )
        event._auto_generate_tasks = True
        event.save()

        # Verify correct number of tasks (3 prep + 2 followup = 5)
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 5)

        # Verify milestone-specific tasks exist
        self.assertTrue(
            tasks.filter(
                title=f"Prepare milestone progress report for {event.title}"
            ).exists()
        )
        self.assertTrue(
            tasks.filter(title=f"Update project timeline based on review").exists()
        )

    def test_stakeholder_consultation_task_generation(self):
        """Test task generation for stakeholder_consultation activity type."""
        event = Event(
            title="Community Stakeholder Consultation",
            event_type="consultation",
            description="Stakeholder meeting",
            objectives="Gather feedback",
            status="planned",
            start_date=date.today() + timedelta(days=10),
            venue="Community Center",
            address="Barangay",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            project_activity_type="stakeholder_consultation",
        )
        event._auto_generate_tasks = True
        event.save()

        # Verify correct number of tasks (3 prep + 3 followup = 6)
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 6)

        # Verify consultation-specific tasks
        self.assertTrue(
            tasks.filter(
                title=f"Identify and invite stakeholders for {event.title}"
            ).exists()
        )
        self.assertTrue(tasks.filter(title=f"Analyze consultation results").exists())
        self.assertTrue(
            tasks.filter(
                title=f"Share consultation summary with stakeholders"
            ).exists()
        )

    def test_technical_review_task_generation(self):
        """Test task generation for technical_review activity type."""
        event = Event(
            title="Technical Design Review",
            event_type="review",
            description="Technical review",
            objectives="Review technical specs",
            status="planned",
            start_date=date.today() + timedelta(days=10),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            project_activity_type="technical_review",
        )
        event._auto_generate_tasks = True
        event.save()

        # Verify correct number of tasks (3 prep + 2 followup = 5)
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 5)

        # Verify technical review-specific tasks
        self.assertTrue(
            tasks.filter(
                title=f"Prepare technical documentation for {event.title}"
            ).exists()
        )
        self.assertTrue(
            tasks.filter(title=f"Invite technical experts for {event.title}").exists()
        )

    def test_progress_review_task_generation(self):
        """Test task generation for progress_review activity type."""
        event = Event(
            title="Monthly Progress Review",
            event_type="review",
            description="Progress meeting",
            objectives="Review progress",
            status="planned",
            start_date=date.today() + timedelta(days=10),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            project_activity_type="progress_review",
        )
        event._auto_generate_tasks = True
        event.save()

        # Verify correct number of tasks (2 prep + 2 followup = 4)
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 4)

        # Verify progress review-specific tasks
        self.assertTrue(
            tasks.filter(
                title=f"Prepare progress update report for {event.title}"
            ).exists()
        )
        self.assertTrue(
            tasks.filter(title=f"Update action items based on review").exists()
        )

    def test_closeout_task_generation(self):
        """Test task generation for closeout activity type."""
        event = Event(
            title="Project Closeout Meeting",
            event_type="meeting",
            description="Final closeout",
            objectives="Close project",
            status="planned",
            start_date=date.today() + timedelta(days=10),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            project_activity_type="closeout",
        )
        event._auto_generate_tasks = True
        event.save()

        # Verify correct number of tasks (3 prep + 3 followup = 6)
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 6)

        # Verify closeout-specific tasks
        self.assertTrue(
            tasks.filter(
                title=f"Prepare project closeout report for {event.title}"
            ).exists()
        )
        self.assertTrue(
            tasks.filter(title=f"Archive project files and documentation").exists()
        )
        self.assertTrue(
            tasks.filter(title=f"Send closeout summary to stakeholders").exists()
        )

    def test_generic_activity_task_generation(self):
        """Test task generation for activity without specific type."""
        event = Event(
            title="General Project Meeting",
            event_type="meeting",
            description="General meeting",
            objectives="Discussion",
            status="planned",
            start_date=date.today() + timedelta(days=10),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            # No project_activity_type specified
        )
        event._auto_generate_tasks = True
        event.save()

        # Verify default tasks created (2 prep + 1 followup = 3)
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 3)

        # Verify generic task titles
        self.assertTrue(tasks.filter(title=f"Prepare agenda for {event.title}").exists())
        self.assertTrue(
            tasks.filter(title=f"Send invitations for {event.title}").exists()
        )
        self.assertTrue(
            tasks.filter(title=f"Document minutes for {event.title}").exists()
        )

    def test_task_due_dates(self):
        """Test that task due dates are calculated correctly."""
        start_date = date.today() + timedelta(days=10)
        event = Event(
            title="Test Event",
            event_type="meeting",
            description="Test",
            objectives="Test",
            status="planned",
            start_date=start_date,
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
            related_project=self.workflow,
            is_project_activity=True,
            project_activity_type="project_kickoff",
        )
        event._auto_generate_tasks = True
        event.save()

        tasks = StaffTask.objects.filter(linked_event=event)

        # Check prep tasks (due before event)
        prep_tasks = tasks.filter(due_date__lt=start_date)
        self.assertGreater(prep_tasks.count(), 0)
        for task in prep_tasks:
            self.assertLess(task.due_date, start_date)

        # Check followup tasks (due after event)
        followup_tasks = tasks.filter(due_date__gt=start_date)
        self.assertGreater(followup_tasks.count(), 0)
        for task in followup_tasks:
            self.assertGreater(task.due_date, start_date)


class WorkflowSignalTest(TestCase):
    """Test Phase 6: Signal handlers for event and workflow automation."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="signaltest",
            email="signal@example.com",
            password="testpass123",
            user_type="oobc_staff",
        )

        # Create geographic hierarchy
        region = Region.objects.create(
            code="IX", name="Zamboanga Peninsula", is_active=True
        )
        province = Province.objects.create(
            region=region, code="ZAN", name="Zamboanga del Norte", is_active=True
        )
        municipality = Municipality.objects.create(
            province=province,
            code="DIPOLOG",
            name="Dipolog City",
            municipality_type="city",
            is_active=True,
        )
        barangay = Barangay.objects.create(
            municipality=municipality,
            code="BRGY001",
            name="Central",
            is_active=True,
        )

        community = OBCCommunity.objects.create(
            name="Test Community",
            barangay=barangay,
            community_type="indigenous",
            population_total=500,
            created_by=self.user,
        )

        need = Need.objects.create(
            title="Education Infrastructure Need",
            description="Need for school building",
            assessment_area="education",
            priority_level="high",
            is_validated=True,
            community=community,
            created_by=self.user,
        )

        self.workflow = ProjectWorkflow.objects.create(
            primary_need=need,
            current_stage="need_identification",
            priority_level="high",
            project_lead=self.user,
            created_by=self.user,
        )

    def test_event_creation_signal_logs(self):
        """Test that event creation triggers signal logging."""
        import logging

        with self.assertLogs("coordination.signals", level="INFO") as cm:
            event = Event.objects.create(
                title="Signal Test Event",
                event_type="meeting",
                description="Test",
                objectives="Test",
                status="planned",
                start_date=date.today() + timedelta(days=7),
                venue="Office",
                address="City",
                organizer=self.user,
                created_by=self.user,
                related_project=self.workflow,
                is_project_activity=True,
            )

        # Verify signal logged event creation
        self.assertTrue(
            any(f"Event created: {event.title}" in msg for msg in cm.output)
        )
        self.assertTrue(
            any("Project activity created" in msg for msg in cm.output)
        )

    def test_event_status_change_signal(self):
        """Test that status changes trigger signal logging."""
        import logging

        event = Event.objects.create(
            title="Status Test Event",
            event_type="meeting",
            description="Test",
            objectives="Test",
            status="planned",
            start_date=date.today() + timedelta(days=7),
            venue="Office",
            address="City",
            organizer=self.user,
            created_by=self.user,
        )

        with self.assertLogs("coordination.signals", level="INFO") as cm:
            event.status = "confirmed"
            event.save()

        # Verify signal logged status change
        self.assertTrue(
            any("status changed: planned → confirmed" in msg for msg in cm.output)
        )

    def test_workflow_stage_change_creates_milestone_review(self):
        """Test that entering review stage auto-creates milestone review activity."""
        # Change workflow to review stage
        self.workflow.current_stage = "review"
        self.workflow.save()

        # Verify milestone review event was auto-created
        milestone_events = Event.objects.filter(
            related_project=self.workflow,
            project_activity_type="milestone_review",
        )
        self.assertEqual(milestone_events.count(), 1)

        # Verify event details
        event = milestone_events.first()
        self.assertIn("Milestone Review", event.title)
        self.assertEqual(event.status, "draft")
        self.assertEqual(event.created_by, self.user)  # project_lead

        # Verify tasks were auto-generated
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertGreater(tasks.count(), 0)  # Should have milestone review tasks
