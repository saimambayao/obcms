# Chat System Architecture - No AI Fallback

**Document Version:** 1.0
**Date:** 2025-10-06
**Status:** Design Specification

---

## System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Chat Input Box + Autocomplete Dropdown                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                    QUERY PROCESSING PIPELINE                    │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STAGE 1: FAQ Handler                                    │  │
│  │  • Check pre-computed answers                            │  │
│  │  • Fuzzy match against FAQ database                      │  │
│  │  • Return instant response if matched                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓ (not matched)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STAGE 2: Entity Extraction                              │  │
│  │  • Parse query for entities:                             │  │
│  │    - Locations (region, province, municipality)          │  │
│  │    - Ethnolinguistic groups                              │  │
│  │    - Livelihoods                                          │  │
│  │    - Date ranges                                          │  │
│  │    - Status values                                        │  │
│  │    - Numerical values                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STAGE 3: Clarification Detection                        │  │
│  │  • Check if query is ambiguous                           │  │
│  │  • Detect missing critical entities                      │  │
│  │  • Generate clarification questions                      │  │
│  │  • Return dialog if clarification needed                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓ (clear enough)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STAGE 4: Intent Classification                          │  │
│  │  • Classify into: data_query, analysis, help, general   │  │
│  │  • Calculate confidence score                            │  │
│  │  • Select query template category                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STAGE 5: Query Generation & Execution                  │  │
│  │  • Try all matching query templates (200+ variations)   │  │
│  │  • Substitute entities into templates                    │  │
│  │  • Validate generated query (AST, whitelist)            │  │
│  │  • Execute against database                              │  │
│  │  • Format results                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│             ┌────────────────┴────────────────┐                 │
│             ↓ (success)                       ↓ (failed)        │
│  ┌─────────────────────────┐    ┌───────────────────────────┐  │
│  │  Response Formatter     │    │  STAGE 6: Fallback        │  │
│  │  • Natural language     │    │  • Generate suggestions   │  │
│  │  • Tables/charts        │    │  • Find similar queries   │  │
│  │  • Follow-up prompts    │    │  • Show query builder     │  │
│  └─────────────────────────┘    │  • Provide help links     │  │
│                                  └───────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                      RESPONSE DELIVERY                          │
│  • HTMX-powered (no page reload)                               │
│  • Animated transitions                                         │
│  • Suggestions for next query                                   │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### **1. FAQ Handler**

**Location:** `src/common/ai_services/chat/faq_handler.py`

**Responsibilities:**
- Store pre-computed answers for common questions
- Perform fuzzy matching against FAQ database
- Return instant responses for matched queries
- Track FAQ hit rate for analytics

**Data Structure:**
```python
FAQ_RESPONSES = {
    'query_pattern': {
        'answer': str,
        'related_queries': List[str],
        'last_updated': datetime,
        'hit_count': int
    }
}
```

**Performance:**
- Response time: <10ms
- Hit rate target: 30%
- Cache: In-memory dictionary

**Cache Update Strategy:**
- Daily refresh of computed statistics
- Manual updates for static FAQs
- Automatic detection of new common queries

---

### **2. Entity Extractor**

**Location:** `src/common/ai_services/chat/entity_extractor.py`

**Responsibilities:**
- Extract structured entities from natural language
- Resolve entity ambiguities
- Normalize entity values
- Provide confidence scores

**Supported Entity Types:**

```python
ENTITY_TYPES = {
    'location': {
        'subtypes': ['region', 'province', 'municipality', 'barangay'],
        'resolver': LocationResolver,
        'normalization': True
    },
    'ethnolinguistic_group': {
        'subtypes': ['maranao', 'maguindanao', 'tausug', etc.],
        'resolver': EthnicGroupResolver,
        'normalization': True
    },
    'livelihood': {
        'subtypes': ['farming', 'fishing', 'trading', etc.],
        'resolver': LivelihoodResolver,
        'normalization': True
    },
    'date_range': {
        'subtypes': ['absolute', 'relative'],
        'resolver': DateRangeResolver,
        'normalization': True
    },
    'status': {
        'subtypes': ['ongoing', 'completed', 'draft', etc.],
        'resolver': StatusResolver,
        'normalization': True
    },
    'number': {
        'subtypes': ['cardinal', 'ordinal'],
        'resolver': NumberResolver,
        'normalization': True
    }
}
```

**Extraction Pipeline:**
```
Raw Query → Token Parsing → Pattern Matching → Normalization → Validation
```

**Example:**
```python
Input:  "maranao fishing communities zamboanga last 6 months"
Output: {
    'ethnolinguistic_group': {'value': 'Maranao', 'confidence': 0.95},
    'livelihood': {'value': 'fishing', 'confidence': 0.90},
    'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.85},
    'date_range': {'start': '2024-04-06', 'end': '2025-10-06', 'confidence': 1.0}
}
```

---

### **3. Clarification Handler**

**Location:** `src/common/ai_services/chat/clarification.py`

**Responsibilities:**
- Detect ambiguous queries
- Generate clarification questions
- Provide structured options
- Handle multi-turn clarification

**Clarification Triggers:**

```python
CLARIFICATION_RULES = {
    'missing_location': {
        'condition': 'location_required and no location_entity',
        'question': 'Which region would you like to know about?',
        'options': ['Region IX', 'Region X', 'Region XI', 'Region XII', 'All'],
        'priority': 'high'
    },
    'ambiguous_date': {
        'condition': 'date_required and no date_entity',
        'question': 'Which time period?',
        'options': ['Last 30 days', 'Last 3 months', 'This year', 'All time'],
        'priority': 'medium'
    },
    'multiple_interpretations': {
        'condition': 'intent_confidence < 0.7',
        'question': 'What did you mean?',
        'options': 'dynamic',  # Generated from possible interpretations
        'priority': 'high'
    }
}
```

**Response Format:**
```python
{
    'type': 'clarification_needed',
    'message': 'Which region would you like to know about?',
    'options': [
        {'label': 'Region IX (Zamboanga)', 'value': 'region_ix', 'icon': 'map-marker'},
        {'label': 'Region X (Northern Mindanao)', 'value': 'region_x', 'icon': 'map-marker'},
        {'label': 'All regions', 'value': 'all', 'icon': 'globe'}
    ],
    'original_query': 'show communities',
    'session_id': 'uuid'
}
```

---

### **4. Enhanced Query Templates**

**Location:** `src/common/ai_services/chat/query_templates.py`

**Architecture:**

```python
QueryTemplate = {
    'pattern': str,           # Regex pattern to match
    'query_template': str,    # Django ORM query template
    'required_entities': List[str],
    'optional_entities': List[str],
    'examples': List[str],
    'priority': int,          # Higher = try first
    'category': str
}
```

**Template Categories:**

1. **Communities (50+ templates)**
   - Count queries
   - List queries
   - Filter queries
   - Aggregate queries

2. **MANA/Workshops (40+ templates)**
   - Workshop listings
   - Participant counts
   - Assessment queries
   - Theme extraction

3. **Coordination (30+ templates)**
   - Partnership queries
   - Stakeholder listings
   - Meeting queries
   - Organization info

4. **Policies (25+ templates)**
   - Policy searches
   - Status filters
   - Sector queries

5. **Projects (25+ templates)**
   - PPA queries
   - Budget queries
   - Timeline queries

6. **Staff/Tasks (20+ templates)**
   - Task assignments
   - Workload queries
   - Calendar queries

**Total: 200+ query templates**

---

### **5. Fallback Handler**

**Location:** `src/common/ai_services/chat/fallback_handler.py`

**Responsibilities:**
- Handle failed query generation
- Provide actionable suggestions
- Find similar successful queries
- Offer query builder UI

**Fallback Strategy:**

```python
FallbackResponse = {
    'type': 'query_failed',
    'original_query': str,
    'error_analysis': {
        'likely_issue': str,  # "missing_location", "unrecognized_term", etc.
        'confidence': float
    },
    'suggestions': {
        'corrected_queries': List[str],    # Auto-corrected versions
        'similar_queries': List[str],      # Past successful queries
        'template_examples': List[str]     # Common query templates
    },
    'alternatives': [
        {
            'type': 'query_builder',
            'label': 'Build query step-by-step',
            'action': 'open_query_builder'
        },
        {
            'type': 'help',
            'label': 'Learn query syntax',
            'action': 'open_help'
        }
    ]
}
```

**Similar Query Finder Algorithm:**
```python
def find_similar_queries(failed_query: str) -> List[str]:
    # 1. Get successful queries from last 30 days
    candidates = ChatMessage.objects.filter(
        confidence__gte=0.7,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).values_list('user_message', flat=True)

    # 2. Calculate Levenshtein distance
    similarities = [
        (query, levenshtein_distance(failed_query, query))
        for query in candidates
    ]

    # 3. Return top 5 most similar
    return [q for q, d in sorted(similarities, key=lambda x: x[1])[:5]]
```

---

### **6. Query Autocomplete**

**Location:** `src/common/ai_services/chat/autocomplete.py`

**Responsibilities:**
- Provide real-time suggestions as user types
- Learn from successful queries
- Template-based completions
- Entity-aware suggestions

**Suggestion Sources:**

1. **Template-based:**
   ```python
   TEMPLATE_STARTERS = [
       "How many communities",
       "Show me workshops",
       "List partnerships",
       "What are the top needs",
       "Recent assessments"
   ]
   ```

2. **Past successful queries:**
   - User's own query history
   - Organization-wide popular queries
   - Recently successful queries

3. **Entity-aware completions:**
   ```
   User types: "communities in reg"
   Suggestions:
     - communities in Region IX
     - communities in Region X
     - communities in Region XI
   ```

**Performance:**
- Response time: <50ms
- Cache: Redis with 5-minute TTL
- Update frequency: Real-time for user history

---

### **7. Visual Query Builder**

**Location:** `src/templates/common/chat/query_builder.html`

**Architecture:**

```
Step 1: What do you want to know?
  [Count] [List] [Statistics] [Aggregate]

Step 2: About what?
  [Communities] [Workshops] [Policies] [Partnerships] [Tasks]

Step 3: Where? (if applicable)
  [All locations] [Region IX] [Region X] [Specific province ▼]

Step 4: When? (if applicable)
  [All time] [Last 30 days] [Last 3 months] [This year] [Custom ▼]

Step 5: Additional filters (optional)
  [Ethnolinguistic group ▼] [Livelihood ▼] [Status ▼]

[Preview: "There are 47 communities with fishing livelihood in Region IX"]

[Execute Query →]
```

**Technology Stack:**
- HTMX for interactivity
- Alpine.js for client-side state
- Tailwind CSS for styling
- Django backend for query generation

---

## Data Flow Examples

### Example 1: Successful FAQ Match

```
User: "How many regions does OBCMS cover?"
  ↓
FAQHandler.try_faq()
  ↓ (matched)
Return: {
  'answer': 'OBCMS covers 4 regions: Region IX, X, XI, XII',
  'confidence': 1.0,
  'source': 'faq',
  'response_time': 8ms
}
```

### Example 2: Entity Extraction + Clarification

```
User: "communities fishing"
  ↓
EntityExtractor.extract()
  ↓
{
  'livelihood': 'fishing',
  'location': None  ← Missing!
}
  ↓
ClarificationHandler.needs_clarification()
  ↓ (yes, missing location)
Return: {
  'type': 'clarification',
  'question': 'Which region?',
  'options': ['Region IX', 'Region X', 'All']
}
  ↓
User selects: "Region IX"
  ↓
QueryExecutor.execute()
  ↓
Return: "Found 23 fishing communities in Region IX"
```

### Example 3: Query Failure → Fallback

```
User: "comunitys in regon 9"  ← Typos
  ↓
EntityExtractor.extract()
  ↓
{
  'location': 'Region IX',  ← Autocorrected
  'entity_type': 'communities'  ← Fuzzy matched
}
  ↓
QueryExecutor.execute()
  ↓
[Try 50 template variations]
  ↓ (all failed)
FallbackHandler.handle_failed_query()
  ↓
Return: {
  'suggestions': [
    "How many communities in Region IX?",
    "Show me communities in Region IX",
    "List all communities in Region IX"
  ],
  'similar_queries': [
    "communities in Region IX",
    "OBC communities Region IX"
  ],
  'query_builder_available': True
}
```

---

## Performance Targets

| Stage | Target Response Time | Success Rate |
|-------|---------------------|--------------|
| FAQ Handler | <10ms | 30% match rate |
| Entity Extraction | <20ms | 95% accuracy |
| Clarification | <50ms | 100% reliability |
| Query Execution | <100ms | 95% success |
| Fallback Handler | <50ms | 100% helpful |

**Overall Target:**
- Average response time: <100ms
- Query success rate: 95%+
- User satisfaction: 80%+

---

## Security Considerations

### Query Execution Safety

**Whitelist Enforcement:**
- Only approved models accessible
- Only read operations allowed
- No dynamic code execution
- Result size limits (max 1000)

**Validation Layers:**
1. Entity validation
2. AST parsing
3. Whitelist checking
4. Query result sanitization

---

## Monitoring & Observability

### Metrics to Track

```python
CHAT_METRICS = {
    'faq_hit_rate': 'Percentage of queries matched to FAQs',
    'entity_extraction_accuracy': 'Percentage of correctly extracted entities',
    'clarification_rate': 'Percentage of queries needing clarification',
    'query_success_rate': 'Percentage of successful database queries',
    'fallback_rate': 'Percentage of queries using fallback',
    'query_builder_usage': 'Percentage using visual builder',
    'average_response_time': 'Average time to response',
    'user_retry_rate': 'Percentage of users retrying failed queries'
}
```

### Logging Strategy

```python
# Log every query with full pipeline trace
ChatQueryLog = {
    'query': str,
    'user': User,
    'session': str,
    'pipeline_trace': [
        {'stage': 'faq', 'matched': False, 'duration': 8},
        {'stage': 'entity_extraction', 'entities': {...}, 'duration': 15},
        {'stage': 'clarification', 'needed': False, 'duration': 5},
        {'stage': 'query_execution', 'success': True, 'duration': 45}
    ],
    'total_duration': 73,
    'success': True,
    'result_count': 23
}
```

---

## Scalability Considerations

**Current System:**
- Handle 100 concurrent users
- 1000 queries/hour
- <100ms response time

**Scaling Strategy:**
1. **Cache Layer:**
   - Redis for FAQ responses
   - Cache entity extraction results
   - Cache query templates

2. **Database Optimization:**
   - Indexed query patterns
   - Read replicas for queries
   - Connection pooling

3. **Horizontal Scaling:**
   - Stateless service design
   - Load balancer compatible
   - Distributed caching

---

## Conclusion

This architecture eliminates AI dependency while providing:
- ✅ **Faster responses** (<100ms vs 1-3s)
- ✅ **Better accuracy** (95% vs 60%)
- ✅ **Zero API costs**
- ✅ **Clear user guidance**
- ✅ **Production scalability**

**Next:** Review [Implementation Plan](IMPLEMENTATION_PLAN.md)
