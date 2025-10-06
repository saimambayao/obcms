"""
Performance tests for auto-sync operations to identify N+1 query issues.

This test suite profiles database queries and execution time for:
1. MunicipalityCoverage.refresh_from_communities()
2. ProvinceCoverage.refresh_from_municipalities()
3. Signal-triggered sync operations
"""

import time
from decimal import Decimal
from unittest.mock import patch
from django.db import connection, reset_queries
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from common.models import Region, Province, Municipality, Barangay
from communities.models import OBCCommunity, MunicipalityCoverage, ProvinceCoverage

User = get_user_model()


@override_settings(
    DEBUG=True,  # Enable query logging
    SKIP_GEOCODING=True,  # Disable geocoding for performance tests
)
class AutoSyncPerformanceTest(TestCase):
    """Test suite for auto-sync performance analysis."""

    @classmethod
    def setUpTestData(cls):
        """Create test data hierarchy."""
        cls.user = User.objects.create_user(username="testuser", password="testpass")

        # Mock geocoding to prevent API calls
        with patch('common.services.geocoding.geocode_location'):
            # Create administrative hierarchy
            cls.region = Region.objects.create(
                code="12", name="Region XII (SOCCSKSARGEN)"
            )
            cls.province = Province.objects.create(
                code="1263", name="South Cotabato", region=cls.region
            )

            # Create 3 municipalities
            cls.municipalities = []
            for i in range(3):
                municipality = Municipality.objects.create(
                    code=f"126301{i}",
                    name=f"Test Municipality {i + 1}",
                    province=cls.province,
                )
                cls.municipalities.append(municipality)

                # Create 10 barangays per municipality
                for j in range(10):
                    barangay = Barangay.objects.create(
                        code=f"126301{i}00{j}",
                        name=f"Barangay {j + 1}",
                        municipality=municipality,
                    )

                    # Create OBC community for each barangay
                    OBCCommunity.objects.create(
                        barangay=barangay,
                        name=f"OBC {i}-{j}",
                        estimated_obc_population=100 + (i * 10) + j,
                        households=20 + i + j,
                        families=18 + i + j,
                        children_0_9=10 + i,
                        adolescents_10_14=8 + i,
                        youth_15_30=15 + i,
                        adults_31_59=25 + i,
                        seniors_60_plus=5 + i,
                        women_count=50 + i,
                        solo_parents_count=3 + i,
                        pwd_count=2 + i,
                        farmers_count=10 + i,
                        fisherfolk_count=5 + i,
                        unemployed_count=4 + i,
                        indigenous_peoples_count=1 + i,
                        idps_count=0,
                        migrants_transients_count=2 + i,
                        csos_count=1,
                        associations_count=2,
                        number_of_peoples_organizations=1,
                        number_of_cooperatives=1,
                        number_of_social_enterprises=0,
                        number_of_micro_enterprises=3 + i,
                        number_of_unbanked_obc=30 + i,
                        mosques_count=1,
                        madrasah_count=1,
                        asatidz_count=2,
                        religious_leaders_count=3,
                    )

            # Total created: 3 municipalities × 10 barangays = 30 communities

    def test_01_baseline_query_count(self):
        """Establish baseline query count without optimization."""
        municipality = self.municipalities[0]

        reset_queries()
        start_time = time.time()

        # Test current implementation
        coverage, _ = MunicipalityCoverage.objects.get_or_create(
            municipality=municipality
        )
        coverage.refresh_from_communities()

        duration = time.time() - start_time
        query_count = len(connection.queries)

        print(f"\n{'='*60}")
        print("BASELINE: MunicipalityCoverage.refresh_from_communities()")
        print(f"{'='*60}")
        print(f"Queries executed: {query_count}")
        print(f"Execution time: {duration:.4f} seconds")
        print(f"Communities synced: 10")
        print(f"{'='*60}\n")

        # Print first 10 queries to analyze
        print("First 10 queries:")
        for i, query in enumerate(connection.queries[:10], 1):
            sql = query["sql"][:150] + "..." if len(query["sql"]) > 150 else query["sql"]
            print(f"{i}. [{query['time']}s] {sql}")

        # Assertions (before optimization)
        # Current implementation likely has N+1 issues
        # Expected: 3-5 queries (optimal)
        # Actual: likely 10+ queries (one per community or field)
        print(f"\n⚠️  Expected queries: 3-5 (optimal)")
        print(f"⚠️  Actual queries: {query_count}")

        if query_count > 5:
            print(f"❌ N+1 query issue detected! {query_count - 5} extra queries")

    def test_02_provincial_sync_baseline(self):
        """Test provincial sync baseline performance."""
        province = self.province

        reset_queries()
        start_time = time.time()

        coverage, _ = ProvinceCoverage.objects.get_or_create(province=province)
        coverage.refresh_from_municipalities()

        duration = time.time() - start_time
        query_count = len(connection.queries)

        print(f"\n{'='*60}")
        print("BASELINE: ProvinceCoverage.refresh_from_municipalities()")
        print(f"{'='*60}")
        print(f"Queries executed: {query_count}")
        print(f"Execution time: {duration:.4f} seconds")
        print(f"Municipalities synced: 3")
        print(f"{'='*60}\n")

        # Print queries
        print("Queries executed:")
        for i, query in enumerate(connection.queries, 1):
            sql = query["sql"][:150] + "..." if len(query["sql"]) > 150 else query["sql"]
            print(f"{i}. [{query['time']}s] {sql}")

        print(f"\n⚠️  Expected queries: 3-4 (optimal)")
        print(f"⚠️  Actual queries: {query_count}")

    def test_03_signal_triggered_sync_performance(self):
        """Test signal-triggered sync when creating a new community."""
        municipality = self.municipalities[0]
        barangay = municipality.barangays.first()

        # Create MunicipalityCoverage first
        MunicipalityCoverage.sync_for_municipality(municipality)

        reset_queries()
        start_time = time.time()

        # Create a new community (triggers signal)
        new_community = OBCCommunity.objects.create(
            barangay=barangay,
            name="New OBC Community",
            estimated_obc_population=150,
            households=30,
        )

        duration = time.time() - start_time
        query_count = len(connection.queries)

        print(f"\n{'='*60}")
        print("SIGNAL TRIGGERED SYNC: post_save -> sync_for_municipality()")
        print(f"{'='*60}")
        print(f"Queries executed: {query_count}")
        print(f"Execution time: {duration:.4f} seconds")
        print(f"{'='*60}\n")

        # Print queries
        print("Queries executed:")
        for i, query in enumerate(connection.queries, 1):
            sql = query["sql"][:200] + "..." if len(query["sql"]) > 200 else query["sql"]
            print(f"{i}. [{query['time']}s] {sql}")

        # Clean up
        new_community.delete()

    def test_04_bulk_create_performance(self):
        """Test performance when bulk creating communities."""
        municipality = self.municipalities[1]
        barangays = list(municipality.barangays.all()[:5])

        # Clear existing communities
        OBCCommunity.objects.filter(barangay__in=barangays).delete()

        reset_queries()
        start_time = time.time()

        # Bulk create 5 communities (each triggers signal)
        communities = []
        for i, barangay in enumerate(barangays):
            community = OBCCommunity(
                barangay=barangay,
                name=f"Bulk OBC {i}",
                estimated_obc_population=100 + i,
                households=20 + i,
            )
            communities.append(community)

        OBCCommunity.objects.bulk_create(communities)

        # Note: bulk_create doesn't trigger signals
        # Manual sync needed
        MunicipalityCoverage.sync_for_municipality(municipality)

        duration = time.time() - start_time
        query_count = len(connection.queries)

        print(f"\n{'='*60}")
        print("BULK CREATE: 5 communities + manual sync")
        print(f"{'='*60}")
        print(f"Queries executed: {query_count}")
        print(f"Execution time: {duration:.4f} seconds")
        print(f"{'='*60}\n")

        print(f"⚠️  Bulk create doesn't trigger signals")
        print(f"⚠️  Manual sync required: MunicipalityCoverage.sync_for_municipality()")

    def test_05_analyze_aggregate_query(self):
        """Analyze the aggregate query in refresh_from_communities."""
        municipality = self.municipalities[0]

        reset_queries()

        # Test aggregate query directly
        from django.db.models import Sum
        from communities.models import AGGREGATED_NUMERIC_FIELDS

        communities = OBCCommunity.objects.filter(
            barangay__municipality=municipality, is_deleted=False
        )

        # Current implementation (inefficient?)
        aggregates = communities.aggregate(
            **{f"{field}__sum": Sum(field) for field in AGGREGATED_NUMERIC_FIELDS}
        )

        query_count = len(connection.queries)

        print(f"\n{'='*60}")
        print("AGGREGATE QUERY ANALYSIS")
        print(f"{'='*60}")
        print(f"Fields aggregated: {len(AGGREGATED_NUMERIC_FIELDS)}")
        print(f"Queries executed: {query_count}")
        print(f"{'='*60}\n")

        # Print the SQL
        if connection.queries:
            sql = connection.queries[-1]["sql"]
            print("Generated SQL:")
            print(sql[:500] + "..." if len(sql) > 500 else sql)

        # This should be 1 query
        self.assertEqual(
            query_count, 1, "Aggregate should execute in a single query"
        )

    def test_06_full_cascade_sync_performance(self):
        """Test full cascade: Community -> Municipality -> Province."""
        municipality = self.municipalities[0]
        barangay = municipality.barangays.first()

        # Ensure coverage exists
        MunicipalityCoverage.sync_for_municipality(municipality)
        ProvinceCoverage.sync_for_province(self.province)

        reset_queries()
        start_time = time.time()

        # Update an existing community (triggers cascade)
        community = OBCCommunity.objects.get(barangay=barangay)
        community.estimated_obc_population = 500
        community.save()

        duration = time.time() - start_time
        query_count = len(connection.queries)

        print(f"\n{'='*60}")
        print("CASCADE SYNC: Community save -> Municipality -> Province")
        print(f"{'='*60}")
        print(f"Queries executed: {query_count}")
        print(f"Execution time: {duration:.4f} seconds")
        print(f"{'='*60}\n")

        # Print queries
        print("Queries executed:")
        for i, query in enumerate(connection.queries, 1):
            sql = query["sql"][:200] + "..." if len(query["sql"]) > 200 else query["sql"]
            print(f"{i}. [{query['time']}s] {sql}")

        print(
            f"\n⚠️  Cascade triggers 2 syncs: Municipal + Provincial"
        )
        print(f"⚠️  Expected queries: ~8-10 (optimal)")
        print(f"⚠️  Actual queries: {query_count}")


@override_settings(DEBUG=True)
class OptimizedSyncPerformanceTest(TestCase):
    """Test suite for optimized sync implementation."""

    # This will contain tests for the optimized version
    # after we implement the fixes

    def test_optimized_municipal_sync(self):
        """Test optimized municipal sync (to be implemented)."""
        # TODO: Implement after optimization
        self.skipTest("Optimization not yet implemented")

    def test_optimized_provincial_sync(self):
        """Test optimized provincial sync (to be implemented)."""
        # TODO: Implement after optimization
        self.skipTest("Optimization not yet implemented")


class SyncPerformanceBenchmark(TestCase):
    """Benchmark suite for comparing before/after optimization."""

    def test_benchmark_comparison(self):
        """Compare baseline vs optimized performance."""
        # TODO: Implement comprehensive benchmark
        self.skipTest("Benchmarking suite to be implemented")
