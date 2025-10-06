# MOA PPA WorkItem Integration: Implementation Tracker

**Document Type**: Implementation Tracking & Progress Monitoring
**Status**: IN PROGRESS
**Start Date**: October 6, 2025
**Target Completion**: TBD (Based on phase complexity)
**Owner**: BICTO Development Team

---

## 📋 Implementation Overview

This document tracks the systematic implementation of the MOA PPA WorkItem Integration across 8 phases. All tasks follow the approved implementation plan with PRIORITY and COMPLEXITY assessments (no time estimates per CLAUDE.md).

**Related Documents:**
- Architecture: `docs/research/MOA_PPA_WORKITEM_INTEGRATION_ARCHITECTURE.md`
- Implementation Plan: `docs/research/MOA_PPA_WORKITEM_INTEGRATION_PLAN.md`
- Roadmap: `docs/improvements/MOA_PPA_WORKITEM_INTEGRATION_ROADMAP.md`

---

## 🎯 Phase Status Overview

| Phase | Priority | Complexity | Status | Progress | Blockers |
|-------|----------|------------|--------|----------|----------|
| Phase 1: Database Foundation | CRITICAL | Moderate | 🟡 IN PROGRESS | 0% | None |
| Phase 2: Service Layer | CRITICAL | Complex | ⚪ PENDING | 0% | Requires Phase 1 |
| Phase 3: API Endpoints | HIGH | Moderate | ⚪ PENDING | 0% | Requires Phase 2 |
| Phase 4: UI/UX Enhancements | HIGH | Moderate | ⚪ PENDING | 0% | Requires Phase 3 |
| Phase 5: Compliance & Reporting | CRITICAL | Moderate | ⚪ PENDING | 0% | Requires Phase 2 |
| Phase 6: Automation | MEDIUM | Complex | ⚪ PENDING | 0% | Requires Phase 2 |
| Phase 7: Testing & Deployment | HIGH | Complex | ⚪ PENDING | 0% | Requires Phases 1-6 |
| Phase 8: Documentation & Training | MEDIUM | Simple | ⚪ PENDING | 0% | Requires Phase 7 |

**Legend**: 🟢 COMPLETE | 🟡 IN PROGRESS | ⚪ PENDING | 🔴 BLOCKED

---

## PHASE 1: DATABASE FOUNDATION

**Priority**: CRITICAL
**Complexity**: Moderate
**Dependencies**: None
**Status**: 🟡 IN PROGRESS

### 1.1 Create Migration Files

#### ✅ Task 1.1.1: MonitoringEntry Integration Migration
**File**: `src/monitoring/migrations/0018_add_workitem_integration.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Add `execution_project` field (OneToOne to WorkItem, null=True, blank=True)
- [ ] Add `enable_workitem_tracking` field (BooleanField, default=False)
- [ ] Add `budget_distribution_policy` field (CharField, max_length=20, choices=['equal', 'weighted', 'manual'])
- [ ] Add `auto_sync_progress` field (BooleanField, default=True)
- [ ] Add `auto_sync_status` field (BooleanField, default=True)
- [ ] Add database index on `enable_workitem_tracking`
- [ ] Test migration on development database (backup required first)

**Acceptance Criteria:**
- Migration applies cleanly without errors
- All new fields are nullable (backward compatible)
- Database backup created before migration
- Rollback procedure tested

**Implementation Notes:**
```python
# Expected migration structure
operations = [
    migrations.AddField(
        model_name='monitoringentry',
        name='execution_project',
        field=models.OneToOneField(
            'common.WorkItem',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name='ppa_entry',
            help_text="Root WorkItem (project) for execution tracking"
        ),
    ),
    # ... additional fields
]
```

---

#### ✅ Task 1.1.2: WorkItem Explicit FK Migration
**File**: `src/common/migrations/0021_workitem_explicit_fks.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Add `related_ppa` FK (to MonitoringEntry, null=True, blank=True)
- [ ] Add `related_assessment` FK (to Assessment, null=True, blank=True)
- [ ] Add `related_policy` FK (to PolicyRecommendation, null=True, blank=True)
- [ ] Add `allocated_budget` field (DecimalField, max_digits=14, decimal_places=2)
- [ ] Add `actual_expenditure` field (DecimalField, max_digits=14, decimal_places=2)
- [ ] Add `budget_notes` field (TextField, blank=True)
- [ ] Add indexes on all FK fields
- [ ] Data migration: convert existing Generic FK to explicit FK where applicable

**Acceptance Criteria:**
- All existing WorkItem relationships preserved
- Generic FK data migrated to explicit FKs
- No orphaned records
- Performance verified (query count reduced)

**Implementation Notes:**
```python
# Data migration to convert Generic FK to explicit FK
def migrate_generic_to_explicit(apps, schema_editor):
    WorkItem = apps.get_model('common', 'WorkItem')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    ppa_ct = ContentType.objects.get(app_label='monitoring', model='monitoringentry')

    for work_item in WorkItem.objects.filter(content_type=ppa_ct):
        if work_item.object_id:
            work_item.related_ppa_id = work_item.object_id
            work_item.save(update_fields=['related_ppa'])
```

---

### 1.2 Update Model Methods

#### ✅ Task 1.2.1: MonitoringEntry Execution Methods
**File**: `src/monitoring/models.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Add `create_execution_project(structure_template='activity')` method
- [ ] Add `sync_progress_from_workitem()` method
- [ ] Add `sync_status_from_workitem()` method
- [ ] Add `get_budget_allocation_tree()` method
- [ ] Add `validate_budget_distribution()` method
- [ ] Write unit tests for all methods (>95% coverage)

**Acceptance Criteria:**
- All methods have docstrings with examples
- Methods are idempotent (safe to call multiple times)
- Validation errors raise appropriate exceptions
- Test coverage >95%

**Implementation Template:**
```python
class MonitoringEntry(models.Model):
    # ... existing fields ...

    execution_project = models.OneToOneField(
        'common.WorkItem',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='ppa_entry'
    )

    def create_execution_project(self, structure_template='activity', created_by=None):
        """
        Create root WorkItem project for execution tracking.

        Args:
            structure_template: 'program', 'activity', or 'minimal'
            created_by: User creating the project

        Returns:
            WorkItem: Created project instance

        Raises:
            ValidationError: If execution_project already exists
        """
        from common.services.workitem_generation import WorkItemGenerationService

        if self.execution_project:
            raise ValidationError("Execution project already exists")

        service = WorkItemGenerationService()
        project = service.generate_from_ppa(
            ppa=self,
            template=structure_template,
            created_by=created_by or self.created_by
        )

        self.execution_project = project
        self.enable_workitem_tracking = True
        self.save(update_fields=['execution_project', 'enable_workitem_tracking'])

        return project
```

---

#### ✅ Task 1.2.2: WorkItem PPA Integration Methods
**File**: `src/common/work_item_model.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Add `get_ppa_source()` property
- [ ] Add `calculate_budget_from_children()` method
- [ ] Add `validate_budget_rollup()` method
- [ ] Add `sync_to_ppa()` method
- [ ] Write unit tests (>95% coverage)

**Implementation Template:**
```python
class WorkItem(MPTTModel):
    # ... existing fields ...

    related_ppa = models.ForeignKey(
        'monitoring.MonitoringEntry',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='work_items'
    )

    @property
    def get_ppa_source(self):
        """
        Get the source PPA for this work item.
        Traverses up the tree to find root with PPA link.

        Returns:
            MonitoringEntry or None
        """
        if self.related_ppa:
            return self.related_ppa

        # Check if this is execution project for a PPA
        if hasattr(self, 'ppa_entry'):
            return self.ppa_entry

        # Traverse up tree
        if self.parent:
            return self.parent.get_ppa_source

        return None
```

---

### 1.3 Register Audit Logging

#### ✅ Task 1.3.1: Configure Auditlog
**Files**: `src/monitoring/models.py`, `src/common/work_item_model.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Register MonitoringEntry with django-auditlog
- [ ] Register WorkItem with django-auditlog
- [ ] Include all budget-related fields in audit
- [ ] Test audit trail captures changes correctly
- [ ] Verify audit log export functionality

**Implementation:**
```python
# In src/monitoring/models.py (at bottom)
from auditlog.registry import auditlog

auditlog.register(
    MonitoringEntry,
    include_fields=[
        'title', 'category', 'status', 'approval_status',
        'budget_allocation', 'budget_obc_allocation',
        'execution_project', 'enable_workitem_tracking',
        'budget_distribution_policy', 'auto_sync_progress',
        'implementing_moa', 'lead_organization'
    ]
)

# In src/common/work_item_model.py (at bottom)
auditlog.register(
    WorkItem,
    include_fields=[
        'title', 'work_type', 'status', 'priority', 'progress',
        'related_ppa', 'allocated_budget', 'actual_expenditure',
        'parent', 'start_date', 'due_date'
    ]
)
```

---

## PHASE 2: SERVICE LAYER

**Priority**: CRITICAL
**Complexity**: Complex
**Dependencies**: Phase 1 complete
**Status**: ⚪ PENDING

### 2.1 Budget Distribution Service

#### ✅ Task 2.1.1: Create Budget Distribution Service
**File**: `src/monitoring/services/budget_distribution.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Create service class `BudgetDistributionService`
- [ ] Implement `distribute_equal(ppa, work_items)` method
- [ ] Implement `distribute_weighted(ppa, work_items, weights)` method
- [ ] Implement `distribute_manual(ppa, allocations)` method
- [ ] Add validation: sum of allocations = PPA budget
- [ ] Handle decimal precision correctly
- [ ] Write comprehensive unit tests

**Acceptance Criteria:**
- All distribution methods validated
- Budget rollup always equals PPA budget (within 0.01 tolerance)
- Handles edge cases (zero budget, single work item, uneven distribution)
- Performance: <100ms for 1000+ work items

**Implementation Template:**
```python
from decimal import Decimal
from django.core.exceptions import ValidationError

class BudgetDistributionService:
    """Service for distributing PPA budget across WorkItem hierarchy."""

    def distribute_equal(self, ppa, work_items):
        """
        Distribute budget equally across all work items.

        Args:
            ppa: MonitoringEntry instance
            work_items: QuerySet of WorkItem instances

        Returns:
            dict: {work_item_id: allocated_amount}
        """
        if not ppa.budget_allocation:
            raise ValidationError("PPA has no budget allocation")

        count = work_items.count()
        if count == 0:
            raise ValidationError("No work items to distribute budget")

        # Equal distribution with remainder handling
        amount_per_item = ppa.budget_allocation / count

        allocations = {}
        total_allocated = Decimal('0.00')

        for item in work_items:
            allocations[item.id] = amount_per_item
            total_allocated += amount_per_item

        # Handle rounding remainder (assign to first item)
        remainder = ppa.budget_allocation - total_allocated
        if remainder != 0:
            first_item = work_items.first()
            allocations[first_item.id] += remainder

        return allocations
```

---

### 2.2 WorkItem Generation Service

#### ✅ Task 2.2.1: Create WorkItem Generation Service
**File**: `src/common/services/workitem_generation.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Create service class `WorkItemGenerationService`
- [ ] Implement WBS template structures (program, activity, minimal)
- [ ] Auto-generate project hierarchy from PPA data
- [ ] Handle budget distribution during generation
- [ ] Validate parent-child relationships
- [ ] Write unit tests for all templates

**Acceptance Criteria:**
- Generates valid MPTT hierarchy
- Budget distributed correctly during generation
- All work items linked to source PPA
- Templates customizable via settings

**Implementation Template:**
```python
from common.models import WorkItem

class WorkItemGenerationService:
    """Service for generating WorkItem hierarchy from PPA templates."""

    TEMPLATES = {
        'program': {
            'structure': [
                {'work_type': 'sub_project', 'title': 'Planning & Design', 'budget_pct': 0.20},
                {'work_type': 'sub_project', 'title': 'Implementation', 'budget_pct': 0.60},
                {'work_type': 'sub_project', 'title': 'M&E', 'budget_pct': 0.20},
            ]
        },
        'activity': {
            'structure': [
                {'work_type': 'activity', 'title': 'Preparation', 'budget_pct': 0.15},
                {'work_type': 'activity', 'title': 'Execution', 'budget_pct': 0.75},
                {'work_type': 'activity', 'title': 'Completion', 'budget_pct': 0.10},
            ]
        },
        'minimal': {
            'structure': [
                {'work_type': 'task', 'title': 'Main Deliverable', 'budget_pct': 1.00},
            ]
        }
    }

    def generate_from_ppa(self, ppa, template='activity', created_by=None):
        """
        Generate WorkItem hierarchy from PPA using template.

        Args:
            ppa: MonitoringEntry instance
            template: 'program', 'activity', or 'minimal'
            created_by: User creating the work items

        Returns:
            WorkItem: Root project instance
        """
        from monitoring.services.budget_distribution import BudgetDistributionService

        # Create root project
        project = WorkItem.objects.create(
            title=ppa.title,
            description=ppa.summary,
            work_type='project',
            related_ppa=ppa,
            allocated_budget=ppa.budget_allocation,
            created_by=created_by,
            start_date=ppa.start_date,
            due_date=ppa.target_end_date,
            priority='high' if ppa.priority == 'urgent' else ppa.priority
        )

        # Generate children from template
        template_data = self.TEMPLATES.get(template, self.TEMPLATES['activity'])
        budget_service = BudgetDistributionService()

        for item_config in template_data['structure']:
            child_budget = ppa.budget_allocation * Decimal(str(item_config['budget_pct']))

            WorkItem.objects.create(
                parent=project,
                title=f"{item_config['title']} - {ppa.title}",
                work_type=item_config['work_type'],
                related_ppa=ppa,
                allocated_budget=child_budget,
                created_by=created_by,
                start_date=ppa.start_date,
                due_date=ppa.target_end_date
            )

        return project
```

---

### 2.3 Django Signal Handlers

#### ✅ Task 2.3.1: Create Signal Handlers
**File**: `src/monitoring/signals.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Create signal handlers file
- [ ] Implement `post_save` for MonitoringEntry approval changes
- [ ] Auto-create WorkItem when PPA reaches "technical_review"
- [ ] Auto-activate WorkItem when PPA reaches "enacted"
- [ ] Register signals in `apps.py`
- [ ] Write signal tests

**Implementation:**
```python
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from monitoring.models import MonitoringEntry
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=MonitoringEntry)
def track_approval_status_change(sender, instance, **kwargs):
    """Track approval status changes for workflow automation."""
    if instance.pk:
        try:
            old_instance = MonitoringEntry.objects.get(pk=instance.pk)
            instance._old_approval_status = old_instance.approval_status
        except MonitoringEntry.DoesNotExist:
            instance._old_approval_status = None

@receiver(post_save, sender=MonitoringEntry)
def handle_ppa_approval_workflow(sender, instance, created, **kwargs):
    """
    Auto-create WorkItem project when PPA approved for execution.

    Triggers:
    - technical_review: Create execution project structure
    - enacted: Activate project (set status to in_progress)
    """
    if created:
        return

    old_status = getattr(instance, '_old_approval_status', None)
    new_status = instance.approval_status

    # Trigger: Technical Review → Create execution project
    if (old_status != 'technical_review' and
        new_status == 'technical_review' and
        instance.enable_workitem_tracking and
        not instance.execution_project):

        try:
            project = instance.create_execution_project(
                structure_template=instance.budget_distribution_policy or 'activity',
                created_by=instance.updated_by or instance.created_by
            )
            logger.info(f"Auto-created execution project for PPA {instance.id}: {project.id}")
        except Exception as e:
            logger.error(f"Failed to create execution project for PPA {instance.id}: {e}")

    # Trigger: Enacted → Activate execution project
    if (old_status != 'enacted' and
        new_status == 'enacted' and
        instance.execution_project):

        instance.execution_project.status = 'in_progress'
        instance.execution_project.save(update_fields=['status'])
        logger.info(f"Activated execution project for enacted PPA {instance.id}")
```

**Register in apps.py:**
```python
# src/monitoring/apps.py
from django.apps import AppConfig

class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self):
        import monitoring.signals  # noqa
```

---

## PHASE 3: API ENDPOINTS

**Priority**: HIGH
**Complexity**: Moderate
**Dependencies**: Phase 2 complete
**Status**: ⚪ PENDING

### 3.1 PPA-WorkItem Integration APIs

#### ✅ Task 3.1.1: Enable WorkItem Tracking Endpoint
**File**: `src/monitoring/api_views.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Endpoint**: `POST /api/monitoring-entries/{id}/enable_workitem_tracking/`

**Requirements:**
- [ ] Create APIView class
- [ ] Validate PPA is in correct approval stage
- [ ] Call `create_execution_project()` method
- [ ] Return created project details
- [ ] Handle errors gracefully
- [ ] Write API tests

**Implementation:**
```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from monitoring.models import MonitoringEntry
from common.serializers import WorkItemSerializer

@api_view(['POST'])
def enable_workitem_tracking(request, pk):
    """
    Enable WorkItem execution tracking for a PPA.

    POST /api/monitoring-entries/{id}/enable_workitem_tracking/

    Body:
        {
            "structure_template": "program" | "activity" | "minimal"
        }

    Returns:
        {
            "success": true,
            "execution_project": {...WorkItem data...},
            "message": "Execution tracking enabled"
        }
    """
    try:
        ppa = MonitoringEntry.objects.get(pk=pk)
    except MonitoringEntry.DoesNotExist:
        return Response(
            {"error": "PPA not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Validate approval status
    if ppa.approval_status not in ['technical_review', 'budget_review', 'enacted']:
        return Response(
            {"error": "PPA must be in technical review or later stage"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if already enabled
    if ppa.execution_project:
        return Response(
            {"error": "WorkItem tracking already enabled"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create execution project
    template = request.data.get('structure_template', 'activity')
    project = ppa.create_execution_project(
        structure_template=template,
        created_by=request.user
    )

    return Response({
        "success": True,
        "execution_project": WorkItemSerializer(project).data,
        "message": "Execution tracking enabled successfully"
    }, status=status.HTTP_201_CREATED)
```

---

#### ✅ Task 3.1.2: Budget Allocation Tree Endpoint
**File**: `src/monitoring/api_views.py`
**Status**: ⚪ PENDING

**Endpoint**: `GET /api/monitoring-entries/{id}/budget_allocation_tree/`

**Requirements:**
- [ ] Return hierarchical budget breakdown
- [ ] Include actual expenditure per work item
- [ ] Calculate variance (allocated vs actual)
- [ ] Format as tree structure (JSON)
- [ ] Write API tests

**Response Format:**
```json
{
    "ppa_id": "uuid",
    "total_budget": "5000000.00",
    "total_allocated": "5000000.00",
    "total_expended": "1250000.00",
    "tree": [
        {
            "id": "project-uuid",
            "title": "Livelihood Training Program",
            "work_type": "project",
            "allocated": "5000000.00",
            "expended": "1250000.00",
            "variance": "3750000.00",
            "children": [
                {
                    "id": "activity-uuid-1",
                    "title": "Preparation",
                    "work_type": "activity",
                    "allocated": "750000.00",
                    "expended": "500000.00",
                    "variance": "250000.00",
                    "children": []
                }
            ]
        }
    ]
}
```

---

## PHASE 4: UI/UX ENHANCEMENTS

**Priority**: HIGH
**Complexity**: Moderate
**Dependencies**: Phase 3 complete
**Status**: ⚪ PENDING

### 4.1 MOA PPA Dashboard Tab

#### ✅ Task 4.1.1: Add Work Items Tab
**File**: `src/templates/monitoring/detail.html`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Add "Work Items" tab to PPA detail page
- [ ] Show hierarchical tree view of all work items
- [ ] Display budget allocation per work item
- [ ] Show progress percentage
- [ ] Add "Enable Tracking" button (if not enabled)
- [ ] Use HTMX for instant updates
- [ ] Follow OBCMS UI standards

**UI Components:**
```django
{# src/templates/monitoring/detail.html #}

{% extends "base.html" %}
{% block content %}

<div class="container mx-auto px-4 py-6">
    <!-- PPA Header -->
    <div class="bg-white rounded-xl border shadow-sm p-6 mb-6">
        <h1 class="text-2xl font-bold text-gray-900">{{ ppa.title }}</h1>
        <div class="mt-2 flex items-center gap-4">
            <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                {{ ppa.get_category_display }}
            </span>
            <span class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm">
                {{ ppa.get_approval_status_display }}
            </span>
        </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-xl border shadow-sm">
        <div class="border-b border-gray-200">
            <nav class="flex -mb-px">
                <a href="#details" class="py-4 px-6 border-b-2 border-blue-500 text-blue-600 font-medium">
                    Details
                </a>
                <a href="#work-items" class="py-4 px-6 border-b-2 border-transparent hover:border-gray-300 text-gray-500 hover:text-gray-700">
                    Work Items
                </a>
                <a href="#budget" class="py-4 px-6 border-b-2 border-transparent hover:border-gray-300 text-gray-500 hover:text-gray-700">
                    Budget Tracking
                </a>
            </nav>
        </div>

        <!-- Work Items Tab Content -->
        <div id="work-items-tab" class="p-6">
            {% if ppa.execution_project %}
                <!-- Tree View -->
                <div class="space-y-2">
                    {% include "monitoring/partials/work_item_tree.html" with item=ppa.execution_project level=0 %}
                </div>
            {% else %}
                <!-- Enable Tracking CTA -->
                <div class="text-center py-12">
                    <i class="fas fa-project-diagram text-6xl text-gray-300 mb-4"></i>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">
                        Work Item Tracking Not Enabled
                    </h3>
                    <p class="text-gray-500 mb-6">
                        Enable execution tracking to break down this PPA into manageable work items.
                    </p>
                    <button
                        hx-post="{% url 'api:enable-workitem-tracking' ppa.id %}"
                        hx-vals='{"structure_template": "activity"}'
                        hx-swap="outerHTML"
                        class="px-6 py-3 bg-gradient-to-r from-blue-500 to-teal-500 text-white rounded-xl hover:shadow-lg transition-all"
                    >
                        <i class="fas fa-tasks mr-2"></i>
                        Enable Work Item Tracking
                    </button>
                </div>
            {% endif %}
        </div>
    </div>
</div>

{% endblock %}
```

---

## PHASE 5: COMPLIANCE & REPORTING

**Priority**: CRITICAL
**Complexity**: Moderate
**Dependencies**: Phase 2 complete
**Status**: ⚪ PENDING

### 5.1 MFBM Budget Execution Report

#### ✅ Task 5.1.1: Create MFBM Excel Report
**File**: `src/monitoring/services/reports.py`
**Status**: ⚪ PENDING
**Assignee**: TBD

**Requirements:**
- [ ] Create `generate_mfbm_budget_execution_report()` function
- [ ] Include all PPAs with budget allocation
- [ ] Show WorkItem expenditure if tracking enabled
- [ ] Calculate variance (allocated vs expended)
- [ ] Export to Excel (openpyxl)
- [ ] Follow MFBM format standards

**Excel Columns:**
1. PPA Code
2. PPA Title
3. Implementing MOA
4. Budget Allocated (PHP)
5. Actual Expenditure (PHP)
6. Variance (PHP)
7. Variance %
8. Status
9. Remarks

**Implementation:**
```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from django.http import HttpResponse

def generate_mfbm_budget_execution_report(fiscal_year, moa_filter=None):
    """
    Generate MFBM Budget Execution Report (Excel).

    Args:
        fiscal_year: Fiscal year to report
        moa_filter: Optional MOA name filter

    Returns:
        HttpResponse with Excel file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = f"Budget Execution FY{fiscal_year}"

    # Header row
    headers = [
        'PPA Code', 'PPA Title', 'Implementing MOA',
        'Budget Allocated', 'Actual Expenditure', 'Variance',
        'Variance %', 'Status', 'Remarks'
    ]

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="1F4788", end_color="1F4788", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")

    # Data rows
    ppas = MonitoringEntry.objects.filter(fiscal_year=fiscal_year)
    if moa_filter:
        ppas = ppas.filter(implementing_moa__name__icontains=moa_filter)

    for row_num, ppa in enumerate(ppas.with_funding_totals(), start=2):
        # Calculate actual from WorkItem if tracking enabled
        if ppa.execution_project:
            actual = ppa.execution_project.get_descendants().aggregate(
                total=Sum('actual_expenditure')
            )['total'] or 0
        else:
            actual = ppa.total_disbursements

        variance = ppa.budget_allocation - actual
        variance_pct = (variance / ppa.budget_allocation * 100) if ppa.budget_allocation else 0

        ws.cell(row=row_num, column=1, value=ppa.program_code or f"PPA-{ppa.id}")
        ws.cell(row=row_num, column=2, value=ppa.title)
        ws.cell(row=row_num, column=3, value=ppa.implementing_moa.name if ppa.implementing_moa else "")
        ws.cell(row=row_num, column=4, value=float(ppa.budget_allocation or 0))
        ws.cell(row=row_num, column=5, value=float(actual))
        ws.cell(row=row_num, column=6, value=float(variance))
        ws.cell(row=row_num, column=7, value=f"{variance_pct:.2f}%")
        ws.cell(row=row_num, column=8, value=ppa.get_status_display())
        ws.cell(row=row_num, column=9, value="WorkItem Tracking" if ppa.execution_project else "Manual Tracking")

    # Auto-size columns
    for col in ws.columns:
        max_length = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2

    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=MFBM_Budget_Execution_FY{fiscal_year}.xlsx'
    wb.save(response)

    return response
```

---

## PHASE 6: AUTOMATION

**Priority**: MEDIUM
**Complexity**: Complex
**Dependencies**: Phase 2 complete
**Status**: ⚪ PENDING

### 6.1 Celery Scheduled Tasks

#### ✅ Task 6.1.1: Nightly Progress Sync
**File**: `src/monitoring/tasks.py`
**Status**: ⚪ PENDING

**Requirements:**
- [ ] Create `auto_sync_ppa_progress` Celery task
- [ ] Run nightly at 2:00 AM
- [ ] Sync progress from WorkItem to MonitoringEntry
- [ ] Log sync results
- [ ] Handle errors gracefully

**Implementation:**
```python
from celery import shared_task
from monitoring.models import MonitoringEntry
import logging

logger = logging.getLogger(__name__)

@shared_task
def auto_sync_ppa_progress():
    """
    Sync PPA progress from WorkItem hierarchy.
    Runs nightly at 2:00 AM.

    Returns:
        dict: {synced: count, errors: count}
    """
    synced_count = 0
    error_count = 0

    ppas = MonitoringEntry.objects.filter(
        enable_workitem_tracking=True,
        auto_sync_progress=True,
        execution_project__isnull=False
    )

    for ppa in ppas:
        try:
            ppa.sync_progress_from_workitem()
            synced_count += 1
        except Exception as e:
            logger.error(f"Failed to sync progress for PPA {ppa.id}: {e}")
            error_count += 1

    logger.info(f"Progress sync complete: {synced_count} synced, {error_count} errors")

    return {
        'synced': synced_count,
        'errors': error_count
    }
```

**Schedule in settings:**
```python
# src/obc_management/settings/base.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'auto-sync-ppa-progress': {
        'task': 'monitoring.tasks.auto_sync_ppa_progress',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
    },
    'detect-budget-variances': {
        'task': 'monitoring.tasks.detect_budget_variances',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'send-approval-deadline-reminders': {
        'task': 'monitoring.tasks.send_approval_deadline_reminders',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
    },
}
```

---

## PHASE 7: TESTING & DEPLOYMENT

**Priority**: HIGH
**Complexity**: Complex
**Dependencies**: Phases 1-6 complete
**Status**: ⚪ PENDING

### 7.1 Unit Tests (Target: >95% Coverage)

#### ✅ Task 7.1.1: Model Tests
**File**: `src/monitoring/tests/test_workitem_integration.py`
**Status**: ⚪ PENDING

**Test Coverage:**
- [ ] `MonitoringEntry.create_execution_project()` - all templates
- [ ] `MonitoringEntry.sync_progress_from_workitem()` - bidirectional
- [ ] `WorkItem.get_ppa_source()` - tree traversal
- [ ] Budget rollup validation
- [ ] Signal handlers (approval workflow)

---

## PHASE 8: DOCUMENTATION & TRAINING

**Priority**: MEDIUM
**Complexity**: Simple
**Dependencies**: Phase 7 complete
**Status**: ⚪ PENDING

### 8.1 User Documentation

#### ✅ Task 8.1.1: MOA User Guide
**File**: `docs/user-guides/MOA_WORKITEM_TRACKING_GUIDE.md`
**Status**: ⚪ PENDING

**Contents:**
- [ ] How to enable WorkItem tracking for a PPA
- [ ] Understanding the work breakdown structure
- [ ] Tracking progress and updating tasks
- [ ] Viewing budget allocation tree
- [ ] Generating reports

---

## 📊 Progress Dashboard

### Overall Implementation Progress

```
Phase 1: ████░░░░░░ 0%   (0/9 tasks complete)
Phase 2: ░░░░░░░░░░ 0%   (0/6 tasks complete)
Phase 3: ░░░░░░░░░░ 0%   (0/4 tasks complete)
Phase 4: ░░░░░░░░░░ 0%   (0/3 tasks complete)
Phase 5: ░░░░░░░░░░ 0%   (0/3 tasks complete)
Phase 6: ░░░░░░░░░░ 0%   (0/3 tasks complete)
Phase 7: ░░░░░░░░░░ 0%   (0/5 tasks complete)
Phase 8: ░░░░░░░░░░ 0%   (0/3 tasks complete)

Total: ░░░░░░░░░░ 0%   (0/36 tasks complete)
```

---

## 🚨 Blockers & Risks

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| Migration data loss | HIGH | Database backup before all migrations | DevOps |
| Performance degradation | MEDIUM | Query optimization, caching, indexes | Backend Team |
| User adoption resistance | MEDIUM | Training, gradual rollout, support | Training Team |
| Budget sync conflicts | HIGH | Idempotent sync, conflict resolution | Backend Team |

---

## 📝 Notes & Decisions

### October 6, 2025
- ✅ Corrected all agency references (BICTO → MFBM/BPDA)
- ✅ Implementation plan approved by stakeholder
- 🟡 Starting Phase 1: Database Foundation

---

**Last Updated**: October 6, 2025
**Next Review**: TBD (After Phase 1 completion)
**Document Owner**: BICTO Development Team
