"""
Example Views Demonstrating Organization Context Usage.

Shows how to use organization-scoped mixins with existing views.
These are reference implementations - adapt for your specific models.

See: docs/plans/bmms/TRANSITION_PLAN.md
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from common.mixins.organization_mixins import (
    OrganizationFilteredMixin,
    OrganizationFormMixin,
    MultiOrganizationAccessMixin
)
from common.mixins.ocm_mixins import (
    OCMAggregationMixin,
    OCMDashboardMixin,
    OCMReadOnlyDetailMixin
)


# ========== COMMUNITIES APP EXAMPLES ==========

class CommunityListView(LoginRequiredMixin, OrganizationFilteredMixin, ListView):
    """
    Example: Organization-scoped community list.

    Behavior:
    - OOBC staff: See all communities (can filter by organization)
    - OCM users: See all communities (read-only)
    - MOA staff: See only their organization's communities
    """
    model = None  # Set to your model
    template_name = 'communities/communities_list.html'
    organization_filter_field = 'implementing_moa'  # FK field to Organization
    context_object_name = 'communities'


class CommunityDetailView(LoginRequiredMixin, OrganizationFilteredMixin, DetailView):
    """
    Example: Organization-scoped community detail.

    Security:
    - Validates user has access to community's organization
    - OCM users: Read-only access
    - MOA staff: Their organization only
    """
    model = None  # Set to your model
    template_name = 'communities/communities_detail.html'
    organization_filter_field = 'implementing_moa'
    context_object_name = 'community'


class CommunityCreateView(LoginRequiredMixin, OrganizationFormMixin, CreateView):
    """
    Example: Create community with organization context.

    Features:
    - Auto-sets organization from context
    - MOA staff: Organization field disabled (locked to their MOA)
    - OOBC staff: Can select any organization
    """
    model = None  # Set to your model
    template_name = 'communities/communities_form.html'
    organization_field_name = 'implementing_moa'
    fields = ['name', 'implementing_moa', 'description']  # Include org field


# ========== COORDINATION APP EXAMPLES ==========

class ActivityListView(LoginRequiredMixin, OrganizationFilteredMixin, ListView):
    """
    Example: Organization-scoped activities.

    Use for events, meetings, engagements filtered by organization.
    """
    model = None  # Set to your model (e.g., StakeholderEngagement)
    template_name = 'coordination/activity_list.html'
    organization_filter_field = 'community__implementing_moa'  # Related field
    context_object_name = 'activities'


# ========== MANA APP EXAMPLES ==========

class AssessmentListView(LoginRequiredMixin, OrganizationFilteredMixin, ListView):
    """
    Example: Organization-scoped assessments.

    Note: MANA is OOBC-internal, so MOA staff should not access.
    Add extra validation if needed.
    """
    model = None  # Set to your model (e.g., Assessment)
    template_name = 'mana/assessment_list.html'
    organization_filter_field = 'implementing_moa'
    context_object_name = 'assessments'

    def get_queryset(self):
        """Block MOA staff from MANA."""
        if self.request.user.is_moa_staff:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("MOA users cannot access MANA assessments.")

        return super().get_queryset()


# ========== OCM AGGREGATION EXAMPLES ==========

class OCMDashboardView(LoginRequiredMixin, OCMDashboardMixin, ListView):
    """
    Example: OCM multi-MOA comparison dashboard.

    Features:
    - Aggregated view across all 44 MOAs
    - Comparison charts and trends
    - Export to PDF/Excel
    - Read-only for OCM users
    """
    model = None  # Set to your model
    template_name = 'ocm/moa_dashboard.html'
    organization_filter_field = 'implementing_moa'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        """Add OCM dashboard data."""
        context = super().get_context_data(**kwargs)

        # Add comparison data for charts
        context['budget_comparison'] = self.get_comparison_data(
            metric_field='budget_allocated',
            organization_field='implementing_moa'
        )

        # Add trend data
        context['monthly_trends'] = self.get_trend_data(
            date_field='created_at',
            metric_field='budget_allocated',
            organization_field='implementing_moa'
        )

        return context


class OCMCommunityDetailView(LoginRequiredMixin, OCMReadOnlyDetailMixin, DetailView):
    """
    Example: OCM read-only community detail.

    OCM can view but not edit/delete.
    """
    model = None  # Set to your model
    template_name = 'ocm/community_detail.html'
    context_object_name = 'community'

    def has_edit_permission(self):
        """OCM cannot edit (handled by mixin)."""
        return not getattr(self.request, 'is_ocm_user', False)

    def has_delete_permission(self):
        """OCM cannot delete (handled by mixin)."""
        return not getattr(self.request, 'is_ocm_user', False)


# ========== MULTI-ORGANIZATION REPORT EXAMPLES ==========

class CrossMOAReportView(LoginRequiredMixin, MultiOrganizationAccessMixin, ListView):
    """
    Example: Report that can filter across multiple MOAs.

    Features:
    - OOBC/OCM can select multiple organizations to compare
    - MOA staff: Limited to their organization
    - URL: /reports/cross-moa/?orgs=uuid1&orgs=uuid2
    """
    model = None  # Set to your model
    template_name = 'reports/cross_moa_report.html'
    organization_filter_field = 'implementing_moa'
    organization_param_name = 'orgs'  # Query parameter name
    context_object_name = 'items'


# ========== HELPER FUNCTIONS FOR VIEWS ==========

def get_organization_choices(user):
    """
    Get organization choices for forms based on user permissions.

    Returns:
        QuerySet of organizations user can select
    """
    from common.services.rbac_service import RBACService
    return RBACService.get_organizations_with_access(user)


def validate_organization_access(user, organization):
    """
    Validate user has access to organization.

    Raises:
        PermissionDenied if user cannot access organization
    """
    from common.middleware.organization_context import user_can_access_organization
    from django.core.exceptions import PermissionDenied

    if not user_can_access_organization(user, organization):
        raise PermissionDenied(
            f"You do not have access to {organization.name}."
        )


def switch_organization(request, organization_id):
    """
    Switch user's current organization context.

    Args:
        request: HTTP request
        organization_id: UUID of organization to switch to

    Returns:
        bool: True if switched successfully
    """
    from coordination.models import Organization
    from common.services.rbac_service import RBACService

    # Check if user can switch
    if not RBACService.can_switch_organization(request.user):
        return False

    try:
        organization = Organization.objects.get(id=organization_id)

        # Validate access
        from common.middleware.organization_context import user_can_access_organization
        if not user_can_access_organization(request.user, organization):
            return False

        # Store in session
        request.session['current_organization'] = str(organization.id)
        return True

    except Organization.DoesNotExist:
        return False
