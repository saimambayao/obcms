#!/usr/bin/env bash
# SQLite Database Backup Script for OBCMS
# Creates timestamped backups of the OBC database with clean geographic data

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups/sqlite}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_PATH="${DB_PATH:-src/obc_management/db.sqlite3}"
BACKUP_FILE="${BACKUP_DIR}/obcms_backup_${TIMESTAMP}.sqlite3"
BACKUP_FILE_COMPRESSED="${BACKUP_FILE}.gz"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OBCMS SQLite Database Backup Utility            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

# Display configuration
echo -e "${GREEN}Configuration:${NC}"
echo -e "  Database: ${YELLOW}${DB_PATH}${NC}"
echo -e "  Backup Directory: ${YELLOW}${BACKUP_DIR}${NC}"
echo -e "  Timestamp: ${YELLOW}${TIMESTAMP}${NC}"
echo

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}✗${NC} Database file not found: ${DB_PATH}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Database file found"

# Get database size
DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
echo -e "  Current size: ${YELLOW}${DB_SIZE}${NC}"
echo

# Create backup using SQLite backup command (safer than cp)
echo -e "${BLUE}→${NC} Creating database backup..."
echo -e "  Output: ${YELLOW}${BACKUP_FILE}${NC}"

if sqlite3 "$DB_PATH" ".backup '${BACKUP_FILE}'" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backup created successfully"

    # Get file size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "  Size: ${YELLOW}${BACKUP_SIZE}${NC}"
else
    echo -e "${RED}✗${NC} Backup failed"
    exit 1
fi
echo

# Verify backup integrity
echo -e "${BLUE}→${NC} Verifying backup integrity..."
if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
    echo -e "${GREEN}✓${NC} Backup integrity verified"
else
    echo -e "${RED}✗${NC} Backup integrity check failed"
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

# Get Python path
PYTHON_CMD="python3"
if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
fi

# Count records
REGIONS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM communities_region;" 2>/dev/null)
PROVINCES=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM communities_province;" 2>/dev/null)
MUNICIPALITIES=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM communities_municipality;" 2>/dev/null)
BARANGAYS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM communities_barangay;" 2>/dev/null)

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
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/obcms_backup_*.sqlite3.gz 2>/dev/null | wc -l | xargs)
if [ "$BACKUP_COUNT" -gt 10 ]; then
    REMOVE_COUNT=$((BACKUP_COUNT - 10))
    ls -1t "$BACKUP_DIR"/obcms_backup_*.sqlite3.gz | tail -"$REMOVE_COUNT" | xargs rm -f
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
echo -e "  ${YELLOW}gunzip -c ${BACKUP_FILE_COMPRESSED} > src/obc_management/db.sqlite3${NC}"
echo
echo -e "${BLUE}Or use the restore script:${NC}"
echo -e "  ${YELLOW}./scripts/restore_sqlite.sh ${BACKUP_FILE_COMPRESSED}${NC}"
echo
