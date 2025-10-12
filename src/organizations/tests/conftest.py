"""
Pytest Configuration and Fixtures for Organizations App Tests.

Provides reusable fixtures for:
- Test organizations (OOBC, MOH, MOLE, pilot MOAs)
- Test users with memberships
- Database setup/teardown
- Test client configurations
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from organizations.models import Organization, OrganizationMembership, _thread_locals

User = get_user_model()


@pytest.fixture(scope='function')
def clean_thread_locals():
    """
    Clean up thread-local storage before and after each test.

    CRITICAL: Ensures no data leakage between tests.
    """
    # Cleanup before test
    if hasattr(_thread_locals, 'organization'):
        del _thread_locals.organization
    if hasattr(_thread_locals, 'request'):
        del _thread_locals.request

    yield

    # Cleanup after test
    if hasattr(_thread_locals, 'organization'):
        del _thread_locals.organization
    if hasattr(_thread_locals, 'request'):
        del _thread_locals.request


@pytest.fixture
def test_client():
    """Provide Django test client."""
    return Client()


# ============================================================================
# ORGANIZATION FIXTURES
# ============================================================================

@pytest.fixture
def org_oobc(db):
    """
    Create OOBC organization (ID=1 for backward compatibility).

    OOBC is the primary organization for existing OBCMS data.
    """
    return Organization.objects.create(
        code='OOBC',
        name='Office for Other Bangsamoro Communities',
        org_type='office',
        enable_mana=True,
        enable_planning=True,
        enable_budgeting=True,
        enable_me=True,
        enable_coordination=True,
        enable_policies=True,
        is_active=True,
    )


@pytest.fixture
def org_moh(db):
    """Create Ministry of Health (pilot MOA)."""
    return Organization.objects.create(
        code='MOH',
        name='Ministry of Health',
        org_type='ministry',
        is_pilot=True,
        is_active=True,
    )


@pytest.fixture
def org_mole(db):
    """Create Ministry of Labor and Employment (pilot MOA)."""
    return Organization.objects.create(
        code='MOLE',
        name='Ministry of Labor and Employment',
        org_type='ministry',
        is_pilot=True,
        is_active=True,
    )


@pytest.fixture
def org_mafar(db):
    """Create Ministry of Agriculture (pilot MOA)."""
    return Organization.objects.create(
        code='MAFAR',
        name='Ministry of Agriculture, Fisheries and Agrarian Reform',
        org_type='ministry',
        is_pilot=True,
        is_active=True,
    )


@pytest.fixture
def pilot_moas(db, org_moh, org_mole, org_mafar):
    """Provide all 3 pilot MOAs."""
    return [org_moh, org_mole, org_mafar]


@pytest.fixture
def all_44_moas(db):
    """
    Create all 44 BARMM MOAs (for comprehensive tests).

    Organizations are created in order:
    - OOBC (ID=1)
    - 16 Ministries
    - 10 Offices
    - 8 Agencies
    - 7 Special Bodies
    - 3 Commissions
    """
    organizations = []

    # OOBC (must be first)
    organizations.append(Organization.objects.create(
        code='OOBC',
        name='Office for Other Bangsamoro Communities',
        org_type='office',
        is_active=True,
    ))

    # Ministries (16)
    ministries = [
        ('MAFAR', 'Ministry of Agriculture, Fisheries and Agrarian Reform', True),
        ('MBHTE', 'Ministry of Basic, Higher and Technical Education', False),
        ('MENRE', 'Ministry of Environment, Natural Resources and Energy', False),
        ('MFBM', 'Ministry of Finance, Budget and Management', False),
        ('MOH', 'Ministry of Health', True),
        ('MHSD', 'Ministry of Human Settlements and Development', False),
        ('MIPA', 'Ministry of Indigenous Peoples Affairs', False),
        ('MILG', 'Ministry of Interior and Local Government', False),
        ('MOLE', 'Ministry of Labor and Employment', True),
        ('MPWH', 'Ministry of Public Works and Highways', False),
        ('MSSD', 'Ministry of Social Services and Development', False),
        ('MTI', 'Ministry of Trade, Investments and Tourism', False),
        ('MTIT', 'Ministry of Transportation and Information Technology', False),
        ('MWDWA', 'Ministry of Women, Development and Welfare Affairs', False),
        ('MYNDA', 'Ministry of Youth and Nonprofit Development Affairs', False),
    ]

    for code, name, is_pilot in ministries:
        organizations.append(Organization.objects.create(
            code=code,
            name=name,
            org_type='ministry',
            is_pilot=is_pilot,
            is_active=True,
        ))

    # Offices (10)
    offices = [
        'OCM', 'OMP', 'OPARL', 'OPMDA', 'OSM',
        'OTAF', 'OADP', 'OBCE', 'OCRE', 'OMLA',
    ]
    for code in offices:
        organizations.append(Organization.objects.create(
            code=code,
            name=f'Office - {code}',
            org_type='office',
            is_active=True,
        ))

    # Agencies (8)
    agencies = [
        'BAI', 'BEDC', 'BTA', 'BSWM',
        'CAB', 'CSC-BARMM', 'RLEA', 'TESDA-BARMM',
    ]
    for code in agencies:
        organizations.append(Organization.objects.create(
            code=code,
            name=f'Agency - {code}',
            org_type='agency',
            is_active=True,
        ))

    # Special Bodies (7)
    special = [
        'BIDA', 'BIAF', 'BRTA', 'BSBC',
        'BWPB', 'MUWASSCO', 'SPBI',
    ]
    for code in special:
        organizations.append(Organization.objects.create(
            code=code,
            name=f'Special Body - {code}',
            org_type='special',
            is_active=True,
        ))

    # Commissions (3)
    commissions = ['BCHRC', 'BWCRC', 'BYDC']
    for code in commissions:
        organizations.append(Organization.objects.create(
            code=code,
            name=f'Commission - {code}',
            org_type='commission',
            is_active=True,
        ))

    return organizations


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def regular_user(db):
    """Create regular user without organization membership."""
    return User.objects.create_user(
        username='regular_user',
        email='regular@example.com',
        password='testpass123',
    )


@pytest.fixture
def oobc_staff_user(db, org_oobc):
    """Create OOBC staff user with membership."""
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
def oobc_admin_user(db, org_oobc):
    """Create OOBC admin user with elevated permissions."""
    user = User.objects.create_user(
        username='oobc_admin',
        email='admin@oobc.gov.ph',
        password='testpass123',
    )
    OrganizationMembership.objects.create(
        user=user,
        organization=org_oobc,
        role='admin',
        is_primary=True,
        can_manage_users=True,
        can_approve_plans=True,
        can_approve_budgets=True,
        can_view_reports=True,
    )
    return user


@pytest.fixture
def moh_staff_user(db, org_moh):
    """Create MOH staff user with membership."""
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
def multi_org_user(db, org_oobc, org_moh, org_mole):
    """
    Create user with memberships in multiple organizations.

    Primary: OOBC (staff)
    Secondary: MOH (viewer), MOLE (viewer)
    """
    user = User.objects.create_user(
        username='multi_org',
        email='multi@system.gov.ph',
        password='testpass123',
    )

    # OOBC membership (primary)
    OrganizationMembership.objects.create(
        user=user,
        organization=org_oobc,
        role='staff',
        is_primary=True,
    )

    # MOH membership (secondary)
    OrganizationMembership.objects.create(
        user=user,
        organization=org_moh,
        role='viewer',
        is_primary=False,
    )

    # MOLE membership (secondary)
    OrganizationMembership.objects.create(
        user=user,
        organization=org_mole,
        role='viewer',
        is_primary=False,
    )

    return user


@pytest.fixture
def superuser(db):
    """Create superuser with full system access."""
    return User.objects.create_user(
        username='admin',
        email='admin@system.gov.ph',
        password='adminpass123',
        is_superuser=True,
        is_staff=True,
    )


# ============================================================================
# MEMBERSHIP FIXTURES
# ============================================================================

@pytest.fixture
def staff_membership(db, regular_user, org_oobc):
    """Create staff-level membership."""
    return OrganizationMembership.objects.create(
        user=regular_user,
        organization=org_oobc,
        role='staff',
        is_primary=True,
    )


@pytest.fixture
def admin_membership(db, regular_user, org_oobc):
    """Create admin-level membership with elevated permissions."""
    return OrganizationMembership.objects.create(
        user=regular_user,
        organization=org_oobc,
        role='admin',
        is_primary=True,
        can_manage_users=True,
        can_approve_plans=True,
        can_approve_budgets=True,
        can_view_reports=True,
    )


@pytest.fixture
def viewer_membership(db, regular_user, org_oobc):
    """Create viewer-level membership (read-only)."""
    return OrganizationMembership.objects.create(
        user=regular_user,
        organization=org_oobc,
        role='viewer',
        is_primary=True,
        can_manage_users=False,
        can_approve_plans=False,
        can_approve_budgets=False,
        can_view_reports=True,
    )


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope='function')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Ensure database is ready before each test.

    This fixture wraps django_db_setup to ensure proper isolation.
    """
    with django_db_blocker.unblock():
        # Database is ready
        pass


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests by default.

    This prevents the need to add @pytest.mark.django_db to every test.
    """
    pass


# ============================================================================
# REQUEST FACTORY FIXTURES
# ============================================================================

@pytest.fixture
def request_factory():
    """Provide Django RequestFactory."""
    from django.test import RequestFactory
    return RequestFactory()


@pytest.fixture
def authenticated_request(request_factory, oobc_staff_user):
    """Provide authenticated request with OOBC staff user."""
    request = request_factory.get('/')
    request.user = oobc_staff_user
    return request


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def organization_data():
    """
    Provide sample organization data for testing.

    Useful for form testing and API endpoint testing.
    """
    return {
        'code': 'TEST',
        'name': 'Test Organization',
        'org_type': 'office',
        'enable_mana': True,
        'enable_planning': True,
        'enable_budgeting': True,
        'enable_me': True,
        'enable_coordination': True,
        'enable_policies': True,
        'is_active': True,
    }


@pytest.fixture
def membership_data(regular_user, org_oobc):
    """Provide sample membership data for testing."""
    return {
        'user': regular_user,
        'organization': org_oobc,
        'role': 'staff',
        'is_primary': True,
        'can_view_reports': True,
    }
