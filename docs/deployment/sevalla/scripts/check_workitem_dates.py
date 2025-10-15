#!/usr/bin/env python
"""Check WorkItem dates to debug calendar feed"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.work_item_model import WorkItem

# Get all work items
work_items = WorkItem.objects.all()

print(f"Total WorkItems: {work_items.count()}")
print()

for w in work_items:
    print(f"ID: {w.id}")
    print(f"  Title: {w.title}")
    print(f"  Type: {w.work_type}")
    print(f"  Status: {w.status}")
    print(f"  is_calendar_visible: {w.is_calendar_visible}")
    print(f"  start_date: {w.start_date}")
    print(f"  due_date: {w.due_date}")
    print(f"  start_time: {w.start_time}")
    print(f"  end_time: {w.end_time}")
    print(f"  Created: {w.created_at}")
    print()

# Check if dates are within October 2025
print("\n" + "="*80)
print("CALENDAR FILTER ANALYSIS")
print("="*80)
for w in work_items:
    if w.start_date or w.due_date:
        print(f"\n{w.title}:")
        print(f"  start_date: {w.start_date}")
        print(f"  due_date: {w.due_date}")

        # Check if visible in October 2025 view
        import datetime
        oct_start = datetime.date(2025, 10, 1)
        oct_end = datetime.date(2025, 10, 31)

        visible = False
        if w.start_date:
            if oct_start <= w.start_date <= oct_end:
                visible = True
                print(f"  ✅ start_date is in October 2025 range")
        if w.due_date:
            if oct_start <= w.due_date <= oct_end:
                visible = True
                print(f"  ✅ due_date is in October 2025 range")

        if not visible:
            print(f"  ❌ NOT VISIBLE in October 2025 calendar view!")
            print(f"     Dates are outside Oct 1-31, 2025 range")
    else:
        print(f"\n{w.title}:")
        print(f"  ❌ NO DATES SET! Will not appear on calendar")
