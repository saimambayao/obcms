from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.utils import timezone
from .models import User, Region, Province, Municipality, Barangay
from .forms import UserRegistrationForm, CustomLoginForm

# 5 Standard PPS (Policy, Program, Service) Areas for Recommendations
RECOMMENDATIONS_AREAS = {
    "economic-development": {
        "name": "Economic Development",
        "categories": ["economic_development"],
        "icon": "fas fa-chart-line",
        "color": "green",
    },
    "social-development": {
        "name": "Social Development",
        "categories": ["social_development"],
        "icon": "fas fa-users",
        "color": "purple",
    },
    "cultural-development": {
        "name": "Cultural Development",
        "categories": ["cultural_development"],
        "icon": "fas fa-mosque",
        "color": "orange",
    },
    "rehabilitation-development": {
        "name": "Rehabilitation & Development",
        "categories": ["infrastructure", "environment"],
        "icon": "fas fa-hammer",
        "color": "blue",
    },
    "protection-rights": {
        "name": "Protection of Rights",
        "categories": ["human_rights"],
        "icon": "fas fa-balance-scale",
        "color": "red",
    },
}


class CustomLoginView(LoginView):
    """Custom login view with OBC branding and approval check."""

    template_name = "common/login.html"
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Check if user is approved before allowing login."""
        user = form.get_user()
        if not user.is_approved and not user.is_superuser:
            messages.error(
                self.request,
                "Your account is pending approval. Please contact the administrator.",
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view."""

    next_page = reverse_lazy("common:login")

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


class UserRegistrationView(CreateView):
    """User registration view with approval workflow."""

    model = User
    form_class = UserRegistrationForm
    template_name = "common/register.html"
    success_url = reverse_lazy("common:login")

    def form_valid(self, form):
        """Set user as pending approval after registration."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Registration successful! Your account is pending approval. "
            "You will be notified once your account is approved.",
        )
        return response


@login_required
def dashboard(request):
    """Main dashboard view after login."""
    user = request.user

    if (
        not user.is_staff
        and not user.is_superuser
        and user.has_perm("mana.can_access_regional_mana")
        and not user.has_perm("mana.can_facilitate_workshop")
    ):
        participant_account = getattr(user, "workshop_participant_account", None)
        if participant_account:
            return redirect(
                "mana:participant_dashboard",
                assessment_id=participant_account.assessment_id,
            )

    from communities.models import OBCCommunity, Stakeholder
    from mana.models import Assessment, Need
    from coordination.models import Partnership
    from policy_tracking.models import PolicyRecommendation
    from common.work_item_model import WorkItem
    from django.db.models import Count

    # Get dashboard statistics
    stats = {
        "communities": {
            "total": OBCCommunity.objects.count(),
            "active": OBCCommunity.objects.filter(is_active=True).count(),
            "by_region": OBCCommunity.objects.values(
                "barangay__municipality__province__region__name"
            ).annotate(count=Count("id"))[:5],
            "recent": OBCCommunity.objects.order_by("-created_at")[:5],
        },
        "mana": {
            "total_assessments": Assessment.objects.count(),
            "completed": Assessment.objects.filter(status="completed").count(),
            "in_progress": Assessment.objects.filter(
                status__in=["data_collection", "analysis"]
            ).count(),
            "high_priority": Need.objects.filter(impact_severity=5).count(),
        },
        "coordination": {
            "total_events": WorkItem.objects.filter(work_type='activity').count(),
            "active_partnerships": Partnership.objects.filter(status="active").count(),
            "upcoming_events": WorkItem.objects.filter(
                work_type='activity',
                start_date__gte=timezone.now().date(),
                status="planned"
            ).count(),
            "pending_actions": 0,  # Will be calculated if ActionItem model exists
            # Partnership breakdown by organization type
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
            # Recommendations breakdown by category
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
    }

    # Check if user is a MANA participant and get their assessment ID
    participant_account = getattr(user, "workshop_participant_account", None)
    participant_assessment_id = None
    if participant_account:
        participant_assessment_id = str(participant_account.assessment_id)

    context = {
        "user": request.user,
        "user_type_display": request.user.get_user_type_display(),
        "is_approved": request.user.is_approved,
        "stats": stats,
        "participant_assessment_id": participant_assessment_id,
    }
    return render(request, "common/dashboard.html", context)


@login_required
def dashboard_stats_cards(request):
    """Return just the dashboard stat cards for HTMX auto-refresh."""
    from communities.models import OBCCommunity
    from mana.models import Assessment
    from coordination.models import Partnership
    from policy_tracking.models import PolicyRecommendation

    # Calculate stats (same as dashboard view but only what's needed for cards)
    stats = {
        "communities": {
            "total": OBCCommunity.objects.count(),
            "barangay_total": OBCCommunity.objects.filter(
                barangay__isnull=False
            ).count(),
            "municipal_total": OBCCommunity.objects.filter(
                municipality__isnull=False
            ).count(),
        },
        "mana": {
            "total_assessments": Assessment.objects.count(),
        },
        "coordination": {
            "active_partnerships": Partnership.objects.filter(status="active").count(),
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
        "monitoring": {
            "total": 0,
            "pending_requests": 0,
            "avg_progress": 0,
        },
    }

    return render(request, "partials/dashboard_stats_cards.html", {"stats": stats})


@login_required
def profile(request):
    """User profile view."""
    context = {
        "user": request.user,
    }
    return render(request, "common/profile.html", context)


@login_required
def communities_home(request):
    """OBC Communities module home page."""
    from communities.models import (
        OBCCommunity,
        MunicipalityCoverage,
        ProvinceCoverage,
        Stakeholder,
        CommunityInfrastructure,
    )
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
    }

    context = {
        "stats": stats,
        "communities": communities[:20],  # Show first 20 communities
    }
    return render(request, "common/communities_home.html", context)


@login_required
def mana_home(request):
    """MANA module home page."""
    from mana.models import Assessment, Need, BaselineStudy
    from django.db.models import Count, Q

    # Get MANA statistics
    assessments = Assessment.objects.select_related("community", "category")
    needs = Need.objects.select_related("category", "assessment")
    baseline_studies = BaselineStudy.objects.select_related("community")

    # Calculate assessment metrics
    total_assessments = assessments.count()
    completed_assessments = assessments.filter(status="completed").count()
    in_progress_assessments = assessments.filter(
        status__in=["data_collection", "analysis"]
    ).count()
    planned_assessments = assessments.filter(
        status__in=["planning", "preparation"]
    ).count()

    # Calculate assessments by area/category (based on category name containing keywords)
    education_assessments = assessments.filter(
        Q(category__name__icontains="education")
        | Q(category__category_type__icontains="education")
    ).count()
    economic_assessments = assessments.filter(
        Q(category__name__icontains="economic")
        | Q(category__category_type__icontains="economic")
    ).count()
    social_assessments = assessments.filter(
        Q(category__name__icontains="social")
        | Q(category__category_type__icontains="social")
    ).count()
    cultural_assessments = assessments.filter(
        Q(category__name__icontains="cultural")
        | Q(category__category_type__icontains="cultural")
    ).count()
    infrastructure_assessments = assessments.filter(
        Q(category__name__icontains="infrastructure")
        | Q(category__category_type__icontains="infrastructure")
    ).count()

    stats = {
        "mana": {
            "total_assessments": total_assessments,
            "completed": completed_assessments,
            "in_progress": in_progress_assessments,
            "planned": planned_assessments,
            "by_area": {
                "education": education_assessments,
                "economic": economic_assessments,
                "social": social_assessments,
                "cultural": cultural_assessments,
                "infrastructure": infrastructure_assessments,
            },
        },
        "assessments": {
            "total": total_assessments,
            "completed": completed_assessments,
            "ongoing": in_progress_assessments,
            "by_status": assessments.values("status").annotate(count=Count("id")),
            "recent": assessments.order_by("-created_at")[:10],
        },
        "needs": {
            "total": needs.count(),
            "critical": needs.filter(urgency_level="immediate").count(),
            "by_category": needs.values("category__name").annotate(count=Count("id"))[
                :10
            ],
            "recent": needs.order_by("-created_at")[:10],
        },
        "baseline_studies": {
            "total": baseline_studies.count(),
            "completed": baseline_studies.filter(status="completed").count(),
            "ongoing": baseline_studies.filter(
                status__in=["data_collection", "analysis"]
            ).count(),
        },
    }

    context = {
        "stats": stats,
    }
    return render(request, "common/mana_home.html", context)


@login_required
def coordination_home(request):
    """Coordination module home page - Coordination with BMOAs, NGAs, and LGUs."""
    from coordination.models import (
        Partnership,
        Organization,
        StakeholderEngagement,
        PartnershipSignatory,
    )
    from common.work_item_model import WorkItem
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta

    # Get coordination statistics for BMOAs, NGAs, and LGUs
    now = timezone.now()

    # 1. Mapped Partners (Organizations that have been registered and researched)
    # Organizations that are active and have description/mandate information (indicating research)
    mapped_partners = Organization.objects.filter(
        is_active=True, organization_type__in=["bmoa", "nga", "lgu"]
    ).exclude(description="")

    mapped_partners_stats = {
        "total": mapped_partners.count(),
        "bmoa": mapped_partners.filter(organization_type="bmoa").count(),
        "nga": mapped_partners.filter(organization_type="nga").count(),
        "lgu": mapped_partners.filter(organization_type="lgu").count(),
    }

    # 2. Active Partnerships
    active_partnerships = Partnership.objects.filter(status="active")

    # Count partnerships by organization type involved through signatories
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

    # 3. Coordination Activities Done (Completed activities and engagements)
    completed_activities = WorkItem.objects.filter(
        work_type='activity',
        status="completed"
    )
    completed_engagements = StakeholderEngagement.objects.filter(status="completed")

    total_completed_activities = (
        completed_activities.count() + completed_engagements.count()
    )

    # Note: Organization type filtering for activities requires participant tracking
    # which may be stored in activity_data JSON field or related EventParticipant model
    # For now, using total counts without organization breakdown
    coordination_activities_done_stats = {
        "total": total_completed_activities,
        "bmoa": 0,  # TODO: Implement participant tracking in WorkItem
        "nga": 0,   # TODO: Implement participant tracking in WorkItem
        "lgu": 0,   # TODO: Implement participant tracking in WorkItem
    }

    # 4. Planned Coordination Activities (Upcoming activities and planned engagements)
    planned_activities = WorkItem.objects.filter(
        work_type='activity',
        status__in=["not_started", "in_progress"],
        start_date__gte=now.date()
    )

    planned_engagements = StakeholderEngagement.objects.filter(
        status__in=["planned", "scheduled"], planned_date__gte=now
    )

    total_planned_activities = planned_activities.count() + planned_engagements.count()

    # Note: Organization type filtering requires participant tracking
    planned_coordination_activities_stats = {
        "total": total_planned_activities,
        "bmoa": 0,  # TODO: Implement participant tracking in WorkItem
        "nga": 0,   # TODO: Implement participant tracking in WorkItem
        "lgu": 0,   # TODO: Implement participant tracking in WorkItem
    }

    # Recent activities for display
    recent_activities = WorkItem.objects.filter(
        work_type='activity',
        start_date__gte=now.date() - timedelta(days=30)
    ).order_by("-start_date")[:5]

    # Activity categories breakdown (by event_type in activity_data)
    # Note: event_type is stored in activity_data JSON field
    all_activities = WorkItem.objects.filter(work_type='activity')
    event_by_type = {
        "meeting": sum(1 for a in all_activities if a.activity_data.get("event_type") == "meeting"),
        "workshop": sum(1 for a in all_activities if a.activity_data.get("event_type") == "workshop"),
        "conference": sum(1 for a in all_activities if a.activity_data.get("event_type") == "conference"),
        "consultation": sum(1 for a in all_activities if a.activity_data.get("event_type") == "consultation"),
    }

    # Active partnerships list for display
    active_partnerships_list = Partnership.objects.filter(status="active").order_by(
        "-created_at"
    )[:5]

    stats = {
        "mapped_partners": mapped_partners_stats,
        "active_partnerships": active_partnerships_stats,
        "coordination_activities_done": coordination_activities_done_stats,
        "planned_coordination_activities": planned_coordination_activities_stats,
        "recent_events": recent_activities,  # Using WorkItem activities
        "coordination": {
            "active_partnerships": active_partnerships_list,
            "by_type": event_by_type,
        },
    }

    context = {
        "stats": stats,
    }
    return render(request, "common/coordination_home.html", context)


@login_required
def recommendations_home(request):
    """Recommendations Tracking module home page."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count, Q

    # Get recommendations tracking statistics
    recommendations = PolicyRecommendation.objects.select_related(
        "proposed_by", "lead_author"
    )
    evidence = PolicyEvidence.objects.select_related("policy")

    # Define recommendation types
    policy_categories = ["governance", "legal_framework", "administrative"]
    program_categories = [
        "education",
        "economic_development",
        "social_development",
        "cultural_development",
    ]
    service_categories = ["healthcare", "infrastructure", "environment", "human_rights"]

    # Define status mappings
    submitted_statuses = [
        "submitted",
        "under_consideration",
        "approved",
        "in_implementation",
        "implemented",
    ]
    proposed_statuses = ["draft", "under_review", "needs_revision"]

    # Calculate main metrics
    total_recommendations = recommendations.count()
    total_implemented = recommendations.filter(status="implemented").count()
    total_submitted = recommendations.filter(status__in=submitted_statuses).count()
    total_proposed = recommendations.filter(status__in=proposed_statuses).count()

    # Calculate breakdown by type
    policies_total = recommendations.filter(category__in=policy_categories).count()
    programs_total = recommendations.filter(category__in=program_categories).count()
    services_total = recommendations.filter(category__in=service_categories).count()

    # Implemented breakdown
    implemented_policies = recommendations.filter(
        status="implemented", category__in=policy_categories
    ).count()
    implemented_programs = recommendations.filter(
        status="implemented", category__in=program_categories
    ).count()
    implemented_services = recommendations.filter(
        status="implemented", category__in=service_categories
    ).count()

    # Submitted breakdown
    submitted_policies = recommendations.filter(
        status__in=submitted_statuses, category__in=policy_categories
    ).count()
    submitted_programs = recommendations.filter(
        status__in=submitted_statuses, category__in=program_categories
    ).count()
    submitted_services = recommendations.filter(
        status__in=submitted_statuses, category__in=service_categories
    ).count()

    # Proposed breakdown
    proposed_policies = recommendations.filter(
        status__in=proposed_statuses, category__in=policy_categories
    ).count()
    proposed_programs = recommendations.filter(
        status__in=proposed_statuses, category__in=program_categories
    ).count()
    proposed_services = recommendations.filter(
        status__in=proposed_statuses, category__in=service_categories
    ).count()

    # Area breakdowns using the 5 standard areas
    economic_development = recommendations.filter(
        category="economic_development"
    ).count()
    social_development = recommendations.filter(category="social_development").count()
    cultural_development = recommendations.filter(
        category="cultural_development"
    ).count()
    rehabilitation_development = recommendations.filter(
        category__in=["infrastructure", "environment"]
    ).count()
    protection_rights = recommendations.filter(category="human_rights").count()

    stats = {
        "recommendations": {
            "total": total_recommendations,
            "implemented": total_implemented,
            "submitted": total_submitted,
            "proposed": total_proposed,
            "policies": policies_total,
            "programs": programs_total,
            "services": services_total,
            "implemented_policies": implemented_policies,
            "implemented_programs": implemented_programs,
            "implemented_services": implemented_services,
            "submitted_policies": submitted_policies,
            "submitted_programs": submitted_programs,
            "submitted_services": submitted_services,
            "proposed_policies": proposed_policies,
            "proposed_programs": proposed_programs,
            "proposed_services": proposed_services,
        },
        "areas": {
            "economic_development": economic_development,
            "social_development": social_development,
            "cultural_development": cultural_development,
            "rehabilitation_development": rehabilitation_development,
            "protection_rights": protection_rights,
        },
        "recommendations_tracking": {
            "recent_recommendations": recommendations.order_by("-created_at")[:5],
            "recent_evidence": evidence.order_by("-date_added")[:5],
        },
        "areas_data": RECOMMENDATIONS_AREAS,
    }

    context = {
        "stats": stats,
    }
    return render(request, "common/recommendations_home.html", context)


@login_required
def communities_add(request):
    """Add new community page."""
    from communities.models import OBCCommunity
    from common.models import Barangay
    from .forms import OBCCommunityForm

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
    return render(request, "common/communities_add.html", context)


def _render_manage_obc(request, scope="barangay"):
    """Shared renderer for managing OBC records at different administrative levels."""
    from communities.models import OBCCommunity
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
    return render(request, "common/communities_manage.html", context)


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
    from communities.models import Stakeholder, OBCCommunity
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
    return render(request, "common/communities_stakeholders.html", context)


@login_required
def mana_new_assessment(request):
    """New MANA assessment page."""
    from mana.models import Assessment, NeedsCategory
    from communities.models import OBCCommunity

    # Get recent assessments for reference
    recent_assessments = Assessment.objects.order_by("-created_at")[:5]
    communities = OBCCommunity.objects.filter(is_active=True).order_by("barangay__name")
    categories = NeedsCategory.objects.all().order_by("name")

    context = {
        "recent_assessments": recent_assessments,
        "communities": communities,
        "categories": categories,
    }
    return render(request, "common/mana_new_assessment.html", context)


@login_required
def mana_manage_assessments(request):
    """Manage MANA assessments page."""
    from mana.models import Assessment, Need
    from django.db.models import Count

    # Get all assessments with related data
    assessments = (
        Assessment.objects.select_related("community", "category", "lead_assessor")
        .annotate(needs_count=Count("identified_needs"))
        .order_by("-created_at")
    )

    # Filter functionality
    status_filter = request.GET.get("status")
    community_filter = request.GET.get("community")

    if status_filter:
        assessments = assessments.filter(status=status_filter)

    if community_filter:
        assessments = assessments.filter(community__id=community_filter)

    # Get filter options
    from communities.models import OBCCommunity

    communities = OBCCommunity.objects.order_by("barangay__name")
    status_choices = (
        Assessment.STATUS_CHOICES if hasattr(Assessment, "STATUS_CHOICES") else []
    )

    # Statistics
    stats = {
        "total_assessments": assessments.count(),
        "completed": assessments.filter(status="completed").count(),
        "in_progress": assessments.filter(
            status__in=["data_collection", "analysis"]
        ).count(),
        "pending": assessments.filter(status="pending").count(),
    }

    context = {
        "assessments": assessments,
        "communities": communities,
        "status_choices": status_choices,
        "current_status": status_filter,
        "current_community": community_filter,
        "stats": stats,
    }
    return render(request, "common/mana_manage_assessments.html", context)


@login_required
def mana_geographic_data(request):
    """Delegate to domain-specific MANA geographic data view."""
    from .mana import mana_geographic_data as module_mana_geographic_data

    return module_mana_geographic_data(request)


@login_required
def coordination_organizations(request):
    """Manage coordination organizations page."""
    from coordination.models import Organization, OrganizationContact
    from django.db.models import Count

    # Get all organizations with related data
    organizations = Organization.objects.annotate(
        contacts_count=Count("contacts"), partnerships_count=Count("led_partnerships")
    ).order_by("name")

    # Filter functionality
    type_filter = request.GET.get("type")
    status_filter = request.GET.get("status")

    if type_filter:
        organizations = organizations.filter(organization_type=type_filter)

    if status_filter == "active":
        organizations = organizations.filter(is_active=True)
    elif status_filter == "inactive":
        organizations = organizations.filter(is_active=False)

    # Get filter options
    org_types = (
        Organization.ORGANIZATION_TYPE_CHOICES
        if hasattr(Organization, "ORGANIZATION_TYPE_CHOICES")
        else []
    )

    # Statistics
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
        "stats": stats,
    }
    return render(request, "common/coordination_organizations.html", context)


@login_required
def coordination_partnerships(request):
    """Manage coordination partnerships page."""
    from coordination.models import Partnership, Organization
    from django.db.models import Count

    # Get all partnerships with related data
    partnerships = (
        Partnership.objects.select_related("lead_organization")
        .annotate(signatories_count=Count("signatories"))
        .order_by("-created_at")
    )

    # Filter functionality
    status_filter = request.GET.get("status")
    type_filter = request.GET.get("type")

    if status_filter:
        partnerships = partnerships.filter(status=status_filter)

    if type_filter:
        partnerships = partnerships.filter(partnership_type=type_filter)

    # Get filter options
    status_choices = (
        Partnership.STATUS_CHOICES if hasattr(Partnership, "STATUS_CHOICES") else []
    )
    type_choices = (
        Partnership.PARTNERSHIP_TYPE_CHOICES
        if hasattr(Partnership, "PARTNERSHIP_TYPE_CHOICES")
        else []
    )

    # Statistics
    stats = {
        "total_partnerships": partnerships.count(),
        "active_partnerships": partnerships.filter(status="active").count(),
        "pending_partnerships": partnerships.filter(status="pending").count(),
        "by_type": partnerships.values("partnership_type").annotate(count=Count("id")),
    }

    context = {
        "partnerships": partnerships,
        "status_choices": status_choices,
        "type_choices": type_choices,
        "current_status": status_filter,
        "current_type": type_filter,
        "stats": stats,
    }
    return render(request, "common/coordination_partnerships.html", context)


@login_required
def coordination_events(request):
    """Coordination management dashboard."""
    from coordination.models import Event, EventParticipant
    from django.db.models import Count
    from django.utils import timezone

    # Get all events with related data
    events = (
        Event.objects.select_related("community", "organizer")
        .annotate(participants_count=Count("participants"))
        .order_by("-start_date")
    )

    # Filter functionality
    status_filter = request.GET.get("status")
    type_filter = request.GET.get("type")

    if status_filter:
        events = events.filter(status=status_filter)

    if type_filter:
        events = events.filter(event_type=type_filter)

    # Get filter options
    status_choices = Event.STATUS_CHOICES if hasattr(Event, "STATUS_CHOICES") else []
    type_choices = (
        Event.EVENT_TYPE_CHOICES if hasattr(Event, "EVENT_TYPE_CHOICES") else []
    )

    # Separate upcoming and past events
    now = timezone.now().date()
    upcoming_events = events.filter(start_date__gte=now)
    past_events = events.filter(start_date__lt=now)

    # Statistics
    stats = {
        "total_coordination": events.count(),
        "upcoming_coordination": upcoming_events.count(),
        "completed_coordination": events.filter(status="completed").count(),
        "past_coordination": past_events.count(),
        "total_participants": EventParticipant.objects.count(),
    }

    context = {
        "events": events,
        "upcoming_events": upcoming_events[:10],
        "past_events": past_events[:10],
        "status_choices": status_choices,
        "type_choices": type_choices,
        "current_status": status_filter,
        "current_type": type_filter,
        "stats": stats,
        "total_coordination_count": stats["total_coordination"],
        "upcoming_coordination_count": stats["upcoming_coordination"],
        "completed_coordination_count": stats["completed_coordination"],
        "total_participants_count": stats["total_participants"],
    }
    return render(request, "common/coordination_events.html", context)


@login_required
def coordination_view_all(request):
    """Coordination overview and reports page."""
    from coordination.models import Partnership, Organization
    from common.work_item_model import WorkItem
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    # Get comprehensive coordination data
    activities = WorkItem.objects.filter(work_type='activity')
    partnerships = Partnership.objects.select_related("lead_organization")
    organizations = Organization.objects.filter(is_active=True)

    # Time-based statistics
    now = timezone.now()
    last_30_days = now.date() - timedelta(days=30)

    # Comprehensive statistics
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
            "recent": activities.filter(start_date__gte=last_30_days).count(),
            # Note: event_type is in activity_data JSON field, cannot use values/annotate
            "by_type": [],  # TODO: Implement JSON field aggregation
        },
    }

    # Recent activity
    recent_events = activities.order_by("-created_at")[:5]
    recent_partnerships = partnerships.order_by("-created_at")[:5]

    context = {
        "stats": stats,
        "recent_events": recent_events,
        "recent_partnerships": recent_partnerships,
        "organizations": organizations[:10],
    }
    return render(request, "common/coordination_view_all.html", context)


@login_required
def recommendations_new(request):
    """Create new recommendation page."""
    from policy_tracking.models import PolicyRecommendation

    # Get recent recommendations for reference
    recent_recommendations = PolicyRecommendation.objects.order_by("-created_at")[:5]

    context = {
        "recent_recommendations": recent_recommendations,
        "areas_data": RECOMMENDATIONS_AREAS,
    }
    return render(request, "common/recommendations_new.html", context)


@login_required
def recommendations_manage(request):
    """Manage recommendations page."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count

    # Get all recommendations with related data
    recommendations = (
        PolicyRecommendation.objects.select_related(
            "proposed_by", "lead_author", "assigned_reviewer"
        )
        .annotate(evidence_count=Count("evidence"))
        .order_by("-created_at")
    )

    # Filter functionality
    status_filter = request.GET.get("status")
    category_filter = request.GET.get("category")
    area_filter = request.GET.get("area")

    if status_filter:
        recommendations = recommendations.filter(status=status_filter)

    if category_filter:
        recommendations = recommendations.filter(category=category_filter)

    if area_filter and area_filter in RECOMMENDATIONS_AREAS:
        area_categories = RECOMMENDATIONS_AREAS[area_filter]["categories"]
        recommendations = recommendations.filter(category__in=area_categories)

    # Get filter options
    status_choices = (
        PolicyRecommendation.STATUS_CHOICES
        if hasattr(PolicyRecommendation, "STATUS_CHOICES")
        else []
    )
    category_choices = (
        PolicyRecommendation.CATEGORY_CHOICES
        if hasattr(PolicyRecommendation, "CATEGORY_CHOICES")
        else []
    )

    # Statistics
    stats = {
        "total_recommendations": recommendations.count(),
        "implemented": recommendations.filter(status="implemented").count(),
        "under_review": recommendations.filter(status="under_review").count(),
        "approved": recommendations.filter(status="approved").count(),
    }

    context = {
        "recommendations": recommendations,
        "status_choices": status_choices,
        "category_choices": category_choices,
        "current_status": status_filter,
        "current_category": category_filter,
        "current_area": area_filter,
        "stats": stats,
        "areas_data": RECOMMENDATIONS_AREAS,
    }
    return render(request, "common/recommendations_manage.html", context)


@login_required
def recommendations_by_area(request, area_slug):
    """View recommendations filtered by specific area."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count, Q
    from django.http import Http404

    # Validate area slug
    if area_slug not in RECOMMENDATIONS_AREAS:
        raise Http404("Area not found")

    area_info = RECOMMENDATIONS_AREAS[area_slug]
    area_categories = area_info["categories"]

    # Get recommendations for this area
    recommendations = (
        PolicyRecommendation.objects.filter(category__in=area_categories)
        .select_related("proposed_by", "lead_author")
        .annotate(evidence_count=Count("evidence"))
    )

    # Define status mappings
    submitted_statuses = [
        "submitted",
        "under_consideration",
        "approved",
        "in_implementation",
        "implemented",
    ]
    proposed_statuses = ["draft", "under_review", "needs_revision"]

    # Calculate area-specific metrics
    total_area_recommendations = recommendations.count()
    implemented_area = recommendations.filter(status="implemented").count()
    submitted_area = recommendations.filter(status__in=submitted_statuses).count()
    proposed_area = recommendations.filter(status__in=proposed_statuses).count()

    # Get filter parameter
    status_filter = request.GET.get("status")
    if status_filter:
        if status_filter == "proposed":
            recommendations = recommendations.filter(status__in=proposed_statuses)
        elif status_filter == "submitted":
            recommendations = recommendations.filter(status__in=submitted_statuses)
        elif status_filter == "implemented":
            recommendations = recommendations.filter(status="implemented")

    # Recent recommendations for this area
    recent_recommendations = recommendations.order_by("-created_at")[:10]

    stats = {
        "area_info": area_info,
        "total": total_area_recommendations,
        "implemented": implemented_area,
        "submitted": submitted_area,
        "proposed": proposed_area,
        "current_filter": status_filter,
    }

    context = {
        "area_slug": area_slug,
        "area_info": area_info,
        "stats": stats,
        "recommendations": recent_recommendations,
        "current_filter": status_filter,
    }
    return render(request, "common/recommendations_by_area.html", context)


# ========================================
# PHASE 2: PLANNING & BUDGETING DASHBOARDS
# ========================================


@login_required
def gap_analysis_dashboard(request):
    """
    Gap Analysis Dashboard - Show unfunded community needs.

    Part of Phase 2 implementation for evidence-based budgeting.
    Displays high-priority needs that don't have budget linkage.
    """
    from mana.models import Need
    from django.db.models import Q, Count, Sum

    # Get filter parameters
    region_id = request.GET.get("region")
    category_id = request.GET.get("category")
    urgency = request.GET.get("urgency")
    submission_type = request.GET.get("submission_type")

    # Base query: needs that are validated/prioritized but not linked to budget
    unfunded_needs = Need.objects.filter(
        Q(linked_ppa__isnull=True),  # Not linked to any PPA
        status__in=["validated", "prioritized"],  # Only validated needs
    ).select_related(
        "community__barangay__municipality__province__region",
        "category",
        "submitted_by_user",
        "forwarded_to_mao",
    )

    # Apply filters
    if region_id:
        unfunded_needs = unfunded_needs.filter(
            community__barangay__municipality__province__region_id=region_id
        )
    if category_id:
        unfunded_needs = unfunded_needs.filter(category_id=category_id)
    if urgency:
        unfunded_needs = unfunded_needs.filter(urgency_level=urgency)
    if submission_type:
        unfunded_needs = unfunded_needs.filter(submission_type=submission_type)

    # Calculate statistics
    total_unfunded = unfunded_needs.count()
    total_estimated_cost = (
        unfunded_needs.aggregate(total=Sum("estimated_cost"))["total"] or 0
    )
    total_affected_population = (
        unfunded_needs.aggregate(total=Sum("affected_population"))["total"] or 0
    )

    # Breakdown by urgency
    urgency_breakdown = (
        unfunded_needs.values("urgency_level")
        .annotate(
            count=Count("id"),
            total_cost=Sum("estimated_cost"),
        )
        .order_by("-count")
    )

    # Breakdown by category
    category_breakdown = (
        unfunded_needs.values("category__name", "category__category_type")
        .annotate(
            count=Count("id"),
            total_cost=Sum("estimated_cost"),
        )
        .order_by("-count")[:10]
    )

    # Breakdown by region
    region_breakdown = (
        unfunded_needs.values(
            "community__barangay__municipality__province__region__name"
        )
        .annotate(
            count=Count("id"),
            total_cost=Sum("estimated_cost"),
        )
        .order_by("-count")
    )

    # Top priority unfunded needs
    top_unfunded = unfunded_needs.order_by("-priority_score", "-impact_severity")[:20]

    # Get forwarded but unfunded (in MAO pipeline)
    forwarded_unfunded = (
        unfunded_needs.filter(forwarded_to_mao__isnull=False)
        .values("forwarded_to_mao__name", "forwarded_to_mao__acronym")
        .annotate(
            count=Count("id"),
            total_cost=Sum("estimated_cost"),
        )
        .order_by("-count")
    )

    context = {
        "total_unfunded": total_unfunded,
        "total_estimated_cost": total_estimated_cost,
        "total_affected_population": total_affected_population,
        "urgency_breakdown": urgency_breakdown,
        "category_breakdown": category_breakdown,
        "region_breakdown": region_breakdown,
        "top_unfunded": top_unfunded,
        "forwarded_unfunded": forwarded_unfunded,
        "current_filters": {
            "region": region_id,
            "category": category_id,
            "urgency": urgency,
            "submission_type": submission_type,
        },
    }

    return render(request, "common/gap_analysis_dashboard.html", context)


@login_required
def policy_budget_matrix(request):
    """
    Policy-Budget Matrix - Show which policies are funded and which aren't.

    Part of Phase 2 implementation for policy-to-budget integration.
    """
    from recommendations.policy_tracking.models import PolicyRecommendation
    from monitoring.models import MonitoringEntry
    from django.db.models import Count, Sum, Q

    # Get all approved policies
    policies = (
        PolicyRecommendation.objects.filter(
            status__in=["approved", "in_implementation", "implemented"]
        )
        .select_related(
            "proposed_by",
            "lead_author",
        )
        .prefetch_related(
            "implementing_ppas",
            "related_needs",
            "milestones",
        )
    )

    # Build matrix data
    matrix_data = []
    for policy in policies:
        # Get implementing PPAs
        ppas = policy.implementing_ppas.all()
        total_budget = (
            ppas.aggregate(Sum("budget_allocation"))["total_budget__sum"] or 0
        )

        # Get needs addressed through this policy
        needs_count = policy.related_needs.count()

        # Get implementation progress from milestones
        milestones = policy.milestones.all()
        if milestones.exists():
            avg_progress = (
                milestones.aggregate(avg=Sum("progress_percentage"))["avg"]
                / milestones.count()
                if milestones.count() > 0
                else 0
            )
        else:
            avg_progress = 0

        # Determine funding status
        if ppas.exists():
            funding_status = "funded"
        elif needs_count > 0:
            funding_status = "needs_identified"
        else:
            funding_status = "not_funded"

        matrix_data.append(
            {
                "policy": policy,
                "ppa_count": ppas.count(),
                "total_budget": total_budget,
                "needs_count": needs_count,
                "milestone_count": milestones.count(),
                "avg_progress": avg_progress,
                "funding_status": funding_status,
            }
        )

    # Calculate summary statistics
    total_policies = len(matrix_data)
    funded_policies = sum(1 for p in matrix_data if p["funding_status"] == "funded")
    total_policy_budget = sum(p["total_budget"] for p in matrix_data)

    # Breakdown by category
    category_breakdown = {}
    for item in matrix_data:
        cat = item["policy"].category
        if cat not in category_breakdown:
            category_breakdown[cat] = {
                "count": 0,
                "funded": 0,
                "total_budget": 0,
            }
        category_breakdown[cat]["count"] += 1
        if item["funding_status"] == "funded":
            category_breakdown[cat]["funded"] += 1
        category_breakdown[cat]["total_budget"] += item["total_budget"]

    context = {
        "matrix_data": matrix_data,
        "total_policies": total_policies,
        "funded_policies": funded_policies,
        "funding_rate": (
            (funded_policies / total_policies * 100) if total_policies > 0 else 0
        ),
        "total_policy_budget": total_policy_budget,
        "category_breakdown": category_breakdown,
    }

    return render(request, "common/policy_budget_matrix.html", context)


@login_required
def mao_focal_persons_registry(request):
    """
    MAO Focal Persons Registry - Directory of all MAO focal persons.

    Part of Phase 2 implementation for MAO coordination.
    """
    from coordination.models import MAOFocalPerson, Organization
    from django.db.models import Q, Count

    # Get filter parameters
    mao_id = request.GET.get("mao")
    role = request.GET.get("role")
    is_active = request.GET.get("is_active")
    search = request.GET.get("search")

    # Base query
    focal_persons = MAOFocalPerson.objects.select_related(
        "mao",
        "user",
    ).prefetch_related(
        "managed_services",
    )

    # Apply filters
    if mao_id:
        focal_persons = focal_persons.filter(mao_id=mao_id)
    if role:
        focal_persons = focal_persons.filter(role=role)
    if is_active == "true":
        focal_persons = focal_persons.filter(is_active=True)
    elif is_active == "false":
        focal_persons = focal_persons.filter(is_active=False)
    if search:
        focal_persons = focal_persons.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__username__icontains=search)
            | Q(designation__icontains=search)
            | Q(mao__name__icontains=search)
            | Q(mao__acronym__icontains=search)
        )

    # Order by MAO, role, and appointment date
    focal_persons = focal_persons.order_by("mao__name", "role", "-appointed_date")

    # Get statistics
    total_focal_persons = focal_persons.count()
    active_count = focal_persons.filter(is_active=True).count()
    primary_count = focal_persons.filter(role="primary", is_active=True).count()

    # MAO coverage
    maos_with_focal_persons = focal_persons.values("mao").distinct().count()
    total_maos = Organization.objects.filter(organization_type="bmoa").count()

    # Group by MAO
    maos_grouped = {}
    for fp in focal_persons:
        mao_name = fp.mao.name
        if mao_name not in maos_grouped:
            maos_grouped[mao_name] = {"mao": fp.mao, "focal_persons": []}
        maos_grouped[mao_name]["focal_persons"].append(fp)

    context = {
        "focal_persons": focal_persons,
        "maos_grouped": maos_grouped,
        "total_focal_persons": total_focal_persons,
        "active_count": active_count,
        "primary_count": primary_count,
        "maos_with_focal_persons": maos_with_focal_persons,
        "total_maos": total_maos,
        "coverage_rate": (
            (maos_with_focal_persons / total_maos * 100) if total_maos > 0 else 0
        ),
        "current_filters": {
            "mao": mao_id,
            "role": role,
            "is_active": is_active,
            "search": search,
        },
    }

    return render(request, "common/mao_focal_persons_registry.html", context)


def community_needs_summary(request):
    """
    Community Needs Summary - Overview of all community needs.

    Part of Phase 2 implementation for community participation tracking.
    """
    from mana.models import Need
    from django.db.models import Count, Sum, Q, Avg

    # Get filter parameters
    status = request.GET.get("status")
    submission_type = request.GET.get("submission_type")
    community_id = request.GET.get("community")

    # Base query
    needs = Need.objects.select_related(
        "community__barangay__municipality__province__region",
        "category",
        "submitted_by_user",
        "forwarded_to_mao",
        "linked_ppa",
    )

    # Apply filters
    if status:
        needs = needs.filter(status=status)
    if submission_type:
        needs = needs.filter(submission_type=submission_type)
    if community_id:
        needs = needs.filter(community_id=community_id)

    # Calculate statistics
    total_needs = needs.count()

    # By submission type
    assessment_driven = needs.filter(submission_type="assessment_driven").count()
    community_submitted = needs.filter(submission_type="community_submitted").count()

    # By funding status
    funded = needs.filter(linked_ppa__isnull=False).count()
    forwarded = needs.filter(
        forwarded_to_mao__isnull=False, linked_ppa__isnull=True
    ).count()
    unfunded = needs.filter(
        linked_ppa__isnull=True,
        forwarded_to_mao__isnull=True,
        status__in=["validated", "prioritized"],
    ).count()

    # Financial summary
    total_estimated_cost = (
        needs.aggregate(Sum("estimated_cost"))["estimated_cost__sum"] or 0
    )
    funded_cost = (
        needs.filter(linked_ppa__isnull=False).aggregate(Sum("estimated_cost"))[
            "estimated_cost__sum"
        ]
        or 0
    )
    gap_cost = total_estimated_cost - funded_cost

    # Impact summary
    total_affected_population = (
        needs.aggregate(Sum("affected_population"))["affected_population__sum"] or 0
    )
    avg_priority_score = (
        needs.aggregate(Avg("priority_score"))["priority_score__avg"] or 0
    )

    # Community votes (participatory budgeting)
    total_votes = needs.aggregate(Sum("community_votes"))["community_votes__sum"] or 0

    # Breakdown by status
    status_breakdown = (
        needs.values("status").annotate(count=Count("id")).order_by("-count")
    )

    # Breakdown by urgency
    urgency_breakdown = (
        needs.values("urgency_level").annotate(count=Count("id")).order_by("-count")
    )

    # Recent needs
    recent_needs = needs.order_by("-created_at")[:15]

    # Top priority unfunded
    top_priority_unfunded = needs.filter(
        linked_ppa__isnull=True, status__in=["validated", "prioritized"]
    ).order_by("-priority_score", "-impact_severity")[:10]

    context = {
        "total_needs": total_needs,
        "assessment_driven": assessment_driven,
        "community_submitted": community_submitted,
        "funded": funded,
        "forwarded": forwarded,
        "unfunded": unfunded,
        "total_estimated_cost": total_estimated_cost,
        "funded_cost": funded_cost,
        "gap_cost": gap_cost,
        "funding_rate": (funded / total_needs * 100) if total_needs > 0 else 0,
        "total_affected_population": total_affected_population,
        "avg_priority_score": avg_priority_score,
        "total_votes": total_votes,
        "status_breakdown": status_breakdown,
        "urgency_breakdown": urgency_breakdown,
        "recent_needs": recent_needs,
        "top_priority_unfunded": top_priority_unfunded,
        "current_filters": {
            "status": status,
            "submission_type": submission_type,
            "community": community_id,
        },
    }

    return render(request, "common/community_needs_summary.html", context)


# ========================================
# PHASE 1: ENHANCED DASHBOARD VIEWS
# ========================================


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
        from common.work_item_model import WorkItem

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

        # Get upcoming activities from WorkItem
        upcoming_events = WorkItem.objects.filter(
            work_type='activity',
            start_date__gte=timezone.now().date(),
            start_date__lte=timezone.now().date() + timedelta(days=7),
        ).count()

        current_week = timezone.now().isocalendar()[1]
        # Get tasks due this week from WorkItem
        tasks_due = WorkItem.objects.filter(
            work_type='task',
            due_date__week=current_week,
            status__in=["not_started", "in_progress"]
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
        from common.work_item_model import WorkItem

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

        # Recent tasks completed (from WorkItem)
        for work_item in WorkItem.objects.filter(
            work_type='task',
            status="completed",
            updated_at__gte=timezone.now() - timedelta(days=30)
        ).select_related("assigned_to")[:10]:
            activities.append(
                {
                    "icon": "fa-check-circle",
                    "color": "green",
                    "title": f"Task completed: {work_item.title}",
                    "subtitle": f'by {work_item.assigned_to.get_full_name() if work_item.assigned_to else "Unassigned"}',
                    "timestamp": work_item.updated_at,
                    "url": "#",
                }
            )

        # Recent activities (from WorkItem)
        for activity in WorkItem.objects.filter(
            work_type='activity',
            created_at__gte=timezone.now() - timedelta(days=30)
        )[:10]:
            activities.append(
                {
                    "icon": "fa-calendar",
                    "color": "purple",
                    "title": f"Activity scheduled: {activity.title}",
                    "subtitle": f'{activity.start_date.strftime("%b %d, %Y") if activity.start_date else "Date TBD"}',
                    "timestamp": activity.created_at,
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
        <div hx-get="/common/dashboard/activity/?page={page + 1}" hx-trigger="revealed" hx-swap="afterend" class="text-center py-4">
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
        from common.work_item_model import WorkItem

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

        # Overdue tasks (from WorkItem)
        overdue = WorkItem.objects.filter(
            work_type='task',
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
