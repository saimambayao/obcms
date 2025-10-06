"""
Legacy Model Migration Verification Script

This script verifies that all legacy model records (StaffTask, Event, ProjectWorkflow)
have been successfully migrated to the new WorkItem model before deletion.

Safety: This is a READ-ONLY verification script. It does not modify any data.
"""

from common.models import StaffTask, WorkItem
from coordination.models import Event
from project_central.models import ProjectWorkflow
import json
from django.db.models import Q


def verify_stafftask_migration():
    """Verify StaffTask → WorkItem migration"""
    print("\n" + "="*60)
    print("1. StaffTask Migration Check")
    print("="*60)

    staff_tasks = StaffTask.objects.all()
    total_tasks = staff_tasks.count()
    matched = 0
    unmatched = []

    print(f"\nTotal StaffTask records: {total_tasks}")

    for task in staff_tasks:
        # Look for WorkItem with matching attributes
        work_items = WorkItem.objects.filter(
            Q(work_type='task') | Q(work_type='subtask'),
            title=task.title,
            start_date=task.start_date,
            due_date=task.due_date
        )

        print(f"\n  StaffTask ID {task.id}: '{task.title}'")
        print(f"    Start: {task.start_date}, Due: {task.due_date}")
        print(f"    Assigned to: {task.assigned_to}")
        print(f"    Status: {task.status}")

        if work_items.exists():
            wi = work_items.first()
            matched += 1
            print(f"    ✅ MIGRATED to WorkItem ID: {wi.id}")
            print(f"       WorkItem type: {wi.work_type}")
            print(f"       Assignees: {wi.assignees.count()} users")
        else:
            unmatched.append(task)
            print(f"    ⚠️  NO MATCHING WORKITEM FOUND!")

    print(f"\n  Summary: {matched}/{total_tasks} StaffTasks matched")

    return total_tasks, matched, unmatched


def verify_event_migration():
    """Verify Event → WorkItem migration"""
    print("\n" + "="*60)
    print("2. Event Migration Check")
    print("="*60)

    events = Event.objects.all()
    total_events = events.count()
    matched = 0
    unmatched = []

    print(f"\nTotal Event records: {total_events}")

    for event in events:
        # Look for WorkItem with matching attributes
        work_items = WorkItem.objects.filter(
            Q(work_type='activity') | Q(work_type='sub_activity'),
            title=event.title,
            start_date=event.start_date
        )

        print(f"\n  Event ID {event.id}: '{event.title}'")
        print(f"    Start: {event.start_date}")
        if event.end_date:
            print(f"    End: {event.end_date}")
        print(f"    Type: {event.event_type}")

        if work_items.exists():
            wi = work_items.first()
            matched += 1
            print(f"    ✅ MIGRATED to WorkItem ID: {wi.id}")
            print(f"       WorkItem type: {wi.work_type}")
        else:
            unmatched.append(event)
            print(f"    ⚠️  NO MATCHING WORKITEM FOUND!")

    print(f"\n  Summary: {matched}/{total_events} Events matched")

    return total_events, matched, unmatched


def verify_projectworkflow_migration():
    """Verify ProjectWorkflow → WorkItem migration"""
    print("\n" + "="*60)
    print("3. ProjectWorkflow Migration Check")
    print("="*60)

    workflows = ProjectWorkflow.objects.all()
    total_workflows = workflows.count()

    print(f"\nTotal ProjectWorkflow records: {total_workflows}")

    if total_workflows == 0:
        print("  ✅ No ProjectWorkflows to migrate")
        return total_workflows, 0, []

    matched = 0
    unmatched = []

    for workflow in workflows:
        work_items = WorkItem.objects.filter(
            Q(work_type='project') | Q(work_type='sub_project'),
            title=workflow.name
        )

        print(f"\n  ProjectWorkflow ID {workflow.id}: '{workflow.name}'")

        if work_items.exists():
            wi = work_items.first()
            matched += 1
            print(f"    ✅ MIGRATED to WorkItem ID: {wi.id}")
        else:
            unmatched.append(workflow)
            print(f"    ⚠️  NO MATCHING WORKITEM FOUND!")

    print(f"\n  Summary: {matched}/{total_workflows} ProjectWorkflows matched")

    return total_workflows, matched, unmatched


def check_workitem_counts():
    """Display WorkItem statistics"""
    print("\n" + "="*60)
    print("4. WorkItem Statistics")
    print("="*60)

    total = WorkItem.objects.count()
    projects = WorkItem.objects.filter(Q(work_type='project') | Q(work_type='sub_project')).count()
    activities = WorkItem.objects.filter(Q(work_type='activity') | Q(work_type='sub_activity')).count()
    tasks = WorkItem.objects.filter(Q(work_type='task') | Q(work_type='subtask')).count()

    print(f"\n  Total WorkItems: {total}")
    print(f"  - Projects: {projects}")
    print(f"  - Activities: {activities}")
    print(f"  - Tasks: {tasks}")

    return total, projects, activities, tasks


def generate_summary(task_stats, event_stats, workflow_stats):
    """Generate final summary and recommendation"""
    print("\n" + "="*60)
    print("MIGRATION VERIFICATION SUMMARY")
    print("="*60)

    total_legacy = task_stats[0] + event_stats[0] + workflow_stats[0]
    total_matched = task_stats[1] + event_stats[1] + workflow_stats[1]

    print(f"\nLegacy Records:")
    print(f"  StaffTask: {task_stats[0]} (matched: {task_stats[1]})")
    print(f"  Event: {event_stats[0]} (matched: {event_stats[1]})")
    print(f"  ProjectWorkflow: {workflow_stats[0]} (matched: {workflow_stats[1]})")
    print(f"  TOTAL: {total_legacy} legacy records")

    print(f"\nMigration Success Rate: {total_matched}/{total_legacy} ({100*total_matched/total_legacy if total_legacy > 0 else 0:.1f}%)")

    all_unmatched = task_stats[2] + event_stats[2] + workflow_stats[2]

    if all_unmatched:
        print(f"\n⚠️  WARNING: {len(all_unmatched)} unmatched records found!")
        print("\n  Unmatched records:")
        for item in all_unmatched:
            model_name = item.__class__.__name__
            print(f"    - {model_name} ID {item.id}: '{item.title if hasattr(item, 'title') else item.name}'")
        print("\n❌ RECOMMENDATION: DO NOT DELETE LEGACY RECORDS YET")
        print("   Investigate unmatched records before proceeding.")
        return False
    else:
        print("\n✅ VERIFICATION PASSED!")
        print("   All legacy records have matching WorkItem equivalents.")
        print("\n✅ RECOMMENDATION: Safe to proceed with legacy record deletion")
        print("   Next steps:")
        print("   1. Create database backups")
        print("   2. Run deletion script")
        print("   3. Verify calendar/UI functionality")
        return True


def main():
    """Main verification routine"""
    print("="*60)
    print("LEGACY MODEL MIGRATION VERIFICATION")
    print("="*60)
    print("\nThis script verifies that all legacy records have been")
    print("successfully migrated to the WorkItem model.")
    print("\nREAD-ONLY: No data will be modified.\n")

    # Run verification checks
    task_stats = verify_stafftask_migration()
    event_stats = verify_event_migration()
    workflow_stats = verify_projectworkflow_migration()

    # Display WorkItem counts
    check_workitem_counts()

    # Generate summary and recommendation
    safe_to_delete = generate_summary(task_stats, event_stats, workflow_stats)

    print("\n" + "="*60)
    print("END OF VERIFICATION REPORT")
    print("="*60 + "\n")

    return safe_to_delete


if __name__ == "__main__":
    # This allows running as a Django management command
    import django
    import os
    import sys

    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
    django.setup()

    main()
