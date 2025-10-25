"""
OBCMSOrganizationMiddleware for BMMS embedded architecture.

This middleware auto-injects the default OOBC organization in OBCMS mode,
ensuring request.organization is always available without URL extraction.

Architecture:
- OBCMS Mode: Auto-inject OOBC (this middleware)
- BMMS Mode: Skip, let OrganizationMiddleware extract from URL

Design Decisions:
- Runs BEFORE OrganizationMiddleware in middleware chain
- Only operates in OBCMS mode (is_obcms_mode() == True)
- Ensures default organization exists on initialization
- Sets request.organization for all requests in OBCMS mode
- In BMMS mode, this middleware is a no-op (pass-through)

References:
- docs/plans/bmms/implementation/BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md
- docs/plans/bmms/implementation/tasks/phase3_middleware.txt
"""

import logging
from typing import Callable

from django.http import HttpRequest, HttpResponse

from obc_management.settings.bmms_config import is_obcms_mode
from organizations.utils import ensure_default_organization_exists, get_default_organization
from organizations.models.scoped import set_current_organization, clear_current_organization

logger = logging.getLogger(__name__)


class OBCMSOrganizationMiddleware:
    """
    Auto-inject OOBC organization in OBCMS mode.

    This middleware ensures that in OBCMS (single-tenant) mode, every request
    automatically has the default OOBC organization set in request.organization.

    In BMMS (multi-tenant) mode, this middleware does nothing and lets
    OrganizationMiddleware handle organization extraction from URLs.

    Middleware Order:
        1. AuthenticationMiddleware (Django built-in)
        2. OBCMSOrganizationMiddleware (this) - Auto-inject OOBC in OBCMS mode
        3. OrganizationMiddleware - Extract org from URL in BMMS mode

    Usage:
        MIDDLEWARE = [
            ...
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware',
            'organizations.middleware.OrganizationMiddleware',
            ...
        ]
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """
        Initialize middleware.

        On initialization:
        - Store response handler
        - Ensure default organization exists in OBCMS mode

        Args:
            get_response: Next middleware/view in chain
        """
        from django.apps import apps

        self.get_response = get_response

        # Ensure OOBC exists on startup (OBCMS mode only)
        # Don't access database during app initialization
        if is_obcms_mode() and apps.ready:
            try:
                org = ensure_default_organization_exists()
                if org:
                    logger.info(
                        f'OBCMSOrganizationMiddleware initialized: {org.code} - {org.name}'
                    )
            except Exception as e:
                logger.error(
                    f'Failed to ensure default organization exists: {e}',
                    exc_info=True
                )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and inject OOBC organization in OBCMS mode.

        Flow:
        1. Check mode: if BMMS mode, skip (pass-through)
        2. If OBCMS mode, load default organization
        3. Set request.organization attribute
        4. Set thread-local organization context
        5. Process request
        6. Cleanup thread-local storage

        Args:
            request: HttpRequest instance

        Returns:
            HttpResponse instance
        """
        from django.apps import apps

        # Skip in BMMS mode - let OrganizationMiddleware handle it
        if not is_obcms_mode():
            return self.get_response(request)

        # Don't access database during app initialization
        if not apps.ready:
            return self.get_response(request)

        # OBCMS mode: auto-inject OOBC
        try:
            organization = get_default_organization()

            # Set on request
            request.organization = organization

            # Set thread-local for model queries
            set_current_organization(organization)

            logger.debug(
                f'OBCMS mode: Auto-injected organization {organization.code} '
                f'for user {request.user.username if request.user.is_authenticated else "anonymous"}'
            )

        except Exception as e:
            logger.error(
                f'Failed to load default organization in OBCMS mode: {e}',
                exc_info=True
            )
            # Set to None rather than failing the request
            request.organization = None
            clear_current_organization()

        # Process request
        response = self.get_response(request)

        # Cleanup thread-local storage
        # Note: OrganizationMiddleware will also call this, but it's safe to call multiple times
        clear_current_organization()

        return response
