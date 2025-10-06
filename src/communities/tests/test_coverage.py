from django.contrib.auth import get_user_model
from django.test import TestCase

from common.models import Barangay, Municipality, Province, Region

from ..models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage
from ..serializers import MunicipalityCoverageSerializer

User = get_user_model()


class MunicipalityCoverageModelTest(TestCase):
    """Tests for the MunicipalityCoverage model helpers."""

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
            username="encoder",
            password="testpass123",
            user_type="oobc_staff",
        )
        self.coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            total_obc_communities=3,
            estimated_obc_population=2500,
            key_barangays="Barangay A, Barangay B",
            created_by=self.user,
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.coverage),
            "Isulan Bangsamoro Coverage",
        )

    def test_region_and_province_properties(self):
        self.assertEqual(self.coverage.region, self.region)
        self.assertEqual(self.coverage.province, self.province)

    def test_display_name_property(self):
        self.assertEqual(
            self.coverage.display_name,
            "Isulan, Sultan Kudarat",
        )

    def test_soft_delete_and_restore_cycle(self):
        self.coverage.soft_delete()
        self.coverage.refresh_from_db()

        self.assertTrue(self.coverage.is_deleted)
        self.assertIsNotNone(self.coverage.deleted_at)
        self.assertFalse(
            MunicipalityCoverage.objects.filter(pk=self.coverage.pk).exists()
        )
        self.assertTrue(
            MunicipalityCoverage.all_objects.filter(
                pk=self.coverage.pk, is_deleted=True
            ).exists()
        )

        self.coverage.restore()
        self.coverage.refresh_from_db()

        self.assertFalse(self.coverage.is_deleted)
        self.assertIsNone(self.coverage.deleted_at)
        self.assertTrue(
            MunicipalityCoverage.objects.filter(pk=self.coverage.pk).exists()
        )


class MunicipalityCoverageSerializerTest(TestCase):
    """Ensure the serializer exposes derived attributes."""

    def setUp(self):
        region = Region.objects.create(code="IX", name="Zamboanga Peninsula")
        province = Province.objects.create(
            region=region, code="PROV-002", name="Zamboanga City"
        )
        municipality = Municipality.objects.create(
            province=province,
            code="MUN-002",
            name="Zamboanga City",
            municipality_type="independent_city",
        )
        self.coverage = MunicipalityCoverage.objects.create(
            municipality=municipality,
            total_obc_communities=5,
            estimated_obc_population=5400,
            key_barangays="Barangay Baliwasan",
        )

    def test_serializer_output(self):
        serializer = MunicipalityCoverageSerializer(instance=self.coverage)
        data = serializer.data
        self.assertEqual(data["municipality_name"], "Zamboanga City")
        self.assertEqual(data["province_name"], "Zamboanga City")
        self.assertEqual(data["region_name"], "Zamboanga Peninsula")
        self.assertEqual(data["total_obc_communities"], 5)
        self.assertTrue(data["auto_sync"])


class MunicipalityCoverageSyncTest(TestCase):
    """Validate automatic aggregation between barangay communities and coverage."""

    def setUp(self):
        self.region = Region.objects.create(code="BAR", name="BARMM Edge")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-123",
            name="Test Province",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-123",
            name="Sample Municipality",
        )
        self.barangay_a = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Barangay Uno",
        )
        self.barangay_b = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Barangay Dos",
        )

    def tearDown(self):
        from municipal_profiles.models import OBCCommunityHistory

        OBCCommunityHistory.objects.all().delete()

    def test_coverage_created_and_updated_from_communities(self):
        # Initial community creation should spawn coverage automatically
        OBCCommunity.objects.create(
            barangay=self.barangay_a,
            community_names="Community A",
            estimated_obc_population=150,
            households=30,
            women_count=60,
        )

        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertTrue(coverage.auto_sync)
        self.assertEqual(coverage.total_obc_communities, 1)
        self.assertIsNone(coverage.estimated_obc_population)
        self.assertEqual(coverage.households, 30)
        self.assertEqual(coverage.women_count, 60)
        self.assertIn("Barangay Uno", coverage.key_barangays)

        OBCCommunity.objects.create(
            barangay=self.barangay_b,
            community_names="Community B",
            estimated_obc_population=200,
            households=40,
            women_count=80,
        )

        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 2)
        self.assertIsNone(coverage.estimated_obc_population)
        self.assertEqual(coverage.households, 70)
        self.assertEqual(coverage.women_count, 140)
        self.assertIn("Barangay Dos", coverage.key_barangays)

        # Removing a community should resync totals
        coverage.auto_sync = True
        coverage.save(update_fields=["auto_sync"])
        OBCCommunity.objects.filter(barangay=self.barangay_a).delete()
        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 1)
        self.assertIsNone(coverage.estimated_obc_population)
        self.assertEqual(coverage.households, 40)
        self.assertEqual(coverage.women_count, 80)

    def test_auto_sync_can_be_disabled(self):
        OBCCommunity.objects.create(
            barangay=self.barangay_a,
            community_names="Community A",
            estimated_obc_population=120,
        )
        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        MunicipalityCoverage.objects.filter(pk=coverage.pk).update(
            auto_sync=False,
            total_obc_communities=99,
            estimated_obc_population=9999,
            key_barangays="Custom Entry",
        )
        coverage.refresh_from_db()
        self.assertFalse(coverage.auto_sync)

        OBCCommunity.objects.create(
            barangay=self.barangay_b,
            community_names="Community B",
            estimated_obc_population=80,
        )

        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 99)
        self.assertEqual(coverage.estimated_obc_population, 9999)
        self.assertEqual(coverage.key_barangays, "Custom Entry")


class ProvinceCoverageAggregationTest(TestCase):
    """Ensure provincial coverage aggregates municipal data correctly."""

    def setUp(self):
        self.region = Region.objects.create(code="R12", name="SOCCSKSARGEN")
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-777",
            name="Sample Province",
        )
        self.municipality_a = Municipality.objects.create(
            province=self.province,
            code="MUN-A",
            name="Municipality A",
        )
        self.municipality_b = Municipality.objects.create(
            province=self.province,
            code="MUN-B",
            name="Municipality B",
        )

        self.coverage_a = MunicipalityCoverage.objects.create(
            municipality=self.municipality_a,
            total_obc_communities=3,
            estimated_obc_population=450,
            households=90,
            women_count=180,
        )
        self.coverage_b = MunicipalityCoverage.objects.create(
            municipality=self.municipality_b,
            total_obc_communities=2,
            estimated_obc_population=250,
            households=50,
            women_count=110,
        )

    def test_sync_for_province_aggregates_totals(self):
        coverage = ProvinceCoverage.sync_for_province(self.province)
        coverage.refresh_from_db()

        self.assertEqual(coverage.total_municipalities, 2)
        self.assertEqual(coverage.total_obc_communities, 5)
        self.assertIsNone(coverage.estimated_obc_population)
        self.assertEqual(coverage.households, 140)
        self.assertIn(self.municipality_a.name, coverage.key_municipalities)
        self.assertIn(self.municipality_b.name, coverage.key_municipalities)

        MunicipalityCoverage.objects.filter(pk=self.coverage_a.pk).update(
            total_obc_communities=4,
            estimated_obc_population=600,
        )
        MunicipalityCoverage.objects.filter(pk=self.coverage_b.pk).update(
            estimated_obc_population=300,
            households=55,
        )

        ProvinceCoverage.sync_for_province(self.province)
        coverage.refresh_from_db()

        self.assertEqual(coverage.total_obc_communities, 6)
        self.assertIsNone(coverage.estimated_obc_population)
        self.assertEqual(coverage.households, 145)

    def test_auto_sync_respected(self):
        coverage = ProvinceCoverage.sync_for_province(self.province)
        coverage.auto_sync = False
        coverage.estimated_obc_population = 700
        coverage.save(update_fields=["auto_sync", "estimated_obc_population"])

        MunicipalityCoverage.objects.filter(pk=self.coverage_a.pk).update(
            total_obc_communities=10,
            estimated_obc_population=1000,
        )
        ProvinceCoverage.sync_for_province(self.province)

        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 5)
        self.assertEqual(coverage.estimated_obc_population, 700)

        coverage.auto_sync = True
        coverage.save(update_fields=["auto_sync"])
        ProvinceCoverage.sync_for_province(self.province)
        coverage.refresh_from_db()
        self.assertEqual(coverage.total_obc_communities, 12)
        self.assertIsNone(coverage.estimated_obc_population)
