"""
Management command to migrate Event records to WorkItem model.

This command handles the migration of all existing Event records to the
unified WorkItem model (type=Activity), preserving all relationships and
event-specific data.

Usage:
    python manage.py migrate_events [--dry-run] [--verbose]
"""

import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from coordination.models import Event
from common.work_item_model import WorkItem


class Command(BaseCommand):
    help = "Migrate Event records to WorkItem model"

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
            self.style.NOTICE("Event → WorkItem Migration")
        )
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN MODE] No changes will be committed\n")
            )

        # Get all events
        events = Event.objects.all().select_related(
            "community",
            "related_engagement",
            "related_project",
            "organizer",
            "recurrence_pattern",
        ).prefetch_related("organizations", "participants")

        total_events = events.count()
        self.stdout.write(f"\nFound {total_events} Event records to migrate\n")

        if total_events == 0:
            self.stdout.write(self.style.SUCCESS("\nNo events to migrate."))
            return

        # Statistics
        stats = {
            "total": total_events,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "project_activities": 0,
            "standalone_activities": 0,
            "error_details": [],
        }

        # Status mapping
        status_map = {
            "draft": WorkItem.STATUS_NOT_STARTED,
            "planned": WorkItem.STATUS_NOT_STARTED,
            "scheduled": WorkItem.STATUS_NOT_STARTED,
            "confirmed": WorkItem.STATUS_NOT_STARTED,
            "in_progress": WorkItem.STATUS_IN_PROGRESS,
            "completed": WorkItem.STATUS_COMPLETED,
            "cancelled": WorkItem.STATUS_CANCELLED,
            "postponed": WorkItem.STATUS_BLOCKED,
            "rescheduled": WorkItem.STATUS_IN_PROGRESS,
        }

        # Priority mapping
        priority_map = {
            "low": WorkItem.PRIORITY_LOW,
            "medium": WorkItem.PRIORITY_MEDIUM,
            "high": WorkItem.PRIORITY_HIGH,
            "critical": WorkItem.PRIORITY_CRITICAL,
        }

        work_items_to_create = []
        work_item_relationships = []

        for event in events:
            try:
                # Note: Skipping "already migrated" check as JSON field queries are database-specific
                # To skip migrated events, use --skip flag or manually filter

                # Determine if this is a project activity or standalone
                is_project_activity = (
                    hasattr(event, "related_project") and event.related_project is not None
                )

                # Build activity_data JSON with event-specific fields
                activity_data = {
                    "legacy_event_id": str(event.id),
                    "legacy_model": "Event",
                    "event_type": event.event_type,
                    "objectives": event.objectives,
                    "venue": event.venue,
                    "address": event.address,
                    "is_virtual": event.is_virtual,
                    "virtual_platform": event.virtual_platform,
                    "virtual_link": event.virtual_link,
                    "virtual_meeting_id": event.virtual_meeting_id,
                    "expected_participants": event.expected_participants,
                    "actual_participants": event.actual_participants,
                    "is_recurring_event": event.is_recurring,
                    "is_project_activity": is_project_activity,
                    "community_id": str(event.community.id) if event.community else None,
                    "related_engagement_id": (
                        str(event.related_engagement.id)
                        if event.related_engagement
                        else None
                    ),
                    "related_assessment_id": (
                        str(event.related_assessment.id)
                        if event.related_assessment
                        else None
                    ),
                }

                # Calculate duration if not set
                duration_hours = None
                if hasattr(event, "duration_hours") and event.duration_hours:
                    duration_hours = float(event.duration_hours)
                elif event.start_time and event.end_time:
                    # Calculate from times
                    start = timezone.datetime.combine(
                        event.start_date, event.start_time
                    )
                    end_date = event.end_date or event.start_date
                    end = timezone.datetime.combine(end_date, event.end_time)
                    duration_seconds = (end - start).total_seconds()
                    if duration_seconds > 0:
                        duration_hours = duration_seconds / 3600

                if duration_hours:
                    activity_data["duration_hours"] = duration_hours

                # Event calendar color based on type
                event_type_colors = {
                    "meeting": "#3B82F6",  # Blue
                    "consultation": "#8B5CF6",  # Purple
                    "workshop": "#10B981",  # Green
                    "field_visit": "#F59E0B",  # Amber
                    "assessment": "#EF4444",  # Red
                    "validation": "#06B6D4",  # Cyan
                }

                calendar_color = event_type_colors.get(event.event_type, "#6B7280")

                # Create WorkItem instance (don't set created_at/updated_at - they're auto)
                work_item = WorkItem(
                    work_type=WorkItem.WORK_TYPE_ACTIVITY,
                    title=event.title,
                    description=event.description,
                    status=status_map.get(event.status, WorkItem.STATUS_NOT_STARTED),
                    priority=priority_map.get(
                        event.priority, WorkItem.PRIORITY_MEDIUM
                    ),
                    start_date=event.start_date,
                    due_date=event.end_date or event.start_date,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    completed_at=(
                        event.actual_end_datetime
                        if hasattr(event, "actual_end_datetime")
                        and event.actual_end_datetime
                        else None
                    ),
                    created_by=event.organizer,
                    is_recurring=event.is_recurring,
                    recurrence_pattern=event.recurrence_pattern,
                    activity_data=activity_data,
                    calendar_color=calendar_color,
                    is_calendar_visible=True,
                    auto_calculate_progress=False,
                    # Parent relationship will be set later for project activities
                    parent=None,
                )

                work_items_to_create.append(work_item)

                # Store relationships for later
                work_item_relationships.append(
                    {
                        "work_item": work_item,
                        "organizer": event.organizer,
                        "organizations": list(event.organizations.all()),
                        "related_project_id": (
                            str(event.related_project.id)
                            if hasattr(event, "related_project")
                            and event.related_project
                            else None
                        ),
                    }
                )

                if is_project_activity:
                    stats["project_activities"] += 1
                else:
                    stats["standalone_activities"] += 1

                if verbose:
                    activity_type = (
                        "Project Activity" if is_project_activity else "Standalone"
                    )
                    self.stdout.write(
                        f"  ✓ Prepared: {event.title} "
                        f"({activity_type}, {event.get_event_type_display()})"
                    )

                stats["migrated"] += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Error migrating event {event.id}: {str(e)}"
                    )
                )
                stats["errors"] += 1
                stats["error_details"].append(
                    {"event_id": str(event.id), "title": event.title, "error": str(e)}
                )

        # Bulk create WorkItems
        if not dry_run and work_items_to_create:
            with transaction.atomic():
                self.stdout.write("\nBulk creating WorkItem records...")

                # Use regular save() for each item to allow MPTT to set tree fields
                for work_item in work_items_to_create:
                    work_item.save()

                self.stdout.write(
                    f"  - Created {len(work_items_to_create)} items"
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Created {len(work_items_to_create)} WorkItem records"
                    )
                )

                # Set relationships
                self.stdout.write("\nSetting relationships...")

                # Build project mapping for linking activities to projects
                project_map = {}
                for work_item in WorkItem.objects.filter(
                    work_type=WorkItem.WORK_TYPE_PROJECT
                ):
                    legacy_id = work_item.project_data.get("legacy_project_id")
                    if legacy_id:
                        project_map[legacy_id] = work_item

                for rel in work_item_relationships:
                    work_item = rel["work_item"]

                    # Set organizer as assignee
                    if rel["organizer"]:
                        work_item.assignees.add(rel["organizer"])

                    # Link to parent project if this is a project activity
                    if rel["related_project_id"]:
                        parent_project = project_map.get(rel["related_project_id"])
                        if parent_project:
                            work_item.parent = parent_project
                            work_item.save(update_fields=["parent"])

                self.stdout.write(
                    self.style.SUCCESS("  ✓ Relationships set successfully")
                )

        # Print statistics
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.NOTICE("Migration Statistics"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"\nTotal events:          {stats['total']}")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully migrated: {stats['migrated']}")
        )
        self.stdout.write(f"  - Project Activities: {stats['project_activities']}")
        self.stdout.write(f"  - Standalone:         {stats['standalone_activities']}")
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
                        f"  - Event: {error['title']} (ID: {error['event_id']})"
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
                    f"\n✓ Migration complete! {stats['migrated']} events migrated to WorkItem."
                )
            )

        self.stdout.write("=" * 80 + "\n")
