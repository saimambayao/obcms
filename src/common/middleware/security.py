"""Security middleware for Content Security Policy and other security headers."""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Diagnostic middleware to log all incoming requests.

    This helps debug issues where requests aren't appearing in logs.
    Should be placed FIRST in MIDDLEWARE to catch all requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log incoming request with key details
        logger.info(
            f"INCOMING REQUEST: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR')} "
            f"Host: {request.META.get('HTTP_HOST')}"
        )

        try:
            response = self.get_response(request)
            logger.info(
                f"RESPONSE: {request.method} {request.path} -> {response.status_code}"
            )
            return response
        except Exception as e:
            logger.error(
                f"ERROR processing {request.method} {request.path}: {e}",
                exc_info=True
            )
            raise


class ContentSecurityPolicyMiddleware:
    """
    Middleware to add Content Security Policy (CSP) headers.

    Helps prevent XSS attacks, clickjacking, and other code injection attacks
    by controlling which resources can be loaded and executed.

    Configured via settings.CONTENT_SECURITY_POLICY
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only add CSP header if configured (typically in production)
        if hasattr(settings, "CONTENT_SECURITY_POLICY"):
            response["Content-Security-Policy"] = settings.CONTENT_SECURITY_POLICY

        return response
