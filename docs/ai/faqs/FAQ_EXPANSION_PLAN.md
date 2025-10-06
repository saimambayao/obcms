# OBCMS FAQ System - Expansion, Systematization & Accuracy Plan

**Version:** 2.0
**Date:** January 7, 2025
**Status:** Planning
**Location:** `docs/ai/faqs/FAQ_EXPANSION_PLAN.md`

---

## Executive Summary

### Current State
- **Total Templates:** 471 (54 geographic templates)
- **Recent Success:** Location queries working perfectly (Cotabato, Zamboanga, Bukidnon, Davao)
- **FAQ System:** `common/ai_services/chat/faq_handler.py` with priority-based matching
- **Gap:** Limited FAQ coverage for simple, common user questions

### Goals
1. **Expand FAQ coverage to 100+ questions** across 5 categories
2. **Systematize FAQ organization** with clear priority framework
3. **Ensure accuracy** through 4-level validation strategy
4. **Prioritize simple questions** for new user experience
5. **Enable monitoring** with usage analytics and feedback

### Expected Outcomes
- **80%+ match rate** for simple user questions
- **95%+ accuracy rate** based on user feedback
- **< 50ms response time** for instant FAQ answers
- **Comprehensive coverage** of system identity, geography, modules, access, and data questions
- **Maintainable system** with source tracking and regular reviews

---

## Current State Analysis

### What We Have ✅
- **Location Query Success:** "Where is Cotabato?", "Where is Zamboanga?" working perfectly
- **Priority System:** Priority 12 for location queries, higher for critical FAQs
- **Template Fallback:** 471 query templates for complex questions
- **Fast Responses:** Location FAQs respond instantly (< 15ms)

### What's Working Well ✅
- Geographic FAQ structure (FAQ → template fallback)
- Priority-based matching prevents wrong answers
- Instant responses for common location queries
- Clean integration with chat AI system

### Gaps Identified ❌
1. **System Identity Questions:** "What is OBCMS?", "What is OOBC?", "What is OBC?" - Not covered
2. **Access Questions:** "Can I use this?", "How do I log in?", "Who can access?" - Missing
3. **Module Questions:** "What is MANA?", "What is coordination?", "What are PPAs?" - Limited
4. **Help Questions:** "How do I start?", "Where is help?", "Contact support?" - Not systematized
5. **Ultra-Simple Questions:** "What is this?", "Help", "Where?" - Need special handling

---

## FAQ Category Framework

### Priority Assignment Logic

**Priority Range:** 5-20 (higher = more important, matches first)

| Priority | Category | Use Case | Examples |
|----------|----------|----------|----------|
| **18-20** | System Identity (CRITICAL) | New user's first questions | "What is OBCMS?", "What is OOBC?" |
| **15-17** | Access & Help (CRITICAL) | Getting started, permissions | "Can I use this?", "How do I log in?" |
| **12-14** | Geographic (HIGH) | Location queries | "Where is Cotabato?", "What regions?" |
| **10-12** | Modules & Features (HIGH) | Understanding capabilities | "What is MANA?", "What can I do?" |
| **8-10** | Support & Troubleshooting (MEDIUM) | User assistance | "Reset password", "Report bug" |
| **5-8** | Statistics & Advanced (LOW) | Data queries | "How many communities?", "Total programs?" |

---

## Simple Questions Focus 🎯

### Ultra-Simple Question Handling

**User Emphasis:** "Include simple questions" - Many users will ask extremely simple, short queries.

#### Single-Word & Two-Word Queries

**Challenge:** Context-free questions need helpful prompts

**Examples:**
- "Help" → "How can I help you? Try: 'What is OBCMS?', 'Where is Cotabato?', 'How do I log in?'"
- "Where?" → "Where would you like information about? Try: 'Where is [province name]?' or 'What regions are covered?'"
- "Login" → "To log in, visit [URL] with your OOBC credentials. Need help? Try: 'Forgot password' or 'Request access'"

**Strategy:**
1. Recognize context-free query
2. Provide 3-5 example questions
3. Offer most common next steps

#### Variant Management

**Challenge:** Simple questions have many informal variations

**Example - "What is OBCMS?"**
- Primary: "What is OBCMS?"
- Variants: "What's OBCMS?", "OBCMS meaning?", "Define OBCMS", "OBCMS?", "Tell me about OBCMS"

**Strategy:**
- Store primary question + list of variants
- Handle contractions ("what's", "it's", "don't")
- Accept abbreviations and acronyms
- Support informal language ("tell me", "explain")

#### Typo Tolerance

**Challenge:** Short queries prone to typos

**Common Typos:**
- "OBCSM" → OBCMS
- "OOOB" → OOBC
- "BARAM" / "BARRM" → BARMM
- "Cotabto" → Cotabato

**Strategy:**
- Fuzzy matching for short queries (edit distance ≤ 2)
- Acronym recognition (order-independent for very short strings)
- Suggest correction: "Did you mean 'OBCMS'?"

---

## Expansion Plan - 100+ FAQs

### Phase 1 | PRIORITY: CRITICAL - System Identity (20 FAQs)

**Prerequisites:** None - instant answers only
**Complexity:** Simple
**Dependencies:** Documentation review (CLAUDE.md, README.md)

#### Core Identity FAQs (Priority 20)

1. **"What is OBCMS?"**
   - Answer: "OBCMS (Office for Other Bangsamoro Communities Management System) is a comprehensive platform for managing programs, services, and data for Bangsamoro communities outside BARMM."
   - Variants: "what's obcms", "obcms meaning", "define obcms", "obcms definition"
   - Source: CLAUDE.md - Architecture Overview

2. **"What is OOBC?"**
   - Answer: "OOBC (Office for Other Bangsamoro Communities) is the government office serving Bangsamoro communities in Regions IX, X, XI, and XII outside the Bangsamoro Autonomous Region."
   - Variants: "what's oobc", "oobc meaning", "oobc full form"
   - Source: CLAUDE.md - Domain Context

3. **"What is OBC?"**
   - Answer: "OBC (Other Bangsamoro Communities) refers to Bangsamoro communities living outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM), primarily in Regions IX, X, XI, and XII."
   - Variants: "obc meaning", "obc definition", "other bangsamoro communities"
   - Source: CLAUDE.md - Geographic Scope

4. **"What is BARMM?"**
   - Answer: "BARMM (Bangsamoro Autonomous Region in Muslim Mindanao) is the autonomous region in the southern Philippines. OOBC serves Bangsamoro communities OUTSIDE BARMM."
   - Variants: "barmm meaning", "what's barmm", "bangsamoro autonomous region"
   - Source: CLAUDE.md - Domain Context

5-20. **[Additional system identity, purpose, module abbreviations, and getting started FAQs - see full plan in documentation]**

---

### Phase 2 | PRIORITY: CRITICAL - Access & Help (15 FAQs)

**Prerequisites:** Admin contact information, documentation links
**Complexity:** Simple to Moderate
**Dependencies:** Phase 1 complete

#### Key FAQs Include:
- "How do I log in?"
- "Can I use this?"
- "Forgot password"
- "Who do I contact for help?"
- "How do I report a bug?"
- "Where is the user guide?"

---

### Phase 3 | PRIORITY: HIGH - Geographic Essentials (20 FAQs)

**Prerequisites:** Database access, existing location queries
**Complexity:** Simple (instant) to Moderate (database)
**Dependencies:** Phase 1 complete

#### Includes:
- Regional coverage questions ("What regions does OOBC serve?")
- Regional definitions ("What is Region IX?", "What is SOCCSKSARGEN?")
- Province locations (expand existing Cotabato, Zamboanga, Bukidnon, Davao)
- Major city locations

---

### Phase 4 | PRIORITY: MEDIUM - Modules & Features (25 FAQs)

**Prerequisites:** Module documentation, user guides
**Complexity:** Moderate
**Dependencies:** Phase 1-2 complete

#### Covers:
- MANA module procedures
- Communities module
- Coordination module
- M&E/Projects module
- Policies module

---

### Phase 5 | PRIORITY: LOW - Statistics & Advanced (20 FAQs)

**Prerequisites:** Optimized database queries, caching
**Complexity:** Moderate to Complex
**Dependencies:** All previous phases complete

#### Includes:
- System statistics ("How many provinces?", "How many communities?")
- Advanced features
- Data quality and management
- Advanced configuration

---

## Enhanced FAQ Data Structure

### Proposed Structure
```python
{
    # Identification
    'id': 'faq_001_obcms_definition',
    'category': 'system_identity',
    'priority': 20,

    # Question Management
    'primary_question': 'What is OBCMS?',
    'variants': ['what is obcms', 'obcms meaning', 'define obcms'],

    # Answer Content
    'response': 'OBCMS is...',
    'response_type': 'instant',  # or 'database_query'

    # Accuracy & Verification
    'source': 'CLAUDE.md - Architecture Overview',
    'source_url': 'docs/CLAUDE.md#architecture-overview',
    'last_verified': '2025-01-07',

    # Analytics & Feedback
    'usage_count': 0,
    'helpful_votes': 0,
    'unhelpful_votes': 0,

    # Maintenance
    'status': 'active',
    'review_frequency': 'monthly',
    'next_review_date': '2025-02-07'
}
```

---

## Accuracy & Quality Assurance

### Level 1: Source Verification
- Every FAQ must have a verified source
- Acceptable sources: Documentation, Database schema, Official OOBC documents
- Unacceptable: Assumptions, outdated docs, unverified information

### Level 2: Regular Review Schedule
- **High-Priority (15-20):** Monthly review
- **Medium-Priority (10-14):** Quarterly review
- **Low-Priority (5-9):** Biannual review

### Level 3: Testing Strategy
- Unit tests for FAQ matching logic
- Integration tests for FAQ → Template chain
- Performance tests (< 50ms instant, < 200ms database)
- User feedback tests (95%+ helpful ratio)

### Level 4: Maintenance Procedures
- Automated alerts for outdated FAQs (> 6 months)
- Database change triggers
- Documentation update triggers
- Quarterly maintenance tasks

---

## Success Metrics & Monitoring

### Quantitative Metrics
1. **Coverage Rate:** 80% match rate target for simple questions
2. **Response Accuracy:** 95% "Yes" rate on "Was this helpful?"
3. **Response Time:** < 50ms instant, < 200ms database
4. **FAQ Usage Distribution:** Track most-used FAQs and gaps

### Qualitative Metrics
1. **User Feedback Comments:** Weekly review of negative feedback
2. **Unanswered Questions Log:** Discover FAQ gaps
3. **Staff Feedback:** Quarterly surveys

### Monitoring Dashboard (Future)
- Real-time coverage, accuracy, response time metrics
- Top questions tracking
- Alerts for low-performing FAQs
- Weekly report emails

---

## Implementation Roadmap

### Phase 1 | PRIORITY: CRITICAL - System Identity
**Tasks:**
1. Review documentation sources
2. Write 20 system identity FAQs with sources
3. Implement enhanced FAQ structure
4. Add unit tests
5. Deploy and monitor

**Success Criteria:**
- ✅ All 20 FAQs have verified sources
- ✅ Response time < 50ms
- ✅ Unit tests passing
- ✅ "What is OBCMS?" matches with priority 20

---

### Phase 2 | PRIORITY: CRITICAL - Access & Help
**Tasks:**
1. Compile admin contacts
2. Write 15 access & help FAQs
3. Add user feedback mechanism
4. Add unit tests
5. Deploy and monitor

---

### Phase 3-5 | Follow-up Phases
[Continue with Geographic, Modules, Statistics as outlined above]

---

### Phase 6 | PRIORITY: FUTURE - Continuous Improvement
**Tasks:**
- Monthly review of high-priority FAQs
- Quarterly review of all FAQs
- Weekly analysis of unanswered queries
- Create new FAQs based on gaps
- Update sources when documentation changes

---

## Summary & Next Steps

**Scope:** 100+ FAQs across 5 phases

**Key Features:**
- Simple question focus
- Enhanced FAQ structure with verification
- 4-level accuracy validation
- Comprehensive testing
- Success metrics and monitoring

**Immediate Actions:**
1. Review this plan with OOBC stakeholders
2. Assign implementation team
3. Set up monitoring
4. Begin Phase 1 (system identity FAQs)
5. Establish review schedule

---

**Document Version:** 2.0
**Last Updated:** January 7, 2025
**Next Review:** February 7, 2025
**Owner:** OBCMS Development Team
**Status:** ✅ Ready for Implementation
