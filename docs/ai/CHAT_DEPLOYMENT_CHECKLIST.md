# OBCMS Chat System - Production Deployment Checklist

**Date:** 2025-10-06
**System:** No-AI Chat Integration
**Status:** Ready for Production

---

## Pre-Deployment Verification

### 1. Code Review

- [x] **Chat engine updated**
  - File: `src/common/ai_services/chat/chat_engine.py`
  - AI fallback removed from active code path
  - Performance logging added
  - All handlers initialized

- [x] **Feature flag verified**
  ```python
  CHAT_USE_AI_FALLBACK = False  # Default
  ```

- [x] **All components integrated**
  - FAQ Handler ✅
  - Entity Extractor ✅
  - Clarification Handler ✅
  - Template Matcher ✅
  - Query Executor ✅
  - Response Formatter ✅
  - Fallback Handler ✅

### 2. Template Registration

- [x] **Verify template count**
  ```bash
  cd src
  python manage.py shell
  >>> from common.ai_services.chat.query_templates import get_template_registry
  >>> registry = get_template_registry()
  >>> stats = registry.get_stats()
  >>> print(f"Total templates: {stats['total_templates']}")
  >>> print(f"Categories: {list(stats['categories'].keys())}")
  >>> exit()
  ```
  **Expected:** 147+ templates across 7 categories

- [x] **Template categories verified**
  - Communities: 40+ templates ✅
  - MANA: 30+ templates ✅
  - Coordination: 25+ templates ✅
  - Policies: 20+ templates ✅
  - Projects: 20+ templates ✅
  - Staff: 10+ templates ✅
  - General: 12+ templates ✅

### 3. FAQ Configuration

- [ ] **Update FAQ statistics cache**
  ```bash
  cd src
  python manage.py shell
  >>> from common.ai_services.chat.faq_handler import get_faq_handler
  >>> handler = get_faq_handler()
  >>> stats_result = handler.update_stats_cache()
  >>> print(f"Updated stats: {stats_result}")
  >>> exit()
  ```

- [ ] **Verify FAQ entries**
  ```bash
  python manage.py shell
  >>> from common.ai_services.chat.faq_handler import get_faq_handler
  >>> handler = get_faq_handler()
  >>> print(f"Total FAQs: {len(handler.base_faqs)}")
  >>> exit()
  ```
  **Expected:** 20+ FAQs

### 4. Environment Configuration

- [ ] **Production .env file**
  ```bash
  # Verify settings
  grep "CHAT_USE_AI_FALLBACK" .env
  ```
  **Expected:** `CHAT_USE_AI_FALLBACK=False` (or not present)

- [ ] **Redis configuration**
  ```bash
  # Test Redis connection
  redis-cli ping
  ```
  **Expected:** `PONG`

- [ ] **Cache settings**
  ```python
  # settings/production.py
  CACHES = {
      'default': {
          'BACKEND': 'django_redis.cache.RedisCache',
          'LOCATION': 'redis://127.0.0.1:6379/1',
      }
  }
  ```

### 5. Database Migrations

- [ ] **Run migrations**
  ```bash
  cd src
  python manage.py migrate
  ```
  **Expected:** All migrations applied

- [ ] **Verify models**
  ```bash
  python manage.py showmigrations common
  ```
  **Expected:** All [X] checked

---

## Testing

### 1. Unit Tests

- [ ] **Run component tests**
  ```bash
  cd src
  pytest common/tests/test_faq_handler.py -v
  pytest common/tests/test_entity_extractor.py -v
  pytest common/tests/test_clarification.py -v
  pytest common/tests/test_template_matcher.py -v
  pytest common/tests/test_fallback_handler.py -v
  ```

### 2. Integration Tests

- [ ] **Run full integration test suite**
  ```bash
  cd src
  pytest common/tests/test_chat_integration_complete.py -v
  ```
  **Expected:** All 25 tests pass

- [ ] **Verify no AI calls**
  ```bash
  pytest common/tests/test_chat_integration_complete.py::ChatIntegrationCompleteTests::test_no_ai_calls_made -v
  ```
  **Expected:** PASSED

- [ ] **Performance benchmark**
  ```bash
  pytest common/tests/test_chat_integration_complete.py::ChatIntegrationCompleteTests::test_performance_benchmarks -v
  ```
  **Expected:** All queries < 100ms

### 3. Manual Testing

- [ ] **Test FAQ queries**
  ```python
  from common.ai_services.chat.chat_engine import get_conversational_assistant
  assistant = get_conversational_assistant()

  # Test FAQ
  result = assistant.chat(user_id=1, message="What can you do?")
  assert result['source'] == 'faq'
  print(f"✓ FAQ: {result['response_time']:.2f}ms")
  ```

- [ ] **Test data queries**
  ```python
  # Test template query
  result = assistant.chat(user_id=1, message="How many communities in Region IX?")
  assert result['source'] in ['template', 'rule_based', 'faq']
  print(f"✓ Data query: {result['response_time']:.2f}ms")
  ```

- [ ] **Test clarification**
  ```python
  # Test clarification
  result = assistant.chat(user_id=1, message="show communities")
  # May trigger clarification or FAQ
  print(f"✓ Clarification test: {result.get('type', 'response')}")
  ```

- [ ] **Test fallback**
  ```python
  # Test fallback
  result = assistant.chat(user_id=1, message="xyz invalid query 123")
  assert result['source'] == 'fallback'
  assert len(result['suggestions']) > 0
  print(f"✓ Fallback: {len(result['suggestions'])} suggestions")
  ```

---

## Performance Verification

### 1. Response Time Benchmarks

- [ ] **Run performance test**
  ```python
  import time
  from common.ai_services.chat.chat_engine import get_conversational_assistant

  assistant = get_conversational_assistant()

  test_queries = [
      "What can you do?",
      "How many communities?",
      "Show my tasks",
      "Go to dashboard",
  ]

  for query in test_queries:
      start = time.time()
      result = assistant.chat(user_id=1, message=query)
      elapsed = (time.time() - start) * 1000
      print(f"{query:30} {elapsed:6.2f}ms | {result['source']}")
  ```

  **Expected:** All < 100ms

### 2. Memory Usage

- [ ] **Check memory footprint**
  ```bash
  # Monitor memory during queries
  ps aux | grep python | grep manage
  ```
  **Expected:** Normal Django process size

### 3. Log Analysis

- [ ] **Check for AI warnings**
  ```bash
  tail -100 logs/chat.log | grep -i "ai fallback"
  ```
  **Expected:** No output (no AI calls)

- [ ] **Monitor response times**
  ```bash
  tail -100 logs/chat.log | grep "Total time"
  ```
  **Expected:** All < 100ms

---

## Deployment Steps

### 1. Backup

- [ ] **Backup current code**
  ```bash
  git branch backup-before-chat-integration
  git push origin backup-before-chat-integration
  ```

- [ ] **Backup database**
  ```bash
  python manage.py dumpdata > backup_before_chat_$(date +%Y%m%d).json
  ```

### 2. Deploy Code

- [ ] **Pull latest changes**
  ```bash
  git pull origin main
  ```

- [ ] **Verify chat engine**
  ```bash
  git log --oneline --grep="chat\|Chat" -10
  ```

- [ ] **Install dependencies** (if any new)
  ```bash
  pip install -r requirements/production.txt
  ```

### 3. Configuration

- [ ] **Update settings**
  ```python
  # Verify in settings/production.py
  CHAT_USE_AI_FALLBACK = False
  ```

- [ ] **Restart services**
  ```bash
  # Restart Django
  sudo systemctl restart obcms-gunicorn

  # Restart Celery (if used)
  sudo systemctl restart obcms-celery
  ```

### 4. Initialize System

- [ ] **Update FAQ cache**
  ```bash
  python manage.py shell
  >>> from common.ai_services.chat.faq_handler import get_faq_handler
  >>> handler = get_faq_handler()
  >>> handler.update_stats_cache()
  >>> exit()
  ```

- [ ] **Clear old caches**
  ```bash
  python manage.py shell
  >>> from django.core.cache import cache
  >>> cache.clear()
  >>> exit()
  ```

---

## Post-Deployment Verification

### 1. Health Checks

- [ ] **System health**
  ```bash
  curl http://localhost:8000/health/
  ```
  **Expected:** 200 OK

- [ ] **Admin access**
  ```bash
  curl -I http://localhost:8000/admin/
  ```
  **Expected:** 200 OK (or 302 redirect to login)

### 2. Chat Functionality

- [ ] **Test via admin interface**
  - Go to `/admin/chat/chatmessage/`
  - Create test message: "What can you do?"
  - Verify response is generated
  - Check response time in logs

- [ ] **Test via API** (if applicable)
  ```bash
  curl -X POST http://localhost:8000/api/chat/ \
    -H "Content-Type: application/json" \
    -d '{"message": "How many communities?", "user_id": 1}'
  ```

### 3. Monitor Logs

- [ ] **Watch logs for errors**
  ```bash
  tail -f logs/chat.log
  ```
  **Watch for:** Response times, sources, any errors

- [ ] **Check for AI warnings**
  ```bash
  tail -f logs/chat.log | grep -i "deprecated\|gemini\|ai"
  ```
  **Expected:** No active AI calls

### 4. Performance Monitoring

- [ ] **Monitor response times (first hour)**
  ```bash
  # Watch response times
  tail -f logs/chat.log | grep "Total time"
  ```
  **Expected:** 90%+ queries < 100ms

- [ ] **Check error rate**
  ```bash
  # Count errors in last 100 queries
  tail -100 logs/chat.log | grep -i "error" | wc -l
  ```
  **Expected:** < 5 errors

---

## Rollback Plan

### If Issues Occur

1. **Immediate rollback**
   ```bash
   git checkout backup-before-chat-integration
   sudo systemctl restart obcms-gunicorn
   ```

2. **Restore database** (if needed)
   ```bash
   python manage.py loaddata backup_before_chat_$(date +%Y%m%d).json
   ```

3. **Clear caches**
   ```bash
   python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.clear()
   >>> exit()
   ```

4. **Notify team**
   - Document issue
   - Review logs
   - Plan fix

---

## Success Criteria

### Must Pass

- [x] All integration tests pass
- [ ] No AI calls detected in logs
- [ ] Response time < 100ms average
- [ ] FAQ cache updated successfully
- [ ] Templates registered (147+)
- [ ] Manual testing successful

### Performance Targets

| Metric | Target | Check |
|--------|--------|-------|
| FAQ response time | <10ms | [ ] |
| Template query time | <100ms | [ ] |
| Fallback response time | <100ms | [ ] |
| Query success rate | >95% | [ ] |
| Error rate | <5% | [ ] |

---

## Documentation

### Verify Available

- [x] Integration Complete Report: `CHAT_NO_AI_INTEGRATION_COMPLETE.md`
- [x] Quick Start Guide: `docs/ai/chat/QUICK_START_NO_AI.md`
- [x] Integration Summary: `CHAT_INTEGRATION_SUMMARY.md`
- [x] This Checklist: `CHAT_DEPLOYMENT_CHECKLIST.md`

### Update After Deployment

- [ ] **Deployment log**
  - Date deployed
  - Version deployed
  - Issues encountered
  - Resolution steps

- [ ] **Performance baseline**
  - Initial response times
  - Query success rate
  - FAQ hit rate

---

## Support Contacts

### Technical Issues

- **Logs:** `logs/chat.log`
- **Code:** `src/common/ai_services/chat/`
- **Tests:** `src/common/tests/test_chat_*.py`
- **Docs:** `docs/ai/`

### Monitoring

- **Performance:** Check `response_time` in logs
- **Errors:** Check Django error logs
- **Usage:** Check `ChatMessage` model in admin

---

## Sign-Off

### Pre-Deployment

- [ ] Technical lead review
- [ ] Code review completed
- [ ] Tests passing
- [ ] Documentation reviewed

### Post-Deployment

- [ ] Deployment successful
- [ ] Health checks passed
- [ ] Performance verified
- [ ] No errors detected

**Deployed By:** ___________________
**Date:** ___________________
**Time:** ___________________
**Status:** ___________________

---

## Notes

```
Record any issues, observations, or recommendations here:




```

---

**Checklist Version:** 1.0
**Date Created:** 2025-10-06
**Status:** Ready for Production ✅
