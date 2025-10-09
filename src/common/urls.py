from django.urls import path
from django.views.generic import RedirectView
from . import views
from communities import data_utils
from coordination import views as coordination_views

app_name = "common"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("register/moa/", views.MOARegistrationView.as_view(), name="moa_register"),
    path("register/moa/success/", views.MOARegistrationSuccessView.as_view(), name="moa_register_success"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("restricted/", views.page_restricted, name="page_restricted"),
    path("communities/", views.communities_home, name="communities_home"),
    path("communities/add/", views.communities_add, name="communities_add"),
    path(
        "communities/add-municipality/",
        views.communities_add_municipality,
        name="communities_add_municipality",
    ),
    path(
        "communities/add-province/",
        views.communities_add_province,
        name="communities_add_province",
    ),
    path(
        "communities/<int:community_id>/",
        views.communities_view,
        name="communities_view",
    ),
    path(
        "communities/<int:community_id>/edit/",
        views.communities_edit,
        name="communities_edit",
    ),
    path(
        "communities/<int:community_id>/delete/",
        views.communities_delete,
        name="communities_delete",
    ),
    path(
        "communities/<int:community_id>/restore/",
        views.communities_restore,
        name="communities_restore",
    ),
    path("communities/manage/", views.communities_manage, name="communities_manage"),
    path(
        "communities/managemunicipal/",
        views.communities_manage_municipal,
        name="communities_manage_municipal",
    ),
    path(
        "communities/managebarangayobc/",
        views.communities_manage,
        name="communities_manage_barangay_obc",
    ),
    path(
        "communities/managemunicipalobc/",
        views.communities_manage_municipal,
        name="communities_manage_municipal_obc",
    ),
    path(
        "communities/manageprovincial/",
        views.communities_manage_provincial,
        name="communities_manage_provincial",
    ),
    path(
        "communities/manageprovincialobc/",
        views.communities_manage_provincial,
        name="communities_manage_provincial_obc",
    ),
    path(
        "communities/municipal/<int:coverage_id>/",
        views.communities_view_municipal,
        name="communities_view_municipal",
    ),
    path(
        "communities/municipal/<int:coverage_id>/edit/",
        views.communities_edit_municipal,
        name="communities_edit_municipal",
    ),
    path(
        "communities/municipal/<int:coverage_id>/delete/",
        views.communities_delete_municipal,
        name="communities_delete_municipal",
    ),
    path(
        "communities/municipal/<int:coverage_id>/restore/",
        views.communities_restore_municipal,
        name="communities_restore_municipal",
    ),
    path(
        "communities/province/<int:coverage_id>/",
        views.communities_view_provincial,
        name="communities_view_provincial",
    ),
    path(
        "communities/province/<int:coverage_id>/edit/",
        views.communities_edit_provincial,
        name="communities_edit_provincial",
    ),
    path(
        "communities/province/<int:coverage_id>/delete/",
        views.communities_delete_provincial,
        name="communities_delete_provincial",
    ),
    path(
        "communities/province/<int:coverage_id>/submit/",
        views.communities_submit_provincial,
        name="communities_submit_provincial",
    ),
    path(
        "communities/province/<int:coverage_id>/restore/",
        views.communities_restore_provincial,
        name="communities_restore_provincial",
    ),
    path(
        "communities/stakeholders/",
        views.communities_stakeholders,
        name="communities_stakeholders",
    ),
    path("locations/centroid/", views.location_centroid, name="location_centroid"),
    path("mana/", views.mana_home, name="mana_home"),
    path("mana/stats-cards/", views.mana_stats_cards, name="mana_stats_cards"),
    path("mana/regional/", views.mana_regional_overview, name="mana_regional_overview"),
    path(
        "mana/provincial/",
        views.mana_provincial_overview,
        name="mana_provincial_overview",
    ),
    path(
        "mana/provincial/<int:province_id>/",
        views.mana_provincial_card_detail,
        name="mana_provincial_card_detail",
    ),
    path(
        "mana/provincial/<int:province_id>/edit/",
        views.mana_province_edit,
        name="mana_province_edit",
    ),
    path(
        "mana/provincial/<int:province_id>/delete/",
        views.mana_province_delete,
        name="mana_province_delete",
    ),
    path("mana/desk-review/", views.mana_desk_review, name="mana_desk_review"),
    path("mana/survey/", views.mana_survey_module, name="mana_survey_module"),
    path("mana/kii/", views.mana_key_informant_interviews, name="mana_kii"),
    path("mana/playbook/", views.mana_playbook, name="mana_playbook"),
    path(
        "mana/activity-planner/",
        views.mana_activity_planner,
        name="mana_activity_planner",
    ),
    path("mana/activity-log/", views.mana_activity_log, name="mana_activity_log"),
    path(
        "mana/activity-processing/",
        views.mana_activity_processing,
        name="mana_activity_processing",
    ),
    path("mana/new-assessment/", views.mana_new_assessment, name="mana_new_assessment"),
    path(
        "mana/manage-assessments/",
        views.mana_manage_assessments,
        name="mana_manage_assessments",
    ),
    path(
        "mana/manage-assessments/<uuid:assessment_id>/",
        views.mana_assessment_detail,
        name="mana_assessment_detail",
    ),
    path(
        "mana/manage-assessments/<uuid:assessment_id>/edit/",
        views.mana_assessment_edit,
        name="mana_assessment_edit",
    ),
    path(
        "mana/manage-assessments/<uuid:assessment_id>/delete/",
        views.mana_assessment_delete,
        name="mana_assessment_delete",
    ),
    path(
        "mana/geographic-data/", views.mana_geographic_data, name="mana_geographic_data"
    ),
    path("coordination/", views.coordination_home, name="coordination_home"),
    path(
        "coordination/organizations/",
        views.coordination_organizations,
        name="coordination_organizations",
    ),
    path(
        "coordination/organizations/add/",
        views.organization_create,
        name="coordination_organization_add",
    ),
    path(
        "coordination/organizations/<uuid:organization_id>/edit/",
        views.organization_edit,
        name="coordination_organization_edit",
    ),
    path(
        "coordination/organizations/<uuid:organization_id>/delete/",
        views.organization_delete,
        name="coordination_organization_delete",
    ),
    path(
        "coordination/organizations/<uuid:organization_id>/",
        views.organization_detail,
        name="coordination_organization_detail",
    ),
    # TODO: Implement organization calendar feed if needed
    # path(
    #     "coordination/organizations/<uuid:organization_id>/calendar-feed/",
    #     views.organization_calendar_feed,  # Function doesn't exist yet
    #     name="coordination_organization_calendar_feed",
    # ),
    path(
        "coordination/partnerships/",
        views.coordination_partnerships,
        name="coordination_partnerships",
    ),
    path(
        "coordination/partnerships/add/",
        views.partnership_create,
        name="coordination_partnership_add",
    ),
    path(
        "coordination/partnerships/<uuid:partnership_id>/",
        views.partnership_detail,
        name="coordination_partnership_view",
    ),
    path(
        "coordination/partnerships/<uuid:partnership_id>/edit/",
        views.partnership_update,
        name="coordination_partnership_edit",
    ),
    path(
        "coordination/partnerships/<uuid:partnership_id>/delete/",
        views.partnership_delete,
        name="coordination_partnership_delete",
    ),
    # Legacy Event URLs removed - replaced by WorkItem system (activities)
    path("coordination/events/", views.coordination_events, name="coordination_events"),
    path(
        "coordination/calendar/",
        views.coordination_calendar,
        name="coordination_calendar",
    ),
    path(
        "coordination/activities/add/",
        views.coordination_activity_create,
        name="coordination_activity_add",
    ),
    path(
        "coordination/view-all/",
        views.coordination_view_all,
        name="coordination_view_all",
    ),
    path("recommendations/", views.recommendations_home, name="recommendations_home"),
    path("recommendations/stats-cards/", views.recommendations_stats_cards, name="recommendations_stats_cards"),
    path("recommendations/new/", views.recommendations_new, name="recommendations_new"),
    path("recommendations/create/", views.recommendations_create, name="recommendations_create"),
    path("recommendations/autosave/", views.recommendations_autosave, name="recommendations_autosave"),
    path(
        "recommendations/manage/",
        views.recommendations_manage,
        name="recommendations_manage",
    ),
    path(
        "recommendations/programs/",
        views.recommendations_programs,
        name="recommendations_programs",
    ),
    path(
        "recommendations/services/",
        views.recommendations_services,
        name="recommendations_services",
    ),
    path("recommendations/<uuid:pk>/view/", views.recommendations_view, name="recommendations_view"),
    path("recommendations/<uuid:pk>/edit/", views.recommendations_edit, name="recommendations_edit"),
    path("recommendations/<uuid:pk>/delete/", views.recommendations_delete, name="recommendations_delete"),
    path(
        "recommendations/area/<str:area_slug>/",
        views.recommendations_by_area,
        name="recommendations_by_area",
    ),
    path("oobc-management/", views.oobc_management_home, name="oobc_management_home"),
    path("oobc-management/user-approvals/", views.MOAApprovalListView.as_view(), name="moa_approval_list"),
    path("oobc-management/approvals/<int:user_id>/endorse/", views.approve_moa_user_stage_one, name="approve_moa_user_stage_one"),
    path("oobc-management/approvals/<int:user_id>/risk/", views.moa_approval_risk_prompt, name="moa_approval_risk_prompt"),
    path("oobc-management/approvals/<int:user_id>/approve/", views.approve_moa_user, name="approve_moa_user"),
    path("oobc-management/approvals/<int:user_id>/reject/", views.reject_moa_user, name="reject_moa_user"),
    path("oobc-management/calendar/", views.oobc_calendar, name="oobc_calendar"),
    path("oobc-management/calendar/modern/", views.oobc_calendar_modern, name="oobc_calendar_modern"),
    path("oobc-management/calendar/advanced-modern/", views.oobc_calendar_advanced_modern, name="oobc_calendar_advanced_modern"),
    path(
        "oobc-management/calendar/feed/json/",
        views.oobc_calendar_feed_json,
        name="oobc_calendar_feed_json",
    ),
    # Unified Calendar Feed (WorkItem Hierarchy)
    path(
        "oobc-management/calendar/work-items/feed/",
        views.work_items_calendar_feed,
        name="work_items_calendar_feed",
    ),
    path(
        "oobc-management/work-items/<uuid:work_item_id>/modal/",
        views.work_item_modal,
        name="work_item_modal",
    ),
    path(
        "oobc-management/calendar/feed/ics/",
        views.oobc_calendar_feed_ics,
        name="oobc_calendar_feed_ics",
    ),
    path(
        "oobc-management/calendar/brief/",
        views.oobc_calendar_brief,
        name="oobc_calendar_brief",
    ),
    path(
        "oobc-management/calendar/preferences/",
        views.calendar_preferences,
        name="calendar_preferences",
    ),
    # Calendar Resource Management
    path(
        "oobc-management/calendar/resources/",
        views.resource_list,
        name="calendar_resource_list",
    ),
    path(
        "oobc-management/calendar/resources/add/",
        views.resource_create,
        name="calendar_resource_create",
    ),
    path(
        "oobc-management/calendar/resources/<int:resource_id>/",
        views.resource_detail,
        name="calendar_resource_detail",
    ),
    path(
        "oobc-management/calendar/resources/<int:resource_id>/edit/",
        views.resource_edit,
        name="calendar_resource_edit",
    ),
    path(
        "oobc-management/calendar/resources/<int:resource_id>/delete/",
        views.resource_delete,
        name="calendar_resource_delete",
    ),
    path(
        "oobc-management/calendar/resources/<int:resource_id>/calendar/",
        views.resource_calendar,
        name="calendar_resource_calendar",
    ),
    path(
        "oobc-management/calendar/resources/<int:resource_id>/book/",
        views.booking_request,
        name="calendar_booking_request",
    ),
    path(
        "oobc-management/calendar/bookings/",
        views.booking_list,
        name="calendar_booking_list",
    ),
    path(
        "oobc-management/calendar/bookings/request/",
        views.booking_request,
        name="calendar_booking_request_general",
    ),
    path(
        "oobc-management/calendar/bookings/<int:booking_id>/approve/",
        views.booking_approve,
        name="calendar_booking_approve",
    ),
    # Phase 3: Enhanced Resource Booking
    path(
        "coordination/resources/<int:resource_id>/bookings/feed/",
        coordination_views.resource_bookings_feed,
        name="coordination_resource_bookings_feed",
    ),
    path(
        "coordination/resources/check-conflicts/",
        coordination_views.calendar_check_conflicts,
        name="coordination_check_conflicts",
    ),
    path(
        "coordination/resources/<int:resource_id>/book-enhanced/",
        coordination_views.resource_booking_form,
        name="coordination_resource_booking_form",
    ),
    # Staff Leave Management
    path(
        "oobc-management/staff/leave/", views.staff_leave_list, name="staff_leave_list"
    ),
    path(
        "oobc-management/staff/leave/request/",
        views.staff_leave_request,
        name="staff_leave_request",
    ),
    path(
        "oobc-management/staff/leave/<int:leave_id>/approve/",
        views.staff_leave_approve,
        name="staff_leave_approve",
    ),
    # Calendar Sharing
    path(
        "oobc-management/calendar/share/",
        views.calendar_share_create,
        name="calendar_share_create",
    ),
    path(
        "oobc-management/calendar/share/manage/",
        views.calendar_share_manage,
        name="calendar_share_manage",
    ),
    path(
        "calendar/shared/<str:token>/",
        views.calendar_share_view,
        name="calendar_share_view",
    ),
    path(
        "oobc-management/calendar/share/<int:share_id>/toggle/",
        views.calendar_share_toggle,
        name="calendar_share_toggle",
    ),
    path(
        "oobc-management/calendar/share/<int:share_id>/delete/",
        views.calendar_share_delete,
        name="calendar_share_delete",
    ),
    # Legacy Event Attendance URLs removed - WorkItem attendance system TBD
    # Calendar API (drag-and-drop, interactive features)
    path(
        "api/calendar/event/update/",
        views.calendar_event_update,
        name="calendar_event_update",
    ),
    path("oobc-management/staff/", views.staff_management, name="staff_management"),
    # Legacy StaffTask URLs removed - replaced by WorkItem system (see lines 807-846)
    path(
        "oobc-management/staff/teams/assign/",
        views.staff_team_assign,
        name="staff_team_assign",
    ),
    path(
        "oobc-management/staff/teams/manage/",
        views.staff_team_manage,
        name="staff_team_manage",
    ),
    path(
        "oobc-management/staff/profiles/",
        views.staff_profiles_list,
        name="staff_profiles_list",
    ),
    path(
        "oobc-management/staff/profiles/add/",
        views.staff_profile_create,
        name="staff_profile_create",
    ),
    path(
        "oobc-management/staff/profiles/<int:pk>/",
        views.staff_profiles_detail,
        name="staff_profiles_detail",
    ),
    path(
        "oobc-management/staff/profiles/<int:pk>/edit/",
        views.staff_profile_update,
        name="staff_profile_update",
    ),
    path(
        "oobc-management/staff/profiles/<int:pk>/delete/",
        views.staff_profile_delete,
        name="staff_profile_delete",
    ),
    path(
        "oobc-management/staff/performance/",
        views.staff_performance_dashboard,
        name="staff_performance_dashboard",
    ),
    path(
        "oobc-management/staff/training/",
        views.staff_training_development,
        name="staff_training_development",
    ),
    path(
        "oobc-management/planning-budgeting/",
        views.planning_budgeting,
        name="planning_budgeting",
    ),
    path(
        "oobc-management/user-approvals/", views.user_approvals, name="user_approvals"
    ),
    path(
        "oobc-management/user-approvals/<int:user_id>/action/",
        views.user_approval_action,
        name="user_approval_action",
    ),
    # Phase 1: Enhanced Dashboard - HTMX Endpoints
    path("dashboard/stats-cards/", views.dashboard_stats_cards, name="dashboard_stats_cards"),
    path("dashboard/metrics/", views.dashboard_metrics, name="dashboard_metrics"),
    path("dashboard/activity/", views.dashboard_activity, name="dashboard_activity"),
    path("dashboard/alerts/", views.dashboard_alerts, name="dashboard_alerts"),
    # Phase 2: Planning & Budgeting Integration Dashboards
    path(
        "oobc-management/gap-analysis/",
        views.gap_analysis_dashboard,
        name="gap_analysis_dashboard",
    ),
    path(
        "oobc-management/policy-budget-matrix/",
        views.policy_budget_matrix,
        name="policy_budget_matrix",
    ),
    path(
        "oobc-management/mao-focal-persons/",
        views.mao_focal_persons_registry,
        name="mao_focal_persons_registry",
    ),
    path(
        "oobc-management/community-needs/submit/",
        views.community_need_submit,
        name="community_need_submit",
    ),
    path(
        "oobc-management/community-needs/",
        views.community_needs_summary,
        name="community_needs_summary",
    ),
    # Phase 4: Participatory Budgeting - Community Voting
    path(
        "community/voting/",
        views.community_voting_browse,
        name="community_voting_browse",
    ),
    path(
        "community/voting/vote/",
        views.community_voting_vote,
        name="community_voting_vote",
    ),
    path(
        "community/voting/results/",
        views.community_voting_results,
        name="community_voting_results",
    ),
    # Phase 4: Budget Feedback & Transparency
    path(
        "oobc-management/budget-feedback/",
        views.budget_feedback_dashboard,
        name="budget_feedback_dashboard",
    ),
    path(
        "services/feedback/<uuid:application_id>/",
        views.submit_service_feedback,
        name="submit_service_feedback",
    ),
    path("transparency/", views.transparency_dashboard, name="transparency_dashboard"),
    # Phase 5: Strategic Planning Integration
    path(
        "oobc-management/strategic-goals/",
        views.strategic_goals_dashboard,
        name="strategic_goals_dashboard",
    ),
    path(
        "oobc-management/annual-planning/",
        views.annual_planning_dashboard,
        name="annual_planning_dashboard",
    ),
    path(
        "oobc-management/rdp-alignment/",
        views.regional_development_alignment,
        name="regional_development_alignment",
    ),
    # Phase 6: Scenario Planning & Budget Optimization
    path("oobc-management/scenarios/", views.scenario_list, name="scenario_list"),
    path(
        "oobc-management/scenarios/create/",
        views.scenario_create,
        name="scenario_create",
    ),
    path(
        "oobc-management/scenarios/<uuid:scenario_id>/",
        views.scenario_detail,
        name="scenario_detail",
    ),
    path(
        "oobc-management/scenarios/compare/",
        views.scenario_compare,
        name="scenario_compare",
    ),
    path(
        "oobc-management/scenarios/<uuid:scenario_id>/optimize/",
        views.scenario_optimize,
        name="scenario_optimize",
    ),
    # Phase 7: Analytics & Forecasting
    path(
        "oobc-management/analytics/",
        views.analytics_dashboard,
        name="analytics_dashboard",
    ),
    path(
        "oobc-management/forecasting/",
        views.budget_forecasting,
        name="budget_forecasting",
    ),
    path("oobc-management/trends/", views.trend_analysis, name="trend_analysis"),
    path("oobc-management/impact/", views.impact_assessment, name="impact_assessment"),
    # Data Import/Export/Report URLs
    path(
        "communities/import/",
        data_utils.import_communities_csv,
        name="import_communities",
    ),
    path(
        "communities/export/", data_utils.export_communities, name="export_communities"
    ),
    path(
        "communities/report/",
        data_utils.generate_obc_report,
        name="generate_obc_report",
    ),
    path("data-guidelines/", data_utils.data_guidelines, name="data_guidelines"),
    # Deprecation Dashboard
    path(
        "admin/deprecation/",
        views.deprecation_dashboard,
        name="deprecation_dashboard",
    ),
    # WorkItem CRUD URLs (Phase 3: Unified Work Hierarchy)
    path(
        "oobc-management/work-items/",
        views.work_item_list,
        name="work_item_list",
    ),
    path(
        "oobc-management/work-items/create/",
        views.work_item_create,
        name="work_item_create",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/",
        views.work_item_detail,
        name="work_item_detail",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/edit/",
        views.work_item_edit,
        name="work_item_edit",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/delete/",
        views.work_item_delete,
        name="work_item_delete",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/delete/modal/",
        views.work_item_delete_modal,
        name="work_item_delete_modal",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/tree/",
        views.work_item_tree_partial,
        name="work_item_tree_partial",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/update-progress/",
        views.work_item_update_progress,
        name="work_item_update_progress",
    ),
    path(
        "oobc-management/work-items/calendar/feed/",
        views.work_item_calendar_feed,
        name="work_item_calendar_feed",
    ),
    # Calendar sidebar inline editing
    path(
        "oobc-management/work-items/<uuid:pk>/sidebar/detail/",
        views.work_item_sidebar_detail,
        name="work_item_sidebar_detail",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/sidebar/edit/",
        views.work_item_sidebar_edit,
        name="work_item_sidebar_edit",
    ),
    # Calendar sidebar quick-create (double-click on date)
    path(
        "oobc-management/work-items/sidebar/create/",
        views.work_item_sidebar_create,
        name="work_item_sidebar_create",
    ),
    # Calendar sidebar actions (duplicate & delete)
    path(
        "oobc-management/work-items/<uuid:pk>/duplicate/",
        views.work_item_duplicate,
        name="work_item_duplicate",
    ),
    # Related Items management
    path(
        "oobc-management/work-items/<uuid:pk>/search-related/",
        views.work_item_search_related,
        name="work_item_search_related",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/add-related/",
        views.work_item_add_related,
        name="work_item_add_related",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/remove-related/<uuid:related_id>/",
        views.work_item_remove_related,
        name="work_item_remove_related",
    ),
    # Quick child creation
    path(
        "oobc-management/work-items/<uuid:pk>/quick-create-child/",
        views.work_item_quick_create_child,
        name="work_item_quick_create_child",
    ),
    # Assignment management
    path(
        "oobc-management/work-items/<uuid:pk>/search-users/",
        views.work_item_search_users,
        name="work_item_search_users",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/add-assignee/",
        views.work_item_add_assignee,
        name="work_item_add_assignee",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/remove-assignee/<int:user_id>/",
        views.work_item_remove_assignee,
        name="work_item_remove_assignee",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/search-teams/",
        views.work_item_search_teams,
        name="work_item_search_teams",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/add-team/",
        views.work_item_add_team,
        name="work_item_add_team",
    ),
    path(
        "oobc-management/work-items/<uuid:pk>/remove-team/<int:team_id>/",
        views.work_item_remove_team,
        name="work_item_remove_team",
    ),
    # ============================================================================
    # LEGACY URL REDIRECTS REMOVED
    # ============================================================================
    # All legacy URL redirects for StaffTask, Event, and ProjectWorkflow have
    # been removed. The system now exclusively uses the WorkItem hierarchy.
    #
    # Migration complete: 2025-10-05
    # - StaffTask URLs → WorkItem URLs
    # - Event URLs → WorkItem (activity) URLs
    # - ProjectWorkflow URLs → WorkItem (project) URLs
    #
    # If you encounter broken links, please update them to use:
    # - work_item_list, work_item_detail, work_item_create, etc.
    # ============================================================================

    path("", views.dashboard, name="home"),  # Default to dashboard
]

# Unified Search URLs
from common.views.search import (
    unified_search_view,
    search_autocomplete,
    search_stats,
    reindex_module,
)

urlpatterns += [
    path('search/', unified_search_view, name='unified_search'),
    path('search/autocomplete/', search_autocomplete, name='search_autocomplete'),
    path('search/stats/', search_stats, name='search_stats'),
    path('search/reindex/<str:module>/', reindex_module, name='reindex_module'),
]

# AI Chat Assistant URLs
from common.views.chat import (
    chat_message,
    chat_history,
    clear_chat_history,
    chat_stats,
    chat_capabilities,
    chat_suggestion,
    chat_clarification_response,
)

urlpatterns += [
    path('chat/message/', chat_message, name='chat_message'),
    path('chat/history/', chat_history, name='chat_history'),
    path('chat/clear/', clear_chat_history, name='chat_clear'),
    path('chat/stats/', chat_stats, name='chat_stats'),
    path('chat/capabilities/', chat_capabilities, name='chat_capabilities'),
    path('chat/suggestion/', chat_suggestion, name='chat_suggestion'),
    path('chat/clarification/', chat_clarification_response, name='chat_clarification_response'),
]

# Query Builder URLs
from common.views.query_builder import (
    query_builder_entities,
    query_builder_config,
    query_builder_filters,
    query_builder_preview,
    query_builder_execute,
)

urlpatterns += [
    path('api/query-builder/entities/', query_builder_entities, name='query_builder_entities'),
    path('api/query-builder/config/<str:entity_type>/', query_builder_config, name='query_builder_config'),
    path('api/query-builder/filters/', query_builder_filters, name='query_builder_filters'),
    path('api/query-builder/preview/', query_builder_preview, name='query_builder_preview'),
    path('api/query-builder/execute/', query_builder_execute, name='query_builder_execute'),
]
