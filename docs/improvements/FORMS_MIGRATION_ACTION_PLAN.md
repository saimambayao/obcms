# FORMS & SERIALIZERS MIGRATION - ACTION PLAN
**CRITICAL: 17 Crash Points Must Be Fixed ASAP**

**Date:** October 5, 2025
**Status:** 🔴 CRITICAL - Views will crash on user access
**Priority:** IMMEDIATE

---

## EXECUTIVE SUMMARY

**Problem:** 17 view functions use deprecated forms that raise `NotImplementedError`

**Impact:** Users will see 500 errors when accessing:
- Staff task management pages (11 crash points)
- Event coordination pages (4 crash points)
- Project workflow pages (2 crash points)

**Solution:** Replace all deprecated forms with `WorkItemForm`

---

## IMMEDIATE ACTIONS REQUIRED

### 🔴 CRITICAL FIX 1: common/views/management.py (11 locations)

**File:** `/src/common/views/management.py`
**Problem:** Using `StaffTaskForm` which raises `NotImplementedError`

**Affected Lines:**
```
1071: form = StaffTaskForm(request.POST or None, request=request)
1139: form = StaffTaskForm(request.POST, **form_kwargs)
1177: form = StaffTaskForm(initial=initial, **form_kwargs)
1326: new_task_form = StaffTaskForm(...)
1378: "form": StaffTaskForm(...)
1763: "form": StaffTaskForm(...)
1783: new_task_form = StaffTaskForm(...)
2042: form = StaffTaskForm(request.POST, instance=task, request=request)
2090: form = StaffTaskForm(instance=task, request=request)
2398: form = StaffTaskForm(...)
[+1 more]
```

**Fix Required:**
```python
# OLD (crashes):
from common.forms import StaffTaskForm
form = StaffTaskForm(request.POST or None, request=request)

# NEW (works):
from common.forms.work_items import WorkItemForm
form = WorkItemForm(request.POST or None, work_type='task')
```

**Testing Required:**
- Staff task creation
- Staff task editing
- Task assignment workflow
- Task board functionality

---

### 🔴 CRITICAL FIX 2: coordination/views.py (4 locations)

**File:** `/src/coordination/views.py`
**Problem:** Using `EventForm` which raises `NotImplementedError`

**Affected Lines:**
```
516: event_form = EventForm(request.POST)
551: event_form = EventForm(initial=initial)
579: form = EventForm(request.POST, instance=event)
644: form = EventForm(instance=event)
```

**Fix Required:**
```python
# OLD (crashes):
from coordination.forms import EventForm
event_form = EventForm(request.POST)

# NEW (works):
from common.forms.work_items import WorkItemForm
event_form = WorkItemForm(request.POST, work_type='activity')
```

**Testing Required:**
- Event creation
- Event editing
- Event calendar display
- Recurring events

---

### 🔴 CRITICAL FIX 3: project_central/views.py (2 locations)

**File:** `/src/project_central/views.py`
**Problem:** Using `ProjectWorkflowForm` which raises `NotImplementedError`

**Affected Lines:**
```
774: form = ProjectWorkflowForm(request.POST, instance=workflow)
786: form = ProjectWorkflowForm(instance=workflow)
```

**Fix Required:**
```python
# OLD (crashes):
from project_central.forms import ProjectWorkflowForm
form = ProjectWorkflowForm(request.POST, instance=workflow)

# NEW (works):
from common.forms.work_items import WorkItemForm
form = WorkItemForm(request.POST, work_type='project', instance=workflow)
```

**Testing Required:**
- Project workflow editing
- Workflow stage advancement
- Project detail pages

---

### 🐛 BUG FIX: coordination/forms.py (Orphaned Code)

**File:** `/src/coordination/forms.py`
**Problem:** Module-level `__init__` method at line 347 (NOT part of any class)

**Code to Remove:**
- **Lines 347-410** - Orphaned `__init__` method
- Contains ProjectWorkflow import and logic
- Never executed (dead code)

**Action:**
```bash
# Delete lines 347-410 from coordination/forms.py
sed -i '' '347,410d' /src/coordination/forms.py
```

**Verify:** No other code references this orphaned method

---

## WORKITEM SERIALIZER (Create New)

### Missing: WorkItemSerializer

**File to Create:** `/src/common/serializers.py`

**Required Implementation:**
```python
from rest_framework import serializers
from common.work_item_model import WorkItem

class WorkItemSerializer(serializers.ModelSerializer):
    """
    Unified serializer for WorkItem model.

    Supports all work_types: project, activity, task
    """

    work_type_display = serializers.CharField(
        source='get_work_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    assignees_names = serializers.StringRelatedField(
        source='assignees',
        many=True,
        read_only=True
    )

    class Meta:
        model = WorkItem
        fields = [
            'id', 'work_type', 'work_type_display',
            'title', 'description', 'status', 'status_display',
            'priority', 'start_date', 'due_date',
            'assignees', 'assignees_names', 'teams',
            'parent', 'created_by', 'created_at', 'updated_at',
            # Type-specific fields
            'type_specific_data',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
```

---

## MONITORING SERIALIZER MIGRATION

### Update: monitoring/serializers.py

**Problem:** `MonitoringEntryStaffTaskSerializer` uses abstract `StaffTask` model

**Current Code (lines 135-149):**
```python
from common.models import StaffTask

class MonitoringEntryStaffTaskSerializer(serializers.ModelSerializer):
    """Serialize StaffTask records linked to monitoring entries."""

    class Meta:
        model = StaffTask
        fields = [...]
```

**Fix Required:**
```python
from common.work_item_model import WorkItem

class MonitoringEntryWorkItemSerializer(serializers.ModelSerializer):
    """Serialize WorkItem records linked to monitoring entries."""

    class Meta:
        model = WorkItem
        fields = [...]

    def get_queryset(self):
        # Only monitoring-related work items
        return WorkItem.objects.filter(
            type_specific_data__domain='monitoring'
        )
```

**Update Usage (line 372-378):**
```python
def get_task_assignments(self, obj):
    # OLD:
    tasks = obj.tasks.filter(domain=StaffTask.DOMAIN_MONITORING)
    serializer = MonitoringEntryStaffTaskSerializer(tasks, many=True)

    # NEW:
    tasks = WorkItem.objects.filter(
        type_specific_data__monitoring_entry=obj.id
    )
    serializer = MonitoringEntryWorkItemSerializer(tasks, many=True)

    return serializer.data
```

---

## CLEANUP TASKS (After Fixes)

### Remove Deprecated Form Stubs

**Files to Update:**

1. **common/forms/staff.py**
   - Remove `StaffTaskForm` class (lines 492-505)
   - Keep deprecation comment for reference

2. **coordination/forms.py**
   - Remove `EventForm` class (lines 254-410)
   - Remove `EventQuickUpdateForm` class (lines 412-434)
   - Remove orphaned `__init__` (lines 347-410)

3. **project_central/forms.py**
   - Remove `ProjectWorkflowForm` class (lines 29-44)
   - Remove `ProjectWorkflowFromPPAForm` class (lines 47-62)

4. **common/forms/__init__.py**
   - Remove `StaffTaskForm` from exports
   - Update `__all__` list

---

## TESTING CHECKLIST

### Phase 1: Critical Fixes Verification

- [ ] **Staff Tasks (11 views)**
  - [ ] Create new task via management UI
  - [ ] Edit existing task
  - [ ] Assign task to user
  - [ ] Complete task workflow
  - [ ] Verify task board display

- [ ] **Events (4 views)**
  - [ ] Create new event
  - [ ] Edit existing event
  - [ ] Create recurring event
  - [ ] View event calendar

- [ ] **Projects (2 views)**
  - [ ] Edit project workflow
  - [ ] Advance workflow stage

### Phase 2: Serializer Testing

- [ ] **WorkItem API**
  - [ ] GET /api/workitems/ (list)
  - [ ] GET /api/workitems/{id}/ (detail)
  - [ ] POST /api/workitems/ (create)
  - [ ] PUT /api/workitems/{id}/ (update)

- [ ] **Monitoring API**
  - [ ] GET monitoring entry with tasks
  - [ ] Verify task data structure
  - [ ] Check backward compatibility

### Phase 3: Integration Testing

- [ ] All dashboard pages load
- [ ] No 500 errors in logs
- [ ] No missing form imports
- [ ] All CRUD operations work

---

## ROLLBACK PLAN

**If issues occur:**

1. **Immediate Rollback:**
   ```bash
   git revert HEAD
   git push
   ```

2. **Partial Rollback (by file):**
   ```bash
   git checkout HEAD~1 -- src/common/views/management.py
   git checkout HEAD~1 -- src/coordination/views.py
   git checkout HEAD~1 -- src/project_central/views.py
   ```

3. **Keep migrations:** Don't rollback WorkItem model/migrations

---

## IMPLEMENTATION SEQUENCE

### Step 1: Preparation (5 min)
- [ ] Create feature branch: `git checkout -b fix/deprecated-forms`
- [ ] Backup current files
- [ ] Review WorkItemForm API

### Step 2: Fix Views (30-45 min)
- [ ] Fix common/views/management.py (11 locations)
- [ ] Fix coordination/views.py (4 locations)
- [ ] Fix project_central/views.py (2 locations)
- [ ] Update imports

### Step 3: Remove Orphaned Code (5 min)
- [ ] Delete coordination/forms.py:347-410
- [ ] Verify no side effects

### Step 4: Create WorkItem Serializer (15-20 min)
- [ ] Implement in common/serializers.py
- [ ] Add to API viewsets
- [ ] Test endpoints

### Step 5: Migrate Monitoring Serializer (15-20 min)
- [ ] Update MonitoringEntryStaffTaskSerializer
- [ ] Update get_task_assignments method
- [ ] Test monitoring API

### Step 6: Cleanup (10-15 min)
- [ ] Remove deprecated form stubs
- [ ] Update imports in __init__.py
- [ ] Run linting/formatting

### Step 7: Testing (30-45 min)
- [ ] Manual testing of all affected views
- [ ] API endpoint testing
- [ ] Integration testing

### Step 8: Deploy
- [ ] Create PR with detailed description
- [ ] Code review
- [ ] Merge to main
- [ ] Monitor production logs

---

## SUCCESS CRITERIA

**The migration is complete when:**

✅ All 17 view functions work without errors
✅ No deprecated forms exist in codebase
✅ WorkItemSerializer is implemented and working
✅ Monitoring serializer uses WorkItem
✅ All tests pass
✅ No orphaned code remains
✅ Production runs without 500 errors

---

## RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Views still crash | LOW | HIGH | Thorough testing before merge |
| Data loss during migration | VERY LOW | CRITICAL | WorkItem model already exists, just updating forms |
| API compatibility issues | MEDIUM | MEDIUM | Maintain field names, test all endpoints |
| Missing edge cases | MEDIUM | MEDIUM | Comprehensive testing checklist |
| Merge conflicts | LOW | LOW | Small, focused changes per file |

---

## NOTES

**Current Situation:**
- ✅ WorkItem model exists and is stable
- ✅ WorkItem form exists and is complete
- ❌ Views still use deprecated forms (17 crash points)
- ❌ No WorkItem serializer
- ❌ Monitoring uses legacy StaffTask serializer

**Why This Is Critical:**
- Users WILL encounter 500 errors
- Multiple core features are broken
- Forms raise NotImplementedError on instantiation
- This is a production-blocking issue

**Estimated Total Effort:**
- Critical fixes: 1-1.5 hours
- Serializer work: 30-45 minutes
- Testing: 30-45 minutes
- Documentation: 15-20 minutes
- **Total: 2.5-3.5 hours**

---

**Related Documents:**
- [Full Audit Report](FORMS_SERIALIZERS_AUDIT_REPORT.md)
- [WorkItem Migration Guide](WORKITEM_MIGRATION_COMPLETE.md)
- [UI Components Guide](docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md)

---

**Report Generated:** October 5, 2025
**Next Action:** Begin Step 1 (Preparation)
