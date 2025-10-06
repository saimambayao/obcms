import json
import re
import unicodedata
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from common.models import Barangay, Municipality, Province, Region


BASE_DIR = Path(__file__).resolve().parents[3]
DATASET_DIR = BASE_DIR / "data_imports" / "datasets"

POPULATION_DATASETS = {
    "IX": DATASET_DIR / "region_ix_population_raw.txt",
    "X": DATASET_DIR / "region_x_population_raw.txt",
    "XI": DATASET_DIR / "region_xi_population_raw.txt",
    "XII": DATASET_DIR / "region_xii_population_raw.txt",
}


def _load_province_geodata() -> dict:
    """Return province geodata payload if the dataset is present."""

    dataset_path = DATASET_DIR / "province_geo.json"
    if not dataset_path.exists():
        return {}

    try:
        with dataset_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return {}


PROVINCE_GEODATA = _load_province_geodata()


def _load_municipality_geodata() -> dict:
    """Return municipality geodata payload if the dataset is present."""

    dataset_path = DATASET_DIR / "municipality_geo.json"
    if not dataset_path.exists():
        return {}

    try:
        with dataset_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return {}


MUNICIPALITY_GEODATA = _load_municipality_geodata()


REGION_STRUCTURE = {
    "IX": {
        "name": "Zamboanga Peninsula",
        "description": "Region IX encompasses the Zamboanga Peninsula and nearby islands in western Mindanao.",
        "provinces": [
            {
                "code": "ZAM_DEL_NORTE",
                "name": "Zamboanga del Norte",
                "capital": "Dipolog City",
                "municipalities": [
                    {"name": "Dipolog City", "municipality_type": "component_city"},
                    {"name": "Dapitan City", "municipality_type": "component_city"},
                    {"name": "Baliguian"},
                    {"name": "Godod"},
                    {"name": "Gutalac"},
                    {"name": "Jose Dalman (Ponot)"},
                    {"name": "Kalawit"},
                    {"name": "Katipunan"},
                    {"name": "La Libertad"},
                    {"name": "Labason"},
                    {"name": "Leon B. Postigo (Bacungan)"},
                    {"name": "Liloy"},
                    {"name": "Manukan"},
                    {"name": "Mutia"},
                    {"name": "Pinan (New Pinan)"},
                    {"name": "Polanco"},
                    {"name": "President Manuel A. Roxas"},
                    {"name": "Rizal"},
                    {"name": "Salug"},
                    {"name": "Sergio Osmena Sr."},
                    {"name": "Siayan"},
                    {"name": "Sibuco"},
                    {"name": "Sibutad"},
                    {"name": "Sindangan"},
                    {"name": "Siocon"},
                    {"name": "Sirawai"},
                    {"name": "Tampilisan"},
                ],
            },
            {
                "code": "ZAM_DEL_SUR",
                "name": "Zamboanga del Sur",
                "capital": "Pagadian City",
                "municipalities": [
                    {"name": "Pagadian City", "municipality_type": "component_city"},
                    {"name": "Aurora"},
                    {"name": "Bayog"},
                    {"name": "Dimataling"},
                    {"name": "Dinas"},
                    {"name": "Dumalinao"},
                    {"name": "Dumingag"},
                    {"name": "Guipos"},
                    {"name": "Josefina"},
                    {"name": "Kumalarang"},
                    {"name": "Labangan"},
                    {"name": "Lakewood"},
                    {"name": "Lapuyan"},
                    {"name": "Mahayag"},
                    {"name": "Margosatubig"},
                    {"name": "Midsalip"},
                    {"name": "Molave"},
                    {"name": "Pitogo"},
                    {"name": "Ramon Magsaysay"},
                    {"name": "San Miguel"},
                    {"name": "San Pablo"},
                    {"name": "Sominot"},
                    {"name": "Tabina"},
                    {"name": "Tambulig"},
                    {"name": "Tigbao"},
                    {"name": "Tukuran"},
                    {"name": "Vincenzo A. Sagun"},
                ],
            },
            {
                "code": "ZAM_SIBUGAY",
                "name": "Zamboanga Sibugay",
                "capital": "Ipil",
                "municipalities": [
                    {"name": "Alicia"},
                    {"name": "Buug"},
                    {"name": "Diplahan"},
                    {"name": "Imelda"},
                    {"name": "Ipil"},
                    {"name": "Kabasalan"},
                    {"name": "Mabuhay"},
                    {"name": "Malangas"},
                    {"name": "Naga"},
                    {"name": "Olutanga"},
                    {"name": "Payao"},
                    {"name": "Roseller Lim"},
                    {"name": "Siay"},
                    {"name": "Talusan"},
                    {"name": "Titay"},
                    {"name": "Tungawan"},
                ],
            },
            {
                "code": "HUC_ZAMBOANGA_CITY",
                "name": "Zamboanga City (HUC)",
                "capital": "Zamboanga City",
                "municipalities": [
                    {
                        "name": "Zamboanga City",
                        "municipality_type": "independent_city",
                    }
                ],
            },
            {
                "code": "HUC_ISABELA_CITY",
                "name": "Isabela City (Administered by Region IX)",
                "capital": "Isabela City",
                "municipalities": [
                    {
                        "name": "Isabela City",
                        "municipality_type": "independent_city",
                    }
                ],
            },
            {
                "code": "SULU",
                "name": "Sulu",
                "capital": "Jolo",
                "municipalities": [
                    {"name": "Banguingui"},
                    {"name": "Hadji Panglima Tahil"},
                    {"name": "Indanan"},
                    {"name": "Jolo", "municipality_type": "component_city"},
                    {"name": "Kalingalan Caluang"},
                    {"name": "Lugus"},
                    {"name": "Luuk"},
                    {"name": "Maimbung"},
                    {"name": "Omar"},
                    {"name": "Panamao"},
                    {"name": "Pandami"},
                    {"name": "Panglima Estino"},
                    {"name": "Pangutaran"},
                    {"name": "Parang"},
                    {"name": "Pata"},
                    {"name": "Patikul"},
                    {"name": "Siasi"},
                    {"name": "Talipao"},
                    {"name": "Tapul"},
                ],
            },
        ],
    },
    "X": {
        "name": "Northern Mindanao",
        "description": "Region X comprises the provinces of Bukidnon, Camiguin, Lanao del Norte, Misamis Occidental, and Misamis Oriental.",
        "provinces": [
            {
                "code": "BUKIDNON",
                "name": "Bukidnon",
                "capital": "Malaybalay City",
                "municipalities": [
                    {"name": "Malaybalay City", "municipality_type": "component_city"},
                    {"name": "Valencia City", "municipality_type": "component_city"},
                    {"name": "Baungon"},
                    {"name": "Cabanglasan"},
                    {"name": "Damulog"},
                    {"name": "Dangcagan"},
                    {"name": "Don Carlos"},
                    {"name": "Impasugong"},
                    {"name": "Kadingilan"},
                    {"name": "Kalilangan"},
                    {"name": "Kibawe"},
                    {"name": "Kitaotao"},
                    {"name": "Lantapan"},
                    {"name": "Libona"},
                    {"name": "Malitbog"},
                    {"name": "Manolo Fortich"},
                    {"name": "Maramag"},
                    {"name": "Pangantucan"},
                    {"name": "Quezon"},
                    {"name": "San Fernando"},
                    {"name": "Sumilao"},
                    {"name": "Talakag"},
                ],
            },
            {
                "code": "CAMIGUIN",
                "name": "Camiguin",
                "capital": "Mambajao",
                "municipalities": [
                    {"name": "Catarman"},
                    {"name": "Guinsiliban"},
                    {"name": "Mahinog"},
                    {"name": "Mambajao"},
                    {"name": "Sagay"},
                ],
            },
            {
                "code": "LANAO_DEL_NORTE",
                "name": "Lanao del Norte",
                "capital": "Tubod",
                "municipalities": [
                    {"name": "Bacolod"},
                    {"name": "Baloi"},
                    {"name": "Baroy"},
                    {"name": "Kapatagan"},
                    {"name": "Kauswagan"},
                    {"name": "Kolambugan"},
                    {"name": "Lala"},
                    {"name": "Linamon"},
                    {"name": "Magsaysay"},
                    {"name": "Maigo"},
                    {"name": "Matungao"},
                    {"name": "Munai"},
                    {"name": "Nunungan"},
                    {"name": "Pantao Ragat"},
                    {"name": "Pantar"},
                    {"name": "Poona Piagapo"},
                    {"name": "Salvador"},
                    {"name": "Sapad"},
                    {"name": "Sultan Naga Dimaporo"},
                    {"name": "Tagoloan"},
                    {"name": "Tangcal"},
                    {"name": "Tubod"},
                ],
            },
            {
                "code": "MIS_OCCIDENTAL",
                "name": "Misamis Occidental",
                "capital": "Oroquieta City",
                "municipalities": [
                    {"name": "Oroquieta City", "municipality_type": "component_city"},
                    {"name": "Ozamiz City", "municipality_type": "component_city"},
                    {"name": "Tangub City", "municipality_type": "component_city"},
                    {"name": "Aloran"},
                    {"name": "Baliangao"},
                    {"name": "Bonifacio"},
                    {"name": "Calamba"},
                    {"name": "Clarin"},
                    {"name": "Concepcion"},
                    {"name": "Don Victoriano Chiongbian"},
                    {"name": "Jimenez"},
                    {"name": "Lopez Jaena"},
                    {"name": "Panaon"},
                    {"name": "Plaridel"},
                    {"name": "Sapang Dalaga"},
                    {"name": "Sinacaban"},
                    {"name": "Tudela"},
                ],
            },
            {
                "code": "MIS_ORIENTAL",
                "name": "Misamis Oriental",
                "capital": "Cagayan de Oro City",
                "municipalities": [
                    {"name": "El Salvador City", "municipality_type": "component_city"},
                    {"name": "Gingoog City", "municipality_type": "component_city"},
                    {"name": "Alubijid"},
                    {"name": "Balingasag"},
                    {"name": "Balingoan"},
                    {"name": "Binuangan"},
                    {"name": "Claveria"},
                    {"name": "Gitagum"},
                    {"name": "Initao"},
                    {"name": "Jasaan"},
                    {"name": "Kinoguitan"},
                    {"name": "Lagonglong"},
                    {"name": "Laguindingan"},
                    {"name": "Libertad"},
                    {"name": "Lugait"},
                    {"name": "Magsaysay"},
                    {"name": "Manticao"},
                    {"name": "Medina"},
                    {"name": "Naawan"},
                    {"name": "Opol"},
                    {"name": "Salay"},
                    {"name": "Sugbongcogon"},
                    {"name": "Tagoloan"},
                    {"name": "Talisayan"},
                    {"name": "Villanueva"},
                ],
            },
            {
                "code": "HUC_CAGAYAN_DE_ORO",
                "name": "Cagayan de Oro City (HUC)",
                "capital": "Cagayan de Oro City",
                "municipalities": [
                    {
                        "name": "Cagayan de Oro City",
                        "municipality_type": "independent_city",
                    }
                ],
            },
            {
                "code": "HUC_ILIGAN_CITY",
                "name": "Iligan City (HUC)",
                "capital": "Iligan City",
                "municipalities": [
                    {
                        "name": "Iligan City",
                        "municipality_type": "independent_city",
                    }
                ],
            },
        ],
    },
    "XI": {
        "name": "Davao Region",
        "description": "Region XI comprises the provinces of Davao del Norte, Davao del Sur, Davao Oriental, Davao de Oro, and Davao Occidental.",
        "provinces": [
            {
                "code": "DAVAO_DE_ORO",
                "name": "Davao de Oro",
                "capital": "Nabunturan",
                "municipalities": [
                    {"name": "Compostela"},
                    {"name": "Laak"},
                    {"name": "Mabini"},
                    {"name": "Maco"},
                    {"name": "Maragusan"},
                    {"name": "Mawab"},
                    {"name": "Monkayo"},
                    {"name": "Montevista"},
                    {"name": "Nabunturan"},
                    {"name": "New Bataan"},
                    {"name": "Pantukan"},
                ],
            },
            {
                "code": "DAVAO_DEL_NORTE",
                "name": "Davao del Norte",
                "capital": "Tagum City",
                "municipalities": [
                    {"name": "Tagum City", "municipality_type": "component_city"},
                    {"name": "Panabo City", "municipality_type": "component_city"},
                    {
                        "name": "Island Garden City of Samal",
                        "municipality_type": "component_city",
                    },
                    {"name": "Asuncion"},
                    {"name": "Braulio E. Dujali"},
                    {"name": "Carmen"},
                    {"name": "Kapalong"},
                    {"name": "New Corella"},
                    {"name": "San Isidro"},
                    {"name": "Santo Tomas"},
                    {"name": "Talaingod"},
                ],
            },
            {
                "code": "DAVAO_DEL_SUR",
                "name": "Davao del Sur",
                "capital": "Digos City",
                "municipalities": [
                    {"name": "Digos City", "municipality_type": "component_city"},
                    {"name": "Bansalan"},
                    {"name": "Hagonoy"},
                    {"name": "Kiblawan"},
                    {"name": "Magsaysay"},
                    {"name": "Malalag"},
                    {"name": "Matanao"},
                    {"name": "Padada"},
                    {"name": "Santa Cruz"},
                    {"name": "Sulop"},
                ],
            },
            {
                "code": "DAVAO_OCCIDENTAL",
                "name": "Davao Occidental",
                "capital": "Malita",
                "municipalities": [
                    {"name": "Don Marcelino"},
                    {"name": "Jose Abad Santos"},
                    {"name": "Malita"},
                    {"name": "Santa Maria"},
                    {"name": "Sarangani"},
                ],
            },
            {
                "code": "DAVAO_ORIENTAL",
                "name": "Davao Oriental",
                "capital": "Mati City",
                "municipalities": [
                    {"name": "Mati City", "municipality_type": "component_city"},
                    {"name": "Baganga"},
                    {"name": "Banaybanay"},
                    {"name": "Boston"},
                    {"name": "Caraga"},
                    {"name": "Cateel"},
                    {"name": "Governor Generoso"},
                    {"name": "Lupon"},
                    {"name": "Manay"},
                    {"name": "San Isidro"},
                    {"name": "Tarragona"},
                ],
            },
            {
                "code": "HUC_DAVAO_CITY",
                "name": "Davao City (HUC)",
                "capital": "Davao City",
                "municipalities": [
                    {
                        "name": "Davao City",
                        "municipality_type": "independent_city",
                    }
                ],
            },
        ],
    },
    "XII": {
        "name": "SOCCSKSARGEN",
        "description": "Region XII comprises South Cotabato, Cotabato, Sultan Kudarat, Sarangani, and the component cities in the area.",
        "provinces": [
            {
                "code": "COTABATO",
                "name": "Cotabato",
                "capital": "Kidapawan City",
                "municipalities": [
                    {"name": "Kidapawan City", "municipality_type": "component_city"},
                    {"name": "Alamada"},
                    {"name": "Aleosan"},
                    {"name": "Antipas"},
                    {"name": "Arakan"},
                    {"name": "Banisilan"},
                    {"name": "Carmen"},
                    {"name": "Kabacan"},
                    {"name": "Libungan"},
                    {"name": "M'lang"},
                    {"name": "Magpet"},
                    {"name": "Makilala"},
                    {"name": "Matalam"},
                    {"name": "Midsayap"},
                    {"name": "Pigcawayan"},
                    {"name": "Pikit"},
                    {"name": "President Roxas"},
                    {"name": "Tulunan"},
                ],
            },
            {
                "code": "SARANGANI",
                "name": "Sarangani",
                "capital": "Alabel",
                "municipalities": [
                    {"name": "Alabel"},
                    {"name": "Glan"},
                    {"name": "Kiamba"},
                    {"name": "Maasim"},
                    {"name": "Maitum"},
                    {"name": "Malapatan"},
                    {"name": "Malungon"},
                ],
            },
            {
                "code": "SOUTH_COTABATO",
                "name": "South Cotabato",
                "capital": "Koronadal City",
                "municipalities": [
                    {"name": "Koronadal City", "municipality_type": "component_city"},
                    {"name": "Banga"},
                    {"name": "Lake Sebu"},
                    {"name": "Norala"},
                    {"name": "Polomolok"},
                    {"name": "Santo Nino"},
                    {"name": "Surallah"},
                    {"name": "T'Boli"},
                    {"name": "Tampakan"},
                    {"name": "Tantangan"},
                    {"name": "Tupi"},
                ],
            },
            {
                "code": "SULTAN_KUDARAT",
                "name": "Sultan Kudarat",
                "capital": "Isulan",
                "municipalities": [
                    {"name": "Tacurong City", "municipality_type": "component_city"},
                    {"name": "Bagumbayan"},
                    {"name": "Columbio"},
                    {"name": "Esperanza"},
                    {"name": "Isulan"},
                    {"name": "Kalamansig"},
                    {"name": "Lambayong"},
                    {"name": "Lebak"},
                    {"name": "Lutayan"},
                    {"name": "Palimbang"},
                    {"name": "President Quirino"},
                    {"name": "Senator Ninoy Aquino"},
                ],
            },
            {
                "code": "HUC_GENERAL_SANTOS_CITY",
                "name": "General Santos City (HUC)",
                "capital": "General Santos City",
                "municipalities": [
                    {
                        "name": "General Santos City",
                        "municipality_type": "independent_city",
                    }
                ],
            },
        ],
    },
}


class Command(BaseCommand):
    """Populate the administrative hierarchy for priority Mindanao regions."""

    help = "Populate administrative hierarchy for Regions IX, X, XI, and XII"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.municipality_codes = {}

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update existing data",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            self.populate_regions()
            self.populate_provinces()
            self.populate_municipalities()
            self.populate_barangays_and_population()

        self.stdout.write(
            self.style.SUCCESS("Successfully populated administrative hierarchy")
        )

    @staticmethod
    def _normalize_code(value: str) -> str:
        """Create a deterministic uppercase code from a human readable value."""

        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        normalized = re.sub(r"[()]+", " ", normalized)
        normalized = re.sub(r"[^A-Za-z0-9]+", "_", normalized).strip("_")
        return normalized.upper()

    def _municipality_code(self, province_code: str, name: str) -> str:
        """Derive a unique code for a municipality within a province."""

        base_code = self._normalize_code(name)
        return f"{province_code}_{base_code}" if province_code else base_code

    def populate_regions(self):
        for code, data in REGION_STRUCTURE.items():
            Region.objects.update_or_create(
                code=code,
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "is_active": True,
                },
            )
            self.stdout.write(f"Upserted region: {code} - {data['name']}")

    def populate_provinces(self):
        for region_code, region_data in REGION_STRUCTURE.items():
            try:
                region = Region.objects.get(code=region_code)
            except Region.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Region {region_code} missing"))
                continue

            for province_data in region_data["provinces"]:
                defaults = {
                    "region": region,
                    "name": province_data["name"],
                    "capital": province_data["capital"],
                    "is_active": True,
                }

                geometry = PROVINCE_GEODATA.get(province_data["code"])
                if not geometry:
                    # Fall back to a case-insensitive name lookup when no code match exists.
                    geometry = next(
                        (
                            payload
                            for payload in PROVINCE_GEODATA.values()
                            if payload.get("name", "").lower()
                            == province_data["name"].lower()
                        ),
                        None,
                    )

                if geometry:
                    center = geometry.get("center")
                    if center:
                        defaults["center_coordinates"] = center

                    bounding_box = geometry.get("bounding_box")
                    if bounding_box:
                        defaults["bounding_box"] = bounding_box

                    boundary_geojson = geometry.get("geojson")
                    if boundary_geojson:
                        defaults["boundary_geojson"] = boundary_geojson

                Province.objects.update_or_create(
                    code=province_data["code"],
                    defaults=defaults,
                )
                self.stdout.write(
                    f"Upserted province: {province_data['code']} - {province_data['name']}"
                )

    def populate_municipalities(self):
        for region_data in REGION_STRUCTURE.values():
            for province_data in region_data["provinces"]:
                try:
                    province = Province.objects.get(code=province_data["code"])
                except Province.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Province {province_data['code']} missing; skipping municipalities"
                        )
                    )
                    continue

                for municipality in province_data["municipalities"]:
                    name = municipality["name"].strip()
                    municipality_type = municipality.get(
                        "municipality_type", "municipality"
                    )
                    code = municipality.get("code") or self._municipality_code(
                        province.code, name
                    )

                    defaults = {
                        "province": province,
                        "name": name,
                        "municipality_type": municipality_type,
                        "is_active": True,
                    }

                    geometry = MUNICIPALITY_GEODATA.get(code)
                    if not geometry:
                        target_province_name = province_data["name"].lower()
                        geometry = next(
                            (
                                payload
                                for payload in MUNICIPALITY_GEODATA.values()
                                if payload.get("name", "").lower() == name.lower()
                                and payload.get("province", "").lower()
                                == target_province_name
                            ),
                            None,
                        )

                    if geometry:
                        center = geometry.get("center")
                        if center:
                            defaults["center_coordinates"] = center

                        bounding_box = geometry.get("bounding_box")
                        if bounding_box:
                            defaults["bounding_box"] = bounding_box

                        boundary_geojson = geometry.get("geojson")
                        if boundary_geojson:
                            defaults["boundary_geojson"] = boundary_geojson

                    Municipality.objects.update_or_create(
                        code=code,
                        defaults=defaults,
                    )

                    key = (province.code, name.lower())
                    self.municipality_codes[key] = code
                    self.stdout.write(f"Upserted municipality: {code} - {name}")

    def populate_barangays_and_population(self):
        for region_code, dataset_path in POPULATION_DATASETS.items():
            population_data = self.load_population_dataset(region_code)
            if not population_data:
                continue

            for province_key, province_data in population_data.items():
                province = self._resolve_province(province_key)
                if not province:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Population dataset ({region_code}): province {province_key} not found"
                        )
                    )
                    continue

                province_population = province_data.get("population")
                if province_population is not None:
                    province.population_total = province_population
                    province.save(update_fields=["population_total"])

                for municipality_name, municipality_data in province_data.get(
                    "municipalities", {}
                ).items():
                    municipality = self._resolve_municipality(
                        province, municipality_name
                    )
                    if not municipality:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Population dataset ({region_code}): municipality {municipality_name} "
                                f"not found in province {province.name}"
                            )
                        )
                        continue

                    population = municipality_data.get("population")
                    if population is not None:
                        municipality.population_total = population
                        municipality.save(update_fields=["population_total"])

                    self._upsert_barangays(
                        municipality, municipality_data.get("barangays", {})
                    )

    def _resolve_province(self, identifier):
        try:
            return Province.objects.get(code=identifier)
        except Province.DoesNotExist:
            try:
                return Province.objects.get(name__iexact=identifier)
            except Province.DoesNotExist:
                return None

    def _resolve_municipality(self, province, name):
        try:
            return province.municipalities.get(name__iexact=name)
        except Municipality.DoesNotExist:
            return None

    def _barangay_code(self, municipality_code, barangay_name):
        base = self._normalize_code(barangay_name)
        candidate = f"{municipality_code}_{base}" if municipality_code else base
        if len(candidate) <= 64:
            return candidate
        suffix = base[:16] if base else "B"
        return f"{(municipality_code or 'BRGY')[:32]}_{suffix}"[:64]

    def _upsert_barangays(self, municipality, barangays):
        for name, population in barangays.items():
            normalized_name = name.strip()
            barangay = Barangay.objects.filter(
                municipality=municipality, name__iexact=normalized_name
            ).first()

            code = self._barangay_code(municipality.code, normalized_name)
            if barangay:
                updates = []
                if barangay.code != code:
                    barangay.code = code
                    updates.append("code")
                if barangay.population_total != population:
                    barangay.population_total = population
                    updates.append("population_total")
                if not barangay.is_active:
                    barangay.is_active = True
                    updates.append("is_active")
                if updates:
                    barangay.save(update_fields=updates)
            else:
                Barangay.objects.create(
                    municipality=municipality,
                    name=normalized_name,
                    code=code,
                    population_total=population,
                    is_active=True,
                )
                self.stdout.write(f"Upserted barangay: {code} - {normalized_name}")

    def load_population_dataset(self, region_code):
        dataset_path = POPULATION_DATASETS.get(region_code)
        if not dataset_path or not dataset_path.exists():
            return {}

        province_alias = {
            "CITY OF ILIGAN": "HUC_ILIGAN_CITY",
            "CITY OF CAGAYAN DE ORO": "HUC_CAGAYAN_DE_ORO",
            "CITY OF GENERAL SANTOS": "HUC_GENERAL_SANTOS_CITY",
            "DAVAO CITY (HUC)": "HUC_DAVAO_CITY",
            "CITY OF DAVAO": "HUC_DAVAO_CITY",
            "CITY OF ZAMBOANGA": "HUC_ZAMBOANGA_CITY",
            "CITY OF ISABELA": "HUC_ISABELA_CITY",
            "LANAO DEL NORTE *": "LANAO_DEL_NORTE",
            "MISAMIS ORIENTAL*": "MIS_ORIENTAL",
            "MISAMIS ORIENTAL *": "MIS_ORIENTAL",
        }

        municipality_alias = {
            "CITY OF MALAYBALAY": "Malaybalay City",
            "CITY OF VALENCIA": "Valencia City",
            "CITY OF EL SALVADOR": "El Salvador City",
            "CITY OF GINGOOG": "Gingoog City",
            "CITY OF OROQUIETA": "Oroquieta City",
            "CITY OF OZAMIZ": "Ozamiz City",
            "CITY OF TANGUB": "Tangub City",
            "ILIGAN CITY": "Iligan City",
            "CAGAYAN DE ORO CITY": "Cagayan de Oro City",
            "CITY OF PANABO": "Panabo City",
            "CITY OF TAGUM": "Tagum City",
            "CITY OF DIGOS": "Digos City",
            "CITY OF MATI": "Mati City",
            "GENERAL SANTOS CITY": "General Santos City",
            "KIDAPAWAN CITY": "Kidapawan City",
            "KORONADAL CITY": "Koronadal City",
            "TACURONG CITY": "Tacurong City",
            "MAITUM": "Maitum",
            "M'LANG": "M'lang",
            "SEN. NINOY AQUINO": "Senator Ninoy Aquino",
            "CITY OF DAPITAN": "Dapitan City",
            "CITY OF DIPOLOG": "Dipolog City",
            "PRES. MANUEL A. ROXAS": "President Manuel A. Roxas",
            "SERGIO OSMEÑA SR.": "Sergio Osmena Sr.",
            "SERGIO OSMENA SR.": "Sergio Osmena Sr.",
            "LEON T. POSTIGO 1": "Leon B. Postigo (Bacungan)",
            "LEON T. POSTIGO": "Leon B. Postigo (Bacungan)",
            "PINAN": "Pinan (New Pinan)",
            "PIÑAN": "Pinan (New Pinan)",
            "JOSE DALMAN": "Jose Dalman (Ponot)",
            "CITY OF PAGADIAN": "Pagadian City",
            "ZAMBOANGA CITY": "Zamboanga City",
            "ISABELA CITY": "Isabela City",
            "IMPASUG-ONG": "Impasugong",
        }

        def clean_number(value: str) -> int:
            return int(value.replace(",", "").replace(" ", ""))

        data = {}
        province = None
        municipality = None

        with dataset_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                if not raw_line.strip():
                    continue

                stripped = raw_line.rstrip("\n")
                parts = [part.strip() for part in stripped.split("\t") if part.strip()]
                if len(parts) < 2:
                    continue

                name, value = parts[0], parts[-1]
                try:
                    population = clean_number(value)
                except ValueError:
                    continue

                indent = len(raw_line) - len(raw_line.lstrip("\t"))

                if indent == 0:
                    province_key = province_alias.get(name.upper(), name.title())
                    province = province_key
                    data.setdefault(
                        province,
                        {"population": population, "municipalities": {}},
                    )
                    municipality = None
                elif indent == 1:
                    municipality_name = municipality_alias.get(
                        name.upper(), name.title()
                    )
                    data[province]["municipalities"][municipality_name] = {
                        "population": population,
                        "barangays": {},
                    }
                    municipality = municipality_name
                else:
                    if not municipality:
                        continue
                    data[province]["municipalities"][municipality]["barangays"][
                        name
                    ] = population

        return data
