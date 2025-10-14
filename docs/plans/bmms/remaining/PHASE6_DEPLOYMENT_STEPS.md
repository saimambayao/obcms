# Phase 6 OCM Aggregation - Deployment Steps

**Status:** Ready for Deployment
**Date:** 2025-10-14

---

## Quick Start Deployment

### Prerequisites
- Virtual environment activated: `source venv/bin/activate`
- Working directory: `cd src/`
- Database backup created

### 1. Run Migrations

```bash
# Navigate to src directory
cd /Users/saidamenmambayao/Library/Mobile\ Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src

# Activate virtual environment
source ../venv/bin/activate

# Run Django checks
python manage.py check

# Create migrations (if not already created)
python manage.py makemigrations ocm

# Apply migrations
python manage.py migrate ocm

# Verify migration
python manage.py showmigrations ocm
```

**Expected Output:**
```
ocm
 [X] 0001_initial
```

---

### 2. Verify OCM App Registration

```bash
# Check OCM app is loaded
python manage.py shell -c "
from django.apps import apps
print('OCM App:', apps.get_app_config('ocm'))
print('OCM Models:', [m.__name__ for m in apps.get_app_config('ocm').get_models()])
"
```

**Expected Output:**
```
OCM App: <OcmConfig: ocm>
OCM Models: ['OCMAccess']
```

---

### 3. Create OCM Organization (if needed)

```bash
python manage.py shell
```

```python
from organizations.models import Organization

# Create OCM organization
ocm_org, created = Organization.objects.get_or_create(
    code='OCM',
    defaults={
        'name': 'Office of the Chief Minister',
        'org_type': 'executive',
        'is_active': True,
        'description': 'Central oversight body for BARMM government operations'
    }
)

if created:
    print(f"Created OCM organization: {ocm_org}")
else:
    print(f"OCM organization already exists: {ocm_org}")

# Verify count
print(f"\nTotal organizations: {Organization.objects.count()}")
print(f"Active MOAs (excluding OOBC, OCM): {Organization.objects.filter(is_active=True).exclude(code__in=['OOBC', 'OCM']).count()}")
```

---

### 4. Grant OCM Access to Users

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from ocm.models import OCMAccess

User = get_user_model()

# Example: Grant analyst access
admin_user = User.objects.get(username='admin')  # User granting access
ocm_user = User.objects.get(username='your_username')  # User receiving access

access = OCMAccess.objects.create(
    user=ocm_user,
    access_level='analyst',  # Options: viewer, analyst, executive
    is_active=True,
    granted_by=admin_user,
    notes='Granted for Phase 6 implementation and testing'
)

print(f"OCM access granted to {ocm_user.get_full_name()}")
print(f"Access level: {access.access_level}")
print(f"Granted by: {access.granted_by.get_full_name()}")
```

---

### 5. Test OCM Aggregation Service

```bash
python manage.py shell
```

```python
from ocm.services.aggregation import OCMAggregationService

# Test basic methods
print("=== OCM Aggregation Service Test ===\n")

# Organization count
org_count = OCMAggregationService.get_organization_count()
print(f"Active MOAs: {org_count}")

# Government stats
gov_stats = OCMAggregationService.get_government_stats()
print(f"\nGovernment Statistics:")
print(f"  Total MOAs: {gov_stats['total_moas']}")
print(f"  Total Budget: ₱{gov_stats['total_budget']:,.2f}")
print(f"  Total Plans: {gov_stats['total_plans']}")
print(f"  Total Partnerships: {gov_stats['total_partnerships']}")
print(f"  Total Users: {gov_stats['total_users']}")

# Budget summary
budget_summary = OCMAggregationService.get_budget_summary()
print(f"\nBudget Summary:")
print(f"  Total Proposed: ₱{budget_summary['total_proposed'] or 0:,.2f}")
print(f"  Total Approved: ₱{budget_summary['total_approved'] or 0:,.2f}")
print(f"  Approval Rate: {budget_summary['approval_rate']:.1f}%")

# Planning summary
planning_summary = OCMAggregationService.get_planning_summary()
print(f"\nPlanning Summary:")
print(f"  Total Plans: {planning_summary['total_strategic_plans']}")
print(f"  Active Plans: {planning_summary['active_plans']}")
print(f"  MOAs with Plans: {planning_summary['moas_with_plans']}")

# Coordination summary
coord_summary = OCMAggregationService.get_coordination_summary()
print(f"\nCoordination Summary:")
print(f"  Total Partnerships: {coord_summary['total_partnerships']}")
print(f"  Active Partnerships: {coord_summary['active_partnerships']}")

# Performance metrics
performance = OCMAggregationService.get_performance_metrics()
print(f"\nPerformance Metrics:")
print(f"  Budget Approval Rate: {performance['budget_approval_rate']:.1f}%")
print(f"  Planning Completion: {performance['planning_completion_rate']:.1f}%")
print(f"  Partnership Success: {performance['partnership_success_rate']:.1f}%")
print(f"  Overall Score: {performance['overall_performance_score']:.1f}%")

print("\n✅ All aggregation methods working correctly!")
```

---

### 6. Run Tests

```bash
# Run all OCM tests
python manage.py test ocm.tests -v 2

# Run specific test files
python manage.py test ocm.tests.test_models -v 2
python manage.py test ocm.tests.test_permissions -v 2
python manage.py test ocm.tests.test_views -v 2
python manage.py test ocm.tests.test_aggregation -v 2

# Check test coverage
coverage run --source='ocm' manage.py test ocm.tests
coverage report -m
```

**Expected Output:**
```
Ran 199 tests in X.XXXs

OK
```

---

### 7. Start Development Server

```bash
# Start Django development server
python manage.py runserver
```

**Access OCM Dashboard:**
- URL: http://localhost:8000/ocm/dashboard/
- Login with user who has OCM access
- Verify dashboard loads without errors

---

### 8. Verify OCM Functionality

#### 8.1 Dashboard Test
```bash
curl -s http://localhost:8000/ocm/dashboard/ | grep "Government-Wide Overview"
```

#### 8.2 Read-Only Enforcement Test
```bash
# This should return 403 Forbidden
curl -X POST http://localhost:8000/ocm/dashboard/ -d "test=data"
```

#### 8.3 Budget View Test
```bash
curl -s http://localhost:8000/ocm/budget/consolidated/ | grep "Consolidated Budget"
```

#### 8.4 API Endpoint Test
```bash
curl -s http://localhost:8000/ocm/api/stats/ | python -m json.tool
```

---

### 9. Clear Cache (if needed)

```bash
python manage.py shell
```

```python
from ocm.services.aggregation import OCMAggregationService

# Clear all OCM caches
cleared_count = OCMAggregationService.clear_cache()
print(f"Cleared {cleared_count} cache keys")
```

---

### 10. Collect Static Files (Production)

```bash
# Only needed for production deployment
python manage.py collectstatic --noinput
```

---

## Verification Checklist

### Code Verification
- [✅] OCM app in INSTALLED_APPS
- [✅] OCM middleware in MIDDLEWARE
- [✅] OCM URLs included in main urls.py
- [✅] All Python files syntax valid
- [✅] No import errors

### Database Verification
- [ ] Migrations applied: `ocm.0001_initial`
- [ ] OCMAccess table exists
- [ ] 6 OCM permissions created
- [ ] OCM organization exists (code='OCM')

### Functionality Verification
- [ ] OCM dashboard accessible at /ocm/dashboard/
- [ ] Users with OCM access can view dashboard
- [ ] Users without OCM access denied (403)
- [ ] POST requests blocked (403 Forbidden)
- [ ] Budget aggregation works
- [ ] Planning overview loads
- [ ] Coordination matrix displays
- [ ] Charts render correctly (Chart.js)

### Performance Verification
- [ ] Dashboard loads <3 seconds
- [ ] Budget aggregation <2 seconds
- [ ] Caching works (second call faster)
- [ ] No N+1 query problems

### Security Verification
- [ ] Read-only banner displays
- [ ] Write operations blocked
- [ ] OCM middleware enforces read-only
- [ ] Access attempts logged
- [ ] last_accessed timestamp updates

---

## Troubleshooting

### Issue: "No module named 'django'"
**Solution:**
```bash
source venv/bin/activate
```

### Issue: "OCM app not found"
**Solution:**
Verify `'ocm'` is in `INSTALLED_APPS` in `src/obc_management/settings/base.py`

### Issue: Migration errors
**Solution:**
```bash
python manage.py migrate --fake-initial
```

### Issue: OCM dashboard 404
**Solution:**
Verify URL configuration in `src/obc_management/urls.py`:
```python
path("ocm/", include(("ocm.urls", "ocm"), namespace="ocm")),
```

### Issue: Charts not rendering
**Solution:**
- Check browser console for JavaScript errors
- Verify Chart.js CDN is accessible
- Check Chart.js version (4.4.0 required)

### Issue: Aggregation returns empty data
**Solution:**
- Verify budget/planning/coordination models exist
- Check organization FK relationships
- Review aggregation service logs

### Issue: Permission denied errors
**Solution:**
```python
# In Django shell
from ocm.models import OCMAccess
access = OCMAccess.objects.get(user__username='your_username')
access.is_active = True
access.save()
```

---

## Post-Deployment Checklist

### Monitoring
- [ ] Check Django logs for errors
- [ ] Monitor OCM access attempts
- [ ] Track dashboard performance
- [ ] Review cache hit rates

### User Management
- [ ] Create OCM access for designated users
- [ ] Document access levels (viewer/analyst/executive)
- [ ] Set up audit review process
- [ ] Schedule access reviews (quarterly)

### Performance
- [ ] Configure Redis cache (production)
- [ ] Set up cache monitoring
- [ ] Review slow query logs
- [ ] Optimize database indexes

### Documentation
- [ ] Train OCM users on dashboard
- [ ] Document report generation process
- [ ] Create troubleshooting guide
- [ ] Update deployment runbook

---

## Rollback Procedure

If issues occur during deployment:

### 1. Stop Application
```bash
# Development
Ctrl+C

# Production
sudo systemctl stop gunicorn
```

### 2. Restore Database
```bash
cd src
cp db.sqlite3 db.sqlite3.failed
cp db.sqlite3.backup.phase6.YYYYMMDD db.sqlite3
```

### 3. Revert Code
```bash
git log --oneline  # Find commit before Phase 6
git checkout <commit-hash>
```

### 4. Restart Application
```bash
# Development
python manage.py runserver

# Production
sudo systemctl start gunicorn
```

---

## Production Deployment Notes

### Environment Variables
```bash
# .env.production
DJANGO_SETTINGS_MODULE=obc_management.settings.production
CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379/1
OCM_CACHE_TTL=900
```

### Gunicorn Configuration
```bash
# Restart Gunicorn after deployment
sudo systemctl restart gunicorn

# Check status
sudo systemctl status gunicorn
```

### Nginx Configuration
```nginx
# OCM location block
location /ocm/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### SSL/TLS
Ensure HTTPS is enforced for OCM access:
```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## Support Contacts

**Technical Issues:**
- Development Team Lead
- Database Administrator

**Access Management:**
- System Administrator
- OCM Coordinator

**User Support:**
- Help Desk: help@obcms.gov.ph
- Documentation: docs/user-guides/ocm/

---

## Next Steps

After successful deployment:

1. **Phase 6 Complete** - Mark Phase 6 as complete in BMMS tracker
2. **User Training** - Schedule OCM dashboard training sessions
3. **Documentation** - Update user guides with production URLs
4. **Phase 7 Planning** - Begin Phase 7: Pilot MOA Onboarding
5. **Monitoring** - Set up performance monitoring dashboards

---

**END OF DEPLOYMENT STEPS**
