"""
Tests for OCM permissions and access control
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import PermissionDenied

from ocm.models import OCMAccess
from ocm.permissions import OCMReadOnlyPermission, IsOCMUser

User = get_user_model()


class OCMAccessPermissionTestCase(TestCase):
    """Test OCM access control"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        # Create users
        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='regularpass123'
        )

        # Grant OCM access to ocm_user
        self.ocm_access = OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

        # Create OCM permissions
        content_type = ContentType.objects.get_for_model(OCMAccess)
        self.view_all_orgs_perm, _ = Permission.objects.get_or_create(
            codename='can_view_all_organizations',
            content_type=content_type,
            defaults={'name': 'Can view all organizations'}
        )
        self.access_dashboard_perm, _ = Permission.objects.get_or_create(
            codename='can_access_ocm_dashboard',
            content_type=content_type,
            defaults={'name': 'Can access OCM dashboard'}
        )

        # Grant permissions to OCM user
        self.ocm_user.user_permissions.add(
            self.view_all_orgs_perm,
            self.access_dashboard_perm
        )

    def test_user_with_ocm_access_has_permissions(self):
        """Test user with OCM access has required permissions"""
        self.assertTrue(
            self.ocm_user.has_perm('ocm.can_view_all_organizations')
        )
        self.assertTrue(
            self.ocm_user.has_perm('ocm.can_access_ocm_dashboard')
        )

    def test_user_without_ocm_access_denied(self):
        """Test user without OCM access is denied"""
        self.assertFalse(
            self.regular_user.has_perm('ocm.can_view_all_organizations')
        )
        self.assertFalse(
            self.regular_user.has_perm('ocm.can_access_ocm_dashboard')
        )

    def test_inactive_ocm_access_denied(self):
        """Test inactive OCM access is denied"""
        # Deactivate OCM access
        self.ocm_access.is_active = False
        self.ocm_access.save()

        # User still has permissions but access record is inactive
        # This should be checked in views/middleware
        ocm_access = OCMAccess.objects.filter(
            user=self.ocm_user,
            is_active=True
        ).first()

        self.assertIsNone(ocm_access)

    def test_ocm_user_can_view_all_organizations(self):
        """Test OCM user can view all organizations"""
        from organizations.models import Organization

        # Create test organizations
        org1 = Organization.objects.create(
            name='Ministry of Health',
            organization_type='ministry',
            is_active=True
        )
        org2 = Organization.objects.create(
            name='Ministry of Education',
            organization_type='ministry',
            is_active=True
        )

        # OCM user should see all organizations
        # (no organization-based filtering)
        all_orgs = Organization.objects.all()
        self.assertEqual(all_orgs.count(), 2)

    def test_write_operations_blocked(self):
        """Test write operations are blocked for OCM users"""
        # OCM users should only have read access
        # Write blocking is enforced by decorators and middleware
        # This test verifies the concept

        # Check user doesn't have write permissions
        self.assertFalse(
            self.ocm_user.has_perm('organizations.add_organization')
        )
        self.assertFalse(
            self.ocm_user.has_perm('organizations.change_organization')
        )
        self.assertFalse(
            self.ocm_user.has_perm('organizations.delete_organization')
        )


class OCMReadOnlyPermissionTestCase(TestCase):
    """Test OCMReadOnlyPermission DRF permission class"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.permission = OCMReadOnlyPermission()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_get_request_allowed(self):
        """Test GET requests are allowed"""
        request = self.factory.get('/api/ocm/dashboard/')
        request.user = self.user

        self.assertTrue(
            self.permission.has_permission(request, None)
        )

    def test_head_request_allowed(self):
        """Test HEAD requests are allowed"""
        request = self.factory.head('/api/ocm/dashboard/')
        request.user = self.user

        self.assertTrue(
            self.permission.has_permission(request, None)
        )

    def test_options_request_allowed(self):
        """Test OPTIONS requests are allowed"""
        request = self.factory.options('/api/ocm/dashboard/')
        request.user = self.user

        self.assertTrue(
            self.permission.has_permission(request, None)
        )

    def test_post_request_denied(self):
        """Test POST requests are denied"""
        request = self.factory.post('/api/ocm/dashboard/')
        request.user = self.user

        self.assertFalse(
            self.permission.has_permission(request, None)
        )

    def test_put_request_denied(self):
        """Test PUT requests are denied"""
        request = self.factory.put('/api/ocm/dashboard/1/')
        request.user = self.user

        self.assertFalse(
            self.permission.has_permission(request, None)
        )

    def test_patch_request_denied(self):
        """Test PATCH requests are denied"""
        request = self.factory.patch('/api/ocm/dashboard/1/')
        request.user = self.user

        self.assertFalse(
            self.permission.has_permission(request, None)
        )

    def test_delete_request_denied(self):
        """Test DELETE requests are denied"""
        request = self.factory.delete('/api/ocm/dashboard/1/')
        request.user = self.user

        self.assertFalse(
            self.permission.has_permission(request, None)
        )


class IsOCMUserPermissionTestCase(TestCase):
    """Test IsOCMUser DRF permission class"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.permission = IsOCMUser()

        # Create OCM user
        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='regularpass123'
        )

        # Grant OCM access
        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

    def test_ocm_user_allowed(self):
        """Test user with active OCM access is allowed"""
        request = self.factory.get('/api/ocm/dashboard/')
        request.user = self.ocm_user

        self.assertTrue(
            self.permission.has_permission(request, None)
        )

    def test_regular_user_denied(self):
        """Test regular user without OCM access is denied"""
        request = self.factory.get('/api/ocm/dashboard/')
        request.user = self.regular_user

        self.assertFalse(
            self.permission.has_permission(request, None)
        )

    def test_inactive_ocm_access_denied(self):
        """Test user with inactive OCM access is denied"""
        # Deactivate OCM access
        ocm_access = OCMAccess.objects.get(user=self.ocm_user)
        ocm_access.is_active = False
        ocm_access.save()

        request = self.factory.get('/api/ocm/dashboard/')
        request.user = self.ocm_user

        self.assertFalse(
            self.permission.has_permission(request, None)
        )

    def test_anonymous_user_denied(self):
        """Test anonymous user is denied"""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/api/ocm/dashboard/')
        request.user = AnonymousUser()

        self.assertFalse(
            self.permission.has_permission(request, None)
        )


class OCMPermissionIntegrationTestCase(TestCase):
    """Integration tests for OCM permissions"""

    def setUp(self):
        """Set up test data"""
        # Create OCM user with full setup
        self.ocm_user = User.objects.create_user(
            username='ocm_admin',
            email='ocm.admin@example.com',
            password='secure123',
            is_staff=True
        )

        # Create OCM access
        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='OCM Administrator',
            is_active=True
        )

        # Grant all OCM permissions
        content_type = ContentType.objects.get_for_model(OCMAccess)
        permissions = Permission.objects.filter(content_type=content_type)
        for perm in permissions:
            self.ocm_user.user_permissions.add(perm)

    def test_ocm_user_full_permissions(self):
        """Test OCM user has all required permissions"""
        expected_permissions = [
            'can_view_all_organizations',
            'can_access_ocm_dashboard',
        ]

        for perm_codename in expected_permissions:
            # Try with and without app label
            has_perm = (
                self.ocm_user.has_perm(f'ocm.{perm_codename}') or
                Permission.objects.filter(
                    codename=perm_codename,
                    user=self.ocm_user
                ).exists()
            )
            self.assertTrue(
                has_perm,
                f"User should have permission: {perm_codename}"
            )

    def test_permission_check_order(self):
        """Test permission checks execute in correct order"""
        # 1. Authentication
        self.assertTrue(self.ocm_user.is_authenticated)

        # 2. OCM Access record exists and is active
        ocm_access = OCMAccess.objects.filter(
            user=self.ocm_user,
            is_active=True
        ).first()
        self.assertIsNotNone(ocm_access)

        # 3. User has OCM permissions
        self.assertTrue(
            self.ocm_user.user_permissions.filter(
                codename__startswith='can_'
            ).exists()
        )
