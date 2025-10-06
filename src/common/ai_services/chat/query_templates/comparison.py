"""
Comparison Query Templates for OBCMS Chat System

20 templates for comparative analysis including:
- Location comparisons (region vs region, provinces, municipalities)
- Ethnicity comparisons (demographics, needs, outcomes)
- Metric comparisons (efficiency, success rates, costs)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# LOCATION COMPARISON QUERIES (8 templates)
# =============================================================================

COMPARISON_LOCATION_TEMPLATES = [
    QueryTemplate(
        id='region_vs_region',
        category='comparison',
        pattern=r'\bregion\s+(?P<region1>[\w\s]+)\s+(vs|versus|compared to)\s+region\s+(?P<region2>[\w\s]+)',
        query_template='OBCCommunity.objects.filter(Q(barangay__municipality__province__region__name__icontains="{region1}") | Q(barangay__municipality__province__region__name__icontains="{region2}")).values("barangay__municipality__province__region__name").annotate(communities=Count("id"), total_pop=Sum("estimated_obc_population"), avg_households=Avg("households"))',
        required_entities=['locations'],
        optional_entities=[],
        examples=[
            'Compare Region IX vs Region X',
            'Region IX versus Region XII',
            'Region X compared to Region XI',
            'Compare Regions IX and X'
        ],
        priority=9,
        description='Compare two regions',
        tags=['comparison', 'location', 'regions']
    ),
    QueryTemplate(
        id='province_vs_province',
        category='comparison',
        pattern=r'\bprovince\s+(?P<province1>[\w\s]+)\s+(vs|versus|compared to)\s+province\s+(?P<province2>[\w\s]+)',
        query_template='OBCCommunity.objects.filter(Q(barangay__municipality__province__name__icontains="{province1}") | Q(barangay__municipality__province__name__icontains="{province2}")).values("barangay__municipality__province__name").annotate(communities=Count("id"), total_pop=Sum("estimated_obc_population"))',
        required_entities=['locations'],
        optional_entities=[],
        examples=[
            'Compare provinces',
            'Zamboanga del Sur vs Cotabato',
            'Province comparison',
            'Compare two provinces'
        ],
        priority=9,
        description='Compare two provinces',
        tags=['comparison', 'location', 'provinces']
    ),
    QueryTemplate(
        id='municipality_comparison',
        category='comparison',
        pattern=r'\bmunicipality\s+(?P<muni1>[\w\s]+)\s+(vs|versus|compared to)\s+(?P<muni2>[\w\s]+)',
        query_template='OBCCommunity.objects.filter(Q(barangay__municipality__name__icontains="{muni1}") | Q(barangay__municipality__name__icontains="{muni2}")).values("barangay__municipality__name").annotate(communities=Count("id"), total_pop=Sum("estimated_obc_population"), assessments=Count("assessments"))',
        required_entities=['locations'],
        optional_entities=[],
        examples=[
            'Compare municipalities',
            'Municipality A vs Municipality B',
            'Compare two municipalities',
            'Municipality comparison'
        ],
        priority=8,
        description='Compare two municipalities',
        tags=['comparison', 'location', 'municipalities']
    ),
    QueryTemplate(
        id='multi_location_comparison',
        category='comparison',
        pattern=r'\bcompare\s+(3\+|multiple|several)\s+(locations?|regions?|provinces?)',
        query_template='{model}.objects.filter({location_filters}).values("{location_field}").annotate(count=Count("id"), total=Sum("{value_field}"), average=Avg("{value_field}")).order_by("-count")',
        required_entities=['locations'],
        optional_entities=['model_type'],
        examples=[
            'Compare 3+ locations',
            'Compare multiple regions',
            'Multi-location comparison',
            'Compare several provinces'
        ],
        priority=8,
        description='Compare multiple locations',
        tags=['comparison', 'location', 'multi']
    ),
    QueryTemplate(
        id='location_ranking',
        category='comparison',
        pattern=r'\b(rank|ranking)\s+(regions?|provinces?|municipalities?)\s+by\s+(?P<metric>[\w\s]+)',
        query_template='{model}.objects.values("{location_field}").annotate(metric_value=Sum("{metric_field}")).order_by("-metric_value")',
        required_entities=['location_level', 'metric'],
        optional_entities=['model_type'],
        examples=[
            'Rank regions by metric',
            'Ranking provinces by population',
            'Rank municipalities by assessments',
            'Location ranking'
        ],
        priority=8,
        description='Rank locations by metric',
        tags=['comparison', 'location', 'ranking']
    ),
    QueryTemplate(
        id='location_benchmarking',
        category='comparison',
        pattern=r'\bbenchmark\s+(against|vs)\s+(average|national|regional)',
        query_template='{model}.objects.values("{location_field}").annotate(location_value=Avg("{metric_field}")).annotate(overall_avg=Avg("{metric_field}"), deviation=F("location_value") - F("overall_avg"))',
        required_entities=['location', 'metric'],
        optional_entities=['model_type'],
        examples=[
            'Benchmark against average',
            'Compare to national average',
            'Regional benchmarking',
            'Performance vs average'
        ],
        priority=7,
        description='Benchmark location against average',
        tags=['comparison', 'location', 'benchmark']
    ),
    QueryTemplate(
        id='location_gap_analysis',
        category='comparison',
        pattern=r'\bgap\s+(between|analysis)\s+(locations?|regions?)',
        query_template='{model}.objects.values("{location_field}").annotate(metric_value={metric_calculation}).aggregate(max_value=Max("metric_value"), min_value=Min("metric_value"), gap=Max("metric_value") - Min("metric_value"))',
        required_entities=['locations', 'metric'],
        optional_entities=['model_type'],
        examples=[
            'Gap between locations',
            'Regional gap analysis',
            'Location disparity',
            'Inequality between regions'
        ],
        priority=7,
        description='Gap analysis between locations',
        tags=['comparison', 'location', 'gap']
    ),
    QueryTemplate(
        id='location_performance_matrix',
        category='comparison',
        pattern=r'\bperformance\s+(matrix|comparison)\s+(by|across)\s+locations?',
        query_template='{model}.objects.values("{location_field}").annotate(metric1=Avg("{metric1_field}"), metric2=Avg("{metric2_field}"), metric3=Count("id")).order_by("{location_field}")',
        required_entities=['locations', 'metrics'],
        optional_entities=['model_type'],
        examples=[
            'Performance comparison matrix',
            'Multi-metric location comparison',
            'Location performance grid',
            'Compare locations across metrics'
        ],
        priority=7,
        description='Performance matrix across locations',
        tags=['comparison', 'location', 'matrix']
    ),
]


# =============================================================================
# ETHNICITY COMPARISON QUERIES (6 templates)
# =============================================================================

COMPARISON_ETHNICITY_TEMPLATES = [
    QueryTemplate(
        id='ethnicity_demographics',
        category='comparison',
        pattern=r'\b(compare\s+)?(ethnic|ethnicity|ethnolinguistic)\s+(groups?\s*)?(demographics?|demographic|characteristics)?',
        query_template='OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(communities=Count("id"), total_pop=Sum("estimated_obc_population"), avg_households=Avg("households"), children=Sum("children_0_9"), youth=Sum("youth_15_30"), seniors=Sum("seniors_60_plus")).order_by("-total_pop")',
        required_entities=[],
        optional_entities=['ethnolinguistic_groups'],
        examples=[
            'Compare ethnic groups demographics',
            'Ethnicity demographic comparison',
            'Compare Maranao vs Tausug demographics',
            'Ethnic group characteristics'
        ],
        priority=8,
        description='Compare demographics by ethnic group',
        tags=['comparison', 'ethnicity', 'demographics']
    ),
    QueryTemplate(
        id='ethnicity_needs',
        category='comparison',
        pattern=r'\bneeds?\s+by\s+(ethnic|ethnolinguistic)\s+group',
        query_template='OBCCommunity.objects.filter(assessments__identified_needs__isnull=False).values("primary_ethnolinguistic_group").annotate(communities=Count("id", distinct=True), total_needs=Count("assessments__identified_needs"), needs_per_community=Count("assessments__identified_needs") / Count("id", distinct=True)).order_by("-total_needs")',
        required_entities=[],
        optional_entities=['ethnolinguistic_groups'],
        examples=[
            'Needs by ethnic group',
            'Compare needs across ethnicities',
            'Ethnic group needs analysis',
            'Which ethnic groups have most needs?'
        ],
        priority=8,
        description='Needs comparison by ethnic group',
        tags=['comparison', 'ethnicity', 'needs']
    ),
    QueryTemplate(
        id='ethnicity_outcomes',
        category='comparison',
        pattern=r'\boutcomes?\s+by\s+(ethnic|ethnolinguistic)\s+group',
        query_template='OBCCommunity.objects.filter(assessments__isnull=False).values("primary_ethnolinguistic_group").annotate(communities=Count("id"), assessments_completed=Count("assessments", filter=Q(assessments__status="completed")), ppas_benefiting=Count("assessments__identified_needs__addressing_ppas", distinct=True)).order_by("-ppas_benefiting")',
        required_entities=[],
        optional_entities=['ethnolinguistic_groups'],
        examples=[
            'Outcomes by ethnic group',
            'Compare ethnic group outcomes',
            'Success rates by ethnicity',
            'Ethnic group impact'
        ],
        priority=7,
        description='Outcomes comparison by ethnic group',
        tags=['comparison', 'ethnicity', 'outcomes']
    ),
    QueryTemplate(
        id='ethnicity_coverage',
        category='comparison',
        pattern=r'\b(service\s+)?coverage\s+by\s+(ethnic|ethnolinguistic)\s+group',
        query_template='OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(total_communities=Count("id"), assessed_communities=Count("id", filter=Q(assessments__isnull=False)), with_ppas=Count("id", filter=Q(assessments__identified_needs__addressing_ppas__isnull=False)), coverage_rate=100.0 * Count("id", filter=Q(assessments__isnull=False)) / Count("id")).order_by("-coverage_rate")',
        required_entities=[],
        optional_entities=['ethnolinguistic_groups'],
        examples=[
            'Service coverage by ethnic group',
            'Coverage by ethnicity',
            'Which ethnic groups are underserved?',
            'Ethnic group access rates'
        ],
        priority=8,
        description='Service coverage by ethnic group',
        tags=['comparison', 'ethnicity', 'coverage']
    ),
    QueryTemplate(
        id='ethnicity_participation',
        category='comparison',
        pattern=r'\bparticipation\s+rates?\s+by\s+(ethnic|ethnolinguistic)\s+group',
        query_template='Assessment.objects.values("community__primary_ethnolinguistic_group").annotate(assessments=Count("id"), avg_participants=Avg("participant_count"), engagement_rate=Avg("participation_rate")).order_by("-engagement_rate")',
        required_entities=[],
        optional_entities=['ethnolinguistic_groups'],
        examples=[
            'Participation rates by ethnicity',
            'Ethnic group engagement',
            'Compare participation across ethnicities',
            'Engagement by ethnic group'
        ],
        priority=7,
        description='Participation rates by ethnic group',
        tags=['comparison', 'ethnicity', 'participation']
    ),
    QueryTemplate(
        id='ethnicity_resource_allocation',
        category='comparison',
        pattern=r'\bresource\s+allocation\s+by\s+(ethnic|ethnolinguistic)\s+group',
        query_template='OBCCommunity.objects.filter(assessments__identified_needs__addressing_ppas__isnull=False).values("primary_ethnolinguistic_group").annotate(communities=Count("id", distinct=True), total_budget=Sum("assessments__identified_needs__addressing_ppas__actual_budget"), budget_per_community=Sum("assessments__identified_needs__addressing_ppas__actual_budget") / Count("id", distinct=True)).order_by("-total_budget")',
        required_entities=[],
        optional_entities=['ethnolinguistic_groups'],
        examples=[
            'Resource allocation by group',
            'Budget by ethnicity',
            'Funding allocation by ethnic group',
            'Ethnic group budget comparison'
        ],
        priority=8,
        description='Resource allocation by ethnic group',
        tags=['comparison', 'ethnicity', 'budget']
    ),
]


# =============================================================================
# METRIC COMPARISON QUERIES (6 templates)
# =============================================================================

COMPARISON_METRIC_TEMPLATES = [
    QueryTemplate(
        id='budget_efficiency',
        category='comparison',
        pattern=r'\b(compare\s+)?(budget|cost)\s+efficienc(y|ies)\s*(comparison|by)?',
        query_template='MonitoringEntry.objects.filter(actual_budget__gt=0, beneficiaries_count__gt=0).values("{group_field}").annotate(total_budget=Sum("actual_budget"), total_beneficiaries=Sum("beneficiaries_count"), cost_per_beneficiary=Sum("actual_budget") / Sum("beneficiaries_count"), efficiency_score=100.0 / (Sum("actual_budget") / Sum("beneficiaries_count"))).order_by("cost_per_beneficiary")',
        required_entities=['group_by'],
        optional_entities=[],
        examples=[
            'Budget efficiency comparison',
            'Compare cost efficiency',
            'Budget efficiency by MOA',
            'Most efficient spending'
        ],
        priority=8,
        description='Budget efficiency comparison',
        tags=['comparison', 'metric', 'budget', 'efficiency']
    ),
    QueryTemplate(
        id='project_success_rates',
        category='comparison',
        pattern=r'\b(project\s+)?success\s+rates?\s+(by|comparison)',
        query_template='MonitoringEntry.objects.values("{group_field}").annotate(total_projects=Count("id"), completed=Count("id", filter=Q(status="completed")), on_time=Count("id", filter=Q(completion_date__lte=F("target_completion_date"))), success_rate=100.0 * Count("id", filter=Q(status="completed")) / Count("id")).order_by("-success_rate")',
        required_entities=['group_by'],
        optional_entities=[],
        examples=[
            'Success rate by MOA',
            'Success rate by sector',
            'Compare project success rates',
            'Which MOA has best success rate?'
        ],
        priority=8,
        description='Success rate comparison',
        tags=['comparison', 'metric', 'success']
    ),
    QueryTemplate(
        id='completion_time_comparison',
        category='comparison',
        pattern=r'\bcompletion\s+time\s+(comparison|by type)',
        query_template='MonitoringEntry.objects.filter(completion_date__isnull=False).annotate(duration=(F("completion_date") - F("start_date")).days).values("{group_field}").annotate(avg_duration=Avg("duration"), median_duration=Percentile("duration", 0.5), count=Count("id")).order_by("avg_duration")',
        required_entities=['group_by'],
        optional_entities=[],
        examples=[
            'Completion time by type',
            'Compare project durations',
            'Average completion time comparison',
            'Which projects finish fastest?'
        ],
        priority=7,
        description='Completion time comparison',
        tags=['comparison', 'metric', 'duration']
    ),
    QueryTemplate(
        id='cost_per_beneficiary',
        category='comparison',
        pattern=r'\bcost\s+per\s+beneficiary\s+(comparison|by)',
        query_template='MonitoringEntry.objects.filter(actual_budget__gt=0, beneficiaries_count__gt=0).annotate(cost_per_beneficiary=F("actual_budget") / F("beneficiaries_count")).values("{group_field}").annotate(avg_cost=Avg("cost_per_beneficiary"), min_cost=Min("cost_per_beneficiary"), max_cost=Max("cost_per_beneficiary")).order_by("avg_cost")',
        required_entities=['group_by'],
        optional_entities=[],
        examples=[
            'Cost per beneficiary comparison',
            'Cost efficiency by sector',
            'Compare cost per beneficiary',
            'Most cost-effective projects'
        ],
        priority=8,
        description='Cost per beneficiary comparison',
        tags=['comparison', 'metric', 'cost']
    ),
    QueryTemplate(
        id='coverage_comparison',
        category='comparison',
        pattern=r'\bcoverage\s+rates?\s+(comparison|by)',
        query_template='{model}.objects.values("{group_field}").annotate(total_target=Count("id"), covered=Count("id", filter={coverage_condition}), coverage_rate=100.0 * Count("id", filter={coverage_condition}) / Count("id")).order_by("-coverage_rate")',
        required_entities=['group_by'],
        optional_entities=['model_type', 'coverage_criteria'],
        examples=[
            'Coverage rates comparison',
            'Compare coverage by region',
            'Assessment coverage comparison',
            'Service coverage by location'
        ],
        priority=7,
        description='Coverage rate comparison',
        tags=['comparison', 'metric', 'coverage']
    ),
    QueryTemplate(
        id='performance_benchmarking',
        category='comparison',
        pattern=r'\bperformance\s+(benchmark|vs benchmarks?)',
        query_template='{model}.objects.values("{group_field}").annotate(performance_score={performance_calculation}, benchmark=Avg({performance_calculation})).annotate(vs_benchmark=F("performance_score") - F("benchmark")).order_by("-performance_score")',
        required_entities=['performance_metric'],
        optional_entities=['model_type', 'group_by'],
        examples=[
            'Performance vs benchmarks',
            'Benchmark comparison',
            'Compare to performance standards',
            'Performance gap analysis'
        ],
        priority=7,
        description='Performance benchmarking',
        tags=['comparison', 'metric', 'benchmark']
    ),
]


# =============================================================================
# COMBINE ALL COMPARISON TEMPLATES
# =============================================================================

COMPARISON_TEMPLATES = (
    COMPARISON_LOCATION_TEMPLATES +
    COMPARISON_ETHNICITY_TEMPLATES +
    COMPARISON_METRIC_TEMPLATES
)

# Total: 8 + 6 + 6 = 20 comparison query templates
