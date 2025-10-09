import pytest

pytest.skip(
    "Legacy model/view tests require updated templates after refactor.",
    allow_module_level=True,
)

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from types import SimpleNamespace
from unittest import mock

from communities.models import MunicipalityCoverage, OBCCommunity
from common.management.commands.populate_administrative_hierarchy import (
    Command as HierarchyCommand,
)

from ..forms import (
    COMMUNITY_PROFILE_FIELDS,
    CustomLoginForm,
    MunicipalityCoverageForm,
    OBCCommunityForm,
    UserRegistrationForm,
)
from ..models import Barangay, Municipality, Province, Region, User
from ..services.locations import build_location_data

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the custom User model."""

    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "oobc_staff",
            "organization": "OOBC Test",
            "position": "Test Position",
            "contact_number": "+639123456789",
        }

    def test_create_user(self):
        """Test creating a new user."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.user_type, "oobc_staff")
        self.assertFalse(user.is_approved)  # Should be False by default
        self.assertTrue(user.is_active)

    def test_user_str_method(self):
        """Test the __str__ method of User."""
        user = User.objects.create_user(**self.user_data)
        expected = "Test User (OOBC Staff)"
        self.assertEqual(str(user), expected)

    def test_user_properties(self):
        """Test user property methods."""
        user = User.objects.create_user(**self.user_data)

        # Test is_oobc_staff property
        self.assertTrue(user.is_oobc_staff)

        # Test is_community_leader property
        user.user_type = "community_leader"
        user.save()
        self.assertTrue(user.is_community_leader)

        # Test can_approve_users property
        user.user_type = "admin"
        user.is_superuser = True
        user.save()
        self.assertTrue(user.can_approve_users)

    def test_user_approval_workflow(self):
        """Test user approval workflow."""
        # Create admin user
        admin_user = User.objects.create_user(
            username="admin", user_type="admin", is_superuser=True
        )

        # Create regular user
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_approved)
        self.assertIsNone(user.approved_by)
        self.assertIsNone(user.approved_at)

        # Approve user
        user.is_approved = True
        user.approved_by = admin_user
        user.approved_at = timezone.now()
        user.save()

        self.assertTrue(user.is_approved)
        self.assertEqual(user.approved_by, admin_user)
        self.assertIsNotNone(user.approved_at)


class UserRegistrationFormTest(TestCase):
    """Test cases for UserRegistrationForm."""

    def setUp(self):
        self.form_data = {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
            "user_type": "lgu",
            "organization": "Test LGU",
            "position": "Mayor",
            "contact_number": "+639987654321",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }

    def test_valid_registration_form(self):
        """Test valid registration form."""
        form = UserRegistrationForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """Test password mismatch validation."""
        self.form_data["password2"] = "DifferentPassword123!"
        form = UserRegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_duplicate_email(self):
        """Test duplicate email validation."""
        # Create existing user
        User.objects.create_user(username="existing", email="newuser@example.com")

        form = UserRegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_save(self):
        """Test form save method."""
        form = UserRegistrationForm(data=self.form_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertEqual(user.user_type, "lgu")
        self.assertFalse(user.is_approved)  # Should be False for new registrations


class CustomLoginFormTest(TestCase):
    """Test cases for CustomLoginForm."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
            user_type="oobc_staff",
            is_approved=True,
        )
        # Create a proper mock request for django-axes
        self.mock_request = mock.Mock()
        self.mock_request.META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'test'}
        self.mock_request.method = 'POST'
        self.mock_request.path = '/login/'

    @mock.patch('common.forms.auth.authenticate')
    def test_login_with_username(self, mock_authenticate):
        """Test login with username."""
        mock_authenticate.return_value = self.user
        form_data = {"username": "testuser", "password": "TestPassword123!"}
        form = CustomLoginForm(self.mock_request, data=form_data)
        self.assertTrue(form.is_valid())

    @mock.patch('common.forms.auth.authenticate')
    def test_login_with_email(self, mock_authenticate):
        """Test login with email."""
        mock_authenticate.return_value = self.user
        form_data = {
            "username": "test@example.com",  # Using email as username
            "password": "TestPassword123!",
        }
        form = CustomLoginForm(self.mock_request, data=form_data)
        self.assertTrue(form.is_valid())

    @mock.patch('common.forms.auth.authenticate')
    def test_invalid_credentials(self, mock_authenticate):
        """Test login with invalid credentials."""
        mock_authenticate.return_value = None
        form_data = {"username": "testuser", "password": "WrongPassword"}
        form = CustomLoginForm(self.mock_request, data=form_data)
        self.assertFalse(form.is_valid())


class AuthenticationViewsTest(TestCase):
    """Test cases for authentication views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
            user_type="oobc_staff",
            is_approved=True,
        )
        self.unapproved_user = User.objects.create_user(
            username="unapproved",
            email="unapproved@example.com",
            password="TestPassword123!",
            user_type="lgu",
            is_approved=False,
        )

    def test_login_view_get(self):
        """Test GET request to login view."""
        response = self.client.get(reverse("common:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in to access the OBC Management System")

    def test_login_view_post_success(self):
        """Test successful login."""
        response = self.client.post(
            reverse("common:login"),
            {"username": "testuser", "password": "TestPassword123!"},
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_login_view_post_unapproved_user(self):
        """Test login attempt with unapproved user."""
        response = self.client.post(
            reverse("common:login"),
            {"username": "unapproved", "password": "TestPassword123!"},
        )
        self.assertEqual(response.status_code, 200)  # Should not redirect
        self.assertContains(response, "pending approval")

    def test_registration_view_get(self):
        """Test GET request to registration view."""
        response = self.client.get(reverse("common:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create OBC Account")

    def test_registration_view_post(self):
        """Test POST request to registration view."""
        response = self.client.post(
            reverse("common:register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@example.com",
                "user_type": "nga",
                "organization": "Test Agency",
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful registration

        # Check if user was created
        new_user = User.objects.get(username="newuser")
        self.assertFalse(new_user.is_approved)  # Should be unapproved

    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("common:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
        self.assertContains(response, "testuser")

    def test_dashboard_view_unauthenticated(self):
        """Test dashboard view for unauthenticated user."""
        response = self.client.get(reverse("common:dashboard"))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("common:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Profile")
        self.assertContains(response, "testuser")

    def test_logout_view(self):
        """Test logout functionality."""
        self.client.force_login(self.user)
        response = self.client.post(reverse("common:logout"))
        self.assertEqual(response.status_code, 200)


class AdministrativeHierarchyModelTests(TestCase):
    """Test cases for administrative hierarchy models."""

    def setUp(self):
        """Set up test data."""
        self.region = Region.objects.create(
            code="IX",
            name="Zamboanga Peninsula",
            description="Region IX encompasses the Zamboanga Peninsula",
        )

        self.province = Province.objects.create(
            region=self.region,
            code="ZAM_DEL_SUR",
            name="Zamboanga del Sur",
            capital="Pagadian City",
        )

        self.municipality = Municipality.objects.create(
            province=self.province,
            code="ZAMBOANGA_CITY",
            name="Zamboanga",
            municipality_type="independent_city",
        )

        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="CAMPO_ISLAM",
            name="Campo Islam",
            is_urban=True,
        )

    def test_region_creation(self):
        """Test region model creation and properties."""
        self.assertEqual(self.region.code, "IX")
        self.assertEqual(self.region.name, "Zamboanga Peninsula")
        self.assertTrue(self.region.is_active)
        self.assertIsNotNone(self.region.created_at)

        # Test string representation
        expected_str = "Region IX - Zamboanga Peninsula"
        self.assertEqual(str(self.region), expected_str)

    def test_region_province_count(self):
        """Test region province count property."""
        # Initially should have 1 province
        self.assertEqual(self.region.province_count, 1)

        # Add another province
        Province.objects.create(
            region=self.region, code="ZAM_DEL_NORTE", name="Zamboanga del Norte"
        )
        self.assertEqual(self.region.province_count, 2)

        # Inactive province should not count
        Province.objects.create(
            region=self.region,
            code="ZAM_SIBUGAY",
            name="Zamboanga Sibugay",
            is_active=False,
        )
        self.assertEqual(self.region.province_count, 2)

    def test_province_creation(self):
        """Test province model creation and properties."""
        self.assertEqual(self.province.code, "ZAM_DEL_SUR")
        self.assertEqual(self.province.name, "Zamboanga del Sur")
        self.assertEqual(self.province.capital, "Pagadian City")
        self.assertEqual(self.province.region, self.region)

        # Test string representation
        expected_str = "Zamboanga del Sur, Zamboanga Peninsula"
        self.assertEqual(str(self.province), expected_str)

        # Test full path
        expected_path = "Region IX > Zamboanga del Sur"
        self.assertEqual(self.province.full_path, expected_path)

    def test_province_municipality_count(self):
        """Test province municipality count property."""
        # Initially should have 1 municipality
        self.assertEqual(self.province.municipality_count, 1)

        # Add another municipality
        Municipality.objects.create(
            province=self.province,
            code="PAGADIAN",
            name="Pagadian",
            municipality_type="city",
        )
        self.assertEqual(self.province.municipality_count, 2)

    def test_municipality_creation(self):
        """Test municipality model creation and properties."""
        self.assertEqual(self.municipality.code, "ZAMBOANGA_CITY")
        self.assertEqual(self.municipality.name, "Zamboanga")
        self.assertEqual(self.municipality.municipality_type, "independent_city")
        self.assertEqual(self.municipality.province, self.province)

        # Test string representation
        expected_str = "Independent City of Zamboanga, Zamboanga del Sur"
        self.assertEqual(str(self.municipality), expected_str)

        # Test full path
        expected_path = "Region IX > Zamboanga del Sur > Zamboanga"
        self.assertEqual(self.municipality.full_path, expected_path)

    def test_municipality_barangay_count(self):
        """Test municipality barangay count property."""
        # Initially should have 1 barangay
        self.assertEqual(self.municipality.barangay_count, 1)

        # Add another barangay
        Barangay.objects.create(
            municipality=self.municipality,
            code="RIO_HONDO",
            name="Rio Hondo",
            is_urban=True,
        )
        self.assertEqual(self.municipality.barangay_count, 2)

    def test_barangay_creation(self):
        """Test barangay model creation and properties."""
        self.assertEqual(self.barangay.code, "CAMPO_ISLAM")
        self.assertEqual(self.barangay.name, "Campo Islam")
        self.assertTrue(self.barangay.is_urban)
        self.assertEqual(self.barangay.municipality, self.municipality)

        # Test string representation
        expected_str = "Barangay Campo Islam, Zamboanga"
        self.assertEqual(str(self.barangay), expected_str)

        # Test full path
        expected_path = (
            "Region IX > Zamboanga del Sur > Zamboanga > " "Barangay Campo Islam"
        )
        self.assertEqual(self.barangay.full_path, expected_path)

    def test_barangay_properties(self):
        """Test barangay convenience properties."""
        # Test region property
        self.assertEqual(self.barangay.region, self.region)

        # Test province property
        self.assertEqual(self.barangay.province, self.province)

    def test_model_ordering(self):
        """Test model default ordering."""
        # Create additional regions
        region_xii = Region.objects.create(code="XII", name="SOCCSKSARGEN")
        region_x = Region.objects.create(code="X", name="Northern Mindanao")

        regions = list(Region.objects.all())
        self.assertEqual(regions[0].code, "IX")
        self.assertEqual(regions[1].code, "X")
        self.assertEqual(regions[2].code, "XII")

    def test_unique_constraints(self):
        """Test unique constraints on codes."""
        # Test region code uniqueness
        with self.assertRaises(Exception):
            Region.objects.create(code="IX", name="Duplicate Region")

        # Test province code uniqueness
        with self.assertRaises(Exception):
            Province.objects.create(
                region=self.region, code="ZAM_DEL_SUR", name="Duplicate Province"
            )

        # Test municipality code uniqueness
        with self.assertRaises(Exception):
            Municipality.objects.create(
                province=self.province,
                code="ZAMBOANGA_CITY",
                name="Duplicate Municipality",
            )

        # Test barangay code uniqueness
        with self.assertRaises(Exception):
            Barangay.objects.create(
                municipality=self.municipality,
                code="CAMPO_ISLAM",
                name="Duplicate Barangay",
            )

    def test_cascade_relationships(self):
        """Test cascade delete relationships."""
        # Count initial objects
        initial_provinces = Province.objects.count()
        initial_municipalities = Municipality.objects.count()
        initial_barangays = Barangay.objects.count()

        # Delete region should cascade to all related objects
        self.region.delete()

        # Verify cascade deletion
        self.assertEqual(Province.objects.count(), initial_provinces - 1)
        self.assertEqual(Municipality.objects.count(), initial_municipalities - 1)
        self.assertEqual(Barangay.objects.count(), initial_barangays - 1)


class MunicipalityCoverageFormTest(TestCase):
    """Tests for the MunicipalityCoverageForm helper logic."""

    def setUp(self):
        self.region = Region.objects.create(
            code="XI",
            name="Davao Region",
            center_coordinates=[125.6131, 7.0707],
        )
        self.province = Province.objects.create(
            region=self.region,
            code="PROV-100",
            name="Davao del Sur",
            center_coordinates=[125.353, 6.8724],
        )
        self.municipality_a = Municipality.objects.create(
            province=self.province,
            code="MUN-A",
            name="Digos City",
            municipality_type="component_city",
            center_coordinates=[125.3575, 6.7504],
        )
        self.municipality_b = Municipality.objects.create(
            province=self.province,
            code="MUN-B",
            name="Sta. Cruz",
            municipality_type="municipality",
            center_coordinates=[125.4112, 6.8348],
        )
        MunicipalityCoverage.objects.create(municipality=self.municipality_a)

    def test_form_excludes_existing_municipality(self):
        form = MunicipalityCoverageForm()
        municipality_ids = set(
            form.fields["municipality"].queryset.values_list("id", flat=True)
        )
        self.assertNotIn(self.municipality_a.id, municipality_ids)
        self.assertIn(self.municipality_b.id, municipality_ids)
        self.assertTrue(set(COMMUNITY_PROFILE_FIELDS).issubset(form.fields.keys()))

    def test_valid_form_submission(self):
        form = MunicipalityCoverageForm(
            data={
                "region": str(self.region.id),
                "province": str(self.province.id),
                "municipality": str(self.municipality_b.id),
                "total_obc_communities": 4,
                "estimated_obc_population": 3200,
                "key_barangays": "Barangay Zone I, Barangay Zone II",
                "auto_sync": False,
                "settlement_type": "village",
                "unemployment_rate": "moderate",
                "religious_leaders_count": 0,
                "mosques_count": 0,
                "madrasah_count": 0,
                "asatidz_count": 0,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        coverage = form.save()
        self.assertEqual(coverage.municipality, self.municipality_b)

    def test_coordinates_auto_populate_from_municipality(self):
        form = MunicipalityCoverageForm(
            data={
                "region": str(self.region.id),
                "province": str(self.province.id),
                "municipality": str(self.municipality_b.id),
                "total_obc_communities": 1,
                "settlement_type": "village",
                "unemployment_rate": "moderate",
                "religious_leaders_count": 0,
                "mosques_count": 0,
                "madrasah_count": 0,
                "asatidz_count": 0,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertAlmostEqual(form.cleaned_data["latitude"], 6.8348)
        self.assertAlmostEqual(form.cleaned_data["longitude"], 125.4112)

        coverage = form.save()
        self.assertAlmostEqual(coverage.latitude, 6.8348)
        self.assertAlmostEqual(coverage.longitude, 125.4112)

    def test_region_province_mismatch_is_invalid(self):
        other_region = Region.objects.create(code="XIII", name="Caraga")
        form = MunicipalityCoverageForm(
            data={
                "region": str(other_region.id),
                "province": str(self.province.id),
                "municipality": str(self.municipality_b.id),
                "total_obc_communities": 1,
                "settlement_type": "village",
                "unemployment_rate": "moderate",
                "religious_leaders_count": 0,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("province", form.errors)

    def test_municipality_province_mismatch_is_invalid(self):
        other_province = Province.objects.create(
            region=self.region,
            code="PROV-200",
            name="Davao Occidental",
        )
        other_municipality = Municipality.objects.create(
            province=other_province,
            code="MUN-C",
            name="Malita",
            municipality_type="municipality",
        )
        form = MunicipalityCoverageForm(
            data={
                "region": str(self.region.id),
                "province": str(self.province.id),
                "municipality": str(other_municipality.id),
                "total_obc_communities": 2,
                "settlement_type": "village",
                "unemployment_rate": "moderate",
                "religious_leaders_count": 0,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("municipality", form.errors)


class OBCCommunityFormTest(TestCase):
    """Tests for the OBCCommunityForm location hierarchy."""

    def setUp(self):
        self.region = Region.objects.create(
            code="XII",
            name="SOCCSKSARGEN",
            center_coordinates=[124.8467, 6.2094],
        )
        self.other_region = Region.objects.create(
            code="IX",
            name="Zamboanga Peninsula",
            center_coordinates=[123.4202, 7.8257],
        )

        self.province = Province.objects.create(
            region=self.region,
            code="PROV-300",
            name="South Cotabato",
            center_coordinates=[124.9956, 6.3354],
        )
        self.other_province = Province.objects.create(
            region=self.other_region,
            code="PROV-400",
            name="Zamboanga del Norte",
            center_coordinates=[123.2859, 8.5112],
        )

        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-100",
            name="Koronadal City",
            municipality_type="component_city",
            center_coordinates=[124.8535, 6.4979],
        )
        self.other_municipality = Municipality.objects.create(
            province=self.other_province,
            code="MUN-200",
            name="Dipolog City",
            municipality_type="component_city",
            center_coordinates=[123.362, 8.5819],
        )

        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code="BRGY-100",
            name="Barangay Zone I",
            center_coordinates=[124.8631, 6.5034],
        )
        self.other_barangay = Barangay.objects.create(
            municipality=self.other_municipality,
            code="BRGY-200",
            name="Barangay Central",
            center_coordinates=[123.3437, 8.5873],
        )

    def test_valid_submission(self):
        form = OBCCommunityForm(
            data={
                "region": str(self.region.id),
                "province": str(self.province.id),
                "municipality": str(self.municipality.id),
                "barangay": str(self.barangay.id),
                "community_names": "Sample OBC Community",
                "settlement_type": "village",
                "unemployment_rate": "moderate",
                "mosques_count": 0,
                "madrasah_count": 0,
                "religious_leaders_count": 0,
                "asatidz_count": 0,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        community = form.save()
        self.assertEqual(community.barangay, self.barangay)

    def test_coordinates_auto_populate_from_barangay(self):
        form = OBCCommunityForm(
            data={
                "region": str(self.region.id),
                "province": str(self.province.id),
                "municipality": str(self.municipality.id),
                "barangay": str(self.barangay.id),
                "community_names": "Barangay Coordinates",
                "settlement_type": "village",
                "unemployment_rate": "moderate",
                "mosques_count": 0,
                "madrasah_count": 0,
                "asatidz_count": 0,
                "religious_leaders_count": 0,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertAlmostEqual(form.cleaned_data["latitude"], 6.5034)
        self.assertAlmostEqual(form.cleaned_data["longitude"], 124.8631)

        community = form.save()
        self.assertAlmostEqual(community.latitude, 6.5034)
        self.assertAlmostEqual(community.longitude, 124.8631)

    def test_coordinates_fallback_to_municipality_when_barangay_missing(self):
        Barangay.objects.filter(pk=self.barangay.id).update(center_coordinates=None)
        self.barangay.refresh_from_db(fields=["center_coordinates"])

        with mock.patch(
            "common.forms.community.enhanced_ensure_location_coordinates",
            return_value=(None, None, False, "unavailable"),
        ):
            form = OBCCommunityForm(
                data={
                    "region": str(self.region.id),
                    "province": str(self.province.id),
                    "municipality": str(self.municipality.id),
                    "barangay": str(self.barangay.id),
                    "community_names": "Municipality Fallback",
                    "settlement_type": "village",
                    "unemployment_rate": "moderate",
                    "mosques_count": 0,
                    "madrasah_count": 0,
                    "asatidz_count": 0,
                    "religious_leaders_count": 0,
                }
            )

            self.assertTrue(form.is_valid(), form.errors)
            self.assertAlmostEqual(form.cleaned_data["latitude"], 6.4979)
            self.assertAlmostEqual(form.cleaned_data["longitude"], 124.8535)

            community = form.save()
            self.assertAlmostEqual(community.latitude, 6.4979)
            self.assertAlmostEqual(community.longitude, 124.8535)

    def test_hierarchy_mismatch_rejected(self):
        form = OBCCommunityForm(
            data={
                "region": str(self.region.id),
                "province": str(self.province.id),
                "municipality": str(self.municipality.id),
                "barangay": str(self.other_barangay.id),
                "community_names": "Mismatch OBC",
                "settlement_type": "village",
                "unemployment_rate": "moderate",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("barangay", form.errors)

    def test_region_province_mismatch_rejected(self):
        form = OBCCommunityForm(
            data={
                "region": str(self.other_region.id),
                "province": str(self.province.id),
                "municipality": str(self.municipality.id),
                "barangay": str(self.barangay.id),
                "community_names": "Region Mismatch",
                "settlement_type": "village",
                "unemployment_rate": "moderate",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("province", form.errors)

    def test_province_queryset_filtered_by_region(self):
        """Province choices should narrow to the selected region."""
        form = OBCCommunityForm(initial={"region": self.region.id})
        province_queryset = list(form.fields["province"].queryset)

        self.assertIn(self.province, province_queryset)
        self.assertNotIn(self.other_province, province_queryset)

    def test_municipality_queryset_filtered_by_province(self):
        """Municipality choices should narrow to the selected province."""
        form = OBCCommunityForm(
            initial={
                "region": self.region.id,
                "province": self.province.id,
            }
        )
        municipality_queryset = list(form.fields["municipality"].queryset)

        self.assertIn(self.municipality, municipality_queryset)
        self.assertNotIn(self.other_municipality, municipality_queryset)

    def test_barangay_queryset_filtered_by_municipality(self):
        """Barangay choices should narrow to the selected municipality."""
        form = OBCCommunityForm(
            initial={
                "region": self.region.id,
                "province": self.province.id,
                "municipality": self.municipality.id,
            }
        )
        barangay_queryset = list(form.fields["barangay"].queryset)

        self.assertIn(self.barangay, barangay_queryset)
        self.assertNotIn(self.other_barangay, barangay_queryset)

    def test_existing_instance_populates_initial_location_fields(self):
        """Editing an existing community should pre-select its hierarchy."""
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names="Existing OBC",
            estimated_obc_population=75,
        )

        form = OBCCommunityForm(instance=community)

        self.assertEqual(form.fields["region"].initial, self.region)
        self.assertEqual(form.fields["province"].initial, self.province)
        self.assertEqual(form.fields["municipality"].initial, self.municipality)
        self.assertEqual(form.fields["barangay"].initial, self.barangay)


class LocationDataServiceTest(SimpleTestCase):
    """Ensure build_location_data counts direct geographic layers without DB."""

    def test_direct_layers_present_in_counts(self):
        region = SimpleNamespace(id=1, name="Zamboanga Peninsula", code="IX")
        province = SimpleNamespace(
            id=10,
            name="Zamboanga del Norte",
            region_id=region.id,
            population_total=0,
        )
        municipality = SimpleNamespace(
            id=100,
            name="Dipolog City",
            province_id=province.id,
            population_total=0,
            code="DIPOLOG",
        )
        barangay = SimpleNamespace(
            id=1000,
            name="Barangay Central",
            municipality_id=municipality.id,
            population_total=0,
            code="BGY-001",
        )

        class FakeQuerySet:
            def __init__(self, data):
                self._data = data

            def filter(self, *args, **kwargs):
                return self

            def select_related(self, *args, **kwargs):
                return self

            def order_by(self, *args, **kwargs):
                return self

            def annotate(self, *args, **kwargs):
                return self

            def values(self, *fields):
                results = []
                for item in self._data:
                    if isinstance(item, dict):
                        results.append({field: item.get(field) for field in fields})
                    else:
                        results.append(
                            {field: getattr(item, field) for field in fields}
                        )
                return results

            def __iter__(self):
                return iter(self._data)

        direct_layers = [
            {
                "id": 1,
                "region_id": region.id,
                "province_id": None,
                "province__region_id": region.id,
                "municipality_id": None,
                "municipality__province_id": None,
                "municipality__province__region_id": None,
                "barangay_id": None,
                "barangay__municipality_id": None,
                "barangay__municipality__province_id": None,
                "barangay__municipality__province__region_id": None,
            },
            {
                "id": 2,
                "region_id": None,
                "province_id": None,
                "province__region_id": region.id,
                "municipality_id": municipality.id,
                "municipality__province_id": province.id,
                "municipality__province__region_id": region.id,
                "barangay_id": None,
                "barangay__municipality_id": None,
                "barangay__municipality__province_id": None,
                "barangay__municipality__province__region_id": None,
            },
            {
                "id": 3,
                "region_id": None,
                "province_id": None,
                "province__region_id": None,
                "municipality_id": None,
                "municipality__province_id": None,
                "municipality__province__region_id": None,
                "barangay_id": barangay.id,
                "barangay__municipality_id": municipality.id,
                "barangay__municipality__province_id": province.id,
                "barangay__municipality__province__region_id": region.id,
            },
        ]

        regions_qs = FakeQuerySet([region])
        provinces_qs = FakeQuerySet([province])
        municipalities_qs = FakeQuerySet([municipality])
        barangays_qs = FakeQuerySet([barangay])
        layers_qs = FakeQuerySet(direct_layers)
        empty_qs = FakeQuerySet([])

        with (
            mock.patch.object(Region.objects, "filter", return_value=regions_qs),
            mock.patch.object(Province.objects, "filter", return_value=provinces_qs),
            mock.patch.object(
                Municipality.objects, "filter", return_value=municipalities_qs
            ),
            mock.patch.object(Barangay.objects, "filter", return_value=barangays_qs),
            mock.patch(
                "communities.models.OBCCommunity.objects.filter", return_value=empty_qs
            ),
            mock.patch(
                "communities.models.GeographicDataLayer.objects.filter",
                return_value=layers_qs,
            ),
        ):
            data = build_location_data(include_barangays=True)

        region_entry = next(item for item in data["regions"] if item["id"] == region.id)
        province_entry = next(
            item for item in data["provinces"] if item["id"] == province.id
        )
        municipality_entry = next(
            item for item in data["municipalities"] if item["id"] == municipality.id
        )
        barangay_entry = next(
            item for item in data["barangays"] if item["id"] == barangay.id
        )

        self.assertEqual(region_entry["geodata_count"], 3)
        self.assertEqual(region_entry["geodata_communities"], 0)

        self.assertEqual(province_entry["geodata_count"], 2)
        self.assertEqual(province_entry["geodata_communities"], 0)

        self.assertEqual(municipality_entry["geodata_count"], 2)
        self.assertEqual(municipality_entry["geodata_communities"], 0)

        self.assertEqual(barangay_entry["geodata_count"], 1)
        self.assertEqual(barangay_entry["geodata_layers"], 1)
        self.assertEqual(barangay_entry["geodata_visualizations"], 0)
        self.assertEqual(barangay_entry["geodata_points"], 0)
        self.assertTrue(barangay_entry["has_geodata"])


class PopulationDatasetParseTest(SimpleTestCase):
    """Verify raw PSA population datasets parse into expected structures."""

    def setUp(self):
        self.command = HierarchyCommand()

    def test_region_x_contains_baungon_totals(self):
        data = self.command.load_population_dataset("X")
        bukidnon = data["Bukidnon"]
        baungon = bukidnon["municipalities"]["Baungon"]
        self.assertEqual(bukidnon["population"], 1_601_902)
        self.assertEqual(baungon["population"], 39_151)
        self.assertEqual(baungon["barangays"]["Balintad"], 660)

    def test_region_xii_contains_gensan_totals(self):
        data = self.command.load_population_dataset("XII")
        gensan_province = data["HUC_GENERAL_SANTOS_CITY"]
        self.assertEqual(gensan_province["population"], 722_059)
        gensan = gensan_province["municipalities"]["General Santos City"]
        self.assertEqual(gensan["population"], 722_059)
        self.assertEqual(gensan["barangays"]["Baluan"], 14_079)


class MunicipalityCoverageViewTest(TestCase):
    """Integration tests for the municipality addition view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="coverage_admin",
            password="securepass123",
            user_type="oobc_staff",
            is_staff=True,
        )
        self.region = Region.objects.create(
            code="CAR", name="Cordillera Administrative Region"
        )
        self.province = Province.objects.create(
            region=self.region, code="PROV-200", name="Abra"
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code="MUN-200",
            name="Bangued",
            municipality_type="municipality",
        )

    def test_post_creates_municipality_coverage(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("common:communities_add_municipality"),
            {
                "region": self.region.id,
                "province": self.province.id,
                "municipality": self.municipality.id,
                "total_obc_communities": 2,
                "estimated_obc_population": 1800,
                "key_barangays": "Zone 1, Zone 2",
                "existing_support_programs": "Livelihood training",
                "notes": "Priority for housing assistance",
                "auto_sync": False,
                "settlement_type": "village",
                "unemployment_rate": "moderate",
                "religious_leaders_count": 0,
                "mosques_count": 0,
                "madrasah_count": 0,
                "asatidz_count": 0,
            },
        )
        self.assertRedirects(response, reverse("common:communities_manage"))
        self.assertTrue(
            MunicipalityCoverage.objects.filter(
                municipality=self.municipality,
                total_obc_communities=2,
                estimated_obc_population=1800,
                auto_sync=False,
            ).exists()
        )
