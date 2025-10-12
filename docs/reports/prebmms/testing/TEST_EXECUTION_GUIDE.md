# Budget System Test Execution Guide

**Quick reference for running all Phase 2 Budget System tests**

## Quick Start

```bash
# 1. Setup environment
cd src
export RUN_PLAYWRIGHT_E2E=1
export PLAYWRIGHT_BASE_URL=http://localhost:8000
export PLAYWRIGHT_USERNAME=testuser
export PLAYWRIGHT_PASSWORD=TestPass123!

# 2. Run all tests
pytest budget_preparation/tests budget_execution/tests -v --cov

# 3. View coverage report
coverage html
open htmlcov/index.html
```

## Test Categories

### 1. Unit & Integration Tests (Existing)
```bash
# All unit and integration tests
pytest budget_preparation/tests budget_execution/tests -v

# By category
pytest -m unit -v              # Unit tests only
pytest -m integration -v        # Integration tests only
pytest -m financial -v          # Financial constraints (CRITICAL)
pytest -m slow -v              # Performance tests
```

### 2. E2E Tests (NEW)
```bash
# Prerequisites
pip install playwright pytest-playwright
playwright install

# Set environment variables
export RUN_PLAYWRIGHT_E2E=1
export PLAYWRIGHT_BASE_URL=http://localhost:8000
export PLAYWRIGHT_USERNAME=testuser
export PLAYWRIGHT_PASSWORD=TestPass123!

# Run E2E tests
pytest budget_preparation/tests/test_e2e_budget_preparation.py -v
pytest budget_execution/tests/test_e2e_budget_execution.py -v

# Watch tests in browser
pytest budget_preparation/tests/test_e2e_budget_preparation.py -v --headed

# Run specific test
pytest budget_preparation/tests/test_e2e_budget_preparation.py::TestBudgetProposalCreation::test_create_budget_proposal -v
```

### 3. Load Tests (NEW)
```bash
# Prerequisites
pip install locust

# Start server
python manage.py runserver

# Run load test (web interface)
cd budget_preparation/tests
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089
# Set: Users=500, Spawn Rate=10, Duration=10m

# Run headless with report
locust -f locustfile.py --host=http://localhost:8000 \
       --users=500 --spawn-rate=10 --run-time=10m \
       --headless --html=load_test_report.html

# Quick smoke test
locust -f locustfile.py --host=http://localhost:8000 \
       --users=50 --spawn-rate=5 --run-time=2m --headless
```

### 4. Security Tests (NEW)
```bash
# All security tests
pytest budget_preparation/tests/test_security.py -v

# By category
pytest budget_preparation/tests/test_security.py::TestSQLInjection -v
pytest budget_preparation/tests/test_security.py::TestXSS -v
pytest budget_preparation/tests/test_security.py::TestCSRF -v
pytest budget_preparation/tests/test_security.py::TestAuthorization -v
pytest budget_preparation/tests/test_security.py::TestDataExposure -v
pytest budget_preparation/tests/test_security.py::TestRateLimiting -v

# CRITICAL: Must pass 100%
pytest budget_preparation/tests/test_security.py -v --tb=short
```

### 5. Accessibility Tests (NEW)
```bash
# Prerequisites
pip install axe-playwright-python
playwright install

# Set environment variables
export RUN_PLAYWRIGHT_E2E=1
export PLAYWRIGHT_BASE_URL=http://localhost:8000
export PLAYWRIGHT_USERNAME=testuser
export PLAYWRIGHT_PASSWORD=TestPass123!

# All accessibility tests
pytest budget_execution/tests/test_accessibility.py -v

# By category
pytest budget_execution/tests/test_accessibility.py::TestBudgetPreparationAccessibility -v
pytest budget_execution/tests/test_accessibility.py::TestSpecificAccessibilityRequirements -v
pytest budget_execution/tests/test_accessibility.py::TestResponsiveAccessibility -v

# Watch in browser
pytest budget_execution/tests/test_accessibility.py -v --headed
```

## Complete Test Execution

### Full Test Suite (30-45 minutes)
```bash
#!/bin/bash
# run_all_tests.sh

# Setup
export RUN_PLAYWRIGHT_E2E=1
export PLAYWRIGHT_BASE_URL=http://localhost:8000
export PLAYWRIGHT_USERNAME=testuser
export PLAYWRIGHT_PASSWORD=TestPass123!

cd src

echo "Running Unit & Integration Tests..."
pytest budget_preparation/tests budget_execution/tests \
       -v --cov --cov-report=html --cov-report=term-missing

echo "Running E2E Tests..."
pytest budget_preparation/tests/test_e2e_budget_preparation.py -v
pytest budget_execution/tests/test_e2e_budget_execution.py -v

echo "Running Security Tests..."
pytest budget_preparation/tests/test_security.py -v

echo "Running Accessibility Tests..."
pytest budget_execution/tests/test_accessibility.py -v

echo "Starting Load Test (2 minute smoke test)..."
cd budget_preparation/tests
locust -f locustfile.py --host=http://localhost:8000 \
       --users=100 --spawn-rate=10 --run-time=2m \
       --headless --html=../../../load_test_report.html

echo "All tests complete!"
echo "Coverage report: htmlcov/index.html"
echo "Load test report: load_test_report.html"
```

### Quick Smoke Test (5-10 minutes)
```bash
#!/bin/bash
# quick_test.sh

export RUN_PLAYWRIGHT_E2E=1
export PLAYWRIGHT_BASE_URL=http://localhost:8000
export PLAYWRIGHT_USERNAME=testuser
export PLAYWRIGHT_PASSWORD=TestPass123!

cd src

# Critical tests only
pytest -m financial -v                    # Financial constraints
pytest -m integration -v                  # Integration tests
pytest budget_preparation/tests/test_security.py::TestAuthorization -v  # Auth
pytest budget_execution/tests/test_accessibility.py::TestSpecificAccessibilityRequirements::test_color_contrast -v

echo "Quick smoke test complete!"
```

### Pre-Deployment Checklist
```bash
#!/bin/bash
# pre_deployment_tests.sh

export RUN_PLAYWRIGHT_E2E=1
export PLAYWRIGHT_BASE_URL=http://staging.example.com
export PLAYWRIGHT_USERNAME=testuser
export PLAYWRIGHT_PASSWORD=TestPass123!

cd src

# 1. Unit tests
echo "1. Running unit tests..."
pytest -m unit -v
if [ $? -ne 0 ]; then echo "❌ Unit tests failed"; exit 1; fi

# 2. Financial constraint tests (CRITICAL)
echo "2. Running financial constraint tests..."
pytest -m financial -v
if [ $? -ne 0 ]; then echo "❌ Financial tests failed"; exit 1; fi

# 3. Security tests (CRITICAL)
echo "3. Running security tests..."
pytest budget_preparation/tests/test_security.py -v
if [ $? -ne 0 ]; then echo "❌ Security tests failed"; exit 1; fi

# 4. E2E tests
echo "4. Running E2E tests..."
pytest budget_preparation/tests/test_e2e_budget_preparation.py -v
pytest budget_execution/tests/test_e2e_budget_execution.py -v
if [ $? -ne 0 ]; then echo "❌ E2E tests failed"; exit 1; fi

# 5. Accessibility tests
echo "5. Running accessibility tests..."
pytest budget_execution/tests/test_accessibility.py -v
if [ $? -ne 0 ]; then echo "❌ Accessibility tests failed"; exit 1; fi

# 6. Load test (staging only)
echo "6. Running load test (5 minutes)..."
cd budget_preparation/tests
locust -f locustfile.py --host=$PLAYWRIGHT_BASE_URL \
       --users=200 --spawn-rate=10 --run-time=5m \
       --headless --html=../../../staging_load_report.html
if [ $? -ne 0 ]; then echo "❌ Load test failed"; exit 1; fi

echo "✅ All pre-deployment tests passed!"
```

## Test Results

### Expected Output

#### Unit/Integration Tests
```
==================== test session starts ====================
collected 254 items

budget_preparation/tests/test_models.py ............ [ 10%]
budget_preparation/tests/test_services.py ....... [ 20%]
budget_execution/tests/test_financial_constraints.py .... [ 30%]
budget_execution/tests/test_services.py .......... [ 50%]
budget_execution/tests/test_integration.py ...... [ 70%]
budget_execution/tests/test_performance.py .... [ 90%]

==================== 254 passed in 45.23s ====================
```

#### E2E Tests
```
==================== test session starts ====================
collected 30 items

test_e2e_budget_preparation.py::TestBudgetProposalCreation::test_create_budget_proposal PASSED [ 3%]
test_e2e_budget_preparation.py::TestBudgetProposalCreation::test_add_program_budget PASSED [ 6%]
...
test_e2e_budget_execution.py::TestExecutionWorkflow::test_full_execution_cycle PASSED [100%]

==================== 30 passed in 120.45s ====================
```

#### Load Test Report
```
Type     Name                                    # reqs      # fails  |   Avg   Min   Max  Med  |  req/s
--------|---------------------------------------|-----------|-----------|------|-----|-----|------|-------
GET      /budget/preparation/                     12543         0     |    42    10   245   38  |  20.87
POST     /api/budget/preparation/proposals/        2345         3     |    78    25   512   65  |   3.91
...

Percentage of requests that completed in time:
 50%    38ms
 66%    45ms
 75%    52ms
 80%    58ms
 90%    78ms
 95%    95ms
 98%   124ms
 99%   156ms
100%   245ms

✅ All performance targets met!
Success rate: 99.87%
Average response time: 42ms (target: <50ms)
```

#### Security Tests
```
==================== test session starts ====================
collected 25 items

test_security.py::TestSQLInjection::test_sql_injection_in_search PASSED [ 4%]
test_security.py::TestSQLInjection::test_sql_injection_in_filter PASSED [ 8%]
test_security.py::TestXSS::test_xss_in_proposal_title PASSED [ 12%]
test_security.py::TestCSRF::test_csrf_protection_on_create PASSED [ 16%]
test_security.py::TestAuthorization::test_cannot_access_other_organization_budget PASSED [ 20%]
...

==================== 25 passed in 18.34s ====================
```

#### Accessibility Tests
```
==================== test session starts ====================
collected 17 items

test_accessibility.py::TestBudgetPreparationAccessibility::test_budget_list_accessibility PASSED [ 5%]
test_accessibility.py::TestSpecificAccessibilityRequirements::test_color_contrast PASSED [ 10%]
test_accessibility.py::TestSpecificAccessibilityRequirements::test_form_labels PASSED [ 15%]
test_accessibility.py::TestSpecificAccessibilityRequirements::test_keyboard_accessibility PASSED [ 20%]
...

==================== 17 passed in 45.67s ====================
```

## Troubleshooting

### E2E Tests Not Running
```bash
# Check environment variables
echo $RUN_PLAYWRIGHT_E2E
echo $PLAYWRIGHT_BASE_URL

# Verify Playwright installed
playwright --version

# Reinstall if needed
pip install --upgrade playwright pytest-playwright
playwright install
```

### Load Test Connection Refused
```bash
# Ensure server is running
python manage.py runserver

# Check server accessible
curl http://localhost:8000

# Try different port
python manage.py runserver 8001
# Update locust command with new port
```

### Security Tests Failing
```bash
# Check CSRF settings
# Some tests need enforce_csrf_checks=True

# Check database state
python manage.py migrate

# Reset test database
rm db.sqlite3
python manage.py migrate
python manage.py loaddata test_data.json
```

### Accessibility Tests No Violations Found
```bash
# This is good! But verify:
# 1. Page actually loaded
# 2. axe-playwright installed correctly

pip install --upgrade axe-playwright-python

# Run with headed browser to verify
pytest test_accessibility.py -v --headed
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Budget System Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12

    - name: Install dependencies
      run: |
        pip install -r requirements/development.txt
        playwright install

    - name: Run unit tests
      run: |
        cd src
        pytest budget_preparation/tests budget_execution/tests \
               --cov --cov-report=xml

    - name: Run E2E tests
      env:
        RUN_PLAYWRIGHT_E2E: 1
        PLAYWRIGHT_BASE_URL: http://localhost:8000
      run: |
        cd src
        python manage.py runserver &
        sleep 5
        pytest budget_*/tests/test_e2e*.py -v

    - name: Run security tests
      run: |
        cd src
        pytest budget_preparation/tests/test_security.py -v

    - name: Run accessibility tests
      env:
        RUN_PLAYWRIGHT_E2E: 1
      run: |
        cd src
        pytest budget_execution/tests/test_accessibility.py -v

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## Performance Benchmarks

### Expected Test Execution Times
- Unit tests: 5-10 seconds
- Integration tests: 15-30 seconds
- E2E tests: 60-120 seconds
- Security tests: 15-30 seconds
- Accessibility tests: 30-60 seconds
- Load test (2 min): 2-3 minutes
- Load test (10 min): 10-12 minutes

### Hardware Recommendations
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Optimal**: 16GB RAM, 8 CPU cores

## Test Data Management

### Creating Test Data
```bash
# Load initial test data
python manage.py loaddata budget_test_data.json

# Create test organizations
python manage.py shell
>>> from common.models import Organization
>>> Organization.objects.create(name="Test Org 1")
>>> Organization.objects.create(name="Test Org 2")

# Create test users
python manage.py createsuperuser --username=testadmin
python manage.py create_test_users  # If custom command exists
```

### Cleaning Test Data
```bash
# Reset database
rm db.sqlite3
python manage.py migrate

# Or use test database
python manage.py test --keepdb  # Keeps DB between runs
```

## Support and Resources

### Documentation
- [Budget System Test Suite Complete](./BUDGET_SYSTEM_TEST_SUITE_COMPLETE.md)
- [Budget Test Quick Reference](./BUDGET_TEST_QUICK_REFERENCE.md)
- [Phase 2 Testing Expansion Complete](./PHASE2_TESTING_EXPANSION_COMPLETE.md)

### External Resources
- [Playwright Documentation](https://playwright.dev/python/)
- [Locust Documentation](https://docs.locust.io/)
- [Axe DevTools](https://www.deque.com/axe/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Getting Help
```bash
# Pytest help
pytest --help

# Playwright help
playwright --help

# Locust help
locust --help

# Show available pytest markers
pytest --markers
```

---

**Quick Start**: Run `bash quick_test.sh` for a 5-minute smoke test
**Full Suite**: Run `bash run_all_tests.sh` for complete test coverage
**Pre-Deploy**: Run `bash pre_deployment_tests.sh` before production deployment
