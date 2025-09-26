"""Views for Monitoring & Evaluation dashboard and detail pages."""

from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.forms import modelformset_factory
import csv
import json
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from common.services.locations import build_location_data, get_object_centroid
from communities.models import OBCCommunity
from common.models import Municipality
from .forms import (
    MonitoringMOAEntryForm,
    MonitoringOOBCEntryForm,
    MonitoringRequestEntryForm,
    MonitoringUpdateForm,
    MonitoringOBCQuickCreateForm,
)
from .models import MonitoringEntry, MonitoringUpdate


def _normalise_float(value):
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _prefetch_entries():
    """Return a queryset with the relations needed across views."""

    return (
        MonitoringEntry.objects.all()
        .select_related(
            "lead_organization",
            "submitted_by_community",
            "submitted_to_organization",
            "related_assessment",
            "related_event",
            "related_policy",
            "created_by",
            "updated_by",
        )
        .prefetch_related("communities", "supporting_organizations", "updates")
    )


@login_required
def monitoring_dashboard(request):
    """Render the consolidated Monitoring & Evaluation workspace."""

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
        "gradient": "from-blue-500 via-blue-600 to-blue-700",
        "total": moa_year_qs.count(),
        "metrics": [
            {"label": "Completed", "value": moa_year_qs.filter(status="completed").count()},
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
        "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
        "total": oobc_year_qs.count(),
        "metrics": [
            {"label": "Completed", "value": oobc_year_qs.filter(status="completed").count()},
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
                    Q(request_status="submitted") | Q(request_status="") | Q(request_status__isnull=True)
                ).count(),
            },
        ],
    }

    stats_cards = [moa_stats, oobc_stats, request_stats]

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
        "coordination_events": entries.filter(related_event__isnull=False).count(),
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
        key: index for index, (key, _label) in enumerate(MonitoringEntry.CATEGORY_CHOICES)
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
        MonitoringEntry.objects.filter(
            communities__in=entry.communities.all()
        )
        .exclude(pk=entry.pk)
        .distinct()
        .select_related("lead_organization")
    )

    context = {
        "entry": entry,
        "updates": entry.updates.select_related("created_by"),
        "update_form": update_form,
        "related_entries": related_entries,
    }
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
                "name": community.display_name or (barangay.name if barangay else "OBC"),
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

    moa_entries = _prefetch_entries().filter(category="moa_ppa")
    current_year = timezone.now().year

    # Filter for current year entries
    moa_year_qs = moa_entries.filter(
        Q(start_date__year=current_year)
        | Q(start_date__isnull=True, created_at__year=current_year)
    )

    # Statistics cards
    total_moa_ppas = moa_entries.count()
    total_budget = moa_entries.aggregate(
        total=Sum("budget_allocation"),
        obc_total=Sum("budget_obc_allocation")
    )

    # Geographic coverage
    geographic_coverage = {
        'regions': moa_entries.exclude(coverage_region__isnull=True).values('coverage_region__name').distinct().count(),
        'provinces': moa_entries.exclude(coverage_province__isnull=True).values('coverage_province__name').distinct().count(),
        'municipalities': moa_entries.exclude(coverage_municipality__isnull=True).values('coverage_municipality__name').distinct().count(),
    }

    # Timeline analysis
    upcoming_deadlines = moa_entries.filter(
        target_end_date__gte=timezone.now().date(),
        target_end_date__lte=timezone.now().date() + timezone.timedelta(days=30)
    ).count()

    stats_cards = [
        {
            "title": "Total MOA PPAs",
            "subtitle": f"Active Programs & Projects",
            "icon": "fas fa-building-columns",
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "total": total_moa_ppas,
            "metrics": [
                {"label": "Completed", "value": moa_entries.filter(status="completed").count()},
                {"label": "Ongoing", "value": moa_entries.filter(status="ongoing").count()},
                {"label": "Planning", "value": moa_entries.filter(status="planning").count()},
            ],
        },
        {
            "title": "Budget Allocation",
            "subtitle": f"Total & OBC-Specific (PHP)",
            "icon": "fas fa-peso-sign",
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "total": f"₱{total_budget['total'] or 0:,.0f}",
            "metrics": [
                {"label": "OBC Budget", "value": f"₱{total_budget['obc_total'] or 0:,.0f}"},
                {"label": "With Budget", "value": moa_entries.exclude(budget_allocation__isnull=True).count()},
                {"label": "Pending", "value": moa_entries.filter(budget_allocation__isnull=True).count()},
            ],
        },
        {
            "title": "Geographic Coverage",
            "subtitle": f"Implementation Areas",
            "icon": "fas fa-map-marked-alt",
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "total": geographic_coverage['regions'],
            "metrics": [
                {"label": "Regions", "value": geographic_coverage['regions']},
                {"label": "Provinces", "value": geographic_coverage['provinces']},
                {"label": "Municipalities", "value": geographic_coverage['municipalities']},
            ],
        },
        {
            "title": "Timeline Status",
            "subtitle": f"Implementation Schedule",
            "icon": "fas fa-calendar-check",
            "gradient": "from-orange-500 via-orange-600 to-orange-700",
            "total": upcoming_deadlines,
            "metrics": [
                {"label": "Due Soon", "value": upcoming_deadlines},
                {"label": "On Time", "value": moa_entries.filter(status="ongoing", progress__gte=50).count()},
                {"label": "Delayed", "value": moa_entries.filter(target_end_date__lt=timezone.now().date(), status__in=["ongoing", "planning"]).count()},
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
            "label": dict(MonitoringEntry.STATUS_CHOICES).get(item["status"], item["status"]),
            "total": item["total"],
        }
        for item in (
            moa_entries.order_by()
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )
    ]

    # Recent updates
    recent_updates = MonitoringUpdate.objects.filter(
        entry__category="moa_ppa"
    ).select_related("entry", "created_by").order_by("-created_at")[:10]

    # Progress snapshot
    progress_snapshot = moa_entries.aggregate(
        avg_progress=Avg("progress"),
        latest_update=Max("updated_at"),
    )

    # Implementing organizations
    implementing_orgs = moa_entries.exclude(implementing_moa__isnull=True).values(
        'implementing_moa__name'
    ).annotate(total=Count('id')).order_by('-total')[:10]

    context = {
        "stats_cards": stats_cards,
        "quick_actions": quick_actions,
        "moa_entries": moa_entries.order_by("-updated_at"),
        "status_breakdown": status_breakdown,
        "recent_updates": recent_updates,
        "progress_snapshot": progress_snapshot,
        "implementing_orgs": implementing_orgs,
        "current_year": current_year,
    }

    return render(request, "monitoring/moa_ppas_dashboard.html", context)


@login_required
def import_moa_data(request):
    """Import MOA PPAs data from CSV or Excel file."""

    if request.method == "POST":
        if 'csv_file' not in request.FILES:
            messages.error(request, "Please select a CSV file to upload.")
            return redirect("monitoring:moa_ppas")

        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect("monitoring:moa_ppas")

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(decoded_file.splitlines())

            imported_count = 0
            error_count = 0

            for row in csv_reader:
                try:
                    # Create MOA PPA entry from CSV data
                    entry = MonitoringEntry.objects.create(
                        title=row.get('title', '').strip(),
                        category='moa_ppa',
                        summary=row.get('summary', '').strip(),
                        status=row.get('status', 'planning').lower(),
                        progress=int(row.get('progress', 0)),
                        budget_allocation=float(row.get('budget_allocation', 0)) if row.get('budget_allocation') else None,
                        budget_obc_allocation=float(row.get('budget_obc_allocation', 0)) if row.get('budget_obc_allocation') else None,
                        oobc_unit=row.get('oobc_unit', '').strip(),
                        created_by=request.user,
                        updated_by=request.user,
                    )
                    imported_count += 1
                except Exception as e:
                    error_count += 1
                    continue

            if imported_count > 0:
                messages.success(request, f"Successfully imported {imported_count} MOA PPAs.")
            if error_count > 0:
                messages.warning(request, f"{error_count} entries could not be imported due to data errors.")

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")

        return redirect("monitoring:moa_ppas")

    context = {
        "sample_csv_headers": [
            "title", "summary", "status", "progress", "budget_allocation",
            "budget_obc_allocation", "oobc_unit"
        ]
    }
    return render(request, "monitoring/import_moa_data.html", context)


@login_required
def export_moa_data(request):
    """Export MOA PPAs data to CSV format."""

    moa_entries = MonitoringEntry.objects.filter(category="moa_ppa").select_related(
        "implementing_moa", "coverage_region", "coverage_province", "coverage_municipality"
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="moa_ppas_export_{datetime.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)

    # Write header
    writer.writerow([
        'Title', 'Status', 'Progress (%)', 'Implementing MOA', 'Budget Allocation (PHP)',
        'OBC Budget Allocation (PHP)', 'Start Date', 'Target End Date', 'Region',
        'Province', 'Municipality', 'Summary', 'OOBC Unit', 'Created Date', 'Last Updated'
    ])

    # Write data rows
    for entry in moa_entries:
        writer.writerow([
            entry.title,
            entry.get_status_display(),
            entry.progress,
            entry.implementing_moa.name if entry.implementing_moa else '',
            entry.budget_allocation or '',
            entry.budget_obc_allocation or '',
            entry.start_date.strftime('%Y-%m-%d') if entry.start_date else '',
            entry.target_end_date.strftime('%Y-%m-%d') if entry.target_end_date else '',
            entry.coverage_region.name if entry.coverage_region else '',
            entry.coverage_province.name if entry.coverage_province else '',
            entry.coverage_municipality.name if entry.coverage_municipality else '',
            entry.summary,
            entry.oobc_unit,
            entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            entry.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

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
        total_obc_budget=Sum("budget_obc_allocation")
    )

    # Geographic distribution
    regional_distribution = moa_entries.exclude(coverage_region__isnull=True).values(
        'coverage_region__name'
    ).annotate(count=Count('id')).order_by('-count')

    # Implementation timeline
    upcoming_deadlines = moa_entries.filter(
        target_end_date__gte=timezone.now().date(),
        target_end_date__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('target_end_date')

    # Progress analysis
    progress_analysis = {
        'high_progress': moa_entries.filter(progress__gte=75).count(),
        'medium_progress': moa_entries.filter(progress__gte=50, progress__lt=75).count(),
        'low_progress': moa_entries.filter(progress__lt=50).count(),
        'avg_progress': moa_entries.aggregate(avg=Avg('progress'))['avg'] or 0
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
        selected_ids = request.POST.getlist('selected_entries')
        new_status = request.POST.get('new_status')
        new_progress = request.POST.get('new_progress')

        if not selected_ids:
            messages.error(request, "Please select at least one MOA PPA to update.")
            return redirect("monitoring:moa_ppas")

        try:
            entries = MonitoringEntry.objects.filter(
                id__in=selected_ids,
                category="moa_ppa"
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
    moa_entries = MonitoringEntry.objects.filter(category="moa_ppa").order_by("-updated_at")
    paginator = Paginator(moa_entries, 20)
    page_number = request.GET.get('page')
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
        meeting_title = request.POST.get('meeting_title')
        meeting_date = request.POST.get('meeting_date')
        meeting_time = request.POST.get('meeting_time')
        participants = request.POST.get('participants')
        agenda = request.POST.get('agenda')
        selected_ppas = request.POST.getlist('selected_ppas')

        try:
            # Here you would typically create a coordination event
            # For now, we'll just create a placeholder response
            messages.success(
                request,
                f"Review meeting '{meeting_title}' scheduled for {meeting_date} at {meeting_time}. "
                f"Selected {len(selected_ppas)} MOA PPAs for review."
            )
            return redirect("monitoring:moa_ppas")

        except Exception as e:
            messages.error(request, f"Error scheduling meeting: {str(e)}")

    # Get MOA PPAs that need review (low progress or overdue)
    review_candidates = MonitoringEntry.objects.filter(
        category="moa_ppa",
        status__in=["ongoing", "planning"]
    ).filter(
        Q(progress__lt=50) |
        Q(target_end_date__lt=timezone.now().date()) |
        Q(last_status_update__lt=timezone.now().date() - timedelta(days=30))
    ).order_by('target_end_date', 'progress')

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
        total=Sum("budget_allocation"),
        obc_total=Sum("budget_obc_allocation")
    )

    # Community impact
    total_communities_served = oobc_entries.exclude(communities__isnull=True).distinct().count()
    unique_communities = oobc_entries.values('communities__name').distinct().count()

    # OOBC units analysis
    oobc_units = oobc_entries.exclude(oobc_unit='').values('oobc_unit').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    stats_cards = [
        {
            "title": "Total OOBC Initiatives",
            "subtitle": f"Office-Led Programs",
            "icon": "fas fa-hand-holding-heart",
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "total": total_oobc_initiatives,
            "metrics": [
                {"label": "Completed", "value": oobc_entries.filter(status="completed").count()},
                {"label": "Ongoing", "value": oobc_entries.filter(status="ongoing").count()},
                {"label": "Planning", "value": oobc_entries.filter(status="planning").count()},
            ],
        },
        {
            "title": "Budget Investment",
            "subtitle": f"Program Funding (PHP)",
            "icon": "fas fa-hand-holding-usd",
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "total": f"₱{total_budget['total'] or 0:,.0f}",
            "metrics": [
                {"label": "OBC Budget", "value": f"₱{total_budget['obc_total'] or 0:,.0f}"},
                {"label": "With Budget", "value": oobc_entries.exclude(budget_allocation__isnull=True).count()},
                {"label": "Pending", "value": oobc_entries.filter(budget_allocation__isnull=True).count()},
            ],
        },
        {
            "title": "Community Impact",
            "subtitle": f"OBC Communities Served",
            "icon": "fas fa-users",
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "total": unique_communities,
            "metrics": [
                {"label": "Direct", "value": total_communities_served},
                {"label": "Partners", "value": oobc_entries.exclude(supporting_organizations__isnull=True).distinct().count()},
                {"label": "Multi-Unit", "value": oobc_entries.filter(supporting_organizations__isnull=False).distinct().count()},
            ],
        },
        {
            "title": "Implementation Status",
            "subtitle": f"Progress Overview",
            "icon": "fas fa-chart-line",
            "gradient": "from-orange-500 via-orange-600 to-orange-700",
            "total": f"{oobc_entries.aggregate(avg=Avg('progress'))['avg'] or 0:.0f}%",
            "metrics": [
                {"label": "High (75%+)", "value": oobc_entries.filter(progress__gte=75).count()},
                {"label": "Medium", "value": oobc_entries.filter(progress__gte=50, progress__lt=75).count()},
                {"label": "Low (<50%)", "value": oobc_entries.filter(progress__lt=50).count()},
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
            "label": dict(MonitoringEntry.STATUS_CHOICES).get(item["status"], item["status"]),
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
    recent_updates = MonitoringUpdate.objects.filter(
        entry__category="oobc_ppa"
    ).select_related("entry", "created_by").order_by("-created_at")[:10]

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
    obc_year_qs = obc_entries.filter(
        Q(created_at__year=current_year)
    )

    # Statistics cards
    total_obc_requests = obc_entries.count()

    # Request status analysis
    pending_statuses = ["submitted", "under_review", "clarification"]
    in_progress_statuses = ["endorsed", "approved", "in_progress"]
    completed_requests = obc_entries.filter(request_status="completed").count()
    pending_requests = obc_entries.filter(request_status__in=pending_statuses).count()
    active_requests = obc_entries.filter(request_status__in=in_progress_statuses).count()

    # Priority analysis
    high_priority = obc_entries.filter(priority="high").count()
    urgent_priority = obc_entries.filter(priority="urgent").count()

    # Community analysis
    requesting_communities = obc_entries.exclude(submitted_by_community__isnull=True).values(
        'submitted_by_community__name'
    ).distinct().count()

    # Receiving organizations
    receiving_orgs = obc_entries.exclude(submitted_to_organization__isnull=True).values(
        'submitted_to_organization__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]

    stats_cards = [
        {
            "title": "Total OBC Requests",
            "subtitle": f"Community Proposals",
            "icon": "fas fa-file-signature",
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
            "gradient": "from-red-500 via-orange-500 to-yellow-500",
            "total": urgent_priority + high_priority,
            "metrics": [
                {"label": "Urgent", "value": urgent_priority},
                {"label": "High", "value": high_priority},
                {"label": "Standard", "value": obc_entries.filter(priority__in=["medium", "low"]).count()},
            ],
        },
        {
            "title": "Community Participation",
            "subtitle": f"Requesting Communities",
            "icon": "fas fa-mosque",
            "gradient": "from-green-500 via-emerald-500 to-teal-500",
            "total": requesting_communities,
            "metrics": [
                {"label": "Active", "value": obc_entries.filter(request_status__in=in_progress_statuses).values('submitted_by_community').distinct().count()},
                {"label": "Pending", "value": obc_entries.filter(request_status__in=pending_statuses).values('submitted_by_community').distinct().count()},
                {"label": "Completed", "value": obc_entries.filter(request_status="completed").values('submitted_by_community').distinct().count()},
            ],
        },
        {
            "title": "Response Rate",
            "subtitle": f"Processing Efficiency",
            "icon": "fas fa-tachometer-alt",
            "gradient": "from-purple-500 via-pink-500 to-rose-500",
            "total": f"{(completed_requests + active_requests) / max(total_obc_requests, 1) * 100:.0f}%",
            "metrics": [
                {"label": "Resolved", "value": completed_requests + active_requests},
                {"label": "Under Review", "value": obc_entries.filter(request_status="under_review").count()},
                {"label": "Awaiting", "value": obc_entries.filter(request_status="submitted").count()},
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
    recent_updates = MonitoringUpdate.objects.filter(
        entry__category="obc_request"
    ).select_related("entry", "created_by").order_by("-created_at")[:10]

    # Progress snapshot
    progress_snapshot = {
        'latest_update': obc_entries.aggregate(latest=Max("updated_at"))['latest'],
        'pending_review': pending_requests,
        'avg_response_days': 7  # This would be calculated from actual data
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
