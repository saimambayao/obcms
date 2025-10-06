# Staging Rehearsal Checklist

**Status:** Adopted
**Last Updated:** 2025-10-02
**Owner:** OOBC Development Team

This checklist is executed before every production deployment to ensure the
staging environment faithfully mirrors production conditions and that critical
paths remain healthy.

## 1. Environment & Data Snapshot
- [ ] Snapshot current production database.
- [ ] Restore snapshot to staging (do **not** reset user credentials).
- [ ] Sync `.env.staging` secrets with latest queue/API credentials.
- [ ] Verify Redis, Celery workers, and beat processes are online.

## 2. Migration Dry Run
- [ ] Run `python manage.py showmigrations --plan` and review output.
- [ ] Apply migrations: `python manage.py migrate`.
- [ ] Confirm no pending migrations remain.

## 3. Smoke Tests (via pytest markers)
- [ ] `pytest -m smoke --ds=obc_management.settings` (core routes, APIs).
- [ ] `pytest src/project_central/tests/test_views.py::MyTasksWithProjectsViewTests` (HTMX dashboard).
- [ ] `pytest src/common/tests/test_task_automation.py` (template automation).
- [ ] `pytest src/common/tests/test_tasks_notifications.py` (Celery notification batching).

## 4. Functional Checks
- [ ] Create/refresh Project Management Portal workflow and verify tasks render with filters.
- [ ] Trigger `generate_workflow_tasks` and confirm no duplicate tasks on re-run.
- [ ] Create a StaffTask with resource booking spec and confirm booking appears.
- [ ] Run `send_calendar_notifications_batch.delay()` and confirm pending notifications change status.

## 5. Performance Baseline
- [ ] Execute `pytest src/tests/test_calendar_performance.py -k calendar_aggregation` to capture timings.
- [ ] Record query count and response time changes from previous rehearsal.
- [ ] Document any regressions in `docs/testing/TEST_RESULTS_REPORT.md`.

## 6. Observability & Logs
- [ ] Tail Celery worker logs during test runs.
- [ ] Review Django request logs for errors while exercising dashboards.
- [ ] Ensure monitoring alerts (Grafana/Prometheus if enabled) show healthy status.

## 7. Sign-off
- [ ] Update `docs/testing/TEST_RESULTS_REPORT.md` with outcomes.
- [ ] Notify deployment owners that staging is green.
- [ ] Attach this checklist to the release ticket.
