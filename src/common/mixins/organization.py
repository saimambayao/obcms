"""
Organization-aware mixins for class-based views.

Provides mixins for CBVs to ensure organization context and
validate user access in BMMS mode. This implements the embedded
architecture pattern for multi-tenancy.

Key mixins:
- OrganizationRequiredMixin: Validates organization context in dispatch()
- get_organization(): Access current organization safely
- get_context_data(): Auto-adds organization to template context

Usage:
    class MyView(OrganizationRequiredMixin, LoginRequiredMixin, ListView):
        model = OBCCommunity
        template_name = 'communities/list.html'

Note: Must be placed FIRST in mixin/inheritance chain before LoginRequiredMixin

See: docs/plans/bmms/implementation/tasks/phase4_view_decorators.txt
"""
import logging
from django.http import HttpResponseForbidden
from django.core.exceptions import ImproperlyConfigured
from organizations.models import OrganizationMembership
from obc_management.settings.bmms_config import is_bmms_mode

logger = logging.getLogger(__name__)


class OrganizationRequiredMixin:
    """
    Mixin to ensure request has organization context.

    This mixin validates organization context in the dispatch() method
    before the view is processed. It should be placed FIRST in the
    mixin/inheritance chain to ensure it runs before other mixins.

    Behavior:
    - OBCMS mode: Transparent (organization auto-set by middleware)
    - BMMS mode: Validates OrganizationMembership for access control
    - Superusers: Always granted access
    - No organization: Returns HTTP 403 Forbidden

    Usage:
        class MyView(OrganizationRequiredMixin, LoginRequiredMixin, ListView):
            model = OBCCommunity
            template_name = 'communities/list.html'

            def get_queryset(self):
                # Auto-filtered by OrganizationScopedManager
                return super().get_queryset()

    Attributes:
        require_organization: If True, enforces organization requirement (default: True)
    """

    require_organization = True

    def dispatch(self, request, *args, **kwargs):
        """
        Validate organization context before dispatching view.

        This method is called before any HTTP method handler (get, post, etc.).
        It ensures organization context exists and user has access.

        Args:
            request: Django HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            HttpResponseForbidden: If organization invalid or access denied
            HttpResponse: From parent dispatch if validation passes
        """
        # Check organization context
        if self.require_organization:
            if not hasattr(request, 'organization') or request.organization is None:
                logger.error(
                    f'No organization context for view: {self.__class__.__name__}. '
                    f'Ensure OrganizationContextMiddleware is enabled.'
                )
                return HttpResponseForbidden(
                    'Organization context required but not found. '
                    'Please ensure middleware is properly configured.'
                )

            # Validate access in BMMS mode
            if is_bmms_mode() and request.user.is_authenticated:
                # Superusers can access any organization
                if not request.user.is_superuser:
                    has_access = OrganizationMembership.objects.filter(
                        user=request.user,
                        organization=request.organization,
                        is_active=True
                    ).exists()

                    if not has_access:
                        logger.warning(
                            f'User {request.user.username} denied access to org '
                            f'{request.organization.code} in {self.__class__.__name__}'
                        )
                        return HttpResponseForbidden(
                            f'You do not have access to {request.organization.name}. '
                            f'Please contact your system administrator.'
                        )

                    logger.debug(
                        f'User {request.user.username} granted access to '
                        f'organization {request.organization.code} in {self.__class__.__name__}'
                    )

        return super().dispatch(request, *args, **kwargs)

    def get_organization(self):
        """
        Get organization from request safely.

        This method provides safe access to the current organization
        with proper error handling. Use this instead of accessing
        request.organization directly in your views.

        Returns:
            Organization: Current organization from request.organization
            None: If require_organization=False and no organization set

        Raises:
            ImproperlyConfigured: If called before dispatch() or organization not set
                                 when require_organization=True

        Example:
            def get_queryset(self):
                org = self.get_organization()
                return MyModel.objects.filter(organization=org)
        """
        if not hasattr(self, 'request'):
            raise ImproperlyConfigured(
                'get_organization() called before dispatch(). '
                'Ensure the view has been properly initialized.'
            )

        if not hasattr(self.request, 'organization'):
            if self.require_organization:
                raise ImproperlyConfigured(
                    'Organization not available on request. '
                    'Ensure OrganizationContextMiddleware is enabled and '
                    'OrganizationRequiredMixin.dispatch() has been called.'
                )
            return None

        return self.request.organization

    def get_context_data(self, **kwargs):
        """
        Add organization to template context.

        This method automatically adds the current organization to
        the template context, making it available in templates.

        Returns:
            dict: Context with 'organization' key added

        Template usage:
            <h1>{{ organization.name }}</h1>
            <p>Organization Code: {{ organization.code }}</p>
        """
        context = super().get_context_data(**kwargs)

        # Add organization to context if available
        if hasattr(self.request, 'organization') and self.request.organization:
            context['organization'] = self.request.organization
            logger.debug(
                f'Organization {self.request.organization.code} added to '
                f'context for {self.__class__.__name__}'
            )

        return context

    def get_queryset(self):
        """
        Get queryset with organization filtering.

        Override this method in your view if you need custom queryset logic.
        By default, models using OrganizationScopedManager will automatically
        filter by request.organization.

        Example:
            def get_queryset(self):
                # Auto-filtered by OrganizationScopedManager
                qs = super().get_queryset()
                # Add custom filtering
                return qs.filter(status='active')
        """
        return super().get_queryset()
