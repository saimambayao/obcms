"""
Tests for Organization Context Middleware and RBAC.

Tests organization-scoped data isolation for BMMS multi-tenant support.

Run: python manage.py test common.tests.test_organization_context
"""

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from coordination.models import Organization
from common.middleware.organization_context import (
    OrganizationContextMiddleware,
    get_organization_from_request,
    user_can_access_organization,
    is_ocm_user,
)
from common.services.rbac_service import RBACService


User = get_user_model()


class OrganizationContextMiddlewareTestCase(TestCase):
    """Test OrganizationContextMiddleware functionality."""

    def setUp(self):
        """Set up test data."""
        # Create organizations
        self.org_moa_a = Organization.objects.create(
            name='Ministry of Agriculture',
            acronym='MOA-A',
            organization_type='bmoa',
            is_active=True
        )
        self.org_moa_b = Organization.objects.create(
            name='Ministry of Education',
            acronym='MOE',
            organization_type='bmoa',
            is_active=True
        )
        self.org_ocm = Organization.objects.create(
            name='Office of the Chief Minister',
            acronym='OCM',
            organization_type='bmoa',
            is_active=True
        )

        # Create users
        self.oobc_staff = User.objects.create_user(
            username='oobc_staff',
            password='testpass123',
            user_type='oobc_staff'
        )

        self.moa_staff = User.objects.create_user(
            username='moa_staff',
            password='testpass123',
            user_type='bmoa',
            moa_organization=self.org_moa_a
        )

        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            password='testpass123',
            user_type='cm_office',
            moa_organization=self.org_ocm
        )

        # Create request factory
        self.factory = RequestFactory()

    def test_organization_from_url_kwargs(self):
        """Test extracting organization from URL kwargs."""
        request = self.factory.get(f'/test/{self.org_moa_a.id}/')
        request.user = self.oobc_staff

        # Mock resolver_match
        class MockResolverMatch:
            kwargs = {'org_id': str(self.org_moa_a.id)}

        request.resolver_match = MockResolverMatch()
        request.session = {}

        org = get_organization_from_request(request)
        self.assertEqual(org, self.org_moa_a)

    def test_organization_from_query_params(self):
        """Test extracting organization from query parameters."""
        request = self.factory.get(f'/test/?org={self.org_moa_a.id}')
        request.user = self.oobc_staff
        request.session = {}

        org = get_organization_from_request(request)
        self.assertEqual(org, self.org_moa_a)

    def test_organization_from_user_default(self):
        """Test using user's default organization."""
        request = self.factory.get('/test/')
        request.user = self.moa_staff
        request.session = {}

        org = get_organization_from_request(request)
        self.assertEqual(org, self.org_moa_a)

    def test_organization_access_validation(self):
        """Test that MOA staff can only access their organization."""
        request = self.factory.get(f'/test/?org={self.org_moa_b.id}')
        request.user = self.moa_staff
        request.session = {}

        # Should return None because MOA staff can't access other orgs
        org = get_organization_from_request(request)
        self.assertIsNone(org)

    def test_middleware_sets_organization(self):
        """Test middleware sets request.organization."""
        middleware = OrganizationContextMiddleware(lambda r: None)

        request = self.factory.get('/')
        request.user = self.moa_staff
        request.session = {}

        middleware(request)

        # Should have organization attribute (lazy)
        self.assertTrue(hasattr(request, 'organization'))
        # Evaluate lazy object
        self.assertEqual(request.organization, self.org_moa_a)


class UserAccessPermissionsTestCase(TestCase):
    """Test user access permissions for organizations."""

    def setUp(self):
        """Set up test data."""
        self.org_moa_a = Organization.objects.create(
            name='Ministry of Agriculture',
            acronym='MOA-A',
            organization_type='bmoa'
        )
        self.org_ocm = Organization.objects.create(
            name='Office of the Chief Minister',
            acronym='OCM',
            organization_type='bmoa'
        )

        self.oobc_staff = User.objects.create_user(
            username='oobc_staff',
            password='testpass123',
            user_type='oobc_staff'
        )
        self.moa_staff = User.objects.create_user(
            username='moa_staff',
            password='testpass123',
            user_type='bmoa',
            moa_organization=self.org_moa_a
        )
        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            password='testpass123',
            user_type='cm_office',
            moa_organization=self.org_ocm
        )

    def test_oobc_staff_can_access_any_organization(self):
        """Test OOBC staff can access any organization."""
        self.assertTrue(
            user_can_access_organization(self.oobc_staff, self.org_moa_a)
        )

    def test_moa_staff_can_access_own_organization(self):
        """Test MOA staff can access their own organization."""
        self.assertTrue(
            user_can_access_organization(self.moa_staff, self.org_moa_a)
        )

    def test_moa_staff_cannot_access_other_organization(self):
        """Test MOA staff cannot access other organizations."""
        org_other = Organization.objects.create(
            name='Other Ministry',
            acronym='OTHER',
            organization_type='bmoa'
        )
        self.assertFalse(
            user_can_access_organization(self.moa_staff, org_other)
        )

    def test_ocm_user_can_access_all_organizations(self):
        """Test OCM users can access all organizations."""
        self.assertTrue(
            user_can_access_organization(self.ocm_user, self.org_moa_a)
        )

    def test_ocm_user_detection(self):
        """Test is_ocm_user function."""
        self.assertTrue(is_ocm_user(self.ocm_user))
        self.assertFalse(is_ocm_user(self.moa_staff))
        self.assertFalse(is_ocm_user(self.oobc_staff))


class RBACServiceTestCase(TestCase):
    """Test RBACService organization context support."""

    def setUp(self):
        """Set up test data."""
        self.org_moa_a = Organization.objects.create(
            name='Ministry of Agriculture',
            acronym='MOA-A',
            organization_type='bmoa'
        )

        self.oobc_staff = User.objects.create_user(
            username='oobc_staff',
            password='testpass123',
            user_type='oobc_staff'
        )
        self.moa_staff = User.objects.create_user(
            username='moa_staff',
            password='testpass123',
            user_type='bmoa',
            moa_organization=self.org_moa_a
        )

        self.factory = RequestFactory()

    def test_get_organizations_with_access_oobc(self):
        """Test OOBC staff gets all organizations."""
        orgs = RBACService.get_organizations_with_access(self.oobc_staff)
        self.assertEqual(len(orgs), 1)  # MOA-A

    def test_get_organizations_with_access_moa(self):
        """Test MOA staff gets only their organization."""
        orgs = RBACService.get_organizations_with_access(self.moa_staff)
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0], self.org_moa_a)

    def test_can_switch_organization_oobc(self):
        """Test OOBC staff can switch organizations."""
        self.assertTrue(
            RBACService.can_switch_organization(self.oobc_staff)
        )

    def test_cannot_switch_organization_moa(self):
        """Test MOA staff cannot switch organizations."""
        self.assertFalse(
            RBACService.can_switch_organization(self.moa_staff)
        )

    def test_permission_check_with_organization_context(self):
        """Test permission checking respects organization context."""
        request = self.factory.get('/')
        request.user = self.moa_staff
        request.organization = self.org_moa_a

        # MOA staff can view their organization's data
        has_perm = RBACService.has_permission(
            request,
            'communities.view_obc_community',
            organization=self.org_moa_a
        )
        self.assertTrue(has_perm)

    def test_permission_denied_for_mana(self):
        """Test MOA staff cannot access MANA."""
        request = self.factory.get('/')
        request.user = self.moa_staff
        request.organization = self.org_moa_a

        # MOA staff cannot access MANA
        has_perm = RBACService.has_permission(
            request,
            'mana.view_assessment',
            organization=self.org_moa_a
        )
        self.assertFalse(has_perm)


class OrganizationScopedQuerySetTestCase(TestCase):
    """Test organization-scoped queryset filtering."""

    def setUp(self):
        """Set up test data."""
        from common.mixins.organization_mixins import OrganizationFilteredMixin
        from django.views.generic import ListView

        self.org_a = Organization.objects.create(
            name='Org A',
            acronym='ORGA',
            organization_type='bmoa'
        )
        self.org_b = Organization.objects.create(
            name='Org B',
            acronym='ORGB',
            organization_type='bmoa'
        )

        self.moa_staff_a = User.objects.create_user(
            username='moa_a',
            password='testpass123',
            user_type='bmoa',
            moa_organization=self.org_a
        )

        # Create test view
        class TestView(OrganizationFilteredMixin, ListView):
            model = Organization
            organization_filter_field = 'id'

            def get(self, request, *args, **kwargs):
                qs = self.get_queryset()
                return {'count': qs.count()}

        self.view_class = TestView
        self.factory = RequestFactory()

    def test_moa_staff_sees_only_their_organization(self):
        """Test MOA staff queryset filtered to their organization."""
        request = self.factory.get('/')
        request.user = self.moa_staff_a
        request.organization = self.org_a

        view = self.view_class()
        view.request = request

        qs = view.get_queryset()

        # Should only see their organization
        # Note: This test uses Organization as model, so filtering by id
        # In real usage, you'd filter related models
        self.assertIn(self.org_a, qs)


class OCMAggregationTestCase(TestCase):
    """Test OCM aggregation access."""

    def setUp(self):
        """Set up test data."""
        self.org_ocm = Organization.objects.create(
            name='Office of the Chief Minister',
            acronym='OCM',
            organization_type='bmoa'
        )

        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            password='testpass123',
            user_type='cm_office',
            moa_organization=self.org_ocm
        )

        self.factory = RequestFactory()

    def test_ocm_read_only_enforcement(self):
        """Test OCM users have read-only access."""
        from common.mixins.ocm_mixins import OCMAggregationMixin
        from django.views.generic import ListView

        class TestOCMView(OCMAggregationMixin, ListView):
            model = Organization
            ocm_read_only = True

            def post(self, request, *args, **kwargs):
                return {'success': True}

        view = TestOCMView.as_view()
        request = self.factory.post('/')
        request.user = self.ocm_user

        # Should raise PermissionDenied for POST
        with self.assertRaises(PermissionDenied):
            view(request)

    def test_ocm_can_view(self):
        """Test OCM users can view (GET requests)."""
        from common.mixins.ocm_mixins import OCMAggregationMixin
        from django.views.generic import ListView
        from django.http import JsonResponse

        class TestOCMView(OCMAggregationMixin, ListView):
            model = Organization
            ocm_read_only = True

            def get(self, request, *args, **kwargs):
                return JsonResponse({'success': True})

        view = TestOCMView.as_view()
        request = self.factory.get('/')
        request.user = self.ocm_user

        # Should succeed for GET
        response = view(request)
        self.assertEqual(response.status_code, 200)
