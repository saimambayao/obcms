"""
Policies Query Templates for OBCMS Chat System

45+ template variations for querying Policy Recommendation data including:
- Count queries (total policies, filtered counts)
- List queries (show policies, filter by attributes)
- Evidence-based queries (policies with evidence, supporting data, impact evidence)
- Implementation tracking (policy status, progress, outcomes)
- Legislative linkage (policies to legislation, pending legislation)
- Stakeholder queries (policy stakeholders, consultation records)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# HELPER FUNCTIONS FOR QUERY GENERATION
# =============================================================================

def build_status_filter_clause(status: str) -> str:
    """Build status filter clause for policies."""
    status_map = {
        'active': 'status__in=["draft", "under_review", "approved"]',
        'draft': 'status="draft"',
        'under review': 'status="under_review"',
        'approved': 'status="approved"',
        'implemented': 'status="implemented"',
        'submitted': 'status="submitted"',
        'pending': 'status__in=["draft", "under_review"]'
    }
    return status_map.get(status.lower(), f'status__icontains="{status}"')


# =============================================================================
# COUNT QUERY TEMPLATES (10 templates)
# =============================================================================

POLICIES_COUNT_TEMPLATES = [
    QueryTemplate(
        id='count_total_policies',
        category='policies',
        pattern=r'\b(how many|total|count|number of)\s+(all\s+)?(policy|policies|policy recommendations?)\b',
        query_template='PolicyRecommendation.objects.count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many policies are there?',
            'Total policies',
            'Count all policy recommendations',
            'Number of policies',
            'How many policy recommendations?'
        ],
        priority=7,
        description='Count total policy recommendations',
        tags=['count', 'policies', 'total']
    ),
    QueryTemplate(
        id='count_policies_by_status',
        category='policies',
        pattern=r'\b(((how many|count|total)\s+)?(?P<status>draft|approved|implemented|submitted|active|pending)\s+(policies?|policy recommendations?)|(policies?|policy recommendations?)\s+(?P<status2>under review))\b',
        query_template='PolicyRecommendation.objects.filter({status_filter}).count()',
        required_entities=['status'],
        optional_entities=[],
        examples=[
            'How many approved policies?',
            'Count draft policies',
            'Total implemented policies',
            'Policies under review'
        ],
        priority=9,
        description='Count policies by status',
        tags=['count', 'policies', 'status']
    ),
    QueryTemplate(
        id='count_policies_by_sector',
        category='policies',
        pattern=r'\b(how many|count|total)\s+(policies?|policy recommendations?)\s+(in|for)\s+(?P<sector>[\w\s]+?)(\s+sector)?(\?|$)',
        query_template='PolicyRecommendation.objects.filter(category__icontains="{sector}").count()',
        required_entities=['sector'],
        optional_entities=[],
        examples=[
            'How many policies in education sector?',
            'Count policies for health',
            'Total policies in infrastructure sector'
        ],
        priority=8,
        description='Count policies by sector',
        tags=['count', 'policies', 'sector']
    ),
    QueryTemplate(
        id='count_policies_by_priority',
        category='policies',
        pattern=r'\b((how many|count|total)\s+)?(?P<priority>high|critical|urgent|medium|low)\s+(priority\s+)?(policies?|policy recommendations?)\b',
        query_template='PolicyRecommendation.objects.filter(priority__icontains="{priority}").count()',
        required_entities=['priority'],
        optional_entities=[],
        examples=[
            'How many high priority policies?',
            'Count critical priority policies',
            'Total urgent policies'
        ],
        priority=8,
        description='Count policies by priority level',
        tags=['count', 'policies', 'priority']
    ),
    QueryTemplate(
        id='count_policies_by_scope',
        category='policies',
        pattern=r'\b(how many|count|total)\s+(?P<scope>national|regional|provincial|municipal)\s+(level\s+)?(policies?|policy recommendations?)',
        query_template='PolicyRecommendation.objects.filter(scope__icontains="{scope}").count()',
        required_entities=['scope'],
        optional_entities=[],
        examples=[
            'How many national level policies?',
            'Count regional policies',
            'Total provincial policies'
        ],
        priority=8,
        description='Count policies by geographic scope',
        tags=['count', 'policies', 'scope']
    ),
    QueryTemplate(
        id='count_policies_with_evidence',
        category='policies',
        pattern=r'\b(how many|count|total)\s+(policies?|policy recommendations?)\s+with\s+(evidence|supporting data|documentation)',
        query_template='PolicyRecommendation.objects.filter(evidence_base__isnull=False).exclude(evidence_base="").count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many policies with evidence?',
            'Count policies with supporting data',
            'Total policies with documentation'
        ],
        priority=8,
        description='Count policies with evidence base',
        tags=['count', 'policies', 'evidence']
    ),
    QueryTemplate(
        id='count_policies_pending_legislation',
        category='policies',
        pattern=r'\b(how many|count|total)\s+(policies?|policy recommendations?)\s+(pending|awaiting|submitted for)\s+(legislation|approval)',
        query_template='PolicyRecommendation.objects.filter(status__in=["submitted", "under_review"]).count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many policies pending legislation?',
            'Count policies awaiting approval',
            'Total policies submitted for legislation'
        ],
        priority=8,
        description='Count policies pending legislation',
        tags=['count', 'policies', 'legislation', 'pending']
    ),
    QueryTemplate(
        id='count_policies_with_stakeholders',
        category='policies',
        pattern=r'\b(how many|count|total)\s+(policies?|policy recommendations?)\s+with\s+(stakeholder|consultation|engagement)',
        query_template='PolicyRecommendation.objects.filter(stakeholders__isnull=False).distinct().count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many policies with stakeholder engagement?',
            'Count policies with consultation',
            'Total policies with stakeholders'
        ],
        priority=7,
        description='Count policies with stakeholder involvement',
        tags=['count', 'policies', 'stakeholders']
    ),
    QueryTemplate(
        id='count_policies_by_type',
        category='policies',
        pattern=r'\b(how many|count|total)\s+(?P<type>policy|program|service)\s+(recommendations?|initiatives?)',
        query_template='PolicyRecommendation.objects.filter(recommendation_type__icontains="{type}").count()',
        required_entities=['type'],
        optional_entities=[],
        examples=[
            'How many policy recommendations?',
            'Count program initiatives',
            'Total service recommendations'
        ],
        priority=7,
        description='Count by recommendation type',
        tags=['count', 'policies', 'type']
    ),
    QueryTemplate(
        id='count_policies_recent',
        category='policies',
        pattern=r'\b(how many|count|total)\s+(recent|new|latest)\s+(policies?|policy recommendations?)',
        query_template='PolicyRecommendation.objects.filter(created_at__gte=timezone.now() - timedelta(days=90)).count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many recent policies?',
            'Count new policy recommendations',
            'Total latest policies'
        ],
        priority=7,
        description='Count recently created policies (last 90 days)',
        tags=['count', 'policies', 'recent']
    ),
]


# =============================================================================
# LIST QUERY TEMPLATES (12 templates)
# =============================================================================

POLICIES_LIST_TEMPLATES = [
    QueryTemplate(
        id='list_all_policies',
        category='policies',
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(all\s+)?(policies?|policy recommendations?)\b',
        query_template='PolicyRecommendation.objects.all().select_related("created_by").order_by("-created_at")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me policies',
            'List all policy recommendations',
            'Display policies',
            'Get all policies'
        ],
        priority=6,
        description='List all policy recommendations',
        tags=['list', 'policies']
    ),
    QueryTemplate(
        id='list_policies_by_status',
        category='policies',
        pattern=r'\b(((show|list|display)\s+(me\s+)?)?(?P<status>draft|approved|implemented|submitted|active|pending)\s+(policies?|policy recommendations?)|(policies?|policy recommendations?)\s+(?P<status2>under review))\b',
        query_template='PolicyRecommendation.objects.filter({status_filter}).select_related("created_by").order_by("-created_at")[:30]',
        required_entities=['status'],
        optional_entities=[],
        examples=[
            'Show me approved policies',
            'List draft policies',
            'Display implemented policies',
            'Policies under review'
        ],
        priority=8,
        description='List policies by status',
        tags=['list', 'policies', 'status']
    ),
    QueryTemplate(
        id='list_policies_by_sector',
        category='policies',
        pattern=r'\b(show|list|display)\s+(me\s+)?(?P<sector>[\w]+)\s+(policies?|policy recommendations?)|(show|list|display)\s+(me\s+)?(policies?|policy recommendations?)\s+(in|for)\s+(?P<sector2>[\w\s]+?)(\s+sector)?(\?|$)',
        query_template='PolicyRecommendation.objects.filter(category__icontains="{sector}").select_related("created_by").order_by("-priority", "-created_at")[:30]',
        required_entities=['sector'],
        optional_entities=[],
        examples=[
            'Show me policies in education sector',
            'List policies for health',
            'Display infrastructure policies'
        ],
        priority=8,
        description='List policies by sector',
        tags=['list', 'policies', 'sector']
    ),
    QueryTemplate(
        id='list_policies_by_priority',
        category='policies',
        pattern=r'\b(show|list|display)\s+(me\s+)?(?P<priority>high|critical|urgent|medium|low)\s+priority\s+(policies?|policy recommendations?)',
        query_template='PolicyRecommendation.objects.filter(priority__icontains="{priority}").select_related("created_by").order_by("-created_at")[:30]',
        required_entities=['priority'],
        optional_entities=[],
        examples=[
            'Show me high priority policies',
            'List critical priority policies',
            'Display urgent policies'
        ],
        priority=8,
        description='List policies by priority level',
        tags=['list', 'policies', 'priority']
    ),
    QueryTemplate(
        id='list_recent_policies',
        category='policies',
        pattern=r'\b(recent|latest|new|newly added)\s+(policies?|policy recommendations?)\b',
        query_template='PolicyRecommendation.objects.all().select_related("created_by").order_by("-created_at")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Recent policies',
            'Latest policy recommendations',
            'Newly added policies',
            'Show recent policies'
        ],
        priority=7,
        description='List recently added policies',
        tags=['list', 'policies', 'recent']
    ),
    QueryTemplate(
        id='list_policies_with_evidence',
        category='policies',
        pattern=r'\b(show|list|display)\s+(me\s+)?(policies?|policy recommendations?)\s+with\s+(evidence|supporting data|documentation)',
        query_template='PolicyRecommendation.objects.filter(evidence_base__isnull=False).exclude(evidence_base="").select_related("created_by").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me policies with evidence',
            'List policies with supporting data',
            'Display policies with documentation'
        ],
        priority=8,
        description='List policies with evidence base',
        tags=['list', 'policies', 'evidence']
    ),
    QueryTemplate(
        id='list_policies_by_scope',
        category='policies',
        pattern=r'\b(show|list|display)\s+(me\s+)?(?P<scope>national|regional|provincial|municipal)\s+(level\s+)?(policies?|policy recommendations?)',
        query_template='PolicyRecommendation.objects.filter(scope__icontains="{scope}").select_related("created_by").order_by("-priority")[:30]',
        required_entities=['scope'],
        optional_entities=[],
        examples=[
            'Show me national level policies',
            'List regional policies',
            'Display provincial policies'
        ],
        priority=8,
        description='List policies by geographic scope',
        tags=['list', 'policies', 'scope']
    ),
    QueryTemplate(
        id='search_policies_keyword',
        category='policies',
        pattern=r'\b(search|find)\s+(for\s+)?(policies?|policy recommendations?)\s+(about|on|related to)\s+(?P<keyword>[\w\s]+)',
        query_template='PolicyRecommendation.objects.filter(Q(title__icontains="{keyword}") | Q(description__icontains="{keyword}")).select_related("created_by").order_by("-priority", "-created_at")[:20]',
        required_entities=['keyword'],
        optional_entities=[],
        examples=[
            'Search for policies about education',
            'Find policies on livelihood',
            'Search policy recommendations related to health'
        ],
        priority=8,
        description='Search policies by keyword',
        tags=['search', 'policies', 'keyword']
    ),
    QueryTemplate(
        id='list_policies_pending_legislation',
        category='policies',
        pattern=r'\b(show|list|display)\s+(me\s+)?(policies?|policy recommendations?)\s+(pending|awaiting|submitted for)\s+(legislation|approval)',
        query_template='PolicyRecommendation.objects.filter(status__in=["submitted", "under_review"]).select_related("created_by").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me policies pending legislation',
            'List policies awaiting approval',
            'Display policies submitted for legislation'
        ],
        priority=8,
        description='List policies pending legislation',
        tags=['list', 'policies', 'legislation', 'pending']
    ),
    QueryTemplate(
        id='list_policies_with_stakeholders',
        category='policies',
        pattern=r'\b(show|list|display)\s+(me\s+)?(policies?|policy recommendations?)\s+with\s+(stakeholder|consultation)',
        query_template='PolicyRecommendation.objects.filter(stakeholders__isnull=False).distinct().prefetch_related("stakeholders").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me policies with stakeholder engagement',
            'List policies with consultation',
            'Display policies with stakeholders'
        ],
        priority=7,
        description='List policies with stakeholder involvement',
        tags=['list', 'policies', 'stakeholders']
    ),
    QueryTemplate(
        id='list_policies_by_author',
        category='policies',
        pattern=r'\b(show|list|display)\s+(me\s+)?(policies?|policy recommendations?)\s+(by|created by|from)\s+(?P<author>[\w\s]+)',
        query_template='PolicyRecommendation.objects.filter(created_by__username__icontains="{author}").select_related("created_by").order_by("-created_at")[:30]',
        required_entities=['author'],
        optional_entities=[],
        examples=[
            'Show me policies by John Doe',
            'List policies created by admin',
            'Display policy recommendations from staff'
        ],
        priority=7,
        description='List policies by author',
        tags=['list', 'policies', 'author']
    ),
    QueryTemplate(
        id='list_top_priority_policies',
        category='policies',
        pattern=r'\b(top|highest)\s+priority\s+(policies?|policy recommendations?)',
        query_template='PolicyRecommendation.objects.filter(priority__in=["high", "critical", "urgent"]).select_related("created_by").order_by("-created_at")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Top priority policies',
            'Highest priority policy recommendations',
            'Show me top priority policies'
        ],
        priority=7,
        description='List top priority policies',
        tags=['list', 'policies', 'priority', 'top']
    ),
]


# =============================================================================
# EVIDENCE-BASED QUERY TEMPLATES (8 templates)
# =============================================================================

POLICIES_EVIDENCE_TEMPLATES = [
    QueryTemplate(
        id='policies_with_impact_evidence',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+with\s+(impact|outcome)\s+(evidence|data|results)',
        query_template='PolicyRecommendation.objects.filter(impact_indicators__isnull=False).exclude(impact_indicators="").select_related("created_by").order_by("-priority")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies with impact evidence',
            'Policy recommendations with outcome data',
            'Policies with impact results'
        ],
        priority=8,
        description='Policies with impact evidence',
        tags=['policies', 'evidence', 'impact']
    ),
    QueryTemplate(
        id='policies_evidence_based',
        category='policies',
        pattern=r'\bevidence.?based\s+(policies?|policy recommendations?)',
        query_template='PolicyRecommendation.objects.filter(evidence_base__isnull=False).exclude(evidence_base="").select_related("created_by").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Evidence-based policies',
            'Evidence based policy recommendations',
            'Show me evidence-based policies'
        ],
        priority=8,
        description='Evidence-based policy recommendations',
        tags=['policies', 'evidence', 'based']
    ),
    QueryTemplate(
        id='policies_supporting_data',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+with\s+(supporting|baseline|research)\s+(data|evidence|documentation)',
        query_template='PolicyRecommendation.objects.filter(Q(evidence_base__isnull=False) | Q(supporting_documents__isnull=False)).distinct().select_related("created_by").order_by("-priority")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies with supporting data',
            'Policy recommendations with baseline evidence',
            'Policies with research documentation'
        ],
        priority=7,
        description='Policies with supporting data',
        tags=['policies', 'evidence', 'data']
    ),
    QueryTemplate(
        id='policies_assessment_based',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+(based on|from|derived from)\s+(assessments?|needs? analysis)',
        query_template='PolicyRecommendation.objects.filter(related_needs__isnull=False).distinct().prefetch_related("related_needs__assessment").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies based on assessments',
            'Policy recommendations from needs analysis',
            'Policies derived from assessments'
        ],
        priority=8,
        description='Policies based on assessments',
        tags=['policies', 'assessment', 'needs']
    ),
    QueryTemplate(
        id='policies_without_evidence',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+(without|lacking|missing)\s+(evidence|supporting data|documentation)',
        query_template='PolicyRecommendation.objects.filter(Q(evidence_base__isnull=True) | Q(evidence_base="")).select_related("created_by").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies without evidence',
            'Policy recommendations lacking supporting data',
            'Policies missing documentation'
        ],
        priority=7,
        description='Policies without evidence base',
        tags=['policies', 'evidence', 'gap']
    ),
    QueryTemplate(
        id='policies_evidence_quality',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+(evidence|data)\s+(quality|strength|completeness)',
        query_template='PolicyRecommendation.objects.annotate(has_evidence=Case(When(evidence_base__isnull=False, then=1), default=0), has_impact=Case(When(impact_indicators__isnull=False, then=1), default=0), evidence_score=F("has_evidence") + F("has_impact")).order_by("-evidence_score", "-priority")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies by evidence quality',
            'Policy recommendations data strength',
            'Policies evidence completeness'
        ],
        priority=7,
        description='Policies ranked by evidence quality',
        tags=['policies', 'evidence', 'quality']
    ),
    QueryTemplate(
        id='policies_impact_assessment',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+with\s+(impact|outcome)\s+(assessment|evaluation|measurement)',
        query_template='PolicyRecommendation.objects.filter(impact_indicators__isnull=False).exclude(impact_indicators="").select_related("created_by").order_by("-priority")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies with impact assessment',
            'Policy recommendations with outcome evaluation',
            'Policies with impact measurement'
        ],
        priority=7,
        description='Policies with impact assessment',
        tags=['policies', 'impact', 'assessment']
    ),
    QueryTemplate(
        id='policies_research_backed',
        category='policies',
        pattern=r'\bresearch.?backed\s+(policies?|policy recommendations?)',
        query_template='PolicyRecommendation.objects.filter(evidence_base__icontains="research").select_related("created_by").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Research-backed policies',
            'Research backed policy recommendations',
            'Show me research-backed policies'
        ],
        priority=7,
        description='Research-backed policy recommendations',
        tags=['policies', 'research', 'evidence']
    ),
]


# =============================================================================
# IMPLEMENTATION TRACKING TEMPLATES (8 templates)
# =============================================================================

POLICIES_IMPLEMENTATION_TEMPLATES = [
    QueryTemplate(
        id='policy_implementation_status',
        category='policies',
        pattern=r'\b(policy|policies?)\s+(implementation|progress)\s+(status|tracking)',
        query_template='PolicyRecommendation.objects.values("status").annotate(count=Count("id")).order_by("-count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policy implementation status',
            'Policies progress tracking',
            'Show me policy implementation status'
        ],
        priority=8,
        description='Policy implementation status overview',
        tags=['policies', 'implementation', 'status']
    ),
    QueryTemplate(
        id='policy_implementation_rate',
        category='policies',
        pattern=r'\b(policy|policies?)\s+(implementation|completion)\s+(rate|percentage)',
        query_template='PolicyRecommendation.objects.aggregate(total=Count("id"), implemented=Count("id", filter=Q(status="implemented")), rate=100.0 * Count("id", filter=Q(status="implemented")) / Count("id"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policy implementation rate',
            'Policies completion percentage',
            'What is the policy implementation rate?'
        ],
        priority=8,
        description='Policy implementation rate',
        tags=['policies', 'implementation', 'rate']
    ),
    QueryTemplate(
        id='policies_implementation_progress',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+(in|under|being)\s+(implementation|progress|implemented)',
        query_template='PolicyRecommendation.objects.filter(status__in=["approved", "under_implementation"]).select_related("created_by").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies in implementation',
            'Policy recommendations under progress',
            'Show me policies being implemented'
        ],
        priority=8,
        description='Policies currently in implementation',
        tags=['policies', 'implementation', 'progress']
    ),
    QueryTemplate(
        id='policies_fully_implemented',
        category='policies',
        pattern=r'\b(fully\s+)?(implemented|completed)\s+(policies?|policy recommendations?)',
        query_template='PolicyRecommendation.objects.filter(status="implemented").select_related("created_by").order_by("-implementation_date")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Fully implemented policies',
            'Completed policy recommendations',
            'Show me implemented policies'
        ],
        priority=8,
        description='Fully implemented policies',
        tags=['policies', 'implemented', 'completed']
    ),
    QueryTemplate(
        id='policies_implementation_gaps',
        category='policies',
        pattern=r'\b(policy|policies?)\s+(implementation|execution)\s+(gaps?|challenges?|barriers?)',
        query_template='PolicyRecommendation.objects.filter(status__in=["approved", "under_review"]).exclude(implementation_challenges__isnull=True).select_related("created_by").order_by("-priority")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policy implementation gaps',
            'Policies implementation challenges',
            'Policy execution barriers'
        ],
        priority=7,
        description='Policies with implementation gaps',
        tags=['policies', 'implementation', 'gaps']
    ),
    QueryTemplate(
        id='policies_implementation_timeline',
        category='policies',
        pattern=r'\b(policy|policies?)\s+(implementation|rollout)\s+(timeline|schedule|timeframe)',
        query_template='PolicyRecommendation.objects.filter(status__in=["approved", "under_implementation"]).exclude(target_implementation_date__isnull=True).select_related("created_by").order_by("target_implementation_date")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policy implementation timeline',
            'Policies rollout schedule',
            'Policy implementation timeframe'
        ],
        priority=7,
        description='Policy implementation timeline',
        tags=['policies', 'implementation', 'timeline']
    ),
    QueryTemplate(
        id='policies_overdue_implementation',
        category='policies',
        pattern=r'\b(overdue|delayed|past due)\s+(policy|policies?|policy\s+implementation)?',
        query_template='PolicyRecommendation.objects.filter(status__in=["approved", "under_implementation"], target_implementation_date__lt=timezone.now().date()).select_related("created_by").order_by("target_implementation_date")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Overdue policy implementation',
            'Delayed policies',
            'Past due policy implementation'
        ],
        priority=8,
        description='Policies with overdue implementation',
        tags=['policies', 'implementation', 'overdue']
    ),
    QueryTemplate(
        id='policies_implementation_success',
        category='policies',
        pattern=r'\b(successful|effective|high.?impact)\s+(policy|policies?)\s+(implementation)?',
        query_template='PolicyRecommendation.objects.filter(status="implemented", impact_indicators__isnull=False).exclude(impact_indicators="").select_related("created_by").order_by("-implementation_date")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Successful policy implementation',
            'Effective policies',
            'High-impact policy implementation'
        ],
        priority=7,
        description='Successfully implemented policies',
        tags=['policies', 'implementation', 'success']
    ),
]


# =============================================================================
# STAKEHOLDER QUERY TEMPLATES (7 templates)
# =============================================================================

POLICIES_STAKEHOLDER_TEMPLATES = [
    QueryTemplate(
        id='policies_by_stakeholder',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+(involving|with|from)\s+(?P<stakeholder>[\w\s]+?)(\s+stakeholder)?(\?|$)',
        query_template='PolicyRecommendation.objects.filter(stakeholders__name__icontains="{stakeholder}").distinct().prefetch_related("stakeholders").order_by("-priority", "-created_at")[:30]',
        required_entities=['stakeholder'],
        optional_entities=[],
        examples=[
            'Policies involving MOA stakeholder',
            'Policy recommendations with OOBC',
            'Policies from community stakeholders'
        ],
        priority=7,
        description='Policies by stakeholder',
        tags=['policies', 'stakeholders']
    ),
    QueryTemplate(
        id='policies_consultation_records',
        category='policies',
        pattern=r'\b(policy|policies?)\s+(consultation|engagement)\s+(records?|history|summary)',
        query_template='PolicyRecommendation.objects.filter(consultation_records__isnull=False).exclude(consultation_records="").select_related("created_by").order_by("-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policy consultation records',
            'Policies engagement history',
            'Policy consultation summary'
        ],
        priority=7,
        description='Policies with consultation records',
        tags=['policies', 'consultation', 'stakeholders']
    ),
    QueryTemplate(
        id='policies_multi_stakeholder',
        category='policies',
        pattern=r'\b((multi.?stakeholder|collaborative)\s+(policies?|policy recommendations?)|(policies?|policy recommendations?)\s+with\s+multiple\s+stakeholders)',
        query_template='PolicyRecommendation.objects.annotate(stakeholder_count=Count("stakeholders")).filter(stakeholder_count__gte=3).prefetch_related("stakeholders").order_by("-stakeholder_count", "-priority")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Multi-stakeholder policies',
            'Collaborative policy recommendations',
            'Policies with multiple stakeholders'
        ],
        priority=7,
        description='Multi-stakeholder policy recommendations',
        tags=['policies', 'stakeholders', 'collaborative']
    ),
    QueryTemplate(
        id='policies_stakeholder_feedback',
        category='policies',
        pattern=r'\b((policy|policies?)\s+(stakeholder|community)\s+(feedback|input|comments)|(policies?|policy recommendations?)\s+with\s+(stakeholder|community)\s+(feedback|input|comments))',
        query_template='PolicyRecommendation.objects.filter(stakeholder_feedback__isnull=False).exclude(stakeholder_feedback="").select_related("created_by").order_by("-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policy stakeholder feedback',
            'Policies with community input',
            'Policy stakeholder comments'
        ],
        priority=7,
        description='Policies with stakeholder feedback',
        tags=['policies', 'stakeholders', 'feedback']
    ),
    QueryTemplate(
        id='policies_public_consultation',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+with\s+(public|community)\s+(consultation|participation)',
        query_template='PolicyRecommendation.objects.filter(public_consultation=True).select_related("created_by").order_by("-consultation_date", "-priority")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies with public consultation',
            'Policy recommendations with community participation',
            'Policies with public input'
        ],
        priority=7,
        description='Policies with public consultation',
        tags=['policies', 'consultation', 'public']
    ),
    QueryTemplate(
        id='policies_stakeholder_count',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+by\s+(stakeholder|partner)\s+(count|number)',
        query_template='PolicyRecommendation.objects.annotate(stakeholder_count=Count("stakeholders")).filter(stakeholder_count__gt=0).order_by("-stakeholder_count")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies by stakeholder count',
            'Policy recommendations by partner number',
            'Policies ranked by stakeholders'
        ],
        priority=6,
        description='Policies ranked by stakeholder count',
        tags=['policies', 'stakeholders', 'count']
    ),
    QueryTemplate(
        id='policies_without_stakeholders',
        category='policies',
        pattern=r'\b(policies?|policy recommendations?)\s+(without|lacking|missing)\s+(stakeholder|consultation)',
        query_template='PolicyRecommendation.objects.filter(stakeholders__isnull=True).select_related("created_by").order_by("-priority", "-created_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies without stakeholder engagement',
            'Policy recommendations lacking consultation',
            'Policies missing stakeholders'
        ],
        priority=7,
        description='Policies without stakeholder involvement',
        tags=['policies', 'stakeholders', 'gap']
    ),
]


# =============================================================================
# COMBINE ALL TEMPLATES
# =============================================================================

POLICIES_TEMPLATES = (
    POLICIES_COUNT_TEMPLATES +
    POLICIES_LIST_TEMPLATES +
    POLICIES_EVIDENCE_TEMPLATES +
    POLICIES_IMPLEMENTATION_TEMPLATES +
    POLICIES_STAKEHOLDER_TEMPLATES
)

# Total: 10 + 12 + 8 + 8 + 7 = 45 distinct templates with 130+ example query variations
# Original: 25 templates | Added: 20 templates | New Total: 45 templates
