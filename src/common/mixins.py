"""
View mixins for MOA RBAC system.

Provides reusable mixins for ListView/DetailView classes.
"""

from django.core.exceptions import PermissionDenied


class MOAFilteredQuerySetMixin:
    """
    Mixin for ListView/DetailView that auto-filters queryset for MOA users.

    Usage:
        class PPAListView(MOAFilteredQuerySetMixin, ListView):
            model = MonitoringEntry
            moa_filter_field = 'implementing_moa'

    Attributes:
        moa_filter_field: Field name to filter by (defaults to 'implementing_moa')
    """
    moa_filter_field = 'implementing_moa'

    def get_queryset(self):
        qs = super().get_queryset()

        if (self.request.user.is_authenticated and
            self.request.user.is_moa_staff and
            self.moa_filter_field):

            # Determine the filter value based on field type
            moa_org = self.request.user.moa_organization

            # If filtering by an ID field (id, pk, or *_id), use the organization's PK
            # Otherwise, use the organization object for ForeignKey lookups
            if self.moa_filter_field in ('id', 'pk') or self.moa_filter_field.endswith('_id'):
                filter_value = moa_org.pk if moa_org else None
            else:
                filter_value = moa_org

            # Filter to user's MOA only
            filter_kwargs = {
                self.moa_filter_field: filter_value
            }
            qs = qs.filter(**filter_kwargs)

        return qs


class MOAOrganizationAccessMixin:
    """
    Mixin to restrict organization access to user's own MOA.

    Checks object-level permissions for organization views.
    """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if (self.request.user.is_authenticated and
            self.request.user.is_moa_staff):

            # Check if user owns this organization
            if not self.request.user.owns_moa_organization(obj):
                raise PermissionDenied(
                    "You can only access your own MOA organization."
                )

        return obj


class MOAPPAAccessMixin:
    """
    Mixin to restrict PPA access to user's own MOA PPAs.

    Checks object-level permissions for PPA views.
    """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if (self.request.user.is_authenticated and
            self.request.user.is_moa_staff):

            # Check if user can access this PPA
            if not self.request.user.can_view_ppa(obj):
                raise PermissionDenied(
                    "You can only access PPAs for your own MOA."
                )

        return obj


class MOAViewOnlyMixin:
    """
    Mixin to restrict MOA users to view-only access.

    Blocks POST, PUT, PATCH, DELETE methods for MOA users.
    """

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated and
            request.user.is_moa_staff and
            request.method not in ['GET', 'HEAD', 'OPTIONS']):

            raise PermissionDenied(
                "MOA users have view-only access to this resource."
            )

        return super().dispatch(request, *args, **kwargs)
