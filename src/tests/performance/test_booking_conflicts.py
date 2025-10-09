"""Performance checks for resource booking conflict validation."""

from __future__ import annotations

from datetime import timedelta

import pytest

from common.models import CalendarResourceBooking
from tests.perf_utils.runner import measure_callable, record_perf_metric


@pytest.mark.django_db
@pytest.mark.performance
def test_booking_conflict_validation(perf_booking_dataset):
    resource = perf_booking_dataset["resource"]
    base_start = perf_booking_dataset["base_start"]
    label = perf_booking_dataset["label"]

    overlap_start = base_start + timedelta(minutes=45)
    overlap_end = overlap_start + timedelta(hours=2)

    def conflict_lookup() -> bool:
        return CalendarResourceBooking.objects.filter(
            resource=resource,
            start_datetime__lt=overlap_end,
            end_datetime__gt=overlap_start,
            status__in=[
                CalendarResourceBooking.STATUS_PENDING,
                CalendarResourceBooking.STATUS_APPROVED,
            ],
        ).exists()

    result = measure_callable(conflict_lookup)

    assert result.value is True
    assert result.query_count <= 2, result.query_count
    assert result.duration_ms < 120, f"Conflict lookup took {result.duration_ms:.2f} ms"
    record_perf_metric(
        "resource_booking_conflict_lookup",
        result,
        extra={"label": label},
    )
