"""
Legacy Model Migration Verification Management Command

This command verifies that all legacy model records (StaffTask, Event, ProjectWorkflow)
have been successfully migrated to the new WorkItem model before deletion.

Usage:
    python manage.py verify_legacy_migration
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from common.models import StaffTask, WorkItem
from coordination.models import Event
from project_central.models import ProjectWorkflow


class Command(BaseCommand):
    help = 'Verify that all legacy records have been migrated to WorkItem'

    def verify_stafftask_migration(self):
        """Verify StaffTask → WorkItem migration"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("1. StaffTask Migration Check")
        self.stdout.write("="*60)

        staff_tasks = StaffTask.objects.all()
        total_tasks = staff_tasks.count()
        matched = 0
        unmatched = []

        self.stdout.write(f"\nTotal StaffTask records: {total_tasks}")

        for task in staff_tasks:
            # Look for WorkItem with matching attributes
            work_items = WorkItem.objects.filter(
                Q(work_type='task') | Q(work_type='subtask'),
                title=task.title,
                start_date=task.start_date,
                due_date=task.due_date
            )

            self.stdout.write(f"\n  StaffTask ID {task.id}: '{task.title}'")
            self.stdout.write(f"    Start: {task.start_date}, Due: {task.due_date}")
            self.stdout.write(f"    Assigned to: {task.assigned_to}")
            self.stdout.write(f"    Status: {task.status}")

            if work_items.exists():
                wi = work_items.first()
                matched += 1
                self.stdout.write(self.style.SUCCESS(
                    f"    ✅ MIGRATED to WorkItem ID: {wi.id}"
                ))
                self.stdout.write(f"       WorkItem type: {wi.work_type}")
                self.stdout.write(f"       Assignees: {wi.assignees.count()} users")
            else:
                unmatched.append(task)
                self.stdout.write(self.style.WARNING(
                    f"    ⚠️  NO MATCHING WORKITEM FOUND!"
                ))

        self.stdout.write(f"\n  Summary: {matched}/{total_tasks} StaffTasks matched")

        return total_tasks, matched, unmatched

    def verify_event_migration(self):
        """Verify Event → WorkItem migration"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("2. Event Migration Check")
        self.stdout.write("="*60)

        events = Event.objects.all()
        total_events = events.count()
        matched = 0
        unmatched = []

        self.stdout.write(f"\nTotal Event records: {total_events}")

        for event in events:
            # Look for WorkItem with matching attributes
            work_items = WorkItem.objects.filter(
                Q(work_type='activity') | Q(work_type='sub_activity'),
                title=event.title,
                start_date=event.start_date
            )

            self.stdout.write(f"\n  Event ID {event.id}: '{event.title}'")
            self.stdout.write(f"    Start: {event.start_date}")
            if event.end_date:
                self.stdout.write(f"    End: {event.end_date}")
            self.stdout.write(f"    Type: {event.event_type}")

            if work_items.exists():
                wi = work_items.first()
                matched += 1
                self.stdout.write(self.style.SUCCESS(
                    f"    ✅ MIGRATED to WorkItem ID: {wi.id}"
                ))
                self.stdout.write(f"       WorkItem type: {wi.work_type}")
            else:
                unmatched.append(event)
                self.stdout.write(self.style.WARNING(
                    f"    ⚠️  NO MATCHING WORKITEM FOUND!"
                ))

        self.stdout.write(f"\n  Summary: {matched}/{total_events} Events matched")

        return total_events, matched, unmatched

    def verify_projectworkflow_migration(self):
        """Verify ProjectWorkflow → WorkItem migration"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("3. ProjectWorkflow Migration Check")
        self.stdout.write("="*60)

        workflows = ProjectWorkflow.objects.all()
        total_workflows = workflows.count()

        self.stdout.write(f"\nTotal ProjectWorkflow records: {total_workflows}")

        if total_workflows == 0:
            self.stdout.write(self.style.SUCCESS("  ✅ No ProjectWorkflows to migrate"))
            return total_workflows, 0, []

        matched = 0
        unmatched = []

        for workflow in workflows:
            work_items = WorkItem.objects.filter(
                Q(work_type='project') | Q(work_type='sub_project'),
                title=workflow.name
            )

            self.stdout.write(f"\n  ProjectWorkflow ID {workflow.id}: '{workflow.name}'")

            if work_items.exists():
                wi = work_items.first()
                matched += 1
                self.stdout.write(self.style.SUCCESS(
                    f"    ✅ MIGRATED to WorkItem ID: {wi.id}"
                ))
            else:
                unmatched.append(workflow)
                self.stdout.write(self.style.WARNING(
                    f"    ⚠️  NO MATCHING WORKITEM FOUND!"
                ))

        self.stdout.write(f"\n  Summary: {matched}/{total_workflows} ProjectWorkflows matched")

        return total_workflows, matched, unmatched

    def check_workitem_counts(self):
        """Display WorkItem statistics"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("4. WorkItem Statistics")
        self.stdout.write("="*60)

        total = WorkItem.objects.count()
        projects = WorkItem.objects.filter(
            Q(work_type='project') | Q(work_type='sub_project')
        ).count()
        activities = WorkItem.objects.filter(
            Q(work_type='activity') | Q(work_type='sub_activity')
        ).count()
        tasks = WorkItem.objects.filter(
            Q(work_type='task') | Q(work_type='subtask')
        ).count()

        self.stdout.write(f"\n  Total WorkItems: {total}")
        self.stdout.write(f"  - Projects: {projects}")
        self.stdout.write(f"  - Activities: {activities}")
        self.stdout.write(f"  - Tasks: {tasks}")

        return total, projects, activities, tasks

    def generate_summary(self, task_stats, event_stats, workflow_stats):
        """Generate final summary and recommendation"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("MIGRATION VERIFICATION SUMMARY")
        self.stdout.write("="*60)

        total_legacy = task_stats[0] + event_stats[0] + workflow_stats[0]
        total_matched = task_stats[1] + event_stats[1] + workflow_stats[1]

        self.stdout.write(f"\nLegacy Records:")
        self.stdout.write(f"  StaffTask: {task_stats[0]} (matched: {task_stats[1]})")
        self.stdout.write(f"  Event: {event_stats[0]} (matched: {event_stats[1]})")
        self.stdout.write(f"  ProjectWorkflow: {workflow_stats[0]} (matched: {workflow_stats[1]})")
        self.stdout.write(f"  TOTAL: {total_legacy} legacy records")

        success_rate = (100 * total_matched / total_legacy) if total_legacy > 0 else 0
        self.stdout.write(
            f"\nMigration Success Rate: {total_matched}/{total_legacy} ({success_rate:.1f}%)"
        )

        all_unmatched = task_stats[2] + event_stats[2] + workflow_stats[2]

        if all_unmatched:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️  WARNING: {len(all_unmatched)} unmatched records found!"
            ))
            self.stdout.write("\n  Unmatched records:")
            for item in all_unmatched:
                model_name = item.__class__.__name__
                title = item.title if hasattr(item, 'title') else item.name
                self.stdout.write(f"    - {model_name} ID {item.id}: '{title}'")
            self.stdout.write(self.style.ERROR(
                "\n❌ RECOMMENDATION: DO NOT DELETE LEGACY RECORDS YET"
            ))
            self.stdout.write("   Investigate unmatched records before proceeding.")
            return False
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ VERIFICATION PASSED!"))
            self.stdout.write("   All legacy records have matching WorkItem equivalents.")
            self.stdout.write(self.style.SUCCESS(
                "\n✅ RECOMMENDATION: Safe to proceed with legacy record deletion"
            ))
            self.stdout.write("\n   Next steps:")
            self.stdout.write("   1. Create database backups")
            self.stdout.write("   2. Run deletion script")
            self.stdout.write("   3. Verify calendar/UI functionality")
            return True

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write("="*60)
        self.stdout.write("LEGACY MODEL MIGRATION VERIFICATION")
        self.stdout.write("="*60)
        self.stdout.write("\nThis command verifies that all legacy records have been")
        self.stdout.write("successfully migrated to the WorkItem model.")
        self.stdout.write("\nREAD-ONLY: No data will be modified.\n")

        # Run verification checks
        task_stats = self.verify_stafftask_migration()
        event_stats = self.verify_event_migration()
        workflow_stats = self.verify_projectworkflow_migration()

        # Display WorkItem counts
        self.check_workitem_counts()

        # Generate summary and recommendation
        safe_to_delete = self.generate_summary(task_stats, event_stats, workflow_stats)

        self.stdout.write("\n" + "="*60)
        self.stdout.write("END OF VERIFICATION REPORT")
        self.stdout.write("="*60 + "\n")

        if safe_to_delete:
            self.stdout.write(self.style.SUCCESS(
                "Safe to proceed with deletion. Run: python manage.py delete_legacy_records"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "Fix unmatched records before proceeding with deletion."
            ))
