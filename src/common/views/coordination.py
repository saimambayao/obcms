"""Views for coordination module dashboards and listings."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import reverse
from django.template.loader import render_to_string

from coordination.views import (
    coordination_note_activity_options as _coordination_note_activity_options,
    coordination_note_create as _coordination_note_create,
    engagement_create as _engagement_create,
    organization_create as _organization_create,
    organization_delete as _organization_delete,
    organization_detail as _organization_detail,
    organization_edit as _organization_edit,
    organization_work_items_partial as _organization_work_items_partial,
    partnership_create as _partnership_create,
    partnership_delete as _partnership_delete,
    partnership_detail as _partnership_detail,
    partnership_update as _partnership_update,
)
from coordination.utils.organizations import get_organization

# Note: event_create is defined locally in this file (line 389)
# It now redirects to WorkItem system since Event model is deprecated


@login_required
def coordination_home(request):
    """Coordination module home page - coordination with BMOAs, NGAs, and LGUs."""
    from django.shortcuts import redirect

    # Restrict access for MANA participants
    user = request.user
    if (
        not user.is_staff
        and not user.is_superuser
        and user.has_perm("mana.can_access_regional_mana")
        and not user.has_perm("mana.can_facilitate_workshop")
    ):
        messages.error(request, "You do not have permission to access coordination.")
        raise PermissionDenied("User lacks required permission to access coordination")

    from datetime import timedelta

    from django.db.models import Count, Q
    from django.utils import timezone

    from coordination.models import (
        Organization,
        Partnership,
        PartnershipSignatory,
        StakeholderEngagement,
    )
    from common.work_item_model import WorkItem

    now = timezone.now()

    mapped_partners = Organization.objects.filter(
        is_active=True, organization_type__in=["bmoa", "nga", "lgu"]
    ).exclude(description="")

    mapped_partners_stats = {
        "total": mapped_partners.count(),
        "bmoa": mapped_partners.filter(organization_type="bmoa").count(),
        "nga": mapped_partners.filter(organization_type="nga").count(),
        "lgu": mapped_partners.filter(organization_type="lgu").count(),
    }

    active_partnerships = Partnership.objects.filter(status="active")
    bmoa_partnerships = (
        active_partnerships.filter(signatories__organization__organization_type="bmoa")
        .distinct()
        .count()
    )
    nga_partnerships = (
        active_partnerships.filter(signatories__organization__organization_type="nga")
        .distinct()
        .count()
    )
    lgu_partnerships = (
        active_partnerships.filter(signatories__organization__organization_type="lgu")
        .distinct()
        .count()
    )

    active_partnerships_stats = {
        "total": active_partnerships.count(),
        "bmoa": bmoa_partnerships,
        "nga": nga_partnerships,
        "lgu": lgu_partnerships,
    }

    # WorkItem activities (replaced Event model)
    completed_activities = WorkItem.objects.filter(
        work_type=WorkItem.WORK_TYPE_ACTIVITY,
        status=WorkItem.STATUS_COMPLETED
    )
    completed_engagements = StakeholderEngagement.objects.filter(status="completed")

    total_completed_activities = (
        completed_activities.count() + completed_engagements.count()
    )

    # For now, set organization type stats to 0 since WorkItem doesn't have participant tracking
    # This would need to be implemented via activity_data JSON field if needed
    bmoa_events = 0
    nga_events = 0
    lgu_events = 0

    coordination_activities_done_stats = {
        "total": total_completed_activities,
        "bmoa": bmoa_events,
        "nga": nga_events,
        "lgu": lgu_events,
    }

    # WorkItem planned activities (replaced Event model)
    planned_activities = WorkItem.objects.filter(
        work_type=WorkItem.WORK_TYPE_ACTIVITY,
        status__in=[WorkItem.STATUS_NOT_STARTED, WorkItem.STATUS_IN_PROGRESS],
        start_date__gte=now.date()
    )
    planned_engagements = StakeholderEngagement.objects.filter(
        status__in=["planned", "scheduled"], planned_date__gte=now
    )

    total_planned_activities = planned_activities.count() + planned_engagements.count()

    # For now, set organization type stats to 0 since WorkItem doesn't have participant tracking
    bmoa_planned = 0
    nga_planned = 0
    lgu_planned = 0

    planned_coordination_activities_stats = {
        "total": total_planned_activities,
        "bmoa": bmoa_planned,
        "nga": nga_planned,
        "lgu": lgu_planned,
    }

    # Recent WorkItem activities (replaced Event model)
    recent_events = WorkItem.objects.filter(
        work_type=WorkItem.WORK_TYPE_ACTIVITY
    ).order_by("-updated_at", "-created_at")[:10]

    # Event types from activity_data JSON field
    all_activities = WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_ACTIVITY)
    event_by_type = {
        "meeting": sum(1 for a in all_activities if (a.activity_data or {}).get("event_type") == "meeting"),
        "workshop": sum(1 for a in all_activities if (a.activity_data or {}).get("event_type") == "workshop"),
        "conference": sum(1 for a in all_activities if (a.activity_data or {}).get("event_type") == "conference"),
        "consultation": sum(1 for a in all_activities if (a.activity_data or {}).get("event_type") == "consultation"),
    }

    active_partnerships_list = Partnership.objects.filter(status="active").order_by(
        "-updated_at", "-created_at"
    )[:10]

    recent_partnerships = Partnership.objects.order_by("-updated_at", "-created_at")[
        :10
    ]

    recent_partners = (
        Organization.objects.filter(is_active=True)
        .order_by("-updated_at", "-created_at")[:10]
    )

    stats = {
        "mapped_partners": mapped_partners_stats,
        "active_partnerships": active_partnerships_stats,
        "coordination_activities_done": coordination_activities_done_stats,
        "planned_coordination_activities": planned_coordination_activities_stats,
        "coordination": {
            "active_partnerships": active_partnerships_list,
            "by_type": event_by_type,
        },
        "recent": {
            "events": recent_events,
            "partners": recent_partners,
            "partnerships": recent_partnerships,
        },
    }

    return render(request, "coordination/coordination_home.html", {"stats": stats})


@login_required
def coordination_organizations(request):
    """Manage coordination organizations page."""
    from django.db.models import Count, F, Q

    from coordination.models import Organization, OrganizationContact

    organizations = (
        Organization.objects.annotate(
            contacts_count=Count("contacts", distinct=True),
            led_partnerships_count=Count("led_partnerships", distinct=True),
            member_partnerships_count=Count("partnerships", distinct=True),
        )
        .annotate(
            partnerships_count=F("led_partnerships_count")
            + F("member_partnerships_count")
        )
        .order_by("name")
    )

    type_filter = request.GET.get("type")
    status_filter = request.GET.get("status")
    search_query = request.GET.get("search")

    if type_filter:
        organizations = organizations.filter(organization_type=type_filter)

    if status_filter == "active":
        organizations = organizations.filter(is_active=True)
    elif status_filter == "inactive":
        organizations = organizations.filter(is_active=False)

    if search_query:
        organizations = organizations.filter(
            Q(name__icontains=search_query)
            | Q(acronym__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(head_of_organization__icontains=search_query)
            | Q(focal_person__icontains=search_query)
        )

    org_types = (
        Organization.ORGANIZATION_TYPE_CHOICES
        if hasattr(Organization, "ORGANIZATION_TYPE_CHOICES")
        else []
    )

    stats = {
        "total_organizations": organizations.count(),
        "active_organizations": organizations.filter(is_active=True).count(),
        "total_contacts": OrganizationContact.objects.count(),
        "by_type": organizations.values("organization_type").annotate(
            count=Count("id")
        ),
    }

    context = {
        "organizations": organizations,
        "org_types": org_types,
        "current_type": type_filter,
        "current_status": status_filter,
        "search_query": search_query,
        "stats": stats,
    }
    return render(request, "coordination/coordination_organizations.html", context)


@login_required
def organization_create(request):
    """Proxy to coordination frontend organization creation view."""

    return _organization_create(request)


@login_required
def organization_edit(request, organization_id):
    """Proxy to coordination frontend organization edit view."""

    return _organization_edit(request, organization_id=organization_id)


@login_required
def organization_detail(request, organization_id):
    """Expose the organization detail frontend view."""

    return _organization_detail(request, organization_id=organization_id)


@login_required
def organization_work_items_partial(request, organization_id):
    """Proxy to organization MOA work items partial view."""

    return _organization_work_items_partial(request, organization_id=organization_id)


@login_required
def organization_delete(request, organization_id):
    """Proxy to the organization delete confirmation flow."""

    return _organization_delete(request, organization_id=organization_id)


@login_required
def coordination_partnerships(request):
    """Manage coordination partnerships page."""
    from django.db.models import Count, Q

    from coordination.models import Organization, Partnership

    partnerships = (
        Partnership.objects.select_related("lead_organization")
        .prefetch_related("organizations")
        .annotate(signatories_count=Count("signatories"))
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status")
    type_filter = request.GET.get("type")
    search_query = request.GET.get("search")
    organization_filter = request.GET.get("organization")
    organization_instance = None

    if status_filter:
        partnerships = partnerships.filter(status=status_filter)

    if type_filter:
        partnerships = partnerships.filter(partnership_type=type_filter)

    if search_query:
        partnerships = partnerships.filter(
            Q(title__icontains=search_query)
            | Q(lead_organization__name__icontains=search_query)
            | Q(organizations__name__icontains=search_query)
            | Q(description__icontains=search_query)
        ).distinct()

    if organization_filter:
        organization_instance = get_organization(organization_filter)
        if organization_instance:
            partnerships = partnerships.filter(
                Q(lead_organization=organization_instance)
                | Q(organizations=organization_instance)
            ).distinct()

    status_choices = (
        Partnership.STATUS_CHOICES if hasattr(Partnership, "STATUS_CHOICES") else []
    )
    type_choices = (
        Partnership.PARTNERSHIP_TYPE_CHOICES
        if hasattr(Partnership, "PARTNERSHIP_TYPE_CHOICES")
        else []
    )

    stats = {
        "total_partnerships": partnerships.count(),
        "active_partnerships": partnerships.filter(status="active").count(),
        "pending_partnerships": partnerships.filter(
            status__in=["pending_approval", "pending_signature"]
        ).count(),
        "by_type": partnerships.values("partnership_type").annotate(count=Count("id")),
    }

    context = {
        "partnerships": partnerships,
        "status_choices": status_choices,
        "type_choices": type_choices,
        "current_status": status_filter,
        "current_type": type_filter,
        "search_query": search_query,
        "current_organization": organization_instance,
        "stats": stats,
    }
    return render(request, "coordination/coordination_partnerships.html", context)


@login_required
def partnership_create(request):
    """Proxy to coordination frontend partnership creation view."""

    return _partnership_create(request)


@login_required
def partnership_detail(request, partnership_id):
    """Proxy to frontend partnership detail view."""

    return _partnership_detail(request, partnership_id)


@login_required
def partnership_update(request, partnership_id):
    """Proxy to frontend partnership update view."""

    return _partnership_update(request, partnership_id)


@login_required
def partnership_delete(request, partnership_id):
    """Proxy to frontend partnership delete view."""

    return _partnership_delete(request, partnership_id)


@login_required
def event_create(request):
    """Create coordination event via WorkItem system."""
    from django.shortcuts import redirect
    # Events now use WorkItem with work_type='activity'
    # See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
    return redirect('common:work_item_create')


@login_required
def coordination_activity_create(request):
    """Proxy to coordination activity creation view."""

    return _engagement_create(request)


@login_required
def coordination_note_create(request):
    """Proxy to coordination note creation view."""

    return _coordination_note_create(request)


@login_required
def coordination_note_activity_options(request):
    """Proxy HTMX endpoint for coordination note activity filtering."""

    return _coordination_note_activity_options(request)


@login_required
def coordination_events(request):
    """Coordination management dashboard built on WorkItem activities."""
    from django.db.models import Count, Q
    from django.utils import timezone

    from common.work_item_model import WorkItem

    search_query = (request.GET.get("search") or "").strip()
    status_filter = (request.GET.get("status") or "").strip()
    type_filter = (request.GET.get("event_type") or request.GET.get("type") or "").strip()

    base_queryset = (
        WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_ACTIVITY)
        .filter(activity_category=WorkItem.ACTIVITY_CATEGORY_COORDINATION)
        .select_related("created_by")
        .prefetch_related("assignees", "teams")
    )

    # Build event type options before filters are applied so dropdown shows all choices
    type_options = sorted(
        {
            event_type
            for event_type in base_queryset.exclude(
                activity_data__event_type__isnull=True
            ).values_list("activity_data__event_type", flat=True)
            if event_type
        }
    )

    activities_qs = base_queryset

    if search_query:
        activities_qs = activities_qs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(activity_data__venue__icontains=search_query)
            | Q(activity_data__address__icontains=search_query)
        )

    if status_filter:
        activities_qs = activities_qs.filter(status=status_filter)

    if type_filter:
        activities_qs = activities_qs.filter(activity_data__event_type=type_filter)

    activities_qs = activities_qs.order_by("-start_date", "-created_at")
    activities = list(activities_qs)

    now = timezone.now().date()
    upcoming_activities = [
        activity
        for activity in activities
        if activity.start_date and activity.start_date >= now
    ]
    past_activities = [
        activity
        for activity in activities
        if activity.start_date and activity.start_date < now
    ]
    completed_count = sum(
        1 for activity in activities if activity.status == WorkItem.STATUS_COMPLETED
    )

    total_participants = 0
    for activity in activities:
        data = activity.activity_data or {}
        total_participants += (
            data.get("actual_participants")
            or data.get("expected_participants")
            or 0
        )

    stats = {
        "total_coordination": len(activities),
        "upcoming_coordination": len(upcoming_activities),
        "completed_coordination": completed_count,
        "total_participants": total_participants,
    }

    stat_cards = [
        {
            "label": "Total Coordination Activities",
            "icon": "fas fa-calendar-alt",
            "icon_color": "text-amber-600",
            "value": stats["total_coordination"],
        },
        {
            "label": "Completed",
            "icon": "fas fa-check-circle",
            "icon_color": "text-emerald-600",
            "value": stats["completed_coordination"],
        },
        {
            "label": "Upcoming",
            "icon": "fas fa-clock",
            "icon_color": "text-blue-600",
            "value": stats["upcoming_coordination"],
        },
        {
            "label": "Participants Logged",
            "icon": "fas fa-users",
            "icon_color": "text-purple-600",
            "value": stats["total_participants"],
        },
    ]

    quick_actions = [
        {
            "title": "Plan a Coordination Activity",
            "description": "Create a WorkItem activity with calendar-ready details.",
            "icon": "fas fa-calendar-plus",
            "icon_gradient": "from-blue-500 to-blue-600",
            "cta": "Plan Activity",
            "url": f"{reverse('common:work_item_create')}?work_type={WorkItem.WORK_TYPE_ACTIVITY}",
        },
        {
            "title": "Coordination Notes",
            "description": "Capture minutes, attendance, and partner highlights.",
            "icon": "fas fa-clipboard-list",
            "icon_gradient": "from-emerald-500 to-teal-500",
            "cta": "Record Notes",
            "url": reverse("coordination:note_add"),
        },
        {
            "title": "Coordination Insights",
            "description": "View comprehensive coordination metrics and reports.",
            "icon": "fas fa-chart-line",
            "icon_gradient": "from-orange-500 to-amber-500",
            "cta": "Open Dashboard",
            "url": reverse("coordination:view_all"),
        },
        {
            "title": "Calendar Management",
            "description": "Manage coordination schedules in the unified calendar.",
            "icon": "fas fa-calendar-week",
            "icon_gradient": "from-purple-500 to-indigo-500",
            "cta": "Manage Calendar",
            "url": reverse("common:oobc_calendar"),
        },
    ]

    calendar_feed_url = (
        f"{reverse('common:work_items_calendar_feed')}?type=activity"
        f"&activity_category={WorkItem.ACTIVITY_CATEGORY_COORDINATION}"
    )

    root_queryset = (
        activities_qs.annotate(children_count=Count("children")).order_by("tree_id", "lft")
    )

    activities_tree_html = render_to_string(
        "work_items/partials/tree_wrapper.html",
        {
            "work_items": root_queryset,
            "tree_title": "Coordination Activities",
            "items_display_label": "coordination activities",
            "show_add_button": False,
            "create_button_label": "Add Coordination Activity",
            "empty_state_title": "No coordination activities found",
            "empty_state_description": "Plan a coordination activity to populate this list.",
            "work_item_create_url": f"{reverse('common:work_item_sidebar_create')}?work_type={WorkItem.WORK_TYPE_ACTIVITY}",
        },
        request=request,
    )

    calendar_fetch_url = calendar_feed_url

    context = {
        "activities": activities,
        "upcoming_activities": upcoming_activities[:10],
        "past_activities": past_activities[:10],
        "status_choices": WorkItem.STATUS_CHOICES,
        "event_type_options": type_options,
        "current_status": status_filter,
        "current_type": type_filter,
        "search_query": search_query,
        "stats": stats,
        "stat_cards": stat_cards,
        "upcoming_coordination_count": stats["upcoming_coordination"],
        "completed_coordination_count": stats["completed_coordination"],
        "total_coordination_count": stats["total_coordination"],
        "total_participants_count": stats["total_participants"],
        "quick_actions": quick_actions,
        "activities_tree_html": activities_tree_html,
        "calendar_fetch_url": calendar_fetch_url,
    }
    return render(request, "coordination/coordination_events.html", context)


@login_required
def coordination_calendar(request):
    """Coordination calendar view - redirects to main calendar."""
    from django.shortcuts import redirect
    return redirect('common:oobc_calendar')


@login_required
def coordination_view_all(request):
    """Coordination overview and reports page."""
    from datetime import timedelta

    from django.db.models import Count
    from django.utils import timezone

    from coordination.models import Organization, Partnership
    from common.work_item_model import WorkItem

    # WorkItem activities (replaced Event model)
    activities = WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_ACTIVITY)
    partnerships = Partnership.objects.select_related("lead_organization")
    organizations = Organization.objects.filter(is_active=True)

    now = timezone.now()
    last_30_days = now.date() - timedelta(days=30)

    # Count event types from activity_data JSON field
    event_type_counts = {}
    for activity in activities:
        event_type = (activity.activity_data or {}).get("event_type")
        if event_type:
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

    stats = {
        "organizations": {
            "total": organizations.count(),
            "by_type": organizations.values("organization_type").annotate(
                count=Count("id")
            )[:5],
        },
        "partnerships": {
            "total": partnerships.count(),
            "active": partnerships.filter(status="active").count(),
            "recent": partnerships.filter(created_at__gte=last_30_days).count(),
            "by_status": partnerships.values("status").annotate(count=Count("id")),
        },
        "events": {
            "total": activities.count(),
            "upcoming": activities.filter(start_date__gte=now.date()).count(),
            "recent": activities.filter(created_at__gte=last_30_days).count(),
            "by_type": [{"event_type": k, "count": v} for k, v in list(event_type_counts.items())[:5]],
        },
    }

    recent_events = activities.order_by("-created_at")[:5]
    recent_partnerships = partnerships.order_by("-created_at")[:5]

    context = {
        "stats": stats,
        "recent_events": recent_events,
        "recent_partnerships": recent_partnerships,
        "organizations": organizations[:10],
    }
    return render(request, "coordination/coordination_view_all.html", context)


__all__ = [
    "coordination_home",
    "coordination_organizations",
    "coordination_partnerships",
    "partnership_create",
    "partnership_detail",
    "partnership_update",
    "partnership_delete",
    "organization_work_items_partial",
    "coordination_events",
    "coordination_view_all",
]
