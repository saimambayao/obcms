"""Management command to create pilot BMMS users."""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from organizations.services import PilotUserService


class Command(BaseCommand):
    help = "Create an individual pilot user with organization assignment and role"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--organization", required=True, help="Organization code (e.g., MOH)")
        parser.add_argument("--role", required=True, help="Pilot role identifier (planner, budget_officer, etc.)")
        parser.add_argument("--first-name", dest="first_name", default="")
        parser.add_argument("--last-name", dest="last_name", default="")
        parser.add_argument("--phone", default="")
        parser.add_argument("--position", default="")
        parser.add_argument("--department", default="")
        parser.add_argument("--password", default=None)
        parser.add_argument("--no-email", action="store_true", help="Skip sending welcome email")

    def handle(self, *args, **options):  # type: ignore[override]
        service = PilotUserService()
        try:
            result = service.create_pilot_user(
                username=options["username"],
                email=options["email"],
                organization_code=options["organization"],
                role=options["role"],
                first_name=options["first_name"],
                last_name=options["last_name"],
                phone=options["phone"],
                position=options["position"],
                department=options["department"],
                password=options["password"],
                send_welcome_email=not options["no_email"],
            )
        except Exception as exc:  # pragma: no cover - CLI entry point
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Pilot user '{result.user.username}' created for {options['organization']}"
            )
        )
        self.stdout.write(f"Temporary password: {result.raw_password}")
