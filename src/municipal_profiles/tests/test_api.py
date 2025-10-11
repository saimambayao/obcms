import pytest

try:
    from django.contrib.auth import get_user_model
    from django.urls import reverse
    from rest_framework import status
    from rest_framework.test import APITestCase

    from common.models import Barangay, Municipality, Province, Region
    from communities.models import OBCCommunity
    from municipal_profiles.models import MunicipalOBCProfile
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django and DRF are required for municipal profile API tests",
        allow_module_level=True,
    )

User = get_user_model()


class MunicipalOBCProfileAPITest(APITestCase):
    """Integration tests for municipal level OBC profile APIs."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="municipal-user",
            email="municipal@example.com",
            password="pass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.region = Region.objects.create(code="R09", name="Zamboanga Peninsula")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-100",
            name="Zamboanga del Norte",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-100",
            name="Dipolog City",
        )

        self.barangay_a = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-A",
            name="Barangay Central",
        )
        self.barangay_b = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-B",
            name="Barangay Miputak",
        )

        self.community_a = OBCCommunity.objects.create(
            barangay=self.barangay_a,
            community_names="Central Cluster",
            estimated_obc_population=150,
            households=30,
            families=25,
        )
        self.community_b = OBCCommunity.objects.create(
            barangay=self.barangay_b,
            community_names="Coastal Cluster",
            estimated_obc_population=120,
            households=24,
            families=20,
        )
        self.aggregated_population = (
            self.community_a.estimated_obc_population
            + self.community_b.estimated_obc_population
        )

        self.client.force_authenticate(self.user)

    def _create_payload(self):
        return {
            "municipality": self.municipality.id,
            "reported_metrics": {
                "sections": {
                    "demographics": {
                        "estimated_obc_population": self.aggregated_population + 40,
                        "households": 70,
                    }
                },
                "provided_fields": [
                    "estimated_obc_population",
                    "households",
                ],
            },
            "reported_notes": "Initial municipal submission",
            "history_note": "Baseline upload",
        }

    def _create_profile_via_api(self):
        url = reverse("municipal_profiles_api:municipal-obc-profile-list")
        payload = self._create_payload()
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_create_profile_initialises_aggregation(self):
        """POST /profiles should create the profile and populate aggregates."""
        previous_version = MunicipalOBCProfile.objects.get(
            municipality=self.municipality
        ).aggregation_version

        response = self._create_profile_via_api()

        self.assertGreaterEqual(
            response.data["aggregation_version"], previous_version + 1
        )
        demographics = response.data["aggregated_metrics"]["sections"]["demographics"]
        self.assertEqual(
            demographics["estimated_obc_population"], self.aggregated_population
        )

        profile = MunicipalOBCProfile.objects.get(municipality=self.municipality)
        self.assertEqual(profile.reported_notes, "Initial municipal submission")
        self.assertEqual(
            profile.aggregation_version, response.data["aggregation_version"]
        )

    def test_refresh_aggregation_increments_version(self):
        """Refreshing the aggregation should recompute totals and bump the version."""
        self._create_profile_via_api()
        profile = MunicipalOBCProfile.objects.get(municipality=self.municipality)

        # Update barangay data to trigger a different aggregate result.
        self.community_a.estimated_obc_population = 175
        self.community_a.save(update_fields=["estimated_obc_population", "updated_at"])
        profile.refresh_from_db()
        version_after_signal = profile.aggregation_version

        refresh_url = reverse(
            "municipal_profiles_api:municipal-obc-profile-refresh-aggregation",
            args=[profile.id],
        )
        response = self.client.post(refresh_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aggregation_version"], version_after_signal + 1)

        demographics = response.data["aggregated_metrics"]["sections"]["demographics"]
        expected_total = (
            self.community_a.estimated_obc_population
            + self.community_b.estimated_obc_population
        )
        self.assertEqual(demographics["estimated_obc_population"], expected_total)
