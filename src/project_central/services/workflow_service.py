"""
Workflow Service

Business logic for managing project workflow stages, transitions, and automation.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Service class for workflow management and automation.

    Handles:
    - Stage transition validation
    - Automated task generation
    - Stage-specific business logic
    - Notifications
    """

    # Task templates for each workflow stage
    STAGE_TASK_TEMPLATES = {
        "need_validation": [
            {
                "title": "Review and validate community need",
                "description": "Verify need data, evidence sources, and community validation. Update priority score if needed.",
                "priority": "high",
                "days_to_complete": 7,
            },
            {
                "title": "Confirm need is not duplicate",
                "description": "Check existing needs and PPAs to ensure this is not a duplicate request.",
                "priority": "medium",
                "days_to_complete": 3,
            },
        ],
        "policy_linkage": [
            {
                "title": "Identify related policy recommendations",
                "description": "Search policy tracking system for relevant recommendations that address this need.",
                "priority": "medium",
                "days_to_complete": 5,
            },
            {
                "title": "Link need to applicable policies",
                "description": "Create M2M relationships between need and policy recommendations in admin.",
                "priority": "medium",
                "days_to_complete": 2,
            },
        ],
        "mao_coordination": [
            {
                "title": "Identify appropriate MAO",
                "description": "Determine which Bangsamoro Ministerial Agency/Office has mandate for this need.",
                "priority": "high",
                "days_to_complete": 3,
            },
            {
                "title": "Contact MAO focal person",
                "description": "Reach out to MAO focal person to discuss need and confirm MAO will address it.",
                "priority": "high",
                "days_to_complete": 7,
            },
            {
                "title": "Obtain MAO commitment",
                "description": "Get formal or informal commitment from MAO to include this in their planning.",
                "priority": "high",
                "days_to_complete": 14,
            },
        ],
        "budget_planning": [
            {
                "title": "Create PPA (MonitoringEntry) for this need",
                "description": "Create a Program/Project/Activity entry in monitoring system with budget details.",
                "priority": "critical",
                "days_to_complete": 7,
            },
            {
                "title": "Prepare budget justification",
                "description": "Compile evidence from MANA assessment, community needs, and policy alignment to justify budget request.",
                "priority": "high",
                "days_to_complete": 10,
            },
            {
                "title": "Determine funding source",
                "description": "Identify appropriate funding source (GAA, Block Grant, LGU, Donor) for this PPA.",
                "priority": "high",
                "days_to_complete": 5,
            },
            {
                "title": "Check budget ceiling compliance",
                "description": "Verify budget allocation does not exceed sector/funding source ceiling.",
                "priority": "high",
                "days_to_complete": 2,
            },
            {
                "title": "Calculate cost per beneficiary",
                "description": "Determine cost-effectiveness metrics and compare to similar PPAs.",
                "priority": "medium",
                "days_to_complete": 3,
            },
        ],
        "approval": [
            {
                "title": "Submit PPA for technical review",
                "description": "Prepare technical documentation and submit PPA to technical review committee.",
                "priority": "critical",
                "days_to_complete": 3,
            },
            {
                "title": "Address technical review feedback",
                "description": "Respond to any questions or concerns raised during technical review.",
                "priority": "high",
                "days_to_complete": 5,
            },
            {
                "title": "Submit for budget review",
                "description": "Forward PPA to finance office for budget allocation review.",
                "priority": "critical",
                "days_to_complete": 3,
            },
            {
                "title": "Coordinate stakeholder consultation (if required)",
                "description": "Schedule and conduct consultation with community and MAO if consultation required.",
                "priority": "high",
                "days_to_complete": 14,
            },
            {
                "title": "Prepare executive approval package",
                "description": "Compile all documentation for Chief Minister's Office review.",
                "priority": "critical",
                "days_to_complete": 5,
            },
        ],
        "implementation": [
            {
                "title": "Create detailed implementation plan",
                "description": "Develop timeline, milestones, and activity schedule for PPA implementation.",
                "priority": "high",
                "days_to_complete": 7,
            },
            {
                "title": "Assign implementation responsibilities",
                "description": "Identify staff and partners responsible for each activity.",
                "priority": "high",
                "days_to_complete": 5,
            },
            {
                "title": "Record initial funding obligation",
                "description": "Create FundingFlow record for initial budget obligation.",
                "priority": "high",
                "days_to_complete": 2,
            },
        ],
        "monitoring": [
            {
                "title": "Set up M&E data collection",
                "description": "Establish system for collecting progress data, outcome indicators, and beneficiary information.",
                "priority": "high",
                "days_to_complete": 7,
            },
            {
                "title": "Schedule quarterly progress reviews",
                "description": "Calendar regular check-ins to assess progress, challenges, and budget utilization.",
                "priority": "medium",
                "days_to_complete": 3,
            },
        ],
        "completion": [
            {
                "title": "Conduct final evaluation",
                "description": "Assess overall project success, outcome achievement, and impact on community.",
                "priority": "high",
                "days_to_complete": 14,
            },
            {
                "title": "Complete financial reconciliation",
                "description": "Verify all budget obligations and disbursements, document savings or overruns.",
                "priority": "high",
                "days_to_complete": 10,
            },
            {
                "title": "Document lessons learned",
                "description": "Capture key insights for future projects, including budget and cost-effectiveness lessons.",
                "priority": "medium",
                "days_to_complete": 7,
            },
            {
                "title": "Update cost-effectiveness database",
                "description": "Record final cost per beneficiary and effectiveness ratings for future reference.",
                "priority": "medium",
                "days_to_complete": 3,
            },
        ],
    }

    @classmethod
    def trigger_stage_actions(cls, workflow, new_stage, user):
        """
        Execute automated actions when workflow advances to a new stage.

        Args:
            workflow: ProjectWorkflow instance
            new_stage: The new stage being entered
            user: User who triggered the stage transition
        """
        try:
            logger.info(
                f"Triggering stage actions for workflow {workflow.id}: {new_stage}"
            )

            # Generate tasks for this stage
            cls.generate_stage_tasks(workflow, new_stage, user)

            # Send notifications
            cls.send_stage_notification(workflow, new_stage, user)

            # Execute stage-specific logic
            if new_stage == "mao_coordination":
                cls._handle_mao_coordination_stage(workflow)
            elif new_stage == "budget_planning":
                cls._handle_budget_planning_stage(workflow)
            elif new_stage == "approval":
                cls._handle_approval_stage(workflow)
            elif new_stage == "implementation":
                cls._handle_implementation_stage(workflow)
            elif new_stage == "completion":
                cls._handle_completion_stage(workflow)

            logger.info(
                f"Stage actions completed successfully for workflow {workflow.id}"
            )

        except Exception as e:
            logger.error(
                f"Error in trigger_stage_actions for workflow {workflow.id}: {e}",
                exc_info=True,
            )
            # Don't raise - we don't want to block stage advancement

    @classmethod
    def generate_stage_tasks(cls, workflow, stage, user):
        """
        Auto-generate tasks for a workflow stage.

        Args:
            workflow: ProjectWorkflow instance
            stage: Workflow stage to generate tasks for
            user: User who triggered stage advancement
        """
        from common.models import WorkItem
        from django.contrib.contenttypes.models import ContentType

        templates = cls.STAGE_TASK_TEMPLATES.get(stage, [])

        for template in templates:
            due_date = timezone.now().date() + timedelta(
                days=template["days_to_complete"]
            )

            # Get ContentType for workflow
            workflow_ct = ContentType.objects.get_for_model(workflow)

            # Create WorkItem task with domain in task_data
            task = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=template["title"],
                description=template["description"],
                priority=template["priority"],
                status="not_started",
                due_date=due_date,
                created_by=user,
                content_type=workflow_ct,
                object_id=workflow.id,
                task_data={
                    "domain": "project_central",
                    "workflow_stage": stage,
                    "auto_generated": True,
                    "linked_ppa_id": str(workflow.ppa.id) if workflow.ppa else None,
                },
            )

            # Assign to project lead if available
            if workflow.project_lead:
                task.assignees.add(workflow.project_lead)

            logger.info(
                f"Generated task '{task.title}' for workflow {workflow.id}, stage {stage}"
            )

        return len(templates)

    @classmethod
    def send_stage_notification(cls, workflow, new_stage, user):
        """
        Send notification about stage transition.

        Args:
            workflow: ProjectWorkflow instance
            new_stage: New stage entered
            user: User who triggered transition
        """
        # Build recipient list
        recipients = []

        if workflow.project_lead and workflow.project_lead.email:
            recipients.append(workflow.project_lead.email)

        if workflow.mao_focal_person and hasattr(workflow.mao_focal_person, "email"):
            if workflow.mao_focal_person.email:
                recipients.append(workflow.mao_focal_person.email)

        if not recipients:
            logger.warning(
                f"No email recipients for workflow {workflow.id} stage notification"
            )
            return

        # Prepare email
        subject = f"[OBCMS] Project Workflow Advanced: {workflow.primary_need.title}"

        context = {
            "workflow": workflow,
            "new_stage": workflow.get_current_stage_display(),
            "user": user,
            "workflow_url": workflow.get_absolute_url(),
        }

        # For now, simple text email (Phase 2 can add HTML templates)
        message = f"""
Project workflow has been advanced to: {workflow.get_current_stage_display()}

Project: {workflow.primary_need.title}
Advanced by: {user.get_full_name() or user.username}
New stage: {workflow.get_current_stage_display()}

View workflow: {settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://localhost:8000'}{workflow.get_absolute_url()}

Tasks have been automatically generated for this stage.
        """

        try:
            send_mail(
                subject=subject,
                message=message.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=True,
            )
            logger.info(
                f"Sent stage notification for workflow {workflow.id} to {len(recipients)} recipients"
            )
        except Exception as e:
            logger.error(f"Failed to send email for workflow {workflow.id}: {e}")

    @classmethod
    def _handle_mao_coordination_stage(cls, workflow):
        """Stage-specific logic for MAO coordination."""
        # Create alert if no MAO focal person assigned after 7 days
        # (This would be checked by daily alert generation task)
        pass

    @classmethod
    def _handle_budget_planning_stage(cls, workflow):
        """Stage-specific logic for budget planning."""
        # Update workflow estimated budget from need if available
        if workflow.primary_need and hasattr(workflow.primary_need, "estimated_cost"):
            if not workflow.estimated_budget and workflow.primary_need.estimated_cost:
                workflow.estimated_budget = workflow.primary_need.estimated_cost
                workflow.save(update_fields=["estimated_budget"])

    @classmethod
    def _handle_approval_stage(cls, workflow):
        """Stage-specific logic for approval."""
        # Set PPA approval_status to technical_review if still in draft
        if workflow.ppa:
            from monitoring.models import MonitoringEntry

            if workflow.ppa.approval_status == MonitoringEntry.APPROVAL_STATUS_DRAFT:
                workflow.ppa.approval_status = (
                    MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW
                )
                workflow.ppa.save(update_fields=["approval_status"])

    @classmethod
    def _handle_implementation_stage(cls, workflow):
        """Stage-specific logic for implementation."""
        # Update PPA status to ongoing
        if workflow.ppa and workflow.ppa.status != "ongoing":
            workflow.ppa.status = "ongoing"
            workflow.ppa.save(update_fields=["status"])

    @classmethod
    def _handle_completion_stage(cls, workflow):
        """Stage-specific logic for completion."""
        # Update workflow completion date
        if not workflow.actual_completion_date:
            workflow.actual_completion_date = timezone.now().date()
            workflow.save(update_fields=["actual_completion_date"])

        # Mark need as completed
        if workflow.primary_need and workflow.primary_need.status != "completed":
            workflow.primary_need.status = "completed"
            workflow.primary_need.save(update_fields=["status"])

        # Update PPA status
        if workflow.ppa and workflow.ppa.status != "completed":
            workflow.ppa.status = "completed"
            workflow.ppa.save(update_fields=["status"])

    @classmethod
    def validate_stage_requirements(cls, workflow, target_stage):
        """
        Validate that all requirements are met to advance to target stage.

        Args:
            workflow: ProjectWorkflow instance
            target_stage: Stage to advance to

        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []

        # Use the model's built-in validation
        can_advance, reason = workflow.can_advance_to_stage(target_stage)
        if not can_advance:
            errors.append(reason)
            return False, errors

        # Additional validation based on stage
        if target_stage == "mao_coordination":
            if not workflow.primary_need.is_validated:
                errors.append("Need must be validated before MAO coordination.")

        elif target_stage == "budget_planning":
            if not workflow.mao_focal_person:
                errors.append(
                    "MAO focal person must be assigned before budget planning."
                )

        elif target_stage == "approval":
            if not workflow.ppa:
                errors.append("PPA must be created before approval stage.")
            elif not workflow.ppa.budget_allocation:
                errors.append("PPA must have budget allocation set.")
            elif not workflow.ppa.funding_source:
                errors.append("PPA must have funding source specified.")

        elif target_stage == "implementation":
            if workflow.ppa:
                from monitoring.models import MonitoringEntry

                if workflow.ppa.approval_status not in [
                    MonitoringEntry.APPROVAL_STATUS_APPROVED,
                    MonitoringEntry.APPROVAL_STATUS_ENACTED,
                ]:
                    errors.append("PPA must be approved before implementation.")

        return len(errors) == 0, errors

    @classmethod
    def bulk_advance_workflows(cls, workflow_ids, target_stage, user):
        """
        Bulk advance multiple workflows to a target stage.

        Args:
            workflow_ids: List of workflow IDs
            target_stage: Stage to advance all workflows to
            user: User performing the bulk action

        Returns:
            dict: {'succeeded': count, 'failed': count, 'errors': [...]}
        """
        from project_central.models import ProjectWorkflow

        results = {"succeeded": 0, "failed": 0, "errors": []}

        workflows = ProjectWorkflow.objects.filter(id__in=workflow_ids)

        for workflow in workflows:
            is_valid, errors = cls.validate_stage_requirements(workflow, target_stage)

            if is_valid:
                try:
                    workflow.advance_stage(target_stage, user)
                    results["succeeded"] += 1
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Workflow {workflow.id}: {str(e)}")
            else:
                results["failed"] += 1
                results["errors"].append(f"Workflow {workflow.id}: {', '.join(errors)}")

        return results

    @classmethod
    def get_workflow_metrics(cls, fiscal_year=None):
        """
        Calculate workflow metrics for reporting.

        Args:
            fiscal_year: Fiscal year to filter by (optional)

        Returns:
            dict: Metrics dictionary
        """
        from project_central.models import ProjectWorkflow
        from django.db.models import Count, Avg, Q

        workflows = ProjectWorkflow.objects.all()

        if fiscal_year:
            workflows = workflows.filter(
                Q(initiated_date__year=fiscal_year) | Q(ppa__fiscal_year=fiscal_year)
            )

        metrics = {
            "total_workflows": workflows.count(),
            "by_stage": dict(
                workflows.values("current_stage")
                .annotate(count=Count("id"))
                .values_list("current_stage", "count")
            ),
            "by_priority": dict(
                workflows.values("priority_level")
                .annotate(count=Count("id"))
                .values_list("priority_level", "count")
            ),
            "on_track": workflows.filter(is_on_track=True).count(),
            "blocked": workflows.filter(is_blocked=True).count(),
            "avg_days_in_stage": workflows.annotate(
                days_in_stage=Count("stage_history")
            ).aggregate(avg=Avg("days_in_stage"))["avg"]
            or 0,
            "overdue_count": sum(1 for w in workflows if w.is_overdue()),
        }

        return metrics
