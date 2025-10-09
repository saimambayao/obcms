"""
Comprehensive Cross-Level Integration Tests for OBC Hierarchy System.

Tests the complete data flow: Barangay OBC → Municipal Coverage → Provincial Coverage

Test Categories:
- A. Full Hierarchy Data Flow (8 tests)
- B. Data Integrity Validation (6 tests)
- C. Performance Testing (4 tests)
- D. Edge Cases (8 tests)
- E. Concurrent Modifications (4 tests)
- F. Geographic Hierarchy Validation (4 tests)
"""

import pytest

pytest.skip(
    "Legacy community integration tests require updated hierarchy fixtures after refactor.",
    allow_module_level=True,
)

import time
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.db.models import Sum

from common.models import Barangay, Municipality, Province, Region
from ..models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage, AGGREGATED_NUMERIC_FIELDS
from .mocks import mock_geocoding

User = get_user_model()


class OBCHierarchyDataFlowTests(TestCase):
    """Test Category A: Full Hierarchy Data Flow (8 tests)"""

    def setUp(self):
        """Create geographic hierarchy for testing."""
        # Start geocoding mock to avoid API calls
        self.geocoding_mock = mock_geocoding()
        self.geocoding_mock.__enter__()

        self.region = Region.objects.create(code="IX", name="Zamboanga Peninsula")
        self.province = Province.objects.create(
            region=self.region,
            code="ZN",
            name="Zamboanga del Norte"
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="DIPOLOG",
            name="Dipolog City",
            municipality_type="component_city"
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Central"
        )

    def tearDown(self):
        """Stop geocoding mock."""
        self.geocoding_mock.__exit__(None, None, None)

    def test_01_create_barangay_triggers_municipal_and_provincial(self):
        """Test 1: Create Barangay OBC → Verify Municipal auto-creates → Verify Provincial auto-creates"""

        # No coverage should exist yet
        self.assertFalse(MunicipalityCoverage.objects.filter(municipality=self.municipality).exists())
        self.assertFalse(ProvinceCoverage.objects.filter(province=self.province).exists())

        # Create Barangay OBC
        obc = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Test Community",
            estimated_obc_population=500,
            households=100,
            women_count=250,
            children_0_9=80,
            mosques_count=2
        )

        # Verify Municipal Coverage auto-created
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertTrue(municipal_coverage.auto_sync)
        self.assertEqual(municipal_coverage.total_obc_communities, 1)
        self.assertEqual(municipal_coverage.households, 100)
        self.assertEqual(municipal_coverage.women_count, 250)
        self.assertEqual(municipal_coverage.children_0_9, 80)
        self.assertEqual(municipal_coverage.mosques_count, 2)
        self.assertIn("Central", municipal_coverage.key_barangays)

        # Verify Provincial Coverage auto-created
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertTrue(provincial_coverage.auto_sync)
        self.assertEqual(provincial_coverage.total_municipalities, 1)
        self.assertEqual(provincial_coverage.total_obc_communities, 1)
        self.assertEqual(provincial_coverage.households, 100)
        self.assertEqual(provincial_coverage.women_count, 250)
        self.assertIn("Dipolog City", provincial_coverage.key_municipalities)

    def test_02_update_barangay_cascades_upward(self):
        """Test 2: Update Barangay OBC population → Verify Municipal updates → Verify Provincial updates"""

        # Create initial OBC
        obc = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Test Community",
            estimated_obc_population=500,
            households=100,
            women_count=250
        )

        # Update the Barangay OBC
        obc.households = 150
        obc.women_count = 350
        obc.pwd_count = 20
        obc.save()

        # Verify Municipal Coverage updated
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.households, 150)
        self.assertEqual(municipal_coverage.women_count, 350)
        self.assertEqual(municipal_coverage.pwd_count, 20)

        # Verify Provincial Coverage updated
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial_coverage.households, 150)
        self.assertEqual(provincial_coverage.women_count, 350)
        self.assertEqual(provincial_coverage.pwd_count, 20)

    def test_03_delete_barangay_recalculates_upward(self):
        """Test 3: Delete Barangay OBC → Verify Municipal recalculates → Verify Provincial recalculates"""

        # Create two OBCs
        obc1 = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Community 1",
            households=100,
            women_count=200
        )

        barangay2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="East"
        )
        obc2 = OBCCommunity.objects.create(
            barangay=barangay2,
            community_names="Community 2",
            households=50,
            women_count=100
        )

        # Verify initial totals
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.total_obc_communities, 2)
        self.assertEqual(municipal_coverage.households, 150)
        self.assertEqual(municipal_coverage.women_count, 300)

        # Delete one OBC
        obc1.delete()

        # Verify Municipal recalculated
        municipal_coverage.refresh_from_db()
        self.assertEqual(municipal_coverage.total_obc_communities, 1)
        self.assertEqual(municipal_coverage.households, 50)
        self.assertEqual(municipal_coverage.women_count, 100)

        # Verify Provincial recalculated
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial_coverage.total_obc_communities, 1)
        self.assertEqual(provincial_coverage.households, 50)

    def test_04_multiple_barangays_same_municipality(self):
        """Test 4: Create multiple Barangay OBCs in same municipality → Verify aggregation"""

        # Create 3 barangays with OBCs
        data = [
            ("BRGY-001", "Central", 100, 200),
            ("BRGY-002", "East", 150, 300),
            ("BRGY-003", "West", 80, 160),
        ]

        for code, name, households, women in data:
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=code,
                name=name
            )
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"{name} Community",
                households=households,
                women_count=women,
                children_0_9=households // 2
            )

        # Verify Municipal aggregation
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.total_obc_communities, 3)
        self.assertEqual(municipal_coverage.households, 330)  # 100 + 150 + 80
        self.assertEqual(municipal_coverage.women_count, 660)  # 200 + 300 + 160
        self.assertEqual(municipal_coverage.children_0_9, 165)  # 50 + 75 + 40

        # Verify all barangays listed
        self.assertIn("Central", municipal_coverage.key_barangays)
        self.assertIn("East", municipal_coverage.key_barangays)
        self.assertIn("West", municipal_coverage.key_barangays)

    def test_05_multiple_municipalities_provincial_totals(self):
        """Test 5: Create Barangays across multiple municipalities → Verify provincial totals"""

        # Create second municipality
        municipality2 = Municipality.objects.create(
            province=self.province,
            code="DAPITAN",
            name="Dapitan City",
            municipality_type="component_city"
        )

        # Create OBCs in both municipalities
        brgy1 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Central"
        )
        OBCCommunity.objects.create(
            barangay=brgy1,
            community_names="Dipolog Community",
            households=100,
            women_count=200,
            farmers_count=50
        )

        brgy2 = Barangay.objects.create(
            municipality=municipality2,
            code="BRGY-002",
            name="Dakudao"
        )
        OBCCommunity.objects.create(
            barangay=brgy2,
            community_names="Dapitan Community",
            households=75,
            women_count=150,
            farmers_count=30
        )

        # Verify Provincial totals
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial_coverage.total_municipalities, 2)
        self.assertEqual(provincial_coverage.total_obc_communities, 2)
        self.assertEqual(provincial_coverage.households, 175)  # 100 + 75
        self.assertEqual(provincial_coverage.women_count, 350)  # 200 + 150
        self.assertEqual(provincial_coverage.farmers_count, 80)  # 50 + 30

        # Verify both municipalities listed
        self.assertIn("Dipolog City", provincial_coverage.key_municipalities)
        self.assertIn("Dapitan City", provincial_coverage.key_municipalities)

    def test_06_soft_delete_excludes_from_aggregation(self):
        """Test 6: Soft delete Barangay OBC → Verify exclusion from aggregation"""

        # Create two OBCs
        obc1 = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Community 1",
            households=100,
            women_count=200
        )

        barangay2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="East"
        )
        obc2 = OBCCommunity.objects.create(
            barangay=barangay2,
            community_names="Community 2",
            households=50,
            women_count=100
        )

        # Verify initial totals
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.total_obc_communities, 2)
        self.assertEqual(municipal_coverage.households, 150)

        # Soft delete one OBC
        obc1.soft_delete()

        # Trigger re-sync (normally done by signal, but soft_delete doesn't trigger post_delete)
        municipal_coverage.refresh_from_communities()
        municipal_coverage.refresh_from_db()

        # Verify soft-deleted OBC excluded from aggregation
        self.assertEqual(municipal_coverage.total_obc_communities, 1)
        self.assertEqual(municipal_coverage.households, 50)
        self.assertEqual(municipal_coverage.women_count, 100)

    def test_07_restore_includes_in_aggregation(self):
        """Test 7: Restore Barangay OBC → Verify re-inclusion in aggregation"""

        # Create and soft-delete OBC
        obc = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Test Community",
            households=100,
            women_count=200
        )

        obc.soft_delete()

        # Verify excluded
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        municipal_coverage.refresh_from_communities()
        municipal_coverage.refresh_from_db()
        self.assertEqual(municipal_coverage.total_obc_communities, 0)

        # Restore OBC
        obc.restore()

        # Trigger re-sync
        municipal_coverage.refresh_from_communities()
        municipal_coverage.refresh_from_db()

        # Verify re-included in aggregation
        self.assertEqual(municipal_coverage.total_obc_communities, 1)
        self.assertEqual(municipal_coverage.households, 100)
        self.assertEqual(municipal_coverage.women_count, 200)

    def test_08_mixed_operations_final_state_correct(self):
        """Test 8: Mixed operations (create, update, delete) → Verify final state correct"""

        # Create 3 OBCs
        brgys = []
        obcs = []
        for i in range(1, 4):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-00{i}",
                name=f"Barangay {i}"
            )
            brgys.append(brgy)
            obc = OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i}",
                households=100,
                women_count=200
            )
            obcs.append(obc)

        # Update one
        obcs[0].households = 150
        obcs[0].save()

        # Delete one
        obcs[1].delete()

        # Soft delete one
        obcs[2].soft_delete()

        # Trigger re-sync
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        municipal_coverage.refresh_from_communities()
        municipal_coverage.refresh_from_db()

        # Verify final state: Only obcs[0] should be counted (updated, not deleted)
        self.assertEqual(municipal_coverage.total_obc_communities, 1)
        self.assertEqual(municipal_coverage.households, 150)  # Updated value
        self.assertEqual(municipal_coverage.women_count, 200)


class OBCDataIntegrityTests(TestCase):
    """Test Category B: Data Integrity Validation (6 tests)"""

    def setUp(self):
        """Create geographic hierarchy with sample data."""
        # Start geocoding mock to avoid API calls
        self.geocoding_mock = mock_geocoding()
        self.geocoding_mock.__enter__()

        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="SK",
            name="Sultan Kudarat"
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="ISULAN",
            name="Isulan"
        )

    def tearDown(self):
        """Stop geocoding mock."""
        self.geocoding_mock.__exit__(None, None, None)

    def test_01_population_sum_accuracy(self):
        """Test population sum accuracy across all levels"""

        # Create 3 barangays with known populations
        populations = [500, 750, 1000]
        for i, pop in enumerate(populations, 1):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{i:03d}",
                name=f"Barangay {i}"
            )
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i}",
                estimated_obc_population=pop
            )

        # Verify Municipal aggregation (estimated_obc_population should be None for auto-sync)
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # Verify Provincial aggregation
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)

        # Manual verification of sum
        total_population = sum(populations)
        barangay_sum = OBCCommunity.objects.filter(
            barangay__municipality=self.municipality
        ).aggregate(total=Sum('estimated_obc_population'))['total']

        self.assertEqual(barangay_sum, total_population)
        self.assertEqual(barangay_sum, 2250)

    def test_02_household_count_aggregation(self):
        """Test household count aggregation"""

        households = [100, 150, 200]
        for i, hh in enumerate(households, 1):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{i:03d}",
                name=f"Barangay {i}"
            )
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i}",
                households=hh
            )

        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.households, sum(households))

        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial_coverage.households, sum(households))

    def test_03_community_count_totals(self):
        """Test community count totals"""

        # Create communities in different barangays
        for i in range(1, 6):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{i:03d}",
                name=f"Barangay {i}"
            )
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i}"
            )

        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.total_obc_communities, 5)

        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial_coverage.total_obc_communities, 5)

    def test_04_vulnerable_sector_aggregations(self):
        """Test vulnerable sector aggregations (9 fields)"""

        vulnerable_sectors = {
            'women_count': [100, 150, 200],
            'solo_parents_count': [10, 15, 20],
            'pwd_count': [20, 25, 30],
            'farmers_count': [50, 60, 70],
            'fisherfolk_count': [30, 40, 50],
            'unemployed_count': [25, 35, 45],
            'indigenous_peoples_count': [15, 20, 25],
            'idps_count': [5, 10, 15],
            'migrants_transients_count': [10, 15, 20]
        }

        # Create 3 barangays
        for i in range(3):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{i+1:03d}",
                name=f"Barangay {i+1}"
            )

            kwargs = {field: values[i] for field, values in vulnerable_sectors.items()}
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i+1}",
                **kwargs
            )

        # Verify Municipal aggregation
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        for field, values in vulnerable_sectors.items():
            expected = sum(values)
            actual = getattr(municipal_coverage, field)
            self.assertEqual(actual, expected, f"Field {field} mismatch: expected {expected}, got {actual}")

        # Verify Provincial aggregation
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        for field, values in vulnerable_sectors.items():
            expected = sum(values)
            actual = getattr(provincial_coverage, field)
            self.assertEqual(actual, expected, f"Provincial {field} mismatch: expected {expected}, got {actual}")

    def test_05_age_demographics_aggregation(self):
        """Test age demographics aggregation (5 fields)"""

        age_demographics = {
            'children_0_9': [50, 60, 70],
            'adolescents_10_14': [30, 35, 40],
            'youth_15_30': [100, 120, 140],
            'adults_31_59': [150, 180, 200],
            'seniors_60_plus': [20, 25, 30]
        }

        # Create 3 barangays
        for i in range(3):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{i+1:03d}",
                name=f"Barangay {i+1}"
            )

            kwargs = {field: values[i] for field, values in age_demographics.items()}
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i+1}",
                **kwargs
            )

        # Verify Municipal aggregation
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        for field, values in age_demographics.items():
            expected = sum(values)
            actual = getattr(municipal_coverage, field)
            self.assertEqual(actual, expected, f"Field {field} mismatch: expected {expected}, got {actual}")

        # Verify Provincial aggregation
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        for field, values in age_demographics.items():
            expected = sum(values)
            actual = getattr(provincial_coverage, field)
            self.assertEqual(actual, expected, f"Provincial {field} mismatch: expected {expected}, got {actual}")

    def test_06_key_lists_accuracy(self):
        """Test key_barangays and key_municipalities lists accuracy"""

        # Create barangays with specific names
        barangay_names = ["Central", "East District", "West Village", "North Zone"]
        for i, name in enumerate(barangay_names, 1):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{i:03d}",
                name=name
            )
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"{name} Community"
            )

        # Verify Municipal key_barangays
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        for name in barangay_names:
            self.assertIn(name, municipal_coverage.key_barangays)

        # Verify Provincial key_municipalities
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertIn(self.municipality.name, provincial_coverage.key_municipalities)


class OBCPerformanceTests(TransactionTestCase):
    """Test Category C: Performance Testing (4 tests)"""

    def setUp(self):
        """Create realistic scale for performance testing."""
        # Start geocoding mock to avoid API calls
        self.geocoding_mock = mock_geocoding()
        self.geocoding_mock.__enter__()

        self.region = Region.objects.create(code="IX", name="Zamboanga Peninsula")
        self.province = Province.objects.create(
            region=self.region,
            code="ZN",
            name="Zamboanga del Norte"
        )

    def tearDown(self):
        """Stop geocoding mock."""
        self.geocoding_mock.__exit__(None, None, None)

    def test_01_reasonable_scale_performance(self):
        """Test with 1 province, 5 municipalities, 50 barangays (reasonable scale)"""

        start_time = time.time()

        # Create 5 municipalities
        municipalities = []
        for i in range(1, 6):
            municipality = Municipality.objects.create(
                province=self.province,
                code=f"MUN-{i:03d}",
                name=f"Municipality {i}"
            )
            municipalities.append(municipality)

        # Create 10 barangays per municipality (50 total)
        for municipality in municipalities:
            for j in range(1, 11):
                brgy = Barangay.objects.create(
                    municipality=municipality,
                    code=f"{municipality.code}-BRGY-{j:03d}",
                    name=f"{municipality.name} Barangay {j}"
                )
                OBCCommunity.objects.create(
                    barangay=brgy,
                    community_names=f"Community {j}",
                    estimated_obc_population=500,
                    households=100,
                    women_count=250
                )

        end_time = time.time()
        creation_time = end_time - start_time

        # Verify creation completed
        self.assertEqual(OBCCommunity.objects.count(), 50)
        self.assertEqual(MunicipalityCoverage.objects.count(), 5)
        self.assertEqual(ProvinceCoverage.objects.count(), 1)

        # Verify provincial totals
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial_coverage.total_municipalities, 5)
        self.assertEqual(provincial_coverage.total_obc_communities, 50)
        self.assertEqual(provincial_coverage.households, 5000)  # 100 * 50

        # Performance assertion: should complete in reasonable time
        print(f"\nCreation time for 50 communities: {creation_time:.2f}s")
        self.assertLess(creation_time, 30.0, "Creation took too long (>30s)")

    def test_02_auto_sync_time_on_create(self):
        """Measure auto-sync time on Barangay create"""

        municipality = Municipality.objects.create(
            province=self.province,
            code="TEST",
            name="Test Municipality"
        )
        brgy = Barangay.objects.create(
            municipality=municipality,
            code="BRGY-001",
            name="Test Barangay"
        )

        # Measure sync time
        start_time = time.time()
        OBCCommunity.objects.create(
            barangay=brgy,
            community_names="Test Community",
            households=100
        )
        end_time = time.time()

        sync_time = end_time - start_time

        # Verify sync completed
        self.assertTrue(MunicipalityCoverage.objects.filter(municipality=municipality).exists())
        self.assertTrue(ProvinceCoverage.objects.filter(province=self.province).exists())

        print(f"\nAuto-sync time on create: {sync_time:.4f}s")
        self.assertLess(sync_time, 1.0, "Auto-sync on create took too long (>1s)")

    def test_03_auto_sync_time_on_update(self):
        """Measure auto-sync time on Barangay update"""

        municipality = Municipality.objects.create(
            province=self.province,
            code="TEST",
            name="Test Municipality"
        )
        brgy = Barangay.objects.create(
            municipality=municipality,
            code="BRGY-001",
            name="Test Barangay"
        )
        obc = OBCCommunity.objects.create(
            barangay=brgy,
            community_names="Test Community",
            households=100
        )

        # Measure sync time on update
        start_time = time.time()
        obc.households = 200
        obc.save()
        end_time = time.time()

        sync_time = end_time - start_time

        # Verify update synced
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=municipality)
        self.assertEqual(municipal_coverage.households, 200)

        print(f"\nAuto-sync time on update: {sync_time:.4f}s")
        self.assertLess(sync_time, 1.0, "Auto-sync on update took too long (>1s)")

    def test_04_manual_refresh_performance(self):
        """Measure refresh_from_communities() performance"""

        municipality = Municipality.objects.create(
            province=self.province,
            code="TEST",
            name="Test Municipality"
        )

        # Create 20 barangays
        for i in range(1, 21):
            brgy = Barangay.objects.create(
                municipality=municipality,
                code=f"BRGY-{i:03d}",
                name=f"Barangay {i}"
            )
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i}",
                households=100
            )

        municipal_coverage = MunicipalityCoverage.objects.get(municipality=municipality)

        # Measure manual refresh time
        start_time = time.time()
        municipal_coverage.refresh_from_communities()
        end_time = time.time()

        refresh_time = end_time - start_time

        print(f"\nManual refresh time (20 communities): {refresh_time:.4f}s")
        self.assertLess(refresh_time, 0.5, "Manual refresh took too long (>0.5s)")


class OBCEdgeCaseTests(TestCase):
    """Test Category D: Edge Cases (8 tests)"""

    def setUp(self):
        """Create basic geographic hierarchy."""
        # Start geocoding mock to avoid API calls
        self.geocoding_mock = mock_geocoding()
        self.geocoding_mock.__enter__()

        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="SK",
            name="Sultan Kudarat"
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="ISULAN",
            name="Isulan"
        )

    def tearDown(self):
        """Stop geocoding mock."""
        self.geocoding_mock.__exit__(None, None, None)

    def test_01_empty_municipality(self):
        """Test empty municipality (no Barangay OBCs)"""

        # Create municipality but no OBCs
        # Coverage should still be created but with zero values
        # Actually, coverage is only created when first OBC is created

        # Manually create coverage to test edge case
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )
        coverage.refresh_from_communities()
        coverage.refresh_from_db()

        self.assertEqual(coverage.total_obc_communities, 0)
        self.assertEqual(coverage.households, 0)
        self.assertEqual(coverage.key_barangays, "")

    def test_02_empty_province(self):
        """Test empty province (no Municipal Coverages)"""

        # Manually create provincial coverage
        coverage = ProvinceCoverage.objects.create(
            province=self.province
        )
        coverage.refresh_from_municipalities()
        coverage.refresh_from_db()

        self.assertEqual(coverage.total_municipalities, 0)
        self.assertEqual(coverage.total_obc_communities, 0)
        self.assertEqual(coverage.households, 0)

    def test_03_zero_population_barangay(self):
        """Test Barangay with zero population"""

        brgy = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Empty Barangay"
        )
        obc = OBCCommunity.objects.create(
            barangay=brgy,
            community_names="Empty Community",
            estimated_obc_population=0,
            households=0
        )

        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.total_obc_communities, 1)
        self.assertEqual(municipal_coverage.households, 0)

    def test_04_missing_demographic_fields(self):
        """Test Barangay with missing demographic fields (all null)"""

        brgy = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Incomplete Data Barangay"
        )
        obc = OBCCommunity.objects.create(
            barangay=brgy,
            community_names="Incomplete Community"
            # All demographic fields left as null/default
        )

        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # All aggregated fields should be 0 (not null)
        self.assertEqual(municipal_coverage.households, 0)
        self.assertEqual(municipal_coverage.women_count, 0)
        self.assertEqual(municipal_coverage.children_0_9, 0)

    def test_05_manual_override_vs_auto_sync(self):
        """Test Municipal with manual override vs auto-sync conflict"""

        brgy = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Test Barangay"
        )
        OBCCommunity.objects.create(
            barangay=brgy,
            community_names="Test Community",
            households=100
        )

        # Disable auto-sync and set manual values
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        municipal_coverage.auto_sync = False
        municipal_coverage.households = 999
        municipal_coverage.save()

        # Create another OBC
        brgy2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Test Barangay 2"
        )
        OBCCommunity.objects.create(
            barangay=brgy2,
            community_names="Test Community 2",
            households=50
        )

        # Manual values should be preserved (auto-sync disabled)
        municipal_coverage.refresh_from_db()
        self.assertEqual(municipal_coverage.households, 999)

        # Re-enable auto-sync
        municipal_coverage.auto_sync = True
        municipal_coverage.save()
        municipal_coverage.refresh_from_communities()
        municipal_coverage.refresh_from_db()

        # Should now reflect actual totals
        self.assertEqual(municipal_coverage.households, 150)  # 100 + 50

    def test_06_mixed_auto_sync_provincial(self):
        """Test Provincial with mixed auto_sync=True and auto_sync=False municipals"""

        # Create two municipalities
        municipality2 = Municipality.objects.create(
            province=self.province,
            code="TACURONG",
            name="Tacurong City"
        )

        # Municipality 1: auto-sync enabled
        brgy1 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Isulan Barangay"
        )
        OBCCommunity.objects.create(
            barangay=brgy1,
            community_names="Isulan Community",
            households=100
        )

        # Municipality 2: auto-sync disabled with manual values
        brgy2 = Barangay.objects.create(
            municipality=municipality2,
            code="BRGY-002",
            name="Tacurong Barangay"
        )
        OBCCommunity.objects.create(
            barangay=brgy2,
            community_names="Tacurong Community",
            households=50
        )

        municipal_coverage2 = MunicipalityCoverage.objects.get(municipality=municipality2)
        municipal_coverage2.auto_sync = False
        municipal_coverage2.households = 999
        municipal_coverage2.save()

        # Provincial should aggregate actual values from both
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        # Provincial aggregates from Municipal records, not Barangay
        # So it will get 100 (auto-sync) + 999 (manual) = 1099
        self.assertEqual(provincial_coverage.households, 1099)

    def test_07_deletion_cascade_municipality(self):
        """Test deletion cascade (delete Municipality → verify coverage deleted)"""

        brgy = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Test Barangay"
        )
        OBCCommunity.objects.create(
            barangay=brgy,
            community_names="Test Community"
        )

        # Verify coverage exists
        self.assertTrue(MunicipalityCoverage.objects.filter(municipality=self.municipality).exists())

        # Delete municipality (should cascade)
        municipality_id = self.municipality.id
        self.municipality.delete()

        # Coverage should be deleted
        self.assertFalse(MunicipalityCoverage.objects.filter(pk=municipality_id).exists())

    def test_08_deletion_cascade_province(self):
        """Test deletion cascade (delete Province → verify all coverages deleted)"""

        # Create OBC
        brgy = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Test Barangay"
        )
        OBCCommunity.objects.create(
            barangay=brgy,
            community_names="Test Community"
        )

        # Verify coverages exist
        self.assertTrue(MunicipalityCoverage.objects.filter(municipality=self.municipality).exists())
        self.assertTrue(ProvinceCoverage.objects.filter(province=self.province).exists())

        # Delete province (should cascade)
        province_id = self.province.id
        self.province.delete()

        # All coverages should be deleted
        self.assertFalse(ProvinceCoverage.objects.filter(pk=province_id).exists())
        self.assertFalse(MunicipalityCoverage.objects.filter(municipality__province_id=province_id).exists())


class OBCConcurrentModificationTests(TransactionTestCase):
    """Test Category E: Concurrent Modifications (4 tests)"""

    def setUp(self):
        """Create basic geographic hierarchy."""
        # Start geocoding mock to avoid API calls
        self.geocoding_mock = mock_geocoding()
        self.geocoding_mock.__enter__()

        self.region = Region.objects.create(code="IX", name="Zamboanga Peninsula")
        self.province = Province.objects.create(
            region=self.region,
            code="ZN",
            name="Zamboanga del Norte"
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="DIPOLOG",
            name="Dipolog City"
        )

    def tearDown(self):
        """Stop geocoding mock."""
        self.geocoding_mock.__exit__(None, None, None)

    def test_01_multiple_creates_same_municipality(self):
        """Test multiple Barangay OBC creates in same municipality (race condition)"""

        # Create multiple OBCs quickly
        obcs = []
        for i in range(1, 6):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{i:03d}",
                name=f"Barangay {i}"
            )
            obc = OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i}",
                households=100
            )
            obcs.append(obc)

        # Verify final state is correct
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.total_obc_communities, 5)
        self.assertEqual(municipal_coverage.households, 500)

    def test_02_simultaneous_updates(self):
        """Test simultaneous updates to different Barangays in same municipality"""

        # Create two OBCs
        brgy1 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay 1"
        )
        obc1 = OBCCommunity.objects.create(
            barangay=brgy1,
            community_names="Community 1",
            households=100
        )

        brgy2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Barangay 2"
        )
        obc2 = OBCCommunity.objects.create(
            barangay=brgy2,
            community_names="Community 2",
            households=150
        )

        # Update both simultaneously
        obc1.households = 120
        obc1.save()

        obc2.households = 180
        obc2.save()

        # Verify final state
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.households, 300)  # 120 + 180

    def test_03_create_during_manual_edit(self):
        """Test creating Barangay OBC while Municipal is being manually edited"""

        # Create initial OBC
        brgy1 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay 1"
        )
        OBCCommunity.objects.create(
            barangay=brgy1,
            community_names="Community 1",
            households=100
        )

        # Start manual edit (disable auto-sync)
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        municipal_coverage.auto_sync = False
        municipal_coverage.households = 999
        municipal_coverage.save()

        # Create another OBC (should not affect manual values)
        brgy2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Barangay 2"
        )
        OBCCommunity.objects.create(
            barangay=brgy2,
            community_names="Community 2",
            households=50
        )

        # Manual values should be preserved
        municipal_coverage.refresh_from_db()
        self.assertEqual(municipal_coverage.households, 999)

    def test_04_bulk_operations_then_refresh(self):
        """Test auto-sync disabled during bulk operations, then manual refresh"""

        # Disable auto-sync before bulk operations
        municipal_coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            auto_sync=False
        )

        # Bulk create OBCs
        for i in range(1, 11):
            brgy = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{i:03d}",
                name=f"Barangay {i}"
            )
            OBCCommunity.objects.create(
                barangay=brgy,
                community_names=f"Community {i}",
                households=100
            )

        # Values should not be auto-synced
        municipal_coverage.refresh_from_db()
        self.assertEqual(municipal_coverage.households, 0)

        # Re-enable auto-sync and manual refresh
        municipal_coverage.auto_sync = True
        municipal_coverage.save()
        municipal_coverage.refresh_from_communities()
        municipal_coverage.refresh_from_db()

        # Should now reflect all communities
        self.assertEqual(municipal_coverage.total_obc_communities, 10)
        self.assertEqual(municipal_coverage.households, 1000)


class OBCGeographicHierarchyTests(TestCase):
    """Test Category F: Geographic Hierarchy Validation (4 tests)"""

    def setUp(self):
        """Create complete geographic hierarchy."""
        # Start geocoding mock to avoid API calls
        self.geocoding_mock = mock_geocoding()
        self.geocoding_mock.__enter__()

        self.region = Region.objects.create(
            code="IX",
            name="Zamboanga Peninsula"
        )
        self.province = Province.objects.create(
            region=self.region,
            code="ZN",
            name="Zamboanga del Norte"
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="DIPOLOG",
            name="Dipolog City"
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="CENTRAL",
            name="Central"
        )

    def tearDown(self):
        """Stop geocoding mock."""
        self.geocoding_mock.__exit__(None, None, None)

    def test_01_complete_relationships(self):
        """Test Barangay → Municipality → Province → Region relationships"""

        obc = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Test Community"
        )

        # Verify relationships
        self.assertEqual(obc.barangay, self.barangay)
        self.assertEqual(obc.municipality, self.municipality)
        self.assertEqual(obc.province, self.province)
        self.assertEqual(obc.region, self.region)

    def test_02_region_access_from_barangay(self):
        """Test accessing region from Barangay OBC (obc.barangay.municipality.province.region)"""

        obc = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Test Community"
        )

        # Full path access
        region_via_path = obc.barangay.municipality.province.region
        self.assertEqual(region_via_path, self.region)
        self.assertEqual(region_via_path.code, "IX")
        self.assertEqual(region_via_path.name, "Zamboanga Peninsula")

    def test_03_full_location_property(self):
        """Test full_location property accuracy across all levels"""

        # Barangay OBC
        obc = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Test Community",
            specific_location="Purok 5"
        )

        # Expected: "Region IX - Zamboanga Peninsula > Zamboanga del Norte > Dipolog City > Central > Purok 5"
        full_location = obc.full_location
        self.assertIn("Central", full_location)
        self.assertIn("Purok 5", full_location)

        # Municipal Coverage
        municipal_coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(municipal_coverage.full_location, "Dipolog City, Zamboanga del Norte")

        # Provincial Coverage
        provincial_coverage = ProvinceCoverage.objects.get(province=self.province)
        self.assertIn("Zamboanga del Norte", provincial_coverage.full_location)

    def test_04_coordinates_inheritance(self):
        """Test coordinates inheritance/resolution"""

        # Set coordinates at Barangay level
        obc = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Test Community",
            latitude=8.5833,
            longitude=123.3417
        )

        # Verify coordinates accessible
        self.assertEqual(obc.latitude, 8.5833)
        self.assertEqual(obc.longitude, 123.3417)
        self.assertEqual(obc.coordinates, [123.3417, 8.5833])  # [lng, lat] for GeoJSON
