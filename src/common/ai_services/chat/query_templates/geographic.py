"""
Geographic Query Templates for OBCMS Chat System

Comprehensive templates for querying administrative hierarchy:
- Region → Province → Municipality → Barangay
- 50+ templates covering all geographic intelligence needs
- Fixes critical issue: Users can now list provinces, municipalities, etc.
"""

from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# REGION QUERIES (12 templates)
# =============================================================================

REGION_TEMPLATES = [
    QueryTemplate(
        id='count_all_regions',
        category='geographic',
        pattern=r'\b(how many|count|total|number of)\s+(obc\s+)?regions?\b',
        query_template='Region.objects.count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many regions?',
            'Count regions',
            'Total regions',
            'Number of regions'
        ],
        priority=8,
        description='Count total regions in system',
        result_type='count',
        tags=['count', 'region', 'geographic']
    ),

    QueryTemplate(
        id='list_all_regions',
        category='geographic',
        pattern=r'\b(show|list|display|get|what are)\s+(me\s+)?(the\s+)?(list of\s+)?(all\s+)?regions?\b',
        query_template='Region.objects.all().order_by("name")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me all regions',
            'List regions',
            'Display regions',
            'What are the regions?',
            'Get all regions',
            'Show regions list'
        ],
        priority=10,
        description='List all regions in OBC coverage',
        result_type='list',
        tags=['list', 'region', 'geographic']
    ),

    QueryTemplate(
        id='count_regions_with_obc',
        category='geographic',
        pattern=r'\b(how many|count)\s+regions?\s+(with|having)\s+(obc|communities?|coverage)\b',
        query_template='Region.objects.filter(provinces__municipalities__barangays__obc_communities__isnull=False).distinct().count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many regions with OBC?',
            'Count regions with communities',
            'Regions having OBC presence'
        ],
        priority=9,
        description='Count regions with OBC presence',
        result_type='count',
        tags=['count', 'region', 'obc']
    ),

    QueryTemplate(
        id='region_by_name',
        category='geographic',
        pattern=r'\b(show|get|details|info|information)\s+(me\s+)?(about\s+)?region\s+(?P<region_name>[\w\s]+?)(\?|$)',
        query_template='Region.objects.filter(name__icontains="{region_name}").first()',
        required_entities=['region'],
        optional_entities=[],
        examples=[
            'Show me Region IX',
            'Get Region XII details',
            'Information about Region X',
            'Details of BARMM region'
        ],
        priority=10,
        description='Get specific region details',
        result_type='single',
        tags=['detail', 'region', 'geographic']
    ),

    QueryTemplate(
        id='regions_with_boundaries',
        category='geographic',
        pattern=r'\b(which|what)\s+regions?\s+(have|with)\s+(boundaries?|geojson|geographic data)\b',
        query_template='Region.objects.filter(boundary_geojson__isnull=False)',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Which regions have boundaries?',
            'Regions with GeoJSON',
            'What regions have geographic data?'
        ],
        priority=7,
        description='Regions with GeoJSON boundaries',
        result_type='list',
        tags=['list', 'region', 'boundaries']
    ),

    QueryTemplate(
        id='region_demographics',
        category='geographic',
        pattern=r'\b(show|get)\s+(obc\s+)?population\s+by\s+region\b',
        query_template='Region.objects.annotate(total_pop=Sum("provinces__municipalities__barangays__obc_communities__estimated_obc_population")).order_by("-total_pop")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show population by region',
            'Get OBC population by region',
            'Population breakdown by region'
        ],
        priority=8,
        description='OBC population totals by region',
        result_type='aggregate',
        tags=['aggregate', 'region', 'population']
    ),

    QueryTemplate(
        id='region_communities_count',
        category='geographic',
        pattern=r'\b(show|get|count)\s+(obc\s+)?communities?\s+(per|by|in each)\s+region\b',
        query_template='Region.objects.annotate(community_count=Count("provinces__municipalities__barangays__obc_communities", distinct=True)).order_by("-community_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show communities per region',
            'Get OBC communities by region',
            'Count communities in each region'
        ],
        priority=8,
        description='Community count per region',
        result_type='aggregate',
        tags=['aggregate', 'region', 'communities']
    ),

    QueryTemplate(
        id='region_coverage_analysis',
        category='geographic',
        pattern=r'\b(show|get)\s+(mana\s+)?(assessment|coverage)\s+(by|per)\s+region\b',
        query_template='Region.objects.annotate(assessment_count=Count("provinces__municipalities__barangays__obc_communities__assessments", distinct=True)).order_by("-assessment_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show assessment coverage by region',
            'Get MANA coverage per region',
            'Assessment distribution by region'
        ],
        priority=7,
        description='Assessment coverage by region',
        result_type='aggregate',
        tags=['aggregate', 'region', 'mana']
    ),

    QueryTemplate(
        id='region_ppa_count',
        category='geographic',
        pattern=r'\b(show|get|count)\s+(ppas?|projects?|programs?|activities?)\s+(by|per|in each)\s+region\b',
        query_template='Region.objects.annotate(ppa_count=Count("provinces__municipalities__barangays__obc_communities__activities", distinct=True)).order_by("-ppa_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show PPAs by region',
            'Get projects per region',
            'Count programs in each region'
        ],
        priority=7,
        description='PPA count per region',
        result_type='aggregate',
        tags=['aggregate', 'region', 'ppa']
    ),

    QueryTemplate(
        id='region_budget_allocation',
        category='geographic',
        pattern=r'\b(show|get)\s+budget\s+(allocation|by)\s+region\b',
        query_template='Region.objects.annotate(total_budget=Sum("provinces__municipalities__barangays__obc_communities__activities__budget_allocated")).order_by("-total_budget")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show budget allocation by region',
            'Get budget by region',
            'Budget distribution per region'
        ],
        priority=7,
        description='Budget allocation by region',
        result_type='aggregate',
        tags=['aggregate', 'region', 'budget']
    ),

    QueryTemplate(
        id='region_needs_count',
        category='geographic',
        pattern=r'\b(show|get|count)\s+(identified\s+)?needs?\s+(by|per|in each)\s+region\b',
        query_template='Region.objects.annotate(needs_count=Count("provinces__municipalities__barangays__obc_communities__needs", distinct=True)).order_by("-needs_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show identified needs by region',
            'Get needs per region',
            'Count needs in each region'
        ],
        priority=7,
        description='Identified needs count by region',
        result_type='aggregate',
        tags=['aggregate', 'region', 'needs']
    ),

    QueryTemplate(
        id='regions_by_population_density',
        category='geographic',
        pattern=r'\b(rank|sort|order)\s+regions?\s+by\s+(obc\s+)?population\b',
        query_template='Region.objects.annotate(total_pop=Sum("provinces__municipalities__barangays__obc_communities__estimated_obc_population")).order_by("-total_pop")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Rank regions by OBC population',
            'Sort regions by population',
            'Order regions by OBC population'
        ],
        priority=8,
        description='Regions ranked by OBC population',
        result_type='aggregate',
        tags=['aggregate', 'region', 'ranking']
    ),
]


# =============================================================================
# PROVINCE QUERIES (12 templates)
# =============================================================================

PROVINCE_TEMPLATES = [
    QueryTemplate(
        id='count_all_provinces',
        category='geographic',
        pattern=r'\b(how many|count|total|number of)\s+(obc\s+)?provinces?\b',
        query_template='Province.objects.count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many provinces?',
            'Count provinces',
            'Total provinces',
            'Number of provinces'
        ],
        priority=8,
        description='Count total provinces in system',
        result_type='count',
        tags=['count', 'province', 'geographic']
    ),

    QueryTemplate(
        id='list_all_provinces',
        category='geographic',
        pattern=r'\b(show|list|display|get|what are)\s+(me\s+)?(the\s+)?(list of\s+)?(all\s+)?provinces?\b',
        query_template='Province.objects.all().order_by("region__name", "name")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me all provinces',
            'List provinces',
            'Display provinces',
            'What are the provinces?',
            'Get all provinces',
            'Show the list of provinces',
            'Show me the list of province'
        ],
        priority=10,
        description='List all provinces with region grouping',
        result_type='list',
        tags=['list', 'province', 'geographic']
    ),

    QueryTemplate(
        id='count_provinces_by_region',
        category='geographic',
        pattern=r'\b(how many|count)\s+provinces?\s+(in|at|within|under)\s+(?P<region_name>[\w\s]+?)(\?|$)',
        query_template='Province.objects.filter(region__name__icontains="{region_name}").count()',
        required_entities=['region'],
        optional_entities=[],
        examples=[
            'How many provinces in Region IX?',
            'Count provinces in Region XII',
            'Provinces within BARMM'
        ],
        priority=10,
        description='Count provinces in specific region',
        result_type='count',
        tags=['count', 'province', 'region']
    ),

    QueryTemplate(
        id='list_provinces_by_region',
        category='geographic',
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(the\s+)?provinces?\s+(in|at|within|under|of)\s+(?P<region_name>[\w\s]+?)(\?|$)',
        query_template='Province.objects.filter(region__name__icontains="{region_name}").order_by("name")',
        required_entities=['region'],
        optional_entities=[],
        examples=[
            'Show provinces in Region IX',
            'List provinces of Region XII',
            'Display provinces in BARMM',
            'Get provinces within Region X'
        ],
        priority=10,
        description='List provinces in specific region',
        result_type='list',
        tags=['list', 'province', 'region']
    ),

    QueryTemplate(
        id='province_by_name',
        category='geographic',
        pattern=r'\b(show|get|details|info|information)\s+(me\s+)?(about\s+)?(?P<province_name>[\w\s]+?)\s+province\b',
        query_template='Province.objects.filter(name__icontains="{province_name}").first()',
        required_entities=['province'],
        optional_entities=[],
        examples=[
            'Show me Zamboanga del Sur province',
            'Get Cotabato province details',
            'Information about Sultan Kudarat province'
        ],
        priority=10,
        description='Get specific province details',
        result_type='single',
        tags=['detail', 'province', 'geographic']
    ),

    QueryTemplate(
        id='provinces_with_boundaries',
        category='geographic',
        pattern=r'\b(which|what)\s+provinces?\s+(have|with)\s+(boundaries?|geojson|geographic data)\b',
        query_template='Province.objects.filter(boundary_geojson__isnull=False)',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Which provinces have boundaries?',
            'Provinces with GeoJSON',
            'What provinces have geographic data?'
        ],
        priority=7,
        description='Provinces with GeoJSON boundaries',
        result_type='list',
        tags=['list', 'province', 'boundaries']
    ),

    QueryTemplate(
        id='province_demographics',
        category='geographic',
        pattern=r'\b(show|get)\s+(obc\s+)?population\s+by\s+province\b',
        query_template='Province.objects.annotate(total_pop=Sum("municipalities__barangays__obc_communities__estimated_obc_population")).order_by("-total_pop")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show population by province',
            'Get OBC population by province',
            'Population breakdown by province'
        ],
        priority=8,
        description='OBC population totals by province',
        result_type='aggregate',
        tags=['aggregate', 'province', 'population']
    ),

    QueryTemplate(
        id='province_communities_count',
        category='geographic',
        pattern=r'\b(show|get|count)\s+(obc\s+)?communities?\s+(per|by|in each)\s+province\b',
        query_template='Province.objects.annotate(community_count=Count("municipalities__barangays__obc_communities", distinct=True)).order_by("-community_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show communities per province',
            'Get OBC communities by province',
            'Count communities in each province'
        ],
        priority=8,
        description='Community count per province',
        result_type='aggregate',
        tags=['aggregate', 'province', 'communities']
    ),

    QueryTemplate(
        id='province_coverage_analysis',
        category='geographic',
        pattern=r'\b(show|get)\s+(mana\s+)?(assessment|coverage)\s+(by|per)\s+province\b',
        query_template='Province.objects.annotate(assessment_count=Count("municipalities__barangays__obc_communities__assessments", distinct=True)).order_by("-assessment_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show assessment coverage by province',
            'Get MANA coverage per province',
            'Assessment distribution by province'
        ],
        priority=7,
        description='Assessment coverage by province',
        result_type='aggregate',
        tags=['aggregate', 'province', 'mana']
    ),

    QueryTemplate(
        id='province_ppa_count',
        category='geographic',
        pattern=r'\b(show|get|count)\s+(ppas?|projects?|programs?|activities?)\s+(by|per|in each)\s+province\b',
        query_template='Province.objects.annotate(ppa_count=Count("municipalities__barangays__obc_communities__activities", distinct=True)).order_by("-ppa_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show PPAs by province',
            'Get projects per province',
            'Count programs in each province'
        ],
        priority=7,
        description='PPA count per province',
        result_type='aggregate',
        tags=['aggregate', 'province', 'ppa']
    ),

    QueryTemplate(
        id='province_budget_allocation',
        category='geographic',
        pattern=r'\b(show|get)\s+budget\s+(allocation|by)\s+province\b',
        query_template='Province.objects.annotate(total_budget=Sum("municipalities__barangays__obc_communities__activities__budget_allocated")).order_by("-total_budget")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show budget allocation by province',
            'Get budget by province',
            'Budget distribution per province'
        ],
        priority=7,
        description='Budget allocation by province',
        result_type='aggregate',
        tags=['aggregate', 'province', 'budget']
    ),

    QueryTemplate(
        id='provinces_by_obc_population',
        category='geographic',
        pattern=r'\b(rank|sort|order)\s+provinces?\s+by\s+(obc\s+)?population\b',
        query_template='Province.objects.annotate(total_pop=Sum("municipalities__barangays__obc_communities__estimated_obc_population")).order_by("-total_pop")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Rank provinces by OBC population',
            'Sort provinces by population',
            'Order provinces by OBC population'
        ],
        priority=8,
        description='Provinces ranked by OBC population',
        result_type='aggregate',
        tags=['aggregate', 'province', 'ranking']
    ),
]


# =============================================================================
# MUNICIPALITY QUERIES (12 templates)
# =============================================================================

MUNICIPALITY_TEMPLATES = [
    QueryTemplate(
        id='count_all_municipalities',
        category='geographic',
        pattern=r'\b(how many|count|total|number of)\s+municipalities\b',
        query_template='Municipality.objects.filter(municipality_type="municipality").count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many municipalities?',
            'Count municipalities',
            'Number of municipalities'
        ],
        priority=15,  # CRITICAL: Higher than all community templates
        description='Count municipalities only (excluding cities)',
        result_type='count',
        tags=['count', 'municipality', 'geographic']
    ),

    QueryTemplate(
        id='count_cities_only_geographic',
        category='geographic',
        pattern=r'\b(how many|count|total|number of)\s+cities\b',
        query_template='Municipality.objects.exclude(municipality_type=\"municipality\").count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many cities?',
            'Count cities',
            'Total cities',
            'Number of cities'
        ],
        priority=15,  # Same as municipalities for consistency
        description='Count cities only (excluding regular municipalities)',
        result_type='count',
        tags=['count', 'city', 'geographic']
    ),

    QueryTemplate(
        id='list_all_municipalities',
        category='geographic',
        pattern=r'\b(show|list|display|get|what are)\s+(me\s+)?(the\s+)?(list of\s+)?(all\s+)?(municipalities|cities)\b',
        query_template='Municipality.objects.all().order_by("province__name", "name")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me all municipalities',
            'List municipalities',
            'Display cities',
            'What are the municipalities?',
            'Get all municipalities',
            'Show municipalities list'
        ],
        priority=10,
        description='List all municipalities/cities with province grouping',
        result_type='list',
        tags=['list', 'municipality', 'geographic']
    ),

    QueryTemplate(
        id='count_municipalities_by_province',
        category='geographic',
        pattern=r'\b(how many|count)\s+(municipalities|cities)\s+(in|at|within|under)\s+(?P<province_name>[\w\s]+?)(\?|$)',
        query_template='Municipality.objects.filter(province__name__icontains="{province_name}").count()',
        required_entities=['province'],
        optional_entities=[],
        examples=[
            'How many municipalities in Cotabato?',
            'Count cities in Zamboanga del Sur',
            'Municipalities within Sultan Kudarat'
        ],
        priority=10,
        description='Count municipalities in specific province',
        result_type='count',
        tags=['count', 'municipality', 'province']
    ),

    QueryTemplate(
        id='list_municipalities_by_province',
        category='geographic',
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(the\s+)?(municipalities|cities)\s+(in|at|within|under|of)\s+(?P<province_name>[\w\s]+?)(\?|$)',
        query_template='Municipality.objects.filter(province__name__icontains="{province_name}").order_by("name")',
        required_entities=['province'],
        optional_entities=[],
        examples=[
            'Show municipalities in Cotabato',
            'List cities of Sultan Kudarat',
            'Display municipalities within Zamboanga del Sur',
            'Get municipalities in Cotabato province'
        ],
        priority=10,
        description='List municipalities in specific province',
        result_type='list',
        tags=['list', 'municipality', 'province']
    ),

    QueryTemplate(
        id='municipality_by_name',
        category='geographic',
        pattern=r'\b(show|get|details|info|information)\s+(me\s+)?(about\s+)?(?P<municipality_name>[\w\s]+?)\s+(municipality|city)\b',
        query_template='Municipality.objects.filter(name__icontains="{municipality_name}").first()',
        required_entities=['municipality'],
        optional_entities=[],
        examples=[
            'Show me Pagadian City',
            'Get Cotabato City details',
            'Information about Tacurong municipality'
        ],
        priority=10,
        description='Get specific municipality details',
        result_type='single',
        tags=['detail', 'municipality', 'geographic']
    ),

    QueryTemplate(
        id='municipalities_by_urban_rural',
        category='geographic',
        pattern=r'\b(show|list)\s+(urban|rural)\s+(municipalities|cities)\b',
        query_template='Municipality.objects.filter(is_urban={"urban": "True", "rural": "False"}["{classification}"])',
        required_entities=['urban_rural_classification'],
        optional_entities=[],
        examples=[
            'Show urban municipalities',
            'List rural cities',
            'Display urban areas'
        ],
        priority=7,
        description='Municipalities by urban/rural classification',
        result_type='list',
        tags=['list', 'municipality', 'classification']
    ),

    QueryTemplate(
        id='municipality_demographics',
        category='geographic',
        pattern=r'\b(show|get)\s+(obc\s+)?population\s+by\s+municipality\b',
        query_template='Municipality.objects.annotate(total_pop=Sum("barangays__obc_communities__estimated_obc_population")).order_by("-total_pop")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show population by municipality',
            'Get OBC population by municipality',
            'Population breakdown by municipality'
        ],
        priority=8,
        description='OBC population totals by municipality',
        result_type='aggregate',
        tags=['aggregate', 'municipality', 'population']
    ),

    QueryTemplate(
        id='municipality_communities_count',
        category='geographic',
        pattern=r'\b(show|get|count)\s+(obc\s+)?communities?\s+(per|by|in each)\s+municipality\b',
        query_template='Municipality.objects.annotate(community_count=Count("barangays__obc_communities", distinct=True)).order_by("-community_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show communities per municipality',
            'Get OBC communities by municipality',
            'Count communities in each municipality'
        ],
        priority=8,
        description='Community count per municipality',
        result_type='aggregate',
        tags=['aggregate', 'municipality', 'communities']
    ),

    QueryTemplate(
        id='municipality_ppa_count',
        category='geographic',
        pattern=r'\b(show|get|count)\s+(ppas?|projects?|programs?|activities?)\s+(by|per|in each)\s+municipality\b',
        query_template='Municipality.objects.annotate(ppa_count=Count("barangays__obc_communities__activities", distinct=True)).order_by("-ppa_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show PPAs by municipality',
            'Get projects per municipality',
            'Count programs in each municipality'
        ],
        priority=7,
        description='PPA count per municipality',
        result_type='aggregate',
        tags=['aggregate', 'municipality', 'ppa']
    ),

    QueryTemplate(
        id='municipality_budget',
        category='geographic',
        pattern=r'\b(show|get)\s+budget\s+(by|per)\s+municipality\b',
        query_template='Municipality.objects.annotate(total_budget=Sum("barangays__obc_communities__activities__budget_allocated")).order_by("-total_budget")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show budget by municipality',
            'Get budget per municipality',
            'Budget distribution by municipality'
        ],
        priority=7,
        description='Budget allocation by municipality',
        result_type='aggregate',
        tags=['aggregate', 'municipality', 'budget']
    ),

    QueryTemplate(
        id='municipalities_with_high_obc',
        category='geographic',
        pattern=r'\b(show|list)\s+municipalities?\s+with\s+(high|over|more than)\s+(?P<threshold>\d+)\s+(obc\s+)?population\b',
        query_template='Municipality.objects.annotate(total_pop=Sum("barangays__obc_communities__estimated_obc_population")).filter(total_pop__gt={threshold}).order_by("-total_pop")',
        required_entities=['population_threshold'],
        optional_entities=[],
        examples=[
            'Show municipalities with high OBC population',
            'List municipalities with over 1000 OBC population',
            'Municipalities with more than 500 OBC'
        ],
        priority=7,
        description='Municipalities above population threshold',
        result_type='list',
        tags=['list', 'municipality', 'population']
    ),

    QueryTemplate(
        id='municipalities_administrative_data',
        category='geographic',
        pattern=r'\b(show|get)\s+administrative\s+(data|info|information)\s+for\s+municipalities\b',
        query_template='Municipality.objects.all().select_related("province__region")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show administrative data for municipalities',
            'Get administrative info for municipalities',
            'Municipality administrative information'
        ],
        priority=6,
        description='Administrative information for municipalities',
        result_type='list',
        tags=['list', 'municipality', 'administrative']
    ),
]


# =============================================================================
# BARANGAY QUERIES (8 templates)
# =============================================================================

BARANGAY_TEMPLATES = [
    QueryTemplate(
        id='count_all_barangays',
        category='geographic',
        pattern=r'\b(how many|count|total|number of)\s+(obc\s+)?barangays?\b',
        query_template='Barangay.objects.count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many barangays?',
            'Count barangays',
            'Total barangays',
            'Number of barangays'
        ],
        priority=8,
        description='Count total barangays in system',
        result_type='count',
        tags=['count', 'barangay', 'geographic']
    ),

    QueryTemplate(
        id='list_all_barangays',
        category='geographic',
        pattern=r'\b(show|list|display|get|what are)\s+(me\s+)?(the\s+)?(list of\s+)?(all\s+)?barangays?\b',
        query_template='Barangay.objects.all().order_by("municipality__name", "name")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me all barangays',
            'List barangays',
            'Display barangays',
            'What are the barangays?',
            'Get all barangays'
        ],
        priority=10,
        description='List all barangays with municipality grouping',
        result_type='list',
        tags=['list', 'barangay', 'geographic']
    ),

    QueryTemplate(
        id='count_barangays_by_municipality',
        category='geographic',
        pattern=r'\b(how many|count)\s+barangays?\s+(in|at|within|under)\s+(?P<municipality_name>[\w\s]+?)(\?|$)',
        query_template='Barangay.objects.filter(municipality__name__icontains="{municipality_name}").count()',
        required_entities=['municipality'],
        optional_entities=[],
        examples=[
            'How many barangays in Pagadian?',
            'Count barangays in Cotabato City',
            'Barangays within Tacurong'
        ],
        priority=10,
        description='Count barangays in specific municipality',
        result_type='count',
        tags=['count', 'barangay', 'municipality']
    ),

    QueryTemplate(
        id='list_barangays_by_municipality',
        category='geographic',
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(the\s+)?barangays?\s+(in|at|within|under|of)\s+(?P<municipality_name>[\w\s]+?)(\?|$)',
        query_template='Barangay.objects.filter(municipality__name__icontains="{municipality_name}").order_by("name")',
        required_entities=['municipality'],
        optional_entities=[],
        examples=[
            'Show barangays in Pagadian',
            'List barangays of Cotabato City',
            'Display barangays within Tacurong',
            'Get barangays in Zamboanga City'
        ],
        priority=10,
        description='List barangays in specific municipality',
        result_type='list',
        tags=['list', 'barangay', 'municipality']
    ),

    QueryTemplate(
        id='barangay_by_name',
        category='geographic',
        pattern=r'\b(show|get|details|info|information)\s+(me\s+)?(about\s+)?barangay\s+(?P<barangay_name>[\w\s]+?)(\?|$)',
        query_template='Barangay.objects.filter(name__icontains="{barangay_name}").first()',
        required_entities=['barangay'],
        optional_entities=[],
        examples=[
            'Show me Barangay Poblacion',
            'Get Barangay Matina details',
            'Information about Barangay Rosary Heights'
        ],
        priority=10,
        description='Get specific barangay details',
        result_type='single',
        tags=['detail', 'barangay', 'geographic']
    ),

    QueryTemplate(
        id='barangays_with_obc',
        category='geographic',
        pattern=r'\b(which|what)\s+barangays?\s+(have|with)\s+(obc|communities?)\b',
        query_template='Barangay.objects.filter(obc_communities__isnull=False).distinct()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Which barangays have OBC?',
            'Barangays with communities',
            'What barangays have OBC presence?'
        ],
        priority=9,
        description='Barangays with OBC communities',
        result_type='list',
        tags=['list', 'barangay', 'obc']
    ),

    QueryTemplate(
        id='barangay_demographics',
        category='geographic',
        pattern=r'\b(show|get)\s+(obc\s+)?population\s+by\s+barangay\b',
        query_template='Barangay.objects.annotate(total_pop=Sum("obc_communities__estimated_obc_population")).order_by("-total_pop")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show population by barangay',
            'Get OBC population by barangay',
            'Population breakdown by barangay'
        ],
        priority=8,
        description='OBC population totals by barangay',
        result_type='aggregate',
        tags=['aggregate', 'barangay', 'population']
    ),

    QueryTemplate(
        id='barangays_with_coordinates',
        category='geographic',
        pattern=r'\b(which|what)\s+barangays?\s+(have|with)\s+(coordinates?|gps|location data)\b',
        query_template='Barangay.objects.filter(center_coordinates__isnull=False)',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Which barangays have coordinates?',
            'Barangays with GPS',
            'What barangays have location data?'
        ],
        priority=7,
        description='Barangays with GPS coordinates',
        result_type='list',
        tags=['list', 'barangay', 'coordinates']
    ),
]


# =============================================================================
# CROSS-LEVEL GEOGRAPHIC QUERIES (6 templates)
# =============================================================================

CROSS_LEVEL_TEMPLATES = [
    QueryTemplate(
        id='administrative_hierarchy',
        category='geographic',
        pattern=r'\b(show|display|get)\s+(administrative\s+)?hierarchy\b',
        query_template='Region.objects.all().prefetch_related("provinces__municipalities__barangays")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show administrative hierarchy',
            'Display hierarchy',
            'Get administrative structure'
        ],
        priority=8,
        description='Full administrative hierarchy: Region → Province → Municipality → Barangay',
        result_type='list',
        tags=['list', 'geographic', 'hierarchy']
    ),

    QueryTemplate(
        id='geographic_coverage_gaps',
        category='geographic',
        pattern=r'\b(show|find|identify|display)\s+(geographic\s+)?(coverage\s+)?gaps?\b',
        query_template='Municipality.objects.annotate(community_count=Count("barangays__obc_communities")).filter(community_count=0)',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show geographic coverage gaps',
            'Find gaps in coverage',
            'Identify administrative units without OBC',
            'Show coverage gaps',
            'Find geographic gaps',
            'Display coverage gaps'
        ],
        priority=7,
        description='Administrative units without OBC presence',
        result_type='list',
        tags=['list', 'geographic', 'gaps']
    ),

    QueryTemplate(
        id='geographic_rollup_summary',
        category='geographic',
        pattern=r'\b(show|get)\s+(geographic|administrative)\s+summary\b',
        query_template='{"regions": Region.objects.count(), "provinces": Province.objects.count(), "municipalities": Municipality.objects.count(), "barangays": Barangay.objects.count()}',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show geographic summary',
            'Get administrative summary',
            'Geographic rollup'
        ],
        priority=8,
        description='Summary stats rolled up by administrative level',
        result_type='aggregate',
        tags=['aggregate', 'geographic', 'summary']
    ),

    QueryTemplate(
        id='adjacent_administrative_units',
        category='geographic',
        pattern=r'\b(show|find|get)\s+(adjacent|neighboring)\s+(provinces?|municipalities?)\s+(to|near)\s+(?P<location_name>[\w\s]+?)(\?|$)',
        query_template='# Adjacent units query requires spatial analysis',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Show adjacent provinces to Cotabato',
            'Find neighboring municipalities to Pagadian',
            'Get provinces near Sultan Kudarat'
        ],
        priority=6,
        description='Find adjacent administrative units (requires GeoJSON)',
        result_type='list',
        tags=['list', 'geographic', 'spatial']
    ),

    QueryTemplate(
        id='geographic_comparison',
        category='geographic',
        pattern=r'\b(compare|contrast)\s+(?P<location1>[\w\s]+?)\s+(vs|versus|and)\s+(?P<location2>[\w\s]+?)(\?|$)',
        query_template='# Comparison query - extract stats for both locations',
        required_entities=['location', 'location'],
        optional_entities=[],
        examples=[
            'Compare Region IX vs Region X',
            'Contrast Cotabato and Sultan Kudarat',
            'Compare Zamboanga del Sur and Zamboanga del Norte'
        ],
        priority=7,
        description='Compare two geographic areas',
        result_type='aggregate',
        tags=['aggregate', 'geographic', 'comparison']
    ),

    QueryTemplate(
        id='administrative_boundaries_export',
        category='geographic',
        pattern=r'\b(export|download|get)\s+(administrative\s+)?boundaries?|boundaries?\s+(geojson|data|export)\b',
        query_template='{"regions": Region.objects.filter(boundary_geojson__isnull=False), "provinces": Province.objects.filter(boundary_geojson__isnull=False)}',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Export administrative boundaries',
            'Download GeoJSON boundaries',
            'Get boundary data',
            'Export boundaries',
            'Download boundaries'
        ],
        priority=6,
        description='Export GeoJSON boundaries for mapping',
        result_type='list',
        tags=['list', 'geographic', 'export']
    ),
]


# =============================================================================
# LOCATION INFORMATION QUERIES (8 templates)
# =============================================================================

LOCATION_INFO_TEMPLATES = [
    QueryTemplate(
        id='province_location_info',
        category='geographic',
        pattern=r'\b(where is|what region is|which region|location of)\s+(?P<province_name>[\w\s]+?)\s+(province|prov)?\b',
        query_template='Province.objects.filter(name__icontains="{province_name}").values("name", "region__name").first()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Where is Cotabato province?',
            'What region is Zamboanga del Norte?',
            'Which region is Bukidnon in?',
            'Location of Davao del Sur province'
        ],
        priority=12,
        description='Get region location information for a province',
        result_type='single',
        tags=['location', 'province', 'region', 'info']
    ),
    QueryTemplate(
        id='municipality_location_info',
        category='geographic',
        pattern=r'\b(where is|what province is|which province|location of)\s+(?P<municipality_name>[\w\s]+?)\s+(municipality|city|muni)?\b',
        query_template='Municipality.objects.filter(name__icontains="{municipality_name}").values("name", "province__name", "province__region__name").first()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Where is Zamboanga City?',
            'What province is Cotabato City in?',
            'Which province is Marawi in?',
            'Location of Dipolog municipality'
        ],
        priority=12,
        description='Get province and region location information for a municipality/city',
        result_type='single',
        tags=['location', 'municipality', 'province', 'info']
    ),
    QueryTemplate(
        id='barangay_location_info',
        category='geographic',
        pattern=r'\b(where is|what municipality is|which municipality|location of)\s+(?P<barangay_name>[\w\s]+?)\s+(barangay|brgy)?\b',
        query_template='Barangay.objects.filter(name__icontains="{barangay_name}").values("name", "municipality__name", "municipality__province__name").first()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Where is Barangay Poblacion?',
            'What municipality is Brgy. San Jose in?',
            'Which municipality is Barangay Riverside in?',
            'Location of Barangay Bagua'
        ],
        priority=12,
        description='Get municipality and province location information for a barangay',
        result_type='single',
        tags=['location', 'barangay', 'municipality', 'info']
    ),
]

# =============================================================================
# COMBINE ALL GEOGRAPHIC TEMPLATES
# =============================================================================

GEOGRAPHIC_TEMPLATES = (
    REGION_TEMPLATES +
    PROVINCE_TEMPLATES +
    MUNICIPALITY_TEMPLATES +
    BARANGAY_TEMPLATES +
    CROSS_LEVEL_TEMPLATES +
    LOCATION_INFO_TEMPLATES
)

# Total: 53 templates
# - Region: 12 templates
# - Province: 12 templates
# - Municipality: 12 templates
# - Barangay: 8 templates
# - Cross-level: 6 templates
# - Location info: 3 templates
