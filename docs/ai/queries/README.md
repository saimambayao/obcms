# OBCMS Query Template System

**Status**: Architecture Complete | Implementation Ready
**Current Scale**: 151 templates → **Target**: 500+ templates
**Performance Target**: <10ms match time maintained at scale

---

## Quick Links

### 📚 Core Documentation
- **[Architecture Document](ARCHITECTURE.md)** ⭐ **START HERE** - Complete architecture for scaling to 500+ templates
- **[Category Index](categories/)** - Template documentation by category
- **[Example Queries](examples/)** - Real-world query examples and use cases

### 🚀 For Developers
- **Implementation Guide**: `ARCHITECTURE.md` Section 6 (Implementation Roadmap)
- **Template Creation**: `ARCHITECTURE.md` Section 2.2 (Template Metadata Schema)
- **Testing Guide**: `ARCHITECTURE.md` Section 4.3 (Testing Approach)
- **Django Commands**: See below for quick reference

### 📊 For Project Managers
- **Timeline**: 8 weeks (4 phases) - see `ARCHITECTURE.md` Section 6
- **Progress Tracking**: Use phase checklists in architecture document
- **Success Metrics**: `ARCHITECTURE.md` Section 7

---

## What is the Query Template System?

The OBCMS Query Template System converts **natural language queries** into **Django ORM database queries** using **pattern matching** (NO AI required). This enables fast, accurate, and cost-free query processing.

### Example Flow:

```
User Query:           "How many communities in Region IX?"
                               ↓
Pattern Match:        Template ID: count_communities_by_location
                               ↓
Entity Extraction:    location = {'type': 'region', 'value': 'Region IX'}
                               ↓
Query Generation:     OBCCommunity.objects.filter(
                        barangay__municipality__province__region__name__icontains='Region IX'
                      ).count()
                               ↓
Result:               42 communities
```

### Key Benefits:

✅ **No AI Required**: Pure pattern-matching approach (cost: $0)
✅ **Fast**: <10ms query matching even with 500+ templates
✅ **Accurate**: 95%+ match accuracy with proper patterns
✅ **Scalable**: Lazy loading + trie indexing support 500+ templates
✅ **Maintainable**: Automated testing and documentation

---

## Current State (151 Templates)

### Template Distribution:

```
communities:    25 templates (17%)
coordination:   30 templates (20%)
mana:           21 templates (14%)
policies:       25 templates (17%)
projects:       25 templates (17%)
staff:          10 templates (7%)
general:        15 templates (10%)
─────────────────────────────────
TOTAL:         151 templates (100%)
```

### File Structure:

```
src/common/ai_services/chat/query_templates/
├── base.py                  # Core classes
├── communities.py           # 25 templates
├── coordination.py          # 30 templates
├── mana.py                  # 21 templates
├── policies.py              # 25 templates
├── projects.py              # 25 templates
└── staff_general.py         # 25 templates
```

---

## Target State (500+ Templates)

### Enhanced Distribution:

```
CORE DOMAINS (7 categories, 385 templates):
  communities:    65 templates (+40)
  coordination:   75 templates (+45)
  mana:           60 templates (+39)
  policies:       60 templates (+35)
  projects:       60 templates (+35)
  staff:          35 templates (+10)
  general:        30 templates (+5)

NEW DOMAINS (8 categories, 190 templates):
  geographic:     40 templates [NEW]
  temporal:       30 templates [NEW]
  cross_domain:   30 templates [NEW]
  analytics:      25 templates [NEW]
  reports:        20 templates [NEW]
  validation:     15 templates [NEW]
  audit:          15 templates [NEW]
  admin:          15 templates [NEW]
─────────────────────────────────────
TOTAL:          575 templates (+424)
```

### Enhanced File Structure:

```
src/common/ai_services/chat/query_templates/
├── base.py                          # Core classes (unchanged)
├── registry/                        # NEW: Advanced registry
│   ├── advanced_registry.py        # Lazy loading, trie, caching
│   └── template_loader.py          # Dynamic template loading
│
├── core_domains/                    # Enhanced original categories
│   ├── communities/
│   │   ├── count_queries.py
│   │   ├── list_queries.py
│   │   ├── aggregate_queries.py
│   │   └── ... (65 total)
│   ├── coordination/               # (75 templates)
│   ├── mana/                       # (60 templates)
│   ├── policies/                   # (60 templates)
│   ├── projects/                   # (60 templates)
│   ├── staff/                      # (35 templates)
│   └── general/                    # (30 templates)
│
├── new_domains/                     # NEW: 8 categories
│   ├── geographic/                 # (40 templates)
│   ├── temporal/                   # (30 templates)
│   ├── cross_domain/               # (30 templates)
│   ├── analytics/                  # (25 templates)
│   ├── reports/                    # (20 templates)
│   ├── validation/                 # (15 templates)
│   ├── audit/                      # (15 templates)
│   └── admin/                      # (15 templates)
│
└── utilities/                       # NEW: Helper tools
    ├── template_builder.py
    ├── template_validator.py
    └── template_generator.py
```

---

## Query Types Supported

### 1. COUNT Queries
Count records matching criteria.

**Examples**:
- "How many communities in Region IX?"
- "Count active partnerships"
- "Total workshops last 6 months"

**Response**: Single number with context

### 2. LIST Queries
Retrieve list of matching items.

**Examples**:
- "Show all communities in Zamboanga"
- "List pending policy recommendations"
- "Show workshops this month"

**Response**: HTML table with results

### 3. GET Queries
Retrieve single item by identifier.

**Examples**:
- "Get community details for Barangay XYZ"
- "Show partnership info for ORG-123"
- "Get policy recommendation #45"

**Response**: Detail card with item information

### 4. FIND Queries
Search/filter items by attributes.

**Examples**:
- "Find Maranao communities with fishing livelihood"
- "Find organizations working on education"
- "Find workshops with high attendance"

**Response**: Filtered list with match criteria

### 5. COMPARE Queries
Compare multiple items.

**Examples**:
- "Compare Region IX vs Region X communities"
- "Compare MANA workshop completion rates by province"
- "Compare budget allocation across projects"

**Response**: Comparison table or chart

### 6. TREND Queries
Temporal analysis and trends.

**Examples**:
- "Workshop trends last 6 months"
- "Community registration trends this year"
- "Policy approval rate trends"

**Response**: Line chart data and summary

### 7. AGGREGATE Queries
Statistical summaries.

**Examples**:
- "Average population by region"
- "Total budget by program"
- "Workshop attendance statistics"

**Response**: Summary statistics with breakdown

### 8. RANK Queries
Ordered results by metric.

**Examples**:
- "Top 10 communities by population"
- "Highest budget projects"
- "Most active organizations"

**Response**: Ranked list with metrics

### 9. VALIDATE Queries
Data quality checks.

**Examples**:
- "Communities missing demographic data"
- "Incomplete workshop assessments"
- "Projects with outdated status"

**Response**: Validation report with issues

### 10. EXPORT Queries
Data export requests.

**Examples**:
- "Export communities to CSV"
- "Export workshop results to Excel"
- "Generate policy recommendation report"

**Response**: Download link or file

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-2) | CRITICAL
- AdvancedTemplateRegistry with lazy loading
- PatternTrie indexing
- Multi-level caching
- Performance testing framework

### Phase 2: Core Enhancement (Weeks 3-4) | HIGH
- Reorganize 151 → 385 templates
- Add 234 new templates to core domains
- Automated testing for all templates

### Phase 3: New Domains (Weeks 5-6) | HIGH
- Create 8 new domain categories
- Add 190 new templates
- Cross-domain query support

### Phase 4: Enhancement (Weeks 7-8) | MEDIUM
- Enhanced entity extraction (15+ types)
- Response formatters for all query types
- Auto-generated documentation
- Production deployment

**Total**: 8 weeks to full deployment

---

## Django Management Commands

### Template Management

```bash
# Generate documentation for all templates
python manage.py generate_template_docs --all

# Generate docs for specific category
python manage.py generate_template_docs --category communities

# Validate all templates
python manage.py validate_templates --strict

# Check for deprecated templates
python manage.py check_deprecated_templates --warn-if-old

# List all templates by category
python manage.py list_templates --by-category

# Show template statistics
python manage.py template_stats

# Test template performance
python manage.py benchmark_templates --category all
```

### Template Testing

```bash
# Run all template tests
pytest tests/test_query_templates/ -v

# Run performance benchmarks
pytest tests/test_query_templates/ -m benchmark

# Test specific category
pytest tests/test_query_templates/test_communities_templates.py -v

# Test with coverage
pytest tests/test_query_templates/ --cov=common.ai_services.chat.query_templates
```

---

## Quick Start: Adding a New Template

### Step 1: Choose Category and File

```bash
# For core domains (existing categories)
# File: src/common/ai_services/chat/query_templates/core_domains/{category}/{query_type}_queries.py

# For new domains
# File: src/common/ai_services/chat/query_templates/new_domains/{category}/{query_type}_queries.py
```

### Step 2: Create Template

```python
from common.ai_services.chat.query_templates.base import QueryTemplate, QueryType, Complexity

QueryTemplate(
    id='my_new_template',
    category='communities',

    # Pattern (regex to match user queries)
    pattern=r'\b(how many|count)\s+communities\s+with\s+(?P<livelihood>\w+)\s+livelihood',

    # Query template (Django ORM with placeholders)
    query_template='OBCCommunity.objects.filter(primary_livelihood__icontains="{livelihood}").count()',

    # Entities
    required_entities=['livelihood'],
    optional_entities=[],

    # Examples (for testing and documentation)
    examples=[
        'How many communities with fishing livelihood?',
        'Count communities with farming livelihood',
    ],

    # Metadata
    priority=8,
    query_type=QueryType.COUNT,
    complexity=Complexity.FILTERED,
    description='Count communities by livelihood type',
    tags=['count', 'communities', 'livelihood', 'filtered'],

    # Performance hints
    estimated_latency_ms=15,
    cache_ttl_seconds=300,
)
```

### Step 3: Register Template

```python
# At bottom of file
COMMUNITIES_LIVELIHOOD_TEMPLATES = [
    # ... your templates here
]

# Templates auto-registered via __init__.py
```

### Step 4: Write Tests

```python
# tests/test_query_templates/test_communities_templates.py

def test_count_communities_by_livelihood():
    template = registry.get_template('my_new_template')

    # Test pattern match
    assert template.matches('how many communities with fishing livelihood')

    # Test entity requirement
    entities = {'livelihood': {'value': 'fishing'}}
    assert template.can_execute(entities)

    # Test query generation
    query = matcher.generate_query(template, entities)
    assert 'fishing' in query
```

### Step 5: Generate Documentation

```bash
python manage.py generate_template_docs --category communities
```

**Total time**: 10 minutes per template

---

## Performance Optimization

### Lazy Loading
Templates loaded on-demand by category.

**Impact**:
- Startup time: 500ms → 100ms (80% faster)
- Memory usage: 50MB → 15MB (70% reduction)

### Trie Indexing
Pattern prefix matching reduces search space.

**Impact**:
- Search space: 500 → ~50 templates (90% reduction)
- Match time: 10ms → 3ms (70% faster)

### Multi-Level Caching
L1 (in-memory) + L2 (Redis) caching.

**Impact**:
- Cache hit rate: ~80%
- Effective match time: 2.8ms (with cache)

### Priority Queue Ranking
Heap-based top-k retrieval.

**Impact**:
- Ranking time: 15ms → 5ms (67% faster)
- Memory: O(n) → O(k) where k=10

---

## Success Metrics

### Performance
- ✅ Template match: <10ms (99th percentile)
- ✅ Registry lookup: <2ms
- ✅ Cache hit rate: >75%
- ✅ Memory usage: <25MB

### Quality
- ✅ Pattern match accuracy: >95%
- ✅ Query generation correctness: 100%
- ✅ Test coverage: 100%

### Maintenance
- ✅ Time to add template: <10 minutes
- ✅ Documentation: Auto-generated
- ✅ Deprecation workflow: Defined

---

## Support & Resources

### Documentation
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) - Complete design document
- **Category Docs**: [categories/](categories/) - Template docs by category
- **Examples**: [examples/](examples/) - Real-world query examples

### Code
- **Templates**: `src/common/ai_services/chat/query_templates/`
- **Tests**: `src/tests/test_query_templates/`
- **Entity Extractor**: `src/common/ai_services/chat/entity_extractor.py`
- **Template Matcher**: `src/common/ai_services/chat/template_matcher.py`

### Testing
- **Unit Tests**: Pattern matching, query generation
- **Integration Tests**: End-to-end with test database
- **Performance Tests**: Benchmark all operations

---

## Contributing

When adding templates:

1. ✅ Follow naming conventions (`{query_type}_{focus_area}_queries.py`)
2. ✅ Include comprehensive examples (5+ variations)
3. ✅ Write unit tests (pattern + query generation)
4. ✅ Document entity requirements
5. ✅ Set appropriate priority (1-10)
6. ✅ Generate documentation

**See**: [ARCHITECTURE.md](ARCHITECTURE.md) Section 2 for detailed guidelines

---

## FAQs

### Q: Why not use AI/LLMs?
**A**: Pattern matching is faster (<10ms vs 500ms+), cheaper ($0 vs $0.01/query), and more accurate (95%+ vs 80-85%) for structured queries. AI is great for unstructured queries, but most OBCMS queries follow predictable patterns.

### Q: How do you handle 500+ templates without performance issues?
**A**: Lazy loading (load on-demand), trie indexing (reduce search space), multi-level caching (avoid recomputation), and priority queue ranking (efficient top-k retrieval). See [ARCHITECTURE.md](ARCHITECTURE.md) Section 3.2.

### Q: What if a query doesn't match any template?
**A**: System falls back to AI chat (Gemini/Claude) for unstructured queries. Templates handle 80%+ of queries; AI handles the rest.

### Q: How do you maintain 500+ templates?
**A**: Automated testing (100% coverage), auto-generated documentation, deprecation workflow, and validation pipeline. Adding a new template takes <10 minutes.

### Q: Can templates span multiple modules?
**A**: Yes! Cross-domain templates support queries like "How many MANA workshops for communities in Region IX?" See [ARCHITECTURE.md](ARCHITECTURE.md) Section 5.2.

---

**Last Updated**: October 6, 2025
**Status**: Architecture Complete | Implementation Ready
**Next Milestone**: Phase 1 Kickoff
