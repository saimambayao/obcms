# WorkItem Production Deployment Checklist

**Migration Date:** October 5, 2025
**Status:** READY FOR PRODUCTION

## Pre-Deployment Verification

- [ ] All legacy data migrated to WorkItem (0 legacy records remaining)
- [ ] All code refactored to use WorkItem (0 legacy imports in active code)
- [ ] Legacy models marked as abstract
- [ ] Tests passing (>95% pass rate)
- [ ] Calendar integration verified
- [ ] Database backup created

## Environment Configuration

### Required .env Settings (Production)

```env
# WorkItem System (REQUIRED)
USE_WORKITEM_MODEL=1
USE_UNIFIED_CALENDAR=1
DUAL_WRITE_ENABLED=0
LEGACY_MODELS_READONLY=1

# Database (ensure migrations applied)
DATABASE_URL=postgresql://...

# Security (standard settings)
DEBUG=0
SECRET_KEY=... (rotate after deployment)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Deployment Steps

### 1. Backup Database

```bash
# PostgreSQL backup
pg_dump obcms_prod > backup_workitem_deployment_$(date +%Y%m%d).sql

# SQLite backup (development)
cp src/db.sqlite3 src/db.sqlite3.backup.$(date +%Y%m%d)
```

### 2. Pull Latest Code

```bash
git pull origin main
```

### 3. Update Dependencies

```bash
pip install -r requirements/production.txt
```

### 4. Apply Migrations

```bash
cd src
python manage.py migrate
python manage.py check --deploy
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. Restart Services

```bash
# Systemd services
sudo systemctl restart obcms
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat

# Docker Compose
docker-compose -f docker-compose.prod.yml restart

# Coolify (if using)
# Restart via Coolify dashboard
```

### 7. Verify Deployment

```bash
# Check WorkItem system
python manage.py shell -c "from common.models import WorkItem; print(f'WorkItems: {WorkItem.objects.count()}')"

# Check calendar feed
curl https://yourdomain.com/oobc-management/calendar/work-items/feed/ | jq '.[:2]'

# Check admin access
curl -I https://yourdomain.com/admin/common/workitem/
```

## Post-Deployment Monitoring

### First 24 Hours

- [ ] Monitor error logs: `tail -f logs/django.log`
- [ ] Check calendar page load times
- [ ] Verify work item CRUD operations
- [ ] Test hierarchy navigation
- [ ] Collect user feedback

### First Week

- [ ] Monitor database query performance
- [ ] Review Sentry/error tracking
- [ ] Gather user satisfaction metrics
- [ ] Document any issues encountered

## Rollback Plan (Emergency Only)

If critical issues arise:

```bash
# 1. Restore database backup
psql obcms_prod < backup_workitem_deployment_YYYYMMDD.sql

# 2. Revert code
git revert <commit-hash>
git push origin main

# 3. Restart services
sudo systemctl restart obcms

# Time required: ~10 minutes
```

**Note:** Legacy models are abstract, so rollback requires code revert.

## Success Criteria

- WorkItem system operational
- 0 legacy model references in active code
- Calendar displaying all work types
- CRUD operations working
- No regression in performance
- User feedback positive

## Feature Flag Verification

Run the feature flag test script to verify configuration:

```bash
cd src
python scripts/test_feature_flags.py
```

Expected output:
```
WorkItem Feature Flags Configuration
============================================================

Current Configuration:
✅ USE_WORKITEM_MODEL: True
✅ USE_UNIFIED_CALENDAR: True
✅ DUAL_WRITE_ENABLED: False
✅ LEGACY_MODELS_READONLY: True

============================================================
✅ All feature flags correctly configured for production
```

## Support Contacts

- Technical Lead: [Name]
- DevOps: [Name]
- On-Call: [Contact]

## Related Documentation

- **Migration Summary:** [WORKITEM_MIGRATION_COMPLETE.md](/WORKITEM_MIGRATION_COMPLETE.md)
- **Code Migration Guide:** [docs/refactor/LEGACY_CODE_DEPRECATION_PLAN.md](../refactor/LEGACY_CODE_DEPRECATION_PLAN.md)
- **Activity Clarification:** [docs/guidelines/EVENT_VS_WORKITEM_ACTIVITY.md](../guidelines/EVENT_VS_WORKITEM_ACTIVITY.md)
- **PostgreSQL Migration:** [docs/deployment/POSTGRESQL_MIGRATION_SUMMARY.md](POSTGRESQL_MIGRATION_SUMMARY.md)
- **Staging Guide:** [docs/env/staging-complete.md](../env/staging-complete.md)
