# Pilot Database Setup and Operations

This document covers provisioning and maintaining the PostgreSQL database dedicated to
BMMS Phase 7 pilot onboarding.

## 1. Create Database and User
```sql
CREATE DATABASE bmms_pilot ENCODING 'UTF8';
CREATE USER bmms_pilot WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE bmms_pilot TO bmms_pilot;
```

Update `.env` using `.env.staging.example` as a reference.

## 2. Apply Migrations
```bash
docker compose exec web python manage.py migrate
```

## 3. Daily Backups
Use `scripts/backup_pilot_db.sh` to generate compressed dumps.

```bash
0 1 * * * /opt/bmms/scripts/backup_pilot_db.sh /var/backups/bmms/pilot >> /var/log/bmms/backup.log 2>&1
```

Backups older than `BACKUP_RETENTION_DAYS` (default 30) are automatically pruned.

## 4. Restore Procedure
```bash
./scripts/restore_pilot_db.sh /var/backups/bmms/pilot/bmms_pilot_YYYYMMDD_HHMMSS.sql
```

Perform quarterly restore drills in an isolated environment to verify integrity.

## 5. Monitoring and Health Checks
- Connection pooling configured via `CONN_MAX_AGE=600`
- Enable `pg_stat_statements` for slow query analysis (optional)
- Track `pg_dump` success/failure through system logs

## 6. Performance Targets
- Common queries under 200 ms (validated via Django debug toolbar in staging)
- Vacuum analyze weekly or enable autovacuum thresholds tuned for pilot load

## 7. Security Controls
- Limit database access to application subnet
- Rotate credentials every 90 days
- Store dumps in encrypted storage (S3 with server-side encryption or LUKS volume)

With these steps the pilot database remains isolated, recoverable, and production-ready.
