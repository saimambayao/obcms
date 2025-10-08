# OBCMS Directory Structure Reorganization Plan

**Date**: 2025-10-08
**Status**: Planning
**Priority**: HIGH - Code quality and maintainability

## Executive Summary

This document outlines the plan to reorganize the OBCMS directory structure to align with Django best practices as of 2024-2025. The current structure has several issues including duplicate directories, misplaced files, and incorrect BASE_DIR configuration.

## Current Issues Identified

### 1. CRITICAL: Incorrect BASE_DIR Configuration

**Problem**: `BASE_DIR` in `settings/base.py` points to `src/obc_management/` instead of `src/`

```python
# Current (WRONG)
BASE_DIR = Path(__file__).resolve().parent.parent  # = src/obc_management/

# This causes:
# - STATIC_ROOT = src/obc_management/staticfiles (WRONG)
# - MEDIA_ROOT = src/obc_management/media (WRONG)
# - LOG files in src/obc_management/logs/ (WRONG)
```

**Impact**:
- Duplicate directory structures
- Confusion about where files should be stored
- Non-standard Django project layout

### 2. Test Files in src/ Root (CRITICAL)

**Files to relocate**:
```
src/test_ai_chat_queries.py → src/tests/ai_assistant/test_chat_queries.py
src/test_ai_chat_quick.py → src/tests/ai_assistant/test_chat_quick.py
src/test_chat_municipality.py → src/tests/ai_assistant/test_chat_municipality.py
src/test_cotabato_query.py → src/tests/ai_assistant/test_cotabato_query.py
src/test_e2e_chat.py → src/tests/ai_assistant/test_e2e_chat.py
src/test_municipalities_cities_final.py → src/tests/communities/test_municipalities_cities_final.py
src/test_municipality_fix.py → src/tests/communities/test_municipality_fix.py
src/test_performance_chat.py → src/tests/performance/test_performance_chat.py
src/test_project_activity_integration.py → src/tests/project_central/test_project_activity_integration.py
```

**Django Best Practice**: Test files should be in `tests/` directory or within each app's `tests/` subdirectory.

### 3. Utility Scripts in src/ Root

**Files to relocate**:
```
src/export_sqlite_data.py → src/scripts/export_sqlite_data.py
src/performance_analysis.py → src/scripts/performance_analysis.py
src/verify_legacy_cleanup.py → src/scripts/verify_legacy_cleanup.py
src/update_faq_and_test.py → src/scripts/update_faq_and_test.py
```

**Best Practice**: Standalone scripts should be in `scripts/` directory or converted to Django management commands.

### 4. Duplicate Settings File

**File to remove**:
```
src/obc_management/settings/base 2.py (duplicate backup file)
```

### 5. Incorrect Directory Locations

**Directories to clean up**:
```
src/obc_management/ai_assistant/ → DELETE (empty vector_indices directory only)
src/obc_management/static/ → DELETE or verify empty
src/obc_management/staticfiles/ → DELETE or verify empty
src/obc_management/logs/ → Files will be moved when BASE_DIR is fixed
src/obc_management/media/ → Files will be moved when BASE_DIR is fixed
```

**Note**: `src/ai_assistant/` is the correct location for the AI assistant app.

### 6. Documentation Location

**Current**: `src/docs/` (inside Django src directory)
**Should be**: `docs/` (at project root level)

However, checking CLAUDE.md, it appears docs/ is already at the project root. The `src/docs/` directory appears to be app-specific documentation.

## Reorganization Plan

### Phase 1: Fix BASE_DIR Configuration (CRITICAL)

**Steps**:

1. Update `src/obc_management/settings/base.py`:
   ```python
   # Change from:
   BASE_DIR = Path(__file__).resolve().parent.parent

   # To:
   BASE_DIR = Path(__file__).resolve().parent.parent.parent
   ```

2. Verify all path configurations:
   ```python
   STATIC_ROOT = BASE_DIR / "staticfiles"  # src/staticfiles ✓
   STATICFILES_DIRS = [BASE_DIR / "static"]  # src/static ✓
   MEDIA_ROOT = BASE_DIR / "media"  # src/media ✓
   ```

3. Update LOGGING configuration:
   ```python
   "filename": BASE_DIR / "logs" / "django.log"  # src/logs/django.log ✓
   ```

**Impact**: This will automatically fix the directory structure issues.

### Phase 2: Reorganize Test Files

**Steps**:

1. Create test directory structure:
   ```bash
   mkdir -p src/tests/ai_assistant
   mkdir -p src/tests/communities
   mkdir -p src/tests/performance
   mkdir -p src/tests/project_central
   ```

2. Move test files with git mv (preserves history):
   ```bash
   git mv src/test_ai_chat_queries.py src/tests/ai_assistant/test_chat_queries.py
   git mv src/test_ai_chat_quick.py src/tests/ai_assistant/test_chat_quick.py
   git mv src/test_chat_municipality.py src/tests/ai_assistant/test_chat_municipality.py
   git mv src/test_cotabato_query.py src/tests/ai_assistant/test_cotabato_query.py
   git mv src/test_e2e_chat.py src/tests/ai_assistant/test_e2e_chat.py
   git mv src/test_municipalities_cities_final.py src/tests/communities/test_municipalities_cities_final.py
   git mv src/test_municipality_fix.py src/tests/communities/test_municipality_fix.py
   git mv src/test_performance_chat.py src/tests/performance/test_performance_chat.py
   git mv src/test_project_activity_integration.py src/tests/project_central/test_project_activity_integration.py
   ```

3. Create `__init__.py` files in test directories:
   ```bash
   touch src/tests/__init__.py
   touch src/tests/ai_assistant/__init__.py
   touch src/tests/communities/__init__.py
   touch src/tests/performance/__init__.py
   touch src/tests/project_central/__init__.py
   ```

4. Update imports in moved test files if necessary.

### Phase 3: Reorganize Utility Scripts

**Steps**:

1. Ensure scripts directory exists:
   ```bash
   mkdir -p src/scripts
   ```

2. Move utility scripts:
   ```bash
   git mv src/export_sqlite_data.py src/scripts/export_sqlite_data.py
   git mv src/performance_analysis.py src/scripts/performance_analysis.py
   git mv src/verify_legacy_cleanup.py src/scripts/verify_legacy_cleanup.py
   git mv src/update_faq_and_test.py src/scripts/update_faq_and_test.py
   ```

3. Add README to scripts directory explaining their purpose.

### Phase 4: Clean Up Duplicate/Incorrect Directories

**Steps**:

1. Remove duplicate settings file:
   ```bash
   rm src/obc_management/settings/"base 2.py"
   ```

2. Remove empty/incorrect directories in obc_management:
   ```bash
   rm -rf src/obc_management/ai_assistant/  # Only contains empty vector_indices
   ```

3. Verify and clean up if empty (do NOT delete if contains files):
   ```bash
   # Check first, then delete only if empty
   ls -la src/obc_management/static/
   ls -la src/obc_management/staticfiles/
   ```

4. After BASE_DIR fix, verify files have moved from obc_management/logs and obc_management/media to root level:
   ```bash
   # Files should be in:
   src/logs/django.log
   src/media/documents/
   ```

### Phase 5: Update Configuration Files

**Files to update**:

1. `.gitignore` - Ensure correct paths are ignored:
   ```
   # Media files
   /src/media/

   # Static files (collected)
   /src/staticfiles/

   # Logs
   /src/logs/*.log

   # Python cache
   __pycache__/
   *.pyc

   # Tests
   .pytest_cache/
   .coverage
   htmlcov/
   ```

2. `pytest.ini` or `pyproject.toml` - Update test discovery paths if needed.

3. `scripts/bootstrap_venv.sh` - Verify it doesn't reference old paths.

## Testing Strategy

### After Each Phase:

1. **Run Django check**:
   ```bash
   cd src
   ./manage.py check
   ./manage.py check --deploy
   ```

2. **Run migrations** (dry run first):
   ```bash
   ./manage.py migrate --plan
   ./manage.py migrate
   ```

3. **Collect static files**:
   ```bash
   ./manage.py collectstatic --noinput
   ```

4. **Run test suite**:
   ```bash
   pytest -v
   ```

5. **Start development server**:
   ```bash
   ./manage.py runserver
   ```

6. **Manual verification**:
   - Access admin panel
   - Upload a file (test media handling)
   - Check logs are being written
   - Verify static files are served correctly

### Full System Test After All Phases:

```bash
# Full test suite
cd src
pytest -v --cov=. --cov-report=html

# Code quality checks
black --check .
isort --check .
flake8

# Django checks
./manage.py check --deploy
./manage.py validate_templates  # If custom command exists

# Performance tests
pytest tests/performance/ -v
```

## Rollback Plan

If issues are encountered:

1. **Git rollback**: All changes use `git mv` to preserve history
   ```bash
   git checkout -- .
   git clean -fd
   ```

2. **Settings rollback**: Keep backup of base.py
   ```bash
   cp src/obc_management/settings/base.py src/obc_management/settings/base.py.backup
   ```

3. **Database backup**: Ensure db.sqlite3 backup exists before testing
   ```bash
   cp src/db.sqlite3 src/db.sqlite3.backup
   ```

## Expected Directory Structure After Reorganization

```
obcms/                          # Project root
├── .env                        # Environment variables
├── .gitignore
├── README.md
├── CLAUDE.md                   # AI configuration
├── package.json                # Node.js dependencies
├── requirements/
│   ├── base.txt
│   └── development.txt
├── docs/                       # Documentation (at root level ✓)
│   ├── README.md
│   ├── deployment/
│   ├── development/
│   └── improvements/
├── scripts/                    # Project-level scripts
│   └── bootstrap_venv.sh
└── src/                        # Django project source
    ├── manage.py
    ├── db.sqlite3
    ├── pytest.ini
    ├── .pytest_cache/
    ├── obc_management/         # Main Django project config
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── celery.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── settings/
    │       ├── __init__.py
    │       ├── base.py         # Fixed BASE_DIR ✓
    │       ├── development.py
    │       ├── production.py
    │       └── staging.py
    ├── static/                 # Global static files
    │   ├── admin/
    │   ├── common/
    │   ├── css/
    │   └── vendor/
    ├── staticfiles/            # Collected static files (gitignored)
    ├── media/                  # User uploads (gitignored)
    │   └── documents/
    ├── logs/                   # Application logs (gitignored)
    │   └── django.log
    ├── templates/              # Global templates
    │   ├── admin/
    │   ├── common/
    │   └── components/
    ├── tests/                  # Centralized tests ✓
    │   ├── __init__.py
    │   ├── ai_assistant/
    │   ├── communities/
    │   ├── performance/
    │   └── project_central/
    ├── scripts/                # Utility scripts ✓
    │   ├── export_sqlite_data.py
    │   ├── performance_analysis.py
    │   └── verify_legacy_cleanup.py
    ├── common/                 # Django apps below
    ├── communities/
    ├── coordination/
    ├── mana/
    ├── monitoring/
    ├── recommendations/
    ├── project_central/
    ├── ai_assistant/
    ├── data_imports/
    ├── municipal_profiles/
    └── services/
```

## Success Criteria

✅ All tests pass after reorganization
✅ Django check --deploy shows no errors
✅ Development server runs without errors
✅ Static files served correctly
✅ Media uploads work correctly
✅ Logs written to correct location
✅ No duplicate directories
✅ No test files in src/ root
✅ No utility scripts in src/ root
✅ BASE_DIR correctly points to src/
✅ Documentation updated

## Post-Reorganization Tasks

1. Update CLAUDE.md with any new directory structure notes
2. Update docs/development/README.md
3. Update deployment documentation
4. Create migration guide for other developers
5. Update CI/CD configuration if applicable

## References

- [Django Project Structure Best Practices 2025](https://studygyaan.com/django/best-practice-to-structure-django-project-directories-and-files)
- [Django Official Documentation - Settings](https://docs.djangoproject.com/en/5.2/topics/settings/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [OBCMS CLAUDE.md](../../CLAUDE.md)
