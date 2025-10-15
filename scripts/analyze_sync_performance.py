"""
Quick performance analysis script for auto-sync operations.
Run this from the project root to analyze N+1 query issues.

Usage:
    python analyze_sync_performance.py
"""

import os
import sys
import django
import time

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
django.setup()

from django.db import connection, reset_queries
from django.conf import settings
from communities.models import MunicipalityCoverage, ProvinceCoverage, OBCCommunity
from common.models import Municipality, Province

# Enable query logging
settings.DEBUG = True


def analyze_municipal_sync():
    """Analyze MunicipalityCoverage.refresh_from_communities()."""
    print("\n" + "="*70)
    print("ANALYZING: MunicipalityCoverage.refresh_from_communities()")
    print("="*70)

    # Find a municipality with OBC communities
    municipality = Municipality.objects.filter(
        barangays__obc_communities__isnull=False
    ).first()

    if not municipality:
        print("❌ No municipalities with OBC communities found")
        return

    community_count = OBCCommunity.objects.filter(
        barangay__municipality=municipality
    ).count()

    print(f"Municipality: {municipality.name}, {municipality.province.name}")
    print(f"OBC Communities: {community_count}")

    # Get or create coverage
    coverage, _ = MunicipalityCoverage.objects.get_or_create(
        municipality=municipality
    )

    # Reset query counter
    reset_queries()
    start_time = time.time()

    # Execute the sync
    coverage.refresh_from_communities()

    duration = time.time() - start_time
    query_count = len(connection.queries)

    print(f"\n📊 RESULTS:")
    print(f"  Queries executed: {query_count}")
    print(f"  Execution time: {duration:.4f}s")
    print(f"  Avg time per query: {(duration/query_count)*1000:.2f}ms" if query_count > 0 else "")

    # Analyze queries
    print(f"\n🔍 QUERY ANALYSIS:")

    select_queries = [q for q in connection.queries if 'SELECT' in q['sql']]
    update_queries = [q for q in connection.queries if 'UPDATE' in q['sql']]

    print(f"  SELECT queries: {len(select_queries)}")
    print(f"  UPDATE queries: {len(update_queries)}")

    # Expected: 1-2 SELECT (aggregate + values_list), 1 UPDATE
    # If we have more, we have N+1 issues
    if query_count > 5:
        print(f"\n❌ N+1 QUERY ISSUE DETECTED!")
        print(f"   Expected: 3-5 queries")
        print(f"   Actual: {query_count} queries")
        print(f"   Extra queries: {query_count - 5}")
    else:
        print(f"\n✅ Query count looks good ({query_count} queries)")

    # Print all queries for analysis
    print(f"\n📋 ALL QUERIES:")
    for i, query in enumerate(connection.queries, 1):
        sql = query['sql'][:200] + "..." if len(query['sql']) > 200 else query['sql']
        print(f"\n{i}. [{query['time']}s]")
        print(f"   {sql}")

    return query_count, duration


def analyze_provincial_sync():
    """Analyze ProvinceCoverage.refresh_from_municipalities()."""
    print("\n\n" + "="*70)
    print("ANALYZING: ProvinceCoverage.refresh_from_municipalities()")
    print("="*70)

    # Find a province with municipality coverages
    province = Province.objects.filter(
        municipalities__obc_coverage__isnull=False
    ).first()

    if not province:
        print("❌ No provinces with municipality coverages found")
        return

    municipal_count = MunicipalityCoverage.objects.filter(
        municipality__province=province,
        is_deleted=False
    ).count()

    print(f"Province: {province.name}, {province.region.name}")
    print(f"Municipality Coverages: {municipal_count}")

    # Get or create coverage
    coverage, _ = ProvinceCoverage.objects.get_or_create(province=province)

    # Reset query counter
    reset_queries()
    start_time = time.time()

    # Execute the sync
    coverage.refresh_from_municipalities()

    duration = time.time() - start_time
    query_count = len(connection.queries)

    print(f"\n📊 RESULTS:")
    print(f"  Queries executed: {query_count}")
    print(f"  Execution time: {duration:.4f}s")
    print(f"  Avg time per query: {(duration/query_count)*1000:.2f}ms" if query_count > 0 else "")

    # Analyze queries
    print(f"\n🔍 QUERY ANALYSIS:")

    select_queries = [q for q in connection.queries if 'SELECT' in q['sql']]
    update_queries = [q for q in connection.queries if 'UPDATE' in q['sql']]

    print(f"  SELECT queries: {len(select_queries)}")
    print(f"  UPDATE queries: {len(update_queries)}")

    # Expected: 1-2 SELECT, 1 UPDATE
    if query_count > 5:
        print(f"\n❌ N+1 QUERY ISSUE DETECTED!")
        print(f"   Expected: 3-5 queries")
        print(f"   Actual: {query_count} queries")
        print(f"   Extra queries: {query_count - 5}")
    else:
        print(f"\n✅ Query count looks good ({query_count} queries)")

    # Print all queries
    print(f"\n📋 ALL QUERIES:")
    for i, query in enumerate(connection.queries, 1):
        sql = query['sql'][:200] + "..." if len(query['sql']) > 200 else query['sql']
        print(f"\n{i}. [{query['time']}s]")
        print(f"   {sql}")

    return query_count, duration


def main():
    """Run all performance analyses."""
    print("="*70)
    print("AUTO-SYNC PERFORMANCE ANALYSIS")
    print("="*70)

    try:
        municipal_queries, municipal_time = analyze_municipal_sync()
        provincial_queries, provincial_time = analyze_provincial_sync()

        print("\n\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Municipal Sync:  {municipal_queries} queries in {municipal_time:.4f}s")
        print(f"Provincial Sync: {provincial_queries} queries in {provincial_time:.4f}s")

        total_queries = municipal_queries + provincial_queries
        optimal_queries = 10  # 5 per sync operation

        if total_queries > optimal_queries:
            print(f"\n❌ OPTIMIZATION NEEDED:")
            print(f"   Total queries: {total_queries}")
            print(f"   Optimal: {optimal_queries}")
            print(f"   Overhead: {total_queries - optimal_queries} extra queries")
        else:
            print(f"\n✅ PERFORMANCE IS GOOD!")

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
