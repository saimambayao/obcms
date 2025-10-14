"""
Organization-aware view decorators for BMMS multi-tenant support.

Provides decorators for function-based views to ensure organization
context exists and validate user access in BMMS mode.

This module implements the embedded architecture pattern where:
- OBCMS mode: Single organization (OOBC) automatically set by middleware
- BMMS mode: Multiple organizations with explicit membership validation

Key decorators:
- @require_organization: Validates organization context exists
- @organization_param(param_name): Loads organization from URL parameters

Usage:
    @login_required
    @require_organization
    def my_view(request):
        # request.organization is guaranteed to exist
        communities = OBCCommunity.objects.all()  # Auto-filtered
        return render(request, 'template.html')

See: docs/plans/bmms/implementation/tasks/phase4_view_decorators.txt
"""
import logging
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from organizations.models import Organization, OrganizationMembership
from obc_management.settings.bmms_config import is_bmms_mode, is_obcms_mode

logger = logging.getLogger(__name__)


def require_organization(view_func):
    """
    Decorator to ensure request has valid organization context.

    In OBCMS mode: Transparent (organization auto-injected by middleware)
    In BMMS mode: Validates user has access to requested organization

    Behavior:
    - Checks request.organization exists (set by OrganizationContextMiddleware)
    - In OBCMS mode: Allows access (single organization)
    - In BMMS mode: Validates OrganizationMembership (user must be member)
    - Superusers: Always granted access

    Usage:
        @login_required
        @require_organization
        def my_view(request):
            # request.organization is guaranteed to exist
            communities = OBCCommunity.objects.all()  # Auto-filtered
            return render(request, 'template.html')

    Returns:
        HttpResponseForbidden: If organization context missing or access denied
        HttpResponse: From wrapped view if validation passes
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if organization exists on request (set by middleware)
        if not hasattr(request, 'organization') or request.organization is None:
            logger.error(
                f'No organization context in request for view: {view_func.__name__}. '
                f'Ensure OrganizationContextMiddleware is enabled.'
            )
            return HttpResponseForbidden(
                'Organization context required but not found. '
                'Please ensure middleware is properly configured.'
            )

        # In BMMS mode, validate user access
        if is_bmms_mode() and request.user.is_authenticated:
            # Superusers can access any organization
            if request.user.is_superuser:
                logger.debug(
                    f'Superuser {request.user.username} granted access to '
                    f'organization {request.organization.code}'
                )
                return view_func(request, *args, **kwargs)

            # Check for active membership
            has_access = OrganizationMembership.objects.filter(
                user=request.user,
                organization=request.organization,
                is_active=True
            ).exists()

            if not has_access:
                logger.warning(
                    f'User {request.user.username} denied access to '
                    f'organization {request.organization.code} in view {view_func.__name__}'
                )
                return HttpResponseForbidden(
                    f'You do not have access to {request.organization.name}. '
                    f'Please contact your system administrator.'
                )

            logger.debug(
                f'User {request.user.username} granted access to '
                f'organization {request.organization.code}'
            )

        # In OBCMS mode, access is automatically granted (single org)
        return view_func(request, *args, **kwargs)

    return wrapper


def organization_param(param_name='org_code'):
    """
    Decorator to extract organization from URL parameters.

    This decorator loads the organization from a URL parameter
    and validates user access before calling the view. Useful for
    views that need explicit organization selection via URL.

    The decorator:
    1. Extracts organization code from URL kwargs
    2. Loads Organization object (or returns 404)
    3. Validates user access (in BMMS mode)
    4. Sets request.organization for the view

    Usage:
        @login_required
        @organization_param('org_code')
        def my_view(request, org_code):
            # request.organization is set and validated
            return render(request, 'template.html')

        # URL pattern: path('org/<str:org_code>/view/', my_view)

    Args:
        param_name: Name of URL parameter containing org code (default: 'org_code')

    Returns:
        HttpResponseForbidden: If org code invalid or access denied
        HttpResponse: From wrapped view if validation passes
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Extract org code from kwargs
            org_code = kwargs.get(param_name)

            if not org_code:
                logger.error(
                    f'Organization parameter "{param_name}" missing in '
                    f'view {view_func.__name__}'
                )
                return HttpResponseForbidden(
                    f'Organization parameter "{param_name}" is required.'
                )

            # Load organization (case-insensitive, active only)
            try:
                organization = get_object_or_404(
                    Organization,
                    code__iexact=org_code,
                    is_active=True
                )
            except Exception as e:
                logger.error(
                    f'Failed to load organization with code "{org_code}": {e}'
                )
                return HttpResponseForbidden(
                    f'Organization "{org_code}" not found or inactive.'
                )

            # Validate access in BMMS mode
            if is_bmms_mode() and request.user.is_authenticated:
                if not request.user.is_superuser:
                    has_access = OrganizationMembership.objects.filter(
                        user=request.user,
                        organization=organization,
                        is_active=True
                    ).exists()

                    if not has_access:
                        logger.warning(
                            f'User {request.user.username} denied access to '
                            f'organization {organization.code} via URL parameter '
                            f'in view {view_func.__name__}'
                        )
                        return HttpResponseForbidden(
                            f'You do not have access to {organization.name}.'
                        )

            # Set organization on request
            request.organization = organization
            logger.debug(
                f'Organization {organization.code} loaded from URL parameter '
                f'"{param_name}" for view {view_func.__name__}'
            )

            # Call view
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
