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

        # Cache result and track key
        if use_cache:
            cache.set(cache_key, has_perm, cls.CACHE_TIMEOUT)
            cls._track_cache_key(cache_key)

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

        # OOBC staff: Check RBAC restrictions first, then fall back to full access
        if user.is_oobc_staff:
            # Check if this feature has RBAC restrictions
            try:
                from common.rbac_models import Feature
                feature_obj = Feature.objects.filter(
                    feature_key=feature_code,
                    is_active=True
                ).first()

                if feature_obj:
                    # Feature exists in RBAC system - delegate to RBAC check
                    # This will check user's roles and permissions properly
                    return cls._check_feature_access(user, feature_code, organization)
            except Exception:
                # RBAC models not available - fall back to legacy behavior
                pass

            # Legacy: Full access for non-RBAC features (backward compatibility)
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
        # Use the new clear_cache implementation
        cls.clear_cache(user_id=user_id)

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

        # Cache result and track key
        if use_cache:
            cache.set(cache_key, has_access, cls.CACHE_TIMEOUT)
            cls._track_cache_key(cache_key)

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

        OPTIMIZED VERSION - Fixes N+1 query issue.

        Args:
            user: User object
            organization: Optional organization context

        Returns:
            Set of permission IDs user has access to

        Logic:
        1. Get all active role IDs for user (single query)
        2. Get all permissions from those roles (single query)
        3. Add direct user permissions (single query)
        4. Remove explicitly denied permissions (single query)
        5. Filter expired permissions

        Performance: Reduces from N+1 queries to 4 queries total.
        """
        if not user.is_authenticated:
            return set()

        try:
            from common.rbac_models import UserRole, UserPermission, RolePermission

            permission_ids = set()
            now = timezone.now()

            # OPTIMIZATION: Get all user role IDs in a single query
            user_role_ids = UserRole.objects.filter(
                user=user,
                is_active=True
            )

            # Filter by organization if provided
            if organization:
                user_role_ids = user_role_ids.filter(
                    models.Q(organization=organization) | models.Q(organization__isnull=True)
                )

            # Filter out expired roles
            user_role_ids = user_role_ids.filter(
                models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
            ).values_list('role_id', flat=True)

            # OPTIMIZATION: Get all permissions from roles in a single query
            if user_role_ids:
                role_permission_ids = RolePermission.objects.filter(
                    role_id__in=user_role_ids,
                    is_active=True,
                    is_granted=True
                ).filter(
                    models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
                ).values_list('permission_id', flat=True)

                permission_ids.update(role_permission_ids)

            # Get direct user permissions (grants) - single query
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

            # Remove explicitly denied permissions - single query
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
        Clear RBAC cache with Redis pattern support.

        Args:
            user_id: Clear cache for specific user (None = all users)
            feature_key: Clear cache for specific feature (None = all features)

        Implementation:
        - Uses Redis pattern deletion if available (django-redis)
        - Falls back to tracking set for cache-agnostic deletion
        - Gracefully handles non-Redis backends

        Performance: O(N) where N is number of matching keys
        """
        from django.core.cache import cache
        import logging

        logger = logging.getLogger('rbac.cache')

        # Build pattern based on parameters
        if user_id and feature_key:
            pattern = f"rbac:user:{user_id}:feature:{feature_key}:*"
        elif user_id:
            pattern = f"rbac:user:{user_id}:*"
        elif feature_key:
            pattern = f"rbac:*:feature:{feature_key}:*"
        else:
            pattern = "rbac:*"

        try:
            # Try Redis-specific pattern deletion (django-redis backend)
            if hasattr(cache, 'delete_pattern'):
                deleted_count = cache.delete_pattern(pattern)
                logger.info(f"Cleared {deleted_count} RBAC cache keys matching: {pattern}")
                return deleted_count

            # Fallback: Use cache key tracking set
            tracker_key = "rbac:cache_keys"

            if hasattr(cache, 'smembers'):
                # Redis SET-based tracking
                all_keys = cache.smembers(tracker_key) or set()

                deleted_count = 0
                for key in all_keys:
                    # Simple pattern matching
                    if cls._matches_pattern(key.decode() if isinstance(key, bytes) else key, pattern):
                        cache.delete(key)
                        cache.srem(tracker_key, key)
                        deleted_count += 1

                logger.info(f"Cleared {deleted_count} RBAC cache keys using tracker: {pattern}")
                return deleted_count

            # Last resort: Clear all RBAC cache (inefficient but safe)
            logger.warning(f"Cache backend doesn't support pattern deletion. Clearing all RBAC cache.")

            # Try to clear at least user-specific or feature-specific
            if user_id:
                # Clear known cache key combinations for this user
                for org_id in ['', 'none']:
                    base_key = f"rbac:user:{user_id}:feature:"
                    # Can't enumerate all features, so just note the limitation
                    logger.warning(f"Limited cache invalidation for user {user_id}")

            return 0

        except Exception as e:
            logger.error(f"Error clearing RBAC cache: {e}")
            # Don't fail - cache invalidation errors shouldn't break the app
            return 0

    @classmethod
    def _matches_pattern(cls, key: str, pattern: str) -> bool:
        """
        Simple pattern matching for cache keys.

        Args:
            key: Cache key to test
            pattern: Pattern with * wildcards

        Returns:
            bool: True if key matches pattern
        """
        import re

        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace('*', '.*')
        regex_pattern = f"^{regex_pattern}$"

        return bool(re.match(regex_pattern, key))

    @classmethod
    def _track_cache_key(cls, cache_key: str):
        """
        Track cache key for pattern-based deletion.

        Only used when cache backend doesn't support delete_pattern.

        Args:
            cache_key: Key to track
        """
        from django.core.cache import cache

        tracker_key = "rbac:cache_keys"

        try:
            if hasattr(cache, 'sadd'):
                cache.sadd(tracker_key, cache_key)
        except Exception:
            # Tracking failure shouldn't break caching
            pass

    @classmethod
    def warm_cache_for_user(cls, user, organization=None):
        """
        Pre-populate cache with user's most common permissions.

        Call this after login for faster initial page load.

        Args:
            user: User object to warm cache for
            organization: Optional organization context

        Returns:
            int: Number of permissions cached
        """
        if not user.is_authenticated:
            return 0

        import logging
        logger = logging.getLogger('rbac.cache')

        try:
            from common.rbac_models import Feature

            # Get frequently accessed features (navbar, dashboards, common actions)
            common_features = Feature.objects.filter(
                is_active=True,
                category__in=['navigation', 'dashboard', 'common']
            ).values_list('feature_key', flat=True)

            # Fallback: if no features have categories, get by module
            if not common_features:
                common_features = Feature.objects.filter(
                    is_active=True,
                    module__in=['common', 'communities', 'coordination']
                ).values_list('feature_key', flat=True)[:20]  # Limit to 20

            cached_count = 0

            # Pre-compute and cache permissions for common features
            for feature_key in common_features:
                try:
                    # This will cache the result
                    cls.has_feature_access(user, feature_key, organization, use_cache=True)
                    cached_count += 1
                except Exception as e:
                    logger.warning(f"Failed to warm cache for feature {feature_key}: {e}")

            logger.info(f"Warmed RBAC cache for user {user.username}: {cached_count} features cached")
            return cached_count

        except Exception as e:
            logger.error(f"Error warming RBAC cache for user {user.username}: {e}")
            return 0

    @classmethod
    def has_permissions(
        cls,
        request: HttpRequest,
        permission_codes: List[str],
        require_all: bool = True,
        organization = None
    ) -> bool:
        """
        Check multiple permissions in a single call.

        More efficient than calling has_permission() multiple times.

        Args:
            request: HTTP request with user
            permission_codes: List of permission codes to check
            require_all: True = AND logic (all required), False = OR logic (any required)
            organization: Optional organization context

        Returns:
            bool: True if permission check passes

        Examples:
            # User must have ALL permissions
            has_permissions(request, ['communities.view', 'communities.edit'], require_all=True)

            # User must have AT LEAST ONE permission
            has_permissions(request, ['communities.view', 'coordination.view'], require_all=False)
        """
        if not request.user.is_authenticated:
            return False

        # Superusers bypass all checks
        if request.user.is_superuser:
            return True

        # Check each permission (uses cache for performance)
        results = []
        for code in permission_codes:
            result = cls.has_permission(request, code, organization)
            results.append(result)

            # Early exit optimization
            if require_all and not result:
                # AND logic: if any permission fails, return False immediately
                return False
            elif not require_all and result:
                # OR logic: if any permission succeeds, return True immediately
                return True

        # Final evaluation
        return all(results) if require_all else any(results)

    @classmethod
    def get_cache_stats(cls, user_id: int = None) -> dict:
        """
        Get cache statistics for monitoring.

        Args:
            user_id: Optional user ID to get specific stats

        Returns:
            dict: Cache statistics
        """
        from django.core.cache import cache
        import logging

        logger = logging.getLogger('rbac.cache')

        try:
            tracker_key = "rbac:cache_keys"

            if hasattr(cache, 'smembers'):
                all_keys = cache.smembers(tracker_key) or set()

                if user_id:
                    # Filter keys for specific user
                    user_pattern = f"rbac:user:{user_id}:*"
                    user_keys = [k for k in all_keys if cls._matches_pattern(
                        k.decode() if isinstance(k, bytes) else k, user_pattern
                    )]

                    return {
                        'total_cached_keys': len(all_keys),
                        'user_cached_keys': len(user_keys),
                        'user_id': user_id,
                    }

                return {
                    'total_cached_keys': len(all_keys),
                }

            return {
                'error': 'Cache stats not available - backend does not support key tracking'
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}
