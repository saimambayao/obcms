# OBCMS k6 Load Testing Plan

## Purpose
- Establish a repeatable load-, stress-, and resilience-testing workflow for OBCMS using k6.
- Validate that API endpoints, HTMX interactions, and background services sustain expected concurrency while meeting latency and reliability targets.
- Provide engineering and QA teams with actionable guidance that aligns with existing testing, observability, and release practices.

## Tooling Overview
- k6 strengths: JavaScript-based scenarios, threshold assertions, checks for functional validation, and first-class CLI/CI integration.
- Supported executors: `constant-vus`, `ramping-vus`, `arrival-rate`, `ramping-arrival-rate`, and `externally-controlled` to progressively stress services.
- Outputs: native summary metrics, JSON exports, HTML trends (via `summary-trend`), and integrations with InfluxDB, Prometheus, and Grafana using `k6 run --out`.

## Repository Layout
- Scripts directory: `tests/performance/k6/` for scenario entry points (`*.js`).
- Shared helpers: `tests/performance/k6/lib/` for auth token acquisition, payload builders, request factories, metric tags, and response validators.
- Environment configuration: `tests/performance/k6/env.example.json` mirroring `.env` keys without sensitive values; each environment creates its own `env.<name>.json` ignored by git.

## Test Scenarios

### Scenario 1: Public & Authenticated API Requests
- **Priority:** CRITICAL
- **Complexity:** Moderate
- **Dependencies:** DRF endpoints, authentication middleware, rate-limit policies.
- **Prerequisites:** Seeded database (`./manage.py loaddata` fixtures), API client credentials, persona-specific user accounts.
- **Focus Areas:**
  - CRUD flows for high-traffic modules (communities, coordination tasks, policy tracking).
  - WorkItem operations, recommendations APIs, planning/budget endpoints, and executive metrics feeds.
  - Role-based throttling and permission checks (provincial coordinator, municipal facilitator, central admin).
  - Latency thresholds: `p(95) < 500ms` for read-heavy endpoints; `< 700ms` for write-heavy endpoints.

### Scenario 2: HTMX Interaction Bursts
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** HTMX endpoints, partial templates, `HX-Trigger` notifications.
- **Prerequisites:** Representative user journeys captured via HAR recordings or manual tracing with request headers.
- **Focus Areas:**
  - Simulate concurrent partial updates (dashboard filters, kanban card moves) using HTTP requests with HTMX headers.
  - Cover monitoring dashboards, WorkItem calendars, recommendations quick actions, and analytics widgets.
  - Observe response payload sizes, CPU usage, and database query counts using Django debug logs.
  - Assert thresholds on `http_req_duration` and custom metrics for template rendering time.

### Scenario 3: Background Workflow Entry Points
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Celery task triggers exposed through HTTP/REST or scheduled endpoints.
- **Prerequisites:** Task queue configured in the test environment, visibility into worker metrics, and celery beat schedules.
- **Focus Areas:**
  - Drive task-enqueuing endpoints at peak expected rates; track queue depth and processing latency.
  - Use custom k6 metrics to record HTTP response time and worker acknowledgements (webhooks, log scrapes, or Prometheus counters).
  - Target WorkItem escalation triggers, recommendation approvals, and planning/budget recalculation tasks.

### Scenario 4: File Upload and Document Processing
- **Priority:** MEDIUM
- **Complexity:** Complex
- **Dependencies:** Document upload endpoints, storage adapters, virus scanning hooks.
- **Prerequisites:** Synthetic documents sized to match production medians, temporary storage buckets, `CONTENT_SECURITY_POLICY` overrides for test hosts.
- **Focus Areas:**
  - Multipart upload throughput under concurrent load and resumable upload handling (if enabled).
  - Validate response codes, processing completion times, and generated metadata records.
  - Thresholds on failure rates (`http_req_failed < 1%`) and end-to-end processing duration.

### Scenario 5: Authentication & Session Resilience
- **Priority:** MEDIUM
- **Complexity:** Simple
- **Dependencies:** Login endpoints, JWT/session issuance, refresh mechanisms, MFA bypass switches for automation.
- **Prerequisites:** Test accounts for each role, configured CAPTCHA bypass or test secret, CSRF exemptions for scripted clients when applicable.
- **Focus Areas:**
  - Burst logins to verify session store performance and cache eviction behaviour.
  - Token refresh under sustained concurrency, ensuring no elevated `401`/`403` rates.
  - Checks confirming security headers and cookie flags remain intact.

### Scenario 6: Monitoring Calendar & WorkItem Streams
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Monitoring calendar feeds, WorkItem sync APIs, dashboard polling intervals.
- **Prerequisites:** Staff accounts mapped to WorkItems, datasets with varied statuses, calendar sharing and subscriptions enabled.
- **Focus Areas:**
  - Sustain concurrent polling of calendar and dashboard endpoints to measure cache effectiveness and prevent thundering herd effects.
  - Stress WorkItem update endpoints (status/progress changes) while dashboards poll for updates.
  - Thresholds: `p(95) http_req_duration < 600ms` for calendar feeds; WorkItem update failure rate `< 0.5%`.

### Scenario 7: Executive Analytics & Recommendations
- **Priority:** MEDIUM
- **Complexity:** Moderate
- **Dependencies:** Trend analytics APIs, budget feedback endpoints, recommendations listings.
- **Prerequisites:** Seeded analytics KPIs, recommendation datasets, cache warming scripts for dashboards.
- **Focus Areas:**
  - Simulate high-frequency dashboard refreshes alongside recommendation filtering and bookmarking actions.
  - Track cache hit ratios and database query volume; ensure `http_req_failed < 1%`.
  - Maintain aggregated response latency at `p(95) < 750ms` under sustained concurrency.

## Execution Strategy
- Define scenario profiles in `tests/performance/k6/scenarios.js`, combining executors (`ramping-arrival-rate` for endurance, `constant-vus` for regression baselines).
- Store threshold definitions alongside scenarios to fail runs automatically when metrics exceed targets, enabling CI gating.
- Parameterize base URLs, credentials, dataset identifiers, and feature flags via environment variables (`K6_BASE_URL`, `K6_CLIENT_ID`, etc.).
- Use tagged checks (`check(res, { 'status 200': r => r.status === 200 })`) and `group()` blocks to structure metrics per feature.

## Data & Environment Management
- Maintain a dedicated performance database snapshot to avoid polluting development data; refresh via scripted fixtures.
- Ensure Celery workers, cache backends, and background services mirror production configurations (Redis, database replicas) where feasible.
- Leverage `k6 run --tag scenario=<name>` to mark runs by build number, environment, and scenario for downstream dashboards.

## Observability & Reporting
- Preferred command: `k6 run --out json=./reports/k6_run.json --summary-export=./reports/k6_summary.json`.
- For sustained monitoring, integrate with:
  - Grafana Cloud or self-hosted Grafana via Prometheus remote-write.
  - InfluxDB + Grafana using `k6 run --out influxdb=http://localhost:8086/k6`.
  - OpenTelemetry collector if existing observability stack already emits OTLP metrics.
- Document interpretation guidelines in `docs/testing/performance/` (e.g., regression notes, spike root causes).

## CI/CD Integration
- Add a workflow (e.g., `ci/performance.yml`) that provisions services via docker-compose, then runs targeted k6 scripts on demand (nightly or manual dispatch).
- Guard merges by requiring the performance workflow to pass for critical modules; allow manual overrides with documented risk acceptance.
- Upload artifacts (JSON summaries, trend HTML) to CI for traceability and share quick-look graphs with release notes.

## Governance & Review
- Version-control scenario scripts; enforce code review by platform leads before changing thresholds or executor shapes.
- When new modules ship, append scenarios with clearly stated priority, dependencies, and prerequisites to keep coverage current.
- Maintain a changelog within `tests/performance/k6/README.md` capturing scenario additions, metric target adjustments, and known exceptions.

## Next Actions
- **Priority:** HIGH | **Complexity:** Moderate — Bootstrap `tests/performance/k6/` scaffold, including base script, shared helpers, and environment templates.
- **Priority:** MEDIUM | **Complexity:** Moderate — Implement Grafana dashboards wired to k6 outputs (JSON, Prometheus, or InfluxDB).
- **Priority:** MEDIUM | **Complexity:** Simple — Schedule recurring performance test execution aligned with release cadences and annotate runs in release notes.
