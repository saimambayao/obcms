# Budget Test Suite - Quick Reference

**Quick guide for implementing and running Phase 2 Budget System tests**

## Directory Structure

```
src/
├── budget_preparation/tests/
│   ├── fixtures/budget_data.py         # 15 fixtures
│   ├── test_models.py                  # 21 tests
│   └── test_services.py                # 19 tests
├── budget_execution/tests/
│   ├── fixtures/execution_data.py      # 15 fixtures
│   ├── fixtures/test_scenarios.py      # Test scenarios
│   ├── test_financial_constraints.py   # 16 CRITICAL tests
│   ├── test_services.py                # 25 tests
│   ├── test_integration.py             # 10 tests
│   └── test_performance.py             # 10 tests
└── pytest.ini                          # Configuration
```

## Quick Commands

### Run All Tests
```bash
cd src
pytest budget_preparation/ budget_execution/ -v
```

### Run Specific Module
```bash
# Budget Preparation only
pytest budget_preparation/ -v

# Budget Execution only
pytest budget_execution/ -v
```

### Run by Category
```bash
# Financial constraints (CRITICAL - 100% pass required)
pytest -m financial -v

# Integration tests
pytest -m integration -v

# Performance tests
pytest -m slow -v

# Unit tests only
pytest -m unit -v
```

### Run Specific Test File
```bash
pytest budget_execution/tests/test_financial_constraints.py -v
pytest budget_preparation/tests/test_models.py -v
```

### Run Specific Test Class
```bash
pytest budget_execution/tests/test_financial_constraints.py::TestObligationConstraints -v
```

### Run Specific Test Method
```bash
pytest budget_execution/tests/test_financial_constraints.py::TestObligationConstraints::test_obligation_cannot_exceed_allotment -v
```

### Coverage Reports
```bash
# Terminal report
pytest --cov=budget_preparation --cov=budget_execution --cov-report=term-missing

# HTML report (detailed)
pytest --cov=budget_preparation --cov=budget_execution --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=budget_preparation --cov=budget_execution --cov-report=xml
```

## Key Fixtures

### Budget Preparation
```python
# Basic fixtures
test_organization          # OOBC organization
test_user                 # Budget officer
test_admin_user           # Budget approver
budget_proposal           # Draft proposal (₱100M)
approved_budget_proposal  # Approved (₱95M)
program_budget            # Program (₱50M)
budget_line_item          # Single line item

# Complex fixtures
complete_budget_structure # Full proposal with programs
multiple_line_items       # Multiple categories

# Planning integration
strategic_plan            # 2024-2028 plan
strategic_goal            # Education goal
annual_work_plan          # FY 2025 plan
monitoring_entry          # PPA/program
```

### Budget Execution
```python
# Basic fixtures
execution_user            # Execution officer
allotment_q1             # Q1 allotment (₱10M)
allotment_q2             # Q2 allotment (₱12M)
work_item                # Work item
obligation               # Obligation (₱5M)
disbursement             # Disbursement

# Complex fixtures
complete_execution_cycle # Full lifecycle
multi_quarter_execution  # Q1-Q4 scenario
multiple_disbursements   # Progressive payments
```

## Test Implementation Checklist

### When Models Are Ready

1. **Remove TODOs**
```bash
# Find all TODOs
grep -r "TODO:" budget_*/tests/

# Implement each test method
```

2. **Implement Model Tests First**
```bash
pytest budget_preparation/tests/test_models.py -v
pytest budget_execution/tests/test_financial_constraints.py -v
```

3. **Then Service Tests**
```bash
pytest budget_preparation/tests/test_services.py -v
pytest budget_execution/tests/test_services.py -v
```

4. **Then Integration Tests**
```bash
pytest budget_execution/tests/test_integration.py -v
```

5. **Finally Performance Tests**
```bash
pytest budget_execution/tests/test_performance.py -v
```

## Critical Tests (Must Pass 100%)

### Financial Constraints
```bash
# These MUST pass before production
pytest budget_execution/tests/test_financial_constraints.py::TestObligationConstraints -v
pytest budget_execution/tests/test_financial_constraints.py::TestDisbursementConstraints -v
pytest budget_execution/tests/test_financial_constraints.py::TestStatusCascades -v
pytest budget_execution/tests/test_financial_constraints.py::TestTransactionRollback -v
```

### Specific Critical Tests
1. `test_obligation_cannot_exceed_allotment` - MUST FAIL when exceeded
2. `test_disbursement_cannot_exceed_obligation` - MUST FAIL when exceeded
3. `test_transaction_rollback_on_error` - MUST rollback on failure
4. `test_status_cascade_when_fully_disbursed` - MUST update status

## Common Test Patterns

### Using Fixtures
```python
def test_something(self, budget_proposal, test_user):
    # Fixtures injected automatically
    assert budget_proposal.submitted_by == test_user
```

### Testing Constraints
```python
def test_constraint(self, allotment):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Obligation.objects.create(
                allotment=allotment,
                amount=allotment.amount * 2  # Exceeds!
            )
```

### Testing Calculations
```python
def test_calculation(self, program_budget):
    program_budget.approved_amount = Decimal('45000000.00')
    variance = program_budget.get_variance()
    assert variance == Decimal('-5000000.00')
```

## Performance Targets

| Test | Target | Command |
|------|--------|---------|
| Bulk line items (100) | < 2s | `pytest budget_execution/tests/test_performance.py::TestBudgetPerformance::test_bulk_line_item_creation` |
| Complex query (50 programs) | < 1s | `pytest budget_execution/tests/test_performance.py::TestBudgetPerformance::test_complex_query_performance` |
| Financial validation (1000) | < 5s | `pytest budget_execution/tests/test_performance.py::TestBudgetPerformance::test_financial_validation_performance` |
| Aggregation (10k items) | < 3s | `pytest budget_execution/tests/test_performance.py::TestBudgetPerformance::test_aggregation_heavy_query` |

## Coverage Targets

| Component | Target | Check |
|-----------|--------|-------|
| Budget Preparation Models | 95%+ | `pytest budget_preparation/tests/test_models.py --cov=budget_preparation.models` |
| Budget Execution Models | 95%+ | `pytest budget_execution/tests/ --cov=budget_execution.models` |
| Overall | 90%+ | `pytest budget_*/tests/ --cov=budget_preparation --cov=budget_execution` |

## Troubleshooting

### Import Errors
```bash
# Make sure you're in src/ directory
cd src
pytest budget_preparation/tests/ -v
```

### Database Errors
```bash
# Create migrations if needed
python manage.py makemigrations budget_preparation budget_execution
python manage.py migrate
```

### Fixture Not Found
```bash
# Check conftest.py imports
cat budget_execution/tests/conftest.py
# Should include pytest_plugins list
```

### Performance Test Failures
```bash
# Run with profiling
pytest -m slow --durations=10 -v
```

## Test Markers Reference

```python
@pytest.mark.django_db        # Enable database
@pytest.mark.integration       # Integration test
@pytest.mark.financial         # Financial constraint (CRITICAL)
@pytest.mark.slow             # Performance test
@pytest.mark.unit             # Fast unit test
@pytest.mark.service          # Service layer test
@pytest.mark.model            # Model test
```

## Useful Options

```bash
# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run last failed tests
pytest --lf

# Run only new/modified tests
pytest --new-first

# Verbose with output
pytest -vv -s

# Parallel execution (with pytest-xdist)
pytest -n auto
```

## Pre-Production Checklist

- [ ] All financial constraint tests pass (100%)
- [ ] Overall coverage ≥ 90%
- [ ] All performance targets met
- [ ] Integration tests pass
- [ ] No N+1 query issues
- [ ] Transaction rollback verified
- [ ] Concurrent access tested
- [ ] Edge cases covered

## Quick Verification

```bash
# Run critical tests
pytest -m financial -v

# Check coverage
pytest --cov=budget_preparation --cov=budget_execution --cov-report=term-missing

# Verify performance
pytest -m slow -v

# Full suite
pytest budget_preparation/ budget_execution/ -v --tb=short
```

## Get Help

```bash
# List all tests
pytest --collect-only

# List all markers
pytest --markers

# Show fixtures
pytest --fixtures

# Verbose help
pytest --help
```
