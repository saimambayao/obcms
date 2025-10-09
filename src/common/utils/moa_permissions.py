"""
Permission utilities for MOA RBAC system.

Provides decorators and helper functions for controlling MOA user access.
"""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def moa_view_only(view_func):
    """
    Decorator: Allow MOA users view-only access.

    MOA users can only use GET, HEAD, OPTIONS methods.
    POST, PUT, PATCH, DELETE are blocked.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_moa_staff:
            if request.method not in ['GET', 'HEAD', 'OPTIONS']:
                raise PermissionDenied(
                    "MOA users have view-only access to this resource. "
                    "You cannot create, edit, or delete."
                )
        return view_func(request, *args, **kwargs)
    return wrapper


def moa_can_edit_organization(view_func):
    """
    Decorator: Allow MOA users to edit their own organization only.

    Checks pk or organization_id in URL kwargs.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_moa_staff:
            org_id = kwargs.get('pk') or kwargs.get('organization_id')
            if org_id and not request.user.owns_moa_organization(org_id):
                raise PermissionDenied(
                    "You can only edit your own MOA organization. "
                    f"This organization does not belong to your MOA."
                )
        return view_func(request, *args, **kwargs)
    return wrapper


def moa_can_edit_ppa(view_func):
    """
    Decorator: Allow MOA users to edit their own MOA PPAs only.

    Checks pk or entry_id in URL kwargs.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_moa_staff:
            ppa_id = kwargs.get('pk') or kwargs.get('entry_id')
            if ppa_id:
                from monitoring.models import MonitoringEntry
                ppa = get_object_or_404(MonitoringEntry, pk=ppa_id)
                if not request.user.can_edit_ppa(ppa):
                    raise PermissionDenied(
                        "You can only edit PPAs for your own MOA. "
                        f"This PPA belongs to {ppa.implementing_moa}."
                    )
        return view_func(request, *args, **kwargs)
    return wrapper


def moa_can_edit_work_item(view_func):
    """
    Decorator: Allow MOA users to edit work items linked to their MOA PPAs only.

    Checks pk in URL kwargs.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_moa_staff:
            work_item_id = kwargs.get('pk')
            if work_item_id:
                from common.work_item_model import WorkItem
                work_item = get_object_or_404(WorkItem, pk=work_item_id)
                if not request.user.can_edit_work_item(work_item):
                    raise PermissionDenied(
                        "You can only edit work items linked to your MOA's PPAs."
                    )
        return view_func(request, *args, **kwargs)
    return wrapper


def moa_can_edit_service(view_func):
    """
    Decorator: Allow MOA users to edit their own MOA services only.

    Checks pk or service_id in URL kwargs.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_moa_staff:
            service_id = kwargs.get('pk') or kwargs.get('service_id')
            if service_id:
                from services.models import ServiceOffering
                service = get_object_or_404(ServiceOffering, pk=service_id)
                if service.offering_mao != request.user.moa_organization:
                    raise PermissionDenied(
                        "You can only edit services for your own MOA. "
                        f"This service belongs to {service.offering_mao}."
                    )
        return view_func(request, *args, **kwargs)
    return wrapper


def moa_no_access(view_func):
    """
    Decorator: Block MOA users from accessing this view entirely.

    Use for MANA assessments, OOBC internal modules, etc.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_moa_staff:
            raise PermissionDenied(
                "MOA users do not have access to this module. "
                "This is an OOBC internal function."
            )
        return view_func(request, *args, **kwargs)
    return wrapper


# Helper functions

def user_can_access_mana(user):
    """Check if user can access MANA assessments."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_oobc_staff:
        return True
    # MOA users cannot access MANA
    return not user.is_moa_staff


def user_can_access_policies(user):
    """Check if user can access policy recommendations."""
    if not user.is_authenticated:
        return False
    # MOA users CAN access policies (filtered to their MOA's policies only)
    # OOBC staff see all policies
    return user.is_superuser or user.is_oobc_staff or user.is_moa_staff


def user_can_access_oobc_initiatives(user):
    """Check if user can access OOBC initiatives."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_oobc_staff:
        return True
    # MOA users cannot access OOBC initiatives
    return not user.is_moa_staff


def user_can_access_me_analytics(user):
    """Check if user can access M&E analytics."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_oobc_staff:
        return True
    # MOA users cannot access strategic M&E analytics
    return not user.is_moa_staff
