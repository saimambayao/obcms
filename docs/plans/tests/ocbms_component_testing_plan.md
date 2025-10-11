# OBCMS Component Testing Plan

## Purpose
- Define how component-level testing reinforces OBCMS reliability across Django apps, HTMX-powered UI, and supporting services.
- Supply engineering and QA teams with executable guidance centered on priority, complexity, dependencies, and prerequisites instead of calendar-based estimates.
- Align component testing with adjacent documentation: unit, integration, performance, and end-to-end plans in `docs/plans/tests/`.

## Scope & Component Definition
- Treat a "component" as a cohesive unit that couples presentation, business logic, and integration seams while remaining independently testable.
- Include reusable UI fragments, DRF viewsets, data access helpers, background tasks, messaging adapters, and administrative utilities.
- Exclude cross-module orchestration (handled in integration testing) and fully user-driven workflows (covered by e2e tests).

## Readiness & Completion Criteria
- **Priority:** CRITICAL — Components must have deterministic tests before integration or staging promotion.
- **Complexity:** Moderate — Expect tailored fixtures, mocks, and HTMX coverage; automation is mandatory before feature sign-off.
- **Dependencies:** Respective module factories, shared fixtures in `tests/conftest.py`, and environment toggles defined in settings.
- **Prerequisites:** Migrations applied to `src/db.sqlite3`, feature flags documented, and linked documentation updated when scope expands.

## Component Coverage Categories

### Frontend UI Components
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** UI component standards in `docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`
- **Prerequisites:** Template fragments must use shared components under `src/templates/components/`
- **Coverage Goals:** Validate rendering, interactivity, and HTMX behaviors of isolated templates or reusable fragments (stat cards, quick actions, form inputs).
- **Implementation Notes:**
  - Use Django's `Template` API or `pytest-django` `Client` with `HX-Request` headers to render specific components in isolation.
  - Stub context data (e.g., metrics, user roles) and assert rendered HTML snippets with `pytest-django`'s response content helpers.
  - Validate HTMX attributes (`hx-get`, `hx-target`, `hx-swap`) and accessibility hooks (ARIA labels, focus order).
  - Golden files belong under `src/templates/tests/snapshots/`; keep them in sync with Tailwind utility expectations.
  - Include monitoring dashboards (WorkItem summaries, calendars), recommendations cards, planning/budget widgets, and executive analytics tiles in component snapshots to ensure consistent visuals.

### API Endpoint Components
- **Priority:** CRITICAL
- **Complexity:** Moderate
- **Dependencies:** Endpoint serializers and permission classes in `src/<app>/views.py` and `src/<app>/serializers.py`
- **Prerequisites:** Factory fixtures for users and domain objects (`src/<app>/tests.py`)
- **Coverage Goals:** Request/response contract, validation, authorization, and HTMX triggers in DRF views.
- **Implementation Notes:**
  - Drive views with `APIClient` or `RequestFactory`, mocking downstream services (e.g., `common.emails`, `mana.matching`).
  - Assert status codes, serialized payloads, `HX-Trigger` headers, and audit logging records.
  - Include regression cases for edge permissions (e.g., provincial coordinator vs. OBC central staff).
  - Cover monitoring APIs (WorkItem operations, calendar feeds), recommendations endpoints, planning/budget scenario APIs, and executive dashboard data feeds alongside existing modules.

### Data Access Components
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Django ORM models, custom querysets, and repository helpers under `src/common` and app-level `repositories.py`
- **Prerequisites:** Migrations applied to `src/db.sqlite3`; transactional test cases via `pytest.mark.django_db`
- **Coverage Goals:** Query correctness, constraint handling, transaction safety, and migration compatibility.
- **Implementation Notes:**
  - Seed fixtures using factories; verify CRUD flows and complex filters (e.g., policy tracking status aggregations).
  - Test soft-delete or visibility filters to prevent data leakage across communities.
  - Cover raw SQL utilities in `data_imports` with temporary tables and rollback assertions.
  - Add monitoring-derived aggregation helpers, recommendations ranking, and planning/analytics KPI computations to the data-access suite.

### Background Jobs & Workflow Tasks
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Celery tasks in `src/<app>/tasks.py`, schedulers, and workflow orchestrators
- **Prerequisites:** Task queue configuration in settings and patchable service adapters
- **Coverage Goals:** Job orchestration, retries, emitted events, and idempotency.
- **Implementation Notes:**
  - Use `celery.app.task` `apply` helpers or `pytest` fixtures to invoke tasks synchronously.
  - Mock integrations (email gateways, SMS, analytics) and confirm audit trail updates.
  - Assert HTMX notifications or WebSocket events triggered after successful completion.

### Messaging Interfaces
- **Priority:** MEDIUM
- **Complexity:** Moderate
- **Dependencies:** Kafka/Rabbit adapters or internal publish/subscribe utilities in `src/common/messaging`
- **Prerequisites:** Stub message broker clients; fixtures for payload schemas
- **Coverage Goals:** Consumer acknowledgement paths, payload validation, and publisher retries.
- **Implementation Notes:**
  - Simulate inbound payloads, inspect state mutations, and verify outbound routing keys.
  - Ensure malformed messages surface actionable errors without crashing workers.

### Authentication & Authorization Components
- **Priority:** CRITICAL
- **Complexity:** Moderate
- **Dependencies:** Auth backends, permission evaluators, policy guards in `src/common/auth` and app policies
- **Prerequisites:** Role/permission fixtures and user session factories
- **Coverage Goals:** Token generation, policy enforcement, and audit trail visibility.
- **Implementation Notes:**
  - Test positive and negative paths for each role (OOBC admin, provincial officer, municipal coordinator).
  - Exercise decorator utilities such as `common.utils.moa_permissions` with `RequestFactory` requests to ensure MOA RBAC rules raise `PermissionDenied` for unauthorized organizations, PPAs, and work items.
  - Verify permission denial responses include HTMX-safe error banners where applicable.
  - Confirm expired or tampered tokens trigger secure logouts and incident logging.

### Caching Layer Components
- **Priority:** MEDIUM
- **Complexity:** Simple
- **Dependencies:** Cache adapters in `src/common/cache.py` and app-specific caching utilities
- **Prerequisites:** Configurable cache backend (Redis/memory) with test overrides
- **Coverage Goals:** Cache population, invalidation rules, and fallback behavior.
- **Implementation Notes:**
  - Stub cache backend using `django.core.cache.cache` with `locmem` settings.
  - Assert correct key construction, TTL settings, and data freshness after invalidation triggers.

### File & Media Pipelines
- **Priority:** MEDIUM
- **Complexity:** Moderate
- **Dependencies:** Storage adapters, document processors, and media transforms in `src/documents` and related apps
- **Prerequisites:** Temporary storage directories and factory-generated files
- **Coverage Goals:** Upload validation, transformation fidelity, metadata extraction, and cleanup.
- **Implementation Notes:**
  - Use in-memory files via `SimpleUploadedFile`; stub cloud storage (`storages.backends`).
  - Validate virus scanning hooks, file size caps, and thumbnail generation.
  - Confirm failures surface HTMX error banners and leave database records consistent.

### CLI & Administrative Utilities
- **Priority:** LOW
- **Complexity:** Simple
- **Dependencies:** Management commands under `src/<app>/management/commands/`
- **Prerequisites:** Fixture datasets and isolated settings toggles
- **Coverage Goals:** Argument parsing, protected operations, and success/error exit codes.
- **Implementation Notes:**
  - Invoke commands via `call_command` inside tests; capture stdout/stderr for assertions.
  - Mock destructive operations (e.g., bulk deletes) and confirm dry-run safeguards.

## Tooling & Environment
- **Primary Command:** `pytest --ds=obc_management.settings -m component` (extend `pytest.ini` markers if missing).
- **Component Harness:** Prefer pytest fixtures that render templates, execute DRF views, or exercise services without full page reloads.
- **HTMX Simulation:** Attach `HX-Request: true` headers and verify `HX-Trigger`, `HX-Redirect`, and swap behavior; leverage `hx-swap="outerHTML swap:300ms"` conventions.
- **Snapshot Management:** Store HTML or JSON snapshots under `tests/snapshots/component/`; review diffs alongside Tailwind class updates to avoid regressions.

## Test Data & Fixture Strategy
- Maintain factories in `src/<app>/tests/factories.py` (or `tests/factories/`) to generate minimal, component-focused data.
- Use `pytest.mark.django_db(transaction=True)` only when the component performs complex transactional logic; keep default function-level transactions otherwise.
- Keep HTMX state fixtures (e.g., `data-task-id` attributes, swap targets) reusable across UI component tests.
- When stubbing external services, record the expected payload shape in `tests/fixtures/` and document assumptions inline.

## CI Integration & Reporting
- Add a CI job that runs `pytest -m component --ds=obc_management.settings` after unit tests and before integration tests.
- Fail fast when component coverage dips: enforce mandatory assertion counts for each component category and track them in coverage reports.
- Emit `JUnitXML` artifacts for component suites so dashboards can break down pass/fail ratios by module and priority.

## Documentation Guardrails
- Mirror this plan in automated checks under `tests/documentation/` to ensure headings, priority callouts, and dependency notes stay intact.
- Update related plans (unit, integration, e2e, performance) whenever new component categories appear; cross-link using relative paths.
- Treat documentation updates as part of component definition of done; no feature closes without verifying plan alignment.

## Continuous Improvement Actions
- **Priority:** HIGH — Audit existing component tests for coverage gaps in HTMX-driven templates and DRF responses; tag them with `@pytest.mark.component`.
- **Priority:** MEDIUM — Introduce golden snapshot reviews for stat cards, quick action tiles, and executive dashboards.
- **Priority:** MEDIUM — Extend Celery and messaging component suites with failure-mode tests to verify retry logic and audit logging consistency.
- **Priority:** LOW — Capture CLI component outputs in structured fixtures to speed up drift detection.
