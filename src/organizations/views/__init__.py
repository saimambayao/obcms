"""
Views for organizations app - BMMS multi-tenant organization management.

This module provides views for:
- Organization switching interface
- Organization membership management
- Organization selection and context
- API endpoints for organization operations
"""

import logging
from typing import Dict, Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from organizations.models import Organization, OrganizationMembership
from obc_management.settings.bmms_config import (
    is_bmms_mode,
    is_obcms_mode,
    organization_switching_enabled
)

logger = logging.getLogger(__name__)
User = get_user_model()


# ============================================================================
# ORGANIZATION SWITCHING VIEWS
# ============================================================================

@login_required
def switch_organization(request, organization_code):
    """
    Switch the current organization context.

    URL Pattern: /organizations/switch/<organization_code>/

    Args:
        request: HttpRequest instance
        organization_code: Organization code to switch to

    Returns:
        Redirect to previous page or dashboard
    """
    # Only allow switching in BMMS mode
    if not is_bmms_mode() or not organization_switching_enabled():
        messages.error(request, _("Organization switching is not available in OBCMS mode."))
        return redirect('common:dashboard')

    # Get organization
    organization = get_object_or_404(
        Organization,
        code=organization_code.upper(),
        is_active=True
    )

    # Check user access
    if not _user_can_access_organization(request.user, organization):
        messages.error(
            request,
            _("You do not have access to {organization_name}.").format(
                organization_name=organization.name
            )
        )
        return redirect('common:dashboard')

    # Store in session
    request.session['selected_organization_id'] = organization.id
    request.session['selected_organization_code'] = organization.code

    # Log the switch
    logger.info(
        f"User {request.user.username} switched to organization {organization.code}"
    )

    messages.success(
        request,
        _("Switched to {organization_name}.").format(
            organization_name=organization.name
        )
    )

    # Redirect to next URL or dashboard
    next_url = request.GET.get('next', None)
    if next_url and next_url.startswith('/'):
        return redirect(next_url)

    return redirect('common:dashboard')


@login_required
def organization_switcher(request):
    """
    Display organization switching interface.

    URL Pattern: /organizations/switcher/

    Shows all organizations the user has access to and allows switching.
    """
    # Only available in BMMS mode
    if not is_bmms_mode() or not organization_switching_enabled():
        return redirect('common:dashboard')

    # Get user's organizations
    user_memberships = OrganizationMembership.objects.filter(
        user=request.user,
        is_active=True,
        organization__is_active=True
    ).select_related('organization').order_by('-is_primary', 'organization__name')

    # Get current organization
    current_org = getattr(request, 'organization', None)

    context = {
        'user_memberships': user_memberships,
        'current_organization': current_org,
        'page_title': _('Switch Organization'),
        'is_switcher_page': True,
    }

    return render(request, 'organizations/organization_switcher.html', context)


# ============================================================================
# ORGANIZATION MANAGEMENT VIEWS
# ============================================================================

class OrganizationListView(LoginRequiredMixin, ListView):
    """List all organizations (admin/superuser only)."""

    model = Organization
    template_name = 'organizations/organization_list.html'
    context_object_name = 'organizations'
    paginate_by = 20

    def get_queryset(self):
        """Filter organizations based on user permissions."""
        user = self.request.user

        if user.is_superuser:
            # Superusers see all organizations
            return Organization.objects.all().order_by('code')

        # Regular users only see their organizations
        return Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).distinct().order_by('code')

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Organizations')
        context['is_admin_view'] = self.request.user.is_superuser
        return context


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    """Display organization details."""

    model = Organization
    template_name = 'organizations/organization_detail.html'
    context_object_name = 'organization'
    slug_field = 'code'
    slug_url_kwarg = 'code'

    def get_queryset(self):
        """Filter based on user access."""
        user = self.request.user

        if user.is_superuser:
            return Organization.objects.all()

        return Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).distinct()

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        organization = context['organization']

        # Get user's membership
        try:
            membership = OrganizationMembership.objects.get(
                user=self.request.user,
                organization=organization
            )
            context['user_membership'] = membership
        except OrganizationMembership.DoesNotExist:
            context['user_membership'] = None

        # Get organization members
        if self.request.user.is_superuser:
            members = OrganizationMembership.objects.filter(
                organization=organization,
                is_active=True
            ).select_related('user').order_by('-is_primary', 'user__username')
        else:
            members = OrganizationMembership.objects.filter(
                organization=organization,
                is_active=True
            ).select_related('user').order_by('-is_primary', 'user__username')

        context['members'] = members
        context['page_title'] = organization.name
        context['can_manage'] = self._can_manage_organization(organization)

        return context

    def _can_manage_organization(self, organization):
        """Check if user can manage this organization."""
        user = self.request.user

        if user.is_superuser:
            return True

        try:
            membership = OrganizationMembership.objects.get(
                user=user,
                organization=organization
            )
            return membership.can_manage_users
        except OrganizationMembership.DoesNotExist:
            return False


# ============================================================================
# MEMBERSHIP MANAGEMENT VIEWS
# ============================================================================

@login_required
def my_memberships(request):
    """
    Display user's organization memberships.

    URL Pattern: /organizations/my-memberships/
    """
    memberships = OrganizationMembership.objects.filter(
        user=request.user
    ).select_related('organization').order_by('-is_primary', 'organization__name')

    context = {
        'memberships': memberships,
        'page_title': _('My Organizations'),
        'can_switch': is_bmms_mode() and organization_switching_enabled(),
    }

    return render(request, 'organizations/my_memberships.html', context)


@require_POST
@login_required
def set_primary_organization(request, organization_id):
    """
    Set user's primary organization.

    URL Pattern: /organizations/set-primary/<int:organization_id>/

    Args:
        request: HttpRequest instance
        organization_id: ID of organization to set as primary

    Returns:
        JsonResponse with success/error status
    """
    try:
        organization = get_object_or_404(Organization, id=organization_id)

        # Check user has membership
        membership = get_object_or_404(
            OrganizationMembership,
            user=request.user,
            organization=organization,
            is_active=True
        )

        # Clear existing primary
        OrganizationMembership.objects.filter(
            user=request.user,
            is_primary=True
        ).update(is_primary=False)

        # Set new primary
        membership.is_primary = True
        membership.save()

        # Update session
        request.session['selected_organization_id'] = organization.id
        request.session['selected_organization_code'] = organization.code

        logger.info(
            f"User {request.user.username} set {organization.code} as primary organization"
        )

        return JsonResponse({
            'success': True,
            'message': _("{organization_name} set as primary organization.").format(
                organization_name=organization.name
            )
        })

    except Exception as e:
        logger.error(f"Error setting primary organization: {e}")
        return JsonResponse({
            'success': False,
            'message': _("Failed to set primary organization. Please try again.")
        }, status=400)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_my_organizations(request):
    """
    API endpoint to get user's organizations.

    URL Pattern: /api/v1/organizations/my-organizations/

    Returns:
        JSON response with user's organizations and current selection
    """
    try:
        # Get user's memberships
        memberships = OrganizationMembership.objects.filter(
            user=request.user,
            is_active=True,
            organization__is_active=True
        ).select_related('organization').order_by('-is_primary', 'organization__name')

        # Build response data
        organizations = []
        current_org_id = getattr(request, 'organization', None)

        for membership in memberships:
            org = membership.organization
            organizations.append({
                'id': org.id,
                'code': org.code,
                'name': org.name,
                'org_type': org.org_type,
                'is_primary': membership.is_primary,
                'role': membership.role,
                'enabled_modules': org.enabled_modules,
                'is_current': current_org_id and current_org_id.id == org.id
            })

        response_data = {
            'organizations': organizations,
            'current_organization': {
                'id': current_org_id.id,
                'code': current_org_id.code,
                'name': current_org_id.name,
                'enabled_modules': current_org_id.enabled_modules
            } if current_org_id else None,
            'can_switch': is_bmms_mode() and organization_switching_enabled(),
            'is_bmms_mode': is_bmms_mode()
        }

        return Response(response_data)

    except Exception as e:
        logger.error(f"Error in api_my_organizations: {e}")
        return Response(
            {'error': 'Failed to retrieve organizations'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_switch_organization(request):
    """
    API endpoint to switch organization.

    URL Pattern: /api/v1/organizations/switch/

    Request Body:
        {
            "organization_id": 123
        }

    Returns:
        JSON response with success/error status
    """
    if not is_bmms_mode() or not organization_switching_enabled():
        return Response(
            {'error': 'Organization switching is not available'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        organization_id = request.data.get('organization_id')
        if not organization_id:
            return Response(
                {'error': 'Organization ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        organization = get_object_or_404(Organization, id=organization_id, is_active=True)

        # Check user access
        if not _user_can_access_organization(request.user, organization):
            return Response(
                {'error': 'You do not have access to this organization'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Store in session
        request.session['selected_organization_id'] = organization.id
        request.session['selected_organization_code'] = organization.code

        # Log the switch
        logger.info(
            f"User {request.user.username} switched to organization {organization.code} via API"
        )

        return Response({
            'success': True,
            'message': f'Switched to {organization.name}',
            'organization': {
                'id': organization.id,
                'code': organization.code,
                'name': organization.name,
                'enabled_modules': organization.enabled_modules
            }
        })

    except Exception as e:
        logger.error(f"Error in api_switch_organization: {e}")
        return Response(
            {'error': 'Failed to switch organization'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _user_can_access_organization(user, organization):
    """
    Check if user has access to organization.

    Args:
        user: User instance
        organization: Organization instance

    Returns:
        bool: True if user can access organization
    """
    if user.is_superuser:
        return True

    return OrganizationMembership.objects.filter(
        user=user,
        organization=organization,
        is_active=True
    ).exists()


# ============================================================================
# CONTEXT PROCESSOR
# ============================================================================

def organization_switcher_context(request):
    """
    Add organization switcher context to templates.

    This context processor adds data needed for the organization switcher
    dropdown/component in templates.

    Add to settings.py:
        TEMPLATES = [{
            'OPTIONS': {
                'context_processors': [
                    ...
                    'organizations.views.organization_switcher_context',
                ]
            }
        }]
    """
    if not request.user.is_authenticated:
        return {}

    # Only in BMMS mode with switching enabled
    if not is_bmms_mode() or not organization_switching_enabled():
        return {
            'show_organization_switcher': False,
            'user_organizations': [],
            'current_organization': None,
        }

    try:
        # Get user's organizations
        memberships = OrganizationMembership.objects.filter(
            user=request.user,
            is_active=True,
            organization__is_active=True
        ).select_related('organization').order_by('-is_primary', 'organization__name')

        current_org = getattr(request, 'organization', None)

        return {
            'show_organization_switcher': True,
            'user_organizations': [
                {
                    'id': m.organization.id,
                    'code': m.organization.code,
                    'name': m.organization.name,
                    'is_primary': m.is_primary,
                    'is_current': current_org and current_org.id == m.organization.id
                }
                for m in memberships
            ],
            'current_organization': current_org,
            'organization_switching_enabled': True,
        }

    except Exception as e:
        logger.error(f"Error in organization_switcher_context: {e}")
        return {
            'show_organization_switcher': False,
            'user_organizations': [],
            'current_organization': None,
        }