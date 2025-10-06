# AI Chat Query Patterns - Developer Reference

**Quick reference for working query patterns and implementation details**

---

## Overview

The OBCMS AI Chat Assistant uses a hybrid approach:
1. **Rule-based pattern matching** for fast, predictable responses
2. **Gemini AI fallback** for complex or unmatched queries
3. **Intent classification** to route queries appropriately

---

## Working Query Patterns

### Pattern 1: Geographic Location Queries

**Pattern:** `[ACTION] [ENTITY] in [LOCATION]`

**Intent:** `data_query`

**Examples:**
```
✅ "Tell me about OBC communities in Davao City"
✅ "How many communities are in Region IX?"
✅ "Show me assessments in Zamboanga del Sur"
✅ "List communities in Northern Mindanao"
```

**Implementation:**
```python
# Intent Classification
- Detects "data_query" intent (keywords: "tell", "how many", "show", "list")
- Extracts entities: ["communities", "regions"]

# Query Generation (Rule-based)
def _extract_location_from_message(message_lower):
    # Pattern matching for "in [Location]", "at [Location]"
    # Falls back to known location list
    return location  # e.g., "Davao City"

# Query Construction
query = f"OBCCommunity.objects.filter(
    Q(barangay__municipality__name__icontains='{location}') |
    Q(barangay__municipality__province__name__icontains='{location}')
)"

# Fallback if Query Fails
- Gemini conversational AI with OBCMS context
- Provides helpful guidance and navigation tips
```

**Detected Entities:**
- `communities`: barangay, community, communities, obc
- `regions`: region, province, municipality, area, city, davao, zamboanga, cotabato

**Location Extraction:**
- Regex patterns: `r"in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"`
- Known locations: zamboanga, davao, cotabato, bukidnon, lanao, etc.

---

### Pattern 2: Count Queries

**Pattern:** `How many [ENTITY] (in [LOCATION])?`

**Intent:** `data_query`

**Examples:**
```
✅ "How many communities are there?"
✅ "Count workshops in the system"
✅ "Total number of policy recommendations"
✅ "How many projects do we have?"
```

**Implementation:**
```python
# Intent Classification
- Keywords: "how many", "count", "total", "number of"
- Action: "aggregate"

# Query Generation
if "communities" in entities:
    if location:
        query = f"OBCCommunity.objects.filter(...).count()"
    else:
        query = "OBCCommunity.objects.all().count()"
elif "workshops" in entities:
    query = "Assessment.objects.all().count()"
# etc.

# Response Formatting
- Format count with commas: "42" → "There are 42 communities..."
- Suggest follow-ups: "Show me the list", "Break down by region"
```

**Entity Mapping:**
- `communities` → `OBCCommunity.objects`
- `workshops` → `Assessment.objects`
- `policies` → `PolicyRecommendation.objects`
- `projects` → `WorkItem.objects` (or PPA)
- `organizations` → `Organization.objects`

---

### Pattern 3: Status Filter Queries

**Pattern:** `Show [STATUS] [ENTITY]`

**Intent:** `data_query`

**Examples:**
```
✅ "Show me approved policy recommendations"
✅ "List active projects"
✅ "Find completed workshops"
```

**Implementation:**
```python
# Intent Classification
- Keywords: "show", "list", "find", "display"
- Entities: Extract status and entity

# Query Generation
# Note: Currently falls back to Gemini due to status field mapping complexity
query = f"{Entity}.objects.filter(status='{status}')"

# Gemini Fallback (Current Behavior)
- Provides contextual response about where to find this data
- Suggests using module filters
```

**Status Keywords:**
- approved, active, completed
- pending, draft, in-progress
- planned, ongoing

---

### Pattern 4: List All Queries

**Pattern:** `List all [ENTITY]`

**Intent:** `data_query`

**Examples:**
```
✅ "List all coordination activities"
✅ "Show me all organizations"
✅ "Display all regions"
```

**Implementation:**
```python
# Intent Classification
- Keywords: "list all", "show all", "display"
- Action: "read"

# Query Generation
if "list" in message_lower or "show" in message_lower:
    query = f"{Entity}.objects.all()"

# Response Formatting
- Shows first 5 results
- Indicates total count
- Provides "Show more" suggestion
```

---

### Pattern 5: Help Queries

**Pattern:** `What can you help (me) with?`

**Intent:** `help`

**Examples:**
```
✅ "What can you help me with?"
✅ "What data do you have?"
✅ "How do I use this?"
✅ "Show me example queries"
```

**Implementation:**
```python
# Intent Classification
- Keywords: "help", "what can", "how do i", "how to"
- Confidence boost for "help" keyword

# Response
- Template-based (fast, no AI needed)
- Shows structured help guide
- Includes example queries by category
- Provides quick action suggestions
```

**Response Template:**
```markdown
**OBCMS AI Assistant - Quick Help**

**📊 Data Queries**
- 'How many communities are in Region IX?'
- 'Show me MANA assessments in Zamboanga'
...

**🧭 Navigation**
- 'Take me to the dashboard'
...

**💡 Tips:**
- Use natural language - just ask!
...
```

---

### Pattern 6: Conversational Queries

**Pattern:** Greetings, thanks, casual chat

**Intent:** `general`

**Examples:**
```
✅ "Hello"
✅ "Good morning"
✅ "Thank you"
✅ "Thanks for your help"
```

**Implementation:**
```python
# Intent Classification
- Keywords: "hi", "hello", "hey", "thanks", "thank you"
- Pattern: r"^(hi|hello|hey)"

# Response Routing
if "hi" or "hello" in message:
    return format_greeting()
elif "thanks" or "thank you" in message:
    return format_thanks()

# Response
- Template-based (instant)
- Includes helpful suggestions
- Encourages user to ask questions
```

---

## Intent Classification Details

### Intent Types

```python
INTENT_TYPES = {
    "data_query": "Request for data from system",
    "analysis": "Request for insights/trends",
    "navigation": "Request to navigate pages",
    "help": "Request for assistance",
    "general": "Conversational/greeting"
}
```

### Confidence Scoring

**Formula:**
```
score = keyword_matches * 0.3 +
        pattern_matches * 0.5 +
        entity_matches * 0.2
max_score = 1.0
```

**Example:**
```python
# Query: "How many communities are in Region IX?"

keyword_matches = 2  # "how many", "communities"
pattern_matches = 1  # matches r"how many .+ (are|in|have)"
entity_matches = 2   # "communities", "regions"

score = 2*0.3 + 1*0.5 + 2*0.2 = 1.5
final_score = min(1.5, 1.0) = 1.0  # Perfect confidence!
```

---

## Query Executor Security

### Allowed Models (Read-Only)

```python
ALLOWED_MODELS = {
    "OBCCommunity": "communities.models.OBCCommunity",
    "Municipality": "common.models.Municipality",
    "Province": "common.models.Province",
    "Region": "common.models.Region",
    "Barangay": "common.models.Barangay",
    "Assessment": "mana.models.Assessment",
    "PolicyRecommendation": "recommendations.policy_tracking.models.PolicyRecommendation",
    "Organization": "coordination.models.Organization",
    "Partnership": "coordination.models.Partnership",
    "WorkItem": "common.work_item_model.WorkItem",
    "Event": "common.models.Event",
}
```

### Allowed Methods

```python
ALLOWED_METHODS = {
    # Read operations only
    "filter", "exclude", "get", "first", "last",
    "exists", "count", "aggregate", "annotate",
    "values", "values_list", "order_by", "distinct",
    "select_related", "prefetch_related", "all", "none"
}
```

### Dangerous Keywords (Blocked)

```python
DANGEROUS_KEYWORDS = {
    "delete", "update", "create", "save",
    "bulk_create", "bulk_update", "raw", "execute",
    "cursor", "eval", "exec", "compile",
    "__import__", "open", "file", "input",
    "system", "popen", "subprocess"
}
```

### Validation Process

```python
def _validate_query(query_string):
    # 1. String-based keyword detection
    if any(keyword in query_string.lower() for keyword in DANGEROUS_KEYWORDS):
        return {"is_safe": False, "reason": "Dangerous keyword"}

    # 2. AST parsing
    tree = ast.parse(query_string, mode="eval")
    validate_ast(tree)  # Checks for assignments, imports, unauthorized calls

    # 3. Model validation
    if not any(model in query_string for model in ALLOWED_MODELS):
        return {"is_safe": False, "reason": "No recognized model"}

    return {"is_safe": True}
```

---

## Gemini Fallback Mechanism

### When Fallback Activates

```python
# Scenario 1: Query generation fails
if not query_string:
    if self.has_gemini:
        return self._fallback_to_gemini(message, context)
    else:
        return format_error("Could not understand query")

# Scenario 2: Query execution fails
if not exec_result["success"]:
    if self.has_gemini:
        return self._fallback_to_gemini(message, context)
    else:
        return format_error(exec_result["error"])
```

### Fallback Prompt Template

```python
def _build_conversational_prompt(message, context):
    return f"""You are the OBCMS AI Assistant helping users with the
Office for Other Bangsamoro Communities system.

User Question: "{message}"

Context: OBCMS manages data about Bangsamoro communities outside BARMM, including:
- Community profiles (demographics, needs, services)
- MANA assessments (Mapping and Needs Assessment)
- Coordination activities (partnerships, workshops)
- Policy recommendations
- Project management

Please provide a helpful, conversational response to the user's question.
If you don't have specific data, guide them on what they can ask or where
they can find the information in the system.

Keep your response concise (2-3 sentences) and friendly.

Response:"""
```

### Fallback Response Format

```python
{
    "response": "Natural language response from Gemini",
    "data": {},  # Empty - no structured data
    "suggestions": [
        "Tell me more",
        "What else can you help with?",
        "Show me some data"
    ],
    "visualization": None
}
```

---

## Response Formatting

### Format by Result Type

```python
def format_query_result(result, result_type, question, entities):
    if isinstance(result, int):
        return format_count(result, question, entities)
    elif isinstance(result, dict):
        return format_aggregate(result, question, entities)
    elif isinstance(result, list):
        return format_list(result, question, entities)
    else:
        return format_generic(result, question)
```

### Count Response

```python
# Input: result = 42
# Output:
{
    "response": "There are 42 communities matching your query.",
    "data": {"count": 42, "entity": "communities"},
    "suggestions": [
        "Show me the list of communities",
        "Break down by region",
        "Compare with other areas"
    ],
    "visualization": "bar_chart"  # count > 10
}
```

### List Response

```python
# Input: result = [{"id": 1, "name": "..."}, ...]
# Output:
{
    "response": "Found 42 communities. Here are the first 5:\n\n1. ...\n2. ...",
    "data": {
        "items": [...],  # All items
        "count": 42,
        "preview_count": 5
    },
    "suggestions": [
        "Show me more details",
        "Filter these communities",
        "Analyze these results"
    ],
    "visualization": "table"
}
```

---

## Performance Optimization

### Response Time Breakdown

```
Total Response Time (7-8 seconds for Gemini fallback)
├─ Intent Classification: 5-10ms
├─ Query Generation (Gemini): 3-5 seconds
│   └─ API call to Gemini
├─ Query Execution: 50-200ms (if succeeds)
└─ Fallback to Gemini: 2-4 seconds (if query fails)
    └─ Second API call to Gemini
```

### Optimization Opportunities

#### 1. Query Result Caching

```python
# Cache common queries
cache_key = f"chat_query:{hashlib.md5(message.encode()).hexdigest()}"
cached_result = cache.get(cache_key)

if cached_result:
    return cached_result

# Execute query...

cache.set(cache_key, result, timeout=300)  # 5 minutes
```

#### 2. Skip Query Generation for Known Patterns

```python
# Direct to fallback for vague queries
if message_lower in ["tell me everything", "show me data", "what do you have"]:
    return self._fallback_to_gemini(message, context)
```

#### 3. Parallel Processing (Future)

```python
# Generate query and prepare fallback simultaneously
with ThreadPoolExecutor() as executor:
    query_future = executor.submit(generate_query, message)
    # Start query generation

    query_string = query_future.result(timeout=2)

    if not query_string:
        # Fallback already prepared
        return fallback_response
```

---

## Testing Patterns

### Unit Test Template

```python
def test_geographic_query():
    assistant = get_conversational_assistant()

    result = assistant.chat(
        user_id=1,
        message="Tell me about OBC communities in Davao City"
    )

    assert result['intent'] == 'data_query'
    assert result['confidence'] > 0.5
    assert 'Davao' in result['response']
    assert result['suggestions']
    assert result['response'] is not None
```

### Integration Test Template

```python
@pytest.mark.integration
def test_end_to_end_query():
    # Test full flow: intent → query → execute → format
    assistant = get_conversational_assistant()

    queries = [
        "How many communities are in Region IX?",
        "Tell me about OBC communities in Davao City",
        "What can you help me with?"
    ]

    for query in queries:
        result = assistant.chat(user_id=1, message=query)

        # Should not error
        assert 'error' not in result.get('response', '').lower()

        # Should have suggestions
        assert len(result.get('suggestions', [])) > 0

        # Should complete quickly (with Gemini: <10s)
        # Measured in test execution
```

---

## Common Issues & Solutions

### Issue 1: "Could not understand" Errors

**Symptoms:**
- Query returns error message
- No fallback triggered

**Cause:**
- Gemini not configured
- API quota exceeded

**Solution:**
```python
# Ensure Gemini fallback is implemented
if not self.has_gemini:
    logger.warning("Gemini not available - responses will be limited")

# Check API quota
if gemini_error == "quota exceeded":
    # Show helpful message
    return format_error(
        "AI assistant is temporarily busy. Please try again in a moment."
    )
```

---

### Issue 2: Slow Response Times

**Symptoms:**
- Responses take > 10 seconds
- Multiple API calls

**Cause:**
- Two sequential Gemini calls (query gen + fallback)

**Solution:**
```python
# Option 1: Direct to fallback for known-fail patterns
if is_vague_query(message):
    return self._fallback_to_gemini(message, context)

# Option 2: Cache query generation results
if message in common_queries:
    query_string = query_cache[message]
```

---

### Issue 3: Model Import Warnings

**Symptoms:**
```
WARNING Could not import mana.models.Workshop
WARNING Could not import common.models.Task
```

**Cause:**
- Incorrect model paths in `ALLOWED_MODELS`

**Solution:**
```python
# Update query_executor.py ALLOWED_MODELS
ALLOWED_MODELS = {
    "Assessment": "mana.models.Assessment",  # NOT Workshop
    "WorkItem": "common.work_item_model.WorkItem",  # NOT Task
    # etc.
}
```

---

## Code Locations

**Main Implementation:**
- `/src/common/ai_services/chat/chat_engine.py` - Main orchestrator
- `/src/common/ai_services/chat/intent_classifier.py` - Intent detection
- `/src/common/ai_services/chat/query_executor.py` - Safe query execution
- `/src/common/ai_services/chat/response_formatter.py` - Response formatting
- `/src/common/ai_services/chat/conversation_manager.py` - Context management

**Tests:**
- `/src/test_ai_chat_quick.py` - Quick 5-query test
- `/src/test_ai_chat_queries.py` - Comprehensive 25+ query test

**Documentation:**
- `/docs/testing/AI_CHAT_QUERY_TEST_RESULTS.md` - Test results
- `/docs/USER_GUIDE_AI_CHAT.md` - User guide
- `/docs/development/AI_CHAT_QUERY_PATTERNS.md` - This file

---

## Quick Reference: Adding New Query Patterns

### Step 1: Add Keywords to Intent Classifier

```python
# intent_classifier.py
DATA_ENTITIES = {
    "new_entity": ["keyword1", "keyword2", "keyword3"],
}
```

### Step 2: Add Model to Query Executor

```python
# query_executor.py
ALLOWED_MODELS = {
    "NewModel": "app.models.NewModel",
}
```

### Step 3: Add Rule-based Pattern

```python
# chat_engine.py - _generate_query_rule_based()
if "new_entity" in entities:
    if location:
        return f"NewModel.objects.filter(location__icontains='{location}')"
    else:
        return "NewModel.objects.all()"
```

### Step 4: Test

```python
# test_ai_chat_quick.py
result = assistant.chat(user_id=1, message="How many new_entities are there?")
assert result['intent'] == 'data_query'
assert result['response'] is not None
```

---

**For more information, see:**
- [AI Chat Implementation Guide](/docs/improvements/CONVERSATIONAL_AI_IMPLEMENTATION.md)
- [AI Chat Test Results](/docs/testing/AI_CHAT_QUERY_TEST_RESULTS.md)
- [User Guide](/docs/USER_GUIDE_AI_CHAT.md)
