"""
Comprehensive Performance Analysis Script for OBCMS
Analyzes database queries, response times, and memory usage.
"""

import os
import sys
import django
import time
import tracemalloc
from decimal import Decimal
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from django.db import connection, reset_queries
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

# Enable query logging
settings.DEBUG = True

User = get_user_model()

class PerformanceAnalyzer:
    """Performance testing and analysis utilities."""

    def __init__(self):
        self.results = []

    def measure_operation(self, name, operation_func, *args, **kwargs):
        """Measure database queries, time, and memory for an operation."""
        reset_queries()
        tracemalloc.start()

        start_time = time.time()
        result = operation_func(*args, **kwargs)
        elapsed = (time.time() - start_time) * 1000  # ms

        query_count = len(connection.queries)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        analysis = {
            'name': name,
            'elapsed_ms': round(elapsed, 2),
            'query_count': query_count,
            'memory_peak_mb': round(peak / 1024 / 1024, 2),
            'status': 'PASS' if elapsed < 500 else 'SLOW'
        }

        self.results.append(analysis)
        return result, analysis

    def print_report(self):
        """Print comprehensive performance report."""
        print("\n" + "="*80)
        print("OBCMS PERFORMANCE ANALYSIS REPORT")
        print("="*80)

        print(f"\n{'Operation':<50} {'Time (ms)':<12} {'Queries':<10} {'Memory (MB)':<12} {'Status':<8}")
        print("-"*80)

        for result in self.results:
            print(f"{result['name']:<50} {result['elapsed_ms']:<12} {result['query_count']:<10} {result['memory_peak_mb']:<12} {result['status']:<8}")

        # Summary statistics
        total_ops = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        avg_time = sum(r['elapsed_ms'] for r in self.results) / total_ops if total_ops > 0 else 0
        avg_queries = sum(r['query_count'] for r in self.results) / total_ops if total_ops > 0 else 0

        print("-"*80)
        print(f"\nSUMMARY:")
        print(f"  Total Operations: {total_ops}")
        print(f"  Passed (< 500ms): {passed}/{total_ops} ({passed/total_ops*100:.1f}%)")
        print(f"  Average Time: {avg_time:.2f} ms")
        print(f"  Average Queries: {avg_queries:.1f}")
        print("\n" + "="*80)


def test_work_item_tree_operations():
    """Test WorkItem tree performance."""
    from common.work_item_model import WorkItem

    analyzer = PerformanceAnalyzer()

    # Test 1: Get ancestors (deep hierarchy)
    def create_deep_hierarchy():
        parent = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Deep Project"
        )
        current = parent
        for i in range(10):
            current = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Level {i}",
                parent=current
            )
        return current

    leaf = create_deep_hierarchy()

    def get_ancestors():
        return list(leaf.get_ancestors())

    _, analysis = analyzer.measure_operation(
        "WorkItem.get_ancestors() - 10 level hierarchy",
        get_ancestors
    )

    # Test 2: Get descendants (wide tree)
    def create_wide_tree():
        root = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Wide Project"
        )
        for i in range(50):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
                parent=root
            )
        return root

    root = create_wide_tree()

    def get_descendants():
        return list(root.get_descendants())

    _, analysis = analyzer.measure_operation(
        "WorkItem.get_descendants() - 50 children",
        get_descendants
    )

    # Test 3: Large tree navigation
    def create_large_tree():
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Large Project"
        )
        for i in range(20):
            activity = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_ACTIVITY,
                title=f"Activity {i}",
                parent=project
            )
            for j in range(10):
                WorkItem.objects.create(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Task {i}-{j}",
                    parent=activity
                )
        return project

    large_project = create_large_tree()

    def navigate_tree():
        descendants = large_project.get_descendants()
        return descendants.count()

    _, analysis = analyzer.measure_operation(
        "WorkItem large tree navigation - 220 nodes",
        navigate_tree
    )

    analyzer.print_report()
    WorkItem.objects.all().delete()


def test_database_query_patterns():
    """Test common query patterns for optimization."""
    from common.work_item_model import WorkItem

    analyzer = PerformanceAnalyzer()
    user = User.objects.first() or User.objects.create_user(
        username='perf_test',
        password='test123'
    )

    # Create test data
    items = []
    for i in range(100):
        item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=f"Query Test {i}",
            created_by=user
        )
        items.append(item)

    # Test 1: N+1 query without select_related
    def query_without_optimization():
        tasks = WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_TASK)[:20]
        return [task.created_by.username if task.created_by else None for task in tasks]

    _, analysis = analyzer.measure_operation(
        "Query 20 items WITHOUT select_related (N+1 issue)",
        query_without_optimization
    )

    # Test 2: Optimized query with select_related
    def query_with_optimization():
        tasks = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK
        ).select_related('created_by')[:20]
        return [task.created_by.username if task.created_by else None for task in tasks]

    _, analysis = analyzer.measure_operation(
        "Query 20 items WITH select_related (optimized)",
        query_with_optimization
    )

    # Test 3: Bulk retrieval
    def bulk_query():
        return list(WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_TASK
        ).values_list('title', flat=True))

    _, analysis = analyzer.measure_operation(
        "Bulk query 100 items with values_list",
        bulk_query
    )

    analyzer.print_report()
    WorkItem.objects.all().delete()


def test_calendar_operations():
    """Test calendar feed performance."""
    from common.services.calendar import build_calendar_payload
    from django.core.cache import cache

    analyzer = PerformanceAnalyzer()

    # Clear cache first
    cache.clear()

    # Test 1: Calendar payload (cold cache)
    def build_payload_cold():
        return build_calendar_payload()

    _, analysis = analyzer.measure_operation(
        "Calendar payload generation (cold cache)",
        build_payload_cold
    )

    # Test 2: Calendar payload (warm cache)
    def build_payload_warm():
        return build_calendar_payload()

    _, analysis = analyzer.measure_operation(
        "Calendar payload generation (warm cache)",
        build_payload_warm
    )

    analyzer.print_report()


def test_obc_community_operations():
    """Test OBC community data operations."""
    from communities.models import OBCCommunity, MunicipalityCoverage
    from common.models import Municipality, Province, Region, Barangay

    analyzer = PerformanceAnalyzer()

    # Create test data
    try:
        region = Region.objects.create(code="99", name="Test Region")
        province = Province.objects.create(code="9999", name="Test Province", region=region)
        municipality = Municipality.objects.create(
            code="999999",
            name="Test Municipality",
            province=province
        )

        # Create barangays and communities
        for i in range(10):
            barangay = Barangay.objects.create(
                code=f"99999900{i}",
                name=f"Test Barangay {i}",
                municipality=municipality
            )
            OBCCommunity.objects.create(
                barangay=barangay,
                name=f"OBC {i}",
                estimated_obc_population=100 + i
            )

        # Test: Municipality coverage sync
        def sync_coverage():
            coverage, _ = MunicipalityCoverage.objects.get_or_create(
                municipality=municipality
            )
            coverage.refresh_from_communities()
            return coverage

        _, analysis = analyzer.measure_operation(
            "MunicipalityCoverage sync for 10 communities",
            sync_coverage
        )

        analyzer.print_report()

    finally:
        # Cleanup
        if 'region' in locals():
            region.delete()


if __name__ == '__main__':
    print("\n🔍 Starting OBCMS Performance Analysis...\n")

    print("\n📊 Testing Work Item Tree Operations...")
    test_work_item_tree_operations()

    print("\n📊 Testing Database Query Patterns...")
    test_database_query_patterns()

    print("\n📊 Testing Calendar Operations...")
    test_calendar_operations()

    print("\n📊 Testing OBC Community Operations...")
    test_obc_community_operations()

    print("\n✅ Performance Analysis Complete!\n")
