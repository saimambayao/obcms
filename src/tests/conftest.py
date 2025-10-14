"""
Pytest configuration for OBCMS/BMMS dual-mode testing.

This module provides fixtures for testing the BMMS embedded architecture,
including organization scoping, data isolation, and dual-mode testing.
"""
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from obc_management.settings.bmms_config import BMMSMode
from organizations.models import Organization, OrganizationMembership
from organizations.utils import get_or_create_default_organization

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup database for tests."""
    with django_db_blocker.unblock():
        # Ensure default OOBC organization exists
        get_or_create_default_organization()


@pytest.fixture
def obcms_mode(settings):
    """Force OBCMS mode for this test."""
    settings.BMMS_MODE = BMMSMode.OBCMS
    settings.RBAC_SETTINGS['ENABLE_MULTI_TENANT'] = False
    settings.RBAC_SETTINGS['ALLOW_ORGANIZATION_SWITCHING'] = False
    return settings


@pytest.fixture
def bmms_mode(settings):
    """Force BMMS mode for this test."""
    settings.BMMS_MODE = BMMSMode.BMMS
    settings.RBAC_SETTINGS['ENABLE_MULTI_TENANT'] = True
    settings.RBAC_SETTINGS['ALLOW_ORGANIZATION_SWITCHING'] = True
    return settings


@pytest.fixture
def default_organization(db):
    """Get default OOBC organization."""
    org, _ = Organization.objects.get_or_create(
        code='OOBC',
        defaults={
            'name': 'Office for Other Bangsamoro Communities',
            'short_name': 'OOBC',
            'organization_type': 'office',
            'is_active': True,
            'enabled_modules': [
                'communities',
                'mana',
                'coordination',
                'policies',
                'monitoring',
            ],
        }
    )
    return org


@pytest.fixture
def pilot_moh_organization(db):
    """Get Ministry of Health organization."""
    org, _ = Organization.objects.get_or_create(
        code='MOH',
        defaults={
            'name': 'Ministry of Health',
            'short_name': 'MOH',
            'organization_type': 'ministry',
            'is_active': True,
            'is_pilot': True,
            'enabled_modules': ['communities', 'mana', 'monitoring'],
        }
    )
    return org


@pytest.fixture
def pilot_mole_organization(db):
    """Get Ministry of Labor and Employment organization."""
    org, _ = Organization.objects.get_or_create(
        code='MOLE',
        defaults={
            'name': 'Ministry of Labor and Employment',
            'short_name': 'MOLE',
            'organization_type': 'ministry',
            'is_active': True,
            'is_pilot': True,
            'enabled_modules': ['communities', 'coordination'],
        }
    )
    return org


@pytest.fixture
def pilot_mafar_organization(db):
    """Get Ministry of Agriculture organization."""
    org, _ = Organization.objects.get_or_create(
        code='MAFAR',
        defaults={
            'name': 'Ministry of Agriculture, Fisheries and Agrarian Reform',
            'short_name': 'MAFAR',
            'organization_type': 'ministry',
            'is_active': True,
            'is_pilot': True,
            'enabled_modules': ['communities', 'planning'],
        }
    )
    return org


@pytest.fixture
def oobc_admin_user(db, default_organization):
    """Create OOBC admin user."""
    user = User.objects.create_user(
        username='oobc_admin',
        email='admin@oobc.gov.ph',
        password='testpass123',
        user_type='oobc_executive',
        is_staff=True,
    )
    OrganizationMembership.objects.create(
        user=user,
        organization=default_organization,
        role='admin',
        is_primary=True,
        is_active=True,
        can_manage_users=True,
        can_approve_plans=True,
        can_approve_budgets=True,
    )
    return user


@pytest.fixture
def moh_admin_user(db, pilot_moh_organization):
    """Create MOH admin user."""
    user = User.objects.create_user(
        username='moh_admin',
        email='admin@moh.barmm.gov.ph',
        password='testpass123',
        user_type='bmoa',
        is_staff=True,
    )
    OrganizationMembership.objects.create(
        user=user,
        organization=pilot_moh_organization,
        role='admin',
        is_primary=True,
        is_active=True,
        can_manage_users=True,
        can_approve_plans=True,
        can_approve_budgets=True,
    )
    return user


@pytest.fixture
def mole_staff_user(db, pilot_mole_organization):
    """Create MOLE staff user."""
    user = User.objects.create_user(
        username='mole_staff',
        email='staff@mole.barmm.gov.ph',
        password='testpass123',
        user_type='bmoa',
    )
    OrganizationMembership.objects.create(
        user=user,
        organization=pilot_mole_organization,
        role='staff',
        is_primary=True,
        is_active=True,
        can_view_reports=True,
    )
    return user


@pytest.fixture
def ocm_user(db):
    """Create OCM user with cross-organization access."""
    user = User.objects.create_user(
        username='ocm_admin',
        email='admin@ocm.barmm.gov.ph',
        password='testpass123',
        user_type='cm_office',
        is_staff=True,
    )
    # OCM users get read-only access to all organizations
    return user
