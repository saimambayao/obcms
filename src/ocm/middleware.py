"""
OCM Access Middleware

Middleware for enforcing OCM access and read-only constraints.
"""
import logging

from django.http import HttpResponseForbidden
from django.urls import resolve

logger = logging.getLogger(__name__)


class OCMAccessMiddleware:
    """
    Middleware to enforce OCM access and read-only constraints.
    
    Features:
    - Detects OCM views (namespace == 'ocm')
    - Verifies active OCM access (staff/superusers bypass)
    - Enforces read-only constraint
    - Updates last_accessed timestamp
    - Sets request.is_ocm_view and request.ocm_access flags
    - Comprehensive logging for security audit
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """Process each request"""
        response = self.process_request(request)
        if response:
            return response
        
        response = self.get_response(request)
        
        return response
    
    def process_request(self, request):
        """
        Process request to detect OCM views and verify access.
        
        Sets flags:
        - request.is_ocm_view: True if this is an OCM view
        - request.ocm_access: OCMAccess object if user has access
        """
        # Initialize flags
        request.is_ocm_view = False
        request.ocm_access = None
        
        # Skip for anonymous users
        if not request.user.is_authenticated:
            return None
        
        # Resolve URL to check namespace
        try:
            resolved = resolve(request.path_info)
            namespace = resolved.namespace
        except Exception:
            return None
        
        # Check if this is an OCM view
        if namespace != 'ocm':
            return None
        
        # Mark as OCM view
        request.is_ocm_view = True
        logger.info(f"OCM view detected: {request.path} for user {request.user.username}")
        
        # CRITICAL: Staff and superusers bypass OCM access requirement
        if request.user.is_staff or request.user.is_superuser:
            logger.info(f"Staff/superuser {request.user.username} bypassing OCM access check")
            return None
        
        # Verify OCM access
        if not hasattr(request.user, 'ocm_access'):
            logger.warning(
                f"OCM access denied: User {request.user.username} "
                f"has no ocm_access attempting to access {request.path}"
            )
            return HttpResponseForbidden(
                "Access Denied: You do not have OCM access. "
                "Please contact your administrator to request access."
            )
        
        ocm_access = request.user.ocm_access
        
        # Check if access is active
        if not ocm_access.is_active:
            logger.warning(
                f"OCM access denied: User {request.user.username} "
                f"has inactive ocm_access attempting to access {request.path}"
            )
            return HttpResponseForbidden(
                "Access Denied: Your OCM access has been deactivated. "
                "Please contact your administrator."
            )
        
        # Set OCM access on request for views to use
        request.ocm_access = ocm_access
        
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process view to enforce read-only constraint and update timestamp.
        """
        # Skip if not OCM view
        if not getattr(request, 'is_ocm_view', False):
            return None
        
        # CRITICAL: Staff and superusers bypass read-only restrictions
        if request.user.is_staff or request.user.is_superuser:
            logger.info(f"Staff/superuser {request.user.username} bypassing read-only check")
            return None
        
        # Enforce read-only
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            logger.error(
                f"OCM read-only violation: User {request.user.username} "
                f"attempted {request.method} on {request.path}"
            )
            return HttpResponseForbidden(
                "Access Denied: OCM views are read-only. "
                "Write operations are not permitted."
            )
        
        # Update last accessed timestamp
        if hasattr(request, 'ocm_access') and request.ocm_access:
            request.ocm_access.update_last_accessed()
            logger.debug(f"Updated last_accessed for user {request.user.username}")
        
        return None
