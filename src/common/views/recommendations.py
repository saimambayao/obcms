"""Views for the recommendations tracking module."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..constants import RECOMMENDATIONS_AREAS
from ..utils.permissions import has_oobc_management_access


def _ensure_can_manage_recommendations(user):
    """
    Raise PermissionDenied for MOA staff attempting to modify recommendations.
    """

    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication is required to manage recommendations.")

    if getattr(user, "is_moa_staff", False):
        raise PermissionDenied(
            "MOA focal persons have read-only access to recommendations."
        )


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
    _ensure_can_manage_recommendations(request.user)

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
    _ensure_can_manage_recommendations(request.user)

    if request.method != 'POST':
        return redirect('common:recommendations_new')

    from recommendations.policy_tracking.models import PolicyRecommendation
    from communities.models import OBCCommunity
    from mana.models import Assessment
    from common.models import Barangay, Municipality, Province
    import json

    try:
        target_region_id = request.POST.get('target_region') or None
        target_province_id = request.POST.get('target_province') or None
        target_municipality_id = request.POST.get('target_municipality') or None
        target_barangay_id = request.POST.get('target_barangay') or None

        if target_barangay_id:
            barangay = (
                Barangay.objects.select_related("municipality__province__region")
                .filter(pk=target_barangay_id)
                .first()
            )
            if barangay:
                target_municipality_id = target_municipality_id or barangay.municipality_id
                if barangay.municipality:
                    target_province_id = target_province_id or barangay.municipality.province_id
                    if barangay.municipality.province:
                        target_region_id = (
                            target_region_id or barangay.municipality.province.region_id
                        )
        elif target_municipality_id:
            municipality = (
                Municipality.objects.select_related("province__region")
                .filter(pk=target_municipality_id)
                .first()
            )
            if municipality:
                target_province_id = target_province_id or municipality.province_id
                if municipality.province:
                    target_region_id = target_region_id or municipality.province.region_id
        elif target_province_id:
            province = (
                Province.objects.select_related("region")
                .filter(pk=target_province_id)
                .first()
            )
            if province:
                target_region_id = target_region_id or province.region_id

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
            target_region_id=target_region_id,
            target_province_id=target_province_id,
            target_municipality_id=target_municipality_id,
            target_barangay_id=target_barangay_id,

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
    _ensure_can_manage_recommendations(request.user)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

    # For now, just return success - actual auto-save can be implemented later
    return JsonResponse({'success': True})


@login_required
def recommendations_manage(request):
    """Manage recommendations page."""
    can_manage_recommendations = has_oobc_management_access(request.user)

    from django.db.models import Count

    from recommendations.policy_tracking.models import (
        PolicyEvidence,
        PolicyRecommendation,
    )

    recommendations = (
        PolicyRecommendation.objects.select_related(
            "proposed_by",
            "lead_author",
            "assigned_reviewer",
            "target_region",
            "target_province",
            "target_municipality",
            "target_barangay",
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
        "can_manage_recommendations": can_manage_recommendations,
    }
    return render(request, "recommendations/recommendations_manage.html", context)


def _recommendations_by_type(request, recommendation_type: str):
    """Shared handler to list recommendations filtered by type."""
    can_manage_recommendations = has_oobc_management_access(request.user)

    from django.db.models import Count

    from recommendations.policy_tracking.models import PolicyRecommendation

    queryset = (
        PolicyRecommendation.objects.filter(recommendation_type=recommendation_type)
        .select_related(
            "proposed_by",
            "lead_author",
            "assigned_reviewer",
            "target_region",
            "target_province",
            "target_municipality",
            "target_barangay",
        )
        .annotate(evidence_count=Count("evidence"))
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    if priority_filter:
        queryset = queryset.filter(priority=priority_filter)

    stats = {
        "total": queryset.count(),
        "implemented": queryset.filter(status="implemented").count(),
        "under_review": queryset.filter(status="under_review").count(),
        "approved": queryset.filter(status="approved").count(),
    }

    type_display = dict(PolicyRecommendation.RECOMMENDATION_TYPES).get(
        recommendation_type, recommendation_type.title()
    )

    context = {
        "recommendations": queryset,
        "type_key": recommendation_type,
        "type_label": type_display,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
        "stats": stats,
        "can_manage_recommendations": can_manage_recommendations,
    }
    template_name = "recommendations/recommendations_type_list.html"
    return render(request, template_name, context)


@login_required
def recommendations_programs(request):
    """List program recommendations only."""
    return _recommendations_by_type(request, "program")


@login_required
def recommendations_services(request):
    """List service recommendations only."""
    return _recommendations_by_type(request, "service")


@login_required
def recommendations_view(request, pk):
    """Display a read-only view of a policy recommendation."""
    from django.shortcuts import get_object_or_404
    from recommendations.policy_tracking.models import PolicyRecommendation

    recommendation = get_object_or_404(
        PolicyRecommendation.objects.select_related(
            "proposed_by",
            "lead_author",
            "assigned_reviewer",
            "target_region",
            "target_province",
            "target_municipality",
            "target_barangay",
        ).prefetch_related(
            "target_communities",
            "related_assessments",
            "evidence"
        ),
        pk=pk
    )

    context = {
        "recommendation": recommendation,
        "areas_data": RECOMMENDATIONS_AREAS,
    }
    return render(request, "recommendations/recommendations_view.html", context)


@login_required
def recommendations_edit(request, pk):
    """Edit an existing policy recommendation."""
    _ensure_can_manage_recommendations(request.user)

    from django.shortcuts import get_object_or_404
    from recommendations.policy_tracking.models import PolicyRecommendation
    from communities.models import OBCCommunity
    from mana.models import Assessment
    from coordination.models import Organization
    from common.models import Region, Province, Municipality, Barangay

    recommendation = get_object_or_404(
        PolicyRecommendation.objects.select_related(
            "proposed_by", "lead_author"
        ),
        pk=pk
    )

    if request.method == "POST":
        # Check if this is an AJAX auto-save request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        is_draft_save = request.POST.get('save_as_draft') == 'true'

        try:
            target_region_id = request.POST.get('target_region') or None
            target_province_id = request.POST.get('target_province') or None
            target_municipality_id = request.POST.get('target_municipality') or None
            target_barangay_id = request.POST.get('target_barangay') or None

            if target_barangay_id:
                barangay = (
                    Barangay.objects.select_related("municipality__province__region")
                    .filter(pk=target_barangay_id)
                    .first()
                )
                if barangay:
                    target_municipality_id = target_municipality_id or barangay.municipality_id
                    if barangay.municipality:
                        target_province_id = target_province_id or barangay.municipality.province_id
                        if barangay.municipality.province:
                            target_region_id = (
                                target_region_id or barangay.municipality.province.region_id
                            )
            elif target_municipality_id:
                municipality = (
                    Municipality.objects.select_related("province__region")
                    .filter(pk=target_municipality_id)
                    .first()
                )
                if municipality:
                    target_province_id = target_province_id or municipality.province_id
                    if municipality.province:
                        target_region_id = target_region_id or municipality.province.region_id
            elif target_province_id:
                province = (
                    Province.objects.select_related("region")
                    .filter(pk=target_province_id)
                    .first()
                )
                if province:
                    target_region_id = target_region_id or province.region_id

            # Handle secondary categories (for comprehensive category)
            secondary_categories = request.POST.getlist('secondary_categories')
            secondary_categories_json = secondary_categories if secondary_categories else None

            # Update recommendation fields
            if request.POST.get('title'):
                recommendation.title = request.POST.get('title')
            if request.POST.get('category'):
                recommendation.category = request.POST.get('category')
            recommendation.secondary_categories = secondary_categories_json
            if request.POST.get('description'):
                recommendation.description = request.POST.get('description')
            if request.POST.get('rationale'):
                recommendation.rationale = request.POST.get('rationale')
            if request.POST.get('problem_statement'):
                recommendation.problem_statement = request.POST.get('problem_statement')
            if request.POST.get('policy_objectives'):
                recommendation.policy_objectives = request.POST.get('policy_objectives')
            if request.POST.get('proposed_solution'):
                recommendation.proposed_solution = request.POST.get('proposed_solution')
            if request.POST.get('implementation_strategy'):
                recommendation.implementation_strategy = request.POST.get('implementation_strategy')
            if request.POST.get('expected_outcomes'):
                recommendation.expected_outcomes = request.POST.get('expected_outcomes')
            if request.POST.get('success_metrics'):
                recommendation.success_metrics = request.POST.get('success_metrics')

            # New fields
            if request.POST.get('recommendation_type'):
                recommendation.recommendation_type = request.POST.get('recommendation_type')
            if request.POST.get('importance'):
                recommendation.importance = request.POST.get('importance')
            if request.POST.get('urgency'):
                recommendation.urgency = request.POST.get('urgency')
            if request.POST.get('scope'):
                recommendation.scope = request.POST.get('scope')
            recommendation.core_recommendation_type = request.POST.get('core_recommendation_type', '')
            recommendation.core_recommendation_other = request.POST.get('core_recommendation_other', '')
            recommendation.target_region_id = target_region_id
            recommendation.target_province_id = target_province_id
            recommendation.target_municipality_id = target_municipality_id
            recommendation.target_barangay_id = target_barangay_id

            # Evidence base
            recommendation.consultation_references = request.POST.get('consultation_references', '')
            recommendation.research_data = request.POST.get('research_data', '')

            # Resources
            if request.POST.get('estimated_cost'):
                recommendation.estimated_cost = request.POST.get('estimated_cost')
            recommendation.budget_implications = request.POST.get('budget_implications', '')
            if request.POST.get('implementation_start_date'):
                recommendation.implementation_start_date = request.POST.get('implementation_start_date')
            if request.POST.get('implementation_deadline'):
                recommendation.implementation_deadline = request.POST.get('implementation_deadline')

            # Impact
            recommendation.potential_risks = request.POST.get('potential_risks', '')
            recommendation.mitigation_strategies = request.POST.get('mitigation_strategies', '')
            recommendation.short_term_benefits = request.POST.get('short_term_benefits', '')
            recommendation.long_term_benefits = request.POST.get('long_term_benefits', '')
            recommendation.equity_considerations = request.POST.get('equity_considerations', '')
            recommendation.sustainability_measures = request.POST.get('sustainability_measures', '')
            recommendation.cultural_alignment = request.POST.get('cultural_alignment', '')

            # M&E
            recommendation.tracking_mechanisms = request.POST.get('tracking_mechanisms', '')
            recommendation.reporting_schedule = request.POST.get('reporting_schedule', '')
            recommendation.monitoring_framework = request.POST.get('monitoring_framework', '')

            # Stakeholders
            recommendation.stakeholder_feedback_detailed = request.POST.get('stakeholder_feedback_detailed', '')
            recommendation.community_validated = request.POST.get('community_validated') == 'true'

            # Meta
            recommendation.notes = request.POST.get('notes', '')

            recommendation.save()

            # Update M2M relationships
            if request.POST.getlist('target_communities'):
                recommendation.target_communities.set(request.POST.getlist('target_communities'))

            if request.POST.getlist('related_assessments'):
                recommendation.related_assessments.set(request.POST.getlist('related_assessments'))

            # Update organization relationships
            if request.POST.getlist('responsible_agencies'):
                recommendation.responsible_agencies.set(request.POST.getlist('responsible_agencies'))
            if request.POST.getlist('lgus_involved'):
                recommendation.lgus_involved.set(request.POST.getlist('lgus_involved'))
            if request.POST.getlist('ngas_involved'):
                recommendation.ngas_involved.set(request.POST.getlist('ngas_involved'))
            if request.POST.getlist('cso_partners'):
                recommendation.cso_partners.set(request.POST.getlist('cso_partners'))

            # Handle AJAX auto-save request
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Auto-saved successfully'})

            # Handle draft save request
            if is_draft_save:
                return JsonResponse({'success': True, 'message': 'Draft saved successfully'})

            # Regular form submission
            messages.success(
                request,
                f'Recommendation "{recommendation.title}" has been updated successfully.'
            )
            return redirect("common:recommendations_manage")

        except Exception as e:
            if is_ajax or is_draft_save:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, f'Error updating recommendation: {str(e)}')

    # GET request - prepare form data
    obc_communities = OBCCommunity.objects.select_related('barangay__municipality__province__region').order_by('name')
    mana_assessments = Assessment.objects.filter(status='completed').order_by('-created_at')
    partner_organizations = Organization.objects.all().order_by('organization_type', 'name')

    # Geographic hierarchy for filters
    regions = Region.objects.all().order_by('name')
    provinces = Province.objects.all().order_by('name')
    municipalities = Municipality.objects.all().order_by('name')
    barangays = Barangay.objects.all().order_by('name')

    context = {
        "recommendation": recommendation,
        "areas_data": RECOMMENDATIONS_AREAS,
        "obc_communities": obc_communities,
        "mana_assessments": mana_assessments,
        "partner_organizations": partner_organizations,
        "regions": regions,
        "provinces": provinces,
        "municipalities": municipalities,
        "barangays": barangays,
        "page_title": "Edit Recommendation",
        "breadcrumb_label": "Edit Recommendation",
    }
    return render(request, "recommendations/recommendations_edit.html", context)


@login_required
def recommendations_delete(request, pk):
    """Delete a recommendation."""
    _ensure_can_manage_recommendations(request.user)

    from recommendations.policy_tracking.models import PolicyRecommendation

    recommendation = get_object_or_404(PolicyRecommendation, id=pk)

    if request.method == "POST":
        # Store reference number for success message
        reference_number = recommendation.reference_number
        recommendation.delete()
        messages.success(
            request,
            f'Recommendation "{reference_number}" has been deleted successfully.'
        )
        return redirect("common:recommendations_manage")

    # For GET requests, show confirmation page
    context = {
        "recommendation": recommendation,
        "page_title": "Delete Recommendation",
        "breadcrumb_label": "Delete Recommendation",
    }
    return render(request, "recommendations/recommendations_delete_confirm.html", context)


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
        .select_related(
            "proposed_by",
            "lead_author",
            "target_region",
            "target_province",
            "target_municipality",
            "target_barangay",
        )
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
    "recommendations_create",
    "recommendations_autosave",
    "recommendations_manage",
    "recommendations_view",
    "recommendations_edit",
    "recommendations_by_area",
]
