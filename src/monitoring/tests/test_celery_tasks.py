"""Regression tests for monitoring Celery tasks."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

try:
    from django.contrib.auth import get_user_model
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for monitoring Celery task tests",
        allow_module_level=True,
    )

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry
from monitoring.tasks import auto_sync_ppa_progress, detect_budget_variances

User = get_user_model()

pytestmark = pytest.mark.unit


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="celery_staff",
        password="testpass123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def organization(staff_user):
    return Organization.objects.create(
        name="Celery Org",
        acronym="CEL",
        organization_type="bmoa",
        created_by=staff_user,
    )


def create_execution_project(ppa, *, created_by, complete_children=0, total_children=4):
    """Attach an execution project with child work items."""
    project = ppa.create_execution_project(created_by=created_by)
    ppa.execution_project = project
    ppa.enable_workitem_tracking = True
    ppa.save(update_fields=["execution_project", "enable_workitem_tracking", "updated_at"])

    for idx in range(total_children):
        status = (
            WorkItem.STATUS_COMPLETED if idx < complete_children else WorkItem.STATUS_IN_PROGRESS
        )
        WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=f"Task {idx + 1}",
            parent=project,
            related_ppa=ppa,
            status=status,
        )
    return project


@pytest.mark.django_db
def test_auto_sync_ppa_progress_updates_progress(staff_user, organization):
    ppa = MonitoringEntry.objects.create(
        title="Sync PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="ongoing",
        budget_allocation=Decimal("1000000.00"),
        fiscal_year=2025,
        auto_sync_progress=True,
        enable_workitem_tracking=True,
        created_by=staff_user,
        updated_by=staff_user,
    )

    create_execution_project(ppa, created_by=staff_user, complete_children=2, total_children=4)

    with patch("monitoring.utils.email.send_progress_sync_notification") as mock_notify:
        result = auto_sync_ppa_progress.apply(args=[], kwargs={}).get()

    ppa.refresh_from_db()
    assert ppa.progress == 50  # 2 of 4 tasks completed
    assert result["total_processed"] == 1
    assert result["total_updated"] == 1
    mock_notify.assert_called_once()


@pytest.mark.django_db
def test_detect_budget_variances_flags_overspending(monkeypatch, staff_user, organization):
    ppa = MonitoringEntry.objects.create(
        title="Variance PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="ongoing",
        budget_allocation=Decimal("1000000.00"),
        fiscal_year=2025,
        created_by=staff_user,
        updated_by=staff_user,
    )

    # Inject stub for total_actual_disbursed
    monkeypatch.setattr(
        MonitoringEntry,
        "total_actual_disbursed",
        lambda self: Decimal("1250000.00"),
        raising=False,
    )

    # Patch Alert model within task to avoid cross-app dependencies
    with patch("project_central.models.Alert") as mock_alert, patch(
        "monitoring.utils.email.send_budget_variance_alert"
    ) as mock_email:
        mock_alert.objects.filter.return_value.first.return_value = None
        mock_alert.create_alert = MagicMock()

        result = detect_budget_variances.apply(args=[], kwargs={}).get()

    assert result["total_variances"] == 1
    assert result["alerts_created"] == 1
    assert result["emails_sent"] == 1
    mock_alert.create_alert.assert_called_once()
    mock_email.assert_called_once_with(ppa, Decimal("250000.00"), 25.0)
