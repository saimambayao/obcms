# Auto-Sync Quick Reference Guide

**For Developers:** Quick reference for working with OBC coverage auto-sync

---

## How Auto-Sync Works

The system automatically keeps `MunicipalityCoverage` and `ProvinceCoverage` records in sync with individual `OBCCommunity` records.

```
OBCCommunity (Barangay level)
      ↓ auto-sync
MunicipalityCoverage (Municipality level)
      ↓ auto-sync
ProvinceCoverage (Province level)
```

**Triggers:**
- Creating/updating an `OBCCommunity` → syncs Municipality → syncs Province
- Deleting an `OBCCommunity` → syncs Municipality → syncs Province

---

## Individual Operations

### Creating a Community

```python
from common.models import Barangay
from communities.models import OBCCommunity

barangay = Barangay.objects.get(...)
community = OBCCommunity.objects.create(
    barangay=barangay,
    estimated_obc_population=1000,
    households=200,
    # ... other fields
)
# ✅ MunicipalityCoverage and ProvinceCoverage auto-sync via signals
```

### Updating a Community

```python
community = OBCCommunity.objects.get(...)
community.estimated_obc_population = 1500
community.households = 300
community.save()
# ✅ Auto-syncs municipality and province
```

### Deleting a Community

```python
community = OBCCommunity.objects.get(...)
community.delete()
# ✅ Auto-syncs municipality and province
```

### Manual Sync

```python
from communities.models import MunicipalityCoverage, ProvinceCoverage
from common.models import Municipality, Province

# Sync a specific municipality
municipality = Municipality.objects.get(...)
MunicipalityCoverage.sync_for_municipality(municipality)

# Sync a specific province
province = Province.objects.get(...)
ProvinceCoverage.sync_for_province(province)
```

---

## Bulk Operations (RECOMMENDED)

### Why Use Bulk Sync?

When creating/updating many communities at once:
- ❌ Individual syncs trigger cascade for each community (slow)
- ✅ Bulk sync triggers cascade once per province (fast)

### Bulk Creating Communities

```python
from communities.models import OBCCommunity
from communities.utils import bulk_sync_communities

# Method 1: bulk_create (doesn't trigger signals)
communities = [
    OBCCommunity(barangay=brgy1, ...),
    OBCCommunity(barangay=brgy2, ...),
    # ... more communities
]
created = OBCCommunity.objects.bulk_create(communities)

# Manual sync required (signals not triggered)
bulk_sync_communities(created)  # ✅ Efficient sync
```

### Bulk Updating Communities

```python
from communities.models import OBCCommunity
from communities.utils import bulk_sync_communities

# Method 1: Update queryset (doesn't trigger signals)
OBCCommunity.objects.filter(...).update(
    estimated_obc_population=F('estimated_obc_population') + 100
)

# Manual sync required
communities = OBCCommunity.objects.filter(...)
bulk_sync_communities(communities)  # ✅ Efficient sync
```

### Data Import Example

```python
from communities.utils import bulk_sync_communities, sync_entire_hierarchy

# Option 1: Sync specific communities
communities = OBCCommunity.objects.filter(...)
stats = bulk_sync_communities(communities)
print(f"Synced {stats['municipalities_synced']} municipalities")
print(f"Synced {stats['provinces_synced']} provinces")

# Option 2: Sync entire region
from common.models import Region

region = Region.objects.get(code='12')
stats = sync_entire_hierarchy(region)
print(f"Synced {stats['municipalities_synced']} municipalities")
print(f"Synced {stats['provinces_synced']} provinces")
```

---

## Utility Functions

### bulk_sync_communities()

Sync municipality and province coverages for multiple communities.

```python
from communities.utils import bulk_sync_communities

communities = OBCCommunity.objects.filter(...)
stats = bulk_sync_communities(
    communities,
    sync_provincial=True  # Default: True
)
# Returns: {'municipalities_synced': 10, 'provinces_synced': 2, 'communities_processed': 50}
```

### bulk_refresh_municipalities()

Refresh multiple municipality coverages and optionally sync provinces.

```python
from communities.utils import bulk_refresh_municipalities

municipalities = Municipality.objects.filter(...)
stats = bulk_refresh_municipalities(
    municipalities,
    sync_provincial=True  # Default: True
)
# Returns: {'municipalities_synced': 10, 'provinces_synced': 2}
```

### bulk_refresh_provinces()

Refresh multiple province coverages.

```python
from communities.utils import bulk_refresh_provinces

provinces = Province.objects.filter(...)
stats = bulk_refresh_provinces(provinces)
# Returns: {'provinces_synced': 2}
```

### sync_entire_hierarchy()

Sync all municipalities and provinces in a region (or all regions).

```python
from communities.utils import sync_entire_hierarchy

# Sync specific region
region = Region.objects.get(code='12')
stats = sync_entire_hierarchy(region)

# Sync all regions
stats = sync_entire_hierarchy()

# Returns: {'municipalities_synced': 50, 'provinces_synced': 5, 'region': 'Region XII'}
```

---

## Management Commands

### Sync All Coverage Records

```bash
# Sync all municipalities and provinces with OBC communities
python manage.py sync_obc_coverage

# Dry run (preview changes without saving)
python manage.py sync_obc_coverage --dry-run
```

**Output:**
```
Found 50 municipalities with Barangay OBCs

  + Created: Baungon, Bukidnon
  ✓ Updated: Iligan City, Lanao del Norte
  ...

📊 Executing optimized bulk sync...
✓ Synced 50 municipalities

Found 5 provinces with Barangay OBCs

  + Created: Bukidnon, Region X
  ✓ Updated: Lanao del Norte, Region X
  ...

📊 Executing optimized bulk provincial sync...
✓ Synced 5 provinces

SUMMARY:
  Barangay OBCs:       150
  Municipal Coverage:  45 created, 5 updated
  Provincial Coverage: 4 created, 1 updated
```

---

## Performance Best Practices

### ✅ DO

1. **Use bulk_create for multiple communities**
   ```python
   OBCCommunity.objects.bulk_create(communities)
   bulk_sync_communities(communities)
   ```

2. **Batch updates and sync once**
   ```python
   # Update many communities
   for community in communities:
       community.estimated_obc_population = new_value
       # DON'T save() here

   # Bulk update and sync
   OBCCommunity.objects.bulk_update(communities, ['estimated_obc_population'])
   bulk_sync_communities(communities)
   ```

3. **Use bulk_refresh for data migrations**
   ```python
   # After importing data
   municipalities = Municipality.objects.filter(...)
   bulk_refresh_municipalities(municipalities)
   ```

### ❌ DON'T

1. **Don't manually loop and save in migrations**
   ```python
   # ❌ BAD: Triggers signal cascade for each community
   for community in communities:
       community.save()  # Syncs municipality and province EVERY time!

   # ✅ GOOD: Use bulk operations
   OBCCommunity.objects.bulk_update(communities, fields)
   bulk_sync_communities(communities)
   ```

2. **Don't sync unnecessarily**
   ```python
   # ❌ BAD: Unnecessary sync
   MunicipalityCoverage.sync_for_municipality(municipality)  # Already synced by signal

   # ✅ GOOD: Let signals handle it
   community.save()  # Auto-syncs via signal
   ```

---

## Troubleshooting

### Coverage Not Updating

**Problem:** MunicipalityCoverage or ProvinceCoverage not reflecting new data

**Solutions:**

1. Check auto_sync flag:
   ```python
   coverage = MunicipalityCoverage.objects.get(...)
   if not coverage.auto_sync:
       coverage.auto_sync = True
       coverage.save()
       coverage.refresh_from_communities()
   ```

2. Manual sync:
   ```python
   MunicipalityCoverage.sync_for_municipality(municipality)
   ProvinceCoverage.sync_for_province(province)
   ```

3. Re-sync all:
   ```bash
   python manage.py sync_obc_coverage
   ```

### Performance Issues

**Problem:** Sync operations taking too long

**Diagnosis:**
```bash
# Run performance analysis
python analyze_sync_performance.py
```

**Solutions:**

1. Use bulk_sync for multiple operations
2. Check database indexes
3. Monitor query count (should be < 5 per sync)

### Missing Coverage Records

**Problem:** Some municipalities/provinces have no coverage record

**Solutions:**

1. Run sync command:
   ```bash
   python manage.py sync_obc_coverage
   ```

2. Or use utility:
   ```python
   from communities.utils import sync_entire_hierarchy
   sync_entire_hierarchy()
   ```

---

## API Reference

### OBCCommunity Signals

**post_save:** Triggers MunicipalityCoverage and ProvinceCoverage sync
**post_delete:** Triggers MunicipalityCoverage and ProvinceCoverage sync

### MunicipalityCoverage Methods

- `refresh_from_communities()` - Aggregate data from barangay communities
- `sync_for_municipality(municipality)` - Class method to sync a specific municipality
- `soft_delete(user=None)` - Soft delete and trigger provincial sync
- `restore()` - Restore and trigger provincial sync

### ProvinceCoverage Methods

- `refresh_from_municipalities()` - Aggregate data from municipal coverages
- `sync_for_province(province)` - Class method to sync a specific province
- `soft_delete(user=None)` - Soft delete (no further sync needed)
- `restore()` - Restore (no further sync needed)

---

## Quick Checklist

### Before Data Import
- [ ] Understand if bulk_create is appropriate
- [ ] Plan to use bulk_sync_communities() after import
- [ ] Consider disabling auto_sync temporarily for large imports

### After Data Import
- [ ] Run bulk_sync_communities() or sync_obc_coverage
- [ ] Verify coverage records created
- [ ] Check aggregate totals match source data

### When Debugging
- [ ] Run analyze_sync_performance.py
- [ ] Check auto_sync flag on coverage records
- [ ] Verify signals are not being skipped
- [ ] Check for soft-deleted records (is_deleted=True)

---

## See Also

- [AUTO_SYNC_PERFORMANCE_OPTIMIZATION.md](../../AUTO_SYNC_PERFORMANCE_OPTIMIZATION.md) - Technical analysis
- [AUTO_SYNC_OPTIMIZATION_SUMMARY.md](../../AUTO_SYNC_OPTIMIZATION_SUMMARY.md) - Implementation summary
- `/src/communities/utils/bulk_sync.py` - Utility source code
- `/src/communities/signals.py` - Signal handlers

---

**Last Updated:** October 5, 2025
**Maintainer:** OBCMS Development Team
