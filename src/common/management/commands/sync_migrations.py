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


class Command(BaseCommand):
    help = 'Synchronize migration state with existing database tables'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking for migration state mismatches...')

        # Check if ai_assistant_aioperation table exists
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'ai_assistant_aioperation'
                );
            """)
            aioperation_exists = cursor.fetchone()[0]

        if aioperation_exists:
            self.stdout.write(
                self.style.WARNING(
                    '📋 Detected existing ai_assistant tables - syncing migration state...'
                )
            )

            # Check if migrations are already applied
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM django_migrations
                        WHERE app = 'ai_assistant'
                        AND name = '0001_initial'
                    );
                """)
                migration_applied = cursor.fetchone()[0]

            if not migration_applied:
                self.stdout.write('   Faking ai_assistant.0001_initial...')
                try:
                    call_command('migrate', 'ai_assistant', '0001_initial', fake=True, verbosity=0)
                    self.stdout.write(self.style.SUCCESS('   ✅ Faked 0001_initial'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ⚠️  Could not fake 0001_initial: {e}'))

                self.stdout.write('   Faking ai_assistant.0002_initial...')
                try:
                    call_command('migrate', 'ai_assistant', '0002_initial', fake=True, verbosity=0)
                    self.stdout.write(self.style.SUCCESS('   ✅ Faked 0002_initial'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ⚠️  Could not fake 0002_initial: {e}'))

                self.stdout.write(self.style.SUCCESS('✅ Migration state synchronized'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ Migrations already in sync'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Fresh database detected - no sync needed'))
