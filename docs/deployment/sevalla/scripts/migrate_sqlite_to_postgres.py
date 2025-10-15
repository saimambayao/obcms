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
logger.info("Starting SQLite data export")

# SECURITY: Use hardcoded command to prevent command injection
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

# SECURITY: Validate output file path
output_file = '../obcms_migration_data.json'
output_path = os.path.abspath(output_file)
base_output_dir = os.path.dirname(output_path)

# Ensure output directory exists and is within expected bounds
if not base_output_dir.startswith(base_dir):
    logger.error(f"Invalid output path: {output_path}")
    sys.exit(1)

# SECURITY: Validate command components
allowed_commands = ['python3', 'python', sys.executable]
if export_cmd[0] not in allowed_commands:
    logger.error(f"Invalid command: {export_cmd[0]}")
    sys.exit(1)

try:
    logger.info(f"Exporting to: {output_path}")
    with open(output_file, 'w') as f:
        # SECURITY: Use subprocess.run with validated arguments
        result = subprocess.run(
            export_cmd,
            stdout=f,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300  # 5 minute timeout to prevent hanging
        )
        if result.returncode != 0:
            logger.error(f"Export failed with return code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            print(f"❌ Export failed: See logs for details")
            sys.exit(1)

    # Check file size
    file_size = os.path.getsize('../obcms_migration_data.json')
    print(f"✅ Exported to obcms_migration_data.json ({file_size:,} bytes)")

except subprocess.TimeoutExpired:
    logger.error("Export timed out after 5 minutes")
    print("❌ Export timed out")
    sys.exit(1)
except Exception as e:
    logger.error(f"Export error: {type(e).__name__}: {str(e)}")
    print(f"❌ Export error: See logs for details")
    sys.exit(1)

print("\n" + "=" * 80)
print("Export complete! Now run the import step in Docker container:")
print("=" * 80)
print("\n📥 Import command:")
print("docker-compose exec web python src/manage.py loaddata /app/obcms_migration_data.json")
print("\nOr use the automated script:")
print("./migrate_sqlite_to_postgres.sh")
