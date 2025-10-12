"""
Budget Execution URL Configuration
Phase 2B: Budget Execution (Parliament Bill No. 325 Section 78)

URL patterns for budget execution views.
"""

from django.urls import path
from . import views

app_name = 'budget_execution'

urlpatterns = [
    # ========================================================================
    # DASHBOARD
    # ========================================================================
    path('', views.budget_dashboard, name='dashboard'),

    # ========================================================================
    # ALLOTMENTS
    # ========================================================================
    path('allotments/', views.allotment_list, name='allotment_list'),
    path('allotments/release/', views.allotment_release, name='allotment_release'),
    path('allotments/<uuid:pk>/', views.allotment_detail, name='allotment_detail'),
    path('allotments/<uuid:pk>/approve/', views.allotment_approve, name='allotment_approve'),

    # ========================================================================
    # OBLIGATIONS
    # ========================================================================
    path('obligations/', views.obligation_list, name='obligation_list'),
    path('obligations/create/', views.obligation_create, name='obligation_create'),
    path('obligations/<uuid:pk>/', views.obligation_detail, name='obligation_detail'),
    path('obligations/<uuid:pk>/edit/', views.obligation_edit, name='obligation_edit'),

    # ========================================================================
    # DISBURSEMENTS
    # ========================================================================
    path('disbursements/', views.disbursement_list, name='disbursement_list'),
    path('disbursements/record/', views.disbursement_record, name='disbursement_record'),
    path('disbursements/<uuid:pk>/', views.disbursement_detail, name='disbursement_detail'),

    # ========================================================================
    # HTMX PARTIALS & AJAX ENDPOINTS
    # ========================================================================
    path('ajax/recent-transactions/', views.recent_transactions, name='recent_transactions'),
    path('ajax/pending-approvals/', views.pending_approvals, name='pending_approvals'),
    path('ajax/budget-alerts/', views.budget_alerts, name='budget_alerts'),
    path('ajax/budget-details/', views.get_budget_details, name='get_budget_details'),

    # Aliases for template compatibility
    path('ajax/allotment-balance/', views.get_budget_details, name='get_allotment_balance'),
    path('ajax/obligation-details/', views.get_budget_details, name='get_obligation_details'),

    # Form aliases (for template URL compatibility)
    path('obligation/form/', views.obligation_create, name='obligation_form'),
    path('disbursement/form/', views.disbursement_record, name='disbursement_form'),
]
