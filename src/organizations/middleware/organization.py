"""
OrganizationMiddleware for BMMS multi-tenant request context.

This middleware sets the current organization on every request based on:
1. Organization code in URL path (/moa/<ORG_CODE>/...) - BMMS mode only
2. User's primary organization (fallback) - BMMS mode only
3. Session-stored organization selection - BMMS mode only

Mode-Aware Behavior:
- OBCMS Mode: Pass-through (OBCMSOrganizationMiddleware already set organization)
- BMMS Mode: Extract org from URL and validate user access

Security Features:
- Verifies user has access to requested organization
- Blocks unauthorized access attempts
- Allows superusers to access any organization
- Stores organization in thread-local storage for models

Design Decisions:
- Runs AFTER OBCMSOrganizationMiddleware in middleware chain
- In OBCMS mode, skips all URL extraction logic
- In BMMS mode, extracts organization from /moa/<ORG_CODE>/ URLs
- URL-based organization takes precedence (explicit selection)
- Session persistence for organization selection across requests
- Thread-local cleanup ensures no memory leaks
- Middleware must run AFTER AuthenticationMiddleware

References:
- docs/plans/bmms/implementation/BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md
- docs/plans/bmms/implementation/tasks/phase3_middleware.txt
"""

import logging
from typing import Optional

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import AnonymousUser

from obc_management.settings.bmms_config import is_obcms_mode
from organizations.models.organization import Organization, OrganizationMembership
from organizations.models.scoped import (
    set_current_organization,
    clear_current_organization,
)

logger = logging.getLogger(__name__)


class OrganizationMiddleware:
    """
    Set organization context on every request (BMMS mode only).

    This middleware performs the following operations in BMMS mode:
    1. Extracts organization from URL pattern (/moa/<ORG_CODE>/...)
    2. Loads organization from database
    3. Verifies user has access (via OrganizationMembership)
    4. Sets request.organization attribute
    5. Stores organization in thread-local storage
    6. Cleans up thread-local after response

    In OBCMS mode, this middleware is a pass-through since
    OBCMSOrganizationMiddleware already set request.organization.

    URL Pattern (BMMS mode only):
        /moa/OOBC/... → Sets organization to OOBC
        /moa/MOH/...  → Sets organization to MOH
        /...          → Uses user's primary organization or session

    Access Control:
        - User must have active OrganizationMembership
        - Superusers can access any organization
        - Anonymous users: no organization context
        - Unauthenticated requests: organization required for MOA URLs

    Middleware Order:
        1. AuthenticationMiddleware (Django built-in)
        2. OBCMSOrganizationMiddleware - Auto-inject OOBC in OBCMS mode
        3. OrganizationMiddleware (this) - Extract org from URL in BMMS mode
    """

    def __init__(self, get_response):
        """Initialize middleware with response handler."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and set organization context.

        Mode-Aware Flow:
        - OBCMS Mode: Skip (OBCMSOrganizationMiddleware already set organization)
        - BMMS Mode: Extract org from URL and validate access

        Args:
            request: HttpRequest instance

        Returns:
            HttpResponse instance
        """
        from django.apps import apps

        # Don't access database during app initialization
        if not apps.ready:
            return self.get_response(request)

        # Skip in OBCMS mode - OBCMSOrganizationMiddleware already handled it
        if is_obcms_mode():
            # Organization already set by OBCMSOrganizationMiddleware
            # Just pass through to next middleware/view
            response = self.get_response(request)
            # Still cleanup thread-local storage (defensive)
            clear_current_organization()
            return response

        # BMMS mode: Extract organization from URL
        # Step 1: Extract organization code from URL
        org_code = self._extract_org_code_from_url(request.path)

        organization = None

        if org_code:
            # URL specifies organization: /moa/<ORG_CODE>/...
            organization = self._get_organization_from_code(org_code)

            if not organization:
                # Invalid organization code
                return HttpResponseForbidden(
                    f'Organization not found: {org_code}'
                )

            # Verify access
            if not self._user_can_access_organization(request.user, organization):
                return HttpResponseForbidden(
                    f'You do not have access to {organization.name}. '
                    f'Please contact your system administrator.'
                )

            # Store in session for persistence
            request.session['selected_organization_id'] = organization.id

        else:
            # No org in URL: try session, then primary organization
            if request.user.is_authenticated:
                organization = self._get_user_organization(request)

        # Step 2: Set organization on request and thread-local
        request.organization = organization

        if organization:
            set_current_organization(organization)
            logger.debug(
                f'Organization context set: {organization.code} '
                f'for user: {request.user.username if request.user.is_authenticated else "anonymous"}'
            )
        else:
            clear_current_organization()

        # Step 3: Process request
        response = self.get_response(request)

        # Step 4: Cleanup thread-local storage
        clear_current_organization()

        return response

    def _extract_org_code_from_url(self, path: str) -> Optional[str]:
        """
        Extract organization code from URL path.

        URL Pattern: /moa/<ORG_CODE>/...

        Args:
            path: URL path string

        Returns:
            Organization code (uppercase) or None

        Examples:
            /moa/OOBC/dashboard/ � 'OOBC'
            /moa/moh/assessments/ � 'MOH'
            /dashboard/ � None
        """
        parts = path.strip('/').split('/')

        # Check for /moa/<ORG_CODE>/ pattern
        if len(parts) >= 2 and parts[0] == 'moa':
            org_code = parts[1].upper()
            return org_code

        return None

    def _get_organization_from_code(self, code: str) -> Optional[Organization]:
        """
        Load organization from database by code.

        Args:
            code: Organization code (e.g., 'OOBC', 'MOH')

        Returns:
            Organization instance or None
        """
        try:
            return Organization.objects.get(
                code=code,
                is_active=True
            )
        except Organization.DoesNotExist:
            logger.warning(f'Organization not found or inactive: {code}')
            return None

    def _user_can_access_organization(
        self,
        user,
        organization: Organization
    ) -> bool:
        """
        Check if user has access to organization.

        Access Rules:
        - Superusers: can access any organization
        - Authenticated users: must have active OrganizationMembership
        - Anonymous users: no access

        Args:
            user: User instance or AnonymousUser
            organization: Organization instance

        Returns:
            bool: True if user can access, False otherwise
        """
        # Anonymous users have no organization access
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False

        # Superusers can access any organization
        if user.is_superuser:
            return True

        # Check for active membership
        return OrganizationMembership.objects.filter(
            user=user,
            organization=organization,
            is_active=True
        ).exists()

    def _get_user_organization(self, request: HttpRequest) -> Optional[Organization]:
        """
        Get organization for authenticated user.

        Priority:
        1. Session-stored organization (from last selection)
        2. User's primary organization
        3. None

        Args:
            request: HttpRequest instance

        Returns:
            Organization instance or None
        """
        # Try session first (persists org selection across requests)
        org_id = request.session.get('selected_organization_id')
        if org_id:
            try:
                organization = Organization.objects.get(
                    id=org_id,
                    is_active=True
                )
                # Verify user still has access
                if self._user_can_access_organization(request.user, organization):
                    return organization
                else:
                    # Clear invalid session
                    del request.session['selected_organization_id']
            except Organization.DoesNotExist:
                # Clear invalid session
                del request.session['selected_organization_id']

        # Fall back to primary organization
        try:
            membership = OrganizationMembership.objects.filter(
                user=request.user,
                is_primary=True,
                is_active=True
            ).select_related('organization').first()

            if membership and membership.organization.is_active:
                # Store in session for next request
                request.session['selected_organization_id'] = membership.organization.id
                return membership.organization

        except Exception as e:
            logger.error(f'Error getting primary organization: {e}')

        # No organization found
        return None


# ========== CONTEXT PROCESSOR ==========


def organization_context(request: HttpRequest) -> dict:
    """
    Context processor to add organization to all templates.

    Add to settings.py:
        TEMPLATES = [{
            'OPTIONS': {
                'context_processors': [
                    ...
                    'organizations.middleware.organization_context',
                ]
            }
        }]

    Usage in templates:
        {% if request.organization %}
            <h1>{{ request.organization.name }}</h1>
            <p>{{ request.organization.code }}</p>
        {% endif %}

        <!-- Organization-aware URL generation -->
        <a href="{{ org_url_prefix }}/communities/">Communities</a>

    Args:
        request: HttpRequest instance

    Returns:
        dict: Context with organization data and URL prefix
    """
    from obc_management.settings.bmms_config import is_bmms_mode

    organization = getattr(request, 'organization', None)

    # Generate org_url_prefix for template URL generation
    org_url_prefix = ''
    if is_bmms_mode() and organization:
        org_url_prefix = f'/moa/{organization.code}'

    if organization:
        return {
            'current_organization': organization,
            'organization_code': organization.code,
            'organization_name': organization.name,
            'enabled_modules': organization.enabled_modules,
            'org_url_prefix': org_url_prefix,
            'is_bmms_mode': is_bmms_mode(),
        }

    return {
        'current_organization': None,
        'organization_code': None,
        'organization_name': None,
        'enabled_modules': [],
        'org_url_prefix': '',
        'is_bmms_mode': is_bmms_mode(),
    }
