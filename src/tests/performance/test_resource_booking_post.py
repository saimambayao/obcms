"""Performance benchmark for submitting resource booking requests."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from common.models import CalendarResourceBooking
from tests.perf_utils.runner import record_perf_metric


@pytest.mark.django_db
@pytest.mark.performance
def test_resource_booking_post(perf_booking_dataset, perf_http_runner):
    user = perf_booking_dataset["user"]
    resource = perf_booking_dataset["resource"]
    label = perf_booking_dataset["label"]

    latest_booking = (
        CalendarResourceBooking.objects.filter(resource=resource)
        .order_by("-end_datetime")
        .first()
    )
    base_start = latest_booking.end_datetime if latest_booking else timezone.now()
    submission_start = timezone.localtime(base_start + timedelta(minutes=45)).replace(
        microsecond=0
    )
    form_data = {
        "resource": resource.pk,
        "start_datetime": submission_start.strftime("%Y-%m-%dT%H:%M"),
        "end_datetime": (submission_start + timedelta(hours=2)).strftime(
            "%Y-%m-%dT%H:%M"
        ),
        "notes": "Performance benchmark submission",
    }

    initial_count = CalendarResourceBooking.objects.filter(resource=resource).count()

    result = perf_http_runner.post(
        "common:calendar_booking_request_general",
        user=user,
        data=form_data,
        expected_status=None,
    )

    assert result.status_code in {200, 302}
    assert (
        CalendarResourceBooking.objects.filter(resource=resource).count()
        == initial_count + 1
    )
    assert result.query_count <= 18, result.query_count
    assert result.duration_ms < 650, f"Booking POST took {result.duration_ms:.2f} ms"
    record_perf_metric(
        "resource_booking_post",
        result,
        extra={"label": label},
    )
