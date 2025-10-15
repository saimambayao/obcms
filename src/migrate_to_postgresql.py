#!/usr/bin/env python
"""
OBCMS/BMMS PostgreSQL Migration Script
Migrates from SQLite to PostgreSQL for production deployment

This script:
1. Exports data from SQLite
2. Creates PostgreSQL database structure
3. Imports data to PostgreSQL
4. Validates migration integrity

Usage:
    python migrate_to_postgresql.py [--export-only] [--import-only] [--validate-only]
"""

import os
import sys
import django
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import argparse

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.apps import apps
from django.conf import settings

class PostgreSQLMigrator:
    """Handle migration from SQLite to PostgreSQL"""

    def __init__(self):
        self.sqlite_db_path = settings.DATABASES['default']['NAME']
        self.pg_config = self._get_postgres_config()

    def _get_postgres_config(self):
        """Get PostgreSQL configuration from environment or defaults"""
        return {
            'dbname': os.environ.get('POSTGRES_DB', 'obcms_prod'),
            'user': os.environ.get('POSTGRES_USER', 'obcms_user'),
            'password': os.environ.get('POSTGRES_PASSWORD', ''),
            'host': os.environ.get('POSTGRES_HOST', 'localhost'),
            'port': os.environ.get('POSTGRES_PORT', '5432'),
        }

    def export_sqlite_data(self):
        """Export all data from SQLite to JSON files"""
        print("📤 Exporting data from SQLite...")

        # Create export directory
        export_dir = 'postgres_export'
        os.makedirs(export_dir, exist_ok=True)

        # Connect to SQLite
        sqlite_conn = sqlite3.connect(self.sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row

        # Get all table names
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        exported_data = {}

        for table in tables:
            print(f"   Exporting table: {table}")

            # Get table schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            # Export table data
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            table_data = {
                'schema': columns,
                'data': [dict(row) for row in rows]
            }

            # Save to JSON file
            with open(f'{export_dir}/{table}.json', 'w') as f:
                json.dump(table_data, f, indent=2, default=str)

            exported_data[table] = len(rows)

        sqlite_conn.close()

        print(f"✅ Exported {len(tables)} tables to {export_dir}/")
        return exported_data

    def create_postgres_database(self):
        """Create PostgreSQL database"""
        print("🗄️  Creating PostgreSQL database...")

        # Connect to PostgreSQL (postgres database to create new database)
        pg_config = self.pg_config.copy()
        pg_config['dbname'] = 'postgres'

        try:
            conn = psycopg2.connect(**pg_config)
            conn.autocommit = True
            cursor = conn.cursor()

            # Drop database if exists
            cursor.execute(f"DROP DATABASE IF EXISTS {self.pg_config['dbname']}")
            print(f"   Dropped existing database: {self.pg_config['dbname']}")

            # Create database
            cursor.execute(f"CREATE DATABASE {self.pg_config['dbname']}")
            print(f"   Created database: {self.pg_config['dbname']}")

            conn.close()

        except psycopg2.Error as e:
            print(f"❌ Error creating database: {e}")
            return False

        return True

    def create_postgres_tables(self):
        """Create tables in PostgreSQL using Django migrations"""
        print("📋 Creating PostgreSQL tables...")

        try:
            # Run Django migrations
            call_command('migrate', verbosity=2, interactive=False)
            print("✅ PostgreSQL tables created successfully")
            return True

        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

    def import_data_to_postgres(self):
        """Import data from JSON files to PostgreSQL"""
        print("📥 Importing data to PostgreSQL...")

        export_dir = 'postgres_export'
        if not os.path.exists(export_dir):
            print(f"❌ Export directory not found: {export_dir}")
            return False

        # Connect to PostgreSQL
        try:
            conn = psycopg2.connect(**self.pg_config)
            conn.autocommit = True  # Enable autocommit for constraint handling
            cursor = conn.cursor()

            # Temporarily disable constraints
            print("   Temporarily disabling constraints...")
            cursor.execute("SET session_replication_role = replica;")

            # Get all JSON files
            json_files = [f for f in os.listdir(export_dir) if f.endswith('.json')]

            imported_counts = {}
            failed_tables = []

            for json_file in json_files:
                table_name = json_file[:-5]  # Remove .json extension
                print(f"   Importing table: {table_name}")

                # Load data from JSON
                with open(f'{export_dir}/{json_file}', 'r') as f:
                    table_data = json.load(f)

                if not table_data['data']:
                    print(f"   No data to import for {table_name}")
                    continue

                # Try to import data
                try:
                    self._import_table_data(cursor, table_name, table_data)
                    imported_counts[table_name] = len(table_data['data'])
                except Exception as e:
                    print(f"   ⚠️  Skipping {table_name}: {str(e)[:100]}...")
                    failed_tables.append(table_name)
                    continue

            # Re-enable constraints
            print("   Re-enabling constraints...")
            cursor.execute("SET session_replication_role = DEFAULT;")

            conn.commit()
            conn.close()

            print(f"✅ Imported {len(imported_counts)} tables")
            for table, count in imported_counts.items():
                print(f"   {table}: {count} records")

            if failed_tables:
                print(f"⚠️  {len(failed_tables)} tables skipped due to constraint issues:")
                for table in failed_tables:
                    print(f"   - {table}")

            return True

        except Exception as e:
            print(f"❌ Error importing data: {e}")
            return False

    def _import_table_data(self, cursor, table_name, table_data):
        """Import data for a specific table"""
        data = table_data['data']

        if not data:
            return

        # Get column names from first row
        columns = list(data[0].keys())

        # Check column types for the table to handle type conversions
        column_types = {}
        try:
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s
                AND table_schema = 'public'
            """, (table_name,))
            column_types = {row[0]: row[1] for row in cursor.fetchall()}
        except:
            pass  # If we can't get column types, continue without type checking

        # Create placeholder string
        placeholders = ', '.join(['%s'] * len(columns))

        # Prepare insert statement
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        # Insert data in batches
        batch_size = 1000
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            values = []
            for row in batch:
                row_values = []
                for col in columns:
                    value = row.get(col)
                    col_type = column_types.get(col, '')

                    # Handle None values properly
                    if value is None or value == '':
                        value = None
                    # Handle boolean type conversion
                    elif col_type == 'boolean':
                        if isinstance(value, bool):
                            value = value
                        elif isinstance(value, int):
                            value = bool(value)
                        elif isinstance(value, str):
                            value = value.lower() in ('true', '1', 'yes', 't', 'y')
                    # Handle integer type conversion
                    elif col_type == 'integer' and isinstance(value, bool):
                        value = 1 if value else 0
                    # Keep original value for other types
                    row_values.append(value)
                values.append(row_values)
            cursor.executemany(insert_sql, values)

    def validate_migration(self):
        """Validate migration integrity"""
        print("✅ Validating migration integrity...")

        # Connect to both databases
        sqlite_conn = sqlite3.connect(self.sqlite_db_path)
        pg_conn = psycopg2.connect(**self.pg_config)

        validation_results = {}

        try:
            # Get Django models
            from django.apps import apps

            for model in apps.get_models():
                table_name = model._meta.db_table

                # Get count from SQLite
                sqlite_cursor = sqlite_conn.cursor()
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                sqlite_count = sqlite_cursor.fetchone()[0]

                # Get count from PostgreSQL
                pg_cursor = pg_conn.cursor()
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                pg_count = pg_cursor.fetchone()[0]

                validation_results[table_name] = {
                    'sqlite': sqlite_count,
                    'postgres': pg_count,
                    'match': sqlite_count == pg_count
                }

                if sqlite_count != pg_count:
                    print(f"   ⚠️  Mismatch in {table_name}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
                else:
                    print(f"   ✅ {table_name}: {sqlite_count} records")

            # Check for any mismatches
            mismatches = [name for name, result in validation_results.items() if not result['match']]

            if mismatches:
                print(f"❌ Validation failed for {len(mismatches)} tables")
                return False
            else:
                print("✅ Migration validation successful")
                return True

        except Exception as e:
            print(f"❌ Error during validation: {e}")
            return False

        finally:
            sqlite_conn.close()
            pg_conn.close()

    def run_migration(self, export_only=False, import_only=False, validate_only=False):
        """Run the complete migration process"""
        print("=" * 60)
        print("OBCMS/BMMS POSTGRESQL MIGRATION")
        print("=" * 60)
        print(f"SQLite DB: {self.sqlite_db_path}")
        print(f"PostgreSQL DB: {self.pg_config['dbname']}")
        print("")

        try:
            # Export from SQLite
            if not import_only and not validate_only:
                self.export_sqlite_data()
                print("")

            # Create PostgreSQL database
            if not export_only and not import_only and not validate_only:
                if not self.create_postgres_database():
                    return False
                print("")

            # Create PostgreSQL tables
            if not export_only and not import_only and not validate_only:
                if not self.create_postgres_tables():
                    return False
                print("")

            # Import to PostgreSQL
            if not export_only and not validate_only:
                if not self.import_data_to_postgres():
                    return False
                print("")

            # Validate migration
            if not export_only and not import_only:
                if not self.validate_migration():
                    return False
                print("")

            print("=" * 60)
            print("🎉 POSTGRESQL MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)

            if export_only:
                print("✅ Data exported to postgres_export/ directory")
                print("Next steps:")
                print("1. Set up PostgreSQL database")
                print("2. Update DATABASE_URL in .env")
                print("3. Run: python migrate_to_postgresql.py --import-only")

            elif import_only:
                print("✅ Data imported from postgres_export/ directory")
                print("Next step:")
                print("1. Run: python migrate_to_postgresql.py --validate-only")

            elif validate_only:
                print("✅ Migration validation completed")

            else:
                print("✅ Full migration completed")
                print("✅ SQLite data migrated to PostgreSQL")
                print("✅ PostgreSQL ready for production")

            return True

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Migrate OBCMS from SQLite to PostgreSQL')
    parser.add_argument('--export-only', action='store_true', help='Only export data from SQLite')
    parser.add_argument('--import-only', action='store_true', help='Only import data to PostgreSQL')
    parser.add_argument('--validate-only', action='store_true', help='Only validate migration integrity')

    args = parser.parse_args()

    if args.export_only and args.import_only:
        print("❌ Cannot use --export-only and --import-only together")
        return 1

    if args.export_only and args.validate_only:
        print("❌ Cannot use --export-only and --validate-only together")
        return 1

    if args.import_only and args.validate_only:
        print("❌ Cannot use --import-only and --validate-only together")
        return 1

    migrator = PostgreSQLMigrator()
    success = migrator.run_migration(
        export_only=args.export_only,
        import_only=args.import_only,
        validate_only=args.validate_only
    )

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())