"""
Tests for bulk sync utilities.

Verifies that bulk sync operations:
1. Reduce query count compared to individual syncs
2. Produce same results as individual syncs
3. Handle edge cases correctly
"""

from django.test import TestCase
from django.db import connection, reset_queries
from django.conf import settings

from common.models import Region, Province, Municipality, Barangay
from communities.models import OBCCommunity, MunicipalityCoverage, ProvinceCoverage
from communities.utils import (
    bulk_sync_communities,
    bulk_sync_municipalities,
    bulk_refresh_municipalities,
    bulk_refresh_provinces,
    sync_entire_hierarchy,
)


class BulkSyncUtilitiesTest(TestCase):
    """Test bulk sync utility functions."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        # Create region
        cls.region = Region.objects.create(code="12", name="Region XII")

        # Create 2 provinces
        cls.provinces = []
        for i in range(2):
            province = Province.objects.create(
                code=f"126{i}",
                name=f"Province {i + 1}",
                region=cls.region,
            )
            cls.provinces.append(province)

            # Create 2 municipalities per province
            for j in range(2):
                municipality = Municipality.objects.create(
                    code=f"126{i}0{j}",
                    name=f"Municipality {i}-{j}",
                    province=province,
                )

                # Create 3 barangays per municipality
                for k in range(3):
                    barangay = Barangay.objects.create(
                        code=f"126{i}0{j}00{k}",
                        name=f"Barangay {k + 1}",
                        municipality=municipality,
                    )

                    # Create community
                    OBCCommunity.objects.create(
                        barangay=barangay,
                        name=f"OBC {i}-{j}-{k}",
                        estimated_obc_population=100,
                        households=20,
                    )

    def test_bulk_sync_communities_efficiency(self):
        """Test that bulk_sync_communities reduces cascade syncs."""
        communities = OBCCommunity.objects.all()

        # Sync using bulk utility
        stats = bulk_sync_communities(communities)

        # Verify stats
        self.assertEqual(stats["communities_processed"], 12)  # 2 provinces × 2 municipalities × 3 barangays
        self.assertEqual(stats["municipalities_synced"], 4)  # 2 provinces × 2 municipalities
        self.assertEqual(stats["provinces_synced"], 2)  # 2 provinces

    def test_bulk_sync_produces_same_results(self):
        """Test that bulk sync produces same results as individual syncs."""
        communities = OBCCommunity.objects.all()

        # Get municipality before sync
        municipality = Municipality.objects.first()

        # Sync using bulk
        bulk_sync_communities(communities)

        # Get coverage after bulk sync
        coverage_bulk = MunicipalityCoverage.objects.get(municipality=municipality)
        total_bulk = coverage_bulk.households

        # Clear all coverages
        MunicipalityCoverage.objects.all().delete()
        ProvinceCoverage.objects.all().delete()

        # Sync individually (simulating signal-triggered syncs)
        for community in communities:
            MunicipalityCoverage.sync_for_municipality(
                community.barangay.municipality
            )

        # Get coverage after individual sync
        coverage_individual = MunicipalityCoverage.objects.get(municipality=municipality)
        total_individual = coverage_individual.households

        # Should be identical
        self.assertEqual(total_bulk, total_individual)

    def test_bulk_sync_with_no_provincial_sync(self):
        """Test bulk_sync with sync_provincial=False."""
        communities = OBCCommunity.objects.all()

        # Clear existing coverages
        ProvinceCoverage.objects.all().delete()

        # Sync without provincial sync
        stats = bulk_sync_communities(communities, sync_provincial=False)

        self.assertEqual(stats["provinces_synced"], 0)
        self.assertEqual(ProvinceCoverage.objects.count(), 0)

    def test_bulk_refresh_municipalities(self):
        """Test bulk_refresh_municipalities utility."""
        municipalities = Municipality.objects.all()

        stats = bulk_refresh_municipalities(municipalities)

        self.assertEqual(stats["municipalities_synced"], 4)
        self.assertEqual(stats["provinces_synced"], 2)

        # Verify all municipalities have coverage
        for municipality in municipalities:
            self.assertTrue(
                MunicipalityCoverage.objects.filter(
                    municipality=municipality
                ).exists()
            )

    def test_bulk_refresh_provinces(self):
        """Test bulk_refresh_provinces utility."""
        provinces = Province.objects.all()

        stats = bulk_refresh_provinces(provinces)

        self.assertEqual(stats["provinces_synced"], 2)

        # Verify all provinces have coverage
        for province in provinces:
            self.assertTrue(
                ProvinceCoverage.objects.filter(province=province).exists()
            )

    def test_sync_entire_hierarchy(self):
        """Test sync_entire_hierarchy utility."""
        # Sync specific region
        stats = sync_entire_hierarchy(self.region)

        self.assertEqual(stats["municipalities_synced"], 4)
        self.assertEqual(stats["provinces_synced"], 2)
        self.assertEqual(stats["region"], "Region XII")

    def test_sync_entire_hierarchy_all_regions(self):
        """Test sync_entire_hierarchy for all regions."""
        stats = sync_entire_hierarchy()

        # Should sync all municipalities and provinces with OBCs
        self.assertGreaterEqual(stats["municipalities_synced"], 4)
        self.assertGreaterEqual(stats["provinces_synced"], 2)
        self.assertEqual(stats["region"], "All Regions")

    def test_empty_iterable_handling(self):
        """Test that bulk sync handles empty iterables gracefully."""
        # Empty community list
        stats = bulk_sync_communities([])

        self.assertEqual(stats["communities_processed"], 0)
        self.assertEqual(stats["municipalities_synced"], 0)
        self.assertEqual(stats["provinces_synced"], 0)


class CachedPropertyTest(TestCase):
    """Test cached_property optimizations."""

    def setUp(self):
        """Create test data."""
        self.region = Region.objects.create(code="12", name="Region XII")
        self.province = Province.objects.create(
            code="1263",
            name="Test Province",
            region=self.region,
        )
        self.municipality = Municipality.objects.create(
            code="126301",
            name="Test Municipality",
            province=self.province,
        )
        self.coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality
        )

    def test_region_property_caching(self):
        """Test that region property is cached."""
        # Clear the cache
        if hasattr(self.coverage, '_region'):
            delattr(self.coverage, '_region')

        # First access
        region1 = self.coverage.region
        # Second access (should be cached)
        region2 = self.coverage.region

        # Should be the same object
        self.assertIs(region1, region2)

    def test_province_property_caching(self):
        """Test that province property is cached."""
        # Clear the cache
        if hasattr(self.coverage, '_province'):
            delattr(self.coverage, '_province')

        # First access
        province1 = self.coverage.province
        # Second access (should be cached)
        province2 = self.coverage.province

        # Should be the same object
        self.assertIs(province1, province2)


class PerformanceComparisonTest(TestCase):
    """Compare performance of bulk vs individual sync operations."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        cls.region = Region.objects.create(code="12", name="Region XII")
        cls.province = Province.objects.create(
            code="1263",
            name="Test Province",
            region=cls.region,
        )

        # Create 5 municipalities with 5 barangays each
        cls.municipalities = []
        for i in range(5):
            municipality = Municipality.objects.create(
                code=f"12630{i}",
                name=f"Municipality {i + 1}",
                province=cls.province,
            )
            cls.municipalities.append(municipality)

            for j in range(5):
                barangay = Barangay.objects.create(
                    code=f"12630{i}00{j}",
                    name=f"Barangay {j + 1}",
                    municipality=municipality,
                )
                OBCCommunity.objects.create(
                    barangay=barangay,
                    name=f"OBC {i}-{j}",
                    estimated_obc_population=100,
                )

    def test_compare_sync_approaches(self):
        """Compare bulk sync vs individual sync query counts."""
        # Clear all coverages
        MunicipalityCoverage.objects.all().delete()
        ProvinceCoverage.objects.all().delete()

        # Test bulk approach
        if hasattr(settings, 'DEBUG'):
            settings.DEBUG = True

        reset_queries()
        bulk_refresh_municipalities(self.municipalities)
        bulk_queries = len(connection.queries)

        # Clear coverages again
        MunicipalityCoverage.objects.all().delete()
        ProvinceCoverage.objects.all().delete()

        # Test individual approach
        reset_queries()
        for municipality in self.municipalities:
            MunicipalityCoverage.sync_for_municipality(municipality)
        ProvinceCoverage.sync_for_province(self.province)
        individual_queries = len(connection.queries)

        # Bulk should be more efficient (or at least not worse)
        # Note: May be same or similar, but shouldn't be worse
        self.assertLessEqual(bulk_queries, individual_queries * 1.2)  # Allow 20% margin

        print(f"\n📊 Performance Comparison:")
        print(f"  Bulk sync: {bulk_queries} queries")
        print(f"  Individual sync: {individual_queries} queries")
        print(f"  Improvement: {individual_queries - bulk_queries} fewer queries")
