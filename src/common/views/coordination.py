"""Views for coordination module dashboards and listings."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from coordination.views import (
    engagement_create as _engagement_create,
    organization_create as _organization_create,
    organization_delete as _organization_delete,
    organization_detail as _organization_detail,
    organization_edit as _organization_edit,
    partnership_create as _partnership_create,
    partnership_delete as _partnership_delete,
    partnership_detail as _partnership_detail,
    partnership_update as _partnership_update,
)

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
        return redirect("common:page_restricted")

    from datetime import timedelta

    from django.db.models import Count, Q
    from django.utils import timezone

    from coordination.models import (
        Event,
        EventParticipant,
        Organization,
        Partnership,
        PartnershipSignatory,
        StakeholderEngagement,
    )

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

    completed_events = Event.objects.filter(status="completed")
    completed_engagements = StakeholderEngagement.objects.filter(status="completed")

    total_completed_activities = (
        completed_events.count() + completed_engagements.count()
    )

    bmoa_events = (
        completed_events.filter(participants__organization__organization_type="bmoa")
        .distinct()
        .count()
    )
    nga_events = (
        completed_events.filter(participants__organization__organization_type="nga")
        .distinct()
        .count()
    )
    lgu_events = (
        completed_events.filter(participants__organization__organization_type="lgu")
        .distinct()
        .count()
    )

    coordination_activities_done_stats = {
        "total": total_completed_activities,
        "bmoa": bmoa_events,
        "nga": nga_events,
        "lgu": lgu_events,
    }

    planned_events = Event.objects.filter(
        status__in=["planned", "scheduled"], start_date__gte=now.date()
    )
    planned_engagements = StakeholderEngagement.objects.filter(
        status__in=["planned", "scheduled"], planned_date__gte=now
    )

    total_planned_activities = planned_events.count() + planned_engagements.count()

    bmoa_planned = (
        planned_events.filter(participants__organization__organization_type="bmoa")
        .distinct()
        .count()
    )
    nga_planned = (
        planned_events.filter(participants__organization__organization_type="nga")
        .distinct()
        .count()
    )
    lgu_planned = (
        planned_events.filter(participants__organization__organization_type="lgu")
        .distinct()
        .count()
    )

    planned_coordination_activities_stats = {
        "total": total_planned_activities,
        "bmoa": bmoa_planned,
        "nga": nga_planned,
        "lgu": lgu_planned,
    }

    recent_events = Event.objects.order_by("-updated_at", "-created_at")[:10]

    event_by_type = {
        "meeting": Event.objects.filter(event_type="meeting").count(),
        "workshop": Event.objects.filter(event_type="workshop").count(),
        "conference": Event.objects.filter(event_type="conference").count(),
        "consultation": Event.objects.filter(event_type="consultation").count(),
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
        try:
            organization_instance = Organization.objects.get(pk=organization_filter)
        except (Organization.DoesNotExist, ValueError, TypeError):
            organization_instance = None

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
def coordination_events(request):
    """Coordination management dashboard."""
    from django.db.models import Count
    from django.utils import timezone

    from coordination.models import Event, EventParticipant
    from project_central.models import ProjectWorkflow

    events = (
        Event.objects.select_related("community", "organizer", "related_project")
        .prefetch_related("staff_tasks")
        .annotate(participants_count=Count("participants"))
        .order_by("-start_date")
    )

    status_filter = request.GET.get("status")
    type_filter = request.GET.get("type")
    project_filter = request.GET.get("project")
    is_project_activity_filter = request.GET.get("is_project_activity")

    if status_filter:
        events = events.filter(status=status_filter)

    if type_filter:
        events = events.filter(event_type=type_filter)

    # Project-related filters
    if project_filter:
        try:
            project_id = int(project_filter)
            events = events.filter(related_project_id=project_id)
        except (TypeError, ValueError):
            pass

    if is_project_activity_filter:
        if is_project_activity_filter.lower() == "true":
            events = events.filter(is_project_activity=True)
        elif is_project_activity_filter.lower() == "false":
            events = events.filter(is_project_activity=False)

    status_choices = Event.STATUS_CHOICES if hasattr(Event, "STATUS_CHOICES") else []
    type_choices = (
        Event.EVENT_TYPE_CHOICES if hasattr(Event, "EVENT_TYPE_CHOICES") else []
    )

    now = timezone.now().date()
    upcoming_events = events.filter(start_date__gte=now)
    past_events = events.filter(start_date__lt=now)
    completed_events_count = events.filter(status="completed").count()

    stats = {
        "total_coordination": events.count(),
        "upcoming_coordination": upcoming_events.count(),
        "completed_coordination": completed_events_count,
        "total_participants": EventParticipant.objects.count(),
    }

    # Get projects with events for filter dropdown
    project_options = (
        ProjectWorkflow.objects.filter(events__isnull=False)
        .annotate(event_count=Count("events"))
        .order_by("-event_count", "title")
        .distinct()
    )

    context = {
        "events": events,
        "upcoming_events": upcoming_events[:10],
        "past_events": past_events[:10],
        "status_choices": status_choices,
        "type_choices": type_choices,
        "current_status": status_filter,
        "current_type": type_filter,
        "current_project": project_filter,
        "current_is_project_activity": is_project_activity_filter,
        "project_options": project_options,
        "stats": stats,
        "upcoming_coordination_count": stats["upcoming_coordination"],
        "completed_coordination_count": stats["completed_coordination"],
        "total_coordination_count": stats["total_coordination"],
        "total_participants_count": stats["total_participants"],
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

    from coordination.models import Event, Organization, Partnership

    events = Event.objects.select_related("community", "organizer")
    partnerships = Partnership.objects.select_related("lead_organization")
    organizations = Organization.objects.filter(is_active=True)

    now = timezone.now()
    last_30_days = now.date() - timedelta(days=30)

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
            "total": events.count(),
            "upcoming": events.filter(start_date__gte=now.date()).count(),
            "recent": events.filter(start_date__gte=last_30_days).count(),
            "by_type": events.values("event_type").annotate(count=Count("id"))[:5],
        },
    }

    recent_events = events.order_by("-created_at")[:5]
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
    "coordination_events",
    "coordination_view_all",
]
