# Enhanced Portfolio Dashboard View
# Copy this function to replace the portfolio_dashboard_view in views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
import json

from common.models import WorkItem
from .models import Alert
from mana.models import Need
from monitoring.models import MonitoringEntry
from coordination.models import Organization
from recommendations.policy_tracking.models import PolicyRecommendation


@login_required
def portfolio_dashboard_view(request):
    """
    Integrated portfolio dashboard showing project lifecycle with budget metrics.
    Includes Chart.js visualizations for budget by sector and funding source.
    """
    current_year = timezone.now().year

    # Summary metrics
    total_budget = (
        MonitoringEntry.objects.filter(fiscal_year=current_year).aggregate(
            total=Sum("budget_allocation")
        )["total"]
        or 0
    )

    active_projects = MonitoringEntry.objects.filter(status="ongoing").count()
    unfunded_needs = Need.objects.filter(
        linked_ppa__isnull=True, priority_score__gte=4.0
    ).count()
    total_beneficiaries = (
        MonitoringEntry.objects.filter(fiscal_year=current_year).aggregate(
            total=Sum("obc_slots")
        )["total"]
        or 0
    )

    # Additional metrics
    maos_engaged = Organization.objects.filter(organization_type="bmoa").count()
    policies_implemented = PolicyRecommendation.objects.filter(
        status="implemented"
    ).count()

    # Pipeline data (5 stages)
    needs_identified = Need.objects.filter(status="identified").count()
    needs_validated = Need.objects.filter(
        is_validated=True, linked_ppa__isnull=True
    ).count()
    ppas_planning = MonitoringEntry.objects.filter(status="planning").count()
    ppas_ongoing = MonitoringEntry.objects.filter(status="ongoing").count()
    ppas_completed = MonitoringEntry.objects.filter(status="completed").count()

    # Budget by Sector (Chart.js data)
    budget_by_sector = (
        MonitoringEntry.objects.filter(fiscal_year=current_year)
        .values("sector")
        .annotate(total=Sum("budget_allocation"))
        .order_by("-total")
    )

    sector_labels = [item["sector"] or "Unknown" for item in budget_by_sector]
    sector_values = [float(item["total"] or 0) for item in budget_by_sector]

    # Budget by Funding Source (Chart.js data)
    budget_by_source = (
        MonitoringEntry.objects.filter(fiscal_year=current_year)
        .values("funding_source")
        .annotate(total=Sum("budget_allocation"))
        .order_by("-total")
    )

    source_labels = [item["funding_source"] or "Unknown" for item in budget_by_source]
    source_values = [float(item["total"] or 0) for item in budget_by_source]

    # Strategic Goals Progress (mock data - replace with actual goal tracking)
    strategic_goals = [
        {"name": "Education Access", "progress": 75, "target": 100},
        {"name": "Economic Development", "progress": 60, "target": 100},
        {"name": "Social Services", "progress": 85, "target": 100},
        {"name": "Infrastructure", "progress": 45, "target": 100},
        {"name": "Cultural Development", "progress": 70, "target": 100},
    ]

    # Recent alerts
    recent_alerts = Alert.objects.filter(
        is_active=True, is_acknowledged=False
    ).order_by("-severity", "-created_at")[:5]

    # Recent workflows
    recent_workflows = ProjectWorkflow.objects.all()[:10]

    context = {
        "total_budget": total_budget,
        "active_projects": active_projects,
        "unfunded_needs": unfunded_needs,
        "total_beneficiaries": total_beneficiaries,
        "maos_engaged": maos_engaged,
        "policies_implemented": policies_implemented,
        "needs_identified": needs_identified,
        "needs_validated": needs_validated,
        "ppas_planning": ppas_planning,
        "ppas_ongoing": ppas_ongoing,
        "ppas_completed": ppas_completed,
        "sector_labels_json": json.dumps(sector_labels),
        "sector_values_json": json.dumps(sector_values),
        "source_labels_json": json.dumps(source_labels),
        "source_values_json": json.dumps(source_values),
        "strategic_goals": strategic_goals,
        "recent_alerts": recent_alerts,
        "recent_workflows": recent_workflows,
        "current_year": current_year,
    }

    return render(request, "project_central/portfolio_dashboard.html", context)
