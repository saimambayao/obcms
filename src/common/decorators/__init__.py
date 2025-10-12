"""Decorators for OBCMS."""

from .rbac import require_permission, require_feature_access

__all__ = ['require_permission', 'require_feature_access']
