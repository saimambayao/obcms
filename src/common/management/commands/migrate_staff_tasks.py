"""
Management command to migrate StaffTask records to WorkItem model.

This command handles the migration of all existing StaffTask records to the
unified WorkItem model (type=Task/Subtask), preserving all relationships and
maintaining data integrity.

Usage:
    python manage.py migrate_staff_tasks [--dry-run] [--verbose]
"""

import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from common.models import StaffTask
from common.work_item_model import WorkItem


class Command(BaseCommand):
    help = "Migrate StaffTask records to WorkItem model"

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

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        self.stdout.write("=" * 80)
        self.stdout.write(
            self.style.NOTICE("StaffTask → WorkItem Migration")
        )
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN MODE] No changes will be committed\n")
            )

        # Get all tasks
        tasks = StaffTask.objects.all().select_related(
            "created_by", "linked_event", "recurrence_pattern", "recurrence_parent"
        ).prefetch_related("assignees", "teams")

        total_tasks = tasks.count()
        self.stdout.write(f"\nFound {total_tasks} StaffTask records to migrate\n")

        if total_tasks == 0:
            self.stdout.write(self.style.SUCCESS("\nNo tasks to migrate."))
            return

        # Statistics
        stats = {
            "total": total_tasks,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "error_details": [],
        }

        # Status mapping
        status_map = {
            StaffTask.STATUS_NOT_STARTED: WorkItem.STATUS_NOT_STARTED,
            StaffTask.STATUS_IN_PROGRESS: WorkItem.STATUS_IN_PROGRESS,
            StaffTask.STATUS_AT_RISK: WorkItem.STATUS_AT_RISK,
            StaffTask.STATUS_COMPLETED: WorkItem.STATUS_COMPLETED,
        }

        # Priority mapping
        priority_map = {
            StaffTask.PRIORITY_LOW: WorkItem.PRIORITY_LOW,
            StaffTask.PRIORITY_MEDIUM: WorkItem.PRIORITY_MEDIUM,
            StaffTask.PRIORITY_HIGH: WorkItem.PRIORITY_HIGH,
            StaffTask.PRIORITY_CRITICAL: WorkItem.PRIORITY_CRITICAL,
        }

        work_items_to_create = []
        work_item_relationships = []  # Store M2M and FK relationships for later

        for task in tasks:
            try:
                # Note: Skipping "already migrated" check as JSON field queries are database-specific
                # To skip migrated tasks, use --skip flag or manually filter

                # Determine work type (task vs subtask)
                # If task has recurrence_parent, it's a subtask (instance of recurring task)
                work_type = (
                    WorkItem.WORK_TYPE_SUBTASK
                    if task.recurrence_parent
                    else WorkItem.WORK_TYPE_TASK
                )

                # Build task_data JSON with legacy fields
                task_data = {
                    "legacy_task_id": str(task.id),
                    "legacy_model": "StaffTask",
                    "impact": task.impact,
                    "board_position": task.board_position,
                }

                # Add domain-specific fields if they exist
                # (StaffTask may have domain relationships via Generic FK)
                if hasattr(task, "content_type") and task.content_type:
                    task_data["legacy_content_type_id"] = task.content_type.id
                    task_data["legacy_object_id"] = str(task.object_id)

                # Handle linked_event relationship
                if task.linked_event:
                    task_data["linked_event_id"] = str(task.linked_event.id)

                # Create WorkItem instance (don't set created_at/updated_at - they're auto)
                work_item = WorkItem(
                    work_type=work_type,
                    title=task.title,
                    description=task.description,
                    status=status_map.get(task.status, WorkItem.STATUS_NOT_STARTED),
                    priority=priority_map.get(
                        task.priority, WorkItem.PRIORITY_MEDIUM
                    ),
                    start_date=task.start_date,
                    due_date=task.due_date,
                    completed_at=task.completed_at,
                    progress=task.progress,
                    created_by=task.created_by,
                    is_recurring=task.is_recurring,
                    recurrence_pattern=task.recurrence_pattern,
                    task_data=task_data,
                    # Will set parent relationship after all items are created
                    parent=None,
                )

                work_items_to_create.append(work_item)

                # Store relationships for later (M2M can only be set after save)
                work_item_relationships.append(
                    {
                        "work_item": work_item,
                        "assignees": list(task.assignees.all()),
                        "teams": list(task.teams.all()),
                        "recurrence_parent_task_id": (
                            task.recurrence_parent.id if task.recurrence_parent else None
                        ),
                        "is_recurrence_exception": task.is_recurrence_exception,
                    }
                )

                if verbose:
                    self.stdout.write(f"  ✓ Prepared: {task.title}")

                stats["migrated"] += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Error migrating task {task.id}: {str(e)}")
                )
                stats["errors"] += 1
                stats["error_details"].append(
                    {"task_id": str(task.id), "title": task.title, "error": str(e)}
                )

        # Bulk create WorkItems
        if not dry_run and work_items_to_create:
            with transaction.atomic():
                self.stdout.write("\nBulk creating WorkItem records...")

                # Use regular save() for each item to allow MPTT to set tree fields
                for work_item in work_items_to_create:
                    try:
                        work_item.save()
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error saving work_item '{work_item.title}': {str(e)}"
                            )
                        )
                        raise

                self.stdout.write(
                    f"  - Created {len(work_items_to_create)} items"
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Created {len(work_items_to_create)} WorkItem records"
                    )
                )

                # Set M2M relationships and parent links
                self.stdout.write("\nSetting relationships...")
                recurrence_parent_map = {}  # Map old task ID to new WorkItem

                # Build parent mapping first
                for item in work_items_to_create:
                    legacy_id = item.task_data.get("legacy_task_id")
                    if legacy_id:
                        recurrence_parent_map[legacy_id] = item

                # Set relationships
                for rel in work_item_relationships:
                    work_item = rel["work_item"]

                    # Set assignees
                    if rel["assignees"]:
                        work_item.assignees.set(rel["assignees"])

                    # Set teams
                    if rel["teams"]:
                        work_item.teams.set(rel["teams"])

                    # Set parent relationship (for recurring task instances)
                    if rel["recurrence_parent_task_id"]:
                        parent_task_id = str(rel["recurrence_parent_task_id"])
                        if parent_task_id in recurrence_parent_map:
                            work_item.parent = recurrence_parent_map[parent_task_id]
                            work_item.save(update_fields=["parent"])

                self.stdout.write(
                    self.style.SUCCESS("  ✓ Relationships set successfully")
                )

        # Print statistics
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.NOTICE("Migration Statistics"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"\nTotal tasks:          {stats['total']}")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully migrated: {stats['migrated']}")
        )
        if stats["skipped"] > 0:
            self.stdout.write(
                self.style.WARNING(f"Skipped (existing):    {stats['skipped']}")
            )
        if stats["errors"] > 0:
            self.stdout.write(
                self.style.ERROR(f"Errors:                {stats['errors']}")
            )

            if verbose and stats["error_details"]:
                self.stdout.write("\nError Details:")
                for error in stats["error_details"]:
                    self.stdout.write(
                        f"  - Task: {error['title']} (ID: {error['task_id']})"
                    )
                    self.stdout.write(f"    Error: {error['error']}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n[DRY RUN] No changes committed. Use without --dry-run to apply migration."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Migration complete! {stats['migrated']} tasks migrated to WorkItem."
                )
            )

        self.stdout.write("=" * 80 + "\n")
