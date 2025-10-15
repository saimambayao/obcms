#!/bin/bash
# Automatic database backup with proper path detection

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Get Django's configured database path
DB_PATH=$(cd "$PROJECT_ROOT/src" && ../venv/bin/python manage.py shell -c "
from django.conf import settings
print(settings.DATABASES['default']['NAME'])
" 2>/dev/null)

if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database not found at $DB_PATH"
    exit 1
fi

# Create backup directory if needed
BACKUP_DIR="$PROJECT_ROOT/backups"
mkdir -p "$BACKUP_DIR"

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db.sqlite3.backup.$TIMESTAMP"

echo "Backing up: $DB_PATH"
echo "        to: $BACKUP_FILE"

cp "$DB_PATH" "$BACKUP_FILE"

# Verify backup
ORIGINAL_SIZE=$(wc -c < "$DB_PATH")
BACKUP_SIZE=$(wc -c < "$BACKUP_FILE")

if [ "$ORIGINAL_SIZE" -eq "$BACKUP_SIZE" ]; then
    echo "✅ Backup successful! ($BACKUP_SIZE bytes)"

    # Show backup contents summary
    sqlite3 "$BACKUP_FILE" "
        SELECT 'Users: ' || COUNT(*) FROM auth_user
        UNION ALL
        SELECT 'Regions: ' || COUNT(*) FROM common_region
        UNION ALL
        SELECT 'Provinces: ' || COUNT(*) FROM common_province
        UNION ALL
        SELECT 'Communities: ' || COUNT(*) FROM communities_obc_community;
    "
else
    echo "❌ Backup verification failed!"
    exit 1
fi

# Clean old backups (keep last 10)
echo ""
echo "Cleaning old backups (keeping last 10)..."
ls -t "$BACKUP_DIR"/db.sqlite3.backup.* 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true

echo ""
echo "Recent backups:"
ls -lht "$BACKUP_DIR"/db.sqlite3.backup.* 2>/dev/null | head -n 5 || echo "No backups found"
