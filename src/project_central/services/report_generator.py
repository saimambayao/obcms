"""
Report Generator Service

Automated report generation for project management and budget monitoring.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.template.loader import render_to_string
from io import BytesIO
import csv

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Service for generating reports in various formats.

    Supports:
    - Portfolio performance reports
    - Budget utilization reports
    - Workflow progress reports
    - Cost-effectiveness reports
    - Multiple output formats (PDF, CSV, Excel)
    """

    @classmethod
    def generate_portfolio_report(cls, fiscal_year=None, output_format="dict"):
        """
        Generate comprehensive portfolio performance report.

        Args:
            fiscal_year: Fiscal year to report on (optional)
            output_format: Output format ('dict', 'csv', 'pdf')

        Returns:
            Report data in requested format
        """
        from project_central.services import AnalyticsService, WorkflowService
        from project_central.models import Alert

        # Gather data
        budget_by_sector = AnalyticsService.get_budget_allocation_by_sector(fiscal_year)
        budget_by_source = AnalyticsService.get_budget_allocation_by_source(fiscal_year)
        budget_by_region = AnalyticsService.get_budget_allocation_by_region(fiscal_year)
        utilization = AnalyticsService.get_utilization_rates(fiscal_year)
        cost_effectiveness = AnalyticsService.get_cost_effectiveness_metrics(
            fiscal_year=fiscal_year
        )
        workflow_metrics = WorkflowService.get_workflow_metrics(fiscal_year)
        alert_summary = Alert.objects.filter(is_active=True).count()

        report_data = {
            "report_type": "Portfolio Performance Report",
            "fiscal_year": fiscal_year or timezone.now().year,
            "generated_at": timezone.now().isoformat(),
            "summary": {
                "total_budget": budget_by_sector["totals"]["total_budget"],
                "total_projects": budget_by_sector["totals"]["project_count"],
                "budget_utilization": utilization["ppa_utilization"][
                    "disbursement_rate"
                ],
                "active_workflows": workflow_metrics["total_workflows"],
                "active_alerts": alert_summary,
            },
            "budget_allocation": {
                "by_sector": budget_by_sector,
                "by_source": budget_by_source,
                "by_region": budget_by_region,
            },
            "utilization_rates": utilization,
            "cost_effectiveness": cost_effectiveness,
            "workflow_performance": workflow_metrics,
        }

        if output_format == "dict":
            return report_data

        elif output_format == "csv":
            return cls._export_to_csv(report_data)

        elif output_format == "pdf":
            return cls._export_to_pdf(report_data, "portfolio_report.html")

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    @classmethod
    def generate_budget_utilization_report(
        cls, fiscal_year=None, sector=None, output_format="dict"
    ):
        """
        Generate detailed budget utilization report.

        Args:
            fiscal_year: Fiscal year to report on (optional)
            sector: Filter by sector (optional)
            output_format: Output format ('dict', 'csv')

        Returns:
            Report data in requested format
        """
        from monitoring.models import MonitoringEntry
        from project_central.models import BudgetCeiling

        # Get all approved PPAs
        queryset = MonitoringEntry.objects.filter(
            approval_status__in=[
                MonitoringEntry.APPROVAL_STATUS_APPROVED,
                MonitoringEntry.APPROVAL_STATUS_ENACTED,
            ]
        )

        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)

        if sector:
            queryset = queryset.filter(sector=sector)

        # Build detailed PPA list
        ppa_details = []
        for ppa in queryset:
            obligation_rate = 0
            disbursement_rate = 0

            if ppa.budget_allocation and ppa.budget_allocation > 0:
                obligation_rate = (
                    (ppa.total_obligated or 0) / ppa.budget_allocation * 100
                )
                disbursement_rate = (
                    (ppa.total_disbursed or 0) / ppa.budget_allocation * 100
                )

            ppa_details.append(
                {
                    "title": ppa.title,
                    "sector": ppa.sector,
                    "funding_source": ppa.funding_source,
                    "budget_allocation": float(ppa.budget_allocation or 0),
                    "total_obligated": float(ppa.total_obligated or 0),
                    "total_disbursed": float(ppa.total_disbursed or 0),
                    "obligation_rate": float(obligation_rate),
                    "disbursement_rate": float(disbursement_rate),
                    "status": ppa.status,
                    "progress": ppa.progress,
                }
            )

        # Get ceiling data
        ceiling_year = fiscal_year or timezone.now().year
        ceilings = BudgetCeiling.objects.filter(
            fiscal_year=ceiling_year,
            is_active=True,
        )

        ceiling_details = []
        for ceiling in ceilings:
            ceiling_details.append(
                {
                    "name": ceiling.name,
                    "ceiling_amount": float(ceiling.ceiling_amount),
                    "allocated_amount": float(ceiling.allocated_amount),
                    "utilization_pct": ceiling.get_utilization_percentage(),
                    "remaining_amount": float(ceiling.get_remaining_amount()),
                    "enforcement_level": ceiling.enforcement_level,
                }
            )

        report_data = {
            "report_type": "Budget Utilization Report",
            "fiscal_year": fiscal_year or timezone.now().year,
            "sector": sector or "All Sectors",
            "generated_at": timezone.now().isoformat(),
            "ppa_details": ppa_details,
            "ceiling_details": ceiling_details,
            "summary": {
                "total_ppas": len(ppa_details),
                "total_budget": sum(p["budget_allocation"] for p in ppa_details),
                "total_obligated": sum(p["total_obligated"] for p in ppa_details),
                "total_disbursed": sum(p["total_disbursed"] for p in ppa_details),
            },
        }

        if output_format == "dict":
            return report_data

        elif output_format == "csv":
            return cls._export_budget_utilization_to_csv(report_data)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    @classmethod
    def generate_workflow_progress_report(cls, fiscal_year=None, output_format="dict"):
        """
        Generate workflow progress report.

        Args:
            fiscal_year: Fiscal year to report on (optional)
            output_format: Output format ('dict', 'csv')

        Returns:
            Report data in requested format
        """
        from project_central.models import ProjectWorkflow
        from django.db.models import Q

        queryset = ProjectWorkflow.objects.all().select_related(
            "primary_need", "ppa", "project_lead", "mao_focal_person"
        )

        if fiscal_year:
            queryset = queryset.filter(
                Q(start_date__year=fiscal_year) | Q(ppa__fiscal_year=fiscal_year)
            )

        workflow_details = []
        for workflow in queryset:
            days_in_current_stage = (
                (timezone.now().date() - workflow.last_stage_change).days
                if workflow.last_stage_change
                else 0
            )

            workflow_details.append(
                {
                    "need_title": workflow.primary_need.title,
                    "current_stage": workflow.get_current_stage_display(),
                    "priority_level": workflow.get_priority_level_display(),
                    "project_lead": (
                        workflow.project_lead.get_full_name()
                        if workflow.project_lead
                        else "Unassigned"
                    ),
                    "mao_focal_person": (
                        workflow.mao_focal_person.name
                        if workflow.mao_focal_person
                        else "Not assigned"
                    ),
                    "is_on_track": workflow.is_on_track,
                    "is_blocked": workflow.is_blocked,
                    "days_in_current_stage": days_in_current_stage,
                    "target_completion_date": (
                        workflow.target_completion_date.isoformat()
                        if workflow.target_completion_date
                        else None
                    ),
                    "is_overdue": workflow.is_overdue(),
                    "ppa_title": workflow.ppa.title if workflow.ppa else "No PPA",
                    "estimated_budget": float(workflow.estimated_budget or 0),
                }
            )

        report_data = {
            "report_type": "Workflow Progress Report",
            "fiscal_year": fiscal_year or timezone.now().year,
            "generated_at": timezone.now().isoformat(),
            "workflow_details": workflow_details,
            "summary": {
                "total_workflows": len(workflow_details),
                "on_track": sum(1 for w in workflow_details if w["is_on_track"]),
                "blocked": sum(1 for w in workflow_details if w["is_blocked"]),
                "overdue": sum(1 for w in workflow_details if w["is_overdue"]),
            },
        }

        if output_format == "dict":
            return report_data

        elif output_format == "csv":
            return cls._export_workflow_progress_to_csv(report_data)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    @classmethod
    def generate_cost_effectiveness_report(cls, fiscal_year=None, output_format="dict"):
        """
        Generate cost-effectiveness analysis report.

        Args:
            fiscal_year: Fiscal year to report on (optional)
            output_format: Output format ('dict', 'csv')

        Returns:
            Report data in requested format
        """
        from project_central.services import AnalyticsService

        metrics = AnalyticsService.get_cost_effectiveness_metrics(
            fiscal_year=fiscal_year
        )

        report_data = {
            "report_type": "Cost-Effectiveness Report",
            "fiscal_year": fiscal_year or timezone.now().year,
            "generated_at": timezone.now().isoformat(),
            "overall_metrics": metrics["overall"],
            "sector_metrics": metrics["by_sector"],
        }

        if output_format == "dict":
            return report_data

        elif output_format == "csv":
            return cls._export_cost_effectiveness_to_csv(report_data)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    @classmethod
    def _export_to_csv(cls, report_data):
        """
        Export report data to CSV format.

        Args:
            report_data: Dictionary of report data

        Returns:
            BytesIO: CSV file buffer
        """
        output = BytesIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Report Type", report_data.get("report_type", "Report")])
        writer.writerow(["Generated At", report_data.get("generated_at", "")])
        writer.writerow([])

        # Write summary
        if "summary" in report_data:
            writer.writerow(["Summary"])
            for key, value in report_data["summary"].items():
                writer.writerow([key.replace("_", " ").title(), value])
            writer.writerow([])

        output.seek(0)
        return output

    @classmethod
    def _export_budget_utilization_to_csv(cls, report_data):
        """Export budget utilization report to CSV."""
        output = BytesIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Budget Utilization Report"])
        writer.writerow(["Fiscal Year", report_data["fiscal_year"]])
        writer.writerow(["Generated At", report_data["generated_at"]])
        writer.writerow([])

        # Write PPA details
        writer.writerow(["PPA Details"])
        writer.writerow(
            [
                "Title",
                "Sector",
                "Funding Source",
                "Budget Allocation",
                "Total Obligated",
                "Total Disbursed",
                "Obligation Rate %",
                "Disbursement Rate %",
                "Status",
                "Progress %",
            ]
        )

        for ppa in report_data["ppa_details"]:
            writer.writerow(
                [
                    ppa["title"],
                    ppa["sector"],
                    ppa["funding_source"],
                    ppa["budget_allocation"],
                    ppa["total_obligated"],
                    ppa["total_disbursed"],
                    ppa["obligation_rate"],
                    ppa["disbursement_rate"],
                    ppa["status"],
                    ppa["progress"],
                ]
            )

        writer.writerow([])

        # Write ceiling details
        writer.writerow(["Budget Ceiling Details"])
        writer.writerow(
            [
                "Name",
                "Ceiling Amount",
                "Allocated Amount",
                "Utilization %",
                "Remaining Amount",
                "Enforcement Level",
            ]
        )

        for ceiling in report_data["ceiling_details"]:
            writer.writerow(
                [
                    ceiling["name"],
                    ceiling["ceiling_amount"],
                    ceiling["allocated_amount"],
                    ceiling["utilization_pct"],
                    ceiling["remaining_amount"],
                    ceiling["enforcement_level"],
                ]
            )

        output.seek(0)
        return output

    @classmethod
    def _export_workflow_progress_to_csv(cls, report_data):
        """Export workflow progress report to CSV."""
        output = BytesIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Workflow Progress Report"])
        writer.writerow(["Fiscal Year", report_data["fiscal_year"]])
        writer.writerow(["Generated At", report_data["generated_at"]])
        writer.writerow([])

        # Write workflow details
        writer.writerow(
            [
                "Need Title",
                "Current Stage",
                "Priority",
                "Project Lead",
                "MAO Focal Person",
                "On Track",
                "Blocked",
                "Days in Stage",
                "Target Completion",
                "Overdue",
                "PPA",
                "Estimated Budget",
            ]
        )

        for workflow in report_data["workflow_details"]:
            writer.writerow(
                [
                    workflow["need_title"],
                    workflow["current_stage"],
                    workflow["priority_level"],
                    workflow["project_lead"],
                    workflow["mao_focal_person"],
                    "Yes" if workflow["is_on_track"] else "No",
                    "Yes" if workflow["is_blocked"] else "No",
                    workflow["days_in_current_stage"],
                    workflow["target_completion_date"] or "",
                    "Yes" if workflow["is_overdue"] else "No",
                    workflow["ppa_title"],
                    workflow["estimated_budget"],
                ]
            )

        output.seek(0)
        return output

    @classmethod
    def _export_cost_effectiveness_to_csv(cls, report_data):
        """Export cost-effectiveness report to CSV."""
        output = BytesIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Cost-Effectiveness Report"])
        writer.writerow(["Fiscal Year", report_data["fiscal_year"]])
        writer.writerow(["Generated At", report_data["generated_at"]])
        writer.writerow([])

        # Write overall metrics
        writer.writerow(["Overall Metrics"])
        for key, value in report_data["overall_metrics"].items():
            writer.writerow([key.replace("_", " ").title(), value])

        writer.writerow([])

        # Write sector metrics
        writer.writerow(["Sector Metrics"])
        writer.writerow(
            [
                "Sector",
                "Total Budget",
                "Total Beneficiaries",
                "Avg Cost per Beneficiary",
                "Project Count",
            ]
        )

        for sector in report_data["sector_metrics"]:
            writer.writerow(
                [
                    sector["sector"],
                    sector["total_budget"],
                    sector["total_beneficiaries"],
                    sector["avg_cost_per_beneficiary"],
                    sector["project_count"],
                ]
            )

        output.seek(0)
        return output

    @classmethod
    def _export_to_pdf(cls, report_data, template_name):
        """
        Export report data to PDF format.

        Args:
            report_data: Dictionary of report data
            template_name: Name of template to use

        Returns:
            BytesIO: PDF file buffer

        Note:
            Requires weasyprint or similar PDF library.
            This is a placeholder implementation.
        """
        # Placeholder for PDF generation
        # In Phase 2, implement with weasyprint or reportlab
        logger.warning("PDF export not yet implemented")
        raise NotImplementedError("PDF export will be implemented in Phase 2")
