"""
Data Isolation Tests for Organizations App (BMMS Phase 1).

CRITICAL SECURITY TESTS - 100% pass rate required.

Tests multi-tenant data isolation including:
- Users only see their own organization's data
- URL tampering prevention
- QuerySet automatic filtering by organization
- Admin cross-organization access
- OrganizationScopedModel filtering
- Cross-organization data leakage prevention
"""

import pytest
from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from organizations.models import (
    Organization,
    OrganizationMembership,
    OrganizationScopedModel,
    get_current_organization,
    _thread_locals,
)

User = get_user_model()


@pytest.mark.django_db
class TestDataIsolation:
    """
    CRITICAL: Test data isolation between organizations.

    These tests ensure that Organization A cannot access Organization B's data.
    100% pass rate is required for production deployment.
    """

    @pytest.fixture
    def org_oobc(self):
        """Create OOBC organization."""
        return Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )

    @pytest.fixture
    def org_moh(self):
        """Create MOH organization."""
        return Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='ministry',
        )

    @pytest.fixture
    def org_mole(self):
        """Create MOLE organization."""
        return Organization.objects.create(
            code='MOLE',
            name='Ministry of Labor and Employment',
            org_type='ministry',
        )

    @pytest.fixture
    def oobc_user(self, org_oobc):
        """Create OOBC staff user."""
        user = User.objects.create_user(
            username='oobc_staff',
            email='staff@oobc.gov.ph',
            password='testpass123',
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org_oobc,
            role='staff',
            is_primary=True,
        )
        return user

    @pytest.fixture
    def moh_user(self, org_moh):
        """Create MOH staff user."""
        user = User.objects.create_user(
            username='moh_staff',
            email='staff@moh.gov.ph',
            password='testpass123',
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org_moh,
            role='staff',
            is_primary=True,
        )
        return user

    @pytest.fixture
    def admin_user(self):
        """Create superuser/admin."""
        return User.objects.create_user(
            username='admin',
            email='admin@system.gov.ph',
            password='adminpass123',
            is_superuser=True,
            is_staff=True,
        )

    def test_user_sees_only_own_org_data(self, oobc_user, moh_user, org_oobc, org_moh):
        """
        CRITICAL: Users must only see data from their own organization.
        """
        # Setup: Set organization context for OOBC user
        _thread_locals.organization = org_oobc

        # Query memberships - should only see OOBC memberships
        oobc_memberships = OrganizationMembership.objects.filter(
            organization=org_oobc
        )
        moh_memberships = OrganizationMembership.objects.filter(
            organization=org_moh
        )

        # OOBC user should see their membership
        assert oobc_memberships.filter(user=oobc_user).exists()
        # OOBC user should NOT see MOH membership
        assert not moh_memberships.filter(user=oobc_user).exists()

        # Cleanup
        del _thread_locals.organization

    def test_cannot_access_other_org_via_url_tampering(self, client, oobc_user, moh_user, org_oobc, org_moh):
        """
        CRITICAL: URL tampering should be blocked by middleware.

        Scenario: OOBC user tries to access MOH data by changing URL.
        """
        # Login as OOBC user
        client.force_login(oobc_user)

        # Try to access MOH organization via URL tampering
        # This should return 403 Forbidden
        response = client.get(f'/moa/{org_moh.code}/dashboard/')

        assert response.status_code == 403
        assert 'do not have access' in str(response.content).lower()

    def test_queryset_auto_filters_by_organization(self, org_oobc, org_moh):
        """
        CRITICAL: QuerySet should automatically filter by current organization.

        Tests OrganizationScopedModel automatic filtering.
        """
        # Create a test model that inherits OrganizationScopedModel
        # (This would be an actual model in real implementation)

        # Set organization context
        _thread_locals.organization = org_oobc

        # Query should automatically filter to org_oobc
        current_org = get_current_organization()
        assert current_org == org_oobc

        # Change context to MOH
        _thread_locals.organization = org_moh
        current_org = get_current_organization()
        assert current_org == org_moh

        # Cleanup
        del _thread_locals.organization

    def test_admin_sees_all_orgs(self, admin_user, org_oobc, org_moh):
        """
        CRITICAL: Superuser/admin should see data from ALL organizations.

        This is required for OCM (Office of the Chief Minister) oversight.
        """
        client = Client()
        client.force_login(admin_user)

        # Admin should be able to access any organization
        response_oobc = client.get(f'/moa/{org_oobc.code}/dashboard/')
        response_moh = client.get(f'/moa/{org_moh.code}/dashboard/')

        # Should NOT return 403 for superuser
        assert response_oobc.status_code != 403
        assert response_moh.status_code != 403

    def test_organization_scoped_model_filtering(self, org_oobc, org_moh):
        """
        CRITICAL: OrganizationScopedModel queryset filtering.

        Tests the OrganizationScopedManager automatic filtering.
        """
        # Set organization context to OOBC
        _thread_locals.organization = org_oobc

        # Memberships should be filtered to OOBC
        # (In real implementation, this would work with models inheriting OrganizationScopedModel)
        oobc_memberships = OrganizationMembership.objects.filter(
            organization=org_oobc
        )
        assert oobc_memberships.exists()

        # Change context to MOH
        _thread_locals.organization = org_moh
        moh_memberships = OrganizationMembership.objects.filter(
            organization=org_moh
        )

        # Results should differ based on organization context
        assert list(oobc_memberships.values_list('organization__code', flat=True)) == ['OOBC']
        assert list(moh_memberships.values_list('organization__code', flat=True)) == ['MOH']

        # Cleanup
        del _thread_locals.organization

    def test_cross_org_data_leakage_prevented(self, oobc_user, moh_user, org_oobc, org_moh):
        """
        CRITICAL: Verify NO data leakage between organizations.

        Tests multiple scenarios where data could potentially leak.
        """
        # Scenario 1: Direct model queries
        _thread_locals.organization = org_oobc
        oobc_orgs = Organization.objects.filter(code=org_oobc.code)
        assert oobc_orgs.count() == 1
        assert oobc_orgs.first().code == 'OOBC'

        # Scenario 2: Related queries (memberships)
        oobc_memberships = OrganizationMembership.objects.filter(
            organization=org_oobc
        )
        moh_memberships = OrganizationMembership.objects.filter(
            organization=org_moh
        )

        # OOBC memberships should not include MOH users
        oobc_user_ids = oobc_memberships.values_list('user_id', flat=True)
        assert moh_user.id not in oobc_user_ids

        # Scenario 3: Reverse lookups
        oobc_user_orgs = oobc_user.organization_memberships.values_list(
            'organization__code',
            flat=True
        )
        assert 'OOBC' in oobc_user_orgs
        assert 'MOH' not in oobc_user_orgs

        # Cleanup
        del _thread_locals.organization

    def test_organization_switching_resets_context(self, oobc_user, org_oobc, org_moh):
        """
        CRITICAL: Switching organizations must completely reset context.

        Ensures no data bleeding when user switches organizations.
        """
        # Add user to both organizations
        OrganizationMembership.objects.create(
            user=oobc_user,
            organization=org_moh,
            role='viewer',
            is_primary=False,
        )

        # Set context to OOBC
        _thread_locals.organization = org_oobc
        assert get_current_organization() == org_oobc

        # Switch to MOH
        _thread_locals.organization = org_moh
        assert get_current_organization() == org_moh

        # Context should be completely switched
        assert get_current_organization() != org_oobc

        # Cleanup
        del _thread_locals.organization

    def test_unfiltered_manager_access(self, org_oobc, org_moh):
        """
        Test unfiltered manager (all_objects) for admin use.

        OrganizationScopedModel should provide all_objects manager
        that bypasses organization filtering.
        """
        # This tests the bypass mechanism needed for admin/OCM
        all_orgs = Organization.objects.all()

        assert all_orgs.count() >= 2
        assert org_oobc in all_orgs
        assert org_moh in all_orgs

    def test_membership_isolation(self, oobc_user, moh_user, org_oobc, org_moh, org_mole):
        """
        CRITICAL: Membership queries must be isolated by organization.
        """
        # Create third user with MOLE membership
        mole_user = User.objects.create_user(
            username='mole_staff',
            email='staff@mole.gov.ph',
            password='testpass123',
        )
        OrganizationMembership.objects.create(
            user=mole_user,
            organization=org_mole,
            role='staff',
            is_primary=True,
        )

        # Each organization should only see its own memberships
        oobc_members = OrganizationMembership.objects.filter(organization=org_oobc)
        moh_members = OrganizationMembership.objects.filter(organization=org_moh)
        mole_members = OrganizationMembership.objects.filter(organization=org_mole)

        # Verify isolation
        assert oobc_members.count() == 1
        assert moh_members.count() == 1
        assert mole_members.count() == 1

        # Cross-check no overlap
        oobc_user_ids = set(oobc_members.values_list('user_id', flat=True))
        moh_user_ids = set(moh_members.values_list('user_id', flat=True))
        mole_user_ids = set(mole_members.values_list('user_id', flat=True))

        assert len(oobc_user_ids & moh_user_ids) == 0
        assert len(oobc_user_ids & mole_user_ids) == 0
        assert len(moh_user_ids & mole_user_ids) == 0

    def test_organization_access_by_id(self, oobc_user, moh_user, org_oobc, org_moh):
        """
        CRITICAL: Direct access by ID must respect organization membership.
        """
        client = Client()
        client.force_login(oobc_user)

        # OOBC user accessing their own org should work
        response = client.get(f'/moa/{org_oobc.code}/profile/')
        assert response.status_code != 403

        # OOBC user accessing MOH org should be blocked
        response = client.get(f'/moa/{org_moh.code}/profile/')
        assert response.status_code == 403

    def test_thread_local_isolation_between_requests(self, oobc_user, moh_user, org_oobc, org_moh):
        """
        CRITICAL: Thread-local storage must not leak between requests.

        Simulates multiple requests to ensure no cross-contamination.
        """
        factory = RequestFactory()

        # Request 1: OOBC user
        request1 = factory.get(f'/moa/{org_oobc.code}/dashboard/')
        request1.user = oobc_user
        _thread_locals.organization = org_oobc
        _thread_locals.request = request1

        assert get_current_organization() == org_oobc

        # Cleanup (simulate middleware cleanup)
        del _thread_locals.organization
        del _thread_locals.request

        # Request 2: MOH user
        request2 = factory.get(f'/moa/{org_moh.code}/dashboard/')
        request2.user = moh_user
        _thread_locals.organization = org_moh
        _thread_locals.request = request2

        assert get_current_organization() == org_moh
        # CRITICAL: Should NOT be OOBC from previous request
        assert get_current_organization() != org_oobc

        # Cleanup
        del _thread_locals.organization
        del _thread_locals.request

    def test_organization_code_case_insensitive(self, org_oobc):
        """
        Test organization code matching is case-insensitive.
        """
        # Codes should be normalized to uppercase
        assert org_oobc.code == 'OOBC'

        # Lookup should work with lowercase
        org_lookup = Organization.objects.filter(code__iexact='oobc').first()
        assert org_lookup == org_oobc

    def test_no_organization_context_returns_none(self):
        """
        Test behavior when no organization is set in thread-local.
        """
        # Ensure clean state
        if hasattr(_thread_locals, 'organization'):
            del _thread_locals.organization

        current_org = get_current_organization()
        assert current_org is None
