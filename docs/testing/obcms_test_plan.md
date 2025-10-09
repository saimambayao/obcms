# OBCMS Test Plan — Executive Summary

This document defines the test strategy, scope, priorities, and concrete test scenarios for the OBCMS project. It covers unit, integration, API, UI/HTMX, end-to-end (E2E), performance, security, and data migration tests. Tests should be reproducible, independent, and automatable via CI. Follow repository conventions: tests live under `src/<app>/tests.py` (or `src/<app>/tests/` subpackages) and docs under `docs/`.

## Contract

- Inputs: OBCMS codebase, local dev DB (`db.sqlite3`), Django settings in `src/obc_management/settings.py`.
- Outputs: Test artifacts (pytest results, coverage), failing test reports, reproducible test fixtures.
- Error modes: Database state conflicts (do NOT delete `db.sqlite3`), fixture races, HTMX-specific asynchronous UI flakiness.
- Success criteria: Tests pass locally and in CI; coverage >= 85% for critical modules (aim for repo-wide >= 85%); no regressions for critical flows.

## Assumptions

- Use Python 3.12 virtualenv per repo docs (`./scripts/bootstrap_venv.sh && source venv/bin/activate`).
- Django + DRF + pytest + pytest-django are installed (see `requirements/development.txt`).
- Never delete `db.sqlite3` — use migrations / fake migrations when needed.

Priority labels (use in test tracking): PRIORITY: CRITICAL, HIGH, MEDIUM, LOW (no time estimates).

## Scope

### In-scope modules (as identified in repo docs/AGENTS.md)
- `communities`
- `coordination`
- `mana`
- `src/policies`
- `src/documents`
- `policy_tracking`
- `ai_assistant`
- `common` and utilities used across apps
- Templates / HTMX interactions in `templates` and `components`
- Management commands, migrations, and data import scripts in `src` and `scripts`

### Out-of-scope initially
- Production deployment verification (covered by separate deployment tests)
- Third-party integrations requiring production credentials (test stubs/mocks only)

## Test types & strategy

1. Unit tests (PRIORITY: CRITICAL / Complexity: Simple)
   - Goal: fast, isolated tests for models, serializers, utilities, form logic.
   - Tools: pytest, pytest-django, model factories (factory_boy).
   - Location: `src/<app>/tests/test_models.py`, `test_serializers.py`, `test_utils.py`.
   - Mock external network calls and heavy dependencies.

2. Integration tests (PRIORITY: CRITICAL / Complexity: Moderate)
   - Goal: test database interactions, DRF endpoints, Django views (incl. HTMX responses).
   - Tools: pytest-django, Django test client, requests (for small API integration).
   - Test HTMX-specific behaviors: `HX-Request` header responses, OOB swaps, triggers.

3. API contract tests (PRIORITY: HIGH / Complexity: Moderate)
   - Goal: test publicly exposed REST endpoints, expected JSON shapes, auth, permissions.
   - Tools: pytest + DRF APITestCase or APIClient.

4. End-to-end UI tests (PRIORITY: HIGH / Complexity: Complex)
   - Goal: real browser workflows for critical user journeys: login, CRUD flows, HTMX interactions.
   - Tools: Playwright or Cypress (Playwright recommended for multi-browser support).
   - Headless runs in CI; set up fixture users and test data.

5. Performance & load tests (PRIORITY: MEDIUM / Complexity: Complex)
   - Goal: key endpoints (e.g., list APIs, search, data import) under expected loads.
   - Tools: Locust or k6; synthetic scenarios focused on hotspots.

6. Security tests (PRIORITY: HIGH / Complexity: Moderate)
   - Goal: authentication, authorization, CSRF, XSS, clickjacking checks.
   - Tools: automated checks (bandit/OWASP ZAP for scanning), manual review for templates and HTMX endpoints.

7. Migration & data integrity tests (PRIORITY: HIGH / Complexity: Moderate)
   - Goal: run migrations against a copy of `db.sqlite3` using `--fake` options as necessary; test data-import scripts.
   - Important: DO NOT delete `db.sqlite3`. Use `--database` test DB or copy it to `backups/` before changes.

8. Smoke & release tests (PRIORITY: CRITICAL)
   - Goal: basic sanity checks after deployment: server boot, migrations applied, a few key pages render.

## Test data & fixtures

- Use `factory_boy` for factories: `tests/factories/` with factories for Users, Communities, Policies, Documents, Tasks, etc.
- Use separate pytest fixtures for:
  - `admin_user`, `staff_user`, `regular_user`
  - `sample_community`, `sample_policy`, `sample_document`
  - `tx_db` and `client` with different permissions scopes
- Use small seed fixtures in JSON for representative data used by end-to-end tests. Keep them under `tests/fixtures/`.
- For E2E and performance tests, use a dedicated test DB instance (Postgres in CI) rather than the production `db.sqlite3`.

## CI Integration & Commands

### Local dev commands (follow repo docs)
- Create venv and activate:
```bash
./scripts/bootstrap_venv.sh
source venv/bin/activate
pip install -r requirements/development.txt
```
- Run migrations (do not delete `db.sqlite3`):
```bash
./manage.py migrate
```
- Run tests:
```bash
pytest --ds=obc_management.settings
```
- Run a single test module:
```bash
pytest src/communities/tests/test_models.py::test_community_str --ds=obc_management.settings -q
```
- Linting & formatting (pre-commit):
```bash
black src && isort src && flake8 src
pre-commit run --all-files
```
- Coverage:
```bash
coverage run -m pytest --ds=obc_management.settings
coverage report
```

### CI pipeline (GitHub Actions recommended)
Steps:
1. Checkout
2. Setup Python 3.12
3. Cache pip
4. Install dependencies from `requirements/development.txt`
5. Run `./manage.py migrate` against ephemeral Postgres service
6. Run `black --check`, `isort --check`, `flake8`
7. Run `pytest --ds=obc_management.settings --maxfail=1 -q`
8. Upload coverage to reporting (Codecov)
9. On release, run E2E (Playwright) in a separate job

Break builds on lint or test failures.

## Test matrix & priorities (key flows)

- Authentication & authorization (PRIORITY: CRITICAL)
  - Login, logout, password reset, session expiry
  - Role-based page & endpoint access (admin vs staff vs regular)

- Core CRUD flows (PRIORITY: CRITICAL)
  - Communities, Policies, Documents create/read/update/delete
  - HTMX create/edit modals and optimistic updates

- Data import/export (PRIORITY: HIGH)
  - CSV/JSON imports (scripts under `data_imports`), mass imports don't corrupt DB

- Search & filters (PRIORITY: HIGH)
  - Query templates, expansion behavior, pagination

- Templates & UI components (PRIORITY: HIGH)
  - Reuse of `components/form_field_select.html`, correct styles, accessible labels

- Notifications & counters (PRIORITY: MEDIUM)
  - Stat cards and quick action cards reflecting state changes

- Background jobs & scheduled tasks (PRIORITY: MEDIUM)
  - Periodic tasks, data cleanup, cache invalidation

- AI assistant interactions (PRIORITY: HIGH)
  - Input validation, safe fallbacks, rate limiting, sanitized outputs

## Concrete test scenarios (select examples; expand all similar areas similarly)

For each scenario include: title, assumptions, numbered steps, expected results, success/failure criteria.

### Scenario 1: User login happy path
- Assumptions: fresh state, `admin_user` fixture exists
- Steps:
  1. Open login page (`/accounts/login/`).
  2. Enter valid username & password.
  3. Submit form.
- Expected:
  - Redirect to dashboard (HTTP 302 -> `/` or configured landing).
  - Session cookie set and `request.user.is_authenticated` true.
- Success criteria: user lands on dashboard and page shows user-specific content.

### Scenario 2: Unauthorized access to admin endpoint
- Assumptions: `regular_user` logged in
- Steps:
  1. Login as `regular_user`.
  2. Request admin-only page `/admin-only/` or API endpoint.
- Expected:
  - HTTP 403 or redirect to forbidden page.
- Failure: access granted.

### Scenario 3: Create Community (HTMX modal)
- Assumptions: `staff_user` with permission
- Steps:
  1. Navigate to communities list.
  2. Click "New Community" (HTMX opens modal).
  3. Fill required fields and click Save.
- Expected:
  - HTMX returns fragment with new row (outerHTML swap).
  - List updates with new community entry (no full page reload).
  - Server returns `HX-Trigger` to show toast.
- Edge cases:
  - Submit with missing required field -> modal shows field error.
  - Concurrent save (double-click) -> no duplicate entries (idempotency).

### Scenario 4: API CRUD for Policy (DRF)
- Assumptions: API token for staff user
- Steps:
  1. POST `/api/policies/` with valid JSON.
  2. Expect HTTP 201 with JSON including `id` and fields.
  3. GET `/api/policies/<id>/` returns same data.
  4. PATCH to update -> HTTP 200 and updated fields.
  5. DELETE -> HTTP 204 and resource removed.
- Edge cases:
  - Invalid payload -> HTTP 400 with field errors.
  - Unauthorized token -> HTTP 401.

### Scenario 5: Data-import script robustness
- Assumptions: sample CSV with malformed lines
- Steps:
  1. Run `python scripts/import_policy_csv.py tests/fixtures/imports/policies_malformed.csv`.
- Expected:
  - Script logs errors for malformed lines but continues processing valid ones.
  - Atomicity rules respected where necessary (transactional per-row or per-file as design).
- Failure: script crashes and stops without processing valid items.

### Scenario 6: E2E critical user flow (Create Policy -> Assign to Community -> Notify)
- Assumptions: Clean seeded DB with test users
- Steps:
  1. Login as staff user in browser.
  2. Navigate to Policies page -> Create Policy with modal.
  3. Assign the policy to an existing community from dropdown.
  4. Save and assert notification appears and counters increase.
- Expected:
  - All UI updates are reflected.
  - Backend shows assignment in DB.

### Scenario 7: Migration safety and data integrity
- Assumptions: current `db.sqlite3` present; migration script prepared
- Steps:
  1. Create a copy of `db.sqlite3` to `backups/`.
  2. Run `./manage.py migrate --database=default`.
  3. Run data integrity checks (counts of key tables).
- Expected:
  - Migrations apply successfully (or yield actionable errors).
  - No loss of data in the backup copy.

## Edge cases & negative tests (examples)

- Empty inputs and zero-length strings
- Extremely long input (max length violations)
- Concurrent edits (race conditions in optimistic update flows)
- Broken HTMX requests (missing HX headers)
- CSRF absent or invalid token
- GRACEFUL handling of external service timeouts (AI assistant, external APIs)
- Permission escalation attempts

## Test authorship & naming conventions

- Tests must be named `test_<behavior>.py` and functions as `test_<expected_behavior>`.
- Keep tests small and single-assertion where sensible (or using several asserts that relate to the single behavior).
- Place unit tests next to the module when small, or under `src/<app>/tests/` for larger suites.
- Use factory fixtures located at `src/<app>/tests/factories.py` or central `factories.py`.

## Quality gates (local checklist)

Before merging:
- Build: `./manage.py check` (Django checks)
- Lint/Format: `black src && isort src && flake8 src`
- Unit tests: `pytest -k "not e2e" --ds=obc_management.settings`
- Integration tests: `pytest tests/integration --ds=obc_management.settings`
- E2E: Playwright tests run in a separate job after server is deployed for tests

> Note: I cannot run these steps from here; run them locally or in CI.

## Recommended toolchain & automation

- Pytest + pytest-django + factory_boy + pytest-cov
- Playwright for E2E (headless + CI)
- Locust or k6 for performance
- Bandit/OWASP ZAP for security scanning
- pre-commit hooks: black, isort, flake8

## Example test templates

Unit test (pytest) template:
```python
# src/communities/tests/test_models.py
import pytest
from src.communities.models import Community
from src.communities.tests.factories import CommunityFactory

@pytest.mark.django_db
def test_community_str():
    c = CommunityFactory(name="Barangay Test")
    assert str(c) == "Barangay Test"
```

Integration test (DRF) template:
```python
# src/policies/tests/test_api.py
import pytest
from rest_framework.test import APIClient
from src.policies.tests.factories import PolicyFactory
from src.common.tests.factories import StaffUserFactory

@pytest.mark.django_db
def test_create_policy_api():
    client = APIClient()
    user = StaffUserFactory()
    client.force_authenticate(user=user)
    payload = {"title": "Test Policy", "content": "Test content"}
    r = client.post("/api/policies/", payload, format="json")
    assert r.status_code == 201
    assert r.json()["title"] == "Test Policy"
```

E2E (Playwright) minimal test example (saved under `tests/e2e`):
```javascript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  await page.goto('http://localhost:8000/accounts/login/');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/dashboard/);
});
```

## Reporting & Metrics

- Required: a coverage badge (Codecov or Coveralls).
- Add test-results artifacts for failing runs in CI.
- Track test flakiness, failing patterns; quarantine flaky tests with `@pytest.mark.flaky` and local investigation.

## Test ownership & roadmap (no dates)

- PRIORITY: CRITICAL — Authentication, Authorization, Core CRUD, HTMX flows, API contracts.
  - Owners: teams responsible for each app module.
- PRIORITY: HIGH — Data import, AI assistant integrations, Templates & accessibility.
- PRIORITY: MEDIUM — Performance tests, background jobs.
- PRIORITY: LOW — Cosmetic UI tests only (visual) and extended cross-browser sweep.

## Deliverables (files to add)

Save under `docs/` and `src/` as appropriate:
- `docs/testing/obcms_test_plan.md` (this document)
- `src/<app>/tests/` test packages and `tests/factories.py`
- `tests/e2e/` Playwright tests and `playwright.config.ts`
- `ci/github/workflows/ci.yml` (CI pipeline)
- `requirements/test.txt` (if separating test deps)

## Try it locally — exact commands

```bash
# create venv and install dev deps (macOS, zsh)
./scripts/bootstrap_venv.sh
source venv/bin/activate
pip install -r requirements/development.txt

# run Django migrations (do not delete db.sqlite3)
./manage.py migrate

# run the full pytest suite
pytest --ds=obc_management.settings

# run unit tests only (fast)
pytest -k "unit or models or utils" --ds=obc_management.settings

# run e2e (after starting dev server)
# in one terminal:
./manage.py runserver
# in another:
npx playwright test
```

## Next steps I can do for you

- Scaffold test directories and 5–10 example tests (unit + integration + one E2E), including factories and fixtures.
- Generate a GitHub Actions `ci.yml` for automated runs.
- Add Playwright config and one recorded E2E flow.
- Add a small `tests/README.md` explaining how to run and add tests.

## Requirements coverage

- Plan a full test suite for OBCMS: Done (document above)
- Place plan into docs: Provided as content to save at `docs/testing/obcms_test_plan.md` — action: save file locally (commands above).
- Follow repo guidelines (db protection & docs placement): Observed (notes in plan include DO NOT DELETE `db.sqlite3` and docs location).

## Quality gates triage (local/CI checks — run locally/CI)
- Build: check -> command provided
- Lint/Typecheck: commands provided
- Unit tests: command provided
- Integration/E2E: commands & guidance provided