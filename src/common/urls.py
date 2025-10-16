from django.urls import path, re_path
from django.views.generic import RedirectView
from . import views

app_name = "common"

UUID_OR_HEX_PATTERN = (
    r"[0-9a-fA-F]{32}"
    r"|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

urlpatterns = [
    # ============================================================================
    # AUTHENTICATION & PROFILE
    # ============================================================================
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("register/moa/", views.MOARegistrationView.as_view(), name="moa_register"),
    path("register/moa/success/", views.MOARegistrationSuccessView.as_view(), name="moa_register_success"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("restricted/", views.page_restricted, name="page_restricted"),

    # ============================================================================
    # OOBC MANAGEMENT
    # ============================================================================
    path("oobc-management/", views.oobc_management_home, name="oobc_management_home"),

    # User Approvals (All Users)
    path("oobc-management/user-approvals/", views.user_approvals, name="user_approvals"),
    path("oobc-management/user-approvals/<int:user_id>/action/", views.user_approval_action, name="user_approval_action"),

    # MOA User Approvals (Two-Level Workflow)
    path("oobc-management/moa-approvals/", views.MOAApprovalListView.as_view(), name="moa_approval_list"),
    path("oobc-management/moa-approvals/<int:user_id>/endorse/", views.approve_moa_user_stage_one, name="approve_moa_user_stage_one"),
    path("oobc-management/moa-approvals/<int:user_id>/risk/", views.moa_approval_risk_prompt, name="moa_approval_risk_prompt"),
    path("oobc-management/moa-approvals/<int:user_id>/approve/", views.approve_moa_user, name="approve_moa_user"),
    path("oobc-management/moa-approvals/<int:user_id>/reject/", views.reject_moa_user, name="reject_moa_user"),

    # OOBC Calendar
    path("oobc-management/calendar/", views.oobc_calendar, name="oobc_calendar"),
    path("oobc-management/calendar/modern/", views.oobc_calendar_modern, name="oobc_calendar_modern"),
    path("oobc-management/calendar/advanced-modern/", views.oobc_calendar_advanced_modern, name="oobc_calendar_advanced_modern"),
    path("oobc-management/calendar/feed/json/", views.oobc_calendar_feed_json, name="oobc_calendar_feed_json"),
    path("oobc-management/calendar/work-items/feed/", views.work_items_calendar_feed, name="work_items_calendar_feed"),
    path("oobc-management/work-items/<uuid:work_item_id>/modal/", views.work_item_modal, name="work_item_modal"),
    path("oobc-management/calendar/feed/ics/", views.oobc_calendar_feed_ics, name="oobc_calendar_feed_ics"),
    path("oobc-management/calendar/brief/", views.oobc_calendar_brief, name="oobc_calendar_brief"),
    path("oobc-management/calendar/preferences/", views.calendar_preferences, name="calendar_preferences"),
    path("api/calendar/event/update/", views.calendar_event_update, name="calendar_event_update"),

    # Staff Management
    path("oobc-management/staff/", views.staff_management, name="staff_management"),
    path("oobc-management/staff/teams/assign/", views.staff_team_assign, name="staff_team_assign"),
    path("oobc-management/staff/teams/manage/", views.staff_team_manage, name="staff_team_manage"),
    path("oobc-management/staff/profiles/", views.staff_profiles_list, name="staff_profiles_list"),
    path("oobc-management/staff/profiles/add/", views.staff_profile_create, name="staff_profile_create"),
    path("oobc-management/staff/profiles/<int:pk>/", views.staff_profiles_detail, name="staff_profiles_detail"),
    path("oobc-management/staff/profiles/<int:pk>/edit/", views.staff_profile_update, name="staff_profile_update"),
    path("oobc-management/staff/profiles/<int:pk>/delete/", views.staff_profile_delete, name="staff_profile_delete"),
    path("oobc-management/staff/performance/", views.staff_performance_dashboard, name="staff_performance_dashboard"),
    path("oobc-management/staff/training/", views.staff_training_development, name="staff_training_development"),

    # Planning & Budgeting
    path("oobc-management/planning-budgeting/", views.planning_budgeting, name="planning_budgeting"),

    # ============================================================================
    # DASHBOARD HTMX ENDPOINTS
    # ============================================================================
    path("dashboard/stats-cards/", views.dashboard_stats_cards, name="dashboard_stats_cards"),
    path("dashboard/metrics/", views.dashboard_metrics, name="dashboard_metrics"),
    path("dashboard/activity/", views.dashboard_activity, name="dashboard_activity"),
    path("dashboard/alerts/", views.dashboard_alerts, name="dashboard_alerts"),
    path("dashboard/staff/stats/", views.staff_dashboard_stats, name="staff_dashboard_stats"),

    # ============================================================================
    # PLANNING & BUDGETING INTEGRATION
    # ============================================================================
    path("oobc-management/gap-analysis/", views.gap_analysis_dashboard, name="gap_analysis_dashboard"),
    path("oobc-management/policy-budget-matrix/", views.policy_budget_matrix, name="policy_budget_matrix"),
    path("oobc-management/mao-focal-persons/", views.mao_focal_persons_registry, name="mao_focal_persons_registry"),
    path("oobc-management/community-needs/submit/", views.community_need_submit, name="community_need_submit"),
    path("oobc-management/community-needs/", views.community_needs_summary, name="community_needs_summary"),

    # ============================================================================
    # PARTICIPATORY BUDGETING
    # ============================================================================
    path("community/voting/", views.community_voting_browse, name="community_voting_browse"),
    path("community/voting/vote/", views.community_voting_vote, name="community_voting_vote"),
    path("community/voting/results/", views.community_voting_results, name="community_voting_results"),
    path("oobc-management/budget-feedback/", views.budget_feedback_dashboard, name="budget_feedback_dashboard"),
    path("services/feedback/<uuid:application_id>/", views.submit_service_feedback, name="submit_service_feedback"),
    path("transparency/", views.transparency_dashboard, name="transparency_dashboard"),

    # ============================================================================
    # STRATEGIC PLANNING
    # ============================================================================
    path("oobc-management/strategic-goals/", views.strategic_goals_dashboard, name="strategic_goals_dashboard"),
    path("oobc-management/annual-planning/", views.annual_planning_dashboard, name="annual_planning_dashboard"),
    path("oobc-management/rdp-alignment/", views.regional_development_alignment, name="regional_development_alignment"),

    # ============================================================================
    # SCENARIO PLANNING & OPTIMIZATION
    # ============================================================================
    path("oobc-management/scenarios/", views.scenario_list, name="scenario_list"),
    path("oobc-management/scenarios/create/", views.scenario_create, name="scenario_create"),
    path("oobc-management/scenarios/<uuid:scenario_id>/", views.scenario_detail, name="scenario_detail"),
    path("oobc-management/scenarios/compare/", views.scenario_compare, name="scenario_compare"),
    path("oobc-management/scenarios/<uuid:scenario_id>/optimize/", views.scenario_optimize, name="scenario_optimize"),

    # ============================================================================
    # ANALYTICS & FORECASTING
    # ============================================================================
    path("oobc-management/analytics/", views.analytics_dashboard, name="analytics_dashboard"),
    path("oobc-management/forecasting/", views.budget_forecasting, name="budget_forecasting"),
    path("oobc-management/trends/", views.trend_analysis, name="trend_analysis"),
    path("oobc-management/impact/", views.impact_assessment, name="impact_assessment"),

    # ============================================================================
    # DEPRECATION DASHBOARD
    # ============================================================================
    path("admin/deprecation/", views.deprecation_dashboard, name="deprecation_dashboard"),

    # ============================================================================
    # WORKITEM MANAGEMENT (Unified Work Hierarchy)
    # ============================================================================
    path("oobc-management/work-items/", views.work_item_list, name="work_item_list"),
    path("oobc-management/work-items/create/", views.work_item_create, name="work_item_create"),
    path("oobc-management/work-items/<uuid:pk>/", views.work_item_detail, name="work_item_detail"),
    path("oobc-management/work-items/<uuid:pk>/edit/", views.work_item_edit, name="work_item_edit"),
    path("oobc-management/work-items/<uuid:pk>/delete/", views.work_item_delete, name="work_item_delete"),
    path("oobc-management/work-items/<uuid:pk>/delete/modal/", views.work_item_delete_modal, name="work_item_delete_modal"),
    path("oobc-management/work-items/<uuid:pk>/tree/", views.work_item_tree_partial, name="work_item_tree_partial"),
    path("oobc-management/work-items/<uuid:pk>/update-progress/", views.work_item_update_progress, name="work_item_update_progress"),
    path("oobc-management/work-items/calendar/feed/", views.work_item_calendar_feed, name="work_item_calendar_feed"),
    path("oobc-management/work-items/<uuid:pk>/sidebar/detail/", views.work_item_sidebar_detail, name="work_item_sidebar_detail"),
    path("oobc-management/work-items/<uuid:pk>/sidebar/edit/", views.work_item_sidebar_edit, name="work_item_sidebar_edit"),
    path("oobc-management/work-items/sidebar/create/", views.work_item_sidebar_create, name="work_item_sidebar_create"),
    path("oobc-management/work-items/<uuid:pk>/duplicate/", views.work_item_duplicate, name="work_item_duplicate"),
    path("oobc-management/work-items/<uuid:pk>/search-related/", views.work_item_search_related, name="work_item_search_related"),
    path("oobc-management/work-items/<uuid:pk>/add-related/", views.work_item_add_related, name="work_item_add_related"),
    path("oobc-management/work-items/<uuid:pk>/remove-related/<uuid:related_id>/", views.work_item_remove_related, name="work_item_remove_related"),
    path("oobc-management/work-items/<uuid:pk>/quick-create-child/", views.work_item_quick_create_child, name="work_item_quick_create_child"),
    path("oobc-management/work-items/<uuid:pk>/search-users/", views.work_item_search_users, name="work_item_search_users"),
    path("oobc-management/work-items/<uuid:pk>/add-assignee/", views.work_item_add_assignee, name="work_item_add_assignee"),
    path("oobc-management/work-items/<uuid:pk>/remove-assignee/<int:user_id>/", views.work_item_remove_assignee, name="work_item_remove_assignee"),
    path("oobc-management/work-items/<uuid:pk>/search-teams/", views.work_item_search_teams, name="work_item_search_teams"),
    path("oobc-management/work-items/<uuid:pk>/add-team/", views.work_item_add_team, name="work_item_add_team"),
    path("oobc-management/work-items/<uuid:pk>/remove-team/<int:team_id>/", views.work_item_remove_team, name="work_item_remove_team"),

    # ============================================================================
    # HOME REDIRECT
    # ============================================================================
    path("", views.dashboard, name="home"),
]

# ============================================================================
# RBAC MANAGEMENT (Integrated with User Approvals)
# ============================================================================
from common.views.rbac_management import (
    rbac_dashboard,
    rbac_users_list,
    user_permissions_list,
    user_permissions_detail,
    rbac_role_assignment_form,
    user_role_assign,
    user_role_remove,
    user_feature_toggle,
    rbac_bulk_assign_form,
    bulk_assign_roles,
    rbac_bulk_remove_roles,
    rbac_permission_grant_form,
    rbac_permission_grant,
    rbac_permission_remove,
    role_list,
    feature_list,
)

urlpatterns += [
    # RBAC Dashboard
    path('rbac/', rbac_dashboard, name='rbac_dashboard'),

    # User permissions management
    path('rbac/users/', user_permissions_list, name='rbac_users'),
    path('rbac/users/list/', rbac_users_list, name='rbac_users_list'),  # HTMX endpoint
    path('rbac/user/<int:user_id>/permissions/', user_permissions_detail, name='rbac_user_permissions'),

    # Role assignment/removal (HTMX)
    path('rbac/user/<int:user_id>/roles/form/', rbac_role_assignment_form, name='rbac_role_assignment_form'),
    path('rbac/user/<int:user_id>/roles/assign/', user_role_assign, name='rbac_role_assign'),
    path('rbac/user/<int:user_id>/roles/<uuid:role_id>/remove/', user_role_remove, name='rbac_user_role_remove'),

    # Feature toggles (HTMX)
    path('rbac/user/<int:user_id>/features/<uuid:feature_id>/toggle/', user_feature_toggle, name='rbac_feature_toggle'),

    # Permission management (HTMX)
    path('rbac/user/<int:user_id>/permissions/grant/form/', rbac_permission_grant_form, name='rbac_permission_grant_form'),
    path('rbac/user/<int:user_id>/permissions/grant/', rbac_permission_grant, name='rbac_permission_grant'),
    path('rbac/user/<int:user_id>/permissions/<uuid:permission_id>/remove/', rbac_permission_remove, name='rbac_permission_remove'),

    # Bulk operations
    path('rbac/bulk/assign/form/', rbac_bulk_assign_form, name='rbac_bulk_assign_form'),
    path('rbac/bulk/assign/', bulk_assign_roles, name='rbac_bulk_assign'),
    path('rbac/bulk/remove/', rbac_bulk_remove_roles, name='rbac_bulk_remove_roles'),

    # Role & feature listing
    path('rbac/roles/', role_list, name='rbac_roles'),
    path('rbac/features/', feature_list, name='rbac_features'),
]

# ============================================================================
# UNIFIED SEARCH
# ============================================================================
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

# ============================================================================
# AI CHAT ASSISTANT
# ============================================================================
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

# ============================================================================
# QUERY BUILDER
# ============================================================================
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

# ============================================================================
# MULTI-TENANT ORGANIZATION MANAGEMENT
# ============================================================================
from common.views.multi_tenant_urls import (
    switch_organization,
    organization_selection,
    validate_organization,
    current_organization,
    set_organization_preference,
    organization_dashboard,
    organization_switcher_partial,
    quick_switch_organization,
)

urlpatterns += [
    # Organization switching and management
    path('switch-organization/', switch_organization, name='switch_organization'),
    path('switch-organization/<str:org_code>/', switch_organization, name='switch_organization_code'),
    path('organization-selection/', organization_selection, name='organization_selection'),
    path('organization-dashboard/<str:org_code>/', organization_dashboard, name='organization_dashboard'),

    # API endpoints for organization management
    path('api/validate-organization/<str:org_code>/', validate_organization, name='validate_organization'),
    path('api/current-organization/', current_organization, name='current_organization'),
    path('api/set-organization-preference/', set_organization_preference, name='set_organization_preference'),

    # HTMX endpoints for instant UI updates
    path('partial/organization-switcher/', organization_switcher_partial, name='organization_switcher_partial'),
    path('quick-switch-organization/', quick_switch_organization, name='quick_switch_organization'),
]
