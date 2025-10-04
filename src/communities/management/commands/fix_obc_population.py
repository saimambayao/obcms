"""Management command to fix OBC population that exceeds total barangay population."""

from django.core.management.base import BaseCommand
from django.db.models import F

from communities.models import OBCCommunity


class Command(BaseCommand):
    help = "Fix OBC communities where estimated OBC population exceeds total barangay population"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be fixed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Find all OBC communities where estimated_obc_population > barangay.population_total
        # We need to check against the Barangay's population_total since that's what's displayed
        invalid_communities = OBCCommunity.objects.filter(
            estimated_obc_population__gt=F("barangay__population_total"),
            barangay__population_total__gt=0,
        ).select_related("barangay__municipality")

        count = invalid_communities.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ No invalid population data found. All OBC populations are valid!"
                )
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"\n{'🔍 PREVIEW' if dry_run else '⚠️  FIXING'} {count} OBC record(s) with invalid population data:\n"
            )
        )

        fixed_count = 0
        for community in invalid_communities:
            old_obc_pop = community.estimated_obc_population
            barangay_total_pop = community.barangay.population_total

            self.stdout.write(
                f"\n  📍 {community.barangay.name}, {community.barangay.municipality.name}"
            )
            self.stdout.write(
                f"     ❌ Est. OBC Population: {old_obc_pop:,} (exceeds total)"
            )
            self.stdout.write(f"     ℹ️  Total Barangay Pop:  {barangay_total_pop:,}")
            self.stdout.write(
                f"     ✅ Will set OBC pop to: {barangay_total_pop:,} (capped at total)"
            )

            if not dry_run:
                community.estimated_obc_population = barangay_total_pop
                community.save(update_fields=["estimated_obc_population", "updated_at"])
                fixed_count += 1

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n\n🔍 DRY RUN: {count} record(s) would be fixed. Run without --dry-run to apply changes.\n"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n\n✅ Successfully fixed {fixed_count} OBC record(s)!\n"
                )
            )
            self.stdout.write(
                "   All OBC populations are now capped at their barangay's total population.\n"
            )
