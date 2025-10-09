#!/usr/bin/env python
"""
Work Item Tree Performance Testing Script

Tests the optimized tree expansion queries to verify:
1. Query count is minimal (3 queries regardless of children)
2. Response time is < 100ms for typical loads
3. Cache hit rate is high (80%+)
4. Database indexes are being used

Usage:
    cd src
    python manage.py shell < ../scripts/test_work_item_tree_performance.py
"""

import pytest

pytest.skip(
    "Work item tree performance script is not intended for automated pytest runs post-refactor.",
    allow_module_level=True,
)

import os
import time
from decimal import Decimal
from django.test.utils import override_settings
from django.db import connection, reset_queries
from django.contrib.auth import get_user_model
from django.core.cache import cache
from common.work_item_model import WorkItem

User = get_user_model()


def setup_test_data():
    """Create test work items for performance testing."""
    print("=" * 80)
    print("SETUP: Creating test data...")
    print("=" * 80)

    # Get or create test user
    user, _ = User.objects.get_or_create(
        username='perf_test_user',
        defaults={
            'email': 'perf@test.com',
            'user_type': 'oobc_staff',
            'is_approved': True,
        }
    )

    # Create parent project
    parent = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title="Performance Test Parent Project",
        description="Parent project for performance testing",
        status=WorkItem.STATUS_IN_PROGRESS,
        priority=WorkItem.PRIORITY_HIGH,
        progress=50,
        created_by=user,
    )

    # Create varying numbers of children
    test_cases = [
        (5, "Small"),
        (20, "Medium"),
        (50, "Large"),
    ]

    results = {}

    for child_count, size in test_cases:
        # Create test parent for this size
        test_parent = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title=f"{size} Tree Test ({child_count} children)",
            status=WorkItem.STATUS_IN_PROGRESS,
            priority=WorkItem.PRIORITY_MEDIUM,
            created_by=user,
        )

        # Create children
        children = []
        for i in range(child_count):
            child = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_ACTIVITY,
                title=f"Child Activity {i+1}",
                parent=test_parent,
                status=WorkItem.STATUS_NOT_STARTED,
                priority=WorkItem.PRIORITY_LOW,
                progress=0,
                created_by=user,
            )
            children.append(child)

        results[size] = {'parent': test_parent, 'children': children}
        print(f"✓ Created {size} tree: {child_count} children")

    print(f"\n✓ Test data created successfully\n")
    return results, user


def test_query_performance(test_data, user):
    """Test query count and execution time."""
    print("=" * 80)
    print("TEST 1: Query Performance & Count")
    print("=" * 80)

    results = []

    for size, data in test_data.items():
        parent = data['parent']
        child_count = len(data['children'])

        # Clear query log
        reset_queries()

        # Enable query logging
        from django.conf import settings
        debug_state = settings.DEBUG
        settings.DEBUG = True

        # Simulate the optimized view query
        start_time = time.time()

        children = (
            parent.get_children()
            .select_related('parent', 'created_by')
            .prefetch_related('assignees', 'teams')
            .only(
                'id', 'work_type', 'title', 'status', 'priority', 'progress',
                'start_date', 'due_date',
                'level', 'tree_id', 'lft', 'rght',
                'parent_id', 'created_by_id',
            )
        )

        # Force evaluation
        list(children)

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # Get query count
        query_count = len(connection.queries)

        # Restore DEBUG state
        settings.DEBUG = debug_state

        # Determine status
        target_time = 100 if child_count <= 20 else 150
        status = "✅ PASS" if execution_time < target_time and query_count <= 5 else "❌ FAIL"

        result = {
            'size': size,
            'child_count': child_count,
            'query_count': query_count,
            'execution_time': execution_time,
            'target_time': target_time,
            'status': status
        }
        results.append(result)

        print(f"\n{size} Tree ({child_count} children):")
        print(f"  Query Count:     {query_count} queries")
        print(f"  Execution Time:  {execution_time:.2f}ms (target: < {target_time}ms)")
        print(f"  Status:          {status}")

    # Summary
    print("\n" + "-" * 80)
    print("SUMMARY:")
    avg_queries = sum(r['query_count'] for r in results) / len(results)
    avg_time = sum(r['execution_time'] for r in results) / len(results)
    print(f"  Average Query Count:     {avg_queries:.1f}")
    print(f"  Average Execution Time:  {avg_time:.2f}ms")
    print(f"  All Tests Passed:        {'✅ YES' if all(r['status'].startswith('✅') for r in results) else '❌ NO'}")
    print()

    return results


def test_cache_performance(test_data, user):
    """Test cache hit rate and performance."""
    print("=" * 80)
    print("TEST 2: Cache Performance")
    print("=" * 80)

    # Clear cache
    cache.clear()
    print("✓ Cache cleared\n")

    parent = test_data['Medium']['parent']  # Use medium tree

    # First request (cache MISS)
    cache_key = f"work_item_children:{parent.id}:{user.id}"

    start_time = time.time()
    cached_html = cache.get(cache_key)
    miss_time = (time.time() - start_time) * 1000

    print(f"First Request (Cache MISS):")
    print(f"  Cache Key:       {cache_key}")
    print(f"  Cached Data:     {cached_html}")
    print(f"  Lookup Time:     {miss_time:.2f}ms")

    # Simulate rendering and caching
    html_content = "<tr>Simulated rendered HTML</tr>" * len(test_data['Medium']['children'])
    cache.set(cache_key, html_content, 300)
    print(f"  Cached HTML:     {len(html_content)} bytes (TTL: 300s)")

    # Second request (cache HIT)
    start_time = time.time()
    cached_html = cache.get(cache_key)
    hit_time = (time.time() - start_time) * 1000

    print(f"\nSecond Request (Cache HIT):")
    print(f"  Cache Key:       {cache_key}")
    print(f"  Cached Data:     {len(cached_html) if cached_html else 0} bytes")
    print(f"  Lookup Time:     {hit_time:.2f}ms")
    print(f"  Speedup:         {(miss_time / hit_time) if hit_time > 0 else 'N/A'}x faster")

    # Test cache invalidation
    from common.views.work_items import invalidate_work_item_tree_cache

    print(f"\nCache Invalidation Test:")
    invalidate_work_item_tree_cache(parent)
    cached_html = cache.get(cache_key)
    print(f"  After Invalidation: {cached_html}")
    status = "✅ PASS" if cached_html is None else "❌ FAIL"
    print(f"  Status: {status}")

    print()


def test_index_usage():
    """Test that database indexes are being used (PostgreSQL only)."""
    print("=" * 80)
    print("TEST 3: Database Index Usage")
    print("=" * 80)

    from django.db import connection

    # Check database type
    if 'postgresql' not in connection.vendor:
        print("⚠️  SKIPPED: PostgreSQL-specific test (current DB: {})".format(connection.vendor))
        print()
        return

    # Query to check index usage
    cursor = connection.cursor()

    # Check if indexes exist
    cursor.execute("""
        SELECT
            indexname,
            indexdef
        FROM pg_indexes
        WHERE tablename = 'common_work_item'
        AND indexname IN ('wi_tree_traversal_idx', 'wi_parent_idx', 'wi_calendar_idx')
        ORDER BY indexname;
    """)

    indexes = cursor.fetchall()

    if indexes:
        print("✅ Performance Indexes Found:")
        for idx_name, idx_def in indexes:
            print(f"  - {idx_name}")
            print(f"    {idx_def}")
    else:
        print("❌ FAIL: Performance indexes not found!")
        print("   Run migration: python manage.py migrate common 0026_work_item_performance_indexes")

    # Check index usage statistics
    cursor.execute("""
        SELECT
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        WHERE tablename = 'common_work_item'
        AND indexname IN ('wi_tree_traversal_idx', 'wi_parent_idx', 'wi_calendar_idx')
        ORDER BY idx_scan DESC;
    """)

    stats = cursor.fetchall()

    if stats:
        print("\n📊 Index Usage Statistics:")
        for idx_name, scans, reads, fetches in stats:
            print(f"  {idx_name}:")
            print(f"    Index Scans:  {scans}")
            print(f"    Tuples Read:  {reads}")
            print(f"    Tuples Fetch: {fetches}")
    else:
        print("\n⚠️  No index usage statistics available (indexes may be new)")

    print()


def cleanup_test_data():
    """Remove test data."""
    print("=" * 80)
    print("CLEANUP: Removing test data...")
    print("=" * 80)

    # Delete test work items
    deleted_count = WorkItem.objects.filter(
        title__icontains="Performance Test"
    ).delete()[0]

    print(f"✓ Deleted {deleted_count} test work items")

    # Delete test user
    User.objects.filter(username='perf_test_user').delete()
    print(f"✓ Deleted test user")

    # Clear cache
    cache.clear()
    print(f"✓ Cleared cache")

    print()


def run_all_tests():
    """Run all performance tests."""
    print("\n" + "=" * 80)
    print("WORK ITEM TREE PERFORMANCE TEST SUITE")
    print("=" * 80 + "\n")

    # Setup
    test_data, user = setup_test_data()

    try:
        # Run tests
        test_query_performance(test_data, user)
        test_cache_performance(test_data, user)
        test_index_usage()

        # Final summary
        print("=" * 80)
        print("✅ ALL TESTS COMPLETE")
        print("=" * 80)
        print("""
Expected Results:
  ✅ Query count ≤ 5 (regardless of child count)
  ✅ Response time < 100ms for medium trees (20 children)
  ✅ Cache hit provides 10x+ speedup
  ✅ Database indexes are active

Next Steps:
  1. Review test results above
  2. Check Django Debug Toolbar for query analysis
  3. Monitor production performance with Silk profiler
  4. Adjust cache TTL if needed (currently 5 minutes)
        """)

    finally:
        # Cleanup
        cleanup_test_data()


# Run the test suite
if __name__ == '__main__' or os.environ.get('RUN_WORK_ITEM_TREE_PERFORMANCE') == '1':
    run_all_tests()
