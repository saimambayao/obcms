"""Performance checks for the consolidated calendar feed."""

from __future__ import annotations

import pytest

from tests.perf_utils.runner import record_perf_metric


@pytest.mark.django_db
@pytest.mark.performance
def test_calendar_feed_performance(perf_calendar_dataset, perf_http_runner):
    user = perf_calendar_dataset["user"]
    label = perf_calendar_dataset["label"]

    result = perf_http_runner.get(
        "common:oobc_calendar_feed_json",
        user=user,
        params={"modules": "coordination,staff"},
    )

    assert result.status_code == 200
    assert result.query_count <= 18, result.query_count
    assert result.duration_ms < 750, f"Feed took {result.duration_ms:.2f} ms"
    assert result.payload_bytes > 0
    record_perf_metric(
        "calendar_feed",
        result,
        extra={
            "label": label,
            "payload_bytes": result.payload_bytes,
        },
    )
