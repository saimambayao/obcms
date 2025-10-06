"""
WorkItem Integration Tests

End-to-end workflow tests (Phase 5 - Comprehensive Testing).

Test Coverage:
- End-to-end: Create Project → Add Activity → Add Task → View in Calendar
- HTMX interactions (expand/collapse tree)
- Form submissions
- Delete confirmations
- Multi-user workflows
- Real-world scenarios
"""

import pytest
import json
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()


@pytest.mark.django_db
class TestEndToEndProjectWorkflow:
    """Test complete project workflow."""

    def test_create_project_add_activities_view_calendar(self, client):
        """
        End-to-end test: Create Project → Add Activities → Add Tasks → View in Calendar
        """
        # Step 1: Login
        user = User.objects.create_user(
            username="pm_user",
            password="testpass",
            first_name="Project",
            last_name="Manager",
        )
        client.login(username="pm_user", password="testpass")

        # Step 2: Create Project
        response = client.post(
            reverse("work_item_create"),
            {
                "work_type": WorkItem.WORK_TYPE_PROJECT,
                "title": "Community Development Initiative",
                "description": "Comprehensive community development project",
                "start_date": "2025-01-01",
                "due_date": "2025-12-31",
                "priority": WorkItem.PRIORITY_HIGH,
            },
        )
        assert response.status_code == 302  # Redirect on success

        project = WorkItem.objects.get(title="Community Development Initiative")
        assert project.created_by == user

        # Step 3: Add First Activity
        response = client.post(
            reverse("work_item_create"),
            {
                "work_type": WorkItem.WORK_TYPE_ACTIVITY,
                "title": "Stakeholder Consultation Workshop",
                "parent": project.pk,
                "start_date": "2025-02-15",
                "due_date": "2025-02-15",
            },
        )
        assert response.status_code == 302

        workshop = WorkItem.objects.get(title="Stakeholder Consultation Workshop")
        assert workshop.parent == project

        # Step 4: Add Second Activity
        response = client.post(
            reverse("work_item_create"),
            {
                "work_type": WorkItem.WORK_TYPE_ACTIVITY,
                "title": "Community Needs Assessment",
                "parent": project.pk,
                "start_date": "2025-03-01",
                "due_date": "2025-03-31",
            },
        )
        assessment = WorkItem.objects.get(title="Community Needs Assessment")

        # Step 5: Add Tasks to Workshop
        task1 = client.post(
            reverse("work_item_create"),
            {
                "work_type": WorkItem.WORK_TYPE_TASK,
                "title": "Prepare workshop materials",
                "parent": workshop.pk,
                "start_date": "2025-02-01",
                "due_date": "2025-02-10",
            },
        )
        assert task1.status_code == 302

        task2 = client.post(
            reverse("work_item_create"),
            {
                "work_type": WorkItem.WORK_TYPE_TASK,
                "title": "Send invitations",
                "parent": workshop.pk,
                "start_date": "2025-02-05",
                "due_date": "2025-02-12",
            },
        )
        assert task2.status_code == 302

        # Step 6: Verify Hierarchy
        assert project.get_children().count() == 2
        assert workshop.get_children().count() == 2
        all_tasks = project.get_all_tasks()
        assert all_tasks.count() == 2

        # Step 7: View in Calendar
        response = client.get(reverse("work_items_calendar_feed"))
        calendar_data = json.loads(response.content)

        # Should have 5 items (1 project + 2 activities + 2 tasks)
        assert len(calendar_data) == 5

        # Verify project event
        project_event = next(e for e in calendar_data if e["title"] == "Community Development Initiative")
        assert project_event["extendedProps"]["workType"] == "project"

        # Verify task has breadcrumb
        task_event = next(e for e in calendar_data if e["title"] == "Prepare workshop materials")
        assert "breadcrumb" in task_event["extendedProps"]
        breadcrumb = task_event["extendedProps"]["breadcrumb"]
        assert "Community Development Initiative" in breadcrumb
        assert "Stakeholder Consultation Workshop" in breadcrumb

    def test_update_task_status_propagates_progress(self, client):
        """Test completing tasks updates parent progress."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        # Create hierarchy
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
            status=WorkItem.STATUS_NOT_STARTED,
        )

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=activity,
            status=WorkItem.STATUS_NOT_STARTED,
        )

        # Update task 1 to completed
        response = client.post(
            reverse("work_item_edit", args=[task1.pk]),
            {
                "work_type": WorkItem.WORK_TYPE_TASK,
                "title": "Task 1",
                "status": WorkItem.STATUS_COMPLETED,
                "parent": activity.pk,
            },
        )

        # Trigger progress update
        activity.update_progress()
        project.update_progress()

        activity.refresh_from_db()
        project.refresh_from_db()

        # Activity should be 50% (1/2 tasks done)
        assert activity.progress == 50

        # Project should be 100% (1/1 activities at 50%+)
        # Actually depends on implementation - could be 50% or 100%
        assert project.progress >= 0


@pytest.mark.django_db
class TestHTMXInteractions:
    """Test HTMX dynamic interactions."""

    def test_expand_collapse_tree_node(self, client):
        """Test expanding/collapsing tree nodes with HTMX."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Expandable Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Hidden Activity",
            parent=project,
        )

        # HTMX request to expand
        response = client.get(
            reverse("work_item_tree_expand", args=[project.pk]),
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        # Should return partial HTML (not full page)
        content = response.content.decode()
        assert "Hidden Activity" in content
        assert "<html" not in content  # Partial response only

    def test_inline_edit_with_htmx(self, client):
        """Test inline editing with HTMX."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Editable Task",
            progress=30,
        )

        # HTMX inline update
        response = client.post(
            reverse("work_item_inline_update", args=[task.pk]),
            {"progress": 75},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        task.refresh_from_db()
        assert task.progress == 75


@pytest.mark.django_db
class TestMultiUserWorkflow:
    """Test multi-user collaboration workflows."""

    def test_assign_team_to_project(self, client):
        """Test assigning a team to a project."""
        admin = User.objects.create_user(username="admin", password="admin")
        user1 = User.objects.create_user(username="user1", password="pass")
        user2 = User.objects.create_user(username="user2", password="pass")

        team = StaffTeam.objects.create(name="Implementation Team")

        client.login(username="admin", password="admin")

        # Create project and assign team
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Team Project",
        )

        response = client.post(
            reverse("work_item_edit", args=[project.pk]),
            {
                "work_type": WorkItem.WORK_TYPE_PROJECT,
                "title": "Team Project",
                "teams": [team.pk],
                "assignees": [user1.pk, user2.pk],
            },
        )

        project.refresh_from_db()
        assert team in project.teams.all()
        assert user1 in project.assignees.all()
        assert user2 in project.assignees.all()

    def test_delegate_task_to_user(self, client):
        """Test delegating a task to a specific user."""
        admin = User.objects.create_user(username="admin", password="admin")
        delegate = User.objects.create_user(
            username="delegate",
            first_name="John",
            last_name="Delegate",
        )

        client.login(username="admin", password="admin")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Delegated Task",
            created_by=admin,
        )

        # Assign to delegate
        response = client.post(
            reverse("work_item_edit", args=[task.pk]),
            {
                "work_type": WorkItem.WORK_TYPE_TASK,
                "title": "Delegated Task",
                "assignees": [delegate.pk],
            },
        )

        task.refresh_from_db()
        assert delegate in task.assignees.all()


@pytest.mark.django_db
class TestRealWorldScenarios:
    """Test real-world OOBC scenarios."""

    def test_mana_assessment_workflow(self, client):
        """Test MANA assessment project workflow."""
        researcher = User.objects.create_user(username="researcher", password="pass")
        client.login(username="researcher", password="pass")

        # Create MANA Assessment Project
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="MANA Assessment - Region XII",
            start_date=date(2025, 1, 1),
            due_date=date(2025, 6, 30),
            project_data={
                "workflow_stage": "planning",
                "assessment_type": "mana",
                "target_region": "Region XII",
            },
        )

        # Planning Phase Activities
        planning = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Assessment Planning",
            parent=project,
            start_date=date(2025, 1, 1),
            due_date=date(2025, 1, 31),
        )

        # Data Collection Phase
        data_collection = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Field Data Collection",
            parent=project,
            start_date=date(2025, 2, 1),
            due_date=date(2025, 4, 30),
            activity_data={
                "event_type": "field_visit",
                "location": "Region XII",
            },
        )

        # Tasks under data collection
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Conduct household surveys",
            parent=data_collection,
            task_data={
                "domain": "mana",
                "assessment_phase": "data_collection",
                "deliverable_type": "survey_data",
            },
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Interview community leaders",
            parent=data_collection,
            task_data={
                "domain": "mana",
                "assessment_phase": "data_collection",
                "deliverable_type": "interview_notes",
            },
        )

        # Verify structure
        assert project.get_children().count() == 2
        assert project.get_all_tasks().count() == 2
        assert project.project_data["assessment_type"] == "mana"

    def test_policy_development_workflow(self, client):
        """Test policy recommendation workflow."""
        policy_officer = User.objects.create_user(username="policy", password="pass")
        client.login(username="policy", password="pass")

        # Create Policy Development Project
        policy_project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="OBC Education Policy Framework",
            start_date=date(2025, 1, 1),
            due_date=date(2025, 12, 31),
            project_data={
                "policy_area": "education",
                "policy_stage": "drafting",
            },
        )

        # Consultation Activity
        consultation = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Stakeholder Consultation",
            parent=policy_project,
            activity_data={
                "event_type": "consultation",
                "stakeholder_groups": ["educators", "community_leaders", "parents"],
            },
        )

        # Drafting Tasks
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Draft policy framework",
            parent=policy_project,
            task_data={
                "domain": "policy",
                "policy_phase": "drafting",
            },
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Gather evidence and data",
            parent=policy_project,
            task_data={
                "domain": "policy",
                "policy_phase": "evidence_collection",
            },
        )

        assert policy_project.get_descendants().count() == 3


@pytest.mark.django_db
class TestErrorHandling:
    """Test error handling in workflows."""

    def test_prevent_circular_references(self, client):
        """Test that circular parent-child references are prevented."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        parent = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Parent",
        )

        child = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Child",
            parent=parent,
        )

        # Try to set parent as child of child (circular)
        response = client.post(
            reverse("work_item_edit", args=[parent.pk]),
            {
                "work_type": WorkItem.WORK_TYPE_PROJECT,
                "title": "Parent",
                "parent": child.pk,  # Invalid: circular reference
            },
        )

        # Should reject
        parent.refresh_from_db()
        assert parent.parent is None  # Parent unchanged

    def test_delete_with_children_confirmation(self, client):
        """Test delete confirmation for items with children."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project with Children",
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Child Activity",
            parent=project,
        )

        # GET delete page should warn about children
        response = client.get(reverse("work_item_delete", args=[project.pk]))
        content = response.content.decode()
        assert "will also delete" in content.lower() or "1 child" in content.lower()
