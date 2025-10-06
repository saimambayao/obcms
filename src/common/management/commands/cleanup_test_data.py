"""
Management command to remove dummy and test geographic data from the database.

This command removes all test/dummy regions, provinces, municipalities, and barangays,
keeping only legitimate data from the 4 target regions:
- Region IX (Zamboanga Peninsula)
- Region X (Northern Mindanao)
- Region XI (Davao Region)
- Region XII (SOCCSKSARGEN)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from common.models import Region, Province, Municipality, Barangay
from communities.models import OBCCommunity, MunicipalityCoverage, ProvinceCoverage
from auditlog.models import LogEntry


class Command(BaseCommand):
    help = "Remove dummy and test geographic data, keeping only legitimate data from 4 target regions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip confirmation prompt",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        skip_confirm = options["yes"]

        self.stdout.write(self.style.WARNING("\n" + "=" * 80))
        self.stdout.write(
            self.style.WARNING("Geographic Data Cleanup - Remove Test/Dummy Data")
        )
        self.stdout.write(self.style.WARNING("=" * 80 + "\n"))

        # Define legitimate region codes
        legitimate_codes = {"IX", "X", "XI", "XII"}

        # Find all regions
        all_regions = Region.objects.all()
        legitimate_regions = Region.objects.filter(code__in=legitimate_codes)
        test_regions = Region.objects.exclude(code__in=legitimate_codes)

        self.stdout.write(self.style.SUCCESS("\n📊 Current Database Status:\n"))
        self.stdout.write(f"  Total Regions: {all_regions.count()}")
        self.stdout.write(
            f"  Legitimate Regions (IX, X, XI, XII): {legitimate_regions.count()}"
        )
        self.stdout.write(f"  Test/Dummy Regions: {test_regions.count()}")

        # Count related objects for test regions
        test_provinces = Province.objects.filter(region__in=test_regions)
        test_municipalities = Municipality.objects.filter(province__region__in=test_regions)
        test_barangays = Barangay.objects.filter(
            municipality__province__region__in=test_regions
        )
        test_obc_communities = OBCCommunity.all_objects.filter(
            barangay__municipality__province__region__in=test_regions
        )
        test_municipality_coverage = MunicipalityCoverage.all_objects.filter(
            municipality__province__region__in=test_regions
        )
        test_province_coverage = ProvinceCoverage.all_objects.filter(
            province__region__in=test_regions
        )

        self.stdout.write("\n" + self.style.ERROR("🗑️  Objects to be DELETED:\n"))

        # Display test regions
        if test_regions.exists():
            self.stdout.write(self.style.ERROR(f"\n  Test/Dummy Regions ({test_regions.count()}):"))
            for region in test_regions:
                self.stdout.write(f"    - ID: {region.id}, Code: {region.code}, Name: {region.name}")

        # Display test provinces
        if test_provinces.exists():
            self.stdout.write(
                self.style.ERROR(f"\n  Provinces in test regions ({test_provinces.count()}):"))
            for province in test_provinces[:10]:  # Show first 10
                self.stdout.write(
                    f"    - {province.name} (Region: {province.region.code})"
                )
            if test_provinces.count() > 10:
                self.stdout.write(f"    ... and {test_provinces.count() - 10} more")

        # Display test municipalities
        if test_municipalities.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"\n  Municipalities in test regions ({test_municipalities.count()}):"
                )
            )
            for muni in test_municipalities[:10]:  # Show first 10
                self.stdout.write(
                    f"    - {muni.name} ({muni.province.name}, {muni.province.region.code})"
                )
            if test_municipalities.count() > 10:
                self.stdout.write(
                    f"    ... and {test_municipalities.count() - 10} more"
                )

        # Display test barangays
        if test_barangays.exists():
            self.stdout.write(
                self.style.ERROR(f"\n  Barangays in test regions ({test_barangays.count()}):")
            )
            for brgy in test_barangays[:10]:  # Show first 10
                self.stdout.write(
                    f"    - {brgy.name} ({brgy.municipality.name}, {brgy.province.name})"
                )
            if test_barangays.count() > 10:
                self.stdout.write(f"    ... and {test_barangays.count() - 10} more")

        # Display test OBC communities
        if test_obc_communities.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"\n  OBC Communities in test regions ({test_obc_communities.count()}):"
                )
            )
            for community in test_obc_communities[:10]:
                self.stdout.write(
                    f"    - {community.display_name} ({community.barangay.name}, {community.municipality.name})"
                )
            if test_obc_communities.count() > 10:
                self.stdout.write(
                    f"    ... and {test_obc_communities.count() - 10} more"
                )

        # Display municipality coverage
        if test_municipality_coverage.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"\n  Municipality Coverage in test regions ({test_municipality_coverage.count()}):"
                )
            )
            for coverage in test_municipality_coverage:
                self.stdout.write(
                    f"    - {coverage.municipality.name} ({coverage.province.name})"
                )

        # Display province coverage
        if test_province_coverage.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"\n  Province Coverage in test regions ({test_province_coverage.count()}):"
                )
            )
            for coverage in test_province_coverage:
                self.stdout.write(f"    - {coverage.province.name} ({coverage.region.code})")

        # Display legitimate regions that will be KEPT
        self.stdout.write("\n" + self.style.SUCCESS("✅ Legitimate Regions to KEEP:\n"))
        for region in legitimate_regions:
            province_count = Province.objects.filter(region=region).count()
            municipality_count = Municipality.objects.filter(
                province__region=region
            ).count()
            barangay_count = Barangay.objects.filter(
                municipality__province__region=region
            ).count()

            self.stdout.write(
                f"  - Region {region.code}: {region.name}"
            )
            self.stdout.write(
                f"      Provinces: {province_count}, "
                f"Municipalities: {municipality_count}, "
                f"Barangays: {barangay_count}"
            )

        # Summary
        total_to_delete = (
            test_regions.count()
            + test_provinces.count()
            + test_municipalities.count()
            + test_barangays.count()
            + test_obc_communities.count()
            + test_municipality_coverage.count()
            + test_province_coverage.count()
        )

        self.stdout.write("\n" + self.style.WARNING("📋 Deletion Summary:\n"))
        self.stdout.write(f"  Regions: {test_regions.count()}")
        self.stdout.write(f"  Provinces: {test_provinces.count()}")
        self.stdout.write(f"  Municipalities: {test_municipalities.count()}")
        self.stdout.write(f"  Barangays: {test_barangays.count()}")
        self.stdout.write(f"  OBC Communities: {test_obc_communities.count()}")
        self.stdout.write(f"  Municipality Coverage: {test_municipality_coverage.count()}")
        self.stdout.write(f"  Province Coverage: {test_province_coverage.count()}")
        self.stdout.write(f"  TOTAL: {total_to_delete} objects")

        if total_to_delete == 0:
            self.stdout.write(
                self.style.SUCCESS("\n✅ No test/dummy data found. Database is clean!")
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n🔍 DRY RUN MODE - No changes made to database")
            )
            return

        # Confirmation
        if not skip_confirm:
            self.stdout.write("\n" + self.style.WARNING("⚠️  WARNING:"))
            self.stdout.write(
                "  This operation will PERMANENTLY DELETE all test/dummy geographic data."
            )
            self.stdout.write(
                "  Related OBC communities, assessments, and other linked data will also be affected."
            )
            confirm = input("\nType 'DELETE' (all caps) to confirm deletion: ")

            if confirm != "DELETE":
                self.stdout.write(self.style.ERROR("\n❌ Operation cancelled."))
                return

        # Perform deletion
        self.stdout.write("\n" + self.style.WARNING("🔥 Deleting test/dummy data..."))

        try:
            # Temporarily disable foreign key constraints for SQLite
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = OFF;")

            with transaction.atomic():
                # Delete in order (child to parent due to foreign key constraints)
                deleted_counts = {}

                # 0. Delete audit log entries first (they reference all objects)
                self.stdout.write("  Deleting audit log entries...")
                # Get content types for all models we're deleting
                region_ct = ContentType.objects.get_for_model(Region)
                province_ct = ContentType.objects.get_for_model(Province)
                municipality_ct = ContentType.objects.get_for_model(Municipality)
                barangay_ct = ContentType.objects.get_for_model(Barangay)
                obc_ct = ContentType.objects.get_for_model(OBCCommunity)
                muni_cov_ct = ContentType.objects.get_for_model(MunicipalityCoverage)
                prov_cov_ct = ContentType.objects.get_for_model(ProvinceCoverage)

                # Delete audit logs for all objects
                audit_count = LogEntry.objects.filter(
                    content_type__in=[
                        region_ct,
                        province_ct,
                        municipality_ct,
                        barangay_ct,
                        obc_ct,
                        muni_cov_ct,
                        prov_cov_ct,
                    ],
                    object_pk__in=(
                        [str(r.pk) for r in test_regions]
                        + [str(p.pk) for p in test_provinces]
                        + [str(m.pk) for m in test_municipalities]
                        + [str(b.pk) for b in test_barangays]
                        + [str(o.pk) for o in test_obc_communities]
                        + [str(mc.pk) for mc in test_municipality_coverage]
                        + [str(pc.pk) for pc in test_province_coverage]
                    ),
                ).delete()[0]
                deleted_counts["audit_logs"] = audit_count

                # 1. Delete OBC Communities first (they reference barangays)
                self.stdout.write("  Deleting OBC Communities...")
                obc_count, _ = test_obc_communities.delete()
                deleted_counts["obc_communities"] = obc_count

                # 2. Delete Municipality Coverage (references municipalities)
                self.stdout.write("  Deleting Municipality Coverage...")
                muni_cov_count, _ = test_municipality_coverage.delete()
                deleted_counts["municipality_coverage"] = muni_cov_count

                # 3. Delete Province Coverage (references provinces)
                self.stdout.write("  Deleting Province Coverage...")
                prov_cov_count, _ = test_province_coverage.delete()
                deleted_counts["province_coverage"] = prov_cov_count

                # 4. Delete barangays
                self.stdout.write("  Deleting Barangays...")
                barangay_count, _ = test_barangays.delete()
                deleted_counts["barangays"] = barangay_count

                # 5. Delete municipalities
                self.stdout.write("  Deleting Municipalities...")
                municipality_count, _ = test_municipalities.delete()
                deleted_counts["municipalities"] = municipality_count

                # 6. Delete provinces
                self.stdout.write("  Deleting Provinces...")
                province_count, _ = test_provinces.delete()
                deleted_counts["provinces"] = province_count

                # 7. Delete regions (should cascade delete any remaining related objects)
                self.stdout.write("  Deleting Regions...")
                region_count, _ = test_regions.delete()
                deleted_counts["regions"] = region_count

                self.stdout.write(self.style.SUCCESS("\n✅ Deletion completed successfully!"))
                self.stdout.write("\n📊 Deleted:")
                self.stdout.write(f"  Audit Log Entries: {deleted_counts['audit_logs']}")
                self.stdout.write(f"  Regions: {deleted_counts['regions']}")
                self.stdout.write(f"  Provinces: {deleted_counts['provinces']}")
                self.stdout.write(f"  Municipalities: {deleted_counts['municipalities']}")
                self.stdout.write(f"  Barangays: {deleted_counts['barangays']}")
                self.stdout.write(f"  OBC Communities: {deleted_counts['obc_communities']}")
                self.stdout.write(
                    f"  Municipality Coverage: {deleted_counts['municipality_coverage']}"
                )
                self.stdout.write(f"  Province Coverage: {deleted_counts['province_coverage']}")

                # Verify remaining data
                remaining_regions = Region.objects.all()
                self.stdout.write(
                    self.style.SUCCESS(f"\n✅ Remaining Regions: {remaining_regions.count()}")
                )
                for region in remaining_regions:
                    self.stdout.write(f"  - Region {region.code}: {region.name}")

            # Re-enable foreign key constraints
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = ON;")

        except Exception as e:
            # Re-enable foreign key constraints even if there's an error
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = ON;")

            self.stdout.write(
                self.style.ERROR(f"\n❌ Error during deletion: {str(e)}")
            )
            self.stdout.write(self.style.ERROR("Transaction rolled back. No changes made."))
            raise
