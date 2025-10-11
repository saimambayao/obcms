"""Tests for the population hierarchy import command."""

import tempfile
from pathlib import Path

import pytest

try:
    from django.core.management import call_command
    from django.test import TestCase
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for population import tests",
        allow_module_level=True,
    )

from common.models import Barangay, Municipality, Province, Region


class PopulationImportCommandTest(TestCase):
    """Verify that the import command builds and updates the location hierarchy."""

    def setUp(self) -> None:
        super().setUp()
        self._dataset_tempdir = tempfile.TemporaryDirectory()
        self.dataset_dir = Path(self._dataset_tempdir.name)
        self.dataset_file = self.dataset_dir / "region_ix_population_raw.txt"

    def tearDown(self) -> None:
        self._dataset_tempdir.cleanup()
        super().tearDown()

    def write_dataset(self, content: str) -> None:
        self.dataset_file.write_text(content, encoding="utf-8")

    def import_dataset(self) -> None:
        call_command(
            "import_population_hierarchy",
            "--regions",
            "IX",
            "--dataset-dir",
            str(self.dataset_dir),
        )

    def test_import_creates_and_updates_hierarchy(self) -> None:
        initial_content = (
            "TEST PROVINCE\t100\n"
            "\tSample City\t60\n"
            "\t\tBarangay Uno\t30\n"
            "\t\tBarangay Dos\t30\n"
            "\tSample Town\t40\n"
            "\t\tBarangay Tres\t40\n"
        )
        self.write_dataset(initial_content)

        self.import_dataset()

        region = Region.objects.get(code="IX")
        self.assertEqual(region.name, "Zamboanga Peninsula")

        province = Province.objects.get(name="Test Province")
        self.assertEqual(province.population_total, 100)
        self.assertEqual(province.region, region)
        self.assertTrue(province.code)

        city = Municipality.objects.get(name="Sample City")
        self.assertEqual(city.population_total, 60)
        self.assertEqual(city.municipality_type, "city")

        town = Municipality.objects.get(name="Sample Town")
        self.assertEqual(town.population_total, 40)
        self.assertEqual(town.municipality_type, "municipality")

        barangay = Barangay.objects.get(name="Barangay Tres")
        self.assertEqual(barangay.population_total, 40)

        updated_content = (
            "TEST PROVINCE\t120\n"
            "\tSample City\t70\n"
            "\t\tBarangay Uno\t35\n"
            "\t\tBarangay Dos\t35\n"
            "\tSample Town\t50\n"
            "\t\tBarangay Tres\t50\n"
        )
        self.write_dataset(updated_content)

        self.import_dataset()

        province.refresh_from_db()
        self.assertEqual(province.population_total, 120)

        city.refresh_from_db()
        self.assertEqual(city.population_total, 70)

        barangay.refresh_from_db()
        self.assertEqual(barangay.population_total, 50)

        self.assertEqual(Region.objects.count(), 1)
        self.assertEqual(Province.objects.count(), 1)
        self.assertEqual(Municipality.objects.count(), 2)
        self.assertEqual(Barangay.objects.count(), 3)
