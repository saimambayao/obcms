"""
OCM Decorators

Function decorators for enforcing OCM access and read-only constraints.
"""
import logging
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)


def _require_ocm_access_inner(view_func, request, *args, **kwargs):
    """Inner function for OCM access checking"""

    # SECURITY: Require explicit OCM access even for staff/superusers
    # Superusers must have OCM access for audit trail and proper authorization
    if request.user.is_superuser:
        logger.warning(f"Superuser {request.user.username} accessing OCM: {request.path} - OCM access required")
        # Superusers still need OCM access for proper audit trail
        # Do not bypass the check - enforce same access controls

    # Staff users cannot bypass OCM access requirements
    # if request.user.is_staff:  # REMOVED - Security fix
    
    # Check if user has OCM access
    if not hasattr(request.user, 'ocm_access'):
        logger.warning(f"OCM access denied: User {request.user.username} has no ocm_access")
        return HttpResponseForbidden(
            "Access Denied: You do not have OCM access. "
            "Please contact your administrator to request access."
        )
    
    ocm_access = request.user.ocm_access
    
    # Check if OCM access is active
    if not ocm_access.is_active:
        logger.warning(f"OCM access denied: User {request.user.username} has inactive OCM access")
        return HttpResponseForbidden(
            "Access Denied: Your OCM access has been deactivated. "
            "Please contact your administrator."
        )
    
    # Update last accessed timestamp
    ocm_access.update_last_accessed()
    
    # Allow access
    return view_func(request, *args, **kwargs)


def require_ocm_access(view_func):
    """
    Decorator to require active OCM access.
    
    Staff and superusers bypass this check.
    Updates last_accessed timestamp on successful access.
    
    Usage:
        @login_required
        @require_ocm_access
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return _require_ocm_access_inner(view_func, request, *args, **kwargs)
    
    return wrapper


def _enforce_readonly_inner(view_func, request, *args, **kwargs):
    """Inner function for read-only enforcement"""

    # SECURITY: Read-only restrictions apply to ALL users including staff/superusers
    # This prevents accidental data modification by privileged users
    if request.user.is_superuser:
        logger.warning(f"Superuser {request.user.username} accessing OCM read-only: {request.path} - Enforcing read-only")
        # Even superusers must respect read-only constraints in OCM views

    # Staff users cannot bypass read-only restrictions
    # if request.user.is_staff:  # REMOVED - Security fix
    
    # Block write methods
    if request.method not in ['GET', 'HEAD', 'OPTIONS']:
        logger.error(
            f"OCM read-only violation: User {request.user.username} "
            f"attempted {request.method} on {request.path}"
        )
        return HttpResponseForbidden(
            "Access Denied: OCM views are read-only. "
            "Write operations are not permitted."
        )
    
    return view_func(request, *args, **kwargs)


def enforce_readonly(view_func):
    """
    Decorator to enforce read-only access (blocks POST, PUT, PATCH, DELETE).
    
    Staff and superusers bypass this restriction.
    
    Usage:
        @login_required
        @enforce_readonly
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return _enforce_readonly_inner(view_func, request, *args, **kwargs)
    
    return wrapper


def ocm_readonly_view(view_func):
    """
    Combined decorator: requires OCM access AND enforces read-only.

    SECURITY: Use this decorator on ALL OCM views.
    ALL users including staff/superusers must have OCM access.
    Read-only restrictions apply to ALL users.

    This is the primary decorator you should use for OCM views.

    Usage:
        @login_required
        @ocm_readonly_view
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # SECURITY: NO BYPASSES - All users must follow OCM access controls
        if request.user.is_superuser:
            logger.warning(f"Superuser {request.user.username} accessing OCM: {request.path} - Full OCM checks applied")
            # Even superusers get full OCM access validation and read-only enforcement

        # Staff users cannot bypass OCM restrictions
        # if request.user.is_staff:  # REMOVED - Security fix
        
        # First check read-only (fail fast)
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            logger.error(
                f"OCM read-only violation: User {request.user.username} "
                f"attempted {request.method} on {request.path}"
            )
            return HttpResponseForbidden(
                "Access Denied: OCM views are read-only. "
                "Write operations are not permitted."
            )
        
        # Then check OCM access
        if not hasattr(request.user, 'ocm_access'):
            logger.warning(f"OCM access denied: User {request.user.username} has no ocm_access")
            return HttpResponseForbidden(
                "Access Denied: You do not have OCM access. "
                "Please contact your administrator to request access."
            )
        
        ocm_access = request.user.ocm_access
        
        if not ocm_access.is_active:
            logger.warning(f"OCM access denied: User {request.user.username} has inactive OCM access")
            return HttpResponseForbidden(
                "Access Denied: Your OCM access has been deactivated. "
                "Please contact your administrator."
            )
        
        # Update last accessed
        ocm_access.update_last_accessed()
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_ocm_analyst(view_func):
    """
    Decorator to require analyst or executive level access.

    Used for report generation views.
    ALL users including staff/superusers must have proper OCM analyst access.

    Usage:
        @login_required
        @require_ocm_analyst
        def generate_report(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # SECURITY: No bypasses - all users need proper OCM analyst access
        if request.user.is_superuser:
            logger.warning(f"Superuser {request.user.username} accessing OCM analyst: {request.path} - Analyst access required")
            # Even superusers need analyst level OCM access

        # Staff users cannot bypass analyst access requirements
        # if request.user.is_staff:  # REMOVED - Security fix
        
        # Check OCM access first
        if not hasattr(request.user, 'ocm_access'):
            return HttpResponseForbidden("Access Denied: You do not have OCM access.")
        
        ocm_access = request.user.ocm_access
        
        if not ocm_access.is_active:
            return HttpResponseForbidden("Access Denied: Your OCM access is inactive.")
        
        # Check analyst level
        if ocm_access.access_level not in ['analyst', 'executive']:
            logger.warning(
                f"OCM analyst access denied: User {request.user.username} "
                f"has level {ocm_access.access_level}, requires analyst or executive"
            )
            return HttpResponseForbidden(
                "Access Denied: This feature requires Analyst or Executive access level."
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_ocm_executive(view_func):
    """
    Decorator to require executive level access.

    Used for data export views.
    ALL users including staff/superusers must have proper OCM executive access.

    Usage:
        @login_required
        @require_ocm_executive
        def export_data(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # SECURITY: No bypasses - all users need proper OCM executive access
        if request.user.is_superuser:
            logger.warning(f"Superuser {request.user.username} accessing OCM executive: {request.path} - Executive access required")
            # Even superusers need executive level OCM access

        # Staff users cannot bypass executive access requirements
        # if request.user.is_staff:  # REMOVED - Security fix
        
        # Check OCM access first
        if not hasattr(request.user, 'ocm_access'):
            return HttpResponseForbidden("Access Denied: You do not have OCM access.")
        
        ocm_access = request.user.ocm_access
        
        if not ocm_access.is_active:
            return HttpResponseForbidden("Access Denied: Your OCM access is inactive.")
        
        # Check executive level
        if ocm_access.access_level != 'executive':
            logger.warning(
                f"OCM executive access denied: User {request.user.username} "
                f"has level {ocm_access.access_level}, requires executive"
            )
            return HttpResponseForbidden(
                "Access Denied: This feature requires Executive access level."
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
