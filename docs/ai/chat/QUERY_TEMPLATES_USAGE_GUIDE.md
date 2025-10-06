# Query Templates Usage Guide

**Quick reference for using the OBCMS Query Templates Infrastructure**

## Table of Contents
1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Creating Custom Templates](#creating-custom-templates)
4. [Advanced Features](#advanced-features)
5. [Integration Examples](#integration-examples)

---

## Quick Start

### Import and Initialize

```python
from common.ai_services.chat.query_templates import (
    QueryTemplate,
    get_template_registry,
    get_template_matcher
)

# Get singleton instances
registry = get_template_registry()
matcher = get_template_matcher()
```

### Basic Template Matching

```python
# Match a query and generate Django ORM code
result = matcher.match_and_generate(
    query='how many communities in Region IX',
    entities={'location': {'type': 'region', 'value': 'Region IX'}},
    category='communities'
)

if result['success']:
    print(f"Generated query: {result['query']}")
    print(f"Match score: {result['score']:.2f}")
    print(f"Template ID: {result['template'].id}")
else:
    print(f"Error: {result['error']}")
    print(f"Missing entities: {result['missing_entities']}")
```

---

## Basic Usage

### 1. Matching Queries to Templates

```python
# Example: Count communities in a location
query = "how many communities in Zamboanga"
entities = {
    'location': {
        'type': 'province',
        'value': 'Zamboanga del Norte'
    }
}

result = matcher.match_and_generate(
    query=query,
    entities=entities,
    category='communities'
)

# Output:
# {
#     'success': True,
#     'template': QueryTemplate(...),
#     'query': "OBCCommunity.objects.filter(barangay__municipality__province__name__icontains='Zamboanga del Norte').count()",
#     'score': 0.95,
#     'error': None,
#     'missing_entities': []
# }
```

### 2. Finding Templates by Category

```python
# Get all community-related templates
community_templates = registry.get_templates_by_category('communities')

print(f"Found {len(community_templates)} community templates")

for template in community_templates[:5]:
    print(f"- {template.id}: {template.description}")
    print(f"  Priority: {template.priority}")
    print(f"  Examples: {template.examples[0]}")
```

### 3. Searching Templates

```python
# Search for matching templates
matches = registry.search_templates(
    query='show workshops in davao',
    category='mana',
    min_priority=50
)

print(f"Found {len(matches)} matching templates")
```

### 4. Template Autocomplete

```python
# Get suggestions for partial query
suggestions = matcher.get_template_suggestions(
    partial_query='how many',
    category='communities',
    max_suggestions=5
)

for suggestion in suggestions:
    print(f"- {suggestion['example']}")
    print(f"  Category: {suggestion['category']}")
    print(f"  Priority: {suggestion['priority']}")
```

---

## Creating Custom Templates

### Simple Template

```python
# Create a simple count template
template = QueryTemplate(
    id='count_farming_communities',
    category='communities',
    pattern=r'\b(how many|count|total)\s+farming\s+communities\b',
    query_template='OBCCommunity.objects.filter(primary_livelihood__icontains="farming").count()',
    required_entities=[],
    optional_entities=['location'],
    examples=[
        'How many farming communities?',
        'Count farming communities',
        'Total farming communities'
    ],
    priority=75,
    description='Count communities with farming livelihood'
)

# Register the template
registry.register(template)
```

### Template with Entity Substitution

```python
# Template with location and date filters
template = QueryTemplate(
    id='workshops_by_location_date',
    category='mana',
    pattern=r'workshops?\s+in\s+(.+)\s+(?:from|since|between)',
    query_template=(
        'WorkshopActivity.objects.filter('
        '{location_filter}, {date_range_filter}'
        ').order_by("-date_conducted")'
    ),
    required_entities=['location', 'date_range'],
    optional_entities=[],
    examples=[
        'workshops in Zamboanga from January to March',
        'workshop in Region IX since last month'
    ],
    priority=85,
    description='List workshops by location and date range'
)

registry.register(template)
```

### Template with Multiple Patterns

```python
# Template matching multiple query variations
template = QueryTemplate(
    id='active_partnerships_location',
    category='coordination',
    pattern=r'(?:show|list|display|get)\s+(?:active\s+)?partnerships?\s+(?:in|at|from)\s+(.+)',
    query_template='Partnership.objects.filter({location_filter}, status="active")',
    required_entities=['location'],
    optional_entities=[],
    examples=[
        'show active partnerships in Davao',
        'list partnerships in Region IX',
        'display partnerships from Zamboanga'
    ],
    priority=80,
    description='List active partnerships in a location'
)

registry.register(template)
```

### Batch Registration

```python
# Register multiple templates at once
templates = [
    QueryTemplate(
        id='template1',
        category='policies',
        pattern=r'pattern1',
        query_template='Model1.objects.all()',
        required_entities=[]
    ),
    QueryTemplate(
        id='template2',
        category='policies',
        pattern=r'pattern2',
        query_template='Model2.objects.filter(status="active")',
        required_entities=[]
    ),
]

registry.register_many(templates)
```

---

## Advanced Features

### 1. Custom Entity Substitution

```python
# Substitute entities into a template manually
template_string = 'OBCCommunity.objects.filter({location_filter}, {status_filter})'

entities = {
    'location': {'type': 'region', 'value': 'Region IX'},
    'status': {'value': 'active'}
}

query = matcher.substitute_entities(template_string, entities)
print(query)
# Output: "OBCCommunity.objects.filter(barangay__municipality__province__region__name__icontains='Region IX', status__iexact='active')"
```

### 2. Template Validation

```python
# Check if template can execute with given entities
template = registry.get_template('count_communities_location')

entities_complete = {
    'location': {'type': 'region', 'value': 'Region IX'}
}

validation = matcher.validate_template(template, entities_complete)
print(f"Valid: {validation['is_valid']}")
print(f"Missing: {validation['missing_entities']}")

# With missing entities
entities_incomplete = {}

validation = matcher.validate_template(template, entities_incomplete)
print(f"Valid: {validation['is_valid']}")
print(f"Missing: {validation['missing_entities']}")
# Output: Valid: False, Missing: ['location']
```

### 3. Template Ranking

```python
# Find and rank multiple matching templates
query = 'how many communities'
entities = {'location': {'type': 'region', 'value': 'Region IX'}}

# Find matches
matches = matcher.find_matching_templates(
    query=query,
    entities=entities,
    category='communities'
)

# Rank by match quality
ranked = matcher.rank_templates(
    templates=matches,
    query=query,
    entities=entities
)

# Display ranked results
for i, match in enumerate(ranked[:3], 1):
    print(f"{i}. {match['template'].id}")
    print(f"   Score: {match['score']:.2f}")
    print(f"   Priority: {match['template'].priority}")
```

### 4. Registry Statistics

```python
# Get registry statistics
stats = registry.get_stats()

print(f"Total templates: {stats['total_templates']}")
print(f"Average priority: {stats['avg_priority']:.1f}")
print("\nTemplates by category:")
for category, count in stats['categories'].items():
    print(f"  {category}: {count}")

print("\nTemplates by tag:")
for tag, count in stats['tags'].items():
    print(f"  {tag}: {count}")
```

### 5. Using Helper Functions

```python
from common.ai_services.chat.query_templates.base import (
    build_location_filter,
    build_status_filter,
    build_date_range_filter
)

# Build location filter
entities = {'location': {'type': 'province', 'value': 'Zamboanga del Norte'}}
loc_filter = build_location_filter(entities)
print(loc_filter)
# Output: "province__name__icontains='Zamboanga del Norte'"

# Build status filter
entities = {'status': 'active'}
status_filter = build_status_filter(entities)
print(status_filter)
# Output: "status='active'"

# Build date range filter
from datetime import datetime
entities = {
    'date_start': datetime(2025, 1, 1),
    'date_end': datetime(2025, 12, 31)
}
date_filter = build_date_range_filter(entities, 'created_at')
print(date_filter)
# Output: "created_at__gte='2025-01-01', created_at__lte='2025-12-31'"
```

---

## Integration Examples

### Integration with Chat Engine

```python
from common.ai_services.chat.query_templates import get_template_matcher
from common.ai_services.chat.entity_extractor import EntityExtractor
from common.ai_services.chat.intent_classifier import IntentClassifier

def process_query(user_query: str):
    """Complete query processing pipeline"""

    # Step 1: Classify intent
    classifier = IntentClassifier()
    intent = classifier.classify(user_query)

    # Step 2: Extract entities
    extractor = EntityExtractor()
    entities = extractor.extract(user_query)

    # Step 3: Match to template and generate query
    matcher = get_template_matcher()
    result = matcher.match_and_generate(
        query=user_query,
        entities=entities,
        category=intent.get('category', 'general')
    )

    if result['success']:
        # Execute the generated query
        query_string = result['query']
        # Note: In production, use proper query execution with security
        return {
            'status': 'success',
            'query': query_string,
            'template_id': result['template'].id,
            'score': result['score']
        }
    else:
        return {
            'status': 'error',
            'error': result['error'],
            'missing_entities': result['missing_entities']
        }

# Example usage
response = process_query('how many communities in Region IX')
print(response)
```

### Adding Templates Dynamically

```python
# Create template collection for new module
NEW_MODULE_TEMPLATES = []

def register_custom_template(pattern, query_template, **kwargs):
    """Helper to register custom templates"""
    template = QueryTemplate(
        pattern=pattern,
        query_template=query_template,
        **kwargs
    )
    registry = get_template_registry()
    registry.register(template)
    return template

# Register custom templates
register_custom_template(
    id='custom_query_1',
    category='custom',
    pattern=r'custom pattern here',
    query_template='CustomModel.objects.filter({location_filter})',
    required_entities=['location'],
    examples=['example query'],
    priority=70
)
```

### Error Handling

```python
def safe_query_generation(query, entities, category=None):
    """Safely generate query with error handling"""
    try:
        matcher = get_template_matcher()
        result = matcher.match_and_generate(
            query=query,
            entities=entities,
            category=category
        )

        if not result['success']:
            # Handle specific error cases
            if 'No matching templates' in result.get('error', ''):
                return {
                    'error': 'NO_MATCH',
                    'message': 'Could not find a matching template for your query',
                    'suggestion': 'Try rephrasing your question'
                }
            elif result.get('missing_entities'):
                return {
                    'error': 'MISSING_ENTITIES',
                    'message': f"Missing required information: {', '.join(result['missing_entities'])}",
                    'missing': result['missing_entities']
                }

        return result

    except Exception as e:
        return {
            'error': 'INTERNAL_ERROR',
            'message': f'An error occurred: {str(e)}'
        }

# Usage
result = safe_query_generation(
    'how many communities',
    {},  # No entities
    'communities'
)
```

---

## Best Practices

### 1. Template Design
- Use specific patterns (high priority) for exact matches
- Use broader patterns (low priority) for fallback
- Include multiple example queries
- Set priority based on specificity (90-100: exact, 70-89: common, 40-69: general, 1-39: fallback)

### 2. Entity Handling
- Always validate required entities before execution
- Provide meaningful error messages for missing entities
- Use optional entities for query refinement

### 3. Performance
- Keep pattern complexity reasonable (avoid excessive backtracking)
- Use category filtering to reduce search space
- Cache frequently used templates

### 4. Testing
- Test templates with various query phrasings
- Test edge cases (empty strings, special characters, Unicode)
- Verify entity substitution correctness

### 5. Maintenance
- Organize templates by category
- Document pattern purpose and examples
- Monitor template usage and optimize based on patterns

---

## Common Patterns

### Location-based Queries
```python
pattern=r'(?:in|at|from)\s+(?P<location>.+)',
query_template='Model.objects.filter({location_filter})',
required_entities=['location']
```

### Count Queries
```python
pattern=r'(?:how many|count|total|number of)\s+(.+)',
query_template='Model.objects.filter(...).count()',
result_type='count'
```

### List Queries
```python
pattern=r'(?:show|list|display|get)\s+(.+)',
query_template='Model.objects.filter(...).order_by("-created_at")',
result_type='list'
```

### Date Range Queries
```python
pattern=r'(?:from|since|between)\s+(.+)',
query_template='Model.objects.filter({date_range_filter})',
required_entities=['date_range']
```

---

## Troubleshooting

### Template Not Matching

**Problem:** Query doesn't match any template

**Solutions:**
1. Check pattern regex is correct (use regex tester)
2. Verify category is correct
3. Check entity requirements are met
4. Lower priority threshold in search

### Low Match Score

**Problem:** Template matches but score is low

**Solutions:**
1. Increase template priority
2. Make pattern more specific
3. Ensure all required entities are present
4. Add more example queries

### Missing Entities

**Problem:** Template requires entities not extracted

**Solutions:**
1. Improve entity extraction
2. Make entities optional if not critical
3. Provide entity input form to user
4. Use fallback template with fewer requirements

---

## Resources

- **API Reference:** `/docs/ai/chat/QUERY_TEMPLATES_INFRASTRUCTURE_COMPLETE.md`
- **Test Suite:** `/src/common/tests/test_template_matcher.py`
- **Example Templates:** `/src/common/ai_services/chat/query_templates/`
- **Architecture:** `/docs/ai/fallback/ARCHITECTURE.md`

---

**Last Updated:** October 6, 2025
**Version:** 1.0.0
