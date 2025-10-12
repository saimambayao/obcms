"""
Coordination Module URL Configuration

URL patterns for coordination features including partnerships,
organizations, resource booking, and AI-powered insights.

Migration Status (Phase 0.5):
- Phase 0.5a: Partnerships (5 URLs) - COMPLETE
- Phase 0.5b: Organizations (6 URLs) - COMPLETE
- Phase 0.5c: Core Coordination (7 URLs) - COMPLETE
- Phase 0.5d: Calendar Resources (14 URLs) - COMPLETE ✅
- Phase 0.5e: Staff Leave (3 URLs) - COMPLETE ✅
- Phase 0.5f: Calendar Sharing (5 URLs) - COMPLETE ✅

Total URLs Migrated: 35 URLs (Phase 0.5a-f complete!)
"""

from django.urls import path, re_path
from . import views
from common import views as common_views

app_name = "coordination"

# UUID/HEX pattern for backward compatibility
UUID_OR_HEX_PATTERN = (
    r"[0-9a-fA-F]{32}"
    r"|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

urlpatterns = [
    # ============================================================================
    # PHASE 0.5a: PARTNERSHIPS (5 URLs) - Migrated 2025-10-13
    # ============================================================================
    path(
        "partnerships/",
        common_views.coordination_partnerships,
        name="partnerships",
    ),
    path(
        "partnerships/add/",
        common_views.partnership_create,
        name="partnership_add",
    ),
    re_path(
        rf"^partnerships/(?P<partnership_id>{UUID_OR_HEX_PATTERN})/$",
        common_views.partnership_detail,
        name="partnership_view",
    ),
    re_path(
        rf"^partnerships/(?P<partnership_id>{UUID_OR_HEX_PATTERN})/edit/$",
        common_views.partnership_update,
        name="partnership_edit",
    ),
    re_path(
        rf"^partnerships/(?P<partnership_id>{UUID_OR_HEX_PATTERN})/delete/$",
        common_views.partnership_delete,
        name="partnership_delete",
    ),

    # ============================================================================
    # PHASE 0.5b: ORGANIZATIONS (6 URLs) - Migrated 2025-10-13
    # ============================================================================
    path(
        "organizations/",
        common_views.coordination_organizations,
        name="organizations",
    ),
    path(
        "organizations/add/",
        common_views.organization_create,
        name="organization_add",
    ),
    re_path(
        rf"^organizations/(?P<organization_id>{UUID_OR_HEX_PATTERN})/edit/$",
        common_views.organization_edit,
        name="organization_edit",
    ),
    re_path(
        rf"^organizations/(?P<organization_id>{UUID_OR_HEX_PATTERN})/delete/$",
        common_views.organization_delete,
        name="organization_delete",
    ),
    re_path(
        rf"^organizations/(?P<organization_id>{UUID_OR_HEX_PATTERN})/work-items/partial/$",
        common_views.organization_work_items_partial,
        name="organization_work_items_partial",
    ),
    re_path(
        rf"^organizations/(?P<organization_id>{UUID_OR_HEX_PATTERN})/$",
        common_views.organization_detail,
        name="organization_detail",
    ),

    # ============================================================================
    # PHASE 0.5c: CORE COORDINATION (7 URLs) - Migrated 2025-10-13
    # ============================================================================
    path("", common_views.coordination_home, name="home"),
    path("events/", common_views.coordination_events, name="events"),
    path("calendar/", common_views.coordination_calendar, name="calendar"),
    path("view-all/", common_views.coordination_view_all, name="view_all"),
    path("activities/add/", common_views.coordination_activity_create, name="activity_add"),
    path("notes/add/", common_views.coordination_note_create, name="note_add"),
    path(
        "notes/activity-options/",
        common_views.coordination_note_activity_options,
        name="note_activity_options",
    ),

    # ============================================================================
    # PHASE 0.5d: CALENDAR RESOURCES (14 URLs) - Migrated 2025-10-13
    # ============================================================================
    # Calendar Resource Management
    path(
        "resources/",
        common_views.resource_list,
        name="resource_list",
    ),
    path(
        "resources/add/",
        common_views.resource_create,
        name="resource_create",
    ),
    path(
        "resources/<int:resource_id>/",
        common_views.resource_detail,
        name="resource_detail",
    ),
    path(
        "resources/<int:resource_id>/edit/",
        common_views.resource_edit,
        name="resource_edit",
    ),
    path(
        "resources/<int:resource_id>/delete/",
        common_views.resource_delete,
        name="resource_delete",
    ),
    path(
        "resources/<int:resource_id>/calendar/",
        common_views.resource_calendar,
        name="resource_calendar",
    ),
    path(
        "resources/<int:resource_id>/book/",
        common_views.booking_request,
        name="booking_request",
    ),
    path(
        "bookings/",
        common_views.booking_list,
        name="booking_list",
    ),
    path(
        "bookings/request/",
        common_views.booking_request,
        name="booking_request_general",
    ),
    path(
        "bookings/<int:booking_id>/approve/",
        common_views.booking_approve,
        name="booking_approve",
    ),
    # Enhanced Resource Booking (coordination-specific views)
    path(
        "resources/<int:resource_id>/bookings/feed/",
        views.resource_bookings_feed,
        name="resource_bookings_feed",
    ),
    path(
        "resources/check-conflicts/",
        views.calendar_check_conflicts,
        name="check_conflicts",
    ),
    path(
        "resources/<int:resource_id>/book-enhanced/",
        views.resource_booking_form,
        name="resource_booking_form",
    ),

    # ============================================================================
    # PHASE 0.5e: STAFF LEAVE (3 URLs) - Migrated 2025-10-13
    # ============================================================================
    path(
        "staff/leave/",
        common_views.staff_leave_list,
        name="leave_list",
    ),
    path(
        "staff/leave/request/",
        common_views.staff_leave_request,
        name="leave_request",
    ),
    path(
        "staff/leave/<int:leave_id>/approve/",
        common_views.staff_leave_approve,
        name="leave_approve",
    ),

    # ============================================================================
    # PHASE 0.5f: CALENDAR SHARING (5 URLs) - Migrated 2025-10-13
    # ============================================================================
    path(
        "calendar/share/",
        common_views.calendar_share_create,
        name="share_create",
    ),
    path(
        "calendar/share/manage/",
        common_views.calendar_share_manage,
        name="share_manage",
    ),
    path(
        "calendar/shared/<str:token>/",
        common_views.calendar_share_view,
        name="share_view",
    ),
    path(
        "calendar/share/<int:share_id>/toggle/",
        common_views.calendar_share_toggle,
        name="share_toggle",
    ),
    path(
        "calendar/share/<int:share_id>/delete/",
        common_views.calendar_share_delete,
        name="share_delete",
    ),

    # ============================================================================
    # MOA CALENDAR FEED (Coordination-specific)
    # ============================================================================
    path(
        'organizations/<uuid:organization_id>/calendar-feed/',
        views.moa_calendar_feed,
        name='moa_calendar_feed',
    ),

    # ============================================================================
    # AI INTELLIGENCE ENDPOINTS - TODO: Implement these views
    # ============================================================================
    # path(
    #     'ai/match-stakeholders/<int:pk>/',
    #     views.ai_match_stakeholders,
    #     name='ai-match-stakeholders'
    # ),
    # path(
    #     'ai/predict-partnerships/<int:pk>/',
    #     views.ai_predict_partnerships,
    #     name='ai-predict-partnerships'
    # ),
    # path(
    #     'ai/meeting-intelligence/<int:pk>/',
    #     views.ai_meeting_intelligence,
    #     name='ai-meeting-intelligence'
    # ),
    # path(
    #     'ai/optimize-resources/<int:pk>/',
    #     views.ai_optimize_resources,
    #     name='ai-optimize-resources'
    # ),
]
