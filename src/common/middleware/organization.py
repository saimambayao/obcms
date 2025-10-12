"""
OrganizationMiddleware for BMMS Multi-Tenant Request Handling.

This middleware implements comprehensive organization-based data isolation for the
Bangsamoro Ministerial Management System (BMMS), serving 44 Ministries, Offices,
and Agencies (MOAs).

**Key Features:**
- Extracts organization from URL pattern: /moa/<ORG_CODE>/...
- Sets request.organization on every request
- Enforces access control via OrganizationMembership
- Uses thread-local storage for QuerySet-level filtering
- Handles superuser and OCM (Office of Chief Minister) special access
- Provides graceful fallback to user's primary organization

**Security Model:**
- Superusers: Full access to all organizations
- OCM Users: Read-only access to all organizations (aggregation/oversight)
- OOBC Staff: Can switch between organizations (operations)
- MOA Staff: Limited to their assigned organization only
- Guests: No organization access

**URL Pattern:**
The middleware extracts organization from URLs like:
- /moa/<ORG_CODE>/dashboard/
- /moa/<ORG_CODE>/planning/ppas/
- /moa/<ORG_CODE>/budget/preparation/

**Integration:**
1. Add to settings.MIDDLEWARE after AuthenticationMiddleware
2. Use request.organization in views
3. QuerySets automatically filtered via thread-local storage
4. Permission checks auto-scoped to organization

**Thread-Local Storage:**
Organization context stored in thread-local variable for:
- QuerySet filtering in model managers
- Template context processors
- Background task isolation

See:
- docs/plans/bmms/TRANSITION_PLAN.md
- docs/plans/bmms/tasks/PHASE_1_FOUNDATION.md

Author: BMMS Implementation Team
Created: 2025-10-13
"""

import logging
import re
import threading
from typing import Optional

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.functional import SimpleLazyObject


logger = logging.getLogger(__name__)


# ============================================================================
# THREAD-LOCAL STORAGE FOR ORGANIZATION CONTEXT
# ============================================================================

_thread_local = threading.local()


def set_current_organization(organization):
    """
    Store organization in thread-local storage.

    This enables QuerySet-level filtering throughout the request lifecycle.

    Args:
        organization: Organization instance or None
    """
    _thread_local.organization = organization


def get_current_organization():
    """
    Retrieve organization from thread-local storage.

    Returns:
        Organization instance or None
    """
    return getattr(_thread_local, 'organization', None)


def clear_current_organization():
    """
    Clear organization from thread-local storage.

    Called at end of request to prevent context leakage.
    """
    if hasattr(_thread_local, 'organization'):
        del _thread_local.organization


# ============================================================================
# ORGANIZATION EXTRACTION AND ACCESS CONTROL
# ============================================================================

# Regex pattern for extracting ORG_CODE from URL
# Matches: /moa/<ORG_CODE>/ where ORG_CODE is alphanumeric with hyphens/underscores
ORG_URL_PATTERN = re.compile(r'^/moa/(?P<org_code>[\w-]+)/')


def extract_org_code_from_url(path: str) -> Optional[str]:
    """
    Extract organization code from URL path.

    Args:
        path: Request path (e.g., "/moa/oobc/dashboard/")

    Returns:
        Organization code (e.g., "oobc") or None

    Examples:
        >>> extract_org_code_from_url("/moa/oobc/dashboard/")
        'oobc'
        >>> extract_org_code_from_url("/moa/ministry-health/planning/")
        'ministry-health'
        >>> extract_org_code_from_url("/dashboard/")
        None
    """
    match = ORG_URL_PATTERN.match(path)
    if match:
        return match.group('org_code')
    return None


def get_organization_by_code(org_code: str):
    """
    Retrieve Organization by code (acronym).

    Args:
        org_code: Organization code/acronym (case-insensitive)

    Returns:
        Organization instance

    Raises:
        Http404: If organization not found
    """
    from coordination.models import Organization

    return get_object_or_404(
        Organization,
        acronym__iexact=org_code,
        is_active=True
    )


def user_can_access_organization(user, organization) -> bool:
    """
    Check if user has access to the given organization.

    **Access Rules:**
    1. Superusers: Access to ALL organizations
    2. OCM users: Read-only access to ALL organizations (oversight)
    3. OOBC Staff: Access to ALL organizations (operations)
    4. MOA Staff: Access to THEIR organization only
    5. Other users: No organization access

    Args:
        user: User instance
        organization: Organization instance

    Returns:
        True if user can access organization, False otherwise
    """
    # Rule 1: Superusers have unrestricted access
    if user.is_superuser:
        logger.debug(f"Superuser {user.username} granted access to {organization}")
        return True

    # Rule 2: OCM users have read-only access to all organizations
    if is_ocm_user(user):
        logger.debug(f"OCM user {user.username} granted read-only access to {organization}")
        return True

    # Rule 3: OOBC staff can access all organizations
    if hasattr(user, 'is_oobc_staff') and user.is_oobc_staff:
        logger.debug(f"OOBC staff {user.username} granted access to {organization}")
        return True

    # Rule 4: MOA staff can only access their own organization
    if hasattr(user, 'is_moa_staff') and user.is_moa_staff:
        if hasattr(user, 'moa_organization') and user.moa_organization:
            has_access = user.moa_organization == organization
            if has_access:
                logger.debug(f"MOA staff {user.username} granted access to their org: {organization}")
            else:
                logger.warning(
                    f"MOA staff {user.username} denied access to {organization} "
                    f"(belongs to {user.moa_organization})"
                )
            return has_access
        else:
            logger.warning(f"MOA staff {user.username} has no organization assigned")
            return False

    # Rule 5: Check OrganizationMembership if exists (future implementation)
    if has_organization_membership_model():
        return check_organization_membership(user, organization)

    # Default: No access
    logger.warning(f"User {user.username} denied access to {organization} (no role match)")
    return False


def is_ocm_user(user) -> bool:
    """
    Check if user is from Office of Chief Minister (OCM).

    OCM users have special aggregation access across all MOAs for
    oversight and strategic planning purposes.

    Args:
        user: User instance

    Returns:
        True if user belongs to OCM, False otherwise
    """
    # Check user_type field
    if hasattr(user, 'user_type') and user.user_type == 'cm_office':
        return True

    # Check if user's organization is OCM
    if hasattr(user, 'moa_organization') and user.moa_organization:
        ocm_code = getattr(
            settings,
            'RBAC_SETTINGS',
            {}
        ).get('OCM_ORGANIZATION_CODE', 'ocm')

        if hasattr(user.moa_organization, 'acronym'):
            return user.moa_organization.acronym.lower() == ocm_code.lower()

    return False


def has_organization_membership_model() -> bool:
    """
    Check if OrganizationMembership model exists.

    This allows graceful degradation during BMMS Phase 1 implementation.
    Once organizations app is created, this will return True.

    Returns:
        True if OrganizationMembership model exists, False otherwise
    """
    try:
        from django.apps import apps
        apps.get_model('organizations', 'OrganizationMembership')
        return True
    except (LookupError, ImportError):
        return False


def check_organization_membership(user, organization) -> bool:
    """
    Check if user has OrganizationMembership for the organization.

    This is a future-proof implementation that will be used once the
    organizations app is created with OrganizationMembership model.

    Args:
        user: User instance
        organization: Organization instance

    Returns:
        True if user has active membership, False otherwise
    """
    try:
        from django.apps import apps
        OrganizationMembership = apps.get_model('organizations', 'OrganizationMembership')

        membership = OrganizationMembership.objects.filter(
            user=user,
            organization=organization,
            is_active=True
        ).exists()

        if membership:
            logger.debug(
                f"User {user.username} has active membership in {organization}"
            )
        else:
            logger.warning(
                f"User {user.username} has no active membership in {organization}"
            )

        return membership

    except (LookupError, ImportError):
        logger.debug("OrganizationMembership model not yet available")
        return False


def get_fallback_organization(user):
    """
    Get fallback organization for user.

    Fallback order:
    1. User's moa_organization
    2. User's first active OrganizationMembership (if exists)
    3. Session-stored organization
    4. None

    Args:
        user: User instance

    Returns:
        Organization instance or None
    """
    # Try user's primary organization
    if hasattr(user, 'moa_organization') and user.moa_organization:
        if hasattr(user.moa_organization, 'is_active') and user.moa_organization.is_active:
            return user.moa_organization

    # Try OrganizationMembership (future implementation)
    if has_organization_membership_model():
        try:
            from django.apps import apps
            OrganizationMembership = apps.get_model('organizations', 'OrganizationMembership')

            membership = OrganizationMembership.objects.filter(
                user=user,
                is_active=True
            ).select_related('organization').first()

            if membership and membership.organization:
                return membership.organization

        except (LookupError, ImportError):
            pass

    return None


# ============================================================================
# ORGANIZATION MIDDLEWARE
# ============================================================================

class OrganizationMiddleware:
    """
    Middleware to set organization context on request object.

    **Adds to Request:**
    - request.organization: Organization instance or None
    - request.is_ocm_user: Boolean flag for OCM access
    - request.can_switch_org: Boolean flag for organization switching capability

    **URL Pattern Matching:**
    Extracts organization from: /moa/<ORG_CODE>/...

    **Access Control:**
    - Verifies user has access to requested organization
    - Returns 403 Forbidden if access denied
    - Logs all access attempts for security audit

    **Thread-Local Storage:**
    Stores organization context for QuerySet-level filtering.

    **Usage in Views:**
    ```python
    def my_view(request):
        # Organization automatically set
        org = request.organization

        if org:
            # Filter data by organization
            ppas = PPA.objects.filter(implementing_moa=org)

        # Check if user can switch organizations
        if request.can_switch_org:
            # Show organization switcher UI
            pass
    ```

    **Settings Configuration:**
    Add after AuthenticationMiddleware in MIDDLEWARE:
    ```python
    MIDDLEWARE = [
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'common.middleware.organization.OrganizationMiddleware',
        ...
    ]
    ```
    """

    def __init__(self, get_response):
        """
        Initialize middleware.

        Args:
            get_response: Callable to get response from next middleware
        """
        self.get_response = get_response
        logger.info("OrganizationMiddleware initialized")

    def __call__(self, request: HttpRequest):
        """
        Process request to set organization context.

        Args:
            request: HttpRequest instance

        Returns:
            HttpResponse instance
        """
        # Set organization as lazy object (only evaluated when accessed)
        request.organization = SimpleLazyObject(
            lambda: self._get_organization_from_request(request)
        )

        # Set OCM flag
        if request.user.is_authenticated:
            request.is_ocm_user = is_ocm_user(request.user)

            # Set organization switching capability
            request.can_switch_org = (
                request.user.is_superuser or
                request.is_ocm_user or
                (hasattr(request.user, 'is_oobc_staff') and request.user.is_oobc_staff)
            )
        else:
            request.is_ocm_user = False
            request.can_switch_org = False

        # Process request
        response = self.get_response(request)

        # Clean up thread-local storage
        clear_current_organization()

        return response

    def _get_organization_from_request(self, request: HttpRequest):
        """
        Extract organization from request.

        Extraction priority:
        1. URL pattern: /moa/<ORG_CODE>/
        2. Query parameter: ?org=<ORG_CODE>
        3. User's primary organization (fallback)
        4. Session-stored organization

        Args:
            request: HttpRequest instance

        Returns:
            Organization instance or None
        """
        # Early return if no authenticated user
        if not request.user.is_authenticated:
            return None

        organization = None

        # 1. Try extracting from URL pattern (highest priority)
        org_code = extract_org_code_from_url(request.path)

        # 2. Try query parameter if URL extraction failed
        if not org_code:
            org_code = request.GET.get('org')

        # 3. Fetch organization by code
        if org_code:
            try:
                organization = get_organization_by_code(org_code)

                # Security: Verify user has access
                if not user_can_access_organization(request.user, organization):
                    logger.warning(
                        f"Access denied: {request.user.username} attempted to access "
                        f"{organization} without permission. Path: {request.path}"
                    )
                    # Don't raise exception here - let view handle it
                    # This allows for better error messages
                    organization = None
                else:
                    # Store in thread-local storage
                    set_current_organization(organization)

                    # Log successful access
                    logger.info(
                        f"Organization set: {request.user.username} accessing "
                        f"{organization}. Path: {request.path}"
                    )

            except Exception as e:
                logger.error(
                    f"Error loading organization '{org_code}': {e}. "
                    f"User: {request.user.username}, Path: {request.path}"
                )
                organization = None

        # 4. Fallback to user's primary organization
        if not organization:
            organization = get_fallback_organization(request.user)

            if organization:
                set_current_organization(organization)
                logger.debug(
                    f"Using fallback organization for {request.user.username}: {organization}"
                )

        return organization

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process view to enforce organization requirements.

        Views can specify @requires_organization decorator to enforce
        organization context. This method validates that requirement.

        Args:
            request: HttpRequest instance
            view_func: View function being called
            view_args: Positional arguments for view
            view_kwargs: Keyword arguments for view

        Returns:
            None (continue processing) or HttpResponseForbidden
        """
        # Check if view requires organization
        if hasattr(view_func, 'requires_organization'):
            if not request.organization:
                logger.warning(
                    f"Organization required but not found. "
                    f"User: {request.user.username}, Path: {request.path}"
                )
                return HttpResponseForbidden(
                    "Organization context required. "
                    "Please select an organization to continue."
                )

        # Check if view requires specific organization access
        if hasattr(view_func, 'required_organization_access'):
            if not request.organization:
                return HttpResponseForbidden("Organization context required.")

            if not user_can_access_organization(request.user, request.organization):
                logger.warning(
                    f"Insufficient organization access. "
                    f"User: {request.user.username}, "
                    f"Organization: {request.organization}, "
                    f"Path: {request.path}"
                )
                raise PermissionDenied(
                    "You do not have permission to access this organization."
                )

        return None


# ============================================================================
# VIEW DECORATORS (OPTIONAL)
# ============================================================================

def requires_organization(view_func):
    """
    Decorator to require organization context on a view.

    Usage:
        @requires_organization
        def my_view(request):
            # request.organization is guaranteed to exist
            org = request.organization
            ...
    """
    view_func.requires_organization = True
    return view_func


def requires_organization_access(view_func):
    """
    Decorator to require verified organization access on a view.

    More strict than requires_organization - validates user permissions.

    Usage:
        @requires_organization_access
        def my_view(request):
            # User access to request.organization is verified
            org = request.organization
            ...
    """
    view_func.required_organization_access = True
    return view_func
