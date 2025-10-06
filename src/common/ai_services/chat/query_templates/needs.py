"""
Needs Query Templates for OBCMS Chat System

Critical templates for querying community needs identified through assessments.
Enables evidence-based budgeting pipeline: Assessments → Needs → Policies → PPAs → Budget

Covers:
- Basic needs queries (count, filter by sector/priority/location/status)
- Needs analysis (unmet needs, top priorities, by assessment/community)
- Cross-domain queries (needs with/without PPAs, gap analysis)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# HELPER FUNCTIONS FOR QUERY GENERATION
# =============================================================================

def build_sector_filter_clause(sector: str) -> str:
    """Build sector filter clause using NeedsCategory relationship."""
    return f'category__sector__icontains="{sector}"'


def build_priority_filter_clause(priority: str) -> str:
    """Build priority filter using urgency_level and impact_severity."""
    # Map common priority terms to urgency_level
    priority_map = {
        'critical': 'immediate',
        'high': 'short_term',
        'medium': 'medium_term',
        'low': 'long_term'
    }
    urgency = priority_map.get(priority.lower(), priority)
    return f'urgency_level="{urgency}"'


def build_status_filter_clause(status: str) -> str:
    """Build status filter clause."""
    # Map common status terms to Need status choices
    status_map = {
        'unmet': 'identified',
        'unfulfilled': 'identified',
        'met': 'completed',
        'fulfilled': 'completed',
        'partially_met': 'in_progress',
        'ongoing': 'in_progress',
        'planned': 'planned'
    }
    need_status = status_map.get(status.lower(), status)
    return f'status="{need_status}"'


def build_location_filter_clause(location_data: Dict[str, Any], base_field: str = "community__barangay__municipality__province__region") -> str:
    """Build location filter clause based on extracted location entity."""
    loc_type = location_data.get('type', 'region')
    loc_value = location_data.get('value', '')

    if loc_type == 'region':
        return f"{base_field}__name__icontains='{loc_value}'"
    elif loc_type == 'province':
        return f"community__barangay__municipality__province__name__icontains='{loc_value}'"
    elif loc_type == 'municipality':
        return f"community__barangay__municipality__name__icontains='{loc_value}'"
    elif loc_type == 'barangay':
        return f"community__barangay__name__icontains='{loc_value}'"
    else:
        # Generic search across all levels
        return f"Q(community__barangay__municipality__province__region__name__icontains='{loc_value}') | Q(community__barangay__municipality__province__name__icontains='{loc_value}')"


# =============================================================================
# BASIC NEEDS QUERY TEMPLATES (5 templates)
# =============================================================================

NEEDS_COUNT_TEMPLATES = [
    QueryTemplate(
        id='count_all_needs',
        category='needs',
        pattern=r'\b(how many|total|count|number of)\s+(all\s+|identified\s+|community\s+)?needs\b',
        query_template='Need.objects.count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many needs have been identified?',
            'Total needs',
            'Count all needs',
            'Number of identified needs',
            'How many community needs?'
        ],
        priority=10,
        result_type='count',
        description='Count total identified needs across all communities',
        tags=['count', 'needs', 'total']
    ),
    QueryTemplate(
        id='count_needs_by_priority',
        category='needs',
        pattern=r'\b(how many|count|total|number of)\s+(?P<priority>critical|high|medium|low|immediate|urgent)\s+(priority\s+)?needs\b',
        query_template='Need.objects.filter({priority_filter}).count()',
        required_entities=['priority_level'],
        optional_entities=[],
        examples=[
            'How many critical needs?',
            'Count high priority needs',
            'Total immediate needs',
            'Number of urgent needs',
            'How many high priority needs?'
        ],
        priority=10,
        result_type='count',
        description='Count needs by priority/urgency level',
        tags=['count', 'needs', 'priority']
    ),
    QueryTemplate(
        id='count_needs_by_sector',
        category='needs',
        pattern=r'\b(how many|count|total|number of)\s+(?P<sector>[\w\s]+?)\s+(sector\s+)?needs\b',
        query_template='Need.objects.filter({sector_filter}).count()',
        required_entities=['sector'],
        optional_entities=[],
        examples=[
            'How many infrastructure needs?',
            'Count education needs',
            'Total health sector needs',
            'Number of livelihood needs',
            'How many economic development needs?'
        ],
        priority=10,
        result_type='count',
        description='Count needs by development sector',
        tags=['count', 'needs', 'sector']
    ),
    QueryTemplate(
        id='count_needs_by_location',
        category='needs',
        pattern=r'\b(how many|count|total)\s+needs\s+(in|at|within|from)\s+(?P<location>[\w\s]+?)(\?|$)',
        query_template='Need.objects.filter({location_filter}).count()',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'How many needs in Region IX?',
            'Count needs in Zamboanga del Sur',
            'Total needs in Sultan Kudarat',
            'Needs in Cotabato City'
        ],
        priority=9,
        result_type='count',
        description='Count needs in specific location',
        tags=['count', 'needs', 'location']
    ),
    QueryTemplate(
        id='count_needs_by_status',
        category='needs',
        pattern=r'\b(how many|count|total|number of)\s+(?P<status>unmet|unfulfilled|met|fulfilled|ongoing|planned|identified|completed)\s+needs\b',
        query_template='Need.objects.filter({status_filter}).count()',
        required_entities=['status'],
        optional_entities=[],
        examples=[
            'How many unmet needs?',
            'Count fulfilled needs',
            'Total ongoing needs',
            'Number of identified needs',
            'How many completed needs?'
        ],
        priority=10,
        result_type='count',
        description='Count needs by fulfillment status',
        tags=['count', 'needs', 'status']
    ),
]


# =============================================================================
# NEEDS ANALYSIS TEMPLATES (5 templates)
# =============================================================================

NEEDS_ANALYSIS_TEMPLATES = [
    QueryTemplate(
        id='list_unmet_needs',
        category='needs',
        pattern=r'\b((show|list|display)\s+(me\s+)?(unmet|unfulfilled|unaddressed)\s+needs|needs\s+without\s+(funding|ppas))\b',
        query_template='Need.objects.filter(status="identified", linked_ppa__isnull=True).select_related("community__barangay__municipality__province__region", "category", "assessment").order_by("-priority_score", "-impact_severity")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me unmet needs',
            'List unfulfilled needs',
            'Display unaddressed needs',
            'Needs without funding',
            'Show needs not yet addressed'
        ],
        priority=10,
        result_type='list',
        description='List needs without implementing PPAs (unmet needs)',
        tags=['list', 'needs', 'unmet', 'gap']
    ),
    QueryTemplate(
        id='list_top_priority_needs',
        category='needs',
        pattern=r'\b(top|highest|critical)\s+(\d+\s+)?(priority\s+)?needs\b',
        query_template='Need.objects.select_related("community__barangay__municipality__province__region", "category", "assessment").order_by("-priority_score", "-impact_severity", "-community_votes")[:10]',
        required_entities=[],
        optional_entities=['numbers'],
        examples=[
            'Top priority needs',
            'Top 10 critical needs',
            'Highest priority needs',
            'Show top 5 priority needs',
            'Most critical needs'
        ],
        priority=10,
        result_type='list',
        description='List top priority needs by priority score and impact',
        tags=['list', 'needs', 'priority', 'top']
    ),
    QueryTemplate(
        id='needs_by_assessment',
        category='needs',
        pattern=r'\bneeds\s+(from|identified in|in)\s+(assessment|workshop|study|baseline)\s*(?P<assessment_id>[\w-]*)',
        query_template='Need.objects.filter(assessment__id="{assessment_id}").select_related("community__barangay__municipality__province", "category").order_by("-priority_score")[:50]',
        required_entities=['assessment'],
        optional_entities=[],
        examples=[
            'Needs from Assessment X',
            'What needs were identified in workshop?',
            'Show needs in assessment abc123',
            'Needs from baseline study'
        ],
        priority=9,
        result_type='list',
        description='List needs identified in a specific assessment',
        tags=['list', 'needs', 'assessment']
    ),
    QueryTemplate(
        id='needs_by_community',
        category='needs',
        pattern=r'\b(needs\s+(for|in|of)\s+.*?community|what needs does.*community|(show|list|display)\s+needs\s+in\s+.*?community)',
        query_template='Need.objects.filter(community__display_name__icontains="{community}").select_related("community__barangay", "category", "assessment").order_by("-priority_score")[:30]',
        required_entities=['community'],
        optional_entities=[],
        examples=[
            'Needs for Community Y',
            'What needs does this community have?',
            'Show needs in Maranao community',
            'Community needs list'
        ],
        priority=9,
        result_type='list',
        description='List needs for a specific OBC community',
        tags=['list', 'needs', 'community']
    ),
    QueryTemplate(
        id='list_needs_by_sector',
        category='needs',
        pattern=r'\b(show|list|display)\s+(me\s+)?(?P<sector>[\w\s]+?)\s+(sector\s+)?needs\b',
        query_template='Need.objects.filter({sector_filter}).select_related("community__barangay__municipality__province", "category", "assessment").order_by("-priority_score", "-impact_severity")[:30]',
        required_entities=['sector'],
        optional_entities=[],
        examples=[
            'Show infrastructure needs',
            'List education needs',
            'Display health sector needs',
            'Show me livelihood needs',
            'Economic development needs'
        ],
        priority=9,
        result_type='list',
        description='List needs in a specific development sector',
        tags=['list', 'needs', 'sector']
    ),
]


# =============================================================================
# CROSS-DOMAIN QUERY TEMPLATES (2 templates)
# =============================================================================

NEEDS_CROSS_DOMAIN_TEMPLATES = [
    QueryTemplate(
        id='needs_with_ppas',
        category='needs',
        pattern=r'\b(needs\s+with\s+(implementing\s+)?(ppas|programs|projects|funding|budget)|(show|list|display)\s+addressed\s+needs)',
        query_template='Need.objects.filter(linked_ppa__isnull=False).select_related("community__barangay__municipality__province", "category", "linked_ppa").order_by("-priority_score")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Needs with implementing PPAs',
            'Show addressed needs',
            'Needs with funding',
            'Needs with programs',
            'Needs with budget allocation'
        ],
        priority=9,
        result_type='list',
        description='List needs that have implementing PPAs/programs',
        tags=['list', 'needs', 'ppas', 'addressed']
    ),
    QueryTemplate(
        id='needs_without_ppas',
        category='needs',
        pattern=r'\b(needs\s+without\s+(implementing\s+)?(ppas|programs|projects|funding|budget)|needs\s+not\s+yet\s+addressed|unaddressed\s+needs)',
        query_template='Need.objects.filter(linked_ppa__isnull=True).select_related("community__barangay__municipality__province__region", "category").order_by("-priority_score", "-impact_severity", "-community_votes")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Needs not yet addressed',
            'Unaddressed needs',
            'Needs without PPAs',
            'Needs without funding',
            'Needs without programs'
        ],
        priority=10,
        result_type='list',
        description='List needs without implementing PPAs (gap analysis)',
        tags=['list', 'needs', 'gap', 'unaddressed']
    ),
]


# =============================================================================
# COMBINE ALL TEMPLATES
# =============================================================================

NEEDS_TEMPLATES = (
    NEEDS_COUNT_TEMPLATES +
    NEEDS_ANALYSIS_TEMPLATES +
    NEEDS_CROSS_DOMAIN_TEMPLATES
)

# Total: 5 + 5 + 2 = 12 critical needs templates
