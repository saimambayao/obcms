"""
Organization Context Middleware for BMMS Multi-Tenant Support.

Extracts organization context from URLs, query params, session, or user's default.
Enables organization-scoped data isolation for 44 MOAs (Ministries, Offices, Agencies).

Context Sources (priority order):
1. URL kwargs (org_id, organization_id)
2. Query parameters (?org=...)
3. User's default organization (user.moa_organization)
4. Session (request.session['current_organization'])

Special Cases:
- OCM (Office of Chief Minister): Can view all organizations
- OOBC Staff: Can switch between organizations
- MOA Staff: Limited to their organization only

Integration:
- Works with existing MOAFilteredQuerySetMixin pattern
- Compatible with organization-scoped permissions
- Caches organization context per request

See: docs/plans/bmms/TRANSITION_PLAN.md
"""

from typing import Optional
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from obc_management.settings.bmms_config import is_obcms_mode, is_bmms_mode
from organizations.utils import get_or_create_default_organization


def get_organization_from_request(request: HttpRequest):
    """
    Extract organization context from request.

    Mode-aware behavior:
    - OBCMS mode: Always return default OOBC organization
    - BMMS mode: Extract from URL/session/user

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
    Check if user has access to the given organization.

    Rules:
    - OCM users: Access to ALL organizations (oversight)
    - OOBC Staff: Access to ALL organizations (operations)
    - MOA Staff: Access to THEIR organization only
    - Other users: No organization access
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Superusers have access to everything
    if user.is_superuser:
        return True

    # OCM users have read-only access to all MOAs
    if is_ocm_user(user):
        return True

    # OOBC staff can access all organizations
    if user.is_oobc_staff:
        return True

    # MOA staff can only access their own organization
    if user.is_moa_staff:
        if user.moa_organization:
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
