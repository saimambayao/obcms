"""Tests for signal handlers that auto-create tasks."""

import pytest

pytest.skip(
    "Legacy task signal tests require StaffTask/TaskTemplate models removed in WorkItem refactor.",
    allow_module_level=True,
)

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from common.models import StaffTask, TaskTemplate, TaskTemplateItem, User
from common.tests.factories import (
    create_assessment,
    create_baseline_study,
    create_community,
    create_event,
    create_monitoring_entry,
    create_partnership,
    create_policy_milestone,
    create_policy_recommendation,
    create_service_application,
    create_service_offering,
    create_workshop_activity,
)


class AssessmentSignalTests(TestCase):
    """Test automated task creation when Assessment is created."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        # Create assessment template
        self.template = TaskTemplate.objects.create(
            name="mana_assessment_basic",
            domain=StaffTask.DOMAIN_MANA,
            description="Basic MANA assessment workflow",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Plan assessment: {assessment_name}",
            description="Complete assessment planning",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            task_category="planning",
            estimated_hours=4,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_PLANNING,
        )

    def test_assessment_creation_triggers_task_generation(self):
        """Test that creating an assessment auto-creates tasks."""
        initial_count = StaffTask.objects.count()

        assessment = create_assessment(
            created_by=self.admin,
            title="Region IX Education Assessment",
            primary_methodology="survey",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 30),
        )

        # Should create tasks
        self.assertGreater(StaffTask.objects.count(), initial_count)

        # Verify tasks are linked to assessment
        tasks = StaffTask.objects.filter(related_assessment=assessment)
        self.assertGreater(tasks.count(), 0)

    def test_assessment_update_does_not_create_tasks(self):
        """Test that updating an assessment doesn't create duplicate tasks."""
        assessment = create_assessment(
            created_by=self.admin,
            title="Test Assessment",
            primary_methodology="survey",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 30),
        )

        initial_count = StaffTask.objects.count()

        # Update the assessment
        assessment.title = "Updated Test Assessment"
        assessment.save()

        # Should not create new tasks
        self.assertEqual(StaffTask.objects.count(), initial_count)

    def test_assessment_methodology_selects_correct_template(self):
        """Test that different methodologies use different templates."""
        # Create templates for different methodologies
        survey_template = TaskTemplate.objects.create(
            name="mana_assessment_survey",
            domain=StaffTask.DOMAIN_MANA,
            is_active=True,
        )
        TaskTemplateItem.objects.create(
            template=survey_template,
            title="Design survey",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

        workshop_template = TaskTemplate.objects.create(
            name="mana_assessment_workshop",
            domain=StaffTask.DOMAIN_MANA,
            is_active=True,
        )
        TaskTemplateItem.objects.create(
            template=workshop_template,
            title="Organize workshop",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

        # Create survey assessment
        survey_assessment = create_assessment(
            created_by=self.admin,
            title="Survey Assessment",
            primary_methodology="survey",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 30),
        )

        # Create workshop assessment
        workshop_assessment = create_assessment(
            created_by=self.admin,
            title="Workshop Assessment",
            primary_methodology="workshop",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 30),
        )

        # Check that tasks were created with correct templates
        survey_tasks = StaffTask.objects.filter(related_assessment=survey_assessment)
        workshop_tasks = StaffTask.objects.filter(
            related_assessment=workshop_assessment
        )

        # Both should have created tasks
        self.assertGreater(survey_tasks.count(), 0)
        self.assertGreater(workshop_tasks.count(), 0)


class BaselineStudySignalTests(TestCase):
    """Test automated task creation when BaselineStudy is created."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        # Create baseline template
        self.template = TaskTemplate.objects.create(
            name="mana_baseline_study",
            domain=StaffTask.DOMAIN_MANA,
            description="Baseline study workflow",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Baseline: {baseline_name}",
            description="Complete baseline study",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

        self.community = create_community()
        self.assessment = create_assessment(
            created_by=self.admin,
            planned_start=date(2025, 10, 1),
            planned_end=date(2025, 10, 31),
        )

    def test_baseline_creation_triggers_tasks(self):
        """Test that creating a baseline study auto-creates tasks."""
        initial_count = StaffTask.objects.count()

        baseline = create_baseline_study(
            assessment=self.assessment,
            community=self.community,
            principal_investigator=self.admin,
            created_by=self.admin,
            title="Region XII Baseline Study",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 12, 1),
        )

        self.assertGreater(StaffTask.objects.count(), initial_count)

        tasks = StaffTask.objects.filter(related_baseline=baseline)
        self.assertGreater(tasks.count(), 0)


class WorkshopActivitySignalTests(TestCase):
    """Test automated task creation when WorkshopActivity is created."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        # Create workshop template
        self.template = TaskTemplate.objects.create(
            name="mana_workshop_facilitation",
            domain=StaffTask.DOMAIN_MANA,
            description="Workshop facilitation workflow",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Facilitate: {workshop_name}",
            description="Run workshop",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

        self.assessment = create_assessment(
            created_by=self.admin,
            planned_start=date(2025, 10, 1),
            planned_end=date(2025, 10, 31),
        )

    def test_workshop_creation_triggers_tasks(self):
        """Test that creating a workshop auto-creates tasks."""
        initial_count = StaffTask.objects.count()

        workshop = create_workshop_activity(
            assessment=self.assessment,
            created_by=self.admin,
            title="Community Engagement Workshop",
            scheduled_date=date(2025, 11, 15),
        )

        self.assertGreater(StaffTask.objects.count(), initial_count)

        tasks = StaffTask.objects.filter(related_workshop=workshop)
        self.assertGreater(tasks.count(), 0)


class EventSignalTests(TestCase):
    """Test automated task creation when Event is created."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        # Create event templates
        self.meeting_template = TaskTemplate.objects.create(
            name="event_meeting_standard",
            domain=StaffTask.DOMAIN_COORDINATION,
            is_active=True,
        )
        TaskTemplateItem.objects.create(
            template=self.meeting_template,
            title="Prepare for meeting: {event_name}",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_MEDIUM,
        )

        self.workshop_template = TaskTemplate.objects.create(
            name="event_workshop_full",
            domain=StaffTask.DOMAIN_COORDINATION,
            is_active=True,
        )
        TaskTemplateItem.objects.create(
            template=self.workshop_template,
            title="Organize workshop: {event_name}",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

    def test_meeting_event_triggers_tasks(self):
        """Test that creating a meeting event auto-creates tasks."""
        initial_count = StaffTask.objects.count()

        event = create_event(
            created_by=self.admin,
            title="Provincial Coordination Meeting",
            event_type="meeting",
            start_date=date(2025, 11, 20),
        )

        self.assertGreater(StaffTask.objects.count(), initial_count)

        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertGreater(tasks.count(), 0)

    def test_workshop_event_triggers_tasks(self):
        """Test that creating a workshop event auto-creates tasks."""
        initial_count = StaffTask.objects.count()

        event = create_event(
            created_by=self.admin,
            title="Capacity Building Workshop",
            event_type="workshop",
            start_date=date(2025, 11, 25),
        )

        self.assertGreater(StaffTask.objects.count(), initial_count)

    def test_non_task_event_types_skip_creation(self):
        """Test that non-meeting/workshop/conference events don't create tasks."""
        initial_count = StaffTask.objects.count()

        # Create a 'visit' event (not in the trigger list)
        event = create_event(
            created_by=self.admin,
            title="Field Visit",
            event_type="field_visit",
            start_date=date(2025, 11, 30),
        )

        # Should not create tasks
        self.assertEqual(StaffTask.objects.count(), initial_count)

    def test_event_update_does_not_create_tasks(self):
        """Test that updating an event doesn't create duplicate tasks."""
        event = create_event(
            created_by=self.admin,
            title="Test Meeting",
            event_type="meeting",
            start_date=date(2025, 12, 1),
        )

        initial_count = StaffTask.objects.count()

        # Update the event
        event.title = "Updated Test Meeting"
        event.save()

        # Should not create new tasks
        self.assertEqual(StaffTask.objects.count(), initial_count)


class PartnershipSignalTests(TestCase):
    """Test automated task creation when Partnership is created."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        # Create partnership template
        self.template = TaskTemplate.objects.create(
            name="partnership_negotiation",
            domain=StaffTask.DOMAIN_COORDINATION,
            is_active=True,
        )
        TaskTemplateItem.objects.create(
            template=self.template,
            title="Negotiate: {partnership_name}",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

    def test_partnership_creation_triggers_tasks(self):
        """Test that creating a partnership auto-creates tasks."""
        initial_count = StaffTask.objects.count()

        partnership = create_partnership(created_by=self.admin)

        self.assertGreater(StaffTask.objects.count(), initial_count)

        tasks = StaffTask.objects.filter(related_partnership=partnership)
        self.assertGreater(tasks.count(), 0)


class PolicySignalTests(TestCase):
    """Test automated task creation when Policy is created."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        # Create policy template
        self.template = TaskTemplate.objects.create(
            name="policy_development_full_cycle",
            domain=StaffTask.DOMAIN_POLICY,
            is_active=True,
        )
        TaskTemplateItem.objects.create(
            template=self.template,
            title="Develop: {policy_title}",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            policy_phase=StaffTask.POLICY_PHASE_EVIDENCE,
        )

    def test_policy_creation_triggers_tasks(self):
        """Test that creating a policy auto-creates tasks."""
        initial_count = StaffTask.objects.count()

        policy = create_policy_recommendation(
            proposed_by=self.admin,
            title="Education Subsidy Policy",
            status="draft",
        )

        self.assertGreater(StaffTask.objects.count(), initial_count)

        tasks = StaffTask.objects.filter(related_policy=policy)
        self.assertGreater(tasks.count(), 0)
        self.assertEqual(tasks.first().domain, StaffTask.DOMAIN_POLICY)


class PolicyMilestoneSignalTests(TestCase):
    """Test automated task creation when PolicyImplementationMilestone is created."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        self.policy = create_policy_recommendation(
            proposed_by=self.admin,
            title="Test Policy",
            status="approved",
        )

    def test_milestone_creation_creates_single_task(self):
        """Test that creating a milestone creates a single task."""
        initial_count = StaffTask.objects.count()

        milestone = create_policy_milestone(
            policy=self.policy,
            created_by=self.admin,
            title="Phase 1 Implementation",
            target_date=date(2025, 12, 31),
        )

        # Should create exactly one task
        self.assertEqual(StaffTask.objects.count(), initial_count + 1)

        task = StaffTask.objects.filter(related_policy_milestone=milestone).first()
        self.assertIsNotNone(task)
        self.assertEqual(task.title, f"Complete: {milestone.title}")
        self.assertEqual(task.due_date, milestone.target_date)
        self.assertEqual(task.policy_phase, StaffTask.POLICY_PHASE_IMPLEMENTATION)


class MonitoringEntrySignalTests(TestCase):
    """Test automated task creation when PPA MonitoringEntry is created."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        # Create PPA template
        self.template = TaskTemplate.objects.create(
            name="ppa_budget_cycle",
            domain=StaffTask.DOMAIN_MONITORING,
            is_active=True,
        )
        TaskTemplateItem.objects.create(
            template=self.template,
            title="Budget: {ppa_title}",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

    def test_ppa_creation_triggers_tasks(self):
        """Test that creating a PPA monitoring entry auto-creates tasks."""
        initial_count = StaffTask.objects.count()

        ppa = create_monitoring_entry(
            created_by=self.admin,
            title="2025 Education Program",
            category="moa_ppa",
            start_date=date(2025, 1, 1),
            budget_allocated=Decimal("1000000.00"),
        )

        self.assertGreater(StaffTask.objects.count(), initial_count)

        tasks = StaffTask.objects.filter(related_ppa=ppa)
        self.assertGreater(tasks.count(), 0)

    def test_non_ppa_monitoring_entry_skips_tasks(self):
        """Test that non-PPA monitoring entries don't create tasks."""
        initial_count = StaffTask.objects.count()

        entry = create_monitoring_entry(
            created_by=self.admin,
            title="General Monitoring",
            category="obc_request",
            start_date=date(2025, 1, 1),
        )

        # Should not create tasks
        self.assertEqual(StaffTask.objects.count(), initial_count)


class ServiceApplicationSignalTests(TestCase):
    """Test automated task creation when ServiceApplication is submitted."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        self.service = create_service_offering(
            created_by=self.admin,
            title="Scholarship Application",
            service_type="education",
        )
        self.applicant = User.objects.create_user(
            username="applicant",
            password="pass1234",
            user_type="obc_representative",
            is_approved=True,
        )

    def test_submitted_application_creates_review_task(self):
        """Test that submitting an application creates a review task."""
        initial_count = StaffTask.objects.count()

        application = create_service_application(
            service=self.service,
            applicant_user=self.applicant,
            applicant_name="Juan Dela Cruz",
            status="submitted",
        )

        # Should create exactly one review task
        self.assertEqual(StaffTask.objects.count(), initial_count + 1)

        task = StaffTask.objects.filter(related_application=application).first()
        self.assertIsNotNone(task)
        self.assertIn("Review application", task.title)
        self.assertIn(application.applicant_name, task.title)
        self.assertEqual(task.service_phase, StaffTask.SERVICE_PHASE_REVIEW)
        self.assertEqual(task.domain, StaffTask.DOMAIN_SERVICES)

        # Verify due date is 7 days from now
        expected_due = timezone.now().date() + timedelta(days=7)
        self.assertEqual(task.due_date, expected_due)

    def test_draft_application_does_not_create_task(self):
        """Test that draft applications don't trigger task creation."""
        initial_count = StaffTask.objects.count()

        application = create_service_application(
            service=self.service,
            applicant_user=self.applicant,
            applicant_name="Test User",
            status="draft",
        )

        # Should not create tasks
        self.assertEqual(StaffTask.objects.count(), initial_count)


class MonitoringProgressSyncTests(TestCase):
    """Ensure staff task updates keep MonitoringEntry progress synchronized."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="progress",
            password="pass123",
            user_type="oobc_staff",
            is_approved=True,
        )
        self.monitoring_entry = create_monitoring_entry(created_by=self.user)

    def _make_task(self, status=StaffTask.STATUS_NOT_STARTED):
        return StaffTask.objects.create(
            title="Monitoring task",
            related_ppa=self.monitoring_entry,
            status=status,
            due_date=date.today() + timedelta(days=5),
            created_by=self.user,
        )

    def test_progress_updates_on_completion(self):
        task_a = self._make_task()
        task_b = self._make_task()

        self.monitoring_entry.refresh_from_db()
        self.assertEqual(self.monitoring_entry.progress, 0)

        task_a.status = StaffTask.STATUS_COMPLETED
        task_a.save(update_fields=["status"])

        self.monitoring_entry.refresh_from_db()
        self.assertEqual(self.monitoring_entry.progress, 50)

        task_b.status = StaffTask.STATUS_COMPLETED
        task_b.save(update_fields=["status"])

        self.monitoring_entry.refresh_from_db()
        self.assertEqual(self.monitoring_entry.progress, 100)

    def test_progress_resets_when_tasks_removed(self):
        task = self._make_task(status=StaffTask.STATUS_COMPLETED)
        self.monitoring_entry.refresh_from_db()
        self.assertEqual(self.monitoring_entry.progress, 100)

        task.delete()

        self.monitoring_entry.refresh_from_db()
        self.assertEqual(self.monitoring_entry.progress, 0)
