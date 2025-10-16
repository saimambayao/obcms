import csv
import io
from datetime import datetime, timedelta

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from common.utils.moa_permissions import moa_view_only
from common.models import Barangay, Province, Region
from common.forms import OBCCommunityForm
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.services.geodata import serialize_layers_for_map

from .models import (
    CommunityInfrastructure,
    CommunityLivelihood,
    GeographicDataLayer,
    MapVisualization,
    MunicipalityCoverage,
    OBCCommunity,
    Stakeholder,
    StakeholderEngagement,
)
from .forms import GeographicDataLayerForm, MapVisualizationForm
from .serializers import (
    CommunityInfrastructureSerializer,
    CommunityLivelihoodSerializer,
    CommunityStatsSerializer,
    OBCCommunityListSerializer,
    OBCCommunitySerializer,
    StakeholderEngagementSerializer,
    StakeholderListSerializer,
    StakeholderSerializer,
    StakeholderStatsSerializer,
)


class OBCCommunityViewSet(viewsets.ModelViewSet):
    """ViewSet for OBC Community model."""

    queryset = (
        OBCCommunity.objects.select_related(
            "barangay",
            "barangay__municipality",
            "barangay__municipality__province",
            "barangay__municipality__province__region",
        )
        .prefetch_related("livelihoods", "infrastructure", "stakeholders")
        .all()
    )

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return OBCCommunityListSerializer
        return OBCCommunitySerializer

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get community statistics."""
        communities = self.get_queryset()

        # Basic counts
        total_communities = communities.count()
        total_population = sum(c.population or 0 for c in communities)
        total_households = sum(c.households or 0 for c in communities)

        # By region
        by_region = {}
        for community in communities:
            region_name = community.region.name
            if region_name not in by_region:
                by_region[region_name] = 0
            by_region[region_name] += 1

        # By development status
        by_unemployment_rate = {}
        for community in communities:
            rate = community.get_unemployment_rate_display()
            if rate not in by_unemployment_rate:
                by_unemployment_rate[rate] = 0
            by_unemployment_rate[rate] += 1

        # By settlement type
        by_settlement_type = {}
        for community in communities:
            settlement = community.get_settlement_type_display()
            if settlement not in by_settlement_type:
                by_settlement_type[settlement] = 0
            by_settlement_type[settlement] += 1

        # Religious facilities
        religious_facilities = {
            "communities_with_mosque": communities.filter(mosques_count__gt=0).count(),
            "communities_with_madrasah": communities.filter(
                madrasah_count__gt=0
            ).count(),
            "total_religious_leaders": sum(
                c.religious_leaders_count for c in communities
            ),
        }

        # Average household size
        household_sizes = [
            c.average_household_size for c in communities if c.average_household_size
        ]
        average_household_size = (
            sum(household_sizes) / len(household_sizes) if household_sizes else 0
        )

        # Language distribution
        language_distribution = {}
        for community in communities:
            if community.primary_language:
                lang = community.primary_language
                if lang not in language_distribution:
                    language_distribution[lang] = 0
                language_distribution[lang] += 1

        stats_data = {
            "total_communities": total_communities,
            "total_population": total_population,
            "total_households": total_households,
            "by_region": by_region,
            "by_unemployment_rate": by_unemployment_rate,
            "by_settlement_type": by_settlement_type,
            "religious_facilities": religious_facilities,
            "average_household_size": round(average_household_size, 1),
            "language_distribution": language_distribution,
        }

        serializer = CommunityStatsSerializer(stats_data)
        return Response(serializer.data)


class StakeholderViewSet(viewsets.ModelViewSet):
    """ViewSet for Stakeholder model."""

    queryset = (
        Stakeholder.objects.select_related(
            "community",
            "community__barangay",
            "community__barangay__municipality",
            "community__barangay__municipality__province",
            "community__barangay__municipality__province__region",
        )
        .prefetch_related("engagements")
        .all()
    )

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return StakeholderListSerializer
        return StakeholderSerializer

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()

        # Filter by community
        community_id = self.request.query_params.get("community", None)
        if community_id:
            queryset = queryset.filter(community_id=community_id)

        # Filter by stakeholder type
        stakeholder_type = self.request.query_params.get("type", None)
        if stakeholder_type:
            queryset = queryset.filter(stakeholder_type=stakeholder_type)

        # Filter by influence level
        influence_level = self.request.query_params.get("influence", None)
        if influence_level:
            queryset = queryset.filter(influence_level=influence_level)

        # Filter by active status
        is_active = self.request.query_params.get("active", None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Filter by verified status
        is_verified = self.request.query_params.get("verified", None)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == "true")

        return queryset

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get stakeholder statistics."""
        stakeholders = self.get_queryset()

        # Basic counts
        total_stakeholders = stakeholders.count()
        active_stakeholders = stakeholders.filter(is_active=True).count()
        verified_stakeholders = stakeholders.filter(is_verified=True).count()

        # By type
        by_type = {}
        for stakeholder in stakeholders:
            stype = stakeholder.get_stakeholder_type_display()
            if stype not in by_type:
                by_type[stype] = 0
            by_type[stype] += 1

        # By influence level
        by_influence_level = {}
        for stakeholder in stakeholders:
            influence = stakeholder.get_influence_level_display()
            if influence not in by_influence_level:
                by_influence_level[influence] = 0
            by_influence_level[influence] += 1

        # By engagement level
        by_engagement_level = {}
        for stakeholder in stakeholders:
            engagement = stakeholder.get_engagement_level_display()
            if engagement not in by_engagement_level:
                by_engagement_level[engagement] = 0
            by_engagement_level[engagement] += 1

        # By community
        by_community = {}
        for stakeholder in stakeholders:
            community = stakeholder.community.barangay.name
            if community not in by_community:
                by_community[community] = 0
            by_community[community] += 1

        # Recent engagements (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_engagements = StakeholderEngagement.objects.filter(
            stakeholder__in=stakeholders, date__gte=thirty_days_ago
        ).count()

        stats_data = {
            "total_stakeholders": total_stakeholders,
            "active_stakeholders": active_stakeholders,
            "verified_stakeholders": verified_stakeholders,
            "by_type": by_type,
            "by_influence_level": by_influence_level,
            "by_engagement_level": by_engagement_level,
            "by_community": by_community,
            "recent_engagements": recent_engagements,
        }

        serializer = StakeholderStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """Verify a stakeholder."""
        stakeholder = self.get_object()
        stakeholder.is_verified = True
        stakeholder.verification_date = timezone.now().date()
        stakeholder.save()

        serializer = self.get_serializer(stakeholder)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def unverify(self, request, pk=None):
        """Unverify a stakeholder."""
        stakeholder = self.get_object()
        stakeholder.is_verified = False
        stakeholder.verification_date = None
        stakeholder.save()

        serializer = self.get_serializer(stakeholder)
        return Response(serializer.data)


class StakeholderEngagementViewSet(viewsets.ModelViewSet):
    """ViewSet for Stakeholder Engagement model."""

    serializer_class = StakeholderEngagementSerializer
    queryset = StakeholderEngagement.objects.select_related(
        "stakeholder", "stakeholder__community"
    ).all()

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()

        # Filter by stakeholder
        stakeholder_id = self.request.query_params.get("stakeholder", None)
        if stakeholder_id:
            queryset = queryset.filter(stakeholder_id=stakeholder_id)

        # Filter by community
        community_id = self.request.query_params.get("community", None)
        if community_id:
            queryset = queryset.filter(stakeholder__community_id=community_id)

        # Filter by engagement type
        engagement_type = self.request.query_params.get("type", None)
        if engagement_type:
            queryset = queryset.filter(engagement_type=engagement_type)

        # Filter by outcome
        outcome = self.request.query_params.get("outcome", None)
        if outcome:
            queryset = queryset.filter(outcome=outcome)

        # Filter by follow-up needed
        follow_up = self.request.query_params.get("follow_up", None)
        if follow_up is not None:
            queryset = queryset.filter(follow_up_needed=follow_up.lower() == "true")

        # Filter by date range
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset


class CommunityLivelihoodViewSet(viewsets.ModelViewSet):
    """ViewSet for Community Livelihood model."""

    serializer_class = CommunityLivelihoodSerializer
    queryset = CommunityLivelihood.objects.select_related("community").all()

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()

        # Filter by community
        community_id = self.request.query_params.get("community", None)
        if community_id:
            queryset = queryset.filter(community_id=community_id)

        return queryset


class CommunityInfrastructureViewSet(viewsets.ModelViewSet):
    """ViewSet for Community Infrastructure model."""

    serializer_class = CommunityInfrastructureSerializer
    queryset = CommunityInfrastructure.objects.select_related("community").all()

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()

        # Filter by community
        community_id = self.request.query_params.get("community", None)
        if community_id:
            queryset = queryset.filter(community_id=community_id)

        return queryset


# ============================================================================
# COMMUNITIES MODULE VIEWS
# ============================================================================

@login_required
def communities_home(request):
    """OBC Communities module home page."""
    from django.db.models import Count, Sum, Q, Avg

    # Get community statistics
    communities = OBCCommunity.objects.select_related(
        "barangay__municipality__province__region"
    ).annotate(stakeholder_count=Count("stakeholders"))

    # Get municipal coverage statistics
    municipal_coverages = MunicipalityCoverage.objects.select_related(
        "municipality__province__region"
    )

    # Calculate total OBC population (avoid double-counting since municipal data is auto-synced from barangay data)
    total_obc_population = (
        communities.aggregate(total=Sum("estimated_obc_population"))["total"] or 0
    )

    # Count of barangay, municipal, and provincial OBCs
    total_barangay_obcs = communities.count()
    total_municipal_obcs = municipal_coverages.count()
    province_ids = set(
        communities.values_list("barangay__municipality__province_id", flat=True)
    )
    province_ids.update(
        municipal_coverages.values_list("municipality__province_id", flat=True)
    )
    province_ids.update(
        ProvinceCoverage.objects.values_list("province_id", flat=True)
    )
    province_ids.discard(None)

    total_provincial_obcs = Province.objects.filter(pk__in=province_ids).count()

    # Additional demographic statistics
    vulnerable_sectors = communities.aggregate(
        total_women=Sum("women_count"),
        total_pwd=Sum("pwd_count"),
        total_elderly=Sum("elderly_count"),
        total_idps=Sum("idps_count"),
        total_farmers=Sum("farmers_count"),
        total_fisherfolk=Sum("fisherfolk_count"),
        total_teachers_asatidz=Sum("teachers_asatidz_count"),
        total_religious_leaders_ulama=Sum("religious_leaders_ulama_count"),
        total_csos=Sum("csos_count"),
        total_associations=Sum("associations_count"),
    )

    # Infrastructure statistics
    infrastructure_stats = (
        CommunityInfrastructure.objects.filter(
            availability_status__in=["limited", "poor", "none"]
        )
        .values("infrastructure_type")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    # Unemployment rate breakdown
    unemployment_rates = (
        communities.values("unemployment_rate")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Ethnolinguistic group distribution
    ethnolinguistic_groups = (
        communities.exclude(primary_ethnolinguistic_group__isnull=True)
        .exclude(primary_ethnolinguistic_group="")
        .values("primary_ethnolinguistic_group")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

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
            "recent": communities.order_by("-created_at")[:10],
            "unemployment_rates": unemployment_rates,
            "with_madrasah": communities.filter(has_madrasah=True).count(),
            "with_mosque": communities.filter(has_mosque=True).count(),
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
    }

    context = {
        "stats": stats,
        "communities": communities[:20],  # Show first 20 communities
    }
    return render(request, "communities/communities_home.html", context)


@login_required
def communities_add(request):
    """Add new community page."""
    if request.method == "POST":
        form = OBCCommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            # Set any additional fields if needed
            community.save()
            messages.success(
                request,
                f'Community "{community.barangay.name}" has been successfully added.',
            )
            return redirect("communities:communities_manage")
    else:
        form = OBCCommunityForm()

    # Get recent communities for reference
    recent_communities = OBCCommunity.objects.order_by("-created_at")[:5]
    barangays = Barangay.objects.select_related(
        "municipality__province__region"
    ).order_by("municipality__province__region__name", "municipality__name", "name")

    context = {
        "form": form,
        "recent_communities": recent_communities,
        "barangays": barangays,
    }
    return render(request, "communities/communities_add.html", context)


def _render_manage_obc(request, scope="barangay"):
    """Shared renderer for managing OBC records at different administrative levels."""
    from django.db.models import Count, Sum
    from django.db.models import Q

    show_archived = request.GET.get("archived") == "1"

    base_manager = OBCCommunity.all_objects if show_archived else OBCCommunity.objects

    # Base queryset for communities with related data
    communities = (
        base_manager.select_related("barangay__municipality__province__region")
        .annotate(stakeholder_count=Count("stakeholders"))
        .order_by("barangay__name")
    )

    if show_archived:
        communities = communities.filter(is_deleted=True)

    # Filters
    region_filter = request.GET.get("region")
    status_filter = request.GET.get("status")
    search_query = request.GET.get("search")

    if region_filter:
        communities = communities.filter(
            barangay__municipality__province__region__id=region_filter
        )

    if status_filter:
        if status_filter == "active":
            communities = communities.filter(is_active=True)
        elif status_filter == "inactive":
            communities = communities.filter(is_active=False)

    if search_query:
        communities = communities.filter(
            Q(barangay__name__icontains=search_query)
            | Q(barangay__municipality__name__icontains=search_query)
            | Q(barangay__municipality__province__name__icontains=search_query)
            | Q(barangay__municipality__province__region__name__icontains=search_query)
        )

    total_communities = communities.count()
    total_obc_population = (
        communities.aggregate(total=Sum("estimated_obc_population"))["total"] or 0
    )
    municipality_ids = set(
        communities.values_list("barangay__municipality_id", flat=True)
    )
    total_municipalities = len(municipality_ids)

    # Municipal-level synchronization breakdown based on assessment activity
    manual_municipality_ids = set(
        communities.filter(needs_assessment_date__isnull=False).values_list(
            "barangay__municipality_id", flat=True
        )
    )
    manual_municipalities = len(manual_municipality_ids)
    auto_synced_municipalities = max(total_municipalities - manual_municipalities, 0)

    if scope == "municipal":
        if show_archived:
            page_title = "Archived Municipal OBCs"
            page_description = (
                "Review archived municipality-level records and restore when needed."
            )
        else:
            page_title = "Manage Municipal OBCs"
            page_description = (
                "Monitor municipal-level OBC records and synchronization status."
            )
        stat_cards = [
            {
                "title": (
                    "Total Municipal OBCs in the Database"
                    if not show_archived
                    else "Total Archived Municipal OBCs"
                ),
                "value": total_municipalities,
                "icon": "fas fa-city",
                "gradient": "from-blue-500 via-blue-600 to-blue-700",
                "text_color": "text-blue-100",
            },
            {
                "title": (
                    "Total OBC Population from the Municipalities"
                    if not show_archived
                    else "Archived OBC Population Total"
                ),
                "value": total_obc_population,
                "icon": "fas fa-users",
                "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
                "text_color": "text-emerald-100",
            },
            {
                "title": "Auto-Synced Municipalities",
                "value": auto_synced_municipalities,
                "icon": "fas fa-sync-alt",
                "gradient": "from-purple-500 via-purple-600 to-purple-700",
                "text_color": "text-purple-100",
            },
            {
                "title": "Manually Updated Municipalities",
                "value": manual_municipalities,
                "icon": "fas fa-edit",
                "gradient": "from-orange-500 via-orange-600 to-orange-700",
                "text_color": "text-orange-100",
            },
        ]
    else:
        if show_archived:
            page_title = "Archived Barangay OBCs"
            page_description = (
                "Review archived barangay-level records and restore when appropriate."
            )
        else:
            page_title = "Manage Barangay OBCs"
            page_description = (
                "View, edit, and manage all registered barangay-level OBC communities."
            )
        stat_cards = [
            {
                "title": (
                    "Total Barangay OBCs in the Database"
                    if not show_archived
                    else "Total Archived Barangay OBCs"
                ),
                "value": total_communities,
                "icon": "fas fa-users",
                "gradient": "from-blue-500 via-blue-600 to-blue-700",
                "text_color": "text-blue-100",
            },
            {
                "title": (
                    "Total OBC Population from Barangays"
                    if not show_archived
                    else "Archived OBC Population Total"
                ),
                "value": total_obc_population,
                "icon": "fas fa-user-friends",
                "gradient": "from-emerald-500 via-emerald-600 to-emerald-700",
                "text_color": "text-emerald-100",
            },
            {
                "title": "Total Municipalities OBCs in the Database",
                "value": total_municipalities,
                "icon": "fas fa-city",
                "gradient": "from-purple-500 via-purple-600 to-purple-700",
                "text_color": "text-purple-100",
            },
        ]

    lg_columns = 4 if len(stat_cards) >= 4 else 3
    stat_cards_grid_class = (
        f"mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-{lg_columns} gap-6"
    )

    regions = Region.objects.all().order_by("name")

    context = {
        "communities": communities,
        "regions": regions,
        "current_region": region_filter,
        "current_status": status_filter,
        "search_query": search_query,
        "total_communities": total_communities,
        "total_population": total_obc_population,
        "total_municipalities": total_municipalities,
        "stat_cards": stat_cards,
        "stat_cards_grid_class": stat_cards_grid_class,
        "page_title": page_title,
        "page_description": page_description,
        "view_scope": scope,
        "show_archived": show_archived,
    }
    return render(request, "communities/communities_manage.html", context)


@login_required
def communities_manage(request):
    """Manage communities page (barangay scope by default)."""
    return _render_manage_obc(request, scope="barangay")


@login_required
def communities_manage_barangay_obc(request):
    """Explicit barangay-level management view."""
    return _render_manage_obc(request, scope="barangay")


@login_required
def communities_manage_municipal_obc(request):
    """Municipal-level OBC management view."""
    return _render_manage_obc(request, scope="municipal")


@login_required
def communities_stakeholders(request):
    """Manage stakeholders page."""
    from django.db.models import Count

    # Get all stakeholders with related data
    stakeholders = Stakeholder.objects.select_related(
        "community", "community__barangay__municipality__province__region"
    ).prefetch_related("engagements")

    # Filter functionality
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

    # Get filter options
    communities = OBCCommunity.objects.order_by("barangay__name")
    stakeholder_types = Stakeholder.STAKEHOLDER_TYPES

    # Statistics
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


# Geographic Data Views


@moa_view_only
@login_required
def add_data_layer(request):
    """Create a new geographic data layer."""
    if request.method == "POST":
        form = GeographicDataLayerForm(request.POST, user=request.user)
        if form.is_valid():
            layer = form.save()
            messages.success(
                request,
                f'Geographic data layer "{layer.name}" has been created successfully.',
            )
            return redirect("communities:geographic_data_list")
    else:
        form = GeographicDataLayerForm(user=request.user)

    context = {
        "form": form,
        "title": "Add Geographic Data Layer",
    }
    return render(request, "communities/add_data_layer.html", context)


@moa_view_only
@login_required
def create_visualization(request):
    """Create a new map visualization."""
    if request.method == "POST":
        form = MapVisualizationForm(request.POST, user=request.user)
        if form.is_valid():
            visualization = form.save()
            messages.success(
                request,
                f'Map visualization "{visualization.title}" has been created successfully.',
            )
            return redirect("communities:geographic_data_list")
    else:
        form = MapVisualizationForm(user=request.user)

    context = {
        "form": form,
        "title": "Create Map Visualization",
    }
    return render(request, "communities/create_visualization.html", context)


@moa_view_only
@login_required
def geographic_data_list(request):
    """List geographic data layers and visualizations."""
    data_layers = GeographicDataLayer.objects.all().order_by("-created_at")
    visualizations = MapVisualization.objects.all().order_by("-created_at")

    map_layers, map_config = serialize_layers_for_map(data_layers)

    # Basic statistics
    stats = {
        "total_layers": data_layers.count(),
        "total_visualizations": visualizations.count(),
        "communities_mapped": OBCCommunity.objects.filter(
            Q(geographic_layers__isnull=False)
            | Q(community_map_visualizations__isnull=False)
        )
        .distinct()
        .count(),
        "active_layers": data_layers.filter(is_visible=True).count(),
    }

    context = {
        "data_layers": data_layers[:10],  # Show first 10
        "visualizations": visualizations[:10],  # Show first 10
        "stats": stats,
        "title": "Geographic Data & Mapping",
        "map_layers": map_layers,
        "map_config": map_config,
    }
    return render(request, "communities/geographic_data_list.html", context)
