"""
Proxy Models for Backward Compatibility

This module provides proxy models that maintain the legacy API while
using the new unified WorkItem model underneath.

Phase 4: Backward Compatibility & Proxy Models
See: docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md
"""

from django.db import models
from django.utils import timezone
from common.work_item_model import WorkItem


class StaffTaskProxy(WorkItem):
    """
    Proxy model for StaffTask → WorkItem migration.

    Filters to work_type='task' and provides the same interface
    as the legacy StaffTask model.

    Usage:
        # Old code continues to work
        task = StaffTaskProxy.objects.create(
            title="Review policy draft",
            status="in_progress",
            priority="high"
        )

        # Behind the scenes, it creates a WorkItem with work_type='task'
    """

    class Meta:
        proxy = True
        verbose_name = "Staff Task (Legacy)"
        verbose_name_plural = "Staff Tasks (Legacy)"

    objects = models.Manager()

    def __init__(self, *args, **kwargs):
        # Map legacy StaffTask fields to WorkItem fields
        if 'board_position' in kwargs:
            # Legacy field - ignore or store in task_data
            kwargs.pop('board_position')

        # Auto-set work_type to 'task'
        kwargs.setdefault('work_type', WorkItem.WORK_TYPE_TASK)

        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Ensure work_type is always 'task'
        self.work_type = WorkItem.WORK_TYPE_TASK
        super().save(*args, **kwargs)

    # ========== LEGACY FIELD MAPPINGS ==========

    @property
    def board_position(self):
        """Legacy field for Kanban board ordering."""
        return self.task_data.get('board_position', 0)

    @board_position.setter
    def board_position(self, value):
        if not self.task_data:
            self.task_data = {}
        self.task_data['board_position'] = value

    @property
    def linked_event(self):
        """Legacy relationship to coordination.Event."""
        # Check if related_object is an Event
        from coordination.models import Event
        if isinstance(self.related_object, Event):
            return self.related_object
        # Also check activity_data for event reference
        event_id = self.task_data.get('linked_event_id')
        if event_id:
            return Event.objects.filter(id=event_id).first()
        return None

    @linked_event.setter
    def linked_event(self, event):
        if event:
            from django.contrib.contenttypes.models import ContentType
            self.content_type = ContentType.objects.get_for_model(event)
            self.object_id = event.id
            if not self.task_data:
                self.task_data = {}
            self.task_data['linked_event_id'] = str(event.id)

    @property
    def linked_workflow(self):
        """Legacy relationship to project_central.ProjectWorkflow."""
        from project_central.models import ProjectWorkflow
        if isinstance(self.related_object, ProjectWorkflow):
            return self.related_object
        workflow_id = self.task_data.get('linked_workflow_id')
        if workflow_id:
            return ProjectWorkflow.objects.filter(id=workflow_id).first()
        return None

    @linked_workflow.setter
    def linked_workflow(self, workflow):
        if workflow:
            from django.contrib.contenttypes.models import ContentType
            self.content_type = ContentType.objects.get_for_model(workflow)
            self.object_id = workflow.id
            if not self.task_data:
                self.task_data = {}
            self.task_data['linked_workflow_id'] = str(workflow.id)

    @property
    def is_overdue(self):
        """Return True if the task is overdue."""
        if self.status == self.STATUS_COMPLETED or not self.due_date:
            return False
        return self.due_date < timezone.now().date()

    @property
    def assignee_display_name(self):
        """Return a human-friendly assignee label."""
        members = list(self.assignees.all())
        if not members:
            return "Unassigned"

        labels = [
            (member.get_full_name() or member.username).strip()
            for member in members
        ]
        return ", ".join(filter(None, labels)) or "Unassigned"

    # Legacy domain-specific fields (stored in task_data JSON)
    @property
    def task_category(self):
        return self.task_data.get('task_category', '')

    @task_category.setter
    def task_category(self, value):
        if not self.task_data:
            self.task_data = {}
        self.task_data['task_category'] = value

    @property
    def assessment_phase(self):
        return self.task_data.get('assessment_phase', '')

    @assessment_phase.setter
    def assessment_phase(self, value):
        if not self.task_data:
            self.task_data = {}
        self.task_data['assessment_phase'] = value

    @property
    def deliverable_type(self):
        return self.task_data.get('deliverable_type', '')

    @deliverable_type.setter
    def deliverable_type(self, value):
        if not self.task_data:
            self.task_data = {}
        self.task_data['deliverable_type'] = value


class ProjectWorkflowProxy(WorkItem):
    """
    Proxy model for ProjectWorkflow → WorkItem migration.

    Filters to work_type='project' and provides the same interface
    as the legacy ProjectWorkflow model.
    """

    class Meta:
        proxy = True
        verbose_name = "Project Workflow (Legacy)"
        verbose_name_plural = "Project Workflows (Legacy)"

    objects = models.Manager()

    def __init__(self, *args, **kwargs):
        # Auto-set work_type to 'project'
        kwargs.setdefault('work_type', WorkItem.WORK_TYPE_PROJECT)
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Ensure work_type is always 'project'
        self.work_type = WorkItem.WORK_TYPE_PROJECT
        super().save(*args, **kwargs)

    # ========== LEGACY FIELD MAPPINGS ==========

    @property
    def current_stage(self):
        """Legacy workflow_stage field."""
        return self.project_data.get('workflow_stage', 'need_identification')

    @current_stage.setter
    def current_stage(self, value):
        if not self.project_data:
            self.project_data = {}
        self.project_data['workflow_stage'] = value

    @property
    def priority_level(self):
        """Map priority to legacy priority_level."""
        # WorkItem uses: low, medium, high, urgent, critical
        # ProjectWorkflow uses: low, medium, high, urgent, critical (same!)
        return self.priority

    @priority_level.setter
    def priority_level(self, value):
        self.priority = value

    @property
    def overall_progress(self):
        """Map progress to legacy overall_progress."""
        return self.progress

    @overall_progress.setter
    def overall_progress(self, value):
        self.progress = value

    @property
    def initiated_date(self):
        """Map start_date to legacy initiated_date."""
        return self.start_date

    @initiated_date.setter
    def initiated_date(self, value):
        self.start_date = value

    @property
    def target_completion_date(self):
        """Map due_date to legacy target_completion_date."""
        return self.due_date

    @target_completion_date.setter
    def target_completion_date(self, value):
        self.due_date = value

    @property
    def is_on_track(self):
        """Calculate on-track status from WorkItem status."""
        return self.status not in [
            WorkItem.STATUS_AT_RISK,
            WorkItem.STATUS_BLOCKED,
        ]

    @property
    def is_blocked(self):
        """Check if project is blocked."""
        return self.status == WorkItem.STATUS_BLOCKED

    # Additional legacy fields stored in project_data
    @property
    def estimated_budget(self):
        return self.project_data.get('estimated_budget')

    @estimated_budget.setter
    def estimated_budget(self, value):
        if not self.project_data:
            self.project_data = {}
        self.project_data['estimated_budget'] = str(value) if value else None

    @property
    def budget_approved(self):
        return self.project_data.get('budget_approved', False)

    @budget_approved.setter
    def budget_approved(self, value):
        if not self.project_data:
            self.project_data = {}
        self.project_data['budget_approved'] = value

    @property
    def notes(self):
        return self.description

    @notes.setter
    def notes(self, value):
        self.description = value


class EventProxy(WorkItem):
    """
    Proxy model for Event (coordination.Event) → WorkItem migration.

    Filters to work_type='activity' and provides the same interface
    as the legacy Event model.
    """

    class Meta:
        proxy = True
        verbose_name = "Event (Legacy)"
        verbose_name_plural = "Events (Legacy)"

    objects = models.Manager()

    def __init__(self, *args, **kwargs):
        # Handle legacy Event.__init__ parameters
        if 'start_datetime' in kwargs:
            start_dt = kwargs.pop('start_datetime')
            if start_dt:
                kwargs.setdefault('start_date', start_dt.date())
                kwargs.setdefault('start_time', start_dt.time())

        if 'end_datetime' in kwargs:
            end_dt = kwargs.pop('end_datetime')
            if end_dt:
                kwargs.setdefault('end_time', end_dt.time())
                # Handle multi-day events
                if 'start_date' in kwargs and end_dt.date() != kwargs['start_date']:
                    kwargs.setdefault('due_date', end_dt.date())

        if 'organized_by' in kwargs:
            organizer = kwargs.pop('organized_by')
            if organizer:
                kwargs.setdefault('created_by', organizer)

        # Auto-set work_type to 'activity'
        kwargs.setdefault('work_type', WorkItem.WORK_TYPE_ACTIVITY)
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Ensure work_type is always 'activity'
        self.work_type = WorkItem.WORK_TYPE_ACTIVITY
        super().save(*args, **kwargs)

    # ========== LEGACY FIELD MAPPINGS ==========

    @property
    def event_type(self):
        """Legacy event_type field."""
        return self.activity_data.get('event_type', 'other')

    @event_type.setter
    def event_type(self, value):
        if not self.activity_data:
            self.activity_data = {}
        self.activity_data['event_type'] = value

    @property
    def objectives(self):
        """Legacy objectives field."""
        return self.activity_data.get('objectives', '')

    @objectives.setter
    def objectives(self, value):
        if not self.activity_data:
            self.activity_data = {}
        self.activity_data['objectives'] = value

    @property
    def venue(self):
        """Legacy venue field."""
        return self.activity_data.get('venue', '')

    @venue.setter
    def venue(self, value):
        if not self.activity_data:
            self.activity_data = {}
        self.activity_data['venue'] = value

    @property
    def organizer(self):
        """Map created_by to legacy organizer."""
        return self.created_by

    @organizer.setter
    def organizer(self, value):
        self.created_by = value

    @property
    def end_date(self):
        """Map due_date to legacy end_date."""
        return self.due_date

    @end_date.setter
    def end_date(self, value):
        self.due_date = value


# ========== CUSTOM MANAGERS FOR PROXY MODELS ==========

class StaffTaskProxyManager(models.Manager):
    """Custom manager that filters to work_type='task'."""

    def get_queryset(self):
        return super().get_queryset().filter(work_type=WorkItem.WORK_TYPE_TASK)


class ProjectWorkflowProxyManager(models.Manager):
    """Custom manager that filters to work_type='project'."""

    def get_queryset(self):
        return super().get_queryset().filter(work_type=WorkItem.WORK_TYPE_PROJECT)


class EventProxyManager(models.Manager):
    """Custom manager that filters to work_type='activity'."""

    def get_queryset(self):
        return super().get_queryset().filter(work_type=WorkItem.WORK_TYPE_ACTIVITY)


# Apply custom managers
StaffTaskProxy.objects = StaffTaskProxyManager()
ProjectWorkflowProxy.objects = ProjectWorkflowProxyManager()
EventProxy.objects = EventProxyManager()
