# MOA PPA Integration with WorkItem Hierarchy: Technical Architecture

**Document Type**: Technical Architecture Design
**Date**: 2025-10-05
**Status**: DRAFT - Architectural Specification
**Scope**: MonitoringEntry (MOA PPAs) → WorkItem Integration
**Author**: OBCMS System Architect

**Key Stakeholder Agencies**:
- **BPDA (Bangsamoro Planning and Development Authority)**: Chief planning agency; certifies PPA alignment with Bangsamoro Development Plan
- **MFBM (Ministry of Finance, Budget and Management)**: Budget formulation, execution, and fiscal policy; reviews budget allocations
- **BICTO (Bangsamoro Information and Communications Technology Office)**: ICT infrastructure, e-governance systems, technical implementation
- **MOAs/OOBC**: Implementing agencies for PPAs

---

## Executive Summary

### Current State

**MonitoringEntry (MOA PPAs)** exists as a standalone M&E tracking system with:
- Budget allocation and funding flows (allocations, obligations, disbursements)
- Approval workflow (draft → technical review → budget review → executive approval → enacted)
- Budget ceiling enforcement via Project Management Portal integration
- NO hierarchical project structure (single-level PPAs)

**WorkItem** provides hierarchical work management with:
- MPTT-based hierarchy (Projects → Activities → Tasks)
- Progress tracking and calendar integration
- Generic FK for domain relationships
- NO budget tracking at work item level

**The Gap**: PPAs lack decomposition into activities/tasks, while WorkItems lack budget/approval workflow.

### Architectural Verdict

**HYBRID INTEGRATION**: MonitoringEntry remains the "source of truth" for budget and approval, while WorkItem provides hierarchical execution tracking.

**Key Design Decisions**:
1. **MonitoringEntry = Project-Level Container** - Each PPA maps to a top-level WorkItem (work_type='project')
2. **WorkItem Hierarchy = Execution WBS** - Activities and tasks beneath PPA project inherit budget context
3. **Budget Distribution = Work Package Model** - Introduce lightweight budget allocation at task level
4. **Approval Workflow = MonitoringEntry Only** - No duplication in WorkItem
5. **Integration = Explicit Foreign Key** - Replace Generic FK with direct MonitoringEntry → WorkItem relationship

**Alignment Score Target**: 85/100 (from current 65/100 for WorkItem-only, 40/100 for MonitoringEntry-only)

---

## 1. Data Model Integration Architecture

### 1.1 Conceptual Model: PPA → Project → Activity → Task

```
┌─────────────────────────────────────────────────────────────────────┐
│ MonitoringEntry (PPA)                                               │
│ - Budget Allocation: PHP 5,000,000                                  │
│ - Approval Status: approved                                         │
│ - Fiscal Year: 2025                                                 │
│ - Sector: social                                                    │
│ - Implementing MOA: MSSD                                            │
└──────────────────┬──────────────────────────────────────────────────┘
                   │ 1:1 relationship
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ WorkItem (Project)                                                  │
│ - work_type: 'project'                                              │
│ - title: "Livelihood Training Program for OBCs"                     │
│ - related_ppa: FK → MonitoringEntry                                 │
│ - progress: Auto-calculated from children (0-100%)                  │
└──────────────────┬──────────────────────────────────────────────────┘
                   │ parent-child (MPTT)
                   ├─────────────────┬─────────────────┬──────────────
                   ▼                 ▼                 ▼
          ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
          │ WorkItem       │  │ WorkItem       │  │ WorkItem       │
          │ (Activity)     │  │ (Activity)     │  │ (Activity)     │
          │                │  │                │  │                │
          │ "Workshop in   │  │ "Field Visit   │  │ "Consultation  │
          │  Cotabato"     │  │  in Zamboanga" │  │  in Davao"     │
          │                │  │                │  │                │
          │ Budget: 1.5M   │  │ Budget: 2.0M   │  │ Budget: 1.5M   │
          └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
                   │                   │                   │
             ┌─────┴────┐        ┌─────┴────┐        ┌─────┴────┐
             ▼          ▼        ▼          ▼        ▼          ▼
        ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
        │Task:   │ │Task:   │ │Task:   │ │Task:   │ │Task:   │ │Task:   │
        │Prepare │ │Conduct │ │Travel  │ │Site    │ │Schedule│ │Prepare │
        │Venue   │ │Training│ │Arrange │ │Visit   │ │Meeting │ │Report  │
        │        │ │        │ │        │ │        │ │        │ │        │
        │Budget: │ │Budget: │ │Budget: │ │Budget: │ │Budget: │ │Budget: │
        │300K    │ │1.2M    │ │500K    │ │1.5M    │ │200K    │ │1.3M    │
        └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

**Budget Rollup Flow**:
```
Task Level:         PHP 300K + 1.2M + 500K + 1.5M + 200K + 1.3M = 5M
Activity Level:     Cotabato (1.5M) + Zamboanga (2.0M) + Davao (1.5M) = 5M
Project Level:      WorkItem project (inherits from PPA)
PPA Level:          MonitoringEntry.budget_allocation = 5M (source of truth)
```

---

### 1.2 Database Schema Changes

#### 1.2.1 MonitoringEntry Model (Minimal Changes)

**Current State**: Already has comprehensive budget tracking.

**Proposed Addition**:

```python
# src/monitoring/models.py

class MonitoringEntry(models.Model):
    # ... existing fields (622 lines of existing implementation) ...

    # ========== WORKITEM INTEGRATION (NEW) ==========

    # Explicit relationship to project-level WorkItem
    execution_project = models.OneToOneField(
        'common.WorkItem',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='ppa_source',
        help_text="Project-level WorkItem for execution tracking (work_type must be 'project')"
    )

    # Budget distribution policy
    BUDGET_DISTRIBUTION_MANUAL = 'manual'
    BUDGET_DISTRIBUTION_EQUAL = 'equal'
    BUDGET_DISTRIBUTION_WEIGHTED = 'weighted'
    BUDGET_DISTRIBUTION_CHOICES = [
        (BUDGET_DISTRIBUTION_MANUAL, 'Manual Allocation'),
        (BUDGET_DISTRIBUTION_EQUAL, 'Equal Distribution'),
        (BUDGET_DISTRIBUTION_WEIGHTED, 'Weighted by Effort'),
    ]

    budget_distribution_policy = models.CharField(
        max_length=20,
        choices=BUDGET_DISTRIBUTION_CHOICES,
        default=BUDGET_DISTRIBUTION_MANUAL,
        help_text="How budget is distributed to work items"
    )

    # Execution tracking enablement
    enable_workitem_tracking = models.BooleanField(
        default=False,
        help_text="Enable hierarchical execution tracking via WorkItem"
    )

    # Auto-sync settings
    auto_sync_progress = models.BooleanField(
        default=True,
        help_text="Automatically sync progress from WorkItem hierarchy"
    )

    auto_sync_status = models.BooleanField(
        default=True,
        help_text="Automatically sync status based on WorkItem project status"
    )

    def clean(self):
        """Model validation."""
        super().clean()
        errors = {}

        # Existing validation... (lines 694-740)

        # NEW: Validate execution_project is actually a project
        if self.execution_project:
            if self.execution_project.work_type != 'project':
                errors['execution_project'] = (
                    'Execution project must have work_type="project"'
                )

            # Prevent circular reference
            if hasattr(self.execution_project, 'related_ppa'):
                if self.execution_project.related_ppa and self.execution_project.related_ppa != self:
                    errors['execution_project'] = (
                        'This WorkItem is already linked to another PPA'
                    )

        if errors:
            raise ValidationError(errors)

    def sync_progress_from_workitem(self):
        """
        Sync PPA progress from WorkItem hierarchy.

        Returns:
            int: Updated progress percentage
        """
        if not self.execution_project or not self.auto_sync_progress:
            return self.progress

        # Get progress from project (auto-calculated from children)
        project_progress = self.execution_project.calculate_progress_from_children()

        if project_progress != self.progress:
            self.progress = project_progress
            self.save(update_fields=['progress', 'updated_at'])

        return self.progress

    def sync_status_from_workitem(self):
        """
        Sync PPA status from WorkItem project status.

        Mapping:
        - WorkItem.not_started → MonitoringEntry.planning
        - WorkItem.in_progress → MonitoringEntry.ongoing
        - WorkItem.completed → MonitoringEntry.completed
        - WorkItem.at_risk → MonitoringEntry.ongoing (flag in notes)
        - WorkItem.blocked → MonitoringEntry.on_hold
        - WorkItem.cancelled → MonitoringEntry.cancelled
        """
        if not self.execution_project or not self.auto_sync_status:
            return self.status

        status_mapping = {
            'not_started': 'planning',
            'in_progress': 'ongoing',
            'at_risk': 'ongoing',  # Keep ongoing but flag
            'blocked': 'on_hold',
            'completed': 'completed',
            'cancelled': 'cancelled',
        }

        new_status = status_mapping.get(self.execution_project.status)

        if new_status and new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status', 'updated_at'])

        return self.status

    def get_budget_allocation_tree(self):
        """
        Get hierarchical budget allocation breakdown.

        Returns:
            dict: {
                'ppa_budget': Decimal,
                'allocated_to_workitems': Decimal,
                'unallocated': Decimal,
                'breakdown': [
                    {
                        'work_item_id': UUID,
                        'title': str,
                        'work_type': str,
                        'allocated_budget': Decimal,
                        'children': [...]
                    }
                ]
            }
        """
        if not self.execution_project:
            return {
                'ppa_budget': self.budget_allocation,
                'allocated_to_workitems': Decimal('0.00'),
                'unallocated': self.budget_allocation,
                'breakdown': []
            }

        # Delegate to service layer
        from monitoring.services.budget_distribution import BudgetDistributionService
        return BudgetDistributionService.get_allocation_tree(self)
```

**Migration Impact**: LOW - Optional FK, no data migration required initially.

---

#### 1.2.2 WorkItem Model (Enhanced Domain Relationships)

**Current State**: Generic FK only (lines 222-226 in work_item_model.py).

**Proposed Changes**:

```python
# src/common/work_item_model.py

class WorkItem(MPTTModel):
    # ... existing fields (lines 1-220) ...

    # ========== DOMAIN RELATIONSHIPS (ENHANCED) ==========

    # EXPLICIT FOREIGN KEYS (type-safe, indexed, reverse relationships)

    # PPA Relationship (NEW - PRIMARY INTEGRATION POINT)
    related_ppa = models.ForeignKey(
        'monitoring.MonitoringEntry',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='work_items',
        help_text="MOA/OOBC PPA this work item implements (for project-level items)"
    )

    # Assessment Relationship
    related_assessment = models.ForeignKey(
        'mana.Assessment',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='work_items',
        help_text="MANA Assessment this work item supports"
    )

    # Policy Relationship
    related_policy = models.ForeignKey(
        'policy_tracking.PolicyRecommendation',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='implementing_work_items',
        help_text="Policy recommendation this work item implements"
    )

    # Community Relationship
    related_community = models.ForeignKey(
        'communities.BarangayOBC',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='work_items',
        help_text="OBC community this work item serves"
    )

    # Generic FK (fallback for other relationships)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.UUIDField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    # ========== BUDGET TRACKING (NEW - LIGHTWEIGHT) ==========

    # Task-level budget allocation (optional)
    allocated_budget = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Budget allocated to this work item (for activities and tasks)"
    )

    # Actual expenditure tracking (optional)
    actual_expenditure = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        help_text="Actual expenditure recorded for this work item"
    )

    # Budget notes
    budget_notes = models.TextField(
        blank=True,
        help_text="Notes on budget allocation or spending"
    )

    # ... existing metadata fields (lines 228-231) ...

    def clean(self):
        """Model validation."""
        super().clean()  # Existing validation from lines 268-284

        # NEW: Validate PPA relationship rules
        if self.related_ppa:
            # Only top-level projects can link to PPAs
            if self.parent is not None:
                raise ValidationError({
                    'related_ppa': 'Only top-level projects can be linked to PPAs'
                })

            # Work type must be project
            if self.work_type not in [self.WORK_TYPE_PROJECT, self.WORK_TYPE_SUB_PROJECT]:
                raise ValidationError({
                    'related_ppa': 'Only projects can be linked to PPAs'
                })

            # Check if PPA already has a linked project
            if self.related_ppa.execution_project and self.related_ppa.execution_project != self:
                raise ValidationError({
                    'related_ppa': f'This PPA is already linked to project: {self.related_ppa.execution_project.title}'
                })

        # NEW: Validate budget allocation
        if self.allocated_budget is not None:
            # Must have a parent with budget context OR linked PPA
            if not self.parent and not self.related_ppa:
                raise ValidationError({
                    'allocated_budget': 'Budget allocation requires parent work item or linked PPA'
                })

            # Cannot exceed parent budget (if parent has budget)
            if self.parent and self.parent.allocated_budget:
                siblings_budget = self.parent.get_children().exclude(id=self.id).aggregate(
                    total=Sum('allocated_budget')
                )['total'] or Decimal('0.00')

                if siblings_budget + self.allocated_budget > self.parent.allocated_budget:
                    raise ValidationError({
                        'allocated_budget': (
                            f'Total allocation ({siblings_budget + self.allocated_budget:,.2f}) '
                            f'exceeds parent budget ({self.parent.allocated_budget:,.2f})'
                        )
                    })

    def get_ppa_source(self):
        """
        Get the source PPA for budget context.

        Traverses up the hierarchy to find the root project's linked PPA.

        Returns:
            MonitoringEntry or None
        """
        # Direct link
        if self.related_ppa:
            return self.related_ppa

        # Check root project
        root = self.get_root()
        if root and root.related_ppa:
            return root.related_ppa

        return None

    def get_allocated_budget_rollup(self):
        """
        Calculate total allocated budget including all descendants.

        Returns:
            Decimal: Sum of allocated_budget for self and all children
        """
        total = self.allocated_budget or Decimal('0.00')

        children_total = self.get_descendants().aggregate(
            total=Sum('allocated_budget')
        )['total'] or Decimal('0.00')

        return total + children_total

    def get_expenditure_rollup(self):
        """
        Calculate total actual expenditure including all descendants.

        Returns:
            Decimal: Sum of actual_expenditure for self and all children
        """
        total = self.actual_expenditure or Decimal('0.00')

        children_total = self.get_descendants().aggregate(
            total=Sum('actual_expenditure')
        )['total'] or Decimal('0.00')

        return total + children_total

    def get_budget_variance(self):
        """
        Calculate budget variance (allocated vs. actual).

        Returns:
            dict: {
                'allocated': Decimal,
                'actual': Decimal,
                'variance': Decimal,
                'variance_pct': float,
                'status': 'under_budget' | 'on_budget' | 'over_budget'
            }
        """
        allocated = self.get_allocated_budget_rollup()
        actual = self.get_expenditure_rollup()
        variance = allocated - actual

        if allocated == 0:
            variance_pct = 0.0
        else:
            variance_pct = float((variance / allocated) * 100)

        # Status determination
        if actual > allocated:
            status = 'over_budget'
        elif abs(variance_pct) <= 5:
            status = 'on_budget'
        else:
            status = 'under_budget'

        return {
            'allocated': allocated,
            'actual': actual,
            'variance': variance,
            'variance_pct': variance_pct,
            'status': status
        }
```

**Migration Impact**: MEDIUM - New FK fields (nullable, no data migration required), budget fields (optional).

---

#### 1.2.3 New Model: WorkItemBudgetAllocation (Optional, Future Enhancement)

**Purpose**: Explicit budget allocation records with audit trail (alternative to `allocated_budget` field).

**Complexity**: MEDIUM
**Priority**: LOW (can use simple `allocated_budget` field initially)

```python
# src/common/models/budget.py

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid

class WorkItemBudgetAllocation(models.Model):
    """
    Explicit budget allocation record for work items.

    Provides audit trail and allows multiple allocation tranches per work item.
    Alternative to WorkItem.allocated_budget field.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    work_item = models.ForeignKey(
        'common.WorkItem',
        on_delete=models.CASCADE,
        related_name='budget_allocations',
        help_text="Work item receiving budget allocation"
    )

    # Allocation Details
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Budget amount allocated"
    )

    allocation_type = models.CharField(
        max_length=20,
        choices=[
            ('initial', 'Initial Allocation'),
            ('supplement', 'Supplemental Allocation'),
            ('adjustment', 'Budget Adjustment'),
            ('reallocation', 'Reallocation from Other Item'),
        ],
        default='initial'
    )

    source_ppa = models.ForeignKey(
        'monitoring.MonitoringEntry',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='workitem_budget_allocations',
        help_text="Source PPA if allocation comes from PPA budget"
    )

    # Approval
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_workitem_budgets'
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    # Tracking
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_workitem_budgets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'common_work_item_budget_allocation'
        ordering = ['-created_at']
        verbose_name = 'Work Item Budget Allocation'
        verbose_name_plural = 'Work Item Budget Allocations'
        indexes = [
            models.Index(fields=['work_item', 'allocation_type']),
            models.Index(fields=['source_ppa', '-created_at']),
        ]

    def __str__(self):
        return f"{self.work_item.title}: PHP {self.amount:,.2f}"
```

**Decision**: Start with simple `WorkItem.allocated_budget` field. Introduce `WorkItemBudgetAllocation` only if audit trail requirements become critical.

---

## 2. Work Type Mapping: PPA Categories → WorkItem Types

### 2.1 PPA Category Classification

**MonitoringEntry.category** (lines 167-171 in monitoring/models.py):
```python
CATEGORY_CHOICES = [
    ("moa_ppa", "MOA Project / Program / Activity"),
    ("oobc_ppa", "OOBC Project / Program / Activity"),
    ("obc_request", "OBC Request or Proposal"),
]
```

### 2.2 Mapping Strategy

| PPA Category | WorkItem work_type | Rationale |
|--------------|-------------------|-----------|
| **moa_ppa** | `project` | MOA-led initiatives treated as projects in WorkItem hierarchy |
| **oobc_ppa** | `project` | OOBC-led initiatives also projects (may have sub-projects) |
| **obc_request** | `project` OR `task` | **Depends on scope**: Large requests → projects; Small requests → tasks under "OBC Requests Portfolio" |

### 2.3 Hierarchical Decomposition Rules

**Rule 1: Program-Level PPAs → Sub-Projects**

If a PPA represents a **program** (e.g., "OBC Livelihood Development Program FY2025"):
```
MonitoringEntry: "OBC Livelihood Development Program FY2025" (category=oobc_ppa)
    ↓ (1:1 via execution_project)
WorkItem: "OBC Livelihood Development Program FY2025" (work_type=project)
    ├─ WorkItem: "Component 1: Skills Training" (work_type=sub_project)
    │   ├─ WorkItem: "Workshop in Cotabato" (work_type=activity)
    │   └─ WorkItem: "Workshop in Zamboanga" (work_type=activity)
    ├─ WorkItem: "Component 2: Equipment Provision" (work_type=sub_project)
    │   └─ WorkItem: "Procurement Activity" (work_type=activity)
    └─ WorkItem: "Component 3: M&E" (work_type=sub_project)
        └─ WorkItem: "Quarterly Monitoring" (work_type=activity)
```

**Rule 2: Project-Level PPAs → Activities**

If a PPA represents a **discrete project** (e.g., "Halal Certification Workshop Cotabato City"):
```
MonitoringEntry: "Halal Certification Workshop Cotabato City" (category=moa_ppa)
    ↓ (1:1 via execution_project)
WorkItem: "Halal Certification Workshop Cotabato City" (work_type=project)
    ├─ WorkItem: "Pre-Workshop Preparation" (work_type=activity)
    │   ├─ WorkItem: "Venue Booking" (work_type=task)
    │   └─ WorkItem: "Participant Invitation" (work_type=task)
    ├─ WorkItem: "Workshop Conduct" (work_type=activity)
    │   ├─ WorkItem: "Registration" (work_type=task)
    │   ├─ WorkItem: "Training Sessions" (work_type=task)
    │   └─ WorkItem: "Certification" (work_type=task)
    └─ WorkItem: "Post-Workshop Follow-up" (work_type=activity)
        └─ WorkItem: "M&E Report" (work_type=task)
```

**Rule 3: Activity-Level PPAs → Tasks Only**

If a PPA represents a **single activity** (e.g., "Site Visit to OBC Community in Davao"):
```
MonitoringEntry: "Site Visit to OBC Community in Davao" (category=oobc_ppa)
    ↓ (1:1 via execution_project)
WorkItem: "Site Visit to OBC Community in Davao" (work_type=project)
    ├─ WorkItem: "Travel Arrangements" (work_type=task)
    ├─ WorkItem: "Conduct Site Visit" (work_type=task)
    ├─ WorkItem: "Document Findings" (work_type=task)
    └─ WorkItem: "Prepare Report" (work_type=task)
```

**Rule 4: OBC Requests → Task-Level Items (Optional Project Container)**

Small OBC requests (category=obc_request):
```
MonitoringEntry: "OBC Maranao Community Request: Mosque Repair" (category=obc_request)
    ↓ (1:1 via execution_project)
WorkItem: "Mosque Repair - Barangay Poblacion" (work_type=project)
    ├─ WorkItem: "Assessment and Costing" (work_type=task)
    ├─ WorkItem: "Procurement of Materials" (work_type=task)
    ├─ WorkItem: "Repair Work Supervision" (work_type=task)
    └─ WorkItem: "Completion Inspection" (work_type=task)
```

---

## 3. Budget Workflow Integration

### 3.1 Approval Workflow: MonitoringEntry as Single Source of Truth

**Current State**: MonitoringEntry has comprehensive approval workflow (lines 601-671).

**Design Decision**: **NO duplication in WorkItem**. WorkItem inherits approval context from linked PPA.

**Workflow Stages**:
```
MonitoringEntry.approval_status:
1. draft                        → WorkItem NOT CREATED YET (prepared by MOA/OOBC)
2. technical_review             → WorkItem can be created (planning phase)
                                   [Reviewed by: BPDA for BDP alignment, MOA technical staff]
3. budget_review                → WorkItem budget allocation locked
                                   [Reviewed by: MFBM budget analyst for fiscal compliance]
4. stakeholder_consultation     → WorkItem execution can start
5. executive_approval           → WorkItem active
6. approved                     → WorkItem fully authorized
7. enacted                      → WorkItem budget released
                                   [MFBM releases budget allocation]
8. rejected                     → WorkItem archived/cancelled
```

**Integration Points**:

```python
# src/monitoring/services/approval_workflow.py

class PPAApprovalService:
    """Service for managing PPA approval workflow with WorkItem integration."""

    @staticmethod
    def approve_technical_review(ppa: MonitoringEntry, user, comments=""):
        """
        Approve technical review stage.

        Typically performed by: BPDA (planning alignment) or relevant MOA technical staff
        Side effect: Enable WorkItem creation for execution planning.
        """
        from project_central.models import BudgetApprovalStage

        # Update approval stage (existing logic)
        stage = BudgetApprovalStage.objects.get(ppa=ppa, stage='technical_review')
        stage.approve(user, comments)

        # Update PPA approval status
        ppa.approval_status = MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW
        ppa.reviewed_by = user
        ppa.save()

        # NEW: Enable WorkItem tracking
        if not ppa.execution_project:
            # Auto-create project-level WorkItem
            from common.models import WorkItem
            from monitoring.services.workitem_generation import WorkItemGenerationService

            project = WorkItemGenerationService.create_project_from_ppa(ppa, created_by=user)
            ppa.execution_project = project
            ppa.enable_workitem_tracking = True
            ppa.save(update_fields=['execution_project', 'enable_workitem_tracking'])

    @staticmethod
    def approve_budget_review(ppa: MonitoringEntry, user, comments=""):
        """
        Approve budget review stage.

        Typically performed by: MFBM budget analyst
        Side effect: Lock WorkItem budget allocations.
        """
        # Update approval stage (existing logic)
        from project_central.models import BudgetApprovalStage
        stage = BudgetApprovalStage.objects.get(ppa=ppa, stage='budget_review')
        stage.approve(user, comments)

        # Update PPA
        ppa.approval_status = MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION
        ppa.budget_approved_by = user
        ppa.save()

        # NEW: Lock WorkItem budgets (prevent further allocation changes)
        if ppa.execution_project:
            from monitoring.services.budget_distribution import BudgetDistributionService
            BudgetDistributionService.lock_budget_allocations(ppa.execution_project)

    @staticmethod
    def enact_budget(ppa: MonitoringEntry, user, comments=""):
        """
        Enact budget (final approval).

        Side effect: Activate WorkItem project for execution.
        """
        # Update PPA
        ppa.approval_status = MonitoringEntry.APPROVAL_STATUS_ENACTED
        ppa.executive_approved_by = user
        ppa.save()

        # NEW: Activate WorkItem project
        if ppa.execution_project:
            ppa.execution_project.status = 'in_progress'
            ppa.execution_project.save(update_fields=['status', 'updated_at'])
```

### 3.2 Budget Distribution Service

**Purpose**: Distribute PPA budget across WorkItem hierarchy.

```python
# src/monitoring/services/budget_distribution.py

from decimal import Decimal
from typing import List, Dict
from django.db import transaction
from common.models import WorkItem
from monitoring.models import MonitoringEntry

class BudgetDistributionService:
    """Service for distributing PPA budgets across WorkItem hierarchy."""

    @staticmethod
    def distribute_budget_equally(ppa: MonitoringEntry):
        """
        Distribute PPA budget equally across top-level children.

        Example:
            PPA Budget: 5,000,000
            Children: 3 activities
            Allocation: 1,666,666.67 per activity
        """
        if not ppa.execution_project:
            raise ValueError("PPA must have execution_project to distribute budget")

        children = ppa.execution_project.get_children()
        count = children.count()

        if count == 0:
            return

        per_child = ppa.budget_allocation / count

        with transaction.atomic():
            for child in children:
                child.allocated_budget = per_child
                child.save(update_fields=['allocated_budget', 'updated_at'])

    @staticmethod
    def distribute_budget_weighted(ppa: MonitoringEntry, weights: Dict[str, Decimal]):
        """
        Distribute PPA budget using weighted allocation.

        Args:
            ppa: MonitoringEntry instance
            weights: {work_item_id: weight_factor}

        Example:
            PPA Budget: 5,000,000
            Weights: {
                'activity-1-id': Decimal('0.30'),  # 30% → 1,500,000
                'activity-2-id': Decimal('0.50'),  # 50% → 2,500,000
                'activity-3-id': Decimal('0.20'),  # 20% → 1,000,000
            }
        """
        if not ppa.execution_project:
            raise ValueError("PPA must have execution_project")

        # Validate weights sum to 1.0
        total_weight = sum(weights.values())
        if abs(total_weight - Decimal('1.00')) > Decimal('0.01'):
            raise ValueError(f"Weights must sum to 1.0 (got {total_weight})")

        with transaction.atomic():
            for work_item_id, weight in weights.items():
                work_item = WorkItem.objects.get(id=work_item_id)
                work_item.allocated_budget = ppa.budget_allocation * weight
                work_item.save(update_fields=['allocated_budget', 'updated_at'])

    @staticmethod
    def distribute_budget_manual(allocations: Dict[str, Decimal]):
        """
        Manually set budget allocations for work items.

        Args:
            allocations: {work_item_id: budget_amount}
        """
        with transaction.atomic():
            for work_item_id, amount in allocations.items():
                work_item = WorkItem.objects.get(id=work_item_id)
                work_item.allocated_budget = amount
                work_item.save(update_fields=['allocated_budget', 'updated_at'])

    @staticmethod
    def get_allocation_tree(ppa: MonitoringEntry) -> Dict:
        """
        Get hierarchical budget allocation tree.

        Returns:
            {
                'ppa_budget': Decimal,
                'allocated_to_workitems': Decimal,
                'unallocated': Decimal,
                'allocation_percentage': float,
                'breakdown': [
                    {
                        'work_item_id': UUID,
                        'title': str,
                        'work_type': str,
                        'level': int,
                        'allocated_budget': Decimal,
                        'actual_expenditure': Decimal,
                        'variance': Decimal,
                        'children': [...]
                    }
                ]
            }
        """
        if not ppa.execution_project:
            return {
                'ppa_budget': ppa.budget_allocation,
                'allocated_to_workitems': Decimal('0.00'),
                'unallocated': ppa.budget_allocation,
                'allocation_percentage': 0.0,
                'breakdown': []
            }

        def build_tree(work_item):
            """Recursively build allocation tree."""
            children_data = []
            for child in work_item.get_children():
                children_data.append(build_tree(child))

            variance = work_item.get_budget_variance()

            return {
                'work_item_id': str(work_item.id),
                'title': work_item.title,
                'work_type': work_item.work_type,
                'level': work_item.level,
                'allocated_budget': work_item.allocated_budget or Decimal('0.00'),
                'actual_expenditure': work_item.actual_expenditure or Decimal('0.00'),
                'variance': variance['variance'],
                'variance_pct': variance['variance_pct'],
                'children': children_data
            }

        tree = build_tree(ppa.execution_project)

        # Calculate totals
        total_allocated = ppa.execution_project.get_allocated_budget_rollup()
        unallocated = ppa.budget_allocation - total_allocated

        allocation_pct = float(
            (total_allocated / ppa.budget_allocation * 100)
            if ppa.budget_allocation > 0 else 0
        )

        return {
            'ppa_budget': ppa.budget_allocation,
            'allocated_to_workitems': total_allocated,
            'unallocated': unallocated,
            'allocation_percentage': allocation_pct,
            'breakdown': [tree]
        }

    @staticmethod
    def lock_budget_allocations(work_item: WorkItem):
        """
        Lock budget allocations after budget review approval.

        Implementation: Add metadata flag to prevent further changes.
        """
        # Store lock flag in project_data JSON
        if not work_item.project_data:
            work_item.project_data = {}

        work_item.project_data['budget_locked'] = True
        work_item.project_data['budget_locked_at'] = timezone.now().isoformat()
        work_item.save(update_fields=['project_data', 'updated_at'])

        # Lock all descendants
        for descendant in work_item.get_descendants():
            if not descendant.project_data:
                descendant.project_data = {}
            descendant.project_data['budget_locked'] = True
            descendant.save(update_fields=['project_data', 'updated_at'])
```

---

## 4. Hierarchical Structure Implementation

### 4.1 WorkItem Generation Service

**Purpose**: Auto-generate WorkItem hierarchy from PPA templates.

```python
# src/monitoring/services/workitem_generation.py

from common.models import WorkItem, User
from monitoring.models import MonitoringEntry
from django.db import transaction

class WorkItemGenerationService:
    """Service for generating WorkItem hierarchies from PPAs."""

    @staticmethod
    def create_project_from_ppa(ppa: MonitoringEntry, created_by: User = None) -> WorkItem:
        """
        Create a project-level WorkItem from PPA.

        Args:
            ppa: MonitoringEntry instance
            created_by: User creating the project

        Returns:
            WorkItem: Created project-level work item
        """
        # Map PPA dates to WorkItem
        start_date = ppa.start_date
        due_date = ppa.target_end_date

        # Map PPA status to WorkItem status
        status_mapping = {
            'planning': 'not_started',
            'ongoing': 'in_progress',
            'completed': 'completed',
            'on_hold': 'blocked',
            'cancelled': 'cancelled',
        }

        work_item_status = status_mapping.get(ppa.status, 'not_started')

        # Create project
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title=ppa.title,
            description=ppa.summary,
            status=work_item_status,
            priority=WorkItem.PRIORITY_MEDIUM,  # Map from ppa.priority if needed
            start_date=start_date,
            due_date=due_date,
            progress=ppa.progress,
            related_ppa=ppa,
            created_by=created_by,
            is_calendar_visible=True,
            calendar_color='#3B82F6',  # Blue for MOA PPAs
            auto_calculate_progress=True,
            # Store PPA-specific data in project_data JSON
            project_data={
                'ppa_category': ppa.category,
                'implementing_moa': str(ppa.implementing_moa_id) if ppa.implementing_moa else None,
                'sector': ppa.sector,
                'fiscal_year': ppa.fiscal_year,
                'approval_status': ppa.approval_status,
                'funding_source': ppa.funding_source,
            }
        )

        return project

    @staticmethod
    @transaction.atomic
    def generate_default_structure_program(ppa: MonitoringEntry, created_by: User = None) -> WorkItem:
        """
        Generate default WBS for program-level PPAs.

        Structure:
            Project
            ├─ Sub-Project: Planning & Design
            ├─ Sub-Project: Implementation
            └─ Sub-Project: Monitoring & Evaluation
        """
        project = WorkItemGenerationService.create_project_from_ppa(ppa, created_by)

        # Sub-project 1: Planning & Design
        planning = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUB_PROJECT,
            title="Planning & Design",
            parent=project,
            status='not_started',
            priority=WorkItem.PRIORITY_HIGH,
            created_by=created_by,
            description="Planning, design, and preparation phase"
        )

        # Sub-project 2: Implementation
        implementation = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUB_PROJECT,
            title="Implementation",
            parent=project,
            status='not_started',
            priority=WorkItem.PRIORITY_HIGH,
            created_by=created_by,
            description="Main implementation phase"
        )

        # Sub-project 3: M&E
        me = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_SUB_PROJECT,
            title="Monitoring & Evaluation",
            parent=project,
            status='not_started',
            priority=WorkItem.PRIORITY_MEDIUM,
            created_by=created_by,
            description="Monitoring, evaluation, and reporting"
        )

        # Distribute budget (example: 20% planning, 60% implementation, 20% M&E)
        if ppa.budget_allocation:
            planning.allocated_budget = ppa.budget_allocation * Decimal('0.20')
            implementation.allocated_budget = ppa.budget_allocation * Decimal('0.60')
            me.allocated_budget = ppa.budget_allocation * Decimal('0.20')

            planning.save(update_fields=['allocated_budget'])
            implementation.save(update_fields=['allocated_budget'])
            me.save(update_fields=['allocated_budget'])

        return project

    @staticmethod
    @transaction.atomic
    def generate_default_structure_activity(ppa: MonitoringEntry, created_by: User = None) -> WorkItem:
        """
        Generate default WBS for activity-level PPAs.

        Structure:
            Project
            ├─ Activity: Preparation
            ├─ Activity: Execution
            └─ Activity: Completion
        """
        project = WorkItemGenerationService.create_project_from_ppa(ppa, created_by)

        preparation = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Preparation",
            parent=project,
            status='not_started',
            created_by=created_by,
            description="Pre-activity preparation tasks"
        )

        execution = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Execution",
            parent=project,
            status='not_started',
            created_by=created_by,
            description="Main activity execution"
        )

        completion = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Completion & Reporting",
            parent=project,
            status='not_started',
            created_by=created_by,
            description="Post-activity completion and documentation"
        )

        # Distribute budget (example: 15% prep, 75% execution, 10% completion)
        if ppa.budget_allocation:
            preparation.allocated_budget = ppa.budget_allocation * Decimal('0.15')
            execution.allocated_budget = ppa.budget_allocation * Decimal('0.75')
            completion.allocated_budget = ppa.budget_allocation * Decimal('0.10')

            preparation.save(update_fields=['allocated_budget'])
            execution.save(update_fields=['allocated_budget'])
            completion.save(update_fields=['allocated_budget'])

        return project
```

---

## 5. Migration Strategy

### 5.1 Migration Phases

#### Phase 1: Database Schema Changes (PRIORITY: CRITICAL)

**Deliverables**:
1. Add `execution_project` FK to MonitoringEntry
2. Add budget tracking fields to WorkItem (`allocated_budget`, `actual_expenditure`)
3. Add explicit FKs to WorkItem (`related_ppa`, `related_assessment`, etc.)
4. Add PPA integration helper methods to both models

**Migration Script**:
```python
# src/monitoring/migrations/0018_add_workitem_integration.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('monitoring', '0017_add_model_validation_constraints'),
        ('common', '0020_workitem'),
    ]

    operations = [
        # Add execution_project FK to MonitoringEntry
        migrations.AddField(
            model_name='monitoringentry',
            name='execution_project',
            field=models.OneToOneField(
                blank=True,
                help_text='Project-level WorkItem for execution tracking',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='ppa_source',
                to='common.workitem'
            ),
        ),

        # Add budget distribution policy
        migrations.AddField(
            model_name='monitoringentry',
            name='budget_distribution_policy',
            field=models.CharField(
                choices=[
                    ('manual', 'Manual Allocation'),
                    ('equal', 'Equal Distribution'),
                    ('weighted', 'Weighted by Effort')
                ],
                default='manual',
                help_text='How budget is distributed to work items',
                max_length=20
            ),
        ),

        # Add WorkItem tracking flags
        migrations.AddField(
            model_name='monitoringentry',
            name='enable_workitem_tracking',
            field=models.BooleanField(
                default=False,
                help_text='Enable hierarchical execution tracking via WorkItem'
            ),
        ),

        migrations.AddField(
            model_name='monitoringentry',
            name='auto_sync_progress',
            field=models.BooleanField(
                default=True,
                help_text='Automatically sync progress from WorkItem hierarchy'
            ),
        ),

        migrations.AddField(
            model_name='monitoringentry',
            name='auto_sync_status',
            field=models.BooleanField(
                default=True,
                help_text='Automatically sync status based on WorkItem project status'
            ),
        ),
    ]
```

```python
# src/common/migrations/0021_workitem_budget_and_explicit_fks.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('common', '0020_workitem'),
        ('monitoring', '0018_add_workitem_integration'),
        ('mana', '0020_need_budget_inclusion_date_need_community_votes_and_more'),
        ('policy_tracking', '0007_policyrecommendation_target_barangay_and_more'),
        ('communities', '0028_clear_municipal_estimated_population'),
    ]

    operations = [
        # Add explicit domain FKs
        migrations.AddField(
            model_name='workitem',
            name='related_ppa',
            field=models.ForeignKey(
                blank=True,
                help_text='MOA/OOBC PPA this work item implements',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='work_items',
                to='monitoring.monitoringentry'
            ),
        ),

        migrations.AddField(
            model_name='workitem',
            name='related_assessment',
            field=models.ForeignKey(
                blank=True,
                help_text='MANA Assessment this work item supports',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='work_items',
                to='mana.assessment'
            ),
        ),

        migrations.AddField(
            model_name='workitem',
            name='related_policy',
            field=models.ForeignKey(
                blank=True,
                help_text='Policy recommendation this work item implements',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='implementing_work_items',
                to='policy_tracking.policyrecommendation'
            ),
        ),

        migrations.AddField(
            model_name='workitem',
            name='related_community',
            field=models.ForeignKey(
                blank=True,
                help_text='OBC community this work item serves',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='work_items',
                to='communities.barangayobc'
            ),
        ),

        # Add budget tracking fields
        migrations.AddField(
            model_name='workitem',
            name='allocated_budget',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Budget allocated to this work item',
                max_digits=14,
                null=True
            ),
        ),

        migrations.AddField(
            model_name='workitem',
            name='actual_expenditure',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                help_text='Actual expenditure recorded for this work item',
                max_digits=14,
                null=True
            ),
        ),

        migrations.AddField(
            model_name='workitem',
            name='budget_notes',
            field=models.TextField(
                blank=True,
                help_text='Notes on budget allocation or spending'
            ),
        ),

        # Add indexes for performance
        migrations.AddIndex(
            model_name='workitem',
            index=models.Index(fields=['related_ppa', 'work_type'], name='workitem_ppa_type_idx'),
        ),

        migrations.AddIndex(
            model_name='workitem',
            index=models.Index(fields=['allocated_budget', 'actual_expenditure'], name='workitem_budget_idx'),
        ),
    ]
```

**Testing Requirements**:
- Unit tests: Model validation (PPA → Project linkage rules)
- Integration tests: Create PPA → auto-generate WorkItem
- Performance tests: Budget rollup calculations on 100+ work items

---

#### Phase 2: Service Layer Implementation (PRIORITY: HIGH)

**Deliverables**:
1. `BudgetDistributionService` (budget allocation logic)
2. `WorkItemGenerationService` (auto-generate WBS from PPA)
3. `PPAApprovalService` (integrate approval workflow)

**Testing**:
```python
# src/monitoring/tests/test_workitem_integration.py

from decimal import Decimal
from django.test import TestCase
from monitoring.models import MonitoringEntry
from common.models import WorkItem, User
from monitoring.services.workitem_generation import WorkItemGenerationService
from monitoring.services.budget_distribution import BudgetDistributionService

class WorkItemIntegrationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_pm',
            password='test123',
            user_type='oobc_staff'
        )

        self.ppa = MonitoringEntry.objects.create(
            title="Livelihood Training Program FY2025",
            category='oobc_ppa',
            status='planning',
            budget_allocation=Decimal('5000000.00'),
            fiscal_year=2025,
            sector='social',
            created_by=self.user
        )

    def test_create_project_from_ppa(self):
        """Test auto-generation of project from PPA."""
        project = WorkItemGenerationService.create_project_from_ppa(
            self.ppa,
            created_by=self.user
        )

        self.assertEqual(project.work_type, WorkItem.WORK_TYPE_PROJECT)
        self.assertEqual(project.title, self.ppa.title)
        self.assertEqual(project.related_ppa, self.ppa)
        self.assertEqual(project.status, 'not_started')  # Mapped from 'planning'

    def test_bidirectional_linkage(self):
        """Test bidirectional PPA ↔ WorkItem linkage."""
        project = WorkItemGenerationService.create_project_from_ppa(self.ppa, self.user)

        self.ppa.execution_project = project
        self.ppa.save()

        # Forward: PPA → WorkItem
        self.assertEqual(self.ppa.execution_project, project)

        # Reverse: WorkItem → PPA
        self.assertEqual(project.related_ppa, self.ppa)

    def test_budget_distribution_equal(self):
        """Test equal budget distribution."""
        project = WorkItemGenerationService.generate_default_structure_program(
            self.ppa,
            created_by=self.user
        )

        # Should have 3 sub-projects
        children = project.get_children()
        self.assertEqual(children.count(), 3)

        # Total allocated should equal PPA budget
        total_allocated = sum(
            child.allocated_budget for child in children
        )
        self.assertEqual(total_allocated, self.ppa.budget_allocation)

    def test_budget_rollup_calculation(self):
        """Test budget rollup from children."""
        project = WorkItemGenerationService.generate_default_structure_activity(
            self.ppa,
            created_by=self.user
        )

        rollup = project.get_allocated_budget_rollup()

        # Rollup should equal sum of children's budgets
        self.assertEqual(rollup, self.ppa.budget_allocation)

    def test_progress_sync_from_workitem(self):
        """Test progress sync from WorkItem → PPA."""
        project = WorkItemGenerationService.create_project_from_ppa(self.ppa, self.user)
        self.ppa.execution_project = project
        self.ppa.auto_sync_progress = True
        self.ppa.save()

        # Create activities
        activity1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            parent=project,
            status='completed'
        )
        activity2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 2",
            parent=project,
            status='in_progress'
        )

        # Sync progress
        project.update_progress()  # Should be 50% (1/2 completed)
        new_progress = self.ppa.sync_progress_from_workitem()

        self.assertEqual(new_progress, 50)
        self.assertEqual(self.ppa.progress, 50)
```

---

#### Phase 3: UI Integration (PRIORITY: MEDIUM)

**Deliverables**:
1. PPA detail page: "Enable Execution Tracking" button
2. WorkItem hierarchy view integrated into PPA detail
3. Budget allocation UI (visual tree with drag-drop budget distribution)
4. Budget variance dashboard widget

**UI Mockup** (PPA Detail Page Enhancement):
```html
<!-- src/templates/monitoring/detail.html -->

<!-- Existing PPA details... -->

{% if entry.enable_workitem_tracking %}
    <!-- WorkItem Hierarchy Section -->
    <div class="mt-8">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold text-gray-900">
                Execution Tracking
            </h3>
            <a href="{% url 'work_items:project_detail' entry.execution_project.id %}"
               class="text-blue-600 hover:text-blue-800">
                View Full Project
            </a>
        </div>

        <!-- Budget Allocation Tree -->
        <div class="bg-white border rounded-xl p-6 mb-6">
            <h4 class="text-lg font-medium mb-4">Budget Allocation</h4>

            <div class="mb-4">
                <div class="flex justify-between text-sm mb-2">
                    <span class="text-gray-600">Total PPA Budget</span>
                    <span class="font-semibold">₱{{ entry.budget_allocation|floatformat:2 }}</span>
                </div>
                <div class="flex justify-between text-sm mb-2">
                    <span class="text-gray-600">Allocated to Activities</span>
                    <span class="font-semibold text-blue-600">
                        ₱{{ budget_tree.allocated_to_workitems|floatformat:2 }}
                    </span>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-gray-600">Unallocated</span>
                    <span class="font-semibold text-orange-600">
                        ₱{{ budget_tree.unallocated|floatformat:2 }}
                    </span>
                </div>

                <!-- Progress bar -->
                <div class="w-full bg-gray-200 rounded-full h-2 mt-3">
                    <div class="bg-blue-600 h-2 rounded-full"
                         style="width: {{ budget_tree.allocation_percentage }}%">
                    </div>
                </div>
                <p class="text-xs text-gray-500 mt-1">
                    {{ budget_tree.allocation_percentage|floatformat:1 }}% allocated
                </p>
            </div>

            <!-- Hierarchical breakdown -->
            <div class="mt-6">
                {% include "monitoring/partials/budget_tree_node.html" with node=budget_tree.breakdown.0 %}
            </div>
        </div>

        <!-- WorkItem Progress Overview -->
        <div class="grid grid-cols-3 gap-4">
            <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div class="text-sm text-blue-600 font-medium">Total Tasks</div>
                <div class="text-2xl font-bold text-blue-900 mt-1">
                    {{ execution_stats.total_tasks }}
                </div>
            </div>
            <div class="bg-green-50 border border-green-200 rounded-xl p-4">
                <div class="text-sm text-green-600 font-medium">Completed</div>
                <div class="text-2xl font-bold text-green-900 mt-1">
                    {{ execution_stats.completed_tasks }}
                </div>
            </div>
            <div class="bg-orange-50 border border-orange-200 rounded-xl p-4">
                <div class="text-sm text-orange-600 font-medium">In Progress</div>
                <div class="text-2xl font-bold text-orange-900 mt-1">
                    {{ execution_stats.in_progress_tasks }}
                </div>
            </div>
        </div>
    </div>
{% else %}
    <!-- Enable Tracking Button -->
    <div class="mt-8 bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl p-8 text-center">
        <i class="fas fa-project-diagram text-4xl text-gray-400 mb-4"></i>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">
            Enable Execution Tracking
        </h3>
        <p class="text-gray-600 mb-6 max-w-md mx-auto">
            Break down this PPA into activities and tasks for detailed execution tracking and budget management.
        </p>

        <form method="post" action="{% url 'monitoring:enable_workitem_tracking' entry.id %}">
            {% csrf_token %}
            <button type="submit"
                    class="px-6 py-3 bg-gradient-to-r from-blue-600 to-teal-600 text-white rounded-xl hover:shadow-lg transition">
                <i class="fas fa-check-circle mr-2"></i>
                Enable Execution Tracking
            </button>
        </form>
    </div>
{% endif %}
```

---

## 6. API Integration Points

### 6.1 REST API Endpoints

```python
# src/monitoring/api_urls.py

from rest_framework.routers import DefaultRouter
from monitoring.api_views import MonitoringEntryViewSet

router = DefaultRouter()
router.register(r'monitoring-entries', MonitoringEntryViewSet, basename='monitoringentry')

urlpatterns = router.urls
```

```python
# src/monitoring/api_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from monitoring.models import MonitoringEntry
from monitoring.serializers import MonitoringEntryDetailSerializer
from monitoring.services.workitem_generation import WorkItemGenerationService
from monitoring.services.budget_distribution import BudgetDistributionService

class MonitoringEntryViewSet(viewsets.ModelViewSet):
    queryset = MonitoringEntry.objects.all()
    serializer_class = MonitoringEntryDetailSerializer

    @action(detail=True, methods=['post'])
    def enable_workitem_tracking(self, request, pk=None):
        """
        Enable WorkItem execution tracking for this PPA.

        POST /api/monitoring-entries/{id}/enable_workitem_tracking/
        {
            "structure_template": "program" | "activity" | "minimal"
        }
        """
        ppa = self.get_object()

        if ppa.enable_workitem_tracking:
            return Response(
                {'error': 'WorkItem tracking already enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        structure_template = request.data.get('structure_template', 'activity')

        if structure_template == 'program':
            project = WorkItemGenerationService.generate_default_structure_program(
                ppa,
                created_by=request.user
            )
        elif structure_template == 'activity':
            project = WorkItemGenerationService.generate_default_structure_activity(
                ppa,
                created_by=request.user
            )
        else:
            project = WorkItemGenerationService.create_project_from_ppa(
                ppa,
                created_by=request.user
            )

        ppa.execution_project = project
        ppa.enable_workitem_tracking = True
        ppa.save()

        return Response({
            'message': 'WorkItem tracking enabled',
            'execution_project_id': str(project.id),
            'structure_template': structure_template
        })

    @action(detail=True, methods=['get'])
    def budget_allocation_tree(self, request, pk=None):
        """
        Get hierarchical budget allocation breakdown.

        GET /api/monitoring-entries/{id}/budget_allocation_tree/
        """
        ppa = self.get_object()
        tree = BudgetDistributionService.get_allocation_tree(ppa)
        return Response(tree)

    @action(detail=True, methods=['post'])
    def distribute_budget(self, request, pk=None):
        """
        Distribute PPA budget across WorkItem hierarchy.

        POST /api/monitoring-entries/{id}/distribute_budget/
        {
            "method": "equal" | "weighted" | "manual",
            "weights": {"work-item-id": 0.30, ...},  // For weighted
            "allocations": {"work-item-id": 1500000.00, ...}  // For manual
        }
        """
        ppa = self.get_object()
        method = request.data.get('method', 'equal')

        if method == 'equal':
            BudgetDistributionService.distribute_budget_equally(ppa)
        elif method == 'weighted':
            weights = request.data.get('weights', {})
            BudgetDistributionService.distribute_budget_weighted(ppa, weights)
        elif method == 'manual':
            allocations = request.data.get('allocations', {})
            BudgetDistributionService.distribute_budget_manual(allocations)
        else:
            return Response(
                {'error': 'Invalid method. Use: equal, weighted, or manual'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Return updated allocation tree
        tree = BudgetDistributionService.get_allocation_tree(ppa)
        return Response(tree)

    @action(detail=True, methods=['post'])
    def sync_from_workitem(self, request, pk=None):
        """
        Manually trigger progress/status sync from WorkItem.

        POST /api/monitoring-entries/{id}/sync_from_workitem/
        """
        ppa = self.get_object()

        if not ppa.execution_project:
            return Response(
                {'error': 'No execution project linked'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_progress = ppa.sync_progress_from_workitem()
        new_status = ppa.sync_status_from_workitem()

        return Response({
            'progress': new_progress,
            'status': new_status,
            'message': 'Sync completed'
        })
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

**Coverage Targets**:
- MonitoringEntry methods: 90% coverage
- WorkItem PPA integration: 90% coverage
- Service layer: 95% coverage

**Test Suite**:
```python
# src/monitoring/tests/test_ppa_workitem_integration.py
# src/common/tests/test_workitem_budget_tracking.py
# src/monitoring/tests/test_budget_distribution_service.py
```

### 7.2 Integration Tests

**Scenarios**:
1. Create PPA → Enable WorkItem tracking → Distribute budget → Sync progress
2. Approval workflow triggers WorkItem activation
3. WorkItem status changes sync back to PPA
4. Budget ceiling enforcement with WorkItem allocations

### 7.3 Performance Tests

**Benchmarks**:
- Budget rollup calculation: < 100ms for hierarchy with 100 work items
- Progress sync: < 50ms
- Budget allocation tree API: < 200ms

---

## 8. Deployment Checklist

**Pre-Deployment**:
- [ ] Run migrations on staging environment
- [ ] Verify no data loss in MonitoringEntry
- [ ] Test PPA → WorkItem generation with real data
- [ ] Validate budget rollup calculations
- [ ] Performance test with production data size
- [ ] BICTO infrastructure review (server capacity, database optimization, security)

**Post-Deployment**:
- [ ] Monitor Celery tasks for sync operations
- [ ] Check database query performance (slow query log)
- [ ] Validate API response times
- [ ] User acceptance testing with OOBC staff
- [ ] BICTO monitoring of system performance and security compliance

---

## 9. Future Enhancements (Post-MVP)

**PRIORITY: LOW | COMPLEXITY: Complex**

### 9.1 Earned Value Management (EVM)

**PREREQUISITES**: Budget tracking stable, WorkPackage model implemented

**Features**:
- Planned Value (PV) calculation from baseline
- Earned Value (EV) from progress * budget
- Actual Cost (AC) tracking integration
- SPI/CPI metrics dashboard

**See**: `/docs/research/WORKITEM_ARCHITECTURAL_ASSESSMENT.md` Section 3.2

### 9.2 Resource Allocation at Work Item Level

**PREREQUISITES**: ResourceProfile, ResourceAssignment models

**Features**:
- Assign staff to specific activities/tasks with hourly allocations
- Resource utilization tracking
- Cost rollup from hourly rates

**See**: `/docs/research/WORKITEM_ARCHITECTURAL_ASSESSMENT.md` Section 3.3

### 9.3 Critical Path Analysis

**PREREQUISITES**: WorkItemDependency model

**Features**:
- Define dependencies between activities/tasks
- Auto-calculate critical path
- Schedule variance alerts

**See**: `/docs/research/WORKITEM_ARCHITECTURAL_ASSESSMENT.md` Section 3.5

---

## 10. Conclusion

### 10.1 Architectural Summary

**Integration Model**: **HYBRID - Source of Truth Separation**

| Aspect | Source of Truth | Integration Mechanism |
|--------|----------------|----------------------|
| **Budget** | MonitoringEntry | WorkItem.allocated_budget (distributed portion) |
| **Approval** | MonitoringEntry | WorkItem inherits approval context (read-only) |
| **Execution** | WorkItem | Hierarchical task/activity tracking |
| **Progress** | WorkItem (calculated) | Synced to MonitoringEntry.progress |
| **Status** | WorkItem | Synced to MonitoringEntry.status (mapped values) |

### 10.2 Success Metrics

**Alignment Score Target**: 85/100 (from current 40/100 for standalone MonitoringEntry)

**After Full Integration**:
- ✅ PPAs decomposed into hierarchical WBS (projects → activities → tasks)
- ✅ Budget tracking at task level with rollup to PPA
- ✅ Approval workflow integrated with execution tracking
- ✅ Progress automatically calculated from work item completion
- ✅ Bi-directional sync (PPA ↔ WorkItem) with no data duplication
- ✅ Calendar integration for all PPA activities
- ✅ Budget variance tracking and alerts

### 10.3 Risks and Mitigations

**Risk 1: Data Sync Complexity**
- **Mitigation**: Implement idempotent sync methods, extensive testing

**Risk 2: Performance Degradation (Budget Rollup)**
- **Mitigation**: Database indexes, caching layer, async Celery tasks

**Risk 3: User Confusion (Dual Systems)**
- **Mitigation**: Clear UI guidance, training, progressive feature rollout

**Risk 4: Migration Failures**
- **Mitigation**: Rollback plan, staging environment testing, phased deployment

### 10.4 Next Steps

**PRIORITY: CRITICAL | COMPLEXITY: Moderate**

1. **Review & Approval** (1 week)
   - BPDA planning review (alignment with Bangsamoro Development Plan)
   - MFBM budget review (fiscal policy and budget framework compliance)
   - BICTO technical review (ICT infrastructure and security standards)
   - OOBC technical team feedback
   - Stakeholder alignment

2. **Phase 1 Implementation** (2-3 weeks)
   - Database schema migrations
   - Model method implementations
   - Unit test coverage

3. **Phase 2 Implementation** (2-3 weeks)
   - Service layer development
   - API endpoint implementation
   - Integration testing

4. **Phase 3 Implementation** (3-4 weeks)
   - UI development
   - User acceptance testing
   - Documentation and training

**Total Estimated Effort**: 8-10 weeks for full integration (MVP scope)

---

**End of Technical Architecture Document**

**Maintained By**: OBCMS System Architect
**Review Cycle**: Quarterly or after major feature additions
**Last Updated**: 2025-10-05

**References**:
- [WORKITEM_ARCHITECTURAL_ASSESSMENT.md](./WORKITEM_ARCHITECTURAL_ASSESSMENT.md)
- [Unified PM Research](./obcms_unified_pm_research.md)
- [MonitoringEntry Model](/src/monitoring/models.py)
- [WorkItem Model](/src/common/work_item_model.py)
