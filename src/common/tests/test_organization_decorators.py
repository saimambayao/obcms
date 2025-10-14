"""
Tests for organization decorators.

Tests the @require_organization and @organization_param() decorators
for function-based views.
"""
from django.test import TestCase, RequestFactory
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model
from common.decorators.organization import require_organization, organization_param
from organizations.models import Organization, OrganizationMembership

User = get_user_model()


class RequireOrganizationDecoratorTest(TestCase):
    """Test @require_organization decorator."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create test organization
        self.org = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='ministry',
            is_active=True
        )

    def test_decorator_passes_with_organization(self):
        """Test decorator allows request with organization context."""
        @require_organization
        def test_view(request):
            return HttpResponse('OK')

        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')

    def test_decorator_blocks_without_organization(self):
        """Test decorator blocks request without organization context."""
        @require_organization
        def test_view(request):
            return HttpResponse('OK')

        request = self.factory.get('/')
        request.user = self.user
        # No organization set

        response = test_view(request)
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertIn('Organization context required', response.content.decode())

    def test_decorator_allows_superuser_in_bmms_mode(self):
        """Test decorator allows superuser access in BMMS mode."""
        @require_organization
        def test_view(request):
            return HttpResponse('OK')

        # Make user superuser
        self.user.is_superuser = True
        self.user.save()

        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        response = test_view(request)
        self.assertEqual(response.status_code, 200)

    def test_decorator_validates_membership_in_bmms_mode(self):
        """Test decorator validates OrganizationMembership in BMMS mode."""
        @require_organization
        def test_view(request):
            return HttpResponse('OK')

        # Create membership
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org,
            role='member',
            is_active=True
        )

        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        response = test_view(request)
        self.assertEqual(response.status_code, 200)


class OrganizationParamDecoratorTest(TestCase):
    """Test @organization_param() decorator."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create test organization
        self.org = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='ministry',
            is_active=True
        )

    def test_decorator_loads_organization_from_url(self):
        """Test decorator loads organization from URL parameter."""
        @organization_param('org_code')
        def test_view(request, org_code):
            return HttpResponse(f'Org: {request.organization.code}')

        request = self.factory.get('/')
        request.user = self.user

        response = test_view(request, org_code='OOBC')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Org: OOBC', response.content.decode())

    def test_decorator_handles_missing_parameter(self):
        """Test decorator returns 403 when parameter missing."""
        @organization_param('org_code')
        def test_view(request, org_code=None):
            return HttpResponse('OK')

        request = self.factory.get('/')
        request.user = self.user

        response = test_view(request)
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertIn('parameter', response.content.decode().lower())

    def test_decorator_handles_invalid_org_code(self):
        """Test decorator returns 403 for invalid organization code."""
        @organization_param('org_code')
        def test_view(request, org_code):
            return HttpResponse('OK')

        request = self.factory.get('/')
        request.user = self.user

        response = test_view(request, org_code='INVALID')
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_decorator_case_insensitive_lookup(self):
        """Test decorator performs case-insensitive organization lookup."""
        @organization_param('org_code')
        def test_view(request, org_code):
            return HttpResponse(f'Org: {request.organization.code}')

        request = self.factory.get('/')
        request.user = self.user

        # Test lowercase
        response = test_view(request, org_code='oobc')
        self.assertEqual(response.status_code, 200)

        # Test mixed case
        response = test_view(request, org_code='OoBc')
        self.assertEqual(response.status_code, 200)

    def test_decorator_validates_membership(self):
        """Test decorator validates membership for loaded organization."""
        @organization_param('org_code')
        def test_view(request, org_code):
            return HttpResponse('OK')

        # Create membership
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org,
            role='member',
            is_active=True
        )

        request = self.factory.get('/')
        request.user = self.user

        response = test_view(request, org_code='OOBC')
        self.assertEqual(response.status_code, 200)
