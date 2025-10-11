# OBCMS End-to-End Testing Plan

## Purpose
- Validate OBCMS’s critical user journeys through the entire stack—browser UI, HTMX interactions, Django backend, Celery tasks, and persistence layers—using automated browser testing.
- Align tooling and practices with modern E2E frameworks such as Playwright (per Playwright docs: cross-browser support, auto-waiting, built-in test runner) and Cypress (per Cypress guides: interactive runner, network control, CI integration).
- Provide engineering and QA teams with structured guidance emphasizing priority, complexity, dependencies, and prerequisites instead of timelines.

## Tooling Strategy
- **Primary Framework:** Playwright Test (Node.js) for cross-browser coverage (Chromium, WebKit, Firefox), automatic waits, trace viewer, and GitHub Actions workflow scaffolding.
- **Secondary Option:** Cypress for interactive debugging or when component/E2E hybrid testing is beneficial; maintain parity in test cases if both tools are used.
- **Support Utilities:**
  - Playwright fixtures for authentication contexts (`storageState`), tracing (`--trace on`), and video artifacts.
  - Custom helpers for HTMX assertions (checking `hx-trigger`, `hx-swap` behavior post-interaction).
  - ENV-driven base URLs and credentials via `.env.e2e`.

## Environment Requirements
- Dedicated E2E environment mirroring production feature flags, seeded with deterministic sample data (communities, policies, coordination tasks).
- Stable URLs: `E2E_BASE_URL` pointing to staging or ephemeral preview deployments spun up via CI.
- Test accounts per persona: OOBC admin, provincial coordinator, municipal officer, and AI assistant operator. Credentials managed via secrets store.
- Background services (Celery, Redis, email backend) in running state; configure SMTP to use mailhog/test capture.

## Module & Workflow Coverage
- **communities** — PRIORITY: CRITICAL | COMPLEXITY: Complex | Ensure directory listings, profiling flows, and HTMX filters behave end-to-end.
- **coordination** — PRIORITY: CRITICAL | COMPLEXITY: Complex | Validate kanban task lifecycle, notifications, and optimistic UI updates.
- **mana** — PRIORITY: HIGH | COMPLEXITY: Complex | Cover facilitator scheduling, participant intake, and workshop recording workflows.
- **policies** — PRIORITY: HIGH | COMPLEXITY: Moderate | Exercise policy creation, review/approval steps, and publication banners.
- **policy_tracking** — PRIORITY: HIGH | COMPLEXITY: Moderate | Confirm dashboards, timelines, and alerts display aggregated data accurately.
- **documents** — PRIORITY: HIGH | COMPLEXITY: Complex | Test uploads, metadata extraction, previews, and retention/deletion flows.
- **project_central (M&E / Project Management)** — PRIORITY: CRITICAL | COMPLEXITY: Complex | Cover PPA creation, indicator tracking, budget monitoring, and reporting dashboards.
- **recommendations** — PRIORITY: HIGH | COMPLEXITY: Moderate | Validate drafting, categorizing, and approving policy recommendations with stakeholder assignments.
- **ai_assistant** — PRIORITY: MEDIUM | COMPLEXITY: Complex | Validate conversational UI, response rendering, and audit logging.
- **monitoring (OOBC management)** — PRIORITY: CRITICAL | COMPLEXITY: Complex | Validate WorkItem lifecycle, calendar synchronization, escalation rules, and monitoring dashboards.
- **common (shared navigation, staff management, notifications, RBAC)** — PRIORITY: CRITICAL | COMPLEXITY: Moderate | Assert global navigation, staff team management, leave approvals, breadcrumbs, flash messages, and permission guards across personas.
- **data_imports (admin workflows)** — PRIORITY: MEDIUM | COMPLEXITY: Complex | Verify admin-triggered imports, validation feedback, and post-import reconciliation when surfaced via UI.
- **common dashboards & analytics** — PRIORITY: HIGH | COMPLEXITY: Complex | Ensure executive dashboards (budget feedback, trend analysis, analytics suite) reflect live data and cross-module metrics.
- For any new app/module, add corresponding E2E flows during onboarding and update this section to reflect required coverage.

## Test Scenarios

### Authentication & Session Management
- **Priority:** CRITICAL; **Complexity:** Moderate; **Dependencies:** Login views, MFA toggles, session storage.
- **Prerequisites:** Seeded user credentials, bypass tokens for captcha/MFA if active.
- **Coverage:** Login, logout, password reset, session timeout handling, multi-role switch (if applicable). Verify security headers and landing redirects.

### Community Directory Management
- **Priority:** CRITICAL; **Complexity:** Complex; **Dependencies:** Communities app views, HTMX filters, forms.
- **Prerequisites:** Seeded region/province data, file uploads disabled or routed to temp storage.
- **Coverage:** Search/filter communities, create/edit forms with validation, attach documents, confirm HTMX partial updates and success toasts.

### Coordination Task Workflow
- **Priority:** CRITICAL; **Complexity:** Complex; **Dependencies:** Coordination app, notifications, Celery tasks.
- **Prerequisites:** Task templates, worker queue ready, notification capture fixtures.
- **Coverage:** Create tasks, assign to staff, change status via kanban actions, ensure background notifications fired (inspect mock inbox/logs), verify optimistic UI updates.

### OOBC Staff Management & Calendar Operations
- **Priority:** CRITICAL; **Complexity:** Complex; **Dependencies:** Staff team management (common), monitoring WorkItem services, calendar endpoints, notifications.
- **Prerequisites:** Staff accounts across roles, seeded WorkItems linked to PPAs/tasks, calendar feature flags enabled, mocked email/SMS gateways.
- **Coverage:** Create and edit staff profiles/teams, approve leave requests, assign WorkItems to staff, validate that calendar views render assignments with correct metadata and that changes propagate to WorkItem dashboards and alerts.

### Policy Tracking & Reporting
- **Priority:** HIGH; **Complexity:** Moderate; **Dependencies:** Policy tracking dashboards, aggregation APIs.
- **Prerequisites:** Historical policy data seeded, cache warmed or cleared per test.
- **Coverage:** View dashboards with correct metrics, drill into policy detail, export reports (CSV/PDF) and validate file download metadata.

### M&E Program & Indicator Management (Project Central)
- **Priority:** CRITICAL; **Complexity:** Complex; **Dependencies:** PPA models, indicator services, budget tracking, reporting views.
- **Prerequisites:** Seeded PPAs, funding sources, indicator templates, mocked analytics hooks.
- **Coverage:** Create/update PPAs, configure indicators and targets, record measurements, review dashboards (heatmaps, outcome charts), generate M&E reports, confirm Celery-driven analytics (if enabled) log success states.

### Policy Authoring & Approval (Policies App)
- **Priority:** HIGH; **Complexity:** Moderate; **Dependencies:** Policy authoring forms, approval workflows, notification hooks.
- **Prerequisites:** Reviewer and approver accounts, sample policy templates.
- **Coverage:** Draft new policy, route for approval, approve/reject with comments, ensure publication status propagates to listings and downstream dashboards.

### Policy Recommendation Workflow
- **Priority:** HIGH; **Complexity:** Moderate; **Dependencies:** Recommendations module views, categorization services, stakeholder assignments.
- **Prerequisites:** Seeded recommendation types, stakeholder directory, notification integration.
- **Coverage:** Create recommendation drafts, classify by domain, assign responsible offices, capture approval decisions, and verify visibility on management dashboards and exports.

### Document Management Pipeline
- **Priority:** HIGH; **Complexity:** Complex; **Dependencies:** Document uploads, virus scanning hooks, metadata processing.
- **Prerequisites:** Temporary storage bucket, test documents (PDF, images) with varying sizes.
- **Coverage:** Upload documents, observe progress indicators, validate metadata display, test deletion with confirmation banners.

### MANA Workshop Facilitation
- **Priority:** HIGH; **Complexity:** Complex; **Dependencies:** MANA module views, participant forms, scoring logic.
- **Prerequisites:** Facilitator and participant accounts, seeded workshop templates, mock SMS/email integrations for notifications.
- **Coverage:** Schedule workshop, enroll participants, record assessments, generate facilitator summary, verify success banners and audit entries.

### AI Assistant Interaction
- **Priority:** MEDIUM; **Complexity:** Complex; **Dependencies:** ai_assistant UI, backend inference stubs.
- **Prerequisites:** Mock AI responses via feature flag or stubbed API to keep tests deterministic.
- **Coverage:** Initiate conversation, submit query, render formatted answer, handle error fallback, verify audit log entries.

### Cross-Module Regression Suite
- **Priority:** MEDIUM; **Complexity:** Complex; **Dependencies:** Multi-app workflows (community → coordination → policy tracking).
- **Prerequisites:** Combined data fixture aligning identifiers across apps.
- **Coverage:** End-user journey from discovering a community need to logging a coordination task, initiating relevant MANA interventions, linking to PPA records in Project Central, and monitoring policy response, ensuring data consistency at each step.

### Executive Dashboards & Analytics
- **Priority:** HIGH; **Complexity:** Complex; **Dependencies:** Common analytics dashboards (trend analysis, budget feedback, staff performance), aggregated services, caching layer.
- **Prerequisites:** Seeded KPIs, alerts, and historical records; cache backends primed for testing.
- **Coverage:** Load each executive dashboard, verify metrics align with source data, test filter combinations, ensure charts render, and confirm updates after upstream mutations (e.g., new WorkItems changing KPIs).

### Data Import Administration
- **Priority:** MEDIUM; **Complexity:** Complex; **Dependencies:** Admin UI for data imports, validation services, audit logs.
- **Prerequisites:** Sample import files (CSV/JSON), mocked external storage if required.
- **Coverage:** Trigger import, monitor progress indicators, review validation errors, confirm successful records appear in target modules (communities, policies) and audit trail captures the event.

### Planning, Budgeting, and Attendance Operations
- **Priority:** MEDIUM; **Complexity:** Complex; **Dependencies:** OOB management planning/budgeting views, attendance QR workflows, staff training modules.
- **Prerequisites:** Budget scenarios, attendance rosters, QR codes, and training catalog fixtures.
- **Coverage:** Execute budget planning flow (create scenario, adjust allocations, generate feedback), perform attendance check-in/out via QR interface, review training assignments, and ensure outcomes surface on relevant dashboards and staff profiles.

## Test Data & State Management
- Use Playwright’s global setup to import `storageState` for authenticated sessions; refresh tokens between tests when testing login flows.
- Reset database via management command (`./manage.py e2e_reset`) or fixture load prior to each suite run.
- For destructive flows (deletions), operate on test-specific records to avoid cross-test contamination.

## HTMX Contract Validation
- Record expected `HX-Trigger`, `HX-Redirect`, and `HX-Refresh` headers for each interaction; assert against them in Playwright to guarantee client/server contract stability.
- Leverage Playwright event listeners to capture `htmx:beforeSwap`, `htmx:afterSwap`, and `htmx:responseError` occurrences, surfacing mismatches between optimistic UI updates and server acknowledgements.
- Maintain a shared catalog of HTMX target IDs and `data-task-id` attributes to keep selectors aligned with the UI Components & Standards guide and prevent regressions during refactors.

## Observability & Artifacts
- Enable Playwright tracing (`npx playwright test --trace on`) for all CI runs; store trace zips and videos under `reports/e2e/`.
- Capture screenshots on failure (`--reporter=line,list,json`) and publish JSON reports for downstream analytics.
- Log browser console output and network errors to catch silent failures.

## CI/CD Integration
- Configure GitHub Actions workflow `ci/e2e.yml`:
  1. Build frontend assets (if needed) and run Django server via `./manage.py runserver 0.0.0.0:8000` behind `playwright test --web-server`.
  2. Execute Playwright tests across configured projects (Chromium headless minimal, optional WebKit nightly).
  3. Upload trace, video, screenshot artifacts.
- Run smoke subset on every pull request (login + critical path), full suite nightly or before releases.
- Allow manual retrigger with environment overrides for testing hotfixes.

## Maintenance Practices
- Keep selectors resilient: use data-testid attributes in templates/components to reduce coupling to CSS changes.
- Review failing traces regularly; update fixtures when domain models evolve.
- Pair new features with matching E2E scenarios; ensure test plans stay updated in `docs/plans/tests/`.
- Decommission brittle flows by migrating them to targeted integration tests when UI coverage is redundant.
- Maintain parity between Playwright helpers and Django HTMX behaviours; update custom assertions when headers or
  response contracts change to avoid false negatives.
- Add smoke assertions that verify essential middleware (CSRF, session, locale) is wired correctly before longer
  journeys execute to surface configuration regressions early.

## Risk Mitigation & Quality Gates
- **Priority:** HIGH | **Complexity:** Moderate | **Dependencies:** Stable staging data snapshots and reliable login
  fixtures.
- **Failure Budget:** Limit flaky test retries to two consecutive reruns; auto-open an issue when exceeded to trigger
  investigation.
- **Regression Containment:** Require green Playwright smoke suite before merging to `main`; block deployments when
  smoke suite or data reset command fails.
- **Data Integrity:** Validate that destructive actions (delete/archive) run against disposable fixtures by checking
  data identifiers before performing cleanup. Abort scenarios if guard rails detect production-like IDs.
- **Accessibility Checks:** Integrate axe-core scans on the top 5 user journeys (login, community directory, task
  board, PPA dashboard, analytics home) and treat violations as blockers until resolved or triaged with mitigation
  notes.

## Next Actions
- **Priority:** HIGH — Scaffold Playwright project (`npm init playwright@latest`) with configuration stored under `tests/e2e/playwright.config.ts`.
- **Priority:** HIGH — Implement global fixtures for authentication, HTMX validation helpers, and artifact handling.
- **Priority:** MEDIUM — Set up CI workflow and seed management command to reset E2E data before runs.
- **Priority:** MEDIUM — Create smoke suite covering authentication, community creation, and coordination task assignment as baseline coverage.
