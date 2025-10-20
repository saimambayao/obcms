"""Logging middleware for API requests and deprecation tracking."""

import logging
import time
from pathlib import Path

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

# Loggers
api_logger = logging.getLogger('api')
security_logger = logging.getLogger('django.security')


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
            log_path = Path(settings.BASE_DIR) / 'logs' / 'deprecation.log'
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.touch(exist_ok=True)

            handler = logging.FileHandler(log_path, encoding='utf-8')
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
