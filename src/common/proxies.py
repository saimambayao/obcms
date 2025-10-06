"""Proxy models for backward compatibility with legacy code.

These proxies allow legacy code to continue using the old model names
while the underlying data is stored in the unified WorkItem model.

See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
"""

from common.work_item_model import WorkItem


class StaffTaskProxy(WorkItem):
    """Proxy model for StaffTask (WorkItem with work_type='task')."""

    class Meta:
        proxy = True
        verbose_name = "Staff Task"
        verbose_name_plural = "Staff Tasks"

    # Status constants for backward compatibility
    STATUS_NOT_STARTED = WorkItem.STATUS_NOT_STARTED
    STATUS_IN_PROGRESS = WorkItem.STATUS_IN_PROGRESS
    STATUS_COMPLETED = WorkItem.STATUS_COMPLETED
    STATUS_AT_RISK = WorkItem.STATUS_AT_RISK
    STATUS_BLOCKED = WorkItem.STATUS_BLOCKED
    STATUS_CANCELLED = WorkItem.STATUS_CANCELLED

    # Priority constants for backward compatibility
    PRIORITY_LOW = WorkItem.PRIORITY_LOW
    PRIORITY_MEDIUM = WorkItem.PRIORITY_MEDIUM
    PRIORITY_HIGH = WorkItem.PRIORITY_HIGH
    PRIORITY_URGENT = WorkItem.PRIORITY_URGENT
    PRIORITY_CRITICAL = WorkItem.PRIORITY_CRITICAL

    # Choices for backward compatibility
    STATUS_CHOICES = WorkItem.STATUS_CHOICES
    PRIORITY_CHOICES = WorkItem.PRIORITY_CHOICES

    # Domain constants for backward compatibility
    DOMAIN_ASSESSMENT = 'assessment'
    DOMAIN_COORDINATION = 'coordination'
    DOMAIN_MONITORING = 'monitoring'
    DOMAIN_POLICY = 'policy'
    DOMAIN_GENERAL = 'general'

    # Domain choices for backward compatibility
    DOMAIN_CHOICES = [
        (DOMAIN_GENERAL, 'General'),
        (DOMAIN_ASSESSMENT, 'Assessment'),
        (DOMAIN_COORDINATION, 'Coordination'),
        (DOMAIN_MONITORING, 'Monitoring'),
        (DOMAIN_POLICY, 'Policy'),
    ]

    def save(self, *args, **kwargs):
        """Ensure work_type is set to 'task' on save."""
        if not self.work_type:
            self.work_type = 'task'
        return super().save(*args, **kwargs)


class ProjectWorkflowProxy(WorkItem):
    """Proxy model for ProjectWorkflow (WorkItem with work_type='workflow')."""

    class Meta:
        proxy = True
        verbose_name = "Project Workflow"
        verbose_name_plural = "Project Workflows"

    # Status constants (inherit from WorkItem)
    STATUS_NOT_STARTED = WorkItem.STATUS_NOT_STARTED
    STATUS_IN_PROGRESS = WorkItem.STATUS_IN_PROGRESS
    STATUS_COMPLETED = WorkItem.STATUS_COMPLETED
    STATUS_AT_RISK = WorkItem.STATUS_AT_RISK
    STATUS_BLOCKED = WorkItem.STATUS_BLOCKED
    STATUS_CANCELLED = WorkItem.STATUS_CANCELLED
    STATUS_CHOICES = WorkItem.STATUS_CHOICES

    # Priority constants (inherit from WorkItem)
    PRIORITY_LOW = WorkItem.PRIORITY_LOW
    PRIORITY_MEDIUM = WorkItem.PRIORITY_MEDIUM
    PRIORITY_HIGH = WorkItem.PRIORITY_HIGH
    PRIORITY_URGENT = WorkItem.PRIORITY_URGENT
    PRIORITY_CRITICAL = WorkItem.PRIORITY_CRITICAL
    PRIORITY_CHOICES = WorkItem.PRIORITY_CHOICES

    # Legacy PRIORITY_LEVELS for backward compatibility with old code
    PRIORITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    # Workflow stages for backward compatibility
    WORKFLOW_STAGES = [
        ('need_identification', 'Need Identification'),
        ('need_validation', 'Need Validation'),
        ('policy_linkage', 'Policy Linkage'),
        ('mao_coordination', 'MAO Coordination'),
        ('budget_planning', 'Budget Planning'),
        ('approval', 'Approval Process'),
        ('implementation', 'Implementation'),
        ('monitoring', 'Monitoring & Evaluation'),
        ('completion', 'Completion'),
    ]

    @property
    def current_stage(self):
        """Get current workflow stage from project_data."""
        return self.project_data.get('workflow_stage', 'need_identification') if self.project_data else 'need_identification'

    @current_stage.setter
    def current_stage(self, value):
        """Set current workflow stage in project_data."""
        if not self.project_data:
            self.project_data = {}
        self.project_data['workflow_stage'] = value

    def save(self, *args, **kwargs):
        """Ensure work_type is set to 'workflow' on save."""
        if not self.work_type:
            self.work_type = 'workflow'
        return super().save(*args, **kwargs)


class EventProxy(WorkItem):
    """Proxy model for Event (WorkItem with work_type='activity')."""

    class Meta:
        proxy = True
        verbose_name = "Event"
        verbose_name_plural = "Events"

    # Status constants (inherit from WorkItem)
    STATUS_NOT_STARTED = WorkItem.STATUS_NOT_STARTED
    STATUS_IN_PROGRESS = WorkItem.STATUS_IN_PROGRESS
    STATUS_COMPLETED = WorkItem.STATUS_COMPLETED
    STATUS_AT_RISK = WorkItem.STATUS_AT_RISK
    STATUS_BLOCKED = WorkItem.STATUS_BLOCKED
    STATUS_CANCELLED = WorkItem.STATUS_CANCELLED
    STATUS_CHOICES = WorkItem.STATUS_CHOICES

    # Priority constants (inherit from WorkItem)
    PRIORITY_LOW = WorkItem.PRIORITY_LOW
    PRIORITY_MEDIUM = WorkItem.PRIORITY_MEDIUM
    PRIORITY_HIGH = WorkItem.PRIORITY_HIGH
    PRIORITY_URGENT = WorkItem.PRIORITY_URGENT
    PRIORITY_CRITICAL = WorkItem.PRIORITY_CRITICAL
    PRIORITY_CHOICES = WorkItem.PRIORITY_CHOICES

    # Event type constants for backward compatibility
    EVENT_CULTURAL = "cultural"
    EVENT_RELIGIOUS = "religious"
    EVENT_MEETING = "meeting"
    EVENT_TRAINING = "training"
    EVENT_DISASTER = "disaster"
    EVENT_OTHER = "other"

    # Event type choices for backward compatibility
    EVENT_TYPE_CHOICES = [
        (EVENT_CULTURAL, "Cultural Celebration"),
        (EVENT_RELIGIOUS, "Religious Observance"),
        (EVENT_MEETING, "Community Meeting"),
        (EVENT_TRAINING, "Community Training"),
        (EVENT_DISASTER, "Disaster/Emergency"),
        (EVENT_OTHER, "Other"),
    ]

    def save(self, *args, **kwargs):
        """Ensure work_type is set to 'activity' on save."""
        if not self.work_type:
            self.work_type = 'activity'
        return super().save(*args, **kwargs)
