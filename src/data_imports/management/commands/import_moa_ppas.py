"""Management command to import MOA PPAs from YAML datasets."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from coordination.models import Organization
from monitoring.models import MonitoringEntry

User = get_user_model()


class Command(BaseCommand):
    help = "Import MOA Programs, Projects, and Activities from YAML datasets"

    def add_arguments(self, parser):
        parser.add_argument(
            "--moa",
            dest="moa_filter",
            help="Limit import to a specific MOA name or acronym",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing records when titles already exist",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse datasets and show summary without writing to the database",
        )

    def handle(self, *args, **options):
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise CommandError(
                "PyYAML is required to import MOA PPAs. Install it via 'pip install PyYAML'."
            ) from exc

        dataset_dir = (
            Path(settings.BASE_DIR).parent / "data_imports" / "datasets" / "ppa"
        )

        if not dataset_dir.exists():
            raise CommandError(f"Dataset directory not found: {dataset_dir}")

        moa_filter = options.get("moa_filter")
        allow_update = options.get("update")
        dry_run = options.get("dry_run")

        yaml_files = sorted(dataset_dir.glob("*.yaml"))
        if not yaml_files:
            self.stdout.write(self.style.WARNING("No YAML files found to import."))
            return

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
        skipped_count = 0
        missing_orgs: Dict[str, int] = {}

        def normalize_indicator_entries(entries: Optional[Iterable[Dict[str, Any]]]) -> Iterable[Dict[str, Any]]:
            for entry in entries or []:
                indicator = (entry or {}).get("indicator")
                if not indicator:
                    continue
                target = (entry or {}).get("target")
                yield {"indicator": indicator, "target": target}

        for yaml_path in yaml_files:
            with yaml_path.open("r", encoding="utf-8") as stream:
                payload = yaml.safe_load(stream) or {}

            moa_name = payload.get("moa")
            acronym = payload.get("acronym")

            if moa_filter and moa_filter.lower() not in {
                (moa_name or "").lower(),
                (acronym or "").lower(),
            }:
                continue

            organization = self._resolve_organization(moa_name, acronym)
            if not organization:
                key = moa_name or acronym or yaml_path.stem
                missing_orgs[key] = missing_orgs.get(key, 0) + len(payload.get("ppas", []))
                self.stdout.write(
                    self.style.ERROR(
                        f"Skipping dataset '{yaml_path.name}' – implementing organization not found: {moa_name or acronym}"
                    )
                )
                continue

            ppas = payload.get("ppas", []) or []
            special_provisions = payload.get("special_provisions", []) or []

            special_lookup: Dict[str, list] = {}
            remaining_special = []
            for provision in special_provisions:
                title_raw = (provision or {}).get("title", "")
                details_raw = (provision or {}).get("details") or ""
                title = title_raw.strip()
                details = details_raw.strip()
                if not title and not details:
                    continue
                record = {"title": title, "details": details}
                remaining_special.append(record)
                key = title.lower() if title else ""
                special_lookup.setdefault(key, []).append(record)

            for entry in ppas:
                title = entry.get("title", "").strip()
                if not title:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping unnamed PPA in dataset '{yaml_path.name}'"
                        )
                    )
                    continue

                description = (entry.get("description") or "").strip()
                budget_raw = entry.get("approved_budget")
                budget_value = self._parse_decimal(budget_raw)

                outcome_list = list(normalize_indicator_entries(entry.get("outcome_indicators")))
                output_list = list(normalize_indicator_entries(entry.get("output_indicators")))

                outcome_framework: Dict[str, Any] = {}
                if outcome_list:
                    outcome_framework["outcomes"] = outcome_list
                if output_list:
                    outcome_framework["outputs"] = output_list

                legacy_outcome_text = "\n".join(
                    f"- {item['indicator']}: {item.get('target', '')}"
                    for item in outcome_list
                )
                legacy_output_text = "\n".join(
                    f"- {item['indicator']}: {item.get('target', '')}"
                    for item in output_list
                )

                special_text = ""
                bucket = special_lookup.get(title.lower())
                if bucket:
                    record = bucket.pop(0)
                    special_text = record.get("details", "")
                    if record in remaining_special:
                        remaining_special.remove(record)

                defaults = {
                    "category": "moa_ppa",
                    "summary": description,
                    "status": "planning",
                    "progress": 0,
                    "lead_organization": organization,
                    "implementing_moa": organization,
                    "budget_allocation": budget_value,
                    "budget_currency": "PHP",
                    "outcome_framework": outcome_framework,
                    "outcome_indicators": legacy_outcome_text,
                    "accomplishments": "",
                    "challenges": "",
                    "support_required": (
                        f"Special Provision:\n{special_text}" if special_text else ""
                    ),
                    "follow_up_actions": legacy_output_text,
                    "created_by": system_user,
                    "updated_by": system_user,
                }

                if dry_run:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.HTTP_INFO(
                            f"[DRY RUN] Would import '{title}' for {organization.name}"
                        )
                    )
                    continue

                with transaction.atomic():
                    entry_obj, created = MonitoringEntry.objects.get_or_create(
                        title=title,
                        category="moa_ppa",
                        implementing_moa=organization,
                        defaults=defaults,
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created MOA PPA: {title} ({organization.acronym or organization.name})"
                            )
                        )
                    else:
                        if allow_update:
                            for field, value in defaults.items():
                                if field == "created_by":
                                    continue
                                setattr(entry_obj, field, value)
                            update_fields = [
                                field for field in defaults.keys() if field != "created_by"
                            ]
                            entry_obj.save(update_fields=update_fields)
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Updated MOA PPA: {title} ({organization.acronym or organization.name})"
                                )
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.HTTP_INFO(
                                    f"Skipped existing MOA PPA (use --update to overwrite): {title}"
                                )
                            )

            if not dry_run and remaining_special:
                lines: list[str] = []
                for record in remaining_special:
                    title = record.get("title", "")
                    details = record.get("details", "")
                    if title:
                        lines.append(f"{title}:\n{details}")
                    else:
                        lines.append(details)
                aggregated_text = "Special Provisions:\n\n" + "\n\n".join(lines)
                should_update_org = allow_update or not organization.notes
                if should_update_org and organization.notes != aggregated_text:
                    organization.notes = aggregated_text
                    organization.save(update_fields=["notes", "updated_at"])

        summary_parts = [
            f"Created: {created_count}",
            f"Updated: {updated_count}",
            f"Skipped: {skipped_count}",
        ]
        self.stdout.write(self.style.SUCCESS("Import summary -> " + ", ".join(summary_parts)))

        if missing_orgs:
            self.stdout.write("\nOrganizations not found:")
            for name, count in missing_orgs.items():
                self.stdout.write(f" - {name} (missing {count} PPAs)")

    def _resolve_organization(self, name: Optional[str], acronym: Optional[str]) -> Optional[Organization]:
        """Return the organization using name or acronym."""

        candidates = Organization.objects.none()
        if name:
            candidates = Organization.objects.filter(name__iexact=name)
            if candidates.exists():
                return candidates.first()

        if acronym:
            candidates = Organization.objects.filter(acronym__iexact=acronym)
            if candidates.exists():
                return candidates.first()

        return None

    def _parse_decimal(self, raw_value: Any) -> Optional[Decimal]:
        if raw_value in (None, "", 0):
            return None
        try:
            return Decimal(str(raw_value))
        except (ValueError, ArithmeticError):
            self.stdout.write(
                self.style.WARNING(
                    f"Could not parse decimal value '{raw_value}', defaulting to None"
                )
            )
            return None
