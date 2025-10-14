# Phase -1 Reconciliation Implementation Report

**Date:** 2025-10-14  
**Prepared by:** Codex (GPT-5)

## Scope
- Corrected `OrganizationContextMiddleware` import path and made the middleware mode-aware for OBCMS and BMMS.
- Introduced central BMMS mode configuration (`bmms_config.py`) and exposed `BMMS_MODE`/`DEFAULT_ORGANIZATION_CODE` in settings.
- Updated RBAC configuration defaults to follow the active mode and standardised the OCM organization code to `OCM`.
- Added `organizations.utils.get_or_create_default_organization()` to supply the default OOBC organization when running in OBCMS mode.
- Created `.env.obcms` to document the single-tenant baseline configuration.

## Key Decisions
- **Middleware Strategy:** Option A (refactor existing middleware) retained a single middleware responsible for `request.organization`, avoiding conflicts with planned middleware.
- **Mode Defaults:** `ENABLE_MULTI_TENANT` and `ALLOW_ORGANIZATION_SWITCHING` now derive their defaults from the configured BMMS mode, preventing accidental multi-tenant behaviour in OBCMS.

## Implementation Highlights
- `src/common/middleware/organization_context.py`
  - Imports BMMS mode helpers and default-organization utility.
  - Auto-injects the OOBC organization whenever `BMMS_MODE=obcms`, caches the result per request, and preserves existing BMMS logic.
  - Updated class docstring to emphasise single-middleware ownership of organization context.
- `src/obc_management/settings/bmms_config.py`
  - New helper module supplying `BMMSMode`, mode predicates, and convenience accessors for defaults.
- `src/obc_management/settings/base.py`
  - Imports `BMMSMode`, defines `BMMS_MODE` and `DEFAULT_ORGANIZATION_CODE`, and aligns RBAC defaults with the active mode.
- `src/organizations/utils.py`
  - Provides `get_or_create_default_organization()` with safe defaults for OOBC metadata.
- `.env.obcms`
  - Documents the canonical single-tenant environment variables for local setup.

## Verification
- `../venv/bin/python manage.py check` ✅ – Django system check passed with no issues.
- `../venv/bin/python manage.py test --keepdb` ⚠️ – Fails before execution: `ImportError` for `tests` package under `budget_preparation`. Existing path collision (duplicate `tests` directory) predates current work; manual intervention required to normalise package layout before the full suite can run.
- Mode helper validation:
  - `is_obcms_mode()` → `True`, `multi_tenant_enabled()` → `False`, `organization_switching_enabled()` → `False` with default settings.
  - With `BMMS_MODE=bmms`, helpers flip to `True` and middleware returns `None` for unauthenticated requests as expected.
- Middleware sanity check (OBCMS): `get_organization_from_request()` returns the OOBC organization for anonymous requests, confirming default injection.

## Remaining Risks / Follow-ups
- Resolve the `budget_preparation/tests` import collision so the full Django test suite can execute (`ImportError: 'tests' module incorrectly imported ...`). No new test failures were observed because the suite did not execute.
- Consider seeding `.env.obcms` secrets (e.g., `SECRET_KEY`) with environment-specific values before deploying or sharing.

## Ready for Phase 0
- ✅ All Phase -1 code fixes implemented.
- ✅ Mode helpers and middleware validated in both modes.
- ✅ Configuration documented.
- ⚠️ Test suite blocked by pre-existing module import issue; highlight for resolution prior to Phase 0 sign-off.
