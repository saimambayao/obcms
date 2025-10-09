"""Tests for extended task management views (domain, analytics, templates)."""

import pytest

pytest.skip(
    "Legacy task view tests require StaffTask/TaskTemplate routes removed in WorkItem refactor.",
    allow_module_level=True,
)

import json
import uuid
from datetime import date, timedelta
from unittest.mock import patch

from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from common.models import (
    StaffTask,
    StaffTeam,
    TaskTemplate,
    TaskTemplateItem,
    User,
)
from common.tests.factories import (
    create_assessment,
    create_event,
    create_policy_recommendation,
)


class DomainTasksViewTests(TestCase):
    """Test the domain-filtered task views."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.client.force_login(self.admin)
        self.factory = RequestFactory()

        self.team = StaffTeam.objects.create(name="MANA Team")

        # Create tasks in different domains
        self.mana_task = StaffTask.objects.create(
            title="MANA Assessment Planning",
            domain=StaffTask.DOMAIN_MANA,
            created_by=self.admin,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_PLANNING,
        )
        self.mana_task.teams.add(self.team)

        self.policy_task = StaffTask.objects.create(
            title="Policy Brief Development",
            domain=StaffTask.DOMAIN_POLICY,
            created_by=self.admin,
            policy_phase=StaffTask.POLICY_PHASE_EVIDENCE,
        )
        self.policy_task.teams.add(self.team)

        self.coordination_task = StaffTask.objects.create(
            title="Stakeholder Meeting",
            domain=StaffTask.DOMAIN_COORDINATION,
            created_by=self.admin,
        )
        self.coordination_task.teams.add(self.team)

    def test_domain_tasks_view_filters_by_domain(self):
        """Test that domain tasks view only shows tasks from specified domain."""
        url = reverse("common:tasks_by_domain", kwargs={"domain": "mana"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        tasks = response.context["tasks"]

        # Should only contain MANA tasks
        self.assertIn(self.mana_task, tasks)
        self.assertNotIn(self.policy_task, tasks)
        self.assertNotIn(self.coordination_task, tasks)

    def test_domain_tasks_view_shows_all_domains(self):
        """Test that we can access different domain views."""
        domains = ["mana", "coordination", "policy", "monitoring", "services"]

        for domain in domains:
            url = reverse("common:tasks_by_domain", kwargs={"domain": domain})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_domain_tasks_view_filters_by_status(self):
        """Test filtering domain tasks by status."""
        # Create completed task
        completed_task = StaffTask.objects.create(
            title="Completed MANA Task",
            domain=StaffTask.DOMAIN_MANA,
            status=StaffTask.STATUS_COMPLETED,
            created_by=self.admin,
        )
        completed_task.teams.add(self.team)

        url = reverse("common:tasks_by_domain", kwargs={"domain": "mana"})
        response = self.client.get(url, {"status": "completed"})

        self.assertEqual(response.status_code, 200)
        tasks = list(response.context["tasks"])

        self.assertIn(completed_task, tasks)
        self.assertNotIn(self.mana_task, tasks)  # not_started task

    def test_domain_tasks_view_filters_by_priority(self):
        """Test filtering domain tasks by priority."""
        high_priority_task = StaffTask.objects.create(
            title="Urgent MANA Task",
            domain=StaffTask.DOMAIN_MANA,
            priority=StaffTask.PRIORITY_HIGH,
            created_by=self.admin,
        )
        high_priority_task.teams.add(self.team)

        url = reverse("common:tasks_by_domain", kwargs={"domain": "mana"})
        response = self.client.get(url, {"priority": "high"})

        self.assertEqual(response.status_code, 200)
        tasks = list(response.context["tasks"])

        self.assertIn(high_priority_task, tasks)

    def test_domain_task_analytics_returns_stats(self):
        """Domain analytics view provides aggregate stats."""
        request = self.factory.get(
            reverse(
                "common:domain_task_analytics", kwargs={"domain": StaffTask.DOMAIN_MANA}
            )
        )
        request.user = self.admin

        with patch("common.views.tasks.render") as mock_render:
            mock_render.return_value = HttpResponse()
            from common.views import tasks as task_views

            task_views.domain_task_analytics(request, StaffTask.DOMAIN_MANA)

            args, _ = mock_render.call_args
            context = args[2]
            self.assertGreaterEqual(context["stats"]["total"], 1)


class AssessmentTasksViewTests(TestCase):
    """Test the assessment-specific task view."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.client.force_login(self.admin)

        self.assessment = create_assessment(
            created_by=self.admin,
            title="Test Assessment",
            primary_methodology="survey",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 30),
        )

        self.team = StaffTeam.objects.create(name="Assessment Team")

        # Create tasks in different phases
        self.planning_task = StaffTask.objects.create(
            title="Assessment Planning",
            domain=StaffTask.DOMAIN_MANA,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_PLANNING,
            related_assessment=self.assessment,
            created_by=self.admin,
        )
        self.planning_task.teams.add(self.team)

        self.data_task = StaffTask.objects.create(
            title="Data Collection",
            domain=StaffTask.DOMAIN_MANA,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            related_assessment=self.assessment,
            created_by=self.admin,
        )
        self.data_task.teams.add(self.team)

        self.analysis_task = StaffTask.objects.create(
            title="Data Analysis",
            domain=StaffTask.DOMAIN_MANA,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            related_assessment=self.assessment,
            created_by=self.admin,
        )
        self.analysis_task.teams.add(self.team)

    def test_assessment_tasks_view_groups_by_phase(self):
        """Test that assessment tasks are grouped by phase."""
        url = reverse(
            "common:assessment_tasks", kwargs={"assessment_id": self.assessment.id}
        )
        with patch("common.views.tasks.render") as mock_render:
            mock_render.return_value = HttpResponse()
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        tasks_by_phase = mock_render.call_args[0][2]["tasks_by_phase"]

        self.assertIn("planning", tasks_by_phase)
        self.assertIn("data_collection", tasks_by_phase)
        self.assertIn("analysis", tasks_by_phase)

        self.assertIn(self.planning_task, tasks_by_phase["planning"])
        self.assertIn(self.data_task, tasks_by_phase["data_collection"])
        self.assertIn(self.analysis_task, tasks_by_phase["analysis"])

    def test_assessment_tasks_view_unknown_assessment_returns_404(self):
        """Requesting non-existent assessment returns 404."""
        url = reverse("common:assessment_tasks", kwargs={"assessment_id": uuid.uuid4()})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class EventTasksViewTests(TestCase):
    """Test the event-specific task view."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.client.force_login(self.admin)

        self.event = create_event(
            created_by=self.admin,
            title="Coordination Meeting",
            event_type="meeting",
            start_date=date(2025, 12, 1),
        )

        self.event_task = StaffTask.objects.create(
            title="Prepare agenda",
            domain=StaffTask.DOMAIN_COORDINATION,
            linked_event=self.event,
            created_by=self.admin,
        )

    def test_event_tasks_view_accessible(self):
        """Test that event tasks view is accessible."""
        url = reverse("common:event_tasks", kwargs={"event_id": self.event.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("tasks", response.context)
        self.assertIn(self.event_task, response.context["tasks"])


class PolicyTasksViewTests(TestCase):
    """Test the policy-specific task view."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.client.force_login(self.admin)

        self.team = StaffTeam.objects.create(name="Policy Team")

        self.policy = create_policy_recommendation(
            proposed_by=self.admin,
            title="Policy Recommendation",
            status="draft",
        )

        # Create policy tasks in different phases
        self.research_task = StaffTask.objects.create(
            title="Policy Research",
            domain=StaffTask.DOMAIN_POLICY,
            policy_phase=StaffTask.POLICY_PHASE_EVIDENCE,
            created_by=self.admin,
            related_policy=self.policy,
        )
        self.research_task.teams.add(self.team)

        self.drafting_task = StaffTask.objects.create(
            title="Policy Drafting",
            domain=StaffTask.DOMAIN_POLICY,
            policy_phase=StaffTask.POLICY_PHASE_DRAFTING,
            created_by=self.admin,
            related_policy=self.policy,
        )
        self.drafting_task.teams.add(self.team)

    def test_policy_tasks_view_groups_by_phase(self):
        """Test that policy tasks are grouped by phase."""
        url = reverse("common:policy_tasks", kwargs={"policy_id": self.policy.id})
        with patch("common.views.tasks.render") as mock_render:
            mock_render.return_value = HttpResponse()
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        tasks_by_phase = mock_render.call_args[0][2]["tasks_by_phase"]

        self.assertIn("evidence_collection", tasks_by_phase)
        self.assertIn("drafting", tasks_by_phase)


class TaskAnalyticsViewTests(TestCase):
    """Test the task analytics dashboard."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.client.force_login(self.admin)

        self.team = StaffTeam.objects.create(name="Analytics Team")

        # Create diverse tasks for analytics
        for i in range(5):
            task = StaffTask.objects.create(
                title=f"MANA Task {i}",
                domain=StaffTask.DOMAIN_MANA,
                priority=(
                    StaffTask.PRIORITY_HIGH if i % 2 == 0 else StaffTask.PRIORITY_MEDIUM
                ),
                status=(
                    StaffTask.STATUS_COMPLETED
                    if i < 3
                    else StaffTask.STATUS_IN_PROGRESS
                ),
                estimated_hours=4 + i,
                created_by=self.admin,
            )
            task.teams.add(self.team)

        for i in range(3):
            task = StaffTask.objects.create(
                title=f"Policy Task {i}",
                domain=StaffTask.DOMAIN_POLICY,
                priority=StaffTask.PRIORITY_MEDIUM,
                status=StaffTask.STATUS_IN_PROGRESS,
                estimated_hours=6,
                created_by=self.admin,
            )
            task.teams.add(self.team)

    def test_analytics_view_accessible(self):
        """Test that analytics view is accessible."""
        url = reverse("common:task_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_analytics_view_calculates_domain_breakdown(self):
        """Test that analytics calculates domain breakdown."""
        url = reverse("common:task_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        domain_breakdown = list(response.context["domain_breakdown"])

        self.assertGreater(len(domain_breakdown), 0)

        mana_entry = next(
            (d for d in domain_breakdown if d["domain"] == StaffTask.DOMAIN_MANA), None
        )
        self.assertIsNotNone(mana_entry)

    def test_analytics_view_calculates_completion_rate(self):
        """Test that analytics calculates completion rates."""
        url = reverse("common:task_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        completion_rates = response.context["completion_rates"]

        self.assertGreater(len(completion_rates), 0)
        mana_rate = next(
            (
                entry
                for entry in completion_rates
                if entry["domain"]
                == dict(StaffTask.DOMAIN_CHOICES)[StaffTask.DOMAIN_MANA]
            ),
            None,
        )
        self.assertIsNotNone(mana_rate)

    def test_analytics_view_calculates_priority_distribution(self):
        """Test that analytics shows priority distribution."""
        url = reverse("common:task_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        priority_breakdown = response.context["priority_breakdown"]

        self.assertGreater(len(priority_breakdown), 0)

    def test_analytics_view_recent_completed_counts(self):
        """Recent completed count reflects tasks finished in last 30 days."""
        self.mana_task_completed = StaffTask.objects.create(
            title="Recent Completed",
            domain=StaffTask.DOMAIN_MANA,
            status=StaffTask.STATUS_COMPLETED,
            completed_at=timezone.now(),
            created_by=self.admin,
        )

        url = reverse("common:task_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.context["recent_completed"], 1)


class EnhancedDashboardViewTests(TestCase):
    """Test the enhanced personal task dashboard."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.staff = User.objects.create_user(
            username="staff",
            password="pass1234",
            user_type="oobc_staff",
            is_approved=True,
        )
        self.client.force_login(self.staff)

        self.team = StaffTeam.objects.create(name="My Team")

        # Create tasks assigned to staff
        self.my_task = StaffTask.objects.create(
            title="My Task",
            domain=StaffTask.DOMAIN_MANA,
            status=StaffTask.STATUS_IN_PROGRESS,
            created_by=self.admin,
        )
        self.my_task.teams.add(self.team)
        self.my_task.assignees.set([self.staff])

        self.other_task = StaffTask.objects.create(
            title="Other Task",
            domain=StaffTask.DOMAIN_POLICY,
            status=StaffTask.STATUS_NOT_STARTED,
            created_by=self.admin,
        )
        self.other_task.teams.add(self.team)

    def test_enhanced_dashboard_shows_user_tasks(self):
        """Test that enhanced dashboard shows tasks assigned to user."""
        url = reverse("common:enhanced_task_dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        tasks = list(response.context["my_tasks"])

        # Should include tasks assigned to this user
        self.assertIn(self.my_task, tasks)

    def test_enhanced_dashboard_filters_by_domain(self):
        """Test filtering enhanced dashboard by domain."""
        url = reverse("common:enhanced_task_dashboard")
        response = self.client.get(url, {"domain": StaffTask.DOMAIN_MANA})

        self.assertEqual(response.status_code, 200)
        tasks = list(response.context["my_tasks"])

        # Should only show MANA domain tasks
        self.assertIn(self.my_task, tasks)
        self.assertEqual(response.context["selected_domain"], StaffTask.DOMAIN_MANA)

    def test_enhanced_dashboard_calculates_personal_stats(self):
        """Test that enhanced dashboard calculates personal statistics."""
        url = reverse("common:enhanced_task_dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # Should have stats in context
        self.assertIn("stats", response.context)


class TaskTemplateListViewTests(TestCase):
    """Test the task template list view."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.client.force_login(self.admin)

        # Create templates
        self.template1 = TaskTemplate.objects.create(
            name="mana_assessment_basic",
            domain=StaffTask.DOMAIN_MANA,
            description="Basic MANA assessment",
            is_active=True,
        )

        self.template2 = TaskTemplate.objects.create(
            name="policy_development",
            domain=StaffTask.DOMAIN_POLICY,
            description="Policy development cycle",
            is_active=True,
        )

        self.inactive_template = TaskTemplate.objects.create(
            name="deprecated_template",
            domain=StaffTask.DOMAIN_COORDINATION,
            description="Old template",
            is_active=False,
        )

    def test_template_list_shows_active_templates(self):
        """Test that template list shows only active templates."""
        url = reverse("common:task_template_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        templates = list(response.context["templates"])

        self.assertIn(self.template1, templates)
        self.assertIn(self.template2, templates)
        self.assertNotIn(self.inactive_template, templates)

    def test_template_list_filters_by_domain(self):
        """Test filtering templates by domain."""
        url = reverse("common:task_template_list")
        response = self.client.get(url, {"domain": "mana"})

        self.assertEqual(response.status_code, 200)
        templates = list(response.context["templates"])

        self.assertIn(self.template1, templates)
        self.assertNotIn(self.template2, templates)


class TaskTemplateDetailViewTests(TestCase):
    """Test the task template detail view."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.client.force_login(self.admin)

        # Create template with items
        self.template = TaskTemplate.objects.create(
            name="test_template",
            domain=StaffTask.DOMAIN_MANA,
            description="Test template",
            is_active=True,
        )

        self.item1 = TaskTemplateItem.objects.create(
            template=self.template,
            title="Task 1",
            description="First task",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

        self.item2 = TaskTemplateItem.objects.create(
            template=self.template,
            title="Task 2",
            description="Second task",
            sequence=2,
            days_from_start=7,
            priority=StaffTask.PRIORITY_MEDIUM,
        )

    def test_template_detail_shows_template_info(self):
        """Test that template detail shows template information."""
        url = reverse(
            "common:task_template_detail", kwargs={"template_id": self.template.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["template"], self.template)

    def test_template_detail_shows_all_items(self):
        """Test that template detail shows all template items."""
        url = reverse(
            "common:task_template_detail", kwargs={"template_id": self.template.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        items = list(response.context["items"])

        self.assertIn(self.item1, items)
        self.assertIn(self.item2, items)
        self.assertEqual(len(items), 2)

    def test_template_detail_items_ordered_by_sequence(self):
        """Test that template items are ordered by sequence."""
        url = reverse(
            "common:task_template_detail", kwargs={"template_id": self.template.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        items = list(response.context["items"])

        # Items should be in sequence order
        self.assertEqual(items[0], self.item1)
        self.assertEqual(items[1], self.item2)


class TaskTemplateInstantiateViewTests(TestCase):
    """Test the task template instantiation endpoint."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_approved=True,
        )
        self.client.force_login(self.admin)

        self.team = StaffTeam.objects.create(name="Test Team")

        # Create template
        self.template = TaskTemplate.objects.create(
            name="instantiate_test",
            domain=StaffTask.DOMAIN_MANA,
            description="Template for instantiation testing",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Task from template",
            description="Auto-created task",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
        )

    def test_instantiate_template_creates_tasks(self):
        """Test that instantiating a template creates tasks."""
        initial_count = StaffTask.objects.count()

        url = reverse(
            "common:instantiate_template", kwargs={"template_id": self.template.id}
        )
        response = self.client.post(url, {"context": json.dumps({})})

        self.assertEqual(response.status_code, 200)
        self.assertGreater(StaffTask.objects.count(), initial_count)

        # Verify response
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["tasks_created"], 0)

    def test_instantiate_nonexistent_template_fails(self):
        """Test that instantiating nonexistent template fails gracefully."""
        url = reverse("common:instantiate_template", kwargs={"template_id": 99999})
        response = self.client.post(url, {"context": json.dumps({})})

        self.assertEqual(response.status_code, 404)
