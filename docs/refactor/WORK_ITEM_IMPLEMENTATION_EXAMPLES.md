# WorkItem Implementation Examples

**Related:** [UNIFIED_WORK_HIERARCHY_EVALUATION.md](./UNIFIED_WORK_HIERARCHY_EVALUATION.md)

This document provides concrete code examples for implementing the unified WorkItem system.

---

## Table of Contents

1. [Model Implementation](#model-implementation)
2. [Migration Scripts](#migration-scripts)
3. [Query Patterns](#query-patterns)
4. [Form Examples](#form-examples)
5. [View Examples](#view-examples)
6. [Calendar Integration](#calendar-integration)
7. [Testing Examples](#testing-examples)

---

## 1. Model Implementation

### 1.1 Complete WorkItem Model

```python
# src/common/models.py (new WorkItem model)

import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from mptt.models import MPTTModel, TreeForeignKey


class WorkItem(MPTTModel):
    """
    Unified hierarchical work management model.

    Supports:
    - Projects and Sub-Projects
    - Activities and Sub-Activities
    - Tasks and Subtasks
    - Flexible hierarchical relationships
    - Calendar integration
    - Domain-specific data via JSON fields
    """

    # ========== WORK TYPES ==========
    WORK_TYPE_PROJECT = 'project'
    WORK_TYPE_SUB_PROJECT = 'sub_project'
    WORK_TYPE_ACTIVITY = 'activity'
    WORK_TYPE_SUB_ACTIVITY = 'sub_activity'
    WORK_TYPE_TASK = 'task'
    WORK_TYPE_SUBTASK = 'subtask'

    WORK_TYPE_CHOICES = [
        (WORK_TYPE_PROJECT, 'Project'),
        (WORK_TYPE_SUB_PROJECT, 'Sub-Project'),
        (WORK_TYPE_ACTIVITY, 'Activity'),
        (WORK_TYPE_SUB_ACTIVITY, 'Sub-Activity'),
        (WORK_TYPE_TASK, 'Task'),
        (WORK_TYPE_SUBTASK, 'Subtask'),
    ]

    # ========== IDENTITY ==========
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_type = models.CharField(
        max_length=20,
        choices=WORK_TYPE_CHOICES,
        db_index=True,
        help_text="Type of work item"
    )
    title = models.CharField(max_length=255, help_text="Title of work item")
    description = models.TextField(blank=True, help_text="Detailed description")

    # ========== HIERARCHY (MPTT) ==========
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="Parent work item (null for top-level)"
    )

    # Related items (non-hierarchical cross-references)
    related_items = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='related_to',
        help_text="Related work items (dependencies, references)"
    )

    # ========== STATUS & PRIORITY ==========
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_AT_RISK = 'at_risk'
    STATUS_BLOCKED = 'blocked'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Not Started'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_AT_RISK, 'At Risk'),
        (STATUS_BLOCKED, 'Blocked'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
        db_index=True
    )

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'
    PRIORITY_CRITICAL = 'critical'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_URGENT, 'Urgent'),
        (PRIORITY_CRITICAL, 'Critical'),
    ]
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        db_index=True
    )

    # ========== DATES & SCHEDULING ==========
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Calendar display
    is_calendar_visible = models.BooleanField(
        default=True,
        help_text="Show in calendar view"
    )
    calendar_color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hex color code for calendar display"
    )

    # ========== PROGRESS TRACKING ==========
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)"
    )

    auto_calculate_progress = models.BooleanField(
        default=True,
        help_text="Auto-calculate progress from children"
    )

    # ========== ASSIGNMENT ==========
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_work_items',
        blank=True,
        help_text="Assigned users"
    )

    teams = models.ManyToManyField(
        'common.StaffTeam',
        related_name='work_items',
        blank=True,
        help_text="Assigned teams"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_work_items'
    )

    # ========== RECURRENCE ==========
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.ForeignKey(
        'RecurringEventPattern',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='recurring_work_items'
    )

    # ========== TYPE-SPECIFIC DATA (JSON) ==========
    project_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Project-specific fields (workflow_stage, budget, etc.)"
    )

    activity_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Activity-specific fields (event_type, location, etc.)"
    )

    task_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Task-specific fields (domain, deliverable_type, etc.)"
    )

    # ========== DOMAIN RELATIONSHIPS ==========
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.UUIDField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    # ========== METADATA ==========
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ========== MPTT META ==========
    class MPTTMeta:
        order_insertion_by = ['start_date', 'priority', 'title']

    class Meta:
        db_table = 'common_work_item'
        ordering = ['tree_id', 'lft']  # MPTT ordering
        verbose_name = 'Work Item'
        verbose_name_plural = 'Work Items'
        indexes = [
            models.Index(fields=['work_type', 'status']),
            models.Index(fields=['parent', 'work_type']),
            models.Index(fields=['start_date', 'due_date']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['tree_id', 'lft', 'rght']),  # MPTT performance
        ]

    def __str__(self):
        return f"{self.get_work_type_display()}: {self.title}"

    # ========== HIERARCHY METHODS ==========

    def get_root_project(self):
        """Get the top-level project this item belongs to."""
        root = self.get_root()
        return root if root.work_type == self.WORK_TYPE_PROJECT else None

    def get_all_tasks(self):
        """Get all tasks and subtasks under this work item."""
        return self.get_descendants().filter(
            work_type__in=[self.WORK_TYPE_TASK, self.WORK_TYPE_SUBTASK]
        )

    def get_children_by_type(self, work_type):
        """Get immediate children of specific type."""
        return self.get_children().filter(work_type=work_type)

    def get_ancestors_by_type(self, work_type):
        """Get ancestors of specific type."""
        return self.get_ancestors().filter(work_type=work_type)

    # ========== VALIDATION ==========

    ALLOWED_CHILD_TYPES = {
        WORK_TYPE_PROJECT: [WORK_TYPE_SUB_PROJECT, WORK_TYPE_ACTIVITY, WORK_TYPE_TASK],
        WORK_TYPE_SUB_PROJECT: [WORK_TYPE_SUB_PROJECT, WORK_TYPE_ACTIVITY, WORK_TYPE_TASK],
        WORK_TYPE_ACTIVITY: [WORK_TYPE_SUB_ACTIVITY, WORK_TYPE_TASK],
        WORK_TYPE_SUB_ACTIVITY: [WORK_TYPE_SUB_ACTIVITY, WORK_TYPE_TASK],
        WORK_TYPE_TASK: [WORK_TYPE_SUBTASK],
        WORK_TYPE_SUBTASK: [],  # No children allowed
    }

    def can_have_child_type(self, child_type):
        """Check if this work item can have the specified child type."""
        return child_type in self.ALLOWED_CHILD_TYPES.get(self.work_type, [])

    def clean(self):
        """Model validation."""
        super().clean()

        # Validate parent-child relationship
        if self.parent:
            if not self.parent.can_have_child_type(self.work_type):
                raise ValidationError({
                    'parent': f"{self.parent.get_work_type_display()} cannot have "
                              f"{self.get_work_type_display()} as child"
                })

        # Validate dates
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError({
                'due_date': 'Due date must be after start date'
            })

        # Prevent circular references in related_items (handled in save)

    # ========== PROGRESS CALCULATION ==========

    def calculate_progress_from_children(self):
        """Calculate progress based on child completion."""
        if not self.auto_calculate_progress:
            return self.progress

        children = self.get_children()
        if not children.exists():
            return self.progress

        total_children = children.count()
        completed_children = children.filter(status=self.STATUS_COMPLETED).count()

        if total_children == 0:
            return self.progress

        calculated_progress = int((completed_children / total_children) * 100)
        return calculated_progress

    def update_progress(self):
        """Update progress and propagate to ancestors."""
        if self.auto_calculate_progress:
            new_progress = self.calculate_progress_from_children()
            if new_progress != self.progress:
                self.progress = new_progress
                self.save(update_fields=['progress', 'updated_at'])

        # Propagate to parent
        if self.parent and self.parent.auto_calculate_progress:
            self.parent.update_progress()

    # ========== CALENDAR INTEGRATION ==========

    def get_calendar_event(self):
        """Return FullCalendar-compatible event dict."""
        return {
            'id': str(self.id),
            'title': self.title,
            'start': self.start_date.isoformat() if self.start_date else None,
            'end': self.due_date.isoformat() if self.due_date else None,
            'backgroundColor': self.calendar_color,
            'borderColor': self._get_status_border_color(),
            'extendedProps': {
                'workType': self.work_type,
                'workTypeDisplay': self.get_work_type_display(),
                'status': self.status,
                'statusDisplay': self.get_status_display(),
                'priority': self.priority,
                'priorityDisplay': self.get_priority_display(),
                'progress': self.progress,
                'assignees': [u.get_full_name() for u in self.assignees.all()],
            }
        }

    def _get_status_border_color(self):
        """Get border color based on status."""
        status_colors = {
            self.STATUS_NOT_STARTED: '#9CA3AF',
            self.STATUS_IN_PROGRESS: '#3B82F6',
            self.STATUS_AT_RISK: '#F59E0B',
            self.STATUS_BLOCKED: '#EF4444',
            self.STATUS_COMPLETED: '#10B981',
            self.STATUS_CANCELLED: '#6B7280',
        }
        return status_colors.get(self.status, '#3B82F6')

    # ========== TYPE-SPECIFIC HELPERS ==========

    @property
    def is_project(self):
        return self.work_type in [self.WORK_TYPE_PROJECT, self.WORK_TYPE_SUB_PROJECT]

    @property
    def is_activity(self):
        return self.work_type in [self.WORK_TYPE_ACTIVITY, self.WORK_TYPE_SUB_ACTIVITY]

    @property
    def is_task(self):
        return self.work_type in [self.WORK_TYPE_TASK, self.WORK_TYPE_SUBTASK]

    # ========== LEGACY COMPATIBILITY ==========

    @property
    def domain(self):
        """Backward compatibility with StaffTask.domain."""
        return self.task_data.get('domain', 'general')

    @domain.setter
    def domain(self, value):
        if not self.task_data:
            self.task_data = {}
        self.task_data['domain'] = value

    @property
    def workflow_stage(self):
        """Backward compatibility with ProjectWorkflow.current_stage."""
        return self.project_data.get('workflow_stage', 'need_identification')

    @workflow_stage.setter
    def workflow_stage(self, value):
        if not self.project_data:
            self.project_data = {}
        self.project_data['workflow_stage'] = value

    @property
    def event_type(self):
        """Backward compatibility with Event.event_type."""
        return self.activity_data.get('event_type', 'other')

    @event_type.setter
    def event_type(self, value):
        if not self.activity_data:
            self.activity_data = {}
        self.activity_data['event_type'] = value
```

---

## 2. Migration Scripts

### 2.1 Data Migration: StaffTask → WorkItem

```python
# src/common/management/commands/migrate_staff_tasks_to_work_items.py

from django.core.management.base import BaseCommand
from django.db import transaction
from common.models import StaffTask, WorkItem
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate StaffTask to WorkItem'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without committing changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        tasks = StaffTask.objects.all().select_related(
            'created_by', 'linked_event', 'linked_workflow'
        ).prefetch_related('assignees', 'teams')

        total = tasks.count()
        self.stdout.write(f"Migrating {total} StaffTasks...")

        migrated = 0
        errors = 0

        for task in tasks:
            try:
                with transaction.atomic():
                    # Determine work type
                    work_type = WorkItem.WORK_TYPE_SUBTASK if task.task_context == 'standalone' else WorkItem.WORK_TYPE_TASK

                    # Create WorkItem
                    work_item = WorkItem(
                        id=task.id,  # Preserve UUID
                        work_type=work_type,
                        title=task.title,
                        description=task.description,
                        status=self._map_status(task.status),
                        priority=task.priority,
                        start_date=task.start_date,
                        due_date=task.due_date,
                        completed_at=task.completed_at,
                        progress=task.progress,
                        is_recurring=task.is_recurring,
                        recurrence_pattern=task.recurrence_pattern,
                        created_by=task.created_by,
                        created_at=task.created_at,
                        updated_at=task.updated_at,

                        # Task-specific data
                        task_data={
                            'domain': task.domain,
                            'task_category': task.task_category,
                            'assessment_phase': task.assessment_phase,
                            'policy_phase': task.policy_phase,
                            'service_phase': task.service_phase,
                            'task_role': task.task_role,
                            'estimated_hours': float(task.estimated_hours) if task.estimated_hours else None,
                            'actual_hours': float(task.actual_hours) if task.actual_hours else None,
                            'deliverable_type': task.deliverable_type,
                            'geographic_scope': task.geographic_scope,
                        },
                    )

                    if not dry_run:
                        work_item.save()

                        # Migrate M2M relationships
                        work_item.assignees.set(task.assignees.all())
                        work_item.teams.set(task.teams.all())

                        # Link to parent if task has context
                        if task.linked_workflow:
                            # Find or create project work item for this workflow
                            parent_project = self._get_or_create_project_work_item(task.linked_workflow)
                            work_item.parent = parent_project
                            work_item.save()

                    migrated += 1
                    if migrated % 100 == 0:
                        self.stdout.write(f"Migrated {migrated}/{total}...")

            except Exception as e:
                errors += 1
                logger.error(f"Error migrating task {task.id}: {e}")
                self.stdout.write(self.style.ERROR(f"Error: {task.id} - {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Migration complete: {migrated} migrated, {errors} errors"
            )
        )

    def _map_status(self, old_status):
        """Map StaffTask status to WorkItem status."""
        status_map = {
            'not_started': WorkItem.STATUS_NOT_STARTED,
            'in_progress': WorkItem.STATUS_IN_PROGRESS,
            'at_risk': WorkItem.STATUS_AT_RISK,
            'completed': WorkItem.STATUS_COMPLETED,
        }
        return status_map.get(old_status, WorkItem.STATUS_NOT_STARTED)

    def _get_or_create_project_work_item(self, workflow):
        """Get or create WorkItem for ProjectWorkflow."""
        # This would be implemented in the ProjectWorkflow migration
        # For now, just return None (tasks remain top-level)
        return None
```

### 2.2 Data Migration: ProjectWorkflow → WorkItem

```python
# src/project_central/management/commands/migrate_workflows_to_work_items.py

from django.core.management.base import BaseCommand
from django.db import transaction
from project_central.models import ProjectWorkflow
from common.models import WorkItem


class Command(BaseCommand):
    help = 'Migrate ProjectWorkflow to WorkItem'

    def handle(self, *args, **options):
        workflows = ProjectWorkflow.objects.all().select_related(
            'primary_need', 'project_lead', 'created_by'
        )

        for workflow in workflows:
            with transaction.atomic():
                work_item = WorkItem(
                    id=workflow.id,
                    work_type=WorkItem.WORK_TYPE_PROJECT,
                    title=workflow.primary_need.title,
                    description=workflow.primary_need.description,
                    status=self._map_status(workflow.current_stage),
                    priority=workflow.priority_level,
                    start_date=workflow.initiated_date,
                    due_date=workflow.target_completion_date,
                    completed_at=workflow.actual_completion_date,
                    progress=workflow.overall_progress,
                    created_by=workflow.created_by,

                    # Project-specific data
                    project_data={
                        'workflow_stage': workflow.current_stage,
                        'stage_history': workflow.stage_history,
                        'estimated_budget': float(workflow.estimated_budget) if workflow.estimated_budget else None,
                        'budget_approved': workflow.budget_approved,
                        'is_on_track': workflow.is_on_track,
                        'is_blocked': workflow.is_blocked,
                        'blocker_description': workflow.blocker_description,
                        'notes': workflow.notes,
                        'lessons_learned': workflow.lessons_learned,
                    },
                )

                work_item.save()

                # Assign project lead
                if workflow.project_lead:
                    work_item.assignees.add(workflow.project_lead)

                self.stdout.write(f"Migrated workflow: {work_item.title}")
```

---

## 3. Query Patterns

### 3.1 Common Queries

```python
# Get all top-level projects
projects = WorkItem.objects.filter(
    work_type=WorkItem.WORK_TYPE_PROJECT,
    parent__isnull=True
)

# Get all tasks under a project (including nested)
project = WorkItem.objects.get(id=project_id)
all_tasks = project.get_descendants().filter(
    work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
)

# Get project tree structure
project_tree = WorkItem.objects.filter(
    tree_id=project.tree_id
).order_by('tree_id', 'lft')

# Get my assigned work items
my_work = WorkItem.objects.filter(
    assignees=request.user,
    status__in=[WorkItem.STATUS_NOT_STARTED, WorkItem.STATUS_IN_PROGRESS]
).select_related('parent')

# Get upcoming activities
from datetime import date, timedelta
upcoming = WorkItem.objects.filter(
    work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY],
    start_date__gte=date.today(),
    start_date__lte=date.today() + timedelta(days=30)
).order_by('start_date')

# Get high-priority incomplete tasks
critical_tasks = WorkItem.objects.filter(
    work_type=WorkItem.WORK_TYPE_TASK,
    priority__in=[WorkItem.PRIORITY_HIGH, WorkItem.PRIORITY_CRITICAL],
    status__in=[WorkItem.STATUS_NOT_STARTED, WorkItem.STATUS_IN_PROGRESS]
)
```

### 3.2 Hierarchical Queries (MPTT)

```python
# Get all children of a work item
children = work_item.get_children()

# Get all descendants (recursive)
descendants = work_item.get_descendants()

# Get all ancestors (path to root)
ancestors = work_item.get_ancestors()

# Get siblings
siblings = work_item.get_siblings()

# Get root project
root = work_item.get_root()

# Check if work item is leaf node (no children)
is_leaf = work_item.is_leaf_node()

# Get level in tree (0 = root)
level = work_item.level

# Move work item to different parent
work_item.move_to(new_parent, position='last-child')
```

---

## 4. Form Examples

### 4.1 Unified WorkItem Form

```python
# src/common/forms/work_item.py

from django import forms
from common.models import WorkItem


class WorkItemForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = [
            'work_type', 'parent', 'title', 'description',
            'status', 'priority', 'start_date', 'due_date',
            'assignees', 'teams', 'is_calendar_visible',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter parent choices based on work_type
        if 'work_type' in self.data:
            work_type = self.data.get('work_type')
            self.fields['parent'].queryset = self._get_allowed_parents(work_type)

    def _get_allowed_parents(self, child_type):
        """Get allowed parent work items based on child type."""
        parent_types = []

        if child_type == WorkItem.WORK_TYPE_SUB_PROJECT:
            parent_types = [WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT]
        elif child_type == WorkItem.WORK_TYPE_ACTIVITY:
            parent_types = [WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT]
        elif child_type == WorkItem.WORK_TYPE_SUB_ACTIVITY:
            parent_types = [WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY]
        elif child_type == WorkItem.WORK_TYPE_TASK:
            parent_types = [
                WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT,
                WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY
            ]
        elif child_type == WorkItem.WORK_TYPE_SUBTASK:
            parent_types = [WorkItem.WORK_TYPE_TASK]

        if parent_types:
            return WorkItem.objects.filter(work_type__in=parent_types)
        return WorkItem.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        work_type = cleaned_data.get('work_type')

        if parent and not parent.can_have_child_type(work_type):
            raise forms.ValidationError(
                f"{parent.get_work_type_display()} cannot have "
                f"{WorkItem(work_type=work_type).get_work_type_display()} as child"
            )

        return cleaned_data
```

### 4.2 Type-Specific Forms

```python
class ProjectWorkItemForm(WorkItemForm):
    """Form for creating/editing projects."""

    workflow_stage = forms.ChoiceField(
        choices=[...],  # From ProjectWorkflow.WORKFLOW_STAGES
        required=False
    )
    estimated_budget = forms.DecimalField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['work_type'].initial = WorkItem.WORK_TYPE_PROJECT
        self.fields['work_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.project_data = {
            'workflow_stage': self.cleaned_data.get('workflow_stage'),
            'estimated_budget': float(self.cleaned_data.get('estimated_budget') or 0),
        }
        if commit:
            instance.save()
        return instance
```

---

## 5. View Examples

### 5.1 HTMX WorkItem Tree View

```python
# src/common/views/work_items.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from common.models import WorkItem


def work_item_tree(request, work_item_id=None):
    """Display hierarchical tree of work items."""

    if work_item_id:
        root = get_object_or_404(WorkItem, id=work_item_id)
        tree = root.get_descendants(include_self=True)
    else:
        # Show all top-level projects
        tree = WorkItem.objects.filter(parent__isnull=True)

    if request.headers.get('HX-Request'):
        # HTMX partial update
        return render(request, 'common/partials/work_item_tree_rows.html', {
            'tree': tree
        })

    return render(request, 'common/work_item_tree.html', {
        'tree': tree,
        'root': root if work_item_id else None
    })


def work_item_create(request, parent_id=None):
    """Create new work item (optionally under parent)."""

    parent = get_object_or_404(WorkItem, id=parent_id) if parent_id else None

    if request.method == 'POST':
        form = WorkItemForm(request.POST)
        if form.is_valid():
            work_item = form.save(commit=False)
            work_item.parent = parent
            work_item.created_by = request.user
            work_item.save()
            form.save_m2m()

            if request.headers.get('HX-Request'):
                # Return updated tree section
                return render(request, 'common/partials/work_item_row.html', {
                    'item': work_item
                })

            return redirect('work_item_detail', work_item_id=work_item.id)
    else:
        form = WorkItemForm(initial={'parent': parent})

    return render(request, 'common/work_item_form.html', {
        'form': form,
        'parent': parent
    })
```

---

## 6. Calendar Integration

### 6.1 Calendar Data Endpoint

```python
# src/common/views/calendar.py

from django.http import JsonResponse
from django.utils.dateparse import parse_date
from common.models import WorkItem


def calendar_events(request):
    """Return work items as FullCalendar events."""

    start = parse_date(request.GET.get('start'))
    end = parse_date(request.GET.get('end'))

    events = WorkItem.objects.filter(
        is_calendar_visible=True,
        start_date__gte=start,
        start_date__lte=end
    ).select_related('parent').prefetch_related('assignees')

    calendar_events = [event.get_calendar_event() for event in events]

    return JsonResponse(calendar_events, safe=False)
```

### 6.2 Calendar Template

```html
<!-- src/templates/common/calendar.html -->

<div id="calendar"></div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: '/api/calendar/events/',
        eventClick: function(info) {
            // Show work item modal
            htmx.ajax('GET', `/work-items/${info.event.id}/detail/`, {
                target: '#modal-container',
                swap: 'innerHTML'
            });
        },
        eventDidMount: function(info) {
            // Add tooltip
            tippy(info.el, {
                content: `
                    <strong>${info.event.title}</strong><br>
                    ${info.event.extendedProps.workTypeDisplay}<br>
                    Status: ${info.event.extendedProps.statusDisplay}<br>
                    Progress: ${info.event.extendedProps.progress}%
                `
            });
        }
    });
    calendar.render();
});
</script>
```

---

## 7. Testing Examples

### 7.1 Model Tests

```python
# src/common/tests/test_work_item.py

from django.test import TestCase
from common.models import WorkItem


class WorkItemHierarchyTest(TestCase):
    def test_project_can_have_activity(self):
        """Project can have activity as child."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Test Project"
        )
        activity = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Test Activity",
            parent=project
        )
        self.assertEqual(activity.parent, project)
        self.assertIn(activity, project.get_children())

    def test_task_cannot_have_project(self):
        """Task cannot have project as child."""
        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Test Task"
        )
        self.assertFalse(task.can_have_child_type(WorkItem.WORK_TYPE_PROJECT))

    def test_progress_calculation(self):
        """Progress auto-calculates from children."""
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            auto_calculate_progress=True
        )
        task1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 1",
            parent=project,
            status=WorkItem.STATUS_COMPLETED
        )
        task2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Task 2",
            parent=project,
            status=WorkItem.STATUS_IN_PROGRESS
        )

        calculated = project.calculate_progress_from_children()
        self.assertEqual(calculated, 50)  # 1 of 2 completed
```

---

**Document Status:** IMPLEMENTATION READY
**Next Step:** Begin Phase 1 - Model Creation
