"""
Tests for OCM models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

from ocm.models import OCMAccess

User = get_user_model()


class OCMAccessModelTestCase(TestCase):
    """Test cases for OCMAccess model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='testpass123'
        )
        self.ocm_access = OCMAccess.objects.create(
            user=self.user,
            granted_by=self.user,
            reason='Testing OCM access',
            is_active=True
        )

    def test_ocm_access_creation(self):
        """Test OCMAccess model creation"""
        self.assertIsNotNone(self.ocm_access.id)
        self.assertEqual(self.ocm_access.user, self.user)
        self.assertEqual(self.ocm_access.granted_by, self.user)
        self.assertTrue(self.ocm_access.is_active)
        self.assertIsNotNone(self.ocm_access.granted_at)
        self.assertIsNone(self.ocm_access.revoked_at)
        self.assertIsNone(self.ocm_access.last_accessed)

    def test_ocm_access_str_method(self):
        """Test __str__ method"""
        expected = f"OCM Access - {self.user.username}"
        self.assertEqual(str(self.ocm_access), expected)

    def test_update_last_accessed_method(self):
        """Test update_last_accessed() method"""
        # Initially last_accessed is None
        self.assertIsNone(self.ocm_access.last_accessed)

        # Call update_last_accessed
        self.ocm_access.update_last_accessed()

        # Verify last_accessed is set
        self.assertIsNotNone(self.ocm_access.last_accessed)

        # Store the timestamp
        first_access = self.ocm_access.last_accessed

        # Wait a moment and update again
        import time
        time.sleep(0.1)
        self.ocm_access.update_last_accessed()

        # Verify timestamp changed
        self.assertGreater(self.ocm_access.last_accessed, first_access)

    def test_ocm_access_inactive(self):
        """Test inactive OCMAccess"""
        inactive_access = OCMAccess.objects.create(
            user=self.user,
            granted_by=self.user,
            reason='Inactive test',
            is_active=False,
            revoked_at=timezone.now()
        )

        self.assertFalse(inactive_access.is_active)
        self.assertIsNotNone(inactive_access.revoked_at)

    def test_multiple_users_with_ocm_access(self):
        """Test multiple users can have OCM access"""
        user2 = User.objects.create_user(
            username='ocm_user2',
            email='ocm2@example.com',
            password='testpass123'
        )

        ocm_access2 = OCMAccess.objects.create(
            user=user2,
            granted_by=self.user,
            reason='Second user access'
        )

        self.assertEqual(OCMAccess.objects.count(), 2)
        self.assertEqual(OCMAccess.objects.filter(is_active=True).count(), 2)

    def test_ocm_access_granted_by_field(self):
        """Test granted_by field tracks who granted access"""
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )

        access = OCMAccess.objects.create(
            user=self.user,
            granted_by=admin_user,
            reason='Granted by admin'
        )

        self.assertEqual(access.granted_by, admin_user)

    def test_ocm_access_reason_field(self):
        """Test reason field stores explanation"""
        reason = "Access granted for fiscal year budget review"
        access = OCMAccess.objects.create(
            user=self.user,
            granted_by=self.user,
            reason=reason
        )

        self.assertEqual(access.reason, reason)


class OCMPermissionsTestCase(TestCase):
    """Test OCM permissions registration"""

    def test_ocm_permissions_exist(self):
        """Test OCM custom permissions are registered"""
        # Get OCMAccess content type
        content_type = ContentType.objects.get_for_model(OCMAccess)

        # Check for expected permissions
        expected_permissions = [
            'can_view_all_organizations',
            'can_access_ocm_dashboard',
        ]

        for perm_codename in expected_permissions:
            permission_exists = Permission.objects.filter(
                codename=perm_codename,
                content_type=content_type
            ).exists()

            # Note: Permissions are created via migrations
            # This test verifies they exist after migration
            self.assertTrue(
                permission_exists or Permission.objects.filter(
                    codename=perm_codename
                ).exists(),
                f"Permission '{perm_codename}' should exist"
            )

    def test_user_can_be_granted_ocm_permissions(self):
        """Test user can receive OCM permissions"""
        user = User.objects.create_user(
            username='ocm_test',
            email='test@example.com',
            password='test123'
        )

        # Try to create or get permission
        content_type = ContentType.objects.get_for_model(OCMAccess)
        permission, created = Permission.objects.get_or_create(
            codename='can_view_all_organizations',
            content_type=content_type,
            defaults={'name': 'Can view all organizations'}
        )

        # Grant permission to user
        user.user_permissions.add(permission)

        # Verify user has permission
        self.assertTrue(
            user.has_perm(f'{content_type.app_label}.can_view_all_organizations')
        )


class OCMAccessQuerySetTestCase(TestCase):
    """Test OCMAccess model queries"""

    def setUp(self):
        """Create test users and access records"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )

        # Active access
        OCMAccess.objects.create(
            user=self.user1,
            granted_by=self.user1,
            reason='Active access'
        )

        # Inactive access
        OCMAccess.objects.create(
            user=self.user2,
            granted_by=self.user1,
            reason='Revoked access',
            is_active=False,
            revoked_at=timezone.now()
        )

    def test_filter_active_access(self):
        """Test filtering active OCM access"""
        active_access = OCMAccess.objects.filter(is_active=True)
        self.assertEqual(active_access.count(), 1)
        self.assertEqual(active_access.first().user, self.user1)

    def test_filter_inactive_access(self):
        """Test filtering inactive OCM access"""
        inactive_access = OCMAccess.objects.filter(is_active=False)
        self.assertEqual(inactive_access.count(), 1)
        self.assertEqual(inactive_access.first().user, self.user2)

    def test_filter_by_user(self):
        """Test filtering OCM access by user"""
        user1_access = OCMAccess.objects.filter(user=self.user1)
        self.assertEqual(user1_access.count(), 1)
        self.assertTrue(user1_access.first().is_active)

    def test_filter_recently_accessed(self):
        """Test filtering recently accessed records"""
        # Update last_accessed for user1
        access = OCMAccess.objects.get(user=self.user1)
        access.update_last_accessed()

        # Query records accessed in last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent = OCMAccess.objects.filter(
            last_accessed__gte=one_hour_ago
        )

        self.assertEqual(recent.count(), 1)
        self.assertEqual(recent.first().user, self.user1)
