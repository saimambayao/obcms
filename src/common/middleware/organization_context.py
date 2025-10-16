"""
Organization Context Middleware for BMMS Multi-Tenant Support.

Extracts organization context from URLs, query params, session, or user's default.
Enables organization-scoped data isolation for 44 MOAs (Ministries, Offices, Agencies).

This middleware integrates with the enhanced organizations/middleware.py to provide:
- Backward compatibility with existing OBCMS patterns
- Integration with organizations app models and utilities
- Thread-safe context management
- Comprehensive audit logging

Context Sources (priority order):
1. Enhanced organizations middleware (primary source)
2. URL kwargs (org_id, organization_id) - legacy support
3. Query parameters (?org=...) - legacy support
4. User's default organization (user.moa_organization) - fallback
5. Session (request.session['current_organization']) - persistence

Special Cases:
- OCM (Office of Chief Minister): Read-only access to all organizations
- OOBC Staff: Can switch between organizations
- MOA Staff: Limited to their organization only
- Superusers: Full access to all organizations

Integration:
- Works with enhanced organizations/middleware.OrganizationMiddleware
- Compatible with organization-scoped permissions
- Supports existing MOAFilteredQuerySetMixin pattern
- Thread-safe concurrent request handling

See: docs/plans/bmms/TRANSITION_PLAN.md
"""

from typing import Optional
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject
from django.core.exceptions import PermissionDenied

from obc_management.settings.bmms_config import is_obcms_mode, is_bmms_mode
from organizations.utils import get_or_create_default_organization
from organizations.models.organization import Organization


def get_organization_from_request(request: HttpRequest):
    """
    Extract organization context from request with enhanced integration.

    This function now integrates with the enhanced organizations/middleware.py
    to provide seamless organization context management.

    Mode-aware behavior:
    - OBCMS mode: Always return default OOBC organization
    - BMMS mode: Use enhanced organizations middleware as primary source
    - Legacy fallback: Extract from URL/session/user for backward compatibility

    Returns:
        Organization instance or None
    """
    from organizations.models import Organization

    # ========== OBCMS MODE: Auto-inject default organization ==========
    if is_obcms_mode():
        if not hasattr(request, "_cached_default_org"):
            request._cached_default_org, _ = get_or_create_default_organization()
        return request._cached_default_org

    # Fail-safe: if not explicitly in BMMS mode, do not resolve organization
    if not is_bmms_mode():
        return None

    # ========== INTEGRATION: Check if enhanced middleware already set context ==========
    if hasattr(request, 'organization') and request.organization:
        # Enhanced organizations middleware has already set the organization
        # Verify it's a valid Organization instance
        if isinstance(request.organization, Organization):
            return request.organization

    # ========== LEGACY FALLBACK: Original logic for backward compatibility ==========
    # Early return if no authenticated user
    if not request.user.is_authenticated:
        return None

    organization = None
    org_id = None

    # 1. Check URL kwargs (highest priority)
    if hasattr(request, 'resolver_match') and request.resolver_match:
        kwargs = request.resolver_match.kwargs
        org_id = kwargs.get('org_id') or kwargs.get('organization_id')

    # 2. Check query parameters
    if not org_id:
        org_id = request.GET.get('org')

    # 3. Try to fetch organization by ID
    if org_id:
        try:
            organization = Organization.objects.get(id=org_id)

            # Security: Verify user has access to this organization
            if not user_can_access_organization(request.user, organization):
                return None

            # Store in session for next request
            request.session['current_organization'] = str(organization.id)

        except (Organization.DoesNotExist, ValueError):
            pass

    # 4. Check user's default organization
    if not organization and hasattr(request.user, 'moa_organization'):
        organization = request.user.moa_organization

    # 5. Check session (lowest priority)
    if not organization and 'current_organization' in request.session:
        try:
            org_id = request.session['current_organization']
            organization = Organization.objects.get(id=org_id)

            # Verify access still valid
            if not user_can_access_organization(request.user, organization):
                del request.session['current_organization']
                organization = None

        except (Organization.DoesNotExist, KeyError):
            # Clean up invalid session data
            if 'current_organization' in request.session:
                del request.session['current_organization']

    return organization


def user_can_access_organization(user, organization) -> bool:
    """
    Check if user has access to the given organization with enhanced integration.

    This function now integrates with the organizations app for comprehensive
    access checking and supports the enhanced organization context.

    Rules:
    - Superusers: Access to ALL organizations
    - OCM users: Read-only access to ALL organizations (oversight)
    - OOBC Staff: Access to ALL organizations (operations)
    - MOA Staff: Access to THEIR organization only
    - Other users: No organization access

    Integration:
    - Uses organizations.models.OrganizationMembership for precise access control
    - Supports thread-safe context checking
    - Compatible with enhanced organizations middleware
    """
    from django.contrib.auth import get_user_model
    from organizations.models.organization import OrganizationMembership

    User = get_user_model()

    # Anonymous users have no access
    if not user.is_authenticated:
        return False

    # Superusers have access to everything
    if user.is_superuser:
        return True

    # OCM users have read-only access to all MOAs
    if is_ocm_user(user):
        return True

    # OOBC staff can access all organizations
    if hasattr(user, 'is_oobc_staff') and user.is_oobc_staff:
        return True

    # Enhanced: Check organization memberships via organizations app
    try:
        return OrganizationMembership.objects.filter(
            user=user,
            organization=organization,
            is_active=True
        ).exists()
    except Exception:
        # Fallback to legacy checks for backward compatibility
        if hasattr(user, 'is_moa_staff') and user.is_moa_staff:
            if hasattr(user, 'moa_organization') and user.moa_organization:
                return user.moa_organization == organization
            return False

    # Default: no access
    return False


def is_ocm_user(user) -> bool:
    """
    Check if user is from Office of Chief Minister (OCM).

    OCM users have special aggregation access across all MOAs.
    """
    # Check if user belongs to OCM organization
    if hasattr(user, 'moa_organization') and user.moa_organization:
        # OCM organization code from settings
        from django.conf import settings
        ocm_code = getattr(settings, 'RBAC_SETTINGS', {}).get('OCM_ORGANIZATION_CODE', 'ocm')

        if hasattr(user.moa_organization, 'acronym'):
            return user.moa_organization.acronym.lower() == ocm_code.lower()

    # Also check user_type
    return user.user_type == 'cm_office'


class OrganizationContextMiddleware:
    """
    Middleware to set organization context on request object.

    Mode-aware behavior:
    - OBCMS mode: Auto-injects default OOBC organization
    - BMMS mode: Extracts organization from URL/session/user

    This is the ONLY middleware that sets request.organization.
    Do NOT create additional organization middleware classes.

    Usage:
        # In views.py
        organization = request.organization
        if organization:
            queryset = queryset.filter(moa_organization=organization)

    Integration with RBAC:
        # Permission checks use organization context
        from common.services.rbac_service import RBACService

        if RBACService.has_permission(request, 'communities.view_obc_community'):
            # Permission automatically scoped to request.organization
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set organization as lazy object (only evaluated when accessed)
        request.organization = SimpleLazyObject(
            lambda: get_organization_from_request(request)
        )

        # Also set OCM flag for quick checks
        if request.user.is_authenticated:
            request.is_ocm_user = is_ocm_user(request.user)
        else:
            request.is_ocm_user = False

        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process view to validate organization access.

        If view explicitly requires organization context, validate access.
        """
        # Check if view requires organization
        if hasattr(view_func, 'requires_organization'):
            if not request.organization:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden(
                    "Organization context required. Please select an organization."
                )

        return None
