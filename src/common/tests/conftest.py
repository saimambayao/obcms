"""
Pytest Configuration and Shared Fixtures for WorkItem Tests

Provides common fixtures and test utilities for all WorkItem tests.
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.test import Client

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        password="testpass",
        first_name="Test",
        last_name="User",
        email="testuser@oobc.gov.ph",
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_superuser(
        username="admin",
        password="admin",
        email="admin@oobc.gov.ph",
    )


@pytest.fixture
def authenticated_client(client, user):
    """Return authenticated client."""
    client.login(username="testuser", password="testpass")
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Return admin client."""
    client.login(username="admin", password="admin")
    return client


@pytest.fixture
def staff_team():
    """Create a test staff team."""
    return StaffTeam.objects.create(
        name="Test Team",
        description="Team for testing",
        is_active=True,
    )


@pytest.fixture
def sample_project(user):
    """Create a sample project."""
    return WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title="Sample Project",
        description="Sample project for testing",
        start_date=date.today(),
        due_date=date.today() + timedelta(days=90),
        created_by=user,
    )


@pytest.fixture
def sample_activity(sample_project):
    """Create a sample activity under project."""
    return WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_ACTIVITY,
        title="Sample Activity",
        parent=sample_project,
        start_date=date.today(),
        due_date=date.today() + timedelta(days=30),
    )


@pytest.fixture
def sample_task(sample_activity):
    """Create a sample task under activity."""
    return WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="Sample Task",
        parent=sample_activity,
        start_date=date.today(),
        due_date=date.today() + timedelta(days=7),
    )


@pytest.fixture
def project_hierarchy(user):
    """
    Create a complete project hierarchy:
    - 1 Project
    - 2 Activities
    - 4 Tasks (2 per activity)
    """
    project = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title="Hierarchy Project",
        created_by=user,
    )

    activity1 = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_ACTIVITY,
        title="Activity 1",
        parent=project,
    )

    activity2 = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_ACTIVITY,
        title="Activity 2",
        parent=project,
    )

    task1_1 = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="Task 1.1",
        parent=activity1,
    )

    task1_2 = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="Task 1.2",
        parent=activity1,
    )

    task2_1 = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="Task 2.1",
        parent=activity2,
    )

    task2_2 = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title="Task 2.2",
        parent=activity2,
    )

    return {
        "project": project,
        "activities": [activity1, activity2],
        "tasks": [task1_1, task1_2, task2_1, task2_2],
    }


# Helper functions

def create_work_item(**kwargs):
    """Helper to create work items with defaults."""
    defaults = {
        "work_type": WorkItem.WORK_TYPE_TASK,
        "title": "Test Work Item",
        "status": WorkItem.STATUS_NOT_STARTED,
        "priority": WorkItem.PRIORITY_MEDIUM,
    }
    defaults.update(kwargs)
    return WorkItem.objects.create(**defaults)


def assert_work_item_hierarchy(parent, expected_children_count):
    """Assert work item hierarchy structure."""
    assert parent.get_children().count() == expected_children_count


def assert_progress_equals(work_item, expected_progress):
    """Assert work item progress."""
    work_item.refresh_from_db()
    assert work_item.progress == expected_progress
