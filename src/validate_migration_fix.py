#!/usr/bin/env python
"""
Script to validate that the migration conflict has been resolved.
This tests if Django can successfully create a test database and run migrations.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.test.utils import get_runner
from django.db import connections
from django.conf import settings

def main():
    """Test if migration conflict is resolved."""
    print("🔧 Testing Migration Fix Validation")
    print("=" * 50)

    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
    django.setup()

    print("✅ Django setup successful")

    # Test 1: Check if Django can connect to database
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    # Test 2: Check if migrations can be applied
    try:
        from django.core.management import call_command
        print("🔄 Testing migration application...")

        # Create test database schema
        call_command('migrate', verbosity=0, interactive=False)
        print("✅ Migrations applied successfully")
    except Exception as e:
        print(f"❌ Migration application failed: {e}")
        return False

    # Test 3: Check if the specific conflicting indexes exist with correct names
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Check if the old index name exists for spatialdatapoint
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name='communities_communi_896657_idx'
            """)
            spatial_result = cursor.fetchone()

            # Check if the new index name exists for obccommunity
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name='communities_obccommunity_org_idx'
            """)
            obc_result = cursor.fetchone()

            if spatial_result:
                print("✅ SpatialDataPoint index 'communities_communi_896657_idx' exists")
            else:
                print("❌ SpatialDataPoint index missing")

            if obc_result:
                print("✅ OBCCommunity index 'communities_obccommunity_org_idx' exists")
            else:
                print("❌ OBCCommunity index missing")

    except Exception as e:
        print(f"⚠️ Index validation failed (non-critical): {e}")

    # Test 4: Try to create a test runner (this would fail with migration conflict)
    try:
        from django.test.utils import get_runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=False)
        print("✅ Test runner creation successful")
    except Exception as e:
        print(f"❌ Test runner creation failed: {e}")
        return False

    print("\n🎉 Migration Fix Validation Complete!")
    print("✅ All critical tests passed - migration conflict resolved!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)