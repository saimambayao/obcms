# OBCMS Component Testing Plan

## Scope
- Align component-level testing across OBCMS modules with platform architecture (Django apps, HTMX-driven UI, service adapters).
- Provide ready-to-implement guidelines that QA and engineering teams can execute without introducing timeline estimates.

## Test Categories

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

## Execution Notes
- Use `pytest --ds=obc_management.settings` with granular markers (`@pytest.mark.component`) to segment component suites.
- Maintain factories in `src/<app>/tests/factories.py` to keep fixtures DRY and reuse across categories.
- Update this plan alongside new modules; ensure each addition lists priority, complexity, dependencies, and prerequisites before implementation begins.
