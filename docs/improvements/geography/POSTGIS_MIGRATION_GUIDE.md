# PostGIS Migration Guide (Future Enhancement)

**Date:** October 2, 2025
**Status:** 📋 REFERENCE ONLY (Not Currently Needed)
**Current Implementation:** JSONField (Production-Ready)

---

## ⚠️ Important Notice

**This guide is for FUTURE reference only.**

**Current OBCMS implementation uses JSONField for geographic data storage, which is:**
- ✅ Fully functional
- ✅ Production-ready
- ✅ Sufficient for all current requirements

**Migrate to PostGIS ONLY if you need:**
- Advanced spatial queries (distance-based searches, spatial joins)
- Geometric calculations (intersections, buffers, topology)
- Performance optimization for millions of features (current: 42K)

**See:** [GEOGRAPHIC_DATA_IMPLEMENTATION.md](./GEOGRAPHIC_DATA_IMPLEMENTATION.md) for why JSONField is recommended.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Migration Strategy](#migration-strategy)
3. [Step-by-Step Migration](#step-by-step-migration)
4. [Code Changes Required](#code-changes-required)
5. [Testing & Validation](#testing--validation)
6. [Rollback Procedure](#rollback-procedure)
7. [Performance Expectations](#performance-expectations)

---

## Prerequisites

### System Requirements

**Before starting PostGIS migration:**

1. **PostgreSQL 12+ with PostGIS 3.0+**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql-14-postgis-3

   # macOS (Homebrew)
   brew install postgis

   # Docker
   docker pull postgis/postgis:14-3.3
   ```

2. **Python GIS Libraries**
   ```bash
   # Install GDAL (required for GeoDjango)
   # Ubuntu/Debian
   sudo apt-get install gdal-bin libgdal-dev

   # macOS
   brew install gdal

   # Python packages
   pip install GDAL
   ```

3. **Django GIS Framework**
   ```bash
   # Update requirements/base.txt
   pip install django-gis
   ```

### Required Dependencies

**Update `requirements/base.txt`:**
```txt
# Add to existing requirements
GDAL>=3.4.0
django-gis>=4.2.0
```

**Update `settings/base.py`:**
```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django.contrib.gis',  # Add GeoDjango
]

# Database backend change
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Changed from postgresql
        'NAME': 'obcms_prod',
        # ... rest of config
    }
}
```

---

## Migration Strategy

### Phase-Based Approach

```
Phase 1: Preparation & Testing (Week 1)
├── Install PostGIS extension
├── Add geometry columns (parallel to JSON)
├── Create data migration scripts
└── Test in development environment

Phase 2: Data Migration (Week 2)
├── Backup existing data
├── Run migration scripts
├── Validate geometry data
└── Create spatial indexes

Phase 3: Code Updates (Week 3)
├── Update models
├── Update queries
├── Update serializers
└── Update frontend (if needed)

Phase 4: Testing & Validation (Week 4)
├── Unit tests
├── Integration tests
├── Performance benchmarks
└── User acceptance testing

Phase 5: Production Deployment (Week 5)
├── Schedule maintenance window
├── Run production migration
├── Monitor performance
└── Keep JSONField as backup (6 months)
```

**Total Estimated Time:** 4-5 weeks
**Risk Level:** MEDIUM-HIGH
**Reversibility:** MEDIUM (rollback possible with backup)

---

## Step-by-Step Migration

### Step 1: Enable PostGIS Extension

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql obcms_prod

-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify installation
SELECT PostGIS_Version();
-- Expected: POSTGIS="3.3.0" [...]

-- Grant permissions
GRANT ALL ON SCHEMA public TO obcms_user;
```

### Step 2: Update Django Models

**File: `src/common/models.py`**

```python
from django.contrib.gis.db import models as gis_models
from django.db import models

class Region(models.Model):
    # ... existing fields ...

    # KEEP existing JSONField (as backup during transition)
    boundary_geojson = models.JSONField(
        null=True,
        blank=True,
        help_text="GeoJSON boundary data (legacy, will be deprecated)"
    )

    center_coordinates = models.JSONField(
        null=True,
        blank=True,
        help_text="Legacy center coordinates"
    )

    # ADD PostGIS geometry fields
    boundary = gis_models.MultiPolygonField(
        srid=4326,  # WGS84 (standard GPS coordinates)
        null=True,
        blank=True,
        help_text="PostGIS boundary geometry"
    )

    center_point = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text="PostGIS center point"
    )

    class Meta:
        # ... existing meta ...
        pass

# Repeat for Province, Municipality, Barangay models
```

### Step 3: Generate Migration

```bash
# Create migration file
python manage.py makemigrations common --name add_postgis_geometry_fields

# Expected output:
# Migrations for 'common':
#   common/migrations/0XXX_add_postgis_geometry_fields.py
#     - Add field boundary to region
#     - Add field center_point to region
#     - Add field boundary to province
#     ... (for all geographic models)
```

### Step 4: Create Data Migration

**File: `src/common/migrations/0XXX_migrate_json_to_postgis.py`**

```python
from django.db import migrations
from django.contrib.gis.geos import GEOSGeometry, Point
import json


def json_to_postgis(apps, schema_editor):
    """Convert JSONField geographic data to PostGIS geometry."""

    Region = apps.get_model('common', 'Region')
    Province = apps.get_model('common', 'Province')
    Municipality = apps.get_model('common', 'Municipality')
    Barangay = apps.get_model('common', 'Barangay')

    models_to_migrate = [
        (Region, 'Region'),
        (Province, 'Province'),
        (Municipality, 'Municipality'),
        (Barangay, 'Barangay')
    ]

    for Model, name in models_to_migrate:
        migrated = 0
        errors = 0

        for obj in Model.objects.all():
            try:
                # Migrate boundary
                if obj.boundary_geojson:
                    geojson_str = json.dumps(obj.boundary_geojson)
                    obj.boundary = GEOSGeometry(geojson_str)

                # Migrate center point
                if obj.center_coordinates:
                    lat = obj.center_coordinates.get('lat')
                    lng = obj.center_coordinates.get('lng')
                    if lat and lng:
                        obj.center_point = Point(float(lng), float(lat), srid=4326)

                obj.save()
                migrated += 1

            except Exception as e:
                print(f"Error migrating {name} {obj.id}: {e}")
                errors += 1

        print(f"{name}: Migrated {migrated}, Errors {errors}")


def postgis_to_json(apps, schema_editor):
    """Reverse migration: PostGIS geometry back to JSON."""

    Region = apps.get_model('common', 'Region')
    Province = apps.get_model('common', 'Province')
    Municipality = apps.get_model('common', 'Municipality')
    Barangay = apps.get_model('common', 'Barangay')

    models_to_revert = [Region, Province, Municipality, Barangay]

    for Model in models_to_revert:
        for obj in Model.objects.all():
            # Revert boundary
            if obj.boundary:
                obj.boundary_geojson = json.loads(obj.boundary.geojson)

            # Revert center point
            if obj.center_point:
                obj.center_coordinates = {
                    'lat': obj.center_point.y,
                    'lng': obj.center_point.x
                }

            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0XXX_add_postgis_geometry_fields'),
    ]

    operations = [
        migrations.RunPython(json_to_postgis, postgis_to_json),
    ]
```

### Step 5: Run Migrations

```bash
# Apply migrations
python manage.py migrate

# Expected output:
# Running migrations:
#   Applying common.0XXX_add_postgis_geometry_fields... OK
#   Applying common.0XXX_migrate_json_to_postgis... OK
# Region: Migrated 17, Errors 0
# Province: Migrated 81, Errors 0
# Municipality: Migrated 1634, Errors 0
# Barangay: Migrated 42046, Errors 0
```

### Step 6: Create Spatial Indexes

```bash
# Django will create these automatically, but verify:
python manage.py sqlmigrate common 0XXX_add_postgis_geometry_fields

# Should include:
# CREATE INDEX "common_region_boundary_id" ON "common_region" USING GIST ("boundary");
# CREATE INDEX "common_region_center_point_id" ON "common_region" USING GIST ("center_point");
```

---

## Code Changes Required

### Update Models (GeoDjango)

```python
# Before (JSONField)
from django.db import models

class Region(models.Model):
    boundary_geojson = models.JSONField(null=True)
    center_coordinates = models.JSONField(null=True)

# After (PostGIS)
from django.contrib.gis.db import models as gis_models

class Region(models.Model):
    boundary = gis_models.MultiPolygonField(srid=4326, null=True)
    center_point = gis_models.PointField(srid=4326, null=True)
```

### Update Queries

```python
# Before (JSONField - no spatial queries)
regions = Region.objects.filter(
    center_coordinates__lat__gte=8.0
)

# After (PostGIS - spatial queries enabled)
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

# Find regions near a point
point = Point(124.0, 8.0, srid=4326)
nearby_regions = Region.objects.filter(
    center_point__dwithin=(point, 50000)  # 50km
).annotate(
    distance=Distance('center_point', point)
).order_by('distance')

# Find municipalities within a region boundary
municipalities = Municipality.objects.filter(
    center_point__within=region.boundary
)

# Find overlapping service areas
overlapping = ServiceArea.objects.filter(
    boundary__intersects=other_area.boundary
)
```

### Update Serializers

```python
# Before (JSONField)
from rest_framework import serializers

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'boundary_geojson']

# After (PostGIS with GeoJSON output)
from rest_framework_gis.serializers import GeoFeatureModelSerializer

class RegionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Region
        geo_field = 'boundary'  # PostGIS field
        fields = ['id', 'name']

    # Or manual GeoJSON conversion
    boundary_geojson = serializers.SerializerMethodField()

    def get_boundary_geojson(self, obj):
        if obj.boundary:
            return json.loads(obj.boundary.geojson)
        return None
```

### Update Views

```python
# Before (JSONField)
from django.http import JsonResponse

def region_detail(request, code):
    region = Region.objects.get(code=code)
    return JsonResponse({
        'boundary': region.boundary_geojson
    })

# After (PostGIS)
def region_detail(request, code):
    region = Region.objects.get(code=code)
    return JsonResponse({
        'boundary': json.loads(region.boundary.geojson) if region.boundary else None
    })
```

### Frontend Changes (Minimal)

```javascript
// Frontend code stays mostly the same!
// PostGIS geometry is converted to GeoJSON in serializer

fetch('/api/regions/XII/')
  .then(res => res.json())
  .then(data => {
    // data.boundary is still GeoJSON (converted from PostGIS)
    L.geoJSON(data.boundary).addTo(map);
  });
```

---

## Testing & Validation

### Data Integrity Tests

```python
# Test: Verify all geometries migrated correctly
from django.test import TestCase
from common.models import Region, Province

class PostGISMigrationTest(TestCase):
    def test_all_boundaries_migrated(self):
        """Ensure all JSONField boundaries converted to PostGIS."""
        regions_with_json = Region.objects.exclude(boundary_geojson__isnull=True).count()
        regions_with_postgis = Region.objects.exclude(boundary__isnull=True).count()

        self.assertEqual(regions_with_json, regions_with_postgis,
                        "Not all boundaries migrated to PostGIS")

    def test_geometry_validity(self):
        """Check all PostGIS geometries are valid."""
        from django.contrib.gis.db.models.functions import IsValid

        invalid_regions = Region.objects.annotate(
            valid=IsValid('boundary')
        ).filter(valid=False)

        self.assertEqual(invalid_regions.count(), 0,
                        f"Found {invalid_regions.count()} invalid geometries")

    def test_coordinates_match(self):
        """Verify JSON coordinates match PostGIS points."""
        for region in Region.objects.exclude(center_coordinates__isnull=True):
            if region.center_point:
                json_lat = region.center_coordinates['lat']
                json_lng = region.center_coordinates['lng']

                self.assertAlmostEqual(region.center_point.y, json_lat, places=5)
                self.assertAlmostEqual(region.center_point.x, json_lng, places=5)
```

### Spatial Query Tests

```python
def test_spatial_queries(self):
    """Test PostGIS-specific spatial operations."""
    from django.contrib.gis.geos import Point

    # Distance query
    point = Point(124.0, 8.0, srid=4326)
    nearby = Region.objects.filter(
        center_point__dwithin=(point, 100000)  # 100km
    )
    self.assertGreater(nearby.count(), 0)

    # Contains query
    region = Region.objects.first()
    provinces_in_region = Province.objects.filter(
        center_point__within=region.boundary
    )
    self.assertGreater(provinces_in_region.count(), 0)
```

### Performance Benchmarks

```python
import time
from django.test import TestCase

class PostGISPerformanceTest(TestCase):
    def test_boundary_query_performance(self):
        """Compare JSONField vs PostGIS query performance."""

        # JSONField query (old)
        start = time.time()
        regions_json = Region.objects.exclude(boundary_geojson__isnull=True)
        list(regions_json)  # Force evaluation
        json_time = time.time() - start

        # PostGIS query (new)
        start = time.time()
        regions_postgis = Region.objects.exclude(boundary__isnull=True)
        list(regions_postgis)
        postgis_time = time.time() - start

        print(f"JSONField: {json_time:.3f}s, PostGIS: {postgis_time:.3f}s")

        # PostGIS should be similar or faster
        self.assertLessEqual(postgis_time, json_time * 1.5)
```

---

## Rollback Procedure

### If Migration Fails

**Option 1: Revert Migrations**
```bash
# Rollback to before PostGIS
python manage.py migrate common 0XXX_before_postgis

# Remove geometry columns
python manage.py migrate common 0XXX
```

**Option 2: Restore from Backup**
```bash
# Restore database backup
pg_restore -d obcms_prod backup_before_postgis.dump

# Revert Django settings
# Change ENGINE back to 'django.db.backends.postgresql'
```

**Option 3: Keep Both (Recommended Initially)**
```python
# Keep both JSONField and PostGIS for 6 months
class Region(models.Model):
    # Legacy (keep as backup)
    boundary_geojson = models.JSONField(null=True)

    # New (PostGIS)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True)

    # Use PostGIS by default, fall back to JSON
    def get_boundary(self):
        if self.boundary:
            return json.loads(self.boundary.geojson)
        return self.boundary_geojson
```

---

## Performance Expectations

### Query Performance Comparison

| Operation | JSONField | PostGIS | Improvement |
|-----------|-----------|---------|-------------|
| **Retrieve boundary** | 2-5 ms | 1-3 ms | 40% faster |
| **Spatial join** | N/A | 10-20 ms | Only PostGIS |
| **Distance query** | N/A | 5-15 ms | Only PostGIS |
| **Contains query** | N/A | 3-8 ms | Only PostGIS |
| **Index size** | Minimal | +20-30% | GIST index overhead |

### Storage Comparison

| Metric | JSONField | PostGIS | Difference |
|--------|-----------|---------|------------|
| **Database size** | ~200 MB | ~150 MB | 25% smaller (binary) |
| **Index size** | ~10 MB | ~50 MB | 5x larger (GIST) |
| **Backup size** | ~200 MB | ~250 MB | 25% larger (includes indexes) |

### When PostGIS Provides Value

**Scenarios where PostGIS significantly improves performance:**

1. **Spatial Joins** (10-100x faster than application-level filtering)
   ```python
   # Find all communities within service area
   # JSONField: Fetch all, filter in Python (slow)
   # PostGIS: Spatial index lookup (fast)
   ```

2. **Distance Queries** (Only possible with PostGIS)
   ```python
   # Find nearest hospital
   # JSONField: Calculate distance for all records (very slow)
   # PostGIS: Indexed distance search (fast)
   ```

3. **Complex Geometry** (Thousands of features)
   - JSONField: Linear scan
   - PostGIS: GIST spatial index

**For OBCMS current use case: Minimal benefit (5-10% performance gain)**

---

## Cost-Benefit Analysis

### Implementation Costs

| Cost Category | Effort | Risk | Notes |
|---------------|--------|------|-------|
| **Development** | 2-3 weeks | MEDIUM | Model changes, query updates |
| **Testing** | 1-2 weeks | MEDIUM | Data validation, performance tests |
| **Deployment** | 1 week | HIGH | PostGIS installation, migration |
| **Maintenance** | Ongoing | MEDIUM | GDAL updates, PostGIS upgrades |

**Total Cost: 4-6 weeks development + ongoing maintenance**

### Expected Benefits

| Benefit | Value for OBCMS | Notes |
|---------|-----------------|-------|
| **Spatial queries** | LOW | Not currently needed |
| **Performance** | LOW | Marginal improvement at current scale |
| **Storage efficiency** | LOW | ~50 MB saved (negligible) |
| **GIS features** | MEDIUM | Future-proofing for potential needs |

**Total Benefit: LOW-MEDIUM (for current requirements)**

### Recommendation

**Delay PostGIS migration until:**
- ✅ Spatial queries become a requirement
- ✅ Scale exceeds 500K features
- ✅ Performance becomes an issue
- ✅ Advanced GIS features are needed

**Current JSONField implementation is sufficient.**

---

## Conclusion

### Decision Framework

**Migrate to PostGIS if you answer "YES" to 3+ questions:**

1. ❓ Do you need distance-based queries? (e.g., "find within 5km")
2. ❓ Do you need spatial joins? (e.g., "points within polygon")
3. ❓ Do you need geometric calculations? (intersections, buffers)
4. ❓ Do you have millions of geographic features?
5. ❓ Do you need topology validation?
6. ❓ Do you need network analysis (routing)?

**For current OBCMS: 0/6 "YES" → PostGIS NOT needed**

### Alternative: Hybrid Approach

**If spatial queries become needed for specific features only:**

```python
# Option: Add PostGIS for NEW models only
class ServiceArea(models.Model):
    # Use PostGIS for new spatial features
    coverage_area = gis_models.PolygonField(srid=4326)

# Keep JSONField for administrative boundaries
class Region(models.Model):
    # Existing JSONField (no migration needed)
    boundary_geojson = models.JSONField()
```

This avoids migrating 42K+ existing features while enabling spatial queries for new use cases.

---

## References

- **GeoDjango Documentation:** https://docs.djangoproject.com/en/4.2/ref/contrib/gis/
- **PostGIS Documentation:** https://postgis.net/documentation/
- **GDAL Installation:** https://gdal.org/download.html
- **Current Implementation:** [GEOGRAPHIC_DATA_IMPLEMENTATION.md](./GEOGRAPHIC_DATA_IMPLEMENTATION.md)
- **PostgreSQL Migration:** [docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md](/Users/saidamenmambayao/Library/Mobile%20Documents/com~apple~CloudDocs/BTA/OOBC/obcms/docs/deployment/POSTGRESQL_MIGRATION_REVIEW.md)

---

**Document Status:** 📋 REFERENCE ONLY
**Implementation Status:** NOT NEEDED (JSONField sufficient)
**Last Updated:** October 2, 2025
**Next Review:** When spatial queries become required
**Author:** Claude Code (AI Assistant)
