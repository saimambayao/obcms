"""
DRF permission classes for RBAC.

Provides permission classes for Django REST Framework API views
integrating with the RBACService.
"""

from rest_framework import permissions
from common.services.rbac_service import RBACService


class HasFeatureAccess(permissions.BasePermission):
    """
    DRF permission class to check feature access.

    Usage:
        class CommunityViewSet(viewsets.ModelViewSet):
            permission_classes = [HasFeatureAccess]
            feature_code = 'communities.barangay_obc'
    """
    message = "You do not have access to this feature."

    def has_permission(self, request, view):
        """Check if user has feature access."""
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication required."
            return False

        # Get feature code from view
        feature_code = getattr(view, 'feature_code', None)
        if not feature_code:
            # If no feature code specified, allow access
            # (let other permission classes handle it)
            return True

        # Get organization context
        organization = RBACService.get_user_organization_context(request)

        # Check feature access
        has_access = RBACService.has_feature_access(
            request.user,
            feature_code,
            organization
        )

        if not has_access:
            feature_name = feature_code.split('.')[-1].replace('_', ' ').title()
            self.message = f"You do not have access to the {feature_name} feature."

        return has_access


class HasPermission(permissions.BasePermission):
    """
    DRF permission class to check a single permission.

    Usage:
        class CommunityViewSet(viewsets.ModelViewSet):
            permission_classes = [HasPermission]
            permission_code = 'communities.create_obc_community'
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        """Check if user has permission."""
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication required."
            return False

        # Get permission code from view
        permission_code = getattr(view, 'permission_code', None)
        if not permission_code:
            # If no permission code specified, allow access
            return True

        # Get organization context
        organization = RBACService.get_user_organization_context(request)

        # Check permission
        has_perm = RBACService.has_permission(
            request,
            permission_code,
            organization
        )

        if not has_perm:
            self.message = f"You do not have permission: {permission_code}"

        return has_perm

    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        # Default implementation delegates to has_permission
        # Override in subclasses for object-specific logic
        return self.has_permission(request, view)


class HasAnyPermission(permissions.BasePermission):
    """
    DRF permission class to check if user has ANY of multiple permissions (OR logic).

    Usage:
        class CommunityViewSet(viewsets.ModelViewSet):
            permission_classes = [HasAnyPermission]
            permissions_required = [
                'communities.edit_obc_community',
                'communities.manage_obc_community'
            ]
    """
    message = "You do not have any of the required permissions."

    def has_permission(self, request, view):
        """Check if user has any of the required permissions."""
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication required."
            return False

        # Get permissions from view
        permissions_required = getattr(view, 'permissions_required', None)
        if not permissions_required:
            # If no permissions specified, allow access
            return True

        if not isinstance(permissions_required, (list, tuple)):
            raise ValueError('permissions_required must be a list or tuple')

        # Get organization context
        organization = RBACService.get_user_organization_context(request)

        # Check if user has ANY of the required permissions
        has_any = any(
            RBACService.has_permission(request, perm, organization)
            for perm in permissions_required
        )

        if not has_any:
            self.message = f"You need one of: {', '.join(permissions_required)}"

        return has_any


class HasAllPermissions(permissions.BasePermission):
    """
    DRF permission class to check if user has ALL of multiple permissions (AND logic).

    Usage:
        class CommunityViewSet(viewsets.ModelViewSet):
            permission_classes = [HasAllPermissions]
            permissions_required = [
                'communities.view_obc_community',
                'communities.edit_obc_community'
            ]
    """
    message = "You do not have all required permissions."

    def has_permission(self, request, view):
        """Check if user has all required permissions."""
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication required."
            return False

        # Get permissions from view
        permissions_required = getattr(view, 'permissions_required', None)
        if not permissions_required:
            # If no permissions specified, allow access
            return True

        if not isinstance(permissions_required, (list, tuple)):
            raise ValueError('permissions_required must be a list or tuple')

        # Get organization context
        organization = RBACService.get_user_organization_context(request)

        # Check if user has ALL required permissions
        missing_perms = []
        for perm in permissions_required:
            if not RBACService.has_permission(request, perm, organization):
                missing_perms.append(perm)

        if missing_perms:
            self.message = f"Missing permissions: {', '.join(missing_perms)}"
            return False

        return True
