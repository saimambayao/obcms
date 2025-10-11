# OBCMS Integration Testing Plan

## Purpose
- Verify end-to-end behavior of OBCMS features across Django views, serializers, models, Celery tasks, and HTMX interactions without requiring full browser automation.
- Build on best practices from Django’s testing tools (official documentation on the Django test client) and pytest’s integration guidance (“Good Integration Practices” in pytest docs).
- Provide teams with actionable guidance—using priorities, complexity, dependencies, and prerequisites—so integration suites stay reliable and maintainable.

## Guiding Principles
- Treat integration tests as feature slices: exercise real database interactions, templates, and signals while stubbing only external systems (email gateways, third-party APIs).
- Reuse pytest fixtures for authenticated users, seeded data, and HTMX headers to keep tests succinct.
- Tag integration tests with `@pytest.mark.integration` to separate them from fast unit suites.
- Maintain deterministic data: reset DB between tests (`pytest-django` transactional fixtures) and seed via Factory Boy.

## Test Categories

### API Endpoint Flows
- **Priority:** CRITICAL
- **Complexity:** Moderate
- **Dependencies:** DRF viewsets, serializers, permissions, audit logging.
- **Prerequisites:** Database fixtures, APIClient fixture, role-based auth tokens.
- **Focus Areas:**
  - Full CRUD journeys (create -> read -> update -> delete) for high-traffic modules.
  - Permission matrix validation using real middleware.
  - Assertion of `HX-Trigger` headers, pagination, filtering, and serialized payload structure.
  - Include monitoring WorkItem endpoints, recommendations APIs, planning/budget scenarios, and executive metric feeds alongside core modules.

### HTMX View Interactions
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Template partials, HTMX endpoints, context processors.
- **Prerequisites:** Django test client with `HX-Request` header fixture; sample template data.
- **Focus Areas:**
  - Rendering partials with expected HTML structure and CSS classes (per OBCMS UI standards).
  - Confirming swap behaviors (`hx-swap`), redirect flows, and toast triggers.
  - Validating session state changes (notifications, flash messages).

### Multi-Step Workflows
- **Priority:** HIGH
- **Complexity:** Complex
- **Dependencies:** Workflow services, Celery task triggers, database transactions.
- **Prerequisites:** Celery task inspection mocks (e.g., `celery_app.task_always_eager = True`), seeded data to traverse the workflow.
- **Focus Areas:**
  - Verify that creating/updating records triggers downstream tasks (emails, analytics) with correct payloads.
  - Ensure database state transitions are atomic across steps.
  - Validate HTMX updates or API responses returned after asynchronous triggers.
  - Cover monitoring WorkItem escalations, automated recommendation routing, and budget approval pipelines managed through Celery jobs.

### Monitoring & Calendar Synchronization
- **Priority:** HIGH
- **Complexity:** Complex
- **Dependencies:** Monitoring services, WorkItem sync utilities, calendar serialization helpers.
- **Prerequisites:** Seeded WorkItems linked to PPAs, calendar resources, staff roles.
- **Focus Areas:**
  - Validate that WorkItem changes propagate to monitoring dashboards and calendar feeds.
  - Assert that status/progress sync methods update linked PPAs and trigger alerts.
  - Ensure calendar filters, share settings, and leave requests integrate correctly with monitoring data.

### Cross-App Data Sync
- **Priority:** MEDIUM
- **Complexity:** Complex
- **Dependencies:** Signals, cross-app services (`common`, `data_imports`).
- **Prerequisites:** Factories for linked models; ability to mock external integrations (e.g., data imports from CSV/JSON).
- **Focus Areas:**
  - Ensure changes in one app (e.g., communities) propagate correctly to dependent apps (coordination tasks, policy tracking).
  - Test idempotent retries and duplicate prevention.
  - Capture audit log entries to confirm traceability.
  - Include flows linking WorkItems to PPAs in Project Central, recommendations to policy tracking, and budget adjustments feeding analytics dashboards.

### Reporting & Aggregation Endpoints
- **Priority:** MEDIUM
- **Complexity:** Moderate
- **Dependencies:** ORM aggregation queries, cached dashboards, export views.
- **Prerequisites:** Seeded metrics data, cache backend configured for tests.
- **Focus Areas:**
  - Validate aggregated counts, charts, and exported files through HTTP responses.
  - Confirm cache invalidation after data mutations.
  - Assert query efficiency with `assertNumQueries` where applicable.
  - Cover executive dashboards (trend analysis, budget feedback, staff performance) and monitoring analytics endpoints.

### Recommendations Lifecycle
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Recommendations serializers, approval services, notification hooks.
- **Prerequisites:** Stakeholder fixtures, recommendation type catalogs, mocked notification channels.
- **Focus Areas:**
  - Create, edit, categorize, and approve recommendations while checking stakeholder assignments.
  - Verify that approvals trigger policy tracking updates and appear in management dashboards.
  - Ensure audit logs capture each lifecycle event.

### Planning, Budgeting, and Attendance Flows
- **Priority:** MEDIUM
- **Complexity:** Complex
- **Dependencies:** Planning/budget services (`common`), attendance QR utilities, staff training modules.
- **Prerequisites:** Scenario templates, budget lines, attendance rosters, staff profiles.
- **Focus Areas:**
  - Exercise budget scenario creation, adjustment, and approval flows with downstream analytics updates.
  - Test attendance check-in/out integration with staff performance metrics.
  - Confirm training assignments update staff profiles and associated dashboards.

## Fixtures & Utilities
- Shared fixtures live in `tests/conftest.py` or app-level `tests/conftest.py`:
  - `client` / `api_client`: Authenticated users with role-specific logins.
  - `hx_client`: Wrapper injecting `HX-Request` headers.
  - `celery_eager`: Context manager forcing synchronous task execution (`CELERY_TASK_ALWAYS_EAGER=True`).
  - `mock_external_services`: Pytest fixture to patch SMS/email/Messaging adapters.
- Use Factory Boy for deterministic data creation; store heavy sample payloads under `tests/fixtures/`.

## Tooling & Configuration
- Run with `pytest --ds=obc_management.settings -m integration` to execute only integration suites.
- Leverage Django’s `Client` and REST framework `APIClient` per docs to simulate browser/API interactions.
- Capture HTTP responses using pytest’s `caplog` and `capfd` to assert logs or console output.
- Configure `pytest.ini` markers:
  ```ini
  [pytest]
  markers =
      integration: integration tests spanning multiple components
  ```

## Data Management
- Prefer transactional test cases; rely on `pytest-django`’s `db` fixture to ensure rollbacks.
- For long-running workflows, use `@pytest.mark.django_db(transaction=True)` to allow multi-threading.
- Snapshot baseline data states for high-risk flows (e.g., policy tracking) to detect regressions quickly.

## CI Integration
- Add a dedicated CI job `pytest -m integration` triggered on pull requests touching backend code.
- Run integration suite nightly against staging database snapshots to detect data-related regressions early.
- Publish HTML test reports (pytest `--html` plugin) and database query stats for review.

## Maintenance
- When introducing a new feature, add integration coverage once unit tests pass; keep tests focused on user-observable outcomes.
- Review integration tests quarterly to retire redundant cases or refocus on high-risk areas.
- Document known limitations or required mocks in `tests/README.md` for future contributors.

## Next Actions
- **Priority:** HIGH — Tag existing integration-style tests with `@pytest.mark.integration` and align fixtures with this plan.
- **Priority:** HIGH — Establish `hx_client` and `celery_eager` fixtures to standardize HTMX and async verification.
- **Priority:** MEDIUM — Create CI pipeline entry for integration suite and publish resulting artifacts.
