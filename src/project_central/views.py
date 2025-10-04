"""Project Central Views provide integrated project management interfaces."""

from datetime import date

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from common.models import StaffTask
from common.services.task_automation import create_tasks_from_template
from coordination.models import Organization
from mana.models import Need
from monitoring.models import MonitoringEntry
from recommendations.policy_tracking.models import PolicyRecommendation

from .forms import AlertFilterForm
from .models import Alert, BudgetCeiling, BudgetScenario, ProjectWorkflow


# ========== TASK 8: Portfolio Dashboard View ==========


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

    summary_cards = [
        {
            "title": "Total Budget",
            "value": total_budget,
            "value_type": "currency",
            "icon": "fa-money-bill-wave",
            "gradient": "from-emerald-600 via-teal-500 to-sky-500",
            "pill": f"FY {current_year}",
        },
        {
            "title": "Active Projects",
            "value": active_projects,
            "icon": "fa-diagram-project",
            "gradient": "from-blue-600 via-sky-500 to-cyan-500",
            "subtitle": "Currently being implemented",
        },
        {
            "title": "Unfunded Needs",
            "value": unfunded_needs,
            "icon": "fa-triangle-exclamation",
            "gradient": "from-rose-600 via-orange-500 to-amber-500",
            "subtitle": "High priority, awaiting budget",
        },
        {
            "title": "OBC Beneficiaries",
            "value": total_beneficiaries,
            "icon": "fa-people-group",
            "gradient": "from-violet-600 via-purple-500 to-fuchsia-500",
            "subtitle": "Slots allocated across PPAs",
        },
        {
            "title": "MAOs Engaged",
            "value": maos_engaged,
            "icon": "fa-handshake-angle",
            "gradient": "from-indigo-600 via-blue-500 to-slate-500",
            "subtitle": "LGU partners with active coordination",
        },
        {
            "title": "Policies Implemented",
            "value": policies_implemented,
            "icon": "fa-gavel",
            "gradient": "from-emerald-700 via-lime-500 to-teal-500",
            "subtitle": "Policy recommendations in execution",
        },
    ]

    pipeline_counts = [
        (
            "Needs Identified",
            needs_identified,
            "fa-lightbulb",
            "bg-emerald-500",
            "Pipeline entries sourced from communities",
        ),
        (
            "Needs Validated",
            needs_validated,
            "fa-circle-check",
            "bg-sky-500",
            "Validated and ready for planning",
        ),
        (
            "Planning",
            ppas_planning,
            "fa-sitemap",
            "bg-amber-500",
            "PPAs shaping budget packages",
        ),
        (
            "Ongoing",
            ppas_ongoing,
            "fa-arrows-rotate",
            "bg-violet-500",
            "Implementation in progress",
        ),
        (
            "Completed",
            ppas_completed,
            "fa-flag-checkered",
            "bg-emerald-600",
            "Fully delivered outputs",
        ),
    ]

    max_pipeline = max((count for _, count, _, _, _ in pipeline_counts), default=0)
    pipeline_steps = []
    for label, count, icon, bar_class, description in pipeline_counts:
        percentage = 0
        if max_pipeline:
            percentage = max(6, round((count / max_pipeline) * 100)) if count else 0
        pipeline_steps.append(
            {
                "label": label,
                "count": count,
                "icon": icon,
                "bar_class": bar_class,
                "description": description,
                "percentage": percentage,
            }
        )

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
        "budget_by_sector": budget_by_sector,
        "budget_by_source": budget_by_source,
        "sector_labels_json": json.dumps(sector_labels),
        "sector_values_json": json.dumps(sector_values),
        "source_labels_json": json.dumps(source_labels),
        "source_values_json": json.dumps(source_values),
        "strategic_goals": strategic_goals,
        "recent_alerts": recent_alerts,
        "recent_workflows": recent_workflows,
        "current_year": current_year,
        "summary_cards": summary_cards,
        "pipeline_steps": pipeline_steps,
    }

    return render(request, "project_central/portfolio_dashboard.html", context)


# ========== TASK 9: Project Workflow Detail View ==========


@login_required
def project_workflow_detail(request, workflow_id):
    """
    Display detailed project workflow with stage progression.
    Shows visual timeline of 9 workflow stages with completion status.
    """
    workflow = get_object_or_404(
        ProjectWorkflow.objects.select_related(
            'primary_need',
            'ppa',
            'project_lead'
        ).prefetch_related(
            'project_activities',  # Related events
            'tasks__assignees',
            'ppa__workflow_tasks'
        ),
        id=workflow_id
    )

    # Get all stages with completion status
    stages = []
    stage_choices = ProjectWorkflow.WORKFLOW_STAGES
    current_index = [s[0] for s in stage_choices].index(workflow.current_stage)

    for idx, (stage_key, stage_label) in enumerate(stage_choices):
        stages.append(
            {
                "key": stage_key,
                "label": stage_label,
                "number": idx + 1,
                "status": (
                    "completed"
                    if idx < current_index
                    else ("current" if idx == current_index else "pending")
                ),
                "icon": _get_stage_icon(stage_key),
            }
        )

    # Get stage history
    history = workflow.stage_history if workflow.stage_history else []

    # Get related tasks and alerts
    tasks = StaffTask.objects.filter(linked_workflow=workflow).order_by("-created_at")
    alerts = Alert.objects.filter(related_workflow=workflow, is_active=True).order_by(
        "-severity", "-created_at"
    )

    # Get project activities
    activities = workflow.project_activities.all()
    upcoming_activities = workflow.get_upcoming_activities(days=30)

    # Get all project tasks (including activity tasks)
    all_tasks = workflow.all_project_tasks

    # Calculate progress percentage based on stage
    progress_percentage = workflow.get_stage_progress_percentage()

    context = {
        "workflow": workflow,
        "need": workflow.primary_need,
        "ppa": workflow.ppa,
        "stages": stages,
        "history": history,
        "current_stage_index": current_index,
        "progress_percentage": progress_percentage,
        "tasks": tasks,
        "alerts": alerts,
        "activities": activities,
        "upcoming_activities": upcoming_activities,
        "all_tasks": all_tasks,
    }

    return render(request, "project_central/workflow_detail.html", context)


def _get_stage_icon(stage_key):
    """Return Font Awesome icon for each workflow stage."""
    icons = {
        "need_identification": "fa-lightbulb",
        "need_validation": "fa-check-circle",
        "policy_linkage": "fa-link",
        "mao_coordination": "fa-handshake",
        "budget_planning": "fa-calculator",
        "approval": "fa-gavel",
        "implementation": "fa-cogs",
        "monitoring": "fa-chart-line",
        "completion": "fa-flag-checkered",
    }
    return icons.get(stage_key, "fa-circle")


@login_required
def project_list_view(request):
    """List all project workflows."""
    workflows = ProjectWorkflow.objects.all().order_by("-initiated_date")

    stage_filter = request.GET.get("stage")
    if stage_filter:
        workflows = workflows.filter(current_stage=stage_filter)

    context = {
        "workflows": workflows,
        "stage_filter": stage_filter,
        "stage_choices": ProjectWorkflow.WORKFLOW_STAGES,
    }
    return render(request, "project_central/project_list.html", context)


@login_required
def create_project_workflow(request):
    messages.info(request, "Create project workflow functionality coming soon.")
    return redirect("project_central:project_list")


@login_required
def edit_project_workflow(request, workflow_id):
    messages.info(request, "Edit project workflow functionality coming soon.")
    return redirect("project_central:project_workflow_detail", workflow_id=workflow_id)


@login_required
def advance_project_stage(request, workflow_id):
    """Advance workflow to next stage with validation."""
    workflow = get_object_or_404(ProjectWorkflow, id=workflow_id)

    if request.method == "POST":
        notes = request.POST.get("notes", "")

        # Get current and next stage
        stage_choices = ProjectWorkflow.WORKFLOW_STAGES
        current_index = [s[0] for s in stage_choices].index(workflow.current_stage)

        # Check if already at final stage
        if current_index >= len(stage_choices) - 1:
            messages.warning(
                request, "Cannot advance: Already at final stage (Completion)"
            )
            return redirect(
                "project_central:project_workflow_detail", workflow_id=workflow_id
            )

        # Get next stage
        next_stage = stage_choices[current_index + 1][0]

        # Validate if can advance
        can_advance, reason = workflow.can_advance_to_stage(next_stage)

        if not can_advance:
            messages.error(request, f"Cannot advance: {reason}")
            return redirect(
                "project_central:project_workflow_detail", workflow_id=workflow_id
            )

        # Advance the stage
        success = workflow.advance_stage(next_stage, request.user, notes)

        if success:
            messages.success(
                request, f"Workflow advanced to {workflow.get_current_stage_display()}"
            )
        else:
            messages.error(request, "Failed to advance workflow stage")

        return redirect(
            "project_central:project_workflow_detail", workflow_id=workflow_id
        )

    return redirect("project_central:project_workflow_detail", workflow_id=workflow_id)


# ========== TASK 10: Alert Listing View ==========


@login_required
def alert_list_view(request):
    """Alert listing view with filters and acknowledgment."""
    alerts = Alert.objects.all().order_by("-created_at")
    filter_form = AlertFilterForm(request.GET or None)

    if filter_form.is_valid():
        cleaned = filter_form.cleaned_data

        if cleaned.get("active", "true") != "false":
            alerts = alerts.filter(is_active=True)

        if cleaned.get("acknowledgment") == "pending":
            alerts = alerts.filter(is_acknowledged=False)

        alert_type = cleaned.get("alert_type")
        if alert_type:
            alerts = alerts.filter(alert_type=alert_type)

        severity = cleaned.get("severity")
        if severity:
            alerts = alerts.filter(severity=severity)

        show_active = cleaned.get("active", "true") != "false"
        show_unacknowledged = cleaned.get("acknowledgment") == "pending"
    else:
        show_active = True
        show_unacknowledged = False

    severity_counts = Alert.get_unacknowledged_count_by_severity()
    severity_totals = {item["severity"]: item["count"] for item in severity_counts}

    severity_styles = {
        "critical": {
            "gradient": "from-rose-500 to-rose-600",
            "icon": "fa-circle-exclamation",
        },
        "high": {
            "gradient": "from-orange-500 to-amber-500",
            "icon": "fa-triangle-exclamation",
        },
        "medium": {"gradient": "from-yellow-400 to-amber-400", "icon": "fa-bell"},
        "low": {"gradient": "from-sky-400 to-blue-500", "icon": "fa-flag"},
        "info": {"gradient": "from-slate-400 to-slate-500", "icon": "fa-circle-info"},
    }

    severity_cards = []
    for value, label in Alert.SEVERITY_LEVELS:
        style = severity_styles.get(
            value, {"gradient": "from-emerald-500 to-emerald-600", "icon": "fa-bell"}
        )
        severity_cards.append(
            {
                "key": value,
                "label": label,
                "count": severity_totals.get(value, 0),
                "gradient": style["gradient"],
                "icon": style["icon"],
            }
        )

    context = {
        "alerts": alerts,
        "severity_cards": severity_cards,
        "filter_form": filter_form,
        "show_active": show_active,
        "show_unacknowledged": show_unacknowledged,
    }

    return render(request, "project_central/alert_list.html", context)


@login_required
def alert_detail_view(request, alert_id):
    """Show alert details."""
    alert = get_object_or_404(Alert, id=alert_id)
    context = {"alert": alert}
    return render(request, "project_central/alert_detail.html", context)


@login_required
def acknowledge_alert(request, alert_id):
    """Acknowledge an alert (HTMX-enabled)."""
    alert = get_object_or_404(Alert, id=alert_id)

    if request.method == "POST":
        notes = request.POST.get("notes", "")
        alert.acknowledge(request.user, notes)

        # Check if HTMX request
        if request.headers.get("HX-Request"):
            # Return updated alert row HTML
            return render(
                request,
                "project_central/partials/alert_row.html",
                {
                    "alert": alert,
                },
            )
        else:
            messages.success(request, f"Alert '{alert.title}' has been acknowledged.")
            return redirect("project_central:alert_list")

    return render(request, "project_central/acknowledge_alert.html", {"alert": alert})


@login_required
def bulk_acknowledge_alerts(request):
    messages.info(request, "Bulk acknowledge functionality coming soon.")
    return redirect("project_central:alert_list")


@login_required
def generate_alerts_now(request):
    """Manual alert generation endpoint (triggers Celery task immediately)."""
    if request.method == "POST":
        from .tasks import generate_daily_alerts_task

        # Trigger Celery task asynchronously
        task = generate_daily_alerts_task.delay()

        messages.success(
            request,
            "Alert generation task has been queued. Alerts will be updated shortly.",
        )

        # Check if HTMX request
        if request.headers.get("HX-Request"):
            return HttpResponse(status=204, headers={"HX-Trigger": "alert-refresh"})
        else:
            return redirect("project_central:alert_list")

    return redirect("project_central:alert_list")


# ========== TASK 11: Budget Planning Dashboard ==========


@login_required
def budget_planning_dashboard(request):
    """Basic budget planning dashboard - budget allocation, utilization by sector/source."""
    current_year = timezone.now().year
    fiscal_year = request.GET.get("fiscal_year", current_year)

    try:
        fiscal_year = int(fiscal_year)
    except (ValueError, TypeError):
        fiscal_year = current_year

    budget_ceilings = BudgetCeiling.objects.filter(
        fiscal_year=fiscal_year, is_active=True
    ).order_by("sector", "funding_source")

    sector_allocation = (
        MonitoringEntry.objects.filter(fiscal_year=fiscal_year)
        .values("sector")
        .annotate(total_allocation=Sum("budget_allocation"), ppa_count=Count("id"))
        .order_by("-total_allocation")
    )

    source_allocation = (
        MonitoringEntry.objects.filter(fiscal_year=fiscal_year)
        .values("funding_source")
        .annotate(total_allocation=Sum("budget_allocation"), ppa_count=Count("id"))
        .order_by("-total_allocation")
    )

    total_allocated = (
        MonitoringEntry.objects.filter(fiscal_year=fiscal_year).aggregate(
            total=Sum("budget_allocation")
        )["total"]
        or 0
    )

    scenarios = BudgetScenario.objects.filter(fiscal_year=fiscal_year).order_by(
        "-is_baseline", "-created_at"
    )

    context = {
        "fiscal_year": fiscal_year,
        "current_year": current_year,
        "budget_ceilings": budget_ceilings,
        "sector_allocation": sector_allocation,
        "source_allocation": source_allocation,
        "total_allocated": total_allocated,
        "scenarios": scenarios,
    }

    return render(request, "project_central/budget_planning_dashboard.html", context)


# ========== Additional View Stubs (Phases 2-8) ==========


@login_required
def me_analytics_dashboard(request):
    """M&E Analytics Dashboard with comprehensive project metrics."""
    from .services import AnalyticsService

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get("fiscal_year", current_year))

    # Get comprehensive dashboard data
    dashboard_data = AnalyticsService.get_dashboard_summary(fiscal_year)

    context = {
        "fiscal_year": fiscal_year,
        "current_year": current_year,
        "budget_by_sector": dashboard_data["budget_by_sector"],
        "budget_by_source": dashboard_data["budget_by_source"],
        "budget_by_region": dashboard_data["budget_by_region"],
        "utilization_rates": dashboard_data["utilization_rates"],
        "cost_effectiveness": dashboard_data["cost_effectiveness"],
        "workflow_performance": dashboard_data["workflow_performance"],
    }

    return render(request, "project_central/me_analytics_dashboard.html", context)


@login_required
def sector_analytics(request, sector):
    """Detailed analytics for a specific sector."""
    from .services import AnalyticsService

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get("fiscal_year", current_year))

    # Get sector-specific data
    budget_allocation = AnalyticsService.get_budget_allocation_by_sector(fiscal_year)
    cost_effectiveness = AnalyticsService.get_cost_effectiveness_metrics(
        sector=sector, fiscal_year=fiscal_year
    )

    # Filter for this sector
    sector_data = next(
        (s for s in budget_allocation["sectors"] if s["sector"] == sector), None
    )

    if not sector_data:
        messages.warning(request, f"No data found for sector: {sector}")
        return redirect("project_central:me_analytics_dashboard")

    # Get projects in this sector
    ppas = MonitoringEntry.objects.filter(
        sector=sector, fiscal_year=fiscal_year
    ).order_by("-budget_allocation")

    context = {
        "sector": sector,
        "fiscal_year": fiscal_year,
        "sector_data": sector_data,
        "cost_effectiveness": cost_effectiveness,
        "ppas": ppas,
    }

    return render(request, "project_central/sector_analytics.html", context)


@login_required
def geographic_analytics(request):
    """Geographic distribution of budget and projects."""
    from .services import AnalyticsService

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get("fiscal_year", current_year))

    budget_by_region = AnalyticsService.get_budget_allocation_by_region(fiscal_year)

    context = {
        "fiscal_year": fiscal_year,
        "budget_by_region": budget_by_region,
    }

    return render(request, "project_central/geographic_analytics.html", context)


@login_required
def policy_analytics(request, policy_id):
    """Analytics for a specific policy recommendation."""
    from policy_tracking.models import PolicyRecommendation

    policy = get_object_or_404(PolicyRecommendation, id=policy_id)

    # Find needs linked to this policy
    linked_needs = policy.linked_needs.all()

    # Find workflows for those needs
    workflows = ProjectWorkflow.objects.filter(primary_need__in=linked_needs)

    # Find PPAs linked to those needs
    ppas = MonitoringEntry.objects.filter(linked_need__in=linked_needs)

    # Calculate budget allocated to this policy
    total_budget = ppas.aggregate(total=Sum("budget_allocation"))["total"] or 0

    context = {
        "policy": policy,
        "linked_needs": linked_needs,
        "workflows": workflows,
        "ppas": ppas,
        "total_budget": total_budget,
        "needs_count": linked_needs.count(),
        "ppas_count": ppas.count(),
    }

    return render(request, "project_central/policy_analytics.html", context)


@login_required
def report_list_view(request):
    """List of available reports."""
    reports = [
        {
            "title": "Project Portfolio Report",
            "description": "Comprehensive overview of project status, budget performance, beneficiaries, and workflow milestones.",
            "icon": "fa-project-diagram",
            "gradient": "from-indigo-500 to-purple-500",
            "actions": [
                {
                    "label": "View Report",
                    "icon": "fa-eye",
                    "url": reverse("project_central:generate_portfolio_report"),
                    "variant": "primary",
                },
                {
                    "label": "Download CSV",
                    "icon": "fa-download",
                    "url": f"{reverse('project_central:generate_portfolio_report')}?format=csv",
                    "variant": "outline",
                },
            ],
        },
        {
            "title": "Needs Assessment Impact Report",
            "description": "Trace needs from identification to delivery, including linked PPAs, funding status, and outcome achievement.",
            "icon": "fa-chart-line",
            "gradient": "from-pink-500 to-rose-500",
            "actions": [
                {
                    "label": "View Report",
                    "icon": "fa-eye",
                    "url": reverse("project_central:generate_needs_impact_report"),
                    "variant": "primary",
                },
                {
                    "label": "Download CSV",
                    "icon": "fa-download",
                    "url": f"{reverse('project_central:generate_needs_impact_report')}?format=csv",
                    "variant": "outline",
                },
            ],
        },
        {
            "title": "Policy Implementation Report",
            "description": "Monitor policy recommendation status, budget allocation, and implementation progress across sectors.",
            "icon": "fa-gavel",
            "gradient": "from-sky-500 to-cyan-500",
            "actions": [
                {
                    "label": "View Report",
                    "icon": "fa-eye",
                    "url": reverse("project_central:generate_policy_report"),
                    "variant": "primary",
                },
                {
                    "label": "Download CSV",
                    "icon": "fa-download",
                    "url": f"{reverse('project_central:generate_policy_report')}?format=csv",
                    "variant": "outline",
                },
            ],
        },
        {
            "title": "MAO Coordination Report",
            "description": "Track MAO participation, quarterly updates, collaborative PPAs, and coordination effectiveness.",
            "icon": "fa-handshake",
            "gradient": "from-emerald-500 to-teal-500",
            "badge": "Coming Soon",
            "actions": [
                {
                    "label": "View Outline",
                    "icon": "fa-eye",
                    "url": reverse("project_central:generate_mao_report"),
                    "variant": "disabled",
                },
            ],
        },
        {
            "title": "M&E Consolidated Report",
            "description": "Outcomes achieved, cost-effectiveness, lessons learned, and impact assessment across the portfolio.",
            "icon": "fa-chart-bar",
            "gradient": "from-amber-500 to-orange-500",
            "badge": "Analytics Available",
            "actions": [
                {
                    "label": "Open Dashboard",
                    "icon": "fa-chart-column",
                    "url": reverse("project_central:me_analytics_dashboard"),
                    "variant": "primary",
                },
            ],
        },
        {
            "title": "Budget Execution Report",
            "description": "Budget obligations, disbursements, variance analysis, and utilization rates by sector, source, and region.",
            "icon": "fa-money-bill-wave",
            "gradient": "from-blue-500 to-slate-600",
            "actions": [
                {
                    "label": "View Report",
                    "icon": "fa-eye",
                    "url": reverse("project_central:generate_budget_execution_report"),
                    "variant": "primary",
                },
                {
                    "label": "Download CSV",
                    "icon": "fa-download",
                    "url": f"{reverse('project_central:generate_budget_execution_report')}?format=csv",
                    "variant": "outline",
                },
            ],
        },
        {
            "title": "Annual Planning Cycle Report",
            "description": "Year-over-year utilization, allocation decisions, scenario comparisons, and planning recommendations.",
            "icon": "fa-calendar-alt",
            "gradient": "from-fuchsia-500 to-rose-500",
            "badge": "Planning Mode",
            "actions": [
                {
                    "label": "Open Budget Planner",
                    "icon": "fa-compass",
                    "url": reverse("project_central:budget_planning_dashboard"),
                    "variant": "primary",
                },
            ],
        },
    ]

    context = {"reports": reports}
    return render(request, "project_central/report_list.html", context)


@login_required
def generate_portfolio_report(request):
    """Generate portfolio performance report."""
    from .services import ReportGenerator

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get("fiscal_year", current_year))
    output_format = request.GET.get("format", "dict")

    try:
        if output_format == "csv":
            report_data = ReportGenerator.generate_portfolio_report(
                fiscal_year, output_format="csv"
            )
            response = HttpResponse(report_data.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="portfolio_report_{fiscal_year}.csv"'
            )
            return response

        else:
            # Display in HTML
            report_data = ReportGenerator.generate_portfolio_report(
                fiscal_year, output_format="dict"
            )
            context = {
                "report_data": report_data,
                "fiscal_year": fiscal_year,
            }
            return render(
                request, "project_central/reports/portfolio_report.html", context
            )

    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect("project_central:report_list")


@login_required
def generate_needs_impact_report(request):
    """Generate workflow progress report."""
    from .services import ReportGenerator

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get("fiscal_year", current_year))
    output_format = request.GET.get("format", "dict")

    try:
        if output_format == "csv":
            report_data = ReportGenerator.generate_workflow_progress_report(
                fiscal_year, output_format="csv"
            )
            response = HttpResponse(report_data.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="workflow_progress_{fiscal_year}.csv"'
            )
            return response

        else:
            report_data = ReportGenerator.generate_workflow_progress_report(
                fiscal_year, output_format="dict"
            )
            context = {
                "report_data": report_data,
                "fiscal_year": fiscal_year,
            }
            return render(
                request,
                "project_central/reports/workflow_progress_report.html",
                context,
            )

    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect("project_central:report_list")


@login_required
def generate_policy_report(request):
    """Generate cost-effectiveness report."""
    from .services import ReportGenerator

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get("fiscal_year", current_year))
    output_format = request.GET.get("format", "dict")

    try:
        if output_format == "csv":
            report_data = ReportGenerator.generate_cost_effectiveness_report(
                fiscal_year, output_format="csv"
            )
            response = HttpResponse(report_data.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="cost_effectiveness_{fiscal_year}.csv"'
            )
            return response

        else:
            report_data = ReportGenerator.generate_cost_effectiveness_report(
                fiscal_year, output_format="dict"
            )
            context = {
                "report_data": report_data,
                "fiscal_year": fiscal_year,
            }
            return render(
                request,
                "project_central/reports/cost_effectiveness_report.html",
                context,
            )

    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect("project_central:report_list")


@login_required
def generate_mao_report(request):
    """Generate MAO coordination report."""
    # Future implementation: MAO-specific reporting
    messages.info(request, "MAO-specific reporting coming soon.")
    return redirect("project_central:report_list")


@login_required
def generate_budget_execution_report(request):
    """Generate budget utilization report."""
    from .services import ReportGenerator

    current_year = timezone.now().year
    fiscal_year = int(request.GET.get("fiscal_year", current_year))
    sector = request.GET.get("sector")
    output_format = request.GET.get("format", "dict")

    try:
        if output_format == "csv":
            report_data = ReportGenerator.generate_budget_utilization_report(
                fiscal_year, sector, output_format="csv"
            )
            response = HttpResponse(report_data.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="budget_utilization_{fiscal_year}.csv"'
            )
            return response

        else:
            report_data = ReportGenerator.generate_budget_utilization_report(
                fiscal_year, sector, output_format="dict"
            )
            context = {
                "report_data": report_data,
                "fiscal_year": fiscal_year,
                "sector": sector,
            }
            return render(
                request,
                "project_central/reports/budget_utilization_report.html",
                context,
            )

    except Exception as e:
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect("project_central:report_list")


@login_required
def report_detail_view(request, report_id):
    messages.info(request, "Report detail view coming in Phase 5.")
    return redirect("project_central:portfolio_dashboard")


@login_required
def download_report(request, report_id):
    messages.info(request, "Report download coming in Phase 5.")
    return redirect("project_central:portfolio_dashboard")


@login_required
def my_tasks_with_projects(request):
    from django.db.models import Q

    user = request.user
    today = timezone.now().date()

    base_filter = (
        Q(assignees=user)
        | Q(created_by=user)
        | Q(teams__memberships__user=user, teams__memberships__is_active=True)
    )

    tasks_qs = (
        StaffTask.objects.filter(base_filter)
        .filter(Q(linked_workflow__isnull=False) | Q(related_ppa__isnull=False))
        .select_related(
            "linked_workflow",
            "linked_workflow__primary_need",
            "linked_workflow__ppa",
            "related_ppa",
        )
        .prefetch_related("assignees", "teams")
        .distinct()
    )

    status_filter = request.GET.get("status", "")
    stage_filter = request.GET.get("stage", "")
    domain_filter = request.GET.get("domain", "")
    search_query = (request.GET.get("q") or "").strip()
    show_overdue = request.GET.get("overdue") == "1"

    valid_statuses = {value for value, _ in StaffTask.STATUS_CHOICES}
    if status_filter in valid_statuses:
        tasks_qs = tasks_qs.filter(status=status_filter)
    if stage_filter:
        tasks_qs = tasks_qs.filter(linked_workflow__current_stage=stage_filter)
    valid_domains = {value for value, _ in StaffTask.DOMAIN_CHOICES}
    if domain_filter in valid_domains:
        tasks_qs = tasks_qs.filter(domain=domain_filter)
    if show_overdue:
        tasks_qs = tasks_qs.filter(
            due_date__lt=today,
            status__in=[
                StaffTask.STATUS_NOT_STARTED,
                StaffTask.STATUS_IN_PROGRESS,
                StaffTask.STATUS_AT_RISK,
            ],
        )
    if search_query:
        tasks_qs = tasks_qs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(linked_workflow__primary_need__title__icontains=search_query)
            | Q(related_ppa__title__icontains=search_query)
        )

    def sort_key(task: StaffTask):
        due = task.due_date or date.max
        return (due, task.priority, task.title.lower())

    task_list = sorted(tasks_qs, key=sort_key)

    summary = {
        "total": len(task_list),
        "overdue": sum(1 for task in task_list if task.is_overdue),
        "in_progress": sum(
            1 for task in task_list if task.status == StaffTask.STATUS_IN_PROGRESS
        ),
        "completed": sum(
            1 for task in task_list if task.status == StaffTask.STATUS_COMPLETED
        ),
    }

    context = {
        "tasks": task_list,
        "summary": summary,
        "status_choices": StaffTask.STATUS_CHOICES,
        "stage_choices": ProjectWorkflow.WORKFLOW_STAGES,
        "domain_choices": StaffTask.DOMAIN_CHOICES,
        "current_filters": {
            "status": status_filter,
            "stage": stage_filter,
            "domain": domain_filter,
            "overdue": "1" if show_overdue else "0",
            "q": search_query,
        },
    }

    if request.headers.get("HX-Request"):
        return render(
            request,
            "project_central/partials/project_task_table.html",
            context,
        )

    return render(request, "project_central/my_tasks.html", context)


@login_required
def generate_workflow_tasks(request, workflow_id):
    workflow = get_object_or_404(ProjectWorkflow, id=workflow_id)
    ppa = workflow.ppa

    from django.db import transaction

    template_map = {
        "need_identification": "project_need_validation",
        "need_validation": "project_need_validation",
        "policy_linkage": "project_policy_integration",
        "mao_coordination": "project_mao_coordination",
        "budget_planning": "project_budget_planning",
        "approval": "project_budget_approval",
        "implementation": "project_implementation",
        "monitoring": "project_monitoring",
        "completion": "project_completion",
    }

    template_name = template_map.get(workflow.current_stage, "project_generic_stage")

    base_filters = {
        "created_from_template__name": template_name,
        "linked_workflow": workflow,
    }

    if StaffTask.objects.filter(**base_filters).exists():
        messages.info(request, "Workflow tasks for this stage already exist.")
        return redirect(
            "project_central:project_workflow_detail", workflow_id=workflow_id
        )

    start_date = workflow.initiated_date or timezone.now().date()
    context_kwargs = {
        "linked_workflow": workflow,
        "related_ppa": ppa,
        "workflow_stage": workflow.current_stage,
        "created_by": request.user,
        "start_date": start_date,
        "auto_generated": True,
        "idempotency_filter": {"linked_workflow": workflow},
    }

    if workflow.primary_need:
        context_kwargs["related_need"] = workflow.primary_need
        context_kwargs["need_title"] = workflow.primary_need.title

    booking_specs = None
    if request.GET.get("auto_resource") == "1":
        booking_specs = {
            "default": [
                {
                    "resource_name": request.GET.get("resource_name", "Projector"),
                    "start_offset_days": 0,
                    "start_offset_hours": 2,
                    "duration_hours": 2,
                    "notes": f"Workflow stage: {workflow.get_current_stage_display()}",
                }
            ]
        }
        context_kwargs["resource_bookings"] = booking_specs

    try:
        with transaction.atomic():
            tasks = create_tasks_from_template(template_name, **context_kwargs)
    except ValidationError as exc:
        messages.error(request, f"Task generation failed: {exc}")
    else:
        if tasks:
            messages.success(
                request,
                f"Created {len(tasks)} tasks for stage {workflow.get_current_stage_display()}.",
            )
        else:
            messages.warning(
                request,
                "No tasks were generated for the current workflow stage.",
            )

    return redirect("project_central:project_workflow_detail", workflow_id=workflow_id)


@login_required
def budget_approval_dashboard(request):
    """
    Budget approval dashboard showing PPAs at each approval stage.
    Displays 5-stage approval process with pending and recent approvals.
    """
    # Get counts for each approval stage
    approval_counts = {}
    for stage_value, stage_label in MonitoringEntry.APPROVAL_STATUS_CHOICES:
        count = MonitoringEntry.objects.filter(approval_status=stage_value).count()
        approval_counts[stage_value] = {"label": stage_label, "count": count}

    stage_styles = {
        MonitoringEntry.APPROVAL_STATUS_DRAFT: {
            "gradient": "from-slate-500 to-slate-600",
            "icon": "fa-pen-to-square",
            "description": "Items under preparation before formal review.",
        },
        MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW: {
            "gradient": "from-blue-500 to-indigo-500",
            "icon": "fa-microscope",
            "description": "Technical validation with line agencies and reviewers.",
        },
        MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW: {
            "gradient": "from-purple-500 to-fuchsia-500",
            "icon": "fa-scale-balanced",
            "description": "Budget alignment checks with finance teams.",
        },
        MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION: {
            "gradient": "from-amber-500 to-orange-500",
            "icon": "fa-people-group",
            "description": "Stakeholder consultations and consensus building.",
        },
        MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL: {
            "gradient": "from-emerald-500 to-emerald-600",
            "icon": "fa-gavel",
            "description": "Final executive clearance before rollout.",
        },
        MonitoringEntry.APPROVAL_STATUS_APPROVED: {
            "gradient": "from-teal-500 to-cyan-500",
            "icon": "fa-circle-check",
            "description": "Approved PPAs awaiting enactment.",
        },
        MonitoringEntry.APPROVAL_STATUS_ENACTED: {
            "gradient": "from-sky-500 to-blue-500",
            "icon": "fa-seedling",
            "description": "Enacted and funded PPAs ready for execution.",
        },
        MonitoringEntry.APPROVAL_STATUS_REJECTED: {
            "gradient": "from-rose-500 to-rose-600",
            "icon": "fa-circle-xmark",
            "description": "Items returned or declined during review.",
        },
    }

    stage_cards = []
    for stage_value, stage_label in MonitoringEntry.APPROVAL_STATUS_CHOICES:
        style = stage_styles.get(
            stage_value, stage_styles[MonitoringEntry.APPROVAL_STATUS_DRAFT]
        )
        stage_cards.append(
            {
                "key": stage_value,
                "label": stage_label,
                "count": approval_counts[stage_value]["count"],
                "gradient": style["gradient"],
                "icon": style["icon"],
                "description": style["description"],
            }
        )

    # Get PPAs pending approval (in review stages)
    pending_approvals = MonitoringEntry.objects.filter(
        approval_status__in=[
            MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW,
            MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW,
            MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION,
            MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL,
        ]
    ).order_by("approval_status", "-created_at")

    # Get recently approved PPAs
    recently_approved = MonitoringEntry.objects.filter(
        approval_status__in=[
            MonitoringEntry.APPROVAL_STATUS_APPROVED,
            MonitoringEntry.APPROVAL_STATUS_ENACTED,
        ]
    ).order_by("-updated_at")[:10]

    # Get recently rejected PPAs
    recently_rejected = MonitoringEntry.objects.filter(
        approval_status=MonitoringEntry.APPROVAL_STATUS_REJECTED
    ).order_by("-updated_at")[:5]

    context = {
        "stage_cards": stage_cards,
        "pending_approvals": pending_approvals,
        "recently_approved": recently_approved,
        "recently_rejected": recently_rejected,
        "total_pending": pending_approvals.count(),
    }

    return render(request, "project_central/budget_approval_dashboard.html", context)


@login_required
def review_budget_approval(request, ppa_id):
    """Review a PPA for budget approval."""
    from .services import BudgetApprovalService

    ppa = get_object_or_404(MonitoringEntry, id=ppa_id)

    # Validate budget ceiling compliance
    is_valid, errors = BudgetApprovalService.validate_budget_ceiling(ppa)

    # Get approval history
    approval_history = ppa.approval_history if ppa.approval_history else []

    context = {
        "ppa": ppa,
        "is_ceiling_compliant": is_valid,
        "ceiling_errors": errors,
        "approval_history": approval_history,
        "can_approve": BudgetApprovalService.can_advance_approval_stage(
            ppa, request.user
        ),
    }

    return render(request, "project_central/review_budget_approval.html", context)


@login_required
def approve_budget(request, ppa_id):
    """Approve a PPA and advance approval stage."""
    from .services import BudgetApprovalService

    ppa = get_object_or_404(MonitoringEntry, id=ppa_id)

    if request.method == "POST":
        notes = request.POST.get("notes", "")

        # Determine next stage based on current status
        next_stage_map = {
            MonitoringEntry.APPROVAL_STATUS_TECHNICAL_REVIEW: MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW,
            MonitoringEntry.APPROVAL_STATUS_BUDGET_REVIEW: MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION,
            MonitoringEntry.APPROVAL_STATUS_STAKEHOLDER_CONSULTATION: MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL,
            MonitoringEntry.APPROVAL_STATUS_EXECUTIVE_APPROVAL: MonitoringEntry.APPROVAL_STATUS_APPROVED,
        }

        next_stage = next_stage_map.get(ppa.approval_status)

        if next_stage:
            try:
                BudgetApprovalService.advance_approval_stage(
                    ppa, next_stage, request.user, notes
                )
                messages.success(
                    request,
                    f"PPA '{ppa.title}' has been approved and advanced to next stage.",
                )
                return redirect("project_central:budget_approval_dashboard")
            except ValueError as e:
                messages.error(request, f"Approval failed: {str(e)}")
                return redirect("project_central:review_budget_approval", ppa_id=ppa_id)
        else:
            messages.error(request, "Cannot determine next approval stage.")
            return redirect("project_central:review_budget_approval", ppa_id=ppa_id)

    return redirect("project_central:review_budget_approval", ppa_id=ppa_id)


@login_required
def reject_budget(request, ppa_id):
    """Reject a PPA with reason."""
    from .services import BudgetApprovalService

    ppa = get_object_or_404(MonitoringEntry, id=ppa_id)

    if request.method == "POST":
        reason = request.POST.get("reason", "")

        if not reason:
            messages.error(request, "Rejection reason is required.")
            return redirect("project_central:review_budget_approval", ppa_id=ppa_id)

        try:
            BudgetApprovalService.reject_approval(ppa, request.user, reason)
            messages.success(request, f"PPA '{ppa.title}' has been rejected.")
            return redirect("project_central:budget_approval_dashboard")
        except Exception as e:
            messages.error(request, f"Rejection failed: {str(e)}")
            return redirect("project_central:review_budget_approval", ppa_id=ppa_id)

    return redirect("project_central:review_budget_approval", ppa_id=ppa_id)


# ========== PHASE 6: M&E ANALYTICS DASHBOARDS ==========


@login_required
def project_calendar_view(request, workflow_id):
    """Display project-specific calendar view."""
    workflow = get_object_or_404(
        ProjectWorkflow.objects.select_related('primary_need', 'project_lead'),
        pk=workflow_id
    )

    context = {
        'workflow': workflow,
    }

    return render(request, 'project_central/project_calendar.html', context)


@login_required
def project_calendar_events(request, workflow_id):
    """Return calendar events for a specific project."""
    workflow = get_object_or_404(ProjectWorkflow, pk=workflow_id)

    events = []

    # Project activities (events)
    for event in workflow.project_activities.all():
        events.append({
            'id': f'event-{event.id}',
            'title': event.title,
            'start': event.start_datetime.isoformat() if event.start_datetime else event.start_date.isoformat(),
            'end': event.end_datetime.isoformat() if event.end_datetime else None,
            'backgroundColor': '#8b5cf6',  # Purple for project activities
            'borderColor': '#7c3aed',
            'url': f'/api/coordination/events/{event.id}/',
            'extendedProps': {
                'type': 'activity',
                'activity_type': event.project_activity_type,
                'status': event.status,
            }
        })

    # Project tasks with due dates
    for task in workflow.all_project_tasks:
        if task.due_date:
            events.append({
                'id': f'task-{task.id}',
                'title': task.title,
                'start': task.due_date.isoformat(),
                'backgroundColor': '#3b82f6',  # Blue for tasks
                'borderColor': '#2563eb',
                'url': f'/oobc-management/staff/tasks/{task.id}/',
                'extendedProps': {
                    'type': 'task',
                    'priority': task.priority,
                    'status': task.status,
                    'task_context': task.task_context,
                }
            })

    return JsonResponse(events, safe=False)


@login_required
def ppa_me_dashboard(request, ppa_id):
    """
    M&E dashboard for single PPA with detailed analytics.

    Shows:
    - Progress metrics (budget, timeline, beneficiaries)
    - Outcome framework (if defined in outcome_framework JSON field)
    - Accomplishments narrative
    - Challenges and support required
    - Related needs and policies
    """
    ppa = get_object_or_404(MonitoringEntry, id=ppa_id)

    # Calculate progress metrics
    today = timezone.now().date()

    # Budget progress (using budget_allocation as baseline)
    budget_allocation = float(ppa.budget_allocation or 0)
    budget_obc_allocation = float(ppa.budget_obc_allocation or 0)
    budget_utilization_pct = (
        (budget_obc_allocation / budget_allocation * 100)
        if budget_allocation > 0
        else 0
    )

    # Timeline progress
    timeline_progress_pct = 0
    days_elapsed = 0
    days_remaining = 0

    if ppa.start_date and ppa.target_end_date:
        total_days = (ppa.target_end_date - ppa.start_date).days
        days_elapsed = (today - ppa.start_date).days if today >= ppa.start_date else 0
        days_remaining = (
            (ppa.target_end_date - today).days if today <= ppa.target_end_date else 0
        )

        if total_days > 0:
            timeline_progress_pct = min(100, (days_elapsed / total_days * 100))

    # Beneficiary progress
    total_slots = ppa.total_slots or 0
    obc_slots = ppa.obc_slots or 0
    beneficiary_progress_pct = (obc_slots / total_slots * 100) if total_slots > 0 else 0

    # Overall progress (from model field)
    overall_progress_pct = ppa.progress

    # Outcome framework (from JSON field)
    outcome_framework_data = (
        ppa.outcome_framework if isinstance(ppa.outcome_framework, dict) else {}
    )
    outcomes = outcome_framework_data.get("outcomes", [])

    # Related needs and policies
    related_needs = ppa.needs_addressed.all()[:10]
    related_policies = ppa.implementing_policies.all()[:5]

    # Communities served
    communities_served = ppa.communities.all()[:10]

    # Milestone tracking
    milestones = ppa.milestone_dates if isinstance(ppa.milestone_dates, list) else []

    # Supporting organizations
    supporting_orgs = ppa.supporting_organizations.all()[:10]

    # Calculate cost effectiveness
    cost_per_beneficiary = float(ppa.cost_per_beneficiary or 0)
    if not cost_per_beneficiary and obc_slots > 0 and budget_obc_allocation > 0:
        cost_per_beneficiary = budget_obc_allocation / obc_slots

    context = {
        "ppa": ppa,
        # Progress metrics
        "budget_utilization_pct": budget_utilization_pct,
        "timeline_progress_pct": timeline_progress_pct,
        "beneficiary_progress_pct": beneficiary_progress_pct,
        "overall_progress_pct": overall_progress_pct,
        # Budget details
        "budget_allocation": budget_allocation,
        "budget_obc_allocation": budget_obc_allocation,
        "cost_per_beneficiary": cost_per_beneficiary,
        # Timeline details
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "total_slots": total_slots,
        "obc_slots": obc_slots,
        # Outcome framework
        "outcomes": outcomes,
        "outcome_indicators": ppa.outcome_indicators,
        # Relationships
        "related_needs": related_needs,
        "related_policies": related_policies,
        "communities_served": communities_served,
        "supporting_orgs": supporting_orgs,
        # Milestones
        "milestones": milestones,
        # Narratives
        "accomplishments": ppa.accomplishments,
        "challenges": ppa.challenges,
        "support_required": ppa.support_required,
        "follow_up_actions": ppa.follow_up_actions,
    }

    return render(request, "project_central/ppa_me_dashboard.html", context)
