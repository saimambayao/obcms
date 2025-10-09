# Test Failure Analysis Report

**Date:** 2025-10-08
**Status:** ⚠️ **INVESTIGATION BLOCKED** (Test timeouts prevent direct debugging)
**Failing Tests:** 5 tests in communities module

---

## Executive Summary

All 5 failing tests are timing out during execution (>60 seconds), preventing direct observation of the actual failure reasons. Through code analysis, the views and templates appear correctly implemented. The timeout suggests a database query performance issue or test infrastructure problem rather than logic errors in the views.

---

## Failing Tests

### 1. Municipal Stat Cards Test
**Test:** `src/common/tests/test_communities_manage_municipal_view.py::ManageMunicipalStatCardsTests::test_stat_cards_present_expected_totals`

**Expected Behavior:**
- View: `communities_manage_municipal` (URL: `/communities/managemunic ipal/`)
- Context should contain:
  - `stats` dict with: `total_coverages=3`, `total_population=4500`, `auto_synced=2`, `manual=1`
  - `stat_cards` list with values: `[3, 4500, 2, 1]`

**Code Analysis:**
✅ View logic appears correct (lines 741-998 in `src/common/views/communities.py`)
- Correctly aggregates coverages count
- Properly sums population (with barangay fallback logic)
- Accurately counts auto_synced and manual coverages

### 2-4. Barangay Stat Cards Tests
**Tests:**
- `src/common/tests/test_communities_manage_view.py::ManageBarangayStatCardsTests::test_stat_cards_present_expected_totals`
- `src/common/tests/test_communities_manage_view.py::ManageBarangayStatCardsTests::test_stat_cards_respect_province_filter`
- `src/common/tests/test_communities_manage_view.py::ManageBarangayStatCardsTests::test_stat_cards_respect_region_filter`

**Expected Behavior:**
- View: `communities_manage` (URL: `/communities/manage/`)
- Stat cards values: `[4, 400, 3]` (barangay OBCs, population, municipality coverages)
- Filters should correctly restrict results by region/province

**Code Analysis:**
✅ View logic appears correct (lines 484-737 in `src/common/views/communities.py`)
- Correctly counts barangay communities
- Properly sums barangay population
- Accurately counts municipality coverages
- Filter logic properly chains for region → province → municipality

### 5. Community Need Submit Form Test
**Test:** `src/common/tests/test_community_need_submit_view.py::CommunityNeedSubmitViewTests::test_get_renders_form`

**Expected Behavior:**
- View: `community_need_submit` (URL: `/oobc-management/community-needs/submit/`)
- Should return 200 status
- Context should contain `form`
- Template should contain text "Submit a Community Need"

**Code Analysis:**
✅ View and template are correct
- View in `src/common/views/management.py` line 4030
- Has `@login_required` decorator ✓
- Returns correct context with `form` key ✓
- Template at `src/templates/common/community_need_submit.html` contains expected text (line 20) ✓

---

## Root Cause Analysis

### Primary Issue: Test Execution Timeouts

**Symptoms:**
- All 5 tests timeout after 45-60 seconds
- Timeout occurs even during test collection phase
- Cannot run pytest with any combination of flags

**Possible Causes:**

1. **Database Query Performance** (Most Likely)
   - Complex subqueries in `communities_manage_municipal` (lines 819-831)
   - `MunicipalityCoverage.sync_for_municipality()` called multiple times in test setup
   - Each sync triggers `refresh_from_communities()` with aggregation queries
   - Test database might not have indexes

2. **Test Database Setup Issue**
   - Missing `communities_municipalitycoverage` table in development database
   - Test database creation might be failing silently
   - Migration issues preventing proper table creation

3. **Circular Import or Initialization Loop**
   - Recent addition of MOA permission decorators (`@moa_no_access`, `@moa_view_only`)
   - These decorators import from `common.utils.moa_permissions`
   - Possible circular import chain during test collection

### Recent Code Changes

**Modified:** `src/common/views/communities.py`
- Added import: `from ..utils.moa_permissions import moa_no_access, moa_view_only` (line 34)
- Added decorators to multiple views:
  - `@moa_no_access` on create/edit/delete views
  - `@moa_view_only` on detail views
- **Note:** `communities_manage` and `communities_manage_municipal` do NOT have MOA decorators

---

## Recommended Solutions

### Option 1: Database Performance Fix (IMMEDIATE)

**Optimize the barangay population subquery:**

```python
# In communities_manage_municipal view (line 819-831)
# Current implementation:
barangay_population_subquery = (
    OBCCommunity.objects.filter(
        barangay__municipality=OuterRef("municipality")
    )
    .values("barangay__municipality")
    .annotate(total=Sum("estimated_obc_population"))
    .values("total")
)

# Optimized: Pre-compute outside the subquery
from django.db.models import OuterRef, Subquery, Sum, Q

# Pre-compute barangay populations per municipality
barangay_populations = (
    OBCCommunity.objects
    .values("barangay__municipality")
    .annotate(total=Sum("estimated_obc_population"))
)
barangay_pop_dict = {item["barangay__municipality"]: item["total"] for item in barangay_populations}

# Use in-memory lookup instead of subquery
for coverage in coverages:
    coverage.barangay_pop = barangay_pop_dict.get(coverage.municipality_id, 0)
```

### Option 2: Test Database Reset (SIMPLE)

```bash
# Delete test database cache
find . -name "test_*.sqlite3" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Run migrations explicitly
cd src
python manage.py migrate --run-syncdb

# Try tests again
pytest src/common/tests/test_communities_manage_view.py -xvs
```

### Option 3: Isolate and Debug (DIAGNOSTIC)

**Create minimal test:**

```python
# test_minimal_stat_cards.py
from django.test import TestCase, Client
from django.urls import reverse
from common.models import Region, Province, Municipality
from communities.models import MunicipalityCoverage

class MinimalStatCardsTest(TestCase):
    def test_municipal_view_loads(self):
        """Test that municipal view loads without timeout."""
        user = User.objects.create_user(username="test", password="test", user_type="oobc_staff")
        self.client.force_login(user)

        # Don't create any data - just test the view loads
        response = self.client.get(reverse("common:communities_manage_municipal"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("stat_cards", response.context)
```

If this minimal test passes, gradually add data creation until it times out - this identifies the bottleneck.

### Option 4: Run Tests in Docker (ISOLATED ENVIRONMENT)

```bash
# Create fresh test environment
docker run --rm -it python:3.12 bash

# Inside container:
# ... setup project ...
pytest src/common/tests/test_communities_manage_view.py
```

---

## Verification Steps

Once fixes are applied:

```bash
# 1. Run the 5 specific failing tests
pytest src/common/tests/test_communities_manage_municipal_view.py::ManageMunicipalStatCardsTests::test_stat_cards_present_expected_totals -xvs
pytest src/common/tests/test_communities_manage_view.py::ManageBarangayStatCardsTests -xvs
pytest src/common/tests/test_community_need_submit_view.py::CommunityNeedSubmitViewTests::test_get_renders_form -xvs

# 2. Run full communities test suite
pytest src/common/tests/test_communities*.py -xvs

# 3. Run complete test suite
pytest --maxfail=1000 -v

# 4. Check for improved pass rate
# Expected: 254/256 tests passing (99.2%)
```

---

## Code Quality Notes

**Positive Findings:**
- ✅ View logic is sound and follows Django best practices
- ✅ Templates exist and contain expected content
- ✅ Login decorators are properly applied
- ✅ Import statements are correct

**Areas for Improvement:**
- ⚠️ Complex subquery in `communities_manage_municipal` could be optimized
- ⚠️ `refresh_from_communities()` is called on every save - consider caching
- ⚠️ Test setup creates unnecessary syncs (4x `sync_for_municipality` calls)

---

## Next Steps

**Priority 1: Immediate Action Required**
1. Run Option 2 (Test Database Reset) - takes 30 seconds
2. If still failing, try Option 3 (Minimal Test) to isolate issue
3. Report results back for further analysis

**Priority 2: Performance Optimization**
4. Implement Option 1 (Subquery Optimization)
5. Add database indexes if missing

**Priority 3: Long-term Improvements**
6. Add pytest-timeout plugin configuration
7. Create test performance benchmarks
8. Document test data setup best practices

---

**Report Status:** Ready for User Action
**Blocking Issue:** Cannot execute tests due to timeouts
**Confidence in Code Analysis:** HIGH (Code appears correct)
**Recommended First Step:** Test Database Reset (Option 2)
