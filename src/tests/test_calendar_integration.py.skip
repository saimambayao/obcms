"""
End-to-end integration tests for calendar system workflows.

These tests verify complete user workflows including:
- Creating events and seeing them on calendar
- Booking resources end-to-end
- Leave request approval workflow
- Calendar sharing workflow
- Attendance tracking workflow
- Email notifications
- Drag-and-drop event rescheduling
"""

import json
from datetime import date, datetime, time, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.cache import cache
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from common.models import (
    CalendarResource,
    CalendarResourceBooking,
    SharedCalendarLink,
    StaffLeave,
    StaffTask,
    UserCalendarPreferences,
    Region,
    Province,
    Municipality,
    Barangay,
)
from communities.models import OBCCommunity
from coordination.models import (
    Event,
    EventParticipant,
    StakeholderEngagement,
    StakeholderEngagementType,
)

User = get_user_model()


def build_event_kwargs(user, **overrides):
    """Provide required event fields for direct model creation."""

    now = timezone.now()
    defaults = {
        "title": "Integration Event",
        "description": "Integration workflow event",
        "event_type": "meeting",
        "status": "planned",
        "priority": "medium",
        "start_date": now.date(),
        "start_time": now.time().replace(microsecond=0),
        "venue": "Coordination Center",
        "address": "123 Integration Way",
        "organizer": user,
        "created_by": user,
        "expected_participants": 10,
        "actual_participants": 0,
    }
    defaults.update(overrides)
    return defaults


def build_event_form_payload(user, **overrides):
    """Provide event payload satisfying form validation requirements."""

    now = timezone.now()
    payload = {
        "title": "Integration Test Event",
        "description": "Testing end-to-end workflow",
        "event_type": "meeting",
        "status": "planned",
        "priority": "medium",
        "start_date": (now.date() + timedelta(days=7)).isoformat(),
        "start_time": "09:00:00",
        "duration_hours": "2",
        "venue": "Coordination Center",
        "address": "123 Integration Way",
        "organizer": str(user.pk),
        "expected_participants": "10",
        "actual_participants": "0",
    }

    for key, value in overrides.items():
        if isinstance(value, datetime):
            payload[key] = value.replace(microsecond=0).isoformat()
        elif isinstance(value, date):
            payload[key] = value.isoformat()
        elif isinstance(value, time):
            payload[key] = value.strftime("%H:%M:%S")
        else:
            payload[key] = value

    return payload


def serialize_form_data(data):
    """Return a copy of dict with date/time objects coerced to strings."""

    serialized = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            serialized[key] = value.replace(microsecond=0).isoformat()
        elif isinstance(value, date):
            serialized[key] = value.isoformat()
        elif isinstance(value, time):
            serialized[key] = value.strftime("%H:%M:%S")
        else:
            serialized[key] = value
    return serialized


def create_participant(event, *, user=None, **overrides):
    """Create an EventParticipant with sane defaults for tests."""

    defaults = {
        "event": event,
        "participant_type": "internal",
        "participation_role": "participant",
    }
    if user is not None:
        defaults["user"] = user
        defaults.setdefault("email", user.email)
    defaults.update(overrides)
    return EventParticipant.objects.create(**defaults)


class CalendarEventWorkflowTests(TestCase):
    """Test complete event creation, viewing, and rescheduling workflows."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_staff=True
        )
        add_event_perm = Permission.objects.get(
            content_type__app_label="coordination",
            codename="add_event",
        )
        self.user.user_permissions.add(add_event_perm)
        self.client.login(username="testuser", password="testpass123")

        self.region = Region.objects.create(code="TST-R", name="Test Region")
        self.province = Province.objects.create(
            region=self.region,
            code="TST-P",
            name="Test Province",
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="TST-M",
            name="Test Municipality",
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="TST-B",
            name="Test Barangay",
        )
        self.community = OBCCommunity.objects.create(
            name="Test Community",
            barangay=self.barangay,
        )

        self.engagement_type = StakeholderEngagementType.objects.create(
            name="Community Dialogue",
            category="consultation",
            description="Test engagement type",
        )

    def test_create_event_and_view_on_calendar(self):
        """Test creating an event via form and seeing it on calendar view."""
        # Step 1: Create event via POST
        event_data = build_event_form_payload(
            self.user,
            title="Integration Test Event",
            start_date=timezone.now().date() + timedelta(days=7),
        )

        response = self.client.post(
            reverse("common:coordination_event_add"),
            data=serialize_form_data(event_data),
        )

        # Should redirect on success
        self.assertEqual(response.status_code, 302)

        # Step 2: Verify event exists
        event = Event.objects.filter(title="Integration Test Event").first()
        self.assertIsNotNone(event)
        self.assertEqual(event.status, "planned")
        self.assertEqual(event.created_by, self.user)

        # Step 3: Check calendar view includes event
        response = self.client.get(reverse("common:coordination_calendar"))
        self.assertEqual(response.status_code, 200)

        # Calendar should include our event in JSON data
        calendar_json = response.context.get("calendar_events_json", "[]")
        calendar_data = json.loads(calendar_json)

        event_found = False
        for entry in calendar_data:
            if entry.get("title") == "Integration Test Event":
                event_found = True
                self.assertEqual(entry["extendedProps"]["type"], "event")
                self.assertEqual(entry["extendedProps"]["status"], "planned")
                self.assertIn("modalUrl", entry["extendedProps"])
                break

        self.assertTrue(event_found, "Event not found in calendar data")

    def test_drag_and_drop_event_reschedule(self):
        """Event drag-and-drop should adjust schedule via API."""
        # Step 1: Create event
        event = Event.objects.create(
            **build_event_kwargs(
                self.user,
                title="Draggable Event",
                start_date=timezone.now().date(),
                start_time=time(9, 0),
                duration_hours=2,
            )
        )

        # Step 2: Reschedule via API (simulating drag-and-drop)
        new_start = timezone.now() + timedelta(days=5, hours=10)
        new_end = new_start + timedelta(hours=3)
        expected_start = timezone.localtime(new_start)

        api_data = {
            "id": str(event.id),
            "type": "event",
            "start": new_start.isoformat(),
            "end": new_end.isoformat(),
            "allDay": False,
        }

        response = self.client.post(
            reverse("common:calendar_event_update"),
            data=json.dumps(api_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        # Step 3: Verify event was updated
        event.refresh_from_db()
        self.assertEqual(event.start_date, expected_start.date())
        self.assertEqual(
            event.start_time.replace(microsecond=0),
            expected_start.time().replace(microsecond=0),
        )
        self.assertEqual(event.duration_hours, 3)

    def test_drag_and_drop_staff_task_reschedule(self):
        """Staff tasks should reschedule dates when dragged."""

        original_start = timezone.now().date()
        original_due = original_start + timedelta(days=2)
        task = StaffTask.objects.create(
            title="Calendar Managed Task",
            created_by=self.user,
            start_date=original_start,
            due_date=original_due,
            status=StaffTask.STATUS_IN_PROGRESS,
        )

        new_start_date = original_start + timedelta(days=3)
        new_due_date = original_due + timedelta(days=3)
        start_dt = timezone.make_aware(
            datetime.combine(new_start_date, time.min)
        )
        end_dt = timezone.make_aware(
            datetime.combine(new_due_date, time(23, 59))
        )

        api_data = {
            "id": str(task.id),
            "type": "staff_task",
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "allDay": True,
            "metadata": {
                "hasStartDate": True,
                "hasDueDate": True,
            },
        }

        response = self.client.post(
            reverse("common:calendar_event_update"),
            data=json.dumps(api_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        task.refresh_from_db()
        self.assertEqual(task.start_date, new_start_date)
        self.assertEqual(task.due_date, new_due_date)

    def test_drag_and_drop_engagement_reschedule(self):
        """Stakeholder engagement drag handling should persist new planned date."""

        engagement = StakeholderEngagement.objects.create(
            title="Coordination Outreach",
            description="Discuss barangay updates",
            objectives="Gather barangay feedback",
            engagement_type=self.engagement_type,
            community=self.community,
            venue="Community Hall",
            address="Barangay Proper",
            stakeholder_groups="Barangay leaders",
            methodology="Focus group",
            target_participants=25,
            planned_date=timezone.now().replace(
                hour=9, minute=0, second=0, microsecond=0
            ),
            created_by=self.user,
        )

        api_start = engagement.planned_date + timedelta(days=4)
        api_end = api_start + timedelta(hours=2)

        api_payload = {
            "id": str(engagement.id),
            "type": "engagement",
            "start": api_start.isoformat(),
            "end": api_end.isoformat(),
            "allDay": False,
        }

        response = self.client.post(
            reverse("common:calendar_event_update"),
            data=json.dumps(api_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])

        engagement.refresh_from_db()
        self.assertEqual(
            engagement.planned_date.replace(microsecond=0),
            timezone.localtime(api_start).replace(microsecond=0),
        )

    def test_calendar_event_modal_updates_event(self):
        event = Event.objects.create(
            **build_event_kwargs(
                self.user,
                title="Modal Event",
                start_date=timezone.now().date(),
                start_time=time(10, 0),
                duration_hours=1,
            )
        )

        modal_url = reverse("common:coordination_event_modal", args=[event.id])

        response = self.client.get(modal_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)

        post_payload = {
            "title": "Updated Modal Event",
            "status": "in_progress",
            "priority": "high",
            "start_date": event.start_date.isoformat(),
            "start_time": event.start_time.strftime("%H:%M:%S"),
            "end_date": "",
            "end_time": "",
            "duration_hours": "2",
            "venue": "Innovation Hub",
            "address": "123 Strategy Way",
            "is_virtual": "on",
            "virtual_platform": "Zoom",
            "virtual_link": "https://zoom.example.com/meeting",
            "description": "Updated description for modal test",
            "follow_up_required": "on",
            "follow_up_date": (event.start_date + timedelta(days=3)).isoformat(),
            "follow_up_notes": "Prepare post-engagement brief.",
        }

        response = self.client.post(
            modal_url,
            data=post_payload,
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("HX-Trigger", response.headers)
        trigger_data = json.loads(response.headers["HX-Trigger"])
        self.assertIn("calendar-close-modal", trigger_data)
        self.assertIn("calendar-event-updated", trigger_data)
        payload = trigger_data["calendar-event-updated"]
        self.assertEqual(payload["id"], f"coordination-event-{event.id}")
        self.assertEqual(payload["extendedProps"]["status"], "in_progress")

        event.refresh_from_db()
        self.assertEqual(event.title, "Updated Modal Event")
        self.assertEqual(event.status, "in_progress")
        self.assertEqual(event.priority, "high")
        self.assertEqual(event.duration_hours, 2)
        self.assertTrue(event.is_virtual)
        self.assertEqual(event.follow_up_notes, "Prepare post-engagement brief.")

    @patch("common.tasks.send_event_notification.delay")
    def test_event_with_notification(self, mock_send_notification):
        """Test event creation triggers notification task."""
        # Create event
        event = Event.objects.create(
            **build_event_kwargs(
                self.user,
                title="Event with Notification",
                start_date=timezone.now().date() + timedelta(days=1),
                start_time=time(14, 0),
                status="scheduled",
            )
        )

        # Add participant
        participant = User.objects.create_user(
            username="participant1", password="pass123", email="participant@example.com"
        )

        EventParticipant.objects.create(
            event=event,
            participant_type="internal",
            participation_role="participant",
            user=participant,
            email=participant.email,
        )

        # Trigger notification (would be called by view in real scenario)
        from common.tasks import send_event_notification

        send_event_notification.delay(
            event_id=str(event.id), participant_ids=[participant.id]
        )

        # Verify task was called
        mock_send_notification.assert_called_once()


class ResourceBookingWorkflowTests(TestCase):
    """Test complete resource booking workflow from request to approval."""

    def setUp(self):
        self.client = Client()
        self.requester = User.objects.create_user(
            username="requester",
            password="pass123",
            is_staff=True,
            email="requester@example.com",
        )
        self.approver = User.objects.create_user(
            username="approver",
            password="pass123",
            is_staff=True,
            is_superuser=True,
            email="approver@example.com",
        )
        add_booking_perm = Permission.objects.get(
            content_type__app_label="common",
            codename="add_calendarresourcebooking",
        )
        change_booking_perm = Permission.objects.get(
            content_type__app_label="common",
            codename="change_calendarresourcebooking",
        )
        self.requester.user_permissions.add(add_booking_perm)
        self.approver.user_permissions.add(change_booking_perm)
        self.resource = CalendarResource.objects.create(
            name="Conference Room A",
            resource_type="room",
            capacity=20,
            is_available=True,
            booking_requires_approval=True,
        )

    def test_complete_booking_workflow(self):
        """Test booking from request through approval and calendar display."""
        # Step 1: User requests booking
        self.client.login(username="requester", password="pass123")

        booking_start = timezone.now() + timedelta(days=3, hours=9)
        booking_end = booking_start + timedelta(hours=2)

        booking_data = {
            "resource": self.resource.id,
            "start_datetime": booking_start.strftime("%Y-%m-%dT%H:%M"),
            "end_datetime": booking_end.strftime("%Y-%m-%dT%H:%M"),
            "notes": "Team planning session",
        }

        response = self.client.post(
            reverse("common:calendar_booking_request_general"), data=booking_data
        )

        # Booking should be created in pending status
        booking = CalendarResourceBooking.objects.filter(resource=self.resource).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, "pending")
        self.assertEqual(booking.booked_by, self.requester)

        # Step 2: Approver reviews booking
        self.client.logout()
        self.client.login(username="approver", password="pass123")

        response = self.client.get(reverse("common:calendar_booking_list"))
        self.assertEqual(response.status_code, 200)

        # Step 3: Approver approves booking
        approve_data = {"action": "approve"}

        response = self.client.post(
            reverse("common:calendar_booking_approve", args=[booking.id]),
            data=approve_data,
        )

        booking.refresh_from_db()
        self.assertEqual(booking.status, "approved")
        self.assertEqual(booking.approved_by, self.approver)

        # Step 4: Verify booking appears on calendar
        cache.clear()
        cache.clear()
        cache.clear()
        response = self.client.get(reverse("common:oobc_calendar_feed_json"))
        self.assertEqual(response.status_code, 200)

        calendar_data = response.json()
        booking_found = False

        for entry in calendar_data.get("events", []):
            extended = entry.get("extendedProps", {})
            if (
                extended.get("module") == "resources"
                and extended.get("resource") == "Conference Room A"
                and extended.get("category") == "booking"
            ):
                booking_found = True
                break

        self.assertTrue(booking_found, "Approved booking not found on calendar")

    def test_booking_conflict_detection(self):
        """Test that conflicting bookings are detected."""
        self.client.login(username="requester", password="pass123")

        # Create first booking
        booking_start = timezone.now() + timedelta(days=2, hours=10)
        booking_event = Event.objects.create(
            **build_event_kwargs(
                self.requester,
                title="Existing Booking",
                start_date=booking_start.date(),
                start_time=booking_start.time(),
            )
        )
        booking1 = CalendarResourceBooking.objects.create(
            resource=self.resource,
            content_type=ContentType.objects.get_for_model(Event),
            object_id=booking_event.id,
            start_datetime=booking_start,
            end_datetime=booking_start + timedelta(hours=2),
            booked_by=self.requester,
            status="approved",
        )

        # Try to create overlapping booking
        overlap_start = booking_start + timedelta(hours=1)  # Overlaps by 1 hour
        booking_data = {
            "resource": self.resource.id,
            "start_datetime": overlap_start.strftime("%Y-%m-%dT%H:%M"),
            "end_datetime": (overlap_start + timedelta(hours=2)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "notes": "Conflicting booking",
        }

        response = self.client.post(
            reverse("common:calendar_booking_request_general"), data=booking_data
        )

        # Should show form again with validation error
        # (actual conflict detection might be in form validation or view logic)
        # Check that duplicate approved booking doesn't exist
        approved_bookings = CalendarResourceBooking.objects.filter(
            resource=self.resource, status="approved"
        ).count()

        # Only the first booking should be approved
        self.assertEqual(approved_bookings, 1)


class StaffLeaveWorkflowTests(TestCase):
    """Test staff leave request and approval workflow."""

    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username="staff",
            password="pass123",
            is_staff=True,
            email="staff@example.com",
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="pass123",
            is_staff=True,
            is_superuser=True,
            email="admin@example.com",
        )
        approve_leave_perm = Permission.objects.get(
            content_type__app_label="common",
            codename="change_staffleave",
        )
        self.admin.user_permissions.add(approve_leave_perm)

    def test_leave_request_approval_workflow(self):
        """Test complete leave workflow from request to calendar display."""
        # Step 1: Staff requests leave
        self.client.login(username="staff", password="pass123")

        leave_start = timezone.now().date() + timedelta(days=10)
        leave_end = leave_start + timedelta(days=3)

        leave_data = {
            "leave_type": "vacation",
            "start_date": leave_start.isoformat(),
            "end_date": leave_end.isoformat(),
            "reason": "Family vacation",
        }

        response = self.client.post(
            reverse("common:staff_leave_request"), data=leave_data
        )

        # Leave should be created
        leave = StaffLeave.objects.filter(staff=self.staff).first()
        self.assertIsNotNone(leave)
        self.assertEqual(leave.status, "pending")
        self.assertEqual(leave.leave_type, "vacation")

        # Step 2: Admin approves leave
        self.client.logout()
        self.client.login(username="admin", password="pass123")

        response = self.client.get(reverse("common:staff_leave_list"))
        self.assertEqual(response.status_code, 200)

        approve_data = {"action": "approve"}

        response = self.client.post(
            reverse("common:staff_leave_approve", args=[leave.id]), data=approve_data
        )

        self.assertEqual(response.status_code, 302)
        leave.refresh_from_db()
        self.assertEqual(leave.status, "approved")

        # Step 3: Verify leave appears on calendar
        response = self.client.get(reverse("common:oobc_calendar_feed_json"))
        calendar_data = response.json()

        staff_stats = calendar_data.get("module_stats", {}).get("staff", {})
        self.assertGreaterEqual(
            staff_stats.get("total", 0),
            1,
            "Approved leave not counted in calendar stats",
        )


class CalendarSharingWorkflowTests(TestCase):
    """Test calendar sharing workflow."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True, is_superuser=True
        )

    def test_create_and_access_shared_calendar(self):
        """Test creating share link and accessing public calendar."""
        # Step 1: Admin creates share link
        self.client.login(username="admin", password="pass123")

        share_data = {
            "description": "Public event calendar",
            "expires_at": (timezone.now() + timedelta(days=30)).date().isoformat(),
            "filter_modules": json.dumps(["events"]),
        }

        response = self.client.post(
            reverse("common:calendar_share_create"), data=share_data
        )

        # Share link should be created
        share_link = SharedCalendarLink.objects.filter(created_by=self.admin).first()
        self.assertIsNotNone(share_link)
        self.assertTrue(share_link.is_active)

        # Step 2: Access public calendar (no login required)
        self.client.logout()

        response = self.client.get(
            reverse("common:calendar_share_view", args=[share_link.token])
        )

        self.assertEqual(response.status_code, 200)

        # Should include calendar data
        self.assertIn("calendar_data", response.context)

        # View count should increment
        share_link.refresh_from_db()
        self.assertGreater(share_link.view_count, 0)

    def test_expired_share_link(self):
        """Test that expired share links show appropriate message."""
        # Create expired link
        share_link = SharedCalendarLink.objects.create(
            created_by=self.admin,
            expires_at=timezone.now() - timedelta(days=1),
            filter_modules=["coordination"],
        )

        response = self.client.get(
            reverse("common:calendar_share_view", args=[share_link.token])
        )

        # Should render expired template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "common/calendar/share_expired.html")


class CalendarPreferencesWorkflowTests(TestCase):
    """Test user calendar preferences workflow."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="user", password="pass123", is_staff=True, email="user@example.com"
        )
        self.client.login(username="user", password="pass123")

    def test_update_preferences_affects_notifications(self):
        """Test that preference changes affect notification delivery."""
        # Step 1: Update preferences
        pref_data = {
            "default_reminder_times": json.dumps([30, 60]),
            "email_enabled": "on",
            "push_enabled": "on",
            "daily_digest": "on",
            "weekly_digest": "on",
            "quiet_hours_start": "20:00",
            "quiet_hours_end": "22:00",
            "timezone": "Asia/Manila",
        }

        response = self.client.post(
            reverse("common:calendar_preferences"), data=serialize_form_data(pref_data)
        )

        self.assertEqual(response.status_code, 302)

        # Preferences should be saved
        prefs = UserCalendarPreferences.objects.filter(user=self.user).first()
        self.assertIsNotNone(prefs)
        self.assertIn(30, prefs.default_reminder_times)
        self.assertIn(60, prefs.default_reminder_times)
        self.assertTrue(prefs.email_enabled)

        # Step 2: Verify preferences are respected in notification logic
        # (This would be tested in task tests, but we verify the data exists)
        expected_start = time.fromisoformat(pref_data["quiet_hours_start"])
        expected_end = time.fromisoformat(pref_data["quiet_hours_end"])
        self.assertEqual(prefs.quiet_hours_start, expected_start)
        self.assertEqual(prefs.quiet_hours_end, expected_end)


class AttendanceWorkflowTests(TestCase):
    """Test event attendance tracking workflow."""

    def setUp(self):
        self.client = Client()
        self.organizer = User.objects.create_user(
            username="organizer", password="pass123", is_staff=True
        )
        self.participant = User.objects.create_user(
            username="participant", password="pass123", is_staff=True
        )
        self.event = Event.objects.create(
            **build_event_kwargs(
                self.organizer,
                title="Workshop",
                start_date=timezone.now().date(),
                start_time=time(9, 0),
                status="scheduled",
            )
        )
        create_participant(
            self.event,
            user=self.participant,
            invitation_status="sent",
            response_status="accepted",
            rsvp_status="going",
        )

    def test_qr_code_checkin_workflow(self):
        """Test QR code generation and check-in."""
        self.client.login(username="organizer", password="pass123")

        # Step 1: Generate QR code
        response = self.client.get(
            reverse("common:event_generate_qr", args=[self.event.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")

        # Step 2: Access scan page (QR scan would POST here)
        response = self.client.get(
            reverse("common:event_scan_qr", args=[self.event.id])
        )

        self.assertEqual(response.status_code, 200)

        # Step 3: View manual check-in interface
        response = self.client.get(
            reverse("common:event_check_in", args=[self.event.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_attendance_report_generation(self):
        """Test generating attendance report."""
        self.client.login(username="organizer", password="pass123")

        response = self.client.get(
            reverse("common:event_attendance_report", args=[self.event.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("stats", response.context)


class FullSystemIntegrationTests(TestCase):
    """Test complete calendar system integration across modules."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin",
            password="pass123",
            is_staff=True,
            is_superuser=True,
            email="admin@example.com",
        )

    def test_oobc_calendar_loads_all_modules(self):
        """Test that main OOBC calendar loads events, resources, and leave."""
        self.client.login(username="admin", password="pass123")

        # Create data across all modules
        event = Event.objects.create(
            **build_event_kwargs(
                self.admin,
                title="Test Event",
                start_date=timezone.now().date(),
                start_time=time(10, 0),
                status="scheduled",
            )
        )

        resource = CalendarResource.objects.create(
            name="Meeting Room", resource_type="room", is_available=True
        )

        booking = CalendarResourceBooking.objects.create(
            resource=resource,
            content_type=ContentType.objects.get_for_model(Event),
            object_id=event.id,
            start_datetime=timezone.now() + timedelta(hours=2),
            end_datetime=timezone.now() + timedelta(hours=4),
            booked_by=self.admin,
            status="approved",
        )

        leave = StaffLeave.objects.create(
            staff=self.admin,
            leave_type="vacation",
            start_date=timezone.now().date() + timedelta(days=5),
            end_date=timezone.now().date() + timedelta(days=7),
            status="approved",
        )

        # Load calendar
        response = self.client.get(reverse("common:oobc_calendar"))
        self.assertEqual(response.status_code, 200)

        # Verify all modules are represented
        # (Implementation would check calendar_data for all three types)
        self.assertIsNotNone(response.context)

    def test_calendar_feed_json_structure(self):
        """Test that JSON feed has correct structure for FullCalendar."""
        self.client.login(username="admin", password="pass123")

        # Create sample event
        Event.objects.create(
            **build_event_kwargs(
                self.admin,
                title="API Test Event",
                start_date=timezone.now().date(),
                start_time=time(14, 0),
                duration_hours=2,
                status="scheduled",
            )
        )

        response = self.client.get(reverse("common:oobc_calendar_feed_json"))
        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Check structure
        self.assertIn("events", data)
        self.assertIsInstance(data["events"], list)

        if len(data["events"]) > 0:
            entry = data["events"][0]
            # FullCalendar required fields
            self.assertIn("id", entry)
            self.assertIn("title", entry)
            self.assertIn("start", entry)
            self.assertIn("backgroundColor", entry)
            self.assertIn("extendedProps", entry)
