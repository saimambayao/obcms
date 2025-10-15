#!/bin/bash
#
# Production Deployment Script
# Deploys integrated Calendar, Task Management, and Project Management systems
#
# Usage: ./scripts/deploy_production.sh
#

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

# Configuration
PROJECT_DIR="/var/www/obcms"
VENV_DIR="${PROJECT_DIR}/../venv"
SRC_DIR="${PROJECT_DIR}/src"
BACKUP_DIR="${HOME}/backups"
LOG_FILE="${PROJECT_DIR}/logs/deployment_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Header
echo "================================================================"
echo "OBCMS PRODUCTION DEPLOYMENT"
echo "================================================================"
echo ""
echo "Integrated Calendar, Task Management, and Project Management Systems"
echo ""
echo "This script will:"
echo "  1. Enable maintenance mode"
echo "  2. Backup current database"
echo "  3. Pull latest code"
echo "  4. Update dependencies"
echo "  5. Run database migrations"
echo "  6. Collect static files"
echo "  7. Clear caches"
echo "  8. Restart services"
echo "  9. Disable maintenance mode"
echo " 10. Verify deployment"
echo ""

# Confirmation
read -p "Continue with production deployment? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled by user"
    exit 0
fi

log "Starting deployment..."

# Step 1: Enable Maintenance Mode
log "Step 1/10: Enabling maintenance mode..."
touch "${PROJECT_DIR}/MAINTENANCE_MODE"
log "  ✓ Maintenance mode enabled"

# Step 2: Backup Database
log "Step 2/10: Backing up database..."
mkdir -p "$BACKUP_DIR"

# Detect database type from environment
cd "$SRC_DIR"
source "${VENV_DIR}/bin/activate"

DB_ENGINE=$(${VENV_DIR}/bin/python -c "
from django.conf import settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
import django
django.setup()
from django.conf import settings
print(settings.DATABASES['default']['ENGINE'])
" 2>/dev/null || echo "unknown")

BACKUP_FILE="${BACKUP_DIR}/obcms_$(date +%Y%m%d_%H%M%S)"

if [[ "$DB_ENGINE" == *"postgresql"* ]]; then
    log "  Detected PostgreSQL database"
    pg_dump -U postgres obcms_production > "${BACKUP_FILE}.sql"
    log "  ✓ PostgreSQL backup created: ${BACKUP_FILE}.sql"
elif [[ "$DB_ENGINE" == *"sqlite"* ]]; then
    log "  Detected SQLite database"
    cp "${SRC_DIR}/db.sqlite3" "${BACKUP_FILE}.sqlite3"
    log "  ✓ SQLite backup created: ${BACKUP_FILE}.sqlite3"
else
    warning "  Unknown database engine: $DB_ENGINE"
    warning "  Manual backup recommended"
fi

# Verify backup created
if [ ! -f "${BACKUP_FILE}.sql" ] && [ ! -f "${BACKUP_FILE}.sqlite3" ]; then
    error "Backup file not created! Aborting deployment."
    rm "${PROJECT_DIR}/MAINTENANCE_MODE"
    exit 1
fi

# Step 3: Stop Services
log "Step 3/10: Stopping services..."
sudo systemctl stop gunicorn || warning "  gunicorn not running"
sudo systemctl stop celery || warning "  celery not running"
sudo systemctl stop celery-beat || warning "  celery-beat not running"
log "  ✓ Services stopped"

# Step 4: Pull Latest Code
log "Step 4/10: Pulling latest code..."
cd "$PROJECT_DIR"

# Record current commit for rollback
PREVIOUS_COMMIT=$(git rev-parse HEAD)
log "  Current commit: $PREVIOUS_COMMIT"

# Pull latest
git fetch origin
git checkout main
git pull origin main

CURRENT_COMMIT=$(git rev-parse HEAD)
log "  New commit: $CURRENT_COMMIT"

if [ "$PREVIOUS_COMMIT" == "$CURRENT_COMMIT" ]; then
    warning "  No new commits to deploy"
fi

# Step 5: Update Dependencies
log "Step 5/10: Updating dependencies..."
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install -r requirements/production.txt
log "  ✓ Dependencies updated"

# Step 6: Run Database Migrations
log "Step 6/10: Running database migrations..."
cd "$SRC_DIR"

# Show migration plan
log "  Migration plan:"
${VENV_DIR}/bin/python manage.py migrate --plan | tee -a "$LOG_FILE"

# Run migrations
${VENV_DIR}/bin/python manage.py migrate

# Verify migrations
UNAPPLIED=$(${VENV_DIR}/bin/python manage.py showmigrations | grep "\[ \]" | wc -l)
if [ "$UNAPPLIED" -gt 0 ]; then
    error "  $UNAPPLIED migrations not applied!"
    error "  Deployment may be incomplete. Please review."
else
    log "  ✓ All migrations applied successfully"
fi

# Step 7: Collect Static Files
log "Step 7/10: Collecting static files..."
${VENV_DIR}/bin/python manage.py collectstatic --noinput
log "  ✓ Static files collected"

# Step 8: Clear Caches
log "Step 8/10: Clearing caches..."

# Django cache
${VENV_DIR}/bin/python manage.py shell << EOF
from django.core.cache import cache
cache.clear()
print("Django cache cleared")
EOF

# Redis cache (if available)
if command -v redis-cli &> /dev/null; then
    redis-cli FLUSHALL
    log "  ✓ Redis cache cleared"
fi

log "  ✓ Caches cleared"

# Step 9: Restart Services
log "Step 9/10: Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat
sudo systemctl restart nginx

# Wait for services to start
sleep 3

# Verify services started
GUNICORN_STATUS=$(systemctl is-active gunicorn || echo "failed")
CELERY_STATUS=$(systemctl is-active celery || echo "failed")
NGINX_STATUS=$(systemctl is-active nginx || echo "failed")

if [ "$GUNICORN_STATUS" != "active" ]; then
    error "  Gunicorn failed to start!"
    exit 1
fi

if [ "$CELERY_STATUS" != "active" ]; then
    warning "  Celery failed to start (non-critical)"
fi

if [ "$NGINX_STATUS" != "active" ]; then
    error "  Nginx failed to start!"
    exit 1
fi

log "  ✓ Services restarted successfully"
log "    - Gunicorn: $GUNICORN_STATUS"
log "    - Celery: $CELERY_STATUS"
log "    - Nginx: $NGINX_STATUS"

# Step 10: Disable Maintenance Mode
log "Step 10/10: Disabling maintenance mode..."
rm "${PROJECT_DIR}/MAINTENANCE_MODE"
log "  ✓ Maintenance mode disabled"

# Deployment Verification
log "================================================================"
log "DEPLOYMENT VERIFICATION"
log "================================================================"

# Run Django checks
log "Running Django deployment checks..."
${VENV_DIR}/bin/python manage.py check --deploy

# Test site accessibility
log "Testing site accessibility..."
SITE_URL="http://localhost:8000"  # Update with actual domain
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL" || echo "000")

if [ "$HTTP_STATUS" == "200" ] || [ "$HTTP_STATUS" == "302" ]; then
    log "  ✓ Site is accessible (HTTP $HTTP_STATUS)"
else
    error "  Site returned HTTP $HTTP_STATUS"
    warning "  Please check logs and verify manually"
fi

# Summary
log "================================================================"
log "DEPLOYMENT SUMMARY"
log "================================================================"
log "Status: COMPLETED"
log "Previous commit: $PREVIOUS_COMMIT"
log "Current commit: $CURRENT_COMMIT"
log "Backup location: ${BACKUP_FILE}.*"
log "Deployment log: $LOG_FILE"
log ""
log "Next steps:"
log "  1. Run smoke tests"
log "  2. Monitor error logs"
log "  3. Verify calendar, tasks, and project features"
log "  4. Check user feedback"
log ""
log "Smoke test command:"
log "  ./scripts/smoke_test.sh"
log ""
log "Monitor logs:"
log "  tail -f ${PROJECT_DIR}/logs/django.log"
log "  tail -f ${PROJECT_DIR}/logs/gunicorn.log"
log "  tail -f ${PROJECT_DIR}/logs/celery.log"
log ""

# Check for errors in recent logs
log "Recent errors in Django log:"
if [ -f "${PROJECT_DIR}/logs/django.log" ]; then
    RECENT_ERRORS=$(tail -100 "${PROJECT_DIR}/logs/django.log" | grep -i error | wc -l)
    if [ "$RECENT_ERRORS" -gt 0 ]; then
        warning "  Found $RECENT_ERRORS error entries in recent logs"
        warning "  Please review: tail -100 ${PROJECT_DIR}/logs/django.log | grep -i error"
    else
        log "  ✓ No errors found in recent logs"
    fi
fi

log "================================================================"
log "Deployment completed successfully at $(date)"
log "================================================================"

exit 0
