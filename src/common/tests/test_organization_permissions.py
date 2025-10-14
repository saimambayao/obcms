"""
Tests for organization permissions.

Tests the OrganizationAccessPermission for Django REST Framework views.
"""
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from common.permissions.organization import OrganizationAccessPermission
from organizations.models import Organization, OrganizationMembership

User = get_user_model()


class MockView:
    """Mock view for testing."""
    pass


class OrganizationAccessPermissionTest(TestCase):
    """Test OrganizationAccessPermission."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.permission = OrganizationAccessPermission()
        self.view = MockView()

        # Create test organization
        self.org = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='ministry',
            is_active=True
        )

    def test_permission_granted_with_organization(self):
        """Test permission granted when organization context exists."""
        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        has_perm = self.permission.has_permission(request, self.view)
        # In OBCMS mode (default), should be True
        self.assertTrue(has_perm)

    def test_permission_denied_without_organization(self):
        """Test permission denied when organization context missing."""
        request = self.factory.get('/')
        request.user = self.user
        # No organization

        has_perm = self.permission.has_permission(request, self.view)
        self.assertFalse(has_perm)

    def test_permission_granted_for_superuser(self):
        """Test permission always granted for superusers."""
        self.user.is_superuser = True
        self.user.save()

        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        has_perm = self.permission.has_permission(request, self.view)
        self.assertTrue(has_perm)

    def test_permission_validates_membership(self):
        """Test permission validates OrganizationMembership."""
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

        has_perm = self.permission.has_permission(request, self.view)
        # Should be True (has membership)
        self.assertTrue(has_perm)

    def test_has_object_permission_validates_organization(self):
        """Test has_object_permission() validates object organization."""
        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        # Create mock object with organization
        class MockObject:
            def __init__(self, org):
                self.organization = org
                self.pk = 1
                self.__class__.__name__ = 'MockObject'

        obj = MockObject(self.org)

        has_perm = self.permission.has_object_permission(request, self.view, obj)
        self.assertTrue(has_perm)

    def test_has_object_permission_blocks_cross_org_access(self):
        """Test has_object_permission() blocks cross-organization access."""
        # Create another organization
        other_org = Organization.objects.create(
            code='MOA1',
            name='Test Ministry 1',
            org_type='ministry',
            is_active=True
        )

        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        # Create mock object with different organization
        class MockObject:
            def __init__(self, org):
                self.organization = org
                self.pk = 1
                self.__class__.__name__ = 'MockObject'

        obj = MockObject(other_org)

        has_perm = self.permission.has_object_permission(request, self.view, obj)
        self.assertFalse(has_perm)

    def test_has_object_permission_allows_non_org_objects(self):
        """Test has_object_permission() allows objects without organization."""
        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        # Create mock object without organization attribute
        class MockObject:
            def __init__(self):
                self.pk = 1

        obj = MockObject()

        has_perm = self.permission.has_object_permission(request, self.view, obj)
        # Should allow objects that don't have organization attribute
        self.assertTrue(has_perm)

    def test_permission_denied_for_unauthenticated(self):
        """Test permission denied for unauthenticated users in BMMS mode."""
        from unittest.mock import patch

        request = self.factory.get('/')
        request.user = None
        request.organization = self.org

        # Mock BMMS mode
        with patch('common.permissions.organization.is_bmms_mode', return_value=True):
            has_perm = self.permission.has_permission(request, self.view)
            self.assertFalse(has_perm)

    def test_permission_denied_for_inactive_membership(self):
        """Test permission denied when membership is inactive."""
        from unittest.mock import patch

        # Create inactive membership
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org,
            role='member',
            is_active=False
        )

        request = self.factory.get('/')
        request.user = self.user
        request.organization = self.org

        # Mock BMMS mode
        with patch('common.permissions.organization.is_bmms_mode', return_value=True):
            has_perm = self.permission.has_permission(request, self.view)
            self.assertFalse(has_perm)
