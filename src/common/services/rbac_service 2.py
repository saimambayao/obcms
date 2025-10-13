"""
RBAC Service for BMMS Multi-Tenant Organization Context.

Provides organization-aware permission checking and resource access control.
Integrates with the new comprehensive RBAC models (Feature, Permission, Role, etc.)
and maintains backward compatibility with existing MOA RBAC system.

Features:
- Feature-based permission checks (navbar, modules, actions)
- Role-based access control (Admin, Manager, Staff, Viewer)
- Organization-scoped permissions (MOA A cannot access MOA B)
- OCM aggregation access (read-only across all MOAs)
- Multi-organization access for OOBC staff
- Caching for performance
- Integration with middleware organization context

See:
- docs/plans/bmms/TRANSITION_PLAN.md
- docs/improvements/NAVBAR_RBAC_ANALYSIS.md
- src/common/rbac_models.py
"""

from typing import Optional, List, Set
from django.core.cache import cache
from django.db import models
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class RBACService:
    """
    Role-Based Access Control service with organization context.

    Provides:
    - Organization-scoped permission checks
    - Multi-organization access control
    - OCM special access (read-only aggregation)
    - Permission caching for performance
    """

    # Cache timeout in seconds (5 minutes)
    CACHE_TIMEOUT = 300

    @classmethod
    def _get_cache_key(cls, user_id: int, feature_code: str, org_id: Optional[str] = None) -> str:
        """Generate cache key for permission check."""
        if org_id:
            return f"rbac:user:{user_id}:feature:{feature_code}:org:{org_id}"
        return f"rbac:user:{user_id}:feature:{feature_code}"

    @classmethod
    def get_user_organization_context(cls, request: HttpRequest):
        """
        Get organization context from request.

        Returns organization from:
        1. request.organization (set by middleware)
        2. User's default organization
        3. None (no organization context)
        """
        if hasattr(request, 'organization'):
            return request.organization

        if request.user.is_authenticated and hasattr(request.user, 'moa_organization'):
            return request.user.moa_organization

        return None

    @classmethod
    def has_permission(
        cls,
        request: HttpRequest,
        feature_code: str,
        organization = None,
        use_cache: bool = True
    ) -> bool:
        """
        Check if user has permission for feature in organization context.

        Args:
            request: HTTP request with user and organization context
            feature_code: Feature permission code (e.g., 'communities.view_obc_community')
            organization: Optional organization override (uses request.organization by default)
            use_cache: Whether to use cached permissions

        Returns:
            bool: True if user has permission

        Rules:
        - Superusers: Full access
        - OCM users: Read-only access to all organizations
        - OOBC staff: Full access to all organizations
        - MOA staff: Access to their organization only
        """
        if not request.user.is_authenticated:
            return False

        # Superusers bypass all checks
        if request.user.is_superuser:
            return True

        # Get organization context
        if organization is None:
            organization = cls.get_user_organization_context(request)

        # Build cache key
        org_id = str(organization.id) if organization else None
        cache_key = cls._get_cache_key(request.user.id, feature_code, org_id)

        # Check cache
        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Perform permission check
        has_perm = cls._check_permission(request.user, feature_code, organization)

        # Cache result
        if use_cache:
            cache.set(cache_key, has_perm, cls.CACHE_TIMEOUT)

        return has_perm

    @classmethod
    def _check_permission(cls, user, feature_code: str, organization) -> bool:
        """
        Internal permission check logic.

        Handles:
        - OCM aggregation access (read-only)
        - OOBC staff access (full)
        - MOA staff access (organization-scoped)
        """
        from common.middleware.organization_context import is_ocm_user

        # Parse feature code
        parts = feature_code.split('.')
        if len(parts) != 2:
            return False

        app_label, action_perm = parts
        is_read_action = action_perm.startswith('view_') or action_perm == 'read'

        # OCM users: Read-only access to all organizations
        if is_ocm_user(user):
            return is_read_action

        # OOBC staff: Full access to all organizations
        if user.is_oobc_staff:
            return True

        # MOA staff: Organization-scoped access
        if user.is_moa_staff:
            # No access if no organization context
            if not organization:
                return False

            # Can only access their own organization
            if user.moa_organization and user.moa_organization == organization:
                # Check specific app permissions
                if app_label == 'mana':
                    return False  # MOA staff cannot access MANA

                # Default: allow access to their organization's data
                return True

            return False

        # Default: no access
        return False

    @classmethod
    def get_organizations_with_access(cls, user) -> List:
        """
        Get list of organizations user can access.

        Returns:
            List of Organization objects user can access
        """
        from coordination.models import Organization
        from common.middleware.organization_context import is_ocm_user

        if not user.is_authenticated:
            return []

        # Superusers and OOBC staff: All organizations
        if user.is_superuser or user.is_oobc_staff:
            return list(Organization.objects.filter(
                organization_type='bmoa',
                is_active=True
            ))

        # OCM users: All organizations (read-only)
        if is_ocm_user(user):
            return list(Organization.objects.filter(
                organization_type='bmoa',
                is_active=True
            ))

        # MOA staff: Their organization only
        if user.is_moa_staff and user.moa_organization:
            return [user.moa_organization]

        return []

    @classmethod
    def invalidate_user_cache(cls, user_id: int):
        """
        Invalidate all cached permissions for a user.

        Call this when user permissions change.
        """
        # Clear all permission caches for this user
        # Note: This is a simple implementation
        # For production, consider more sophisticated cache invalidation
        cache_pattern = f"rbac:user:{user_id}:*"
        # Django cache doesn't support pattern deletion by default
        # This is a placeholder - implement based on your cache backend
        pass

    @classmethod
    def can_switch_organization(cls, user) -> bool:
        """
        Check if user can switch between organizations.

        Returns:
            bool: True if user can switch organizations
        """
        if not user.is_authenticated:
            return False

        # Superusers, OOBC staff, and OCM can switch
        if user.is_superuser or user.is_oobc_staff:
            return True

        from common.middleware.organization_context import is_ocm_user
        if is_ocm_user(user):
            return True

        # MOA staff cannot switch (locked to their organization)
        return False

    @classmethod
    def get_permission_context(cls, request: HttpRequest) -> dict:
        """
        Get complete permission context for templates.

        Returns:
            dict: Permission context with organization info
        """
        if not request.user.is_authenticated:
            return {
                'has_organization_context': False,
                'current_organization': None,
                'can_switch_organization': False,
                'available_organizations': [],
                'is_ocm_user': False,
            }

        organization = cls.get_user_organization_context(request)
        available_orgs = cls.get_organizations_with_access(request.user)

        from common.middleware.organization_context import is_ocm_user

        return {
            'has_organization_context': organization is not None,
            'current_organization': organization,
            'can_switch_organization': cls.can_switch_organization(request.user),
            'available_organizations': available_orgs,
            'is_ocm_user': is_ocm_user(request.user),
            'is_oobc_staff': request.user.is_oobc_staff,
            'is_moa_staff': request.user.is_moa_staff,
        }

    # ========== NEW RBAC MODEL INTEGRATION ==========

    @classmethod
    def has_feature_access(
        cls,
        user,
        feature_key: str,
        organization = None,
        use_cache: bool = True
    ) -> bool:
        """
        Check if user can access a feature (navbar item, module, etc.).

        Args:
            user: User object
            feature_key: Feature identifier (e.g., 'communities.barangay_obc')
            organization: Optional organization context
            use_cache: Whether to use cached results

        Returns:
            bool: True if user can access the feature

        Examples:
            has_feature_access(user, 'communities.barangay_obc')
            has_feature_access(user, 'mana.regional_overview', organization)
        """
        if not user.is_authenticated:
            return False

        # Superusers bypass all checks
        if user.is_superuser:
            return True

        # Build cache key
        org_id = str(organization.id) if organization else None
        cache_key = cls._get_cache_key(user.id, f"feature:{feature_key}", org_id)

        # Check cache
        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Perform feature access check
        has_access = cls._check_feature_access(user, feature_key, organization)

        # Cache result
        if use_cache:
            cache.set(cache_key, has_access, cls.CACHE_TIMEOUT)

        return has_access

    @classmethod
    def _check_feature_access(cls, user, feature_key: str, organization) -> bool:
        """
        Internal feature access check using RBAC models.

        Checks:
        1. Feature exists and is active
        2. User has role-based permission for feature
        3. User has direct permission override
        4. Organization context is valid
        """
        try:
            from common.rbac_models import Feature, UserRole, UserPermission

            # Get feature
            feature = Feature.objects.filter(
                feature_key=feature_key,
                is_active=True
            ).first()

            if not feature:
                # Feature not found - fall back to legacy permission check
                return cls._check_permission(user, feature_key, organization)

            # Check if feature is organization-specific
            if feature.organization and organization:
                if feature.organization != organization:
                    return False

            # Get user's permissions for this feature
            user_perms = cls.get_user_permissions(user, organization)

            # Check if user has any permission for this feature
            feature_perms = feature.permissions.filter(
                id__in=user_perms,
                is_active=True
            )

            return feature_perms.exists()

        except Exception:
            # Fall back to legacy permission check
            return cls._check_permission(user, feature_key, organization)

    @classmethod
    def get_user_permissions(cls, user, organization = None) -> Set:
        """
        Get all permission IDs for a user (from roles and direct grants).

        Args:
            user: User object
            organization: Optional organization context

        Returns:
            Set of permission IDs user has access to

        Logic:
        1. Get all active roles for user (in organization context)
        2. Get all permissions from those roles
        3. Add direct user permissions
        4. Remove explicitly denied permissions
        5. Filter expired permissions
        """
        if not user.is_authenticated:
            return set()

        try:
            from common.rbac_models import UserRole, UserPermission, RolePermission

            permission_ids = set()
            now = timezone.now()

            # Get user's active roles (in organization context)
            user_roles = UserRole.objects.filter(
                user=user,
                is_active=True
            )

            # Filter by organization if provided
            if organization:
                user_roles = user_roles.filter(
                    models.Q(organization=organization) | models.Q(organization__isnull=True)
                )

            # Filter out expired roles
            user_roles = user_roles.filter(
                models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
            )

            # Get permissions from roles
            for user_role in user_roles:
                role_perms = RolePermission.objects.filter(
                    role=user_role.role,
                    is_active=True,
                    is_granted=True
                ).filter(
                    models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
                ).values_list('permission_id', flat=True)

                permission_ids.update(role_perms)

            # Get direct user permissions (grants)
            direct_grants = UserPermission.objects.filter(
                user=user,
                is_active=True,
                is_granted=True
            )

            # Filter by organization if provided
            if organization:
                direct_grants = direct_grants.filter(
                    models.Q(organization=organization) | models.Q(organization__isnull=True)
                )

            # Filter expired
            direct_grants = direct_grants.filter(
                models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
            ).values_list('permission_id', flat=True)

            permission_ids.update(direct_grants)

            # Remove explicitly denied permissions
            direct_denials = UserPermission.objects.filter(
                user=user,
                is_active=True,
                is_granted=False
            )

            if organization:
                direct_denials = direct_denials.filter(
                    models.Q(organization=organization) | models.Q(organization__isnull=True)
                )

            direct_denials = direct_denials.filter(
                models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
            ).values_list('permission_id', flat=True)

            permission_ids.difference_update(direct_denials)

            return permission_ids

        except Exception:
            # Fall back to empty set
            return set()

    @classmethod
    def get_accessible_features(cls, user, organization = None) -> List:
        """
        Get all features user can access.

        Args:
            user: User object
            organization: Optional organization context

        Returns:
            List of Feature objects user can access
        """
        if not user.is_authenticated:
            return []

        try:
            from common.rbac_models import Feature

            # Superusers see all features
            if user.is_superuser:
                return list(Feature.objects.filter(is_active=True))

            # Get user's permission IDs
            user_perms = cls.get_user_permissions(user, organization)

            if not user_perms:
                return []

            # Get features that have permissions in user's permission set
            features = Feature.objects.filter(
                permissions__id__in=user_perms,
                permissions__is_active=True,
                is_active=True
            ).distinct()

            # Filter by organization if provided
            if organization:
                features = features.filter(
                    models.Q(organization=organization) | models.Q(organization__isnull=True)
                )

            return list(features.order_by('module', 'sort_order', 'name'))

        except Exception:
            return []

    @classmethod
    def clear_cache(cls, user_id: int = None, feature_key: str = None):
        """
        Clear RBAC cache.

        Args:
            user_id: Clear cache for specific user (None = all users)
            feature_key: Clear cache for specific feature (None = all features)
        """
        if user_id and feature_key:
            # Clear specific user-feature combination
            cache_pattern = f"rbac:user:{user_id}:feature:{feature_key}:*"
        elif user_id:
            # Clear all cache for user
            cache_pattern = f"rbac:user:{user_id}:*"
        elif feature_key:
            # Clear all cache for feature
            cache_pattern = f"rbac:*:feature:{feature_key}:*"
        else:
            # Clear all RBAC cache
            cache_pattern = "rbac:*"

        # Note: Django cache doesn't support pattern deletion by default
        # This is a placeholder - implement based on your cache backend
        # For Redis: use SCAN and DELETE
        # For Memcached: clear all
        # For development: cache.clear()
        pass
