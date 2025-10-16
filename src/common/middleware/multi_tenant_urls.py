"""
Multi-tenant URL Middleware for BMMS Architecture

Enhances the existing organization context middleware to support ORG_CODE extraction
from URL patterns in BMMS multi-tenant mode.

URL Pattern Support:
- /moa/{ORG_CODE}/dashboard/ → Extract ORG_CODE from URL
- /moa/{ORG_CODE}/communities/ → Extract ORG_CODE from URL
- /moa/{ORG_CODE}/mana/ → Extract ORG_CODE from URL

Integration:
- Works with existing OrganizationContextMiddleware
- Maintains backward compatibility with OBCMS mode
- Supports organization switching without page reload
"""

from typing import Optional
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from obc_management.settings.bmms_config import is_bmms_mode, is_obcms_mode


def extract_org_code_from_url(request: HttpRequest) -> Optional[str]:
    """
    Extract ORG_CODE from URL path for BMMS multi-tenant mode.

    Args:
        request: HTTP request object

    Returns:
        str or None: Organization code extracted from URL

    Examples:
        /moa/DSWD/dashboard/ → Returns "DSWD"
        /moa/DOH/communities/ → Returns "DOH"
        /dashboard/ → Returns None (OBCMS mode)
    """
    if not is_bmms_mode():
        return None

    # Check URL path for /moa/{ORG_CODE}/ pattern
    path = request.path.strip('/')
    path_parts = path.split('/')

    # Pattern: /moa/{ORG_CODE}/...
    if len(path_parts) >= 2 and path_parts[0] == 'moa':
        org_code = path_parts[1]

        # Validate ORG_CODE format (alphanumeric, underscores, hyphens)
        if org_code and org_code.replace('_', '').replace('-', '').isalnum():
            return org_code.upper()

    return None


def get_organization_by_code(org_code: str):
    """
    Get organization instance by code.

    Args:
        org_code: Organization code

    Returns:
        Organization instance or None
    """
    try:
        from organizations.models import Organization
        return Organization.objects.get(code=org_code.upper(), is_active=True)
    except Organization.DoesNotExist:
        return None


def validate_organization_access(request: HttpRequest, organization) -> bool:
    """
    Validate if user has access to organization.

    Args:
        request: HTTP request object
        organization: Organization instance

    Returns:
        bool: True if user has access
    """
    if not request.user.is_authenticated:
        return False

    # Superusers have access to everything
    if request.user.is_superuser:
        return True

    # Check user's organization assignments
    try:
        from organizations.models import UserOrganizationAssignment
        return UserOrganizationAssignment.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True
        ).exists()
    except ImportError:
        # Fallback to legacy logic
        return hasattr(request.user, 'moa_organization') and \
               request.user.moa_organization == organization


def set_organization_context_from_code(request: HttpRequest) -> Optional['Organization']:
    """
    Set organization context from ORG_CODE extracted from URL.

    Args:
        request: HTTP request object

    Returns:
        Organization instance or None
    """
    org_code = extract_org_code_from_url(request)
    if not org_code:
        return None

    # Get organization by code
    organization = get_organization_by_code(org_code)
    if not organization:
        return None

    # Validate user access
    if not validate_organization_access(request, organization):
        raise PermissionDenied(f"Access denied to organization {org_code}")

    # Set organization in request (will be cached by middleware)
    request.organization = organization

    # Store in session for persistence
    request.session['current_organization_code'] = organization.code
    request.session['current_organization'] = str(organization.id)

    return organization


class MultiTenantURLMiddleware:
    """
    Middleware to handle multi-tenant URL patterns and organization context.

    This middleware:
    1. Extracts ORG_CODE from URL patterns in BMMS mode
    2. Validates organization access
    3. Sets organization context
    4. Handles organization switching

    Usage:
        # Add to MIDDLEWARE in settings.py
        'common.middleware.multi_tenant_urls.MultiTenantURLMiddleware',
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only process in BMMS mode
        if is_bmms_mode():
            try:
                # Extract and set organization context from URL
                organization = set_organization_context_from_code(request)

                # If no organization found in URL, try session
                if not organization and request.user.is_authenticated:
                    organization = self.get_organization_from_session(request)

                # Set organization for access in views
                if organization:
                    request.organization = organization
                else:
                    # Redirect to organization selection if needed
                    if self.requires_organization_context(request):
                        return redirect('organization_selection')

            except PermissionDenied:
                # Handle permission denied gracefully
                return redirect('common:page_restricted')

        response = self.get_response(request)
        return response

    def get_organization_from_session(self, request: HttpRequest) -> Optional['Organization']:
        """
        Get organization from session storage.

        Args:
            request: HTTP request object

        Returns:
            Organization instance or None
        """
        org_code = request.session.get('current_organization_code')
        if not org_code:
            return None

        organization = get_organization_by_code(org_code)
        if organization and validate_organization_access(request, organization):
            return organization

        # Clean up invalid session data
        if 'current_organization_code' in request.session:
            del request.session['current_organization_code']
        if 'current_organization' in request.session:
            del request.session['current_organization']

        return None

    def requires_organization_context(self, request: HttpRequest) -> bool:
        """
        Check if current URL requires organization context.

        Args:
            request: HTTP request object

        Returns:
            bool: True if organization context required
        """
        # URLs that don't require organization context
        no_org_required_paths = [
            '/login/',
            '/logout/',
            '/register/',
            '/health/',
            '/live/',
            '/ready/',
            '/admin/',
            '/api/',
            '/static/',
            '/media/',
            '/ocm/',  # OCM URLs are separate
        ]

        path = request.path
        return not any(path.startswith(prefix) for prefix in no_org_required_paths)


def create_organization_switcher(request: HttpRequest) -> dict:
    """
    Create organization switcher data for templates.

    Args:
        request: HTTP request object

    Returns:
        dict: Organization switcher data
    """
    if not is_bmms_mode() or not request.user.is_authenticated:
        return {}

    try:
        from organizations.models import UserOrganizationAssignment

        # Get user's accessible organizations
        assignments = UserOrganizationAssignment.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('organization')

        organizations = [assignment.organization for assignment in assignments]
        current_org = getattr(request, 'organization', None)

        return {
            'organizations': organizations,
            'current_organization': current_org,
            'can_switch': len(organizations) > 1,
        }
    except ImportError:
        return {}


def generate_organization_url(request: HttpRequest, url_name: str, org_code: str = None, **kwargs) -> str:
    """
    Generate organization-aware URL for BMMS mode.

    Args:
        request: HTTP request object
        url_name: URL name to reverse
        org_code: Organization code (optional)
        **kwargs: Additional URL parameters

    Returns:
        str: Generated URL
    """
    if is_obcms_mode():
        # OBCMS mode: standard URL reversal
        from django.urls import reverse
        return reverse(url_name, kwargs=kwargs)

    # BMMS mode: include organization context
    if not org_code:
        # Try to get from request
        org_code = extract_org_code_from_url(request)

    if not org_code:
        # Try to get from session
        org_code = request.session.get('current_organization_code')

    if org_code:
        # Add organization code to URL parameters
        kwargs['org_code'] = org_code

    from django.urls import reverse
    return reverse(url_name, kwargs=kwargs)


# Utility functions for views
def require_organization_context(view_func):
    """
    Decorator to require organization context for views.

    Args:
        view_func: View function to decorate

    Returns:
        Decorated view function
    """
    def wrapped_view(request, *args, **kwargs):
        if is_bmms_mode() and not getattr(request, 'organization', None):
            from django.shortcuts import redirect
            return redirect('organization_selection')

        return view_func(request, *args, **kwargs)

    # Mark view as requiring organization
    wrapped_view.requires_organization = True
    return wrapped_view


def organization_required(view_func):
    """
    Alternative decorator name for require_organization_context.
    """
    return require_organization_context(view_func)