# OBCMS Integration Testing Plan

## Purpose
- Validate cross-layer behaviour inside OBCMS without the overhead of full browser automation, covering Django views, DRF endpoints, Celery tasks, HTMX partials, and persistence touchpoints.
- Apply practices recommended by the Django Test Client, pytest-django, and pytest “Good Integration Practices” so suites stay deterministic and debuggable.
- Provide engineering and QA teams with actionable priorities, complexities, dependencies, and prerequisites—no timelines—so integration coverage evolves methodically alongside features.

## Scope & Objectives
- Exercise business-critical workflows end-to-end within the Django stack (request → model → signal → serializer/template).
- Guarantee instant UI expectations (HTMX `hx-swap` behaviour, toast triggers, stat card refreshes) align with `docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`.
- Confirm asynchronous boundaries (Celery, notifications, analytics jobs) produce observable side effects and user feedback.
- Keep data deterministic by seeding through factories and transactional fixtures, supporting nightly runs against staging snapshots.

## Tooling & Infrastructure
- **Priority:** CRITICAL | **Complexity:** Moderate
- **Dependencies:** `pytest`, `pytest-django`, Factory Boy, DRF test clients, shared fixtures (`tests/conftest.py`, `src/<app>/tests/conftest.py`), and `pytest.ini` markers.
- **Prerequisites:** Marker registration, environment bootstrapped via `./scripts/bootstrap_venv.sh`, dependencies installed from `requirements/development.txt`, and migrations applied to the preserved `src/db.sqlite3`.
- **Practices:**
  - Tag every multi-component case with `@pytest.mark.integration`.
  - Load HTMX headers using the `hx_client` fixture so responses can assert `HX-Trigger` payloads.
  - Force Celery jobs to execute synchronously during tests through the `celery_eager` fixture.
  - Capture logs with `caplog` / `capfd` to verify asynchronous telemetry.
  - Example `pytest.ini` stanza:
    ```ini
    [pytest]
    markers =
        integration: integration tests spanning multiple components
    ```

## Environment Configuration
- **Priority:** CRITICAL | **Complexity:** Moderate
- **Dependencies:** Django settings module (`obc_management.settings`), Celery configuration, Redis broker (patched when not present), email/SMS adapters (mocked), and cached dashboards.
- **Prerequisites:**
  - `.env` populated from `.env.example` with optional Gemini / SMS credentials when enabling related tests.
  - Deterministic seed data provided via Factory Boy.
  - Database state reset per test using pytest-django transactional fixtures (`db`, `transactional_db`).
  - External APIs mocked at the service layer; keep connectors behind injectable helpers for easy patching.

## Coverage Pillars

### API Endpoint Flows
- **Priority:** CRITICAL | **Complexity:** Moderate
- **Dependencies:** DRF viewsets, serializers, permissions, throttling, audit logging.
- **Prerequisites:** Authenticated `APIClient` instances, role-aware factories, permission fixtures.
- **Focus Areas:**
  - CRUD journeys for high-traffic apps (monitoring, coordination, recommendations, policy tracking, communities).
  - Permission matrices with middleware engaged (RBAC, MOA scoping, HTMX-aware guards).
  - Response contract validation (pagination, filtering, serializer payloads, optional `HX-Trigger` headers).
  - Regression coverage for WorkItem APIs, planning/budget scenarios, and executive metric feeds.

### HTMX View Interactions
- **Priority:** HIGH | **Complexity:** Moderate
- **Dependencies:** Template partials, HTMX endpoints, context processors, instant UI helpers.
- **Prerequisites:** `hx_client` fixture, deterministic template data, reusable form/table components from `src/templates/components/`.
- **Focus Areas:**
  - Rendering partials with canonical DOM structure (rounded-xl cards, emerald focus states, chevron icons).
  - Verifying `HX-Trigger` payloads that drive toast messaging, counter refreshes, and optimistic updates.
  - Confirming `hx-swap` directives, redirect flows, and session state (messages framework) updates.
  - Ensuring UI contracts remain WCAG 2.1 AA compliant across mobile/desktop breakpoints.

### Multi-Step Workflows
- **Priority:** HIGH | **Complexity:** Complex
- **Dependencies:** Workflow services, Celery task triggers, signal listeners, transactional boundaries.
- **Prerequisites:** `celery_eager` fixture, factories for intermediate records, mocks for third-party connectors.
- **Focus Areas:**
  - Chain-of-events verification (record creation → Celery execution → downstream models/messages).
  - Atomic operations and idempotent retries when workflows partially succeed.
  - Monitoring escalations, automated recommendation routing, budget approvals, AI chat follow-ups.

### Monitoring & Calendar Synchronization
- **Priority:** HIGH | **Complexity:** Complex
- **Dependencies:** Monitoring services, WorkItem builders, calendar serializers, WorkItem tree regeneration logic.
- **Prerequisites:** `monitoring_entry_factory`, `execution_project_builder`, seeded WorkItems, patched calendar exports.
- **Focus Areas:**
  - Propagating WorkItem progress/status into MonitoringEntry stat cards and dashboards.
  - Confirming calendar feeds reflect WorkItem updates (filters, share settings, leave requests).
  - Validating HTMX partials (`work_items_summary`, `work_items_tab`) including toast triggers when regeneration fails.

### Cross-App Data Sync
- **Priority:** MEDIUM | **Complexity:** Complex
- **Dependencies:** Django signals, shared services (`src/common`, `src/data_imports`), audit logging, idempotency safeguards.
- **Prerequisites:** Linked model factories, patchable import/export pipelines, audit-log capture helpers.
- **Focus Areas:**
  - Communities → coordination/policy tracking propagation.
  - WorkItems ↔ Project Central (execution project mirroring, progress syncing).
  - Duplicate prevention and retry logic with traceable audit entries.

### Reporting & Aggregation Endpoints
- **Priority:** MEDIUM | **Complexity:** Moderate
- **Dependencies:** ORM aggregations, cached dashboards, export responders (CSV/XLS), query optimizers.
- **Prerequisites:** Seeded metrics datasets, configured cache backend, `assertNumQueries` helpers.
- **Focus Areas:**
  - Validating aggregate counts, charts, and export payloads.
  - Ensuring cache invalidation occurs after data mutations.
  - Confirming executive dashboards (trend analysis, staff performance, budget feedback) stay in sync with source models.

### Recommendations Lifecycle
- **Priority:** HIGH | **Complexity:** Moderate
- **Dependencies:** Recommendation serializers, approval services, notification hooks, policy tracking connectors.
- **Prerequisites:** Stakeholder fixtures, recommendation catalogs, mocked messaging channels.
- **Focus Areas:**
  - Draft → categorize → approve flows with stakeholder assignment assertions.
  - Downstream updates in policy tracking dashboards and analytics.
  - Audit log coverage for every lifecycle event.

### Planning, Budgeting, and Attendance Flows
- **Priority:** MEDIUM | **Complexity:** Complex
- **Dependencies:** Budget services (`src/common`), QR attendance utilities, staff training modules.
- **Prerequisites:** Scenario templates, budget lines, attendance rosters, staff profiles, patched QR scanners.
- **Focus Areas:**
  - Scenario creation, adjustment, approval, and analytic updates.
  - Attendance check-in/out integration with staff performance metrics.
  - Training assignment syncing to profiles and dashboards.

## Fixtures & Data Utilities
- Shared fixtures:
  - `client` / `api_client`: role-aware authenticated clients.
  - `hx_client`: Django client with `HX-Request` header for HTMX assertions.
  - `celery_eager`: context manager that sets `CELERY_TASK_ALWAYS_EAGER=True` and `CELERY_TASK_EAGER_PROPAGATES=True`.
  - `mock_external_services`: patches email/SMS/broadcast adapters.
  - Monitoring helpers (`monitoring_entry_factory`, `execution_project_builder`, `monitoring/tests/hx_client`) reused across API and view tests.
- Prefer Factory Boy for deterministic objects; keep heavy payloads under `tests/fixtures/`.
- Assert HTML with DOM-id checks or lightweight parsers (e.g., `BeautifulSoup` when available) to avoid brittle whitespace coupling.

## Execution Strategy
- Primary command: `pytest --ds=obc_management.settings -m integration`.
- Optional subsets: `pytest -m "integration and not slow"` for PR gating; run the full matrix nightly or before release branches.
- Provide shell wrappers (e.g., `scripts/test_integration.sh`) that activate the virtualenv and pass through arguments.
- Limit flaky test retries to two attempts; auto-create a ticket when limits are exceeded.

## Reporting & Observability
- Export HTML/JUnit artifacts (`pytest --html=reports/integration.html --self-contained-html`) for CI review.
- Capture query counts via `pytest-django` `assertNumQueries` contexts, logging spikes for monitoring dashboards.
- Assert structured log output (`HX-Trigger` payloads, Celery event breadcrumbs) using `caplog`.

## Maintenance
- Pair new feature work with integration coverage once unit tests stabilise; focus on user-visible outcomes.
- Review suites quarterly to retire redundant cases, expand to new modules, and refresh fixtures when domain models evolve.
- Document skips and external dependencies in `tests/README.md` alongside remediation plans.

## Next Actions
- **Priority:** HIGH — Tag remaining cross-component tests with `@pytest.mark.integration` and align fixtures with this plan.
- **Priority:** HIGH — Expand monitoring HTMX tests to cover summary/tab partials (verifying `HX-Trigger` contracts and stat-card data).
- **Priority:** MEDIUM — Add a CI workflow stage that runs `pytest -m integration` and publishes HTML + JUnit reports.
- **Priority:** MEDIUM — Introduce smoke subsets (authentication + monitoring + coordination) for PR gating while preserving full nightly coverage.
