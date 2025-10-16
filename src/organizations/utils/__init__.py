"""
Organization utilities for BMMS multi-tenant support.

Provides utility functions for managing organizations, particularly
for OBCMS mode where a default OOBC organization is required.
"""
import logging
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from obc_management.settings.bmms_config import (
    is_obcms_mode,
    is_bmms_mode,
    get_default_organization_code,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def get_default_organization():
    """
    Get the default organization for OBCMS mode.

    Returns:
        Organization: OOBC organization instance

    Raises:
        Organization.DoesNotExist: If default org not found

    Example:
        >>> org = get_default_organization()
        >>> print(org.code)
        'OOBC'
    """
    from organizations.models import Organization

    code = get_default_organization_code()
    return Organization.objects.get(code=code, is_active=True)


def get_or_create_default_organization():
    """
    Get or create the default organization for OBCMS mode.

    Creates OOBC organization with sensible defaults if it doesn't exist.

    Returns:
        tuple: (Organization, created) where created is boolean

    Example:
        >>> org, created = get_or_create_default_organization()
        >>> if created:
        ...     print(f"Created {org.name}")
        ... else:
        ...     print(f"Found existing {org.name}")
    """
    from organizations.models import Organization

    code = get_default_organization_code()
    return Organization.objects.get_or_create(
        code=code,
        defaults={
            'name': 'Office for Other Bangsamoro Communities',
            'acronym': 'OOBC',
            'org_type': 'office',
            'is_active': True,
            'enable_mana': True,
            'enable_planning': True,
            'enable_budgeting': True,
            'enable_me': True,
            'enable_coordination': True,
            'enable_policies': True,
        }
    )


def create_user_membership(user, organization, role='staff', is_primary=False):
    """
    Create or update user's membership in an organization.

    Args:
        user: User instance
        organization: Organization instance
        role: Role in organization (admin, manager, staff, viewer)
        is_primary: Whether this is the user's primary organization

    Returns:
        OrganizationMembership: Created or updated membership
    """
    from organizations.models import OrganizationMembership

    membership, created = OrganizationMembership.objects.get_or_create(
        user=user,
        organization=organization,
        defaults={
            'role': role,
            'is_primary': is_primary,
            'is_active': True,
        }
    )

    if not created:
        # Update existing membership
        membership.role = role
        membership.is_primary = is_primary
        membership.is_active = True
        membership.save()

    return membership


def ensure_default_organization_exists():
    """
    Ensure default organization exists in OBCMS mode.

    Called during system initialization to guarantee OOBC org exists.
    Only operates in OBCMS mode - does nothing in BMMS mode.

    Returns:
        Organization: The default organization, or None if in BMMS mode

    Example:
        >>> # In Django ready() method or management command
        >>> from organizations.utils import ensure_default_organization_exists
        >>> org = ensure_default_organization_exists()
    """
    if is_obcms_mode():
        org, created = get_or_create_default_organization()
        if created:
            logger.info(f'Created default organization: {org.code} - {org.name}')
        return org
    return None


def ensure_user_has_organization(user):
    """
    Ensure user has at least one organization membership.

    In OBCMS mode, automatically assigns user to OOBC.
    In BMMS mode, requires explicit organization assignment.

    Args:
        user: User instance

    Returns:
        OrganizationMembership: User's primary membership
    """
    if not user.is_authenticated:
        return None

    # Check if user already has memberships
    from organizations.models import OrganizationMembership

    existing_membership = OrganizationMembership.objects.filter(
        user=user,
        is_active=True
    ).first()

    if existing_membership:
        return existing_membership

    # In OBCMS mode, auto-assign to OOBC
    if is_obcms_mode():
        organization, _ = get_or_create_default_organization()
        membership = create_user_membership(
            user=user,
            organization=organization,
            role='staff',
            is_primary=True
        )

        logger.info(f"Auto-assigned user {user.username} to OOBC in OBCMS mode")
        return membership

    # In BMMS mode, user needs explicit organization assignment
    logger.warning(f"User {user.username} has no organization membership in BMMS mode")
    return None


def get_organization_context_for_user(user) -> dict:
    """
    Get complete organization context for a user.

    Args:
        user: User instance

    Returns:
        dict: Organization context data
    """
    if not user.is_authenticated:
        return {
            'user_organizations': [],
            'current_organization': None,
            'primary_organization': None,
            'can_switch': False,
            'is_bmms_mode': is_bmms_mode(),
        }

    # Get user's organizations
    from organizations.models import OrganizationMembership

    memberships = OrganizationMembership.objects.filter(
        user=user,
        is_active=True,
        organization__is_active=True
    ).select_related('organization').order_by('-is_primary', 'organization__name')

    user_organizations = []
    primary_organization = None
    current_organization = None

    for membership in memberships:
        org = membership.organization
        org_data = {
            'id': org.id,
            'code': org.code,
            'name': org.name,
            'org_type': org.org_type,
            'is_primary': membership.is_primary,
            'role': membership.role,
            'enabled_modules': org.enabled_modules,
        }
        user_organizations.append(org_data)

        if membership.is_primary:
            primary_organization = org

        # In a real request, this would come from request.organization
        # For utility purposes, we'll use the primary org
        if not current_organization:
            current_organization = org

    return {
        'user_organizations': user_organizations,
        'current_organization': current_organization,
        'primary_organization': primary_organization,
        'can_switch': is_bmms_mode() and len(user_organizations) > 1,
        'is_bmms_mode': is_bmms_mode(),
        'organization_count': len(user_organizations),
    }
