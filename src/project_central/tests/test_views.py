"""Tests for Project Central views."""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from common.models import (
    StaffTask,
    TaskTemplate,
    TaskTemplateItem,
    CalendarResource,
    CalendarResourceBooking,
)
from common.tests.factories import create_community
from mana.models import Need, NeedsCategory
from monitoring.models import MonitoringEntry
from project_central.models import ProjectWorkflow

User = get_user_model()


def ensure_template(name: str) -> TaskTemplate:
    template, created = TaskTemplate.objects.get_or_create(
        name=name,
        defaults={
            "domain": StaffTask.DOMAIN_PROJECT_CENTRAL,
            "description": f"Auto template for {name}",
            "is_active": True,
        },
    )
    if created or not template.items.exists():
        TaskTemplateItem.objects.create(
            template=template,
            title=f"{name.replace('_', ' ').title()} Task",
            description="Auto-generated task",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            task_category="project",
        )
    return template


class MyTasksWithProjectsViewTests(TestCase):
    """Validate the HTMX-enabled project task listing."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="pc_user",
            email="pc@example.com",
            password="pass1234",
        )
        self.client.force_login(self.user)

        self.need = self._create_need()
        self.ppa = MonitoringEntry.objects.create(
            title="Community Livelihood Support",
            category="moa_ppa",
            status="planning",
            priority="medium",
            created_by=self.user,
        )
        self.workflow = ProjectWorkflow.objects.create(
            primary_need=self.need,
            ppa=self.ppa,
            current_stage="budget_planning",
            project_lead=self.user,
            created_by=self.user,
        )

        self.workflow_task = StaffTask.objects.create(
            title="Prepare budget matrix",
            status=StaffTask.STATUS_IN_PROGRESS,
            domain=StaffTask.DOMAIN_PROJECT_CENTRAL,
            due_date=date.today() + timedelta(days=5),
            linked_workflow=self.workflow,
            created_by=self.user,
        )
        self.workflow_task.assignees.add(self.user)

        self.monitoring_task = StaffTask.objects.create(
            title="Compile field report",
            status=StaffTask.STATUS_COMPLETED,
            domain=StaffTask.DOMAIN_MONITORING,
            due_date=date.today() - timedelta(days=1),
            related_ppa=self.ppa,
            created_by=self.user,
        )
        self.monitoring_task.assignees.add(self.user)

        self.overdue_task = StaffTask.objects.create(
            title="Follow up with MAO",
            status=StaffTask.STATUS_NOT_STARTED,
            domain=StaffTask.DOMAIN_PROJECT_CENTRAL,
            due_date=date.today() - timedelta(days=2),
            linked_workflow=self.workflow,
            created_by=self.user,
        )
        self.overdue_task.assignees.add(self.user)

        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass1234",
        )
        unrelated_task = StaffTask.objects.create(
            title="Other project task",
            status=StaffTask.STATUS_NOT_STARTED,
            domain=StaffTask.DOMAIN_PROJECT_CENTRAL,
            due_date=date.today() + timedelta(days=3),
            created_by=other_user,
        )
        unrelated_task.assignees.add(other_user)

    def _create_need(self):
        community = create_community(name="Barangay Uno")
        category = NeedsCategory.objects.create(
            name="Livelihood",
            sector="economic_development",
            description="Livelihood support",
        )
        return Need.objects.create(
            title="Livelihood Assistance",
            description="Provide livelihood kits to displaced families.",
            category=category,
            community=community,
            affected_population=150,
            geographic_scope="Barangay Uno",
            urgency_level="short_term",
            impact_severity=3,
            feasibility="medium",
            evidence_sources="Community survey",
            identified_by=self.user,
        )

    def test_view_lists_user_tasks(self):
        url = reverse("project_central:my_tasks_with_projects")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_central/my_tasks.html")
        self.assertContains(response, "Prepare budget matrix")
        self.assertContains(response, "Compile field report")
        self.assertNotContains(response, "Other project task")
        self.assertIn("summary", response.context)
        self.assertEqual(response.context["summary"]["total"], 3)

    def test_stage_filter_limits_results(self):
        url = reverse("project_central:my_tasks_with_projects")
        response = self.client.get(url, {"stage": "budget_planning"})

        self.assertContains(response, "Prepare budget matrix")
        self.assertContains(response, "Follow up with MAO")
        self.assertNotContains(response, "Compile field report")

    def test_status_filter_limits_results(self):
        url = reverse("project_central:my_tasks_with_projects")
        response = self.client.get(url, {"status": StaffTask.STATUS_COMPLETED})

        self.assertContains(response, "Compile field report")
        self.assertNotContains(response, "Prepare budget matrix")

    def test_search_filters_results(self):
        url = reverse("project_central:my_tasks_with_projects")
        response = self.client.get(url, {"q": "budget matrix"})

        self.assertContains(response, "Prepare budget matrix")
        self.assertNotContains(response, "Compile field report")

    def test_htmx_request_renders_partial(self):
        url = reverse("project_central:my_tasks_with_projects")
        response = self.client.get(
            url,
            {"status": StaffTask.STATUS_COMPLETED},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "project_central/partials/project_task_table.html"
        )
        content = response.content.decode()
        self.assertIn("Compile field report", content)
        self.assertNotIn("Prepare budget matrix", content)
        self.assertIn(f'data-task-id="{self.monitoring_task.id}"', content)

    def test_overdue_filter(self):
        url = reverse("project_central:my_tasks_with_projects")
        response = self.client.get(url, {"overdue": "1"})

        self.assertContains(response, "Follow up with MAO")
        self.assertNotContains(response, "Prepare budget matrix")


class GenerateWorkflowTasksViewTests(TestCase):
    """Ensure workflow task generation triggers template-based creation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="workflow_user",
            email="workflow@example.com",
            password="pass1234",
        )
        self.client.force_login(self.user)

        community = create_community(name="Barangay Dos")
        category = NeedsCategory.objects.create(
            name="Infrastructure",
            sector="infrastructure",
            description="Infrastructure support",
        )
        self.need = Need.objects.create(
            title="Road Repair",
            description="Repair main access road",
            category=category,
            community=community,
            affected_population=200,
            geographic_scope="Barangay Dos",
            urgency_level="short_term",
            impact_severity=4,
            feasibility="medium",
            evidence_sources="Barangay report",
            identified_by=self.user,
        )

        self.ppa = MonitoringEntry.objects.create(
            title="Road Rehabilitation PPA",
            category="moa_ppa",
            status="planning",
            priority="medium",
            created_by=self.user,
        )

        self.workflow = ProjectWorkflow.objects.create(
            primary_need=self.need,
            ppa=self.ppa,
            current_stage="budget_planning",
            project_lead=self.user,
            created_by=self.user,
        )

        ensure_template("project_budget_planning")

    def test_generate_workflow_tasks_creates_records(self):
        url = reverse(
            "project_central:generate_workflow_tasks", args=[self.workflow.id]
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("project_central:project_workflow_detail", args=[self.workflow.id]),
        )
        tasks = StaffTask.objects.filter(linked_workflow=self.workflow)
        self.assertTrue(tasks.exists())

    def test_generate_workflow_tasks_is_idempotent(self):
        url = reverse(
            "project_central:generate_workflow_tasks", args=[self.workflow.id]
        )
        self.client.post(url)
        initial_count = StaffTask.objects.filter(linked_workflow=self.workflow).count()

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("project_central:project_workflow_detail", args=[self.workflow.id]),
        )
        self.assertEqual(
            StaffTask.objects.filter(linked_workflow=self.workflow).count(),
            initial_count,
        )


class GenerateWorkflowTasksResourceBookingTests(TestCase):
    """Verify resource booking integration can be triggered via workflow view."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="workflow_resource",
            email="workflow_resource@example.com",
            password="pass1234",
        )
        self.client.force_login(self.user)

        community = create_community(name="Barangay Tres")
        category = NeedsCategory.objects.create(
            name="Health",
            sector="health",
            description="Health interventions",
        )
        self.need = Need.objects.create(
            title="Medical Mission",
            description="Conduct medical mission",
            category=category,
            community=community,
            affected_population=300,
            geographic_scope="Barangay Tres",
            urgency_level="short_term",
            impact_severity=3,
            feasibility="high",
            evidence_sources="Health survey",
            identified_by=self.user,
        )

        self.ppa = MonitoringEntry.objects.create(
            title="Medical Mission PPA",
            category="moa_ppa",
            status="planning",
            priority="medium",
            created_by=self.user,
        )

        self.workflow = ProjectWorkflow.objects.create(
            primary_need=self.need,
            ppa=self.ppa,
            current_stage="monitoring",
            project_lead=self.user,
            created_by=self.user,
        )

        ensure_template("project_monitoring")
        self.resource = CalendarResource.objects.create(
            resource_type=CalendarResource.RESOURCE_ROOM,
            name="Strategy Room",
        )

    def test_generate_with_resource_hint(self):
        url = reverse(
            "project_central:generate_workflow_tasks", args=[self.workflow.id]
        )
        response = self.client.post(
            f"{url}?auto_resource=1&resource_name={self.resource.name}"
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("project_central:project_workflow_detail", args=[self.workflow.id]),
        )
        tasks = StaffTask.objects.filter(linked_workflow=self.workflow)
        self.assertTrue(tasks.exists())
        booking_exists = CalendarResourceBooking.objects.filter(
            resource=self.resource,
            object_id__in=tasks.values_list("pk", flat=True),
        ).exists()
        self.assertTrue(booking_exists)


class ProjectCalendarViewTests(TestCase):
    """Test project-specific calendar view and events API."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")

        # Create test community
        self.community = create_community(
            name="Test Barangay",
            municipality_name="Test Municipality"
        )

        # Create need category
        self.category = NeedsCategory.objects.create(
            name="Education",
            description="Education needs"
        )

        # Create need
        self.need = Need.objects.create(
            title="Test Need for Calendar",
            description="Test need description",
            category=self.category,
            barangay=self.community,
            status="identified",
            priority_score=8.0,
        )

        # Create workflow
        self.workflow = ProjectWorkflow.objects.create(
            primary_need=self.need,
            project_lead=self.user,
            current_stage="need_identification",
            priority_level="high",
        )

    def test_calendar_view_accessible(self):
        """Test that calendar view is accessible."""
        url = reverse('project_central:project_calendar', kwargs={'workflow_id': self.workflow.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project_central/project_calendar.html')
        self.assertContains(response, 'Project Calendar')
        self.assertContains(response, self.workflow.primary_need.title)

    def test_calendar_events_api_returns_json(self):
        """Test that calendar events API returns valid JSON."""
        url = reverse('project_central:project_calendar_events', kwargs={'workflow_id': self.workflow.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        # Should return empty list initially
        import json
        events = json.loads(response.content)
        self.assertIsInstance(events, list)

    def test_calendar_events_includes_tasks(self):
        """Test that tasks with due dates appear in calendar events."""
        # Create task with due date
        task = StaffTask.objects.create(
            title="Test Calendar Task",
            description="Test task for calendar",
            linked_workflow=self.workflow,
            due_date=date.today() + timedelta(days=7),
            priority=StaffTask.PRIORITY_HIGH,
            status=StaffTask.STATUS_NOT_STARTED,
            created_by=self.user,
        )
        task.assignees.add(self.user)

        url = reverse('project_central:project_calendar_events', kwargs={'workflow_id': self.workflow.id})
        response = self.client.get(url)

        import json
        events = json.loads(response.content)

        # Should have 1 task event
        task_events = [e for e in events if e['extendedProps']['type'] == 'task']
        self.assertEqual(len(task_events), 1)
        self.assertEqual(task_events[0]['title'], 'Test Calendar Task')
        self.assertEqual(task_events[0]['backgroundColor'], '#3b82f6')

    def test_calendar_requires_login(self):
        """Test that calendar views require authentication."""
        self.client.logout()

        # Test calendar view
        url = reverse('project_central:project_calendar', kwargs={'workflow_id': self.workflow.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test events API
        url = reverse('project_central:project_calendar_events', kwargs={'workflow_id': self.workflow.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
