"""Data factories for performance tests."""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable, Tuple

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from common.models import CalendarResource, CalendarResourceBooking, StaffLeave
from coordination.models import Event

User = get_user_model()


def create_staff_user(
    username: str,
    *,
    email: str | None = None,
    is_superuser: bool = True,
    is_staff: bool = True,
) -> User:
    """Create a staff user suited for performance tests."""

    user = User.objects.create_user(
        username=username,
        password="testpass123",
        email=email or f"{username}@example.com",
        is_staff=is_staff,
        is_superuser=is_superuser,
    )
    return user


def create_event(
    owner: User,
    *,
    title: str,
    start_date,
    start_time,
    duration_hours: float = 2.0,
    status: str = "scheduled",
) -> Event:
    """Create a coordination event with required fields populated."""

    return Event.objects.create(
        title=title,
        description="Performance seed event",
        event_type="meeting",
        status=status,
        priority="medium",
        start_date=start_date,
        start_time=start_time,
        duration_hours=duration_hours,
        venue="Performance Hub",
        address="123 Benchmark Ave",
        organizer=owner,
        created_by=owner,
        expected_participants=25,
        actual_participants=0,
    )


def bulk_create_events(owner: User, *, count: int = 150) -> Iterable[Event]:
    """Create a batch of events with staggered dates."""

    events: list[Event] = []
    now = timezone.now()
    for index in range(count):
        start_date = (now + timedelta(days=index % 45)).date()
        start_time = (now + timedelta(minutes=30 * index)).time().replace(microsecond=0)
        events.append(
            create_event(
                owner,
                title=f"Performance Event {index}",
                start_date=start_date,
                start_time=start_time,
                duration_hours=2,
                status="scheduled" if index % 3 else "planned",
            )
        )
    return events


def seed_calendar_dataset(
    owner: User,
    *,
    event_count: int,
    booking_count: int,
    leave_count: int,
) -> None:
    """Seed events, bookings, and leaves for a given owner."""

    bulk_create_events(owner, count=event_count)
    create_resource_with_bookings(owner, booking_count=booking_count)
    create_staff_leaves(owner, count=leave_count)


def create_resource_with_bookings(
    owner: User,
    *,
    booking_count: int = 40,
    start: timezone.datetime | None = None,
) -> Tuple[CalendarResource, timezone.datetime]:
    """Create a resource and a set of bookings anchored around ``start``."""

    resource = CalendarResource.objects.create(
        name="Performance Conference Room",
        resource_type=CalendarResource.RESOURCE_ROOM,
        is_available=True,
        booking_requires_approval=True,
        capacity=30,
    )

    base_start = start or timezone.now() + timedelta(days=1)
    event_type = ContentType.objects.get_for_model(Event)
    template_event = create_event(
        owner,
        title="Booking Seed Event",
        start_date=base_start.date(),
        start_time=base_start.time().replace(microsecond=0),
        duration_hours=2,
        status="scheduled",
    )

    for index in range(booking_count):
        slot_start = base_start + timedelta(hours=2 * index)
        CalendarResourceBooking.objects.create(
            resource=resource,
            content_type=event_type,
            object_id=template_event.id,
            start_datetime=slot_start,
            end_datetime=slot_start + timedelta(hours=1, minutes=30),
            booked_by=owner,
            status=CalendarResourceBooking.STATUS_APPROVED,
            notes="Performance benchmark seed",
        )

    return resource, base_start


def create_staff_leaves(user: User, *, count: int = 12) -> None:
    """Create a spread of staff leave entries for calendar aggregation."""

    today = timezone.now().date()
    for index in range(count):
        start = today + timedelta(days=index * 3)
        StaffLeave.objects.create(
            staff=user,
            leave_type=StaffLeave.LEAVE_VACATION,
            start_date=start,
            end_date=start + timedelta(days=2),
            status=(
                StaffLeave.STATUS_APPROVED
                if index % 2 == 0
                else StaffLeave.STATUS_PENDING
            ),
            reason="Performance dataset",
        )


def create_attendance_event(
    owner: User,
    *,
    participant_count: int = 40,
) -> Event:
    """Create an event ready for attendance tracking.

    NOTE: EventParticipant model was removed during WorkItem migration.
    This function now only creates the event without participants.
    Use WorkItem model for full event functionality.
    """

    now = timezone.now()
    event = create_event(
        owner,
        title="Attendance Benchmark",
        start_date=now.date(),
        start_time=now.time().replace(microsecond=0),
        duration_hours=3,
        status="scheduled",
    )

    return event
