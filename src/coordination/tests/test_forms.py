"""Tests for coordination module forms."""

import pytest

try:
    from django.test import TestCase
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for coordination form tests",
        allow_module_level=True,
    )

from common.models import Barangay, Municipality, Province, Region
from coordination.forms import OrganizationForm
from coordination.models import Organization


class OrganizationFormTests(TestCase):
    """Validate the partner organization form behavior."""

    @classmethod
    def setUpTestData(cls):
        cls.region = Region.objects.create(code="ZAM", name="Zamboanga Peninsula")
        cls.province = Province.objects.create(
            region=cls.region,
            code="ZAM-001",
            name="Zamboanga del Norte",
        )
        cls.municipality = Municipality.objects.create(
            province=cls.province,
            code="ZAM-001-001",
            name="Dipolog City",
        )
        cls.barangay = Barangay.objects.create(
            municipality=cls.municipality,
            code="ZAM-001-001-001",
            name="Barangay Central",
        )

    def _base_payload(self):
        return {
            "name": "Coordination Partner",
            "organization_type": "ngo",
            "partnership_status": "active",
            "engagement_frequency": "as_needed",
            "is_active": "on",
        }

    def test_plaintext_social_media_entries_are_parsed(self):
        """Allow simple 'platform: url' entries without forcing JSON."""
        payload = self._base_payload()
        payload["social_media"] = (
            "facebook: https://facebook.com/oobc\n" "x: https://x.com/oobcofficial"
        )

        form = OrganizationForm(data=payload)
        self.assertTrue(form.is_valid(), form.errors)

        instance = form.save(commit=False)
        self.assertEqual(
            instance.social_media,
            {
                "facebook": "https://facebook.com/oobc",
                "x": "https://x.com/oobcofficial",
            },
        )

    def test_location_hierarchy_auto_populates_from_barangay(self):
        """Selecting a barangay should cascade to municipality, province, and region."""
        payload = self._base_payload()
        payload.update(
            {
                "barangay": str(self.barangay.pk),
                "province": "",
                "municipality": "",
                "region": "",
            }
        )

        form = OrganizationForm(data=payload)
        self.assertTrue(form.is_valid(), form.errors)

        organization = form.save(commit=False)
        self.assertEqual(organization.barangay, self.barangay)
        self.assertEqual(organization.municipality, self.municipality)
        self.assertEqual(organization.province, self.province)
        self.assertEqual(organization.region, self.region)

    def test_mismatched_location_selection_triggers_errors(self):
        """Reject combinations where the parent administrative unit does not match."""
        other_region = Region.objects.create(code="BAS", name="Basilan")
        payload = self._base_payload()
        payload.update(
            {
                "province": str(self.province.pk),
                "region": str(other_region.pk),
            }
        )

        form = OrganizationForm(data=payload)
        self.assertFalse(form.is_valid())
        self.assertIn("province", form.errors)

    def test_model_clean_keeps_location_hierarchy_consistent(self):
        """Model-level validation should enforce geographic hierarchy even outside forms."""
        organization = Organization(
            name="Manual Save Org",
            organization_type="ngo",
            barangay=self.barangay,
        )

        organization.full_clean()
        organization.save()

        self.assertEqual(organization.municipality, self.municipality)
        self.assertEqual(organization.province, self.province)
        self.assertEqual(organization.region, self.region)
        self.assertEqual(
            organization.location_display,
            f"{self.barangay.name}, {self.municipality.name}, {self.province.name}, {self.region.name}",
        )
