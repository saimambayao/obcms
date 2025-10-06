#!/usr/bin/env python
"""Test calendar feed endpoint directly"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from common.views.calendar import work_items_calendar_feed

User = get_user_model()

# Get first user
user = User.objects.first()
if not user:
    print("❌ No users in database!")
    sys.exit(1)

print(f"Testing calendar feed as user: {user.username}")
print()

# Create request
factory = RequestFactory()
request = factory.get('/oobc-management/calendar/work-items/feed/')
request.user = user

# Call the view
response = work_items_calendar_feed(request)

print(f"Response status: {response.status_code}")
print(f"Response content length: {len(response.content)} bytes")
print()
print("Response content:")
print(response.content.decode('utf-8'))
print()

# Parse JSON if possible
import json
try:
    data = json.loads(response.content)
    print(f"\nParsed JSON: {type(data)}")
    print(f"Number of events: {len(data)}")
    if len(data) > 0:
        print(f"\nFirst event:")
        print(json.dumps(data[0], indent=2))
except Exception as e:
    print(f"❌ Error parsing JSON: {e}")
