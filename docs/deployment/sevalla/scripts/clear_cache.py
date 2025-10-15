#!/usr/bin/env python
"""Clear all calendar caches"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

print("Clearing all calendar caches...")
print()

# Clear ALL cache keys that start with "calendar"
cache_keys = cache.keys('calendar*') if hasattr(cache, 'keys') else []
if cache_keys:
    print(f"Found {len(cache_keys)} calendar cache keys:")
    for key in cache_keys[:20]:  # Show first 20
        print(f"  - {key}")
    if len(cache_keys) > 20:
        print(f"  ... and {len(cache_keys) - 20} more")
    cache.delete_many(cache_keys)
    print(f"\n✅ Deleted {len(cache_keys)} cache keys")
else:
    print("No specific keys found, clearing entire cache...")
    cache.clear()
    print("✅ Cache cleared")

print("\nInvalidating calendar version for all users...")
for user in User.objects.all():
    version_key = f'calendar_version:{user.id}'
    current_version = cache.get(version_key) or 0
    new_version = current_version + 1
    cache.set(version_key, new_version, timeout=None)
    print(f"  User {user.username}: version {current_version} → {new_version}")

print("\n✅ All calendar caches invalidated!")
print("\nNow refresh your browser to see the events.")
