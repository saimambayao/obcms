"""Load core pilot MOAs for the BMMS pilot onboarding."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from organizations.models import Organization

PILOT_MOAS = [
    {
        "code": "MOH",
        "name": "Ministry of Health",
        "acronym": "MOH",
        "org_type": "ministry",
    },
    {
        "code": "MOLE",
        "name": "Ministry of Labor and Employment",
        "acronym": "MOLE",
        "org_type": "ministry",
    },
    {
        "code": "MAFAR",
        "name": "Ministry of Agriculture, Fisheries and Agrarian Reform",
        "acronym": "MAFAR",
        "org_type": "ministry",
    },
]


class Command(BaseCommand):
    help = "Create or update the pilot MOA records required for Phase 7 onboarding"

    def handle(self, *args, **options):  # type: ignore[override]
        created = 0
        updated = 0
        for payload in PILOT_MOAS:
            _, was_created = Organization.objects.update_or_create(
                code=payload["code"],
                defaults={
                    "name": payload["name"],
                    "acronym": payload["acronym"],
                    "org_type": payload["org_type"],
                    "is_active": True,
                    "is_pilot": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Pilot MOA sync complete (created={created}, updated={updated})"
            )
        )
