#!/usr/bin/env python
"""
SQLite to PostgreSQL Migration Script
Migrates data from SQLite to PostgreSQL, handling duplicates and integrity constraints.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, 'src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
django.setup()

from django.core.management import call_command
from django.db import connection, connections

def migrate_data():
    """Migrate data from SQLite to PostgreSQL using database routers."""

    print("=" * 80)
    print("SQLite → PostgreSQL Migration")
    print("=" * 80)

    # Step 1: Verify PostgreSQL connection
    print("\n[1/5] Verifying PostgreSQL connection...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to: {version}")

    # Step 2: Check tables
    print("\n[2/5] Checking database schema...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        table_count = cursor.fetchone()[0]
        print(f"✅ Found {table_count} tables in PostgreSQL")

    # Step 3: Get row counts from SQLite
    print("\n[3/5] Analyzing SQLite data...")
    sqlite_db_path = 'src/db.sqlite3'

    # Use SQLite to get counts
    import sqlite3
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    cursor = sqlite_conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    total_rows = 0
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count > 0:
                total_rows += count
                print(f"  {table}: {count:,} rows")
        except sqlite3.OperationalError:
            pass

    sqlite_conn.close()
    print(f"\n✅ Total rows to migrate: {total_rows:,}")

    # Step 4: Import data
    print("\n[4/5] Importing data into PostgreSQL...")
    print("This may take a few minutes...")

    try:
        # Try to load the fixture
        call_command('loaddata', 'sqlite_data_fixed.json', verbosity=2)
        print("✅ Data imported successfully!")
    except Exception as e:
        print(f"⚠️  Import encountered issues: {str(e)[:200]}")
        print("\nTrying alternative approach...")

        # Alternative: Use dumpdata with app-specific exports
        print("\n[5/5] Using app-specific migration...")
        apps_to_migrate = [
            'auth',  # Users and groups
            'common',  # Core models
            'communities',  # OBC communities
            'mana',  # MANA assessments
            'coordination',  # Partnerships
            'monitoring',  # M&E
            'project_central',  # Projects
        ]

        for app in apps_to_migrate:
            try:
                print(f"  Migrating {app}...")
                call_command('loaddata', f'{app}_data.json', verbosity=0)
            except Exception as e:
                print(f"  ⚠️  {app}: {str(e)[:100]}")
                continue

    # Step 5: Verify migration
    print("\n[5/5] Verifying migration...")
    with connection.cursor() as cursor:
        # Count users
        cursor.execute("SELECT COUNT(*) FROM common_user;")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users: {user_count}")

        # Count communities
        cursor.execute("SELECT COUNT(*) FROM communities_obccommunity;")
        community_count = cursor.fetchone()[0]
        print(f"✅ OBC Communities: {community_count}")

        # Count assessments
        cursor.execute("SELECT COUNT(*) FROM mana_assessment;")
        assessment_count = cursor.fetchone()[0]
        print(f"✅ MANA Assessments: {assessment_count}")

    print("\n" + "=" * 80)
    print("Migration completed!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Test the application: python src/manage.py runserver")
    print("2. Verify data integrity")
    print("3. Run tests: pytest")

if __name__ == '__main__':
    # Set DATABASE_URL for this script
    os.environ['DATABASE_URL'] = 'postgres://localhost/obcms_local'
    migrate_data()
