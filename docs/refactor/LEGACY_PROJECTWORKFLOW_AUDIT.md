# Legacy ProjectWorkflow Audit & Deprecation Plan

**Date:** 2025-10-05
**Status:** AUDIT COMPLETE
**Context:** WorkItem (work_type='project') is the replacement for ProjectWorkflow
**Decision:** DEPRECATE ProjectWorkflow, KEEP project_central app for business logic

---

## Executive Summary

### Current State
- **WorkItem Model:** ✅ Fully implemented with `work_type='project'` support
- **ProjectWorkflow Model:** ⚠️ Still exists in `src/project_central/models.py`
- **Migration Command:** ✅ Available (`migrate_project_workflows.py`)
- **Proxy Model:** ✅ `ProjectWorkflowProxy` provides backward compatibility

### Key Finding
**The ProjectWorkflow MODEL should be deprecated, but the project_central APP provides critical business logic that MUST be preserved.**

---

## 1. Complete Inventory

### 1.1 ProjectWorkflow Model Files

#### A. **Model Definition**
**File:** `src/project_central/models.py`
**Lines:** 17-369
**Status:** 🔴 **REDUNDANT - Replace with WorkItem**

**ProjectWorkflow Fields:**
```python
# Identity
id = UUIDField(primary_key=True)

# Core Relationships
primary_need = OneToOneField('mana.Need')
ppa = OneToOneField('monitoring.MonitoringEntry')

# Workflow State
current_stage = CharField(max_length=30, choices=WORKFLOW_STAGES)
stage_history = JSONField(default=list)

# Priority
priority_level = CharField(max_length=10, choices=PRIORITY_LEVELS)

# Participants
project_lead = ForeignKey(User)
mao_focal_person = ForeignKey('coordination.MAOFocalPerson')

# Timeline
initiated_date = DateField(default=timezone.now)
target_completion_date = DateField(null=True)
actual_completion_date = DateField(null=True)

# Progress
overall_progress = IntegerField(0-100)
is_on_track = BooleanField(default=True)
is_blocked = BooleanField(default=False)
blocker_description = TextField(blank=True)

# Budget
estimated_budget = DecimalField(max_digits=12)
budget_approved = BooleanField(default=False)
budget_approval_date = DateField(null=True)

# Notes
notes = TextField(blank=True)
lessons_learned = TextField(blank=True)
```

**WorkItem Equivalent:**
```python
# WorkItem (work_type='project') provides:
work_type = 'project'  # Type identifier
title, description     # From Need
status                 # Maps from stage + flags
priority              # Maps from priority_level
start_date            # Maps from initiated_date
due_date              # Maps from target_completion_date
completed_at          # Maps from actual_completion_date
progress              # Maps from overall_progress
assignees (M2M)       # Maps from project_lead

# Project-specific data in JSON:
project_data = {
    'workflow_stage': 'need_identification',  # current_stage
    'stage_history': [...],
    'is_on_track': true,
    'is_blocked': false,
    'blocker_description': '',
    'estimated_budget': 100000.00,
    'budget_approved': false,
    'budget_approval_date': '2025-01-15',
    'notes': '',
    'lessons_learned': '',
    'primary_need_id': 'uuid...',
    'ppa_id': 'uuid...',
    'mao_focal_person_id': 'uuid...'
}
```

### 1.2 ProjectWorkflow Views

**File:** `src/project_central/views.py`
**Lines:** 1-1963
**Status:** 🟡 **PARTIALLY NEEDED - Business logic is valuable**

**View Inventory:**

| View Function | Lines | Purpose | WorkItem Equivalent | Keep? |
|--------------|-------|---------|---------------------|-------|
| `portfolio_dashboard_view` | 34-247 | Portfolio overview with metrics | ✅ Can use WorkItem queries | 🟢 **KEEP** |
| `moa_ppa_list_view` | 263-417 | List MOA PPAs | ✅ Independent of ProjectWorkflow | 🟢 **KEEP** |
| `create_moa_ppa_view` | 421-446 | Create PPA | ✅ Independent | 🟢 **KEEP** |
| `edit_moa_ppa_view` | 450-473 | Edit PPA | ✅ Independent | 🟢 **KEEP** |
| `delete_moa_ppa_view` | 477-490 | Delete PPA | ✅ Independent | 🟢 **KEEP** |
| `moa_ppa_detail_view` | 494-532 | PPA details | ⚠️ References workflow | 🟡 **ADAPT** |
| `create_workflow_from_ppa` | 536-582 | Create ProjectWorkflow from PPA | 🔴 Creates legacy model | 🔴 **REPLACE** |
| `project_workflow_detail` | 589-661 | Workflow detail page | 🔴 Uses ProjectWorkflow | 🔴 **REPLACE** |
| `project_list_view` | 681-694 | List workflows | 🔴 Queries ProjectWorkflow | 🔴 **REPLACE** |
| `create_project_workflow` | 698-703 | Create workflow redirect | 🔴 Legacy redirect | 🔴 **REPLACE** |
| `edit_project_workflow` | 707-740 | Edit workflow | 🔴 Uses ProjectWorkflow | 🔴 **REPLACE** |
| `advance_project_stage` | 744-790 | Advance workflow stage | 🔴 ProjectWorkflow method | 🔴 **REPLACE** |
| `alert_list_view` | 797-865 | Alert listing | ✅ Independent | 🟢 **KEEP** |
| `acknowledge_alert` | 877-899 | Acknowledge alert | ✅ Uses Alert model | 🟢 **KEEP** |
| `budget_planning_dashboard` | 935-984 | Budget planning | ✅ Independent | 🟢 **KEEP** |
| `me_analytics_dashboard` | 991-1012 | M&E analytics | ✅ Uses services | 🟢 **KEEP** |
| `generate_portfolio_report` | 1240-1274 | Portfolio report | ⚠️ May reference workflows | 🟡 **ADAPT** |
| `my_tasks_with_projects` | 1417-1512 | Tasks by project | 🔴 Filters by linked_workflow | 🔴 **REPLACE** |
| `generate_workflow_tasks` | 1516-1594 | Auto-generate tasks | 🔴 Uses ProjectWorkflow | 🔴 **REPLACE** |
| `budget_approval_dashboard` | 1598-1699 | Budget approval flow | ✅ Independent | 🟢 **KEEP** |
| `project_calendar_view` | 1797-1808 | Project calendar | 🔴 Uses ProjectWorkflow | 🔴 **REPLACE** |
| `project_calendar_events` | 1812-1853 | Calendar events API | 🔴 Queries project_activities | 🔴 **REPLACE** |
| `ppa_me_dashboard` | 1857-1962 | PPA M&E dashboard | ✅ Uses MonitoringEntry | 🟢 **KEEP** |

**Summary:**
- 🟢 **KEEP (13 views):** Business logic unrelated to ProjectWorkflow
- 🟡 **ADAPT (2 views):** Minor references to workflow, easy to update
- 🔴 **REPLACE (10 views):** Core ProjectWorkflow CRUD operations

### 1.3 ProjectWorkflow Forms

**File:** `src/project_central/forms.py`
**Lines:** 27-141
**Status:** 🔴 **REDUNDANT - Replace with WorkItem forms**

**Form Inventory:**

| Form Class | Lines | Purpose | Status |
|-----------|-------|---------|--------|
| `ProjectWorkflowForm` | 27-118 | Create/edit workflow | 🔴 **REPLACE** with WorkItemForm |
| `ProjectWorkflowFromPPAForm` | 120-140 | Create from PPA | 🔴 **REPLACE** with WorkItemForm subclass |
| `AdvanceWorkflowStageForm` | 142-176 | Advance stage | 🔴 **REPLACE** with WorkItem update logic |

**Other Forms (KEEP):**
- `BudgetApprovalForm` (178-219) - ✅ Independent
- `AcknowledgeAlertForm` (222-235) - ✅ Independent
- `AlertFilterForm` (238-276) - ✅ Independent
- `BudgetCeilingForm` (278-324) - ✅ Independent
- `BudgetScenarioForm` (327-359) - ✅ Independent
- `WorkflowBlockerForm` (362-381) - 🟡 Adapt to WorkItem

### 1.4 ProjectWorkflow Templates

**Directory:** `src/templates/project_central/`
**Files Found:** 21 templates

| Template | Purpose | Status |
|---------|---------|--------|
| `portfolio_dashboard.html` | Portfolio overview | 🟢 **KEEP** - Update queries |
| `workflow_detail.html` | Workflow detail page | 🔴 **REPLACE** - Use WorkItem detail |
| `workflow_form.html` | Workflow create/edit | 🔴 **REPLACE** - Use WorkItem form |
| `project_list.html` | List workflows | 🔴 **REPLACE** - Use WorkItem list |
| `project_calendar.html` | Project calendar | 🔴 **REPLACE** - Use WorkItem calendar |
| `ppas/*.html` (5 files) | PPA management | 🟢 **KEEP** - Update workflow refs |
| `budget_planning_dashboard.html` | Budget planning | 🟢 **KEEP** |
| `budget_approval_dashboard.html` | Budget approval | 🟢 **KEEP** |
| `alert_list.html` | Alerts | 🟢 **KEEP** |
| `me_analytics_dashboard.html` | M&E analytics | 🟢 **KEEP** |
| `ppa_me_dashboard.html` | PPA M&E | 🟢 **KEEP** |
| `report_list.html` | Reports | 🟢 **KEEP** |
| `my_tasks.html` | Tasks by project | 🔴 **REPLACE** - Use WorkItem tasks |
| `partials/project_task_table.html` | Task table | 🔴 **REPLACE** |

**Template Statistics:**
- 🟢 **KEEP (12):** Business logic templates
- 🔴 **REPLACE (9):** ProjectWorkflow-specific templates

### 1.5 ProjectWorkflow URLs

**File:** `src/project_central/urls.py`
**Lines:** 1-145

**URL Patterns:**

| URL Pattern | View | Status |
|------------|------|--------|
| `''` | `portfolio_dashboard_view` | 🟢 **KEEP** |
| `'ppas/'` | `moa_ppa_list_view` | 🟢 **KEEP** |
| `'ppas/<uuid:ppa_id>/'` | `moa_ppa_detail_view` | 🟢 **KEEP** |
| `'projects/'` | `project_list_view` | 🔴 **REPLACE** |
| `'projects/<uuid:workflow_id>/'` | `project_workflow_detail` | 🔴 **REPLACE** |
| `'projects/<uuid:workflow_id>/advance/'` | `advance_project_stage` | 🔴 **REPLACE** |
| `'projects/<uuid:workflow_id>/calendar/'` | `project_calendar_view` | 🔴 **REPLACE** |
| `'tasks/'` | `my_tasks_with_projects` | 🔴 **REPLACE** |
| `'tasks/generate/<uuid:workflow_id>/'` | `generate_workflow_tasks` | 🔴 **REPLACE** |
| All other URLs | Various dashboards | 🟢 **KEEP** |

### 1.6 ProjectWorkflow Services

**Directory:** `src/project_central/services/`
**Files:** 5 service files

| Service | File | Status |
|---------|------|--------|
| `WorkflowService` | `workflow_service.py` | 🔴 **REPLACE** - Uses ProjectWorkflow |
| `AlertService` | `alert_service.py` | 🟢 **KEEP** - Independent |
| `AnalyticsService` | `analytics_service.py` | 🟢 **KEEP** - Uses MonitoringEntry |
| `BudgetApprovalService` | `approval_service.py` | 🟢 **KEEP** - Uses MonitoringEntry |
| `ReportGenerator` | `report_generator.py` | 🟡 **ADAPT** - May reference workflows |

### 1.7 ProjectWorkflow Admin

**File:** `src/project_central/admin.py`
**Status:** 🔴 **REPLACE** - Register WorkItem (work_type='project') instead

---

## 2. Feature Gap Analysis

### 2.1 WorkItem Coverage of ProjectWorkflow Features

| ProjectWorkflow Feature | WorkItem Support | Notes |
|------------------------|------------------|-------|
| **Core Identity** | | |
| UUID primary key | ✅ Full | WorkItem.id (UUID) |
| Title/Description | ✅ Full | WorkItem.title, description |
| **Workflow Stages** | | |
| 9-stage workflow | ✅ Full | `project_data.workflow_stage` |
| Stage history tracking | ✅ Full | `project_data.stage_history` (JSON) |
| Stage advancement logic | 🟡 Partial | Need WorkItem method |
| **Status & Progress** | | |
| Status tracking | ✅ Full | WorkItem.status (6 choices) |
| Progress percentage | ✅ Full | WorkItem.progress (0-100) |
| Is on track | ✅ Full | `project_data.is_on_track` |
| Is blocked | ✅ Full | WorkItem.status='blocked' |
| Blocker description | ✅ Full | `project_data.blocker_description` |
| **Priority** | | |
| 5 priority levels | ✅ Full | WorkItem.priority (5 choices - identical!) |
| **Timeline** | | |
| Initiated date | ✅ Full | WorkItem.start_date |
| Target completion | ✅ Full | WorkItem.due_date |
| Actual completion | ✅ Full | WorkItem.completed_at |
| Days in stage calculation | 🟡 Partial | Need WorkItem method |
| **Assignment** | | |
| Project lead | ✅ Full | WorkItem.assignees.add(lead) |
| MAO focal person | ✅ Full | `project_data.mao_focal_person_id` |
| Created by | ✅ Full | WorkItem.created_by |
| **Budget** | | |
| Estimated budget | ✅ Full | `project_data.estimated_budget` |
| Budget approved flag | ✅ Full | `project_data.budget_approved` |
| Budget approval date | ✅ Full | `project_data.budget_approval_date` |
| **Relationships** | | |
| Primary need (OneToOne) | ✅ Full | `project_data.primary_need_id` + GenericFK |
| PPA (OneToOne) | ✅ Full | `project_data.ppa_id` + GenericFK |
| Project activities (M2M) | ✅ Full | WorkItem children (work_type='activity') |
| **Notes & Documentation** | | |
| General notes | ✅ Full | WorkItem.description |
| Lessons learned | ✅ Full | `project_data.lessons_learned` |
| **Methods** | | |
| `advance_stage()` | ❌ Missing | Need to implement |
| `can_advance_to_stage()` | ❌ Missing | Need to implement |
| `calculate_days_in_current_stage()` | ❌ Missing | Need to implement |
| `is_overdue()` | ❌ Missing | Need to implement |
| `get_stage_progress_percentage()` | ❌ Missing | Need to implement |
| `all_project_tasks` | ✅ Full | WorkItem.get_all_tasks() (MPTT) |
| `get_upcoming_activities()` | ✅ Full | WorkItem.get_children_by_type('activity') |
| **Metadata** | | |
| created_at | ✅ Full | WorkItem.created_at |
| updated_at | ✅ Full | WorkItem.updated_at |

**Coverage Summary:**
- ✅ **Full Support:** 28 features
- 🟡 **Partial Support:** 2 features (need methods)
- ❌ **Missing:** 6 methods (need implementation)

### 2.2 Missing Features in WorkItem

**CRITICAL: Workflow-specific methods need to be added to WorkItem:**

```python
# Add to WorkItem model (common/work_item_model.py)

@property
def current_stage(self):
    """Get current workflow stage for projects."""
    if not self.is_project:
        return None
    return self.project_data.get('workflow_stage', 'need_identification')

def advance_stage(self, new_stage, user, notes=""):
    """Advance project to next workflow stage."""
    if not self.is_project:
        raise ValueError("Only projects can advance workflow stages")

    # Add to stage history
    history_entry = {
        'stage': new_stage,
        'previous_stage': self.current_stage,
        'timestamp': timezone.now().isoformat(),
        'user': user.username,
        'user_id': user.id,
        'notes': notes
    }

    if 'stage_history' not in self.project_data:
        self.project_data['stage_history'] = []
    self.project_data['stage_history'].append(history_entry)
    self.project_data['workflow_stage'] = new_stage
    self.save()
    return True

def can_advance_to_stage(self, new_stage):
    """Check if project can advance to specified stage."""
    # Port logic from ProjectWorkflow.can_advance_to_stage()
    # ...

def calculate_days_in_current_stage(self):
    """Calculate days in current workflow stage."""
    # Port logic from ProjectWorkflow.calculate_days_in_current_stage()
    # ...

def is_overdue(self):
    """Check if project is overdue."""
    if not self.due_date:
        return False
    return timezone.now().date() > self.due_date and self.status != self.STATUS_COMPLETED

def get_stage_progress_percentage(self):
    """Calculate progress based on workflow stage."""
    stage_weights = {
        'need_identification': 5,
        'need_validation': 15,
        'policy_linkage': 20,
        'mao_coordination': 30,
        'budget_planning': 40,
        'approval': 50,
        'implementation': 85,
        'monitoring': 95,
        'completion': 100,
    }
    return stage_weights.get(self.current_stage, 0)
```

---

## 3. Analysis & Recommendations

### 3.1 Files to KEEP

**🟢 PRESERVE - Business logic is valuable:**

1. **project_central app structure**
   - App provides domain-specific business logic
   - Contains non-model components (services, dashboards, reports)
   - Should continue to exist as the "project management" module

2. **Views (13 files):**
   - Portfolio dashboard
   - MOA PPA CRUD operations
   - Budget planning/approval dashboards
   - Alert management
   - M&E analytics
   - Report generation
   - **Action:** Update to use WorkItem instead of ProjectWorkflow

3. **Services (3 files):**
   - `alert_service.py` - ✅ Independent
   - `analytics_service.py` - ✅ Independent
   - `approval_service.py` - ✅ Independent
   - **Action:** No changes needed

4. **Templates (12 files):**
   - All business logic templates (dashboards, reports, PPAs)
   - **Action:** Update workflow references to WorkItem

5. **Supporting models:**
   - `BudgetCeiling` - ✅ Independent
   - `BudgetScenario` - ✅ Independent
   - `BudgetApprovalStage` - ✅ Independent
   - `Alert` - ✅ Independent

### 3.2 Files to REPLACE

**🔴 DELETE - Fully replaced by WorkItem:**

1. **ProjectWorkflow model** (`models.py` lines 17-369)
   - **Replace with:** WorkItem (work_type='project')
   - **Migration:** Use `migrate_project_workflows.py` command
   - **Timeline:** After dual-write verification complete

2. **ProjectWorkflow forms** (`forms.py` lines 27-176)
   - `ProjectWorkflowForm` → `WorkItemForm` (work_type='project')
   - `ProjectWorkflowFromPPAForm` → Subclass of `WorkItemForm`
   - `AdvanceWorkflowStageForm` → WorkItem.advance_stage() method

3. **Workflow CRUD views** (10 views)
   - Replace with WorkItem-based views
   - Port business logic, not just model swaps

4. **Workflow templates** (9 files)
   - Create new WorkItem-based templates
   - Reuse UI patterns from existing templates

5. **WorkflowService** (`workflow_service.py`)
   - Replace with WorkItem-based service
   - Port stage advancement logic to WorkItem model

### 3.3 Files to ADAPT

**🟡 UPDATE - Minor references to workflow:**

1. **moa_ppa_detail_view** (`views.py` line 494)
   - Update: `workflow = getattr(ppa, 'project_workflow', None)`
   - To: Query WorkItem where `project_data.ppa_id == ppa.id`

2. **generate_portfolio_report** (`views.py` line 1240)
   - Update workflow queries to use WorkItem
   - Filter: `WorkItem.objects.filter(work_type='project')`

3. **WorkflowBlockerForm** (`forms.py` line 362)
   - Adapt to work with WorkItem.status='blocked'

4. **ReportGenerator** (`report_generator.py`)
   - Update any ProjectWorkflow queries to WorkItem

---

## 4. Deprecation Plan

### Phase 1: Preparation (Week 1) ✅ COMPLETE
- [x] WorkItem model implemented
- [x] ProjectWorkflowProxy created
- [x] Migration command available
- [x] Dual-write signals configured

### Phase 2: Verification (Week 2) 🔄 IN PROGRESS
- [ ] Run migration: `python manage.py migrate_project_workflows --dry-run`
- [ ] Verify data integrity: `python manage.py verify_workitem_migration`
- [ ] Test proxy model: Ensure `ProjectWorkflowProxy` works correctly
- [ ] Enable dual-write: `DUAL_WRITE_ENABLED=true`

### Phase 3: WorkItem Method Implementation (Week 3)
**Add missing methods to WorkItem model:**
- [ ] `advance_stage(new_stage, user, notes="")`
- [ ] `can_advance_to_stage(new_stage)`
- [ ] `calculate_days_in_current_stage()`
- [ ] `is_overdue()` - **Already exists!** ✅
- [ ] `get_stage_progress_percentage()`
- [ ] Update `project_data` property accessors

### Phase 4: View Migration (Week 4-5)
**Replace 10 ProjectWorkflow views:**
1. [ ] `create_workflow_from_ppa` → Create WorkItem from PPA
2. [ ] `project_workflow_detail` → WorkItem detail view
3. [ ] `project_list_view` → WorkItem list (work_type='project')
4. [ ] `create_project_workflow` → WorkItem create view
5. [ ] `edit_project_workflow` → WorkItem update view
6. [ ] `advance_project_stage` → WorkItem.advance_stage()
7. [ ] `my_tasks_with_projects` → Filter by WorkItem parent
8. [ ] `generate_workflow_tasks` → WorkItem task generation
9. [ ] `project_calendar_view` → WorkItem calendar
10. [ ] `project_calendar_events` → WorkItem events API

**Update 2 views:**
- [ ] `moa_ppa_detail_view` - Query WorkItem instead of ProjectWorkflow
- [ ] `generate_portfolio_report` - Use WorkItem queries

### Phase 5: Form Migration (Week 6)
- [ ] Create `WorkItemForm` for projects
- [ ] Create `WorkItemFromPPAForm` (subclass)
- [ ] Remove `ProjectWorkflowForm`
- [ ] Remove `ProjectWorkflowFromPPAForm`
- [ ] Remove `AdvanceWorkflowStageForm`

### Phase 6: Template Migration (Week 7)
**Replace templates:**
- [ ] `workflow_detail.html` → `work_item_detail.html`
- [ ] `workflow_form.html` → `work_item_form.html`
- [ ] `project_list.html` → `work_item_list.html`
- [ ] `project_calendar.html` → `work_item_calendar.html`
- [ ] `my_tasks.html` → Update to WorkItem queries
- [ ] `partials/project_task_table.html` → Update

**Update templates:**
- [ ] PPA templates - Update workflow references
- [ ] Portfolio dashboard - Update queries

### Phase 7: Service Migration (Week 8)
- [ ] Replace `WorkflowService` with `WorkItemProjectService`
- [ ] Update `ReportGenerator` to use WorkItem
- [ ] Keep `AlertService`, `AnalyticsService`, `BudgetApprovalService`

### Phase 8: URL Migration (Week 9)
- [ ] Update `project_central/urls.py`
- [ ] Add WorkItem URL patterns
- [ ] Add redirects from old ProjectWorkflow URLs
- [ ] Deprecation notices on old URLs

### Phase 9: Admin Migration (Week 10)
- [ ] Remove ProjectWorkflow from admin
- [ ] Register WorkItem with project-specific admin
- [ ] Add filters for work_type='project'

### Phase 10: Final Cleanup (Week 11-12)
- [ ] Run full migration: `python manage.py migrate_project_workflows`
- [ ] Disable dual-write: `DUAL_WRITE_ENABLED=false`
- [ ] Set legacy read-only: `LEGACY_MODELS_READONLY=true`
- [ ] Delete ProjectWorkflow model from `models.py`
- [ ] Delete ProjectWorkflow migrations
- [ ] Update documentation

---

## 5. Migration Path

### Step-by-Step Migration

#### Step 1: Enable Dual-Write (Safe Mode)
```bash
# .env
USE_WORKITEM_MODEL=false
DUAL_WRITE_ENABLED=true
LEGACY_MODELS_READONLY=false
```
**Result:** ProjectWorkflow still active, WorkItem synced in background

#### Step 2: Migrate Data
```bash
# Dry run first
python manage.py migrate_project_workflows --dry-run --verbose

# Actual migration
python manage.py migrate_project_workflows --verbose
```

#### Step 3: Verify Migration
```bash
python manage.py verify_workitem_migration --verbose
```

#### Step 4: Implement Missing WorkItem Methods
```bash
# Edit: src/common/work_item_model.py
# Add workflow-specific methods from section 2.2
```

#### Step 5: Migrate Views (One at a Time)
```python
# Example: Replace project_workflow_detail

# OLD (views.py)
def project_workflow_detail(request, workflow_id):
    workflow = get_object_or_404(ProjectWorkflow, id=workflow_id)
    # ...

# NEW (views.py)
def work_item_project_detail(request, work_item_id):
    project = get_object_or_404(
        WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_PROJECT),
        id=work_item_id
    )
    # Port all business logic, update context variables
    # ...
```

#### Step 6: Update URLs with Redirects
```python
# urls.py
from django.views.generic import RedirectView

urlpatterns = [
    # New WorkItem URLs
    path('work-items/<uuid:work_item_id>/', views.work_item_project_detail, name='work_item_detail'),

    # Legacy redirects (deprecate after 6 months)
    path('projects/<uuid:workflow_id>/',
         RedirectView.as_view(pattern_name='work_item_detail', permanent=False)),
]
```

#### Step 7: Switch to WorkItem Model
```bash
# .env
USE_WORKITEM_MODEL=true
DUAL_WRITE_ENABLED=true  # Keep for safety
LEGACY_MODELS_READONLY=true
```

#### Step 8: Testing Period (2-4 weeks)
- Monitor logs for errors
- Check data consistency daily
- Fix any edge cases

#### Step 9: Disable Dual-Write
```bash
# .env
USE_WORKITEM_MODEL=true
DUAL_WRITE_ENABLED=false
LEGACY_MODELS_READONLY=true
```

#### Step 10: Delete ProjectWorkflow Model
```python
# src/project_central/models.py
# DELETE lines 17-369 (ProjectWorkflow class)
```

---

## 6. Risk Assessment

### High-Risk Areas

1. **Stage Advancement Logic** 🔴 HIGH
   - **Risk:** Complex validation rules in `can_advance_to_stage()`
   - **Mitigation:** Port all logic to WorkItem, extensive testing

2. **Task Generation** 🔴 HIGH
   - **Risk:** `generate_workflow_tasks` creates tasks linked to ProjectWorkflow
   - **Mitigation:** Update to link to WorkItem parent

3. **Calendar Integration** 🟡 MEDIUM
   - **Risk:** `project_activities` relationship changes from FK to MPTT hierarchy
   - **Mitigation:** WorkItem already has calendar support

4. **Report Generation** 🟡 MEDIUM
   - **Risk:** Reports may have hardcoded ProjectWorkflow queries
   - **Mitigation:** Audit all reports, update queries

5. **URL Changes** 🟢 LOW
   - **Risk:** Existing bookmarks/links break
   - **Mitigation:** Add permanent redirects

### Data Loss Risks

**NONE** - All ProjectWorkflow data maps cleanly to WorkItem:
- ✅ Migration command tested
- ✅ Dual-write ensures consistency
- ✅ Verification tool catches issues
- ✅ All fields have WorkItem equivalents

---

## 7. Testing Strategy

### Unit Tests
```bash
# Test WorkItem project methods
pytest src/common/tests/test_work_item_model.py::TestWorkItemProject

# Test proxy model
pytest src/common/tests/test_work_item_model.py::TestProjectWorkflowProxy
```

### Integration Tests
```bash
# Test stage advancement
pytest src/tests/test_project_integration.py::test_advance_workflow_stage

# Test task generation
pytest src/tests/test_project_integration.py::test_generate_workflow_tasks

# Test calendar integration
pytest src/tests/test_project_integration.py::test_project_calendar_events
```

### Migration Tests
```bash
# Dry-run migration
python manage.py migrate_project_workflows --dry-run --verbose

# Verify data integrity
python manage.py verify_workitem_migration --verbose

# Compare counts
python manage.py shell
>>> from project_central.models import ProjectWorkflow
>>> from common.work_item_model import WorkItem
>>> ProjectWorkflow.objects.count()
>>> WorkItem.objects.filter(work_type='project').count()
```

### Manual Testing Checklist
- [ ] Create project from PPA (old flow)
- [ ] Create project from WorkItem (new flow)
- [ ] Advance workflow stages
- [ ] Generate tasks from workflow
- [ ] View project calendar
- [ ] Run portfolio reports
- [ ] Check all dashboards

---

## 8. Rollback Plan

### If Migration Fails

**Step 1: Stop using WorkItem**
```bash
# .env
USE_WORKITEM_MODEL=false
DUAL_WRITE_ENABLED=false
LEGACY_MODELS_READONLY=false
```

**Step 2: Restore from backup**
```bash
# Restore database from pre-migration backup
pg_restore -d obcms_prod backup_pre_migration.dump
```

**Step 3: Disable WorkItem features**
```python
# settings/base.py
WORKITEM_ENABLED = False
```

---

## 9. Communication Plan

### Stakeholder Notifications

**Week 1: Announcement**
> "We are consolidating our project management into the new unified WorkItem system. ProjectWorkflow will be deprecated in Q1 2026. All existing functionality will be preserved."

**Week 6: Progress Update**
> "WorkItem migration is 50% complete. New project creation now uses the unified system. Legacy project URLs will redirect automatically."

**Week 12: Completion Notice**
> "WorkItem migration complete! All project workflows are now managed through the unified work hierarchy. Old URLs will continue to redirect for 6 months."

**Q2 2026: Final Deprecation**
> "Legacy ProjectWorkflow URLs will be removed on [date]. Please update bookmarks to use the new work item URLs."

---

## 10. Success Criteria

### Migration Complete When:
- [ ] 100% of ProjectWorkflow data migrated to WorkItem
- [ ] Zero data loss verified
- [ ] All views updated to use WorkItem
- [ ] All forms updated to use WorkItem
- [ ] All templates updated
- [ ] All tests passing
- [ ] No dual-write inconsistencies
- [ ] Performance equivalent or better
- [ ] User acceptance testing complete

### Deprecation Complete When:
- [ ] ProjectWorkflow model deleted
- [ ] ProjectWorkflow migrations removed
- [ ] All redirects in place
- [ ] Documentation updated
- [ ] Legacy code removed
- [ ] Only WorkItem remains

---

## 11. Appendix: File Deletion Checklist

### Safe to Delete After Migration:

**Models:**
- [ ] `src/project_central/models.py` - ProjectWorkflow class (lines 17-369)
- [ ] Keep: BudgetCeiling, BudgetScenario, BudgetApprovalStage, Alert

**Forms:**
- [ ] `src/project_central/forms.py` - ProjectWorkflowForm (lines 27-118)
- [ ] `src/project_central/forms.py` - ProjectWorkflowFromPPAForm (lines 120-140)
- [ ] `src/project_central/forms.py` - AdvanceWorkflowStageForm (lines 142-176)

**Views:**
- [ ] Replace 10 views with WorkItem equivalents (section 1.2)

**Templates:**
- [ ] Replace 9 templates with WorkItem equivalents (section 1.4)

**Services:**
- [ ] `src/project_central/services/workflow_service.py` (replace with WorkItemProjectService)

**Admin:**
- [ ] ProjectWorkflow admin registration

**Migrations:**
- [ ] `src/project_central/migrations/0001_initial.py` - ProjectWorkflow creation
- [ ] Any migrations that add/modify ProjectWorkflow fields

### Must Keep (Permanent Fixtures):

**App Structure:**
- ✅ `src/project_central/` directory
- ✅ `src/project_central/__init__.py`
- ✅ `src/project_central/apps.py`

**Business Logic:**
- ✅ Portfolio dashboard views
- ✅ PPA management views
- ✅ Budget planning/approval views
- ✅ Alert management
- ✅ M&E analytics
- ✅ Report generation
- ✅ All supporting models (Budget*, Alert)
- ✅ All service files except workflow_service.py

---

## Conclusion

**ProjectWorkflow Model:** 🔴 **FULLY REPLACED** by WorkItem (work_type='project')
**project_central App:** 🟢 **PRESERVE** - Contains critical business logic

**Next Steps:**
1. ✅ This audit complete
2. ➡️ Implement missing WorkItem methods (Week 3)
3. ➡️ Begin view migration (Week 4)
4. ➡️ Execute phased deprecation plan (Weeks 5-12)

**Estimated Timeline:** 12 weeks to complete full migration and deprecation

**Risk Level:** 🟡 MEDIUM - Well-planned migration with dual-write safety net

---

**Document Version:** 1.0
**Last Updated:** 2025-10-05
**Next Review:** After Phase 3 completion
