# MonitoringEntry QuerySet Reference

Quick reference guide for using MonitoringEntry custom manager methods.

## Table of Contents

- [Performance Methods](#performance-methods)
- [Category Filters](#category-filters)
- [Status Filters](#status-filters)
- [Date Filters](#date-filters)
- [Business Logic Filters](#business-logic-filters)
- [Chaining Examples](#chaining-examples)

## Performance Methods

### `with_related()`

Optimally prefetch all common relationships.

**Use Case:** When you need to display entry details with related organizations, communities, policies, etc.

**Performance:** Reduces 100+ queries to 2-3 queries.

```python
# Dashboard view - fetch 50 entries with all relationships
entries = MonitoringEntry.objects.with_related()[:50]

# Accessing related data triggers no additional queries
for entry in entries:
    print(entry.implementing_moa.name)  # No query
    print(entry.lead_organization.name)  # No query
    for community in entry.communities.all():  # No query
        print(community.display_name)
```

**Relationships Prefetched:**

**ForeignKeys (select_related):**
- `lead_organization`
- `implementing_moa`
- `submitted_by_community`
- `submitted_to_organization`
- `related_assessment`
- `related_policy`
- `coverage_region`, `coverage_province`, `coverage_municipality`, `coverage_barangay`
- `created_by`, `updated_by`, `reviewed_by`, `budget_approved_by`, `executive_approved_by`

**ManyToMany (prefetch_related):**
- `communities`
- `supporting_organizations`
- `needs_addressed`
- `implementing_policies`
- `standard_outcome_indicators`
- `funding_flows`
- `workflow_stages`
- `updates`

### `with_funding_totals()`

Annotate funding calculations at database level.

**Use Case:** When you need allocation, obligation, and disbursement totals.

**Performance:** Database aggregation vs. Python loops.

```python
# Budget dashboard - get entries with funding totals
entries = MonitoringEntry.objects.with_funding_totals()

for entry in entries:
    print(f"Budget: ₱{entry.budget_allocation:,.2f}")
    print(f"Allocations: ₱{entry.total_allocations_sum or 0:,.2f}")
    print(f"Obligations: ₱{entry.total_obligations_sum or 0:,.2f}")
    print(f"Disbursements: ₱{entry.total_disbursements_sum or 0:,.2f}")

    # Calculate variance
    variance = (entry.total_allocations_sum or 0) - (entry.budget_allocation or 0)
    print(f"Variance: ₱{variance:,.2f}")
```

**Annotated Fields:**
- `total_allocations_sum` - Sum of allocation tranches
- `total_obligations_sum` - Sum of obligation tranches
- `total_disbursements_sum` - Sum of disbursement tranches

## Category Filters

### `moa_ppas()`

Filter to MOA Programs, Projects, and Activities.

```python
# Get all MOA PPAs
moa_entries = MonitoringEntry.objects.moa_ppas()

# MOA PPAs for current year
current_year_moa = MonitoringEntry.objects.moa_ppas().by_fiscal_year(2025)
```

### `oobc_ppas()`

Filter to OOBC-led initiatives.

```python
# Get all OOBC initiatives
oobc_entries = MonitoringEntry.objects.oobc_ppas()

# Active OOBC programs
active_oobc = MonitoringEntry.objects.oobc_ppas().active()
```

### `obc_requests()`

Filter to OBC community requests.

```python
# Get all OBC requests
requests = MonitoringEntry.objects.obc_requests()

# Pending OBC requests
pending_requests = MonitoringEntry.objects.obc_requests().pending_approval()
```

## Status Filters

### `active()`

Returns entries in "planning" or "ongoing" status.

```python
# All active entries
active_entries = MonitoringEntry.objects.active()

# Active MOA PPAs
active_moa = MonitoringEntry.objects.moa_ppas().active()

# Count active entries
active_count = MonitoringEntry.objects.active().count()
```

### `completed()`

Returns entries with "completed" status.

```python
# All completed entries
completed = MonitoringEntry.objects.completed()

# Completed initiatives by sector
completed_economic = MonitoringEntry.objects.completed().by_sector('economic')

# Completion rate
total = MonitoringEntry.objects.count()
completed_count = MonitoringEntry.objects.completed().count()
completion_rate = (completed_count / total) * 100
```

### `high_priority()`

Returns entries marked as "high" or "urgent" priority.

```python
# All high-priority items
urgent = MonitoringEntry.objects.high_priority()

# High-priority requests needing attention
urgent_requests = (
    MonitoringEntry.objects
    .obc_requests()
    .high_priority()
    .pending_approval()
)
```

### `pending_approval()`

Returns entries not yet approved.

```python
# All pending approval
pending = MonitoringEntry.objects.pending_approval()

# Pending MOA PPAs
pending_moa = MonitoringEntry.objects.moa_ppas().pending_approval()

# Pending approval by approval status
draft = MonitoringEntry.objects.pending_approval().filter(approval_status='draft')
```

## Date Filters

### `by_fiscal_year(year)`

Filter entries by fiscal year.

```python
# Current fiscal year
current_year = 2025
fy_2025 = MonitoringEntry.objects.by_fiscal_year(current_year)

# MOA PPAs for FY 2025
moa_fy2025 = MonitoringEntry.objects.moa_ppas().by_fiscal_year(2025)

# Multi-year comparison
fy_2024 = MonitoringEntry.objects.by_fiscal_year(2024).count()
fy_2025 = MonitoringEntry.objects.by_fiscal_year(2025).count()
```

### `by_plan_year(year)`

Filter entries by planning year.

```python
# AIP 2025 entries
aip_2025 = MonitoringEntry.objects.by_plan_year(2025)

# Planning year entries by category
aip_moa = MonitoringEntry.objects.moa_ppas().by_plan_year(2025)
aip_oobc = MonitoringEntry.objects.oobc_ppas().by_plan_year(2025)
```

## Business Logic Filters

### `by_sector(sector)`

Filter entries by sector.

**Valid Sectors:**
- `'economic'` - Economic Development
- `'social'` - Social Development
- `'infrastructure'` - Infrastructure
- `'environment'` - Environment & DRRM
- `'governance'` - Governance & Institution Building
- `'peace_security'` - Peace, Security & Reconciliation

```python
# Economic development initiatives
economic = MonitoringEntry.objects.by_sector('economic')

# Social development MOA PPAs
social_moa = MonitoringEntry.objects.moa_ppas().by_sector('social')

# Sector breakdown
from monitoring.models import MonitoringEntry

for sector, label in MonitoringEntry.SECTOR_CHOICES:
    count = MonitoringEntry.objects.by_sector(sector).count()
    print(f"{label}: {count}")
```

### `by_organization(org)`

Filter entries by lead organization.

```python
from coordination.models import Organization

# Get specific organization
mooe = Organization.objects.get(acronym='MOOE')

# All MOOE entries
mooe_entries = MonitoringEntry.objects.by_organization(mooe)

# Active MOOE programs
active_mooe = MonitoringEntry.objects.by_organization(mooe).active()
```

### `over_budget()`

Find entries where allocations exceed budget.

**Note:** Automatically applies `with_funding_totals()` annotation.

```python
# All over-budget entries
over_budget = MonitoringEntry.objects.over_budget()

# Over-budget MOA PPAs requiring review
budget_issues = (
    MonitoringEntry.objects
    .moa_ppas()
    .over_budget()
    .with_related()
)

for entry in budget_issues:
    budget = entry.budget_allocation or 0
    allocated = entry.total_allocations_sum or 0
    variance = allocated - budget
    print(f"{entry.title}: Over by ₱{variance:,.2f}")
```

## Chaining Examples

### Dashboard Statistics

```python
from django.utils import timezone

current_year = timezone.now().year

# Current year MOA PPAs breakdown
moa_stats = {
    'total': MonitoringEntry.objects.moa_ppas().by_fiscal_year(current_year).count(),
    'active': MonitoringEntry.objects.moa_ppas().active().by_fiscal_year(current_year).count(),
    'completed': MonitoringEntry.objects.moa_ppas().completed().by_fiscal_year(current_year).count(),
    'high_priority': MonitoringEntry.objects.moa_ppas().high_priority().count(),
}
```

### Complex Filtering

```python
# Critical items needing immediate attention
critical = (
    MonitoringEntry.objects
    .active()
    .high_priority()
    .pending_approval()
    .with_related()
)

# Over-budget initiatives by sector
from monitoring.models import MonitoringEntry

for sector, label in MonitoringEntry.SECTOR_CHOICES:
    over_budget_count = (
        MonitoringEntry.objects
        .by_sector(sector)
        .over_budget()
        .count()
    )
    if over_budget_count > 0:
        print(f"{label}: {over_budget_count} over budget")
```

### Performance-Optimized Queries

```python
# Detail view - single entry with all relationships
entry = MonitoringEntry.objects.with_related().get(pk=entry_id)

# Dashboard view - multiple entries with funding totals
entries = (
    MonitoringEntry.objects
    .with_related()
    .with_funding_totals()
    .order_by('-updated_at')[:20]
)

# Report generation - filtered entries with all data
report_entries = (
    MonitoringEntry.objects
    .moa_ppas()
    .by_fiscal_year(2025)
    .active()
    .with_related()
    .with_funding_totals()
)
```

### Aggregation Examples

```python
from django.db.models import Sum, Avg, Count

# Total budget by category
budget_by_category = (
    MonitoringEntry.objects
    .values('category')
    .annotate(
        total_budget=Sum('budget_allocation'),
        avg_progress=Avg('progress'),
        count=Count('id')
    )
)

# Sector-wise funding analysis
sector_analysis = (
    MonitoringEntry.objects
    .with_funding_totals()
    .values('sector')
    .annotate(
        total_allocation=Sum('total_allocations_sum'),
        total_disbursement=Sum('total_disbursements_sum'),
        entry_count=Count('id')
    )
)
```

## Best Practices

### 1. Always Use `with_related()` for List Views

```python
# ✅ GOOD - Optimized
entries = MonitoringEntry.objects.with_related()[:50]

# ❌ BAD - N+1 queries
entries = MonitoringEntry.objects.all()[:50]
```

### 2. Chain Filters from General to Specific

```python
# ✅ GOOD - Readable, efficient
entries = (
    MonitoringEntry.objects
    .moa_ppas()
    .by_fiscal_year(2025)
    .active()
    .high_priority()
)

# ❌ BAD - Harder to read
entries = MonitoringEntry.objects.filter(
    category='moa_ppa',
    fiscal_year=2025,
    status__in=['planning', 'ongoing'],
    priority__in=['high', 'urgent']
)
```

### 3. Use `with_funding_totals()` When Needed

```python
# ✅ GOOD - Database-level aggregation
entries = MonitoringEntry.objects.with_funding_totals()
for entry in entries:
    total = entry.total_allocations_sum or 0

# ❌ BAD - Python-level calculation (N queries)
entries = MonitoringEntry.objects.all()
for entry in entries:
    total = sum(flow.amount for flow in entry.funding_flows.filter(tranche_type='allocation'))
```

### 4. Combine Methods for Complex Queries

```python
# ✅ GOOD - Combines performance and filtering
entries = (
    MonitoringEntry.objects
    .moa_ppas()
    .active()
    .with_related()
    .with_funding_totals()
)

# Now you can access everything without additional queries
for entry in entries:
    print(entry.implementing_moa.name)  # No query
    print(entry.total_allocations_sum)  # Already calculated
```

## Performance Tips

1. **Use `select_related()` for ForeignKeys** - Already included in `with_related()`
2. **Use `prefetch_related()` for ManyToMany** - Already included in `with_related()`
3. **Annotate at database level** - Use `with_funding_totals()` for calculations
4. **Filter early, fetch late** - Chain filters before calling `with_related()`
5. **Use `count()` for statistics** - Don't fetch full objects just to count

## Reference

**Model Location:** `src/monitoring/models.py`
**View Helper:** `src/monitoring/views.py` - `_prefetch_entries()`
**Documentation:** `docs/improvements/MONITORING_CUSTOM_MANAGER.md`

**Related Django Documentation:**
- [Managers](https://docs.djangoproject.com/en/5.1/topics/db/managers/)
- [QuerySets](https://docs.djangoproject.com/en/5.1/ref/models/querysets/)
- [select_related](https://docs.djangoproject.com/en/5.1/ref/models/querysets/#select-related)
- [prefetch_related](https://docs.djangoproject.com/en/5.1/ref/models/querysets/#prefetch-related)
