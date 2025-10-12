from django.test import TestCase
from django.urls import reverse

from common.models import Barangay, Municipality, Province, Region, User
from communities.models import MunicipalityCoverage, OBCCommunity


class ManageBarangayStatCardsTests(TestCase):
    """Ensure barangay management stat cards surface accurate aggregates."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="password123",
            user_type="admin",
            is_staff=True,
            is_superuser=True,
            is_approved=True,
        )
        self.client.force_login(self.user)

        self.region_one = Region.objects.create(code="R1", name="Region One")
        self.region_two = Region.objects.create(code="R2", name="Region Two")

        self.province_one = Province.objects.create(
            region=self.region_one,
            code="P1",
            name="Province One",
        )
        self.province_two = Province.objects.create(
            region=self.region_two,
            code="P2",
            name="Province Two",
        )

        self.municipality_a = Municipality.objects.create(
            province=self.province_one,
            code="M1",
            name="Municipality A",
            municipality_type="municipality",
        )
        self.municipality_b = Municipality.objects.create(
            province=self.province_one,
            code="M2",
            name="Municipality B",
            municipality_type="city",
        )
        self.municipality_c = Municipality.objects.create(
            province=self.province_two,
            code="M3",
            name="Municipality C",
            municipality_type="municipality",
        )

        self._create_community(self.municipality_a, "001", 120)
        self._create_community(self.municipality_a, "002", 80)
        self._create_community(self.municipality_b, "003", None)
        self._create_community(self.municipality_c, "004", 200)

    def _create_community(self, municipality, code_suffix, population):
        barangay = Barangay.objects.create(
            municipality=municipality,
            code=f"BRGY-{municipality.code}-{code_suffix}",
            name=f"Barangay {code_suffix}",
        )
        community = OBCCommunity.objects.create(
            barangay=barangay,
            estimated_obc_population=population,
        )
        # Sync municipality coverage to match production behavior
        MunicipalityCoverage.sync_for_municipality(municipality)
        return community

    def test_stat_cards_present_expected_totals(self):
        response = self.client.get(reverse("communities:communities_manage"))
        self.assertEqual(response.status_code, 200)

        stat_cards = response.context["stat_cards"]
        values = [card["value"] for card in stat_cards]

        # 4 barangay communities total and 3 municipal coverages
        # Barangay population sums to 400 while ignoring None values
        self.assertEqual(values, [4, 400, 3])
        self.assertEqual(MunicipalityCoverage.objects.count(), 3)
        self.assertEqual(stat_cards[0]["title"], "Total Barangay OBCs in the Database")
        self.assertEqual(stat_cards[1]["title"], "Total OBC Population from Barangays")
        self.assertEqual(
            stat_cards[2]["title"], "Total Municipalities OBCs in the Database"
        )
        self.assertIn("lg:grid-cols-3", response.context["stat_cards_grid_class"])

        barangay_table = response.context["barangay_table"]
        self.assertEqual(len(barangay_table["rows"]), 4)
        self.assertTrue(barangay_table["show_actions"])
        self.assertEqual(
            barangay_table["headers"],
            [
                {"label": "Community"},
                {"label": "Location"},
                {"label": "Coverage Snapshot"},
                {"label": "Ethnolinguistic & Languages"},
            ],
        )

    def test_stat_cards_respect_region_filter(self):
        response = self.client.get(
            reverse("communities:communities_manage"),
            {"region": self.region_one.id},
        )
        self.assertEqual(response.status_code, 200)

        stat_cards = response.context["stat_cards"]
        values = [card["value"] for card in stat_cards]

        # Region One retains three communities, 200 population, and two coverages
        self.assertEqual(values, [3, 200, 2])
        self.assertEqual(response.context["total_communities"], 3)
        self.assertEqual(response.context["total_population"], 200)
        self.assertEqual(len(response.context["barangay_table"]["rows"]), 3)

    def test_stat_cards_respect_province_filter(self):
        response = self.client.get(
            reverse("communities:communities_manage"),
            {"province": self.province_two.id},
        )
        self.assertEqual(response.status_code, 200)

        stat_cards = response.context["stat_cards"]
        values = [card["value"] for card in stat_cards]

        # Province Two isolates the single community in Municipality C
        self.assertEqual(values, [1, 200, 1])
        self.assertEqual(response.context["total_communities"], 1)
        self.assertEqual(response.context["total_population"], 200)
        self.assertEqual(len(response.context["barangay_table"]["rows"]), 1)
