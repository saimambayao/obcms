"""Prioritization matrix for linking MANA assessments to budget PPAs."""

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import render

from common.decorators.rbac import require_feature_access
from mana.models import Assessment, Need
from .models import MonitoringEntry


@login_required
@require_feature_access('monitoring_access')
def prioritization_matrix(request):
    """
    Display prioritization matrix linking MANA needs to PPAs.

    Helps planners identify:
    - High-priority needs without budget allocation
    - Budget allocations without linked assessments
    - Coverage gaps by sector and region
    """
    # Get all active assessments
    assessments = (
        Assessment.objects.filter(status__in=["ongoing", "completed"])
        .select_related("community", "category")
        .prefetch_related("needs")
    )

    # Get all PPAs
    ppas = MonitoringEntry.objects.select_related(
        "related_assessment", "coverage_region", "lead_organization"
    ).all()

    # Calculate priority matrix
    matrix_data = []

    for assessment in assessments:
        needs = assessment.needs.all()
        linked_ppas = ppas.filter(related_assessment=assessment)

        total_needs = needs.count()
        critical_needs = (
            needs.filter(severity="critical").count()
            if hasattr(Need, "severity")
            else 0
        )
        high_needs = (
            needs.filter(severity="high").count() if hasattr(Need, "severity") else 0
        )

        total_budget = linked_ppas.aggregate(total=Sum("budget_allocation"))[
            "total"
        ] or Decimal("0.00")

        # Calculate priority score (simplified algorithm)
        priority_score = 0
        if total_needs > 0:
            priority_score += (critical_needs * 3) + (high_needs * 2)
            if total_budget == 0:
                priority_score += 5  # Boost for unfunded needs

        matrix_data.append(
            {
                "assessment": assessment,
                "total_needs": total_needs,
                "critical_needs": critical_needs,
                "high_needs": high_needs,
                "linked_ppas_count": linked_ppas.count(),
                "total_budget": total_budget,
                "priority_score": priority_score,
                "has_funding_gap": total_needs > 0 and total_budget == 0,
                "urgency": (
                    "critical"
                    if priority_score >= 10
                    else "high" if priority_score >= 5 else "medium"
                ),
            }
        )

    # Sort by priority score descending
    matrix_data = sorted(matrix_data, key=lambda x: x["priority_score"], reverse=True)

    # Calculate summary stats
    total_assessments = len(matrix_data)
    assessments_with_gaps = sum(1 for item in matrix_data if item["has_funding_gap"])
    total_unfunded_needs = sum(
        item["total_needs"] for item in matrix_data if item["has_funding_gap"]
    )

    # Sector coverage analysis
    sector_coverage = {}
    for ppa in ppas:
        if ppa.sector:
            if ppa.sector not in sector_coverage:
                sector_coverage[ppa.sector] = {
                    "ppa_count": 0,
                    "total_budget": Decimal("0.00"),
                    "assessment_count": 0,
                }
            sector_coverage[ppa.sector]["ppa_count"] += 1
            sector_coverage[ppa.sector][
                "total_budget"
            ] += ppa.budget_allocation or Decimal("0.00")

    # Count assessments per sector (simplified - would need sector field on Assessment)
    for item in matrix_data:
        if item["assessment"].category:
            # This is simplified - in real implementation, map category to sector
            pass

    context = {
        "matrix_data": matrix_data,
        "total_assessments": total_assessments,
        "assessments_with_gaps": assessments_with_gaps,
        "gap_percentage": (
            (assessments_with_gaps / total_assessments * 100)
            if total_assessments > 0
            else 0
        ),
        "total_unfunded_needs": total_unfunded_needs,
        "sector_coverage": sector_coverage,
    }

    return render(request, "monitoring/prioritization_matrix.html", context)
