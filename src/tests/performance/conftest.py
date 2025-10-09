"""Shared fixtures for calendar performance tests."""

from __future__ import annotations

import os

import pytest
from django.test import Client

from tests.perf_utils import factories
from tests.perf_utils.runner import PerfHTTPRunner


if os.getenv("PERF", "1") == "0":  # pragma: no cover - controlled via env
    pytest.skip("Performance suite disabled via PERF=0", allow_module_level=True)


@pytest.fixture
def perf_http_runner() -> PerfHTTPRunner:
    return PerfHTTPRunner(Client())


@pytest.fixture(
    params=[
        ("baseline", 80, 30, 8),
        ("stress", 320, 120, 24),
    ],
    ids=["baseline", "stress"],
)
def perf_calendar_dataset(request, db):
    label, event_count, booking_count, leave_count = request.param
    user = factories.create_staff_user(f"perf_admin_{label}")
    factories.seed_calendar_dataset(
        user,
        event_count=event_count,
        booking_count=booking_count,
        leave_count=leave_count,
    )
    return {"user": user, "label": label}


@pytest.fixture(
    params=[("baseline", 40), ("stress", 160)],
    ids=["baseline", "stress"],
)
def perf_booking_dataset(request, db):
    label, booking_count = request.param
    user = factories.create_staff_user(f"perf_scheduling_{label}")
    resource, base_start = factories.create_resource_with_bookings(
        user, booking_count=booking_count
    )
    return {
        "user": user,
        "resource": resource,
        "base_start": base_start,
        "label": label,
    }


@pytest.fixture(
    params=[("baseline", 30), ("stress", 120)],
    ids=["baseline", "stress"],
)
def perf_attendance_dataset(request, db):
    label, participant_count = request.param
    owner = factories.create_staff_user(f"perf_attendance_{label}")
    event, participants = factories.create_attendance_event(
        owner, participant_count=participant_count
    )
    return {
        "owner": owner,
        "event": event,
        "participant": participants[0],
        "label": label,
    }
