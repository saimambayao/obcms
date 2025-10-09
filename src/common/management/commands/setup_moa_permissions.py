"""Management command to set up MOA staff permissions and groups."""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from common.models import User


class Command(BaseCommand):
    help = 'Set up permissions and groups for MOA staff management'

    def handle(self, *args, **options):
        """Create MOA Coordinator group and can_approve_moa_users permission."""

        # Get or create content type for User model
        content_type = ContentType.objects.get_for_model(User)

        # Create custom permission
        permission, created = Permission.objects.get_or_create(
            codename='can_approve_moa_users',
            content_type=content_type,
            defaults={
                'name': 'Can approve MOA user registrations',
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('Created permission: can_approve_moa_users')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Permission already exists: can_approve_moa_users')
            )

        # Create MOA Coordinator group
        group, created = Group.objects.get_or_create(name='MOA Coordinator')

        if created:
            self.stdout.write(
                self.style.SUCCESS('Created group: MOA Coordinator')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Group already exists: MOA Coordinator')
            )

        # Add permission to group
        if permission not in group.permissions.all():
            group.permissions.add(permission)
            self.stdout.write(
                self.style.SUCCESS(
                    'Added can_approve_moa_users permission to MOA Coordinator group'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Permission already assigned to MOA Coordinator group'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('\n✅ MOA permissions setup complete!')
        )
        self.stdout.write('\nTo grant approval rights to a user:')
        self.stdout.write('  1. Add them to the "MOA Coordinator" group, OR')
        self.stdout.write('  2. Mark them as OOBC Executive, OR')
        self.stdout.write('  3. Make them a superuser')
