"""
Management command to fix OBC population data.

This command corrects the incorrect assumption that estimated_obc_population
equals total_barangay_population. OBC population is a SUBSET and must be
researched separately.
"""

from django.core.management.base import BaseCommand
from django.db import transaction, models
from communities.models import OBCCommunity, MunicipalityCoverage


class Command(BaseCommand):
    help = "Fix OBC population data: set estimated_obc_population to NULL (requires research)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be changed without saving",
        )
        parser.add_argument(
            "--also-fix-municipal",
            action="store_true",
            help="Also refresh municipal coverage aggregates after fixing barangay data",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        also_fix_municipal = options["also_fix_municipal"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be saved"))

        # Find all OBC communities where estimated_obc_population equals total_barangay_population
        # This indicates incorrect auto-generation
        incorrect_communities = OBCCommunity.objects.filter(
            estimated_obc_population__isnull=False,
            total_barangay_population__isnull=False,
            estimated_obc_population=models.F('total_barangay_population')
        )

        total_count = incorrect_communities.count()

        self.stdout.write(
            self.style.WARNING(
                f"\nFound {total_count} OBC communities with incorrect population data"
            )
        )
        self.stdout.write(
            "These have estimated_obc_population = total_barangay_population (incorrect assumption)"
        )

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("\n✓ No incorrect records found!"))
            return

        # Show sample of what will be changed
        sample = incorrect_communities[:5]
        self.stdout.write("\nSample of records to be corrected:")
        self.stdout.write("-" * 80)
        for obc in sample:
            self.stdout.write(
                f"  {obc.barangay.name}, {obc.barangay.municipality.name}"
            )
            self.stdout.write(
                f"    Current: estimated_obc={obc.estimated_obc_population}, "
                f"total={obc.total_barangay_population}"
            )
            self.stdout.write(
                f"    Will set: estimated_obc=NULL (requires research), "
                f"total={obc.total_barangay_population} (unchanged)"
            )
            self.stdout.write("")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nDRY RUN: Would correct {total_count} OBC communities"
                )
            )
            return

        # Ask for confirmation
        self.stdout.write(
            self.style.WARNING(
                f"\nThis will set estimated_obc_population to NULL for {total_count} communities."
            )
        )
        self.stdout.write(
            "The OBC population must be researched/assessed separately from total barangay population."
        )

        confirm = input("\nProceed with correction? (yes/no): ")
        if confirm.lower() not in ["yes", "y"]:
            self.stdout.write(self.style.ERROR("Aborted."))
            return

        # Fix the data
        with transaction.atomic():
            # Also fix the legacy 'population' field
            updated = incorrect_communities.update(
                estimated_obc_population=None,
                population=None,
                notes=models.F('notes') + ' | OBC population corrected: set to NULL (requires research)'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Successfully corrected {updated} OBC community records"
            )
        )

        # Fix municipal coverage if requested
        if also_fix_municipal:
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write("Refreshing Municipal Coverage Aggregates...")
            self.stdout.write("=" * 80)

            municipal_coverages = MunicipalityCoverage.objects.filter(auto_sync=True)
            total_municipal = municipal_coverages.count()

            self.stdout.write(f"\nFound {total_municipal} municipal coverages with auto_sync=True")

            for idx, coverage in enumerate(municipal_coverages, 1):
                if idx % 50 == 0:
                    self.stdout.write(f"  Processing {idx}/{total_municipal}...")

                coverage.refresh_from_communities()

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Refreshed {total_municipal} municipal coverage records"
                )
            )

        # Final summary
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("CORRECTION COMPLETE"))
        self.stdout.write("=" * 80)
        self.stdout.write("\nWhat was corrected:")
        self.stdout.write("  • estimated_obc_population: Set to NULL (requires separate research)")
        self.stdout.write("  • population (legacy): Set to NULL")
        self.stdout.write("  • total_barangay_population: Unchanged (context data)")

        if also_fix_municipal:
            self.stdout.write(f"  • Municipal coverage aggregates: Refreshed ({total_municipal} records)")

        self.stdout.write("\nNext steps:")
        self.stdout.write("  1. Research actual OBC populations per barangay")
        self.stdout.write("  2. Update estimated_obc_population with researched data")
        self.stdout.write("  3. Municipal aggregates will auto-sync from barangay data")
        self.stdout.write("")
