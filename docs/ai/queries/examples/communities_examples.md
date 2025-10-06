# Communities Module Query Examples

Real-world examples of query templates for OBC (Other Bangsamoro Communities) management.

**Total Templates**: 25 (current) → 65 (target)
**Query Types**: COUNT, LIST, GET, FIND, AGGREGATE
**Primary Entities**: location, ethnolinguistic_group, livelihood, status

---

## COUNT Queries (10 examples)

### Example 1: Total Communities

**User Query**: "How many communities are there?"

**Matched Template**: `count_total_communities`

**Pattern**: `\b(how many|total|count|number of)\s+(obc\s+)?communities\b`

**Extracted Entities**: None required

**Generated Query**:
```python
OBCCommunity.objects.count()
```

**Result**: 127 communities

**Response Format**:
```json
{
    "type": "count",
    "data": {"count": 127},
    "html": "<div class='result-number'>127</div><div class='result-context'>OBC communities in the system</div>"
}
```

**Template Priority**: 7/10 (HIGH)
**Estimated Latency**: 5ms
**Cache TTL**: 300s

---

### Example 2: Communities by Location (Region)

**User Query**: "How many communities in Region IX?"

**Matched Template**: `count_communities_by_location`

**Pattern**: `\b(how many|count|total)\s+(obc\s+)?communities\s+(in|at|within|from)\s+(?P<location>[\w\s]+)`

**Extracted Entities**:
- **location**:
  - type: `region`
  - value: `Region IX`
  - confidence: 0.95

**Generated Query**:
```python
OBCCommunity.objects.filter(
    barangay__municipality__province__region__name__icontains='Region IX'
).count()
```

**Result**: 42 communities

**Response Format**:
```json
{
    "type": "count",
    "data": {
        "count": 42,
        "location": "Region IX",
        "location_type": "region"
    },
    "html": "<div class='result-number'>42</div><div class='result-context'>communities in Region IX</div>"
}
```

**Template Priority**: 9/10 (CRITICAL)
**Estimated Latency**: 15ms
**Cache TTL**: 600s

---

### Example 3: Communities by Location (Province)

**User Query**: "Count communities in Zamboanga del Sur"

**Matched Template**: `count_communities_by_location`

**Pattern**: Same as Example 2

**Extracted Entities**:
- **location**:
  - type: `province`
  - value: `Zamboanga del Sur`
  - confidence: 0.92

**Generated Query**:
```python
OBCCommunity.objects.filter(
    barangay__municipality__province__name__icontains='Zamboanga del Sur'
).count()
```

**Result**: 18 communities

**Template Priority**: 9/10 (CRITICAL)
**Estimated Latency**: 12ms

---

### Example 4: Communities by Ethnolinguistic Group

**User Query**: "How many Maranao communities?"

**Matched Template**: `count_communities_by_ethnicity`

**Pattern**: `\b(how many|count|total)\s+(?P<ethnicity>\w+)\s+communities\b`

**Extracted Entities**:
- **ethnolinguistic_group**:
  - value: `Maranao`
  - confidence: 0.98

**Generated Query**:
```python
OBCCommunity.objects.filter(
    primary_ethnolinguistic_group__icontains='Maranao'
).count()
```

**Result**: 35 communities

**Response Format**:
```json
{
    "type": "count",
    "data": {
        "count": 35,
        "ethnolinguistic_group": "Maranao"
    },
    "html": "<div class='result-number'>35</div><div class='result-context'>Maranao communities</div>"
}
```

**Template Priority**: 8/10 (HIGH)
**Estimated Latency**: 10ms
**Cache TTL**: 600s

---

### Example 5: Communities by Livelihood

**User Query**: "How many communities with fishing livelihood?"

**Matched Template**: `count_communities_by_livelihood`

**Pattern**: `\b(how many|count|total)\s+communities\s+(with|having)\s+(?P<livelihood>[\w\s]+?)\s+(livelihood|as livelihood)`

**Extracted Entities**:
- **livelihood**:
  - value: `fishing`
  - confidence: 0.95

**Generated Query**:
```python
OBCCommunity.objects.filter(
    primary_livelihood__icontains='fishing'
).count()
```

**Result**: 28 communities

**Template Priority**: 8/10 (HIGH)
**Estimated Latency**: 12ms

---

### Example 6: Complex Filter (Ethnicity + Location)

**User Query**: "How many Maranao communities in Region IX?"

**Matched Template**: `count_communities_by_ethnicity_and_location`

**Pattern**: `\b(how many|count)\s+(?P<ethnicity>\w+)\s+communities\s+(in|at)\s+(?P<location>[\w\s]+)`

**Extracted Entities**:
- **ethnolinguistic_group**:
  - value: `Maranao`
  - confidence: 0.98
- **location**:
  - type: `region`
  - value: `Region IX`
  - confidence: 0.95

**Generated Query**:
```python
OBCCommunity.objects.filter(
    primary_ethnolinguistic_group__icontains='Maranao',
    barangay__municipality__province__region__name__icontains='Region IX'
).count()
```

**Result**: 15 communities

**Response Format**:
```json
{
    "type": "count",
    "data": {
        "count": 15,
        "ethnolinguistic_group": "Maranao",
        "location": "Region IX"
    },
    "html": "<div class='result-number'>15</div><div class='result-context'>Maranao communities in Region IX</div>"
}
```

**Template Priority**: 9/10 (CRITICAL)
**Complexity**: FILTERED
**Estimated Latency**: 18ms

---

## LIST Queries (8 examples)

### Example 7: List All Communities

**User Query**: "Show all communities"

**Matched Template**: `list_all_communities`

**Pattern**: `\b(show|list|display)\s+(all\s+)?(obc\s+)?communities\b`

**Extracted Entities**: None required

**Generated Query**:
```python
OBCCommunity.objects.all()[:20]  # Paginated, default 20
```

**Result**: [OBCCommunity(id=1, name='Community A', ...), ...]

**Response Format**:
```json
{
    "type": "list",
    "data": {
        "items": [...],
        "count": 20,
        "total": 127,
        "has_more": true
    },
    "html": "<table class='query-results-table'>...</table>"
}
```

**Template Priority**: 7/10 (HIGH)
**Estimated Latency**: 25ms

---

### Example 8: List Communities by Location

**User Query**: "Show communities in Zamboanga del Sur"

**Matched Template**: `list_communities_by_location`

**Pattern**: `\b(show|list|display)\s+communities\s+(in|at|from)\s+(?P<location>[\w\s]+)`

**Extracted Entities**:
- **location**:
  - type: `province`
  - value: `Zamboanga del Sur`
  - confidence: 0.92

**Generated Query**:
```python
OBCCommunity.objects.filter(
    barangay__municipality__province__name__icontains='Zamboanga del Sur'
).select_related('barangay__municipality__province')[:20]
```

**Result**: List of 18 communities

**Response Format**:
```html
<table class="query-results-table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Barangay</th>
            <th>Municipality</th>
            <th>Population</th>
            <th>Ethnicity</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Community Alpha</td>
            <td>Barangay XYZ</td>
            <td>Pagadian City</td>
            <td>250</td>
            <td>Maranao</td>
        </tr>
        <!-- ... more rows ... -->
    </tbody>
</table>
```

**Template Priority**: 9/10 (CRITICAL)
**Estimated Latency**: 30ms

---

### Example 9: List Communities by Livelihood

**User Query**: "List communities with farming livelihood"

**Matched Template**: `list_communities_by_livelihood`

**Extracted Entities**:
- **livelihood**:
  - value: `farming`
  - confidence: 0.95

**Generated Query**:
```python
OBCCommunity.objects.filter(
    primary_livelihood__icontains='farming'
).select_related('barangay__municipality__province__region')[:20]
```

**Result**: List of farming communities

**Template Priority**: 8/10 (HIGH)
**Estimated Latency**: 28ms

---

## AGGREGATE Queries (4 examples)

### Example 10: Total Population by Region

**User Query**: "What's the total population by region?"

**Matched Template**: `aggregate_population_by_region`

**Pattern**: `\b(total|sum|aggregate)\s+(population|residents)\s+by\s+region`

**Extracted Entities**: None required

**Generated Query**:
```python
OBCCommunity.objects.values(
    'barangay__municipality__province__region__name'
).annotate(
    total_population=Sum('total_population')
).order_by('-total_population')
```

**Result**:
```python
[
    {'barangay__municipality__province__region__name': 'Region IX', 'total_population': 12500},
    {'barangay__municipality__province__region__name': 'Region X', 'total_population': 8300},
    {'barangay__municipality__province__region__name': 'Region XII', 'total_population': 6200},
]
```

**Response Format**:
```json
{
    "type": "aggregate",
    "data": {
        "aggregates": {
            "Region IX": 12500,
            "Region X": 8300,
            "Region XII": 6200
        },
        "total": 27000
    },
    "html": "<div class='aggregate-result'>...</div>",
    "chart_config": {
        "type": "bar",
        "data": {...}
    }
}
```

**Template Priority**: 7/10 (MEDIUM)
**Complexity**: AGGREGATED
**Estimated Latency**: 35ms

---

### Example 11: Average Population per Community

**User Query**: "What's the average population per community?"

**Matched Template**: `aggregate_avg_population`

**Pattern**: `\b(average|mean|avg)\s+population\s+(per|of)\s+communit`

**Generated Query**:
```python
OBCCommunity.objects.aggregate(
    avg_population=Avg('total_population')
)
```

**Result**: `{'avg_population': 95.7}`

**Response Format**:
```json
{
    "type": "aggregate",
    "data": {
        "avg_population": 95.7
    },
    "html": "<div class='aggregate-item'><span class='label'>Average Population:</span><span class='value'>95.7</span></div>"
}
```

**Template Priority**: 6/10 (MEDIUM)
**Estimated Latency**: 20ms

---

## FIND Queries (3 examples)

### Example 12: Find Communities by Multiple Criteria

**User Query**: "Find Maranao communities with fishing livelihood in Zamboanga"

**Matched Template**: `find_communities_by_ethnicity_livelihood_location`

**Pattern**: `\bfind\s+(?P<ethnicity>\w+)\s+communities\s+with\s+(?P<livelihood>\w+)\s+livelihood\s+in\s+(?P<location>[\w\s]+)`

**Extracted Entities**:
- **ethnolinguistic_group**: `Maranao`
- **livelihood**: `fishing`
- **location**: `Zamboanga` (province type inferred)

**Generated Query**:
```python
OBCCommunity.objects.filter(
    primary_ethnolinguistic_group__icontains='Maranao',
    primary_livelihood__icontains='fishing',
    Q(barangay__municipality__province__name__icontains='Zamboanga') |
    Q(barangay__municipality__province__region__name__icontains='Zamboanga')
)[:20]
```

**Result**: List of matching communities

**Template Priority**: 9/10 (CRITICAL)
**Complexity**: MULTI_CRITERIA
**Estimated Latency**: 40ms

---

## Performance Notes

### Query Optimization

**Fast Queries** (<20ms):
- Simple COUNT queries without joins
- LIST queries with proper indexing
- Cached results (L1/L2 cache hit)

**Medium Queries** (20-40ms):
- COUNT with location filters (one JOIN)
- LIST with select_related() optimization
- AGGREGATE queries without complex grouping

**Slower Queries** (40-100ms):
- Multi-criteria FIND queries (multiple JOINs)
- Complex AGGREGATE with grouping
- LIST queries without optimization

### Caching Strategy

**High Cache TTL** (600s = 10 minutes):
- Total counts (rarely change)
- Location-based counts (stable)
- Ethnicity-based counts (stable)

**Medium Cache TTL** (300s = 5 minutes):
- List queries with filters
- Aggregate queries

**Low Cache TTL** (60s = 1 minute):
- Recent updates queries
- Status-based queries

---

## Entity Extraction Examples

### Location Entities

**Region Extraction**:
- "Region IX" → `{'type': 'region', 'value': 'Region IX'}`
- "Zamboanga Peninsula" → `{'type': 'region', 'value': 'Region IX'}`

**Province Extraction**:
- "Zamboanga del Sur" → `{'type': 'province', 'value': 'Zamboanga del Sur'}`
- "Sultan Kudarat" → `{'type': 'province', 'value': 'Sultan Kudarat'}`

**Municipality Extraction**:
- "Pagadian City" → `{'type': 'municipality', 'value': 'Pagadian City'}`
- "Cotabato City" → `{'type': 'municipality', 'value': 'Cotabato City'}`

### Ethnolinguistic Group Entities

**Recognized Groups**:
- Maranao, Maguindanao, Tausug, Yakan, Sama, Badjao, Iranun, Kalagan, Kalibugan

**Extraction**:
- "Maranao communities" → `{'value': 'Maranao', 'confidence': 0.98}`
- "Tausug" → `{'value': 'Tausug', 'confidence': 0.98}`

### Livelihood Entities

**Recognized Livelihoods**:
- Fishing, Farming, Trading, Government, Education, Crafts, Manufacturing

**Extraction**:
- "fishing livelihood" → `{'value': 'fishing', 'confidence': 0.95}`
- "farmers" → `{'value': 'farming', 'confidence': 0.90}`

---

## Common Query Variations

### "How many communities..."

**Variations**:
- "How many communities are there?"
- "Total communities"
- "Count all communities"
- "Number of communities"
- "Community count"

**All match**: `count_total_communities`

### "Show communities..."

**Variations**:
- "Show all communities"
- "List communities"
- "Display communities"
- "Give me communities"
- "Communities list"

**All match**: `list_all_communities`

### Location Specifications

**Region**:
- "in Region IX"
- "from Region IX"
- "within Region IX"
- "at Region IX"

**Province**:
- "in Zamboanga del Sur"
- "from Zamboanga del Sur province"

**Municipality**:
- "in Pagadian City"
- "at Pagadian"

---

**Last Updated**: October 6, 2025
**Template Count**: 25 current → 65 target
**Next**: See [ARCHITECTURE.md](../ARCHITECTURE.md) for expansion plan
