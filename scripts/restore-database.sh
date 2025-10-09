#!/bin/bash
# OBCMS Database Restore Script
# Restores PostgreSQL database from backup

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if backup file provided
if [ -z "$1" ]; then
    echo -e "${RED}✗ ERROR: No backup file specified${NC}"
    echo -e "${YELLOW}Usage: $0 <backup-file>${NC}"
    echo -e "${YELLOW}Example: $0 backups/postgres/obcms_backup_20251009_120000.sql.gz${NC}"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}✗ ERROR: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Load environment
if [ -f "$PROJECT_ROOT/.env.production" ]; then
    source "$PROJECT_ROOT/.env.production"
else
    echo -e "${RED}✗ ERROR: .env.production not found${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠ WARNING: This will REPLACE the current database!${NC}"
echo -e "${YELLOW}Database: $POSTGRES_DB${NC}"
echo -e "${YELLOW}Backup file: $BACKUP_FILE${NC}"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

# Create a pre-restore backup
echo -e "${YELLOW}⚙ Creating pre-restore backup...${NC}"
cd "$PROJECT_ROOT"
./scripts/backup-database.sh

# Stop web and celery services
echo -e "${YELLOW}⚙ Stopping application services...${NC}"
docker-compose -f docker-compose.prod.yml stop web celery celery-beat
echo -e "${GREEN}✓ Services stopped${NC}"

# Restore database
echo -e "${YELLOW}⚙ Restoring database from backup...${NC}"
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | docker-compose -f docker-compose.prod.yml exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
else
    cat "$BACKUP_FILE" | docker-compose -f docker-compose.prod.yml exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
fi
echo -e "${GREEN}✓ Database restored${NC}"

# Restart services
echo -e "${YELLOW}⚙ Restarting application services...${NC}"
docker-compose -f docker-compose.prod.yml up -d web celery celery-beat
echo -e "${GREEN}✓ Services restarted${NC}"

echo -e "\n${GREEN}✓ Database restore complete${NC}"
echo -e "${YELLOW}Please verify the application is working correctly${NC}\n"
