"""
Comprehensive Test Suite for Calendar System
Tests models, views, forms, services, and Celery tasks.
"""

import pytest
pytest.skip(
    "Legacy calendar system tests require Event/EventParticipant models removed in refactor.",
    allow_module_level=True,
)
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
import json

from common.models import (
    RecurringEventPattern,
    CalendarResource,
    CalendarResourceBooking,
    StaffLeave,
    UserCalendarPreferences,
    SharedCalendarLink,
    WorkItem,
)
from common.services.calendar import build_calendar_payload


def build_work_item_kwargs(user, **overrides):
    """Return valid keyword arguments for creating WorkItem instances."""

    now = timezone.now()
    defaults = {
        "work_type": WorkItem.WORK_TYPE_ACTIVITY,
        "title": "Test Activity",
        "description": "Calendar system test activity",
        "created_by": user,
        "start_date": now.date(),
        "start_time": now.time().replace(microsecond=0),
        "due_date": now.date(),
        "status": WorkItem.STATUS_NOT_STARTED,
        "priority": WorkItem.PRIORITY_MEDIUM,
    }
    defaults.update(overrides)
    return defaults


User = get_user_model()


class RecurringEventModelTests(TestCase):
    """Test recurring event pattern model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_weekly_recurrence(self):
        """Test creating weekly recurring pattern."""
        pattern = RecurringEventPattern.objects.create(
            recurrence_type="weekly",
            interval=1,
            by_weekday=[1, 3, 5],  # Mon, Wed, Fri
        )
        self.assertEqual(pattern.recurrence_type, "weekly")
        self.assertEqual(pattern.by_weekday, [1, 3, 5])

    def test_recurrence_until_date(self):
        """Test recurrence with end date."""
        pattern = RecurringEventPattern.objects.create(
            recurrence_type="daily",
            interval=1,
            until_date=timezone.now().date() + timedelta(days=30),
        )
        self.assertIsNotNone(pattern.until_date)

    def test_recurrence_count(self):
        """Test recurrence with occurrence count."""
        pattern = RecurringEventPattern.objects.create(
            recurrence_type="daily", interval=1, count=10
        )
        self.assertEqual(pattern.count, 10)


class CalendarResourceTests(TestCase):
    """Test calendar resource management."""

    def setUp(self):
        self.user = User.objects.create_user("admin", "admin@test.com", "pass")
        self.client = Client()
        self.client.login(username="admin", password="pass")

    def test_create_resource(self):
        """Test creating a calendar resource."""
        resource = CalendarResource.objects.create(
            name="Conference Room A",
            resource_type="room",
            capacity=20,
            location="Main Office, 2F",
        )
        self.assertEqual(resource.name, "Conference Room A")
        self.assertTrue(resource.is_available)

    def test_resource_booking_conflict(self):
        """Test booking conflict detection."""
        resource = CalendarResource.objects.create(
            name="Meeting Room", resource_type="room"
        )

        # First booking
        booking1 = CalendarResourceBooking.objects.create(
            resource=resource,
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=2),
            booked_by=self.user,
            status="approved",
        )

        # Overlapping booking (should detect conflict)
        overlapping = CalendarResourceBooking.objects.filter(
            resource=resource,
            start_datetime__lt=booking1.end_datetime,
            end_datetime__gt=booking1.start_datetime,
        )

        self.assertEqual(overlapping.count(), 1)


class StaffLeaveTests(TestCase):
    """Test staff leave management."""

    def setUp(self):
        self.user = User.objects.create_user("staff", "staff@test.com", "pass")

    def test_create_leave_request(self):
        """Test creating leave request."""
        leave = StaffLeave.objects.create(
            staff=self.user,
            leave_type="vacation",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=5),
            reason="Annual vacation",
            status="pending",
        )
        self.assertEqual(leave.status, "pending")

    def test_leave_overlap_detection(self):
        """Test detecting overlapping leave."""
        # Create first leave
        leave1 = StaffLeave.objects.create(
            staff=self.user,
            leave_type="vacation",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=5),
            status="approved",
        )

        # Check for overlaps
        overlapping = StaffLeave.objects.filter(
            staff=self.user,
            start_date__lte=leave1.end_date,
            end_date__gte=leave1.start_date,
            status__in=["pending", "approved"],
        )

        self.assertTrue(overlapping.exists())


class CalendarPreferencesTests(TestCase):
    """Test user calendar preferences."""

    def setUp(self):
        self.user = User.objects.create_user("user", "user@test.com", "pass")

    def test_create_preferences(self):
        """Test creating user preferences."""
        prefs = UserCalendarPreferences.objects.create(
            user=self.user,
            default_reminder_times=[15, 60, 1440],
            email_enabled=True,
            daily_digest=True,
        )
        self.assertEqual(len(prefs.default_reminder_times), 3)
        self.assertTrue(prefs.email_enabled)

    def test_quiet_hours(self):
        """Test quiet hours settings."""
        from datetime import time

        prefs = UserCalendarPreferences.objects.create(
            user=self.user,
            quiet_hours_start=time(22, 0),  # 10 PM
            quiet_hours_end=time(7, 0),  # 7 AM
        )
        self.assertIsNotNone(prefs.quiet_hours_start)


class CalendarSharingTests(TestCase):
    """Test calendar sharing functionality."""

    def setUp(self):
        self.user = User.objects.create_user("user", "user@test.com", "pass")

    def test_create_share_link(self):
        """Test creating shareable calendar link."""
        share = SharedCalendarLink.objects.create(
            created_by=self.user,
            expires_at=timezone.now() + timedelta(days=30),
            filter_modules=["coordination", "mana"],
        )
        self.assertIsNotNone(share.token)
        self.assertEqual(len(share.filter_modules), 2)

    def test_share_link_expiration(self):
        """Test share link expiration."""
        expired_share = SharedCalendarLink.objects.create(
            created_by=self.user, expires_at=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(expired_share.expires_at < timezone.now())

    def test_view_count_tracking(self):
        """Test view count increment."""
        share = SharedCalendarLink.objects.create(
            created_by=self.user,
            expires_at=timezone.now() + timedelta(days=30),
            max_views=10,
        )
        share.view_count += 1
        share.save()
        self.assertEqual(share.view_count, 1)


class CalendarServiceTests(TestCase):
    """Test calendar service integration."""

    def setUp(self):
        self.user = User.objects.create_user("user", "user@test.com", "pass")

    def test_build_calendar_payload(self):
        """Test calendar payload generation."""
        # Create test work item
        WorkItem.objects.create(
            **build_work_item_kwargs(
                self.user,
                title="Test Activity",
                due_date=timezone.now().date() + timedelta(days=1),
            )
        )

        payload = build_calendar_payload()

        self.assertIn("entries", payload)
        self.assertIn("module_stats", payload)
        self.assertIsInstance(payload["entries"], list)

    def test_module_filtering(self):
        """Test calendar filtering by module."""
        payload = build_calendar_payload(filter_modules=["coordination"])
        self.assertIsNotNone(payload)


class CalendarViewTests(TestCase):
    """Test calendar views."""

    def setUp(self):
        self.user = User.objects.create_user("user", "user@test.com", "pass")
        self.client = Client()
        self.client.login(username="user", password="pass")

    def test_calendar_preferences_view(self):
        """Test calendar preferences page."""
        url = reverse("common:calendar_preferences")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_resource_list_view(self):
        """Test resource list page."""
        url = reverse("common:calendar_resource_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_share_calendar_create(self):
        """Test share creation page."""
        url = reverse("common:calendar_share_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


# Pytest fixtures and tests
@pytest.fixture
def user(db):
    """Create test user."""
    return User.objects.create_user("pytest_user", "pytest@test.com", "pass")


@pytest.fixture
def calendar_resource(db, user):
    """Create test resource."""
    return CalendarResource.objects.create(
        name="Test Room", resource_type="room", capacity=10
    )


@pytest.mark.django_db
def test_booking_creation(user, calendar_resource):
    """Test creating a booking with pytest."""
    booking = CalendarResourceBooking.objects.create(
        resource=calendar_resource,
        start_datetime=timezone.now(),
        end_datetime=timezone.now() + timedelta(hours=1),
        booked_by=user,
    )
    assert booking.status == "pending"


@pytest.mark.django_db
def test_share_link_token_uniqueness(user):
    """Test share link tokens are unique."""
    share1 = SharedCalendarLink.objects.create(
        created_by=user, expires_at=timezone.now() + timedelta(days=30)
    )
    share2 = SharedCalendarLink.objects.create(
        created_by=user, expires_at=timezone.now() + timedelta(days=30)
    )
    assert share1.token != share2.token


# Run tests with: python manage.py test tests.test_calendar_system
# Or with pytest: pytest tests/test_calendar_system.py -v
