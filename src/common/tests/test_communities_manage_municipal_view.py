from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from common.models import Municipality, Province, Region

from communities.models import MunicipalityCoverage


class ManageMunicipalStatCardsTests(TestCase):
    """Verify that the municipal management dashboard aggregates stat cards correctly."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="staffer",
            password="testpass123",
            user_type="oobc_staff",
        )
        self.client.force_login(self.user)
        self.region = Region.objects.create(code="BAR", name="BARMM Test Region")
        self.province = Province.objects.create(
            region=self.region, code="PROV-01", name="Test Province"
        )

    def _create_municipality(self, code, name):
        return Municipality.objects.create(
            province=self.province,
            code=code,
            name=name,
            municipality_type="municipality",
        )

    def _create_coverage(self, code, name, **overrides):
        defaults = {
            "total_obc_communities": 2,
            "estimated_obc_population": 800,
            "auto_sync": True,
        }
        defaults.update(overrides)
        return MunicipalityCoverage.objects.create(
            municipality=self._create_municipality(code, name),
            **defaults,
        )

    def test_stat_cards_present_expected_totals(self):
        MunicipalityCoverage.objects.create(
            municipality=self._create_municipality("MUN-001", "Alpha"),
            total_obc_communities=3,
            estimated_obc_population=1000,
            auto_sync=True,
        )
        MunicipalityCoverage.objects.create(
            municipality=self._create_municipality("MUN-002", "Bravo"),
            total_obc_communities=4,
            estimated_obc_population=2000,
            auto_sync=False,
        )
        MunicipalityCoverage.objects.create(
            municipality=self._create_municipality("MUN-003", "Charlie"),
            total_obc_communities=2,
            estimated_obc_population=1500,
            auto_sync=True,
        )

        response = self.client.get(reverse("communities:communities_manage_municipal"))

        self.assertEqual(response.status_code, 200)

        stats = response.context["stats"]
        self.assertEqual(stats["total_coverages"], 3)
        self.assertEqual(stats["total_population"], 4500)
        self.assertEqual(stats["auto_synced"], 2)
        self.assertEqual(stats["manual"], 1)

        stat_cards = response.context["stat_cards"]
        values = [card["value"] for card in stat_cards]
        self.assertEqual(values, [3, 4500, 2, 1])

    def test_table_rows_include_action_urls(self):
        coverage = self._create_coverage("MUN-010", "Zeta", auto_sync=False)

        response = self.client.get(reverse("communities:communities_manage_municipal"))
        self.assertEqual(response.status_code, 200)

        table = response.context["municipality_table"]
        self.assertEqual(len(table["headers"]), 5)
        self.assertEqual(len(table["rows"]), 1)

        row = table["rows"][0]
        expected_view_url = reverse(
            "communities:communities_view_municipal", args=[coverage.pk]
        )
        expected_edit_url = reverse(
            "communities:communities_edit_municipal", args=[coverage.pk]
        )

        self.assertEqual(row["view_url"], expected_view_url)
        self.assertEqual(row["edit_url"], expected_edit_url)
        self.assertIn("?review_delete=1", row["delete_preview_url"])
        self.assertNotIn("restore_url", row)
        self.assertIn("Zeta", row["cells"][0]["content"])

    def test_archived_rows_expose_restore_action(self):
        coverage = self._create_coverage("MUN-020", "Yankee")
        coverage.soft_delete(user=self.user)

        response = self.client.get(
            reverse("communities:communities_manage_municipal"), {"archived": "1"}
        )
        self.assertEqual(response.status_code, 200)

        table = response.context["municipality_table"]
        self.assertEqual(len(table["rows"]), 1)
        row = table["rows"][0]

        expected_view_url = (
            f"{reverse('communities:communities_view_municipal', args=[coverage.pk])}?archived=1"
        )
        expected_restore_url = reverse(
            "communities:communities_restore_municipal", args=[coverage.pk]
        )

        self.assertEqual(row["view_url"], expected_view_url)
        self.assertEqual(row["restore_url"], expected_restore_url)
        self.assertNotIn("edit_url", row)
        self.assertNotIn("delete_preview_url", row)

    def test_read_only_user_sees_view_only_actions(self):
        readonly_user = get_user_model().objects.create_user(
            username="readonly",
            password="readonlypass",
            user_type="moa_staff",
        )
        self.client.force_login(readonly_user)
        coverage = self._create_coverage("MUN-030", "Xray")

        response = self.client.get(reverse("communities:communities_manage_municipal"))
        self.assertEqual(response.status_code, 200)

        table = response.context["municipality_table"]
        row = table["rows"][0]

        self.assertIn("view_url", row)
        self.assertNotIn("edit_url", row)
        self.assertNotIn("delete_preview_url", row)
        self.assertNotIn("restore_url", row)

        expected_view_url = reverse(
            "communities:communities_view_municipal", args=[coverage.pk]
        )
        self.assertEqual(row["view_url"], expected_view_url)
