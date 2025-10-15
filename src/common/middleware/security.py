"""Security middleware for Content Security Policy and other security headers."""

import logging
from django.conf import settings
from django.core.exceptions import DisallowedHost

logger = logging.getLogger(__name__)


class KubernetesInternalHostMiddleware:
    """
    Allow Kubernetes internal IPs (10.96.*.*) to bypass ALLOWED_HOSTS validation.

    This middleware must run BEFORE Django's CommonMiddleware which validates hosts.
    Kubernetes health check probes use internal service IPs that change dynamically.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the HTTP_HOST header
        host = request.META.get('HTTP_HOST', '')

        # Extract hostname without port
        hostname = host.split(':')[0] if ':' in host else host

        # Check if this is a Kubernetes internal IP
        if hostname.startswith('10.96.'):
            logger.info(f"K8s internal request from {hostname} - bypassing ALLOWED_HOSTS")
            # Temporarily add this host to ALLOWED_HOSTS for this request
            original_allowed_hosts = settings.ALLOWED_HOSTS
            # Make a copy and add the K8s IP
            if isinstance(original_allowed_hosts, list):
                settings.ALLOWED_HOSTS = list(original_allowed_hosts) + [hostname]
            else:
                # If it's our custom class, convert to list temporarily
                settings.ALLOWED_HOSTS = list(original_allowed_hosts) + [hostname]

            try:
                response = self.get_response(request)
                return response
            finally:
                # Restore original ALLOWED_HOSTS
                settings.ALLOWED_HOSTS = original_allowed_hosts
        else:
            # Normal request, let it proceed with standard validation
            return self.get_response(request)


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
