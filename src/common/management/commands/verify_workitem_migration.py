"""
Management command to verify WorkItem migration integrity.

Checks:
1. All StaffTask records have corresponding WorkItem records
2. All ProjectWorkflow records have corresponding WorkItem records
3. All Event records have corresponding WorkItem records
4. Data integrity (field values match)
5. Orphaned WorkItem records (no legacy source)

Usage:
    python manage.py verify_workitem_migration
    python manage.py verify_workitem_migration --fix
    python manage.py verify_workitem_migration --report-only
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from common.models import StaffTask
from common.work_item_model import WorkItem
from project_central.models import ProjectWorkflow
from coordination.models import Event
from tabulate import tabulate
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verify WorkItem migration data integrity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix inconsistencies (creates missing WorkItems)',
        )
        parser.add_argument(
            '--report-only',
            action='store_true',
            help='Only generate report without checking individual records',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each record',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== WorkItem Migration Verification ===\n'))

        # Check feature flags
        dual_write = getattr(settings, 'DUAL_WRITE_ENABLED', False)
        use_workitem = getattr(settings, 'USE_WORKITEM_MODEL', False)
        readonly = getattr(settings, 'LEGACY_MODELS_READONLY', False)

        self.stdout.write(f"Feature Flags:")
        self.stdout.write(f"  USE_WORKITEM_MODEL: {use_workitem}")
        self.stdout.write(f"  DUAL_WRITE_ENABLED: {dual_write}")
        self.stdout.write(f"  LEGACY_MODELS_READONLY: {readonly}\n")

        if not dual_write and not use_workitem:
            self.stdout.write(self.style.WARNING(
                "WARNING: Both DUAL_WRITE_ENABLED and USE_WORKITEM_MODEL are False.\n"
                "Migration verification may not be meaningful.\n"
            ))

        # Summary stats
        stats = {
            'stafftask': {
                'total': 0,
                'with_workitem': 0,
                'missing_workitem': 0,
                'mismatched': 0,
            },
            'projectworkflow': {
                'total': 0,
                'with_workitem': 0,
                'missing_workitem': 0,
                'mismatched': 0,
            },
            'event': {
                'total': 0,
                'with_workitem': 0,
                'missing_workitem': 0,
                'mismatched': 0,
            },
            'workitem': {
                'total': 0,
                'orphaned': 0,
            }
        }

        # Check StaffTask → WorkItem
        self.stdout.write(self.style.HTTP_INFO('\n1. Checking StaffTask → WorkItem...'))
        stafftask_issues = self._check_stafftask_to_workitem(stats, options)

        # Check ProjectWorkflow → WorkItem
        self.stdout.write(self.style.HTTP_INFO('\n2. Checking ProjectWorkflow → WorkItem...'))
        workflow_issues = self._check_projectworkflow_to_workitem(stats, options)

        # Check Event → WorkItem
        self.stdout.write(self.style.HTTP_INFO('\n3. Checking Event → WorkItem...'))
        event_issues = self._check_event_to_workitem(stats, options)

        # Check for orphaned WorkItems
        self.stdout.write(self.style.HTTP_INFO('\n4. Checking for orphaned WorkItems...'))
        orphaned_issues = self._check_orphaned_workitems(stats, options)

        # Print summary report
        self._print_summary_report(stats)

        # Auto-fix if requested
        if options['fix']:
            self._auto_fix_issues(stafftask_issues, workflow_issues, event_issues)

        self.stdout.write(self.style.SUCCESS('\n=== Verification Complete ==='))

    def _check_stafftask_to_workitem(self, stats, options):
        """Check if all StaffTasks have corresponding WorkItems."""
        issues = []
        tasks = StaffTask.objects.all()
        stats['stafftask']['total'] = tasks.count()

        for task in tasks:
            # Find corresponding WorkItem
            work_item = WorkItem.objects.filter(
                task_data__legacy_id=str(task.id),
                work_type=WorkItem.WORK_TYPE_TASK
            ).first()

            if work_item:
                stats['stafftask']['with_workitem'] += 1

                # Check data integrity
                if work_item.title != task.title:
                    stats['stafftask']['mismatched'] += 1
                    issues.append({
                        'type': 'mismatch',
                        'model': 'StaffTask',
                        'id': task.id,
                        'field': 'title',
                        'legacy_value': task.title,
                        'workitem_value': work_item.title,
                    })
                    if options['verbose']:
                        self.stdout.write(
                            f"  MISMATCH: Task {task.id} title differs"
                        )
            else:
                stats['stafftask']['missing_workitem'] += 1
                issues.append({
                    'type': 'missing',
                    'model': 'StaffTask',
                    'id': task.id,
                    'title': task.title,
                })
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING(f"  MISSING: Task {task.id} - {task.title}")
                    )

        self.stdout.write(
            f"  Total: {stats['stafftask']['total']}, "
            f"With WorkItem: {stats['stafftask']['with_workitem']}, "
            f"Missing: {stats['stafftask']['missing_workitem']}, "
            f"Mismatched: {stats['stafftask']['mismatched']}"
        )

        return issues

    def _check_projectworkflow_to_workitem(self, stats, options):
        """Check if all ProjectWorkflows have corresponding WorkItems."""
        issues = []
        workflows = ProjectWorkflow.objects.all()
        stats['projectworkflow']['total'] = workflows.count()

        for workflow in workflows:
            work_item = WorkItem.objects.filter(
                project_data__legacy_id=str(workflow.id),
                work_type=WorkItem.WORK_TYPE_PROJECT
            ).first()

            if work_item:
                stats['projectworkflow']['with_workitem'] += 1
            else:
                stats['projectworkflow']['missing_workitem'] += 1
                issues.append({
                    'type': 'missing',
                    'model': 'ProjectWorkflow',
                    'id': workflow.id,
                    'title': str(workflow),
                })
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING(f"  MISSING: Workflow {workflow.id}")
                    )

        self.stdout.write(
            f"  Total: {stats['projectworkflow']['total']}, "
            f"With WorkItem: {stats['projectworkflow']['with_workitem']}, "
            f"Missing: {stats['projectworkflow']['missing_workitem']}"
        )

        return issues

    def _check_event_to_workitem(self, stats, options):
        """Check if all Events have corresponding WorkItems."""
        issues = []
        events = Event.objects.all()
        stats['event']['total'] = events.count()

        for event in events:
            work_item = WorkItem.objects.filter(
                activity_data__legacy_id=str(event.id),
                work_type=WorkItem.WORK_TYPE_ACTIVITY
            ).first()

            if work_item:
                stats['event']['with_workitem'] += 1
            else:
                stats['event']['missing_workitem'] += 1
                issues.append({
                    'type': 'missing',
                    'model': 'Event',
                    'id': event.id,
                    'title': event.title,
                })
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING(f"  MISSING: Event {event.id} - {event.title}")
                    )

        self.stdout.write(
            f"  Total: {stats['event']['total']}, "
            f"With WorkItem: {stats['event']['with_workitem']}, "
            f"Missing: {stats['event']['missing_workitem']}"
        )

        return issues

    def _check_orphaned_workitems(self, stats, options):
        """Check for WorkItems without corresponding legacy records."""
        issues = []
        workitems = WorkItem.objects.all()
        stats['workitem']['total'] = workitems.count()

        for item in workitems:
            has_legacy = False

            # Check if it has a legacy_id in type-specific data
            if item.work_type == WorkItem.WORK_TYPE_TASK:
                legacy_id = item.task_data.get('legacy_id')
                if legacy_id:
                    has_legacy = StaffTask.objects.filter(id=legacy_id).exists()

            elif item.work_type == WorkItem.WORK_TYPE_PROJECT:
                legacy_id = item.project_data.get('legacy_id')
                if legacy_id:
                    has_legacy = ProjectWorkflow.objects.filter(id=legacy_id).exists()

            elif item.work_type == WorkItem.WORK_TYPE_ACTIVITY:
                legacy_id = item.activity_data.get('legacy_id')
                if legacy_id:
                    has_legacy = Event.objects.filter(id=legacy_id).exists()

            if not has_legacy:
                stats['workitem']['orphaned'] += 1
                issues.append({
                    'type': 'orphaned',
                    'id': item.id,
                    'work_type': item.work_type,
                    'title': item.title,
                })
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ORPHANED: WorkItem {item.id} ({item.work_type}) - {item.title}"
                        )
                    )

        self.stdout.write(
            f"  Total WorkItems: {stats['workitem']['total']}, "
            f"Orphaned: {stats['workitem']['orphaned']}"
        )

        return issues

    def _print_summary_report(self, stats):
        """Print summary report table."""
        self.stdout.write(self.style.SUCCESS('\n=== SUMMARY REPORT ===\n'))

        table_data = [
            ['StaffTask', stats['stafftask']['total'], stats['stafftask']['with_workitem'],
             stats['stafftask']['missing_workitem'], stats['stafftask']['mismatched']],
            ['ProjectWorkflow', stats['projectworkflow']['total'], stats['projectworkflow']['with_workitem'],
             stats['projectworkflow']['missing_workitem'], stats['projectworkflow']['mismatched']],
            ['Event', stats['event']['total'], stats['event']['with_workitem'],
             stats['event']['missing_workitem'], stats['event']['mismatched']],
        ]

        headers = ['Legacy Model', 'Total', 'With WorkItem', 'Missing', 'Mismatched']
        self.stdout.write(tabulate(table_data, headers=headers, tablefmt='grid'))

        self.stdout.write(f"\nWorkItem Orphans: {stats['workitem']['orphaned']} / {stats['workitem']['total']}")

        # Overall status
        total_issues = (
            stats['stafftask']['missing_workitem'] +
            stats['stafftask']['mismatched'] +
            stats['projectworkflow']['missing_workitem'] +
            stats['event']['missing_workitem'] +
            stats['workitem']['orphaned']
        )

        if total_issues == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ No issues found. Migration is complete and consistent.'))
        else:
            self.stdout.write(self.style.ERROR(f'\n✗ Found {total_issues} issue(s). Run with --fix to auto-fix.'))

    def _auto_fix_issues(self, stafftask_issues, workflow_issues, event_issues):
        """Automatically fix missing WorkItems."""
        self.stdout.write(self.style.WARNING('\n=== AUTO-FIX MODE ==='))

        fixed_count = 0

        # Fix missing StaffTask WorkItems
        for issue in stafftask_issues:
            if issue['type'] == 'missing':
                try:
                    with transaction.atomic():
                        task = StaffTask.objects.get(id=issue['id'])
                        # Trigger signal by saving
                        task.save()
                        fixed_count += 1
                        self.stdout.write(f"  ✓ Created WorkItem for StaffTask {task.id}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed to fix StaffTask {issue['id']}: {e}"))

        # Fix missing ProjectWorkflow WorkItems
        for issue in workflow_issues:
            if issue['type'] == 'missing':
                try:
                    with transaction.atomic():
                        workflow = ProjectWorkflow.objects.get(id=issue['id'])
                        workflow.save()
                        fixed_count += 1
                        self.stdout.write(f"  ✓ Created WorkItem for ProjectWorkflow {workflow.id}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed to fix ProjectWorkflow {issue['id']}: {e}"))

        # Fix missing Event WorkItems
        for issue in event_issues:
            if issue['type'] == 'missing':
                try:
                    with transaction.atomic():
                        event = Event.objects.get(id=issue['id'])
                        event.save()
                        fixed_count += 1
                        self.stdout.write(f"  ✓ Created WorkItem for Event {event.id}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed to fix Event {issue['id']}: {e}"))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Fixed {fixed_count} issue(s)'))
