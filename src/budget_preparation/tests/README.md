# Budget Preparation Test Suite

Comprehensive test suite for Phase 2A Budget Preparation module.

## Test Structure

```
budget_preparation/tests/
├── __init__.py
├── conftest.py                    # Pytest configuration
├── fixtures/
│   ├── __init__.py
│   └── budget_data.py            # Test fixtures
├── test_models.py                # Model unit tests
└── test_services.py              # Service layer tests
```

## Test Categories

### Unit Tests (test_models.py)
- **BudgetProposal**: Creation, validation, status transitions
- **ProgramBudget**: Allocation, variance calculations
- **BudgetLineItem**: Auto-calculation, category validation
- **BudgetJustification**: Ordering, content management

### Service Tests (test_services.py)
- **BudgetBuilderService**: Proposal creation workflow
- **ProposalWorkflowService**: Approval/rejection flows
- **BudgetCalculationService**: Aggregations and totals
- **BudgetValidationService**: Business rule validation

## Fixtures

### Core Fixtures
- `test_organization` - Test MOA organization
- `test_user` - Budget officer user
- `test_admin_user` - Budget director/approver
- `budget_proposal` - Draft budget proposal
- `approved_budget_proposal` - Approved proposal for execution testing
- `program_budget` - Single program budget
- `budget_line_item` - Single line item

### Complex Fixtures
- `complete_budget_structure` - Full proposal with 3 programs and 15 line items
- `multiple_line_items` - Line items across all categories

### Planning Integration
- `strategic_plan` - Test strategic plan (2024-2028)
- `strategic_goal` - Test strategic goal
- `annual_work_plan` - Test annual work plan
- `monitoring_entry` - Test PPA/program

## Running Tests

### Run all budget preparation tests
```bash
cd src
pytest budget_preparation/tests/ -v
```

### Run specific test file
```bash
pytest budget_preparation/tests/test_models.py -v
```

### Run specific test class
```bash
pytest budget_preparation/tests/test_models.py::TestBudgetProposal -v
```

### Run with coverage
```bash
pytest budget_preparation/tests/ --cov=budget_preparation --cov-report=html
```

### Run only unit tests
```bash
pytest budget_preparation/tests/ -m unit
```

## Test Implementation Status

### ✅ Ready (Structure Complete)
- Test directory structure
- Fixture definitions
- Test templates with TODO markers

### 🚧 Pending (Waiting for Models)
- Model creation tests
- Validation tests
- Service method tests
- Integration tests

### 📋 Implementation Checklist

When models are ready:
1. Remove `pass` statements from test methods
2. Implement actual test logic
3. Run test suite: `pytest budget_preparation/`
4. Verify 100% pass rate
5. Check coverage: `pytest --cov-report=html`
6. Fix any failing tests
7. Add additional edge case tests

## Test Data Scenarios

### Small Budget
- Total: ₱10M
- Programs: 2
- Line items per program: 3

### Medium Budget
- Total: ₱100M
- Programs: 5
- Line items per program: 10

### Large Budget
- Total: ₱500M
- Programs: 15
- Line items per program: 30

## Expected Coverage Targets

- **Model Tests**: 95%+ coverage
- **Service Tests**: 90%+ coverage
- **Integration Tests**: 85%+ coverage
- **Overall**: 90%+ coverage

## Common Test Patterns

### Testing Model Creation
```python
def test_create_budget_proposal(self, test_organization, test_user):
    proposal = BudgetProposal.objects.create(
        organization=test_organization,
        fiscal_year=2025,
        title="Test Proposal",
        total_requested_budget=Decimal('100000000.00'),
        submitted_by=test_user
    )
    assert proposal.id is not None
    assert proposal.status == 'draft'
```

### Testing Constraints
```python
def test_unique_constraint(self, test_organization, test_user):
    # Create first
    BudgetProposal.objects.create(...)

    # Duplicate should fail
    with pytest.raises(IntegrityError):
        BudgetProposal.objects.create(...)
```

### Testing Calculations
```python
def test_variance_calculation(self, program_budget):
    program_budget.approved_amount = Decimal('45000000.00')
    program_budget.save()

    variance = program_budget.get_variance()
    assert variance == expected_value
```

## Notes

- All fixtures use realistic OOBC amounts and structures
- Tests use `pytest.mark.django_db` for database access
- Fixtures are reusable across test files
- Helper functions provided for common operations
