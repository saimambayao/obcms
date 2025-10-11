"""Signal behaviour tests for MonitoringEntry approval workflow."""

import pytest
from django.contrib.auth import get_user_model

from coordination.models import Organization
from monitoring.models import MonitoringEntry
from monitoring.signals import track_approval_status_change
from common.work_item_model import WorkItem

User = get_user_model()

pytestmark = pytest.mark.unit


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="signal_staff",
        password="testpass123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def organization(staff_user):
    return Organization.objects.create(
        name="Signal Org",
        acronym="SIG",
        organization_type="bmoa",
        created_by=staff_user,
    )


@pytest.mark.django_db
def test_technical_review_auto_creates_execution_project(staff_user, organization):
    entry = MonitoringEntry.objects.create(
        title="Signal Test PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        approval_status=MonitoringEntry.APPROVAL_STATUS_DRAFT,
        enable_workitem_tracking=True,
        budget_distribution_policy="activity",
        created_by=staff_user,
        updated_by=staff_user,
    )

    entry.approval_status = MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW
    entry.reviewed_by = staff_user
    entry.save()

    entry.refresh_from_db()
    assert entry.execution_project is not None
    assert entry.execution_project.related_ppa == entry
    assert entry.execution_project.work_type == WorkItem.WORK_TYPE_PROJECT


@pytest.mark.django_db
def test_enacted_status_activates_execution_project(staff_user, organization):
    entry = MonitoringEntry.objects.create(
        title="Activation Test PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        approval_status=MonitoringEntry.APPROVAL_STATUS_DRAFT,
        enable_workitem_tracking=True,
        budget_distribution_policy="activity",
        created_by=staff_user,
        updated_by=staff_user,
    )

    # Initial save triggers technical_review automation
    entry.approval_status = MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW
    entry.reviewed_by = staff_user
    entry.save()
    entry.refresh_from_db()

    execution_project = entry.execution_project
    assert execution_project is not None
    assert execution_project.status == WorkItem.STATUS_NOT_STARTED

    entry.approval_status = MonitoringEntry.APPROVAL_STATUS_ENACTED
    entry.save()

    entry.refresh_from_db()
    execution_project.refresh_from_db()
    assert execution_project.status == WorkItem.STATUS_IN_PROGRESS


@pytest.mark.django_db
def test_track_approval_status_change_sets_old_status(staff_user, organization):
    entry = MonitoringEntry.objects.create(
        title="Tracking PPA",
        category="moa_ppa",
        implementing_moa=organization,
        status="planning",
        progress=0,
        approval_status=MonitoringEntry.APPROVAL_STATUS_DRAFT,
        enable_workitem_tracking=False,
        created_by=staff_user,
        updated_by=staff_user,
    )

    track_approval_status_change(MonitoringEntry, entry)
    assert getattr(entry, "_old_approval_status", None) == MonitoringEntry.APPROVAL_STATUS_DRAFT

    entry.approval_status = MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW
    track_approval_status_change(MonitoringEntry, entry)
    assert getattr(entry, "_old_approval_status", None) == MonitoringEntry.APPROVAL_STATUS_DRAFT
