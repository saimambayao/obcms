from datetime import date, time as time_obj

import pytest

try:
    from django.contrib.auth.models import Permission
    from django.test import TestCase
    from django.urls import reverse
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for coordination note tests",
        allow_module_level=True,
    )

from common.models import User
from common.work_item_model import WorkItem
from coordination.models import CoordinationNote


class CoordinationNoteCreateViewTests(TestCase):
    """Ensure coordination notes can be recorded against WorkItem activities."""

    def setUp(self):
        self.url = reverse("common:coordination_note_add")
        self.activity = self._create_activity("Coordination Dialogue", date(2025, 5, 12))
        self.user = User.objects.create_user(
            username="note_taker",
            password="secret123",
            email="note@example.com",
            user_type="admin",
            is_approved=True,
        )

    def _create_activity(self, title, start_date):
        return WorkItem.objects.create(
            title=title,
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            status=WorkItem.STATUS_IN_PROGRESS,
            start_date=start_date,
        )

    def _grant_permission(self):
        permission = Permission.objects.get(
            codename="add_coordinationnote",
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("common:login"), response.url)

    def test_permission_required(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_coordination_note(self):
        self._grant_permission()
        self.client.force_login(self.user)

        post_data = {
            "title": "Minutes: Coordination Dialogue",
            "note_date": "2025-05-12",
            "note_time": "09:00",
            "work_item": str(self.activity.pk),
            "location_description": "Conference Room",
            "meeting_overview": "Discuss coordination roadmap.",
            "key_agenda": "Agenda item 1",
            "discussion_highlights": "Key outcomes captured.",
            "decisions": "Action items confirmed.",
            "action_items": "Prepare briefing note.",
            "follow_up_items": "Share minutes with partners.",
            "attachments_links": "",
            "additional_notes": "",
        }

        response = self.client.post(self.url, post_data)

        self.assertRedirects(response, reverse("common:coordination_events"))
        note = CoordinationNote.objects.get(title="Minutes: Coordination Dialogue")
        self.assertEqual(note.work_item, self.activity)
        self.assertEqual(note.recorded_by, self.user)
        self.assertEqual(note.note_date, date(2025, 5, 12))
        self.assertEqual(note.note_time, time_obj(hour=9))


class CoordinationNoteActivityOptionsTests(TestCase):
    """Validate HTMX activity options endpoint for coordination notes."""

    def setUp(self):
        self.url = reverse("common:coordination_note_activity_options")
        self.user = User.objects.create_user(
            username="note_user",
            password="secret123",
            email="noteuser@example.com",
            user_type="admin",
            is_approved=True,
        )
        self.activity_may = WorkItem.objects.create(
            title="Regional Coordination Dialogue",
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            status=WorkItem.STATUS_NOT_STARTED,
            start_date=date(2025, 5, 15),
        )
        self.activity_june = WorkItem.objects.create(
            title="Municipal Coordination Follow-up",
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            status=WorkItem.STATUS_NOT_STARTED,
            start_date=date(2025, 6, 1),
        )

    def _grant_permission(self):
        permission = Permission.objects.get(
            codename="add_coordinationnote",
            content_type__app_label="coordination",
        )
        self.user.user_permissions.add(permission)

    def test_activity_options_filter_by_date(self):
        self._grant_permission()
        self.client.force_login(self.user)

        response = self.client.get(
            self.url,
            {"note_date": "2025-05-15"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Regional Coordination Dialogue")
        self.assertNotContains(response, "Municipal Coordination Follow-up")
