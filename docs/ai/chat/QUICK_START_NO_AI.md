# OBCMS Chat System - Quick Start Guide (No AI)

**Last Updated:** 2025-10-06
**Status:** Production Ready

This guide helps you quickly understand and use the AI-free chat system.

---

## 🚀 Quick Start (5 minutes)

### 1. Basic Usage

```python
from common.ai_services.chat.chat_engine import get_conversational_assistant

# Get assistant instance
assistant = get_conversational_assistant()

# Process a query
result = assistant.chat(
    user_id=1,
    message="How many communities in Region IX?"
)

# Display response
print(result['response'])
# Output: "There are 47 communities in Region IX (Zamboanga Peninsula)..."

# Check source (never 'ai' or 'gemini')
print(f"Source: {result['source']}")
# Output: Source: template

# Check performance
print(f"Response time: {result['response_time']:.2f}ms")
# Output: Response time: 87.32ms
```

### 2. Response Structure

```python
{
    'response': str,           # Human-readable response
    'source': str,             # 'faq', 'template', 'clarification', 'fallback'
    'intent': str,             # 'data_query', 'analysis', 'navigation', etc.
    'confidence': float,       # 0.0 to 1.0
    'response_time': float,    # milliseconds
    'data': dict,              # structured data for UI
    'suggestions': list,       # follow-up queries
    'visualization': str       # optional visualization type
}
```

---

## 📋 Pipeline Overview

### 6-Stage Pipeline (NO AI)

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ 1. FAQ Handler      │ ◄── Instant responses (<10ms)
│    - 20+ FAQs       │
│    - Fuzzy match    │
└──────┬──────────────┘
       │ (if no match)
       ▼
┌─────────────────────┐
│ 2. Entity Extractor │ ◄── Extract locations, dates, etc. (<20ms)
│    - Locations      │
│    - Livelihoods    │
│    - Date ranges    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 3. Intent Classifier│ ◄── Pattern-based classification (<10ms)
│    - data_query     │
│    - analysis       │
│    - navigation     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 4. Clarification    │ ◄── Ask if ambiguous (<10ms)
│    Handler          │
└──────┬──────────────┘
       │ (if clear)
       ▼
┌─────────────────────┐
│ 5. Template Matcher │ ◄── 147 templates, query execution (<50ms)
│    + Query Executor │
└──────┬──────────────┘
       │ (if fails)
       ▼
┌─────────────────────┐
│ 6. Fallback Handler │ ◄── Suggestions (NO AI) (<50ms)
│    - Spelling fix   │
│    - Examples       │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│  Response   │
└─────────────┘
```

---

## 🎯 Common Use Cases

### Case 1: FAQ Query

```python
# User: "What can you do?"

result = assistant.chat(user_id=1, message="What can you do?")

print(result['source'])        # 'faq'
print(result['response_time']) # ~5-10ms
print(result['suggestions'])   # Related queries
```

### Case 2: Data Query

```python
# User: "How many communities in Zamboanga?"

result = assistant.chat(user_id=1, message="How many communities in Zamboanga?")

print(result['source'])     # 'template' or 'rule_based'
print(result['intent'])     # 'data_query'
print(result['confidence']) # 0.85-0.95
print(result['data'])       # {'count': 47, 'location': 'Zamboanga', ...}
```

### Case 3: Clarification Needed

```python
# User: "show communities" (ambiguous - which location?)

result = assistant.chat(user_id=1, message="show communities")

if result['type'] == 'clarification':
    print(result['clarification']['message'])
    # "Which region would you like to know about?"

    print(result['clarification']['options'])
    # [
    #   {'label': 'Region IX', 'value': 'region_ix', ...},
    #   {'label': 'Region X', 'value': 'region_x', ...},
    #   ...
    # ]
```

### Case 4: Fallback (Invalid Query)

```python
# User: "xyz abc nonsense 123"

result = assistant.chat(user_id=1, message="xyz abc nonsense 123")

print(result['source'])        # 'fallback'
print(result['suggestions'])   # Corrected queries, examples
print(result['data']['error_analysis'])
# {
#   'likely_issue': 'unrecognized_term',
#   'explanation': '...',
#   'suggestion': '...'
# }
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env
CHAT_USE_AI_FALLBACK=False  # CRITICAL: Must be False in production
FAQ_CACHE_TTL=86400         # 24 hours
CLARIFICATION_TTL=1800      # 30 minutes
```

### Django Settings

```python
# settings/production.py

# Disable AI fallback (CRITICAL)
CHAT_USE_AI_FALLBACK = False

# Cache for FAQ and stats
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## 📊 Monitoring & Debugging

### Check Logs

```bash
# Watch chat activity
tail -f logs/chat.log

# Filter for AI warnings (should be none)
tail -f logs/chat.log | grep "AI fallback"

# Monitor performance
tail -f logs/chat.log | grep "Total time"
```

### Performance Metrics

```python
# Get FAQ stats
from common.ai_services.chat.faq_handler import get_faq_handler

handler = get_faq_handler()
stats = handler.get_faq_stats()

print(f"Total FAQs: {stats['total_faqs']}")
print(f"Total hits: {stats['total_hits']}")
print(f"Hit rate: {stats['hit_rate']}%")
```

### Template Coverage

```python
# Check template registration
from common.ai_services.chat.query_templates import get_template_registry

registry = get_template_registry()
stats = registry.get_stats()

print(f"Total templates: {stats['total_templates']}")
print(f"Categories: {stats['categories']}")
```

---

## 🧪 Testing

### Manual Testing

```python
# Test queries
test_queries = [
    "What can you do?",                      # FAQ
    "How many communities in Region IX?",    # Template
    "show communities",                      # Clarification
    "xyz invalid query",                     # Fallback
]

for query in test_queries:
    result = assistant.chat(user_id=1, message=query)
    print(f"\nQuery: {query}")
    print(f"Source: {result['source']}")
    print(f"Response: {result['response'][:80]}...")
    print(f"Time: {result.get('response_time', 0):.2f}ms")
```

### Run Integration Tests

```bash
cd src

# Run all chat integration tests
pytest common/tests/test_chat_integration_complete.py -v

# Run specific test
pytest common/tests/test_chat_integration_complete.py::ChatIntegrationCompleteTests::test_no_ai_calls_made -v

# Run with coverage
pytest common/tests/test_chat_integration_complete.py --cov=common.ai_services.chat
```

---

## 🐛 Troubleshooting

### Issue: Slow response times

**Symptom:** Response time > 100ms

**Diagnosis:**
```python
# Check each stage
result = assistant.chat(user_id=1, message="test query")
print(f"Total time: {result['response_time']:.2f}ms")

# Check logs for stage breakdown
tail -f logs/chat.log | grep "Stage time"
```

**Fix:**
- Optimize database queries (add indexes)
- Update FAQ cache
- Check Redis connectivity

### Issue: No FAQ matches

**Symptom:** All queries go to template matching

**Diagnosis:**
```python
from common.ai_services.chat.faq_handler import get_faq_handler

handler = get_faq_handler()
result = handler.try_faq("help")
print(result)  # Should not be None
```

**Fix:**
```python
# Update FAQ stats cache
handler.update_stats_cache()
```

### Issue: Template not matching

**Symptom:** Valid query goes to fallback

**Diagnosis:**
```python
from common.ai_services.chat.template_matcher import get_template_matcher

matcher = get_template_matcher()
matches = matcher.find_matching_templates(
    "how many communities",
    {},
    category='communities'
)
print(f"Found {len(matches)} matches")
```

**Fix:**
- Check template registration
- Verify pattern matching
- Add missing template

### Issue: AI calls detected

**Symptom:** Logs show AI fallback warnings

**Diagnosis:**
```bash
grep "AI fallback" logs/chat.log
```

**Fix:**
```python
# Verify setting
from django.conf import settings
print(settings.CHAT_USE_AI_FALLBACK)  # Should be False

# Or set in .env
CHAT_USE_AI_FALLBACK=False
```

---

## 📚 Additional Resources

### Documentation

- **Main README:** `docs/ai/README.md`
- **Architecture:** `docs/ai/fallback/ARCHITECTURE.md`
- **Implementation Status:** `docs/ai/fallback/IMPLEMENTATION_STATUS.md`
- **Entity Extractor:** `src/common/ai_services/chat/ENTITY_EXTRACTOR_README.md`
- **Complete Integration:** `CHAT_NO_AI_INTEGRATION_COMPLETE.md`

### Code Files

- **Chat Engine:** `src/common/ai_services/chat/chat_engine.py`
- **FAQ Handler:** `src/common/ai_services/chat/faq_handler.py`
- **Entity Extractor:** `src/common/ai_services/chat/entity_extractor.py`
- **Template Matcher:** `src/common/ai_services/chat/template_matcher.py`
- **Fallback Handler:** `src/common/ai_services/chat/fallback_handler.py`

### Templates

- **Communities:** `src/common/ai_services/chat/query_templates/communities.py`
- **MANA:** `src/common/ai_services/chat/query_templates/mana.py`
- **Coordination:** `src/common/ai_services/chat/query_templates/coordination.py`
- **Policies:** `src/common/ai_services/chat/query_templates/policies.py`
- **Projects:** `src/common/ai_services/chat/query_templates/projects.py`
- **Staff:** `src/common/ai_services/chat/query_templates/staff_general.py`

---

## ✅ Verification Checklist

Before deploying:

- [ ] `CHAT_USE_AI_FALLBACK=False` in production
- [ ] Redis is running (for caching)
- [ ] FAQ stats cache updated
- [ ] 147 templates registered
- [ ] Integration tests pass
- [ ] Logs show no AI warnings
- [ ] Response times < 100ms
- [ ] Manual testing completed

---

## 🎓 Tips & Best Practices

### 1. Always Check Source

```python
result = assistant.chat(user_id=1, message="query")

# Verify no AI was used
assert result['source'] not in ['ai', 'gemini']
```

### 2. Use FAQ for Common Queries

FAQ responses are instant (<10ms). Add frequently asked questions to FAQ handler.

### 3. Monitor Performance

Set up alerts for queries > 100ms.

### 4. Update Caches Regularly

```python
# Daily task
from common.ai_services.chat.faq_handler import get_faq_handler
handler = get_faq_handler()
handler.update_stats_cache()
```

### 5. Add Missing Templates

If a valid query goes to fallback repeatedly, add a template for it.

---

## 📞 Support

For questions or issues:

1. Check logs: `logs/chat.log`
2. Run diagnostics: `pytest common/tests/test_chat_integration_complete.py`
3. Review documentation: `docs/ai/`
4. File issue: Include query, expected behavior, actual behavior

---

**Quick Start Guide - Version 1.0**
**Last Updated:** 2025-10-06
**Status:** Production Ready ✅
