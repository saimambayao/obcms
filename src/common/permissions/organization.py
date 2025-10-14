"""
Organization-aware permissions for Django REST Framework.

Provides permission classes for API views to validate organization
context and user access in BMMS mode. Implements embedded architecture
pattern for multi-tenant API access control.

Key permissions:
- OrganizationAccessPermission: Validates organization context and membership
- has_permission(): Check user can access organization
- has_object_permission(): Prevent cross-organization data access

Usage:
    class MyAPIView(APIView):
        permission_classes = [IsAuthenticated, OrganizationAccessPermission]

    class MyViewSet(ModelViewSet):
        permission_classes = [IsAuthenticated, OrganizationAccessPermission]
        queryset = MyModel.objects.all()  # Auto-filtered by manager

See: docs/plans/bmms/implementation/tasks/phase4_view_decorators.txt
"""
import logging
from rest_framework.permissions import BasePermission
from organizations.models import OrganizationMembership
from obc_management.settings.bmms_config import is_bmms_mode

logger = logging.getLogger(__name__)


class OrganizationAccessPermission(BasePermission):
    """
    Permission to validate organization context and user access.

    This permission class enforces organization-based access control
    for Django REST Framework API views. It validates:

    1. Request has organization context (from middleware)
    2. User has active membership in organization (BMMS mode only)
    3. Superusers have access to all organizations
    4. Objects belong to user's organization (cross-org prevention)

    Behavior:
    - OBCMS mode: Always grants access (single organization)
    - BMMS mode: Validates OrganizationMembership for access
    - Superusers: Always granted access
    - No organization: Access denied

    Usage:
        class CommunityViewSet(ModelViewSet):
            serializer_class = CommunitySerializer
            permission_classes = [IsAuthenticated, OrganizationAccessPermission]
            queryset = OBCCommunity.objects.all()  # Auto-filtered

        class MyAPIView(APIView):
            permission_classes = [IsAuthenticated, OrganizationAccessPermission]

            def get(self, request):
                # request.organization is validated
                communities = OBCCommunity.objects.all()
                ...

    Message:
        Returns 403 Forbidden with descriptive message if access denied
    """

    def has_permission(self, request, view):
        """
        Check if user has permission to access organization.

        This method is called before the view is executed. It validates
        that the request has organization context and the user is a member
        of that organization (in BMMS mode).

        Args:
            request: DRF request object with .user and .organization
            view: View being accessed (for logging)

        Returns:
            bool: True if access granted, False otherwise

        Permission flow:
            1. Check organization context exists
            2. In OBCMS mode: Grant access (single org)
            3. In BMMS mode: Check OrganizationMembership
            4. Superusers: Always grant access
        """
        # Check organization context exists (set by middleware)
        if not hasattr(request, 'organization') or request.organization is None:
            logger.error(
                f'No organization context for API view: {view.__class__.__name__}. '
                f'Ensure OrganizationContextMiddleware is enabled.'
            )
            return False

        # In OBCMS mode, access automatically granted (single organization)
        if not is_bmms_mode():
            logger.debug(
                f'OBCMS mode: Access granted to organization '
                f'{request.organization.code} for {view.__class__.__name__}'
            )
            return True

        # In BMMS mode, validate membership
        if not request.user or not request.user.is_authenticated:
            logger.warning(
                f'Unauthenticated user denied access to organization '
                f'{request.organization.code} in {view.__class__.__name__}'
            )
            return False

        # Superusers have access to all organizations
        if request.user.is_superuser:
            logger.debug(
                f'Superuser {request.user.username} granted access to '
                f'organization {request.organization.code} in {view.__class__.__name__}'
            )
            return True

        # Check for active membership
        has_access = OrganizationMembership.objects.filter(
            user=request.user,
            organization=request.organization,
            is_active=True
        ).exists()

        if not has_access:
            logger.warning(
                f'User {request.user.username} denied API access to org '
                f'{request.organization.code} in {view.__class__.__name__} '
                f'(no active membership)'
            )
        else:
            logger.debug(
                f'User {request.user.username} granted API access to org '
                f'{request.organization.code} in {view.__class__.__name__}'
            )

        return has_access

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access specific object.

        This method is called for detail views (retrieve, update, delete)
        to ensure the object belongs to the user's organization. It prevents
        cross-organization data access.

        Args:
            request: DRF request object
            view: View being accessed
            obj: Model instance being accessed

        Returns:
            bool: True if access granted, False otherwise

        Object validation:
            - If object has 'organization' attribute: Must match request.organization
            - If object lacks 'organization': Allow (not organization-scoped)
            - Cross-org access: Deny with warning log
        """
        # If object has organization attribute, verify it matches request org
        if hasattr(obj, 'organization'):
            # Check if object's organization matches request organization
            if obj.organization != request.organization:
                logger.warning(
                    f'User {request.user.username} attempted cross-org access: '
                    f'request org={request.organization.code}, '
                    f'object org={obj.organization.code} '
                    f'(model={obj.__class__.__name__}, pk={obj.pk})'
                )
                return False

            logger.debug(
                f'User {request.user.username} granted object access: '
                f'model={obj.__class__.__name__}, pk={obj.pk}, '
                f'org={obj.organization.code}'
            )

        # Object doesn't have organization attribute - allow
        # (Not all models are organization-scoped)
        return True
