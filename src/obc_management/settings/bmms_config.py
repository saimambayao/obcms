"""
BMMS Configuration Module

Provides configuration constants and utilities for BMMS multi-tenant mode.

IMPORTANT: This module is imported during settings initialization.
Do NOT import django.conf.settings here to avoid circular import deadlock.
"""


class BMMSMode:
    """BMMS operational modes."""
    OBCMS = 'obcms'  # Single-tenant mode (OOBC only)
    BMMS = 'bmms'    # Multi-tenant mode (44 MOAs)


def is_bmms_mode():
    """
    Check if system is running in BMMS mode.

    Note: Import settings inside function to avoid circular import during module load.
    """
    from django.conf import settings
    return getattr(settings, 'BMMS_MODE', BMMSMode.OBCMS) == BMMSMode.BMMS


def is_obcms_mode():
    """Check if system is running in OBCMS mode."""
    return not is_bmms_mode()


def get_default_organization_code():
    """
    Get the default organization code for OBCMS mode.

    Note: Import settings inside function to avoid circular import during module load.
    """
    from django.conf import settings
    return getattr(settings, 'DEFAULT_ORGANIZATION_CODE', 'OOBC')


def multi_tenant_enabled():
    """
    Check if multi-tenant features are enabled.

    Note: Import settings inside function to avoid circular import during module load.
    """
    from django.conf import settings
    if is_obcms_mode():
        return False  # OBCMS always single-tenant
    return getattr(settings, 'ENABLE_MULTI_TENANT', True)


def organization_switching_enabled():
    """
    Check if organization switching is allowed.

    Note: Import settings inside function to avoid circular import during module load.
    """
    from django.conf import settings
    if is_obcms_mode():
        return False  # No switching in OBCMS mode
    return getattr(settings, 'ALLOW_ORGANIZATION_SWITCHING', True)
