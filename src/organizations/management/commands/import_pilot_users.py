"""Bulk import pilot users from a CSV file."""

from __future__ import annotations

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from organizations.services import PilotUserService

REQUIRED_COLUMNS = {"email", "first_name", "last_name", "organization", "role"}


class Command(BaseCommand):
    help = "Import pilot users from a CSV file (see docs/deployment/USER_IMPORT_CSV_FORMAT.md)"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("csv_path", help="Path to the CSV file to import")
        parser.add_argument("--dry-run", action="store_true", help="Validate the CSV without creating users")
        parser.add_argument(
            "--send-emails",
            action="store_true",
            help="Send welcome emails to newly created users",
        )

    def handle(self, *args, **options):  # type: ignore[override]
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        service = PilotUserService()
        created_count = 0
        errors = []

        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing_cols = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing_cols:
                raise CommandError(
                    "CSV file is missing required columns: " + ", ".join(sorted(missing_cols))
                )

            for index, row in enumerate(reader, start=2):  # include header row
                email = row.get("email", "").strip()
                username = email.split("@")[0]
                first_name = row.get("first_name", "").strip()
                last_name = row.get("last_name", "").strip()
                organization = row.get("organization", "").strip()
                role = row.get("role", "").strip()

                if not email or not organization or not role:
                    errors.append((index, "Missing required fields"))
                    continue

                if options["dry_run"]:
                    continue

                try:
                    service.create_pilot_user(
                        username=username,
                        email=email,
                        organization_code=organization,
                        role=role,
                        first_name=first_name,
                        last_name=last_name,
                        phone=row.get("phone", "").strip() or None,
                        position=row.get("position", "").strip() or None,
                        department=row.get("department", "").strip() or None,
                        send_welcome_email=options["send_emails"],
                    )
                    created_count += 1
                except Exception as exc:
                    errors.append((index, str(exc)))

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run complete - no users created"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Created {created_count} users"))

        if errors:
            self.stdout.write(self.style.ERROR("Errors encountered:"))
            for row_number, message in errors:
                self.stdout.write(f"  Row {row_number}: {message}")

        if errors and not options["dry_run"]:
            raise CommandError("Import completed with errors")
