"""
Tests for organization mixins.

Tests the OrganizationRequiredMixin for class-based views.
"""
from django.test import TestCase, RequestFactory
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from common.mixins.organization import OrganizationRequiredMixin
from organizations.models import Organization, OrganizationMembership

User = get_user_model()


class TestView(OrganizationRequiredMixin, ListView):
    """Test view using OrganizationRequiredMixin."""
    model = User
    template_name = 'test.html'


class OptionalOrgView(OrganizationRequiredMixin, ListView):
    """Test view with optional organization."""
    model = User
    template_name = 'test.html'
    require_organization = False


class OrganizationRequiredMixinTest(TestCase):
    """Test OrganizationRequiredMixin."""

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

    def test_mixin_allows_request_with_organization(self):
        """Test mixin allows request with organization context."""
        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        view = TestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_mixin_blocks_request_without_organization(self):
        """Test mixin blocks request without organization context."""
        request = self.factory.get('/')
        request.user = self.user
        # No organization

        view = TestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_mixin_allows_superuser(self):
        """Test mixin allows superuser access."""
        self.user.is_superuser = True
        self.user.save()

        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        view = TestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_mixin_validates_membership(self):
        """Test mixin validates OrganizationMembership."""
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

        view = TestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_organization_returns_organization(self):
        """Test get_organization() returns current organization."""
        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        view = TestView()
        view.setup(request)
        view.dispatch(request)

        org = view.get_organization()
        self.assertEqual(org, self.org)
        self.assertEqual(org.code, 'OOBC')

    def test_get_organization_raises_error_if_called_early(self):
        """Test get_organization() raises error if called before dispatch."""
        view = TestView()

        with self.assertRaises(ImproperlyConfigured):
            view.get_organization()

    def test_get_context_data_includes_organization(self):
        """Test get_context_data() adds organization to context."""
        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        view = TestView()
        view.setup(request)
        view.object_list = User.objects.none()

        context = view.get_context_data()

        self.assertIn('organization', context)
        self.assertEqual(context['organization'], self.org)

    def test_optional_organization_allows_no_org(self):
        """Test require_organization=False allows requests without org."""
        request = self.factory.get('/')
        request.user = self.user
        # No organization

        view = OptionalOrgView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_organization_returns_none_when_optional(self):
        """Test get_organization() returns None when org optional and not set."""
        request = self.factory.get('/')
        request.user = self.user
        # No organization

        view = OptionalOrgView()
        view.setup(request)
        view.dispatch(request)

        org = view.get_organization()
        self.assertIsNone(org)
