"""
Analytics Service

Aggregates MonitoringEntry data for dashboards, reports, and decision support.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, Optional

from django.db.models import Count, Q
from django.utils import timezone

from monitoring.models import MonitoringEntry
from project_central.models import ProjectWorkflow


DECIMAL_ZERO = Decimal("0")
SECTOR_LABELS = dict(MonitoringEntry.SECTOR_CHOICES)


def _safe_decimal(value: Optional[Decimal]) -> Decimal:
    """Convert None to Decimal zero."""
    return Decimal(value) if isinstance(value, Decimal) else Decimal(value or 0)


@dataclass
class _AggregationTotals:
    budget: Decimal = DECIMAL_ZERO
    allocations: Decimal = DECIMAL_ZERO
    obligations: Decimal = DECIMAL_ZERO
    disbursements: Decimal = DECIMAL_ZERO
    beneficiaries: int = 0
    projects: int = 0


class AnalyticsService:
    """Domain analytics for the project management portal."""

    # --------------------------------------------------------------------- #
    # Private helpers
    # --------------------------------------------------------------------- #

    @classmethod
    def _monitoring_queryset(cls, fiscal_year: Optional[int] = None):
        qs = MonitoringEntry.objects.all()
        if fiscal_year:
            qs = qs.filter(fiscal_year=fiscal_year)
        return qs.select_related("coverage_region")

    @classmethod
    def _aggregate_entries(cls, entries: Iterable[MonitoringEntry]) -> _AggregationTotals:
        totals = _AggregationTotals()
        for entry in entries:
            totals.projects += 1
            totals.budget += _safe_decimal(entry.budget_allocation)
            totals.allocations += entry.total_allocations
            totals.obligations += entry.total_obligations
            totals.disbursements += entry.total_disbursements
            totals.beneficiaries += entry.total_slots or 0
        return totals

    # --------------------------------------------------------------------- #
    # Budget allocation analytics
    # --------------------------------------------------------------------- #

    @classmethod
    def get_budget_allocation_by_sector(cls, fiscal_year: Optional[int] = None) -> Dict:
        """
        Aggregate budget allocation and utilization statistics by sector.
        """
        entries = list(cls._monitoring_queryset(fiscal_year))
        sector_map: Dict[str, Dict] = defaultdict(
            lambda: {
                "sector": "unspecified",
                "sector_label": "Unspecified",
                "project_count": 0,
                "total_budget": DECIMAL_ZERO,
                "total_allocations": DECIMAL_ZERO,
                "total_obligations": DECIMAL_ZERO,
                "total_disbursed": DECIMAL_ZERO,
            }
        )

        overall = _AggregationTotals()

        for entry in entries:
            sector_key = entry.sector or "unspecified"
            bucket = sector_map[sector_key]
            bucket["sector"] = sector_key
            bucket["sector_label"] = SECTOR_LABELS.get(sector_key, "Unspecified")
            bucket["project_count"] += 1
            budget = _safe_decimal(entry.budget_allocation)
            bucket["total_budget"] += budget
            bucket["total_allocations"] += entry.total_allocations
            bucket["total_obligations"] += entry.total_obligations
            bucket["total_disbursed"] += entry.total_disbursements

            overall.projects += 1
            overall.budget += budget
            overall.allocations += entry.total_allocations
            overall.obligations += entry.total_obligations
            overall.disbursements += entry.total_disbursements

        sectors = []
        for data in sector_map.values():
            obligations = data["total_obligations"]
            allocations = data["total_allocations"]

            data["obligation_rate"] = (
                float((obligations / data["total_budget"]) * 100)
                if data["total_budget"] > 0
                else 0.0
            )
            data["disbursement_rate"] = (
                float((data["total_disbursed"] / obligations) * 100)
                if obligations > 0
                else 0.0
            )
            data["total_budget"] = float(data["total_budget"])
            data["total_allocations"] = float(data["total_allocations"])
            data["total_obligations"] = float(obligations)
            data["total_disbursed"] = float(data["total_disbursed"])
            sectors.append(data)

        sectors.sort(key=lambda item: item["total_budget"], reverse=True)

        summary = {
            "total_budget": float(overall.budget),
            "total_allocations": float(overall.allocations),
            "total_obligations": float(overall.obligations),
            "total_disbursed": float(overall.disbursements),
            "project_count": overall.projects,
        }

        return {
            "fiscal_year": fiscal_year or timezone.now().year,
            "sectors": sectors,
            "totals": summary,
            "top_sectors": sectors[:5],
        }

    @classmethod
    def get_budget_allocation_by_source(cls, fiscal_year: Optional[int] = None) -> Dict:
        """
        Aggregate budget allocation by funding source.
        """
        entries = cls._monitoring_queryset(fiscal_year)
        sources: Dict[str, Dict] = defaultdict(
            lambda: {
                "funding_source": "unspecified",
                "project_count": 0,
                "total_budget": DECIMAL_ZERO,
                "total_disbursed": DECIMAL_ZERO,
            }
        )
        total_budget = DECIMAL_ZERO
        total_projects = 0

        for entry in entries:
            source = entry.funding_source or "unspecified"
            label = source.replace("_", " ").title()
            if source == "other" and entry.funding_source_other:
                label = entry.funding_source_other

            bucket = sources[source]
            bucket["funding_source"] = label
            bucket["project_count"] += 1
            budget = _safe_decimal(entry.budget_allocation)
            bucket["total_budget"] += budget
            bucket["total_disbursed"] += entry.total_disbursements

            total_budget += budget
            total_projects += 1

        data = []
        for bucket in sources.values():
            bucket["total_budget"] = float(bucket["total_budget"])
            bucket["total_disbursed"] = float(bucket["total_disbursed"])
            data.append(bucket)

        data.sort(key=lambda item: item["total_budget"], reverse=True)

        return {
            "fiscal_year": fiscal_year or timezone.now().year,
            "sources": data,
            "totals": {
                "total_budget": float(total_budget),
                "project_count": total_projects,
            },
        }

    @classmethod
    def get_budget_allocation_by_region(cls, fiscal_year: Optional[int] = None) -> Dict:
        """
        Aggregate budget allocation by geographic coverage region.
        """
        entries = cls._monitoring_queryset(fiscal_year)
        regions: Dict[str, Dict] = defaultdict(
            lambda: {
                "region": "Unspecified",
                "project_count": 0,
                "total_budget": DECIMAL_ZERO,
            }
        )

        for entry in entries:
            region_name = (
                entry.coverage_region.name if entry.coverage_region else "Unspecified"
            )
            bucket = regions[region_name]
            bucket["region"] = region_name
            bucket["project_count"] += 1
            bucket["total_budget"] += _safe_decimal(entry.budget_allocation)

        region_list = []
        for bucket in regions.values():
            bucket["total_budget"] = float(bucket["total_budget"])
            region_list.append(bucket)

        region_list.sort(key=lambda item: item["total_budget"], reverse=True)

        return {
            "fiscal_year": fiscal_year or timezone.now().year,
            "regions": region_list,
        }

    # --------------------------------------------------------------------- #
    # Utilization & effectiveness analytics
    # --------------------------------------------------------------------- #

    @classmethod
    def get_utilization_rates(cls, fiscal_year: Optional[int] = None) -> Dict:
        """
        Compute organization-wide budget utilization metrics.
        """
        entries = cls._monitoring_queryset(fiscal_year)
        totals = cls._aggregate_entries(entries)

        by_status = dict(
            entries.values("status").annotate(count=Count("id")).values_list("status", "count")
        )

        return {
            "fiscal_year": fiscal_year or timezone.now().year,
            "ppa_utilization": {
                "total_budget": float(totals.budget),
                "total_allocations": float(totals.allocations),
                "total_obligations": float(totals.obligations),
                "total_disbursed": float(totals.disbursements),
                "obligation_rate": float(
                    (totals.obligations / totals.budget * 100)
                    if totals.budget > 0
                    else 0.0
                ),
                "disbursement_rate": float(
                    (totals.disbursements / totals.obligations * 100)
                    if totals.obligations > 0
                    else 0.0
                ),
                "budget_utilization_rate": float(
                    (totals.disbursements / totals.budget * 100)
                    if totals.budget > 0
                    else 0.0
                ),
            },
            "status_breakdown": by_status,
        }

    @classmethod
    def get_cost_effectiveness_metrics(
        cls, sector: Optional[str] = None, fiscal_year: Optional[int] = None
    ) -> Dict:
        """
        Summarize cost-per-beneficiary and rating distribution.
        """
        entries = cls._monitoring_queryset(fiscal_year)
        if sector:
            entries = entries.filter(sector=sector)

        total_budget = DECIMAL_ZERO
        total_beneficiaries = 0
        rating_counts = defaultdict(int)
        top_entries = []

        for entry in entries:
            total_budget += _safe_decimal(entry.budget_allocation)
            total_beneficiaries += entry.total_slots or 0
            if entry.cost_effectiveness_rating:
                rating_counts[entry.cost_effectiveness_rating] += 1
            cost_per_beneficiary = (
                float(entry.cost_per_beneficiary)
                if entry.cost_per_beneficiary
                else None
            )
            top_entries.append(
                {
                    "title": entry.title,
                    "sector": entry.sector,
                    "budget_allocation": float(_safe_decimal(entry.budget_allocation)),
                    "total_slots": entry.total_slots or 0,
                    "cost_per_beneficiary": cost_per_beneficiary,
                    "rating": entry.cost_effectiveness_rating or "unrated",
                }
            )

        top_entries = [
            e for e in top_entries if e["cost_per_beneficiary"] is not None
        ]
        top_entries.sort(key=lambda item: item["cost_per_beneficiary"])

        avg_cost_per_beneficiary = (
            float(total_budget / total_beneficiaries)
            if total_beneficiaries > 0
            else 0.0
        )

        return {
            "fiscal_year": fiscal_year or timezone.now().year,
            "sector": sector,
            "summary": {
                "total_budget": float(total_budget),
                "total_beneficiaries": total_beneficiaries,
                "average_cost_per_beneficiary": avg_cost_per_beneficiary,
            },
            "rating_distribution": dict(rating_counts),
            "top_programs": top_entries[:5],
        }

    # --------------------------------------------------------------------- #
    # Dashboard aggregate
    # --------------------------------------------------------------------- #

    @classmethod
    def get_dashboard_summary(cls, fiscal_year: Optional[int] = None) -> Dict:
        """
        Aggregate high-level analytics for dashboards and scheduled reports.
        """
        fiscal_year = fiscal_year or timezone.now().year

        budget_by_sector = cls.get_budget_allocation_by_sector(fiscal_year)
        budget_by_source = cls.get_budget_allocation_by_source(fiscal_year)
        budget_by_region = cls.get_budget_allocation_by_region(fiscal_year)
        utilization_rates = cls.get_utilization_rates(fiscal_year)
        cost_effectiveness = cls.get_cost_effectiveness_metrics(fiscal_year=fiscal_year)
        workflow_performance = cls._get_workflow_performance(fiscal_year)

        return {
            "fiscal_year": fiscal_year,
            "budget_by_sector": budget_by_sector,
            "budget_by_source": budget_by_source,
            "budget_by_region": budget_by_region,
            "utilization_rates": utilization_rates,
            "cost_effectiveness": cost_effectiveness,
            "workflow_performance": workflow_performance,
        }

    @classmethod
    def _get_workflow_performance(cls, fiscal_year: Optional[int] = None) -> Dict:
        """
        Summarize workflow metrics for dashboard contexts.
        """
        workflows = ProjectWorkflow.objects.all()
        if fiscal_year:
            workflows = workflows.filter(
                Q(start_date__year=fiscal_year) | Q(ppa__fiscal_year=fiscal_year)
            )

        total_workflows = workflows.count()
        on_track = workflows.filter(is_on_track=True).count()
        blocked = workflows.filter(is_blocked=True).count()

        return {
            "total_workflows": total_workflows,
            "on_track": on_track,
            "blocked": blocked,
            "by_stage": dict(
                workflows.values("current_stage")
                .annotate(count=Count("id"))
                .values_list("current_stage", "count")
            ),
        }


__all__ = ["AnalyticsService"]
