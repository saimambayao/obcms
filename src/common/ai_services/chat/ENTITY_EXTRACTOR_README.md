# Entity Extractor - OBCMS Chat System

## Overview

The Entity Extractor service extracts structured entities from natural language queries **without using AI**. It uses pattern matching, fuzzy matching, and database validation to achieve high accuracy and performance.

## Performance

- **Average extraction time:** 4.75ms
- **Target:** <20ms
- **Status:** ✅ **4x faster than target**

## Supported Entity Types

### 1. Locations
- **Regions:** IX (Zamboanga), X (Northern Mindanao), XI (Davao), XII (SOCCSKSARGEN)
- **Provinces:** Sultan Kudarat, Maguindanao, South Cotabato, etc.
- **Municipalities:** Database-backed fuzzy matching
- **Barangays:** Database-backed fuzzy matching

**Examples:**
```python
"communities in region ix" → Region IX
"zamboanga peninsula" → Region IX
"sultan kudarat" → Sultan Kudarat (province)
```

### 2. Ethnolinguistic Groups
- Meranaw (Maranao, Marano)
- Maguindanaon (Maguindanao)
- Tausug (Tausog)
- Sama (Sama-Bajau, Badjao)
- Yakan, Iranun, Kalagan, Kolibugan, Sangil, Molbog, etc.

**Examples:**
```python
"maranao communities" → Meranaw
"tausug fishing" → Tausug
"badjao people" → Sama
```

### 3. Livelihoods
- Farming (farmer, agriculture, crops)
- Fishing (fisher, fisherfolk, aquaculture)
- Trading (trader, merchant, sari-sari)
- Weaving, Livestock, Carpentry, etc.

**Examples:**
```python
"fishing communities" → fishing
"farmers in region ix" → farming
"trader associations" → trading
```

### 4. Date Ranges

**Relative:**
- "last 30 days", "last 6 months", "last year"
- "this year", "current year"
- "recent", "latest"

**Absolute:**
- "2024", "2023"
- "january 2024", "jan 2024"
- "from jan to mar", "january to march"

**Examples:**
```python
"last 6 months" → start: 2024-04-06, end: 2025-10-06
"this year" → start: 2025-01-01, end: now
"2024" → start: 2024-01-01, end: 2024-12-31
```

### 5. Status Values
- Ongoing (in progress, active, running)
- Completed (done, finished, closed)
- Draft, Pending, Approved, Rejected, Cancelled, Suspended

**Examples:**
```python
"ongoing projects" → ongoing
"completed assessments" → completed
"in progress tasks" → ongoing
```

### 6. Numbers
- **Cardinal:** 5, 10, 25, 100
- **Ordinal:** first, 2nd, third, 5th
- **Written:** five, ten, twenty

**Examples:**
```python
"top 5 communities" → [5]
"first workshop" → [1]
"ten families" → [10]
```

## Usage

### Basic Usage

```python
from common.ai_services.chat.entity_extractor import EntityExtractor

# Initialize extractor
extractor = EntityExtractor()

# Extract entities from query
query = "maranao fishing communities in zamboanga last 6 months"
entities = extractor.extract_entities(query)

print(entities)
# {
#     'ethnolinguistic_group': {'value': 'Meranaw', 'confidence': 0.90},
#     'livelihood': {'value': 'fishing', 'confidence': 0.95},
#     'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.85},
#     'date_range': {
#         'start': datetime(2024, 4, 6),
#         'end': datetime(2025, 10, 6),
#         'confidence': 1.0,
#         'range_type': 'relative'
#     }
# }
```

### Get Human-Readable Summary

```python
# Generate summary
summary = extractor.get_entity_summary(entities)
print(summary)
# "Found: Meranaw, fishing livelihood, Region IX (region), recent data"
```

### Validate Entities

```python
# Validate extracted entities
is_valid, issues = extractor.validate_entities(entities)
print(f"Valid: {is_valid}")
print(f"Issues: {issues}")
# Valid: True
# Issues: []
```

### Individual Resolvers

You can also use individual resolvers directly:

```python
from common.ai_services.chat.entity_resolvers import (
    LocationResolver,
    EthnicGroupResolver,
    LivelihoodResolver,
    DateRangeResolver,
    StatusResolver,
    NumberResolver,
)

# Location resolver
location_resolver = LocationResolver()
location = location_resolver.resolve("zamboanga peninsula")
# {'type': 'region', 'value': 'Region IX', 'confidence': 0.85}

# Date range resolver
date_resolver = DateRangeResolver()
date_range = date_resolver.resolve("last 30 days")
# {'start': datetime(...), 'end': datetime(...), 'range_type': 'relative'}
```

## Confidence Scores

All extracted entities include confidence scores (0.0 - 1.0):

- **1.0:** Exact match (e.g., "region ix" → Region IX)
- **0.95:** High confidence (e.g., "maranao" → Meranaw)
- **0.90:** Good match (e.g., "fisherman" → fishing)
- **0.85:** Fuzzy match (e.g., "zamboanga" → Region IX)
- **0.75:** Lower confidence (partial match)
- **<0.50:** Low confidence (may need clarification)

## Examples

### Example 1: Multi-Entity Query

```python
query = "top 10 maguindanao farming communities in sultan kudarat"
entities = extractor.extract_entities(query)

# Extracted:
# - numbers: [{'value': 10, 'type': 'cardinal', 'confidence': 1.0}]
# - ethnolinguistic_group: {'value': 'Maguindanaon', 'confidence': 0.90}
# - livelihood: {'value': 'farming', 'confidence': 0.95}
# - location: {'type': 'province', 'value': 'Sultan Kudarat', 'confidence': 0.92}
```

### Example 2: Status and Date Range

```python
query = "ongoing workshops in region xii this year"
entities = extractor.extract_entities(query)

# Extracted:
# - status: {'value': 'ongoing', 'confidence': 0.95}
# - location: {'type': 'region', 'value': 'Region XII', 'confidence': 0.95}
# - date_range: {'start': datetime(2025, 1, 1), 'end': datetime(2025, 10, 6), 'range_type': 'relative'}
```

### Example 3: Fuzzy Matching

```python
# Handles typos and variations
query = "marano fishermen zambanga"  # Note: typos!
entities = extractor.extract_entities(query)

# Still extracts correctly:
# - ethnolinguistic_group: {'value': 'Meranaw', 'confidence': 0.90}
# - livelihood: {'value': 'fishing', 'confidence': 0.90}
```

## Integration with Chat System

The Entity Extractor is designed to work with the OBCMS chat system:

1. **FAQ Handler** checks for pre-computed answers
2. **Entity Extractor** extracts structured entities from query
3. **Clarification Handler** detects if entities are missing/ambiguous
4. **Query Generator** uses entities to build database queries
5. **Response Formatter** formats results for user

## Performance Benchmarks

Tested on 8 diverse queries:

| Query Type | Avg Time | Entities | Status |
|------------|----------|----------|--------|
| Multi-entity | 1.06ms | 5 | ✅ |
| Complex | 15.17ms | 4 | ✅ |
| Status + Date | 1.17ms | 3 | ✅ |
| Fuzzy match | 11.99ms | 2 | ✅ |
| Date range | 6.30ms | 4 | ✅ |
| Province | 0.16ms | 2 | ✅ |
| Simple | 1.98ms | 2 | ✅ |
| Numbers | 0.12ms | 3 | ✅ |

**Overall Average:** 4.75ms (4x faster than 20ms target)

## Architecture

### EntityExtractor Class
- Main orchestrator for all entity extraction
- Delegates to specialized resolvers
- Provides validation and summary methods

### Resolver Classes
- **LocationResolver:** Geographic entities with database validation
- **EthnicGroupResolver:** Ethnolinguistic group variations
- **LivelihoodResolver:** Livelihood keyword mapping
- **DateRangeResolver:** Natural language date parsing
- **StatusResolver:** Workflow and task status
- **NumberResolver:** Cardinal, ordinal, written numbers

### Design Principles
1. **No AI dependency:** Pure pattern matching and fuzzy logic
2. **High performance:** Sub-20ms extraction target
3. **Database-backed:** Validates locations against actual data
4. **Confidence scoring:** All entities include reliability scores
5. **Extensible:** Easy to add new entity types and patterns

## Testing

Comprehensive test suite included in `src/common/tests/test_entity_extractor.py`:

- 56 test cases covering all entity types
- Performance tests (<20ms requirement)
- Fuzzy matching and typo handling
- Edge cases and error handling
- Integration tests with realistic queries

```bash
# Run tests
cd src
python -m pytest common/tests/test_entity_extractor.py -v
```

## Extending the Entity Extractor

### Adding New Ethnolinguistic Group

Edit `entity_resolvers.py`:

```python
ETHNIC_GROUP_VARIATIONS = {
    # ... existing ...
    'new_group': ['new group', 'variant 1', 'variant 2'],
}
```

### Adding New Livelihood

Edit `entity_resolvers.py`:

```python
LIVELIHOOD_KEYWORDS = {
    # ... existing ...
    'new_livelihood': ['keyword1', 'keyword2', 'keyword3'],
}
```

### Adding New Region

Edit `entity_resolvers.py`:

```python
REGION_PATTERNS = {
    # ... existing ...
    'XIII': {
        'names': ['region xiii', 'region 13', 'caraga'],
        'official_name': 'Region XIII',
        'code': 'XIII',
    },
}
```

## See Also

- [Chat System Architecture](../../../docs/ai/fallback/ARCHITECTURE.md)
- [Implementation Plan](../../../docs/ai/fallback/IMPLEMENTATION_PLAN.md)
- [Query Templates](query_templates.py) (to be implemented)
- [Clarification Handler](clarification.py) (to be implemented)

## License

Part of the OBCMS (Office for Other Bangsamoro Communities Management System)
