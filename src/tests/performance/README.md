# Calendar Performance Tests

The tests in this package benchmark critical calendar flows. Each module focuses on a single scenario and enforces upper bounds for query counts and response times. The helpers in `tests/perf_utils/` seed realistic data and wrap requests with instrumentation.

## Running Locally

```bash
scripts/run_calendar_perf.sh
```

Pass additional pytest arguments as needed, e.g. `scripts/run_calendar_perf.sh -k calendar_feed`.

The script exports `PERF_METRICS_FILE` so every scenario appends its measurements to `var/perf_reports/perf_<timestamp>.json`. Invoke the script with `PERF=0` to skip the suite entirely.

## Adding New Scenarios

1. Extend or add data factories in `tests/perf_utils/factories.py` if the scenario requires new fixtures.
2. Create a test module under `tests/performance/` and mark tests with `@pytest.mark.performance`.
3. Use `PerfHTTPRunner` or `measure_callable` to capture timing and query counts; assert the agreed thresholds.
4. Document the new flow and thresholds in `docs/testing/calendar_performance_plan.md`.

## Maintenance

- Threshold changes must be agreed with the calendar module owners.
- The suite is intended to run nightly in CI via `scripts/run_calendar_perf.sh`.
- A quarterly review should confirm that scenarios and datasets still reflect production usage.
