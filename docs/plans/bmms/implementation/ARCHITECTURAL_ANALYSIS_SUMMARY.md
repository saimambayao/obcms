# OBCMS Architectural Analysis Summary

**Quick Reference Guide for BMMS Migration**
**Date:** October 14, 2025

---

## At a Glance

| Category | Status | Priority | Impact |
|----------|--------|----------|--------|
| **Organizations Infrastructure** | ✅ **READY** | - | Foundation complete |
| **User Model Organization FK** | ❌ **NEEDS FIX** | 🔴 CRITICAL | Blocks pilot launch |
| **RBAC System Organization FKs** | ❌ **NEEDS FIX** | 🔴 CRITICAL | Permission system |
| **Model Organization Scoping** | ⚠️ **IN PROGRESS** | 🟡 HIGH | 40+ models to update |
| **Query Filtering** | ❌ **TODO** | 🟡 HIGH | All views need updates |
| **Geographic Data** | ✅ **READY** | - | No changes needed |
| **Middleware & Settings** | ✅ **READY** | - | Already configured |

---

## Critical Blockers (MUST FIX BEFORE PILOT)

### 1. User Model Organization FK ⚠️ CRITICAL

**Current:**
```python
class User(AbstractUser):
    moa_organization = ForeignKey('coordination.Organization')  # ❌ WRONG MODEL
```

**Required:**
```python
class User(AbstractUser):
    # Keep old FK for backward compatibility
    moa_organization = ForeignKey('coordination.Organization', help_text='DEPRECATED')

    # New approach: Use OrganizationMembership
    # Access via: user.organization_memberships.all()
```

**Action:** Add OrganizationMembership relationships, migrate existing users

---

### 2. RBAC Models Organization FKs ⚠️ CRITICAL

**Files to Update:**
- `src/common/rbac_models.py` - Role, Feature models
- Change all `ForeignKey('coordination.Organization')` → `ForeignKey('organizations.Organization')`

**Impact:** Permission system won't work correctly without this fix

---

### 3. Core Model Organization Scoping ⚠️ HIGH

**Priority 1 Models (CRITICAL):**
- `OBCCommunity` - Add `organization` FK
- `Assessment` - Add `organization` FK
- `PPA` - Add `implementing_moa` FK
- `StakeholderEngagement` - Add `organization` FK
- `Partnership` - Add `lead_organization` FK
- `StrategicPlan` - Add `organization` FK
- `WorkItem` - Update `organization` FK to point to organizations.Organization
- `BudgetProposal` - Add `organization` FK
- `Disbursement` - Add `organization` FK
- `ProgressReport` - Add `organization` FK

**Action:** Add nullable organization FK, migrate OOBC data, make FK required

---

### 4. Query Filtering ⚠️ HIGH

**All views need organization filtering:**
```python
# ❌ BEFORE (No filtering)
def community_list(request):
    communities = OBCCommunity.objects.all()

# ✅ AFTER (Organization-scoped)
def community_list(request):
    org = request.organization
    communities = OBCCommunity.objects.filter(organization=org)
```

**Affected Apps:**
- communities/ - All CRUD operations
- mana/ - Assessment management
- coordination/ - Stakeholder engagement
- monitoring/ - PPA tracking
- planning/ - Strategic planning
- budget_preparation/ - Budget proposals
- budget_execution/ - Disbursements

---

## Already Working (No Changes Needed)

### ✅ Organizations App (Phase 1 Complete)

**Models:**
- `Organization` - Represents 44 BARMM MOAs
- `OrganizationMembership` - User-to-organization relationships

**Features:**
- Multiple organizations per user
- Primary organization designation
- Role-based permissions
- Built-in validation

---

### ✅ OrganizationScopedModel

**File:** `src/organizations/models/scoped.py`

**Usage:**
```python
# Inherit from OrganizationScopedModel
class OBCCommunity(OrganizationScopedModel):
    name = models.CharField(max_length=200)
    # organization FK automatically added

# Queries automatically scoped:
OBCCommunity.objects.all()  # Only current org's communities

# Admin/OCM access:
OBCCommunity.all_objects.all()  # All communities across all orgs
```

---

### ✅ OrganizationContextMiddleware

**File:** `src/common/middleware/organization_context.py`

**Features:**
- Extracts organization from URL, query params, session, or user default
- Sets `request.organization` for all views
- Implements access control rules (OCM read-only, MOA isolation)

**Access Rules:**
- Superusers: All organizations
- OCM users: All organizations (read-only)
- OOBC staff: All organizations (full access)
- MOA staff: Their organization only

---

### ✅ RBAC Infrastructure

**Models:** Feature, Permission, Role, RolePermission, UserRole, UserPermission

**Features:**
- Organization-scoped roles
- Permission inheritance
- Temporary role assignments
- Direct permission grants
- Expiration support

**Status:** Fully implemented, just needs FK updates to organizations.Organization

---

### ✅ Settings & Configuration

**File:** `src/obc_management/settings/base.py`

```python
RBAC_SETTINGS = {
    'ENABLE_MULTI_TENANT': True,  # ✅ Already enabled
    'OCM_ORGANIZATION_CODE': 'ocm',
    'ALLOW_ORGANIZATION_SWITCHING': True,
}
```

---

## Migration Phases

### Phase 0: Foundation (PRE-PILOT) 🔴 CRITICAL

**Timeline:** 1-2 weeks
**Status:** NOT STARTED

**Tasks:**
1. Fix User model organization FK
2. Update RBAC models organization FKs
3. Create OOBC organization record
4. Migrate existing users and roles
5. Test: OOBC continues to function

**Deliverables:**
- ✅ User.organization points to organizations.Organization
- ✅ All RBAC models use organizations.Organization
- ✅ All existing users linked to OOBC organization
- ✅ All tests passing

---

### Phase 1: Pilot Launch 🟡 HIGH

**Timeline:** 2-4 weeks after Phase 0
**Status:** READY (awaiting Phase 0)

**Tasks:**
1. Create pilot MOA organizations (MOH, MOLE, MAFAR)
2. Add organization FK to OBCCommunity
3. Add organization FK to Assessment
4. Add organization FK to PPA
5. Update critical queries

**Deliverables:**
- ✅ 3 pilot MOAs can log in
- ✅ Pilot MOAs can create communities, assessments
- ✅ Data isolation verified (MOH ≠ MOLE ≠ MAFAR)
- ✅ OOBC data unchanged

---

### Phase 2: Expand Scoping (DURING PILOT) 🟡 HIGH

**Timeline:** 3-6 months during pilot operation
**Status:** READY (awaiting Phase 1)

**Tasks:**
1. Add organization FK to remaining models
2. Update all views with organization filtering
3. Update all APIs with organization filtering
4. Update dashboards
5. Performance optimization

**Deliverables:**
- ✅ All models organization-scoped
- ✅ All queries filtered by organization
- ✅ All APIs respect organization context
- ✅ Query performance <300ms

---

### Phase 3: Full Rollout 🟢 MEDIUM

**Timeline:** 6-12 months after successful pilot
**Status:** PLANNED

**Tasks:**
1. Create remaining 41 MOA organizations
2. Onboard MOAs in batches (8-10 per wave)
3. Train MOA staff
4. Monitor performance and data integrity
5. Scale testing

**Deliverables:**
- ✅ All 44 MOAs operational
- ✅ Performance acceptable (<500ms with 44 orgs)
- ✅ Zero cross-organization data leaks
- ✅ OOBC continues to function

---

## Risk Assessment

### 🔴 HIGH RISK (Blockers)

| Risk | Impact | Mitigation |
|------|--------|-----------|
| User model FK points to wrong org | All authentication breaks | Dual FKs during transition |
| RBAC models use wrong org FK | Permission system fails | Update all RBAC FKs, test thoroughly |
| Data migration errors | Data loss or corruption | Comprehensive backups, rollback plan |

### 🟡 MEDIUM RISK (Manageable)

| Risk | Impact | Mitigation |
|------|--------|-----------|
| 40+ models need scoping | Large codebase changes | Phased migration, extensive testing |
| Query performance degradation | Slow application | Proper indexing, query optimization |
| Cross-organization data leaks | Security breach | Thorough integration testing |

### 🟢 LOW RISK (Minor)

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Geographic data changes | Reference data issues | No changes needed |
| Settings misconfiguration | Feature flags not working | Settings already configured |
| Middleware ordering | Context not available | Already properly ordered |

---

## Quick Win Checklist

Before starting BMMS pilot:

- [ ] **Create organizations.Organization for OOBC**
- [ ] **Add User.organization_memberships support**
- [ ] **Update all RBAC model FKs**
- [ ] **Add organization FK to OBCCommunity**
- [ ] **Add organization FK to Assessment**
- [ ] **Add organization FK to PPA**
- [ ] **Update communities/views.py with org filtering**
- [ ] **Update mana/views.py with org filtering**
- [ ] **Update monitoring/views.py with org filtering**
- [ ] **Test data isolation (MOA A ≠ MOA B)**
- [ ] **Test OCM read-only access**
- [ ] **Test OOBC backward compatibility**
- [ ] **Create 3 pilot MOA organizations**
- [ ] **Performance test: query time <300ms**
- [ ] **Security test: no cross-org data leaks**

---

## Testing Priorities

### 1. Data Isolation Tests ⚠️ CRITICAL
```python
def test_moa_data_isolation():
    # MOH user should NOT see MOLE data
    assert MOH_user_cannot_access_MOLE_community()
    assert MOLE_user_cannot_access_MOH_assessment()
    assert MAFAR_user_cannot_access_MOH_ppa()
```

### 2. OCM Aggregation Tests ⚠️ HIGH
```python
def test_ocm_read_only_access():
    # OCM can view all MOA data (read-only)
    assert OCM_user_can_view_MOH_data()
    assert OCM_user_can_view_MOLE_data()
    assert OCM_user_cannot_edit_MOH_data()
```

### 3. OOBC Backward Compatibility Tests ⚠️ HIGH
```python
def test_oobc_continues_to_function():
    # OOBC data must remain accessible
    assert OOBC_user_can_access_existing_communities()
    assert OOBC_dashboards_show_correct_data()
    assert OOBC_reports_generate_successfully()
```

---

## Performance Targets

| Metric | Target | Threshold |
|--------|--------|-----------|
| **Single-org query time** | <300ms | <500ms |
| **Dashboard load time** | <1s | <2s |
| **API response time** | <200ms | <500ms |
| **Database connections** | <50 | <100 |
| **Memory usage** | <2GB | <4GB |

---

## Next Steps

### Immediate (This Week)
1. Review this architectural analysis with development team
2. Prioritize Phase 0 tasks (User model, RBAC FKs)
3. Create detailed implementation plan for Phase 0
4. Set up test environment for BMMS development

### Short-term (Next 2 Weeks)
1. Complete Phase 0 implementation
2. Test OOBC backward compatibility
3. Prepare for Phase 1 pilot launch
4. Create pilot MOA organizations

### Medium-term (Next 1-3 Months)
1. Launch Phase 1 pilot with 3 MOAs
2. Monitor pilot operation closely
3. Begin Phase 2 implementation
4. Performance tuning and optimization

---

**For detailed analysis, see:** [OBCMS_ARCHITECTURAL_ANALYSIS.md](./OBCMS_ARCHITECTURAL_ANALYSIS.md)

**Key Documents:**
- [BMMS Transition Plan](./TRANSITION_PLAN.md)
- [BMMS Implementation Tasks](./tasks/)
- [Organizations App README](../../development/organizations.md)
