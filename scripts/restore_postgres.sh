#!/usr/bin/env bash
# PostgreSQL Database Restore Script for OBCMS
# Restores a backup created by backup_postgres.sh

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DATABASE_NAME="${POSTGRES_DB:-obcms_local}"

# Parse DATABASE_URL if present
if [ ! -z "${DATABASE_URL:-}" ]; then
    DATABASE_NAME=$(echo "$DATABASE_URL" | sed -E 's|postgres://[^/]*/(.*)|\1|')
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      OBCMS PostgreSQL Database Restore Utility        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

# Check for backup file argument
if [ $# -eq 0 ]; then
    echo -e "${RED}✗${NC} No backup file specified"
    echo
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  $0 <backup_file>"
    echo
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lht ./backups/postgres/*.sql.gz 2>/dev/null | head -5 | awk '{printf "  %s %s %s  %s\n", $6, $7, $8, $9}' || echo -e "  ${RED}No backups found${NC}"
    echo
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}✗${NC} Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Display configuration
echo -e "${GREEN}Configuration:${NC}"
echo -e "  Database: ${YELLOW}${DATABASE_NAME}${NC}"
echo -e "  Backup file: ${YELLOW}${BACKUP_FILE}${NC}"
echo -e "  Size: ${YELLOW}$(du -h "$BACKUP_FILE" | cut -f1)${NC}"
echo

# Check if PostgreSQL is accessible
echo -e "${BLUE}→${NC} Checking PostgreSQL connection..."
if ! pg_isready -d "$DATABASE_NAME" >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} Cannot connect to PostgreSQL database '${DATABASE_NAME}'"
    echo -e "${YELLOW}  Make sure PostgreSQL is running and DATABASE_URL is configured${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} PostgreSQL connection OK"
echo

# Warning
echo -e "${RED}⚠ WARNING:${NC} This will ${RED}REPLACE${NC} all data in database '${DATABASE_NAME}'"
echo
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

# Drop existing database
echo -e "${BLUE}→${NC} Dropping existing database..."
dropdb --if-exists "$DATABASE_NAME" 2>/dev/null || true
echo -e "${GREEN}✓${NC} Database dropped"
echo

# Create new database
echo -e "${BLUE}→${NC} Creating new database..."
createdb "$DATABASE_NAME"
echo -e "${GREEN}✓${NC} Database created"
echo

# Restore backup
echo -e "${BLUE}→${NC} Restoring backup..."
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo -e "  Decompressing and restoring..."
    if gunzip -c "$BACKUP_FILE" | psql -d "$DATABASE_NAME" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Restore completed successfully"
    else
        echo -e "${RED}✗${NC} Restore failed"
        exit 1
    fi
else
    if psql -d "$DATABASE_NAME" < "$BACKUP_FILE" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Restore completed successfully"
    else
        echo -e "${RED}✗${NC} Restore failed"
        exit 1
    fi
fi
echo

# Verify restoration
echo -e "${BLUE}→${NC} Verifying restoration..."
REGIONS=$(psql -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM communities_region;" 2>/dev/null | xargs)
PROVINCES=$(psql -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM communities_province;" 2>/dev/null | xargs)
MUNICIPALITIES=$(psql -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM communities_municipality;" 2>/dev/null | xargs)
BARANGAYS=$(psql -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM communities_barangay;" 2>/dev/null | xargs)

echo -e "${GREEN}Restored Geographic Data:${NC}"
echo -e "  Regions: ${YELLOW}${REGIONS}${NC}"
echo -e "  Provinces: ${YELLOW}${PROVINCES}${NC}"
echo -e "  Municipalities: ${YELLOW}${MUNICIPALITIES}${NC}"
echo -e "  Barangays: ${YELLOW}${BARANGAYS}${NC}"
echo

# Success summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 Restore Complete! ✓                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}Database '${DATABASE_NAME}' has been restored from:${NC}"
echo -e "  ${BACKUP_FILE}"
echo
