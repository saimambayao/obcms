"""Task management views with domain-specific filtering and analytics."""

import warnings
from datetime import timedelta
import json

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count, Q, Avg, Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from common.models import StaffTask, TaskTemplate, TaskTemplateItem
from common.services.task_automation import create_tasks_from_template
from common.utils.deprecation import deprecation_warning


# ============================================================================
# Domain-Specific Task Views (DEPRECATED - Use WorkItem views instead)
# ============================================================================


@login_required
def tasks_by_domain(request, domain):
    """View tasks filtered by specific domain.

    DEPRECATED: This view is deprecated and will be removed in a future release.
    Please use WorkItem views instead.
    """
    deprecation_warning('tasks_by_domain', 'WorkItem views')

    tasks = (
        StaffTask.objects.filter(domain=domain)
        .select_related(
            "created_by",
            "related_assessment",
            "related_policy",
            "related_ppa",
            "linked_event",
            "created_from_template",
        )
        .prefetch_related(
            "assignees",
            "teams",
        )
        .order_by("-created_at")
    )

    # Additional filtering from query params
    status = request.GET.get("status")
    if status:
        tasks = tasks.filter(status=status)

    priority = request.GET.get("priority")
    if priority:
        tasks = tasks.filter(priority=priority)

    phase = request.GET.get("phase")
    if phase and domain == StaffTask.DOMAIN_MANA:
        tasks = tasks.filter(assessment_phase=phase)
    elif phase and domain == StaffTask.DOMAIN_POLICY:
        tasks = tasks.filter(policy_phase=phase)
    elif phase and domain == StaffTask.DOMAIN_SERVICES:
        tasks = tasks.filter(service_phase=phase)

    context = {
        "domain": domain,
        "domain_display": dict(StaffTask.DOMAIN_CHOICES).get(domain, "Unknown"),
        "tasks": tasks,
        "status_choices": StaffTask.STATUS_CHOICES,
        "priority_choices": StaffTask.PRIORITY_CHOICES,
    }

    if domain == StaffTask.DOMAIN_MANA:
        context["phase_choices"] = StaffTask.ASSESSMENT_PHASE_CHOICES
    elif domain == StaffTask.DOMAIN_POLICY:
        context["phase_choices"] = StaffTask.POLICY_PHASE_CHOICES
    elif domain == StaffTask.DOMAIN_SERVICES:
        context["phase_choices"] = StaffTask.SERVICE_PHASE_CHOICES

    return render(request, "common/tasks/domain_tasks.html", context)


@login_required
def assessment_tasks(request, assessment_id):
    """View all tasks for a specific assessment, grouped by phase.

    DEPRECATED: This view is deprecated and will be removed in a future release.
    Please use WorkItem views instead.
    """
    deprecation_warning('assessment_tasks', 'WorkItem views')

    from mana.models import Assessment

    assessment = get_object_or_404(Assessment, id=assessment_id)
    tasks = (
        StaffTask.objects.filter(related_assessment=assessment)
        .select_related(
            "created_by",
            "created_from_template",
        )
        .prefetch_related(
            "assignees",
            "teams",
        )
        .order_by("assessment_phase", "due_date", "title")
    )

    # Group by phase
    tasks_by_phase = {}
    for task in tasks:
        phase = task.assessment_phase or "unassigned"
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append(task)

    context = {
        "assessment": assessment,
        "tasks": tasks,
        "tasks_by_phase": tasks_by_phase,
        "phase_choices": StaffTask.ASSESSMENT_PHASE_CHOICES,
    }

    return render(request, "common/tasks/assessment_tasks.html", context)


@login_required
def event_tasks(request, event_id):
    """View all tasks for a specific event."""
    from coordination.models import Event

    event = get_object_or_404(Event, id=event_id)
    tasks = (
        StaffTask.objects.filter(linked_event=event)
        .select_related(
            "created_by",
            "created_from_template",
        )
        .prefetch_related(
            "assignees",
            "teams",
        )
        .order_by("due_date")
    )

    context = {
        "event": event,
        "tasks": tasks,
    }

    return render(request, "common/tasks/event_tasks.html", context)


@login_required
def policy_tasks(request, policy_id):
    """View all tasks for a specific policy, grouped by phase."""
    from policy_tracking.models import PolicyRecommendation

    policy = get_object_or_404(PolicyRecommendation, id=policy_id)
    tasks = (
        StaffTask.objects.filter(related_policy=policy)
        .select_related(
            "created_by",
            "created_from_template",
        )
        .prefetch_related(
            "assignees",
            "teams",
        )
        .order_by("policy_phase", "due_date")
    )

    # Group by phase
    tasks_by_phase = {}
    for task in tasks:
        phase = task.policy_phase or "unassigned"
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append(task)

    context = {
        "policy": policy,
        "tasks": tasks,
        "tasks_by_phase": tasks_by_phase,
        "phase_choices": StaffTask.POLICY_PHASE_CHOICES,
    }

    return render(request, "common/tasks/policy_tasks.html", context)


@login_required
def ppa_tasks(request, ppa_id):
    """View all tasks for a specific PPA."""
    from monitoring.models import MonitoringEntry

    ppa = get_object_or_404(MonitoringEntry, id=ppa_id)
    tasks = (
        StaffTask.objects.filter(related_ppa=ppa)
        .select_related(
            "created_by",
            "created_from_template",
        )
        .prefetch_related(
            "assignees",
            "teams",
        )
        .order_by("task_role", "due_date")
    )

    # Group by role
    tasks_by_role = {}
    for task in tasks:
        role = task.task_role or "unassigned"
        if role not in tasks_by_role:
            tasks_by_role[role] = []
        tasks_by_role[role].append(task)

    context = {
        "ppa": ppa,
        "tasks": tasks,
        "tasks_by_role": tasks_by_role,
        "role_choices": StaffTask.TASK_ROLE_CHOICES,
    }

    return render(request, "common/tasks/ppa_tasks.html", context)


@login_required
def service_tasks(request, service_id):
    """View all tasks for a specific service."""
    from services.models import ServiceOffering

    service = get_object_or_404(ServiceOffering, id=service_id)
    tasks = (
        StaffTask.objects.filter(related_service=service)
        .select_related(
            "created_by",
            "created_from_template",
        )
        .prefetch_related(
            "assignees",
            "teams",
        )
        .order_by("service_phase", "due_date")
    )

    context = {
        "service": service,
        "tasks": tasks,
    }

    return render(request, "common/tasks/service_tasks.html", context)


# ============================================================================
# Enhanced Task Dashboard (DEPRECATED - Use WorkItem dashboard instead)
# ============================================================================


@login_required
def enhanced_task_dashboard(request):
    """Enhanced task dashboard with domain filtering and analytics.

    DEPRECATED: This view is deprecated and will be removed in a future release.
    Please use WorkItem dashboard instead.
    """
    deprecation_warning('enhanced_task_dashboard', 'WorkItem dashboard')

    # Get user's tasks with optimized queries
    my_tasks = (
        StaffTask.objects.filter(assignees=request.user)
        .select_related(
            "created_by",
            "related_assessment",
            "related_policy",
            "related_ppa",
            "linked_event",
        )
        .prefetch_related(
            "assignees",
            "teams",
        )
    )

    # Apply filters
    domain_filter = request.GET.get("domain")
    if domain_filter and domain_filter != "all":
        my_tasks = my_tasks.filter(domain=domain_filter)

    status_filter = request.GET.get("status")
    if status_filter:
        my_tasks = my_tasks.filter(status=status_filter)

    priority_filter = request.GET.get("priority")
    if priority_filter:
        my_tasks = my_tasks.filter(priority=priority_filter)

    # Sort
    sort_by = request.GET.get("sort", "due_date")
    my_tasks = my_tasks.order_by(sort_by)

    # Compute quick stats
    stats = {
        "total": my_tasks.count(),
        "not_started": my_tasks.filter(status=StaffTask.STATUS_NOT_STARTED).count(),
        "in_progress": my_tasks.filter(status=StaffTask.STATUS_IN_PROGRESS).count(),
        "at_risk": my_tasks.filter(status=StaffTask.STATUS_AT_RISK).count(),
        "completed": my_tasks.filter(status=StaffTask.STATUS_COMPLETED).count(),
        "overdue": my_tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=[StaffTask.STATUS_NOT_STARTED, StaffTask.STATUS_IN_PROGRESS],
        ).count(),
    }

    # Domain breakdown
    domain_stats = (
        my_tasks.values("domain").annotate(count=Count("id")).order_by("-count")
    )

    context = {
        "my_tasks": my_tasks,
        "stats": stats,
        "domain_stats": domain_stats,
        "domain_choices": StaffTask.DOMAIN_CHOICES,
        "status_choices": StaffTask.STATUS_CHOICES,
        "priority_choices": StaffTask.PRIORITY_CHOICES,
        "selected_domain": domain_filter or "all",
        "selected_status": status_filter,
        "selected_priority": priority_filter,
        "sort_by": sort_by,
    }

    return render(request, "common/tasks/enhanced_dashboard.html", context)


# ============================================================================
# Task Analytics Views (DEPRECATED - Use WorkItem analytics instead)
# ============================================================================


@login_required
def task_analytics(request):
    """Overall task analytics dashboard.

    DEPRECATED: This view is deprecated and will be removed in a future release.
    Please use WorkItem analytics instead.
    """
    deprecation_warning('task_analytics', 'WorkItem analytics')

    # Overall statistics
    total_tasks = StaffTask.objects.count()

    # Status breakdown summarised for template consumption
    status_counts_qs = StaffTask.objects.values("status").annotate(count=Count("id"))
    status_counts = {row["status"]: row["count"] for row in status_counts_qs}
    status_breakdown = {
        "total": total_tasks,
        "completed": status_counts.get(StaffTask.STATUS_COMPLETED, 0),
        "in_progress": status_counts.get(StaffTask.STATUS_IN_PROGRESS, 0),
        "not_started": status_counts.get(StaffTask.STATUS_NOT_STARTED, 0),
        "at_risk": status_counts.get(StaffTask.STATUS_AT_RISK, 0),
        "cancelled": status_counts.get("cancelled", 0),
    }

    # Domain breakdown
    domain_breakdown = (
        StaffTask.objects.values("domain")
        .annotate(
            count=Count("id"),
            completed=Count("id", filter=Q(status=StaffTask.STATUS_COMPLETED)),
            in_progress=Count("id", filter=Q(status=StaffTask.STATUS_IN_PROGRESS)),
            overdue=Count(
                "id",
                filter=Q(
                    due_date__lt=timezone.now().date(),
                    status__in=[
                        StaffTask.STATUS_NOT_STARTED,
                        StaffTask.STATUS_IN_PROGRESS,
                    ],
                ),
            ),
        )
        .order_by("-count")
    )

    # Priority distribution
    priority_breakdown = (
        StaffTask.objects.values("priority")
        .annotate(count=Count("id"))
        .order_by("priority")
    )

    # Completion rates by domain
    completion_rates = []
    for domain_code, domain_name in StaffTask.DOMAIN_CHOICES:
        domain_tasks = StaffTask.objects.filter(domain=domain_code)
        total = domain_tasks.count()
        if total > 0:
            completed = domain_tasks.filter(status=StaffTask.STATUS_COMPLETED).count()
            completion_rates.append(
                {
                    "domain": domain_name,
                    "total": total,
                    "completed": completed,
                    "rate": round((completed / total) * 100, 1),
                }
            )

    # Effort tracking
    effort_stats = StaffTask.objects.aggregate(
        total_estimated=Sum("estimated_hours"),
        total_actual=Sum("actual_hours"),
        avg_estimated=Avg("estimated_hours"),
        avg_actual=Avg("actual_hours"),
    )

    # Recent activity (tasks completed in last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_completed = StaffTask.objects.filter(
        completed_at__gte=thirty_days_ago
    ).count()

    stats_summary = {
        "total_tasks": total_tasks,
        "completed_tasks": status_breakdown["completed"],
        "in_progress_tasks": status_breakdown["in_progress"],
        "not_started_tasks": status_breakdown["not_started"],
        "at_risk_tasks": status_breakdown["at_risk"],
    }

    context = {
        "total_tasks": total_tasks,
        "status_breakdown": status_breakdown,
        "domain_breakdown": list(domain_breakdown),
        "priority_breakdown": list(priority_breakdown),
        "completion_rates": completion_rates,
        "effort_stats": effort_stats,
        "recent_completed": recent_completed,
        "stats": stats_summary,
        "domain_data": list(domain_breakdown),
        "priority_data": list(priority_breakdown),
        "status_data": list(status_counts_qs),
    }

    return render(request, "common/tasks/analytics.html", context)


@login_required
def domain_task_analytics(request, domain):
    """Domain-specific task analytics."""

    domain_tasks = StaffTask.objects.filter(domain=domain)

    # Basic stats
    stats = {
        "total": domain_tasks.count(),
        "completed": domain_tasks.filter(status=StaffTask.STATUS_COMPLETED).count(),
        "in_progress": domain_tasks.filter(status=StaffTask.STATUS_IN_PROGRESS).count(),
        "not_started": domain_tasks.filter(status=StaffTask.STATUS_NOT_STARTED).count(),
        "overdue": domain_tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=[StaffTask.STATUS_NOT_STARTED, StaffTask.STATUS_IN_PROGRESS],
        ).count(),
    }

    # Phase-specific breakdown
    phase_field = None
    if domain == StaffTask.DOMAIN_MANA:
        phase_field = "assessment_phase"
    elif domain == StaffTask.DOMAIN_POLICY:
        phase_field = "policy_phase"
    elif domain == StaffTask.DOMAIN_SERVICES:
        phase_field = "service_phase"

    phase_breakdown = None
    if phase_field:
        phase_breakdown = (
            domain_tasks.values(phase_field)
            .annotate(
                count=Count("id"),
                completed=Count("id", filter=Q(status=StaffTask.STATUS_COMPLETED)),
            )
            .order_by(phase_field)
        )

    # Team workload (for this domain)
    team_workload = (
        domain_tasks.values("teams__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Assignee workload
    assignee_workload = (
        domain_tasks.values(
            "assignees__username",
            "assignees__first_name",
            "assignees__last_name",
        )
        .annotate(
            count=Count("id"),
            completed=Count("id", filter=Q(status=StaffTask.STATUS_COMPLETED)),
        )
        .order_by("-count")[:10]
    )

    # Effort tracking
    effort_stats = domain_tasks.aggregate(
        total_estimated=Sum("estimated_hours"),
        total_actual=Sum("actual_hours"),
    )

    context = {
        "domain": domain,
        "domain_display": dict(StaffTask.DOMAIN_CHOICES).get(domain, "Unknown"),
        "stats": stats,
        "phase_breakdown": phase_breakdown,
        "phase_field": phase_field,
        "team_workload": team_workload,
        "assignee_workload": assignee_workload,
        "effort_stats": effort_stats,
    }

    return render(request, "common/tasks/domain_analytics.html", context)


# ============================================================================
# Template Management Views
# ============================================================================


@login_required
def task_template_list(request):
    """List all task templates."""
    templates = (
        TaskTemplate.objects.filter(is_active=True)
        .annotate(item_count=Count("items"))
        .order_by("domain", "name")
    )

    domain_filter = request.GET.get("domain")
    if domain_filter:
        templates = templates.filter(domain=domain_filter)

    context = {
        "templates": templates,
        "domain_choices": StaffTask.DOMAIN_CHOICES,
        "selected_domain": domain_filter,
    }

    return render(request, "common/tasks/template_list.html", context)


@login_required
def task_template_detail(request, template_id):
    """View template details with items."""
    template = get_object_or_404(TaskTemplate, id=template_id)
    items = template.items.all().order_by("sequence")

    context = {
        "template": template,
        "items": items,
    }

    return render(request, "common/tasks/template_detail.html", context)


@login_required
@require_http_methods(["POST"])
def instantiate_template(request, template_id):
    """Instantiate a template to create tasks."""
    template = get_object_or_404(TaskTemplate, id=template_id)

    # Get context from POST data
    context_data = json.loads(request.POST.get("context", "{}"))

    # Create tasks
    tasks = create_tasks_from_template(
        template_name=template.name, created_by=request.user, **context_data
    )

    return JsonResponse(
        {
            "success": True,
            "tasks_created": len(tasks),
            "task_ids": [t.id for t in tasks],
        }
    )


# ============================================================================
# Task Quick Actions (HTMX endpoints)
# ============================================================================


@login_required
@require_http_methods(["POST"])
def task_complete(request, task_id):
    """Mark task as completed."""
    task = get_object_or_404(StaffTask, id=task_id)
    task.status = StaffTask.STATUS_COMPLETED
    task.progress = 100
    task.completed_at = timezone.now()
    task.save()

    if request.headers.get("HX-Request"):
        return HttpResponse(
            status=204,
            headers={
                "HX-Trigger": json.dumps(
                    {
                        "task-updated": {"id": task_id, "action": "complete"},
                        "show-toast": "Task marked as completed",
                    }
                )
            },
        )

    return JsonResponse({"success": True, "task_id": task_id})


@login_required
@require_http_methods(["POST"])
def task_start(request, task_id):
    """Mark task as in progress."""
    task = get_object_or_404(StaffTask, id=task_id)
    task.status = StaffTask.STATUS_IN_PROGRESS
    if not task.start_date:
        task.start_date = timezone.now().date()
    task.save()

    if request.headers.get("HX-Request"):
        return HttpResponse(
            status=204,
            headers={
                "HX-Trigger": json.dumps(
                    {
                        "task-updated": {"id": task_id, "action": "start"},
                        "show-toast": "Task started",
                    }
                )
            },
        )

    return JsonResponse({"success": True, "task_id": task_id})


@login_required
@require_http_methods(["POST"])
def task_assign(request, task_id):
    """Assign task to user."""
    task = get_object_or_404(StaffTask, id=task_id)
    user_id = request.POST.get("user_id")

    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = get_object_or_404(User, id=user_id)
    task.assignees.add(user)

    if request.headers.get("HX-Request"):
        return HttpResponse(
            status=204,
            headers={
                "HX-Trigger": json.dumps(
                    {
                        "task-updated": {"id": task_id, "action": "assign"},
                        "show-toast": f"Task assigned to {user.get_full_name() or user.username}",
                    }
                )
            },
        )

    return JsonResponse({"success": True, "task_id": task_id, "user_id": user_id})
