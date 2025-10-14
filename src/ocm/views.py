"""
OCM Views

Views for OCM (Office of the Chief Minister) dashboard and aggregation.
All views enforce read-only access and require OCM access.
"""
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .decorators import ocm_readonly_view
from .services.aggregation import OCMAggregationService

logger = logging.getLogger(__name__)


@login_required
@ocm_readonly_view
def ocm_dashboard(request):
    """
    Main OCM dashboard with government-wide statistics.
    
    Shows:
    - MOA count
    - Budget summary
    - Planning summary
    - Coordination summary
    - Performance metrics
    - All organizations list
    """
    context = {
        'gov_stats': OCMAggregationService.get_government_stats(),
        'budget_summary': OCMAggregationService.get_budget_summary(),
        'planning_summary': OCMAggregationService.get_planning_summary(),
        'coordination_summary': OCMAggregationService.get_coordination_summary(),
        'performance_metrics': OCMAggregationService.get_performance_metrics(),
        'all_organizations': OCMAggregationService.get_all_organizations(),
    }
    
    return render(request, 'ocm/dashboard/main.html', context)


@login_required
@ocm_readonly_view
def consolidated_budget(request):
    """
    Consolidated budget view with fiscal year filter.
    
    Shows budget data across all MOAs.
    """
    fiscal_year = request.GET.get('fiscal_year')
    if fiscal_year:
        fiscal_year = int(fiscal_year)
    
    # Get available fiscal years
    current_year = timezone.now().year
    available_years = [current_year, current_year - 1, current_year - 2]
    
    context = {
        'budget_data': OCMAggregationService.get_consolidated_budget(fiscal_year),
        'budget_summary': OCMAggregationService.get_budget_summary(fiscal_year),
        'fiscal_year': fiscal_year or current_year,
        'available_years': available_years,
    }
    
    return render(request, 'ocm/budget/consolidated.html', context)



@login_required
@ocm_readonly_view
def moa_budget_detail(request, org_code):
    """Detailed budget for specific MOA"""
    from organizations.models import Organization
    
    organization = get_object_or_404(Organization, code=org_code)
    
    # Get budget data for this organization
    all_budget_data = OCMAggregationService.get_consolidated_budget()
    org_budget = next(
        (b for b in all_budget_data if b['organization_code'] == org_code),
        None
    )
    
    context = {
        'organization': organization,
        'budget_data': org_budget,
    }
    
    return render(request, 'ocm/budget/detail.html', context)


@login_required
@ocm_readonly_view
def planning_overview(request):
    """Strategic planning status across all MOAs"""
    context = {
        'planning_status': OCMAggregationService.get_strategic_planning_status(),
        'planning_summary': OCMAggregationService.get_planning_summary(),
    }
    
    return render(request, 'ocm/planning/overview.html', context)


@login_required
@ocm_readonly_view
def moa_planning_detail(request, org_code):
    """Planning details for specific MOA"""
    from organizations.models import Organization
    
    organization = get_object_or_404(Organization, code=org_code)
    
    # Get planning data for this organization
    planning_status = OCMAggregationService.get_strategic_planning_status()
    org_planning = next(
        (p for p in planning_status['by_organization'] if p['organization_code'] == org_code),
        None
    )
    
    context = {
        'organization': organization,
        'planning_data': org_planning,
    }
    
    return render(request, 'ocm/planning/detail.html', context)


@login_required
@ocm_readonly_view
def coordination_matrix(request):
    """Inter-MOA partnerships visualization"""
    context = {
        'partnerships': OCMAggregationService.get_inter_moa_partnerships(),
        'coordination_summary': OCMAggregationService.get_coordination_summary(),
    }
    
    return render(request, 'ocm/coordination/matrix.html', context)


@login_required
@ocm_readonly_view
def partnership_detail(request, pk):
    """Partnership details"""
    partnerships = OCMAggregationService.get_inter_moa_partnerships()
    partnership = next((p for p in partnerships if p['id'] == pk), None)
    
    if not partnership:
        from django.http import Http404
        raise Http404("Partnership not found")
    
    context = {
        'partnership': partnership,
    }
    
    return render(request, 'ocm/coordination/detail.html', context)


@login_required
@ocm_readonly_view
def performance_overview(request):
    """Government-wide performance metrics"""
    context = {
        'performance_metrics': OCMAggregationService.get_performance_metrics(),
        'all_organizations': OCMAggregationService.get_all_organizations(),
    }
    
    return render(request, 'ocm/performance/overview.html', context)


@login_required
@ocm_readonly_view
def moa_performance_detail(request, org_code):
    """MOA-specific performance"""
    from organizations.models import Organization
    
    organization = get_object_or_404(Organization, code=org_code)
    
    # Get performance data for this organization (placeholder)
    context = {
        'organization': organization,
        'performance_data': {
            'budget_efficiency': 85,
            'program_delivery': 78,
            'stakeholder_satisfaction': 82,
        }
    }
    
    return render(request, 'ocm/performance/detail.html', context)


@login_required
@ocm_readonly_view
def reports_list(request):
    """Available report types"""
    context = {
        'report_types': [
            {
                'name': 'Budget Report',
                'description': 'Comprehensive budget analysis across all MOAs',
                'features': ['Budget allocation', 'Utilization rates', 'Comparative analysis']
            },
            {
                'name': 'Planning Report',
                'description': 'Strategic planning status and progress',
                'features': ['Strategic plans', 'Annual work plans', 'Completion rates']
            },
            {
                'name': 'Coordination Report',
                'description': 'Inter-MOA partnerships and collaboration',
                'features': ['Active partnerships', 'Collaborative networks', 'Success metrics']
            },
            {
                'name': 'Performance Report',
                'description': 'Government-wide performance metrics',
                'features': ['KPI tracking', 'Trend analysis', 'Benchmarking']
            },
            {
                'name': 'Executive Summary',
                'description': 'High-level overview for executive decision-making',
                'features': ['Key statistics', 'Critical insights', 'Recommendations']
            },
            {
                'name': 'Custom Report',
                'description': 'Build your own report with selected metrics',
                'features': ['Flexible parameters', 'Multiple data sources', 'Export options']
            },
        ]
    }
    
    return render(request, 'ocm/reports/list.html', context)


@login_required
@ocm_readonly_view
def generate_report(request):
    """Report generation form"""
    # Placeholder - full implementation in future phase
    context = {
        'message': 'Report generation feature coming soon'
    }
    
    return render(request, 'ocm/reports/generate.html', context)


# API Views

@login_required
@ocm_readonly_view
def api_government_stats(request):
    """JSON endpoint for government statistics"""
    stats = OCMAggregationService.get_government_stats()
    
    # Convert Decimal to float for JSON serialization
    for key, value in stats.items():
        if hasattr(value, '__float__'):
            stats[key] = float(value)
    
    return JsonResponse(stats)


@login_required
@ocm_readonly_view
def api_filter_data(request):
    """JSON endpoint for filtering data"""
    filter_type = request.GET.get('type', 'budget')
    fiscal_year = request.GET.get('fiscal_year')
    
    if filter_type == 'budget':
        data = OCMAggregationService.get_consolidated_budget(
            int(fiscal_year) if fiscal_year else None
        )
    elif filter_type == 'planning':
        data = OCMAggregationService.get_strategic_planning_status()
    elif filter_type == 'coordination':
        data = OCMAggregationService.get_inter_moa_partnerships()
    else:
        data = []
    
    return JsonResponse({'data': data})
