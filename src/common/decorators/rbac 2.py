"""
RBAC decorators for function-based views.

Provides permission and feature access control decorators that integrate
with the RBACService for organization-based access control.
"""

from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def _get_organization_from_request(request, organization_param=None):
    """
    Extract organization ID from request.

    Args:
        request: Django request object
        organization_param: Parameter name to extract from kwargs/GET

    Returns:
        Organization ID or None
    """
    if not organization_param:
        return None

    # Try kwargs first (URL parameters)
    org_id = request.resolver_match.kwargs.get(organization_param)
    if org_id:
        return org_id

    # Try GET parameters
    org_id = request.GET.get(organization_param)
    if org_id:
        return org_id

    # Try POST parameters
    if hasattr(request, 'POST'):
        org_id = request.POST.get(organization_param)
        if org_id:
            return org_id

    return None


def require_permission(permission_code, organization_param=None):
    """
    Decorator to require a specific permission for view access.

    Args:
        permission_code (str): Permission code to check (e.g., 'communities.view_obc_community')
        organization_param (str, optional): Parameter name containing organization ID

    Usage:
        @require_permission('communities.create_obc_community')
        def create_community(request):
            ...

        @require_permission('communities.edit_obc_community', organization_param='org_id')
        def edit_community(request, org_id):
            ...

    Raises:
        PermissionDenied: If user lacks the required permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Import here to avoid circular imports
            from common.services.rbac_service import RBACService

            if not request.user.is_authenticated:
                messages.error(
                    request,
                    "You must be logged in to access this resource."
                )
                raise PermissionDenied("Authentication required")

            # Extract organization context
            organization_id = _get_organization_from_request(request, organization_param)
            organization = None

            if organization_id:
                from coordination.models import Organization
                try:
                    organization = Organization.objects.get(pk=organization_id)
                except Organization.DoesNotExist:
                    pass

            # Check permission using RBACService
            if not RBACService.has_permission(request, permission_code, organization):
                messages.error(
                    request,
                    f"You do not have permission to access this resource."
                )
                raise PermissionDenied(
                    f"User lacks required permission: {permission_code}"
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_feature_access(feature_code, organization_param=None):
    """
    Decorator to require feature access for view access.

    Args:
        feature_code (str): Feature code to check (e.g., 'communities.barangay_obc', 'mana.regional_overview')
        organization_param (str, optional): Parameter name containing organization ID

    Usage:
        @require_feature_access('communities.barangay_obc')
        def communities_home(request):
            ...

        @require_feature_access('mana.regional_overview', organization_param='org_id')
        def mana_assessment(request, org_id):
            ...

    Raises:
        PermissionDenied: If user lacks feature access
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Import here to avoid circular imports
            from common.services.rbac_service import RBACService

            if not request.user.is_authenticated:
                messages.error(
                    request,
                    "You must be logged in to access this feature."
                )
                raise PermissionDenied("Authentication required")

            # Extract organization context
            organization_id = _get_organization_from_request(request, organization_param)
            organization = None

            if organization_id:
                from coordination.models import Organization
                try:
                    organization = Organization.objects.get(pk=organization_id)
                except Organization.DoesNotExist:
                    pass

            # Check feature access using RBACService
            if not RBACService.has_feature_access(request.user, feature_code, organization):
                feature_name = feature_code.split('.')[-1].replace('_', ' ').title()
                messages.error(
                    request,
                    f"You do not have access to the {feature_name} module."
                )
                raise PermissionDenied(
                    f"User lacks access to feature: {feature_code}"
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
