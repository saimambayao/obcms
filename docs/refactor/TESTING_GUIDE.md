# WorkItem Testing Guide

**Phase 5: Comprehensive Testing Suite**

This guide covers the complete testing infrastructure for the unified WorkItem model.

## Table of Contents

1. [Test Suite Overview](#test-suite-overview)
2. [Running Tests](#running-tests)
3. [Test Coverage](#test-coverage)
4. [Test Structure](#test-structure)
5. [Using Test Factories](#using-test-factories)
6. [Performance Testing](#performance-testing)
7. [CI/CD Integration](#cicd-integration)

---

## Test Suite Overview

The WorkItem testing suite provides comprehensive coverage across all functionality:

### Test Files

| File | Purpose | Coverage |
|------|---------|----------|
| `test_work_item_model.py` | Model tests | Hierarchy, validation, MPTT operations, progress calculation |
| `test_work_item_migration.py` | Migration tests | StaffTask → WorkItem, ProjectWorkflow → WorkItem, data integrity |
| `test_work_item_views.py` | View tests | CRUD operations, permissions, HTMX integration |
| `test_work_item_calendar.py` | Calendar tests | JSON feed, filtering, breadcrumbs, colors |
| `test_work_item_performance.py` | Performance tests | MPTT queries, bulk operations, scalability |
| `test_work_item_integration.py` | Integration tests | End-to-end workflows, multi-user scenarios |
| `test_work_item_factories.py` | Test utilities | Factory classes, fixtures, helpers |

### Test Statistics

- **Total Test Files:** 7
- **Estimated Test Cases:** 150+
- **Target Coverage:** 95%+
- **Performance Benchmarks:** < 100ms for MPTT queries on 1000+ items

---

## Running Tests

### Prerequisites

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install test dependencies
pip install -r requirements/development.txt
```

### Run All Tests

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=common.work_item_model --cov=common.views.work_items --cov-report=html
```

### Run Specific Test Files

```bash
# Model tests only
pytest src/common/tests/test_work_item_model.py -v

# Migration tests only
pytest src/common/tests/test_work_item_migration.py -v

# Performance tests only
pytest src/common/tests/test_work_item_performance.py -v -m performance
```

### Run Specific Test Classes

```bash
# Run hierarchy tests
pytest src/common/tests/test_work_item_model.py::TestWorkItemHierarchy -v

# Run calendar tests
pytest src/common/tests/test_work_item_calendar.py::TestWorkItemCalendarFeed -v
```

### Run Specific Test Methods

```bash
# Run single test
pytest src/common/tests/test_work_item_model.py::TestWorkItemCreation::test_create_project -v
```

### Skip Performance Tests

Performance tests are marked with `@pytest.mark.performance` and can be skipped:

```bash
# Skip performance tests (faster test runs)
pytest -m "not performance"
```

---

## Test Coverage

### Generate Coverage Report

```bash
# HTML report (recommended)
pytest --cov=common --cov-report=html

# Open report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Coverage Targets

| Component | Target Coverage | Critical Files |
|-----------|----------------|----------------|
| Models | 95%+ | `work_item_model.py` |
| Views | 90%+ | `views/work_items.py` |
| Forms | 85%+ | `forms/work_items.py` |
| Admin | 80%+ | `work_item_admin.py` |
| Overall | 90%+ | All WorkItem-related code |

### Coverage Reports

```bash
# Terminal report
pytest --cov=common --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=common --cov-report=xml

# JSON report
pytest --cov=common --cov-report=json
```

---

## Test Structure

### Test Organization

Tests follow the **AAA Pattern** (Arrange, Act, Assert):

```python
@pytest.mark.django_db
class TestWorkItemCreation:
    def test_create_project(self):
        # Arrange
        start_date = date.today()
        due_date = date.today() + timedelta(days=90)

        # Act
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Test Project",
            start_date=start_date,
            due_date=due_date,
        )

        # Assert
        assert project.id is not None
        assert project.work_type == WorkItem.WORK_TYPE_PROJECT
        assert project.parent is None
```

### Fixtures and Conftest

Create `conftest.py` for shared fixtures:

```python
# src/common/tests/conftest.py

import pytest
from django.contrib.auth import get_user_model

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()

@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        password="testpass",
    )

@pytest.fixture
def authenticated_client(client, user):
    """Return authenticated client."""
    client.login(username="testuser", password="testpass")
    return client

@pytest.fixture
def sample_project(user):
    """Create a sample project."""
    return WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title="Sample Project",
        created_by=user,
    )
```

---

## Using Test Factories

### Basic Usage

```python
from common.tests.test_work_item_factories import (
    ProjectFactory,
    ActivityFactory,
    TaskFactory,
    UserFactory,
)

# Create a project
project = ProjectFactory(title="My Project")

# Create with relationships
user = UserFactory()
task = TaskFactory(created_by=user)
task.assignees.add(user)

# Create hierarchy
project = ProjectFactory()
activity = ActivityFactory(parent=project)
task = TaskFactory(parent=activity)
```

### Helper Functions

```python
from common.tests.test_work_item_factories import (
    create_project_hierarchy,
    create_mana_assessment_project,
    create_policy_development_project,
)

# Create complete project structure
project, activities, tasks = create_project_hierarchy(
    num_activities=5,
    num_tasks_per_activity=3,
)

# Create domain-specific projects
mana_project = create_mana_assessment_project()
policy_project = create_policy_development_project()
```

### Custom Factory Usage

```python
# Override factory attributes
project = ProjectFactory(
    title="Custom Project",
    project_data={
        "budget": 1000000,
        "workflow_stage": "implementation",
    },
)

# Create multiple instances
projects = ProjectFactory.create_batch(10)

# Build without saving
unsaved_task = TaskFactory.build()
# Save manually when needed
unsaved_task.save()
```

---

## Performance Testing

### Performance Benchmarks

All performance tests must meet these benchmarks:

| Operation | Target | Test |
|-----------|--------|------|
| `get_ancestors()` | < 100ms | Deep hierarchy (10 levels) |
| `get_descendants()` | < 100ms | Wide tree (1000+ nodes) |
| Bulk create | < 2s | 1000 work items |
| Calendar feed | < 500ms | 100 work items |
| Progress propagation | < 1s | 100 tasks |

### Running Performance Tests

```bash
# Run all performance tests
pytest -m performance -v

# With timing information
pytest -m performance -v --durations=10
```

### Example Performance Test

```python
@pytest.mark.performance
@pytest.mark.django_db
class TestWorkItemMPTTPerformance:
    def test_get_ancestors_performance(self):
        # Create deep hierarchy
        parent = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Root",
        )

        current = parent
        for i in range(9):
            current = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Level {i}",
                parent=current,
            )

        # Measure performance
        start_time = time.time()
        ancestors = current.get_ancestors()
        list(ancestors)
        elapsed_time = (time.time() - start_time) * 1000

        assert elapsed_time < 100, f"Took {elapsed_time:.2f}ms (> 100ms)"
```

---

## CI/CD Integration

### GitHub Actions Configuration

Create `.github/workflows/tests.yml`:

```yaml
name: Run Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_obcms
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements/development.txt

      - name: Run tests
        env:
          DATABASE_URL: postgres://test_user:test_pass@localhost:5432/test_obcms
        run: |
          cd src
          pytest --cov=common --cov-report=xml --cov-report=term-missing

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

      - name: Check coverage threshold
        run: |
          coverage report --fail-under=90
```

### Pre-commit Hook

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        args: ['-v', '--tb=short']
        language: system
        pass_filenames: false
        always_run: true
```

Install pre-commit:

```bash
pip install pre-commit
pre-commit install
```

### Coverage Requirements

Enforce minimum coverage in `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = obc_management.settings
pythonpath = src
markers =
    performance: Calendar performance regression tests (run separately)

addopts =
    --strict-markers
    --cov-fail-under=90
    --maxfail=5
```

---

## Test Data Management

### Test Fixtures (JSON)

Create fixtures for consistent test data:

```bash
# Export test data
python manage.py dumpdata common.WorkItem --indent 2 > src/common/tests/fixtures/work_items.json
```

Load in tests:

```python
@pytest.mark.django_db
class TestWithFixtures:
    fixtures = ['work_items.json']

    def test_with_fixture_data(self):
        # Fixtures are automatically loaded
        assert WorkItem.objects.count() > 0
```

### Database Reset

Use `--reuse-db` for faster test runs:

```bash
# Create test database once
pytest --reuse-db

# Subsequent runs reuse the database
pytest --reuse-db
```

---

## Debugging Tests

### Verbose Output

```bash
# Show all test names
pytest -v

# Show print statements
pytest -s

# Both
pytest -vs
```

### Debugging Failed Tests

```bash
# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show full traceback
pytest --tb=long
```

### Selective Test Execution

```bash
# Run failed tests from last run
pytest --lf

# Run failed first, then others
pytest --ff
```

---

## Best Practices

### 1. Test Independence

Each test should be completely independent:

```python
# ✅ Good - creates own data
def test_create_project():
    project = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title="Test",
    )
    assert project.id is not None

# ❌ Bad - relies on external state
def test_update_project():
    project = WorkItem.objects.first()  # Assumes data exists
    project.title = "Updated"
    project.save()
```

### 2. Clear Test Names

Use descriptive test names:

```python
# ✅ Good
def test_project_cannot_have_project_as_child()
def test_completed_tasks_update_parent_progress()

# ❌ Bad
def test_validation()
def test_progress()
```

### 3. Use Factories

Prefer factories over manual object creation:

```python
# ✅ Good
project = ProjectFactory(title="Test Project")

# ❌ Bad (verbose, error-prone)
project = WorkItem.objects.create(
    work_type=WorkItem.WORK_TYPE_PROJECT,
    title="Test Project",
    status=WorkItem.STATUS_NOT_STARTED,
    priority=WorkItem.PRIORITY_MEDIUM,
    # ... many more fields
)
```

### 4. Test Edge Cases

Always test edge cases and error conditions:

```python
def test_validate_circular_reference():
    """Test that circular parent-child refs are rejected."""
    parent = WorkItem.objects.create(...)
    child = WorkItem.objects.create(parent=parent, ...)

    # Try to create circular reference
    parent.parent = child

    with pytest.raises(ValidationError):
        parent.full_clean()
```

---

## Troubleshooting

### Common Issues

#### 1. Database Lock Errors

```bash
# Use --reuse-db to avoid recreating database
pytest --reuse-db
```

#### 2. Slow Tests

```bash
# Identify slow tests
pytest --durations=10

# Skip performance tests during development
pytest -m "not performance"
```

#### 3. Import Errors

```bash
# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use pytest.ini pythonpath setting
```

#### 4. Factory Import Errors

Ensure factory_boy is installed:

```bash
pip install factory-boy
```

---

## Next Steps

After completing testing:

1. **Review Coverage Report** - Identify gaps in test coverage
2. **Run Performance Benchmarks** - Ensure all tests meet performance targets
3. **Set Up CI/CD** - Automate test execution on all commits
4. **Document Edge Cases** - Add tests for discovered edge cases
5. **Monitor Test Health** - Set up test failure alerts

---

## Summary

The comprehensive test suite ensures:

- ✅ **Model Integrity**: All MPTT operations work correctly
- ✅ **Data Migration**: StaffTask/ProjectWorkflow data preserved
- ✅ **View Functionality**: CRUD operations and permissions enforced
- ✅ **Calendar Integration**: JSON feed and filtering work correctly
- ✅ **Performance**: System scales to 1000+ work items
- ✅ **Integration**: End-to-end workflows function properly

**Target Coverage: 95%+**

**Performance Target: < 100ms for MPTT queries on 1000+ items**

---

**Phase 5 Complete ✓**

Next: [Phase 6 - Production Deployment](./PRODUCTION_DEPLOYMENT.md)
