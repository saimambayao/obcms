"""Signal handlers for coordination app.

Provides automation for:
- Event creation and updates
- Project workflow stage transitions
- Task generation triggers
- Notification coordination
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import logging

from .models import Event

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Event)
def handle_event_creation(sender, instance, created, **kwargs):
    """
    Handle post-save event creation.

    Logs event creation and provides extension point for notifications.
    Auto-task generation is handled in Event.save() via _auto_generate_tasks.
    """
    if created:
        # Log event creation
        logger.info(
            f"Event created: {instance.title} (ID: {instance.id}, Type: {instance.event_type})"
        )

        # Log project activity details
        if instance.is_project_activity and instance.related_project:
            logger.info(
                f"Project activity created for '{instance.related_project}' "
                f"(Activity type: {instance.project_activity_type or 'generic'})"
            )

            # Log project lead information for future notification implementation
            project_lead = instance.related_project.project_lead
            if project_lead:
                logger.info(
                    f"Project lead: {project_lead.get_full_name() or project_lead.username}"
                )
                # TODO: Implement notification system
                # - Send email to project lead about new activity
                # - Create notification in user dashboard
                # - Add to project activity feed


@receiver(pre_save, sender=Event)
def handle_event_update(sender, instance, **kwargs):
    """
    Handle pre-save event updates.

    Detects and logs:
    - Status changes (draft -> confirmed, etc.)
    - Project linkage changes
    - Date changes
    """
    if instance.pk:
        try:
            old_instance = Event.objects.get(pk=instance.pk)

            # Detect status changes
            if old_instance.status != instance.status:
                logger.info(
                    f"Event {instance.id} status changed: "
                    f"{old_instance.status} → {instance.status}"
                )

                # Log confirmation events
                if instance.status == "confirmed":
                    logger.info(
                        f"Event {instance.id} confirmed: {instance.title} "
                        f"on {instance.start_date}"
                    )
                    # TODO: Send confirmation notifications
                    # - Notify participants
                    # - Update project timeline if project activity
                    # - Add to confirmed events calendar

                # Log cancellation events
                elif instance.status == "cancelled":
                    logger.info(
                        f"Event {instance.id} cancelled: {instance.title} "
                        f"(Reason: {instance.notes or 'Not specified'})"
                    )
                    # TODO: Handle cancellation
                    # - Notify participants
                    # - Cancel related tasks
                    # - Update project schedule

            # Detect project linkage changes
            if old_instance.related_project != instance.related_project:
                old_project = old_instance.related_project
                new_project = instance.related_project
                logger.info(
                    f"Event {instance.id} project changed: "
                    f"{old_project or 'None'} → {new_project or 'None'}"
                )
                # TODO: Handle project change
                # - Update related tasks
                # - Notify old and new project leads
                # - Update project activity feeds

            # Detect date changes
            if old_instance.start_date != instance.start_date:
                logger.info(
                    f"Event {instance.id} rescheduled: "
                    f"{old_instance.start_date} → {instance.start_date}"
                )
                # TODO: Handle rescheduling
                # - Notify participants
                # - Update related task due dates
                # - Send calendar updates

        except Event.DoesNotExist:
            # Instance exists but not in database yet (shouldn't happen but handle gracefully)
            logger.warning(
                f"Event {instance.pk} not found during pre_save signal (possibly mid-transaction)"
            )


# Project Workflow signal handlers
# Import at function level to avoid circular imports
try:
    from project_central.models import ProjectWorkflow

    @receiver(pre_save, sender=ProjectWorkflow)
    def handle_workflow_stage_change(sender, instance, **kwargs):
        """
        Handle workflow stage progression.

        Automatically creates milestone review activities when entering review stage.
        Provides extension point for other stage-based automation.
        """
        if instance.pk:
            try:
                old_instance = ProjectWorkflow.objects.get(pk=instance.pk)

                if old_instance.current_stage != instance.current_stage:
                    logger.info(
                        f"Workflow {instance.id} stage changed: "
                        f"{old_instance.current_stage} → {instance.current_stage}"
                    )

                    # Auto-create milestone review when entering review stage
                    if instance.current_stage == "review":
                        from datetime import date, timedelta

                        # Create milestone review activity
                        review_event = Event.objects.create(
                            title=f"Milestone Review: {instance.primary_need.title}",
                            event_type="meeting",
                            related_project=instance,
                            is_project_activity=True,
                            project_activity_type="milestone_review",
                            start_date=date.today() + timedelta(days=7),
                            status="draft",
                            notes=(
                                f"Automatically scheduled milestone review for "
                                f"project entering review stage."
                            ),
                            created_by=instance.project_lead or instance.created_by,
                        )

                        # Enable auto-task generation for this event
                        review_event._auto_generate_tasks = True
                        review_event.save()

                        logger.info(
                            f"Auto-created milestone review event {review_event.id} "
                            f"for workflow {instance.id}"
                        )

                    # Log other stage transitions for future automation
                    elif instance.current_stage == "implementation":
                        logger.info(
                            f"Workflow {instance.id} entered implementation stage - "
                            f"ready for progress tracking"
                        )
                        # TODO: Create implementation kickoff activity
                        # TODO: Set up progress review schedule

                    elif instance.current_stage == "completed":
                        logger.info(
                            f"Workflow {instance.id} completed - "
                            f"ready for closeout activities"
                        )
                        # TODO: Create project closeout activity
                        # TODO: Trigger final documentation tasks

            except ProjectWorkflow.DoesNotExist:
                logger.warning(
                    f"Workflow {instance.pk} not found during pre_save signal"
                )

except ImportError:
    # project_central app not installed or not available
    logger.info("project_central app not available - workflow signals not registered")
