"""
Model Tests for Organizations App (BMMS Phase 1).

Tests Organization and OrganizationMembership models including:
- Model creation and validation
- Unique constraints
- String representations
- Default values
- Relationships and foreign keys
"""

import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone

from organizations.models import Organization, OrganizationMembership

User = get_user_model()


@pytest.mark.django_db
class TestOrganizationModel:
    """Test Organization model."""

    def test_create_organization_success(self):
        """Test successful organization creation with all required fields."""
        org = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
            is_active=True,
        )

        assert org.code == 'OOBC'
        assert org.name == 'Office for Other Bangsamoro Communities'
        assert org.org_type == 'office'
        assert org.is_active is True
        assert org.id is not None
        assert org.created_at is not None
        assert org.updated_at is not None

    def test_organization_code_unique(self):
        """Test that organization code must be unique."""
        Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )

        # Attempting to create duplicate code should fail
        with pytest.raises(IntegrityError):
            Organization.objects.create(
                code='OOBC',
                name='Duplicate Organization',
                org_type='office',
            )

    def test_organization_str_method(self):
        """Test Organization __str__ method."""
        org = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='ministry',
        )

        expected_str = 'MOH - Ministry of Health'
        assert str(org) == expected_str

    def test_module_flags_defaults(self):
        """Test that module activation flags default to True."""
        org = Organization.objects.create(
            code='MAFAR',
            name='Ministry of Agriculture, Fisheries and Agrarian Reform',
            org_type='ministry',
        )

        # All module flags should default to True
        assert org.enable_mana is True
        assert org.enable_planning is True
        assert org.enable_budgeting is True
        assert org.enable_me is True
        assert org.enable_coordination is True
        assert org.enable_policies is True

    def test_organization_optional_fields(self):
        """Test organization with optional fields populated."""
        org = Organization.objects.create(
            code='MOLE',
            name='Ministry of Labor and Employment',
            acronym='MOLE',
            org_type='ministry',
            mandate='To promote employment and ensure worker welfare',
            email='info@mole.gov.ph',
            phone='+63-2-8527-3000',
            website='https://mole.gov.ph',
            address='Cotabato City, BARMM',
            head_official='Minister John Doe',
            head_title='Minister',
            is_pilot=True,
        )

        assert org.acronym == 'MOLE'
        assert org.mandate == 'To promote employment and ensure worker welfare'
        assert org.email == 'info@mole.gov.ph'
        assert org.phone == '+63-2-8527-3000'
        assert org.website == 'https://mole.gov.ph'
        assert org.address == 'Cotabato City, BARMM'
        assert org.head_official == 'Minister John Doe'
        assert org.head_title == 'Minister'
        assert org.is_pilot is True

    def test_organization_org_type_choices(self):
        """Test various organization type choices."""
        org_types = [
            ('ministry', 'Ministry'),
            ('office', 'Office'),
            ('agency', 'Agency'),
            ('special', 'Special Body'),
            ('commission', 'Commission'),
        ]

        for code_suffix, (org_type, org_name) in enumerate(org_types, start=1):
            org = Organization.objects.create(
                code=f'TEST{code_suffix}',
                name=f'Test {org_name}',
                org_type=org_type,
            )
            assert org.org_type == org_type


@pytest.mark.django_db
class TestOrganizationMembershipModel:
    """Test OrganizationMembership model."""

    @pytest.fixture
    def organization(self):
        """Create test organization."""
        return Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )

    @pytest.fixture
    def user(self):
        """Create test user."""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

    def test_create_membership_success(self, user, organization):
        """Test successful membership creation."""
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
            is_primary=True,
        )

        assert membership.user == user
        assert membership.organization == organization
        assert membership.role == 'staff'
        assert membership.is_primary is True
        assert membership.is_active is True
        assert membership.joined_date is not None

    def test_user_org_unique_constraint(self, user, organization):
        """Test that user-organization combination must be unique."""
        OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
        )

        # Attempting to create duplicate membership should fail
        with pytest.raises(IntegrityError):
            OrganizationMembership.objects.create(
                user=user,
                organization=organization,
                role='admin',
            )

    def test_primary_membership_behavior(self, user, organization):
        """Test primary membership flag behavior."""
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
            is_primary=True,
        )

        assert membership.is_primary is True

        # User should be able to query their primary organization
        primary_membership = OrganizationMembership.objects.filter(
            user=user,
            is_primary=True
        ).first()

        assert primary_membership == membership
        assert primary_membership.organization == organization

    def test_multiple_memberships_per_user(self, user):
        """Test that a user can belong to multiple organizations."""
        org1 = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='ministry',
        )
        org2 = Organization.objects.create(
            code='MOLE',
            name='Ministry of Labor and Employment',
            org_type='ministry',
        )

        membership1 = OrganizationMembership.objects.create(
            user=user,
            organization=org1,
            role='staff',
            is_primary=True,
        )
        membership2 = OrganizationMembership.objects.create(
            user=user,
            organization=org2,
            role='viewer',
            is_primary=False,
        )

        # User should have 2 memberships
        assert user.organization_memberships.count() == 2
        assert membership1 in user.organization_memberships.all()
        assert membership2 in user.organization_memberships.all()

    def test_membership_str_method(self, user, organization):
        """Test OrganizationMembership __str__ method."""
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='admin',
        )

        expected_str = f'{user.username} @ {organization.code} (admin)'
        assert str(membership) == expected_str

    def test_membership_role_choices(self, user, organization):
        """Test various role choices for membership."""
        roles = ['admin', 'manager', 'staff', 'viewer']

        for role in roles:
            # Create new org for each membership to avoid unique constraint
            org = Organization.objects.create(
                code=f'TEST_{role.upper()}',
                name=f'Test Organization for {role}',
                org_type='office',
            )
            membership = OrganizationMembership.objects.create(
                user=user,
                organization=org,
                role=role,
            )
            assert membership.role == role

    def test_membership_permissions_fields(self, user, organization):
        """Test permission fields in membership."""
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='admin',
            can_manage_users=True,
            can_approve_plans=True,
            can_approve_budgets=True,
            can_view_reports=True,
        )

        assert membership.can_manage_users is True
        assert membership.can_approve_plans is True
        assert membership.can_approve_budgets is True
        assert membership.can_view_reports is True

    def test_membership_optional_fields(self, user, organization):
        """Test optional fields in membership."""
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
            position='Senior Officer',
            department='Planning Division',
        )

        assert membership.position == 'Senior Officer'
        assert membership.department == 'Planning Division'
