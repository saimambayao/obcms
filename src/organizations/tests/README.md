# Organizations App Test Suite

Comprehensive test suite for the Organizations app (BMMS Phase 1).

## Quick Start

### Run All Tests

```bash
cd src
pytest organizations/tests/ -v
```

### Run Data Isolation Tests (CRITICAL)

```bash
cd src
pytest organizations/tests/test_data_isolation.py -v
```

**Expected Result:** 15/15 tests passing (100% pass rate required)

### Run with Coverage

```bash
cd src
pytest organizations/tests/ --cov=organizations --cov-report=html --cov-report=term-missing -v
```

View coverage report:
```bash
open htmlcov/index.html
```

---

## Test Modules

### 1. test_models.py (18 tests)

Tests Organization and OrganizationMembership models.

**Key Tests:**
- Organization creation and validation
- Unique constraints
- Module flags defaults
- Membership relationships

**Run:**
```bash
pytest organizations/tests/test_models.py -v
```

---

### 2. test_middleware.py (14 tests)

Tests OrganizationMiddleware functionality.

**Key Tests:**
- URL pattern extraction
- Organization context setting
- Access control enforcement
- Thread-local cleanup

**Run:**
```bash
pytest organizations/tests/test_middleware.py -v
```

---

### 3. test_data_isolation.py (15 tests) = CRITICAL

Tests multi-tenant data isolation (security-critical).

**Key Tests:**
- Organization data isolation
- URL tampering prevention
- Cross-organization access control
- Thread-local isolation

**Run:**
```bash
pytest organizations/tests/test_data_isolation.py -v
```

**REQUIREMENT:** 100% pass rate before production deployment.

---

### 4. test_integration.py (18 tests)

Tests complete workflows and user interactions.

**Key Tests:**
- Full request-response cycles
- Organization switching
- Membership management
- Pilot MOA features
- Multi-organization users

**Run:**
```bash
pytest organizations/tests/test_integration.py -v
```

---

## Fixtures

Located in `conftest.py`

### Organization Fixtures
- `org_oobc` - OOBC organization
- `org_moh` - Ministry of Health (pilot)
- `org_mole` - Ministry of Labor (pilot)
- `org_mafar` - Ministry of Agriculture (pilot)
- `pilot_moas` - All 3 pilot MOAs
- `all_44_moas` - Complete set of 44 BARMM MOAs

### User Fixtures
- `regular_user` - User without organization
- `oobc_staff_user` - OOBC staff with membership
- `moh_staff_user` - MOH staff with membership
- `multi_org_user` - User with multiple memberships
- `superuser` - System administrator

### Utility Fixtures
- `test_client` - Django test client
- `request_factory` - Django RequestFactory
- `clean_thread_locals` - Thread-local cleanup

---

## Coverage Targets

| Component | Target | Priority |
|-----------|--------|----------|
| models.py | >90% | HIGH |
| middleware.py | >95% | CRITICAL |
| Data isolation tests | 100% | CRITICAL |
| Overall | >85% | HIGH |

---

## Test Categories

### Security Tests

```bash
pytest organizations/tests/test_data_isolation.py -v
```

All security tests must pass (100% pass rate).

### Integration Tests

```bash
pytest organizations/tests/test_integration.py -v
```

### Unit Tests

```bash
pytest organizations/tests/test_models.py organizations/tests/test_middleware.py -v
```

---

## Troubleshooting

### Tests Not Running

Ensure Organizations app is installed:
```bash
cd src
python manage.py startapp organizations
```

Add to INSTALLED_APPS in `settings/base.py`:
```python
INSTALLED_APPS = [
    # ...
    'organizations',
    # ...
]
```

### Database Errors

Create test database:
```bash
cd src
python manage.py migrate
pytest organizations/tests/ --create-db -v
```

### Import Errors

Ensure you're in the correct directory:
```bash
cd src  # Must be in src/ directory
pytest organizations/tests/ -v
```

---

## Pre-Commit Checklist

Before committing changes:

- [ ] Run all tests: `pytest organizations/tests/ -v`
- [ ] All tests passing (65/65)
- [ ] Data isolation tests: 100% pass rate
- [ ] Coverage >85%
- [ ] No lint errors

---

## Documentation

- [Complete Test Suite Documentation](../../../docs/testing/ORGANIZATIONS_TEST_SUITE.md)
- [BMMS Phase 1 Tasks](../../../docs/plans/bmms/tasks/phase1_foundation_organizations.txt)
- [Organizations App README](../README.md)

---

## Contact

For questions about the test suite:
- Review documentation: `docs/testing/ORGANIZATIONS_TEST_SUITE.md`
- Check BMMS planning: `docs/plans/bmms/`
- Run tests with verbose output: `pytest -vv --tb=long`

---

**CRITICAL:** Data isolation tests must have 100% pass rate before production deployment.
