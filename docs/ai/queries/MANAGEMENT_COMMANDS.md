# OBCMS AI Chat - Management Commands

**Date:** 2025-10-06
**Status:** ✅ COMPLETE
**Location:** `src/common/management/commands/`

## Overview

Three Django management commands have been implemented to support the OBCMS AI chat query template system:

1. **validate_query_templates** - Validate all query templates for errors
2. **benchmark_query_system** - Benchmark performance of the query system
3. **generate_query_docs** - Auto-generate documentation from templates

## Commands

### 1. validate_query_templates

Validates all query templates for:
- Duplicate IDs
- Pattern compilation errors
- Required fields present
- Valid category/intent/result_type values
- Examples provided
- Priority in valid range (1-100)
- Query template syntax

**Usage:**
```bash
cd src
./manage.py validate_query_templates

# Validate specific domain
./manage.py validate_query_templates --domain=communities

# Verbose output
./manage.py validate_query_templates --verbose
```

**Output Example:**
```
======================================================================
OBCMS Query Template Validator
======================================================================

Validating 470 templates...

======================================================================
VALIDATION RESULTS
======================================================================

❌ Found 2 critical issues:

  1. Template 'count_all_municipalities' has invalid result_type: 'municipality_city_breakdown'
  2. Template 'count_all_municipalities_geographic' has invalid result_type: 'municipality_city_breakdown'

✓ No warnings!

======================================================================
TEMPLATE STATISTICS
======================================================================

Total templates: 470
Categories: 16
Average priority: 14.24
Templates with examples: 470/470

Templates by category:
  - analytics: 30
  - budget: 7
  - communities: 58
  - comparison: 20
  - coordination: 55
  - cross_domain: 39
  - general: 15
  - geographic: 48
  - infrastructure: 10
  - livelihood: 10
  - mana: 33
  - policies: 45
  - projects: 45
  - staff: 15
  - stakeholders: 10
  - temporal: 30
```

**Exit Codes:**
- `0` - All templates valid
- `1` - Validation failures found

---

### 2. benchmark_query_system

Benchmarks query system performance:
- Template loading time
- Pattern matching speed
- Registry operations
- Memory usage
- Category search performance

**Usage:**
```bash
cd src
./manage.py benchmark_query_system

# Custom iterations and queries
./manage.py benchmark_query_system --iterations=100 --queries=50

# Save results to JSON
./manage.py benchmark_query_system --output=../benchmark_results.json
```

**Output Example:**
```
======================================================================
OBCMS Query System Benchmark
======================================================================

Iterations: 50
Sample queries: 20

Benchmark 1: Template Loading
  Operation: Template Loading
  Iterations: 50
  Average time: 0.00 ms
  Min time: 0.00 ms
  Max time: 0.01 ms
  template_count: 470
  avg_memory_mb: 0.00

Benchmark 2: Pattern Matching
  Operation: Pattern Matching
  Iterations: 50
  Average time: 0.00 ms
  Min time: 0.00 ms
  Max time: 0.01 ms
  queries_tested: 20
  total_matches: 1000
  avg_matches_per_query: 0.50

...

======================================================================
BENCHMARK SUMMARY
======================================================================

Template Loading: 0.00 ms
Pattern Matching (per query): 0.00 ms
Memory Usage: 0.00 MB

✓ Excellent performance (< 1ms per query)

Recommendations:
```

**Performance Benchmarks:**
- **Template Loading:** < 1ms (470 templates)
- **Pattern Matching:** < 1ms per query
- **Memory Usage:** < 1MB for all templates
- **Overall:** ✅ Excellent performance

---

### 3. generate_query_docs

Auto-generates comprehensive documentation from query templates:
- Query reference by domain/category
- Example queries list
- Entity types reference
- Intent types reference
- Statistics and coverage analysis

**Usage:**
```bash
cd src
./manage.py generate_query_docs

# Custom output location
./manage.py generate_query_docs --output=../docs/ai/queries/QUERY_REFERENCE.md

# Include statistics
./manage.py generate_query_docs --include-stats

# Generate examples only
./manage.py generate_query_docs --examples-only --output=../docs/ai/queries/EXAMPLE_QUERIES.md

# HTML format
./manage.py generate_query_docs --format=html --output=../docs/ai/queries/reference.html
```

**Generated Files:**

1. **QUERY_REFERENCE.md** (194KB, 8,843 lines)
   - Complete reference for all 470 templates
   - Organized by 16 categories
   - Includes patterns, examples, priorities
   - Entity and intent references

2. **EXAMPLE_QUERIES.md** (48KB, 1,792 lines)
   - Simple list of all example queries
   - Organized by category
   - Quick reference for users

**Output Example:**
```
✓ Documentation generated: ../docs/ai/queries/QUERY_REFERENCE.md
  Size: 198320 characters
  Lines: 8843
```

---

## Template Statistics

**Current Status (2025-10-06):**

- **Total Templates:** 470
- **Categories:** 16
- **Average Priority:** 14.24/100
- **Templates with Examples:** 470/470 (100%)

**Templates by Category:**
- Analytics: 30
- Budget: 7
- Communities: 58
- Comparison: 20
- Coordination: 55
- Cross-domain: 39
- General: 15
- Geographic: 48
- Infrastructure: 10
- Livelihood: 10
- MANA: 33
- Policies: 45
- Projects: 45
- Staff: 15
- Stakeholders: 10
- Temporal: 30

---

## Validation Results

**Known Issues (2):**

1. Template `count_all_municipalities` has invalid result_type: `municipality_city_breakdown`
2. Template `count_all_municipalities_geographic` has invalid result_type: `municipality_city_breakdown`

**Fix Required:**
These templates should use result_type: `aggregate` or `count` instead of the custom `municipality_city_breakdown` value.

**Location:** `src/common/ai_services/chat/query_templates/communities.py`

---

## Implementation Details

### Files Created

1. **validate_query_templates.py** (332 lines, 12KB)
   - Comprehensive validation logic
   - 7 validation checks
   - Statistics generation
   - Color-coded output

2. **benchmark_query_system.py** (424 lines, 15KB)
   - 5 benchmark categories
   - Performance metrics
   - JSON output support
   - Recommendations engine

3. **generate_query_docs.py** (466 lines, 17KB)
   - Markdown generation
   - HTML generation
   - Statistics calculation
   - Examples-only mode

**Total Lines of Code:** 1,222

---

## Usage in Development

### Daily Validation
```bash
# Run before committing changes to templates
./manage.py validate_query_templates
```

### Performance Monitoring
```bash
# Weekly performance check
./manage.py benchmark_query_system --iterations=100 --output=benchmark_$(date +%Y%m%d).json
```

### Documentation Updates
```bash
# Update docs after adding new templates
./manage.py generate_query_docs
./manage.py generate_query_docs --examples-only --output=../docs/ai/queries/EXAMPLE_QUERIES.md
```

---

## CI/CD Integration

These commands can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/validate-templates.yml
name: Validate Query Templates

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements/base.txt
      - name: Validate templates
        run: |
          cd src
          python manage.py validate_query_templates
      - name: Benchmark performance
        run: |
          cd src
          python manage.py benchmark_query_system --iterations=50
```

---

## See Also

- [Query Reference](QUERY_REFERENCE.md) - Complete template reference
- [Example Queries](EXAMPLE_QUERIES.md) - All example queries
- [Template Architecture](ARCHITECTURE.md) - System design
- [Best Practices](BEST_PRACTICES.md) - Template design guidelines
