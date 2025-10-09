"""Performance checks for manual attendance check-in."""

from __future__ import annotations

import pytest

from tests.perf_utils.runner import record_perf_metric


@pytest.mark.django_db
@pytest.mark.performance
def test_attendance_check_in(perf_attendance_dataset, perf_http_runner):
    owner = perf_attendance_dataset["owner"]
    event = perf_attendance_dataset["event"]
    participant = perf_attendance_dataset["participant"]
    label = perf_attendance_dataset["label"]

    result = perf_http_runner.post(
        "common:event_check_in",
        user=owner,
        reverse_kwargs={"event_id": event.id},
        data={"participant_id": participant.id, "action": "check_in"},
        expected_status=302,
    )

    assert result.query_count <= 8, result.query_count
    assert result.duration_ms < 450, f"Check-in took {result.duration_ms:.2f} ms"
    record_perf_metric(
        "attendance_check_in",
        result,
        extra={"label": label},
    )
