"""Security middleware for Content Security Policy and other security headers."""

from django.conf import settings


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
