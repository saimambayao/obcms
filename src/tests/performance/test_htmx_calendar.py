"""Performance checks for the coordination calendar HTMX fragment."""

from __future__ import annotations

import pytest

from tests.perf_utils.runner import record_perf_metric


@pytest.mark.django_db
@pytest.mark.performance
def test_coordination_calendar_htmx(perf_calendar_dataset, perf_http_runner):
    user = perf_calendar_dataset["user"]
    label = perf_calendar_dataset["label"]

    result = perf_http_runner.get("common:coordination_calendar", user=user)

    assert result.status_code == 200
    assert result.query_count <= 20, result.query_count
    assert result.duration_ms < 900, f"HTMX calendar took {result.duration_ms:.2f} ms"
    assert result.payload_bytes <= 358_400, result.payload_bytes
    record_perf_metric(
        "coordination_calendar_htmx",
        result,
        extra={
            "label": label,
            "payload_bytes": result.payload_bytes,
        },
    )
