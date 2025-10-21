"""
Middleware to allow Kubernetes health check probes from internal pod networks.

This middleware bypasses Django's ALLOWED_HOSTS validation for requests
from internal Kubernetes pod IPs, allowing health checks to succeed
without compromising security for public requests.
"""
import re
from django.core.exceptions import DisallowedHost
from django.http import HttpResponse


class KubernetesHealthCheckMiddleware:
    """Allow health check requests from internal Kubernetes pod networks."""

    # Kubernetes internal networks (private IP ranges)
    INTERNAL_NETWORKS = [
        r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$',           # 10.0.0.0/8
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$',  # 172.16.0.0/12
        r'^192\.168\.\d{1,3}\.\d{1,3}$',              # 192.168.0.0/16
        r'^127\.0\.0\.\d{1,3}$',                      # 127.0.0.0/8 (localhost)
    ]

    # Health check paths that should be accessible from internal IPs
    HEALTH_CHECK_PATHS = ['/health/', '/healthz/', '/ready/', '/alive/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Catch DisallowedHost exceptions for health checks from internal IPs.

        If the request is a health check from an internal Kubernetes IP,
        bypass the DisallowedHost error and return a simple 200 OK.
        """
        if not isinstance(exception, DisallowedHost):
            return None

        # Only handle health check paths
        if request.path not in self.HEALTH_CHECK_PATHS:
            return None

        # Extract host IP (remove port if present)
        host = request.get_host().split(':')[0]

        # Check if request is from internal network
        if self._is_internal_ip(host):
            # Return simple 200 OK for health checks from internal IPs
            return HttpResponse("OK", status=200, content_type="text/plain")

        # Let Django handle the DisallowedHost exception normally
        return None

    def _is_internal_ip(self, ip):
        """Check if IP is from internal Kubernetes network."""
        for pattern in self.INTERNAL_NETWORKS:
            if re.match(pattern, ip):
                return True
        return False
