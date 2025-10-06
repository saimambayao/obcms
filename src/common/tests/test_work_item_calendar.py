"""
WorkItem Calendar Integration Tests

Tests for calendar feed and integration (Phase 5 - Testing).

Test Coverage:
- work_items_calendar_feed returns correct JSON
- Hierarchy metadata included (level, parentId)
- Breadcrumbs generated correctly
- Type filtering works
- Date range filtering works
- Modal opens with correct data
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
class TestWorkItemCalendarFeed:
    """Test calendar JSON feed."""

    def test_calendar_feed_accessible(self, client):
        """Test calendar feed is accessible."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        response = client.get(reverse("work_items_calendar_feed"))
        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

    def test_calendar_feed_returns_events(self, client):
        """Test calendar feed returns work items as events."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Calendar Task",
            start_date=date(2025, 10, 15),
            due_date=date(2025, 10, 20),
            calendar_color="#F59E0B",
        )

        response = client.get(reverse("work_items_calendar_feed"))
        data = json.loads(response.content)

        assert len(data) == 1
        event = data[0]
        assert event["id"] == str(work_item.id)
        assert event["title"] == "Calendar Task"
        assert event["start"] == "2025-10-15"
        assert event["end"] == "2025-10-20"
        assert event["backgroundColor"] == "#F59E0B"

    def test_calendar_feed_includes_hierarchy_metadata(self, client):
        """Test that hierarchy metadata is included."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Main Project",
            start_date=date.today(),
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Workshop",
            parent=project,
            start_date=date.today(),
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            parent=activity,
            start_date=date.today(),
        )

        response = client.get(reverse("work_items_calendar_feed"))
        data = json.loads(response.content)

        # Find the task event
        task_event = next(e for e in data if e["title"] == "Task")

        # Check hierarchy metadata
        assert "extendedProps" in task_event
        assert task_event["extendedProps"]["workType"] == "task"
        assert "parentId" in task_event["extendedProps"]
        assert task_event["extendedProps"]["parentId"] == str(activity.id)

    def test_calendar_feed_generates_breadcrumbs(self, client):
        """Test breadcrumb generation in calendar events."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project Alpha",
            start_date=date.today(),
        )

        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Workshop Beta",
            parent=project,
            start_date=date.today(),
        )

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task Gamma",
            parent=activity,
            start_date=date.today(),
        )

        response = client.get(reverse("work_items_calendar_feed"))
        data = json.loads(response.content)

        task_event = next(e for e in data if e["title"] == "Task Gamma")

        # Check breadcrumb
        assert "breadcrumb" in task_event["extendedProps"]
        breadcrumb = task_event["extendedProps"]["breadcrumb"]
        assert "Project Alpha" in breadcrumb
        assert "Workshop Beta" in breadcrumb
        assert "Task Gamma" in breadcrumb


@pytest.mark.django_db
class TestWorkItemCalendarFiltering:
    """Test calendar feed filtering."""

    def test_filter_by_work_type(self, client):
        """Test filtering calendar by work type."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            start_date=date.today(),
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            start_date=date.today(),
        )

        # Filter for tasks only
        response = client.get(
            reverse("work_items_calendar_feed"),
            {"work_type": WorkItem.WORK_TYPE_TASK},
        )
        data = json.loads(response.content)

        assert len(data) == 1
        assert data[0]["title"] == "Task"

    def test_filter_by_date_range(self, client):
        """Test filtering calendar by date range."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        # Item within range
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Within Range",
            start_date=date(2025, 10, 15),
        )

        # Item outside range
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Outside Range",
            start_date=date(2025, 12, 1),
        )

        response = client.get(
            reverse("work_items_calendar_feed"),
            {
                "start": "2025-10-01",
                "end": "2025-10-31",
            },
        )
        data = json.loads(response.content)

        assert len(data) == 1
        assert data[0]["title"] == "Within Range"

    def test_filter_by_status(self, client):
        """Test filtering by status."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Completed",
            status=WorkItem.STATUS_COMPLETED,
            start_date=date.today(),
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="In Progress",
            status=WorkItem.STATUS_IN_PROGRESS,
            start_date=date.today(),
        )

        response = client.get(
            reverse("work_items_calendar_feed"),
            {"status": WorkItem.STATUS_IN_PROGRESS},
        )
        data = json.loads(response.content)

        assert len(data) == 1
        assert data[0]["title"] == "In Progress"

    def test_filter_by_assignee(self, client):
        """Test filtering by assignee."""
        user1 = User.objects.create_user(username="user1", password="pass")
        user2 = User.objects.create_user(username="user2", password="pass")
        client.login(username="user1", password="pass")

        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="User 1 Task",
            start_date=date.today(),
        )
        task1.assignees.add(user1)

        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="User 2 Task",
            start_date=date.today(),
        )
        task2.assignees.add(user2)

        response = client.get(
            reverse("work_items_calendar_feed"),
            {"assignee": user1.id},
        )
        data = json.loads(response.content)

        assert len(data) == 1
        assert data[0]["title"] == "User 1 Task"


@pytest.mark.django_db
class TestWorkItemCalendarModal:
    """Test calendar modal/detail view."""

    def test_calendar_modal_shows_details(self, client):
        """Test modal view shows work item details."""
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
            title="Task Details",
            description="Detailed description",
            status=WorkItem.STATUS_IN_PROGRESS,
            priority=WorkItem.PRIORITY_HIGH,
            progress=60,
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
        )
        work_item.assignees.add(user)
        work_item.teams.add(team)

        response = client.get(
            reverse("work_item_calendar_modal", args=[work_item.pk])
        )

        assert response.status_code == 200
        content = response.content.decode()

        assert "Task Details" in content
        assert "Detailed description" in content
        assert "In Progress" in content
        assert "High" in content
        assert "60%" in content
        assert "John Doe" in content
        assert "Test Team" in content


@pytest.mark.django_db
class TestWorkItemCalendarColors:
    """Test calendar color coding."""

    def test_status_based_colors(self, client):
        """Test that status affects border color."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        completed_task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Completed",
            status=WorkItem.STATUS_COMPLETED,
            start_date=date.today(),
        )

        at_risk_task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="At Risk",
            status=WorkItem.STATUS_AT_RISK,
            start_date=date.today(),
        )

        response = client.get(reverse("work_items_calendar_feed"))
        data = json.loads(response.content)

        completed_event = next(e for e in data if e["title"] == "Completed")
        at_risk_event = next(e for e in data if e["title"] == "At Risk")

        # Completed should have green border
        assert completed_event["borderColor"] == "#10B981"

        # At Risk should have amber border
        assert at_risk_event["borderColor"] == "#F59E0B"

    def test_custom_calendar_colors(self, client):
        """Test custom calendar colors."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Custom Color Project",
            start_date=date.today(),
            calendar_color="#8B5CF6",  # Purple
        )

        response = client.get(reverse("work_items_calendar_feed"))
        data = json.loads(response.content)

        assert data[0]["backgroundColor"] == "#8B5CF6"


@pytest.mark.django_db
class TestWorkItemCalendarIntegration:
    """Test full calendar integration."""

    def test_calendar_page_loads(self, client):
        """Test calendar page renders."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        response = client.get(reverse("work_items_calendar"))
        assert response.status_code == 200
        assert "FullCalendar" in response.content.decode() or "calendar" in response.content.decode()

    def test_calendar_displays_multiple_types(self, client):
        """Test calendar shows different work item types."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            start_date=date.today(),
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity",
            start_date=date.today(),
        )

        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task",
            start_date=date.today(),
        )

        response = client.get(reverse("work_items_calendar_feed"))
        data = json.loads(response.content)

        assert len(data) == 3
        work_types = [e["extendedProps"]["workType"] for e in data]
        assert "project" in work_types
        assert "activity" in work_types
        assert "task" in work_types

    def test_calendar_updates_on_drag_drop(self, client):
        """Test calendar date update on drag-drop."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Draggable Task",
            start_date=date(2025, 10, 15),
            due_date=date(2025, 10, 20),
        )

        # Simulate drag-drop update
        new_start = date(2025, 10, 20)
        new_end = date(2025, 10, 25)

        response = client.post(
            reverse("work_item_update_dates", args=[task.pk]),
            {
                "start_date": new_start.isoformat(),
                "due_date": new_end.isoformat(),
            },
        )

        assert response.status_code == 200
        task.refresh_from_db()
        assert task.start_date == new_start
        assert task.due_date == new_end


# Note: URL configuration required
# urlpatterns = [
#     path('calendar/', work_items_calendar, name='work_items_calendar'),
#     path('calendar/feed/', work_items_calendar_feed, name='work_items_calendar_feed'),
#     path('calendar/<uuid:pk>/modal/', work_item_calendar_modal, name='work_item_calendar_modal'),
#     path('calendar/<uuid:pk>/update-dates/', work_item_update_dates, name='work_item_update_dates'),
# ]
