"""
Test script for OCM Aggregation Service
"""

from ocm.services import OCMAggregationService


def test_aggregation_service():
    """Test all aggregation service methods"""
    print("=" * 60)
    print("Testing OCM Aggregation Service")
    print("=" * 60)

    # Test base organization methods
    print("\n1. Base Organization Methods:")
    print(f"   - get_organization_count(): {OCMAggregationService.get_organization_count()}")

    orgs = OCMAggregationService.get_all_organizations()
    print(f"   - get_all_organizations(): {len(orgs)} organizations")
    if orgs:
        print(f"     First: {orgs[0]}")

    stats = OCMAggregationService.get_government_stats()
    print(f"   - get_government_stats(): {stats}")

    # Test budget methods
    print("\n2. Budget Aggregation Methods:")
    fiscal_year = 2025
    consolidated = OCMAggregationService.get_consolidated_budget(fiscal_year)
    print(f"   - get_consolidated_budget({fiscal_year}): {len(consolidated)} organizations")
    if consolidated:
        print(f"     First: {consolidated[0]}")

    budget_summary = OCMAggregationService.get_budget_summary(fiscal_year)
    print(f"   - get_budget_summary({fiscal_year}): {budget_summary}")

    # Test planning methods
    print("\n3. Planning Aggregation Methods:")
    planning_status = OCMAggregationService.get_strategic_planning_status()
    print(f"   - get_strategic_planning_status(): {len(planning_status)} organizations")
    if planning_status:
        print(f"     First: {planning_status[0]}")

    planning_summary = OCMAggregationService.get_planning_summary()
    print(f"   - get_planning_summary(): {planning_summary}")

    # Test coordination methods
    print("\n4. Coordination Aggregation Methods:")
    partnerships = OCMAggregationService.get_inter_moa_partnerships()
    print(f"   - get_inter_moa_partnerships(): {len(partnerships)} partnerships")
    if partnerships:
        print(f"     First: {partnerships[0]}")

    coord_summary = OCMAggregationService.get_coordination_summary()
    print(f"   - get_coordination_summary(): {coord_summary}")

    # Test performance methods
    print("\n5. Performance Metrics Methods:")
    metrics = OCMAggregationService.get_performance_metrics()
    print(f"   - get_performance_metrics(): {metrics}")

    # Test cache management
    print("\n6. Cache Management:")
    cleared = OCMAggregationService.clear_cache()
    print(f"   - clear_cache(): Cleared {cleared} cache keys")

    print("\n" + "=" * 60)
    print("✓ All methods tested successfully!")
    print("=" * 60)


if __name__ == '__main__':
    import django
    import os
    import sys

    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
    django.setup()

    # Run tests
    test_aggregation_service()
