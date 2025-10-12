"""
Organizations app configuration for BMMS multi-tenancy.

This app provides the foundation for multi-tenant BMMS (Bangsamoro Ministerial
Management System), enabling 44 BARMM MOAs (Ministries, Offices, and Agencies)
to share a single platform while maintaining complete data isolation.

Key Components:
- Organization model: Represents each MOA with module activation flags
- OrganizationMembership: User-to-Organization relationships with roles
- OrganizationMiddleware: Sets organization context on every request
- OrganizationScopedModel: Abstract base class for organization-scoped data
"""

from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    """Configuration for the organizations app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "organizations"
    verbose_name = "Organizations (BMMS)"

    def ready(self):
        """Initialize app signals and configurations when Django starts."""
        # Import signal handlers if needed in future phases
        # import organizations.signals
        pass
