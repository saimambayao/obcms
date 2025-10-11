"""Shared fixtures for monitoring integration tests."""

from decimal import Decimal
from typing import Iterable, Optional

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


@pytest.fixture
def staff_user(db):
    """Create a staff user approved for monitoring workflows."""
    return User.objects.create_user(
        username="monitoring_staff",
        password="testpass123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def organization(staff_user):
    """Provision an implementing organization for monitoring entries."""
    return Organization.objects.create(
        name="Integration Test Org",
        acronym="ITO",
        organization_type="bmoa",
        created_by=staff_user,
    )


@pytest.fixture
def monitoring_entry_factory(staff_user, organization):
    """Factory fixture to create MonitoringEntry instances with sane defaults."""

    def factory(**overrides) -> MonitoringEntry:
        defaults = {
            "title": overrides.get("title", "Integration PPA"),
            "category": overrides.get("category", "moa_ppa"),
            "implementing_moa": overrides.get("implementing_moa", organization),
            "status": overrides.get("status", "planning"),
            "priority": overrides.get("priority", "medium"),
            "progress": overrides.get("progress", 0),
            "budget_allocation": overrides.get(
                "budget_allocation", Decimal("1000000.00")
            ),
            "created_by": overrides.get("created_by", staff_user),
            "updated_by": overrides.get("updated_by", staff_user),
        }
        defaults.update(overrides)
        return MonitoringEntry.objects.create(**defaults)

    return factory


@pytest.fixture
def execution_project_builder():
    """Return a helper that creates a project with descendant WorkItems."""

    def builder(
        ppa: MonitoringEntry,
        *,
        created_by,
        statuses: Optional[Iterable[str]] = None,
        completed: int = 1,
        total: int = 3,
    ):
        project = ppa.create_execution_project(created_by=created_by)
        ppa.execution_project = project
        ppa.enable_workitem_tracking = True
        ppa.save(
            update_fields=["execution_project", "enable_workitem_tracking", "updated_at"]
        )

        if statuses is None:
            statuses = [
                WorkItem.STATUS_COMPLETED
                if idx < completed
                else WorkItem.STATUS_IN_PROGRESS
                for idx in range(total)
            ]
        else:
            statuses = list(statuses)

        for idx, status in enumerate(statuses):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {idx + 1}",
                parent=project,
                related_ppa=ppa,
                status=status,
            )

        return project

    return builder


@pytest.fixture
def hx_client(staff_user):
    """Authenticated Django client that automatically sends HTMX headers."""
    client = Client()
    client.force_login(staff_user)
    client.defaults["HTTP_HX_REQUEST"] = "true"
    return client


@pytest.fixture
def celery_eager(settings):
    """Force Celery tasks to run synchronously during a test."""
    previous_eager = getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False)
    previous_propagates = getattr(settings, "CELERY_TASK_EAGER_PROPAGATES", False)

    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

    yield

    settings.CELERY_TASK_ALWAYS_EAGER = previous_eager
    settings.CELERY_TASK_EAGER_PROPAGATES = previous_propagates
