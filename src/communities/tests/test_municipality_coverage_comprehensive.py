"""
Comprehensive testing of MunicipalityCoverage model and auto-sync functionality.

This test suite verifies:
- Model creation & validation
- Auto-sync from Barangay OBCs (signal-based)
- Population reconciliation
- Manual override & sync control
- Computed properties
- Soft delete & cascade
- Integration with Provincial Coverage
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from common.models import Barangay, Municipality, Province, Region

from ..models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage

User = get_user_model()


class MunicipalityCoverageCreationValidationTests(TestCase):
    """Test Category A: Model Creation & Validation (8 scenarios)"""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
            municipality_type="municipality",
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            user_type="oobc_staff",
        )

    def test_create_with_minimum_fields(self):
        """1. Create MunicipalityCoverage with only required field (municipality)"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        self.assertIsNotNone(coverage.pk)
        self.assertEqual(coverage.municipality, self.municipality)
        self.assertTrue(coverage.auto_sync)  # Default value
        self.assertIsNone(coverage.estimated_obc_population)
        self.assertIsNone(coverage.total_obc_communities)
        self.assertEqual(coverage.key_barangays, "")

    def test_create_with_all_fields(self):
        """2. Create MunicipalityCoverage with comprehensive data"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            estimated_obc_population=5000,
            total_obc_communities=10,
            key_barangays="Brgy A, Brgy B, Brgy C",
            households=1200,
            families=1000,
            children_0_9=800,
            adolescents_10_14=400,
            youth_15_30=1200,
            adults_31_59=2000,
            seniors_60_plus=600,
            women_count=2500,
            pwd_count=100,
            farmers_count=500,
            existing_support_programs="DSWD TABANG, LGU Scholarship",
            auto_sync=False,
            created_by=self.user,
            updated_by=self.user,
        )

        self.assertEqual(coverage.estimated_obc_population, 5000)
        self.assertEqual(coverage.total_obc_communities, 10)
        self.assertEqual(coverage.households, 1200)
        self.assertEqual(coverage.children_0_9, 800)
        self.assertEqual(coverage.women_count, 2500)
        self.assertFalse(coverage.auto_sync)
        self.assertEqual(coverage.created_by, self.user)

    def test_onetoone_constraint(self):
        """3. Test OneToOne constraint - one coverage per municipality"""
        MunicipalityCoverage.objects.create(municipality=self.municipality)

        with self.assertRaises(IntegrityError):
            MunicipalityCoverage.objects.create(municipality=self.municipality)

    def test_duplicate_prevention_via_get_or_create(self):
        """4. Test duplicate prevention using get_or_create pattern"""
        coverage1, created1 = MunicipalityCoverage.objects.get_or_create(
            municipality=self.municipality
        )

        self.assertTrue(created1)

        coverage2, created2 = MunicipalityCoverage.objects.get_or_create(
            municipality=self.municipality
        )

        self.assertFalse(created2)
        self.assertEqual(coverage1.pk, coverage2.pk)

    def test_auto_sync_default_value(self):
        """5. Test auto_sync field defaults to True"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        self.assertTrue(coverage.auto_sync)

    def test_foreign_key_cascade_deletion(self):
        """6. Test foreign key CASCADE - deleting municipality deletes coverage"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )
        coverage_pk = coverage.pk

        # Delete municipality
        self.municipality.delete()

        # Coverage should be deleted too
        self.assertFalse(
            MunicipalityCoverage.all_objects.filter(pk=coverage_pk).exists()
        )

    def test_created_by_updated_by_tracking(self):
        """7. Test user tracking (created_by, updated_by)"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            created_by=self.user,
        )

        self.assertEqual(coverage.created_by, self.user)
        self.assertIsNone(coverage.updated_by)

        # Update with different user
        user2 = User.objects.create_user(
            username="updater",
            password="testpass123",
            user_type="oobc_staff",
        )
        coverage.updated_by = user2
        coverage.save()

        coverage.refresh_from_db()
        self.assertEqual(coverage.created_by, self.user)
        self.assertEqual(coverage.updated_by, user2)

    def test_existing_support_programs_field(self):
        """8. Test existing_support_programs TextField"""
        programs = "DSWD TABANG Program, LGU Scholarship, OOBC Livelihood Training"
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            existing_support_programs=programs,
        )

        coverage.refresh_from_db()
        self.assertEqual(coverage.existing_support_programs, programs)


class MunicipalityCoverageAutoSyncTests(TestCase):
    """Test Category B: Auto-Sync from Barangay OBCs (12 scenarios)"""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
            municipality_type="municipality",
        )
        self.brgy1 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay Alpha",
        )
        self.brgy2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Barangay Beta",
        )
        self.brgy3 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-003",
            name="Barangay Gamma",
        )

    def tearDown(self):
        # Clean up history records if they exist
        try:
            from municipal_profiles.models import OBCCommunityHistory
            OBCCommunityHistory.objects.all().delete()
        except ImportError:
            pass

    def test_create_multiple_barangay_obcs(self):
        """1. Create multiple Barangay OBCs in same municipality"""
        obc1 = OBCCommunity.objects.create(
            barangay=self.brgy1,
            community_names="Community Alpha",
            estimated_obc_population=500,
        )
        obc2 = OBCCommunity.objects.create(
            barangay=self.brgy2,
            community_names="Community Beta",
            estimated_obc_population=300,
        )
        obc3 = OBCCommunity.objects.create(
            barangay=self.brgy3,
            community_names="Community Gamma",
            estimated_obc_population=700,
        )

        # Verify all were created
        self.assertEqual(
            OBCCommunity.objects.filter(
                barangay__municipality=self.municipality
            ).count(),
            3
        )

    def test_auto_sync_aggregates_population(self):
        """2. Verify auto-sync aggregates estimated_obc_population"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            estimated_obc_population=500,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy2,
            estimated_obc_population=300,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy3,
            estimated_obc_population=700,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # Note: auto_sync sets estimated_obc_population to None (manual curation)
        # But barangay_attributed_population should show the total
        self.assertIsNone(coverage.estimated_obc_population)
        self.assertEqual(coverage.barangay_attributed_population, 1500)

    def test_auto_sync_aggregates_households(self):
        """3. Verify auto-sync aggregates households count"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            households=100,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy2,
            households=75,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy3,
            households=125,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(coverage.households, 300)

    def test_auto_sync_aggregates_families(self):
        """4. Verify auto-sync aggregates families count"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            families=90,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy2,
            families=65,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy3,
            families=110,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(coverage.families, 265)

    def test_auto_sync_aggregates_age_demographics(self):
        """5. Verify auto-sync aggregates all age demographic fields"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            children_0_9=100,
            adolescents_10_14=50,
            youth_15_30=150,
            adults_31_59=200,
            seniors_60_plus=30,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy2,
            children_0_9=80,
            adolescents_10_14=40,
            youth_15_30=120,
            adults_31_59=160,
            seniors_60_plus=25,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(coverage.children_0_9, 180)
        self.assertEqual(coverage.adolescents_10_14, 90)
        self.assertEqual(coverage.youth_15_30, 270)
        self.assertEqual(coverage.adults_31_59, 360)
        self.assertEqual(coverage.seniors_60_plus, 55)

    def test_auto_sync_aggregates_vulnerable_sectors(self):
        """6. Verify auto-sync aggregates vulnerable sector counts"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            women_count=250,
            solo_parents_count=20,
            pwd_count=15,
            farmers_count=80,
            fisherfolk_count=40,
            unemployed_count=30,
            indigenous_peoples_count=10,
            idps_count=5,
            migrants_transients_count=12,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy2,
            women_count=180,
            solo_parents_count=15,
            pwd_count=10,
            farmers_count=60,
            fisherfolk_count=30,
            unemployed_count=20,
            indigenous_peoples_count=8,
            idps_count=3,
            migrants_transients_count=8,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(coverage.women_count, 430)
        self.assertEqual(coverage.solo_parents_count, 35)
        self.assertEqual(coverage.pwd_count, 25)
        self.assertEqual(coverage.farmers_count, 140)
        self.assertEqual(coverage.fisherfolk_count, 70)
        self.assertEqual(coverage.unemployed_count, 50)
        self.assertEqual(coverage.indigenous_peoples_count, 18)
        self.assertEqual(coverage.idps_count, 8)
        self.assertEqual(coverage.migrants_transients_count, 20)

    def test_auto_sync_updates_total_communities(self):
        """7. Verify auto-sync updates total_obc_communities count"""
        OBCCommunity.objects.create(barangay=self.brgy1)
        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(coverage.total_obc_communities, 1)

        OBCCommunity.objects.create(barangay=self.brgy2)
        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 2)

        OBCCommunity.objects.create(barangay=self.brgy3)
        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 3)

    def test_auto_sync_builds_key_barangays_list(self):
        """8. Verify auto-sync builds key_barangays list"""
        OBCCommunity.objects.create(barangay=self.brgy1)
        OBCCommunity.objects.create(barangay=self.brgy2)
        OBCCommunity.objects.create(barangay=self.brgy3)

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # Check that all barangay names are in the key_barangays field
        self.assertIn("Barangay Alpha", coverage.key_barangays)
        self.assertIn("Barangay Beta", coverage.key_barangays)
        self.assertIn("Barangay Gamma", coverage.key_barangays)

    def test_refresh_from_communities_explicit_call(self):
        """9. Test refresh_from_communities() method explicitly"""
        # Create communities first
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            households=100,
            women_count=200,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy2,
            households=150,
            women_count=300,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # Manually update coverage to wrong values
        MunicipalityCoverage.objects.filter(pk=coverage.pk).update(
            households=0,
            women_count=0,
        )
        coverage.refresh_from_db()
        self.assertEqual(coverage.households, 0)

        # Call refresh_from_communities()
        coverage.refresh_from_communities()
        coverage.refresh_from_db()

        # Should be updated to correct aggregated values
        self.assertEqual(coverage.households, 250)
        self.assertEqual(coverage.women_count, 500)

    def test_auto_sync_cascade_on_create(self):
        """10. Test auto-sync cascade when Barangay OBC created"""
        # Initially no coverage exists
        self.assertFalse(
            MunicipalityCoverage.objects.filter(municipality=self.municipality).exists()
        )

        # Create OBC - should trigger coverage creation via signal
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            households=100,
        )

        # Coverage should now exist
        self.assertTrue(
            MunicipalityCoverage.objects.filter(municipality=self.municipality).exists()
        )
        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(coverage.households, 100)

    def test_auto_sync_cascade_on_update(self):
        """11. Test auto-sync cascade when Barangay OBC updated"""
        obc = OBCCommunity.objects.create(
            barangay=self.brgy1,
            households=100,
            women_count=200,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(coverage.households, 100)
        self.assertEqual(coverage.women_count, 200)

        # Update OBC
        obc.households = 150
        obc.women_count = 300
        obc.save()

        # Coverage should update
        coverage.refresh_from_db()
        self.assertEqual(coverage.households, 150)
        self.assertEqual(coverage.women_count, 300)

    def test_auto_sync_cascade_on_delete(self):
        """12. Test auto-sync cascade when Barangay OBC deleted"""
        obc1 = OBCCommunity.objects.create(
            barangay=self.brgy1,
            households=100,
        )
        obc2 = OBCCommunity.objects.create(
            barangay=self.brgy2,
            households=150,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertEqual(coverage.total_obc_communities, 2)
        self.assertEqual(coverage.households, 250)

        # Delete one OBC
        obc1.delete()

        # Coverage should update
        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 1)
        self.assertEqual(coverage.households, 150)


class MunicipalityCoveragePopulationReconciliationTests(TestCase):
    """Test Category C: Population Reconciliation (5 scenarios)"""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
        )
        self.brgy1 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay Alpha",
        )
        self.brgy2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Barangay Beta",
        )

    def test_population_reconciliation_property(self):
        """1. Test population_reconciliation property returns correct dict"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            estimated_obc_population=500,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy2,
            estimated_obc_population=300,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        coverage.auto_sync = False
        coverage.estimated_obc_population = 1000
        coverage.save()

        reconciliation = coverage.population_reconciliation

        self.assertIsInstance(reconciliation, dict)
        self.assertIn("total_municipal", reconciliation)
        self.assertIn("attributed_to_barangays", reconciliation)
        self.assertIn("unattributed", reconciliation)
        self.assertIn("attribution_rate", reconciliation)
        self.assertIn("auto_sync_enabled", reconciliation)

    def test_with_manual_population_set(self):
        """2. Test with manual estimated_obc_population set"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            estimated_obc_population=400,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        coverage.auto_sync = False
        coverage.estimated_obc_population = 1000  # Manual override
        coverage.save()

        reconciliation = coverage.population_reconciliation

        self.assertEqual(reconciliation["total_municipal"], 1000)
        self.assertEqual(reconciliation["attributed_to_barangays"], 400)
        self.assertEqual(reconciliation["unattributed"], 600)
        self.assertFalse(reconciliation["auto_sync_enabled"])

    def test_with_only_barangay_attributed_population(self):
        """3. Test with only barangay-attributed population (auto_sync=True)"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            estimated_obc_population=500,
        )
        OBCCommunity.objects.create(
            barangay=self.brgy2,
            estimated_obc_population=300,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # With auto_sync=True, estimated_obc_population should be None
        self.assertTrue(coverage.auto_sync)
        self.assertIsNone(coverage.estimated_obc_population)

        reconciliation = coverage.population_reconciliation

        self.assertEqual(reconciliation["total_municipal"], 0)  # None becomes 0
        self.assertEqual(reconciliation["attributed_to_barangays"], 800)
        self.assertEqual(reconciliation["unattributed"], 0)  # auto_sync=True
        self.assertTrue(reconciliation["auto_sync_enabled"])

    def test_attribution_rate_calculation(self):
        """4. Test attribution_rate calculation"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            estimated_obc_population=600,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        coverage.auto_sync = False
        coverage.estimated_obc_population = 1000
        coverage.save()

        reconciliation = coverage.population_reconciliation

        # 600 / 1000 = 0.6 = 60%
        self.assertEqual(reconciliation["attribution_rate"], 60.0)

    def test_unattributed_population_gap_detection(self):
        """5. Test unattributed population gap detection"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            estimated_obc_population=300,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        coverage.auto_sync = False
        coverage.estimated_obc_population = 1500
        coverage.save()

        # Gap: 1500 - 300 = 1200 unattributed
        self.assertEqual(coverage.unattributed_population, 1200)

        reconciliation = coverage.population_reconciliation
        self.assertEqual(reconciliation["unattributed"], 1200)


class MunicipalityCoverageManualOverrideTests(TestCase):
    """Test Category D: Manual Override & Sync Control (4 scenarios)"""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
        )
        self.brgy1 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay Alpha",
        )

    def test_auto_sync_false_no_automatic_updates(self):
        """1. Test with auto_sync=False (no automatic updates)"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            households=100,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # Disable auto_sync and set manual values
        coverage.auto_sync = False
        coverage.households = 999
        coverage.total_obc_communities = 99
        coverage.save()

        # Create another OBC
        brgy2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Barangay Beta",
        )
        OBCCommunity.objects.create(
            barangay=brgy2,
            households=200,
        )

        # Manual values should remain unchanged
        coverage.refresh_from_db()
        self.assertEqual(coverage.households, 999)
        self.assertEqual(coverage.total_obc_communities, 99)

    def test_manual_population_overrides_barangay_total(self):
        """2. Test manual estimated_obc_population overrides barangay total"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            estimated_obc_population=500,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # Set manual override
        coverage.auto_sync = False
        coverage.estimated_obc_population = 2000  # Override
        coverage.save()

        # Manual value should be preserved
        coverage.refresh_from_db()
        self.assertEqual(coverage.estimated_obc_population, 2000)

        # But barangay_attributed_population should still show barangay total
        self.assertEqual(coverage.barangay_attributed_population, 500)

    def test_refresh_from_communities_with_auto_sync_false(self):
        """3. Test refresh_from_communities() with auto_sync=False"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            households=100,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        coverage.auto_sync = False
        coverage.households = 999
        coverage.save()

        # Call refresh_from_communities() - should do nothing when auto_sync=False
        coverage.refresh_from_communities()
        coverage.refresh_from_db()

        # Manual value should remain (refresh_from_communities checks auto_sync)
        self.assertEqual(coverage.households, 999)

    def test_toggling_auto_sync_on_off(self):
        """4. Test toggling auto_sync on/off"""
        OBCCommunity.objects.create(
            barangay=self.brgy1,
            households=100,
            women_count=200,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)

        # Initially auto_sync=True
        self.assertTrue(coverage.auto_sync)
        self.assertEqual(coverage.households, 100)

        # Disable auto_sync
        coverage.auto_sync = False
        coverage.households = 999
        coverage.save()

        coverage.refresh_from_db()
        self.assertEqual(coverage.households, 999)

        # Re-enable auto_sync and refresh
        coverage.auto_sync = True
        coverage.save()
        coverage.refresh_from_communities()

        # Should now use aggregated values
        coverage.refresh_from_db()
        self.assertEqual(coverage.households, 100)
        self.assertEqual(coverage.women_count, 200)


class MunicipalityCoverageComputedPropertiesTests(TestCase):
    """Test Category E: Computed Properties (6 scenarios)"""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
        )

    def test_display_name_property(self):
        """1. Test display_name property"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        expected = f"{self.municipality.name}, {self.province.name}"
        self.assertEqual(coverage.display_name, expected)

    def test_region_property_shortcut(self):
        """2. Test region property shortcut"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        self.assertEqual(coverage.region, self.region)
        self.assertEqual(coverage.region.code, "XII")

    def test_province_property_shortcut(self):
        """3. Test province property shortcut"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        self.assertEqual(coverage.province, self.province)
        self.assertEqual(coverage.province.name, "Sultan Kudarat")

    def test_municipality_property(self):
        """4. Test municipality property"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        self.assertEqual(coverage.municipality, self.municipality)

    def test_full_location_property(self):
        """5. Test full_location property"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        expected = f"{self.municipality.name}, {self.province.name}"
        self.assertEqual(coverage.full_location, expected)

    def test_coordinates_property(self):
        """6. Test coordinates property"""
        # Set coordinates on municipality
        self.municipality.latitude = 6.6333
        self.municipality.longitude = 124.6000
        self.municipality.save()

        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            latitude=6.6333,
            longitude=124.6000,
        )

        coords = coverage.coordinates
        self.assertIsNotNone(coords)
        self.assertEqual(coords[0], 124.6000)  # longitude
        self.assertEqual(coords[1], 6.6333)    # latitude


class MunicipalityCoverageSoftDeleteTests(TestCase):
    """Test Category F: Soft Delete & Cascade (4 scenarios)"""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_soft_delete_functionality(self):
        """1. Test soft_delete() functionality"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        # Soft delete
        coverage.soft_delete(user=self.user)

        # Check soft delete flags
        coverage.refresh_from_db()
        self.assertTrue(coverage.is_deleted)
        self.assertIsNotNone(coverage.deleted_at)
        self.assertEqual(coverage.deleted_by, self.user)

        # Should not appear in default manager
        self.assertFalse(
            MunicipalityCoverage.objects.filter(pk=coverage.pk).exists()
        )

        # But should exist in all_objects manager
        self.assertTrue(
            MunicipalityCoverage.all_objects.filter(pk=coverage.pk).exists()
        )

    def test_restore_functionality(self):
        """2. Test restore() functionality"""
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        # Soft delete then restore
        coverage.soft_delete(user=self.user)
        coverage.restore()

        # Check restored state
        coverage.refresh_from_db()
        self.assertFalse(coverage.is_deleted)
        self.assertIsNone(coverage.deleted_at)

        # Should appear in default manager again
        self.assertTrue(
            MunicipalityCoverage.objects.filter(pk=coverage.pk).exists()
        )

    def test_deletion_triggers_provincial_sync(self):
        """3. Test that deleting triggers provincial coverage sync"""
        # Create coverage
        brgy = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay Alpha",
        )
        OBCCommunity.objects.create(
            barangay=brgy,
            households=100,
        )

        # Provincial coverage should be created
        provincial = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial.total_municipalities, 1)

        # Delete municipal coverage
        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        coverage.delete()

        # Provincial coverage should update
        provincial.refresh_from_db()
        self.assertEqual(provincial.total_municipalities, 0)

    def test_default_manager_behavior(self):
        """4. Test default manager behavior (hides soft-deleted)"""
        coverage1 = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

        # Create another municipality and coverage
        municipality2 = Municipality.objects.create(
            province=self.province,
            code="MUN-002",
            name="Tacurong",
        )
        coverage2 = MunicipalityCoverage.objects.create(
            municipality=municipality2
        )

        # Initially both visible
        self.assertEqual(MunicipalityCoverage.objects.count(), 2)

        # Soft delete one
        coverage1.soft_delete()

        # Default manager should show only 1
        self.assertEqual(MunicipalityCoverage.objects.count(), 1)

        # all_objects should show both
        self.assertEqual(MunicipalityCoverage.all_objects.count(), 2)


class MunicipalityCoverageProvincialIntegrationTests(TestCase):
    """Test Category G: Integration with Provincial Coverage (5 scenarios)"""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality1 = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
        )
        self.municipality2 = Municipality.objects.create(
            province=self.province,
            code="MUN-002",
            name="Tacurong",
        )

    def test_creating_triggers_provincial_sync(self):
        """1. Create MunicipalityCoverage and verify provincial sync"""
        brgy = Barangay.objects.create(
            municipality=self.municipality1,
            code="BRGY-001",
            name="Barangay Alpha",
        )
        OBCCommunity.objects.create(
            barangay=brgy,
            households=100,
            women_count=200,
        )

        # Provincial coverage should be auto-created
        provincial = ProvinceCoverage.objects.get(province=self.province)

        self.assertIsNotNone(provincial)
        self.assertEqual(provincial.total_municipalities, 1)
        self.assertEqual(provincial.total_obc_communities, 1)
        self.assertEqual(provincial.households, 100)
        self.assertEqual(provincial.women_count, 200)

    def test_updating_triggers_provincial_sync(self):
        """2. Update MunicipalityCoverage and verify provincial sync"""
        brgy = Barangay.objects.create(
            municipality=self.municipality1,
            code="BRGY-001",
            name="Barangay Alpha",
        )
        obc = OBCCommunity.objects.create(
            barangay=brgy,
            households=100,
        )

        provincial = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial.households, 100)

        # Update OBC (triggers municipal sync, which triggers provincial sync)
        obc.households = 200
        obc.save()

        provincial.refresh_from_db()
        self.assertEqual(provincial.households, 200)

    def test_deleting_triggers_provincial_sync(self):
        """3. Delete MunicipalityCoverage and verify provincial sync"""
        brgy1 = Barangay.objects.create(
            municipality=self.municipality1,
            code="BRGY-001",
            name="Barangay Alpha",
        )
        brgy2 = Barangay.objects.create(
            municipality=self.municipality2,
            code="BRGY-002",
            name="Barangay Beta",
        )

        OBCCommunity.objects.create(barangay=brgy1, households=100)
        OBCCommunity.objects.create(barangay=brgy2, households=150)

        provincial = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial.total_municipalities, 2)
        self.assertEqual(provincial.households, 250)

        # Delete one municipal coverage
        coverage1 = MunicipalityCoverage.objects.get(municipality=self.municipality1)
        coverage1.delete()

        provincial.refresh_from_db()
        self.assertEqual(provincial.total_municipalities, 1)
        self.assertEqual(provincial.households, 150)

    def test_sync_for_municipality_class_method(self):
        """4. Test sync_for_municipality() class method"""
        brgy = Barangay.objects.create(
            municipality=self.municipality1,
            code="BRGY-001",
            name="Barangay Alpha",
        )
        OBCCommunity.objects.create(
            barangay=brgy,
            households=100,
        )

        # Manually call sync_for_municipality
        coverage = MunicipalityCoverage.sync_for_municipality(self.municipality1)

        self.assertIsNotNone(coverage)
        self.assertEqual(coverage.municipality, self.municipality1)
        self.assertEqual(coverage.households, 100)

        # Should also trigger provincial sync
        provincial = ProvinceCoverage.objects.get(province=self.province)
        self.assertIsNotNone(provincial)

    def test_cascade_sync_barangay_to_provincial(self):
        """5. Test cascade sync: barangay → municipal → provincial"""
        brgy = Barangay.objects.create(
            municipality=self.municipality1,
            code="BRGY-001",
            name="Barangay Alpha",
        )

        # Create OBC (should cascade all the way to provincial)
        obc = OBCCommunity.objects.create(
            barangay=brgy,
            households=100,
            women_count=200,
            farmers_count=50,
        )

        # Verify municipal coverage
        municipal = MunicipalityCoverage.objects.get(municipality=self.municipality1)
        self.assertEqual(municipal.households, 100)
        self.assertEqual(municipal.women_count, 200)
        self.assertEqual(municipal.farmers_count, 50)

        # Verify provincial coverage
        provincial = ProvinceCoverage.objects.get(province=self.province)
        self.assertEqual(provincial.households, 100)
        self.assertEqual(provincial.women_count, 200)
        self.assertEqual(provincial.farmers_count, 50)


class MunicipalityCoverageFullWorkflowIntegrationTest(TestCase):
    """Integration test: Full workflow from barangay to provincial"""

    def setUp(self):
        self.region = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
        )

    def test_full_workflow(self):
        """Complete workflow: Create, Update, Delete with cascading sync"""
        # Step 1: Create administrative hierarchy
        brgy1 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay Alpha",
        )
        brgy2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Barangay Beta",
        )
        brgy3 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-003",
            name="Barangay Gamma",
        )

        # Step 2: Create 3 Barangay OBCs
        obc1 = OBCCommunity.objects.create(
            barangay=brgy1,
            community_names="Community Alpha",
            estimated_obc_population=500,
            households=100,
            women_count=250,
        )
        obc2 = OBCCommunity.objects.create(
            barangay=brgy2,
            community_names="Community Beta",
            estimated_obc_population=300,
            households=60,
            women_count=150,
        )
        obc3 = OBCCommunity.objects.create(
            barangay=brgy3,
            community_names="Community Gamma",
            estimated_obc_population=700,
            households=140,
            women_count=350,
        )

        # Step 3: Verify MunicipalityCoverage auto-created and aggregated
        municipal = MunicipalityCoverage.objects.get(municipality=self.municipality)

        self.assertEqual(municipal.total_obc_communities, 3)
        self.assertEqual(municipal.barangay_attributed_population, 1500)
        self.assertEqual(municipal.households, 300)
        self.assertEqual(municipal.women_count, 750)
        self.assertIn("Barangay Alpha", municipal.key_barangays)
        self.assertIn("Barangay Beta", municipal.key_barangays)
        self.assertIn("Barangay Gamma", municipal.key_barangays)

        # Step 4: Update one Barangay OBC population
        obc2.estimated_obc_population = 400
        obc2.households = 80
        obc2.women_count = 200
        obc2.save()

        # Step 5: Verify MunicipalityCoverage auto-updated
        municipal.refresh_from_db()

        self.assertEqual(municipal.barangay_attributed_population, 1600)
        self.assertEqual(municipal.households, 320)
        self.assertEqual(municipal.women_count, 800)

        # Step 6: Delete one Barangay OBC
        obc1.delete()

        # Step 7: Verify MunicipalityCoverage recalculated
        municipal.refresh_from_db()

        self.assertEqual(municipal.total_obc_communities, 2)
        self.assertEqual(municipal.barangay_attributed_population, 1100)
        self.assertEqual(municipal.households, 220)
        self.assertEqual(municipal.women_count, 550)
        self.assertNotIn("Barangay Alpha", municipal.key_barangays)
        self.assertIn("Barangay Beta", municipal.key_barangays)
        self.assertIn("Barangay Gamma", municipal.key_barangays)

        # Step 8: Verify ProvinceCoverage also updated
        provincial = ProvinceCoverage.objects.get(province=self.province)

        self.assertEqual(provincial.total_municipalities, 1)
        self.assertEqual(provincial.total_obc_communities, 2)
        self.assertEqual(provincial.households, 220)
        self.assertEqual(provincial.women_count, 550)
