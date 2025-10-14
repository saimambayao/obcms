# Comprehensive Testing Strategy for OBCMS Deployment and BMMS Transition

**Document Version:** 1.0
**Date:** October 14, 2025
**Status:** OFFICIAL - Production Deployment Guide
**Scope:** OBCMS staging/production deployment + BMMS pilot validation

---

## Executive Summary

This document provides a comprehensive testing strategy for OBCMS production deployment and BMMS multi-tenant transition validation. Testing is structured across three critical phases: **Pre-Deployment Validation** (staging environment), **Pilot MOA Deployment** (3 MOAs), and **Full Rollout Preparation** (44 MOAs).

### Current Testing Status

| Category | Status | Coverage | Priority |
|----------|--------|----------|----------|
| **Unit Tests** | ✅ EXCELLENT | 99.2% passing (254/256) | COMPLETE |
| **Data Isolation Tests** | ✅ EXCELLENT | 100% critical security | COMPLETE |
| **Performance Tests** | ✅ GOOD | 83% passing (10/12) | COMPLETE |
| **Multi-Tenant Tests** | ⚠️ PARTIAL | Organizations only | IN PROGRESS |
| **Load Tests** | ❌ MISSING | 0% (44 MOAs scale) | REQUIRED |
| **Regression Tests** | ❌ MISSING | 0% (module migrations) | REQUIRED |

### Testing Infrastructure

- **Test Framework:** pytest + Django TestCase
- **Performance Testing:** pytest fixtures with baseline/stress modes
- **Load Testing:** Locust (to be implemented)
- **Browser Testing:** Selenium/Playwright (partially implemented)
- **API Testing:** DRF test client + APIClient
- **Coverage Tool:** pytest-cov

---

## Part 1: Pre-Deployment Testing (Staging Environment)

### 1.1 Multi-Tenant Data Isolation Testing (CRITICAL)

**Priority:** 🔴 CRITICAL - 100% pass rate required
**Effort:** HIGH (already implemented for Organizations app)
**Location:** `/src/organizations/tests/test_data_isolation.py` (13,667 bytes)

#### Test Scenarios

**Scenario 1: Cross-Organization Data Access Prevention**
```python
def test_moa_a_cannot_see_moa_b_strategic_plans(client, moh_user, mole_user):
    """CRITICAL: MOH user must not see MOLE strategic plans."""
    # Setup: Create strategic plans for both MOAs
    moh_plan = StrategicPlan.objects.create(
        title="MOH Health Strategy 2025-2030",
        organization=moh_user.organization,
        start_year=2025,
        end_year=2030
    )

    mole_plan = StrategicPlan.objects.create(
        title="MOLE Employment Strategy 2025-2030",
        organization=mole_user.organization,
        start_year=2025,
        end_year=2030
    )

    # Test: MOH user logs in
    client.force_login(moh_user)

    # Verify: List view shows only MOH plans
    response = client.get(f'/moa/{moh_user.organization.code}/planning/strategic-plans/')
    content = response.content.decode()

    assert "MOH Health Strategy" in content
    assert "MOLE Employment Strategy" not in content

    # Verify: Direct access to MOLE plan returns 403
    response = client.get(f'/moa/{moh_user.organization.code}/planning/strategic-plans/{mole_plan.id}/')
    assert response.status_code == 403
```

**Scenario 2: URL Tampering Prevention**
```python
def test_url_tampering_blocked(client, moh_user):
    """CRITICAL: Changing org code in URL must return 403."""
    client.force_login(moh_user)

    # User is MOH staff, tries to access MOLE URL
    response = client.get('/moa/MOLE/dashboard/')
    assert response.status_code == 403
    assert "do not have access" in response.content.decode().lower()
```

**Scenario 3: Database Query Scoping Verification**
```python
@pytest.mark.django_db
def test_queryset_automatic_organization_filtering(moh_user):
    """CRITICAL: QuerySets must automatically filter by organization."""
    # Setup: Set organization context
    _thread_locals.organization = moh_user.organization

    # Create assessment for MOH
    assessment = Assessment.objects.create(
        title="MOH Community Health Assessment",
        organization=moh_user.organization,
        status='published'
    )

    # Query without explicit filter
    all_assessments = Assessment.objects.all()

    # Verify: Only MOH assessments returned
    assert all_assessments.count() == 1
    assert all_assessments.first().organization == moh_user.organization

    # Cleanup
    del _thread_locals.organization
```

**Scenario 4: HTMX Endpoint Security**
```python
def test_htmx_endpoints_respect_organization_scoping(client, moh_user, mole_budget):
    """CRITICAL: HTMX partial updates must verify organization ownership."""
    client.force_login(moh_user)

    # Attempt to update MOLE budget via HTMX
    response = client.post(
        f'/moa/{moh_user.organization.code}/budget/proposals/{mole_budget.id}/approve/',
        HTTP_HX_REQUEST='true'
    )

    assert response.status_code in [403, 404]  # Blocked or not found
```

**Scenario 5: Admin Panel Organization Scoping**
```python
def test_admin_queryset_filtering(admin_client, moh_admin_user):
    """Admins should only see their MOA's data unless superuser."""
    admin_client.force_login(moh_admin_user)

    # Access budget proposal changelist
    response = admin_client.get('/admin/budget_preparation/budgetproposal/')

    # Verify: Only MOH proposals visible
    assert response.status_code == 200
    content = response.content.decode()
    assert "MOH" in content
    assert "MOLE" not in content  # Should not see other MOAs
```

#### Acceptance Criteria

- ✅ 100% pass rate on all cross-organization access tests
- ✅ URL tampering returns 403 Forbidden
- ✅ Database queries automatically scoped by organization
- ✅ HTMX endpoints enforce organization ownership
- ✅ Admin panels filter by user's organization
- ✅ No data leakage across organizations detected

---

### 1.2 Module-Specific Multi-Tenant Testing

#### Planning Module Tests

**Test File:** `/src/planning/tests/test_organization_scoping.py` (to be created)

```python
@pytest.mark.django_db
class TestPlanningMultiTenant:
    """Test Planning module multi-tenant isolation."""

    def test_strategic_plan_list_scoped_by_organization(self, moh_user, mole_user):
        """Strategic plans must be filtered by user's organization."""
        # Create plans for both organizations
        moh_plan = StrategicPlan.objects.create(
            title="MOH Plan",
            organization=moh_user.organization
        )
        mole_plan = StrategicPlan.objects.create(
            title="MOLE Plan",
            organization=mole_user.organization
        )

        # Query as MOH user
        _thread_locals.organization = moh_user.organization
        plans = StrategicPlan.objects.all()

        assert plans.count() == 1
        assert plans.first() == moh_plan

    def test_annual_work_plan_creation_auto_assigns_organization(self, moh_user):
        """Work plans must auto-assign user's organization."""
        _thread_locals.organization = moh_user.organization

        plan = AnnualWorkPlan.objects.create(
            title="MOH Annual Plan 2025",
            year=2025
        )

        # Verify organization auto-assigned
        assert plan.organization == moh_user.organization

    def test_cross_organization_goal_linking_prevented(self, moh_user):
        """Goals cannot link to other organization's strategic plans."""
        mole_org = Organization.objects.create(code='MOLE', name='MOLE')
        mole_plan = StrategicPlan.objects.create(
            title="MOLE Plan",
            organization=mole_org
        )

        _thread_locals.organization = moh_user.organization

        with pytest.raises(ValidationError):
            goal = StrategicGoal.objects.create(
                strategic_plan=mole_plan,  # Wrong organization
                title="Health Goal"
            )
```

#### Budgeting Module Tests

**Test File:** `/src/budget_preparation/tests/test_organization_scoping.py`

```python
@pytest.mark.django_db
class TestBudgetingMultiTenant:
    """Test Budgeting module multi-tenant isolation."""

    def test_budget_proposals_filtered_by_organization(self, moh_user):
        """Budget proposals must be scoped to user's organization."""
        # Verify view uses request.user.organization (not hardcoded OOBC)
        client = Client()
        client.force_login(moh_user)

        response = client.get(f'/moa/{moh_user.organization.code}/budget/')

        # Should use user's organization, not OOBC
        assert response.context['organization'] == moh_user.organization
        assert response.context['organization'].code != 'OOBC'

    def test_budget_approval_workflow_respects_organization(self, moh_user, mole_proposal):
        """Budget approval must verify organization ownership."""
        client = Client()
        client.force_login(moh_user)

        # MOH user tries to approve MOLE proposal
        response = client.post(
            f'/moa/{moh_user.organization.code}/budget/proposals/{mole_proposal.id}/approve/'
        )

        assert response.status_code in [403, 404]
```

#### MANA Module Tests

**Test File:** `/src/mana/tests/test_organization_scoping.py`

```python
@pytest.mark.django_db
class TestMANAMultiTenant:
    """Test MANA module multi-tenant isolation."""

    def test_assessments_scoped_by_organization(self, moh_user, mole_user):
        """Assessments must be filtered by organization."""
        moh_assessment = Assessment.objects.create(
            title="MOH Health Assessment",
            organization=moh_user.organization,
            status='published'
        )

        mole_assessment = Assessment.objects.create(
            title="MOLE Employment Assessment",
            organization=mole_user.organization,
            status='published'
        )

        # MOH user query
        _thread_locals.organization = moh_user.organization
        assessments = Assessment.objects.all()

        assert assessments.count() == 1
        assert assessments.first() == moh_assessment

    def test_beneficiary_data_privacy_enforcement(self, moh_user):
        """Beneficiary data must be strictly isolated (Data Privacy Act 2012)."""
        # CRITICAL: Beneficiary PII must never leak across organizations
        assessment = Assessment.objects.create(
            title="Health Assessment",
            organization=moh_user.organization
        )

        # Create beneficiary linked to assessment
        beneficiary = Beneficiary.objects.create(
            assessment=assessment,
            organization=moh_user.organization,
            full_name="Juan Dela Cruz",
            national_id="123456789"
        )

        # Verify other MOA cannot access
        mole_user = create_user(organization=create_organization('MOLE'))
        _thread_locals.organization = mole_user.organization

        beneficiaries = Beneficiary.objects.all()
        assert beneficiaries.count() == 0  # Should see no beneficiaries
```

---

### 1.3 Performance Testing Under Multi-Tenant Load

**Priority:** 🟡 HIGH
**Effort:** MODERATE
**Tools:** pytest + fixtures, Locust for stress testing

#### Test Scenarios

**Scenario 1: Dashboard Load Time (Multi-Org)**
```python
@pytest.mark.django_db
def test_dashboard_load_time_with_44_moas(perf_client):
    """Dashboard should load < 500ms even with 44 MOAs data."""
    # Setup: Create 44 MOAs with realistic data
    for i in range(44):
        org = create_moa(f'MOA{i:02d}')
        create_test_data(org, proposals=10, plans=5, assessments=20)

    # Test: Load dashboard for MOH
    moh_user = User.objects.get(organization__code='MOH')
    perf_client.force_login(moh_user)

    start_time = time.time()
    response = perf_client.get(f'/moa/MOH/dashboard/')
    end_time = time.time()

    load_time_ms = (end_time - start_time) * 1000

    assert response.status_code == 200
    assert load_time_ms < 500, f"Dashboard load time {load_time_ms:.2f}ms exceeds 500ms"
```

**Scenario 2: Concurrent User Load Test**
```python
@pytest.mark.slow
@pytest.mark.django_db
def test_500_concurrent_users_across_all_moas():
    """System should handle 500 concurrent users (11-12 per MOA average)."""
    # Create 44 MOAs with 12 users each (528 total users)
    users = []
    for i in range(44):
        org = Organization.objects.get(code=f'MOA{i:02d}')
        for j in range(12):
            user = User.objects.create_user(
                username=f'{org.code}_user{j}',
                organization=org
            )
            users.append(user)

    # Simulate 500 concurrent sessions
    def user_session(user):
        client = Client()
        client.force_login(user)
        client.get(f'/moa/{user.organization.code}/')
        client.get(f'/moa/{user.organization.code}/planning/')
        client.get(f'/moa/{user.organization.code}/budget/')
        return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(user_session, user) for user in users[:500]]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    success_rate = (sum(results) / len(results)) * 100
    assert success_rate >= 95, f"Success rate {success_rate:.1f}% < 95%"
```

**Scenario 3: Database Query Performance (N+1 Prevention)**
```python
def test_strategic_plan_list_query_count(moh_user):
    """Strategic plan list should use ≤ 5 queries regardless of data volume."""
    # Create 100 strategic plans with related goals
    for i in range(100):
        plan = StrategicPlan.objects.create(
            title=f"Plan {i}",
            organization=moh_user.organization
        )
        for j in range(5):
            StrategicGoal.objects.create(
                strategic_plan=plan,
                title=f"Goal {j}"
            )

    client = Client()
    client.force_login(moh_user)

    with CaptureQueriesContext(connection) as queries:
        response = client.get(f'/moa/{moh_user.organization.code}/planning/strategic-plans/')

    query_count = len(queries)
    assert query_count <= 5, f"Query count {query_count} exceeds 5 (N+1 problem)"
```

#### Acceptance Criteria

- ✅ Dashboard loads < 500ms with 44 MOAs data
- ✅ 95% success rate with 500 concurrent users
- ✅ No N+1 query problems (≤ 5 queries per list view)
- ✅ API response times < 300ms
- ✅ GeoJSON rendering < 400ms
- ✅ HTMX partial updates < 50ms

---

### 1.4 OCM Aggregation Testing

**Priority:** 🟡 HIGH
**Scope:** OCM read-only access across all 44 MOAs

#### Test Scenarios

**Scenario 1: OCM Consolidated Budget View**
```python
@pytest.mark.django_db
def test_ocm_consolidated_budget_aggregates_all_moas(ocm_user):
    """OCM should see aggregated budget data from all 44 MOAs."""
    # Setup: Create budget proposals for 3 MOAs
    moh_proposal = BudgetProposal.objects.create(
        organization=Organization.objects.get(code='MOH'),
        fiscal_year=2025,
        total_amount=1000000
    )

    mole_proposal = BudgetProposal.objects.create(
        organization=Organization.objects.get(code='MOLE'),
        fiscal_year=2025,
        total_amount=800000
    )

    mafar_proposal = BudgetProposal.objects.create(
        organization=Organization.objects.get(code='MAFAR'),
        fiscal_year=2025,
        total_amount=1200000
    )

    # Test: OCM user accesses consolidated budget
    client = Client()
    client.force_login(ocm_user)

    response = client.get('/ocm/consolidated-budget/?fiscal_year=2025')

    # Verify: All MOAs visible
    assert response.status_code == 200
    data = response.json() if hasattr(response, 'json') else response.context

    total = data['total_budget']
    assert total == 3000000  # Sum of all 3 proposals

    moa_breakdown = data['moa_breakdown']
    assert len(moa_breakdown) == 3
    assert any(item['code'] == 'MOH' for item in moa_breakdown)
```

**Scenario 2: OCM Cannot Modify Data**
```python
def test_ocm_user_cannot_approve_budgets(ocm_user, moh_proposal):
    """OCM access must be strictly read-only."""
    client = Client()
    client.force_login(ocm_user)

    # Attempt to approve budget
    response = client.post(f'/ocm/budget/proposals/{moh_proposal.id}/approve/')

    assert response.status_code == 403  # Forbidden

    # Verify proposal status unchanged
    moh_proposal.refresh_from_db()
    assert moh_proposal.status != 'approved'
```

**Scenario 3: OCM Performance Dashboard Aggregation**
```python
def test_ocm_performance_overview_query_performance(ocm_user):
    """OCM dashboard should aggregate 44 MOAs in < 2 seconds."""
    # Setup: Create data for all 44 MOAs
    for i in range(44):
        org = Organization.objects.get(code=f'MOA{i:02d}')
        StrategicPlan.objects.create(organization=org, title=f"Plan {i}")
        BudgetProposal.objects.create(organization=org, fiscal_year=2025)

    client = Client()
    client.force_login(ocm_user)

    start_time = time.time()
    response = client.get('/ocm/performance-overview/')
    end_time = time.time()

    load_time = end_time - start_time
    assert load_time < 2.0, f"OCM dashboard took {load_time:.2f}s (should be < 2s)"
```

#### Acceptance Criteria

- ✅ OCM sees aggregated data from all 44 MOAs
- ✅ OCM cannot modify any data (403 on POST/PUT/DELETE)
- ✅ OCM dashboard loads < 2 seconds with full dataset
- ✅ OCM export functionality works correctly
- ✅ Audit logs track OCM data access

---

## Part 2: Pilot MOA Deployment Testing (3 MOAs)

### 2.1 Pilot MOA Selection and Setup

**Pilot MOAs:**
1. **MOH** - Ministry of Health (complex workflows, high data volume)
2. **MOLE** - Ministry of Labor and Employment (partnership-heavy)
3. **MAFAR** - Ministry of Agriculture, Fisheries and Agrarian Reform (budget-intensive)

#### Test Environment Setup

```bash
# Setup pilot environment
cd src
python manage.py load_pilot_moas
python manage.py import_pilot_users --csv pilot_users.csv
python manage.py generate_pilot_data --users 5 --programs 3 --year 2025
```

#### Pilot User Roles

| Organization | Role | Count | Responsibilities |
|--------------|------|-------|------------------|
| MOH | Admin | 1 | Full MOA management |
| MOH | Manager | 2 | Approve plans/budgets |
| MOH | Staff | 2 | Data entry, reporting |
| MOLE | Admin | 1 | Full MOA management |
| MOLE | Manager | 2 | Partnership management |
| MOLE | Staff | 2 | Coordination tasks |
| MAFAR | Admin | 1 | Full MOA management |
| MAFAR | Manager | 2 | Budget oversight |
| MAFAR | Staff | 2 | Program execution |

---

### 2.2 User Acceptance Testing (UAT) Scenarios

**Priority:** 🔴 CRITICAL - Must pass before full rollout
**Duration:** 2 weeks pilot period
**Participants:** 15 pilot users (5 per MOA)

#### UAT-1: Strategic Planning Workflow

**User Story:** As a MOH Manager, I want to create and submit a 5-year strategic plan for approval.

**Test Steps:**
1. Login as MOH Manager
2. Navigate to Planning module
3. Create new strategic plan (2025-2030)
4. Add 3 strategic goals with metrics
5. Create annual work plan for 2025
6. Add 5 work plan objectives
7. Submit for approval
8. MOH Admin reviews and approves
9. Verify plan status changes to "Approved"
10. Verify MOLE/MAFAR users cannot see MOH plan

**Expected Results:**
- ✅ Strategic plan created successfully
- ✅ Goals and objectives linked correctly
- ✅ Approval workflow completes without errors
- ✅ Data isolation: MOLE/MAFAR see only their own plans

#### UAT-2: Budget Preparation Workflow

**User Story:** As a MAFAR Staff member, I want to prepare FY 2025 budget proposal.

**Test Steps:**
1. Login as MAFAR Staff
2. Navigate to Budget Preparation module
3. Create new budget proposal for FY 2025
4. Add 3 programs with budget allocations
5. Add budget line items to each program
6. Submit proposal for review
7. MAFAR Manager reviews and requests revision
8. MAFAR Staff updates and resubmits
9. MAFAR Admin approves
10. Verify proposal appears in OCM consolidated view

**Expected Results:**
- ✅ Budget proposal workflow completes
- ✅ Multi-level approval works correctly
- ✅ Budget totals calculate accurately
- ✅ OCM can view (read-only) MAFAR budget
- ✅ MOH/MOLE cannot access MAFAR budget

#### UAT-3: Inter-MOA Partnership Creation

**User Story:** As a MOLE Manager, I want to create a bilateral partnership with MOH for employment-health program.

**Test Steps:**
1. Login as MOLE Manager
2. Navigate to Coordination > Inter-MOA Partnerships
3. Create new partnership (MOLE lead, MOH participant)
4. Set partnership type: "Joint Program"
5. Add resource commitments from both MOAs
6. Set status: "Pending Approval"
7. MOH receives notification
8. MOH Manager reviews and accepts
9. Partnership status changes to "Active"
10. Verify both MOAs can view partnership
11. Verify MAFAR cannot see partnership (not participant)

**Expected Results:**
- ✅ Partnership created with correct MOA access
- ✅ Email notifications sent to both MOAs
- ✅ Only participating MOAs see partnership
- ✅ OCM can view all partnerships

#### UAT-4: MANA Assessment Creation

**User Story:** As a MOH Staff member, I want to conduct a community health assessment.

**Test Steps:**
1. Login as MOH Staff
2. Navigate to MANA module
3. Create new assessment for Zamboanga del Sur
4. Select assessment type: "Health and Nutrition"
5. Add demographic data
6. Complete assessment form
7. Upload supporting documents
8. Publish assessment
9. Verify assessment visible in MOH dashboard
10. Verify MOLE/MAFAR cannot access assessment

**Expected Results:**
- ✅ Assessment creation workflow smooth
- ✅ Geographic data integration works
- ✅ Document upload successful
- ✅ Data isolation maintained
- ✅ Assessment data protected (Data Privacy Act 2012)

#### UAT-5: Organization Switching (Multi-Org Users)

**User Story:** As a superuser with access to multiple MOAs, I want to switch between organizations.

**Test Steps:**
1. Login as superuser
2. Verify organization selector visible in navigation
3. Current organization: MOH
4. Navigate to Planning module (see MOH plans)
5. Switch to MOLE via selector
6. Verify URL changes to `/moa/MOLE/...`
7. Navigate to Planning module (see MOLE plans)
8. Verify no data bleeding from MOH
9. Switch to MAFAR
10. Repeat verification

**Expected Results:**
- ✅ Organization switcher works correctly
- ✅ URL updates properly
- ✅ Data scoped correctly after switch
- ✅ No session data bleeding
- ✅ Thread-local storage cleaned properly

---

### 2.3 Regression Testing During Pilot

**Purpose:** Ensure OOBC functionality remains intact while BMMS pilot runs

#### Regression Test Suite

**Test 1: OOBC Existing Data Integrity**
```python
def test_oobc_data_unaffected_by_bmms_pilot():
    """OOBC existing data must remain accessible and unmodified."""
    # Verify OOBC organization ID remains 1
    oobc = Organization.objects.get(code='OOBC')
    assert oobc.id == 1

    # Verify existing strategic plans still accessible
    oobc_plans = StrategicPlan.objects.filter(organization=oobc)
    assert oobc_plans.exists()

    # Verify OOBC users can still log in
    oobc_user = User.objects.filter(
        organization_memberships__organization=oobc
    ).first()
    client = Client()
    assert client.login(username=oobc_user.username, password='correct_password')
```

**Test 2: OOBC URL Backward Compatibility**
```python
def test_oobc_urls_still_work(oobc_user):
    """Legacy OOBC URLs must continue working."""
    client = Client()
    client.force_login(oobc_user)

    # Old-style URL (without /moa/ prefix)
    response = client.get('/dashboard/')
    assert response.status_code in [200, 302]  # Success or redirect

    # New-style URL
    response = client.get('/moa/OOBC/dashboard/')
    assert response.status_code == 200
```

**Test 3: Performance Regression (OOBC Baseline)**
```python
def test_oobc_performance_not_degraded(oobc_user):
    """OOBC operations should not slow down due to multi-tenancy overhead."""
    client = Client()
    client.force_login(oobc_user)

    # Measure dashboard load time
    start_time = time.time()
    response = client.get('/moa/OOBC/dashboard/')
    end_time = time.time()

    load_time_ms = (end_time - start_time) * 1000

    # Should be same as pre-BMMS baseline
    assert load_time_ms < 200, f"Dashboard load time {load_time_ms:.2f}ms degraded"
```

#### Acceptance Criteria

- ✅ 100% OOBC functionality preserved
- ✅ No performance degradation for OOBC users
- ✅ Existing OOBC data accessible
- ✅ Legacy URLs continue working
- ✅ OOBC user workflows unchanged

---

### 2.4 Pilot Feedback Collection

**Duration:** 2 weeks
**Participants:** 15 pilot users

#### Feedback Mechanisms

1. **Daily Check-ins:** Quick survey (5 questions, 2 minutes)
2. **Weekly Interviews:** 30-minute sessions with each MOA admin
3. **Issue Tracking:** Dedicated pilot support channel
4. **Performance Metrics:** Automated collection (page load times, error rates)

#### Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| User Satisfaction | ≥ 8/10 | Daily survey |
| Task Completion Rate | ≥ 95% | UAT scenarios |
| Error Rate | < 1% | Server logs |
| Page Load Time | < 500ms | Performance monitoring |
| Support Tickets | < 5/day | Helpdesk system |

---

## Part 3: Full Rollout Testing (44 MOAs)

### 3.1 Scalability Testing

**Priority:** 🔴 CRITICAL
**Tools:** Locust for load generation, Prometheus/Grafana for monitoring

#### Load Test Scenarios

**Scenario 1: Peak Load Simulation (1000 Concurrent Users)**

```python
# locustfile_bmms.py

from locust import HttpUser, task, between
import random

class BMSMUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login as random MOA user."""
        self.moa_code = random.choice(MOA_CODES)  # 44 MOAs
        self.client.post("/accounts/login/", {
            "username": f"{self.moa_code.lower()}_staff",
            "password": "pilot_password"
        })

    @task(10)
    def view_dashboard(self):
        """Most common operation: view dashboard."""
        self.client.get(f"/moa/{self.moa_code}/dashboard/")

    @task(5)
    def list_strategic_plans(self):
        """View strategic plans list."""
        self.client.get(f"/moa/{self.moa_code}/planning/strategic-plans/")

    @task(3)
    def list_budget_proposals(self):
        """View budget proposals."""
        self.client.get(f"/moa/{self.moa_code}/budget/proposals/")

    @task(2)
    def create_assessment(self):
        """Create MANA assessment."""
        self.client.post(f"/moa/{self.moa_code}/mana/assessments/create/", {
            "title": f"Assessment {random.randint(1000, 9999)}",
            "status": "draft"
        })

    @task(1)
    def view_inter_moa_partnerships(self):
        """View inter-MOA partnerships."""
        self.client.get(f"/moa/{self.moa_code}/coordination/inter-moa-partnerships/")
```

**Run Load Test:**
```bash
# Simulate 1000 concurrent users across 44 MOAs
locust -f locustfile_bmms.py --host=https://staging.obcms.gov.ph \
    --users 1000 --spawn-rate 50 --run-time 30m
```

**Acceptance Criteria:**
- ✅ 95% requests complete successfully
- ✅ Average response time < 500ms
- ✅ 95th percentile response time < 1000ms
- ✅ 99th percentile response time < 2000ms
- ✅ No memory leaks detected
- ✅ Database connection pool stable (< 80% utilization)

---

#### Scenario 2: Database Stress Test

```python
@pytest.mark.stress
def test_database_connection_pool_under_load():
    """Verify PgBouncer handles 1000 connections correctly."""
    # Setup: 44 MOAs × 50 users each = 2200 potential connections
    # PgBouncer should pool these to < 200 actual DB connections

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for _ in range(2200):
            moa_code = random.choice(MOA_CODES)
            future = executor.submit(database_query, moa_code)
            futures.append(future)

        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    success_rate = (sum(results) / len(results)) * 100
    assert success_rate >= 99, f"DB connection success rate {success_rate:.1f}% < 99%"
```

---

#### Scenario 3: Redis Cache Performance

```python
def test_redis_cache_hit_rate_under_load():
    """Redis should maintain > 80% cache hit rate under load."""
    # Simulate 10,000 dashboard requests
    hit_count = 0
    miss_count = 0

    for i in range(10000):
        moa_code = random.choice(MOA_CODES)
        cache_key = f'dashboard_stats:{moa_code}'

        if cache.get(cache_key):
            hit_count += 1
        else:
            # Cache miss - fetch from DB and cache
            stats = get_dashboard_stats(moa_code)
            cache.set(cache_key, stats, timeout=300)
            miss_count += 1

    hit_rate = (hit_count / (hit_count + miss_count)) * 100
    assert hit_rate >= 80, f"Cache hit rate {hit_rate:.1f}% < 80%"
```

---

### 3.2 Data Migration Validation

**Priority:** 🔴 CRITICAL
**Scope:** Validate organization field migrations across all modules

#### Pre-Migration Checks

```python
def test_pre_migration_data_snapshot():
    """Create snapshot of all data before migration."""
    snapshot = {
        'strategic_plans': StrategicPlan.objects.count(),
        'budget_proposals': BudgetProposal.objects.count(),
        'assessments': Assessment.objects.count(),
        'partnerships': Partnership.objects.count()
    }

    # Save snapshot to file
    with open('pre_migration_snapshot.json', 'w') as f:
        json.dump(snapshot, f)
```

#### Post-Migration Validation

```python
def test_post_migration_data_integrity():
    """Verify all data preserved and correctly scoped after migration."""
    # Load pre-migration snapshot
    with open('pre_migration_snapshot.json') as f:
        snapshot = json.load(f)

    # Verify counts match
    assert StrategicPlan.objects.count() == snapshot['strategic_plans']
    assert BudgetProposal.objects.count() == snapshot['budget_proposals']

    # Verify all records have organization assigned
    assert StrategicPlan.objects.filter(organization__isnull=True).count() == 0
    assert BudgetProposal.objects.filter(organization__isnull=True).count() == 0

    # Verify OOBC data assigned correctly
    oobc = Organization.objects.get(code='OOBC')
    oobc_plans = StrategicPlan.objects.filter(organization=oobc)
    assert oobc_plans.count() > 0
```

#### Migration Rollback Test

```python
def test_migration_rollback_successful():
    """Verify migration can be rolled back without data loss."""
    # Take snapshot
    pre_rollback_count = StrategicPlan.objects.count()

    # Rollback migration
    call_command('migrate', 'planning', '0001', verbosity=0)

    # Verify data still exists
    assert StrategicPlan.objects.count() == pre_rollback_count

    # Re-apply migration
    call_command('migrate', 'planning', verbosity=0)
```

---

### 3.3 Inter-MOA Partnership Testing

**Priority:** 🟡 HIGH
**Scope:** Validate partnerships work correctly across all 44 MOAs

#### Test Scenarios

**Scenario 1: Complex Multi-MOA Partnership**
```python
def test_5_way_moa_partnership():
    """Test partnership involving 5 MOAs."""
    # Create partnership: MOH (lead) + MOLE + MAFAR + MENRE + MSU
    partnership = InterMOAPartnership.objects.create(
        title="Multi-Sectoral Health & Livelihood Program",
        lead_moa_code='MOH',
        participating_moa_codes=['MOLE', 'MAFAR', 'MENRE', 'MSU'],
        partnership_type='multilateral',
        status='active'
    )

    # Verify all 5 MOAs can view
    for code in ['MOH', 'MOLE', 'MAFAR', 'MENRE', 'MSU']:
        user = User.objects.filter(organization__code=code).first()
        assert partnership.can_view(user) == True

    # Verify non-participant MOAs cannot view
    other_user = User.objects.filter(organization__code='MSWDO').first()
    assert partnership.can_view(other_user) == False
```

**Scenario 2: Partnership Budget Tracking**
```python
def test_partnership_budget_allocation_across_moas():
    """Verify budget commitments from multiple MOAs tracked correctly."""
    partnership = InterMOAPartnership.objects.create(
        title="Regional Infrastructure Project",
        lead_moa_code='MPWH',
        participating_moa_codes=['MOLE', 'MENRE'],
        resource_commitments={
            'MPWH': {'budget': 5000000, 'staff': 10},
            'MOLE': {'budget': 2000000, 'staff': 5},
            'MENRE': {'budget': 1000000, 'staff': 3}
        }
    )

    # Calculate total budget
    total_budget = sum(
        commit['budget']
        for commit in partnership.resource_commitments.values()
    )

    assert total_budget == 8000000

    # Verify OCM can see aggregated budget
    ocm_user = User.objects.get(organization__code='OCM')
    assert partnership.can_view(ocm_user) == True
```

---

### 3.4 Continuous Regression Testing

**Priority:** 🟡 HIGH
**Automation:** CI/CD pipeline integration

#### Automated Regression Suite

```yaml
# .github/workflows/regression-tests.yml

name: BMMS Regression Tests

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  regression:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Dependencies
        run: |
          pip install -r requirements/test.txt

      - name: Run Multi-Tenant Tests
        run: |
          cd src
          pytest organizations/tests/test_data_isolation.py -v --tb=short

      - name: Run Module Scoping Tests
        run: |
          cd src
          pytest planning/tests/test_organization_scoping.py -v
          pytest budget_preparation/tests/test_organization_scoping.py -v
          pytest mana/tests/test_organization_scoping.py -v

      - name: Run Performance Tests
        run: |
          cd src
          PERF=1 pytest tests/performance/ -v --maxfail=1

      - name: Coverage Report
        run: |
          cd src
          pytest --cov=. --cov-report=xml --cov-report=term

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

---

## Part 4: Testing Infrastructure and Tools

### 4.1 Testing Environment Configuration

#### Staging Environment

**File:** `src/obc_management/settings/staging.py`

```python
# Staging-specific test settings
ENABLE_MULTI_TENANT = True
OCM_ORGANIZATION_CODE = 'ocm'
ALLOW_ORGANIZATION_SWITCHING = True

# Database connection pool for load testing
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Celery for async task testing
CELERY_TASK_ALWAYS_EAGER = False  # Test real async behavior
CELERY_TASK_EAGER_PROPAGATES = True  # Propagate exceptions

# Caching for performance testing
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

### 4.2 Test Data Generation

**Command:** `python manage.py generate_test_data`

```python
# src/organizations/management/commands/generate_test_data.py

class Command(BaseCommand):
    """Generate realistic test data for BMMS testing."""

    def add_arguments(self, parser):
        parser.add_argument('--moas', type=int, default=44)
        parser.add_argument('--users-per-moa', type=int, default=10)
        parser.add_argument('--plans-per-moa', type=int, default=5)
        parser.add_argument('--budgets-per-moa', type=int, default=3)

    def handle(self, *args, **options):
        # Create 44 MOAs
        for i in range(options['moas']):
            org = Organization.objects.create(
                code=f'MOA{i:02d}',
                name=f'Ministry {i}',
                org_type='ministry'
            )

            # Create users
            for j in range(options['users_per_moa']):
                user = User.objects.create_user(
                    username=f'{org.code}_user{j}',
                    email=f'user{j}@{org.code.lower()}.gov.ph',
                    organization=org
                )

            # Create strategic plans
            for k in range(options['plans_per_moa']):
                plan = StrategicPlan.objects.create(
                    title=f'{org.name} Strategic Plan {k+1}',
                    organization=org,
                    start_year=2025,
                    end_year=2030
                )

            # Create budget proposals
            for l in range(options['budgets_per_moa']):
                BudgetProposal.objects.create(
                    organization=org,
                    fiscal_year=2025,
                    total_amount=random.randint(1000000, 5000000)
                )
```

---

### 4.3 Monitoring and Observability

#### Grafana Dashboard Configuration

**File:** `config/grafana/dashboards/bmms-testing.json`

Key Metrics to Monitor:
- Request rate (per MOA)
- Response time (p50, p95, p99)
- Error rate (per MOA)
- Database connection pool usage
- Redis cache hit rate
- Celery task queue length

#### Prometheus Alerts

```yaml
# config/prometheus/alerts.yml

groups:
  - name: bmms_testing
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected ({{ $value }} errors/sec)"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "95th percentile response time > 1s"

      - alert: DatabaseConnectionPoolExhausted
        expr: db_connections_active / db_connections_max > 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool > 90% utilized"
```

---

## Part 5: Test Execution Plan

### 5.1 Pre-Deployment Testing Timeline

| Week | Phase | Activities | Exit Criteria |
|------|-------|-----------|---------------|
| **Week 1** | Unit & Integration | Run all existing tests, fix failures | 100% pass rate |
| **Week 2** | Multi-Tenant Tests | Implement organization scoping tests | All modules tested |
| **Week 3** | Performance Baseline | Measure current OOBC performance | Baseline established |
| **Week 4** | Staging Deployment | Deploy to staging, smoke tests | All services operational |

### 5.2 Pilot Testing Timeline

| Week | Phase | Activities | Exit Criteria |
|------|-------|-----------|---------------|
| **Week 5** | Pilot Setup | Onboard 15 pilot users | All users can log in |
| **Week 6** | UAT Round 1 | Execute UAT scenarios 1-5 | 90% task completion |
| **Week 7** | Bug Fixes | Address pilot feedback | Critical issues resolved |
| **Week 8** | UAT Round 2 | Re-test fixed issues | 100% task completion |

### 5.3 Full Rollout Testing Timeline

| Week | Phase | Activities | Exit Criteria |
|------|-------|-----------|---------------|
| **Week 9** | Load Testing | Simulate 44 MOAs, 1000 users | Performance targets met |
| **Week 10** | Scalability Validation | Stress tests, failover tests | System stable |
| **Week 11** | OCM Testing | Aggregation across 44 MOAs | OCM dashboard functional |
| **Week 12** | Final Validation | Sign-off from stakeholders | Production go-live approval |

---

## Part 6: Acceptance Criteria Summary

### 6.1 Production Deployment Go/No-Go Criteria

**✅ GO Criteria (All must pass):**

1. **Data Isolation:** 100% pass rate on cross-organization access tests
2. **Performance:** 95th percentile response time < 1 second under 44 MOA load
3. **Pilot Feedback:** User satisfaction ≥ 8/10
4. **UAT Completion:** 100% critical scenarios completed successfully
5. **Regression:** Zero OOBC functionality regressions detected
6. **Security:** Zero data leakage vulnerabilities found
7. **Scalability:** System handles 1000 concurrent users with 95% success rate
8. **Database:** Connection pool stable under load (< 80% utilization)
9. **Monitoring:** All dashboards operational, alerts configured
10. **Rollback Plan:** Tested and documented

**🔴 NO-GO Criteria (Any triggers delay):**

1. Critical security vulnerability discovered
2. Data corruption detected during migration
3. Performance degradation > 50% from baseline
4. Pilot user satisfaction < 7/10
5. UAT task completion rate < 90%
6. Database connection pool exhaustion under normal load
7. Memory leaks detected in production environment
8. Rollback procedure fails in staging

---

### 6.2 BMMS Pilot Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **User Adoption** | 100% of 15 pilot users active | Login analytics |
| **Data Entry Accuracy** | < 2% error rate | Manual audit |
| **Task Completion Time** | ≤ 120% of OOBC baseline | UAT timing |
| **Support Tickets** | < 5 critical issues/week | Helpdesk tracking |
| **System Uptime** | ≥ 99.5% | Monitoring logs |
| **Performance** | Average response < 500ms | Prometheus metrics |
| **User Satisfaction** | ≥ 8/10 | Weekly surveys |

---

## Part 7: Risk Mitigation and Rollback Plan

### 7.1 Testing Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Data leakage between MOAs** | MEDIUM | CRITICAL | Comprehensive data isolation tests, manual audit |
| **Performance degradation** | MEDIUM | HIGH | Load testing before rollout, horizontal scaling ready |
| **Migration data loss** | LOW | CRITICAL | Full database backup, rollback script tested |
| **Pilot user confusion** | HIGH | MEDIUM | Training sessions, user guides, dedicated support |
| **OCM aggregation failure** | LOW | HIGH | Fallback to individual MOA reports |
| **Redis cache failure** | LOW | MEDIUM | Graceful degradation to database queries |

### 7.2 Rollback Procedures

**Scenario 1: Critical Security Vulnerability**
```bash
# Immediate rollback
cd /opt/obcms
git checkout production-stable
./deploy.sh rollback

# Revert database migrations
cd src
python manage.py migrate planning 0001
python manage.py migrate budget_preparation 0001
python manage.py migrate mana 0001

# Verify OOBC-only mode
python manage.py shell -c "from django.conf import settings; print(settings.ENABLE_MULTI_TENANT)"
# Should output: False
```

**Scenario 2: Performance Degradation**
```bash
# Scale up resources
docker-compose up --scale web=8  # Double web workers

# Enable aggressive caching
# In settings: CACHES['default']['TIMEOUT'] = 3600

# Reduce MOA concurrency temporarily
# Limit to 20 MOAs until optimization complete
```

---

## Part 8: Testing Checklist

### Pre-Deployment Checklist

- [ ] All unit tests passing (99.2%)
- [ ] Data isolation tests 100% pass rate
- [ ] Performance tests meet targets
- [ ] Multi-tenant load tests complete
- [ ] OCM aggregation tested across 44 MOAs
- [ ] Database migrations validated
- [ ] Rollback procedure tested
- [ ] Monitoring dashboards configured
- [ ] Alert rules activated
- [ ] Backup procedures verified

### Pilot Deployment Checklist

- [ ] 15 pilot users onboarded
- [ ] Training sessions completed
- [ ] UAT scenarios executed
- [ ] Pilot feedback collected
- [ ] Critical issues resolved
- [ ] User satisfaction ≥ 8/10
- [ ] Data isolation verified in pilot environment
- [ ] Performance metrics within targets

### Full Rollout Checklist

- [ ] All 44 MOAs data seeded
- [ ] Load testing complete (1000 users)
- [ ] Scalability validated
- [ ] Inter-MOA partnerships tested
- [ ] OCM dashboard functional
- [ ] Security audit passed
- [ ] Final stakeholder approval
- [ ] Production cutover plan ready

---

## Conclusion

This comprehensive testing strategy ensures OBCMS production deployment and BMMS transition are thoroughly validated across all critical dimensions: **security (data isolation), performance (scalability), functionality (UAT scenarios), and reliability (regression testing)**.

**Key Success Factors:**
1. **100% data isolation** - Zero tolerance for cross-organization data leakage
2. **Pilot-driven validation** - Real user feedback before full rollout
3. **Performance at scale** - 44 MOAs, 1000 concurrent users
4. **Continuous regression testing** - Automated CI/CD checks
5. **Clear go/no-go criteria** - Objective deployment decisions

**Next Steps:**
1. Implement missing multi-tenant tests for Planning, Budgeting, MANA modules
2. Execute staging environment validation (4 weeks)
3. Launch pilot with 3 MOAs (8 weeks)
4. Conduct full rollout testing (4 weeks)
5. Production go-live with 44 MOAs

**Estimated Total Testing Duration:** 16 weeks from staging to full production

---

**Document Status:** OFFICIAL
**Last Updated:** October 14, 2025
**Next Review:** After pilot completion
**Owner:** OBCMS Testing Team
**Approval Required From:** Project Lead, Security Team, Infrastructure Team
