"""
Management command to warm RBAC permission cache.

Precomputes and caches permissions for all active users to improve
initial page load performance after login or cache invalidation.

Usage:
    python manage.py warm_rbac_cache
    python manage.py warm_rbac_cache --user-id 123
    python manage.py warm_rbac_cache --user-type moa_staff
    python manage.py warm_rbac_cache --organization-id abc-123
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from common.services.rbac_service import RBACService

User = get_user_model()


class Command(BaseCommand):
    help = 'Warm RBAC permission cache for users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Warm cache for specific user ID',
        )
        parser.add_argument(
            '--user-type',
            type=str,
            choices=['oobc_staff', 'moa_staff', 'cm_office'],
            help='Warm cache for all users of specific type',
        )
        parser.add_argument(
            '--organization-id',
            type=str,
            help='Warm cache for all users in specific organization',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of users to process (default: 100)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually warming cache',
        )

    def handle(self, *args, **options):
        start_time = timezone.now()

        # Build queryset based on options
        users = User.objects.filter(is_active=True)

        if options['user_id']:
            users = users.filter(pk=options['user_id'])
            self.stdout.write(f"Warming cache for user ID: {options['user_id']}")

        elif options['user_type']:
            users = users.filter(user_type=options['user_type'])
            self.stdout.write(f"Warming cache for user type: {options['user_type']}")

        elif options['organization_id']:
            users = users.filter(moa_organization__id=options['organization_id'])
            self.stdout.write(f"Warming cache for organization ID: {options['organization_id']}")

        else:
            self.stdout.write("Warming cache for ALL active users")

        # Apply limit
        users = users[:options['limit']]
        total_users = users.count()

        if total_users == 0:
            self.stdout.write(self.style.WARNING('No users found matching criteria'))
            return

        self.stdout.write(f"Found {total_users} users to process")

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN - No cache will be warmed'))
            for user in users:
                self.stdout.write(f"  Would warm cache for: {user.username} ({user.get_full_name()})")
            return

        # Warm cache for each user
        success_count = 0
        error_count = 0
        total_features_cached = 0

        self.stdout.write("\nWarming caches...")

        for i, user in enumerate(users, 1):
            try:
                # Get organization context
                organization = None
                if hasattr(user, 'moa_organization') and user.moa_organization:
                    organization = user.moa_organization

                # Warm cache
                features_cached = RBACService.warm_cache_for_user(user, organization)

                total_features_cached += features_cached
                success_count += 1

                # Progress indicator
                if i % 10 == 0:
                    self.stdout.write(f"  Processed {i}/{total_users} users...")

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {user.username}: {features_cached} features cached"
                    )
                )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ {user.username}: Error - {str(e)}"
                    )
                )

        # Summary
        elapsed_time = (timezone.now() - start_time).total_seconds()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Cache Warming Complete"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total users processed:     {total_users}")
        self.stdout.write(f"Successful:                {success_count}")
        self.stdout.write(f"Errors:                    {error_count}")
        self.stdout.write(f"Total features cached:     {total_features_cached}")
        self.stdout.write(f"Elapsed time:              {elapsed_time:.2f}s")

        if success_count > 0:
            avg_features = total_features_cached / success_count
            avg_time = elapsed_time / success_count
            self.stdout.write(f"Avg features per user:     {avg_features:.1f}")
            self.stdout.write(f"Avg time per user:         {avg_time:.3f}s")

        # Get cache stats
        try:
            cache_stats = RBACService.get_cache_stats()
            if 'error' not in cache_stats:
                self.stdout.write(f"\nCache Statistics:")
                self.stdout.write(f"  Total cached keys:       {cache_stats.get('total_cached_keys', 'N/A')}")
        except Exception:
            pass

        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\nCompleted with {error_count} errors. Check logs for details."
                )
            )
