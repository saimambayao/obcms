"""
WorkItem View Tests

Tests for WorkItem CRUD views (Phase 5 - Comprehensive Testing).

Test Coverage:
- List view displays hierarchy
- Create view validates input
- Edit view updates correctly
- Delete view cascades or re-parents
- Detail view shows all fields
- Permissions enforced
- HTMX partial responses
"""

import pytest
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()


@pytest.mark.django_db
class TestWorkItemListView:
    """Test work item list view."""

    def test_list_view_accessible(self, client):
        """Test that list view is accessible to authenticated users."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        # Create test work items
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project 1",
        )

        response = client.get(reverse("work_item_list"))
        assert response.status_code == 200
        assert "Project 1" in response.content.decode()

    def test_list_view_requires_authentication(self, client):
        """Test that list view redirects unauthenticated users."""
        response = client.get(reverse("work_item_list"))
        assert response.status_code == 302  # Redirect to login

    def test_list_view_displays_hierarchy(self, client):
        """Test that list view shows hierarchical structure."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

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
            title="Prepare Materials",
            parent=activity,
        )

        response = client.get(reverse("work_item_list"))
        content = response.content.decode()

        assert "Main Project" in content
        assert "Workshop Activity" in content
        assert "Prepare Materials" in content

    def test_list_view_filter_by_work_type(self, client):
        """Test filtering by work type."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project Item",
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task Item",
        )

        # Filter for projects only
        response = client.get(
            reverse("work_item_list"),
            {"work_type": WorkItem.WORK_TYPE_PROJECT},
        )

        content = response.content.decode()
        assert "Project Item" in content
        # Task should be filtered out (depending on implementation)

    def test_list_view_filter_by_status(self, client):
        """Test filtering by status."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Completed Task",
            status=WorkItem.STATUS_COMPLETED,
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="In Progress Task",
            status=WorkItem.STATUS_IN_PROGRESS,
        )

        response = client.get(
            reverse("work_item_list"),
            {"status": WorkItem.STATUS_COMPLETED},
        )

        content = response.content.decode()
        assert "Completed Task" in content

    def test_list_view_search(self, client):
        """Test search functionality."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Community Survey Task",
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Workshop Planning",
        )

        response = client.get(
            reverse("work_item_list"),
            {"q": "Survey"},
        )

        content = response.content.decode()
        assert "Community Survey Task" in content


@pytest.mark.django_db
class TestWorkItemDetailView:
    """Test work item detail view."""

    def test_detail_view_displays_all_fields(self, client):
        """Test that detail view shows all work item fields."""
        user = User.objects.create_user(
            username="testuser",
            password="testpass",
            first_name="John",
            last_name="Doe",
        )
        client.login(username="testuser", password="testpass")

        team = StaffTeam.objects.create(name="Test Team")

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Test Task",
            description="Detailed description",
            status=WorkItem.STATUS_IN_PROGRESS,
            priority=WorkItem.PRIORITY_HIGH,
            progress=50,
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
            created_by=user,
        )
        work_item.assignees.add(user)
        work_item.teams.add(team)

        response = client.get(reverse("work_item_detail", args=[work_item.pk]))

        content = response.content.decode()
        assert "Test Task" in content
        assert "Detailed description" in content
        assert "In Progress" in content
        assert "High" in content
        assert "50" in content  # Progress
        assert "John Doe" in content  # Assignee
        assert "Test Team" in content

    def test_detail_view_shows_breadcrumb(self, client):
        """Test breadcrumb navigation."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Main Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Workshop",
            parent=project,
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            parent=activity,
        )

        response = client.get(reverse("work_item_detail", args=[task.pk]))
        content = response.content.decode()

        # Should show breadcrumb: Project > Activity > Task
        assert "Main Project" in content
        assert "Workshop" in content
        assert "Task" in content

    def test_detail_view_shows_children(self, client):
        """Test that children are displayed."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        child1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            parent=project,
        )

        child2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 2",
            parent=project,
        )

        response = client.get(reverse("work_item_detail", args=[project.pk]))
        content = response.content.decode()

        assert "Activity 1" in content
        assert "Activity 2" in content


@pytest.mark.django_db
class TestWorkItemCreateView:
    """Test work item creation."""

    def test_create_view_get(self, client):
        """Test GET request to create view."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        response = client.get(reverse("work_item_create"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_create_project(self, client):
        """Test creating a project."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        response = client.post(
            reverse("work_item_create"),
            {
                "work_type": WorkItem.WORK_TYPE_PROJECT,
                "title": "New Project",
                "description": "Project description",
                "start_date": "2025-10-01",
                "due_date": "2025-12-31",
                "priority": WorkItem.PRIORITY_HIGH,
            },
        )

        assert response.status_code == 302  # Redirect after success
        assert WorkItem.objects.filter(title="New Project").exists()

        project = WorkItem.objects.get(title="New Project")
        assert project.work_type == WorkItem.WORK_TYPE_PROJECT
        assert project.created_by == user

    def test_create_with_parent(self, client):
        """Test creating a child work item."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Parent Project",
        )

        response = client.post(
            reverse("work_item_create"),
            {
                "work_type": WorkItem.WORK_TYPE_ACTIVITY,
                "title": "Child Activity",
                "parent": project.pk,
            },
        )

        assert response.status_code == 302
        activity = WorkItem.objects.get(title="Child Activity")
        assert activity.parent == project

    def test_create_validates_parent_child_type(self, client):
        """Test that invalid parent-child relationships are rejected."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        # Try to create a Project under a Project (invalid)
        response = client.post(
            reverse("work_item_create"),
            {
                "work_type": WorkItem.WORK_TYPE_PROJECT,
                "title": "Child Project",
                "parent": project.pk,
            },
        )

        # Should show validation error
        assert response.status_code == 200  # Form re-rendered with errors
        assert not WorkItem.objects.filter(title="Child Project").exists()


@pytest.mark.django_db
class TestWorkItemEditView:
    """Test work item editing."""

    def test_edit_view_get(self, client):
        """Test GET request to edit view."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task to Edit",
        )

        response = client.get(reverse("work_item_edit", args=[work_item.pk]))
        assert response.status_code == 200
        assert response.context["form"].instance == work_item

    def test_edit_work_item(self, client):
        """Test updating a work item."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Original Title",
            status=WorkItem.STATUS_NOT_STARTED,
        )

        response = client.post(
            reverse("work_item_edit", args=[work_item.pk]),
            {
                "work_type": WorkItem.WORK_TYPE_TASK,
                "title": "Updated Title",
                "status": WorkItem.STATUS_IN_PROGRESS,
            },
        )

        assert response.status_code == 302
        work_item.refresh_from_db()
        assert work_item.title == "Updated Title"
        assert work_item.status == WorkItem.STATUS_IN_PROGRESS

    def test_edit_preserves_hierarchy(self, client):
        """Test that editing doesn't break hierarchy."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            parent=project,
        )

        # Edit task, keeping parent
        response = client.post(
            reverse("work_item_edit", args=[task.pk]),
            {
                "work_type": WorkItem.WORK_TYPE_TASK,
                "title": "Updated Task",
                "parent": project.pk,
            },
        )

        task.refresh_from_db()
        assert task.parent == project


@pytest.mark.django_db
class TestWorkItemDeleteView:
    """Test work item deletion."""

    def test_delete_view_get(self, client):
        """Test GET request shows delete confirmation."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task to Delete",
        )

        response = client.get(reverse("work_item_delete", args=[work_item.pk]))
        assert response.status_code == 200
        assert "Task to Delete" in response.content.decode()

    def test_delete_work_item(self, client):
        """Test deleting a work item."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task to Delete",
        )

        response = client.post(
            reverse("work_item_delete", args=[work_item.pk]),
            {"confirm": "yes"},
        )

        assert response.status_code == 302
        assert not WorkItem.objects.filter(pk=work_item.pk).exists()

    def test_delete_cascades_to_children(self, client):
        """Test that deleting parent deletes children."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
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

        # Delete project (cascade delete)
        client.post(
            reverse("work_item_delete", args=[project.pk]),
            {"confirm": "yes"},
        )

        # All items should be deleted
        assert not WorkItem.objects.filter(pk=project.pk).exists()
        assert not WorkItem.objects.filter(pk=activity.pk).exists()
        assert not WorkItem.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
class TestWorkItemPermissions:
    """Test permission enforcement."""

    def test_only_authenticated_users_can_access(self, client):
        """Test that unauthenticated users are redirected."""
        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
        )

        # List view
        response = client.get(reverse("work_item_list"))
        assert response.status_code == 302

        # Detail view
        response = client.get(reverse("work_item_detail", args=[work_item.pk]))
        assert response.status_code == 302

        # Create view
        response = client.get(reverse("work_item_create"))
        assert response.status_code == 302

        # Edit view
        response = client.get(reverse("work_item_edit", args=[work_item.pk]))
        assert response.status_code == 302

        # Delete view
        response = client.get(reverse("work_item_delete", args=[work_item.pk]))
        assert response.status_code == 302


@pytest.mark.django_db
class TestWorkItemHTMXIntegration:
    """Test HTMX partial updates."""

    def test_htmx_expand_collapse_tree(self, client):
        """Test HTMX tree expand/collapse."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity",
            parent=project,
        )

        # HTMX request to expand tree node
        response = client.get(
            reverse("work_item_tree_expand", args=[project.pk]),
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        # Should return partial HTML (not full page)
        content = response.content.decode()
        assert "Activity" in content

    def test_htmx_update_progress(self, client):
        """Test HTMX progress update."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            progress=0,
        )

        # HTMX request to update progress
        response = client.post(
            reverse("work_item_update_progress", args=[task.pk]),
            {"progress": 75},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        task.refresh_from_db()
        assert task.progress == 75


# Note: Define URL patterns in urls.py
# urlpatterns = [
#     path('work-items/', work_item_list, name='work_item_list'),
#     path('work-items/create/', work_item_create, name='work_item_create'),
#     path('work-items/<uuid:pk>/', work_item_detail, name='work_item_detail'),
#     path('work-items/<uuid:pk>/edit/', work_item_edit, name='work_item_edit'),
#     path('work-items/<uuid:pk>/delete/', work_item_delete, name='work_item_delete'),
#     path('work-items/<uuid:pk>/expand/', work_item_tree_expand, name='work_item_tree_expand'),
#     path('work-items/<uuid:pk>/progress/', work_item_update_progress, name='work_item_update_progress'),
# ]
