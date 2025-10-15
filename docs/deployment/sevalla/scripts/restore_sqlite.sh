#!/usr/bin/env bash
# SQLite Database Restore Script for OBCMS
# Restores a backup created by backup_sqlite.sh

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_PATH="${DB_PATH:-src/obc_management/db.sqlite3}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OBCMS SQLite Database Restore Utility           ║${NC}"
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
    ls -lht ./backups/sqlite/*.sqlite3.gz 2>/dev/null | head -5 | awk '{printf "  %s %s %s  %s\n", $6, $7, $8, $9}' || echo -e "  ${RED}No backups found${NC}"
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
echo -e "  Database: ${YELLOW}${DB_PATH}${NC}"
echo -e "  Backup file: ${YELLOW}${BACKUP_FILE}${NC}"
echo -e "  Size: ${YELLOW}$(du -h "$BACKUP_FILE" | cut -f1)${NC}"
echo

# Check if current database exists
if [ -f "$DB_PATH" ]; then
    CURRENT_SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo -e "  Current database size: ${YELLOW}${CURRENT_SIZE}${NC}"
fi
echo

# Warning
echo -e "${RED}⚠ WARNING:${NC} This will ${RED}REPLACE${NC} the database at '${DB_PATH}'"
echo
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

# Backup current database before restore
if [ -f "$DB_PATH" ]; then
    echo -e "${BLUE}→${NC} Backing up current database..."
    CURRENT_BACKUP="${DB_PATH}.before_restore_$(date +%Y%m%d_%H%M%S)"
    cp "$DB_PATH" "$CURRENT_BACKUP"
    echo -e "${GREEN}✓${NC} Current database backed up to:"
    echo -e "  ${YELLOW}${CURRENT_BACKUP}${NC}"
    echo
fi

# Restore backup
echo -e "${BLUE}→${NC} Restoring backup..."
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo -e "  Decompressing and restoring..."
    if gunzip -c "$BACKUP_FILE" > "$DB_PATH" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Restore completed successfully"
    else
        echo -e "${RED}✗${NC} Restore failed"
        if [ -f "$CURRENT_BACKUP" ]; then
            echo -e "${YELLOW}→${NC} Restoring previous database..."
            mv "$CURRENT_BACKUP" "$DB_PATH"
            echo -e "${GREEN}✓${NC} Previous database restored"
        fi
        exit 1
    fi
else
    if cp "$BACKUP_FILE" "$DB_PATH" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Restore completed successfully"
    else
        echo -e "${RED}✗${NC} Restore failed"
        if [ -f "$CURRENT_BACKUP" ]; then
            echo -e "${YELLOW}→${NC} Restoring previous database..."
            mv "$CURRENT_BACKUP" "$DB_PATH"
            echo -e "${GREEN}✓${NC} Previous database restored"
        fi
        exit 1
    fi
fi
echo

# Verify integrity
echo -e "${BLUE}→${NC} Verifying database integrity..."
if sqlite3 "$DB_PATH" "PRAGMA integrity_check;" | grep -q "ok"; then
    echo -e "${GREEN}✓${NC} Database integrity verified"
else
    echo -e "${RED}✗${NC} Database integrity check failed"
    if [ -f "$CURRENT_BACKUP" ]; then
        echo -e "${YELLOW}→${NC} Restoring previous database..."
        mv "$CURRENT_BACKUP" "$DB_PATH"
        echo -e "${GREEN}✓${NC} Previous database restored"
    fi
    exit 1
fi
echo

# Verify restoration
echo -e "${BLUE}→${NC} Verifying restoration..."
REGIONS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM communities_region;" 2>/dev/null)
PROVINCES=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM communities_province;" 2>/dev/null)
MUNICIPALITIES=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM communities_municipality;" 2>/dev/null)
BARANGAYS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM communities_barangay;" 2>/dev/null)

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
echo -e "${YELLOW}Database restored from:${NC}"
echo -e "  ${BACKUP_FILE}"
echo
if [ -f "$CURRENT_BACKUP" ]; then
    echo -e "${YELLOW}Previous database saved at:${NC}"
    echo -e "  ${CURRENT_BACKUP}"
    echo
fi
