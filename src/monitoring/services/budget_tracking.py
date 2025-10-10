"""Utilities for building MOA budget tracking context."""

from collections import defaultdict
from decimal import Decimal
from typing import Iterable, Mapping, MutableMapping, Sequence

from common.work_item_model import WorkItem
from monitoring.models import MonitoringEntry


def _normalise_decimal(value) -> Decimal:
    """Return a Decimal value, falling back to 0.00 when None or empty."""
    if value in (None, ""):
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _aggregate_work_items(ppas: Sequence[MonitoringEntry]) -> MutableMapping[str, list[WorkItem]]:
    """Return a mapping of PPA ID to related work items for faster lookups."""
    work_items = WorkItem.objects.filter(
        related_ppa__in=ppas,
    ).exclude(
        parent__isnull=True,
        auto_calculate_progress=True,
    ).only(
        "related_ppa_id",
        "allocated_budget",
        "actual_expenditure",
    )
    grouped: MutableMapping[str, list[WorkItem]] = defaultdict(list)
    for item in work_items:
        grouped[str(item.related_ppa_id)].append(item)
    return grouped


def build_moa_budget_tracking(
    organization,
    moa_ppas: Iterable[MonitoringEntry] | None = None,
) -> Mapping[str, object]:
    """
    Compute budget tracking details for an organization's MOA PPAs.

    Returns a dictionary containing:
        - ``moa_ppas``: list of MonitoringEntry instances annotated with budget values
        - ``moa_budget_stats``: overall totals and utilization metrics
    """
    default_stats = {
        "total_budget": Decimal("0.00"),
        "total_allocated": Decimal("0.00"),
        "total_work_item_budget": Decimal("0.00"),
        "total_expenditure": Decimal("0.00"),
        "utilization_rate": 0.0,
        "total_variance": Decimal("0.00"),
        "has_work_item_budget": False,
    }

    if organization is None:
        return {"moa_ppas": [], "moa_budget_stats": default_stats}

    if moa_ppas is None:
        moa_ppas_query = (
            MonitoringEntry.objects.filter(
                category="moa_ppa",
                implementing_moa=organization,
            )
            .select_related("implementing_moa")
            .order_by("-updated_at")
        )
        moa_ppas_list = list(moa_ppas_query)
    else:
        moa_ppas_list = list(moa_ppas)

    if not moa_ppas_list or getattr(organization, "organization_type", "") != "bmoa":
        return {"moa_ppas": moa_ppas_list, "moa_budget_stats": default_stats}

    grouped_work_items = _aggregate_work_items(moa_ppas_list)

    total_budget = Decimal("0.00")
    total_allocated = Decimal("0.00")
    total_expenditure = Decimal("0.00")
    has_work_item_budget = False

    for ppa in moa_ppas_list:
        ppa_budget = _normalise_decimal(ppa.budget_allocation)
        total_budget += ppa_budget

        work_items = grouped_work_items.get(str(ppa.pk), [])
        ppa_allocated = sum(
            (_normalise_decimal(item.allocated_budget) for item in work_items),
            Decimal("0.00"),
        )
        ppa_expenditure = sum(
            (_normalise_decimal(item.actual_expenditure) for item in work_items),
            Decimal("0.00"),
        )

        ppa.work_item_budget = ppa_allocated
        ppa.total_expenditure = ppa_expenditure
        ppa.variance = ppa_budget - ppa_expenditure
        ppa.utilization_rate = (
            float((ppa_expenditure / ppa_budget) * 100)
            if ppa_budget > Decimal("0.00")
            else 0.0
        )
        ppa.has_work_item_budget = ppa_allocated > Decimal("0.00")

        total_allocated += ppa_allocated
        total_expenditure += ppa_expenditure
        if ppa_allocated > Decimal("0.00"):
            has_work_item_budget = True

    utilization_rate = (
        float((total_expenditure / total_budget) * 100)
        if total_budget > Decimal("0.00")
        else 0.0
    )

    moa_budget_stats = {
        "total_budget": total_budget,
        "total_allocated": total_allocated,
        "total_work_item_budget": total_allocated,  # Sum of all work item allocated budgets
        "total_expenditure": total_expenditure,
        "utilization_rate": utilization_rate,
        "total_variance": total_budget - total_expenditure,
        "has_work_item_budget": has_work_item_budget,
    }

    return {"moa_ppas": moa_ppas_list, "moa_budget_stats": moa_budget_stats}
