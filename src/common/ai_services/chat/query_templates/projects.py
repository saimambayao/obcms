"""
Projects/PPAs (Programs, Projects, Activities) Query Templates for OBCMS Chat System

Comprehensive templates for querying MOA/Ministry work including:
- Project queries (active, completed, by ministry, by sector)
- Program queries (by sector, beneficiaries)
- Activity tracking (by quarter, timeline)
- Budget linkage (by budget, utilization)
- Impact queries (outcomes, beneficiary impact)
- MOA/Ministry queries (projects by MOA, ministry work, agency activities)

Total: 45+ templates covering all PPA domains
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# PROJECT LISTING TEMPLATES (10 templates)
# =============================================================================

PROJECTS_LIST_TEMPLATES = [
    QueryTemplate(
        id='list_all_projects',
        category='projects',
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(all\s+)?(ppas?|projects?|programs?)\b',
        query_template='MonitoringEntry.objects.all().order_by("-created_at")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me projects',
            'List all PPAs',
            'Display programs',
            'Get all projects'
        ],
        priority=6,
        description='List all projects/PPAs',
        tags=['list', 'projects', 'ppas'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_active_projects',
        category='projects',
        pattern=r'\b(show|list|display)\s+(me\s+)?(active|ongoing)\s+(ppas?|projects?|programs?)\b',
        query_template='MonitoringEntry.objects.filter(status="ongoing").order_by("-start_date")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me active projects',
            'List ongoing PPAs',
            'Display active programs',
            'Get ongoing projects'
        ],
        priority=8,
        description='List active/ongoing projects',
        tags=['list', 'projects', 'active', 'ongoing'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_completed_projects',
        category='projects',
        pattern=r'\b(show|list|display)\s+(me\s+)?(completed|finished|done)\s+(ppas?|projects?|programs?)\b',
        query_template='MonitoringEntry.objects.filter(status="completed").order_by("-end_date")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me completed projects',
            'List finished PPAs',
            'Display done programs',
            'Get completed projects'
        ],
        priority=8,
        description='List completed projects',
        tags=['list', 'projects', 'completed'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_projects_by_ministry',
        category='projects',
        pattern=r'\b((show|list|display)\s+(me\s+)?)?(ppas?|projects?|programs?)\s+(by|from|of)\s+(?P<ministry>[\w\s]+?)(\?|$)',
        query_template='MonitoringEntry.objects.filter(implementing_agency__icontains="{ministry}").order_by("-created_at")[:30]',
        required_entities=['ministry'],
        optional_entities=[],
        examples=[
            'Show me projects by MSWDO',
            'List PPAs from MILG',
            'Display programs of BARMM',
            'Projects by Ministry of Health'
        ],
        priority=8,
        description='List projects by specific ministry/agency',
        tags=['list', 'projects', 'ministry', 'moa'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_projects_by_sector',
        category='projects',
        pattern=r'\b((show|list|display)\s+(me\s+)?)?(ppas?|projects?|programs?)\s+in\s+(?P<sector>[\w\s]+?)\s+sector',
        query_template='MonitoringEntry.objects.filter(sector__icontains="{sector}").order_by("-budget_allocation")[:30]',
        required_entities=['sector'],
        optional_entities=[],
        examples=[
            'Show me projects in education sector',
            'List PPAs in health sector',
            'Display programs in infrastructure sector',
            'Projects in economic sector'
        ],
        priority=8,
        description='List projects by sector',
        tags=['list', 'projects', 'sector'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_projects_by_location',
        category='projects',
        pattern=r'\b((show|list|display)\s+(me\s+)?)?(ppas?|projects?|programs?)\s+(in|at|within|from)\s+(?P<location>[\w\s]+?)(\?|$)',
        query_template='MonitoringEntry.objects.filter(Q(location__icontains="{location}")).order_by("-start_date")[:30]',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Show me projects in Region IX',
            'List PPAs in Zamboanga',
            'Display programs in Cotabato',
            'Projects in Region XII'
        ],
        priority=8,
        description='List projects in specific location',
        tags=['list', 'projects', 'location'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_recent_projects',
        category='projects',
        pattern=r'\b(recent|latest|new|newly added)\s+(ppas?|projects?|programs?)\b',
        query_template='MonitoringEntry.objects.all().order_by("-created_at")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Recent projects',
            'Latest PPAs',
            'Newly added programs',
            'Show recent projects'
        ],
        priority=7,
        description='List recently added projects',
        tags=['list', 'projects', 'recent'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_projects_by_type',
        category='projects',
        pattern=r'\b((show|list|display|get)\s+(me\s+)?(all\s+)?)?(?P<type>projects?|programs?|activities)\b',
        query_template='MonitoringEntry.objects.filter(entry_type__icontains="{type}").order_by("-created_at")[:30]',
        required_entities=['type'],
        optional_entities=[],
        examples=[
            'Show me project entries',
            'List program PPAs',
            'Display activity entries',
            'Show programs'
        ],
        priority=7,
        description='List entries by type (project/program/activity)',
        tags=['list', 'projects', 'type'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_high_budget_projects',
        category='projects',
        pattern=r'\b((show|list|display)\s+(me\s+)?)?(ppas?|projects?|programs?)\s+(with\s+)?((high|large)\s+)?(budgets?|large budgets?)\b',
        query_template='MonitoringEntry.objects.filter(budget_allocation__gte=10000000).order_by("-budget_allocation")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me high budget projects',
            'List large budget PPAs',
            'Display high budget programs',
            'Projects with large budgets'
        ],
        priority=7,
        description='List projects with budget over 10M',
        tags=['list', 'projects', 'budget', 'high'],
        result_type='list'
    ),
    QueryTemplate(
        id='list_overdue_projects',
        category='projects',
        pattern=r'\b(show|list|display)\s+(me\s+)?(overdue|delayed|late)\s+(ppas?|projects?|programs?)\b',
        query_template='MonitoringEntry.objects.filter(end_date__lt=timezone.now().date(), status="ongoing").order_by("end_date")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me overdue projects',
            'List delayed PPAs',
            'Display late programs',
            'Get overdue projects'
        ],
        priority=8,
        description='List overdue projects',
        tags=['list', 'projects', 'overdue', 'delayed'],
        result_type='list'
    ),
]


# =============================================================================
# PROJECT COUNT TEMPLATES (10 templates)
# =============================================================================

PROJECTS_COUNT_TEMPLATES = [
    QueryTemplate(
        id='count_total_projects',
        category='projects',
        pattern=r'\b(how many|total|count|number of)\s+(ppas?|projects?|programs?|activities)\b',
        query_template='MonitoringEntry.objects.count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many projects are there?',
            'Total PPAs',
            'Count all projects',
            'Number of programs',
            'How many activities?'
        ],
        priority=7,
        description='Count total projects/PPAs',
        tags=['count', 'projects', 'total'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_active_projects',
        category='projects',
        pattern=r'\b(how many|count|total)\s+(active|ongoing)\s+(ppas?|projects?|programs?)\b',
        query_template='MonitoringEntry.objects.filter(status="ongoing").count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many active projects?',
            'Count ongoing PPAs',
            'Total active programs',
            'Number of ongoing projects'
        ],
        priority=8,
        description='Count active/ongoing projects',
        tags=['count', 'projects', 'active', 'ongoing'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_completed_projects',
        category='projects',
        pattern=r'\b(how many|count|total)\s+(completed|finished|done)\s+(ppas?|projects?|programs?)\b',
        query_template='MonitoringEntry.objects.filter(status="completed").count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many completed projects?',
            'Count finished PPAs',
            'Total completed programs',
            'Number of done projects'
        ],
        priority=8,
        description='Count completed projects',
        tags=['count', 'projects', 'completed'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_projects_by_ministry',
        category='projects',
        pattern=r'\b(how many|count|total)\s+(ppas?|projects?|programs?)\s+(by|from|of)\s+(?P<ministry>[\w\s]+?)(\?|$)',
        query_template='MonitoringEntry.objects.filter(implementing_agency__icontains="{ministry}").count()',
        required_entities=['ministry'],
        optional_entities=[],
        examples=[
            'How many projects by MSWDO?',
            'Count PPAs from MILG',
            'Total programs of BARMM',
            'Projects by Ministry of Health'
        ],
        priority=9,
        description='Count projects by ministry/agency',
        tags=['count', 'projects', 'ministry', 'moa'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_projects_by_sector',
        category='projects',
        pattern=r'\b(how many|count|total)\s+(ppas?|projects?|programs?)\s+in\s+(?P<sector>[\w\s]+?)\s+sector',
        query_template='MonitoringEntry.objects.filter(sector__icontains="{sector}").count()',
        required_entities=['sector'],
        optional_entities=[],
        examples=[
            'How many projects in education sector?',
            'Count PPAs in health sector',
            'Total programs in infrastructure sector',
            'Projects in economic sector'
        ],
        priority=9,
        description='Count projects by sector',
        tags=['count', 'projects', 'sector'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_projects_by_location',
        category='projects',
        pattern=r'\b(how many|count|total)\s+(ppas?|projects?|programs?)\s+(in|at|within|from)\s+(?P<location>[\w\s]+?)(\?|$)',
        query_template='MonitoringEntry.objects.filter(Q(location__icontains="{location}")).count()',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'How many projects in Region IX?',
            'Count PPAs in Zamboanga',
            'Total programs in Cotabato',
            'Projects in Region XII'
        ],
        priority=9,
        description='Count projects in location',
        tags=['count', 'projects', 'location'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_projects_by_type',
        category='projects',
        pattern=r'\b(how many|count|total|number of)\s+(?P<type>project|program|activity)s?(?:\s+(entries?|ppas?))?\b',
        query_template='MonitoringEntry.objects.filter(entry_type__icontains="{type}").count()',
        required_entities=['type'],
        optional_entities=[],
        examples=[
            'How many project entries?',
            'Count program PPAs',
            'Total activity entries',
            'Number of programs'
        ],
        priority=8,
        description='Count entries by type',
        tags=['count', 'projects', 'type'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_overdue_projects',
        category='projects',
        pattern=r'\b(how many|count|total)\s+(overdue|delayed|late)\s+(ppas?|projects?|programs?)\b',
        query_template='MonitoringEntry.objects.filter(end_date__lt=timezone.now().date(), status="ongoing").count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many overdue projects?',
            'Count delayed PPAs',
            'Total late programs',
            'Number of overdue projects'
        ],
        priority=9,
        description='Count overdue projects',
        tags=['count', 'projects', 'overdue', 'delayed'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_projects_by_year',
        category='projects',
        pattern=r'\b(how many|count|total)\s+(ppas?|projects?|programs?)\s+(in|started in|from)\s+(?P<year>\d{4})',
        query_template='MonitoringEntry.objects.filter(start_date__year={year}).count()',
        required_entities=['year'],
        optional_entities=[],
        examples=[
            'How many projects in 2025?',
            'Count PPAs started in 2024',
            'Total programs from 2023',
            'Projects in 2024'
        ],
        priority=8,
        description='Count projects by year',
        tags=['count', 'projects', 'year'],
        result_type='count'
    ),
    QueryTemplate(
        id='count_projects_ending_soon',
        category='projects',
        pattern=r'\b(how many|count|total)\s+(ppas?|projects?|programs?)\s+ending\s+soon',
        query_template='MonitoringEntry.objects.filter(end_date__gte=timezone.now().date(), end_date__lte=timezone.now().date() + timedelta(days=30), status="ongoing").count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many projects ending soon?',
            'Count PPAs ending this month',
            'Total programs ending soon',
            'Projects ending within 30 days'
        ],
        priority=8,
        description='Count projects ending within 30 days',
        tags=['count', 'projects', 'ending', 'soon'],
        result_type='count'
    ),
]


# =============================================================================
# BUDGET ANALYSIS TEMPLATES (10 templates)
# =============================================================================

PROJECTS_BUDGET_TEMPLATES = [
    QueryTemplate(
        id='total_budget_allocation',
        category='projects',
        pattern=r'\b(total|overall|combined)\s+(budget|allocation)\s+(for\s+)?(ppas?|projects?|programs?)?',
        query_template='MonitoringEntry.objects.aggregate(total=Sum("budget_allocation"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Total budget allocation',
            'Overall budget for PPAs',
            'Combined project budget',
            'What is the total budget?'
        ],
        priority=8,
        description='Total budget allocation across all projects',
        tags=['budget', 'total', 'allocation'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='budget_by_sector',
        category='projects',
        pattern=r'\bbudget\s+(by|per|for each)\s+sector',
        query_template='MonitoringEntry.objects.values("sector").annotate(total_budget=Sum("budget_allocation")).order_by("-total_budget")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Budget by sector',
            'Budget per sector',
            'Budget for each sector',
            'Sector budget breakdown'
        ],
        priority=8,
        description='Budget breakdown by sector',
        tags=['budget', 'sector', 'breakdown'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='budget_by_ministry',
        category='projects',
        pattern=r'\bbudget\s+(by|per|for each)\s+(ministry|agency|moa)',
        query_template='MonitoringEntry.objects.values("implementing_agency").annotate(total_budget=Sum("budget_allocation")).order_by("-total_budget")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Budget by ministry',
            'Budget per agency',
            'Budget for each MOA',
            'Ministry budget breakdown'
        ],
        priority=8,
        description='Budget breakdown by ministry/agency',
        tags=['budget', 'ministry', 'moa', 'breakdown'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='budget_utilization_rate',
        category='projects',
        pattern=r'\bbudget\s+(utilization|usage|spending)\s+(rate|percentage)?',
        query_template='MonitoringEntry.objects.aggregate(total_allocated=Sum("budget_allocation"), total_utilized=Sum("budget_utilized"), total_balance=Sum("budget_balance"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Budget utilization rate',
            'Budget usage percentage',
            'Budget spending rate',
            'Show me budget utilization'
        ],
        priority=8,
        description='Overall budget utilization statistics',
        tags=['budget', 'utilization', 'rate'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='underutilized_budget_projects',
        category='projects',
        pattern=r'\b(underutilized|low utilization|unused)\s+budget\s+(ppas?|projects?|programs?)',
        query_template='MonitoringEntry.objects.filter(budget_utilized__lt=F("budget_allocation") * 0.5, status="ongoing").order_by("-budget_balance")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Underutilized budget projects',
            'Low utilization PPAs',
            'Projects with unused budget',
            'Budget underutilization'
        ],
        priority=8,
        description='Projects with low budget utilization (<50%)',
        tags=['budget', 'underutilized', 'low'],
        result_type='list'
    ),
    QueryTemplate(
        id='budget_by_location',
        category='projects',
        pattern=r'\bbudget\s+(in|for|allocated to)\s+(?P<location>[\w\s]+?)(\?|$)',
        query_template='MonitoringEntry.objects.filter(Q(location__icontains="{location}")).aggregate(total=Sum("budget_allocation"))["total"]',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Budget in Region IX',
            'Budget for Zamboanga',
            'Budget allocated to Cotabato',
            'Total budget in Region XII'
        ],
        priority=9,
        description='Total budget in specific location',
        tags=['budget', 'location', 'total'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='budget_range_projects',
        category='projects',
        pattern=r'\b(ppas?|projects?|programs?)\s+with\s+budget\s+(from|between)\s+(?P<min_budget>[\d,]+)\s+(to|and)\s+(?P<max_budget>[\d,]+)',
        query_template='MonitoringEntry.objects.filter(budget_allocation__gte={min_budget}, budget_allocation__lte={max_budget}).count()',
        required_entities=['min_budget', 'max_budget'],
        optional_entities=[],
        examples=[
            'Projects with budget from 1000000 to 5000000',
            'PPAs with budget between 500000 and 2000000',
            'Programs with budget from 2M to 10M'
        ],
        priority=8,
        description='Projects within budget range',
        tags=['budget', 'range', 'filter'],
        result_type='count'
    ),
    QueryTemplate(
        id='top_budget_projects',
        category='projects',
        pattern=r'\b(top|highest|largest)\s+(budget|funded)\s+(ppas?|projects?|programs?)',
        query_template='MonitoringEntry.objects.filter(budget_allocation__isnull=False).order_by("-budget_allocation")[:10]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Top budget projects',
            'Highest funded PPAs',
            'Largest budget programs',
            'Show me top funded projects'
        ],
        priority=7,
        description='Top 10 projects by budget',
        tags=['budget', 'top', 'highest'],
        result_type='list'
    ),
    QueryTemplate(
        id='budget_balance_analysis',
        category='projects',
        pattern=r'\bbudget\s+(balance|remaining|left)',
        query_template='MonitoringEntry.objects.aggregate(total_balance=Sum("budget_balance"), total_allocated=Sum("budget_allocation"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Budget balance',
            'Budget remaining',
            'How much budget is left?',
            'Total budget balance'
        ],
        priority=7,
        description='Total budget balance/remaining',
        tags=['budget', 'balance', 'remaining'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='budget_overrun_projects',
        category='projects',
        pattern=r'\b(budget\s+overrun|over budget|exceeded budget)\s+(ppas?|projects?|programs?)',
        query_template='MonitoringEntry.objects.filter(budget_utilized__gt=F("budget_allocation")).order_by("-budget_utilized")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Budget overrun projects',
            'Over budget PPAs',
            'Projects that exceeded budget',
            'Budget overruns'
        ],
        priority=8,
        description='Projects with budget overruns',
        tags=['budget', 'overrun', 'exceeded'],
        result_type='list'
    ),
]


# =============================================================================
# IMPACT & BENEFICIARY TEMPLATES (8 templates)
# =============================================================================

PROJECTS_IMPACT_TEMPLATES = [
    QueryTemplate(
        id='total_beneficiaries',
        category='projects',
        pattern=r'\b(total|overall|combined)\s+(beneficiaries|people served|target population)',
        query_template='MonitoringEntry.objects.aggregate(total=Sum("target_beneficiaries"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Total beneficiaries',
            'Overall people served',
            'Combined target population',
            'How many beneficiaries?'
        ],
        priority=8,
        description='Total beneficiaries across all projects',
        tags=['impact', 'beneficiaries', 'total'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='beneficiaries_by_sector',
        category='projects',
        pattern=r'\bbeneficiaries\s+(by|per|in)\s+sector',
        query_template='MonitoringEntry.objects.values("sector").annotate(total_beneficiaries=Sum("target_beneficiaries")).order_by("-total_beneficiaries")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Beneficiaries by sector',
            'Beneficiaries per sector',
            'Beneficiaries in each sector',
            'Sector beneficiary breakdown'
        ],
        priority=8,
        description='Beneficiaries by sector',
        tags=['impact', 'beneficiaries', 'sector'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='beneficiaries_by_location',
        category='projects',
        pattern=r'\bbeneficiaries\s+(in|at|from)\s+(?P<location>[\w\s]+?)(\?|$)',
        query_template='MonitoringEntry.objects.filter(Q(location__icontains="{location}")).aggregate(total=Sum("target_beneficiaries"))["total"]',
        required_entities=['location'],
        optional_entities=[],
        examples=[
            'Beneficiaries in Region IX',
            'Beneficiaries at Zamboanga',
            'Beneficiaries from Cotabato',
            'People served in Region XII'
        ],
        priority=9,
        description='Total beneficiaries in location',
        tags=['impact', 'beneficiaries', 'location'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='project_outcomes',
        category='projects',
        pattern=r'\b(project|ppa|program)\s+(outcomes|results|achievements|impact)',
        query_template='MonitoringEntry.objects.filter(status="completed").values("id", "title", "outcomes", "target_beneficiaries", "actual_beneficiaries")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Project outcomes',
            'PPA results',
            'Program achievements',
            'Project impact'
        ],
        priority=7,
        description='Project outcomes and achievements',
        tags=['impact', 'outcomes', 'results'],
        result_type='list'
    ),
    QueryTemplate(
        id='highest_impact_projects',
        category='projects',
        pattern=r'\b(highest|most|top)\s+impact\s+(ppas?|projects?|programs?)',
        query_template='MonitoringEntry.objects.filter(actual_beneficiaries__isnull=False).order_by("-actual_beneficiaries")[:10]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Highest impact projects',
            'Most impact PPAs',
            'Top impact programs',
            'Projects with highest impact'
        ],
        priority=7,
        description='Projects with highest beneficiary impact',
        tags=['impact', 'highest', 'beneficiaries'],
        result_type='list'
    ),
    QueryTemplate(
        id='beneficiary_reach_rate',
        category='projects',
        pattern=r'\bbeneficiary\s+(reach|achievement|attainment)\s+(rate|percentage)',
        query_template='MonitoringEntry.objects.filter(target_beneficiaries__gt=0, actual_beneficiaries__isnull=False).annotate(reach_rate=ExpressionWrapper(F("actual_beneficiaries") / F("target_beneficiaries") * 100, output_field=FloatField())).values("id", "title", "target_beneficiaries", "actual_beneficiaries", "reach_rate")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Beneficiary reach rate',
            'Beneficiary achievement percentage',
            'Beneficiary attainment rate',
            'How many beneficiaries reached?'
        ],
        priority=7,
        description='Beneficiary reach/achievement rates',
        tags=['impact', 'beneficiaries', 'rate'],
        result_type='list'
    ),
    QueryTemplate(
        id='communities_served',
        category='projects',
        pattern=r'\b(communities|barangays)\s+(served|reached|covered|benefited)',
        query_template='MonitoringEntry.objects.aggregate(total=Sum("communities_served"))["total"]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Communities served',
            'Barangays reached',
            'Communities covered',
            'How many communities benefited?'
        ],
        priority=7,
        description='Total communities served by projects',
        tags=['impact', 'communities', 'served'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='sector_impact_comparison',
        category='projects',
        pattern=r'\b(compare|comparison)\s+(impact|outcomes|results)\s+(by|across)\s+sectors?',
        query_template='MonitoringEntry.objects.values("sector").annotate(total_beneficiaries=Sum("actual_beneficiaries"), total_projects=Count("id"), avg_completion=Avg("completion_percentage")).order_by("-total_beneficiaries")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Compare impact by sector',
            'Comparison of outcomes across sectors',
            'Compare results by sector',
            'Sector impact comparison'
        ],
        priority=7,
        description='Compare impact across sectors',
        tags=['impact', 'comparison', 'sector'],
        result_type='aggregate'
    ),
]


# =============================================================================
# TIMELINE & MONITORING TEMPLATES (7 templates)
# =============================================================================

PROJECTS_TIMELINE_TEMPLATES = [
    QueryTemplate(
        id='project_completion_rates',
        category='projects',
        pattern=r'\b(project|ppa|program)\s+completion\s+(rates?|percentage|status)',
        query_template='MonitoringEntry.objects.aggregate(avg_completion=Avg("completion_percentage"), total=Count("id"), completed=Count("id", filter=Q(status="completed")))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Project completion rates',
            'PPA completion percentage',
            'Program completion status',
            'Overall completion rates'
        ],
        priority=8,
        description='Overall completion statistics',
        tags=['timeline', 'completion', 'rate'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='projects_ending_this_month',
        category='projects',
        pattern=r'\b(ppas?|projects?|programs?)\s+ending\s+(this month|soon|this quarter)',
        query_template='MonitoringEntry.objects.filter(end_date__gte=timezone.now().date(), end_date__lte=timezone.now().date() + timedelta(days=30), status="ongoing").order_by("end_date")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Projects ending this month',
            'PPAs ending soon',
            'Programs ending this quarter',
            'Projects ending within 30 days'
        ],
        priority=8,
        description='Projects ending within 30 days',
        tags=['timeline', 'ending', 'soon'],
        result_type='list'
    ),
    QueryTemplate(
        id='project_timeline_by_year',
        category='projects',
        pattern=r'\b(ppas?|projects?|programs?)\s+timeline\s+(by|in)\s+(?P<year>\d{4})',
        query_template='MonitoringEntry.objects.filter(start_date__year={year}).values("id", "title", "start_date", "end_date", "status", "completion_percentage").order_by("start_date")[:30]',
        required_entities=['year'],
        optional_entities=[],
        examples=[
            'Projects timeline by 2025',
            'PPAs timeline in 2024',
            'Programs timeline by 2023',
            'Show project timeline in 2025'
        ],
        priority=8,
        description='Project timeline by year',
        tags=['timeline', 'year'],
        result_type='list'
    ),
    QueryTemplate(
        id='active_project_timeline',
        category='projects',
        pattern=r'\b(active|ongoing)\s+(ppas?|projects?|programs?)\s+timeline',
        query_template='MonitoringEntry.objects.filter(status="ongoing").values("id", "title", "start_date", "end_date", "completion_percentage").order_by("end_date")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Active projects timeline',
            'Ongoing PPAs timeline',
            'Active programs timeline',
            'Show ongoing project timeline'
        ],
        priority=7,
        description='Timeline of active projects',
        tags=['timeline', 'active', 'ongoing'],
        result_type='list'
    ),
    QueryTemplate(
        id='delayed_projects_analysis',
        category='projects',
        pattern=r'\b(delayed|overdue|late|behind schedule)\s+(ppas?|projects?|programs?)\s+(analysis|report)',
        query_template='MonitoringEntry.objects.filter(end_date__lt=timezone.now().date(), status="ongoing").annotate(delay_days=ExpressionWrapper(timezone.now().date() - F("end_date"), output_field=DurationField())).order_by("-delay_days")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Delayed projects analysis',
            'Overdue PPAs report',
            'Late programs analysis',
            'Projects behind schedule'
        ],
        priority=8,
        description='Analysis of delayed/overdue projects',
        tags=['timeline', 'delayed', 'overdue', 'analysis'],
        result_type='list'
    ),
    QueryTemplate(
        id='completion_by_quarter',
        category='projects',
        pattern=r'\b(ppas?|projects?|programs?)\s+completion\s+by\s+quarter',
        query_template='MonitoringEntry.objects.filter(status="completed").annotate(quarter=ExtractQuarter("end_date"), year=ExtractYear("end_date")).values("year", "quarter").annotate(count=Count("id")).order_by("-year", "-quarter")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Projects completion by quarter',
            'PPAs completion by quarter',
            'Program completion by quarter',
            'Quarterly completion report'
        ],
        priority=7,
        description='Project completion by quarter',
        tags=['timeline', 'completion', 'quarter'],
        result_type='aggregate'
    ),
    QueryTemplate(
        id='project_duration_analysis',
        category='projects',
        pattern=r'\b(project|ppa|program)\s+duration\s+(analysis|average|statistics)',
        query_template='MonitoringEntry.objects.filter(start_date__isnull=False, end_date__isnull=False).annotate(duration=ExpressionWrapper(F("end_date") - F("start_date"), output_field=DurationField())).aggregate(avg_duration=Avg("duration"), min_duration=Min("duration"), max_duration=Max("duration"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Project duration analysis',
            'PPA duration average',
            'Program duration statistics',
            'Average project duration'
        ],
        priority=7,
        description='Project duration statistics',
        tags=['timeline', 'duration', 'analysis'],
        result_type='aggregate'
    ),
]


# =============================================================================
# COMBINE ALL TEMPLATES
# =============================================================================

PROJECTS_TEMPLATES = (
    PROJECTS_LIST_TEMPLATES +
    PROJECTS_COUNT_TEMPLATES +
    PROJECTS_BUDGET_TEMPLATES +
    PROJECTS_IMPACT_TEMPLATES +
    PROJECTS_TIMELINE_TEMPLATES
)

# Total: 10 + 10 + 10 + 8 + 7 = 45 templates with 150+ example query variations
# Original: 25 templates | Added: 20 templates | New Total: 45 templates
