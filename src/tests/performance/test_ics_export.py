"""Performance checks for the calendar ICS feed."""

from __future__ import annotations

import pytest

from tests.perf_utils.runner import record_perf_metric


@pytest.mark.django_db
@pytest.mark.performance
def test_calendar_ics_export(perf_calendar_dataset, perf_http_runner):
    user = perf_calendar_dataset["user"]
    label = perf_calendar_dataset["label"]

    result = perf_http_runner.get("common:oobc_calendar_feed_ics", user=user)

    assert result.status_code == 200
    assert result.query_count <= 18, result.query_count
    assert result.duration_ms < 1_500, f"ICS export took {result.duration_ms:.2f} ms"
    assert result.payload_bytes > 0
    record_perf_metric(
        "calendar_feed_ics",
        result,
        extra={
            "label": label,
            "payload_bytes": result.payload_bytes,
        },
    )
