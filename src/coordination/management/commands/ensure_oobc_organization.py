"""
Management command to ensure OOBC organization exists with correct data.

This command is idempotent - it can be run multiple times safely.
It will create OOBC if it doesn't exist, or update it with correct data if it does.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from coordination.models import Organization

User = get_user_model()


class Command(BaseCommand):
    help = "Ensure OOBC organization exists with correct data"

    def handle(self, *args, **options):
        # Get or create system user for created_by field
        system_user, _ = User.objects.get_or_create(
            username="system",
            defaults={
                "email": "system@bangsamoro.gov.ph",
                "first_name": "OBCMS",
                "last_name": "Admin",
                "is_active": True,
            },
        )

        # OOBC data from barmm_ministries.yaml
        oobc_data = {
            "name": "Office for Other Bangsamoro Communities",
            "acronym": "OOBC",
            "organization_type": "bmoa",
            "mandate": (
                "Recommends policies and systematic programs for promoting the welfare of "
                "Bangsamoro communities outside the region, including provision of services."
            ),
            "powers_and_functions": "\n".join([
                "Gather socio-economic data and assess needs of Bangsamoro communities outside BARMM to inform responsive interventions.",
                "Coordinate with BARMM ministries, offices, and agencies to integrate Other Bangsamoro Communities priorities into policies, programs, and services.",
                "Facilitate partnerships with NGAs, LGUs, and development partners to protect OBC rights and advance socio-economic and cultural development.",
            ]),
            "description": (
                "The Office for Other Bangsamoro Communities serves Bangsamoro people "
                "residing outside the BARMM territorial jurisdiction"
            ),
            "is_active": True,
            "is_priority": True,
            "partnership_status": "active",
        }

        # Try to get OOBC by acronym or name
        oobc = Organization.objects.filter(acronym="OOBC").first()

        if not oobc:
            oobc = Organization.objects.filter(
                name="Office for Other Bangsamoro Communities"
            ).first()

        if oobc:
            # OOBC exists - update it with correct data
            updated_fields = []

            for field, value in oobc_data.items():
                if field == "name":
                    continue  # Don't update name

                current_value = getattr(oobc, field)
                if current_value != value:
                    setattr(oobc, field, value)
                    updated_fields.append(field)

            if updated_fields:
                oobc.save(update_fields=updated_fields)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Updated OOBC organization with fields: {', '.join(updated_fields)}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        "✓ OOBC organization already has correct data"
                    )
                )
        else:
            # OOBC doesn't exist - create it
            oobc_data["created_by"] = system_user
            oobc = Organization.objects.create(**oobc_data)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created OOBC organization: {oobc.name} ({oobc.acronym})"
                )
            )

        # Display final OOBC details
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("OOBC Organization Details:")
        self.stdout.write("=" * 80)
        self.stdout.write(f"ID: {oobc.id}")
        self.stdout.write(f"Name: {oobc.name}")
        self.stdout.write(f"Acronym: {oobc.acronym}")
        self.stdout.write(f"Type: {oobc.organization_type}")
        self.stdout.write(f"Description: {oobc.description}")
        self.stdout.write(f"Mandate: {oobc.mandate}")
        self.stdout.write(f"\nPowers and Functions:")
        for line in oobc.powers_and_functions.split('\n'):
            self.stdout.write(f"  - {line}")
        self.stdout.write(f"\nIs Active: {oobc.is_active}")
        self.stdout.write(f"Is Priority: {oobc.is_priority}")
        self.stdout.write(f"Partnership Status: {oobc.partnership_status}")
        self.stdout.write("=" * 80)
