"""
OrganizationMiddleware for BMMS multi-tenant request context.

This middleware sets the current organization on every request based on:
1. Organization code in URL path (/moa/<ORG_CODE>/...)
2. User's primary organization (fallback)
3. Session-stored organization selection

Security Features:
- Verifies user has access to requested organization
- Blocks unauthorized access attempts
- Allows superusers to access any organization
- Stores organization in thread-local storage for models
- Comprehensive audit logging for all context changes
- Thread-safe concurrent request handling

Design Decisions:
- URL-based organization takes precedence (explicit selection)
- Session persistence for organization selection across requests
- Thread-local cleanup ensures no memory leaks
- Middleware must run AFTER AuthenticationMiddleware
- OCM special access patterns for cross-organization queries
- Mode-aware behavior (OBCMS vs BMMS)
"""

import logging
import threading
import time
from typing import Optional, Dict, Any
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from organizations.models.organization import Organization, OrganizationMembership
from organizations.models.scoped import (
    set_current_organization,
    clear_current_organization,
    get_current_organization,
)
from obc_management.settings.bmms_config import is_obcms_mode, is_bmms_mode

# Thread-local storage for request context
_thread_context = threading.local()

# Audit logger for organization context changes
audit_logger = logging.getLogger('organizations.audit')
security_logger = logging.getLogger('organizations.security')

logger = logging.getLogger(__name__)


class OrganizationMiddleware:
    """
    Set organization context on every request with comprehensive audit logging.

    This middleware performs the following operations:
    1. Extracts organization from URL pattern (/moa/<ORG_CODE>/...)
    2. Loads organization from database with caching
    3. Verifies user has access (via OrganizationMembership)
    4. Sets request.organization attribute
    5. Stores organization in thread-local storage
    6. Logs all context changes for audit trail
    7. Handles OCM special access patterns
    8. Cleans up thread-local after response

    URL Pattern:
        /moa/OOBC/... → Sets organization to OOBC
        /moa/MOH/...  → Sets organization to MOH
        /...          → Uses user's primary organization or session

    Access Control:
        - User must have active OrganizationMembership
        - Superusers can access any organization
        - OCM users have read-only cross-organization access
        - Anonymous users: no organization context
        - Unauthenticated requests: organization required for MOA URLs

    Thread Safety:
        - Each request gets its own thread-local context
        - Automatic cleanup prevents memory leaks
        - Supports concurrent requests with different organizations
    """

    def __init__(self, get_response):
        """Initialize middleware with response handler."""
        self.get_response = get_response
        self._request_start_time = {}

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and set organization context with comprehensive logging.

        Args:
            request: HttpRequest instance

        Returns:
            HttpResponse instance
        """
        # Store request start time for performance monitoring
        request._org_context_start = time.time()

        # Initialize thread-local context for this request
        self._init_thread_context(request)

        try:
            # Step 1: Handle OBCMS mode (auto-inject default organization)
            if is_obcms_mode():
                organization = self._handle_obcms_mode(request)
            else:
                # Step 2: Extract organization from URL or user context
                organization = self._extract_organization_context(request)

            # Step 3: Set organization on request and thread-local
            request.organization = organization
            self._set_thread_organization(organization, request)

            # Step 4: Log context change
            self._log_organization_context_change(organization, request)

            # Step 5: Process request
            response = self.get_response(request)

            # Step 6: Log request completion
            self._log_request_completion(request, response)

            return response

        except Exception as e:
            # Log error and re-raise
            self._log_context_error(request, e)
            raise
        finally:
            # Step 7: Cleanup thread-local storage
            self._cleanup_thread_context()

    def _init_thread_context(self, request: HttpRequest):
        """Initialize thread-local context for this request."""
        _thread_context.request_id = id(request)
        _thread_context.user_id = request.user.id if request.user.is_authenticated else None
        _thread_context.ip_address = self._get_client_ip(request)
        _thread_context.user_agent = request.META.get('HTTP_USER_AGENT', '')[:200]
        _thread_context.start_time = time.time()

    def _handle_obcms_mode(self, request: HttpRequest) -> Optional[Organization]:
        """
        Handle OBCMS mode by auto-injecting default OOBC organization.

        In OBCMS mode, all requests automatically use the default OOBC organization.
        """
        from organizations.utils import get_or_create_default_organization

        organization, _ = get_or_create_default_organization()

        # Log OBCMS mode context
        audit_logger.info(
            f'OBCMS mode: Using default organization {organization.code} '
            f'for user: {request.user.username if request.user.is_authenticated else "anonymous"}'
        )

        return organization

    def _extract_organization_context(self, request: HttpRequest) -> Optional[Organization]:
        """Extract organization context from URL, session, or user."""
        # Step 1: Extract organization code from URL
        org_code = self._extract_org_code_from_url(request.path)
        organization = None

        if org_code:
            # URL specifies organization: /moa/<ORG_CODE>/...
            organization = self._get_organization_from_code(org_code)

            if not organization:
                # Invalid organization code
                security_logger.warning(
                    f'Invalid organization code attempted: {org_code} '
                    f'by user: {request.user.username if request.user.is_authenticated else "anonymous"} '
                    f'from IP: {self._get_client_ip(request)}'
                )
                raise PermissionDenied(f'Organization not found: {org_code}')

            # Verify access
            if not self._user_can_access_organization(request.user, organization):
                security_logger.warning(
                    f'Unauthorized access attempt to {organization.code} '
                    f'by user: {request.user.username if request.user.is_authenticated else "anonymous"} '
                    f'from IP: {self._get_client_ip(request)}'
                )
                raise PermissionDenied(
                    f'You do not have access to {organization.name}. '
                    f'Please contact your system administrator.'
                )

            # Store in session for persistence
            request.session['selected_organization_id'] = organization.id

        else:
            # No org in URL: try session, then primary organization
            if request.user.is_authenticated:
                organization = self._get_user_organization(request)

        return organization

    def _set_thread_organization(self, organization: Optional[Organization], request: HttpRequest):
        """Set organization in thread-local storage and update scoped context."""
        if organization:
            set_current_organization(organization)

            # Store additional context in thread-local
            _thread_context.organization_id = organization.id
            _thread_context.organization_code = organization.code
            _thread_context.is_ocm_user = self._is_ocm_user(request.user, organization)

            logger.debug(
                f'Organization context set: {organization.code} '
                f'for user: {request.user.username if request.user.is_authenticated else "anonymous"} '
                f'OCM: {_thread_context.is_ocm_user}'
            )
        else:
            clear_current_organization()

            # Clear thread-local organization context
            if hasattr(_thread_context, 'organization_id'):
                delattr(_thread_context, 'organization_id')
            if hasattr(_thread_context, 'organization_code'):
                delattr(_thread_context, 'organization_code')
            _thread_context.is_ocm_user = False

    def _log_organization_context_change(self, organization: Optional[Organization], request: HttpRequest):
        """Log organization context changes for audit trail."""
        if organization:
            audit_logger.info(
                f'Organization context set | '
                f'Org: {organization.code} ({organization.id}) | '
                f'User: {request.user.username if request.user.is_authenticated else "anonymous"} | '
                f'IP: {self._get_client_ip(request)} | '
                f'Path: {request.path} | '
                f'OCM: {_thread_context.is_ocm_user} | '
                f'Mode: {"OBCMS" if is_obcms_mode() else "BMMS"}'
            )
        else:
            audit_logger.info(
                f'No organization context | '
                f'User: {request.user.username if request.user.is_authenticated else "anonymous"} | '
                f'IP: {self._get_client_ip(request)} | '
                f'Path: {request.path} | '
                f'Mode: {"OBCMS" if is_obcms_mode() else "BMMS"}'
            )

    def _log_request_completion(self, request: HttpRequest, response: HttpResponse):
        """Log request completion with performance metrics."""
        if hasattr(request, '_org_context_start'):
            duration = time.time() - request._org_context_start

            log_level = 'WARNING' if response.status_code >= 400 else 'INFO'

            getattr(audit_logger, log_level.lower())(
                f'Request completed | '
                f'Status: {response.status_code} | '
                f'Duration: {duration:.3f}s | '
                f'Org: {getattr(_thread_context, "organization_code", "None")} | '
                f'User: {request.user.username if request.user.is_authenticated else "anonymous"}'
            )

    def _log_context_error(self, request: HttpRequest, error: Exception):
        """Log context setting errors."""
        security_logger.error(
            f'Organization context error | '
            f'Error: {str(error)} | '
            f'User: {request.user.username if request.user.is_authenticated else "anonymous"} | '
            f'IP: {self._get_client_ip(request)} | '
            f'Path: {request.path}'
        )

    def _cleanup_thread_context(self):
        """Clean up thread-local storage to prevent memory leaks."""
        try:
            clear_current_organization()

            # Clear all thread-local attributes
            attrs_to_clear = [
                'request_id', 'user_id', 'ip_address', 'user_agent',
                'start_time', 'organization_id', 'organization_code', 'is_ocm_user'
            ]

            for attr in attrs_to_clear:
                if hasattr(_thread_context, attr):
                    delattr(_thread_context, attr)

        except Exception as e:
            logger.error(f'Error cleaning up thread context: {e}')

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address with proxy support."""
        # Check for forwarded headers
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()

        # Check for Cloudflare
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip

        # Fall back to remote address
        return request.META.get('REMOTE_ADDR', 'Unknown')

    def _is_ocm_user(self, user, organization: Optional[Organization] = None) -> bool:
        """Check if user is from Office of Chief Minister (OCM)."""
        if not user.is_authenticated:
            return False

        # Superusers have OCM-like access
        if user.is_superuser:
            return True

        # Check user type
        if hasattr(user, 'user_type') and user.user_type == 'cm_office':
            return True

        # Check organization membership
        if organization and hasattr(user, 'organization_memberships'):
            from django.conf import settings
            ocm_code = getattr(settings, 'RBAC_SETTINGS', {}).get('OCM_ORGANIZATION_CODE', 'OCM')

            return user.organization_memberships.filter(
                organization__code__iexact=ocm_code,
                is_active=True
            ).exists()

        return False

    def _extract_org_code_from_url(self, path: str) -> Optional[str]:
        """
        Extract organization code from URL path.

        URL Pattern: /moa/<ORG_CODE>/...

        Args:
            path: URL path string

        Returns:
            Organization code (uppercase) or None

        Examples:
            /moa/OOBC/dashboard/ → 'OOBC'
            /moa/moh/assessments/ → 'MOH'
            /dashboard/ → None
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
        - OCM users: read-only access to all organizations
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

        # OCM users have read-only access to all organizations
        if self._is_ocm_user(user, organization):
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

    Args:
        request: HttpRequest instance

    Returns:
        dict: Context with organization data
    """
    organization = getattr(request, 'organization', None)

    if organization:
        return {
            'current_organization': organization,
            'organization_code': organization.code,
            'organization_name': organization.name,
            'enabled_modules': organization.enabled_modules,
        }

    return {
        'current_organization': None,
        'organization_code': None,
        'organization_name': None,
        'enabled_modules': [],
    }


# ========== THREAD-LOCAL UTILITIES ==========


def get_thread_context() -> Dict[str, Any]:
    """
    Get current thread-local organization context.

    Returns:
        Dict with thread context data or empty dict
    """
    context = {}

    if hasattr(_thread_context, 'organization_id'):
        context['organization_id'] = _thread_context.organization_id
    if hasattr(_thread_context, 'organization_code'):
        context['organization_code'] = _thread_context.organization_code
    if hasattr(_thread_context, 'is_ocm_user'):
        context['is_ocm_user'] = _thread_context.is_ocm_user
    if hasattr(_thread_context, 'user_id'):
        context['user_id'] = _thread_context.user_id
    if hasattr(_thread_context, 'request_id'):
        context['request_id'] = _thread_context.request_id
    if hasattr(_thread_context, 'ip_address'):
        context['ip_address'] = _thread_context.ip_address

    return context


def is_ocm_context() -> bool:
    """
    Check if current thread context is OCM user.

    Returns:
        True if current user is OCM, False otherwise
    """
    return getattr(_thread_context, 'is_ocm_user', False)


def get_current_organization_id() -> Optional[int]:
    """
    Get current organization ID from thread-local context.

    Returns:
        Organization ID or None
    """
    return getattr(_thread_context, 'organization_id', None)


def get_current_organization_code() -> Optional[str]:
    """
    Get current organization code from thread-local context.

    Returns:
        Organization code or None
    """
    return getattr(_thread_context, 'organization_code', None)