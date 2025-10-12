# Phase 0: URL Refactoring - Fix "Monolithic Router Anti-Pattern"

**Document Version:** 1.0
**Date:** 2025-10-13
**Status:** Ready for Implementation
**Priority:** CRITICAL - Foundation for all Pre-BMMS phases
**Complexity:** Moderate

---

## Executive Summary

### Current Problem

The OBCMS codebase suffers from a **"Monolithic Router Anti-Pattern"** where the `common/urls.py` file has grown to **847 lines** and handles URL routing for multiple Django apps that should manage their own routing.

**Impact:**
- **Tight Coupling**: All modules depend on common app for routing
- **Maintenance Burden**: Single file becomes bottleneck for development
- **Poor Separation of Concerns**: Communities, MANA, Coordination, and Recommendations logic mixed with common infrastructure
- **BMMS Blocker**: Cannot cleanly implement multi-tenant URL structure (`/moa/<ORG_CODE>/module/`)

### Target Outcome

**Clean Module Separation** with each Django app managing its own URL routing:

```
common/urls.py       847 lines → <200 lines (Dashboard, Auth, Shared Infrastructure)
communities/urls.py  0 lines   → ~50 lines (Community Management)
mana/urls.py         185 lines → ~250 lines (All MANA routes)
coordination/urls.py 0 lines   → ~100 lines (All Coordination routes)
recommendations/     0 lines   → ~80 lines (Policy Recommendations)
  policies/urls.py
```

**Benefits:**
- ✅ Clean module boundaries for future development
- ✅ Proper URL namespacing (`communities:manage` instead of `common:communities_manage`)
- ✅ Foundation for BMMS multi-tenant routing
- ✅ Easier testing and maintenance
- ✅ Better code organization

### Priority & Complexity

- **Priority:** CRITICAL - Must complete before Planning/Budgeting modules
- **Complexity:** Moderate
- **Risk:** Medium (898 template references to update)
- **Dependencies:** None (Phase 0 is the foundation)

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Target Architecture](#target-architecture)
3. [Detailed Task Breakdown](#detailed-task-breakdown)
4. [Technical Specifications](#technical-specifications)
5. [Implementation Guidelines](#implementation-guidelines)
6. [Testing Strategy](#testing-strategy)
7. [Success Criteria](#success-criteria)
8. [Rollback Plan](#rollback-plan)

---

## Current State Analysis

### Current URL Structure

**common/urls.py (847 lines) - Breakdown:**

```python
# ❌ PROBLEM: Single file handles routing for ALL apps

app_name = "common"

urlpatterns = [
    # ✅ CORRECT: Core common functionality (~150 lines)
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),

    # ❌ WRONG: Communities app URLs (~120 lines)
    path("communities/", views.communities_home, name="communities_home"),
    path("communities/add/", views.communities_add, name="communities_add"),
    path("communities/<int:community_id>/", views.communities_view, name="communities_view"),
    # ... 40+ more communities URLs

    # ❌ WRONG: MANA app URLs (~180 lines)
    path("mana/", views.mana_home, name="mana_home"),
    path("mana/new-assessment/", views.mana_new_assessment, name="mana_new_assessment"),
    path("mana/manage-assessments/", views.mana_manage_assessments, name="mana_manage_assessments"),
    # ... 50+ more MANA URLs

    # ❌ WRONG: Coordination app URLs (~150 lines)
    path("coordination/", views.coordination_home, name="coordination_home"),
    path("coordination/organizations/", views.coordination_organizations, name="coordination_organizations"),
    path("coordination/partnerships/", views.coordination_partnerships, name="coordination_partnerships"),
    # ... 45+ more coordination URLs

    # ❌ WRONG: Recommendations app URLs (~100 lines)
    path("recommendations/", views.recommendations_home, name="recommendations_home"),
    path("recommendations/new/", views.recommendations_new, name="recommendations_new"),
    path("recommendations/manage/", views.recommendations_manage, name="recommendations_manage"),
    # ... 30+ more recommendations URLs

    # ❌ WRONG: OOBC Management URLs (~150 lines)
    path("oobc-management/", views.oobc_management_home, name="oobc_management_home"),
    path("oobc-management/calendar/", views.oobc_calendar, name="oobc_calendar"),
    path("oobc-management/staff/", views.staff_management, name="staff_management"),
    # ... 40+ more OOBC management URLs
]
```

### Current Views Distribution

**common/views.py (2,266 lines) - Contains views for:**

- Communities module (~400 lines)
- MANA module (~500 lines)
- Coordination module (~350 lines)
- Recommendations module (~250 lines)
- OOBC Management module (~400 lines)
- Core common functionality (~366 lines)

### Template Impact

**898 template references** use `{% url 'common:module_action' %}` pattern that must be updated.

### Existing Module URLs

**Already have their own urls.py files:**
- ✅ `communities/urls.py` - Geographic data only (38 lines)
- ✅ `mana/urls.py` - Facilitator/Participant workflows (185 lines)
- ✅ `coordination/urls.py` - Exists but minimal
- ✅ `recommendations/policies/urls.py` - Exists but minimal

**Problem:** These files exist but `common/urls.py` still duplicates their routing.

---

## Target Architecture

### Target URL Structure

```python
# src/obc_management/urls.py - ROOT URL CONFIGURATION

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # ✅ Common App (Dashboard, Auth, Infrastructure ONLY)
    path("", include("common.urls")),  # ~200 lines

    # ✅ Module-Specific Apps (Each manages own routing)
    path("communities/", include("communities.urls")),  # ~50 lines
    path("mana/", include("mana.urls")),  # ~250 lines
    path("coordination/", include("coordination.urls")),  # ~100 lines
    path("recommendations/policies/", include("recommendations.policies.urls")),  # ~80 lines
    path("monitoring/", include("monitoring.urls")),  # Existing

    # API
    path("api/v1/", include("api.v1.urls")),
]
```

### Target Directory Structure

```
src/
├── common/
│   ├── urls.py           # ~200 lines (Dashboard, Auth, Shared Infrastructure)
│   ├── views/
│   │   ├── __init__.py
│   │   ├── auth.py       # Authentication views
│   │   ├── dashboard.py  # Dashboard views
│   │   ├── profile.py    # User profile views
│   │   ├── search.py     # Unified search (existing)
│   │   ├── chat.py       # AI chat (existing)
│   │   └── query_builder.py  # Query builder (existing)
│   └── views.py          # Re-exports for backward compatibility
│
├── communities/
│   ├── urls.py           # ~50 lines (All community management)
│   ├── views.py          # Community views (moved from common)
│   └── data_utils.py     # Existing
│
├── mana/
│   ├── urls.py           # ~250 lines (Assessment workflows + MANA core)
│   ├── views.py          # MANA core views (moved from common)
│   ├── facilitator_views.py  # Existing
│   ├── participant_views.py  # Existing
│   └── ai_views.py       # Existing
│
├── coordination/
│   ├── urls.py           # ~100 lines (Organizations, Partnerships, Events)
│   ├── views.py          # Coordination views (moved from common)
│   └── models.py         # Existing
│
├── recommendations/
│   └── policies/
│       ├── urls.py       # ~80 lines (Policy recommendations)
│       ├── views.py      # Policy views (moved from common)
│       └── models.py     # Existing
│
└── obc_management/
    ├── urls.py           # Root URL config (includes all apps)
    └── settings/         # Django settings
```

---

## Detailed Task Breakdown

### Step 1: Audit Current URL Patterns

**Objective:** Identify which URL patterns belong to which app

- [ ] **Task 1.1:** Extract Communities URLs from common/urls.py
  - Identify all paths starting with `"communities/"`
  - Document view functions used
  - Note any cross-app dependencies

- [ ] **Task 1.2:** Extract MANA URLs from common/urls.py
  - Identify all paths starting with `"mana/"`
  - Document view functions used
  - Separate from existing mana/urls.py content

- [ ] **Task 1.3:** Extract Coordination URLs from common/urls.py
  - Identify all paths starting with `"coordination/"`
  - Document view functions used
  - Note integration with WorkItem system

- [ ] **Task 1.4:** Extract Recommendations URLs from common/urls.py
  - Identify all paths starting with `"recommendations/"`
  - Document view functions used
  - Determine if should go to policies app or new recommendations app

- [ ] **Task 1.5:** Identify Common-Only URLs
  - Dashboard URLs
  - Authentication URLs
  - Profile URLs
  - OOBC Management URLs (Staff, Calendar, Work Items)
  - Data utilities (import/export)
  - Search, Chat, Query Builder (already separated)

**Deliverables:**
- `docs/plans/bmms/prebmms/url_audit_report.md` - Complete URL mapping

---

### Step 2: Create/Update URLs Files

**Objective:** Set up proper URL routing for each app

- [ ] **Task 2.1:** Update communities/urls.py
  - Add all community management URLs
  - Set `app_name = "communities"`
  - Organize by functional area:
    - Barangay OBC management
    - Municipal OBC management
    - Provincial OBC management
    - Stakeholder management
    - Geographic data (existing)

- [ ] **Task 2.2:** Update mana/urls.py
  - Merge existing MANA URLs with common/urls.py MANA URLs
  - Organize by functional area:
    - Assessment workflows (existing: facilitator, participant)
    - Assessment management (from common)
    - Activity planning (from common)
    - Geographic data (from common)
    - AI analysis (existing)

- [ ] **Task 2.3:** Update coordination/urls.py
  - Add all coordination URLs from common
  - Organize by functional area:
    - Organizations
    - Partnerships
    - Events/Activities
    - Calendar integration
    - Resource booking

- [ ] **Task 2.4:** Update recommendations/policies/urls.py
  - Add all recommendations URLs from common
  - Organize by functional area:
    - Policy recommendations CRUD
    - Programs and services
    - Area-based filtering
    - Stats and metrics

- [ ] **Task 2.5:** Refactor common/urls.py
  - Keep only core common functionality:
    - Authentication (login, logout, registration)
    - Dashboard and metrics
    - Profile management
    - OOBC Management (Staff, Calendar, Work Items)
    - Data utilities (import/export, guidelines)
    - Deprecation dashboard
    - Search, Chat, Query Builder (existing)
  - Remove all module-specific URLs
  - Add temporary backward-compatible redirects

**Deliverables:**
- Updated `urls.py` files for each app
- Reduced `common/urls.py` from 847 lines to <200 lines

---

### Step 3: Move Views to Respective Apps

**Objective:** Relocate view functions from common to their proper apps

- [ ] **Task 3.1:** Restructure common/views.py
  - Split `common/views.py` (2,266 lines) into organized modules:
    ```
    common/views/
    ├── __init__.py          # Re-exports for backward compatibility
    ├── auth.py              # CustomLoginView, CustomLogoutView, UserRegistrationView
    ├── dashboard.py         # dashboard, dashboard_stats_cards, dashboard_metrics
    ├── profile.py           # profile, user settings
    ├── oobc_management.py   # OOBC Management views
    ├── data_utils.py        # Import/export utilities
    └── deprecation.py       # Deprecation dashboard
    ```
  - Update imports in `common/views/__init__.py` for backward compatibility

- [ ] **Task 3.2:** Move Communities Views
  - Create/update `communities/views.py`
  - Move community-related views from `common/views.py`:
    - `communities_home`, `communities_add`, `communities_manage`
    - `communities_view`, `communities_edit`, `communities_delete`
    - `communities_manage_municipal`, `communities_manage_provincial`
    - `communities_stakeholders`
    - All Provincial/Municipal OBC views
  - Update imports to use `communities.models`

- [ ] **Task 3.3:** Move MANA Views
  - Create/update `mana/views.py` for core MANA views
  - Move MANA views from `common/views.py`:
    - `mana_home`, `mana_stats_cards`
    - `mana_regional_overview`, `mana_provincial_overview`
    - `mana_new_assessment`, `mana_manage_assessments`
    - `mana_assessment_detail`, `mana_assessment_edit`, `mana_assessment_delete`
    - `mana_geographic_data`
    - Activity planner and log views
  - Keep existing facilitator/participant/ai views in separate files

- [ ] **Task 3.4:** Move Coordination Views
  - Create/update `coordination/views.py`
  - Move coordination views from `common/views.py`:
    - `coordination_home`, `coordination_events`
    - `coordination_organizations`, `organization_*` views
    - `coordination_partnerships`, `partnership_*` views
    - `coordination_calendar`, `coordination_view_all`
    - `coordination_activity_create`, `coordination_note_create`
  - Update to use coordination models

- [ ] **Task 3.5:** Move Recommendations Views
  - Create/update `recommendations/policies/views.py`
  - Move recommendations views from `common/views.py`:
    - `recommendations_home`, `recommendations_stats_cards`
    - `recommendations_new`, `recommendations_create`, `recommendations_autosave`
    - `recommendations_manage`, `recommendations_view`, `recommendations_edit`, `recommendations_delete`
    - `recommendations_programs`, `recommendations_services`
    - `recommendations_by_area`
  - Update to use recommendations models

**Deliverables:**
- Organized view modules for each app
- Backward-compatible `common/views/__init__.py`
- Updated imports throughout views

---

### Step 4: Update Template URL References

**Objective:** Update all template references to use correct namespaces

- [ ] **Task 4.1:** Audit Template References
  - Run: `grep -r "{% url 'common:" src/templates/ > template_audit.txt`
  - Categorize by module (communities, mana, coordination, recommendations)
  - Total: **898 template references** to update

- [ ] **Task 4.2:** Update Communities Template References
  - Find: `{% url 'common:communities_*' %}`
  - Replace: `{% url 'communities:*' %}`
  - Example: `{% url 'common:communities_manage' %}` → `{% url 'communities:manage' %}`
  - Estimated: ~150 references

- [ ] **Task 4.3:** Update MANA Template References
  - Find: `{% url 'common:mana_*' %}`
  - Replace: `{% url 'mana:*' %}`
  - Example: `{% url 'common:mana_home' %}` → `{% url 'mana:home' %}`
  - Estimated: ~250 references

- [ ] **Task 4.4:** Update Coordination Template References
  - Find: `{% url 'common:coordination_*' %}`
  - Replace: `{% url 'coordination:*' %}`
  - Example: `{% url 'common:coordination_organizations' %}` → `{% url 'coordination:organizations' %}`
  - Estimated: ~180 references

- [ ] **Task 4.5:** Update Recommendations Template References
  - Find: `{% url 'common:recommendations_*' %}`
  - Replace: `{% url 'recommendations:policies:*' %}` or `{% url 'recommendations:*' %}`
  - Example: `{% url 'common:recommendations_manage' %}` → `{% url 'recommendations:manage' %}`
  - Estimated: ~100 references

- [ ] **Task 4.6:** Update OOBC Management Template References
  - Review OOBC Management URLs (calendar, staff, work items)
  - Decide: Keep in `common` namespace OR move to separate `oobc_management` namespace
  - Update templates accordingly
  - Estimated: ~150 references

- [ ] **Task 4.7:** Update Navigation Templates
  - Update main navigation (`templates/base.html`, `templates/components/navigation.html`)
  - Update module-specific navigation menus
  - Ensure all menu links use correct namespaces

**Deliverables:**
- All 898 template references updated
- Script: `scripts/update_template_urls.py` (optional automation)

---

### Step 5: Add Backward-Compatible Redirects

**Objective:** Provide graceful migration path for bookmarks and external links

- [ ] **Task 5.1:** Implement Redirect Middleware (Optional)
  - Create `common/middleware/url_redirects.py`
  - Handle old URL patterns and redirect to new namespaces
  - Log redirects for monitoring

- [ ] **Task 5.2:** Add Redirect Views in common/urls.py
  ```python
  from django.views.generic import RedirectView

  urlpatterns += [
      # ⚠️ Temporary redirects (remove after 1 release cycle)
      path("communities/", RedirectView.as_view(
          pattern_name='communities:home',
          permanent=False
      )),
      path("mana/", RedirectView.as_view(
          pattern_name='mana:home',
          permanent=False
      )),
      path("coordination/", RedirectView.as_view(
          pattern_name='coordination:home',
          permanent=False
      )),
      # ... more redirects
  ]
  ```

- [ ] **Task 5.3:** Document Deprecation Timeline
  - Add deprecation notices to old URL patterns
  - Set removal date (e.g., 2 months after Phase 0 completion)
  - Update deprecation dashboard

**Deliverables:**
- Backward-compatible redirect configuration
- Deprecation documentation

---

### Step 6: Update Tests

**Objective:** Ensure all tests use correct URL namespaces

- [ ] **Task 6.1:** Update URL Resolution Tests
  - Find: `reverse('common:module_*')`
  - Replace: `reverse('module:*')`
  - Update test fixtures if needed

- [ ] **Task 6.2:** Add URL Namespace Tests
  ```python
  # tests/test_url_namespaces.py

  from django.urls import reverse
  from django.test import TestCase

  class URLNamespaceTests(TestCase):
      """Test that all URL namespaces resolve correctly"""

      def test_communities_namespace_works(self):
          """Communities URLs accessible via correct namespace"""
          url = reverse('communities:manage')
          self.assertEqual(url, '/communities/')

      def test_mana_namespace_works(self):
          """MANA URLs accessible via correct namespace"""
          url = reverse('mana:home')
          self.assertEqual(url, '/mana/')

      def test_coordination_namespace_works(self):
          """Coordination URLs accessible via correct namespace"""
          url = reverse('coordination:home')
          self.assertEqual(url, '/coordination/')

      def test_recommendations_namespace_works(self):
          """Recommendations URLs accessible via correct namespace"""
          url = reverse('recommendations:home')
          self.assertEqual(url, '/recommendations/policies/')
  ```

- [ ] **Task 6.3:** Add Backward Compatibility Tests
  ```python
  def test_old_communities_url_redirects(self):
      """Old common:communities URLs redirect to new namespace"""
      response = self.client.get('/communities/')  # Old URL
      self.assertEqual(response.status_code, 302)
      self.assertTrue(response.url.startswith('/communities/'))
  ```

- [ ] **Task 6.4:** Run Full Test Suite
  - Execute: `pytest -v`
  - Fix failing tests related to URL changes
  - Ensure 99%+ test coverage maintained

**Deliverables:**
- Updated test suite (all tests passing)
- New URL namespace test coverage

---

### Step 7: Update Documentation

**Objective:** Document new URL structure for developers

- [ ] **Task 7.1:** Update CLAUDE.md
  - Document new URL namespace patterns
  - Provide examples of correct URL usage
  - Add migration guide section

- [ ] **Task 7.2:** Create Migration Guide
  - Document: `docs/deployment/url_refactoring_migration_guide.md`
  - Include before/after examples
  - Provide search/replace patterns for remaining code

- [ ] **Task 7.3:** Update API Documentation
  - Update any API docs referencing URL patterns
  - Update Swagger/OpenAPI specs if applicable

- [ ] **Task 7.4:** Update Developer Onboarding Docs
  - Document new project structure
  - Explain URL namespace conventions
  - Add examples for creating new modules

**Deliverables:**
- Updated `CLAUDE.md`
- Migration guide document
- Updated developer documentation

---

### Step 8: Final Verification & Cleanup

**Objective:** Ensure refactoring is complete and stable

- [ ] **Task 8.1:** Manual Testing
  - Test all module homepages
  - Test CRUD operations for each module
  - Test navigation between modules
  - Test user authentication flows

- [ ] **Task 8.2:** Performance Testing
  - Compare page load times before/after
  - Check URL resolution performance
  - Monitor redirect overhead

- [ ] **Task 8.3:** Code Review
  - Review all changed files
  - Check for import errors
  - Verify coding standards compliance

- [ ] **Task 8.4:** Remove TODOs
  - Remove temporary comments
  - Clean up debugging code
  - Finalize documentation

- [ ] **Task 8.5:** Git Commit
  - Create feature branch: `feature/phase-0-url-refactoring`
  - Commit changes with descriptive message
  - Create pull request for review

**Deliverables:**
- Clean, tested codebase
- Git branch ready for merge

---

## Technical Specifications

### URL Namespace Mapping

**OLD → NEW Namespace Mapping:**

| Old Namespace | New Namespace | Example |
|---------------|---------------|---------|
| `common:communities_manage` | `communities:manage` | `{% url 'communities:manage' %}` |
| `common:communities_view` | `communities:detail` | `{% url 'communities:detail' pk=id %}` |
| `common:mana_home` | `mana:home` | `{% url 'mana:home' %}` |
| `common:mana_new_assessment` | `mana:assessment_create` | `{% url 'mana:assessment_create' %}` |
| `common:coordination_home` | `coordination:home` | `{% url 'coordination:home' %}` |
| `common:coordination_organizations` | `coordination:organizations` | `{% url 'coordination:organizations' %}` |
| `common:recommendations_home` | `recommendations:home` | `{% url 'recommendations:home' %}` |
| `common:recommendations_manage` | `recommendations:manage` | `{% url 'recommendations:manage' %}` |

### View Migration Mapping

**Communities Views (common/views.py → communities/views.py):**

```python
# OLD: common/views.py
def communities_home(request):
    # ... implementation

# NEW: communities/views.py
def home(request):  # Shorter name (namespace provides context)
    # ... same implementation

# URL:
# OLD: path("communities/", views.communities_home, name="communities_home")
# NEW: path("", views.home, name="home")  # in communities/urls.py
```

**MANA Views (common/views.py → mana/views.py):**

```python
# OLD: common/views.py
def mana_home(request):
    # ... implementation

# NEW: mana/views.py
def home(request):
    # ... same implementation

# URL:
# OLD: path("mana/", views.mana_home, name="mana_home")
# NEW: path("", views.home, name="home")  # in mana/urls.py
```

### File Size Targets

**Target File Sizes After Refactoring:**

| File | Current | Target | Status |
|------|---------|--------|--------|
| `common/urls.py` | 847 lines | <200 lines | ✅ Target |
| `common/views.py` | 2,266 lines | <500 lines | ✅ Target |
| `communities/urls.py` | 38 lines | ~50 lines | ✅ Target |
| `communities/views.py` | 0 lines | ~400 lines | ✅ Create |
| `mana/urls.py` | 185 lines | ~250 lines | ✅ Expand |
| `mana/views.py` | 0 lines | ~500 lines | ✅ Create |
| `coordination/urls.py` | Minimal | ~100 lines | ✅ Expand |
| `coordination/views.py` | 0 lines | ~350 lines | ✅ Create |
| `recommendations/policies/urls.py` | Minimal | ~80 lines | ✅ Expand |
| `recommendations/policies/views.py` | 0 lines | ~250 lines | ✅ Create |

---

## Implementation Guidelines

### Code Examples for Creating urls.py Files

**Example: communities/urls.py (Complete Structure)**

```python
"""
Communities Module URL Configuration

This module handles all URL routing for Bangsamoro community management,
including Barangay OBC, Municipal OBC, and Provincial OBC.

URL Namespace: 'communities'
Base Path: /communities/
"""

from django.urls import path
from . import views, data_utils

app_name = "communities"

urlpatterns = [
    # Module Home
    path("", views.home, name="home"),

    # Barangay OBC Management
    path("barangay/", views.manage_barangay, name="manage_barangay"),
    path("barangay/add/", views.add_barangay, name="add_barangay"),
    path("barangay/<int:pk>/", views.detail_barangay, name="detail_barangay"),
    path("barangay/<int:pk>/edit/", views.edit_barangay, name="edit_barangay"),
    path("barangay/<int:pk>/delete/", views.delete_barangay, name="delete_barangay"),
    path("barangay/<int:pk>/restore/", views.restore_barangay, name="restore_barangay"),

    # Municipal OBC Management
    path("municipal/", views.manage_municipal, name="manage_municipal"),
    path("municipal/add/", views.add_municipality, name="add_municipality"),
    path("municipal/<int:pk>/", views.detail_municipal, name="detail_municipal"),
    path("municipal/<int:pk>/edit/", views.edit_municipal, name="edit_municipal"),
    path("municipal/<int:pk>/delete/", views.delete_municipal, name="delete_municipal"),
    path("municipal/<int:pk>/restore/", views.restore_municipal, name="restore_municipal"),

    # Provincial OBC Management
    path("provincial/", views.manage_provincial, name="manage_provincial"),
    path("provincial/add/", views.add_province, name="add_province"),
    path("provincial/<int:pk>/", views.detail_provincial, name="detail_provincial"),
    path("provincial/<int:pk>/edit/", views.edit_provincial, name="edit_provincial"),
    path("provincial/<int:pk>/delete/", views.delete_provincial, name="delete_provincial"),
    path("provincial/<int:pk>/submit/", views.submit_provincial, name="submit_provincial"),
    path("provincial/<int:pk>/restore/", views.restore_provincial, name="restore_provincial"),

    # Stakeholders
    path("stakeholders/", views.stakeholders, name="stakeholders"),

    # Location Utilities
    path("locations/centroid/", views.location_centroid, name="location_centroid"),

    # Geographic Data (existing)
    path("geographic-data/", views.geographic_data_list, name="geographic_data_list"),
    path("geographic-data/add-layer/", views.add_data_layer, name="add_data_layer"),
    path("geographic-data/create-visualization/", views.create_visualization, name="create_visualization"),

    # Data Import/Export
    path("import/", data_utils.import_communities_csv, name="import_csv"),
    path("export/", data_utils.export_communities, name="export"),
    path("report/", data_utils.generate_obc_report, name="generate_report"),
]
```

**Example: mana/urls.py (Expanded with Core MANA)**

```python
"""
MANA (Mapping and Needs Assessment) Module URL Configuration

Handles all MANA-related routing including facilitator workflows,
participant assessments, and core MANA management.

URL Namespace: 'mana'
Base Path: /mana/
"""

from django.urls import path
from . import views, facilitator_views, participant_views, ai_views

app_name = "mana"

urlpatterns = [
    # ============================================================================
    # CORE MANA MANAGEMENT (from common)
    # ============================================================================

    # Module Home
    path("", views.home, name="home"),
    path("stats-cards/", views.stats_cards, name="stats_cards"),

    # Overview Dashboards
    path("regional/", views.regional_overview, name="regional_overview"),
    path("provincial/", views.provincial_overview, name="provincial_overview"),
    path("provincial/<int:province_id>/", views.provincial_detail, name="provincial_detail"),
    path("provincial/<int:province_id>/edit/", views.province_edit, name="province_edit"),
    path("provincial/<int:province_id>/delete/", views.province_delete, name="province_delete"),

    # Assessment Management
    path("assessments/new/", views.assessment_create, name="assessment_create"),
    path("assessments/", views.manage_assessments, name="manage_assessments"),
    path("assessments/<uuid:pk>/", views.assessment_detail, name="assessment_detail"),
    path("assessments/<uuid:pk>/edit/", views.assessment_edit, name="assessment_edit"),
    path("assessments/<uuid:pk>/delete/", views.assessment_delete, name="assessment_delete"),

    # MANA Modules
    path("desk-review/", views.desk_review, name="desk_review"),
    path("survey/", views.survey_module, name="survey_module"),
    path("kii/", views.key_informant_interviews, name="kii"),
    path("playbook/", views.playbook, name="playbook"),

    # Activity Management
    path("activity-planner/", views.activity_planner, name="activity_planner"),
    path("activity-log/", views.activity_log, name="activity_log"),
    path("activity-processing/", views.activity_processing, name="activity_processing"),

    # Geographic Data
    path("geographic-data/", views.geographic_data, name="geographic_data"),

    # ============================================================================
    # FACILITATOR & PARTICIPANT WORKFLOWS (existing)
    # ============================================================================

    # Account Creation
    path("create-account/", facilitator_views.create_account, name="create_account"),

    # Assessment Selection
    path("participant/assessments/", participant_views.participant_assessments_list, name="participant_assessments_list"),
    path("facilitator/assessments/", facilitator_views.facilitator_assessments_list, name="facilitator_assessments_list"),
    path("facilitator/dashboard/", facilitator_views.facilitator_assessments_list, name="facilitator_dashboard_redirect"),

    # Participant Routes
    path("assessments/<uuid:assessment_id>/participant/onboarding/", participant_views.participant_onboarding, name="participant_onboarding"),
    path("assessments/<uuid:assessment_id>/participant/dashboard/", participant_views.participant_dashboard, name="participant_dashboard"),
    path("assessments/<uuid:assessment_id>/participant/workshops/<str:workshop_type>/", participant_views.participant_workshop_detail, name="participant_workshop_detail"),
    path("assessments/<uuid:assessment_id>/participant/workshops/<str:workshop_type>/review/", participant_views.participant_workshop_review, name="participant_workshop_review"),
    path("assessments/<uuid:assessment_id>/participant/workshops/<str:workshop_type>/outputs/", participant_views.participant_workshop_outputs, name="participant_workshop_outputs"),
    path("assessments/<uuid:assessment_id>/participant/notifications/<int:notification_id>/mark-read/", participant_views.mark_notification_read, name="mark_notification_read"),

    # Facilitator Routes
    path("assessments/<uuid:assessment_id>/facilitator/dashboard/", facilitator_views.facilitator_dashboard, name="facilitator_dashboard"),
    path("assessments/<uuid:assessment_id>/facilitator/participants/", facilitator_views.manage_participants, name="facilitator_manage_participants"),
    path("assessments/<uuid:assessment_id>/facilitator/participants/<int:participant_id>/reset/", facilitator_views.reset_participant_progress, name="facilitator_reset_participant"),
    path("assessments/<uuid:assessment_id>/facilitator/workshops/<str:workshop_type>/advance/", facilitator_views.advance_workshop, name="facilitator_advance_workshop"),
    path("assessments/<uuid:assessment_id>/facilitator/workshops/<str:workshop_type>/synthesis/", facilitator_views.generate_synthesis, name="facilitator_generate_synthesis"),
    path("assessments/<uuid:assessment_id>/facilitator/synthesis/<int:synthesis_id>/regenerate/", facilitator_views.regenerate_synthesis, name="facilitator_regenerate_synthesis"),
    path("assessments/<uuid:assessment_id>/facilitator/synthesis/<int:synthesis_id>/approve/", facilitator_views.approve_synthesis, name="facilitator_approve_synthesis"),
    path("assessments/<uuid:assessment_id>/facilitator/exports/<str:workshop_type>/<str:format_type>/", facilitator_views.export_workshop_responses, name="facilitator_export_workshop"),

    # ============================================================================
    # MANA INTEGRATION FEATURES
    # ============================================================================

    # Task Management
    path("assessments/<uuid:assessment_id>/tasks/board/", views.assessment_tasks_board, name="assessment_tasks_board"),

    # Calendar Integration
    path("assessments/<uuid:assessment_id>/calendar/", views.assessment_calendar, name="assessment_calendar"),
    path("assessments/<uuid:assessment_id>/calendar/feed/", views.assessment_calendar_feed, name="assessment_calendar_feed"),

    # Needs Prioritization
    path("needs/prioritize/", views.needs_prioritization_board, name="needs_prioritize"),
    path("needs/update-ranking/", views.needs_update_ranking, name="needs_update_ranking"),
    path("needs/<int:need_id>/vote/", views.need_vote, name="need_vote"),
    path("needs/export/", views.needs_export, name="needs_export"),

    # ============================================================================
    # AI ANALYSIS
    # ============================================================================

    # Workshop Analysis
    path("workshop/<int:workshop_id>/ai-analysis/", ai_views.workshop_ai_analysis, name="workshop_ai_analysis"),
    path("workshop/<int:workshop_id>/analyze/", ai_views.trigger_workshop_analysis, name="trigger_workshop_analysis"),
    path("workshop/<int:workshop_id>/analysis/status/", ai_views.analysis_status, name="analysis_status"),
    path("workshop/<int:workshop_id>/generate-report/", ai_views.generate_report, name="generate_report"),
    path("workshop/<int:workshop_id>/report/status/", ai_views.report_status, name="report_status"),
    path("workshop/<int:workshop_id>/themes/", ai_views.theme_analysis, name="theme_analysis"),
    path("workshop/<int:workshop_id>/needs/", ai_views.needs_analysis, name="needs_analysis"),
    path("workshop/<int:workshop_id>/export-analysis/", ai_views.export_analysis_json, name="export_analysis_json"),

    # Content Validation
    path("validate-content/", ai_views.validate_content, name="validate_content"),
]
```

### View Migration Patterns

**Pattern 1: Simple View Migration**

```python
# BEFORE: common/views.py
def communities_home(request):
    """Communities module homepage"""
    obcs = BarangayOBC.objects.all()
    return render(request, 'communities/home.html', {'obcs': obcs})

# AFTER: communities/views.py
def home(request):
    """Communities module homepage"""
    obcs = BarangayOBC.objects.all()
    return render(request, 'communities/home.html', {'obcs': obcs})

# Note: Function name shortened (namespace provides context)
```

**Pattern 2: View with Namespace References**

```python
# BEFORE: common/views.py
def communities_manage(request):
    if request.method == 'POST':
        # ... process form
        messages.success(request, 'OBC created successfully')
        return redirect('common:communities_view', pk=obc.id)
    return render(request, 'communities/manage.html')

# AFTER: communities/views.py
def manage(request):
    if request.method == 'POST':
        # ... process form
        messages.success(request, 'OBC created successfully')
        return redirect('communities:detail', pk=obc.id)  # Updated namespace
    return render(request, 'communities/manage.html')
```

**Pattern 3: View with Cross-Module References**

```python
# BEFORE: common/views.py
def mana_assessment_detail(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    # Link to coordination calendar
    calendar_url = reverse('common:coordination_calendar')
    return render(request, 'mana/detail.html', {
        'assessment': assessment,
        'calendar_url': calendar_url
    })

# AFTER: mana/views.py
def assessment_detail(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    # Link to coordination calendar (updated namespace)
    calendar_url = reverse('coordination:calendar')
    return render(request, 'mana/detail.html', {
        'assessment': assessment,
        'calendar_url': calendar_url
    })
```

### Template Update Patterns

**Pattern 1: Simple URL Tag Update**

```django
{# BEFORE #}
<a href="{% url 'common:communities_manage' %}">Manage OBCs</a>

{# AFTER #}
<a href="{% url 'communities:manage' %}">Manage OBCs</a>
```

**Pattern 2: URL with Parameters**

```django
{# BEFORE #}
<a href="{% url 'common:communities_view' community_id=obc.id %}">View</a>

{# AFTER #}
<a href="{% url 'communities:detail' pk=obc.id %}">View</a>
```

**Pattern 3: URL in Form Action**

```django
{# BEFORE #}
<form method="post" action="{% url 'common:mana_new_assessment' %}">

{# AFTER #}
<form method="post" action="{% url 'mana:assessment_create' %}">
```

**Pattern 4: Navigation Menu**

```django
{# BEFORE: templates/base.html #}
<nav>
    <a href="{% url 'common:communities_home' %}">Communities</a>
    <a href="{% url 'common:mana_home' %}">MANA</a>
    <a href="{% url 'common:coordination_home' %}">Coordination</a>
    <a href="{% url 'common:recommendations_home' %}">Recommendations</a>
</nav>

{# AFTER: templates/base.html #}
<nav>
    <a href="{% url 'communities:home' %}">Communities</a>
    <a href="{% url 'mana:home' %}">MANA</a>
    <a href="{% url 'coordination:home' %}">Coordination</a>
    <a href="{% url 'recommendations:home' %}">Recommendations</a>
</nav>
```

### Redirect Configuration

**Option 1: RedirectView (Recommended)**

```python
# common/urls.py - Add temporary redirects

from django.views.generic import RedirectView

urlpatterns = [
    # ... core common URLs ...

    # ============================================================================
    # TEMPORARY BACKWARD-COMPATIBLE REDIRECTS
    # Remove after 2 months (e.g., after 2025-12-13)
    # ============================================================================

    # Communities redirects
    path(
        "communities/",
        RedirectView.as_view(pattern_name='communities:home', permanent=False),
        name="communities_redirect"
    ),
    path(
        "communities/manage/",
        RedirectView.as_view(pattern_name='communities:manage', permanent=False),
        name="communities_manage_redirect"
    ),

    # MANA redirects
    path(
        "mana/",
        RedirectView.as_view(pattern_name='mana:home', permanent=False),
        name="mana_redirect"
    ),
    path(
        "mana/manage-assessments/",
        RedirectView.as_view(pattern_name='mana:manage_assessments', permanent=False),
        name="mana_assessments_redirect"
    ),

    # Coordination redirects
    path(
        "coordination/",
        RedirectView.as_view(pattern_name='coordination:home', permanent=False),
        name="coordination_redirect"
    ),

    # Recommendations redirects
    path(
        "recommendations/",
        RedirectView.as_view(pattern_name='recommendations:home', permanent=False),
        name="recommendations_redirect"
    ),
]
```

**Option 2: Custom Redirect Middleware (Advanced)**

```python
# common/middleware/url_redirects.py

import logging
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

logger = logging.getLogger(__name__)

class URLRefactoringRedirectMiddleware:
    """
    Middleware to handle redirects from old URL patterns to new namespaced URLs.

    This is a temporary migration tool and should be removed after the
    transition period (2 months after deployment).
    """

    # Mapping of old URL patterns to new namespace:name
    REDIRECT_MAP = {
        '/communities/': 'communities:home',
        '/mana/': 'mana:home',
        '/coordination/': 'coordination:home',
        '/recommendations/': 'recommendations:home',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request path matches old URL pattern
        for old_path, new_name in self.REDIRECT_MAP.items():
            if request.path.startswith(old_path):
                try:
                    new_url = reverse(new_name)
                    logger.info(f"Redirecting {old_path} → {new_url}")
                    return redirect(new_url, permanent=False)
                except NoReverseMatch:
                    logger.warning(f"Could not reverse {new_name}")

        response = self.get_response(request)
        return response
```

---

## Testing Strategy

### URL Resolution Tests

**Create: tests/test_url_namespaces.py**

```python
"""
URL Namespace Resolution Tests

Verifies that all URL patterns resolve correctly after refactoring.
"""

from django.test import TestCase
from django.urls import reverse, NoReverseMatch


class URLNamespaceTests(TestCase):
    """Test that all URL namespaces resolve correctly"""

    def test_communities_namespace_exists(self):
        """Communities namespace is properly configured"""
        try:
            url = reverse('communities:home')
            self.assertTrue(url.startswith('/communities'))
        except NoReverseMatch:
            self.fail("communities:home namespace not found")

    def test_mana_namespace_exists(self):
        """MANA namespace is properly configured"""
        try:
            url = reverse('mana:home')
            self.assertTrue(url.startswith('/mana'))
        except NoReverseMatch:
            self.fail("mana:home namespace not found")

    def test_coordination_namespace_exists(self):
        """Coordination namespace is properly configured"""
        try:
            url = reverse('coordination:home')
            self.assertTrue(url.startswith('/coordination'))
        except NoReverseMatch:
            self.fail("coordination:home namespace not found")

    def test_recommendations_namespace_exists(self):
        """Recommendations namespace is properly configured"""
        try:
            url = reverse('recommendations:home')
            self.assertIsNotNone(url)
        except NoReverseMatch:
            self.fail("recommendations:home namespace not found")

    def test_common_namespace_reduced(self):
        """Common namespace contains only core functionality"""
        # Should exist
        self.assertIsNotNone(reverse('common:dashboard'))
        self.assertIsNotNone(reverse('common:login'))
        self.assertIsNotNone(reverse('common:logout'))

        # Should NOT exist (moved to modules)
        with self.assertRaises(NoReverseMatch):
            reverse('common:communities_home')
        with self.assertRaises(NoReverseMatch):
            reverse('common:mana_home')
        with self.assertRaises(NoReverseMatch):
            reverse('common:coordination_home')


class URLParameterTests(TestCase):
    """Test URLs with parameters resolve correctly"""

    def test_communities_detail_with_pk(self):
        """Community detail URLs accept pk parameter"""
        url = reverse('communities:detail', kwargs={'pk': 1})
        self.assertEqual(url, '/communities/barangay/1/')

    def test_mana_assessment_detail_with_uuid(self):
        """MANA assessment URLs accept UUID parameter"""
        import uuid
        test_uuid = uuid.uuid4()
        url = reverse('mana:assessment_detail', kwargs={'pk': test_uuid})
        self.assertIn(str(test_uuid), url)

    def test_coordination_organization_with_uuid(self):
        """Coordination organization URLs accept UUID parameter"""
        import uuid
        test_uuid = uuid.uuid4()
        url = reverse('coordination:organization_detail', kwargs={'organization_id': test_uuid})
        self.assertIn(str(test_uuid), url)
```

### Backward Compatibility Tests

**Add to: tests/test_url_backwards_compatibility.py**

```python
"""
Backward Compatibility Tests

Ensures old URL patterns redirect correctly to new namespaces.
"""

from django.test import TestCase, Client


class BackwardCompatibilityTests(TestCase):
    """Test backward-compatible redirects work correctly"""

    def setUp(self):
        self.client = Client()

    def test_old_communities_url_redirects(self):
        """Old /communities/ URL redirects to new namespace"""
        response = self.client.get('/communities/')
        # Should redirect (302) to new URL
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/communities'))

    def test_old_mana_url_redirects(self):
        """Old /mana/ URL redirects to new namespace"""
        response = self.client.get('/mana/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/mana'))

    def test_old_coordination_url_redirects(self):
        """Old /coordination/ URL redirects to new namespace"""
        response = self.client.get('/coordination/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/coordination'))

    def test_redirects_are_temporary(self):
        """Redirects use 302 (temporary) not 301 (permanent)"""
        response = self.client.get('/communities/')
        self.assertEqual(response.status_code, 302)  # Temporary redirect
        self.assertNotEqual(response.status_code, 301)  # Not permanent


class RedirectLoggingTests(TestCase):
    """Test that redirects are properly logged for monitoring"""

    def test_redirect_logs_old_url(self):
        """Redirects log the old URL for tracking"""
        with self.assertLogs('common.middleware.url_redirects', level='INFO') as logs:
            self.client.get('/communities/')
            self.assertTrue(any('/communities/' in log for log in logs.output))
```

### Integration Tests

**Add to: tests/test_url_integration.py**

```python
"""
URL Integration Tests

Tests full request/response cycle for refactored URLs.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class URLIntegrationTests(TestCase):
    """Test complete request/response cycle"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_communities_module_accessible(self):
        """Communities module is accessible via new namespace"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/communities/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'communities/home.html')

    def test_mana_module_accessible(self):
        """MANA module is accessible via new namespace"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/mana/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mana/home.html')

    def test_coordination_module_accessible(self):
        """Coordination module is accessible via new namespace"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/coordination/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coordination/home.html')

    def test_navigation_between_modules_works(self):
        """Users can navigate between modules via new URLs"""
        self.client.login(username='testuser', password='testpass123')

        # Start at dashboard
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

        # Navigate to Communities
        response = self.client.get('/communities/')
        self.assertEqual(response.status_code, 200)

        # Navigate to MANA
        response = self.client.get('/mana/')
        self.assertEqual(response.status_code, 200)

        # Navigate to Coordination
        response = self.client.get('/coordination/')
        self.assertEqual(response.status_code, 200)
```

### Test Execution Strategy

**Run tests progressively:**

```bash
# Step 1: Test URL resolution
pytest tests/test_url_namespaces.py -v

# Step 2: Test backward compatibility
pytest tests/test_url_backwards_compatibility.py -v

# Step 3: Test integration
pytest tests/test_url_integration.py -v

# Step 4: Run full test suite
pytest -v

# Step 5: Check test coverage
coverage run -m pytest
coverage report
coverage html  # Generate HTML report
```

---

## Success Criteria

### Quantitative Metrics

- [ ] **common/urls.py reduced from 847 lines to <200 lines** (76% reduction)
- [ ] **common/views.py reduced from 2,266 lines to <500 lines** (78% reduction)
- [ ] **All 898 template references updated** (100% migration)
- [ ] **4 module urls.py files created/expanded** (communities, mana, coordination, recommendations)
- [ ] **4 module views.py files created** with proper separation
- [ ] **All tests passing** (99%+ pass rate maintained)
- [ ] **Zero broken links** (manual verification)
- [ ] **<100ms URL resolution overhead** (performance test)

### Qualitative Metrics

- [ ] **Clean module boundaries** - Each app manages own routing
- [ ] **Proper URL namespacing** - Module context clear from namespace
- [ ] **BMMS-ready architecture** - Foundation for multi-tenant routing
- [ ] **Maintainable codebase** - Easy to add new modules
- [ ] **Developer-friendly** - Clear conventions documented

### Acceptance Tests

- [ ] **Manual Testing Checklist:**
  - [ ] All module homepages load correctly
  - [ ] CRUD operations work in each module
  - [ ] Navigation menus use correct URLs
  - [ ] Forms submit to correct endpoints
  - [ ] Redirects work for old bookmarks
  - [ ] No 404 errors when clicking links
  - [ ] User authentication flows work
  - [ ] Permission-based redirects work

- [ ] **Code Review Checklist:**
  - [ ] No `common:module_*` references remain in templates
  - [ ] All views import from correct modules
  - [ ] URL patterns follow naming conventions
  - [ ] Redirect middleware properly configured
  - [ ] Deprecation warnings in place
  - [ ] Documentation updated

- [ ] **Performance Checklist:**
  - [ ] Page load times unchanged or improved
  - [ ] URL resolution performance acceptable
  - [ ] No N+1 query issues introduced
  - [ ] Redirect overhead minimal

---

## Rollback Plan

### If Issues Found During Implementation

**Rollback Steps:**

1. **Stop Deployment**
   ```bash
   # Revert to previous commit
   git checkout main
   git log --oneline -10  # Find commit before refactoring
   git checkout <previous-commit-hash>
   ```

2. **Restore Original Files**
   ```bash
   # Restore from backup (if created)
   cp common/urls.py.backup common/urls.py
   cp common/views.py.backup common/views.py
   ```

3. **Restart Development Server**
   ```bash
   cd src
   ./manage.py runserver
   ```

4. **Verify System Functional**
   - Test all module homepages
   - Verify CRUD operations
   - Check user authentication

### If Issues Found After Deployment

**Mitigation Steps:**

1. **Activate Backward-Compatible Redirects**
   - Ensure redirect middleware is enabled
   - Verify redirect patterns cover all old URLs
   - Monitor redirect logs for uncaught patterns

2. **Hot-Fix Critical Issues**
   ```bash
   # Create hotfix branch
   git checkout -b hotfix/url-refactoring-fixes

   # Fix critical issues
   # ... make fixes ...

   # Deploy hotfix
   git commit -m "Hotfix: URL refactoring issues"
   git push origin hotfix/url-refactoring-fixes
   ```

3. **Add Missing Redirects**
   ```python
   # common/urls.py - Add any missing redirects
   path("missing-pattern/", RedirectView.as_view(
       pattern_name='correct:namespace',
       permanent=False
   ))
   ```

4. **Communicate with Users**
   - Notify users of temporary issues
   - Provide clear instructions for workarounds
   - Set expected resolution timeline

### Complete Rollback (Last Resort)

**If refactoring causes critical system failure:**

```bash
# 1. Revert all changes
git revert <refactoring-commit-range> --no-commit
git commit -m "ROLLBACK: Phase 0 URL refactoring"

# 2. Deploy reverted code immediately
git push origin main

# 3. Restart application
./scripts/restart_server.sh

# 4. Verify system restored
./scripts/health_check.sh

# 5. Document issues for future attempt
# Create: docs/plans/bmms/prebmms/phase_0_rollback_report.md
```

---

## Dependencies & Prerequisites

### Prerequisites

- [ ] **Git branch created:** `feature/phase-0-url-refactoring`
- [ ] **Database backup:** Created before starting
- [ ] **Virtual environment:** Active and up-to-date
- [ ] **All tests passing:** 99%+ baseline pass rate
- [ ] **Code review:** Architecture team approval
- [ ] **Documentation:** CLAUDE.md reviewed

### Dependencies

**Phase 0 has NO dependencies** - This is the foundation for all Pre-BMMS work.

**What depends on Phase 0:**
- Phase 1: Planning Module
- Phase 2: Budgeting Module
- All future module additions

---

## Timeline & Effort Estimate

### Task Breakdown by Effort

| Task | Complexity | Estimated Effort |
|------|-----------|------------------|
| Step 1: Audit URL Patterns | Simple | Simple |
| Step 2: Create/Update URL Files | Moderate | Moderate |
| Step 3: Move Views to Apps | Complex | Complex |
| Step 4: Update Template References | Very Complex | Very Complex |
| Step 5: Add Redirects | Simple | Simple |
| Step 6: Update Tests | Moderate | Moderate |
| Step 7: Documentation | Simple | Simple |
| Step 8: Verification & Cleanup | Moderate | Moderate |

**Total Effort:** Complexity: Moderate

**Critical Path:**
1. Audit → Create URLs → Move Views → Update Templates → Test

**Recommended Approach:**
- **Incremental Migration:** Complete one module at a time
- **Test After Each Module:** Ensure stability before moving to next
- **Parallel Work:** URL creation and view migration can happen simultaneously

---

## Post-Implementation

### Monitoring

**Track for 2 weeks after deployment:**

1. **Redirect Usage**
   - Monitor redirect logs
   - Identify high-traffic old URLs
   - Consider permanent redirects for heavily-used patterns

2. **Error Rates**
   - Monitor 404 errors
   - Track NoReverseMatch exceptions
   - Fix any missed URL references

3. **Performance**
   - Track page load times
   - Monitor URL resolution performance
   - Check for N+1 query issues

### Deprecation Timeline

**Removal Schedule for Backward-Compatible Redirects:**

| Date | Action |
|------|--------|
| 2025-10-13 | Phase 0 completion |
| 2025-11-13 | Review redirect usage (30 days) |
| 2025-12-13 | Remove redirects (60 days) |

**Before Removal:**
- [ ] Verify <1% traffic on redirects
- [ ] Communicate deprecation to users
- [ ] Update bookmarks and documentation
- [ ] Search for any hardcoded old URLs in external systems

### Documentation Updates

**Update after completion:**

- [ ] CLAUDE.md - Add URL namespace guidelines
- [ ] docs/development/README.md - Document URL conventions
- [ ] docs/README.md - Update development guides
- [ ] API documentation - Update endpoint examples
- [ ] User guides - Update screenshots and instructions

---

## Conclusion

Phase 0: URL Refactoring is a **critical foundation** for Pre-BMMS development. By completing this refactoring FIRST, we:

1. ✅ **Establish clean module boundaries** for future development
2. ✅ **Enable proper URL namespacing** for BMMS multi-tenancy
3. ✅ **Reduce technical debt** in common app
4. ✅ **Improve maintainability** for ongoing development
5. ✅ **Create scalable architecture** for 44 MOA support

**Next Steps After Completion:**

1. ✅ Merge Phase 0 to main branch
2. ✅ Begin Phase 1: Planning Module (clean foundation ready)
3. ✅ Continue Pre-BMMS feature development with proper architecture

---

**Document Status:** ✅ Ready for Implementation
**Approval Required:** Architecture Team
**Start Date:** TBD
**Target Completion:** TBD (Complexity: Moderate)

**Related Documents:**
- [Pre-BMMS Feature Analysis](../PRE_BMMS_FEATURE_ANALYSIS.md)
- [BMMS Comprehensive Plan](../../BANGSAMORO_BUDGET_SYSTEM_COMPREHENSIVE_PLAN.md)
- [OBCMS URL Standards](../../../development/README.md#url-patterns)
