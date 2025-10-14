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
    
    # CRITICAL: Staff and superusers bypass OCM access requirements
    if request.user.is_staff or request.user.is_superuser:
        logger.info(f"Staff/superuser {request.user.username} bypassing OCM access check")
        return view_func(request, *args, **kwargs)
    
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
    
    # CRITICAL: Staff and superusers bypass read-only restrictions
    if request.user.is_staff or request.user.is_superuser:
        logger.info(f"Staff/superuser {request.user.username} bypassing read-only check")
        return view_func(request, *args, **kwargs)
    
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
    
    CRITICAL: Use this decorator on ALL OCM views.
    Staff and superusers bypass both checks.
    
    This is the primary decorator you should use for OCM views.
    
    Usage:
        @login_required
        @ocm_readonly_view
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # CRITICAL: Staff and superusers bypass ALL restrictions
        if request.user.is_staff or request.user.is_superuser:
            logger.info(f"Staff/superuser {request.user.username} bypassing all OCM restrictions")
            return view_func(request, *args, **kwargs)
        
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
    Staff and superusers bypass this check.
    
    Usage:
        @login_required
        @require_ocm_analyst
        def generate_report(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # CRITICAL: Staff and superusers bypass
        if request.user.is_staff or request.user.is_superuser:
            logger.info(f"Staff/superuser {request.user.username} bypassing analyst check")
            return view_func(request, *args, **kwargs)
        
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
    Staff and superusers bypass this check.
    
    Usage:
        @login_required
        @require_ocm_executive
        def export_data(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # CRITICAL: Staff and superusers bypass
        if request.user.is_staff or request.user.is_superuser:
            logger.info(f"Staff/superuser {request.user.username} bypassing executive check")
            return view_func(request, *args, **kwargs)
        
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
