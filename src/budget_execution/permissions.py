"""
Budget Execution Permissions
Phase 2B: Budget Execution (Parliament Bill No. 325 Section 78)

Permission classes and decorators for budget execution operations.
"""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


# ============================================================================
# PERMISSION CHECKERS
# ============================================================================


def is_budget_officer(user):
    """
    Check if user has budget officer role.

    Budget officers can:
    - Release allotments
    - Create obligations
    - Record disbursements
    """
    if not user.is_authenticated:
        return False

    # Check if user is in Budget Officers group
    if user.groups.filter(name='Budget Officers').exists():
        return True

    # Check if user is superuser or staff
    if user.is_superuser or user.is_staff:
        return True

    return False


def is_finance_director(user):
    """
    Check if user has finance director role.

    Finance directors can:
    - Approve allotments
    - Override budget constraints (with justification)
    - Access all financial reports
    """
    if not user.is_authenticated:
        return False

    # Check if user is in Finance Directors group
    if user.groups.filter(name='Finance Directors').exists():
        return True

    # Check if user is superuser
    if user.is_superuser:
        return True

    return False


def is_finance_staff(user):
    """
    Check if user has finance staff role.

    Finance staff can:
    - Create obligations
    - Record disbursements
    - View financial reports
    """
    if not user.is_authenticated:
        return False

    # Check if user is in Finance Staff group
    if user.groups.filter(name='Finance Staff').exists():
        return True

    # Check if user is budget officer or higher
    if is_budget_officer(user) or is_finance_director(user):
        return True

    return False


def can_disburse(user):
    """
    Check if user has disbursement recording privileges.

    Can record disbursements:
    - Finance Staff
    - Budget Officers
    - Finance Directors
    """
    if not user.is_authenticated:
        return False

    # Check if user is in Disbursement Officers group
    if user.groups.filter(name='Disbursement Officers').exists():
        return True

    # Finance staff and above can record disbursements
    if is_finance_staff(user):
        return True

    return False


# ============================================================================
# PERMISSION DECORATORS
# ============================================================================


def budget_officer_required(view_func):
    """
    Decorator to restrict view access to budget officers only.

    Usage:
        @budget_officer_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not is_budget_officer(request.user):
            raise PermissionDenied(
                "You must be a Budget Officer to access this page."
            )
        return view_func(request, *args, **kwargs)

    return wrapped_view


def finance_director_required(view_func):
    """
    Decorator to restrict view access to finance directors only.

    Usage:
        @finance_director_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not is_finance_director(request.user):
            raise PermissionDenied(
                "You must be a Finance Director to access this page."
            )
        return view_func(request, *args, **kwargs)

    return wrapped_view


def finance_staff_required(view_func):
    """
    Decorator to restrict view access to finance staff only.

    Usage:
        @finance_staff_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not is_finance_staff(request.user):
            raise PermissionDenied(
                "You must be a Finance Staff member to access this page."
            )
        return view_func(request, *args, **kwargs)

    return wrapped_view


def disbursement_officer_required(view_func):
    """
    Decorator to restrict view access to users with disbursement privileges.

    Usage:
        @disbursement_officer_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not can_disburse(request.user):
            raise PermissionDenied(
                "You must have disbursement privileges to access this page."
            )
        return view_func(request, *args, **kwargs)

    return wrapped_view


# ============================================================================
# PERMISSION MIXINS (For Class-Based Views)
# ============================================================================


class BudgetOfficerMixin:
    """
    Mixin for class-based views requiring budget officer permissions.

    Usage:
        class MyView(BudgetOfficerMixin, View):
            ...
    """

    def dispatch(self, request, *args, **kwargs):
        if not is_budget_officer(request.user):
            raise PermissionDenied(
                "You must be a Budget Officer to access this page."
            )
        return super().dispatch(request, *args, **kwargs)


class FinanceDirectorMixin:
    """
    Mixin for class-based views requiring finance director permissions.

    Usage:
        class MyView(FinanceDirectorMixin, View):
            ...
    """

    def dispatch(self, request, *args, **kwargs):
        if not is_finance_director(request.user):
            raise PermissionDenied(
                "You must be a Finance Director to access this page."
            )
        return super().dispatch(request, *args, **kwargs)


class FinanceStaffMixin:
    """
    Mixin for class-based views requiring finance staff permissions.

    Usage:
        class MyView(FinanceStaffMixin, View):
            ...
    """

    def dispatch(self, request, *args, **kwargs):
        if not is_finance_staff(request.user):
            raise PermissionDenied(
                "You must be a Finance Staff member to access this page."
            )
        return super().dispatch(request, *args, **kwargs)


class DisbursementOfficerMixin:
    """
    Mixin for class-based views requiring disbursement privileges.

    Usage:
        class MyView(DisbursementOfficerMixin, View):
            ...
    """

    def dispatch(self, request, *args, **kwargs):
        if not can_disburse(request.user):
            raise PermissionDenied(
                "You must have disbursement privileges to access this page."
            )
        return super().dispatch(request, *args, **kwargs)


# ============================================================================
# PERMISSION CLASSES (For DRF Views)
# ============================================================================


try:
    from rest_framework.permissions import BasePermission

    class CanReleaseAllotment(BasePermission):
        """
        DRF permission: Budget officers only.
        """
        message = "You must be a Budget Officer to release allotments."

        def has_permission(self, request, view):
            return is_budget_officer(request.user)

    class CanApproveAllotment(BasePermission):
        """
        DRF permission: Finance directors only.
        """
        message = "You must be a Finance Director to approve allotments."

        def has_permission(self, request, view):
            return is_finance_director(request.user)

    class CanCreateObligation(BasePermission):
        """
        DRF permission: Finance staff and above.
        """
        message = "You must be a Finance Staff member to create obligations."

        def has_permission(self, request, view):
            return is_finance_staff(request.user)

    class CanRecordDisbursement(BasePermission):
        """
        DRF permission: Users with disbursement privileges.
        """
        message = "You must have disbursement privileges to record disbursements."

        def has_permission(self, request, view):
            return can_disburse(request.user)

except ImportError:
    # DRF not installed or not available
    pass
