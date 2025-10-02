"""
Security event logging utilities.

Provides structured logging for security-relevant events:
- Failed authentication attempts
- Unauthorized access attempts
- Permission denials
- Sensitive data access
- Administrative actions
"""

import logging
from django.conf import settings

# Get security logger
security_logger = logging.getLogger('django.security')


def log_failed_login(request, username, reason="Invalid credentials"):
    """
    Log failed login attempt with IP address and user agent.

    Args:
        request: HttpRequest object
        username: Attempted username
        reason: Reason for failure (default: "Invalid credentials")
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

    security_logger.warning(
        f"Failed login attempt | Username: {username} | IP: {ip_address} | "
        f"User-Agent: {user_agent} | Reason: {reason}"
    )


def log_successful_login(request, user):
    """
    Log successful login for audit trail.

    Args:
        request: HttpRequest object
        user: User object
    """
    ip_address = get_client_ip(request)

    security_logger.info(
        f"Successful login | User: {user.username} (ID: {user.id}) | "
        f"IP: {ip_address}"
    )


def log_logout(request, user):
    """
    Log user logout.

    Args:
        request: HttpRequest object
        user: User object
    """
    ip_address = get_client_ip(request)

    security_logger.info(
        f"User logout | User: {user.username} (ID: {user.id}) | "
        f"IP: {ip_address}"
    )


def log_unauthorized_access(request, path, user=None):
    """
    Log unauthorized access attempt.

    Args:
        request: HttpRequest object
        path: Attempted path/URL
        user: User object (if authenticated)
    """
    ip_address = get_client_ip(request)
    user_info = f"{user.username} (ID: {user.id})" if user else "Anonymous"

    security_logger.warning(
        f"Unauthorized access attempt | User: {user_info} | "
        f"Path: {path} | IP: {ip_address}"
    )


def log_permission_denied(request, user, permission, resource=None):
    """
    Log permission denial.

    Args:
        request: HttpRequest object
        user: User object
        permission: Required permission
        resource: Resource being accessed (optional)
    """
    ip_address = get_client_ip(request)
    resource_info = f" | Resource: {resource}" if resource else ""

    security_logger.warning(
        f"Permission denied | User: {user.username} (ID: {user.id}) | "
        f"Permission: {permission}{resource_info} | IP: {ip_address}"
    )


def log_sensitive_data_access(request, user, data_type, record_id=None):
    """
    Log access to sensitive data for audit trail.

    Args:
        request: HttpRequest object
        user: User object
        data_type: Type of data accessed (e.g., "OBC Community Data", "Assessment")
        record_id: ID of specific record (optional)
    """
    ip_address = get_client_ip(request)
    record_info = f" (ID: {record_id})" if record_id else ""

    security_logger.info(
        f"Sensitive data access | User: {user.username} (ID: {user.id}) | "
        f"Data: {data_type}{record_info} | IP: {ip_address}"
    )


def log_data_export(request, user, export_type, record_count):
    """
    Log data export operation.

    Args:
        request: HttpRequest object
        user: User object
        export_type: Type of data exported
        record_count: Number of records exported
    """
    ip_address = get_client_ip(request)

    security_logger.warning(
        f"Data export | User: {user.username} (ID: {user.id}) | "
        f"Type: {export_type} | Records: {record_count} | IP: {ip_address}"
    )


def log_admin_action(request, user, action, target=None):
    """
    Log administrative action.

    Args:
        request: HttpRequest object
        user: User object
        action: Action performed (e.g., "User account created", "Permission granted")
        target: Target of action (optional)
    """
    ip_address = get_client_ip(request)
    target_info = f" | Target: {target}" if target else ""

    security_logger.warning(
        f"Admin action | User: {user.username} (ID: {user.id}) | "
        f"Action: {action}{target_info} | IP: {ip_address}"
    )


def log_security_event(request, event_type, details, severity="INFO"):
    """
    Generic security event logging.

    Args:
        request: HttpRequest object
        event_type: Type of security event
        details: Event details
        severity: Log level (INFO, WARNING, ERROR, CRITICAL)
    """
    ip_address = get_client_ip(request)
    user = request.user if request.user.is_authenticated else None
    user_info = f"{user.username} (ID: {user.id})" if user else "Anonymous"

    log_message = (
        f"Security event | Type: {event_type} | User: {user_info} | "
        f"Details: {details} | IP: {ip_address}"
    )

    severity = severity.upper()
    if severity == "CRITICAL":
        security_logger.critical(log_message)
    elif severity == "ERROR":
        security_logger.error(log_message)
    elif severity == "WARNING":
        security_logger.warning(log_message)
    else:
        security_logger.info(log_message)


def get_client_ip(request):
    """
    Get client IP address from request, handling proxies.

    Args:
        request: HttpRequest object

    Returns:
        IP address string
    """
    # Check X-Forwarded-For header (for proxies/load balancers)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP (client IP) if multiple IPs present
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # Fall back to REMOTE_ADDR
        ip = request.META.get('REMOTE_ADDR', 'Unknown')

    return ip


# ============================================================================
# DECORATOR FOR AUTOMATIC SECURITY LOGGING
# ============================================================================

def log_sensitive_access(data_type):
    """
    Decorator to automatically log sensitive data access.

    Usage:
        @log_sensitive_access("OBC Community Data")
        def view_community(request, community_id):
            ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                record_id = kwargs.get('pk') or kwargs.get('id')
                log_sensitive_data_access(request, request.user, data_type, record_id)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
