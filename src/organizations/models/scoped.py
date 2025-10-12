"""
Organization-scoped models for BMMS multi-tenancy.

This module provides the base class and utilities for organization-scoped data isolation.
All models that need organization-level data isolation should inherit from OrganizationScopedModel.
"""
import threading
from django.db import models
from django.utils.translation import gettext_lazy as _


# Thread-local storage for request context
_thread_locals = threading.local()


def get_current_organization():
    """
    Get the current organization from thread-local storage.

    Returns:
        Organization or None: The current organization set by OrganizationMiddleware
    """
    return getattr(_thread_locals, 'organization', None)


def set_current_organization(organization):
    """
    Set the current organization in thread-local storage.

    Args:
        organization: The Organization instance to set as current
    """
    _thread_locals.organization = organization


def clear_current_organization():
    """Clear the current organization from thread-local storage."""
    if hasattr(_thread_locals, 'organization'):
        del _thread_locals.organization


class OrganizationScopedManager(models.Manager):
    """
    Custom manager that automatically filters querysets by the current organization.

    This manager is used by OrganizationScopedModel to ensure data isolation.
    It filters all queries by the organization set in thread-local storage.
    """

    def get_queryset(self):
        """
        Get queryset filtered by current organization.

        Returns:
            QuerySet: Filtered by current organization if available,
                     otherwise returns unfiltered queryset (for admin/migrations)
        """
        queryset = super().get_queryset()
        current_org = get_current_organization()

        if current_org:
            # Filter by current organization from request context
            return queryset.filter(organization=current_org)

        # No organization in context: return unfiltered
        # This allows:
        # - Django migrations to run
        # - Management commands to access all data
        # - Admin/OCM staff to see cross-organization data
        return queryset

    def for_organization(self, organization):
        """
        Explicitly filter by a specific organization.

        Args:
            organization: Organization instance to filter by

        Returns:
            QuerySet: Filtered by the specified organization
        """
        return super().get_queryset().filter(organization=organization)

    def all_organizations(self):
        """
        Get unfiltered queryset across all organizations.

        Use this for admin views or OCM aggregation.

        Returns:
            QuerySet: Unfiltered queryset
        """
        return super().get_queryset()


class OrganizationScopedModel(models.Model):
    """
    Abstract base class for models that should be organization-scoped.

    All models inheriting from this class will:
    1. Have an `organization` foreign key
    2. Automatically filter queries by current organization
    3. Provide an `all_objects` manager for cross-organization access

    Usage:
        class MyModel(OrganizationScopedModel):
            name = models.CharField(max_length=100)
            # organization field is automatically added

        # Normal queries are automatically scoped:
        MyModel.objects.all()  # Only returns objects for current org

        # Admin/OCM can access all orgs:
        MyModel.all_objects.all()  # Returns all objects across all orgs

    Attributes:
        organization: ForeignKey to Organization (automatically added)
        objects: OrganizationScopedManager (auto-filtered by current org)
        all_objects: Manager (unfiltered, for admin/OCM use)
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_set',
        help_text=_('Organization that owns this record')
    )

    # Default manager: auto-filters by current organization
    objects = OrganizationScopedManager()

    # Unfiltered manager: for admin/OCM cross-organization access
    all_objects = models.Manager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization']),
        ]

    def save(self, *args, **kwargs):
        """
        Override save to auto-set organization if not provided.

        If organization is not set, use the current organization from
        thread-local storage (set by OrganizationMiddleware).
        """
        if not self.organization_id:
            current_org = get_current_organization()
            if current_org:
                self.organization = current_org

        super().save(*args, **kwargs)
