"""Mixins for OBCMS class-based views."""

from .rbac_mixins import (
    PermissionRequiredMixin,
    FeatureAccessMixin,
    MultiPermissionMixin,
)

__all__ = [
    'PermissionRequiredMixin',
    'FeatureAccessMixin',
    'MultiPermissionMixin',
]
