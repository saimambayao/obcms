"""Budget Preparation URL Configuration

URL patterns for budget preparation views and HTMX endpoints.
Implements Parliament Bill No. 325 budget workflows.
"""

from django.urls import path
from . import views

app_name = 'budget_preparation'

urlpatterns = [
    # Dashboard
    path('', views.budget_dashboard, name='dashboard'),

    # Budget Proposal URLs
    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposals/create/', views.proposal_create, name='proposal_create'),
    path('proposals/<int:pk>/', views.proposal_detail, name='proposal_detail'),
    path('proposals/<int:pk>/edit/', views.proposal_edit, name='proposal_edit'),
    path('proposals/<int:pk>/delete/', views.proposal_delete, name='proposal_delete'),
    path('proposals/<int:pk>/submit/', views.proposal_submit, name='proposal_submit'),
    path('proposals/<int:pk>/approve/', views.proposal_approve, name='proposal_approve'),
    path('proposals/<int:pk>/reject/', views.proposal_reject, name='proposal_reject'),

    # Program Budget URLs
    path('proposals/<int:proposal_pk>/programs/create/', views.program_create, name='program_create'),
    path('programs/<int:pk>/edit/', views.program_edit, name='program_edit'),
    path('programs/<int:pk>/delete/', views.program_delete, name='program_delete'),

    # HTMX API Endpoints
    path('api/stats/', views.proposal_stats, name='proposal_stats'),
    path('api/recent-proposals/', views.recent_proposals_partial, name='recent_proposals_partial'),
]
