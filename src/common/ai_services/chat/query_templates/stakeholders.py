"""
Stakeholder Network Query Templates for OBCMS Chat System

10 high-value, low-complexity templates for querying stakeholder network data.
Simple filter/count queries for immediate deployment.

Key Models:
- Stakeholder: Tracks key community figures (leaders, religious, teachers, etc.)
- Related to OBCCommunity via community foreign key

Stakeholder Types:
- community_leader: Community Leader
- barangay_captain: Barangay Captain
- tribal_leader: Tribal Leader/Datu
- ulama: Ulama
- imam: Imam/Khatib
- ustadz: Ustadz/Religious Teacher
- arabic_teacher: ALIVE/Arabic Teacher
- madrasa_teacher: Madrasah Teacher
- youth_leader: Youth Leader
- women_leader: Women Leader
- business_leader: Business Leader
- cooperative_leader: Cooperative Leader
- health_worker: Community Health Worker
- volunteer: Community Volunteer
- other: Other

Influence Levels:
- very_high, high, medium, low, emerging

Engagement Levels:
- very_active, active, moderate, limited, inactive

Attributes:
- full_name: Full name
- stakeholder_type: Type/role
- position: Official position/title
- organization: Organization represented
- influence_level: Level of influence
- engagement_level: Level of engagement
- is_active: Active status
"""

from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# STAKEHOLDER NETWORK TEMPLATES (10 templates)
# =============================================================================

STAKEHOLDER_TEMPLATES = [
    # Template 1: Count stakeholders by type
    QueryTemplate(
        id='count_stakeholders_by_type',
        category='stakeholders',
        pattern=r'\b(how many|count|total)\s+(?P<stakeholder_type>religious|ulama|imam|ustadz|youth|women|community|barangay|tribal|business|cooperative|health|madrasa|arabic)(\s+(leaders?|stakeholders?|teachers?|workers?|captains?))?\b',
        query_template="Stakeholder.objects.filter(stakeholder_type__icontains='{stakeholder_type}').count()",
        required_entities=['stakeholder_type'],
        optional_entities=[],
        examples=[
            'How many religious leaders?',
            'Count ulama stakeholders',
            'Total youth leaders',
            'How many imam?',
            'Women leaders count'
        ],
        priority=9,
        description='Count stakeholders by type (religious, youth, women, etc.)',
        tags=['stakeholders', 'type', 'count'],
        result_type='count'
    ),

    # Template 2: Count stakeholders by influence level
    QueryTemplate(
        id='count_stakeholders_by_influence',
        category='stakeholders',
        pattern=r'\b(how many|count|total)\s+(?P<influence>very\s*high|high|medium|low|emerging)\s+(influence|influential)\s+(stakeholders?|leaders?)',
        query_template="Stakeholder.objects.filter(influence_level__icontains='{influence}').count()",
        required_entities=['influence'],
        optional_entities=[],
        examples=[
            'How many high influence stakeholders?',
            'Count very high influence leaders',
            'Total emerging influence stakeholders',
            'Medium influence leaders count',
            'How many influential stakeholders?'
        ],
        priority=8,
        description='Count stakeholders by influence level',
        tags=['stakeholders', 'influence', 'count'],
        result_type='count'
    ),

    # Template 3: Count stakeholders by engagement level
    QueryTemplate(
        id='count_stakeholders_by_engagement',
        category='stakeholders',
        pattern=r'\b(how many|count|total)\s+(?P<engagement>very\s*active|active|moderate|limited|inactive)\s+(stakeholders?|leaders?)',
        query_template="Stakeholder.objects.filter(engagement_level__icontains='{engagement}').count()",
        required_entities=['engagement'],
        optional_entities=[],
        examples=[
            'How many active stakeholders?',
            'Count very active leaders',
            'Total inactive stakeholders',
            'Limited engagement leaders count',
            'Moderate stakeholders count'
        ],
        priority=8,
        description='Count stakeholders by engagement level',
        tags=['stakeholders', 'engagement', 'count'],
        result_type='count'
    ),

    # Template 4: Count religious leaders
    QueryTemplate(
        id='count_religious_leaders',
        category='stakeholders',
        pattern=r'\b(how many|count|total)\s+(ulama|imams?|ustadz|religious\s*leaders?|religious\s*teachers?)',
        query_template="Stakeholder.objects.filter(Q(stakeholder_type='ulama') | Q(stakeholder_type='imam') | Q(stakeholder_type='ustadz')).count()",
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many ulama?',
            'Count imams',
            'Total ustadz',
            'Religious leaders count',
            'How many religious teachers?'
        ],
        priority=9,
        description='Count religious leaders (Ulama, Imams, Ustadz)',
        tags=['stakeholders', 'religious', 'count'],
        result_type='count'
    ),

    # Template 5: Count community organizations
    QueryTemplate(
        id='count_community_organizations',
        category='stakeholders',
        pattern=r'\b(how many|count|total)\s+(csos?|civil\s*society|associations?|organizations?)\s+(by\s*community|per\s*community)?',
        query_template="OBCCommunity.objects.aggregate(total_csos=Sum('csos_count'), total_associations=Sum('associations_count'))",
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many CSOs by community?',
            'Count civil society organizations',
            'Total associations per community',
            'Community organizations count',
            'CSO count'
        ],
        priority=7,
        description='Count CSOs and associations by community',
        tags=['stakeholders', 'organizations', 'count'],
        result_type='aggregate'
    ),

    # Template 6: List high influence stakeholders
    QueryTemplate(
        id='list_high_influence_stakeholders',
        category='stakeholders',
        pattern=r'\b(show|list|find|which|who)\s+(are\s*)?(the\s*)?(high|very\s*high)\s+(influence|influential)\s+(stakeholders?|leaders?)',
        query_template="Stakeholder.objects.filter(influence_level__in=['high', 'very_high']).select_related('community__barangay').values('full_name', 'stakeholder_type', 'position', 'influence_level', 'community__barangay__name', 'community__barangay__municipality__name').order_by('-influence_level', 'stakeholder_type')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show high influence stakeholders',
            'List very high influence leaders',
            'Who are the influential stakeholders?',
            'Find high influence leaders',
            'Which leaders have high influence?'
        ],
        priority=8,
        description='List stakeholders with high/very high influence',
        tags=['stakeholders', 'influence', 'list'],
        result_type='list'
    ),

    # Template 7: List inactive stakeholders
    QueryTemplate(
        id='list_inactive_stakeholders',
        category='stakeholders',
        pattern=r'\b(show|list|find|which|who)\s+(are\s*)?(inactive|limited\s*engagement)\s+(stakeholders?|leaders?)',
        query_template="Stakeholder.objects.filter(engagement_level__in=['inactive', 'limited'], is_active=True).select_related('community__barangay').values('full_name', 'stakeholder_type', 'engagement_level', 'community__barangay__name', 'contact_number').order_by('engagement_level', 'stakeholder_type')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show inactive stakeholders',
            'List stakeholders with limited engagement',
            'Who are the inactive leaders?',
            'Find stakeholders needing re-engagement',
            'Which leaders are inactive?'
        ],
        priority=8,
        description='List inactive or limited engagement stakeholders',
        tags=['stakeholders', 'engagement', 'list'],
        result_type='list'
    ),

    # Template 8: Stakeholder engagement history
    QueryTemplate(
        id='stakeholder_engagement_history',
        category='stakeholders',
        pattern=r'\b(engagement|activities|interactions)\s+(history|record|log)\s+(for|of|by)\s+(?P<stakeholder_name>[\w\s]+)',
        query_template="Stakeholder.objects.filter(Q(full_name__icontains='{stakeholder_name}') | Q(nickname__icontains='{stakeholder_name}')).select_related('community').values('full_name', 'stakeholder_type', 'engagement_level', 'position', 'organization', 'community__barangay__name', 'responsibilities')",
        required_entities=['stakeholder_name'],
        optional_entities=[],
        examples=[
            'Engagement history for Ustadz Abdullah',
            'Activities record of Imam Hassan',
            'Interactions by Datu Miguel',
            'Show engagement for Barangay Captain Maria',
            'Stakeholder activities for Juan Santos'
        ],
        priority=7,
        description='Show engagement history for specific stakeholder',
        tags=['stakeholders', 'engagement', 'list'],
        result_type='list'
    ),

    # Template 9: Stakeholders by expertise
    QueryTemplate(
        id='stakeholders_by_expertise',
        category='stakeholders',
        pattern=r'\b(stakeholders?|leaders?|experts?)\s+(with|having|by)\s+(expertise|skills?|specialization)\s+(in\s*)?(?P<expertise>[\w\s]+)',
        query_template="Stakeholder.objects.filter(Q(position__icontains='{expertise}') | Q(responsibilities__icontains='{expertise}') | Q(expertise__icontains='{expertise}')).select_related('community__barangay').values('full_name', 'stakeholder_type', 'position', 'organization', 'community__barangay__name').order_by('stakeholder_type')",
        required_entities=['expertise'],
        optional_entities=[],
        examples=[
            'Stakeholders with expertise in education',
            'Leaders having health skills',
            'Experts by agriculture specialization',
            'Stakeholders with livelihood expertise',
            'Who has expertise in peace building?'
        ],
        priority=7,
        description='Find stakeholders by specific expertise or skills',
        tags=['stakeholders', 'expertise', 'list'],
        result_type='list'
    ),

    # Template 10: Stakeholder networks analysis
    QueryTemplate(
        id='stakeholder_networks_analysis',
        category='stakeholders',
        pattern=r'\b(stakeholder|network)\s+(connections?|networks?|relationships?|analysis)\s+(by\s*community)?',
        query_template="Stakeholder.objects.exclude(external_connections='').select_related('community__barangay').values('full_name', 'stakeholder_type', 'organization', 'external_connections', 'community__barangay__name', 'community__barangay__municipality__name').order_by('community__barangay__name', 'stakeholder_type')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Stakeholder connections by community',
            'Network analysis',
            'Show stakeholder relationships',
            'Network connections',
            'Stakeholder network analysis'
        ],
        priority=7,
        description='Analyze stakeholder networks and external connections',
        tags=['stakeholders', 'network', 'list'],
        result_type='list'
    ),
]


# Export templates for registration
__all__ = ['STAKEHOLDER_TEMPLATES']
