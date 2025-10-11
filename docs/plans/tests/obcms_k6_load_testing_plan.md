# OBCMS k6 Load Testing Plan

## Purpose
- Establish a repeatable load- and stress-testing workflow for OBCMS using k6.
- Ensure API endpoints, HTMX interactions, and background services sustain expected concurrency while meeting latency and reliability targets.
- Provide engineering and QA teams with actionable guidance that fits existing testing and observability practices.

## Tooling Overview
- k6 core strengths: JavaScript-based scenarios, threshold assertions, checks for functional validation, and first-class CLI/CI integration.
- Supported executors: `constant-vus`, `ramping-vus`, `arrival-rate`, and `externally-controlled` for progressive stress evaluation.
- Outputs: native summary metrics, JSON exports, and integrations with InfluxDB, Prometheus, and Grafana (via `k6 run --out`).

## Repository Layout
- Proposed scripts directory: `tests/performance/k6/`.
- Shared helpers module: `tests/performance/k6/lib/` for auth token acquisition, payload builders, and metric tags.
- Environment configuration file: `tests/performance/k6/env.example.json` mirroring `.env` secrets (omit real credentials from git).

## Test Scenarios

### 1. Public & Authenticated API Requests
- **Priority:** CRITICAL
- **Complexity:** Moderate
- **Dependencies:** DRF endpoints, authentication middleware, rate-limit policies.
- **Prerequisites:** Seeded database (`./manage.py loaddata` fixtures), API client credentials, seeded users per persona.
- **Focus Areas:**
  - CRUD flows for high-traffic modules (communities, coordination tasks, policy tracking).
  - Include monitoring WorkItem operations, recommendations APIs, planning/budget endpoints, and executive metrics feeds.
  - Role-specific throttling and permission checks (e.g., provincial coordinator vs. central admin).
  - Response latency thresholds: `p(95) < 500ms` for standard reads, `< 700ms` for write-heavy endpoints.

### 2. HTMX Interaction Bursts
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** HTMX endpoints, partial templates, `HX-Trigger` notifications.
- **Prerequisites:** Representative user journeys captured in HAR files or manual tracing.
- **Focus Areas:**
  - Simulate concurrent partial updates (e.g., dashboard filters, kanban card moves) via HTTP requests that mirror HTMX headers.
  - Cover monitoring dashboards, WorkItem calendars, recommendations quick actions, and analytics widgets.
  - Validate response payload sizes, CPU usage, and database query counts via Django debug logs.
  - Assert thresholds on `http_req_duration` and custom metrics for template rendering time.

### 3. Background Workflow Entry Points
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Celery task triggers exposed through HTTP/REST or scheduled endpoints.
- **Prerequisites:** Task queue configured in test environment, ability to monitor worker throughput.
- **Focus Areas:**
  - Drive task-enqueuing endpoints at peak expected rates, ensuring queue depth and processing latency stay within acceptable bounds.
  - Use custom k6 metrics to record HTTP response time and worker acknowledgement events (via webhooks or log scraping).
  - Target WorkItem escalation triggers, recommendation approval workflows, and planning/budget recalculation tasks.

### 4. File Upload and Document Processing
- **Priority:** MEDIUM
- **Complexity:** Complex
- **Dependencies:** Document upload endpoints, storage adapters, virus scanning hooks.
- **Prerequisites:** Synthetic documents sized to match production medians, temporary storage buckets.
- **Focus Areas:**
  - Multipart upload throughput under concurrent load.
  - Validation of response codes, processing completion times, and generated metadata records.
  - Thresholds on failure rates (`http_req_failed < 1%`) and end-to-end processing duration.

### 5. Authentication & Session Resilience
- **Priority:** MEDIUM
- **Complexity:** Simple
- **Dependencies:** Login endpoints, JWT/session issuance, refresh mechanisms.
- **Prerequisites:** Test accounts for each role, captcha or MFA bypass switches for automated runs.
- **Focus Areas:**
  - Login bursts to verify session store performance.
  - Token refresh under sustained concurrency, ensuring no elevated `401`/`403` rates.
  - Custom checks confirming security headers remain intact.

## Execution Strategy
- Define scenario profiles in `tests/performance/k6/scenarios.js`, combining multiple executors per test run (`ramping-arrival-rate` for endurance, `constant-vus` for baseline regression).
- Store threshold definitions alongside scenarios to fail the run when metrics exceed targets, enabling CI gating.
- Parameterize base URLs, credentials, and dataset identifiers via environment variables: `K6_BASE_URL`, `K6_CLIENT_ID`, etc.
- Use tagged checks (`check(res, { 'status 200': r => r.status === 200 })`) and add `group()` blocks to structure metrics per feature.

## Data & Environment Management
- Maintain a dedicated performance database snapshot to avoid polluting development data; refresh via scripted fixtures.
- Ensure Celery workers and cache backends mirror production configurations (Redis, database write replicas) where feasible.
- Leverage `--tag` options to mark runs by build number, environment, and scenario for downstream dashboards.

## Observability & Reporting
- Recommended output: `k6 run --out json=./reports/k6_run.json --summary-export=./reports/k6_summary.json`.
- For sustained monitoring, integrate with:
  - Grafana Cloud or self-hosted Grafana via Prometheus remote-write.
  - InfluxDB + Grafana stack using `k6 run --out influxdb=http://localhost:8086/k6`.
- Document interpretation guidelines in `reports/performance/` (e.g., spike root causes, regression notes).

## CI/CD Integration
- Add a GitHub Actions (or equivalent) workflow `ci/performance.yml` that spins up services via docker-compose, then runs targeted k6 scripts on demand (nightly or manual dispatch).
- Guard merges by requiring performance workflow to pass for critical modules; optionally allow manual overrides with documented risk acceptance.
- Upload artifacts (JSON summaries, HTML trends) to the CI pipeline for traceability.

## Governance & Review
- Version-control scenario scripts; enforce code review by platform leads before changing thresholds.
- When new modules ship, append corresponding scenarios with clearly stated priority, dependencies, and prerequisites.
- Maintain a changelog within `tests/performance/k6/README.md` capturing scenario additions and metric target adjustments.

## Next Actions
- **Priority:** HIGH — Bootstrap `tests/performance/k6/` scaffold, including base script and environment templates.
- **Priority:** MEDIUM — Implement dashboards in Grafana tied to k6 outputs.
- **Priority:** MEDIUM — Schedule recurring performance test execution aligned with release cadences.
- **6. Monitoring Calendar & WorkItem Streams**
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Monitoring calendar feeds, WorkItem sync APIs, dashboard polling intervals.
- **Prerequisites:** Staff accounts, WorkItem dataset with various statuses, calendar sharing enabled.
- **Focus Areas:**
  - Sustain concurrent polling of calendar and dashboard endpoints to measure cache effectiveness.
  - Stress WorkItem update endpoints (status/progress changes) while dashboards poll for updates.
  - Threshold: `p(95) http_req_duration < 600ms` for calendar feeds; WorkItem update failure rate `< 0.5%`.

- **7. Executive Analytics & Recommendations**
- **Priority:** MEDIUM
- **Complexity:** Moderate
- **Dependencies:** Trend analysis APIs, budget feedback endpoints, recommendations listings.
- **Prerequisites:** Seeded analytics KPIs, recommendation datasets, cache warming scripts.
- **Focus Areas:**
  - Simulate high-frequency dashboard refreshes combined with recommendation filtering.
  - Track cache hit ratios and database query volume; ensure `http_req_failed < 1%`.
  - Capture thresholds for aggregated responses (`p(95) < 750ms`) under sustained concurrency.
