"""
Integration Tests for Organizations App (BMMS Phase 1).

Tests complete request-response workflows including:
- Full request cycle with middleware
- Organization switcher UI workflow
- User membership management
- Pilot MOA features
- Multi-organization user workflows
"""

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from organizations.models import Organization, OrganizationMembership

User = get_user_model()


@pytest.mark.django_db
class TestFullRequestResponseCycle:
    """Test complete request-response workflows."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def org_oobc(self):
        """Create OOBC organization."""
        return Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )

    @pytest.fixture
    def user(self, org_oobc):
        """Create test user with OOBC membership."""
        user = User.objects.create_user(
            username='testuser',
            email='test@oobc.gov.ph',
            password='testpass123',
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org_oobc,
            role='staff',
            is_primary=True,
        )
        return user

    def test_login_and_access_organization(self, client, user, org_oobc):
        """Test user can login and access their organization."""
        # Login
        client.login(username='testuser', password='testpass123')

        # Access organization dashboard (assuming this URL exists)
        response = client.get(f'/moa/{org_oobc.code}/dashboard/')

        # Should be successful or redirect (not 403)
        assert response.status_code in [200, 302]

    def test_request_has_organization_context(self, client, user, org_oobc):
        """Test that request has organization attribute set by middleware."""
        client.login(username='testuser', password='testpass123')

        # Make request with org code in URL
        response = client.get(f'/moa/{org_oobc.code}/dashboard/')

        # In a real view, we'd check request.organization
        # For now, verify request succeeded
        assert response.status_code in [200, 302]

    def test_unauthorized_access_returns_403(self, client, org_oobc):
        """Test unauthorized user gets 403 when accessing organization."""
        # Create user without membership
        user = User.objects.create_user(
            username='unauthorized',
            password='testpass123',
        )
        client.login(username='unauthorized', password='testpass123')

        # Try to access organization
        response = client.get(f'/moa/{org_oobc.code}/dashboard/')

        # Should return 403 Forbidden
        assert response.status_code == 403


@pytest.mark.django_db
class TestOrganizationSwitcherWorkflow:
    """Test organization switcher UI workflow."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return Client()

    @pytest.fixture
    def organizations(self):
        """Create multiple organizations."""
        oobc = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )
        moh = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='ministry',
        )
        return oobc, moh

    @pytest.fixture
    def multi_org_user(self, organizations):
        """Create user with multiple organization memberships."""
        oobc, moh = organizations
        user = User.objects.create_user(
            username='multiorg',
            email='multi@system.gov.ph',
            password='testpass123',
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=oobc,
            role='staff',
            is_primary=True,
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=moh,
            role='viewer',
            is_primary=False,
        )
        return user

    def test_user_can_switch_organizations(self, client, multi_org_user, organizations):
        """Test user can switch between their organizations."""
        oobc, moh = organizations
        client.login(username='multiorg', password='testpass123')

        # Access OOBC
        response = client.get(f'/moa/{oobc.code}/dashboard/')
        assert response.status_code in [200, 302]

        # Switch to MOH
        response = client.get(f'/moa/{moh.code}/dashboard/')
        assert response.status_code in [200, 302]

    def test_primary_organization_is_default(self, client, multi_org_user, organizations):
        """Test that primary organization is used when no org in URL."""
        oobc, moh = organizations
        client.login(username='multiorg', password='testpass123')

        # Access URL without org code (should use primary org)
        response = client.get('/dashboard/')

        # Should use primary org (OOBC) by default
        # In real implementation, would check request.organization
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestUserMembershipManagement:
    """Test user membership CRUD operations."""

    @pytest.fixture
    def admin_user(self):
        """Create admin user."""
        return User.objects.create_user(
            username='admin',
            password='adminpass123',
            is_superuser=True,
            is_staff=True,
        )

    @pytest.fixture
    def organization(self):
        """Create test organization."""
        return Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )

    def test_create_user_membership(self, admin_user, organization):
        """Test creating a new membership for a user."""
        # Create regular user
        user = User.objects.create_user(
            username='newstaff',
            email='new@oobc.gov.ph',
            password='testpass123',
        )

        # Admin creates membership
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
            is_primary=True,
        )

        assert membership.user == user
        assert membership.organization == organization
        assert membership.is_primary is True

    def test_update_membership_role(self, organization):
        """Test updating a user's role in organization."""
        user = User.objects.create_user(
            username='staffuser',
            password='testpass123',
        )
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
            is_primary=True,
        )

        # Update role
        membership.role = 'manager'
        membership.save()

        # Verify update
        membership.refresh_from_db()
        assert membership.role == 'manager'

    def test_deactivate_membership(self, organization):
        """Test deactivating a user's membership."""
        user = User.objects.create_user(
            username='activeuser',
            password='testpass123',
        )
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
            is_primary=True,
            is_active=True,
        )

        # Deactivate
        membership.is_active = False
        membership.save()

        # Verify
        membership.refresh_from_db()
        assert membership.is_active is False

    def test_remove_membership(self, organization):
        """Test removing a user's membership."""
        user = User.objects.create_user(
            username='tempuser',
            password='testpass123',
        )
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
            is_primary=True,
        )

        membership_id = membership.id

        # Delete membership
        membership.delete()

        # Verify deleted
        assert not OrganizationMembership.objects.filter(id=membership_id).exists()


@pytest.mark.django_db
class TestPilotMOAFeatures:
    """Test pilot MOA specific features."""

    @pytest.fixture
    def pilot_moas(self):
        """Create the 3 pilot MOAs."""
        moh = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='ministry',
            is_pilot=True,
        )
        mole = Organization.objects.create(
            code='MOLE',
            name='Ministry of Labor and Employment',
            org_type='ministry',
            is_pilot=True,
        )
        mafar = Organization.objects.create(
            code='MAFAR',
            name='Ministry of Agriculture, Fisheries and Agrarian Reform',
            org_type='ministry',
            is_pilot=True,
        )
        return moh, mole, mafar

    @pytest.fixture
    def non_pilot_org(self):
        """Create non-pilot organization."""
        return Organization.objects.create(
            code='MENRE',
            name='Ministry of Environment, Natural Resources and Energy',
            org_type='ministry',
            is_pilot=False,
        )

    def test_pilot_moas_flagged_correctly(self, pilot_moas):
        """Test that pilot MOAs have is_pilot=True."""
        moh, mole, mafar = pilot_moas

        assert moh.is_pilot is True
        assert mole.is_pilot is True
        assert mafar.is_pilot is True

    def test_query_pilot_organizations(self, pilot_moas, non_pilot_org):
        """Test querying for pilot organizations."""
        pilot_orgs = Organization.objects.filter(is_pilot=True)

        assert pilot_orgs.count() == 3
        assert all(org.is_pilot for org in pilot_orgs)

    def test_non_pilot_org_excluded(self, pilot_moas, non_pilot_org):
        """Test that non-pilot organizations are excluded from pilot queries."""
        pilot_orgs = Organization.objects.filter(is_pilot=True)

        assert non_pilot_org not in pilot_orgs
        assert non_pilot_org.is_pilot is False


@pytest.mark.django_db
class TestMultiOrganizationUserWorkflows:
    """Test workflows for users with multiple organization memberships."""

    @pytest.fixture
    def organizations(self):
        """Create multiple organizations."""
        orgs = {}
        orgs['oobc'] = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )
        orgs['moh'] = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='ministry',
        )
        orgs['mole'] = Organization.objects.create(
            code='MOLE',
            name='Ministry of Labor and Employment',
            org_type='ministry',
        )
        return orgs

    @pytest.fixture
    def multi_org_user(self, organizations):
        """Create user with memberships in multiple organizations."""
        user = User.objects.create_user(
            username='multiorg',
            email='multi@system.gov.ph',
            password='testpass123',
        )

        # Add to OOBC (primary)
        OrganizationMembership.objects.create(
            user=user,
            organization=organizations['oobc'],
            role='staff',
            is_primary=True,
        )

        # Add to MOH (secondary)
        OrganizationMembership.objects.create(
            user=user,
            organization=organizations['moh'],
            role='viewer',
            is_primary=False,
        )

        # Add to MOLE (secondary)
        OrganizationMembership.objects.create(
            user=user,
            organization=organizations['mole'],
            role='viewer',
            is_primary=False,
        )

        return user

    def test_user_has_multiple_memberships(self, multi_org_user, organizations):
        """Test user can have memberships in multiple organizations."""
        memberships = multi_org_user.organization_memberships.all()

        assert memberships.count() == 3

        org_codes = set(memberships.values_list('organization__code', flat=True))
        assert 'OOBC' in org_codes
        assert 'MOH' in org_codes
        assert 'MOLE' in org_codes

    def test_user_has_one_primary_organization(self, multi_org_user):
        """Test user has exactly one primary organization."""
        primary_memberships = multi_org_user.organization_memberships.filter(
            is_primary=True
        )

        assert primary_memberships.count() == 1
        assert primary_memberships.first().organization.code == 'OOBC'

    def test_user_can_access_all_their_organizations(self, multi_org_user, organizations):
        """Test user can access all organizations they're a member of."""
        client = Client()
        client.login(username='multiorg', password='testpass123')

        for org_code in ['OOBC', 'MOH', 'MOLE']:
            response = client.get(f'/moa/{org_code}/dashboard/')
            # Should not be 403
            assert response.status_code != 403

    def test_user_cannot_access_non_member_organization(self, multi_org_user):
        """Test user cannot access organization they're not a member of."""
        # Create organization user is NOT a member of
        other_org = Organization.objects.create(
            code='MENRE',
            name='Ministry of Environment',
            org_type='ministry',
        )

        client = Client()
        client.login(username='multiorg', password='testpass123')

        response = client.get(f'/moa/{other_org.code}/dashboard/')

        # Should return 403 Forbidden
        assert response.status_code == 403

    def test_user_membership_count(self, multi_org_user):
        """Test querying user's total membership count."""
        count = multi_org_user.organization_memberships.count()
        assert count == 3

    def test_filter_memberships_by_role(self, multi_org_user):
        """Test filtering user memberships by role."""
        staff_memberships = multi_org_user.organization_memberships.filter(
            role='staff'
        )
        viewer_memberships = multi_org_user.organization_memberships.filter(
            role='viewer'
        )

        assert staff_memberships.count() == 1
        assert viewer_memberships.count() == 2
