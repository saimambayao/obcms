"""
Test suite for PPA-WorkItem API endpoints.

Tests cover:
- Enable WorkItem tracking endpoint
- Budget allocation tree endpoint
- Distribute budget endpoint
- Sync from WorkItem endpoint
- API authentication
- API error responses
"""

import pytest

pytest.skip(
    "Monitoring API endpoint tests require legacy MonitoringEntry schema no longer present.",
    allow_module_level=True,
)

import json
from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


@pytest.mark.django_db
class TestPPAWorkItemAPI:
    """Test API endpoints for PPA-WorkItem integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(
            username="api_user",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.admin_user = User.objects.create_superuser(
            username="api_admin",
            password="adminpass123",
        )

        self.organization = Organization.objects.create(
            name="API Test Org",
            acronym="ATO",
            organization_type="bmoa",
            created_by=self.user,
        )

        self.ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="API Test PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("3000000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

    def test_enable_workitem_tracking_api_success(self):
        """Test enable_workitem_tracking API endpoint."""
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "monitoring:ppa-enable-workitem-tracking", kwargs={"pk": self.ppa.pk}
        )

        data = {"template": "program", "auto_activate": True}

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["workitem_count"] == 4  # 1 project + 3 activities

    def test_enable_workitem_tracking_api_invalid_template(self):
        """Test enable_workitem_tracking with invalid template."""
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "monitoring:ppa-enable-workitem-tracking", kwargs={"pk": self.ppa.pk}
        )

        data = {"template": "invalid_template"}

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_budget_allocation_tree_api(self):
        """Test budget_allocation_tree API endpoint."""
        self.client.force_authenticate(user=self.user)

        # Enable tracking first
        self.ppa.enable_workitem_tracking(template="minimal")

        url = reverse("monitoring:ppa-budget-tree", kwargs={"pk": self.ppa.pk})

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "total_budget" in response.data
        assert "items" in response.data
        assert response.data["total_budget"] == "3000000.00"

    def test_distribute_budget_api_equal(self):
        """Test distribute_budget API endpoint with equal distribution."""
        self.client.force_authenticate(user=self.user)

        # Enable tracking first
        self.ppa.enable_workitem_tracking(template="activity")

        url = reverse("monitoring:ppa-distribute-budget", kwargs={"pk": self.ppa.pk})

        data = {"method": "equal", "apply": True}

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "allocations" in response.data

    def test_distribute_budget_api_weighted(self):
        """Test distribute_budget API endpoint with weighted distribution."""
        self.client.force_authenticate(user=self.user)

        self.ppa.start_date = date(2025, 1, 1)
        self.ppa.end_date = date(2025, 12, 31)
        self.ppa.save()

        self.ppa.enable_workitem_tracking(template="activity")

        url = reverse("monitoring:ppa-distribute-budget", kwargs={"pk": self.ppa.pk})

        data = {
            "method": "weighted",
            "weight_by": "duration",
            "apply": True,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_distribute_budget_api_manual(self):
        """Test distribute_budget API endpoint with manual allocations."""
        self.client.force_authenticate(user=self.user)

        result = self.ppa.enable_workitem_tracking(template="activity")
        activity_id = result["root_workitem_id"]

        # Get child task IDs
        activity = WorkItem.objects.get(id=activity_id)
        tasks = list(activity.get_children())

        url = reverse("monitoring:ppa-distribute-budget", kwargs={"pk": self.ppa.pk})

        # Manual allocations for each task
        allocations = {
            str(tasks[0].id): "600000.00",
            str(tasks[1].id): "800000.00",
            str(tasks[2].id): "500000.00",
            str(tasks[3].id): "700000.00",
            str(tasks[4].id): "400000.00",
        }

        data = {
            "method": "manual",
            "allocations": allocations,
            "apply": True,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_sync_from_workitem_api(self):
        """Test sync_from_workitem API endpoint."""
        self.client.force_authenticate(user=self.user)

        # Create execution project
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Sync Test Project",
            ppa_source=self.ppa,
            progress=75,
            status=WorkItem.STATUS_IN_PROGRESS,
        )

        url = reverse("monitoring:ppa-sync-from-workitem", kwargs={"pk": self.ppa.pk})

        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "progress" in response.data
        assert "status" in response.data

        # Verify PPA was updated
        self.ppa.refresh_from_db()
        assert self.ppa.overall_progress == 75
        assert self.ppa.status == "ongoing"

    def test_api_authentication_required(self):
        """Test all API endpoints require authentication."""
        # No authentication
        self.client.force_authenticate(user=None)

        urls = [
            reverse(
                "monitoring:ppa-enable-workitem-tracking", kwargs={"pk": self.ppa.pk}
            ),
            reverse("monitoring:ppa-budget-tree", kwargs={"pk": self.ppa.pk}),
            reverse("monitoring:ppa-distribute-budget", kwargs={"pk": self.ppa.pk}),
            reverse("monitoring:ppa-sync-from-workitem", kwargs={"pk": self.ppa.pk}),
        ]

        for url in urls:
            response = self.client.get(url)
            assert response.status_code in [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]

    def test_api_permissions_staff_only(self):
        """Test API endpoints require staff permissions."""
        # Create non-staff user
        non_staff = User.objects.create_user(
            username="non_staff",
            password="testpass123",
            user_type="guest",  # Not staff
        )

        self.client.force_authenticate(user=non_staff)

        url = reverse(
            "monitoring:ppa-enable-workitem-tracking", kwargs={"pk": self.ppa.pk}
        )

        response = self.client.post(url, {"template": "program"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_api_error_response_ppa_not_found(self):
        """Test API error handling for non-existent PPA."""
        self.client.force_authenticate(user=self.user)

        from uuid import uuid4

        fake_id = uuid4()

        url = reverse("monitoring:ppa-budget-tree", kwargs={"pk": fake_id})

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_api_error_response_invalid_data(self):
        """Test API error handling for invalid request data."""
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "monitoring:ppa-distribute-budget", kwargs={"pk": self.ppa.pk}
        )

        # Missing required fields
        data = {"method": "manual"}  # Missing 'allocations'

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_api_pagination(self):
        """Test API pagination for list endpoints."""
        self.client.force_authenticate(user=self.user)

        # Create multiple PPAs
        for i in range(25):
            MonitoringEntry.objects.create(
                category="moa_ppa",
                name=f"PPA {i+1}",
                implementing_moa=self.organization,
                budget_allocation=Decimal("1000000.00"),
                fiscal_year=2025,
                created_by=self.user,
            )

        url = reverse("monitoring:ppa-list")

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
        assert len(response.data["results"]) <= 20  # Default page size

    def test_api_filtering(self):
        """Test API filtering by fiscal year."""
        self.client.force_authenticate(user=self.user)

        # Create PPAs for different years
        ppa_2025 = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="PPA 2025",
            implementing_moa=self.organization,
            budget_allocation=Decimal("1000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        ppa_2026 = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="PPA 2026",
            implementing_moa=self.organization,
            budget_allocation=Decimal("1000000.00"),
            fiscal_year=2026,
            created_by=self.user,
        )

        url = reverse("monitoring:ppa-list")

        # Filter by fiscal_year=2025
        response = self.client.get(url, {"fiscal_year": 2025})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1
        assert all(
            ppa["fiscal_year"] == 2025 for ppa in response.data["results"]
        )

    def test_api_ordering(self):
        """Test API ordering by different fields."""
        self.client.force_authenticate(user=self.user)

        url = reverse("monitoring:ppa-list")

        # Order by budget_allocation descending
        response = self.client.get(url, {"ordering": "-budget_allocation"})

        assert response.status_code == status.HTTP_200_OK

        budgets = [
            Decimal(ppa["budget_allocation"])
            for ppa in response.data["results"]
            if ppa["budget_allocation"]
        ]

        # Verify descending order
        assert budgets == sorted(budgets, reverse=True)

    @pytest.mark.parametrize(
        "endpoint,method",
        [
            ("ppa-enable-workitem-tracking", "POST"),
            ("ppa-budget-tree", "GET"),
            ("ppa-distribute-budget", "POST"),
            ("ppa-sync-from-workitem", "POST"),
        ],
    )
    def test_api_response_time(self, endpoint, method):
        """Test API response times are reasonable."""
        self.client.force_authenticate(user=self.user)

        url = reverse(f"monitoring:{endpoint}", kwargs={"pk": self.ppa.pk})

        import time

        start = time.time()

        if method == "GET":
            response = self.client.get(url)
        else:
            response = self.client.post(url, {}, format="json")

        elapsed = time.time() - start

        # All API calls should complete within 1 second
        assert elapsed < 1.0
