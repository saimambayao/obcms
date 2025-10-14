# Testing Strategy Executive Summary

**Date:** October 14, 2025
**Document:** Comprehensive Testing Strategy for OBCMS/BMMS
**Status:** Ready for Implementation

---

## Overview

This document summarizes the comprehensive testing strategy for OBCMS production deployment and BMMS multi-tenant transition. Testing is structured across three phases with specific success criteria for each.

---

## Current State Assessment

### Existing Test Coverage

| Test Category | Status | Coverage | Notes |
|--------------|--------|----------|-------|
| **Unit Tests** | ✅ EXCELLENT | 99.2% (254/256 passing) | Strong foundation |
| **Data Isolation** | ✅ EXCELLENT | 100% critical security | Organizations app only |
| **Performance** | ✅ GOOD | 83% (10/12 passing) | Calendar/booking tested |
| **Integration** | ✅ GOOD | Organizations app complete | 14,758 bytes of tests |
| **Multi-Tenant** | ⚠️ PARTIAL | Phase 1 only | Need Planning/Budget/MANA |
| **Load Testing** | ❌ MISSING | 0% | Required for 44 MOAs |
| **Regression** | ❌ MISSING | 0% | Required for migrations |

### Test Infrastructure

**Strengths:**
- ✅ pytest framework with comprehensive fixtures
- ✅ Performance test infrastructure (baseline/stress modes)
- ✅ Data isolation test suite (2,852 lines for Organizations)
- ✅ Django TestCase + DRF APIClient ready
- ✅ pytest-cov for coverage reporting

**Gaps:**
- ❌ Locust load testing not implemented
- ❌ Selenium/Playwright browser tests partial
- ❌ Multi-tenant tests missing for Planning/Budget/MANA
- ❌ 44 MOA scale tests not executed

---

## Critical Testing Priorities

### Priority 1: Multi-Tenant Data Isolation (CRITICAL)

**Requirement:** 100% pass rate - Zero tolerance for data leakage

**Test Scenarios:**
1. **Cross-Organization Access Prevention** - MOA A cannot see MOA B's data
2. **URL Tampering Blocked** - Changing org code in URL returns 403
3. **Database Query Scoping** - Automatic organization filtering verified
4. **HTMX Endpoint Security** - Partial updates verify ownership
5. **Admin Panel Scoping** - Admin users see only their MOA's data

**Implementation:**
```python
# Example critical test
def test_moa_a_cannot_see_moa_b_strategic_plans(moh_user, mole_user):
    """CRITICAL: MOH user must not see MOLE strategic plans."""
    moh_plan = create_plan(moh_user.organization)
    mole_plan = create_plan(mole_user.organization)

    client.force_login(moh_user)
    plans = StrategicPlan.objects.all()  # Should auto-filter

    assert plans.count() == 1
    assert moh_plan in plans
    assert mole_plan not in plans  # MUST NOT SEE
```

**Modules Requiring Tests:**
- ❌ Planning Module (4 models)
- ❌ Budgeting Module (views + admin)
- ❌ MANA Module (Assessment model)
- ❌ Communities Module (OBCCommunity model)
- ❌ Coordination Module (legacy models)
- ❌ Policies Module (PolicyRecommendation model)

**Effort:** 16 hours (4 modules × 4 hours each)

---

### Priority 2: Performance Testing Under Multi-Tenant Load (HIGH)

**Requirement:** System must handle 44 MOAs with 1000 concurrent users

**Key Performance Targets:**
- Dashboard load: < 500ms
- API responses: < 300ms
- Database queries: ≤ 5 per list view (N+1 prevention)
- Cache hit rate: > 80%
- Success rate: ≥ 95% under peak load

**Load Test Scenarios:**
1. **Peak Concurrent Users** - 1000 users (22-23 per MOA average)
2. **Database Connection Pool** - 2200 connections → < 200 via PgBouncer
3. **Redis Cache Performance** - Maintain 80% hit rate
4. **OCM Aggregation** - Cross-MOA queries < 2 seconds

**Implementation Tool:** Locust

```python
# Example Locust scenario
class BMSMUser(HttpUser):
    @task(10)
    def view_dashboard(self):
        self.client.get(f"/moa/{self.moa_code}/dashboard/")

    @task(5)
    def list_plans(self):
        self.client.get(f"/moa/{self.moa_code}/planning/strategic-plans/")
```

**Effort:** 12 hours (setup + execution + analysis)

---

### Priority 3: Pilot MOA User Acceptance Testing (CRITICAL)

**Requirement:** 100% critical scenarios completed, ≥ 8/10 user satisfaction

**Pilot Setup:**
- **3 MOAs:** MOH (Ministry of Health), MOLE (Ministry of Labor), MAFAR (Ministry of Agriculture)
- **15 Users:** 5 per MOA (1 admin, 2 managers, 2 staff)
- **Duration:** 2 weeks intensive testing

**UAT Scenarios:**
1. **Strategic Planning Workflow** - Create 5-year plan, submit for approval
2. **Budget Preparation Workflow** - Create FY 2025 budget, multi-level approval
3. **Inter-MOA Partnership** - Create bilateral partnership between 2 MOAs
4. **MANA Assessment** - Create community assessment, verify data isolation
5. **Organization Switching** - Multi-org users switch contexts correctly

**Success Metrics:**
- Task completion rate: ≥ 95%
- User satisfaction: ≥ 8/10
- Support tickets: < 5 critical/week
- Data isolation: Zero violations detected

**Effort:** 80 hours (2 weeks × 40 hours)

---

## Three-Phase Testing Approach

### Phase 1: Pre-Deployment Testing (4 weeks)

**Week 1: Unit & Integration Tests**
- Run all existing tests (256 tests)
- Fix 2 failing attendance tests
- Achieve 100% pass rate

**Week 2: Multi-Tenant Tests**
- Implement organization scoping tests for Planning/Budget/MANA
- 100% data isolation verification
- Admin panel scoping tests

**Week 3: Performance Baseline**
- Measure current OOBC performance
- Establish baseline metrics
- Identify optimization opportunities

**Week 4: Staging Deployment**
- Deploy to staging environment
- Smoke tests on all modules
- Monitoring dashboards configured

**Exit Criteria:**
- ✅ 100% unit test pass rate
- ✅ Multi-tenant tests implemented
- ✅ Performance baseline established
- ✅ Staging environment operational

---

### Phase 2: Pilot MOA Testing (8 weeks)

**Week 5: Pilot Setup**
- Onboard 15 pilot users (3 MOAs)
- Training sessions completed
- All users can log in successfully

**Week 6: UAT Round 1**
- Execute 5 critical UAT scenarios
- Collect user feedback
- Track completion rates

**Week 7: Bug Fixes**
- Address critical pilot feedback
- Fix data isolation issues
- Performance optimization

**Week 8: UAT Round 2**
- Re-test fixed issues
- Validate 100% task completion
- Final pilot sign-off

**Exit Criteria:**
- ✅ 100% task completion rate
- ✅ User satisfaction ≥ 8/10
- ✅ Zero critical security issues
- ✅ Performance targets met

---

### Phase 3: Full Rollout Testing (4 weeks)

**Week 9: Load Testing**
- Simulate 44 MOAs with 1000 concurrent users
- Database stress tests
- Redis cache performance validation

**Week 10: Scalability Validation**
- Horizontal scaling tests
- Failover testing (Redis Sentinel, PgBouncer)
- Connection pool stress tests

**Week 11: OCM Testing**
- Aggregation across all 44 MOAs
- Read-only enforcement
- Performance under aggregation load

**Week 12: Final Validation**
- Stakeholder sign-off
- Production cutover plan review
- Go-live approval

**Exit Criteria:**
- ✅ 95% success rate with 1000 users
- ✅ OCM aggregation functional
- ✅ Scalability validated
- ✅ Stakeholder approval obtained

---

## Critical Test Scenarios by Module

### Planning Module Tests

**Critical Scenarios:**
1. MOH user creates strategic plan → only visible to MOH
2. MOH user tries to access MOLE plan → 403 Forbidden
3. Strategic plan list shows only user's org plans
4. Goals cannot link to other org's plans
5. Dashboard stats scoped to user's org

**Test File:** `src/planning/tests/test_organization_scoping.py` (NEW)
**Lines:** ~800 (estimated)
**Effort:** 4 hours

---

### Budgeting Module Tests

**Critical Scenarios:**
1. Budget proposals filtered by user's org (not hardcoded OOBC)
2. Budget approval workflow verifies org ownership
3. Program budgets inherit org from parent proposal
4. Admin panel shows only user's org proposals
5. HTMX endpoints enforce org security

**Test File:** `src/budget_preparation/tests/test_organization_scoping.py` (NEW)
**Lines:** ~800 (estimated)
**Effort:** 4 hours

---

### MANA Module Tests

**Critical Scenarios:**
1. Assessments scoped by organization
2. Beneficiary data strictly isolated (Data Privacy Act 2012)
3. Assessment list shows only user's org assessments
4. Cross-org assessment access blocked
5. Dashboard stats organization-scoped

**Test File:** `src/mana/tests/test_organization_scoping.py` (NEW)
**Lines:** ~600 (estimated)
**Effort:** 4 hours

---

### OCM Aggregation Tests

**Critical Scenarios:**
1. OCM sees aggregated data from all 44 MOAs
2. OCM cannot modify any data (read-only)
3. OCM dashboard loads < 2 seconds
4. OCM export includes all MOAs
5. OCM access audit logged

**Test File:** `src/ocm/tests/test_aggregation_security.py` (NEW)
**Lines:** ~400 (estimated)
**Effort:** 4 hours

---

## Performance Test Targets

### Response Time Targets

| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Dashboard load | < 500ms | ~200ms (OOBC) | ✅ GOOD |
| List views | < 300ms | ~150ms (OOBC) | ✅ GOOD |
| API endpoints | < 300ms | ~180ms (OOBC) | ✅ GOOD |
| HTMX partials | < 50ms | ~30ms (OOBC) | ✅ EXCELLENT |
| GeoJSON rendering | < 400ms | ~350ms (OOBC) | ✅ GOOD |

**Note:** OOBC baselines must be maintained under multi-tenant load

### Database Performance Targets

| Metric | Target | Tool |
|--------|--------|------|
| N+1 queries prevented | ≤ 5 queries per list view | CaptureQueriesContext |
| Index usage | 100% on org filters | EXPLAIN queries |
| Connection pool usage | < 80% under peak load | PgBouncer stats |
| Query cache hit rate | > 80% | Redis stats |

### Scalability Targets

| Scenario | Target | Current |
|----------|--------|---------|
| Concurrent users | 1000 (95% success) | Not tested |
| MOAs supported | 44 | 1 (OOBC only) |
| Database connections | < 200 actual (via pooling) | Not tested |
| Memory usage | Stable (no leaks) | Stable (OOBC) |

---

## Regression Testing Strategy

**Purpose:** Ensure OOBC functionality preserved during BMMS transition

### Regression Test Categories

**1. Data Integrity Tests**
- OOBC existing data unmodified
- OOBC organization ID remains 1
- OOBC user access preserved

**2. URL Backward Compatibility**
- Legacy OOBC URLs continue working
- Redirect middleware functional
- No broken links

**3. Performance Regression**
- OOBC operations not slower
- Dashboard load time unchanged
- Query performance maintained

**4. Feature Regression**
- All OOBC workflows functional
- MANA assessments work
- Budget preparation unchanged
- Planning module accessible

**Automation:** CI/CD pipeline runs regression suite on every commit

```yaml
# .github/workflows/regression-tests.yml
name: BMMS Regression Tests
on: [push, pull_request]

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - name: Run Multi-Tenant Tests
        run: pytest organizations/tests/test_data_isolation.py -v

      - name: Run Module Scoping Tests
        run: |
          pytest planning/tests/test_organization_scoping.py -v
          pytest budget_preparation/tests/test_organization_scoping.py -v
```

---

## Testing Infrastructure Requirements

### Tools Required

**Already Available:**
- ✅ pytest + pytest-cov
- ✅ Django TestCase
- ✅ DRF APIClient
- ✅ Performance fixtures (baseline/stress modes)

**Need to Implement:**
- ❌ Locust (load testing)
- ❌ Selenium/Playwright (browser automation)
- ❌ Test data generation scripts (44 MOAs)

### Environment Setup

**Staging Environment:**
- PostgreSQL 15 with PgBouncer
- Redis 7 with Sentinel
- 4 web servers (nginx load balancer)
- Prometheus + Grafana monitoring

**Test Data:**
- 44 MOAs seeded
- 10 users per MOA (440 total users)
- 5 strategic plans per MOA
- 3 budget proposals per MOA
- 20 assessments per MOA

**Generation Command:**
```bash
python manage.py generate_test_data \
    --moas 44 \
    --users-per-moa 10 \
    --plans-per-moa 5 \
    --budgets-per-moa 3
```

---

## Risk Assessment and Mitigation

### Critical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Data leakage between MOAs** | MEDIUM | CRITICAL | Comprehensive isolation tests, manual audit |
| **Performance degradation** | MEDIUM | HIGH | Load testing before rollout, scaling ready |
| **Migration data loss** | LOW | CRITICAL | Full backup, rollback tested |
| **Pilot user confusion** | HIGH | MEDIUM | Training, user guides, support |

### Rollback Plan

**Trigger Conditions:**
1. Critical security vulnerability
2. Data corruption detected
3. Performance degradation > 50%
4. Pilot satisfaction < 7/10

**Rollback Procedure:**
```bash
# 1. Revert code
git checkout production-stable

# 2. Rollback migrations
python manage.py migrate planning 0001
python manage.py migrate budget_preparation 0001

# 3. Disable multi-tenant
# In settings: ENABLE_MULTI_TENANT = False

# 4. Verify OOBC mode
python manage.py check
```

**Testing Rollback:** Must be tested in staging before production

---

## Success Criteria Summary

### Production Go/No-Go Criteria

**✅ GO Criteria (All must pass):**

1. ✅ Data isolation: 100% pass rate
2. ✅ Performance: 95th percentile < 1 second
3. ✅ Pilot feedback: User satisfaction ≥ 8/10
4. ✅ UAT completion: 100% critical scenarios
5. ✅ Regression: Zero OOBC functionality issues
6. ✅ Security: Zero data leakage found
7. ✅ Scalability: 95% success with 1000 users
8. ✅ Database: Connection pool < 80% under load
9. ✅ Monitoring: All dashboards operational
10. ✅ Rollback: Tested successfully

**🔴 NO-GO Criteria (Any triggers delay):**

1. Critical security vulnerability
2. Data corruption detected
3. Performance degradation > 50%
4. Pilot satisfaction < 7/10
5. UAT completion < 90%
6. Database connection exhaustion
7. Memory leaks detected
8. Rollback procedure fails

---

## Effort Estimation

### Test Implementation Effort

| Task | Effort | Priority |
|------|--------|----------|
| **Multi-tenant tests (4 modules)** | 16 hours | CRITICAL |
| **Load testing setup (Locust)** | 8 hours | HIGH |
| **Browser automation tests** | 12 hours | MEDIUM |
| **Test data generation** | 4 hours | HIGH |
| **CI/CD integration** | 4 hours | MEDIUM |
| **Performance baseline** | 8 hours | HIGH |
| **Regression suite** | 8 hours | HIGH |
| **Documentation** | 4 hours | MEDIUM |

**Total:** 64 hours (8 person-days)

### Testing Execution Effort

| Phase | Duration | Effort |
|-------|----------|--------|
| **Pre-deployment** | 4 weeks | 160 hours |
| **Pilot testing** | 8 weeks | 320 hours |
| **Full rollout testing** | 4 weeks | 160 hours |

**Total:** 16 weeks (640 hours)

---

## Immediate Next Steps

### Week 1 Actions (CRITICAL)

1. **Implement Planning Module Multi-Tenant Tests** (4 hours)
   - Create `test_organization_scoping.py`
   - Test strategic plans, goals, work plans
   - Verify 100% data isolation

2. **Implement Budgeting Module Multi-Tenant Tests** (4 hours)
   - Test budget proposals scoped by org
   - Verify views use `request.user.organization` (not hardcoded OOBC)
   - Test admin panel scoping

3. **Implement MANA Module Multi-Tenant Tests** (4 hours)
   - Test assessments scoped by org
   - Verify beneficiary data isolation (Data Privacy Act)
   - Test dashboard stats organization-scoped

4. **Setup Load Testing Infrastructure** (4 hours)
   - Install Locust
   - Create `locustfile_bmms.py`
   - Configure test scenarios

**Total Week 1 Effort:** 16 hours

---

## Conclusion

This comprehensive testing strategy provides a clear roadmap for validating OBCMS production deployment and BMMS multi-tenant transition. The strategy prioritizes **critical security testing (data isolation)**, **performance validation (scalability)**, and **user acceptance (pilot testing)** to ensure a successful rollout to all 44 BARMM MOAs.

**Key Success Factors:**
1. **Zero-tolerance for data leakage** - 100% pass rate required
2. **Pilot-driven validation** - Real user feedback before full rollout
3. **Performance at scale** - 1000 concurrent users across 44 MOAs
4. **Automated regression testing** - CI/CD prevents regressions
5. **Clear go/no-go criteria** - Objective deployment decisions

**Timeline to Production:**
- **4 weeks:** Pre-deployment testing (staging validation)
- **8 weeks:** Pilot MOA testing (3 MOAs, 15 users)
- **4 weeks:** Full rollout testing (44 MOAs, scalability validation)
- **Total:** 16 weeks from staging to production

**Current Readiness:** 72% overall (100% infrastructure, 60% application-level multi-tenancy)

**Recommended Action:** Begin implementation of multi-tenant tests immediately to accelerate production readiness.

---

**Document Owner:** OBCMS Testing Team
**Status:** Ready for Implementation
**Next Review:** After Week 1 test implementation
**Approval Required:** Project Lead, Security Team, QA Lead

