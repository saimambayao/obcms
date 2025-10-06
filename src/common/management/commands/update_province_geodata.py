"""Update province population totals and map metadata from curated datasets."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Optional, Set

from django.core.management.base import BaseCommand
from django.db import transaction

from common.models import Province

from .populate_administrative_hierarchy import (
    POPULATION_DATASETS,
    PROVINCE_GEODATA,
    Command as HierarchyCommand,
)


ROMAN_NUMERALS = {
    "i",
    "ii",
    "iii",
    "iv",
    "v",
    "vi",
    "vii",
    "viii",
    "ix",
    "x",
    "xi",
    "xii",
    "xiii",
    "xiv",
    "xv",
}


class Command(BaseCommand):
    """Populate province-level population and geographic fields using datasets."""

    help = (
        "Refresh population totals, coordinates, and GeoJSON maps for provinces in "
        "target regions (defaults to Regions IX, X, XI, XII)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--regions",
            nargs="+",
            default=["IX", "X", "XI", "XII"],
            help="Region codes to process (default: IX X XI XII)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show updates without modifying the database",
        )

    def handle(self, *args, **options):
        region_codes = options["regions"]
        dry_run = options["dry_run"]

        helper = HierarchyCommand()
        helper.stdout = self.stdout
        helper.stderr = self.stderr

        population_lookup = self._build_population_lookup(helper, region_codes)

        provinces = (
            Province.objects.filter(region__code__in=region_codes)
            .select_related("region")
            .order_by("region__code", "name")
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN: displaying pending province updates only")
            )

        updated_count = 0
        with transaction.atomic():
            for province in provinces:
                pending_fields = {}

                population = self._resolve_population(population_lookup, province)
                if (
                    population is not None
                    and province.population_total != population
                ):
                    pending_fields["population_total"] = population

                geometry = self._resolve_geometry(province)
                if geometry:
                    center = geometry.get("center")
                    if center and province.center_coordinates != center:
                        pending_fields["center_coordinates"] = center

                    bbox = geometry.get("bounding_box")
                    if bbox and province.bounding_box != bbox:
                        pending_fields["bounding_box"] = bbox

                    boundary = geometry.get("geojson")
                    if boundary and province.boundary_geojson != boundary:
                        pending_fields["boundary_geojson"] = boundary

                if not pending_fields:
                    continue

                label = f"{province.name} (Region {province.region.code})"
                if dry_run:
                    field_list = ", ".join(sorted(pending_fields.keys()))
                    self.stdout.write(f"Would update {label}: {field_list}")
                    continue

                for field, value in pending_fields.items():
                    setattr(province, field, value)

                province.save(update_fields=list(pending_fields.keys()))
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated {label}: {', '.join(sorted(pending_fields.keys()))}"
                    )
                )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Completed province refresh for regions {', '.join(region_codes)} "
                    f"({updated_count} provinces updated)"
                )
            )

    def _build_population_lookup(
        self, helper: HierarchyCommand, region_codes: Iterable[str]
    ) -> Dict[str, int]:
        lookup: Dict[str, int] = {}

        for region_code in region_codes:
            dataset_path = POPULATION_DATASETS.get(region_code)
            if not dataset_path or not dataset_path.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Population dataset for region {region_code} is missing"
                    )
                )
                continue

            region_data = helper.load_population_dataset(region_code)
            for key, payload in region_data.items():
                population = payload.get("population")
                if population is None:
                    continue

                for candidate in self._candidate_keys(key):
                    lookup[candidate] = population

        return lookup

    @staticmethod
    def _resolve_population(lookup: Dict[str, int], province: Province) -> Optional[int]:
        for candidate in Command._candidate_keys(province.code, province.name):
            if candidate in lookup:
                return lookup[candidate]
        return None

    @classmethod
    def _resolve_geometry(cls, province: Province) -> Optional[dict]:
        geometry = PROVINCE_GEODATA.get(province.code)
        if geometry:
            return geometry

        province_keys = cls._candidate_keys(province.code, province.name)
        for code, payload in PROVINCE_GEODATA.items():
            dataset_keys = cls._candidate_keys(code, payload.get("name"))
            if province_keys.intersection(dataset_keys):
                return payload

        return None

    @classmethod
    def _candidate_keys(cls, *values: Optional[str]) -> Set[str]:
        keys: Set[str] = set()
        for value in values:
            if not value:
                continue

            lower = value.lower()
            keys.add(lower)

            normalized = cls._normalise_key(lower)
            if normalized:
                keys.add(normalized)

            if "-" in lower:
                suffix = lower.split("-", 1)[1]
                keys.add(suffix)
                normalized_suffix = cls._normalise_key(suffix)
                if normalized_suffix:
                    keys.add(normalized_suffix)

            if "_" in lower:
                suffix = lower.split("_", 1)[1]
                keys.add(suffix)
                normalized_suffix = cls._normalise_key(suffix)
                if normalized_suffix:
                    keys.add(normalized_suffix)

        return {key for key in keys if key}

    @staticmethod
    def _normalise_key(value: str) -> str:
        slug = value.lower().replace("_", " ").replace("-", " ")

        for old, new in (
            ("city of ", ""),
            ("province of ", ""),
            (" province", ""),
            (" city", ""),
            (" (huc)", ""),
            ("huc ", ""),
        ):
            slug = slug.replace(old, new)

        tokens = [token for token in slug.split() if token]
        if tokens and tokens[0] in ROMAN_NUMERALS:
            tokens = tokens[1:]

        slug = " ".join(tokens)
        return re.sub(r"[^a-z0-9]+", "", slug)
