"""Test command to verify coordinate auto-generation functionality."""

import json

import pytest

try:
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.core.management.base import BaseCommand
    from django.test.client import Client

    from common.models import Barangay, Municipality, Province, Region
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for coordinate management command tests",
        allow_module_level=True,
    )


User = get_user_model()


class Command(BaseCommand):
    help = "Test coordinate auto-generation functionality"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose", action="store_true", help="Show detailed test output"
        )

    def handle(self, *args, **options):
        """Main test execution."""
        self.verbose = options.get("verbose", False)
        self.client = Client()

        allowed_hosts = list(getattr(settings, "ALLOWED_HOSTS", []))
        if "testserver" not in allowed_hosts:
            allowed_hosts.append("testserver")
            settings.ALLOWED_HOSTS = allowed_hosts

        # Create or get a test user
        test_user, created = User.objects.get_or_create(
            username="test_coordinates",
            defaults={
                "email": "test@example.com",
                "user_type": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            test_user.set_password("testpassword")
            test_user.save()

        self.client.force_login(test_user)

        self.stdout.write(
            self.style.SUCCESS("Testing coordinate auto-generation functionality")
        )

        # Test API endpoint functionality
        self._test_centroid_api()

        # Test coordinate coverage
        self._test_coordinate_coverage()

        # Test specific region coordinates
        self._test_target_regions()

        self.stdout.write(self.style.SUCCESS("Coordinate testing completed!"))

    def _test_centroid_api(self):
        """Test the centroid API endpoint."""
        self.stdout.write("Testing centroid API endpoint...")

        # Test cases: [level, sample_ids_to_test]
        test_cases = [
            ("region", ["IX", "X", "XI", "XII"]),
        ]

        for level, test_ids in test_cases:
            if level == "region":
                for region_code in test_ids:
                    region = Region.objects.filter(code=region_code).first()
                    if region:
                        self._test_single_centroid(
                            level, region.id, f"Region {region_code}"
                        )
            # Add more test cases for province, municipality, barangay as needed

    def _test_single_centroid(self, level, obj_id, description):
        """Test centroid API for a single object."""
        response = self.client.get(
            "/locations/centroid/", {"level": level, "id": obj_id}
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("has_location"):
                lat, lng = data["lat"], data["lng"]
                if self.verbose:
                    self.stdout.write(
                        f"  ✓ {description}: ({lat:.6f}, {lng:.6f}) - {data.get('source', 'unknown')}"
                    )
                else:
                    self.stdout.write(f"  ✓ {description}: coordinates found")

                # Validate coordinate bounds
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ {description}: Invalid coordinates {lat}, {lng}"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ {description}: No coordinates available")
                )
        else:
            self.stdout.write(
                self.style.ERROR(f"  ✗ {description}: API error {response.status_code}")
            )

    def _test_coordinate_coverage(self):
        """Test coordinate coverage across administrative levels."""
        self.stdout.write("Checking coordinate coverage...")

        # Test target regions
        regions = Region.objects.filter(code__in=["IX", "X", "XI", "XII"])
        regions_with_coords = 0
        for region in regions:
            if region.center_coordinates:
                regions_with_coords += 1

        self.stdout.write(
            f"  Regions: {regions_with_coords}/{regions.count()} have coordinates"
        )

        # Test provinces in target regions
        provinces = Province.objects.filter(region__code__in=["IX", "X", "XI", "XII"])
        provinces_with_coords = sum(1 for p in provinces if p.center_coordinates)

        self.stdout.write(
            f"  Provinces: {provinces_with_coords}/{provinces.count()} have coordinates"
        )

        # Test sample municipalities
        municipalities = Municipality.objects.filter(
            province__region__code__in=["IX", "X", "XI", "XII"]
        )[
            :50
        ]  # Sample first 50
        municipalities_with_coords = sum(
            1 for m in municipalities if m.center_coordinates
        )

        self.stdout.write(
            f"  Sample Municipalities: {municipalities_with_coords}/{municipalities.count()} have coordinates"
        )

    def _test_target_regions(self):
        """Test specific coordinate accuracy for target regions."""
        self.stdout.write("Testing target region coordinate accuracy...")

        expected_coordinates = {
            "IX": {"lat": 8.6549449, "lng": 123.4243754, "name": "Zamboanga Peninsula"},
            "X": {"lat": 8.4860705, "lng": 124.656805, "name": "Northern Mindanao"},
            "XI": {"lat": 7.085773, "lng": 125.616083, "name": "Davao Region"},
            "XII": {"lat": 6.2965755, "lng": 124.9860759, "name": "SOCCSKSARGEN"},
        }

        for code, expected in expected_coordinates.items():
            region = Region.objects.filter(code=code).first()
            if region and region.center_coordinates:
                actual_lng, actual_lat = region.center_coordinates
                lat_diff = abs(actual_lat - expected["lat"])
                lng_diff = abs(actual_lng - expected["lng"])

                # Allow for small differences in coordinates
                if lat_diff < 1.0 and lng_diff < 1.0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Region {code} coordinates are accurate"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Region {code} coordinates may need review: "
                            f"expected ({expected['lat']:.6f}, {expected['lng']:.6f}), "
                            f"got ({actual_lat:.6f}, {actual_lng:.6f})"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Region {code} missing coordinates")
                )
