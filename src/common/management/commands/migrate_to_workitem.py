"""
Unified orchestrator command for migrating all legacy work models to WorkItem.

This command coordinates the migration of StaffTask, ProjectWorkflow, and Event
records to the unified WorkItem model in the correct order to preserve all
hierarchical relationships.

Migration Order:
1. ProjectWorkflow → WorkItem (Projects) - Top-level items
2. Event → WorkItem (Activities) - Link to Projects
3. StaffTask → WorkItem (Tasks) - Link to Projects/Activities

Usage:
    python manage.py migrate_to_workitem [--dry-run] [--verbose] [--skip-projects] [--skip-events] [--skip-tasks]
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from common.work_item_model import WorkItem
from project_central.models import ProjectWorkflow
from coordination.models import Event
from common.models import StaffTask


class Command(BaseCommand):
    help = "Unified migration of StaffTask, ProjectWorkflow, and Event to WorkItem model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview migration without committing changes",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Display detailed migration information",
        )
        parser.add_argument(
            "--skip-projects",
            action="store_true",
            help="Skip ProjectWorkflow migration",
        )
        parser.add_argument(
            "--skip-events",
            action="store_true",
            help="Skip Event migration",
        )
        parser.add_argument(
            "--skip-tasks",
            action="store_true",
            help="Skip StaffTask migration",
        )
        parser.add_argument(
            "--rollback",
            action="store_true",
            help="Delete all migrated WorkItem records (use with caution!)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbose"]
        skip_projects = options["skip_projects"]
        skip_events = options["skip_events"]
        skip_tasks = options["skip_tasks"]
        rollback = options["rollback"]

        # Handle rollback
        if rollback:
            self.handle_rollback(dry_run, verbose)
            return

        self.stdout.write("=" * 80)
        self.stdout.write(
            self.style.NOTICE("Unified Work Hierarchy Migration")
        )
        self.stdout.write(self.style.NOTICE("Legacy Models → WorkItem"))
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN MODE] No changes will be committed\n")
            )

        # Display pre-migration statistics
        self.display_pre_migration_stats()

        # Migration sequence
        migration_steps = []

        if not skip_projects:
            migration_steps.append(
                {
                    "name": "ProjectWorkflow → WorkItem (Projects)",
                    "command": "migrate_project_workflows",
                    "order": 1,
                }
            )

        if not skip_events:
            migration_steps.append(
                {
                    "name": "Event → WorkItem (Activities)",
                    "command": "migrate_events",
                    "order": 2,
                }
            )

        if not skip_tasks:
            migration_steps.append(
                {
                    "name": "StaffTask → WorkItem (Tasks)",
                    "command": "migrate_staff_tasks",
                    "order": 3,
                }
            )

        if not migration_steps:
            self.stdout.write(
                self.style.WARNING(
                    "\nAll migrations skipped. Nothing to do."
                )
            )
            return

        # Execute migrations in order
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.NOTICE("Migration Sequence")
        )
        self.stdout.write("=" * 80 + "\n")

        for step in migration_steps:
            self.stdout.write(
                f"\n[Step {step['order']}/{len(migration_steps)}] {step['name']}"
            )
            self.stdout.write("-" * 80 + "\n")

            try:
                # Build command arguments
                cmd_args = []
                if dry_run:
                    cmd_args.append("--dry-run")
                if verbose:
                    cmd_args.append("--verbose")

                # Execute migration command
                call_command(step["command"], *cmd_args)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"\n✗ Migration step failed: {step['name']}"
                    )
                )
                self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
                self.stdout.write(
                    self.style.WARNING(
                        "\nMigration aborted. Please fix errors and retry."
                    )
                )
                return

        # Display post-migration statistics
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.NOTICE("Post-Migration Summary")
        )
        self.stdout.write("=" * 80 + "\n")

        self.display_post_migration_stats(dry_run)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n[DRY RUN] No changes committed. Use without --dry-run to apply migration."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "\n✓ Unified migration complete! All legacy models migrated to WorkItem."
                )
            )
            self.stdout.write(
                "\nNext Steps:"
            )
            self.stdout.write(
                "  1. Verify data integrity: python manage.py verify_workitem_migration"
            )
            self.stdout.write(
                "  2. Test WorkItem functionality in development"
            )
            self.stdout.write(
                "  3. Update views/templates to use WorkItem"
            )
            self.stdout.write(
                "  4. Deprecate legacy models (Phase 3)"
            )

        self.stdout.write("\n" + "=" * 80 + "\n")

    def display_pre_migration_stats(self):
        """Display statistics before migration."""
        self.stdout.write("\nPre-Migration Statistics:")
        self.stdout.write("-" * 80)

        # Legacy model counts
        projects_count = ProjectWorkflow.objects.count()
        events_count = Event.objects.count()
        tasks_count = StaffTask.objects.count()
        total_legacy = projects_count + events_count + tasks_count

        self.stdout.write(f"\nLegacy Models:")
        self.stdout.write(f"  - ProjectWorkflow: {projects_count}")
        self.stdout.write(f"  - Event:           {events_count}")
        self.stdout.write(f"  - StaffTask:       {tasks_count}")
        self.stdout.write(f"  - Total:           {total_legacy}")

        # Existing WorkItem counts
        work_items_count = WorkItem.objects.count()
        projects_migrated = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_PROJECT
        ).count()
        activities_migrated = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_ACTIVITY
        ).count()
        tasks_migrated = WorkItem.objects.filter(
            work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
        ).count()

        self.stdout.write(f"\nExisting WorkItem Records:")
        self.stdout.write(f"  - Projects:   {projects_migrated}")
        self.stdout.write(f"  - Activities: {activities_migrated}")
        self.stdout.write(f"  - Tasks:      {tasks_migrated}")
        self.stdout.write(f"  - Total:      {work_items_count}")
        self.stdout.write("")

    def display_post_migration_stats(self, dry_run=False):
        """Display statistics after migration."""
        if dry_run:
            self.stdout.write("\n(Statistics would be displayed here after actual migration)")
            return

        # WorkItem counts by type
        total = WorkItem.objects.count()
        projects = WorkItem.objects.filter(
            work_type__in=[WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT]
        ).count()
        activities = WorkItem.objects.filter(
            work_type__in=[
                WorkItem.WORK_TYPE_ACTIVITY,
                WorkItem.WORK_TYPE_SUB_ACTIVITY,
            ]
        ).count()
        tasks = WorkItem.objects.filter(
            work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
        ).count()

        self.stdout.write(f"\nWorkItem Records by Type:")
        self.stdout.write(f"  - Projects:   {projects}")
        self.stdout.write(f"  - Activities: {activities}")
        self.stdout.write(f"  - Tasks:      {tasks}")
        self.stdout.write(f"  - Total:      {total}")

        # Hierarchy statistics
        root_items = WorkItem.objects.filter(parent__isnull=True).count()
        child_items = WorkItem.objects.filter(parent__isnull=False).count()

        self.stdout.write(f"\nHierarchy:")
        self.stdout.write(f"  - Root items:  {root_items}")
        self.stdout.write(f"  - Child items: {child_items}")

        # Status distribution
        status_counts = {}
        for status, _ in WorkItem.STATUS_CHOICES:
            count = WorkItem.objects.filter(status=status).count()
            if count > 0:
                status_counts[status] = count

        self.stdout.write(f"\nStatus Distribution:")
        for status, count in status_counts.items():
            status_display = dict(WorkItem.STATUS_CHOICES)[status]
            self.stdout.write(f"  - {status_display}: {count}")

        # Calendar integration
        calendar_visible = WorkItem.objects.filter(is_calendar_visible=True).count()
        recurring = WorkItem.objects.filter(is_recurring=True).count()

        self.stdout.write(f"\nCalendar Integration:")
        self.stdout.write(f"  - Calendar visible: {calendar_visible}")
        self.stdout.write(f"  - Recurring items:  {recurring}")

    def handle_rollback(self, dry_run, verbose):
        """Rollback migration by deleting migrated WorkItem records."""
        self.stdout.write("=" * 80)
        self.stdout.write(
            self.style.WARNING("ROLLBACK: Delete Migrated WorkItem Records")
        )
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN MODE] No changes will be committed\n")
            )

        # Count records to delete
        migrated_projects = WorkItem.objects.filter(
            project_data__legacy_model="ProjectWorkflow"
        ).count()
        migrated_events = WorkItem.objects.filter(
            activity_data__legacy_model="Event"
        ).count()
        migrated_tasks = WorkItem.objects.filter(
            task_data__legacy_model="StaffTask"
        ).count()
        total_to_delete = migrated_projects + migrated_events + migrated_tasks

        self.stdout.write(f"\nRecords to delete:")
        self.stdout.write(f"  - Migrated Projects:   {migrated_projects}")
        self.stdout.write(f"  - Migrated Activities: {migrated_events}")
        self.stdout.write(f"  - Migrated Tasks:      {migrated_tasks}")
        self.stdout.write(self.style.WARNING(f"  - Total:               {total_to_delete}"))

        if total_to_delete == 0:
            self.stdout.write(
                self.style.SUCCESS("\nNo migrated records found. Nothing to rollback.")
            )
            return

        # Confirm deletion (in non-dry-run mode)
        if not dry_run:
            self.stdout.write(
                self.style.ERROR(
                    f"\n⚠ WARNING: This will permanently delete {total_to_delete} WorkItem records!"
                )
            )
            confirm = input("\nType 'DELETE' to confirm rollback: ")

            if confirm != "DELETE":
                self.stdout.write(
                    self.style.WARNING("\nRollback cancelled.")
                )
                return

            # Execute deletion
            with transaction.atomic():
                self.stdout.write("\nDeleting migrated WorkItem records...")

                deleted_projects = WorkItem.objects.filter(
                    project_data__legacy_model="ProjectWorkflow"
                ).delete()

                deleted_events = WorkItem.objects.filter(
                    activity_data__legacy_model="Event"
                ).delete()

                deleted_tasks = WorkItem.objects.filter(
                    task_data__legacy_model="StaffTask"
                ).delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Rollback complete! Deleted {total_to_delete} WorkItem records."
                    )
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"\n[DRY RUN] Would delete {total_to_delete} WorkItem records."
                )
            )

        self.stdout.write("=" * 80 + "\n")
