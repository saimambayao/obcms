"""Permission utilities for MOA staff management."""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from common.constants import STAFF_USER_TYPES


def can_approve_moa_users(user):
    """
    Check if a user can approve MOA staff registrations.

    Authorized users:
    - Superusers
    - OOBC Executive Director
    - Users in 'MOA Coordinator' group (with can_approve_moa_users permission)

    Args:
        user: User instance to check

    Returns:
        bool: True if user can approve MOA users
    """
    if not user or not user.is_authenticated:
        return False

    # Superusers can always approve
    if user.is_superuser:
        return True

    # OOBC Executive Director can approve
    if user.user_type == 'oobc_executive':
        return True

    # Check for MOA Coordinator permission
    try:
        content_type = ContentType.objects.get_for_model(user.__class__)
        permission = Permission.objects.get(
            codename='can_approve_moa_users',
            content_type=content_type
        )
        return user.has_perm(f'{content_type.app_label}.can_approve_moa_users')
    except (Permission.DoesNotExist, ContentType.DoesNotExist):
        return False


def get_pending_moa_count():
    """
    Get count of pending MOA staff registrations.

    Returns:
        int: Number of MOA staff awaiting approval
    """
    from common.models import User

    return User.objects.filter(
        user_type__in=['bmoa', 'lgu', 'nga'],
        is_active=True,
        moa_first_level_approved=True,
        is_approved=False,
    ).count()


def get_pending_first_level_count(moa_organization):
    """
    Get count of pending MOA staff registrations awaiting focal person approval.

    Args:
        moa_organization: Organization instance or None

    Returns:
        int: Number of MOA staff awaiting focal endorsement for the organization
    """
    if not moa_organization:
        return 0

    from common.models import User

    return User.objects.filter(
        moa_organization=moa_organization,
        user_type__in=['bmoa', 'lgu', 'nga'],
        is_active=True,
        is_approved=False,
        moa_first_level_approved=False,
    ).count()


def is_moa_focal_approver(user):
    """
    Determine whether the user can perform first-level approvals as a focal person.

    Checks for active MAO focal person assignments and focal designations in the
    user's position metadata.
    """
    if not user or not user.is_authenticated:
        return False

    if not getattr(user, "is_moa_staff", False):
        return False

    # Focal designation via position metadata
    position = getattr(user, "position", "") or ""
    if "focal" in position.lower():
        return bool(getattr(user, "moa_organization_id", None))

    # Check MAO focal person registry assignments (BMOA organizations)
    try:
        from coordination.models import MAOFocalPerson
    except Exception:
        return False

    return MAOFocalPerson.objects.filter(
        user=user,
        is_active=True,
    ).exists()


def has_oobc_management_access(user):
    """
    Determine whether a user can manage OOBC-controlled records.

    Grants access to superusers and OOBC leadership/staff roles defined in
    STAFF_USER_TYPES. MOA focal persons and other external roles receive
    read-only access.
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return getattr(user, "user_type", None) in STAFF_USER_TYPES


__all__ = [
    'can_approve_moa_users',
    'get_pending_moa_count',
    'get_pending_first_level_count',
    'is_moa_focal_approver',
    'has_oobc_management_access',
]
