"""
Management command to ensure default OOBC organization exists for OBCMS mode.

Usage:
    python manage.py ensure_default_organization

This command is idempotent - safe to run multiple times.
"""
from django.core.management.base import BaseCommand
from organizations.utils import get_or_create_default_organization


class Command(BaseCommand):
    help = 'Ensure default OOBC organization exists for OBCMS mode'

    def handle(self, *args, **options):
        """Execute command."""
        self.stdout.write('Checking for default organization...')

        organization, created = get_or_create_default_organization()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created default organization: {organization.code} - {organization.name}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Default organization already exists: {organization.code} - {organization.name}'
                )
            )

        # Display organization details
        self.stdout.write('\nOrganization Details:')
        self.stdout.write(f'  ID: {organization.id}')
        self.stdout.write(f'  Code: {organization.code}')
        self.stdout.write(f'  Name: {organization.name}')
        self.stdout.write(f'  Acronym: {organization.acronym}')
        self.stdout.write(f'  Type: {organization.get_org_type_display()}')
        self.stdout.write(f'  Active: {organization.is_active}')

        # Display enabled modules
        enabled_modules = []
        if organization.enable_mana:
            enabled_modules.append('MANA')
        if organization.enable_planning:
            enabled_modules.append('Planning')
        if organization.enable_budgeting:
            enabled_modules.append('Budgeting')
        if organization.enable_me:
            enabled_modules.append('M&E')
        if organization.enable_coordination:
            enabled_modules.append('Coordination')
        if organization.enable_policies:
            enabled_modules.append('Policies')

        self.stdout.write(f'  Enabled Modules: {", ".join(enabled_modules)}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Default organization ready (ID: {organization.id})'
            )
        )
