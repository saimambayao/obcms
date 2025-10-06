"""
Policy Module URL Configuration

URL patterns for policy tracking, recommendations, and AI-powered
policy analysis features.
"""

from django.urls import path
from . import views

app_name = "policies"

urlpatterns = [
    # AI Intelligence Endpoints - TODO: Implement these views
    # path(
    #     'ai/gather-evidence/<int:pk>/',
    #     views.ai_gather_evidence,
    #     name='ai-gather-evidence'
    # ),
    # path(
    #     'ai/generate-policy/<int:pk>/',
    #     views.ai_generate_policy,
    #     name='ai-generate-policy'
    # ),
    # path(
    #     'ai/simulate-impact/<int:pk>/',
    #     views.ai_simulate_impact,
    #     name='ai-simulate-impact'
    # ),
    # path(
    #     'ai/check-compliance/<int:pk>/',
    #     views.ai_check_compliance,
    #     name='ai-check-compliance'
    # ),
]
