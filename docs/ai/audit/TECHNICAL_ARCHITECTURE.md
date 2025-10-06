# OBCMS AI Technical Architecture

**Document Date:** 2025-10-06
**Source:** Code audit of Python implementation

---

## System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                            OBCMS AI INFRASTRUCTURE                          │
└────────────────────────────────────────────────────────────────────────────┘

                                    ▼

┌────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL AI SERVICES                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Google Gemini API │  │  Anthropic Claude│  │  OpenAI GPT-4        │  │
│  │  (Primary)         │  │  (MANA synthesis)│  │  (MANA synthesis)    │  │
│  │  • 2.5 Flash       │  │  • Haiku         │  │  • gpt-4o-mini       │  │
│  │  • 1.5 Pro         │  │  (configurable)  │  │  (configurable)      │  │
│  └────────────────────┘  └──────────────────┘  └──────────────────────┘  │
│                                                                              │
└────────────────────────────────────────────────────────────────────────────┘

                                    ▼

┌────────────────────────────────────────────────────────────────────────────┐
│                         AI CORE INFRASTRUCTURE                              │
│                       (src/ai_assistant/)                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  GeminiService (services/gemini_service.py)                          │  │
│  │  • API integration, retry logic, token counting, caching            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  EmbeddingService (services/embedding_service.py)                    │  │
│  │  • Sentence Transformers (all-MiniLM-L6-v2, 384-dim)                │  │
│  │  • Local execution, no API costs                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  VectorStore (services/vector_store.py)                              │  │
│  │  • FAISS (Facebook AI Similarity Search)                             │  │
│  │  • Local disk persistence, fast similarity search (<100ms)          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  SimilaritySearchService (services/similarity_search.py)             │  │
│  │  • Cross-module semantic search                                      │  │
│  │  • Threshold-based filtering, result ranking                         │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  CacheService (services/cache_service.py)                            │  │
│  │  • Redis-backed response caching                                     │  │
│  │  • TTL management (1h - 90d), cache warming, stats tracking         │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  BangsomoroCulturalContext (cultural_context.py)                     │  │
│  │  • 10 ethnolinguistic groups, Islamic principles, traditional gov   │  │
│  │  • Cultural validation, terminology guidance, stakeholder mapping   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  CostTracker (utils/cost_tracker.py)                                 │  │
│  │  • Real-time cost tracking, budget alerts, optimization suggestions │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└────────────────────────────────────────────────────────────────────────────┘

                                    ▼

┌────────────────────────────────────────────────────────────────────────────┐
│                      MODULE-SPECIFIC AI SERVICES                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────┐  ┌──────────────────┐  ┌────────────────────────┐ │
│  │  MANA             │  │  Communities     │  │  Coordination          │ │
│  │  (5 services)     │  │  (3 services)    │  │  (4 services)          │ │
│  ├───────────────────┤  ├──────────────────┤  ├────────────────────────┤ │
│  │ ResponseAnalyzer  │  │ DataValidator    │  │ StakeholderMatcher     │ │
│  │ ThemeExtractor    │  │ NeedsClassifier  │  │ PartnershipPredictor   │ │
│  │ NeedsExtractor    │  │ CommunityMatcher │  │ MeetingIntelligence    │ │
│  │ ReportGenerator   │  │                  │  │ ResourceOptimizer      │ │
│  │ CulturalValidator │  │                  │  │                        │ │
│  └───────────────────┘  └──────────────────┘  └────────────────────────┘ │
│                                                                              │
│  ┌───────────────────┐  ┌──────────────────┐  ┌────────────────────────┐ │
│  │  Project Central  │  │  Policies        │  │  Common                │ │
│  │  (4 services)     │  │  (4 services)    │  │  (5 components)        │ │
│  ├───────────────────┤  ├──────────────────┤  ├────────────────────────┤ │
│  │ AnomalyDetector   │  │ PolicyGenerator  │  │ ChatEngine             │ │
│  │ PerformanceForecst│  │ EvidenceGatherer │  │ IntentClassifier       │ │
│  │ RiskAnalyzer      │  │ ImpactSimulator  │  │ QueryExecutor          │ │
│  │ MEReportGenerator │  │ ComplianceChecker│  │ ResponseFormatter      │ │
│  └───────────────────┘  └──────────────────┘  │ ConversationManager    │ │
│                                                └────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘

                                    ▼

┌────────────────────────────────────────────────────────────────────────────┐
│                        BACKGROUND PROCESSING (CELERY)                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Daily:      • Anomaly detection (Project Central)                         │
│              • Resource utilization (Coordination)                          │
│              • Partnership alerts (Coordination)                            │
│                                                                              │
│  Weekly:     • Performance forecasting (Project Central)                   │
│              • Risk analysis (Project Central)                              │
│                                                                              │
│  Monthly:    • M&E report generation (Project Central)                     │
│                                                                              │
│  Quarterly:  • Quarterly M&E reports (Project Central)                     │
│                                                                              │
│  Nightly:    • Stakeholder matching (Coordination)                          │
│              • Policy simulations (Policies)                                │
│                                                                              │
│  On-demand:  • Workshop analysis (MANA)                                    │
│              • Report generation (MANA, Policies)                           │
│              • Evidence synthesis (Policies)                                │
│                                                                              │
└────────────────────────────────────────────────────────────────────────────┘

                                    ▼

┌────────────────────────────────────────────────────────────────────────────┐
│                             DATA LAYER                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  PostgreSQL Database                                                  │ │
│  │  • AIConversation, AIInsight, AIGeneratedDocument                    │ │
│  │  • AIUsageMetrics, AIOperation (cost tracking)                       │ │
│  │  • DocumentEmbedding (metadata only)                                 │ │
│  │  • ChatMessage, WorkshopSynthesis                                    │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  Redis Cache                                                          │ │
│  │  • AI responses (1h - 90d TTL)                                       │ │
│  │  • Conversation context (30 min)                                     │ │
│  │  • Analysis results (24h - 30d)                                      │ │
│  │  • Embedding model singleton                                         │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │  FAISS Vector Indices (Disk)                                         │ │
│  │  • communities.index, communities.metadata                           │ │
│  │  • policies.index, policies.metadata                                 │ │
│  │  • assessments.index, assessments.metadata (planned)                 │ │
│  │  • organizations.index, projects.index                               │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└────────────────────────────────────────────────────────────────────────────┘

                                    ▼

┌────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  • Django Admin (full access to AI models)                                 │
│  • REST APIs (ai_assistant, MANA, Common)                                  │
│  • Web Views (HTMX-powered for MANA, Common chat)                          │
│  • Management Commands (indexing, health checks)                            │
│                                                                              │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Examples

### Example 1: Conversational Chat Query

```
User: "How many communities are in Region IX?"
   ↓
POST /chat/message/
   ↓
ConversationalAssistant.chat()
   ├─ ConversationManager.get_context() → Last 5 turns from Redis
   ├─ IntentClassifier.classify() → "data_query" (confidence: 0.85)
   ├─ QueryExecutor.generate_and_execute()
   │  ├─ Generate: OBCCommunity.objects.filter(...).count()
   │  ├─ Validate: AST parsing, whitelist check
   │  └─ Execute: result = 47
   ├─ ResponseFormatter.format_query_result()
   │  └─ "There are 47 communities in Region IX."
   └─ ConversationManager.add_exchange()
      ├─ Save to ChatMessage model
      └─ Update Redis cache
   ↓
Render: common/chat/message_pair.html (HTMX)
```

### Example 2: MANA Workshop Analysis

```
Facilitator: Click "Analyze Workshop" button
   ↓
POST /workshop/<id>/analyze/
   ↓
Trigger: analyze_workshop_responses.delay(workshop_id) [Celery]
   ↓
Background Task:
   ├─ ResponseAnalyzer.analyze_question_responses()
   │  └─ Gemini analyzes each question's responses
   │     → Summary, key points, sentiment, action items
   ├─ ThemeExtractor.extract_themes()
   │  └─ Gemini extracts top 8 themes with examples
   ├─ NeedsExtractor.extract_needs()
   │  └─ Gemini categorizes into 10 need categories
   └─ Cache results (30 days)
   ↓
Frontend: HTMX polling every 2s
   ↓
GET /workshop/<id>/analysis/status/
   ↓
Return cached results when ready
   ↓
Render: AI insights dashboard (no page reload)
```

### Example 3: Project Central Anomaly Detection

```
Celery Beat Scheduler: Daily 6:00 AM
   ↓
detect_daily_anomalies_task()
   ↓
For each active PPA:
   ├─ Calculate timeline progress (elapsed / total days)
   ├─ Calculate budget utilization (disbursed / allocated)
   ├─ Compute deviation (utilization - progress)
   ├─ If deviation ≥ 15%:
   │  ├─ Classify severity (MEDIUM/HIGH/CRITICAL)
   │  ├─ GeminiService.generate_text()
   │  │  └─ Generate 3-5 specific recommendations
   │  └─ Create Alert object (if HIGH/CRITICAL)
   └─ Cache anomaly data (24h)
   ↓
Dashboard: Instant display (pre-computed, cached)
```

### Example 4: Policy Generation with Evidence

```
Staff: Request policy on "Education for Maranao communities"
   ↓
POST /api/policies/generate/
   ↓
EvidenceGatherer.gather_evidence()
   ├─ Query vector: EmbeddingService.generate_embedding(query)
   ├─ Search communities index → 8 relevant communities
   ├─ Search MANA assessments → 5 relevant assessments
   ├─ Search existing policies → 2 similar policies
   └─ GeminiService.synthesize_evidence()
      → Evidence narrative with citations
   ↓
PolicyGenerator.generate_policy_recommendation()
   ├─ Input: Evidence + BangsomoroCulturalContext
   ├─ GeminiService.generate_text() [temperature: 0.6]
   └─ Output: 11-section policy document
      • Title, Executive Summary, Problem Statement
      • Rationale, Proposed Solution, Objectives
      • Expected Outcomes, Implementation Strategy
      • Budget Implications, Success Metrics, Citations
   ↓
ImpactSimulator.simulate_impact()
   ├─ Best case scenario (100% funding, 120% efficiency)
   ├─ Realistic scenario (85% funding, 100% efficiency)
   ├─ Worst case scenario (60% funding, 75% efficiency)
   └─ Pilot program scenario (30% funding, 110% efficiency)
   ↓
ComplianceChecker.check_compliance()
   ├─ Check against 8 laws (R.A. 11054, etc.)
   ├─ GeminiService.generate_text() [temperature: 0.2]
   └─ Output: Compliance score, risk level, recommendations
   ↓
Save: PolicyRecommendation model + cache (7d)
```

---

## Security Architecture

### Query Execution Whitelist

```python
# Only these models are accessible via AI chat
ALLOWED_MODELS = {
    'OBCCommunity',
    'Municipality',
    'Province',
    'Region',
    'Barangay',
    'Assessment',
    'PolicyRecommendation',
    'Organization',
    'Partnership',
    'WorkItem',
    'Event'
}

# Only read operations allowed
ALLOWED_OPERATIONS = {
    'filter', 'exclude', 'get', 'count',
    'aggregate', 'annotate', 'values',
    'order_by', 'distinct'
}

# Blocked operations
BLOCKED_OPERATIONS = {
    'create', 'update', 'delete', 'save',
    'bulk_create', 'bulk_update', '__import__',
    'exec', 'eval', 'compile'
}
```

### AST Validation

```python
def validate_query_code(code: str) -> bool:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        # Block function calls (except whitelisted)
        if isinstance(node, ast.Call):
            if not is_allowed_operation(node):
                raise SecurityError("Disallowed operation")
        # Block attribute access (except whitelisted)
        if isinstance(node, ast.Attribute):
            if node.attr in BLOCKED_OPERATIONS:
                raise SecurityError("Blocked operation")
    return True
```

---

## Cost Optimization Strategies

### 1. Local Embeddings (Sentence Transformers)
- **Before:** OpenAI embeddings → $0.0001 per 1K tokens
- **After:** Local Sentence Transformers → $0
- **Savings:** 100% on embedding costs

### 2. FAISS Local Storage
- **Before:** Pinecone cloud → $70/month
- **After:** FAISS local → $0
- **Savings:** $70/month

### 3. Redis Response Caching
- **Target:** 80% cache hit rate
- **Effect:** 80% reduction in duplicate API calls
- **Savings:** ~$120/month at moderate usage

### 4. Background Pre-computation
- **Effect:** Instant dashboard access (no API call on page load)
- **Example:** Stakeholder matches pre-computed nightly
- **Savings:** ~200 API calls/day = $15/month

### Total Cost Optimization: ~$200/month saved

---

## Performance Characteristics

| Operation | Response Time | Caching | Cost |
|-----------|---------------|---------|------|
| **Chat query (cached)** | <50ms | 1h | $0 |
| **Chat query (uncached)** | 1-2s | - | $0.002 |
| **Vector similarity search** | <100ms | N/A | $0 |
| **Workshop analysis** | 30-60s | 30d | $0.15 |
| **Policy generation** | 45-90s | 7d | $0.25 |
| **M&E report generation** | 20-40s | 30d | $0.08 |
| **Anomaly detection (1 PPA)** | 2-3s | 24h | $0.01 |

---

## Monitoring & Observability

### Cost Tracking
```python
AIOperation.objects.filter(
    created_at__date=today
).aggregate(
    total_cost=Sum('cost'),
    total_tokens=Sum('tokens_used'),
    avg_response_time=Avg('response_time')
)
```

### Health Monitoring
```bash
python manage.py ai_health_check --verbose

✓ Google API Key configured
✓ Gemini Service operational
✓ Redis cache operational
✓ Cultural Context loaded
✓ Cost Tracking functional
```

### Usage Analytics
```python
AIUsageMetrics.objects.filter(
    date__gte=start_date
).aggregate(
    total_conversations=Sum('conversations_started'),
    total_messages=Sum('messages_sent'),
    total_insights=Sum('insights_generated'),
    total_documents=Sum('documents_created')
)
```

---

## Scalability Considerations

### Current Limits
- **FAISS Index:** Handles 100K+ vectors efficiently
- **Redis Cache:** 4GB memory → ~40K cached responses
- **Celery Workers:** 4 workers → ~100 concurrent tasks
- **Database:** PostgreSQL → millions of records

### Scaling Strategy
1. **Horizontal Scaling:**
   - Add more Celery workers
   - Redis cluster for cache
   - Read replicas for database

2. **Vertical Scaling:**
   - Larger FAISS indices (millions of vectors)
   - More Redis memory (64GB+)
   - Faster CPUs for embeddings

3. **Optimization:**
   - Increase cache TTLs
   - Batch API calls
   - Use Gemini Flash for simple queries

---

## Future Architecture Enhancements

### Phase 1: Multi-LLM Support
```
GeminiService → Abstract AIService
   ├─ GeminiProvider
   ├─ ClaudeProvider
   └─ GPTProvider
```

### Phase 2: Advanced Analytics
- Real-time trend detection
- Predictive alerts
- Proactive recommendations

### Phase 3: Collaboration Features
- AI-powered stakeholder recommendations
- Automated partnership formation
- Intelligent task assignment

---

## Conclusion

OBCMS AI architecture is:
- ✅ **Modular:** Clear separation of concerns
- ✅ **Scalable:** Handles growth via caching + background tasks
- ✅ **Cost-Effective:** Local embeddings + FAISS = minimal API costs
- ✅ **Secure:** Whitelist-based, read-only, validated
- ✅ **Observable:** Comprehensive monitoring and cost tracking
- ✅ **Culturally Aware:** Bangsamoro context in every response

**The architecture is production-ready and designed for long-term sustainability.**

---

**Document Version:** 1.0
**Date:** 2025-10-06
**Author:** AI Infrastructure Audit Team
