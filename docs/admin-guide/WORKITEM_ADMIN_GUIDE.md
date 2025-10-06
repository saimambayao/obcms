# WorkItem Admin Guide

**Document Type**: Administrator Guide
**Target Audience**: BICTO Technical Staff, System Administrators
**System Module**: WorkItem Integration
**Last Updated**: October 6, 2025

---

## Overview

This guide provides system administration procedures for managing the WorkItem Integration system, including configuration, monitoring, troubleshooting, and performance optimization.

---

## System Configuration

### Django Settings

**File**: `src/obc_management/settings/base.py`

```python
# WorkItem Configuration
WORKITEM_AUTO_SYNC_ENABLED = env.bool('WORKITEM_AUTO_SYNC_ENABLED', default=True)
WORKITEM_BUDGET_TOLERANCE = Decimal('0.01')  # 1 centavo tolerance
WORKITEM_MAX_DEPTH = 5  # Max MPTT tree depth
WORKITEM_CELERY_QUEUE = 'workitem_sync'  # Dedicated Celery queue
```

### Template Customization

WorkItem generation templates are defined in:

**File**: `src/monitoring/services/workitem_generation.py`

```python
STRUCTURE_TEMPLATES = {
    'program': {
        'levels': ['project', 'sub_project', 'activity', 'task'],
        'default_activities': 5,
        'default_tasks_per_activity': 3
    },
    'activity': {
        'levels': ['project', 'activity', 'task'],
        'default_activities': 3,
        'default_tasks_per_activity': 2
    },
    'minimal': {
        'levels': ['project', 'task'],
        'default_tasks': 5
    }
}
```

To customize templates:
1. Edit template configuration
2. Restart Django application
3. Test with development PPA

---

## Signal Handler Management

### Auto-Sync Signals

**File**: `src/monitoring/signals.py`

```python
@receiver(post_save, sender=WorkItem)
def sync_workitem_to_ppa(sender, instance, created, **kwargs):
    """Auto-sync WorkItem changes to PPA."""
    if instance.auto_calculate_progress:
        instance.update_progress()

    ppa = instance.get_ppa_source
    if ppa and ppa.auto_sync_progress:
        ppa.sync_progress_from_workitem()
```

**Disabling Signals (for bulk operations):**

```python
from django.db.models.signals import post_save
from monitoring.signals import sync_workitem_to_ppa

# Disable signal
post_save.disconnect(sync_workitem_to_ppa, sender=WorkItem)

# Perform bulk operation
for work_item in WorkItem.objects.filter(status='planning'):
    work_item.status = 'in_progress'
    work_item.save()

# Re-enable signal
post_save.connect(sync_workitem_to_ppa, sender=WorkItem)
```

---

## Celery Task Monitoring

### Background Tasks

WorkItem integration uses Celery for async operations:

**Tasks:**
- `sync_ppa_progress_task`: Sync progress from WorkItems to PPAs
- `sync_ppa_status_task`: Sync status from WorkItems to PPAs
- `distribute_budget_task`: Distribute budget across work items

**Monitoring:**

```bash
# View active tasks
celery -A obc_management inspect active

# View scheduled tasks
celery -A obc_management inspect scheduled

# View task stats
celery -A obc_management inspect stats

# Purge failed tasks
celery -A obc_management purge
```

**Task Queue Configuration:**

```bash
# Dedicated queue for WorkItem tasks
celery -A obc_management worker -Q workitem_sync -c 2 --loglevel=info
```

---

## Performance Optimization

### Database Indexes

Ensure these indexes exist:

```sql
-- WorkItem indexes
CREATE INDEX idx_workitem_related_ppa ON common_work_item(related_ppa_id);
CREATE INDEX idx_workitem_status_priority ON common_work_item(status, priority);
CREATE INDEX idx_workitem_tree ON common_work_item(tree_id, lft, rght);

-- MonitoringEntry indexes
CREATE INDEX idx_monitoring_exec_project ON monitoring_monitoringentry(execution_project_id);
CREATE INDEX idx_monitoring_enable_workitem ON monitoring_monitoringentry(enable_workitem_tracking);
```

**Check index usage:**

```sql
SELECT
    schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM
    pg_stat_user_indexes
WHERE
    tablename IN ('common_work_item', 'monitoring_monitoringentry')
ORDER BY
    idx_scan ASC;
```

### Query Optimization

**Use select_related and prefetch_related:**

```python
# Bad: N+1 query problem
for work_item in WorkItem.objects.filter(related_ppa__isnull=False):
    print(work_item.related_ppa.title)  # Separate query each time

# Good: Single query with JOIN
work_items = WorkItem.objects.filter(
    related_ppa__isnull=False
).select_related('related_ppa', 'created_by')

for work_item in work_items:
    print(work_item.related_ppa.title)  # No additional query
```

**Use MPTTqueryset efficiently:**

```python
# Bad: Multiple queries for tree traversal
parent = WorkItem.objects.get(id=some_id)
children = parent.get_children()
for child in children:
    grandchildren = child.get_children()  # Separate query

# Good: Single query for entire tree
parent = WorkItem.objects.get(id=some_id)
descendants = parent.get_descendants()  # All in one query
tree = parent.get_descendants(include_self=True).select_related('related_ppa')
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Auto-Sync Not Working

**Symptoms:**
- PPA progress not updating when WorkItems change

**Diagnosis:**

```python
# Check signal connections
from django.db.models.signals import post_save
print(post_save.receivers)  # Should show sync_workitem_to_ppa

# Check PPA auto-sync settings
ppa = MonitoringEntry.objects.get(id='uuid')
print(f"Auto-sync progress: {ppa.auto_sync_progress}")
print(f"Auto-sync status: {ppa.auto_sync_status}")

# Check Celery queue
celery -A obc_management inspect active_queues
```

**Resolution:**
1. Verify signals are connected
2. Check Celery worker is running
3. Enable auto-sync on PPA if disabled
4. Check Celery logs for errors

---

#### Issue 2: Budget Rollup Validation Errors

**Symptoms:**
- Users cannot save work items due to budget mismatch

**Diagnosis:**

```python
# Check budget rollup
work_item = WorkItem.objects.get(id='uuid')
children_budget = work_item.calculate_budget_from_children()
allocated_budget = work_item.allocated_budget or Decimal('0.00')

print(f"Allocated: ₱{allocated_budget:,.2f}")
print(f"Children sum: ₱{children_budget:,.2f}")
print(f"Variance: ₱{abs(allocated_budget - children_budget):,.2f}")
```

**Resolution:**

```python
# Option 1: Auto-correct budget rollup
def fix_budget_rollup(work_item_id):
    work_item = WorkItem.objects.get(id=work_item_id)
    children_budget = work_item.calculate_budget_from_children()

    if work_item.allocated_budget != children_budget:
        print(f"Correcting: {work_item.allocated_budget} → {children_budget}")
        work_item.allocated_budget = children_budget
        work_item.save(update_fields=['allocated_budget'])

# Option 2: Redistribute budget
from monitoring.services.budget_distribution import BudgetDistributionService
ppa = MonitoringEntry.objects.get(id='ppa-uuid')
work_items = list(ppa.work_items.all())
BudgetDistributionService.distribute_equal(ppa, work_items)
```

---

#### Issue 3: MPTT Tree Corruption

**Symptoms:**
- Work item hierarchy displays incorrectly
- get_children() returns wrong results

**Diagnosis:**

```python
# Check MPTT tree integrity
from mptt.exceptions import InvalidMove
from common.work_item_model import WorkItem

# Verify tree structure
for work_item in WorkItem.objects.all():
    try:
        work_item.get_ancestors()
        work_item.get_descendants()
    except Exception as e:
        print(f"Corrupted: {work_item.id} - {e}")
```

**Resolution:**

```bash
# Rebuild MPTT tree
python manage.py rebuild_mptt common.WorkItem
```

---

## Monitoring & Alerts

### Application Monitoring

**Key Metrics to Monitor:**

| Metric | Threshold | Alert Action |
|--------|-----------|--------------|
| WorkItem sync failure rate | >5% | Investigate Celery queue |
| Budget validation errors | >10/hour | Check for systematic issue |
| MPTT query time | >500ms | Optimize queries or rebuild tree |
| API response time | >2s | Scale infrastructure |

**Monitoring Setup (Prometheus):**

```python
# Add custom metrics
from prometheus_client import Counter, Histogram

workitem_sync_counter = Counter(
    'workitem_sync_total',
    'Total WorkItem sync operations',
    ['status']
)

budget_validation_histogram = Histogram(
    'budget_validation_seconds',
    'Budget validation duration'
)
```

### Log Monitoring

**Important Log Patterns:**

```bash
# Grep for errors
tail -f logs/django.log | grep "WorkItem"
tail -f logs/celery.log | grep "sync_ppa"

# Error patterns to watch
grep "Budget rollup mismatch" logs/django.log
grep "MPTT tree" logs/django.log
grep "Celery timeout" logs/celery.log
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup WorkItem and MonitoringEntry tables
pg_dump -h localhost -U obcms_user -t common_work_item -t monitoring_monitoringentry obcms_db > workitem_backup.sql

# Restore
psql -h localhost -U obcms_user obcms_db < workitem_backup.sql
```

### Pre-Migration Backup

Before major changes:

```bash
# Full database backup
python manage.py dumpdata monitoring.MonitoringEntry common.WorkItem --indent 2 > workitem_pre_migration.json

# Restore if needed
python manage.py loaddata workitem_pre_migration.json
```

---

## Security

### Permission Management

**Required Permissions:**

```python
# Define custom permissions in models
class MonitoringEntry(models.Model):
    class Meta:
        permissions = [
            ('enable_workitem_tracking', 'Can enable WorkItem tracking'),
            ('distribute_budget', 'Can distribute budget'),
            ('view_budget_reports', 'Can view budget reports'),
        ]
```

**Assign to Groups:**

```python
# Create permission groups
from django.contrib.auth.models import Group, Permission

moa_group = Group.objects.get_or_create(name='MOA Staff')[0]
mfbm_group = Group.objects.get_or_create(name='MFBM Analysts')[0]

# Assign permissions
enable_perm = Permission.objects.get(codename='enable_workitem_tracking')
budget_perm = Permission.objects.get(codename='distribute_budget')

moa_group.permissions.add(enable_perm)
mfbm_group.permissions.add(budget_perm)
```

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial admin guide created | BICTO Technical Team |

---

**For technical support:**
- Email: bicto-admin@oobc.barmm.gov.ph
- Phone: +63 (XX) XXXX-XXXX
