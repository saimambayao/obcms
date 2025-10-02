"""Dashboard landing views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone


@login_required
def dashboard(request):
    """Main dashboard view after login."""

    # Redirect MANA Participants and Facilitators to their respective dashboards
    if not request.user.is_staff and not request.user.is_superuser:
        if request.user.has_perm("mana.can_access_regional_mana"):
            # Facilitators go to Manage Assessments dashboard
            if request.user.has_perm("mana.can_facilitate_workshop"):
                return redirect("common:mana_manage_assessments")
            # Participants go to their participant dashboard
            else:
                # Get participant's assessment
                try:
                    from mana.models import WorkshopParticipantAccount

                    participant = WorkshopParticipantAccount.objects.get(
                        user=request.user
                    )
                    # Redirect to participant dashboard for their assessment
                    return redirect(
                        "mana:participant_dashboard",
                        assessment_id=str(participant.assessment.id),
                    )
                except WorkshopParticipantAccount.DoesNotExist:
                    # No participant account - redirect to regional overview
                    return redirect("common:mana_regional_overview")

    from django.db.models import Avg, Count

    from communities.models import (
        MunicipalityCoverage,
        OBCCommunity,
        Stakeholder,
    )
    from coordination.models import Event, Partnership
    from mana.models import Assessment, Need
    from monitoring.models import MonitoringEntry
    from recommendations.policy_tracking.models import PolicyRecommendation
    from common.models import User

    communities_qs = OBCCommunity.objects.all()
    barangay_total = communities_qs.count()
    municipal_total = MunicipalityCoverage.objects.count()
    combined_total = barangay_total + municipal_total

    oobc_staff_qs = User.objects.filter(user_type__in=["oobc_staff", "admin"])

    stats = {
        "communities": {
            "total": barangay_total,
            "combined_total": combined_total,
            "barangay_total": barangay_total,
            "municipal_total": municipal_total,
            "active": communities_qs.filter(is_active=True).count(),
            "by_region": communities_qs.values(
                "barangay__municipality__province__region__name"
            ).annotate(count=Count("id"))[:5],
            "recent": communities_qs.order_by("-created_at")[:5],
        },
        "mana": {
            "total_assessments": Assessment.objects.count(),
            "completed": Assessment.objects.filter(status="completed").count(),
            "in_progress": Assessment.objects.filter(
                status__in=["data_collection", "analysis"]
            ).count(),
            "high_priority": Need.objects.filter(impact_severity=5).count(),
        },
        "monitoring": {
            "total": MonitoringEntry.objects.count(),
            "moa_ppa": MonitoringEntry.objects.filter(category="moa_ppa").count(),
            "oobc_ppa": MonitoringEntry.objects.filter(category="oobc_ppa").count(),
            "obc_requests": MonitoringEntry.objects.filter(
                category="obc_request"
            ).count(),
            "pending_requests": MonitoringEntry.objects.filter(
                category="obc_request",
                request_status__in=[
                    "submitted",
                    "under_review",
                    "clarification",
                    "endorsed",
                ],
            ).count(),
            "avg_progress": MonitoringEntry.objects.aggregate(avg=Avg("progress"))[
                "avg"
            ]
            or 0,
            "linked_assessments": MonitoringEntry.objects.filter(
                related_assessment__isnull=False
            ).count(),
            "linked_events": MonitoringEntry.objects.filter(
                related_event__isnull=False
            ).count(),
            "linked_policies": MonitoringEntry.objects.filter(
                related_policy__isnull=False
            ).count(),
        },
        "coordination": {
            "total_events": Event.objects.count(),
            "active_partnerships": Partnership.objects.filter(status="active").count(),
            "upcoming_events": Event.objects.filter(
                start_date__gte=timezone.now().date(), status="planned"
            ).count(),
            "pending_actions": 0,
            "bmoas": Partnership.objects.filter(
                status="active", lead_organization__organization_type="bmoa"
            ).count(),
            "ngas": Partnership.objects.filter(
                status="active", lead_organization__organization_type="nga"
            ).count(),
            "lgus": Partnership.objects.filter(
                status="active", lead_organization__organization_type="lgu"
            ).count(),
        },
        "policy_tracking": {
            "total_policies": PolicyRecommendation.objects.count(),
            "implemented": PolicyRecommendation.objects.filter(
                status="implemented"
            ).count(),
            "under_review": PolicyRecommendation.objects.filter(
                status="under_review"
            ).count(),
            "high_priority": PolicyRecommendation.objects.filter(
                priority__in=["high", "urgent", "critical"]
            ).count(),
            "total_recommendations": PolicyRecommendation.objects.count(),
            "policies": PolicyRecommendation.objects.filter(
                category__in=["governance", "legal_framework", "administrative"]
            ).count(),
            "programs": PolicyRecommendation.objects.filter(
                category__in=[
                    "education",
                    "economic_development",
                    "social_development",
                    "cultural_development",
                ]
            ).count(),
            "services": PolicyRecommendation.objects.filter(
                category__in=[
                    "healthcare",
                    "infrastructure",
                    "environment",
                    "human_rights",
                ]
            ).count(),
        },
        "oobc_management": {
            "total_staff": oobc_staff_qs.count(),
            "active_staff": oobc_staff_qs.filter(is_active=True).count(),
            "pending_approvals": User.objects.filter(is_approved=False).count(),
        },
    }

    context = {
        "user": request.user,
        "user_type_display": request.user.get_user_type_display(),
        "is_approved": request.user.is_approved,
        "stats": stats,
    }
    return render(request, "common/dashboard.html", context)


@login_required
def dashboard_metrics(request):
    """Live metrics HTML (updates every 60s)."""
    from django.http import HttpResponse
    from django.db.models import Sum
    from datetime import timedelta

    try:
        # Import models safely
        from monitoring.models import MonitoringEntry
        from mana.models import Need
        from coordination.models import Event
        from common.models.staff import StaffTask

        # Aggregate from all modules
        total_budget = (
            MonitoringEntry.objects.aggregate(total=Sum("budget_allocation"))["total"]
            or 0
        )

        active_projects = MonitoringEntry.objects.filter(status="ongoing").count()

        unfunded_needs = Need.objects.filter(
            linked_ppa__isnull=True, priority_score__gte=4.0
        ).count()

        total_beneficiaries = (
            MonitoringEntry.objects.aggregate(total=Sum("obc_slots"))["total"] or 0
        )

        upcoming_events = Event.objects.filter(
            start_date__gte=timezone.now().date(),
            start_date__lte=timezone.now().date() + timedelta(days=7),
        ).count()

        current_week = timezone.now().isocalendar()[1]
        tasks_due = StaffTask.objects.filter(
            due_date__week=current_week, status__in=["not_started", "in_progress"]
        ).count()

    except Exception as e:
        # Fallback values if models don't exist
        total_budget = 0
        active_projects = 0
        unfunded_needs = 0
        total_beneficiaries = 0
        upcoming_events = 0
        tasks_due = 0

    # Render metric cards
    html = f"""
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="metric-card bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-600">Total Budget</p>
                    <p class="text-3xl font-bold text-emerald-600">₱{total_budget/1_000_000:.1f}M</p>
                </div>
                <div class="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-money-bill-wave text-emerald-600 text-xl"></i>
                </div>
            </div>
        </div>

        <div class="metric-card bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-600">Active Projects</p>
                    <p class="text-3xl font-bold text-blue-600">{active_projects}</p>
                </div>
                <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-project-diagram text-blue-600 text-xl"></i>
                </div>
            </div>
        </div>

        <div class="metric-card bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-600">High-Priority Needs</p>
                    <p class="text-3xl font-bold text-red-600">{unfunded_needs}</p>
                    <p class="text-xs text-gray-500">Unfunded</p>
                </div>
                <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
                </div>
            </div>
        </div>

        <div class="metric-card bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-600">OBC Beneficiaries</p>
                    <p class="text-3xl font-bold text-purple-600">{total_beneficiaries:,}</p>
                </div>
                <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-users text-purple-600 text-xl"></i>
                </div>
            </div>
        </div>

        <div class="metric-card bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-600">Upcoming Events</p>
                    <p class="text-3xl font-bold text-orange-600">{upcoming_events}</p>
                    <p class="text-xs text-gray-500">Next 7 days</p>
                </div>
                <div class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-calendar text-orange-600 text-xl"></i>
                </div>
            </div>
        </div>

        <div class="metric-card bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-600">Tasks Due This Week</p>
                    <p class="text-3xl font-bold text-yellow-600">{tasks_due}</p>
                </div>
                <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-tasks text-yellow-600 text-xl"></i>
                </div>
            </div>
        </div>
    </div>
    """

    return HttpResponse(html)


@login_required
def dashboard_activity(request):
    """Recent activity feed (infinite scroll)."""
    from django.http import HttpResponse
    from datetime import timedelta

    page = int(request.GET.get("page", 1))
    per_page = 20

    # Aggregate recent items from all modules
    activities = []

    try:
        from mana.models import Need
        from monitoring.models import MonitoringEntry
        from common.models.staff import StaffTask
        from coordination.models import Event

        # Recent needs
        for need in Need.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related("community")[:10]:
            activities.append(
                {
                    "icon": "fa-lightbulb",
                    "color": "blue",
                    "title": f"New need: {need.title}",
                    "subtitle": f"in {need.community}",
                    "timestamp": need.created_at,
                    "url": "#",
                }
            )

        # Recent PPAs
        for ppa in MonitoringEntry.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )[:10]:
            lead_org = ppa.lead_organization.name if ppa.lead_organization else "OOBC"
            activities.append(
                {
                    "icon": "fa-project-diagram",
                    "color": "emerald",
                    "title": f"New PPA: {ppa.title}",
                    "subtitle": f"Lead: {lead_org}",
                    "timestamp": ppa.created_at,
                    "url": f"/monitoring/entry/{ppa.id}/",
                }
            )

        # Recent tasks completed
        for task in StaffTask.objects.filter(
            status="completed", updated_at__gte=timezone.now() - timedelta(days=30)
        ).select_related("assigned_to")[:10]:
            activities.append(
                {
                    "icon": "fa-check-circle",
                    "color": "green",
                    "title": f"Task completed: {task.title}",
                    "subtitle": f'by {task.assigned_to.get_full_name() if task.assigned_to else "Unassigned"}',
                    "timestamp": task.updated_at,
                    "url": "#",
                }
            )

        # Recent events
        for event in Event.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )[:10]:
            activities.append(
                {
                    "icon": "fa-calendar",
                    "color": "purple",
                    "title": f"Event scheduled: {event.title}",
                    "subtitle": f'{event.start_date.strftime("%b %d, %Y")}',
                    "timestamp": event.created_at,
                    "url": "#",
                }
            )

    except Exception:
        # Fallback empty activities
        pass

    # Sort by timestamp
    activities = sorted(activities, key=lambda x: x["timestamp"], reverse=True)

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    activities_page = activities[start:end]
    has_next = len(activities) > end

    # Render HTML
    html = '<div class="space-y-3">'
    for activity in activities_page:
        timestamp_str = activity["timestamp"].strftime("%b %d, %I:%M %p")
        html += f"""
        <a href="{activity['url']}" class="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
            <div class="w-10 h-10 bg-{activity['color']}-100 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas {activity['icon']} text-{activity['color']}-600"></i>
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{activity['title']}</p>
                <p class="text-xs text-gray-500 truncate">{activity['subtitle']}</p>
                <p class="text-xs text-gray-400 mt-1">{timestamp_str}</p>
            </div>
        </a>
        """

    if not activities_page:
        html += """
        <div class="text-center py-8 text-gray-400">
            <i class="fas fa-inbox text-3xl mb-2"></i>
            <p class="text-sm">No recent activity</p>
        </div>
        """

    html += "</div>"

    # Infinite scroll trigger
    if has_next:
        html += f"""
        <div hx-get="/dashboard/activity/?page={page + 1}" hx-trigger="revealed" hx-swap="afterend" class="text-center py-4">
            <i class="fas fa-spinner fa-spin text-gray-400"></i>
        </div>
        """

    return HttpResponse(html)


@login_required
def dashboard_alerts(request):
    """Critical alerts (updates every 30s)."""
    from django.http import HttpResponse

    alerts = []

    try:
        from mana.models import Need
        from common.models.staff import StaffTask

        # Unfunded needs
        unfunded = Need.objects.filter(
            linked_ppa__isnull=True, priority_score__gte=4.0
        ).count()

        if unfunded > 0:
            alerts.append(
                {
                    "type": "warning",
                    "icon": "fa-exclamation-triangle",
                    "title": f"{unfunded} high-priority needs unfunded",
                    "action_url": "#",
                    "action_text": "Review",
                }
            )

        # Overdue tasks
        overdue = StaffTask.objects.filter(
            due_date__lt=timezone.now().date(),
            status__in=["not_started", "in_progress"],
        ).count()

        if overdue > 0:
            alerts.append(
                {
                    "type": "danger",
                    "icon": "fa-clock",
                    "title": f"{overdue} tasks overdue",
                    "action_url": "/oobc-management/staff/tasks/",
                    "action_text": "View",
                }
            )

    except Exception:
        # Fallback empty alerts
        pass

    # Render
    if not alerts:
        return HttpResponse(
            """
        <div class="flex items-center p-4 bg-green-50 border border-green-200 rounded-lg">
            <i class="fas fa-check-circle text-green-600 mr-3"></i>
            <span class="text-sm font-medium text-green-800">All systems normal</span>
        </div>
        """
        )

    html = '<div class="space-y-2">'
    for alert in alerts:
        colors = {"danger": "red", "warning": "yellow"}
        color = colors.get(alert["type"], "yellow")
        html += f"""
        <div class="flex items-center justify-between p-4 bg-{color}-50 border border-{color}-200 rounded-lg">
            <div class="flex items-center space-x-3 flex-1 min-w-0">
                <i class="fas {alert['icon']} text-{color}-600 flex-shrink-0"></i>
                <span class="text-sm font-medium text-{color}-800 truncate">{alert['title']}</span>
            </div>
            <a href="{alert['action_url']}" class="ml-3 text-sm font-medium text-{color}-700 hover:text-{color}-800 flex-shrink-0">
                {alert['action_text']} →
            </a>
        </div>
        """
    html += "</div>"

    return HttpResponse(html)


@login_required
def dashboard_stats_cards(request):
    """Render dashboard stats cards (HTMX endpoint - not implemented yet)."""
    from django.http import HttpResponse
    return HttpResponse("Not implemented", status=501)


__all__ = ["dashboard", "dashboard_stats_cards", "dashboard_metrics", "dashboard_activity", "dashboard_alerts"]
