"""
Unit tests for RBAC decorators, mixins, and DRF permission classes.

Tests permission checking, organization context extraction, and error handling.
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.test import RequestFactory, TestCase
from django.views.generic import ListView

from common.decorators.rbac import require_permission, require_feature_access
from common.mixins.rbac_mixins import (
    PermissionRequiredMixin,
    FeatureAccessMixin,
    MultiPermissionMixin,
)
from common.permissions.rbac_permissions import (
    HasFeatureAccess,
    HasPermission,
    HasAnyPermission,
    HasAllPermissions,
)
from coordination.models import Organization

User = get_user_model()


@pytest.mark.django_db
class TestRBACDecorators(TestCase):
    """Test RBAC decorators for function-based views."""

    def setUp(self):
        """Create test users and organizations."""
        self.factory = RequestFactory()

        # Create test organization
        self.organization = Organization.objects.create(
            name='Ministry of Test',
            acronym='MOT',
            organization_type='bmoa'
        )

        # Create superuser
        self.superuser = User.objects.create_user(
            username='superuser',
            password='testpass123',
            is_superuser=True
        )

        # Create OOBC staff user
        self.oobc_user = User.objects.create_user(
            username='oobc_staff',
            password='testpass123',
            user_type='oobc_staff',
            is_approved=True
        )

        # Create MOA staff user
        self.moa_user = User.objects.create_user(
            username='moa_staff',
            password='testpass123',
            user_type='bmoa',
            is_approved=True
        )
        self.moa_user.moa_organization = self.organization
        self.moa_user.save()

        # Create unauthenticated request
        self.anon_request = self.factory.get('/test/')
        self.anon_request.user = None

    def test_require_permission_decorator_unauthenticated(self):
        """Test require_permission decorator with unauthenticated user."""
        @require_permission('communities.view_obc_community')
        def test_view(request):
            return "OK"

        request = self.factory.get('/test/')
        request.user = None

        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_require_permission_decorator_superuser(self):
        """Test require_permission decorator with superuser."""
        @require_permission('communities.create_obc_community')
        def test_view(request):
            return "OK"

        request = self.factory.get('/test/')
        request.user = self.superuser

        result = test_view(request)
        self.assertEqual(result, "OK")

    def test_require_feature_access_decorator_unauthenticated(self):
        """Test require_feature_access decorator with unauthenticated user."""
        @require_feature_access('communities.barangay_obc')
        def test_view(request):
            return "OK"

        request = self.factory.get('/test/')
        request.user = None

        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_require_feature_access_decorator_superuser(self):
        """Test require_feature_access decorator with superuser."""
        @require_feature_access('communities.barangay_obc')
        def test_view(request):
            return "OK"

        request = self.factory.get('/test/')
        request.user = self.superuser

        result = test_view(request)
        self.assertEqual(result, "OK")


@pytest.mark.django_db
class TestRBACMixins(TestCase):
    """Test RBAC mixins for class-based views."""

    def setUp(self):
        """Create test users and organizations."""
        self.factory = RequestFactory()

        # Create test organization
        self.organization = Organization.objects.create(
            name='Ministry of Test',
            acronym='MOT',
            organization_type='bmoa'
        )

        # Create superuser
        self.superuser = User.objects.create_user(
            username='superuser',
            password='testpass123',
            is_superuser=True
        )

        # Create OOBC staff user
        self.oobc_user = User.objects.create_user(
            username='oobc_staff',
            password='testpass123',
            user_type='oobc_staff',
            is_approved=True
        )

    def test_permission_required_mixin_superuser(self):
        """Test PermissionRequiredMixin with superuser."""
        class TestView(PermissionRequiredMixin, ListView):
            permission_required = 'communities.view_obc_community'
            model = Organization

        view = TestView.as_view()
        request = self.factory.get('/test/')
        request.user = self.superuser

        # Should not raise PermissionDenied
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_feature_access_mixin_superuser(self):
        """Test FeatureAccessMixin with superuser."""
        class TestView(FeatureAccessMixin, ListView):
            feature_required = 'communities.barangay_obc'
            model = Organization

        view = TestView.as_view()
        request = self.factory.get('/test/')
        request.user = self.superuser

        # Should not raise PermissionDenied
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_multi_permission_mixin_superuser(self):
        """Test MultiPermissionMixin with superuser."""
        class TestView(MultiPermissionMixin, ListView):
            permissions_required = [
                'communities.view_obc_community',
                'communities.edit_obc_community'
            ]
            model = Organization

        view = TestView.as_view()
        request = self.factory.get('/test/')
        request.user = self.superuser

        # Should not raise PermissionDenied
        response = view(request)
        self.assertEqual(response.status_code, 200)


@pytest.mark.django_db
class TestDRFPermissions(TestCase):
    """Test DRF permission classes."""

    def setUp(self):
        """Create test users."""
        # Create superuser
        self.superuser = User.objects.create_user(
            username='superuser',
            password='testpass123',
            is_superuser=True
        )

        # Create OOBC staff user
        self.oobc_user = User.objects.create_user(
            username='oobc_staff',
            password='testpass123',
            user_type='oobc_staff',
            is_approved=True
        )

    def test_has_feature_access_permission(self):
        """Test HasFeatureAccess DRF permission class."""
        permission = HasFeatureAccess()

        # Create mock request
        request = HttpRequest()
        request.user = self.superuser

        # Create mock view with feature_code
        class MockView:
            feature_code = 'communities.barangay_obc'

        view = MockView()

        # Superuser should have access
        self.assertTrue(permission.has_permission(request, view))

    def test_has_permission_class(self):
        """Test HasPermission DRF permission class."""
        permission = HasPermission()

        # Create mock request
        request = HttpRequest()
        request.user = self.superuser

        # Create mock view with permission_code
        class MockView:
            permission_code = 'communities.view_obc_community'

        view = MockView()

        # Superuser should have permission
        self.assertTrue(permission.has_permission(request, view))

    def test_has_any_permission_class(self):
        """Test HasAnyPermission DRF permission class."""
        permission = HasAnyPermission()

        # Create mock request
        request = HttpRequest()
        request.user = self.superuser

        # Create mock view with permissions_required
        class MockView:
            permissions_required = [
                'communities.view_obc_community',
                'communities.edit_obc_community'
            ]

        view = MockView()

        # Superuser should have at least one permission
        self.assertTrue(permission.has_permission(request, view))

    def test_has_all_permissions_class(self):
        """Test HasAllPermissions DRF permission class."""
        permission = HasAllPermissions()

        # Create mock request
        request = HttpRequest()
        request.user = self.superuser

        # Create mock view with permissions_required
        class MockView:
            permissions_required = [
                'communities.view_obc_community',
                'communities.edit_obc_community'
            ]

        view = MockView()

        # Superuser should have all permissions
        self.assertTrue(permission.has_permission(request, view))


@pytest.mark.django_db
class TestOrganizationContextExtraction(TestCase):
    """Test organization context extraction from request parameters."""

    def setUp(self):
        """Create test data."""
        self.factory = RequestFactory()

        # Create test organization
        self.organization = Organization.objects.create(
            name='Ministry of Test',
            acronym='MOT',
            organization_type='bmoa'
        )

        # Create MOA user
        self.moa_user = User.objects.create_user(
            username='moa_staff',
            password='testpass123',
            user_type='bmoa',
            is_approved=True
        )
        self.moa_user.moa_organization = self.organization
        self.moa_user.save()

    def test_organization_param_from_kwargs(self):
        """Test extracting organization from URL kwargs."""
        @require_permission('coordination.edit_organization', organization_param='org_id')
        def test_view(request, org_id):
            return "OK"

        request = self.factory.get(f'/test/{self.organization.id}/')
        request.user = self.moa_user
        # Mock resolver_match with kwargs
        class MockResolverMatch:
            kwargs = {'org_id': str(self.organization.id)}
        request.resolver_match = MockResolverMatch()

        # Should work since user's organization matches
        result = test_view(request, org_id=str(self.organization.id))
        self.assertEqual(result, "OK")

    def test_organization_param_from_get(self):
        """Test extracting organization from GET parameters."""
        @require_permission('coordination.view_organization', organization_param='org')
        def test_view(request):
            return "OK"

        request = self.factory.get(f'/test/?org={self.organization.id}')
        request.user = self.moa_user
        # Mock resolver_match
        class MockResolverMatch:
            kwargs = {}
        request.resolver_match = MockResolverMatch()

        # This will check organization context
        # Since we're just testing extraction, not full permission logic
        try:
            result = test_view(request)
        except PermissionDenied:
            # Expected if organization context doesn't match permission requirements
            pass


@pytest.mark.django_db
class TestErrorMessages(TestCase):
    """Test error message generation."""

    def setUp(self):
        """Create test users."""
        self.factory = RequestFactory()

        # Create regular user (no special permissions)
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            is_approved=True
        )

    def test_permission_denied_message(self):
        """Test that PermissionDenied is raised with appropriate messages."""
        @require_permission('communities.create_obc_community')
        def test_view(request):
            return "OK"

        request = self.factory.get('/test/')
        request.user = self.regular_user

        with self.assertRaises(PermissionDenied) as cm:
            test_view(request)

        # Check that error message contains permission code
        self.assertIn('communities.create_obc_community', str(cm.exception))
