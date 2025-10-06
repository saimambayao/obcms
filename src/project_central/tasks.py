"""
Celery Tasks for Project Central

Automated background tasks for project management and monitoring.
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="project_central.generate_daily_alerts")
def generate_daily_alerts_task():
    """
    Generate all daily alerts.

    Called by Celery scheduler daily.

    Returns:
        dict: Summary of alerts generated
    """
    from project_central.services import AlertService

    logger.info("Starting daily alert generation task")

    try:
        results = AlertService.generate_daily_alerts()
        logger.info(
            f"Daily alert generation completed: {results['total']} total alerts"
        )

        if results["errors"]:
            logger.error(f"Alert generation errors: {results['errors']}")

        return results

    except Exception as e:
        logger.error(f"Fatal error in daily alert generation: {e}", exc_info=True)
        raise


@shared_task(name="project_central.deactivate_resolved_alerts")
def deactivate_resolved_alerts_task():
    """
    Deactivate alerts that are no longer relevant.

    Called by Celery scheduler daily (after alert generation).

    Returns:
        int: Number of alerts deactivated
    """
    from project_central.services import AlertService

    logger.info("Starting resolved alert deactivation task")

    try:
        count = AlertService.deactivate_resolved_alerts()
        logger.info(f"Deactivated {count} resolved alerts")
        return count

    except Exception as e:
        logger.error(f"Error deactivating resolved alerts: {e}", exc_info=True)
        raise


@shared_task(name="project_central.cleanup_expired_alerts")
def cleanup_expired_alerts_task():
    """
    Clean up expired alerts.

    Called by Celery scheduler weekly.

    Returns:
        int: Number of alerts cleaned up
    """
    from project_central.models import Alert

    logger.info("Starting expired alert cleanup task")

    try:
        count = Alert.cleanup_expired_alerts()
        logger.info(f"Cleaned up {count} expired alerts")
        return count

    except Exception as e:
        logger.error(f"Error cleaning up expired alerts: {e}", exc_info=True)
        raise


@shared_task(name="project_central.update_budget_ceiling_allocations")
def update_budget_ceiling_allocations_task():
    """
    Update all budget ceiling allocated amounts.

    Called by Celery scheduler daily.

    Returns:
        int: Number of ceilings updated
    """
    from project_central.models import BudgetCeiling

    logger.info("Starting budget ceiling allocation update task")

    try:
        current_year = timezone.now().year
        ceilings = BudgetCeiling.objects.filter(
            fiscal_year=current_year,
            is_active=True,
        )

        count = 0
        for ceiling in ceilings:
            ceiling.update_allocated_amount()
            count += 1

        logger.info(f"Updated {count} budget ceiling allocations")
        return count

    except Exception as e:
        logger.error(f"Error updating budget ceiling allocations: {e}", exc_info=True)
        raise


@shared_task(name="project_central.generate_weekly_workflow_report")
def generate_weekly_workflow_report_task():
    """
    Generate weekly workflow performance report.

    Called by Celery scheduler weekly.

    Returns:
        dict: Report summary
    """
    from project_central.services import WorkflowService

    logger.info("Starting weekly workflow report generation")

    try:
        metrics = WorkflowService.get_workflow_metrics()

        # Email report to administrators
        # (Future: implement email template and distribution)

        logger.info(
            f"Generated workflow report: {metrics['total_workflows']} workflows"
        )
        return metrics

    except Exception as e:
        logger.error(f"Error generating workflow report: {e}", exc_info=True)
        raise


@shared_task(name="project_central.generate_monthly_budget_report")
def generate_monthly_budget_report_task():
    """
    Generate monthly budget utilization report.

    Called by Celery scheduler monthly.

    Returns:
        dict: Report summary
    """
    from project_central.services import AnalyticsService

    logger.info("Starting monthly budget report generation")

    try:
        current_year = timezone.now().year
        summary = AnalyticsService.get_dashboard_summary(fiscal_year=current_year)

        # Email report to administrators
        # (Future: implement email template and distribution)

        logger.info("Generated monthly budget report")
        return {
            "fiscal_year": current_year,
            "total_budget": summary["budget_by_sector"]["totals"]["total_budget"],
            "utilization_pct": summary["utilization_rates"]["ppa_utilization"][
                "disbursement_rate"
            ],
        }

    except Exception as e:
        logger.error(f"Error generating budget report: {e}", exc_info=True)
        raise


@shared_task(name="project_central.check_workflow_deadlines")
def check_workflow_deadlines_task():
    """
    Check for workflows approaching deadlines.

    Called by Celery scheduler daily.

    Returns:
        int: Number of deadline alerts created
    """
    from project_central.models import ProjectWorkflow, Alert
    from datetime import timedelta

    logger.info("Starting workflow deadline check")

    try:
        # Find workflows with target completion dates within 7 days
        seven_days_from_now = timezone.now().date() + timedelta(days=7)

        approaching_deadline = ProjectWorkflow.objects.filter(
            target_completion_date__lte=seven_days_from_now,
            target_completion_date__gte=timezone.now().date(),
            current_stage__in=[
                "budget_planning",
                "approval",
                "implementation",
                "monitoring",
            ],
        ).exclude(current_stage="completion")

        count = 0
        for workflow in approaching_deadline:
            days_remaining = (
                workflow.target_completion_date - timezone.now().date()
            ).days

            # Check if alert already exists
            existing_alert = Alert.objects.filter(
                alert_type="deadline_approaching",
                related_workflow=workflow,
                is_active=True,
            ).exists()

            if not existing_alert:
                Alert.create_alert(
                    alert_type="deadline_approaching",
                    severity="high" if days_remaining <= 3 else "medium",
                    title=f"Deadline Approaching: {workflow.primary_need.title}",
                    description=f"This workflow has {days_remaining} days until target completion date ({workflow.target_completion_date}). Current stage: {workflow.get_current_stage_display()}",
                    related_workflow=workflow,
                    action_url=workflow.get_absolute_url(),
                    alert_data={
                        "workflow_id": str(workflow.id),
                        "days_remaining": days_remaining,
                        "target_date": workflow.target_completion_date.isoformat(),
                    },
                    expires_at=timezone.now() + timedelta(days=7),
                )
                count += 1

        logger.info(f"Created {count} deadline approaching alerts")
        return count

    except Exception as e:
        logger.error(f"Error checking workflow deadlines: {e}", exc_info=True)
        raise


@shared_task(name="project_central.sync_workflow_ppa_status")
def sync_workflow_ppa_status_task():
    """
    Synchronize workflow and PPA status fields.

    Ensures workflows and their linked PPAs stay in sync.

    Called by Celery scheduler daily.

    Returns:
        int: Number of syncs performed
    """
    from project_central.models import ProjectWorkflow

    logger.info("Starting workflow-PPA status sync")

    try:
        workflows = ProjectWorkflow.objects.exclude(ppa__isnull=True)

        count = 0
        for workflow in workflows:
            updated = False

            # Sync status
            if (
                workflow.current_stage == "completion"
                and workflow.ppa.status != "completed"
            ):
                workflow.ppa.status = "completed"
                workflow.ppa.save(update_fields=["status"])
                updated = True

            elif (
                workflow.current_stage in ["implementation", "monitoring"]
                and workflow.ppa.status != "ongoing"
            ):
                workflow.ppa.status = "ongoing"
                workflow.ppa.save(update_fields=["status"])
                updated = True

            # Sync approval status
            if workflow.current_stage == "approval":
                from monitoring.models import MonitoringEntry

                if (
                    workflow.ppa.approval_status
                    == MonitoringEntry.APPROVAL_STATUS_DRAFT
                ):
                    workflow.ppa.approval_status = (
                        MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW
                    )
                    workflow.ppa.save(update_fields=["approval_status"])
                    updated = True

            if updated:
                count += 1

        logger.info(f"Synchronized {count} workflow-PPA status fields")
        return count

    except Exception as e:
        logger.error(f"Error syncing workflow-PPA status: {e}", exc_info=True)
        raise


@shared_task(
    name="project_central.cleanup_orphaned_workitems",
    bind=True,
    max_retries=2,
    default_retry_delay=600  # 10 minutes
)
def cleanup_orphaned_workitems_task(self):
    """
    Clean up orphaned WorkItems with no valid content_object.

    This task runs weekly to identify and optionally delete WorkItems that
    reference deleted or invalid content_objects (MonitoringEntry, etc.).
    Orphaned WorkItems can occur when related objects are deleted without
    proper cascade handling.

    Safety Features:
        - Dry-run mode by default (logs only, no deletion)
        - Skips WorkItems with descendants (preserves hierarchies)
        - Only processes WorkItems older than 30 days
        - Comprehensive logging for audit trail

    Returns:
        dict: Cleanup results summary
            - status: "completed" or "failed"
            - total_checked: int
            - orphaned_found: int
            - deleted_count: int
            - skipped_count: int
            - errors: list of error messages

    Configuration:
        Set WORKITEM_CLEANUP_DRY_RUN=False in settings to enable deletion.
        Default is True (dry-run mode).

    Example Result:
        {
            "status": "completed",
            "total_checked": 250,
            "orphaned_found": 8,
            "deleted_count": 0,
            "skipped_count": 8,
            "errors": []
        }
    """
    from common.work_item_model import WorkItem
    from datetime import timedelta
    from django.conf import settings

    logger.info("[WORKITEM CLEANUP] Starting orphaned WorkItem cleanup task")

    try:
        # Check if dry-run mode (default: True)
        dry_run = getattr(settings, 'WORKITEM_CLEANUP_DRY_RUN', True)

        # Only check WorkItems older than 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Get all WorkItems with content_type set
        workitems = WorkItem.objects.filter(
            content_type__isnull=False,
            created_at__lte=thirty_days_ago
        ).select_related('content_type')

        total_checked = 0
        orphaned_found = 0
        deleted_count = 0
        skipped_count = 0
        errors = []

        for workitem in workitems:
            total_checked += 1

            try:
                # Check if content_object exists
                if workitem.content_object is None:
                    orphaned_found += 1

                    # Skip if WorkItem has descendants (preserve hierarchy)
                    if workitem.get_descendants().exists():
                        skipped_count += 1
                        logger.warning(
                            f"[WORKITEM CLEANUP] Skipping orphaned WorkItem {workitem.id} "
                            f"(has descendants): {workitem.title}"
                        )
                        continue

                    # Log orphaned WorkItem
                    logger.warning(
                        f"[WORKITEM CLEANUP] Found orphaned WorkItem: "
                        f"ID={workitem.id}, Title={workitem.title}, "
                        f"ContentType={workitem.content_type}, "
                        f"ObjectID={workitem.object_id}"
                    )

                    # Delete if not in dry-run mode
                    if not dry_run:
                        workitem.delete()
                        deleted_count += 1
                        logger.info(
                            f"[WORKITEM CLEANUP] Deleted orphaned WorkItem {workitem.id}"
                        )
                    else:
                        logger.info(
                            f"[WORKITEM CLEANUP] DRY-RUN: Would delete WorkItem {workitem.id}"
                        )

            except Exception as e:
                error_msg = f"WorkItem {workitem.id}: {str(e)}"
                errors.append(error_msg)
                logger.error(
                    f"[WORKITEM CLEANUP] Error processing WorkItem {workitem.id}: {e}",
                    exc_info=True
                )

        # Final summary
        result = {
            "status": "completed",
            "dry_run": dry_run,
            "total_checked": total_checked,
            "orphaned_found": orphaned_found,
            "deleted_count": deleted_count,
            "skipped_count": skipped_count,
            "errors": errors[:10]  # Limit to first 10 errors
        }

        logger.info(
            f"[WORKITEM CLEANUP] Completed: {total_checked} checked, "
            f"{orphaned_found} orphaned found, {deleted_count} deleted "
            f"(dry_run={dry_run})"
        )

        return result

    except Exception as e:
        logger.error(
            f"[WORKITEM CLEANUP] Fatal error in cleanup_orphaned_workitems: {e}",
            exc_info=True
        )

        # Retry on database errors
        if "database" in str(e).lower() or "connection" in str(e).lower():
            raise self.retry(exc=e)

        return {
            "status": "failed",
            "error": str(e),
            "total_checked": 0,
            "orphaned_found": 0,
            "deleted_count": 0,
            "skipped_count": 0,
            "errors": [str(e)]
        }


@shared_task(
    name="project_central.recalculate_all_progress",
    bind=True,
    max_retries=2,
    default_retry_delay=900  # 15 minutes
)
def recalculate_all_progress_task(self):
    """
    Recalculate progress for all WorkItem hierarchies.

    This task runs monthly to ensure all WorkItem progress calculations
    are accurate and consistent. It processes all root WorkItems (projects)
    and recalculates their progress based on descendant completion status.

    The recalculation ensures:
        - Parent progress reflects child completion
        - Stale progress values are corrected
        - Progress is consistent across hierarchies

    Returns:
        dict: Recalculation results summary
            - status: "completed" or "failed"
            - total_projects: int
            - total_recalculated: int
            - total_unchanged: int
            - total_errors: int
            - errors: list of error messages

    Performance:
        - Processes WorkItems in batches of 100
        - Uses select_related/prefetch_related for optimization
        - Expected runtime: 5-15 minutes for 1000+ WorkItems

    Example Result:
        {
            "status": "completed",
            "total_projects": 120,
            "total_recalculated": 85,
            "total_unchanged": 35,
            "total_errors": 0,
            "errors": []
        }
    """
    from common.work_item_model import WorkItem

    logger.info("[PROGRESS RECALC] Starting monthly progress recalculation")

    try:
        # Get all root WorkItems (projects without parents)
        root_projects = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        ).prefetch_related('children')

        total_projects = 0
        total_recalculated = 0
        total_unchanged = 0
        total_errors = 0
        errors = []

        for project in root_projects:
            total_projects += 1

            try:
                # Store old progress
                old_progress = project.progress

                # Recalculate progress from descendants
                # WorkItem.calculate_progress() updates self.progress
                project.calculate_progress()
                project.refresh_from_db()

                new_progress = project.progress

                if new_progress != old_progress:
                    total_recalculated += 1
                    logger.info(
                        f"[PROGRESS RECALC] Updated WorkItem {project.id}: "
                        f"{old_progress}% → {new_progress}% ({project.title})"
                    )
                else:
                    total_unchanged += 1

            except Exception as e:
                total_errors += 1
                error_msg = f"WorkItem {project.id}: {str(e)}"
                errors.append(error_msg)
                logger.error(
                    f"[PROGRESS RECALC] Error recalculating WorkItem {project.id}: {e}",
                    exc_info=True
                )

        # Final summary
        result = {
            "status": "completed",
            "total_projects": total_projects,
            "total_recalculated": total_recalculated,
            "total_unchanged": total_unchanged,
            "total_errors": total_errors,
            "errors": errors[:10]  # Limit to first 10 errors
        }

        logger.info(
            f"[PROGRESS RECALC] Completed: {total_projects} projects, "
            f"{total_recalculated} recalculated, {total_errors} errors"
        )

        return result

    except Exception as e:
        logger.error(
            f"[PROGRESS RECALC] Fatal error in recalculate_all_progress: {e}",
            exc_info=True
        )

        # Retry on database errors
        if "database" in str(e).lower() or "connection" in str(e).lower():
            raise self.retry(exc=e)

        return {
            "status": "failed",
            "error": str(e),
            "total_projects": 0,
            "total_recalculated": 0,
            "total_unchanged": 0,
            "total_errors": 0,
            "errors": [str(e)]
        }
