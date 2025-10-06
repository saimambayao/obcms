"""
Infrastructure Analysis Query Templates for OBCMS Chat System

10 high-value, low-complexity templates for querying community infrastructure data.
These templates fill critical gaps with simple filter/count queries for immediate deployment.

Key Models:
- CommunityInfrastructure: Tracks water, electricity, healthcare, education, etc.
- Related to OBCCommunity via community foreign key

Infrastructure Types:
- water: Water Supply
- electricity: Electricity
- roads: Roads/Transportation
- communication: Communication/Internet
- health: Health Facilities
- education: Education Facilities
- religious: Religious Facilities
- market: Market/Trading Post
- waste: Waste Management
- drainage: Drainage System

Availability Status:
- available: Available
- limited: Limited
- poor: Poor Quality
- none: Not Available
- planned: Planned/Proposed

Condition:
- excellent, good, fair, poor, very_poor

Priority:
- critical, high, medium, low
"""

from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# INFRASTRUCTURE ANALYSIS TEMPLATES (10 templates)
# =============================================================================

INFRASTRUCTURE_TEMPLATES = [
    # Template 1: Count communities by water access
    QueryTemplate(
        id='count_communities_by_water_access',
        category='infrastructure',
        pattern=r'\b(how many|count|total)\s+(obc\s+)?communities\s+(have|with|having)?\s*(?P<rating>poor|limited|available|none|no)?\s*(water|water supply|water access)',
        query_template="OBCCommunity.objects.filter(infrastructure__infrastructure_type='water', infrastructure__availability_status__icontains='{rating}').distinct().count()",
        required_entities=['rating'],
        optional_entities=[],
        examples=[
            'How many communities have poor water access?',
            'Communities with limited water supply',
            'Count communities with no water access',
            'Communities having available water',
            'Total communities with poor water'
        ],
        priority=9,
        description='Count communities by water access rating',
        tags=['infrastructure', 'water', 'count'],
        result_type='count'
    ),

    # Template 2: Count communities without electricity
    QueryTemplate(
        id='count_communities_by_electricity',
        category='infrastructure',
        pattern=r'\b(how many|count|total)\s+(obc\s+)?communities\s+(without|with no|lacking|have no|need|poor|limited)?\s*(electricity|power|electric)',
        query_template="OBCCommunity.objects.filter(infrastructure__infrastructure_type='electricity', infrastructure__availability_status__in=['none', 'poor', 'limited']).distinct().count()",
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many communities without electricity?',
            'Communities with no power',
            'Count communities lacking electricity',
            'Communities need electricity',
            'Total communities with poor electricity'
        ],
        priority=9,
        description='Count communities without adequate electricity access',
        tags=['infrastructure', 'electricity', 'count'],
        result_type='count'
    ),

    # Template 3: Count communities by healthcare facilities
    QueryTemplate(
        id='count_communities_by_healthcare',
        category='infrastructure',
        pattern=r'\b(how many|count|total)\s+(obc\s+)?communities\s+(without|with no|lacking|have no|need|poor)?\s*(health\s*facilities|healthcare|health\s*centers?|hospitals?|clinics?)',
        query_template="OBCCommunity.objects.filter(infrastructure__infrastructure_type='health', infrastructure__availability_status__in=['none', 'poor', 'limited']).distinct().count()",
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many communities with no health facilities?',
            'Communities without healthcare',
            'Count communities lacking health centers',
            'Communities need health facilities',
            'Total communities with poor health access'
        ],
        priority=9,
        description='Count communities with inadequate healthcare facilities',
        tags=['infrastructure', 'health', 'count'],
        result_type='count'
    ),

    # Template 4: Count communities by education facilities
    QueryTemplate(
        id='count_communities_by_education',
        category='infrastructure',
        pattern=r'\b(how many|count|total)\s+(obc\s+)?communities\s+(without|with no|lacking|have no|need)?\s*(schools?|education\s*facilities|learning\s*centers?|madrasah)',
        query_template="OBCCommunity.objects.filter(infrastructure__infrastructure_type='education', infrastructure__availability_status__in=['none', 'poor', 'limited']).distinct().count()",
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many communities without schools nearby?',
            'Communities with no education facilities',
            'Count communities lacking schools',
            'Communities need schools',
            'Total communities with poor education access'
        ],
        priority=9,
        description='Count communities with inadequate education facilities',
        tags=['infrastructure', 'education', 'count'],
        result_type='count'
    ),

    # Template 5: Count communities by sanitation access
    QueryTemplate(
        id='count_communities_by_sanitation',
        category='infrastructure',
        pattern=r'\b(how many|count|total)\s+(obc\s+)?communities\s+(with|having|by)?\s*(?P<rating>poor|limited|available|none|good)?\s*(sanitation|waste\s*management|drainage|sewage)',
        query_template="OBCCommunity.objects.filter(Q(infrastructure__infrastructure_type='waste') | Q(infrastructure__infrastructure_type='drainage'), infrastructure__availability_status__icontains='{rating}').distinct().count()",
        required_entities=['rating'],
        optional_entities=[],
        examples=[
            'How many communities have poor sanitation?',
            'Communities with limited waste management',
            'Count communities by drainage rating',
            'Communities with no sanitation',
            'Total communities with available drainage'
        ],
        priority=8,
        description='Count communities by sanitation/waste management access',
        tags=['infrastructure', 'sanitation', 'count'],
        result_type='count'
    ),

    # Template 6: List critical infrastructure gaps
    QueryTemplate(
        id='list_critical_infrastructure_gaps',
        category='infrastructure',
        pattern=r'\b(show|list|find|display)\s+(obc\s+)?communities\s+(with|having)?\s*(critical|urgent|priority|high\s*priority)?\s*(infrastructure|needs|gaps|improvements)',
        query_template="OBCCommunity.objects.filter(infrastructure__priority_for_improvement__in=['critical', 'high']).distinct().values('id', 'barangay__name', 'barangay__municipality__name', 'barangay__municipality__province__name')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show communities with critical infrastructure needs',
            'List communities with urgent infrastructure gaps',
            'Find communities with high priority improvements',
            'Display communities with critical needs',
            'Communities with priority infrastructure gaps'
        ],
        priority=8,
        description='List communities with critical/high priority infrastructure needs',
        tags=['infrastructure', 'critical', 'list'],
        result_type='list'
    ),

    # Template 7: List communities with poor water
    QueryTemplate(
        id='list_communities_poor_water',
        category='infrastructure',
        pattern=r'\b(show|list|find|which|what)\s+(obc\s+)?communities\s+(need|require|lack|have\s*poor|with\s*poor|without)?\s*(water|water\s*supply|water\s*access)',
        query_template="OBCCommunity.objects.filter(infrastructure__infrastructure_type='water', infrastructure__availability_status__in=['poor', 'none', 'limited']).distinct().values('id', 'barangay__name', 'barangay__municipality__name', 'barangay__municipality__province__name')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show communities needing water improvements',
            'List communities with poor water supply',
            'Which communities lack water access?',
            'Find communities without water',
            'Communities requiring water improvements'
        ],
        priority=8,
        description='List communities needing water infrastructure improvements',
        tags=['infrastructure', 'water', 'list'],
        result_type='list'
    ),

    # Template 8: List communities with poor electricity
    QueryTemplate(
        id='list_communities_poor_electricity',
        category='infrastructure',
        pattern=r'\b(show|list|find|which|what)\s+(obc\s+)?communities\s+(need|require|lack|have\s*poor|with\s*poor|without)?\s*(electricity|power|electric)',
        query_template="OBCCommunity.objects.filter(infrastructure__infrastructure_type='electricity', infrastructure__availability_status__in=['poor', 'none', 'limited']).distinct().values('id', 'barangay__name', 'barangay__municipality__name', 'barangay__municipality__province__name')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show communities needing electricity',
            'List communities with poor power access',
            'Which communities lack electricity?',
            'Find communities without power',
            'Communities requiring electricity improvements'
        ],
        priority=8,
        description='List communities needing electricity infrastructure improvements',
        tags=['infrastructure', 'electricity', 'list'],
        result_type='list'
    ),

    # Template 9: Infrastructure coverage by province
    QueryTemplate(
        id='infrastructure_coverage_by_province',
        category='infrastructure',
        pattern=r'\b(show|list|display|summary|breakdown)\s*(of)?\s*(infrastructure|water|electricity|health|education)?\s*(availability|coverage|access)?\s*by\s*province',
        query_template="CommunityInfrastructure.objects.values('community__barangay__municipality__province__name', 'infrastructure_type').annotate(total=Count('id'), available=Count('id', filter=Q(availability_status='available'))).order_by('community__barangay__municipality__province__name', 'infrastructure_type')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show infrastructure availability by province',
            'Infrastructure coverage summary by province',
            'Display water access by province',
            'List electricity availability by province',
            'Health facilities breakdown by province'
        ],
        priority=7,
        description='Show infrastructure availability summary grouped by province',
        tags=['infrastructure', 'province', 'summary'],
        result_type='aggregate'
    ),

    # Template 10: Infrastructure improvement priorities
    QueryTemplate(
        id='infrastructure_improvement_priorities',
        category='infrastructure',
        pattern=r'\b(show|list|what|which)\s+(infrastructure|improvements?|projects?|priorities)\s+(are\s*)?(flagged|marked|priority|critical|high|urgent)',
        query_template="CommunityInfrastructure.objects.filter(priority_for_improvement__in=['critical', 'high']).select_related('community__barangay__municipality__province').values('community__barangay__name', 'infrastructure_type', 'availability_status', 'priority_for_improvement', 'notes').order_by('-priority_for_improvement', 'infrastructure_type')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show infrastructure flagged as priority',
            'List critical infrastructure improvements',
            'What infrastructure projects are urgent?',
            'Which improvements are high priority?',
            'Infrastructure marked as critical'
        ],
        priority=7,
        description='List infrastructure flagged for priority improvements',
        tags=['infrastructure', 'priority', 'list'],
        result_type='list'
    ),
]


# Export templates for registration
__all__ = ['INFRASTRUCTURE_TEMPLATES']
