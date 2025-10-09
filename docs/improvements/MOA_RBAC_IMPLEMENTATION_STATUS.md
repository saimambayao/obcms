# MOA RBAC Implementation Status

**Status:** Design Complete - Ready for Implementation
**Priority:** CRITICAL
**Last Updated:** 2025-10-08

---

## Quick Links

- **Main Design Doc:** [MOA_RBAC_DESIGN.md](MOA_RBAC_DESIGN.md)
- **Separation Analysis:** [MOA_OOBC_SEPARATION_ANALYSIS.md](MOA_OOBC_SEPARATION_ANALYSIS.md)

---

## Implementation Progress

### Phase 1: Foundation (Database Schema) - NOT STARTED

**Priority:** CRITICAL
**Complexity:** Moderate
**Dependencies:** None

- [ ] Migration: Add `moa_organization` FK to User model
- [ ] Data Migration: Backfill from `organization` CharField
- [ ] Update User model with permission methods
- [ ] Test migrations in development
- [ ] Verify backfill accuracy

**Status:** 0% Complete

**Blockers:** None - Ready to start

---

### Phase 2: Permission Utilities - NOT STARTED

**Priority:** CRITICAL
**Complexity:** Moderate
**Dependencies:** Phase 1 complete

- [ ] Create `src/common/permissions/` module structure
- [ ] Implement `decorators.py` (5 decorators)
- [ ] Implement `mixins.py` (3 mixins)
- [ ] Implement `templatetags/moa_permissions.py` (8 tags)
- [ ] Write unit tests (100% coverage target)

**Status:** 0% Complete

**Blockers:** Waiting for Phase 1

---

### Phase 3: View Protection - NOT STARTED

**Priority:** HIGH
**Complexity:** Moderate
**Dependencies:** Phase 2 complete

#### 3.1 Communities Module (View-Only)
- [ ] Apply `@moa_view_only` to community views
- [ ] Test: MOA can view, cannot edit

#### 3.2 Coordination Module (Edit Own Organization)
- [ ] Apply `@moa_can_edit_organization` decorator
- [ ] Apply `MOAOrganizationAccessMixin` to CBVs
- [ ] Test: MOA can edit own, cannot edit others

#### 3.3 Monitoring Module (Edit Own PPAs)
- [ ] Apply `@moa_can_edit_ppa` decorator
- [ ] Apply `MOAPPAAccessMixin` to CBVs
- [ ] Use `MOAFilteredQuerySetMixin` for list views
- [ ] Test: MOA can CRUD own PPAs only

#### 3.4 MANA Module (No Access)
- [ ] Apply `@moa_no_access` to all MANA views
- [ ] Test: MOA gets 403 Forbidden

#### 3.5 Common Module (Work Items)
- [ ] Apply `@moa_can_edit_work_item` decorator
- [ ] Filter work items by related PPA
- [ ] Test: MOA can edit own work items only

**Status:** 0% Complete

**Blockers:** Waiting for Phase 2

---

### Phase 4: Template Updates - NOT STARTED

**Priority:** HIGH
**Complexity:** Simple
**Dependencies:** Phase 3 complete

- [ ] Update base navigation template
- [ ] Update PPA templates with permission checks
- [ ] Update organization templates
- [ ] Add permission denial messages
- [ ] Hide unauthorized UI elements

**Files to Update:**
- `src/templates/common/base.html`
- `src/templates/monitoring/ppa_detail.html`
- `src/templates/monitoring/ppa_list.html`
- `src/templates/coordination/organization_detail.html`
- `src/templates/communities/community_detail.html`

**Status:** 0% Complete

**Blockers:** Waiting for Phase 3

---

### Phase 5: Model-Level Security - NOT STARTED

**Priority:** MEDIUM
**Complexity:** Moderate
**Dependencies:** Phases 1-4 complete

- [ ] Add validation to `MonitoringEntry.save()`
- [ ] Add validation to `MonitoringEntry.delete()`
- [ ] Add validation to `Organization.save()`
- [ ] Implement pre-save signals for enforcement

**Status:** 0% Complete

**Blockers:** Waiting for Phase 4

---

### Phase 6: Testing & Verification - NOT STARTED

**Priority:** HIGH
**Complexity:** Moderate
**Dependencies:** Phases 1-5 complete

- [ ] Unit tests (permission utilities) - Target: 100% coverage
- [ ] Integration tests (complete workflows)
- [ ] Security tests (privilege escalation attempts)
- [ ] Manual testing (user acceptance)
- [ ] Performance testing (QuerySet filtering overhead)

**Status:** 0% Complete

**Blockers:** Waiting for Phase 5

---

### Phase 7: Documentation & Training - NOT STARTED

**Priority:** MEDIUM
**Complexity:** Simple
**Dependencies:** Phases 1-6 complete

- [ ] MOA User Guide
- [ ] Admin Guide (managing MOA accounts)
- [ ] Developer Guide (extending RBAC)
- [ ] Training materials for MOA focal users
- [ ] Video tutorials (optional)

**Status:** 0% Complete

**Blockers:** Waiting for Phase 6

---

## Overall Progress: 0% Complete

**Total Tasks:** 47
**Completed:** 0
**In Progress:** 0
**Blocked:** 0
**Not Started:** 47

---

## Key Decisions Made

### ✅ Architectural Decisions

1. **User-Organization Linking:** Add `moa_organization` ForeignKey to User model (requires migration)
   - **Alternative Rejected:** Use CharField matching (fragile, error-prone)

2. **Permission Enforcement:** Defense-in-depth (view, model, template layers)
   - **Rationale:** Security best practice - fail closed

3. **QuerySet Filtering:** Auto-filter by default using mixins
   - **Rationale:** Prevent data leakage, reduce developer burden

4. **Access Control Model:**
   - Tier 1: View-only (OBC communities, policy recommendations)
   - Tier 2: Full CRUD (own organization, own PPAs, work items)
   - Tier 3: No access (MANA, other MOAs, admin)

---

## Critical Implementation Notes

### Database Migration

**IMPORTANT:** The `moa_organization` backfill migration matches users to organizations by **name** (case-insensitive). This may result in **unmatched users** if:
- Organization name in `User.organization` doesn't match `Organization.name`
- Organization doesn't exist yet
- Typos in organization names

**Action Required:** After running migrations, review unmatched users and manually assign `moa_organization`.

### Security Considerations

1. **Always check permissions at ALL three layers:**
   - View (decorators)
   - Model (validation)
   - Template (conditional rendering)

2. **QuerySet filtering is NOT sufficient security:**
   - Developers might forget to apply filters
   - Direct model access bypasses filters
   - Always validate in model methods

3. **Audit logging is REQUIRED:**
   - Log all MOA user actions
   - Log permission denials
   - Review logs regularly for suspicious activity

---

## Testing Requirements

### Unit Test Coverage Targets

- **Permission decorators:** 100% coverage
- **Permission mixins:** 100% coverage
- **User model methods:** 100% coverage
- **Template tags:** 100% coverage

### Integration Test Scenarios

1. **MOA user can view OBC communities** (GET succeeds)
2. **MOA user cannot create OBC communities** (POST returns 403)
3. **MOA user can edit own organization** (PUT succeeds)
4. **MOA user cannot edit other MOA organization** (PUT returns 403)
5. **MOA user can create PPA** (POST succeeds)
6. **MOA user can edit own PPA** (PUT succeeds)
7. **MOA user cannot edit other MOA PPA** (PUT returns 403)
8. **MOA user cannot access MANA** (GET returns 403)
9. **MOA user can view policy recommendations for their MOA**
10. **MOA user cannot view policy recommendations for other MOAs**

### Security Test Scenarios

1. **Privilege escalation attempt:** MOA user tries to set `is_superuser=True`
2. **Organization hijacking:** MOA user tries to change `moa_organization`
3. **Cross-MOA access:** MOA user tries to edit PPA with direct URL manipulation
4. **User type escalation:** MOA user tries to change `user_type` to `oobc_staff`
5. **CSRF bypass attempt:** Submit form without CSRF token
6. **Session hijacking:** Test session security measures

---

## Deployment Checklist

### Pre-Deployment

- [ ] All migrations tested in staging
- [ ] Backfill script validated
- [ ] Unit tests: 100% passing
- [ ] Integration tests: 100% passing
- [ ] Security tests: 100% passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Training materials prepared

### Deployment Day

- [ ] **Backup production database** (CRITICAL)
- [ ] Apply migrations (0031, 0032)
- [ ] Verify `moa_organization` populated
- [ ] Deploy codebase
- [ ] Restart application servers
- [ ] Run smoke tests
- [ ] Monitor error logs (24 hours)

### Post-Deployment

- [ ] Verify MOA users can access PPAs
- [ ] Verify MOA users blocked from MANA
- [ ] Verify MOA users can edit organization
- [ ] Collect user feedback
- [ ] Address any issues
- [ ] Document lessons learned

---

## Known Issues & Risks

### Issue 1: Unmatched Users in Backfill

**Risk:** MEDIUM
**Impact:** MOA users won't have `moa_organization` assigned
**Mitigation:**
- Manual review after migration
- Admin interface to assign organizations
- User notification to contact admin

### Issue 2: Performance Overhead from QuerySet Filtering

**Risk:** LOW
**Impact:** Additional database queries for permission checks
**Mitigation:**
- Use `select_related('moa_organization')` in views
- Add database indexes on `implementing_moa`
- Monitor query performance in production

### Issue 3: UI Confusion for MOA Users

**Risk:** LOW
**Impact:** MOA users try to access unauthorized features
**Mitigation:**
- Clear permission denial messages
- Hide unauthorized UI elements
- Provide MOA user guide
- Training sessions

---

## Next Actions (Priority Order)

1. **Review design document** with OOBC stakeholders
2. **Obtain approval** for database migration
3. **Create development branch:** `feature/moa-rbac`
4. **Implement Phase 1:** Database migrations
5. **Test Phase 1** thoroughly before proceeding
6. **Proceed through phases sequentially**
7. **Security audit** before production deployment

---

## Contact & Support

**Implementation Lead:** TBD
**Security Review:** TBD
**Stakeholder Approval:** OOBC Director

**Questions?** Contact: dev@oobc.gov.ph

---

**Last Updated:** 2025-10-08
**Next Review:** After Phase 1 completion
