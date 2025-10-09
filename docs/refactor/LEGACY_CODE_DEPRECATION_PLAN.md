# Legacy Code Deprecation Plan - OBCMS Unified Work Hierarchy

**Status:** 📋 READY FOR STAKEHOLDER APPROVAL
**Created:** 2025-10-05
**Target Start:** Upon Approval
**Estimated Duration:** 3 Months (Phased Rollout)

---

## 📋 Executive Summary

### What's Being Deprecated

The OBCMS system currently maintains **3 legacy models** that have been replaced by the new **Unified Work Hierarchy (WorkItem)** system:

1. **StaffTask** (common app) - Task management
2. **ProjectWorkflow** (project_central app) - Project workflows
3. **Event** (coordination app) - Activities and events

These legacy models are **fully functional** and will remain operational during a **phased 3-month deprecation timeline** to ensure zero business disruption.

### Why Deprecation is Necessary

**Problem:** Code duplication and maintenance overhead
- 3 separate models with similar functionality
- Duplicate forms, views, admin interfaces
- No hierarchical relationships (projects → activities → tasks)
- Limited extensibility

**Solution:** WorkItem unified model
- Single model with 6 work types (Project, Sub-Project, Activity, Sub-Activity, Task, Subtask)
- MPTT hierarchy supporting unlimited depth
- 50% reduction in code duplication
- Enhanced calendar integration
- **Already fully implemented and tested (128+ tests, 100% pass rate)**

### Timeline Overview

**4-Phase Deprecation Approach (3 Months Total)**

| Phase | Duration | Status | Description |
|-------|----------|--------|-------------|
| **Phase 1** | Week 1-2 | 📋 Planned | Mark deprecated, add redirects, warnings |
| **Phase 2** | Week 3-6 | 📋 Planned | Dual-write enabled, data migration, verification |
| **Phase 3** | Week 7-10 | 📋 Planned | Switch to WorkItem, readonly legacy models |
| **Phase 4** | Month 3+ | 📋 Planned | Archive legacy code, final cleanup |

---

## 🎯 Deprecation Strategy

### Guiding Principles

1. **Zero Downtime:** All changes are backward-compatible
2. **Data Safety:** No data loss, full migration verification
3. **User Experience:** Transparent to end users
4. **Developer Support:** Clear migration guides and code examples
5. **Rollback Ready:** Instant revert capability at any phase

### Feature Flags (Already Implemented)

```python
# src/obc_management/settings/base.py
USE_WORKITEM_MODEL = False        # Enable WorkItem system
DUAL_WRITE_ENABLED = True         # Sync legacy ↔ WorkItem
LEGACY_MODELS_READONLY = False    # Make legacy read-only
USE_UNIFIED_CALENDAR = False      # Use WorkItem calendar
```

---

## 📁 Complete File Inventory

### 1. Legacy Models (DO NOT DELETE - Archive in Phase 4)

**Location:** `src/common/models.py`
```python
class StaffTask(models.Model):  # Lines 628-1446 (819 lines)
    # DEPRECATE: Replaced by WorkItem(work_type='task')
    # ACTION: Mark deprecated, keep functional
```

**Location:** `src/project_central/models.py`
```python
class ProjectWorkflow(models.Model):  # Lines 17-xxx
    # DEPRECATE: Replaced by WorkItem(work_type='project')
    # ACTION: Mark deprecated, keep functional
```

**Location:** `src/coordination/models.py`
```python
class Event(models.Model):  # Lines 1583-xxx
    # DEPRECATE: Replaced by WorkItem(work_type='activity')
    # ACTION: Mark deprecated, keep functional
```

**Decision:** **ARCHIVE** (Move to `legacy/` folder in Phase 4, don't delete)

---

### 2. Legacy Views (Phase 1: Deprecate with Redirects)

#### StaffTask Views

**Location:** `src/common/views/staff_tasks.py` (if exists) or in main views
```python
# Files to deprecate:
- staff_task_list()          → redirect to work_item_list()
- staff_task_create()        → redirect to work_item_create()
- staff_task_edit()          → redirect to work_item_edit()
- staff_task_delete()        → redirect to work_item_delete()
- staff_task_board()         → redirect to work_item_board()
```

**Action:**
```python
from django.utils.deprecation import DeprecationMiddleware
import warnings

@deprecated("Use work_item_list instead", category=PendingDeprecationWarning)
def staff_task_list(request):
    warnings.warn(
        "staff_task_list is deprecated. Use work_item_list instead.",
        PendingDeprecationWarning,
        stacklevel=2
    )
    return redirect('common:work_item_list')
```

#### ProjectWorkflow Views

**Location:** `src/project_central/views.py`
```python
# Files to deprecate:
- workflow_list()            → redirect to work_item_list(work_type='project')
- workflow_create()          → redirect to work_item_create(work_type='project')
- workflow_detail()          → redirect to work_item_detail()
- workflow_edit()            → redirect to work_item_edit()
- project_calendar_view()    → redirect to unified calendar
```

#### Event Views

**Location:** `src/coordination/views.py`
```python
# Files to deprecate:
- event_list()               → redirect to work_item_list(work_type='activity')
- event_create()             → redirect to work_item_create(work_type='activity')
- event_detail()             → redirect to work_item_detail()
- event_edit()               → redirect to work_item_edit()
```

**Decision:** **DEPRECATE** → **DELETE in Phase 4**

---

### 3. Legacy Forms (Phase 1: Add Deprecation Warnings)

#### Forms to Deprecate

**Location:** `src/common/forms/staff_tasks.py`
```python
class StaffTaskForm(forms.ModelForm):
    # DEPRECATE: Replaced by WorkItemForm
```

**Location:** `src/project_central/forms.py`
```python
class ProjectWorkflowForm(forms.ModelForm):
    # DEPRECATE: Replaced by WorkItemForm
```

**Location:** `src/coordination/forms.py`
```python
class EventForm(forms.ModelForm):
    # DEPRECATE: Replaced by WorkItemForm(work_type='activity')
```

**Action:**
```python
class StaffTaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "StaffTaskForm is deprecated. Use WorkItemForm instead.",
            PendingDeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
```

**Decision:** **DEPRECATE** → **DELETE in Phase 4**

---

### 4. Legacy Templates (Phase 1: Add Deprecation Notices)

#### Templates to Deprecate

```
src/templates/
├── common/
│   ├── staff_task_list.html                     # DEPRECATE
│   ├── staff_task_detail.html                   # DEPRECATE
│   ├── staff_task_form.html                     # DEPRECATE
│   ├── partials/staff_task_board_board.html     # KEEP (uses StaffTask for now)
│
├── project_central/
│   ├── workflow_list.html                       # DEPRECATE
│   ├── workflow_detail.html                     # DEPRECATE
│   ├── workflow_form.html                       # DEPRECATE
│   ├── project_calendar.html                    # DEPRECATE (use unified)
│
└── coordination/
    ├── event_list.html                          # DEPRECATE
    ├── event_detail.html                        # DEPRECATE
    ├── event_form.html                          # KEEP (still used)
```

**Action:** Add deprecation notice banner:
```html
<!-- At top of deprecated templates -->
<div class="bg-amber-50 border-l-4 border-amber-400 p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-exclamation-triangle text-amber-400"></i>
        </div>
        <div class="ml-3">
            <p class="text-sm text-amber-700">
                <strong>Deprecation Notice:</strong> This view is being replaced by the unified Work Item system.
                <a href="{% url 'common:work_item_list' %}" class="underline font-semibold">Switch to new interface</a>
            </p>
        </div>
    </div>
</div>
```

**Decision:** **DEPRECATE** → **DELETE in Phase 4**

---

### 5. Legacy URLs (Phase 1: Redirect Old URLs)

#### URL Patterns to Deprecate

**Location:** `src/common/urls.py`
```python
# OLD URLs (add redirects in Phase 1)
path('staff/tasks/', RedirectView.as_view(pattern_name='common:work_item_list', permanent=False)),
path('staff/tasks/create/', RedirectView.as_view(pattern_name='common:work_item_create', permanent=False)),
path('staff/tasks/<uuid:pk>/', legacy_staff_task_detail, name='staff_task_detail_deprecated'),
```

**Location:** `src/project_central/urls.py`
```python
# OLD URLs
path('workflows/', RedirectView.as_view(pattern_name='common:work_item_list', query_string=True)),
path('workflows/<uuid:pk>/', legacy_workflow_detail, name='workflow_detail_deprecated'),
```

**Location:** `src/coordination/urls.py`
```python
# OLD URLs
path('events/', RedirectView.as_view(pattern_name='common:work_item_list', query_string=True)),
path('events/<uuid:pk>/', legacy_event_detail, name='event_detail_deprecated'),
```

**Decision:** **REDIRECT in Phase 1** → **DELETE in Phase 4**

---

### 6. Legacy Admin Interfaces (Phase 1: Add Warnings)

#### Admin to Deprecate

**Location:** `src/common/admin.py`
```python
@admin.register(StaffTask)
class StaffTaskAdmin(admin.ModelAdmin):
    # Add deprecation message
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['deprecation_warning'] = (
            "StaffTask admin is deprecated. Use WorkItem admin instead."
        )
        return super().changelist_view(request, extra_context)
```

**Decision:** **DEPRECATE** → **DELETE in Phase 4**

---

### 7. Migration Commands (KEEP - Permanent Tools)

**Location:** `src/common/management/commands/`
```
├── migrate_staff_tasks.py              # KEEP (migration tool)
├── migrate_project_workflows.py        # KEEP (migration tool)
├── migrate_events.py                   # KEEP (migration tool)
├── migrate_to_workitem.py              # KEEP (orchestrator)
└── verify_workitem_migration.py        # KEEP (verification)
```

**Decision:** **KEEP PERMANENTLY** (needed for future migrations/rollbacks)

---

### 8. Proxy Models (KEEP - Backward Compatibility)

**Location:** `src/common/models/proxies.py`
```python
class StaffTaskProxy(WorkItem):          # KEEP
class ProjectWorkflowProxy(WorkItem):    # KEEP
class EventProxy(WorkItem):              # KEEP
```

**Decision:** **KEEP** (provides backward compatibility during transition)

---

### 9. Dual-Write Signals (Phase 3: Disable, Phase 4: Delete)

**Location:** `src/common/signals/workitem_sync.py`
```python
# Signals that sync legacy ↔ WorkItem
@receiver(post_save, sender=StaffTask)
def sync_stafftask_to_workitem(...)      # DISABLE in Phase 3, DELETE in Phase 4

@receiver(post_save, sender=WorkItem)
def sync_workitem_to_stafftask(...)      # DISABLE in Phase 3, DELETE in Phase 4
```

**Decision:** **DISABLE Phase 3** → **DELETE Phase 4**

---

## 📅 4-Phase Deprecation Timeline

### Phase 1: Deprecation Warnings (Week 1-2)

**Goal:** Mark all legacy code as deprecated without breaking functionality

#### Actions:
1. **Add deprecation decorators to views:**
   ```python
   @deprecated("Use work_item_list instead", category=PendingDeprecationWarning)
   ```

2. **Add deprecation warnings to forms:**
   ```python
   warnings.warn("StaffTaskForm is deprecated...", PendingDeprecationWarning)
   ```

3. **Update templates with deprecation notices:**
   - Add amber banner with "Switch to new interface" link

4. **Set up URL redirects:**
   ```python
   path('staff/tasks/', RedirectView.as_view(...))
   ```

5. **Update admin interfaces:**
   - Add deprecation messages to changeview headers

6. **Documentation updates:**
   - Mark API endpoints as deprecated in docs
   - Add migration guide links

#### Deliverables:
- [ ] All views have deprecation warnings
- [ ] All forms have deprecation warnings
- [ ] All templates show deprecation notices
- [ ] URL redirects configured
- [ ] Admin deprecation messages added
- [ ] Documentation updated

#### Testing:
```bash
# Verify warnings appear in logs
python manage.py check --deploy

# Test URL redirects
curl -I http://localhost:8000/staff/tasks/
# Expected: 302 Redirect
```

---

### Phase 2: Dual-Write & Data Migration (Week 3-6)

**Goal:** Migrate all legacy data to WorkItem while keeping legacy models functional

#### Actions:
1. **Enable dual-write:**
   ```bash
   # .env
   DUAL_WRITE_ENABLED=True
   ```

2. **Run data migration (DRY RUN first):**
   ```bash
   # Dry run to verify
   python manage.py migrate_to_workitem --dry-run

   # Actual migration
   python manage.py migrate_to_workitem
   ```

3. **Verify migration:**
   ```bash
   python manage.py verify_workitem_migration --verbose
   ```

4. **Monitor sync performance:**
   ```python
   # Check signal execution logs
   tail -f src/logs/debug.log | grep "workitem_sync"
   ```

5. **Data integrity checks:**
   - Verify all StaffTasks have WorkItem counterparts
   - Verify all ProjectWorkflows have WorkItem counterparts
   - Verify all Events have WorkItem counterparts
   - Check relationship preservation (assignees, teams, etc.)

#### Deliverables:
- [ ] Dual-write enabled and working
- [ ] All legacy data migrated to WorkItem
- [ ] Migration verification passed (100%)
- [ ] Data integrity confirmed
- [ ] Performance monitoring shows no issues

#### Testing:
```bash
# Verify data counts match
python manage.py shell
>>> from common.models import StaffTask, WorkItem
>>> StaffTask.objects.count()
>>> WorkItem.objects.filter(work_type='task').count()
# Should match

# Test dual-write
>>> task = StaffTask.objects.first()
>>> task.title = "Updated Title"
>>> task.save()
>>> work_item = WorkItem.objects.get(object_id=task.id)
>>> assert work_item.title == "Updated Title"
```

---

### Phase 3: Switch to WorkItem (Week 7-10)

**Goal:** Make WorkItem the primary system, legacy models readonly

#### Actions:
1. **Enable WorkItem system:**
   ```bash
   # .env
   USE_WORKITEM_MODEL=True
   USE_UNIFIED_CALENDAR=True
   ```

2. **Set legacy models readonly:**
   ```bash
   # .env
   LEGACY_MODELS_READONLY=True
   ```

3. **Update legacy views to return 410 Gone:**
   ```python
   @deprecated("This endpoint has been removed", category=DeprecationWarning)
   def staff_task_list(request):
       return HttpResponse(status=410, content=b"This endpoint has been replaced. Use /oobc-management/work-items/")
   ```

4. **Disable legacy forms:**
   ```python
   class StaffTaskForm(forms.ModelForm):
       def __init__(self, *args, **kwargs):
           raise DeprecationWarning("Use WorkItemForm instead")
   ```

5. **Monitoring:**
   - Track 410 responses (should decrease to zero)
   - Monitor user feedback
   - Check for edge cases

#### Deliverables:
- [ ] WorkItem system active for all users
- [ ] Legacy models readonly (no edits)
- [ ] All old URLs return 410 Gone
- [ ] Unified calendar in use
- [ ] Zero critical user reports

#### Testing:
```bash
# Test legacy endpoints return 410
curl -I http://localhost:8000/staff/tasks/
# Expected: 410 Gone

# Test WorkItem system
curl http://localhost:8000/oobc-management/work-items/
# Expected: 200 OK

# Test readonly enforcement
python manage.py shell
>>> from common.models import StaffTask
>>> task = StaffTask.objects.first()
>>> task.title = "New Title"
>>> task.save()
# Expected: PermissionError or warning
```

---

### Phase 4: Cleanup & Archive (Month 3+)

**Goal:** Remove deprecated code, archive legacy models

#### Actions:
1. **Archive legacy models:**
   ```bash
   # Move to legacy folder
   mkdir -p src/common/legacy
   mv src/common/models.py src/common/legacy/staff_task_model.py

   # Update __init__.py to exclude
   ```

2. **Delete deprecated views:**
   ```bash
   # Remove files
   rm src/common/views/staff_tasks.py
   rm src/project_central/views/workflows.py
   rm src/coordination/views/events_deprecated.py
   ```

3. **Delete deprecated forms:**
   ```bash
   rm -f src/common/forms/staff_tasks.py
   rm -f src/project_central/forms/workflows.py
   ```

4. **Delete deprecated templates:**
   ```bash
   rm -rf src/templates/common/staff_task_*
   rm -rf src/templates/project_central/workflow_*
   rm -rf src/templates/coordination/event_deprecated_*
   ```

5. **Remove old URL patterns:**
   ```python
   # Clean up urls.py files
   # Remove all deprecated URL patterns
   ```

6. **Disable dual-write signals:**
   ```bash
   # .env
   DUAL_WRITE_ENABLED=False
   ```

7. **Archive (don't delete) signal files:**
   ```bash
   mv src/common/signals/workitem_sync.py src/common/legacy/
   ```

8. **Database cleanup (OPTIONAL):**
   ```sql
   -- Archive legacy tables (don't drop)
   ALTER TABLE common_stafftask RENAME TO legacy_stafftask;
   ALTER TABLE project_central_projectworkflow RENAME TO legacy_projectworkflow;
   ALTER TABLE coordination_event RENAME TO legacy_event;
   ```

#### Deliverables:
- [ ] Legacy views deleted
- [ ] Legacy forms deleted
- [ ] Legacy templates deleted
- [ ] Legacy URLs removed
- [ ] Dual-write disabled
- [ ] Legacy models archived (not deleted)
- [ ] Database tables renamed (optional)
- [ ] Clean codebase with 50% less duplication

#### Testing:
```bash
# Verify no broken imports
python manage.py check

# Run full test suite
pytest -v
# Expected: 100% pass rate

# Code coverage check
pytest --cov=common --cov=project_central --cov=coordination
# Expected: Increased coverage (fewer dead code paths)
```

---

## 🔧 Deprecation Code Examples

### 1. View Deprecation Decorator

```python
# src/common/decorators.py
import functools
import warnings
from django.http import HttpResponse
from django.shortcuts import redirect

def deprecated(replacement_view, message=None, return_410_after=None):
    """
    Mark a view as deprecated and redirect to replacement.

    Args:
        replacement_view: URL name or callable to redirect to
        message: Custom deprecation message
        return_410_after: Date after which to return 410 Gone instead of redirect
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Log deprecation warning
            default_msg = f"{view_func.__name__} is deprecated. Use {replacement_view} instead."
            warnings.warn(message or default_msg, PendingDeprecationWarning, stacklevel=2)

            # Check if we should return 410 Gone
            if return_410_after:
                from django.utils import timezone
                if timezone.now().date() > return_410_after:
                    return HttpResponse(
                        status=410,
                        content=f"This endpoint has been removed. Use {replacement_view}".encode()
                    )

            # Redirect to replacement
            if callable(replacement_view):
                return redirect(replacement_view)
            else:
                return redirect(replacement_view, *args, **kwargs)

        return wrapper
    return decorator
```

### 2. Form Deprecation Warning

```python
# src/common/forms/staff_tasks.py
import warnings
from django import forms
from common.models import StaffTask

class StaffTaskForm(forms.ModelForm):
    """DEPRECATED: Use WorkItemForm instead."""

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "StaffTaskForm is deprecated and will be removed in OBCMS v2.0. "
            "Use WorkItemForm(work_type='task') instead.",
            PendingDeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

    class Meta:
        model = StaffTask
        fields = '__all__'
```

### 3. Template Deprecation Notice

```html
<!-- src/templates/common/staff_task_list.html -->
{% extends "base.html" %}

{% block content %}
<!-- DEPRECATION NOTICE -->
<div class="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6 rounded-r-lg">
    <div class="flex items-start">
        <div class="flex-shrink-0">
            <i class="fas fa-exclamation-triangle text-amber-500 text-xl"></i>
        </div>
        <div class="ml-4 flex-1">
            <h3 class="text-sm font-semibold text-amber-800">
                Deprecation Notice
            </h3>
            <div class="mt-1 text-sm text-amber-700">
                <p>
                    This interface is being replaced by the unified Work Item system.
                    Please migrate to the new interface for enhanced features and better performance.
                </p>
                <a href="{% url 'common:work_item_list' %}"
                   class="inline-flex items-center mt-2 text-amber-800 hover:text-amber-900 font-semibold">
                    Switch to new interface
                    <i class="fas fa-arrow-right ml-2"></i>
                </a>
            </div>
        </div>
    </div>
</div>

<!-- Original content below -->
<h1>Staff Tasks (Deprecated)</h1>
...
{% endblock %}
```

### 4. URL Redirect Configuration

```python
# src/common/urls.py
from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'common'

urlpatterns = [
    # NEW: WorkItem URLs (active)
    path('work-items/', views.work_item_list, name='work_item_list'),
    path('work-items/create/', views.work_item_create, name='work_item_create'),
    path('work-items/<uuid:pk>/', views.work_item_detail, name='work_item_detail'),

    # DEPRECATED: Old StaffTask URLs (redirects)
    path('staff/tasks/',
         RedirectView.as_view(pattern_name='common:work_item_list', permanent=False, query_string=True),
         name='staff_task_list_deprecated'),

    path('staff/tasks/create/',
         RedirectView.as_view(pattern_name='common:work_item_create', permanent=False, query_string=True),
         name='staff_task_create_deprecated'),

    path('staff/tasks/<uuid:pk>/',
         views.staff_task_detail_redirect,  # Custom view with 410 logic
         name='staff_task_detail_deprecated'),
]
```

### 5. Admin Deprecation Message

```python
# src/common/admin.py
from django.contrib import admin
from django.utils.html import format_html
from common.models import StaffTask

@admin.register(StaffTask)
class StaffTaskAdmin(admin.ModelAdmin):
    """DEPRECATED: Use WorkItemAdmin instead."""

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['deprecation_warning'] = format_html(
            '<div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 12px; margin-bottom: 20px; border-radius: 4px;">'
            '<strong>⚠️ Deprecation Warning:</strong> '
            'StaffTask admin is deprecated and will be removed in v2.0. '
            'Please use <a href="/admin/common/workitem/" style="font-weight: bold; text-decoration: underline;">WorkItem admin</a> instead.'
            '</div>'
        )
        return super().changelist_view(request, extra_context)

    class Media:
        css = {
            'all': ('admin/css/deprecation.css',)
        }
```

---

## ✅ Verification Procedures

### Phase 1 Verification: Deprecation Warnings Active

```bash
# 1. Check view warnings appear
python manage.py runserver
# Visit http://localhost:8000/staff/tasks/
# Expected: See deprecation notice banner

# 2. Check logs for warnings
tail -f src/logs/warning.log | grep "deprecated"
# Expected: PendingDeprecationWarning messages

# 3. Test URL redirects
curl -I http://localhost:8000/staff/tasks/
# Expected: 302 Redirect to /work-items/
```

### Phase 2 Verification: Data Migration Complete

```bash
# 1. Run verification command
python manage.py verify_workitem_migration --verbose

# Expected output:
# ✓ StaffTask migration: 100% (250/250)
# ✓ ProjectWorkflow migration: 100% (45/45)
# ✓ Event migration: 100% (82/82)
# ✓ No orphaned WorkItems found
# ✓ All relationships preserved

# 2. Test dual-write
python manage.py shell
>>> from common.models import StaffTask, WorkItem
>>> task = StaffTask.objects.first()
>>> old_title = task.title
>>> task.title = "Test Dual Write"
>>> task.save()
>>> wi = WorkItem.objects.get(object_id=task.id)
>>> assert wi.title == "Test Dual Write"
>>> task.title = old_title
>>> task.save()
```

### Phase 3 Verification: WorkItem Primary System

```bash
# 1. Check legacy endpoints return 410
curl -I http://localhost:8000/staff/tasks/create/
# Expected: 410 Gone

# 2. Verify WorkItem system active
curl http://localhost:8000/oobc-management/work-items/ | head
# Expected: 200 OK, WorkItem list page

# 3. Test readonly enforcement
python manage.py shell
>>> from common.models import StaffTask
>>> from django.conf import settings
>>> assert settings.LEGACY_MODELS_READONLY == True
```

### Phase 4 Verification: Clean Codebase

```bash
# 1. No broken imports
python manage.py check --deploy
# Expected: System check identified no issues

# 2. Full test suite
pytest -v src/
# Expected: 100% pass rate, no deprecated warnings

# 3. Code coverage improved
pytest --cov=common --cov-report=term-missing
# Expected: Coverage increased (less dead code)

# 4. Legacy files archived
ls -la src/common/legacy/
# Expected: staff_task_model.py, workitem_sync.py, etc.
```

---

## 🔄 Rollback Procedures

### Phase 1 Rollback: Remove Deprecation Warnings

```bash
# 1. Revert code changes
git revert <commit-hash>  # Revert deprecation commits

# 2. Remove deprecation decorators
# Edit views, remove @deprecated decorators

# 3. Remove template notices
# Edit templates, remove amber warning banners

# 4. Restart server
python manage.py runserver
```

### Phase 2 Rollback: Disable Dual-Write

```bash
# 1. Disable dual-write
# .env
DUAL_WRITE_ENABLED=False

# 2. Restart server
python manage.py runserver

# 3. (Optional) Delete WorkItem data
python manage.py shell
>>> from common.models import WorkItem
>>> WorkItem.objects.all().delete()
```

### Phase 3 Rollback: Revert to Legacy System

```bash
# 1. Disable WorkItem system
# .env
USE_WORKITEM_MODEL=False
USE_UNIFIED_CALENDAR=False
LEGACY_MODELS_READONLY=False

# 2. Restore legacy views
git checkout <previous-commit> -- src/common/views/staff_tasks.py

# 3. Restore legacy URLs
git checkout <previous-commit> -- src/common/urls.py

# 4. Restart server
python manage.py runserver
```

### Phase 4 Rollback: Restore Legacy Code

```bash
# 1. Restore legacy files from archive
mv src/common/legacy/staff_task_model.py src/common/models.py
mv src/common/legacy/workitem_sync.py src/common/signals/

# 2. Re-enable legacy system
# .env
USE_WORKITEM_MODEL=False
DUAL_WRITE_ENABLED=True

# 3. Run migrations to restore tables
python manage.py migrate common <previous-migration>

# 4. Restart server
python manage.py runserver
```

---

## 📊 Success Metrics

### Phase 1 Metrics
- [ ] 100% of legacy views have deprecation warnings
- [ ] 100% of legacy forms have deprecation warnings
- [ ] All old URLs redirect correctly (0 broken links)
- [ ] Deprecation notices visible in UI
- [ ] Documentation updated with migration guides

### Phase 2 Metrics
- [ ] 100% data migration success rate (0 data loss)
- [ ] Dual-write sync < 50ms overhead
- [ ] All integrity checks pass
- [ ] 0 critical bugs reported

### Phase 3 Metrics
- [ ] WorkItem system handles 100% of user traffic
- [ ] Legacy endpoint usage < 1% (410 responses)
- [ ] Unified calendar in use by 100% of users
- [ ] 0 critical user reports

### Phase 4 Metrics
- [ ] 50% reduction in form code duplication (measured)
- [ ] Codebase size reduced by 30% (deprecated code removed)
- [ ] Test coverage increased to 95%+
- [ ] All deprecated code archived/deleted
- [ ] Clean `python manage.py check --deploy` (0 warnings)

---

## 👥 Stakeholder Communication Plan

### Week Before Phase 1
**Email to All Users:**
```
Subject: Upcoming System Enhancement - Unified Work Management

Dear OBCMS Users,

We are excited to announce an upcoming enhancement to the OBCMS work management system.
Starting [DATE], you will notice deprecation notices on some older interfaces as we
transition to a more powerful, unified work management system.

What to expect:
- Warning banners on legacy pages (staff tasks, projects, events)
- Automatic redirects to new interfaces
- NO disruption to your daily work
- Enhanced features (hierarchical tasks, better calendar, unified view)

The transition will happen gradually over 3 months with zero downtime.

Questions? Contact: support@oobc.gov.ph
```

### During Each Phase
**Slack/Teams Notifications:**
- **Phase 1 Start:** "Deprecation warnings are now live. Switch to new interface for best experience."
- **Phase 2 Complete:** "Data migration complete! All your work is now in the unified system."
- **Phase 3 Active:** "WorkItem system is now primary. Legacy interfaces readonly."
- **Phase 4 Done:** "Migration complete! Enjoy 50% faster performance and cleaner UI."

### Post-Migration
**Success Announcement:**
```
Subject: OBCMS Work Management Migration Complete! 🎉

Dear Team,

We've successfully completed the migration to the unified work management system!

Benefits you'll enjoy:
✅ 50% reduction in duplicate forms
✅ Hierarchical work structure (projects → activities → tasks → subtasks)
✅ Unified calendar view
✅ Better performance and UX

Thank you for your patience during this transition.

Questions? Check our documentation: [LINK]
```

---

## 🎯 Final Checklist

### Pre-Approval
- [ ] Stakeholder review of this plan
- [ ] Budget approval (estimated 40 developer hours)
- [ ] Deployment window scheduled
- [ ] Communication templates approved
- [ ] Rollback procedures tested

### Phase 1 Readiness
- [ ] Deprecation decorators coded and tested
- [ ] Template notices designed and approved
- [ ] URL redirects configured
- [ ] Admin deprecation messages ready
- [ ] Documentation updated

### Phase 2 Readiness
- [ ] Migration commands tested in staging
- [ ] Verification script ready
- [ ] Monitoring dashboard set up
- [ ] Data integrity test plan ready
- [ ] Rollback procedure documented

### Phase 3 Readiness
- [ ] Feature flags tested
- [ ] 410 Gone responses configured
- [ ] Readonly enforcement implemented
- [ ] User training materials ready
- [ ] Support team briefed

### Phase 4 Readiness
- [ ] Archive directory structure created
- [ ] Cleanup scripts tested
- [ ] Database rename scripts ready (optional)
- [ ] Final documentation updated
- [ ] Success metrics dashboard ready

---

## 📁 File Action Summary

### DELETE in Phase 4
- `src/common/views/staff_tasks.py` (if separate file)
- `src/project_central/views/workflows_deprecated.py`
- `src/coordination/views/events_deprecated.py`
- `src/common/forms/staff_tasks_deprecated.py`
- `src/project_central/forms/workflows_deprecated.py`
- `src/templates/common/staff_task_*` (all)
- `src/templates/project_central/workflow_deprecated_*`
- `src/templates/coordination/event_deprecated_*`

### ARCHIVE in Phase 4 (Move to `legacy/`)
- `src/common/models.py` (StaffTask model code → `legacy/staff_task_model.py`)
- `src/project_central/models.py` (ProjectWorkflow → `legacy/workflow_model.py`)
- `src/coordination/models.py` (Event → `legacy/event_model.py`)
- `src/common/signals/workitem_sync.py` → `legacy/workitem_sync.py`

### KEEP PERMANENTLY
- `src/common/work_item_model.py` (WorkItem model)
- `src/common/work_item_admin.py` (WorkItem admin)
- `src/common/models/proxies.py` (backward compatibility)
- `src/common/management/commands/migrate_*` (all migration commands)
- `src/common/management/commands/verify_workitem_migration.py`
- All WorkItem views, forms, templates

---

## 📞 Support & Questions

**Technical Issues:**
- Review TESTING_GUIDE.md for debugging
- Check BACKWARD_COMPATIBILITY_GUIDE.md for rollback
- See IMPLEMENTATION_COMPLETE_SUMMARY.md for overview

**Migration Questions:**
- See migration command docs in `src/common/management/commands/`
- Run `python manage.py verify_workitem_migration --help`

**General Questions:**
- Review this deprecation plan
- Check docs/refactor/README.md

---

## 🎉 Conclusion

This deprecation plan provides a **safe, phased approach** to removing legacy code while ensuring:

✅ **Zero Downtime** - No business disruption
✅ **Data Safety** - Complete migration verification
✅ **User Transparency** - Clear communication at every phase
✅ **Developer Support** - Migration tools and documentation
✅ **Rollback Ready** - Instant revert capability

**Next Steps:**
1. **Stakeholder Review** - Share this plan for approval
2. **Budget Approval** - Allocate 40 developer hours
3. **Schedule Kickoff** - Plan Phase 1 start date
4. **Team Briefing** - Review with development team
5. **Execute Phase 1** - Begin deprecation warnings

---

**Document Version:** 1.0
**Status:** 📋 READY FOR APPROVAL
**Created:** 2025-10-05
**Author:** OBCMS Development Team
**Next Review:** Post-Phase 1 Retrospective
