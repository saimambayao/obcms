"""Helper utilities for creating calendar resource bookings from tasks."""

from __future__ import annotations

from datetime import datetime, timedelta, time
from typing import Iterable, Mapping, Sequence

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone

from common.models import CalendarResource, CalendarResourceBooking
from common.work_item_model import WorkItem


class ResourceBookingSpecError(ValueError):
    """Raised when a booking specification cannot be fulfilled."""


def _ensure_aware(dt: datetime) -> datetime:
    if timezone.is_aware(dt):
        return dt
    return timezone.make_aware(dt, timezone.get_current_timezone())


def _resolve_datetime(
    task: WorkItem, spec: Mapping[str, object], attr_prefix: str
) -> datetime | None:
    value = spec.get(attr_prefix)
    if value:
        if isinstance(value, datetime):
            return _ensure_aware(value)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ResourceBookingSpecError(
                    f"Invalid datetime format for '{attr_prefix}': {value}"
                ) from exc
            return _ensure_aware(parsed)
    # Use offsets if explicit datetime not provided
    base_date = task.start_date or task.due_date
    if not base_date:
        return None

    base_dt = datetime.combine(base_date, time(hour=8))
    base_dt = _ensure_aware(base_dt)

    offset_days_key = f"{attr_prefix}_offset_days"
    offset_hours_key = f"{attr_prefix}_offset_hours"

    offset = timedelta(
        days=int(spec.get(offset_days_key, 0) or 0),
        hours=int(spec.get(offset_hours_key, 0) or 0),
    )
    return base_dt + offset


def _determine_end_datetime(
    start_dt: datetime | None, spec: Mapping[str, object], task: WorkItem
) -> datetime | None:
    value = spec.get("end")
    if value:
        if isinstance(value, datetime):
            return _ensure_aware(value)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ResourceBookingSpecError(
                    f"Invalid datetime format for 'end': {value}"
                ) from exc
            return _ensure_aware(parsed)

    duration_hours = spec.get("duration_hours")
    if start_dt and duration_hours is not None:
        try:
            duration = float(duration_hours)
        except (TypeError, ValueError) as exc:
            raise ResourceBookingSpecError("duration_hours must be numeric") from exc
        return start_dt + timedelta(hours=duration)

    # Fallback to task due_date if available
    if task.due_date:
        end_dt = datetime.combine(task.due_date, time(hour=17))
        return _ensure_aware(end_dt)

    return start_dt


def _resolve_resource(spec: Mapping[str, object]) -> CalendarResource | None:
    resource_id = spec.get("resource_id")
    if resource_id:
        return CalendarResource.objects.filter(pk=resource_id).first()

    resource_name = spec.get("resource_name")
    if resource_name:
        return CalendarResource.objects.filter(name=resource_name).first()

    return None


def create_bookings_for_task(
    task: WorkItem,
    specs: Sequence[Mapping[str, object]] | Mapping[str, object],
    *,
    user=None,
) -> list[CalendarResourceBooking]:
    """Create resource bookings for a task based on specification objects.

    Args:
        task: The WorkItem instance to associate bookings with.
        specs: Iterable of booking specifications. Each spec supports the
            following keys:

            - ``resource_id`` or ``resource_name`` (required)
            - ``start`` / ``end`` (ISO string or ``datetime``)
            - ``start_offset_days`` / ``start_offset_hours``
            - ``end`` / ``duration_hours``
            - ``status`` (defaults to ``pending``)
            - ``notes`` (optional)
            - ``approved_by`` (user id) and ``status``
        user: user initiating the booking; defaults to task.created_by.

    Returns:
        List of persisted ``CalendarResourceBooking`` objects.

    Raises:
        ResourceBookingSpecError: if specifications are invalid.
        ValidationError: if any booking fails model validation.
    """

    if not specs:
        return []

    if isinstance(specs, Mapping):
        specs = [specs]

    bookings: list[CalendarResourceBooking] = []
    booked_by = user or task.created_by
    if booked_by is None:
        raise ResourceBookingSpecError(
            "A booked_by user is required to create bookings"
        )

    content_type = ContentType.objects.get_for_model(task)

    for spec in specs:
        if not isinstance(spec, Mapping):
            raise ResourceBookingSpecError(
                "Each booking specification must be a mapping"
            )

        resource = _resolve_resource(spec)
        if resource is None:
            raise ResourceBookingSpecError(
                "Resource could not be resolved for booking spec"
            )

        start_dt = _resolve_datetime(task, spec, "start")
        if start_dt is None:
            raise ResourceBookingSpecError(
                "Unable to determine start datetime for booking"
            )

        end_dt = _determine_end_datetime(start_dt, spec, task)
        if end_dt is None:
            raise ResourceBookingSpecError(
                "Unable to determine end datetime for booking"
            )

        status = spec.get("status", CalendarResourceBooking.STATUS_PENDING)
        notes = spec.get("notes") or f"Auto-booked for task: {task.title}"

        booking = CalendarResourceBooking(
            resource=resource,
            start_datetime=start_dt,
            end_datetime=end_dt,
            status=status,
            notes=notes,
            booked_by=booked_by,
        )
        booking.content_type = content_type
        booking.object_id = task.pk

        approved_by_id = spec.get("approved_by")
        if approved_by_id:
            booking.approved_by_id = approved_by_id

        # Validate before saving to surface conflicts
        booking.full_clean()
        booking.save()
        bookings.append(booking)

    return bookings
