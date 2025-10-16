from django.urls import path

from common.views import mana as mana_views
from . import ai_views, facilitator_views, participant_views, views

app_name = "mana"

urlpatterns = [
    # Account creation
    path(
        "create-account/",
        facilitator_views.create_account,
        name="create_account",
    ),
    # Assessment selection
    path(
        "participant/assessments/",
        participant_views.participant_assessments_list,
        name="participant_assessments_list",
    ),
    path(
        "facilitator/assessments/",
        facilitator_views.facilitator_assessments_list,
        name="facilitator_assessments_list",
    ),
    # Facilitator dashboard redirects to assessments list
    path(
        "facilitator/dashboard/",
        facilitator_views.facilitator_assessments_list,
        name="facilitator_dashboard_redirect",
    ),
    # Participant-facing routes
    path(
        "assessments/<uuid:assessment_id>/participant/onboarding/",
        participant_views.participant_onboarding,
        name="participant_onboarding",
    ),
    path(
        "assessments/<uuid:assessment_id>/participant/dashboard/",
        participant_views.participant_dashboard,
        name="participant_dashboard",
    ),
    path(
        "assessments/<uuid:assessment_id>/participant/workshops/<str:workshop_type>/",
        participant_views.participant_workshop_detail,
        name="participant_workshop_detail",
    ),
    path(
        "assessments/<uuid:assessment_id>/participant/workshops/<str:workshop_type>/review/",
        participant_views.participant_workshop_review,
        name="participant_workshop_review",
    ),
    path(
        "assessments/<uuid:assessment_id>/participant/workshops/<str:workshop_type>/outputs/",
        participant_views.participant_workshop_outputs,
        name="participant_workshop_outputs",
    ),
    path(
        "assessments/<uuid:assessment_id>/participant/notifications/<int:notification_id>/mark-read/",
        participant_views.mark_notification_read,
        name="mark_notification_read",
    ),
    # Facilitator routes
    path(
        "assessments/<uuid:assessment_id>/facilitator/dashboard/",
        facilitator_views.facilitator_dashboard,
        name="facilitator_dashboard",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/participants/",
        facilitator_views.manage_participants,
        name="facilitator_manage_participants",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/participants/<int:participant_id>/reset/",
        facilitator_views.reset_participant_progress,
        name="facilitator_reset_participant",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/workshops/<str:workshop_type>/advance/",
        facilitator_views.advance_workshop,
        name="facilitator_advance_workshop",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/workshops/<str:workshop_type>/synthesis/",
        facilitator_views.generate_synthesis,
        name="facilitator_generate_synthesis",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/synthesis/<int:synthesis_id>/regenerate/",
        facilitator_views.regenerate_synthesis,
        name="facilitator_regenerate_synthesis",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/synthesis/<int:synthesis_id>/approve/",
        facilitator_views.approve_synthesis,
        name="facilitator_approve_synthesis",
    ),
    path(
        "assessments/<uuid:assessment_id>/facilitator/exports/<str:workshop_type>/<str:format_type>/",
        facilitator_views.export_workshop_responses,
        name="facilitator_export_workshop",
    ),
    # Phase 2: MANA Integration URLs
    path(
        "assessments/<uuid:assessment_id>/tasks/board/",
        views.assessment_tasks_board,
        name="mana_assessment_tasks_board",
    ),
    path(
        "assessments/<uuid:assessment_id>/calendar/",
        views.assessment_calendar,
        name="mana_assessment_calendar",
    ),
    path(
        "assessments/<uuid:assessment_id>/calendar/feed/",
        views.assessment_calendar_feed,
        name="mana_assessment_calendar_feed",
    ),
    path(
        "needs/prioritize/",
        views.needs_prioritization_board,
        name="mana_needs_prioritize",
    ),
    path(
        "needs/update-ranking/",
        views.needs_update_ranking,
        name="mana_needs_update_ranking",
    ),
    path(
        "needs/<int:need_id>/vote/",
        views.need_vote,
        name="mana_need_vote",
    ),
    path(
        "needs/export/",
        views.needs_export,
        name="mana_needs_export",
    ),
    # AI Analysis URLs
    path(
        "workshop/<int:workshop_id>/ai-analysis/",
        ai_views.workshop_ai_analysis,
        name="workshop_ai_analysis",
    ),
    path(
        "workshop/<int:workshop_id>/analyze/",
        ai_views.trigger_workshop_analysis,
        name="trigger_workshop_analysis",
    ),
    path(
        "workshop/<int:workshop_id>/analysis/status/",
        ai_views.analysis_status,
        name="analysis_status",
    ),
    path(
        "workshop/<int:workshop_id>/generate-report/",
        ai_views.generate_report,
        name="generate_report",
    ),
    path(
        "workshop/<int:workshop_id>/report/status/",
        ai_views.report_status,
        name="report_status",
    ),
    path(
        "workshop/<int:workshop_id>/themes/",
        ai_views.theme_analysis,
        name="theme_analysis",
    ),
    path(
        "workshop/<int:workshop_id>/needs/",
        ai_views.needs_analysis,
        name="needs_analysis",
    ),
    path(
        "workshop/<int:workshop_id>/export-analysis/",
        ai_views.export_analysis_json,
        name="export_analysis_json",
    ),
    path(
        "validate-content/",
        ai_views.validate_content,
        name="validate_content",
    ),
    # ============================================================================
    # Phase 0.3: MANA Module URLs (migrated from common/urls.py)
    # ============================================================================
<<<<<<< Updated upstream
    path("", mana_views.mana_home, name="mana_home"),
    path("stats-cards/", mana_views.mana_stats_cards, name="mana_stats_cards"),
    path("regional/", mana_views.mana_regional_overview, name="mana_regional_overview"),
    path(
        "provincial/",
        mana_views.mana_provincial_overview,
        name="mana_provincial_overview",
    ),
    path(
        "provincial/<int:province_id>/",
        mana_views.mana_provincial_card_detail,
        name="mana_provincial_card_detail",
    ),
    path(
        "provincial/<int:province_id>/edit/",
        mana_views.mana_province_edit,
        name="mana_province_edit",
    ),
    path(
        "provincial/<int:province_id>/delete/",
        mana_views.mana_province_delete,
        name="mana_province_delete",
    ),
    path("desk-review/", mana_views.mana_desk_review, name="mana_desk_review"),
    path("survey/", mana_views.mana_survey_module, name="mana_survey_module"),
    path("kii/", mana_views.mana_key_informant_interviews, name="mana_kii"),
    path("playbook/", mana_views.mana_playbook, name="mana_playbook"),
    path(
        "activity-planner/",
        mana_views.mana_activity_planner,
        name="mana_activity_planner",
    ),
    path("activity-log/", mana_views.mana_activity_log, name="mana_activity_log"),
    path(
        "activity-processing/",
        mana_views.mana_activity_processing,
        name="mana_activity_processing",
    ),
    path("new-assessment/", mana_views.mana_new_assessment, name="mana_new_assessment"),
    path(
        "manage-assessments/",
        mana_views.mana_manage_assessments,
        name="mana_manage_assessments",
    ),
    path(
        "manage-assessments/<uuid:assessment_id>/",
        mana_views.mana_assessment_detail,
        name="mana_assessment_detail",
    ),
    path(
        "manage-assessments/<uuid:assessment_id>/edit/",
        mana_views.mana_assessment_edit,
        name="mana_assessment_edit",
    ),
    path(
        "manage-assessments/<uuid:assessment_id>/delete/",
        mana_views.mana_assessment_delete,
        name="mana_assessment_delete",
    ),
    path(
        "geographic-data/", mana_views.mana_geographic_data, name="mana_geographic_data"
    ),
=======
    # NOTE: These URLs are commented out due to missing view functions
    # TODO: Implement missing views or migrate required functionality
    path("", views.mana_home, name="mana_home"),
    # path("new-assessment/", views.mana_new_assessment, name="mana_new_assessment"),
    # path("manage-assessments/", views.mana_manage_assessments, name="mana_manage_assessments"),
    # path("geographic-data/", views.mana_geographic_data, name="mana_geographic_data")
>>>>>>> Stashed changes
]
