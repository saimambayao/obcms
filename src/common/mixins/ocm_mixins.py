"""
OCM (Office of Chief Minister) Aggregation View Mixins.

Provides special read-only aggregation access for OCM users across all 44 MOAs.
OCM has oversight responsibility and needs cross-organizational visibility.

Features:
- Read-only access to all MOA data
- Aggregated reporting and analytics
- Prevents write operations (view/export only)
- Organization comparison views

See: docs/product/BARMM_MOA_STRUCTURE_ANALYSIS.md
"""

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum, Q


class OCMAggregationMixin:
    """
    Mixin for views providing OCM with aggregated cross-MOA visibility.

    OCM Role:
        - Office of Chief Minister oversight
        - Read-only access to all 44 MOAs
        - Aggregated reports and dashboards
        - Cannot modify any MOA data

    Usage:
        class CrossMOAReportView(OCMAggregationMixin, ListView):
            model = Assessment
            template_name = 'ocm/moa_comparison.html'
    """

    ocm_only = False  # Set True to restrict to OCM users only
    ocm_read_only = True  # Enforce read-only for OCM

    def dispatch(self, request, *args, **kwargs):
        """Validate OCM access before processing request."""
        # Check OCM-only restriction
        if self.ocm_only:
            from common.middleware.organization_context import is_ocm_user
            if not is_ocm_user(request.user) and not request.user.is_superuser:
                raise PermissionDenied(
                    "This view is restricted to Office of Chief Minister (OCM) users only."
                )

        # Enforce read-only for OCM users
        if self.ocm_read_only:
            from common.middleware.organization_context import is_ocm_user
            if is_ocm_user(request.user) and request.method not in ['GET', 'HEAD', 'OPTIONS']:
                raise PermissionDenied(
                    "OCM users have read-only access. You cannot create, edit, or delete data."
                )

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return aggregated queryset across all MOAs."""
        qs = super().get_queryset()

        # OCM and superusers see all organizations
        from common.middleware.organization_context import is_ocm_user
        if is_ocm_user(self.request.user) or self.request.user.is_superuser:
            return qs

        # OOBC staff see all (operational access)
        if self.request.user.is_oobc_staff:
            return qs

        # MOA staff: restricted to their organization (fallback)
        if self.request.user.is_moa_staff and self.request.user.moa_organization:
            # This should not normally be reached if ocm_only=True
            organization_field = getattr(self, 'organization_filter_field', 'organization')
            filter_kwargs = {
                organization_field: self.request.user.moa_organization
            }
            return qs.filter(**filter_kwargs)

        # No access for other users
        return qs.none()

    def get_context_data(self, **kwargs):
        """Add OCM-specific aggregation context."""
        context = super().get_context_data(**kwargs)

        # Add OCM flag
        from common.middleware.organization_context import is_ocm_user
        context['is_ocm_user'] = is_ocm_user(self.request.user)
        context['is_ocm_only_view'] = self.ocm_only

        # Add MOA summary statistics if OCM user
        if is_ocm_user(self.request.user) or self.request.user.is_superuser:
            context['moa_statistics'] = self.get_moa_statistics()

        return context

    def get_moa_statistics(self):
        """
        Generate aggregated statistics across all MOAs.

        Override this method to customize statistics for your model.
        """
        from coordination.models import Organization

        # Get all active BMOA organizations
        organizations = Organization.objects.filter(
            organization_type='bmoa',
            is_active=True
        )

        stats = {
            'total_moas': organizations.count(),
            'organizations': organizations,
        }

        # Add model-specific stats if available
        queryset = self.get_queryset()
        organization_field = getattr(self, 'organization_filter_field', 'organization')

        if hasattr(queryset.model, organization_field):
            # Count items per MOA
            stats['per_moa_counts'] = queryset.values(
                organization_field
            ).annotate(
                count=Count('id')
            ).order_by('-count')

        return stats


class OCMDashboardMixin(OCMAggregationMixin):
    """
    Specialized mixin for OCM dashboard views.

    Provides:
    - Multi-MOA comparison charts
    - Trend analysis across organizations
    - Executive summaries
    """

    ocm_only = True  # Dashboards are OCM-exclusive

    def get_comparison_data(self, metric_field: str, organization_field: str = 'organization'):
        """
        Get comparison data across MOAs for charting.

        Args:
            metric_field: Field to aggregate (e.g., 'budget_allocated')
            organization_field: FK field to Organization

        Returns:
            List of dicts with organization and metric value
        """
        from django.db.models import Sum
        from coordination.models import Organization

        queryset = self.get_queryset()

        # Aggregate by organization
        comparison = queryset.values(
            f'{organization_field}__name',
            f'{organization_field}__acronym'
        ).annotate(
            total=Sum(metric_field)
        ).order_by('-total')

        return list(comparison)

    def get_trend_data(self, date_field: str, metric_field: str, organization_field: str = 'organization'):
        """
        Get time-series trend data for each MOA.

        Args:
            date_field: Date field for grouping (e.g., 'created_at')
            metric_field: Field to aggregate
            organization_field: FK field to Organization

        Returns:
            Dict with organization trends
        """
        from django.db.models.functions import TruncMonth
        from django.db.models import Count, Sum

        queryset = self.get_queryset()

        # Group by month and organization
        trends = queryset.annotate(
            month=TruncMonth(date_field)
        ).values(
            'month',
            f'{organization_field}__name',
            f'{organization_field}__acronym'
        ).annotate(
            count=Count('id'),
            total=Sum(metric_field) if metric_field else Count('id')
        ).order_by('month', f'{organization_field}__name')

        return list(trends)

    def get_context_data(self, **kwargs):
        """Add dashboard-specific context."""
        context = super().get_context_data(**kwargs)

        # Add dashboard title
        context['dashboard_title'] = 'Office of Chief Minister - Multi-MOA Dashboard'

        # Add export options
        context['can_export'] = True
        context['export_formats'] = ['PDF', 'Excel', 'CSV']

        return context


class OCMReadOnlyDetailMixin:
    """
    Mixin for detail views that OCM can view but not modify.

    Hides edit/delete buttons from OCM users.
    """

    def get_context_data(self, **kwargs):
        """Add OCM read-only context."""
        context = super().get_context_data(**kwargs)

        from common.middleware.organization_context import is_ocm_user

        # Disable edit/delete for OCM
        if is_ocm_user(self.request.user):
            context['can_edit'] = False
            context['can_delete'] = False
            context['read_only_message'] = (
                "Office of Chief Minister users have read-only access to this data."
            )
        else:
            # Delegate to normal permission checks
            context['can_edit'] = self.has_edit_permission()
            context['can_delete'] = self.has_delete_permission()

        return context

    def has_edit_permission(self):
        """Check if user can edit (override in subclass)."""
        return True

    def has_delete_permission(self):
        """Check if user can delete (override in subclass)."""
        return True
