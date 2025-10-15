#!/bin/bash

# OBCMS Database Backup Script for Docker
# This script creates automated backups of the PostgreSQL database

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${POSTGRES_DB}_backup_${TIMESTAMP}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to create backup
create_backup() {
    print_status "Starting database backup..."
    print_status "Database: ${POSTGRES_DB}"
    print_status "Backup file: ${BACKUP_FILE}"

    # Create backup directory if it doesn't exist
    mkdir -p "${BACKUP_DIR}"

    # Perform database backup
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
        -h "${POSTGRES_HOST:-db}" \
        -p "${POSTGRES_PORT:-5432}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        --format=custom \
        --file="${BACKUP_DIR}/${BACKUP_FILE}"

    # Compress the backup
    print_status "Compressing backup..."
    gzip "${BACKUP_DIR}/${BACKUP_FILE}"

    print_success "Backup created: ${BACKUP_DIR}/${COMPRESSED_FILE}"

    # Show backup size
    BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${COMPRESSED_FILE}" | cut -f1)
    print_status "Backup size: ${BACKUP_SIZE}"
}

# Function to cleanup old backups
cleanup_old_backups() {
    print_status "Cleaning up backups older than ${RETENTION_DAYS} days..."

    # Find and remove old backup files
    DELETED=$(find "${BACKUP_DIR}" \
        -name "${POSTGRES_DB}_backup_*.sql.gz" \
        -type f \
        -mtime "+${RETENTION_DAYS}" \
        -delete \
        -print | wc -l)

    if [ "${DELETED}" -gt 0 ]; then
        print_success "Deleted ${DELETED} old backup files"
    else
        print_status "No old backup files to delete"
    fi
}

# Function to list backups
list_backups() {
    print_status "Available backups:"
    if [ -d "${BACKUP_DIR}" ] && [ "$(ls -A "${BACKUP_DIR}" 2>/dev/null)" ]; then
        ls -lah "${BACKUP_DIR}"/"${POSTGRES_DB}"_backup_*.sql.gz | \
        awk '{print $9 " (" $5 ", " $6 " " $7 " " $8 ")"}'
    else
        print_warning "No backup files found"
    fi
}

# Function to restore backup
restore_backup() {
    if [ -z "$1" ]; then
        print_error "Please specify a backup file to restore"
        print_status "Usage: $0 restore <backup_file>"
        exit 1
    fi

    BACKUP_FILE_TO_RESTORE="$1"

    if [ ! -f "${BACKUP_DIR}/${BACKUP_FILE_TO_RESTORE}" ]; then
        print_error "Backup file not found: ${BACKUP_DIR}/${BACKUP_FILE_TO_RESTORE}"
        exit 1
    fi

    print_warning "This will RESTORE the database from backup"
    print_warning "All current data will be REPLACED"
    read -p "Are you sure you want to continue? (yes/no): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_status "Restore cancelled"
        exit 1
    fi

    print_status "Restoring database from: ${BACKUP_FILE_TO_RESTORE}"

    # Extract if compressed
    if [[ "${BACKUP_FILE_TO_RESTORE}" == *.gz ]]; then
        TEMP_FILE="${BACKUP_FILE_TO_RESTORE%.gz}"
        gunzip -c "${BACKUP_DIR}/${BACKUP_FILE_TO_RESTORE}" > "${BACKUP_DIR}/${TEMP_FILE}"
        BACKUP_FILE_TO_RESTORE="${TEMP_FILE}"
    fi

    # Restore database
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_restore \
        -h "${POSTGRES_HOST:-db}" \
        -p "${POSTGRES_PORT:-5432}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        "${BACKUP_DIR}/${BACKUP_FILE_TO_RESTORE}"

    # Clean up temporary file
    if [[ "${TEMP_FILE}" == *_temp ]]; then
        rm -f "${BACKUP_DIR}/${TEMP_FILE}"
    fi

    print_success "Database restored successfully"
}

# Function to verify backup
verify_backup() {
    if [ -z "$1" ]; then
        print_error "Please specify a backup file to verify"
        print_status "Usage: $0 verify <backup_file>"
        exit 1
    fi

    BACKUP_FILE_TO_VERIFY="$1"

    if [ ! -f "${BACKUP_DIR}/${BACKUP_FILE_TO_VERIFY}" ]; then
        print_error "Backup file not found: ${BACKUP_DIR}/${BACKUP_FILE_TO_VERIFY}"
        exit 1
    fi

    print_status "Verifying backup file: ${BACKUP_FILE_TO_VERIFY}"

    # Extract if compressed for verification
    if [[ "${BACKUP_FILE_TO_VERIFY}" == *.gz ]]; then
        TEMP_FILE="${BACKUP_FILE_TO_VERIFY%.gz}_temp"
        gunzip -c "${BACKUP_DIR}/${BACKUP_FILE_TO_VERIFY}" > "${BACKUP_DIR}/${TEMP_FILE}"
        BACKUP_FILE_TO_VERIFY="${TEMP_FILE}"
    fi

    # Verify backup file integrity
    if pg_restore --list "${BACKUP_DIR}/${BACKUP_FILE_TO_VERIFY}" > /dev/null 2>&1; then
        print_success "Backup file is valid"
    else
        print_error "Backup file is corrupted or invalid"
        exit 1
    fi

    # Clean up temporary file
    if [[ "${TEMP_FILE}" == *_temp ]]; then
        rm -f "${BACKUP_DIR}/${TEMP_FILE}"
    fi
}

# Function to show usage
show_usage() {
    echo "OBCMS Database Backup Script for Docker"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  create          Create a new database backup (default)"
    echo "  list            List all available backups"
    echo "  restore <file>  Restore database from backup file"
    echo "  verify <file>   Verify backup file integrity"
    echo "  cleanup         Remove old backup files"
    echo "  help            Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  POSTGRES_DB         Database name (default: obcms)"
    echo "  POSTGRES_USER       Database user (default: obcms)"
    echo "  POSTGRES_PASSWORD   Database password"
    echo "  POSTGRES_HOST       Database host (default: db)"
    echo "  POSTGRES_PORT       Database port (default: 5432)"
    echo "  BACKUP_DIR          Backup directory (default: /backups)"
    echo "  BACKUP_RETENTION_DAYS  Backup retention period (default: 30)"
    echo ""
    echo "Examples:"
    echo "  $0 create                           # Create backup"
    echo "  $0 restore obcms_backup_20231201_120000.sql.gz  # Restore backup"
    echo "  $0 verify obcms_backup_20231201_120000.sql.gz   # Verify backup"
    echo ""
}

# Main script logic
main() {
    case "${1:-create}" in
        create)
            create_backup
            cleanup_old_backups
            ;;
        list)
            list_backups
            ;;
        restore)
            restore_backup "$2"
            ;;
        verify)
            verify_backup "$2"
            ;;
        cleanup)
            cleanup_old_backups
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Check required environment variables
if [ -z "${POSTGRES_PASSWORD}" ]; then
    print_error "POSTGRES_PASSWORD environment variable is required"
    exit 1
fi

# Set default values
export POSTGRES_DB="${POSTGRES_DB:-obcms}"
export POSTGRES_USER="${POSTGRES_USER:-obcms}"
export POSTGRES_HOST="${POSTGRES_HOST:-db}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"

# Run main function with all arguments
main "$@"