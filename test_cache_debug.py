"""Debug script to test cache invalidation for WorkItem calendar feed."""

from datetime import date, timedelta

import pytest

try:
    from django.conf import settings
    from django.core.cache import cache
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for cache debugging script",
        allow_module_level=True,
    )

print("=" * 80)
print("CACHE CONFIGURATION DEBUG")
print("=" * 80)

# Check Django cache backend
print("\n1. DJANGO CACHE BACKEND:")
print("-" * 80)
if hasattr(settings, 'CACHES'):
    print(f"Cache backend configured: {settings.CACHES}")
else:
    print("⚠️  NO CACHES setting found - Django is using DummyCache (development default)")
    print("   DummyCache doesn't actually store anything - all cache.get() returns None")
    print("   This explains why cache invalidation has no effect!")

# Test cache operations
print("\n2. CACHE OPERATION TEST:")
print("-" * 80)
test_key = "test_key_12345"
test_value = {"test": "data"}

cache.set(test_key, test_value, 300)
retrieved = cache.get(test_key)

print(f"Set cache key: {test_key}")
print(f"Retrieved value: {retrieved}")

if retrieved is None:
    print("❌ CACHE NOT WORKING - Using DummyCache backend")
else:
    print("✅ Cache is working")

# Simulate calendar feed cache key generation
print("\n3. CALENDAR FEED CACHE KEY FORMAT:")
print("-" * 80)

user_id = 1
work_type = None
status = None
start_date = date(2025, 10, 1)
end_date = date(2025, 10, 31)

# Calendar feed format (from calendar.py line 98)
calendar_cache_key = f"calendar_feed:{user_id}:{work_type}:{status}:{start_date}:{end_date}"
print(f"Calendar endpoint uses: {calendar_cache_key}")
print(f"  Type of start_date: {type(start_date)}")
print(f"  Type of end_date: {type(end_date)}")

# Simulate deletion cache key generation
print("\n4. DELETION CACHE KEY FORMAT:")
print("-" * 80)

today = date.today()
start_of_month = today.replace(day=1)
end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

deletion_cache_key = f"calendar_feed:{user_id}:{work_type}:{status}:{start_of_month}:{end_of_month}"
print(f"Deletion code uses: {deletion_cache_key}")
print(f"  Type of start_of_month: {type(start_of_month)}")
print(f"  Type of end_of_month: {type(end_of_month)}")

# Test if keys match
print("\n5. CACHE KEY COMPARISON:")
print("-" * 80)

# Calendar might receive ISO strings from FullCalendar
iso_start = "2025-10-01T00:00:00+08:00"
iso_end = "2025-10-31T23:59:59+08:00"

from datetime import datetime

parsed_start = datetime.fromisoformat(iso_start).date()
parsed_end = datetime.fromisoformat(iso_end).date()

calendar_iso_key = f"calendar_feed:{user_id}:{work_type}:{status}:{parsed_start}:{parsed_end}"
print(f"Calendar with ISO parsing: {calendar_iso_key}")

# Check if date objects match
print(f"\nDate comparison:")
print(f"  start_of_month ({start_of_month}) == parsed_start ({parsed_start}): {start_of_month == parsed_start}")
print(f"  end_of_month ({end_of_month}) == parsed_end ({parsed_end}): {end_of_month == parsed_end}")

# Test None serialization
print("\n6. NONE VALUE SERIALIZATION:")
print("-" * 80)
key_with_none_1 = f"calendar_feed:{user_id}:{None}:{None}:{start_date}:{end_date}"
key_with_none_2 = f"calendar_feed:{user_id}:None:None:{start_date}:{end_date}"

print(f"Using None directly: {key_with_none_1}")
print(f"Using string 'None': {key_with_none_2}")
print(f"Are they equal? {key_with_none_1 == key_with_none_2}")

# Conclusion
print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)

if not hasattr(settings, 'CACHES'):
    print("❌ ROOT CAUSE: Django is using DummyCache (no CACHES setting)")
    print("   - All cache.set() calls do nothing")
    print("   - All cache.get() calls return None")
    print("   - All cache.delete() calls do nothing")
    print("\n✅ SOLUTION:")
    print("   Add cache configuration to settings/base.py:")
    print("""
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
           'LOCATION': 'obcms-calendar-cache',
       }
   }
   """)
else:
    print("✅ Cache backend is configured")
    print("   Check if cache keys are matching between calendar feed and deletion")

print("=" * 80)
