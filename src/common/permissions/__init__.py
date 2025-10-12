"""DRF permission classes for OBCMS."""

from .rbac_permissions import (
    HasFeatureAccess,
    HasPermission,
    HasAnyPermission,
    HasAllPermissions,
)

__all__ = [
    'HasFeatureAccess',
    'HasPermission',
    'HasAnyPermission',
    'HasAllPermissions',
]
