"""
Organization middleware package for BMMS embedded architecture.

This package contains middleware components for BMMS dual-mode operation:
- OBCMSOrganizationMiddleware: Auto-inject OOBC in OBCMS mode
- OrganizationMiddleware: Extract org from URL in BMMS mode (moved from parent)
"""
from organizations.middleware.obcms_middleware import OBCMSOrganizationMiddleware
from organizations.middleware.organization import OrganizationMiddleware

__all__ = ['OBCMSOrganizationMiddleware', 'OrganizationMiddleware']
