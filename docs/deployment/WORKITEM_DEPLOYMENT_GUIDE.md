# WorkItem Deployment Guide

**Document Type**: Deployment Guide
**Target Audience**: DevOps Engineers, System Administrators
**Status**: Production-Ready
**Last Updated**: October 6, 2025

---

## Pre-Deployment Checklist

### Requirements Verification

- [ ] **Database**: PostgreSQL 14+ configured
- [ ] **Python**: Version 3.12 installed
- [ ] **Redis**: Running for Celery broker
- [ ] **Celery**: Worker processes configured
- [ ] **Django**: Version 4.2+ with all dependencies
- [ ] **MPTT**: django-mptt package installed
- [ ] **Migrations**: All migrations applied successfully

### Configuration Files

- [ ] Environment variables configured (.env)
- [ ] Django settings validated (base.py, production.py)
- [ ] Celery configuration verified (celeryconfig.py)
- [ ] Logging configuration set up

---

## Migration Procedures

### Database Migrations

**Order of Execution:**

```bash
# 1. Apply WorkItem model migrations
python manage.py migrate common

# 2. Apply MonitoringEntry integration migrations
python manage.py migrate monitoring

# 3. Verify migration success
python manage.py showmigrations common monitoring

# Expected output: All migrations should show [X]
```

**Key Migrations:**

| Migration | Description | Critical |
|-----------|-------------|----------|
| `common.0020_workitem` | Create WorkItem model with MPTT | Yes |
| `common.0021_add_model_validation_constraints` | Add budget/progress constraints | Yes |
| `monitoring.0018_add_workitem_integration` | Add execution_project FK | Yes |

### Data Migration (if upgrading from legacy system)

**Step 1: Backup Existing Data**

```bash
# Backup before migration
python manage.py dumpdata monitoring.MonitoringEntry --indent 2 > monitoring_pre_migration.json
python manage.py dumpdata common.Event common.StaffTask --indent 2 > legacy_pre_migration.json
```

**Step 2: Run Migration Script** (if applicable)

```bash
# Migrate existing Events/Tasks to WorkItem (if needed)
python manage.py migrate_to_workitem --dry-run
python manage.py migrate_to_workitem --execute
```

**Step 3: Verify Migration**

```bash
# Verify data integrity
python manage.py verify_workitem_migration
```

---

## Testing Procedures

### Pre-Deployment Testing

**Unit Tests:**

```bash
# Run full test suite
pytest src/common/tests/test_work_item*.py -v
pytest src/monitoring/tests/test_workitem*.py -v

# Expected: All tests pass (100% success rate)
```

**Integration Tests:**

```bash
# Test WorkItem integration
pytest src/tests/test_work_item_integration.py -v

# Test budget distribution
pytest src/monitoring/tests/test_budget_distribution.py -v
```

**Performance Tests:**

```bash
# Test with large dataset
pytest src/tests/performance/test_workitem_performance.py -v

# Benchmark MPTT queries
python manage.py benchmark_mptt_queries
```

### Post-Deployment Smoke Tests

**Test 1: Enable WorkItem Tracking**

```bash
# Create test PPA
python manage.py shell
>>> from monitoring.models import MonitoringEntry
>>> ppa = MonitoringEntry.objects.create(
...     title="Test PPA",
...     category="moa_ppa",
...     budget_allocation=1000000.00
... )
>>> ppa.enable_workitem_tracking = True
>>> project = ppa.create_execution_project(structure_template='activity')
>>> print(f"Success: {project.id}")
```

**Test 2: Budget Distribution**

```bash
>>> from monitoring.services.budget_distribution import BudgetDistributionService
>>> work_items = list(ppa.work_items.all())
>>> distribution = BudgetDistributionService.distribute_equal(ppa, work_items)
>>> print(f"Distributed: {sum(distribution.values())}")
```

**Test 3: Progress Sync**

```bash
>>> ppa.sync_progress_from_workitem()
>>> print(f"Progress: {ppa.progress}%")
```

---

## Rollback Procedures

### Rollback Plan

**If Deployment Fails:**

**Step 1: Restore Database**

```bash
# Stop application
sudo systemctl stop obcms-web obcms-celery

# Restore database from backup
psql -h localhost -U obcms_user obcms_db < pre_deployment_backup.sql

# Verify restoration
python manage.py check --database default
```

**Step 2: Revert Code**

```bash
# Rollback to previous git tag
git checkout tags/v1.0.0  # Previous stable version
pip install -r requirements/base.txt
python manage.py collectstatic --noinput
```

**Step 3: Restart Services**

```bash
sudo systemctl start obcms-web
sudo systemctl start obcms-celery
sudo systemctl status obcms-web obcms-celery
```

### Fake Migration (for recovery)

If migrations fail:

```bash
# Mark migration as applied without running
python manage.py migrate common 0020_workitem --fake

# Then fix data manually and apply next migrations
```

---

## Production Monitoring

### Key Metrics

**Application Metrics:**

- WorkItem creation rate (items/hour)
- Budget distribution operations (per day)
- Progress sync frequency (syncs/hour)
- API response times (p50, p95, p99)

**Database Metrics:**

- WorkItem table size (rows, disk usage)
- MPTT query performance (avg time)
- Index hit ratio (should be >95%)
- Lock contention (should be minimal)

**Celery Metrics:**

- Task success rate (should be >99%)
- Task execution time (avg, max)
- Queue depth (should be <100)
- Worker availability (should have ≥2 workers)

### Monitoring Setup

**Prometheus Configuration:**

```yaml
# /etc/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'obcms_workitem'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**Grafana Dashboard:**

Import dashboard from: `docs/monitoring/workitem_dashboard.json`

### Alert Rules

**Critical Alerts:**

```yaml
# alerts.yml
groups:
  - name: workitem_alerts
    rules:
      - alert: WorkItemSyncFailureHigh
        expr: rate(workitem_sync_errors_total[5m]) > 0.05
        annotations:
          summary: "WorkItem sync failure rate >5%"

      - alert: BudgetValidationErrors
        expr: rate(budget_validation_errors_total[1h]) > 10
        annotations:
          summary: "Budget validation errors >10/hour"
```

---

## Performance Optimization

### Database Optimization

**Connection Pooling:**

```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 seconds
        }
    }
}
```

**Query Optimization:**

```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM common_work_item
WHERE related_ppa_id = 'some-uuid'
AND tree_id = 1;

-- Add missing indexes if needed
CREATE INDEX CONCURRENTLY idx_workitem_tree_ppa
ON common_work_item(tree_id, related_ppa_id);
```

### Caching Strategy

**Redis Cache Configuration:**

```python
# settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300  # 5 minutes
    }
}

# Cache budget allocation trees
@cache_page(300)  # 5 minutes
def budget_allocation_tree(request, ppa_id):
    ...
```

---

## Security Hardening

### Production Settings

```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['obcms.oobc.barmm.gov.ph']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Permission Verification

```bash
# Verify file permissions
chmod 600 .env
chmod 755 src/manage.py
chmod -R 755 src/static

# Verify database user permissions
psql -h localhost -U obcms_user -c "\du"
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All migrations tested in staging
- [ ] Database backup completed
- [ ] Code review completed
- [ ] Test suite passing (100%)
- [ ] Performance tests passing
- [ ] Security audit completed
- [ ] Documentation updated

### Deployment

- [ ] Code deployed to production
- [ ] Migrations applied successfully
- [ ] Static files collected
- [ ] Celery workers restarted
- [ ] Web server restarted
- [ ] Smoke tests passed

### Post-Deployment

- [ ] Monitor error logs (first 24 hours)
- [ ] Verify metrics dashboard
- [ ] Test critical workflows
- [ ] User acceptance testing
- [ ] Performance monitoring
- [ ] Backup verification

---

## Troubleshooting

### Deployment Issues

**Issue: Migration Timeout**

```bash
# Increase statement timeout
export PGSTATEMENT_TIMEOUT=3600000  # 1 hour
python manage.py migrate

# Or run migration in screen session
screen -S migration
python manage.py migrate
# Ctrl+A, D to detach
```

**Issue: Celery Not Processing Tasks**

```bash
# Check Celery worker status
celery -A obc_management inspect active_queues
celery -A obc_management inspect stats

# Restart workers
sudo systemctl restart obcms-celery
```

**Issue: High Database Load**

```sql
-- Identify slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Kill long-running queries
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';
```

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial deployment guide | BICTO DevOps Team |

---

**For deployment support:**
- Email: bicto-devops@oobc.barmm.gov.ph
- Emergency: +63 (XX) XXXX-XXXX (24/7 on-call)
