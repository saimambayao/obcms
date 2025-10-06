"""Management command to populate BARMM Ministries, Offices, and Agencies."""

from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from coordination.models import Organization

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Populate BARMM Ministries, Offices, and Agencies based on dataset definitions"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing organizations if they already exist",
        )

    def handle(self, *args, **options):
        try:
            import yaml
        except (
            ImportError
        ) as exc:  # pragma: no cover - executed only when dependency missing
            raise CommandError(
                "PyYAML is required to load BARMM organization datasets. Install it via 'pip install PyYAML'."
            ) from exc

        dataset_path = (
            Path(settings.BASE_DIR)
            / "data_imports"
            / "datasets"
            / "barmm_ministries.yaml"
        )

        if not dataset_path.exists():
            raise CommandError(f"Dataset not found: {dataset_path}")

        with dataset_path.open("r", encoding="utf-8") as dataset_file:
            dataset = yaml.safe_load(dataset_file) or {}

        ministries = dataset.get("ministries", [])
        other_entities = dataset.get("other_entities", [])

        self.stdout.write("Populating BARMM Ministries, Offices, and Agencies...")

        system_user, created = User.objects.get_or_create(
            username="system",
            defaults={
                "email": "system@bangsamoro.gov.ph",
                "first_name": "OBCMS",
                "last_name": "Admin",
                "is_active": True,
            },
        )

        if not created:
            desired_fields = {"first_name": "OBCMS", "last_name": "Admin"}
            updates = {
                field: value
                for field, value in desired_fields.items()
                if getattr(system_user, field) != value
            }
            if updates:
                for field, value in updates.items():
                    setattr(system_user, field, value)
                system_user.save(update_fields=list(updates.keys()))

        created_count = 0
        updated_count = 0

        def upsert_organization(entry, parent_name=None):
            nonlocal created_count, updated_count

            name = entry["name"]
            acronym = entry.get("acronym", "")
            mandate = entry.get("mandate", "")
            powers_list = entry.get("powers_and_functions", []) or []
            powers = "\n".join(powers_list)

            description_parts = []
            if parent_name:
                description_parts.append(f"Attached to {parent_name}.")
            if mandate:
                description_parts.append(mandate)
            description = " ".join(description_parts).strip()

            defaults = {
                "acronym": acronym,
                "organization_type": "bmoa",
                "description": description or mandate,
                "mandate": mandate,
                "powers_and_functions": powers,
                "is_active": True,
                "created_by": system_user,
            }

            org, created = Organization.objects.get_or_create(
                name=name, defaults=defaults
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created organization: {name}{f' ({acronym})' if acronym else ''}"
                    )
                )
                return

            should_update = (
                options["update"] or not org.mandate or not org.powers_and_functions
            )

            if should_update:
                org.acronym = acronym
                org.organization_type = "bmoa"
                org.description = description or mandate or org.description
                org.mandate = mandate
                org.powers_and_functions = powers
                org.is_active = True
                org.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated organization: {name}{f' ({acronym})' if acronym else ''}"
                    )
                )

        for ministry in ministries:
            upsert_organization(ministry)

            for attached in ministry.get("attached_agencies", []) or []:
                upsert_organization(attached, parent_name=ministry["name"])

        for entity in other_entities:
            upsert_organization(entity)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Created {created_count} organizations, updated {updated_count} organizations."
            )
        )
