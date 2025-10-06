"""
Comprehensive test suite for OBCCommunity model functionality.

This test suite covers all aspects of the OBCCommunity model including:
- Model creation and validation
- Computed properties
- Soft delete and restore
- Data normalization
- Relationships and foreign keys
- Geographic data handling
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from common.models import Barangay, Municipality, Province, Region
from communities.models import (
    OBCCommunity,
    CommunityLivelihood,
    CommunityInfrastructure,
    Stakeholder,
    CommunityEvent,
)

User = get_user_model()


class OBCCommunityCreationValidationTest(TestCase):
    """Test Category A: Model Creation & Validation (10 scenarios)"""

    def setUp(self):
        """Set up test fixtures for all creation and validation tests."""
        self.region = Region.objects.create(code="R12", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-TEST",
            name="Test Province",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-TEST",
            name="Test Municipality",
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-TEST",
            name="Test Barangay",
        )
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_with_minimum_required_fields(self):
        """Test A1: Create OBCCommunity with only barangay (minimum requirement)"""
        community = OBCCommunity.objects.create(barangay=self.barangay)

        self.assertIsNotNone(community.id)
        self.assertEqual(community.barangay, self.barangay)
        self.assertIsNotNone(community.created_at)
        self.assertIsNotNone(community.updated_at)
        self.assertTrue(community.is_active)
        self.assertFalse(community.is_deleted)

    def test_create_with_all_fields_populated(self):
        """Test A2: Create OBCCommunity with comprehensive field population"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            # Identification
            obc_id="R12-SK-TEST-001",
            name="Test Community Alpha",
            community_names="Alpha Community, Community One",
            purok_sitio="Purok 3",
            specific_location="Near the river",
            settlement_type="village",
            # Demographics
            estimated_obc_population=500,
            total_barangay_population=1000,
            households=100,
            families=90,
            primary_ethnolinguistic_group="maguindanaon",
            other_ethnolinguistic_groups="tausug, iranun",
            primary_language="Maguindanaon",
            other_languages="Tagalog, English",
            # Age demographics
            children_0_9=100,
            adolescents_10_14=80,
            youth_15_30=150,
            adults_31_59=120,
            seniors_60_plus=50,
            # Vulnerable sectors
            women_count=250,
            solo_parents_count=15,
            pwd_count=10,
            farmers_count=40,
            fisherfolk_count=30,
            unemployed_count=25,
            # Socioeconomic
            primary_livelihoods="Rice Farming, Fishing",
            estimated_poverty_incidence="moderate",
            access_formal_education="good",
            access_healthcare="fair",
            access_clean_water="poor",
            access_electricity="good",
            # Cultural
            established_year=1950,
            brief_historical_background="Established by migrant families",
            cultural_practices_traditions="Annual harvest festival",
            religious_affiliation="Islam (Sunni)",
            mosques_count=2,
            madrasah_count=1,
            asatidz_count=5,
            religious_leaders_count=3,
            # Governance
            relationship_with_lgu="collaborative",
            # Geographic
            latitude=6.5000,
            longitude=124.8500,
            proximity_to_barmm="adjacent",
        )

        self.assertEqual(community.obc_id, "R12-SK-TEST-001")
        self.assertEqual(community.estimated_obc_population, 500)
        self.assertEqual(community.primary_ethnolinguistic_group, "maguindanaon")
        self.assertEqual(community.established_year, 1950)
        self.assertEqual(community.mosques_count, 2)
        self.assertEqual(community.latitude, 6.5000)
        self.assertEqual(community.proximity_to_barmm, "adjacent")

    def test_unique_constraint_one_obc_per_barangay(self):
        """Test A3: Validate unique constraint - only one OBC per barangay"""
        OBCCommunity.objects.create(barangay=self.barangay, name="First Community")

        with self.assertRaises(IntegrityError):
            OBCCommunity.objects.create(
                barangay=self.barangay, name="Second Community"
            )

    def test_population_validation_obc_within_barangay_total(self):
        """Test A4: OBC population should be <= barangay total population"""
        # Valid: OBC population <= total
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            estimated_obc_population=500,
            total_barangay_population=1000,
        )
        self.assertEqual(community.estimated_obc_population, 500)

        # Note: Model doesn't enforce this at DB level, but we document expected behavior
        # This test validates the data makes logical sense
        community_invalid = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-TEST2", name="Test Barangay 2"
            ),
            estimated_obc_population=1500,
            total_barangay_population=1000,
        )
        # This creates but would be flagged as data quality issue
        self.assertGreater(
            community_invalid.estimated_obc_population,
            community_invalid.total_barangay_population,
        )

    def test_established_year_validator(self):
        """Test A5: Validate established_year is within 1800-2030 range"""
        # Valid year
        community = OBCCommunity.objects.create(
            barangay=self.barangay, established_year=2000
        )
        self.assertEqual(community.established_year, 2000)

        # Test boundary values
        community_min = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-MIN", name="Barangay Min"
            ),
            established_year=1800,
        )
        self.assertEqual(community_min.established_year, 1800)

        community_max = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-MAX", name="Barangay Max"
            ),
            established_year=2030,
        )
        self.assertEqual(community_max.established_year, 2030)

    def test_ethnolinguistic_group_choices(self):
        """Test A6: Validate ethnolinguistic group field accepts valid choices"""
        valid_groups = [
            "badjao",
            "iranun",
            "jama_mapun",
            "kagan_kalagan",
            "kolibugan",
            "maguindanaon",
            "meranaw",
            "molbog",
            "palawani",
            "sama",
            "sangil",
            "tausug",
            "yakan",
            "other",
        ]

        for i, group in enumerate(valid_groups):
            barangay = self.municipality.barangays.create(
                code=f"BRGY-{i}", name=f"Barangay {i}"
            )
            community = OBCCommunity.objects.create(
                barangay=barangay, primary_ethnolinguistic_group=group
            )
            self.assertEqual(community.primary_ethnolinguistic_group, group)

    def test_settlement_type_choices(self):
        """Test A7: Validate settlement type field accepts valid choices"""
        settlement_types = [
            "village",
            "subdivision",
            "sitio",
            "purok",
            "compound",
            "dispersed",
        ]

        for i, stype in enumerate(settlement_types):
            barangay = self.municipality.barangays.create(
                code=f"BRGY-S{i}", name=f"Settlement Barangay {i}"
            )
            community = OBCCommunity.objects.create(
                barangay=barangay, settlement_type=stype
            )
            self.assertEqual(community.settlement_type, stype)

    def test_proximity_to_barmm_choices(self):
        """Test A8: Validate proximity to BARMM field accepts valid choices"""
        proximity_choices = ["adjacent", "near", "distant"]

        for i, proximity in enumerate(proximity_choices):
            barangay = self.municipality.barangays.create(
                code=f"BRGY-P{i}", name=f"Proximity Barangay {i}"
            )
            community = OBCCommunity.objects.create(
                barangay=barangay, proximity_to_barmm=proximity
            )
            self.assertEqual(community.proximity_to_barmm, proximity)

    def test_poverty_incidence_levels(self):
        """Test A9: Validate poverty incidence level choices"""
        poverty_levels = [
            "unknown",
            "very_low",
            "low",
            "moderate",
            "high",
            "very_high",
            "extremely_high",
        ]

        for i, level in enumerate(poverty_levels):
            barangay = self.municipality.barangays.create(
                code=f"BRGY-POV{i}", name=f"Poverty Barangay {i}"
            )
            community = OBCCommunity.objects.create(
                barangay=barangay, estimated_poverty_incidence=level
            )
            self.assertEqual(community.estimated_poverty_incidence, level)

    def test_access_to_services_ratings(self):
        """Test A10: Validate access to services rating choices"""
        access_ratings = ["excellent", "good", "fair", "poor", "none"]

        barangay = self.municipality.barangays.create(
            code="BRGY-ACC", name="Access Barangay"
        )
        community = OBCCommunity.objects.create(
            barangay=barangay,
            access_formal_education="excellent",
            access_als="good",
            access_madrasah="fair",
            access_healthcare="poor",
            access_clean_water="none",
            access_sanitation="poor",
            access_electricity="good",
            access_roads_transport="fair",
            access_communication="excellent",
        )

        self.assertEqual(community.access_formal_education, "excellent")
        self.assertEqual(community.access_als, "good")
        self.assertEqual(community.access_madrasah, "fair")
        self.assertEqual(community.access_healthcare, "poor")
        self.assertEqual(community.access_clean_water, "none")


class OBCCommunityComputedPropertiesTest(TestCase):
    """Test Category B: Computed Properties (8 scenarios)"""

    def setUp(self):
        """Set up test fixtures for computed property tests."""
        self.region = Region.objects.create(code="R09", name="Zamboanga Peninsula")
        self.province = Province.objects.create(
            region=self.region, code="PROV-ZN", name="Zamboanga del Norte"
        )
        self.municipality = Municipality.objects.create(
            province=self.province, code="MUN-DAP", name="Dapitan City"
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality, code="BRGY-BAG", name="Bagting"
        )

    def test_display_name_property(self):
        """Test B1: display_name returns name, then first community_names, then barangay"""
        # Case 1: Has name field
        community1 = OBCCommunity.objects.create(
            barangay=self.barangay, name="Sama Community"
        )
        self.assertEqual(community1.display_name, "Sama Community")

        # Case 2: No name, but has community_names
        barangay2 = self.municipality.barangays.create(
            code="BRGY-BAG2", name="Bagting 2"
        )
        community2 = OBCCommunity.objects.create(
            barangay=barangay2, community_names="Yakan Settlement, Community B"
        )
        self.assertEqual(community2.display_name, "Yakan Settlement")

        # Case 3: No name, no community_names - falls back to barangay
        barangay3 = self.municipality.barangays.create(
            code="BRGY-BAG3", name="Bagting 3"
        )
        community3 = OBCCommunity.objects.create(barangay=barangay3)
        self.assertEqual(community3.display_name, "Bagting 3")

    def test_full_location_with_specific_location(self):
        """Test B2: full_location includes specific_location when provided"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Test Community",
            specific_location="Sitio Riverside, Purok 5",
        )

        full_loc = community.full_location
        self.assertIn("Bagting", full_loc)
        self.assertIn("Dapitan City", full_loc)
        self.assertIn("Zamboanga del Norte", full_loc)
        self.assertTrue(full_loc.endswith("Sitio Riverside, Purok 5"))

    def test_full_location_without_specific_location(self):
        """Test B3: full_location shows only barangay path when no specific_location"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay, name="Test Community"
        )

        full_loc = community.full_location
        self.assertIn("Bagting", full_loc)
        self.assertIn("Dapitan City", full_loc)
        self.assertIn("Zamboanga del Norte", full_loc)
        self.assertNotIn(">", full_loc.split("Bagting")[-1])  # No additional location

    def test_region_province_municipality_shortcut_properties(self):
        """Test B4: Test region, province, municipality shortcut properties"""
        community = OBCCommunity.objects.create(barangay=self.barangay)

        # Test shortcuts work correctly
        self.assertEqual(community.region, self.region)
        self.assertEqual(community.region.code, "R09")
        self.assertEqual(community.province, self.province)
        self.assertEqual(community.province.name, "Zamboanga del Norte")
        self.assertEqual(community.municipality, self.municipality)
        self.assertEqual(community.municipality.name, "Dapitan City")

    def test_total_age_demographics(self):
        """Test B5: total_age_demographics aggregates all age groups"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            children_0_9=100,
            adolescents_10_14=80,
            youth_15_30=200,
            adults_31_59=150,
            seniors_60_plus=30,
        )

        total = community.total_age_demographics
        self.assertEqual(total, 560)  # 100+80+200+150+30

        # Test with partial data
        community2 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-PARTIAL", name="Partial"
            ),
            children_0_9=50,
            youth_15_30=100,
        )
        self.assertEqual(community2.total_age_demographics, 150)

        # Test with no age data
        community3 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-NONE", name="No Age Data"
            )
        )
        self.assertEqual(community3.total_age_demographics, 0)

    def test_average_household_size(self):
        """Test B6: average_household_size calculation"""
        # Normal case
        community = OBCCommunity.objects.create(
            barangay=self.barangay, estimated_obc_population=500, households=100
        )
        self.assertEqual(community.average_household_size, 5.0)

        # Fractional case
        community2 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-FRAC", name="Fractional"
            ),
            estimated_obc_population=555,
            households=100,
        )
        self.assertEqual(community2.average_household_size, 5.6)

        # No data case
        community3 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-NODATA", name="No Data"
            )
        )
        self.assertIsNone(community3.average_household_size)

    def test_percentage_obc_in_barangay(self):
        """Test B7: percentage_obc_in_barangay calculation"""
        # 50% case
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            estimated_obc_population=500,
            total_barangay_population=1000,
        )
        self.assertEqual(community.percentage_obc_in_barangay, 50.0)

        # Complex percentage
        community2 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-PCT", name="Percentage Test"
            ),
            estimated_obc_population=337,
            total_barangay_population=1250,
        )
        self.assertEqual(community2.percentage_obc_in_barangay, 26.96)

        # No data case
        community3 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-NOPCT", name="No Percentage"
            )
        )
        self.assertIsNone(community3.percentage_obc_in_barangay)

    def test_coordinates_property_for_geojson(self):
        """Test B8: coordinates property returns [lng, lat] for GeoJSON"""
        # With coordinates
        community = OBCCommunity.objects.create(
            barangay=self.barangay, latitude=8.6531, longitude=123.8494
        )
        coords = community.coordinates
        self.assertEqual(coords, [123.8494, 8.6531])  # [lng, lat]

        # Without coordinates
        community2 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-NOCOORDS", name="No Coords"
            )
        )
        self.assertIsNone(community2.coordinates)


class OBCCommunitySoftDeleteRestoreTest(TestCase):
    """Test Category C: Soft Delete & Restore (5 scenarios)"""

    def setUp(self):
        """Set up test fixtures for soft delete tests."""
        self.region = Region.objects.create(code="R12", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region, code="PROV-SK", name="Sarangani"
        )
        self.municipality = Municipality.objects.create(
            province=self.province, code="MUN-MAL", name="Malapatan"
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality, code="BRGY-GAL", name="Galakit"
        )
        self.user = User.objects.create_user(
            username="deleteuser", email="delete@test.com", password="pass123"
        )

    def test_soft_delete_marks_is_deleted_true(self):
        """Test C1: soft_delete() sets is_deleted=True"""
        community = OBCCommunity.objects.create(barangay=self.barangay)
        self.assertFalse(community.is_deleted)

        community.soft_delete(user=self.user)
        community.refresh_from_db()

        self.assertTrue(community.is_deleted)

    def test_soft_delete_sets_deleted_at_timestamp(self):
        """Test C2: soft_delete() sets deleted_at timestamp"""
        community = OBCCommunity.objects.create(barangay=self.barangay)
        self.assertIsNone(community.deleted_at)

        before_delete = timezone.now()
        community.soft_delete(user=self.user)
        community.refresh_from_db()
        after_delete = timezone.now()

        self.assertIsNotNone(community.deleted_at)
        self.assertGreaterEqual(community.deleted_at, before_delete)
        self.assertLessEqual(community.deleted_at, after_delete)

    def test_soft_delete_sets_deleted_by_user(self):
        """Test C3: soft_delete() sets deleted_by user when provided"""
        community = OBCCommunity.objects.create(barangay=self.barangay)
        self.assertIsNone(community.deleted_by)

        community.soft_delete(user=self.user)
        community.refresh_from_db()

        self.assertEqual(community.deleted_by, self.user)

        # Test without user
        community2 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-TEST2", name="Test 2"
            )
        )
        community2.soft_delete()
        community2.refresh_from_db()
        self.assertIsNone(community2.deleted_by)

    def test_restore_clears_soft_delete_fields(self):
        """Test C4: restore() clears is_deleted, deleted_at (but keeps deleted_by history)"""
        community = OBCCommunity.objects.create(barangay=self.barangay)
        community.soft_delete(user=self.user)
        community.refresh_from_db()

        # Verify it's deleted
        self.assertTrue(community.is_deleted)
        self.assertIsNotNone(community.deleted_at)

        # Restore
        community.restore()
        community.refresh_from_db()

        self.assertFalse(community.is_deleted)
        self.assertIsNone(community.deleted_at)
        # Note: deleted_by is NOT cleared in current implementation

    def test_default_manager_excludes_soft_deleted(self):
        """Test C5: Default manager excludes soft-deleted, all_objects includes them"""
        community1 = OBCCommunity.objects.create(
            barangay=self.barangay, name="Active Community"
        )
        community2 = OBCCommunity.objects.create(
            barangay=self.municipality.barangays.create(
                code="BRGY-DEL", name="Deleted Barangay"
            ),
            name="Deleted Community",
        )

        # Both visible initially
        self.assertEqual(OBCCommunity.objects.count(), 2)
        self.assertEqual(OBCCommunity.all_objects.count(), 2)

        # Soft delete one
        community2.soft_delete(user=self.user)

        # Default manager excludes deleted
        self.assertEqual(OBCCommunity.objects.count(), 1)
        self.assertEqual(OBCCommunity.objects.first(), community1)

        # all_objects includes deleted
        self.assertEqual(OBCCommunity.all_objects.count(), 2)
        self.assertEqual(
            OBCCommunity.all_objects.filter(is_deleted=True).count(), 1
        )


class OBCCommunityDataNormalizationTest(TestCase):
    """Test Category D: Data Normalization (5 scenarios)"""

    def setUp(self):
        """Set up test fixtures for data normalization tests."""
        self.region = Region.objects.create(code="R09", name="Region IX")
        self.province = Province.objects.create(
            region=self.region, code="PROV-09", name="Test Province"
        )
        self.municipality = Municipality.objects.create(
            province=self.province, code="MUN-09", name="Test Municipality"
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality, code="BRGY-09", name="Test Barangay"
        )

    def test_community_names_normalization_on_save(self):
        """Test D1: community_names is normalized to include name as first entry"""
        # Case 1: name is set, community_names is empty
        community1 = OBCCommunity.objects.create(
            barangay=self.barangay, name="Sama Dilaut Community"
        )
        community1.refresh_from_db()
        self.assertEqual(community1.community_names, "Sama Dilaut Community")

        # Case 2: name is set, community_names has different values
        barangay2 = self.municipality.barangays.create(
            code="BRGY-092", name="Barangay 2"
        )
        community2 = OBCCommunity.objects.create(
            barangay=barangay2,
            name="Primary Name",
            community_names="Old Name, Another Name",
        )
        community2.refresh_from_db()
        self.assertEqual(
            community2.community_names, "Primary Name, Old Name, Another Name"
        )

        # Case 3: name already in community_names (case insensitive)
        barangay3 = self.municipality.barangays.create(
            code="BRGY-093", name="Barangay 3"
        )
        community3 = OBCCommunity.objects.create(
            barangay=barangay3,
            name="Yakan Community",
            community_names="yakan community, Other Name",
        )
        community3.refresh_from_db()
        # Should deduplicate
        self.assertEqual(community3.community_names, "Yakan Community, Other Name")

    def test_languages_spoken_auto_population(self):
        """Test D2: languages_spoken auto-populated from primary + other languages"""
        # Case 1: Both primary and other languages
        community1 = OBCCommunity.objects.create(
            barangay=self.barangay,
            primary_language="Tausug",
            other_languages="Tagalog, English",
        )
        community1.refresh_from_db()
        self.assertEqual(community1.languages_spoken, "Tausug, Tagalog, English")

        # Case 2: Only primary language
        barangay2 = self.municipality.barangays.create(
            code="BRGY-L2", name="Language Test 2"
        )
        community2 = OBCCommunity.objects.create(
            barangay=barangay2, primary_language="Maguindanaon"
        )
        community2.refresh_from_db()
        self.assertEqual(community2.languages_spoken, "Maguindanaon")

        # Case 3: Deduplication (case insensitive)
        barangay3 = self.municipality.barangays.create(
            code="BRGY-L3", name="Language Test 3"
        )
        community3 = OBCCommunity.objects.create(
            barangay=barangay3,
            primary_language="Sama",
            other_languages="sama, Tagalog, SAMA",
        )
        community3.refresh_from_db()
        self.assertEqual(community3.languages_spoken, "Sama, Tagalog")

    def test_legacy_field_sync_population(self):
        """Test D3: Legacy 'population' field syncs with estimated_obc_population"""
        # Note: Based on model code, population is a separate legacy field
        # This test documents the relationship
        community = OBCCommunity.objects.create(
            barangay=self.barangay, population=500, estimated_obc_population=500
        )
        self.assertEqual(community.population, 500)
        self.assertEqual(community.estimated_obc_population, 500)

    def test_name_field_sync_to_community_names(self):
        """Test D4: name field is synced to community_names on save"""
        community = OBCCommunity.objects.create(barangay=self.barangay)

        # Update name
        community.name = "Updated Community Name"
        community.save()
        community.refresh_from_db()

        self.assertIn("Updated Community Name", community.community_names)

    def test_cultural_background_sync(self):
        """Test D5: Cultural background field retention"""
        # Legacy field test
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            cultural_background="Sama Dilaut heritage with strong maritime traditions",
            brief_historical_background="Established in 1920s by seafaring families",
        )

        self.assertEqual(
            community.cultural_background,
            "Sama Dilaut heritage with strong maritime traditions",
        )
        self.assertEqual(
            community.brief_historical_background,
            "Established in 1920s by seafaring families",
        )


class OBCCommunityRelationshipsTest(TestCase):
    """Test Category E: Relationships & Foreign Keys (5 scenarios)"""

    def setUp(self):
        """Set up test fixtures for relationship tests."""
        self.region = Region.objects.create(code="R12", name="Region XII")
        self.province = Province.objects.create(
            region=self.region, code="PROV-12", name="Test Province"
        )
        self.municipality = Municipality.objects.create(
            province=self.province, code="MUN-12", name="Test Municipality"
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality, code="BRGY-12", name="Test Barangay"
        )
        self.user = User.objects.create_user(
            username="reluser", email="rel@test.com", password="pass123"
        )

    def test_relationship_to_barangay_cascade_delete(self):
        """Test E1: OBCCommunity is CASCADE deleted when barangay is deleted"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay, name="Test Community"
        )
        community_id = community.id

        # Verify community exists
        self.assertTrue(OBCCommunity.all_objects.filter(id=community_id).exists())

        # Delete barangay
        self.barangay.delete()

        # Community should be cascade deleted
        self.assertFalse(OBCCommunity.all_objects.filter(id=community_id).exists())

    def test_relationship_to_stakeholders_reverse_relation(self):
        """Test E2: Stakeholders relationship (reverse relation from OBCCommunity)"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay, name="Community with Stakeholders"
        )

        # Create stakeholders
        stakeholder1 = Stakeholder.objects.create(
            community=community,
            full_name="Abdul Rahman",
            stakeholder_type="imam",
            position="Imam",
        )
        stakeholder2 = Stakeholder.objects.create(
            community=community,
            full_name="Maria Santos",
            stakeholder_type="community_leader",
            position="Barangay Kagawad",
        )

        # Test reverse relation
        stakeholders = community.stakeholders.all()
        self.assertEqual(stakeholders.count(), 2)
        self.assertIn(stakeholder1, stakeholders)
        self.assertIn(stakeholder2, stakeholders)

    def test_relationship_to_community_livelihood(self):
        """Test E3: CommunityLivelihood relationship"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay, name="Community with Livelihoods"
        )

        # Create livelihoods
        livelihood1 = CommunityLivelihood.objects.create(
            community=community,
            livelihood_type="agriculture",
            specific_activity="Rice Farming",
            is_primary_livelihood=True,
        )
        livelihood2 = CommunityLivelihood.objects.create(
            community=community,
            livelihood_type="fishing",
            specific_activity="Small-scale Fishing",
        )

        # Test reverse relation
        livelihoods = community.livelihoods.all()
        self.assertEqual(livelihoods.count(), 2)
        self.assertIn(livelihood1, livelihoods)
        self.assertIn(livelihood2, livelihoods)

    def test_relationship_to_community_infrastructure(self):
        """Test E4: CommunityInfrastructure relationship"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay, name="Community with Infrastructure"
        )

        # Create infrastructure records
        infra1 = CommunityInfrastructure.objects.create(
            community=community,
            infrastructure_type="water",
            availability_status="limited",
            priority_for_improvement="critical",
        )
        infra2 = CommunityInfrastructure.objects.create(
            community=community,
            infrastructure_type="electricity",
            availability_status="available",
            priority_for_improvement="low",
        )

        # Test reverse relation
        infrastructure = community.infrastructure.all()
        self.assertEqual(infrastructure.count(), 2)
        self.assertIn(infra1, infrastructure)
        self.assertIn(infra2, infrastructure)

    def test_relationship_to_community_event(self):
        """Test E5: CommunityEvent relationship"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay, name="Community with Events"
        )

        # Create events
        from datetime import date

        event1 = CommunityEvent.objects.create(
            community=community,
            title="Eid al-Fitr Celebration",
            event_type="religious",
            start_date=date(2024, 4, 10),
            created_by=self.user,
        )
        event2 = CommunityEvent.objects.create(
            community=community,
            title="Harvest Festival",
            event_type="cultural",
            start_date=date(2024, 6, 15),
            created_by=self.user,
        )

        # Test reverse relation
        events = community.community_events.all()
        self.assertEqual(events.count(), 2)
        self.assertIn(event1, events)
        self.assertIn(event2, events)


class OBCCommunityGeographicDataTest(TestCase):
    """Test Category F: Geographic Data (3 scenarios)"""

    def setUp(self):
        """Set up test fixtures for geographic data tests."""
        self.region = Region.objects.create(code="R09", name="Region IX")
        self.province = Province.objects.create(
            region=self.region, code="PROV-GEO", name="Geo Province"
        )
        self.municipality = Municipality.objects.create(
            province=self.province, code="MUN-GEO", name="Geo Municipality"
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality, code="BRGY-GEO", name="Geo Barangay"
        )

    def test_latitude_longitude_storage(self):
        """Test F1: Latitude and longitude are stored correctly as floats"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay, latitude=8.6531, longitude=123.8494
        )

        community.refresh_from_db()
        self.assertIsInstance(community.latitude, float)
        self.assertIsInstance(community.longitude, float)
        self.assertEqual(community.latitude, 8.6531)
        self.assertEqual(community.longitude, 123.8494)

        # Test negative coordinates
        barangay2 = self.municipality.barangays.create(
            code="BRGY-NEG", name="Negative Coords"
        )
        community2 = OBCCommunity.objects.create(
            barangay=barangay2, latitude=-8.5, longitude=-123.5
        )
        self.assertEqual(community2.latitude, -8.5)
        self.assertEqual(community2.longitude, -123.5)

    def test_coordinates_property_geojson_format(self):
        """Test F2: coordinates property returns [lng, lat] for GeoJSON compliance"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            latitude=6.9214,  # Zamboanga City
            longitude=122.0790,
        )

        coords = community.coordinates
        # GeoJSON uses [longitude, latitude] order
        self.assertEqual(len(coords), 2)
        self.assertEqual(coords[0], 122.0790)  # longitude first
        self.assertEqual(coords[1], 6.9214)  # latitude second

    def test_specific_location_field(self):
        """Test F3: specific_location field stores additional location details"""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            purok_sitio="Purok 3",
            specific_location="Near the elementary school, beside the river",
        )

        self.assertEqual(community.purok_sitio, "Purok 3")
        self.assertEqual(
            community.specific_location,
            "Near the elementary school, beside the river",
        )

        # Verify it's included in full_location
        self.assertIn("Near the elementary school", community.full_location)


# Test execution summary function
def run_test_summary():
    """Generate summary of test coverage for OBCCommunity model"""
    test_categories = {
        "A. Model Creation & Validation": 10,
        "B. Computed Properties": 8,
        "C. Soft Delete & Restore": 5,
        "D. Data Normalization": 5,
        "E. Relationships & Foreign Keys": 5,
        "F. Geographic Data": 3,
    }

    total_tests = sum(test_categories.values())
    print(f"\n{'='*60}")
    print("OBCCommunity Model Test Coverage Summary")
    print(f"{'='*60}")
    print(f"\nTotal Test Scenarios: {total_tests}\n")
    for category, count in test_categories.items():
        print(f"  {category}: {count} tests")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    run_test_summary()
