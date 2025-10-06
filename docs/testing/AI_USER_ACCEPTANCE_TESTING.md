# OBCMS AI - User Acceptance Testing (UAT) Guide

**Version:** 1.0
**Date:** October 6, 2025
**Estimated Time:** 2-3 hours

---

## Overview

This guide helps OOBC staff test all AI features before production deployment. Complete each test scenario and document results.

**Testing Team:**
- Product Owner / Manager
- MANA Coordinator
- M&E Specialist
- IT Administrator

---

## Pre-Testing Checklist

- [ ] AI deployment completed (`./scripts/deploy_ai.sh`)
- [ ] All services running (Django, Redis, Celery)
- [ ] Test data loaded (communities, assessments, policies)
- [ ] Admin account created
- [ ] GOOGLE_API_KEY configured

---

## Test Scenarios

### Module 1: Communities AI Features

#### Test 1.1: Data Validation

**Objective:** Verify AI catches data inconsistencies

**Steps:**
1. Navigate to Communities → Add New Community
2. Enter inconsistent data:
   - Total Population: 5000
   - Households: 50
   - Male: 3000
   - Female: 3000
3. Submit form

**Expected Result:**
- ✅ Form shows validation warning
- ✅ Warning indicates: "Total population (5000) doesn't match male (3000) + female (3000)"
- ✅ Suggestion provided: "Review population data for accuracy"

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________
```

---

#### Test 1.2: Needs Classification

**Objective:** AI predicts community needs

**Steps:**
1. Navigate to Communities → Select any coastal community
2. View community detail page
3. Look for "AI-Predicted Community Needs" widget

**Expected Result:**
- ✅ Widget displays 12 need categories
- ✅ Each category shows confidence score (0-100%)
- ✅ Top 3 priorities highlighted
- ✅ Recommendations listed

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Screenshot: _________________
```

---

#### Test 1.3: Similar Communities

**Objective:** Find communities with similar characteristics

**Steps:**
1. Select a community
2. View detail page
3. Find "Similar Communities" widget
4. Click on a similar community link

**Expected Result:**
- ✅ Widget shows 5 similar communities
- ✅ Each shows similarity score (percentage)
- ✅ Matching features listed (population_size, ethnolinguistic_group, etc.)
- ✅ Clicking navigates to that community

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________
```

---

### Module 2: MANA AI Features

#### Test 2.1: Response Analysis

**Objective:** AI analyzes workshop responses

**Steps:**
1. Navigate to MANA → Select completed workshop
2. View workshop detail page
3. Look for "AI Analysis Summary" widget

**Expected Result:**
- ✅ Executive summary displayed (2-3 paragraphs)
- ✅ Key points extracted (bullet list)
- ✅ Sentiment indicator (positive/neutral/negative)
- ✅ Confidence score shown

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Summary Quality (1-5): ___
Accuracy (1-5): ___
```

---

#### Test 2.2: Theme Extraction

**Objective:** AI identifies common themes

**Steps:**
1. In workshop detail, find "Common Themes" section
2. Review identified themes
3. Compare with actual workshop responses

**Expected Result:**
- ✅ 3-5 themes identified
- ✅ Each theme has frequency count
- ✅ Example quotes provided
- ✅ Sub-themes listed

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Themes make sense: [  ] Yes  [  ] No
Missing important theme: _________________
```

---

#### Test 2.3: Needs Extraction

**Objective:** AI categorizes community needs from workshop

**Steps:**
1. In workshop detail, find "Identified Needs" section
2. Review needs by category
3. Check priority levels

**Expected Result:**
- ✅ Needs organized into 10 categories
- ✅ Each category shows:
  - Priority (CRITICAL/HIGH/MEDIUM/LOW)
  - Urgency score
  - Estimated beneficiaries
- ✅ Recommendations provided

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Most critical need identified: _________________
Matches actual workshop: [  ] Yes  [  ] No
```

---

#### Test 2.4: Auto-Report Generation

**Objective:** AI generates assessment report

**Steps:**
1. In workshop detail, click "Generate AI Report" button
2. Wait for generation (15-30 seconds)
3. Review generated report

**Expected Result:**
- ✅ Report includes:
  - Community overview
  - Methodology
  - Key findings
  - Priority recommendations
  - Next steps
- ✅ Report is 2-3 pages
- ✅ Professional government tone
- ✅ Culturally appropriate language

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Report quality (1-5): ___
Would use in production: [  ] Yes  [  ] No
Edits needed: _________________
```

---

#### Test 2.5: Cultural Validation

**Objective:** AI ensures cultural appropriateness

**Steps:**
1. Review generated report
2. Check for:
   - Respectful language
   - No prohibited terms (e.g., "tribal", "backward")
   - Islamic values acknowledged
   - Ethnolinguistic groups properly named

**Expected Result:**
- ✅ No culturally insensitive language
- ✅ Bangsamoro context acknowledged
- ✅ Community asset-based framing
- ✅ Cultural validation score >90%

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Issues: _________________

Cultural appropriateness (1-5): ___
```

---

### Module 3: Coordination AI Features

#### Test 3.1: Stakeholder Matching

**Objective:** AI matches stakeholders to community needs

**Steps:**
1. Navigate to Coordination → Stakeholder Matching
2. Select a community
3. Select a need category (e.g., Health)
4. View recommendations

**Expected Result:**
- ✅ Top 10 stakeholders listed
- ✅ Match scores shown (percentage)
- ✅ Matching criteria displayed
- ✅ Rationale provided for each match

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Top match makes sense: [  ] Yes  [  ] No
Match score reasonable: [  ] Yes  [  ] No
```

---

#### Test 3.2: Partnership Prediction

**Objective:** AI predicts partnership success

**Steps:**
1. Select a stakeholder and community
2. View partnership prediction
3. Review success probability and factors

**Expected Result:**
- ✅ Success probability displayed (0-100%)
- ✅ Risk factors listed
- ✅ Success factors listed
- ✅ Recommendations provided

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Prediction seems accurate: [  ] Yes  [  ] No  [  ] Uncertain
```

---

#### Test 3.3: Meeting Intelligence

**Objective:** AI summarizes meetings and extracts action items

**Steps:**
1. Navigate to Coordination → Meetings
2. Select a meeting with minutes
3. Click "Analyze Meeting" button
4. Review AI-generated summary

**Expected Result:**
- ✅ Executive summary (3-4 sentences)
- ✅ Key decisions extracted
- ✅ Action items with owners and deadlines
- ✅ Auto-create tasks button available

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Action items captured: ___/___
Ready to create tasks: [  ] Yes  [  ] No
```

---

### Module 4: Policy AI Features

#### Test 4.1: Evidence Gathering

**Objective:** AI gathers cross-module evidence

**Steps:**
1. Navigate to Policies → Create New Policy
2. Enter policy topic: "Healthcare access for coastal communities"
3. Click "Gather Evidence"
4. Review evidence dashboard

**Expected Result:**
- ✅ Evidence from 3+ modules
- ✅ Citation counts displayed
- ✅ Evidence synthesis summary
- ✅ Strength of evidence rating

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Evidence sources: MANA ___, Communities ___, Projects ___
Total citations: ___
```

---

#### Test 4.2: Auto-Policy Generation

**Objective:** AI generates policy recommendation

**Steps:**
1. After evidence gathering, click "Generate Policy Draft"
2. Wait 30-60 seconds
3. Review generated policy

**Expected Result:**
- ✅ Policy includes:
  - Title
  - Executive summary
  - Problem statement
  - Proposed solution
  - Expected impact
  - Implementation plan
  - Budget estimate
- ✅ 3-5 pages
- ✅ Professional tone
- ✅ Culturally appropriate

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Policy quality (1-5): ___
Ready for review: [  ] Yes  [  ] Needs major edits
Time saved vs manual: ____%
```

---

#### Test 4.3: Impact Simulation

**Objective:** AI simulates policy impact

**Steps:**
1. In policy detail, click "Simulate Impact"
2. Review 4 scenarios (best case, realistic, worst case, pilot)
3. Compare scenarios

**Expected Result:**
- ✅ Each scenario shows:
  - Beneficiaries reached
  - Cost per beneficiary
  - Timeline (months)
  - Success probability
  - Risk factors
  - Success factors
- ✅ Visual comparison chart

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Scenarios realistic: [  ] Yes  [  ] No
Helpful for decision-making: [  ] Yes  [  ] No
```

---

### Module 5: M&E AI Features

#### Test 5.1: Anomaly Detection

**Objective:** AI detects budget and timeline issues

**Steps:**
1. Navigate to Projects → Dashboard
2. View "Anomaly Alerts" widget
3. Review detected anomalies

**Expected Result:**
- ✅ Critical anomalies highlighted
- ✅ Each anomaly shows:
  - PPA name
  - Anomaly type (budget overrun/delay)
  - Severity level
  - Current vs expected metrics
  - Recommendations
- ✅ Click to view details

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Anomalies detected: ___
False positives: ___
Actionable: [  ] Yes  [  ] No
```

---

#### Test 5.2: Performance Forecasting

**Objective:** AI predicts project completion

**Steps:**
1. Select an ongoing project
2. View "Performance Forecast" widget
3. Review predictions

**Expected Result:**
- ✅ Predicted completion date
- ✅ Confidence level
- ✅ Delay estimate (if any)
- ✅ Factors affecting timeline
- ✅ Recommendations

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Forecast seems reasonable: [  ] Yes  [  ] No
```

---

#### Test 5.3: Automated M&E Reports

**Objective:** AI generates quarterly reports

**Steps:**
1. Navigate to Projects → Reports
2. Select "Generate Quarterly Report"
3. Choose Q3 2025
4. Review generated report

**Expected Result:**
- ✅ Report includes:
  - Executive summary
  - Statistics (totals, completion rates)
  - Budget analysis
  - Key achievements
  - Challenges
  - Recommendations
- ✅ 5-10 pages
- ✅ Charts and visualizations

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Report quality (1-5): ___
Time saved: ____%
```

---

### Module 6: Unified Search

#### Test 6.1: Natural Language Search

**Objective:** Search across all modules using natural language

**Steps:**
1. Click global search bar (top navigation)
2. Type: "coastal fishing communities in Zamboanga"
3. Press Enter
4. Review results

**Expected Result:**
- ✅ Results from multiple modules:
  - Communities
  - MANA assessments
  - Policies
  - Organizations
  - Projects
- ✅ Results ranked by relevance
- ✅ AI-generated summary at top
- ✅ Filter by module available

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Results relevant: [  ] Yes  [  ] No
Total results: ___
Most helpful module: _________________
```

---

#### Test 6.2: Search Filters

**Objective:** Refine search with filters

**Steps:**
1. From search results, apply filters:
   - Module: MANA
   - Date range: Last 6 months
2. Review filtered results

**Expected Result:**
- ✅ Results update instantly
- ✅ Only MANA results shown
- ✅ Only recent items shown
- ✅ Can clear filters

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________
```

---

### Module 7: Conversational AI Assistant

#### Test 7.1: Chat Widget

**Objective:** Natural language queries via chat

**Steps:**
1. Click chat button (bottom-right corner)
2. Chat window opens
3. Type: "How many communities are there?"
4. Send message

**Expected Result:**
- ✅ Chat widget opens smoothly
- ✅ Response within 3 seconds
- ✅ Natural language answer
- ✅ Accurate count
- ✅ Follow-up suggestions provided

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Response: _________________
Accurate: [  ] Yes  [  ] No
```

---

#### Test 7.2: Multi-Turn Conversation

**Objective:** Chat maintains context

**Steps:**
1. In chat, ask: "How many communities in Region IX?"
2. Then ask: "What about Region XII?"
3. Then ask: "Show me the coastal ones"

**Expected Result:**
- ✅ Second question understands context ("communities")
- ✅ Third question understands context ("coastal communities")
- ✅ Responses build on previous conversation
- ✅ Can reference previous queries

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Context maintained: [  ] Yes  [  ] No
```

---

#### Test 7.3: Data Queries

**Objective:** Chat executes safe database queries

**Steps:**
1. Ask: "List the top 5 communities by population"
2. Review response
3. Verify accuracy

**Expected Result:**
- ✅ Query executed successfully
- ✅ Results formatted as list
- ✅ Data is accurate
- ✅ No error messages

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Reason: _________________

Query result: _________________
```

---

#### Test 7.4: Security - Dangerous Queries

**Objective:** Chat blocks dangerous operations

**Steps:**
1. Try asking: "Delete all communities"
2. Try asking: "Update all communities to name 'test'"
3. Review responses

**Expected Result:**
- ✅ Delete request blocked
- ✅ Update request blocked
- ✅ Error message: "I can only read data, not modify it"
- ✅ Security maintained

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Security issue: _________________
```

---

## Performance Testing

### Test P.1: Response Times

**Objective:** Verify AI features are fast enough

**Steps:**
Measure response times for:
1. Needs classification
2. Search query
3. Chat response
4. Report generation

**Expected Results:**
- Needs classification: < 2s
- Search query: < 1s
- Chat response: < 3s
- Report generation: < 60s

**Actual Results:**
```
Needs classification: ___s [  ] PASS  [  ] FAIL
Search query: ___s [  ] PASS  [  ] FAIL
Chat response: ___s [  ] PASS  [  ] FAIL
Report generation: ___s [  ] PASS  [  ] FAIL
```

---

### Test P.2: Concurrent Users

**Objective:** System handles multiple users

**Steps:**
1. Have 3 team members use different AI features simultaneously
2. Monitor performance
3. Note any slowdowns

**Expected Result:**
- ✅ No significant slowdown
- ✅ All queries complete successfully
- ✅ No timeout errors

**Actual Result:**
```
[  ] PASS
[  ] FAIL - Issue: _________________
```

---

## User Experience Testing

### Test UX.1: Overall Usability

**Rate each aspect (1-5):**

| Aspect | Rating | Comments |
|--------|--------|----------|
| Ease of use | | |
| UI design | | |
| Response quality | | |
| Accuracy | | |
| Helpfulness | | |
| Speed | | |
| Reliability | | |

---

### Test UX.2: Cultural Sensitivity

**Questions:**
1. Does AI use appropriate language for Bangsamoro context?
   [ ] Always  [ ] Usually  [ ] Sometimes  [ ] Rarely

2. Are Islamic values respected?
   [ ] Yes  [ ] Mostly  [ ] No

3. Are ethnolinguistic groups properly named?
   [ ] Yes  [ ] Mostly  [ ] No

4. Any culturally insensitive content observed?
   [ ] No  [ ] Yes - Details: _________________

---

## Issue Tracking

### Critical Issues (Must Fix Before Production)
```
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________
```

### High Priority Issues
```
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________
```

### Medium Priority Issues (Nice to Have)
```
1. _________________________________________________
2. _________________________________________________
```

### Low Priority / Enhancement Requests
```
1. _________________________________________________
2. _________________________________________________
```

---

## Overall Assessment

### Summary

**Total Tests:** ___
**Passed:** ___
**Failed:** ___
**Pass Rate:** ___%

**Recommendation:**
```
[  ] APPROVE for production - All critical tests passed
[  ] APPROVE with conditions - Minor issues to address
[  ] NEEDS WORK - Significant issues found
[  ] REJECT - Major problems, not ready
```

**Conditions/Notes:**
```
_________________________________________________
_________________________________________________
_________________________________________________
```

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| MANA Coordinator | | | |
| M&E Specialist | | | |
| IT Administrator | | | |

---

## Next Steps After UAT

### If Approved:
1. [ ] Address any critical issues
2. [ ] Document workarounds for known issues
3. [ ] Schedule production deployment
4. [ ] Plan user training
5. [ ] Prepare support documentation

### If Not Approved:
1. [ ] Review and prioritize issues
2. [ ] Create fix timeline
3. [ ] Schedule re-testing
4. [ ] Communicate status to stakeholders

---

**Testing Complete:** ___/___/___
**Tested By:** _________________
**Version Tested:** 1.0
