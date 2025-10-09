"""Tests for task model domain logic and properties."""

import pytest

pytest.skip(
    "Legacy StaffTask model tests removed after WorkItem refactor.",
    allow_module_level=True,
)

from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from common.models import StaffTask, TaskTemplate, TaskTemplateItem, User
from common.tests.factories import (
    create_assessment,
    create_event,
    create_partnership,
    create_policy_recommendation,
    create_service_offering,
)


class StaffTaskDomainTests(TestCase):
    """Test the StaffTask domain field and categorization."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

    def test_domain_choices_available(self):
        """Test that all domain choices are available."""
        domains = dict(StaffTask.DOMAIN_CHOICES)

        self.assertIn(StaffTask.DOMAIN_GENERAL, domains)
        self.assertIn(StaffTask.DOMAIN_MANA, domains)
        self.assertIn(StaffTask.DOMAIN_COORDINATION, domains)
        self.assertIn(StaffTask.DOMAIN_POLICY, domains)
        self.assertIn(StaffTask.DOMAIN_MONITORING, domains)
        self.assertIn(StaffTask.DOMAIN_SERVICES, domains)

    def test_task_can_be_created_with_each_domain(self):
        """Test that tasks can be created with each domain."""
        for domain_code, _ in StaffTask.DOMAIN_CHOICES:
            task = StaffTask.objects.create(
                title=f"Task in {domain_code}",
                domain=domain_code,
                created_by=self.admin,
            )
            self.assertEqual(task.domain, domain_code)

    def test_default_domain_is_internal(self):
        """Test that default domain is 'internal'."""
        task = StaffTask.objects.create(
            title="Task without domain",
            created_by=self.admin,
        )
        self.assertEqual(task.domain, StaffTask.DOMAIN_GENERAL)


class StaffTaskPrimaryDomainObjectTests(TestCase):
    """Test the primary_domain_object property."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        # Create related objects
        self.assessment = create_assessment(
            created_by=self.admin,
            title="Test Assessment",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 15),
        )

        self.event = create_event(
            created_by=self.admin,
            title="Test Event",
            event_type="meeting",
            start_date=date(2025, 11, 15),
        )

        self.policy = create_policy_recommendation(
            proposed_by=self.admin,
            title="Test Policy",
            status="draft",
        )

    def test_primary_domain_object_returns_assessment(self):
        """Test that primary_domain_object returns assessment when linked."""
        task = StaffTask.objects.create(
            title="Assessment Task",
            domain=StaffTask.DOMAIN_MANA,
            related_assessment=self.assessment,
            created_by=self.admin,
        )

        self.assertEqual(task.primary_domain_object, self.assessment)

    def test_primary_domain_object_returns_event(self):
        """Test that primary_domain_object returns event when linked."""
        task = StaffTask.objects.create(
            title="Event Task",
            domain=StaffTask.DOMAIN_COORDINATION,
            linked_event=self.event,
            created_by=self.admin,
        )

        self.assertEqual(task.primary_domain_object, self.event)

    def test_primary_domain_object_returns_policy(self):
        """Test that primary_domain_object returns policy when linked."""
        task = StaffTask.objects.create(
            title="Policy Task",
            domain=StaffTask.DOMAIN_POLICY,
            related_policy=self.policy,
            created_by=self.admin,
        )

        self.assertEqual(task.primary_domain_object, self.policy)


class StaffTaskValidationTests(TestCase):
    """Ensure StaffTask validation rules hold."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="validator",
            password="pass123",
            user_type="oobc_staff",
            is_approved=True,
        )
        self.assessment = create_assessment(
            created_by=self.user,
            title="Validation Assessment",
            planned_start=date.today(),
            planned_end=date.today() + timedelta(days=5),
        )
        self.event = create_event(
            created_by=self.user,
            title="Validation Event",
            event_type="meeting",
            start_date=date.today(),
        )

    def test_only_one_domain_relation_allowed(self):
        """Multiple domain relations should raise a validation error."""
        task = StaffTask(
            title="Overlinked task",
            related_assessment=self.assessment,
            linked_event=self.event,
            created_by=self.user,
        )

        with self.assertRaises(ValidationError) as exc:
            task.full_clean()

        self.assertIn(
            "Task can only be linked to one primary domain object", str(exc.exception)
        )

    def test_recurring_task_requires_start_date(self):
        """Recurring tasks must include a start date."""
        task = StaffTask(
            title="Recurring without start",
            is_recurring=True,
            created_by=self.user,
        )

        from common.models import RecurringEventPattern

        task.recurrence_pattern = RecurringEventPattern.objects.create(
            recurrence_type=RecurringEventPattern.RECURRENCE_WEEKLY,
            interval=1,
            by_weekday=[1],
        )

        with self.assertRaises(ValidationError) as exc:
            task.full_clean()

        self.assertIn("Recurring tasks must define a start date", str(exc.exception))


class StaffTaskPhaseFieldsTests(TestCase):
    """Test phase fields for different domains."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

    def test_assessment_phase_choices(self):
        """Test that assessment phase choices are available."""
        phases = dict(StaffTask.ASSESSMENT_PHASE_CHOICES)

        self.assertIn(StaffTask.ASSESSMENT_PHASE_PLANNING, phases)
        self.assertIn(StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION, phases)
        self.assertIn(StaffTask.ASSESSMENT_PHASE_ANALYSIS, phases)
        self.assertIn(StaffTask.ASSESSMENT_PHASE_REPORT_WRITING, phases)
        self.assertIn(StaffTask.ASSESSMENT_PHASE_REVIEW, phases)

    def test_policy_phase_choices(self):
        """Test that policy phase choices are available."""
        phases = dict(StaffTask.POLICY_PHASE_CHOICES)

        self.assertIn(StaffTask.POLICY_PHASE_DRAFTING, phases)
        self.assertIn(StaffTask.POLICY_PHASE_EVIDENCE, phases)
        self.assertIn(StaffTask.POLICY_PHASE_REVIEW, phases)
        self.assertIn(StaffTask.POLICY_PHASE_CONSULTATION, phases)
        self.assertIn(StaffTask.POLICY_PHASE_IMPLEMENTATION, phases)

    def test_service_phase_choices(self):
        """Test that service phase choices are available."""
        phases = dict(StaffTask.SERVICE_PHASE_CHOICES)

        self.assertIn(StaffTask.SERVICE_PHASE_SETUP, phases)
        self.assertIn(StaffTask.SERVICE_PHASE_REVIEW, phases)
        self.assertIn(StaffTask.SERVICE_PHASE_DELIVERY, phases)
        self.assertIn(StaffTask.SERVICE_PHASE_FOLLOWUP, phases)
        self.assertIn(StaffTask.SERVICE_PHASE_REPORTING, phases)

    def test_task_with_assessment_phase(self):
        """Test creating task with assessment phase."""
        task = StaffTask.objects.create(
            title="Assessment Planning Task",
            domain=StaffTask.DOMAIN_MANA,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_PLANNING,
            created_by=self.admin,
        )

        self.assertEqual(task.assessment_phase, StaffTask.ASSESSMENT_PHASE_PLANNING)
        self.assertFalse(task.policy_phase)
        self.assertFalse(task.service_phase)

    def test_task_with_policy_phase(self):
        """Test creating task with policy phase."""
        task = StaffTask.objects.create(
            title="Policy Research Task",
            domain=StaffTask.DOMAIN_POLICY,
            policy_phase=StaffTask.POLICY_PHASE_REVIEW,
            created_by=self.admin,
        )

        self.assertEqual(task.policy_phase, StaffTask.POLICY_PHASE_REVIEW)
        self.assertFalse(task.assessment_phase)
        self.assertFalse(task.service_phase)

    def test_task_with_service_phase(self):
        """Test creating task with service phase."""
        task = StaffTask.objects.create(
            title="Service Review Task",
            domain=StaffTask.DOMAIN_SERVICES,
            service_phase=StaffTask.SERVICE_PHASE_REVIEW,
            created_by=self.admin,
        )

        self.assertEqual(task.service_phase, StaffTask.SERVICE_PHASE_REVIEW)
        self.assertFalse(task.assessment_phase)
        self.assertFalse(task.policy_phase)


class StaffTaskRelatedObjectTests(TestCase):
    """Test related object foreign keys."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

    def test_task_can_link_to_assessment(self):
        """Test that task can be linked to an assessment."""
        assessment = create_assessment(
            created_by=self.admin,
            title="Test Assessment",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 15),
        )

        task = StaffTask.objects.create(
            title="Assessment Task",
            related_assessment=assessment,
            created_by=self.admin,
        )

        self.assertEqual(task.related_assessment, assessment)

    def test_task_can_link_to_event(self):
        """Test that task can be linked to an event."""
        event = create_event(
            created_by=self.admin,
            title="Test Event",
            event_type="meeting",
            start_date=date(2025, 11, 15),
        )

        task = StaffTask.objects.create(
            title="Event Task",
            linked_event=event,
            created_by=self.admin,
        )

        self.assertEqual(task.linked_event, event)

    def test_task_can_link_to_policy(self):
        """Test that task can be linked to a policy."""
        policy = create_policy_recommendation(
            proposed_by=self.admin,
            title="Test Policy",
            status="draft",
        )

        task = StaffTask.objects.create(
            title="Policy Task",
            related_policy=policy,
            created_by=self.admin,
        )

        self.assertEqual(task.related_policy, policy)

    def test_task_can_link_to_partnership(self):
        """Test that task can be linked to a partnership."""
        partnership = create_partnership(created_by=self.admin)

        task = StaffTask.objects.create(
            title="Partnership Task",
            related_partnership=partnership,
            created_by=self.admin,
        )

        self.assertEqual(task.related_partnership, partnership)

    def test_task_can_link_to_service(self):
        """Test that task can be linked to a service."""
        service = create_service_offering(created_by=self.admin)

        task = StaffTask.objects.create(
            title="Service Task",
            related_service=service,
            created_by=self.admin,
        )

        self.assertEqual(task.related_service, service)


class TaskTemplateModelTests(TestCase):
    """Test TaskTemplate model."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

    def test_create_task_template(self):
        """Test creating a task template."""
        template = TaskTemplate.objects.create(
            name="test_template",
            domain=StaffTask.DOMAIN_MANA,
            description="Test template",
            is_active=True,
        )

        self.assertEqual(template.name, "test_template")
        self.assertEqual(template.domain, StaffTask.DOMAIN_MANA)
        self.assertTrue(template.is_active)

    def test_template_string_representation(self):
        """Test template __str__ method."""
        template = TaskTemplate.objects.create(
            name="mana_assessment",
            domain=StaffTask.DOMAIN_MANA,
        )

        self.assertIn("mana_assessment", str(template))

    def test_template_can_have_multiple_items(self):
        """Test that template can have multiple items."""
        template = TaskTemplate.objects.create(
            name="multi_item_template",
            domain=StaffTask.DOMAIN_POLICY,
        )

        item1 = TaskTemplateItem.objects.create(
            template=template,
            title="First Task",
            sequence=1,
            days_from_start=0,
        )

        item2 = TaskTemplateItem.objects.create(
            template=template,
            title="Second Task",
            sequence=2,
            days_from_start=7,
        )

        self.assertEqual(template.items.count(), 2)
        self.assertIn(item1, template.items.all())
        self.assertIn(item2, template.items.all())


class TaskTemplateItemModelTests(TestCase):
    """Test TaskTemplateItem model."""

    def setUp(self):
        """Set up test data."""
        self.template = TaskTemplate.objects.create(
            name="test_template",
            domain=StaffTask.DOMAIN_MANA,
        )

    def test_create_template_item(self):
        """Test creating a template item."""
        item = TaskTemplateItem.objects.create(
            template=self.template,
            title="Test Task",
            description="Task description",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            task_category="planning",
            estimated_hours=4,
        )

        self.assertEqual(item.title, "Test Task")
        self.assertEqual(item.sequence, 1)
        self.assertEqual(item.days_from_start, 0)
        self.assertEqual(item.priority, StaffTask.PRIORITY_HIGH)

    def test_template_item_string_representation(self):
        """Test template item __str__ method."""
        item = TaskTemplateItem.objects.create(
            template=self.template,
            title="Planning Task",
            sequence=1,
            days_from_start=0,
        )

        self.assertIn("Planning Task", str(item))

    def test_template_item_with_assessment_phase(self):
        """Test creating template item with assessment phase."""
        item = TaskTemplateItem.objects.create(
            template=self.template,
            title="Data Collection",
            sequence=2,
            days_from_start=7,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
        )

        self.assertEqual(
            item.assessment_phase, StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION
        )

    def test_template_item_with_policy_phase(self):
        """Test creating template item with policy phase."""
        policy_template = TaskTemplate.objects.create(
            name="policy_template",
            domain=StaffTask.DOMAIN_POLICY,
        )

        item = TaskTemplateItem.objects.create(
            template=policy_template,
            title="Policy Drafting",
            sequence=1,
            days_from_start=0,
            policy_phase=StaffTask.POLICY_PHASE_DRAFTING,
        )

        self.assertEqual(item.policy_phase, StaffTask.POLICY_PHASE_DRAFTING)

    def test_template_items_ordered_by_sequence(self):
        """Test that template items are ordered by sequence."""
        item3 = TaskTemplateItem.objects.create(
            template=self.template,
            title="Third",
            sequence=3,
            days_from_start=14,
        )

        item1 = TaskTemplateItem.objects.create(
            template=self.template,
            title="First",
            sequence=1,
            days_from_start=0,
        )

        item2 = TaskTemplateItem.objects.create(
            template=self.template,
            title="Second",
            sequence=2,
            days_from_start=7,
        )

        # Query items through template
        items = list(self.template.items.all())

        # Should be ordered by sequence
        self.assertEqual(items[0], item1)
        self.assertEqual(items[1], item2)
        self.assertEqual(items[2], item3)


class StaffTaskCreatedFromTemplateTests(TestCase):
    """Test the created_from_template relationship."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_approved=True,
        )

        self.template = TaskTemplate.objects.create(
            name="test_template",
            domain=StaffTask.DOMAIN_MANA,
        )

    def test_task_can_reference_template(self):
        """Test that task can reference the template it was created from."""
        task = StaffTask.objects.create(
            title="Task from Template",
            created_from_template=self.template,
            created_by=self.admin,
        )

        self.assertEqual(task.created_from_template, self.template)

    def test_template_tracks_created_tasks(self):
        """Test that template can access tasks created from it."""
        task1 = StaffTask.objects.create(
            title="Task 1",
            created_from_template=self.template,
            created_by=self.admin,
        )

        task2 = StaffTask.objects.create(
            title="Task 2",
            created_from_template=self.template,
            created_by=self.admin,
        )

        created_tasks = self.template.created_tasks.all()

        self.assertEqual(created_tasks.count(), 2)
        self.assertIn(task1, created_tasks)
        self.assertIn(task2, created_tasks)

    def test_task_without_template_reference(self):
        """Test that manually created tasks don't have template reference."""
        task = StaffTask.objects.create(
            title="Manual Task",
            created_by=self.admin,
        )

        self.assertIsNone(task.created_from_template)
