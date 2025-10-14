"""Assign pilot roles to existing users."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from organizations.services import PilotRoleService


class Command(BaseCommand):
    help = "Assign a pilot role (Django group) to an existing user"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("username", help="Username to assign the role to")
        parser.add_argument("role", help="Pilot role identifier")

    def handle(self, *args, **options):  # type: ignore[override]
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=options["username"])
        except user_model.DoesNotExist as exc:  # pragma: no cover - CLI entry point
            raise CommandError(f"User '{options['username']}' not found") from exc

        service = PilotRoleService()
        try:
            group = service.assign_role(user, options["role"])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Assigned role '{group.name}' to user '{user.username}'"
            )
        )
