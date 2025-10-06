# WorkItem Integration - Quick Start Guide

**Status**: Production-Ready
**Version**: 1.0
**Last Updated**: October 6, 2025

---

## Overview

The **WorkItem Integration System** enables detailed execution tracking and budget management for MOA Programs, Projects, and Activities (PPAs) in OBCMS. Break down large PPAs into manageable work items, track progress hierarchically, and generate comprehensive reports for MFBM and BPDA stakeholders.

### Key Features

- ✅ **Hierarchical Work Breakdown**: Project → Activities → Tasks → Subtasks
- ✅ **Budget Distribution**: Allocate and track budget across work items
- ✅ **Progress Tracking**: Auto-calculate progress from child completion
- ✅ **Real-time Sync**: Progress/status automatically syncs to PPA
- ✅ **Comprehensive Reporting**: Budget, development, and performance reports
- ✅ **RESTful API**: Programmatic access to all features

---

## Quick Start (5 Steps)

### Prerequisites

- OBCMS account with "MOA Staff" or higher role
- PPA with budget allocation set
- Access to Monitoring & Evaluation module

### Step 1: Enable WorkItem Tracking

1. Navigate to **Monitoring & Evaluation → MOA PPAs**
2. Select your PPA
3. Click **"Enable WorkItem Tracking"**
4. Choose structure template (recommend: **Activity Template**)
5. Select budget distribution policy (recommend: **Equal Distribution**)
6. Click **"Create Execution Project"**

**Result**: Execution project created with work items automatically generated.

---

### Step 2: Review Generated Work Items

1. Click **"View Execution Project"** button
2. Explore the work breakdown structure:
   - **Level 1**: Project (top level)
   - **Level 2**: Activities (major milestones)
   - **Level 3**: Tasks (actionable items)

**Result**: You can see all generated work items in tree view.

---

### Step 3: Add Custom Work Items

1. Select a parent work item (e.g., an Activity)
2. Click **"+ Add Child"** button
3. Fill in the form:
   - **Title**: "Prepare training materials"
   - **Work Type**: Task
   - **Due Date**: Set deadline
   - **Assignees**: Assign team members
4. Click **"Create Work Item"**

**Result**: New task added to the project.

---

### Step 4: Track Progress

1. Open a task work item
2. Update **Status** to "In Progress"
3. Add progress note (optional)
4. When complete, update status to "Completed"

**Result**: Progress automatically rolls up to parent activity and project.

---

### Step 5: Generate Reports

1. Navigate to **Reports** tab
2. Select report type:
   - **Budget Execution Report** (for MFBM)
   - **Progress Report** (for MOA management)
   - **Development Report** (for BPDA)
3. Click **"Generate Report"**
4. Export to Excel or PDF

**Result**: Professional reports ready for stakeholders.

---

## Installation (for developers)

### Database Setup

```bash
# Apply migrations
cd src
python manage.py migrate common
python manage.py migrate monitoring

# Verify installation
python manage.py shell
>>> from common.work_item_model import WorkItem
>>> from monitoring.models import MonitoringEntry
>>> print("Installation successful!")
```

### Dependencies

```bash
# Install required packages
pip install django-mptt>=0.14.0
pip install djangorestframework>=3.14.0
pip install django-filter>=23.0

# Verify installation
python -c "import mptt; print(f'MPTT version: {mptt.__version__}')"
```

### Celery Configuration

```bash
# Start Celery worker for WorkItem sync
celery -A obc_management worker -Q workitem_sync -c 2 --loglevel=info
```

---

## Basic Usage Examples

### Python API

```python
from monitoring.models import MonitoringEntry
from monitoring.services.budget_distribution import BudgetDistributionService

# Enable WorkItem tracking
ppa = MonitoringEntry.objects.get(id='your-ppa-id')
execution_project = ppa.create_execution_project(
    structure_template='activity',
    created_by=request.user
)

# Distribute budget
work_items = list(ppa.work_items.all())
distribution = BudgetDistributionService.distribute_equal(ppa, work_items)
BudgetDistributionService.apply_distribution(ppa, distribution)

# Sync progress
ppa.sync_progress_from_workitem()
print(f"Progress: {ppa.progress}%")
```

### REST API

```bash
# Authentication
curl -X POST https://obcms.oobc.barmm.gov.ph/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Enable WorkItem tracking
curl -X POST https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/{ppa_id}/enable-workitem-tracking/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"structure_template": "activity"}'

# Get budget allocation tree
curl -X GET https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/{ppa_id}/budget-allocation-tree/ \
  -H "Authorization: Bearer {token}"
```

---

## Documentation

### User Guides

- **[MOA WorkItem Tracking Guide](docs/user-guides/MOA_WORKITEM_TRACKING_GUIDE.md)** - For MOA program managers
- **[MFBM Budget Reports Guide](docs/user-guides/MFBM_BUDGET_REPORTS_GUIDE.md)** - For budget analysts
- **[BPDA Development Reports Guide](docs/user-guides/BPDA_DEVELOPMENT_REPORTS_GUIDE.md)** - For planning officers

### Technical Documentation

- **[API Reference](docs/api/WORKITEM_API_REFERENCE.md)** - RESTful API documentation
- **[Admin Guide](docs/admin-guide/WORKITEM_ADMIN_GUIDE.md)** - System administration
- **[Deployment Guide](docs/deployment/WORKITEM_DEPLOYMENT_GUIDE.md)** - Production deployment

### Training

- **[Training Presentation](docs/training/WORKITEM_TRAINING_PRESENTATION.md)** - 2-hour training outline

---

## Architecture

### Database Models

**WorkItem Model** (MPTT Tree Structure):
```python
class WorkItem(MPTTModel):
    # Identity
    work_type = CharField(choices=WORK_TYPE_CHOICES)  # project, activity, task, subtask
    title = CharField(max_length=500)
    description = TextField()

    # Hierarchy (MPPT)
    parent = TreeForeignKey('self', null=True, blank=True)

    # Status & Progress
    status = CharField(choices=STATUS_CHOICES)
    progress = PositiveSmallIntegerField(0-100)
    auto_calculate_progress = BooleanField(default=True)

    # Budget
    allocated_budget = DecimalField(max_digits=14, decimal_places=2)
    actual_expenditure = DecimalField(max_digits=14, decimal_places=2)

    # Domain Linkage
    related_ppa = ForeignKey('monitoring.MonitoringEntry')
```

**MonitoringEntry Integration**:
```python
class MonitoringEntry(models.Model):
    # WorkItem Integration
    execution_project = OneToOneField('common.WorkItem', related_name='ppa_source')
    enable_workitem_tracking = BooleanField(default=False)
    budget_distribution_policy = CharField(choices=['equal', 'weighted', 'manual'])
    auto_sync_progress = BooleanField(default=True)
    auto_sync_status = BooleanField(default=True)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enable-workitem-tracking/` | POST | Enable WorkItem tracking for PPA |
| `/budget-allocation-tree/` | GET | Get hierarchical budget breakdown |
| `/distribute-budget/` | POST | Distribute budget across work items |
| `/sync-from-workitem/` | POST | Sync progress/status from work items |

---

## Testing

### Run Unit Tests

```bash
# Test WorkItem model
pytest src/common/tests/test_work_item_model.py -v

# Test budget distribution service
pytest src/monitoring/tests/test_budget_distribution.py -v

# Test API endpoints
pytest src/monitoring/tests/test_workitem_api.py -v
```

### Run Integration Tests

```bash
# Test full WorkItem integration workflow
pytest src/common/tests/test_work_item_integration.py -v
```

### Expected Test Coverage

- **WorkItem Model**: >95% coverage
- **Budget Distribution Service**: >95% coverage
- **API Views**: >90% coverage
- **Overall**: >92% coverage

---

## Troubleshooting

### Common Issues

**Issue 1: "Cannot enable WorkItem tracking"**

**Cause**: PPA has no budget allocation set

**Solution**:
```python
ppa = MonitoringEntry.objects.get(id='your-id')
ppa.budget_allocation = Decimal('5000000.00')
ppa.save()
```

---

**Issue 2: "Budget rollup mismatch"**

**Cause**: Child work item budgets don't sum to parent

**Solution**:
```python
work_item = WorkItem.objects.get(id='parent-id')
children_sum = work_item.calculate_budget_from_children()
work_item.allocated_budget = children_sum
work_item.save()
```

---

**Issue 3: "Progress not syncing to PPA"**

**Cause**: Auto-sync disabled or Celery not running

**Solution**:
```python
# Enable auto-sync
ppa.auto_sync_progress = True
ppa.save()

# Manual sync
ppa.sync_progress_from_workitem()
```

---

## Support & Resources

### Getting Help

- **Support Email**: bicto-support@oobc.barmm.gov.ph
- **Documentation**: https://docs.obcms.oobc.barmm.gov.ph
- **GitHub Issues**: https://github.com/oobc-barmm/obcms/issues

### Training

- **Schedule Training**: Contact bicto-training@oobc.barmm.gov.ph
- **Self-Paced Learning**: See docs/training/

### Community

- **User Forum**: https://forum.obcms.oobc.barmm.gov.ph
- **Slack Channel**: #obcms-workitem

---

## Roadmap

### Completed Features ✅

- [x] Hierarchical work breakdown structure (MPTT)
- [x] Budget allocation and tracking
- [x] Progress auto-calculation
- [x] Real-time PPA sync
- [x] Comprehensive reporting (Budget, Development, Performance)
- [x] RESTful API

### Upcoming Features 🚀

- [ ] Gantt chart visualization
- [ ] Resource allocation and leveling
- [ ] Critical path analysis
- [ ] Mobile app for field updates
- [ ] AI-powered budget forecasting

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** feature branch (`feature/amazing-feature`)
3. **Commit** changes with clear messages
4. **Test** thoroughly (pytest)
5. **Submit** pull request

**Code Style**: Follow PEP 8 and use Black formatter

---

## License

This software is developed for the Office for Other Bangsamoro Communities (OOBC), BARMM.

**Copyright © 2025 OOBC, BARMM. All rights reserved.**

---

## Changelog

### Version 1.0 (2025-10-06)

**Initial Release:**
- WorkItem model with MPTT hierarchy
- MonitoringEntry integration (execution_project FK)
- Budget distribution service (equal, weighted, manual)
- Progress/status auto-sync
- 4 REST API endpoints
- Comprehensive documentation suite
- Training materials

---

## Quick Reference Card

### Common Commands

```bash
# Enable WorkItem tracking
python manage.py shell
>>> ppa = MonitoringEntry.objects.get(id='uuid')
>>> ppa.create_execution_project(structure_template='activity')

# Distribute budget
>>> from monitoring.services.budget_distribution import BudgetDistributionService
>>> work_items = list(ppa.work_items.all())
>>> BudgetDistributionService.distribute_equal(ppa, work_items)

# Sync progress
>>> ppa.sync_progress_from_workitem()

# Generate budget tree
>>> tree = ppa.get_budget_allocation_tree()

# Rebuild MPTT tree (if corrupted)
python manage.py rebuild_mptt common.WorkItem
```

### Keyboard Shortcuts (Web UI)

- `Ctrl + N`: Create new work item
- `Ctrl + E`: Edit selected work item
- `Ctrl + S`: Save work item
- `Delete`: Delete selected work item
- `Ctrl + F`: Search work items

---

## Contact

**BICTO (Bangsamoro Information and Communications Technology Office)**

- **Website**: https://obcms.oobc.barmm.gov.ph
- **Email**: bicto@oobc.barmm.gov.ph
- **Phone**: +63 (XX) XXXX-XXXX
- **Address**: OOBC Office, Cotabato City, BARMM

---

**Document Version**: 1.0
**Last Updated**: October 6, 2025
**Maintained By**: BICTO Development Team
