# OBCMS Critical Test Issues - Quick Reference

**Date:** 2025-10-06
**Overall Pass Rate:** 62.6% (701/1120 tests)
**Critical Issues:** 3 categories requiring immediate attention

---

## 🔴 CRITICAL ISSUE #1: MonitoringEntry Model Mismatch

**Impact:** 94 test setup errors
**Affected Files:**
- `common/tests/test_workitem_generation_service.py`
- `common/tests/test_workitem_ppa_methods.py`

**Error:**
```python
TypeError: MonitoringEntry() got unexpected keyword arguments: 'name'
```

**Root Cause:**
Test fixtures are calling `MonitoringEntry.objects.create(name=...)` but the model doesn't have a `name` field.

**Fix Required:**
1. Identify correct field name in `MonitoringEntry` model
2. Update all test fixtures in both files (51 tests affected)
3. Verify work item-PPA integration still works

**Files to Update:**
```python
# common/tests/test_workitem_generation_service.py (line 50)
self.ppa = MonitoringEntry.objects.create(
    name="Test PPA",  # ❌ WRONG FIELD
    # Should be: title="Test PPA" or description="Test PPA"
    ...
)

# common/tests/test_workitem_ppa_methods.py (line 46)
# Same issue - update fixture creation
```

---

## 🔴 CRITICAL ISSUE #2: Chat AI JSON Parsing

**Impact:** 12 errors across chat and AI services
**Affected Modules:**
- `common/ai_services/chat/chat_engine.py`
- `recommendations/policies/ai_services/`

**Error:**
```
ERROR AI query generation failed: the JSON object must be str, bytes or bytearray, not dict
```

**Root Cause:**
AI service is returning a dict, but JSON parser expects a string. Inconsistent response handling.

**Fix Required:**
```python
# common/ai_services/chat/chat_engine.py (line 203)
# Current (BROKEN):
query_data = json.loads(ai_response)  # Fails if ai_response is already dict

# Fix:
if isinstance(ai_response, dict):
    query_data = ai_response
else:
    query_data = json.loads(ai_response)
```

**Affected Functions:**
- `chat_engine.py::_generate_query_from_ai()` - Line 203
- `evidence_gatherer.py::gather_evidence()` - Line 170
- `policy_generator.py::generate_policy()` - Line 242, 316
- `compliance_checker.py::check_compliance()` - Line 232
- `impact_simulator.py::simulate_impact()` - Line 240

---

## 🔴 CRITICAL ISSUE #3: Chat Authentication & URLs

**Impact:** 5 test failures in chat widget
**Affected Tests:**
- `test_chat_message_requires_authentication`
- `test_chat_message_success_with_gemini`
- `test_clear_chat_history`

**Error 1: Login URL Mismatch**
```python
# Test expects: /accounts/login/
# System redirects to: /login/

# Fix in settings.py or update test assertion:
assert response.url.startswith('/login/')  # Instead of exact match
```

**Error 2: Missing URL Route**
```python
# django.urls.exceptions.NoReverseMatch: Reverse for 'clear_chat_history' not found

# Fix: Add to common/urls.py
path('chat/clear/', views.clear_chat_history, name='clear_chat_history'),
```

**Error 3: Mock Not Called**
```python
# Test: test_chat_message_success_with_gemini
# Issue: Mock service not being invoked

# Review test setup - ensure mock is properly patched
@patch('common.ai_services.chat.chat_engine.GeminiService.chat_with_ai')
def test_chat_message_success_with_gemini(self, mock_chat_ai):
    # Ensure mock is called with correct path
```

---

## ⚠️ HIGH PRIORITY ISSUES

### Work Items (102 failures)
- Calendar feed generation broken
- Tree hierarchy serialization errors
- Task context validation failing

### PPA/Monitoring (19 failures + 36 errors)
- Celery task failures (auto-sync, budget variance)
- Budget rollup validation broken
- Signal error handling issues

### Performance (10+ slow tests)
- Cache invalidation takes 59 seconds (setup)
- Gemini API tests timeout after 3-5 seconds
- SQLite database locking under concurrency

---

## 📊 Module Health Summary

| Module | Status | Pass Rate | Action Required |
|--------|--------|-----------|-----------------|
| ai_assistant | ✅ Healthy | 91.7% | Minor fixes |
| mana | ✅ Good | 85.1% | Low priority |
| recommendations | ✅ Good | 87.3% | Low priority |
| municipal_profiles | ✅ Good | 83.3% | Low priority |
| coordination | ⚠️ Fair | 72.6% | Medium priority |
| common | ⚠️ Fair | 70.1% | **HIGH PRIORITY** |
| communities | ⚠️ Fair | 67.3% | Medium priority |
| project_central | ⚠️ Fair | 65.9% | Medium priority |
| monitoring | ❌ Poor | 40.0% | **CRITICAL** |
| integration | ❌ Poor | 44.1% | High priority |

---

## 🛠️ Immediate Action Plan

### Today (2-3 hours)
1. ✅ Fix `MonitoringEntry` field name (10 min)
2. ✅ Update 94 test fixtures (30 min)
3. ✅ Fix AI JSON parsing in chat_engine.py (15 min)
4. ✅ Add missing `clear_chat_history` URL route (5 min)
5. ✅ Fix login URL assertion in tests (5 min)
6. ✅ Run tests again - expect ~150 fewer failures

### This Week
1. Refactor work item-PPA integration
2. Fix calendar feed generation
3. Resolve Celery task mocking issues
4. Communities bulk sync fixes

### Before Production
1. Achieve 80%+ test pass rate
2. Fix all CRITICAL and HIGH priority issues
3. Optimize slow tests (reduce total runtime by 50%)
4. PostgreSQL migration readiness testing

---

## 📝 Quick Test Commands

```bash
# Test specific critical areas
pytest common/tests/test_workitem_generation_service.py -v
pytest common/tests/test_chat_comprehensive.py -v
pytest monitoring/tests/ -v

# Run after fixes (expect improvements)
pytest --tb=short -q | tail -5

# Coverage check
coverage run -m pytest --maxfail=0 -q
coverage report --skip-covered
```

---

## 🔍 Root Cause Analysis

### Why So Many Failures?

1. **Model Schema Evolution** (94 errors)
   - Models changed but tests not updated
   - No migration validation in CI/CD

2. **AI Service Inconsistency** (12 errors)
   - Response format varies (dict vs JSON string)
   - No standardized response wrapper

3. **URL Configuration Drift** (5 errors)
   - Routes added without updating tests
   - Login URL changed but tests still expect old path

4. **SQLite Limitations** (7 errors)
   - Concurrency issues in tests
   - Production will use PostgreSQL (fixes this)

---

**Next Review:** After critical fixes are applied
**Expected Outcome:** 850+ tests passing (76%+ pass rate)
**Timeline:** 1-2 days for critical fixes
