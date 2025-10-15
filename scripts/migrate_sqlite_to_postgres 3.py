#!/usr/bin/env python3
"""
Migrate data from SQLite (development) to PostgreSQL (Docker)
"""
import os
import sys
import subprocess
import shlex
import logging

# Set up secure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SECURITY: Validate working directory before changing
base_dir = '/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms'
if not os.path.exists(base_dir) or not os.path.isdir(base_dir):
    logger.error(f"Invalid base directory: {base_dir}")
    sys.exit(1)

# Change to src directory
src_dir = os.path.join(base_dir, 'src')
if not os.path.exists(src_dir) or not os.path.isdir(src_dir):
    logger.error(f"Source directory not found: {src_dir}")
    sys.exit(1)

os.chdir(src_dir)
logger.info(f"Changed to directory: {src_dir}")

# Set Django settings for SQLite (SECURITY: Use hardcoded values to prevent injection)
os.environ['DJANGO_SETTINGS_MODULE'] = 'obc_management.settings'
os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
logger.info("Django settings configured for SQLite migration")

print("=" * 80)
print("OBCMS Data Migration: SQLite → PostgreSQL")
print("=" * 80)

# Step 1: Export from SQLite
print("\n📤 Step 1: Exporting data from SQLite...")
export_cmd = [
    sys.executable,
    'manage.py',
    'dumpdata',
    '--natural-foreign',
    '--natural-primary',
    '--exclude=contenttypes',
    '--exclude=auth.Permission',
    '--exclude=sessions.Session',
    '--exclude=admin.LogEntry',
    '--exclude=auditlog.LogEntry',
    '--indent=2'
]

try:
    with open('../obcms_migration_data.json', 'w') as f:
        result = subprocess.run(export_cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"❌ Export failed: {result.stderr}")
            sys.exit(1)

    # Check file size
    file_size = os.path.getsize('../obcms_migration_data.json')
    print(f"✅ Exported to obcms_migration_data.json ({file_size:,} bytes)")

except Exception as e:
    print(f"❌ Export error: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("Export complete! Now run the import step in Docker container:")
print("=" * 80)
print("\n📥 Import command:")
print("docker-compose exec web python src/manage.py loaddata /app/obcms_migration_data.json")
print("\nOr use the automated script:")
print("./migrate_sqlite_to_postgres.sh")
