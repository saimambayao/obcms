# MOA PPA WorkItem Integration: Visual Diagrams

**Document Type**: Architecture Diagrams
**Date**: 2025-10-05
**Last Updated**: 2025-10-06
**Purpose**: Quick Visual Reference for System Integration

**Note**: This document uses correct BARMM agency nomenclature:
- **MFBM**: Ministry of Finance and Budget Management (budget formulation, execution, fiscal policy)
- **BPDA**: Bangsamoro Planning and Development Authority (planning, development coordination, BDP alignment)
- **BICTO**: Bangsamoro ICT Office (ICT infrastructure, OBCMS platform, e-governance)

---

## 1. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MONITORING ENTRY (PPA)                          │
│                     Source of Truth for Budget                       │
├─────────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                       │
│ title: CharField                                                    │
│ category: 'moa_ppa' | 'oobc_ppa' | 'obc_request'                    │
│ budget_allocation: Decimal (MASTER BUDGET)                          │
│ approval_status: 'draft' | ... | 'enacted'                          │
│ fiscal_year: Integer                                                │
│ sector: 'economic' | 'social' | ...                                 │
│                                                                     │
│ === NEW FIELDS ===                                                  │
│ execution_project: OneToOne → WorkItem (FK)                         │
│ enable_workitem_tracking: Boolean                                   │
│ budget_distribution_policy: 'manual' | 'equal' | 'weighted'         │
│ auto_sync_progress: Boolean                                         │
│ auto_sync_status: Boolean                                           │
└──────────────────┬──────────────────────────────────────────────────┘
                   │ 1:1 relationship
                   │ (bidirectional)
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     WORK ITEM (PROJECT)                             │
│                     Execution Tracking Root                          │
├─────────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                       │
│ work_type: 'project' (REQUIRED for PPA linkage)                    │
│ title: CharField                                                    │
│ status: 'not_started' | 'in_progress' | 'completed' | ...           │
│ progress: Integer (0-100) - AUTO-CALCULATED                         │
│ parent: FK → WorkItem (NULL for top-level)                          │
│                                                                     │
│ === NEW FIELDS ===                                                  │
│ related_ppa: FK → MonitoringEntry (EXPLICIT)                        │
│ allocated_budget: Decimal (DISTRIBUTED PORTION)                     │
│ actual_expenditure: Decimal                                         │
│ budget_notes: TextField                                             │
└──────────────────┬──────────────────────────────────────────────────┘
                   │ parent-child (MPTT hierarchy)
                   │
     ┌─────────────┼─────────────┬─────────────┐
     │             │             │             │
     ▼             ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│WorkItem  │  │WorkItem  │  │WorkItem  │  │WorkItem  │
│(Activity)│  │(Activity)│  │(Activity)│  │(Sub-Proj)│
│          │  │          │  │          │  │          │
│Budget:   │  │Budget:   │  │Budget:   │  │Budget:   │
│1.5M      │  │2.0M      │  │1.0M      │  │500K      │
└────┬─────┘  └────┬─────┘  └──────────┘  └──────────┘
     │             │
     │             │
┌────┴───┐    ┌────┴───┐
│WorkItem│    │WorkItem│
│(Task)  │    │(Task)  │
│        │    │        │
│Budget: │    │Budget: │
│300K    │    │500K    │
└────────┘    └────────┘
```

---

## 2. Data Flow Diagram: Budget Distribution

```
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: PPA Creation                                               │
│  User creates MonitoringEntry via form                              │
│  Budget: PHP 5,000,000                                              │
│  Approval Status: draft                                             │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Technical Review Approval                                  │
│  PPAApprovalService.approve_technical_review(ppa, user)             │
│                                                                     │
│  Side Effect:                                                       │
│  - Auto-create WorkItem project from PPA                            │
│  - Link via ppa.execution_project = project                         │
│  - Set ppa.enable_workitem_tracking = True                          │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: WBS Decomposition                                          │
│  User manually creates sub-projects/activities/tasks OR             │
│  Uses auto-generation:                                              │
│    WorkItemGenerationService.generate_default_structure_program()   │
│                                                                     │
│  Result:                                                            │
│  Project → 3 Sub-Projects (Planning, Implementation, M&E)           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Budget Distribution                                        │
│  BudgetDistributionService.distribute_budget_weighted(ppa, {        │
│    'planning-id': 0.20,      // 20% = 1,000,000                     │
│    'implementation-id': 0.60, // 60% = 3,000,000                    │
│    'me-id': 0.20             // 20% = 1,000,000                     │
│  })                                                                 │
│                                                                     │
│  Result:                                                            │
│  Each WorkItem.allocated_budget set                                 │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: Budget Review Approval                                     │
│  PPAApprovalService.approve_budget_review(ppa, user)                │
│                                                                     │
│  Side Effect:                                                       │
│  - Lock all WorkItem budget allocations (prevent changes)           │
│  - Validate total allocated ≤ PPA budget                            │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6: Budget Enactment                                           │
│  PPAApprovalService.enact_budget(ppa, user)                         │
│                                                                     │
│  Side Effect:                                                       │
│  - Activate WorkItem project (status → 'in_progress')               │
│  - Release budget for execution                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Progress Sync Flow: WorkItem → PPA

```
┌─────────────────────────────────────────────────────────────────────┐
│  TRIGGER: User marks WorkItem task as completed                     │
│  Action: task.status = 'completed'                                  │
│  Signal: workitem_status_changed.send(instance=task)                │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: Update Parent Progress (MPTT Propagation)                  │
│  task.parent.update_progress()                                      │
│                                                                     │
│  Calculation:                                                       │
│  progress = (completed_children / total_children) * 100             │
│                                                                     │
│  Example:                                                           │
│  Activity has 5 tasks, 3 completed → 60% progress                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Propagate to Root Project                                  │
│  Recursively update all ancestors up to root project                │
│                                                                     │
│  Root Project Progress Calculation:                                 │
│  - All descendants: 42 tasks                                        │
│  - Completed: 18 tasks                                              │
│  - Progress: 42.9%                                                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Sync to PPA (if auto_sync_progress = True)                 │
│  Signal handler calls:                                              │
│    ppa = root_project.related_ppa                                   │
│    ppa.sync_progress_from_workitem()                                │
│                                                                     │
│  Result:                                                            │
│  MonitoringEntry.progress = 43 (rounded from 42.9%)                 │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Update Dashboard & Reports                                 │
│  - PPA progress bar updates via HTMX                                │
│  - Calendar events reflect new status                               │
│  - Email notifications sent (if configured)                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Status Sync Mapping: WorkItem → PPA

```
WorkItem Status              PPA Status           Notes
────────────────────────────────────────────────────────────────────
'not_started'           →    'planning'          Initial state
'in_progress'           →    'ongoing'           Active execution
'at_risk'               →    'ongoing'           Flag in notes, send alert
'blocked'               →    'on_hold'           Manual intervention required
'completed'             →    'completed'         All work finished
'cancelled'             →    'cancelled'         Project terminated
```

**Sync Logic**:
```python
def sync_status_from_workitem(self):
    """MonitoringEntry method."""
    if not self.execution_project or not self.auto_sync_status:
        return self.status

    status_mapping = {
        'not_started': 'planning',
        'in_progress': 'ongoing',
        'at_risk': 'ongoing',
        'blocked': 'on_hold',
        'completed': 'completed',
        'cancelled': 'cancelled',
    }

    new_status = status_mapping.get(self.execution_project.status)

    if new_status and new_status != self.status:
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])

        # Special handling for 'at_risk'
        if self.execution_project.status == 'at_risk':
            Alert.objects.create(
                alert_type='workitem_execution_at_risk',
                severity='medium',
                title=f"PPA Execution At Risk: {self.title}",
                description=f"Linked WorkItem project is flagged as at risk.",
                related_ppa=self
            )

    return self.status
```

---

## 5. Budget Variance Tracking Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  TRIGGER: User records expenditure                                  │
│  Action: task.actual_expenditure = 350,000 (allocated: 300,000)     │
│  Variance: -50,000 (over budget by PHP 50K)                         │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: Calculate Variance (WorkItem Method)                       │
│  variance = task.get_budget_variance()                              │
│                                                                     │
│  Returns:                                                           │
│  {                                                                  │
│    'allocated': 300000.00,                                          │
│    'actual': 350000.00,                                             │
│    'variance': -50000.00,                                           │
│    'variance_pct': -16.67,                                          │
│    'status': 'over_budget'                                          │
│  }                                                                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Create Alert (via Signal)                                  │
│  Alert.objects.create(                                              │
│    alert_type='workitem_budget_variance',                           │
│    severity='high',                                                 │
│    title='Budget Overrun: Venue Booking Task',                      │
│    description='Actual expenditure exceeds allocation by 16.67%',   │
│    related_workflow=task,                                           │
│    related_ppa=task.get_ppa_source()                                │
│  )                                                                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Rollup to Parent (Activity Level)                          │
│  activity.get_allocated_budget_rollup()  // Sum all tasks           │
│  activity.get_expenditure_rollup()       // Sum all actuals         │
│                                                                     │
│  Activity Variance: -50,000 (if no other tasks compensate)          │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Rollup to Project (PPA Level)                              │
│  project.get_expenditure_rollup()                                   │
│                                                                     │
│  If project total expenditure > PPA.budget_allocation:              │
│    Create CRITICAL alert                                            │
│    Notify executive approver                                        │
│    Flag PPA in dashboard (red indicator)                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Approval Workflow Integration

```
┌─────────────────────────────────────────────────────────────────────┐
│  MonitoringEntry Approval Stages                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. DRAFT                                                           │
│     - PPA created, no WorkItem yet                                  │
│     - Budget planning in progress                                   │
│     - NOT visible to approvers                                      │
│                                                                     │
│  ────────────────────────────────────────────────────────────────   │
│                                                                     │
│  2. TECHNICAL_REVIEW                                                │
│     - Submit for technical assessment                               │
│     ▶ TRIGGER: Auto-create WorkItem project                         │
│       WorkItemGenerationService.create_project_from_ppa()           │
│     - Reviewer can see execution plan (WBS)                         │
│                                                                     │
│  ────────────────────────────────────────────────────────────────   │
│                                                                     │
│  3. BUDGET_REVIEW                                                   │
│     - Budget office validates allocations                           │
│     - Reviews budget distribution across work items                 │
│     ▶ TRIGGER: Lock WorkItem budget allocations                     │
│       BudgetDistributionService.lock_budget_allocations()           │
│     - Check against budget ceilings                                 │
│                                                                     │
│  ────────────────────────────────────────────────────────────────   │
│                                                                     │
│  4. STAKEHOLDER_CONSULTATION                                        │
│     - OBC communities review                                        │
│     - Partner organizations provide input                           │
│     - NO WorkItem changes (read-only WBS view)                      │
│                                                                     │
│  ────────────────────────────────────────────────────────────────   │
│                                                                     │
│  5. EXECUTIVE_APPROVAL                                              │
│     - Executive approves budget and execution plan                  │
│     - Final go/no-go decision                                       │
│                                                                     │
│  ────────────────────────────────────────────────────────────────   │
│                                                                     │
│  6. APPROVED                                                        │
│     - PPA approved, awaiting budget release                         │
│                                                                     │
│  ────────────────────────────────────────────────────────────────   │
│                                                                     │
│  7. ENACTED                                                         │
│     - Budget officially released                                    │
│     ▶ TRIGGER: Activate WorkItem project                            │
│       project.status = 'in_progress'                                │
│     - Execution can begin                                           │
│     - Progress tracking active                                      │
│                                                                     │
│  ────────────────────────────────────────────────────────────────   │
│                                                                     │
│  8. REJECTED (Terminal State)                                       │
│     - PPA rejected at any stage                                     │
│     ▶ TRIGGER: Archive WorkItem project                             │
│       project.status = 'cancelled'                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  PPA Detail Page │  │  Budget Dist UI  │  │  WorkItem Board │  │
│  │  (HTMX)          │  │  (Drag-drop)     │  │  (Kanban)       │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬────────┘  │
│           │                     │                     │            │
└───────────┼─────────────────────┼─────────────────────┼────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API LAYER (DRF)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  /api/monitoring-entries/{id}/enable_workitem_tracking/            │
│  /api/monitoring-entries/{id}/budget_allocation_tree/              │
│  /api/monitoring-entries/{id}/distribute_budget/                   │
│  /api/monitoring-entries/{id}/sync_from_workitem/                  │
│  /api/work-items/{id}/                                             │
│  /api/work-items/{id}/hierarchy/                                   │
│                                                                     │
└───────────┬─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  WorkItemGenerationService                                  │   │
│  │  - create_project_from_ppa()                                │   │
│  │  - generate_default_structure_program()                     │   │
│  │  - generate_default_structure_activity()                    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  BudgetDistributionService                                  │   │
│  │  - distribute_budget_equally()                              │   │
│  │  - distribute_budget_weighted()                             │   │
│  │  - distribute_budget_manual()                               │   │
│  │  - get_allocation_tree()                                    │   │
│  │  - lock_budget_allocations()                                │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  PPAApprovalService (Enhanced)                              │   │
│  │  - approve_technical_review() → create WorkItem             │   │
│  │  - approve_budget_review() → lock budgets                   │   │
│  │  - enact_budget() → activate project                        │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
└───────────┬─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER (Django ORM)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐         ┌──────────────────────┐         │
│  │  MonitoringEntry    │◄───────►│  WorkItem (MPTT)     │         │
│  │  (PPA)              │   1:1   │  (Project Hierarchy) │         │
│  │                     │         │                      │         │
│  │  budget_allocation  │         │  allocated_budget    │         │
│  │  approval_status    │         │  actual_expenditure  │         │
│  │  execution_project  │────────►│  related_ppa         │         │
│  └─────────────────────┘         │  parent (MPTT)       │         │
│                                  └──────────────────────┘         │
│                                                                     │
│  ┌─────────────────────┐         ┌──────────────────────┐         │
│  │  BudgetApprovalStage│         │  Alert               │         │
│  │  (Approval Workflow)│         │  (Budget Variance)   │         │
│  └─────────────────────┘         └──────────────────────┘         │
│                                                                     │
└───────────┬─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKGROUND TASKS (Celery)                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  auto_sync_ppa_progress (Nightly)                           │   │
│  │  - For each PPA with enable_workitem_tracking=True          │   │
│  │  - Sync progress from WorkItem hierarchy                    │   │
│  │  - Create audit log                                         │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  detect_budget_variances (Every 6 hours)                    │   │
│  │  - Check for actual_expenditure > allocated_budget          │   │
│  │  - Create alerts for variances                              │   │
│  │  - Notify stakeholders                                      │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Database Schema Diagram (Key Tables)

```sql
-- MONITORING.MONITORINGENTRY (PPA)
CREATE TABLE monitoring_monitoringentry (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    category VARCHAR(20),  -- 'moa_ppa', 'oobc_ppa', 'obc_request'
    budget_allocation NUMERIC(14,2),
    approval_status VARCHAR(30),  -- 'draft', ..., 'enacted'
    fiscal_year INTEGER,

    -- NEW FIELDS
    execution_project_id UUID REFERENCES common_workitem(id) ON DELETE SET NULL,
    enable_workitem_tracking BOOLEAN DEFAULT FALSE,
    budget_distribution_policy VARCHAR(20) DEFAULT 'manual',
    auto_sync_progress BOOLEAN DEFAULT TRUE,
    auto_sync_status BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- COMMON.WORKITEM (Project Hierarchy)
CREATE TABLE common_workitem (
    id UUID PRIMARY KEY,
    work_type VARCHAR(20),  -- 'project', 'sub_project', 'activity', 'task', 'subtask'
    title VARCHAR(500),
    status VARCHAR(20),  -- 'not_started', 'in_progress', 'completed', ...
    progress SMALLINT,  -- 0-100

    -- MPTT Fields
    parent_id UUID REFERENCES common_workitem(id) ON DELETE CASCADE,
    lft INTEGER,
    rght INTEGER,
    tree_id INTEGER,
    level INTEGER,

    -- NEW EXPLICIT FKs
    related_ppa_id UUID REFERENCES monitoring_monitoringentry(id) ON DELETE SET NULL,
    related_assessment_id UUID REFERENCES mana_assessment(id) ON DELETE SET NULL,
    related_policy_id UUID REFERENCES policy_tracking_policyrecommendation(id) ON DELETE SET NULL,
    related_community_id UUID REFERENCES communities_barangayobc(id) ON DELETE SET NULL,

    -- NEW BUDGET TRACKING
    allocated_budget NUMERIC(14,2),
    actual_expenditure NUMERIC(14,2) DEFAULT 0,
    budget_notes TEXT,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_monitoringentry_execution_project ON monitoring_monitoringentry(execution_project_id);
CREATE INDEX idx_workitem_related_ppa ON common_workitem(related_ppa_id, work_type);
CREATE INDEX idx_workitem_parent_mptt ON common_workitem(parent_id, lft, rght);
CREATE INDEX idx_workitem_budget ON common_workitem(allocated_budget, actual_expenditure);
```

---

## 9. API Request/Response Examples

### Enable WorkItem Tracking

**Request**:
```http
POST /api/monitoring-entries/123e4567-e89b-12d3-a456-426614174000/enable_workitem_tracking/
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "structure_template": "activity"
}
```

**Response**:
```json
{
  "message": "WorkItem tracking enabled",
  "execution_project_id": "987fcdeb-51a2-43d1-b789-123456789abc",
  "structure_template": "activity"
}
```

### Get Budget Allocation Tree

**Request**:
```http
GET /api/monitoring-entries/123e4567-e89b-12d3-a456-426614174000/budget_allocation_tree/
Authorization: Bearer <jwt-token>
```

**Response**:
```json
{
  "ppa_budget": "5000000.00",
  "allocated_to_workitems": "4500000.00",
  "unallocated": "500000.00",
  "allocation_percentage": 90.0,
  "breakdown": [
    {
      "work_item_id": "987fcdeb-51a2-43d1-b789-123456789abc",
      "title": "Livelihood Training Program FY2025",
      "work_type": "project",
      "level": 0,
      "allocated_budget": "0.00",
      "actual_expenditure": "0.00",
      "variance": "0.00",
      "variance_pct": 0.0,
      "children": [
        {
          "work_item_id": "aaa11111-2222-3333-4444-555555555555",
          "title": "Preparation",
          "work_type": "activity",
          "level": 1,
          "allocated_budget": "750000.00",
          "actual_expenditure": "0.00",
          "variance": "750000.00",
          "variance_pct": 0.0,
          "children": [
            {
              "work_item_id": "bbb22222-3333-4444-5555-666666666666",
              "title": "Venue Booking",
              "work_type": "task",
              "level": 2,
              "allocated_budget": "300000.00",
              "actual_expenditure": "0.00",
              "variance": "300000.00",
              "variance_pct": 0.0,
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

### Distribute Budget (Weighted)

**Request**:
```http
POST /api/monitoring-entries/123e4567-e89b-12d3-a456-426614174000/distribute_budget/
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "method": "weighted",
  "weights": {
    "aaa11111-2222-3333-4444-555555555555": "0.15",
    "bbb22222-3333-4444-5555-666666666666": "0.75",
    "ccc33333-4444-5555-6666-777777777777": "0.10"
  }
}
```

**Response**:
```json
{
  "ppa_budget": "5000000.00",
  "allocated_to_workitems": "5000000.00",
  "unallocated": "0.00",
  "allocation_percentage": 100.0,
  "breakdown": [...]
}
```

---

## 10. User Journey: Enable Execution Tracking

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER: OOBC Program Manager                                         │
│  GOAL: Enable detailed execution tracking for approved PPA          │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Navigate to PPA Detail Page
  URL: /monitoring/entry/123e4567-e89b-12d3-a456-426614174000/
  Current Status: PPA approved, no execution tracking

Step 2: Click "Enable Execution Tracking"
  Button: <i class="fas fa-check-circle"></i> Enable Execution Tracking
  Modal: "Choose WBS Structure Template"
    - Option 1: Program (3 sub-projects)
    - Option 2: Activity (3 activities)
    - Option 3: Minimal (empty project)

Step 3: Select Template and Confirm
  User selects: "Activity" template
  API Call: POST /api/monitoring-entries/{id}/enable_workitem_tracking/
    { "structure_template": "activity" }

Step 4: System Auto-Generates WBS
  Created:
    - 1 Project: "Livelihood Training Program FY2025"
    - 3 Activities: "Preparation", "Execution", "Completion"
  Budget: Distributed (15%, 75%, 10%)

Step 5: View Execution Tracking Section
  Page refreshes (HTMX swap)
  Shows:
    - Budget allocation tree (visual breakdown)
    - Progress overview (0 tasks completed)
    - Link to full project view

Step 6: Customize WBS (Optional)
  User clicks "View Full Project"
  Navigates to WorkItem project detail
  Can:
    - Add/edit/delete activities and tasks
    - Adjust budget allocations (if not locked)
    - Assign staff to tasks
    - Set deadlines

Step 7: Execute and Monitor
  As tasks are completed:
    - Progress auto-updates in PPA
    - Budget variance tracked
    - Alerts generated for issues
```

---

**End of Diagrams Document**

**Usage**: Reference this document for quick visual understanding of integration architecture.

**Maintained By**: BICTO System Architect (OBCMS Platform)
**Last Updated**: 2025-10-06
