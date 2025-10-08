# PostgreSQL Migration - Next Steps

**Date**: 2025-10-08
**Status**: Planned (Not Urgent)
**Current Database**: SQLite (db.sqlite3) ✅ Working

## Current Situation

**SQLite Database** (`src/db.sqlite3`):
- ✅ 6,598 OBC Communities
- ✅ 282 Municipal Coverage records
- ✅ 8 Events
- ✅ 4 MANA Assessments
- ✅ All data accessible and functional

**PostgreSQL Status**:
- Empty databases (`obcms_local`, `obcms_test`)
- No active migration completed
- Docker setup configured but not used

## Why Migrate to PostgreSQL?

### **Benefits**:
1. **Production-Ready**: PostgreSQL is production-grade RDBMS
2. **Better Performance**: Handles concurrent users better than SQLite
3. **Advanced Features**: Full-text search, JSON queries, PostGIS (if needed)
4. **Team Collaboration**: Multiple developers can connect simultaneously
5. **Deployment Standard**: Matches production environment

### **SQLite Limitations**:
- ⚠️ Not recommended for production with multiple users
- ⚠️ No concurrent write access
- ⚠️ Limited scalability for large datasets
- ✅ Perfect for development/testing (current use case)

## Migration Plan

### **Phase 1: Prepare PostgreSQL Database**

**1. Create PostgreSQL Database and User**

```bash
# Option A: Use existing local PostgreSQL
createdb obcms_dev
createuser obcms_user -P  # Set password when prompted

# Grant permissions
psql -d obcms_dev -c "GRANT ALL PRIVILEGES ON DATABASE obcms_dev TO obcms_user;"
```

**2. Update .env for PostgreSQL**

```env
DATABASE_URL=postgres://obcms_user:your_password@localhost:5432/obcms_dev
```

**3. Run Django Migrations**

```bash
cd src
python manage.py migrate
```

---

### **Phase 2: Export Data from SQLite**

**1. Create Full Data Export**

```bash
cd src
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude=contenttypes \
  --exclude=auth.Permission \
  --exclude=sessions.Session \
  --exclude=admin.LogEntry \
  --exclude=auditlog.LogEntry \
  --indent=2 \
  --output=../obcms_full_export.json
```

**2. Verify Export**

```bash
ls -lh ../obcms_full_export.json
# Should be ~50-100MB with all your data
```

---

### **Phase 3: Import Data to PostgreSQL**

**1. Update .env to PostgreSQL**

```env
DATABASE_URL=postgres://obcms_user:your_password@localhost:5432/obcms_dev
```

**2. Import Data**

```bash
cd src
python manage.py loaddata ../obcms_full_export.json
```

**3. Verify Import**

```bash
python manage.py shell
```

```python
from communities.models import OBCCommunity
print(f"Communities: {OBCCommunity.objects.count()}")
# Should show 6,598
```

---

### **Phase 4: Verification & Testing**

**1. Run Full Test Suite**

```bash
cd src
pytest -v
python manage.py check --deploy
```

**2. Test All Modules**

- [ ] Communities listing works
- [ ] MANA assessments load
- [ ] Coordination events display
- [ ] M&E data accessible
- [ ] Admin panel functional
- [ ] File uploads work

**3. Performance Check**

```bash
# Test query performance
python manage.py shell
```

```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    list(OBCCommunity.objects.all()[:100])

print(f"Queries: {len(ctx.captured_queries)}")
print(f"Time: {sum(float(q['time']) for q in ctx.captured_queries):.3f}s")
```

---

### **Phase 5: Backup Strategy**

**1. Setup Automated PostgreSQL Backups**

Create cron job:
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/obcms && ./scripts/backup_postgres.sh
```

**2. Test Restore Process**

```bash
# Create test backup
./scripts/backup_postgres.sh

# Restore to test database
createdb obcms_restore_test
gunzip -c backups/postgres/obcms_backup_*.sql.gz | psql obcms_restore_test

# Verify
psql obcms_restore_test -c "SELECT COUNT(*) FROM communities_obccommunity;"
```

---

## Rollback Plan

If PostgreSQL migration fails, rollback to SQLite:

**1. Update .env**

```env
DATABASE_URL=sqlite:///db.sqlite3
```

**2. Restart Server**

```bash
python manage.py runserver
```

**3. Verify Data**

All data remains in SQLite (unchanged).

---

## Timeline (Suggested)

**Week 1: Preparation**
- Install PostgreSQL (if not already installed)
- Test connection
- Run migrations on empty PostgreSQL database

**Week 2: Migration**
- Export SQLite data
- Import to PostgreSQL
- Test all modules
- Verify data integrity

**Week 3: Validation**
- Run full test suite
- Performance testing
- Team testing
- Backup/restore verification

**Week 4: Production**
- Switch to PostgreSQL for development
- Monitor for issues
- Document any differences
- Update team documentation

---

## Prerequisites

Before migration:

- [ ] PostgreSQL installed and running
- [ ] Database user created with proper permissions
- [ ] Full backup of SQLite database
- [ ] Test environment verified
- [ ] Team notified of migration schedule
- [ ] Downtime window scheduled (if applicable)

---

## PostgreSQL Installation (macOS)

```bash
# Install via Homebrew
brew install postgresql@17

# Start PostgreSQL
brew services start postgresql@17

# Verify installation
psql --version
# Should show: psql (PostgreSQL) 17.x

# Create initial user (if needed)
createuser -s postgres
```

---

## Docker Alternative

If you prefer Docker-based PostgreSQL:

**1. Start Docker Services**

```bash
cd /path/to/obcms
docker-compose up -d postgres
```

**2. Update .env**

```env
DATABASE_URL=postgres://obcms:obcms_dev_password@localhost:5432/obcms
```

**3. Wait for PostgreSQL to Start**

```bash
docker-compose logs -f postgres
# Wait for "database system is ready to accept connections"
```

**4. Run Migrations**

```bash
docker-compose exec web python src/manage.py migrate
```

---

## Notes

- **Current Setup**: SQLite is working perfectly for development
- **No Rush**: Migration can happen when convenient
- **Data Safety**: All data is backed up (multiple copies)
- **Zero Risk**: SQLite remains untouched during PostgreSQL setup

---

## Contact / Questions

If you encounter issues during migration:
1. Check logs: `src/logs/django.log`
2. Review Django database settings
3. Verify PostgreSQL is running: `pg_isready`
4. Check connection: `psql -U obcms_user -d obcms_dev`

---

**Created**: 2025-10-08
**Last Updated**: 2025-10-08
**Status**: Ready for execution when needed
