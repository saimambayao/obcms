"""Views for Monitoring & Evaluation dashboard and detail pages."""

from collections import defaultdict
from decimal import Decimal
import csv
import json
import logging
from datetime import datetime, timedelta
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Max, Q, Sum
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from common.utils.moa_permissions import moa_can_edit_ppa

from common.services.locations import build_location_data, get_object_centroid
from communities.models import OBCCommunity
from common.models import Municipality
from common.work_item_model import WorkItem
from coordination.models import Organization
from .forms import (
    MonitoringMOAEntryForm,
    MonitoringOOBCEntryForm,
    MonitoringRequestEntryForm,
    MonitoringUpdateForm,
    MonitoringOBCQuickCreateForm,
)
from .models import MonitoringEntry, MonitoringUpdate
from .services import BudgetDistributionService, build_moa_budget_tracking


logger = logging.getLogger(__name__)


def _normalise_float(value):
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _prefetch_entries():
    """Return a queryset with the relations needed across views."""
    # Use custom manager's with_related() for optimal performance
    return MonitoringEntry.objects.with_related()


def _build_workitem_context(entry):
    """
    Assemble context data for the Work Items tab.

    Returns metrics even when tracking is disabled so the template stays stable.
    """
    default_stats = {
        "total_budget_allocated": Decimal("0.00"),
        "total_work_items": 0,
        "avg_progress": 0,
        "budget_variance_pct": 0.0,
        "unallocated_budget": Decimal("0.00"),
    }
    context = {
        "work_items": None,
        "budget_summary": None,
        "progress_by_type": {},
        "workitem_stats": default_stats,
    }

    execution_project = getattr(entry, "execution_project", None)
    if not execution_project:
        return context

    descendants = entry.work_items.all()
    child_items = descendants.exclude(work_type=WorkItem.WORK_TYPE_PROJECT)

    total_budget_allocated = (
        child_items.aggregate(total=Sum("allocated_budget"))["total"]
        or Decimal("0.00")
    )
    total_budget_allocated = Decimal(str(total_budget_allocated))

    budget = entry.budget_allocation or Decimal("0.00")
    budget = Decimal(str(budget))
    unallocated_budget = budget - total_budget_allocated

    variance_pct = 0.0
    if budget != Decimal("0.00"):
        variance_pct = float(
            ((total_budget_allocated - budget) / budget) * Decimal("100.0")
        )

    average_progress = descendants.aggregate(avg=Avg("progress"))["avg"]
    if average_progress is None:
        average_progress_value = 0
    else:
        average_progress_value = int(round(float(average_progress)))

    progress_by_type = {}
    for work_type_key, work_type_label in WorkItem.WORK_TYPE_CHOICES:
        items_of_type = descendants.filter(work_type=work_type_key)
        if items_of_type.exists():
            avg_value = items_of_type.aggregate(avg=Avg("progress"))["avg"] or 0
            progress_by_type[work_type_label] = {
                "count": items_of_type.count(),
                "avg_progress": round(float(avg_value), 1),
            }

    # Get only root-level work items (immediate children of execution_project)
    # The tree template will recursively load descendants via HTMX
    root_work_items = execution_project.get_children().select_related("created_by")

    context.update(
        {
            "work_items": root_work_items,
            "budget_summary": {
                "total": budget,
                "allocated": total_budget_allocated,
                "remaining": unallocated_budget,
            },
            "progress_by_type": progress_by_type,
            "workitem_stats": {
                "total_budget_allocated": total_budget_allocated,
                "total_work_items": descendants.count(),
                "avg_progress": average_progress_value,
                "budget_variance_pct": variance_pct,
                "unallocated_budget": unallocated_budget,
            },
        }
    )
    return context


def _render_workitems_tab(request, entry, *, status=200, triggers=None):
    """Render the Work Items tab partial with refreshed context."""
    context = {"entry": entry}
    context.update(_build_workitem_context(entry))

    response = render(
        request,
        "monitoring/partials/work_items_tab.html",
        context,
        status=status,
    )
    if triggers:
        response["HX-Trigger"] = json.dumps(triggers)
    return response


@login_required
def work_items_summary_partial(request, pk):
    """
    HTMX endpoint: return refreshed Work Items summary metrics.

    Used to update the stat cards and budget overview without reloading the tab.
    """
    entry = get_object_or_404(_prefetch_entries(), pk=pk)

    if not getattr(entry, "execution_project", None):
        return HttpResponse(status=204)

    context = {"entry": entry}
    context.update(_build_workitem_context(entry))
    return render(
        request,
        "monitoring/partials/work_items_summary.html",
        context,
    )


@login_required
def monitoring_dashboard(request):
    """Render the consolidated Monitoring & Evaluation workspace."""
    # Restrict access for MANA participants
    user = request.user
    if (
        not user.is_staff
        and not user.is_superuser
        and user.has_perm("mana.can_access_regional_mana")
        and not user.has_perm("mana.can_facilitate_workshop")
    ):
        return redirect("common:page_restricted")

    entries = _prefetch_entries()
    base_queryset = MonitoringEntry.objects.all()
    current_year = timezone.now().year

    def filter_for_year(queryset):
        return queryset.filter(
            Q(start_date__year=current_year)
            | Q(start_date__isnull=True, created_at__year=current_year)
        )

    moa_year_qs = filter_for_year(base_queryset.filter(category="moa_ppa"))
    oobc_year_qs = filter_for_year(base_queryset.filter(category="oobc_ppa"))
    request_year_qs = filter_for_year(base_queryset.filter(category="obc_request"))

    moa_stats = {
        "title": "MOA PPAs",
        "subtitle": f"{current_year} Overview",
        "icon": "fas fa-building-columns",
        "icon_color": "text-blue-600",
        "gradient": "from-blue-500 via-blue-600 to-blue-700",
        "total": moa_year_qs.count(),
        "metrics": [
            {
                "label": "Completed",
                "value": moa_year_qs.filter(status="completed").count(),
            },
            {
                "label": "Ongoing",
                "value": moa_year_qs.filter(status__in=["ongoing", "on_hold"]).count(),
            },
            {
                "label": "Not Started",
                "value": moa_year_qs.filter(status__in=["planning"]).count(),
            },
        ],
    }

    oobc_stats = {
        "title": "OOBC Initiatives",
        "subtitle": f"{current_year} Overview",
        "icon": "fas fa-hand-holding-heart",
        "icon_color": "text-emerald-600",
        "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
        "total": oobc_year_qs.count(),
        "metrics": [
            {
                "label": "Completed",
                "value": oobc_year_qs.filter(status="completed").count(),
            },
            {
                "label": "Ongoing",
                "value": oobc_year_qs.filter(status__in=["ongoing", "on_hold"]).count(),
            },
            {
                "label": "Not Started",
                "value": oobc_year_qs.filter(status__in=["planning"]).count(),
            },
        ],
    }

    request_on_process_statuses = [
        "under_review",
        "clarification",
        "endorsed",
        "approved",
        "in_progress",
    ]

    request_stats = {
        "title": "OBC Requests / Proposals",
        "subtitle": f"{current_year} Overview",
        "icon": "fas fa-file-signature",
        "icon_color": "text-purple-600",
        "gradient": "from-cyan-500 via-sky-500 to-indigo-500",
        "total": request_year_qs.count(),
        "metrics": [
            {
                "label": "Completed",
                "value": request_year_qs.filter(request_status="completed").count(),
            },
            {
                "label": "On Process",
                "value": request_year_qs.filter(
                    request_status__in=request_on_process_statuses
                ).count(),
            },
            {
                "label": "Not Started",
                "value": request_year_qs.filter(
                    Q(request_status="submitted")
                    | Q(request_status="")
                    | Q(request_status__isnull=True)
                ).count(),
            },
        ],
    }

    stats_cards = [moa_stats, oobc_stats, request_stats]

    recent_moa_entries = entries.filter(category="moa_ppa").order_by(
        "-updated_at", "-created_at"
    )[:10]
    recent_oobc_entries = entries.filter(category="oobc_ppa").order_by(
        "-updated_at", "-created_at"
    )[:10]
    recent_request_entries = entries.filter(category="obc_request").order_by(
        "-updated_at", "-created_at"
    )[:10]

    grouped_entries = defaultdict(list)
    for entry in entries:
        grouped_entries[entry.category].append(entry)

    raw_category_summary = (
        entries.order_by()
        .values("category")
        .annotate(
            total=Count("id"),
            completed=Count("id", filter=Q(status="completed")),
        )
    )

    raw_status_breakdown = (
        entries.order_by()
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    linked_counts = {
        "mana_assessments": entries.filter(related_assessment__isnull=False).count(),
        "coordination_events": WorkItem.objects.filter(
            related_ppa__in=entries,
            work_type__in=[
                WorkItem.WORK_TYPE_ACTIVITY,
                WorkItem.WORK_TYPE_SUB_ACTIVITY,
            ],
        )
        .distinct()
        .count(),
        "policy_recommendations": entries.filter(related_policy__isnull=False).count(),
    }

    progress_snapshot = entries.aggregate(
        avg_progress=Avg("progress"),
        latest_update=Max("updated_at"),
    )

    pending_requests = entries.filter(
        category="obc_request",
        request_status__in=["submitted", *request_on_process_statuses],
    ).count()

    category_labels = dict(MonitoringEntry.CATEGORY_CHOICES)
    status_labels = dict(MonitoringEntry.STATUS_CHOICES)
    request_status_labels = dict(MonitoringEntry.REQUEST_STATUS_CHOICES)

    category_order = {
        key: index
        for index, (key, _label) in enumerate(MonitoringEntry.CATEGORY_CHOICES)
    }

    category_summary = [
        {
            "key": item["category"],
            "label": category_labels.get(item["category"], item["category"]),
            "total": item["total"],
            "completed": item["completed"],
        }
        for item in raw_category_summary
    ]
    status_breakdown = [
        {
            "key": item["status"],
            "label": status_labels.get(item["status"], item["status"]),
            "total": item["total"],
        }
        for item in raw_status_breakdown
    ]
    request_breakdown = [
        {
            "key": item["request_status"],
            "label": request_status_labels.get(
                item["request_status"], item["request_status"]
            ),
            "total": item["total"],
        }
        for item in (
            entries.filter(category="obc_request")
            .order_by()
            .values("request_status")
            .annotate(total=Count("id"))
            .order_by("request_status")
        )
    ]

    category_sections = [
        {
            "key": key,
            "label": category_labels.get(key, key),
            "entries": value,
        }
        for key, value in grouped_entries.items()
    ]

    category_summary.sort(key=lambda item: category_order.get(item["key"], 99))
    category_sections.sort(key=lambda item: category_order.get(item["key"], 99))

    quick_actions = [
        {
            "title": "Log MOA PPA",
            "description": "Document MOA-led projects accessible to OBC communities.",
            "icon": "fas fa-building-columns",
            "color": "bg-blue-500",
            "url": reverse("monitoring:create_moa"),
        },
        {
            "title": "Log OOBC Initiative",
            "description": "Capture OOBC-led programmes supporting partner communities.",
            "icon": "fas fa-hand-holding-heart",
            "color": "bg-emerald-500",
            "url": reverse("monitoring:create_oobc"),
        },
        {
            "title": "Submit OBC Request",
            "description": "Track requests and proposals submitted by OBC partners.",
            "icon": "fas fa-file-signature",
            "color": "bg-indigo-500",
            "url": reverse("monitoring:create_request"),
        },
    ]

    context = {
        "stats_cards": stats_cards,
        "quick_actions": quick_actions,
        "entries": entries,
        "recent_feeds": {
            "moa": recent_moa_entries,
            "oobc": recent_oobc_entries,
            "requests": recent_request_entries,
        },
        "category_sections": category_sections,
        "category_summary": category_summary,
        "status_breakdown": status_breakdown,
        "request_breakdown": request_breakdown,
        "linked_counts": linked_counts,
        "progress_snapshot": progress_snapshot,
        "pending_requests": pending_requests,
        "category_labels": category_labels,
        "status_labels": status_labels,
        "request_status_labels": request_status_labels,
    }
    return render(request, "monitoring/dashboard.html", context)


@login_required
def monitoring_entry_detail(request, pk):
    """Display a monitoring entry with recent updates and linked data."""

    entry = get_object_or_404(_prefetch_entries(), pk=pk)
    update_form = MonitoringUpdateForm()

    if request.method == "POST" and request.POST.get("action") == "add_update":
        update_form = MonitoringUpdateForm(request.POST)
        if update_form.is_valid():
            update = update_form.save(commit=False)
            update.entry = entry
            update.created_by = request.user
            update.save()

            if update.status:
                entry.status = update.status
            if update.request_status:
                entry.request_status = update.request_status
            if update.progress is not None:
                entry.progress = update.progress
            entry.last_status_update = update.follow_up_date or timezone.now().date()
            entry.updated_by = request.user
            entry.save()

            messages.success(request, "Update logged successfully.")
            return redirect("monitoring:detail", pk=entry.pk)
        messages.error(
            request,
            "Unable to record the update. Please review the highlighted fields.",
        )

    related_entries = (
        MonitoringEntry.objects.filter(communities__in=entry.communities.all())
        .exclude(pk=entry.pk)
        .distinct()
        .select_related("lead_organization")
    )

    support_raw = (entry.support_required or "").strip()
    special_provision_text = ""
    support_text_clean = support_raw

    if support_text_clean.lower().startswith("special provision"):
        _, _, after_label = support_text_clean.partition(":")
        provision_block = after_label.lstrip()
        additional_support = ""
        if "\n\n" in provision_block:
            provision_block, additional_support = provision_block.split("\n\n", 1)
        special_provision_text = provision_block.strip()
        support_text_clean = additional_support.strip()

    workitem_context = _build_workitem_context(entry)

    budget_context = {
        "moa_ppas": [],
        "moa_budget_stats": {
            "total_budget": Decimal("0.00"),
            "total_allocated": Decimal("0.00"),
            "total_expenditure": Decimal("0.00"),
            "utilization_rate": 0.0,
            "total_variance": Decimal("0.00"),
        },
    }
    if entry.category == "moa_ppa" and entry.implementing_moa:
        moa_ppas_queryset = (
            MonitoringEntry.objects.filter(
                category="moa_ppa",
                implementing_moa=entry.implementing_moa,
            )
            .select_related("implementing_moa")
            .order_by("-updated_at")
        )
        budget_context = build_moa_budget_tracking(
            entry.implementing_moa,
            moa_ppas_queryset,
        )

    context = {
        "entry": entry,
        "updates": entry.updates.select_related("created_by"),
        "update_form": update_form,
        "related_entries": related_entries,
        "special_provision_text": special_provision_text,
        "support_text_clean": support_text_clean,
    }
    context.update(workitem_context)
    context.update(budget_context)
    return render(request, "monitoring/detail.html", context)


@login_required
def create_moa_entry(request):
    """Create view for MOA PPAs."""

    form = MonitoringMOAEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.created_by = request.user
        entry.updated_by = request.user
        entry.save()
        form.save_m2m()
        form._post_save(entry)
        messages.success(request, "MOA PPA logged successfully.")
        return redirect("monitoring:detail", pk=entry.pk)

    community_locations = []
    community_queryset = (
        OBCCommunity.objects.filter(is_active=True)
        .select_related("barangay__municipality__province__region")
        .order_by(
            "barangay__municipality__province__region__code",
            "barangay__municipality__name",
            "barangay__name",
        )
    )

    for community in community_queryset:
        barangay = community.barangay
        municipality = barangay.municipality if barangay else None
        province = municipality.province if municipality else None
        region = province.region if province else None

        latitude = _normalise_float(community.latitude)
        longitude = _normalise_float(community.longitude)

        if latitude is None or longitude is None:
            latitude, longitude = get_object_centroid(barangay)

        if (latitude is None or longitude is None) and municipality is not None:
            latitude, longitude = get_object_centroid(municipality)

        if (latitude is None or longitude is None) and province is not None:
            latitude, longitude = get_object_centroid(province)

        if (latitude is None or longitude is None) and region is not None:
            latitude, longitude = get_object_centroid(region)

        has_location = latitude is not None and longitude is not None

        community_locations.append(
            {
                "id": str(community.pk),
                "type": "community",
                "name": community.display_name
                or (barangay.name if barangay else "OBC"),
                "latitude": latitude,
                "longitude": longitude,
                "barangay_id": str(barangay.pk) if barangay else None,
                "barangay_name": barangay.name if barangay else "",
                "municipality_id": str(municipality.pk) if municipality else None,
                "municipality_name": municipality.name if municipality else "",
                "province_id": str(province.pk) if province else None,
                "province_name": province.name if province else "",
                "region_id": str(region.pk) if region else None,
                "region_name": region.name if region else "",
                "full_path": getattr(barangay, "full_path", ""),
                "has_location": has_location,
            }
        )

    municipalties = (
        Municipality.objects.filter(is_active=True)
        .select_related("province__region")
        .order_by("province__region__name", "province__name", "name")
    )

    for municipality in municipalties:
        province = municipality.province
        region = province.region if province else None

        latitude, longitude = get_object_centroid(municipality)
        has_location = latitude is not None and longitude is not None

        full_path_parts = [municipality.name]
        if province:
            full_path_parts.append(province.name)
        community_locations.append(
            {
                "id": f"municipality-{municipality.pk}",
                "type": "municipality",
                "name": municipality.name,
                "latitude": latitude,
                "longitude": longitude,
                "barangay_id": None,
                "barangay_name": "",
                "municipality_id": str(municipality.pk),
                "municipality_name": municipality.name,
                "province_id": str(province.pk) if province else None,
                "province_name": province.name if province else "",
                "region_id": str(region.pk) if region else None,
                "region_name": region.name if region else "",
                "full_path": ", ".join(full_path_parts),
                "has_location": has_location,
            }
        )

    return render(
        request,
        "monitoring/create_moa.html",
        {
            "form": form,
            "location_data": build_location_data(include_barangays=True),
            "community_locations": community_locations,
        },
    )


@login_required
@require_POST
def ajax_create_obc(request):
    """Handle inline creation of OBC communities from the MOA form."""

    obc_form = MonitoringOBCQuickCreateForm(request.POST)
    if obc_form.is_valid():
        community = obc_form.save()

        barangay = community.barangay
        municipality = barangay.municipality
        province = municipality.province
        region = province.region

        return JsonResponse(
            {
                "success": True,
                "community": {
                    "id": str(community.id),
                    "name": community.display_name,
                    "barangay": barangay.name,
                    "municipality": municipality.name,
                    "province": province.name,
                    "region": region.name,
                },
            }
        )

    error_payload = {
        field: [str(message) for message in messages]
        for field, messages in obc_form.errors.items()
    }
    return JsonResponse({"success": False, "errors": error_payload}, status=400)


@login_required
def create_oobc_entry(request):
    """Create view for OOBC initiatives."""

    form = MonitoringOOBCEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.created_by = request.user
        entry.updated_by = request.user
        entry.save()
        form.save_m2m()
        form._post_save(entry)
        messages.success(request, "OOBC initiative recorded successfully.")
        return redirect("monitoring:detail", pk=entry.pk)

    return render(
        request,
        "monitoring/create_oobc.html",
        {
            "form": form,
        },
    )


@login_required
def create_request_entry(request):
    """Create view for OBC requests and proposals."""

    form = MonitoringRequestEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.created_by = request.user
        entry.updated_by = request.user
        entry.save()
        form.save_m2m()
        form._post_save(entry)
        messages.success(request, "OBC request submitted successfully.")
        return redirect("monitoring:detail", pk=entry.pk)

    return render(
        request,
        "monitoring/create_request.html",
        {
            "form": form,
        },
    )


@login_required
def moa_ppas_dashboard(request):
    """Dedicated dashboard for MOA PPAs (Ministries, Offices, and Agencies Programs, Projects, and Activities)."""

    all_moa_entries = _prefetch_entries().filter(category="moa_ppa")
    current_year = timezone.now().year

    status_filter = request.GET.get("status", "").strip()
    moa_filter = request.GET.get("implementing_moa", "").strip()
    fiscal_year_filter = request.GET.get("fiscal_year", "").strip()
    search_query = request.GET.get("q", "").strip()

    filtered_entries = all_moa_entries

    if request.user.is_authenticated and request.user.is_moa_staff:
        user_moa = getattr(request.user, "moa_organization", None)
        if user_moa:
            all_moa_entries = all_moa_entries.filter(implementing_moa=user_moa)
            filtered_entries = all_moa_entries
            moa_filter = str(user_moa.pk)
        else:
            all_moa_entries = all_moa_entries.none()
            filtered_entries = all_moa_entries

    if status_filter:
        filtered_entries = filtered_entries.filter(status=status_filter)

    if moa_filter:
        try:
            filtered_entries = filtered_entries.filter(implementing_moa__id=moa_filter)
        except (TypeError, ValueError):
            filtered_entries = filtered_entries.none()

    if fiscal_year_filter:
        filtered_entries = filtered_entries.filter(fiscal_year=fiscal_year_filter)

    if search_query:
        filtered_entries = filtered_entries.filter(
            Q(title__icontains=search_query)
            | Q(summary__icontains=search_query)
            | Q(implementing_moa__name__icontains=search_query)
        )

    # Filter for current year entries (based on filtered queryset)
    moa_year_qs = filtered_entries.filter(
        Q(start_date__year=current_year)
        | Q(start_date__isnull=True, created_at__year=current_year)
    )

    # Statistics cards
    total_moa_ppas = filtered_entries.count()
    total_budget = filtered_entries.aggregate(
        total=Sum("budget_allocation"), obc_total=Sum("budget_obc_allocation")
    )

    # Geographic coverage
    geographic_coverage = {
        "regions": filtered_entries.exclude(coverage_region__isnull=True)
        .values("coverage_region__name")
        .distinct()
        .count(),
        "provinces": filtered_entries.exclude(coverage_province__isnull=True)
        .values("coverage_province__name")
        .distinct()
        .count(),
        "municipalities": filtered_entries.exclude(coverage_municipality__isnull=True)
        .values("coverage_municipality__name")
        .distinct()
        .count(),
    }

    implementing_moa_qs = filtered_entries.exclude(implementing_moa__isnull=True)
    total_moa_orgs = implementing_moa_qs.values("implementing_moa").distinct().count()
    ministry_moa_count = (
        implementing_moa_qs.filter(
            Q(implementing_moa__name__istartswith="Ministry")
            | Q(implementing_moa__name__iexact="Office of the Chief Minister")
        )
        .values("implementing_moa")
        .distinct()
        .count()
    )
    other_exec_moa_count = max(total_moa_orgs - ministry_moa_count, 0)

    stats_cards = [
        {
            "title": "Total MOAs",
            "subtitle": f"Implementing Partners",
            "icon": "fas fa-sitemap",
            "icon_color": "text-sky-600",
            "gradient": "from-sky-500 via-sky-600 to-sky-700",
            "total": total_moa_orgs,
            "metric_columns": "grid-cols-2",
            "metrics": [
                {"label": "Ministries", "value": ministry_moa_count},
                {
                    "label": "Other Exec Offices",
                    "value": other_exec_moa_count,
                },
            ],
        },
        {
            "title": "Total MOA PPAs",
            "subtitle": f"Active Programs & Projects",
            "icon": "fas fa-building-columns",
            "icon_color": "text-amber-600",  # Total/General

            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "total": total_moa_ppas,
            "metrics": [
                {
                    "label": "Completed",
                    "value": filtered_entries.filter(status="completed").count(),
                },
                {
                    "label": "Ongoing",
                    "value": filtered_entries.filter(status="ongoing").count(),
                },
                {
                    "label": "Planning",
                    "value": filtered_entries.filter(status="planning").count(),
                },
            ],
        },
        {
            "title": "Budget Allocation",
            "subtitle": f"Total & OBC-Specific (PHP)",
            "icon": "fas fa-peso-sign",
            "icon_color": "text-emerald-600",  # Success/Financial
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "total": f"₱{total_budget['total'] or 0:,.0f}",
            "metrics": [
                {
                    "label": "OBC Budget",
                    "value": f"₱{total_budget['obc_total'] or 0:,.0f}",
                },
                {
                    "label": "With Budget",
                    "value": filtered_entries.exclude(
                        budget_allocation__isnull=True
                    ).count(),
                },
                {
                    "label": "Pending",
                    "value": filtered_entries.filter(budget_allocation__isnull=True).count(),
                },
            ],
        },
        {
            "title": "Geographic Coverage",
            "subtitle": f"Implementation Areas",
            "icon": "fas fa-map-marked-alt",
            "icon_color": "text-purple-600",  # Info/Geographic
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "total": geographic_coverage["regions"],
            "metrics": [
                {"label": "Regions", "value": geographic_coverage["regions"]},
                {"label": "Provinces", "value": geographic_coverage["provinces"]},
                {
                    "label": "Municipalities",
                    "value": geographic_coverage["municipalities"]},
            ],
        },
    ]

    # Quick actions specific to MOA PPAs
    quick_actions = [
        {
            "title": "Add New MOA PPA",
            "description": "Register a new MOA-led program or project.",
            "icon": "fas fa-plus-circle",
            "color": "bg-blue-500",
            "url": reverse("monitoring:create_moa"),
        },
        {
            "title": "Import MOA Data",
            "description": "Import multiple MOA PPAs from Excel or CSV.",
            "icon": "fas fa-file-import",
            "color": "bg-green-500",
            "url": reverse("monitoring:import_moa_data"),
        },
        {
            "title": "Generate Report",
            "description": "Create comprehensive MOA PPAs report.",
            "icon": "fas fa-chart-line",
            "color": "bg-purple-500",
            "url": reverse("monitoring:generate_moa_report"),
        },
        {
            "title": "Export Data",
            "description": "Export MOA PPAs data to Excel or CSV.",
            "icon": "fas fa-download",
            "color": "bg-indigo-500",
            "url": reverse("monitoring:export_moa_data"),
        },
        {
            "title": "Bulk Update Status",
            "description": "Update multiple MOA PPAs status at once.",
            "icon": "fas fa-edit",
            "color": "bg-orange-500",
            "url": reverse("monitoring:bulk_update_moa_status"),
        },
        {
            "title": "Schedule Review",
            "description": "Schedule coordination meeting for MOA PPAs.",
            "icon": "fas fa-calendar-plus",
            "color": "bg-teal-500",
            "url": reverse("monitoring:schedule_moa_review"),
        },
    ]

    # Status breakdown
    status_breakdown = [
        {
            "key": item["status"],
            "label": dict(MonitoringEntry.STATUS_CHOICES).get(
                item["status"], item["status"]
            ),
            "total": item["total"],
        }
        for item in (
            filtered_entries.order_by()
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )
    ]

    # Progress snapshot
    progress_snapshot = filtered_entries.aggregate(
        avg_progress=Avg("progress"),
        latest_update=Max("updated_at"),
    )

    hero_config = {
        "badge_icon": "fas fa-building-columns",
        "badge_text": f"MOA Programs · {current_year}",
        "title": "MOA PPAs Management",
        "title_suffix": "",
        "subtitle": (
            "Monitor BARMM ministries, offices, and agencies initiatives that benefit "
            "Bangsamoro communities outside the region."
        ),
        "extra_chips": [],
        "contacts": [],
        "overview": {
            "entries_label": "MOA PPAs tracked",
            "budget_label": "Total budget",
        },
    }

    selected_moa_details = None
    if moa_filter:
        selected_moa_details = Organization.objects.filter(pk=moa_filter).first()

        if selected_moa_details:
            subtitle_source = next(
                (
                    value.strip()
                    for value in [
                        selected_moa_details.description or "",
                        selected_moa_details.mandate or "",
                        selected_moa_details.target_beneficiaries or "",
                        selected_moa_details.geographic_coverage or "",
                    ]
                    if value and value.strip()
                ),
                hero_config["subtitle"],
            )

            acronym = (selected_moa_details.acronym or "").strip()
            name_normalised = (selected_moa_details.name or "").strip()
            hero_config["title"] = selected_moa_details.name
            hero_config["title_suffix"] = (
                acronym
                if acronym
                and name_normalised
                and acronym.lower() != name_normalised.lower()
                else ""
            )

            type_label = selected_moa_details.get_organization_type_display()
            badge_text = f"{type_label or 'Implementing MOA'} · {current_year}"

            hero_config["badge_icon"] = "fas fa-briefcase"
            hero_config["badge_text"] = badge_text
            hero_config["subtitle"] = subtitle_source
            hero_config["overview"]["entries_label"] = "PPAs under this MOA"
            hero_config["overview"]["budget_label"] = "Total budget (PHP)"

            extra_chips = []
            if type_label:
                extra_chips.append({"icon": "fas fa-sitemap", "text": type_label})
            if selected_moa_details.geographic_coverage:
                extra_chips.append(
                    {
                        "icon": "fas fa-map-location-dot",
                        "text": selected_moa_details.geographic_coverage,
                    }
                )
            hero_config["extra_chips"] = extra_chips

            contacts = []
            if selected_moa_details.focal_person:
                contacts.append(
                    {
                        "icon": "fas fa-user-tie",
                        "label": "Focal person",
                        "value": selected_moa_details.focal_person,
                        "meta": selected_moa_details.focal_person_position,
                    }
                )
            elif selected_moa_details.head_of_organization:
                contacts.append(
                    {
                        "icon": "fas fa-user-shield",
                        "label": selected_moa_details.head_position or "Head of agency",
                        "value": selected_moa_details.head_of_organization,
                        "meta": None,
                    }
                )

            primary_contact = next(
                (
                    value.strip()
                    for value in [
                        selected_moa_details.focal_person_contact or "",
                        selected_moa_details.mobile or "",
                        selected_moa_details.phone or "",
                    ]
                    if value and value.strip()
                ),
                "",
            )
            if primary_contact:
                contacts.append(
                    {
                        "icon": "fas fa-phone",
                        "label": "Primary contact",
                        "value": primary_contact,
                        "meta": None,
                    }
                )

            contact_email = next(
                (
                    value.strip()
                    for value in [
                        selected_moa_details.focal_person_email or "",
                        selected_moa_details.email or "",
                    ]
                    if value and value.strip()
                ),
                "",
            )
            if contact_email:
                contacts.append(
                    {
                        "icon": "fas fa-envelope",
                        "label": "Email",
                        "value": contact_email,
                        "meta": None,
                    }
                )

            hero_config["contacts"] = contacts

    hero_budget_total_display = "₱0"
    if len(stats_cards) > 2:
        hero_budget_total_display = stats_cards[2].get("total") or "₱0"

    # Implementing organizations
    implementing_orgs = (
        filtered_entries.exclude(implementing_moa__isnull=True)
        .values("implementing_moa__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    page_size_param = request.GET.get("page_size", "10")
    try:
        page_size = int(page_size_param)
    except (TypeError, ValueError):
        page_size = 10

    if page_size not in {10, 25, 50}:
        page_size = 10

    paginated_entries = filtered_entries.order_by("created_at", "id")
    paginator = Paginator(paginated_entries, page_size)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    implementing_moa_options = (
        all_moa_entries.exclude(implementing_moa__isnull=True)
        .values("implementing_moa__id", "implementing_moa__name")
        .distinct()
        .order_by("implementing_moa__name")
    )

    fiscal_year_options = sorted(
        {
            year
            for year in all_moa_entries.values_list("fiscal_year", flat=True)
            if year
        },
        reverse=True,
    )

    preserved_query = request.GET.copy()
    if "page" in preserved_query:
        preserved_query.pop("page")
    base_querystring = preserved_query.urlencode()

    context = {
        "stats_cards": stats_cards,
        "quick_actions": quick_actions,
        "page_obj": page_obj,
        "page_size": page_size,
        "page_size_options": [10, 25, 50],
        "status_breakdown": status_breakdown,
        "progress_snapshot": progress_snapshot,
        "hero_config": hero_config,
        "selected_moa_details": selected_moa_details,
        "hero_budget_total_display": hero_budget_total_display,
        "implementing_orgs": implementing_orgs,
        "current_year": current_year,
        "status_choices": MonitoringEntry.STATUS_CHOICES,
        "selected_status": status_filter,
        "selected_moa": moa_filter,
        "selected_year": fiscal_year_filter,
        "search_query": search_query,
        "implementing_moa_options": implementing_moa_options,
        "fiscal_year_options": fiscal_year_options,
        "result_count": paginator.count,
        "base_querystring": base_querystring,
    }

    return render(request, "monitoring/moa_ppas_dashboard.html", context)


@login_required
def import_moa_data(request):
    """Import MOA PPAs data from CSV or Excel file."""

    if request.method == "POST":
        if "csv_file" not in request.FILES:
            messages.error(request, "Please select a CSV file to upload.")
            return redirect("monitoring:moa_ppas")

        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect("monitoring:moa_ppas")

        try:
            decoded_file = csv_file.read().decode("utf-8")
            csv_reader = csv.DictReader(decoded_file.splitlines())

            imported_count = 0
            error_count = 0

            for row in csv_reader:
                try:
                    # Create MOA PPA entry from CSV data
                    entry = MonitoringEntry.objects.create(
                        title=row.get("title", "").strip(),
                        category="moa_ppa",
                        summary=row.get("summary", "").strip(),
                        status=row.get("status", "planning").lower(),
                        progress=int(row.get("progress", 0)),
                        budget_allocation=(
                            float(row.get("budget_allocation", 0))
                            if row.get("budget_allocation")
                            else None
                        ),
                        budget_obc_allocation=(
                            float(row.get("budget_obc_allocation", 0))
                            if row.get("budget_obc_allocation")
                            else None
                        ),
                        oobc_unit=row.get("oobc_unit", "").strip(),
                        created_by=request.user,
                        updated_by=request.user,
                    )
                    imported_count += 1
                except Exception as e:
                    error_count += 1
                    continue

            if imported_count > 0:
                messages.success(
                    request, f"Successfully imported {imported_count} MOA PPAs."
                )
            if error_count > 0:
                messages.warning(
                    request,
                    f"{error_count} entries could not be imported due to data errors.",
                )

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")

        return redirect("monitoring:moa_ppas")

    context = {
        "sample_csv_headers": [
            "title",
            "summary",
            "status",
            "progress",
            "budget_allocation",
            "budget_obc_allocation",
            "oobc_unit",
        ]
    }
    return render(request, "monitoring/import_moa_data.html", context)


@login_required
def export_moa_data(request):
    """Export MOA PPAs data to CSV format."""

    moa_entries = MonitoringEntry.objects.filter(category="moa_ppa").select_related(
        "implementing_moa",
        "coverage_region",
        "coverage_province",
        "coverage_municipality",
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="moa_ppas_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    )

    writer = csv.writer(response)

    # Write header
    writer.writerow(
        [
            "Title",
            "Status",
            "Progress (%)",
            "Implementing MOA",
            "Budget Allocation (PHP)",
            "OBC Budget Allocation (PHP)",
            "Start Date",
            "Target End Date",
            "Region",
            "Province",
            "Municipality",
            "Summary",
            "OOBC Unit",
            "Created Date",
            "Last Updated",
        ]
    )

    # Write data rows
    for entry in moa_entries:
        writer.writerow(
            [
                entry.title,
                entry.get_status_display(),
                entry.progress,
                entry.implementing_moa.name if entry.implementing_moa else "",
                entry.budget_allocation or "",
                entry.budget_obc_allocation or "",
                entry.start_date.strftime("%Y-%m-%d") if entry.start_date else "",
                (
                    entry.target_end_date.strftime("%Y-%m-%d")
                    if entry.target_end_date
                    else ""
                ),
                entry.coverage_region.name if entry.coverage_region else "",
                entry.coverage_province.name if entry.coverage_province else "",
                entry.coverage_municipality.name if entry.coverage_municipality else "",
                entry.summary,
                entry.oobc_unit,
                entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                entry.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    return response


@login_required
def generate_moa_report(request):
    """Generate comprehensive MOA PPAs report."""

    moa_entries = _prefetch_entries().filter(category="moa_ppa")
    current_year = timezone.now().year

    # Report statistics
    total_entries = moa_entries.count()
    completed_entries = moa_entries.filter(status="completed").count()
    ongoing_entries = moa_entries.filter(status="ongoing").count()
    planning_entries = moa_entries.filter(status="planning").count()

    # Budget analysis
    total_budget = moa_entries.aggregate(
        total_budget=Sum("budget_allocation"),
        total_obc_budget=Sum("budget_obc_allocation"),
    )

    # Geographic distribution
    regional_distribution = (
        moa_entries.exclude(coverage_region__isnull=True)
        .values("coverage_region__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Implementation timeline
    upcoming_deadlines = moa_entries.filter(
        target_end_date__gte=timezone.now().date(),
        target_end_date__lte=timezone.now().date() + timedelta(days=30),
    ).order_by("target_end_date")

    # Progress analysis
    progress_analysis = {
        "high_progress": moa_entries.filter(progress__gte=75).count(),
        "medium_progress": moa_entries.filter(
            progress__gte=50, progress__lt=75
        ).count(),
        "low_progress": moa_entries.filter(progress__lt=50).count(),
        "avg_progress": moa_entries.aggregate(avg=Avg("progress"))["avg"] or 0,
    }

    context = {
        "report_date": datetime.now(),
        "total_entries": total_entries,
        "completed_entries": completed_entries,
        "ongoing_entries": ongoing_entries,
        "planning_entries": planning_entries,
        "total_budget": total_budget,
        "regional_distribution": regional_distribution,
        "upcoming_deadlines": upcoming_deadlines,
        "progress_analysis": progress_analysis,
        "current_year": current_year,
    }

    return render(request, "monitoring/moa_report.html", context)


@login_required
def bulk_update_moa_status(request):
    """Bulk update status for multiple MOA PPAs."""

    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_entries")
        new_status = request.POST.get("new_status")
        new_progress = request.POST.get("new_progress")

        if not selected_ids:
            messages.error(request, "Please select at least one MOA PPA to update.")
            return redirect("monitoring:moa_ppas")

        try:
            entries = MonitoringEntry.objects.filter(
                id__in=selected_ids, category="moa_ppa"
            )

            updated_count = 0
            for entry in entries:
                if new_status:
                    entry.status = new_status
                if new_progress:
                    entry.progress = int(new_progress)
                entry.updated_by = request.user
                entry.save()
                updated_count += 1

            messages.success(request, f"Successfully updated {updated_count} MOA PPAs.")

        except Exception as e:
            messages.error(request, f"Error updating entries: {str(e)}")

        return redirect("monitoring:moa_ppas")

    # Get MOA PPAs for selection
    moa_entries = MonitoringEntry.objects.filter(category="moa_ppa").order_by(
        "-updated_at"
    )
    paginator = Paginator(moa_entries, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "status_choices": MonitoringEntry.STATUS_CHOICES,
    }

    return render(request, "monitoring/bulk_update_moa_status.html", context)


@login_required
def schedule_moa_review(request):
    """Schedule coordination meeting for MOA PPAs review."""

    if request.method == "POST":
        meeting_title = request.POST.get("meeting_title")
        meeting_date = request.POST.get("meeting_date")
        meeting_time = request.POST.get("meeting_time")
        participants = request.POST.get("participants")
        agenda = request.POST.get("agenda")
        selected_ppas = request.POST.getlist("selected_ppas")

        try:
            # Here you would typically create a coordination event
            # For now, we'll just create a placeholder response
            messages.success(
                request,
                f"Review meeting '{meeting_title}' scheduled for {meeting_date} at {meeting_time}. "
                f"Selected {len(selected_ppas)} MOA PPAs for review.",
            )
            return redirect("monitoring:moa_ppas")

        except Exception as e:
            messages.error(request, f"Error scheduling meeting: {str(e)}")

    # Get MOA PPAs that need review (low progress or overdue)
    review_candidates = (
        MonitoringEntry.objects.filter(
            category="moa_ppa", status__in=["ongoing", "planning"]
        )
        .filter(
            Q(progress__lt=50)
            | Q(target_end_date__lt=timezone.now().date())
            | Q(last_status_update__lt=timezone.now().date() - timedelta(days=30))
        )
        .order_by("target_end_date", "progress")
    )

    context = {
        "review_candidates": review_candidates,
        "suggested_date": (timezone.now() + timedelta(days=7)).date(),
    }

    return render(request, "monitoring/schedule_moa_review.html", context)


@login_required
def oobc_initiatives_dashboard(request):
    """Dedicated dashboard for OOBC Initiatives."""

    oobc_entries = _prefetch_entries().filter(category="oobc_ppa")
    current_year = timezone.now().year

    # Filter for current year entries
    oobc_year_qs = oobc_entries.filter(
        Q(start_date__year=current_year)
        | Q(start_date__isnull=True, created_at__year=current_year)
    )

    # Statistics cards
    total_oobc_initiatives = oobc_entries.count()
    total_budget = oobc_entries.aggregate(
        total=Sum("budget_allocation"), obc_total=Sum("budget_obc_allocation")
    )

    # Community impact
    total_communities_served = (
        oobc_entries.exclude(communities__isnull=True).distinct().count()
    )
    unique_communities = oobc_entries.values("communities__name").distinct().count()

    # OOBC units analysis
    oobc_units = (
        oobc_entries.exclude(oobc_unit="")
        .values("oobc_unit")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    stats_cards = [
        {
            "title": "Total OOBC Initiatives",
            "subtitle": f"Office-Led Programs",
            "icon": "fas fa-hand-holding-heart",            "icon_color": "text-amber-600",  # Total/General - Amber
            "total": total_oobc_initiatives,
            "metrics": [
                {
                    "label": "Completed",
                    "value": oobc_entries.filter(status="completed").count(),
                },
                {
                    "label": "Ongoing",
                    "value": oobc_entries.filter(status="ongoing").count(),
                },
                {
                    "label": "Planning",
                    "value": oobc_entries.filter(status="planning").count(),
                },
            ],
        },
        {
            "title": "Budget Investment",
            "subtitle": f"Program Funding (PHP)",
            "icon": "fas fa-hand-holding-usd",
            "icon_color": "text-blue-600",  # Info - Blue
            
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "total": f"₱{total_budget['total'] or 0:,.0f}",
            "metrics": [
                {
                    "label": "OBC Budget",
                    "value": f"₱{total_budget['obc_total'] or 0:,.0f}",
                },
                {
                    "label": "With Budget",
                    "value": oobc_entries.exclude(
                        budget_allocation__isnull=True
                    ).count(),
                },
                {
                    "label": "Pending",
                    "value": oobc_entries.filter(
                        budget_allocation__isnull=True
                    ).count(),
                },
            ],
        },
        {
            "title": "Community Impact",
            "subtitle": f"OBC Communities Served",
            "icon": "fas fa-users",
            "icon_color": "text-purple-600",  # Community/Proposed - Purple
            
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "total": unique_communities,
            "metrics": [
                {"label": "Direct", "value": total_communities_served},
                {
                    "label": "Partners",
                    "value": oobc_entries.exclude(supporting_organizations__isnull=True)
                    .distinct()
                    .count(),
                },
                {
                    "label": "Multi-Unit",
                    "value": oobc_entries.filter(supporting_organizations__isnull=False)
                    .distinct()
                    .count(),
                },
            ],
        },
        {
            "title": "Implementation Status",
            "subtitle": f"Progress Overview",
            "icon": "fas fa-chart-line",
            "icon_color": "text-emerald-600",  # Success/Progress - Emerald
            
            "gradient": "from-orange-500 via-orange-600 to-orange-700",
            "total": f"{oobc_entries.aggregate(avg=Avg('progress'))['avg'] or 0:.0f}%",
            "metrics": [
                {
                    "label": "High (75%+)",
                    "value": oobc_entries.filter(progress__gte=75).count(),
                },
                {
                    "label": "Medium",
                    "value": oobc_entries.filter(
                        progress__gte=50, progress__lt=75
                    ).count(),
                },
                {
                    "label": "Low (<50%)",
                    "value": oobc_entries.filter(progress__lt=50).count(),
                },
            ],
        },
    ]

    # Quick actions specific to OOBC Initiatives
    quick_actions = [
        {
            "title": "Add New Initiative",
            "description": "Register a new OOBC-led program or project.",
            "icon": "fas fa-plus-circle",
            "color": "bg-emerald-500",
            "url": reverse("monitoring:create_oobc"),
        },
        {
            "title": "Impact Assessment",
            "description": "Analyze community impact and outcomes.",
            "icon": "fas fa-chart-bar",
            "color": "bg-blue-500",
            "url": reverse("monitoring:oobc_impact_report"),
        },
        {
            "title": "Unit Performance",
            "description": "Compare OOBC unit effectiveness.",
            "icon": "fas fa-trophy",
            "color": "bg-purple-500",
            "url": reverse("monitoring:oobc_unit_performance"),
        },
        {
            "title": "Export Data",
            "description": "Export OOBC initiatives to Excel or CSV.",
            "icon": "fas fa-download",
            "color": "bg-indigo-500",
            "url": reverse("monitoring:export_oobc_data"),
        },
        {
            "title": "Budget Review",
            "description": "Review budget allocation and utilization.",
            "icon": "fas fa-calculator",
            "color": "bg-orange-500",
            "url": reverse("monitoring:oobc_budget_review"),
        },
        {
            "title": "Community Feedback",
            "description": "Gather feedback from beneficiary communities.",
            "icon": "fas fa-comments",
            "color": "bg-teal-500",
            "url": reverse("monitoring:oobc_community_feedback"),
        },
    ]

    # Status breakdown
    status_breakdown = [
        {
            "key": item["status"],
            "label": dict(MonitoringEntry.STATUS_CHOICES).get(
                item["status"], item["status"]
            ),
            "total": item["total"],
        }
        for item in (
            oobc_entries.order_by()
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )
    ]

    # Recent updates
    recent_updates = (
        MonitoringUpdate.objects.filter(entry__category="oobc_ppa")
        .select_related("entry", "created_by")
        .order_by("-created_at")[:10]
    )

    # Progress snapshot
    progress_snapshot = oobc_entries.aggregate(
        avg_progress=Avg("progress"),
        latest_update=Max("updated_at"),
    )

    # OOBC units breakdown
    oobc_units_breakdown = list(oobc_units)

    context = {
        "stats_cards": stats_cards,
        "quick_actions": quick_actions,
        "oobc_entries": oobc_entries.order_by("-updated_at"),
        "status_breakdown": status_breakdown,
        "recent_updates": recent_updates,
        "progress_snapshot": progress_snapshot,
        "oobc_units_breakdown": oobc_units_breakdown,
        "current_year": current_year,
    }

    return render(request, "monitoring/oobc_initiatives_dashboard.html", context)


@login_required
def obc_requests_dashboard(request):
    """Dedicated dashboard for OBC Requests and Proposals."""

    obc_entries = _prefetch_entries().filter(category="obc_request")
    current_year = timezone.now().year

    # Filter for current year entries
    obc_year_qs = obc_entries.filter(Q(created_at__year=current_year))

    # Statistics cards
    total_obc_requests = obc_entries.count()

    # Request status analysis
    pending_statuses = ["submitted", "under_review", "clarification"]
    in_progress_statuses = ["endorsed", "approved", "in_progress"]
    completed_requests = obc_entries.filter(request_status="completed").count()
    pending_requests = obc_entries.filter(request_status__in=pending_statuses).count()
    active_requests = obc_entries.filter(
        request_status__in=in_progress_statuses
    ).count()

    # Priority analysis
    high_priority = obc_entries.filter(priority="high").count()
    urgent_priority = obc_entries.filter(priority="urgent").count()

    # Community analysis
    requesting_communities = (
        obc_entries.exclude(submitted_by_community__isnull=True)
        .values("submitted_by_community__name")
        .distinct()
        .count()
    )

    # Receiving organizations
    receiving_orgs = (
        obc_entries.exclude(submitted_to_organization__isnull=True)
        .values("submitted_to_organization__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    stats_cards = [
        {
            "title": "Total OBC Requests",
            "subtitle": f"Community Proposals",
            "icon": "fas fa-file-signature",
            "icon_color": "text-blue-600",
            "gradient": "from-cyan-500 via-sky-500 to-indigo-500",
            "total": total_obc_requests,
            "metrics": [
                {"label": "Completed", "value": completed_requests},
                {"label": "Active", "value": active_requests},
                {"label": "Pending", "value": pending_requests},
            ],
        },
        {
            "title": "Request Priority",
            "subtitle": f"Urgency Classification",
            "icon": "fas fa-exclamation-triangle",
            "icon_color": "text-orange-600",
            "gradient": "from-red-500 via-orange-500 to-yellow-500",
            "total": urgent_priority + high_priority,
            "metrics": [
                {"label": "Urgent", "value": urgent_priority},
                {"label": "High", "value": high_priority},
                {
                    "label": "Standard",
                    "value": obc_entries.filter(priority__in=["medium", "low"]).count(),
                },
            ],
        },
        {
            "title": "Community Participation",
            "subtitle": f"Requesting Communities",
            "icon": "fas fa-mosque",
            "icon_color": "text-emerald-600",
            "gradient": "from-green-500 via-emerald-500 to-teal-500",
            "total": requesting_communities,
            "metrics": [
                {
                    "label": "Active",
                    "value": obc_entries.filter(request_status__in=in_progress_statuses)
                    .values("submitted_by_community")
                    .distinct()
                    .count(),
                },
                {
                    "label": "Pending",
                    "value": obc_entries.filter(request_status__in=pending_statuses)
                    .values("submitted_by_community")
                    .distinct()
                    .count(),
                },
                {
                    "label": "Completed",
                    "value": obc_entries.filter(request_status="completed")
                    .values("submitted_by_community")
                    .distinct()
                    .count(),
                },
            ],
        },
        {
            "title": "Response Rate",
            "subtitle": f"Processing Efficiency",
            "icon": "fas fa-tachometer-alt",
            "icon_color": "text-purple-600",
            "gradient": "from-purple-500 via-pink-500 to-rose-500",
            "total": f"{(completed_requests + active_requests) / max(total_obc_requests, 1) * 100:.0f}%",
            "metrics": [
                {"label": "Resolved", "value": completed_requests + active_requests},
                {
                    "label": "Under Review",
                    "value": obc_entries.filter(request_status="under_review").count(),
                },
                {
                    "label": "Awaiting",
                    "value": obc_entries.filter(request_status="submitted").count(),
                },
            ],
        },
    ]

    # Quick actions specific to OBC Requests
    quick_actions = [
        {
            "title": "Submit New Request",
            "description": "Register a new community request or proposal.",
            "icon": "fas fa-plus-circle",
            "color": "bg-blue-500",
            "url": reverse("monitoring:create_request"),
        },
        {
            "title": "Priority Queue",
            "description": "Review high-priority and urgent requests.",
            "icon": "fas fa-flag",
            "color": "bg-red-500",
            "url": reverse("monitoring:obc_priority_queue"),
        },
        {
            "title": "Community Dashboard",
            "description": "View requests by community and region.",
            "icon": "fas fa-map-marked-alt",
            "color": "bg-green-500",
            "url": reverse("monitoring:obc_community_dashboard"),
        },
        {
            "title": "Generate Reports",
            "description": "Create comprehensive OBC requests analysis.",
            "icon": "fas fa-chart-line",
            "color": "bg-purple-500",
            "url": reverse("monitoring:generate_obc_report"),
        },
        {
            "title": "Bulk Status Update",
            "description": "Update multiple request statuses at once.",
            "icon": "fas fa-edit",
            "color": "bg-orange-500",
            "url": reverse("monitoring:bulk_update_obc_status"),
        },
        {
            "title": "Export Requests",
            "description": "Export OBC requests data to Excel or CSV.",
            "icon": "fas fa-download",
            "color": "bg-indigo-500",
            "url": reverse("monitoring:export_obc_data"),
        },
    ]

    # Request status breakdown
    request_status_breakdown = [
        {
            "key": item["request_status"],
            "label": dict(MonitoringEntry.REQUEST_STATUS_CHOICES).get(
                item["request_status"], item["request_status"]
            ),
            "total": item["total"],
        }
        for item in (
            obc_entries.order_by()
            .values("request_status")
            .annotate(total=Count("id"))
            .order_by("request_status")
        )
    ]

    # Recent updates
    recent_updates = (
        MonitoringUpdate.objects.filter(entry__category="obc_request")
        .select_related("entry", "created_by")
        .order_by("-created_at")[:10]
    )

    # Progress snapshot
    progress_snapshot = {
        "latest_update": obc_entries.aggregate(latest=Max("updated_at"))["latest"],
        "pending_review": pending_requests,
        "avg_response_days": 7,  # This would be calculated from actual data
    }

    context = {
        "stats_cards": stats_cards,
        "quick_actions": quick_actions,
        "obc_entries": obc_entries.order_by("-updated_at"),
        "request_status_breakdown": request_status_breakdown,
        "recent_updates": recent_updates,
        "progress_snapshot": progress_snapshot,
        "receiving_orgs": receiving_orgs,
        "current_year": current_year,
    }

    return render(request, "monitoring/obc_requests_dashboard.html", context)


# Placeholder views for OOBC Initiatives quick actions
@login_required
def oobc_impact_report(request):
    """Placeholder for OOBC impact assessment report."""
    messages.info(request, "Impact Assessment feature coming soon!")
    return redirect("monitoring:oobc_initiatives")


@login_required
def oobc_unit_performance(request):
    """Placeholder for OOBC unit performance comparison."""
    messages.info(request, "Unit Performance feature coming soon!")
    return redirect("monitoring:oobc_initiatives")


@login_required
def export_oobc_data(request):
    """Placeholder for OOBC data export."""
    messages.info(request, "OOBC Data Export feature coming soon!")
    return redirect("monitoring:oobc_initiatives")


@login_required
def oobc_budget_review(request):
    """Placeholder for OOBC budget review."""
    messages.info(request, "Budget Review feature coming soon!")
    return redirect("monitoring:oobc_initiatives")


@login_required
def oobc_community_feedback(request):
    """Placeholder for OOBC community feedback."""
    messages.info(request, "Community Feedback feature coming soon!")
    return redirect("monitoring:oobc_initiatives")


# Placeholder views for OBC Requests quick actions
@login_required
def obc_priority_queue(request):
    """Placeholder for OBC priority queue."""
    messages.info(request, "Priority Queue feature coming soon!")
    return redirect("monitoring:obc_requests")


@login_required
def obc_community_dashboard(request):
    """Placeholder for OBC community dashboard."""
    messages.info(request, "Community Dashboard feature coming soon!")
    return redirect("monitoring:obc_requests")


@login_required
def generate_obc_report(request):
    """Placeholder for OBC requests report."""
    messages.info(request, "OBC Reports feature coming soon!")
    return redirect("monitoring:obc_requests")


@login_required
def bulk_update_obc_status(request):
    """Placeholder for OBC bulk status update."""
    messages.info(request, "Bulk Status Update feature coming soon!")
    return redirect("monitoring:obc_requests")


@login_required
def export_obc_data(request):
    """Placeholder for OBC data export."""
    messages.info(request, "OBC Data Export feature coming soon!")
    return redirect("monitoring:obc_requests")


# ==================== WORKITEM INTEGRATION VIEWS ====================


@moa_can_edit_ppa
@login_required
@require_POST
def enable_workitem_tracking(request, pk):
    """
    HTMX endpoint: Enable WorkItem tracking for a MonitoringEntry.

    Creates execution project hierarchy and updates tracking flags.
    """
    entry = get_object_or_404(MonitoringEntry, pk=pk)

    if entry.category != "moa_ppa":
        message = "Work item tracking is only available for MOA PPAs."
        return _render_workitems_tab(
            request, entry, status=400, triggers={"show-toast": message}
        )

    if entry.execution_project:
        return _render_workitems_tab(
            request,
            entry,
            triggers={"show-toast": "Work item tracking already enabled."},
        )

    template_type = (
        request.POST.get("template_type")
        or request.POST.get("structure_template")
        or "activity"
    )
    template_choices = {"program", "activity", "milestone", "minimal"}
    if template_type not in template_choices:
        template_type = "activity"

    policy = (
        request.POST.get("budget_distribution_policy")
        or entry.budget_distribution_policy
        or "equal"
    )
    policy_choices = {"equal", "weighted", "manual"}
    if policy not in policy_choices:
        policy = "equal"

    try:
        with transaction.atomic():
            project = entry.create_execution_project(
                structure_template=template_type, created_by=request.user
            )
            entry.execution_project = project
            entry.enable_workitem_tracking = True
            entry.budget_distribution_policy = policy
            entry.updated_by = request.user
            entry.save(
                update_fields=[
                    "execution_project",
                    "enable_workitem_tracking",
                    "budget_distribution_policy",
                    "updated_by",
                    "updated_at",
                ]
            )
    except ValidationError as exc:
        message = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        logger.warning(
            "Failed to enable WorkItem tracking for %s: %s", entry.id, message
        )
        return _render_workitems_tab(
            request, entry, status=400, triggers={"show-toast": message}
        )
    except Exception:
        logger.exception(
            "Unexpected error while enabling WorkItem tracking for %s", entry.id
        )
        return _render_workitems_tab(
            request,
            entry,
            status=500,
            triggers={
                "show-toast": "Unable to enable work item tracking right now. Please try again."
            },
        )

    entry.refresh_from_db()
    return _render_workitems_tab(
        request,
        entry,
        triggers={
            "show-toast": "Work item tracking enabled. Execution project created.",
            "refresh-counters": True,
        },
    )


@moa_can_edit_ppa
@login_required
@require_POST
def disable_workitem_tracking(request, pk):
    """
    HTMX/JSON endpoint: Disable WorkItem tracking and remove execution project.
    """
    entry = get_object_or_404(MonitoringEntry, pk=pk)

    if not request.user.is_superuser:
        message = "Only superuser administrators can disable work item tracking."
        if request.headers.get("HX-Request"):
            return _render_workitems_tab(
                request, entry, status=403, triggers={"show-toast": message}
            )
        return JsonResponse({"error": message}, status=403)

    if not entry.execution_project:
        message = "This PPA does not have an execution project to disable."
        if request.headers.get("HX-Request"):
            return _render_workitems_tab(
                request, entry, status=400, triggers={"show-toast": message}
            )
        return JsonResponse({"error": message}, status=400)

    try:
        with transaction.atomic():
            entry.disable_workitem_tracking(updated_by=request.user)
    except Exception:
        logger.exception("Failed to disable WorkItem tracking for %s", entry.id)
        message = "Unable to disable work item tracking right now. Please try again."
        if request.headers.get("HX-Request"):
            return _render_workitems_tab(
                request, entry, status=500, triggers={"show-toast": message}
            )
        return JsonResponse({"error": message}, status=500)

    entry.refresh_from_db()
    if request.headers.get("HX-Request"):
        return _render_workitems_tab(
            request,
            entry,
            triggers={"show-toast": "Work item tracking disabled. Execution project removed."},
        )

    return JsonResponse({"success": True})


@moa_can_edit_ppa
@login_required
@require_POST
def distribute_budget(request, pk):
    """
    HTMX/JSON endpoint: Distribute PPA budget across work items.

    Supports direct HTMX calls (uses stored policy) and JSON payload submissions
    from the budget distribution modal.
    """
    entry = get_object_or_404(MonitoringEntry, pk=pk)

    if not entry.execution_project:
        message = "Enable work item tracking before distributing budget."
        if request.headers.get("HX-Request"):
            return _render_workitems_tab(
                request, entry, status=400, triggers={"show-toast": message}
            )
        return JsonResponse({"error": message}, status=400)

    payload_method = request.POST.get("method")
    distribution_payload = None

    if request.content_type and "application/json" in request.content_type:
        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            payload = {}
        method = payload.get("method") or payload_method
        distribution_payload = payload.get("distribution")
    else:
        method = payload_method
        distribution_raw = request.POST.get("distribution")
        if distribution_raw:
            try:
                distribution_payload = json.loads(distribution_raw)
            except json.JSONDecodeError:
                distribution_payload = None

    if not method:
        method = entry.budget_distribution_policy or "equal"

    allowed_methods = {"equal", "weighted", "manual"}
    if method not in allowed_methods:
        method = "equal"

    try:
        if distribution_payload:
            distribution = {}
            for key, value in distribution_payload.items():
                try:
                    item_id = uuid.UUID(str(key))
                except (TypeError, ValueError) as exc:
                    raise ValidationError(f"Invalid work item id: {key}") from exc
                distribution[item_id] = Decimal(str(value or 0))
        elif method == "equal":
            distribution = BudgetDistributionService.distribute_equal(entry)
        else:
            raise ValidationError(
                "Detailed distribution data is required for this method."
            )

        with transaction.atomic():
            entry.budget_distribution_policy = method
            entry.updated_by = request.user
            entry.save(update_fields=["budget_distribution_policy", "updated_by", "updated_at"])
            BudgetDistributionService.apply_distribution(entry, distribution)
    except ValidationError as exc:
        message = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        if request.headers.get("HX-Request"):
            return _render_workitems_tab(
                request, entry, status=400, triggers={"show-toast": message}
            )
        return JsonResponse({"error": message}, status=400)
    except Exception:
        logger.exception("Failed to distribute budget for %s", entry.id)
        message = "Unable to distribute budget. Please try again."
        if request.headers.get("HX-Request"):
            return _render_workitems_tab(
                request, entry, status=500, triggers={"show-toast": message}
            )
        return JsonResponse({"error": message}, status=500)

    entry.refresh_from_db()
    if request.headers.get("HX-Request"):
        return _render_workitems_tab(
            request,
            entry,
            triggers={"show-toast": "Budget distributed successfully."},
        )

    workitem_stats = _build_workitem_context(entry)["workitem_stats"]
    return JsonResponse(
        {
            "success": True,
            "entry_id": str(entry.id),
            "method": method,
            "totals": {
                "allocated": str(workitem_stats["total_budget_allocated"]),
                "unallocated": str(workitem_stats["unallocated_budget"]),
            },
        }
    )


@login_required
@require_POST
def sync_progress(request, pk):
    """
    HTMX/JSON endpoint: Sync MonitoringEntry progress and status from WorkItems.
    """
    entry = get_object_or_404(MonitoringEntry, pk=pk)

    if not entry.execution_project:
        message = "Enable work item tracking before syncing progress."
        if request.headers.get("HX-Request"):
            return _render_workitems_tab(
                request, entry, status=400, triggers={"show-toast": message}
            )
        return JsonResponse({"error": message}, status=400)

    try:
        progress = entry.sync_progress_from_workitem()
        status_value = entry.sync_status_from_workitem()
    except Exception:
        logger.exception("Failed to sync progress for %s", entry.id)
        message = "Unable to sync progress right now. Please try again."
        if request.headers.get("HX-Request"):
            return _render_workitems_tab(
                request, entry, status=500, triggers={"show-toast": message}
            )
        return JsonResponse({"error": message}, status=500)

    entry.refresh_from_db()
    if request.headers.get("HX-Request"):
        return _render_workitems_tab(
            request,
            entry,
            triggers={"show-toast": "Progress synchronized from Work Items."},
        )
    return JsonResponse(
        {"success": True, "progress": progress, "status": status_value}
    )


@login_required
def work_item_children(request, work_item_id):
    """
    HTMX endpoint: Return children of a WorkItem for lazy loading.

    Used by work_item_tree.html to load child items when user expands a node.
    """
    from common.work_item_model import WorkItem

    work_item = get_object_or_404(WorkItem, pk=work_item_id)
    children = work_item.get_children().select_related('created_by')
    depth = int(request.GET.get('depth', 1))

    context = {
        'children': children,
        'depth': depth
    }

    return render(request, 'monitoring/partials/work_item_children.html', context)


# ==================== COMPLIANCE REPORTS (Phase 5) ====================

@login_required
def reports_dashboard(request):
    """
    Compliance Reports Dashboard.

    Provides access to government compliance reports:
    - MFBM Budget Execution Report
    - BPDA Development Alignment Report
    - COA Budget Variance Report
    """
    current_year = timezone.now().year

    # Get fiscal years for filter
    fiscal_years = sorted(
        set(
            MonitoringEntry.objects.exclude(fiscal_year__isnull=True)
            .values_list('fiscal_year', flat=True)
            .distinct()
        ),
        reverse=True
    )

    # Get implementing MOAs for filter
    implementing_moas = (
        MonitoringEntry.objects.exclude(implementing_moa__isnull=True)
        .values('implementing_moa__id', 'implementing_moa__name')
        .distinct()
        .order_by('implementing_moa__name')
    )

    # Get sectors for filter
    sectors = MonitoringEntry.SECTOR_CHOICES

    context = {
        'current_year': current_year,
        'fiscal_years': fiscal_years,
        'implementing_moas': implementing_moas,
        'sectors': sectors,
    }

    return render(request, 'monitoring/reports_dashboard.html', context)


@login_required
def mfbm_budget_report_download(request):
    """
    Download MFBM Budget Execution Report.

    Query Parameters:
        - fiscal_year: Required fiscal year
        - moa_filter: Optional MOA organization ID filter
    """
    from .services.reports import generate_mfbm_budget_execution_report

    fiscal_year = request.GET.get('fiscal_year')
    moa_filter = request.GET.get('moa_filter', None)

    if not fiscal_year:
        messages.error(request, "Fiscal year is required for MFBM report.")
        return redirect('monitoring:reports_dashboard')

    try:
        fiscal_year = int(fiscal_year)
    except (TypeError, ValueError):
        messages.error(request, "Invalid fiscal year provided.")
        return redirect('monitoring:reports_dashboard')

    # Generate report
    try:
        report_buffer = generate_mfbm_budget_execution_report(
            fiscal_year=fiscal_year,
            moa_filter=moa_filter
        )

        # Prepare response
        response = HttpResponse(
            report_buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        filename = f"MFBM_Budget_Execution_FY{fiscal_year}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        messages.error(request, f"Error generating MFBM report: {str(e)}")
        return redirect('monitoring:reports_dashboard')


@login_required
def bpda_development_report_download(request):
    """
    Download BPDA Development Alignment Report.

    Query Parameters:
        - fiscal_year: Required fiscal year
        - sector: Optional sector filter
    """
    from .services.reports import generate_bpda_development_report

    fiscal_year = request.GET.get('fiscal_year')
    sector = request.GET.get('sector', None)

    if not fiscal_year:
        messages.error(request, "Fiscal year is required for BPDA report.")
        return redirect('monitoring:reports_dashboard')

    try:
        fiscal_year = int(fiscal_year)
    except (TypeError, ValueError):
        messages.error(request, "Invalid fiscal year provided.")
        return redirect('monitoring:reports_dashboard')

    # Generate report
    try:
        report_buffer = generate_bpda_development_report(
            fiscal_year=fiscal_year,
            sector=sector
        )

        # Prepare response
        response = HttpResponse(
            report_buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        filename = f"BPDA_Development_Alignment_FY{fiscal_year}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        messages.error(request, f"Error generating BPDA report: {str(e)}")
        return redirect('monitoring:reports_dashboard')


@login_required
def coa_variance_report_download(request):
    """
    Download COA Budget Variance Report.

    Query Parameters:
        - fiscal_year: Required fiscal year
        - moa_filter: Optional MOA organization ID filter
    """
    from .services.reports import generate_coa_variance_report

    fiscal_year = request.GET.get('fiscal_year')
    moa_filter = request.GET.get('moa_filter', None)

    if not fiscal_year:
        messages.error(request, "Fiscal year is required for COA report.")
        return redirect('monitoring:reports_dashboard')

    try:
        fiscal_year = int(fiscal_year)
    except (TypeError, ValueError):
        messages.error(request, "Invalid fiscal year provided.")
        return redirect('monitoring:reports_dashboard')

    # Generate report
    try:
        report_buffer = generate_coa_variance_report(
            fiscal_year=fiscal_year,
            moa_filter=moa_filter
        )

        # Prepare response
        response = HttpResponse(
            report_buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        filename = f"COA_Budget_Variance_FY{fiscal_year}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        messages.error(request, f"Error generating COA report: {str(e)}")
        return redirect('monitoring:reports_dashboard')


@login_required
def ppa_calendar_feed(request, entry_id):
    """
    Calendar feed endpoint for a specific PPA.

    Returns JSON calendar events containing only work items from this PPA's
    execution hierarchy (filtered by ppa_category and implementing_moa for isolation).

    Args:
        entry_id: UUID of the MonitoringEntry (PPA)

    Returns:
        JsonResponse with calendar events in FullCalendar format
    """
    from common.work_item_model import WorkItem
    from django.http import JsonResponse
    import json

    try:
        entry = MonitoringEntry.objects.get(id=entry_id)
    except MonitoringEntry.DoesNotExist:
        return JsonResponse({'error': 'PPA not found'}, status=404)

    # Get all work items for this PPA (execution project + descendants)
    # Filter by related_ppa to get direct PPA work items
    # Also include work items in the execution project hierarchy
    work_items = WorkItem.objects.filter(
        related_ppa=entry,
        is_calendar_visible=True
    ).select_related(
        'created_by',
        'related_ppa'
    )

    # Also include execution project work items if exists
    if entry.execution_project:
        execution_items = entry.execution_project.get_descendants(include_self=True).filter(
            is_calendar_visible=True
        )
        # Combine querysets
        from itertools import chain
        work_items = list(chain(work_items, execution_items))

    # Build calendar events
    events = []
    for item in work_items:
        # Skip items without dates
        if not item.start_date:
            continue

        # Determine color based on work type
        color_map = {
            'project': '#3b82f6',  # Blue
            'activity': '#10b981',  # Emerald
            'task': '#8b5cf6',     # Purple
            'subtask': '#f59e0b',  # Amber
        }

        event = {
            'id': str(item.id),
            'title': item.title,
            'start': item.start_date.isoformat(),
            'end': (item.due_date or item.start_date).isoformat(),
            'allDay': not (item.start_time and item.end_time),
            'backgroundColor': color_map.get(item.work_type, '#6b7280'),
            'borderColor': color_map.get(item.work_type, '#6b7280'),
            'textColor': '#ffffff',
            'extendedProps': {
                'work_item_id': str(item.id),
                'work_type': item.work_type,
                'status': item.status,
                'priority': item.priority,
                'progress': item.progress,
                'description': item.description or '',
            }
        }

        # Add time if available
        if item.start_time:
            from datetime import datetime, time
            start_datetime = datetime.combine(item.start_date, item.start_time)
            event['start'] = start_datetime.isoformat()

        if item.end_time and item.due_date:
            end_datetime = datetime.combine(item.due_date, item.end_time)
            event['end'] = end_datetime.isoformat()

        events.append(event)

    return JsonResponse(events, safe=False)
