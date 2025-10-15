#!/bin/bash
# Database restoration script with automatic path detection

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Get Django's configured database path
DB_PATH=$(cd "$PROJECT_ROOT/src" && ../venv/bin/python manage.py shell -c "
from django.conf import settings
print(settings.DATABASES['default']['NAME'])
" 2>/dev/null)

if [ -z "$DB_PATH" ]; then
    echo "Error: Could not determine database path"
    exit 1
fi

echo "Django database location: $DB_PATH"

# List available backups
echo ""
echo "Available backups:"
ls -lht "$PROJECT_ROOT"/backups/*.backup.* 2>/dev/null || echo "No backups found in backups/"
ls -lht "$PROJECT_ROOT"/src/*.backup.* 2>/dev/null || echo "No backups found in src/"
ls -lht "$PROJECT_ROOT"/src/obc_management/*.backup.* 2>/dev/null || echo "No backups in src/obc_management/"

if [ -z "$1" ]; then
    echo ""
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 backups/db.sqlite3.backup.20250930_221241"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Show backup info
echo ""
echo "Backup file info:"
ls -lh "$BACKUP_FILE"
sqlite3 "$BACKUP_FILE" "
    SELECT 'Users: ' || COUNT(*) FROM auth_user
    UNION ALL
    SELECT 'Regions: ' || COUNT(*) FROM common_region
    UNION ALL
    SELECT 'Provinces: ' || COUNT(*) FROM common_province
    UNION ALL
    SELECT 'Communities: ' || COUNT(*) FROM communities_obc_community;
"

# Confirm restoration
read -p "Restore this backup to $DB_PATH? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restoration cancelled"
    exit 0
fi

# Create safety backup
SAFETY_BACKUP="${DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
echo ""
echo "Creating safety backup: $SAFETY_BACKUP"
cp "$DB_PATH" "$SAFETY_BACKUP"

# Restore
echo "Restoring $BACKUP_FILE to $DB_PATH"
cp "$BACKUP_FILE" "$DB_PATH"

# Verify
echo ""
echo "Verification:"
cd "$PROJECT_ROOT/src" && ../venv/bin/python manage.py shell -c "
from common.models import Region, Province, Municipality, Barangay
print(f'✅ Regions: {Region.objects.count()}')
print(f'✅ Provinces: {Province.objects.count()}')
print(f'✅ Municipalities: {Municipality.objects.count()}')
print(f'✅ Barangays: {Barangay.objects.count()}')
"

echo ""
echo "✅ Restoration complete!"
echo "Safety backup saved at: $SAFETY_BACKUP"
