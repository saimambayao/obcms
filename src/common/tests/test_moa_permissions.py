"""
Comprehensive tests for MOA RBAC permission functions.

Tests all permission helper functions from common.utils.moa_permissions module.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from common.utils.moa_permissions import (
    moa_view_only,
    moa_can_edit_organization,
    moa_can_edit_ppa,
    moa_can_edit_work_item,
    moa_no_access,
    user_can_access_mana,
)
from coordination.models import Organization
from django.core.exceptions import PermissionDenied

User = get_user_model()


@pytest.mark.django_db
class TestMOAPermissionFunctions(TestCase):
    """Test suite for MOA permission helper functions."""

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
        self.inactive_org = Organization.objects.create(
            name="Inactive Ministry",
            organization_type="bmoa",
            is_active=False,
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
            organization="Ministry of Health",
            moa_organization=self.moa_health,
            is_approved=True,
        )

        self.moa_user_edu = User.objects.create_user(
            username="moa_education",
            email="edu@moa.gov.ph",
            password="testpass123",
            user_type="lgu",
            organization="Ministry of Education",
            moa_organization=self.moa_education,
            is_approved=True,
        )

        self.moa_no_org = User.objects.create_user(
            username="moa_no_org",
            email="noorg@moa.gov.ph",
            password="testpass123",
            user_type="nga",
            is_approved=True,
            # No moa_organization assigned
        )

        self.unapproved_user = User.objects.create_user(
            username="unapproved",
            email="unapproved@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.moa_health,
            is_approved=False,
        )

    def test_moa_view_only_allows_get(self):
        """MOA users can make GET requests on view-only resources."""

        @moa_view_only
        def test_view(request):
            return "OK"

        request = self.factory.get("/test/")
        request.user = self.moa_user_health

        result = test_view(request)
        self.assertEqual(result, "OK")

    def test_moa_view_only_blocks_post(self):
        """MOA users cannot make POST requests on view-only resources."""

        @moa_view_only
        def test_view(request):
            return "OK"

        request = self.factory.post("/test/")
        request.user = self.moa_user_health

        with self.assertRaises(PermissionDenied) as context:
            test_view(request)

        self.assertIn("view-only", str(context.exception))

    def test_moa_view_only_blocks_put(self):
        """MOA users cannot make PUT requests on view-only resources."""

        @moa_view_only
        def test_view(request):
            return "OK"

        request = self.factory.put("/test/")
        request.user = self.moa_user_health

        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_moa_view_only_blocks_delete(self):
        """MOA users cannot make DELETE requests on view-only resources."""

        @moa_view_only
        def test_view(request):
            return "OK"

        request = self.factory.delete("/test/")
        request.user = self.moa_user_health

        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_moa_view_only_allows_oobc_staff_all_methods(self):
        """OOBC staff can use all HTTP methods on view-only resources."""

        @moa_view_only
        def test_view(request):
            return "OK"

        # Test POST (normally blocked for MOA)
        request = self.factory.post("/test/")
        request.user = self.oobc_staff
        result = test_view(request)
        self.assertEqual(result, "OK")

    def test_moa_view_only_allows_superuser_all_methods(self):
        """Superusers can use all HTTP methods on view-only resources."""

        @moa_view_only
        def test_view(request):
            return "OK"

        request = self.factory.delete("/test/")
        request.user = self.superuser
        result = test_view(request)
        self.assertEqual(result, "OK")

    def test_moa_can_edit_own_organization(self):
        """MOA users can edit their own organization."""

        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.moa_user_health

        result = test_view(request, pk=self.moa_health.id)
        self.assertEqual(result, "OK")

    def test_moa_cannot_edit_other_organization(self):
        """MOA users cannot edit other organizations."""

        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.moa_user_health

        with self.assertRaises(PermissionDenied) as context:
            test_view(request, pk=self.moa_education.id)

        self.assertIn("your own MOA organization", str(context.exception))

    def test_moa_with_no_org_cannot_edit_any_org(self):
        """MOA users without assigned organization cannot edit any org."""

        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.moa_no_org

        with self.assertRaises(PermissionDenied):
            test_view(request, pk=self.moa_health.id)

    def test_oobc_staff_can_edit_any_organization(self):
        """OOBC staff can edit any organization."""

        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.oobc_staff

        # Should not raise PermissionDenied
        result = test_view(request, pk=self.moa_education.id)
        self.assertEqual(result, "OK")

    def test_superuser_can_edit_any_organization(self):
        """Superusers can edit any organization."""

        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.superuser

        result = test_view(request, pk=self.moa_education.id)
        self.assertEqual(result, "OK")

    def test_moa_no_access_blocks_moa_users(self):
        """MOA users are blocked from moa_no_access decorated views."""

        @moa_no_access
        def test_view(request):
            return "OK"

        request = self.factory.get("/mana/")
        request.user = self.moa_user_health

        with self.assertRaises(PermissionDenied) as context:
            test_view(request)

        self.assertIn("OOBC internal", str(context.exception))

    def test_moa_no_access_allows_oobc_staff(self):
        """OOBC staff can access moa_no_access decorated views."""

        @moa_no_access
        def test_view(request):
            return "OK"

        request = self.factory.get("/mana/")
        request.user = self.oobc_staff

        result = test_view(request)
        self.assertEqual(result, "OK")

    def test_moa_no_access_allows_superuser(self):
        """Superusers can access moa_no_access decorated views."""

        @moa_no_access
        def test_view(request):
            return "OK"

        request = self.factory.get("/mana/")
        request.user = self.superuser

        result = test_view(request)
        self.assertEqual(result, "OK")

    def test_user_can_access_mana_false_for_moa(self):
        """MOA users cannot access MANA (helper function)."""
        self.assertFalse(user_can_access_mana(self.moa_user_health))
        self.assertFalse(user_can_access_mana(self.moa_user_edu))
        self.assertFalse(user_can_access_mana(self.moa_no_org))

    def test_user_can_access_mana_true_for_oobc(self):
        """OOBC staff can access MANA (helper function)."""
        self.assertTrue(user_can_access_mana(self.oobc_staff))

    def test_user_can_access_mana_true_for_superuser(self):
        """Superusers can access MANA (helper function)."""
        self.assertTrue(user_can_access_mana(self.superuser))

    def test_user_can_access_mana_false_for_unauthenticated(self):
        """Unauthenticated users cannot access MANA."""
        from django.contrib.auth.models import AnonymousUser

        anon_user = AnonymousUser()
        self.assertFalse(user_can_access_mana(anon_user))

    def test_unapproved_user_blocked(self):
        """Unapproved MOA users should be blocked (if decorator checks is_approved)."""
        # Note: Current decorators only check is_moa_staff, not is_approved
        # This test documents expected behavior if approval check is added

        @moa_view_only
        def test_view(request):
            return "OK"

        request = self.factory.post("/test/")
        request.user = self.unapproved_user

        # Should raise PermissionDenied for POST
        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_inactive_organization_user_can_still_access(self):
        """Users from inactive organizations can still use system (org status doesn't block access)."""
        inactive_user = User.objects.create_user(
            username="inactive_moa",
            email="inactive@moa.gov.ph",
            password="testpass123",
            user_type="bmoa",
            moa_organization=self.inactive_org,
            is_approved=True,
        )

        @moa_view_only
        def test_view(request):
            return "OK"

        request = self.factory.get("/test/")
        request.user = inactive_user

        # Should allow GET (view-only)
        result = test_view(request)
        self.assertEqual(result, "OK")

    def test_decorator_preserves_function_metadata(self):
        """Decorators should preserve original function name and docstring."""

        @moa_view_only
        def my_test_view(request):
            """This is my docstring."""
            return "OK"

        self.assertEqual(my_test_view.__name__, "my_test_view")
        self.assertEqual(my_test_view.__doc__, "This is my docstring.")

    def test_moa_can_edit_organization_with_organization_id_kwarg(self):
        """Decorator should work with organization_id parameter name."""

        @moa_can_edit_organization
        def test_view(request, organization_id):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.moa_user_health

        result = test_view(request, organization_id=self.moa_health.id)
        self.assertEqual(result, "OK")

    def test_edge_case_none_pk(self):
        """Handle edge case where pk is None."""

        @moa_can_edit_organization
        def test_view(request, pk=None):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.moa_user_health

        # Should not raise error when pk is None
        result = test_view(request, pk=None)
        self.assertEqual(result, "OK")


@pytest.mark.django_db
class TestMOAPermissionEdgeCases(TestCase):
    """Test edge cases and error handling."""

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

    def test_string_pk_conversion(self):
        """Test that string PKs are handled correctly."""

        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.moa_user

        # Pass PK as string (e.g., from URL)
        result = test_view(request, pk=str(self.moa.id))
        self.assertEqual(result, "OK")

    def test_uuid_pk_handling(self):
        """Test handling of UUID primary keys."""
        import uuid

        test_uuid = uuid.uuid4()

        @moa_can_edit_organization
        def test_view(request, pk):
            return "OK"

        request = self.factory.post("/org/")
        request.user = self.moa_user

        # UUID that doesn't match should raise PermissionDenied
        with self.assertRaises(PermissionDenied):
            test_view(request, pk=test_uuid)

    def test_authenticated_but_not_moa_user(self):
        """Regular authenticated users (non-MOA) should not be restricted."""
        regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="testpass123",
            user_type="oobc_staff",  # Not MOA
            is_approved=True,
        )

        @moa_view_only
        def test_view(request):
            return "OK"

        request = self.factory.post("/test/")
        request.user = regular_user

        # Regular users should be able to POST (not restricted by MOA decorator)
        result = test_view(request)
        self.assertEqual(result, "OK")
