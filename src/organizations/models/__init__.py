"""
Organizations app models for BMMS multi-tenancy.

This module provides the foundation for multi-tenant data isolation in BMMS.

Models:
- Organization: Represents each of the 44 BARMM MOAs
- OrganizationMembership: User-to-Organization relationships with roles
- OrganizationScopedModel: Abstract base class for organization-scoped data
"""

from organizations.models.organization import (
    Organization,
    OrganizationMembership,
)
from organizations.models.scoped import (
    OrganizationScopedModel,
    OrganizationScopedManager,
    get_current_organization,
    set_current_organization,
    clear_current_organization,
    _thread_locals,
)

__all__ = [
    "Organization",
    "OrganizationMembership",
    "OrganizationScopedModel",
    "OrganizationScopedManager",
    "get_current_organization",
    "set_current_organization",
    "clear_current_organization",
    "_thread_locals",
]
