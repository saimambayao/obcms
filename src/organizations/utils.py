"""
Utility functions for organizations app.
"""
from django.conf import settings


def get_or_create_default_organization():
    """
    Get or create the default organization for OBCMS mode.

    Returns:
        tuple: (Organization, created) similar to get_or_create()
    """
    from organizations.models import Organization

    # Get default organization code from settings
    default_code = getattr(settings, 'DEFAULT_ORGANIZATION_CODE', 'OOBC')

    # Get or create organization
    organization, created = Organization.objects.get_or_create(
        code=default_code,
        defaults={
            'name': 'Office for Other Bangsamoro Communities',
            'org_type': 'office',
            'is_active': True,
        }
    )

    return organization, created
