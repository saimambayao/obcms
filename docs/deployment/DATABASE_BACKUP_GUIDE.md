# OBCMS PostgreSQL Database Backup Guide

**Date:** 2025-10-06
**Status:** ✅ Production-Ready
**Purpose:** Complete guide for backing up and restoring the OBCMS PostgreSQL database with clean OBC geographic data

---

## Quick Start

### Create a Backup

```bash
# From project root
./scripts/backup_postgres.sh
```

### Restore a Backup

```bash
# List available backups
ls -lht backups/postgres/

# Restore specific backup
./scripts/restore_postgres.sh backups/postgres/obcms_backup_20251006_143000.sql.gz
```

---

## Overview

The OBCMS database backup system provides:

- **Automated backups** with timestamps
- **Compressed storage** (gzip)
- **Automatic cleanup** (keeps last 10 backups)
- **Database statistics** (regions, provinces, municipalities, barangays)
- **Easy restoration** with verification
- **Clean OBC data** (regions, provinces, municipalities, cities, barangays)

### What's Included in Backups

✅ **Geographic Data:**
- Regions (with boundaries in GeoJSON)
- Provinces (with center coordinates)
- Municipalities/Cities (with bounding boxes)
- Barangays (complete OBC communities)

✅ **System Data:**
- User accounts and permissions
- MANA assessments and data
- Coordination records
- Policy recommendations
- Work items and tasks
- All Django migrations

✅ **Metadata:**
- Timestamps and audit trails
- Database schema and indexes
- Foreign key relationships

---

## Backup Scripts

### 1. Backup Script (`scripts/backup_postgres.sh`)

**Features:**
- Creates timestamped SQL dump
- Compresses with gzip
- Shows database statistics
- Auto-cleanup (keeps last 10)
- Colored output and progress indicators

**Usage:**

```bash
# Default backup (uses DATABASE_URL from .env)
./scripts/backup_postgres.sh

# Custom backup directory
BACKUP_DIR=/path/to/backups ./scripts/backup_postgres.sh

# Custom database name
POSTGRES_DB=obcms_custom ./scripts/backup_postgres.sh
```

**Output:**

```
╔════════════════════════════════════════════════════════╗
║      OBCMS PostgreSQL Database Backup Utility         ║
╚════════════════════════════════════════════════════════╝

Configuration:
  Database: obcms_local
  Backup Directory: ./backups/postgres
  Timestamp: 20251006_143527

→ Checking PostgreSQL connection...
✓ PostgreSQL connection OK

→ Creating database backup...
  Output: ./backups/postgres/obcms_backup_20251006_143527.sql
✓ Backup created successfully
  Size: 2.4M

→ Compressing backup...
✓ Backup compressed successfully
  Compressed size: 456K
  File: ./backups/postgres/obcms_backup_20251006_143527.sql.gz

→ Database statistics:
Geographic Data (OBC Communities):
  Regions: 17
  Provinces: 81
  Municipalities: 1488
  Barangays: 42046

→ Recent backups:
  Oct  6 14:35  obcms_backup_20251006_143527.sql.gz
  Oct  6 12:20  obcms_backup_20251006_122015.sql.gz
  Oct  5 16:45  obcms_backup_20251005_164532.sql.gz

→ Cleaning up old backups (keeping last 10)...
✓ No cleanup needed (3 backups)

╔════════════════════════════════════════════════════════╗
║                 Backup Complete! ✓                     ║
╚════════════════════════════════════════════════════════╝

Backup file: ./backups/postgres/obcms_backup_20251006_143527.sql.gz

To restore this backup:
  gunzip -c ./backups/postgres/obcms_backup_20251006_143527.sql.gz | psql obcms_local

Or use the restore script:
  ./scripts/restore_postgres.sh ./backups/postgres/obcms_backup_20251006_143527.sql.gz
```

---

### 2. Restore Script (`scripts/restore_postgres.sh`)

**Features:**
- Lists available backups
- Safety confirmation prompt
- Drops and recreates database
- Decompresses automatically
- Verifies restoration

**Usage:**

```bash
# Show available backups
./scripts/restore_postgres.sh

# Restore specific backup
./scripts/restore_postgres.sh backups/postgres/obcms_backup_20251006_143527.sql.gz
```

**Safety Warning:**

```
⚠ WARNING: This will REPLACE all data in database 'obcms_local'

Are you sure you want to continue? (yes/no): yes
```

**Output:**

```
╔════════════════════════════════════════════════════════╗
║      OBCMS PostgreSQL Database Restore Utility        ║
╚════════════════════════════════════════════════════════╝

Configuration:
  Database: obcms_local
  Backup file: backups/postgres/obcms_backup_20251006_143527.sql.gz
  Size: 456K

→ Checking PostgreSQL connection...
✓ PostgreSQL connection OK

⚠ WARNING: This will REPLACE all data in database 'obcms_local'

Are you sure you want to continue? (yes/no): yes

→ Dropping existing database...
✓ Database dropped

→ Creating new database...
✓ Database created

→ Restoring backup...
  Decompressing and restoring...
✓ Restore completed successfully

→ Verifying restoration...
Restored Geographic Data:
  Regions: 17
  Provinces: 81
  Municipalities: 1488
  Barangays: 42046

╔════════════════════════════════════════════════════════╗
║                 Restore Complete! ✓                    ║
╚════════════════════════════════════════════════════════╝

Database 'obcms_local' has been restored from:
  backups/postgres/obcms_backup_20251006_143527.sql.gz
```

---

## Manual Backup Methods

### Using pg_dump Directly

```bash
# Basic backup
pg_dump obcms_local > backup.sql

# Compressed backup
pg_dump obcms_local | gzip > backup.sql.gz

# Custom format (faster restore)
pg_dump -Fc obcms_local > backup.dump

# With connection string
pg_dump postgres://user:pass@localhost:5432/obcms_local > backup.sql
```

### Using psql for Restore

```bash
# From SQL file
psql obcms_local < backup.sql

# From compressed SQL
gunzip -c backup.sql.gz | psql obcms_local

# From custom format
pg_restore -d obcms_local backup.dump
```

---

## Backup Strategies

### Development Environment

**Frequency:** Before major changes
**Retention:** 10 most recent backups (automatic)
**Storage:** Local `backups/postgres/` directory

```bash
# Before migrations
./scripts/backup_postgres.sh

# Before schema changes
./scripts/backup_postgres.sh

# Before bulk data imports
./scripts/backup_postgres.sh
```

### Staging Environment

**Frequency:** Daily (automated via cron)
**Retention:** 30 days
**Storage:** Local + cloud storage (S3/Google Cloud)

```bash
# Cron job (daily at 2 AM)
0 2 * * * cd /path/to/obcms && ./scripts/backup_postgres.sh

# Manual backup before deployment
./scripts/backup_postgres.sh
```

### Production Environment

**Frequency:**
- Daily full backups
- Hourly incremental (if using WAL archiving)

**Retention:**
- Daily: 30 days
- Weekly: 12 weeks
- Monthly: 12 months

**Storage:**
- Primary: Cloud storage (encrypted)
- Secondary: Off-site backup
- Tertiary: Local snapshots

```bash
# Full backup (daily)
./scripts/backup_postgres.sh

# Copy to cloud storage
aws s3 cp backups/postgres/obcms_backup_*.sql.gz s3://obcms-backups/production/

# Or Google Cloud
gsutil cp backups/postgres/obcms_backup_*.sql.gz gs://obcms-backups/production/
```

---

## Advanced Backup Options

### Backup Specific Tables

```bash
# Only geographic data
pg_dump -t communities_region \
        -t communities_province \
        -t communities_municipality \
        -t communities_barangay \
        obcms_local > geographic_data_backup.sql

# Only MANA data
pg_dump -t mana_* obcms_local > mana_backup.sql
```

### Backup with Exclusions

```bash
# Exclude large tables (e.g., logs)
pg_dump --exclude-table=django_admin_log \
        --exclude-table=celery_* \
        obcms_local > backup_no_logs.sql
```

### Parallel Backup (Faster)

```bash
# Use multiple CPUs
pg_dump -Fd -j 4 obcms_local -f backup_dir/

# Restore parallel backup
pg_restore -Fd -j 4 -d obcms_local backup_dir/
```

---

## Automated Backups

### Using Cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add backup jobs
# Daily backup at 2 AM
0 2 * * * cd /path/to/obcms && ./scripts/backup_postgres.sh >> /var/log/obcms_backup.log 2>&1

# Weekly cleanup (Sunday at 3 AM)
0 3 * * 0 find /path/to/obcms/backups/postgres -name "*.sql.gz" -mtime +30 -delete
```

### Using systemd Timer (Linux)

Create `/etc/systemd/system/obcms-backup.service`:

```ini
[Unit]
Description=OBCMS PostgreSQL Backup
After=postgresql.service

[Service]
Type=oneshot
User=obcms
WorkingDirectory=/opt/obcms
ExecStart=/opt/obcms/scripts/backup_postgres.sh
StandardOutput=journal
StandardError=journal
```

Create `/etc/systemd/system/obcms-backup.timer`:

```ini
[Unit]
Description=OBCMS Backup Timer
Requires=obcms-backup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable obcms-backup.timer
sudo systemctl start obcms-backup.timer
```

---

## Backup Verification

### Verify Backup Integrity

```bash
# Test decompression
gunzip -t backup.sql.gz
echo $?  # Should be 0

# Test SQL syntax (dry run)
gunzip -c backup.sql.gz | psql -d postgres --single-transaction --set ON_ERROR_STOP=on -f - --dry-run
```

### Verify Restoration

```bash
# Create test database
createdb obcms_test

# Restore to test database
gunzip -c backup.sql.gz | psql obcms_test

# Check row counts
psql obcms_test -c "SELECT COUNT(*) FROM communities_region;"
psql obcms_test -c "SELECT COUNT(*) FROM communities_barangay;"

# Drop test database
dropdb obcms_test
```

---

## Disaster Recovery

### Recovery Scenarios

#### 1. Accidental Data Deletion

```bash
# Immediate action: Stop all writes
# Restore from most recent backup
./scripts/restore_postgres.sh backups/postgres/obcms_backup_LATEST.sql.gz
```

#### 2. Database Corruption

```bash
# Check database integrity
psql obcms_local -c "SELECT pg_database_size('obcms_local');"

# If corrupted, restore from backup
./scripts/restore_postgres.sh backups/postgres/obcms_backup_LATEST.sql.gz

# Verify restoration
cd src
python manage.py check --database default
```

#### 3. Hardware Failure

```bash
# On new server:
# 1. Install PostgreSQL
# 2. Copy backup from cloud storage
aws s3 cp s3://obcms-backups/production/obcms_backup_LATEST.sql.gz ./

# 3. Restore database
./scripts/restore_postgres.sh obcms_backup_LATEST.sql.gz
```

### Recovery Time Objectives (RTO)

| Backup Size | Restore Time | RTO Target |
|------------|--------------|------------|
| < 100 MB   | < 1 minute   | 5 minutes  |
| 100-500 MB | 1-5 minutes  | 15 minutes |
| 500 MB-2 GB| 5-20 minutes | 1 hour     |
| > 2 GB     | 20+ minutes  | 4 hours    |

---

## Troubleshooting

### Backup Issues

**Problem:** `pg_dump: command not found`

```bash
# Solution: Install PostgreSQL client tools
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql-client

# CentOS/RHEL
sudo yum install postgresql
```

**Problem:** `psql: FATAL: database does not exist`

```bash
# Solution: Check DATABASE_URL or POSTGRES_DB
echo $DATABASE_URL
echo $POSTGRES_DB

# Or specify database explicitly
POSTGRES_DB=obcms_local ./scripts/backup_postgres.sh
```

**Problem:** Backup takes too long

```bash
# Solution: Use custom format with compression
pg_dump -Fc -Z9 obcms_local > backup.dump

# Or parallel dump
pg_dump -Fd -j 4 obcms_local -f backup_dir/
```

### Restore Issues

**Problem:** `ERROR: role "obcms_user" does not exist`

```bash
# Solution: Create user first
createuser obcms_user
psql -c "ALTER USER obcms_user WITH PASSWORD 'password';"

# Then restore
./scripts/restore_postgres.sh backup.sql.gz
```

**Problem:** Restore fails with permission errors

```bash
# Solution: Restore as superuser, then fix ownership
sudo -u postgres psql obcms_local < backup.sql

# Fix ownership
psql obcms_local -c "REASSIGN OWNED BY postgres TO obcms_user;"
```

**Problem:** Out of disk space during restore

```bash
# Solution: Check available space
df -h

# Clean up old backups
find backups/postgres -name "*.sql.gz" -mtime +30 -delete

# Or restore to different location
psql obcms_local < backup.sql --file=/tmp/restore.log
```

---

## Best Practices

### ✅ DO:
- **Backup before migrations** - Always create a backup before running `migrate`
- **Test backups regularly** - Restore to a test database monthly
- **Store backups off-site** - Use cloud storage for production
- **Encrypt backups** - Use GPG or cloud encryption for sensitive data
- **Monitor backup success** - Check logs and verify backup sizes
- **Document backup procedures** - Keep this guide updated
- **Version backups** - Use timestamps in backup filenames
- **Automate backups** - Use cron or systemd timers

### ❌ DON'T:
- **Don't rely on single backup** - Always have multiple copies
- **Don't backup to same disk** - Store on different storage
- **Don't ignore backup failures** - Set up alerts
- **Don't skip testing** - Untested backups are useless
- **Don't store passwords in scripts** - Use environment variables
- **Don't backup to public storage** - Use private, encrypted storage
- **Don't forget to rotate** - Clean up old backups regularly

---

## Backup Checklist

### Before Major Changes

- [ ] Run backup script: `./scripts/backup_postgres.sh`
- [ ] Verify backup created successfully
- [ ] Check backup size (should be reasonable)
- [ ] Note backup filename for rollback
- [ ] Test backup if critical changes

### After Backup

- [ ] Verify backup file exists and is not empty
- [ ] Check database statistics in output
- [ ] Confirm backup is compressed
- [ ] Document backup purpose (optional)
- [ ] Copy to off-site storage (production only)

### Before Restore

- [ ] **WARNING:** Understand restore will replace ALL data
- [ ] Confirm correct backup file
- [ ] Backup current database (if needed)
- [ ] Stop application server
- [ ] Inform users of downtime

### After Restore

- [ ] Verify row counts match expected values
- [ ] Test critical functionality
- [ ] Check user accounts work
- [ ] Restart application server
- [ ] Monitor for errors

---

## Security Considerations

### Backup Encryption

```bash
# Encrypt backup with GPG
./scripts/backup_postgres.sh
gpg --encrypt --recipient admin@oobc.gov backups/postgres/obcms_backup_*.sql.gz

# Decrypt and restore
gpg --decrypt backup.sql.gz.gpg | gunzip | psql obcms_local
```

### Access Control

```bash
# Restrict backup directory permissions
chmod 700 backups/postgres/
chmod 600 backups/postgres/*.sql.gz

# Only allow postgres user
chown postgres:postgres backups/postgres/
```

### Sensitive Data

- **Remove sensitive data** from development backups
- **Anonymize user data** for testing environments
- **Audit backup access** - Who has access to backups?
- **Encrypt cloud storage** - Always use encryption at rest

---

## Related Documentation

- **[PostgreSQL Migration Summary](POSTGRESQL_MIGRATION_SUMMARY.md)** - Database setup
- **[Staging Environment Guide](../env/staging-complete.md)** - Deployment procedures
- **[Production Settings](../../src/obc_management/settings/production.py)** - Configuration

---

## Support

For backup issues or questions:
1. Check troubleshooting section above
2. Review PostgreSQL logs: `/var/log/postgresql/`
3. Check application logs: `src/logs/`
4. Consult PostgreSQL documentation: https://www.postgresql.org/docs/

---

**Last Updated:** 2025-10-06
**Maintainer:** OBCMS Development Team
