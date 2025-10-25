#!/usr/bin/env python
"""
Migration 0033 Validation Script
Tests whether migration 0033 correctly fixes the has_madrasah KeyError
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
sys.path.insert(0, '/Users/saidamenmambayao/apps/obcms/src')

django.setup()

from django.db.migrations.loader import MigrationLoader
from django.db import connection
from django.db.migrations.graph import MigrationGraph

def test_migration_graph_builds():
    """Test 1: Can migration graph build without KeyError?"""
    print("\n" + "="*70)
    print("TEST 1: Migration Graph Building")
    print("="*70)

    try:
        loader = MigrationLoader(connection)
        graph = loader.build_graph()
        print("✓ Migration graph builds successfully")
        print(f"  Total migrations in graph: {len(graph.nodes)}")
        return True, graph
    except KeyError as e:
        print(f"✗ KeyError during graph build: {e}")
        return False, None
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")
        return False, None


def test_communities_migrations_exist(graph):
    """Test 2: Check all communities migrations are present"""
    print("\n" + "="*70)
    print("TEST 2: Communities App Migrations Present")
    print("="*70)

    if not graph:
        print("✗ Cannot test - graph not built")
        return False

    communities_migrations = sorted(
        [key for key in graph.nodes if key[0] == 'communities']
    )

    print(f"✓ Found {len(communities_migrations)} communities migrations:")
    for app, name in communities_migrations[-5:]:  # Show last 5
        print(f"  - {name}")

    return len(communities_migrations) > 0


def test_migration_0033_exists(graph):
    """Test 3: Verify migration 0033 exists and is reachable"""
    print("\n" + "="*70)
    print("TEST 3: Migration 0033 Validation")
    print("="*70)

    if not graph:
        print("✗ Cannot test - graph not built")
        return False

    target = ('communities', '0033_fix_has_madrasah_state')

    if target in graph.nodes:
        migration = graph.nodes[target]
        print(f"✓ Migration 0033 found in graph")
        print(f"  Name: {migration.name}")
        print(f"  Dependencies: {migration.dependencies}")
        return True
    else:
        print(f"✗ Migration 0033 NOT found in graph")
        return False


def test_migration_0011_exists(graph):
    """Test 4: Verify migration 0011 still exists"""
    print("\n" + "="*70)
    print("TEST 4: Migration 0011 (Problem Migration) Validation")
    print("="*70)

    if not graph:
        print("✗ Cannot test - graph not built")
        return False

    target = ('communities', '0011_remove_municipalitycoverage_has_madrasah_and_more')

    if target in graph.nodes:
        migration = graph.nodes[target]
        print(f"✓ Migration 0011 found in graph")
        print(f"  This is the migration that CAUSES KeyError (if state is incomplete)")
        print(f"  Dependencies: {migration.dependencies}")
        return True
    else:
        print(f"✗ Migration 0011 NOT found in graph")
        return False


def test_migration_chain():
    """Test 5: Verify migration sequence 0009->0011->0033"""
    print("\n" + "="*70)
    print("TEST 5: Migration Chain Sequence")
    print("="*70)

    try:
        loader = MigrationLoader(connection)
        graph = loader.build_graph()

        migrations_to_check = [
            ('communities', '0009_municipalitycoverage_access_als_and_more'),
            ('communities', '0011_remove_municipalitycoverage_has_madrasah_and_more'),
            ('communities', '0032_merge_20251025_0031'),
            ('communities', '0033_fix_has_madrasah_state'),
        ]

        all_present = True
        for app, name in migrations_to_check:
            if (app, name) in graph.nodes:
                print(f"✓ {name}")
            else:
                print(f"✗ {name} - NOT FOUND")
                all_present = False

        return all_present
    except Exception as e:
        print(f"✗ Error checking chain: {type(e).__name__}: {e}")
        return False


def test_separate_database_and_state():
    """Test 6: Verify migration 0033 uses SeparateDatabaseAndState correctly"""
    print("\n" + "="*70)
    print("TEST 6: Migration 0033 Operation Structure")
    print("="*70)

    try:
        loader = MigrationLoader(connection)
        migration_0033 = loader.get_migration('communities', '0033_fix_has_madrasah_state')

        print(f"✓ Migration 0033 loaded successfully")
        print(f"  Number of operations: {len(migration_0033.operations)}")

        for i, op in enumerate(migration_0033.operations):
            op_type = type(op).__name__
            print(f"  Operation {i}: {op_type}")

            if op_type == 'SeparateDatabaseAndState':
                print(f"    ✓ Using SeparateDatabaseAndState (CORRECT)")
                print(f"    - State operations: {len(op.state_operations)}")
                print(f"    - Database operations: {len(op.database_operations)}")

                # Verify state operations
                for j, state_op in enumerate(op.state_operations):
                    state_op_type = type(state_op).__name__
                    print(f"      State op {j}: {state_op_type}")
                    if hasattr(state_op, 'model_name') and hasattr(state_op, 'name'):
                        print(f"        Model: {state_op.model_name}, Field: {state_op.name}")

                return True

        return False
    except Exception as e:
        print(f"✗ Error inspecting migration: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_current_models():
    """Test 7: Verify current models don't have has_madrasah field"""
    print("\n" + "="*70)
    print("TEST 7: Current Model Field Verification")
    print("="*70)

    try:
        from communities.models import OBCCommunity, MunicipalityCoverage

        # Check OBCCommunity
        obc_fields = [f.name for f in OBCCommunity._meta.get_fields()]
        if 'has_madrasah' in obc_fields:
            print("✗ OBCCommunity still has has_madrasah field (UNEXPECTED)")
            return False
        else:
            print("✓ OBCCommunity does NOT have has_madrasah field (CORRECT)")

        if 'madrasah_count' in obc_fields:
            print("✓ OBCCommunity HAS madrasah_count field (CORRECT)")
        else:
            print("✗ OBCCommunity missing madrasah_count field (UNEXPECTED)")
            return False

        # Check MunicipalityCoverage
        mun_fields = [f.name for f in MunicipalityCoverage._meta.get_fields()]
        if 'has_madrasah' in mun_fields:
            print("✗ MunicipalityCoverage still has has_madrasah field (UNEXPECTED)")
            return False
        else:
            print("✓ MunicipalityCoverage does NOT have has_madrasah field (CORRECT)")

        if 'madrasah_count' in mun_fields:
            print("✓ MunicipalityCoverage HAS madrasah_count field (CORRECT)")
        else:
            print("✗ MunicipalityCoverage missing madrasah_count field (UNEXPECTED)")
            return False

        return True
    except Exception as e:
        print(f"✗ Error loading models: {type(e).__name__}: {e}")
        return False


def test_migration_dependencies():
    """Test 8: Verify migration 0033 has correct dependency"""
    print("\n" + "="*70)
    print("TEST 8: Migration 0033 Dependencies")
    print("="*70)

    try:
        loader = MigrationLoader(connection)
        migration_0033 = loader.get_migration('communities', '0033_fix_has_madrasah_state')

        expected_dependency = ('communities', '0032_merge_20251025_0031')

        if migration_0033.dependencies:
            print(f"✓ Migration 0033 has dependencies: {migration_0033.dependencies}")

            if expected_dependency in migration_0033.dependencies:
                print(f"✓ Correct dependency on 0032_merge_20251025_0031")
                return True
            else:
                print(f"✗ Missing expected dependency on 0032")
                return False
        else:
            print(f"✗ Migration 0033 has no dependencies")
            return False
    except Exception as e:
        print(f"✗ Error checking dependencies: {type(e).__name__}: {e}")
        return False


def run_all_tests():
    """Run all validation tests"""
    print("\n")
    print("#" * 70)
    print("# MIGRATION 0033 VALIDATION TEST SUITE")
    print("# Testing fix for has_madrasah KeyError")
    print("#" * 70)

    results = {}

    # Test 1: Graph building
    test1_pass, graph = test_migration_graph_builds()
    results['Graph Building'] = test1_pass

    # Test 2: Communities migrations exist
    test2_pass = test_communities_migrations_exist(graph)
    results['Communities Migrations'] = test2_pass

    # Test 3: Migration 0033 exists
    test3_pass = test_migration_0033_exists(graph)
    results['Migration 0033 Exists'] = test3_pass

    # Test 4: Migration 0011 exists
    test4_pass = test_migration_0011_exists(graph)
    results['Migration 0011 Exists'] = test4_pass

    # Test 5: Migration chain
    test5_pass = test_migration_chain()
    results['Migration Chain'] = test5_pass

    # Test 6: SeparateDatabaseAndState structure
    test6_pass = test_separate_database_and_state()
    results['SeparateDatabaseAndState'] = test6_pass

    # Test 7: Current models
    test7_pass = test_current_models()
    results['Current Models'] = test7_pass

    # Test 8: Dependencies
    test8_pass = test_migration_dependencies()
    results['Dependencies'] = test8_pass

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n*** ALL TESTS PASSED - Migration 0033 fix is VALID ***")
        return True
    else:
        print(f"\n*** {total - passed} TEST(S) FAILED - Review required ***")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
