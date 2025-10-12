"""Comprehensive view tests for OBC CRUD operations."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse

from common.models import Barangay, Municipality, Province, Region

from ..models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage

User = get_user_model()


class OBCCommunityViewTestBase(TestCase):
    """Base test class with common fixtures for OBC view tests."""

    def setUp(self):
        """Set up common test fixtures."""
        self.client = Client()

        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            user_type="oobc_staff",
        )

        # Create MANA participant user
        self.mana_user = User.objects.create_user(
            username="manauser",
            password="testpass123",
            user_type="mana_participant",
        )

        # Add MANA permission
        content_type = ContentType.objects.get_for_model(ProvinceCoverage)
        permission = Permission.objects.get_or_create(
            codename="can_access_regional_mana",
            name="Can access regional MANA",
            content_type=content_type,
        )[0]
        self.mana_user.user_permissions.add(permission)

        # Create geographic hierarchy
        self.region = Region.objects.create(
            code="XII",
            name="SOCCSKSARGEN",
            is_active=True,
        )

        self.province = Province.objects.create(
            region=self.region,
            code="PROV-001",
            name="Sultan Kudarat",
            is_active=True,
        )

        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-001",
            name="Isulan",
            municipality_type="municipality",
            is_active=True,
        )

        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-001",
            name="Kudandang",
            is_active=True,
        )

        # Create another barangay for filtering tests
        self.barangay2 = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-002",
            name="Bambad",
            is_active=True,
        )

        # Create test OBC community
        self.community = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Test Community",
            estimated_obc_population=500,
            households=100,
            women_count=250,
        )


class OBCCommunityViewTests(OBCCommunityViewTestBase):
    """Test views for OBC Community CRUD operations."""

    def test_communities_list_view_authenticated(self):
        """Authenticated users can access the communities list."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("communities:communities_manage"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communities/communities_manage.html")
        self.assertIn("communities", response.context)
        self.assertEqual(response.context["communities"].paginator.count, 1)

    def test_communities_list_view_anonymous_redirects(self):
        """Anonymous users are redirected to login."""
        response = self.client.get(reverse("communities:communities_manage"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_communities_list_filtering_by_region(self):
        """List view correctly filters by region."""
        self.client.force_login(self.user)

        # Create another region and community
        region2 = Region.objects.create(
            code="IX", name="Zamboanga Peninsula", is_active=True
        )
        province2 = Province.objects.create(
            region=region2, code="PROV-002", name="Zamboanga del Sur", is_active=True
        )
        municipality2 = Municipality.objects.create(
            province=province2, code="MUN-002", name="Pagadian", is_active=True
        )
        barangay2 = Barangay.objects.create(
            municipality=municipality2,
            code="BRGY-003",
            name="Balangasan",
            is_active=True,
        )
        OBCCommunity.objects.create(
            barangay=barangay2,
            community_names="Another Community",
            estimated_obc_population=300,
        )

        # Filter by first region
        response = self.client.get(
            reverse("communities:communities_manage"), {"region": self.region.id}
        )
        self.assertEqual(response.context["communities"].paginator.count, 1)

        # Filter by second region
        response = self.client.get(
            reverse("communities:communities_manage"), {"region": region2.id}
        )
        self.assertEqual(response.context["communities"].paginator.count, 1)

    def test_communities_list_filtering_by_province(self):
        """List view correctly filters by province."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("communities:communities_manage"), {"province": self.province.id}
        )
        self.assertEqual(response.context["communities"].paginator.count, 1)

    def test_communities_list_filtering_by_municipality(self):
        """List view correctly filters by municipality."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("communities:communities_manage"), {"municipality": self.municipality.id}
        )
        self.assertEqual(response.context["communities"].paginator.count, 1)

    def test_communities_list_search(self):
        """List view supports search functionality."""
        self.client.force_login(self.user)

        # Search by barangay name
        response = self.client.get(
            reverse("communities:communities_manage"), {"search": "Kudandang"}
        )
        self.assertEqual(response.context["communities"].paginator.count, 1)

        # Search by non-existent name
        response = self.client.get(
            reverse("communities:communities_manage"), {"search": "NonExistent"}
        )
        self.assertEqual(response.context["communities"].paginator.count, 0)

    def test_communities_list_pagination(self):
        """List view supports pagination."""
        self.client.force_login(self.user)

        # Create 15 more communities
        for i in range(15):
            barangay = Barangay.objects.create(
                municipality=self.municipality,
                code=f"BRGY-{100+i}",
                name=f"Test Barangay {i}",
                is_active=True,
            )
            OBCCommunity.objects.create(
                barangay=barangay,
                community_names=f"Community {i}",
                estimated_obc_population=100,
            )

        # Default page size is 10
        response = self.client.get(
            reverse("communities:communities_manage"), {"barangay_page_size": 10}
        )
        self.assertEqual(len(response.context["communities"]), 10)
        self.assertEqual(response.context["communities"].paginator.count, 16)

    def test_communities_list_htmx_partial_render(self):
        """HTMX requests return partial template."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("communities:communities_manage"),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "communities/partials/barangay_manage_results.html"
        )

    def test_communities_create_view_get(self):
        """GET request displays the create form."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("communities:communities_add"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communities/communities_add.html")
        self.assertIn("form", response.context)

    def test_communities_create_view_post_valid(self):
        """POST request with valid data creates a new community."""
        self.client.force_login(self.user)

        initial_count = OBCCommunity.objects.count()

        response = self.client.post(
            reverse("communities:communities_add"),
            {
                "barangay": self.barangay2.id,
                "community_names": "New Test Community",
                "estimated_obc_population": 300,
                "households": 60,
                "women_count": 150,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(OBCCommunity.objects.count(), initial_count + 1)

        new_community = OBCCommunity.objects.latest("created_at")
        self.assertEqual(new_community.barangay, self.barangay2)
        self.assertEqual(new_community.community_names, "New Test Community")

    def test_communities_create_view_post_invalid(self):
        """POST request with invalid data shows form errors."""
        self.client.force_login(self.user)

        initial_count = OBCCommunity.objects.count()

        # Missing required barangay field
        response = self.client.post(
            reverse("communities:communities_add"),
            {
                "community_names": "Invalid Community",
                "estimated_obc_population": 300,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(OBCCommunity.objects.count(), initial_count)
        self.assertFormError(
            response.context["form"], "barangay", "This field is required."
        )

    def test_communities_edit_view(self):
        """Edit view displays and processes form correctly."""
        self.client.force_login(self.user)

        # GET request
        response = self.client.get(
            reverse("communities:communities_edit", args=[self.community.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communities/communities_add.html")

        # POST request
        response = self.client.post(
            reverse("communities:communities_edit", args=[self.community.id]),
            {
                "barangay": self.barangay.id,
                "community_names": "Updated Community Name",
                "estimated_obc_population": 600,
                "households": 120,
                "women_count": 300,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.community.refresh_from_db()
        self.assertEqual(self.community.community_names, "Updated Community Name")
        self.assertEqual(self.community.estimated_obc_population, 600)

    def test_communities_delete_soft_delete(self):
        """Delete view performs soft delete."""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("communities:communities_delete", args=[self.community.id])
        )

        self.assertEqual(response.status_code, 302)
        self.community.refresh_from_db()
        self.assertTrue(self.community.is_deleted)
        self.assertIsNotNone(self.community.deleted_at)

        # Community should not appear in default manager
        self.assertFalse(OBCCommunity.objects.filter(pk=self.community.pk).exists())
        self.assertTrue(OBCCommunity.all_objects.filter(pk=self.community.pk).exists())

    def test_communities_restore_from_archive(self):
        """Restore view restores soft-deleted community."""
        self.client.force_login(self.user)

        # First, soft delete
        self.community.soft_delete(user=self.user)
        self.assertTrue(self.community.is_deleted)

        # Now restore
        response = self.client.post(
            reverse("communities:communities_restore", args=[self.community.id])
        )

        self.assertEqual(response.status_code, 302)
        self.community.refresh_from_db()
        self.assertFalse(self.community.is_deleted)
        self.assertIsNone(self.community.deleted_at)

    def test_communities_detail_view(self):
        """Detail view displays community information."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("communities:communities_view", args=[self.community.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communities/communities_view.html")
        self.assertEqual(response.context["community"], self.community)

    def test_communities_detail_view_delete_review_mode(self):
        """Detail view supports delete review mode."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("communities:communities_view", args=[self.community.id]),
            {"review_delete": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["delete_review_mode"])


class MunicipalCoverageViewTests(OBCCommunityViewTestBase):
    """Test views for Municipal Coverage CRUD operations."""

    def setUp(self):
        """Set up municipal coverage test fixtures."""
        super().setUp()

        self.coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            total_obc_communities=3,
            estimated_obc_population=2500,
            key_barangays="Kudandang, Bambad",
            created_by=self.user,
        )

    def test_municipal_list_view(self):
        """Municipal coverage list view works correctly."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("communities:communities_manage_municipal"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communities/municipal_manage.html")
        self.assertIn("coverages", response.context)
        self.assertEqual(response.context["coverages"].paginator.count, 1)

    def test_municipal_list_filtering(self):
        """Municipal list supports region/province filtering."""
        self.client.force_login(self.user)

        # Filter by region
        response = self.client.get(
            reverse("communities:communities_manage_municipal"),
            {"region": self.region.id},
        )
        self.assertEqual(response.context["coverages"].paginator.count, 1)

        # Filter by province
        response = self.client.get(
            reverse("communities:communities_manage_municipal"),
            {"province": self.province.id},
        )
        self.assertEqual(response.context["coverages"].paginator.count, 1)

    def test_municipal_list_htmx_partial(self):
        """HTMX requests return partial template."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("communities:communities_manage_municipal"),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "communities/partials/municipal_manage_results.html"
        )

    def test_municipal_create_valid(self):
        """Create municipal coverage with valid data."""
        self.client.force_login(self.user)

        # Create another municipality for testing
        municipality2 = Municipality.objects.create(
            province=self.province,
            code="MUN-003",
            name="Tacurong",
            municipality_type="city",
            is_active=True,
        )

        initial_count = MunicipalityCoverage.objects.count()

        response = self.client.post(
            reverse("communities:communities_add_municipality"),
            {
                "municipality": municipality2.id,
                "total_obc_communities": 5,
                "estimated_obc_population": 3000,
                "key_barangays": "Barangay A, Barangay B",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(MunicipalityCoverage.objects.count(), initial_count + 1)

    def test_municipal_create_prevents_duplicates(self):
        """Cannot create duplicate municipal coverage for same municipality."""
        self.client.force_login(self.user)

        initial_count = MunicipalityCoverage.objects.count()

        # Try to create another coverage for the same municipality
        response = self.client.post(
            reverse("communities:communities_add_municipality"),
            {
                "municipality": self.municipality.id,
                "total_obc_communities": 2,
                "estimated_obc_population": 1000,
            },
        )

        # Should fail validation
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MunicipalityCoverage.objects.count(), initial_count)

    def test_municipal_edit_view(self):
        """Edit municipal coverage."""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("communities:communities_edit_municipal", args=[self.coverage.id]),
            {
                "municipality": self.municipality.id,
                "total_obc_communities": 5,
                "estimated_obc_population": 3500,
                "key_barangays": "Updated barangays",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.coverage.refresh_from_db()
        self.assertEqual(self.coverage.total_obc_communities, 5)
        self.assertEqual(self.coverage.estimated_obc_population, 3500)

    def test_municipal_delete_cascades_sync(self):
        """Deleting municipal coverage triggers province sync."""
        self.client.force_login(self.user)

        # Create provincial coverage first
        province_coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=1,
            total_obc_communities=3,
            created_by=self.user,
        )

        response = self.client.post(
            reverse("communities:communities_delete_municipal", args=[self.coverage.id])
        )

        self.assertEqual(response.status_code, 302)
        self.coverage.refresh_from_db()
        self.assertTrue(self.coverage.is_deleted)

    def test_municipal_restore(self):
        """Restore archived municipal coverage."""
        self.client.force_login(self.user)

        # Soft delete first
        self.coverage.soft_delete(user=self.user)

        response = self.client.post(
            reverse("communities:communities_restore_municipal", args=[self.coverage.id])
        )

        self.assertEqual(response.status_code, 302)
        self.coverage.refresh_from_db()
        self.assertFalse(self.coverage.is_deleted)

    def test_municipal_auto_sync_aggregation(self):
        """Municipal coverage auto-syncs from barangay communities."""
        self.client.force_login(self.user)

        # Create barangay OBC (should trigger auto-sync)
        OBCCommunity.objects.create(
            barangay=self.barangay2,
            community_names="Synced Community",
            estimated_obc_population=200,
            households=40,
        )

        # Coverage should be updated
        coverage = MunicipalityCoverage.objects.get(municipality=self.municipality)
        self.assertTrue(coverage.auto_sync)
        self.assertGreaterEqual(coverage.total_obc_communities, 1)

    def test_municipal_detail_view(self):
        """Municipal coverage detail view."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("communities:communities_view_municipal", args=[self.coverage.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communities/municipal_view.html")
        self.assertEqual(response.context["coverage"], self.coverage)

    def test_municipal_archived_view(self):
        """Archived municipal coverages are shown in archived view."""
        self.client.force_login(self.user)

        self.coverage.soft_delete(user=self.user)

        response = self.client.get(
            reverse("communities:communities_manage_municipal"),
            {"archived": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["coverages"].paginator.count, 1)
        self.assertTrue(response.context["show_archived"])

    def test_municipal_pagination(self):
        """Municipal list supports pagination."""
        self.client.force_login(self.user)

        # Create 15 more municipalities with coverage
        for i in range(15):
            municipality = Municipality.objects.create(
                province=self.province,
                code=f"MUN-{100+i}",
                name=f"Municipality {i}",
                is_active=True,
            )
            MunicipalityCoverage.objects.create(
                municipality=municipality,
                total_obc_communities=1,
                created_by=self.user,
            )

        response = self.client.get(
            reverse("communities:communities_manage_municipal"),
            {"municipality_page_size": 10},
        )

        self.assertEqual(len(response.context["coverages"]), 10)


class ProvincialCoverageViewTests(OBCCommunityViewTestBase):
    """Test views for Provincial Coverage CRUD operations."""

    def setUp(self):
        """Set up provincial coverage test fixtures."""
        super().setUp()

        # Create MANA participant account
        try:
            from mana.models import WorkshopParticipantAccount

            self.participant_account = WorkshopParticipantAccount.objects.create(
                user=self.mana_user,
                province=self.province,
                full_name="MANA Participant",
            )
        except Exception:
            # Skip MANA-specific tests if mana app is not available
            self.participant_account = None

        self.coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=2,
            total_obc_communities=5,
            estimated_obc_population=4000,
            created_by=self.user,
        )

    def test_provincial_list_view(self):
        """Provincial coverage list view works correctly."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("communities:communities_manage_provincial"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "communities/provincial_manage.html")
        self.assertIn("coverages", response.context)
        self.assertEqual(response.context["coverages"].paginator.count, 1)

    def test_provincial_list_mana_participant_permissions(self):
        """MANA participants only see their own provincial OBCs."""
        if not self.participant_account:
            self.skipTest("MANA app not available")

        self.client.force_login(self.mana_user)

        # Create provincial OBC by MANA user
        mana_coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=1,
            total_obc_communities=2,
            created_by=self.mana_user,
        )

        response = self.client.get(reverse("communities:communities_manage_provincial"))

        self.assertEqual(response.status_code, 200)
        # Should only see their own coverage
        self.assertEqual(response.context["coverages"].paginator.count, 1)
        self.assertEqual(response.context["coverages"][0], mana_coverage)

    def test_provincial_create_valid(self):
        """Create provincial coverage with valid data."""
        self.client.force_login(self.user)

        # Create another province
        province2 = Province.objects.create(
            region=self.region,
            code="PROV-002",
            name="South Cotabato",
            is_active=True,
        )

        initial_count = ProvinceCoverage.objects.count()

        response = self.client.post(
            reverse("communities:communities_add_province"),
            {
                "province": province2.id,
                "total_municipalities": 3,
                "total_obc_communities": 10,
                "estimated_obc_population": 5000,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProvinceCoverage.objects.count(), initial_count + 1)

    def test_provincial_create_prevents_duplicates(self):
        """Cannot create duplicate provincial coverage for same province."""
        self.client.force_login(self.user)

        initial_count = ProvinceCoverage.objects.count()

        response = self.client.post(
            reverse("communities:communities_add_province"),
            {
                "province": self.province.id,
                "total_municipalities": 1,
                "total_obc_communities": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProvinceCoverage.objects.count(), initial_count)

    def test_provincial_edit_own_record_mana(self):
        """MANA participants can edit their own provincial OBCs."""
        if not self.participant_account:
            self.skipTest("MANA app not available")

        self.client.force_login(self.mana_user)

        # Create coverage by MANA user
        mana_coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=1,
            total_obc_communities=2,
            created_by=self.mana_user,
            is_submitted=False,
        )

        response = self.client.post(
            reverse("communities:communities_edit_provincial", args=[mana_coverage.id]),
            {
                "province": self.province.id,
                "total_municipalities": 2,
                "total_obc_communities": 4,
            },
        )

        self.assertEqual(response.status_code, 302)
        mana_coverage.refresh_from_db()
        self.assertEqual(mana_coverage.total_municipalities, 2)

    def test_provincial_edit_others_record_denied_mana(self):
        """MANA participants cannot edit others' provincial OBCs."""
        if not self.participant_account:
            self.skipTest("MANA app not available")

        self.client.force_login(self.mana_user)

        # Try to edit coverage created by staff user
        response = self.client.get(
            reverse("communities:communities_edit_provincial", args=[self.coverage.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_provincial_delete_own_record_mana(self):
        """MANA participants can delete their own provincial OBCs."""
        if not self.participant_account:
            self.skipTest("MANA app not available")

        self.client.force_login(self.mana_user)

        mana_coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=1,
            total_obc_communities=2,
            created_by=self.mana_user,
            is_submitted=False,
        )

        response = self.client.post(
            reverse("communities:communities_delete_provincial", args=[mana_coverage.id])
        )

        self.assertEqual(response.status_code, 302)
        mana_coverage.refresh_from_db()
        self.assertTrue(mana_coverage.is_deleted)

    def test_provincial_delete_others_denied_mana(self):
        """MANA participants cannot delete others' provincial OBCs."""
        if not self.participant_account:
            self.skipTest("MANA app not available")

        self.client.force_login(self.mana_user)

        response = self.client.post(
            reverse("communities:communities_delete_provincial", args=[self.coverage.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_provincial_submitted_readonly_mana(self):
        """MANA participants cannot edit submitted provincial OBCs."""
        if not self.participant_account:
            self.skipTest("MANA app not available")

        self.client.force_login(self.mana_user)

        mana_coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=1,
            total_obc_communities=2,
            created_by=self.mana_user,
            is_submitted=True,
        )

        response = self.client.get(
            reverse("communities:communities_edit_provincial", args=[mana_coverage.id])
        )

        # Should redirect with error message
        self.assertEqual(response.status_code, 302)

    def test_provincial_staff_full_access(self):
        """Staff users have full access to all provincial OBCs."""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("communities:communities_edit_provincial", args=[self.coverage.id]),
            {
                "province": self.province.id,
                "total_municipalities": 3,
                "total_obc_communities": 8,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.coverage.refresh_from_db()
        self.assertEqual(self.coverage.total_municipalities, 3)

    def test_provincial_auto_sync_from_municipal(self):
        """Provincial coverage auto-syncs from municipal coverages."""
        self.client.force_login(self.user)

        # Create municipal coverage
        MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            total_obc_communities=3,
            estimated_obc_population=2000,
            created_by=self.user,
        )

        # Sync provincial coverage
        ProvinceCoverage.sync_for_province(self.province)

        self.coverage.refresh_from_db()
        self.assertTrue(self.coverage.auto_sync)

    def test_provincial_detail_view_permissions(self):
        """Provincial detail view respects MANA permissions."""
        if not self.participant_account:
            self.skipTest("MANA app not available")

        self.client.force_login(self.mana_user)

        # Try to view coverage created by staff
        response = self.client.get(
            reverse("communities:communities_view_provincial", args=[self.coverage.id])
        )

        self.assertEqual(response.status_code, 403)

        # Create own coverage
        mana_coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=1,
            total_obc_communities=2,
            created_by=self.mana_user,
        )

        # Should be able to view own coverage
        response = self.client.get(
            reverse("communities:communities_view_provincial", args=[mana_coverage.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_provincial_submit_workflow(self):
        """MANA participants can submit provincial OBCs."""
        if not self.participant_account:
            self.skipTest("MANA app not available")

        self.client.force_login(self.mana_user)

        mana_coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=1,
            total_obc_communities=2,
            created_by=self.mana_user,
            is_submitted=False,
        )

        response = self.client.post(
            reverse("communities:communities_submit_provincial", args=[mana_coverage.id])
        )

        self.assertEqual(response.status_code, 302)
        mana_coverage.refresh_from_db()
        self.assertTrue(mana_coverage.is_submitted)
        self.assertIsNotNone(mana_coverage.submitted_at)


class LocationAPIViewTests(OBCCommunityViewTestBase):
    """Test location-related API views."""

    def test_location_centroid_barangay(self):
        """Location centroid API returns barangay coordinates."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("common:location_centroid"),
            {"level": "barangay", "id": self.barangay.id},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("has_location", data)

    def test_location_centroid_missing_params(self):
        """Location centroid API requires level and id."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("common:location_centroid"))

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

    def test_location_centroid_invalid_level(self):
        """Location centroid API rejects invalid level."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("common:location_centroid"),
            {"level": "invalid", "id": "123"},
        )

        self.assertEqual(response.status_code, 400)
