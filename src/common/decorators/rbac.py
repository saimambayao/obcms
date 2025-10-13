"""
RBAC decorators for function-based views.

Provides permission and feature access control decorators that integrate
with the RBACService for organization-based access control.
"""

import logging
from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

# Security audit logger for access denial events
# See: docs/security/RBAC_AUDIT_LOGGING.md
security_logger = logging.getLogger('rbac.access_denied')


def _get_client_ip(request):
    """
    Extract client IP address from request.

    Args:
        request: Django request object

    Returns:
        Client IP address string
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP if behind proxy
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


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
                # Get user info for audit logging
                user_id = request.user.id if hasattr(request.user, 'id') else 'unknown'
                username = request.user.username if hasattr(request.user, 'username') else 'anonymous'
                org_name = organization.name if organization else 'None'
                org_id = organization.id if organization else 'None'
                client_ip = _get_client_ip(request)

                # Security audit log - WARNING level for failed access attempts
                security_logger.warning(
                    f"403 Forbidden - User '{username}' (ID: {user_id}) denied access to "
                    f"permission '{permission_code}' in Organization '{org_name}' (ID: {org_id}) "
                    f"from IP {client_ip}",
                    extra={
                        'user_id': user_id,
                        'username': username,
                        'permission_code': permission_code,
                        'organization_id': org_id,
                        'organization_name': org_name,
                        'client_ip': client_ip,
                        'event_type': 'permission_denied',
                        'severity': 'warning',
                    }
                )

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
                # Get user info for audit logging
                user_id = request.user.id if hasattr(request.user, 'id') else 'unknown'
                username = request.user.username if hasattr(request.user, 'username') else 'anonymous'
                org_name = organization.name if organization else 'None'
                org_id = organization.id if organization else 'None'
                client_ip = _get_client_ip(request)

                # Security audit log - WARNING level for failed access attempts
                security_logger.warning(
                    f"403 Forbidden - User '{username}' (ID: {user_id}) denied access to "
                    f"feature '{feature_code}' in Organization '{org_name}' (ID: {org_id}) "
                    f"from IP {client_ip}",
                    extra={
                        'user_id': user_id,
                        'username': username,
                        'feature_code': feature_code,
                        'organization_id': org_id,
                        'organization_name': org_name,
                        'client_ip': client_ip,
                        'event_type': 'feature_access_denied',
                        'severity': 'warning',
                    }
                )

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
