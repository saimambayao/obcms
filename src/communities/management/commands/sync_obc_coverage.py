"""
Django management command to sync Municipal and Provincial OBC coverage records.

This command ensures that all municipalities and provinces with Barangay OBCs
have corresponding MunicipalityCoverage and ProvinceCoverage records.

Usage:
    python manage.py sync_obc_coverage
    python manage.py sync_obc_coverage --dry-run
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from communities.models import OBCCommunity, MunicipalityCoverage, ProvinceCoverage
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

        # Sync Municipal Coverage
        municipal_created = 0
        municipal_updated = 0

        for municipality in municipalities:
            existing = MunicipalityCoverage.objects.filter(
                municipality=municipality
            ).first()

            if existing:
                if not dry_run:
                    existing.refresh_from_communities()
                municipal_updated += 1
                self.stdout.write(
                    f"  ✓ Updated: {municipality.name}, {municipality.province.name}"
                )
            else:
                if not dry_run:
                    MunicipalityCoverage.sync_for_municipality(municipality)
                municipal_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  + Created: {municipality.name}, {municipality.province.name}"
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

        # Sync Provincial Coverage
        provincial_created = 0
        provincial_updated = 0

        for province in provinces:
            existing = ProvinceCoverage.objects.filter(province=province).first()

            if existing:
                if not dry_run:
                    existing.refresh_from_municipalities()
                provincial_updated += 1
                self.stdout.write(
                    f"  ✓ Updated: {province.name}, {province.region.name}"
                )
            else:
                if not dry_run:
                    ProvinceCoverage.sync_for_province(province)
                provincial_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  + Created: {province.name}, {province.region.name}")
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
