# OBCMS Unit Testing Plan

## Purpose
- Establish consistent unit testing practices tailored to OBCMS' Django-based architecture.
- Align with recommendations from Django’s official testing overview and pytest tooling guides reviewed (Django 5.0 testing docs; pytest usage docs).
- Provide engineering teams with actionable direction that emphasizes priority, complexity, dependencies, and prerequisites instead of calendar-based schedules.

## Testing Principles
- Keep unit tests isolated: mock external services (email, messaging, storage) and avoid hitting the database unless the code under test is an ORM abstraction.
- Prefer pytest style tests with fixtures and parametrization; leverage `pytest-django` for Django integration points.
- Use descriptive naming `test_<behavior>` and store tests alongside app modules (`src/<app>/tests.py` or `src/<app>/tests/test_<module>.py`).
- Maintain high signal: each test should assert a single behavior or closely related outcomes.

## App Coverage Expectations
- Every Django app in `src/` must own a unit test suite that covers its domain logic before component or integration tests run.
- **communities** (Priority: HIGH, Complexity: Moderate) — focus on directory filters, community status transitions, and form validators.
  Dependencies: shared location fixtures and permission matrix updates.
  Prerequisites: region and province seed data plus baseline municipality records in place.
- **coordination** (Priority: HIGH, Complexity: Moderate) — cover task assignment services, HTMX helpers, and notification policies.
  Dependencies: HTMX component templates and notification channel mocks.
  Prerequisites: user role fixtures for coordinators, facilitators, and LGU reviewers.
- **mana** (Priority: HIGH, Complexity: Moderate) — validate facilitator workflows, scoring utilities, and eligibility rules.
  Dependencies: scoring configuration constants and attendance calculators.
  Prerequisites: workshop factory fixtures and facilitator account seeds.
- **policies** (Priority: HIGH, Complexity: Moderate) — assert policy creation serializers, permission checks, and audit logging hooks.
  Dependencies: DRF serializer base classes and audit signal dispatchers.
  Prerequisites: fixture policy categories and role-to-permission maps.
- **documents** (Priority: HIGH, Complexity: Moderate) — test upload validators, metadata extraction services, and storage adapters with mocks.
  Dependencies: storage adapter interfaces and antivirus stubs.
  Prerequisites: representative file fixtures (PDF, DOCX, image) and metadata mapping tables.
- **policy_tracking** (Priority: HIGH, Complexity: Moderate) — cover status aggregation queries, progression calculators, and alert thresholds.
  Dependencies: reporting QuerySets and data warehouse adapters.
  Prerequisites: monitoring entry fixtures spanning draft, review, and completed states.
- **ai_assistant** (Priority: MEDIUM, Complexity: Complex) — unit test intent classification utilities, prompt builders, and guardrails with stubbed AI clients.
  Dependencies: prompt templates and tokenizer utilities.
  Prerequisites: stubbed embedding providers or deterministic mock clients.
- **common** (Priority: CRITICAL, Complexity: Moderate) — ensure shared utilities (auth, caching, forms) have exhaustive unit coverage.
  Dependencies: authentication middlewares and caching layer wrappers.
  Prerequisites: staff account fixtures, cache backend settings, and shared form partials available.
- **monitoring** (Priority: CRITICAL, Complexity: Complex) — validate WorkItem integration services, calendar sync utilities, escalation calculators, and analytics helpers.
  Dependencies: WorkItem factories, calendar sync adapters, and escalation policy constants.
  Prerequisites: seeded monitoring entries and Celery task stubs.
- **recommendations** (Priority: HIGH, Complexity: Moderate) — test recommendation scoring, categorization utilities, stakeholder assignment logic, and serializer validation.
  Dependencies: tagging utilities and recommendation weighting matrices.
  Prerequisites: recommendation fixture data across documents, policies, and coordination tasks.
- **planning & analytics dashboards (common)** (Priority: HIGH, Complexity: Moderate) — cover budget feedback computations, trend analysis helpers, attendance processing, and KPI aggregators.
  Dependencies: analytics calculators in `src/common/analytics` and HTMX dashboard fragments.
  Prerequisites: synthetic timeseries fixtures and attendance CSV samples.
- **data_imports** (Priority: HIGH, Complexity: Complex) — exercise parsers, mapping utilities, and validation rules using synthetic fixtures.
  Dependencies: import schema definitions and error logging helpers.
  Prerequisites: fixture spreadsheets for population, budget, and policy data plus mapping config JSON.
- Add new apps with matching coverage expectations during scaffolding; update this section to reflect their responsibilities and dependencies.

## Coverage Targets

### Domain Logic (Services, Utilities)
- **Priority:** CRITICAL
- **Complexity:** Simple
- **Dependencies:** Business logic modules in `src/<app>/services.py`, `src/common`.
- **Prerequisites:** Factory Boy fixtures or lightweight object builders.
- **Guidelines:**
  - Test pure functions with direct assertions on return values and side effects.
  - Use `pytest.mark.parametrize` for matrix coverage (e.g., eligibility checks, status transitions).
  - Mock external integrations using `monkeypatch` or `unittest.mock.patch`.

### Django Models & QuerySets
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Model methods, custom managers, signals.
- **Prerequisites:** Database access via `pytest.mark.django_db`, migrations applied, factory fixtures.
- **Guidelines:**
  - Focus on logic inside model methods (e.g., computed fields, validation) rather than Django internals.
  - For custom QuerySets, assert generated SQL behavior indirectly by checking result sets on seeded data.
  - Use `assertNumQueries` (from Django test tools) when ensuring query counts stay minimal.

### Serializers & Forms
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** DRF serializers, Django forms, validators.
- **Prerequisites:** Representative payload fixtures, dependency stubs (e.g., permission checks).
- **Guidelines:**
  - Validate `is_valid()` paths with both valid and invalid data, asserting error messages and cleaned data structures.
  - Confirm side-effect methods (e.g., `create`, `update`) interact with repositories correctly via mocks.
  - Ensure form widget attributes conform to OBCMS UI standards (class names, aria labels).

### Views (Logic Extraction)
- **Priority:** MEDIUM
- **Complexity:** Moderate
- **Dependencies:** View helper functions, permission gates, HTMX response builders.
- **Prerequisites:** Request factories (`APIRequestFactory`, Django `RequestFactory`), mocked user/session objects.
- **Guidelines:**
  - Where view logic is complex, extract helper functions/services and unit test them separately.
  - For remaining view-level unit tests, use factory requests and assert status codes, templates, or context keys.
  - Verify HTMX headers (`HX-Trigger`, `HX-Redirect`) for components relying on partial updates.

### Signals & Event Hooks
- **Priority:** MEDIUM
- **Complexity:** Moderate
- **Dependencies:** Django signals, Celery task triggers.
- **Prerequisites:** Signal registration isolated within apps, fixtures to create triggering instances.
- **Guidelines:**
  - Use `django.test.utils.override_settings` to isolate side effects.
  - Mock downstream tasks to assert they are enqueued with expected payloads.

### Permission & Policy Helpers
- **Priority:** CRITICAL
- **Complexity:** Moderate
- **Dependencies:** `src/common/auth`, app-level `policies.py`.
- **Prerequisites:** Role fixtures, policy configuration constants.
- **Guidelines:**
  - Assert both allow and deny paths for each role combination.
  - Cover edge cases highlighted in incident reports or bug backlog.

## Tooling & Configuration
- Use `pytest --ds=obc_management.settings` for all runs; adopt `pytest.ini` markers such as `unit` to segment suites.
- Configure `pytest.ini` to fail on skipped markers without explicit reason (`--strict-markers`), mirroring pytest documentation guidance.
- Keep `conftest.py` focused: define shared fixtures (e.g., `user_factory`, `auth_headers`, `celery_task_mock`).
- Enforce coverage thresholds via `coverage run -m pytest` and `coverage report --fail-under=85`.

## Fixture Strategy
- Prefer Factory Boy factories stored under `src/<app>/tests/factories.py`.
- Use `pytest.fixture` scoped to function for mutable objects; escalate to `module` scope for expensive setups only after measurement.
- Store JSON payload samples in `tests/fixtures/` and load with `pathlib.Path` for reuse across tests.

## Mocking & Isolation
- Adopt `unittest.mock.patch` context managers or decorators to stub external APIs and Celery tasks.
- For HTMX responses, mock `request.headers` to include `HX-Request`.
- Use `freezegun` (already in requirements) to freeze time-sensitive tests such as deadline calculations.

## Test Maintenance
- Enforce linting via `black`, `isort`, and `flake8` on test modules; integrate with pre-commit hooks.
- When bugs are fixed, add regression unit tests capturing the exact failure path before closing issues.
- Document notable fixtures or helper utilities in `tests/README.md` (or create if absent) for discoverability.

## Automation & CI
- Ensure `pytest -k unit` (or equivalent marker) runs on every pull request in CI before integration tests.
- Cache `.pytest_cache` and `pip` directories in CI to keep feedback fast.
- Publish coverage reports as CI artifacts; surface deltas in merge requests.

## Documentation Quality Assurance
- Guard this plan with automated tests in `tests/documentation/test_unit_testing_plan_doc.py` so required sections and language conventions stay intact.
- Keep assertions focused on priority, complexity, dependencies, and prerequisites to align with OBCMS delivery guidelines.
- Extend the checks whenever new sections are introduced so reviewers immediately see missing coverage or outdated phrasing.

## Next Actions
- **Priority:** HIGH — Audit existing tests to confirm unit coverage aligns with this plan; tag tests with `@pytest.mark.unit`.
- **Priority:** HIGH — Create or update shared factories and fixtures per app to reduce duplication.
- **Priority:** MEDIUM — Extend CI pipelines to fail when coverage drops below agreed thresholds.
