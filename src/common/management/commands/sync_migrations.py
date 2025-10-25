"""
Django management command to synchronize migration state with database.

This command checks if tables exist in the database but migrations are not marked
as applied. If so, it fakes the migrations to sync the state without actually
running the SQL.

This is useful when:
- Migrations were run directly on the database
- Migration files were added after tables were created
- Recovering from migration conflicts
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
from django.apps import apps
from django.db.migrations.loader import MigrationLoader
from django.utils import timezone


class Command(BaseCommand):
    help = 'Synchronize migration state with existing database tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be done without making any changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  DRY RUN MODE - No changes will be made'))
            self.stdout.write('')

        self.stdout.write('🔍 Checking for migration state mismatches...')

        # Get all tables from database using Django's introspection API
        # This works across SQLite, PostgreSQL, MySQL, etc.
        with connection.cursor() as cursor:
            all_tables = connection.introspection.table_names(cursor)
            # Filter out Django system tables and PostGIS tables
            existing_tables = {
                table for table in all_tables
                if table not in ('django_migrations', 'spatial_ref_sys')
            }

        if not existing_tables:
            self.stdout.write(self.style.SUCCESS('✅ Fresh database detected - no sync needed'))
            return

        self.stdout.write(f'   Found {len(existing_tables)} existing tables')

        # Get all Django apps
        apps_to_check = {}
        for app_config in apps.get_app_configs():
            if app_config.name.startswith('django.'):
                continue  # Skip Django built-in apps

            app_label = app_config.label
            # Get models for this app
            models = app_config.get_models()
            for model in models:
                table_name = model._meta.db_table
                if table_name in existing_tables:
                    if app_label not in apps_to_check:
                        apps_to_check[app_label] = []
                    apps_to_check[app_label].append(table_name)

        if not apps_to_check:
            self.stdout.write(self.style.SUCCESS('✅ All migrations in sync'))
            return

        # Check and fake migrations for each app
        synced_apps = []
        loader = MigrationLoader(connection)

        for app_label, tables in apps_to_check.items():
            # Check if migrations are already applied
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM django_migrations
                    WHERE app = %s
                    ORDER BY name;
                """, [app_label])
                applied_migrations = {row[0] for row in cursor.fetchall()}

            # Get all migrations for this app from migration files
            all_migrations = {key[1] for key in loader.graph.nodes if key[0] == app_label}

            # Find unapplied migrations
            unapplied_migrations = all_migrations - applied_migrations

            if unapplied_migrations:
                self.stdout.write(
                    self.style.WARNING(
                        f'📋 {app_label}: Found {len(tables)} tables but {len(unapplied_migrations)} unapplied migrations'
                    )
                )
                self.stdout.write(f'   Unapplied: {", ".join(sorted(unapplied_migrations))}')

                if dry_run:
                    self.stdout.write(f'   [DRY RUN] Would fake unapplied migrations for {app_label}')
                    synced_apps.append(app_label)
                else:
                    # Fake unapplied migrations for this app - one at a time to handle state errors
                    try:
                        self.stdout.write(f'   Faking unapplied migrations for {app_label}...')
                        # Fake each migration individually to avoid state inconsistencies
                        sorted_migrations = sorted(unapplied_migrations)
                        for migration_name in sorted_migrations:
                            try:
                                call_command('migrate', app_label, migration_name, fake=True, verbosity=0)
                                self.stdout.write(f'     ✓ Faked {migration_name}')
                            except KeyError as ke:
                                # Known issue with field removal in migration state
                                # If KeyError occurs, the field was already removed from database
                                # Safe to mark as faked since table structure is correct
                                self.stdout.write(self.style.WARNING(f'     ⚠ Skipped {migration_name} (state error: {ke})'))
                                # Manually mark as applied using timezone.now() (database-agnostic)
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                                        [app_label, migration_name, timezone.now()]
                                    )
                            except Exception as me:
                                self.stdout.write(self.style.ERROR(f'     ✗ Failed to fake {migration_name}: {me}'))
                                raise
                        synced_apps.append(app_label)
                        self.stdout.write(self.style.SUCCESS(f'   ✅ Synced {app_label}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'   ⚠️  Error syncing {app_label}: {e}'))

        if synced_apps:
            status_msg = f'✅ Migration state {"would be" if dry_run else ""} synchronized for {len(synced_apps)} apps: {", ".join(synced_apps)}'
            self.stdout.write(self.style.SUCCESS(status_msg.strip()))
        else:
            self.stdout.write(self.style.SUCCESS('✅ All migrations already in sync'))

        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('⚠️  DRY RUN MODE - No changes were made'))
