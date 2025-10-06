"""Management command to create user accounts for all OOBC staff members."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from common.models import User


STAFF_ACCOUNTS = [
    {
        "first_name": "Noron",
        "last_name": "Andan",
        "full_name": "Noron S. Andan, MPA, MAEd",
        "position": "Executive Director",
        "username": "noron.oobc",
        "password": "Noron123",
        "user_type": "oobc_executive",
    },
    {
        "first_name": "Quraish",
        "last_name": "Langcap",
        "full_name": "Quraish D. Langcap",
        "position": "Deputy Executive Director",
        "username": "qurash.oobc",
        "password": "Qurash123",
        "user_type": "oobc_executive",
    },
    {
        "first_name": "Norhan",
        "last_name": "Hadji Abdullah",
        "full_name": "Norhan B. Hadji Abdullah",
        "position": "DMO IV",
        "username": "norhan.oobc",
        "password": "Norhan123",
    },
    {
        "first_name": "Rusman",
        "last_name": "Musa",
        "full_name": "Rusman B. Musa",
        "position": "DMO III",
        "username": "rusman.oobc",
        "password": "Rusman123",
    },
    {
        "first_name": "Farhanna",
        "last_name": "Kabalu",
        "full_name": "Farhanna U. Kabalu",
        "position": "Planning Officer II",
        "username": "farhanna.oobc",
        "password": "Farhanna123",
    },
    {
        "first_name": "Al-Amid",
        "last_name": "Gandawali",
        "full_name": "Al-Amid P. Gandawali",
        "position": "Information System Analyst",
        "username": "al-amid.oobc",
        "password": "Al-amid123",
    },
    {
        "first_name": "Michael",
        "last_name": "Berwal",
        "full_name": "Michael A. Berwal",
        "position": "Administrative Officer II",
        "username": "michael.oobc",
        "password": "Michael123",
    },
    {
        "first_name": "Esnain",
        "last_name": "Mapait",
        "full_name": "Esnain C. Mapait",
        "position": "Community Development Officer I",
        "username": "esnain.oobc",
        "password": "Esnain123",
    },
    {
        "first_name": "Mohammad Hamid",
        "last_name": "Bato",
        "full_name": "Mohammad Hamid M. Bato",
        "position": "Planning Officer I",
        "username": "mohammad.oobc",
        "password": "Mohammad123",
    },
    {
        "first_name": "Habiba",
        "last_name": "Abunawas",
        "full_name": "Habiba B. Abunawas",
        "position": "Development Management Officer I",
        "username": "habiba.oobc",
        "password": "Habiba123",
    },
    {
        "first_name": "Datu Noah",
        "last_name": "Damping",
        "full_name": "Datu Noah P. Damping",
        "position": "Administrative Assistant V",
        "username": "datu.oobc",
        "password": "Datu123",
    },
    {
        "first_name": "Ramla",
        "last_name": "Manguda",
        "full_name": "Ramla L. Manguda",
        "position": "Administrative Assistant I",
        "username": "ramla.oobc",
        "password": "Ramla123",
    },
    {
        "first_name": "Nor-hayya",
        "last_name": "Donde",
        "full_name": "Nor-hayya A. Donde",
        "position": "Administrative Assistant I",
        "username": "nor-hayya.oobc",
        "password": "Nor-hayya123",
    },
    {
        "first_name": "Ummu Calthoom",
        "last_name": "Basug",
        "full_name": "Ummu Calthoom L. Basug",
        "position": "Administrative Assistant I",
        "username": "ummu.oobc",
        "password": "Ummu123",
    },
    {
        "first_name": "Mardiya",
        "last_name": "Jaukal",
        "full_name": "Mardiya M. Jaukal",
        "position": "Administrative Assistant I",
        "username": "mardiya.oobc",
        "password": "Mardiya123",
    },
    {
        "first_name": "Rayyana",
        "last_name": "Pendi",
        "full_name": "Rayyana G. Pendi",
        "position": "Administrative Assistant I",
        "username": "rayyana.oobc",
        "password": "Rayyana123",
    },
    {
        "first_name": "Herdan",
        "last_name": "Tang",
        "full_name": "Herdan V. Tang",
        "position": "Records Officer I",
        "username": "herdan.oobc",
        "password": "Herdan123",
    },
    {
        "first_name": "Datu Abdulbasit",
        "last_name": "Esmael",
        "full_name": "Datu Abdulbasit T. Esmael",
        "position": "Supply Officer I",
        "username": "abdulbasit.oobc",
        "password": "Abdulbasit123",
    },
    {
        "first_name": "Omulheir",
        "last_name": "Noddin",
        "full_name": "Omulheir M. Noddin",
        "position": "Information Officer I",
        "username": "omulheir.oobc",
        "password": "Omulheir123",
    },
    {
        "first_name": "Mohadier",
        "last_name": "Gawan",
        "full_name": "Mohadier S. Gawan",
        "position": "Project Evaluation Officer I",
        "username": "mohadier.oobc",
        "password": "Mohadier123",
    },
    {
        "first_name": "Sittie Fayesha",
        "last_name": "Tumog",
        "full_name": "Sittie Fayesha S. Tumog",
        "position": "Information Assistant",
        "username": "sittie.oobc",
        "password": "Sittie123",
    },
    {
        "first_name": "Hamde",
        "last_name": "Samana",
        "full_name": "Hamde B. Samana",
        "position": "Administrative Aide V",
        "username": "hamde.oobc",
        "password": "Hamde123",
    },
    {
        "first_name": "Mohaimen",
        "last_name": "Gumander",
        "full_name": "Mohaimen R. Gumander",
        "position": "Administrative Aide V",
        "username": "mohaimen.oobc",
        "password": "Mohaimen123",
    },
    {
        "first_name": "Akmad",
        "last_name": "Gandawali",
        "full_name": "Akmad S. Gandawali",
        "position": "Administrative Aide V",
        "username": "akmad.oobc",
        "password": "Akmad123",
    },
    {
        "first_name": "Marifel",
        "last_name": "Introducion",
        "full_name": "Marifel C. Introducion",
        "position": "Administrative Aide V",
        "username": "marifel.oobc",
        "password": "Marifel123",
    },
]


class Command(BaseCommand):
    """Create user accounts for all OOBC staff members with standardized credentials."""

    help = "Creates user accounts for all OOBC staff with format firstname.oobc / Firstname123"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating accounts",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip accounts that already exist instead of updating them",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        skip_existing = options["skip_existing"]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for staff in STAFF_ACCOUNTS:
                username = staff["username"]
                existing_user = User.objects.filter(username=username).first()

                if existing_user:
                    if skip_existing:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"⏭️  Skipped: {username} (already exists)"
                            )
                        )
                        continue

                    # Update existing user
                    if not dry_run:
                        existing_user.first_name = staff["first_name"]
                        existing_user.last_name = staff["last_name"]
                        existing_user.position = staff["position"]
                        existing_user.user_type = staff.get("user_type", "oobc_staff")
                        existing_user.organization = (
                            "Office for Other Bangsamoro Communities, Office of the Chief "
                            "Minister (Bangsamoro Autonomous Region in Muslim Mindanao)"
                        )
                        existing_user.is_active = True
                        existing_user.is_staff = True
                        existing_user.is_approved = True
                        existing_user.email = f"{username}@oobc.gov.ph"
                        existing_user.set_password(staff["password"])
                        existing_user.save()

                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Updated: {username} - {staff['full_name']}"
                        )
                    )
                else:
                    # Create new user
                    if not dry_run:
                        user = User.objects.create_user(
                            username=username,
                            password=staff["password"],
                            first_name=staff["first_name"],
                            last_name=staff["last_name"],
                            email=f"{username}@oobc.gov.ph",
                            user_type=staff.get("user_type", "oobc_staff"),
                            position=staff["position"],
                            organization=(
                                "Office for Other Bangsamoro Communities, Office of the Chief "
                                "Minister (Bangsamoro Autonomous Region in Muslim Mindanao)"
                            ),
                            is_active=True,
                            is_staff=True,
                            is_approved=True,
                        )

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Created: {username} - {staff['full_name']}"
                        )
                    )

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        "\n🔍 DRY RUN MODE - No changes were made to the database"
                    )
                )

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Staff accounts processed successfully!\n"
                f"   Created: {created_count}\n"
                f"   Updated: {updated_count}\n"
                f"   Skipped: {skipped_count}\n"
                f"   Total:   {created_count + updated_count + skipped_count}"
            )
        )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    "\n🔐 All accounts are ready to use with their assigned credentials."
                )
            )
