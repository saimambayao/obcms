"""Task automation service for creating tasks from templates."""

from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Domain constants (for WorkItem.task_data.domain field)
DOMAIN_ASSESSMENT = 'assessment'
DOMAIN_COORDINATION = 'coordination'
DOMAIN_MONITORING = 'monitoring'
DOMAIN_POLICY = 'policy'
DOMAIN_SERVICES = 'services'
DOMAIN_GENERAL = 'general'


def create_tasks_from_template(template_name, **kwargs):
    """
    Create task set from template.

    NOTE: DISABLED - TaskTemplate model was removed during WorkItem migration.
    This function is kept for backward compatibility but always returns empty list.

    Args:
        template_name: Name of TaskTemplate
        **kwargs: Domain-specific FK values (e.g., related_assessment=assessment_obj)
                 Also accepts: start_date, created_by

    Returns:
        Empty list (TaskTemplate system removed)
    """
    # DISABLED: TaskTemplate model doesn't exist
    # See: WORKITEM_MIGRATION_COMPLETE.md
    return []


# ========== SIGNAL HANDLERS FOR AUTOMATED TASK GENERATION ==========


@receiver(post_save, sender="mana.Assessment")
def create_assessment_tasks(sender, instance, created, **kwargs):
    """
    Auto-create tasks when MANA Assessment created.

    DISABLED: TaskTemplate model doesn't exist (removed during WorkItem migration).
    """
    return


@receiver(post_save, sender="mana.BaselineStudy")
def create_baseline_tasks(sender, instance, created, **kwargs):
    """
    Auto-create tasks when Baseline Study created.

    DISABLED: TaskTemplate model doesn't exist (removed during WorkItem migration).
    """
    return


@receiver(post_save, sender="mana.WorkshopActivity")
def create_workshop_tasks(sender, instance, created, **kwargs):
    """
    Auto-create tasks when Workshop Activity created.

    DISABLED: TaskTemplate model doesn't exist (removed during WorkItem migration).
    """
    return


# Event model removed - WorkItem handles activities now
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md


@receiver(post_save, sender="coordination.Partnership")
def create_partnership_tasks(sender, instance, created, **kwargs):
    """
    Auto-create tasks when Partnership created.

    DISABLED: TaskTemplate model doesn't exist (removed during WorkItem migration).
    """
    return


@receiver(post_save, sender="policy_tracking.PolicyRecommendation")
def create_policy_tasks(sender, instance, created, **kwargs):
    """
    Auto-create tasks when Policy created.

    DISABLED: TaskTemplate model doesn't exist (removed during WorkItem migration).
    """
    return


@receiver(post_save, sender="policy_tracking.PolicyImplementationMilestone")
def create_milestone_tasks(sender, instance, created, **kwargs):
    """Auto-create task when PolicyImplementationMilestone created."""
    if not created:
        return

    from django.contrib.contenttypes.models import ContentType
    from common.work_item_model import WorkItem

    task_data = {
        'domain': DOMAIN_POLICY,
        'policy_phase': 'implementation',  # POLICY_PHASE_IMPLEMENTATION
    }

    # Use GenericForeignKey to link to the milestone
    content_type = ContentType.objects.get_for_model(instance)

    WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title=f"Complete: {instance.title}",
        description=instance.description,
        content_type=content_type,
        object_id=instance.pk,
        task_data=task_data,
        priority=(
            WorkItem.PRIORITY_HIGH
            if getattr(instance, "is_critical", False)
            else WorkItem.PRIORITY_MEDIUM
        ),
        due_date=instance.target_date,
        status=WorkItem.STATUS_NOT_STARTED,
    )


@receiver(post_save, sender="monitoring.MonitoringEntry")
def create_ppa_tasks(sender, instance, created, **kwargs):
    """
    Auto-create tasks when PPA created.

    NOTE: Currently disabled because TaskTemplate model doesn't exist.
    TaskTemplate was removed during WorkItem migration but signal still references it.
    This signal needs to be updated to use WorkItem model directly or removed entirely.

    See: WORKITEM_MIGRATION_COMPLETE.md
    """
    # DISABLED: TaskTemplate model doesn't exist, causes ImportError in create_tasks_from_template
    # TODO: Either update to use WorkItem directly or remove this signal
    return

    # if not created or instance.category not in ["moa_ppa", "oobc_ppa"]:
    #     return
    #
    # create_tasks_from_template(
    #     template_name="ppa_budget_cycle",
    #     related_ppa=instance,
    #     ppa_title=instance.title,
    #     start_date=instance.start_date or timezone.now().date(),
    #     created_by=getattr(instance, "created_by", None),
    # )


@receiver(post_save, sender="services.ServiceApplication")
def create_application_tasks(sender, instance, created, **kwargs):
    """Auto-create tasks when ServiceApplication submitted."""
    if not created or instance.status != "submitted":
        return

    from django.contrib.contenttypes.models import ContentType
    from common.work_item_model import WorkItem

    task_data = {
        'domain': DOMAIN_SERVICES,
        'service_phase': 'review',  # SERVICE_PHASE_REVIEW
    }

    # Use GenericForeignKey to link to the service application
    content_type = ContentType.objects.get_for_model(instance)

    WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_TASK,
        title=f"Review application: {instance.applicant_name}",
        description=f"Review service application for {instance.service.title}",
        content_type=content_type,
        object_id=instance.pk,
        task_data=task_data,
        priority=WorkItem.PRIORITY_MEDIUM,
        due_date=timezone.now().date() + timedelta(days=7),
        status=WorkItem.STATUS_NOT_STARTED,
    )
