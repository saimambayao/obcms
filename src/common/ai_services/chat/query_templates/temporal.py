"""
Temporal Query Templates for OBCMS Chat System

30 templates for time-based queries including:
- Date range queries (assessments by period, fiscal years)
- Trend analysis (completion trends, growth rates)
- Historical analysis (period comparisons, aging analysis)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# DATE RANGE QUERIES (10 templates)
# =============================================================================

TEMPORAL_DATE_RANGE_TEMPLATES = [
    QueryTemplate(
        id='count_by_date_range',
        category='temporal',
        pattern=r'\b(assessments?|ppas?|projects?|meetings?)\s+(in|during|from|within|last|past|this)?\s*(last|past|previous|this)?\s*(\d+)?\s*(days?|weeks?|months?|years?|quarters?)',
        query_template='{model}.objects.filter(created_at__gte=timezone.now() - timedelta({period}={value})).count()',
        required_entities=['time_period'],
        optional_entities=['model_type'],
        examples=[
            'Assessments last 30 days',
            'PPAs this quarter',
            'Projects in last 6 months',
            'Meetings last week',
            'How many assessments in the past 90 days?'
        ],
        priority=8,
        description='Count items within date range',
        tags=['temporal', 'date_range', 'count']
    ),
    QueryTemplate(
        id='count_by_fiscal_year',
        category='temporal',
        pattern=r'\b(in|during|for)\s+(fy|fiscal year)\s*(\d{4})',
        query_template='{model}.objects.filter(start_date__year={year}).count()',
        required_entities=['fiscal_year'],
        optional_entities=['model_type'],
        examples=[
            'Projects in FY 2024',
            'Assessments for fiscal year 2025',
            'PPAs during FY 2023',
            'How many projects in fiscal year 2024?'
        ],
        priority=8,
        description='Count items in specific fiscal year',
        tags=['temporal', 'fiscal_year', 'count']
    ),
    QueryTemplate(
        id='count_by_month',
        category='temporal',
        pattern=r'\b(assessments?|ppas?|projects?)\s+(in|during|for)\s+(january|february|march|april|may|june|july|august|september|october|november|december)(\s+\d{4})?',
        query_template='{model}.objects.filter(created_at__month={month}, created_at__year={year}).count()',
        required_entities=['month'],
        optional_entities=['year', 'model_type'],
        examples=[
            'Assessments in January',
            'PPAs during March 2024',
            'Projects for December 2023',
            'How many assessments in January 2024?'
        ],
        priority=8,
        description='Count items in specific month',
        tags=['temporal', 'month', 'count']
    ),
    QueryTemplate(
        id='count_by_quarter',
        category='temporal',
        pattern=r'\b(budget|ppas?|projects?)\s+(by|per|in)\s+quarter',
        query_template='{model}.objects.annotate(quarter=ExtractQuarter("start_date")).values("quarter").annotate(count=Count("id")).order_by("quarter")',
        required_entities=[],
        optional_entities=['model_type', 'year'],
        examples=[
            'Budget by quarter',
            'PPAs per quarter',
            'Projects by quarter 2024',
            'Show quarterly distribution'
        ],
        priority=7,
        description='Group items by quarter',
        tags=['temporal', 'quarter', 'aggregate']
    ),
    QueryTemplate(
        id='count_year_to_date',
        category='temporal',
        pattern=r'\b(ytd|year to date|this year)\s+(assessments?|ppas?|projects?)',
        query_template='{model}.objects.filter(created_at__year=timezone.now().year).count()',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'YTD assessments',
            'Year to date PPAs',
            'This year projects',
            'How many assessments year to date?'
        ],
        priority=8,
        description='Count items year to date',
        tags=['temporal', 'ytd', 'count']
    ),
    QueryTemplate(
        id='count_last_n_days',
        category='temporal',
        pattern=r'\b(last|past|previous)\s+(\d+)\s+days?',
        query_template='{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days={days})).count()',
        required_entities=['number'],
        optional_entities=['model_type'],
        examples=[
            'Last 7 days',
            'Past 30 days assessments',
            'Previous 90 days PPAs',
            'How many in last 14 days?'
        ],
        priority=9,
        description='Count items in last N days',
        tags=['temporal', 'recent', 'count']
    ),
    QueryTemplate(
        id='count_between_dates',
        category='temporal',
        pattern=r'\b(between|from)\s+(?P<start_date>[\w\-/]+)\s+(and|to)\s+(?P<end_date>[\w\-/]+)',
        query_template='{model}.objects.filter(created_at__gte="{start_date}", created_at__lte="{end_date}").count()',
        required_entities=['date_start', 'date_end'],
        optional_entities=['model_type'],
        examples=[
            'Between January 1 and March 31',
            'From 2024-01-01 to 2024-06-30',
            'Assessments between Jan 1 and Dec 31 2024'
        ],
        priority=9,
        description='Count items between two dates',
        tags=['temporal', 'date_range', 'count']
    ),
    QueryTemplate(
        id='count_before_date',
        category='temporal',
        pattern=r'\bbefore\s+(?P<date>[\w\-/\s]+)',
        query_template='{model}.objects.filter(created_at__lt="{date}").count()',
        required_entities=['date_end'],
        optional_entities=['model_type'],
        examples=[
            'Before December 2024',
            'Assessments before 2024-06-30',
            'PPAs before January 2025'
        ],
        priority=7,
        description='Count items before specific date',
        tags=['temporal', 'date_filter', 'count']
    ),
    QueryTemplate(
        id='count_after_date',
        category='temporal',
        pattern=r'\bafter\s+(?P<date>[\w\-/\s]+)',
        query_template='{model}.objects.filter(created_at__gt="{date}").count()',
        required_entities=['date_start'],
        optional_entities=['model_type'],
        examples=[
            'After January 2025',
            'Assessments after 2024-12-31',
            'PPAs after June 1'
        ],
        priority=7,
        description='Count items after specific date',
        tags=['temporal', 'date_filter', 'count']
    ),
    QueryTemplate(
        id='count_current_period',
        category='temporal',
        pattern=r'\b(this|current)\s+(week|month|quarter|year)',
        query_template='{model}.objects.filter(created_at__gte={period_start}).count()',
        required_entities=['time_period'],
        optional_entities=['model_type'],
        examples=[
            'This week assessments',
            'Current month PPAs',
            'This quarter projects',
            'Current year total'
        ],
        priority=8,
        description='Count items in current period',
        tags=['temporal', 'current_period', 'count']
    ),
]


# =============================================================================
# TREND ANALYSIS QUERIES (10 templates)
# =============================================================================

TEMPORAL_TREND_TEMPLATES = [
    QueryTemplate(
        id='assessment_completion_trends',
        category='temporal',
        pattern=r'\b(assessment|assessments)\s+(trend|trends|over time|completion)',
        query_template='Assessment.objects.filter(status="completed").annotate(month=TruncMonth("completion_date")).values("month").annotate(count=Count("id")).order_by("month")',
        required_entities=[],
        optional_entities=['time_period'],
        examples=[
            'Assessment trends over time',
            'Assessment completion trends',
            'Show assessment trends',
            'Track assessment completions'
        ],
        priority=7,
        description='Assessment completion trends by month',
        tags=['temporal', 'trends', 'assessments']
    ),
    QueryTemplate(
        id='ppa_implementation_trends',
        category='temporal',
        pattern=r'\b(ppa|project|projects?)\s+(start|implementation|trends?)\s+(by month|monthly|over time)',
        query_template='MonitoringEntry.objects.annotate(month=TruncMonth("start_date")).values("month").annotate(count=Count("id")).order_by("month")',
        required_entities=[],
        optional_entities=['time_period'],
        examples=[
            'Project starts by month',
            'PPA implementation trends',
            'Project trends over time',
            'Monthly project launches'
        ],
        priority=7,
        description='PPA implementation trends by month',
        tags=['temporal', 'trends', 'ppas']
    ),
    QueryTemplate(
        id='budget_utilization_trends',
        category='temporal',
        pattern=r'\bbudget\s+(utilization|spend|spending)\s+(trends?|over time|by quarter)',
        query_template='MonitoringEntry.objects.annotate(quarter=ExtractQuarter("start_date")).values("quarter").annotate(total_budget=Sum("actual_budget")).order_by("quarter")',
        required_entities=[],
        optional_entities=['time_period'],
        examples=[
            'Budget spend over quarters',
            'Budget utilization trends',
            'Quarterly budget spending',
            'Track budget over time'
        ],
        priority=7,
        description='Budget utilization trends by quarter',
        tags=['temporal', 'trends', 'budget']
    ),
    QueryTemplate(
        id='needs_identification_trends',
        category='temporal',
        pattern=r'\bneeds?\s+(identified|identification)\s+(per month|trends?|over time)',
        query_template='Need.objects.annotate(month=TruncMonth("created_at")).values("month").annotate(count=Count("id")).order_by("month")',
        required_entities=[],
        optional_entities=['time_period'],
        examples=[
            'Needs identified per month',
            'Needs identification trends',
            'Track needs over time',
            'Monthly needs discovery'
        ],
        priority=7,
        description='Needs identification trends by month',
        tags=['temporal', 'trends', 'needs']
    ),
    QueryTemplate(
        id='engagement_frequency_trends',
        category='temporal',
        pattern=r'\b(meeting|engagement|stakeholder)\s+frequency\s+(trends?|over time)',
        query_template='StakeholderEngagement.objects.annotate(month=TruncMonth("engagement_date")).values("month").annotate(count=Count("id")).order_by("month")',
        required_entities=[],
        optional_entities=['time_period'],
        examples=[
            'Meeting frequency trends',
            'Engagement trends over time',
            'Stakeholder meeting patterns',
            'Track engagement frequency'
        ],
        priority=7,
        description='Engagement frequency trends by month',
        tags=['temporal', 'trends', 'engagements']
    ),
    QueryTemplate(
        id='growth_rate_analysis',
        category='temporal',
        pattern=r'\b(growth|growth rate|yoy|year over year)\s+(assessments?|ppas?|projects?)',
        query_template='{model}.objects.annotate(year=ExtractYear("created_at")).values("year").annotate(count=Count("id")).order_by("year")',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'YoY growth in assessments',
            'Year over year project growth',
            'Growth rate analysis',
            'Annual growth trends'
        ],
        priority=7,
        description='Year-over-year growth rate analysis',
        tags=['temporal', 'trends', 'growth']
    ),
    QueryTemplate(
        id='seasonal_patterns',
        category='temporal',
        pattern=r'\b(seasonal|seasonality|by month)\s+(patterns?|variations?|trends?)',
        query_template='{model}.objects.annotate(month=ExtractMonth("created_at")).values("month").annotate(count=Count("id")).order_by("month")',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'Seasonal variations',
            'Monthly patterns',
            'Seasonality analysis',
            'Patterns by month'
        ],
        priority=6,
        description='Seasonal pattern analysis by month',
        tags=['temporal', 'trends', 'seasonal']
    ),
    QueryTemplate(
        id='momentum_analysis',
        category='temporal',
        pattern=r'\b(increasing|decreasing|momentum|velocity)\s+(trends?|patterns?)',
        query_template='{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days=180)).annotate(week=TruncWeek("created_at")).values("week").annotate(count=Count("id")).order_by("week")',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'Increasing trends',
            'Momentum analysis',
            'Velocity tracking',
            'Show acceleration'
        ],
        priority=6,
        description='Momentum and velocity analysis',
        tags=['temporal', 'trends', 'momentum']
    ),
    QueryTemplate(
        id='forecast_projections',
        category='temporal',
        pattern=r'\b(forecast|projected?|predict|next quarter|upcoming)',
        query_template='{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days=365)).annotate(quarter=ExtractQuarter("created_at")).values("quarter").annotate(avg_count=Count("id")).aggregate(projection=Avg("avg_count"))',
        required_entities=[],
        optional_entities=['model_type', 'time_period'],
        examples=[
            'Projected completions next quarter',
            'Forecast upcoming assessments',
            'Predict next quarter PPAs',
            'Projection analysis'
        ],
        priority=6,
        description='Forecast and projection analysis',
        tags=['temporal', 'trends', 'forecast']
    ),
    QueryTemplate(
        id='period_comparisons',
        category='temporal',
        pattern=r'\b(q1|q2|q3|q4|quarter\s+\d)\s+(vs|versus|compared to)\s+(q1|q2|q3|q4|quarter\s+\d)',
        query_template='{model}.objects.filter(Q(created_at__quarter={q1}) | Q(created_at__quarter={q2})).values("created_at__quarter").annotate(count=Count("id"))',
        required_entities=['quarters'],
        optional_entities=['model_type', 'year'],
        examples=[
            'Q1 vs Q2 comparison',
            'Compare Q3 and Q4',
            'Quarter 1 versus quarter 2',
            'Q2 2024 vs Q2 2023'
        ],
        priority=7,
        description='Period-to-period comparison',
        tags=['temporal', 'comparison', 'quarters']
    ),
]


# =============================================================================
# HISTORICAL ANALYSIS QUERIES (10 templates)
# =============================================================================

TEMPORAL_HISTORICAL_TEMPLATES = [
    QueryTemplate(
        id='historical_comparison',
        category='temporal',
        pattern=r'\b(\d{4})\s+(vs|versus|compared?\s+to|and)\s+(\d{4})',
        query_template='{model}.objects.filter(Q(created_at__year={year1}) | Q(created_at__year={year2})).values("created_at__year").annotate(count=Count("id"))',
        required_entities=['years'],
        optional_entities=['model_type'],
        examples=[
            '2024 vs 2023 comparison',
            'Compare 2025 and 2024',
            '2023 versus 2022',
            'Year over year 2024 vs 2023'
        ],
        priority=8,
        description='Compare two years',
        tags=['temporal', 'historical', 'comparison']
    ),
    QueryTemplate(
        id='cumulative_totals',
        category='temporal',
        pattern=r'\b(cumulative|running total|accumulated)\s+(assessments?|ppas?|projects?)',
        query_template='{model}.objects.filter(created_at__lte=timezone.now()).annotate(month=TruncMonth("created_at")).values("month").annotate(count=Count("id")).order_by("month")',
        required_entities=[],
        optional_entities=['model_type', 'time_period'],
        examples=[
            'Cumulative assessments over time',
            'Running total of PPAs',
            'Accumulated projects',
            'Show cumulative totals'
        ],
        priority=7,
        description='Cumulative totals over time',
        tags=['temporal', 'historical', 'cumulative']
    ),
    QueryTemplate(
        id='milestone_tracking',
        category='temporal',
        pattern=r'\b(time to complete|completion time|duration)\s+by\s+(project type|category|type)',
        query_template='MonitoringEntry.objects.filter(completion_date__isnull=False).annotate(duration=F("completion_date") - F("start_date")).values("project_type").annotate(avg_duration=Avg("duration"))',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'Time to complete by project type',
            'Average completion time',
            'Duration by category',
            'Milestone completion tracking'
        ],
        priority=7,
        description='Time to complete by category',
        tags=['temporal', 'historical', 'duration']
    ),
    QueryTemplate(
        id='overdue_analysis',
        category='temporal',
        pattern=r'\b(overdue|past due|late|delayed)\s+(by days|items?|analysis)',
        query_template='{model}.objects.filter(target_date__lt=timezone.now(), status__in=["planning", "in_progress"]).annotate(days_overdue=timezone.now() - F("target_date")).order_by("-days_overdue")',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'Items overdue by days',
            'Overdue analysis',
            'Past due items',
            'Delayed projects'
        ],
        priority=8,
        description='Overdue items analysis',
        tags=['temporal', 'historical', 'overdue']
    ),
    QueryTemplate(
        id='completion_duration',
        category='temporal',
        pattern=r'\b(average|mean)\s+(duration|time|completion time)\s+by\s+(type|category)',
        query_template='{model}.objects.filter(completion_date__isnull=False).annotate(duration=F("completion_date") - F("start_date")).values("{group_field}").annotate(avg_duration=Avg("duration"))',
        required_entities=['group_by'],
        optional_entities=['model_type'],
        examples=[
            'Average duration by type',
            'Mean completion time by category',
            'Duration analysis by project type',
            'Average time to complete'
        ],
        priority=7,
        description='Average completion duration by type',
        tags=['temporal', 'historical', 'duration']
    ),
    QueryTemplate(
        id='aging_analysis',
        category='temporal',
        pattern=r'\b(aging|age analysis|items by age)',
        query_template='{model}.objects.annotate(age_days=(timezone.now() - F("created_at")).days).aggregate(age_0_30=Count("id", filter=Q(age_days__lte=30)), age_30_60=Count("id", filter=Q(age_days__gt=30, age_days__lte=60)), age_60_plus=Count("id", filter=Q(age_days__gt=60)))',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'Items by age (0-30, 30-60, 60+ days)',
            'Aging analysis',
            'Age distribution',
            'How old are items?'
        ],
        priority=7,
        description='Age distribution analysis',
        tags=['temporal', 'historical', 'aging']
    ),
    QueryTemplate(
        id='time_to_approval',
        category='temporal',
        pattern=r'\b(time to approval|approval time|average approval)',
        query_template='MonitoringEntry.objects.filter(approval_date__isnull=False).annotate(approval_time=F("approval_date") - F("created_at")).aggregate(avg_approval_time=Avg("approval_time"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Average approval time',
            'Time to approval',
            'How long for approval?',
            'Approval duration'
        ],
        priority=7,
        description='Average time to approval',
        tags=['temporal', 'historical', 'approval']
    ),
    QueryTemplate(
        id='recurrence_patterns',
        category='temporal',
        pattern=r'\b(recurring|repeating|scheduled|regular)\s+(events?|meetings?|assessments?)',
        query_template='StakeholderEngagement.objects.values("engagement_type").annotate(count=Count("id"), avg_interval=Avg(F("engagement_date") - F("engagement_date"))).order_by("-count")',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'Recurring events schedule',
            'Repeating meetings',
            'Regular assessments pattern',
            'Scheduled engagement frequency'
        ],
        priority=6,
        description='Recurring event patterns',
        tags=['temporal', 'historical', 'recurrence']
    ),
    QueryTemplate(
        id='anniversary_tracking',
        category='temporal',
        pattern=r'\b(one year ago|anniversary|from last year)',
        query_template='{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days=365), created_at__lte=timezone.now() - timedelta(days=350))',
        required_entities=[],
        optional_entities=['model_type'],
        examples=[
            'Items from 1 year ago',
            'Anniversary tracking',
            'From last year',
            'One year old items'
        ],
        priority=6,
        description='Items created ~1 year ago',
        tags=['temporal', 'historical', 'anniversary']
    ),
    QueryTemplate(
        id='historical_averages',
        category='temporal',
        pattern=r'\b(historical average|average by period|mean per period)',
        query_template='{model}.objects.annotate(period=Trunc{period_type}("created_at")).values("period").annotate(count=Count("id")).aggregate(avg_per_period=Avg("count"))',
        required_entities=['time_period'],
        optional_entities=['model_type'],
        examples=[
            'Historical average by month',
            'Mean per quarter',
            'Average by period',
            'Typical monthly count'
        ],
        priority=7,
        description='Historical averages by period',
        tags=['temporal', 'historical', 'average']
    ),
]


# =============================================================================
# COMBINE ALL TEMPORAL TEMPLATES
# =============================================================================

TEMPORAL_TEMPLATES = (
    TEMPORAL_DATE_RANGE_TEMPLATES +
    TEMPORAL_TREND_TEMPLATES +
    TEMPORAL_HISTORICAL_TEMPLATES
)

# Total: 10 + 10 + 10 = 30 temporal query templates
