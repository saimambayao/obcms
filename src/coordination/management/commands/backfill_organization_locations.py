"""Backfill newly added organization location fields from existing metadata."""

import re
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from common.models import Barangay, Municipality, Province, Region
from coordination.models import Organization


def _normalize(text: str) -> str:
    """Return a lowercase, punctuation-stripped value for loose comparisons."""

    normalized = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return normalized.strip()


class Command(BaseCommand):
    """Populate organization.region/province/municipality/barangay when possible."""

    help = (
        "Attempt to infer the headquarters location for partner organizations "
        "based on existing address and coverage fields."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show proposed updates without saving changes.",
        )
        parser.add_argument(
            "--organization",
            dest="organization_ids",
            nargs="+",
            help="Limit backfill to the specified organization UUIDs.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        limit_ids = options.get("organization_ids") or []

        if limit_ids:
            organizations = Organization.objects.filter(pk__in=limit_ids)
            missing_ids = set(limit_ids) - set(str(org.pk) for org in organizations)
            if missing_ids:
                raise CommandError(
                    f"The following organization IDs were not found: {', '.join(sorted(missing_ids))}"
                )
        else:
            organizations = Organization.objects.all()

        region_lookup = self._build_lookup(Region.objects.all(), include_code=True)
        province_lookup = self._build_lookup(Province.objects.select_related("region"))
        municipality_lookup = self._build_lookup(
            Municipality.objects.select_related("province__region")
        )
        barangay_lookup = self._build_lookup(
            Barangay.objects.select_related("municipality__province__region")
        )

        total_examined = 0
        updated_counter = defaultdict(int)
        changes = []

        timestamp = timezone.now().isoformat()
        self.stdout.write("")
        self.stdout.write(
            f"[{timestamp}] Starting organization location backfill "
            f"({'dry-run' if dry_run else 'apply'})"
        )

        with transaction.atomic():
            for organization in organizations.select_related(
                "region", "province", "municipality", "barangay"
            ):
                total_examined += 1
                missing_fields = [
                    field
                    for field in ("region", "province", "municipality", "barangay")
                    if getattr(organization, field + "_id") is None
                ]
                if not missing_fields:
                    continue

                reference_text = self._build_reference_text(organization)
                if not reference_text:
                    continue

                detected = self._detect_location_matches(
                    reference_text,
                    region_lookup,
                    province_lookup,
                    municipality_lookup,
                    barangay_lookup,
                )

                if not detected:
                    continue

                update_fields = []
                previous_state = {
                    "region": organization.region,
                    "province": organization.province,
                    "municipality": organization.municipality,
                    "barangay": organization.barangay,
                }

                for field in ("barangay", "municipality", "province", "region"):
                    match = detected.get(field)
                    if match and getattr(organization, field) != match:
                        setattr(organization, field, match)
                        update_fields.append(field)

                if update_fields:
                    try:
                        organization.clean()
                    except Exception as error:
                        # Revert any in-memory assignments that failed validation.
                        for field, previous_value in previous_state.items():
                            setattr(organization, field, previous_value)
                        self.stderr.write(
                            self.style.WARNING(
                                f"Unable to update {organization} due to validation error: {error}"
                            )
                        )
                        continue

                    changes.append(
                        (
                            organization.pk,
                            {
                                field: getattr(organization, field)
                                for field in update_fields
                            },
                        )
                    )
                    updated_counter[len(update_fields)] += 1

                    if not dry_run:
                        organization.save(update_fields=update_fields)

            if dry_run:
                transaction.set_rollback(True)

        if not changes:
            self.stdout.write(self.style.WARNING("No updates were applied."))
            return

        self.stdout.write("")
        for org_id, fields in changes:
            field_summary = ", ".join(
                f"{field} -> {getattr(value, 'name', getattr(value, 'code', value))}"
                for field, value in fields.items()
            )
            self.stdout.write(f"{org_id}: {field_summary}")

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Analyzed {total_examined} organizations; "
                f"prepared updates for {len(changes)} records "
                f"({'dry-run' if dry_run else 'saved'})"
            )
        )
        for field_count, occurrences in sorted(updated_counter.items()):
            self.stdout.write(
                f"  - {occurrences} organizations updated ({field_count} fields)"
            )

    def _build_lookup(self, queryset, include_code: bool = False) -> dict:
        """Map normalized labels to model instances."""

        lookup = {}
        for instance in queryset:
            if not getattr(instance, "name", None):
                continue
            normalized_name = _normalize(instance.name)
            lookup.setdefault(normalized_name, instance)

            if include_code and getattr(instance, "code", None):
                normalized_code = _normalize(instance.code)
                lookup.setdefault(normalized_code, instance)

        return lookup

    def _build_reference_text(self, organization: Organization) -> str:
        """Gather potential location hints from organization fields."""

        components = [
            organization.address,
            organization.mailing_address,
            organization.geographic_coverage,
            organization.target_beneficiaries,
            organization.areas_of_expertise,
            organization.notes,
            organization.description,
        ]
        text = " ".join(part for part in components if part).strip()
        return _normalize(text) if text else ""

    def _detect_location_matches(
        self,
        normalized_text: str,
        region_lookup: dict,
        province_lookup: dict,
        municipality_lookup: dict,
        barangay_lookup: dict,
    ) -> dict:
        """Return detected location components based on normalized text."""

        matches = {}

        # Attempt precise barangay matches first (most specific).
        barangay_match = self._find_single_match(normalized_text, barangay_lookup)
        if barangay_match:
            matches["barangay"] = barangay_match
            municipality = barangay_match.municipality
            province = municipality.province if municipality else None
            region = province.region if province else None
            matches.setdefault("municipality", municipality)
            matches.setdefault("province", province)
            matches.setdefault("region", region)
            return matches

        municipality_match = self._find_single_match(
            normalized_text, municipality_lookup
        )
        if municipality_match:
            matches["municipality"] = municipality_match
            province = municipality_match.province
            region = province.region if province else None
            matches.setdefault("province", province)
            matches.setdefault("region", region)
            return matches

        province_match = self._find_single_match(normalized_text, province_lookup)
        if province_match:
            matches["province"] = province_match
            matches.setdefault("region", province_match.region)
            return matches

        region_match = self._find_single_match(normalized_text, region_lookup)
        if region_match:
            matches["region"] = region_match

        return matches

    def _find_single_match(self, normalized_text: str, lookup: dict):
        """Return a matched instance if exactly one label is detected."""

        candidates = []
        for key, instance in lookup.items():
            if not key:
                continue
            if f" {key} " in f" {normalized_text} ":
                candidates.append(instance)

        if len(candidates) == 1:
            return candidates[0]
        return None
