"""Views for the recommendations tracking module."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

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

    implemented_policies = recommendations.filter(
        category__in=policy_categories, status="implemented"
    ).count()
    implemented_programs = recommendations.filter(
        category__in=program_categories, status="implemented"
    ).count()
    implemented_services = recommendations.filter(
        category__in=service_categories, status="implemented"
    ).count()

    submitted_recommendations = recommendations.filter(
        status__in=submitted_statuses
    ).count()
    proposed_recommendations = recommendations.filter(
        status__in=proposed_statuses
    ).count()

    submitted_policies = recommendations.filter(
        category__in=policy_categories, status__in=submitted_statuses
    ).count()
    submitted_programs = recommendations.filter(
        category__in=program_categories, status__in=submitted_statuses
    ).count()
    submitted_services = recommendations.filter(
        category__in=service_categories, status__in=submitted_statuses
    ).count()

    proposed_policies = recommendations.filter(
        category__in=policy_categories, status__in=proposed_statuses
    ).count()
    proposed_programs = recommendations.filter(
        category__in=program_categories, status__in=proposed_statuses
    ).count()
    proposed_services = recommendations.filter(
        category__in=service_categories, status__in=proposed_statuses
    ).count()

    recent_policies = (
        recommendations.filter(category__in=policy_categories)
        .order_by("-updated_at", "-created_at")[:10]
    )
    recent_programs = (
        recommendations.filter(category__in=program_categories)
        .order_by("-updated_at", "-created_at")[:10]
    )
    recent_services = (
        recommendations.filter(category__in=service_categories)
        .order_by("-updated_at", "-created_at")[:10]
    )

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
        },
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
            "by_type": evidence.values("evidence_type").annotate(count=Count("id")),
        },
        "areas": {
            area_key.replace("-", "_"): {
                "slug": area_key,
                "name": area_data["name"],
                "categories": area_data["categories"],
                "icon": area_data["icon"],
                "color": area_data["color"],
                "total_recommendations": recommendations.filter(
                    category__in=area_data["categories"]
                ).count(),
                "implemented": recommendations.filter(
                    category__in=area_data["categories"], status="implemented"
                ).count(),
            }
            for area_key, area_data in RECOMMENDATIONS_AREAS.items()
        },
        "recent": {
            "policies": recent_policies,
            "programs": recent_programs,
            "services": recent_services,
        },
        "submitted": submitted_recommendations,
        "proposed": proposed_recommendations,
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
    from communities.models import OBCCommunity
    from mana.models import Assessment
    from coordination.models import Organization
    from common.models import Region, Province, Municipality, Barangay

    recent_recommendations = PolicyRecommendation.objects.order_by("-created_at")[:5]
    obc_communities = OBCCommunity.objects.select_related('barangay__municipality__province__region').order_by('name')
    mana_assessments = Assessment.objects.filter(status='completed').order_by('-created_at')
    partner_organizations = Organization.objects.all().order_by('organization_type', 'name')

    # Geographic hierarchy for filters
    regions = Region.objects.all().order_by('name')
    provinces = Province.objects.all().order_by('name')
    municipalities = Municipality.objects.all().order_by('name')
    barangays = Barangay.objects.all().order_by('name')

    context = {
        "recent_recommendations": recent_recommendations,
        "areas_data": RECOMMENDATIONS_AREAS,
        "obc_communities": obc_communities,
        "mana_assessments": mana_assessments,
        "partner_organizations": partner_organizations,
        "regions": regions,
        "provinces": provinces,
        "municipalities": municipalities,
        "barangays": barangays,
    }
    return render(request, "recommendations/recommendations_new.html", context)


@login_required
def recommendations_create(request):
    """Handle recommendation creation (POST)."""
    if request.method != 'POST':
        return redirect('common:recommendations_new')

    from recommendations.policy_tracking.models import PolicyRecommendation
    from communities.models import OBCCommunity
    from mana.models import Assessment
    import json

    try:
        # Handle secondary categories (for comprehensive category)
        secondary_categories = request.POST.getlist('secondary_categories')
        secondary_categories_json = secondary_categories if secondary_categories else None

        # Create new recommendation
        recommendation = PolicyRecommendation(
            title=request.POST.get('title'),
            category=request.POST.get('category'),
            secondary_categories=secondary_categories_json,
            description=request.POST.get('description'),
            rationale=request.POST.get('rationale'),
            problem_statement=request.POST.get('problem_statement'),
            policy_objectives=request.POST.get('policy_objectives'),
            proposed_solution=request.POST.get('proposed_solution'),
            implementation_strategy=request.POST.get('implementation_strategy'),
            expected_outcomes=request.POST.get('expected_outcomes'),
            success_metrics=request.POST.get('success_metrics'),

            # New fields
            recommendation_type=request.POST.get('recommendation_type', 'policy'),
            importance=request.POST.get('importance', 'high'),
            urgency=request.POST.get('urgency', 'high'),
            scope=request.POST.get('scope'),
            core_recommendation_type=request.POST.get('core_recommendation_type', ''),
            core_recommendation_other=request.POST.get('core_recommendation_other', ''),

            # Evidence base
            consultation_references=request.POST.get('consultation_references', ''),
            research_data=request.POST.get('research_data', ''),

            # Resources
            estimated_cost=request.POST.get('estimated_cost') or None,
            budget_implications=request.POST.get('budget_implications', ''),
            responsible_agencies=','.join(request.POST.getlist('responsible_agencies')),
            implementation_start_date=request.POST.get('implementation_start_date') or None,
            implementation_deadline=request.POST.get('implementation_deadline') or None,

            # Impact
            potential_risks=request.POST.get('potential_risks', ''),
            mitigation_strategies=request.POST.get('mitigation_strategies', ''),
            short_term_benefits=request.POST.get('short_term_benefits', ''),
            long_term_benefits=request.POST.get('long_term_benefits', ''),
            equity_considerations=request.POST.get('equity_considerations', ''),
            sustainability_measures=request.POST.get('sustainability_measures', ''),
            cultural_alignment=request.POST.get('cultural_alignment', ''),

            # M&E
            tracking_mechanisms=request.POST.get('tracking_mechanisms', ''),
            reporting_schedule=request.POST.get('reporting_schedule', ''),
            monitoring_framework=request.POST.get('monitoring_framework', ''),

            # Stakeholders
            stakeholder_feedback_detailed=request.POST.get('stakeholder_feedback_detailed', ''),
            community_validated=request.POST.get('community_validated') == 'true',
            lgus_involved=','.join(request.POST.getlist('lgus_involved')),
            ngas_involved=','.join(request.POST.getlist('ngas_involved')),
            cso_partners=','.join(request.POST.getlist('cso_partners')),

            # Meta
            notes=request.POST.get('notes', ''),
            proposed_by=request.user,
            status='draft' if request.POST.get('save_as_draft') else 'draft',
        )

        recommendation.save()

        # Add M2M relationships
        if request.POST.getlist('target_communities'):
            recommendation.target_communities.set(request.POST.getlist('target_communities'))

        if request.POST.getlist('related_assessments'):
            recommendation.related_assessments.set(request.POST.getlist('related_assessments'))

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'recommendation_id': str(recommendation.id),
                'reference_number': recommendation.reference_number
            })

        messages.success(request, f'Recommendation "{recommendation.title}" created successfully!')
        return redirect('common:recommendations_home')

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        messages.error(request, f'Error creating recommendation: {str(e)}')
        return redirect('common:recommendations_new')


@login_required
def recommendations_autosave(request):
    """Auto-save recommendation draft (AJAX)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

    # For now, just return success - actual auto-save can be implemented later
    return JsonResponse({'success': True})


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
