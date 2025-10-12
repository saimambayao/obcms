"""Integration tests for multi-step community deletion and restoration flows."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from common.models import Barangay, Municipality, Province, Region
from communities.models import MunicipalityCoverage, OBCCommunity


class CommunityDeleteFlowTest(TestCase):
    """Ensure delete and restore actions perform soft deletes with redirects."""

    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="admin",
            password="pass12345",
            is_superuser=True,
            is_staff=True,
        )
        self.client.force_login(self.user)

        self.region = Region.objects.create(code="R99", name="Test Region")
        self.province = Province.objects.create(
            region=self.region, code="P99", name="Test Province"
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="M99",
            name="Test Municipality",
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="B99",
            name="Test Barangay",
        )

    def _create_barangay_obc(self):
        return OBCCommunity.objects.create(
            barangay=self.barangay,
            name="Sample Community",
        )

    def _create_municipal_coverage(self):
        return MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            total_obc_communities=1,
        )

    def test_barangay_delete_archives_record(self):
        community = self._create_barangay_obc()

        response = self.client.post(
            reverse("communities:communities_delete", args=[community.pk])
        )

        self.assertRedirects(
            response,
            f"{reverse('communities:communities_manage')}?archived=1",
            fetch_redirect_response=False,
        )
        community.refresh_from_db()
        self.assertTrue(community.is_deleted)

    def test_barangay_restore_reactivates_record(self):
        community = self._create_barangay_obc()
        community.soft_delete()

        response = self.client.post(
            reverse("communities:communities_restore", args=[community.pk])
        )

        self.assertRedirects(
            response,
            f"{reverse('communities:communities_manage')}?archived=1",
            fetch_redirect_response=False,
        )
        community.refresh_from_db()
        self.assertFalse(community.is_deleted)

    def test_municipal_delete_archives_record(self):
        coverage = self._create_municipal_coverage()

        response = self.client.post(
            reverse("communities:communities_delete_municipal", args=[coverage.pk])
        )

        self.assertRedirects(
            response,
            f"{reverse('communities:communities_manage_municipal')}?archived=1",
            fetch_redirect_response=False,
        )
        coverage.refresh_from_db()
        self.assertTrue(coverage.is_deleted)

    def test_municipal_restore_reactivates_record(self):
        coverage = self._create_municipal_coverage()
        coverage.soft_delete()

        response = self.client.post(
            reverse("communities:communities_restore_municipal", args=[coverage.pk])
        )

        self.assertRedirects(
            response,
            f"{reverse('communities:communities_manage_municipal')}?archived=1",
            fetch_redirect_response=False,
        )
        coverage.refresh_from_db()
        self.assertFalse(coverage.is_deleted)
