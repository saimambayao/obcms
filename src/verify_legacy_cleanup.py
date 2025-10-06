"""
Quick script to verify legacy records directly from database before cleanup
Run with: python verify_legacy_cleanup.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from django.db import connection
from common.models import WorkItem
# Event and ProjectWorkflow are abstract models - use raw SQL
# from coordination.models import Event
# from project_central.models import ProjectWorkflow

print("="*60)
print("LEGACY RECORD VERIFICATION")
print("="*60)

# Check raw database tables
with connection.cursor() as cursor:
    # Count StaffTask records (direct SQL - model is abstract)
    try:
        cursor.execute("SELECT COUNT(*) FROM common_stafftask")
        task_count = cursor.fetchone()[0]
        print(f"\nStaffTask records in DB: {task_count}")

        if task_count > 0:
            cursor.execute("SELECT id, title, start_date, due_date FROM common_stafftask LIMIT 5")
            print("  Sample records:")
            for row in cursor.fetchall():
                print(f"    - ID {row[0]}: {row[1]} (Start: {row[2]}, Due: {row[3]})")
    except Exception as e:
        print(f"  Error reading StaffTask: {e}")
        task_count = 0

    # Count Event records (direct SQL - model is abstract)
    try:
        cursor.execute("SELECT COUNT(*) FROM coordination_event")
        event_count = cursor.fetchone()[0]
        print(f"\nEvent records in DB: {event_count}")

        if event_count > 0:
            cursor.execute("SELECT id, title, start_date FROM coordination_event LIMIT 5")
            print("  Sample records:")
            for row in cursor.fetchall():
                print(f"    - ID {row[0]}: {row[1]} (Start: {row[2]})")
    except Exception as e:
        print(f"  Error reading Event: {e}")
        event_count = 0

    # Count ProjectWorkflow records (direct SQL - model is abstract)
    try:
        cursor.execute("SELECT COUNT(*) FROM project_central_projectworkflow")
        workflow_count = cursor.fetchone()[0]
        print(f"\nProjectWorkflow records in DB: {workflow_count}")

        if workflow_count > 0:
            cursor.execute("SELECT id, name FROM project_central_projectworkflow LIMIT 5")
            print("  Sample records:")
            for row in cursor.fetchall():
                print(f"    - ID {row[0]}: {row[1]}")
    except Exception as e:
        print(f"  Error reading ProjectWorkflow: {e}")
        workflow_count = 0

# Check WorkItem records
workitem_count = WorkItem.objects.count()
print(f"\nWorkItem records: {workitem_count}")
print(f"  - Tasks: {WorkItem.objects.filter(work_type__in=['task', 'subtask']).count()}")
print(f"  - Activities: {WorkItem.objects.filter(work_type__in=['activity', 'sub_activity']).count()}")
print(f"  - Projects: {WorkItem.objects.filter(work_type__in=['project', 'sub_project']).count()}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
total_legacy = task_count + event_count + workflow_count
print(f"\nTotal Legacy Records: {total_legacy}")
print(f"Total WorkItems: {workitem_count}")

if total_legacy == 0:
    print("\n✅ NO LEGACY RECORDS FOUND - Already cleaned up!")
elif total_legacy <= 10 and workitem_count >= total_legacy:
    print("\n✅ SAFE TO DELETE: All legacy records appear to have WorkItem equivalents")
    print("   Recommended: Create backups and proceed with deletion")
else:
    print(f"\n⚠️  CAUTION: {total_legacy} legacy records found")
    print("   Verify migration before deletion")

print("\n" + "="*60 + "\n")
