"""
Management command to populate organization field for existing records.

This is STEP 2 of the three-step migration:
1. Add nullable organization field (migration)
2. Populate organization field (this command) ✓
3. Make organization field required (migration)

Usage:
    # Dry run (no changes)
    python manage.py populate_organization_field --dry-run

    # Populate all apps
    python manage.py populate_organization_field

    # Populate specific app
    python manage.py populate_organization_field --app communities

    # Populate specific model
    python manage.py populate_organization_field --app communities --model OBCCommunity
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from organizations.utils import get_default_organization
from organizations.models.scoped import OrganizationScopedModel


class Command(BaseCommand):
    help = 'Populate organization field for existing records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Only populate models in this app (e.g., communities)',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Only populate this specific model (e.g., OBCCommunity)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        app_label = options.get('app')
        model_name = options.get('model')
        dry_run = options.get('dry_run', False)

        # Get default organization
        try:
            default_org = get_default_organization()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error getting default organization: {e}\n'
                    f'Run: python manage.py ensure_default_organization'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Using default organization: {default_org.code} (ID: {default_org.id})'
            )
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))

        # Get all models that inherit from OrganizationScopedModel
        scoped_models = []

        for app_config in apps.get_app_configs():
            if app_label and app_config.label != app_label:
                continue

            for model in app_config.get_models():
                if issubclass(model, OrganizationScopedModel) and not model._meta.abstract:
                    if model_name and model.__name__ != model_name:
                        continue
                    scoped_models.append(model)

        if not scoped_models:
            self.stdout.write(self.style.WARNING('No organization-scoped models found'))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'\nFound {len(scoped_models)} organization-scoped models\n'
            )
        )

        total_updated = 0

        for model in scoped_models:
            self.stdout.write(f'Processing {model._meta.app_label}.{model.__name__}...')

            # Count records without organization
            records_without_org = model.all_objects.filter(organization__isnull=True).count()

            if records_without_org == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ All records already have organization - skipping\n'
                    )
                )
                continue

            self.stdout.write(
                self.style.WARNING(
                    f'  Found {records_without_org} records without organization'
                )
            )

            if not dry_run:
                with transaction.atomic():
                    updated = model.all_objects.filter(
                        organization__isnull=True
                    ).update(organization=default_org)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Updated {updated} records\n'
                        )
                    )
                    total_updated += updated
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Would update {records_without_org} records (DRY RUN)\n'
                    )
                )
                total_updated += records_without_org

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n🔍 DRY RUN COMPLETE: Would have updated {total_updated} records total'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ SUCCESS: Updated {total_updated} records total'
                )
            )
