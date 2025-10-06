"""Update municipality population totals and map metadata from curated datasets."""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Set

from django.core.management.base import BaseCommand
from django.db import transaction

from common.models import Municipality

from .populate_administrative_hierarchy import (
    POPULATION_DATASETS,
    MUNICIPALITY_GEODATA,
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
    """Populate municipality-level population and geographic fields using datasets."""

    help = (
        "Refresh population totals, coordinates, and GeoJSON boundaries for municipalities"
        " in the target regions (defaults to Regions IX, X, XI, XII)."
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
            help="Show updates without making database changes",
        )

    def handle(self, *args, **options):
        region_codes = options["regions"]
        dry_run = options["dry_run"]

        helper = HierarchyCommand()
        helper.stdout = self.stdout
        helper.stderr = self.stderr

        population_lookup = self._build_population_lookup(helper, region_codes)

        municipalities = (
            Municipality.objects.filter(province__region__code__in=region_codes)
            .select_related("province__region")
            .order_by("province__region__code", "province__name", "name")
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN: displaying pending municipality updates only")
            )

        updated_count = 0
        with transaction.atomic():
            for municipality in municipalities:
                pending: Dict[str, object] = {}

                population = self._resolve_population(population_lookup, municipality)
                if (
                    population is not None
                    and municipality.population_total != population
                ):
                    pending["population_total"] = population

                geometry = self._resolve_geometry(municipality)
                if geometry:
                    center = geometry.get("center")
                    if center and municipality.center_coordinates != center:
                        pending["center_coordinates"] = center

                    bbox = geometry.get("bounding_box")
                    if bbox and municipality.bounding_box != bbox:
                        pending["bounding_box"] = bbox

                    boundary = geometry.get("geojson")
                    if boundary and municipality.boundary_geojson != boundary:
                        pending["boundary_geojson"] = boundary

                if not pending:
                    continue

                label = (
                    f"{municipality.name}, {municipality.province.name}"
                    if municipality.province
                    else municipality.name
                )

                if dry_run:
                    field_list = ", ".join(sorted(pending.keys()))
                    self.stdout.write(f"Would update {label}: {field_list}")
                    continue

                for field, value in pending.items():
                    setattr(municipality, field, value)

                municipality.save(update_fields=list(pending.keys()))
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated {label}: {', '.join(sorted(pending.keys()))}"
                    )
                )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Completed municipality refresh for regions {', '.join(region_codes)} "
                    f"({updated_count} municipalities updated)"
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
            for province_name, province_data in region_data.items():
                municipalities = province_data.get("municipalities", {})
                for municipality_name, municipality_payload in municipalities.items():
                    population = municipality_payload.get("population")
                    if population is None:
                        continue

                    for key in self._candidate_keys(
                        name=municipality_name,
                        province=province_name,
                    ):
                        lookup.setdefault(key, population)

        return lookup

    def _resolve_population(
        self, lookup: Dict[str, int], municipality: Municipality
    ) -> Optional[int]:
        for key in self._candidate_keys(
            name=municipality.name,
            province=municipality.province.name if municipality.province else None,
            code=municipality.code,
        ):
            if key in lookup:
                return lookup[key]
        return None

    def _resolve_geometry(self, municipality: Municipality) -> Optional[dict]:
        geometry = MUNICIPALITY_GEODATA.get(municipality.code)
        if geometry:
            return geometry

        actual_keys = self._candidate_keys(
            name=municipality.name,
            province=municipality.province.name if municipality.province else None,
            code=municipality.code,
        )

        for payload in MUNICIPALITY_GEODATA.values():
            if not isinstance(payload, dict):
                continue
            dataset_keys = self._candidate_keys(
                name=payload.get("name"),
                province=payload.get("province"),
            )
            if actual_keys.intersection(dataset_keys):
                return payload

        return None

    def _candidate_keys(
        self,
        *,
        name: Optional[str],
        province: Optional[str] = None,
        code: Optional[str] = None,
    ) -> Set[str]:
        raw_values: Set[str] = set()

        if code:
            raw_values.add(code)

        if name:
            raw_values.add(name)

        if name and province:
            raw_values.add(f"{name} {province}")
            raw_values.add(f"{province} {name}")

        if province:
            raw_values.add(province)

        normalised_values = set()
        for value in raw_values:
            normalised = self._normalise_key(value)
            if normalised:
                normalised_values.add(normalised)

        return normalised_values

    @staticmethod
    def _normalise_key(value: str) -> str:
        slug = value.lower().replace("_", " ").replace("-", " ")

        replacements = [
            ("city of ", ""),
            ("municipality of ", ""),
            ("province of ", ""),
            (" municipality", ""),
            (" city", ""),
            (" (huc)", ""),
            ("huc ", ""),
            (" sg", " special geographic area"),
        ]

        for old, new in replacements:
            slug = slug.replace(old, new)

        tokens = [token for token in slug.split() if token]
        if tokens and tokens[0] in ROMAN_NUMERALS:
            tokens = tokens[1:]

        cleaned = "".join(tokens)
        return cleaned
