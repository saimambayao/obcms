"""Integration tests for end-to-end task management workflows."""

import json
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from common.models import StaffTask, StaffTeam, TaskTemplate, TaskTemplateItem, User
from common.tests.factories import (
    create_assessment,
    create_event,
    create_policy_recommendation,
)


class AssessmentTaskWorkflowIntegrationTests(TestCase):
    """Test complete workflow from assessment creation to task completion."""

    def setUp(self):
        """Set up test data."""
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_superuser=True,
            is_approved=True,
        )
        self.facilitator = User.objects.create_user(
            username="facilitator",
            password="pass1234",
            user_type="oobc_staff",
            is_approved=True,
        )
        self.client.force_login(self.admin)

        # Create assessment template
        self.template = TaskTemplate.objects.create(
            name="mana_assessment_basic",
            domain=StaffTask.DOMAIN_MANA,
            description="Basic assessment workflow",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Plan assessment: {assessment_name}",
            description="Complete assessment planning for {assessment_name}",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_PLANNING,
            estimated_hours=4,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Collect data",
            description="Data collection phase",
            sequence=2,
            days_from_start=7,
            priority=StaffTask.PRIORITY_HIGH,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            estimated_hours=8,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Analyze results",
            description="Analysis phase",
            sequence=3,
            days_from_start=14,
            priority=StaffTask.PRIORITY_MEDIUM,
            assessment_phase=StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            estimated_hours=6,
        )

        self.team = StaffTeam.objects.create(name="MANA Team", is_active=True)

    def test_complete_assessment_workflow(self):
        """Test complete workflow from assessment creation to task completion."""
        # Step 1: Create an assessment
        assessment = create_assessment(
            created_by=self.admin,
            title="Region IX Education Assessment",
            primary_methodology="survey",
            planned_start=date(2025, 11, 1),
            planned_end=date(2025, 11, 30),
        )

        # Step 2: Verify tasks were auto-created
        tasks = StaffTask.objects.filter(related_assessment=assessment).order_by(
            "due_date"
        )
        self.assertEqual(tasks.count(), 3)

        # Verify task details
        planning_task = tasks[0]
        self.assertIn("Region IX Education Assessment", planning_task.title)
        self.assertEqual(
            planning_task.assessment_phase, StaffTask.ASSESSMENT_PHASE_PLANNING
        )
        self.assertEqual(planning_task.due_date, date(2025, 11, 1))

        data_task = tasks[1]
        self.assertEqual(
            data_task.assessment_phase, StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION
        )
        self.assertEqual(data_task.due_date, date(2025, 11, 8))

        analysis_task = tasks[2]
        self.assertEqual(
            analysis_task.assessment_phase, StaffTask.ASSESSMENT_PHASE_ANALYSIS
        )
        self.assertEqual(analysis_task.due_date, date(2025, 11, 15))

        # Step 3: Assign tasks to team and staff
        for task in tasks:
            task.teams.add(self.team)
            task.assignees.set([self.facilitator])

        # Step 4: View tasks in domain view
        url = reverse("common:tasks_by_domain", kwargs={"domain": "mana"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Region IX Education Assessment")

        # Step 5: View tasks in assessment-specific view
        assessment_url = reverse(
            "common:assessment_tasks",
            kwargs={"assessment_id": assessment.id},
        )
        response = self.client.get(assessment_url)
        self.assertEqual(response.status_code, 200)

        # Verify phase grouping
        tasks_by_phase = response.context["tasks_by_phase"]
        self.assertIn("planning", tasks_by_phase)
        self.assertIn("data_collection", tasks_by_phase)
        self.assertIn("analysis", tasks_by_phase)

        # Step 6: Complete first task
        planning_task.status = StaffTask.STATUS_COMPLETED
        planning_task.progress = 100
        planning_task.completed_at = timezone.now()
        planning_task.save()

        # Step 7: Move second task to in_progress
        data_task.status = StaffTask.STATUS_IN_PROGRESS
        data_task.progress = 50
        data_task.save()

        # Step 8: Verify analytics
        analytics_url = reverse("common:task_analytics")
        response = self.client.get(analytics_url)
        self.assertEqual(response.status_code, 200)

        stats = response.context["stats"]
        self.assertGreater(stats["total_tasks"], 0)
        self.assertGreater(stats["completed_tasks"], 0)

        # Step 9: Complete remaining tasks
        data_task.status = StaffTask.STATUS_COMPLETED
        data_task.progress = 100
        data_task.completed_at = timezone.now()
        data_task.save()

        analysis_task.status = StaffTask.STATUS_COMPLETED
        analysis_task.progress = 100
        analysis_task.completed_at = timezone.now()
        analysis_task.save()

        # Step 10: Verify all tasks completed
        completed_count = StaffTask.objects.filter(
            related_assessment=assessment, status=StaffTask.STATUS_COMPLETED
        ).count()
        self.assertEqual(completed_count, 3)


class EventTaskWorkflowIntegrationTests(TestCase):
    """Test complete workflow for event-related tasks."""

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

        # Create event template
        self.template = TaskTemplate.objects.create(
            name="event_meeting_standard",
            domain=StaffTask.DOMAIN_COORDINATION,
            description="Standard meeting preparation",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Prepare agenda: {event_name}",
            description="Draft and circulate meeting agenda",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            estimated_hours=2,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Send invitations: {event_name}",
            description="Send meeting invitations to participants",
            sequence=2,
            days_from_start=7,
            priority=StaffTask.PRIORITY_HIGH,
            estimated_hours=1,
        )

        self.team = StaffTeam.objects.create(name="Coordination Team")

    def test_event_task_workflow(self):
        """Test creating event and managing its tasks."""
        # Step 1: Create event
        event = create_event(
            created_by=self.admin,
            title="Provincial Coordination Meeting",
            event_type="meeting",
            start_date=date(2025, 12, 15),
        )

        # Step 2: Verify tasks created
        tasks = StaffTask.objects.filter(linked_event=event)
        self.assertEqual(tasks.count(), 2)

        # Step 3: View tasks in event view
        url = reverse("common:event_tasks", kwargs={"event_id": event.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Step 4: Complete tasks
        for task in tasks:
            task.teams.add(self.team)
            task.status = StaffTask.STATUS_COMPLETED
            task.progress = 100
            task.save()

        # Verify all completed
        completed = StaffTask.objects.filter(
            linked_event=event, status=StaffTask.STATUS_COMPLETED
        ).count()
        self.assertEqual(completed, 2)


class PolicyTaskWorkflowIntegrationTests(TestCase):
    """Test complete workflow for policy development tasks."""

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

        # Create policy template
        self.template = TaskTemplate.objects.create(
            name="policy_development_full_cycle",
            domain=StaffTask.DOMAIN_POLICY,
            description="Full policy development cycle",
            is_active=True,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Research: {policy_title}",
            description="Conduct background research",
            sequence=1,
            days_from_start=0,
            priority=StaffTask.PRIORITY_HIGH,
            policy_phase=StaffTask.POLICY_PHASE_EVIDENCE,
            estimated_hours=8,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Draft: {policy_title}",
            description="Draft policy document",
            sequence=2,
            days_from_start=14,
            priority=StaffTask.PRIORITY_HIGH,
            policy_phase=StaffTask.POLICY_PHASE_DRAFTING,
            estimated_hours=12,
        )

        TaskTemplateItem.objects.create(
            template=self.template,
            title="Consultation: {policy_title}",
            description="Stakeholder consultation",
            sequence=3,
            days_from_start=28,
            priority=StaffTask.PRIORITY_MEDIUM,
            policy_phase=StaffTask.POLICY_PHASE_CONSULTATION,
            estimated_hours=6,
        )

        self.team = StaffTeam.objects.create(name="Policy Team")

    def test_policy_development_workflow(self):
        """Test complete policy development workflow."""
        # Step 1: Create policy
        policy = create_policy_recommendation(
            proposed_by=self.admin,
            title="Education Subsidy Policy",
            status="draft",
        )

        # Step 2: Verify tasks created in phases
        tasks = StaffTask.objects.filter(related_policy=policy).order_by("due_date")
        self.assertEqual(tasks.count(), 3)

        # Step 3: View in policy-specific view
        url = reverse("common:policy_tasks", kwargs={"policy_id": policy.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verify phase grouping
        tasks_by_phase = response.context["tasks_by_phase"]
        self.assertIn("evidence_collection", tasks_by_phase)
        self.assertIn("drafting", tasks_by_phase)
        self.assertIn("consultation", tasks_by_phase)

        # Step 4: Progress through phases
        research_task = tasks[0]
        research_task.teams.add(self.team)
        research_task.status = StaffTask.STATUS_COMPLETED
        research_task.progress = 100
        research_task.save()

        # Update policy status
        policy.status = "drafting"
        policy.save()

        drafting_task = tasks[1]
        drafting_task.status = StaffTask.STATUS_IN_PROGRESS
        drafting_task.progress = 60
        drafting_task.save()

        # Step 5: Verify progress in analytics
        analytics_url = reverse("common:task_analytics")
        response = self.client.get(analytics_url, {"domain": "policy"})
        self.assertEqual(response.status_code, 200)


class TemplateInstantiationWorkflowTests(TestCase):
    """Test template instantiation workflow."""

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

        # Create template
        self.template = TaskTemplate.objects.create(
            name="quick_project",
            domain=StaffTask.DOMAIN_GENERAL,
            description="Quick project setup",
            is_active=True,
        )

        for i in range(5):
            TaskTemplateItem.objects.create(
                template=self.template,
                title=f"Project Task {i+1}",
                description=f"Complete task {i+1}",
                sequence=i + 1,
                days_from_start=i * 3,
                priority=StaffTask.PRIORITY_MEDIUM,
                estimated_hours=4,
            )

        self.team = StaffTeam.objects.create(name="Project Team")

    def test_template_browse_and_instantiate_workflow(self):
        """Test browsing templates and instantiating them."""
        # Step 1: Browse template list
        list_url = reverse("common:task_template_list")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)

        templates = list(response.context["templates"])
        self.assertIn(self.template, templates)

        # Step 2: View template details
        detail_url = reverse(
            "common:task_template_detail", kwargs={"template_id": self.template.pk}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

        items = list(response.context["items"])
        self.assertEqual(len(items), 5)

        # Step 3: Instantiate template
        initial_count = StaffTask.objects.count()

        instantiate_url = reverse(
            "common:instantiate_template",
            kwargs={"template_id": self.template.id},
        )
        response = self.client.post(
            instantiate_url,
            {
                "context": json.dumps({"start_date": date.today().isoformat()}),
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        # Step 4: Verify tasks created
        self.assertEqual(StaffTask.objects.count(), initial_count + 5)

        created_tasks = StaffTask.objects.filter(
            created_from_template=self.template
        ).order_by("due_date")

        # Step 5: Verify due dates calculated correctly
        start = date.today()
        for i, task in enumerate(created_tasks):
            expected_due = start + timedelta(days=i * 3)
            self.assertEqual(task.due_date, expected_due)

        # Step 6: Assign and complete tasks
        for task in created_tasks:
            task.teams.add(self.team)
            task.status = StaffTask.STATUS_COMPLETED
            task.progress = 100
            task.save()

        # Step 7: Verify all completed
        completed_count = StaffTask.objects.filter(
            created_from_template=self.template, status=StaffTask.STATUS_COMPLETED
        ).count()
        self.assertEqual(completed_count, 5)


class TaskBoardKanbanWorkflowTests(TestCase):
    """Test kanban board drag-and-drop workflow."""

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

        self.team = StaffTeam.objects.create(name="Kanban Team")

        # Create tasks in different statuses
        self.task1 = StaffTask.objects.create(
            title="Task 1",
            status=StaffTask.STATUS_NOT_STARTED,
            created_by=self.admin,
        )
        self.task1.teams.add(self.team)

        self.task2 = StaffTask.objects.create(
            title="Task 2",
            status=StaffTask.STATUS_NOT_STARTED,
            created_by=self.admin,
        )
        self.task2.teams.add(self.team)

    def test_kanban_drag_and_drop_workflow(self):
        """Test moving tasks between kanban columns."""
        board_url = reverse("common:staff_task_board")

        # Step 1: View board
        response = self.client.get(board_url)
        self.assertEqual(response.status_code, 200)

        # Step 2: Move task from not_started to in_progress
        update_url = reverse("common:staff_task_update")
        response = self.client.post(
            update_url,
            data='{"task_id": %d, "group": "status", "value": "%s", "order": [%d]}'
            % (self.task1.id, StaffTask.STATUS_IN_PROGRESS, self.task1.id),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, StaffTask.STATUS_IN_PROGRESS)

        # Step 3: Move task to completed
        response = self.client.post(
            update_url,
            data='{"task_id": %d, "group": "status", "value": "%s", "order": [%d]}'
            % (self.task1.id, StaffTask.STATUS_COMPLETED, self.task1.id),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, StaffTask.STATUS_COMPLETED)
        self.assertEqual(self.task1.progress, 100)
        self.assertIsNotNone(self.task1.completed_at)


class MultiDomainAnalyticsWorkflowTests(TestCase):
    """Test analytics across multiple domains."""

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

        # Create tasks across all domains
        domains = [
            StaffTask.DOMAIN_MANA,
            StaffTask.DOMAIN_COORDINATION,
            StaffTask.DOMAIN_POLICY,
            StaffTask.DOMAIN_MONITORING,
            StaffTask.DOMAIN_SERVICES,
        ]

        for i, domain in enumerate(domains):
            for j in range(3):
                status = [
                    StaffTask.STATUS_COMPLETED,
                    StaffTask.STATUS_IN_PROGRESS,
                    StaffTask.STATUS_NOT_STARTED,
                ][j]

                task = StaffTask.objects.create(
                    title=f"{domain} task {j}",
                    domain=domain,
                    status=status,
                    priority=(
                        StaffTask.PRIORITY_HIGH if j == 0 else StaffTask.PRIORITY_MEDIUM
                    ),
                    estimated_hours=4,
                    created_by=self.admin,
                )
                task.teams.add(self.team)

    def test_comprehensive_analytics_workflow(self):
        """Test comprehensive analytics across all domains."""
        url = reverse("common:task_analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # Verify domain breakdown
        domain_data = response.context["domain_data"]
        self.assertEqual(len(domain_data), 5)

        # Each domain should have 3 tasks
        for domain_info in domain_data:
            self.assertEqual(domain_info["count"], 3)

        # Verify overall stats
        stats = response.context["stats"]
        self.assertEqual(stats["total_tasks"], 15)
        self.assertEqual(stats["completed_tasks"], 5)

        # Verify priority distribution
        priority_data = response.context["priority_data"]
        self.assertGreater(len(priority_data), 0)
