# Testing Quick Reference Guide

**Purpose:** Quick reference for OBCMS/BMMS testing commands and procedures
**Date:** October 14, 2025

---

## Running Tests

### Run All Tests
```bash
cd src
pytest
```

### Run Specific Test Categories

**Unit Tests:**
```bash
pytest --ignore=tests/performance/
```

**Performance Tests:**
```bash
PERF=1 pytest tests/performance/ -v
```

**Multi-Tenant Data Isolation Tests:**
```bash
pytest organizations/tests/test_data_isolation.py -v --tb=short
```

**Module-Specific Tests:**
```bash
# Planning module
pytest planning/tests/ -v

# Budgeting module
pytest budget_preparation/tests/ -v
pytest budget_execution/tests/ -v

# MANA module
pytest mana/tests/ -v

# Organizations module
pytest organizations/tests/ -v
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

View coverage report: `open htmlcov/index.html`

---

## Test Data Generation

### Generate Pilot Test Data
```bash
cd src

# Load 3 pilot MOAs
python manage.py load_pilot_moas

# Import pilot users from CSV
python manage.py import_pilot_users --csv pilot_users.csv

# Generate test data for pilot
python manage.py generate_pilot_data --users 5 --programs 3 --year 2025
```

### Generate Full 44 MOA Test Data
```bash
python manage.py generate_test_data \
    --moas 44 \
    --users-per-moa 10 \
    --plans-per-moa 5 \
    --budgets-per-moa 3 \
    --assessments-per-moa 20
```

---

## Load Testing

### Setup Locust
```bash
pip install locust
```

### Run Load Test
```bash
# Baseline: 100 concurrent users
locust -f locustfile_bmms.py \
    --host=https://staging.obcms.gov.ph \
    --users 100 \
    --spawn-rate 10 \
    --run-time 10m

# Stress: 1000 concurrent users (44 MOAs)
locust -f locustfile_bmms.py \
    --host=https://staging.obcms.gov.ph \
    --users 1000 \
    --spawn-rate 50 \
    --run-time 30m
```

### View Results
Open browser: `http://localhost:8089`

---

## Database Testing

### Check Query Count (N+1 Detection)
```python
from django.test.utils import CaptureQueriesContext
from django.db import connection

with CaptureQueriesContext(connection) as queries:
    response = client.get('/moa/MOH/planning/strategic-plans/')

print(f"Query count: {len(queries)}")
# Should be ≤ 5 for list views
```

### Check Index Usage
```bash
cd src
python manage.py dbshell

# PostgreSQL
EXPLAIN ANALYZE SELECT * FROM planning_strategicplan WHERE organization_id = 1;

# Should show "Index Scan" not "Seq Scan"
```

---

## Performance Benchmarking

### Measure Page Load Time
```python
import time

start_time = time.time()
response = client.get('/moa/MOH/dashboard/')
end_time = time.time()

load_time_ms = (end_time - start_time) * 1000
print(f"Load time: {load_time_ms:.2f}ms")
# Target: < 500ms
```

### Check Cache Hit Rate
```bash
# Redis CLI
redis-cli

# Get cache stats
INFO stats
# Look for keyspace_hits / (keyspace_hits + keyspace_misses)
# Target: > 80%
```

---

## Multi-Tenant Security Tests

### Test Cross-Organization Access (Manual)
```bash
# 1. Login as MOH user
# 2. Note a MOLE strategic plan ID (e.g., 123)
# 3. Try to access: /moa/MOH/planning/strategic-plans/123/
# Expected: 403 Forbidden or 404 Not Found

# 4. Try URL tampering: /moa/MOLE/dashboard/
# Expected: 403 Forbidden
```

### Test Organization Scoping (Python Shell)
```python
from organizations.models import _thread_locals, Organization
from planning.models import StrategicPlan

# Set organization context to MOH
moh = Organization.objects.get(code='MOH')
_thread_locals.organization = moh

# Query should only return MOH plans
plans = StrategicPlan.objects.all()
assert all(plan.organization == moh for plan in plans)

# Cleanup
del _thread_locals.organization
```

---

## Monitoring & Debugging

### View Test Logs
```bash
# During test run
pytest -v --log-cli-level=INFO

# View recent logs
tail -f logs/django.log
tail -f logs/rbac_security.log
```

### Check Database Connections
```bash
# PostgreSQL
cd src
python manage.py dbshell

SELECT count(*) FROM pg_stat_activity;
# Should be < 200 (with PgBouncer pooling)

# View active queries
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

### Monitor Performance (Prometheus)
```bash
# View metrics endpoint
curl http://localhost:8000/metrics

# Open Grafana
open http://localhost:3000
```

---

## Common Test Failures & Solutions

### Issue: Import Error
```
ModuleNotFoundError: No module named 'organizations'
```

**Solution:**
```bash
# Ensure you're in src/ directory
cd src
pytest
```

---

### Issue: Database Error
```
django.db.utils.OperationalError: no such table: planning_strategicplan
```

**Solution:**
```bash
cd src
python manage.py migrate
pytest
```

---

### Issue: Performance Test Disabled
```
SKIPPED [1] tests/performance/conftest.py:15: Performance suite disabled via PERF=0
```

**Solution:**
```bash
PERF=1 pytest tests/performance/
```

---

### Issue: Multi-Tenant Test Fails
```
AssertionError: Expected 1 plan, found 5
```

**Analysis:** Organization filtering not working

**Solution:**
1. Check model inherits from `OrganizationScopedModel`
2. Verify middleware is configured in settings
3. Check thread-local is set in test

---

## Pre-Deployment Checklist

### Staging Environment
- [ ] All migrations applied: `python manage.py migrate --check`
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Environment variables set: `python manage.py check --deploy`
- [ ] Database backup created
- [ ] Monitoring dashboards configured
- [ ] Alert rules activated

### Test Execution
- [ ] Unit tests: 100% pass rate
- [ ] Performance tests: All pass
- [ ] Data isolation tests: 100% pass
- [ ] Load tests: 95% success rate
- [ ] Regression tests: No failures
- [ ] Manual UAT: All scenarios complete

---

## Pilot Testing Checklist

### Setup
- [ ] 3 pilot MOAs created (MOH, MOLE, MAFAR)
- [ ] 15 pilot users onboarded (5 per MOA)
- [ ] Training sessions completed
- [ ] Support channel established

### Execution
- [ ] UAT Scenario 1: Strategic Planning ✅ / ❌
- [ ] UAT Scenario 2: Budget Preparation ✅ / ❌
- [ ] UAT Scenario 3: Inter-MOA Partnership ✅ / ❌
- [ ] UAT Scenario 4: MANA Assessment ✅ / ❌
- [ ] UAT Scenario 5: Organization Switching ✅ / ❌

### Validation
- [ ] User satisfaction ≥ 8/10
- [ ] Task completion rate ≥ 95%
- [ ] Support tickets < 5 critical/week
- [ ] Performance targets met
- [ ] Zero data leakage incidents

---

## Emergency Procedures

### Rollback Database Migration
```bash
cd src

# List applied migrations
python manage.py showmigrations

# Rollback to previous version
python manage.py migrate planning 0001

# Verify rollback successful
python manage.py showmigrations planning
```

### Disable Multi-Tenancy (Emergency)
```python
# In src/obc_management/settings/production.py
RBAC_SETTINGS = {
    'ENABLE_MULTI_TENANT': False,  # CHANGED
    # ...
}

# Restart application
sudo systemctl restart obcms
```

### Clear Cache (If Issues)
```bash
# Redis
redis-cli FLUSHDB

# Django cache
cd src
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

---

## Performance Targets Quick Reference

| Metric | Target | Command to Check |
|--------|--------|------------------|
| Dashboard load | < 500ms | `pytest tests/performance/test_page_load.py::test_dashboard_load_time` |
| List view queries | ≤ 5 | `pytest tests/performance/test_query_performance.py::test_assessment_list_query_count` |
| API response | < 300ms | `pytest tests/performance/test_api_performance.py::test_api_list_response_time` |
| HTMX swap | < 50ms | `pytest tests/performance/test_htmx_performance.py::test_htmx_swap_time` |
| Cache hit rate | > 80% | `redis-cli INFO stats` |
| Concurrent users | 1000 (95%) | `locust -f locustfile_bmms.py --users 1000` |

---

## Useful Django Management Commands

```bash
cd src

# Database
python manage.py migrate                    # Apply migrations
python manage.py showmigrations            # List migrations
python manage.py dbshell                   # Database shell

# Testing
python manage.py test                      # Run Django tests
python manage.py check                     # Validate config
python manage.py check --deploy            # Production checks

# Data
python manage.py dumpdata > backup.json    # Backup data
python manage.py loaddata backup.json      # Restore data
python manage.py flush                     # Clear database

# Users
python manage.py createsuperuser           # Create admin
python manage.py changepassword <username> # Change password

# Organizations
python manage.py seed_organizations        # Seed 44 MOAs
python manage.py load_pilot_moas          # Load 3 pilot MOAs
python manage.py create_pilot_user         # Create pilot user

# Static files
python manage.py collectstatic             # Collect static files
python manage.py findstatic <file>         # Find static file
```

---

## Contact & Support

**Testing Team Lead:** [Name]
**Email:** testing@obcms.gov.ph
**Slack Channel:** #obcms-testing
**Issue Tracker:** https://github.com/[org]/obcms/issues

**Emergency Contact:** [On-call phone]

---

**Last Updated:** October 14, 2025
**Next Review:** After pilot completion
**Version:** 1.0
