"""Recommendations module views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from django.http import Http404
from policy_tracking.models import PolicyRecommendation, PolicyEvidence

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
    return render(request, "recommendations/recommendations_home.html", context)


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
    return render(request, "recommendations/recommendations_new.html", context)


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
    return render(request, "recommendations/recommendations_manage.html", context)


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
    return render(request, "recommendations/recommendations_by_area.html", context)


@login_required
def recommendations_programs(request):
    """Program recommendations page."""
    from policy_tracking.models import PolicyRecommendation, PolicyEvidence
    from django.db.models import Count

    # Get program-related recommendations
    program_categories = [
        "education", "economic_development", "social_development", "cultural_development"
    ]
    recommendations = (
        PolicyRecommendation.objects.filter(category__in=program_categories)
        .select_related("proposed_by", "lead_author")
        .annotate(evidence_count=Count("evidence"))
        .order_by("-created_at")
    )

    # Define status mappings
    submitted_statuses = [
        "submitted", "under_consideration", "approved", "in_implementation", "implemented"
    ]
    proposed_statuses = ["draft", "under_review", "needs_revision"]

    # Calculate metrics
    total_programs = recommendations.count()
    implemented_programs = recommendations.filter(status="implemented").count()
    submitted_programs = recommendations.filter(status__in=submitted_statuses).count()
    proposed_programs = recommendations.filter(status__in=proposed_statuses).count()

    # Get filter parameter
    status_filter = request.GET.get("status")
    if status_filter:
        if status_filter == "proposed":
            recommendations = recommendations.filter(status__in=proposed_statuses)
        elif status_filter == "submitted":
            recommendations = recommendations.filter(status__in=submitted_statuses)
        elif status_filter == "implemented":
            recommendations = recommendations.filter(status="implemented")

    # Recent recommendations
    recent_recommendations = recommendations.order_by("-created_at")[:10]

    stats = {
        "total": total_programs,
        "implemented": implemented_programs,
        "submitted": submitted_programs,
        "proposed": proposed_programs,
        "current_filter": status_filter,
    }

    context = {
        "stats": stats,
        "recommendations": recent_recommendations,
        "current_filter": status_filter,
        "areas_data": RECOMMENDATIONS_AREAS,
    }
    return render(request, "recommendations/recommendations_programs.html", context)