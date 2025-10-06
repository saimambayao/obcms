"""
Communities Query Templates for OBCMS Chat System

50+ template variations for querying OBC Community data including:
- Count queries (total communities, filtered counts)
- List queries (show communities, filter by attributes)
- Aggregate queries (population stats, demographics)
- Filter queries (ethnicity, livelihood, location combinations)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# HELPER FUNCTIONS FOR QUERY GENERATION
# =============================================================================

def build_location_filter_clause(location_data: Dict[str, Any], base_field: str = "barangay__municipality__province__region") -> str:
    """Build location filter clause based on extracted location entity."""
    loc_type = location_data.get('type', 'region')
    loc_value = location_data.get('value', '')

    if loc_type == 'region':
        return f"{base_field}__name__icontains='{loc_value}'"
    elif loc_type == 'province':
        return f"barangay__municipality__province__name__icontains='{loc_value}'"
    elif loc_type == 'municipality':
        return f"barangay__municipality__name__icontains='{loc_value}'"
    else:
        # Generic search across all levels
        return f"Q(barangay__municipality__province__region__name__icontains='{loc_value}') | Q(barangay__municipality__province__name__icontains='{loc_value}')"


# =============================================================================
# COUNT QUERY TEMPLATES (15 templates)
# =============================================================================

COMMUNITIES_COUNT_TEMPLATES = [
    QueryTemplate(
        id='count_total_communities',
        category='communities',
        pattern=r'\b(how many|total|count|number of)\s+(obc\s+)?communities\b',
        query_template='OBCCommunity.objects.count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many communities are there?',
            'Total communities',
            'Count all OBC communities',
            'Number of communities',
            'How many OBC communities?'
        ],
        priority=7,
        description='Count total OBC communities',
        tags=['count', 'communities', 'total']
    ),
    QueryTemplate(
        id='count_communities_by_location',
        category='communities',
        pattern=r'\b(how many|count|total)\s+(obc\s+)?communities\s+(in|at|within|from)\s+(?P<location>[\w\s]+?)(\?|$)',
        query_template='OBCCommunity.objects.filter({location_filter}).count()',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'How many communities in Region IX?',
            'Count communities in Zamboanga del Sur',
            'Total communities in Sultan Kudarat',
            'Communities in Cotabato City'
        ],
        priority=9,
        description='Count communities in specific location',
        tags=['count', 'communities', 'location']
    ),
    QueryTemplate(
        id='count_communities_by_ethnicity',
        category='communities',
        pattern=r'\b(how many|count|total)\s+(?P<ethnicity>\w+)\s+communities\b',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").count()',
        required_entities=['ethnolinguistic_group'],
        optional_entities=[],
        examples=[
            'How many Maranao communities?',
            'Count Maguindanaon communities',
            'Total Tausug communities',
            'Yakan communities count'
        ],
        priority=8,
        description='Count communities by ethnolinguistic group',
        tags=['count', 'communities', 'ethnicity']
    ),
    QueryTemplate(
        id='count_communities_by_livelihood',
        category='communities',
        pattern=r'\b(how many|count|total)\s+communities\s+(with|having)\s+(?P<livelihood>[\w\s]+?)\s+(livelihood|as livelihood)',
        query_template='OBCCommunity.objects.filter(primary_livelihood__icontains="{livelihood}").count()',
        required_entities=['livelihood'],
        optional_entities=[],
        examples=[
            'How many communities with fishing livelihood?',
            'Count communities having farming',
            'Total communities with trading livelihood'
        ],
        priority=8,
        description='Count communities by primary livelihood',
        tags=['count', 'communities', 'livelihood']
    ),
    QueryTemplate(
        id='count_ethnicity_location',
        category='communities',
        pattern=r'\b(how many|count|total)\s+(?P<ethnicity>\w+)\s+(communities|population)\s+in\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}", {location_filter}).count()',
        required_entities=['ethnolinguistic_group', 'location'],
        optional_entities=[],
        examples=[
            'How many Maranao communities in Region IX?',
            'Count Maguindanaon population in Cotabato',
            'Total Tausug communities in Zamboanga'
        ],
        priority=9,
        description='Count communities by ethnicity and location',
        tags=['count', 'communities', 'ethnicity', 'location']
    ),
    # Note: Geographic count templates (regions, provinces, municipalities, cities, barangays)
    # are handled by geographic.py with higher priority to avoid conflicts
]


# =============================================================================
# LIST QUERY TEMPLATES (15 templates)
# =============================================================================

COMMUNITIES_LIST_TEMPLATES = [
    QueryTemplate(
        id='list_all_communities',
        category='communities',
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(all\s+)?(obc\s+)?communities\b',
        query_template='OBCCommunity.objects.all().order_by("-created_at")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me communities',
            'List all OBC communities',
            'Display communities',
            'Get all communities'
        ],
        priority=6,
        description='List all OBC communities',
        tags=['list', 'communities']
    ),
    QueryTemplate(
        id='list_communities_by_location',
        category='communities',
        pattern=r'\b(show|list|display)\s+(me\s+)?(obc\s+)?communities\s+(in|at|within|from)\s+(?P<location>[\w\s]+?)(\?|$)',
        query_template='OBCCommunity.objects.filter({location_filter}).select_related("barangay__municipality__province__region").order_by("barangay__name")[:50]',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Show me communities in Region IX',
            'List communities in Zamboanga',
            'Display communities in Cotabato',
            'Communities in Region XII'
        ],
        priority=8,
        description='List communities in specific location',
        tags=['list', 'communities', 'location']
    ),
    QueryTemplate(
        id='list_communities_by_ethnicity',
        category='communities',
        pattern=r'\b(show|list|display)\s+(me\s+)?(?P<ethnicity>\w+)\s+communities\b',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").select_related("barangay__municipality__province__region").order_by("-estimated_obc_population")[:30]',
        required_entities=['ethnolinguistic_group'],
        optional_entities=[],
        examples=[
            'Show me Maranao communities',
            'List Maguindanaon communities',
            'Display Tausug communities'
        ],
        priority=8,
        description='List communities by ethnolinguistic group',
        tags=['list', 'communities', 'ethnicity']
    ),
    QueryTemplate(
        id='list_communities_by_livelihood',
        category='communities',
        pattern=r'\b(show|list|display)\s+(me\s+)?communities\s+with\s+(?P<livelihood>[\w\s]+?)\s+(livelihood|as primary)',
        query_template='OBCCommunity.objects.filter(primary_livelihood__icontains="{livelihood}").select_related("barangay__municipality__province").order_by("-estimated_obc_population")[:30]',
        required_entities=['livelihood'],
        optional_entities=[],
        examples=[
            'Show me communities with fishing livelihood',
            'List communities with farming',
            'Display communities with trading livelihood'
        ],
        priority=8,
        description='List communities by livelihood',
        tags=['list', 'communities', 'livelihood']
    ),
    QueryTemplate(
        id='list_recent_communities',
        category='communities',
        pattern=r'\b(recent|latest|new|newly added)\s+(obc\s+)?communities\b',
        query_template='OBCCommunity.objects.all().select_related("barangay__municipality__province__region").order_by("-created_at")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Recent communities',
            'Latest OBC communities',
            'Newly added communities',
            'Show recent communities'
        ],
        priority=7,
        description='List recently added communities',
        tags=['list', 'communities', 'recent']
    ),
]


# =============================================================================
# AGGREGATE QUERY TEMPLATES (10 templates)
# =============================================================================

COMMUNITIES_AGGREGATE_TEMPLATES = [
    QueryTemplate(
        id='aggregate_total_population',
        category='communities',
        pattern=r'\b(total|overall|combined)\s+(obc\s+)?population\b',
        query_template='OBCCommunity.objects.aggregate(total=Sum("estimated_obc_population"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Total OBC population',
            'Overall population',
            'Combined population of all communities',
            'What is the total population?'
        ],
        priority=8,
        description='Total OBC population across all communities',
        tags=['aggregate', 'population', 'total']
    ),
    QueryTemplate(
        id='aggregate_population_by_location',
        category='communities',
        pattern=r'\b(total|overall)\s+population\s+(in|at|within)\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter({location_filter}).aggregate(total=Sum("estimated_obc_population"))["total"]',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Total population in Region IX',
            'Overall population in Zamboanga',
            'Population in Cotabato'
        ],
        priority=8,
        description='Total population in specific location',
        tags=['aggregate', 'population', 'location']
    ),
    QueryTemplate(
        id='aggregate_average_household',
        category='communities',
        pattern=r'\b(average|mean)\s+(household\s+size|households)',
        query_template='OBCCommunity.objects.aggregate(avg_households=Avg("households"), avg_population=Avg("estimated_obc_population"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Average household size',
            'Mean households per community',
            'What is the average household size?'
        ],
        priority=7,
        description='Average household size across communities',
        tags=['aggregate', 'households', 'average']
    ),
    QueryTemplate(
        id='aggregate_top_ethnicities',
        category='communities',
        pattern=r'\b(top|main|major|primary)\s+(ethnolinguistic|ethnic)\s+(groups?|communities)',
        query_template='OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(count=Count("id")).order_by("-count")[:10]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Top ethnolinguistic groups',
            'Main ethnic groups',
            'Major ethnic communities',
            'Primary ethnolinguistic groups'
        ],
        priority=7,
        description='Top ethnolinguistic groups by community count',
        tags=['aggregate', 'ethnicity', 'top']
    ),
    QueryTemplate(
        id='aggregate_top_livelihoods',
        category='communities',
        pattern=r'\b(top|main|major|primary|common)\s+(livelihoods?|economic activities)',
        query_template='OBCCommunity.objects.values("primary_livelihood").annotate(count=Count("id")).order_by("-count")[:10]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Top livelihoods',
            'Main livelihoods',
            'Common economic activities',
            'Primary livelihoods'
        ],
        priority=7,
        description='Top livelihoods across communities',
        tags=['aggregate', 'livelihood', 'top']
    ),
    QueryTemplate(
        id='aggregate_largest_communities',
        category='communities',
        pattern=r'\b(largest|biggest|top\s+\d+)\s+(communities|populations)',
        query_template='OBCCommunity.objects.filter(estimated_obc_population__isnull=False).select_related("barangay__municipality__province__region").order_by("-estimated_obc_population")[:10]',
        required_entities=[],
        optional_entities=['numbers'],
        examples=[
            'Largest communities',
            'Biggest populations',
            'Top 10 largest communities',
            'Show largest communities'
        ],
        priority=7,
        description='Largest communities by population',
        tags=['aggregate', 'population', 'top']
    ),
    QueryTemplate(
        id='aggregate_proximity_barmm',
        category='communities',
        pattern=r'\bcommunities\s+by\s+proximity\s+to\s+barmm',
        query_template='OBCCommunity.objects.values("proximity_to_barmm").annotate(count=Count("id")).order_by("-count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Communities by proximity to BARMM',
            'Group communities by BARMM proximity',
            'How many adjacent to BARMM?'
        ],
        priority=6,
        description='Communities grouped by proximity to BARMM',
        tags=['aggregate', 'proximity', 'barmm']
    ),
]


# =============================================================================
# FILTER QUERY TEMPLATES (10 templates)
# =============================================================================

COMMUNITIES_FILTER_TEMPLATES = [
    QueryTemplate(
        id='filter_ethnicity_livelihood',
        category='communities',
        pattern=r'\b(?P<ethnicity>\w+)\s+(?P<livelihood>\w+)\s+communities',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}", primary_livelihood__icontains="{livelihood}").select_related("barangay__municipality__province__region")[:30]',
        required_entities=['ethnolinguistic_group', 'livelihood'],
        optional_entities=[],
        examples=[
            'Maranao fishing communities',
            'Maguindanaon farming communities',
            'Tausug trading communities'
        ],
        priority=9,
        description='Filter communities by ethnicity and livelihood',
        tags=['filter', 'ethnicity', 'livelihood']
    ),
    QueryTemplate(
        id='filter_location_livelihood',
        category='communities',
        pattern=r'\b(?P<livelihood>\w+)\s+communities\s+in\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter({location_filter}, primary_livelihood__icontains="{livelihood}").select_related("barangay__municipality__province")[:30]',
        required_entities=['location', 'livelihood'],
        optional_entities=[],
        examples=[
            'Fishing communities in Region IX',
            'Farming communities in Cotabato',
            'Trading communities in Zamboanga'
        ],
        priority=9,
        description='Filter communities by location and livelihood',
        tags=['filter', 'location', 'livelihood']
    ),
    QueryTemplate(
        id='filter_ethnicity_location_livelihood',
        category='communities',
        pattern=r'\b(?P<ethnicity>\w+)\s+(?P<livelihood>\w+)\s+communities\s+in\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}", {location_filter}, primary_livelihood__icontains="{livelihood}").select_related("barangay__municipality__province__region")[:20]',
        required_entities=['ethnolinguistic_group', 'livelihood', 'location'],
        optional_entities=[],
        examples=[
            'Maranao fishing communities in Region IX',
            'Maguindanaon farming communities in Cotabato'
        ],
        priority=10,
        description='Filter by ethnicity, livelihood, and location',
        tags=['filter', 'ethnicity', 'livelihood', 'location']
    ),
    QueryTemplate(
        id='filter_recent_additions',
        category='communities',
        pattern=r'\b(recent|latest|new)\s+community\s+additions',
        query_template='OBCCommunity.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).select_related("barangay__municipality__province__region").order_by("-created_at")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Recent community additions',
            'Latest community additions',
            'New communities added this month'
        ],
        priority=7,
        description='Recently added communities (last 30 days)',
        tags=['filter', 'recent']
    ),
]


# =============================================================================
# ADVANCED DEMOGRAPHIC QUERIES (12 templates)
# =============================================================================

COMMUNITIES_DEMOGRAPHIC_TEMPLATES = [
    QueryTemplate(
        id='aggregate_age_distribution',
        category='communities',
        pattern=r'\b(age distribution|population by age|age breakdown)',
        query_template='OBCCommunity.objects.aggregate(children=Sum("children_0_9"), adolescents=Sum("adolescents_10_14"), youth=Sum("youth_15_30"), adults=Sum("adults_31_59"), seniors=Sum("seniors_60_plus"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Age distribution',
            'Population by age',
            'Show age breakdown',
            'What is the age distribution?'
        ],
        priority=7,
        description='Age distribution across all communities',
        tags=['aggregate', 'demographics', 'age']
    ),
    QueryTemplate(
        id='aggregate_children_count',
        category='communities',
        pattern=r'\b(how many|total|count)\s+(children|kids|minors)',
        query_template='OBCCommunity.objects.aggregate(total_children=Sum("children_0_9"), total_adolescents=Sum("adolescents_10_14"))["total_children"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many children?',
            'Total children',
            'Count children in communities',
            'Number of kids'
        ],
        priority=7,
        description='Total children (0-9 years) across communities',
        tags=['aggregate', 'demographics', 'children']
    ),
    QueryTemplate(
        id='aggregate_youth_count',
        category='communities',
        pattern=r'\b(how many|total|count)\s+(youth|young people)',
        query_template='OBCCommunity.objects.aggregate(total=Sum("youth_15_30"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many youth?',
            'Total youth',
            'Count youth population',
            'Young people count'
        ],
        priority=7,
        description='Total youth (15-30 years) across communities',
        tags=['aggregate', 'demographics', 'youth']
    ),
    QueryTemplate(
        id='aggregate_seniors_count',
        category='communities',
        pattern=r'\b(how many|total|count)\s+(seniors|elderly|senior citizens)',
        query_template='OBCCommunity.objects.aggregate(total=Sum("seniors_60_plus"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many seniors?',
            'Total elderly',
            'Count senior citizens',
            'Elderly population'
        ],
        priority=7,
        description='Total seniors (60+ years) across communities',
        tags=['aggregate', 'demographics', 'seniors']
    ),
    QueryTemplate(
        id='aggregate_pwd_count',
        category='communities',
        pattern=r'\b(how many|total|count)\s+(pwd|persons with disabilities|disabled)',
        query_template='OBCCommunity.objects.aggregate(total=Sum("pwd_count"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many PWDs?',
            'Total persons with disabilities',
            'Count disabled population',
            'PWD count'
        ],
        priority=8,
        description='Total PWDs across all communities',
        tags=['aggregate', 'demographics', 'pwd', 'vulnerable']
    ),
    QueryTemplate(
        id='aggregate_solo_parents_count',
        category='communities',
        pattern=r'\b(how many|total|count)\s+solo parents',
        query_template='OBCCommunity.objects.aggregate(total=Sum("solo_parents_count"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many solo parents?',
            'Total solo parents',
            'Count solo parents',
            'Solo parent population'
        ],
        priority=7,
        description='Total solo parents across communities',
        tags=['aggregate', 'demographics', 'solo_parents', 'vulnerable']
    ),
    QueryTemplate(
        id='aggregate_idp_count',
        category='communities',
        pattern=r'\b(how many|total|count)\s+(idps?|internally displaced|displaced persons)',
        query_template='OBCCommunity.objects.aggregate(total=Sum("idps_count"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many IDPs?',
            'Total internally displaced persons',
            'Count IDPs',
            'Displaced persons count'
        ],
        priority=8,
        description='Total IDPs across all communities',
        tags=['aggregate', 'demographics', 'idp', 'vulnerable']
    ),
    QueryTemplate(
        id='aggregate_women_count',
        category='communities',
        pattern=r'\b(how many|total|count)\s+women',
        query_template='OBCCommunity.objects.aggregate(total=Sum("women_count"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many women?',
            'Total women',
            'Count women population',
            'Women count'
        ],
        priority=7,
        description='Total women across communities',
        tags=['aggregate', 'demographics', 'women']
    ),
    QueryTemplate(
        id='aggregate_vulnerable_sectors',
        category='communities',
        pattern=r'\b(vulnerable|disadvantaged)\s+(sectors?|groups?|populations?)',
        query_template='OBCCommunity.objects.aggregate(pwd=Sum("pwd_count"), solo_parents=Sum("solo_parents_count"), idps=Sum("idps_count"), unemployed=Sum("unemployed_count"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Vulnerable sectors',
            'Show vulnerable groups',
            'Disadvantaged populations',
            'Vulnerable population breakdown'
        ],
        priority=8,
        description='Summary of vulnerable sectors across communities',
        tags=['aggregate', 'demographics', 'vulnerable']
    ),
    QueryTemplate(
        id='communities_by_population_range',
        category='communities',
        pattern=r'\bcommunities\s+with\s+population\s+(over|under|between)\s+(?P<population>\d+)',
        query_template='OBCCommunity.objects.filter(estimated_obc_population__gte={population}).count()',
        required_entities=['numbers'],
        optional_entities=[],
        examples=[
            'Communities with population over 1000',
            'Communities with population under 500',
            'How many communities with population over 2000?'
        ],
        priority=7,
        description='Filter communities by population range',
        tags=['filter', 'population', 'demographics']
    ),
    QueryTemplate(
        id='demographics_by_location',
        category='communities',
        pattern=r'\b(demographics|population breakdown)\s+(in|for|of)\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter({location_filter}).aggregate(total_pop=Sum("estimated_obc_population"), children=Sum("children_0_9"), youth=Sum("youth_15_30"), adults=Sum("adults_31_59"), seniors=Sum("seniors_60_plus"))',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Demographics in Region IX',
            'Population breakdown for Zamboanga',
            'Demographics of Cotabato'
        ],
        priority=8,
        description='Demographic breakdown for specific location',
        tags=['aggregate', 'demographics', 'location']
    ),
    QueryTemplate(
        id='average_household_size_by_location',
        category='communities',
        pattern=r'\baverage household\s+(size\s+)?(in|for)\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter({location_filter}).aggregate(avg_households=Avg("households"), avg_population=Avg("estimated_obc_population"))',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Average household size in Region IX',
            'Average household for Zamboanga',
            'Household size in Cotabato'
        ],
        priority=7,
        description='Average household size in specific location',
        tags=['aggregate', 'households', 'location']
    ),
]


# =============================================================================
# ETHNOLINGUISTIC ANALYSIS (10 templates)
# =============================================================================

COMMUNITIES_ETHNOLINGUISTIC_TEMPLATES = [
    QueryTemplate(
        id='ethnicity_distribution',
        category='communities',
        pattern=r'\b(ethnicity|ethnic|ethnolinguistic)\s+(distribution|breakdown|groups)',
        query_template='OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(count=Count("id"), total_pop=Sum("estimated_obc_population")).order_by("-count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Ethnicity distribution',
            'Ethnic breakdown',
            'Ethnolinguistic groups',
            'Show ethnic distribution'
        ],
        priority=8,
        description='Distribution of ethnolinguistic groups',
        tags=['aggregate', 'ethnicity', 'distribution']
    ),
    QueryTemplate(
        id='ethnic_diversity_by_location',
        category='communities',
        pattern=r'\b(ethnic|ethnolinguistic)\s+(diversity|groups)\s+(in|at)\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter({location_filter}).values("primary_ethnolinguistic_group").annotate(count=Count("id")).order_by("-count")',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Ethnic diversity in Region IX',
            'Ethnolinguistic groups in Zamboanga',
            'Show ethnic groups in Cotabato'
        ],
        priority=8,
        description='Ethnic diversity in specific location',
        tags=['aggregate', 'ethnicity', 'location', 'diversity']
    ),
    QueryTemplate(
        id='population_by_ethnicity',
        category='communities',
        pattern=r'\bpopulation\s+(of|by)\s+(?P<ethnicity>\w+)',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").aggregate(total=Sum("estimated_obc_population"))["total"]',
        required_entities=['ethnolinguistic_group'],
        optional_entities=[],
        examples=[
            'Population of Maranao',
            'Population by Maguindanaon',
            'Tausug population',
            'Yakan population total'
        ],
        priority=8,
        description='Total population for specific ethnic group',
        tags=['aggregate', 'ethnicity', 'population']
    ),
    QueryTemplate(
        id='ethnicity_locations',
        category='communities',
        pattern=r'\bwhere (are|do)\s+(?P<ethnicity>\w+)\s+(communities|live|reside)',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").values("barangay__municipality__province__name", "barangay__municipality__name").annotate(count=Count("id")).order_by("-count")[:20]',
        required_entities=['ethnolinguistic_group'],
        optional_entities=[],
        examples=[
            'Where are Maranao communities?',
            'Where do Tausug live?',
            'Maguindanaon locations',
            'Where do Yakan reside?'
        ],
        priority=8,
        description='Locations of specific ethnic group',
        tags=['list', 'ethnicity', 'location']
    ),
    QueryTemplate(
        id='largest_ethnic_group_by_location',
        category='communities',
        pattern=r'\b(largest|dominant|main)\s+ethnic\s+group\s+in\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter({location_filter}).values("primary_ethnolinguistic_group").annotate(count=Count("id"), total_pop=Sum("estimated_obc_population")).order_by("-total_pop")[:1]',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Largest ethnic group in Region IX',
            'Dominant ethnic group in Zamboanga',
            'Main ethnic group in Cotabato'
        ],
        priority=8,
        description='Largest ethnic group in location',
        tags=['aggregate', 'ethnicity', 'location']
    ),
    QueryTemplate(
        id='multi_ethnic_communities',
        category='communities',
        pattern=r'\b(multi-ethnic|diverse|mixed)\s+communities',
        query_template='OBCCommunity.objects.exclude(other_ethnolinguistic_groups__exact="").select_related("barangay__municipality__province")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Multi-ethnic communities',
            'Show diverse communities',
            'Mixed ethnic communities',
            'Communities with multiple ethnic groups'
        ],
        priority=7,
        description='Communities with multiple ethnic groups',
        tags=['list', 'ethnicity', 'diversity']
    ),
    QueryTemplate(
        id='languages_spoken',
        category='communities',
        pattern=r'\b(languages?|dialects?)\s+spoken',
        query_template='OBCCommunity.objects.exclude(languages_spoken__exact="").values("languages_spoken").annotate(count=Count("id")).order_by("-count")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Languages spoken',
            'What languages are spoken?',
            'Show dialects spoken',
            'Language diversity'
        ],
        priority=7,
        description='Languages spoken across communities',
        tags=['aggregate', 'language', 'diversity']
    ),
    QueryTemplate(
        id='ethnicity_livelihood_correlation',
        category='communities',
        pattern=r'\b(?P<ethnicity>\w+)\s+(livelihoods?|economic activities)',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").values("primary_livelihood").annotate(count=Count("id")).order_by("-count")[:10]',
        required_entities=['ethnolinguistic_group'],
        optional_entities=[],
        examples=[
            'Maranao livelihoods',
            'Tausug economic activities',
            'What do Maguindanaon do for livelihood?',
            'Yakan livelihood patterns'
        ],
        priority=8,
        description='Livelihood patterns by ethnic group',
        tags=['aggregate', 'ethnicity', 'livelihood']
    ),
    QueryTemplate(
        id='ethnic_population_percentage',
        category='communities',
        pattern=r'\bpercentage\s+(of\s+)?(?P<ethnicity>\w+)',
        query_template='OBCCommunity.objects.aggregate(total=Count("id"), ethnic_count=Count("id", filter=Q(primary_ethnolinguistic_group__icontains="{ethnicity}")))',
        required_entities=['ethnolinguistic_group'],
        optional_entities=[],
        examples=[
            'Percentage of Maranao',
            'What percentage are Tausug?',
            'Maguindanaon percentage',
            'Share of Yakan communities'
        ],
        priority=7,
        description='Percentage of communities by ethnic group',
        tags=['aggregate', 'ethnicity', 'percentage']
    ),
    QueryTemplate(
        id='rare_ethnic_groups',
        category='communities',
        pattern=r'\b(rare|small|minority|less common)\s+ethnic\s+groups',
        query_template='OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(count=Count("id")).filter(count__lte=5).order_by("count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Rare ethnic groups',
            'Small ethnic groups',
            'Minority ethnic groups',
            'Less common ethnic groups'
        ],
        priority=6,
        description='Ethnic groups with few communities',
        tags=['aggregate', 'ethnicity', 'rare']
    ),
]


# =============================================================================
# LIVELIHOOD PATTERNS (10 templates)
# =============================================================================

COMMUNITIES_LIVELIHOOD_TEMPLATES = [
    QueryTemplate(
        id='livelihood_distribution',
        category='communities',
        pattern=r'\b(livelihood|economic)\s+(distribution|breakdown|patterns)',
        query_template='OBCCommunity.objects.values("primary_livelihood").annotate(count=Count("id"), total_pop=Sum("estimated_obc_population")).order_by("-count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Livelihood distribution',
            'Economic breakdown',
            'Livelihood patterns',
            'Show economic distribution'
        ],
        priority=7,
        description='Distribution of livelihoods',
        tags=['aggregate', 'livelihood', 'distribution']
    ),
    QueryTemplate(
        id='livelihood_by_location',
        category='communities',
        pattern=r'\b(livelihoods?|economic activities)\s+(in|at)\s+(?P<location>[\w\s]+)',
        query_template='OBCCommunity.objects.filter({location_filter}).values("primary_livelihood").annotate(count=Count("id")).order_by("-count")',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Livelihoods in Region IX',
            'Economic activities in Zamboanga',
            'Livelihoods at Cotabato'
        ],
        priority=8,
        description='Livelihood distribution in location',
        tags=['aggregate', 'livelihood', 'location']
    ),
    QueryTemplate(
        id='farmers_count_total',
        category='communities',
        pattern=r'\b(how many|total|count)\s+(farmers?|farming)',
        query_template='OBCCommunity.objects.aggregate(total=Sum("farmers_count"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many farmers?',
            'Total farmers',
            'Count farming population',
            'Farmer count'
        ],
        priority=7,
        description='Total farmers across communities',
        tags=['aggregate', 'livelihood', 'farmers']
    ),
    QueryTemplate(
        id='fisherfolk_count_total',
        category='communities',
        pattern=r'\b(how many|total|count)\s+(fisherfolk|fishermen|fishers)',
        query_template='OBCCommunity.objects.aggregate(total=Sum("fisherfolk_count"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many fisherfolk?',
            'Total fishermen',
            'Count fishers',
            'Fisherfolk count'
        ],
        priority=7,
        description='Total fisherfolk across communities',
        tags=['aggregate', 'livelihood', 'fisherfolk']
    ),
    QueryTemplate(
        id='unemployed_count_total',
        category='communities',
        pattern=r'\b(how many|total|count)\s+unemployed',
        query_template='OBCCommunity.objects.aggregate(total=Sum("unemployed_count"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many unemployed?',
            'Total unemployed',
            'Count unemployment',
            'Unemployed population'
        ],
        priority=7,
        description='Total unemployed across communities',
        tags=['aggregate', 'livelihood', 'unemployed']
    ),
    QueryTemplate(
        id='livelihood_diversity_index',
        category='communities',
        pattern=r'\b(livelihood|economic)\s+(diversity|variety)',
        query_template='OBCCommunity.objects.values("primary_livelihood", "secondary_livelihood").annotate(count=Count("id")).order_by("-count")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Livelihood diversity',
            'Economic variety',
            'How diverse are livelihoods?',
            'Show livelihood diversity'
        ],
        priority=7,
        description='Livelihood diversity across communities',
        tags=['aggregate', 'livelihood', 'diversity']
    ),
    QueryTemplate(
        id='primary_vs_secondary_livelihood',
        category='communities',
        pattern=r'\b(primary|secondary)\s+(vs|versus|compared to)\s+(secondary|primary)\s+livelihood',
        query_template='OBCCommunity.objects.exclude(primary_livelihood__exact="", secondary_livelihood__exact="").values("primary_livelihood", "secondary_livelihood").annotate(count=Count("id"))[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Primary vs secondary livelihood',
            'Primary versus secondary livelihood',
            'Compare primary and secondary livelihoods',
            'Primary livelihood compared to secondary'
        ],
        priority=7,
        description='Comparison of primary and secondary livelihoods',
        tags=['aggregate', 'livelihood', 'comparison']
    ),
    QueryTemplate(
        id='income_levels_distribution',
        category='communities',
        pattern=r'\b(income|earnings?)\s+(levels?|distribution|range)',
        query_template='OBCCommunity.objects.exclude(income_level__exact="").values("income_level").annotate(count=Count("id")).order_by("-count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Income levels',
            'Income distribution',
            'Earnings range',
            'Show income levels'
        ],
        priority=7,
        description='Income level distribution',
        tags=['aggregate', 'livelihood', 'income']
    ),
    QueryTemplate(
        id='livelihood_by_proximity',
        category='communities',
        pattern=r'\b(livelihoods?|economic activities)\s+by\s+proximity\s+to\s+barmm',
        query_template='OBCCommunity.objects.values("proximity_to_barmm", "primary_livelihood").annotate(count=Count("id")).order_by("proximity_to_barmm", "-count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Livelihoods by proximity to BARMM',
            'Economic activities by BARMM proximity',
            'How does proximity affect livelihood?'
        ],
        priority=7,
        description='Livelihood patterns by BARMM proximity',
        tags=['aggregate', 'livelihood', 'proximity']
    ),
    QueryTemplate(
        id='communities_with_multiple_livelihoods',
        category='communities',
        pattern=r'\bcommunities\s+with\s+(multiple|both|dual)\s+livelihoods?',
        query_template='OBCCommunity.objects.exclude(primary_livelihood__exact="", secondary_livelihood__exact="").select_related("barangay__municipality__province")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Communities with multiple livelihoods',
            'Communities with both livelihoods',
            'Dual livelihood communities',
            'Show communities with secondary livelihoods'
        ],
        priority=6,
        description='Communities with both primary and secondary livelihoods',
        tags=['list', 'livelihood', 'multiple']
    ),
]


# =============================================================================
# COMBINE ALL TEMPLATES
# =============================================================================

COMMUNITIES_TEMPLATES = (
    COMMUNITIES_COUNT_TEMPLATES +
    COMMUNITIES_LIST_TEMPLATES +
    COMMUNITIES_AGGREGATE_TEMPLATES +
    COMMUNITIES_FILTER_TEMPLATES +
    COMMUNITIES_DEMOGRAPHIC_TEMPLATES +
    COMMUNITIES_ETHNOLINGUISTIC_TEMPLATES +
    COMMUNITIES_LIVELIHOOD_TEMPLATES
)

# Total: 9 + 5 + 7 + 4 + 12 + 10 + 10 = 57 distinct templates with 130+ example query variations
# Original: 25 templates | Added: 32 templates | New Total: 57 templates
