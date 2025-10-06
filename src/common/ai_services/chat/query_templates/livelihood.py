"""
Livelihood & Economic Query Templates for OBCMS Chat System

10 high-value, low-complexity templates for querying community livelihood and economic data.
Simple filter/count queries for immediate deployment.

Key Models:
- CommunityLivelihood: Tracks livelihood activities within OBC communities
- Related to OBCCommunity via community foreign key

Livelihood Categories:
- agriculture: Agriculture
- fishing: Fishing
- livestock: Livestock
- trade: Trade/Business
- services: Services
- handicrafts: Handicrafts
- transportation: Transportation
- construction: Construction
- government: Government Employment
- private_employment: Private Employment
- other: Other

Income Levels:
- very_low, low, moderate, high, very_high

Attributes:
- is_primary_livelihood: Boolean (primary livelihood for community)
- seasonal: Boolean (whether seasonal work)
- households_involved: Number of households
- percentage_of_community: Percentage involved
- challenges: Text field for challenges
- opportunities: Text field for opportunities
"""

from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# LIVELIHOOD & ECONOMIC TEMPLATES (10 templates)
# =============================================================================

LIVELIHOOD_TEMPLATES = [
    # Template 1: Count livelihoods by type
    QueryTemplate(
        id='count_livelihoods_by_type',
        category='livelihood',
        pattern=r'\b(how many|count|total)\s+(?P<livelihood_type>fishing|agriculture|farming|livestock|trade|business|services|handicrafts?|transportation|construction|government|employment)\s+(communities|livelihoods?)',
        query_template="CommunityLivelihood.objects.filter(livelihood_type__icontains='{livelihood_type}').count()",
        required_entities=['livelihood_type'],
        optional_entities=[],
        examples=[
            'How many fishing communities?',
            'Count agriculture livelihoods',
            'Total livestock communities',
            'How many trade communities?',
            'Handicraft livelihoods count'
        ],
        priority=9,
        description='Count livelihoods by type (fishing, agriculture, etc.)',
        tags=['livelihood', 'type', 'count'],
        result_type='count'
    ),

    # Template 2: Count primary livelihoods distribution
    QueryTemplate(
        id='count_primary_livelihoods',
        category='livelihood',
        pattern=r'\b(distribution|breakdown|summary)\s+of\s+(primary\s+)?(livelihoods?|economic\s*activities)',
        query_template="CommunityLivelihood.objects.filter(is_primary_livelihood=True).values('livelihood_type').annotate(count=Count('id')).order_by('-count')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Distribution of primary livelihoods',
            'Breakdown of livelihoods',
            'Summary of economic activities',
            'Primary livelihood distribution',
            'Livelihood breakdown'
        ],
        priority=8,
        description='Show distribution of primary livelihoods across communities',
        tags=['livelihood', 'primary', 'distribution'],
        result_type='aggregate'
    ),

    # Template 3: Count seasonal vs year-round livelihoods
    QueryTemplate(
        id='count_seasonal_livelihoods',
        category='livelihood',
        pattern=r'\b(how many|count|total)\s+(seasonal|year.round|permanent)\s+(livelihoods?|activities|jobs)',
        query_template="CommunityLivelihood.objects.filter(seasonal=True).count() if 'seasonal' in query else CommunityLivelihood.objects.filter(seasonal=False).count()",
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many seasonal livelihoods?',
            'Count year-round activities',
            'Total seasonal jobs',
            'Permanent livelihood count',
            'Seasonal vs year-round breakdown'
        ],
        priority=7,
        description='Count seasonal vs year-round livelihoods',
        tags=['livelihood', 'seasonal', 'count'],
        result_type='count'
    ),

    # Template 4: Livelihood income levels
    QueryTemplate(
        id='livelihood_income_levels',
        category='livelihood',
        pattern=r'\b(communities|livelihoods?)\s+(by|with)\s+(income\s*level|(?P<income_level>very\s*low|low|moderate|high|very\s*high)\s*income)',
        query_template="CommunityLivelihood.objects.filter(income_level__icontains='{income_level}').select_related('community').values('community__barangay__name', 'livelihood_type', 'income_level').distinct()" if 'income_level' in '{income_level}' else "CommunityLivelihood.objects.values('income_level').annotate(count=Count('id')).order_by('income_level')",
        required_entities=[],
        optional_entities=['income_level'],
        examples=[
            'Communities by livelihood income level',
            'Livelihoods with low income',
            'Communities with moderate income',
            'High income livelihoods',
            'Income level breakdown'
        ],
        priority=8,
        description='Show communities grouped by livelihood income level',
        tags=['livelihood', 'income', 'list'],
        result_type='list'
    ),

    # Template 5: Livelihood participation rate
    QueryTemplate(
        id='livelihood_participation_rate',
        category='livelihood',
        pattern=r'\b(participation|involvement|percentage|how many)\s+(rate|involved|participating)\s+in\s+(primary\s+)?livelihood',
        query_template="CommunityLivelihood.objects.filter(is_primary_livelihood=True).aggregate(avg_participation=Avg('percentage_of_community'))",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Participation rate in primary livelihood',
            'Percentage involved in livelihoods',
            'How many participating in primary livelihood?',
            'Average involvement in livelihoods',
            'Livelihood participation rate'
        ],
        priority=7,
        description='Calculate average participation rate in primary livelihoods',
        tags=['livelihood', 'participation', 'aggregate'],
        result_type='aggregate'
    ),

    # Template 6: List livelihood challenges
    QueryTemplate(
        id='list_livelihood_challenges',
        category='livelihood',
        pattern=r'\b(what|show|list|common)\s+(are\s*)?(the\s*)?(livelihood\s*)?(challenges|problems|issues|difficulties)',
        query_template="CommunityLivelihood.objects.exclude(challenges='').values('livelihood_type', 'challenges', 'community__barangay__name').order_by('livelihood_type')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'What are livelihood challenges?',
            'Show common livelihood problems',
            'List livelihood issues',
            'Common livelihood difficulties',
            'Challenges in livelihoods'
        ],
        priority=8,
        description='List common livelihood challenges faced by communities',
        tags=['livelihood', 'challenges', 'list'],
        result_type='list'
    ),

    # Template 7: List communities by livelihood opportunity
    QueryTemplate(
        id='list_communities_by_livelihood_opportunity',
        category='livelihood',
        pattern=r'\b(show|list|which|what)\s+(communities|livelihoods?)\s+(with|have|having)?\s*(opportunities|potential|prospects)',
        query_template="CommunityLivelihood.objects.exclude(opportunities='').select_related('community__barangay').values('community__barangay__name', 'livelihood_type', 'opportunities', 'community__barangay__municipality__name')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show communities with livelihood opportunities',
            'List livelihoods with potential',
            'Which communities have livelihood prospects?',
            'Communities with opportunities',
            'Livelihood potential by community'
        ],
        priority=8,
        description='List communities with documented livelihood opportunities',
        tags=['livelihood', 'opportunities', 'list'],
        result_type='list'
    ),

    # Template 8: Livelihood diversity by community
    QueryTemplate(
        id='livelihood_diversity_by_community',
        category='livelihood',
        pattern=r'\b(communities|livelihoods?)\s+(with|having)?\s*(multiple|diverse|variety|diversified)\s+(livelihoods?|activities|income\s*sources)',
        query_template="CommunityLivelihood.objects.values('community__barangay__name', 'community__id').annotate(livelihood_count=Count('id')).filter(livelihood_count__gt=1).order_by('-livelihood_count')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Communities with multiple livelihoods',
            'Communities having diverse activities',
            'Variety of income sources by community',
            'Communities with diversified livelihoods',
            'Livelihood diversity by community'
        ],
        priority=7,
        description='Show communities with multiple/diversified livelihoods',
        tags=['livelihood', 'diversity', 'list'],
        result_type='list'
    ),

    # Template 9: Economic organizations count
    QueryTemplate(
        id='economic_organizations_count',
        category='livelihood',
        pattern=r'\b(how many|count|total)\s+(cooperatives?|social\s*enterprises?|associations?|organizations?)\s+(by\s*location|in|at|per\s*community)?',
        query_template="OBCCommunity.objects.aggregate(total_cooperatives=Sum('number_of_cooperatives'), total_enterprises=Sum('number_of_social_enterprises'), total_micro=Sum('number_of_micro_enterprises'))",
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many cooperatives by location?',
            'Count social enterprises in communities',
            'Total cooperatives per community',
            'Economic organizations count',
            'Cooperatives and enterprises total'
        ],
        priority=7,
        description='Count economic organizations (cooperatives, enterprises) by location',
        tags=['livelihood', 'organizations', 'count'],
        result_type='aggregate'
    ),

    # Template 10: Unbanked population analysis
    QueryTemplate(
        id='unbanked_population_analysis',
        category='livelihood',
        pattern=r'\b(communities|how many|count)\s+(with|having)?\s*(unbanked|no\s*bank\s*access|without\s*banking)\s+(population|people|residents)',
        query_template="OBCCommunity.objects.filter(number_of_unbanked_obc__gt=0).values('barangay__name', 'barangay__municipality__name', 'number_of_unbanked_obc', 'estimated_obc_population').order_by('-number_of_unbanked_obc')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Communities with unbanked population',
            'How many unbanked residents?',
            'Count communities without banking access',
            'Communities having unbanked people',
            'Unbanked population by community'
        ],
        priority=7,
        description='Show communities with unbanked population',
        tags=['livelihood', 'banking', 'list'],
        result_type='list'
    ),
]


# Export templates for registration
__all__ = ['LIVELIHOOD_TEMPLATES']
