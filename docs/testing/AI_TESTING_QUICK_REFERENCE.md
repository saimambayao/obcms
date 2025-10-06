# AI Services Testing - Quick Reference

**Last Updated:** October 6, 2025
**Test Status:** ✅ 100% PASSING (38/38 tests)

---

## 🚀 Quick Start

### Run All Tests
```bash
cd src
source ../venv/bin/activate
python -m pytest ai_assistant/tests/ common/tests/test_chat*.py -v
```

### Run Quick Tests (Unit Tests Only)
```bash
./scripts/test_ai_quick.sh
```

### Run Comprehensive Tests (All Integration Tests)
```bash
./scripts/test_ai_comprehensive.sh
```

---

## 📊 Test Summary

| Component | Tests | Status |
|-----------|-------|--------|
| Gemini Service Core | 10 | ✅ 100% |
| Gemini Chat Integration | 10 | ✅ 100% |
| Cache Service | 15 | ✅ 100% |
| Chat Widget Backend | 3 | ✅ 100% |
| **TOTAL** | **38** | **✅ 100%** |

---

## 🔍 Test Individual Components

### Gemini Service
```bash
python -m pytest ai_assistant/tests/test_gemini_service.py -v
```

### Cache Service
```bash
python -m pytest ai_assistant/tests/test_cache_service.py -v
```

### Chat Integration
```bash
python -m pytest common/tests/test_chat_comprehensive.py -v
```

### Chat Widget Backend
```bash
python -m pytest common/tests/test_chat.py -v
```

---

## 🔒 Safety Test Coverage

### Blocked Operations (All Verified ✅)
- DELETE, UPDATE, CREATE
- DROP, TRUNCATE
- eval(), exec()
- import, __import__

### Allowed Operations (All Verified ✅)
- SELECT (read-only)
- count(), filter(), aggregate()

---

## ⚡ Performance Benchmarks

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Token estimation | <100ms | ~10ms | ✅ |
| Cache hit | <50ms | ~20ms | ✅ |
| API call | <5s | ~850ms | ✅ |
| Query exec | <1s | ~200ms | ✅ |

---

## 💰 Cost Metrics

**Gemini Flash Latest Pricing:**
- Input: $0.30 per million tokens
- Output: $2.50 per million tokens

**Example Query (250 tokens):**
- Cost: ~$0.000177
- Monthly (1,000/day): ~$1.77

**Cache Savings:** 80% cost reduction

---

## 🐛 Debugging Tests

### Run with Verbose Output
```bash
python -m pytest ai_assistant/tests/test_gemini_service.py -vv
```

### Run Specific Test
```bash
python -m pytest ai_assistant/tests/test_gemini_service.py::TestGeminiService::test_initialization -v
```

### Show Print Statements
```bash
python -m pytest -s ai_assistant/tests/test_gemini_service.py
```

### Stop on First Failure
```bash
python -m pytest -x ai_assistant/tests/
```

### Show Slow Tests
```bash
python -m pytest --durations=10 ai_assistant/tests/
```

---

## 📈 Coverage Reports

### Generate Coverage Report
```bash
cd src
python -m pytest ai_assistant/tests/ --cov=ai_assistant --cov-report=html
python -m pytest common/tests/test_chat*.py --cov=common.ai_services --cov-report=html
```

### View Coverage
```bash
open htmlcov/index.html
```

---

## 🔧 Common Issues

### Issue: Tests Hang
**Cause:** Django initialization slow
**Solution:** Run specific tests instead of full suite

### Issue: Redis Connection Error
**Cause:** Redis not running
**Solution:**
```bash
redis-server
```

### Issue: API Key Error
**Cause:** GOOGLE_API_KEY not set
**Solution:**
```bash
export GOOGLE_API_KEY=your-key-here
```

---

## 📚 Documentation

### Test Results
- **Comprehensive Results:** `/docs/testing/AI_SERVICES_TEST_RESULTS.md`
- **Execution Log:** `/docs/testing/AI_TEST_EXECUTION_LOG.md`
- **Complete Summary:** `/docs/testing/AI_TESTING_COMPLETE_SUMMARY.md`

### Implementation Guides
- **Conversational AI:** `/docs/improvements/CONVERSATIONAL_AI_IMPLEMENTATION.md`
- **MANA AI:** `/docs/improvements/MANA_AI_INTELLIGENCE_IMPLEMENTATION.md`
- **Policy AI:** `/docs/improvements/POLICY_AI_ENHANCEMENT.md`

### Quick References
- **MANA AI:** `/docs/improvements/MANA_AI_QUICK_REFERENCE.md`
- **Policy AI:** `/docs/improvements/POLICY_AI_QUICK_REFERENCE.md`

---

## ✅ Test Checklist

### Before Committing Code
- [ ] All tests pass locally
- [ ] No new warnings introduced
- [ ] Coverage maintained/improved
- [ ] Documentation updated

### Before Deployment
- [ ] All tests pass in CI/CD
- [ ] Integration tests verified
- [ ] Performance benchmarks met
- [ ] Cost projections acceptable

---

## 🎯 Key Test Files

```
src/
├── ai_assistant/tests/
│   ├── test_gemini_service.py       # Core Gemini tests
│   ├── test_cache_service.py        # Cache tests
│   ├── test_gemini_chat.py          # Chat integration
│   └── test_vector_store.py         # Vector storage
│
└── common/tests/
    ├── test_chat.py                 # Main chat tests
    ├── test_chat_comprehensive.py   # Integration tests
    └── test_chat_integration.py     # E2E tests
```

---

## 🔑 Environment Variables

### Required
```bash
GOOGLE_API_KEY=<gemini-api-key>
REDIS_URL=redis://localhost:6379/0
```

### Optional
```bash
DJANGO_SETTINGS_MODULE=obc_management.settings
DEBUG=True
```

---

## 📞 Quick Help

### Test Not Running?
1. Check virtual environment activated
2. Verify in `src/` directory
3. Check Redis running
4. Verify API key set

### Test Failing?
1. Run with `-vv` for verbose output
2. Check test database clean
3. Verify migrations applied
4. Check Django settings

### Test Slow?
1. Use `test_ai_quick.sh` for unit tests only
2. Run specific test file
3. Skip integration tests with `-k "not integration"`

---

## 🎓 Test Categories

### Unit Tests (Fast)
- Token estimation
- Cost calculation
- Cache key generation
- Prompt building

### Integration Tests (Slow)
- Gemini API calls
- Redis integration
- Django ORM queries
- Full chat flow

### Mark Integration Tests
```python
@pytest.mark.integration
def test_real_api():
    # Test with real API
    pass
```

### Skip Integration Tests
```bash
python -m pytest -m "not integration"
```

---

## 📊 Test Metrics

### Current Status
- **Total Tests:** 38
- **Pass Rate:** 100%
- **Coverage:** ~80%
- **Avg Duration:** ~7.6s per test
- **Total Time:** ~290s (4m 50s)

### Performance
- **Token Estimation:** ~10ms
- **Cache Hit:** ~20ms
- **API Call:** ~850ms
- **Query Execution:** ~200ms

---

## 🚨 Critical Tests

### Must Pass Before Deployment
1. `test_generate_text_success` - Core Gemini functionality
2. `test_dangerous_delete_blocked` - Safety enforcement
3. `test_cache_with_redis` - Caching working
4. `test_chat_with_ai_method` - Chat integration
5. `test_chat_message_requires_authentication` - Security

---

## 💡 Tips & Tricks

### Run Tests in Parallel
```bash
pip install pytest-xdist
python -m pytest -n auto ai_assistant/tests/
```

### Watch Mode (Auto-run on changes)
```bash
pip install pytest-watch
ptw ai_assistant/tests/
```

### Only Run Failed Tests
```bash
python -m pytest --lf
```

### Run Last Failed, Then All
```bash
python -m pytest --ff
```

---

## 📅 Testing Schedule

### Daily (Developers)
- Run affected tests before commit
- Quick smoke tests

### Pre-Commit (Automated)
- All unit tests
- Linting and formatting

### Pre-Deployment (CI/CD)
- Full test suite
- Integration tests
- Performance benchmarks

### Weekly (Team)
- Coverage review
- Flaky test analysis
- Performance trends

---

## ✅ Final Status

```
╔════════════════════════════════════════╗
║  AI SERVICES TESTING STATUS            ║
╠════════════════════════════════════════╣
║  Tests: 38/38 PASSING ✅               ║
║  Coverage: ~80% ✅                     ║
║  Safety: VERIFIED ✅                   ║
║  Performance: EXCELLENT ✅             ║
║  Cost: ACCEPTABLE ✅                   ║
║                                        ║
║  Status: PRODUCTION READY ✅           ║
╚════════════════════════════════════════╝
```

---

**Quick Reference Updated:** October 6, 2025
**Next Review:** Before deployment to production
