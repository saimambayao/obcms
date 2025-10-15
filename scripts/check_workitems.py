#!/usr/bin/env python
"""Check WorkItem database records"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.work_item_model import WorkItem

# Count total work items
total = WorkItem.objects.count()
print(f"Total WorkItems in database: {total}")
print()

if total > 0:
    print("Recent 20 WorkItems:")
    print("-" * 80)
    for w in WorkItem.objects.all().order_by('-created_at')[:20]:
        print(f"ID: {w.id}")
        print(f"  Title: {w.title}")
        print(f"  Type: {w.work_type}")
        print(f"  Status: {w.status}")
        print(f"  Created: {w.created_at}")
        print(f"  Calendar Visible: {w.is_calendar_visible}")
        print()
else:
    print("❌ NO WORK ITEMS FOUND IN DATABASE!")
    print()
    print("This explains why the calendar is empty.")
