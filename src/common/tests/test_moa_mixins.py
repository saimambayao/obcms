"""
Comprehensive tests for MOA RBAC view mixins.

Tests all three mixins from common.mixins module:
- MOAFilteredQuerySetMixin
- MOAOrganizationAccessMixin
- MOAPPAAccessMixin
- MOAViewOnlyMixin
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory
from django.views.generic import ListView, DetailView, UpdateView

from common.mixins import (
    MOAFilteredQuerySetMixin,
    MOAOrganizationAccessMixin,
    MOAPPAAccessMixin,
    MOAViewOnlyMixin,
)
from coordination.models import Organization

User = get_user_model()


@pytest.mark.django_db
class TestMOAFilteredQuerySetMixin(TestCase):
    """Test suite for MOAFilteredQuerySetMixin."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create organizations
        self.moa_health = Organization.objects.create(
            name="Ministry of Health",
            organization_type="bmoa",
            is_active=True,
        )
        self.moa_education = Organization.objects.create(
            name="Ministry of Education",
            organization_type="bmoa",
            is_active=True,
        )

        # Create users
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@oobc.gov.ph",
            password="testpass123",
        )

        self.oobc_staff = User.objects.create_user(
            username="oobc_user",
            email="oobc@oobc.gov.ph",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.moa_user_health = User.objects.create_user(
            username="moa_health",
            email="health@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.moa_health,
            is_approved=True,
        )

        self.moa_user_edu = User.objects.create_user(
            username="moa_education",
            email="edu@moa.gov.ph",
            password="testpass123",
            user_type="lgu",
            moa_organization=self.moa_education,
            is_approved=True,
        )

    def test_filters_queryset_for_moa_user(self):
        """MOA users see only their organization in queryset."""

        class TestListView(MOAFilteredQuerySetMixin, ListView):
            model = Organization
            moa_filter_field = "id"  # Filter by organization itself

        request = self.factory.get("/orgs/")
        request.user = self.moa_user_health

        view = TestListView()
        view.request = request
        view.object_list = view.get_queryset()

        # Should only contain health organization
        self.assertEqual(view.object_list.count(), 1)
        self.assertEqual(view.object_list.first(), self.moa_health)

    def test_does_not_filter_for_oobc_staff(self):
        """OOBC staff see all items in queryset."""

        class TestListView(MOAFilteredQuerySetMixin, ListView):
            model = Organization
            moa_filter_field = "id"

        request = self.factory.get("/orgs/")
        request.user = self.oobc_staff

        view = TestListView()
        view.request = request
        view.object_list = view.get_queryset()

        # Should see all organizations
        self.assertEqual(view.object_list.count(), 2)

    def test_does_not_filter_for_superuser(self):
        """Superusers see all items in queryset."""

        class TestListView(MOAFilteredQuerySetMixin, ListView):
            model = Organization
            moa_filter_field = "id"

        request = self.factory.get("/orgs/")
        request.user = self.superuser

        view = TestListView()
        view.request = request
        view.object_list = view.get_queryset()

        # Should see all organizations
        self.assertEqual(view.object_list.count(), 2)

    def test_custom_filter_field(self):
        """Mixin respects custom moa_filter_field attribute."""

        class TestListView(MOAFilteredQuerySetMixin, ListView):
            model = Organization
            moa_filter_field = "id"  # Custom field

        request = self.factory.get("/orgs/")
        request.user = self.moa_user_health

        view = TestListView()
        view.request = request
        view.object_list = view.get_queryset()

        self.assertEqual(view.object_list.count(), 1)

    def test_no_filter_field_does_not_break(self):
        """Mixin handles missing moa_filter_field gracefully."""

        class TestListView(MOAFilteredQuerySetMixin, ListView):
            model = Organization
            moa_filter_field = None  # No filtering

        request = self.factory.get("/orgs/")
        request.user = self.moa_user_health

        view = TestListView()
        view.request = request
        view.object_list = view.get_queryset()

        # Should return all (no filtering applied)
        self.assertEqual(view.object_list.count(), 2)


@pytest.mark.django_db
class TestMOAOrganizationAccessMixin(TestCase):
    """Test suite for MOAOrganizationAccessMixin."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        self.moa_health = Organization.objects.create(
            name="Ministry of Health",
            organization_type="bmoa",
            is_active=True,
        )
        self.moa_education = Organization.objects.create(
            name="Ministry of Education",
            organization_type="bmoa",
            is_active=True,
        )

        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@oobc.gov.ph", password="testpass123"
        )

        self.oobc_staff = User.objects.create_user(
            username="oobc_user",
            email="oobc@oobc.gov.ph",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.moa_user_health = User.objects.create_user(
            username="moa_health",
            email="health@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.moa_health,
            is_approved=True,
        )

    def test_allows_moa_user_to_access_own_org(self):
        """MOA user can access their own organization."""

        class TestDetailView(MOAOrganizationAccessMixin, DetailView):
            model = Organization

        request = self.factory.get(f"/orgs/{self.moa_health.pk}/")
        request.user = self.moa_user_health

        view = TestDetailView()
        view.request = request
        view.kwargs = {"pk": self.moa_health.pk}

        obj = view.get_object()
        self.assertEqual(obj, self.moa_health)

    def test_blocks_moa_user_from_other_org(self):
        """MOA user cannot access other organization."""

        class TestDetailView(MOAOrganizationAccessMixin, DetailView):
            model = Organization

        request = self.factory.get(f"/orgs/{self.moa_education.pk}/")
        request.user = self.moa_user_health

        view = TestDetailView()
        view.request = request
        view.kwargs = {"pk": self.moa_education.pk}

        with self.assertRaises(PermissionDenied) as context:
            view.get_object()

        self.assertIn("your own MOA organization", str(context.exception))

    def test_allows_oobc_staff_to_access_any_org(self):
        """OOBC staff can access any organization."""

        class TestDetailView(MOAOrganizationAccessMixin, DetailView):
            model = Organization

        request = self.factory.get(f"/orgs/{self.moa_education.pk}/")
        request.user = self.oobc_staff

        view = TestDetailView()
        view.request = request
        view.kwargs = {"pk": self.moa_education.pk}

        obj = view.get_object()
        self.assertEqual(obj, self.moa_education)

    def test_allows_superuser_to_access_any_org(self):
        """Superuser can access any organization."""

        class TestDetailView(MOAOrganizationAccessMixin, DetailView):
            model = Organization

        request = self.factory.get(f"/orgs/{self.moa_education.pk}/")
        request.user = self.superuser

        view = TestDetailView()
        view.request = request
        view.kwargs = {"pk": self.moa_education.pk}

        obj = view.get_object()
        self.assertEqual(obj, self.moa_education)


@pytest.mark.django_db
class TestMOAViewOnlyMixin(TestCase):
    """Test suite for MOAViewOnlyMixin."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        self.moa = Organization.objects.create(
            name="Test MOA", organization_type="bmoa", is_active=True
        )

        self.moa_user = User.objects.create_user(
            username="moa_test",
            email="test@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.moa,
            is_approved=True,
        )

        self.oobc_staff = User.objects.create_user(
            username="oobc_user",
            email="oobc@oobc.gov.ph",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

    def test_allows_get_for_moa_user(self):
        """MOA users can make GET requests."""

        class TestListView(MOAViewOnlyMixin, ListView):
            model = Organization

        request = self.factory.get("/orgs/")
        request.user = self.moa_user

        view = TestListView.as_view()
        response = view(request)

        # Should succeed (status 200)
        self.assertEqual(response.status_code, 200)

    def test_blocks_post_for_moa_user(self):
        """MOA users cannot make POST requests."""

        class TestListView(MOAViewOnlyMixin, ListView):
            model = Organization

        request = self.factory.post("/orgs/")
        request.user = self.moa_user

        view = TestListView.as_view()

        with self.assertRaises(PermissionDenied) as context:
            view(request)

        self.assertIn("view-only", str(context.exception))

    def test_blocks_delete_for_moa_user(self):
        """MOA users cannot make DELETE requests."""

        class TestDetailView(MOAViewOnlyMixin, DetailView):
            model = Organization

        request = self.factory.delete(f"/orgs/{self.moa.pk}/")
        request.user = self.moa_user

        view = TestDetailView.as_view()

        with self.assertRaises(PermissionDenied):
            view(request, pk=self.moa.pk)

    def test_allows_post_for_oobc_staff(self):
        """OOBC staff can make POST requests."""
        from django.http import HttpResponse

        class TestListView(MOAViewOnlyMixin, ListView):
            model = Organization

            def post(self, request, *args, **kwargs):
                # Add POST support for testing
                return HttpResponse(status=200)

        request = self.factory.post("/orgs/")
        request.user = self.oobc_staff

        view = TestListView.as_view()
        response = view(request)

        # Should succeed (not raise PermissionDenied)
        self.assertEqual(response.status_code, 200)

    def test_allows_head_and_options_for_moa(self):
        """MOA users can make HEAD and OPTIONS requests."""

        class TestListView(MOAViewOnlyMixin, ListView):
            model = Organization

        # HEAD request
        request = self.factory.head("/orgs/")
        request.user = self.moa_user
        view = TestListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # OPTIONS request
        request = self.factory.options("/orgs/")
        request.user = self.moa_user
        view = TestListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)


@pytest.mark.django_db
class TestMixinIntegration(TestCase):
    """Test mixins working together in realistic scenarios."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        self.moa_health = Organization.objects.create(
            name="Ministry of Health",
            organization_type="bmoa",
            is_active=True,
        )
        self.moa_education = Organization.objects.create(
            name="Ministry of Education",
            organization_type="bmoa",
            is_active=True,
        )

        self.moa_user_health = User.objects.create_user(
            username="moa_health",
            email="health@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.moa_health,
            is_approved=True,
        )

        self.oobc_staff = User.objects.create_user(
            username="oobc_user",
            email="oobc@oobc.gov.ph",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

    def test_filtered_list_with_view_only(self):
        """Combine filtering and view-only restrictions."""

        class OrganizationListView(MOAFilteredQuerySetMixin, MOAViewOnlyMixin, ListView):
            model = Organization
            moa_filter_field = "id"

        # MOA user - GET allowed, sees only own org
        request = self.factory.get("/orgs/")
        request.user = self.moa_user_health

        view = OrganizationListView()
        view.request = request
        view.object_list = view.get_queryset()

        self.assertEqual(view.object_list.count(), 1)
        self.assertEqual(view.object_list.first(), self.moa_health)

        # MOA user - POST blocked
        request = self.factory.post("/orgs/")
        request.user = self.moa_user_health

        view = OrganizationListView.as_view()
        with self.assertRaises(PermissionDenied):
            view(request)

    def test_organization_detail_with_access_control(self):
        """Combine organization access and view-only."""

        class OrganizationDetailView(
            MOAOrganizationAccessMixin, MOAViewOnlyMixin, DetailView
        ):
            model = Organization

        # MOA user - can view own org
        request = self.factory.get(f"/orgs/{self.moa_health.pk}/")
        request.user = self.moa_user_health

        view = OrganizationDetailView()
        view.request = request
        view.kwargs = {"pk": self.moa_health.pk}

        obj = view.get_object()
        self.assertEqual(obj, self.moa_health)

        # MOA user - cannot edit even own org (view-only)
        request = self.factory.put(f"/orgs/{self.moa_health.pk}/")
        request.user = self.moa_user_health

        view = OrganizationDetailView.as_view()
        with self.assertRaises(PermissionDenied):
            view(request, pk=self.moa_health.pk)

    def test_oobc_staff_bypasses_all_restrictions(self):
        """OOBC staff should not be restricted by any mixin."""
        from django.http import HttpResponse

        class RestrictedListView(MOAFilteredQuerySetMixin, MOAViewOnlyMixin, ListView):
            model = Organization
            moa_filter_field = "id"

            def post(self, request, *args, **kwargs):
                # Add POST support for testing
                return HttpResponse(status=200)

        # OOBC staff - sees all orgs
        request = self.factory.get("/orgs/")
        request.user = self.oobc_staff

        view = RestrictedListView()
        view.request = request
        view.object_list = view.get_queryset()

        self.assertEqual(view.object_list.count(), 2)

        # OOBC staff - can POST
        request = self.factory.post("/orgs/")
        request.user = self.oobc_staff

        view = RestrictedListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
