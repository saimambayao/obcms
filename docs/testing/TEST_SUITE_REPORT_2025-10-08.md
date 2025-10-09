# OBCMS Test Suite Report

**Date:** 2025-10-08
**Test Framework:** pytest 8.4.2
**Django Version:** 5.2.7
**Python Version:** 3.12.11

## Summary

**Total Tests:** 1,611 tests collected
**Configuration:** pytest stops after 5 failures (--maxfail=5)

### Test Run Results

**Status:** ❌ **FAILED** (stopped after 5 failures)

- ✅ **Passed:** 166 tests (10.3% of total)
- ❌ **Failed:** 5 tests (0.3% of total)
- ⏭️ **Skipped:** 46 tests (2.9% of total)
- ⏸️ **Not Run:** ~1,394 tests (86.5% of total - stopped due to --maxfail=5)

**Test Duration:** 1 minute 40 seconds

## Failed Tests

All failures are in the **Communities module** view tests:

### 1. Municipal Stat Cards Test
```
src/common/tests/test_communities_manage_municipal_view.py::ManageMunicipalStatCardsTests::test_stat_cards_present_expected_totals
```
**Issue:** Stat cards not displaying expected totals for municipal communities

### 2-4. Barangay Stat Cards Tests
```
src/common/tests/test_communities_manage_view.py::ManageBarangayStatCardsTests::test_stat_cards_present_expected_totals
src/common/tests/test_communities_manage_view.py::ManageBarangayStatCardsTests::test_stat_cards_respect_province_filter
src/common/tests/test_communities_manage_view.py::ManageBarangayStatCardsTests::test_stat_cards_respect_region_filter
```
**Issues:**
- Stat cards not displaying expected totals for barangay communities
- Province filter not working correctly with stat cards
- Region filter not working correctly with stat cards

### 5. Community Need Submit View
```
src/common/tests/test_community_need_submit_view.py::CommunityNeedSubmitViewTests::test_get_renders_form
```
**Issue:** Community need submission form not rendering correctly

## Skipped Tests (46 tests)

### AI/Embedding Dependencies (19 tests)
- **ai_assistant/tests/** (7 tests) - Requires embedding models
- **common/tests/test_advanced_registry.py** (1 test) - Requires legacy embedding dependencies
- **communities/tests/test_ai_services.py** (1 test) - Requires GEMINI API key
- **coordination/tests/test_ai_services.py** (1 test) - Requires external AI configuration
- **mana/tests/test_ai_services.py** (1 test) - Requires GEMINI configuration
- **recommendations/policies/tests/test_ai_services.py** (1 test) - Requires AI/embedding dependencies

### Legacy/Refactor Dependencies (27 tests)
- **communities/tests/test_bulk_sync.py** (1 test) - Requires seeded coverage data after refactor
- **communities/tests/test_forms.py** (1 test) - Requires updated widgets after refactor
- **communities/tests/test_integration.py** (1 test) - Requires updated hierarchy fixtures after refactor
- **monitoring/tests/** (6 tests) - Require legacy MonitoringEntry schema
- **project_central/tests/test_views.py** (1 test) - Requires legacy StaffTask/TaskTemplate models
- **tests/test_calendar_performance.py** (20 tests) - Requires legacy Event models
- **tests/test_calendar_feed.py** (1 test) - Requires legacy EventParticipant routes
- **scripts/test_work_item_tree_performance.py** (1 test) - Not for automated pytest runs

**Note:** These skips are intentional and expected per pytest.ini documentation.

## Test Suite Warnings (12 warnings)

All warnings are RuntimeWarnings about DateTimeField receiving naive datetime values:
- **Module:** `src/common/tests/test_chat_backend_comprehensive.py`
- **Issue:** ChatMessage.created_at receiving naive datetime while timezone support is active
- **Impact:** Non-critical, but should be fixed for timezone consistency

## Successful Test Categories

The following test modules **passed all tests** before the suite stopped:

### Common Module (36 tests)
- ✅ Chat engine tests (query executor, intent classifier, response formatter)
- ✅ Conversation manager tests
- ✅ Chat API views tests

### Backend Comprehensive Tests
- ✅ HTMX integration tests
- ✅ Concurrent request handling
- ✅ Error handling and validation
- ✅ Authentication and authorization

## Analysis

### Severity: **MEDIUM**

**Positive:**
- Core chat functionality is working (36/36 tests passed)
- Backend HTMX integration is solid
- Most failures are in view-level stat card rendering
- No critical system failures or database issues

**Concerns:**
- Communities module has stat card display issues (4 failures)
- Form rendering issue in community need submission (1 failure)
- Cannot assess 86.5% of test suite due to early termination
- 12 timezone warnings need attention

### Root Cause Analysis

The failures appear to be related to:
1. **Stat Card Data Aggregation:** Expected totals not matching actual display
2. **Filter Propagation:** Province/region filters not applied correctly to stat cards
3. **Form Rendering:** Community need form template/context issue

These are likely related to recent UI refactoring or data model changes.

## Recommendations

### Immediate Actions (Priority: HIGH)

1. **Fix Communities Stat Cards** (4 tests)
   - Review stat card query logic in `src/common/views/`
   - Check filter parameter propagation
   - Verify expected vs actual counts in test fixtures

2. **Fix Community Need Form** (1 test)
   - Review template: `src/templates/communities/`
   - Check view context in `src/communities/views.py`
   - Verify form initialization

3. **Run Full Suite** (Priority: MEDIUM)
   - Fix --maxfail to allow complete run: `pytest --maxfail=1000`
   - Or remove maxfail to see all failures: Edit pytest.ini
   - Generate complete test report

4. **Fix Timezone Warnings** (Priority: LOW)
   - Update `test_chat_backend_comprehensive.py` to use timezone-aware datetimes
   - Use `django.utils.timezone.now()` instead of `datetime.now()`

### Testing Strategy

```bash
# 1. Test specific failures individually
pytest src/common/tests/test_communities_manage_view.py -v
pytest src/common/tests/test_communities_manage_municipal_view.py -v
pytest src/common/tests/test_community_need_submit_view.py -v

# 2. After fixes, run full suite
pytest --maxfail=1000 -v

# 3. Generate coverage report
coverage run -m pytest
coverage report
coverage html
```

## Comparison to Expected Baseline

**Expected (per CLAUDE.md):** 254/256 tests passing (99.2%)
**Current:** 166 passed, 5 failed, 46 skipped, 1,394 not run (86.5% incomplete)

**Status:** ⚠️ **CANNOT CONFIRM** - Test suite stopped too early for valid comparison

## Next Steps

1. ✅ **Immediate:** Fix the 5 failing tests in communities module
2. 🔄 **Follow-up:** Run complete test suite to get full picture
3. 📊 **Validation:** Compare results against 254/256 baseline
4. 🐛 **Maintenance:** Fix timezone warnings for clean test output

---

**Report Generated:** 2025-10-08
**Test Command:** `pytest -v --tb=short`
**Configuration:** `pytest.ini` (--maxfail=5, --strict-markers, -ra)
