"""
Policy Module URL Configuration

URL patterns for policy tracking, recommendations, and AI-powered
policy analysis features.

Phase 0.2 URL Refactoring:
- Migrated from common/urls.py (lines 283-310)
- 12 recommendations URLs moved to policies namespace
- Old URLs redirect via URL refactoring middleware
- Views still imported from common app (view migration is a future phase)
"""

from django.urls import path
from recommendations import views

app_name = "policies"

urlpatterns = [
    # Recommendations Module URLs (migrated from common:recommendations_*)
    # Using simplified names in policies namespace (e.g., 'home' instead of 'recommendations_home')
    path("", views.recommendations_home, name="home"),
    path("new/", views.recommendations_new, name="new"),
    path("manage/", views.recommendations_manage, name="manage"),
    path("area/<str:area_slug>/", views.recommendations_by_area, name="by_area"),

    # TODO: Implement these views and uncomment corresponding URL patterns
    # path("stats-cards/", views.recommendations_stats_cards, name="stats_cards"),
    # path("create/", views.recommendations_create, name="create"),
    # path("autosave/", views.recommendations_autosave, name="autosave"),
    # path("programs/", views.recommendations_programs, name="programs"),
    # path("services/", views.recommendations_services, name="services"),
    # path("<uuid:pk>/view/", views.recommendations_view, name="view"),
    # path("<uuid:pk>/edit/", views.recommendations_edit, name="edit"),
    # path("<uuid:pk>/delete/", views.recommendations_delete, name="delete"),

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
