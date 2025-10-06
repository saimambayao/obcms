"""
Django management command to sync Municipal and Provincial OBC coverage records.

This command ensures that all municipalities and provinces with Barangay OBCs
have corresponding MunicipalityCoverage and ProvinceCoverage records.

Uses optimized bulk sync utilities to minimize database queries.

Usage:
    python manage.py sync_obc_coverage
    python manage.py sync_obc_coverage --dry-run
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from communities.models import OBCCommunity, MunicipalityCoverage, ProvinceCoverage
from communities.utils import bulk_refresh_municipalities, bulk_refresh_provinces
from common.models import Municipality, Province


class Command(BaseCommand):
    help = "Sync Municipal and Provincial OBC coverage records from Barangay OBCs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating records",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No records will be created\n")
            )

        # Get all Barangay OBCs
        barangay_obcs = OBCCommunity.objects.select_related(
            "barangay__municipality__province__region"
        )
        total_barangay_obcs = barangay_obcs.count()

        self.stdout.write(
            self.style.SUCCESS(f"\nFound {total_barangay_obcs} Barangay OBCs\n")
        )

        # Get all unique municipalities with Barangay OBCs
        municipalities = (
            Municipality.objects.filter(barangays__obc_communities__isnull=False)
            .distinct()
            .select_related("province__region")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {municipalities.count()} municipalities with Barangay OBCs\n"
            )
        )

        # Count existing vs new
        municipal_created = 0
        municipal_updated = 0

        for municipality in municipalities:
            existing = MunicipalityCoverage.objects.filter(
                municipality=municipality
            ).first()

            if existing:
                municipal_updated += 1
                self.stdout.write(
                    f"  ✓ Will update: {municipality.name}, {municipality.province.name}"
                )
            else:
                municipal_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  + Will create: {municipality.name}, {municipality.province.name}"
                    )
                )

        # Optimized bulk sync (only if not dry-run)
        if not dry_run:
            self.stdout.write("\n📊 Executing optimized bulk sync...")
            stats = bulk_refresh_municipalities(municipalities, sync_provincial=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Synced {stats['municipalities_synced']} municipalities"
                )
            )

        # Get all unique provinces with Barangay OBCs
        provinces = (
            Province.objects.filter(
                municipalities__barangays__obc_communities__isnull=False
            )
            .distinct()
            .select_related("region")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nFound {provinces.count()} provinces with Barangay OBCs\n"
            )
        )

        # Count existing vs new
        provincial_created = 0
        provincial_updated = 0

        for province in provinces:
            existing = ProvinceCoverage.objects.filter(province=province).first()

            if existing:
                provincial_updated += 1
                self.stdout.write(
                    f"  ✓ Will update: {province.name}, {province.region.name}"
                )
            else:
                provincial_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  + Will create: {province.name}, {province.region.name}")
                )

        # Optimized bulk sync (only if not dry-run)
        if not dry_run:
            self.stdout.write("\n📊 Executing optimized bulk provincial sync...")
            stats = bulk_refresh_provinces(provinces)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Synced {stats['provinces_synced']} provinces"
                )
            )

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("\nSUMMARY:"))
        self.stdout.write(f"  Barangay OBCs:       {total_barangay_obcs}")
        self.stdout.write(
            f"  Municipal Coverage:  {municipal_created} created, {municipal_updated} updated"
        )
        self.stdout.write(
            f"  Provincial Coverage: {provincial_created} created, {provincial_updated} updated"
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nDRY RUN MODE - No changes were made. Run without --dry-run to apply changes.\n"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✓ Sync completed successfully!\n")
            )
