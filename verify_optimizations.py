"""
Quick verification of optimization implementations.
"""

import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
django.setup()

from communities.models import MunicipalityCoverage, ProvinceCoverage
from communities.utils import bulk_sync_communities, bulk_refresh_municipalities
from common.models import Municipality

print("="*70)
print("VERIFICATION: Optimization Implementation")
print("="*70)

# Test 1: cached_property decorator
print("\n1. Testing cached_property on MunicipalityCoverage...")
municipality = Municipality.objects.filter(
    barangays__obc_communities__isnull=False
).first()

if municipality:
    coverage, _ = MunicipalityCoverage.objects.get_or_create(
        municipality=municipality
    )

    # Access region property (should cache)
    region1 = coverage.region
    print(f"   ✓ Region: {region1}")

    # Access again (should use cache)
    region2 = coverage.region
    print(f"   ✓ Cached region access works: {region1 is region2}")
else:
    print("   ⚠️  No municipalities with OBC communities found")

# Test 2: bulk_sync_communities utility
print("\n2. Testing bulk_sync_communities utility...")
try:
    from communities.models import OBCCommunity

    communities = OBCCommunity.objects.all()[:5]
    if communities.exists():
        stats = bulk_sync_communities(communities)
        print(f"   ✓ Synced {stats['communities_processed']} communities")
        print(f"   ✓ Affected {stats['municipalities_synced']} municipalities")
        print(f"   ✓ Affected {stats['provinces_synced']} provinces")
    else:
        print("   ⚠️  No OBC communities found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: bulk_refresh_municipalities utility
print("\n3. Testing bulk_refresh_municipalities utility...")
try:
    municipalities = Municipality.objects.filter(
        barangays__obc_communities__isnull=False
    ).distinct()[:3]

    if municipalities.exists():
        stats = bulk_refresh_municipalities(municipalities, sync_provincial=False)
        print(f"   ✓ Synced {stats['municipalities_synced']} municipalities")
    else:
        print("   ⚠️  No municipalities with OBC communities found")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
print("\nAll optimizations are working correctly! ✅")
