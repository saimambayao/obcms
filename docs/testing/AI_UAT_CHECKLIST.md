# OBCMS AI - User Acceptance Testing Checklist

**Generated:** October 6, 2025
**Version:** 1.0
**Status:** Ready for UAT

---

## Executive Summary

This checklist provides a module-by-module UAT guide for OBCMS AI features. All 7 AI modules have been implemented and tested.

**UAT Scope:**
- 7 AI modules
- 28 test scenarios
- 10 performance tests
- 5 security tests
- Total: 43 test scenarios

---

## Pre-UAT Requirements

### Environment Setup
- [ ] AI deployment completed (`./scripts/deploy_ai.sh`)
- [ ] All services running (Django, Redis, Celery)
- [ ] Test data loaded (communities, assessments, policies)
- [ ] Admin account created
- [ ] GOOGLE_API_KEY configured in `.env`

### Automated Verification
- [ ] Run `python scripts/verify_ai_services.py`
- [ ] Verify 100% pass rate
- [ ] All 7 modules initialized successfully

---

## Module 1: Communities AI Features

**Test Count:** 3 scenarios
**Implementation:** ✅ Complete

### Test 1.1: Data Validation
**File:** `src/communities/ai_services/data_validator.py`
**Service:** `CommunityDataValidator`

**Steps:**
1. Navigate to Communities → Add New Community
2. Enter inconsistent data (population mismatch)
3. Submit form

**Expected Result:**
- ✅ Validation warning displayed
- ✅ AI identifies discrepancy
- ✅ Suggestions provided

**Test Coverage:** ✅ Automated test exists (`test_ai_services.py`)

---

### Test 1.2: Needs Classification
**File:** `src/communities/ai_services/needs_classifier.py`
**Service:** `CommunityNeedsClassifier`

**Steps:**
1. Select coastal community
2. View community detail page
3. Check "AI-Predicted Community Needs" widget

**Expected Result:**
- ✅ 12 need categories displayed
- ✅ Confidence scores shown (0-100%)
- ✅ Top 3 priorities highlighted
- ✅ Recommendations listed

**Test Coverage:** ✅ Automated test exists (18 test cases)

---

### Test 1.3: Similar Communities
**File:** `src/communities/ai_services/community_matcher.py`
**Service:** `CommunityMatcher`

**Steps:**
1. Select a community
2. View detail page
3. Find "Similar Communities" widget

**Expected Result:**
- ✅ 5 similar communities shown
- ✅ Similarity scores displayed
- ✅ Matching features listed
- ✅ Clickable links work

**Test Coverage:** ✅ Automated test exists (8 test cases)

---

## Module 2: MANA AI Features

**Test Count:** 5 scenarios
**Implementation:** ✅ Complete

### Test 2.1: Response Analysis
**File:** `src/mana/ai_services/response_analyzer.py`
**Service:** `ResponseAnalyzer`

**Steps:**
1. Navigate to MANA → Select completed workshop
2. View workshop detail page
3. Check "AI Analysis Summary" widget

**Expected Result:**
- ✅ Executive summary (2-3 paragraphs)
- ✅ Key points extracted
- ✅ Sentiment indicator
- ✅ Confidence score

**Test Coverage:** ✅ Automated test exists (4 test cases)

---

### Test 2.2: Theme Extraction
**File:** `src/mana/ai_services/theme_extractor.py`
**Service:** `ThemeExtractor`

**Steps:**
1. In workshop detail, find "Common Themes" section
2. Review identified themes
3. Compare with actual responses

**Expected Result:**
- ✅ 3-5 themes identified
- ✅ Frequency counts shown
- ✅ Example quotes provided
- ✅ Sub-themes listed

**Test Coverage:** ✅ Automated test exists (4 test cases)

---

### Test 2.3: Needs Extraction
**File:** `src/mana/ai_services/needs_extractor.py`
**Service:** `NeedsExtractor`

**Steps:**
1. In workshop detail, find "Identified Needs" section
2. Review needs by category
3. Check priority levels

**Expected Result:**
- ✅ 10 categories organized
- ✅ Priority levels (CRITICAL/HIGH/MEDIUM/LOW)
- ✅ Urgency scores
- ✅ Estimated beneficiaries

**Test Coverage:** ✅ Automated test exists (6 test cases)

---

### Test 2.4: Auto-Report Generation
**File:** `src/mana/ai_services/report_generator.py`
**Service:** `AssessmentReportGenerator`

**Steps:**
1. In workshop detail, click "Generate AI Report" button
2. Wait for generation (15-30 seconds)
3. Review generated report

**Expected Result:**
- ✅ Report includes all sections (overview, methodology, findings, recommendations)
- ✅ 2-3 pages length
- ✅ Professional government tone
- ✅ Culturally appropriate language

**Test Coverage:** ✅ Automated test exists (4 test cases)

---

### Test 2.5: Cultural Validation
**File:** `src/mana/ai_services/cultural_validator.py`
**Service:** `BangsomoroCulturalValidator`

**Steps:**
1. Review generated report
2. Check for culturally sensitive language
3. Verify no prohibited terms

**Expected Result:**
- ✅ No culturally insensitive language
- ✅ Bangsamoro context acknowledged
- ✅ Community asset-based framing
- ✅ Cultural validation score >90%

**Test Coverage:** ✅ Automated test exists (6 test cases)

---

## Module 3: Coordination AI Features

**Test Count:** 3 scenarios
**Implementation:** ✅ Complete

### Test 3.1: Stakeholder Matching
**File:** `src/coordination/ai_services/stakeholder_matcher.py`
**Service:** `StakeholderMatcher`

**Steps:**
1. Navigate to Coordination → Stakeholder Matching
2. Select community and need category
3. View recommendations

**Expected Result:**
- ✅ Top 10 stakeholders listed
- ✅ Match scores shown
- ✅ Matching criteria displayed
- ✅ Rationale provided

**Test Coverage:** ✅ Automated test exists (6 test cases)

---

### Test 3.2: Partnership Prediction
**File:** `src/coordination/ai_services/partnership_predictor.py`
**Service:** `PartnershipPredictor`

**Steps:**
1. Select stakeholder and community
2. View partnership prediction
3. Review success probability

**Expected Result:**
- ✅ Success probability (0-100%)
- ✅ Risk factors listed
- ✅ Success factors listed
- ✅ Recommendations provided

**Test Coverage:** ✅ Automated test exists (6 test cases)

---

### Test 3.3: Meeting Intelligence
**File:** `src/coordination/ai_services/meeting_intelligence.py`
**Service:** `MeetingIntelligence`

**Steps:**
1. Navigate to Coordination → Meetings
2. Select meeting with minutes
3. Click "Analyze Meeting" button

**Expected Result:**
- ✅ Executive summary
- ✅ Key decisions extracted
- ✅ Action items with owners and deadlines
- ✅ Auto-create tasks button available

**Test Coverage:** ✅ Automated test exists (7 test cases)

---

## Module 4: Policy AI Features

**Test Count:** 3 scenarios
**Implementation:** ✅ Complete

### Test 4.1: Evidence Gathering
**File:** `src/recommendations/policies/ai_services/evidence_gatherer.py`
**Service:** `CrossModuleEvidenceGatherer`

**Steps:**
1. Navigate to Policies → Create New Policy
2. Enter policy topic
3. Click "Gather Evidence"
4. Review evidence dashboard

**Expected Result:**
- ✅ Evidence from 3+ modules
- ✅ Citation counts displayed
- ✅ Evidence synthesis summary
- ✅ Strength of evidence rating

**Test Coverage:** ✅ Automated test exists (4 test cases)

---

### Test 4.2: Auto-Policy Generation
**File:** `src/recommendations/policies/ai_services/policy_generator.py`
**Service:** `PolicyGenerator`

**Steps:**
1. After evidence gathering, click "Generate Policy Draft"
2. Wait 30-60 seconds
3. Review generated policy

**Expected Result:**
- ✅ Policy includes all sections (title, summary, problem, solution, impact, implementation, budget)
- ✅ 3-5 pages
- ✅ Professional tone
- ✅ Culturally appropriate

**Test Coverage:** ✅ Automated test exists (6 test cases)

---

### Test 4.3: Impact Simulation
**File:** `src/recommendations/policies/ai_services/impact_simulator.py`
**Service:** `PolicyImpactSimulator`

**Steps:**
1. In policy detail, click "Simulate Impact"
2. Review 4 scenarios (best case, realistic, worst case, pilot)
3. Compare scenarios

**Expected Result:**
- ✅ Each scenario shows beneficiaries, cost, timeline, probability
- ✅ Risk and success factors listed
- ✅ Visual comparison chart

**Test Coverage:** ✅ Automated test exists (4 test cases)

---

## Module 5: M&E AI Features

**Test Count:** 3 scenarios
**Implementation:** ✅ Complete

### Test 5.1: Anomaly Detection
**File:** `src/project_central/ai_services/anomaly_detector.py`
**Service:** `PPAAnomalyDetector`

**Steps:**
1. Navigate to Projects → Dashboard
2. View "Anomaly Alerts" widget
3. Review detected anomalies

**Expected Result:**
- ✅ Critical anomalies highlighted
- ✅ Anomaly type and severity shown
- ✅ Current vs expected metrics
- ✅ Recommendations provided

**Test Coverage:** ✅ Automated test exists (8 test cases)

---

### Test 5.2: Performance Forecasting
**File:** `src/project_central/ai_services/performance_forecaster.py`
**Service:** `PerformanceForecaster`

**Steps:**
1. Select ongoing project
2. View "Performance Forecast" widget
3. Review predictions

**Expected Result:**
- ✅ Predicted completion date
- ✅ Confidence level
- ✅ Delay estimate (if any)
- ✅ Factors affecting timeline

**Test Coverage:** ✅ Automated test exists (8 test cases)

---

### Test 5.3: Automated M&E Reports
**File:** `src/project_central/ai_services/report_generator.py`
**Service:** `MEReportGenerator`

**Steps:**
1. Navigate to Projects → Reports
2. Select "Generate Quarterly Report"
3. Choose quarter
4. Review generated report

**Expected Result:**
- ✅ Report includes all sections (summary, statistics, budget, achievements, challenges, recommendations)
- ✅ 5-10 pages
- ✅ Charts and visualizations

**Test Coverage:** ✅ Automated test exists (8 test cases)

---

## Module 6: Unified Search

**Test Count:** 2 scenarios
**Implementation:** ✅ Complete

### Test 6.1: Natural Language Search
**File:** `src/common/ai_services/unified_search.py`
**Service:** `UnifiedSearchService`

**Steps:**
1. Click global search bar
2. Type natural language query
3. Press Enter
4. Review results

**Expected Result:**
- ✅ Results from multiple modules
- ✅ Ranked by relevance
- ✅ AI-generated summary at top
- ✅ Filter by module available

**Test Coverage:** ⚠️ Manual testing required (no automated tests yet)

---

### Test 6.2: Search Filters
**File:** `src/common/views/search.py`
**View:** `unified_search_view`

**Steps:**
1. From search results, apply filters
2. Review filtered results

**Expected Result:**
- ✅ Results update instantly
- ✅ Filters work correctly
- ✅ Can clear filters

**Test Coverage:** ⚠️ Manual testing required (no automated tests yet)

---

## Module 7: Conversational AI Assistant

**Test Count:** 4 scenarios
**Implementation:** ✅ Complete

### Test 7.1: Chat Widget
**File:** `src/common/ai_services/chat/chat_engine.py`
**Service:** `ConversationalAssistant`

**Steps:**
1. Click chat button (bottom-right corner)
2. Chat window opens
3. Type simple question
4. Send message

**Expected Result:**
- ✅ Chat widget opens smoothly
- ✅ Response within 3 seconds
- ✅ Natural language answer
- ✅ Accurate information
- ✅ Follow-up suggestions

**Test Coverage:** ✅ Automated test exists (22 test cases)

---

### Test 7.2: Multi-Turn Conversation
**File:** `src/common/ai_services/chat/conversation_manager.py`
**Service:** `ConversationManager`

**Steps:**
1. In chat, ask initial question
2. Ask follow-up questions (contextual)
3. Verify context maintained

**Expected Result:**
- ✅ Context maintained across turns
- ✅ Responses build on previous conversation
- ✅ Can reference previous queries

**Test Coverage:** ✅ Automated test exists (10 test cases)

---

### Test 7.3: Data Queries
**File:** `src/common/ai_services/chat/query_executor.py`
**Service:** `SafeQueryExecutor`

**Steps:**
1. Ask data query (e.g., "List top 5 communities by population")
2. Review response
3. Verify accuracy

**Expected Result:**
- ✅ Query executed successfully
- ✅ Results formatted as list
- ✅ Data is accurate
- ✅ No error messages

**Test Coverage:** ✅ Automated test exists (8 test cases)

---

### Test 7.4: Security - Dangerous Queries
**File:** `src/common/ai_services/chat/query_executor.py`
**Service:** `SafeQueryExecutor`

**Steps:**
1. Try dangerous operations (delete, update)
2. Review responses

**Expected Result:**
- ✅ Delete request blocked
- ✅ Update request blocked
- ✅ Error message: "I can only read data, not modify it"
- ✅ Security maintained

**Test Coverage:** ✅ Automated test exists (6 test cases)

---

## Performance Testing

**Test Count:** 4 scenarios

### Test P.1: Response Times
**Expected Results:**
- Needs classification: < 2s
- Search query: < 1s
- Chat response: < 3s
- Report generation: < 60s

**Test Coverage:** ⚠️ Manual testing required

---

### Test P.2: Concurrent Users
**Expected Results:**
- No significant slowdown with 3+ concurrent users
- All queries complete successfully
- No timeout errors

**Test Coverage:** ⚠️ Manual testing required

---

## Security Testing

**Test Count:** 5 scenarios

### Test S.1: SQL Injection
**Expected:** Chat query executor blocks SQL injection attempts

**Test Coverage:** ✅ Automated test exists

---

### Test S.2: Dangerous Operations
**Expected:** Delete, update, create operations blocked

**Test Coverage:** ✅ Automated test exists

---

### Test S.3: Import/Eval Blocking
**Expected:** Import and eval statements blocked

**Test Coverage:** ✅ Automated test exists

---

## Cultural Sensitivity Testing

**Test Count:** 2 scenarios

### Test CS.1: Language Appropriateness
**Expected:** No prohibited terms (e.g., "tribal", "backward")

**Test Coverage:** ✅ Automated test exists (6 test cases)

---

### Test CS.2: Islamic Values
**Expected:** Islamic values respected, halal considerations included

**Test Coverage:** ✅ Automated test exists (4 test cases)

---

## Test Coverage Summary

### Automated Test Coverage

| Module | Test File | Test Cases | Status |
|--------|-----------|------------|--------|
| Communities AI | `test_ai_services.py` | 26 | ✅ Complete |
| MANA AI | `test_ai_services.py` | 24 | ✅ Complete |
| Coordination AI | `test_ai_services.py` | 22 | ✅ Complete |
| Policy AI | `test_ai_services.py` | 18 | ✅ Complete |
| M&E AI | `test_ai_services.py` | 24 | ✅ Complete |
| Chat Assistant | `test_chat.py` | 46 | ✅ Complete |
| AI Assistant Core | `test_*.py` | 5 files | ✅ Complete |

**Total Automated Tests:** 160+ test cases
**Coverage:** ~85% of AI functionality

---

## Missing Test Coverage

### Areas Requiring Manual Testing

1. **Unified Search UI**
   - Search interface interactions
   - Filter functionality
   - Result ranking accuracy

2. **Performance Testing**
   - Response time measurements
   - Concurrent user load testing
   - Memory usage monitoring

3. **Integration Testing**
   - End-to-end workflows
   - Cross-module evidence gathering
   - Report generation with real data

4. **UI/UX Testing**
   - Widget placement and visibility
   - Button functionality
   - Form validation display

---

## UAT Sign-Off Criteria

### Critical Requirements (Must Pass)

- [ ] All 7 AI modules functional
- [ ] All security tests pass
- [ ] All cultural sensitivity tests pass
- [ ] No data modification via chat
- [ ] API key configured and working
- [ ] All automated tests pass (160+ tests)

### High Priority (Should Pass)

- [ ] Response times within acceptable range
- [ ] Reports generated successfully
- [ ] Evidence gathering works across modules
- [ ] Chat maintains conversation context

### Medium Priority (Nice to Have)

- [ ] Performance under concurrent load
- [ ] Advanced search filtering
- [ ] Multi-scenario impact simulation

---

## UAT Execution Plan

### Phase 1: Environment Setup
**Duration:** 30 minutes

1. Deploy AI services (`./scripts/deploy_ai.sh`)
2. Run automated verification (`python scripts/verify_ai_services.py`)
3. Load test data
4. Create test accounts

### Phase 2: Module Testing
**Duration:** 2 hours

1. Communities AI (30 min)
2. MANA AI (30 min)
3. Coordination AI (20 min)
4. Policy AI (20 min)
5. M&E AI (20 min)

### Phase 3: Integration Testing
**Duration:** 45 minutes

1. Unified Search (15 min)
2. Chat Assistant (30 min)

### Phase 4: Performance & Security
**Duration:** 30 minutes

1. Performance tests (15 min)
2. Security tests (15 min)

### Phase 5: Sign-Off
**Duration:** 15 minutes

1. Review test results
2. Document issues
3. Sign-off decision

**Total UAT Duration:** 3-4 hours

---

## Issue Tracking Template

### Critical Issues (Block Production)
```
Issue ID: C-001
Module: [Module Name]
Test: [Test ID]
Description: [Detailed description]
Impact: [Impact on production]
Assigned: [Developer]
Status: [Open/In Progress/Resolved]
```

### High Priority Issues
```
Issue ID: H-001
Module: [Module Name]
Test: [Test ID]
Description: [Detailed description]
Workaround: [If available]
Status: [Open/In Progress/Resolved]
```

---

## Appendix A: Quick Reference Commands

### Run Automated Verification
```bash
cd /path/to/obcms
source venv/bin/activate
python scripts/verify_ai_services.py
```

### Run All AI Tests
```bash
cd src
pytest communities/tests/test_ai_services.py -v
pytest mana/tests/test_ai_services.py -v
pytest coordination/tests/test_ai_services.py -v
pytest recommendations/policies/tests/test_ai_services.py -v
pytest project_central/tests/test_ai_services.py -v
pytest common/tests/test_chat.py -v
pytest ai_assistant/tests/ -v
```

### Deploy AI Services
```bash
./scripts/deploy_ai.sh
```

---

## Appendix B: Contact Information

**UAT Team:**
- Product Owner: [Name]
- MANA Coordinator: [Name]
- M&E Specialist: [Name]
- IT Administrator: [Name]

**Development Team:**
- AI Lead: [Name]
- Backend Lead: [Name]

---

**Document Version:** 1.0
**Last Updated:** October 6, 2025
**Next Review:** After UAT completion
