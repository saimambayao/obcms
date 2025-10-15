#!/usr/bin/env bash
# PostgreSQL Database Backup Script for OBCMS
# Creates timestamped backups of the OBC database with clean geographic data

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups/postgres}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE_NAME="${POSTGRES_DB:-obcms_local}"

# Parse DATABASE_URL if present
if [ ! -z "${DATABASE_URL:-}" ]; then
    # Extract database name from postgres://user:pass@host:port/dbname
    DATABASE_NAME=$(echo "$DATABASE_URL" | sed -E 's|postgres://[^/]*/(.*)|\1|')
fi

BACKUP_FILE="${BACKUP_DIR}/obcms_backup_${TIMESTAMP}.sql"
BACKUP_FILE_COMPRESSED="${BACKUP_FILE}.gz"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      OBCMS PostgreSQL Database Backup Utility         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

# Display configuration
echo -e "${GREEN}Configuration:${NC}"
echo -e "  Database: ${YELLOW}${DATABASE_NAME}${NC}"
echo -e "  Backup Directory: ${YELLOW}${BACKUP_DIR}${NC}"
echo -e "  Timestamp: ${YELLOW}${TIMESTAMP}${NC}"
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

# Create backup
echo -e "${BLUE}→${NC} Creating database backup..."
echo -e "  Output: ${YELLOW}${BACKUP_FILE}${NC}"

if pg_dump "$DATABASE_NAME" > "$BACKUP_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backup created successfully"

    # Get file size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "  Size: ${YELLOW}${BACKUP_SIZE}${NC}"
else
    echo -e "${RED}✗${NC} Backup failed"
    exit 1
fi
echo

# Compress backup
echo -e "${BLUE}→${NC} Compressing backup..."
if gzip -f "$BACKUP_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backup compressed successfully"

    COMPRESSED_SIZE=$(du -h "$BACKUP_FILE_COMPRESSED" | cut -f1)
    echo -e "  Compressed size: ${YELLOW}${COMPRESSED_SIZE}${NC}"
    echo -e "  File: ${YELLOW}${BACKUP_FILE_COMPRESSED}${NC}"
else
    echo -e "${YELLOW}⚠${NC} Compression failed (backup still available uncompressed)"
    BACKUP_FILE_COMPRESSED="$BACKUP_FILE"
fi
echo

# Database statistics
echo -e "${BLUE}→${NC} Database statistics:"
echo -e "${GREEN}Geographic Data (OBC Communities):${NC}"

# Count records (using psql)
REGIONS=$(psql -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM communities_region;" 2>/dev/null | xargs)
PROVINCES=$(psql -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM communities_province;" 2>/dev/null | xargs)
MUNICIPALITIES=$(psql -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM communities_municipality;" 2>/dev/null | xargs)
BARANGAYS=$(psql -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM communities_barangay;" 2>/dev/null | xargs)

echo -e "  Regions: ${YELLOW}${REGIONS}${NC}"
echo -e "  Provinces: ${YELLOW}${PROVINCES}${NC}"
echo -e "  Municipalities: ${YELLOW}${MUNICIPALITIES}${NC}"
echo -e "  Barangays: ${YELLOW}${BARANGAYS}${NC}"
echo

# List recent backups
echo -e "${BLUE}→${NC} Recent backups:"
ls -lht "$BACKUP_DIR" | head -6 | tail -5 | awk '{printf "  %s %s %s  %s\n", $6, $7, $8, $9}'
echo

# Cleanup old backups (keep last 10)
echo -e "${BLUE}→${NC} Cleaning up old backups (keeping last 10)..."
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/obcms_backup_*.sql.gz 2>/dev/null | wc -l | xargs)
if [ "$BACKUP_COUNT" -gt 10 ]; then
    REMOVE_COUNT=$((BACKUP_COUNT - 10))
    ls -1t "$BACKUP_DIR"/obcms_backup_*.sql.gz | tail -"$REMOVE_COUNT" | xargs rm -f
    echo -e "${GREEN}✓${NC} Removed $REMOVE_COUNT old backup(s)"
else
    echo -e "${GREEN}✓${NC} No cleanup needed (${BACKUP_COUNT} backups)"
fi
echo

# Success summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 Backup Complete! ✓                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}Backup file:${NC} ${BACKUP_FILE_COMPRESSED}"
echo

# Restore instructions
echo -e "${BLUE}To restore this backup:${NC}"
echo -e "  ${YELLOW}gunzip -c ${BACKUP_FILE_COMPRESSED} | psql ${DATABASE_NAME}${NC}"
echo
echo -e "${BLUE}Or use the restore script:${NC}"
echo -e "  ${YELLOW}./scripts/restore_postgres.sh ${BACKUP_FILE_COMPRESSED}${NC}"
echo
