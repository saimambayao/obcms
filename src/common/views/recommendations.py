"""Views for the recommendations tracking module."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..constants import RECOMMENDATIONS_AREAS


@login_required
def recommendations_home(request):
    """Recommendations Tracking module home page."""
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

    from django.db.models import Count, Q

    from recommendations.policy_tracking.models import (
        PolicyEvidence,
        PolicyRecommendation,
    )

    recommendations = PolicyRecommendation.objects.select_related(
        "proposed_by", "lead_author"
    )
    evidence = PolicyEvidence.objects.select_related("policy")

    policy_categories = ["governance", "legal_framework", "administrative"]
    program_categories = [
        "education",
        "economic_development",
        "social_development",
        "cultural_development",
    ]
    service_categories = ["healthcare", "infrastructure", "environment", "human_rights"]

    submitted_statuses = [
        "submitted",
        "under_consideration",
        "approved",
        "in_implementation",
        "implemented",
    ]
    proposed_statuses = ["draft", "under_review", "needs_revision"]

    total_recommendations = recommendations.count()
    implemented_recommendations = recommendations.filter(status="implemented").count()
    under_review_recommendations = recommendations.filter(status="under_review").count()
    high_priority_recommendations = recommendations.filter(
        priority__in=["high", "urgent", "critical"]
    ).count()

    policy_recommendations = recommendations.filter(
        category__in=policy_categories
    ).count()
    program_recommendations = recommendations.filter(
        category__in=program_categories
    ).count()
    service_recommendations = recommendations.filter(
        category__in=service_categories
    ).count()

    stats = {
        "summary": {
            "total": total_recommendations,
            "implemented": implemented_recommendations,
            "under_review": under_review_recommendations,
            "high_priority": high_priority_recommendations,
        },
        "categories": {
            "policies": policy_recommendations,
            "programs": program_recommendations,
            "services": service_recommendations,
        },
        "status_breakdown": recommendations.values("status").annotate(
            count=Count("id")
        ),
        "priority_breakdown": recommendations.values("priority").annotate(
            count=Count("id")
        ),
        "evidence": {
            "total": evidence.count(),
            "recent": evidence.order_by("-created_at")[:10],
            "by_type": evidence.values("evidence_type").annotate(count=Count("id")),
        },
        "areas": {
            area_key: {
                "name": area_data["name"],
                "categories": area_data["categories"],
                "total_recommendations": recommendations.filter(
                    category__in=area_data["categories"]
                ).count(),
                "implemented": recommendations.filter(
                    category__in=area_data["categories"], status="implemented"
                ).count(),
            }
            for area_key, area_data in RECOMMENDATIONS_AREAS.items()
        },
        "recent": recommendations.order_by("-created_at")[:10],
        "submitted": recommendations.filter(status__in=submitted_statuses).count(),
        "proposed": recommendations.filter(status__in=proposed_statuses).count(),
    }

    context = {
        "stats": stats,
        "areas_data": RECOMMENDATIONS_AREAS,
    }
    return render(request, "recommendations/recommendations_home.html", context)


@login_required
def recommendations_stats_cards(request):
    """Return just the recommendations stat cards for HTMX auto-refresh."""
    from recommendations.policy_tracking.models import PolicyRecommendation

    recommendations = PolicyRecommendation.objects.all()

    policy_categories = ["governance", "legal_framework", "administrative"]
    program_categories = [
        "education",
        "economic_development",
        "social_development",
        "cultural_development",
    ]
    service_categories = ["healthcare", "infrastructure", "environment", "human_rights"]

    submitted_statuses = [
        "submitted",
        "under_consideration",
        "approved",
        "in_implementation",
        "implemented",
    ]
    proposed_statuses = ["draft", "under_review", "needs_revision"]

    total_recommendations = recommendations.count()
    implemented_recommendations = recommendations.filter(status="implemented").count()
    submitted_recommendations = recommendations.filter(status__in=submitted_statuses).count()
    proposed_recommendations = recommendations.filter(status__in=proposed_statuses).count()

    policy_recommendations = recommendations.filter(category__in=policy_categories).count()
    program_recommendations = recommendations.filter(category__in=program_categories).count()
    service_recommendations = recommendations.filter(category__in=service_categories).count()

    implemented_policies = recommendations.filter(category__in=policy_categories, status="implemented").count()
    implemented_programs = recommendations.filter(category__in=program_categories, status="implemented").count()
    implemented_services = recommendations.filter(category__in=service_categories, status="implemented").count()

    submitted_policies = recommendations.filter(category__in=policy_categories, status__in=submitted_statuses).count()
    submitted_programs = recommendations.filter(category__in=program_categories, status__in=submitted_statuses).count()
    submitted_services = recommendations.filter(category__in=service_categories, status__in=submitted_statuses).count()

    proposed_policies = recommendations.filter(category__in=policy_categories, status__in=proposed_statuses).count()
    proposed_programs = recommendations.filter(category__in=program_categories, status__in=proposed_statuses).count()
    proposed_services = recommendations.filter(category__in=service_categories, status__in=proposed_statuses).count()

    stats = {
        "recommendations": {
            "total": total_recommendations,
            "implemented": implemented_recommendations,
            "submitted": submitted_recommendations,
            "proposed": proposed_recommendations,
            "policies": policy_recommendations,
            "programs": program_recommendations,
            "services": service_recommendations,
            "implemented_policies": implemented_policies,
            "implemented_programs": implemented_programs,
            "implemented_services": implemented_services,
            "submitted_policies": submitted_policies,
            "submitted_programs": submitted_programs,
            "submitted_services": submitted_services,
            "proposed_policies": proposed_policies,
            "proposed_programs": proposed_programs,
            "proposed_services": proposed_services,
        }
    }

    return render(request, "partials/recommendations_stats_cards.html", {"stats": stats})


@login_required
def recommendations_new(request):
    """Create new recommendation page."""
    from recommendations.policy_tracking.models import PolicyRecommendation

    recent_recommendations = PolicyRecommendation.objects.order_by("-created_at")[:5]

    context = {
        "recent_recommendations": recent_recommendations,
        "areas_data": RECOMMENDATIONS_AREAS,
    }
    return render(request, "recommendations/recommendations_new.html", context)


@login_required
def recommendations_manage(request):
    """Manage recommendations page."""
    from django.db.models import Count

    from recommendations.policy_tracking.models import (
        PolicyEvidence,
        PolicyRecommendation,
    )

    recommendations = (
        PolicyRecommendation.objects.select_related(
            "proposed_by", "lead_author", "assigned_reviewer"
        )
        .annotate(evidence_count=Count("evidence"))
        .order_by("-created_at")
    )

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
    from django.db.models import Count, Q
    from django.http import Http404

    from recommendations.policy_tracking.models import (
        PolicyEvidence,
        PolicyRecommendation,
    )

    if area_slug not in RECOMMENDATIONS_AREAS:
        raise Http404("Area not found")

    area_info = RECOMMENDATIONS_AREAS[area_slug]
    area_categories = area_info["categories"]

    recommendations = (
        PolicyRecommendation.objects.filter(category__in=area_categories)
        .select_related("proposed_by", "lead_author")
        .annotate(evidence_count=Count("evidence"))
    )

    submitted_statuses = [
        "submitted",
        "under_consideration",
        "approved",
        "in_implementation",
        "implemented",
    ]
    proposed_statuses = ["draft", "under_review", "needs_revision"]

    total_area_recommendations = recommendations.count()
    implemented_area = recommendations.filter(status="implemented").count()
    submitted_area = recommendations.filter(status__in=submitted_statuses).count()
    proposed_area = recommendations.filter(status__in=proposed_statuses).count()

    status_filter = request.GET.get("status")
    if status_filter:
        if status_filter == "proposed":
            recommendations = recommendations.filter(status__in=proposed_statuses)
        elif status_filter == "submitted":
            recommendations = recommendations.filter(status__in=submitted_statuses)
        elif status_filter == "implemented":
            recommendations = recommendations.filter(status="implemented")

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


__all__ = [
    "recommendations_home",
    "recommendations_new",
    "recommendations_manage",
    "recommendations_by_area",
]
