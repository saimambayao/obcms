"""Tests for task automation service and template-based task generation."""

from datetime import date, datetime, time, timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from common.models import (
    CalendarResource,
    CalendarResourceBooking,
    StaffTask,
    TaskTemplate,
    TaskTemplateItem,
    User,
)
from common.services.task_automation import create_tasks_from_template
from common.tests.factories import create_assessment, create_event


class TaskAutomationServiceTests(TestCase):
    """Test the core task automation service functions."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )

        # Create a test template
        self.template = TaskTemplate.objects.create(
            name="test_template",
            domain=StaffTask.DOMAIN_MANA,
            description="Test template for automation",
            is_active=True,
        )

        # Create template items
        self.item1 = TaskTemplateItem.objects.create(
            template=self.template,
            title="Task 1: {assessment_name}",
            description="Complete task 1 for {assessment_name}",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            task_category="planning",
            estimated_hours=4,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_PLANNING,
        )

        self.item2 = TaskTemplateItem.objects.create(
            template=self.template,
            title="Task 2: Data collection",
            description="Collect data for assessment",
            sequence=2,
            days_from_start=7,
            priority=StaffTask.PRIORITY_MEDIUM,
            task_category="data_collection",
            estimated_hours=8,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
        )

        self.item3 = TaskTemplateItem.objects.create(
            template=self.template,
            title="Task 3: {assessment_name} analysis",
            description="Analyze data for {assessment_name}",
            sequence=3,
            days_from_start=14,
            priority=StaffTask.PRIORITY_HIGH,
            task_category="analysis",
            estimated_hours=6,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_ANALYSIS,
        )

    def test_create_tasks_from_template_basic(self):
        """Test creating tasks from a template with minimal arguments."""
        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
        )

        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].title, "Task 1: {assessment_name}")
        self.assertEqual(tasks[0].priority, StaffTask.PRIORITY_HIGH)
        self.assertEqual(tasks[0].domain, StaffTask.DOMAIN_MANA)
        self.assertEqual(tasks[0].created_by, self.admin)

    def test_create_tasks_from_template_with_context(self):
        """Test template variable substitution in title and description."""
        # Create a fake assessment object for the FK relationship
        assessment = create_assessment(
            created_by=self.admin,
            title="Region IX Baseline Assessment",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 30),
        )

        tasks = create_tasks_from_template(
            "test_template",
            related_assessment=assessment,
            assessment_name="Region IX Baseline Assessment",
            created_by=self.admin,
        )

        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].title, "Task 1: Region IX Baseline Assessment")
        self.assertIn("Region IX Baseline Assessment", tasks[0].description)
        self.assertEqual(
            tasks[2].title, "Task 3: Region IX Baseline Assessment analysis"
        )

    def test_create_tasks_with_custom_start_date(self):
        """Test due dates calculated from custom start date."""
        start_date = date(2025, 10, 15)
        tasks = create_tasks_from_template(
            "test_template",
            start_date=start_date,
            created_by=self.admin,
        )

        self.assertEqual(tasks[0].due_date, start_date)  # days_from_start=0
        self.assertEqual(tasks[1].due_date, start_date + timedelta(days=7))
        self.assertEqual(tasks[2].due_date, start_date + timedelta(days=14))

    def test_create_tasks_with_default_start_date(self):
        """Test due dates calculated from today when start_date not provided."""
        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
        )

        today = timezone.now().date()
        self.assertEqual(tasks[0].due_date, today)
        self.assertEqual(tasks[1].due_date, today + timedelta(days=7))
        self.assertEqual(tasks[2].due_date, today + timedelta(days=14))

    def test_create_tasks_copies_template_fields(self):
        """Test that task fields are correctly copied from template items."""
        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
        )

        # Check first task
        self.assertEqual(tasks[0].priority, StaffTask.PRIORITY_HIGH)
        self.assertEqual(tasks[0].task_category, "planning")
        self.assertEqual(tasks[0].estimated_hours, 4)
        self.assertEqual(tasks[0].assessment_phase, StaffTask.ASSESSMENT_PHASE_PLANNING)
        self.assertEqual(tasks[0].created_from_template, self.template)

        # Check second task
        self.assertEqual(tasks[1].priority, StaffTask.PRIORITY_MEDIUM)
        self.assertEqual(tasks[1].task_category, "data_collection")
        self.assertEqual(tasks[1].estimated_hours, 8)
        self.assertEqual(
            tasks[1].assessment_phase, StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION
        )

    def test_create_tasks_inactive_template_returns_empty(self):
        """Test that inactive templates don't create tasks."""
        self.template.is_active = False
        self.template.save()

        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
        )

        self.assertEqual(len(tasks), 0)

    def test_create_tasks_nonexistent_template_returns_empty(self):
        """Test that nonexistent template names return empty list."""
        tasks = create_tasks_from_template(
            "nonexistent_template",
            created_by=self.admin,
        )

        self.assertEqual(len(tasks), 0)

    def test_create_tasks_with_related_objects(self):
        """Test passing related objects as kwargs (simulating FK assignments)."""
        assessment = create_assessment(
            created_by=self.admin,
            title="Test Assessment",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 15),
        )

        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
            related_assessment=assessment,
        )

        # All tasks should be created successfully
        self.assertEqual(len(tasks), 3)
        # Verify all tasks are linked to the assessment
        for task in tasks:
            self.assertEqual(task.related_assessment, assessment)

    def test_variable_substitution_handles_missing_keys(self):
        """Test that missing template variables don't break task creation."""
        # Template has {assessment_name} placeholder but we don't provide it
        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
            # No assessment_name provided
        )

        # Should still create tasks, just without substitution
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].title, "Task 1: {assessment_name}")
        self.assertEqual(tasks[2].title, "Task 3: {assessment_name} analysis")

    def test_create_tasks_with_resource_bookings(self):
        """Resource booking specs should create CalendarResourceBooking entries."""

        resource = CalendarResource.objects.create(
            resource_type=CalendarResource.RESOURCE_ROOM,
            name="Planning Room",
            description="Main conference room",
        )

        start_date = date(2025, 12, 1)

        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
            start_date=start_date,
            resource_bookings={
                "default": [
                    {
                        "resource_id": resource.id,
                        "start_offset_hours": 1,
                        "duration_hours": 3,
                        "notes": "Automation booking",
                    }
                ]
            },
        )

        self.assertEqual(len(tasks), 3)
        first_task = tasks[0]

        booking = CalendarResourceBooking.objects.get(
            content_type__model="stafftask",
            object_id=first_task.pk,
        )
        self.assertEqual(booking.resource, resource)
        self.assertEqual(booking.notes, "Automation booking")
        self.assertEqual(booking.booked_by, self.admin)
        tz = timezone.get_current_timezone()
        expected_start = timezone.make_aware(
            datetime.combine(start_date, time(hour=8)), tz
        ) + timedelta(hours=1)
        expected_end = expected_start + timedelta(hours=3)
        self.assertEqual(booking.start_datetime, expected_start)
        self.assertEqual(booking.end_datetime, expected_end)

    def test_create_tasks_with_bad_resource_booking_spec_raises(self):
        """Invalid booking specifications should surface validation errors."""

        with self.assertRaises(ValidationError):
            create_tasks_from_template(
                "test_template",
                created_by=self.admin,
                resource_bookings={"default": [{"resource_name": "Unknown"}]},
            )

    def test_create_tasks_resource_booking_conflict_raises(self):
        """Overlapping bookings should trigger model validation errors."""

        resource = CalendarResource.objects.create(
            resource_type=CalendarResource.RESOURCE_ROOM,
            name="Coordination Hub",
        )

        start_date = date(2025, 12, 5)
        existing_start = timezone.make_aware(datetime.combine(start_date, time(hour=9)))
        existing_end = existing_start + timedelta(hours=2)

        CalendarResourceBooking.objects.create(
            resource=resource,
            booked_by=self.admin,
            start_datetime=existing_start,
            end_datetime=existing_end,
            status=CalendarResourceBooking.STATUS_APPROVED,
            notes="Existing booking",
        )

        with self.assertRaises(ValidationError):
            create_tasks_from_template(
                "test_template",
                created_by=self.admin,
                start_date=start_date,
                resource_bookings={
                    "default": [
                        {
                            "resource_id": resource.id,
                            "start_offset_hours": 1,
                            "duration_hours": 2,
                        }
                    ]
                },
            )

    def test_tasks_created_with_not_started_status(self):
        """Test that all tasks are created with NOT_STARTED status."""
        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
        )

        for task in tasks:
            self.assertEqual(task.status, StaffTask.STATUS_NOT_STARTED)

    def test_template_with_policy_phase_items(self):
        """Test template items with policy phase fields."""
        policy_template = TaskTemplate.objects.create(
            name="policy_template",
            domain=StaffTask.DOMAIN_POLICY,
            description="Policy development template",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=policy_template,
            title="Draft policy brief",
            description="Create initial policy brief",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            task_category="drafting",
            estimated_hours=6,
            policy_phase=StaffTask.POLICY_PHASE_EVIDENCE,
        )

        tasks = create_tasks_from_template(
            "policy_template",
            created_by=self.admin,
        )

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].domain, StaffTask.DOMAIN_POLICY)
        self.assertEqual(tasks[0].policy_phase, StaffTask.POLICY_PHASE_EVIDENCE)

    def test_template_with_service_phase_items(self):
        """Test template items with service phase fields."""
        service_template = TaskTemplate.objects.create(
            name="service_template",
            domain=StaffTask.DOMAIN_SERVICES,
            description="Service processing template",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=service_template,
            title="Review application",
            description="Review service application",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_MEDIUM,
            task_category="review",
            estimated_hours=2,
            service_phase=StaffTask.SERVICE_PHASE_REVIEW,
        )

        tasks = create_tasks_from_template(
            "service_template",
            created_by=self.admin,
        )

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].domain, StaffTask.DOMAIN_SERVICES)
        self.assertEqual(tasks[0].service_phase, StaffTask.SERVICE_PHASE_REVIEW)

    def test_multiple_variable_substitutions(self):
        """Test multiple variables in a single template."""
        multi_var_template = TaskTemplate.objects.create(
            name="multi_var_template",
            domain=StaffTask.DOMAIN_COORDINATION,
            description="Multi-variable template",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=multi_var_template,
            title="{event_name} - {region} coordination",
            description="Coordinate {event_name} in {region}",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            task_category="coordination",
            estimated_hours=4,
        )

        event = create_event(
            created_by=self.admin,
            title="Regional Workshop",
            event_type="workshop",
            start_date=date(2025, 11, 15),
        )

        tasks = create_tasks_from_template(
            "multi_var_template",
            linked_event=event,
            event_name="Regional Workshop",
            region="Region IX",
            created_by=self.admin,
        )

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Regional Workshop - Region IX coordination")
        self.assertIn("Regional Workshop", tasks[0].description)
        self.assertIn("Region IX", tasks[0].description)

    def test_tasks_persist_to_database(self):
        """Test that created tasks are actually saved to database."""
        initial_count = StaffTask.objects.count()

        tasks = create_tasks_from_template(
            "test_template",
            created_by=self.admin,
        )

        self.assertEqual(StaffTask.objects.count(), initial_count + 3)

        # Verify we can retrieve them from database
        db_task = StaffTask.objects.get(id=tasks[0].id)
        self.assertEqual(db_task.title, tasks[0].title)
        self.assertEqual(db_task.created_from_template, self.template)
