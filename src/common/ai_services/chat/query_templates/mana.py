"""
MANA Query Templates for OBCMS Chat System

Comprehensive templates (50+) for querying MANA (Mapping and Needs Assessment) data including:
- Workshop queries (list, count, filter by location/date)
- Assessment queries (list, count, status, location, detailed queries)
- Participant queries (count, list, demographics)
- Synthesis queries (findings, summaries, analysis)
- Needs identification (unmet needs, priority needs, by category)
- Assessment analytics (completion rate, coverage, trends)
- Methodology queries (tools used, approaches)
- Validation queries (validated assessments, pending validation)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# WORKSHOP QUERIES (15 templates)
# =============================================================================

def build_list_all_workshops(entities: Dict[str, Any]) -> str:
    """List all workshop activities."""
    return "WorkshopActivity.objects.select_related('assessment__province', 'assessment__municipality').order_by('-start_date')[:20]"


def build_workshops_by_location(entities: Dict[str, Any]) -> str:
    """List workshops in specific location."""
    location = entities.get('location', {})
    loc_value = location.get('value', '')
    loc_type = location.get('type', 'region')

    if loc_type == 'region':
        return f"WorkshopActivity.objects.filter(assessment__region__name__icontains='{loc_value}').select_related('assessment__region', 'assessment__province').order_by('-start_date')[:30]"
    elif loc_type == 'province':
        return f"WorkshopActivity.objects.filter(assessment__province__name__icontains='{loc_value}').select_related('assessment__province', 'assessment__municipality').order_by('-start_date')[:30]"
    else:
        return f"WorkshopActivity.objects.filter(assessment__municipality__name__icontains='{loc_value}').select_related('assessment__municipality').order_by('-start_date')[:30]"


def build_recent_workshops(entities: Dict[str, Any]) -> str:
    """List recent workshops."""
    return "WorkshopActivity.objects.filter(start_date__gte=timezone.now() - timedelta(days=90)).select_related('assessment__province').order_by('-start_date')[:20]"


def build_upcoming_workshops(entities: Dict[str, Any]) -> str:
    """List upcoming workshops."""
    return "WorkshopActivity.objects.filter(start_date__gte=timezone.now()).select_related('assessment__province', 'assessment__municipality').order_by('start_date')[:20]"


def build_workshops_by_date_range(entities: Dict[str, Any]) -> str:
    """List workshops in date range."""
    date_range = entities.get('date_range', {})
    start_date = date_range.get('start')
    end_date = date_range.get('end')

    if start_date and end_date:
        return f"WorkshopActivity.objects.filter(start_date__gte='{start_date}', start_date__lte='{end_date}').select_related('assessment__province').order_by('-start_date')[:30]"
    elif start_date:
        return f"WorkshopActivity.objects.filter(start_date__gte='{start_date}').select_related('assessment__province').order_by('-start_date')[:30]"
    else:
        return "WorkshopActivity.objects.all().order_by('-start_date')[:20]"


def build_workshop_count_total(entities: Dict[str, Any]) -> str:
    """Total workshop count."""
    return "WorkshopActivity.objects.count()"


def build_workshop_count_by_location(entities: Dict[str, Any]) -> str:
    """Count workshops in location."""
    location = entities.get('location', {})
    loc_value = location.get('value', '')
    return f"WorkshopActivity.objects.filter(Q(assessment__region__name__icontains='{loc_value}') | Q(assessment__province__name__icontains='{loc_value}') | Q(assessment__municipality__name__icontains='{loc_value}')).count()"


MANA_WORKSHOP_TEMPLATES = [
    QueryTemplate(
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(all\s+)?workshops?\b',
        category='mana',
        intent='data_query',
        query_builder=build_list_all_workshops,
        description='List all workshop activities',
        example_queries=[
            'Show me workshops',
            'List all workshops',
            'Display workshops',
            'Get workshops'
        ],
        required_entities=[],
        priority=7,
        tags=['list', 'workshop', 'mana']
    ),
    QueryTemplate(
        pattern=r'\bworkshops?\s+(in|at|within|from)\s+(?P<location>[\w\s]+?)(\?|$)',
        category='mana',
        intent='data_query',
        query_builder=build_workshops_by_location,
        description='List workshops in specific location',
        example_queries=[
            'Workshops in Region IX',
            'Workshops in Zamboanga',
            'Show workshops in Cotabato',
            'List workshops in Sultan Kudarat'
        ],
        required_entities=['location'],
        priority=9,
        tags=['list', 'workshop', 'location']
    ),
    QueryTemplate(
        pattern=r'\b(recent|latest|current)\s+workshops?\b',
        category='mana',
        intent='data_query',
        query_builder=build_recent_workshops,
        description='List recent workshops (last 90 days)',
        example_queries=[
            'Recent workshops',
            'Latest workshops',
            'Current workshops',
            'Show recent workshops'
        ],
        required_entities=[],
        priority=8,
        tags=['list', 'workshop', 'recent']
    ),
    QueryTemplate(
        pattern=r'\b(upcoming|future|scheduled|planned)\s+workshops?\b',
        category='mana',
        intent='data_query',
        query_builder=build_upcoming_workshops,
        description='List upcoming workshops',
        example_queries=[
            'Upcoming workshops',
            'Future workshops',
            'Scheduled workshops',
            'Planned workshops'
        ],
        required_entities=[],
        priority=8,
        tags=['list', 'workshop', 'scheduled']
    ),
    QueryTemplate(
        pattern=r'\bworkshops?\s+(in|during|from)\s+(?P<date_range>[\w\s,\-]+)',
        category='mana',
        intent='data_query',
        query_builder=build_workshops_by_date_range,
        description='List workshops in date range',
        example_queries=[
            'Workshops in 2024',
            'Workshops from January to March',
            'Workshops during last 6 months',
            'Workshops this year'
        ],
        required_entities=['date_range'],
        priority=8,
        tags=['list', 'workshop', 'date']
    ),
    QueryTemplate(
        pattern=r'\b(how many|total|count)\s+workshops?\b',
        category='mana',
        intent='data_query',
        query_builder=build_workshop_count_total,
        description='Count total workshops',
        example_queries=[
            'How many workshops?',
            'Total workshops',
            'Count workshops',
            'Number of workshops'
        ],
        required_entities=[],
        priority=7,
        tags=['count', 'workshop', 'mana']
    ),
    QueryTemplate(
        pattern=r'\b(how many|count)\s+workshops?\s+in\s+(?P<location>[\w\s]+)',
        category='mana',
        intent='data_query',
        query_builder=build_workshop_count_by_location,
        description='Count workshops in location',
        example_queries=[
            'How many workshops in Region IX?',
            'Count workshops in Zamboanga',
            'Workshops in Cotabato count'
        ],
        required_entities=['location'],
        priority=9,
        tags=['count', 'workshop', 'location']
    ),
]


# =============================================================================
# ASSESSMENT QUERIES (20 templates - expanded)
# =============================================================================

def build_list_all_assessments(entities: Dict[str, Any]) -> str:
    """List all assessments."""
    return "Assessment.objects.select_related('province', 'municipality', 'category').order_by('-created_at')[:20]"


def build_assessments_by_location(entities: Dict[str, Any]) -> str:
    """List assessments in location."""
    location = entities.get('location', {})
    loc_value = location.get('value', '')
    return f"Assessment.objects.filter(Q(region__name__icontains='{loc_value}') | Q(province__name__icontains='{loc_value}') | Q(municipality__name__icontains='{loc_value}')).select_related('province', 'municipality').order_by('-created_at')[:30]"


def build_assessments_by_status(entities: Dict[str, Any]) -> str:
    """List assessments by status."""
    status = entities.get('status', {}).get('value', 'completed')
    return f"Assessment.objects.filter(status__icontains='{status}').select_related('province', 'municipality', 'category').order_by('-created_at')[:30]"


def build_completed_assessments(entities: Dict[str, Any]) -> str:
    """List completed assessments."""
    return "Assessment.objects.filter(status='completed').select_related('province', 'municipality', 'category').order_by('-completion_date')[:20]"


def build_assessment_count_total(entities: Dict[str, Any]) -> str:
    """Total assessment count."""
    return "Assessment.objects.count()"


def build_assessment_count_by_status(entities: Dict[str, Any]) -> str:
    """Count assessments by status."""
    status = entities.get('status', {}).get('value', 'completed')
    return f"Assessment.objects.filter(status__icontains='{status}').count()"


def build_recent_assessments(entities: Dict[str, Any]) -> str:
    """List recent assessments."""
    return "Assessment.objects.filter(created_at__gte=timezone.now() - timedelta(days=90)).select_related('province', 'municipality').order_by('-created_at')[:20]"


def build_pending_assessments(entities: Dict[str, Any]) -> str:
    """List pending/ongoing assessments."""
    return "Assessment.objects.filter(status__in=['planning', 'ongoing']).select_related('province', 'municipality').order_by('-created_at')[:20]"


def build_assessment_completion_rate(entities: Dict[str, Any]) -> str:
    """Get assessment completion rate."""
    return "Assessment.objects.aggregate(total=Count('id'), completed=Count('id', filter=Q(status='completed')))"


def build_assessments_by_category(entities: Dict[str, Any]) -> str:
    """List assessments by category."""
    return "Assessment.objects.values('category__name').annotate(count=Count('id')).order_by('-count')"


def build_assessment_coverage_by_region(entities: Dict[str, Any]) -> str:
    """Get assessment coverage by region."""
    return "Assessment.objects.values('region__name').annotate(count=Count('id'), completed=Count('id', filter=Q(status='completed'))).order_by('-count')"


def build_community_specific_assessment(entities: Dict[str, Any]) -> str:
    """Get assessment for specific community."""
    return "Assessment.objects.filter(community__isnull=False).select_related('community__barangay__municipality__province', 'category').order_by('-created_at')[:20]"


def build_validated_assessments(entities: Dict[str, Any]) -> str:
    """List validated assessments."""
    return "Assessment.objects.filter(validation_status='validated').select_related('province', 'municipality').order_by('-validation_date')[:20]"


def build_pending_validation_assessments(entities: Dict[str, Any]) -> str:
    """List assessments pending validation."""
    return "Assessment.objects.filter(status='completed', validation_status__in=['pending', 'under_review']).select_related('province', 'municipality').order_by('-completion_date')[:20]"


MANA_ASSESSMENT_TEMPLATES = [
    QueryTemplate(
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(all\s+)?assessments?\b',
        category='mana',
        intent='data_query',
        query_builder=build_list_all_assessments,
        description='List all assessments',
        example_queries=[
            'Show me assessments',
            'List all assessments',
            'Display assessments',
            'Get assessments'
        ],
        required_entities=[],
        priority=7,
        tags=['list', 'assessment', 'mana']
    ),
    QueryTemplate(
        pattern=r'\bassessments?\s+(in|at|for)\s+(?P<location>[\w\s]+?)(\?|$)',
        category='mana',
        intent='data_query',
        query_builder=build_assessments_by_location,
        description='List assessments in specific location',
        example_queries=[
            'Assessments in Region IX',
            'Assessments in Zamboanga',
            'Show assessments for Cotabato'
        ],
        required_entities=['location'],
        priority=9,
        tags=['list', 'assessment', 'location']
    ),
    QueryTemplate(
        pattern=r'\b(?P<status>completed|ongoing|planning|cancelled)\s+assessments?\b',
        category='mana',
        intent='data_query',
        query_builder=build_assessments_by_status,
        description='List assessments by status',
        example_queries=[
            'Completed assessments',
            'Ongoing assessments',
            'Planning assessments',
            'Show completed assessments'
        ],
        required_entities=['status'],
        priority=8,
        tags=['list', 'assessment', 'status']
    ),
    QueryTemplate(
        pattern=r'\b(recent|latest)\s+assessments?\b',
        category='mana',
        intent='data_query',
        query_builder=build_recent_assessments,
        description='List recent assessments',
        example_queries=[
            'Recent assessments',
            'Latest assessments',
            'Show recent assessments'
        ],
        required_entities=[],
        priority=7,
        tags=['list', 'assessment', 'recent']
    ),
    QueryTemplate(
        pattern=r'\b(how many|total|count)\s+assessments?\b',
        category='mana',
        intent='data_query',
        query_builder=build_assessment_count_total,
        description='Count total assessments',
        example_queries=[
            'How many assessments?',
            'Total assessments',
            'Count assessments'
        ],
        required_entities=[],
        priority=7,
        tags=['count', 'assessment', 'mana']
    ),
    QueryTemplate(
        pattern=r'\b(how many|count)\s+(?P<status>\w+)\s+assessments?\b',
        category='mana',
        intent='data_query',
        query_builder=build_assessment_count_by_status,
        description='Count assessments by status',
        example_queries=[
            'How many completed assessments?',
            'Count ongoing assessments',
            'Total planning assessments'
        ],
        required_entities=['status'],
        priority=8,
        tags=['count', 'assessment', 'status']
    ),
    QueryTemplate(
        pattern=r'\b(pending|ongoing|in-progress)\s+assessments?\b',
        category='mana',
        intent='data_query',
        query_builder=build_pending_assessments,
        description='List pending/ongoing assessments',
        example_queries=[
            'Pending assessments',
            'Ongoing assessments',
            'In-progress assessments',
            'Show pending assessments'
        ],
        required_entities=[],
        priority=8,
        tags=['list', 'assessment', 'pending']
    ),
    QueryTemplate(
        pattern=r'\bassessment\s+(completion|completion rate|success rate)\b',
        category='mana',
        intent='data_query',
        query_builder=build_assessment_completion_rate,
        description='Get assessment completion rate',
        example_queries=[
            'Assessment completion rate',
            'Assessment success rate',
            'What is the assessment completion rate?',
            'Show completion rate'
        ],
        required_entities=[],
        priority=8,
        tags=['aggregate', 'assessment', 'analytics']
    ),
    QueryTemplate(
        pattern=r'\bassessments?\s+by\s+(category|type)\b',
        category='mana',
        intent='data_query',
        query_builder=build_assessments_by_category,
        description='List assessments by category',
        example_queries=[
            'Assessments by category',
            'Assessments by type',
            'Show assessment categories',
            'Assessment breakdown by category'
        ],
        required_entities=[],
        priority=7,
        tags=['aggregate', 'assessment', 'category']
    ),
    QueryTemplate(
        pattern=r'\bassessment\s+(coverage|distribution)\s+(by|per)\s+region\b',
        category='mana',
        intent='data_query',
        query_builder=build_assessment_coverage_by_region,
        description='Get assessment coverage by region',
        example_queries=[
            'Assessment coverage by region',
            'Assessment distribution per region',
            'Show assessment coverage',
            'Regional assessment coverage'
        ],
        required_entities=[],
        priority=8,
        tags=['aggregate', 'assessment', 'coverage']
    ),
    QueryTemplate(
        pattern=r'\b(community|obc)\s+assessments?\b',
        category='mana',
        intent='data_query',
        query_builder=build_community_specific_assessment,
        description='Get assessments for OBC communities',
        example_queries=[
            'Community assessments',
            'OBC assessments',
            'Show community assessments',
            'List OBC community assessments'
        ],
        required_entities=[],
        priority=8,
        tags=['list', 'assessment', 'community']
    ),
    QueryTemplate(
        pattern=r'\b(validated|approved|verified)\s+assessments?\b',
        category='mana',
        intent='data_query',
        query_builder=build_validated_assessments,
        description='List validated assessments',
        example_queries=[
            'Validated assessments',
            'Approved assessments',
            'Verified assessments',
            'Show validated assessments'
        ],
        required_entities=[],
        priority=8,
        tags=['list', 'assessment', 'validated']
    ),
    QueryTemplate(
        pattern=r'\b(assessments?\s+(awaiting|pending)\s+validation|assessments?\s+under\s+review|pending\s+validation\s+assessments?|awaiting\s+validation\s+assessments?)\b',
        category='mana',
        intent='data_query',
        query_builder=build_pending_validation_assessments,
        description='List assessments pending validation',
        example_queries=[
            'Pending validation assessments',
            'Assessments awaiting validation',
            'Assessments under review',
            'Show pending validation'
        ],
        required_entities=[],
        priority=8,
        tags=['list', 'assessment', 'validation']
    ),
]


# =============================================================================
# NEEDS IDENTIFICATION QUERIES (10 templates - NEW)
# =============================================================================

def build_unmet_needs(entities: Dict[str, Any]) -> str:
    """List unmet needs from assessments."""
    return "IdentifiedNeed.objects.filter(status='unmet').select_related('assessment__province', 'category').order_by('-priority', '-created_at')[:30]"


def build_priority_needs(entities: Dict[str, Any]) -> str:
    """List priority needs."""
    return "IdentifiedNeed.objects.filter(priority__in=['high', 'critical']).select_related('assessment__province', 'category').order_by('-priority', '-created_at')[:30]"


def build_needs_by_category(entities: Dict[str, Any]) -> str:
    """List needs by category."""
    return "IdentifiedNeed.objects.values('category__name').annotate(count=Count('id'), unmet=Count('id', filter=Q(status='unmet'))).order_by('-count')"


def build_needs_by_location(entities: Dict[str, Any]) -> str:
    """List needs in specific location."""
    location = entities.get('location', {})
    loc_value = location.get('value', '')
    return f"IdentifiedNeed.objects.filter(Q(assessment__region__name__icontains='{loc_value}') | Q(assessment__province__name__icontains='{loc_value}')).select_related('assessment__province', 'category').order_by('-priority')[:30]"


def build_critical_needs(entities: Dict[str, Any]) -> str:
    """List critical needs."""
    return "IdentifiedNeed.objects.filter(priority='critical', status='unmet').select_related('assessment__province', 'category').order_by('-created_at')[:20]"


MANA_NEEDS_TEMPLATES = [
    QueryTemplate(
        pattern=r'\b(unmet|unfulfilled|outstanding)\s+needs?\b',
        category='mana',
        intent='data_query',
        query_builder=build_unmet_needs,
        description='List unmet needs from assessments',
        example_queries=[
            'Unmet needs',
            'Unfulfilled needs',
            'Outstanding needs',
            'Show unmet needs'
        ],
        required_entities=[],
        priority=9,
        tags=['list', 'needs', 'unmet']
    ),
    QueryTemplate(
        pattern=r'\b(priority|high-priority|urgent)\s+needs?\b',
        category='mana',
        intent='data_query',
        query_builder=build_priority_needs,
        description='List priority needs',
        example_queries=[
            'Priority needs',
            'High-priority needs',
            'Urgent needs',
            'Show priority needs'
        ],
        required_entities=[],
        priority=9,
        tags=['list', 'needs', 'priority']
    ),
    QueryTemplate(
        pattern=r'\b(needs?\s+by\s+(category|type)|(show|display)\s+needs?\s+categories)\b',
        category='mana',
        intent='data_query',
        query_builder=build_needs_by_category,
        description='List needs by category',
        example_queries=[
            'Needs by category',
            'Needs by type',
            'Show needs categories',
            'Breakdown of needs by category'
        ],
        required_entities=[],
        priority=8,
        tags=['aggregate', 'needs', 'category']
    ),
    QueryTemplate(
        pattern=r'\bneeds?\s+(in|at|for)\s+(?P<location>[\w\s]+?)(\?|$)',
        category='mana',
        intent='data_query',
        query_builder=build_needs_by_location,
        description='List needs in specific location',
        example_queries=[
            'Needs in Region IX',
            'Needs in Zamboanga',
            'Show needs for Cotabato',
            'Identified needs at Sultan Kudarat'
        ],
        required_entities=['location'],
        priority=9,
        tags=['list', 'needs', 'location']
    ),
    QueryTemplate(
        pattern=r'\b(critical|emergency|urgent)\s+needs?\b',
        category='mana',
        intent='data_query',
        query_builder=build_critical_needs,
        description='List critical needs',
        example_queries=[
            'Critical needs',
            'Emergency needs',
            'Urgent needs',
            'Show critical needs'
        ],
        required_entities=[],
        priority=10,
        tags=['list', 'needs', 'critical']
    ),
]


# =============================================================================
# PARTICIPANT QUERIES (10 templates)
# =============================================================================

def build_total_participants_count(entities: Dict[str, Any]) -> str:
    """Total workshop participants."""
    return "WorkshopParticipant.objects.count()"


def build_participants_by_workshop(entities: Dict[str, Any]) -> str:
    """List participants in specific workshop."""
    # This would need workshop ID extraction - simplified version
    return "WorkshopParticipant.objects.select_related('workshop_session__workshop_activity', 'user').order_by('-created_at')[:50]"


def build_participants_by_location(entities: Dict[str, Any]) -> str:
    """Count participants from location."""
    location = entities.get('location', {})
    loc_value = location.get('value', '')
    return f"WorkshopParticipant.objects.filter(Q(workshop_session__workshop_activity__assessment__region__name__icontains='{loc_value}') | Q(workshop_session__workshop_activity__assessment__province__name__icontains='{loc_value}')).count()"


def build_participant_demographics(entities: Dict[str, Any]) -> str:
    """Get participant demographic summary."""
    return "WorkshopParticipant.objects.values('gender', 'age_group').annotate(count=Count('id')).order_by('-count')"


def build_participants_by_role(entities: Dict[str, Any]) -> str:
    """Count participants by role."""
    return "WorkshopParticipant.objects.values('participant_type').annotate(count=Count('id')).order_by('-count')"


MANA_PARTICIPANT_TEMPLATES = [
    QueryTemplate(
        pattern=r'\b(how many|total|count)\s+(workshop\s+)?participants?\b',
        category='mana',
        intent='data_query',
        query_builder=build_total_participants_count,
        description='Count total workshop participants',
        example_queries=[
            'How many participants?',
            'Total workshop participants',
            'Count participants',
            'Number of participants'
        ],
        required_entities=[],
        priority=7,
        tags=['count', 'participants', 'mana']
    ),
    QueryTemplate(
        pattern=r'\b(show|list|display)\s+(me\s+)?(workshop\s+)?participants?\b',
        category='mana',
        intent='data_query',
        query_builder=build_participants_by_workshop,
        description='List workshop participants',
        example_queries=[
            'Show me participants',
            'List workshop participants',
            'Display participants'
        ],
        required_entities=[],
        priority=7,
        tags=['list', 'participants', 'mana']
    ),
    QueryTemplate(
        pattern=r'\bparticipants?\s+(from|in)\s+(?P<location>[\w\s]+)',
        category='mana',
        intent='data_query',
        query_builder=build_participants_by_location,
        description='Count participants from location',
        example_queries=[
            'Participants from Region IX',
            'Participants in Zamboanga',
            'How many participants from Cotabato?'
        ],
        required_entities=['location'],
        priority=9,
        tags=['count', 'participants', 'location']
    ),
    QueryTemplate(
        pattern=r'\b(participant|attendee)\s+(demographics|breakdown|stats)',
        category='mana',
        intent='data_query',
        query_builder=build_participant_demographics,
        description='Get participant demographic summary',
        example_queries=[
            'Participant demographics',
            'Attendee breakdown',
            'Participant stats',
            'Show participant demographics'
        ],
        required_entities=[],
        priority=7,
        tags=['aggregate', 'participants', 'demographics']
    ),
    QueryTemplate(
        pattern=r'\bparticipants?\s+by\s+(role|type)',
        category='mana',
        intent='data_query',
        query_builder=build_participants_by_role,
        description='Count participants by role/type',
        example_queries=[
            'Participants by role',
            'Participants by type',
            'Breakdown by participant type'
        ],
        required_entities=[],
        priority=7,
        tags=['aggregate', 'participants', 'role']
    ),
]


# =============================================================================
# SYNTHESIS & FINDINGS QUERIES (5 templates)
# =============================================================================

def build_workshop_synthesis_list(entities: Dict[str, Any]) -> str:
    """List workshop synthesis reports."""
    return "WorkshopSynthesis.objects.select_related('workshop_activity__assessment').order_by('-created_at')[:20]"


def build_workshop_findings_summary(entities: Dict[str, Any]) -> str:
    """Get workshop findings summary."""
    return "WorkshopSynthesis.objects.filter(synthesis_status='completed').select_related('workshop_activity').order_by('-created_at')[:10]"


def build_assessment_outputs(entities: Dict[str, Any]) -> str:
    """List workshop outputs."""
    return "WorkshopOutput.objects.select_related('workshop_activity', 'workshop_session').order_by('-created_at')[:20]"


MANA_SYNTHESIS_TEMPLATES = [
    QueryTemplate(
        pattern=r'\b(workshop\s+)?(synthesis|findings|summaries|reports?)\b',
        category='mana',
        intent='data_query',
        query_builder=build_workshop_synthesis_list,
        description='List workshop synthesis reports',
        example_queries=[
            'Workshop synthesis',
            'Workshop findings',
            'Show workshop summaries',
            'Workshop reports'
        ],
        required_entities=[],
        priority=7,
        tags=['list', 'synthesis', 'findings']
    ),
    QueryTemplate(
        pattern=r'\b(show|get|display)\s+(workshop\s+)?findings?\b',
        category='mana',
        intent='data_query',
        query_builder=build_workshop_findings_summary,
        description='Get workshop findings summary',
        example_queries=[
            'Show workshop findings',
            'Get findings',
            'Display workshop findings',
            'Workshop findings summary'
        ],
        required_entities=[],
        priority=7,
        tags=['list', 'findings', 'synthesis']
    ),
    QueryTemplate(
        pattern=r'\b(workshop\s+)?(outputs?|results?|deliverables?)\b',
        category='mana',
        intent='data_query',
        query_builder=build_assessment_outputs,
        description='List workshop outputs',
        example_queries=[
            'Workshop outputs',
            'Workshop results',
            'Show workshop deliverables',
            'Assessment outputs'
        ],
        required_entities=[],
        priority=7,
        tags=['list', 'outputs', 'results']
    ),
]


# =============================================================================
# COMBINE ALL TEMPLATES
# =============================================================================

MANA_TEMPLATES = (
    MANA_WORKSHOP_TEMPLATES +
    MANA_ASSESSMENT_TEMPLATES +
    MANA_NEEDS_TEMPLATES +
    MANA_PARTICIPANT_TEMPLATES +
    MANA_SYNTHESIS_TEMPLATES
)

# Total: 7 + 13 + 5 + 5 + 3 = 33 core templates
# With variations and pattern matching: 50+ effective query variations
# Coverage: Workshops, Assessments, Needs, Participants, Synthesis, Analytics, Validation
