"""Generate comprehensive pilot test data for Phase 7."""

from __future__ import annotations

import itertools

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from organizations.models import Organization
from organizations.services import PilotUserService

ROLE_ROTATION = ["pilot_admin", "planner", "budget_officer", "me_officer", "viewer"]


class Command(BaseCommand):
    help = "Generate organizations, planning/budget data, and sample users for pilot MOAs"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument(
            "--moa",
            dest="moa",
            default=None,
            help="Optional organization code to limit generation",
        )
        parser.add_argument("--users", type=int, default=5, help="Number of users to create per organization")
        parser.add_argument("--programs", type=int, default=3)
        parser.add_argument("--year", type=int, default=None)

    def handle(self, *args, **options):  # type: ignore[override]
        call_command("load_pilot_moas")

        queryset = Organization.objects.filter(is_pilot=True, is_active=True)
        if options["moa"]:
            queryset = queryset.filter(code__iexact=options["moa"])
            if not queryset.exists():
                raise CommandError(f"Pilot organization {options['moa']} not found")

        pilot_orgs = list(queryset.order_by("code"))
        if not pilot_orgs:
            raise CommandError("No pilot organizations available")

        service = PilotUserService()
        target_year = options["year"] or 2025

        for organization in pilot_orgs:
            self.stdout.write(self.style.MIGRATE_HEADING(f"Generating data for {organization.code}"))

            call_command(
                "generate_sample_programs",
                organization=organization.code,
                programs=options["programs"],
                year=target_year,
            )
            call_command(
                "generate_sample_budgets",
                organization=organization.code,
                programs=options["programs"],
                year=target_year,
            )

            role_cycle = itertools.cycle(ROLE_ROTATION)
            for index in range(options["users"]):
                role = next(role_cycle)
                username = f"{organization.code.lower()}_pilot_{index + 1}"
                email = f"{username}@{organization.code.lower()}.pilot.bmms.gov.ph"
                try:
                    result = service.create_pilot_user(
                        username=username,
                        email=email,
                        organization_code=organization.code,
                        role=role,
                        first_name=f"Pilot {organization.code}",
                        last_name=f"User {index + 1}",
                        department="Pilot Operations",
                        position="Pilot Team Member",
                    )
                    self.stdout.write(f"  - Created user {result.user.username} ({role})")
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f"  ! Skipped user {username}: {exc}"))

        self.stdout.write(self.style.SUCCESS("Pilot data generation complete"))
