# Query Template Examples

This directory contains real-world examples of query templates and their usage patterns.

## Example Categories

### 1. Common User Queries
Everyday queries staff members ask:
- **[common_queries.md](common_queries.md)** - Most frequently used queries
- **[data_queries.md](data_queries.md)** - Data retrieval and counting
- **[search_queries.md](search_queries.md)** - Search and filter operations

### 2. Domain-Specific Examples
Examples by OBCMS module:
- **[communities_examples.md](communities_examples.md)** - OBC community queries
- **[mana_examples.md](mana_examples.md)** - MANA workshop and assessment queries
- **[coordination_examples.md](coordination_examples.md)** - Stakeholder coordination queries
- **[policies_examples.md](policies_examples.md)** - Policy recommendation queries
- **[projects_examples.md](projects_examples.md)** - Project Central queries

### 3. Advanced Query Patterns
Complex multi-criteria queries:
- **[cross_domain_examples.md](cross_domain_examples.md)** - Queries spanning multiple modules
- **[aggregate_examples.md](aggregate_examples.md)** - Statistical and aggregation queries
- **[temporal_examples.md](temporal_examples.md)** - Time-based and trend queries

### 4. Use Case Scenarios
Complete workflows with multiple queries:
- **[mana_facilitator_workflow.md](mana_facilitator_workflow.md)** - MANA workshop facilitation
- **[policy_analyst_workflow.md](policy_analyst_workflow.md)** - Policy development process
- **[coordination_officer_workflow.md](coordination_officer_workflow.md)** - Partnership management

---

## Example Template Format

Each example file follows this structure:

```markdown
# {Category} Query Examples

## Example 1: {Query Title}

**User Query**: "How many communities in Region IX?"

**Matched Template**: `count_communities_by_location`

**Extracted Entities**:
- location: {'type': 'region', 'value': 'Region IX', 'confidence': 0.95}

**Generated Query**:
OBCCommunity.objects.filter(
    barangay__municipality__province__region__name__icontains='Region IX'
).count()

**Result**: 42 communities

**Response Format**:
{
    'type': 'count',
    'data': {'count': 42},
    'html': '<div class="result-number">42</div><div class="result-context">communities in Region IX</div>'
}
```

---

## Quick Reference: Most Common Queries

### Communities Module

**Count queries**:
- "How many communities?" → `count_total_communities`
- "How many communities in Region IX?" → `count_communities_by_location`
- "How many Maranao communities?" → `count_communities_by_ethnicity`

**List queries**:
- "Show all communities" → `list_all_communities`
- "Show communities in Zamboanga" → `list_communities_by_location`
- "List communities with fishing livelihood" → `list_communities_by_livelihood`

### MANA Module

**Count queries**:
- "How many workshops this month?" → `count_workshops_by_date_range`
- "Total completed assessments" → `count_completed_assessments`

**List queries**:
- "Show pending workshops" → `list_workshops_by_status`
- "List workshops in Region IX" → `list_workshops_by_location`

### Coordination Module

**Count queries**:
- "How many active partnerships?" → `count_partnerships_by_status`
- "Count organizations by type" → `count_organizations_by_type`

**List queries**:
- "Show all meetings this week" → `list_meetings_by_date_range`
- "List NGO partners" → `list_organizations_by_type`

---

## Adding New Examples

When adding examples to this directory:

1. ✅ Use real-world user queries
2. ✅ Show complete flow (query → template → result)
3. ✅ Include entity extraction details
4. ✅ Show generated Django ORM query
5. ✅ Provide actual result sample
6. ✅ Include response formatting

**Template**:
```markdown
## Example N: {Descriptive Title}

**User Query**: "{Natural language query}"

**Matched Template**: `template_id`

**Extracted Entities**:
- entity1: {details}
- entity2: {details}

**Generated Query**:
{Django ORM query string}

**Result**: {Sample result}

**Response Format**:
{JSON or HTML response}
```

---

**Last Updated**: October 6, 2025
