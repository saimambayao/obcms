# Implementation Plan - Chat Without AI Fallback

**Project:** OBCMS Chat Enhancement
**Duration:** 4 weeks
**Team:** 5 parallel agents
**Date:** 2025-10-06

---

## Overview

This document outlines the phased implementation of the no-AI-fallback chat system using parallel development agents.

---

## Phase 1: Core Infrastructure (Week 1-2)

### **Agent 1: Entity Extractor**

**Files to Create:**
- `src/common/ai_services/chat/entity_extractor.py`
- `src/common/ai_services/chat/entity_resolvers.py`
- `src/common/tests/test_entity_extractor.py`

**Deliverables:**
1. EntityExtractor class with methods:
   - `extract_entities(query: str) -> Dict`
   - `_extract_location(query: str) -> Optional[Dict]`
   - `_extract_ethnolinguistic_group(query: str) -> Optional[str]`
   - `_extract_livelihood(query: str) -> Optional[str]`
   - `_extract_date_range(query: str) -> Optional[Tuple]`
   - `_extract_status(query: str) -> Optional[str]`
   - `_extract_numbers(query: str) -> List[int]`

2. Entity normalization:
   - LocationResolver (fuzzy matching for locations)
   - DateRangeResolver (natural language dates)
   - EthnicGroupResolver (handle variations)

3. Test coverage: 90%+

**Dependencies:** None

**Estimated Complexity:** Medium

---

### **Agent 2: FAQ Handler**

**Files to Create:**
- `src/common/ai_services/chat/faq_handler.py`
- `src/common/management/commands/update_faq_cache.py`
- `src/common/tests/test_faq_handler.py`

**Deliverables:**
1. FAQHandler class with methods:
   - `try_faq(query: str) -> Optional[Dict]`
   - `add_faq(pattern: str, response: Dict)`
   - `update_stats_cache()`
   - `get_popular_faqs() -> List`

2. Pre-computed FAQ responses:
   - Total communities, workshops, policies
   - Region breakdown
   - System capabilities
   - Common "how to" questions

3. Management command to refresh FAQ cache daily

4. Test coverage: 85%+

**Dependencies:** None

**Estimated Complexity:** Low

---

### **Agent 3: Enhanced Query Templates**

**Files to Create:**
- `src/common/ai_services/chat/query_templates.py`
- `src/common/ai_services/chat/template_matcher.py`
- `src/common/tests/test_query_templates.py`

**Deliverables:**
1. 200+ query templates organized by category:
   - Communities (50 templates)
   - MANA/Workshops (40 templates)
   - Coordination (30 templates)
   - Policies (25 templates)
   - Projects (25 templates)
   - Staff/Tasks (20 templates)
   - General (10 templates)

2. TemplateMatcher class:
   - `find_matching_templates(query, entities, intent) -> List[Template]`
   - Priority-based matching
   - Template validation

3. Template format:
   ```python
   {
       'pattern': r'how many (.+) in (.+)',
       'query_template': '{model}.objects.filter({filters}).count()',
       'required_entities': ['entity_type', 'location'],
       'priority': 10,
       'examples': ['How many communities in Region IX?']
   }
   ```

4. Test coverage: 95%+

**Dependencies:** Entity Extractor (for entity substitution)

**Estimated Complexity:** High

---

### **Agent 4: Clarification Handler**

**Files to Create:**
- `src/common/ai_services/chat/clarification.py`
- `src/templates/common/chat/clarification_dialog.html`
- `src/common/tests/test_clarification.py`

**Deliverables:**
1. ClarificationHandler class:
   - `needs_clarification(query, entities, intent) -> Optional[Dict]`
   - `generate_clarification_dialog(issue_type, context) -> Dict`
   - `apply_clarification(original_query, user_choice) -> str`

2. Clarification templates:
   - Location clarification (region dropdown)
   - Date range clarification (predefined ranges)
   - Ambiguity clarification (multiple interpretations)
   - Missing entity clarification

3. HTMX-powered clarification dialog UI

4. Multi-turn clarification support (session-based)

5. Test coverage: 90%+

**Dependencies:** Entity Extractor

**Estimated Complexity:** Medium

---

## Phase 2: Fallback System (Week 2-3)

### **Agent 5: Fallback Handler**

**Files to Create:**
- `src/common/ai_services/chat/fallback_handler.py`
- `src/common/ai_services/chat/query_corrector.py`
- `src/common/ai_services/chat/similarity.py`
- `src/common/tests/test_fallback_handler.py`

**Deliverables:**
1. FallbackHandler class:
   - `handle_failed_query(query, intent, entities) -> Dict`
   - `generate_suggestions(query) -> List[str]`
   - `find_similar_successful_queries(query) -> List[str]`
   - `analyze_failure_reason(query, intent) -> str`

2. QueryCorrector:
   - Auto-correct common typos
   - Entity spelling correction
   - Suggest alternatives

3. SimilarityCalculator:
   - Levenshtein distance
   - Jaccard similarity
   - Token overlap

4. Fallback response template:
   - Suggested corrections
   - Similar successful queries
   - Query builder prompt
   - Help documentation links

5. Test coverage: 85%+

**Dependencies:** Query Templates, Entity Extractor

**Estimated Complexity:** Medium

---

### **Agent 6: Query Autocomplete**

**Files to Create:**
- `src/common/ai_services/chat/autocomplete.py`
- `src/common/views/chat_autocomplete.py`
- `src/common/tests/test_autocomplete.py`

**Deliverables:**
1. QueryAutocomplete class:
   - `get_suggestions(partial_query, user) -> List[str]`
   - `learn_from_query(query, success) -> None`
   - `get_popular_queries(limit=10) -> List[str]`

2. Suggestion sources:
   - Template-based completions
   - User query history
   - Organization popular queries
   - Entity-aware completions

3. HTMX endpoint: `GET /chat/autocomplete/?q=...`

4. Redis caching (5-minute TTL)

5. Test coverage: 85%+

**Dependencies:** Query Templates, FAQ Handler

**Estimated Complexity:** Low-Medium

---

## Phase 3: Visual Query Builder (Week 3-4)

### **Agent 7: Query Builder Backend**

**Files to Create:**
- `src/common/ai_services/chat/query_builder.py`
- `src/common/views/query_builder.py`
- `src/common/tests/test_query_builder.py`

**Deliverables:**
1. QueryBuilder class:
   - `get_builder_config(entity_type) -> Dict`
   - `build_query(selections) -> str`
   - `preview_query(selections) -> str`
   - `execute_built_query(selections) -> Dict`

2. Builder configuration for each entity:
   - Available filters
   - Filter types (dropdown, date picker, checkbox)
   - Required vs optional filters
   - Default values

3. API endpoints:
   - `GET /query-builder/config/<entity>/`
   - `POST /query-builder/preview/`
   - `POST /query-builder/execute/`

4. Test coverage: 90%+

**Dependencies:** Query Templates, Entity Extractor

**Estimated Complexity:** Medium

---

### **Agent 8: Query Builder Frontend**

**Files to Create:**
- `src/templates/common/chat/query_builder.html`
- `src/static/common/js/query_builder.js` (Alpine.js)
- `src/static/common/css/query_builder.css`

**Deliverables:**
1. Multi-step query builder UI:
   - Step 1: What do you want? (count/list/stats)
   - Step 2: About what? (entity type)
   - Step 3: Where? (location selector)
   - Step 4: When? (date range picker)
   - Step 5: Additional filters (dynamic)
   - Real-time preview
   - Execute button

2. HTMX integration:
   - Dynamic form updates
   - Preview updates without page reload
   - Result display in chat interface

3. Alpine.js state management:
   - Step navigation
   - Form validation
   - Preview generation

4. Responsive design (mobile-friendly)

**Dependencies:** Query Builder Backend

**Estimated Complexity:** Medium-High

---

## Phase 4: Integration & Testing (Week 4)

### **Agent 9: Integration & Refactoring**

**Files to Modify:**
- `src/common/ai_services/chat/chat_engine.py`
- `src/common/ai_services/chat/query_executor.py`
- `src/common/views/chat.py`

**Tasks:**
1. Integrate all new components into ConversationalAssistant:
   ```python
   class ConversationalAssistant:
       def chat(self, user_id, message, session_id):
           # 1. Try FAQ
           faq_result = self.faq_handler.try_faq(message)
           if faq_result:
               return faq_result

           # 2. Extract entities
           entities = self.entity_extractor.extract_entities(message)

           # 3. Check clarification
           clarification = self.clarification_handler.needs_clarification(
               message, entities, intent
           )
           if clarification:
               return clarification

           # 4. Try query execution
           result = self.query_executor.execute(message, entities, intent)
           if result.success:
               return self.response_formatter.format(result)

           # 5. Fallback (NO AI)
           return self.fallback_handler.handle_failed_query(
               message, intent, entities
           )
   ```

2. Remove AI fallback code:
   - Comment out `_fallback_to_gemini()` method
   - Add feature flag for AI fallback (disabled by default)
   - Update error handling

3. Update response formatting:
   - Use new fallback responses
   - Add query builder prompts
   - Improve error messages

**Dependencies:** All previous agents

**Estimated Complexity:** Medium

---

### **Agent 10: Testing & Quality Assurance**

**Files to Create:**
- `src/common/tests/test_chat_integration.py`
- `src/common/tests/test_chat_performance.py`
- `docs/testing/chat_test_plan.md`

**Tasks:**
1. Integration tests:
   - End-to-end query flows
   - Clarification flows
   - Fallback flows
   - Query builder flows

2. Performance benchmarks:
   - Response time tests (<100ms target)
   - Load testing (100 concurrent users)
   - Cache hit rate measurement

3. User acceptance testing:
   - Test with real users
   - Measure satisfaction
   - Gather feedback

4. Regression testing:
   - Ensure existing queries still work
   - Test all 200+ query templates
   - Validate entity extraction accuracy

5. Documentation:
   - User guide for chat system
   - Developer documentation
   - Query syntax reference

**Dependencies:** Integration complete

**Estimated Complexity:** Medium-High

---

## Implementation Timeline

```
Week 1:
  Agent 1: Entity Extractor ████████████████████
  Agent 2: FAQ Handler ██████████████
  Agent 3: Query Templates ████████████████████████████
  Agent 4: Clarification ████████████████

Week 2:
  Agent 3: Query Templates (cont) ██████████
  Agent 5: Fallback Handler ████████████████████
  Agent 6: Autocomplete ██████████████

Week 3:
  Agent 7: Query Builder Backend ████████████████████
  Agent 8: Query Builder Frontend ████████████████████████

Week 4:
  Agent 9: Integration ████████████████
  Agent 10: Testing & QA ██████████████████████

Legend: ██ = Work in progress
```

---

## Parallel Execution Strategy

### **Day 1-3: Kickoff (5 agents in parallel)**

```
Agent 1 (Entity Extractor) → Foundation component
Agent 2 (FAQ Handler) → Independent, quick win
Agent 3 (Query Templates) → Large scope, start early
Agent 4 (Clarification) → Depends on Agent 1
```

Start Agents 1, 2, 3 immediately (Day 1)
Start Agent 4 when Agent 1 at 50% (Day 2)

### **Day 4-7: Fallback System (3 agents)**

```
Agent 5 (Fallback) → Depends on Agents 1, 3
Agent 6 (Autocomplete) → Depends on Agent 3
```

Start Agent 5 when Agent 3 complete
Start Agent 6 when Agent 2 complete

### **Day 8-14: Query Builder (2 agents)**

```
Agent 7 (Backend) → Depends on Agents 1, 3
Agent 8 (Frontend) → Depends on Agent 7
```

Start Agent 7 when Agents 1, 3 complete
Start Agent 8 when Agent 7 at 70%

### **Day 15-21: Integration (2 agents)**

```
Agent 9 (Integration) → Depends on all
Agent 10 (Testing) → Starts with Agent 9
```

---

## Risk Management

### **Risk: Query templates incomplete**
- **Mitigation:** Start with 100 templates, iterate
- **Fallback:** Query builder handles gaps

### **Risk: Entity extraction accuracy low**
- **Mitigation:** Extensive test cases, fuzzy matching
- **Fallback:** Clarification dialogs compensate

### **Risk: Integration breaks existing chat**
- **Mitigation:** Feature flag for new system
- **Fallback:** Can rollback to AI fallback

### **Risk: Performance degradation**
- **Mitigation:** Aggressive caching, benchmarks
- **Fallback:** Optimize critical paths

---

## Success Criteria

### **Functional Requirements**
- ✅ 95%+ query success rate (up from 60%)
- ✅ <100ms average response time (down from 1-3s)
- ✅ Zero AI API calls for chat
- ✅ All existing queries continue working

### **Quality Requirements**
- ✅ 90%+ test coverage
- ✅ Zero critical bugs
- ✅ Performance benchmarks pass
- ✅ Documentation complete

### **User Experience Requirements**
- ✅ 80%+ user satisfaction
- ✅ Clear error messages
- ✅ Query builder accessible
- ✅ Mobile-friendly

---

## Rollout Strategy

### **Phase 1: Internal Testing (Week 4)**
- Deploy to staging
- Internal team testing
- Fix critical bugs

### **Phase 2: Beta Users (Week 5)**
- Select 10 beta users
- Feature flag enabled
- Gather feedback

### **Phase 3: Gradual Rollout (Week 6)**
- 25% of users
- Monitor metrics
- Adjust as needed

### **Phase 4: Full Deployment (Week 7)**
- 100% of users
- AI fallback deprecated
- Celebrate! 🎉

---

## Maintenance Plan

### **Weekly:**
- Review failed query logs
- Add new query templates
- Update FAQ responses

### **Monthly:**
- Analyze usage patterns
- Optimize slow queries
- Update entity dictionaries

### **Quarterly:**
- Review success metrics
- User satisfaction survey
- Feature enhancements

---

## Budget Estimate

**Development Time:**
- 10 agents × 40 hours/week × 4 weeks = 1600 agent-hours
- Actual calendar time: 4 weeks (parallel execution)

**Cost Savings:**
- AI API costs eliminated: ~$50/month
- Annual savings: $600

**ROI:**
- Payback period: Development investment recovered via API cost savings + improved productivity

---

## Conclusion

This implementation plan delivers a production-ready, AI-independent chat system in 4 weeks using parallel development agents.

**Next Steps:**
1. Review and approve plan
2. Launch parallel agents
3. Monitor progress
4. Deploy to production

---

**Plan Owner:** AI Infrastructure Team
**Approval Required:** Technical Lead, Product Manager
**Start Date:** TBD
