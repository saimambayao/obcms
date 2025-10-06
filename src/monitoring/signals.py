"""
Signal handlers for automatic PPA-WorkItem synchronization.

This module implements Django signals that handle:
1. Automatic execution_project creation when PPA approval_status changes to 'technical_review'
2. Automatic execution_project activation when approval_status changes to 'enacted'
3. Bidirectional sync from WorkItem to PPA when WorkItem is saved

Signal flow:
    MonitoringEntry save (approval_status changed)
        -> pre_save: track_approval_status_change
        -> post_save: handle_ppa_approval_workflow
            - technical_review: create execution_project
            - enacted: activate execution_project

    WorkItem save
        -> post_save: sync_workitem_to_ppa
            - sync progress/status to PPA if auto_sync enabled

Documentation: docs/improvements/PPA_WORKITEM_INTEGRATION.md
"""

import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@receiver(pre_save, sender='monitoring.MonitoringEntry')
def track_approval_status_change(sender, instance, **kwargs):
    """
    Track approval_status changes before save.

    Stores the previous approval_status in instance._old_approval_status
    so post_save handler can detect status transitions.

    Args:
        sender: MonitoringEntry model class
        instance: MonitoringEntry instance being saved
        **kwargs: Additional signal arguments
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_approval_status = old_instance.approval_status
        except sender.DoesNotExist:
            instance._old_approval_status = None
    else:
        instance._old_approval_status = None


@receiver(post_save, sender='monitoring.MonitoringEntry')
def handle_ppa_approval_workflow(sender, instance, created, **kwargs):
    """
    Handle automatic PPA-WorkItem workflow automation.

    Triggers:
    1. approval_status changes to 'technical_review' + enable_workitem_tracking=True
       -> Auto-creates execution_project using budget_distribution_policy template

    2. approval_status changes to 'enacted' + execution_project exists
       -> Activates execution_project (status -> 'in_progress')

    Args:
        sender: MonitoringEntry model class
        instance: MonitoringEntry instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments
    """
    # Skip automation for newly created instances (no status change yet)
    if created:
        return

    # Get old approval status
    old_approval_status = getattr(instance, '_old_approval_status', None)

    # Check if approval_status changed
    if old_approval_status == instance.approval_status:
        return

    # ========== TRIGGER 1: Technical Review -> Create execution_project ==========
    if instance.approval_status == instance.APPROVAL_STATUS_TECHNICAL_REVIEW:
        # Only auto-create if enable_workitem_tracking is True
        if not instance.enable_workitem_tracking:
            logger.info(
                f"PPA '{instance.title}' (ID: {instance.id}) reached technical_review, "
                f"but enable_workitem_tracking is False. Skipping auto-creation."
            )
            return

        # Check if execution_project already exists
        if instance.execution_project:
            logger.info(
                f"PPA '{instance.title}' (ID: {instance.id}) already has execution_project. "
                f"Skipping auto-creation."
            )
            return

        # Create execution_project using budget_distribution_policy as template
        try:
            from common.work_item_model import WorkItem

            # Determine structure template from budget_distribution_policy
            structure_template = instance.budget_distribution_policy or 'manual'

            # Use the MonitoringEntry method to create execution project
            execution_project = instance.create_execution_project(
                structure_template=structure_template,
                created_by=instance.reviewed_by or instance.updated_by
            )

            # Link execution_project to MonitoringEntry via OneToOne
            instance.execution_project = execution_project
            instance.save(update_fields=['execution_project', 'updated_at'])

            logger.info(
                f"✓ Auto-created execution_project for PPA '{instance.title}' (ID: {instance.id}) "
                f"using template '{structure_template}'. "
                f"Project ID: {execution_project.id}"
            )

        except ValidationError as e:
            logger.error(
                f"✗ Failed to auto-create execution_project for PPA '{instance.title}' "
                f"(ID: {instance.id}): {e}"
            )

        except Exception as e:
            logger.exception(
                f"✗ Unexpected error creating execution_project for PPA '{instance.title}' "
                f"(ID: {instance.id}): {e}"
            )

    # ========== TRIGGER 2: Enacted -> Activate execution_project ==========
    elif instance.approval_status == instance.APPROVAL_STATUS_ENACTED:
        if not instance.execution_project:
            logger.warning(
                f"PPA '{instance.title}' (ID: {instance.id}) reached 'enacted' status, "
                f"but no execution_project exists. Cannot activate."
            )
            return

        try:
            from common.work_item_model import WorkItem

            execution_project = instance.execution_project

            # Only activate if not already in progress
            if execution_project.status == WorkItem.STATUS_NOT_STARTED:
                execution_project.status = WorkItem.STATUS_IN_PROGRESS
                execution_project.save(update_fields=['status', 'updated_at'])

                logger.info(
                    f"✓ Auto-activated execution_project for PPA '{instance.title}' "
                    f"(ID: {instance.id}). "
                    f"Project ID: {execution_project.id}, Status: in_progress"
                )
            else:
                logger.info(
                    f"Execution_project for PPA '{instance.title}' (ID: {instance.id}) "
                    f"already has status '{execution_project.status}'. Skipping activation."
                )

        except Exception as e:
            logger.exception(
                f"✗ Unexpected error activating execution_project for PPA '{instance.title}' "
                f"(ID: {instance.id}): {e}"
            )


@receiver(post_save, sender='common.WorkItem')
def sync_workitem_to_ppa(sender, instance, created, **kwargs):
    """
    Sync WorkItem changes back to PPA.

    Triggers bidirectional sync when a WorkItem is saved:
    - Calls work_item.sync_to_ppa() to sync progress/status
    - Only syncs if WorkItem is the execution_project (root level)
    - Respects auto_sync_progress and auto_sync_status flags

    Args:
        sender: WorkItem model class
        instance: WorkItem instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments
    """
    # Skip sync for newly created work items (no progress to sync yet)
    if created:
        return

    # Only sync root-level projects that are execution_projects
    if instance.parent is not None:
        return

    # Check if this is an execution_project for a PPA
    if not hasattr(instance, 'ppa_source'):
        return

    try:
        # Call WorkItem's sync_to_ppa method
        sync_result = instance.sync_to_ppa()

        if sync_result['progress_synced'] or sync_result['status_synced']:
            logger.info(
                f"✓ Synced WorkItem '{instance.title}' (ID: {instance.id}) to PPA "
                f"(ID: {sync_result['ppa_id']}). "
                f"Progress synced: {sync_result['progress_synced']}, "
                f"Status synced: {sync_result['status_synced']}"
            )
        else:
            logger.debug(
                f"WorkItem '{instance.title}' (ID: {instance.id}) sync skipped. "
                f"Reason: {sync_result.get('message', 'Auto-sync disabled')}"
            )

    except Exception as e:
        logger.exception(
            f"✗ Unexpected error syncing WorkItem '{instance.title}' "
            f"(ID: {instance.id}) to PPA: {e}"
        )
