"""
Project Central URL Configuration

URL patterns for the integrated project management system.
"""

from django.urls import path
from . import views

app_name = "project_central"

urlpatterns = [
    # Portfolio Dashboard
    path("", views.portfolio_dashboard_view, name="portfolio_dashboard"),
    path("dashboard/", views.portfolio_dashboard_view, name="dashboard"),
    # Budget Planning Dashboard
    path("budget/", views.budget_planning_dashboard, name="budget_planning_dashboard"),
    # Project Workflows
    path("projects/", views.project_list_view, name="project_list"),
    path(
        "projects/create/",
        views.create_project_workflow,
        name="create_project_workflow",
    ),
    path(
        "projects/<uuid:workflow_id>/",
        views.project_workflow_detail,
        name="project_workflow_detail",
    ),
    path(
        "projects/<uuid:workflow_id>/advance/",
        views.advance_project_stage,
        name="advance_project_stage",
    ),
    path(
        "projects/<uuid:workflow_id>/edit/",
        views.edit_project_workflow,
        name="edit_project_workflow",
    ),
    # Project Calendar
    path(
        "projects/<uuid:workflow_id>/calendar/",
        views.project_calendar_view,
        name="project_calendar",
    ),
    path(
        "projects/<uuid:workflow_id>/calendar-events/",
        views.project_calendar_events,
        name="project_calendar_events",
    ),
    # M&E Analytics
    path("analytics/", views.me_analytics_dashboard, name="me_analytics_dashboard"),
    path(
        "analytics/sector/<str:sector>/",
        views.sector_analytics,
        name="sector_analytics",
    ),
    path(
        "analytics/geographic/", views.geographic_analytics, name="geographic_analytics"
    ),
    path(
        "analytics/policy/<uuid:policy_id>/",
        views.policy_analytics,
        name="policy_analytics",
    ),
    # PPA M&E Dashboard (Phase 6)
    path("ppa/<uuid:ppa_id>/me/", views.ppa_me_dashboard, name="ppa_me_dashboard"),
    # Alerts
    path("alerts/", views.alert_list_view, name="alert_list"),
    path("alerts/generate-now/", views.generate_alerts_now, name="generate_alerts_now"),
    path("alerts/<uuid:alert_id>/", views.alert_detail_view, name="alert_detail"),
    path(
        "alerts/<uuid:alert_id>/acknowledge/",
        views.acknowledge_alert,
        name="acknowledge_alert",
    ),
    path(
        "alerts/bulk-acknowledge/",
        views.bulk_acknowledge_alerts,
        name="bulk_acknowledge_alerts",
    ),
    # Reports
    path("reports/", views.report_list_view, name="report_list"),
    path(
        "reports/portfolio/generate/",
        views.generate_portfolio_report,
        name="generate_portfolio_report",
    ),
    path(
        "reports/needs-impact/generate/",
        views.generate_needs_impact_report,
        name="generate_needs_impact_report",
    ),
    path(
        "reports/policy/generate/",
        views.generate_policy_report,
        name="generate_policy_report",
    ),
    path(
        "reports/mao/generate/", views.generate_mao_report, name="generate_mao_report"
    ),
    path(
        "reports/budget/generate/",
        views.generate_budget_execution_report,
        name="generate_budget_execution_report",
    ),
    path("reports/<uuid:report_id>/", views.report_detail_view, name="report_detail"),
    path(
        "reports/<uuid:report_id>/download/",
        views.download_report,
        name="download_report",
    ),
    # Tasks (Enhanced with project integration)
    path("tasks/", views.my_tasks_with_projects, name="my_tasks_with_projects"),
    path(
        "tasks/generate/<uuid:workflow_id>/",
        views.generate_workflow_tasks,
        name="generate_workflow_tasks",
    ),
    # Budget Approval
    path(
        "approvals/", views.budget_approval_dashboard, name="budget_approval_dashboard"
    ),
    path(
        "approvals/<int:ppa_id>/review/",
        views.review_budget_approval,
        name="review_budget_approval",
    ),
    path(
        "approvals/<int:ppa_id>/approve/", views.approve_budget, name="approve_budget"
    ),
    path("approvals/<int:ppa_id>/reject/", views.reject_budget, name="reject_budget"),
]
