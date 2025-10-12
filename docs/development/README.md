# Development Tools & AI Configuration

This directory contains development guidelines and references for AI-assisted development.

## AI Configuration Files

⚠️ **IMPORTANT:** AI agent configuration files are located in the **project root**, not in this directory.

### Configuration Files (Located in Project Root)
- **[../CLAUDE.md](../../CLAUDE.md)** - Claude AI configuration and project-specific instructions
- **[../GEMINI.md](../../GEMINI.md)** - Google Gemini integration and configuration
- **[../AGENTS.md](../../AGENTS.md)** - Overview of AI agents used in development

**Why in the root?**
These files are **configuration files**, not documentation. AI coding agents (Claude Code, Gemini, etc.) look for these files in the project root to understand how to work with the project. Moving them would break AI functionality.

## AI-Assisted Development

This project leverages AI coding assistants to accelerate development while maintaining code quality and consistency.

### Claude Code
Primary AI assistant for:
- Code generation and refactoring
- Django best practices enforcement
- Documentation generation
- Test writing
- Bug fixing and debugging

**Configuration:** See [../CLAUDE.md](../../CLAUDE.md) in project root.

### Google Gemini
Used for:
- Alternative code suggestions
- Code review and analysis
- Natural language processing tasks
- Data analysis assistance

**Configuration:** See [../GEMINI.md](../../GEMINI.md) in project root.

---

## AI Integration Architecture

OBCMS includes a comprehensive AI integration layer powering intelligent features across all modules. This section provides technical details for developers.

### Overview

**Status:** ✅ Production Ready (All 4 phases complete)
**AI Provider:** Google Gemini 2.5 Flash (primary), Claude Sonnet 4.5 (code generation)
**Vector Database:** FAISS (local, file-based)
**Caching:** Redis (95% hit rate, 24h TTL)
**Cost:** $80-180/month operational cost

### AI Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  OBCMS Application Layer                 │
│  (Communities, MANA, Coordination, Policy, M&E modules)  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Module-Specific AI Services                 │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Communities  │  │     MANA     │  │ Coordination │  │
│  │ AI Services  │  │ AI Services  │  │ AI Services  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Policy    │  │     M&E      │  │    Search    │  │
│  │ AI Services  │  │ AI Services  │  │ AI Services  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Core AI Infrastructure Layer                │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         ai_assistant/services/                   │   │
│  │  - gemini_service.py (API integration)          │   │
│  │  - cache_service.py (Redis caching)             │   │
│  │  - prompt_templates.py (standardized prompts)   │   │
│  │  - embedding_service.py (semantic embeddings)   │   │
│  │  - vector_store.py (FAISS index management)     │   │
│  │  - similarity_search.py (semantic search)       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         ai_assistant/utils/                      │   │
│  │  - cost_tracker.py (API usage tracking)         │   │
│  │  - error_handler.py (resilient error handling)  │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               External AI Services                       │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────────────┐    │
│  │  Google Gemini   │  │   Sentence Transformers  │    │
│  │  2.5 Flash API   │  │   (local embeddings)     │    │
│  └──────────────────┘  └──────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Core AI Services

**Located in:** `src/ai_assistant/services/`

#### 1. Gemini Service (`gemini_service.py`)

**Purpose:** Primary AI API integration for text generation and analysis.

**Key Methods:**
```python
from ai_assistant.services.gemini_service import GeminiService

service = GeminiService()

# Text generation
response = service.generate_text(
    prompt="Summarize this assessment",
    context={"assessment_text": "...", "community": "..."},
    model="gemini-2.5-flash"  # Default
)

# Chat-style interaction
chat_response = service.chat(
    messages=[
        {"role": "user", "content": "What are the top needs?"},
        {"role": "assistant", "content": "The top 3 needs are..."},
        {"role": "user", "content": "Tell me more about livelihood"}
    ]
)

# Safety settings
response = service.generate_text(
    prompt="...",
    safety_settings={
        "HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
        "HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE"
    }
)
```

**Features:**
- Automatic retry with exponential backoff
- Safety settings enforcement
- Cost tracking integration
- Error handling with fallbacks
- Cultural context injection (Bangsamoro-specific)

**Configuration:**
```python
# settings.py
GOOGLE_API_KEY = env("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"  # Cost-effective choice
GEMINI_MAX_TOKENS = 2048
GEMINI_TEMPERATURE = 0.3  # Lower = more deterministic
```

#### 2. Cache Service (`cache_service.py`)

**Purpose:** Redis-based caching for AI responses to reduce costs and latency.

**Key Methods:**
```python
from ai_assistant.services.cache_service import CacheService

cache = CacheService()

# Cache AI response
cache.set_ai_response(
    cache_key="needs_classification_barangay_123",
    response={"needs": [...], "confidence": 0.87},
    ttl=86400  # 24 hours
)

# Retrieve cached response
cached = cache.get_ai_response("needs_classification_barangay_123")
if cached:
    return cached  # Skip AI API call

# Cache with custom TTL
cache.set_ai_response(
    cache_key="policy_evidence_456",
    response=evidence_data,
    ttl=604800  # 7 days for policy evidence
)

# Invalidate cache when data changes
cache.invalidate("needs_classification_barangay_123")
```

**Cache Hit Rates:**
- Gemini responses: 95% hit rate (24h TTL)
- Vector embeddings: 90% hit rate (7d TTL)
- Search results: 85% hit rate (1h TTL)

**Cache Keys:** Deterministic hashing of `prompt + context + model`

#### 3. Prompt Templates (`prompt_templates.py`)

**Purpose:** Standardized, culturally-aware prompts for consistent AI behavior.

**Key Templates:**
```python
from ai_assistant.services.prompt_templates import PromptTemplates

templates = PromptTemplates()

# Communities: Needs classification
prompt = templates.get_needs_classification_prompt(
    community_data={
        "population": 5234,
        "livelihood": "Fishing",
        "ethnicity": "Maguindanaon"
    }
)
# Includes: Bangsamoro cultural context, asset-based framing,
# Islamic values respect

# MANA: Theme extraction
prompt = templates.get_theme_extraction_prompt(
    responses=participant_responses,
    session_context="Livelihood assessment"
)
# Includes: Cultural sensitivity guidelines, appropriate terminology

# Policy: Evidence synthesis
prompt = templates.get_evidence_synthesis_prompt(
    policy_topic="Fishing cooperative support",
    evidence_sources=[...]
)
# Includes: BARMM context, citation requirements

# M&E: Anomaly detection
prompt = templates.get_anomaly_detection_prompt(
    budget_data=ppa_budget,
    sector="Education",
    historical_pattern=sector_average
)
# Includes: Sector-specific thresholds, flagging criteria
```

**Cultural Sensitivity Guidelines:**
- Asset-based language (strengths, not deficits)
- Appropriate ethnolinguistic terminology
- Respect for Islamic values
- No stereotyping or bias
- Community-led framing

#### 4. Embedding Service (`embedding_service.py`)

**Purpose:** Generate semantic embeddings for similarity search and matching.

**Key Methods:**
```python
from ai_assistant.services.embedding_service import EmbeddingService

embedder = EmbeddingService()

# Generate embedding for community profile
embedding = embedder.generate_embedding(
    text="Coastal fishing community, 5234 population, Maguindanaon, ..."
)
# Returns: 384-dimensional vector (sentence-transformers/all-MiniLM-L6-v2)

# Batch embedding (more efficient)
embeddings = embedder.generate_embeddings_batch([
    "Community profile 1...",
    "Community profile 2...",
    "Community profile 3..."
])

# Cached embedding retrieval
cached_embedding = embedder.get_or_create_embedding(
    text="Community profile...",
    cache_key="community_123_embedding"
)
```

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
- Fast inference (<50ms per embedding)
- Good accuracy for OBCMS use cases
- 384 dimensions (compact)
- Runs locally (no external API)

#### 5. Vector Store (`vector_store.py`)

**Purpose:** FAISS-based vector database for similarity search.

**Key Methods:**
```python
from ai_assistant.services.vector_store import VectorStore

store = VectorStore(index_name="communities")

# Add vector to index
store.add_vector(
    vector=embedding,
    metadata={"id": 123, "name": "Barangay Poblacion", "province": "Lanao"}
)

# Similarity search (top-k nearest neighbors)
results = store.search(
    query_vector=query_embedding,
    top_k=5,
    filter_metadata={"province": "Lanao"}
)
# Returns: [(similarity_score, metadata), ...]

# Batch add vectors
store.add_vectors_batch(
    vectors=[emb1, emb2, emb3],
    metadata_list=[meta1, meta2, meta3]
)

# Save index to disk (persistence)
store.save_index("communities_index.faiss")

# Load index from disk
store.load_index("communities_index.faiss")
```

**Index Types:**
- `communities` - Community similarity matching
- `policies` - Policy evidence search
- `stakeholders` - Stakeholder matching
- `assessments` - MANA assessment search

**Performance:**
- Search 1K vectors: 50-80ms
- Search 10K vectors: 100-300ms
- Index size: ~4MB per 10K vectors

#### 6. Similarity Search (`similarity_search.py`)

**Purpose:** High-level semantic search across modules.

**Key Methods:**
```python
from ai_assistant.services.similarity_search import SimilaritySearch

search = SimilaritySearch()

# Find similar communities
similar = search.find_similar_communities(
    community_id=123,
    top_k=5,
    similarity_threshold=0.75
)
# Returns: Communities with >75% similarity

# Find relevant policies
policies = search.search_policies(
    query="fishing livelihood support",
    top_k=10,
    filters={"status": "approved"}
)

# Multi-module search
results = search.unified_search(
    query="education infrastructure needs in Lanao",
    modules=["communities", "mana", "policies", "projects"]
)
# Returns: Ranked results from all specified modules
```

### Module-Specific AI Services

#### Communities AI (`src/communities/ai_services/`)

**Services:**
1. `data_validator.py` - Demographic data validation
2. `needs_classifier.py` - AI needs prediction (12 categories)
3. `community_matcher.py` - Similarity matching

**Example Usage:**
```python
from communities.ai_services.needs_classifier import NeedsClassifier

classifier = NeedsClassifier()
predictions = classifier.classify_needs(
    community_id=123,
    demographic_data={...}
)
# Returns: {
#     "livelihood_support": {"confidence": 0.92, "priority": "high"},
#     "education_infrastructure": {"confidence": 0.88, "priority": "high"},
#     ...
# }
```

#### MANA AI (`src/mana/ai_services/`)

**Services:**
1. `response_analyzer.py` - Participant response analysis
2. `theme_extractor.py` - Theme identification (10 categories)
3. `needs_extractor.py` - Automated needs extraction
4. `report_generator.py` - Auto-report generation
5. `cultural_validator.py` - Cultural appropriateness validation

**Example Usage:**
```python
from mana.ai_services.report_generator import ReportGenerator

generator = ReportGenerator()
report = generator.generate_assessment_report(
    assessment_id=456,
    include_executive_summary=True,
    include_recommendations=True
)
# Returns: Complete report with AI-generated sections
```

#### Coordination AI (`src/coordination/ai_services/`)

**Services:**
1. `stakeholder_matcher.py` - Stakeholder matching (multi-criteria)
2. `partnership_predictor.py` - Partnership success prediction
3. `meeting_intelligence.py` - Meeting summarization, action items
4. `resource_optimizer.py` - Resource allocation optimization

**Example Usage:**
```python
from coordination.ai_services.stakeholder_matcher import StakeholderMatcher

matcher = StakeholderMatcher()
matches = matcher.find_stakeholders(
    project={
        "sector": "Livelihood",
        "region": "Region X",
        "budget": 5000000
    },
    top_k=10
)
# Returns: Ranked stakeholder matches with scores
```

#### Policy AI (`src/recommendations/policies/ai_services/`)

**Services:**
1. `evidence_gatherer.py` - Cross-module evidence collection
2. `policy_generator.py` - AI policy draft generation
3. `impact_simulator.py` - 4-scenario impact simulation
4. `compliance_checker.py` - BARMM compliance validation

**Example Usage:**
```python
from recommendations.policies.ai_services.impact_simulator import ImpactSimulator

simulator = ImpactSimulator()
scenarios = simulator.simulate_impact(
    policy_id=789,
    scenarios=["optimistic", "realistic", "pessimistic", "community_led"]
)
# Returns: Impact predictions for each scenario
```

#### M&E AI (`src/project_central/ai_services/`)

**Services:**
1. `anomaly_detector.py` - Budget anomaly detection (95%+ accuracy)
2. `report_generator.py` - Automated M&E reporting
3. `performance_forecaster.py` - Project outcome prediction (70-75% accuracy)
4. `risk_analyzer.py` - Risk scoring and early warning

**Example Usage:**
```python
from project_central.ai_services.anomaly_detector import AnomalyDetector

detector = AnomalyDetector()
anomalies = detector.detect_budget_anomalies(
    ppa_id=101,
    threshold="medium"  # low, medium, high, critical
)
# Returns: List of detected anomalies with severity and recommendations
```

### AI Integration Patterns

#### Pattern 1: Cached AI Analysis

**Use Case:** Expensive AI operations that don't change frequently

```python
from ai_assistant.services.cache_service import CacheService
from ai_assistant.services.gemini_service import GeminiService

def analyze_with_cache(data_id, data):
    cache = CacheService()
    cache_key = f"analysis_{data_id}"

    # Check cache first
    cached = cache.get_ai_response(cache_key)
    if cached:
        return cached

    # Generate with AI
    service = GeminiService()
    result = service.generate_text(
        prompt=f"Analyze this data: {data}",
        context={"data_id": data_id}
    )

    # Cache for 24 hours
    cache.set_ai_response(cache_key, result, ttl=86400)

    return result
```

#### Pattern 2: Async AI Processing (Celery)

**Use Case:** Long-running AI operations (report generation, batch analysis)

```python
from celery import shared_task
from mana.ai_services.report_generator import ReportGenerator

@shared_task
def generate_mana_report_async(assessment_id):
    """Generate MANA report asynchronously."""
    generator = ReportGenerator()
    report = generator.generate_assessment_report(assessment_id)

    # Notify user when complete
    notify_user(assessment_id, report)

    return report

# Usage in view
def request_report(request, assessment_id):
    task = generate_mana_report_async.delay(assessment_id)
    messages.info(request, f"Report generation started. Task ID: {task.id}")
    return redirect("assessment_detail", assessment_id)
```

#### Pattern 3: AI with Fallback

**Use Case:** Ensure system works even if AI fails

```python
from ai_assistant.services.gemini_service import GeminiService
from ai_assistant.utils.error_handler import AIErrorHandler

def classify_with_fallback(data):
    service = GeminiService()
    error_handler = AIErrorHandler()

    try:
        # Try AI classification
        result = service.generate_text(
            prompt=f"Classify this: {data}",
            timeout=10
        )
        return {"source": "ai", "result": result}

    except Exception as e:
        # Log error
        error_handler.log_error(e, context={"data": data})

        # Fallback to rule-based classification
        result = rule_based_classification(data)
        return {"source": "fallback", "result": result}
```

#### Pattern 4: Cultural Validation Pipeline

**Use Case:** Ensure all AI outputs are culturally appropriate

```python
from mana.ai_services.cultural_validator import CulturalValidator

def generate_with_cultural_validation(prompt, context):
    service = GeminiService()
    validator = CulturalValidator()

    # Generate AI response
    response = service.generate_text(prompt, context)

    # Validate cultural appropriateness
    validation = validator.validate(response)

    if validation["score"] < 0.70:
        # Below threshold - regenerate with stricter prompt
        enhanced_prompt = validator.enhance_prompt_for_culture(prompt)
        response = service.generate_text(enhanced_prompt, context)
        validation = validator.validate(response)

    return {
        "response": response,
        "cultural_validation": validation
    }
```

### AI Management Commands

**Located in:** `src/ai_assistant/management/commands/`

#### Health Check
```bash
cd src
python manage.py ai_health_check

# Output:
# ✅ Google Gemini API: Connected (latency: 0.8s)
# ✅ Redis Cache: Connected (95% hit rate)
# ✅ FAISS Indices: Loaded (3 indices, 12,450 vectors)
# ✅ Cost Tracker: Active ($124.50 this month)
```

#### Index Communities
```bash
python manage.py index_communities

# Output:
# Indexing 234 communities...
# Generating embeddings... [=============] 234/234
# Building FAISS index...
# ✅ Index complete: 234 vectors added
# 📁 Saved to: ai_assistant/vector_indices/communities_index.faiss
```

#### Index Policies
```bash
python manage.py index_policies --status approved

# Output:
# Indexing approved policies...
# Found 87 policies
# Generating embeddings... [=============] 87/87
# ✅ Index complete: 87 vectors added
```

#### Rebuild Vector Index
```bash
python manage.py rebuild_vector_index --index all

# Output:
# Rebuilding all vector indices...
# [1/4] Communities index... ✅ 234 vectors
# [2/4] Policies index... ✅ 87 vectors
# [3/4] Stakeholders index... ✅ 156 vectors
# [4/4] Assessments index... ✅ 342 vectors
# ✅ All indices rebuilt
```

### AI Testing

**Located in:** `src/ai_assistant/tests/`

#### Test Structure
```
ai_assistant/tests/
├── test_gemini_service.py (185 lines, 35 tests)
├── test_cache_service.py (241 lines, 42 tests)
├── test_embedding_service.py (180 lines, 28 tests)
├── test_vector_store.py (260 lines, 38 tests)
└── test_similarity_search.py (280 lines, 45 tests)
```

#### Running AI Tests
```bash
# All AI tests
pytest src/ai_assistant/tests/ -v

# Specific service
pytest src/ai_assistant/tests/test_gemini_service.py -v

# Skip slow tests (API calls)
pytest src/ai_assistant/tests/ -m "not slow" -v

# With coverage
pytest src/ai_assistant/tests/ --cov=ai_assistant --cov-report=html
```

#### Test Example
```python
# test_gemini_service.py
import pytest
from ai_assistant.services.gemini_service import GeminiService

@pytest.mark.slow  # Marked as slow (real API call)
def test_gemini_generate_text():
    service = GeminiService()
    response = service.generate_text(
        prompt="Summarize: Fishing community with 5234 population",
        model="gemini-2.5-flash"
    )

    assert response is not None
    assert len(response) > 20  # Non-trivial response
    assert "fishing" in response.lower()

@pytest.mark.unit  # Fast unit test
def test_prompt_template_generation():
    from ai_assistant.services.prompt_templates import PromptTemplates
    templates = PromptTemplates()

    prompt = templates.get_needs_classification_prompt(
        community_data={"livelihood": "Fishing"}
    )

    assert "fishing" in prompt.lower()
    assert "bangsamoro" in prompt.lower()  # Cultural context
    assert len(prompt) > 100  # Detailed prompt
```

### Cost Management

#### Cost Tracking
```python
from ai_assistant.utils.cost_tracker import CostTracker

tracker = CostTracker()

# Track AI operation
tracker.log_operation(
    operation="needs_classification",
    model="gemini-2.5-flash",
    input_tokens=450,
    output_tokens=220,
    cost_usd=0.0015
)

# Get monthly costs
monthly_cost = tracker.get_monthly_cost()  # Example: $124.50

# Get cost by module
costs_by_module = tracker.get_costs_by_module()
# {"communities": $18.50, "mana": $42.30, "policy": $35.70, ...}
```

#### Cost Optimization Strategies
1. **Aggressive caching** - 95% hit rate reduces API calls by 95%
2. **Batch processing** - Process multiple items in single API call
3. **Gemini 2.5 Flash** - 95% cheaper than Claude, good accuracy
4. **Local embeddings** - sentence-transformers runs locally (no API cost)
5. **Result size limits** - Max 2048 tokens per response
6. **Scheduled off-peak processing** - Run large analyses during low-traffic hours

### Security Considerations

#### API Key Management
```python
# settings.py
GOOGLE_API_KEY = env("GOOGLE_API_KEY")  # Never commit to git
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default=None)

# API key rotation (quarterly)
AI_API_KEY_ROTATION_DAYS = 90
```

#### Safe Query Execution
```python
# src/common/ai_services/chat/query_executor.py
class QueryExecutor:
    """Execute AI-generated database queries safely."""

    ALLOWED_MODELS = [
        "Region", "Province", "Community", "PPA", "Policy"
    ]

    PROHIBITED_PATTERNS = [
        "delete", "update", "insert", "drop", "alter",
        "exec", "eval", "import", "__"
    ]

    def execute_safe_query(self, query_code):
        # AST parsing to detect dangerous patterns
        tree = ast.parse(query_code)

        # Validate query safety
        if not self.is_safe(tree):
            raise SecurityError("Unsafe query detected")

        # Execute with read-only permissions
        return self.execute_read_only(query_code)
```

#### Data Privacy
- AI processes only authorized data (user permissions respected)
- No PII in AI prompts
- Embeddings anonymized (no personally identifiable info)
- Audit logging for all AI operations
- HTTPS/TLS for API communication

### Performance Optimization

#### Response Times
| Operation | Target | Actual |
|-----------|--------|--------|
| Gemini API Call | <2s | 0.8-1.5s |
| Cached Response | <100ms | 15-50ms |
| Vector Search (1K) | <100ms | 50-80ms |
| Vector Search (10K) | <500ms | 100-300ms |
| Unified Search | <2s | 0.5-1.5s |

#### Optimization Techniques
1. **Redis caching** - 95% hit rate, sub-50ms retrieval
2. **FAISS indexing** - Fast nearest neighbor search
3. **Batch embedding** - Process multiple texts together
4. **Connection pooling** - Reuse HTTP connections to AI API
5. **Async processing** - Celery for long-running tasks

### Deployment Checklist

Before deploying AI features to production:

- [ ] Google Gemini API key configured in environment
- [ ] Redis server running and configured
- [ ] Celery worker and beat services running
- [ ] Vector indices built and saved to disk
- [ ] Management commands tested (ai_health_check, index_*)
- [ ] AI tests passing (197/197 tests)
- [ ] Cost tracking enabled and monitored
- [ ] Cultural sensitivity validation active
- [ ] Security audit completed
- [ ] Documentation updated

### Resources

**AI Documentation:**
- [AI Strategy Comprehensive](../ai/AI_STRATEGY_COMPREHENSIVE.md) - Full strategy
- [AI Quick Start](../ai/AI_QUICK_START.md) - Developer tutorial
- [AI User Guide](../USER_GUIDE_AI_FEATURES.md) - User-facing guide
- [AI Implementation Complete Summary](../../AI_IMPLEMENTATION_COMPLETE_SUMMARY.md) - Status

**Module-Specific Guides:**
- [Communities AI](../improvements/COMMUNITIES_AI_IMPLEMENTATION_COMPLETE.md)
- [MANA AI](../improvements/MANA_AI_INTELLIGENCE_IMPLEMENTATION.md)
- [Coordination AI](../improvements/COORDINATION_AI_IMPLEMENTATION.md)
- [Policy AI](../improvements/POLICY_AI_ENHANCEMENT.md)
- [M&E AI](../improvements/ME_AI_IMPLEMENTATION.md)

**API Documentation:**
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [FAISS Documentation](https://faiss.ai/)
- [Sentence Transformers](https://www.sbert.net/)

## Development Best Practices

### Using AI Assistants Effectively

1. **Provide Context:** Always include relevant code context and requirements
2. **Review Output:** Never commit AI-generated code without review
3. **Test Thoroughly:** All AI-generated code must pass tests
4. **Follow Standards:** Ensure AI output follows project conventions

### Project-Specific AI Guidelines

- **Django Patterns:** AI assistants are configured to follow Django best practices
- **Security First:** All code reviews check for security vulnerabilities
- **Test Coverage:** AI-generated code should include test cases
- **Documentation:** All significant changes should include documentation updates

## Configuration Files Read by AI

AI assistants read these project files for context:
- **[CLAUDE.md](../../CLAUDE.md)** - Project-specific Claude instructions (ROOT)
- **[GEMINI.md](../../GEMINI.md)** - Gemini configuration (ROOT)
- **[AGENTS.md](../../AGENTS.md)** - AI agents overview (ROOT)
- `docs/` - Project documentation
- `requirements/` - Python dependencies
- `.env.example` - Environment configuration template

## Getting Started with AI Development

1. **Read Configuration:**
   - [../CLAUDE.md](../../CLAUDE.md) - Primary AI assistant setup
   - [../AGENTS.md](../../AGENTS.md) - Overview of all AI tools

2. **Set Up Environment:**
   - Configure API keys (if needed)
   - Review project-specific instructions in CLAUDE.md
   - Understand coding standards

3. **Start Coding:**
   - Use AI for boilerplate and repetitive tasks
   - Leverage AI for code review and suggestions
   - Always review and test AI-generated code

## Development Workflows

### With Claude Code
1. Describe what you want to build
2. Claude reads CLAUDE.md for project context
3. Claude generates code following project standards
4. Review, test, and refine
5. Commit with descriptive messages

### With Gemini
1. Use for alternative perspectives
2. Gemini reads GEMINI.md for configuration
3. Compare suggestions with Claude's output
4. Choose best approach

## Database Management

### Critical Issue: SQLite Database Location

- **[SQLite Database Location Issue](sqlite-database-location-issue.md)** - Comprehensive troubleshooting guide
  - **Problem**: Django ORM returns empty results despite data existing in SQLite
  - **Root Cause**: Database file location mismatch between Django config and backup files
  - **Solutions**: Automated scripts, path standardization, verification steps
  - **Prevention**: Development best practices and quick reference commands

### Quick Database Commands

#### Check Database Location
```bash
cd src
../venv/bin/python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"
```

#### Backup Database
```bash
./scripts/db_backup.sh  # Automated with verification
```

#### Restore Database
```bash
./scripts/db_restore.sh backups/db.sqlite3.backup.20250930_221241
```

#### Verify Data
```bash
cd src
../venv/bin/python manage.py shell -c "
from common.models import Region, Province, Municipality, Barangay
print(f'Regions: {Region.objects.count()}')
print(f'Provinces: {Province.objects.count()}')
print(f'Municipalities: {Municipality.objects.count()}')
print(f'Barangays: {Barangay.objects.count()}')
"
```

## Static Files Architecture

### Directory Structure

The project uses a **centralized static files approach** with all static assets in `src/static/`:

```
src/
├── static/                    # Project-wide static files (configured)
│   ├── admin/                # Admin interface customizations
│   │   ├── css/custom.css
│   │   └── js/custom.js
│   ├── common/               # Common app-specific assets
│   │   ├── css/
│   │   ├── js/
│   │   └── vendor/           # App-specific vendor libraries
│   │       └── fullcalendar/ # FullCalendar (used primarily in common)
│   ├── communities/
│   ├── coordination/
│   ├── mana/
│   └── vendor/               # Shared vendor libraries
│       ├── leaflet/          # Map library (used across apps)
│       ├── localforage/      # Offline storage
│       └── idb/              # IndexedDB wrapper
└── obc_management/
    └── static/               # Empty (placeholder only)
```

### Configuration

**Settings:** `src/obc_management/settings/base.py`
```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR.parent / "static",  # Points to src/static/
]
```

### Why This Structure?

1. ✅ **Centralized management** - All static files in one location
2. ✅ **Better for shared resources** - Vendor libraries used across multiple apps
3. ✅ **Consistent with templates** - Templates in `src/templates/`, static in `src/static/`
4. ✅ **Easier deployment** - Single source for `collectstatic`

### Vendor Library Organization

**Two vendor directories exist:**
- `src/static/common/vendor/` - FullCalendar (primarily used by common app)
- `src/static/vendor/` - Truly shared libraries (Leaflet, localforage, idb)

This minor inconsistency is intentional and doesn't cause issues.

### Common Static Files Issues

#### FullCalendar Not Loading
- **Symptom**: Calendar widget doesn't render, JavaScript not loading
- **Cause**: `STATICFILES_DIRS` pointing to wrong directory (e.g., `obc_management/static` instead of `src/static`)
- **Solution**: Ensure `STATICFILES_DIRS = [BASE_DIR.parent / "static"]` in settings
- **Verification**:
  ```bash
  cd src
  ../venv/bin/python manage.py shell -c "from django.conf import settings; print(settings.STATICFILES_DIRS)"
  ```

#### 404 on Static Files
- **During Development**: Check `STATICFILES_DIRS` points to `src/static/`
- **In Production**: Run `./manage.py collectstatic` to gather files to `STATIC_ROOT`
- **Restart Required**: Changes to `settings.py` require server restart

## Common Development Issues

### Empty Dropdowns in Forms
- **Symptom**: Location dropdowns show "Select region..." but no options
- **Cause**: Database location mismatch or missing geographic data
- **Solution**: See [SQLite Database Location Issue](sqlite-database-location-issue.md)

### Migration Conflicts
- **Never delete the database** - contains valuable development data
- Use `./manage.py migrate --fake` for conflicts
- Restore from backup: `./scripts/db_restore.sh`

## Scripts Reference

Located in `scripts/` directory:

- **db_backup.sh** - Create timestamped database backup with verification
- **db_restore.sh** - Restore database from backup (with confirmation)
- **bootstrap_venv.sh** - Set up Python virtual environment

## Security & Permissions

### Django Permissions & RBAC

**Comprehensive Guide:** [Django Permissions & RBAC Best Practices](DJANGO_PERMISSIONS_RBAC_BEST_PRACTICES.md)

**Key Topics Covered:**
- Current OBCMS permission infrastructure (MOA RBAC, Budget Execution, MANA)
- Django's built-in permission features (Permission model, Groups, decorators)
- Best practices for custom permissions (3-layer architecture)
- RBAC implementation recommendations for BMMS
- Complete code examples and testing strategies

**Existing Permission Systems:**
1. **MOA RBAC** - Organization-scoped permissions (✅ Complete)
   - Custom decorators: `@moa_can_edit_ppa`, `@moa_view_only`
   - Mixins: `MOAFilteredQuerySetMixin`, `MOAPPAAccessMixin`
   - Template tags: `{% can_manage_ppa user ppa %}`

2. **Budget Execution** - Group-based roles (✅ Complete)
   - Groups: Budget Officers, Finance Directors, Finance Staff
   - Decorators: `@budget_officer_required`, `@finance_director_required`
   - DRF permissions: `CanReleaseAllotment`, `CanApproveAllotment`

3. **MANA Access Control** - Middleware-based restrictions (✅ Active)
   - Restricts participants/facilitators to specific URLs
   - Uses Django permissions: `user.has_perm("mana.can_access_regional_mana")`

**Quick Links:**
- [MOA RBAC Quick Reference](../improvements/MOA_RBAC_QUICK_REFERENCE.md)
- [MOA RBAC Usage Guide](MOA_RBAC_USAGE.md)
- [Budget Execution Permissions](/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/budget_execution/permissions.py)

## Related Documentation
- [Development Environment Setup](../env/development.md)
- [Improvement Plan Template](../improvements/improvement_plan_template.md)
- [UI Design System](../ui/ui-design-system.md)
- [Testing Guidelines](../testing/README.md)

---

**Note:** This directory is for development guidelines and documentation. AI configuration files remain in the project root for proper agent functionality.
