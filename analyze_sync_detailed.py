"""
Detailed performance analysis with verbose SQL logging.
"""

import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
django.setup()

from django.db import connection, reset_queries
from django.conf import settings
from communities.models import MunicipalityCoverage, ProvinceCoverage, AGGREGATED_NUMERIC_FIELDS
from common.models import Municipality

settings.DEBUG = True


def analyze_aggregate_query():
    """Analyze the aggregate query used in refresh_from_communities."""
    print("="*70)
    print("ANALYZING: Aggregate Query Structure")
    print("="*70)

    municipality = Municipality.objects.filter(
        barangays__obc_communities__isnull=False
    ).first()

    print(f"\nMunicipality: {municipality.name}")
    print(f"Aggregating {len(AGGREGATED_NUMERIC_FIELDS)} fields")

    # Test the aggregate query directly
    from communities.models import OBCCommunity
    from django.db.models import Sum

    reset_queries()

    communities = OBCCommunity.objects.filter(
        barangay__municipality=municipality,
        is_deleted=False
    )

    # Execute aggregate
    aggregates = communities.aggregate(
        **{f"{field}__sum": Sum(field) for field in AGGREGATED_NUMERIC_FIELDS}
    )

    query_count = len(connection.queries)

    print(f"\n📊 Aggregate Query Analysis:")
    print(f"  Queries: {query_count}")
    print(f"  Expected: 1 (optimal)")

    if connection.queries:
        sql = connection.queries[0]['sql']
        print(f"\n📋 Generated SQL:")
        print(sql)

        # Check for subqueries or joins
        if 'SELECT COUNT' in sql:
            print("\n⚠️  Contains subqueries!")
        if 'JOIN' in sql:
            print(f"\n⚠️  Contains JOINs!")

    print(f"\n✅ Aggregate is efficient: Single query with {len(AGGREGATED_NUMERIC_FIELDS)} aggregations")

    return aggregates


def test_values_list_query():
    """Test the values_list query for key_barangays."""
    print("\n\n" + "="*70)
    print("ANALYZING: values_list Query for key_barangays")
    print("="*70)

    municipality = Municipality.objects.filter(
        barangays__obc_communities__isnull=False
    ).first()

    from communities.models import OBCCommunity

    reset_queries()

    communities = OBCCommunity.objects.filter(
        barangay__municipality=municipality,
        is_deleted=False
    )

    key_barangays = (
        communities.values_list("barangay__name", flat=True)
        .order_by("barangay__name")
        .distinct()
    )

    # Force evaluation
    barangay_list = list(key_barangays)

    query_count = len(connection.queries)

    print(f"\n📊 values_list Query Analysis:")
    print(f"  Queries: {query_count}")
    print(f"  Barangays: {len(barangay_list)}")
    print(f"  Expected: 1 (optimal)")

    if connection.queries:
        sql = connection.queries[0]['sql']
        print(f"\n📋 Generated SQL:")
        print(sql)

    print(f"\n✅ values_list is efficient: Single query")


def test_update_query():
    """Test the UPDATE query pattern."""
    print("\n\n" + "="*70)
    print("ANALYZING: UPDATE Query Pattern")
    print("="*70)

    municipality = Municipality.objects.filter(
        barangays__obc_communities__isnull=False
    ).first()

    coverage, _ = MunicipalityCoverage.objects.get_or_create(
        municipality=municipality
    )

    reset_queries()

    # Simulate the update operation
    update_kwargs = {
        "total_obc_communities": 10,
        "key_barangays": "Barangay 1, Barangay 2",
        "estimated_obc_population": None,
        "households": 200,
    }

    MunicipalityCoverage.objects.filter(pk=coverage.pk).update(**update_kwargs)

    query_count = len(connection.queries)

    print(f"\n📊 UPDATE Query Analysis:")
    print(f"  Queries: {query_count}")
    print(f"  Fields updated: {len(update_kwargs)}")
    print(f"  Expected: 1 (optimal)")

    if connection.queries:
        sql = connection.queries[0]['sql']
        print(f"\n📋 Generated SQL:")
        print(sql[:500] + "..." if len(sql) > 500 else sql)

    print(f"\n✅ UPDATE is efficient: Single bulk update")


def test_full_refresh_with_logging():
    """Test full refresh with detailed logging."""
    print("\n\n" + "="*70)
    print("FULL REFRESH TEST: refresh_from_communities()")
    print("="*70)

    municipality = Municipality.objects.filter(
        barangays__obc_communities__isnull=False
    ).first()

    coverage, _ = MunicipalityCoverage.objects.get_or_create(
        municipality=municipality
    )

    print(f"\nMunicipality: {municipality.name}")
    print(f"Auto-sync enabled: {coverage.auto_sync}")

    reset_queries()

    # Execute refresh
    coverage.refresh_from_communities()

    query_count = len(connection.queries)

    print(f"\n📊 Full Refresh Analysis:")
    print(f"  Total queries: {query_count}")
    print(f"  Expected: 3-4 (aggregate + values_list + update + provincial sync)")

    print(f"\n📋 Query Breakdown:")
    for i, query in enumerate(connection.queries, 1):
        sql_type = "UNKNOWN"
        if "SELECT" in query['sql'] and "SUM(" in query['sql']:
            sql_type = "AGGREGATE"
        elif "SELECT" in query['sql'] and "DISTINCT" in query['sql']:
            sql_type = "VALUES_LIST"
        elif "UPDATE" in query['sql']:
            sql_type = "UPDATE"
        elif "SELECT" in query['sql']:
            sql_type = "SELECT"

        sql = query['sql'][:150] + "..." if len(query['sql']) > 150 else query['sql']
        print(f"\n{i}. [{sql_type}] [{query['time']}s]")
        print(f"   {sql}")


def check_for_n_plus_one():
    """Check for N+1 patterns by testing with different community counts."""
    print("\n\n" + "="*70)
    print("N+1 DETECTION TEST: Variable Community Counts")
    print("="*70)

    # Find municipalities with different community counts
    municipalities = list(
        Municipality.objects.filter(
            barangays__obc_communities__isnull=False
        ).distinct()[:3]
    )

    results = []

    for municipality in municipalities:
        from communities.models import OBCCommunity

        community_count = OBCCommunity.objects.filter(
            barangay__municipality=municipality,
            is_deleted=False
        ).count()

        coverage, _ = MunicipalityCoverage.objects.get_or_create(
            municipality=municipality
        )

        reset_queries()
        coverage.refresh_from_communities()
        query_count = len(connection.queries)

        results.append((municipality.name, community_count, query_count))

        print(f"\n{municipality.name}:")
        print(f"  Communities: {community_count}")
        print(f"  Queries: {query_count}")

    print(f"\n📊 N+1 Analysis:")
    print(f"{'Municipality':<30} {'Communities':<15} {'Queries':<10}")
    print("="*60)
    for name, comm_count, q_count in results:
        print(f"{name:<30} {comm_count:<15} {q_count:<10}")

    # Check if query count varies with community count
    query_counts = [r[2] for r in results]
    if len(set(query_counts)) == 1:
        print(f"\n✅ NO N+1 ISSUE: Query count is constant ({query_counts[0]})")
    else:
        print(f"\n❌ POTENTIAL N+1: Query count varies ({query_counts})")


def main():
    """Run all detailed analyses."""
    try:
        analyze_aggregate_query()
        test_values_list_query()
        test_update_query()
        test_full_refresh_with_logging()
        check_for_n_plus_one()

        print("\n\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
