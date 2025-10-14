"""
OCM Permission Classes

DRF permission classes for OCM views and API endpoints.
"""
import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class OCMReadOnlyPermission(BasePermission):
    """
    Permission class that allows only safe methods (GET, HEAD, OPTIONS).

    Enforces read-only access at the DRF permission level.
    """

    def has_permission(self, request, view):
        """
        Check if request method is safe (read-only).

        Args:
            request: The HTTP request
            view: The view being accessed

        Returns:
            bool: True if method is safe, False otherwise
        """
        is_safe = request.method in ['GET', 'HEAD', 'OPTIONS']

        if not is_safe:
            logger.warning(
                f"OCM read-only violation: User {request.user.username} "
                f"attempted {request.method} on {request.path}"
            )

        return is_safe


class IsOCMUser(BasePermission):
    """
    Permission class that checks if user has active OCM access.

    Staff and superusers bypass this check.
    """

    def has_permission(self, request, view):
        """
        Check if user has active OCM access.

        Args:
            request: The HTTP request
            view: The view being accessed

        Returns:
            bool: True if user has OCM access, False otherwise
        """
        # Staff and superusers bypass OCM access requirement
        if request.user.is_staff or request.user.is_superuser:
            logger.info(f"Staff/superuser {request.user.username} bypassing OCM access check")
            return True

        # Check for active OCM access
        has_access = (
            hasattr(request.user, 'ocm_access') and
            request.user.ocm_access.is_active
        )

        if not has_access:
            logger.warning(
                f"OCM access denied: User {request.user.username} "
                f"does not have active OCM access"
            )

        return has_access


class IsOCMAnalyst(BasePermission):
    """
    Permission class that checks if user has analyst or executive level access.

    Required for report generation views.
    """

    def has_permission(self, request, view):
        """
        Check if user has analyst or executive level access.

        Args:
            request: The HTTP request
            view: The view being accessed

        Returns:
            bool: True if user is analyst or executive, False otherwise
        """
        # Staff and superusers bypass
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check for analyst/executive level
        if not hasattr(request.user, 'ocm_access'):
            return False

        ocm_access = request.user.ocm_access

        if not ocm_access.is_active:
            return False

        is_analyst = ocm_access.access_level in ['analyst', 'executive']

        if not is_analyst:
            logger.warning(
                f"OCM analyst permission denied: User {request.user.username} "
                f"has level {ocm_access.access_level}, requires analyst or executive"
            )

        return is_analyst


class IsOCMExecutive(BasePermission):
    """
    Permission class that checks if user has executive level access.

    Required for data export views.
    """

    def has_permission(self, request, view):
        """
        Check if user has executive level access.

        Args:
            request: The HTTP request
            view: The view being accessed

        Returns:
            bool: True if user is executive, False otherwise
        """
        # Staff and superusers bypass
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check for executive level
        if not hasattr(request.user, 'ocm_access'):
            return False

        ocm_access = request.user.ocm_access

        if not ocm_access.is_active:
            return False

        is_executive = ocm_access.access_level == 'executive'

        if not is_executive:
            logger.warning(
                f"OCM executive permission denied: User {request.user.username} "
                f"has level {ocm_access.access_level}, requires executive"
            )

        return is_executive



class OCMReadOnlyAccess(BasePermission):
    """
    Combined permission class: OCM access + read-only enforcement.

    Use this on API views that need both OCM access and read-only enforcement.
    """

    def has_permission(self, request, view):
        """
        Check both OCM access and read-only method.

        Args:
            request: The HTTP request
            view: The view being accessed

        Returns:
            bool: True if user has OCM access and method is safe, False otherwise
        """
        # Check read-only first
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            logger.warning(
                f"OCM read-only violation: User {request.user.username} "
                f"attempted {request.method} on {request.path}"
            )
            return False

        # Staff and superusers bypass OCM access requirement
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check OCM access
        has_access = (
            hasattr(request.user, 'ocm_access') and
            request.user.ocm_access.is_active
        )

        if not has_access:
            logger.warning(
                f"OCM access denied: User {request.user.username} "
                f"does not have active OCM access"
            )

        return has_access
