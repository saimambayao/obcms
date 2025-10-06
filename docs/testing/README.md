# Testing & Verification Documentation

This directory contains testing guides, verification reports, and demo setup documentation for the OBCMS.

## Core Documentation

### Testing Strategy
- **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** - **Comprehensive testing strategy for OBCMS**
  - Complete test taxonomy (unit, integration, E2E, security, performance)
  - Test implementation guides with code examples
  - CI/CD pipeline integration
  - Test directory structure and organization
  - Tools and frameworks for each test type
  - **Start here for all testing guidance**

### E2E Integration Testing (NEW - 2025-10-06)
- **[E2E_QUICK_START.md](E2E_QUICK_START.md)** - **5-minute quick start guide for E2E tests**
  - How to run tests
  - Understanding results
  - Common issues and fixes
  - **Start here for E2E testing**

- **[E2E_TEST_RESULTS.md](E2E_TEST_RESULTS.md)** - **Complete E2E test results report**
  - All 10 scenarios detailed
  - Performance metrics
  - Cost analysis
  - Issues and recommendations

- **[E2E_TEST_VISUAL_SUMMARY.md](E2E_TEST_VISUAL_SUMMARY.md)** - **Visual summary and charts**
  - Quick reference card
  - Performance dashboard
  - Coverage heatmap
  - Production readiness checklist

### 🆕 2025 Improvements & Research
- **[TESTING_IMPROVEMENTS_SUMMARY.md](TESTING_IMPROVEMENTS_SUMMARY.md)** - **Executive Summary of 2025 Research & Improvements**
  - ✅ Phase 1 complete (S3 fix, pytest guidance, markers)
  - Critical gaps identified with implementation roadmap
  - Test prioritization matrix (High/Medium/Low ROI)
  - Philippine government security requirements
  - Quick reference for what's been done and what's next

- **[TESTING_STRATEGY_IMPROVEMENTS_2025.md](TESTING_STRATEGY_IMPROVEMENTS_2025.md)** - **Detailed Improvements Guide**
  - ⚠️ 9 critical gaps with severity ratings
  - Complete code examples for all new test types (HTMX, Admin, Regional Isolation)
  - Philippine DICT cybersecurity compliance requirements
  - OBCMS-specific test scenarios
  - **Use this as implementation guide for Phase 2 & 3**

### Test Verification Reports
- **[FULL_SUITE_TEST_REPORT.md](FULL_SUITE_TEST_REPORT.md)** - Complete test suite execution report
- **[MANA_TEST_VERIFICATION.md](MANA_TEST_VERIFICATION.md)** - Comprehensive MANA system testing verification
- **[PRODUCTION_TEST_RESULTS.md](PRODUCTION_TEST_RESULTS.md)** - Production deployment test results and findings

### Demo & Testing Environments
- **[REGION_X_DEMO.md](REGION_X_DEMO.md)** - Region X demo environment setup and data
- **[TEST_CREDENTIALS.md](TEST_CREDENTIALS.md)** - Test account credentials (DO NOT commit real credentials)

## Quick Start

### Running Tests

**All tests:**
```bash
pytest
```

**By test type:**
```bash
# Unit tests only
pytest -m unit -v

# Integration tests
pytest -m integration -v

# API tests
pytest -m api -v

# E2E tests
pytest src/tests/e2e/ -v

# Smoke tests (critical paths)
pytest -m smoke -v
```

**By application:**
```bash
# Test specific app
pytest src/mana/tests/

# Test specific file
pytest src/mana/tests/test_models.py

# Test specific function
pytest src/mana/tests/test_models.py::test_assessment_creation
```

**With coverage:**
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Test Types Overview

### 1. Unit Tests
Located in each Django app under `tests/` directory.
- Test isolated functions, methods, and classes
- Fast execution (< 10 seconds for all unit tests)
- 80%+ coverage target

### 2. Integration Tests
Test interactions between components.
- Database transactions
- Celery task execution
- File uploads
- Multi-app workflows

### 3. API Tests
Validate REST API endpoints.
- Authentication & authorization
- CRUD operations
- Filtering & pagination
- Error handling

### 4. End-to-End (E2E) Tests
Test complete user workflows with Playwright.
- Login flows
- MANA assessment workflows
- Coordination event scheduling
- HTMX instant UI updates

### 5. Security Tests
- OWASP Top 10 testing
- Access control validation
- SQL injection protection
- SAST/DAST scanning

### 6. Performance Tests
Load testing with Locust.
- Baseline load tests
- Stress tests
- Database query performance

### 7. Accessibility Tests
WCAG 2.1 AA compliance.
- Automated axe-core scans
- Keyboard navigation
- Screen reader compatibility

See **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** for detailed implementation guidance.

## Creating Test Data

### Development Environment
```bash
cd src
python manage.py setup_mana_test_data
python manage.py setup_region_x_demo
```

### Automated Test Data
Use Django fixtures or management commands to create consistent test datasets.

## Security Notes

⚠️ **IMPORTANT:** This directory may contain test credentials. Ensure:
- Never commit real production credentials
- Use separate test accounts with limited permissions
- Rotate test credentials regularly
- Mark test accounts clearly in the database

## Related Documentation
- [Development Environment](../env/development.md)
- [Testing Environment](../env/testing.md)
- [Deployment Checklist](../deployment/regional_mana_deployment_checklist.md)
