"""
Analytics Query Templates for OBCMS Chat System

30 templates for advanced analytics including:
- Statistical insights (mean, median, distributions)
- Pattern identification (clustering, anomalies)
- Predictive indicators (risk scoring, forecasting)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# STATISTICAL INSIGHTS QUERIES (10 templates)
# =============================================================================

ANALYTICS_STATISTICAL_TEMPLATES = [
    QueryTemplate(
        id='statistical_summary',
        category='analytics',
        pattern=r'\b(statistical|stats)\s+(summary|analysis|overview)',
        query_template='{model}.objects.aggregate(count=Count("id"), mean=Avg("{field}"), median=Percentile("{field}", 0.5), std_dev=StdDev("{field}"), min=Min("{field}"), max=Max("{field}"))',
        required_entities=[],
        optional_entities=['model_type', 'field'],
        examples=[
            'Statistical summary',
            'Stats analysis',
            'Statistical overview',
            'Show statistics'
        ],
        priority=7,
        description='Mean, median, mode, std dev statistics',
        tags=['analytics', 'statistical', 'summary']
    ),
    QueryTemplate(
        id='distribution_analysis',
        category='analytics',
        pattern=r'\bdistribution\s+(analysis|by buckets?|breakdown)',
        query_template='{model}.objects.annotate(bucket=Case(When({field}__lte={lower}, then=Value("Low")), When({field}__lte={mid}, then=Value("Medium")), default=Value("High"))).values("bucket").annotate(count=Count("id"))',
        required_entities=[],
        optional_entities=['model_type', 'field', 'thresholds'],
        examples=[
            'Distribution analysis',
            'Distribution by buckets',
            'Show distribution breakdown',
            'Bucket analysis'
        ],
        priority=7,
        description='Distribution by value buckets',
        tags=['analytics', 'statistical', 'distribution']
    ),
    QueryTemplate(
        id='outlier_detection',
        category='analytics',
        pattern=r'\b(outliers?|anomalies|unusual values)\s+(detection|analysis)',
        query_template='{model}.objects.annotate(z_score=({field} - Avg("{field}")) / StdDev("{field}")).filter(Q(z_score__gt=3) | Q(z_score__lt=-3))',
        required_entities=[],
        optional_entities=['model_type', 'field'],
        examples=[
            'Outliers by Z-score',
            'Anomaly detection',
            'Detect unusual values',
            'Find outliers'
        ],
        priority=7,
        description='Outlier detection using Z-score',
        tags=['analytics', 'statistical', 'outliers']
    ),
    QueryTemplate(
        id='correlation_analysis',
        category='analytics',
        pattern=r'\bcorrelation\s+(between|analysis)',
        query_template='{model}.objects.aggregate(correlation=Corr("{field1}", "{field2}"))',
        required_entities=['fields'],
        optional_entities=['model_type'],
        examples=[
            'Correlation between metrics',
            'Correlation analysis',
            'Measure correlation',
            'Relationship between fields'
        ],
        priority=7,
        description='Correlation between two metrics',
        tags=['analytics', 'statistical', 'correlation']
    ),
    QueryTemplate(
        id='variance_analysis',
        category='analytics',
        pattern=r'\bvariance\s+(analysis|by group)',
        query_template='{model}.objects.values("{group_field}").annotate(variance=Variance("{value_field}"), std_dev=StdDev("{value_field}")).order_by("-variance")',
        required_entities=['group_by'],
        optional_entities=['model_type', 'field'],
        examples=[
            'Variance analysis',
            'Variance by group',
            'Measure variability',
            'Group variance'
        ],
        priority=6,
        description='Variance by group',
        tags=['analytics', 'statistical', 'variance']
    ),
    QueryTemplate(
        id='percentile_ranking',
        category='analytics',
        pattern=r'\b(percentile|90th|95th|99th)\s+(ranking|analysis|values)',
        query_template='{model}.objects.aggregate(p50=Percentile("{field}", 0.5), p75=Percentile("{field}", 0.75), p90=Percentile("{field}", 0.9), p95=Percentile("{field}", 0.95), p99=Percentile("{field}", 0.99))',
        required_entities=[],
        optional_entities=['model_type', 'field', 'percentile'],
        examples=[
            '90th percentile values',
            'Percentile ranking',
            'Top percentile analysis',
            'Show 95th percentile'
        ],
        priority=7,
        description='Percentile ranking analysis',
        tags=['analytics', 'statistical', 'percentile']
    ),
    QueryTemplate(
        id='coefficient_of_variation',
        category='analytics',
        pattern=r'\b(coefficient of variation|cv|variability measure)',
        query_template='{model}.objects.values("{group_field}").annotate(mean=Avg("{value_field}"), std_dev=StdDev("{value_field}"), cv=100.0 * StdDev("{value_field}") / Avg("{value_field}")).order_by("-cv")',
        required_entities=['group_by'],
        optional_entities=['model_type', 'field'],
        examples=[
            'Coefficient of variation',
            'Variability measure',
            'CV analysis',
            'Relative variability'
        ],
        priority=6,
        description='Coefficient of variation (CV)',
        tags=['analytics', 'statistical', 'variability']
    ),
    QueryTemplate(
        id='aggregation_by_dimension',
        category='analytics',
        pattern=r'\baggregate\s+by\s+multiple\s+dimensions',
        query_template='{model}.objects.values("{dim1}", "{dim2}").annotate(count=Count("id"), total=Sum("{value_field}"), avg=Avg("{value_field}")).order_by("{dim1}", "{dim2}")',
        required_entities=['dimensions'],
        optional_entities=['model_type', 'field'],
        examples=[
            'Aggregate by multiple dimensions',
            'Multi-dimensional analysis',
            'Cross-tabulation',
            'Pivot analysis'
        ],
        priority=7,
        description='Aggregate by multiple dimensions',
        tags=['analytics', 'statistical', 'multi_dim']
    ),
    QueryTemplate(
        id='weighted_averages',
        category='analytics',
        pattern=r'\b(weighted average|weighted by)',
        query_template='{model}.objects.aggregate(weighted_avg=Sum(F("{value_field}") * F("{weight_field}")) / Sum("{weight_field}"))',
        required_entities=['fields'],
        optional_entities=['model_type'],
        examples=[
            'Weighted by population',
            'Weighted average',
            'Weighted by budget',
            'Population-weighted average'
        ],
        priority=7,
        description='Weighted averages by dimension',
        tags=['analytics', 'statistical', 'weighted']
    ),
    QueryTemplate(
        id='confidence_intervals',
        category='analytics',
        pattern=r'\bconfidence\s+(interval|range)',
        query_template='{model}.objects.aggregate(mean=Avg("{field}"), std_dev=StdDev("{field}"), count=Count("id")).annotate(margin=1.96 * F("std_dev") / Sqrt(F("count")), lower_bound=F("mean") - F("margin"), upper_bound=F("mean") + F("margin"))',
        required_entities=[],
        optional_entities=['model_type', 'field', 'confidence_level'],
        examples=[
            'Confidence intervals',
            '95% confidence range',
            'Statistical confidence',
            'Margin of error'
        ],
        priority=6,
        description='Statistical confidence intervals',
        tags=['analytics', 'statistical', 'confidence']
    ),
]


# =============================================================================
# PATTERN IDENTIFICATION QUERIES (10 templates)
# =============================================================================

ANALYTICS_PATTERN_TEMPLATES = [
    QueryTemplate(
        id='clustering_analysis',
        category='analytics',
        pattern=r'\b(identify\s+)?(clusters?|clustering|group\s+similar)\s*(analysis|identification)?',
        query_template='{model}.objects.annotate(cluster_key=Concat(Substr(Cast("{field1}", CharField()), 1, 1), Substr(Cast("{field2}", CharField()), 1, 1))).values("cluster_key").annotate(count=Count("id"), avg_field1=Avg("{field1}"), avg_field2=Avg("{field2}")).order_by("-count")',
        required_entities=[],
        optional_entities=['model_type', 'fields'],
        examples=[
            'Identify clusters',
            'Clustering analysis',
            'Group similar items',
            'Find patterns'
        ],
        priority=6,
        description='Clustering and pattern identification',
        tags=['analytics', 'pattern', 'clustering']
    ),
    QueryTemplate(
        id='segmentation',
        category='analytics',
        pattern=r'\b(segment|segmentation)\s+(by|analysis)',
        query_template='{model}.objects.values("{segment_field}").annotate(count=Count("id"), avg_value=Avg("{value_field}"), total_value=Sum("{value_field}")).order_by("-count")',
        required_entities=['group_by'],
        optional_entities=['model_type', 'field'],
        examples=[
            'Group by characteristics',
            'Segmentation analysis',
            'Segment by attributes',
            'Customer segmentation'
        ],
        priority=7,
        description='Segmentation by characteristics',
        tags=['analytics', 'pattern', 'segmentation']
    ),
    QueryTemplate(
        id='anomaly_detection',
        category='analytics',
        pattern=r'\b(anomal(y|ies)|unusual patterns?|irregularit(y|ies))',
        query_template='{model}.objects.annotate(deviation=Abs(F("{field}") - Avg("{field}"))).filter(deviation__gt=2 * StdDev("{field}")).order_by("-deviation")',
        required_entities=[],
        optional_entities=['model_type', 'field'],
        examples=[
            'Detect anomalies',
            'Unusual patterns',
            'Find irregularities',
            'Anomaly detection'
        ],
        priority=7,
        description='Detect unusual patterns',
        tags=['analytics', 'pattern', 'anomaly']
    ),
    QueryTemplate(
        id='similarity_analysis',
        category='analytics',
        pattern=r'\b(similar|find similar|similarity)\s+(communities|projects|items)',
        query_template='{model}.objects.filter({base_filters}).annotate(similarity_score=0).order_by("-similarity_score")[:20]',
        required_entities=['reference_id'],
        optional_entities=['model_type'],
        examples=[
            'Find similar communities',
            'Similar projects',
            'Similarity analysis',
            'Communities like this one'
        ],
        priority=6,
        description='Find similar items',
        tags=['analytics', 'pattern', 'similarity']
    ),
    QueryTemplate(
        id='pattern_matching',
        category='analytics',
        pattern=r'\bcommunities\s+with\s+similar\s+profile',
        query_template='OBCCommunity.objects.filter(primary_ethnolinguistic_group="{ethnicity}", primary_livelihood="{livelihood}").exclude(id="{exclude_id}").select_related("barangay__municipality__province")[:20]',
        required_entities=['profile_attributes'],
        optional_entities=['reference_id'],
        examples=[
            'Communities with similar profiles',
            'Match community characteristics',
            'Find similar demographic profiles',
            'Pattern matching'
        ],
        priority=7,
        description='Pattern matching by profile',
        tags=['analytics', 'pattern', 'matching']
    ),
    QueryTemplate(
        id='grouping_by_characteristics',
        category='analytics',
        pattern=r'\bgroup\s+by\s+(demographics|characteristics|attributes)',
        query_template='{model}.objects.values("{char1}", "{char2}").annotate(count=Count("id")).order_by("-count")[:30]',
        required_entities=['grouping_fields'],
        optional_entities=['model_type'],
        examples=[
            'Group by demographics',
            'Group by characteristics',
            'Cluster by attributes',
            'Categorize by features'
        ],
        priority=7,
        description='Group by multiple characteristics',
        tags=['analytics', 'pattern', 'grouping']
    ),
    QueryTemplate(
        id='hotspot_identification',
        category='analytics',
        pattern=r'\b(hotspot|high.?density|concentration)\s+(identification|areas?|analysis)',
        query_template='{model}.objects.values("{location_field}").annotate(count=Count("id"), density=Count("id") / Count("{location_field}", distinct=True)).filter(count__gte={threshold}).order_by("-density")',
        required_entities=['location_field'],
        optional_entities=['model_type', 'threshold'],
        examples=[
            'Identify hotspots',
            'High-density areas',
            'Concentration analysis',
            'Where are concentrations?'
        ],
        priority=7,
        description='Identify geographic hotspots',
        tags=['analytics', 'pattern', 'hotspot', 'geographic']
    ),
    QueryTemplate(
        id='network_analysis',
        category='analytics',
        pattern=r'\b(network|connection)\s+(analysis|patterns?)',
        query_template='Partnership.objects.annotate(partner_count=Count("partners")).values("focus_areas").annotate(partnerships=Count("id"), avg_partners=Avg("partner_count")).order_by("-partnerships")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Network analysis',
            'Connection patterns',
            'Partnership networks',
            'Collaboration patterns'
        ],
        priority=6,
        description='Network and connection patterns',
        tags=['analytics', 'pattern', 'network']
    ),
    QueryTemplate(
        id='hierarchy_analysis',
        category='analytics',
        pattern=r'\b(hierarch(y|ical)|parent.?child)\s+(analysis|relationships?)',
        query_template='{model}.objects.values("{parent_field}").annotate(children_count=Count("id"), avg_value=Avg("{value_field}")).order_by("-children_count")',
        required_entities=['hierarchy_field'],
        optional_entities=['model_type'],
        examples=[
            'Hierarchical analysis',
            'Parent-child relationships',
            'Hierarchy patterns',
            'Tree structure analysis'
        ],
        priority=6,
        description='Hierarchical relationship analysis',
        tags=['analytics', 'pattern', 'hierarchy']
    ),
    QueryTemplate(
        id='factor_analysis',
        category='analytics',
        pattern=r'\b(factor|contributing factors?)\s+(analysis|identification)',
        query_template='{model}.objects.values("{factor_field}").annotate(count=Count("id"), avg_outcome=Avg("{outcome_field}")).order_by("-avg_outcome")',
        required_entities=['factors'],
        optional_entities=['model_type'],
        examples=[
            'Contributing factors',
            'Factor analysis',
            'What factors contribute?',
            'Identify key factors'
        ],
        priority=6,
        description='Contributing factor analysis',
        tags=['analytics', 'pattern', 'factors']
    ),
]


# =============================================================================
# PREDICTIVE INDICATORS QUERIES (10 templates)
# =============================================================================

ANALYTICS_PREDICTIVE_TEMPLATES = [
    QueryTemplate(
        id='risk_scoring',
        category='analytics',
        pattern=r'\b(risk\s+score|risk\s+assessment|risk\s+level)',
        query_template='{model}.objects.annotate(risk_score=Case(When({high_risk_condition}, then=Value(3)), When({medium_risk_condition}, then=Value(2)), default=Value(1))).values("risk_score").annotate(count=Count("id"))',
        required_entities=[],
        optional_entities=['model_type', 'risk_factors'],
        examples=[
            'Risk score by project',
            'Risk assessment',
            'Community risk levels',
            'Calculate risk scores'
        ],
        priority=7,
        description='Risk scoring and assessment',
        tags=['analytics', 'predictive', 'risk']
    ),
    QueryTemplate(
        id='success_indicators',
        category='analytics',
        pattern=r'\b(success\s+indicators?|factors?\s+of\s+success)',
        query_template='{model}.objects.filter(status="completed").values("{factor_field}").annotate(count=Count("id"), success_rate=100.0 * Count("id", filter=Q({success_condition})) / Count("id")).order_by("-success_rate")',
        required_entities=[],
        optional_entities=['model_type', 'success_criteria'],
        examples=[
            'Indicators of success',
            'Success factors',
            'What predicts success?',
            'Success rate analysis'
        ],
        priority=7,
        description='Indicators of successful outcomes',
        tags=['analytics', 'predictive', 'success']
    ),
    QueryTemplate(
        id='gap_prediction',
        category='analytics',
        pattern=r'\b(predict|gap\s+prediction|future\s+gaps?)',
        query_template='{model}.objects.annotate(current_value=F("{field}"), projected_value=F("{field}") * 1.1, gap=F("projected_value") - F("{target_field}")).filter(gap__gt=0).order_by("-gap")',
        required_entities=[],
        optional_entities=['model_type', 'projection_factor'],
        examples=[
            'Predict future gaps',
            'Gap prediction',
            'Project shortfalls',
            'Forecast deficits'
        ],
        priority=6,
        description='Predict future gaps and shortfalls',
        tags=['analytics', 'predictive', 'gaps']
    ),
    QueryTemplate(
        id='capacity_analysis',
        category='analytics',
        pattern=r'\bcapacit(y|ies)\s+(vs|versus)?\s*(demand|analysis)',
        query_template='{model}.objects.aggregate(total_capacity=Sum("{capacity_field}"), total_demand=Sum("{demand_field}"), utilization_rate=100.0 * Sum("{demand_field}") / Sum("{capacity_field}"), shortfall=Sum("{capacity_field}") - Sum("{demand_field}"))',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'Capacity vs demand',
            'Capacity analysis',
            'Utilization rate',
            'Capacity shortfall'
        ],
        priority=7,
        description='Capacity vs demand analysis',
        tags=['analytics', 'predictive', 'capacity']
    ),
    QueryTemplate(
        id='efficiency_metrics',
        category='analytics',
        pattern=r'\befficienc(y|ies)\s+(metrics?|indicators?|analysis)',
        query_template='{model}.objects.annotate(efficiency=F("{output_field}") / F("{input_field}")).values("{group_field}").annotate(avg_efficiency=Avg("efficiency"), count=Count("id")).order_by("-avg_efficiency")',
        required_entities=['efficiency_fields'],
        optional_entities=['model_type', 'group_by'],
        examples=[
            'Efficiency indicators',
            'Efficiency metrics',
            'Cost efficiency',
            'Output per input'
        ],
        priority=7,
        description='Efficiency indicators and metrics',
        tags=['analytics', 'predictive', 'efficiency']
    ),
    QueryTemplate(
        id='performance_prediction',
        category='analytics',
        pattern=r'\b(performance\s+prediction|predicted\s+performance)',
        query_template='{model}.objects.annotate(predicted_score=({factor1_weight} * F("{factor1}") + {factor2_weight} * F("{factor2}")) / ({factor1_weight} + {factor2_weight})).order_by("-predicted_score")',
        required_entities=[],
        optional_entities=['model_type', 'prediction_factors'],
        examples=[
            'Predicted performance',
            'Performance prediction',
            'Forecast outcomes',
            'Expected performance'
        ],
        priority=6,
        description='Predict future performance',
        tags=['analytics', 'predictive', 'performance']
    ),
    QueryTemplate(
        id='trend_projection',
        category='analytics',
        pattern=r'\b(trend\s+projection|project\s+trends?)',
        query_template='{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days=365)).annotate(month=TruncMonth("created_at")).values("month").annotate(count=Count("id")).aggregate(avg_monthly=Avg("count"), projected_annual=Sum("count") * 12 / 12)',
        required_entities=[],
        optional_entities=['model_type', 'time_period'],
        examples=[
            'Project future trends',
            'Trend projection',
            'Forecast trajectory',
            'Extrapolate trends'
        ],
        priority=6,
        description='Project trends into future',
        tags=['analytics', 'predictive', 'trends']
    ),
    QueryTemplate(
        id='early_warning_indicators',
        category='analytics',
        pattern=r'\b(early\s+warning|warning\s+signs?|red\s+flags?)',
        query_template='{model}.objects.filter({warning_conditions}).annotate(warning_count=Count("id", filter={warning_filters})).filter(warning_count__gte=1).order_by("-warning_count")',
        required_entities=[],
        optional_entities=['model_type', 'warning_criteria'],
        examples=[
            'Early warning indicators',
            'Warning signs',
            'Red flags',
            'Risk indicators'
        ],
        priority=7,
        description='Early warning indicators',
        tags=['analytics', 'predictive', 'warning']
    ),
    QueryTemplate(
        id='impact_prediction',
        category='analytics',
        pattern=r'\b(impact\s+prediction|predicted\s+impact)',
        query_template='{model}.objects.annotate(predicted_impact=F("{beneficiaries}") * F("{impact_factor}")).values("{category}").annotate(total_impact=Sum("predicted_impact"), avg_impact=Avg("predicted_impact")).order_by("-total_impact")',
        required_entities=[],
        optional_entities=['model_type', 'impact_factors'],
        examples=[
            'Predicted impact',
            'Impact prediction',
            'Expected outcomes',
            'Forecast impact'
        ],
        priority=7,
        description='Predict project/policy impact',
        tags=['analytics', 'predictive', 'impact']
    ),
    QueryTemplate(
        id='resource_optimization',
        category='analytics',
        pattern=r'\b(resource\s+optimization|optimal\s+(allocation|distribution))',
        query_template='{model}.objects.annotate(efficiency_score=F("{output}") / F("{resource}"), priority_score=Case(When(priority="critical", then=Value(4)), When(priority="high", then=Value(3)), When(priority="medium", then=Value(2)), default=Value(1)), optimization_score=F("efficiency_score") * F("priority_score")).order_by("-optimization_score")',
        required_entities=[],
        optional_entities=['model_type', 'optimization_criteria'],
        examples=[
            'Optimal resource allocation',
            'Resource optimization',
            'Best distribution',
            'Optimize allocation'
        ],
        priority=7,
        description='Optimal resource allocation',
        tags=['analytics', 'predictive', 'optimization']
    ),
]


# =============================================================================
# COMBINE ALL ANALYTICS TEMPLATES
# =============================================================================

ANALYTICS_TEMPLATES = (
    ANALYTICS_STATISTICAL_TEMPLATES +
    ANALYTICS_PATTERN_TEMPLATES +
    ANALYTICS_PREDICTIVE_TEMPLATES
)

# Total: 10 + 10 + 10 = 30 analytics query templates
