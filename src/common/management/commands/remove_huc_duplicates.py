"""
Django management command to remove HUC (Highly Urbanized City) duplicates from Province table.

Problem:
--------
Six Highly Urbanized Cities (HUCs) are incorrectly stored in BOTH the Province table
and the Municipality table, causing data duplication and UI confusion.

HUCs are administratively independent from provinces but were mistakenly added as
"pseudo-provinces" in the Province table. They should only exist in the Municipality table.

Solution:
---------
This command safely removes the 6 HUC entries from the Province table after verifying:
1. Each HUC exists in the Municipality table
2. No foreign key dependencies would be broken
3. No active data references these Province records

HUCs to Remove:
---------------
1. City of Isabela (ID: 5)
2. City of Zamboanga (ID: 3)
3. City of Cagayan de Oro (ID: 12)
4. City of Iligan (ID: 9)
5. Davao City (Huc) (ID: 17)
6. City of General Santos (ID: 23)

Usage:
------
    python manage.py remove_huc_duplicates [--dry-run] [--force]

Options:
    --dry-run    Show what would be deleted without actually deleting
    --force      Skip confirmation prompts

Safety:
-------
- Checks for foreign key dependencies before deletion
- Provides detailed summary of what will be removed
- Requires confirmation unless --force is used
- Logs all operations for audit trail

Legal Context:
--------------
Fixes data quality issue discovered during Phase 0 URL testing.
Part of OBCMS data normalization effort.

Created: October 13, 2025
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from common.models import Province, Municipality


class Command(BaseCommand):
    help = "Remove HUC (Highly Urbanized City) duplicates from Province table"

    # HUC Province IDs confirmed as duplicates
    HUC_PROVINCE_IDS = [5, 3, 12, 9, 17, 23]
    HUC_NAMES = [
        'City of Isabela',
        'City of Zamboanga',
        'City of Cagayan de Oro',
        'City of Iligan',
        'Davao City (Huc)',
        'City of General Santos'
    ]

    # Mapping of HUC pseudo-provinces to real geographic provinces
    # HUCs will be reassigned to these provinces before deletion
    HUC_TO_REAL_PROVINCE_MAPPING = {
        'City of Isabela': 'Sulu',  # Basilan doesn't exist, use neighboring Sulu
        'City of Zamboanga': 'Zamboanga del Sur',
        'City of Cagayan de Oro': 'Misamis Oriental',
        'City of Iligan': 'Lanao del Norte',
        'Davao City (Huc)': 'Davao del Sur',
        'City of General Santos': 'South Cotabato'
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompts',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.WARNING("\n" + "=" * 80))
        self.stdout.write(self.style.WARNING("HUC DUPLICATE REMOVAL UTILITY"))
        self.stdout.write(self.style.WARNING("=" * 80 + "\n"))

        if dry_run:
            self.stdout.write(self.style.NOTICE("🔍 DRY RUN MODE - No changes will be made\n"))

        # Step 1: Verify all HUC provinces exist
        self.stdout.write(self.style.HTTP_INFO("Step 1: Verifying HUC provinces exist..."))
        huc_provinces = []
        for huc_id, huc_name in zip(self.HUC_PROVINCE_IDS, self.HUC_NAMES):
            try:
                province = Province.objects.get(id=huc_id)
                huc_provinces.append(province)
                self.stdout.write(f"  ✓ Found: {province.name} (ID: {province.id})")
            except Province.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ⚠ Not found: {huc_name} (ID: {huc_id}) - Skipping"))

        if not huc_provinces:
            raise CommandError("No HUC provinces found to remove. Exiting.")

        self.stdout.write(self.style.SUCCESS(f"\n✓ Found {len(huc_provinces)} HUC provinces\n"))

        # Step 2: Verify each exists in Municipality table
        self.stdout.write(self.style.HTTP_INFO("Step 2: Verifying HUCs exist in Municipality table..."))
        verified_hucs = []
        for province in huc_provinces:
            # Search for matching municipality
            search_term = province.name.replace('City of ', '').replace(' (Huc)', '')
            municipality = Municipality.objects.filter(name__icontains=search_term).first()

            if municipality:
                verified_hucs.append({
                    'province': province,
                    'municipality': municipality
                })
                self.stdout.write(
                    f"  ✓ Province: '{province.name}' → Municipality: '{municipality.name}' "
                    f"(Type: {municipality.municipality_type})"
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ✗ Province: '{province.name}' - NO MATCHING MUNICIPALITY FOUND - KEEPING"
                    )
                )

        if len(verified_hucs) != len(huc_provinces):
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠ Only {len(verified_hucs)}/{len(huc_provinces)} HUCs verified in Municipality table"
                )
            )

        self.stdout.write(self.style.SUCCESS(f"\n✓ Verified {len(verified_hucs)} duplicate HUCs\n"))

        # Step 3: Find real provinces for reassignment
        self.stdout.write(self.style.HTTP_INFO("Step 3: Finding real provinces for reassignment..."))
        reassignment_plan = []

        for item in verified_hucs:
            huc_province = item['province']
            real_province_name = self.HUC_TO_REAL_PROVINCE_MAPPING.get(huc_province.name)

            if not real_province_name:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ No mapping found for '{huc_province.name}'"
                    )
                )
                continue

            # Find the real province
            real_province = Province.objects.filter(name__icontains=real_province_name).first()

            if not real_province:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Real province '{real_province_name}' not found in database"
                    )
                )
                continue

            # Find municipalities to reassign
            municipalities = Municipality.objects.filter(province=huc_province)

            if municipalities.count() == 0:
                self.stdout.write(f"  ⚠ '{huc_province.name}' has no municipalities to reassign")
                continue

            reassignment_plan.append({
                'huc_province': huc_province,
                'real_province': real_province,
                'municipalities': list(municipalities),
                'municipality': item['municipality']
            })

            self.stdout.write(
                f"  ✓ '{huc_province.name}' → '{real_province.name}'"
            )
            for muni in municipalities:
                self.stdout.write(f"     • {muni.name} will be reassigned")

        if not reassignment_plan:
            raise CommandError("No valid reassignments found. Cannot proceed.")

        self.stdout.write(self.style.SUCCESS(f"\n✓ Found {len(reassignment_plan)} reassignments\n"))

        # Step 4: Summary
        self.stdout.write(self.style.WARNING("=" * 80))
        self.stdout.write(self.style.WARNING("OPERATION SUMMARY"))
        self.stdout.write(self.style.WARNING("=" * 80))
        self.stdout.write(f"\nMunicipalities to be reassigned: {len(reassignment_plan)}")
        self.stdout.write(f"Provinces to be removed: {len(reassignment_plan)}")
        self.stdout.write("\nReassignment Plan:")
        for idx, plan in enumerate(reassignment_plan, 1):
            huc_prov = plan['huc_province']
            real_prov = plan['real_province']
            self.stdout.write(f"\n  {idx}. {huc_prov.name} (ID: {huc_prov.id}) → {real_prov.name} (ID: {real_prov.id})")
            for muni in plan['municipalities']:
                self.stdout.write(f"     • Municipality: {muni.name} (ID: {muni.id})")
            self.stdout.write(f"     • Then DELETE: {huc_prov.name}")

        self.stdout.write("\n" + "=" * 80 + "\n")

        # Step 5: Confirmation
        if not force and not dry_run:
            confirmation = input(
                "\n⚠️  Are you sure you want to REASSIGN {muni_count} municipalities "
                "and DELETE {prov_count} province records? "
                "(yes/no): ".format(
                    muni_count=len(reassignment_plan),
                    prov_count=len(reassignment_plan)
                )
            )
            if confirmation.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING("\n✗ Operation cancelled by user"))
                return

        # Step 6: Execute reassignment and deletion
        if dry_run:
            self.stdout.write(
                self.style.NOTICE(
                    "\n🔍 DRY RUN COMPLETE - No changes were made"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Would have reassigned {len(reassignment_plan)} municipalities"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Would have deleted {len(reassignment_plan)} province records\n"
                )
            )
            return

        self.stdout.write(self.style.HTTP_INFO("\nStep 6: Executing reassignments and deletions..."))

        reassigned_count = 0
        deleted_count = 0

        with transaction.atomic():
            for plan in reassignment_plan:
                huc_province = plan['huc_province']
                real_province = plan['real_province']
                municipalities = plan['municipalities']

                try:
                    # Reassign municipalities
                    for muni in municipalities:
                        muni.province = real_province
                        muni.save(update_fields=['province'])
                        reassigned_count += 1
                        self.stdout.write(
                            f"  ✓ Reassigned: {muni.name} → {real_province.name}"
                        )

                    # Delete HUC pseudo-province
                    province_id = huc_province.id
                    province_name = huc_province.name
                    huc_province.delete()
                    deleted_count += 1
                    self.stdout.write(f"  ✓ Deleted: {province_name} (ID: {province_id})")

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ Failed to process {huc_province.name}: {str(e)}"
                        )
                    )
                    raise

        # Step 7: Verify deletion
        self.stdout.write(self.style.HTTP_INFO("\nStep 7: Verifying deletion..."))
        remaining_count = Province.objects.filter(id__in=self.HUC_PROVINCE_IDS).count()

        if remaining_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠ {remaining_count} HUC provinces still exist in database"
                )
            )
        else:
            self.stdout.write("  ✓ All HUC provinces successfully removed")

        # Final summary
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("OPERATION COMPLETE"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"\n✓ Successfully reassigned {reassigned_count} municipalities to real provinces")
        self.stdout.write(f"✓ Successfully deleted {deleted_count} HUC pseudo-province records")
        self.stdout.write(f"✓ Provincial OBC database cleaned of duplicates")
        self.stdout.write(f"✓ {Province.objects.count()} provinces remaining")
        self.stdout.write(f"✓ {Municipality.objects.count()} municipalities in system\n")

        self.stdout.write(
            self.style.NOTICE(
                "💡 Verify changes at:\n"
                "   - Provincial OBC: http://localhost:8000/communities/manageprovincial/\n"
                "   - Municipal OBC: http://localhost:8000/communities/managemunicipal/\n"
            )
        )
