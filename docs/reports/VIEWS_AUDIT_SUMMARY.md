# Views Audit Summary - Quick Reference

## Deliverables

### 1. Legacy Model References Count

**By Model Type:**
- **StaffTask:** 9 references across 2 files
- **Event:** 35+ references across 3 files  
- **ProjectWorkflow:** 15+ references across 2 files
- **TOTAL:** 59+ legacy references

**By File:**
```
┌───────────────────────────────────┬───────────┬───────┬────────────────┬───────┬────────────────────┐
│ File                              │ StaffTask │ Event │ ProjectWorkflow│ Total │ Migration Status   │
├───────────────────────────────────┼───────────┼───────┼────────────────┼───────┼────────────────────┤
│ src/common/views.py               │     6     │  13   │       0        │  19   │ ❌ NOT MIGRATED    │
│ src/coordination/views.py         │     0     │  30+  │       0        │  30+  │ ⚠️ PARTIAL        │
│ src/project_central/views.py      │     0     │   1   │      15+       │  16+  │ ⚠️ PARTIAL        │
│ src/mana/views.py                 │     3     │   2   │       0        │   5   │ ❌ NOT MIGRATED    │
│ src/project_central/views_enh...  │     0     │   0   │       1        │   1   │ ⚠️ PARTIAL        │
└───────────────────────────────────┴───────────┴───────┴────────────────┴───────┴────────────────────┘
```

### 2. WorkItem Adoption

**Files Using WorkItem:**
- ✅ `src/common/views/work_items.py` - 100% WorkItem (FULLY MIGRATED)
- ⚠️ `src/common/views/management.py` - 13 WorkItem refs (PARTIAL - has stubs)
- ⚠️ `src/project_central/views.py` - 5 WorkItem.objects queries (PARTIAL - mixed with ProjectWorkflow)

**WorkItem.objects Query Locations:**
1. Line 559: `WorkItem.objects.filter(related_project=workflow, work_type='activity')`
2. Line 563: `WorkItem.objects.none()` (fallback)
3. Line 691: `WorkItem.objects.filter(linked_workflow=workflow)`
4. Line 1494: `WorkItem.objects.filter(**base_filter)`
5. Line 1606: `WorkItem.objects.filter(**base_filters).exists()`

### 3. Problem Files List

**CRITICAL (Immediate Action Required):**

1. **`src/common/views.py` (2277 lines)** 🔴
   - Line 1952: `from common.models.staff import StaffTask`
   - Line 1976: `StaffTask.objects.filter(assigned_to=request.user)`
   - Line 2086: `from common.models.staff import StaffTask`
   - Line 2121: `StaffTask.objects.filter(assigned_to=request.user)`
   - Line 2210: `from common.models.staff import StaffTask`
   - Line 2229: `StaffTask.objects.filter(assigned_to=request.user, status='pending')`
   - Line 115: `from coordination.models import Event, Partnership`
   - Line 138: `Event.objects.count()`
   - Line 140: `Event.objects.filter(event_date__gte=today)`
   - Lines 551, 583, 618: Event queries
   - Lines 624-627: Event type breakdown queries
   - Lines 1256, 1317: Event.objects.select_related
   - Line 1970: `Event.objects.filter(event_date__gte=today)`
   - Line 2136: `Event.objects.filter(event_date__gte=today)`
   
   **Functions:** `home_view()`, `obc_staff_management_list()`, `coordination_dashboard()`, `coordination_home()`, `oobc_calendar()`, `oobc_calendar_api()`, `get_user_metrics()`

2. **`src/mana/views.py`** 🔴
   - Line 411: `from common.models import StaffTask`
   - Line 414: `StaffTask.objects.filter(related_assessment=assessment)`
   - Line 549: `from common.models import StaffTask`
   - Line 551: `StaffTask.objects.filter(related_assessment=assessment)`
   - Line 574: `from coordination.models import Event`
   - Line 576: `Event.objects.filter(related_assessment=assessment)`
   
   **Functions:** `assessment_detail()`, `assessment_tasks_board()`

**MEDIUM-HIGH Priority:**

3. **`src/coordination/views.py`** 🟡
   - Lines 23-24: EventForm, EventQuickUpdateForm imports
   - Line 516: `EventForm(request.POST)`
   - Line 572: `get_object_or_404(Event, pk=event_id)`
   - Lines 597, 625: Event.objects.filter (recurring)
   - Line 691: `Event.objects.select_related("community", "organizer")`
   - Line 749: `get_object_or_404(Event, pk=event_id)`
   - Lines 991, 1011, 1070, 1128: Event attendance tracking
   
   **Functions:** `create_recurring_event()`, `edit_event_instance()`, `coordination_events()`, `event_quick_update_htmx()`, `delete_event()`, attendance functions

4. **`src/project_central/views.py`** 🟡
   - Line 24: `from common.proxies import ProjectWorkflowProxy as ProjectWorkflow`
   - Line 169: `ProjectWorkflow.objects.all()[:10]`
   - Lines 612, 635: ProjectWorkflowFromPPAForm
   - Line 655: `ProjectWorkflow.objects.select_related()`
   - Line 744: `ProjectWorkflow.objects.all().order_by("-initiated_date")`
   - Lines 771, 810, 1582, 1881: get_object_or_404(ProjectWorkflow)
   - Line 1147: `ProjectWorkflow.objects.filter(primary_need__in=linked_needs)`
   - Line 1866: `ProjectWorkflow.objects.select_related()`
   
   **7 Deprecated Functions:** Still contain active code despite @deprecated_workflow_view markers

**LOW Priority:**

5. **`src/project_central/views_enhanced_dashboard.py`** 🟢
   - Line 97: `ProjectWorkflow.objects.all()[:10]`

### 4. Migration Status

**Fully Migrated:**
- ✅ 1 file (5%): `src/common/views/work_items.py`

**Partially Migrated (Mixed Usage):**
- ⚠️ 2 files (30%): 
  - `src/project_central/views.py` (has WorkItem + ProjectWorkflow)
  - `src/common/views/management.py` (has WorkItem imports + deprecated stubs)

**Not Migrated:**
- ❌ 3 files (65%):
  - `src/common/views.py` (CRITICAL - 19 refs)
  - `src/coordination/views.py` (30+ Event refs)
  - `src/mana/views.py` (5 refs)

**Stub/Deprecated Views:**
- 10 functions total:
  - 3 in `src/common/views/management.py`
  - 7 in `src/project_central/views.py`

## Migration Roadmap

### Phase 1: Core System Views
**Target:** `src/common/views.py` + `src/mana/views.py`
- 24 total legacy references
- Core functionality
- Affects: Dashboard, Calendar, Metrics, Assessments

### Phase 2: Domain-Specific Views
**Target:** `src/coordination/views.py` + Complete `src/project_central/views.py`
- 46+ legacy references
- Event management + Project workflows
- Affects: Coordination, Project tracking

### Phase 3: Cleanup
**Target:** Remove all deprecated views and stubs
- Delete 10 deprecated functions
- Clean up legacy imports
- Update URL routing

## Statistics

```
Total View Files:          32
Files with Legacy Refs:     5
Files with WorkItem:        3
Total Legacy References:   59+
Deprecated Functions:      10

Migration Progress:
  Fully Migrated:   5% (1 file)
  Partial:         30% (2 files)  
  Not Migrated:    65% (3 files)
```

---

**Full Details:** See `VIEWS_AUDIT_COMPREHENSIVE.md`  
**Generated:** October 5, 2025
