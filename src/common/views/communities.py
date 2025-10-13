"""Views for OBC communities management screens."""

import json
from typing import Optional, Tuple
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma, naturaltime
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import (
    Case,
    F,
    IntegerField,
    OuterRef,
    Subquery,
    Sum,
    When,
)
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST

from ..forms import (
    MunicipalityCoverageForm,
    OBCCommunityForm,
    ProvinceCoverageForm,
)
from ..models import Barangay, Municipality, Province, Region
from ..services.enhanced_geocoding import enhanced_ensure_location_coordinates
from ..services.locations import build_location_data, get_object_centroid
from ..utils.permissions import has_oobc_management_access


DEFAULT_MAP_CENTER = (7.1907, 125.4553, 6)
PAGE_SIZE_OPTIONS = (10, 25, 50)


def _exclude_huc_provinces(queryset):
    """
    Filter out HUC (Highly Urbanized City) pseudo-provinces from a Province queryset.

    HUCs exist in the database as Province records for data integrity (so their
    single municipality can reference them), but should only appear in Municipal OBC
    views, NOT in Provincial OBC views.

    HUCs are identified by having "City" in their name or "(Huc)" suffix.

    Args:
        queryset: A Province QuerySet to filter

    Returns:
        QuerySet with HUC pseudo-provinces excluded
    """
    from django.db.models import Q

    return queryset.exclude(
        Q(name__icontains='City of') | Q(name__icontains='(Huc)')
    )


def _ensure_can_manage_communities(user):
    """
    Raise PermissionDenied if the user is limited to read-only access.

    MOA focal persons and staff accounts operate in a read-only mode for
    community records. Other authenticated users retain their existing
    permissions and downstream checks (e.g., MANA participants).
    """

    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication is required to manage communities.")

    if getattr(user, "is_moa_staff", False):
        raise PermissionDenied(
            "MOA focal persons have read-only access to community records."
        )


def _sanitize_filter_value(value: Optional[str]) -> Optional[str]:
    """Normalize GET parameters coming from selects that emit the string "None"."""

    if value is None:
        return None

    normalized = str(value).strip()
    if normalized.lower() in {"", "none", "null", "undefined"}:
        return None

    return normalized


def _sync_hierarchical_coverages(municipality):
    """Ensure municipality and province coverage records reflect barangay changes."""

    if municipality is None:
        return

    from communities.models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage

    coverage = MunicipalityCoverage.sync_for_municipality(municipality)
    province = municipality.province
    if province:
        ProvinceCoverage.sync_for_province(province)
    return coverage


def _to_float(value) -> Optional[float]:
    if value in {"", None}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _resolve_map_payload(
    *,
    primary_lat: Optional[float] = None,
    primary_lng: Optional[float] = None,
    primary_zoom: Optional[int] = None,
    barangay=None,
    municipality=None,
    province=None,
    region=None,
):
    """Select the best available coordinates for map rendering."""

    candidates: list[tuple[float, float, int]] = []

    lat = _to_float(primary_lat)
    lng = _to_float(primary_lng)
    zoom = primary_zoom if isinstance(primary_zoom, int) else _to_float(primary_zoom)
    if lat is not None and lng is not None:
        candidates.append((lat, lng, int(zoom) if zoom else 12))

    def add_candidate(source, zoom_level):
        if source is None:
            return
        lat_val, lng_val = get_object_centroid(source)
        if lat_val is None or lng_val is None:
            lat_val, lng_val, _, _ = enhanced_ensure_location_coordinates(source)
        if lat_val is None or lng_val is None:
            return
        candidates.append((lat_val, lng_val, zoom_level))

    if barangay is not None:
        add_candidate(barangay, 15)
        if municipality is None:
            municipality = getattr(barangay, "municipality", None)

    if municipality is not None:
        add_candidate(municipality, 12)
        if province is None:
            province = getattr(municipality, "province", None)

    if province is not None:
        add_candidate(province, 9)
        if region is None:
            region = getattr(province, "region", None)

    if region is not None:
        add_candidate(region, 7)

    if not candidates:
        return {
            "initial_lat": None,
            "initial_lng": None,
            "initial_zoom": None,
            "fallback_lat": DEFAULT_MAP_CENTER[0],
            "fallback_lng": DEFAULT_MAP_CENTER[1],
            "fallback_zoom": DEFAULT_MAP_CENTER[2],
            "has_location": False,
        }

    initial_lat, initial_lng, initial_zoom = candidates[0]

    return {
        "initial_lat": initial_lat,
        "initial_lng": initial_lng,
        "initial_zoom": initial_zoom,
        "fallback_lat": initial_lat,
        "fallback_lng": initial_lng,
        "fallback_zoom": initial_zoom,
        "has_location": True,
    }


def _resolve_page_size(
    request,
    param_name: str,
    *,
    default: int = PAGE_SIZE_OPTIONS[0],
) -> int:
    """Validate requested page size against allowed options."""

    raw_value = request.GET.get(param_name)
    if raw_value is None:
        return default
    try:
        parsed = int(raw_value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed in PAGE_SIZE_OPTIONS else default


def _build_querystring(
    params: dict,
    *,
    exclude: tuple[str, ...] = (),
    overrides: dict | None = None,
) -> str:
    """Compose a querystring while keeping empty values out of the output."""

    overrides = overrides or {}
    filtered: dict[str, str] = {}

    for key, value in params.items():
        if key in exclude or key in overrides:
            continue
        if value in {"", None}:
            continue
        filtered[key] = value

    for key, value in overrides.items():
        if value in {"", None}:
            continue
        filtered[key] = value

    return urlencode(filtered)


def _format_stat_value(value, default: str = "N/A") -> str:
    """Present human-friendly counts with comma separators."""

    if value in ("", None):
        return default
    try:
        return intcomma(int(value))
    except (TypeError, ValueError):
        return default


def _build_barangay_table(communities_page, *, can_manage: bool) -> dict:
    """Assemble data-table friendly rows for the barangay registry."""

    rows: list[dict] = []

    for community in communities_page:
        barangay = community.barangay
        municipality = getattr(barangay, "municipality", None)
        province = getattr(municipality, "province", None)
        region = getattr(province, "region", None)

        # Barangay name and ID (icon now in template first column)
        barangay_name_html = format_html(
            "<div class='space-y-0.5'>"
            "<div class='text-sm font-semibold text-gray-900'>{}</div>"
            "{}"
            "</div>",
            barangay.name,
            (
                format_html(
                    "<div class='text-xs text-gray-500'>ID: {}</div>", community.obc_id
                )
                if community.obc_id
                else ""
            ),
        )

        location_parts = []
        if municipality:
            location_parts.append(
                format_html(
                    "<div class='text-sm font-medium text-gray-900'>{}</div>",
                    municipality.name,
                )
            )
        if province:
            location_parts.append(
                format_html(
                    "<div class='text-sm text-gray-700'>{}</div>", province.name
                )
            )
        if region:
            location_parts.append(
                format_html(
                    "<div class='text-xs text-gray-500'>Region {} · {}</div>",
                    region.code or "—",
                    region.name,
                )
            )
        location_html = format_html(
            "<div class='space-y-0.5'>{}</div>",
            mark_safe("".join(location_parts)) if location_parts else "—",
        )

        snapshot_html = format_html(
            "<div class='space-y-1 text-sm text-gray-700'>"
            "<div><span class='font-semibold text-gray-900'>Est. OBC Population:</span> {}</div>"
            "<div><span class='font-semibold text-gray-900'>Barangay Population:</span> {}</div>"
            "<div><span class='font-semibold text-gray-900'>Households:</span> {}</div>"
            "<div><span class='font-semibold text-gray-900'>Stakeholders tracked:</span> {}</div>"
            "</div>",
            _format_stat_value(community.estimated_obc_population),
            _format_stat_value(community.total_barangay_population),
            _format_stat_value(community.households),
            _format_stat_value(getattr(community, "stakeholder_count", 0), default="0"),
        )

        rows.append(
            {
                "cells": [
                    {"content": barangay_name_html},
                    {"content": location_html},
                    {"content": snapshot_html},
                ],
                "view_url": reverse("communities:communities_view", args=[community.id]),
                "edit_url": reverse("communities:communities_edit", args=[community.id]),
                "delete_preview_url": reverse(
                    "communities:communities_delete", args=[community.id]
                ),
                "delete_message": (
                    "Delete this barangay OBC record? You will be able to review "
                    "details before confirming."
                ),
            }
        )

    return {
        "rows": rows,
        "show_actions": can_manage,
    }


@login_required
def communities_home(request):
    """OBC Communities module home page."""
    from django.db.models import Avg, Count, Q

    from communities.models import (
        CommunityInfrastructure,
        MunicipalityCoverage,
        OBCCommunity,
        ProvinceCoverage,
        Stakeholder,
    )

    communities = OBCCommunity.objects.select_related(
        "barangay__municipality__province__region"
    ).annotate(stakeholder_count=Count("stakeholders"))

    municipality_coverages = MunicipalityCoverage.objects.select_related(
        "municipality__province__region"
    )

    province_coverages = ProvinceCoverage.objects.select_related("province__region")

    vulnerable_sectors = communities.aggregate(
        total_women=Sum("women_count"),
        total_solo_parents=Sum("solo_parents_count"),
        total_pwd=Sum("pwd_count"),
        total_farmers=Sum("farmers_count"),
        total_fisherfolk=Sum("fisherfolk_count"),
        total_unemployed=Sum("unemployed_count"),
        total_indigenous_peoples=Sum("indigenous_peoples_count"),
        total_idps=Sum("idps_count"),
        total_migrants_transients=Sum("migrants_transients_count"),
        total_csos=Sum("csos_count"),
        total_associations=Sum("associations_count"),
        total_peoples_organizations=Sum("number_of_peoples_organizations"),
    )

    infrastructure_stats = (
        CommunityInfrastructure.objects.filter(
            availability_status__in=["limited", "poor", "none"]
        )
        .values("infrastructure_type")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    unemployment_rates = (
        communities.values("unemployment_rate")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    ethnolinguistic_groups = (
        communities.exclude(primary_ethnolinguistic_group__isnull=True)
        .exclude(primary_ethnolinguistic_group="")
        .values("primary_ethnolinguistic_group")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    stakeholder_stats = Stakeholder.objects.values("stakeholder_type").annotate(
        count=Count("id")
    )

    province_performance = (
        municipality_coverages.values("municipality__province__name")
        .annotate(
            communities_count=Sum("total_obc_communities"),
            population=Sum("estimated_obc_population"),
        )
        .order_by("-communities_count")[:5]
    )

    # Calculate totals for the new stat cards
    # Include barangay populations + non-auto-synced municipal populations to avoid double-counting
    barangay_population = (
        communities.aggregate(total=Sum("estimated_obc_population"))["total"] or 0
    )
    municipal_population = (
        municipality_coverages.filter(auto_sync=False).aggregate(
            total=Sum("estimated_obc_population")
        )["total"]
        or 0
    )
    total_obc_population = barangay_population + municipal_population
    total_barangay_obcs = communities.count()
    total_municipal_obcs = municipality_coverages.count()

    # Calculate total provincial OBCs from all three sources
    province_ids = set(
        communities.values_list("barangay__municipality__province_id", flat=True)
    )
    province_ids.update(
        municipality_coverages.values_list("municipality__province_id", flat=True)
    )
    province_ids.update(province_coverages.values_list("province_id", flat=True))
    province_ids.discard(None)
    # Exclude HUC pseudo-provinces from Provincial OBC count
    provincial_obcs_qs = Province.objects.filter(pk__in=province_ids)
    provincial_obcs_qs = _exclude_huc_provinces(provincial_obcs_qs)
    total_provincial_obcs = provincial_obcs_qs.count()

    stats = {
        "communities": {
            "total": communities.count(),
            "active": communities.filter(is_active=True).count(),
            "total_population": communities.aggregate(
                total=Sum("estimated_obc_population")
            )["total"]
            or 0,
            "total_households": communities.aggregate(total=Sum("households"))["total"]
            or 0,
            "by_region": communities.values(
                "barangay__municipality__province__region__name"
            )
            .annotate(count=Count("id"))
            .order_by("-count"),
            "recent": communities.order_by("-updated_at", "-created_at")[:10],
            "unemployment_rates": unemployment_rates,
            "with_madrasah": communities.filter(madrasah_count__gt=0).count(),
            "with_mosque": communities.filter(mosques_count__gt=0).count(),
            # New statistics for the requested stat cards
            "total_obc_population_database": total_obc_population,
            "total_barangay_obcs_database": total_barangay_obcs,
            "total_municipal_obcs_database": total_municipal_obcs,
            "total_provincial_obcs_database": total_provincial_obcs,
        },
        "vulnerable_sectors": vulnerable_sectors,
        "infrastructure_needs": infrastructure_stats,
        "ethnolinguistic_groups": ethnolinguistic_groups,
        "poverty_levels": communities.values("estimated_poverty_incidence")
        .annotate(count=Count("id"))
        .exclude(estimated_poverty_incidence="")
        .order_by("estimated_poverty_incidence"),
        "municipalities": {
            "total": municipality_coverages.count(),
            "total_population": municipality_coverages.aggregate(
                total=Sum("estimated_obc_population")
            )["total"]
            or 0,
            "total_obc_communities": municipality_coverages.aggregate(
                total=Sum("total_obc_communities")
            )["total"]
            or 0,
            "by_region": municipality_coverages.values(
                "municipality__province__region__name"
            )
            .annotate(count=Count("id"))
            .order_by("-count"),
            "recent": municipality_coverages.order_by("-updated_at", "-created_at")[
                :10
            ],
            "top_performers": province_performance,
        },
        "provinces": {
            "total": province_coverages.count(),
            "recent": province_coverages.order_by("-updated_at", "-created_at")[:10],
        },
        "stakeholders": stakeholder_stats,
    }

    context = {
        "stats": stats,
        "communities": communities[:20],
        "municipality_coverages": municipality_coverages[:20],
        "province_coverages": province_coverages[:20],
        "show_geographic_links": not getattr(request.user, "is_moa_staff", False),
    }
    return render(request, "communities/communities_home.html", context)


@login_required
def communities_add(request):
    """Add new community page."""
    _ensure_can_manage_communities(request.user)

    from communities.models import OBCCommunity

    if request.method == "POST":
        form = OBCCommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.save()
            _sync_hierarchical_coverages(community.barangay.municipality)
            messages.success(
                request,
                f'Community "{community.barangay.name}" has been successfully added.',
            )
            return redirect("communities:communities_manage")
    else:
        form = OBCCommunityForm()

    recent_communities = OBCCommunity.objects.order_by("-created_at")[:5]
    barangays = Barangay.objects.select_related(
        "municipality__province__region"
    ).order_by("municipality__province__region__name", "municipality__name", "name")

    context = {
        "form": form,
        "recent_communities": recent_communities,
        "barangays": barangays,
        "location_data": build_location_data(),
        "show_barangay_field": True,
        "page_title": "Add Barangay OBC",
        "breadcrumb_label": "Add Barangay OBC",
        "page_subtitle": "Register a barangay-level OBC profile with detailed demographic, socio-economic, and services data.",
        "form_heading": "Barangay OBC Form",
    }
    return render(request, "communities/communities_add.html", context)


@login_required
def communities_add_municipality(request):
    """Record a municipality or city with Bangsamoro communities."""
    _ensure_can_manage_communities(request.user)

    from communities.models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage

    if request.method == "POST":
        form = MunicipalityCoverageForm(request.POST)
        if form.is_valid():
            coverage = form.save(commit=False)
            coverage.created_by = (
                request.user if request.user.is_authenticated else None
            )
            coverage.updated_by = coverage.created_by
            coverage.save()
            coverage.refresh_from_communities()
            messages.success(
                request,
                f'Municipality/City "{coverage.municipality.name}" has been added to the Bangsamoro coverage map.',
            )
            return redirect("communities:communities_manage")
    else:
        form = MunicipalityCoverageForm()

    recent_coverages = MunicipalityCoverage.objects.select_related(
        "municipality__province__region"
    ).order_by("-created_at")[:5]

    context = {
        "form": form,
        "recent_communities": [],
        "location_data": build_location_data(include_barangays=False),
        "show_barangay_field": False,
        "page_title": "Add Municipal / City OBC",
        "breadcrumb_label": "Add Municipal / City OBC",
        "page_subtitle": "Capture municipality- or city-wide OBC data that can be disaggregated to barangays later.",
        "form_heading": "Municipality OBC Form",
        "recent_coverages": recent_coverages,
    }
    return render(request, "communities/communities_add.html", context)


@login_required
def communities_add_province(request):
    """Record a province-level Bangsamoro coverage profile."""
    _ensure_can_manage_communities(request.user)

    from communities.models import ProvinceCoverage

    if request.method == "POST":
        form = ProvinceCoverageForm(request.POST)
        if form.is_valid():
            coverage = form.save(commit=False)
            coverage.created_by = (
                request.user if request.user.is_authenticated else None
            )
            coverage.updated_by = coverage.created_by
            coverage.save()
            coverage.refresh_from_municipalities()
            messages.success(
                request,
                f'Province "{coverage.province.name}" has been added to the Bangsamoro coverage map.',
            )
            return redirect("communities:communities_manage_provincial")
    else:
        form = ProvinceCoverageForm()

    recent_coverages = ProvinceCoverage.objects.select_related(
        "province__region"
    ).order_by("-created_at")[:5]

    context = {
        "form": form,
        "recent_communities": [],
        "recent_coverages": recent_coverages,
        "location_data": build_location_data(include_barangays=False),
        "show_barangay_field": False,
        "page_title": "Add Provincial OBC",
        "breadcrumb_label": "Add Provincial OBC",
        "page_subtitle": "Capture province-level Bangsamoro coverage data aggregated from constituent municipalities.",
        "form_heading": "Provincial OBC Form",
    }
    return render(request, "communities/communities_add.html", context)


@login_required
def communities_manage(request):
    """Manage communities page."""
    can_manage_communities = has_oobc_management_access(request.user)

    from django.db.models import Count, Q

    from communities.models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage

    communities = (
        OBCCommunity.objects.select_related("barangay__municipality__province__region")
        .annotate(stakeholder_count=Count("stakeholders"))
        .order_by("barangay__name")
    )

    municipality_coverages = MunicipalityCoverage.objects.select_related(
        "municipality__province__region"
    ).order_by(
        "municipality__province__region__name",
        "municipality__province__name",
        "municipality__name",
    )

    province_coverages = ProvinceCoverage.objects.select_related(
        "province__region"
    ).order_by("province__region__name", "province__name")

    region_filter = _sanitize_filter_value(request.GET.get("region"))
    province_filter = _sanitize_filter_value(request.GET.get("province"))
    municipality_filter = _sanitize_filter_value(request.GET.get("municipality"))
    search_query = _sanitize_filter_value(request.GET.get("search"))

    if region_filter:
        communities = communities.filter(
            barangay__municipality__province__region__id=region_filter
        )
        municipality_coverages = municipality_coverages.filter(
            municipality__province__region__id=region_filter
        )
        province_coverages = province_coverages.filter(
            province__region__id=region_filter
        )

    if province_filter:
        communities = communities.filter(
            barangay__municipality__province__id=province_filter
        )
        municipality_coverages = municipality_coverages.filter(
            municipality__province__id=province_filter
        )
        province_coverages = province_coverages.filter(
            province__id=province_filter
        )

    if municipality_filter:
        communities = communities.filter(barangay__municipality__id=municipality_filter)
        municipality_coverages = municipality_coverages.filter(
            municipality__id=municipality_filter
        )

    if search_query:
        communities = communities.filter(
            Q(barangay__name__icontains=search_query)
            | Q(barangay__municipality__name__icontains=search_query)
            | Q(barangay__municipality__province__name__icontains=search_query)
            | Q(barangay__municipality__province__region__name__icontains=search_query)
        )
        municipality_coverages = municipality_coverages.filter(
            Q(municipality__name__icontains=search_query)
            | Q(municipality__province__name__icontains=search_query)
            | Q(municipality__province__region__name__icontains=search_query)
            | Q(key_barangays__icontains=search_query)
        )

    regions = Region.objects.filter(is_active=True).order_by("name")

    # Get provinces and prepare client-side filtering metadata
    from ..models import Province

    base_provinces_qs = (
        Province.objects.select_related("region")
        .filter(is_active=True, region__is_active=True)
        .order_by("region__name", "name")
    )
    # Exclude HUC pseudo-provinces from filtering dropdowns
    base_provinces_qs = _exclude_huc_provinces(base_provinces_qs)

    provinces = base_provinces_qs
    if region_filter:
        provinces = provinces.filter(region__id=region_filter)

    province_options = [
        {
            "id": str(province.id),
            "name": province.name,
            "region_id": str(province.region_id),
            "region_code": province.region.code,
        }
        for province in base_provinces_qs
    ]

    province_options_json = json.dumps(province_options, cls=DjangoJSONEncoder)

    base_municipalities_qs = (
        Municipality.objects.select_related("province__region")
        .filter(
            is_active=True,
            province__is_active=True,
            province__region__is_active=True,
        )
        .order_by("province__name", "name")
    )

    municipalities = base_municipalities_qs
    if region_filter:
        municipalities = municipalities.filter(province__region__id=region_filter)
    if province_filter:
        municipalities = municipalities.filter(province__id=province_filter)

    municipality_options = [
        {
            "id": str(municipality.id),
            "name": municipality.name,
            "province_id": str(municipality.province_id),
            "province_name": municipality.province.name,
            "region_id": str(municipality.province.region_id),
        }
        for municipality in base_municipalities_qs
    ]

    municipality_options_json = json.dumps(municipality_options, cls=DjangoJSONEncoder)

    total_barangay_obcs = communities.count()
    total_barangay_population = (
        communities.aggregate(total=Sum("estimated_obc_population"))["total"] or 0
    )
    total_municipality_obcs = municipality_coverages.count()
    total_municipality_population = (
        municipality_coverages.aggregate(total=Sum("estimated_obc_population"))["total"]
        or 0
    )
    total_municipality_communities = (
        municipality_coverages.aggregate(total=Sum("total_obc_communities"))["total"]
        or 0
    )
    total_province_obcs = province_coverages.count()

    barangay_page_size = _resolve_page_size(request, "barangay_page_size")
    municipality_page_size = _resolve_page_size(request, "municipality_page_size")

    barangay_page_number = request.GET.get("barangay_page") or 1
    municipality_page_number = request.GET.get("municipality_page") or 1

    communities_paginator = Paginator(communities, barangay_page_size)
    communities_page = communities_paginator.get_page(barangay_page_number)

    municipality_paginator = Paginator(municipality_coverages, municipality_page_size)
    municipality_page = municipality_paginator.get_page(municipality_page_number)

    request_params = request.GET.dict()
    barangay_base_querystring = _build_querystring(
        request_params,
        exclude=("barangay_page",),
    )
    municipality_base_querystring = _build_querystring(
        request_params,
        exclude=("municipality_page",),
    )

    barangay_table = _build_barangay_table(
        communities_page,
        can_manage=can_manage_communities,
    )

    stat_cards = [
        {
            "title": "Total Barangay OBCs in the Database",
            "value": total_barangay_obcs,
            "icon": "fas fa-users",
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "text_color": "text-blue-100",
            "icon_color": "text-blue-600",
        },
        {
            "title": "Total OBC Population from Barangays",
            "value": total_barangay_population,
            "icon": "fas fa-user-friends",
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "text_color": "text-emerald-100",
            "icon_color": "text-emerald-600",
        },
        {
            "title": "Total Municipalities OBCs in the Database",
            "value": total_municipality_obcs,
            "icon": "fas fa-city",
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "text_color": "text-purple-100",
            "icon_color": "text-purple-600",
        },
        {
            "title": "Total Provincial OBCs in the Database",
            "value": total_province_obcs,
            "icon": "fas fa-map-marked-alt",
            "gradient": "from-amber-500 via-amber-600 to-amber-700",
            "text_color": "text-amber-100",
            "icon_color": "text-amber-600",
        },
    ]

    lg_columns = 4 if len(stat_cards) >= 4 else 3
    stat_cards_grid_class = (
        f"mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-{lg_columns} gap-6"
    )

    page_title = "Manage Barangay OBC"
    if can_manage_communities:
        page_description = (
            "View, edit, and manage barangay-level Bangsamoro coverage data."
        )
    else:
        page_description = "Review barangay-level Bangsamoro coverage data."

    hero_actions = []
    if can_manage_communities:
        hero_actions.append(
            {
                "href": reverse("communities:communities_add"),
                "label": "Add barangay OBC",
                "icon": "fas fa-plus",
                "variant": "primary",
            }
        )
    hero_actions.append(
        {
            "href": reverse("communities:communities_manage_municipal"),
            "label": "Go to municipal view",
            "icon": "fas fa-landmark",
            "variant": "ghost",
        }
    )

    hero_config = {
        "badge_icon": "fas fa-database",
        "badge_text": "OBC Data - Barangay",
        "icon": "fas fa-map",
        "title": page_title,
        "subtitle": page_description,
        "level_summary": (
            "Barangay-level coverage consolidates community rosters, local leadership,"
            " and frontline service readiness for every OBC community in BARMM."
        ),
        "meta_cards": [],
        "metrics": [],
        "actions": hero_actions,
    }

    context = {
        "communities": communities_page,
        "regions": regions,
        "provinces": provinces,
        "current_region": region_filter,
        "current_province": province_filter,
        "search_query": search_query,
        "province_options_json": province_options_json,
        "total_communities": total_barangay_obcs,
        "total_population": total_barangay_population,
        "municipality_coverages": municipality_page,
        "total_municipality_coverages": total_municipality_obcs,
        "total_municipality_population": total_municipality_population,
        "total_municipality_communities": total_municipality_communities,
        "stat_cards": stat_cards,
        "stat_cards_grid_class": stat_cards_grid_class,
        "barangay_page_size": barangay_page_size,
        "barangay_page_size_options": PAGE_SIZE_OPTIONS,
        "barangay_total_pages": max(communities_page.paginator.num_pages, 1),
        "municipality_page_size": municipality_page_size,
        "municipality_page_size_options": PAGE_SIZE_OPTIONS,
        "municipality_total_pages": max(municipality_page.paginator.num_pages, 1),
        "barangay_base_querystring": barangay_base_querystring,
        "municipality_base_querystring": municipality_base_querystring,
        "page_title": page_title,
        "page_description": page_description,
        "hero_config": hero_config,
        "municipalities": municipalities,
        "current_municipality": municipality_filter,
        "municipality_options_json": municipality_options_json,
        "can_manage_communities": can_manage_communities,
        "barangay_table": barangay_table,
    }
    template_name = "communities/communities_manage.html"
    if request.headers.get("HX-Request"):
        template_name = "communities/partials/barangay_manage_results.html"
    return render(request, template_name, context)


@login_required
def communities_manage_municipal(request):
    """Manage municipality-level OBC coverage."""
    can_manage_communities = has_oobc_management_access(request.user)

    from django.db.models import Count, Q

    from communities.models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage

    show_archived = request.GET.get("archived") == "1"

    base_manager = (
        MunicipalityCoverage.all_objects
        if show_archived
        else MunicipalityCoverage.objects
    )

    coverages = base_manager.select_related(
        "municipality__province__region",
        "created_by",
        "updated_by",
    ).order_by(
        "municipality__province__region__name",
        "municipality__province__name",
        "municipality__name",
    )

    coverages = coverages.filter(
        municipality__is_active=True,
        municipality__province__is_active=True,
        municipality__province__region__is_active=True,
    )

    if show_archived:
        coverages = coverages.filter(is_deleted=True)

    region_filter = _sanitize_filter_value(request.GET.get("region"))
    province_filter = _sanitize_filter_value(request.GET.get("province"))
    search_query = _sanitize_filter_value(request.GET.get("search"))

    if region_filter:
        coverages = coverages.filter(municipality__province__region__id=region_filter)

    if province_filter:
        coverages = coverages.filter(municipality__province__id=province_filter)

    if search_query:
        coverages = coverages.filter(
            Q(municipality__name__icontains=search_query)
            | Q(municipality__province__name__icontains=search_query)
            | Q(municipality__province__region__name__icontains=search_query)
            | Q(key_barangays__icontains=search_query)
        )

    regions = Region.objects.filter(is_active=True).order_by("name")

    # Get provinces and prepare client-side filtering metadata
    from ..models import Province

    base_provinces_qs = (
        Province.objects.select_related("region")
        .filter(is_active=True, region__is_active=True)
        .order_by("region__name", "name")
    )
    # Exclude HUC pseudo-provinces from filtering dropdowns
    base_provinces_qs = _exclude_huc_provinces(base_provinces_qs)

    provinces = base_provinces_qs
    if region_filter:
        provinces = provinces.filter(region__id=region_filter)

    province_options = [
        {
            "id": str(province.id),
            "name": province.name,
            "region_id": str(province.region_id),
            "region_code": province.region.code,
        }
        for province in base_provinces_qs
    ]

    province_options_json = json.dumps(province_options, cls=DjangoJSONEncoder)

    total_coverages = coverages.count()
    barangay_population_subquery = (
        OBCCommunity.objects.filter(barangay__municipality=OuterRef("municipality"))
        .values("barangay__municipality")
        .annotate(total=Sum("estimated_obc_population"))
        .values("total")
    )

    coverages_with_population = coverages.annotate(
        barangay_population=Coalesce(
            Subquery(barangay_population_subquery, output_field=IntegerField()), 0
        )
    )

    total_population = (
        coverages_with_population.aggregate(
            total=Sum(
                Case(
                    When(
                        estimated_obc_population__isnull=False,
                        then="estimated_obc_population",
                    ),
                    default=F("barangay_population"),
                    output_field=IntegerField(),
                )
            )
        )["total"]
        or 0
    )
    total_communities = (
        coverages.aggregate(total=Sum("total_obc_communities"))["total"] or 0
    )
    auto_synced = coverages.filter(auto_sync=True).count()
    manual_updates = coverages.filter(auto_sync=False).count()

    stats = {
        "total_coverages": total_coverages,
        "total_population": total_population,
        "total_communities": total_communities,
        "auto_synced": auto_synced,
        "manual": manual_updates,
    }

    stat_cards = [
        {
            "title": (
                "Total Municipal OBCs in the Database"
                if not show_archived
                else "Total Archived Municipal OBCs"
            ),
            "value": total_coverages,
            "icon": "fas fa-city",
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "text_color": "text-blue-100",
            "icon_color": "text-blue-600",
        },
        {
            "title": (
                "Total OBC Population from the Municipalities"
                if not show_archived
                else "Archived OBC Population Total"
            ),
            "value": total_population,
            "icon": "fas fa-users",
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "text_color": "text-emerald-100",
            "icon_color": "text-emerald-600",
        },
        {
            "title": "Auto-Synced Municipalities",
            "value": auto_synced,
            "icon": "fas fa-sync-alt",
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "text_color": "text-purple-100",
            "icon_color": "text-purple-600",
        },
        {
            "title": "Manually Updated Municipalities",
            "value": manual_updates,
            "icon": "fas fa-edit",
            "gradient": "from-orange-500 via-orange-600 to-orange-700",
            "text_color": "text-orange-100",
            "icon_color": "text-orange-500",
        },
    ]

    stat_cards_grid_class = "mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"

    if show_archived:
        page_title = "Archived Municipal OBCs"
        page_description = (
            "Review archived municipality-level Bangsamoro coverage data."
        )
    else:
        page_title = "Manage Municipal OBC"
        if can_manage_communities:
            page_description = (
                "View, edit, and manage municipality-level Bangsamoro coverage data."
            )
        else:
            page_description = "Review municipality-level Bangsamoro coverage data."

    badge_text = (
        "OBC Data - Municipal (Archived)" if show_archived else "OBC Data - Municipal"
    )

    hero_actions = [
        {
            "href": (
                reverse("communities:communities_manage_municipal")
                if show_archived
                else f"{reverse('communities:communities_manage_municipal')}?archived=1"
            ),
            "label": (
                "Back to active records" if show_archived else "View archived records"
            ),
            "icon": "fas fa-list" if show_archived else "fas fa-archive",
            "variant": "secondary",
        }
    ]
    if can_manage_communities:
        hero_actions.append(
            {
                "href": reverse("communities:communities_add_municipality"),
                "label": "Add municipal OBC",
                "icon": "fas fa-plus",
                "variant": "primary",
            }
        )
    hero_actions.append(
        {
            "href": reverse("communities:communities_manage_provincial"),
            "label": "Go to provincial view",
            "icon": "fas fa-flag",
            "variant": "ghost",
        }
    )

    hero_config = {
        "badge_icon": "fas fa-landmark",
        "badge_text": badge_text,
        "icon": "fas fa-city",
        "title": page_title,
        "subtitle": page_description,
        "level_summary": (
            "Municipal-level coverage aggregates barangay submissions to map OBC"
            " presence, staffing, and active programs across each LGU."
        ),
        "meta_cards": [],
        "metrics": [],
        "actions": hero_actions,
    }

    page_size = _resolve_page_size(request, "municipality_page_size")
    page_number = request.GET.get("municipality_page") or 1

    paginator = Paginator(coverages, page_size)
    coverages_page = paginator.get_page(page_number)

    municipality_table_headers = [
        {"label": "", "class": "w-14"},  # Icon column (no label)
        {"label": "Municipality/City", "class": "flex-1 min-w-[140px]"},
        {"label": "Province & Region", "class": "flex-1 min-w-[140px]"},
        {"label": "Coverage Snapshot", "class": "flex-1 min-w-[180px]"},
        {"label": "Top 5 Barangays", "class": "flex-1 min-w-[200px]"},
        {"label": "Sync Mode", "class": "w-32"},
    ]

    municipality_table_rows: list[dict] = []
    for coverage in coverages_page:
        municipality = getattr(coverage, "municipality", None)
        province = getattr(municipality, "province", None)
        region = getattr(province, "region", None)

        municipality_type = (
            municipality.get_municipality_type_display()
            if municipality and hasattr(municipality, "get_municipality_type_display")
            else "—"
        )

        # Municipality name and type (icon is now in template)
        municipality_name_html = format_html(
            "<div class='space-y-0.5'>"
            "<div class='text-sm font-semibold text-gray-900'>{}</div>"
            "<div class='text-xs text-gray-500'>{}</div>"
            "</div>",
            municipality.name if municipality else "—",
            municipality_type,
        )

        province_name = province.name if province else "—"
        region_code = region.code if region else "—"
        region_name = region.name if region else "—"
        province_html = format_html(
            "<div class='space-y-1'>"
            "<div class='font-medium text-gray-900'>{}</div>"
            "<div class='text-xs text-gray-500'>Region {} · {}</div>"
            "</div>",
            province_name,
            region_code,
            region_name,
        )

        total_obc = coverage.total_obc_communities or 0
        estimated_population = coverage.estimated_obc_population
        total_population = coverage.total_barangay_population or 0
        households = coverage.households or 0
        snapshot_parts = [
            format_html(
                "<div class='text-sm font-semibold text-gray-900'>{} barangay OBCs tracked</div>",
                intcomma(total_obc),
            ),
            format_html(
                "<div class='text-xs text-gray-500'>Est. OBC Population: {}</div>",
                (
                    intcomma(estimated_population)
                    if estimated_population is not None
                    else "—"
                ),
            ),
            format_html(
                "<div class='text-xs text-gray-500'>Total Population: {}</div>",
                intcomma(total_population),
            ),
            format_html(
                "<div class='text-xs text-gray-500'>Households: {}</div>",
                intcomma(households),
            ),
        ]
        snapshot_html = format_html(
            "<div class='space-y-1'>{}</div>",
            format_html_join("", "{}", ((part,) for part in snapshot_parts)),
        )

        # Top 5 Barangays column (by Estimated OBC Population)
        top_barangays = OBCCommunity.objects.filter(
            barangay__municipality=municipality,
            estimated_obc_population__isnull=False
        ).order_by('-estimated_obc_population').values_list(
            'barangay__name', flat=True
        )[:5]

        if top_barangays:
            barangay_names = ", ".join(top_barangays)
            key_barangays_html = format_html(
                "<div class='text-sm text-gray-700 break-words whitespace-normal'>{}</div>",
                barangay_names,
            )
        else:
            key_barangays_html = format_html(
                "<div class='text-sm text-gray-400 italic'>No OBC Population recorded</div>"
            )

        if coverage.auto_sync:
            sync_html = format_html(
                "<span class='inline-flex items-center gap-1 rounded-full border border-emerald-200 "
                "bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700'>"
                "<i class='fas fa-sync'></i>"
                "<span>Auto-sync</span>"
                "</span>"
            )
        else:
            sync_html = format_html(
                "<span class='inline-flex items-center gap-1 rounded-full border border-amber-200 "
                "bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700'>"
                "<i class='fas fa-hand-paper'></i>"
                "<span>Manual</span>"
                "</span>"
            )

        view_url_base = reverse("communities:communities_view_municipal", args=[coverage.pk])
        view_url = f"{view_url_base}?archived=1" if show_archived else view_url_base

        edit_url = None
        delete_preview_url = None
        delete_message = None
        restore_url = None
        if can_manage_communities:
            if show_archived:
                restore_url = reverse(
                    "communities:communities_restore_municipal", args=[coverage.pk]
                )
            else:
                edit_url = reverse(
                    "communities:communities_edit_municipal", args=[coverage.pk]
                )
                delete_preview_url = f"{view_url_base}?review_delete=1"
                delete_message = (
                    "Are you sure you want to delete this municipal OBC coverage? "
                    "You will review the details before final confirmation."
                )

        row = {
            "cells": [
                {"content": municipality_name_html},
                {"content": province_html},
                {"content": snapshot_html},
                {"content": key_barangays_html},
                {"content": sync_html},
            ],
            "view_url": view_url,
        }
        if edit_url:
            row["edit_url"] = edit_url
        if delete_preview_url:
            row["delete_preview_url"] = delete_preview_url
        if delete_message:
            row["delete_message"] = delete_message
        if restore_url:
            row["restore_url"] = restore_url

        municipality_table_rows.append(row)

    request_params = request.GET.dict()
    coverage_base_querystring = _build_querystring(
        request_params,
        exclude=("municipality_page",),
    )

    context = {
        "coverages": coverages_page,
        "regions": regions,
        "provinces": provinces,
        "current_region": region_filter,
        "current_province": province_filter,
        "search_query": search_query,
        "province_options_json": province_options_json,
        "stats": stats,
        "stat_cards": stat_cards,
        "stat_cards_grid_class": stat_cards_grid_class,
        "show_archived": show_archived,
        "page_title": page_title,
        "page_description": page_description,
        "hero_config": hero_config,
        "municipality_page_size": page_size,
        "municipality_page_size_options": PAGE_SIZE_OPTIONS,
        "municipality_base_querystring": coverage_base_querystring,
        "municipality_total_pages": max(coverages_page.paginator.num_pages, 1),
        "can_manage_communities": can_manage_communities,
        "municipality_table": {
            "headers": municipality_table_headers,
            "rows": municipality_table_rows,
            "show_actions": can_manage_communities,
            "actions_width": "w-44",
        },
    }
    template_name = "communities/municipal_manage.html"
    if request.headers.get("HX-Request"):
        template_name = "communities/partials/municipal_manage_results.html"
    return render(request, template_name, context)


@login_required
def communities_manage_provincial(request):
    """Manage province-level OBC coverage."""
    can_manage_communities = has_oobc_management_access(request.user)

    from django.db.models import Q

    from communities.models import MunicipalityCoverage, ProvinceCoverage

    show_archived = request.GET.get("archived") == "1"

    base_manager = (
        ProvinceCoverage.all_objects if show_archived else ProvinceCoverage.objects
    )

    coverages = base_manager.select_related(
        "province__region",
        "created_by",
        "updated_by",
    ).order_by(
        "province__region__name",
        "province__name",
    )

    coverages = coverages.filter(
        province__is_active=True,
        province__region__is_active=True,
    )

    # Exclude HUC pseudo-provinces from Provincial OBC display
    # HUCs should only appear in Municipal OBC views
    from django.db.models import Q
    coverages = coverages.exclude(
        Q(province__name__icontains='City of') | Q(province__name__icontains='(Huc)')
    )

    if show_archived:
        coverages = coverages.filter(is_deleted=True)

    # MANA Participant access control
    is_mana_participant = (
        request.user.has_perm("mana.can_access_regional_mana")
        and not request.user.is_staff
        and not request.user.is_superuser
    )

    participant_region = None
    if is_mana_participant:
        # Get the participant's account and region
        try:
            from mana.models import WorkshopParticipantAccount

            participant_account = WorkshopParticipantAccount.objects.select_related(
                "province__region"
            ).get(user=request.user)
            participant_region = participant_account.province.region

            # Filter to only show Provincial OBCs created by this participant
            coverages = coverages.filter(created_by=request.user)

            # Also filter by their region
            coverages = coverages.filter(province__region=participant_region)
        except WorkshopParticipantAccount.DoesNotExist:
            # If no participant account, show nothing
            coverages = coverages.none()

    region_filter = _sanitize_filter_value(request.GET.get("region"))
    province_filter = _sanitize_filter_value(request.GET.get("province"))
    search_query = _sanitize_filter_value(request.GET.get("search"))

    if region_filter:
        coverages = coverages.filter(province__region__id=region_filter)

    if province_filter:
        coverages = coverages.filter(province__id=province_filter)

    if search_query:
        coverages = coverages.filter(
            Q(province__name__icontains=search_query)
            | Q(province__region__name__icontains=search_query)
            | Q(province__region__code__icontains=search_query)
            | Q(key_municipalities__icontains=search_query)
        )

    regions = Region.objects.filter(is_active=True).order_by("name")

    # For MANA participants, only show their region
    if is_mana_participant and participant_region:
        regions = regions.filter(id=participant_region.id)

    base_provinces_qs = (
        Province.objects.select_related("region")
        .filter(is_active=True, region__is_active=True)
        .order_by("region__name", "name")
    )

    # For MANA participants, only show provinces in their region
    if is_mana_participant and participant_region:
        base_provinces_qs = base_provinces_qs.filter(region=participant_region)

    provinces = base_provinces_qs
    if region_filter:
        provinces = provinces.filter(region__id=region_filter)

    province_options = [
        {
            "id": str(province.id),
            "name": province.name,
            "region_id": str(province.region_id),
            "region_code": province.region.code,
        }
        for province in base_provinces_qs
    ]

    province_options_json = json.dumps(province_options, cls=DjangoJSONEncoder)

    total_coverages = coverages.count()
    total_population = (
        coverages.aggregate(total=Sum("estimated_obc_population"))["total"] or 0
    )
    total_municipalities = (
        coverages.aggregate(total=Sum("total_municipalities"))["total"] or 0
    )
    total_barangay_communities = (
        coverages.aggregate(total=Sum("total_obc_communities"))["total"] or 0
    )
    auto_synced = coverages.filter(auto_sync=True).count()
    manual_updates = coverages.filter(auto_sync=False).count()

    stats = {
        "total_coverages": total_coverages,
        "total_population": total_population,
        "total_municipalities": total_municipalities,
        "total_barangay_communities": total_barangay_communities,
        "auto_synced": auto_synced,
        "manual": manual_updates,
    }

    stat_cards = [
        {
            "title": (
                "Total Provincial OBCs in the Database"
                if not show_archived
                else "Total Archived Provincial OBCs"
            ),
            "value": total_coverages,
            "icon": "fas fa-flag",
            "gradient": "from-blue-500 via-blue-600 to-blue-700",
            "text_color": "text-blue-100",
            "icon_color": "text-blue-600",
        },
        {
            "title": (
                "Total OBC Population from the Provinces"
                if not show_archived
                else "Archived OBC Population Total"
            ),
            "value": total_population,
            "icon": "fas fa-users",
            "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
            "text_color": "text-emerald-100",
            "icon_color": "text-emerald-600",
        },
        {
            "title": "Auto-Synced Provinces",
            "value": auto_synced,
            "icon": "fas fa-sync-alt",
            "gradient": "from-purple-500 via-purple-600 to-purple-700",
            "text_color": "text-purple-100",
            "icon_color": "text-purple-600",
        },
        {
            "title": "Manually Updated Provinces",
            "value": manual_updates,
            "icon": "fas fa-edit",
            "gradient": "from-orange-500 via-orange-600 to-orange-700",
            "text_color": "text-orange-100",
            "icon_color": "text-orange-500",
        },
    ]

    stat_cards_grid_class = "mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"

    if show_archived:
        page_title = "Archived Provincial OBCs"
        page_description = "Review archived province-level Bangsamoro coverage data."
    else:
        page_title = "Manage Provincial OBC"
        if can_manage_communities:
            page_description = (
                "View, edit, and manage province-level Bangsamoro coverage data."
            )
        else:
            page_description = "Review province-level Bangsamoro coverage data."

    badge_text = (
        "OBC Data - Provincial (Archived)" if show_archived else "OBC Data - Provincial"
    )

    hero_actions = [
        {
            "href": (
                reverse("communities:communities_manage_provincial")
                if show_archived
                else f"{reverse('communities:communities_manage_provincial')}?archived=1"
            ),
            "label": (
                "Back to active records" if show_archived else "View archived records"
            ),
            "icon": "fas fa-list" if show_archived else "fas fa-archive",
            "variant": "secondary",
        }
    ]
    if can_manage_communities:
        hero_actions.append(
            {
                "href": reverse("communities:communities_add_province"),
                "label": "Add provincial OBC",
                "icon": "fas fa-plus",
                "variant": "primary",
            }
        )
    hero_actions.append(
        {
            "href": reverse("communities:communities_manage_municipal"),
            "label": "Go to municipal view",
            "icon": "fas fa-city",
            "variant": "ghost",
        }
    )

    hero_config = {
        "badge_icon": "fas fa-flag",
        "badge_text": badge_text,
        "icon": "fas fa-map",
        "title": page_title,
        "subtitle": page_description,
        "level_summary": (
            "Provincial-level coverage delivers a strategic view of OBC reach,"
            " resource deployments, and coordination rhythms across BARMM."
        ),
        "meta_cards": [],
        "metrics": [],
        "actions": hero_actions,
    }

    page_size = _resolve_page_size(request, "province_page_size")
    page_number = request.GET.get("province_page") or 1

    paginator = Paginator(coverages, page_size)
    coverages_page = paginator.get_page(page_number)

    def _format_timestamp_metadata(timestamp, user):
        """Return formatted HTML describing when a record was touched."""

        if not timestamp:
            return format_html(
                "<span class='text-xs text-gray-400'>Not yet recorded</span>"
            )

        try:
            localized = timezone.localtime(timestamp)
        except Exception:  # pragma: no cover - timezone conversion fallback
            localized = timestamp

        user_display = ""
        if user:
            name = user.get_full_name() or user.get_username()
            user_display = format_html(
                " · by <span class='font-medium text-gray-700'>{}</span>", name
            )

        return format_html(
            "<span class='text-xs text-gray-500'>"
            "<span class='font-semibold text-gray-700'>{}</span>"
            "<span class='ml-2 text-gray-400'>{}</span>"
            "{}"
            "</span>",
            localized.strftime("%b %d, %Y"),
            naturaltime(timestamp),
            mark_safe(user_display),
        )

    province_table_headers = [
        {"label": "", "class": "w-14"},  # Icon column (no label)
        {"label": "Province", "class": "flex-1 min-w-[160px]"},
        {"label": "Region", "class": "flex-1 min-w-[120px]"},
        {"label": "Coverage Snapshot", "class": "flex-1 min-w-[200px]"},
        {"label": "Top 5 Municipalities/Cities", "class": "flex-1 min-w-[240px]"},
        {"label": "Sync Mode", "class": "w-32"},
    ]

    province_table_rows: list[dict] = []
    for coverage in coverages_page:
        province = getattr(coverage, "province", None)
        region = getattr(province, "region", None)

        # Province name column (matches Municipal table style)
        province_html = format_html(
            "<div class='flex flex-col'>"
            "<span class='text-sm font-semibold text-gray-900'>{}</span>"
            "</div>",
            province.name if province else "—",
        )

        # Region column (matches Municipal table style)
        region_html = format_html(
            "<div class='flex flex-col'>"
            "<span class='text-sm text-gray-700'>{}</span>"
            "<span class='text-xs text-gray-500'>{}</span>"
            "</div>",
            f"Region {region.code}" if region else "—",
            region.name if region else "",
        )

        estimated_population_html = (
            format_html(
                "<span class='font-semibold text-gray-700'>{}</span>",
                intcomma(coverage.estimated_obc_population),
            )
            if coverage.estimated_obc_population is not None
            else mark_safe("&mdash;")
        )
        households_html = (
            format_html(
                "<span class='font-semibold text-gray-700'>{}</span>",
                intcomma(coverage.households),
            )
            if getattr(coverage, "households", None) not in (None, "")
            else mark_safe("&mdash;")
        )

        # Coverage Snapshot (matches Municipal table style)
        total_municipalities = coverage.total_municipalities or 0
        total_barangay_obcs = coverage.total_obc_communities or 0
        estimated_population = coverage.estimated_obc_population or 0
        households = getattr(coverage, "households", 0) or 0

        snapshot_parts = [
            format_html(
                "<div class='text-sm font-semibold text-gray-900'>{} municipalities tracked</div>",
                intcomma(total_municipalities),
            ),
            format_html(
                "<div class='text-xs text-gray-500'>Barangay OBCs: {}</div>",
                intcomma(total_barangay_obcs),
            ),
            format_html(
                "<div class='text-xs text-gray-500'>Est. OBC Population: {}</div>",
                intcomma(estimated_population),
            ),
            format_html(
                "<div class='text-xs text-gray-500'>Households: {}</div>",
                intcomma(households),
            ),
        ]
        snapshot_html = format_html(
            "<div class='space-y-1'>{}</div>",
            format_html_join("", "{}", ((part,) for part in snapshot_parts)),
        )

        # Top 5 Municipalities/Cities column (by Estimated OBC Population)
        top_municipalities = MunicipalityCoverage.objects.filter(
            municipality__province=province,
            estimated_obc_population__isnull=False
        ).order_by('-estimated_obc_population').values_list(
            'municipality__name', flat=True
        )[:5]

        if top_municipalities:
            municipality_names = ", ".join(top_municipalities)
            key_municipalities_html = format_html(
                "<div class='text-sm text-gray-700 break-words whitespace-normal'>{}</div>",
                municipality_names,
            )
        else:
            key_municipalities_html = format_html(
                "<div class='text-sm text-gray-400 italic'>No OBC Population recorded</div>"
            )

        # Sync Mode column (consistent with Municipal table)
        if coverage.auto_sync:
            sync_mode_html = format_html(
                "<span class='inline-flex items-center gap-1 rounded-full border border-emerald-200 "
                "bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700'>"
                "<i class='fas fa-sync'></i>"
                "<span>Auto-sync</span>"
                "</span>"
            )
        else:
            sync_mode_html = format_html(
                "<span class='inline-flex items-center gap-1 rounded-full border border-amber-200 "
                "bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700'>"
                "<i class='fas fa-hand-paper'></i>"
                "<span>Manual</span>"
                "</span>"
            )

        view_url_base = reverse(
            "communities:communities_view_provincial", args=[coverage.pk]
        )
        view_url = f"{view_url_base}?archived=1" if show_archived else view_url_base

        edit_url = None
        delete_preview_url = None
        delete_message = None
        restore_url = None

        if can_manage_communities:
            if show_archived:
                restore_url = reverse(
                    "communities:communities_restore_provincial", args=[coverage.pk]
                )
            else:
                edit_url = reverse(
                    "communities:communities_edit_provincial", args=[coverage.pk]
                )
                delete_preview_url = f"{view_url_base}?review_delete=1"
                delete_message = (
                    "Are you sure you want to delete this provincial OBC coverage? "
                    "You will review the details before final confirmation."
                )

        row = {
            "cells": [
                {"content": province_html, "class": "flex-1 min-w-[160px]"},
                {"content": region_html, "class": "flex-1 min-w-[120px]"},
                {"content": snapshot_html, "class": "flex-1 min-w-[200px]"},
                {"content": key_municipalities_html, "class": "flex-1 min-w-[240px]"},
                {"content": sync_mode_html, "class": "w-32"},
            ],
            "view_url": view_url,
        }

        if edit_url:
            row["edit_url"] = edit_url
        if delete_preview_url:
            row["delete_preview_url"] = delete_preview_url
        if delete_message:
            row["delete_message"] = delete_message
        if restore_url:
            row["restore_url"] = restore_url

        province_table_rows.append(row)

    empty_state_message = "No provincial OBC records found."
    if can_manage_communities:
        empty_state_message = format_html(
            "No provincial OBC records found. "
            '<a href="{}" class="inline-flex items-center gap-2 text-emerald-600 hover:text-emerald-700">'
            "<i class='fas fa-plus-circle'></i>"
            "<span>Add provincial OBC</span>"
            "</a>",
            reverse("communities:communities_add_province"),
        )

    request_params = request.GET.dict()
    coverage_base_querystring = _build_querystring(
        request_params,
        exclude=("province_page",),
    )

    context = {
        "coverages": coverages_page,
        "regions": regions,
        "provinces": provinces,
        "current_region": region_filter,
        "current_province": province_filter,
        "search_query": search_query,
        "province_options_json": province_options_json,
        "stats": stats,
        "stat_cards": stat_cards,
        "stat_cards_grid_class": stat_cards_grid_class,
        "show_archived": show_archived,
        "page_title": page_title,
        "page_description": page_description,
        "hero_config": hero_config,
        "province_page_size": page_size,
        "province_page_size_options": PAGE_SIZE_OPTIONS,
        "province_base_querystring": coverage_base_querystring,
        "province_total_pages": max(coverages_page.paginator.num_pages, 1),
        "can_manage_communities": can_manage_communities,
        "province_table_headers": province_table_headers,
        "province_table_rows": province_table_rows,
        "province_table": {
            "rows": province_table_rows,
            "show_actions": can_manage_communities,
        },
        "province_table_empty_message": empty_state_message,
    }
    template_name = "communities/provincial_manage.html"
    if request.headers.get("HX-Request"):
        template_name = "communities/partials/provincial_manage_results.html"
    return render(request, template_name, context)


@login_required
def communities_view(request, community_id):
    """Display a read-only view of a barangay-level OBC community."""
    from django.db.models import Q

    from communities.models import MunicipalityCoverage, OBCCommunity
    from monitoring.models import MonitoringEntry
    from recommendations.policy_tracking.models import PolicyRecommendation

    community = get_object_or_404(
        OBCCommunity.all_objects.select_related(
            "barangay__municipality__province__region"
        ),
        pk=community_id,
    )

    delete_review_mode = (
        request.GET.get("review_delete") == "1" and not community.is_deleted
    )
    default_next = reverse("communities:communities_manage")
    if request.GET.get("archived") == "1":
        default_next = f"{default_next}?archived=1"
    redirect_after_action = request.GET.get("next") or default_next

    if community.is_deleted:
        delete_review_mode = False

    municipality_coverage = None
    try:
        municipality_coverage = MunicipalityCoverage.objects.select_related(
            "municipality__province__region"
        ).get(municipality=community.barangay.municipality)
    except MunicipalityCoverage.DoesNotExist:
        municipality_coverage = None

    # Query MOA/PPAs attributed to this barangay OBC
    moa_ppas = (
        MonitoringEntry.objects.filter(communities=community)
        .select_related("lead_organization", "implementing_moa")
        .distinct()
        .order_by("-created_at")[:10]
    )

    # Query recommendations tagged to this barangay OBC or its administrative parents
    location_filters = Q(target_communities=community)

    if getattr(community, "barangay", None):
        barangay = community.barangay
        municipality = getattr(barangay, "municipality", None)
        province = getattr(municipality, "province", None) if municipality else None
        region = getattr(province, "region", None) if province else None

        location_filters |= Q(target_barangay=barangay)

        if municipality:
            location_filters |= Q(target_municipality=municipality)
            location_filters |= Q(target_barangay__municipality=municipality)
            location_filters |= Q(
                target_communities__barangay__municipality=municipality
            )

        if province:
            location_filters |= Q(target_province=province)
            location_filters |= Q(target_municipality__province=province)
            location_filters |= Q(target_barangay__municipality__province=province)
            location_filters |= Q(
                target_communities__barangay__municipality__province=province
            )

        if region:
            location_filters |= Q(target_region=region)

    recommendations = (
        PolicyRecommendation.objects.filter(location_filters)
        .select_related(
            "proposed_by",
            "target_region",
            "target_province",
            "target_municipality",
            "target_barangay",
        )
        .prefetch_related("target_communities__barangay__municipality")
        .order_by("-created_at")
        .distinct()[:10]
    )

    context = {
        "community": community,
        "municipality_coverage": municipality_coverage,
        "moa_ppas": moa_ppas,
        "recommendations": recommendations,
        "delete_review_mode": delete_review_mode,
        "is_archived": community.is_deleted,
        "redirect_after_action": redirect_after_action,
        "map_payload": _resolve_map_payload(
            primary_lat=community.latitude,
            primary_lng=community.longitude,
            primary_zoom=15,
            barangay=getattr(community, "barangay", None),
        ),
    }
    return render(request, "communities/communities_view.html", context)


@login_required
def communities_view_municipal(request, coverage_id):
    """Display a read-only view of a municipal-level OBC coverage."""
    from django.db.models import Q

    from communities.models import MunicipalityCoverage, OBCCommunity
    from monitoring.models import MonitoringEntry
    from recommendations.policy_tracking.models import PolicyRecommendation

    coverage = get_object_or_404(
        MunicipalityCoverage.all_objects.select_related(
            "municipality__province__region"
        ),
        pk=coverage_id,
    )

    delete_review_mode = (
        request.GET.get("review_delete") == "1" and not coverage.is_deleted
    )
    default_next = reverse("communities:communities_manage_municipal")
    if request.GET.get("archived") == "1":
        default_next = f"{default_next}?archived=1"
    redirect_after_action = request.GET.get("next") or default_next

    if coverage.is_deleted:
        delete_review_mode = False

    related_communities = (
        OBCCommunity.objects.select_related("barangay__municipality__province__region")
        .filter(barangay__municipality=coverage.municipality)
        .order_by("barangay__name")
    )

    # Query MOA/PPAs attributed to this municipality
    moa_ppas = (
        MonitoringEntry.objects.filter(
            communities__barangay__municipality=coverage.municipality
        )
        .select_related("lead_organization", "implementing_moa")
        .distinct()
        .order_by("-created_at")[:10]
    )

    # Query recommendations tagged to this municipality or its administrative parents/children
    municipality = coverage.municipality
    province = municipality.province
    region = province.region if province else None

    location_filters = Q(target_municipality=municipality)
    location_filters |= Q(target_barangay__municipality=municipality)
    location_filters |= Q(target_communities__barangay__municipality=municipality)

    if province:
        location_filters |= Q(target_province=province)
        location_filters |= Q(target_municipality__province=province)
        location_filters |= Q(target_barangay__municipality__province=province)
        location_filters |= Q(
            target_communities__barangay__municipality__province=province
        )

    if region:
        location_filters |= Q(target_region=region)

    recommendations = (
        PolicyRecommendation.objects.filter(location_filters)
        .select_related(
            "proposed_by",
            "target_region",
            "target_province",
            "target_municipality",
            "target_barangay",
        )
        .prefetch_related("target_communities__barangay")
        .order_by("-created_at")
        .distinct()[:10]
    )

    context = {
        "coverage": coverage,
        "related_communities": related_communities,
        "moa_ppas": moa_ppas,
        "recommendations": recommendations,
        "delete_review_mode": delete_review_mode,
        "is_archived": coverage.is_deleted,
        "redirect_after_action": redirect_after_action,
        "map_payload": _resolve_map_payload(
            primary_lat=coverage.latitude,
            primary_lng=coverage.longitude,
            primary_zoom=12,
            municipality=coverage.municipality,
        ),
    }
    return render(request, "communities/municipal_view.html", context)


@login_required
def communities_view_provincial(request, coverage_id):
    """Display a read-only view of a province-level OBC coverage."""
    from django.db.models import Q

    from communities.models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage
    from django.core.exceptions import PermissionDenied

    coverage = get_object_or_404(
        ProvinceCoverage.all_objects.select_related("province__region", "created_by"),
        pk=coverage_id,
    )

    # MANA Participant access control - can only view what they created
    is_mana_participant = (
        request.user.has_perm("mana.can_access_regional_mana")
        and not request.user.is_staff
        and not request.user.is_superuser
    )

    if is_mana_participant:
        if coverage.created_by != request.user:
            raise PermissionDenied(
                "You can only view Provincial OBCs that you created."
            )

    can_edit = not coverage.is_submitted and (
        request.user.is_staff
        or request.user.is_superuser
        or (is_mana_participant and coverage.created_by == request.user)
    )

    can_submit = (
        is_mana_participant
        and coverage.created_by == request.user
        and not coverage.is_submitted
    )

    delete_review_mode = (
        request.GET.get("review_delete") == "1" and not coverage.is_deleted
    )
    default_next = reverse("communities:communities_manage_provincial")
    if request.GET.get("archived") == "1":
        default_next = f"{default_next}?archived=1"
    redirect_after_action = request.GET.get("next") or default_next

    if coverage.is_deleted:
        delete_review_mode = False

    related_municipal_coverages = (
        MunicipalityCoverage.objects.select_related("municipality__province__region")
        .filter(municipality__province=coverage.province)
        .order_by("municipality__name")
    )

    related_communities = (
        OBCCommunity.objects.select_related("barangay__municipality__province__region")
        .filter(barangay__municipality__province=coverage.province)
        .order_by("barangay__name")
    )

    # Query MOA/PPAs attributed to this province
    from monitoring.models import MonitoringEntry
    from recommendations.policy_tracking.models import PolicyRecommendation

    moa_ppas = (
        MonitoringEntry.objects.filter(
            communities__barangay__municipality__province=coverage.province
        )
        .select_related("lead_organization", "implementing_moa")
        .distinct()
        .order_by("-created_at")[:10]
    )

    # Query recommendations tagged to this province or its administrative ancestors/descendants
    province = coverage.province
    region = province.region if province else None

    location_filters = Q(target_province=province)
    location_filters |= Q(target_municipality__province=province)
    location_filters |= Q(target_barangay__municipality__province=province)
    location_filters |= Q(target_communities__barangay__municipality__province=province)

    if region:
        location_filters |= Q(target_region=region)

    recommendations = (
        PolicyRecommendation.objects.filter(location_filters)
        .select_related(
            "proposed_by",
            "target_region",
            "target_province",
            "target_municipality",
            "target_barangay",
        )
        .prefetch_related(
            "target_communities__barangay__municipality",
            "target_communities__barangay__municipality__province",
        )
        .order_by("-created_at")
        .distinct()[:10]
    )

    context = {
        "coverage": coverage,
        "related_municipal_coverages": related_municipal_coverages,
        "related_communities": related_communities,
        "moa_ppas": moa_ppas,
        "recommendations": recommendations,
        "delete_review_mode": delete_review_mode,
        "is_archived": coverage.is_deleted,
        "redirect_after_action": redirect_after_action,
        "can_edit": can_edit,
        "can_submit": can_submit,
        "is_mana_participant": is_mana_participant,
        "map_payload": _resolve_map_payload(
            primary_lat=coverage.latitude,
            primary_lng=coverage.longitude,
            primary_zoom=9,
            province=coverage.province,
        ),
    }
    return render(request, "communities/provincial_view.html", context)


@login_required
@require_GET
def location_centroid(request):
    """Return centroid coordinates for the requested administrative unit."""

    level = request.GET.get("level")
    object_id = request.GET.get("id")

    if not level or not object_id:
        return JsonResponse(
            {"error": "Both 'level' and 'id' query parameters are required."},
            status=400,
        )

    lookup_map = {
        "region": Region,
        "province": Province,
        "municipality": Municipality,
        "barangay": Barangay,
    }

    model = lookup_map.get(level)
    if model is None:
        return JsonResponse({"error": "Unsupported level."}, status=400)

    obj = get_object_or_404(model, pk=object_id)

    lat, lng = get_object_centroid(obj)
    source = "cached"

    if lat is None or lng is None:
        lat, lng, updated, geocode_source = enhanced_ensure_location_coordinates(obj)
        if lat is not None and lng is not None:
            source = geocode_source or "geocoded"
        else:
            source = geocode_source or ("geocoded" if updated else "unavailable")

    if lat is None or lng is None:
        return JsonResponse(
            {
                "has_location": False,
                "source": source,
                "message": f"No coordinates available for {level} {obj.name if hasattr(obj, 'name') else obj}",
            }
        )

    # Validate coordinates are within reasonable bounds
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return JsonResponse(
            {
                "has_location": False,
                "source": source,
                "message": f"Invalid coordinates for {level}: lat={lat}, lng={lng}",
            }
        )

    return JsonResponse(
        {
            "has_location": True,
            "lat": float(lat),
            "lng": float(lng),
            "source": source,
            "accuracy": "high" if source == "cached" else "medium",
            "message": f"Coordinates found for {level} {obj.name if hasattr(obj, 'name') else obj}",
        }
    )


@login_required
def communities_edit(request, community_id):
    """Edit an existing barangay-level community."""
    _ensure_can_manage_communities(request.user)

    from communities.models import OBCCommunity

    community = get_object_or_404(
        OBCCommunity.objects.select_related("barangay__municipality__province__region"),
        pk=community_id,
    )

    if request.method == "POST":
        form = OBCCommunityForm(request.POST, instance=community)
        if form.is_valid():
            community = form.save()
            _sync_hierarchical_coverages(community.barangay.municipality)
            messages.success(
                request,
                f'Barangay OBC "{community.display_name}" has been updated successfully.',
            )
            return redirect("communities:communities_manage")
    else:
        form = OBCCommunityForm(instance=community)

    recent_communities = OBCCommunity.objects.exclude(pk=community.pk).order_by(
        "-created_at"
    )[:5]

    context = {
        "form": form,
        "community": community,
        "page_title": "Edit Barangay OBC",
        "breadcrumb_label": "Edit Barangay OBC",
        "page_subtitle": "Update barangay-level community information.",
        "form_heading": "Barangay OBC Form",
        "location_data": build_location_data(),
        "show_barangay_field": True,
        "recent_communities": recent_communities,
    }
    return render(request, "communities/communities_add.html", context)


@login_required
@require_POST
def communities_delete(request, community_id):
    """Delete an existing barangay-level community."""
    _ensure_can_manage_communities(request.user)

    from communities.models import OBCCommunity

    community = get_object_or_404(
        OBCCommunity.objects.select_related("barangay__municipality__province__region"),
        pk=community_id,
    )
    municipality = community.barangay.municipality if community.barangay else None
    community_name = community.display_name
    community.soft_delete(user=request.user)

    _sync_hierarchical_coverages(municipality)

    messages.success(
        request,
        (
            f'Barangay OBC "{community_name}" has been archived. '
            "You can restore it from the Archived Barangay OBCs view."
        ),
    )
    return redirect(f"{reverse('communities:communities_manage')}?archived=1")


@login_required
@require_POST
def communities_restore(request, community_id):
    """Restore a previously archived barangay-level community."""
    _ensure_can_manage_communities(request.user)

    from communities.models import OBCCommunity

    community = get_object_or_404(
        OBCCommunity.all_objects.select_related(
            "barangay__municipality__province__region"
        ),
        pk=community_id,
        is_deleted=True,
    )
    municipality = community.barangay.municipality if community.barangay else None
    community.restore()

    _sync_hierarchical_coverages(municipality)

    messages.success(
        request,
        f'Barangay OBC "{community.display_name}" has been restored to the active registry.',
    )
    return redirect(f"{reverse('communities:communities_manage')}?archived=1")


@login_required
def communities_stakeholders(request):
    """Manage stakeholders page."""
    from django.db.models import Count

    from communities.models import OBCCommunity, Stakeholder

    stakeholders = Stakeholder.objects.select_related(
        "community", "community__barangay__municipality__province__region"
    ).prefetch_related("engagements")

    community_filter = request.GET.get("community")
    type_filter = request.GET.get("type")
    status_filter = request.GET.get("status")

    if community_filter:
        stakeholders = stakeholders.filter(community__id=community_filter)

    if type_filter:
        stakeholders = stakeholders.filter(stakeholder_type=type_filter)

    if status_filter:
        if status_filter == "active":
            stakeholders = stakeholders.filter(is_active=True)
        elif status_filter == "verified":
            stakeholders = stakeholders.filter(is_verified=True)

    communities = OBCCommunity.objects.order_by("barangay__name")
    stakeholder_types = Stakeholder.STAKEHOLDER_TYPES

    stats = {
        "total_stakeholders": stakeholders.count(),
        "active_stakeholders": stakeholders.filter(is_active=True).count(),
        "verified_stakeholders": stakeholders.filter(is_verified=True).count(),
        "by_type": stakeholders.values("stakeholder_type").annotate(count=Count("id")),
    }

    context = {
        "stakeholders": stakeholders.order_by("full_name"),
        "communities": communities,
        "stakeholder_types": stakeholder_types,
        "current_community": community_filter,
        "current_type": type_filter,
        "current_status": status_filter,
        "stats": stats,
    }
    return render(request, "communities/communities_stakeholders.html", context)


@login_required
def communities_edit_municipal(request, coverage_id):
    """Edit an existing municipality coverage record."""
    _ensure_can_manage_communities(request.user)

    from communities.models import MunicipalityCoverage

    coverage = get_object_or_404(
        MunicipalityCoverage.objects.select_related("municipality__province__region"),
        pk=coverage_id,
    )

    if request.method == "POST":
        form = MunicipalityCoverageForm(request.POST, instance=coverage)
        if form.is_valid():
            coverage = form.save()
            coverage.refresh_from_communities()
            messages.success(
                request,
                f"Municipal OBC coverage for {coverage.municipality.name} has been updated.",
            )
            return redirect("communities:communities_manage_municipal")
    else:
        form = MunicipalityCoverageForm(instance=coverage)

    recent_coverages = (
        MunicipalityCoverage.objects.exclude(pk=coverage.pk)
        .select_related("municipality__province__region")
        .order_by("-created_at")[:5]
    )

    context = {
        "form": form,
        "coverage": coverage,
        "page_title": "Edit Municipal OBC",
        "breadcrumb_label": "Edit Municipal OBC",
        "page_subtitle": "Update municipality-level Bangsamoro coverage data.",
        "form_heading": "Municipal OBC Form",
        "location_data": build_location_data(include_barangays=False),
        "show_barangay_field": False,
        "recent_coverages": recent_coverages,
    }
    return render(request, "communities/communities_add.html", context)


@login_required
def communities_edit_provincial(request, coverage_id):
    """Edit an existing province-level coverage record."""
    _ensure_can_manage_communities(request.user)

    from communities.models import ProvinceCoverage

    coverage = get_object_or_404(
        ProvinceCoverage.objects.select_related("province__region", "created_by"),
        pk=coverage_id,
    )

    # MANA Participant access control - can only edit what they created
    is_mana_participant = (
        request.user.has_perm("mana.can_access_regional_mana")
        and not request.user.is_staff
        and not request.user.is_superuser
    )

    if is_mana_participant:
        if coverage.created_by != request.user:
            raise PermissionDenied(
                "You can only edit Provincial OBCs that you created."
            )

        # Cannot edit submitted records
        if coverage.is_submitted:
            messages.error(
                request,
                "This Provincial OBC has been submitted and can no longer be edited. "
                "Contact OOBC staff if you need to make changes.",
            )
            return redirect(
                "communities:communities_view_provincial", coverage_id=coverage.id
            )

    if request.method == "POST":
        form = ProvinceCoverageForm(request.POST, instance=coverage)
        if form.is_valid():
            coverage = form.save(commit=False)
            coverage.updated_by = request.user
            coverage.save()
            coverage.refresh_from_municipalities()
            messages.success(
                request,
                f"Provincial OBC coverage for {coverage.province.name} has been updated.",
            )
            return redirect("communities:communities_manage_provincial")
    else:
        form = ProvinceCoverageForm(instance=coverage)

    recent_coverages = (
        ProvinceCoverage.objects.exclude(pk=coverage.pk)
        .select_related("province__region")
        .order_by("-created_at")[:5]
    )

    context = {
        "form": form,
        "coverage": coverage,
        "page_title": "Edit Provincial OBC",
        "breadcrumb_label": "Edit Provincial OBC",
        "page_subtitle": "Update province-level Bangsamoro coverage data.",
        "form_heading": "Provincial OBC Form",
        "location_data": build_location_data(include_barangays=False),
        "show_barangay_field": False,
        "recent_coverages": recent_coverages,
    }
    return render(request, "communities/communities_add.html", context)


@login_required
@require_POST
def communities_delete_municipal(request, coverage_id):
    """Delete a municipality coverage record."""
    _ensure_can_manage_communities(request.user)

    from communities.models import MunicipalityCoverage, ProvinceCoverage

    coverage = get_object_or_404(
        MunicipalityCoverage.objects.select_related("municipality__province__region"),
        pk=coverage_id,
    )
    municipality_name = coverage.municipality.name
    coverage.soft_delete(user=request.user)
    ProvinceCoverage.sync_for_province(coverage.municipality.province)

    messages.success(
        request,
        (
            f"Municipal OBC coverage for {municipality_name} has been archived. "
            "You can restore it from the Archived Municipal OBCs view."
        ),
    )
    return redirect(f"{reverse('communities:communities_manage_municipal')}?archived=1")


@login_required
@require_POST
def communities_restore_municipal(request, coverage_id):
    """Restore a previously archived municipality coverage record."""
    _ensure_can_manage_communities(request.user)

    from communities.models import MunicipalityCoverage, ProvinceCoverage

    coverage = get_object_or_404(
        MunicipalityCoverage.all_objects.select_related(
            "municipality__province__region"
        ),
        pk=coverage_id,
        is_deleted=True,
    )
    coverage.restore()
    coverage.refresh_from_communities()
    ProvinceCoverage.sync_for_province(coverage.municipality.province)

    messages.success(
        request,
        f"Municipal OBC coverage for {coverage.municipality.name} has been restored.",
    )
    return redirect(f"{reverse('communities:communities_manage_municipal')}?archived=1")


@login_required
@require_POST
def communities_delete_provincial(request, coverage_id):
    """Delete a province coverage record."""
    _ensure_can_manage_communities(request.user)

    from communities.models import ProvinceCoverage

    coverage = get_object_or_404(
        ProvinceCoverage.objects.select_related("province__region", "created_by"),
        pk=coverage_id,
    )

    # MANA Participant access control - can only delete what they created
    is_mana_participant = (
        request.user.has_perm("mana.can_access_regional_mana")
        and not request.user.is_staff
        and not request.user.is_superuser
    )

    if is_mana_participant:
        if coverage.created_by != request.user:
            raise PermissionDenied(
                "You can only delete Provincial OBCs that you created."
            )

        # Cannot delete submitted records
        if coverage.is_submitted:
            messages.error(
                request,
                "This Provincial OBC has been submitted and can no longer be deleted. "
                "Contact OOBC staff if you need to remove it.",
            )
            return redirect(
                "communities:communities_view_provincial", coverage_id=coverage.id
            )

    province_name = coverage.province.name
    coverage.soft_delete(user=request.user)

    messages.success(
        request,
        (
            f"Provincial OBC coverage for {province_name} has been archived. "
            "You can restore it from the Archived Provincial OBCs view."
        ),
    )
    return redirect(f"{reverse('communities:communities_manage_provincial')}?archived=1")


@login_required
@require_POST
def communities_submit_provincial(request, coverage_id):
    """Submit a Provincial OBC record (makes it read-only for MANA participants)."""
    from communities.models import ProvinceCoverage
    from django.core.exceptions import PermissionDenied
    from django.utils import timezone

    coverage = get_object_or_404(
        ProvinceCoverage.objects.select_related("province__region", "created_by"),
        pk=coverage_id,
    )

    # Only MANA participants can submit their own records
    is_mana_participant = (
        request.user.has_perm("mana.can_access_regional_mana")
        and not request.user.is_staff
        and not request.user.is_superuser
    )

    if not is_mana_participant:
        raise PermissionDenied(
            "Only MANA participants can submit Provincial OBC records."
        )

    if coverage.created_by != request.user:
        raise PermissionDenied("You can only submit Provincial OBCs that you created.")

    if coverage.is_submitted:
        messages.warning(
            request,
            f"Provincial OBC for {coverage.province.name} has already been submitted.",
        )
        return redirect("communities:communities_view_provincial", coverage_id=coverage.id)

    # Mark as submitted
    coverage.is_submitted = True
    coverage.submitted_at = timezone.now()
    coverage.submitted_by = request.user
    coverage.save()

    messages.success(
        request,
        f"Provincial OBC for {coverage.province.name} has been submitted successfully. "
        "This record is now read-only. Contact OOBC staff if you need to make changes.",
    )
    return redirect("communities:communities_view_provincial", coverage_id=coverage.id)


@login_required
@require_POST
def communities_restore_provincial(request, coverage_id):
    """Restore a previously archived province coverage record."""
    _ensure_can_manage_communities(request.user)

    from communities.models import ProvinceCoverage

    coverage = get_object_or_404(
        ProvinceCoverage.all_objects.select_related("province__region", "created_by"),
        pk=coverage_id,
        is_deleted=True,
    )

    # MANA Participant access control - can only restore what they created
    is_mana_participant = (
        request.user.has_perm("mana.can_access_regional_mana")
        and not request.user.is_staff
        and not request.user.is_superuser
    )

    if is_mana_participant:
        if coverage.created_by != request.user:
            raise PermissionDenied(
                "You can only restore Provincial OBCs that you created."
            )
    coverage.restore()
    coverage.refresh_from_municipalities()

    messages.success(
        request,
        f"Provincial OBC coverage for {coverage.province.name} has been restored.",
    )
    return redirect(f"{reverse('communities:communities_manage_provincial')}?archived=1")


__all__ = [
    "communities_home",
    "communities_add",
    "communities_add_municipality",
    "communities_add_province",
    "communities_manage",
    "communities_manage_municipal",
    "communities_manage_provincial",
    "communities_view",
    "communities_view_municipal",
    "communities_view_provincial",
    "communities_edit",
    "communities_delete",
    "communities_restore",
    "communities_edit_municipal",
    "communities_delete_municipal",
    "communities_restore_municipal",
    "communities_edit_provincial",
    "communities_delete_provincial",
    "communities_submit_provincial",
    "communities_restore_provincial",
    "communities_stakeholders",
    "location_centroid",
]
