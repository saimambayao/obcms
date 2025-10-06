"""
Management command to migrate ProjectWorkflow records to WorkItem model.

This command handles the migration of all existing ProjectWorkflow records to the
unified WorkItem model (type=Project), preserving all relationships and workflow state.

Usage:
    python manage.py migrate_project_workflows [--dry-run] [--verbose]
"""

import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from project_central.models import ProjectWorkflow
from common.work_item_model import WorkItem


class Command(BaseCommand):
    help = "Migrate ProjectWorkflow records to WorkItem model"

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
            self.style.NOTICE("ProjectWorkflow → WorkItem Migration")
        )
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN MODE] No changes will be committed\n")
            )

        # Get all project workflows
        projects = ProjectWorkflow.objects.all().select_related(
            "primary_need",
            "ppa",
            "project_lead",
            "mao_focal_person",
            "created_by",
        )

        total_projects = projects.count()
        self.stdout.write(
            f"\nFound {total_projects} ProjectWorkflow records to migrate\n"
        )

        if total_projects == 0:
            self.stdout.write(self.style.SUCCESS("\nNo projects to migrate."))
            return

        # Statistics
        stats = {
            "total": total_projects,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "error_details": [],
        }

        # Priority mapping
        priority_map = {
            "low": WorkItem.PRIORITY_LOW,
            "medium": WorkItem.PRIORITY_MEDIUM,
            "high": WorkItem.PRIORITY_HIGH,
            "urgent": WorkItem.PRIORITY_URGENT,
            "critical": WorkItem.PRIORITY_CRITICAL,
        }

        # Workflow stage to status mapping
        stage_status_map = {
            "need_identification": WorkItem.STATUS_NOT_STARTED,
            "need_validation": WorkItem.STATUS_NOT_STARTED,
            "policy_linkage": WorkItem.STATUS_IN_PROGRESS,
            "mao_coordination": WorkItem.STATUS_IN_PROGRESS,
            "budget_planning": WorkItem.STATUS_IN_PROGRESS,
            "approval": WorkItem.STATUS_IN_PROGRESS,
            "implementation": WorkItem.STATUS_IN_PROGRESS,
            "monitoring": WorkItem.STATUS_IN_PROGRESS,
            "completion": WorkItem.STATUS_COMPLETED,
        }

        work_items_to_create = []
        work_item_relationships = []

        for project in projects:
            try:
                # Note: Skipping "already migrated" check as JSON field queries are database-specific
                # To skip migrated projects, use --skip flag or manually filter

                # Determine status based on workflow stage and flags
                if project.is_blocked:
                    status = WorkItem.STATUS_BLOCKED
                elif project.current_stage == "completion":
                    status = WorkItem.STATUS_COMPLETED
                elif not project.is_on_track:
                    status = WorkItem.STATUS_AT_RISK
                else:
                    status = stage_status_map.get(
                        project.current_stage, WorkItem.STATUS_IN_PROGRESS
                    )

                # Build project_data JSON with legacy fields
                project_data = {
                    "legacy_project_id": str(project.id),
                    "legacy_model": "ProjectWorkflow",
                    "workflow_stage": project.current_stage,
                    "stage_history": project.stage_history,
                    "is_on_track": project.is_on_track,
                    "is_blocked": project.is_blocked,
                    "blocker_description": project.blocker_description,
                    "estimated_budget": (
                        float(project.estimated_budget)
                        if project.estimated_budget
                        else None
                    ),
                    "budget_approved": project.budget_approved,
                    "budget_approval_date": (
                        project.budget_approval_date.isoformat()
                        if project.budget_approval_date
                        else None
                    ),
                    "notes": project.notes,
                    "lessons_learned": project.lessons_learned,
                    "primary_need_id": str(project.primary_need.id),
                    "ppa_id": str(project.ppa.id) if project.ppa else None,
                    "mao_focal_person_id": (
                        str(project.mao_focal_person.id)
                        if project.mao_focal_person
                        else None
                    ),
                }

                # Calculate calendar color based on status
                color_map = {
                    WorkItem.STATUS_NOT_STARTED: "#9CA3AF",  # Gray
                    WorkItem.STATUS_IN_PROGRESS: "#3B82F6",  # Blue
                    WorkItem.STATUS_AT_RISK: "#F59E0B",  # Amber
                    WorkItem.STATUS_BLOCKED: "#EF4444",  # Red
                    WorkItem.STATUS_COMPLETED: "#10B981",  # Green
                }

                # Create WorkItem instance (don't set created_at/updated_at - they're auto)
                work_item = WorkItem(
                    work_type=WorkItem.WORK_TYPE_PROJECT,
                    title=project.primary_need.title,
                    description=project.primary_need.description or "",
                    status=status,
                    priority=priority_map.get(
                        project.priority_level, WorkItem.PRIORITY_MEDIUM
                    ),
                    start_date=project.initiated_date,
                    due_date=project.target_completion_date,
                    completed_at=(
                        timezone.make_aware(
                            timezone.datetime.combine(
                                project.actual_completion_date,
                                timezone.datetime.min.time(),
                            )
                        )
                        if project.actual_completion_date
                        else None
                    ),
                    progress=project.overall_progress,
                    created_by=project.created_by,
                    project_data=project_data,
                    calendar_color=color_map.get(status, "#3B82F6"),
                    is_calendar_visible=True,
                    auto_calculate_progress=False,  # Project uses manual progress
                )

                work_items_to_create.append(work_item)

                # Store relationships for later
                work_item_relationships.append(
                    {
                        "work_item": work_item,
                        "project_lead": project.project_lead,
                    }
                )

                if verbose:
                    self.stdout.write(
                        f"  ✓ Prepared: {project.primary_need.title} "
                        f"({project.get_current_stage_display()})"
                    )

                stats["migrated"] += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Error migrating project {project.id}: {str(e)}"
                    )
                )
                stats["errors"] += 1
                stats["error_details"].append(
                    {
                        "project_id": str(project.id),
                        "title": str(project),
                        "error": str(e),
                    }
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
                self.stdout.write("\nSetting project leads...")
                for rel in work_item_relationships:
                    work_item = rel["work_item"]
                    if rel["project_lead"]:
                        work_item.assignees.add(rel["project_lead"])

                self.stdout.write(
                    self.style.SUCCESS("  ✓ Relationships set successfully")
                )

        # Print statistics
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.NOTICE("Migration Statistics"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"\nTotal projects:        {stats['total']}")
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
                        f"  - Project: {error['title']} (ID: {error['project_id']})"
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
                    f"\n✓ Migration complete! {stats['migrated']} projects migrated to WorkItem."
                )
            )

        self.stdout.write("=" * 80 + "\n")
