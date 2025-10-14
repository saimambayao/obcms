"""
Organization utilities for BMMS multi-tenant support.

Provides utility functions for managing organizations, particularly
for OBCMS mode where a default OOBC organization is required.
"""
from django.conf import settings
from obc_management.settings.bmms_config import (
    is_obcms_mode,
    get_default_organization_code,
)


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
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Created default organization: {org.code} - {org.name}')
        return org
    return None
