#!/bin/bash
#
# Rollback Script
# Reverts to previous deployment in case of issues
#
# Usage: ./scripts/rollback.sh [--full]
#   --full: Perform full database and code rollback
#

set -e  # Exit on error
set -u  # Treat unset variables as an error

# Configuration
PROJECT_DIR="/var/www/obcms"
VENV_DIR="${PROJECT_DIR}/../venv"
SRC_DIR="${PROJECT_DIR}/src"
BACKUP_DIR="${HOME}/backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Parse arguments
FULL_ROLLBACK=false
if [ "${1:-}" == "--full" ]; then
    FULL_ROLLBACK=true
fi

echo "================================================================"
echo "OBCMS ROLLBACK"
echo "================================================================"
echo ""

if [ "$FULL_ROLLBACK" == "true" ]; then
    echo "Mode: FULL ROLLBACK (code + database)"
    echo ""
    echo "⚠️  WARNING: This will restore from backup!"
    echo "⚠️  All changes since last backup will be lost!"
else
    echo "Mode: CODE ROLLBACK (code only, database preserved)"
fi

echo ""
read -p "Continue with rollback? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled"
    exit 0
fi

log "Starting rollback..."

# Step 1: Enable Maintenance Mode
log "Step 1: Enabling maintenance mode..."
touch "${PROJECT_DIR}/MAINTENANCE_MODE"
log "  ✓ Maintenance mode enabled"

# Step 2: Stop Services
log "Step 2: Stopping services..."
sudo systemctl stop gunicorn || true
sudo systemctl stop celery || true
sudo systemctl stop celery-beat || true
log "  ✓ Services stopped"

if [ "$FULL_ROLLBACK" == "true" ]; then
    # Full Rollback: Restore database and code

    # Step 3: List available backups
    log "Step 3: Available backups..."
    echo ""
    echo "Available database backups:"
    ls -lht "$BACKUP_DIR"/obcms_*.{sql,sqlite3} 2>/dev/null | head -10
    echo ""

    read -p "Enter backup filename (or 'latest' for most recent): " BACKUP_CHOICE

    if [ "$BACKUP_CHOICE" == "latest" ]; then
        BACKUP_FILE=$(ls -t "$BACKUP_DIR"/obcms_*.{sql,sqlite3} 2>/dev/null | head -1)
    else
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_CHOICE"
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    log "Using backup: $BACKUP_FILE"

    # Step 4: Restore database
    log "Step 4: Restoring database..."

    if [[ "$BACKUP_FILE" == *.sql ]]; then
        # PostgreSQL restore
        log "  Restoring PostgreSQL database..."

        # Drop and recreate database
        psql -U postgres -c "DROP DATABASE IF EXISTS obcms_production;" || true
        psql -U postgres -c "CREATE DATABASE obcms_production;"

        # Restore from backup
        psql -U postgres obcms_production < "$BACKUP_FILE"

        log "  ✓ PostgreSQL database restored"
    elif [[ "$BACKUP_FILE" == *.sqlite3 ]]; then
        # SQLite restore
        log "  Restoring SQLite database..."
        cp "$BACKUP_FILE" "${SRC_DIR}/db.sqlite3"
        log "  ✓ SQLite database restored"
    else
        error "Unknown backup file type: $BACKUP_FILE"
        exit 1
    fi

    # Step 5: Revert code to match database
    log "Step 5: Reverting code..."

    cd "$PROJECT_DIR"

    # Show recent commits
    log "  Recent commits:"
    git log -5 --oneline

    echo ""
    read -p "Enter commit hash to revert to (or 'HEAD~1' for previous): " REVERT_TO

    if [ -z "$REVERT_TO" ]; then
        REVERT_TO="HEAD~1"
    fi

    git checkout "$REVERT_TO"

    CURRENT_COMMIT=$(git rev-parse HEAD)
    log "  ✓ Reverted to commit: $CURRENT_COMMIT"

else
    # Code-only rollback: Revert to previous commit

    # Step 3: Revert code
    log "Step 3: Reverting code to previous commit..."

    cd "$PROJECT_DIR"

    CURRENT_COMMIT=$(git rev-parse HEAD)
    log "  Current commit: $CURRENT_COMMIT"

    # Show recent commits
    log "  Recent commits:"
    git log -5 --oneline

    echo ""
    read -p "Enter commit to revert to (or press Enter for HEAD~1): " REVERT_TO

    if [ -z "$REVERT_TO" ]; then
        REVERT_TO="HEAD~1"
    fi

    git checkout "$REVERT_TO"

    NEW_COMMIT=$(git rev-parse HEAD)
    log "  ✓ Reverted to commit: $NEW_COMMIT"

    # Step 4: Reverse migrations (if needed)
    log "Step 4: Checking migrations..."

    cd "$SRC_DIR"
    source "${VENV_DIR}/bin/activate"

    # Show current migration state
    python manage.py showmigrations

    echo ""
    read -p "Reverse migrations? (yes/no): " REVERSE_MIGRATIONS

    if [ "$REVERSE_MIGRATIONS" == "yes" ]; then
        echo ""
        echo "Common migration points:"
        echo "  common 0012  - Before calendar models"
        echo "  common 0013  - Before task management extension"
        echo ""
        read -p "Enter app and migration (e.g., 'common 0012'): " APP MIGRATION

        if [ -n "$APP" ] && [ -n "$MIGRATION" ]; then
            python manage.py migrate "$APP" "$MIGRATION"
            log "  ✓ Migrations reversed"
        else
            warning "  No migrations reversed"
        fi
    else
        log "  Skipping migration reversal"
    fi
fi

# Step 6: Update dependencies
log "Step 6: Updating dependencies..."
cd "$SRC_DIR"
source "${VENV_DIR}/bin/activate"
pip install -r requirements/production.txt
log "  ✓ Dependencies updated"

# Step 7: Collect static files
log "Step 7: Collecting static files..."
python manage.py collectstatic --noinput
log "  ✓ Static files collected"

# Step 8: Clear caches
log "Step 8: Clearing caches..."
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
if command -v redis-cli &> /dev/null; then
    redis-cli FLUSHALL || true
fi
log "  ✓ Caches cleared"

# Step 9: Restart services
log "Step 9: Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat
sudo systemctl restart nginx

# Wait for services
sleep 3

# Verify services
GUNICORN_STATUS=$(systemctl is-active gunicorn || echo "failed")
NGINX_STATUS=$(systemctl is-active nginx || echo "failed")

if [ "$GUNICORN_STATUS" != "active" ]; then
    error "  Gunicorn failed to start!"
    error "  Check logs: journalctl -u gunicorn -n 50"
    exit 1
fi

if [ "$NGINX_STATUS" != "active" ]; then
    error "  Nginx failed to start!"
    exit 1
fi

log "  ✓ Services restarted"

# Step 10: Disable maintenance mode
log "Step 10: Disabling maintenance mode..."
rm "${PROJECT_DIR}/MAINTENANCE_MODE"
log "  ✓ Maintenance mode disabled"

# Verification
log "================================================================"
log "ROLLBACK VERIFICATION"
log "================================================================"

cd "$SRC_DIR"

# Run Django checks
log "Running Django checks..."
python manage.py check --deploy

# Test site
log "Testing site accessibility..."
SITE_URL="http://localhost:8000"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL" || echo "000")

if [ "$HTTP_STATUS" == "200" ] || [ "$HTTP_STATUS" == "302" ]; then
    log "  ✓ Site is accessible (HTTP $HTTP_STATUS)"
else
    warning "  Site returned HTTP $HTTP_STATUS"
fi

# Summary
log "================================================================"
log "ROLLBACK SUMMARY"
log "================================================================"

if [ "$FULL_ROLLBACK" == "true" ]; then
    log "Type: Full rollback (code + database)"
    log "Database restored from: $BACKUP_FILE"
else
    log "Type: Code rollback only"
fi

CURRENT_COMMIT=$(cd "$PROJECT_DIR" && git rev-parse HEAD)
log "Current commit: $CURRENT_COMMIT"
log ""
log "Rollback completed successfully!"
log ""
log "Recommended next steps:"
log "  1. Run smoke tests: ./scripts/smoke_test.sh"
log "  2. Monitor logs for errors"
log "  3. Verify critical functionality"
log ""

if [ "$FULL_ROLLBACK" == "true" ]; then
    warning "⚠️  Database was restored from backup"
    warning "⚠️  Any data created after backup time is lost"
fi

log "================================================================"

exit 0
