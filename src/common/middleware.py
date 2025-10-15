"""Middleware for access control and security."""

import logging
import time
import json
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin

# Loggers
api_logger = logging.getLogger('api')
security_logger = logging.getLogger('django.security')


class MANAAccessControlMiddleware:
    """
    Restrict MANA Participants and Facilitators to only access:
    - Provincial OBC management pages
    - Regional MANA pages
    - Their own profile
    - Logout

    MANA users are identified by:
    - NOT is_staff
    - NOT is_superuser
    - Has can_access_regional_mana permission
    """

    # URL patterns that MANA users CAN access
    ALLOWED_URL_PATTERNS = [
        # Auth and profile
        "common:login",
        "common:logout",
        "common:profile",
        "common:dashboard",  # Allow dashboard (it will redirect appropriately)
        "common:home",  # Alias for dashboard
        # Provincial OBC
        "common:communities_manage_provincial",
        "common:communities_manage_provincial_obc",
        "common:communities_view_provincial",
        "common:communities_edit_provincial",
        "common:communities_delete_provincial",
        "common:communities_restore_provincial",
        "common:communities_submit_provincial",
        "common:communities_add_province",
        # Regional MANA
        "mana:mana_regional_overview",
        "mana:mana_provincial_overview",
        "mana:mana_provincial_card_detail",
        "mana:mana_province_edit",
        "mana:mana_province_delete",
        "mana:mana_manage_assessments",
        "mana:mana_assessment_detail",
        # MANA app (all regional MANA workshop URLs)
        "mana:",  # Allow all MANA app URLs
        # Static/media files
        "/static/",
        "/media/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is a MANA user (participant or facilitator)
        if request.user.is_authenticated:
            is_mana_user = (
                not request.user.is_staff
                and not request.user.is_superuser
                and request.user.has_perm("mana.can_access_regional_mana")
            )

            if is_mana_user:
                # Get current URL path
                path = request.path

                # Allow static/media files
                if path.startswith("/static/") or path.startswith("/media/"):
                    return self.get_response(request)

                # Check if URL is in allowed list
                try:
                    current_url = resolve(path)
                    url_name = current_url.url_name
                    namespace = current_url.namespace

                    # Build full URL name
                    if namespace:
                        full_url_name = f"{namespace}:{url_name}"
                    else:
                        full_url_name = url_name

                    # Check if URL is allowed
                    is_allowed = False

                    # Check exact matches
                    if full_url_name in self.ALLOWED_URL_PATTERNS:
                        is_allowed = True

                    # Check namespace patterns (e.g., "mana:")
                    for pattern in self.ALLOWED_URL_PATTERNS:
                        if pattern.endswith(":") and full_url_name.startswith(pattern):
                            is_allowed = True
                            break

                    if not is_allowed:
                        # Redirect to Regional MANA overview instead of raising PermissionDenied
                        return redirect("mana:mana_regional_overview")

                except Exception:
                    # If URL resolution fails, allow request to continue
                    # (will be handled by Django's normal 404)
                    pass

        response = self.get_response(request)
        return response


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


class APILoggingMiddleware(MiddlewareMixin):
    """
    Log all API requests and responses for audit trail and security monitoring.

    Logs:
    - Request: method, path, user, IP, user agent, query params
    - Response: status code, duration, response size
    - Errors: Detailed logging for 4xx and 5xx responses

    Security Benefits:
    - Forensic investigation capabilities
    - Attack pattern detection
    - Compliance audit trail
    - Performance monitoring
    """

    def process_request(self, request):
        """Log API request details."""
        # Only log API requests
        if not request.path.startswith('/api/'):
            return None

        # Store request start time for duration calculation
        request._api_log_start = time.time()

        # Get user information
        if request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
        else:
            user_info = "Anonymous"

        # Log request
        api_logger.info(
            f"API Request | "
            f"Method: {request.method} | "
            f"Path: {request.path} | "
            f"User: {user_info} | "
            f"IP: {self._get_client_ip(request)} | "
            f"User-Agent: {self._get_user_agent(request)}"
        )

        return None

    def process_response(self, request, response):
        """Log API response details."""
        # Only log API responses
        if not request.path.startswith('/api/'):
            return response

        # Calculate request duration
        if hasattr(request, '_api_log_start'):
            duration = time.time() - request._api_log_start
        else:
            duration = 0

        # Get user information
        if request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
        else:
            user_info = "Anonymous"

        # Get response size
        response_size = len(response.content) if hasattr(response, 'content') else 0

        # Log response
        log_level = self._get_log_level(response.status_code)
        log_message = (
            f"API Response | "
            f"Method: {request.method} | "
            f"Path: {request.path} | "
            f"User: {user_info} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s | "
            f"Size: {response_size} bytes"
        )

        if log_level == logging.ERROR:
            api_logger.error(log_message)
        elif log_level == logging.WARNING:
            api_logger.warning(log_message)
        else:
            api_logger.info(log_message)

        # Log additional details for errors
        if response.status_code >= 400:
            self._log_error_details(request, response, duration)

        return response

    def _get_client_ip(self, request):
        """Get client IP address (proxy-aware)."""
        # Check for Cloudflare real IP
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip

        # Check for X-Forwarded-For
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP (client IP)
            ip = x_forwarded_for.split(',')[0].strip()
            return ip

        # Fall back to REMOTE_ADDR
        return request.META.get('REMOTE_ADDR', 'Unknown')

    def _get_user_agent(self, request):
        """Get user agent string (truncated)."""
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        # Truncate to 100 characters
        return user_agent[:100] if len(user_agent) > 100 else user_agent

    def _get_log_level(self, status_code):
        """Determine log level based on status code."""
        if status_code >= 500:
            return logging.ERROR
        elif status_code >= 400:
            return logging.WARNING
        else:
            return logging.INFO

    def _log_error_details(self, request, response, duration):
        """Log detailed information for error responses."""
        user_info = f"{request.user.username} (ID: {request.user.id})" if request.user.is_authenticated else "Anonymous"
        ip_address = self._get_client_ip(request)

        # Determine error type
        if response.status_code == 401:
            error_type = "Unauthorized"
        elif response.status_code == 403:
            error_type = "Forbidden"
        elif response.status_code == 404:
            error_type = "Not Found"
        elif response.status_code == 429:
            error_type = "Rate Limited"
        elif response.status_code >= 500:
            error_type = "Server Error"
        else:
            error_type = "Client Error"

        api_logger.warning(
            f"API {error_type} | "
            f"Method: {request.method} | "
            f"Path: {request.path} | "
            f"User: {user_info} | "
            f"IP: {ip_address} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s"
        )


class DeprecationLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log requests to deprecated URLs.

    Logs deprecation events to help monitor usage of legacy endpoints
    and plan safe removal of deprecated code.

    Logged Information:
    - URL path accessed
    - User (authenticated or anonymous)
    - Timestamp
    - Referer (where the request came from)
    - User agent
    - IP address

    Logs are written to: logs/deprecation.log
    """

    # Deprecated URL patterns to monitor
    DEPRECATED_PATTERNS = [
        '/oobc-management/staff/tasks/',
        '/oobc-management/staff/task-templates/',
        '/project-central/',  # Old URL pattern (now redirects to /project-management/)
        '/coordination/events/legacy/',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up dedicated deprecation logger
        self.logger = logging.getLogger('deprecation')

        # Ensure handler exists (create if not configured)
        if not self.logger.handlers:
            handler = logging.FileHandler('logs/deprecation.log')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.WARNING)

    def process_request(self, request):
        """Check if request is to a deprecated URL and log it."""
        path = request.path

        # Check if path matches any deprecated pattern
        is_deprecated = any(
            path.startswith(pattern) for pattern in self.DEPRECATED_PATTERNS
        )

        if is_deprecated:
            # Get user information
            if request.user.is_authenticated:
                user_info = f"{request.user.username} (ID: {request.user.id})"
            else:
                user_info = "Anonymous"

            # Get request metadata
            referer = request.META.get('HTTP_REFERER', 'Direct access')
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]
            ip_address = self._get_client_ip(request)

            # Log deprecation event
            self.logger.warning(
                f"Deprecated URL accessed | "
                f"Path: {path} | "
                f"User: {user_info} | "
                f"IP: {ip_address} | "
                f"Referer: {referer} | "
                f"User-Agent: {user_agent}"
            )

            # Store in request for view layer access
            request.deprecated_url_accessed = True

        return None

    def _get_client_ip(self, request):
        """Get client IP address (proxy-aware)."""
        # Check for Cloudflare real IP
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip

        # Check for X-Forwarded-For
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP (client IP)
            ip = x_forwarded_for.split(',')[0].strip()
            return ip

        # Fall back to REMOTE_ADDR
        return request.META.get('REMOTE_ADDR', 'Unknown')
