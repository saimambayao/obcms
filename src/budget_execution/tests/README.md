# Budget Execution Test Suite

Comprehensive test suite for Phase 2B Budget Execution module.

## Test Structure

```
budget_execution/tests/
├── __init__.py
├── conftest.py                          # Pytest configuration
├── fixtures/
│   ├── __init__.py
│   ├── execution_data.py               # Execution fixtures
│   └── test_scenarios.py               # Test scenarios & data
├── test_financial_constraints.py       # CRITICAL: Financial constraint tests
├── test_services.py                    # Service layer tests
├── test_integration.py                 # Full lifecycle integration tests
└── test_performance.py                 # Performance benchmarks
```

## Test Categories

### Financial Constraint Tests (CRITICAL)
**100% pass rate required - These validate financial integrity**

- **Allotment Constraints**: Cannot exceed approved budget
- **Obligation Constraints**: Cannot exceed allotment
- **Disbursement Constraints**: Cannot exceed obligation
- **Status Cascades**: Automatic status updates
- **Transaction Rollback**: Data integrity on failures

### Service Tests
- **AllotmentReleaseService**: Allotment creation and validation
- **ObligationService**: Obligation management
- **DisbursementService**: Payment recording
- **BudgetBalanceService**: Balance calculations

### Integration Tests
- **Full Budget Cycle**: Proposal → Execution → Completion
- **Multi-Program Execution**: Complex scenarios
- **Quarterly Execution**: Phased releases
- **Progressive Disbursement**: 30-30-40 patterns

### Performance Tests
- **Bulk Operations**: 100+ records - Target: < 2s
- **Complex Queries**: 50 programs - Target: < 1s
- **Financial Validation**: 1000 obligations - Target: < 5s
- **Aggregations**: 10,000 line items - Target: < 3s

## Fixtures

### Core Execution Fixtures
- `execution_user` - Budget execution officer
- `allotment_q1` - Q1 allotment (₱10M)
- `allotment_q2` - Q2 allotment (₱12M)
- `work_item` - Test work item for obligations
- `obligation` - Test obligation
- `disbursement` - Test disbursement

### Complex Fixtures
- `complete_execution_cycle` - Full allotment → obligation → disbursement
- `multi_quarter_execution` - Q1-Q4 execution scenario
- `multiple_disbursements` - Progressive payment series

### Integration Fixtures
- `approved_program_budget` - Approved budget ready for execution
- All fixtures from `budget_preparation.tests.fixtures.budget_data`

## Running Tests

### Run all execution tests
```bash
cd src
pytest budget_execution/tests/ -v
```

### Run CRITICAL financial constraint tests
```bash
pytest budget_execution/tests/test_financial_constraints.py -v -m financial
```

### Run integration tests
```bash
pytest budget_execution/tests/test_integration.py -v -m integration
```

### Run performance tests
```bash
pytest budget_execution/tests/test_performance.py -v -m slow
```

### Run with coverage
```bash
pytest budget_execution/tests/ --cov=budget_execution --cov-report=html
```

## Financial Constraint Test Cases

### Obligation Constraints
```python
# MUST FAIL: Exceed allotment
allotment: ₱100M
obligations: [₱60M, ₱50M]  # Total: ₱110M > ₱100M
```

### Disbursement Constraints
```python
# MUST FAIL: Exceed obligation
obligation: ₱50M
disbursements: [₱30M, ₱25M]  # Total: ₱55M > ₱50M
```

### Progressive Disbursement (30-30-40)
```python
# MUST SUCCEED
obligation: ₱10M
disbursements: [₱3M, ₱3M, ₱4M]  # Total: ₱10M = ₱10M
```

## Test Scenarios

### Quarterly Patterns
- **Equal Distribution**: 25-25-25-25%
- **Frontloaded**: 40-30-20-10%
- **Backloaded**: 10-20-30-40%
- **OOBC Realistic**: 20-30-30-20%

### Utilization Scenarios
- **Excellent**: 85% disbursement rate
- **Good**: 65% disbursement rate
- **Poor**: 15% disbursement rate
- **Year-End Rush**: 90% obligated, 40% disbursed

### Category Distributions
- **Personnel Heavy**: 60-30-10%
- **Capital Heavy**: 20-20-60%
- **Balanced**: 40-40-20%
- **OOBC Typical**: 45-35-20%

## Performance Targets

| Test | Records | Target Time |
|------|---------|------------|
| Bulk Line Items | 100 | < 2 seconds |
| Complex Query | 50 programs | < 1 second |
| Financial Validation | 1000 obligations | < 5 seconds |
| Multi-level Aggregation | 10,000 items | < 3 seconds |

## Implementation Status

### ✅ Ready (Structure Complete)
- Test directory structure
- All fixtures defined
- Test templates with comprehensive scenarios
- Financial constraint test cases

### 🚧 Pending (Waiting for Models & Constraints)
- PostgreSQL constraint triggers
- Service implementations
- API endpoints
- Status update logic

### 📋 Implementation Checklist

When models and constraints are ready:
1. Verify PostgreSQL constraints are active
2. Remove `pass` statements and implement tests
3. Run constraint tests: `pytest -m financial`
4. Verify 100% pass rate on constraints
5. Run performance tests: `pytest -m slow`
6. Verify all targets met
7. Run full suite: `pytest budget_execution/`
8. Generate coverage report

## Expected Coverage Targets

- **Financial Constraint Tests**: 100% pass rate (CRITICAL)
- **Model Tests**: 95%+ coverage
- **Service Tests**: 90%+ coverage
- **Integration Tests**: 85%+ coverage
- **Overall**: 90%+ coverage

## Critical Test Patterns

### Testing Financial Constraints
```python
def test_obligation_cannot_exceed_allotment(self, allotment, work_item, user):
    # Create obligation exceeding allotment
    with pytest.raises(IntegrityError) as exc_info:
        with transaction.atomic():
            Obligation.objects.create(
                allotment=allotment,
                amount=allotment.amount * 2,  # Exceeds!
                ...
            )
    assert 'constraint' in str(exc_info.value)
```

### Testing Progressive Disbursement
```python
def test_progressive_30_30_40(self, obligation, user):
    # 30%
    Disbursement.objects.create(
        obligation=obligation,
        amount=obligation.amount * Decimal('0.30'),
        ...
    )
    # 30%
    Disbursement.objects.create(...)
    # 40%
    Disbursement.objects.create(...)

    total = Disbursement.objects.filter(
        obligation=obligation
    ).aggregate(total=Sum('amount'))['total']
    assert total == obligation.amount
```

### Testing Transaction Rollback
```python
def test_rollback_on_error(self, allotment, work_item):
    initial_count = Obligation.objects.count()

    try:
        with transaction.atomic():
            Obligation.objects.create(...)  # Will fail
    except IntegrityError:
        pass

    # No record should be created
    assert Obligation.objects.count() == initial_count
```

## Notes

- **CRITICAL**: Financial constraint tests MUST pass 100%
- All amounts use Decimal for precision
- Fixtures use realistic OOBC budget amounts
- Performance tests validate production readiness
- Integration tests verify complete workflows
