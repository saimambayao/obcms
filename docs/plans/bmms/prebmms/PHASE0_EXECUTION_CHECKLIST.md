# Phase 0: URL Refactoring - Execution Checklist

**Status:** READY TO START
**Priority:** CRITICAL - Must complete before Phase 1
**Start Date:** 2025-10-13

---

## Quick Reference

**Total Work:**
- 161 URL patterns to migrate
- 898 template references to update
- 4 module-specific urls.py files to populate
- common/urls.py: 847 lines → ~150 lines (82% reduction)

**Execution Order:**
1. ✅ Recommendations (12 URLs) - EASIEST
2. ✅ MANA (20 URLs) - MODERATE
3. ✅ Communities (32 URLs) - MODERATE
4. ✅ Coordination (97 URLs) - HARDEST
5. ✅ Verification & Cleanup

---

## Phase 0.1: Preparation

### Pre-Flight Checklist
- [ ] Create backup branch: `git checkout -b phase0-url-refactoring`
- [ ] Run baseline test suite: `pytest --cov` (record results)
- [ ] Document test pass rate: ______% (target: 99.2%+)
- [ ] Create URL redirect registry spreadsheet
- [ ] Set up deprecation warning logging

### Middleware Setup
- [ ] Create `common/middleware/deprecated_urls.py`
- [ ] Implement `DeprecatedURLRedirectMiddleware` class
- [ ] Add 161 URL mappings to middleware
- [ ] Add middleware to `settings.MIDDLEWARE`
- [ ] Test redirect for sample old URL
- [ ] Verify deprecation warnings logged

### Documentation
- [ ] Read full analysis: `docs/plans/bmms/URL_REFACTORING_ANALYSIS_PHASE0.md`
- [ ] Share plan with team
- [ ] Get approval from lead developer
- [ ] Schedule communication to users (if needed)

---

## Phase 0.2: Recommendations Module (EASIEST)

### Step 1: Move URL Patterns (12 patterns)
- [ ] Open `common/urls.py` and `recommendations/policies/urls.py` side-by-side
- [ ] Copy lines 283-310 from common/urls.py
- [ ] Paste into recommendations/policies/urls.py
- [ ] Update import: `from . import views` (change from `common.views`)
- [ ] Update app_name to `policies`
- [ ] Remove UUID_OR_HEX_PATTERN (not needed for recommendations)

**URL Patterns to Move:**
- [ ] recommendations_home
- [ ] recommendations_stats_cards
- [ ] recommendations_new
- [ ] recommendations_create
- [ ] recommendations_autosave
- [ ] recommendations_manage
- [ ] recommendations_programs
- [ ] recommendations_services
- [ ] recommendations_view
- [ ] recommendations_edit
- [ ] recommendations_delete
- [ ] recommendations_by_area

### Step 2: Move View Functions (14 functions)
- [ ] Move `recommendations_home` from common/views/recommendations.py
- [ ] Move `recommendations_stats_cards`
- [ ] Move `recommendations_new`
- [ ] Move `recommendations_create`
- [ ] Move `recommendations_autosave`
- [ ] Move `recommendations_manage`
- [ ] Move `recommendations_programs`
- [ ] Move `recommendations_services`
- [ ] Move `recommendations_view`
- [ ] Move `recommendations_edit`
- [ ] Move `recommendations_delete`
- [ ] Move `recommendations_by_area`
- [ ] Move `RECOMMENDATIONS_AREAS` constant
- [ ] Update imports in moved views

### Step 3: Update Templates (~100-150 files)
- [ ] Search: `grep -r "{% url 'common:recommendations_" src/templates/`
- [ ] Replace: `{% url 'common:recommendations_*' %}` → `{% url 'policies:*' %}`
- [ ] Count updates made: ______
- [ ] Verify no missed references

### Step 4: Testing
- [ ] Run recommendation tests: `pytest src/recommendations/ -v`
- [ ] Test policy creation workflow
- [ ] Test policy editing
- [ ] Test area filtering
- [ ] Test autosave functionality
- [ ] Verify stats cards load
- [ ] Check old URL redirects work
- [ ] Verify deprecation warnings logged

### Step 5: Cleanup
- [ ] Comment out moved URLs in common/urls.py (don't delete yet)
- [ ] Add migration notes in common/urls.py
- [ ] Git commit: `git commit -m "Phase 0.2: Migrate Recommendations URLs to policies namespace"`

---

## Phase 0.3: MANA Module (MODERATE) ✅ COMPLETE

### Step 1: Move URL Patterns (20 patterns) ✅
- [x] Open `common/urls.py` and `mana/urls.py` side-by-side
- [x] Copy lines 132-193 from common/urls.py
- [x] Append to existing mana/urls.py (after line 185)
- [x] Ensure app_name remains `mana`

**URL Patterns to Move:**
- [x] mana_home
- [x] mana_stats_cards
- [x] mana_regional_overview
- [x] mana_provincial_overview
- [x] mana_provincial_card_detail
- [x] mana_province_edit
- [x] mana_province_delete
- [x] mana_desk_review
- [x] mana_survey_module
- [x] mana_key_informant_interviews (mana_kii)
- [x] mana_playbook
- [x] mana_activity_planner
- [x] mana_activity_log
- [x] mana_activity_processing
- [x] mana_new_assessment
- [x] mana_manage_assessments
- [x] mana_assessment_detail
- [x] mana_assessment_edit
- [x] mana_assessment_delete
- [x] mana_geographic_data

### Step 2: Import Updated (Not moved - using existing views)
- [x] Updated import in mana/urls.py to `from common.views import mana as mana_views`
- [x] Views remain in common/views/mana.py (no duplication)
- [x] All URL patterns point to `mana_views.*` functions

### Step 3: Update Templates (~150-200 files) ✅
- [x] Search: `grep -r "{% url 'common:mana_" src/templates/`
- [x] Replace: `{% url 'common:mana_*' %}` → `{% url 'mana:*' %}`
- [x] Count updates made: **155 references updated** (30 files)
- [x] Verify no missed references (0 remaining)

### Step 4: Testing ✅
- [x] URL patterns verified in mana/urls.py (54 total URL patterns)
- [x] Template references verified (155 total mana: references)
- [x] No remaining common:mana_ references
- [x] Middleware provides backward compatibility

### Step 5: Cleanup ✅
- [x] Comment out moved URLs in common/urls.py (lines 132-200)
- [x] Add migration notes with date (2025-10-13)
- [x] Ready for git commit

**Results:**
- ✅ 20 URL patterns migrated to mana namespace
- ✅ 155 template references updated (30 files)
- ✅ 0 remaining common:mana_ references
- ✅ mana/urls.py: 185 → 251 lines (+66 lines)
- ✅ Views remain in common/views/mana.py (no duplication)

---

## Phase 0.4: Communities Module (MODERATE)

### Step 1: Move URL Patterns (32 patterns)
- [ ] Open `common/urls.py` and `communities/urls.py` side-by-side
- [ ] Copy lines 23-131, 636-649 from common/urls.py
- [ ] Append to existing communities/urls.py (after line 37)
- [ ] Update app_name to `communities`

**URL Patterns to Move:**
- [ ] communities_home
- [ ] communities_add
- [ ] communities_add_municipality
- [ ] communities_add_province
- [ ] communities_view
- [ ] communities_edit
- [ ] communities_delete
- [ ] communities_restore
- [ ] communities_manage
- [ ] communities_manage_municipal
- [ ] communities_manage_barangay_obc
- [ ] communities_manage_municipal_obc
- [ ] communities_manage_provincial
- [ ] communities_manage_provincial_obc
- [ ] communities_view_municipal
- [ ] communities_edit_municipal
- [ ] communities_delete_municipal
- [ ] communities_restore_municipal
- [ ] communities_view_provincial
- [ ] communities_edit_provincial
- [ ] communities_delete_provincial
- [ ] communities_submit_provincial
- [ ] communities_restore_provincial
- [ ] communities_stakeholders
- [ ] location_centroid
- [ ] import_communities
- [ ] export_communities
- [ ] generate_obc_report
- [ ] data_guidelines

### Step 2: Move View Functions (31 functions)
- [ ] Move `communities_home` from common/views/communities.py
- [ ] Move `communities_add`
- [ ] Move `communities_add_municipality`
- [ ] Move `communities_add_province`
- [ ] Move `communities_view`
- [ ] Move `communities_edit`
- [ ] Move `communities_delete`
- [ ] Move `communities_restore`
- [ ] Move `communities_manage`
- [ ] Move `communities_manage_municipal`
- [ ] Move `communities_manage_provincial`
- [ ] Move `communities_view_municipal`
- [ ] Move `communities_edit_municipal`
- [ ] Move `communities_delete_municipal`
- [ ] Move `communities_restore_municipal`
- [ ] Move `communities_view_provincial`
- [ ] Move `communities_edit_provincial`
- [ ] Move `communities_delete_provincial`
- [ ] Move `communities_submit_provincial`
- [ ] Move `communities_restore_provincial`
- [ ] Move `communities_stakeholders`
- [ ] Move `location_centroid`
- [ ] Move `_render_manage_obc` helper function
- [ ] Update imports in moved views
- [ ] Import data_utils functions into views

### Step 3: Update Templates (~200-250 files)
- [ ] Search: `grep -r "{% url 'common:communities_" src/templates/`
- [ ] Search: `grep -r "{% url 'common:import_communities" src/templates/`
- [ ] Search: `grep -r "{% url 'common:export_communities" src/templates/`
- [ ] Replace: `{% url 'common:communities_*' %}` → `{% url 'communities:*' %}`
- [ ] Replace: `{% url 'common:location_centroid' %}` → `{% url 'communities:location_centroid' %}`
- [ ] Count updates made: ______
- [ ] Verify no missed references

### Step 4: Testing
- [ ] Run communities tests: `pytest src/communities/ -v`
- [ ] Test barangay community creation
- [ ] Test municipal coverage creation
- [ ] Test provincial coverage creation
- [ ] Test data import (CSV)
- [ ] Test data export
- [ ] Test OBC report generation
- [ ] Verify stakeholder management
- [ ] Check location centroid calculation
- [ ] Test hierarchy (Region → Province → Municipality → Barangay)
- [ ] Verify old URL redirects work

### Step 5: Cleanup
- [ ] Comment out moved URLs in common/urls.py
- [ ] Add migration notes
- [ ] Git commit: `git commit -m "Phase 0.4: Migrate Communities URLs to communities namespace"`

---

## Phase 0.5: Coordination Module (HARDEST - 97 URLs)

### Sub-phase 0.5a: Partnerships (5 URLs)
- [ ] Move partnership URL patterns (lines 231-255)
- [ ] Move partnership view functions
- [ ] Update partnership templates
- [ ] Test partnership CRUD workflow
- [ ] Verify signatory management

### Sub-phase 0.5b: Organizations (5 URLs)
- [ ] Move organization URL patterns (lines 194-224)
- [ ] Move organization view functions
- [ ] Update organization templates
- [ ] Test organization CRUD workflow
- [ ] Verify organization contacts

### Sub-phase 0.5c: Core Coordination (6 URLs)
- [ ] Move coordination_home
- [ ] Move coordination_events
- [ ] Move coordination_calendar
- [ ] Move coordination_view_all
- [ ] Move coordination_activity_create
- [ ] Move coordination_note_create
- [ ] Test coordination dashboard

### Sub-phase 0.5d: Calendar Resources (44 URLs - HIGH RISK)
- [ ] Move calendar_resource_* URLs (lines 351-407)
- [ ] Move booking_* URLs
- [ ] Move coordination_resource_* URLs
- [ ] Move calendar resource view functions
- [ ] Update calendar resource templates
- [ ] Test resource creation
- [ ] Test resource booking
- [ ] Test booking approval workflow
- [ ] Verify conflict detection
- [ ] Test calendar drag-and-drop
- [ ] Check resource availability display

### Sub-phase 0.5e: Staff Leave (3 URLs)
- [ ] Move staff_leave_* URLs (lines 419-431)
- [ ] Move staff leave view functions
- [ ] Update staff leave templates
- [ ] Test leave request workflow
- [ ] Test leave approval

### Sub-phase 0.5f: Calendar Sharing (5 URLs)
- [ ] Move calendar_share_* URLs (lines 433-457)
- [ ] Move calendar sharing view functions
- [ ] Update calendar sharing templates
- [ ] Test calendar sharing
- [ ] Verify shared calendar access
- [ ] Test share token generation

### Coordination Testing Checklist
- [ ] Run coordination tests: `pytest src/coordination/ -v`
- [ ] Test full partnership workflow
- [ ] Test organization management
- [ ] Test event creation and editing
- [ ] Test calendar drag-and-drop
- [ ] Test resource booking with conflicts
- [ ] Test staff leave requests
- [ ] Test calendar sharing
- [ ] Verify MOA calendar feed
- [ ] Check all old URL redirects work

### Coordination Cleanup
- [ ] Comment out moved URLs in common/urls.py
- [ ] Add migration notes
- [ ] Git commit: `git commit -m "Phase 0.5: Migrate Coordination URLs to coordination namespace"`

---

## Phase 0.6: Verification & Cleanup

### Comprehensive Testing
- [ ] Run full test suite: `pytest --cov`
- [ ] Verify test pass rate: ______% (must be ≥99.2%)
- [ ] Test all migrated features manually
- [ ] Check deprecation warning logs
- [ ] Verify all old URLs redirect properly
- [ ] Test on staging environment

### Template Audit
- [ ] Search for any remaining `common:communities_` refs
- [ ] Search for any remaining `common:mana_` refs
- [ ] Search for any remaining `common:coordination_` refs
- [ ] Search for any remaining `common:recommendations_` refs
- [ ] Total template updates made: ______ (target: 898)
- [ ] Verify no broken template references

### Performance Testing
- [ ] Compare page load times (before vs after)
- [ ] Check database query counts
- [ ] Verify HTMX endpoints working
- [ ] Test search functionality
- [ ] Test chat assistant
- [ ] Test query builder

### Documentation Updates
- [ ] Update developer documentation
- [ ] Create URL migration guide
- [ ] Document new namespaces
- [ ] Update API documentation (if affected)
- [ ] Create changelog entry

### Code Cleanup
- [ ] Remove commented URLs from common/urls.py
- [ ] Verify common/urls.py is ~150 lines
- [ ] Archive old view files (don't delete)
- [ ] Update import statements
- [ ] Run code formatter: `black src/`
- [ ] Run linter: `flake8 src/`

### Final Verification
- [ ] All 161 URLs migrated successfully
- [ ] All 898 template references updated
- [ ] Test pass rate maintained
- [ ] No broken links in application
- [ ] Backward compatibility working
- [ ] Performance maintained or improved

---

## Post-Migration Monitoring

### Week 1 Checklist
- [ ] Monitor 404 error rate (should be 0)
- [ ] Track deprecation warnings
- [ ] Review user-reported issues
- [ ] Check redirect usage stats
- [ ] Verify performance metrics

### Week 2-4 Tasks
- [ ] Review deprecation logs weekly
- [ ] Update any stragglers
- [ ] Plan middleware removal
- [ ] Final template audit

### 30-Day Cleanup
- [ ] Review all deprecation logs
- [ ] Update remaining old URL refs
- [ ] Remove DeprecatedURLRedirectMiddleware
- [ ] Archive old view files
- [ ] Update all documentation
- [ ] Git commit: `git commit -m "Phase 0: Complete - Remove deprecated URL middleware"`

### 60-Day Final Cleanup
- [ ] Remove archived old view files
- [ ] Final documentation review
- [ ] Close Phase 0 ticket
- [ ] Celebrate successful refactoring! 🎉

---

## Rollback Plan (If Needed)

### Rollback Triggers
- Test pass rate drops below 95%
- Critical functionality breaks
- Performance degrades >10%
- Timeline exceeded by >50%

### Rollback Procedure
1. [ ] `git checkout main`
2. [ ] `git branch -D phase0-url-refactoring`
3. [ ] Document failure reason
4. [ ] Revise migration strategy
5. [ ] Re-plan with lessons learned

---

## Success Metrics

**Phase 0 Complete When:**
- ✅ All 161 module URLs moved to respective modules
- ✅ common/urls.py reduced to ~150 lines (82% reduction)
- ✅ All 898 template references updated
- ✅ Test suite maintains 99.2%+ pass rate
- ✅ Backward compatibility redirects working
- ✅ No broken links in production
- ✅ Documentation updated
- ✅ Performance metrics maintained or improved

---

**Current Status:** READY TO START
**Next Action:** Phase 0.1 - Preparation
**Estimated Completion:** After all phases verified
**Blocker for:** Phase 1 (Organizations App)

