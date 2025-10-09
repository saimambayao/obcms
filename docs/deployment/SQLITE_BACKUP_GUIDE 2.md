# OBCMS SQLite Database Backup Guide

**Date:** 2025-10-06
**Status:** ✅ Production-Ready
**Purpose:** Quick guide for backing up and restoring the OBCMS SQLite database (development environment)

---

## Quick Start

### Create a Backup

```bash
# From project root
./scripts/backup_sqlite.sh
```

**Output:**
- Backup file: `backups/sqlite/obcms_backup_TIMESTAMP.sqlite3.gz`
- Size: ~9 MB compressed (from 128 MB database)
- Integrity verified automatically

### Restore a Backup

```bash
# List available backups
ls -lht backups/sqlite/

# Restore specific backup
./scripts/restore_sqlite.sh backups/sqlite/obcms_backup_20251006_235610.sqlite3.gz
```

---

## What's Included

✅ **Geographic Data (Clean OBC Database):**
- All 17 Regions with boundaries (GeoJSON)
- All 81 Provinces with center coordinates
- All 1,488 Municipalities/Cities
- All 42,046 Barangays

✅ **System Data:**
- User accounts and permissions
- MANA assessments
- Coordination records
- Policy recommendations
- Work items and tasks
- All Django migrations

---

## Backup Features

### Automatic Features
- ✅ **Integrity Check** - Verifies database before compression
- ✅ **Compression** - Reduces size from 128 MB to 9 MB (93% reduction)
- ✅ **Auto-Cleanup** - Keeps last 10 backups automatically
- ✅ **Statistics** - Shows row counts for key tables
- ✅ **Timestamped** - Format: `obcms_backup_YYYYMMDD_HHMMSS.sqlite3.gz`

### Safety Features
- ✅ **Backup Current DB** - Before restore, creates safety backup
- ✅ **Rollback on Error** - Restores previous database if restore fails
- ✅ **Confirmation Prompt** - Requires "yes" before replacing database

---

## Usage Examples

### Development Workflow

```bash
# Before migrations
./scripts/backup_sqlite.sh

# Run migrations
cd src
python manage.py migrate

# If something goes wrong, restore
cd ..
./scripts/restore_sqlite.sh backups/sqlite/obcms_backup_LATEST.sqlite3.gz
```

### Before Major Changes

```bash
# Create backup with note
./scripts/backup_sqlite.sh
# Note: Before implementing feature X

# Make changes...

# If needed, restore
./scripts/restore_sqlite.sh backups/sqlite/obcms_backup_TIMESTAMP.sqlite3.gz
```

### Regular Backups (Cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/obcms && ./scripts/backup_sqlite.sh
```

---

## Manual Backup (Alternative)

### Using SQLite Command

```bash
# Copy with integrity check
sqlite3 src/obc_management/db.sqlite3 ".backup backups/manual_backup.sqlite3"

# Compress
gzip backups/manual_backup.sqlite3
```

### Simple File Copy

```bash
# Stop Django server first!
cp src/obc_management/db.sqlite3 backups/db_backup_$(date +%Y%m%d).sqlite3
gzip backups/db_backup_*.sqlite3
```

---

## Restore Options

### Using Restore Script (Recommended)

```bash
./scripts/restore_sqlite.sh backups/sqlite/obcms_backup_20251006_235610.sqlite3.gz
```

Features:
- Backs up current database first
- Verifies integrity after restore
- Shows statistics
- Rollback on failure

### Manual Restore

```bash
# Decompress
gunzip -c backups/sqlite/obcms_backup_20251006_235610.sqlite3.gz > src/obc_management/db.sqlite3

# Verify integrity
sqlite3 src/obc_management/db.sqlite3 "PRAGMA integrity_check;"
```

---

## Database Statistics

After successful backup, you'll see:

```
Database statistics:
Geographic Data (OBC Communities):
  Regions: 17
  Provinces: 81
  Municipalities: 1488
  Barangays: 42046
```

This confirms the clean OBC database with all geographic data intact.

---

## File Sizes

| Type | Size | Notes |
|------|------|-------|
| Original Database | 128 MB | SQLite with all data |
| Uncompressed Backup | 122 MB | Clean backup file |
| Compressed Backup | 9 MB | Gzipped (93% compression) |

---

## Backup Strategy

### Development Environment

- **Frequency:** Before migrations, major changes
- **Retention:** Last 10 backups (automatic cleanup)
- **Storage:** Local `backups/sqlite/` directory

### What to Backup Before

✅ Database migrations (`python manage.py migrate`)
✅ Schema changes or model updates
✅ Bulk data imports or updates
✅ Testing destructive operations
✅ Major refactoring

---

## Troubleshooting

### Backup Issues

**Problem:** `sqlite3: command not found`

```bash
# macOS (usually pre-installed)
which sqlite3

# Install if needed (Homebrew)
brew install sqlite3
```

**Problem:** Database is locked

```bash
# Stop Django development server
# Then run backup
./scripts/backup_sqlite.sh
```

### Restore Issues

**Problem:** Restore fails with corruption

```bash
# The script automatically restores previous database
# Manual restore from safety backup
cp src/obc_management/db.sqlite3.before_restore_* src/obc_management/db.sqlite3
```

---

## Migration to PostgreSQL

When ready to migrate to PostgreSQL:

1. **Create final SQLite backup:**
   ```bash
   ./scripts/backup_sqlite.sh
   ```

2. **Set up PostgreSQL** (see [DATABASE_BACKUP_GUIDE.md](DATABASE_BACKUP_GUIDE.md))

3. **Update .env:**
   ```env
   DATABASE_URL=postgres://user:pass@localhost:5432/obcms_prod
   ```

4. **Run migrations:**
   ```bash
   cd src
   python manage.py migrate
   ```

5. **Start using PostgreSQL backups:**
   ```bash
   ./scripts/backup_postgres.sh
   ```

---

## Related Documentation

- **[PostgreSQL Backup Guide](DATABASE_BACKUP_GUIDE.md)** - For production/staging
- **[PostgreSQL Migration Summary](POSTGRESQL_MIGRATION_SUMMARY.md)** - Migration process
- **[Development Guide](../development/README.md)** - Development workflows

---

## Quick Reference

```bash
# Backup current database
./scripts/backup_sqlite.sh

# List backups
ls -lht backups/sqlite/

# Restore backup
./scripts/restore_sqlite.sh backups/sqlite/obcms_backup_TIMESTAMP.sqlite3.gz

# Check database size
du -h src/obc_management/db.sqlite3

# Verify database integrity
sqlite3 src/obc_management/db.sqlite3 "PRAGMA integrity_check;"
```

---

**Last Updated:** 2025-10-06
**Maintainer:** OBCMS Development Team
