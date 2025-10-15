#!/bin/bash
#
# OBCMS Data Migration: SQLite → PostgreSQL (Docker)
# This script migrates your development data from SQLite to PostgreSQL running in Docker
#

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo "  OBCMS Data Migration: SQLite → PostgreSQL (Docker)"
echo "========================================================================"
echo ""

# Step 1: Check if SQLite database exists
if [ ! -f "src/db.sqlite3" ]; then
    echo "❌ Error: src/db.sqlite3 not found"
    exit 1
fi

echo "📊 SQLite Database Info:"
sqlite3 src/db.sqlite3 "
SELECT 'Users: ' || COUNT(*) FROM auth_user
UNION ALL SELECT 'Regions: ' || COUNT(*) FROM common_region
UNION ALL SELECT 'Provinces: ' || COUNT(*) FROM common_province
UNION ALL SELECT 'Municipalities: ' || COUNT(*) FROM common_municipality
UNION ALL SELECT 'Barangays: ' || COUNT(*) FROM common_barangay;
"
echo ""

# Step 2: Check Docker containers
echo "📦 Checking Docker containers..."
if ! docker-compose ps | grep -q "obcms-web-1.*Up"; then
    echo "❌ Error: Docker containers not running"
    echo "   Run: docker-compose up -d"
    exit 1
fi
echo "✅ Docker containers running"
echo ""

# Step 3: Copy SQLite file to Docker container
echo "📤 Copying SQLite database to Docker container..."
docker cp src/db.sqlite3 obcms-web-1:/tmp/sqlite_backup.db
echo "✅ Database copied"
echo ""

# Step 4: Export data from SQLite
echo "📥 Exporting data from SQLite..."
docker-compose exec -T web sh -c "
cd /app/src && \
DATABASE_URL=sqlite:////tmp/sqlite_backup.db \
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude=contenttypes \
  --exclude=auth.Permission \
  --exclude=sessions.Session \
  --exclude=admin.LogEntry \
  --exclude=auditlog.LogEntry \
  --indent=2
" > /tmp/obcms_migration.json 2>&1

if [ ! -s "/tmp/obcms_migration.json" ]; then
    echo "❌ Error: Export failed or empty"
    cat /tmp/obcms_migration.json
    exit 1
fi

FILE_SIZE=$(ls -lh /tmp/obcms_migration.json | awk '{print $5}')
echo "✅ Exported to /tmp/obcms_migration.json ($FILE_SIZE)"
echo ""

# Step 5: Copy JSON to Docker container
echo "📋 Copying migration data to Docker container..."
docker cp /tmp/obcms_migration.json obcms-web-1:/tmp/migration_data.json
echo "✅ Data copied to container"
echo ""

# Step 6: Import data into PostgreSQL
echo "📥 Importing data into PostgreSQL..."
docker-compose exec -T web sh -c "cd /app/src && python manage.py loaddata /tmp/migration_data.json"
echo "✅ Import complete"
echo ""

# Step 7: Verify migration
echo "🔍 Verifying migration..."
docker-compose exec -T db psql -U obcms -d obcms -c "
SELECT
  'Users: ' || COUNT(*) FROM auth_user
UNION ALL SELECT 'Regions: ' || COUNT(*) FROM common_region
UNION ALL SELECT 'Provinces: ' || COUNT(*) FROM common_province
UNION ALL SELECT 'Municipalities: ' || COUNT(*) FROM common_municipality
UNION ALL SELECT 'Barangays: ' || COUNT(*) FROM common_barangay;
"
echo ""

echo "========================================================================"
echo "  ✅ Migration Complete!"
echo "========================================================================"
echo ""
echo "Your development data has been successfully migrated to PostgreSQL."
echo "Access the application at: http://localhost:8000"
echo ""
