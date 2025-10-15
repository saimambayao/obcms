#!/bin/bash
# OBCMS Database Backup Script
# Creates timestamped backup of PostgreSQL database

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups/postgres"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/obcms_backup_$TIMESTAMP.sql.gz"

echo -e "${YELLOW}⚙ Creating database backup...${NC}"

# Load environment
if [ -f "$PROJECT_ROOT/.env.production" ]; then
    source "$PROJECT_ROOT/.env.production"
else
    echo "Warning: .env.production not found, using defaults"
    POSTGRES_USER=${POSTGRES_USER:-obcms_user}
    POSTGRES_DB=${POSTGRES_DB:-obcms_prod}
fi

# Create backup
cd "$PROJECT_ROOT"
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

# Get file size
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo -e "${GREEN}✓ Backup created: $BACKUP_FILE ($SIZE)${NC}"

# Cleanup old backups (keep last 30 days)
echo -e "${YELLOW}⚙ Cleaning up old backups...${NC}"
find "$BACKUP_DIR" -name "obcms_backup_*.sql.gz" -mtime +30 -delete
echo -e "${GREEN}✓ Cleanup complete${NC}"

# List recent backups
echo -e "\n${YELLOW}Recent backups:${NC}"
ls -lh "$BACKUP_DIR" | tail -n 10
