# AI Chat Backend Test Quick Start Guide

**5-Minute Guide to Running Backend Tests**

---

## Quick Test Commands

### 1. Run All Backend Tests

```bash
cd src
python -m pytest common/tests/test_chat_backend_comprehensive.py -v
```

**Expected:** 28+ passing tests (84.8% success rate)

---

### 2. Run Specific Test Categories

#### Test Views Only
```bash
pytest common/tests/test_chat_backend_comprehensive.py::ChatMessageViewTest -v
pytest common/tests/test_chat_backend_comprehensive.py::ChatHistoryViewTest -v
pytest common/tests/test_chat_backend_comprehensive.py::ChatStatsViewTest -v
```

#### Test Database Models
```bash
pytest common/tests/test_chat_backend_comprehensive.py::ChatMessageModelTest -v
```

#### Test Security
```bash
pytest common/tests/test_chat_backend_comprehensive.py::ChatSecurityTest -v
```

#### Test Performance
```bash
pytest common/tests/test_chat_backend_comprehensive.py::ChatPerformanceTest -v
```

---

### 3. Generate Coverage Report

```bash
pytest common/tests/test_chat_backend_comprehensive.py \
    --cov=common.views.chat \
    --cov-report=html \
    --cov-report=term-missing
```

**View HTML Report:**
```bash
open htmlcov/index.html
```

---

## Test Results at a Glance

| Component | Tests | Passed | Status |
|-----------|-------|--------|--------|
| chat_message view | 12 | 9 | ⚠️ API limits |
| chat_history view | 7 | 6 | ⚠️ Validation fix needed |
| clear_chat_history view | 4 | 4 | ✅ Perfect |
| chat_stats view | 4 | 4 | ✅ Perfect |
| chat_capabilities view | 3 | 3 | ✅ Perfect |
| chat_suggestion view | 3 | 2 | ⚠️ API limits |

**Total:** 28/33 passing (84.8%)

---

## Known Test Failures

### 1. API Rate Limit Failures (5 tests)

**Cause:** Gemini API free tier limit (10 requests/minute)

**Affected Tests:**
- `test_very_long_message`
- `test_special_characters_in_message`
- `test_concurrent_requests_from_same_user`
- `test_valid_suggestion_click`
- `test_processes_as_regular_message`

**Fix:** Mock Gemini API responses (see fix guide below)

---

### 2. Input Validation Failure (1 test)

**Test:** `test_invalid_limit_parameter`

**Error:** `ValueError: invalid literal for int() with base 10: 'invalid'`

**Fix:** Add try-except in `chat_history` view (see fix #2 below)

---

## Quick Fixes

### Fix #1: Mock Gemini API (Required for full test suite)

**File:** `/src/common/tests/test_chat_backend_comprehensive.py`

Add this fixture at the top of the file:

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_ai_assistant():
    """Mock Gemini AI assistant for testing."""
    assistant = Mock()
    assistant.chat.return_value = {
        'response': 'Mocked response',
        'suggestions': ['Next question 1', 'Next question 2'],
        'intent': 'data_query',
        'confidence': 0.9,
        'data': {},
    }
    return assistant
```

Then update failing tests:

```python
@patch('common.ai_services.chat.get_conversational_assistant')
def test_very_long_message(self, mock_get_assistant, mock_ai_assistant):
    mock_get_assistant.return_value = mock_ai_assistant

    long_message = 'A' * 1500
    response = self.client.post(self.url, {'message': long_message})

    self.assertEqual(response.status_code, 200)
```

---

### Fix #2: Add Input Validation

**File:** `/src/common/views/chat.py`

**Line 76:** Replace this:
```python
limit = int(request.GET.get('limit', 20))
```

With this:
```python
try:
    limit = int(request.GET.get('limit', 20))
    limit = max(1, min(limit, 100))  # Clamp between 1-100
except (ValueError, TypeError):
    return JsonResponse(
        {'error': 'Invalid limit parameter. Must be an integer.'},
        status=400
    )
```

---

### Fix #3: Fix Mock Decorator

**File:** `/src/common/tests/test_chat_backend_comprehensive.py`

**Line 115:** Update this test:

```python
@patch('common.ai_services.chat.get_conversational_assistant')
def test_concurrent_requests_from_same_user(self, mock_get_assistant):  # Add parameter!
    mock_assistant = Mock()
    mock_assistant.chat.return_value = {
        'response': 'Test',
        'suggestions': [],
        'intent': 'general',
    }
    mock_get_assistant.return_value = mock_assistant

    for i in range(5):
        response = self.client.post(self.url, {'message': f'Message {i}'})
        self.assertEqual(response.status_code, 200)
```

---

## Verify Fixes

After applying all 3 fixes, run:

```bash
pytest common/tests/test_chat_backend_comprehensive.py -v
```

**Expected Result:** 33/33 tests passing (100%)

---

## Coverage Target

**Current Coverage:** ~85%
**Target Coverage:** >90%

To achieve target:
1. ✅ Apply all fixes above
2. ✅ Add tests for exception handling
3. ✅ Test edge cases (empty database, concurrent access)

---

## Performance Benchmarks

Run performance tests:

```bash
pytest common/tests/test_chat_backend_comprehensive.py::ChatPerformanceTest -v -s
```

**Expected Results:**
- `chat_history`: <100ms
- `chat_stats`: <100ms
- `clear_chat_history`: <100ms
- `chat_message` (with AI): 2-5 seconds (depends on API)

---

## Continuous Integration (CI)

### GitHub Actions Workflow

Create `.github/workflows/test-chat-backend.yml`:

```yaml
name: Chat Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd src
          pip install -r requirements/development.txt

      - name: Run backend tests
        run: |
          cd src
          pytest common/tests/test_chat_backend_comprehensive.py \
            --cov=common.views.chat \
            --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Issue: "API rate limit exceeded"

**Solution:** Mock the API (see Fix #1 above)

---

### Issue: "Tests timeout"

**Cause:** Actual API calls taking too long

**Solution:**
1. Mock Gemini API
2. Reduce test data size
3. Increase pytest timeout: `pytest --timeout=300`

---

### Issue: "Database locked"

**Cause:** SQLite doesn't handle concurrent writes well

**Solution:** Use `TransactionTestCase` instead of `TestCase`

```python
from django.test import TransactionTestCase

class ChatPerformanceTest(TransactionTestCase):
    # Tests that need concurrent access
```

---

### Issue: "Import errors"

**Cause:** Missing dependencies

**Solution:**
```bash
pip install -r requirements/development.txt
```

---

## Test Data Management

### Reset Test Database

```bash
cd src
python manage.py flush --noinput
```

### Create Test Fixtures

```bash
python manage.py dumpdata common.ChatMessage --indent 2 > fixtures/chat_messages.json
```

### Load Test Fixtures

```bash
python manage.py loaddata fixtures/chat_messages.json
```

---

## Best Practices

1. **Always mock external APIs** in tests
2. **Use fixtures** for reusable test data
3. **Test one thing** per test case
4. **Use descriptive test names**
5. **Clean up after tests** (Django does this automatically)
6. **Run tests before commits**

---

## Quick Reference: pytest Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run only failed tests
pytest --lf

# Show coverage
pytest --cov=common.views.chat

# HTML coverage report
pytest --cov=common.views.chat --cov-report=html

# Run in parallel (faster)
pytest -n auto

# Show slowest tests
pytest --durations=10
```

---

## Next Steps

1. **Apply all 3 fixes** (~1.5 hours)
2. **Re-run tests** (expect 100% pass rate)
3. **Review coverage report** (target >90%)
4. **Deploy to staging** for UAT

---

**Last Updated:** 2025-10-06
**Test File:** `/src/common/tests/test_chat_backend_comprehensive.py`
**Full Report:** `/docs/testing/BACKEND_TEST_RESULTS.md`
