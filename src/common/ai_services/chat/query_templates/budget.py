"""
Budget Ceiling Tracking Query Templates for OBCMS Chat System

7 high-value, low-complexity templates for querying budget ceiling and allocation data.
Simple filter/aggregate queries for immediate deployment.

Key Models:
- BudgetCeiling: Tracks budget ceilings by sector, funding source, and fiscal year
- Project/Program/Activity models: Link to budget allocations

Budget Ceiling Fields:
- fiscal_year: Year (e.g., 2024, 2025)
- sector: Sector (economic, social, infrastructure, education, health, etc.)
- funding_source: Source (gaa, block_grant, lgu, donor, internal, others)
- ceiling_amount: Maximum budget limit
- allocated_amount: Amount currently allocated
- enforcement_level: Enforcement (strict, flexible, advisory, monitoring_only)
- is_active: Active status

Sectors:
- economic: Economic Development
- social: Social Development
- infrastructure: Infrastructure
- education: Education
- health: Health
- environment: Environment & Natural Resources
- governance: Governance & Institutions
- peace: Peace & Security
- cultural: Cultural Development

Funding Sources:
- gaa: General Appropriations Act (GAA)
- block_grant: Block Grant
- lgu: Local Government Unit
- donor: Donor Funding
- internal: Internal Revenue
- others: Others
"""

from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# BUDGET CEILING TRACKING TEMPLATES (7 templates)
# =============================================================================

BUDGET_TEMPLATES = [
    # Template 1: Budget ceiling utilization
    QueryTemplate(
        id='budget_ceiling_utilization',
        category='budget',
        pattern=r'\b(?:(show|list|which)\s+)?(budget|ceiling|ceilings?)\s+(?:are\s+)?(near\s*limit|utilization|usage|allocation)(?:\s+(rates?|levels?|percentages?))?(?:\s+by\s*sector)?',
        query_template="BudgetCeiling.objects.filter(is_active=True).annotate(utilization_rate=ExpressionWrapper(F('allocated_amount') / F('ceiling_amount') * 100, output_field=FloatField())).values('name', 'sector', 'fiscal_year', 'ceiling_amount', 'allocated_amount', 'utilization_rate').order_by('-utilization_rate')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Budget ceilings near limit',
            'Budget utilization by sector',
            'Show ceiling usage',
            'Budget allocation rates',
            'Which ceilings are near limit?'
        ],
        priority=9,
        description='Show budget ceiling utilization rates by sector',
        tags=['budget', 'utilization', 'ceiling'],
        result_type='aggregate'
    ),

    # Template 2: Remaining budget by sector
    QueryTemplate(
        id='remaining_budget_by_sector',
        category='budget',
        pattern=r'\b(remaining|available|unused)\s+budget\s+(by\s*sector|under\s*ceilings?)',
        query_template="BudgetCeiling.objects.filter(is_active=True).annotate(remaining=ExpressionWrapper(F('ceiling_amount') - F('allocated_amount'), output_field=DecimalField())).values('sector', 'fiscal_year', 'ceiling_amount', 'allocated_amount', 'remaining').order_by('sector', '-fiscal_year')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Remaining budget by sector',
            'Available budget under ceilings',
            'Unused budget by sector',
            'How much budget is left?',
            'Budget remaining under ceilings'
        ],
        priority=9,
        description='Calculate remaining budget under each ceiling by sector',
        tags=['budget', 'remaining', 'ceiling'],
        result_type='aggregate'
    ),

    # Template 3: Budget ceiling violations
    QueryTemplate(
        id='budget_ceiling_violations',
        category='budget',
        pattern=r'\b(allocations?|budgets?)\s+(exceeding|violating|over|above)\s+(ceilings?|limits?)',
        query_template="BudgetCeiling.objects.filter(is_active=True, allocated_amount__gt=F('ceiling_amount')).values('name', 'sector', 'fiscal_year', 'funding_source', 'ceiling_amount', 'allocated_amount', 'enforcement_level').order_by('-allocated_amount')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Allocations exceeding ceilings',
            'Budget violating limits',
            'Budgets over ceiling',
            'Which allocations exceed limits?',
            'Ceiling violations'
        ],
        priority=9,
        description='Identify allocations exceeding budget ceilings',
        tags=['budget', 'violations', 'ceiling'],
        result_type='list'
    ),

    # Template 4: Total budget by sector
    QueryTemplate(
        id='total_budget_by_sector',
        category='budget',
        pattern=r'\b(total|sum)\s+budget\s+(by\s*sector|allocated\s*by\s*sector)',
        query_template="BudgetCeiling.objects.filter(is_active=True).values('sector').annotate(total_ceiling=Sum('ceiling_amount'), total_allocated=Sum('allocated_amount')).order_by('-total_ceiling')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Total budget by sector',
            'Sum budget allocated by sector',
            'Budget totals per sector',
            'Sector budget summary',
            'How much budget per sector?'
        ],
        priority=8,
        description='Total budget allocated by sector',
        tags=['budget', 'sector', 'total'],
        result_type='aggregate'
    ),

    # Template 5: Total budget by fiscal year
    QueryTemplate(
        id='total_budget_by_fiscal_year',
        category='budget',
        pattern=r'\b(total|sum)\s+budget\s+(by|for|in)\s+(fiscal\s*year|FY|year)\s*(?P<fiscal_year>\d{4})?',
        query_template="BudgetCeiling.objects.filter(is_active=True, fiscal_year='{fiscal_year}').aggregate(total_ceiling=Sum('ceiling_amount'), total_allocated=Sum('allocated_amount'))" if '{fiscal_year}' else "BudgetCeiling.objects.filter(is_active=True).values('fiscal_year').annotate(total_ceiling=Sum('ceiling_amount'), total_allocated=Sum('allocated_amount')).order_by('-fiscal_year')",
        required_entities=[],
        optional_entities=['fiscal_year'],
        examples=[
            'Total budget by fiscal year',
            'Sum budget for FY 2025',
            'Budget totals in 2024',
            'How much budget per year?',
            'Budget by year'
        ],
        priority=8,
        description='Total budget by fiscal year',
        tags=['budget', 'fiscal_year', 'total'],
        result_type='aggregate'
    ),

    # Template 6: Total budget by funding source
    QueryTemplate(
        id='total_budget_by_funding_source',
        category='budget',
        pattern=r'\b(total|sum)\s+budget\s+(by|from)\s+(funding\s*source|GAA|block\s*grant|donor|LGU)',
        query_template="BudgetCeiling.objects.filter(is_active=True).values('funding_source').annotate(total_ceiling=Sum('ceiling_amount'), total_allocated=Sum('allocated_amount')).order_by('-total_ceiling')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Total budget by funding source',
            'Sum budget from GAA',
            'Budget totals by block grant',
            'How much from donor funding?',
            'Budget by LGU'
        ],
        priority=8,
        description='Total budget by funding source (GAA, block grant, donor, etc.)',
        tags=['budget', 'funding_source', 'total'],
        result_type='aggregate'
    ),

    # Template 7: Budget allocation vs utilization
    QueryTemplate(
        id='budget_allocation_vs_utilization',
        category='budget',
        pattern=r'\b(budget|allocation)\s+(vs|versus|compared\s*to)\s+(utilization|spending|disbursement)',
        query_template="BudgetCeiling.objects.filter(is_active=True).annotate(utilization_rate=ExpressionWrapper(F('allocated_amount') / F('ceiling_amount') * 100, output_field=FloatField()), remaining=ExpressionWrapper(F('ceiling_amount') - F('allocated_amount'), output_field=DecimalField())).values('sector', 'fiscal_year', 'funding_source', 'ceiling_amount', 'allocated_amount', 'utilization_rate', 'remaining').order_by('-utilization_rate')",
        required_entities=[],
        optional_entities=[],
        examples=[
            'Budget allocation vs utilization',
            'Allocation versus spending',
            'Compare budget to utilization',
            'Allocation compared to disbursement',
            'Budget vs actual spending'
        ],
        priority=8,
        description='Compare budget allocation vs utilization rates',
        tags=['budget', 'allocation', 'utilization'],
        result_type='aggregate'
    ),
]


# Export templates for registration
__all__ = ['BUDGET_TEMPLATES']
