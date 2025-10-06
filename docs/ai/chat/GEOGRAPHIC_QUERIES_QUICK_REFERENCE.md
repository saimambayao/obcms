# Geographic Queries - Quick Reference Guide

**Module:** `src/common/ai_services/chat/query_templates/geographic.py`
**Category:** `geographic`
**Total Templates:** 50

---

## Quick Query Examples

### Regions (12 templates)

| Query Type | Example | Template ID |
|-----------|---------|-------------|
| Count | "How many regions?" | `count_all_regions` |
| List | "Show me all regions" | `list_all_regions` |
| Filter | "Regions with OBC" | `count_regions_with_obc` |
| Detail | "Show me Region IX" | `region_by_name` |
| Analytics | "Population by region" | `region_demographics` |

### Provinces (12 templates) ⭐ MOST REQUESTED

| Query Type | Example | Template ID |
|-----------|---------|-------------|
| Count | "How many provinces?" | `count_all_provinces` |
| **List** | **"Show me the list of provinces"** | `list_all_provinces` ⭐ |
| Filter | "Provinces in Region IX" | `list_provinces_by_region` |
| Detail | "Zamboanga del Sur details" | `province_by_name` |
| Analytics | "Population by province" | `province_demographics` |

### Municipalities (12 templates)

| Query Type | Example | Template ID |
|-----------|---------|-------------|
| Count | "How many municipalities?" | `count_all_municipalities` |
| List | "Show me all municipalities" | `list_all_municipalities` |
| Filter | "Municipalities in Cotabato" | `list_municipalities_by_province` |
| Detail | "Pagadian City details" | `municipality_by_name` |
| Analytics | "Population by municipality" | `municipality_demographics` |

### Barangays (8 templates)

| Query Type | Example | Template ID |
|-----------|---------|-------------|
| Count | "How many barangays?" | `count_all_barangays` |
| List | "Show me all barangays" | `list_all_barangays` |
| Filter | "Barangays in Cotabato City" | `list_barangays_by_municipality` |
| Detail | "Barangay Poblacion details" | `barangay_by_name` |
| Analytics | "Population by barangay" | `barangay_demographics` |

### Cross-Level (6 templates)

| Query Type | Example | Template ID |
|-----------|---------|-------------|
| Hierarchy | "Show administrative hierarchy" | `administrative_hierarchy` |
| Gaps | "Show coverage gaps" | `geographic_coverage_gaps` |
| Summary | "Geographic summary" | `geographic_rollup_summary` |
| Compare | "Compare Region IX vs Region X" | `geographic_comparison` |
| Export | "Export boundaries" | `administrative_boundaries_export` |

---

## Common Query Patterns

### "Show me..." Queries
```
✅ "Show me all regions"
✅ "Show me all provinces"
✅ "Show me all municipalities"
✅ "Show me all barangays"
✅ "Show me Region IX"
✅ "Show me Cotabato province"
```

### "How many..." Queries
```
✅ "How many regions?"
✅ "How many provinces?"
✅ "How many municipalities?"
✅ "How many barangays?"
✅ "How many provinces in Region IX?"
✅ "How many municipalities in Cotabato?"
```

### "List..." Queries
```
✅ "List all regions"
✅ "List all provinces"
✅ "List all municipalities"
✅ "List all barangays"
✅ "List provinces in Region XII"
✅ "List municipalities in Sultan Kudarat"
```

### Population Queries
```
✅ "Show population by region"
✅ "Show population by province"
✅ "Show population by municipality"
✅ "Show population by barangay"
✅ "Rank provinces by OBC population"
```

### Coverage Queries
```
✅ "Show assessment coverage by region"
✅ "Show MANA coverage by province"
✅ "Show geographic coverage gaps"
✅ "Which regions have OBC?"
✅ "Which barangays have OBC?"
```

---

## Template Priority System

| Priority | Type | Use Case |
|----------|------|----------|
| 10 | List/Detail | Direct user requests (highest priority) |
| 9 | Filtered Count | Specific count queries |
| 8 | Simple Count | General count queries |
| 7 | Analytics | Population, demographics, coverage |
| 6 | Export/Advanced | Specialized queries |

---

## Result Types

| Result Type | Description | Example Query |
|------------|-------------|---------------|
| `count` | Single integer | "How many provinces?" → 25 |
| `list` | Array of objects | "List provinces" → [Province(...), ...] |
| `single` | Single object | "Show Region IX" → Region(...) |
| `aggregate` | Computed stats | "Population by region" → [{region: ..., pop: ...}] |

---

## Integration Examples

### Python Usage

```python
from common.ai_services.chat.query_templates import get_template_registry

registry = get_template_registry()

# Search for templates
matches = registry.search_templates("Show me all provinces")

# Get best match
if matches:
    template = matches[0]
    print(f"Template: {template.id}")
    print(f"Query: {template.query_template}")
    print(f"Result Type: {template.result_type}")
```

### Chat View Usage

```python
# In your chat view
def handle_geographic_query(user_query):
    registry = get_template_registry()
    matches = registry.search_templates(user_query, category='geographic')

    if matches:
        template = matches[0]
        result = execute_template_query(template)
        return format_geographic_response(result, template.result_type)

    return "No matching geographic template found"
```

---

## Testing

### Run All Geographic Tests
```bash
cd src
pytest common/tests/test_geographic_templates.py -v
```

### Run Specific Test
```bash
pytest common/tests/test_geographic_templates.py::TestGeographicTemplates::test_list_provinces_critical -v
```

### Test Coverage
```bash
pytest common/tests/test_geographic_templates.py --cov=common.ai_services.chat.query_templates.geographic
```

---

## Troubleshooting

### Issue: Template not matching

**Check pattern:**
```python
import re
pattern = r'\b(show|list)\s+provinces?\b'
query = "Show me all provinces"
match = re.search(pattern, query, re.IGNORECASE)
print(match)  # Should return match object
```

**Check registration:**
```python
from common.ai_services.chat.query_templates import get_template_registry
registry = get_template_registry()
templates = registry.get_templates_by_category('geographic')
print(f"Registered: {len(templates)} templates")
```

### Issue: Wrong template selected

**Check priority:**
Templates are sorted by priority (10 = highest). If wrong template is selected, check if both match and adjust priorities.

### Issue: Query execution fails

**Check ORM query:**
```python
from common.models import Province

# Test the query directly
Province.objects.all().order_by("region__name", "name")
```

---

## API Reference

### QueryTemplate Structure

```python
QueryTemplate(
    id='template_id',              # Unique identifier
    category='geographic',          # Template category
    pattern=r'regex_pattern',      # Matching pattern
    query_template='ORM_query',    # Django ORM query
    required_entities=[],          # Required entities
    optional_entities=[],          # Optional entities
    examples=['query1', 'query2'], # Example queries
    priority=10,                   # Priority (1-10)
    description='Description',     # Human-readable description
    result_type='list',            # count, list, single, aggregate
    tags=['tag1', 'tag2']          # Searchable tags
)
```

---

## Performance Notes

- **Template matching:** < 5ms
- **Simple queries:** < 50ms
- **Aggregate queries:** 50-200ms
- **Cross-level queries:** 100-500ms

---

## Related Documentation

- **Implementation:** `WORKSTREAM_4_GEOGRAPHIC_TEMPLATES_COMPLETE.md`
- **Chat System:** `docs/ai/chat/CHAT_INTEGRATION_COMPLETE.md`
- **Models:** `src/common/models.py` (Region, Province, Municipality, Barangay)
- **Tests:** `src/common/tests/test_geographic_templates.py`

---

**Last Updated:** 2025-10-06
**Version:** 1.0.0
**Status:** Production Ready ✅
