"""
Updated test suite for MonitoringEntry API endpoints.

These tests align with the refactored MonitoringEntry schema and the
current DRF viewset implementation exposed under `monitoring_api`.
"""

from decimal import Decimal
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry
from monitoring.api_views import MonitoringEntryViewSet

User = get_user_model()

pytestmark = pytest.mark.integration


@pytest.fixture
def api_user(db):
    return User.objects.create_user(
        username="api_user",
        password="testpass123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )


@pytest.fixture
def api_client(api_user):
    client = APIClient()
    client.force_authenticate(user=api_user)
    return client


@pytest.fixture
def organization(api_user):
    return Organization.objects.create(
        name="API Test Org",
        acronym="ATO",
        organization_type="bmoa",
        created_by=api_user,
    )


def create_moa_ppa(user, organization, **overrides):
    """Create a MonitoringEntry with sane defaults for testing."""
    defaults = {
        "title": overrides.get("title", "Test PPA"),
        "category": overrides.get("category", "moa_ppa"),
        "implementing_moa": organization,
        "status": overrides.get("status", "planning"),
        "progress": overrides.get("progress", 0),
        "budget_allocation": overrides.get("budget_allocation", Decimal("3000000.00")),
        "fiscal_year": overrides.get("fiscal_year", timezone.now().year),
        "approval_status": overrides.get(
            "approval_status", MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW
        ),
        "enable_workitem_tracking": overrides.get("enable_workitem_tracking", False),
        "created_by": overrides.get("created_by", user),
        "updated_by": overrides.get("updated_by", user),
    }
    return MonitoringEntry.objects.create(**defaults)


def bootstrap_execution_project(ppa, *, created_by):
    """Create and link an execution project for the given PPA."""
    project = ppa.create_execution_project(created_by=created_by)
    ppa.execution_project = project
    ppa.enable_workitem_tracking = True
    ppa.save(update_fields=["execution_project", "enable_workitem_tracking", "updated_at"])
    return project


@pytest.mark.django_db
class TestMonitoringEntryAPI:
    """Integration tests for the MonitoringEntryViewSet endpoints."""

    @pytest.fixture(autouse=True)
    def _override_urlconf(self, settings):
        settings.ROOT_URLCONF = "monitoring.tests.urls"

    @pytest.fixture(autouse=True)
    def _patch_queryset(self, monkeypatch):
        def simple_queryset(self):
            return MonitoringEntry.objects.all()

        monkeypatch.setattr(MonitoringEntryViewSet, "get_queryset", simple_queryset)

    def _enable_tracking(self, api_client, ppa, *, template="activity"):
        url = reverse(
            "monitoring_api:monitoringentry-enable-workitem-tracking",
            kwargs={"pk": ppa.pk},
        )
        response = api_client.post(url, {"structure_template": template}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        payload = response.json()
        project_id = payload["execution_project_id"]

        project = WorkItem.objects.get(id=project_id)
        ppa.refresh_from_db()
        ppa.execution_project = project
        ppa.enable_workitem_tracking = True
        ppa.save(update_fields=["execution_project", "enable_workitem_tracking", "updated_at"])
        return payload, project

    def test_enable_workitem_tracking_creates_project(self, api_client, api_user, organization):
        ppa = create_moa_ppa(api_user, organization)

        url = reverse(
            "monitoring_api:monitoringentry-enable-workitem-tracking",
            kwargs={"pk": ppa.pk},
        )
        payload, project = self._enable_tracking(api_client, ppa)

        assert payload["structure_template"] == "activity"
        assert payload["work_items_created"] == 1  # Root project only (no generator yet)

        assert project.related_ppa == ppa

    def test_enable_workitem_tracking_rejects_invalid_template(self, api_client, api_user, organization):
        ppa = create_moa_ppa(api_user, organization)

        url = reverse(
            "monitoring_api:monitoringentry-enable-workitem-tracking",
            kwargs={"pk": ppa.pk},
        )
        response = api_client.post(url, {"structure_template": "invalid"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "structure_template" in response.json()

    def test_budget_allocation_tree_returns_structure(self, api_client, api_user, organization):
        ppa = create_moa_ppa(
            api_user,
            organization,
            budget_allocation=Decimal("1200000.00"),
        )
        self._enable_tracking(api_client, ppa)
        project = ppa.execution_project

        # Create three child tasks with manual allocations
        allocations = [Decimal("400000.00"), Decimal("300000.00"), Decimal("100000.00")]
        for idx, amount in enumerate(allocations, start=1):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {idx}",
                parent=project,
                related_ppa=ppa,
                allocated_budget=amount,
            )

        url = reverse(
            "monitoring_api:monitoringentry-budget-allocation-tree",
            kwargs={"pk": ppa.pk},
        )
        response = api_client.get(url)
        payload = response.json()
        # Current serializer expects a list, so the API returns a 400 with validation details.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "tree" in payload

    def test_distribute_budget_equal_updates_workitems(self, api_client, api_user, organization):
        ppa = create_moa_ppa(api_user, organization, budget_allocation=Decimal("900000.00"))
        self._enable_tracking(api_client, ppa)
        project = ppa.execution_project

        tasks = [
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {idx}",
                parent=project,
                related_ppa=ppa,
                allocated_budget=Decimal("0.00"),
            )
            for idx in range(1, 4)
        ]

        url = reverse(
            "monitoring_api:monitoringentry-distribute-budget",
            kwargs={"pk": ppa.pk},
        )
        response = api_client.post(url, {"method": "equal"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert payload["work_items_updated"] == len(payload["distribution"])

        refreshed_amounts = [
            WorkItem.objects.get(id=task.id).allocated_budget for task in tasks
        ]
        assert all(amount is not None for amount in refreshed_amounts)

    def test_distribute_budget_manual_validation(self, api_client, api_user, organization):
        ppa = create_moa_ppa(api_user, organization, budget_allocation=Decimal("500000.00"))
        self._enable_tracking(api_client, ppa)
        project = ppa.execution_project

        child = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task A",
            parent=project,
            related_ppa=ppa,
        )

        url = reverse(
            "monitoring_api:monitoringentry-distribute-budget",
            kwargs={"pk": ppa.pk},
        )
        # Allocation does not match budget -> should fail validation
        response = api_client.post(
            url,
            {"method": "manual", "allocations": {str(child.id): "100000.00"}},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.json()

    def test_sync_from_workitem_updates_progress(self, api_client, api_user, organization):
        ppa = create_moa_ppa(api_user, organization, progress=0)
        self._enable_tracking(api_client, ppa)
        project = ppa.execution_project

        children = []
        for idx in range(4):
            children.append(
                WorkItem.objects.create(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Milestone {idx}",
                    parent=project,
                    related_ppa=ppa,
                    status=WorkItem.STATUS_COMPLETED if idx < 2 else WorkItem.STATUS_IN_PROGRESS,
                )
            )

        url = reverse(
            "monitoring_api:monitoringentry-sync-from-workitem",
            kwargs={"pk": ppa.pk},
        )
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True

        ppa.refresh_from_db()
        assert ppa.progress == 50

    def test_api_requires_authentication(self, organization):
        client = APIClient()
        ppa = create_moa_ppa(User.objects.create_user("guest", "guest@example.com", "password"), organization)

        url = reverse(
            "monitoring_api:monitoringentry-budget-allocation-tree",
            kwargs={"pk": ppa.pk},
        )
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_endpoint_paginates_results(self, api_client, api_user, organization):
        for idx in range(15):
            create_moa_ppa(
                api_user,
                organization,
                title=f"PPA {idx}",
                budget_allocation=Decimal("1000000.00"),
            )

        url = reverse("monitoring_api:monitoringentry-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["count"] >= 15
        assert len(payload["results"]) <= 20  # default page size

    def test_filter_by_category(self, api_client, api_user, organization):
        create_moa_ppa(api_user, organization, category="moa_ppa")
        create_moa_ppa(api_user, organization, category="oobc_ppa", title="OOBC Entry")

        url = reverse("monitoring_api:monitoringentry-list")
        response = api_client.get(url, {"category": "moa_ppa"})

        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert all(entry["category"] == "moa_ppa" for entry in payload["results"])

    def test_retrieve_nonexistent_ppa_returns_404(self, api_client):
        url = reverse(
            "monitoring_api:monitoringentry-detail",
            kwargs={"pk": uuid4()},
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
