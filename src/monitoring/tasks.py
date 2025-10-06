"""Celery tasks for Monitoring & Evaluation background jobs."""

from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from common.models import WorkItem

from .models import MonitoringEntryWorkflowStage


@shared_task(name="monitoring.send_workflow_deadline_reminders")
def send_workflow_deadline_reminders():
    """
    Send reminders for upcoming workflow stage deadlines.

    Runs daily to notify stakeholders of:
    - Deadlines in 3 days
    - Deadlines in 7 days
    - Overdue stages
    """
    today = timezone.now().date()
    three_days = today + timedelta(days=3)
    seven_days = today + timedelta(days=7)

    # Find stages approaching deadline
    upcoming_3_days = MonitoringEntryWorkflowStage.objects.filter(
        due_date=three_days,
        status__in=[
            MonitoringEntryWorkflowStage.STATUS_NOT_STARTED,
            MonitoringEntryWorkflowStage.STATUS_IN_PROGRESS,
        ],
    ).select_related("entry", "owner_team", "owner_organization")

    upcoming_7_days = MonitoringEntryWorkflowStage.objects.filter(
        due_date=seven_days,
        status__in=[
            MonitoringEntryWorkflowStage.STATUS_NOT_STARTED,
            MonitoringEntryWorkflowStage.STATUS_IN_PROGRESS,
        ],
    ).select_related("entry", "owner_team", "owner_organization")

    # Find overdue stages
    overdue_stages = MonitoringEntryWorkflowStage.objects.filter(
        due_date__lt=today,
        status__in=[
            MonitoringEntryWorkflowStage.STATUS_NOT_STARTED,
            MonitoringEntryWorkflowStage.STATUS_IN_PROGRESS,
        ],
    ).select_related("entry", "owner_team", "owner_organization")

    reminder_count = 0

    # Process 3-day reminders
    for stage in upcoming_3_days:
        _send_workflow_reminder(
            stage,
            urgency="high",
            message=f"Deadline in 3 days: {stage.get_stage_display()} for {stage.entry.title}",
        )
        reminder_count += 1

    # Process 7-day reminders
    for stage in upcoming_7_days:
        _send_workflow_reminder(
            stage,
            urgency="medium",
            message=f"Deadline in 7 days: {stage.get_stage_display()} for {stage.entry.title}",
        )
        reminder_count += 1

    # Process overdue reminders
    for stage in overdue_stages:
        days_overdue = (today - stage.due_date).days
        _send_workflow_reminder(
            stage,
            urgency="critical",
            message=f"OVERDUE ({days_overdue} days): {stage.get_stage_display()} for {stage.entry.title}",
        )
        reminder_count += 1

    return {
        "status": "completed",
        "reminders_sent": reminder_count,
        "three_day_count": upcoming_3_days.count(),
        "seven_day_count": upcoming_7_days.count(),
        "overdue_count": overdue_stages.count(),
    }


@shared_task(name="monitoring.send_task_assignment_reminders")
def send_task_assignment_reminders():
    """
    Send reminders for task assignments.

    Runs daily to notify assignees of:
    - Tasks due in 2 days
    - Tasks due in 5 days
    - Overdue tasks
    """
    from django.contrib.contenttypes.models import ContentType
    from .models import MonitoringEntry

    today = timezone.now().date()
    two_days = today + timedelta(days=2)
    five_days = today + timedelta(days=5)

    monitoring_statuses = [
        "not_started",
        "in_progress",
        "at_risk",
    ]

    # Get ContentType for MonitoringEntry
    monitoring_ct = ContentType.objects.get_for_model(MonitoringEntry)

    # Get WorkItems (tasks) linked to MonitoringEntry with monitoring domain
    base_queryset = (
        WorkItem.objects.filter(
            work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK],
            content_type=monitoring_ct,
            due_date__isnull=False,
        )
        .select_related("created_by")
        .prefetch_related("assignees")
    )

    # Further filter to monitoring domain tasks (stored in task_data JSON)
    monitoring_tasks = [
        task for task in base_queryset
        if task.task_data and task.task_data.get("domain") == "monitoring"
    ]

    # Filter by due date and status
    upcoming_2_days = [
        task for task in monitoring_tasks
        if task.due_date == two_days and task.status in monitoring_statuses
    ]

    upcoming_5_days = [
        task for task in monitoring_tasks
        if task.due_date == five_days and task.status in monitoring_statuses
    ]

    overdue_tasks = [
        task for task in monitoring_tasks
        if task.due_date < today and task.status in monitoring_statuses
    ]

    reminder_count = 0

    # Process 2-day reminders
    for task in upcoming_2_days:
        # Get related PPA via GenericForeignKey
        related_ppa = task.content_object if task.content_type == monitoring_ct else None
        ppa_title = getattr(related_ppa, 'title', 'Unlinked PPA') if related_ppa else 'Unlinked PPA'

        _send_task_reminder(
            task,
            urgency="high",
            message=f"Deadline in 2 days: {task.title} for {ppa_title}",
        )
        reminder_count += 1

    # Process 5-day reminders
    for task in upcoming_5_days:
        # Get related PPA via GenericForeignKey
        related_ppa = task.content_object if task.content_type == monitoring_ct else None
        ppa_title = getattr(related_ppa, 'title', 'Unlinked PPA') if related_ppa else 'Unlinked PPA'

        _send_task_reminder(
            task,
            urgency="medium",
            message=f"Deadline in 5 days: {task.title} for {ppa_title}",
        )
        reminder_count += 1

    # Process overdue reminders
    for task in overdue_tasks:
        days_overdue = (today - task.due_date).days
        # Get related PPA via GenericForeignKey
        related_ppa = task.content_object if task.content_type == monitoring_ct else None
        ppa_title = getattr(related_ppa, 'title', 'Unlinked PPA') if related_ppa else 'Unlinked PPA'

        _send_task_reminder(
            task,
            urgency="critical",
            message=f"OVERDUE ({days_overdue} days): {task.title} for {ppa_title}",
        )
        reminder_count += 1

    return {
        "status": "completed",
        "reminders_sent": reminder_count,
        "two_day_count": len(upcoming_2_days),
        "five_day_count": len(upcoming_5_days),
        "overdue_count": len(overdue_tasks),
    }


def _send_workflow_reminder(stage, urgency, message):
    """
    Send email reminder for workflow stage deadline.

    Args:
        stage: MonitoringEntryWorkflowStage instance
        urgency: str - "critical", "high", "medium"
        message: str - notification message
    """
    # Determine recipients
    recipients = []

    # Add owner team members (if available)
    if stage.owner_team:
        team_emails = list(
            stage.owner_team.members.values_list("user__email", flat=True)
        )
        recipients.extend(team_emails)

    # Add organization contacts (if available)
    if stage.owner_organization:
        # Assuming organization has a contact_email field
        if hasattr(stage.owner_organization, "contact_email"):
            recipients.append(stage.owner_organization.contact_email)

    # Filter out None and empty strings
    recipients = [email for email in recipients if email]

    if not recipients:
        # Log if no recipients found
        print(f"[WORKFLOW REMINDER] No recipients for stage {stage.id}: {message}")
        return

    # Construct email
    subject = f"[{urgency.upper()}] Workflow Deadline Reminder"
    email_message = f"""
{message}

Entry: {stage.entry.title}
Stage: {stage.get_stage_display()}
Status: {stage.get_status_display()}
Due Date: {stage.due_date}
Notes: {stage.notes or "No notes"}

Please review and take action as needed.

---
Office for Other Bangsamoro Communities
Planning & Budgeting System
"""

    try:
        send_mail(
            subject=subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        print(f"[WORKFLOW REMINDER] Sent to {', '.join(recipients)}: {message}")
    except Exception as e:
        print(f"[WORKFLOW REMINDER] Failed to send email: {e}")


def _send_task_reminder(task, urgency, message):
    """Send email reminder for monitoring WorkItem task deadlines."""

    recipients = [user.email for user in task.assignees.all() if user.email]

    if not recipients and task.created_by and task.created_by.email:
        recipients.append(task.created_by.email)

    if not recipients:
        print(f"[TASK REMINDER] No recipients for task {task.pk}: {message}")
        return

    # Get related PPA via GenericForeignKey
    from django.contrib.contenttypes.models import ContentType
    from .models import MonitoringEntry

    monitoring_ct = ContentType.objects.get_for_model(MonitoringEntry)
    related_ppa = task.content_object if task.content_type == monitoring_ct else None
    entry_title = getattr(related_ppa, "title", "Unlinked PPA") if related_ppa else "Unlinked PPA"

    # Extract task_role from task_data JSON field
    task_role = task.task_data.get("task_role", "Not specified") if task.task_data else "Not specified"

    subject = f"[{urgency.upper()}] Task Deadline Reminder"
    email_message = f"""
{message}

PPA: {entry_title}
Task: {task.title}
Role: {task_role}
Status: {task.get_status_display()}
Priority: {task.get_priority_display()}
Due Date: {task.due_date}

Description:
{task.description or "No description"}

Notes:
{task.notes or "No notes"}

Please complete this task as soon as possible.

---
Office for Other Bangsamoro Communities
Planning & Budgeting System
"""

    try:
        send_mail(
            subject=subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        print(f"[TASK REMINDER] Sent to {', '.join(recipients)}: {message}")
    except Exception as e:
        print(f"[TASK REMINDER] Failed to send email: {e}")


@shared_task(
    name="monitoring.auto_sync_ppa_progress",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def auto_sync_ppa_progress(self):
    """
    Automatically sync PPA progress from WorkItem completion status.

    This task runs nightly at 2:00 AM to synchronize progress from WorkItem
    execution projects to MonitoringEntry instances. Only PPAs with
    enable_workitem_tracking=True and auto_sync_progress=True are processed.

    The task calculates progress based on completed WorkItem descendants
    (activities/tasks) and updates the MonitoringEntry.progress field.

    Returns:
        dict: Sync results summary
            - status: "completed" or "failed"
            - total_processed: int
            - total_updated: int
            - total_unchanged: int
            - total_errors: int
            - errors: list of error messages

    Retry Logic:
        - Max retries: 3
        - Retry delay: 5 minutes
        - Retries on database errors, connection issues

    Example Result:
        {
            "status": "completed",
            "total_processed": 45,
            "total_updated": 12,
            "total_unchanged": 30,
            "total_errors": 3,
            "errors": ["PPA abc123: WorkItem not found", ...]
        }
    """
    import logging
    from .models import MonitoringEntry
    from .utils.email import send_progress_sync_notification

    logger = logging.getLogger(__name__)
    logger.info("[AUTO SYNC] Starting nightly PPA progress sync from WorkItems")

    try:
        # Find PPAs with WorkItem tracking enabled and auto-sync enabled
        ppas_to_sync = MonitoringEntry.objects.filter(
            enable_workitem_tracking=True,
            auto_sync_progress=True,
            status__in=['planning', 'ongoing']  # Only active PPAs
        ).select_related('implementing_moa', 'created_by')

        total_processed = 0
        total_updated = 0
        total_unchanged = 0
        total_errors = 0
        errors = []

        for ppa in ppas_to_sync:
            total_processed += 1

            try:
                # Store old progress for comparison
                old_progress = ppa.progress

                # Sync progress from WorkItem
                new_progress = ppa.sync_progress_from_workitem()

                if new_progress != old_progress:
                    total_updated += 1
                    logger.info(
                        f"[AUTO SYNC] Updated PPA {ppa.id}: "
                        f"{old_progress}% → {new_progress}% ({ppa.title})"
                    )

                    # Send notification if significant change (handled by email utility)
                    send_progress_sync_notification(ppa, old_progress, new_progress)
                else:
                    total_unchanged += 1

            except Exception as e:
                total_errors += 1
                error_msg = f"PPA {ppa.id}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"[AUTO SYNC] Error syncing {ppa.id}: {e}", exc_info=True)

        # Final summary
        result = {
            "status": "completed",
            "total_processed": total_processed,
            "total_updated": total_updated,
            "total_unchanged": total_unchanged,
            "total_errors": total_errors,
            "errors": errors[:10]  # Limit to first 10 errors
        }

        logger.info(
            f"[AUTO SYNC] Completed: {total_processed} processed, "
            f"{total_updated} updated, {total_errors} errors"
        )

        return result

    except Exception as e:
        logger.error(f"[AUTO SYNC] Fatal error in auto_sync_ppa_progress: {e}", exc_info=True)

        # Retry on database errors
        if "database" in str(e).lower() or "connection" in str(e).lower():
            raise self.retry(exc=e)

        return {
            "status": "failed",
            "error": str(e),
            "total_processed": 0,
            "total_updated": 0,
            "total_unchanged": 0,
            "total_errors": 0,
            "errors": [str(e)]
        }


@shared_task(
    name="monitoring.detect_budget_variances",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def detect_budget_variances(self):
    """
    Detect budget variances and create alerts for overruns.

    This task runs every 6 hours to check for budget overruns where actual
    disbursements exceed allocated budget. Alerts are created for variances
    exceeding 10%, and email notifications are sent to MOA finance officers.

    Variance Thresholds:
        - >10%: Create alert, send email (MEDIUM severity)
        - >20%: Create alert, send email (CRITICAL severity)

    Returns:
        dict: Detection results summary
            - status: "completed" or "failed"
            - total_checked: int
            - total_variances: int
            - alerts_created: int
            - emails_sent: int
            - errors: list of error messages

    Retry Logic:
        - Max retries: 3
        - Retry delay: 5 minutes
        - Retries on database errors, email failures

    Example Result:
        {
            "status": "completed",
            "total_checked": 150,
            "total_variances": 8,
            "alerts_created": 8,
            "emails_sent": 8,
            "errors": []
        }
    """
    import logging
    from decimal import Decimal
    from .models import MonitoringEntry
    from .utils.email import send_budget_variance_alert
    from project_central.models import Alert

    logger = logging.getLogger(__name__)
    logger.info("[BUDGET VARIANCE] Starting budget variance detection")

    try:
        # Find active PPAs with budget allocations
        ppas = MonitoringEntry.objects.filter(
            status__in=['planning', 'ongoing', 'completed'],
            budget_allocation__gt=0
        ).select_related('implementing_moa', 'lead_organization')

        total_checked = 0
        total_variances = 0
        alerts_created = 0
        emails_sent = 0
        errors = []

        for ppa in ppas:
            total_checked += 1

            try:
                # Calculate actual disbursement
                actual_disbursed = ppa.total_actual_disbursed()

                # Skip if no disbursements yet
                if actual_disbursed == Decimal('0.00'):
                    continue

                # Calculate variance
                if actual_disbursed > ppa.budget_allocation:
                    variance_amount = actual_disbursed - ppa.budget_allocation
                    variance_pct = float(
                        (variance_amount / ppa.budget_allocation) * 100
                    )

                    # Only alert if variance > 10%
                    if variance_pct > 10:
                        total_variances += 1

                        # Determine severity
                        if variance_pct > 20:
                            severity = "critical"
                        else:
                            severity = "high"

                        # Check if alert already exists
                        existing_alert = Alert.objects.filter(
                            alert_type="overspending",
                            related_ppa=ppa,
                            is_active=True
                        ).first()

                        if not existing_alert:
                            # Create alert
                            Alert.create_alert(
                                alert_type="overspending",
                                severity=severity,
                                title=f"Budget Variance: {ppa.title}",
                                description=(
                                    f"Actual disbursements exceed budget allocation by "
                                    f"PHP {variance_amount:,.2f} ({variance_pct:.1f}%). "
                                    f"Allocated: PHP {ppa.budget_allocation:,.2f}, "
                                    f"Actual: PHP {actual_disbursed:,.2f}"
                                ),
                                related_ppa=ppa,
                                action_url=f"/monitoring/{ppa.id}/",
                                alert_data={
                                    "ppa_id": str(ppa.id),
                                    "variance_amount": str(variance_amount),
                                    "variance_pct": variance_pct,
                                    "allocated": str(ppa.budget_allocation),
                                    "actual": str(actual_disbursed)
                                },
                                expires_at=timezone.now() + timedelta(days=30)
                            )
                            alerts_created += 1

                            logger.info(
                                f"[BUDGET VARIANCE] Alert created for PPA {ppa.id}: "
                                f"{variance_pct:.1f}% over budget"
                            )

                        # Send email notification
                        email_sent = send_budget_variance_alert(
                            ppa, variance_amount, variance_pct
                        )
                        if email_sent:
                            emails_sent += 1

            except Exception as e:
                error_msg = f"PPA {ppa.id}: {str(e)}"
                errors.append(error_msg)
                logger.error(
                    f"[BUDGET VARIANCE] Error processing PPA {ppa.id}: {e}",
                    exc_info=True
                )

        # Final summary
        result = {
            "status": "completed",
            "total_checked": total_checked,
            "total_variances": total_variances,
            "alerts_created": alerts_created,
            "emails_sent": emails_sent,
            "errors": errors[:10]  # Limit to first 10 errors
        }

        logger.info(
            f"[BUDGET VARIANCE] Completed: {total_checked} checked, "
            f"{total_variances} variances found, {alerts_created} alerts created, "
            f"{emails_sent} emails sent"
        )

        return result

    except Exception as e:
        logger.error(
            f"[BUDGET VARIANCE] Fatal error in detect_budget_variances: {e}",
            exc_info=True
        )

        # Retry on database/email errors
        if any(keyword in str(e).lower() for keyword in ['database', 'connection', 'smtp']):
            raise self.retry(exc=e)

        return {
            "status": "failed",
            "error": str(e),
            "total_checked": 0,
            "total_variances": 0,
            "alerts_created": 0,
            "emails_sent": 0,
            "errors": [str(e)]
        }


@shared_task(
    name="monitoring.send_approval_deadline_reminders",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def send_approval_deadline_reminders(self):
    """
    Send reminders for PPAs pending approval beyond deadline.

    This task runs daily at 8:00 AM to find PPAs that have been pending
    approval for more than 7 days and sends email reminders to MFBM analysts.
    Alerts are also created for overdue approvals.

    Reminder Thresholds:
        - >7 days: Send reminder (HIGH severity)
        - >14 days: Send reminder (CRITICAL severity)

    Returns:
        dict: Reminder results summary
            - status: "completed" or "failed"
            - total_checked: int
            - total_overdue: int
            - reminders_sent: int
            - alerts_created: int
            - errors: list of error messages

    Retry Logic:
        - Max retries: 3
        - Retry delay: 5 minutes
        - Retries on database errors, email failures

    Example Result:
        {
            "status": "completed",
            "total_checked": 75,
            "total_overdue": 12,
            "reminders_sent": 12,
            "alerts_created": 5,
            "errors": []
        }
    """
    import logging
    from datetime import timedelta
    from .models import MonitoringEntry
    from .utils.email import send_approval_deadline_reminder
    from project_central.models import Alert

    logger = logging.getLogger(__name__)
    logger.info("[APPROVAL REMINDER] Starting approval deadline reminder task")

    try:
        today = timezone.now().date()

        # Find PPAs pending approval
        pending_ppas = MonitoringEntry.objects.filter(
            approval_status__in=[
                MonitoringEntry.APPROVAL_STATUS_DRAFT,
                MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW,
                MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW
            ],
            status__in=['planning', 'ongoing']
        ).select_related(
            'implementing_moa',
            'submitted_to_organization',
            'reviewed_by',
            'created_by'
        )

        total_checked = 0
        total_overdue = 0
        reminders_sent = 0
        alerts_created = 0
        errors = []

        for ppa in pending_ppas:
            total_checked += 1

            try:
                # Calculate days pending (from created_at or updated_at)
                pending_since = ppa.updated_at or ppa.created_at
                days_pending = (timezone.now() - pending_since).days

                # Only process if pending > 7 days
                if days_pending > 7:
                    total_overdue += 1

                    # Determine severity
                    if days_pending > 14:
                        severity = "critical"
                    else:
                        severity = "high"

                    # Check if alert already exists (created in last 7 days)
                    seven_days_ago = timezone.now() - timedelta(days=7)
                    existing_alert = Alert.objects.filter(
                        alert_type="approval_bottleneck",
                        related_ppa=ppa,
                        is_active=True,
                        created_at__gte=seven_days_ago
                    ).first()

                    if not existing_alert:
                        # Create alert
                        Alert.create_alert(
                            alert_type="approval_bottleneck",
                            severity=severity,
                            title=f"Approval Overdue: {ppa.title}",
                            description=(
                                f"This PPA has been pending approval for {days_pending} days. "
                                f"Current status: {ppa.get_approval_status_display()}. "
                                f"Budget: PHP {ppa.budget_allocation:,.2f}. "
                                f"Priority: {ppa.get_priority_display()}."
                            ),
                            related_ppa=ppa,
                            action_url=f"/monitoring/{ppa.id}/",
                            alert_data={
                                "ppa_id": str(ppa.id),
                                "days_pending": days_pending,
                                "approval_status": ppa.approval_status,
                                "fiscal_year": ppa.fiscal_year
                            },
                            expires_at=timezone.now() + timedelta(days=14)
                        )
                        alerts_created += 1

                        logger.info(
                            f"[APPROVAL REMINDER] Alert created for PPA {ppa.id}: "
                            f"{days_pending} days pending"
                        )

                    # Send email reminder
                    email_sent = send_approval_deadline_reminder(ppa, days_pending)
                    if email_sent:
                        reminders_sent += 1

            except Exception as e:
                error_msg = f"PPA {ppa.id}: {str(e)}"
                errors.append(error_msg)
                logger.error(
                    f"[APPROVAL REMINDER] Error processing PPA {ppa.id}: {e}",
                    exc_info=True
                )

        # Final summary
        result = {
            "status": "completed",
            "total_checked": total_checked,
            "total_overdue": total_overdue,
            "reminders_sent": reminders_sent,
            "alerts_created": alerts_created,
            "errors": errors[:10]  # Limit to first 10 errors
        }

        logger.info(
            f"[APPROVAL REMINDER] Completed: {total_checked} checked, "
            f"{total_overdue} overdue, {reminders_sent} reminders sent, "
            f"{alerts_created} alerts created"
        )

        return result

    except Exception as e:
        logger.error(
            f"[APPROVAL REMINDER] Fatal error in send_approval_deadline_reminders: {e}",
            exc_info=True
        )

        # Retry on database/email errors
        if any(keyword in str(e).lower() for keyword in ['database', 'connection', 'smtp']):
            raise self.retry(exc=e)

        return {
            "status": "failed",
            "error": str(e),
            "total_checked": 0,
            "total_overdue": 0,
            "reminders_sent": 0,
            "alerts_created": 0,
            "errors": [str(e)]
        }
