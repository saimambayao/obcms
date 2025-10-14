"""
OCM URL Configuration

URL patterns for OCM (Office of the Chief Minister) views.
App namespace: 'ocm'
"""
from django.urls import path

from . import views

app_name = 'ocm'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.ocm_dashboard, name='dashboard'),
    
    # Budget
    path('budget/', views.consolidated_budget, name='consolidated_budget'),
    path('budget/<str:org_code>/', views.moa_budget_detail, name='moa_budget_detail'),
    
    # Planning
    path('planning/', views.planning_overview, name='planning_overview'),
    path('planning/<str:org_code>/', views.moa_planning_detail, name='moa_planning_detail'),
    
    # Coordination
    path('coordination/', views.coordination_matrix, name='coordination_matrix'),
    path('coordination/<int:pk>/', views.partnership_detail, name='partnership_detail'),
    
    # Performance
    path('performance/', views.performance_overview, name='performance_overview'),
    path('performance/<str:org_code>/', views.moa_performance_detail, name='moa_performance_detail'),
    
    # Reports
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    
    # API Endpoints
    path('api/stats/', views.api_government_stats, name='api_government_stats'),
    path('api/filter/', views.api_filter_data, name='api_filter_data'),
]
