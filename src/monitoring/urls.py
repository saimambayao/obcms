"""UI URLs for the Monitoring & Evaluation module."""

from django.urls import path

from . import exports, prioritization, scenario_api, views

app_name = "monitoring"

urlpatterns = [
    path("", views.monitoring_dashboard, name="home"),
    path("moa-ppas/", views.moa_ppas_dashboard, name="moa_ppas"),
    path("moa-ppas/import/", views.import_moa_data, name="import_moa_data"),
    path("moa-ppas/export/", views.export_moa_data, name="export_moa_data"),
    path("moa-ppas/report/", views.generate_moa_report, name="generate_moa_report"),
    path(
        "moa-ppas/bulk-update/",
        views.bulk_update_moa_status,
        name="bulk_update_moa_status",
    ),
    path(
        "moa-ppas/schedule-review/",
        views.schedule_moa_review,
        name="schedule_moa_review",
    ),
    path(
        "oobc-initiatives/", views.oobc_initiatives_dashboard, name="oobc_initiatives"
    ),
    path(
        "oobc-initiatives/impact/", views.oobc_impact_report, name="oobc_impact_report"
    ),
    path(
        "oobc-initiatives/performance/",
        views.oobc_unit_performance,
        name="oobc_unit_performance",
    ),
    path("oobc-initiatives/export/", views.export_oobc_data, name="export_oobc_data"),
    path(
        "oobc-initiatives/budget/", views.oobc_budget_review, name="oobc_budget_review"
    ),
    path(
        "oobc-initiatives/feedback/",
        views.oobc_community_feedback,
        name="oobc_community_feedback",
    ),
    path("obc-requests/", views.obc_requests_dashboard, name="obc_requests"),
    path("obc-requests/priority/", views.obc_priority_queue, name="obc_priority_queue"),
    path(
        "obc-requests/community/",
        views.obc_community_dashboard,
        name="obc_community_dashboard",
    ),
    path("obc-requests/report/", views.generate_obc_report, name="generate_obc_report"),
    path(
        "obc-requests/bulk-update/",
        views.bulk_update_obc_status,
        name="bulk_update_obc_status",
    ),
    path("obc-requests/export/", views.export_obc_data, name="export_obc_data"),
    path("entry/<uuid:pk>/", views.monitoring_entry_detail, name="detail"),
    # WorkItem Integration (HTMX endpoints)
    path(
        "entry/<uuid:pk>/enable-tracking/",
        views.enable_workitem_tracking,
        name="enable_workitem_tracking",
    ),
    path(
        "entry/<uuid:pk>/disable-tracking/",
        views.disable_workitem_tracking,
        name="disable_workitem_tracking",
    ),
    path(
        "entry/<uuid:pk>/distribute-budget/",
        views.distribute_budget,
        name="distribute_budget",
    ),
    path(
        "entry/<uuid:pk>/sync-progress/",
        views.sync_progress,
        name="sync_progress",
    ),
    path(
        "entry/<uuid:pk>/work-items-summary/",
        views.work_items_summary_partial,
        name="work_items_summary",
    ),
    path(
        "work-items/<uuid:work_item_id>/children/",
        views.work_item_children,
        name="work_item_children",
    ),
    path("create/moa/", views.create_moa_entry, name="create_moa"),
    path("create/moa/obc/", views.ajax_create_obc, name="ajax_create_obc"),
    path("create/oobc/", views.create_oobc_entry, name="create_oobc"),
    path("create/request/", views.create_request_entry, name="create_request"),
    # Export endpoints
    path(
        "exports/aip-summary/",
        exports.export_aip_summary_excel,
        name="export_aip_summary",
    ),
    path(
        "exports/compliance/",
        exports.export_compliance_report_excel,
        name="export_compliance",
    ),
    path("exports/budget-csv/", exports.export_budget_csv, name="export_budget_csv"),
    path(
        "exports/funding-timeline/",
        exports.export_funding_timeline_excel,
        name="export_funding_timeline",
    ),
    # Prioritization and scenario planning
    path(
        "prioritization/",
        prioritization.prioritization_matrix,
        name="prioritization_matrix",
    ),
    path(
        "api/scenario/rebalance/",
        scenario_api.scenario_rebalance_budget,
        name="scenario_rebalance",
    ),
    path(
        "api/scenario/funding-mix/",
        scenario_api.scenario_funding_mix,
        name="scenario_funding_mix",
    ),
    path(
        "api/scenario/obligation-forecast/",
        scenario_api.scenario_obligation_forecast,
        name="scenario_obligation_forecast",
    ),
    # Compliance Reports (Phase 5)
    path("reports/", views.reports_dashboard, name="reports_dashboard"),
    path(
        "reports/mfbm-budget/",
        views.mfbm_budget_report_download,
        name="mfbm_budget_report",
    ),
    path(
        "reports/bpda-development/",
        views.bpda_development_report_download,
        name="bpda_development_report",
    ),
    path(
        "reports/coa-variance/",
        views.coa_variance_report_download,
        name="coa_variance_report",
    ),
    # PPA Calendar Feed
    path(
        "entry/<uuid:entry_id>/calendar-feed/",
        views.ppa_calendar_feed,
        name="ppa_calendar_feed",
    ),
]
