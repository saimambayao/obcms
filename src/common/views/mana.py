"""Views for the MANA (Mapping and Needs Assessment) module."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Case, Count, F, IntegerField, Q, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from communities.models import OBCCommunity

from ..models import Barangay, Municipality, Province, Region, StaffProfile
from ..services.locations import build_location_data
from ..utils.moa_permissions import moa_no_access
from common.forms import ProvinceForm
from common.services.geodata import serialize_layers_for_map
from mana.forms import (
    AssessmentUpdateForm,
    DeskReviewQuickEntryForm,
    KIIQuickEntryForm,
    RegionalWorkshopSetupForm,
    SurveyQuickEntryForm,
    Workshop1Form,
    Workshop2Form,
    Workshop3Form,
    Workshop4Form,
    Workshop5Form,
)
from mana.models import (
    Assessment,
    AssessmentCategory,
    AssessmentTeamMember,
    MANAReport,
    Need,
    WorkshopActivity,
    WorkshopParticipantAccount,
    WorkshopResponse,
)
from mana.views import create_workshop_activities

WORKSHOP_FORM_MAP = {
    "workshop_1": Workshop1Form,
    "workshop_2": Workshop2Form,
    "workshop_3": Workshop3Form,
    "workshop_4": Workshop4Form,
    "workshop_5": Workshop5Form,
}

WORKSHOP_GENERAL_FIELDS = Workshop1Form.general_fields
WORKSHOP_SYNTHESIS_FIELDS = Workshop1Form.synthesis_fields

LEGAL_BASIS = [
    {
        "title": "Bangsamoro Organic Law",
        "description": (
            "Affirms the Bangsamoro Government's mandate to protect and advance the rights "
            "of Other Bangsamoro Communities (OBCs) outside BARMM through coordinated "
            "programs with LGUs and national agencies."
        ),
    },
    {
        "title": "Bangsamoro Administrative Code",
        "description": (
            "Designates the Office for Other Bangsamoro Communities (OOBC) to gather data, "
            "conduct needs assessments, and recommend responsive policies and services for OBCs."
        ),
    },
    {
        "title": "Consultation and MANA Mandate",
        "description": (
            "Institutionalizes consultations and the Mapping and Needs Assessment (MANA) "
            "as core mechanisms for evidence-based planning, integrating spatial and "
            "thematic analyses for policy development."
        ),
    },
]

CORE_PRINCIPLES = [
    {
        "title": "Inclusive Participation",
        "details": "Engage leaders, LGUs, NGAs, and marginalized sectors to capture diverse realities.",
    },
    {
        "title": "Transparency & Accountability",
        "details": "Maintain clear communication, document deliberations, and uphold data integrity.",
    },
    {
        "title": "Standardized Methodologies",
        "details": "Use validated qualitative and quantitative tools for comparable findings.",
    },
    {
        "title": "Cultural Sensitivity",
        "details": "Respect languages, traditions, and practices throughout all engagements.",
    },
    {
        "title": "Data Protection",
        "details": "Secure informed consent and safeguard sensitive information gathered on the field.",
    },
    {
        "title": "Sustainability",
        "details": "Design interventions with long-term viability and capacity-building in mind.",
    },
    {
        "title": "Collaboration & Ownership",
        "details": "Coordinate closely with BMOAs, LGUs, NGAs, and community representatives.",
    },
    {
        "title": "Adaptive Management",
        "details": "Iterate processes to respond to emerging needs and lessons learned.",
    },
    {
        "title": "Evidence-Based Decisions",
        "details": "Ground recommendations on rigorously analysed spatial and thematic data.",
    },
    {
        "title": "Equity",
        "details": "Prioritize vulnerable and marginalized segments to avoid exclusion.",
    },
]

MANA_PHASES = [
    {
        "name": "Pre-Assessment",
        "focus": "Formalize partnerships, conduct desk research, and finalize tools and target sites.",
        "key_actions": [
            "Secure agreements with BMOAs, LGUs, and NGAs for access and resource sharing.",
            "Synthesize existing socio-economic and cultural data to refine focus areas.",
            "Co-design standardized instruments and training modules with stakeholders.",
        ],
    },
    {
        "name": "Baseline Mapping & Data Collection",
        "focus": "Deploy mixed methods and validate coverage with community representatives.",
        "key_actions": [
            "Conduct surveys, FGDs, KIIs, and mapping sessions with inclusive facilitation.",
            "Use digital tools to capture demographic, socio-economic, and spatial indicators.",
            "Hold validation huddles to adjust instruments and address data gaps early.",
        ],
    },
    {
        "name": "Thematic In-Depth Studies",
        "focus": "Deep-dive on social, economic, cultural, and rights dimensions using expert input.",
        "key_actions": [
            "Commission specialized analyses aligned with community-identified priorities.",
            "Examine cross-cutting factors such as gender, youth, and disability.",
            "Blend technical reviews with community sense-making for nuanced findings.",
        ],
    },
    {
        "name": "Synthesis & Prioritization",
        "focus": "Consolidate insights and rank issues with stakeholders against agreed criteria.",
        "key_actions": [
            "Integrate baseline and thematic results into a unified analytical framework.",
            "Facilitate validation workshops to confirm urgency, feasibility, and impact.",
            "Document rationale behind final priorities for transparency and follow-through.",
        ],
    },
    {
        "name": "Recommendation & Action Planning",
        "focus": "Translate priorities into policy options, program concepts, and action points.",
        "key_actions": [
            "Draft policy briefs and program notes grounded on Moral Governance principles.",
            "Clarify responsibilities, timelines, and resource requirements with partners.",
            "Co-design communication materials for accessible dissemination to communities.",
        ],
    },
    {
        "name": "Monitoring, Evaluation, and Learning",
        "focus": "Track progress, institutionalize feedback loops, and inform future MANA cycles.",
        "key_actions": [
            "Set indicators and targets aligned with community-defined outcomes.",
            "Schedule periodic reviews (12-24 months) with participatory reflection sessions.",
            "Feed lessons into subsequent consultations and planning processes.",
        ],
    },
]

REPORTING_TIMELINE = [
    {
        "label": "Initial Summary",
        "deadline": "Within 5 working days",
        "description": "Key highlights, emerging issues, and immediate follow-up items.",
    },
    {
        "label": "Comprehensive Report",
        "deadline": "Within 20 working days",
        "description": "Full documentation covering context, methodology, findings, and recommendations.",
    },
    {
        "label": "Quarterly Consolidation",
        "deadline": "Every quarter",
        "description": "Portfolio-wide synthesis of consultations and MANA-linked engagements.",
    },
]

MEL_PRACTICES = [
    {
        "title": "Indicator Tracking",
        "details": "Use community-informed baselines and targets to monitor social, economic, cultural, and rights-based outcomes.",
    },
    {
        "title": "Feedback Integration",
        "details": "Document stakeholder feedback through dialogue sessions, online forms, and community channels for continuous improvement.",
    },
    {
        "title": "Learning Loops",
        "details": "Conduct periodic evaluations and share lessons to recalibrate methodologies and interventions.",
    },
]

ACTIVITY_PREP_CHECKLIST = [
    {
        "category": "Agreements & Coordination",
        "items": [
            "Transmit formal communications to BMOAs, LGUs, and NGAs for scheduling and support.",
            "Book courtesy calls with Governors/Mayors to align on objectives and participant lists.",
            "Confirm security, health, and emergency protocols with local counterparts.",
        ],
    },
    {
        "category": "Team Mobilisation",
        "items": [
            "Assign Team Leader, Deputy, facilitators, documenters, secretariat, and GIS/data leads.",
            "Issue tasking notes covering facilitation flow, documentation formats, and MEL requirements.",
            "Finalize travel, accommodation, and per diem logistics including halal-compliant meals.",
        ],
    },
    {
        "category": "Tools & Materials",
        "items": [
            "Validate survey instruments, KII guides, workshop kits, and translation aids.",
            "Pre-load tablets/laptops with digital forms, mapping basemaps, and reference materials.",
            "Prepare printed kits (agendas, attendance sheets, meta cards, certificates, feedback forms).",
        ],
    },
]

FIELD_ACTIVITY_TRACKERS = [
    {
        "title": "Day 1 – Arrival & Mobilisation",
        "inputs": [
            "Travel logs and participant arrival confirmations.",
            "Accommodation assignment sheet and logistics issues encountered.",
            "Team huddle notes covering key reminders and risk updates.",
        ],
    },
    {
        "title": "Day 2 – Context Setting",
        "inputs": [
            "Opening program minutes and photos with consent list.",
            "Workshop 1 outputs (community maps, stakeholder charts, historical timelines).",
            "Issues raised during plenary Q&A requiring immediate escalation.",
        ],
    },
    {
        "title": "Day 3 – Aspirations & Collaboration",
        "inputs": [
            "Workshop 2 prioritisation matrices and aspiration boards.",
            "Workshop 3 collaboration mapping and empowerment action points.",
            "Attendance differentials (who joined/left) and gender/sectoral balance checks.",
        ],
    },
    {
        "title": "Day 4 – Feedback & Action Planning",
        "inputs": [
            "Workshop 4 feedback summaries on existing programs (successes, gaps, recommendations).",
            "Workshop 5 problem tree analysis assets and impact notes.",
            "Workshop 6 way-forward templates with responsible agencies and timelines.",
        ],
    },
    {
        "title": "Day 5 – Departure",
        "inputs": [
            "Signed completion report, logistics wrap-up checklist, and remaining issues log.",
            "Participant evaluation forms and appreciation messages for LGUs/community leaders.",
            "Team debrief summary capturing lessons, risks, and follow-up assignments.",
        ],
    },
]

POST_ACTIVITY_PROCESS = [
    {
        "stage": "Data Encoding & Cleaning",
        "tasks": [
            "Encode survey results, workshop outputs, and KIIs into the central repository within five days.",
            "Apply data validation rules (duplicates, missing fields, consistency checks).",
            "Coordinate with GIS lead for geotag alignment and map layer updates.",
        ],
    },
    {
        "stage": "Analysis & Synthesis",
        "tasks": [
            "Generate preliminary dashboards for social, economic, cultural, and rights themes.",
            "Triangulate qualitative evidence with quantitative indicators and spatial trends.",
            "Draft priority issue briefs anchored on Moral Governance principles.",
        ],
    },
    {
        "stage": "Reporting & Dissemination",
        "tasks": [
            "Prepare initial summary (5 days) and full report (20 days) per reporting timeline.",
            "Organize validation workshop, capture feedback, and update the final MANA report.",
            "Develop communication assets (policy briefs, infographics) and plan dissemination sessions.",
        ],
    },
    {
        "stage": "MEL & Handover",
        "tasks": [
            "Log action items into the MEL tracker with indicators, owners, and timelines.",
            "Schedule follow-up assessments (12–24 months) and feedback mechanisms (online/offline).",
            "Close coordination loops with OOBC leadership, LGUs, and partners for implementation.",
        ],
    },
]


def _build_regional_dataset(request):
    regions = Region.objects.filter(is_active=True).order_by("name")
    region_ids = list(regions.values_list("id", flat=True))

    region_summary = {
        region.id: {
            "region": region,
            "assessments": {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "planning": 0,
                "reporting": 0,
                "desk_review": 0,
                "survey": 0,
                "kii": 0,
                "workshop": 0,
            },
            "needs": {"total": 0, "critical": 0, "validated": 0},
            "reports": {"total": 0, "finalized": 0, "validation": 0},
        }
        for region in regions
    }

    region_assessments = Assessment.objects.none()
    selected_assessment = None

    if region_ids:
        region_assessments = (
            Assessment.objects.filter(
                community__barangay__municipality__province__region_id__in=region_ids
            )
            .select_related(
                "community__barangay__municipality__province__region",
                "category",
                "lead_assessor",
            )
            .order_by("-created_at")
        )

        regional_workshop_assessments = region_assessments.filter(
            primary_methodology="workshop", assessment_level="regional"
        )

        selected_assessment_id = request.POST.get("assessment") or request.GET.get(
            "assessment"
        )
        if selected_assessment_id:
            selected_assessment = regional_workshop_assessments.filter(
                id=selected_assessment_id
            ).first()

        if selected_assessment is None:
            selected_assessment = regional_workshop_assessments.first()

        aggregated = (
            region_assessments.annotate(
                resolved_region_id=Case(
                    When(
                        community__isnull=False,
                        then=F(
                            "community__barangay__municipality__province__region_id"
                        ),
                    ),
                    When(province__isnull=False, then=F("province__region_id")),
                    default=None,
                    output_field=IntegerField(),
                )
            )
            .values("resolved_region_id")
            .annotate(
                total=Count("id"),
                completed=Count("id", filter=Q(status="completed")),
                in_progress=Count(
                    "id", filter=Q(status__in=["data_collection", "analysis"])
                ),
                planning=Count("id", filter=Q(status__in=["planning", "preparation"])),
                reporting=Count("id", filter=Q(status="reporting")),
                desk_review=Count("id", filter=Q(primary_methodology="desk_review")),
                survey=Count("id", filter=Q(primary_methodology="survey")),
                kii=Count("id", filter=Q(primary_methodology="kii")),
                workshop=Count("id", filter=Q(primary_methodology="workshop")),
            )
        )

        for row in aggregated:
            summary = region_summary.get(row["resolved_region_id"])
            if not summary:
                continue
            assessments = summary["assessments"]
            assessments.update(
                total=row["total"],
                completed=row["completed"],
                in_progress=row["in_progress"],
                planning=row["planning"],
                reporting=row["reporting"],
                desk_review=row["desk_review"],
                survey=row["survey"],
                kii=row["kii"],
                workshop=row["workshop"],
            )

        needs_agg = (
            Need.objects.filter(
                assessment__community__barangay__municipality__province__region_id__in=region_ids
            )
            .annotate(
                resolved_region_id=F(
                    "assessment__community__barangay__municipality__province__region_id"
                )
            )
            .values("resolved_region_id")
            .annotate(
                total=Count("id"),
                critical=Count("id", filter=Q(urgency_level="immediate")),
                validated=Count(
                    "id",
                    filter=Q(
                        status__in=[
                            "validated",
                            "prioritized",
                            "planned",
                            "in_progress",
                            "completed",
                        ]
                    ),
                ),
            )
        )

        for row in needs_agg:
            summary = region_summary.get(row["resolved_region_id"])
            if not summary:
                continue
            summary["needs"].update(
                total=row["total"],
                critical=row["critical"],
                validated=row["validated"],
            )

        reports_agg = (
            MANAReport.objects.filter(
                assessment__community__barangay__municipality__province__region_id__in=region_ids
            )
            .annotate(
                resolved_region_id=F(
                    "assessment__community__barangay__municipality__province__region_id"
                )
            )
            .values("resolved_region_id")
            .annotate(
                total=Count("id"),
                finalized=Count(
                    "id", filter=Q(report_status__in=["final", "submitted"])
                ),
                validation=Count("id", filter=Q(report_status="validation")),
            )
        )

        for row in reports_agg:
            summary = region_summary.get(row["resolved_region_id"])
            if not summary:
                continue
            summary["reports"].update(
                total=row["total"],
                finalized=row["finalized"],
                validation=row["validation"],
            )

    region_cards = [region_summary[region.id] for region in regions]

    methodology_breakdown = [
        {
            "label": "Desk Review",
            "value": sum(card["assessments"]["desk_review"] for card in region_cards),
        },
        {
            "label": "Survey",
            "value": sum(card["assessments"]["survey"] for card in region_cards),
        },
        {
            "label": "Key Informant Interview",
            "value": sum(card["assessments"]["kii"] for card in region_cards),
        },
        {
            "label": "Workshop",
            "value": sum(card["assessments"]["workshop"] for card in region_cards),
        },
    ]

    global_stats = {
        "total_assessments": sum(card["assessments"]["total"] for card in region_cards),
        "completed": sum(card["assessments"]["completed"] for card in region_cards),
        "in_progress": sum(card["assessments"]["in_progress"] for card in region_cards),
        "planning": sum(card["assessments"]["planning"] for card in region_cards),
        "reporting": sum(card["assessments"]["reporting"] for card in region_cards),
        "needs_identified": sum(card["needs"]["total"] for card in region_cards),
        "needs_validated": sum(card["needs"]["validated"] for card in region_cards),
    }

    reports_summary = {
        "total": sum(card["reports"]["total"] for card in region_cards),
        "finalized": sum(card["reports"]["finalized"] for card in region_cards),
        "validation": sum(card["reports"]["validation"] for card in region_cards),
    }

    return {
        "region_cards": region_cards,
        "methodology_breakdown": methodology_breakdown,
        "global_stats": global_stats,
        "reports_summary": reports_summary,
        "recent_assessments": region_assessments[:8],
    }


@login_required
def mana_home(request):
    """MANA module home page."""
    from django.db.models import Count, Q

    from mana.models import Assessment, BaselineStudy, Need

    assessments = Assessment.objects.select_related("community", "category")
    needs = Need.objects.select_related("category", "assessment")
    baseline_studies = BaselineStudy.objects.select_related("community")

    total_assessments = assessments.count()
    completed_assessments = assessments.filter(status="completed").count()
    in_progress_assessments = assessments.filter(
        status__in=["data_collection", "analysis"]
    ).count()
    planned_assessments = assessments.filter(
        status__in=["planning", "preparation"]
    ).count()

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
            "recent": assessments.order_by("-updated_at", "-created_at")[:10],
        },
        "needs": {
            "total": needs.count(),
            "critical": needs.filter(urgency_level="immediate").count(),
            "by_category": needs.values("category__name").annotate(count=Count("id"))[
                :10
            ],
            "recent": needs.order_by("-updated_at", "-created_at")[:10],
        },
        "baseline_studies": {
            "total": baseline_studies.count(),
            "completed": baseline_studies.filter(status="completed").count(),
            "ongoing": baseline_studies.filter(
                status__in=["data_collection", "analysis"]
            ).count(),
            "recent": baseline_studies.order_by("-updated_at", "-created_at")[:10],
        },
    }

    return render(request, "mana/mana_home.html", {"stats": stats})


@login_required
def mana_stats_cards(request):
    """Return just the MANA stat cards for HTMX auto-refresh."""
    from mana.models import Assessment

    assessments = Assessment.objects.all()

    total_assessments = assessments.count()
    completed_assessments = assessments.filter(status="completed").count()
    in_progress_assessments = assessments.filter(
        status__in=["data_collection", "analysis"]
    ).count()
    planned_assessments = assessments.filter(
        status__in=["planning", "preparation"]
    ).count()

    stats = {
        "mana": {
            "total_assessments": total_assessments,
            "completed": completed_assessments,
            "in_progress": in_progress_assessments,
            "planned": planned_assessments,
        }
    }

    return render(request, "partials/mana_stats_cards.html", {"stats": stats})


@login_required
def mana_new_assessment(request):
    """New MANA assessment page."""
    recent_assessments = Assessment.objects.order_by("-created_at")[:5]
    regions = Region.objects.filter(is_active=True).order_by("code", "name")
    provinces = (
        Province.objects.filter(is_active=True)
        .select_related("region")
        .order_by("name")
    )

    staff_profiles = (
        StaffProfile.objects.filter(
            user__is_active=True,
            employment_status=StaffProfile.STATUS_ACTIVE,
        )
        .select_related("user")
        .order_by("user__first_name", "user__last_name")
    )
    staff_members = [profile.user for profile in staff_profiles]

    if request.method == "POST":
        form_data = request.POST
        errors: list[str] = []

        title = form_data.get("title", "").strip()
        primary_methodology = form_data.get("primary_methodology", "workshop")
        priority = form_data.get("priority", "medium")
        objectives = form_data.get("objectives", "").strip()
        description = form_data.get("description", "").strip()
        venue_location = form_data.get("venue_location", "").strip()
        funding_source = form_data.get("funding_source", "").strip()

        planned_start_raw = form_data.get("planned_start_date", "").strip()
        planned_end_raw = form_data.get("planned_end_date", "").strip()
        estimated_budget_raw = form_data.get("estimated_budget", "").strip()

        region_id = form_data.get("region") or None
        province_id = form_data.get("province") or None
        municipality_id = form_data.get("municipality") or None
        barangay_id = form_data.get("barangay") or None
        community_id = form_data.get("community") or None

        assessment_level = form_data.get("assessment_level") or None
        if not assessment_level:
            if community_id:
                assessment_level = "community"
            elif barangay_id:
                assessment_level = "barangay"
            elif municipality_id:
                assessment_level = "city_municipal"
            elif province_id:
                assessment_level = "provincial"
            else:
                assessment_level = "regional"

        if not title:
            errors.append("Provide an assessment title.")

        if not objectives:
            errors.append("Outline the key objectives for this assessment.")

        if not description:
            errors.append("Add a short description summarizing the activity.")

        def parse_date(value: str, label: str) -> date | None:
            if not value:
                errors.append(f"Specify the {label}.")
                return None
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                errors.append(f"Invalid {label} format. Use YYYY-MM-DD.")
                return None

        planned_start_date = parse_date(planned_start_raw, "planned start date")
        planned_end_date = parse_date(planned_end_raw, "planned end date")

        estimated_budget = None
        if estimated_budget_raw:
            try:
                estimated_budget = Decimal(estimated_budget_raw)
            except (InvalidOperation, TypeError):
                errors.append("Enter a valid estimated budget amount.")

        region = None
        if region_id:
            region = Region.objects.filter(pk=region_id).first()
            if not region:
                errors.append("Selected region was not found.")
        else:
            errors.append("Select the region covered by this assessment.")

        province = None
        if province_id:
            province = (
                Province.objects.filter(pk=province_id).select_related("region").first()
            )
            if not province:
                errors.append("Selected province was not found.")

        municipality = None
        if municipality_id:
            municipality = (
                Municipality.objects.filter(pk=municipality_id)
                .select_related("province__region")
                .first()
            )
            if not municipality:
                errors.append("Selected municipality was not found.")

        barangay = None
        if barangay_id:
            barangay = (
                Barangay.objects.filter(pk=barangay_id)
                .select_related("municipality__province__region")
                .first()
            )
            if not barangay:
                errors.append("Selected barangay was not found.")

        community = None
        if community_id:
            community = (
                OBCCommunity.objects.select_related(
                    "barangay__municipality__province__region"
                )
                .filter(pk=community_id)
                .first()
            )
            if not community:
                errors.append("Selected community was not found.")

        # Gather team member ids
        team_leader_id = form_data.get("team_leader") or None
        deputy_leader_id = form_data.get("deputy_leader") or None
        documenter_id = form_data.get("lead_documenter") or None
        facilitator_ids = {
            member_id
            for member_id in [
                form_data.get("workshop_1_facilitator"),
                form_data.get("workshop_2_facilitator"),
                form_data.get("workshop_3_facilitator"),
                form_data.get("workshop_4_facilitator"),
                form_data.get("workshop_5_facilitator"),
            ]
            if member_id
        }

        target_participants = form_data.get("target_participants") or "30"

        if not errors:
            try:
                with transaction.atomic():
                    category, _ = AssessmentCategory.objects.get_or_create(
                        name="OBC-MANA Workshop",
                        defaults={
                            "category_type": "needs_assessment",
                            "description": (
                                "Other Bangsamoro Communities Mapping and Needs Assessment"
                            ),
                            "icon": "fas fa-users",
                            "color": "#3B82F6",
                        },
                    )

                    assessment = Assessment(
                        title=title,
                        category=category,
                        description=description,
                        objectives=objectives,
                        assessment_level=assessment_level,
                        primary_methodology=primary_methodology,
                        priority=priority,
                        planned_start_date=planned_start_date,
                        planned_end_date=planned_end_date,
                        estimated_budget=estimated_budget,
                        location_details=venue_location,
                        lead_assessor=request.user,
                        created_by=request.user,
                    )

                    if funding_source:
                        supplemental_note = f"Funding source: {funding_source}"
                        assessment.location_details = (
                            f"{venue_location}\n{supplemental_note}"
                            if venue_location
                            else supplemental_note
                        )

                    if region:
                        assessment.region = region
                    if province:
                        assessment.province = province
                    if municipality:
                        assessment.municipality = municipality
                    if barangay:
                        assessment.barangay = barangay
                    if community:
                        assessment.community = community

                    assessment.full_clean()
                    assessment.save()

                    def add_team_member(user_id: str | None, role: str) -> None:
                        if not user_id:
                            return
                        AssessmentTeamMember.objects.create(
                            assessment=assessment,
                            user_id=user_id,
                            role=role,
                        )

                    add_team_member(team_leader_id, "team_leader")
                    add_team_member(deputy_leader_id, "deputy_leader")
                    add_team_member(documenter_id, "documenter")
                    for facilitator_id in facilitator_ids:
                        add_team_member(facilitator_id, "facilitator")

                    if primary_methodology == "workshop":
                        create_workshop_activities(
                            assessment,
                            {
                                "planned_start_date": planned_start_raw,
                                "target_participants": target_participants,
                            },
                        )

                messages.success(
                    request,
                    f'Assessment "{assessment.title}" was created successfully.',
                )
                return redirect("common:mana_manage_assessments")
            except ValidationError as exc:
                for field, field_errors in exc.message_dict.items():
                    for error in field_errors:
                        errors.append(f"{field.replace('_', ' ').title()}: {error}")
            except Exception as exc:  # pragma: no cover - guarded fallback
                errors.append("Unable to create the assessment. Please try again.")

        for error in errors:
            messages.error(request, error)

    context = {
        "recent_assessments": recent_assessments,
        "regions": regions,
        "provinces": provinces,
        "staff_members": staff_members,
        "form_data": request.POST if request.method == "POST" else None,
    }
    return render(request, "mana/mana_new_assessment.html", context)


@login_required
def mana_manage_assessments(request):
    """Manage MANA assessments page."""
    from django.db.models import Count

    from communities.models import OBCCommunity
    from mana.models import Assessment, Need

    assessments = (
        Assessment.objects.select_related("community", "category", "lead_assessor")
        .annotate(needs_count=Count("identified_needs"))
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status")
    community_filter = request.GET.get("community")

    if status_filter:
        assessments = assessments.filter(status=status_filter)

    if community_filter:
        assessments = assessments.filter(community__id=community_filter)

    communities = OBCCommunity.objects.order_by("barangay__name")
    status_choices = (
        Assessment.STATUS_CHOICES if hasattr(Assessment, "STATUS_CHOICES") else []
    )

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
    return render(request, "mana/mana_manage_assessments.html", context)


@login_required
def mana_assessment_detail(request, assessment_id):
    """Render a rich detail page for a specific assessment."""

    assessment = get_object_or_404(
        Assessment.objects.select_related(
            "category",
            "lead_assessor",
            "community__barangay__municipality__province__region",
            "province__region",
            "region",
            "municipality__province__region",
            "barangay__municipality__province__region",
        ).prefetch_related(
            "assessmentteammember_set__user",
            "identified_needs__category",
            "workshop_activities",
        ),
        pk=assessment_id,
    )

    team_members = assessment.assessmentteammember_set.select_related("user").order_by(
        "role", "user__first_name", "user__last_name"
    )

    needs_queryset = assessment.identified_needs.all()
    needs_list = list(
        needs_queryset.order_by("-priority_score", "-impact_severity", "title")
    )
    workshops_list = list(
        assessment.workshop_activities.all().order_by("scheduled_date", "start_time")
    )

    needs_summary = {
        "total": len(needs_list),
        "validated": sum(
            1
            for need in needs_list
            if need.status
            in {"validated", "prioritized", "planned", "in_progress", "completed"}
        ),
        "critical": sum(1 for need in needs_list if need.urgency_level == "immediate"),
    }

    workshop_summary = {
        "total": len(workshops_list),
        "completed": sum(1 for item in workshops_list if item.status == "completed"),
        "in_progress": sum(
            1 for item in workshops_list if item.status == "in_progress"
        ),
    }

    status_display = dict(Assessment.STATUS_CHOICES).get(
        assessment.status, assessment.status
    )
    priority_display = dict(Assessment.PRIORITY_CHOICES).get(
        assessment.priority, assessment.priority
    )
    methodology_display = dict(Assessment.ASSESSMENT_METHODOLOGIES).get(
        assessment.primary_methodology, assessment.primary_methodology
    )
    impact_display = dict(Assessment.PRIORITY_CHOICES).get(
        assessment.impact_level, assessment.impact_level
    )

    context = {
        "assessment": assessment,
        "team_members": team_members,
        "needs_list": needs_list,
        "workshops_list": workshops_list,
        "needs_summary": needs_summary,
        "workshop_summary": workshop_summary,
        "status_display": status_display,
        "priority_display": priority_display,
        "methodology_display": methodology_display,
        "impact_display": impact_display,
    }
    return render(request, "mana/mana_assessment_detail.html", context)


@login_required
def mana_assessment_edit(request, assessment_id):
    """Allow users to edit an assessment using the frontend form."""

    assessment = get_object_or_404(
        Assessment.objects.select_related(
            "category",
            "community__barangay__municipality__province__region",
            "province__region",
            "region",
            "municipality__province__region",
            "barangay__municipality__province__region",
            "lead_assessor",
        ),
        pk=assessment_id,
    )

    if request.method == "POST":
        form = AssessmentUpdateForm(
            request.POST, instance=assessment, user=request.user
        )
        if form.is_valid():
            updated_assessment = form.save(user=request.user)
            messages.success(
                request,
                f'Assessment "{updated_assessment.title}" was updated successfully.',
            )
            return redirect(
                "common:mana_assessment_detail", assessment_id=updated_assessment.id
            )
    else:
        form = AssessmentUpdateForm(instance=assessment, user=request.user)

    community_records = (
        OBCCommunity.objects.filter(is_active=True)
        .select_related("barangay__municipality__province__region")
        .order_by(
            "barangay__municipality__province__name",
            "barangay__municipality__name",
            "barangay__name",
            "name",
        )
    )

    community_data = [
        {
            "id": str(community.id),
            "name": community.display_name or community.barangay.name,
            "barangay_id": community.barangay_id,
            "municipality_id": community.barangay.municipality_id,
            "province_id": community.barangay.municipality.province_id,
            "region_id": community.barangay.municipality.province.region_id,
        }
        for community in community_records
    ]

    return render(
        request,
        "mana/mana_assessment_edit.html",
        {
            "assessment": assessment,
            "form": form,
            "location_data": build_location_data(include_barangays=True),
            "community_data": community_data,
        },
    )


@login_required
def mana_assessment_delete(request, assessment_id):
    """Delete a MANA assessment."""
    assessment = get_object_or_404(Assessment, pk=assessment_id)

    assessment_title = assessment.title
    assessment.delete()

    messages.success(
        request,
        f'Assessment "{assessment_title}" was deleted successfully.',
    )
    return redirect("common:mana_manage_assessments")


@login_required
def mana_regional_overview(request):
    """
    Regional-level overview aligning with the MANA implementation guide.

    STAFF ONLY: This is the legacy MANA system for OOBC staff and authorized users.
    Workshop participants should use /mana/workshops/ (new sequential system).
    """
    # Enforce staff-only access
    if not request.user.is_staff and not request.user.has_perm(
        "mana.can_facilitate_workshop"
    ):
        messages.error(
            request,
            "Access denied. This area is restricted to OOBC staff. "
            "Participants should access workshops through their participant dashboard.",
        )
        return redirect("common:dashboard")

    regions = Region.objects.filter(is_active=True).order_by("name")
    region_ids = list(regions.values_list("id", flat=True))

    region_summary = {
        region.id: {
            "region": region,
            "assessments": {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "planning": 0,
                "reporting": 0,
                "desk_review": 0,
                "survey": 0,
                "kii": 0,
                "workshop": 0,
            },
            "needs": {"total": 0, "critical": 0, "validated": 0},
            "reports": {"total": 0, "finalized": 0, "validation": 0},
        }
        for region in regions
    }

    setup_form = RegionalWorkshopSetupForm(regions=regions)
    form_action = request.POST.get("form_name") if request.method == "POST" else None
    if form_action == "regional_setup":
        setup_form = RegionalWorkshopSetupForm(request.POST, regions=regions)
        if setup_form.is_valid():
            assessment = setup_form.save(user=request.user)

            start_date = setup_form.cleaned_data["planned_start_date"].strftime(
                "%Y-%m-%d"
            )
            target_participants = setup_form.cleaned_data.get("target_participants")

            create_workshop_activities(
                assessment,
                {
                    "planned_start_date": start_date,
                    "target_participants": str(target_participants or 30),
                },
            )

            messages.success(
                request,
                f'Regional workshop "{assessment.title}" initialized successfully.',
            )

            query = {"assessment": str(assessment.id), "active_tab": "workshop_1"}
            return redirect(
                f"{reverse('common:mana_regional_overview')}?{urlencode(query)}"
            )

        messages.error(
            request,
            "Please correct the errors below to initialize the regional workshop cycle.",
        )

    workshop_order = [
        "workshop_1",
        "workshop_2",
        "workshop_3",
        "workshop_4",
        "workshop_5",
    ]
    requested_tab = request.GET.get("active_tab") or request.POST.get("active_tab")
    active_workshop_tab = (
        requested_tab if requested_tab in workshop_order else workshop_order[0]
    )
    selected_assessment = None
    regional_workshop_assessments = (
        Assessment.objects.filter(
            assessment_level="regional", primary_methodology="workshop"
        )
        .select_related(
            "category",
            "lead_assessor",
            "community__barangay__municipality__province__region",
            "province__region",
        )
        .order_by("-created_at")
    )
    bound_workshop_forms = {}
    workshop_forms = []

    region_assessments = Assessment.objects.none()

    if region_ids:
        # Query both community-based and province-based assessments for the regions
        from django.db.models import Q

        region_assessments = (
            Assessment.objects.filter(
                Q(community__barangay__municipality__province__region_id__in=region_ids)
                | Q(province__region_id__in=region_ids)
            )
            .select_related(
                "community__barangay__municipality__province__region",
                "province__region",
                "category",
                "lead_assessor",
            )
            .order_by("-created_at")
        )

        regional_workshop_assessments = regional_workshop_assessments.filter(
            Q(province__region_id__in=region_ids)
            | Q(community__barangay__municipality__province__region_id__in=region_ids)
        )

        selected_assessment_id = request.POST.get("assessment") or request.GET.get(
            "assessment"
        )
        if selected_assessment_id:
            selected_assessment = regional_workshop_assessments.filter(
                id=selected_assessment_id
            ).first()

        if selected_assessment is None:
            selected_assessment = regional_workshop_assessments.first()

        aggregated = (
            region_assessments.annotate(
                resolved_region_id=Case(
                    When(
                        community__isnull=False,
                        then=F(
                            "community__barangay__municipality__province__region_id"
                        ),
                    ),
                    When(province__isnull=False, then=F("province__region_id")),
                    default=None,
                    output_field=IntegerField(),
                )
            )
            .values("resolved_region_id")
            .annotate(
                total=Count("id"),
                completed=Count("id", filter=Q(status="completed")),
                in_progress=Count(
                    "id", filter=Q(status__in=["data_collection", "analysis"])
                ),
                planning=Count("id", filter=Q(status__in=["planning", "preparation"])),
                reporting=Count("id", filter=Q(status="reporting")),
                desk_review=Count("id", filter=Q(primary_methodology="desk_review")),
                survey=Count("id", filter=Q(primary_methodology="survey")),
                kii=Count("id", filter=Q(primary_methodology="kii")),
                workshop=Count("id", filter=Q(primary_methodology="workshop")),
            )
        )

        for row in aggregated:
            summary = region_summary.get(row["resolved_region_id"])
            if not summary:
                continue
            assessments = summary["assessments"]
            assessments["total"] = row["total"]
            assessments["completed"] = row["completed"]
            assessments["in_progress"] = row["in_progress"]
            assessments["planning"] = row["planning"]
            assessments["reporting"] = row["reporting"]
            assessments["desk_review"] = row["desk_review"]
            assessments["survey"] = row["survey"]
            assessments["kii"] = row["kii"]
            assessments["workshop"] = row["workshop"]

        needs_agg = (
            Need.objects.filter(
                assessment__community__barangay__municipality__province__region_id__in=region_ids
            )
            .annotate(
                resolved_region_id=F(
                    "assessment__community__barangay__municipality__province__region_id"
                )
            )
            .values("resolved_region_id")
            .annotate(
                total=Count("id"),
                critical=Count("id", filter=Q(urgency_level="immediate")),
                validated=Count(
                    "id",
                    filter=Q(
                        status__in=[
                            "validated",
                            "prioritized",
                            "planned",
                            "in_progress",
                            "completed",
                        ]
                    ),
                ),
            )
        )

        for row in needs_agg:
            summary = region_summary.get(row["resolved_region_id"])
            if not summary:
                continue
            needs = summary["needs"]
            needs["total"] = row["total"]
            needs["critical"] = row["critical"]
            needs["validated"] = row["validated"]

        reports_agg = (
            MANAReport.objects.filter(
                assessment__community__barangay__municipality__province__region_id__in=region_ids
            )
            .annotate(
                resolved_region_id=F(
                    "assessment__community__barangay__municipality__province__region_id"
                )
            )
            .values("resolved_region_id")
            .annotate(
                total=Count("id"),
                finalized=Count(
                    "id", filter=Q(report_status__in=["final", "submitted"])
                ),
                validation=Count("id", filter=Q(report_status="validation")),
            )
        )

        for row in reports_agg:
            summary = region_summary.get(row["resolved_region_id"])
            if not summary:
                continue
            reports = summary["reports"]
            reports["total"] = row["total"]
            reports["finalized"] = row["finalized"]
            reports["validation"] = row["validation"]

    workshop_activity_map = {}
    if selected_assessment:
        workshop_queryset = (
            selected_assessment.workshop_activities.filter(
                workshop_type__in=workshop_order
            )
            .select_related("assessment")
            .order_by("scheduled_date", "start_time")
        )
        for activity in workshop_queryset:
            workshop_activity_map[activity.workshop_type] = activity

    if (
        request.method == "POST"
        and form_action != "regional_setup"
        and selected_assessment
    ):
        target_id = request.POST.get("workshop_id")
        if target_id:
            try:
                activity = selected_assessment.workshop_activities.get(pk=target_id)
            except WorkshopActivity.DoesNotExist:
                messages.error(
                    request,
                    "Unable to locate the selected workshop for this assessment.",
                )
            else:
                workshop_activity_map.setdefault(activity.workshop_type, activity)
                active_workshop_tab = activity.workshop_type

                form = None
                form_class = WORKSHOP_FORM_MAP.get(activity.workshop_type)
                if form_class is None:
                    messages.error(request, "Unsupported workshop configuration.")
                else:
                    form = form_class(request.POST, instance=activity)
                    if form.is_valid():
                        form.save()
                        messages.success(
                            request,
                            f'Updated "{activity.title}" workshop details.',
                        )
                        query = urlencode(
                            {
                                "assessment": str(selected_assessment.id),
                                "active_tab": activity.workshop_type,
                            }
                        )
                        return redirect(
                            f"{reverse('common:mana_regional_overview')}?{query}"
                        )

                if form is not None:
                    bound_workshop_forms[activity.workshop_type] = form
        else:
            messages.error(
                request,
                "No workshop was specified. Please use the provided form controls.",
            )

    workshop_type_labels = dict(WorkshopActivity.WORKSHOP_TYPES)
    for workshop_type in workshop_order:
        form_class = WORKSHOP_FORM_MAP.get(workshop_type)
        base_fields = form_class.base_fields if form_class else {}
        default_question_prompts = [
            {
                "name": name,
                "label": field.label,
            }
            for name, field in base_fields.items()
            if name not in (*WORKSHOP_GENERAL_FIELDS, *WORKSHOP_SYNTHESIS_FIELDS)
        ]

        activity = workshop_activity_map.get(workshop_type)
        label = workshop_type_labels.get(
            workshop_type, workshop_type.replace("_", " ").title()
        )

        form_instance = None
        if activity:
            form_instance = bound_workshop_forms.get(workshop_type)
            if form_instance is None:
                if form_class:
                    form_instance = form_class(instance=activity)

        # Aggregate participant response analytics for this workshop
        response_analytics = None
        participant_responses = []
        if activity and selected_assessment:
            total_participants = WorkshopParticipantAccount.objects.filter(
                assessment=selected_assessment
            ).count()

            submitted_responses = WorkshopResponse.objects.filter(
                workshop=activity, status="submitted"
            ).select_related("participant__user")

            submitted_count = (
                submitted_responses.values("participant").distinct().count()
            )

            response_analytics = {
                "total_participants": total_participants,
                "submitted_count": submitted_count,
                "submission_rate": (
                    (submitted_count / total_participants * 100)
                    if total_participants > 0
                    else 0
                ),
            }

            # Fetch individual participant responses
            from mana.schema import get_questions_for_workshop

            questions = get_questions_for_workshop(workshop_type)

            participants_with_responses = submitted_responses.values(
                "participant"
            ).distinct()

            for participant_data in participants_with_responses:
                participant_id = participant_data["participant"]
                participant = WorkshopParticipantAccount.objects.select_related(
                    "user", "province"
                ).get(id=participant_id)

                responses = submitted_responses.filter(
                    participant=participant
                ).order_by("question_id")

                qa_pairs = []
                for question in questions:
                    response = responses.filter(question_id=question["id"]).first()
                    qa_pairs.append(
                        {
                            "question": question,
                            "response": response,
                        }
                    )

                participant_responses.append(
                    {
                        "participant": participant,
                        "responses": qa_pairs,
                        "submitted_at": (
                            responses.first().submitted_at
                            if responses.exists()
                            else None
                        ),
                    }
                )

        workshop_forms.append(
            {
                "type": workshop_type,
                "label": label,
                "activity": activity,
                "form": form_instance,
                "completed": bool(activity and activity.status == "completed"),
                "general_fields": WORKSHOP_GENERAL_FIELDS,
                "synthesis_fields": WORKSHOP_SYNTHESIS_FIELDS,
                "question_fields": (
                    getattr(form_instance, "question_field_names", [])
                    if form_instance
                    else [item["name"] for item in default_question_prompts]
                ),
                "question_prompts": default_question_prompts,
                "response_analytics": response_analytics,
                "participant_responses": participant_responses,
            }
        )

    regional_workshop_assessments = list(regional_workshop_assessments)

    region_cards = [region_summary[region.id] for region in regions]

    methodology_mix = {
        "Desk Review": sum(card["assessments"]["desk_review"] for card in region_cards),
        "Survey": sum(card["assessments"]["survey"] for card in region_cards),
        "Key Informant Interview": sum(
            card["assessments"]["kii"] for card in region_cards
        ),
        "Workshop": sum(card["assessments"]["workshop"] for card in region_cards),
    }
    methodology_breakdown = [
        {"label": label, "value": value} for label, value in methodology_mix.items()
    ]

    global_stats = {
        "total_assessments": sum(card["assessments"]["total"] for card in region_cards),
        "completed": sum(card["assessments"]["completed"] for card in region_cards),
        "in_progress": sum(card["assessments"]["in_progress"] for card in region_cards),
        "planning": sum(card["assessments"]["planning"] for card in region_cards),
        "reporting": sum(card["assessments"]["reporting"] for card in region_cards),
        "needs_identified": sum(card["needs"]["total"] for card in region_cards),
        "needs_validated": sum(card["needs"]["validated"] for card in region_cards),
    }

    reports_summary = {
        "total": sum(card["reports"]["total"] for card in region_cards),
        "finalized": sum(card["reports"]["finalized"] for card in region_cards),
        "validation": sum(card["reports"]["validation"] for card in region_cards),
    }

    dav = {
        "phase": "Pre-MANA Preparation",
        "summary": "Establish clear objectives, coverage, resources, and risk mitigation steps.",
        "workstreams": [
            {
                "title": "Activity Management Plan",
                "details": (
                    "Define SMART objectives, geographic scope, timelines, budget, and "
                    "risk mitigation strategies for the regional deployment."
                ),
            },
            {
                "title": "Team Composition",
                "details": (
                    "Confirm core team roles (Team Leader, Facilitators, Documenters, "
                    "Secretariat/logistics) and align expectations prior to travel."
                ),
            },
            {
                "title": "Stakeholder Coordination",
                "details": (
                    "Secure endorsements from LGUs, coordinate courtesy calls, and enlist "
                    "community leaders plus NGA partners for mobilization."
                ),
            },
            {
                "title": "Logistics Blueprint",
                "details": (
                    "Finalize venue readiness, equipment, transportation, accommodations, "
                    "and halal-compliant meals with contingency plans."
                ),
            },
            {
                "title": "Participant Management",
                "details": (
                    "Ensure balanced representation across sectors, dispatch invitations, "
                    "and prepare onboarding materials for delegates."
                ),
            },
        ],
    }

    during = {
        "phase": "Field Implementation (5-Day Flow)",
        "summary": "Deliver structured workshops while keeping space for adaptive facilitation.",
        "workstreams": [
            {
                "title": "Day 1: Mobilization",
                "details": (
                    "Handle arrivals, registration, issuance of MANA kits, and evening "
                    "team briefing ahead of plenary opening."
                ),
            },
            {
                "title": "Day 2: Context Setting",
                "details": (
                    "Run opening rites, present OOBC mandates, deliver spatial overviews, "
                    "and facilitate Workshop 1 on community context."
                ),
            },
            {
                "title": "Day 3: Aspirations & Collaboration",
                "details": (
                    "Guide Workshops 2 and 3 to surface vision statements, priority sectors, "
                    "and collaboration pathways with local actors."
                ),
            },
            {
                "title": "Day 4: Feedback & Action Planning",
                "details": (
                    "Collect feedback on existing initiatives, analyse root causes, and "
                    "craft ways forward culminating in closing program."
                ),
            },
            {
                "title": "Daily Debriefs",
                "details": (
                    "Conduct end-of-day reflections to capture wins, address issues, and "
                    "prime the team for succeeding sessions."
                ),
            },
        ],
    }

    post = {
        "phase": "Post-MANA Integration",
        "summary": "Transform outputs into validated reports and actionable plans.",
        "workstreams": [
            {
                "title": "Data Processing",
                "details": (
                    "Encode, clean, and analyse quantitative and qualitative datasets, "
                    "including geospatial layers."
                ),
            },
            {
                "title": "Report Development",
                "details": (
                    "Draft the regional MANA report, convene validation workshops, and "
                    "incorporate feedback prior to submission."
                ),
            },
            {
                "title": "Dissemination",
                "details": (
                    "Prepare policy briefs, presentations, and community feedback sessions "
                    "to socialize results."
                ),
            },
            {
                "title": "Action Planning",
                "details": (
                    "Integrate priorities into OOBC and partner programming, budgeting, and "
                    "advocacy pipelines."
                ),
            },
            {
                "title": "MEL & Knowledge Capture",
                "details": (
                    "Evaluate the deployment, document lessons learned, and update playbooks "
                    "for future cycles."
                ),
            },
        ],
    }

    davao_activity_flow = [dav, during, post]

    recent_assessments = region_assessments[:8]

    context = {
        "legal_basis": LEGAL_BASIS,
        "core_principles": CORE_PRINCIPLES,
        "mana_phases": MANA_PHASES,
        "reporting_timeline": REPORTING_TIMELINE,
        "mel_practices": MEL_PRACTICES,
        "prep_checklist": ACTIVITY_PREP_CHECKLIST,
        "field_trackers": FIELD_ACTIVITY_TRACKERS,
        "post_activity_process": POST_ACTIVITY_PROCESS,
        "region_cards": region_cards,
        "global_stats": global_stats,
        "methodology_breakdown": methodology_breakdown,
        "reports_summary": reports_summary,
        "davao_activity_flow": davao_activity_flow,
        "recent_assessments": recent_assessments,
        "regional_workshop_assessments": regional_workshop_assessments,
        "selected_assessment": selected_assessment,
        "workshop_forms": workshop_forms,
        "active_workshop_tab": active_workshop_tab,
        "regional_setup_form": setup_form,
        "location_data": build_location_data(include_barangays=False),
    }
    return render(request, "mana/mana_regional_overview.html", context)


def _build_provincial_snapshot(provinces, *, recent_limit=8, include_querysets=False):
    """Assemble aggregated metrics and card data for the given provinces."""

    provinces = list(provinces)
    province_summary = {
        province.id: {
            "province": province,
            "assessments": {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "planning": 0,
                "reporting": 0,
                "desk_review": 0,
                "survey": 0,
                "kii": 0,
                "workshop": 0,
                "community_level": 0,
                "municipal_level": 0,
                "barangay_level": 0,
            },
            "needs": {"total": 0, "critical": 0, "validated": 0},
            "reports": {"total": 0, "finalized": 0, "validation": 0},
        }
        for province in provinces
    }

    empty_global_stats = {
        "total_assessments": 0,
        "completed": 0,
        "in_progress": 0,
        "planning": 0,
        "reporting": 0,
        "needs_identified": 0,
        "needs_validated": 0,
    }
    empty_reports_summary = {"total": 0, "finalized": 0, "validation": 0}

    if not province_summary:
        snapshot = {
            "cards": [],
            "global_stats": empty_global_stats,
            "methodology_breakdown": [],
            "coverage_breakdown": [],
            "reports_summary": empty_reports_summary,
            "recent_assessments": [],
        }
        if include_querysets:
            snapshot["assessments_queryset"] = Assessment.objects.none()
            snapshot["reports_queryset"] = MANAReport.objects.none()
        return snapshot

    province_ids = list(province_summary.keys())

    provincial_assessments = (
        Assessment.objects.filter(
            community__barangay__municipality__province_id__in=province_ids
        )
        .select_related(
            "community__barangay__municipality__province__region",
            "category",
            "lead_assessor",
        )
        .order_by("-created_at")
    )

    aggregated = (
        provincial_assessments.annotate(
            derived_province_id=F("community__barangay__municipality__province_id")
        )
        .values("derived_province_id")
        .annotate(
            total=Count("id"),
            completed=Count("id", filter=Q(status="completed")),
            in_progress=Count(
                "id", filter=Q(status__in=["data_collection", "analysis"])
            ),
            planning=Count("id", filter=Q(status__in=["planning", "preparation"])),
            reporting=Count("id", filter=Q(status="reporting")),
            desk_review=Count("id", filter=Q(primary_methodology="desk_review")),
            survey=Count("id", filter=Q(primary_methodology="survey")),
            kii=Count("id", filter=Q(primary_methodology="kii")),
            workshop=Count("id", filter=Q(primary_methodology="workshop")),
            community_level=Count("id", filter=Q(assessment_level="community")),
            municipal_level=Count("id", filter=Q(assessment_level="city_municipal")),
            barangay_level=Count("id", filter=Q(assessment_level="barangay")),
        )
    )

    for row in aggregated:
        summary = province_summary.get(row["derived_province_id"])
        if not summary:
            continue
        assessments = summary["assessments"]
        assessments["total"] = row["total"]
        assessments["completed"] = row["completed"]
        assessments["in_progress"] = row["in_progress"]
        assessments["planning"] = row["planning"]
        assessments["reporting"] = row["reporting"]
        assessments["desk_review"] = row["desk_review"]
        assessments["survey"] = row["survey"]
        assessments["kii"] = row["kii"]
        assessments["workshop"] = row["workshop"]
        assessments["community_level"] = row["community_level"]
        assessments["municipal_level"] = row["municipal_level"]
        assessments["barangay_level"] = row["barangay_level"]

    needs_queryset = Need.objects.filter(
        assessment__community__barangay__municipality__province_id__in=province_ids
    )

    needs_agg = (
        needs_queryset.annotate(
            derived_province_id=F(
                "assessment__community__barangay__municipality__province_id"
            )
        )
        .values("derived_province_id")
        .annotate(
            total=Count("id"),
            critical=Count("id", filter=Q(urgency_level="immediate")),
            validated=Count(
                "id",
                filter=Q(
                    status__in=[
                        "validated",
                        "prioritized",
                        "planned",
                        "in_progress",
                        "completed",
                    ]
                ),
            ),
        )
    )

    for row in needs_agg:
        summary = province_summary.get(row["derived_province_id"])
        if not summary:
            continue
        needs = summary["needs"]
        needs["total"] = row["total"]
        needs["critical"] = row["critical"]
        needs["validated"] = row["validated"]

    reports_queryset = (
        MANAReport.objects.filter(
            assessment__community__barangay__municipality__province_id__in=province_ids
        )
        .select_related(
            "assessment__community__barangay__municipality__province__region"
        )
        .order_by("-created_at")
    )

    reports_agg = (
        reports_queryset.annotate(
            derived_province_id=F(
                "assessment__community__barangay__municipality__province_id"
            )
        )
        .values("derived_province_id")
        .annotate(
            total=Count("id"),
            finalized=Count("id", filter=Q(report_status__in=["final", "submitted"])),
            validation=Count("id", filter=Q(report_status="validation")),
        )
    )

    for row in reports_agg:
        summary = province_summary.get(row["derived_province_id"])
        if not summary:
            continue
        reports = summary["reports"]
        reports["total"] = row["total"]
        reports["finalized"] = row["finalized"]
        reports["validation"] = row["validation"]

    cards = [
        province_summary[province.id]
        for province in provinces
        if province.id in province_summary
    ]

    methodology_mix = {
        "Desk Review": sum(card["assessments"]["desk_review"] for card in cards),
        "Survey": sum(card["assessments"]["survey"] for card in cards),
        "Key Informant Interview": sum(card["assessments"]["kii"] for card in cards),
        "Workshop": sum(card["assessments"]["workshop"] for card in cards),
    }
    methodology_breakdown = [
        {"label": label, "value": value} for label, value in methodology_mix.items()
    ]

    coverage_mix = {
        "Community": sum(card["assessments"]["community_level"] for card in cards),
        "Municipal": sum(card["assessments"]["municipal_level"] for card in cards),
        "Barangay": sum(card["assessments"]["barangay_level"] for card in cards),
    }
    coverage_breakdown = [
        {"label": label, "value": value} for label, value in coverage_mix.items()
    ]

    global_stats = {
        "total_assessments": sum(card["assessments"]["total"] for card in cards),
        "completed": sum(card["assessments"]["completed"] for card in cards),
        "in_progress": sum(card["assessments"]["in_progress"] for card in cards),
        "planning": sum(card["assessments"]["planning"] for card in cards),
        "reporting": sum(card["assessments"]["reporting"] for card in cards),
        "needs_identified": sum(card["needs"]["total"] for card in cards),
        "needs_validated": sum(card["needs"]["validated"] for card in cards),
    }

    reports_summary = {
        "total": sum(card["reports"]["total"] for card in cards),
        "finalized": sum(card["reports"]["finalized"] for card in cards),
        "validation": sum(card["reports"]["validation"] for card in cards),
    }

    if recent_limit is None:
        recent_assessments = list(provincial_assessments)
    else:
        recent_assessments = list(provincial_assessments[:recent_limit])

    snapshot = {
        "cards": cards,
        "global_stats": global_stats,
        "methodology_breakdown": methodology_breakdown,
        "coverage_breakdown": coverage_breakdown,
        "reports_summary": reports_summary,
        "recent_assessments": recent_assessments,
    }

    if include_querysets:
        snapshot["assessments_queryset"] = provincial_assessments
        snapshot["reports_queryset"] = reports_queryset

    return snapshot


@login_required
def mana_provincial_overview(request):
    """Provincial dashboards and operational guidance for MANA deployments."""

    from urllib.parse import urlencode

    def parse_identifier(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    region_filter = parse_identifier(request.GET.get("region"))
    province_filter = parse_identifier(request.GET.get("province"))
    search_term = (request.GET.get("search") or "").strip()

    regions = Region.objects.filter(is_active=True).order_by("name")

    provinces_base_qs = (
        Province.objects.filter(is_active=True)
        .select_related("region")
        .order_by("name")
    )
    if region_filter:
        provinces_base_qs = provinces_base_qs.filter(region_id=region_filter)

    province_options = list(provinces_base_qs)

    filtered_provinces_qs = provinces_base_qs
    if province_filter:
        filtered_provinces_qs = filtered_provinces_qs.filter(id=province_filter)
    if search_term:
        filtered_provinces_qs = filtered_provinces_qs.filter(
            name__icontains=search_term
        )

    provinces = list(filtered_provinces_qs)

    if province_filter and not provinces:
        fallback = (
            Province.objects.filter(pk=province_filter, is_active=True)
            .select_related("region")
            .first()
        )
        if fallback:
            provinces.append(fallback)

    snapshot = _build_provincial_snapshot(provinces)
    province_cards = snapshot["cards"]
    global_stats = snapshot["global_stats"]
    methodology_breakdown = snapshot["methodology_breakdown"]
    coverage_breakdown = snapshot["coverage_breakdown"]
    reports_summary = snapshot["reports_summary"]
    recent_assessments = snapshot["recent_assessments"]

    query_string = request.GET.copy()
    encoded_query = query_string.urlencode()
    overview_base_url = reverse("common:mana_provincial_overview")
    return_url = (
        f"{overview_base_url}?{encoded_query}" if encoded_query else overview_base_url
    )

    page_size_options = [5, 10, 25]
    try:
        page_size = int(request.GET.get("page_size", page_size_options[0]))
    except (TypeError, ValueError):
        page_size = page_size_options[0]

    if page_size not in page_size_options:
        page_size = page_size_options[0]

    paginator = Paginator(province_cards, page_size)

    province_page = None
    page_cards = []
    if paginator.count:
        province_page = paginator.get_page(request.GET.get("page"))
        page_cards = list(province_page.object_list)

    province_rows = []
    for card in page_cards:
        province = card["province"]
        edit_path = reverse("common:mana_province_edit", args=[province.id])
        delete_path = reverse("common:mana_province_delete", args=[province.id])

        province_rows.append(
            {
                "province": province,
                "region": province.region,
                "assessments": card["assessments"],
                "needs": card["needs"],
                "reports": card["reports"],
                "detail_url": reverse(
                    "common:mana_provincial_card_detail", args=[province.id]
                ),
                "edit_url": (
                    f"{edit_path}?{urlencode({'next': return_url})}"
                    if edit_path
                    else ""
                ),
                "delete_url": delete_path,
            }
        )

    base_query_params = request.GET.copy()
    base_query_params["page_size"] = str(page_size)
    if "page" in base_query_params:
        del base_query_params["page"]

    page_query_string = base_query_params.urlencode()
    page_query_prefix = f"{page_query_string}&" if page_query_string else ""

    selected_region = None
    if region_filter:
        selected_region = next(
            (region for region in regions if region.pk == region_filter), None
        )

    selected_province = None
    if province_filter:
        selected_province = next(
            (
                province
                for province in province_options
                if province.pk == province_filter
            ),
            None,
        )

    team_roles = [
        {
            "title": "Team Leader / Executive Director",
            "details": (
                "Provides strategic direction, represents OOBC at high-level meetings, "
                "and assures quality of deliverables."
            ),
        },
        {
            "title": "Deputy Team Leader / DMO IV",
            "details": (
                "Oversees day-to-day execution, coordinates functional teams, and finalizes "
                "provincial reports."
            ),
        },
        {
            "title": "Facilitators",
            "details": (
                "Lead participatory sessions, analyse emerging issues, and ensure balanced "
                "participation across sectors."
            ),
        },
        {
            "title": "Documenters",
            "details": (
                "Record proceedings, manage multimedia assets, transcribe inputs, and "
                "support synthesis."
            ),
        },
        {
            "title": "Information System Analyst",
            "details": (
                "Handles spatial mapping, data visualization, and supports quantitative and "
                "qualitative analysis."
            ),
        },
        {
            "title": "Secretariat / Logistics",
            "details": (
                "Manage venues, travel, registrations, inventories, safety protocols, and "
                "post-activity communications."
            ),
        },
    ]

    logistics_checklist = [
        {
            "title": "Venue Readiness",
            "items": [
                "Ensure plenary and breakout rooms, audio-visual equipment, and internet.",
                "Provide prayer space, gender-sensitive facilities, and security protocols.",
            ],
        },
        {
            "title": "Mobility & Accommodation",
            "items": [
                "Arrange transport for staff and participants, with special focus on remote areas.",
                "Confirm lodging, meals (halal-compliant), and emergency contacts/first-aid.",
            ],
        },
        {
            "title": "Workshop Materials",
            "items": [
                "Prepare registration kits, manuals, translation aids, and documentation forms.",
                "Maintain equipment inventory (laptops, projectors, printers, cameras, recorders).",
            ],
        },
    ]

    stakeholder_channels = [
        {
            "title": "LGU & NGA Interface",
            "details": (
                "Schedule courtesy calls, provide concept notes, and establish monitoring "
                "coordination groups."
            ),
        },
        {
            "title": "Community Gatekeepers",
            "details": (
                "Engage traditional, religious, youth, and women leaders for mobilization "
                "and co-facilitation roles."
            ),
        },
        {
            "title": "Feedback Loop",
            "details": (
                "Activate suggestion boxes, digital forms, and periodic dialogues to capture "
                "community sentiments before and after fieldwork."
            ),
        },
    ]

    data_tools = [
        {
            "title": "Survey Instruments",
            "details": "Standardized OBC survey capturing demographic, socio-economic, and cultural data.",
        },
        {
            "title": "KII & FGD Guides",
            "details": "Structured prompts for thematic deep-dives, aligned with core principles.",
        },
        {
            "title": "Geospatial Checklists",
            "details": "Mapping references for resources, services, and priority locations.",
        },
        {
            "title": "Desk Review Matrix",
            "details": "Template to consolidate secondary data sources and highlight gaps.",
        },
    ]

    capacity_focus = [
        {
            "title": "Workshop 1",
            "details": "Understand history, demographics, and stakeholder mapping per municipality/barangay.",
        },
        {
            "title": "Workshop 2",
            "details": "Document aspirations, priority needs, and sectoral interventions.",
        },
        {
            "title": "Workshop 3",
            "details": "Assess collaboration dynamics and design empowerment strategies.",
        },
        {
            "title": "Workshop 4",
            "details": "Gather feedback on existing initiatives and surface implementation lessons.",
        },
        {
            "title": "Workshop 5",
            "details": "Analyse root causes, factor linkages, and differentiated impacts.",
        },
        {
            "title": "Workshop 6",
            "details": "Craft ways forward, stakeholder role matrices, and preliminary action plans.",
        },
    ]

    context = {
        "regions": regions,
        "province_options": province_options,
        "current_region": str(region_filter) if region_filter else "",
        "current_province": str(province_filter) if province_filter else "",
        "search_term": search_term,
        "province_rows": province_rows,
        "province_count": paginator.count,
        "return_url": return_url,
        "selected_region": selected_region,
        "selected_province": selected_province,
        "global_stats": global_stats,
        "methodology_breakdown": methodology_breakdown,
        "coverage_breakdown": coverage_breakdown,
        "reports_summary": reports_summary,
        "team_roles": team_roles,
        "logistics_checklist": logistics_checklist,
        "stakeholder_channels": stakeholder_channels,
        "data_tools": data_tools,
        "capacity_focus": capacity_focus,
        "recent_assessments": recent_assessments,
        "selection_active": bool(province_cards),
        "province_page": province_page,
        "page_size": page_size,
        "page_size_options": page_size_options,
        "page_query_prefix": page_query_prefix,
    }
    return render(request, "mana/mana_provincial_overview.html", context)


@login_required
def mana_provincial_card_detail(request, province_id):
    """Detailed provincial assessment card view with operational breakdown."""

    province = get_object_or_404(
        Province.objects.select_related("region").filter(is_active=True),
        pk=province_id,
    )

    snapshot = _build_provincial_snapshot(
        [province], recent_limit=15, include_querysets=True
    )
    card = snapshot["cards"][0] if snapshot["cards"] else None
    global_stats = snapshot["global_stats"]
    methodology_breakdown = snapshot["methodology_breakdown"]
    coverage_breakdown = snapshot["coverage_breakdown"]
    reports_summary = snapshot["reports_summary"]
    recent_assessments = snapshot["recent_assessments"]
    assessments_queryset = snapshot.get(
        "assessments_queryset", Assessment.objects.none()
    )
    reports_queryset = snapshot.get("reports_queryset", MANAReport.objects.none())

    if card is None:
        card = {
            "province": province,
            "assessments": {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "planning": 0,
                "reporting": 0,
                "desk_review": 0,
                "survey": 0,
                "kii": 0,
                "workshop": 0,
                "community_level": 0,
                "municipal_level": 0,
                "barangay_level": 0,
            },
            "needs": {"total": 0, "critical": 0, "validated": 0},
            "reports": {"total": 0, "finalized": 0, "validation": 0},
        }

    status_display = dict(Assessment.STATUS_CHOICES)
    assessment_status_breakdown = [
        {
            "code": row["status"],
            "label": status_display.get(
                row["status"], row["status"].replace("_", " ").title()
            ),
            "total": row["total"],
        }
        for row in assessments_queryset.values("status")
        .annotate(total=Count("id"))
        .order_by("-total")
    ]

    needs_queryset = Need.objects.filter(
        assessment__community__barangay__municipality__province=province
    )

    needs_category_breakdown = [
        {
            "label": row["category__name"] or "Uncategorised",
            "total": row["total"],
        }
        for row in needs_queryset.values("category__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:6]
    ]

    critical_needs = list(
        needs_queryset.filter(urgency_level="immediate")
        .select_related("category")
        .order_by("-created_at")[:6]
    )

    latest_reports = list(reports_queryset[:6])
    detailed_assessments = list(assessments_queryset[:20])

    overview_link = f"{reverse('common:mana_provincial_overview')}?region={province.region_id}&province={province.id}"

    context = {
        "province": province,
        "card": card,
        "global_stats": global_stats,
        "methodology_breakdown": methodology_breakdown,
        "coverage_breakdown": coverage_breakdown,
        "reports_summary": reports_summary,
        "recent_assessments": recent_assessments,
        "assessment_status_breakdown": assessment_status_breakdown,
        "needs_category_breakdown": needs_category_breakdown,
        "critical_needs": critical_needs,
        "latest_reports": latest_reports,
        "detailed_assessments": detailed_assessments,
        "overview_link": overview_link,
    }
    return render(request, "mana/mana_provincial_card_detail.html", context)


@login_required
def mana_province_edit(request, province_id):
    """Edit basic province metadata used across provincial MANA views."""

    province = get_object_or_404(
        Province.objects.select_related("region"), pk=province_id, is_active=True
    )
    next_url = (
        request.GET.get("next")
        or request.POST.get("next")
        or reverse("common:mana_provincial_overview")
    )

    if request.method == "POST":
        form = ProvinceForm(request.POST, instance=province)
        if form.is_valid():
            form.save()
            messages.success(
                request, f'Updated province information for "{province.name}".'
            )
            return redirect(next_url)
        messages.error(request, "Please correct the highlighted errors below.")
    else:
        form = ProvinceForm(instance=province)

    context = {
        "form": form,
        "province": province,
        "next_url": next_url,
    }
    return render(request, "mana/mana_province_form.html", context)


@login_required
@require_POST
def mana_province_delete(request, province_id):
    """Soft delete a province from the provincial management listing."""

    province = get_object_or_404(Province, pk=province_id)
    next_url = request.POST.get("next") or reverse("common:mana_provincial_overview")
    province_name = province.name

    if province.is_active:
        province.is_active = False
        province.save(update_fields=["is_active"])
        messages.success(request, f'Province "{province_name}" archived successfully.')
    else:
        messages.info(request, f'Province "{province_name}" is already archived.')

    return redirect(next_url)


@login_required
def mana_desk_review(request):
    """Desk review methodology hub anchored on the MANA guidelines."""
    from django.db.models import Count, Q

    from mana.models import Assessment, MANAReport

    if request.method == "POST":
        form = DeskReviewQuickEntryForm(request.POST, user=request.user)
        if form.is_valid():
            assessment = form.save(user=request.user)
            messages.success(
                request,
                f'Logged desk review "{assessment.title}" for {assessment.community}.',
            )
            return redirect("common:mana_desk_review")
        messages.error(request, "Please correct the highlighted errors below.")
    else:
        form = DeskReviewQuickEntryForm(user=request.user)

    desk_assessments = (
        Assessment.objects.filter(primary_methodology="desk_review")
        .select_related(
            "community__barangay__municipality__province__region",
            "category",
            "lead_assessor",
        )
        .order_by("-created_at")
    )

    desk_stats = desk_assessments.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="completed")),
        in_progress=Count(
            "id",
            filter=Q(status__in=["data_collection", "analysis", "reporting"]),
        ),
        planning=Count("id", filter=Q(status__in=["planning", "preparation"])),
    )

    desk_reports = (
        MANAReport.objects.filter(assessment__primary_methodology="desk_review")
        .select_related(
            "assessment__community__barangay__municipality__province__region"
        )
        .order_by("-created_at")[:6]
    )

    quick_actions = [
        {
            "title": "Full Assessment Setup",
            "description": "Open the complete assessment wizard for comprehensive desk reviews.",
            "icon": "fas fa-clipboard-list",
            "url": f"{reverse('common:mana_new_assessment')}?primary_methodology=desk_review",
            "cta": "Launch Wizard",
            "icon_bg": "from-green-500 to-green-600",
            "cta_class": "text-green-600",
        },
        {
            "title": "Manage Desk Reviews",
            "description": "Track progress, update statuses, and coordinate deliverables.",
            "icon": "fas fa-tasks",
            "url": f"{reverse('common:mana_manage_assessments')}?methodology=desk_review",
            "cta": "View Pipeline",
            "icon_bg": "from-blue-500 to-blue-600",
            "cta_class": "text-blue-600",
        },
        {
            "title": "Data Handling Guide",
            "description": "Review sourcing, citation, and validation standards for desk work.",
            "icon": "fas fa-book-open",
            "url": reverse("common:data_guidelines"),
            "cta": "Read Guide",
            "icon_bg": "from-purple-500 to-purple-600",
            "cta_class": "text-purple-600",
        },
    ]

    desk_review_flow = [
        {
            "title": "Planning & Scoping",
            "items": [
                "Confirm objectives, thematic coverage, and alignment with OOBC mandate.",
                "Inventory available administrative data, past consultations, and spatial resources.",
                "Set validation checkpoints with technical experts and community representatives.",
            ],
        },
        {
            "title": "Evidence Consolidation",
            "items": [
                "Review PSA, MINDA, LGU plans, NGO reports, and previous OBC-MANA outputs.",
                "Map information gaps against Social, Economic, Cultural, and Rights pillars.",
                "Track data provenance and reliability for proper citation and transparency.",
            ],
        },
        {
            "title": "Analysis & Synthesis",
            "items": [
                "Triangulate quantitative indicators with qualitative narratives and spatial insights.",
                "Identify trends, disparities, and emerging issues requiring field validation.",
                "Prepare thematic briefs to guide subsequent consultations or surveys.",
            ],
        },
        {
            "title": "Validation & Reporting",
            "items": [
                "Engage subject matter experts and community proxies for technical checks.",
                "Document assumptions, limitations, and recommended follow-on methodologies.",
                "Populate the MANA report template with desk-review-derived findings and references.",
            ],
        },
    ]

    evidence_matrix = [
        {
            "title": "Social Development",
            "sources": [
                "Education statistics, health situationers, social protection coverage, basic services data.",
            ],
        },
        {
            "title": "Economic Development",
            "sources": [
                "Livelihood assessments, infrastructure inventories, enterprise support programs, market access studies.",
            ],
        },
        {
            "title": "Cultural Development",
            "sources": [
                "Heritage documentation, religious institution mapping, traditional crafts registries, cultural promotion initiatives.",
            ],
        },
        {
            "title": "Protection of Rights",
            "sources": [
                "Governance reports, land tenure records, justice and security data, human rights monitoring outputs.",
            ],
        },
    ]

    quality_controls = [
        "Maintain detailed bibliographies, citations, and annex references for transparency.",
        "Flag contradictory data points and propose field verification strategies.",
        "Ensure data protection rules are followed when handling sensitive secondary sources.",
    ]

    documentation_requirements = [
        "Executive summary distilling key findings and implications for next steps.",
        "Context/background referencing legal mandates, geography, and previous engagements.",
        "Methodology section describing desk review process and validation steps.",
        "Findings organised by program pillars with spatial/thematic linkages.",
        "Priority issues with initial policy/program recommendations aligned with Moral Governance.",
        "Implementation roadmap outlining sequencing, roles, and resource considerations.",
        "Annexes containing data sources, tools, maps, and reference materials.",
    ]

    context = {
        "legal_basis": LEGAL_BASIS,
        "core_principles": CORE_PRINCIPLES,
        "mana_phases": MANA_PHASES,
        "desk_stats": desk_stats,
        "desk_review_flow": desk_review_flow,
        "evidence_matrix": evidence_matrix,
        "quality_controls": quality_controls,
        "documentation_requirements": documentation_requirements,
        "desk_assessments": desk_assessments[:8],
        "desk_reports": desk_reports,
        "quick_actions": quick_actions,
        "desk_review_form": form,
    }
    return render(request, "mana/mana_desk_review.html", context)


@login_required
def mana_survey_module(request):
    """Survey operations playbook for MANA field deployments."""
    from django.db.models import Count, Q

    from mana.models import Assessment

    if request.method == "POST":
        survey_form = SurveyQuickEntryForm(request.POST, user=request.user)
        if survey_form.is_valid():
            assessment = survey_form.save(user=request.user)
            messages.success(
                request,
                f'Survey cycle "{assessment.title}" logged for {assessment.community}.',
            )
            return redirect("common:mana_survey_module")
        messages.error(request, "Please correct the highlighted errors below.")
    else:
        survey_form = SurveyQuickEntryForm(user=request.user)

    survey_assessments = (
        Assessment.objects.filter(primary_methodology="survey")
        .select_related(
            "community__barangay__municipality__province__region",
            "category",
            "lead_assessor",
        )
        .order_by("-created_at")
    )

    survey_stats = survey_assessments.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="completed")),
        in_progress=Count(
            "id",
            filter=Q(status__in=["data_collection", "analysis", "reporting"]),
        ),
        planning=Count("id", filter=Q(status__in=["planning", "preparation"])),
    )

    survey_cadence = [
        {
            "phase": "Quarterly Sampling Prep",
            "focus": "Refresh sampling frames and align targets per region/province.",
            "activities": [
                "Field coordinators validate population lists and update household masterlists.",
                "Agree on quotas and disaggregation with OOBC program leads.",
            ],
        },
        {
            "phase": "Rolling Deployment",
            "focus": "Execute monthly survey windows with rotating field teams.",
            "activities": [
                "Dispatch enumerators based on focal person rosters and logistical readiness.",
                "Log completions daily and sync devices to the central repository.",
            ],
        },
        {
            "phase": "Quality & Verification",
            "focus": "Maintain data integrity through routine spot checks and callbacks.",
            "activities": [
                "Supervisors review 10% samples, flag inconsistencies, and trigger re-visits.",
                "Use analytics dashboards to catch outliers and monitor non-response trends.",
            ],
        },
        {
            "phase": "Insights & Handover",
            "focus": "Translate findings into action points for regional teams.",
            "activities": [
                "Share monthly briefs with regional/provincial focal persons for immediate use.",
                "Feed consolidated indicators into OOBC planning, MEL, and reporting cycles.",
            ],
        },
    ]

    quick_actions = [
        {
            "title": "Full Survey Setup",
            "description": "Launch the full assessment wizard to configure detailed survey parameters.",
            "icon": "fas fa-clipboard-check",
            "url": f"{reverse('common:mana_new_assessment')}?primary_methodology=survey",
            "cta": "Launch Wizard",
            "icon_bg": "from-green-500 to-green-600",
            "cta_class": "text-green-600",
        },
        {
            "title": "Manage Survey Pipeline",
            "description": "Monitor active survey cycles and update statuses across regions.",
            "icon": "fas fa-stream",
            "url": f"{reverse('common:mana_manage_assessments')}?methodology=survey",
            "cta": "View Pipeline",
            "icon_bg": "from-blue-500 to-blue-600",
            "cta_class": "text-blue-600",
        },
        {
            "title": "Field Activity Log",
            "description": "Document daily enumerator updates and issues from the field.",
            "icon": "fas fa-clipboard",
            "url": reverse("common:mana_activity_log"),
            "cta": "Open Log",
            "icon_bg": "from-purple-500 to-purple-600",
            "cta_class": "text-purple-600",
        },
    ]

    data_safeguards = [
        "Secure informed consent scripts per language and keep signed forms with focal persons.",
        "Encrypt tablets, enforce strong credentials, and disable offline exports without approval.",
        "Schedule weekly integrity checks on synced datasets with version history retention.",
        "Document substitutions, callbacks, and escalations in the central tracker for auditability.",
    ]

    resource_needs = [
        "Updated sampling frames, listings, and GIS layers per region/province.",
        "Calibrated devices, spare batteries, and reimbursable transport allowances.",
        "Provincial focal person roster with contact matrix and escalation lines.",
        "Reference decks for indicator definitions, skip logic, and translation keys.",
    ]

    integration_notes = [
        "Compare rolling survey trends with desk review findings to refine outreach.",
        "Share flash reports with coordination teams for immediate policy responses.",
        "Cascade findings through regional forums to validate ground realities and commitments.",
        "Translate consolidated metrics into MEL baselines and dashboard refresh schedules.",
    ]

    coordination_notes = [
        "Assign field coordinators or focal persons per province to steward sampling and logistics.",
        "Use shared sampling templates so regions can align quotas and substitution rules.",
        "Hold monthly coordination huddles to rebalance workloads and address bottlenecks.",
        "Track enumerator capacity, training needs, and equipment status in the operations log.",
    ]

    context = {
        "core_principles": CORE_PRINCIPLES,
        "survey_stats": survey_stats,
        "survey_cadence": survey_cadence,
        "data_safeguards": data_safeguards,
        "resource_needs": resource_needs,
        "integration_notes": integration_notes,
        "survey_assessments": survey_assessments[:8],
        "quick_actions": quick_actions,
        "survey_quick_form": survey_form,
        "coordination_notes": coordination_notes,
    }
    return render(request, "mana/mana_survey.html", context)


@login_required
def mana_key_informant_interviews(request):
    """Key Informant Interview (KII) module with facilitation and documentation guides."""
    from django.db.models import Count, Q

    from mana.models import Assessment

    if request.method == "POST":
        kii_form = KIIQuickEntryForm(request.POST, user=request.user)
        if kii_form.is_valid():
            assessment = kii_form.save(user=request.user)
            messages.success(
                request,
                f'KII track "{assessment.title}" logged for {assessment.community}.',
            )
            return redirect("common:mana_kii")
        messages.error(request, "Please correct the highlighted errors below.")
    else:
        kii_form = KIIQuickEntryForm(user=request.user)

    kii_assessments = (
        Assessment.objects.filter(primary_methodology="kii")
        .select_related(
            "community__barangay__municipality__province__region",
            "category",
            "lead_assessor",
        )
        .order_by("-created_at")
    )

    kii_stats = kii_assessments.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="completed")),
        in_progress=Count(
            "id",
            filter=Q(status__in=["data_collection", "analysis", "reporting"]),
        ),
        planning=Count("id", filter=Q(status__in=["planning", "preparation"])),
    )

    quick_actions = [
        {
            "title": "Full KII Setup",
            "description": "Launch the full wizard to configure multi-phase KII engagements.",
            "icon": "fas fa-headset",
            "url": f"{reverse('common:mana_new_assessment')}?primary_methodology=kii",
            "cta": "Launch Wizard",
            "icon_bg": "from-rose-500 to-rose-600",
            "cta_class": "text-rose-600",
        },
        {
            "title": "Manage KII Pipeline",
            "description": "Review active KII engagements and update interview completion status.",
            "icon": "fas fa-stream",
            "url": f"{reverse('common:mana_manage_assessments')}?methodology=kii",
            "cta": "View Pipeline",
            "icon_bg": "from-blue-500 to-blue-600",
            "cta_class": "text-blue-600",
        },
        {
            "title": "Upload Narratives",
            "description": "Move straight to activity processing to store transcripts and lessons learned.",
            "icon": "fas fa-upload",
            "url": reverse("common:mana_activity_processing"),
            "cta": "Open Workspace",
            "icon_bg": "from-purple-500 to-purple-600",
            "cta_class": "text-purple-600",
        },
    ]

    informant_coordination = [
        "Maintain a shared roster of priority informants per sector and update availability notes after each outreach.",
        "Coordinate with regional focal persons to secure endorsements and introductions before scheduling.",
        "Package community briefers so informants receive context, objectives, and consent details ahead of interviews.",
        "Hold weekly huddles to align question bank adjustments with emerging policy needs.",
    ]

    workflow = [
        {
            "stage": "Preparation",
            "highlights": [
                "Profile key informants across governance, social, economic, cultural, and rights sectors.",
                "Customize interview guides, translation aids, and consent forms.",
                "Brief facilitators on power dynamics and culturally sensitive questioning.",
            ],
        },
        {
            "stage": "Facilitation",
            "highlights": [
                "Open with purpose, confidentiality assurances, and consent confirmation.",
                "Probe for narratives that contextualize survey trends and desk review findings.",
                "Manage time while allowing space for emergent issues and lived experiences.",
            ],
        },
        {
            "stage": "Synthesis",
            "highlights": [
                "Transcribe or summarize interviews promptly with secure storage of recordings.",
                "Capture direct quotes, illustrative cases, and action points per informant.",
                "Feed insights into thematic matrices and recommendation drafting.",
            ],
        },
    ]

    documentation_matrix = [
        {
            "title": "Metadata",
            "entries": [
                "Informant profile (role, organization, sector, location).",
                "Interview date, facilitators, note-takers, and language used.",
            ],
        },
        {
            "title": "Discussion Notes",
            "entries": [
                "Key points per thematic area with supporting evidence.",
                "Observed sentiments, alignment/divergence with other data sources.",
            ],
        },
        {
            "title": "Action Tracks",
            "entries": [
                "Immediate follow-ups, referrals, or issues requiring escalation.",
                "Potential policy or program triggers identified by informants.",
            ],
        },
    ]

    validation_threads = [
        "Cross-reference KII insights with survey and workshop results for triangulation.",
        "Engage technical experts for thematic validation of complex issues raised.",
        "Summarize converging/diverging narratives during synthesis and prioritization phases.",
        "Document how KII evidence influences final recommendations and MEL indicators.",
    ]

    safeguarding_notes = [
        "Obtain explicit consent for recording; offer anonymity where requested.",
        "Secure storage of transcripts and redact sensitive identifiers before sharing.",
        "Provide psychosocial or referral information if sensitive topics emerge.",
        "Coordinate with OOBC communications for responsible storytelling and advocacy use.",
    ]

    context = {
        "core_principles": CORE_PRINCIPLES,
        "kii_stats": kii_stats,
        "workflow": workflow,
        "documentation_matrix": documentation_matrix,
        "validation_threads": validation_threads,
        "safeguarding_notes": safeguarding_notes,
        "kii_assessments": kii_assessments[:8],
        "quick_actions": quick_actions,
        "informant_coordination": informant_coordination,
        "kii_quick_form": kii_form,
    }
    return render(request, "mana/mana_kii.html", context)


@login_required
def mana_playbook(request):
    """Comprehensive MANA playbook based on official guidelines."""

    dataset = _build_regional_dataset(request)

    # Reuse structured guidance from the regional flow definitions
    dav = {
        "phase": "Pre-MANA Preparation",
        "summary": "Establish clear objectives, coverage, resources, and risk mitigation steps before deployment.",
        "workstreams": [
            {
                "title": "Activity Management Plan",
                "details": "Define SMART objectives, geographic scope, timelines, budget, and risk mitigation strategies for the regional deployment.",
            },
            {
                "title": "Team Composition",
                "details": "Confirm core team roles (Team Leader, Facilitators, Documenters, Secretariat/logistics) and align expectations prior to travel.",
            },
            {
                "title": "Stakeholder Coordination",
                "details": "Secure endorsements from LGUs, coordinate courtesy calls, and enlist community leaders plus NGA partners for mobilization.",
            },
            {
                "title": "Logistics Blueprint",
                "details": "Finalize venue readiness, equipment, transportation, accommodations, and halal-compliant meals with contingency plans.",
            },
            {
                "title": "Participant Management",
                "details": "Ensure balanced representation across sectors, dispatch invitations, and prepare onboarding materials for delegates.",
            },
        ],
    }

    during = {
        "phase": "Field Implementation (5-Day Flow)",
        "summary": "Deliver structured workshops while keeping space for adaptive facilitation.",
        "workstreams": [
            {
                "title": "Day 1: Mobilization",
                "details": "Handle arrivals, registration, issuance of MANA kits, and evening team briefing ahead of plenary opening.",
            },
            {
                "title": "Day 2: Context Setting",
                "details": "Run opening rites, present OOBC mandates, deliver spatial overviews, and facilitate Workshop 1 on community context.",
            },
            {
                "title": "Day 3: Aspirations & Collaboration",
                "details": "Guide Workshops 2 and 3 to surface vision statements, priority sectors, and collaboration pathways with local actors.",
            },
            {
                "title": "Day 4: Feedback & Action Planning",
                "details": "Collect feedback on existing initiatives, analyse root causes, and craft ways forward culminating in closing program.",
            },
            {
                "title": "Daily Debriefs",
                "details": "Conduct end-of-day reflections to capture wins, address issues, and prime the team for succeeding sessions.",
            },
        ],
    }

    post = {
        "phase": "Post-MANA Integration",
        "summary": "Transform outputs into validated reports and actionable plans.",
        "workstreams": [
            {
                "title": "Data Processing",
                "details": "Encode, clean, and analyse quantitative and qualitative datasets, including geospatial layers.",
            },
            {
                "title": "Report Development",
                "details": "Draft the regional MANA report, convene validation workshops, and incorporate feedback prior to submission.",
            },
            {
                "title": "Dissemination",
                "details": "Prepare policy briefs, presentations, and community feedback sessions to socialize results.",
            },
            {
                "title": "Action Planning",
                "details": "Integrate priorities into OOBC and partner programming, budgeting, and advocacy pipelines.",
            },
            {
                "title": "MEL & Knowledge Capture",
                "details": "Evaluate the deployment, document lessons learned, and update playbooks for future cycles.",
            },
        ],
    }

    context = {
        "prep_checklist": ACTIVITY_PREP_CHECKLIST,
        "field_trackers": FIELD_ACTIVITY_TRACKERS,
        "post_activity_process": POST_ACTIVITY_PROCESS,
        "reporting_timeline": REPORTING_TIMELINE,
        "mel_practices": MEL_PRACTICES,
        "davao_activity_flow": [dav, during, post],
        "legal_basis": LEGAL_BASIS,
        "core_principles": CORE_PRINCIPLES,
        "mana_phases": MANA_PHASES,
        "methodology_breakdown": dataset["methodology_breakdown"],
        "region_cards": dataset["region_cards"],
        "recent_assessments": dataset["recent_assessments"],
        "reports_summary": dataset["reports_summary"],
    }
    return render(request, "mana/mana_playbook.html", context)


@login_required
def mana_activity_planner(request):
    """Planner for scheduling consultations and MANA activities."""

    planning_milestones = [
        {
            "title": "Define Objectives & Scope",
            "description": "Translate SMART objectives, geographic coverage, and thematic priorities into a deployable Activity Management Plan.",
        },
        {
            "title": "Secure Approvals",
            "description": "Confirm approvals from OOBC leadership and partner LGUs/BMOAs, including budget allocations and resource commitments.",
        },
        {
            "title": "Coordinate Stakeholders",
            "description": "Notify LGUs, community leaders, NGAs, NGOs, and vulnerable sector representatives at least two weeks ahead.",
        },
        {
            "title": "Finalize Logistics",
            "description": "Lock in venues, transport, accommodation, halal catering, and back-up arrangements for contingencies.",
        },
    ]

    risk_matrix = [
        {
            "risk": "Inclement weather and travel disruptions",
            "mitigation": "Identify alternate venues/routes, build buffer days, and coordinate with LGUs for advisories.",
        },
        {
            "risk": "Low participant turnout",
            "mitigation": "Mobilize community leaders early, provide transport support, and maintain contact lists for reminders.",
        },
        {
            "risk": "Security or health incidents",
            "mitigation": "Coordinate with local security/health units, prepare emergency kits, and brief teams on protocols.",
        },
    ]

    context = {
        "planning_milestones": planning_milestones,
        "prep_checklist": ACTIVITY_PREP_CHECKLIST,
        "risk_matrix": risk_matrix,
        "reporting_timeline": REPORTING_TIMELINE,
    }
    return render(request, "mana/mana_activity_planner.html", context)


@login_required
def mana_activity_log(request):
    """Daily logging hub for MANA field implementation."""

    documentation_prompts = [
        {
            "label": "Attendance & Representation",
            "details": "Record sectoral representation (women, youth, elders, PWD, LGU, NGA) and note gaps for follow-up.",
        },
        {
            "label": "Session Highlights",
            "details": "Capture key discussion points, agreements, emerging issues, and commitments per session.",
        },
        {
            "label": "Evidence Collected",
            "details": "Summarize surveys completed, KIIs conducted, maps produced, multimedia assets captured.",
        },
        {
            "label": "Operational Notes",
            "details": "Log logistics matters, risk incidents, accessibility adjustments, and resource utilization.",
        },
        {
            "label": "Immediate Actions",
            "details": "List action items, responsible persons, timelines, and escalation requirements.",
        },
    ]

    debrief_questions = [
        "What breakthroughs or community insights were gained today?",
        "Which priority issues require deeper validation tomorrow?",
        "Were vulnerable groups adequately heard? If not, what adjustments are needed?",
        "Do we need to adjust facilitation tools, language, or logistics based on feedback?",
        "What immediate communications or reports must be relayed to OOBC leadership?",
    ]

    context = {
        "field_trackers": FIELD_ACTIVITY_TRACKERS,
        "documentation_prompts": documentation_prompts,
        "debrief_questions": debrief_questions,
    }
    return render(request, "mana/mana_activity_log.html", context)


@login_required
def mana_activity_processing(request):
    """Post-activity processing workspace for reports, MEL, and dissemination."""

    data_products = [
        {
            "title": "Datasets & Repositories",
            "items": [
                "Cleaned survey datasets with metadata and data dictionaries.",
                "Consolidated workshop outputs (scanned/typed) with attribution.",
                "KII transcripts with consent markers and anonymization notes.",
            ],
        },
        {
            "title": "Analytical Outputs",
            "items": [
                "Priority issue matrix with urgency, feasibility, and impact scoring.",
                "Thematic dashboards (social, economic, cultural, rights) with spatial overlays.",
                "Stakeholder follow-through tracker summarizing commitments and status.",
            ],
        },
        {
            "title": "Dissemination Packages",
            "items": [
                "Executive summaries tailored for OOBC leadership and partners.",
                "Community feedback presentations and talking points in accessible language.",
                "Policy briefs highlighting key recommendations and resource needs.",
            ],
        },
    ]

    follow_through_actions = [
        "Schedule validation workshop with LGU/BMOA/community representatives to confirm findings.",
        "Set up monitoring milestones in MEL system for each priority recommendation.",
        "Coordinate with planning/budget units to integrate identified needs into programming.",
        "Log dissemination activities (briefings, forums, social media) with timelines and owners.",
        "Archive documentation and lessons learned for future MANA cycles and training modules.",
    ]

    context = {
        "post_activity_process": POST_ACTIVITY_PROCESS,
        "data_products": data_products,
        "follow_through_actions": follow_through_actions,
        "mel_practices": MEL_PRACTICES,
    }
    return render(request, "mana/mana_activity_processing.html", context)


@login_required
@moa_no_access
def mana_geographic_data(request):
    """MANA geographic data and mapping page with location-aware filters (blocked for MOA users)."""
    from django.db.models import Count

    from communities.models import GeographicDataLayer, MapVisualization, OBCCommunity

    def parse_identifier(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    region_id = parse_identifier(request.GET.get("region"))
    province_id = parse_identifier(request.GET.get("province"))
    municipality_id = parse_identifier(request.GET.get("municipality"))
    barangay_id = parse_identifier(request.GET.get("barangay"))

    selected_region = (
        Region.objects.filter(pk=region_id, is_active=True).first()
        if region_id
        else None
    )

    selected_province = None
    if province_id:
        selected_province = (
            Province.objects.filter(pk=province_id, is_active=True)
            .select_related("region")
            .first()
        )
        if not selected_province:
            province_id = None
        else:
            region_id = selected_province.region_id
            if not selected_region or selected_region.pk != region_id:
                selected_region = selected_province.region

    selected_municipality = None
    if municipality_id:
        selected_municipality = (
            Municipality.objects.filter(pk=municipality_id, is_active=True)
            .select_related("province__region")
            .first()
        )
        if not selected_municipality:
            municipality_id = None
        else:
            province_id = selected_municipality.province_id
            selected_province = selected_municipality.province
            region_id = selected_province.region_id
            selected_region = selected_province.region

    selected_barangay = None
    if barangay_id:
        selected_barangay = (
            Barangay.objects.filter(pk=barangay_id, is_active=True)
            .select_related("municipality__province__region")
            .first()
        )
        if not selected_barangay:
            barangay_id = None
        else:
            municipality_id = selected_barangay.municipality_id
            selected_municipality = selected_barangay.municipality
            province_id = selected_municipality.province_id
            selected_province = selected_municipality.province
            region_id = selected_province.region_id
            selected_region = selected_province.region

    layer_filters = {}
    visualization_filters = {}
    community_filters = {}

    if barangay_id:
        layer_filters["community__barangay_id"] = barangay_id
        visualization_filters["community__barangay_id"] = barangay_id
        community_filters["barangay_id"] = barangay_id
    elif municipality_id:
        layer_filters["community__barangay__municipality_id"] = municipality_id
        visualization_filters["community__barangay__municipality_id"] = municipality_id
        community_filters["barangay__municipality_id"] = municipality_id
    elif province_id:
        layer_filters["community__barangay__municipality__province_id"] = province_id
        visualization_filters["community__barangay__municipality__province_id"] = (
            province_id
        )
        community_filters["barangay__municipality__province_id"] = province_id
    elif region_id:
        layer_filters["community__barangay__municipality__province__region_id"] = (
            region_id
        )
        visualization_filters[
            "community__barangay__municipality__province__region_id"
        ] = region_id
        community_filters["barangay__municipality__province__region_id"] = region_id

    data_layers_qs = GeographicDataLayer.objects.all().order_by("name")
    if layer_filters:
        data_layers_qs = data_layers_qs.filter(**layer_filters)

    visualizations_qs = MapVisualization.objects.select_related("community").order_by(
        "-created_at"
    )
    if visualization_filters:
        visualizations_qs = visualizations_qs.filter(**visualization_filters)

    communities_qs = (
        OBCCommunity.objects.annotate(
            visualizations_count=Count("community_map_visualizations")
        )
        .filter(visualizations_count__gt=0)
        .order_by("barangay__name")
    )
    if community_filters:
        communities_qs = communities_qs.filter(**community_filters)

    map_layers, map_config = serialize_layers_for_map(data_layers_qs)

    stats = {
        "total_layers": data_layers_qs.count(),
        "total_visualizations": visualizations_qs.count(),
        "communities_mapped": communities_qs.count(),
        "active_layers": (
            data_layers_qs.filter(is_active=True).count()
            if hasattr(GeographicDataLayer, "is_active")
            else data_layers_qs.count()
        ),
    }

    # Limit visualizations display but keep counts accurate.
    visualizations = visualizations_qs[:10]

    filter_summary_parts = []
    if selected_barangay:
        filter_summary_parts.append(
            f"Barangay {selected_barangay.name}, {selected_municipality.name}"
        )
    elif selected_municipality:
        filter_summary_parts.append(
            f"{selected_municipality.name}, {selected_province.name}"
        )
    elif selected_province:
        filter_summary_parts.append(f"Province {selected_province.name}")
    elif selected_region:
        filter_summary_parts.append(
            f"Region {selected_region.code} - {selected_region.name}"
        )

    context = {
        "data_layers": data_layers_qs,
        "visualizations": visualizations,
        "communities": communities_qs,
        "stats": stats,
        "location_data": build_location_data(),
        "current_region": str(region_id or ""),
        "current_province": str(province_id or ""),
        "current_municipality": str(municipality_id or ""),
        "current_barangay": str(barangay_id or ""),
        "selected_region": selected_region,
        "selected_province": selected_province,
        "selected_municipality": selected_municipality,
        "selected_barangay": selected_barangay,
        "filter_summary": ", ".join(filter_summary_parts),
        "filters_applied": any(
            identifier
            for identifier in [region_id, province_id, municipality_id, barangay_id]
        ),
        "map_layers": map_layers,
        "map_config": map_config,
    }
    return render(request, "mana/mana_geographic_data.html", context)


__all__ = [
    "mana_home",
    "mana_new_assessment",
    "mana_manage_assessments",
    "mana_geographic_data",
]
