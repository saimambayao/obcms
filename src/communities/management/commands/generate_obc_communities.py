"""
Management command to generate OBC Communities from existing barangay data.

This command creates OBC community records for barangays in target regions
(IX, X, XI, XII), populating them with existing geographic and demographic data.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from common.models import Region, Province, Municipality, Barangay
from communities.models import OBCCommunity


class Command(BaseCommand):
    help = "Generate OBC Communities from existing barangay data with coordinates and population"

    def add_arguments(self, parser):
        parser.add_argument(
            "--regions",
            nargs="+",
            default=["IX", "X", "XI", "XII"],
            help="Region codes to process (default: IX X XI XII)",
        )
        parser.add_argument(
            "--province",
            help="Limit to specific province name",
        )
        parser.add_argument(
            "--municipality",
            help="Limit to specific municipality name",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit number of OBC communities to create (for testing)",
        )
        parser.add_argument(
            "--min-population",
            type=int,
            default=0,
            help="Only create OBC communities for barangays with population >= this value",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be created without saving to database",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing OBC communities with latest data",
        )

    def handle(self, *args, **options):
        regions = options["regions"]
        province_filter = options.get("province")
        municipality_filter = options.get("municipality")
        limit = options.get("limit")
        min_population = options["min_population"]
        dry_run = options["dry_run"]
        update_existing = options["update_existing"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be saved"))

        # Build barangay queryset
        barangays = Barangay.objects.filter(
            municipality__province__region__code__in=regions,
            is_active=True,
        ).select_related(
            "municipality__province__region"
        )

        # Apply filters
        if province_filter:
            barangays = barangays.filter(municipality__province__name__icontains=province_filter)

        if municipality_filter:
            barangays = barangays.filter(municipality__name__icontains=municipality_filter)

        if min_population > 0:
            barangays = barangays.filter(population_total__gte=min_population)

        # Apply limit if specified
        if limit:
            barangays = barangays[:limit]

        total_barangays = barangays.count()

        self.stdout.write(
            self.style.SUCCESS(f"\nFound {total_barangays} barangays to process")
        )
        self.stdout.write(f"Regions: {', '.join(regions)}")
        if province_filter:
            self.stdout.write(f"Province filter: {province_filter}")
        if municipality_filter:
            self.stdout.write(f"Municipality filter: {municipality_filter}")
        if min_population > 0:
            self.stdout.write(f"Minimum population: {min_population}")

        stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        # Process barangays
        for idx, barangay in enumerate(barangays, 1):
            if idx % 100 == 0:
                self.stdout.write(f"Processing {idx}/{total_barangays}...")

            try:
                result = self._process_barangay(
                    barangay,
                    dry_run=dry_run,
                    update_existing=update_existing
                )
                stats[result] += 1

                if result == "created":
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Created OBC: {barangay.name}, {barangay.municipality.name}, "
                            f"{barangay.municipality.province.name} (Pop: {barangay.population_total or 'N/A'})"
                        )
                    )
                elif result == "updated":
                    self.stdout.write(
                        f"↻ Updated OBC: {barangay.name}, {barangay.municipality.name}"
                    )
                elif result == "skipped":
                    if options.get("verbosity", 1) >= 2:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⊘ Skipped: {barangay.name}, {barangay.municipality.name} (already exists)"
                            )
                        )

            except Exception as e:
                stats["errors"] += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Error processing {barangay.name}, {barangay.municipality.name}: {str(e)}"
                    )
                )

        # Print summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SUMMARY"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total barangays processed: {total_barangays}")
        self.stdout.write(self.style.SUCCESS(f"✓ Created: {stats['created']}"))
        self.stdout.write(f"↻ Updated: {stats['updated']}")
        self.stdout.write(f"⊘ Skipped: {stats['skipped']}")
        if stats["errors"] > 0:
            self.stdout.write(self.style.ERROR(f"✗ Errors: {stats['errors']}"))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nDRY RUN COMPLETE - No changes were saved to the database"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Successfully created/updated {stats['created'] + stats['updated']} OBC communities"
                )
            )

    def _process_barangay(self, barangay, dry_run=False, update_existing=False):
        """Process a single barangay and create/update its OBC community."""

        # Check if OBC community already exists
        existing = OBCCommunity.objects.filter(barangay=barangay).first()

        if existing and not update_existing:
            return "skipped"

        # Prepare OBC community data
        obc_data = self._prepare_obc_data(barangay)

        if dry_run:
            if existing:
                return "updated" if update_existing else "skipped"
            return "created"

        # Create or update OBC community
        if existing and update_existing:
            with transaction.atomic():
                for field, value in obc_data.items():
                    setattr(existing, field, value)
                existing.save()
            return "updated"
        elif not existing:
            with transaction.atomic():
                OBCCommunity.objects.create(barangay=barangay, **obc_data)
            return "created"
        else:
            return "skipped"

    def _prepare_obc_data(self, barangay):
        """Prepare OBC community data from barangay record.

        IMPORTANT:
        - estimated_obc_population should be NULL (not yet researched)
        - total_barangay_population is the full barangay population (for context)
        - OBC population is a SUBSET of total population and must be researched separately
        """

        # Extract coordinates if available
        latitude = None
        longitude = None
        if barangay.center_coordinates:
            # center_coordinates is [longitude, latitude] in GeoJSON format
            if isinstance(barangay.center_coordinates, list) and len(barangay.center_coordinates) == 2:
                longitude = barangay.center_coordinates[0]
                latitude = barangay.center_coordinates[1]

        # Generate OBC ID
        region_code = barangay.municipality.province.region.code
        province_abbr = "".join([w[0] for w in barangay.municipality.province.name.split()[:2]]).upper()
        muni_abbr = "".join([w[0] for w in barangay.municipality.name.split()[:2]]).upper()
        obc_id = f"{region_code}-{province_abbr}-{muni_abbr}-{barangay.id:04d}"

        return {
            # Legacy compatibility fields
            "name": barangay.name,
            "population": None,  # OBC-specific population (to be researched)

            # Identification
            "obc_id": obc_id,
            "community_names": barangay.name,

            # Demographics - CRITICAL DISTINCTION:
            # estimated_obc_population: Only OBC individuals (NULL until researched)
            # total_barangay_population: Total barangay population (for context)
            "estimated_obc_population": None,  # Must be researched/estimated separately
            "total_barangay_population": barangay.population_total,  # Full barangay population

            # Geographic
            "latitude": latitude,
            "longitude": longitude,

            # Source documentation
            "source_document_reference": f"Generated from barangay data - {barangay.code}. OBC population needs research.",

            # Administrative
            "is_active": True,
            "notes": f"Auto-generated from barangay: {barangay.full_path}. estimated_obc_population requires separate research/assessment.",
        }
