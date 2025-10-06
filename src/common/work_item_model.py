"""
Unified Work Item Model for OBCMS

This module implements a unified hierarchical work management system using Django MPTT.
It replaces and consolidates:
- StaffTask (tasks and subtasks)
- ProjectWorkflow (projects and sub-projects)
- Event (activities and sub-activities)

Architecture: MPTT + JSON Fields + Generic Foreign Keys
Documentation: docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
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

    Example hierarchy:
        Project A
        ├── Sub-Project A1
        │   ├── Activity A1.1 (Workshop)
        │   │   ├── Task: Prepare materials
        │   │   └── Task: Send invitations
        │   └── Activity A1.2 (Field Visit)
        ├── Activity A2 (Consultation)
        │   ├── Sub-Activity A2.1 (Stakeholder mapping)
        │   │   └── Task: Interview community leaders
        │   └── Task: Document findings
        └── Task: Submit final report
            ├── Subtask: Draft report
            └── Subtask: Review and finalize
    """

    # ========== WORK TYPE CONSTANTS ==========
    WORK_TYPE_PROJECT = "project"
    WORK_TYPE_SUB_PROJECT = "sub_project"
    WORK_TYPE_ACTIVITY = "activity"
    WORK_TYPE_SUB_ACTIVITY = "sub_activity"
    WORK_TYPE_TASK = "task"
    WORK_TYPE_SUBTASK = "subtask"

    WORK_TYPE_CHOICES = [
        (WORK_TYPE_PROJECT, "Project"),
        (WORK_TYPE_SUB_PROJECT, "Sub-Project"),
        (WORK_TYPE_ACTIVITY, "Activity"),
        (WORK_TYPE_SUB_ACTIVITY, "Sub-Activity"),
        (WORK_TYPE_TASK, "Task"),
        (WORK_TYPE_SUBTASK, "Subtask"),
    ]

    # ========== IDENTITY ==========
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_type = models.CharField(
        max_length=20,
        choices=WORK_TYPE_CHOICES,
        db_index=True,
        help_text="Type of work item",
    )
    title = models.CharField(max_length=500, help_text="Title of work item")
    description = models.TextField(blank=True, help_text="Detailed description")

    # ========== HIERARCHY (MPTT) ==========
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        help_text="Parent work item (null for top-level)",
    )

    # Related items (non-hierarchical cross-references)
    related_items = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="related_to",
        help_text="Related work items (dependencies, references)",
    )

    # ========== STATUS CONSTANTS & CHOICES ==========
    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_AT_RISK = "at_risk"
    STATUS_BLOCKED = "blocked"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "Not Started"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_AT_RISK, "At Risk"),
        (STATUS_BLOCKED, "Blocked"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STARTED,
        db_index=True,
    )

    # ========== PRIORITY CONSTANTS & CHOICES ==========
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    PRIORITY_CRITICAL = "critical"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_URGENT, "Urgent"),
        (PRIORITY_CRITICAL, "Critical"),
    ]
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        db_index=True,
    )

    # ========== DATES & SCHEDULING ==========
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Calendar display
    is_calendar_visible = models.BooleanField(
        default=True, help_text="Show in calendar view"
    )
    calendar_color = models.CharField(
        max_length=7, default="#3B82F6", help_text="Hex color code for calendar display"
    )

    # ========== PROGRESS TRACKING ==========
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)",
    )

    auto_calculate_progress = models.BooleanField(
        default=True, help_text="Auto-calculate progress from children"
    )

    # ========== ASSIGNMENT ==========
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_work_items",
        blank=True,
        help_text="Assigned users",
    )

    teams = models.ManyToManyField(
        "common.StaffTeam",
        related_name="work_items",
        blank=True,
        help_text="Assigned teams",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_work_items",
    )

    # ========== RECURRENCE ==========
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.ForeignKey(
        "RecurringEventPattern",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recurring_work_items",
    )

    # ========== TYPE-SPECIFIC DATA (JSON) ==========
    project_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Project-specific fields (workflow_stage, budget, etc.)",
    )

    activity_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Activity-specific fields (event_type, location, etc.)",
    )

    task_data = models.JSONField(
        default=dict, blank=True, help_text="Task-specific fields (domain, deliverable_type, etc.)"
    )

    # ========== DOMAIN RELATIONSHIPS ==========
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.UUIDField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    # ========== EXPLICIT DOMAIN RELATIONSHIPS ==========
    # Explicit FK fields for better performance (replacing generic FK where possible)

    related_ppa = models.ForeignKey(
        "monitoring.MonitoringEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="work_items",
        help_text="Related MOA PPA (if applicable)",
    )

    related_assessment = models.ForeignKey(
        "mana.Assessment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="work_items",
        help_text="Related MANA Assessment",
    )

    related_policy = models.ForeignKey(
        "policy_tracking.PolicyRecommendation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="work_items",
        help_text="Related Policy Recommendation",
    )

    # ========== BUDGET TRACKING ==========

    allocated_budget = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Budget allocated to this work item (PHP)",
    )

    actual_expenditure = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual expenditure recorded (PHP)",
    )

    budget_notes = models.TextField(
        blank=True,
        help_text="Budget-related notes and explanations",
    )

    # ========== METADATA ==========
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ========== MPTT CONFIGURATION ==========
    class MPTTMeta:
        order_insertion_by = ["priority", "title"]

    class Meta:
        db_table = "common_work_item"
        verbose_name = "Work Item"
        verbose_name_plural = "Work Items"
        indexes = [
            # Filter indexes
            models.Index(fields=["work_type", "status"]),
            models.Index(fields=["start_date", "due_date"]),
            models.Index(fields=["status", "priority"]),
            # Relationship indexes
            models.Index(fields=["related_ppa"], name="wi_rel_ppa_idx"),
            models.Index(fields=["related_assessment"], name="wi_rel_assessment_idx"),
            models.Index(fields=["related_policy"], name="wi_rel_policy_idx"),
            # MPTT tree traversal indexes (critical for tree queries)
            models.Index(fields=["tree_id", "lft", "rght"], name="wi_tree_traversal_idx"),
            models.Index(fields=["parent_id"], name="wi_parent_idx"),
            # Calendar query index
            models.Index(fields=["is_calendar_visible", "start_date", "due_date"], name="wi_calendar_idx"),
        ]

    def __str__(self):
        return f"{self.get_work_type_display()}: {self.title}"

    # ========== HIERARCHY VALIDATION ==========

    ALLOWED_CHILD_TYPES = {
        WORK_TYPE_PROJECT: [WORK_TYPE_SUB_PROJECT, WORK_TYPE_ACTIVITY, WORK_TYPE_TASK],
        WORK_TYPE_SUB_PROJECT: [
            WORK_TYPE_SUB_PROJECT,
            WORK_TYPE_ACTIVITY,
            WORK_TYPE_TASK,
        ],
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
                raise ValidationError(
                    {
                        "parent": f"{self.parent.get_work_type_display()} cannot have "
                        f"{self.get_work_type_display()} as child"
                    }
                )

        # Validate dates
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError({"due_date": "Due date must be after start date"})

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
                self.save(update_fields=["progress", "updated_at"])

        # Propagate to parent
        if self.parent and self.parent.auto_calculate_progress:
            self.parent.update_progress()

    # ========== CALENDAR INTEGRATION ==========

    def get_calendar_event(self):
        """Return FullCalendar-compatible event dict."""
        return {
            "id": str(self.id),
            "title": self.title,
            "start": self.start_date.isoformat() if self.start_date else None,
            "end": self.due_date.isoformat() if self.due_date else None,
            "backgroundColor": self.calendar_color,
            "borderColor": self._get_status_border_color(),
            "extendedProps": {
                "workType": self.work_type,
                "workTypeDisplay": self.get_work_type_display(),
                "status": self.status,
                "statusDisplay": self.get_status_display(),
                "priority": self.priority,
                "priorityDisplay": self.get_priority_display(),
                "progress": self.progress,
                "assignees": [u.get_full_name() for u in self.assignees.all()],
            },
        }

    def _get_status_border_color(self):
        """Get border color based on status."""
        status_colors = {
            self.STATUS_NOT_STARTED: "#9CA3AF",
            self.STATUS_IN_PROGRESS: "#3B82F6",
            self.STATUS_AT_RISK: "#F59E0B",
            self.STATUS_BLOCKED: "#EF4444",
            self.STATUS_COMPLETED: "#10B981",
            self.STATUS_CANCELLED: "#6B7280",
        }
        return status_colors.get(self.status, "#3B82F6")

    # ========== TYPE-SPECIFIC HELPERS ==========

    @property
    def is_project(self):
        """Check if this is a project or sub-project."""
        return self.work_type in [self.WORK_TYPE_PROJECT, self.WORK_TYPE_SUB_PROJECT]

    @property
    def is_activity(self):
        """Check if this is an activity or sub-activity."""
        return self.work_type in [self.WORK_TYPE_ACTIVITY, self.WORK_TYPE_SUB_ACTIVITY]

    @property
    def is_task(self):
        """Check if this is a task or subtask."""
        return self.work_type in [self.WORK_TYPE_TASK, self.WORK_TYPE_SUBTASK]

    # ========== PPA INTEGRATION METHODS ==========

    @property
    def get_ppa_source(self):
        """
        Get the source PPA for this work item.

        Traverses up the MPTT tree to find the root WorkItem with a PPA link.
        Checks in this order:
        1. Direct related_ppa FK on this WorkItem
        2. If this WorkItem is the execution_project for a PPA (reverse OneToOne)
        3. Traverses up parent hierarchy to find PPA

        Returns:
            MonitoringEntry or None: The source PPA if found, otherwise None

        Example:
            >>> task = WorkItem.objects.get(title="Prepare venue")
            >>> ppa = task.get_ppa_source
            >>> print(ppa.title)
            "Livelihood Training Program for OBCs"
        """
        # Check if this WorkItem has a direct PPA link
        if self.related_ppa:
            return self.related_ppa

        # Check if this is the execution_project for a PPA (reverse OneToOne)
        if hasattr(self, "ppa_source"):
            return self.ppa_source

        # Traverse up the parent hierarchy
        if self.parent:
            return self.parent.get_ppa_source

        # No PPA found in hierarchy
        return None

    def calculate_budget_from_children(self):
        """
        Calculate total budget by summing allocated_budget from immediate children.

        Useful for validating budget distribution or auto-calculating parent budgets
        based on child allocations.

        Returns:
            Decimal: Sum of children's allocated_budget (0.00 if no children or no budgets)

        Example:
            >>> project = WorkItem.objects.get(title="Livelihood Program")
            >>> total = project.calculate_budget_from_children()
            >>> print(f"Total child budgets: ₱{total:,.2f}")
            "Total child budgets: ₱5,000,000.00"
        """
        children = self.get_children()

        if not children.exists():
            return Decimal("0.00")

        total = Decimal("0.00")
        for child in children:
            if child.allocated_budget:
                total += child.allocated_budget

        return total

    def validate_budget_rollup(self):
        """
        Validate that children's budgets sum to this work item's allocated_budget.

        Raises ValidationError if:
        - Children budgets exceed parent budget
        - Children budgets are significantly less than parent budget (tolerance: 0.01 PHP)

        Returns:
            bool: True if validation passes

        Raises:
            ValidationError: If budget rollup validation fails

        Example:
            >>> project = WorkItem.objects.get(title="Livelihood Program")
            >>> project.allocated_budget = Decimal("5000000.00")
            >>> project.validate_budget_rollup()  # Checks if children sum to 5M
            True
        """
        if not self.allocated_budget:
            # No parent budget set - nothing to validate
            return True

        children_total = self.calculate_budget_from_children()

        if not children_total:
            # No children with budgets - validation passes
            return True

        # Calculate variance (allow 0.01 PHP tolerance for rounding)
        variance = abs(self.allocated_budget - children_total)
        tolerance = Decimal("0.01")

        if variance > tolerance:
            raise ValidationError(
                {
                    "allocated_budget": (
                        f"Budget rollup mismatch: Parent budget is ₱{self.allocated_budget:,.2f}, "
                        f"but children budgets sum to ₱{children_total:,.2f} "
                        f"(variance: ₱{variance:,.2f})"
                    )
                }
            )

        return True

    def sync_to_ppa(self):
        """
        Sync progress and status back to the source PPA (MonitoringEntry).

        Only syncs if:
        - This WorkItem has a PPA source (via get_ppa_source)
        - PPA has auto_sync flags enabled (auto_sync_progress, auto_sync_status)
        - This is the root execution_project for the PPA

        Calls:
        - ppa.sync_progress_from_workitem() if auto_sync_progress=True
        - ppa.sync_status_from_workitem() if auto_sync_status=True

        Returns:
            dict: Sync status with keys 'progress_synced', 'status_synced', 'ppa_id'

        Example:
            >>> project = WorkItem.objects.get(title="Livelihood Program")
            >>> result = project.sync_to_ppa()
            >>> print(result)
            {'progress_synced': True, 'status_synced': True, 'ppa_id': '...'}
        """
        ppa = self.get_ppa_source

        if not ppa:
            return {
                "progress_synced": False,
                "status_synced": False,
                "ppa_id": None,
                "message": "No PPA source found",
            }

        # Only sync if this is the root execution_project
        if hasattr(self, "ppa_source") and self.ppa_source == ppa:
            result = {"ppa_id": str(ppa.id)}

            # Sync progress if enabled
            if ppa.auto_sync_progress:
                ppa.sync_progress_from_workitem()
                result["progress_synced"] = True
            else:
                result["progress_synced"] = False

            # Sync status if enabled
            if ppa.auto_sync_status:
                ppa.sync_status_from_workitem()
                result["status_synced"] = True
            else:
                result["status_synced"] = False

            return result

        return {
            "progress_synced": False,
            "status_synced": False,
            "ppa_id": str(ppa.id) if ppa else None,
            "message": "Not the execution project for this PPA",
        }

    # ========== LEGACY COMPATIBILITY PROPERTIES ==========

    @property
    def domain(self):
        """Backward compatibility with StaffTask.domain."""
        return self.task_data.get("domain", "general")

    @domain.setter
    def domain(self, value):
        if not self.task_data:
            self.task_data = {}
        self.task_data["domain"] = value

    @property
    def workflow_stage(self):
        """Backward compatibility with ProjectWorkflow.current_stage."""
        return self.project_data.get("workflow_stage", "need_identification")

    @workflow_stage.setter
    def workflow_stage(self, value):
        if not self.project_data:
            self.project_data = {}
        self.project_data["workflow_stage"] = value

    @property
    def event_type(self):
        """Backward compatibility with Event.event_type."""
        return self.activity_data.get("event_type", "other")

    @event_type.setter
    def event_type(self, value):
        if not self.activity_data:
            self.activity_data = {}
        self.activity_data["event_type"] = value


# NOTE: WorkItem is registered with auditlog in common/auditlog_config.py
# This provides centralized audit trail configuration for compliance tracking
