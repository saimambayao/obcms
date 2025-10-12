"""
Audit Middleware for OBCMS Budget System

Captures request context (user, IP, user agent) and stores in thread-local
storage for access by Django signals.

Legal Requirement: Parliament Bill No. 325 Section 78 - Audit Trail

Author: Claude Code (OBCMS System Architect)
Date: October 13, 2025
"""

from threading import current_thread


class AuditMiddleware:
    """
    Middleware to store request user and metadata in thread-local storage.
    Makes user and request info available to Django signals for audit logging.

    Thread-local storage pattern:
    - Set at request start
    - Available to all signals during request
    - Cleaned up after response

    Security:
    - Handles unauthenticated users gracefully
    - Extracts IP from X-Forwarded-For (proxy support)
    - Stores user agent for security audit
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store user in thread-local
        current_thread().request_user = (
            request.user if request.user.is_authenticated else None
        )

        # Store IP address (proxy-aware)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take first IP in X-Forwarded-For chain
            current_thread().request_ip = x_forwarded_for.split(',')[0].strip()
        else:
            current_thread().request_ip = request.META.get('REMOTE_ADDR')

        # Store user agent
        current_thread().request_user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Process request
        response = self.get_response(request)

        # Clean up thread-local storage
        if hasattr(current_thread(), 'request_user'):
            delattr(current_thread(), 'request_user')
        if hasattr(current_thread(), 'request_ip'):
            delattr(current_thread(), 'request_ip')
        if hasattr(current_thread(), 'request_user_agent'):
            delattr(current_thread(), 'request_user_agent')

        return response
