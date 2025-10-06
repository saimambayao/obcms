"""Tests for location-related helper endpoints."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from common.models import Barangay, Municipality, Province, Region


class LocationCentroidViewTests(TestCase):
    """Ensure the centroid lookup endpoint returns stored coordinates."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="centroid-tester",
            email="tester@example.com",
            password="password123",
        )
        self.client.force_login(self.user)

    def test_returns_existing_coordinates(self):
        region = Region.objects.create(
            code="ZZ",
            name="Test Region",
            center_coordinates=[120.123456, 7.654321],
        )

        url = reverse("common:location_centroid")
        response = self.client.get(url, {"level": "region", "id": region.id})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["has_location"])
        self.assertAlmostEqual(payload["lat"], 7.654321)
        self.assertAlmostEqual(payload["lng"], 120.123456)
        self.assertEqual(payload["source"], "cached")

    def test_geocodes_when_coordinates_missing(self):
        region = Region.objects.create(
            code="XY",
            name="Another Region",
        )

        url = reverse("common:location_centroid")

        with patch(
            "common.views.communities.enhanced_ensure_location_coordinates",
            return_value=(7.100001, 123.456789, True, "arcgis"),
        ) as mocked_geocode:
            response = self.client.get(url, {"level": "region", "id": region.id})

        mocked_geocode.assert_called_once_with(region)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["has_location"])
        self.assertAlmostEqual(payload["lat"], 7.100001)
        self.assertAlmostEqual(payload["lng"], 123.456789)
        self.assertEqual(payload["source"], "arcgis")


class LocationDataAPITests(TestCase):
    """Verify the consolidated location payload API behaves as expected."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="location-data-tester",
            email="payload@example.com",
            password="changeme123",
        )
        self.client.force_login(self.user)

        self.region = Region.objects.create(code="RG", name="Region Gold")
        self.province = Province.objects.create(
            region=self.region, code="RG-P1", name="Sample Province"
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="RG-M1",
            name="Sample Municipality",
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="RG-B1",
            name="Sample Barangay",
        )

    def test_location_data_includes_full_hierarchy(self):
        url = reverse("common_api:location-data")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("regions", payload)
        self.assertEqual(len(payload["regions"]), 1)
        self.assertEqual(payload["regions"][0]["id"], self.region.id)

        self.assertIn("provinces", payload)
        self.assertEqual(len(payload["provinces"]), 1)
        self.assertEqual(payload["provinces"][0]["id"], self.province.id)

        self.assertIn("municipalities", payload)
        self.assertEqual(len(payload["municipalities"]), 1)
        self.assertEqual(payload["municipalities"][0]["id"], self.municipality.id)

        self.assertIn("barangays", payload)
        self.assertEqual(len(payload["barangays"]), 1)
        self.assertEqual(payload["barangays"][0]["id"], self.barangay.id)

    def test_location_data_allows_excluding_barangays(self):
        url = reverse("common_api:location-data")
        response = self.client.get(url, {"include_barangays": "0"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("regions", payload)
        self.assertIn("provinces", payload)
        self.assertIn("municipalities", payload)
        self.assertNotIn("barangays", payload)
