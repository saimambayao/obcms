"""
Alert Service

Automated alert generation for project management and budget monitoring.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q, Sum, Count, F
from decimal import Decimal

from project_central.models import Alert, BudgetCeiling, ProjectWorkflow
from mana.models import Need
from monitoring.models import MonitoringEntry
from coordination.models import Organization

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service for automated alert generation.

    Generates alerts for:
    - Unfunded high-priority needs
    - Overdue PPAs
    - Pending quarterly reports
    - Budget ceiling warnings
    - Policy implementation delays
    - Approval bottlenecks
    - Disbursement delays
    - Under/overspending
    """

    @classmethod
    def generate_daily_alerts(cls):
        """
        Generate all daily alerts.

        This is the main entry point called by Celery daily task.

        Returns:
            dict: Summary of alerts generated
        """
        logger.info("Starting daily alert generation")

        results = {
            "unfunded_needs": 0,
            "overdue_ppas": 0,
            "pending_reports": 0,
            "budget_ceilings": 0,
            "policy_lagging": 0,
            "approval_bottlenecks": 0,
            "disbursement_delays": 0,
            "underspending": 0,
            "overspending": 0,
            "workflow_blocked": 0,
            "total": 0,
            "errors": [],
        }

        # Clean up expired alerts first
        expired_count = Alert.cleanup_expired_alerts()
        logger.info(f"Cleaned up {expired_count} expired alerts")

        # Generate each type of alert
        try:
            results["unfunded_needs"] = cls.generate_unfunded_needs_alerts()
        except Exception as e:
            logger.error(f"Error generating unfunded needs alerts: {e}", exc_info=True)
            results["errors"].append(f"unfunded_needs: {str(e)}")

        try:
            results["overdue_ppas"] = cls.generate_overdue_ppa_alerts()
        except Exception as e:
            logger.error(f"Error generating overdue PPA alerts: {e}", exc_info=True)
            results["errors"].append(f"overdue_ppas: {str(e)}")

        try:
            results["budget_ceilings"] = cls.generate_budget_ceiling_alerts()
        except Exception as e:
            logger.error(f"Error generating budget ceiling alerts: {e}", exc_info=True)
            results["errors"].append(f"budget_ceilings: {str(e)}")

        try:
            results["approval_bottlenecks"] = cls.generate_approval_bottleneck_alerts()
        except Exception as e:
            logger.error(
                f"Error generating approval bottleneck alerts: {e}", exc_info=True
            )
            results["errors"].append(f"approval_bottlenecks: {str(e)}")

        try:
            results["disbursement_delays"] = cls.generate_disbursement_delay_alerts()
        except Exception as e:
            logger.error(
                f"Error generating disbursement delay alerts: {e}", exc_info=True
            )
            results["errors"].append(f"disbursement_delays: {str(e)}")

        try:
            results["underspending"] = cls.generate_underspending_alerts()
        except Exception as e:
            logger.error(f"Error generating underspending alerts: {e}", exc_info=True)
            results["errors"].append(f"underspending: {str(e)}")

        try:
            results["overspending"] = cls.generate_overspending_alerts()
        except Exception as e:
            logger.error(f"Error generating overspending alerts: {e}", exc_info=True)
            results["errors"].append(f"overspending: {str(e)}")

        try:
            results["workflow_blocked"] = cls.generate_workflow_blocked_alerts()
        except Exception as e:
            logger.error(
                f"Error generating workflow blocked alerts: {e}", exc_info=True
            )
            results["errors"].append(f"workflow_blocked: {str(e)}")

        results["total"] = sum(v for k, v in results.items() if isinstance(v, int))

        logger.info(
            f"Daily alert generation complete. Total alerts: {results['total']}"
        )
        return results

    @classmethod
    def generate_unfunded_needs_alerts(cls):
        """Generate alerts for unfunded high-priority needs."""
        # Find high-priority needs without linked PPAs
        unfunded_needs = Need.objects.filter(
            Q(linked_ppa__isnull=True),
            Q(priority_score__gte=4.0),
            Q(status__in=["validated", "prioritized"]),
        ).select_related("community", "assessment")

        # Check if alert already exists for these needs
        existing_alert_need_ids = Alert.objects.filter(
            alert_type="unfunded_needs",
            is_active=True,
        ).values_list("related_need_id", flat=True)

        count = 0
        for need in unfunded_needs:
            # Skip if alert already exists for this need
            if need.id in existing_alert_need_ids:
                continue

            # Calculate estimated budget
            estimated_budget = getattr(need, "estimated_cost", None) or 0

            alert = Alert.create_alert(
                alert_type="unfunded_needs",
                severity="high" if need.priority_score >= 4.5 else "medium",
                title=f"Unfunded High-Priority Need: {need.title}",
                description=f"This need has priority score {need.priority_score:.1f} but no PPA has been created to address it. Estimated budget: ₱{estimated_budget:,.2f}",
                related_need=need,
                action_url=f"/admin/mana/need/{need.id}/change/",
                alert_data={
                    "need_id": need.id,
                    "priority_score": float(need.priority_score),
                    "estimated_budget": float(estimated_budget),
                },
                expires_at=timezone.now() + timedelta(days=30),
            )
            count += 1
            logger.info(f"Created unfunded needs alert for need {need.id}")

        return count

    @classmethod
    def generate_overdue_ppa_alerts(cls):
        """Generate alerts for overdue PPAs."""
        # Find PPAs with missed milestones or overdue target dates
        overdue_ppas = MonitoringEntry.objects.filter(
            status="ongoing",
        ).select_related("lead_organization")

        count = 0
        for ppa in overdue_ppas:
            # Check if there's a target end date and if it's overdue
            target_end = getattr(ppa, "target_end_date", None)
            if target_end and target_end < timezone.now().date():
                days_overdue = (timezone.now().date() - target_end).days

                # Check if alert already exists
                existing_alert = Alert.objects.filter(
                    alert_type="overdue_ppa",
                    related_ppa=ppa,
                    is_active=True,
                ).exists()

                if not existing_alert:
                    Alert.create_alert(
                        alert_type="overdue_ppa",
                        severity="high" if days_overdue > 30 else "medium",
                        title=f"PPA Overdue: {ppa.title}",
                        description=f"This PPA is {days_overdue} days past its target end date ({target_end}). Current progress: {ppa.progress}%",
                        related_ppa=ppa,
                        action_url=f"/monitoring/entry/{ppa.id}/",
                        alert_data={
                            "ppa_id": ppa.id,
                            "days_overdue": days_overdue,
                            "progress": ppa.progress,
                        },
                    )
                    count += 1

        return count

    @classmethod
    def generate_budget_ceiling_alerts(cls):
        """Generate alerts for budget ceilings approaching limits."""
        current_year = timezone.now().year

        ceilings = BudgetCeiling.objects.filter(
            fiscal_year=current_year,
            is_active=True,
        )

        count = 0
        for ceiling in ceilings:
            utilization_pct = ceiling.get_utilization_percentage()

            # Alert at 90% threshold
            if utilization_pct >= 90:
                # Check if recent alert exists (within last 7 days)
                recent_alert = Alert.objects.filter(
                    alert_type="budget_ceiling",
                    alert_data__ceiling_id=str(ceiling.id),
                    is_active=True,
                    created_at__gte=timezone.now() - timedelta(days=7),
                ).exists()

                if not recent_alert:
                    Alert.create_alert(
                        alert_type="budget_ceiling",
                        severity="critical" if utilization_pct >= 98 else "high",
                        title=f"Budget Ceiling Alert: {ceiling.name}",
                        description=f"Budget ceiling at {utilization_pct:.1f}% utilization. Allocated: ₱{ceiling.allocated_amount:,.2f} of ₱{ceiling.ceiling_amount:,.2f}. Remaining: ₱{ceiling.get_remaining_amount():,.2f}",
                        action_url=f"/admin/project_central/budgetceiling/{ceiling.id}/change/",
                        alert_data={
                            "ceiling_id": str(ceiling.id),
                            "utilization_pct": utilization_pct,
                            "allocated_amount": float(ceiling.allocated_amount),
                            "ceiling_amount": float(ceiling.ceiling_amount),
                            "remaining_amount": float(ceiling.get_remaining_amount()),
                        },
                        expires_at=timezone.now() + timedelta(days=14),
                    )
                    count += 1

        return count

    @classmethod
    def generate_approval_bottleneck_alerts(cls):
        """Generate alerts for PPAs stuck in approval stages."""
        # Find PPAs in approval for more than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)

        stuck_ppas = MonitoringEntry.objects.filter(
            approval_status__in=[
                MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW,
                MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW,
                MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION,
                MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL,
            ],
            created_at__lt=cutoff_date,
        )

        count = 0
        for ppa in stuck_ppas:
            # Check if alert already exists
            existing_alert = Alert.objects.filter(
                alert_type="approval_bottleneck",
                related_ppa=ppa,
                is_active=True,
            ).exists()

            if not existing_alert:
                days_in_approval = (timezone.now() - ppa.created_at).days

                Alert.create_alert(
                    alert_type="approval_bottleneck",
                    severity="high" if days_in_approval > 60 else "medium",
                    title=f"Approval Bottleneck: {ppa.title}",
                    description=f"PPA has been in {ppa.get_approval_status_display()} stage for {days_in_approval} days. Budget: ₱{ppa.budget_allocation:,.2f}",
                    related_ppa=ppa,
                    action_url=reverse("monitoring:monitoring_entry_detail", kwargs={"entry_id": ppa.id}),
                    alert_data={
                        "ppa_id": ppa.id,
                        "days_in_approval": days_in_approval,
                        "approval_status": ppa.approval_status,
                    },
                )
                count += 1

        return count

    @classmethod
    def generate_disbursement_delay_alerts(cls):
        """Generate alerts for PPAs with low disbursement rates."""
        # Find ongoing PPAs with low disbursement rates
        ongoing_ppas = MonitoringEntry.objects.filter(
            status="ongoing",
            budget_allocation__gt=0,
        )

        count = 0
        for ppa in ongoing_ppas:
            # Calculate disbursement rate (would need FundingFlow model)
            # For now, create stub logic
            # In full implementation, calculate from FundingFlow records

            # Placeholder: Check if progress is high but no recent disbursement records
            if ppa.progress >= 50:
                # Would check FundingFlow here
                # For now, skip this alert type
                pass

        return count

    @classmethod
    def generate_underspending_alerts(cls):
        """Generate alerts for PPAs with low budget utilization."""
        # Find PPAs with low obligation rates relative to time elapsed
        ongoing_ppas = MonitoringEntry.objects.filter(
            status="ongoing",
            budget_allocation__gt=0,
        )

        count = 0
        for ppa in ongoing_ppas:
            # Calculate expected vs actual spending
            # This would require start_date and FundingFlow data
            # Placeholder implementation
            if ppa.progress < 30:
                # Would calculate budget utilization rate here
                pass

        return count

    @classmethod
    def generate_overspending_alerts(cls):
        """Generate alerts for PPAs exceeding budget allocation."""
        # Would require FundingFlow data to calculate actual spending
        # Placeholder implementation
        return 0

    @classmethod
    def generate_workflow_blocked_alerts(cls):
        """Generate alerts for blocked workflows."""
        blocked_workflows = ProjectWorkflow.objects.filter(
            is_blocked=True,
            is_on_track=False,
        ).select_related("primary_need", "project_lead")

        count = 0
        for workflow in blocked_workflows:
            # Check if alert already exists
            existing_alert = Alert.objects.filter(
                alert_type="workflow_blocked",
                related_workflow=workflow,
                is_active=True,
            ).exists()

            if not existing_alert:
                Alert.create_alert(
                    alert_type="workflow_blocked",
                    severity="high",
                    title=f"Workflow Blocked: {workflow.primary_need.title}",
                    description=f"Workflow is blocked: {workflow.blocker_description or 'No description provided'}. Current stage: {workflow.get_current_stage_display()}",
                    related_workflow=workflow,
                    action_url=workflow.get_absolute_url(),
                    alert_data={
                        "workflow_id": str(workflow.id),
                        "current_stage": workflow.current_stage,
                    },
                )
                count += 1

        return count

    @classmethod
    def deactivate_resolved_alerts(cls):
        """Deactivate alerts that are no longer relevant."""
        # Deactivate unfunded needs alerts where need now has PPA
        unfunded_alerts = Alert.objects.filter(
            alert_type="unfunded_needs",
            is_active=True,
            related_need__isnull=False,
        ).select_related("related_need")

        count = 0
        for alert in unfunded_alerts:
            if alert.related_need.linked_ppa:
                alert.deactivate("Need now has linked PPA")
                count += 1

        # Deactivate overdue PPA alerts where PPA is now completed
        overdue_alerts = Alert.objects.filter(
            alert_type="overdue_ppa",
            is_active=True,
            related_ppa__isnull=False,
        ).select_related("related_ppa")

        for alert in overdue_alerts:
            if alert.related_ppa.status == "completed":
                alert.deactivate("PPA completed")
                count += 1

        # Deactivate approval bottleneck alerts where PPA is now approved
        approval_alerts = Alert.objects.filter(
            alert_type="approval_bottleneck",
            is_active=True,
            related_ppa__isnull=False,
        ).select_related("related_ppa")

        for alert in approval_alerts:
            if alert.related_ppa.approval_status in [
                MonitoringEntry.APPROVAL_STATUS_APPROVED,
                MonitoringEntry.APPROVAL_STATUS_ENACTED,
            ]:
                alert.deactivate("PPA approved")
                count += 1

        # Deactivate workflow blocked alerts where workflow is no longer blocked
        blocked_alerts = Alert.objects.filter(
            alert_type="workflow_blocked",
            is_active=True,
            related_workflow__isnull=False,
        ).select_related("related_workflow")

        for alert in blocked_alerts:
            if not alert.related_workflow.is_blocked:
                alert.deactivate("Workflow no longer blocked")
                count += 1

        logger.info(f"Deactivated {count} resolved alerts")
        return count

    @classmethod
    def get_alert_summary(cls):
        """
        Get summary of current active alerts.

        Returns:
            dict: Alert summary metrics
        """
        active_alerts = Alert.objects.filter(is_active=True)

        summary = {
            "total_active": active_alerts.count(),
            "unacknowledged": active_alerts.filter(is_acknowledged=False).count(),
            "by_severity": dict(
                active_alerts.values("severity")
                .annotate(count=Count("id"))
                .values_list("severity", "count")
            ),
            "by_type": dict(
                active_alerts.values("alert_type")
                .annotate(count=Count("id"))
                .values_list("alert_type", "count")
            ),
            "critical_unacknowledged": active_alerts.filter(
                severity="critical", is_acknowledged=False
            ).count(),
        }

        return summary
