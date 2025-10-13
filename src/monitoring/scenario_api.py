"""Scenario planning API endpoints for budget what-if analysis."""

from decimal import Decimal

from django.db import models
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.utils.permissions import HasFeatureAccess
from .models import MonitoringEntry, MonitoringEntryFunding


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasFeatureAccess])
def scenario_rebalance_budget(request):
    """
    Simulate budget rebalancing across PPAs.

    POST data:
    {
        "scenarios": [
            {
                "entry_id": "uuid",
                "new_allocation": 1000000,
                "adjustment_reason": "Increased priority"
            }
        ],
        "total_ceiling": 50000000
    }

    Returns:
    {
        "valid": true,
        "total_allocated": 50000000,
        "remaining": 0,
        "within_ceiling": true,
        "scenarios": [...],
        "summary": {...}
    }
    """
    scenarios = request.data.get("scenarios", [])
    total_ceiling = Decimal(str(request.data.get("total_ceiling", 0)))

    if not scenarios:
        return Response(
            {"error": "No scenarios provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    results = []
    total_allocated = Decimal("0.00")

    for scenario in scenarios:
        entry_id = scenario.get("entry_id")
        new_allocation = Decimal(str(scenario.get("new_allocation", 0)))

        try:
            entry = MonitoringEntry.objects.get(id=entry_id)
        except MonitoringEntry.DoesNotExist:
            return Response(
                {"error": f"Entry {entry_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        old_allocation = entry.budget_allocation or Decimal("0.00")
        difference = new_allocation - old_allocation
        percent_change = (
            (difference / old_allocation * 100) if old_allocation > 0 else 0
        )

        total_allocated += new_allocation

        results.append(
            {
                "entry_id": str(entry.id),
                "entry_title": entry.title,
                "old_allocation": float(old_allocation),
                "new_allocation": float(new_allocation),
                "difference": float(difference),
                "percent_change": float(percent_change),
                "adjustment_reason": scenario.get("adjustment_reason", ""),
            }
        )

    remaining = total_ceiling - total_allocated
    within_ceiling = total_allocated <= total_ceiling

    response_data = {
        "valid": within_ceiling,
        "total_ceiling": float(total_ceiling),
        "total_allocated": float(total_allocated),
        "remaining": float(remaining),
        "within_ceiling": within_ceiling,
        "scenarios": results,
        "summary": {
            "ppa_count": len(results),
            "average_allocation": (
                float(total_allocated / len(results)) if results else 0
            ),
            "utilization_rate": (
                float((total_allocated / total_ceiling * 100))
                if total_ceiling > 0
                else 0
            ),
        },
    }

    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasFeatureAccess])
def scenario_funding_mix(request):
    """
    Analyze what-if funding source mix changes.

    POST data:
    {
        "funding_scenarios": {
            "gaa": 20000000,
            "block_grant": 15000000,
            "lgu_counterpart": 10000000,
            "donor": 5000000
        }
    }

    Returns analysis of how PPAs would be affected by funding source changes.
    """
    funding_scenarios = request.data.get("funding_scenarios", {})

    if not funding_scenarios:
        return Response(
            {"error": "No funding scenarios provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get current distribution
    current_distribution = {}
    for source_key, source_label in MonitoringEntry.FUNDING_SOURCE_CHOICES:
        ppas = MonitoringEntry.objects.filter(funding_source=source_key)
        total = ppas.aggregate(total=models.Sum("budget_allocation"))[
            "total"
        ] or Decimal("0.00")
        current_distribution[source_key] = {
            "label": source_label,
            "current_total": float(total),
            "ppa_count": ppas.count(),
        }

    # Calculate proposed changes
    changes = []
    for source_key, proposed_amount in funding_scenarios.items():
        if source_key in current_distribution:
            current = Decimal(str(current_distribution[source_key]["current_total"]))
            proposed = Decimal(str(proposed_amount))
            difference = proposed - current
            percent_change = (difference / current * 100) if current > 0 else 0

            changes.append(
                {
                    "source": source_key,
                    "label": current_distribution[source_key]["label"],
                    "current_amount": float(current),
                    "proposed_amount": float(proposed),
                    "difference": float(difference),
                    "percent_change": float(percent_change),
                    "affected_ppas": current_distribution[source_key]["ppa_count"],
                }
            )

    total_current = sum(
        Decimal(str(d["current_total"])) for d in current_distribution.values()
    )
    total_proposed = sum(Decimal(str(amount)) for amount in funding_scenarios.values())

    response_data = {
        "current_distribution": current_distribution,
        "proposed_changes": changes,
        "summary": {
            "total_current": float(total_current),
            "total_proposed": float(total_proposed),
            "net_change": float(total_proposed - total_current),
            "diversification_index": len(
                [c for c in changes if c["proposed_amount"] > 0]
            ),
        },
    }

    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, HasFeatureAccess])
def scenario_obligation_forecast(request):
    """
    Forecast obligation and disbursement rates.

    POST data:
    {
        "months_ahead": 6,
        "target_obligation_rate": 85,
        "target_disbursement_rate": 70
    }

    Returns forecasted performance and recommendations.
    """
    months_ahead = request.data.get("months_ahead", 6)
    target_obligation_rate = Decimal(
        str(request.data.get("target_obligation_rate", 85))
    )
    target_disbursement_rate = Decimal(
        str(request.data.get("target_disbursement_rate", 70))
    )

    # Get current rates
    ppas = MonitoringEntry.objects.all()
    total_allocation = ppas.aggregate(total=models.Sum("budget_allocation"))[
        "total"
    ] or Decimal("0.00")

    total_obligations = MonitoringEntryFunding.objects.filter(
        tranche_type=MonitoringEntryFunding.TRANCHE_OBLIGATION
    ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

    total_disbursements = MonitoringEntryFunding.objects.filter(
        tranche_type=MonitoringEntryFunding.TRANCHE_DISBURSEMENT
    ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

    current_obligation_rate = (
        (total_obligations / total_allocation * 100) if total_allocation > 0 else 0
    )
    current_disbursement_rate = (
        (total_disbursements / total_obligations * 100) if total_obligations > 0 else 0
    )

    # Calculate targets
    target_obligations = total_allocation * (target_obligation_rate / 100)
    target_disbursements = total_obligations * (target_disbursement_rate / 100)

    obligation_gap = target_obligations - total_obligations
    disbursement_gap = target_disbursements - total_disbursements

    monthly_obligation_needed = obligation_gap / months_ahead if months_ahead > 0 else 0
    monthly_disbursement_needed = (
        disbursement_gap / months_ahead if months_ahead > 0 else 0
    )

    response_data = {
        "current_status": {
            "total_allocation": float(total_allocation),
            "total_obligations": float(total_obligations),
            "total_disbursements": float(total_disbursements),
            "obligation_rate": float(current_obligation_rate),
            "disbursement_rate": float(current_disbursement_rate),
        },
        "targets": {
            "target_obligation_rate": float(target_obligation_rate),
            "target_disbursement_rate": float(target_disbursement_rate),
            "target_obligations": float(target_obligations),
            "target_disbursements": float(target_disbursements),
        },
        "gaps": {
            "obligation_gap": float(obligation_gap),
            "disbursement_gap": float(disbursement_gap),
            "months_ahead": months_ahead,
            "monthly_obligation_needed": float(monthly_obligation_needed),
            "monthly_disbursement_needed": float(monthly_disbursement_needed),
        },
        "recommendations": _generate_recommendations(
            current_obligation_rate,
            current_disbursement_rate,
            target_obligation_rate,
            target_disbursement_rate,
            obligation_gap,
            disbursement_gap,
        ),
    }

    return Response(response_data)


def _generate_recommendations(
    current_oblig_rate,
    current_disb_rate,
    target_oblig_rate,
    target_disb_rate,
    oblig_gap,
    disb_gap,
):
    """Generate actionable recommendations based on forecast."""
    recommendations = []

    if current_oblig_rate < target_oblig_rate:
        recommendations.append(
            {
                "priority": "high",
                "category": "obligation",
                "message": f"Obligation rate at {current_oblig_rate:.1f}% is below target {target_oblig_rate:.1f}%. Accelerate procurement and contracting processes.",
            }
        )

    if current_disb_rate < target_disb_rate:
        recommendations.append(
            {
                "priority": "high",
                "category": "disbursement",
                "message": f"Disbursement rate at {current_disb_rate:.1f}% is below target {target_disb_rate:.1f}%. Review payment processing and liquidation procedures.",
            }
        )

    if oblig_gap > 0:
        recommendations.append(
            {
                "priority": "medium",
                "category": "planning",
                "message": f"Need to obligate ₱{oblig_gap:,.2f} to meet target. Review PPA implementation timelines.",
            }
        )

    if current_oblig_rate > 95:
        recommendations.append(
            {
                "priority": "low",
                "category": "success",
                "message": "Excellent obligation performance. Focus on maintaining quality of implementation.",
            }
        )

    return recommendations
