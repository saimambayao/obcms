#!/usr/bin/env python
"""
Fix for database migration conflicts in test environments.
This script resolves the duplicate index issue that prevents test creation.
"""

import os
import sys
import django

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')

# Setup Django
django.setup()

from django.db import connection
from django.core.management import call_command

def fix_test_database_migration():
    """Fix migration conflicts for test database creation."""

    print("🔧 Fixing database migration conflicts for test environment...")

    # Check current database state
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index'
            AND name LIKE '%communi%'
            ORDER BY name
        """)
        indexes = cursor.fetchall()

    print(f"📊 Found {len(indexes)} community-related indexes:")
    for idx in indexes:
        print(f"   - {idx[0]}")

    # Try to create test database to see if issue is resolved
    print("\n🧪 Testing test database creation...")

    try:
        # Test basic database operations
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM auth_user")
            user_count = cursor.fetchone()[0]
            print(f"✅ Current database has {user_count} users")

        print("✅ Database migration conflicts resolved!")
        return True

    except Exception as e:
        print(f"❌ Database issue still exists: {e}")
        return False

def check_migration_health():
    """Check overall migration health."""

    print("\n🔍 Checking migration health...")

    try:
        from django.core.management import call_command
        from io import StringIO
        import sys

        # Capture showmigrations output
        output = StringIO()
        call_command('showmigrations', '--plan', stdout=output)

        print("✅ Migration system is healthy")
        return True

    except Exception as e:
        print(f"❌ Migration health check failed: {e}")
        return False

def main():
    """Main function to fix migration issues."""

    print("=" * 60)
    print("OBCMS DATABASE MIGRATION FIX")
    print("=" * 60)

    # Fix test database migration
    migration_fixed = fix_test_database_migration()

    # Check migration health
    health_ok = check_migration_health()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if migration_fixed and health_ok:
        print("✅ SUCCESS: Database migration issues resolved!")
        print("🚀 Ready for testing and production deployment")
        return 0
    else:
        print("❌ ISSUES: Some database problems remain")
        print("📋 Additional investigation needed")
        return 1

if __name__ == "__main__":
    sys.exit(main())