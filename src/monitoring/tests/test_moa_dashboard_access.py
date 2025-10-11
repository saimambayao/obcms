"""Access control tests for the MOA PPAs dashboard."""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from coordination.models import Organization
from monitoring.models import MonitoringEntry


User = get_user_model()

pytestmark = pytest.mark.integration


class MOAStaffDashboardAccessTests(TestCase):
    """Ensure MOA staff only see their organization's PPAs on the dashboard."""

    def setUp(self):
        self.moa_org = Organization.objects.create(
            name="Ministry of Agriculture",
            organization_type="bmoa",
        )
        self.other_org = Organization.objects.create(
            name="Ministry of Health",
            organization_type="bmoa",
        )
        self.moa_user = User.objects.create_user(
            username="moa_user",
            password="testpass123",
            user_type="bmoa",
            is_approved=True,
            moa_organization=self.moa_org,
        )
        self.client.force_login(self.moa_user)

        self.own_entry = MonitoringEntry.objects.create(
            title="Agriculture Support Program",
            category="moa_ppa",
            implementing_moa=self.moa_org,
            status="planning",
            progress=0,
            created_by=self.moa_user,
            updated_by=self.moa_user,
        )
        MonitoringEntry.objects.create(
            title="Health Outreach",
            category="moa_ppa",
            implementing_moa=self.other_org,
            status="planning",
            progress=0,
            created_by=self.moa_user,
            updated_by=self.moa_user,
        )

    def test_dashboard_limits_entries_to_user_moa(self):
        """Unfiltered dashboard returns only the PPAs for the staff's MOA."""
        response = self.client.get(reverse("monitoring:moa_ppas"))
        self.assertEqual(response.status_code, 200)

        entries = list(response.context["page_obj"].object_list)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], self.own_entry)

        self.assertEqual(
            response.context["selected_moa"],
            str(self.moa_org.pk),
        )

        option_ids = {
            str(option["implementing_moa__id"])
            for option in response.context["implementing_moa_options"]
        }
        self.assertEqual(option_ids, {str(self.moa_org.pk)})

    def test_foreign_moa_filter_is_ignored(self):
        """Passing another MOA ID must not expose their PPAs to the staff."""
        url = reverse("monitoring:moa_ppas")
        response = self.client.get(f"{url}?implementing_moa={self.other_org.pk}")
        self.assertEqual(response.status_code, 200)

        entries = list(response.context["page_obj"].object_list)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], self.own_entry)
        self.assertEqual(
            response.context["selected_moa"],
            str(self.moa_org.pk),
        )
