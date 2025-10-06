"""
Event Attendance Tracking Views
QR code check-in, manual attendance, and reporting.

⚠️ DEPRECATED MODULE ⚠️
This entire module is deprecated as Event and EventParticipant models have been
removed and replaced by the WorkItem system.

Attendance tracking will be reimplemented for WorkItem activities.
See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
"""

# ============================================================================
# DEPRECATED - DO NOT USE
# ============================================================================
# All views in this file are deprecated and will be removed in a future version.
# The Event model has been replaced by WorkItem.
# ============================================================================

from django.contrib.auth.decorators import login_required
from django.http import Http404


@login_required
def event_check_in(request, event_id):
    """
    DEPRECATED: Manual check-in interface for event attendance.
    Event model has been replaced by WorkItem.
    """
    raise Http404("Event attendance functionality has been deprecated. Please use WorkItem system.")


@login_required
def event_generate_qr(request, event_id):
    """
    DEPRECATED: Generate QR code for event check-in.
    Event model has been replaced by WorkItem.
    """
    raise Http404("Event attendance functionality has been deprecated. Please use WorkItem system.")


@login_required
def event_scan_qr(request, event_id):
    """
    DEPRECATED: Scan QR code for event check-in.
    Event model has been replaced by WorkItem.
    """
    raise Http404("Event attendance functionality has been deprecated. Please use WorkItem system.")


@login_required
def event_attendance_report(request, event_id):
    """
    DEPRECATED: Generate attendance report for event.
    Event model has been replaced by WorkItem.
    """
    raise Http404("Event attendance functionality has been deprecated. Please use WorkItem system.")
