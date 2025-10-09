# PPA and WorkItem Structure Analysis

**Date:** 2025-01-08
**Purpose:** Understand current PPA and WorkItem implementation for test data creation
**Status:** Analysis Complete

---

## Executive Summary

The OBCMS currently has **209 MOA PPAs** in the database with **22 WorkItems**, of which **4 PPAs have WorkItem execution tracking enabled**. The system implements a sophisticated hierarchical work management system with budget tracking capabilities.

### Key Statistics
- **Total PPAs:** 209 (all `moa_ppa` category)
- **Total WorkItems:** 22
  - 11 Projects
  - 5 Activities
  - 4 Tasks
  - 2 Subtasks
- **PPAs with WorkItem Tracking:** 4 PPAs with execution projects
- **WorkItems with Budget:** 4 (all are execution project roots)
- **WorkItems linked to PPAs:** 11

---

## 1. MonitoringEntry Model (PPAs)

### Model: `monitoring.models.MonitoringEntry`

The MonitoringEntry model serves as the main container for Programs, Projects, and Activities (PPAs) from Ministries, Offices, and Agencies (MOAs).

### Key Fields for Budget Tracking

#### Budget Fields
```python
budget_allocation = DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    # Primary budget allocation for the PPA
    # Example: ₱149,772,172.00

budget_currency = CharField(max_length=10, default="PHP")
    # Currency code (default: PHP)

budget_obc_allocation = DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    # Portion specifically for OBC communities

budget_ceiling = DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    # Maximum budget ceiling for validation

fiscal_year = PositiveIntegerField(null=True, blank=True)
    # Fiscal year (2000-2100)
    # Example: 2025

plan_year = PositiveIntegerField(null=True, blank=True)
    # Planning reference year (AIP year)
```

#### WorkItem Integration Fields
```python
execution_project = OneToOneField('common.WorkItem', null=True, blank=True)
    # Root WorkItem for execution tracking

enable_workitem_tracking = BooleanField(default=False)
    # Toggle for WorkItem-based tracking

budget_distribution_policy = CharField(max_length=20, choices=[...], blank=True)
    # How to distribute budget: 'equal', 'weighted', 'manual'

auto_sync_progress = BooleanField(default=True)
    # Sync progress from WorkItems

auto_sync_status = BooleanField(default=True)
    # Sync status from WorkItems
```

#### Organizational Fields
```python
implementing_moa = ForeignKey('coordination.Organization', ...)
    # Primary MOA implementing the project

lead_organization = ForeignKey('coordination.Organization', ...)
    # Lead organization (may be same as implementing_moa)
```

#### Status and Workflow Fields
```python
category = CharField(max_length=20, choices=CATEGORY_CHOICES)
    # Options: 'moa_ppa', 'oobc_ppa', 'obc_request'

status = CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    # Options: 'planning', 'ongoing', 'completed', 'on_hold', 'cancelled'

priority = CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    # Options: 'low', 'medium', 'high', 'urgent'

progress = PositiveIntegerField(default=0, validators=[0-100])
    # Overall completion percentage

approval_status = CharField(max_length=30, choices=APPROVAL_STATUS_CHOICES, default='draft')
    # Workflow: 'draft', 'technical_review', 'budget_review',
    #           'stakeholder_consultation', 'executive_approval',
    #           'approved', 'enacted', 'rejected'
```

### Example PPA Data

```python
{
    'id': '89174a2a-7d21-45d3-9c5d-a9f0cbfdd7a9',
    'title': 'Promulgation of Religious Edicts',
    'category': 'moa_ppa',
    'budget_allocation': Decimal('149772172.00'),
    'budget_currency': 'PHP',
    'fiscal_year': 2025,
    'implementing_moa': 'Bangsamoro Darul-Ifta'',
    'lead_organization': 'Bangsamoro Darul-Ifta'',
    'status': 'planning',
    'priority': 'medium',
    'progress': 0,
    'enable_workitem_tracking': True,
    'execution_project': <WorkItem object>
}
```

---

## 2. WorkItem Model

### Model: `common.work_item_model.WorkItem`

Unified hierarchical work management using Django MPTT (Modified Preorder Tree Traversal).

### Work Types Hierarchy

```
Project                    # Top-level execution plan
├── Sub-Project           # Major sub-divisions
│   ├── Activity          # Specific activities/events
│   │   ├── Sub-Activity  # Activity breakdowns
│   │   │   └── Task      # Concrete tasks
│   │   │       └── Subtask  # Task breakdowns (up to 5 levels)
│   │   └── Task
│   └── Activity
└── Task
```

### Budget Fields

```python
allocated_budget = DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    # Budget allocated to this work item (PHP)
    # Can be distributed from parent PPA

actual_expenditure = DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    # Actual expenditure recorded (PHP)
    # Updated as work progresses

budget_notes = TextField(blank=True)
    # Budget-related notes and explanations
```

### PPA Relationship Fields

```python
related_ppa = ForeignKey('monitoring.MonitoringEntry', null=True, blank=True)
    # Direct link to parent PPA

ppa_category = CharField(max_length=20, null=True, blank=True, db_index=True)
    # Denormalized category from PPA for performance
    # Options: 'moa_ppa', 'oobc_ppa', 'obc_request'

implementing_moa = ForeignKey('coordination.Organization', null=True, blank=True)
    # Denormalized implementing MOA from PPA
    # Used for efficient filtering/RBAC
```

### Status and Progress Fields

```python
work_type = CharField(max_length=20, choices=WORK_TYPE_CHOICES)
    # 'project', 'sub_project', 'activity', 'sub_activity', 'task', 'subtask'

status = CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    # 'not_started', 'in_progress', 'at_risk', 'blocked', 'completed', 'cancelled'

priority = CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    # 'low', 'medium', 'high', 'urgent', 'critical'

progress = PositiveSmallIntegerField(default=0, validators=[0-100])
    # Progress percentage

auto_calculate_progress = BooleanField(default=True)
    # Auto-calculate from children
```

### Hierarchy Fields (MPTT)

```python
parent = TreeForeignKey('self', null=True, blank=True, on_delete=CASCADE)
    # Parent work item (null for root)

# MPTT auto-generated fields:
lft, rght, tree_id, level
    # Used for efficient tree queries
```

### Example WorkItem Data (Execution Project)

```python
{
    'id': '4e36bd95-9b9a-4fc0-bee8-b8a9ad5c3209',
    'work_type': 'project',
    'title': 'Promulgation of Religious Edicts - Execution Plan',
    'description': 'Execution tracking for MOA Project / Program / Activity: Promulgation of Religious Edicts',
    'status': 'not_started',
    'priority': 'medium',
    'progress': 0,
    'allocated_budget': Decimal('149772172.00'),
    'actual_expenditure': None,
    'related_ppa': <MonitoringEntry: Promulgation of Religious Edicts>,
    'ppa_category': 'moa_ppa',
    'implementing_moa': <Organization: Bangsamoro Darul-Ifta'>,
    'parent': None,  # Root item
    'auto_calculate_progress': True,
    'is_calendar_visible': True,
    'project_data': {
        'monitoring_entry_id': '89174a2a-7d21-45d3-9c5d-a9f0cbfdd7a9',
        'structure_template': 'program',
        'budget_allocation': '149772172.00',
        'fiscal_year': 2025
    }
}
```

---

## 3. Budget Tracking Integration

### How PPAs and WorkItems Connect

1. **PPA Creation** → MonitoringEntry with budget_allocation
2. **Enable Tracking** → `enable_workitem_tracking = True`
3. **Create Execution Project** → Root WorkItem linked via `execution_project`
4. **Budget Distribution** → Budget flows from PPA to WorkItem hierarchy

### Budget Flow

```
MonitoringEntry (PPA)
    budget_allocation: ₱149,772,172.00
        ↓
    execution_project (WorkItem - Project)
        allocated_budget: ₱149,772,172.00
            ↓
        Children (Activities/Tasks)
            allocated_budget: distributed portions
                ↓
            actual_expenditure: tracked as work progresses
```

### Budget Validation

The MonitoringEntry model includes validation:
```python
def validate_budget_distribution(self):
    """Validate sum of child budgets equals PPA budget."""
    # Ensures child WorkItems don't exceed parent budget
    # Tolerance: ±₱0.01
```

---

## 4. Required Fields for Creation

### Creating a MonitoringEntry (PPA)

**Minimum Required:**
```python
MonitoringEntry.objects.create(
    title="Program Name",                    # Required
    category="moa_ppa",                      # Required
    # All other fields are optional with defaults
)
```

**Recommended for Budget Tracking:**
```python
MonitoringEntry.objects.create(
    title="Program Name",
    category="moa_ppa",
    implementing_moa=<Organization object>,   # Required for moa_ppa
    budget_allocation=Decimal("100000.00"),
    fiscal_year=2025,
    status="planning",
    priority="medium",
    enable_workitem_tracking=True,
)
```

### Creating a WorkItem

**Minimum Required:**
```python
WorkItem.objects.create(
    work_type="project",                     # Required
    title="Work Item Title",                 # Required
    # All other fields have defaults
)
```

**Recommended for Budget Tracking:**
```python
WorkItem.objects.create(
    work_type="project",
    title="Execution Plan",
    description="Detailed description",
    status="not_started",
    priority="medium",
    related_ppa=<MonitoringEntry object>,
    allocated_budget=Decimal("100000.00"),
    actual_expenditure=Decimal("0.00"),
    parent=None,  # or parent WorkItem
    auto_calculate_progress=True,
)
```

---

## 5. Current Database State

### PPA Distribution

| Category | Count |
|----------|-------|
| moa_ppa  | 209   |
| **TOTAL** | **209** |

**Note:** All current PPAs are `moa_ppa` (MOA Projects/Programs/Activities). No `oobc_ppa` or `obc_request` entries exist yet.

### WorkItem Distribution

| Work Type | Count |
|-----------|-------|
| project   | 11    |
| activity  | 5     |
| task      | 4     |
| subtask   | 2     |
| **TOTAL** | **22** |

**Status Distribution:**
- All 22 WorkItems are `not_started`

**Budget Status:**
- 4 WorkItems have `allocated_budget` set (all are execution project roots)
- 0 WorkItems have `actual_expenditure` set
- 11 WorkItems are linked to PPAs via `related_ppa`

### PPAs with WorkItem Tracking

**4 PPAs** have execution projects enabled:

1. **Promulgation of Religious Edicts**
   - Budget: ₱149,772,172.00
   - MOA: Bangsamoro Darul-Ifta'
   - Execution Project: 1 child activity

2. **Harmonization of Bangsamoro Agenda on ICT**
   - Budget: ₱64,594,584.00
   - MOA: Bangsamoro ICT Office
   - Execution Project: 1 child activity

3. **BAGO Legal Services**
   - Budget: ₱34,001,249.00
   - MOA: Bangsamoro Attorney-General's Office
   - Execution Project: 1 child

4. **Promotional and Investment Services**
   - Budget: ₱15,149,922.00
   - Execution Project: with children

---

## 6. Test Data Requirements

### For Comprehensive Testing

To test the budget tracking system comprehensively, we need:

1. **Multiple PPAs** with varying budget sizes
   - Small (< ₱1M)
   - Medium (₱1M - ₱50M)
   - Large (> ₱50M)

2. **WorkItem Hierarchies** with budget distribution
   - Project → Activities → Tasks → Subtasks
   - Budget allocated at different levels
   - Some with expenditures recorded

3. **Different Budget Distribution Policies**
   - Equal distribution
   - Weighted distribution
   - Manual distribution

4. **Various Status Combinations**
   - PPAs: planning, ongoing, completed
   - WorkItems: not_started, in_progress, completed
   - Mixed statuses in hierarchy

5. **Budget Tracking Scenarios**
   - Under budget (expenditure < allocated)
   - At budget (expenditure ≈ allocated)
   - Over budget (expenditure > allocated)
   - No expenditure yet

6. **Different Fiscal Years**
   - Current year (2025)
   - Past years (2024, 2023)
   - Future years (2026)

---

## 7. Key Insights for Test Data Creation

### Budget Precision
- Use `Decimal` type, not `float`
- 14 digits total, 2 decimal places
- Currency is always PHP

### Hierarchy Constraints
- Projects can contain any type
- Activities can contain sub-activities, tasks, subtasks
- Tasks can contain subtasks
- Subtasks can nest up to 5 levels deep

### MPTT Considerations
- Use `.get_children()` for immediate children
- Use `.get_descendants()` for entire subtree
- Tree structure is auto-maintained

### Performance Optimization
- `ppa_category` and `implementing_moa` are denormalized for filtering
- Indexed fields: work_type, status, priority, related_ppa

### Budget Validation
- Child budgets should sum to parent budget (±₱0.01 tolerance)
- `budget_allocation` (PPA) → `allocated_budget` (WorkItem)
- Validation method: `validate_budget_distribution()`

---

## 8. Next Steps

### Recommended Actions

1. **Create Test PPAs**
   - Create 10-15 PPAs with varying budgets
   - Different fiscal years
   - Different MOAs
   - Different approval statuses

2. **Create WorkItem Hierarchies**
   - Enable tracking on test PPAs
   - Create 2-3 level hierarchies
   - Distribute budgets across children
   - Add some expenditure data

3. **Test Budget Distribution**
   - Test equal distribution
   - Test weighted distribution
   - Test manual distribution
   - Verify validation works

4. **Test Budget Tracking Views**
   - Verify budget allocation tree display
   - Test variance calculations
   - Test progress sync
   - Test status sync

---

## Appendix: Sample Data Queries

### Get All PPAs with Budget
```python
from monitoring.models import MonitoringEntry

ppas = MonitoringEntry.objects.filter(
    budget_allocation__isnull=False
).select_related('implementing_moa', 'lead_organization')

for ppa in ppas:
    print(f"{ppa.title}: ₱{ppa.budget_allocation:,.2f}")
```

### Get WorkItems with Budget in Hierarchy
```python
from common.work_item_model import WorkItem

# Get execution projects
projects = WorkItem.objects.filter(
    work_type='project',
    allocated_budget__isnull=False
)

for project in projects:
    descendants = project.get_descendants(include_self=True)
    total_allocated = sum(d.allocated_budget or 0 for d in descendants)
    print(f"{project.title}: ₱{total_allocated:,.2f}")
```

### Get Budget Utilization
```python
from common.work_item_model import WorkItem

work_items = WorkItem.objects.filter(
    allocated_budget__isnull=False
).prefetch_related('related_ppa')

for wi in work_items:
    allocated = wi.allocated_budget or 0
    actual = wi.actual_expenditure or 0
    variance = actual - allocated
    pct = (variance / allocated * 100) if allocated else 0

    print(f"{wi.title}:")
    print(f"  Allocated: ₱{allocated:,.2f}")
    print(f"  Actual: ₱{actual:,.2f}")
    print(f"  Variance: ₱{variance:,.2f} ({pct:+.1f}%)")
```

---

**End of Analysis**
