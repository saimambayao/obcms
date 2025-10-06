# Query Template Authoring Guide

**For:** Developers adding new query templates
**Version:** 1.0
**Last Updated:** 2025-10-06

---

## Overview

This guide explains how to add new query templates to the OBCMS AI Chat system. Templates are pattern-based queries that match natural language questions and convert them to Django ORM queries.

**Prerequisites:**
- Python 3.12+
- Django knowledge (QuerySets, ORM)
- Regex basics
- OBCMS database models

---

## Template Structure

### QueryTemplate Dataclass

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class QueryTemplate:
    """Definition of a query template"""
    id: str                          # Unique identifier
    category: str                    # Domain category
    pattern: str                     # Regex pattern (raw string)
    query_template: str             # Django ORM query string
    required_entities: List[str]     # Required extracted entities
    optional_entities: List[str]     # Optional extracted entities
    examples: List[str]              # Example queries
    priority: int                    # Priority 1-10 (higher = preferred)
    description: str                 # Human-readable description
    tags: List[str]                  # Search tags
    result_type: str                 # 'count', 'list', or 'aggregate'
```

### Field Descriptions

**`id` (str):**
- Unique identifier for the template
- Use snake_case: `count_communities_by_region`
- Descriptive of what the template does
- Must be unique across ALL templates

**`category` (str):**
- Domain category (e.g., 'communities', 'geographic', 'mana')
- Must match the file's domain
- Used for filtering and organization

**`pattern` (str):**
- Regex pattern for matching queries
- Use raw string: `r'...'`
- Case-insensitive by default (use `(?i)` if needed)
- Support natural language variations

**`query_template` (str):**
- Django ORM query as a string
- Will be executed with `.format()` for entity substitution
- Use model manager syntax: `Model.objects.filter(...)`

**`required_entities` (List[str]):**
- List of entity types that MUST be extracted
- Query fails if any required entity not found
- Common: ['region'], ['date_range'], ['sector']

**`optional_entities` (List[str]):**
- List of entity types that MAY be extracted
- Query works without them (sensible defaults)
- Enhance query if present

**`examples` (List[str]):**
- 3-5 example queries that should match
- Used for testing and documentation
- Cover variations and edge cases

**`priority` (int):**
- Priority 1-10 for disambiguation
- **10:** Critical queries (exact matches, high-value)
- **8-9:** Common queries (frequent user needs)
- **6-7:** Specialized queries (specific use cases)
- **4-5:** Edge cases (rare queries)
- **1-3:** Fallback patterns (ambiguous)

**`description` (str):**
- Human-readable description of what the template does
- Used in help text and documentation
- Be clear and concise

**`tags` (List[str]):**
- Keywords for searching and categorization
- Include: action ('count', 'list'), domain ('community', 'assessment'), attributes
- Used by search and filtering

**`result_type` (str):**
- **'count':** Returns a number
- **'list':** Returns a list of objects
- **'aggregate':** Returns aggregated data (sums, averages, etc.)

---

## Pattern Writing Best Practices

### 1. Use Word Boundaries

```python
# ❌ BAD: Matches partial words
pattern = r'count communities'
# Matches: "discount communities" (wrong!)

# ✅ GOOD: Exact word matches
pattern = r'\bcount\s+communities\b'
# Matches: "count communities"
# Doesn't match: "discount communities"
```

### 2. Handle Plural/Singular Variations

```python
# ✅ Use optional 's' for plural
pattern = r'\bshow\s+(me\s+)?(all\s+)?provinces?\b'
# Matches: "show province", "show provinces"

# ✅ Use alternation for variations
pattern = r'\b(community|communities)\b'
# Matches: "community", "communities"
```

### 3. Support Natural Language Variations

```python
# ✅ Support multiple action verbs
pattern = r'\b(show|list|display|get)\s+communities\b'
# Matches: "show communities", "list communities", etc.

# ✅ Handle optional words
pattern = r'\b(show|list)\s+(me\s+)?(all\s+)?provinces?\b'
# Matches: "show provinces", "show me all provinces", etc.
```

### 4. Make Patterns Case-Insensitive

```python
# ✅ Case-insensitive by default (no flag needed)
pattern = r'\bshow\s+communities\b'
# Matches: "Show Communities", "SHOW communities", "show COMMUNITIES"

# ✅ Explicit case-insensitive flag (if needed)
pattern = r'(?i)\bshow\s+communities\b'
```

### 5. Extract Entities with Named Groups

```python
# ✅ Extract location
pattern = r'\bcommunities\s+in\s+(?P<region_name>[\w\s]+?)(\?|$)'
# Matches: "communities in Region IX"
# Extracts: {'region_name': 'Region IX'}

# ✅ Extract multiple entities
pattern = r'\b(?P<priority>\w+)\s+(?P<sector>\w+)\s+needs\b'
# Matches: "critical infrastructure needs"
# Extracts: {'priority': 'critical', 'sector': 'infrastructure'}
```

### 6. Handle Optional Entities

```python
# ✅ Optional location
pattern = r'\bshow\s+communities(\s+in\s+(?P<region_name>[\w\s]+?))?(\?|$)'
# Matches: "show communities" (no location)
# Matches: "show communities in Region IX" (with location)
```

### 7. Test Patterns with Real Queries

```python
import re

pattern = r'\b(how many|count)\s+(obc\s+)?communities?\b'
test_queries = [
    "How many communities?",
    "Count communities",
    "how many OBC communities",
    "Count OBC community"
]

for query in test_queries:
    match = re.search(pattern, query, re.IGNORECASE)
    print(f"'{query}' → {'✅' if match else '❌'}")
```

---

## Query Template Writing

### 1. Simple Count Query

```python
QueryTemplate(
    id='count_all_communities',
    category='communities',
    pattern=r'\b(how many|count|total|number of)\s+(obc\s+)?communities?\b',
    query_template='OBCCommunity.objects.count()',
    required_entities=[],
    optional_entities=[],
    examples=[
        'How many communities?',
        'Count communities',
        'Total OBC communities',
        'Number of communities'
    ],
    priority=8,
    description='Count total OBC communities in system',
    tags=['count', 'community', 'total'],
    result_type='count'
)
```

### 2. Filtered Count Query

```python
QueryTemplate(
    id='count_communities_by_region',
    category='communities',
    pattern=r'\b(how many|count)\s+communities?\s+(in|at|within)\s+(?P<region_name>[\w\s]+?)(\?|$)',
    query_template='OBCCommunity.objects.filter(barangay__municipality__province__region__name__icontains="{region_name}").count()',
    required_entities=['region'],
    optional_entities=[],
    examples=[
        'How many communities in Region IX?',
        'Count communities in BARMM',
        'Communities in Zamboanga Peninsula'
    ],
    priority=9,
    description='Count OBC communities in specific region',
    tags=['count', 'community', 'region', 'location'],
    result_type='count'
)
```

### 3. List Query

```python
QueryTemplate(
    id='list_all_provinces',
    category='geographic',
    pattern=r'\b(show|list|display|get)\s+(me\s+)?(the\s+)?(list of\s+)?(all\s+)?provinces?\b',
    query_template='Province.objects.all().order_by("region__name", "name")',
    required_entities=[],
    optional_entities=[],
    examples=[
        'Show me all provinces',
        'List provinces',
        'Display provinces',
        'Show the list of provinces'
    ],
    priority=10,
    description='List all provinces with region grouping',
    tags=['list', 'province', 'geographic'],
    result_type='list'
)
```

### 4. Filtered List Query

```python
QueryTemplate(
    id='list_critical_needs',
    category='needs',
    pattern=r'\b(show|list|display)\s+(me\s+)?(critical|immediate)\s+needs?\b',
    query_template='Need.objects.filter(urgency_level="immediate").order_by("-priority_score", "-impact_severity")[:30]',
    required_entities=[],
    optional_entities=[],
    examples=[
        'Show me critical needs',
        'List immediate needs',
        'Display critical needs'
    ],
    priority=9,
    description='List needs with critical/immediate urgency',
    tags=['list', 'needs', 'critical', 'priority'],
    result_type='list'
)
```

### 5. Aggregate Query

```python
QueryTemplate(
    id='population_by_region',
    category='communities',
    pattern=r'\b(show|display|get)\s+(total\s+)?(obc\s+)?population\s+by\s+region\b',
    query_template='Region.objects.annotate(total_pop=Sum("provinces__municipalities__barangays__obc_communities__estimated_obc_population")).order_by("-total_pop")',
    required_entities=[],
    optional_entities=[],
    examples=[
        'Show population by region',
        'Display OBC population by region',
        'Get total population by region'
    ],
    priority=8,
    description='Aggregate OBC population by region',
    tags=['aggregate', 'population', 'region', 'demographics'],
    result_type='aggregate'
)
```

### 6. Multi-Entity Query

```python
QueryTemplate(
    id='needs_by_sector_and_location',
    category='needs',
    pattern=r'\b(?P<priority>\w+)?\s*(?P<sector>\w+)\s+needs?\s+(in|at|within)\s+(?P<region_name>[\w\s]+?)(\?|$)',
    query_template='Need.objects.filter(category__sector__icontains="{sector}", community__barangay__municipality__province__region__name__icontains="{region_name}").order_by("-priority_score")[:30]',
    required_entities=['sector', 'region'],
    optional_entities=['priority'],
    examples=[
        'Infrastructure needs in Region IX',
        'Critical education needs in Cotabato',
        'Health needs in BARMM'
    ],
    priority=9,
    description='List needs filtered by sector and location',
    tags=['list', 'needs', 'sector', 'location', 'filtered'],
    result_type='list'
)
```

---

## Step-by-Step Tutorial

### Example: Adding "Count Active Partnerships by MOA" Template

**Step 1: Choose Domain File**

We're adding a coordination query, so edit:
```
src/common/ai_services/chat/query_templates/coordination.py
```

**Step 2: Write the Pattern**

```python
# What variations should we support?
# - "Count partnerships by MOA"
# - "Active partnerships by MOA"
# - "Partnerships by implementing MOA"

# Pattern:
pattern = r'\b(count|show|how many)\s+(active\s+)?partnerships?\s+by\s+(implementing\s+)?moa\b'
```

**Step 3: Write the Query Template**

```python
# Django ORM query:
query_template = 'Partnership.objects.filter(status="active").values("implementing_moa__name").annotate(count=Count("id")).order_by("-count")'
```

**Step 4: Determine Entities**

```python
# Required entities: None (query works without extraction)
required_entities = []

# Optional entities: None (no entity extraction needed)
optional_entities = []
```

**Step 5: Write Examples**

```python
examples = [
    'Count partnerships by MOA',
    'Active partnerships by MOA',
    'How many partnerships by implementing MOA?',
    'Show partnerships by MOA'
]
```

**Step 6: Assign Priority**

```python
# Common query, specific use case
priority = 8
```

**Step 7: Write Description**

```python
description = 'Count active partnerships grouped by implementing MOA'
```

**Step 8: Add Tags**

```python
tags = ['count', 'partnership', 'moa', 'coordination', 'grouped']
```

**Step 9: Set Result Type**

```python
result_type = 'aggregate'  # Grouped counts
```

**Step 10: Complete Template**

```python
QueryTemplate(
    id='count_partnerships_by_moa',
    category='coordination',
    pattern=r'\b(count|show|how many)\s+(active\s+)?partnerships?\s+by\s+(implementing\s+)?moa\b',
    query_template='Partnership.objects.filter(status="active").values("implementing_moa__name").annotate(count=Count("id")).order_by("-count")',
    required_entities=[],
    optional_entities=[],
    examples=[
        'Count partnerships by MOA',
        'Active partnerships by MOA',
        'How many partnerships by implementing MOA?',
        'Show partnerships by MOA'
    ],
    priority=8,
    description='Count active partnerships grouped by implementing MOA',
    tags=['count', 'partnership', 'moa', 'coordination', 'grouped'],
    result_type='aggregate'
)
```

**Step 11: Add to Template List**

At the bottom of `coordination.py`:

```python
COORDINATION_TEMPLATES = [
    # ... existing templates ...

    # NEW TEMPLATE
    QueryTemplate(
        id='count_partnerships_by_moa',
        # ... (full template from Step 10)
    ),
]
```

**Step 12: Write Tests**

Create/edit `src/common/tests/test_coordination_templates.py`:

```python
def test_count_partnerships_by_moa_pattern():
    """Test count_partnerships_by_moa pattern matching"""
    registry = get_template_registry()

    test_queries = [
        'Count partnerships by MOA',
        'Active partnerships by MOA',
        'How many partnerships by implementing MOA?',
        'Show partnerships by MOA'
    ]

    for query in test_queries:
        matches = registry.search_templates(query)
        assert len(matches) > 0, f"No matches for '{query}'"

        # Verify correct template matched
        best_match = matches[0]
        assert best_match.id == 'count_partnerships_by_moa', \
            f"Wrong template matched for '{query}': {best_match.id}"
```

**Step 13: Run Tests**

```bash
cd src
python -m pytest common/tests/test_coordination_templates.py::test_count_partnerships_by_moa_pattern -v

# Expected: PASSED
```

**Step 14: Verify Registration**

```bash
cd src
./manage.py validate_query_templates

# Expected: Template listed in coordination category
```

**Step 15: Manual Testing**

```bash
cd src
./manage.py shell

>>> from common.ai_services.chat.query_templates import get_template_registry
>>> registry = get_template_registry()
>>> matches = registry.search_templates("Count partnerships by MOA")
>>> print(matches[0].id)
# Expected: count_partnerships_by_moa
```

---

## Entity Extraction

### Available Entity Resolvers

**1. LocationResolver:**
- Extracts: regions, provinces, municipalities, barangays
- Usage: `required_entities=['region']`
- Example: "Region IX" → `{'region_name': 'Region IX'}`

**2. DateResolver:**
- Extracts: date ranges, fiscal years, quarters, relative dates
- Usage: `required_entities=['date_range']`
- Example: "last 30 days" → `{'days': 30, 'direction': 'past'}`

**3. SectorResolver:**
- Extracts: development sectors
- Usage: `required_entities=['sector']`
- Sectors: education, infrastructure, health, economic_development, etc.
- Example: "infrastructure needs" → `{'sector': 'infrastructure'}`

**4. PriorityLevelResolver:**
- Extracts: priority levels
- Usage: `required_entities=['priority_level']`
- Levels: critical, high, medium, low
- Example: "critical needs" → `{'priority_level': 'immediate'}`

**5. UrgencyLevelResolver:**
- Extracts: urgency levels
- Usage: `required_entities=['urgency_level']`
- Levels: immediate, short_term, medium_term, long_term
- Example: "immediate needs" → `{'urgency_level': 'immediate'}`

**6. NeedStatusResolver:**
- Extracts: need status
- Usage: `required_entities=['need_status']`
- Status: unmet, met, ongoing, planned, validated
- Example: "unmet needs" → `{'need_status': 'identified'}`

**7. StatusResolver:**
- Extracts: general status
- Usage: `required_entities=['status']`
- Status: active, completed, pending, planned
- Example: "active projects" → `{'status': 'active'}`

**8. EthnicityResolver:**
- Extracts: ethnic groups
- Usage: `required_entities=['ethnicity']`
- Groups: Tausug, Maguindanaoan, Maranao, etc.
- Example: "Tausug communities" → `{'ethnicity': 'Tausug'}`

### Using Entities in Query Templates

**Required Entity:**
```python
QueryTemplate(
    id='needs_by_sector',
    pattern=r'\b(?P<sector>\w+)\s+needs?\b',
    query_template='Need.objects.filter(category__sector__icontains="{sector}").count()',
    required_entities=['sector'],  # Query fails if sector not extracted
    # ...
)
```

**Optional Entity:**
```python
QueryTemplate(
    id='list_communities',
    pattern=r'\b(show|list)\s+communities?(\s+in\s+(?P<region_name>[\w\s]+?))?(\?|$)',
    query_template='OBCCommunity.objects.all()' if not '{region_name}' else 'OBCCommunity.objects.filter(barangay__municipality__province__region__name__icontains="{region_name}")',
    optional_entities=['region'],  # Query works without region
    # ...
)
```

### Adding New Entity Resolvers

If you need a new entity type:

**Step 1:** Create resolver in `src/common/ai_services/chat/entity_resolvers.py`:

```python
class CustomEntityResolver:
    """Resolver for custom entity type"""

    def resolve(self, query: str) -> dict:
        """Extract custom entity from query"""
        # Implementation here
        return {
            'value': extracted_value,
            'confidence': 0.95  # 0.0-1.0
        }
```

**Step 2:** Register in `src/common/ai_services/chat/entity_extractor.py`:

```python
def extract_custom_entity(self, query: str) -> dict:
    """Extract custom entity"""
    resolver = CustomEntityResolver()
    return resolver.resolve(query)
```

**Step 3:** Add to extraction pipeline:

```python
# In EntityExtractor class
def extract_entities(self, query: str, entity_types: List[str]) -> dict:
    """Extract specified entities from query"""
    entities = {}

    if 'custom_entity' in entity_types:
        entities['custom_entity'] = self.extract_custom_entity(query)

    # ... other entity types

    return entities
```

---

## Testing Requirements

### Unit Tests

**Test Pattern Matching:**
```python
def test_template_pattern_matching():
    """Verify pattern matches expected queries"""
    registry = get_template_registry()
    template = registry.templates['your_template_id']

    for example in template.examples:
        matches = registry.search_templates(example)
        assert len(matches) > 0, f"Pattern didn't match example: {example}"
        assert matches[0].id == 'your_template_id'
```

**Test Entity Extraction:**
```python
def test_template_entity_extraction():
    """Verify entities extracted correctly"""
    extractor = EntityExtractor()

    query = "critical infrastructure needs in Region IX"
    entities = extractor.extract_entities(query, ['priority', 'sector', 'region'])

    assert entities['priority']['value'] == 'immediate'
    assert entities['sector']['value'] == 'infrastructure'
    assert entities['region']['value'] == 'Region IX'
```

**Test Query Generation:**
```python
def test_template_query_generation():
    """Verify Django ORM query generates correctly"""
    template = QueryTemplate(
        # ... template definition
    )

    entities = {'region_name': 'Region IX'}
    query_str = template.query_template.format(**entities)

    # Verify query string is valid
    assert 'Region IX' in query_str
    assert 'OBCCommunity.objects' in query_str
```

### Integration Tests

**Test End-to-End Flow:**
```python
def test_template_end_to_end():
    """Test complete query flow"""
    registry = get_template_registry()

    query = "How many communities in Region IX?"
    matches = registry.search_templates(query)

    assert len(matches) > 0

    template = matches[0]
    extractor = EntityExtractor()
    entities = extractor.extract_entities(query, template.required_entities)

    # Execute query (in test environment)
    query_str = template.query_template.format(**{k: v['value'] for k, v in entities.items()})
    # result = eval(query_str)  # Only in test environment!

    # Verify result type
    assert template.result_type in ['count', 'list', 'aggregate']
```

---

## Code Review Checklist

Before submitting a new template:

**Pattern Quality:**
- [ ] Pattern handles plural/singular variations
- [ ] Pattern supports natural language variations
- [ ] Pattern uses word boundaries (`\b`)
- [ ] Pattern extracts entities with named groups
- [ ] Pattern tested with all example queries

**Query Template:**
- [ ] Uses Django ORM (not raw SQL)
- [ ] Handles entity substitution correctly
- [ ] Optimized with `select_related()` or `prefetch_related()`
- [ ] Includes appropriate filters
- [ ] Handles empty results gracefully

**Metadata:**
- [ ] Unique ID (no duplicates)
- [ ] Correct category
- [ ] 3-5 example queries provided
- [ ] Clear, concise description
- [ ] Appropriate priority (1-10)
- [ ] Relevant tags
- [ ] Correct result_type

**Entities:**
- [ ] Required entities listed
- [ ] Optional entities listed
- [ ] Entity extraction tested
- [ ] Extraction failures handled

**Testing:**
- [ ] Unit tests written
- [ ] All examples pass tests
- [ ] Entity extraction tested
- [ ] Query generation tested
- [ ] Integration test (if cross-domain)

**Documentation:**
- [ ] Template added to domain list
- [ ] Template documented in guide
- [ ] Example queries documented
- [ ] Edge cases noted

---

## Common Pitfalls

### 1. Overly Broad Patterns

**❌ Problem:**
```python
pattern = r'show communities'
# Matches too many queries (ambiguous)
```

**✅ Solution:**
```python
pattern = r'\b(show|list|display)\s+(me\s+)?(all\s+)?communities?\b'
# More specific, handles variations
```

### 2. Missing Word Boundaries

**❌ Problem:**
```python
pattern = r'count communities'
# Matches: "discount communities" (wrong!)
```

**✅ Solution:**
```python
pattern = r'\bcount\s+communities\b'
# Only matches exact words
```

### 3. Inefficient Queries

**❌ Problem:**
```python
query_template = 'Need.objects.all()'  # Fetches all needs (slow!)
```

**✅ Solution:**
```python
query_template = 'Need.objects.filter(status="identified")[:30]'  # Limited, filtered
```

### 4. Missing Entity Extraction

**❌ Problem:**
```python
pattern = r'\bneeds in (?P<location>[\w\s]+)\b'
required_entities = []  # Forgot to mark region as required!
```

**✅ Solution:**
```python
pattern = r'\bneeds in (?P<region_name>[\w\s]+)\b'
required_entities = ['region']  # Mark as required
```

### 5. Incorrect Priority

**❌ Problem:**
```python
priority = 10  # Too high for a specialized query
```

**✅ Solution:**
```python
priority = 7  # Appropriate for specialized query
```

### 6. Missing Tests

**❌ Problem:**
```python
# No tests written
```

**✅ Solution:**
```python
def test_new_template():
    """Test new template matches expected queries"""
    # ... test implementation
```

---

## Best Practices Summary

1. **Pattern Design:**
   - Use word boundaries (`\b`)
   - Handle variations (plural/singular, synonyms)
   - Extract entities with named groups
   - Test with real user queries

2. **Query Optimization:**
   - Use Django ORM (not raw SQL)
   - Add `select_related()` for foreign keys
   - Add `prefetch_related()` for many-to-many
   - Limit result sets (`.[:30]`)
   - Add appropriate indexes

3. **Entity Extraction:**
   - Mark required vs optional clearly
   - Use appropriate resolvers
   - Handle extraction failures
   - Test extraction accuracy

4. **Priority Assignment:**
   - 10: Critical (exact matches, high-value)
   - 8-9: Common (frequent)
   - 6-7: Specialized (specific)
   - 4-5: Edge cases (rare)
   - 1-3: Fallback (ambiguous)

5. **Testing:**
   - Write unit tests for patterns
   - Test entity extraction
   - Verify query generation
   - Test with real data
   - Check edge cases

6. **Documentation:**
   - Clear descriptions
   - Multiple examples
   - Relevant tags
   - Note edge cases
   - Update guides

---

## Resources

**Code References:**
- Base classes: `src/common/ai_services/chat/query_templates/base.py`
- Entity extractor: `src/common/ai_services/chat/entity_extractor.py`
- Entity resolvers: `src/common/ai_services/chat/entity_resolvers.py`
- Template registry: `src/common/ai_services/chat/query_templates/__init__.py`

**Documentation:**
- Final report: `docs/ai/queries/QUERY_TEMPLATE_EXPANSION_FINAL_REPORT.md`
- Usage guide: `docs/ai/queries/USAGE_GUIDE.md`
- Deployment: `docs/ai/queries/DEPLOYMENT_CHECKLIST.md`

**Testing:**
- Test examples: `src/common/tests/test_*templates.py`
- Entity tests: `src/common/tests/test_entity_extractor.py`

---

**Guide Version:** 1.0
**Last Updated:** 2025-10-06
**Maintainer:** Development Team

---

**END OF AUTHORING GUIDE**
