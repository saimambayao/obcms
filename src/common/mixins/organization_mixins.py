"""
Organization-Scoped View Mixins for BMMS Multi-Tenant Support.

Provides reusable mixins for ListView/DetailView that automatically filter
querysets by organization context from request.organization.

Builds on existing MOAFilteredQuerySetMixin pattern in common.mixins.

Features:
- Automatic organization filtering for multi-tenant data isolation
- OCM aggregation support (view all organizations)
- Form integration (pre-fill organization fields)
- Compatible with existing MOA RBAC system

Usage:
    class CommunityListView(OrganizationFilteredMixin, ListView):
        model = OBCCommunity
        organization_filter_field = 'implementing_moa'

See: docs/plans/bmms/TRANSITION_PLAN.md
"""

from django.core.exceptions import PermissionDenied
from django.db.models import Q


class OrganizationFilteredMixin:
    """
    Mixin for ListView/DetailView that auto-filters queryset by organization.

    Attributes:
        organization_filter_field: Field name to filter by (default: 'organization')
        allow_no_organization: Allow queryset without organization (default: False)
        require_organization_access: Check user access to organization (default: True)

    Behavior:
        - OCM users: See all organizations (aggregated view)
        - OOBC staff: See all organizations (operational view)
        - MOA staff: See their organization only (isolated view)
        - No organization context: Return empty queryset (unless allow_no_organization=True)

    Example:
        class AssessmentListView(OrganizationFilteredMixin, ListView):
            model = Assessment
            organization_filter_field = 'implementing_moa'
    """

    organization_filter_field = 'organization'
    allow_no_organization = False
    require_organization_access = True

    def get_queryset(self):
        """Override to add organization filtering."""
        qs = super().get_queryset()

        # Skip if not authenticated
        if not self.request.user.is_authenticated:
            return qs.none()

        # Get organization context from request (set by middleware)
        organization = getattr(self.request, 'organization', None)

        # OCM and OOBC staff can see all organizations
        if self.request.user.is_superuser or self.request.user.is_oobc_staff:
            # If specific organization selected, filter by it
            if organization:
                filter_kwargs = {
                    self.organization_filter_field: organization
                }
                return qs.filter(**filter_kwargs)
            # Otherwise show all
            return qs

        # Check if user is OCM (can view all, read-only)
        from common.middleware.organization_context import is_ocm_user
        if is_ocm_user(self.request.user):
            # OCM sees all organizations (aggregated view)
            if organization:
                filter_kwargs = {
                    self.organization_filter_field: organization
                }
                return qs.filter(**filter_kwargs)
            return qs

        # MOA staff: Filter to their organization only
        if self.request.user.is_moa_staff:
            if not self.request.user.moa_organization:
                # MOA user has no organization assigned
                return qs.none()

            # Verify access if organization context provided
            if organization and self.require_organization_access:
                if organization != self.request.user.moa_organization:
                    raise PermissionDenied(
                        "You can only access your own MOA's data."
                    )

            # Filter to user's organization
            filter_kwargs = {
                self.organization_filter_field: self.request.user.moa_organization
            }
            return qs.filter(**filter_kwargs)

        # No organization context
        if not organization and not self.allow_no_organization:
            return qs.none()

        # Default: filter by organization if provided
        if organization:
            filter_kwargs = {
                self.organization_filter_field: organization
            }
            return qs.filter(**filter_kwargs)

        return qs

    def get_context_data(self, **kwargs):
        """Add organization context to template."""
        context = super().get_context_data(**kwargs)

        # Add organization info
        organization = getattr(self.request, 'organization', None)
        context['current_organization'] = organization

        # Add RBAC context
        from common.services.rbac_service import RBACService
        context.update(RBACService.get_permission_context(self.request))

        return context


class OrganizationFormMixin:
    """
    Mixin for CreateView/UpdateView to handle organization in forms.

    Automatically:
    - Sets organization field in form initial data
    - Validates user has access to organization
    - Hides/disables organization field for MOA staff

    Example:
        class CommunityCreateView(OrganizationFormMixin, CreateView):
            model = OBCCommunity
            organization_field_name = 'implementing_moa'
    """

    organization_field_name = 'organization'
    auto_set_organization = True

    def get_initial(self):
        """Set initial organization from context."""
        initial = super().get_initial()

        if self.auto_set_organization:
            organization = getattr(self.request, 'organization', None)

            # For MOA staff, always use their organization
            if self.request.user.is_moa_staff:
                organization = self.request.user.moa_organization

            if organization:
                initial[self.organization_field_name] = organization

        return initial

    def get_form(self, form_class=None):
        """Customize form based on user permissions."""
        form = super().get_form(form_class)

        # MOA staff cannot change organization
        if self.request.user.is_moa_staff:
            if self.organization_field_name in form.fields:
                field = form.fields[self.organization_field_name]
                field.disabled = True
                field.widget.attrs['readonly'] = True
                field.help_text = "Organization is set to your MOA."

        return form

    def form_valid(self, form):
        """Validate organization access before saving."""
        # Ensure organization is set
        if self.auto_set_organization and self.organization_field_name in form.fields:
            organization = form.cleaned_data.get(self.organization_field_name)

            # Validate user has access
            from common.middleware.organization_context import user_can_access_organization
            if organization and not user_can_access_organization(self.request.user, organization):
                form.add_error(
                    self.organization_field_name,
                    "You do not have access to this organization."
                )
                return self.form_invalid(form)

        return super().form_valid(form)


class MultiOrganizationAccessMixin:
    """
    Mixin for views that support accessing multiple organizations.

    Enables OOBC staff and OCM to filter/search across organizations.
    MOA staff still restricted to their own organization.

    Usage:
        class ReportView(MultiOrganizationAccessMixin, ListView):
            model = Assessment
            organization_filter_field = 'implementing_moa'
    """

    organization_filter_field = 'organization'
    organization_param_name = 'orgs'  # Query param for org filtering

    def get_queryset(self):
        """Filter by multiple organizations if permitted."""
        qs = super().get_queryset()

        if not self.request.user.is_authenticated:
            return qs.none()

        # Get organization IDs from query params
        org_ids = self.request.GET.getlist(self.organization_param_name)

        # MOA staff: Ignore query params, use their organization only
        if self.request.user.is_moa_staff:
            if self.request.user.moa_organization:
                filter_kwargs = {
                    self.organization_filter_field: self.request.user.moa_organization
                }
                return qs.filter(**filter_kwargs)
            return qs.none()

        # OOBC staff / OCM: Filter by requested organizations
        if org_ids and (self.request.user.is_oobc_staff or getattr(self.request, 'is_ocm_user', False)):
            filter_kwargs = {
                f'{self.organization_filter_field}__id__in': org_ids
            }
            return qs.filter(**filter_kwargs)

        # No filtering: use default behavior
        return qs

    def get_context_data(self, **kwargs):
        """Add multi-org context."""
        context = super().get_context_data(**kwargs)

        # Add available organizations for filtering
        from common.services.rbac_service import RBACService
        context['available_organizations'] = RBACService.get_organizations_with_access(
            self.request.user
        )

        # Add selected organization IDs
        context['selected_organization_ids'] = self.request.GET.getlist(
            self.organization_param_name
        )

        return context
