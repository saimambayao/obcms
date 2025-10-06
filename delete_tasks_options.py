"""
Task Deletion Script - Options

Run from: cd src && python manage.py shell < ../delete_tasks_options.py

CHOOSE ONE OPTION BELOW:
"""

from common.models import StaffTask
from datetime import date

# ============================================
# OPTION 1: Delete ALL tasks (nuclear)
# ============================================
def delete_all_tasks():
    count = StaffTask.objects.count()
    print(f"⚠️  Will delete ALL {count} tasks")
    confirm = input("Type 'DELETE ALL' to confirm: ")
    if confirm == "DELETE ALL":
        StaffTask.objects.all().delete()
        print(f"✅ Deleted {count} tasks")
    else:
        print("❌ Cancelled")

# ============================================
# OPTION 2: Delete only today's bulk tasks
# ============================================
def delete_today_tasks():
    today = date(2025, 10, 4)
    count = StaffTask.objects.filter(created_at__date=today).count()
    print(f"⚠️  Will delete {count} tasks created on {today}")
    confirm = input("Type 'DELETE TODAY' to confirm: ")
    if confirm == "DELETE TODAY":
        StaffTask.objects.filter(created_at__date=today).delete()
        print(f"✅ Deleted {count} tasks from today")
    else:
        print("❌ Cancelled")

# ============================================
# OPTION 3: Keep only test tasks, delete rest
# ============================================
def delete_except_tests():
    test_ids = list(StaffTask.objects.filter(
        title__icontains='test'
    ).values_list('id', flat=True))

    count = StaffTask.objects.exclude(id__in=test_ids).count()
    print(f"⚠️  Will delete {count} tasks (keeping {len(test_ids)} test tasks)")
    confirm = input("Type 'DELETE NON-TEST' to confirm: ")
    if confirm == "DELETE NON-TEST":
        StaffTask.objects.exclude(id__in=test_ids).delete()
        print(f"✅ Deleted {count} tasks, kept {len(test_ids)} test tasks")
    else:
        print("❌ Cancelled")

# ============================================
# OPTION 4: Delete only standalone tasks
# ============================================
def delete_standalone_tasks():
    count = StaffTask.objects.filter(
        linked_workflow__isnull=True,
        linked_event__isnull=True
    ).count()
    print(f"⚠️  Will delete {count} standalone tasks (keep event-linked)")
    confirm = input("Type 'DELETE STANDALONE' to confirm: ")
    if confirm == "DELETE STANDALONE":
        StaffTask.objects.filter(
            linked_workflow__isnull=True,
            linked_event__isnull=True
        ).delete()
        print(f"✅ Deleted {count} standalone tasks")
    else:
        print("❌ Cancelled")


# UNCOMMENT ONE OPTION BELOW AND RUN:

# delete_all_tasks()              # Option 1: Delete everything
# delete_today_tasks()            # Option 2: Delete today's bulk (2242 tasks)
# delete_except_tests()           # Option 3: Keep test tasks only
# delete_standalone_tasks()       # Option 4: Delete 2258 standalone tasks

print("Please uncomment one option and run again")
