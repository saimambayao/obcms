"""
Planning Module URL Configuration

URL patterns for strategic planning, annual work plans, goals, and objectives.

Implements RESTful URL conventions for:
- Strategic Plans (3-5 year planning documents)
- Strategic Goals (linked to strategic plans)
- Annual Work Plans (yearly implementation plans)
- Work Plan Objectives (linked to annual plans)

Phase 0 URL Refactoring:
- Clean RESTful structure with app namespace 'planning'
- Consistent naming conventions across all endpoints
- Follows OBCMS URL standards
"""

from django.urls import path
from . import views

app_name = "planning"

urlpatterns = [
    # Dashboard
    path("", views.planning_dashboard, name="dashboard"),

    # Strategic Plans
    path("strategic/", views.strategic_plan_list, name="strategic_list"),
    path("strategic/create/", views.strategic_plan_create, name="strategic_create"),
    path("strategic/<int:pk>/", views.strategic_plan_detail, name="strategic_detail"),
    path("strategic/<int:pk>/edit/", views.strategic_plan_edit, name="strategic_edit"),
    path("strategic/<int:pk>/delete/", views.strategic_plan_delete, name="strategic_delete"),

    # Strategic Goals
    path("goals/create/<int:plan_id>/", views.goal_create, name="goal_create"),
    path("goals/<int:pk>/edit/", views.goal_edit, name="goal_edit"),
    path("goals/<int:pk>/progress/", views.goal_update_progress, name="goal_update_progress"),
    path("goals/<int:pk>/delete/", views.goal_delete, name="goal_delete"),

    # Annual Work Plans
    path("annual/", views.annual_plan_list, name="annual_list"),
    path("annual/create/", views.annual_plan_create, name="annual_create"),
    path("annual/<int:pk>/", views.annual_plan_detail, name="annual_detail"),
    path("annual/<int:pk>/edit/", views.annual_plan_edit, name="annual_edit"),
    path("annual/<int:pk>/delete/", views.annual_plan_delete, name="annual_delete"),

    # Work Plan Objectives
    path("objectives/create/<int:plan_id>/", views.objective_create, name="objective_create"),
    path("objectives/<int:pk>/edit/", views.objective_edit, name="objective_edit"),
    path("objectives/<int:pk>/progress/", views.objective_update_progress, name="objective_update_progress"),
    path("objectives/<int:pk>/delete/", views.objective_delete, name="objective_delete"),
]
