"""
Management command to clean up test users while preserving admin and OOBC staff.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from common.models import CalendarResourceBooking, WorkItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Remove test users while keeping admin and OOBC staff (users ending with .oobc)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN MODE ==='))
            self.stdout.write('No actual deletions will be performed\n')

        # Identify users to keep
        admin_user = User.objects.get(username='admin', id=1)
        oobc_staff = User.objects.filter(username__endswith='.oobc')

        self.stdout.write(self.style.SUCCESS(f'\n✓ KEEPING:'))
        self.stdout.write(f'  - Admin: {admin_user.username} (ID: {admin_user.id})')
        self.stdout.write(f'  - OOBC Staff: {oobc_staff.count()} users')

        # Identify test users to remove
        test_users = User.objects.exclude(id=admin_user.id).exclude(username__endswith='.oobc')

        self.stdout.write(self.style.WARNING(f'\n✗ REMOVING: {test_users.count()} test users\n'))

        # Check relationships
        bookings = CalendarResourceBooking.objects.filter(booked_by__in=test_users)
        work_items_with_test_assignees = WorkItem.objects.filter(assignees__in=test_users).distinct()
        work_items_created = WorkItem.objects.filter(created_by__in=test_users)

        self.stdout.write(self.style.WARNING('Related data to handle:'))
        self.stdout.write(f'  - Calendar bookings: {bookings.count()}')
        self.stdout.write(f'  - Work items with test assignees: {work_items_with_test_assignees.count()}')
        self.stdout.write(f'  - Work items created by test users: {work_items_created.count()}')

        if dry_run:
            self.stdout.write(self.style.SUCCESS('\n=== DRY RUN COMPLETE ==='))
            self.stdout.write('Run without --dry-run to perform actual deletions')
            return

        # Confirm before proceeding
        self.stdout.write(self.style.WARNING('\n⚠️  WARNING: This will delete test users and reassign their data'))
        confirm = input('Type "yes" to continue: ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Aborted.'))
            return

        self.stdout.write('\n' + '='*60)
        self.stdout.write('PROCESSING DELETIONS')
        self.stdout.write('='*60 + '\n')

        with transaction.atomic():
            # 1. Reassign calendar bookings to admin
            if bookings.exists():
                self.stdout.write(f'→ Reassigning {bookings.count()} calendar bookings to admin...')
                bookings.update(booked_by=admin_user)
                self.stdout.write(self.style.SUCCESS('  ✓ Done'))

            # 2. Remove test users from work item assignees
            if work_items_with_test_assignees.exists():
                self.stdout.write(f'→ Removing test users from {work_items_with_test_assignees.count()} work items...')
                for work_item in work_items_with_test_assignees:
                    # Remove all test user assignees
                    work_item.assignees.remove(*test_users)
                    # If no assignees left, assign to admin
                    if not work_item.assignees.exists():
                        work_item.assignees.add(admin_user)
                self.stdout.write(self.style.SUCCESS('  ✓ Done'))

            # 3. Reassign work items created by test users
            if work_items_created.exists():
                self.stdout.write(f'→ Reassigning {work_items_created.count()} work items created by test users...')
                work_items_created.update(created_by=admin_user)
                self.stdout.write(self.style.SUCCESS('  ✓ Done'))

            # 4. Delete test users
            self.stdout.write(f'\n→ Deleting {test_users.count()} test users...')
            deleted_count = 0
            for user in test_users:
                username = user.username
                user_id = user.id
                try:
                    user.delete()
                    deleted_count += 1
                    self.stdout.write(f'  ✓ Deleted: {username} (ID: {user_id})')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to delete {username}: {e}'))

        # Final summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('CLEANUP COMPLETE'))
        self.stdout.write('='*60)

        remaining_users = User.objects.count()
        self.stdout.write(f'\nDeleted: {deleted_count} test users')
        self.stdout.write(f'Remaining: {remaining_users} users (1 admin + {oobc_staff.count()} OOBC staff)')

        # Verify
        self.stdout.write(self.style.SUCCESS('\n✓ Database cleaned successfully!'))
