"""
Budget Approval Service

Business logic for the 5-stage budget approval workflow.
"""

import logging
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from monitoring.models import MonitoringEntry
from project_central.models import BudgetCeiling, Alert

logger = logging.getLogger(__name__)


class BudgetApprovalService:
    """
    Service for managing the 5-stage budget approval workflow.

    Approval Flow:
    1. Draft → Technical Review
    2. Technical Review → Budget Review
    3. Budget Review → Stakeholder Consultation (optional) / Executive Approval
    4. Stakeholder Consultation → Executive Approval
    5. Executive Approval → Approved
    6. Approved → Enacted
    """

    # Required fields per approval stage
    STAGE_REQUIREMENTS = {
        MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW: [
            "title",
            "category",
            "sector",
            "lead_organization",
            "description",
            "target_beneficiaries",
        ],
        MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW: [
            "budget_allocation",
            "funding_source",
            "appropriation_class",
            "obc_slots",
            "cost_per_beneficiary",
        ],
        MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL: [
            "outcome_framework",  # Should have at least one outcome
        ],
    }

    @classmethod
    @transaction.atomic
    def advance_approval_stage(cls, ppa, new_status, user, notes=""):
        """
        Advance PPA to next approval stage with validation.

        Args:
            ppa: MonitoringEntry instance
            new_status: New approval_status value
            user: User performing approval
            notes: Optional notes about approval

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Validate stage transition
            is_valid, error = cls.validate_stage_transition(ppa, new_status)
            if not is_valid:
                return False, error

            # For budget_review stage, check budget ceiling
            if new_status == MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW:
                ceiling_ok, ceiling_error = cls.validate_budget_ceiling(ppa)
                if not ceiling_ok:
                    return False, ceiling_error

            # Record approval history
            history_entry = {
                "previous_status": ppa.approval_status,
                "new_status": new_status,
                "user": user.username,
                "user_id": user.id,
                "timestamp": timezone.now().isoformat(),
                "notes": notes,
            }

            if not isinstance(ppa.approval_history, list):
                ppa.approval_history = []

            ppa.approval_history.append(history_entry)

            # Update status
            old_status = ppa.approval_status
            ppa.approval_status = new_status

            # Update approval user fields
            if new_status == MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW:
                ppa.reviewed_by = user
            elif new_status == MonitoringEntry.APPROVAL_STATUS_APPROVED:
                ppa.budget_approved_by = user
            elif new_status == MonitoringEntry.APPROVAL_STATUS_ENACTED:
                ppa.executive_approved_by = user

            ppa.save()

            # Generate automatic tasks for this approval stage
            cls._generate_approval_tasks(ppa, new_status, user)

            # Send notification
            cls.send_approval_notification(ppa, old_status, new_status, user)

            # Update budget ceiling allocated amount
            if new_status in [
                MonitoringEntry.APPROVAL_STATUS_APPROVED,
                MonitoringEntry.APPROVAL_STATUS_ENACTED,
            ]:
                cls._update_budget_ceilings(ppa)

            logger.info(
                f"Advanced PPA {ppa.id} from {old_status} to {new_status} by user {user.id}"
            )
            return True, None

        except Exception as e:
            logger.error(f"Error advancing PPA {ppa.id} approval: {e}", exc_info=True)
            return False, f"System error: {str(e)}"

    @classmethod
    @transaction.atomic
    def reject_approval(cls, ppa, user, reason):
        """
        Reject PPA approval and return to draft.

        Args:
            ppa: MonitoringEntry instance
            user: User rejecting
            reason: Reason for rejection

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Record rejection in history
            history_entry = {
                "previous_status": ppa.approval_status,
                "new_status": MonitoringEntry.APPROVAL_STATUS_REJECTED,
                "user": user.username,
                "user_id": user.id,
                "timestamp": timezone.now().isoformat(),
                "notes": f"REJECTED: {reason}",
                "is_rejection": True,
            }

            if not isinstance(ppa.approval_history, list):
                ppa.approval_history = []

            ppa.approval_history.append(history_entry)

            # Update status
            old_status = ppa.approval_status
            ppa.approval_status = MonitoringEntry.APPROVAL_STATUS_REJECTED
            ppa.rejection_reason = reason
            ppa.save()

            # Send rejection notification
            cls.send_rejection_notification(ppa, user, reason)

            # Create alert for rejection
            Alert.create_alert(
                alert_type="approval_bottleneck",
                severity="high",
                title=f"PPA Rejected: {ppa.title}",
                description=f"PPA was rejected during {old_status} stage. Reason: {reason}",
                related_ppa=ppa,
                action_url=f"/monitoring/entry/{ppa.id}/",
            )

            logger.info(f"Rejected PPA {ppa.id} by user {user.id}. Reason: {reason}")
            return True, None

        except Exception as e:
            logger.error(f"Error rejecting PPA {ppa.id}: {e}", exc_info=True)
            return False, f"System error: {str(e)}"

    @classmethod
    def validate_stage_transition(cls, ppa, new_status):
        """
        Validate that PPA can transition to new approval status.

        Args:
            ppa: MonitoringEntry instance
            new_status: Target approval_status

        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Define valid transitions
        valid_transitions = {
            MonitoringEntry.APPROVAL_STATUS_DRAFT: [
                MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW,
            ],
            MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW: [
                MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW,
                MonitoringEntry.APPROVAL_STATUS_REJECTED,
            ],
            MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW: [
                MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION,
                MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL,
                MonitoringEntry.APPROVAL_STATUS_REJECTED,
            ],
            MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION: [
                MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL,
                MonitoringEntry.APPROVAL_STATUS_REJECTED,
            ],
            MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL: [
                MonitoringEntry.APPROVAL_STATUS_APPROVED,
                MonitoringEntry.APPROVAL_STATUS_REJECTED,
            ],
            MonitoringEntry.APPROVAL_STATUS_APPROVED: [
                MonitoringEntry.APPROVAL_STATUS_ENACTED,
            ],
            MonitoringEntry.APPROVAL_STATUS_REJECTED: [
                MonitoringEntry.APPROVAL_STATUS_DRAFT,  # Can restart after addressing issues
            ],
        }

        # Check if transition is valid
        current_status = ppa.approval_status
        if new_status not in valid_transitions.get(current_status, []):
            return False, f"Cannot transition from {current_status} to {new_status}"

        # Check stage-specific requirements
        required_fields = cls.STAGE_REQUIREMENTS.get(new_status, [])
        for field in required_fields:
            value = getattr(ppa, field, None)
            if not value:
                return (
                    False,
                    f"Required field '{field}' must be filled before advancing to {new_status}",
                )

        return True, None

    @classmethod
    def validate_budget_ceiling(cls, ppa):
        """
        Validate that PPA budget allocation does not exceed applicable ceilings.

        Args:
            ppa: MonitoringEntry instance

        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        if not ppa.budget_allocation:
            return True, None  # No budget to check

        # Find applicable ceilings
        ceilings = BudgetCeiling.objects.filter(
            fiscal_year=ppa.fiscal_year,
            is_active=True,
        )

        # Check sector-specific ceiling
        if ppa.sector:
            sector_ceiling = ceilings.filter(
                sector=ppa.sector,
                funding_source__isnull=True,
            ).first()

            if sector_ceiling:
                can_allocate, message = sector_ceiling.can_allocate(
                    ppa.budget_allocation
                )
                if not can_allocate and sector_ceiling.enforcement_level == "hard":
                    return False, f"Sector ceiling exceeded: {message}"

        # Check funding source ceiling
        if ppa.funding_source:
            source_ceiling = ceilings.filter(
                funding_source=ppa.funding_source,
                sector__isnull=True,
            ).first()

            if source_ceiling:
                can_allocate, message = source_ceiling.can_allocate(
                    ppa.budget_allocation
                )
                if not can_allocate and source_ceiling.enforcement_level == "hard":
                    return False, f"Funding source ceiling exceeded: {message}"

        # Check combined sector + funding source ceiling
        if ppa.sector and ppa.funding_source:
            combined_ceiling = ceilings.filter(
                sector=ppa.sector,
                funding_source=ppa.funding_source,
            ).first()

            if combined_ceiling:
                can_allocate, message = combined_ceiling.can_allocate(
                    ppa.budget_allocation
                )
                if not can_allocate and combined_ceiling.enforcement_level == "hard":
                    return False, f"Budget ceiling exceeded: {message}"

        return True, None

    @classmethod
    def _update_budget_ceilings(cls, ppa):
        """Update all applicable budget ceilings after PPA approval."""
        if not ppa.budget_allocation:
            return

        ceilings = BudgetCeiling.objects.filter(
            fiscal_year=ppa.fiscal_year,
            is_active=True,
        )

        for ceiling in ceilings:
            # Update if ceiling applies to this PPA
            applies = True

            if ceiling.sector and ceiling.sector != ppa.sector:
                applies = False

            if ceiling.funding_source and ceiling.funding_source != ppa.funding_source:
                applies = False

            if applies:
                ceiling.update_allocated_amount()

                # Create alert if near limit (90%)
                if ceiling.is_near_limit(90):
                    Alert.create_alert(
                        alert_type="budget_ceiling",
                        severity=(
                            "high"
                            if ceiling.get_utilization_percentage() >= 95
                            else "medium"
                        ),
                        title=f"Budget Ceiling Alert: {ceiling.name}",
                        description=f"Ceiling utilization at {ceiling.get_utilization_percentage():.1f}%. Allocated: ₱{ceiling.allocated_amount:,.2f} / ₱{ceiling.ceiling_amount:,.2f}",
                        action_url=f"/admin/project_central/budgetceiling/{ceiling.id}/change/",
                        alert_data={
                            "ceiling_id": str(ceiling.id),
                            "utilization_pct": ceiling.get_utilization_percentage(),
                            "remaining": float(ceiling.get_remaining_amount()),
                        },
                    )

    @classmethod
    def _generate_approval_tasks(cls, ppa, new_status, user):
        """Generate tasks for approval stage."""
        from common.models import WorkItem
        from django.contrib.contenttypes.models import ContentType

        task_templates = {
            MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW: {
                "title": f"Conduct technical review for: {ppa.title}",
                "description": "Review program design, target beneficiaries, implementation feasibility, and alignment with OOBC mandates.",
                "priority": "high",
                "days": 5,
            },
            MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW: {
                "title": f"Review budget allocation for: {ppa.title}",
                "description": "Verify budget calculations, cost per beneficiary, funding source appropriateness, and ceiling compliance.",
                "priority": "high",
                "days": 5,
            },
            MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION: {
                "title": f"Coordinate stakeholder consultation for: {ppa.title}",
                "description": "Schedule and facilitate consultation with community and MAO stakeholders.",
                "priority": "high",
                "days": 10,
            },
            MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL: {
                "title": f"Prepare executive approval package for: {ppa.title}",
                "description": "Compile all documentation, approvals, and evidence for Chief Minister's Office review.",
                "priority": "critical",
                "days": 3,
            },
        }

        template = task_templates.get(new_status)
        if not template:
            return

        due_date = timezone.now().date() + timezone.timedelta(days=template["days"])

        # Get ContentType for MonitoringEntry (PPA)
        ppa_ct = ContentType.objects.get_for_model(ppa)

        # Create WorkItem task with domain in task_data
        task = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title=template["title"],
            description=template["description"],
            priority=template["priority"],
            status="not_started",
            due_date=due_date,
            created_by=user,
            content_type=ppa_ct,
            object_id=ppa.id,
            task_data={
                "domain": "project_central",
                "workflow_stage": "approval",
                "auto_generated": True,
            },
        )

        logger.info(f"Generated approval task '{task.title}' for PPA {ppa.id}")

    @classmethod
    def send_approval_notification(cls, ppa, old_status, new_status, user):
        """Send notification about approval stage advancement."""
        # Build recipient list
        recipients = []

        if ppa.created_by and ppa.created_by.email:
            recipients.append(ppa.created_by.email)

        if ppa.lead_organization:
            # Could add organization contacts here
            pass

        if not recipients:
            logger.warning(
                f"No email recipients for PPA {ppa.id} approval notification"
            )
            return

        subject = f"[OBCMS] PPA Approval Advanced: {ppa.title}"

        message = f"""
Your PPA has been advanced in the approval workflow.

PPA: {ppa.title}
Previous Stage: {old_status}
New Stage: {new_status}
Approved by: {user.get_full_name() or user.username}

View PPA: {settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://localhost:8000'}/monitoring/entry/{ppa.id}/

Next steps will be communicated as the approval process continues.
        """

        try:
            send_mail(
                subject=subject,
                message=message.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=True,
            )
            logger.info(f"Sent approval notification for PPA {ppa.id}")
        except Exception as e:
            logger.error(f"Failed to send approval email for PPA {ppa.id}: {e}")

    @classmethod
    def send_rejection_notification(cls, ppa, user, reason):
        """Send notification about PPA rejection."""
        recipients = []

        if ppa.created_by and ppa.created_by.email:
            recipients.append(ppa.created_by.email)

        if not recipients:
            return

        subject = f"[OBCMS] PPA Rejected: {ppa.title}"

        message = f"""
Your PPA has been rejected during the approval process.

PPA: {ppa.title}
Rejected by: {user.get_full_name() or user.username}
Reason: {reason}

Please address the issues noted and resubmit your PPA for approval.

View PPA: {settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://localhost:8000'}/monitoring/entry/{ppa.id}/
        """

        try:
            send_mail(
                subject=subject,
                message=message.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send rejection email for PPA {ppa.id}: {e}")

    @classmethod
    def get_approval_queue(cls, stage=None):
        """
        Get PPAs in approval queue.

        Args:
            stage: Optional approval_status to filter by

        Returns:
            QuerySet of MonitoringEntry objects
        """
        ppas = MonitoringEntry.objects.exclude(
            approval_status__in=[
                MonitoringEntry.APPROVAL_STATUS_DRAFT,
                MonitoringEntry.APPROVAL_STATUS_APPROVED,
                MonitoringEntry.APPROVAL_STATUS_ENACTED,
                MonitoringEntry.APPROVAL_STATUS_REJECTED,
            ]
        ).select_related("created_by", "lead_organization")

        if stage:
            ppas = ppas.filter(approval_status=stage)

        return ppas.order_by("created_at")

    @classmethod
    def get_approval_metrics(cls, fiscal_year=None):
        """
        Calculate approval workflow metrics.

        Args:
            fiscal_year: Optional fiscal year filter

        Returns:
            dict: Metrics
        """
        from django.db.models import Count, Avg, F
        from django.db.models.functions import Cast
        from django.db.models.fields import FloatField

        ppas = MonitoringEntry.objects.all()

        if fiscal_year:
            ppas = ppas.filter(fiscal_year=fiscal_year)

        metrics = {
            "total_ppas": ppas.count(),
            "by_approval_status": dict(
                ppas.values("approval_status")
                .annotate(count=Count("id"))
                .values_list("approval_status", "count")
            ),
            "approved_count": ppas.filter(
                approval_status__in=[
                    MonitoringEntry.APPROVAL_STATUS_APPROVED,
                    MonitoringEntry.APPROVAL_STATUS_ENACTED,
                ]
            ).count(),
            "rejected_count": ppas.filter(
                approval_status=MonitoringEntry.APPROVAL_STATUS_REJECTED
            ).count(),
            "in_review_count": ppas.filter(
                approval_status__in=[
                    MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW,
                    MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW,
                    MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION,
                    MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL,
                ]
            ).count(),
        }

        # Calculate approval rate
        if metrics["total_ppas"] > 0:
            metrics["approval_rate"] = (
                metrics["approved_count"] / metrics["total_ppas"]
            ) * 100
        else:
            metrics["approval_rate"] = 0

        return metrics
