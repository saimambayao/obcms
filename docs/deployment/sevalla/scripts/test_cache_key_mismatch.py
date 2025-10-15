"""
Test to demonstrate the exact cache key mismatch issue.

The problem is that FullCalendar sends requests with varying date ranges
depending on the current view, but our cache invalidation assumes fixed
monthly boundaries.

Example scenario:
1. User views October 2025 in month view
   - FullCalendar requests: 2025-09-28 to 2025-11-08 (shows neighboring days)
   - Cache key: calendar_feed:1:None:None:2025-09-28:2025-11-08

2. User deletes an item on Oct 6, 2025
   - Deletion clears: calendar_feed:1:None:None:2025-10-01:2025-10-31

3. User refreshes page
   - FullCalendar still requests: 2025-09-28 to 2025-11-08
   - Cache hit! Returns stale data with deleted item

ROOT CAUSE: Date range mismatch
- Calendar uses view-dependent ranges (varies by month/week/day view)
- Deletion uses fixed month boundaries
- They never match exactly
"""

from datetime import date, timedelta

print("=" * 80)
print("CACHE KEY MISMATCH DEMONSTRATION")
print("=" * 80)

# Simulate FullCalendar month view for October 2025
# FullCalendar shows extra days from neighboring months to fill the grid
print("\n1. FULLCALENDAR MONTH VIEW (October 2025):")
print("-" * 80)

# For October 2025 month view, FullCalendar typically shows:
# - Last few days of September (to complete first week)
# - All of October
# - First few days of November (to complete last week)

october_first = date(2025, 10, 1)  # Wednesday
september_start = october_first - timedelta(days=2)  # Previous Sunday
november_end = date(2025, 11, 1) + timedelta(days=7)  # Next Sunday

print(f"October 1, 2025 is a: {october_first.strftime('%A')}")
print(f"FullCalendar shows: {september_start} to {november_end}")
print(f"  (includes {(november_end - september_start).days} days total)")

# Cache key that FullCalendar will use
fc_cache_key = f"calendar_feed:1:None:None:{september_start}:{november_end}"
print(f"\nFullCalendar cache key: {fc_cache_key}")

# Simulate deletion cache invalidation
print("\n2. DELETION CACHE INVALIDATION (Fixed Monthly Boundaries):")
print("-" * 80)

today = date(2025, 10, 6)
start_of_month = today.replace(day=1)
end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

print(f"Today: {today}")
print(f"Month boundaries: {start_of_month} to {end_of_month}")

deletion_cache_key = f"calendar_feed:1:None:None:{start_of_month}:{end_of_month}"
print(f"\nDeletion cache key: {deletion_cache_key}")

# Check if they match
print("\n3. CACHE KEY COMPARISON:")
print("-" * 80)
print(f"FullCalendar key: {fc_cache_key}")
print(f"Deletion key:     {deletion_cache_key}")
print(f"\nDo they match? {fc_cache_key == deletion_cache_key}")
print("❌ NO! They are different keys.")

# Show the problem
print("\n4. THE PROBLEM:")
print("-" * 80)
print("When user deletes an item:")
print(f"  ✅ Deletion clears: {deletion_cache_key}")
print(f"  ❌ FullCalendar still has cached: {fc_cache_key}")
print("\nResult: Page refresh shows stale data because cache wasn't invalidated!")

# Solutions
print("\n5. SOLUTIONS:")
print("-" * 80)

print("\n📋 SOLUTION A: Wildcard Cache Invalidation (RECOMMENDED)")
print("   Clear ALL calendar caches for this user regardless of date range:")
print("""
   # Get all cache keys matching pattern
   from django.core.cache import cache
   pattern = f"calendar_feed:{user_id}:*"

   # Clear all matching keys
   cache.delete_pattern(pattern)  # Requires Redis

   # OR for LocMemCache: track keys in a set
   cache_keys_set = cache.get(f'calendar_keys:{user_id}') or set()
   for key in cache_keys_set:
       cache.delete(key)
""")

print("\n📋 SOLUTION B: Expanded Range Invalidation")
print("   Clear caches for wider date ranges including neighboring months:")
print("""
   # Instead of just clearing Oct 1-31, clear:
   # - September 15 - November 15 (covers all views)
   for month_offset in range(-1, 2):  # Previous, current, next month
       start = (today.replace(day=1) + timedelta(days=32 * month_offset)).replace(day=1)
       start = start - timedelta(days=15)  # Include overlap
       end = start + timedelta(days=60)    # 60-day window

       cache_key = f"calendar_feed:{user_id}:None:None:{start}:{end}"
       cache.delete(cache_key)
""")

print("\n📋 SOLUTION C: Cache Versioning")
print("   Use a version number that increments on any change:")
print("""
   # In cache key
   version = cache.get(f'calendar_version:{user_id}') or 0
   cache_key = f"calendar_feed:{user_id}:v{version}:..."

   # On deletion
   cache.incr(f'calendar_version:{user_id}')  # All old caches now invalid
""")

print("\n📋 SOLUTION D: Short TTL + Background Refresh")
print("   Reduce cache TTL to 60 seconds instead of 5 minutes:")
print("""
   cache.set(cache_key, work_items, 60)  # 1 minute TTL

   # Accept that stale data might show for max 60 seconds
""")

print("\n" + "=" * 80)
print("RECOMMENDED FIX:")
print("=" * 80)
print("""
Use SOLUTION A (wildcard invalidation) with a cache key tracking system:

1. When caching calendar data:
   - Add cache key to a set: calendar_keys:{user_id}

2. When deleting work item:
   - Get all keys from calendar_keys:{user_id}
   - Delete each key
   - Clear the keys set

This guarantees ALL calendar caches are cleared regardless of date ranges.
""")

print("=" * 80)
