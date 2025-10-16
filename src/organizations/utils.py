"""
Utility functions for organizations app.

This module provides utility functions for:
- Default organization management
- Organization context helpers
- BMMS mode integration
- Data seeding and initialization
"""

import logging
from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from organizations.models import Organization, OrganizationMembership
from obc_management.settings.bmms_config import (
    is_obcms_mode,
    is_bmms_mode,
    get_default_organization_code
)

logger = logging.getLogger(__name__)
User = get_user_model()


def get_or_create_default_organization() -> Tuple[Organization, bool]:
    """
    Get or create the default organization (OOBC).

    In OBCMS mode, this provides the default organization context.
    In BMMS mode, this ensures OOBC exists for backward compatibility.

    Returns:
        Tuple[Organization, bool]: (Organization instance, was_created)
    """
    try:
        organization = Organization.objects.get(code='OOBC')
        return organization, False
    except Organization.DoesNotExist:
        # Create OOBC organization
        organization = Organization.objects.create(
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
            is_pilot=False,  # OOBC is not a pilot, it's the legacy system
        )

        logger.info("Created default OOBC organization")
        return organization, True


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


def get_user_primary_organization(user) -> Optional[Organization]:
    """
    Get user's primary organization.

    Args:
        user: User instance

    Returns:
        Organization or None
    """
    if not user.is_authenticated:
        return None

    try:
        membership = OrganizationMembership.objects.get(
            user=user,
            is_primary=True,
            is_active=True
        )
        return membership.organization
    except OrganizationMembership.DoesNotExist:
        # Fall back to any active membership
        membership = OrganizationMembership.objects.filter(
            user=user,
            is_active=True
        ).first()

        if membership:
            return membership.organization

        return None


def validate_organization_access(user, organization) -> Tuple[bool, str]:
    """
    Validate if user can access organization.

    Args:
        user: User instance
        organization: Organization instance

    Returns:
        Tuple[bool, str]: (can_access, reason)
    """
    if not user.is_authenticated:
        return False, "User not authenticated"

    if user.is_superuser:
        return True, "Superuser access"

    if not organization.is_active:
        return False, "Organization is not active"

    try:
        membership = OrganizationMembership.objects.get(
            user=user,
            organization=organization,
            is_active=True
        )
        return True, f"Active membership as {membership.get_role_display()}"
    except OrganizationMembership.DoesNotExist:
        return False, "No active membership found"


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


def initialize_system_organizations():
    """
    Initialize system organizations for first-time setup.

    This function ensures that critical system organizations exist
    and creates them if they don't. This is typically called during
    system initialization or migration.

    Returns:
        dict: Summary of created/verified organizations
    """
    results = {
        'created': [],
        'verified': [],
        'errors': []
    }

    # Critical organizations that must exist
    critical_orgs = [
        {
            'code': 'OOBC',
            'name': 'Office for Other Bangsamoro Communities',
            'org_type': 'office',
            'is_critical': True,
        },
        {
            'code': 'OCM',
            'name': 'Office of the Chief Minister',
            'org_type': 'office',
            'is_critical': True,
        }
    ]

    for org_data in critical_orgs:
        try:
            org, created = Organization.objects.get_or_create(
                code=org_data['code'],
                defaults={
                    'name': org_data['name'],
                    'org_type': org_data['org_type'],
                    'is_active': True,
                    'enable_mana': True,
                    'enable_planning': True,
                    'enable_budgeting': True,
                    'enable_me': True,
                    'enable_coordination': True,
                    'enable_policies': True,
                }
            )

            if created:
                results['created'].append(org_data['code'])
                logger.info(f"Created critical organization: {org_data['code']}")
            else:
                results['verified'].append(org_data['code'])
                logger.debug(f"Verified critical organization: {org_data['code']}")

        except Exception as e:
            error_msg = f"Failed to create {org_data['code']}: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)

    return results


def migrate_existing_users_to_organizations():
    """
    Migrate existing users to organizations during BMMS transition.

    This function assigns existing users to appropriate organizations
    based on their existing roles and permissions.

    Returns:
        dict: Migration results
    """
    results = {
        'migrated': 0,
        'skipped': 0,
        'errors': []
    }

    if not is_obcms_mode():
        results['errors'].append("This function should only be run in OBCMS mode")
        return results

    # Get default OOBC organization
    oobc_org, _ = get_or_create_default_organization()

    # Find users without organization memberships
    users_without_org = User.objects.filter(
        is_active=True
    ).exclude(
        id__in=OrganizationMembership.objects.filter(
            is_active=True
        ).values_list('user_id', flat=True)
    )

    for user in users_without_org:
        try:
            # Assign user to OOBC
            membership = create_user_membership(
                user=user,
                organization=oobc_org,
                role='staff',
                is_primary=True
            )

            results['migrated'] += 1
            logger.info(f"Migrated user {user.username} to OOBC")

        except Exception as e:
            error_msg = f"Failed to migrate user {user.username}: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)

    results['skipped'] = User.objects.filter(
        is_active=True
    ).count() - results['migrated'] - len(results['errors'])

    return results


def cleanup_organization_context():
    """
    Clean up organization context and session data.

    This function should be called when logging out or switching users
    to ensure no organization context leakage.
    """
    from organizations.models.scoped import clear_current_organization

    # Clear thread-local storage
    clear_current_organization()

    logger.debug("Cleaned up organization context")
