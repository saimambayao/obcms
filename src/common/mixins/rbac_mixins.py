"""
RBAC mixins for class-based views.

Provides permission and feature access control for Django's generic class-based views.
"""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class PermissionRequiredMixin:
    """
    Mixin to require a single permission for CBV access.

    Attributes:
        permission_required (str): Permission code to check
        organization_param (str): URL parameter containing organization ID

    Usage:
        class CommunityCreateView(PermissionRequiredMixin, CreateView):
            model = OBCCommunity
            permission_required = 'communities.create_obc_community'
            organization_param = 'org_id'
    """
    permission_required = None
    organization_param = None

    def dispatch(self, request, *args, **kwargs):
        """Check permission before dispatching to view."""
        if not self.permission_required:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} requires permission_required attribute to be set'
            )

        # Import here to avoid circular imports
        from common.services.rbac_service import RBACService

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this resource.")
            raise PermissionDenied("Authentication required")

        # Get organization context
        organization = self._get_organization_context(request, *args, **kwargs)

        # Check permission
        if not RBACService.has_permission(request, self.permission_required, organization):
            messages.error(
                request,
                f"You do not have permission to access this resource."
            )
            raise PermissionDenied(
                f"User lacks required permission: {self.permission_required}"
            )

        return super().dispatch(request, *args, **kwargs)

    def _get_organization_context(self, request, *args, **kwargs):
        """Extract organization from URL parameters or request."""
        if not self.organization_param:
            return RBACService.get_user_organization_context(request)

        org_id = kwargs.get(self.organization_param)
        if not org_id:
            return None

        from coordination.models import Organization
        try:
            return Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return None


class FeatureAccessMixin:
    """
    Mixin to require feature access for CBV access.

    Attributes:
        feature_required (str): Feature code to check
        organization_param (str): URL parameter containing organization ID

    Usage:
        class CommunityListView(FeatureAccessMixin, ListView):
            model = OBCCommunity
            feature_required = 'communities.barangay_obc'
    """
    feature_required = None
    organization_param = None

    def dispatch(self, request, *args, **kwargs):
        """Check feature access before dispatching to view."""
        if not self.feature_required:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} requires feature_required attribute to be set'
            )

        # Import here to avoid circular imports
        from common.services.rbac_service import RBACService

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this feature.")
            raise PermissionDenied("Authentication required")

        # Get organization context
        organization = self._get_organization_context(request, *args, **kwargs)

        # Check feature access
        if not RBACService.has_feature_access(request.user, self.feature_required, organization):
            feature_name = self.feature_required.split('.')[-1].replace('_', ' ').title()
            messages.error(
                request,
                f"You do not have access to the {feature_name} module."
            )
            raise PermissionDenied(
                f"User lacks access to feature: {self.feature_required}"
            )

        return super().dispatch(request, *args, **kwargs)

    def _get_organization_context(self, request, *args, **kwargs):
        """Extract organization from URL parameters or request."""
        if not self.organization_param:
            # Use RBACService to get organization context
            from common.services.rbac_service import RBACService
            return RBACService.get_user_organization_context(request)

        org_id = kwargs.get(self.organization_param)
        if not org_id:
            return None

        from coordination.models import Organization
        try:
            return Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return None


class MultiPermissionMixin:
    """
    Mixin to require one of multiple permissions for CBV access (OR logic).

    Attributes:
        permissions_required (list): List of permission codes (user needs ANY one)
        organization_param (str): URL parameter containing organization ID

    Usage:
        class CommunityUpdateView(MultiPermissionMixin, UpdateView):
            model = OBCCommunity
            permissions_required = [
                'communities.edit_obc_community',
                'communities.manage_obc_community'
            ]
    """
    permissions_required = None
    organization_param = None

    def dispatch(self, request, *args, **kwargs):
        """Check if user has any of the required permissions."""
        if not self.permissions_required:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} requires permissions_required attribute to be set'
            )

        if not isinstance(self.permissions_required, (list, tuple)):
            raise ImproperlyConfigured(
                'permissions_required must be a list or tuple'
            )

        # Import here to avoid circular imports
        from common.services.rbac_service import RBACService

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this resource.")
            raise PermissionDenied("Authentication required")

        # Get organization context
        organization = self._get_organization_context(request, *args, **kwargs)

        # Check if user has ANY of the required permissions
        has_any_permission = any(
            RBACService.has_permission(request, perm, organization)
            for perm in self.permissions_required
        )

        if not has_any_permission:
            messages.error(
                request,
                "You do not have permission to access this resource."
            )
            raise PermissionDenied(
                f"User lacks required permissions: {', '.join(self.permissions_required)}"
            )

        return super().dispatch(request, *args, **kwargs)

    def _get_organization_context(self, request, *args, **kwargs):
        """Extract organization from URL parameters or request."""
        if not self.organization_param:
            from common.services.rbac_service import RBACService
            return RBACService.get_user_organization_context(request)

        org_id = kwargs.get(self.organization_param)
        if not org_id:
            return None

        from coordination.models import Organization
        try:
            return Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return None


# Import at the end to avoid issues
from django.core.exceptions import ImproperlyConfigured
